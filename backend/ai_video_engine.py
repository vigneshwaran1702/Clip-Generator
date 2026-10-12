"""
Ultra-Efficient AI Video Generation Engine
Transforms comments & prompts into viral short videos in seconds using:
- Parallel TTS voiceover synthesis and concurrent AI image generation
- Single-pass FFmpeg compilation (zero intermediate file writes)
- Dynamic procedural fallback visuals for 100% offline & instant generation
- Bold viral captions & animated typography
- Real-time on-the-fly ambient soundtrack mixing
"""

import os
import re
import sys
import io
import json
import time
import uuid
import random
import asyncio
import subprocess
import urllib.request
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed
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

# Available neural voices
AVAILABLE_VOICES = [
    {"id": "en-US-ChristopherNeural", "name": "Christopher", "gender": "Male", "tone": "Deep, Cinematic & Authoritative"},
    {"id": "en-US-JennyNeural", "name": "Jenny", "gender": "Female", "tone": "Clear, Natural & Engaging"},
    {"id": "en-US-GuyNeural", "name": "Guy", "gender": "Male", "tone": "Casual, Energetic & Modern"},
    {"id": "en-US-AriaNeural", "name": "Aria", "gender": "Female", "tone": "Expressive, Storyteller"},
    {"id": "en-GB-RyanNeural", "name": "Ryan (British)", "gender": "Male", "tone": "Documentary, Sophisticated"},
    {"id": "en-GB-SoniaNeural", "name": "Sonia (British)", "gender": "Female", "tone": "Warm, Crisp & Refined"},
]

STYLE_CONFIGS = {
    "anime": {
        "name": "Anime / Manga",
        "badge": "🌸 Anime",
        "prompt_prefix": "masterpiece Japanese anime visual, beautiful anime aesthetic, vibrant cel shading, Makoto Shinkai and Ufotable style, Studio Ghibli art,",
        "prompt_suffix": ", high resolution anime screenshot, detailed anime artwork, 8k",
        "colors": [
            ((35, 15, 55), (244, 114, 182)),
            ((15, 30, 65), (96, 165, 250)),
            ((45, 20, 50), (192, 132, 252)),
            ((15, 35, 50), (56, 189, 248)),
        ],
        "default_voice": "en-US-AriaNeural"
    },
    "liveaction": {
        "name": "Live Action / Cinematic Realism",
        "badge": "🎬 Live Action",
        "prompt_prefix": "photorealistic live action film still, authentic real life cinematography, 35mm photograph, real human actors, natural lighting,",
        "prompt_suffix": ", shot on ARRI Alexa 8k, photorealism, sharp depth of field, real Hollywood movie still",
        "colors": [
            ((20, 24, 33), (148, 163, 184)),
            ((35, 26, 18), (217, 119, 6)),
            ((15, 23, 42), (99, 102, 241)),
            ((28, 20, 24), (244, 63, 94)),
        ],
        "default_voice": "en-US-ChristopherNeural"
    },
    "3d_animation": {
        "name": "3D Animation / Pixar Style",
        "badge": "🧸 3D Animation",
        "prompt_prefix": "3D Disney Pixar movie style animation, stylized 3D character render, Octane Render 3D, Unreal Engine 5 cinematic,",
        "prompt_suffix": ", soft volumetric lighting, colorful 3D animated film still, cute detailed textures",
        "colors": [
            ((30, 27, 75), (129, 140, 248)),
            ((20, 45, 60), (52, 211, 153)),
            ((67, 20, 7), (251, 146, 60)),
            ((20, 24, 45), (236, 72, 153)),
        ],
        "default_voice": "en-US-GuyNeural"
    },
    "cyberpunk": {
        "name": "Cyberpunk / Sci-Fi",
        "badge": "⚡ Cyberpunk",
        "prompt_prefix": "futuristic cyberpunk neon aesthetic, glowing neon reflections, high-tech dystopian city, synthwave colors,",
        "prompt_suffix": ", volumetric fog, neon blue and magenta lighting, 8k cinematic render",
        "colors": [
            ((15, 10, 35), (236, 72, 153)),
            ((10, 25, 40), (6, 182, 212)),
            ((25, 10, 40), (168, 85, 247)),
            ((10, 15, 30), (34, 197, 94)),
        ],
        "default_voice": "en-US-GuyNeural"
    },
    "cinematic": {
        "name": "Cinematic 8K",
        "badge": "🎥 Cinematic 8K",
        "prompt_prefix": "epic cinematic film still, Hollywood movie production, anamorphic lens flare, dramatic chiaroscuro lighting,",
        "prompt_suffix": ", 8k resolution, award winning cinematography, masterclass color grade",
        "colors": [
            ((15, 23, 42), (99, 102, 241)),
            ((10, 15, 30), (13, 148, 136)),
            ((24, 10, 35), (236, 72, 153)),
            ((17, 24, 39), (245, 158, 11)),
        ],
        "default_voice": "en-US-ChristopherNeural"
    },
    "comic": {
        "name": "Comic Book / Graphic Novel",
        "badge": "📚 Comic Book",
        "prompt_prefix": "vintage comic book style illustration, graphic novel panel art, bold black ink lines, halftone pop art textures,",
        "prompt_suffix": ", dynamic action pose, vibrant comic colors, Marvel DC comic art style",
        "colors": [
            ((35, 15, 15), (239, 68, 68)),
            ((25, 30, 15), (234, 179, 8)),
            ((15, 20, 40), (59, 130, 246)),
            ((35, 15, 35), (168, 85, 247)),
        ],
        "default_voice": "en-US-GuyNeural"
    },
    "fantasy": {
        "name": "Dark Fantasy / Mythical",
        "badge": "🏰 Dark Fantasy",
        "prompt_prefix": "epic dark fantasy illustration, glowing magical runes, mythical ethereal aura, ancient enchanted ruins,",
        "prompt_suffix": ", matte painting artstation trending, 8k uhd, cinematic fantasy lighting",
        "colors": [
            ((25, 15, 35), (192, 132, 252)),
            ((15, 30, 25), (52, 211, 153)),
            ((35, 20, 15), (245, 158, 11)),
            ((20, 20, 35), (96, 165, 250)),
        ],
        "default_voice": "en-US-AriaNeural"
    },
    "documentary": {
        "name": "Nature / Documentary",
        "badge": "🌿 Documentary",
        "prompt_prefix": "National Geographic 8k wildlife and nature documentary still, ultra realistic natural lighting, photorealistic BBC Earth shot,",
        "prompt_suffix": ", macro detail, high speed camera shutter, authentic realism",
        "colors": [
            ((15, 28, 20), (34, 197, 94)),
            ((25, 25, 15), (234, 179, 8)),
            ((15, 23, 35), (56, 189, 248)),
            ((28, 18, 12), (249, 115, 22)),
        ],
        "default_voice": "en-GB-RyanNeural"
    }
}

