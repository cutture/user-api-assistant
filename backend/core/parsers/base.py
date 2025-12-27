
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Union

class BaseParser(ABC):
    """
    Abstract Base Class for all API Documentation Parsers.
    Strategies: OpenAPI, GraphQL, Postman, Markdown/Text.
    """

    @property
    @abstractmethod
    def supported_types(self) -> List[str]:
        """List of supported MIME types or file extensions."""
        pass

    @abstractmethod
    def parse(self, content: Union[str, Dict[str, Any]], **kwargs) -> List[str]:
        """
        Parses content into semantic chunks (documents).
        
        Args:
            content: Raw string content or parsed JSON dict.
            kwargs: Additional metadata (filename, etc.)
            
        Returns:
            List of text chunks suitable for embedding.
        """
        pass
