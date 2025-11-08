docker compose down -v

./gitty.sh

docker compose build --no-cache odoo-boats-app
docker compose up --force-recreate --remove-orphans odoo-boats-app
