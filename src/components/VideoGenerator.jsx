import React, { useEffect, useRef, useState } from "react";
import { supabase } from "../lib/supabase";

const BACKEND_URL = "http://localhost:8000";

const STYLES = [
  { id: "cinematic", name: "Cinematic 8K", icon: "🎥", desc: "Hollywood anamorphic lighting & grading" },
  { id: "liveaction", name: "Live Action", icon: "🎬", desc: "35mm photorealistic film cinematography" },
  { id: "anime", name: "Anime / Manga", icon: "🌸", desc: "Studio Ghibli & Shinkai cel-shaded art" },
  { id: "3d_animation", name: "3D Pixar Animation", icon: "🧸", desc: "Disney Pixar 3D stylized characters" },
  { id: "cyberpunk", name: "Cyberpunk Sci-Fi", icon: "⚡", desc: "Neon glow, rain reflections & synthwave" },
  { id: "documentary", name: "Nature Documentary", icon: "🌿", desc: "BBC Earth & National Geographic realism" },
  { id: "fantasy", name: "Dark Fantasy", icon: "🏰", desc: "Mystical runes, ancient enchanted ruins" },
  { id: "comic", name: "Comic Book", icon: "📚", desc: "Bold ink outlines, halftone pop art" }
];

const VOICES = [
  { id: "en-US-ChristopherNeural", name: "Christopher", tone: "Deep, Cinematic & Authoritative (Male)" },
  { id: "en-US-JennyNeural", name: "Jenny", tone: "Clear, Natural & Engaging (Female)" },
  { id: "en-US-GuyNeural", name: "Guy", tone: "Casual, Energetic & Modern (Male)" },
  { id: "en-US-AriaNeural", name: "Aria", tone: "Expressive Storyteller (Female)" },
  { id: "en-GB-RyanNeural", name: "Ryan", tone: "Sophisticated British Documentary (Male)" },
  { id: "en-GB-SoniaNeural", name: "Sonia", tone: "Warm & Refined British (Female)" }
];

const PRESETS = [
  "Secrets of Ancient Egyptian Pyramids and hidden chambers",
  "How black holes warp space and bend time itself",
  "The bizarre bioluminescent creatures of the Mariana Trench",
  "Why your brain procrastinates and the 2-minute rule to fix it",
  "The hidden language trees use to communicate underground",
  "Cyberpunk metropolis in the year 2088 under neon rain"
];

