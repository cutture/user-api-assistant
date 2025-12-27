
import requests
from bs4 import BeautifulSoup
import re
import time
import sys

# --- SHIM for LangChain compatibility with recent duckduckgo-search ---
try:
    import duckduckgo_search
    if "ddgs" not in sys.modules:
        sys.modules["ddgs"] = duckduckgo_search
except ImportError:
    pass
# ---------------------------------------------------------------------

from langchain_community.tools import DuckDuckGoSearchRun

# Initialize search
search_tool = DuckDuckGoSearchRun()

urls = [
    "https://doc.sitecore.com/xp/en/developers/salesforce-connect/latest/sitecore-connect-for-salesforce-crm/install-sitecore-connect-for-salesforce-crm-on-prem.html",
    "https://developers.sitecore.com/downloads/Salesforce_Connect/2x/Sitecore_Connect_for_Salesforce_CRM_20",
    "https://help.salesforce.com/s/articleView?id=mktg.mc_ceb_sitecore_content.htm&type=5",
    "https://www.google.com/search?q=provide+documentation" 
]

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}

def extract_keywords(url):
    # Ignore common domains
    if "google.com" in url or "search" in url:
        return None
        
    # Get the last path segment
    clean_url = url.split('?')[0].rstrip('/')
    segment = clean_url.split('/')[-1]
    
    # Replace separators
    keywords = re.sub(r'[-_.]', ' ', segment)
    
    # Heuristic: if segment is too short or generic (e.g. "index.html"), take parent
    if len(keywords) < 5 or "index" in keywords.lower():
        segment = clean_url.split('/')[-2]
        keywords = re.sub(r'[-_.]', ' ', segment)
        
    return keywords + " documentation"

print(f"Testing {len(urls)} URLs with Fallback...")

for url in urls:
    print(f"\n--- Processing: {url} ---")
    
    # 1. Filter Google Search
    if "google.com/search" in url:
        print("⚠️ Skipping Google Search URL")
        continue

    content = ""
    try:
        # 2. Try Direct Scrape
        print("   Attempting Scrape...")
        resp = requests.get(url, timeout=10, headers=headers)
        
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.content, 'html.parser')
            for script in soup(["script", "style", "nav", "footer"]):
                script.decompose()
            text = soup.get_text(separator=' ')
            content = " ".join(text.split())
            
            if len(content) < 500:
                print(f"   ⚠️ Scrape too short ({len(content)} chars). Triggering fallback.")
                content = "" # Reset to force fallback
            else:
                print(f"   ✅ Scrape Success ({len(content)} chars)")
        else:
            print(f"   ❌ Scrape Failed (Status {resp.status_code})")

    except Exception as e:
        print(f"   ❌ Scrape Exception: {e}")

    # 3. Fallback Search
    if not content:
        keywords = extract_keywords(url)
        print(f"   🕵️ Fallback Search for: '{keywords}'")
        try:
            # We assume the user wants info FROM this page, so we search for its content
            search_res = search_tool.invoke(keywords)
            print(f"   ✅ Search Result: {search_res[:200]}...")
        except Exception as e:
            print(f"   ❌ Search Failed: {e}")
            
