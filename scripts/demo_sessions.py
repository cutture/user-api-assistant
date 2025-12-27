
import requests
import time
from termcolor import colored

BASE_URL = "http://localhost:8000"

def demo_sessions():
    print(colored("👥 Session Management Demo", "cyan", attrs=["bold"]))

    # 1. Create Sessions
    print(colored("\n1. Creating Sessions...", "yellow"))
    s1 = requests.post(f"{BASE_URL}/sessions/", json={"user_id": "alice"}).json()
    s2 = requests.post(f"{BASE_URL}/sessions/", json={"user_id": "bob"}).json()
    
    print(f"   Alice's Session: {s1['id']}")
    print(f"   Bob's Session:   {s2['id']}")

    # 2. Chat in Alice's Session
    print(colored("\n2. Alice chats (Context Setting)...", "yellow"))
    q1 = "My name is Alice. I am a Python developer."
    print(f"   User: {q1}")
    resp = requests.post(f"{BASE_URL}/sessions/{s1['id']}/chat", json={"query": q1}).json()
    print(f"   Assistant: {resp['response'][:50]}...")

    # 3. Chat in Bob's Session (Independent)
    print(colored("\n3. Bob chats (Independent Context)...", "yellow"))
    q2 = "My name is Bob. I use Golang."
    print(f"   User: {q2}")
    resp = requests.post(f"{BASE_URL}/sessions/{s2['id']}/chat", json={"query": q2}).json()
    print(f"   Assistant: {resp['response'][:50]}...")

    # 4. Verify Context Retention
    print(colored("\n4. Verifying Alice's Context...", "yellow"))
    q3 = "What is my name and what language do I use?"
    print(f"   User: {q3}")
    resp = requests.post(f"{BASE_URL}/sessions/{s1['id']}/chat", json={"query": q3}).json()
    print(f"   Assistant: {resp['response']}")
    
    if "Alice" in resp['response'] and "Python" in resp['response']:
        print(colored("   ✅ Context Preserved!", "green"))
    else:
        print(colored("   ❌ Context Lost!", "red"))

    # 5. List Sessions
    print(colored("\n5. Listing Sessions...", "yellow"))
    sessions = requests.get(f"{BASE_URL}/sessions/").json()
    for s in sessions:
        print(f"   - {s['id']} (User: {s['user_id']}, Msgs: {s['message_count']})")

if __name__ == "__main__":
    try:
        demo_sessions()
    except requests.exceptions.ConnectionError:
        print(colored("❌ Could not connect to API. Is 'uv run main.py' running?", "red"))
