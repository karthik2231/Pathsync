#!/bin/bash
set -e

# Extract environment bindings
if [ ! -f .env ]; then
  echo "=> Creating isolated local .env from .env.example"
  cp .env.example .env
fi

echo "=> Activating Docker Compose orchestration stack..."
docker-compose up --build -d

echo "=> Delaying hooks for Database ignition health checks (10s)..."
sleep 10

echo "=> Running Alembic Structure Migrations..."
docker-compose exec backend alembic upgrade head

echo "=> Bootstrapping Top-500 ESCO Local Taxonomy Vector Store Cache..."
docker-compose exec backend python -c "
import asyncio
from app.utils.esco import build_local_taxonomy_cache
asyncio.run(build_local_taxonomy_cache())
"

echo "========================================="
echo " SkillBridge Deployment Online!          "
echo " >> API Root executing via     8000      "
echo " >> Frontend mapped against Port 80      "
echo "========================================="
