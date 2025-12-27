
import re
from typing import Tuple, Dict, Any

class FilterManager:
    def parse_query(self, query: str) -> Tuple[str, Dict[str, Any]]:
        """
        Extracts metadata filters from a natural language query.
        Supported format: `key:value`
        Example: "login error type:guide source:manual" 
        Returns: ("login error", {"type": "guide", "source": "manual"})
        """
        filters = {}
        
        # Regex to find key:value pairs
        # Keys restricted to alphanumeric/underscore. Values restricted to alphanumeric/dots/dashes/underscores.
        # This prevents picking up valid URLs like https://... which contain colons but shouldn't be parsed as filters.
        # More robust: Look for space-preceded or start-of-line patterns.
        
        pattern = r'(?:^|\s)(\w+):([\w\-\.]+)(?=\s|$)'
        matches = re.findall(pattern, query)
        
        for key, value in matches:
            filters[key] = value
            
        # Remove matched filters from query
        clean_query = re.sub(pattern, '', query).strip()
        
        # Collapse extra spaces
        clean_query = " ".join(clean_query.split())
        
        return clean_query, filters

# Singleton
filter_manager = FilterManager()
