
# 🧪 Comprehensive Feature Testing Guide

This guide walks you through testing every major feature of the **Enterprise API Integration Assistant (v1.0)** using the Public APIs and Sample Data you provided.

---

## 🏗️ 1. Setup & Data Preparation

First, let's populate your Knowledge Base with high-quality sample data.

### Step 1: Download Sample OpenAPI Specs
We have created a helper script to fetch standard specs (Petstore, Museum API).
```powershell
uv run python scripts/download_test_data.py
```
*   **Result**: Creates a `test_data/` folder containing `petstore.json`, `museum.yaml`, etc.

### Step 2: Ingest Data via CLI (Feature: Batch Ingestion)
Process the downloaded specs into the Vector Database.
```powershell
uv run python backend/cli.py batch ./test_data
```
*   **Verify**: You should see logs like `✅ Ingested: petstore.json`.

### Step 3: Restart Backend Server ⚠️
**Crucial Step**: Since the CLI tool runs in a separate process, you must restart your running backend API so it loads the new data into memory.
1.  Go to the terminal running `uv run main.py`.
2.  Press `Ctrl+C` to stop it.
3.  Run `uv run main.py` again.
4.  Wait for "✅ BM25 Index Built..." log.

---

## 🔍 2. Testing Search & Retrieval (Hybrid Search)

**Goal**: Verify the system can find relevant API details using semantic meaning + keywords.

### Scenario A: CLI Search
Find endpoints related to "tickets" in the Museum API.
```powershell
uv run python backend/cli.py search "how to buy tickets"
```
*   **Expected Output**: Should verify retrieval of `/tickets` endpoints from `museum.yaml`.

### Scenario B: Frontend UI Search
1.  Open [http://localhost:3000](http://localhost:3000).
2.  In the chat, ask:
    > "What are the endpoints for buying museum tickets?"
3.  **Verify**: The Assistant should cite `museum.yaml` and list the endpoints.

---

## 🤖 3. Testing Code Generation (Agentic RAG)

**Goal**: Verify the agent can write working code for a specific API.

### Scenario: JSONPlaceholder (No-Auth API)
Use a real public API to test the agent's ability to browse and code.

1.  **Prompt**:
    > "I want to use the JSONPlaceholder API (https://jsonplaceholder.typicode.com). Write a Python script to fetch all users and then find the posts for the user 'Bret'."
2.  **Observation**:
    *   **Research**: Agent should scrape the URL to understand the schema (`/users`, `/posts`).
    *   **Plan**: It should outline a plan (Fetch users -> Find ID -> Fetch posts).
    *   **Code**: It should generate a `requests` based script.
    *   **Self-Correction**: If it makes a mistake (e.g., wrong ID field), the critic might catch it (simulated).

---

## 📊 4. Testing Diagrams (Mermaid Generation)

**Goal**: Verify the system can visualize API architectures.

### Scenario: Petstore Sequence Diagram
Visualize the "Add Pet" flow.
```powershell
uv run python backend/cli.py diagram ./test_data/petstore.json --type sequence --path /pet --method POST > pet_flow.mermaid
```
*   **Verify**: Open `pet_flow.mermaid` (or paste content into [Mermaid Live](https://mermaid.live)). It should show `User -> API -> Backend`.

### Scenario: Schema ERD
Visualize the data model of the Museum.
```powershell
uv run python backend/cli.py diagram ./test_data/museum.yaml --type erd
```
*   **Verify**: Output should show entities like `Museum`, `Ticket`, `Event` and their relationships.

---

## 👥 5. Testing Multi-User Sessions

**Goal**: Verify that context is saved and isolated between users.

### Scenario: "Alice vs Bob" (CLI)
1.  **Create Session for Alice**:
    ```powershell
    uv run python backend/cli.py session create --user-id alice
    ```
    *(Copy the Session ID, e.g., `abc-123`)*

2.  **Chat as Alice**:
    ```powershell
    uv run python backend/cli.py session chat abc-123
    > "My name is Alice. I like Python."
    ```

3.  **Create Session for Bob**:
    ```powershell
    uv run python backend/cli.py session create --user-id bob
    ```
    *(Copy the Session ID, e.g., `xyz-789`)*

4.  **Chat as Bob**:
    ```powershell
    uv run python backend/cli.py session chat xyz-789
    > "Who am I?"
    ```
    *   **Expected**: "I don't know your name yet." (Does NOT know Alice).

5.  **Return to Alice**:
    ```powershell
    uv run python backend/cli.py session chat abc-123
    > "Who am I?"
    ```
    *   **Expected**: "You are Alice." (Context Preserved).

---

## 🛠️ 6. Debugging & Parsers

**Goal**: Verify the parser logic without running the full DB ingest.

### Scenario: Parse a Postman Collection
If you have a Postman export (e.g., `MyCollection.json`):
```powershell
uv run python backend/cli.py parse ./MyCollection.json
```
*   **Verify**: Output should show chunks like `[Request] GET /login ...`.

---

## 🧹 Cleanup
To reset your database after testing:
```powershell
uv run python backend/cli.py reset
```
