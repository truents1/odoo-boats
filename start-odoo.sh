#!/bin/bash
set -e

# This script is now clean and only focuses on starting Odoo with dynamic logging.

TS=$(date +%Y%m%d_%H%M%S)
LOGFILE="/var/log/odoo/odoo_${TS}.log"

echo "Starting Odoo, logging to $LOGFILE"
# The 'exec' command replaces the current shell with the odoo process
exec odoo --config=/etc/odoo/odoo.conf --logfile="$LOGFILE"