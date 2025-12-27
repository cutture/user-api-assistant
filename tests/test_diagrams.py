
import pytest
from core.diagrams.generator import MermaidGenerator

@pytest.fixture
def sample_spec():
    return {
        "openapi": "3.0.0",
        "paths": {
            "/users": {
                "get": {
                    "summary": "Get Users",
                    "responses": {
                        "200": {"description": "OK"}
                    }
                }
            }
        },
        "components": {
            "schemas": {
                "User": {
                    "properties": {
                        "id": {"type": "integer"},
                        "name": {"type": "string"}
                    }
                }
            },
            "securitySchemes": {
                "ApiKey": {
                    "type": "apiKey",
                    "in": "header",
                    "name": "X-API-KEY"
                }
            }
        }
    }

def test_sequence_generator(sample_spec):
    gen = MermaidGenerator()
    code = gen.generate_sequence(sample_spec, "/users", "get")
    
    assert "sequenceDiagram" in code
    assert "User->>API: GET /users" in code
    assert "Backend-->>API: 200 OK" in code

def test_erd_generator(sample_spec):
    gen = MermaidGenerator()
    code = gen.generate_erd(sample_spec)
    
    assert "erDiagram" in code
    assert "User {" in code
    assert "integer id" in code

def test_auth_generator(sample_spec):
    gen = MermaidGenerator()
    code = gen.generate_auth_flow(sample_spec)
    
    assert "sequenceDiagram" in code
    assert "Scheme: ApiKey" in code
    assert "Client->>API: Request + header: X-API-KEY" in code
