#!/bin/sh
#set -euo pipefail

# This script performs the critical backup of the database AND filestore
# using the Odoo API, saving the result as a single ZIP file.

PROJECT_ROOT="/home/anil/odoo-boats"
WIN_BACKUP_DIR="/mnt/c/Users/suram/OneDrive/Backups/odoo"

TS="$(date +%Y%m%d_%H%M%S)"
BACKUP_DIR="$PROJECT_ROOT/backups" # This now resolves to ./backups (which is mounted)
DB_NAME="odoo-boats-db"
mkdir -p "$BACKUP_DIR"
DB_OUTPUT_FILE="$BACKUP_DIR/${DB_NAME}_${TS}.zip"
CODE_OUTPUT_FILE="$BACKUP_DIR/odoo-boats-code_${TS}.tar.gz"

# get master password from env or odoo.conf
ADMIN_PWD="${ADMIN_PWD:-$(awk -F= '/^\s*admin_passwd/ {gsub(/[ "\047]/,"",$2); print $2}' "$PROJECT_ROOT/odoo.conf" || true)}"
[ -n "${ADMIN_PWD:-}" ] || { echo "admin password not found"; exit 1; }

echo "Backing up DB and Filestore to -> $DB_OUTPUT_FILE"
curl -sS -f -X POST http://localhost:8069/web/database/backup \
  -d "master_pwd=$ADMIN_PWD&backup_format=zip&name=$DB_NAME" \
  -o "$DB_OUTPUT_FILE"

echo "Archiving code/config to -> $CODE_OUTPUT_FILE"
tar -C "$PROJECT_ROOT" -czf "$CODE_OUTPUT_FILE" \
  --exclude='./backups' \
  odoo.conf docker-compose.yml Dockerfile custom-addons third_party_addons scripts

# --- FINAL CHECK ---
echo "Backup Complete:"
ls -lha "$DB_OUTPUT_FILE" "$CODE_OUTPUT_FILE"

echo "Copying backups to Windows OneDrive folder..."
echo "$WIN_BACKUP_DIR/"
cp "$DB_OUTPUT_FILE" "$CODE_OUTPUT_FILE" "$WIN_BACKUP_DIR/"
