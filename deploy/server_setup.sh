#!/usr/bin/env bash
# deploy/server_setup.sh — One-time Ubuntu 22.04 server provisioning
# Run as root: bash deploy/server_setup.sh
set -euo pipefail

APP_USER="propconnect"
APP_DIR="/var/www/propconnect"
LOG_DIR="/var/log/propconnect"
RUN_DIR="/var/run/propconnect"
PYTHON_VERSION="3.13"

echo "==> Updating system packages"
apt-get update -y && apt-get upgrade -y

echo "==> Installing system dependencies"
apt-get install -y \
    git curl wget gnupg2 \
    python${PYTHON_VERSION} python${PYTHON_VERSION}-venv python${PYTHON_VERSION}-dev \
    build-essential libpq-dev \
    postgresql-17 postgresql-17-postgis-3 \
    redis-server \
    nginx certbot python3-certbot-nginx \
    nodejs npm \
    supervisor

# Install Node 20 via NodeSource
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt-get install -y nodejs

echo "==> Creating app user"
id -u $APP_USER &>/dev/null || useradd --system --create-home --shell /bin/bash $APP_USER

echo "==> Creating directories"
mkdir -p $APP_DIR $LOG_DIR $RUN_DIR
chown -R $APP_USER:$APP_USER $APP_DIR $LOG_DIR $RUN_DIR

echo "==> Setting up PostgreSQL"
sudo -u postgres psql -c "CREATE USER $APP_USER WITH PASSWORD 'CHANGE_ME';" 2>/dev/null || true
sudo -u postgres psql -c "CREATE DATABASE propconnect OWNER $APP_USER;" 2>/dev/null || true
sudo -u postgres psql -d propconnect -c "CREATE EXTENSION IF NOT EXISTS postgis;" 2>/dev/null || true

echo "==> Cloning repository"
sudo -u $APP_USER git clone https://github.com/YOUR_ORG/property-connect.git $APP_DIR || true

echo "==> Setting up Python virtual environment"
sudo -u $APP_USER python${PYTHON_VERSION} -m venv $APP_DIR/venv
sudo -u $APP_USER $APP_DIR/venv/bin/pip install --upgrade pip
sudo -u $APP_USER $APP_DIR/venv/bin/pip install -r $APP_DIR/backend/requirements.txt

echo "==> Installing systemd service files"
cp $APP_DIR/deploy/gunicorn.service   /etc/systemd/system/gunicorn.service
cp $APP_DIR/deploy/daphne.service     /etc/systemd/system/daphne.service
cp $APP_DIR/deploy/celery.service     /etc/systemd/system/celery.service
cp $APP_DIR/deploy/celerybeat.service /etc/systemd/system/celerybeat.service

systemctl daemon-reload
systemctl enable gunicorn daphne celery celerybeat
systemctl enable nginx redis-server postgresql

echo "==> Installing Nginx config"
cp $APP_DIR/deploy/nginx.conf /etc/nginx/sites-available/propconnect
ln -sf /etc/nginx/sites-available/propconnect /etc/nginx/sites-enabled/propconnect
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl reload nginx

echo "==> Allowing deploy user to reload services without password"
cat >> /etc/sudoers.d/propconnect << 'EOF'
propconnect ALL=(ALL) NOPASSWD: /bin/systemctl reload gunicorn
propconnect ALL=(ALL) NOPASSWD: /bin/systemctl restart gunicorn
propconnect ALL=(ALL) NOPASSWD: /bin/systemctl restart daphne
propconnect ALL=(ALL) NOPASSWD: /bin/systemctl restart celery
propconnect ALL=(ALL) NOPASSWD: /bin/systemctl restart celerybeat
propconnect ALL=(ALL) NOPASSWD: /bin/systemctl reload nginx
propconnect ALL=(ALL) NOPASSWD: /bin/nginx -t
EOF

echo ""
echo "==> Server setup complete. Next steps:"
echo "    1. Copy .env.example to /var/www/propconnect/.env and fill in all values"
echo "    2. Run: certbot --nginx -d belagaviproperty.com -d www.belagaviproperty.com"
echo "    3. Start services: systemctl start gunicorn daphne celery celerybeat"
echo "    4. Add GitHub secrets: DEPLOY_HOST, DEPLOY_USER, DEPLOY_SSH_KEY, VITE_API_BASE_URL, VITE_WS_URL"