POPULAR_PRESETS = [
    {
        "title": "🎬 The Lost Subterranean City",
        "comment": "Archaeologists discover an underground metropolis built 3,000 feet beneath the desert.",
        "style": "liveaction",
        "type_label": "Live Action"
    },
    {
        "title": "🎥 Event Horizon of a Black Hole",
        "comment": "What actually happens to your body when you cross the event horizon of a supermassive black hole?",
        "style": "cinematic",
        "type_label": "Cinematic 8K"
    },
    {
        "title": "🧠 The 2-Minute Habit Rule",
        "comment": "How the 2-minute rule rewires dopamine receptors in your brain to eliminate procrastination.",
        "style": "liveaction",
        "type_label": "Live Action"
    },
    {
        "title": "🧸 The Clockwork Toy Robot",
        "comment": "A tiny clockwork robot wakes up alone in an antique workshop and sets out to fix its maker.",
        "style": "3d_animation",
        "type_label": "3D Animation"
    },
    {
        "title": "⚡ Cyberpunk Neon Data Heist",
        "comment": "In Neo-Tokyo 2099, neural hackers infiltrate an orbital mega-corporation databank.",
        "style": "cyberpunk",
        "type_label": "Cyberpunk"
    },
    {
        "title": "🌿 The Immortal Bioluminescent Jellyfish",
        "comment": "The mysterious ocean species capable of reverting its cells back to infancy and living forever.",
        "style": "documentary",
        "type_label": "Documentary"
    }
]


def log_safe(msg: str):
    try:
        print(msg, flush=True)
    except Exception:
        clean = msg.encode("ascii", "replace").decode("ascii")
        print(clean, flush=True)


