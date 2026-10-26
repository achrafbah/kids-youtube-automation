"""Advanced 2.5D Animated Video & Pedagogical Overlays Engine.
Implements:
- Option 2: Real Animation Flow (Veo 3.1 AI video with auto-fallback to Kinetic Multi-Shot Camera Motion)
- Option 3: Synchronized Arabic Subtitles with full Tashkeel & Animated Cartoon Overlays (Stars, Badges, Emojis)
Designed specifically for Preschool & Primary Kids (ages 3 to 10).
"""

import os
import re
import sys
import wave
import subprocess
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional

import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter, features
import arabic_reshaper
from bidi.algorithm import get_display
import imageio_ffmpeg
from google import genai
from google.genai import types

def get_font_path() -> str:
    """Resolve cross-platform Arabic font for Windows, Linux, and GitHub Actions."""
    repo_font = Path(__file__).resolve().parent.parent / "assets" / "fonts" / "Arial.ttf"
    if repo_font.exists():
        return str(repo_font)
    for p in ["C:\\Windows\\Fonts\\arial.ttf", "C:\\Windows\\Fonts\\segoeui.ttf"]:
        if os.path.exists(p):
            return p
    for p in [
        "/usr/share/fonts/truetype/noto/NotoSansArabic-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSans.ttf"
    ]:
        if os.path.exists(p):
            return p
    return "Arial"

FONT_PATH = get_font_path()

def draw_kawaii_star(target_size=120):
    scale = 4
    size = target_size * scale
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    cx, cy = size / 2, size / 2
    r_outer = size * 0.42
    r_inner = size * 0.20
    
    # Shadow
    pts_shadow = []
    for i in range(10):
        angle = -math.pi / 2 + i * math.pi / 5
        r = r_outer if i % 2 == 0 else r_inner
        pts_shadow.append((cx + r * math.cos(angle), cy + r * math.sin(angle) + 12))
    draw.polygon(pts_shadow, fill=(180, 80, 0, 160))

    # Main golden body
    pts_main = []
    for i in range(10):
        angle = -math.pi / 2 + i * math.pi / 5
        r = r_outer if i % 2 == 0 else r_inner
        pts_main.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
    draw.polygon(pts_main, fill=(255, 218, 25, 255), outline=(235, 120, 10, 255), width=7)

    # Highlight on top point
    pts_hi = [
        pts_main[0],
        (cx + (pts_main[1][0] - cx)*0.55, cy + (pts_main[1][1] - cy)*0.55),
        (cx, cy - r_inner*0.3),
        (cx + (pts_main[9][0] - cx)*0.55, cy + (pts_main[9][1] - cy)*0.55),
    ]
    draw.polygon(pts_hi, fill=(255, 255, 215, 230))
    
    # Eyes
    eye_y = cy - 6 * scale
    eye_r = 5 * scale
    draw.ellipse([cx - 18*scale - eye_r, eye_y - eye_r*1.2, cx - 18*scale + eye_r, eye_y + eye_r*1.2], fill=(40, 20, 5, 255))
    draw.ellipse([cx + 18*scale - eye_r, eye_y - eye_r*1.2, cx + 18*scale + eye_r, eye_y + eye_r*1.2], fill=(40, 20, 5, 255))
    
    # Eye shine
    draw.ellipse([cx - 20*scale, eye_y - eye_r*0.9, cx - 16*scale, eye_y - eye_r*0.1], fill=(255, 255, 255, 255))
    draw.ellipse([cx + 16*scale, eye_y - eye_r*0.9, cx + 20*scale, eye_y - eye_r*0.1], fill=(255, 255, 255, 255))
    
    # Smile
    draw.arc([cx - 12*scale, cy + 2*scale, cx + 12*scale, cy + 18*scale], start=10, end=170, fill=(180, 50, 0, 255), width=5)

    return img.resize((target_size, target_size), Image.Resampling.LANCZOS)

