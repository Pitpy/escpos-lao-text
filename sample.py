from escpos.printer import Usb
from utils.helpers import print_image_text
from components import (
    render_receipt_line,
    render_item_line,
    render_table_header,
    render_total_line
)

def print_receipt():
    """Example receipt using font detection for all text"""
    printer = None
    try:
        # Initialize printer (your specific device)
        printer = Usb(0x1fc9, 0x2016, in_ep=0x82, out_ep=0x01)
        
        # Print header with image rendering
        print_image_text(printer, "P2G Shop", font_size=36, align="center")
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
        
        # Example items with properly positioned Lao text
        items = [
            ("ແກງຈືດໝູຕົ້ມ", 0, 0.00),
            ("ເບຍລາວ", 1, 4.99),        # Beer Lao
            ("ນົມສົດ", 2, 3.49),         # Fresh milk (ນ + ົ + ມ + ສ + ົ + ດ)
            ("ໄຂ່ໄກ່ (12 ໜ່ວຍ)", 1, 5.99),  # Chicken eggs (ໄ + ຂ + ່ + ໄ + ກ + ່)
            ("ກາເຟ", 1, 12.99),         # Coffee
            ("ກ້ວຍ", 0.54, 0.79),        # Banana (ກ + ້ + ວ + ຍ)
            ("ຂອງກິນ", 3, 2.50),        # Snacks (ຂ + ອ + ງ + ກ + ິ + ນ)
            ("ຂອງດື່ມ", 2, 1.75),        # Drinks (ຂ + ອ + ງ + ດ + ື + ມ)
            ("ຂອງໃສ່ລາວແລະນົມສົດແລະເບຍແລະນ້ຳ", 1, 0.99), # Fresh Lao accessories, milk, beer and water (ຂ + ອ + ງ + ໃ + ສ + ິ + ຈ + ລ + ຳ + ແ + ລ + ະ + ນ + ສ + ໍ + ດ + ແ + ລ + ະ + ແ + ລ)
            ("ກູກິ້ວ", 1, 3.00),         # Noodles (ກ + ູ + ກ + ິ + ວ)
        ]
        
        # Print each item using unified image rendering for perfect alignment
        for name, qty, price in items:
            line_total = qty * price
            
            # Render entire line as image for consistent formatting
            item_image = render_item_line(name, qty, price, line_total, font_size=22)
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