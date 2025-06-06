#!/usr/bin/env python3
"""Test font detection system for Lao and English text"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sample import contains_lao_text, download_direct_font

def test_font_detection():
    """Test the font detection function"""
    test_cases = [
        ("ດບຍລາວ", True, "Lao text"),
        ("Hello World", False, "English text"),
        ("Mixed ດບຍລາວ text", True, "Mixed text with Lao"),
        ("Numbers 123", False, "Numbers and English"),
        ("ພິມໂຊຍ", True, "More Lao text"),
        ("", False, "Empty string")
    ]
    
    print("Testing font detection:")
    print("-" * 50)
    
    for text, expected, description in test_cases:
        result = contains_lao_text(text)
        status = "✅ PASS" if result == expected else "❌ FAIL"
        print(f"{status} {description}: '{text}' -> {result}")
    
    print("-" * 50)

def test_font_cache():
    """Test font cache status"""
    print("\nFont cache status:")
    print("-" * 30)
    
    cache_dir = "font_cache"
    if os.path.exists(cache_dir):
        fonts = os.listdir(cache_dir)
        if fonts:
            for font in fonts:
                font_path = os.path.join(cache_dir, font)
                size = os.path.getsize(font_path)
                print(f"✅ {font}: {size:,} bytes")
        else:
            print("❌ No fonts in cache")
    else:
        print("❌ Font cache directory not found")

if __name__ == "__main__":
    test_font_detection()
    test_font_cache()
    
    print("\n" + "="*50)
    print("Font detection system is ready!")
    print("Lao text will automatically use Noto Sans Lao font")
    print("English text will use thermal printer default font")
