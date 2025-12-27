
from .base import BaseParser
from typing import List, Dict, Any, Union
import json

class PostmanParser(BaseParser):
    """
    Parses Postman Collection v2.1 JSON.
    Recursively finds 'item' nodes which represent requests.
    """

    @property
    def supported_types(self) -> List[str]:
        return ["application/vnd.postman.collection+json", ".postman_collection.json"]

    def parse(self, content: Union[str, Dict[str, Any]], **kwargs) -> List[str]:
        if isinstance(content, str):
            try:
                data = json.loads(content)
            except:
                return [content]
        else:
            data = content

        chunks = []
        info = data.get("info", {})
        coll_name = info.get("name", "Unknown Collection")
        coll_desc = info.get("description", "")

        # Recurse items
        self._process_items(data.get("item", []), chunks, parent_context=f"Collection: {coll_name}")
        
        return chunks

    def _process_items(self, items: List[Dict], chunks: List[str], parent_context: str):
        for item in items:
            name = item.get("name", "Unnamed")
            
            # If it's a folder, recurse
            if "item" in item:
                self._process_items(item["item"], chunks, parent_context=f"{parent_context} > {name}")
                continue
            
            # It's a Request
            request = item.get("request", {})
            if not request:
                continue

            method = request.get("method", "GET")
            url = request.get("url", {})
            if isinstance(url, dict):
                raw_url = url.get("raw", "")
            else:
                raw_url = str(url)
                
            desc = request.get("description", "")
            
            # Construct Chunk
            chunk = (
                f"Context: {parent_context}\n"
                f"Request: {name}\n"
                f"Method: {method}\n"
                f"URL: {raw_url}\n"
                f"Description: {desc}\n"
                f"Headers: {json.dumps(request.get('header', []), indent=2)}\n"
                f"Body: {json.dumps(request.get('body', {}), indent=2)}"
            )
            chunks.append(chunk)
