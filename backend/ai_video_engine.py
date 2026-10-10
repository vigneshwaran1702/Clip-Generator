"""
AI Video Generation Engine for AI-Clip-Generator
Transforms any comment, prompt, or topic into a full short video with:
- Intelligent scriptwriting / storyboarding (Hook, Beats, Climax, Outro)
- Ultra-realistic neural voiceover (Edge-TTS with multiple voices)
- AI-generated scene visuals (Pollinations AI + dynamic PIL fallback)
- Cinematic motion (Ken Burns zoom/pan effect)
- Bold viral animated subtitles (9:16 / 16:9 positioned)
- Ambient background music & professional audio mixing
"""

import os
import re
import sys
import io
import json
import time
import uuid
import math
import random
import asyncio
import subprocess
import urllib.request
import urllib.parse
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# Ensure UTF-8 output on Windows consoles
if sys.stdout and hasattr(sys.stdout, "buffer") and sys.stdout.encoding != "utf-8":
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
    except Exception:
        pass

# Path to ffmpeg / ffprobe
FFMPEG_PATH = r"C:\Users\hp\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1.1-full_build\bin\ffmpeg.exe"
FFPROBE_PATH = FFMPEG_PATH.replace("ffmpeg.exe", "ffprobe.exe")

# Available high quality voices
AVAILABLE_VOICES = [
    {"id": "en-US-ChristopherNeural", "name": "Christopher", "gender": "Male", "tone": "Deep, Cinematic & Authoritative"},
    {"id": "en-US-JennyNeural", "name": "Jenny", "gender": "Female", "tone": "Clear, Natural & Engaging"},
    {"id": "en-US-GuyNeural", "name": "Guy", "gender": "Male", "tone": "Casual, Energetic & Modern"},
    {"id": "en-US-AriaNeural", "name": "Aria", "gender": "Female", "tone": "Expressive, Storyteller"},
    {"id": "en-GB-RyanNeural", "name": "Ryan (British)", "gender": "Male", "tone": "Documentary, Sophisticated"},
    {"id": "en-GB-SoniaNeural", "name": "Sonia (British)", "gender": "Female", "tone": "Warm, Crisp & Refined"},
]

POPULAR_PRESETS = [
    {
        "title": "Why Cats Purr",
        "comment": "Why do cats purr? The hidden healing frequency science discovered.",
        "style": "cinematic"
    },
    {
        "title": "Black Hole Horizon",
        "comment": "What actually happens to your body when you cross the event horizon of a black hole?",
        "style": "space"
    },
    {
        "title": "The 2-Minute Rule",
        "comment": "How the 2-minute rule can rewire your brain and crush procrastination instantly.",
        "style": "photorealistic"
    },
    {
        "title": "Mariana Trench Mystery",
        "comment": "Terrifying creatures and anomalies found 36,000 feet deep in the Mariana Trench.",
        "style": "cyberpunk"
    },
    {
        "title": "What If the Moon Vanished?",
        "comment": "What would happen to Earth within 24 hours if the Moon suddenly disappeared?",
        "style": "cinematic"
    }
]


def log_safe(msg: str):
    try:
        print(msg, flush=True)
    except Exception:
        clean = msg.encode("ascii", "replace").decode("ascii")
        print(clean, flush=True)


