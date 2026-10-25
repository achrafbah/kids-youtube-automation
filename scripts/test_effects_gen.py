import os
import sys
import re
import math
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import arabic_reshaper
from bidi.algorithm import get_display
import imageio_ffmpeg

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "output" / "test_effects"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

FONT_PATH = "C:\\Windows\\Fonts\\arial.ttf"

def draw_kawaii_star(target_size=120):
    """Render high-resolution 3D cartoon kawaii star with smooth anti-aliasing."""
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

def clean_arabic_text(text: str) -> str:
    # Strip any emojis or unsupported unicode that render as tofu squares
    clean = re.sub(r'''[^\u0600-\u06FF\u0750-\u077F\u08A0-\u08FFa-zA-Z0-9\s!?,.:;\-\(\)|«»"'/]+''', '', text)
    return re.sub(r'\s+', ' ', clean).strip()

def create_header_badge(title_text="حِكَايَاتُ العَجَائِب • بَرْنَامَجُ الأَخْلَاق", out_path=None):
    w, h = 920, 110
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Rounded badge background: pastel soft purple-blue gradient
    draw.rounded_rectangle([10, 10, w - 10, h - 10], radius=40, fill=(35, 45, 80, 225), outline=(255, 215, 0, 255), width=3)
    
    # Draw cute star icon on the badge
    badge_star = draw_kawaii_star(55)
    img.paste(badge_star, (28, (h - 55) // 2), badge_star)
    img.paste(badge_star, (w - 28 - 55, (h - 55) // 2), badge_star)

    cleaned = clean_arabic_text(title_text)
    font = ImageFont.truetype(FONT_PATH, 40)
    reshaped = arabic_reshaper.reshape(cleaned)
    bidi_txt = get_display(reshaped)
    
    bbox = draw.textbbox((0, 0), bidi_txt, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    
    tx = (w - tw) // 2
    ty = (h - th) // 2 - 5
    
    # Draw text with shadow
    draw.text((tx + 2, ty + 2), bidi_txt, font=font, fill=(0, 0, 0, 200))
    draw.text((tx, ty), bidi_txt, font=font, fill=(255, 255, 255, 255), stroke_fill=(15, 20, 35, 255), stroke_width=3)
    
    if out_path:
        img.save(out_path)
    return img

def create_subtitle_card(text, out_path=None):
    w, h = 980, 180
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Rounded dark translucent card with warm golden border
    draw.rounded_rectangle([10, 10, w - 10, h - 10], radius=45, fill=(18, 22, 38, 220), outline=(255, 200, 50, 240), width=4)
    draw.rounded_rectangle([16, 16, w - 16, h - 16], radius=40, outline=(255, 255, 255, 50), width=1)
    
    # Add cute sparkles on the corners
    sp = draw_sparkle(48)
    img.paste(sp, (22, 22), sp)
    img.paste(sp, (w - 70, 22), sp)

    cleaned = clean_arabic_text(text)
    font = ImageFont.truetype(FONT_PATH, 44)
    reshaped = arabic_reshaper.reshape(cleaned)
    bidi_txt = get_display(reshaped)
    
    bbox = draw.textbbox((0, 0), bidi_txt, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    
    tx = (w - tw) // 2
    ty = (h - th) // 2 - 6
    
    # Shadow
    draw.text((tx + 3, ty + 3), bidi_txt, font=font, fill=(0, 0, 0, 200))
    # Main text in bright white/cream
    draw.text((tx, ty), bidi_txt, font=font, fill=(255, 255, 255, 255), stroke_fill=(10, 15, 25, 255), stroke_width=3)
    
    if out_path:
        img.save(out_path)
    return img

header_p = OUTPUT_DIR / "header_badge.png"
sub_p = OUTPUT_DIR / "sub_test.png"
star_p = OUTPUT_DIR / "star.png"

create_header_badge("حِكَايَاتُ العَجَائِب • بَرْنَامَجُ الأَخْلَاق", header_p)
create_subtitle_card("مَرْحَبًا يَا صِغَارِي! اللَّعِبُ لَذِيذ وَمُمْتِع", sub_p)
star_img = draw_kawaii_star(120)
star_img.save(star_p)

print("Generated graphic overlays successfully!")
