"""
Phase 12 — Try to extract file download info from Mendeley page HTML.
"""

import urllib.request
import urllib.error
import re
import json

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"}

url = "https://data.mendeley.com/datasets/bdd69gyhv8/1"
print(f"=== Reading full page: {url} ===")
try:
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        html = resp.read().decode("utf-8", errors="replace")
        print(f"  Status: {resp.status}")
        print(f"  Page size: {len(html)} bytes")
        
        # Look for various patterns
        patterns = {
            "zip_files": r'[^"\s<>]*\.zip[^"\s<>]*',
            "public_files": r'public-files[^"\s<>]*',
            "file_uuid": r'[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}',
            "download_url": r'download[^"\s<>]*',
            "Original Image": r'Original[^"\s<>]*Image[^"\s<>]*',
            "__NEXT_DATA__": r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>',
            "window.__": r'window\.__[^=]*=\s*(\{.*?\});',
        }
        
        for name, pattern in patterns.items():
            matches = re.findall(pattern, html, re.IGNORECASE | re.DOTALL)
            if matches:
                print(f"\n  {name}: {len(matches)} matches")
                for m in matches[:5]:
                    print(f"    {m[:200]}")
        
        # Look for any JSON embedded in the page
        json_matches = re.findall(r'<script[^>]*type="application/json"[^>]*>(.*?)</script>', html, re.DOTALL)
        if json_matches:
            print(f"\n  JSON script tags: {len(json_matches)}")
            for jm in json_matches[:3]:
                print(f"    Length: {len(jm)}")
                
except Exception as e:
    print(f"  Error: {type(e).__name__}: {e}")
