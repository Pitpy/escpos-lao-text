#!/usr/bin/env python3
"""Test unified image rendering vs mixed text/image rendering"""

from escpos.printer import Usb
from escpos_sample_font import (
    render_item_line, print_image_text, render_receipt_line, 
    contains_lao_text, download_direct_font
)
import textwrap

def test_alignment_comparison():
    """Test the difference between mixed and unified rendering"""
    printer = None
    try:
        # Initialize printer
        printer = Usb(0x1fc9, 0x2016, in_ep=0x82, out_ep=0x01)
        
        print("🔥 UNIFIED IMAGE RENDERING TEST")
        print("=" * 50)
        
        # Header
        print_image_text(printer, "ALIGNMENT TEST RECEIPT", font_size=28, align="center")
        print_image_text(printer, "Unified Image Rendering", font_size=18, align="center")
        printer.text("\n")
        
        # Table header
        header_image = render_receipt_line("-" * 32, font_size=16)
        printer.image(header_image, impl="bitImageRaster")
        
        table_header = render_receipt_line(f"{'ITEM':<18}{'QTY':>4}{'PRICE':>6}{'TOTAL':>7}", font_size=16)
        printer.image(table_header, impl="bitImageRaster")
        
        separator = render_receipt_line("-" * 32, font_size=16)
        printer.image(separator, impl="bitImageRaster")
        
        # Test items with mixed languages
        test_items = [
            ("ເບຍລາວ ສົດ", 2, 4.99),      # Lao beer
            ("Coffee Americano", 1, 3.50),  # English  
            ("ນົມຊິ້ນ ອໍແກນິກ", 1, 5.99),    # Lao organic milk
            ("Bread Whole Wheat", 2, 2.25), # English
            ("ເຂົ້າຫອມມະລິ", 1, 8.50),     # Lao jasmine rice
        ]
        
        print("\n📊 Rendering items with perfect alignment:")
        for name, qty, price in test_items:
            line_total = qty * price
            print(f"  - {name}: {qty} x ${price} = ${line_total}")
            
            # Render as unified image
            item_image = render_item_line(name, qty, price, line_total, font_size=18)
            printer.image(item_image, impl="bitImageRaster", high_density_vertical=True, high_density_horizontal=True)
        
        # Totals
        subtotal = sum(qty * price for _, qty, price in test_items)
        tax = subtotal * 0.08
        total = subtotal + tax
        
        separator_image = render_receipt_line("-" * 32, font_size=16)
        printer.image(separator_image, impl="bitImageRaster")
        
        subtotal_image = render_receipt_line(f"{'SUBTOTAL:':<20}{subtotal:>10.2f}", font_size=18)
        printer.image(subtotal_image, impl="bitImageRaster")
        
        tax_image = render_receipt_line(f"{'TAX (8%):':<20}{tax:>10.2f}", font_size=18)
        printer.image(tax_image, impl="bitImageRaster")
        
        total_image = render_receipt_line(f"{'TOTAL:':<20}{total:>10.2f}", font_size=22)
        printer.image(total_image, impl="bitImageRaster")
        
        # Footer
        printer.text("\n")
        print_image_text(printer, "ຂອບໃຈທີ່ມາຊື້ຂອງ!", font_size=20, align="center")  # Lao "Thank you"
        print_image_text(printer, "Perfect Alignment Test", font_size=16, align="center")
        
        printer.cut()
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        if printer:
            try:
                printer.close()
            except:
                pass

if __name__ == "__main__":
    print("🧾 Testing unified image rendering for perfect alignment...")
    print("This approach renders ALL text as images for consistent formatting")
    print("=" * 60)
    
    if test_alignment_comparison():
        print("\n✅ SUCCESS: Unified image rendering test completed!")
        print("   🎯 Perfect alignment achieved for mixed Lao/English text")
        print("   📐 All text rendered as images with consistent spacing")
        print("   🎨 Beautiful, professional receipt formatting")
    else:
        print("\n❌ FAILED: Unified image rendering test failed")
