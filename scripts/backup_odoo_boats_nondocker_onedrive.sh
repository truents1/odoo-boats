#!/bin/bash
set -e

# CONFIGURATION
APP_SRC="/home/anil/odoo-boats"
WIN_BACKUP_ROOT="/mnt/c/Users/suram/OneDrive/Backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
TMP_DIR="/tmp/odoo-backup-$TIMESTAMP"
ARCHIVE_NAME="odoo-backup-${TIMESTAMP}.tar.gz"
DB_CONTAINER=$(docker ps --filter "name=odoo-boats-db" --format "{{.Names}}" | head -n1)
DB_NAME="odoo-boats-db"
DB_USER="odoo"
DB_PASSWORD="odoo"

# Create temporary workspace
mkdir -p "$TMP_DIR"

echo "📁 Copying app files from $APP_SRC..."
rsync -a --exclude='__pycache__' --exclude='*.log' --exclude='.cache' "$APP_SRC/" "$TMP_DIR/odoo-boats"

echo "🗄️ Dumping PostgreSQL database from container $DB_CONTAINER..."
docker exec -e PGPASSWORD="$DB_PASSWORD" "$DB_CONTAINER" pg_dump -U "$DB_USER" -Fc "$DB_NAME" > "$TMP_DIR/${DB_NAME}.dump"

echo "📦 Compressing backup into $ARCHIVE_NAME..."
tar -czf "$WIN_BACKUP_ROOT/$ARCHIVE_NAME" -C "/tmp" "odoo-backup-$TIMESTAMP"

echo "🧹 Cleaning up temporary files..."
rm -rf "$TMP_DIR"

echo "✅ Backup saved to: $WIN_BACKUP_ROOT/$ARCHIVE_NAME"
