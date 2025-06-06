#!/usr/bin/env python3
"""Test comprehensive Lao font integration with multiple Lao items"""

from escpos.printer import Usb
from sample import print_text_with_font_detection, contains_lao_text
import textwrap

def print_multilingual_receipt():
    """Print a receipt with multiple Lao items to test font detection"""
    printer = None
    try:
        # Initialize printer
        printer = Usb(0x1fc9, 0x2016, in_ep=0x82, out_ep=0x01)
        
        # Header
        print_text_with_font_detection(
            printer,
            "ໂລຊກ ສຸ່ປເມັກກີ",  # Lao supermarket name
            font_size=32,
            align="center"
        )
        
        print_text_with_font_detection(
            printer, 
            "Multilingual Store", 
            font_size=24, 
            align="center"
        )

        # Store info
        print_text_with_font_detection(printer, "Tel: (555) 123-4567", font_size=16, align="center")
        print_text_with_font_detection(printer, "2025-03-15 14:30", font_size=16, align="center")
        printer.text("\n")
        
        # Items header
        printer.set(align="left")
        printer.text("-" * 32 + "\n")
        printer.text(f"{'ITEM':<22}{'QTY':>4}{'PRICE':>6}\n")
        printer.text("-" * 32 + "\n")
        
        # Mixed language items
        items = [
            ("ດບຍລາວ", 2, 4.99),        # Lao tea
            ("ນົມຊິ້ນ", 1, 3.49),         # Lao milk  
            ("Coffee ກະເພ", 1, 8.99),    # Mixed
            ("Bananas", 0.5, 1.99),      # English
            ("ເຂົ້າຈື້", 3, 2.50),        # Lao rice
            ("Bread", 1, 2.99),          # English
        ]
        
        total_amount = 0
        
        for name, qty, price in items:
            line_total = qty * price
            total_amount += line_total
            
            if contains_lao_text(name):
                print(f"🔤 Lao text detected: '{name}'")
                print_text_with_font_detection(printer, name, font_size=18, align="left")
                # Print quantity and price on same line
                printer.set(align="right")  
                printer.text(f"{qty:>4.1f} {price:>6.2f} {line_total:>7.2f}\n")
                printer.set()
            else:
                print(f"🔡 English text: '{name}'")
                # Standard printer formatting for English
                printer.text(f"{textwrap.shorten(name, width=22):<22}")
                printer.text(f"{qty:>4.1f}" if isinstance(qty, float) else f"{qty:>4}")
                printer.text(f"{price:>6.2f}")
                printer.text(f"{line_total:>7.2f}\n")
        
        # Totals
        tax = total_amount * 0.08
        final_total = total_amount + tax
        
        printer.text("-" * 32 + "\n")
        printer.set(align="right")
        printer.text(f"SUBTOTAL: {total_amount:.2f}\n")
        printer.text(f"TAX (8%): {tax:.2f}\n")
        printer.set(width=2, height=2)
        printer.text(f"TOTAL: {final_total:.2f}\n\n")
        printer.set()
        
        # Footer in Lao
        print_text_with_font_detection(
            printer, 
            "ຂອບໃຈທີ່ຊື້ຂອງ!", 
            font_size=20, 
            align="center"
        )
        print_text_with_font_detection(
            printer, 
            "Thank you for shopping!", 
            font_size=18, 
            align="center"
        )
        
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
    print("🧾 Testing multilingual receipt with Lao font detection...")
    print("=" * 50)
    
    if print_multilingual_receipt():
        print("✅ Multilingual receipt printed successfully!")
        print("   - Lao text used Noto Sans Lao font")  
        print("   - English text used thermal printer font")
        print("   - Mixed text handled appropriately")
    else:
        print("❌ Failed to print multilingual receipt")
