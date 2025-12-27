import re
from typing import List, Dict, Any
from langchain_text_splitters import RecursiveCharacterTextSplitter

class APIDocSplitter:
    """
    Splits API documentation into semantic chunks based on endpoints 
    and meaningful sections, rather than just character count.
    """
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.base_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n## ", "\n### ", "\n#### ", "\n- ", "\n", " "]
        )

    def split_text(self, text: str) -> List[str]:
        """
        Splits text using the recursive splitter optimized for Markdown structure.
        """
        return self.base_splitter.split_text(text)

    def split_json_spec(self, spec: Dict[str, Any]) -> List[str]:
        """
        Intelligently splits a JSON/YAML OpenAPI spec file.
        Extracts endpoints (paths) as individual chunks.
        """
        chunks = []
        
        # Extract general info
        info = spec.get("info", {})
        title = info.get("title", "Unknown API")
        description = info.get("description", "")
        
        # Extract Global Context (Servers & Auth) - Crucial for code generation
        servers = spec.get("servers", [])
        server_urls = [s.get("url") for s in servers]
        
        security_schemes = spec.get("components", {}).get("securitySchemes", {})
        auth_info = str(security_schemes)

        global_context = (
            f"Base URLs: {server_urls}\n"
            f"Authentication Schemes: {auth_info}\n"
        )

        # Add a general overview chunk
        chunks.append(f"API: {title}\nDescription: {description}\n{global_context}")

        # Extract Paths/Endpoints
        paths = spec.get("paths", {})
        for path, methods in paths.items():
            for method, details in methods.items():
                summary = details.get("summary", "No summary")
                desc = details.get("description", "")
                
                # Create a semantic chunk for this specific endpoint
                # We inject the global context so this chunk is standalone
                chunk = (
                    f"API: {title}\n"
                    f"Endpoint: {method.upper()} {path}\n"
                    f"Summary: {summary}\n"
                    f"Description: {desc}\n"
                    f"Parameters: {str(details.get('parameters', []))}\n"
                    f"RequestBody: {str(details.get('requestBody', {}))}\n"
                    f"{global_context}"
                )
                chunks.append(chunk)
                
        return chunks
