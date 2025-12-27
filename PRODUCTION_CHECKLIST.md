
# 🚀 Production Readiness Checklist

Before going live, ensure all items are checked to guarantee stability, security, and performance.

## 1. Security 🛡️
- [ ] **Change Default Secrets**: Ensure `GROQ_API_KEY` and other keys are NOT committed to version control.
- [ ] **API Keys**: Rotate development keys; use production-only keys.
- [ ] **HTTPS**: Ensure SSL/TLS is enabled (e.g., via Nginx or Cloudflare).
- [ ] **Allowed Hosts**: Configure `ALLOWED_ORIGINS` in environment variables for CORS.
- [ ] **Debug Mode**: Set `DEBUG=False` (if applicable in framework settings) or ensure logs don't leak secrets.

## 2. Infrastructure 🏗️
- [ ] **Docker**: Ensure `docker-compose.yml` uses restart policies (`restart: always`).
- [ ] **Volumes**: Verify `chroma_data` volume is persistent and backed up.
- [ ] **Resources**: CPU/RAM limits configured if deploying to Kubernetes/ECS.
- [ ] **Scaling**: If running multiple replicas, ensure ChromaDB is externalized or handles concurrency (Default is SQLite-based, better for single instance).

## 3. Monitoring & Ops 📊
- [ ] **Logs**: Verify container logs are being collected (AWS CloudWatch, Datadog, or centralized logging).
- [ ] **Health Checks**: Configure uptime monitors (e.g., UptimeRobot) hitting `/health`.
- [ ] **Alerting**: Set up alerts for `5xx` errors.

## 4. Application 🧩
- [ ] **Migration**: Vector Store initialized? (Run a test ingestion).
- [ ] **Rate Limits**: Tune `slowapi` limits in `main.py` based on expected traffic.
- [ ] **Sanitization**: Confirm `bleach` is active.

## 5. Final Smoke Test 🧪
- [ ] **Deep Health Check**: `curl https://api.yoursite.com/health` returns `{"status": "ok"}`.
- [ ] **Chat Flow**: Test a full RAG query.
