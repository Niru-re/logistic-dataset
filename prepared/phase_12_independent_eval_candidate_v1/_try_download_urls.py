"""
Phase 12 — Try Mendeley download URLs with discovered file UUIDs.
"""

import urllib.request
import urllib.error

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"}

uuids = ["6cbd3156-b5f2-38cf-b4f5-1e7c5dcb19dc", "b9de8157-a6b9-37f8-bc9e-0222c8196f93"]
filenames = ["Original Image.zip", "Augmented Image.zip", "original_image.zip", "augmented_image.zip"]

for uuid in uuids:
    for fname in filenames:
        # Try various URL patterns
        urls = [
            f"https://data.mendeley.com/public-files/datasets/bdd69gyhv8/files/{uuid}/{fname}",
            f"https://data.mendeley.com/public-files/datasets/bdd69gyhv8/files/{uuid}",
            f"https://data.mendeley.com/datasets/bdd69gyhv8/files/{uuid}/{fname}",
            f"https://data.mendeley.com/datasets/bdd69gyhv8/files/{uuid}",
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
                    # If we found a valid file, stop trying other patterns for this UUID
                    if resp.status == 200 and 'zip' in resp.headers.get('Content-Type', '').lower():
                        print(f"  *** FOUND ZIP FILE! ***")
                        break
            except urllib.error.HTTPError as e:
                print(f"  HTTP Error: {e.code} {e.reason}")
            except Exception as e:
                print(f"  Error: {type(e).__name__}: {e}")
