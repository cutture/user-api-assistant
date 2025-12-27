
import pytest
from core.parsers.factory import parser_factory
from core.parsers.openapi import OpenAPIParser
from core.parsers.graphql import GraphQLParser
from core.parsers.postman import PostmanParser

def test_factory_openapi():
    parser = parser_factory.get_parser("application/json")
    assert isinstance(parser, OpenAPIParser)

def test_factory_graphql():
    parser = parser_factory.get_parser("application/graphql")
    assert isinstance(parser, GraphQLParser)
    
    parser2 = parser_factory.get_parser(".graphql")
    assert isinstance(parser2, GraphQLParser)

def test_factory_postman():
    parser = parser_factory.get_parser("application/vnd.postman.collection+json")
    assert isinstance(parser, PostmanParser)

def test_graphql_parsing():
    content = """
    type User {
        id: ID!
        name: String
    }
    
    type Query {
        getUser(id: ID!): User
    }
    """
    parser = GraphQLParser()
    chunks = parser.parse(content)
    
    assert len(chunks) == 2
    assert "Type Definition" in chunks[0]
    assert "User" in chunks[0]
    assert "Query" in chunks[1]

def test_openapi_parsing():
    content = {
        "openapi": "3.0.0",
        "info": {"title": "Test API"},
        "paths": {
            "/users": {
                "get": {"summary": "Get Users"}
            }
        }
    }
    parser = OpenAPIParser()
    chunks = parser.parse(content)
    assert len(chunks) == 2 # Overview + 1 Endpoint
    assert "Endpoint: GET /users" in chunks[1]

def test_postman_parsing():
    content = {
        "info": {"name": "Postman Test"},
        "item": [
            {
                "name": "Folder 1",
                "item": [
                    {
                        "name": "Get Stuff",
                        "request": {
                            "method": "GET",
                            "url": "http://example.com"
                        }
                    }
                ]
            }
        ]
    }
    parser = PostmanParser()
    chunks = parser.parse(content)
    
    assert len(chunks) == 1
    assert "Request: Get Stuff" in chunks[0]
    assert "Folder 1" in chunks[0] # Context should contain parent folder
