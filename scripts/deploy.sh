
#!/bin/bash

# Simple Deployment Helper for Linux/Mac
# Usage: ./deploy.sh [prod|qa|dev]

ENV=${1:-dev}

echo "🚀 Deploying to Environment: $ENV"

if [ "$ENV" == "prod" ]; then
    export NEXT_PUBLIC_API_URL="https://api.yourdomain.com"
    # export LLM_API_KEY="..." # Ideally set in CI/CD or server env
elif [ "$ENV" == "qa" ]; then
    export NEXT_PUBLIC_API_URL="http://your-qa-ip:8000"
else
    # Dev
    export NEXT_PUBLIC_API_URL="http://localhost:8000"
fi

echo "   API URL: $NEXT_PUBLIC_API_URL"

# Build and Run
echo "📦 Building containers..."
docker-compose up -d --build --remove-orphans

# Health Check
echo "🩺 Waiting for service..."
sleep 10
status=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health)

if [ "$status" == "200" ]; then
    echo "✅ Deployment Successful! Backend is healthy."
else
    echo "⚠️ Deployment completed, but Health Check returned $status. Please check logs."
fi
