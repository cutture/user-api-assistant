import requests
import json
import sys

URL = "http://localhost:8000/chat"
PAYLOAD = {"query": "How do I use the Cat Facts API?"}

try:
    print(f"📡 Sending request to {URL}...")
    response = requests.post(URL, json=PAYLOAD)
    
    if response.status_code == 200:
        data = response.json()
        print("\n✅ Backend Success!")
        print("-" * 20)
        print(f"📄 PLAN: {data.get('plan')}")
        print("-" * 20)
        print(f"💻 CODE: {data.get('response')}")
        print("-" * 20)
        print(f"📚 CONTEXT: {len(data.get('context', []))} docs retrieved.")
    else:
        print(f"❌ Backend Error: {response.status_code}")
        print(response.text)
        
except Exception as e:
    print(f"❌ Connection Failed: {e}")
    sys.exit(1)
