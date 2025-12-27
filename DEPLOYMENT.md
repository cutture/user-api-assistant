
# 🚀 Deployment Guide: Development, QA, & Production

This project is containerized with Docker, making it easy to deploy to any environment (Local, VM, Cloud).

## 1. Prerequisites
- [Docker](https://docs.docker.com/get-docker/) & Docker Compose installed.

## 2. Configuration (Environment Variables)
The system uses `docker-compose.yml` which pulls configuration from environment variables.

| Variable | Description | Default | Example for Prod |
|---|---|---|---|
| `NEXT_PUBLIC_API_URL` | Browser-accessible URL of the backend (Where the API runs). | `http://localhost:8000` | `https://api.myapp.com` |
| `LLM_PROVIDER` | LLM Service (groq, ollama, openai). | `groq` | `groq` |
| `LLM_API_KEY` | API Key for the LLM. | (Required) | `gsk_...` |

## 3. Deployment Scenarios

### A. Local Development 💻
Just run:
```bash
docker-compose up --build
```
- Frontend: [http://localhost:3000](http://localhost:3000)
- Backend: [http://localhost:8000](http://localhost:8000)

### B. QA / Staging Server 🧪
On your QA VM (Linux/Windows):
1. **Clone Repo**:
   ```bash
   git clone <repo_url>
   cd api-assistant-antigravity
   ```
2. **Set Environment**:
   Create a `.env` file or export variables:
   ```bash
   export NEXT_PUBLIC_API_URL=http://192.168.1.50:8000  # VM IP Address
   export LLM_API_KEY=your_key_here
   ```
3. **Run**:
   ```bash
   docker-compose up -d --build
   ```

### C. Production (Cloud/VM) 🌍
1. **Security**: Ensure `debug` is off (managed via envs if added later). Use a reverse proxy (Nginx) for HTTPS.
2. **Set Domain**:
   ```bash
   export NEXT_PUBLIC_API_URL=https://api.yourdomain.com
   ```
3. **Deploy**:
   ```bash
   docker-compose up -d --build
   ```
4. **Scale** (Optional):
   You can run multiple replicas if you use a load balancer.

## 4. Verification
Run the health check from the host:
```bash
curl http://localhost:8000/health
```
(Status should be `ok`, services should be `healthy` in `docker ps`).