def draw_sparkle(target_size=120):
    scale = 4
    size = target_size * scale
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    cx, cy = size / 2, size / 2
    r_long = size * 0.44
    r_short = size * 0.08
    
    pts = [
        (cx, cy - r_long),
        (cx + r_short, cy - r_short),
        (cx + r_long, cy),
        (cx + r_short, cy + r_short),
        (cx, cy + r_long),
        (cx - r_short, cy + r_short),
        (cx - r_long, cy),
        (cx - r_short, cy - r_short)
    ]
    glow = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    g_draw = ImageDraw.Draw(glow)
    g_draw.polygon(pts, fill=(255, 240, 100, 180))
    glow = glow.filter(ImageFilter.GaussianBlur(radius=6 * scale // 2))
    img.alpha_composite(glow)
    
    draw.polygon(pts, fill=(255, 255, 240, 255), outline=(255, 215, 0, 255), width=5)
    draw.ellipse([cx - 6*scale, cy - 6*scale, cx + 6*scale, cy + 6*scale], fill=(255, 255, 255, 255))
    return img.resize((target_size, target_size), Image.Resampling.LANCZOS)

def draw_heart(target_size=120):
    scale = 4
    size = target_size * scale
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    cx, cy = size / 2, size / 2
    r = size * 0.22
    s_y = cy + 10
    draw.ellipse([cx - 2*r, s_y - 1.2*r, cx, s_y + 0.8*r], fill=(120, 10, 30, 140))
    draw.ellipse([cx, s_y - 1.2*r, cx + 2*r, s_y + 0.8*r], fill=(120, 10, 30, 140))
    draw.polygon([(cx - 1.9*r, s_y - 0.2*r), (cx + 1.9*r, s_y - 0.2*r), (cx, s_y + 1.9*r)], fill=(120, 10, 30, 140))

    draw.ellipse([cx - 2*r, cy - 1.4*r, cx, cy + 0.6*r], fill=(255, 45, 85, 255))
    draw.ellipse([cx, cy - 1.4*r, cx + 2*r, cy + 0.6*r], fill=(255, 45, 85, 255))
    draw.polygon([(cx - 1.9*r, cy - 0.4*r), (cx + 1.9*r, cy - 0.4*r), (cx, cy + 1.7*r)], fill=(255, 45, 85, 255))
    draw.ellipse([cx - 1.5*r, cy - 1.1*r, cx - 0.5*r, cy - 0.3*r], fill=(255, 180, 200, 220))
    draw.ellipse([cx - 1.3*r, cy - 0.9*r, cx - 0.8*r, cy - 0.5*r], fill=(255, 255, 255, 240))
    return img.resize((target_size, target_size), Image.Resampling.LANCZOS)

def draw_bubble(target_size=120):
    scale = 4
    size = target_size * scale
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    cx, cy = size / 2, size / 2
    r = size * 0.40
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(120, 210, 255, 60), outline=(100, 220, 255, 220), width=6)
    r_in = r * 0.92
    draw.arc([cx - r_in, cy - r_in, cx + r_in, cy + r_in], start=160, end=290, fill=(255, 255, 255, 230), width=8)
    shine_r = r * 0.35
    draw.ellipse([cx - r*0.55 - shine_r, cy - r*0.55 - shine_r*0.6, cx - r*0.55 + shine_r, cy - r*0.55 + shine_r*0.6], fill=(255, 255, 255, 240))
    return img.resize((target_size, target_size), Image.Resampling.LANCZOS)


class AnimationEngine:
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()
        self.env_file = base_dir / ".env"
        self.api_key = self._get_api_key()

    def _get_api_key(self) -> str:
        if self.env_file.exists():
            for line in open(self.env_file, encoding="utf-8"):
                if line.startswith("GEMINI_API_KEY="):
                    return line.strip().split("=", 1)[1]
        return os.environ.get("GEMINI_API_KEY", "AQ.Ab8RN6Ly6CghBsKIp9KFboAoEWe_N7hlrKwYhzBosimjI_JVrA")

    def get_audio_duration(self, audio_path: Path) -> float:
        """Get exact duration in seconds from WAV file."""
        try:
            with wave.open(str(audio_path), "rb") as wf:
                frames = wf.getnframes()
                rate = wf.getframerate()
                return max(1.0, frames / float(rate))
        except Exception:
            return 23.0

    def split_script_into_phrases(self, script_text: str) -> List[str]:
        """Split Arabic narration into kid-friendly short sentences for subtitle cards."""
        import re
        # Split on Arabic punctuation
        raw_chunks = re.split(r'[!؟.\n]+', script_text)
        phrases = []
        for c in raw_chunks:
            cleaned = c.strip()
            if cleaned:
                # If too long (more than 10 words), split by comma
                if len(cleaned.split()) > 10:
                    sub_chunks = cleaned.split("،")
                    for sc in sub_chunks:
                        if sc.strip():
                            phrases.append(sc.strip())
                else:
                    phrases.append(cleaned)
        return phrases if phrases else [script_text]

    def calculate_timings(self, phrases: List[str], total_duration: float) -> List[Dict[str, Any]]:
        """Calculate start and end timestamps proportional to word counts."""
        lengths = [max(1, len(p.split())) for p in phrases]
        total_words = sum(lengths)
        
        timings = []
        current_time = 0.4  # small opening delay
        usable_duration = total_duration - 0.6
        
        for p, w_len in zip(phrases, lengths):
            p_dur = (w_len / total_words) * usable_duration
            start = round(current_time, 2)
            end = round(current_time + p_dur, 2)
            current_time += p_dur
            timings.append({
                "text": p,
                "start": start,
                "end": end
            })
        return timings

    @staticmethod
    def format_arabic_for_render(text: str) -> tuple[str, dict]:
        """Format and clean Arabic text for Pillow rendering across Linux (with Raqm) and Windows/fallback (without Raqm)."""
        clean = re.sub(r'''[^\u0600-\u06FF\u0750-\u077F\u08A0-\u08FFa-zA-Z0-9\s!?,.:;\-\(\)|«»"'/]+''', '', text).strip()
        clean = re.sub(r'\s+', ' ', clean)
        if features.check('raqm'):
            return clean, {"direction": "rtl", "language": "ar"}
        else:
            reshaped = arabic_reshaper.reshape(clean)
            bidi_txt = get_display(reshaped)
            return bidi_txt, {}

    def create_header_badge(self, title_text: str, out_path: Path, theme: str = "default") -> Path:
        """Render glowing top pedagogical header badge with dynamic theme colors."""
        w, h = 940, 110
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Color palette per theme
        palette_map = {
            "emerald": {"fill": (18, 56, 36, 240), "outline": (250, 204, 21, 255)},
            "sapphire": {"fill": (24, 45, 95, 240), "outline": (56, 189, 248, 255)},
            "amber": {"fill": (78, 34, 16, 240), "outline": (251, 146, 60, 255)},
            "teal": {"fill": (15, 55, 65, 240), "outline": (45, 212, 191, 255)},
            "twilight": {"fill": (45, 28, 75, 240), "outline": (192, 132, 252, 255)},
            "ruby": {"fill": (75, 18, 28, 240), "outline": (248, 113, 113, 255)},
            "default": {"fill": (28, 38, 72, 235), "outline": (255, 215, 0, 255)},
        }
        pal = palette_map.get(theme, palette_map["default"])
        
        draw.rounded_rectangle([8, 8, w - 8, h - 8], radius=38, fill=pal["fill"], outline=pal["outline"], width=3)
        draw.rounded_rectangle([13, 13, w - 13, h - 13], radius=34, outline=(255, 255, 255, 45), width=1)
        
        formatted_txt, text_kwargs = self.format_arabic_for_render(title_text)
        font_size = 38
        font = ImageFont.truetype(FONT_PATH, font_size)
        bbox = draw.textbbox((0, 0), formatted_txt, font=font, **text_kwargs)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        while tw > (w - 70) and font_size > 22:
            font_size -= 2
            font = ImageFont.truetype(FONT_PATH, font_size)
            bbox = draw.textbbox((0, 0), formatted_txt, font=font, **text_kwargs)
            tw = bbox[2] - bbox[0]
            th = bbox[3] - bbox[1]
        
        tx = (w - tw) // 2
        ty = (h - th) // 2 - 4
        
        # Shadow & text
        draw.text((tx + 2, ty + 2), formatted_txt, font=font, fill=(0, 0, 0, 200), **text_kwargs)
        draw.text((tx, ty), formatted_txt, font=font, fill=(255, 255, 255, 255), stroke_fill=(15, 20, 35, 255), stroke_width=2, **text_kwargs)
        
        out_path.parent.mkdir(parents=True, exist_ok=True)
        img.save(out_path)
        return out_path

    def create_subtitle_card(self, text: str, emoji: str, out_path: Path) -> Path:
        """Render stylish, readable Arabic subtitle card with tashkeel for kids."""
        w, h = 1000, 190
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Translucent dark indigo card with cheerful warm gold border
        draw.rounded_rectangle([10, 10, w - 10, h - 10], radius=45, fill=(16, 20, 36, 230), outline=(255, 205, 40, 245), width=4)
        draw.rounded_rectangle([16, 16, w - 16, h - 16], radius=40, outline=(255, 255, 255, 60), width=1)
        
        formatted_txt, text_kwargs = self.format_arabic_for_render(text)
        font_size = 46 if len(formatted_txt) < 38 else (38 if len(formatted_txt) < 60 else 32)
        font = ImageFont.truetype(FONT_PATH, font_size)
        bbox = draw.textbbox((0, 0), formatted_txt, font=font, **text_kwargs)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        while tw > (w - 70) and font_size > 22:
            font_size -= 2
            font = ImageFont.truetype(FONT_PATH, font_size)
            bbox = draw.textbbox((0, 0), formatted_txt, font=font, **text_kwargs)
            tw = bbox[2] - bbox[0]
            th = bbox[3] - bbox[1]
        
        tx = (w - tw) // 2
        ty = (h - th) // 2 - 6
        
        # Drop shadow
        draw.text((tx + 3, ty + 3), formatted_txt, font=font, fill=(0, 0, 0, 220), **text_kwargs)
        # Text
        draw.text((tx, ty), formatted_txt, font=font, fill=(255, 255, 255, 255), stroke_fill=(10, 15, 25, 255), stroke_width=3, **text_kwargs)
        
        out_path.parent.mkdir(parents=True, exist_ok=True)
        img.save(out_path)
        return out_path

    def create_floating_element(self, emoji: str, out_path: Path) -> Path:
        """Create animated floating transparent cartoon particle asset without font/glyph bugs."""
        out_path.parent.mkdir(parents=True, exist_ok=True)
        e = emoji.strip() if emoji else ""
        if e in ["⭐", "🌟", "star"]:
            img = draw_kawaii_star(120)
        elif e in ["✨", "sparkle"]:
            img = draw_sparkle(120)
        elif e in ["❤️", "💖", "heart"]:
            img = draw_heart(120)
        elif e in ["🫧", "💧", "bubble"]:
            img = draw_bubble(120)
        else:
            img = draw_kawaii_star(120)
            
        img.save(out_path)
        return out_path

    def create_floating_star(self, out_path: Path) -> Path:
        """Legacy helper for backward compatibility."""
        return self.create_floating_element("⭐", out_path)

    def get_cinematography_and_theme(self, topic_title: str, script_text: str) -> Dict[str, Any]:
        """Determine theme palette, floating particle emojis, and unique camera profile."""
        combined = (topic_title + " " + script_text).lower()
        hash_val = int(hashlib.md5(topic_title.encode("utf-8")).hexdigest(), 16)
        
        # Determine theme palette and particles
        if any(w in combined for w in ["حرف", "حروف", "ألف", "باء", "لغة", "قراءة"]):
            theme = "sapphire"
            p1, p2 = "🔤", "✨"
        elif any(w in combined for w in ["عد", "أرقام", "رقم", "حساب", "رياضيات", "أشكال"]):
            theme = "amber"
            p1, p2 = "🔢", "⭐"
        elif any(w in combined for w in ["أسنان", "نظافة", "غسل", "صابون", "ماء", "يدين"]):
            theme = "teal"
            p1, p2 = "🫧", "💧"
        elif any(w in combined for w in ["نوم", "ليل", "قمر", "نجوم", "مساء"]):
            theme = "twilight"
            p1, p2 = "🌙", "⭐"
        elif any(w in combined for w in ["رياضة", "نشاط", "صباح", "حركة", "قفز"]):
            theme = "ruby"
            p1, p2 = "⚡", "🌟"
        elif any(w in combined for w in ["حيوان", "طبيعة", "غابة", "أليف", "طيور", "كلب"]):
            theme = "emerald"
            p1, p2 = "🦋", "🌸"
        elif any(w in combined for w in ["ألوان", "رسم", "قوس", "لوحة"]):
            theme = "amber"
            p1, p2 = "🎨", "🌈"
        elif any(w in combined for w in ["فواكه", "طعام", "خضار", "أكل"]):
            theme = "emerald"
            p1, p2 = "🍎", "✨"
        else:
            theme = "emerald" if (hash_val % 2 == 0) else "sapphire"
            p1, p2 = "🌟", "❤️"

        # Camera choreography profile (0 to 4 guaranteed varied cinematography)
        cam_profile = hash_val % 5
        return {
            "theme": theme,
            "particle1": p1,
            "particle2": p2,
            "cam_profile": cam_profile
        }

    def try_veo_animation(self, image_path: Path, prompt: str, output_path: Path) -> Optional[Path]:
        """Attempt Veo 3.1 Fast video generation with graceful quota-exhaustion fallback."""
        print("🎬 [Option 2] Probing Veo 3.1 Fast AI Animation engine...", flush=True)
        try:
            client = genai.Client(api_key=self.api_key)
            with open(image_path, "rb") as f:
                img_bytes = f.read()
            image = types.Image(image_bytes=img_bytes, mime_type="image/jpeg")
            
            operation = client.models.generate_videos(
                model="veo-3.1-fast-generate-preview",
                source=types.GenerateVideosSource(
                    prompt=prompt,
                    image=image
                ),
                config=types.GenerateVideosConfig(
                    aspect_ratio="9:16",
                    duration_seconds=4,
                )
            )
            print("Veo operation started. Polling status...", flush=True)
            import time
            while not operation.done:
                time.sleep(8)
                operation = client.operations.get(operation)
            
            if hasattr(operation, "response") and operation.response and getattr(operation.response, "generated_videos", None):
                video_obj = operation.response.generated_videos[0].video
                client.files.download(file=video_obj, destination=str(output_path))
                print(f"🎉 Veo AI Animation SUCCESS: {output_path}", flush=True)
                return output_path
        except Exception as e:
            print(f"ℹ️ Veo 3.1 notice: {e}")
            print("🔄 Falling back seamlessly to Advanced Kinetic Multi-Camera Engine & Overlays.")
            return None

    def render_animated_episode(
        self,
        scene_image_path: Path,
        audio_path: Path,
        bgm_path: Path,
        topic_title: str,
        script_text: str,
        output_video_path: Path,
        theme_emoji: str = "🧸",
        theme_palette: Optional[str] = None,
        particles: Optional[tuple] = None,
        camera_profile: Optional[int] = None
    ) -> Path:
        """Render high-engagement, fully animated 9:16 Shorts with options 2 & 3 and zero repetition."""
        print("🎬 [Option 2 & 3] Rendering animated episode with dynamic multi-profile cinematography...", flush=True)
        output_video_path.parent.mkdir(parents=True, exist_ok=True)
        work_dir = output_video_path.parent / "render_assets"
        work_dir.mkdir(parents=True, exist_ok=True)

        duration = self.get_audio_duration(audio_path)
        print(f"Voiceover duration: {duration:.2f} seconds", flush=True)

        # Step 0: Resolve dynamic theme and cinematography profile
        if theme_palette and particles and camera_profile is not None:
            style_info = {
                "theme": theme_palette,
                "particle1": particles[0],
                "particle2": particles[1],
                "cam_profile": camera_profile
            }
        else:
            style_info = self.get_cinematography_and_theme(topic_title, script_text)

        print(f"🎨 Theme: {style_info['theme']} | Particles: {style_info['particle1']} {style_info['particle2']} | Camera Profile: #{style_info['cam_profile']}", flush=True)

        # Step 1: Prepare base 1080x1920 image
        base_img = Image.open(scene_image_path).resize((1080, 1920), Image.Resampling.LANCZOS)
        temp_base = work_dir / "base_frame.jpg"
        base_img.save(temp_base, quality=95)

        # Step 2: Render Top Header Badge with Theme Colors
        header_path = work_dir / "header_badge.png"
        header_text = f"حِكَايَاتُ العَجَائِب | {topic_title.split(':')[0].strip()}"
        self.create_header_badge(header_text, header_path, theme=style_info["theme"])

        # Step 3: Render Floating Animated Elements
        part1_path = work_dir / "particle_1.png"
        part2_path = work_dir / "particle_2.png"
        self.create_floating_element(style_info["particle1"], part1_path)
        self.create_floating_element(style_info["particle2"], part2_path)

        # Step 4: Generate Synchronized Subtitle Cards
        phrases = self.split_script_into_phrases(script_text)
        timings = self.calculate_timings(phrases, duration)
        print(f"Generated {len(timings)} synchronized Arabic subtitle phrases.", flush=True)

        subtitle_cards = []
        emojis = [theme_emoji, style_info["particle1"], "✨", "❤️", style_info["particle2"], "🌟", "🎉"]
        for idx, item in enumerate(timings):
            card_p = work_dir / f"sub_{idx}.png"
            em = emojis[idx % len(emojis)]
            self.create_subtitle_card(item["text"], em, card_p)
            subtitle_cards.append((card_p, item["start"], item["end"]))

        # Step 5: Build FFmpeg Filter Graph with Dynamic Cinematography Profiles
        total_frames = int(duration * 30 + 30)
        profile = style_info["cam_profile"]

        if profile == 0:
            # Profile 0: Dynamic Ken Burns Push-in with Gentle Atmospheric Sway
            cam_filter = (
                f"zoompan=z='min(zoom+0.0006,1.16)':d={total_frames}:"
                f"x='iw/2-(iw/zoom/2)+15*sin(in/40)':y='ih/2-(ih/zoom/2)*0.82+10*cos(in/45)':s=1080x1920:fps=30"
            )
        elif profile == 1:
            # Profile 1: Heroic Panoramic Tracking Dolly Pan
            cam_filter = (
                f"zoompan=z='1.12':d={total_frames}:"
                f"x='(iw-iw/zoom)*(0.35+0.30*sin(in/({total_frames}*0.8)))':y='ih/2-(ih/zoom/2)*0.84':s=1080x1920:fps=30"
            )
        elif profile == 2:
            # Profile 2: Playful Character Pulse & Speech Cadence
            cam_filter = (
                f"zoompan=z='1.06+0.035*sin(in/28)':d={total_frames}:"
                f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)*0.82+8*sin(in/22)':s=1080x1920:fps=30"
            )
        elif profile == 3:
            # Profile 3: Dramatic Reveal Glide from Scene to Leo's Close-up
            cam_filter = (
                f"zoompan=z='min(zoom+0.0005,1.15)':d={total_frames}:"
                f"x='iw/2-(iw/zoom/2)':y='(ih-ih/zoom)*(0.22+0.28*min(in/({total_frames}*0.6),1.0))':s=1080x1920:fps=30"
            )
        else:
            # Profile 4: Warm Upward Glide & Soft Close-up Focus
            cam_filter = (
                f"zoompan=z='min(zoom+0.0006,1.14)':d={total_frames}:"
                f"x='iw/2-(iw/zoom/2)+12*cos(in/35)':y='(ih-ih/zoom)*(0.55-0.22*min(in/({total_frames}*0.7),1.0))':s=1080x1920:fps=30"
            )

        filter_parts = [
            f"[0:v]{cam_filter},eq=saturation=1.12:contrast=1.04,format=yuv420p[base];"
        ]

        # Overlay Header at top
        filter_parts.append("[base][3:v]overlay=x=(W-w)/2:y=110[v_head];")

        # Overlay Animated Floating Particles (varied dynamic orbits)
        filter_parts.append("[v_head][4:v]overlay=x='90+35*sin(t*2.3)':y='310+28*cos(t*1.9)':eval=frame[v_p1];")
        filter_parts.append("[v_p1][5:v]overlay=x='W-w-90+32*cos(t*2.5)':y='340+30*sin(t*2.1)':eval=frame[v_particles];")

        # Overlay timed subtitle cards
        prev_stream = "v_particles"
        input_offset = 6  # inputs: 0=base, 1=audio, 2=bgm, 3=header, 4=part1, 5=part2, 6...=subs

        for idx, (card_p, start_t, end_t) in enumerate(subtitle_cards):
            curr_stream = f"v_sub_{idx}"
            inp_idx = input_offset + idx
            filter_parts.append(
                f"[{prev_stream}][{inp_idx}:v]overlay=x=(W-w)/2:y=H-h-180:enable='between(t,{start_t},{end_t})'[{curr_stream}];"
            )
            prev_stream = curr_stream

        # Audio mix
        filter_parts.append("[1:a]volume=1.0[voice];")
        filter_parts.append("[2:a]volume=0.12[bgm];")
        filter_parts.append("[voice][bgm]amix=inputs=2:duration=first:dropout_transition=2[a]")

        filter_complex = "".join(filter_parts)

        # Assemble full FFmpeg command
        cmd = [
            self.ffmpeg_bin,
            "-y",
            "-loop", "1", "-i", str(temp_base),
            "-i", str(audio_path),
            "-stream_loop", "-1", "-i", str(bgm_path),
            "-i", str(header_path),
            "-i", str(part1_path),
            "-i", str(part2_path),
        ]

        for card_p, _, _ in subtitle_cards:
            cmd.extend(["-i", str(card_p)])

        cmd.extend([
            "-filter_complex", filter_complex,
            "-map", f"[{prev_stream}]",
            "-map", "[a]",
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "20",
            "-c:a", "aac",
            "-b:a", "192k",
            "-t", str(duration),
            str(output_video_path)
        ])

        print(f"🎬 Executing FFmpeg animation rendering ({duration:.1f}s)...", flush=True)
        subprocess.run(cmd, check=True)
        print(f"✅ Animated 2.5D Video with Subtitles & Overlays ready at: {output_video_path}", flush=True)
        return output_video_path
