
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

def configure_security(app: FastAPI):
    """
    Applies security middlewares and configurations.
    """
    
    # 1. CORS Configuration
    # In Prod, this should be restricted to specific domains
    allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 2. Security Headers (Simulated via Middleware for now)
    # Ideally handled by Nginx/Cloudflare, but good to have application-level backup.
    @app.middleware("http")
    async def add_security_headers(request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response
