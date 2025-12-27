import requests

def reset_db():
    try:
        print("🗑️ Requesting Vector Store Reset...")
        resp = requests.delete("http://localhost:8000/reset")
        if resp.status_code == 200:
            print("✅ SUCCESS: Database cleared.")
        else:
            print(f"❌ FAILURE: {resp.status_code} - {resp.text}")
    except Exception as e:
        print(f"❌ Error connecting to backend: {e}")
        print("Make sure 'uv run main.py' is running!")

if __name__ == "__main__":
    reset_db()
