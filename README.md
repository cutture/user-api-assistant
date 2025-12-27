
# 🚀 Enterprise API Integration Assistant

An **Agentic AI System** designed to act as a **Software Architect**, **Researcher**, and **Coder** for complex API integration tasks.

![License](https://img.shields.io/badge/license-MIT-blue)
![Python](https://img.shields.io/badge/python-3.12-blue)
![Next.js](https://img.shields.io/badge/next.js-14-black)
![Status](https://img.shields.io/badge/status-v1.0.0-green)

## ✨ Logic & Features

### 🧠 Core Intelligence
*   **Multi-Agent Mesh**: Powered by **LangGraph**, orchestrating Retrieval, Planning, Coding, and Review agents.
*   **Hybrid Retrieval (RAG)**: Precision search using **ChromaDB** (Vector) + **BM25** (Keyword) + **RRF** (Reciprocal Rank Fusion) + **MMR** (Maximal Marginal Relevance) for diversity.
*   **Self-Healing**: Agents detect errors, critique their own code, and retry automatically.

### 🏢 Enterprise Capabilities
*   **Multi-Format Parsing**: Ingests **OpenAPI (Swagger)**, **GraphQL Schemas**, **Postman Collections**, and PDF/Docx documentation.
*   **Architecture Visualization**: Auto-generates **Mermaid.js** diagrams (Sequence, ERD, Auth Flows) to explain the system.
*   **Session Management**: Stateful, multi-user conversations with context retention across sessions.
*   **Advanced CLI**: robust command-line interface for managing the knowledge base, debugging parsers, and running batch ingestions.

### 🛠️ Tech Stack
*   **Backend**: Python 3.12, FastAPI, LangGraph, ChromaDB, Typer.
*   **Frontend**: Next.js 14, TailwindCSS, Mermaid.js, Lucide Icons.
*   **LLM Support**: Groq (Llama 3, Qwen 2.5), Ollama (Local), OpenAI compatible.

---

## 🚀 Getting Started

### Prerequisites
*   [uv](https://github.com/astral-sh/uv) (Python Manager)
*   Node.js 20+
*   Git

### 1. Installation
```bash
git clone https://github.com/your-org/api-assistant.git
cd api-assistant
uv sync
cd frontend && npm install
```

### 2. Configuration
```bash
cp .env.example .env
# Edit .env with your API Keys (GROQ_API_KEY, etc.)
```

### 3. Run Application
**Backend**:
```bash
uv run main.py
```
**Frontend**:
```bash
cd frontend
npm run dev
```
Visit `http://localhost:3000` to chat.

---

## 💻 CLI Tool
Manage your Knowledge Base directly from the terminal.

```bash
# Search Docs
python backend/cli.py search "authentication flow"

# Generate Diagram
python backend/cli.py diagram openapi.json --type sequence --path /login

# Batch Ingest
python backend/cli.py batch ./my-docs/

# Interactive Session
python backend/cli.py session create
python backend/cli.py session chat <session_id>
```

---

## 📊 Features in Detail

| Feature | Description | Status |
| :--- | :--- | :--- |
| **Hybrid Search** | Semantic + Keyword search with Reranking | ✅ v1.0 |
| **Advanced Filtering** | Filter by metadata, source, date | ✅ v1.0 |
| **Resilience** | Circuit Breakers, Retry logic, Fallbacks | ✅ v1.0 |
| **Visualizations** | Mermaid Sequence & ER Diagrams | ✅ v1.0 |
| **Multi-User** | Session isolation & history persistence | ✅ v1.0 |
| **Parsing** | OpenAPI, GraphQL, Postman, PDF, Docx | ✅ v1.0 |

---

## 🤝 Contributing
Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct, and the process for submitting pull requests.

## 📄 License
This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.
