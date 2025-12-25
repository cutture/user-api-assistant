# Enterprise API Integration Assistant

An AI-powered assistant to help developers understand, document, and generate code for enterprise API integrations.

## 🚀 Architecture: "The Agentic Mesh"
- **Orchestrator**: LangGraph (Stateful Agent Management)
- **Brain**: DeepSeek R1 / Qwen 2.5 (via Groq) + Gemini 1.5 Flash
- **Memory**: ChromaDB (Local Vector Store)
- **Data Layer**: MCP (Model Context Protocol) for Kaggle Dataset

## 🛠️ Prerequisites
- Python 3.10+
- Node.js 18+
- `uv` (pip replacement)
- Ollama (Optional, for local inference)

## 📂 Structure
- `/backend`: FastAPI + LangGraph Agents
- `/frontend`: Next.js + Shadcn UI
- `/mcp_server`: Model Context Protocol server for API Docs
- `/data`: Kaggle Dataset & ChromaDB
- `/scripts`: Ingestion & Setup Utilities

## ⚡ Quick Start

### 1. Environment Setup
```bash
# Install dependencies
cd backend
uv sync
```

### 2. Run the Backend
```bash
cd backend
uv run main.py
```

### 3. Run the Frontend
```bash
cd frontend
npm install
npm run dev
```
