
import sys
import os
import json

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), "../backend"))

from core.diagrams.generator import mermaid_generator
from termcolor import colored

SAMPLE_SPEC = {
    "openapi": "3.0.0",
    "paths": {
        "/orders": {
            "post": {
                "summary": "Create Order",
                "parameters": [
                    {"name": "Authorization", "in": "header"}
                ],
                "responses": {
                    "201": {"description": "Order Created"},
                    "400": {"description": "Bad Request"}
                }
            }
        }
    },
    "components": {
        "schemas": {
            "Order": {
                "properties": {
                    "id": {"type": "integer"},
                    "items": {"type": "array", "items": {"$ref": "#/components/schemas/OrderItem"}}
                }
            },
            "OrderItem": {
                "properties": {
                    "product_id": {"type": "string"},
                    "quantity": {"type": "integer"}
                }
            }
        },
        "securitySchemes": {
            "OAuth2": {
                "type": "oauth2",
                "flows": {
                    "authorizationCode": {}
                }
            }
        }
    }
}

def demo_diagrams():
    print(colored("🎨 Diagram Generator Demo", "cyan", attrs=["bold"]))

    print(colored("\n1. Sequence Diagram (POST /orders)", "yellow"))
    seq = mermaid_generator.generate_sequence(SAMPLE_SPEC, "/orders", "post")
    print("-" * 40)
    print(seq)
    print("-" * 40)

    print(colored("\n2. ERD (Entity Relationships)", "yellow"))
    erd = mermaid_generator.generate_erd(SAMPLE_SPEC)
    print("-" * 40)
    print(erd)
    print("-" * 40)

    print(colored("\n3. Auth Flow (OAuth2)", "yellow"))
    auth = mermaid_generator.generate_auth_flow(SAMPLE_SPEC)
    print("-" * 40)
    print(auth)
    print("-" * 40)

if __name__ == "__main__":
    demo_diagrams()
