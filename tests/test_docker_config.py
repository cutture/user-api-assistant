
import os
import yaml

def test_backend_dockerfile_structure():
    """Verify Dockerfile.backend uses multi-stage and healthchecks."""
    assert os.path.exists("Dockerfile.backend")
    with open("Dockerfile.backend", "r") as f:
        content = f.read()
        
    # Check Multi-Stage
    assert "FROM ghcr.io/astral-sh/uv" in content
    assert "AS builder" in content
    assert "FROM python:3.12" in content
    
    # Check Healthcheck
    assert "HEALTHCHECK" in content
    assert "--interval=30s" in content
    
def test_frontend_dockerfile_structure():
    """Verify Frontend Dockerfile uses standalone mode and wget."""
    assert os.path.exists("frontend/Dockerfile")
    with open("frontend/Dockerfile", "r") as f:
        content = f.read()
        
    assert "AS runner" in content
    assert "standalone" in content
    assert "apk add --no-cache wget" in content
    assert "HEALTHCHECK" in content

def test_docker_compose_config():
    """Verify docker-compose.yml has healthchecks and volumes."""
    assert os.path.exists("docker-compose.yml")
    with open("docker-compose.yml", "r") as f:
        config = yaml.safe_load(f)
        
    services = config.get("services", {})
    assert "backend" in services
    assert "frontend" in services
    
    # Check Healthchecks
    assert "healthcheck" in services["backend"]
    assert "healthcheck" in services["frontend"]
    
    # Check Backend Volumes
    volumes = services["backend"].get("volumes", [])
    has_chroma = any("chroma" in v for v in volumes)
    assert has_chroma, "Backend must mount chroma volume"

def test_dockerignore():
    """Verify .dockerignore excludes critical files."""
    assert os.path.exists(".dockerignore")
    with open(".dockerignore", "r") as f:
        content = f.read()
        
    assert "node_modules/" in content
    assert ".env" in content
    assert "venv/" in content
