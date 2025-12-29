
import os
import requests
from pathlib import Path

# Configuration
TEST_DATA_DIR = Path(__file__).parent.parent / "test_data"
SPECS = {
    "petstore.json": "https://petstore.swagger.io/v2/swagger.json",
    "museum.yaml": "https://raw.githubusercontent.com/Redocly/museum-openapi-example/main/openapi.yaml",
    "petstore.yaml": "https://raw.githubusercontent.com/swagger-api/swagger-petstore/master/src/main/resources/openapi.yaml"
}

def download_specs():
    if not TEST_DATA_DIR.exists():
        os.makedirs(TEST_DATA_DIR)
        print(f"Created directory: {TEST_DATA_DIR}")

    print("⬇️ Downloading Sample OpenAPI Specs...")
    
    for name, url in SPECS.items():
        try:
            print(f"   Fetching {name}...", end=" ")
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                file_path = TEST_DATA_DIR / name
                file_path.write_text(resp.text, encoding="utf-8")
                print(f"✅ Saved.")
            else:
                print(f"❌ Failed (Status {resp.status_code})")
        except Exception as e:
            print(f"❌ Error: {e}")

    print("\n✅ Download Complete. Data is in 'test_data/' folder.")
    print("   You can now ingest this folder using: ")
    print(f"   python backend/cli.py batch {TEST_DATA_DIR}")

if __name__ == "__main__":
    download_specs()
