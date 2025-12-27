
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), "../backend"))

from core.parsers.factory import parser_factory
from termcolor import colored

def demo_parsing():
    print(colored("🧩 Advanced Parsing Strategy Demo", "cyan", attrs=["bold"]))
    
    # 1. GraphQL Demo
    print(colored("\n1. GraphQL Parsing (.graphql)", "yellow"))
    gql_content = """
    type User {
        id: ID!
        username: String
        email: String
    }
    
    type Query {
        me: User
    }
    """
    parser = parser_factory.get_parser(".graphql")
    if parser:
        chunks = parser.parse(gql_content)
        for i, c in enumerate(chunks):
            print(f"[{i+1}] {c[:50]}...")
            
    # 2. Postman Demo
    print(colored("\n2. Postman Parsing (JSON)", "yellow"))
    postman_content = {
        "info": {"name": "Demo Collection"},
        "item": [
            {
                "name": "Auth",
                "item": [
                    {
                        "name": "Login",
                        "request": {
                            "method": "POST",
                            "url": "https://api.example.com/login",
                            "description": "User login endpoint"
                        }
                    }
                ]
            }
        ]
    }
    parser = parser_factory.get_parser("application/vnd.postman.collection+json")
    if parser:
        chunks = parser.parse(postman_content)
        for i, c in enumerate(chunks):
            print(f"[{i+1}] {c}")

if __name__ == "__main__":
    demo_parsing()
