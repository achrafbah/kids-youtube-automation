import os
import sys
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import arabic_reshaper
from bidi.algorithm import get_display
import imageio_ffmpeg

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "output" / "test_effects"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

FONT_PATH = "C:\\Windows\\Fonts\\arial.ttf"

def create_header_badge(title_text="حِكَايَاتُ العَجَائِب ✨ بَرْنَامَجُ الأَخْلَاق", out_path=None):
    w, h = 920, 110
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Rounded badge background: pastel soft purple-blue gradient
    draw.rounded_rectangle([10, 10, w - 10, h - 10], radius=40, fill=(35, 45, 80, 225), outline=(255, 215, 0, 255), width=3)
    
    font = ImageFont.truetype(FONT_PATH, 42)
    reshaped = arabic_reshaper.reshape(title_text)
    bidi_txt = get_display(reshaped)
    
    bbox = draw.textbbox((0, 0), bidi_txt, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    
    tx = (w - tw) // 2
    ty = (h - th) // 2 - 5
    
    # Draw text with gold glow
    draw.text((tx, ty), bidi_txt, font=font, fill=(255, 255, 255, 255), stroke_fill=(15, 20, 35, 255), stroke_width=3)
    
    if out_path:
        img.save(out_path)
    return img

def create_subtitle_card(text, emoji="✨", out_path=None):
    w, h = 980, 180
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Rounded dark translucent card with warm golden border
    draw.rounded_rectangle([10, 10, w - 10, h - 10], radius=45, fill=(18, 22, 38, 220), outline=(255, 200, 50, 240), width=4)
    
    # Inner subtle glow
    draw.rounded_rectangle([16, 16, w - 16, h - 16], radius=40, outline=(255, 255, 255, 50), width=1)
    
    # Arabic text
    font = ImageFont.truetype(FONT_PATH, 46)
    full_text = f"{emoji} {text}" if emoji else text
    reshaped = arabic_reshaper.reshape(full_text)
    bidi_txt = get_display(reshaped)
    
    bbox = draw.textbbox((0, 0), bidi_txt, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    
    tx = (w - tw) // 2
    ty = (h - th) // 2 - 8
    
    # Shadow
    draw.text((tx + 3, ty + 3), bidi_txt, font=font, fill=(0, 0, 0, 180))
    # Main text in bright white/cream
    draw.text((tx, ty), bidi_txt, font=font, fill=(255, 255, 255, 255), stroke_fill=(10, 15, 25, 255), stroke_width=3)
    
    if out_path:
        img.save(out_path)
    return img

def create_floating_star(out_path=None):
    # Cute yellow star with sparkles
    w, h = 120, 120
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(FONT_PATH, 80)
    draw.text((15, 10), "⭐", font=font)
    if out_path:
        img.save(out_path)
    return img

header_p = OUTPUT_DIR / "header_badge.png"
sub_p = OUTPUT_DIR / "sub_test.png"
star_p = OUTPUT_DIR / "star.png"

create_header_badge("حِكَايَاتُ العَجَائِب 🌟 بَرْنَامَجُ الأَخْلَاق", header_p)
create_subtitle_card("مَرْحَبًا يَا صِغَارِي! اللَّعِبُ لَذِيذ 🧸", "✨", sub_p)
create_floating_star(star_p)

print("Generated graphic overlays successfully!")
