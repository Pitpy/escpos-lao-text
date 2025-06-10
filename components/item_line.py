from PIL import Image, ImageDraw, ImageFont
import os
import textwrap
import unicodedata
from utils.fonts import download_direct_font, get_system_font_fallback
from utils.helpers import contains_lao_text
from contants import PRINTER_WIDTH

def render_item_line(name, qty, price, total, font_size=18):
    """Render a properly aligned item line with columns and correct Lao text positioning"""
    # Normalize Lao text for proper character positioning
    normalized_name = unicodedata.normalize('NFC', name) if contains_lao_text(name) else name
    
    # Determine font path
    font_path = None
    if contains_lao_text(normalized_name):
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
    # For Lao text, use careful character-by-character rendering for better positioning
    if contains_lao_text(normalized_name):
        display_name = render_lao_text_properly(normalized_name, font, max_width=25)
    else:
        display_name = textwrap.shorten(normalized_name, width=18)
    
    qty_str = f"{qty:>4.2f}" if isinstance(qty, float) else f"{qty:>4}"
    price_str = f"{price:>6.2f}"
    total_str = f"{total:>7.2f}"
    
    # Calculate positions for alignment (approximate column positions)
    name_x = 5
    qty_x = 280
    price_x = 380  
    total_x = 480
    
    # Draw each column - use special rendering for Lao text
    if contains_lao_text(normalized_name):
        draw_lao_text_positioned(draw, (name_x, 2), display_name, font)
    else:
        draw.text((name_x, 2), display_name, font=font, fill=0)
    
    draw.text((qty_x, 2), qty_str, font=font, fill=0)
    draw.text((price_x, 2), price_str, font=font, fill=0)
    draw.text((total_x, 2), total_str, font=font, fill=0)
    
    return img

def render_lao_text_properly(text, font, max_width=25):
    """Properly truncate Lao text while preserving character integrity"""
    if len(text) <= max_width:
        return text
    
    # For Lao text, be more careful about truncation
    # Don't break in the middle of base+combining character pairs
    truncated = ""
    char_count = 0
    
    i = 0
    while i < len(text) and char_count < max_width:
        char = text[i]
        
        # Check if this is a base character followed by combining characters
        if i < len(text) - 1 and unicodedata.category(text[i + 1]) == 'Mn':
            # Include the base character and all following combining characters
            base_group = char
            i += 1
            while i < len(text) and unicodedata.category(text[i]) == 'Mn':
                base_group += text[i]
                i += 1
            
            # Check if adding this group would exceed max width
            if char_count + len(base_group) <= max_width:
                truncated += base_group
                char_count += len(base_group)
            else:
                break
        else:
            # Regular character
            truncated += char
            char_count += 1
            i += 1
    
    # Add ellipsis if truncated
    if char_count < len(text):
        truncated += "..."
    
    return truncated

def draw_lao_text_positioned(draw, position, text, font):
    """Draw Lao text with proper combining character positioning and vertical stacking"""
    x, y = position
    
    # Track positions: current_x for next character, last_base_x for combining characters
    current_x = x
    last_base_x = x  # Position of the last base character
    last_base_y = y  # Y position for combining characters
    vowel_positioned = False  # Track if a vowel mark was positioned on current base
    
    i = 0
    while i < len(text):
        char = text[i]
        
        # Check if this character is a combining/nonspacing mark
        # For Lao, check category 'Mn' (Mark, nonspacing) instead of combining class
        category = unicodedata.category(char)
        is_combining = category == 'Mn'  # Mark, nonspacing
        
        if is_combining:
            # Combining character - position it over the last base character with proper stacking
            
            # Different positioning for different types of combining characters
            name = unicodedata.name(char, "")
            combining_class = unicodedata.combining(char)
            
            if "TONE" in name or combining_class == 122:
                # Tone marks (່ ้ ໊ ໋) - position above vowel marks if present
                offset_x = last_base_x + 8  # Center-aligned horizontally
                if vowel_positioned:
                    # If vowel mark already positioned, put tone mark above it
                    offset_y = last_base_y - 8  # Above the vowel mark
                else:
                    # No vowel mark, position normally above base
                    offset_y = last_base_y - 2  # Slightly above base
            elif "VOWEL" in name and combining_class == 0:
                # Vowel marks (ົ ັ ິ ີ) - center alignment above base
                offset_x = last_base_x + 2  # Slightly offset for better visibility
                offset_y = last_base_y - 1  # Same level as base
                vowel_positioned = True  # Mark that vowel is positioned
            elif combining_class == 118:
                # Below vowel marks (ຸ ູ) - center below base
                offset_x = last_base_x + 4
                offset_y = last_base_y  # Below the base character
            else:
                # Default positioning
                offset_x = last_base_x
                offset_y = last_base_y
            
            draw.text((offset_x, offset_y), char, font=font, fill=0)
            # Don't advance current_x for combining characters
        else:
            # Base character - render at current position and advance
            draw.text((current_x, y), char, font=font, fill=0)
            last_base_x = current_x  # Remember this base position for combining characters
            last_base_y = y  # Remember Y position
            vowel_positioned = False  # Reset vowel positioning flag for new base
            
            # Calculate character width for next position
            try:
                bbox = draw.textbbox((0, 0), char, font=font)
                char_width = bbox[2] - bbox[0]
                current_x += max(char_width, 6)  # Advance to next position
            except:
                current_x += 10  # Fallback spacing
        
        i += 1
