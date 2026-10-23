"""
Phase 12 — Find Mendeley API endpoints referenced in page HTML.
"""

import urllib.request
import re

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"}

url = "https://data.mendeley.com/datasets/bdd69gyhv8/1"
req = urllib.request.Request(url, headers=headers)
with urllib.request.urlopen(req, timeout=30) as resp:
    html = resp.read().decode("utf-8", errors="replace")

# Look for API endpoint references
api_patterns = [
    r'/api/[^"\s<>]+',
    r'/v1/[^"\s<>]+',
    r'api\.mendeley\.com[^"\s<>]*',
    r'files/[^"\s<>]+',
    r'dataset[^"\s<>]*file[^"\s<>]*',
]

for pattern in api_patterns:
    matches = re.findall(pattern, html, re.IGNORECASE)
    if matches:
        unique = list(set(matches))
        print(f"Pattern '{pattern}': {len(unique)} unique matches")
        for m in unique[:10]:
            print(f"  {m[:150]}")

# Also look for JavaScript chunk files that might contain API endpoints
js_files = re.findall(r'src="([^"]*\.js[^"]*)"', html)
print(f"\nJavaScript files: {len(js_files)}")
for js in js_files[:10]:
    print(f"  {js}")

# Look for the dataset ID or file info in the HTML
doi_patterns = [
    r'bdd69gyhv8[^"\s<>]*',
    r'Original[^"\s<>]*',
    r'Augmented[^"\s<>]*',
]

for pattern in doi_patterns:
    matches = re.findall(pattern, html, re.IGNORECASE)
    if matches:
        unique = list(set(matches))
        print(f"\nPattern '{pattern}': {len(unique)} unique matches")
        for m in unique[:5]:
            print(f"  {m[:150]}")
