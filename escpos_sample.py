from rich.console import Console
from rich.table import Table
from rich import box
import textwrap
from escpos.printer import Usb

# Sample data
store_info = {
    "name": "SUPERMARKET XYZ",
    "address": "123 Main St, Cityville, ST 12345",
    "phone": "Tel: (555) 123-4567",
    "date": "2025-03-15 14:30:22"
}

items = [
    {"name": "Organic Whole Wheat Bread", "price": 4.99, "quantity": 1},
    {"name": "Premium Whole Milk 1 Gallon", "price": 3.49, "quantity": 2},
    {"name": "Large Free-Range Eggs (12ct)", "price": 5.99, "quantity": 1},
    {"name": "Colombian Coffee Beans 1lb", "price": 12.99, "quantity": 1},
    {"name": "Organic Bananas per lb", "price": 0.79, "quantity": 2.54},
    {"name": "ເບຍລາວ", "price": 1.50, "quantity": 3},
    {"name": "ຂອງຫວານລາວ", "price": 2.00, "quantity": 1},
    {"name": "ຂອງຫວານລາວ ບໍ່ເປັນຂີ້", "price": 1.00, "quantity": 2},
]

tax_rate = 0.0825

# 1. Rich Console Preview
def rich_preview(store_info, items, tax_rate):
    console = Console(width=48)
    subtotal = sum(item["price"] * item["quantity"] for item in items)
    tax = subtotal * tax_rate
    total = subtotal + tax

    console.print(f"\n[bold reverse]{' RECEIPT PREVIEW ':-^48}[/bold reverse]\n")
    console.print(f"[bold][center]{store_info['name']}[/center][/bold]")
    console.print(f"[center]{store_info['address']}[/center]")
    console.print(f"[center]{store_info['phone']}[/center]")
    console.print(f"[center]{store_info['date']}[/center]")
    console.print("─" * 48)

    table = Table(box=box.SIMPLE, padding=(0,1,0,0), show_header=True)
    table.add_column("Item", width=28)
    table.add_column("Price", justify="right")
    table.add_column("Qty", justify="center")
    table.add_column("Total", justify="right")

    for item in items:
        total_price = item["price"] * item["quantity"]
        table.add_row(
            textwrap.shorten(item["name"], width=28, placeholder="..."),
            f"${item['price']:.2f}",
            f"{item['quantity']:.2f}" if isinstance(item['quantity'], float) else str(item['quantity']),
            f"${total_price:.2f}"
        )
    
    console.print(table)
    console.print("─" * 48)
    console.print(f"SUBTOTAL: [bold]${subtotal:.2f}[/bold]", justify="right")
    console.print(f"TAX ({tax_rate*100:.2f}%): [bold]${tax:.2f}[/bold]", justify="right")
    console.print(f"TOTAL: [bold yellow]${total:.2f}[/bold yellow]", justify="right")
    console.print("\n[bold]Payment:[/bold] Visa ****1234")
    console.print(f"[bold]Change Due:[/bold] ${0.00:.2f}")
    console.print("\n[italic center]Thank you for shopping with us![/italic center]")
    console.print("[center]Returns within 14 days with receipt[/center]")

# 2. ESC/POS Thermal Printer Function
def print_receipt(store_info, items, tax_rate):
    try:
        # Configure for your printer (found with system_profiler/lsusb)
        # NXP Semiconductors USB Printer Port (POS-80)
        # Endpoints: IN=0x82, OUT=0x01
        printer = Usb(idVendor=0x1fc9, idProduct=0x2016, in_ep=0x82, out_ep=0x01)

        # Printer setup
        printer.set(align='center', width=2, height=2)
        printer.text(f"{store_info['name']}\n")
        printer.set(align='center', width=1, height=1)
        printer.text(f"{store_info['address']}\n")
        printer.text(f"{store_info['phone']}\n")
        printer.text(f"{store_info['date']}\n\n")
        
        # Print items
        printer.set(align='left')
        printer.text("-" * 48 + "\n")
        printer.text(f"{'Item':<28}{'Price':>7}{'Qty':>7}{'Total':>8}\n")
        printer.text("-" * 48 + "\n")
        
        for item in items:
            # Wrap long item names
            name_lines = textwrap.wrap(item["name"], width=28)
            for i, line in enumerate(name_lines):
                if i == 0:
                    printer.text(f"{line:<28}")
                else:
                    printer.text(f"{' ':<28}")  # Indent wrapped lines
                    
                if i == 0:
                    # Only show price/qty/total on first line
                    qty = f"{item['quantity']:.2f}" if isinstance(item['quantity'], float) else str(item['quantity'])
                    total = f"${item['price'] * item['quantity']:.2f}"
                    printer.text(f"{'$' + str(item['price']):>7}")
                    printer.text(f"{qty:>7}")
                    printer.text(f"{total:>8}\n")
                else:
                    printer.text("\n")
        
        # Calculate totals
        subtotal = sum(item["price"] * item["quantity"] for item in items)
        tax = subtotal * tax_rate
        total = subtotal + tax
        
        # Print totals
        printer.text("-" * 48 + "\n")
        printer.set(align='right')
        printer.text(f"SUBTOTAL: ${subtotal:.2f}\n")
        printer.text(f"TAX ({tax_rate*100:.2f}%): ${tax:.2f}\n")
        printer.set(align='right', width=1, height=2)
        printer.text(f"TOTAL: ${total:.2f}\n\n")
        printer.set(align='left', width=1, height=1)
        
        # Payment info
        printer.text(f"Payment: Visa ****1234\n")
        printer.text(f"Change Due: $0.00\n\n")
        
        # Footer
        printer.set(align='center')
        printer.text("Thank you for shopping with us!\n")
        printer.text("Returns within 14 days with receipt\n")
        
        # Finalize
        printer.cut()
        return True
    except Exception as e:
        print(f"Printer error: {e}")
        return False

# Run both
if __name__ == "__main__":
    # Show rich preview
    rich_preview(store_info, items, tax_rate)
    
    # Print to thermal printer
    print("\nAttempting to print receipt...")
    if print_receipt(store_info, items, tax_rate):
        print("Receipt printed successfully!")
    else:
        print("Failed to print receipt")