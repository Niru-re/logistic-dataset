"""
Phase 12 — Try to download Mendeley file and follow redirects.
"""

import urllib.request
import urllib.error

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

url = "https://data.mendeley.com/v1/datasets/bdd69gyhv8/files/6cbd3156-b5f2-38cf-b4f5-1e7c5dcb19dc/Original%20Image.zip"

try:
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=60) as resp:
        print(f"Status: {resp.status}")
        print(f"Final URL: {resp.geturl()}")
        ct = resp.headers.get("Content-Type", "N/A")
        cl = resp.headers.get("Content-Length", "N/A")
        print(f"Content-Type: {ct}")
        print(f"Content-Length: {cl}")
        data = resp.read(200)
        print(f"First 200 bytes: {data[:200]}")
except urllib.error.HTTPError as e:
    print(f"HTTP Error: {e.code} {e.reason}")
    try:
        body = e.read(500)
        print(f"Error body: {body[:500]}")
    except:
        pass
except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")
