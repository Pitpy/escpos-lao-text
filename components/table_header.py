from PIL import Image, ImageDraw, ImageFont
import os
from utils.fonts import get_system_font_fallback
from contants import PRINTER_WIDTH

def render_table_header(font_size=16):
    """Render table header with proper column alignment"""
    font_path = get_system_font_fallback()
    
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
    
    # Use same column positions as render_item_line
    name_x = 5
    qty_x = 280
    price_x = 380  
    total_x = 480
    
    # Draw column headers
    draw.text((name_x, 2), "ITEM", font=font, fill=0)
    draw.text((qty_x, 2), "QTY", font=font, fill=0)
    draw.text((price_x, 2), "PRICE", font=font, fill=0)
    draw.text((total_x, 2), "TOTAL", font=font, fill=0)
    
    return img