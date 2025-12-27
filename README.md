# 🚀 Enterprise API Integration Assistant

An **Agentic AI System** designed to help enterprise developers integrate complex APIs. It goes beyond simple code generation by acting as a **Software Architect**, **Researcher**, and **Coder** in one loop.

![License](https://img.shields.io/badge/license-MIT-blue)
![Python](https://img.shields.io/badge/python-3.12-blue)
![Next.js](https://img.shields.io/badge/next.js-14-black)

## ✨ Key Features

### 🧠 Core Intelligence
*   **Multi-Agent Architecture**: Powered by **LangGraph**, separating concerns into Retrieval, Planning, Coding, and Validation agents.
*   **Hybrid Retrieval (RAG)**: Combines **ChromaDB** (local vector store) with **DuckDuckGo** (web search) and **URL Scraping**.
*   **Proactive Gap Analysis**: If requirements are vague, the agent asks clarifying questions instead of guessing.

### 🏢 Enterprise Capabilities
*   **Self-Correction Loop**: Validates generated code using an LLM critic, automatically fixing errors before showing the result.
*   **Architecture Visualization**: Generates **Mermaid.js** sequence diagrams to visualize the integration flow.
*   **Interactive Playground**: Auto-generates a mini React app (`APITester.tsx`) to test the API endpoints immediately.
*   **SDK Mode**: Generates full production-grade Client Libraries (Classes + Pydantic Models) when requested.

### 🛠️ Tech Stack
*   **Backend**: Python, FastAPI, LangGraph, LangChain, ChromaDB.
*   **Frontend**: Next.js 14, TailwindCSS, Shadcn UI, Mermaid.js.
*   **LLM Providers**: Groq (Llama 3, Qwen 2.5), Ollama (Local Fallback).
*   **DevOps**: Docker, GitHub Actions (CI/CD).

---

## 🚀 Getting Started

### Prerequisites
*   [uv](https://github.com/astral-sh/uv) (for Python dependency management)
*   Node.js 20+
*   Git

### 1. Clone & Setup
```bash
git clone https://github.com/your-username/api-assistant.git
cd api-assistant

# Install Backend Dependencies
uv sync

# Install Frontend Dependencies
cd frontend
npm install
```

### 2. Environment Configuration
Create a `.env` file in the root directory:
```bash
cp .env.example .env
```
Fill in your keys:
```env
GROQ_API_KEY=gsk_...
LLM_PROVIDER=groq
CHROMA_PATH=./chroma_db
```

### 3. Run Locally (Development)
You need two terminals:

**Backend:**
```bash
# In project root
uv run uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
# OR simply
uv run main.py
```

**Frontend:**
```bash
cd frontend
npm run dev
```
Visit `http://localhost:3000` to chat.

---

## 🐳 Docker Deployment

To run the entire stack with Docker Compose:

```bash
docker-compose up --build
```
*   Frontend: `http://localhost:3000`
*   Backend: `http://localhost:8000`

---

## 🧪 CI/CD
A GitHub Actions workflow (`.github/workflows/ci.yml`) is configured to:
1.  Run static analysis on the Python backend.
2.  Build the Next.js frontend to ensure no build errors.

---

## 📚 Usage Guide

### Intelligent Context
*   **Upload Docs**: Drag & Drop PDF/Word/JSON files to the sidebar.
*   **Paste URLs**: The agent will scrape them for fresh context.
*   **Web Search**: "Find the latest Stripe API docs..." will trigger a live web search.

### Advanced Commands
*   **"Generate an SDK..."**: Triggers the `Client` class generator with Pydantic models.
*   **"Draw a diagram..."**: (or any complex plan) will auto-generate a generic Sequence Diagram.

---

## 🤝 Contributing
1.  Fork the repo
2.  Create a feature branch
3.  Submit a Pull Request
