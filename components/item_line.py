from PIL import Image, ImageDraw, ImageFont
import os
import textwrap
from utils.fonts import download_direct_font, get_system_font_fallback
from utils.helpers import contains_lao_text
from contants import PRINTER_WIDTH

def render_item_line(name, qty, price, total, font_size=18):
    """Render a properly aligned item line with columns"""
    # Determine font path
    font_path = None
    if contains_lao_text(name):
        font_path = download_direct_font("NotoSansLao")
    
    if not font_path:
        font_path = get_system_font_fallback()
    
    # Load font
    try:
        if font_path and os.path.exists(font_path):
            font = ImageFont.truetype(font_path, font_size)
        else:
            font = ImageFont.load_default()
    except:
        font = ImageFont.load_default()

    # Create image with proper dimensions
    img_height = int(font_size * 1.8)
    img = Image.new("1", (PRINTER_WIDTH, img_height), 1)  # White background
    draw = ImageDraw.Draw(img)
    
    # Format the line with proper spacing
    # Truncate name if too long
    display_name = textwrap.shorten(name, width=18)
    qty_str = f"{qty:>4.2f}" if isinstance(qty, float) else f"{qty:>4}"
    price_str = f"{price:>6.2f}"
    total_str = f"{total:>7.2f}"
    
    # Calculate positions for alignment (approximate column positions)
    name_x = 5
    qty_x = 280
    price_x = 380  
    total_x = 480
    
    # Draw each column
    draw.text((name_x, 2), display_name, font=font, fill=0)
    draw.text((qty_x, 2), qty_str, font=font, fill=0)
    draw.text((price_x, 2), price_str, font=font, fill=0)
    draw.text((total_x, 2), total_str, font=font, fill=0)
    
    return img
