
# 📊 Monitoring & Observability Guide

Effective monitoring ensures you know when the assistant is broken before your users do.

## 1. Core Metrics to Watch
| Metric | Source | Warning Threshold | Critical Threshold |
|---|---|---|---|
| **Uptime** | `/health` Endpoint | < 99.9% | DOWN |
| **Latency (p95)** | Middleware / Logs | > 2s | > 5s |
| **Error Rate** | HTTP 5xx | > 1% | > 5% |
| **Rate Limits** | HTTP 429 | > 5% | > 20% |
| **Vector DB** | Connectivity | Disconnected | - |

## 2. Setting Up Logging
### Docker Logs (Basic)
View real-time logs:
```bash
docker-compose logs -f --tail=100
```

### Centralized Logging (Recommended)
Forward Docker logs to a centralized system (ELK Stack, CloudWatch, Datadog).
**Example `daemon.json` config for AWS CloudWatch**:
```json
{
  "log-driver": "awslogs",
  "log-opts": {
    "awslogs-region": "us-east-1",
    "awslogs-group": "api-assistant"
  }
}
```

## 3. Uptime Monitoring
Use a specialized service to ping your health endpoint every 1-5 minutes.
- **Endpoint**: `https://api.yourdomain.com/health`
- **Services**: UptimeRobot, Pingdom, BetterStack.

## 4. Tracing (Advanced)
Since the app uses **LangChain** and **LangGraph**, you can enable **LangSmith** for deep tracing of agent thought processes.
1. Sign up for [LangSmith](https://smith.langchain.com/).
2. Add Env Vars:
   ```bash
   LANGCHAIN_TRACING_V2=true
   LANGCHAIN_API_KEY=your_key
   ```
This provides visibility into token usage, latency per node, and LLM inputs/outputs.
