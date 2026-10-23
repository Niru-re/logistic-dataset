"""
Phase 12 — Discover Mendeley download URLs (read-only discovery).

Attempts to locate the actual downloadable file URLs for the Mendeley dataset
without downloading anything yet. Only inspects HTTP headers/redirects.
"""

import urllib.request
import urllib.error

BASE = "https://data.mendeley.com/public-files/datasets/bdd69gyhv8/1/files"

# Common Mendeley file naming patterns to test
test_urls = [
    # Try the dataset files page
    "https://data.mendeley.com/datasets/bdd69gyhv8/1",
    # Try common file download patterns
    "https://data.mendeley.com/public-files/datasets/bdd69gyhv8/files/",
]

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

for url in test_urls:
    print(f"\n=== Trying: {url} ===")
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as resp:
            print(f"  Status: {resp.status}")
            print(f"  Final URL: {resp.geturl()}")
            print(f"  Content-Type: {resp.headers.get('Content-Type', 'N/A')}")
            print(f"  Content-Length: {resp.headers.get('Content-Length', 'N/A')}")
            # Read a small amount
            data = resp.read(2000)
            print(f"  First 500 bytes: {data[:500]}")
    except urllib.error.HTTPError as e:
        print(f"  HTTP Error: {e.code} {e.reason}")
    except Exception as e:
        print(f"  Error: {e}")
