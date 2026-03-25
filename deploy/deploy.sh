#!/usr/bin/env bash
# deploy/deploy.sh — Zero-downtime deployment script for Property Connect
# Run as: sudo -u propconnect bash deploy/deploy.sh
set -euo pipefail

APP_DIR="/var/www/propconnect"
BACKEND_DIR="$APP_DIR/backend"
FRONTEND_DIR="$APP_DIR/frontend"
VENV="$APP_DIR/venv"
LOG_DIR="/var/log/propconnect"
RUN_DIR="/var/run/propconnect"

echo "==> [$(date '+%Y-%m-%d %H:%M:%S')] Starting deployment"

# ── 1. Pull latest code ────────────────────────────────────────────────────────
echo "==> Pulling latest code from main branch"
git -C "$APP_DIR" fetch origin main
git -C "$APP_DIR" reset --hard origin/main

# ── 2. Backend dependencies ────────────────────────────────────────────────────
echo "==> Installing Python dependencies"
"$VENV/bin/pip" install --quiet -r "$BACKEND_DIR/requirements.txt"

# ── 3. Django: migrate + collectstatic ────────────────────────────────────────
echo "==> Running Django migrations"
DJANGO_SETTINGS_MODULE=config.settings.prod \
    "$VENV/bin/python" "$BACKEND_DIR/manage.py" migrate --noinput

echo "==> Collecting static files"
DJANGO_SETTINGS_MODULE=config.settings.prod \
    "$VENV/bin/python" "$BACKEND_DIR/manage.py" collectstatic --noinput --clear

# ── 4. Frontend build ──────────────────────────────────────────────────────────
echo "==> Installing frontend dependencies"
npm --prefix "$FRONTEND_DIR" ci --silent

echo "==> Building frontend"
npm --prefix "$FRONTEND_DIR" run build

# ── 5. Ensure log/run dirs exist ───────────────────────────────────────────────
mkdir -p "$LOG_DIR" "$RUN_DIR"

# ── 6. Reload services (graceful) ─────────────────────────────────────────────
echo "==> Reloading Gunicorn (zero-downtime)"
sudo systemctl reload gunicorn || sudo systemctl restart gunicorn

echo "==> Restarting Daphne"
sudo systemctl restart daphne

echo "==> Restarting Celery worker"
sudo systemctl restart celery

echo "==> Restarting Celery Beat"
sudo systemctl restart celerybeat

echo "==> Reloading Nginx"
sudo nginx -t && sudo systemctl reload nginx

echo "==> [$(date '+%Y-%m-%d %H:%M:%S')] Deployment complete ✓"
