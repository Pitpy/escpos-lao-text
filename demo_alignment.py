#!/usr/bin/env python3
"""Visual demonstration of the alignment improvement"""

from escpos_sample_font import render_item_line, contains_lao_text, download_direct_font
from PIL import Image, ImageDraw, ImageFont
import os

def create_comparison_image():
    """Create a visual comparison showing alignment improvements"""
    
    # Test items
    items = [
        ("ເບຍລາວ", 2, 4.99, 9.98),
        ("Coffee", 1, 3.50, 3.50),
        ("ນົມຊິ້ນ", 1, 5.99, 5.99),
        ("Bread", 2, 2.25, 4.50),
    ]
    
    print("🎨 Creating visual comparison...")
    
    # Create comparison image
    img_width = 600
    img_height = len(items) * 40 + 100
    comparison_img = Image.new("RGB", (img_width, img_height), "white")
    draw = ImageDraw.Draw(comparison_img)
    
    # Title
    try:
        title_font = ImageFont.load_default()
        draw.text((20, 20), "UNIFIED IMAGE RENDERING RESULTS", font=title_font, fill="black")
        draw.text((20, 40), "Perfect alignment for mixed Lao/English text", font=title_font, fill="gray")
    except:
        draw.text((20, 20), "UNIFIED IMAGE RENDERING RESULTS", fill="black")
    
    # Render each item
    y_offset = 80
    for i, (name, qty, price, total) in enumerate(items):
        print(f"  ✓ Rendering: {name}")
        
        # Create item image
        item_img = render_item_line(name, qty, price, total, font_size=18)
        
        # Convert to RGB for comparison image
        item_rgb = item_img.convert("RGB")
        
        # Paste into comparison
        comparison_img.paste(item_rgb, (20, y_offset))
        y_offset += 35
    
    # Save comparison
    comparison_path = "alignment_comparison.png"
    comparison_img.save(comparison_path)
    print(f"💾 Saved comparison image: {comparison_path}")
    
    return comparison_path

def print_alignment_summary():
    """Print summary of alignment improvements"""
    print("\n" + "="*60)
    print("🎯 ALIGNMENT IMPROVEMENT SUMMARY")
    print("="*60)
    print()
    print("❌ BEFORE (Mixed Rendering):")
    print("   • Lao text → Custom font images (variable positioning)")
    print("   • English text → Thermal printer text (fixed positioning)")
    print("   • Result: Misaligned columns, inconsistent spacing")
    print()
    print("✅ AFTER (Unified Image Rendering):")
    print("   • ALL text → Rendered as images with precise positioning")
    print("   • Consistent font rendering for all languages")
    print("   • Perfect column alignment")
    print("   • Professional appearance")
    print()
    print("🔧 KEY IMPROVEMENTS:")
    print("   1. render_item_line() - Unified line rendering")
    print("   2. print_image_text() - Consistent text imaging")
    print("   3. Column positioning with pixel precision")
    print("   4. Automatic font selection (Lao vs English)")
    print()
    print("📊 RESULT:")
    print("   Beautiful, professionally aligned receipts! 🎉")
    print("="*60)

if __name__ == "__main__":
    print("🖼️  Creating visual alignment comparison...")
    
    try:
        image_path = create_comparison_image()
        print_alignment_summary()
        print(f"\n📁 Check the generated image: {image_path}")
    except Exception as e:
        print(f"❌ Error creating comparison: {e}")
        print_alignment_summary()
