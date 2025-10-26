## Project snapshot for AI coding agents

This repository is an Odoo deployment containing several custom addons (see `custom-addons/`) and a local Docker-based runtime. The guidance below is intentionally concise and actionable so an AI coding agent can be immediately productive.

Key files and locations
- `docker-compose.yml` — defines two services: `odoo-boats-db` (Postgres) and `odoo-boats-app` (Odoo). Use these exact service names when running or exec-ing into containers.
- `odoo.conf` — Odoo configuration (DB credentials, `addons_path`, `data_dir`). NOTE: credentials are present in this file and are discoverable.
- `custom-addons/` — primary place for local addons (each addon follows Odoo patterns: `__manifest__.py`, `models/`, `controllers/`, `views/`, `security/`).
- `third_party_addons/` — vendor addons mounted into the instance.
- `filestore/` — persistent Odoo filestore mapped into the container.

How the system is wired (big picture)
- Docker Compose brings up a Postgres DB and the Odoo app container. The app mounts `custom-addons` and `third_party_addons` into `/mnt/extra-addons/custom` and `/mnt/extra-addons/third-party` respectively (see `docker-compose.yml`).
- Odoo's `addons_path` in `odoo.conf` references those mount points; module discovery and load order are controlled by each addon's `__manifest__.py` and dependency entries there.
- Controllers under `controllers/` expose HTTP endpoints; models in `models/` define business logic and ORM mappings; `security/ir.model.access.csv` controls access.

Common developer workflows (concrete commands)
- Start services (recommended):

```powershell
# from repository root (powershell)
docker compose up -d
# or if docker-compose binary used:
docker-compose up -d
```

- Tail logs or debug:

```powershell
docker compose logs -f odoo-boats-app
docker compose logs -f odoo-boats-db
```

- Enter the Odoo app container and run Odoo CLI (use the exact service name):

```powershell
docker compose exec odoo-boats-app /bin/bash
# inside container example: update a single module and quit
odoo -u <module_name> -d odoo-boats-db --config=/etc/odoo/odoo.conf --stop-after-init
```

Patterns & conventions to follow
- Addon layout: follow existing addons (e.g. `custom-addons/boat_core/`): export Python packages via `__init__.py`, declare module metadata in `__manifest__.py`, and place XML views under `views/` and CSV access rules under `security/`.
- When adding an addon, place it under `custom-addons/` and ensure `__manifest__.py` lists any inter-addon dependencies by name (this repo uses prefixes like `boat_` and `houseboat_`).
- To apply code changes without full restart, use the `-u <module>` Odoo CLI option shown above. For structural DB changes consider `-u` plus test/backup flows.

Integration & cross-component notes
- The app command in `docker-compose.yml` runs `odoo -u all --config=/etc/odoo/odoo.conf`. That means container start will attempt to update all modules — be mindful when changing `command` or the container entrypoint.
- Persistent state: DB lives in Docker volume `/var/lib/postgresql/data` (host: `/srv/odoo-db/odoo-boats`). Filestore is mounted from `./filestore`.

Security / secrets
- `odoo.conf` currently contains DB credentials and the `admin_passwd`. These are tracked in the repo; be cautious when cloning, forking, or publishing.

If you need more details
- Tell me which addon or feature you want to work on (name under `custom-addons/`), and I will extract the manifest, models, and views to provide a precise code-change checklist.

---
Please review and tell me if you'd like me to merge any project-specific snippets from a `README` or `AGENT.md` if you add one to the repo root — I can incorporate it into this file.
