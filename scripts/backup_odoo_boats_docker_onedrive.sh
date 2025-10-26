#!/bin/sh
set -e
BACKUP_DIR=/mnt/c/Users/suram/OneDrive/Backups/odoo-boats_backup_$(date +"%Y%m%d_%H%M%S")
echo "$BACKUP_DIR"
mkdir -p "$BACKUP_DIR"

echo "Backing up Odoo DB+filestore..."
curl -s -X POST http://odoo-boats-app:8069/web/database/backup \
  -d "master_pwd=$ADMIN_PWD&backup_format=zip&name=odoo-boats-db" \
  -o "$BACKUP_DIR/odoo-boats-db.zip"

echo "Archiving configs and addons..."
tar czf "$BACKUP_DIR/odoo-boats-code.tar.gz" \
  odoo.conf docker-compose.yml Dockerfile custom-addons third_party_addons scripts

echo "Backup complete: $BACKUP_DIR"
