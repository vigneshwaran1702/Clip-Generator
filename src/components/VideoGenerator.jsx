import { useEffect, useRef, useState } from "react";
import { supabase } from "../lib/supabase";

export default function VideoGenerator() {
  const [prompt, setPrompt] = useState("");
  const [mode, setMode] = useState("text");
  const [imageUrl, setImageUrl] = useState("");
  const [duration, setDuration] = useState(5);
  const [status, setStatus] = useState("idle");
  const [videoUrl, setVideoUrl] = useState("");
  const [error, setError] = useState("");
  const [user, setUser] = useState(null);
  const [authEmail, setAuthEmail] = useState("");
  const [authPassword, setAuthPassword] = useState("");
  const [authLoading, setAuthLoading] = useState(false);
  const timer = useRef(null);

  // Check auth session
  useEffect(() => {
    supabase.auth.getSession().then(({ data: { session } }) => {
      setUser(session?.user ?? null);
    });

    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, session) => {
      setUser(session?.user ?? null);
    });

    return () => {
      subscription.unsubscribe();
      clearTimeout(timer.current);
    };
  }, []);

  async function handleAnonymousSignIn() {
    setAuthLoading(true);
    setError("");
    try {
      const { data, error: signInErr } = await supabase.auth.signInAnonymously();
      if (signInErr) throw signInErr;
      setUser(data.user);
    } catch (err) {
      setError(err.message || "Could not sign in anonymously. Enable anonymous sign-ins in Supabase dashboard or use email sign-in.");
    } finally {
      setAuthLoading(false);
    }
  }

  async function handleEmailSignIn(e) {
    e.preventDefault();
    if (!authEmail || !authPassword) {
      setError("Please enter both email and password.");
      return;
    }
    setAuthLoading(true);
    setError("");
    try {
      const { data, error: signInErr } = await supabase.auth.signInWithPassword({
        email: authEmail,
        password: authPassword,
      });
      if (signInErr) {
        // Try sign-up if user doesn't exist
        const { data: signUpData, error: signUpErr } = await supabase.auth.signUp({
          email: authEmail,
          password: authPassword,
        });
        if (signUpErr) throw signUpErr;
        setUser(signUpData.user);
      } else {
        setUser(data.user);
      }
    } catch (err) {
      setError(err.message || "Authentication failed.");
    } finally {
      setAuthLoading(false);
    }
  }

  async function handleSignOut() {
    await supabase.auth.signOut();
    setUser(null);
  }

  async function generateVideo(event) {
    event.preventDefault();
    clearTimeout(timer.current);
    setError("");
    setVideoUrl("");

    if (!user) {
      setError("Please sign in or continue anonymously first to create a video job.");
      return;
    }

    if (!prompt.trim()) {
      setError("Enter a video prompt.");
      return;
    }

    if (mode === "image" && (!imageUrl || !imageUrl.startsWith("https://"))) {
      setError("Upload an image first with a valid public https:// URL.");
      return;
    }

    setStatus("submitting");

    try {
      const { data, error: invokeError } = await supabase.functions.invoke(
        "create-video",
        {
          body: {
            prompt: prompt.trim(),
            mode,
            duration: Number(duration),
            ...(mode === "image" ? { image_url: imageUrl.trim() } : {}),
          },
        }
      );

      if (invokeError) throw invokeError;
      if (!data?.request_id) {
        throw new Error(data?.error || "Could not start generation.");
      }

      setStatus("queued");
      pollStatus(data.request_id);
    } catch (err) {
      setStatus("failed");
      setError(err.message || "Generation could not start.");
    }
  }

  async function pollStatus(requestId) {
    try {
      const { data, error: invokeError } = await supabase.functions.invoke(
        "video-status",
        {
          body: { request_id: requestId },
        }
      );

      if (invokeError) throw invokeError;
      if (data?.error) throw new Error(data.error);

      if (data.status === "completed" && data.video_url) {
        setVideoUrl(data.video_url);
        setStatus("completed");
        return;
      }

      if (data.status === "failed") {
        throw new Error("Video generation failed. Try another prompt.");
      }

      setStatus(data.status || "in_progress");
      timer.current = setTimeout(() => pollStatus(requestId), 4000);
    } catch (err) {
      setStatus("failed");
      setError(err.message || "Unable to check video status.");
    }
  }

  const isBusy = ["submitting", "queued", "in_progress", "in_queue"].includes(
    status
  );

  return (
    <div style={styles.card}>
      <div style={styles.headerRow}>
        <div style={styles.brandTitle}>
          <span style={{ fontSize: "1.6rem" }}>⚡</span>
          <div>
            <h2 style={styles.heading}>Fal.ai Wan v2.7 Video Generator</h2>
            <p style={styles.subheading}>
              Serverless Edge AI Video via Supabase Edge Functions & Fal.ai
            </p>
          </div>
        </div>
        {user ? (
          <div style={styles.userBadge}>
            <span>👤 {user.email || "Guest User"}</span>
            <button onClick={handleSignOut} style={styles.smallBtn}>
              Sign Out
            </button>
          </div>
        ) : (
          <div style={styles.authNotice}>
            <button
              onClick={handleAnonymousSignIn}
              disabled={authLoading}
              style={styles.guestBtn}
            >
              {authLoading ? "Signing in..." : "⚡ 1-Click Guest Login"}
            </button>
          </div>
        )}
      </div>

      {!user && (
        <div style={styles.authBox}>
          <p style={{ margin: "0 0 10px 0", fontSize: "0.85rem", color: "#94a3b8" }}>
            Sign in is required by Supabase RLS policies so each job is tracked to your account.
          </p>
          <form onSubmit={handleEmailSignIn} style={styles.authForm}>
            <input
              type="email"
              placeholder="Email address"
              value={authEmail}
              onChange={(e) => setAuthEmail(e.target.value)}
              style={styles.input}
            />
            <input
              type="password"
              placeholder="Password"
              value={authPassword}
              onChange={(e) => setAuthPassword(e.target.value)}
              style={styles.input}
            />
            <button type="submit" disabled={authLoading} style={styles.secondaryBtn}>
              Sign In / Up with Email
            </button>
          </form>
        </div>
      )}

      <form onSubmit={generateVideo} style={{ marginTop: "18px" }}>
        <div style={styles.gridRow}>
          <label style={styles.label}>
            Generation Mode
            <select
              value={mode}
              onChange={(e) => setMode(e.target.value)}
              style={styles.select}
            >
              <option value="text">Text to Video (fal-ai/wan/v2.7/text-to-video)</option>
              <option value="image">Image to Video (fal-ai/wan/v2.7/image-to-video)</option>
            </select>
          </label>

          <label style={styles.label}>
            Duration
            <select
              value={duration}
              onChange={(e) => setDuration(Number(e.target.value))}
              style={styles.select}
            >
              <option value={5}>5 seconds</option>
              <option value={10}>10 seconds</option>
            </select>
          </label>
        </div>

        {mode === "image" && (
          <label style={{ ...styles.label, marginTop: "12px" }}>
            Uploaded Image URL (must be public HTTPS)
            <input
              type="url"
              value={imageUrl}
              onChange={(e) => setImageUrl(e.target.value)}
              placeholder="https://images.unsplash.com/photo-..."
              style={styles.input}
            />
          </label>
        )}

        <label style={{ ...styles.label, marginTop: "14px" }}>
          Describe your video (Prompt)
          <textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            maxLength={5000}
            required
            rows={4}
            placeholder="A cinematic drone shot of a futuristic cyberpunk city with neon reflections in rain..."
            style={styles.textarea}
          />
        </label>

        <div style={{ marginTop: "18px" }}>
          <button
            type="submit"
            disabled={isBusy}
            style={isBusy ? styles.btnDisabled : styles.btnPrimary}
          >
            {status === "submitting"
              ? "Submitting to Queue..."
              : isBusy
              ? `Generating Video (${status})...`
              : "🚀 Generate Video via Wan v2.7"}
          </button>
        </div>

        {status !== "idle" && (
          <div style={styles.statusBox}>
            <span style={styles.pulseDot(isBusy)}></span>
            <p role="status" style={{ margin: 0, fontWeight: 500 }}>
              {isBusy
                ? `Job Status: ${status.toUpperCase()} — Fal.ai is rendering your high-fidelity clip...`
                : status === "completed"
                ? "✨ Video ready!"
                : "Generation paused."}
            </p>
          </div>
        )}

        {error && (
          <div style={styles.errorAlert} role="alert">
            ⚠️ {error}
          </div>
        )}

        {videoUrl && (
          <div style={styles.videoResultCard}>
            <h3 style={{ margin: "0 0 12px 0", color: "#4ade80" }}>🎉 Generated AI Video</h3>
            <video
              src={videoUrl}
              controls
              playsInline
              autoPlay
              loop
              style={styles.videoPlayer}
            />
            <div style={{ marginTop: "12px", display: "flex", gap: "10px" }}>
              <a
                href={videoUrl}
                target="_blank"
                rel="noreferrer"
                style={styles.downloadLink}
              >
                ↗️ Open in New Tab
              </a>
              <a
                href={videoUrl}
                download="ai_generated_video.mp4"
                style={styles.downloadLink}
              >
                ⬇️ Download Video (.mp4)
              </a>
            </div>
          </div>
        )}
      </form>
    </div>
  );
}

