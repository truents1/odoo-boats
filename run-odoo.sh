#!/bin/bash
set -e

# 1. Start Odoo (and wait for DB to be ready)
echo "Starting Odoo services in detached mode..."
docker compose up #-d

# 2. Wait for the Odoo App service to report 'healthy'
echo "Waiting for odoo-boats-app service to report 'healthy' (may take a minute)..."
docker compose wait odoo-boats-app #--timeout 120

# Check the exit status of 'docker compose wait'
if [ $? -ne 0 ]; then
    echo "Error: Odoo app service did not become healthy within the timeout."
    exit 1
fi

echo "Odoo app is ready and accessible."

# 3. Run the host backup script
echo "Running host backup script..."
/home/anil/odoo-boats/scripts/backup_odoo_boats_host.sh

echo "Startup and Backup process complete."