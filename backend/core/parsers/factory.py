
from typing import Dict, Type
from .base import BaseParser
from .openapi import OpenAPIParser
from .graphql import GraphQLParser
from .postman import PostmanParser

class ParserFactory:
    _parsers: Dict[str, BaseParser] = {}

    def __init__(self):
        self._register_parser(OpenAPIParser())
        self._register_parser(GraphQLParser())
        self._register_parser(PostmanParser())

    def _register_parser(self, parser: BaseParser):
        for t in parser.supported_types:
            self._parsers[t] = parser

    def get_parser(self, mime_type_or_ext: str) -> BaseParser:
        """
        Returns a matching parser or None.
        Case insensitive.
        """
        key = mime_type_or_ext.lower()
        
        # exact match
        if key in self._parsers:
            return self._parsers[key]
        
        # Extension fallback
        for k, v in self._parsers.items():
            if key.endswith(k):
                return v
                
        return None

# Singleton
parser_factory = ParserFactory()
