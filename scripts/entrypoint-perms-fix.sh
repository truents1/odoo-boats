#!/bin/bash
set -e

# Odoo typically runs as user 'odoo'. We force the ownership of the mounted volumes to this user.
echo "Fixing permissions on mounted volumes..."
chown -R odoo:odoo /var/lib/odoo/.local
chown -R odoo:odoo /var/log/odoo
chown -R odoo:odoo /usr/src/app/backups

echo "Starting original Odoo script..."
# Now run the Odoo startup script
exec /start-odoo.sh