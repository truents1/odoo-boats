#!/bin/bash
set -e

# Use the ODOO_HOST environment variable set in docker-compose.yml
ODEL_HOST=${ODOO_HOST:-odoo-boats-app}

echo "--- Backup Job Started ---"
echo "Waiting for Odoo service at http://${ODEL_HOST}:8069 to be ready..."

# Wait up to 90 seconds for Odoo's web server to be reachable
for i in {1..45}; do
  if curl -s http://${ODEL_HOST}:8069/web/database/manager > /dev/null; then
    echo "Odoo is ready after $((i*2)) seconds. Running backup script."
    # Execute the actual backup script
    exec /usr/src/app/scripts/backup_odoo_boats_host.sh
    exit 0
  fi
  sleep 2
done

echo "Error: Odoo service did not start within the timeout. Backup aborted."
exit 1