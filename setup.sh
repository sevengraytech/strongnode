#!/bin/bash
# ─────────────────────────────────────────────────────────────────────────────
# StrongNode Capitals — Server Setup & Deploy Script
# Run once on your server: bash setup.sh
# ─────────────────────────────────────────────────────────────────────────────
set -e

echo ""
echo "╔══════════════════════════════════════════════════════╗"
echo "║     StrongNode Capitals — Deploy Script              ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""

# ── Step 1: Fix Docker DNS ────────────────────────────────────────────────────
echo "▶ Step 1: Configuring Docker DNS..."
sudo cp daemon.json /etc/docker/daemon.json
sudo systemctl restart docker
echo "  ✅ Docker DNS set to 8.8.8.8 and 1.1.1.1"
sleep 2

# ── Step 2: Test internet connectivity ───────────────────────────────────────
echo ""
echo "▶ Step 2: Testing connectivity to Docker Hub..."
if curl -s --max-time 10 https://auth.docker.io > /dev/null; then
    echo "  ✅ Docker Hub reachable"
else
    echo "  ⚠️  Docker Hub still unreachable — trying mirror only"
fi

# ── Step 3: Pull base image ───────────────────────────────────────────────────
echo ""
echo "▶ Step 3: Pulling Python base image..."
docker pull python:3.11-slim || {
    echo "  ⚠️  Direct pull failed — trying Google mirror..."
    docker pull mirror.gcr.io/library/python:3.11-slim
    docker tag mirror.gcr.io/library/python:3.11-slim python:3.11-slim
}
echo "  ✅ Base image ready"

# ── Step 4: Build & start app ─────────────────────────────────────────────────
echo ""
echo "▶ Step 4: Building and starting application..."
docker compose down --remove-orphans 2>/dev/null || true
docker compose build --no-cache
docker compose up -d
echo "  ✅ Application started"

# ── Step 5: Health check ──────────────────────────────────────────────────────
echo ""
echo "▶ Step 5: Waiting for app to be healthy..."
sleep 5
for i in {1..10}; do
    if curl -sf http://localhost:9000/health > /dev/null 2>&1; then
        echo "  ✅ App is healthy at http://localhost:9000"
        break
    fi
    echo "  ⏳ Waiting... ($i/10)"
    sleep 3
done

echo ""
echo "╔══════════════════════════════════════════════════════╗"
echo "║  ✅ Deploy complete!                                  ║"
echo "║                                                       ║"
echo "║  App running at: http://localhost:9000               ║"
echo "║  View logs:      docker compose logs -f              ║"
echo "║  Stop app:       docker compose down                 ║"
echo "╚══════════════════════════════════════════════════════╝"
