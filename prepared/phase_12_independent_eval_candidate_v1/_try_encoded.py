"""
Phase 12 — Try Mendeley download with URL-encoded filenames.
"""

import urllib.request
import urllib.error
import urllib.parse

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"}

uuids = ["6cbd3156-b5f2-38cf-b4f5-1e7c5dcb19dc", "b9de8157-a6b9-37f8-bc9e-0222c8196f93"]
# URL-encode spaces
filenames_encoded = {
    "Original Image.zip": urllib.parse.quote("Original Image.zip"),
    "Augmented Image.zip": urllib.parse.quote("Augmented Image.zip"),
}

for uuid in uuids:
    for fname, fname_enc in filenames_encoded.items():
        # Try public-files pattern with encoded filename
        urls = [
            f"https://data.mendeley.com/public-files/datasets/bdd69gyhv8/files/{uuid}/{fname_enc}",
            f"https://data.mendeley.com/v1/datasets/bdd69gyhv8/files/{uuid}/{fname_enc}",
        ]
        for url in urls:
            print(f"\n=== Trying: {url} ===")
            try:
                req = urllib.request.Request(url, headers=headers, method="HEAD")
                with urllib.request.urlopen(req, timeout=30) as resp:
                    print(f"  Status: {resp.status}")
                    print(f"  Final URL: {resp.geturl()}")
                    print(f"  Content-Type: {resp.headers.get('Content-Type', 'N/A')}")
                    print(f"  Content-Length: {resp.headers.get('Content-Length', 'N/A')}")
                    if resp.status == 200:
                        ct = resp.headers.get('Content-Type', '').lower()
                        if 'zip' in ct or 'octet-stream' in ct:
                            print(f"  *** FOUND DOWNLOADABLE FILE! ***")
            except urllib.error.HTTPError as e:
                print(f"  HTTP Error: {e.code} {e.reason}")
            except Exception as e:
                print(f"  Error: {type(e).__name__}: {e}")
