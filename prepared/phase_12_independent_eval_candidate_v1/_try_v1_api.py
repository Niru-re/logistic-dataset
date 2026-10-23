"""
Phase 12 — Try Mendeley v1 API for file listings.
"""

import urllib.request
import urllib.error
import json

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"}

urls = [
    "https://data.mendeley.com/v1/datasets/bdd69gyhv8/files",
    "https://data.mendeley.com/api/datasets/v1/bdd69gyhv8/files",
    "https://data.mendeley.com/api/files/datasets/bdd69gyhv8/1",
]

for url in urls:
    print(f"\n=== Trying: {url} ===")
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as resp:
            print(f"  Status: {resp.status}")
            print(f"  Final URL: {resp.geturl()}")
            print(f"  Content-Type: {resp.headers.get('Content-Type', 'N/A')}")
            data = resp.read(5000)
            print(f"  First 2000 bytes: {data[:2000]}")
    except urllib.error.HTTPError as e:
        print(f"  HTTP Error: {e.code} {e.reason}")
        try:
            body = e.read(1000)
            print(f"  Error body: {body[:1000]}")
        except:
            pass
    except Exception as e:
        print(f"  Error: {type(e).__name__}: {e}")
