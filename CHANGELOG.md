
# Changelog

All notable changes to this project will be documented in this file.

## [1.0.0] - 2025-12-27

### 🚀 Major Features
- **Hybrid Retrieval Engine**: Implemented a sophisticated search capability combining Vector Search (ChromaDB) and Keyword Search (BM25) with Reciprocal Rank Fusion (RRF).
- **Result Diversification**: Added Maximal Marginal Relevance (MMR) re-ranking to reduce redundancy in retrieved context.
- **Advanced Parsers**:
    - **GraphQL**: Native parsing of `.graphql` schemas and IDL.
    - **Postman**: Recursively parses Postman Collections v2.1.
    - **OpenAPI**: Optimized chunking for Swagger/OpenAPI specs.
- **Diagram Generation**: capability to auto-generate Mermaid.js Sequence Diagrams and Entity Relationship Diagrams (ERDs) from API specs.
- **Stateful Sessions**: Introduced `SessionManager` and API endpoints for multi-turn, multi-user chat persistence.
- **CLI Tool**: A comprehensive `typer` based CLI for management, debugging, and batch operations.

### 🛠️ Infrastructure & Resilience
- **Resilience Layer**: Added `@retry` decorators with exponential backoff and Circuit Breaker patterns for LLM and Scraper calls.
- **Caching**: Implemented TTL and Semantic Caching for LLM responses to reduce latency and cost.
- **Security**: Added `slowapi` rate limiting and input sanitization middleware.
- **Docker**: Optimized multi-stage builds for Backend and Standalone builds for Next.js Frontend.

### 🐛 Fixes & Polish
- Fixed singleton import issues in `SessionManager`.
- Standardized error handling with custom `AppError` hierarchy.
- Improved logging and monitoring hooks.
