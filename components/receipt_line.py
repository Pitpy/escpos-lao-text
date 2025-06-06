from PIL import Image, ImageDraw, ImageFont
import os
from utils.fonts import download_direct_font, get_system_font_fallback
from utils.helpers import contains_lao_text
from contants import PRINTER_WIDTH

def render_receipt_line(text, font_path=None, font_size=18, max_width_pixels=PRINTER_WIDTH):
    """Render a complete receipt line as image with perfect alignment"""
    # Choose appropriate font
    if font_path is None:
        if contains_lao_text(text):
            font_path = download_direct_font("NotoSansLao")
        
        if not font_path:
            font_path = get_system_font_fallback()
    
    # Load font
    try:
        if font_path and os.path.exists(font_path):
            font = ImageFont.truetype(font_path, font_size)
        else:
            font = ImageFont.load_default()
            print("Using PIL default font")
    except:
        font = ImageFont.load_default()
        print("Font load failed, using default")

    # Create image
    img_height = int(font_size * 1.8)  # Extra height for proper spacing
    img = Image.new("1", (max_width_pixels, img_height), 1)  # White background
    draw = ImageDraw.Draw(img)
    
    # Draw text (black on white)
    draw.text((5, 2), text, font=font, fill=0)  # Small left margin
    
    return img