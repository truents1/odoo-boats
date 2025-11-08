#!/bin/bash
# Complete Odoo cleanup script

echo "Stopping Odoo..."
docker stop odoo-boats-app

echo "Cleaning database assets..."
docker exec -it odoo-boats-db psql -U odoo -d odoo-boats-db << 'EOSQL'
DELETE FROM ir_attachment WHERE name LIKE '%assets_%';
DELETE FROM ir_attachment WHERE name LIKE 'web.assets%';
DELETE FROM ir_ui_view WHERE type = 'qweb' AND key LIKE '%assets%';
VACUUM FULL ir_attachment;
EOSQL

echo "Cleaning filestore..."
rm -rf ~/odoo-boats/filestore/*

echo "Cleaning cache..."
rm -rf ~/odoo-boats/odoo-local/share/Odoo/sessions/*

echo "Cleaning Python cache..."
find ~/odoo-boats/custom-addons -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find ~/odoo-boats/custom-addons -type f -name "*.pyc" -delete 2>/dev/null

echo "Starting Odoo..."
docker start odoo-boats-app

echo "Waiting for startup..."
sleep 15

echo "Regenerating assets..."
docker exec -u odoo odoo-boats-app odoo \
  -c /etc/odoo/odoo.conf \
  -d odoo-boats-db \
  --update=base,web,website \
  --stop-after-init

echo "Final restart..."
docker restart odoo-boats-app

echo "Done! Wait 10 seconds then access: http://localhost:8069"
