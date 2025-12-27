
import requests
import json
from termcolor import colored

API_URL = "http://localhost:8000/v1/search"

def demo_advanced_search():
    print(colored("🌐 Advanced REST API Demo", "cyan", attrs=["bold"]))
    
    # 1. Basic Search
    print(colored("\n1. Basic Hybrid Search", "yellow"))
    payload = {
        "query": "authentication errors",
        "limit": 3
    }
    try:
        response = requests.post(API_URL, json=payload)
        response.raise_for_status()
        print(json.dumps(response.json(), indent=2))
    except Exception as e:
        print(colored(f"❌ Failed: {e}", "red"))

    # 2. Filtered Search
    print(colored("\n2. Filtered Search (guide)", "yellow"))
    payload = {
        "query": "authentication errors",
        "filters": {"type": "guide"},
        "limit": 2
    }
    try:
        response = requests.post(API_URL, json=payload)
        print(json.dumps(response.json(), indent=2))
    except Exception as e:
         print(colored(f"❌ Failed: {e}", "red"))

if __name__ == "__main__":
    demo_advanced_search()
