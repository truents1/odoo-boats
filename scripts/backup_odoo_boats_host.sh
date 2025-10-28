#!/bin/sh
#set -euo pipefail

# This script performs the critical backup of the database AND filestore
# using the Odoo API, saving the result as a single ZIP file.

# project root = parent of the 'scripts/' folder
PROJECT_ROOT="."
TS="$(date +%Y%m%d_%H%M%S)"
BACKUP_DIR="$PROJECT_ROOT/backups" # This now resolves to ./backups (which is mounted)
DB_NAME="odoo-boats-db"

# Create the backups directory if it doesn't exist
# mkdir -p "$BACKUP_DIR"

# Define the final output filename (DB and Filestore)
OUTPUT_FILE="$BACKUP_DIR/${DB_NAME}_${TS}.zip"

# get master password from env or odoo.conf
ADMIN_PWD="${ADMIN_PWD:-$(awk -F= '/^\s*admin_passwd/ {gsub(/[ "\047]/,"",$2); print $2}' "$PROJECT_ROOT/odoo.conf" || true)}"
[ -n "${ADMIN_PWD:-}" ] || { echo "admin password not found"; exit 1; }

echo "Backing up DB and Filestore to -> $OUTPUT_FILE"

# The Odoo API backup creates a single ZIP containing both DB dump and filestore/ folder.
curl -sS -f -X POST http://localhost:8069/web/database/backup \
  -d "master_pwd=$ADMIN_PWD&backup_format=zip&name=$DB_NAME" \
  -o "$OUTPUT_FILE"

# --- Archiving Code (Optional, but Good Practice) ---
# It's good practice to archive the code and config that corresponds to the data backup.
CODE_ARCHIVE="$BACKUP_DIR/odoo-boats-code_${TS}.tar.gz"

echo "Archiving code/config to -> $CODE_ARCHIVE"
tar -C "$PROJECT_ROOT" -czf "$CODE_ARCHIVE" \
  --exclude='./backups' \
  odoo.conf docker-compose.yml Dockerfile custom-addons third_party_addons scripts

# --- FINAL CHECK ---
echo "Backup Complete:"
ls -lh "$OUTPUT_FILE" "$CODE_ARCHIVE"

WIN_BACKUP_DIR="/mnt/c/Users/suram/OneDrive/Backups/odoo"
echo "Copying backups to Windows OneDrive folder..."
echo "$WIN_BACKUP_DIR/"
cp "$OUTPUT_FILE" "$CODE_ARCHIVE" "$WIN_BACKUP_DIR/"