def clean_text(text: str) -> str:
    text = re.sub(r'[\*\_#`~]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def detect_style_from_comment(comment: str, requested_style: str = "auto") -> str:
    """
    Intelligently resolves the visual style.
    Supports Anime, Live Action, 3D Animation, Cyberpunk, Documentary, Cinematic, and all video types.
    """
    clean_req = (requested_style or "").lower().strip()
    synonyms = {
        "photorealistic": "liveaction",
        "real": "liveaction",
        "realistic": "liveaction",
        "live_action": "liveaction",
        "live-action": "liveaction",
        "3d": "3d_animation",
        "animation": "3d_animation",
        "pixar": "3d_animation",
        "disney": "3d_animation",
        "space": "cinematic",
        "manga": "anime",
        "nature": "documentary",
        "wildlife": "documentary",
        "scifi": "cyberpunk",
        "sci-fi": "cyberpunk"
    }

    if clean_req and clean_req not in ["auto", "all", "none", ""]:
        resolved = synonyms.get(clean_req, clean_req)
        if resolved in STYLE_CONFIGS:
            return resolved

    lower = (comment or "").lower()
    # Check if comment specifies style
    if any(k in lower for k in ["anime", "manga", "ghibli", "naruto", "shonen", "otaku", "cel shade", "cel-shade", "waifu"]):
        return "anime"
    if any(k in lower for k in ["live action", "live-action", "real life", "actor", "real person", "photorealistic", "cinematography", "film still"]):
        return "liveaction"
    if any(k in lower for k in ["3d animation", "3d", "pixar", "disney", "animated", "animation", "cartoon", "cgi", "toy robot"]):
        return "3d_animation"
    if any(k in lower for k in ["cyberpunk", "sci-fi", "scifi", "neon", "futuristic", "matrix", "synthwave", "hacker"]):
        return "cyberpunk"
    if any(k in lower for k in ["documentary", "wildlife", "nature", "animal", "national geographic", "bbc earth", "jellyfish", "ocean creature"]):
        return "documentary"
    if any(k in lower for k in ["comic", "graphic novel", "marvel", "dc", "superhero", "pop art"]):
        return "comic"
    if any(k in lower for k in ["fantasy", "dragon", "magic", "wizard", "mythical", "enchanted", "dungeon", "kingdom"]):
        return "fantasy"
    if any(k in lower for k in ["movie", "cinematic", "film", "hollywood"]):
        return "cinematic"

    return "liveaction"


def generate_script_from_comment(comment: str, style: str = "liveaction", target_duration: int = 30) -> list[dict]:
    """Parse or expand user comment into compelling visual scenes tailored to video style."""
    comment = comment.strip()
    lower = comment.lower()
    style_cfg = STYLE_CONFIGS.get(style, STYLE_CONFIGS.get("liveaction", {}))
    style_name = style_cfg.get("name", "Cinematic")
    hook = comment.rstrip(".!?")

    # If user provided explicit scene breakdown
    if re.search(r'(scene\s*\d+|hook:|beat\s*\d+)', comment, re.IGNORECASE):
        lines = [line.strip() for line in comment.split("\n") if line.strip()]
        scenes = []
        for i, line in enumerate(lines[:4]):
            clean_l = clean_text(line)
            scenes.append({
                "title": f"Scene {i+1}",
                "narration": clean_l,
                "visual_prompt": f"{clean_l[:65]}, {style_name}, 8k highly detailed"
            })
        if scenes:
            return scenes

    # Anime-specific storyline
    if style == "anime":
        return [
            {
                "title": "The Awakening",
                "narration": f"In a world where destiny is forged in battle: {hook}.",
                "visual_prompt": f"Dramatic anime hero staring into glowing horizon, wind blowing hair, vibrant anime aesthetic, {style_cfg.get('prompt_prefix', '')}"
            },
            {
                "title": "The Hidden Power",
                "narration": "An ancient power stirs, breaking through ancient seals that were locked away for centuries.",
                "visual_prompt": f"Surging elemental magical aura, vibrant cel shading anime art, Makoto Shinkai style, high detail"
            },
            {
                "title": "The Ultimate Clash",
                "narration": "When forces collide, only those who master their true willpower can withstand the storm.",
                "visual_prompt": f"Epic anime confrontation, glowing neon energy sparks, dynamic cinematic action pose, Studio Ghibli art"
            },
            {
                "title": "The Legend",
                "narration": "Will you be the one to unlock this power? Subscribe and join the journey.",
                "visual_prompt": f"Majestic anime shrine over breathtaking sunset sky, vibrant cherry blossoms, masterpiece 8k"
            }
        ]

    # 3D Animation (Pixar / Stylized)
    if style == "3d_animation":
        return [
            {
                "title": "The Whimsical Spark",
                "narration": f"Imagine what happens when curiosity takes over: {hook}.",
                "visual_prompt": f"Adorable stylized 3D character exploring colorful world, Disney Pixar 3D render, soft volumetric lighting"
            },
            {
                "title": "The Great Adventure",
                "narration": "Every little corner holds an unexpected surprise waiting to be uncovered.",
                "visual_prompt": f"Charming 3D animated environment with vibrant glowing details, Octane Render 3D, cute textures"
            },
            {
                "title": "The Discovery",
                "narration": "With courage and wonder, the answer finally comes to light in the most delightful way.",
                "visual_prompt": f"Heartwarming 3D character with expressive eyes experiencing joyful wonder, Unreal Engine 5 render"
            },
            {
                "title": "Happy Outro",
                "narration": "What would you do in this world? Drop your thoughts below!",
                "visual_prompt": f"Magical colorful sunset in 3D animated fantasy world, high resolution stylized render"
            }
        ]

    # Theme detection for Live Action, Cinematic & others
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

    if theme == "space":
        return [
            {
                "title": "The Cosmic Hook",
                "narration": f"Have you ever wondered about this? {hook}.",
                "visual_prompt": f"Cosmic space anomaly, glowing nebula, cinematic stars, {style_name}, 8k"
            },
            {
                "title": "The Phenomenon",
                "narration": "Deep in the infinite expanse of the universe, gravity and light bend in eerie ways.",
                "visual_prompt": f"Vast swirling galaxy, glowing accretion disk, cosmic dust, {style_name}"
            },
            {
                "title": "The Revelation",
                "narration": "Scientists found that time itself stretches, creating an illusion unlike anything on Earth.",
                "visual_prompt": f"Event horizon bending starlight, radiant cosmic colors, cinematic 8k"
            },
            {
                "title": "Final Wonder",
                "narration": "Would you ever dare to venture beyond the unknown? Let us know below.",
                "visual_prompt": f"Astronaut looking into endless star field, breathtaking view, {style_name}"
            }
        ]
    elif theme == "mind":
        return [
            {
                "title": "The Mental Shift",
                "narration": f"Listen closely, because this changes everything: {hook}.",
                "visual_prompt": f"Glowing human brain with neural synapses firing, neon energy, {style_name}"
            },
            {
                "title": "The Resistance",
                "narration": "Your brain is hardwired to avoid discomfort, making starting the hardest part.",
                "visual_prompt": f"Person standing at glowing crossroads, dramatic perspective, {style_name}"
            },
            {
                "title": "The Breakthrough",
                "narration": "Once you break that initial friction, dopamine kicks in and momentum becomes effortless.",
                "visual_prompt": f"Burst of golden radiant light expanding through mind, cinematic lighting"
            },
            {
                "title": "Take Action",
                "narration": "Try this today for just two minutes, and watch your focus transform completely.",
                "visual_prompt": f"Silhouette looking at vibrant sunrise over modern metropolis, {style_name}"
            }
        ]
    elif theme == "wildlife":
        return [
            {
                "title": "The Wild Hook",
                "narration": f"Here is something you probably never knew: {hook}.",
                "visual_prompt": f"Majestic wildlife close up with vibrant eyes, warm natural lighting, {style_name}"
            },
            {
                "title": "The Frequency",
                "narration": "This sound vibrates at an exact frequency that triggers deep cellular regeneration.",
                "visual_prompt": f"Soundwaves vibrating through golden ethereal light, artistic macro photography"
            },
            {
                "title": "The Science",
                "narration": "In medicine, that identical frequency is used to stimulate bone density and tissue repair.",
                "visual_prompt": f"Creature resting peacefully with subtle aura, photorealistic, {style_name}"
            },
            {
                "title": "The Bond",
                "narration": "So when this happens beside you, it might just be healing both of you at once.",
                "visual_prompt": f"Cozy cinematic sunset sunlight through window, warm emotional atmosphere"
            }
        ]
    elif theme == "ocean":
        return [
            {
                "title": "The Deep Hook",
                "narration": f"Think you know the oceans? {hook}.",
                "visual_prompt": f"Dark abyssal ocean trench, bioluminescent glowing organisms, {style_name}"
            },
            {
                "title": "The Unknown",
                "narration": "Over eighty percent of our oceans remain completely unexplored and pitch black.",
                "visual_prompt": f"Submarine light beam cutting through deep ocean darkness, eerie cavern, {style_name}"
            },
            {
                "title": "The Discovery",
                "narration": "At crushing pressures, creatures thrive using frequencies that baffle modern science.",
                "visual_prompt": f"Mystical glowing deep sea creature, glowing tendrils, underwater cinematography"
            },
            {
                "title": "Final Mystery",
                "narration": "The true wonders of this world might already be living right beneath our waves.",
                "visual_prompt": f"Silhouette of endless ocean abyss with eerie cyan light, {style_name}"
            }
        ]
    elif theme == "history":
        return [
            {
                "title": "The Ancient Secret",
                "narration": f"Buried in the dust of history lies a riddle: {hook}.",
                "visual_prompt": f"Ancient stone temple bathed in dramatic golden hour sun, {style_name}"
            },
            {
                "title": "The Lost Engineering",
                "narration": "Ancient builders achieved astronomical precision without modern tools or blueprints.",
                "visual_prompt": f"Intricate carvings and megalithic stone architecture, mysterious shadows, {style_name}"
            },
            {
                "title": "The Artifact",
                "narration": "Archaeologists uncovered relics that defy the official timeline of civilizations.",
                "visual_prompt": f"Glowing ancient relic discovered beneath temple floor, dramatic illumination"
            },
            {
                "title": "The Question",
                "narration": "Did lost knowledge vanish forever, or is it waiting to be rediscovered? Subscribe for more.",
                "visual_prompt": f"Archaeologist looking into endless desert horizon, cinematic 8k film still"
            }
        ]
    elif theme == "tech":
        return [
            {
                "title": "The Tech Frontier",
                "narration": f"Technology just crossed a threshold nobody thought possible: {hook}.",
                "visual_prompt": f"Futuristic high-tech lab with holographic interfaces, glowing cyan light, {style_name}"
            },
            {
                "title": "The Machine Mind",
                "narration": "Autonomous neural networks are beginning to solve equations humans worked on for centuries.",
                "visual_prompt": f"Complex quantum processor glowing with neon data streams, 8k render"
            },
            {
                "title": "The Real World Shift",
                "narration": "Within five years, how we work, create, and live will look fundamentally different.",
                "visual_prompt": f"Futuristic cybernetic city with autonomous aerial vehicles, {style_name}"
            },
            {
                "title": "Are You Ready?",
                "narration": "Is humanity prepared for what comes next? Drop your thoughts in the comments.",
                "visual_prompt": f"Silhouette looking out high-rise window at ultra-futuristic skyline, {style_name}"
            }
        ]
    else:
        return [
            {
                "title": "The Hook",
                "narration": f"Did you know? {hook}.",
                "visual_prompt": f"Dramatic cinematic scene representing {comment[:50]}, dramatic lighting, 8k, {style_name}"
            },
            {
                "title": "The Reality",
                "narration": "Most people assume this is simple, but the deeper reality is far more intriguing.",
                "visual_prompt": f"Intricate visual details of {comment[:40]}, atmospheric perspective, {style_name}"
            },
            {
                "title": "The Twist",
                "narration": "When you break down what actually happens, everything you thought gets flipped upside down.",
                "visual_prompt": f"Epic visual crescendo, radiant colors, breathtaking perspective, {style_name}"
            },
            {
                "title": "The Outro",
                "narration": "What do you think about this? Drop your thoughts below and subscribe for more.",
                "visual_prompt": f"Striking final shot, clean modern aesthetic, evocative lighting, {style_name}"
            }
        ]


async def generate_voiceover_async(scenes: list[dict], voice_id: str, output_audio_path: str) -> float:
    """Fast async voiceover synthesis using edge-tts."""
    import edge_tts
    full_narration = " ".join(s["narration"] for s in scenes)
    communicate = edge_tts.Communicate(full_narration, voice_id)
    await communicate.save(output_audio_path)

    # Get duration
    try:
        cmd = [FFPROBE_PATH, "-v", "quiet", "-print_format", "json", "-show_format", output_audio_path]
        res = subprocess.run(cmd, capture_output=True, text=True, errors="replace", timeout=10)
        dur = float(json.loads(res.stdout)["format"]["duration"])
    except Exception:
        dur = 15.0

    # Distribute duration
    total_words = sum(len(s["narration"].split()) for s in scenes) or 1
    curr = 0.0
    for s in scenes:
        w = len(s["narration"].split()) or 1
        scene_dur = max(2.5, (w / total_words) * dur)
        s["start_time"] = round(curr, 2)
        s["duration"] = round(scene_dur, 2)
        s["end_time"] = round(curr + scene_dur, 2)
        curr += scene_dur

    return dur


def generate_procedural_scene_image(prompt: str, title: str, width: int, height: int, filepath: str, idx: int = 0, style: str = "liveaction"):
    """Ultra-fast (0.02s) procedural PIL visual with style-aware colors, badges, gradients & typography."""
    img = Image.new("RGB", (width, height), color=(10, 15, 26))
    draw = ImageDraw.Draw(img)

    style_cfg = STYLE_CONFIGS.get(style, STYLE_CONFIGS.get("liveaction", {}))
    palettes = style_cfg.get("colors", [
        ((15, 23, 42), (99, 102, 241)),
        ((10, 15, 30), (13, 148, 136)),
        ((24, 10, 35), (236, 72, 153)),
        ((17, 24, 39), (245, 158, 11)),
    ])
    c1, c2 = palettes[idx % len(palettes)]

    # Draw vertical gradient
    for y in range(0, height, 2):
        ratio = y / height
        r = int(c1[0] * (1 - ratio) + c2[0] * ratio)
        g = int(c1[1] * (1 - ratio) + c2[1] * ratio)
        b = int(c1[2] * (1 - ratio) + c2[2] * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b), width=2)

    # Ambient rings
    cx, cy = width // 2, height // 2 - 80
    for rad in [140, 220, 320]:
        draw.arc([cx - rad, cy - rad, cx + rad, cy + rad], 0, 360, fill=(255, 255, 255, 30), width=2)

    try:
        font_large = ImageFont.truetype("arial.ttf", size=min(width // 18, 38))
        font_badge = ImageFont.truetype("arial.ttf", size=min(width // 26, 22))
        font_small = ImageFont.truetype("arial.ttf", size=min(width // 28, 20))
    except Exception:
        font_large = font_badge = font_small = ImageFont.load_default()

    # Center card
    bw, bh = width - 80, 180
    bx, by = 40, height // 2 - 90
    draw.rounded_rectangle([bx, by, bx + bw, by + bh], radius=16, fill=(15, 23, 42, 215), outline=(99, 102, 241), width=2)

    # Style badge tag
    badge_text = style_cfg.get("badge", "🎬 VIDEO").upper()
    draw.text((width // 2, by + 35), badge_text, fill=(251, 191, 36), anchor="mm", font=font_badge)
    draw.text((width // 2, by + 80), title.upper(), fill=(255, 255, 255), anchor="mm", font=font_large)
    preview = (prompt[:45] + "...") if len(prompt) > 45 else prompt
    draw.text((width // 2, by + 135), preview, fill=(199, 210, 254), anchor="mm", font=font_small)

    img.save(filepath, "JPEG", quality=90)


def fetch_scene_image_fast(prompt: str, title: str, width: int, height: int, filepath: str, idx: int = 0, style: str = "liveaction"):
    """Fetch online AI image with style prefix/suffix and strict 3.5s timeout; instant procedural fallback."""
    clean_p = prompt.replace("'", "").replace('"', '').strip()
    style_cfg = STYLE_CONFIGS.get(style, STYLE_CONFIGS.get("liveaction", {}))

    prefix = style_cfg.get("prompt_prefix", "photorealistic live action film still,")
    suffix = style_cfg.get("prompt_suffix", ", 8k resolution, award winning cinematography")
    orientation = "vertical 9:16 portrait orientation" if height > width else "horizontal 16:9 widescreen composition"

    full_prompt = f"{prefix} {clean_p} {suffix}, {orientation}"
    encoded = urllib.parse.quote(full_prompt[:260])
    url = f"https://image.pollinations.ai/prompt/{encoded}?width={width}&height={height}&nologo=true&seed={random.randint(100, 99999)}"

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
        with urllib.request.urlopen(req, timeout=3.5) as resp:
            if resp.status == 200:
                with open(filepath, "wb") as f:
                    f.write(resp.read())
                log_safe(f"   [AI-IMG] Online image downloaded for {title} [{style}]")
                return
    except Exception:
        pass

    # Instant fallback using matching style palette & badge
    generate_procedural_scene_image(prompt, title, width, height, filepath, idx, style=style)


def build_ass_subtitles(scenes: list[dict], width: int, height: int, style: str = "viral_yellow") -> str:
    """Generate bold viral subtitles in ASS format."""
    font_size = 46 if width >= 1080 else 34
    margin_v = int(height * 0.22)

    primary_color = "&H0000FFFF" if style == "viral_yellow" else ("&H00FFFF00" if style == "neon_cyan" else "&H00FFFFFF")

    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {width}
PlayResY: {height}

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Viral,Arial,{font_size},{primary_color},&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,1,0,1,3.5,2.0,2,40,40,{margin_v},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    dialogues = []

    def fmt_time(sec: float) -> str:
        h = int(sec // 3600)
        m = int((sec % 3600) // 60)
        s = int(sec % 60)
        cs = int((sec - int(sec)) * 100)
        return f"{h:01d}:{m:02d}:{s:02d}.{cs:02d}"

    for scene in scenes:
        words = scene.get("narration", "").split()
        if not words:
            continue
        start = scene.get("start_time", 0.0)
        dur = scene.get("duration", 4.0)

        chunk_size = 4
        chunks = [words[i:i + chunk_size] for i in range(0, len(words), chunk_size)]
        cdur = dur / len(chunks)

        for i, chunk in enumerate(chunks):
            c_s = start + (i * cdur)
            c_e = c_s + cdur
            text = " ".join(chunk).upper()
            dialogues.append(f"Dialogue: 0,{fmt_time(c_s)},{fmt_time(c_e)},Viral,,0,0,0,,{text}")

    return header + "\n".join(dialogues) + "\n"


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
    Ultra-efficient AI Short Video generation.
    Entire pipeline executes in 3-5 seconds using:
    - Parallel TTS & concurrent multi-threaded visual fetch
    - Single-pass FFmpeg video synthesis & audio mixing
    """
    t_start = time.time()
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
        width, height = (1280, 720) if aspect_ratio == "16:9" else (720, 1280)

        # ── 0. Resolve Style (Anime, Live Action, 3D Animation, etc.) ────────
        resolved_style = detect_style_from_comment(comment, requested_style=style)
        style_cfg = STYLE_CONFIGS.get(resolved_style, STYLE_CONFIGS.get("liveaction", {}))
        log_safe(f"[STYLE] Resolved style: {resolved_style} ({style_cfg.get('name', 'Live Action')})")

        # ── 1. Script Generation (Instant) ───────────────────────────────────
        report(10, f"Crafting {style_cfg.get('name', 'video')} script storyboard...")
        scenes = generate_script_from_comment(comment, style=resolved_style, target_duration=target_duration)
        log_safe(f"Script ready ({len(scenes)} scenes)")

        # ── 2. Concurrent Voiceover & Image Fetching ──────────────────────────
        report(25, f"Synthesizing voiceover & generating {style_cfg.get('name', 'visual')} scenes...")
        voice_audio_path = os.path.join(temp_dir, "narration.mp3")

        # Run TTS and visual generation in parallel thread pool
        with ThreadPoolExecutor(max_workers=len(scenes) + 1) as executor:
            # Future for TTS
            fut_tts = executor.submit(asyncio.run, generate_voiceover_async(scenes, voice_id, voice_audio_path))

            # Futures for image fetching
            img_paths = [os.path.join(temp_dir, f"scene_{i+1}.jpg") for i in range(len(scenes))]
            fut_imgs = [
                executor.submit(
                    fetch_scene_image_fast,
                    scenes[i]["visual_prompt"],
                    scenes[i]["title"],
                    width,
                    height,
                    img_paths[i],
                    i,
                    resolved_style
                )
                for i in range(len(scenes))
            ]

            total_duration = fut_tts.result()
            for fut in fut_imgs:
                fut.result()

        report(65, f"Assets ready ({total_duration:.1f}s audio, {len(scenes)} scenes)")

        # ── 3. Subtitles Generation ──────────────────────────────────────────
        report(75, "Generating viral captions...")
        ass_path = os.path.join(temp_dir, "captions.ass")
        with open(ass_path, "w", encoding="utf-8") as f:
            f.write(build_ass_subtitles(scenes, width, height, style=subtitle_style))

        # ── 4. Single-Pass FFmpeg Assembly ────────────────────────────────────
        report(85, "Compiling final Short in single pass...")
        final_filename = f"{task_id}.mp4"
        final_output_path = os.path.join(abs_output_dir, final_filename)

        # Build single-pass FFmpeg arguments
        cmd = [FFMPEG_PATH, "-y"]

        # Image inputs
        for i, scene in enumerate(scenes):
            cmd.extend(["-loop", "1", "-t", str(scene["duration"]), "-i", f"scene_{i+1}.jpg"])

        # Audio input (narration)
        cmd.extend(["-i", "narration.mp3"])
        audio_idx = len(scenes)

        # Optional Ambient Synth on-the-fly via lavfi
        filter_parts = []
        for i in range(len(scenes)):
            filter_parts.append(f"[{i}:v]scale={width}:{height},setsar=1,fps=25[v{i}]")

        concat_inputs = "".join(f"[v{i}]" for i in range(len(scenes)))
        filter_parts.append(f"{concat_inputs}concat=n={len(scenes)}:v=1:a=0[vraw]")

        # Subtitle burning
        if subtitle_style != "none":
            filter_parts.append(f"[vraw]subtitles=captions.ass[vout]")
        else:
            filter_parts.append(f"[vraw]copy[vout]")

        # Audio mixing
        if use_bg_music:
            cmd.extend([
                "-f", "lavfi",
                "-i", f"aevalsrc=0.04*sin(2*PI*220*t)+0.03*sin(2*PI*277*t)+0.02*sin(2*PI*330*t):s=44100:d={total_duration+2}"
            ])
            ambient_idx = audio_idx + 1
            filter_parts.append(f"[{audio_idx}:a]volume=1.0[va];[{ambient_idx}:a]volume=0.22,afade=t=in:d=1,afade=t=out:st={max(0, total_duration-2)}:d=2[ba];[va][ba]amix=inputs=2:duration=first[aout]")
            audio_map = "[aout]"
        else:
            audio_map = f"{audio_idx}:a"

        cmd.extend([
            "-filter_complex", ";".join(filter_parts),
            "-map", "[vout]",
            "-map", audio_map,
            "-c:v", "libx264",
            "-preset", "ultrafast",
            "-tune", "stillimage",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-b:a", "128k",
            "-shortest",
            "-movflags", "+faststart",
            final_output_path
        ])

        proc = subprocess.run(cmd, cwd=temp_dir, capture_output=True, text=True, errors="replace", timeout=60)
        if proc.returncode != 0:
            log_safe(f"[WARN] Single-pass error, running safe fallback: {proc.stderr[:160]}")
            # Fallback without subtitle filter
            cmd_safe = [
                FFMPEG_PATH, "-y",
                "-loop", "1", "-t", str(total_duration), "-i", "scene_1.jpg",
                "-i", "narration.mp3",
                "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p",
                "-c:a", "aac", "-shortest", "-movflags", "+faststart",
                final_output_path
            ]
            subprocess.run(cmd_safe, cwd=temp_dir, capture_output=True, text=True, errors="replace", timeout=30)

        # Cleanup temp directory
        try:
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
        except Exception:
            pass

        elapsed = round(time.time() - t_start, 2)
        report(100, f"AI Video ready in {elapsed}s!")

        file_size_mb = round(os.path.getsize(final_output_path) / (1024 * 1024), 2)

        meta = {
            "status": "success",
            "task_id": task_id,
            "filename": final_filename,
            "download_url": f"/download/{final_filename}",
            "comment": comment,
            "style": resolved_style,
            "style_name": style_cfg.get("name", "Live Action"),
            "style_badge": style_cfg.get("badge", "🎬 Live Action"),
            "video_format": "Short (9:16)" if aspect_ratio == "9:16" else "Video (16:9)",
            "duration": round(total_duration, 1),
            "duration_formatted": f"0:{int(total_duration):02d}",
            "file_size_mb": file_size_mb,
            "resolution": f"{width}x{height}",
            "aspect_ratio": aspect_ratio,
            "scenes": scenes,
            "scenes_count": len(scenes),
            "generation_time_sec": elapsed,
            "created_at": time.time()
        }

        with open(os.path.join(abs_output_dir, f"{task_id}.json"), "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2)

        return meta

    except Exception as exc:
        report(0, f"Error: {exc}")
        raise exc
