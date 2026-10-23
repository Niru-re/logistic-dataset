"""
Phase 12 — Try various Mendeley URL patterns to find downloadable files.
"""

import urllib.request
import urllib.error

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"}

urls = [
    # Mendeley public files patterns
    "https://data.mendeley.com/public-files/datasets/bdd69gyhv8/files",
    "https://data.mendeley.com/datasets/bdd69gyhv8/files",
    "https://data.mendeley.com/public-files/datasets/bdd69gyhv8/1/files",
    # Try common Mendeley S3/CDN patterns
    "https://md-datasets.s3.amazonaws.com/bdd69gyhv8/Original+Image.zip",
    "https://md-datasets.s3.amazonaws.com/bdd69gyhv8/Original%20Image.zip",
    # Try the article's supplementary material
    "https://ars.els-cdn.com/content/image/1-s2.0-S2352340922009128-mmc1.zip",
    "https://ars.els-cdn.com/content/image/1-s2.0-S2352340922009128-mmc2.zip",
]

for url in urls:
    print(f"\n=== Trying: {url} ===")
    try:
        req = urllib.request.Request(url, headers=headers, method="HEAD")
        with urllib.request.urlopen(req, timeout=15) as resp:
            print(f"  Status: {resp.status}")
            print(f"  Final URL: {resp.geturl()}")
            print(f"  Content-Type: {resp.headers.get('Content-Type', 'N/A')}")
            print(f"  Content-Length: {resp.headers.get('Content-Length', 'N/A')}")
    except urllib.error.HTTPError as e:
        print(f"  HTTP Error: {e.code} {e.reason}")
    except Exception as e:
        print(f"  Error: {type(e).__name__}: {e}")
