#!/bin/sh
#set -euo pipefail

# project root = parent of scripts/
PROJECT_ROOT="$(cd "$(dirname "$0")"/.. && pwd)"
TS="$(date +%Y%m%d_%H%M%S)"
DIR="$PROJECT_ROOT/backups/odoo-boats_backup_${TS}"
mkdir -p "$DIR"

# get master password from env or odoo.conf
ADMIN_PWD="${ADMIN_PWD:-$(awk -F= '/^\s*admin_passwd/ {gsub(/[ "\047]/,"",$2); print $2}' "$PROJECT_ROOT/odoo.conf" || true)}"
[ -n "${ADMIN_PWD:-}" ] || { echo "admin password not found"; exit 1; }

echo "Backing up DB+filestore -> $DIR/odoo-boats-db.zip"
curl -sS -f -X POST http://localhost:8069/web/database/backup \
  -d "master_pwd=$ADMIN_PWD&backup_format=zip&name=odoo-boats-db" \
  -o "$DIR/odoo-boats-db.zip"

echo "Archiving code/config -> $DIR/odoo-boats-code.tar.gz"
tar -C "$PROJECT_ROOT" -czf "$DIR/odoo-boats-code.tar.gz" \
  --exclude='./backups' \
  odoo.conf docker-compose.yml Dockerfile custom-addons third_party_addons scripts

echo "Done -> $DIR"
ls -lh "$DIR"/*
