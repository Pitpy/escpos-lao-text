from escpos.printer import Usb
from PIL import Image, ImageDraw, ImageFont
import requests
import os
import textwrap

# Configuration
FONT_CACHE = "font_cache"
PRINTER_WIDTH = 576  # 80mm paper (576 pixels)
PRINTER_DPI = 203    # Common thermal printer resolution

def download_font(font_url, font_name):
    """Download and cache Google Font - extracts TTF URL from CSS"""
    import re
    
    os.makedirs(FONT_CACHE, exist_ok=True)
    font_path = os.path.join(FONT_CACHE, f"{font_name}.ttf")
    
    if not os.path.exists(font_path):
        print(f"Downloading {font_name} from {font_url}...")
        try:
            # First, get the CSS file - use a user agent that requests TTF format
            headers = {
                'User-Agent': 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1)'  # Older browser to get TTF
            }
            response = requests.get(font_url, headers=headers, timeout=10)
            if response.status_code == 200:
                css_content = response.text
                
                # Extract TTF URL from CSS - updated pattern for Google Fonts
                ttf_pattern = r'src:\s*url\((https://fonts\.gstatic\.com[^)]+\.ttf)\)'
                ttf_match = re.search(ttf_pattern, css_content)
                
                if ttf_match:
                    ttf_url = ttf_match.group(1)
                    print(f"Found TTF URL: {ttf_url}")
                    
                    # Download the actual font file
                    ttf_response = requests.get(ttf_url, headers=headers, timeout=10)
                    if ttf_response.status_code == 200:
                        with open(font_path, "wb") as f:
                            f.write(ttf_response.content)
                        print(f"Successfully downloaded {font_name}")
                    else:
                        raise Exception(f"Failed to download TTF: HTTP {ttf_response.status_code}")
                else:
                    raise Exception("Could not find TTF URL in CSS response")
            else:
                raise Exception(f"Failed to download font CSS: HTTP {response.status_code}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Network error downloading font: {e}")
    else:
        print(f"Using cached font: {font_name}")
    return font_path

def get_system_font_fallback():
    """Get system font as fallback"""
    # macOS system fonts
    macos_fonts = [
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/Arial.ttf",
        "/Library/Fonts/Arial.ttf",
        "/System/Library/Fonts/Times.ttc"
    ]
    
    for font_path in macos_fonts:
        if os.path.exists(font_path):
            return font_path
    
    # If no system fonts found, return None (will use PIL default)
    return None

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

def download_direct_font(font_name="NotoSansLao"):
    """Download font directly from known URLs"""
    os.makedirs(FONT_CACHE, exist_ok=True)
    font_path = os.path.join(FONT_CACHE, f"{font_name}.ttf")
    
    if not os.path.exists(font_path):
        # Direct URLs for some popular fonts
        direct_urls = {
            "NotoSansLao": "https://raw.githubusercontent.com/google/fonts/main/ofl/notosanslao/NotoSansLao%5Bwdth%2Cwght%5D.ttf",
            "Roboto": "https://github.com/google/fonts/raw/main/apache/roboto/Roboto-Regular.ttf",
            "OpenSans": "https://github.com/google/fonts/raw/main/apache/opensans/OpenSans-Regular.ttf"
        }
        
        if font_name in direct_urls:
            try:
                print(f"Downloading {font_name} directly from GitHub...")
                response = requests.get(direct_urls[font_name], timeout=15)
                if response.status_code == 200:
                    with open(font_path, "wb") as f:
                        f.write(response.content)
                    print(f"Successfully downloaded {font_name}")
                    return font_path
                else:
                    print(f"Failed to download {font_name}: HTTP {response.status_code}")
            except Exception as e:
                print(f"Error downloading {font_name}: {e}")
    else:
        print(f"Using cached font: {font_name}")
        return font_path
    
    return None

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

def print_receipt():
    """Example receipt using font detection for all text"""
    printer = None
    try:
        # Initialize printer (your specific device)
        printer = Usb(0x1fc9, 0x2016, in_ep=0x82, out_ep=0x01)
        
        # Print header with image rendering
        print_image_text(printer, "SUPERMARKET XYZ", font_size=36, align="center")
        print_image_text(printer, "Tel: (555) 123-4567", font_size=18, align="center")
        print_image_text(printer, "2025-03-15 14:30", font_size=18, align="center")
        
        # Add spacing
        printer.text("\n")
        
        # Print table header as image for consistency
        header_image = render_receipt_line("-" * 80, font_size=26)
        printer.image(header_image, impl="bitImageRaster")
        
        table_header_image = render_table_header(font_size=22)
        printer.image(table_header_image, impl="bitImageRaster")
        
        separator_image = render_receipt_line("-" * 80, font_size=26)
        printer.image(separator_image, impl="bitImageRaster")
        
        # Example items
        items = [
            ("ເບຍລາວ", 1, 4.99),
            ("Whole Milk", 2, 3.49),
            ("Eggs (12ct)", 1, 5.99),
            ("Coffee Beans", 1, 12.99),
            ("Bananas", 0.54, 0.79),
        ]
        
        # Print each item using unified image rendering for perfect alignment
        for name, qty, price in items:
            line_total = qty * price
            
            # Render entire line as image for consistent formatting
            item_image = render_item_line(name, qty, price, line_total, font_size=20)
            printer.image(item_image, impl="bitImageRaster", high_density_vertical=True, high_density_horizontal=True)
        
        # Calculate total
        subtotal = sum(qty * price for _, qty, price in items)
        tax = subtotal * 0.0825
        total = subtotal + tax
        
        # Print totals as images for consistency
        separator_image = render_receipt_line("-" * 80, font_size=26)
        printer.image(separator_image, impl="bitImageRaster")
        
        subtotal_image = render_total_line("SUBTOTAL:", subtotal, font_size=22)
        printer.image(subtotal_image, impl="bitImageRaster")

        tax_image = render_total_line("TAX:", tax, font_size=22)
        printer.image(tax_image, impl="bitImageRaster")
        
        total_image = render_total_line("TOTAL:", total, font_size=24)
        printer.image(total_image, impl="bitImageRaster")
        
        # Add spacing
        printer.text("\n")
        
        # Footer with image rendering
        print_image_text(printer, "Thank you for your purchase!", font_size=20, align="center")
        print_image_text(printer, "Returns within 14 days", font_size=16, align="center")
        
        # Finalize
        printer.cut()
        return True
    except Exception as e:
        print(f"Printer error: {e}")
    finally:
        try:
            if printer is not None:
                printer.close()
        except:
            pass

if __name__ == "__main__":
    print("Starting receipt printing...")
    if print_receipt():
        print("Receipt printed successfully!")
    else:
        print("Failed to print receipt")