export default function VideoGenerator() {
  const [engineMode, setEngineMode] = useState("local"); // "local" | "supabase"
  const [prompt, setPrompt] = useState("");
  const [style, setStyle] = useState("cinematic");
  const [format, setFormat] = useState("9:16"); // "9:16" | "16:9"
  const [duration, setDuration] = useState(30);
  const [voice, setVoice] = useState("en-US-ChristopherNeural");
  const [subtitleStyle, setSubtitleStyle] = useState("viral_yellow");
  const [useBgMusic, setUseBgMusic] = useState(true);
  const [apiKey, setApiKey] = useState("");

  const [status, setStatus] = useState("idle"); // "idle" | "generating" | "completed" | "error"
  const [progressPct, setProgressPct] = useState(0);
  const [progressMsg, setProgressMsg] = useState("");
  const [errorMsg, setErrorMsg] = useState("");
  const [currentVideo, setCurrentVideo] = useState(null);
  const [library, setLibrary] = useState([]);

  // Supabase auth state for cloud mode
  const [user, setUser] = useState(null);
  const [authEmail, setAuthEmail] = useState("");
  const [authPassword, setAuthPassword] = useState("");
  const [authLoading, setAuthLoading] = useState(false);

  const pollIntervalRef = useRef(null);

  // Load saved library from local engine on mount
  useEffect(() => {
    fetchLibrary();
    // Check Supabase session if configured
    try {
      supabase.auth.getSession().then(({ data }) => {
        if (data?.session?.user) setUser(data.session.user);
      }).catch(() => {});
    } catch (e) {}

    return () => {
      if (pollIntervalRef.current) clearInterval(pollIntervalRef.current);
    };
  }, []);

  async function fetchLibrary() {
    try {
      const res = await fetch(`${BACKEND_URL}/api/ai-shorts`);
      if (res.ok) {
        const data = await res.json();
        setLibrary(data.ai_shorts || []);
      }
    } catch (e) {
      // Backend may be offline or starting
    }
  }

  async function handleGenerate(e) {
    e.preventDefault();
    if (!prompt.trim()) {
      setErrorMsg("Please enter a topic, prompt, or comment for the video.");
      return;
    }

    setErrorMsg("");
    setCurrentVideo(null);
    setStatus("generating");
    setProgressPct(5);
    setProgressMsg("Connecting to AI Engine...");

    const taskId = `ai_gen_${Date.now()}`;

    // Start progress polling
    if (pollIntervalRef.current) clearInterval(pollIntervalRef.current);
    pollIntervalRef.current = setInterval(async () => {
      try {
        const pr = await fetch(`${BACKEND_URL}/progress/${taskId}`);
        if (pr.ok) {
          const pdata = await pr.json();
          if (pdata && pdata.percent !== undefined) {
            setProgressPct(pdata.percent);
            setProgressMsg(pdata.status || "Generating video...");
          }
        }
      } catch (err) {}
    }, 1200);

    try {
      const payload = {
        comment: prompt.trim(),
        voice_id: voice,
        aspect_ratio: format,
        style: style,
        subtitle_style: subtitleStyle,
        use_bg_music: useBgMusic,
        target_duration: Number(duration),
        api_key: apiKey.trim(),
        task_id: taskId
      };

      const response = await fetch(`${BACKEND_URL}/api/generate-ai-video`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      if (pollIntervalRef.current) clearInterval(pollIntervalRef.current);

      if (!response.ok) {
        const errData = await response.json().catch(() => ({}));
        throw new Error(errData.detail || "Video generation failed on backend.");
      }

      const result = await response.json();
      setProgressPct(100);
      setProgressMsg("Video ready!");
      setStatus("completed");
      setCurrentVideo(result);
      fetchLibrary();
    } catch (err) {
      if (pollIntervalRef.current) clearInterval(pollIntervalRef.current);
      setStatus("error");
      setErrorMsg(err.message || "Failed to generate video.");
    }
  }

  return (
    <div style={ui.wrapper}>
      {/* Top Banner & Mode Toggle */}
      <div style={ui.header}>
        <div style={ui.brandWrap}>
          <div style={ui.brandIcon}>🎬</div>
          <div>
            <h1 style={ui.title}>AI Video Generator</h1>
            <p style={ui.subtitle}>
              Turn any topic or comment into viral <b>YouTube Shorts (9:16)</b>, <b>Instagram Reels (9:16)</b>, or <b>YouTube Widescreen (16:9)</b> videos.
            </p>
          </div>
        </div>

        <div style={ui.modePills}>
          <button
            onClick={() => setEngineMode("local")}
            style={{
              ...ui.modeBtn,
              backgroundColor: engineMode === "local" ? "#6366f1" : "rgba(255,255,255,0.06)",
              color: engineMode === "local" ? "#fff" : "#94a3b8"
            }}
          >
            ⚡ Local AI Engine (1-Click, Free)
          </button>
          <button
            onClick={() => setEngineMode("supabase")}
            style={{
              ...ui.modeBtn,
              backgroundColor: engineMode === "supabase" ? "#ec4899" : "rgba(255,255,255,0.06)",
              color: engineMode === "supabase" ? "#fff" : "#94a3b8"
            }}
          >
            ☁️ Cloud Engine (Fal.ai / Wan)
          </button>
        </div>
      </div>

      {/* Main Grid: Form on left, Output Player on right */}
      <div style={ui.grid}>
        {/* LEFT COLUMN: Controls */}
        <div style={ui.card}>
          <form onSubmit={handleGenerate}>
            {/* Prompt Input */}
            <div style={ui.field}>
              <label style={ui.label}>
                💬 Video Topic / Comment / Story
              </label>
              <textarea
                rows={3}
                style={ui.textarea}
                placeholder="E.g. How black holes work in space, or 3 mind-blowing psychology facts..."
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
              />
              {/* Presets */}
              <div style={ui.presetsRow}>
                <span style={{ fontSize: "0.75rem", color: "#64748b" }}>Quick Ideas:</span>
                {PRESETS.slice(0, 3).map((p, idx) => (
                  <button
                    key={idx}
                    type="button"
                    style={ui.presetChip}
                    onClick={() => setPrompt(p)}
                  >
                    {p.length > 32 ? p.slice(0, 32) + "..." : p}
                  </button>
                ))}
              </div>
            </div>

            {/* Video Format (YouTube Shorts / Reels vs YouTube 16:9) */}
            <div style={ui.field}>
              <label style={ui.label}>📱 Platform & Aspect Ratio</label>
              <div style={ui.formatToggle}>
                <button
                  type="button"
                  onClick={() => setFormat("9:16")}
                  style={{
                    ...ui.formatBtn,
                    borderColor: format === "9:16" ? "#6366f1" : "rgba(255,255,255,0.1)",
                    backgroundColor: format === "9:16" ? "rgba(99, 102, 241, 0.15)" : "transparent"
                  }}
                >
                  <span style={{ fontSize: "1.4rem" }}>📱</span>
                  <div>
                    <div style={{ fontWeight: 600, color: "#fff" }}>YouTube Shorts & Instagram Reels</div>
                    <div style={{ fontSize: "0.75rem", color: "#94a3b8" }}>Vertical 9:16 (720x1280)</div>
                  </div>
                </button>
                <button
                  type="button"
                  onClick={() => setFormat("16:9")}
                  style={{
                    ...ui.formatBtn,
                    borderColor: format === "16:9" ? "#6366f1" : "rgba(255,255,255,0.1)",
                    backgroundColor: format === "16:9" ? "rgba(99, 102, 241, 0.15)" : "transparent"
                  }}
                >
                  <span style={{ fontSize: "1.4rem" }}>🖥️</span>
                  <div>
                    <div style={{ fontWeight: 600, color: "#fff" }}>YouTube Standard Video</div>
                    <div style={{ fontSize: "0.75rem", color: "#94a3b8" }}>Widescreen 16:9 (1280x720)</div>
                  </div>
                </button>
              </div>
            </div>

            {/* Style Selection Grid */}
            <div style={ui.field}>
              <label style={ui.label}>🎨 Visual Style</label>
              <div style={ui.stylesGrid}>
                {STYLES.map((s) => (
                  <button
                    key={s.id}
                    type="button"
                    onClick={() => setStyle(s.id)}
                    style={{
                      ...ui.styleCard,
                      borderColor: style === s.id ? "#6366f1" : "rgba(255,255,255,0.08)",
                      backgroundColor: style === s.id ? "rgba(99, 102, 241, 0.2)" : "rgba(15, 23, 42, 0.5)"
                    }}
                  >
                    <span style={{ fontSize: "1.2rem" }}>{s.icon}</span>
                    <div style={{ textAlign: "left" }}>
                      <div style={{ fontSize: "0.85rem", fontWeight: 600, color: "#f8fafc" }}>{s.name}</div>
                      <div style={{ fontSize: "0.7rem", color: "#94a3b8" }}>{s.desc}</div>
                    </div>
                  </button>
                ))}
              </div>
            </div>

            {/* Voice & Duration Row */}
            <div style={ui.row2}>
              <div style={ui.field}>
                <label style={ui.label}>🎙️ AI Voiceover (TTS)</label>
                <select
                  style={ui.select}
                  value={voice}
                  onChange={(e) => setVoice(e.target.value)}
                >
                  {VOICES.map((v) => (
                    <option key={v.id} value={v.id}>
                      {v.name} — {v.tone}
                    </option>
                  ))}
                </select>
              </div>

              <div style={ui.field}>
                <label style={ui.label}>⏱️ Duration</label>
                <select
                  style={ui.select}
                  value={duration}
                  onChange={(e) => setDuration(Number(e.target.value))}
                >
                  <option value={15}>15 Seconds (Quick Short)</option>
                  <option value={30}>30 Seconds (Viral Standard)</option>
                  <option value={60}>60 Seconds (Extended Story)</option>
                </select>
              </div>
            </div>

            {/* Subtitles & Music */}
            <div style={ui.row2}>
              <div style={ui.field}>
                <label style={ui.label}>✨ Viral Subtitle Style</label>
                <select
                  style={ui.select}
                  value={subtitleStyle}
                  onChange={(e) => setSubtitleStyle(e.target.value)}
                >
                  <option value="viral_yellow">🟡 Viral Yellow (Shorts/Reels Style)</option>
                  <option value="neon_cyan">🔵 Neon Electric Cyan</option>
                  <option value="neon_green">🟢 TikTok Neon Green</option>
                  <option value="white">⚪ Crisp Modern White</option>
                  <option value="none">🚫 No Subtitles</option>
                </select>
              </div>

              <div style={{ ...ui.field, justifyContent: "center" }}>
                <label style={{ ...ui.label, cursor: "pointer", display: "flex", alignItems: "center", gap: "8px", marginTop: "24px" }}>
                  <input
                    type="checkbox"
                    checked={useBgMusic}
                    onChange={(e) => setUseBgMusic(e.target.checked)}
                    style={{ width: "18px", height: "18px", accentColor: "#6366f1" }}
                  />
                  <span>🎵 Ambient Synth Music</span>
                </label>
              </div>
            </div>

            {/* Optional API Key for Cloud High-Tier Models */}
            <div style={ui.field}>
              <label style={ui.label}>
                🔑 Optional Cloud API Key (Pollinations / Fal.ai)
              </label>
              <input
                type="password"
                style={ui.input}
                placeholder="Leave blank to use ultra-fast free engine, or paste API key"
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
              />
            </div>

            {/* Generate Button */}
            <button
              type="submit"
              disabled={status === "generating"}
              style={{
                ...ui.submitBtn,
                opacity: status === "generating" ? 0.6 : 1,
                cursor: status === "generating" ? "not-allowed" : "pointer"
              }}
            >
              {status === "generating" ? (
                <span>⏳ Generating AI Video... ({progressPct}%)</span>
              ) : (
                <span>🚀 Generate Viral {format === "9:16" ? "Short / Reel" : "Video"}</span>
              )}
            </button>
          </form>

          {/* Progress Bar */}
          {status === "generating" && (
            <div style={ui.progressWrap}>
              <div style={ui.progressHeader}>
                <span style={{ fontSize: "0.85rem", color: "#cbd5e1" }}>{progressMsg}</span>
                <span style={{ fontSize: "0.85rem", fontWeight: 700, color: "#6366f1" }}>{progressPct}%</span>
              </div>
              <div style={ui.progressBarBg}>
                <div style={{ ...ui.progressBarFill, width: `${progressPct}%` }} />
              </div>
            </div>
          )}

          {/* Error Message */}
          {errorMsg && (
            <div style={ui.errorBanner}>
              ⚠️ {errorMsg}
            </div>
          )}
        </div>

        {/* RIGHT COLUMN: Video Showcase Player */}
        <div style={ui.card}>
          <h2 style={{ fontSize: "1.1rem", fontWeight: 700, color: "#fff", marginBottom: "16px", display: "flex", alignItems: "center", gap: "8px" }}>
            <span>📺</span> Video Preview
          </h2>

          {currentVideo ? (
            <div style={ui.playerContainer}>
              <video
                controls
                autoPlay
                loop
                style={{
                  ...ui.videoPlayer,
                  maxHeight: format === "9:16" ? "540px" : "360px",
                  aspectRatio: format === "9:16" ? "9/16" : "16/9"
                }}
                src={`${BACKEND_URL}${currentVideo.download_url}`}
              />

              <div style={ui.videoMetaCard}>
                <div style={{ fontWeight: 700, color: "#fff", fontSize: "1rem" }}>
                  "{currentVideo.comment}"
                </div>
                <div style={ui.metaRow}>
                  <span>⏱️ {currentVideo.duration_formatted || `${currentVideo.duration}s`}</span>
                  <span>📦 {currentVideo.file_size_mb} MB</span>
                  <span>📐 {currentVideo.resolution}</span>
                  <span style={{ color: "#a5b4fc" }}>🎨 {currentVideo.style_name}</span>
                </div>

                <div style={{ display: "flex", gap: "10px", marginTop: "12px" }}>
                  <a
                    href={`${BACKEND_URL}${currentVideo.download_url}`}
                    download
                    style={ui.downloadBtn}
                  >
                    ⬇️ Download MP4 for YouTube / Instagram
                  </a>
                </div>
              </div>
            </div>
          ) : (
            <div style={ui.emptyPlayer}>
              <div style={{ fontSize: "3rem", marginBottom: "12px" }}>🎬</div>
              <div style={{ fontWeight: 600, color: "#94a3b8" }}>No video generated yet</div>
              <div style={{ fontSize: "0.8rem", color: "#64748b", marginTop: "4px" }}>
                Enter a topic on the left and click Generate to create a viral Short or Video.
              </div>
            </div>
          )}

          {/* Recent Videos Library */}
          <div style={{ marginTop: "32px" }}>
            <h3 style={{ fontSize: "0.95rem", fontWeight: 700, color: "#cbd5e1", marginBottom: "12px", display: "flex", alignItems: "center", gap: "6px" }}>
              <span>📁</span> Recent Creations ({library.length})
            </h3>

            <div style={ui.libraryList}>
              {library.length === 0 ? (
                <div style={{ fontSize: "0.8rem", color: "#64748b" }}>No previous videos found.</div>
              ) : (
                library.slice(0, 5).map((item, i) => (
                  <div key={i} style={ui.libraryItem}>
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div style={ui.libraryItemTitle} title={item.comment || item.filename}>
                        "{item.comment || item.filename}"
                      </div>
                      <div style={{ fontSize: "0.75rem", color: "#64748b" }}>
                        {item.style_name || "Video"} • {item.duration_formatted || `${item.duration}s`} • {item.file_size_mb} MB
                      </div>
                    </div>
                    <div style={{ display: "flex", gap: "6px" }}>
                      <button
                        type="button"
                        onClick={() => setCurrentVideo(item)}
                        style={ui.smallBtn}
                      >
                        ▶️ Play
                      </button>
                      <a
                        href={`${BACKEND_URL}${item.download_url}`}
                        download
                        style={ui.smallBtn}
                      >
                        ⬇️
                      </a>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// ── Stylesheet ──────────────────────────────────────────────────────────────
const ui = {
  wrapper: {
    maxWidth: "1240px",
    margin: "0 auto",
    fontFamily: "'Inter', sans-serif",
    color: "#f1f5f9"
  },
  header: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: "28px",
    flexWrap: "wrap",
    gap: "16px"
  },
  brandWrap: {
    display: "flex",
    alignItems: "center",
    gap: "16px"
  },
  brandIcon: {
    width: "48px",
    height: "48px",
    borderRadius: "14px",
    background: "linear-gradient(135deg, #6366f1, #ec4899)",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    fontSize: "24px",
    boxShadow: "0 8px 24px rgba(99, 102, 241, 0.4)"
  },
  title: {
    margin: 0,
    fontSize: "1.6rem",
    fontWeight: 800,
    fontFamily: "'Outfit', sans-serif",
    background: "linear-gradient(120deg, #fff, #cbd5e1)",
    WebkitBackgroundClip: "text",
    WebkitTextFillColor: "transparent"
  },
  subtitle: {
    margin: "4px 0 0 0",
    fontSize: "0.85rem",
    color: "#94a3b8"
  },
  modePills: {
    display: "flex",
    gap: "8px",
    background: "rgba(15, 23, 42, 0.8)",
    padding: "4px",
    borderRadius: "12px",
    border: "1px solid rgba(255,255,255,0.08)"
  },
  modeBtn: {
    padding: "8px 14px",
    fontSize: "0.8rem",
    fontWeight: 600,
    borderRadius: "8px",
    border: "none",
    cursor: "pointer",
    transition: "all 0.2s"
  },
  grid: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(420px, 1fr))",
    gap: "24px",
    alignItems: "start"
  },
  card: {
    background: "rgba(15, 23, 42, 0.75)",
    backdropFilter: "blur(20px)",
    border: "1px solid rgba(255, 255, 255, 0.08)",
    borderRadius: "20px",
    padding: "24px",
    boxShadow: "0 12px 36px rgba(0, 0, 0, 0.4)"
  },
  field: {
    marginBottom: "18px"
  },
  label: {
    display: "block",
    fontSize: "0.82rem",
    fontWeight: 600,
    color: "#cbd5e1",
    marginBottom: "8px"
  },
  textarea: {
    width: "100%",
    padding: "12px 16px",
    borderRadius: "12px",
    border: "1px solid rgba(255, 255, 255, 0.1)",
    background: "rgba(7, 10, 18, 0.6)",
    color: "#fff",
    fontSize: "0.9rem",
    boxSizing: "border-box",
    outline: "none",
    resize: "vertical"
  },
  input: {
    width: "100%",
    padding: "10px 14px",
    borderRadius: "10px",
    border: "1px solid rgba(255, 255, 255, 0.1)",
    background: "rgba(7, 10, 18, 0.6)",
    color: "#fff",
    fontSize: "0.85rem",
    boxSizing: "border-box",
    outline: "none"
  },
  select: {
    width: "100%",
    padding: "10px 14px",
    borderRadius: "10px",
    border: "1px solid rgba(255, 255, 255, 0.1)",
    background: "rgba(7, 10, 18, 0.8)",
    color: "#fff",
    fontSize: "0.85rem",
    boxSizing: "border-box",
    outline: "none"
  },
  presetsRow: {
    display: "flex",
    gap: "6px",
    alignItems: "center",
    marginTop: "8px",
    flexWrap: "wrap"
  },
  presetChip: {
    padding: "4px 8px",
    fontSize: "0.72rem",
    borderRadius: "6px",
    background: "rgba(99, 102, 241, 0.12)",
    color: "#a5b4fc",
    border: "1px solid rgba(99, 102, 241, 0.3)",
    cursor: "pointer"
  },
  formatToggle: {
    display: "grid",
    gridTemplateColumns: "1fr 1fr",
    gap: "10px"
  },
  formatBtn: {
    display: "flex",
    alignItems: "center",
    gap: "10px",
    padding: "12px",
    borderRadius: "12px",
    border: "1px solid",
    cursor: "pointer",
    textAlign: "left"
  },
  stylesGrid: {
    display: "grid",
    gridTemplateColumns: "1fr 1fr",
    gap: "8px"
  },
  styleCard: {
    display: "flex",
    alignItems: "center",
    gap: "8px",
    padding: "10px",
    borderRadius: "10px",
    border: "1px solid",
    cursor: "pointer"
  },
  row2: {
    display: "grid",
    gridTemplateColumns: "1fr 1fr",
    gap: "12px"
  },
  submitBtn: {
    width: "100%",
    padding: "14px 20px",
    borderRadius: "12px",
    background: "linear-gradient(135deg, #6366f1, #8b5cf6)",
    color: "#fff",
    border: "none",
    fontSize: "1rem",
    fontWeight: 700,
    boxShadow: "0 6px 20px rgba(99, 102, 241, 0.4)",
    marginTop: "8px"
  },
  progressWrap: {
    marginTop: "16px",
    background: "rgba(7, 10, 18, 0.6)",
    borderRadius: "12px",
    padding: "14px",
    border: "1px solid rgba(99, 102, 241, 0.3)"
  },
  progressHeader: {
    display: "flex",
    justifyContent: "space-between",
    marginBottom: "8px"
  },
  progressBarBg: {
    width: "100%",
    height: "8px",
    background: "rgba(255,255,255,0.08)",
    borderRadius: "4px",
    overflow: "hidden"
  },
  progressBarFill: {
    height: "100%",
    background: "linear-gradient(90deg, #6366f1, #ec4899)",
    borderRadius: "4px",
    transition: "width 0.4s ease"
  },
  errorBanner: {
    marginTop: "14px",
    padding: "12px",
    borderRadius: "10px",
    background: "rgba(239, 68, 68, 0.15)",
    border: "1px solid rgba(239, 68, 68, 0.4)",
    color: "#fca5a5",
    fontSize: "0.85rem"
  },
  playerContainer: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center"
  },
  videoPlayer: {
    width: "100%",
    borderRadius: "16px",
    backgroundColor: "#000",
    boxShadow: "0 12px 32px rgba(0,0,0,0.6)"
  },
  videoMetaCard: {
    width: "100%",
    marginTop: "14px",
    padding: "14px",
    borderRadius: "12px",
    background: "rgba(7, 10, 18, 0.6)",
    border: "1px solid rgba(255,255,255,0.08)",
    boxSizing: "border-box"
  },
  metaRow: {
    display: "flex",
    gap: "12px",
    flexWrap: "wrap",
    fontSize: "0.8rem",
    color: "#94a3b8",
    marginTop: "6px"
  },
  downloadBtn: {
    flex: 1,
    padding: "10px 14px",
    borderRadius: "10px",
    background: "linear-gradient(135deg, #10b981, #059669)",
    color: "#fff",
    textDecoration: "none",
    textAlign: "center",
    fontWeight: 700,
    fontSize: "0.85rem",
    boxShadow: "0 4px 14px rgba(16, 185, 129, 0.4)"
  },
  emptyPlayer: {
    padding: "48px 24px",
    textAlign: "center",
    border: "2px dashed rgba(255,255,255,0.1)",
    borderRadius: "16px",
    color: "#64748b"
  },
  libraryList: {
    display: "flex",
    flexDirection: "column",
    gap: "8px"
  },
  libraryItem: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    padding: "10px 14px",
    borderRadius: "10px",
    background: "rgba(7, 10, 18, 0.5)",
    border: "1px solid rgba(255,255,255,0.06)",
    gap: "10px"
  },
  libraryItemTitle: {
    fontSize: "0.85rem",
    fontWeight: 600,
    color: "#f1f5f9",
    whiteSpace: "nowrap",
    overflow: "hidden",
    textOverflow: "ellipsis"
  },
  smallBtn: {
    padding: "6px 10px",
    fontSize: "0.75rem",
    fontWeight: 600,
    borderRadius: "6px",
    background: "rgba(255,255,255,0.1)",
    color: "#fff",
    border: "none",
    cursor: "pointer",
    textDecoration: "none"
  }
};
