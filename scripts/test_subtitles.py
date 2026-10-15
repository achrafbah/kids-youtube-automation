import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import arabic_reshaper
from bidi.algorithm import get_display

# Windows font
FONT_PATH = "C:\\Windows\\Fonts\\arial.ttf"

def render_arabic_text(text: str, font_size: int = 56, text_color=(255, 255, 255), stroke_color=(20, 20, 20), stroke_width=4):
    reshaped_text = arabic_reshaper.reshape(text)
    bidi_text = get_display(reshaped_text)
    
    font = ImageFont.truetype(FONT_PATH, font_size)
    
    # Calculate bounding box
    dummy_img = Image.new("RGBA", (1, 1))
    draw = ImageDraw.Draw(dummy_img)
    bbox = draw.textbbox((0, 0), bidi_text, font=font, stroke_width=stroke_width)
    w = bbox[2] - bbox[0] + 40
    h = bbox[3] - bbox[1] + 30
    
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.text((20, 15), bidi_text, font=font, fill=text_color, stroke_fill=stroke_color, stroke_width=stroke_width)
    return img

test_phrase = "مَرْحَبًا يَا صِغَارِي! اللَّعِبُ لَذِيذ 🧸"
img = render_arabic_text(test_phrase)
out_path = Path("output/test_subtitle_render.png")
out_path.parent.mkdir(parents=True, exist_ok=True)
img.save(out_path)
print(f"Subtitle test image saved to: {out_path.resolve()}, size: {img.size}")
