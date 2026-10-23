"""
Phase 12 — Inspect Mendeley bundle.js for API download endpoints.
"""

import urllib.request
import re

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"}

url = "https://static.data.mendeley.com/scripts/script-v2.0.5.min.js"
print(f"=== Downloading bundle.js: {url} ===")
try:
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        js = resp.read().decode("utf-8", errors="replace")
        print(f"  Size: {len(js)} bytes")
        
        # Look for download-related API patterns
        patterns = [
            r'public-files[^"\']*',
            r'/api/[^"\']*download[^"\']*',
            r'download[^"\']*zip[^"\']*',
            r'files/[^"\']*',
            r'presigned[^"\']*',
            r's3[^"\']*',
            r'cloudfront[^"\']*',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, js, re.IGNORECASE)
            if matches:
                unique = list(set(matches))
                print(f"\n  Pattern '{pattern}': {len(unique)} matches")
                for m in unique[:10]:
                    print(f"    {m[:200]}")
except Exception as e:
    print(f"  Error: {type(e).__name__}: {e}")
