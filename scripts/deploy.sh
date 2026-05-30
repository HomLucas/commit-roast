#!/bin/bash
set -e

echo "Deploying Flight Scanner..."

if [ ! -f .env ]; then
    echo "ERROR: .env file not found!"
    echo "Please copy .env.example to .env and fill in your credentials"
    exit 1
fi

echo "Checking for exposed secrets..."
if grep -q "sk-[a-zA-Z0-9]" .env 2>/dev/null; then
    echo "Warning: Potential API keys found in .env file"
fi

if [ -d .git ]; then
    echo "Pulling latest changes..."
    git pull origin main
fi

echo "Building containers..."
docker-compose build --no-cache

echo "Starting services..."
docker-compose up -d

echo "Waiting for services to be ready..."
sleep 10

echo "Running database migrations..."
docker-compose exec backend alembic upgrade head

echo "Checking service health..."
curl -f http://localhost:8000/api/health || echo "Warning: Backend health check failed"

echo "Deployment complete!"
echo "Frontend: http://localhost:3000"
echo "API: http://localhost:8000"
echo "API Docs: http://localhost:8000/api/docs"
