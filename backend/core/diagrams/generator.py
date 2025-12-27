
from typing import Dict, Any, List

class MermaidGenerator:
    """
    Generates Mermaid.js diagram syntax from API Specifications.
    """

    def generate_sequence(self, spec: Dict[str, Any], path: str, method: str) -> str:
        """
        Generates a Sequence Diagram for a specific API Endpoint.
        User -> API -> Backend System
        """
        method = method.lower()
        paths = spec.get("paths", {})
        if path not in paths or method not in paths[path]:
            return f"Note right of API: Endpoint {method.upper()} {path} not found."

        details = paths[path][method]
        summary = details.get("summary", "API Call")
        
        # Build Diagram
        lines = ["sequenceDiagram", "autonumber"]
        lines.append(f"participant User")
        lines.append(f"participant API as API Gateway")
        lines.append(f"participant Backend as Service")

        # Request
        lines.append(f"User->>API: {method.upper()} {path}")
        lines.append(f"Note right of User: {summary}")
        
        # Headers/Params info
        params = details.get("parameters", [])
        if params:
            param_list = "<br/>".join([f"{p['name']} ({p.get('in', '?')})" for p in params])
            lines.append(f"Note right of User: Params:<br/>{param_list}")

        lines.append(f"API->>Backend: Process Request")
        
        # Response(s)
        responses = details.get("responses", {})
        for code, resp in responses.items():
            desc = resp.get("description", "Response")
            lines.append(f"Backend-->>API: {code} {desc}")
        
        lines.append(f"API-->>User: Final Response")
        
        return "\n".join(lines)

    def generate_erd(self, spec: Dict[str, Any]) -> str:
        """
        Generates an Entity Relationship Diagram (ERD) from OpenAPI Schemas.
        """
        schemas = spec.get("components", {}).get("schemas", {})
        if not schemas:
            return "erDiagram\n    Note: No schemas found."

        lines = ["erDiagram"]
        
        for name, schema in schemas.items():
            props = schema.get("properties", {})
            lines.append(f"    {name} {{")
            for prop_name, prop_details in props.items():
                prop_type = prop_details.get("type", "string")
                # Clean type for mermaid
                lines.append(f"        {prop_type} {prop_name}")
            lines.append("    }")
            
            # Estimate relationships (naive check for $ref)
            # This is hard without full crawling, but let's check basic props
            for prop_name, prop_details in props.items():
                ref = prop_details.get("$ref")
                if not ref and "items" in prop_details:
                     ref = prop_details["items"].get("$ref")
                
                if ref:
                    target = ref.split("/")[-1]
                    # Add relationship line: Entity ||--o{ Target
                    lines.append(f"    {name} ||--o{{ {target} : has")

        return "\n".join(lines)

    def generate_auth_flow(self, spec: Dict[str, Any]) -> str:
        """
        Generates a sequence diagram for the Authentication Flow.
        """
        security_schemes = spec.get("components", {}).get("securitySchemes", {})
        if not security_schemes:
            return "sequenceDiagram\nNote right of Client: No Security Schemes defined."
            
        lines = ["sequenceDiagram"]
        lines.append("participant Client")
        lines.append("participant API")
        lines.append("participant AuthServer")

        for name, scheme in security_schemes.items():
            scheme_type = scheme.get("type", "")
            lines.append(f"Note over Client, AuthServer: Scheme: {name} ({scheme_type})")
            
            if scheme_type == "oauth2":
                flows = scheme.get("flows", {})
                if "authorizationCode" in flows:
                     lines.append("Client->>AuthServer: 1. Request Auth Code")
                     lines.append("AuthServer-->>Client: 2. Return Code")
                     lines.append("Client->>AuthServer: 3. Exchange Code for Token")
                     lines.append("AuthServer-->>Client: 4. Return Access Token")
                elif "clientCredentials" in flows:
                     lines.append("Client->>AuthServer: 1. Request Token (Client Creds)")
                     lines.append("AuthServer-->>Client: 2. Return Access Token")
            
            elif scheme_type == "apiKey":
                loc = scheme.get("in", "header")
                key = scheme.get("name", "api_key")
                lines.append(f"Client->>API: Request + {loc}: {key}")
                lines.append("API->>API: Validate Key")
        
        return "\n".join(lines)

# Singleton
mermaid_generator = MermaidGenerator()
