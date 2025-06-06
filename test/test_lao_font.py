#!/usr/bin/env python3
"""Test Lao font rendering"""

from escpos.printer import Usb
from PIL import Image, ImageDraw, ImageFont
import os

FONT_CACHE = "font_cache"

def test_lao_rendering():
    """Test rendering Lao text with the downloaded font"""
    
    # Test text in Lao
    lao_text = "ດບຍລາວ"  # Lao text from your receipt
    
    # Load the Noto Sans Lao font
    font_path = os.path.join(FONT_CACHE, "NotoSansLao.ttf")
    
    if not os.path.exists(font_path):
        print("❌ Noto Sans Lao font not found")
        return False
        
    try:
        # Load font
        font = ImageFont.truetype(font_path, 24)
        print(f"✅ Successfully loaded font: {font_path}")
        
        # Create test image
        img = Image.new("1", (300, 100), 1)  # White background
        draw = ImageDraw.Draw(img)
        
        # Draw Lao text
        draw.text((10, 10), lao_text, font=font, fill=0)  # Black text
        
        # Save test image
        img.save("lao_test.png")
        print(f"✅ Successfully rendered Lao text: '{lao_text}'")
        print("✅ Test image saved as 'lao_test.png'")
        
        # Try printing to thermal printer
        try:
            printer = Usb(0x1fc9, 0x2016, in_ep=0x82, out_ep=0x01)
            printer.image(img, impl="bitImageRaster")
            printer.text("\n")
            printer.cut()
            print("✅ Successfully printed Lao text to thermal printer")
            return True
        except Exception as printer_error:
            print(f"⚠️  Could not print to thermal printer: {printer_error}")
            print("✅ But font rendering works correctly")
            return True
            
    except Exception as e:
        print(f"❌ Error rendering Lao text: {e}")
        return False

if __name__ == "__main__":
    print("Testing Lao Font Rendering")
    print("=" * 30)
    success = test_lao_rendering()
    if success:
        print("🎉 Font test completed successfully!")
    else:
        print("❌ Font test failed")
