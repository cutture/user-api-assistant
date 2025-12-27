import os
import json
import zipfile
from pathlib import Path
from dotenv import load_dotenv

# Robustly load .env from the project root
script_dir = Path(__file__).resolve().parent
project_root = script_dir.parent
env_path = project_root / ".env"

print(f"🔍 Loading .env from: {env_path}")
load_dotenv(env_path)

username = os.getenv("KAGGLE_USERNAME")
key = os.getenv("KAGGLE_KEY")

if not username or not key:
    print("❌ Error: KAGGLE_USERNAME or KAGGLE_KEY not found in environment.")
    print("Please ensure your .env file exists and contains these keys.")
    exit(1)

print(f"✅ Found Credentials: {username} / {'*' * len(key)}")

# Ensure credentials exist where Kaggle expects them
kaggle_config_dir = Path.home() / ".kaggle"
kaggle_json_path = kaggle_config_dir / "kaggle.json"

if not kaggle_json_path.exists():
    print(f"⚠️ kaggle.json not found at {kaggle_json_path}. Creating it from .env...")
    kaggle_config_dir.mkdir(parents=True, exist_ok=True)
    with open(kaggle_json_path, "w") as f:
        json.dump({"username": username, "key": key}, f)
    print("✅ Created ~/.kaggle/kaggle.json")

# Now import Kaggle API (it will find the json file)
from kaggle.api.kaggle_api_extended import KaggleApi

# Config
DATASET_NAME = "shivd24coder/ultimate-api-dataset-1000-data-sources"
DATA_DIR = project_root / "data"
RAW_DIR = DATA_DIR / "raw"

def setup_directories():
    RAW_DIR.mkdir(parents=True, exist_ok=True)

def download_dataset():
    """Authenticates with Kaggle and downloads the dataset."""
    try:
        api = KaggleApi()
        api.authenticate()
        
        print(f"⬇️ Downloading {DATASET_NAME}...")
        api.dataset_download_files(DATASET_NAME, path=RAW_DIR, unzip=True)
        print("✅ Download & Extraction Complete!")
        
        # Cleanup zip if exists (Kaggle API usually unzips automatically with unzip=True, but sometimes leaves a zip)
        for item in RAW_DIR.glob("*.zip"):
            item.unlink()
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Please ensure KAGGLE_USERNAME and KAGGLE_KEY are set in your .env file.")

if __name__ == "__main__":
    setup_directories()
    download_dataset()
