
from typing import List, Dict, Any, Union
from .base import BaseParser
import json

class OpenAPIParser(BaseParser):
    """
    Parses OpenAPI (Swagger) JSON/YAML specifications.
    Extracts endpoints as individual semantic chunks.
    """

    @property
    def supported_types(self) -> List[str]:
        return ["application/json", "application/yaml", "application/x-yaml", ".json", ".yaml"]

    def parse(self, content: Union[str, Dict[str, Any]], **kwargs) -> List[str]:
        # Ensure dict
        if isinstance(content, str):
            try:
                spec = json.loads(content)
            except json.JSONDecodeError:
                # Fallback or error? For now assume valid JSON if this parser is chosen
                return [content] 
        else:
            spec = content

        chunks = []
        
        # Extract general info
        info = spec.get("info", {})
        title = info.get("title", "Unknown API")
        description = info.get("description", "")
        
        # Extract Global Context (Servers & Auth)
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
                if method.lower() not in ['get', 'post', 'put', 'delete', 'patch', 'options', 'head']:
                    continue
                    
                summary = details.get("summary", "No summary")
                desc = details.get("description", "")
                
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
