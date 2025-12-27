
import re
import json
import uuid

def convert_to_postman_collection(plan_text: str, generated_code: str) -> dict:
    """
    Parses a plan/code string to generate a basic Postman Collection v2.1.
    This is a heuristic parser. It looks for HTTP verbs and URLs.
    """
    collection_id = str(uuid.uuid4())
    
    collection = {
        "info": {
            "_postman_id": collection_id,
            "name": "API Assistant Generated Collection",
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
        },
        "item": []
    }
    
    # 1. Regex to find potential API calls in the generated code or plan
    # Look for patterns like: requests.get("https://...", ...)
    # or comments like "POST /pets"
    
    # Simple regex for python requests
    # format: method, url
    python_pattern = r'requests\.(get|post|put|delete|patch)\(\s*["\'](https?://[^"\']+)["\']'
    matches = re.findall(python_pattern, generated_code, re.IGNORECASE)
    
    seen_requests = set()
    
    for method, url in matches:
        key = (method.upper(), url)
        if key in seen_requests:
            continue
        seen_requests.add(key)
        
        item_name = f"{method.upper()} {url.split('/')[-1]}"
        if not item_name.strip():
            item_name = "API Request"
            
        request_item = {
            "name": item_name,
            "request": {
                "method": method.upper(),
                "header": [
                    {
                        "key": "Content-Type",
                        "value": "application/json",
                        "type": "text"
                    }
                ],
                "url": {
                    "raw": url,
                    "protocol": url.split("://")[0],
                    "host": url.split("://")[1].split("/")[0].split("."),
                    "path": url.split("://")[1].split("/")[1:]
                }
            },
            "response": []
        }
        collection["item"].append(request_item)
        
    # Fallback: finding Markdown-style "GET /path" in plan if code is empty/unparseable
    if not collection["item"]:
        md_pattern = r'(GET|POST|PUT|DELETE)\s+(https?://[^\s\)]+|/[^\s]+)'
        md_matches = re.findall(md_pattern, plan_text)
        
        for method, url in md_matches:
            # If path only, use placeholder host
            full_url = url
            if url.startswith("/"):
                full_url = "{{base_url}}" + url
                
            request_item = {
                "name": f"{method.upper()} Request",
                "request": {
                    "method": method.upper(),
                    "header": [],
                    "url": {
                        "raw": full_url,
                        "host": [full_url] 
                    }
                }
            }
            collection["item"].append(request_item)

    return collection
