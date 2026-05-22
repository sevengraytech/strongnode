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

# ── Step 1: Configure Docker DNS + mirror ────────────────────────────────────
# daemon.json sets DNS (8.8.8.8 / 1.1.1.1) and registry mirror (mirror.gcr.io)
# The mirror is required on servers where Docker Hub is not directly reachable.
echo "▶ Step 1: Configuring Docker daemon (DNS + registry mirror)..."
sudo cp daemon.json /etc/docker/daemon.json
sudo systemctl restart docker
echo "  ✅ Docker daemon configured"
sleep 2

# ── Step 2: Test internet connectivity ───────────────────────────────────────
echo ""
echo "▶ Step 2: Testing internet connectivity..."
if curl -s --max-time 10 https://mirror.gcr.io > /dev/null 2>&1; then
    echo "  ✅ Registry mirror reachable (mirror.gcr.io)"
elif curl -s --max-time 10 https://auth.docker.io > /dev/null 2>&1; then
    echo "  ✅ Docker Hub reachable directly"
else
    echo "  ❌ Neither Docker Hub nor the registry mirror is reachable."
    echo "     Check your server's internet/firewall settings and retry."
    exit 1
fi

# ── Step 3: Pull base image ───────────────────────────────────────────────────
echo ""
echo "▶ Step 3: Pulling Python base image..."
docker pull python:3.11-slim
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
    if curl -sf http://localhost:8080/health > /dev/null 2>&1; then
        echo "  ✅ App is healthy at http://localhost:8081"
        break
    fi
    echo "  ⏳ Waiting... ($i/10)"
    sleep 3
done

echo ""
echo "╔══════════════════════════════════════════════════════╗"
echo "║  ✅ Deploy complete!                                  ║"
echo "║                                                       ║"
echo "║  App running at: http://localhost:8081               ║"
echo "║  View logs:      docker compose logs -f              ║"
echo "║  Stop app:       docker compose down                 ║"
echo "╚══════════════════════════════════════════════════════╝"
