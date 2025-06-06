import os
from utils.fonts import get_system_font_fallback, download_direct_font
from PIL import Image, ImageDraw, ImageFont
import contants

PRINTER_WIDTH = contants.PRINTER_WIDTH
FONT_CACHE = contants.FONT_CACHE

def render_text_image(text, font_path, font_size=24, align="center", max_width_pixels=PRINTER_WIDTH):
    """Render text as printer-compatible raster image"""
    # Load font
    try:
        if font_path and os.path.exists(font_path):
            font = ImageFont.truetype(font_path, font_size)
        else:
            # Try system font fallback
            system_font = get_system_font_fallback()
            if system_font:
                font = ImageFont.truetype(system_font, font_size)
            else:
                # Use PIL default font
                font = ImageFont.load_default()
                print("Using PIL default font as fallback")
    except IOError as e:
        print(f"Font loading error: {e}")
        # Try system font fallback
        system_font = get_system_font_fallback()
        if system_font:
            try:
                font = ImageFont.truetype(system_font, font_size)
                print(f"Using system font fallback: {system_font}")
            except:
                font = ImageFont.load_default()
                print("Using PIL default font as final fallback")
        else:
            font = ImageFont.load_default()
            print("Using PIL default font as fallback")

    # Create drawing context
    dummy_img = Image.new("L", (1, 1), 255)
    dummy_draw = ImageDraw.Draw(dummy_img)
    
    # Calculate text dimensions
    bbox = dummy_draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # Create image with proper dimensions
    img_width = min(max_width_pixels, int(text_width * 1.1))
    img_height = int(text_height * 1.5)
    img = Image.new("1", (img_width, img_height), 1)  # 1-bit image (white background)
    draw = ImageDraw.Draw(img)
    
    # Calculate position
    x = 0
    if align == "center":
        x = (img_width - text_width) // 2
    elif align == "right":
        x = img_width - text_width
    
    # Draw text (black on white)
    draw.text((x, 0), text, font=font, fill=0)
    
    # Convert to printer-compatible format
    return img

def contains_lao_text(text):
    """Check if text contains Lao characters"""
    # Lao Unicode range: U+0E80 to U+0EFF
    for char in text:
        if '\u0E80' <= char <= '\u0EFF':
            return True
    return False

def print_text_with_font_detection(printer, text, font_size=24, align="center", newline=True):
    """Print text using appropriate font based on content"""
    if contains_lao_text(text):
        # Use Lao font for text containing Lao characters
        print_with_google_font(
            printer, 
            text, 
            font_name="Noto Sans Lao", 
            font_style="", 
            font_size=font_size, 
            align=align
        )
    else:
        # Use regular printer text for Latin characters
        align_value = align.lower()
        if align_value not in ["center", "left", "right"]:
            align_value = "center"
        
        printer.set(align=align_value, width=2 if font_size > 30 else 1, height=2 if font_size > 30 else 1)
        if newline:
            printer.text(text + "\n")
        else:
            printer.text(text)
        printer.set()  # Reset formatting

def print_with_google_font(printer, text, font_name="Roboto", font_style="", font_size=24, align="center"):
    """Print text using fonts with comprehensive fallback system"""
    font_path = None
    
    try:
        # Step 1: Try direct download for specific fonts first
        if "noto" in font_name.lower() and "lao" in font_name.lower():
            font_path = download_direct_font("NotoSansLao")
            if font_path:
                print(f"Using downloaded Noto Sans Lao: {font_path}")
            else:
                print("Noto Sans Lao download failed, falling back to system font")
                font_path = get_system_font_fallback()
        
        # Step 2: Try system fonts for other requests (fastest and most reliable)
        elif font_name.lower() in ["roboto", "arial", "helvetica"] or not font_path:
            system_font = get_system_font_fallback()
            if system_font:
                font_path = system_font
                print(f"Using system font: {system_font}")
        
        # Step 3: Use cached Roboto if available
        elif os.path.exists(os.path.join(FONT_CACHE, "Roboto-Bold.ttf")):
            font_path = os.path.join(FONT_CACHE, "Roboto-Bold.ttf")
            print("Using cached Roboto font")
        
        # Step 4: Final fallback to system font
        else:
            font_path = get_system_font_fallback()
            print("Using system font as final fallback")
        
        # Render and print the text as image
        if font_path:
            print(f"Rendering text with font: {font_path}")
            text_image = render_text_image(text, font_path, font_size, align)
            
            # Print image to thermal printer
            printer.image(text_image, impl="bitImageRaster", high_density_vertical=True, high_density_horizontal=True)
            print(f"Successfully printed image text: '{text}'")
            return True
        else:
            raise Exception("No font available")
            
    except Exception as e:
        print(f"Font rendering failed: {e}")
        # Fallback to standard thermal printer text
        try:
            align_value = align.lower()
            if align_value not in ["center", "left", "right"]:
                align_value = "center"
                
            printer.set(align=align_value, width=2 if font_size > 30 else 1, height=2 if font_size > 30 else 1)
            printer.text(text + "\n")
            printer.set()  # Reset formatting
            print(f"Used fallback printer text: '{text}'")
            return False
        except Exception as fallback_error:
            print(f"Even fallback printing failed: {fallback_error}")
            return False
        
def print_image_text(printer, text, font_size=18, align="center", font_path=None):
    """Print any text as image for consistent formatting"""
    try:
        if font_path is None:
            if contains_lao_text(text):
                font_path = download_direct_font("NotoSansLao")
            else:
                font_path = get_system_font_fallback()
        
        text_image = render_text_image(text, font_path, font_size, align)
        printer.image(text_image, impl="bitImageRaster", high_density_vertical=True, high_density_horizontal=True)
        return True
    except Exception as e:
        print(f"Image text rendering failed: {e}")
        # Fallback to regular text
        printer.text(text + "\n")
        return False