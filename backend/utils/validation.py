
from pydantic import ValidationError, field_validator
import re

class RequestValidator:
    @staticmethod
    def validate_api_key(api_key: str) -> str:
        """
        Validates structure of common API keys (e.g. Groq, OpenAI).
        """
        if not api_key:
            raise ValueError("API Key cannot be empty")
            
        # Example: Groq keys start with 'gsk_', OpenAI with 'sk-'
        if not (api_key.startswith("gsk_") or api_key.startswith("sk-")):
             # Weak warning, don't block in case of custom keys, but good for specific apps
             pass 
        
        if len(api_key) < 10:
             raise ValueError("API Key too short to be valid")
             
        return api_key

    @staticmethod
    def validate_no_injection(text: str) -> str:
        """
        Basic check for SQL/Command injection patterns.
        (Note: Parameterized queries are better, but this is a fail-safe for input).
        """
        dangerous_patterns = [
            "; DROP TABLE", 
            "1=1 --", 
            "/bin/sh", 
            "rm -rf"
        ]
        for pattern in dangerous_patterns:
            if pattern in text:
                raise ValueError("Potentially dangerous input detected")
        return text
