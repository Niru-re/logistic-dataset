"""
Phase 12 — Follow Mendeley redirect and extract file download URLs.
"""

import urllib.request
import urllib.error
import re

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"}

# Try to follow the redirect from /files
url = "https://data.mendeley.com/datasets/bdd69gyhv8/files"
print(f"=== Following redirect: {url} ===")
try:
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        print(f"  Status: {resp.status}")
        print(f"  Final URL: {resp.geturl()}")
        data = resp.read(5000)
        print(f"  Content-Type: {resp.headers.get('Content-Type', 'N/A')}")
        print(f"  First 1000 bytes: {data[:1000]}")
except urllib.error.HTTPError as e:
    print(f"  HTTP Error: {e.code} {e.reason}")
    # Try to read error body
    try:
        body = e.read(1000)
        print(f"  Error body: {body[:1000]}")
    except:
        pass
except Exception as e:
    print(f"  Error: {type(e).__name__}: {e}")

# Also try the main dataset page with full HTML read
print("\n=== Reading main dataset page HTML ===")
url2 = "https://data.mendeley.com/datasets/bdd69gyhv8/1"
try:
    req = urllib.request.Request(url2, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        print(f"  Status: {resp.status}")
        print(f"  Final URL: {resp.geturl()}")
        html = resp.read(20000).decode("utf-8", errors="replace")
        # Look for file download patterns
        patterns = [
            r'href="([^"]*\.zip[^"]*)"',
            r'href="([^"]*public-files[^"]*)"',
            r'files/[^"\s<>]+',
            r'Download[^<]*',
            r'Original[^<]*Image[^<]*',
        ]
        for p in patterns:
            matches = re.findall(p, html, re.IGNORECASE)
            if matches:
                print(f"  Pattern '{p}': {matches[:10]}")
        # Search for .zip references
        zip_refs = re.findall(r'[^"\s<>]*\.zip[^"\s<>]*', html, re.IGNORECASE)
        if zip_refs:
            print(f"  ZIP references found: {zip_refs[:20]}")
        else:
            print("  No .zip references found in first 20KB")
except urllib.error.HTTPError as e:
    print(f"  HTTP Error: {e.code} {e.reason}")
except Exception as e:
    print(f"  Error: {type(e).__name__}: {e}")
