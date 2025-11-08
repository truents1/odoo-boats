./gitty.sh

docker compose down
docker compose build --no-cache odoo-boats-app
docker compose up --force-recreate --remove-orphans odoo-boats-app
