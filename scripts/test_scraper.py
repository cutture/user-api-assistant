
import requests
from bs4 import BeautifulSoup
import re

urls = [
    "https://doc.sitecore.com/xp/en/developers/salesforce-connect/latest/sitecore-connect-for-salesforce-crm/install-sitecore-connect-for-salesforce-crm-on-prem.html",
    "https://developers.sitecore.com/downloads/Salesforce_Connect/2x/Sitecore_Connect_for_Salesforce_CRM_20",
    "https://doc.sitecore.com/xp/en/developers/salesforce-connect/latest/sitecore-connect-for-salesforce-crm/index-en.html",
    "https://help.salesforce.com/s/articleView?id=mktg.mc_ceb_sitecore_content.htm&type=5"
]

headers = {"User-Agent": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"}

print(f"Testing {len(urls)} URLs...")

for url in urls:
    print(f"\n--- Testing: {url} ---")
    try:
        resp = requests.get(url, timeout=10, headers=headers)
        print(f"Status: {resp.status_code}")
        
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.content, 'html.parser')
            
            # Remove scripts
            for script in soup(["script", "style"]):
                script.decompose()
            
            text = soup.get_text(separator='\n')
            clean_text = "\n".join([line.strip() for line in text.splitlines() if line.strip()])
            
            print(f"Extracted Length: {len(clean_text)}")
            print(f"Preview: {clean_text[:200]}...")
            
            if len(clean_text) < 500:
                print("⚠️ WARNING: Content seems very short. Likely blocked or JS-rendered.")
        else:
            print("❌ Failed to fetch.")
            
    except Exception as e:
        print(f"❌ Exception: {e}")
