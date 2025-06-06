import os
import requests
from contants import FONT_CACHE

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

def print_with_google_font(printer, text, font_name="Roboto", font_style="", font_size=24, align="center"):
    """Print text using fonts with comprehensive fallback system"""
    from utils.helpers import render_text_image
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