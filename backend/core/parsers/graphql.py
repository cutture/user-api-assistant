
from .base import BaseParser
from typing import List, Dict, Any, Union
import re
import json

class GraphQLParser(BaseParser):
    """
    Parses GraphQL Schema Definitions (SDL) or Introspection JSON.
    Splits by Type definitions, Queries, and Mutations.
    """

    @property
    def supported_types(self) -> List[str]:
        return [".graphql", ".gql", "application/graphql"]

    def parse(self, content: Union[str, Dict[str, Any]], **kwargs) -> List[str]:
        if isinstance(content, dict):
             # Handle Introspection JSON if passed as dict
             return self._parse_introspection(content)
        
        # Assume SDL String
        return self._parse_sdl(content)

    def _parse_sdl(self, text: str) -> List[str]:
        chunks = []
        # Simple Regex strategies to extract meaningful blocks
        
        # 1. Types
        # Pattern: type Name { ... }
        # Note: This regex is non-recursive so strictly nested braces might break it, 
        # but standard gql formatting usually works.
        type_pattern = r'(type\s+\w+\s*\{[^}]+\})' 
        types = re.findall(type_pattern, text, re.DOTALL)
        for t in types:
            chunks.append(f"GraphQL Type Definition:\n{t.strip()}")

        # 2. Interfaces/Unions/Enums
        other_pattern = r'((?:interface|union|enum|input)\s+\w+\s*\{[^}]+\})'
        others = re.findall(other_pattern, text, re.DOTALL)
        for o in others:
             chunks.append(f"GraphQL Definition:\n{o.strip()}")

        # 3. Schema block
        schema_pattern = r'(schema\s*\{[^}]+\})'
        schemas = re.findall(schema_pattern, text, re.DOTALL)
        for s in schemas:
            chunks.append(f"GraphQL Schema Root:\n{s.strip()}")

        if not chunks:
            # Fallback: Just return the whole thing if regex fails to find structure
            chunks.append(text)
            
        return chunks

    def _parse_introspection(self, data: Dict) -> List[str]:
        # TODO: Implement full introspection parsing if needed.
        # For now, convert to string and try best effort or return raw
        return [json.dumps(data, indent=2)]
