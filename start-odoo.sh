#!/bin/bash
set -e

TS=$(date +%Y%m%d_%H%M%S)
LOGFILE="/var/log/odoo/odoo_${TS}.log"

echo "Starting Odoo, logging to $LOGFILE"
exec odoo --config=/etc/odoo/odoo.conf --logfile="$LOGFILE"
