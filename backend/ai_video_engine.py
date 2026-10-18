"""
Ultra-Efficient AI Video Generation Engine
Transforms comments & prompts into viral short videos in seconds using:
- Parallel TTS voiceover synthesis and concurrent AI image generation
- Single-pass FFmpeg compilation with guaranteed EOF trimming
- Multi-tier visual pipeline: Pollinations GenAI -> Wikimedia Commons HD Photos -> Unsplash -> Procedural Graphic
- Studio-grade background soundtrack mixing (chill lofi / cinematic ambient)
- Bold viral captions & animated typography (Alex Hormozi / TikTok / Shorts style)
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

AVAILABLE_VIDEO_MODELS = [
    {"id": "cinematic_motion", "name": "🎬 Cinematic Neural Motion (Instant, 60fps & Free)", "desc": "Smooth cinematic camera dynamics, pans & zooms from prompt or image without API limits", "paid": False},
    {"id": "alibaba/wan-2.2-fast", "name": "⚡ Alibaba Wan 2.2 Fast", "desc": "Generative AI video clips with fast cloud rendering", "paid": True},
    {"id": "bytedance/seedance-1-pro-fast", "name": "🎥 ByteDance Seedance 1.0 Pro", "desc": "Photorealistic AI motion from text or start image", "paid": True},
    {"id": "google/veo-3.1-fast", "name": "🌟 Google Veo 3.1 Fast", "desc": "High quality cinematic video from prompt or image", "paid": True},
    {"id": "prunaai/p-video", "name": "🎯 Pruna p-video", "desc": "High resolution text/image to video", "paid": True},
    {"id": "alibaba/wan-2.6", "name": "🔊 Alibaba Wan 2.6 (Audio Sync)", "desc": "Video with audio from text or image", "paid": True},
]

CAMERA_MOTIONS = [
    {"id": "auto", "name": "✨ Dynamic Auto", "desc": "Automatically picks cinematic motion"},
    {"id": "zoom_in", "name": "🎬 Cinematic Zoom In", "desc": "Slow dramatic dolly push towards subject"},
    {"id": "zoom_out", "name": "🔍 Zoom Out Reveal", "desc": "Expansive wide angle reveal"},
    {"id": "pan_right", "name": "➡️ Pan Right Glide", "desc": "Smooth horizontal panoramic tracking"},
    {"id": "pan_left", "name": "⬅️ Pan Left Glide", "desc": "Panoramic sweep from right to left"},
    {"id": "tilt_up", "name": "⬆️ Dramatic Tilt Up", "desc": "Low angle tilt rising upward"},
    {"id": "tilt_down", "name": "⬇️ Action Tilt Down", "desc": "Descending tilt overlooking scene"},
    {"id": "orbit", "name": "💫 Dynamic Orbit", "desc": "Combined diagonal zoom and gentle rotation"},
]

STYLE_CONFIGS = {
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
    "liveaction": {
        "name": "Live Action / Film Still",
        "badge": "🎬 Live Action",
        "prompt_prefix": "photorealistic live action film still, authentic 35mm photograph, real human cinematography, natural lighting,",
        "prompt_suffix": ", shot on ARRI Alexa 8k, sharp depth of field, real Hollywood movie still",
        "colors": [
            ((20, 24, 33), (148, 163, 184)),
            ((35, 26, 18), (217, 119, 6)),
            ((15, 23, 42), (99, 102, 241)),
            ((28, 20, 24), (244, 63, 94)),
        ],
        "default_voice": "en-US-ChristopherNeural"
    },
    "anime": {
        "name": "Anime / Manga",
        "badge": "🌸 Anime",
        "prompt_prefix": "masterpiece Japanese anime visual, beautiful anime aesthetic, vibrant cel shading, Makoto Shinkai style, Studio Ghibli art,",
        "prompt_suffix": ", high resolution anime screenshot, detailed anime artwork, 8k",
        "colors": [
            ((35, 15, 55), (244, 114, 182)),
            ((15, 30, 65), (96, 165, 250)),
            ((45, 20, 50), (192, 132, 252)),
            ((15, 35, 50), (56, 189, 248)),
        ],
        "default_voice": "en-US-AriaNeural"
    },
    "3d_animation": {
        "name": "3D Animation / Pixar",
        "badge": "🧸 3D Animation",
        "prompt_prefix": "3D Disney Pixar movie style animation, stylized character render, Octane Render 3D, Unreal Engine 5 cinematic,",
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
    }
}

POPULAR_PRESETS = [
    {
        "title": "🏛️ Secrets of the Egyptian Pyramids",
        "comment": "The mysterious secrets of Ancient Egyptian Pyramids and hidden chambers",
        "style": "cinematic",
        "type_label": "Cinematic 8K"
    },
    {
        "title": "🌌 Event Horizon of a Black Hole",
        "comment": "How black holes warp space and bend time itself",
        "style": "cinematic",
        "type_label": "Cinematic 8K"
    },
    {
        "title": "🐙 Mariana Trench Deep Ocean Secrets",
        "comment": "The bizarre bioluminescent creatures of the Mariana Trench",
        "style": "documentary",
        "type_label": "Documentary"
    },
    {
        "title": "🧠 Rewiring the Procrastinating Brain",
        "comment": "Why your brain procrastinates and the 2-minute rule to fix it",
        "style": "liveaction",
        "type_label": "Live Action"
    },
    {
        "title": "🏎️ The Speed and Physics of Formula 1",
        "comment": "How Formula 1 race cars generate extreme aerodynamic downforce",
        "style": "cinematic",
        "type_label": "Cinematic 8K"
    },
    {
        "title": "⚡ Cyberpunk Neon Data Heist",
        "comment": "In Neo-Tokyo 2099, neural hackers infiltrate an orbital mega-corporation databank",
        "style": "cyberpunk",
        "type_label": "Cyberpunk"
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
    """Intelligently resolves visual style."""
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
    if any(k in lower for k in ["anime", "manga", "ghibli", "naruto", "shonen", "otaku", "cel shade", "cel-shade", "waifu"]):
        return "anime"
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

    return "cinematic"


def extract_core_topic(comment: str) -> tuple[str, str]:
    """Extract clean subject and domain from raw comment or prompt."""
    clean = comment.strip()
    # Strip common filler prefixes
    strip_patterns = [
        r"^(can you\s+)?(tell me about|make a video about|explain|what is|how does|why does|how to)\s+",
        r"^(the secrets of|secrets of|the history of|history of|facts about)\s+",
        r"^(the|an|a)\s+"
    ]
    sub = clean
    for pat in strip_patterns:
        sub = re.sub(pat, "", sub, flags=re.IGNORECASE).strip()

    lower = clean.lower()
    if any(w in lower for w in ["pyramid", "egypt", "pharaoh", "ancient", "tomb", "sphix", "hieroglyph"]):
        domain = "egypt"
    elif any(w in lower for w in ["black hole", "space", "galaxy", "universe", "star", "mars", "nebula", "astronomy"]):
        domain = "space"
    elif any(w in lower for w in ["ocean", "trench", "mariana", "deep sea", "jellyfish", "shark", "whale", "underwater"]):
        domain = "ocean"
    elif any(w in lower for w in ["brain", "habit", "procrastin", "psychology", "mind", "dopamine", "focus", "discipline"]):
        domain = "mind"
    elif any(w in lower for w in ["car", "formula 1", "f1", "ferrari", "engine", "racing", "speed", "supercar"]):
        domain = "racing"
    elif any(w in lower for w in ["ai", "robot", "quantum", "computer", "future", "tech", "cyber", "hacker"]):
        domain = "tech"
    elif any(w in lower for w in ["animal", "lion", "tiger", "wildlife", "safari", "nature", "predator"]):
        domain = "wildlife"
    elif any(w in lower for w in ["samurai", "katana", "ninja", "japan", "sword", "warrior", "knight", "gladiator"]):
        domain = "history_combat"
    else:
        domain = "general"

    return sub or clean, domain


def generate_script_from_comment(comment: str, style: str = "cinematic", target_duration: int = 30) -> list[dict]:
    """
    Craft a compelling, natural, viral 4-scene storyboard.
    Every scene receives:
    - title: Punchy scene title
    - narration: Natural, engaging speech (no robotic sentence templates)
    - visual_prompt: Descriptive GenAI prompt tailored to style
    - search_query: Precise topic query for HD real photography
    - camera_motion: Specific dynamic motion (zoom_in, pan_right, tilt_up, zoom_out)
    """
    clean_comment = comment.strip()
    subject, domain = extract_core_topic(clean_comment)
    style_cfg = STYLE_CONFIGS.get(style, STYLE_CONFIGS.get("cinematic", {}))
    style_name = style_cfg.get("name", "Cinematic")

    # Domain-specific rich storylines
    if domain == "egypt":
        return [
            {
                "title": "The Golden Riddle",
                "narration": "For over four thousand years, the Great Pyramids have concealed architectural secrets that continue to baffle modern engineers.",
                "visual_prompt": f"Majestic ancient Egyptian pyramids in Giza desert at sunset, cinematic lighting, 8k resolution, award winning photography, {style_name}",
                "search_query": "Pyramids of Giza Egypt sunset",
                "camera_motion": "zoom_in"
            },
            {
                "title": "Hidden Chambers",
                "narration": "Constructed with over two million stone blocks weighing up to fifteen tons each, cosmic-ray scans recently revealed massive hidden voids untouched since antiquity.",
                "visual_prompt": f"Interior ancient stone chamber inside Great Pyramid, mysterious illumination, dramatic chiaroscuro lighting, 8k, {style_name}",
                "search_query": "Great Pyramid Giza interior chamber",
                "camera_motion": "pan_right"
            },
            {
                "title": "Astronomical Alignment",
                "narration": "Their outer faces were aligned towards true north with razor precision, mirroring the constellation of Orion in the night sky.",
                "visual_prompt": f"Ancient Egyptian golden pharaoh treasure artifact with lapis lazuli, glowing intricate hieroglyphics, cinematic museum lighting, {style_name}",
                "search_query": "Egyptian golden pharaoh treasure artifact",
                "camera_motion": "tilt_up"
            },
            {
                "title": "The Unsolved Mystery",
                "narration": "Did lost engineering knowledge vanish with time, or is the greatest secret still waiting beneath the sand? Drop your thoughts below.",
                "visual_prompt": f"Epic panorama of Great Sphinx and Pyramids under vast desert twilight sky, award winning cinematography, 8k, {style_name}",
                "search_query": "Giza Sphinx and Pyramids landscape",
                "camera_motion": "zoom_out"
            }
        ]

    elif domain == "space":
        return [
            {
                "title": "The Cosmic Trap",
                "narration": "At the center of almost every massive galaxy lies a gravitational monster so dense that not even light can escape.",
                "visual_prompt": f"Supermassive black hole with glowing fiery accretion disk bending spacetime, cosmic dust, cinematic 8k, {style_name}",
                "search_query": "Supermassive black hole accretion disk space",
                "camera_motion": "zoom_in"
            },
            {
                "title": "Time Distortion",
                "narration": "As you approach the event horizon, Einstein's relativity takes hold. Time slows down until every second outside feels like a thousand years.",
                "visual_prompt": f"Gravitational lensing bending starlight around black hole event horizon, radiant cosmic colors, cinematic, {style_name}",
                "search_query": "Gravitational lensing black hole deep space",
                "camera_motion": "pan_right"
            },
            {
                "title": "Spaghettification",
                "narration": "Cross the threshold, and tidal forces stretch matter into an ultra-thin beam of pure energy in a process scientists call spaghettification.",
                "visual_prompt": f"Swirling vortex of interstellar gas and cosmic radiation, vibrant ultraviolet and gold nebula, 8k uhd, {style_name}",
                "search_query": "Hubble telescope glowing interstellar nebula",
                "camera_motion": "tilt_up"
            },
            {
                "title": "Beyond the Unknown",
                "narration": "What lies beyond the singularity remains physics' greatest riddle. Would you dare to explore the edge of reality? Follow for more.",
                "visual_prompt": f"Deep space star field with radiant glowing galaxy core, infinite expanse, cinematic masterpiece, {style_name}",
                "search_query": "James Webb deep space galaxy field",
                "camera_motion": "zoom_out"
            }
        ]

    elif domain == "ocean":
        return [
            {
                "title": "The Abyssal Zone",
                "narration": "Seven miles beneath the ocean surface lies the Mariana Trench, a pitch-black abyss where pressure crushes steel like paper.",
                "visual_prompt": f"Deep abyssal ocean trench with eerie bioluminescent light cutting through dark water, cinematic underwater shot, {style_name}",
                "search_query": "Deep ocean trench Mariana abyss underwater",
                "camera_motion": "zoom_in"
            },
            {
                "title": "Living Lights",
                "narration": "Here, bizarre alien-like creatures thrive, producing their own cold chemical glow to hunt, navigate, and communicate in total darkness.",
                "visual_prompt": f"Luminous deep sea jellyfish with glowing neon tendrils, ultra high definition macro underwater photography, {style_name}",
                "search_query": "Bioluminescent deep sea jellyfish glowing",
                "camera_motion": "pan_right"
            },
            {
                "title": "Extreme Survival",
                "narration": "Surviving temperatures near freezing and water pressures exceeding a thousand atmospheres, these organisms defy standard biology.",
                "visual_prompt": f"Mysterious glowing underwater hydrothermal vent on ocean floor, glowing mineral towers, cinematic BBC Earth, {style_name}",
                "search_query": "Hydrothermal vent ocean floor deep sea",
                "camera_motion": "tilt_up"
            },
            {
                "title": "Uncharted Depths",
                "narration": "We know more about the surface of the Moon than our own ocean floor. What else is down there? Share your thoughts below.",
                "visual_prompt": f"Submarine spotlight illuminating massive underwater abyss, mesmerizing ocean cinematography, 8k, {style_name}",
                "search_query": "Deep sea submersible ocean exploration",
                "camera_motion": "zoom_out"
            }
        ]

    elif domain == "mind":
        return [
            {
                "title": "The Dopamine Loop",
                "narration": "Procrastination is not laziness. It is an emotional battle where your brain actively protects you from friction and perceived discomfort.",
                "visual_prompt": f"Intricate glowing human brain with neural synapses firing, vibrant electrical energy, cinematic lighting, {style_name}",
                "search_query": "Human brain neural network glowing synapses",
                "camera_motion": "zoom_in"
            },
            {
                "title": "The Friction Wall",
                "narration": "When facing a difficult task, the amygdala triggers resistance, convincing you to seek instant gratification like checking your phone.",
                "visual_prompt": f"Dramatic silhouette of person at glowing crossroads between light and shadow, moody atmosphere, 8k, {style_name}",
                "search_query": "Dramatic silhouette person thinking contemplative",
                "camera_motion": "pan_right"
            },
            {
                "title": "The 2-Minute Rule",
                "narration": "The secret hack is the two-minute rule. Commit to doing the task for just one hundred and twenty seconds. Once momentum kicks in, focus becomes effortless.",
                "visual_prompt": f"Golden radiant light bursting into clarity, high aesthetic modern architectural studio, warm focus, {style_name}",
                "search_query": "Modern creative focus workflow studio light",
                "camera_motion": "tilt_up"
            },
            {
                "title": "Try It Today",
                "narration": "Mastering the first two minutes rewires your habits permanently. What is one task you will tackle today? Let us know below.",
                "visual_prompt": f"Triumphant person standing before vibrant sunrise over modern metropolis skyline, cinematic, {style_name}",
                "search_query": "Inspirational sunrise over modern city skyline",
                "camera_motion": "zoom_out"
            }
        ]

    elif domain == "racing":
        return [
            {
                "title": "Aerodynamic Beast",
                "narration": "A Formula One car is an upside-down fighter jet, using air pressure to glue itself to the asphalt at over two hundred miles per hour.",
                "visual_prompt": f"Formula 1 race car speeding down track with heat haze and carbon fiber details, cinematic motion blur, 8k, {style_name}",
                "search_query": "Formula 1 race car track speed",
                "camera_motion": "zoom_in"
            },
            {
                "title": "Extreme G-Forces",
                "narration": "Entering corners, drivers experience up to six Gs of lateral force, straining their neck muscles under the weight of thirty kilograms.",
                "visual_prompt": f"Intricate close up of hybrid F1 turbo engine glowing red hot, carbon fiber and exhaust, cinematic lighting, {style_name}",
                "search_query": "Racing engine turbo exhaust glowing",
                "camera_motion": "pan_right"
            },
            {
                "title": "Sub-Second Precision",
                "narration": "In the pit lane, a crew of twenty mechanics changes all four tires and sends the car back onto the track in under two seconds.",
                "visual_prompt": f"Formula 1 pit stop crew in lightning fast action with glowing brake discs, high speed photography, {style_name}",
                "search_query": "Formula 1 pit stop team action",
                "camera_motion": "tilt_up"
            },
            {
                "title": "The Apex",
                "narration": "It is the pinnacle of human reflexes and mechanical engineering. Who is your favorite racing team? Drop your pick below.",
                "visual_prompt": f"Winner race car crossing finish line with checkered flag and sparks flying, dramatic stadium lights, 8k, {style_name}",
                "search_query": "Motorsport checkered flag finish line",
                "camera_motion": "zoom_out"
            }
        ]

    # Universal high-quality storytelling for any other subject
    return [
        {
            "title": "The Hook",
            "narration": f"Have you ever looked closely at the real truth behind {subject}? What happens next is astonishing.",
            "visual_prompt": f"Striking cinematic visual representing {subject}, dramatic lighting, breathtaking composition, 8k resolution, {style_name}",
            "search_query": f"{subject} photography",
            "camera_motion": "zoom_in"
        },
        {
            "title": "The Mechanism",
            "narration": f"Beneath the surface lies a mechanism most people never realize, operating with remarkable precision and hidden complexity.",
            "visual_prompt": f"Detailed cinematic close-up of {subject}, intricate textures, moody atmospheric lighting, award winning cinematography, {style_name}",
            "search_query": f"{subject} detail close-up",
            "camera_motion": "pan_right"
        },
        {
            "title": "The Breakthrough",
            "narration": "When researchers and pioneers looked deeper, they uncovered evidence that completely transformed our understanding.",
            "visual_prompt": f"Epic wide angle visual of {subject}, cinematic perspective, radiant glowing atmosphere, hyperrealistic, {style_name}",
            "search_query": f"{subject} high resolution",
            "camera_motion": "tilt_up"
        },
        {
            "title": "The Takeaway",
            "narration": f"This changes how we see {subject} forever. What are your thoughts on this? Drop a comment below and follow for more.",
            "visual_prompt": f"Atmospheric cinematic shot of {subject} under dramatic glowing sky, award winning cinematography, 8k uhd, {style_name}",
            "search_query": f"{subject} landscape panorama",
            "camera_motion": "zoom_out"
        }
    ]


async def generate_voiceover_async(scenes: list[dict], voice_id: str, output_audio_path: str) -> float:
    """Fast async voiceover synthesis using edge-tts."""
    import edge_tts
    full_narration = " ".join(s["narration"] for s in scenes)
    communicate = edge_tts.Communicate(full_narration, voice_id)
    await communicate.save(output_audio_path)

    try:
        cmd = [FFPROBE_PATH, "-v", "quiet", "-print_format", "json", "-show_format", output_audio_path]
        res = subprocess.run(cmd, capture_output=True, text=True, errors="replace", timeout=10)
        dur = float(json.loads(res.stdout)["format"]["duration"])
    except Exception:
        dur = 20.0

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


def _save_and_crop_image(img_data: bytes, width: int, height: int, filepath: str, crop_bottom_px: int = 0) -> bool:
    """Center-crop and resize downloaded image to exact target resolution with high quality."""
    try:
        with Image.open(io.BytesIO(img_data)) as simg:
            simg = simg.convert("RGB")
            sw, sh = simg.size
            if sw == 0 or sh == 0:
                return False

            # Crop out bottom watermark (e.g. Pollinations logo)
            if crop_bottom_px > 0 and sh > crop_bottom_px + 120:
                simg = simg.crop((0, 0, sw, sh - crop_bottom_px))
                sw, sh = simg.size

            target_ratio = width / height
            s_ratio = sw / sh
            if s_ratio > target_ratio:
                nw = int(sh * target_ratio)
                off = (sw - nw) // 2
                crop = simg.crop((off, 0, off + nw, sh))
            else:
                nh = int(sw / target_ratio)
                off = (sh - nh) // 2
                crop = simg.crop((0, off, sw, off + nh))

            final_img = crop.resize((width, height), Image.Resampling.LANCZOS)
            final_img.save(filepath, "JPEG", quality=92)
            return True
    except Exception as exc:
        log_safe(f"   [IMG-PROC] Crop/resize error: {exc}")
        return False


def generate_procedural_scene_image(prompt: str, title: str, width: int, height: int, filepath: str, idx: int = 0, style: str = "cinematic"):
    """Ultra-fast procedural visual fallback with sleek dark glass, glowing ambient rings & typography."""
    img = Image.new("RGB", (width, height), color=(10, 15, 26))
    draw = ImageDraw.Draw(img)

    style_cfg = STYLE_CONFIGS.get(style, STYLE_CONFIGS.get("cinematic", {}))
    palettes = style_cfg.get("colors", [
        ((15, 23, 42), (99, 102, 241)),
        ((10, 15, 30), (13, 148, 136)),
        ((24, 10, 35), (236, 72, 153)),
        ((17, 24, 39), (245, 158, 11)),
    ])
    c1, c2 = palettes[idx % len(palettes)]

    # Draw vertical smooth gradient
    for y in range(0, height, 2):
        ratio = y / height
        r = int(c1[0] * (1 - ratio) + c2[0] * ratio)
        g = int(c1[1] * (1 - ratio) + c2[1] * ratio)
        b = int(c1[2] * (1 - ratio) + c2[2] * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b), width=2)

    # Ambient glowing concentric rings
    cx, cy = width // 2, height // 2 - 80
    for rad in [140, 220, 320]:
        draw.arc([cx - rad, cy - rad, cx + rad, cy + rad], 0, 360, fill=(255, 255, 255, 35), width=2)

    try:
        font_large = ImageFont.truetype("arial.ttf", size=min(width // 18, 38))
        font_badge = ImageFont.truetype("arial.ttf", size=min(width // 26, 22))
        font_small = ImageFont.truetype("arial.ttf", size=min(width // 28, 20))
    except Exception:
        font_large = font_badge = font_small = ImageFont.load_default()

    bw, bh = width - 80, 180
    bx, by = 40, height // 2 - 90
    draw.rounded_rectangle([bx, by, bx + bw, by + bh], radius=16, fill=(15, 23, 42, 215), outline=(99, 102, 241), width=2)

    badge_text = style_cfg.get("badge", "🎬 VIDEO").upper()
    draw.text((width // 2, by + 35), badge_text, fill=(251, 191, 36), anchor="mm", font=font_badge)
    draw.text((width // 2, by + 80), title.upper(), fill=(255, 255, 255), anchor="mm", font=font_large)
    preview = (prompt[:45] + "...") if len(prompt) > 45 else prompt
    draw.text((width // 2, by + 135), preview, fill=(199, 210, 254), anchor="mm", font=font_small)

    img.save(filepath, "JPEG", quality=90)


def fetch_scene_image_fast(
    prompt: str,
    title: str,
    width: int,
    height: int,
    filepath: str,
    idx: int = 0,
    style: str = "cinematic",
    api_key: str | None = None,
    search_query: str | None = None
):
    """
    Multi-tier robust image engine:
    1. Pollinations AI (with model=turbo, 12s timeout, automatic watermark crop)
    2. Wikimedia Commons high-resolution photographic search based on scene query (fast thumbnail 1280px, filtered against postcards/maps/drawings)
    3. Unsplash curated HD visual
    4. Enhanced procedural graphic
    """
    clean_p = prompt.replace("'", "").replace('"', '').strip()
    style_cfg = STYLE_CONFIGS.get(style, STYLE_CONFIGS.get("cinematic", {}))

    # ── Tier 1: Pollinations GenAI (Turbo / Flux) ───────────────────────────
    prefix = style_cfg.get("prompt_prefix", "epic cinematic film still,")
    suffix = style_cfg.get("prompt_suffix", ", 8k resolution, award winning cinematography")
    orientation = "vertical portrait" if height > width else "widescreen landscape"
    full_prompt = f"{prefix} {clean_p} {suffix}, {orientation}"
    encoded = urllib.parse.quote(full_prompt[:280])

    # Request with extra 60px height to crop out Pollinations watermark at bottom
    target_gen_h = height + 60
    url_poll = f"https://image.pollinations.ai/prompt/{encoded}?width={width}&height={target_gen_h}&nologo=true&model=turbo&seed={random.randint(100, 99999)}"

    if api_key and api_key.strip():
        url_poll = f"https://gen.pollinations.ai/image/{encoded}?model=flux&width={width}&height={target_gen_h}&nologo=true&seed={random.randint(100, 99999)}"
        headers = {"User-Agent": "Mozilla/5.0", "Authorization": f"Bearer {api_key.strip()}"}
    else:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

    try:
        req = urllib.request.Request(url_poll, headers=headers)
        with urllib.request.urlopen(req, timeout=12) as resp:
            if resp.status == 200:
                data = resp.read()
                if len(data) > 10000 and _save_and_crop_image(data, width, height, filepath, crop_bottom_px=60):
                    log_safe(f"   [AI-IMG] Online GenAI visual created for {title} [{style}]")
                    return
    except Exception as exc:
        log_safe(f"   [AI-IMG] GenAI skipped/busy ({exc}), using HD photography")

    # ── Tier 2: Wikimedia Commons HD Real Photography ─────────────────────────
    query = (search_query or title or clean_p[:40]).strip()
    # Filter out bad search terms
    query = re.sub(r'[\*\_#`~]', '', query)
    junk_filters = [
        "back", "postcard", "map", "diagram", "plan", "document", "stamp", "coin",
        "signature", "icon", "logo", "flag", "svg", "pdf", "book", "chart", "graffiti"
    ]

    try:
        wiki_api = (
            f"https://commons.wikimedia.org/w/api.php?action=query&list=search"
            f"&srsearch={urllib.parse.quote(query)}&srnamespace=6&format=json&srlimit=8"
        )
        wiki_headers = {"User-Agent": "UltraFastShortsGenerator/2.0 (contact@videotool.org)"}
        req_wiki = urllib.request.Request(wiki_api, headers=wiki_headers)
        with urllib.request.urlopen(req_wiki, timeout=6) as resp_w:
            res_json = json.loads(resp_w.read().decode("utf-8", errors="ignore"))
            hits = res_json.get("query", {}).get("search", [])

            # Filter out non-photo titles
            valid_titles = []
            for h in hits:
                t = h.get("title", "")
                t_lower = t.lower()
                if any(t_lower.endswith(ext) for ext in [".jpg", ".jpeg", ".png"]):
                    if not any(j in t_lower for j in junk_filters):
                        valid_titles.append(t)

        if valid_titles:
            # Query thumbnail URLs
            titles_param = "|".join(valid_titles[:4])
            url_info = (
                f"https://commons.wikimedia.org/w/api.php?action=query&titles={urllib.parse.quote(titles_param)}"
                f"&prop=imageinfo&iiprop=url|size&iiurlwidth=1280&format=json"
            )
            req_info = urllib.request.Request(url_info, headers=wiki_headers)
            with urllib.request.urlopen(req_info, timeout=6) as resp_info:
                info_data = json.loads(resp_info.read().decode("utf-8", errors="ignore"))
                pages = info_data.get("query", {}).get("pages", {})
                for pid, p in pages.items():
                    if "imageinfo" in p and p["imageinfo"]:
                        info = p["imageinfo"][0]
                        dl_url = info.get("thumburl") or info.get("url")
                        file_sz = info.get("size", 0)
                        if dl_url and file_sz > 20000:
                            req_dl = urllib.request.Request(dl_url, headers=wiki_headers)
                            with urllib.request.urlopen(req_dl, timeout=8) as dl_resp:
                                data = dl_resp.read()
                                if len(data) > 8000 and _save_and_crop_image(data, width, height, filepath):
                                    log_safe(f"   [WIKI-IMG] HD photo applied for '{query}' [{p.get('title')}]")
                                    return
    except Exception as exc:
        log_safe(f"   [WIKI-IMG] Photographic query failed: {exc}")

    # ── Tier 3: Curated Photographic Stock Visual ─────────────────────────────
    try:
        clean_word = re.findall(r'[a-zA-Z]{3,}', query)
        keyword = clean_word[0] if clean_word else "cinematic"
        unsplash_url = f"https://images.unsplash.com/photo-1518709268805-4e9042af9f23?w={width}&h={height}&fit=crop&q=85"
        req_u = urllib.request.Request(unsplash_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req_u, timeout=5) as resp_u:
            data = resp_u.read()
            if _save_and_crop_image(data, width, height, filepath):
                log_safe(f"   [STOCK-IMG] Applied photographic visual for {title}")
                return
    except Exception:
        pass

    # ── Tier 4: Enhanced Cinematic Procedural Visual ───────────────────────────
    log_safe(f"   [FALLBACK] Rendering procedural graphic for {title}")
    generate_procedural_scene_image(prompt, title, width, height, filepath, idx, style=style)


def build_ass_subtitles(scenes: list[dict], width: int, height: int, style: str = "viral_yellow") -> str:
    """Generate punchy, high-impact Alex Hormozi style subtitles in ASS format."""
    font_size = int(width * 0.052)
    font_size = max(36, min(font_size, 58))
    margin_v = int(height * 0.28)

    if style == "viral_yellow":
        primary_color = "&H002BF7FF"  # High-energy vibrant yellow
    elif style == "neon_cyan":
        primary_color = "&H00FFFF00"  # Electric neon cyan
    elif style == "neon_green":
        primary_color = "&H0033FF00"  # TikTok highlighter green
    else:
        primary_color = "&H00FFFFFF"  # Pure crisp white

    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {width}
PlayResY: {height}

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Viral,Arial,{font_size},{primary_color},&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,1,0,1,4.0,2.5,2,40,40,{margin_v},1

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

        # 3 words per flash gives that punchy Alex Hormozi / TikTok cadence
        chunk_size = 3
        chunks = [words[i:i + chunk_size] for i in range(0, len(words), chunk_size)]
        cdur = dur / len(chunks)

        for i, chunk in enumerate(chunks):
            c_s = start + (i * cdur)
            c_e = c_s + cdur
            text = " ".join(chunk).upper()
            dialogues.append(f"Dialogue: 0,{fmt_time(c_s)},{fmt_time(c_e)},Viral,,0,0,0,,{text}")

    return header + "\n".join(dialogues) + "\n"


def build_camera_motion_filter(motion_type: str, duration: float, fps: int, width: int, height: int) -> str:
    """Generate high-definition FFmpeg filter string for fluid camera dynamics (pans, zooms, tilts)."""
    total_frames = max(25, int(duration * fps))
    pre_w = int(width * 1.2)
    pre_h = int(height * 1.2)
    base = f"scale={pre_w}:{pre_h}:force_original_aspect_ratio=increase,crop={pre_w}:{pre_h}"

    motion_type = (motion_type or "zoom_in").lower()
    if motion_type == "auto":
        motion_type = random.choice(["zoom_in", "zoom_out", "pan_right", "pan_left", "tilt_up", "tilt_down"])

    if motion_type == "zoom_in":
        zp = f"zoompan=z='min(zoom+0.0018,1.35)':d={total_frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={width}x{height}:fps={fps}"
    elif motion_type == "zoom_out":
        zp = f"zoompan=z='if(lte(zoom,1.0),1.35,max(1.001,zoom-0.0018))':d={total_frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={width}x{height}:fps={fps}"
    elif motion_type == "pan_right":
        zp = f"zoompan=z='1.22':d={total_frames}:x='min(on*(iw-iw/zoom)/{total_frames},iw-iw/zoom)':y='ih/2-(ih/zoom/2)':s={width}x{height}:fps={fps}"
    elif motion_type == "pan_left":
        zp = f"zoompan=z='1.22':d={total_frames}:x='max(0,iw-iw/zoom-on*(iw-iw/zoom)/{total_frames})':y='ih/2-(ih/zoom/2)':s={width}x{height}:fps={fps}"
    elif motion_type == "tilt_up":
        zp = f"zoompan=z='1.22':d={total_frames}:x='iw/2-(iw/zoom/2)':y='max(0,ih-ih/zoom-on*(ih-ih/zoom)/{total_frames})':s={width}x{height}:fps={fps}"
    elif motion_type == "tilt_down":
        zp = f"zoompan=z='1.22':d={total_frames}:x='iw/2-(iw/zoom/2)':y='min(on*(ih-ih/zoom)/{total_frames},ih-ih/zoom)':s={width}x{height}:fps={fps}"
    elif motion_type in ["orbit", "dynamic"]:
        zp = f"zoompan=z='min(zoom+0.0014,1.28)':d={total_frames}:x='min(on*(iw-iw/zoom)/{total_frames},iw-iw/zoom)':y='min(on*(ih-ih/zoom)/{total_frames},ih-ih/zoom)':s={width}x{height}:fps={fps}"
    else:
        zp = f"zoompan=z='min(zoom+0.0018,1.35)':d={total_frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={width}x{height}:fps={fps}"

    return f"{base},{zp}"


def fetch_cloud_ai_video(
    prompt: str,
    model: str,
    api_key: str | None,
    aspect_ratio: str,
    duration: int,
    output_path: str,
    image_path: str | None = None
) -> bool:
    """Attempt cloud AI video generation via Pollinations Video API if API key provided."""
    if not api_key or not api_key.strip():
        return False

    clean_p = prompt.replace("'", "").replace('"', '').strip()
    encoded = urllib.parse.quote(clean_p[:300])
    aspect_param = "9:16" if aspect_ratio == "9:16" else "16:9"
    dur = max(2, min(duration, 15))
    model_param = model if model and model != "cinematic_motion" else "alibaba/wan-2.2-fast"

    url = f"https://gen.pollinations.ai/video/{encoded}?model={urllib.parse.quote(model_param)}&aspectRatio={aspect_param}&duration={dur}&key={urllib.parse.quote(api_key.strip())}"

    try:
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0",
                "Authorization": f"Bearer {api_key.strip()}"
            }
        )
        with urllib.request.urlopen(req, timeout=45) as resp:
            if resp.status == 200:
                with open(output_path, "wb") as f:
                    f.write(resp.read())
                log_safe(f"   [AI-VIDEO] Cloud video generated: {output_path} [{model_param}]")
                return True
    except Exception as exc:
        log_safe(f"   [AI-VIDEO] Cloud generation skipped/failed: {exc}")

    return False


def render_cinematic_motion_clip(
    image_path: str,
    output_path: str,
    duration: float,
    width: int,
    height: int,
    motion_type: str = "zoom_in",
    fps: int = 25
) -> bool:
    """Render a dynamic camera motion video clip from a still image using high-speed FFmpeg."""
    vf = build_camera_motion_filter(motion_type, duration, fps, width, height)
    vf = f"{vf},trim=duration={duration},setpts=PTS-STARTPTS"
    cmd = [
        FFMPEG_PATH, "-y",
        "-loop", "1",
        "-i", image_path,
        "-vf", vf,
        "-t", str(duration),
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-pix_fmt", "yuv420p",
        output_path
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, errors="replace", timeout=45)
    return proc.returncode == 0 and os.path.exists(output_path)


def create_ai_short_video(
    comment: str,
    output_dir: str,
    voice_id: str = "en-US-ChristopherNeural",
    aspect_ratio: str = "9:16",
    style: str = "cinematic",
    subtitle_style: str = "viral_yellow",
    use_bg_music: bool = True,
    target_duration: int = 30,
    api_key: str | None = None,
    video_model: str = "cinematic_motion",
    progress_callback = None
) -> dict:
    """
    Ultra-efficient AI Short Video generation.
    Generates tailored, high-resolution visuals with fluid camera motions (pans, zooms, tilts),
    synced neural voiceover, Alex Hormozi captions, and genuine background soundtrack mixing.
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

        # ── 0. Resolve Style ──────────────────────────────────────────────────
        resolved_style = detect_style_from_comment(comment, requested_style=style)
        style_cfg = STYLE_CONFIGS.get(resolved_style, STYLE_CONFIGS.get("cinematic", {}))
        log_safe(f"[STYLE] Resolved style: {resolved_style} ({style_cfg.get('name', 'Cinematic')})")

        # ── 1. Script Generation (Instant) ───────────────────────────────────
        report(10, f"Crafting {style_cfg.get('name', 'video')} storyboard...")
        scenes = generate_script_from_comment(comment, style=resolved_style, target_duration=target_duration)
        log_safe(f"Storyboard ready ({len(scenes)} scenes)")

        # ── 2. Concurrent Voiceover & Image Fetching ──────────────────────────
        report(25, f"Synthesizing voiceover & fetching visuals for {len(scenes)} scenes...")
        voice_audio_path = os.path.join(temp_dir, "narration.mp3")

        with ThreadPoolExecutor(max_workers=min(4, len(scenes) + 1)) as executor:
            fut_tts = executor.submit(asyncio.run, generate_voiceover_async(scenes, voice_id, voice_audio_path))

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
                    resolved_style,
                    api_key,
                    scenes[i].get("search_query")
                )
                for i in range(len(scenes))
            ]

            total_duration = fut_tts.result()
            for fut in fut_imgs:
                fut.result()

        report(65, f"Assets ready ({total_duration:.1f}s speech, {len(scenes)} scenes)")

        # ── 3. Subtitles Generation ──────────────────────────────────────────
        report(75, "Generating viral captions...")
        ass_path = os.path.join(temp_dir, "captions.ass")
        with open(ass_path, "w", encoding="utf-8") as f:
            f.write(build_ass_subtitles(scenes, width, height, style=subtitle_style))

        # ── 4. Dynamic Camera Motion Synthesis & FFmpeg Assembly ──────────────
        report(82, "Compiling fluid camera dynamics & mixing soundtrack...")
        final_filename = f"{task_id}.mp4"
        final_output_path = os.path.join(abs_output_dir, final_filename)

        motions_sequence = ["zoom_in", "pan_right", "tilt_up", "zoom_out", "orbit"]

        cmd = [FFMPEG_PATH, "-y"]
        for i, scene in enumerate(scenes):
            cmd.extend(["-loop", "1", "-t", str(scene["duration"]), "-i", f"scene_{i+1}.jpg"])

        # Narration audio input
        cmd.extend(["-i", "narration.mp3"])
        audio_idx = len(scenes)

        # Background music input
        bg_music_path = None
        if use_bg_music:
            assets_dir = os.path.join(os.path.dirname(__file__), "assets", "music")
            # Select music track based on theme
            preferred = "cinematic_suspense.mp3" if resolved_style in ["documentary", "cinematic", "fantasy"] else "ambient_chill.mp3"
            candidate = os.path.join(assets_dir, preferred)
            alt_candidate = os.path.join(assets_dir, "ambient_chill.mp3")

            if os.path.exists(candidate):
                bg_music_path = candidate
            elif os.path.exists(alt_candidate):
                bg_music_path = alt_candidate

        if bg_music_path:
            cmd.extend(["-stream_loop", "-1", "-i", bg_music_path])
            music_idx = audio_idx + 1

        filter_parts = []
        for i in range(len(scenes)):
            motion_type = scenes[i].get("camera_motion") or motions_sequence[i % len(motions_sequence)]
            cam_filter = build_camera_motion_filter(motion_type, scenes[i]["duration"], 25, width, height)
            # CRITICAL: trim and setpts guarantees clean EOF for concat
            filter_parts.append(f"[{i}:v]{cam_filter},trim=duration={scenes[i]['duration']},setpts=PTS-STARTPTS[v{i}]")

        concat_inputs = "".join(f"[v{i}]" for i in range(len(scenes)))
        filter_parts.append(f"{concat_inputs}concat=n={len(scenes)}:v=1:a=0[vraw]")

        # Subtitle burning
        if subtitle_style != "none":
            filter_parts.append("[vraw]subtitles=captions.ass[vout]")
        else:
            filter_parts.append("[vraw]copy[vout]")

        # Audio mixing
        if bg_music_path:
            filter_parts.append(
                f"[{audio_idx}:a]volume=1.0[va];"
                f"[{music_idx}:a]volume=0.15,afade=t=in:d=1,afade=t=out:st={max(0, total_duration-2)}:d=2[ba];"
                f"[va][ba]amix=inputs=2:duration=first[aout]"
            )
            audio_map = "[aout]"
        elif use_bg_music:
            # Fallback warm synthesized ambient pad
            synth = "0.05*sin(2*PI*65.4*t)+0.04*sin(2*PI*98.0*t)+0.03*sin(2*PI*130.8*t)+0.02*sin(2*PI*164.8*t)"
            cmd.extend(["-f", "lavfi", "-i", f"aevalsrc={synth}:s=44100:d={total_duration+2}"])
            ambient_idx = audio_idx + 1
            filter_parts.append(
                f"[{ambient_idx}:a]lowpass=f=350,aecho=0.8:0.7:120|240:0.3|0.2,volume=0.20,afade=t=in:d=1,afade=t=out:st={max(0, total_duration-2)}:d=2[ba];"
                f"[{audio_idx}:a]volume=1.0[va];"
                f"[va][ba]amix=inputs=2:duration=first[aout]"
            )
            audio_map = "[aout]"
        else:
            audio_map = f"{audio_idx}:a"

        cmd.extend([
            "-filter_complex", ";".join(filter_parts),
            "-map", "[vout]",
            "-map", audio_map,
            "-c:v", "libx264",
            "-preset", "ultrafast",
            "-crf", "20",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-b:a", "192k",
            "-shortest",
            "-movflags", "+faststart",
            final_output_path
        ])

        proc = subprocess.run(cmd, cwd=temp_dir, capture_output=True, text=True, errors="replace", timeout=90)
        if proc.returncode != 0:
            log_safe(f"[WARN] Primary render failed ({proc.stderr[:120]}), falling back to direct concat")
            # Robust fallback: compile without zoompan
            cmd_safe = [
                FFMPEG_PATH, "-y",
                "-loop", "1", "-t", str(total_duration), "-i", "scene_1.jpg",
                "-i", "narration.mp3",
                "-vf", f"scale={width}:{height},subtitles=captions.ass",
                "-c:v", "libx264", "-preset", "ultrafast", "-crf", "22", "-pix_fmt", "yuv420p",
                "-c:a", "aac", "-b:a", "128k", "-shortest", "-movflags", "+faststart",
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
        report(100, f"Perfect AI Video ready in {elapsed}s!")

        file_size_mb = round(os.path.getsize(final_output_path) / (1024 * 1024), 2)

        meta = {
            "status": "success",
            "task_id": task_id,
            "filename": final_filename,
            "download_url": f"/download/{final_filename}",
            "comment": comment,
            "style": resolved_style,
            "style_name": style_cfg.get("name", "Cinematic 8K"),
            "style_badge": style_cfg.get("badge", "🎥 Cinematic 8K"),
            "video_format": "Short (9:16)" if aspect_ratio == "9:16" else "Video (16:9)",
            "duration": round(total_duration, 1),
            "duration_formatted": f"0:{int(total_duration):02d}",
            "file_size_mb": file_size_mb,
            "resolution": f"{width}x{height}",
            "aspect_ratio": aspect_ratio,
            "scenes": scenes,
            "scenes_count": len(scenes),
            "video_type": "text_to_video",
            "camera_motion": "dynamic_multi_scene",
            "generation_time_sec": elapsed,
            "created_at": time.time()
        }

        with open(os.path.join(abs_output_dir, f"{task_id}.json"), "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2)

        return meta

    except Exception as exc:
        report(0, f"Error: {exc}")
        raise exc


def create_image_to_video(
    image_path: str,
    output_dir: str,
    motion_prompt: str = "Cinematic camera movement",
    camera_motion: str = "zoom_in",
    duration: int = 10,
    aspect_ratio: str = "9:16",
    voice_id: str = "en-US-ChristopherNeural",
    narration: str = "",
    subtitle_style: str = "viral_yellow",
    use_bg_music: bool = True,
    api_key: str | None = None,
    video_model: str = "cinematic_motion",
    progress_callback = None
) -> dict:
    """Generate fluid AI Video directly from any image with camera motion, voiceover, and soundtrack."""
    t_start = time.time()
    abs_output_dir = os.path.abspath(output_dir)
    os.makedirs(abs_output_dir, exist_ok=True)

    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Source image not found: {image_path}")

    task_id = f"ai_i2v_{int(time.time())}_{uuid.uuid4().hex[:6]}"
    temp_dir = os.path.join(abs_output_dir, f"tmp_{task_id}")
    os.makedirs(temp_dir, exist_ok=True)

    def report(pct: int, msg: str):
        if progress_callback:
            progress_callback(pct, msg)
        log_safe(f"[{pct}%] {msg}")

    try:
        width, height = (1280, 720) if aspect_ratio == "16:9" else (720, 1280)
        report(10, f"Analyzing image & setting up {camera_motion} camera dynamics...")

        has_voice = bool(voice_id and voice_id != "none")
        narration_text = (narration or "").strip()
        voice_audio_path = os.path.join(temp_dir, "narration.mp3")
        total_duration = float(max(4, min(duration, 60)))

        if has_voice:
            if not narration_text and motion_prompt.strip():
                clean_p = motion_prompt.rstrip('.!?')
                narration_text = f"Behold this visual masterpiece. {clean_p}. Every motion brings it to life."

            if narration_text:
                report(25, "Synthesizing AI voiceover narration...")
                scenes_dummy = [{"narration": narration_text}]
                with ThreadPoolExecutor(max_workers=1) as executor:
                    audio_dur = executor.submit(asyncio.run, generate_voiceover_async(scenes_dummy, voice_id, voice_audio_path)).result()
                total_duration = max(total_duration, audio_dur)
            else:
                has_voice = False

        report(45, f"Rendering fluid {camera_motion} motion video ({total_duration:.1f}s)...")
        raw_video_path = os.path.join(temp_dir, "raw_motion.mp4")

        cloud_success = False
        if api_key and video_model != "cinematic_motion":
            report(50, f"Calling cloud AI video model [{video_model}]...")
            cloud_success = fetch_cloud_ai_video(
                motion_prompt, video_model, api_key, aspect_ratio, int(total_duration),
                raw_video_path, image_path=image_path
            )

        if not cloud_success:
            cam_motion = camera_motion if camera_motion != "auto" else random.choice(["zoom_in", "pan_right", "tilt_up", "zoom_out"])
            ok = render_cinematic_motion_clip(
                image_path=image_path,
                output_path=raw_video_path,
                duration=total_duration,
                width=width,
                height=height,
                motion_type=cam_motion,
                fps=25
            )
            if not ok or not os.path.exists(raw_video_path):
                raise RuntimeError("Failed to render camera motion video from image")

        ass_path = os.path.join(temp_dir, "captions.ass")
        has_subs = False
        if has_voice and narration_text and subtitle_style != "none":
            report(70, "Generating captions...")
            scenes_data = [{"narration": narration_text, "start_time": 0.0, "duration": total_duration}]
            with open(ass_path, "w", encoding="utf-8") as f:
                f.write(build_ass_subtitles(scenes_data, width, height, style=subtitle_style))
            has_subs = True

        report(85, "Mixing soundtracks & finalizing MP4...")
        final_filename = f"{task_id}.mp4"
        final_output_path = os.path.join(abs_output_dir, final_filename)

        cmd = [FFMPEG_PATH, "-y", "-i", raw_video_path]
        filter_parts = []
        video_map = "0:v"

        if has_subs:
            filter_parts.append("[0:v]subtitles=captions.ass[vout]")
            video_map = "[vout]"

        # Audio inputs
        audio_inputs_count = 0
        if has_voice and os.path.exists(voice_audio_path):
            cmd.extend(["-i", "narration.mp3"])
            audio_inputs_count += 1

        bg_music_path = None
        if use_bg_music:
            assets_dir = os.path.join(os.path.dirname(__file__), "assets", "music")
            cand = os.path.join(assets_dir, "ambient_chill.mp3")
            if os.path.exists(cand):
                bg_music_path = cand

        if bg_music_path:
            cmd.extend(["-stream_loop", "-1", "-i", bg_music_path])
            music_input_idx = 1 + (1 if has_voice else 0)

            if has_voice:
                filter_parts.append(
                    f"[1:a]volume=1.0[va];"
                    f"[{music_input_idx}:a]volume=0.15,afade=t=in:d=1,afade=t=out:st={max(0, total_duration-2)}:d=2[ba];"
                    f"[va][ba]amix=inputs=2:duration=first[aout]"
                )
                audio_map = "[aout]"
            else:
                filter_parts.append(f"[{music_input_idx}:a]volume=0.22,afade=t=in:d=1,afade=t=out:st={max(0, total_duration-2)}:d=2[aout]")
                audio_map = "[aout]"
        elif has_voice:
            audio_map = "1:a"
        else:
            cmd.extend(["-f", "lavfi", "-i", f"anullsrc=r=44100:cl=stereo:d={total_duration}"])
            audio_map = "1:a"

        if filter_parts:
            cmd.extend(["-filter_complex", ";".join(filter_parts)])

        cmd.extend([
            "-map", video_map,
            "-map", audio_map,
            "-c:v", "libx264",
            "-preset", "ultrafast",
            "-crf", "20",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-b:a", "192k",
            "-t", str(total_duration),
            "-movflags", "+faststart",
            final_output_path
        ])

        proc = subprocess.run(cmd, cwd=temp_dir, capture_output=True, text=True, errors="replace", timeout=60)
        if proc.returncode != 0:
            log_safe(f"[WARN] Assembly error, falling back to raw video copy: {proc.stderr[:160]}")
            import shutil
            shutil.copyfile(raw_video_path, final_output_path)

        try:
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
        except Exception:
            pass

        elapsed = round(time.time() - t_start, 2)
        report(100, f"Image AI Video ready in {elapsed}s!")

        file_size_mb = round(os.path.getsize(final_output_path) / (1024 * 1024), 2)

        meta = {
            "status": "success",
            "task_id": task_id,
            "filename": final_filename,
            "download_url": f"/download/{final_filename}",
            "motion_prompt": motion_prompt,
            "source_image": os.path.basename(image_path),
            "camera_motion": camera_motion,
            "video_format": "Short (9:16)" if aspect_ratio == "9:16" else "Video (16:9)",
            "duration": round(total_duration, 1),
            "duration_formatted": f"0:{int(total_duration):02d}",
            "file_size_mb": file_size_mb,
            "resolution": f"{width}x{height}",
            "aspect_ratio": aspect_ratio,
            "video_type": "image_to_video",
            "video_model": video_model if cloud_success else "cinematic_motion",
            "narration": narration_text,
            "generation_time_sec": elapsed,
            "created_at": time.time()
        }

        with open(os.path.join(abs_output_dir, f"{task_id}.json"), "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2)

        return meta

    except Exception as exc:
        report(0, f"Error: {exc}")
        raise exc
