docker compose down
sudo git add . -v
sudo git commit -m "updated changes" -v
git pull origin main -v
git push origin main -v

#git -C odoo-boats pull
#docker compose build --no-cache odoo-boats-app 
#docker compose up --force-recreate --remove-orphans odoo-boats-app