def clean_text_for_voice(text: str) -> str:
    """Clean text for natural speech synthesis."""
    text = re.sub(r'[\*\_#`~]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def generate_script_from_comment(comment: str, style: str = "cinematic", target_duration: int = 30) -> list[dict]:
    """
    Generate structured scenes from user's comment / prompt.
    Each scene has:
      - narration: spoken words
      - visual_prompt: descriptive prompt for image generation
      - title: brief scene label
    """
    comment = comment.strip()
    
    # Check if user already provided numbered scenes or script
    if re.search(r'(scene\s*\d+|hook:|beat\s*\d+)', comment, re.IGNORECASE):
        lines = [line.strip() for line in comment.split("\n") if line.strip()]
        scenes = []
        for i, line in enumerate(lines[:5]):
            clean_l = clean_text_for_voice(line)
            scenes.append({
                "title": f"Scene {i+1}",
                "narration": clean_l,
                "visual_prompt": f"{clean_l[:70]}, {style} style, 8k, photorealistic"
            })
        if scenes:
            return scenes

    lower = comment.lower()

    if any(w in lower for w in ["cat", "dog", "animal", "pet", "creature", "lion", "tiger"]):
        theme = "wildlife"
    elif any(w in lower for w in ["space", "moon", "star", "black hole", "mars", "galaxy", "universe", "planet"]):
        theme = "space"
    elif any(w in lower for w in ["brain", "habit", "productivity", "psychology", "mind", "focus", "success"]):
        theme = "mind"
    elif any(w in lower for w in ["ocean", "sea", "trench", "water", "shark", "deep", "mariana"]):
        theme = "ocean"
    elif any(w in lower for w in ["future", "ai", "robot", "tech", "cyber", "quantum", "computer"]):
        theme = "tech"
    elif any(w in lower for w in ["history", "ancient", "pyramid", "empire", "lost", "rome"]):
        theme = "history"
    else:
        theme = "general"

    title_hook = comment.rstrip(".!?")

    if theme == "space":
        scenes = [
            {
                "title": "The Cosmic Hook",
                "narration": f"Have you ever wondered about this? {title_hook}.",
                "visual_prompt": f"Cosmic void, glowing nebula, cinematic space, hyperdetailed, 8k, {style} style"
            },
            {
                "title": "The Phenomenon",
                "narration": "Deep in the infinite expanse of the universe, the laws of physics bend in ways we can barely comprehend.",
                "visual_prompt": f"Vast galaxies colliding, radiant starlight, gravitational lensing, {style} lighting"
            },
            {
                "title": "The Mind-Blowing Fact",
                "narration": "Scientists found that time and light itself stretch, creating an eerie cosmic illusion unlike anything on Earth.",
                "visual_prompt": f"Dramatic space anomaly, glowing event horizon, vibrant atmospheric dust, ultra high definition"
            },
            {
                "title": "The Final Thought",
                "narration": "Would you ever dare to venture beyond the unknown? Let us know in the comments.",
                "visual_prompt": f"Astronaut looking into an endless star field, cinematic reflections, breathtaking vista, {style}"
            }
        ]
    elif theme == "ocean":
        scenes = [
            {
                "title": "The Deep Hook",
                "narration": f"Think you know the oceans? {title_hook}.",
                "visual_prompt": f"Dark abyssal ocean trench, bioluminescent glowing organisms, underwater atmosphere, {style}"
            },
            {
                "title": "The Hidden World",
                "narration": "Over eighty percent of our oceans remain completely unexplored and shrouded in pitch black silence.",
                "visual_prompt": f"Underwater submarine light beam revealing mysterious underwater cavern, deep sea creatures, {style}"
            },
            {
                "title": "The Discovery",
                "narration": "At crushing pressures, creatures thrive using frequencies and bioluminescence that baffle modern science.",
                "visual_prompt": f"Enormous mystical glowing deep sea creature, glowing tendrils, cinematic underwater photography"
            },
            {
                "title": "Final Mystery",
                "narration": "The true aliens of this world might already be living right beneath our waves.",
                "visual_prompt": f"Silhouette of deep ocean trench descending into infinity, eerie blue light, {style}"
            }
        ]
    elif theme == "mind":
        scenes = [
            {
                "title": "The Mental Shift",
                "narration": f"Listen closely, because this could change your life. {title_hook}.",
                "visual_prompt": f"Glowing human brain with neural synapses firing, neon energy, cinematic studio lighting, {style}"
            },
            {
                "title": "The Psychological Secret",
                "narration": "Your brain is hardwired to protect you from discomfort, which is why starting is always the hardest part.",
                "visual_prompt": f"Person standing at a glowing crossroads, futuristic minimalist architecture, high contrast, {style}"
            },
            {
                "title": "The Breakthrough",
                "narration": "Once you break that initial friction, neurochemicals kick in, turning resistance into effortless momentum.",
                "visual_prompt": f"Golden burst of light expanding through mind, cinematic lighting, sleek aesthetic, 8k"
            },
            {
                "title": "Take Action",
                "narration": "Try this today for just two minutes, and watch your focus transform completely.",
                "visual_prompt": f"Silhouette of determined person looking at sunrise over modern city, cinematic depth of field, {style}"
            }
        ]
    elif theme == "wildlife":
        scenes = [
            {
                "title": "The Wild Hook",
                "narration": f"Here is something you probably never knew: {title_hook}.",
                "visual_prompt": f"Close up majestic cat with vibrant eyes, warm cinematic natural lighting, 8k photograph, {style}"
            },
            {
                "title": "The Secret Purpose",
                "narration": "This sound vibrates at an exact frequency between twenty and one hundred and forty Hertz.",
                "visual_prompt": f"Soundwaves vibrating through glowing golden light, artistic macro photography, {style}"
            },
            {
                "title": "The Science",
                "narration": "In human medicine, that identical frequency is used to stimulate bone density and tissue repair.",
                "visual_prompt": f"A feline resting peacefully surrounded by ethereal healing aura, photorealistic, cinematic"
            },
            {
                "title": "The Bond",
                "narration": "So when they do this beside you, they might just be healing both themselves and you.",
                "visual_prompt": f"Emotional cozy cinematic scene, warm sunset sunlight streaming through window, {style}"
            }
        ]
    elif theme == "tech":
        scenes = [
            {
                "title": "The Digital Frontier",
                "narration": f"We are on the verge of a technological revolution. {title_hook}.",
                "visual_prompt": f"Futuristic cyberpunk cyber metropolis, flying vehicles, neon holographic displays, 8k, {style}"
            },
            {
                "title": "The Architecture",
                "narration": "Beneath silicon chips and neural networks, synthetic intelligence is learning at an exponential rate.",
                "visual_prompt": f"Gleaming quantum computer processor glowing with turquoise lasers, cinematic tech, 8k"
            },
            {
                "title": "The Paradigm Shift",
                "narration": "What once took decades of human effort can now be computed in a single millisecond.",
                "visual_prompt": f"Streams of digital data flowing like liquid light across a futuristic sphere, hyperdetailed"
            },
            {
                "title": "The Horizon",
                "narration": "The question is no longer if this will reshape society, but how fast we will adapt.",
                "visual_prompt": f"Silhouette standing on digital glass rooftop looking into a luminous cyber horizon, {style}"
            }
        ]
    else:
        scenes = [
            {
                "title": "The Hook",
                "narration": f"Did you know? {title_hook}.",
                "visual_prompt": f"Dramatic cinematic scene representing {comment[:50]}, dramatic volumetric lighting, 8k, {style}"
            },
            {
                "title": "The Reality",
                "narration": "Most people assume this is simple, but the deeper reality is far more intriguing.",
                "visual_prompt": f"Intricate visual details of {comment[:40]}, mysterious atmosphere, hyperdetailed cinematic, {style}"
            },
            {
                "title": "The Revelation",
                "narration": "When you break down what actually happens, everything you thought you knew gets flipped upside down.",
                "visual_prompt": f"Epic visual crescendo, radiant colors, breathtaking perspective, cinematic composition, {style}"
            },
            {
                "title": "The Outro",
                "narration": "What do you think about this? Drop your thoughts below and follow for more.",
                "visual_prompt": f"Striking final shot, clean modern aesthetic, evocative lighting, 8k masterpiece, {style}"
            }
        ]

    return scenes


async def generate_voiceover(scenes: list[dict], voice_id: str, output_audio_path: str) -> tuple[float, list[dict]]:
    """
    Generate neural TTS audio using edge-tts.
    Returns (total_duration_seconds, timed_scenes).
    """
    import edge_tts

    full_narration = " ".join(s["narration"] for s in scenes)
    log_safe(f"[VOICE] Synthesizing narration with {voice_id} ({len(full_narration)} chars)...")

    communicate = edge_tts.Communicate(full_narration, voice_id)
    
    sub_events = []
    audio_bytes = bytearray()

    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_bytes.extend(chunk["data"])
        elif chunk["type"] in ("SentenceBoundary", "WordBoundary"):
            offset_sec = chunk.get("offset", 0) / 10_000_000.0
            duration_sec = chunk.get("duration", 0) / 10_000_000.0
            sub_events.append({
                "type": chunk["type"],
                "start": offset_sec,
                "end": offset_sec + duration_sec,
                "text": chunk.get("text", "")
            })

    with open(output_audio_path, "wb") as f:
        f.write(audio_bytes)

    duration = get_audio_duration(output_audio_path)
    if duration <= 0:
        duration = 15.0

    total_words = sum(len(s["narration"].split()) for s in scenes) or 1
    current_time = 0.0
    for s in scenes:
        words = len(s["narration"].split()) or 1
        scene_dur = max(2.5, (words / total_words) * duration)
        s["start_time"] = round(current_time, 2)
        s["duration"] = round(scene_dur, 2)
        s["end_time"] = round(current_time + scene_dur, 2)
        current_time += scene_dur

    return duration, sub_events


def get_audio_duration(filepath: str) -> float:
    """Get precise duration of audio file via ffprobe."""
    try:
        cmd = [
            FFPROBE_PATH, "-v", "quiet",
            "-print_format", "json",
            "-show_format", filepath
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, errors="replace", timeout=15)
        data = json.loads(res.stdout)
        return float(data["format"]["duration"])
    except Exception as e:
        log_safe(f"[WARN] ffprobe duration failed: {e}")
        return 0.0


def generate_fallback_image(prompt: str, title: str, width: int, height: int, filepath: str):
    """
    Generate an artistic, cinematic visual card using PIL with dynamic gradients,
    atmospheric glow, and clean design.
    """
    img = Image.new("RGB", (width, height), color=(11, 15, 26))
    draw = ImageDraw.Draw(img)

    # Color themes
    palettes = [
        ((15, 23, 42), (99, 102, 241)),   # Indigo Night
        ((10, 15, 30), (13, 148, 136)),   # Cyber Teal
        ((24, 10, 35), (236, 72, 153)),   # Neon Magenta
        ((17, 24, 39), (245, 158, 11)),   # Amber Gold
        ((6, 78, 59), (16, 185, 129)),    # Emerald
    ]
    c1, c2 = random.choice(palettes)

    # Vertical gradient
    for y in range(height):
        ratio = y / height
        r = int(c1[0] * (1 - ratio) + c2[0] * ratio)
        g = int(c1[1] * (1 - ratio) + c2[1] * ratio)
        b = int(c1[2] * (1 - ratio) + c2[2] * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    # Ambient concentric glow rings
    center_x, center_y = width // 2, height // 2 - 60
    for radius in [100, 160, 220, 280, 360]:
        draw.arc([center_x - radius, center_y - radius, center_x + radius, center_y + radius],
                 start=0, end=360, fill=(255, 255, 255, 25), width=2)

    # Diagonal accent streaks
    for i in range(5):
        sx = random.randint(0, width)
        sy = random.randint(0, height // 2)
        draw.line([(sx, sy), (sx + 200, sy + 300)], fill=(255, 255, 255, 18), width=3)

    try:
        font_large = ImageFont.truetype("arial.ttf", size=min(width // 18, 38))
        font_small = ImageFont.truetype("arial.ttf", size=min(width // 26, 22))
        font_tag = ImageFont.truetype("arial.ttf", size=min(width // 32, 16))
    except Exception:
        font_large = font_small = font_tag = ImageFont.load_default()

    # Center card box
    box_w = width - 80
    box_h = 170
    box_x = 40
    box_y = height // 2 - 85
    draw.rounded_rectangle([box_x, box_y, box_x + box_w, box_y + box_h], radius=18, fill=(17, 24, 39, 210), outline=(99, 102, 241), width=2)

    # Tag badge
    draw.rounded_rectangle([box_x + 20, box_y + 18, box_x + 120, box_y + 44], radius=8, fill=(99, 102, 241, 100))
    draw.text((box_x + 70, box_y + 31), "AI SCENE", fill=(226, 232, 240), anchor="mm", font=font_tag)

    # Title & detail
    draw.text((width // 2, box_y + 80), title.upper(), fill=(255, 255, 255), anchor="mm", font=font_large)
    preview = (prompt[:42] + "...") if len(prompt) > 42 else prompt
    draw.text((width // 2, box_y + 125), preview, fill=(165, 180, 252), anchor="mm", font=font_small)

    img.save(filepath, "JPEG", quality=92)


def fetch_or_create_scene_image(prompt: str, title: str, width: int, height: int, filepath: str, seed: int = 42):
    """
    Fetch photorealistic AI image from Pollinations AI, or fallback to beautiful local generation.
    """
    clean_p = prompt.replace("'", "").replace('"', '').strip()
    encoded_prompt = urllib.parse.quote(f"{clean_p}, vertical 8k cinematic masterpiece, highly detailed")
    
    # Try Pollinations API
    try:
        url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}&nologo=true&seed={seed}"
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        })
        with urllib.request.urlopen(req, timeout=10) as response:
            if response.status == 200:
                with open(filepath, "wb") as f:
                    f.write(response.read())
                log_safe(f"   [AI-IMG] Online image fetched: {os.path.basename(filepath)}")
                return
    except Exception as exc:
        log_safe(f"   [FALLBACK] Using dynamic visual generator ({str(exc)[:40]})")

    # High quality fallback
    generate_fallback_image(prompt, title, width, height, filepath)


def build_ass_subtitles(scenes: list[dict], width: int, height: int, style: str = "viral_yellow") -> str:
    """
    Generate Advanced SubStation Alpha (.ass) subtitle file with viral Shorts styling.
    """
    font_size = 46 if width >= 1080 else 34
    margin_v = int(height * 0.22)  # Position at ~78% height for 9:16 Shorts

    if style == "viral_yellow":
        primary_color = "&H0000FFFF"  # Yellow BGR
        outline_color = "&H00000000"
    elif style == "neon_cyan":
        primary_color = "&H00FFFF00"  # Cyan BGR
        outline_color = "&H00000000"
    else:
        primary_color = "&H00FFFFFF"  # White
        outline_color = "&H00000000"

    ass_header = f"""[Script Info]
Title: AI Shorts Captions
ScriptType: v4.00+
PlayResX: {width}
PlayResY: {height}
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: ViralShort,Arial,{font_size},{primary_color},&H000000FF,{outline_color},&H80000000,-1,0,0,0,100,100,1,0,1,3.5,2.0,2,40,40,{margin_v},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    dialogues = []

    def format_ass_time(sec: float) -> str:
        h = int(sec // 3600)
        m = int((sec % 3600) // 60)
        s = int(sec % 60)
        cs = int((sec - int(sec)) * 100)
        return f"{h:01d}:{m:02d}:{s:02d}.{cs:02d}"

    for scene in scenes:
        narration = scene.get("narration", "")
        start_time = scene.get("start_time", 0.0)
        duration = scene.get("duration", 4.0)

        words = narration.split()
        if not words:
            continue

        chunk_size = 4
        chunks = [words[i:i + chunk_size] for i in range(0, len(words), chunk_size)]
        chunk_dur = duration / len(chunks)

        for i, chunk in enumerate(chunks):
            c_start = start_time + (i * chunk_dur)
            c_end = c_start + chunk_dur
            text = " ".join(chunk).upper()
            dialogues.append(
                f"Dialogue: 0,{format_ass_time(c_start)},{format_ass_time(c_end)},ViralShort,,0,0,0,,{text}"
            )

    return ass_header + "\n".join(dialogues) + "\n"


def generate_ambient_track(duration: float, output_path: str):
    """
    Generate soothing synthesizer audio using FFmpeg aevalsrc.
    """
    freq1 = 220.0   # A3
    freq2 = 277.18  # C#4
    freq3 = 329.63  # E4

    synth_expr = (
        f"0.06*sin(2*PI*{freq1}*t) + "
        f"0.05*sin(2*PI*{freq2}*t) + "
        f"0.04*sin(2*PI*{freq3}*t) + "
        f"0.02*sin(2*PI*440*t)"
    )

    cmd = [
        FFMPEG_PATH, "-y",
        "-f", "lavfi",
        "-i", f"aevalsrc='{synth_expr}':s=44100:d={duration+2}",
        "-af", f"afade=t=in:ss=0:d=2,afade=t=out:st={max(0, duration-2)}:d=2,volume=0.25",
        "-c:a", "aac", "-b:a", "128k",
        output_path
    ]
    subprocess.run(cmd, capture_output=True, text=True, errors="replace", timeout=20)


def create_ai_short_video(
    comment: str,
    output_dir: str,
    voice_id: str = "en-US-ChristopherNeural",
    aspect_ratio: str = "9:16",
    style: str = "cinematic",
    subtitle_style: str = "viral_yellow",
    use_bg_music: bool = True,
    target_duration: int = 30,
    progress_callback = None
) -> dict:
    """
    End-to-end AI Video Generation pipeline from a comment / prompt.
    """
    abs_output_dir = os.path.abspath(output_dir)
    os.makedirs(abs_output_dir, exist_ok=True)
    task_id = f"ai_short_{int(time.time())}_{uuid.uuid4().hex[:6]}"
    temp_dir = os.path.join(abs_output_dir, f"tmp_{task_id}")
    os.makedirs(temp_dir, exist_ok=True)

    def report(pct: int, msg: str):
        if progress_callback:
            progress_callback(pct, msg)
        log_safe(f"[{pct}%] {msg}")

    try:
        # Dimensions
        if aspect_ratio == "16:9":
            width, height = 1280, 720
        else:
            width, height = 720, 1280  # Default vertical 9:16 Shorts

        # Step 1: Script generation
        report(10, "Crafting viral script & visual storyboard...")
        scenes = generate_script_from_comment(comment, style=style, target_duration=target_duration)
        log_safe(f"Generated {len(scenes)} scenes for comment: '{comment[:40]}...'")

        # Step 2: Voiceover synthesis
        report(25, f"Synthesizing neural voiceover...")
        voice_audio_path = os.path.join(temp_dir, "narration.mp3")
        total_duration, sub_events = asyncio.run(
            generate_voiceover(scenes, voice_id, voice_audio_path)
        )
        report(45, f"Voice narration ready ({total_duration:.1f}s)")

        # Step 3: Visual generation for each scene
        report(50, f"Generating visual scenes with AI...")
        scene_video_parts = []

        for i, scene in enumerate(scenes):
            scene_img_name = f"scene_{i+1}.jpg"
            scene_clip_name = f"scene_{i+1}.mp4"
            scene_img_path = os.path.join(temp_dir, scene_img_name)

            report(50 + int((i / len(scenes)) * 20), f"Rendering AI scene {i+1}/{len(scenes)}: {scene['title']}...")
            fetch_or_create_scene_image(
                prompt=scene["visual_prompt"],
                title=scene["title"],
                width=width,
                height=height,
                filepath=scene_img_path,
                seed=random.randint(1000, 999999)
            )

            # Apply Ken Burns smooth zoom / pan effect
            fps = 25
            scene_duration = max(2.0, scene["duration"])
            num_frames = int(scene_duration * fps)

            zoompan_filter = (
                f"zoompan=z='min(zoom+0.0015,1.2)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
                f"d={num_frames}:s={width}x{height}:fps={fps},"
                f"format=yuv420p"
            )

            cmd_scene = [
                FFMPEG_PATH, "-y",
                "-loop", "1",
                "-i", scene_img_name,
                "-vf", zoompan_filter,
                "-t", str(scene_duration),
                "-c:v", "libx264",
                "-preset", "veryfast",
                "-pix_fmt", "yuv420p",
                scene_clip_name
            ]
            subprocess.run(cmd_scene, cwd=temp_dir, capture_output=True, text=True, errors="replace", timeout=60)
            scene_video_parts.append(scene_clip_name)

        # Step 4: Concatenate video parts
        report(72, "Merging visual scenes & transitions...")
        concat_txt = os.path.join(temp_dir, "concat.txt")
        with open(concat_txt, "w", encoding="utf-8") as f:
            for part in scene_video_parts:
                f.write(f"file '{part}'\n")

        merged_video_name = "visuals_merged.mp4"
        cmd_concat = [
            FFMPEG_PATH, "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", "concat.txt",
            "-c", "copy",
            merged_video_name
        ]
        subprocess.run(cmd_concat, cwd=temp_dir, capture_output=True, text=True, errors="replace", timeout=60)

        # Step 5: Subtitles & Audio Mixing
        report(82, "Generating viral captions & mixing audio...")
        ass_content = build_ass_subtitles(scenes, width, height, style=subtitle_style)
        with open(os.path.join(temp_dir, "captions.ass"), "w", encoding="utf-8") as f:
            f.write(ass_content)

        if use_bg_music:
            generate_ambient_track(total_duration, os.path.join(temp_dir, "ambient.aac"))
            # Mix narration at 100% and ambient at 20%
            cmd_mix = [
                FFMPEG_PATH, "-y",
                "-i", "narration.mp3",
                "-i", "ambient.aac",
                "-filter_complex", "[0:a]volume=1.0[v];[1:a]volume=0.20[b];[v][b]amix=inputs=2:duration=first:dropout_transition=2[a]",
                "-map", "[a]",
                "-c:a", "aac", "-b:a", "192k",
                "audio_mixed.m4a"
            ]
            subprocess.run(cmd_mix, cwd=temp_dir, capture_output=True, text=True, errors="replace", timeout=30)
            final_audio_file = "audio_mixed.m4a" if os.path.exists(os.path.join(temp_dir, "audio_mixed.m4a")) else "narration.mp3"
        else:
            final_audio_file = "narration.mp3"

        # Step 6: Burn Subtitles and Output Final MP4
        report(90, "Assembling final Short with subtitles...")
        final_filename = f"{task_id}.mp4"
        final_output_path = os.path.join(abs_output_dir, final_filename)

        video_filter = "subtitles=captions.ass" if subtitle_style != "none" else "null"

        cmd_final = [
            FFMPEG_PATH, "-y",
            "-i", merged_video_name,
            "-i", final_audio_file,
            "-vf", video_filter,
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-crf", "22",
            "-c:a", "aac",
            "-b:a", "192k",
            "-shortest",
            "-movflags", "+faststart",
            final_output_path
        ]

        proc = subprocess.run(cmd_final, cwd=temp_dir, capture_output=True, text=True, errors="replace", timeout=120)
        if proc.returncode != 0:
            log_safe(f"[WARN] Subtitle burn error, falling back without subtitle filter...")
            cmd_fallback = [
                FFMPEG_PATH, "-y",
                "-i", merged_video_name,
                "-i", final_audio_file,
                "-c:v", "copy",
                "-c:a", "aac",
                "-shortest",
                "-movflags", "+faststart",
                final_output_path
            ]
            subprocess.run(cmd_fallback, cwd=temp_dir, capture_output=True, text=True, errors="replace", timeout=60)

        # Cleanup temporary build dir
        try:
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
        except Exception:
            pass

        report(100, "AI Video successfully generated!")

        file_size_mb = round(os.path.getsize(final_output_path) / (1024 * 1024), 2)
        actual_duration = round(get_audio_duration(final_output_path), 1)

        # Save metadata JSON for the generated video
        meta_path = os.path.join(abs_output_dir, f"{task_id}.json")
        result_meta = {
            "status": "success",
            "task_id": task_id,
            "filename": final_filename,
            "download_url": f"/download/{final_filename}",
            "comment": comment,
            "duration": actual_duration or round(total_duration, 1),
            "duration_formatted": f"0:{int(actual_duration or total_duration):02d}",
            "file_size_mb": file_size_mb,
            "resolution": f"{width}x{height}",
            "aspect_ratio": aspect_ratio,
            "scenes": scenes,
            "scenes_count": len(scenes),
            "created_at": time.time()
        }
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(result_meta, f, indent=2)

        return result_meta

    except Exception as exc:
        report(0, f"Error: {str(exc)}")
        raise exc
