"""
Phase 12 — Search Mendeley bundle.js for download API patterns.
"""

import urllib.request
import re

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

url = "https://static.data.mendeley.com/scripts/script-v2.0.5.min.js"
req = urllib.request.Request(url, headers=headers)
with urllib.request.urlopen(req, timeout=30) as resp:
    js = resp.read().decode("utf-8", errors="replace")

print(f"JS size: {len(js)} bytes")

# Search for key terms
for term in ["public-files", "download", "presigned", "s3", "cloudfront", "api/datasets", "files/"]:
    count = js.lower().count(term.lower())
    print(f"'{term}': {count} occurrences")
    if count > 0:
        # Show context around first occurrence
        idx = js.lower().find(term.lower())
        context = js[max(0,idx-100):idx+200]
        print(f"  Context: ...{context}...")