const styles = {
  card: {
    background: "#0f172a",
    border: "1px solid #22324e",
    borderRadius: "16px",
    padding: "28px",
    maxWidth: "800px",
    margin: "0 auto",
    color: "#f1f5f9",
    fontFamily: "'Inter', sans-serif",
    boxShadow: "0 10px 30px rgba(0, 0, 0, 0.4)",
  },
  headerRow: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    flexWrap: "wrap",
    gap: "14px",
    paddingBottom: "18px",
    borderBottom: "1px solid #1e293b",
  },
  brandTitle: {
    display: "flex",
    alignItems: "center",
    gap: "12px",
  },
  heading: {
    fontSize: "1.3rem",
    fontWeight: "700",
    margin: 0,
    background: "linear-gradient(120deg, #ffffff, #a5b4fc)",
    WebkitBackgroundClip: "text",
    WebkitTextFillColor: "transparent",
  },
  subheading: {
    fontSize: "0.82rem",
    color: "#94a3b8",
    margin: "4px 0 0 0",
  },
  userBadge: {
    display: "flex",
    alignItems: "center",
    gap: "10px",
    background: "#1e293b",
    padding: "6px 12px",
    borderRadius: "20px",
    fontSize: "0.82rem",
    color: "#c7d2fe",
  },
  smallBtn: {
    background: "transparent",
    border: "1px solid #475569",
    color: "#cbd5e1",
    padding: "3px 8px",
    borderRadius: "12px",
    cursor: "pointer",
    fontSize: "0.75rem",
  },
  guestBtn: {
    background: "linear-gradient(135deg, #6366f1, #8b5cf6)",
    color: "#ffffff",
    border: "none",
    padding: "8px 16px",
    borderRadius: "10px",
    cursor: "pointer",
    fontWeight: "600",
    fontSize: "0.82rem",
  },
  authNotice: {
    display: "flex",
    gap: "8px",
  },
  authBox: {
    marginTop: "16px",
    padding: "14px",
    background: "#141e33",
    borderRadius: "12px",
    border: "1px solid #1e293b",
  },
  authForm: {
    display: "flex",
    gap: "10px",
    flexWrap: "wrap",
  },
  gridRow: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
    gap: "16px",
  },
  label: {
    display: "flex",
    flexDirection: "column",
    gap: "6px",
    fontSize: "0.88rem",
    fontWeight: "500",
    color: "#cbd5e1",
  },
  input: {
    background: "#070a12",
    border: "1px solid #22324e",
    borderRadius: "8px",
    padding: "10px 14px",
    color: "#f1f5f9",
    fontSize: "0.9rem",
    outline: "none",
  },
  select: {
    background: "#070a12",
    border: "1px solid #22324e",
    borderRadius: "8px",
    padding: "10px 14px",
    color: "#f1f5f9",
    fontSize: "0.9rem",
    outline: "none",
  },
  textarea: {
    background: "#070a12",
    border: "1px solid #22324e",
    borderRadius: "8px",
    padding: "12px 14px",
    color: "#f1f5f9",
    fontSize: "0.9rem",
    outline: "none",
    resize: "vertical",
    fontFamily: "inherit",
  },
  btnPrimary: {
    width: "100%",
    padding: "14px",
    background: "linear-gradient(135deg, #6366f1 0%, #a855f7 100%)",
    color: "#ffffff",
    border: "none",
    borderRadius: "10px",
    fontWeight: "700",
    fontSize: "1rem",
    cursor: "pointer",
    boxShadow: "0 4px 16px rgba(99, 102, 241, 0.4)",
    transition: "transform 0.15s ease",
  },
  btnDisabled: {
    width: "100%",
    padding: "14px",
    background: "#334155",
    color: "#94a3b8",
    border: "none",
    borderRadius: "10px",
    fontWeight: "700",
    fontSize: "1rem",
    cursor: "not-allowed",
  },
  secondaryBtn: {
    background: "#334155",
    color: "#ffffff",
    border: "none",
    padding: "10px 16px",
    borderRadius: "8px",
    cursor: "pointer",
    fontSize: "0.85rem",
    fontWeight: "600",
  },
  statusBox: {
    marginTop: "16px",
    display: "flex",
    alignItems: "center",
    gap: "10px",
    padding: "12px 16px",
    background: "#141e33",
    borderRadius: "10px",
    border: "1px solid #22324e",
    fontSize: "0.88rem",
    color: "#cbd5e1",
  },
  pulseDot: (active) => ({
    width: "10px",
    height: "10px",
    borderRadius: "50%",
    background: active ? "#38bdf8" : "#22c55e",
    boxShadow: active ? "0 0 10px #38bdf8" : "none",
  }),
  errorAlert: {
    marginTop: "14px",
    padding: "12px 16px",
    background: "rgba(239, 68, 68, 0.15)",
    border: "1px solid rgba(239, 68, 68, 0.4)",
    borderRadius: "10px",
    color: "#fca5a5",
    fontSize: "0.88rem",
  },
  videoResultCard: {
    marginTop: "20px",
    padding: "16px",
    background: "#141e33",
    borderRadius: "12px",
    border: "1px solid #22324e",
  },
  videoPlayer: {
    width: "100%",
    maxWidth: "720px",
    borderRadius: "8px",
    maxHeight: "420px",
    backgroundColor: "#000",
  },
  downloadLink: {
    display: "inline-block",
    padding: "8px 14px",
    background: "#334155",
    color: "#ffffff",
    textDecoration: "none",
    borderRadius: "8px",
    fontSize: "0.82rem",
    fontWeight: "600",
  },
};
