#!/usr/bin/env python3
import requests
import re

# Test the font CSS download
font_url = "https://fonts.googleapis.com/css2?family=Noto+Sans+Lao:wght@400;700&display=swap"

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
}

print("Testing Google Fonts CSS download...")
response = requests.get(font_url, headers=headers, timeout=10)
print(f"Status: {response.status_code}")
print(f"Content length: {len(response.text)}")
print("\nFirst 500 chars:")
print(response.text[:500])

# Test regex patterns
css_content = response.text
patterns = [
    r'src:\s*url\((https://fonts\.gstatic\.com[^)]+\.ttf)\)',
    r'src:\s*url\((https://[^)]+\.ttf)\)',
    r'url\((https://fonts\.gstatic\.com[^)]+\.ttf)\)',
    r'(https://fonts\.gstatic\.com[^)]+\.ttf)'
]

print("\nTesting regex patterns:")
for i, pattern in enumerate(patterns):
    match = re.search(pattern, css_content)
    if match:
        print(f"Pattern {i+1} FOUND: {match.group(1)}")
    else:
        print(f"Pattern {i+1}: No match")

# Show all URLs found
all_urls = re.findall(r'(https://[^\s)]+\.ttf)', css_content)
print(f"\nAll TTF URLs found: {all_urls}")
