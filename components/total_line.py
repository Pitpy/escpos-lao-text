from PIL import Image, ImageDraw, ImageFont
import os
from utils.fonts import get_system_font_fallback
from contants import PRINTER_WIDTH

def render_total_line(label, amount, font_size=18, bold=False):
    """Render total line with proper right alignment"""
    font_path = get_system_font_fallback()
    
    try:
        if font_path and os.path.exists(font_path):
            font = ImageFont.truetype(font_path, font_size)
        else:
            font = ImageFont.load_default()
    except:
        font = ImageFont.load_default()

    # Create image
    img_height = int(font_size * 1.8)
    img = Image.new("1", (PRINTER_WIDTH, img_height), 1)  # White background
    draw = ImageDraw.Draw(img)
    
    # Right-align the total (use right side of paper width)
    label_text = f"{label}"
    amount_text = f"{amount:.2f}"
    
    # Position label on left side and amount on right side
    label_x = 300  # Move label more to the right
    amount_x = 480  # Align with total column from items
    
    draw.text((label_x, 2), label_text, font=font, fill=0)
    draw.text((amount_x, 2), amount_text, font=font, fill=0)
    
    return img