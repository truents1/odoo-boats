#!/bin/bash
set -e

# Get the actual user's home directory
if [ -n "$SUDO_USER" ]; then
    USER_HOME=$(getent passwd "$SUDO_USER" | cut -d: -f6)
else
    USER_HOME="$HOME"
fi

PROJECT_DIR="$USER_HOME/odoo-boats"

echo "📍 Working directory: $PROJECT_DIR"
echo "🛑 Stopping containers..."
cd "$PROJECT_DIR"
docker compose down

echo "🧹 Cleaning old directories..."
rm -rf "$PROJECT_DIR/odoo-local"/*
rm -rf "$PROJECT_DIR/logs"/*

echo "📁 Creating fresh directories..."
mkdir -p "$PROJECT_DIR/odoo-local/share/Odoo/sessions"
mkdir -p "$PROJECT_DIR/logs"
mkdir -p "$PROJECT_DIR/filestore"

echo "🔧 Setting ownership to UID 101 (odoo user)..."
chown -R 101:101 "$PROJECT_DIR/odoo-local"
chown -R 101:101 "$PROJECT_DIR/logs"
chown -R 101:101 "$PROJECT_DIR/filestore"

echo "🔑 Setting permissions..."
chmod -R 755 "$PROJECT_DIR/odoo-local"
chmod -R 755 "$PROJECT_DIR/logs"
chmod -R 755 "$PROJECT_DIR/filestore"

echo "✅ Verifying ownership..."
ls -la "$PROJECT_DIR/" | grep -E "odoo-local|logs|filestore"

echo "🚀 Starting containers..."
cd "$PROJECT_DIR"
docker compose up -d

echo "⏳ Waiting for startup..."
sleep 10

echo "📋 Checking logs..."
docker logs --tail 30 odoo-boats-app

echo ""
echo "✅ Done! Access Odoo at: http://localhost:8069"
