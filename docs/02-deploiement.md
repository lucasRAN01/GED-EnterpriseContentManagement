# 02 — Déploiement / exploitation

## Prérequis

- Docker + Docker Compose v2, 4 Go RAM mini (16 Go reco prod), SSD
- Ports : 8000 (Mayan), 8080 (Keycloak opt), 3000 (Metabase opt)
- DNS local + HTTPS en prod (Caddy/Nginx/Traefik devant)

## Install dev

```powershell
Copy-Item ".env.example" ".env"
Copy-Item "config\mayan.env.example" "config\mayan.env"
# renseigner mots de passe dans .env
docker compose up -d
docker compose logs -f app
python scripts\seed_meh.py --password "<MAYAN_ADMIN_PASSWORD>"
```

Première connexion : `http://localhost:8000` avec `MAYAN_ADMIN_USER/PASSWORD`.
La langue de l'interface se règle par utilisateur (menu profil > Langue et fuseau horaire).

Image : `mayanedms/mayanedms:v4.12.2` (l'image `mayanedms/mayan-edms` n'existe pas). Mayan ne lit
que des variables `MAYAN_<RÉGLAGE>` : base via `MAYAN_DATABASES`, Redis via
`MAYAN_CELERY_BROKER_URL`, `MAYAN_CELERY_RESULT_BACKEND` et `MAYAN_LOCK_MANAGER_BACKEND`,
compte initial via `MAYAN_AUTOADMIN_*`. Sans `MAYAN_DATABASES`, Mayan retombe sur SQLite.

OCR français : le pack `tesseract-ocr-fra` n'est pas dans l'image. Il est installé à chaque démarrage
par `MAYAN_APT_INSTALLS`, ce qui demande un accès Internet au serveur. Hors ligne, construire une image
dérivée (`FROM mayanedms/mayanedms:v4.12.2` + `apt-get install tesseract-ocr-fra`).

## Profils optionnels

```powershell
# SSO Keycloak
docker compose --profile sso up -d
# Puis créer realm `meh`, client `mayan` OIDC, renseigner config/mayan.env

# Stats Metabase
docker compose --profile stats up -d
# Connecter Metabase à Postgres en lecture seule, importer dashboards vie-document
```

## Sauvegarde (scripts\backup.ps1)

- `pgdata` : `pg_dump` quotidien
- `mayanmedia` : snapshot volume / Restic vers S3/B2
- Tester restauration mensuelle. Règle 3-2-1.

## Prod Madagascar (on-premise)

- Serveur central MEH + dossiers scan par direction (décentralisé -> centralisé, conforme TDR)
- Onduleur + clim, backup offsite chiffré, supervision `docker ps` + healthchecks
- Montée en charge : le conteneur `app` lance tout (`run_all`) ; au besoin, sortir les workers OCR dans des conteneurs `run_worker worker_b` dédiés, passer la recherche sur OpenSearch si >500k pages
- Sécurité : HTTPS obligatoire, OIDC dès que possible, comptes service à portée minimale, audit exporté

## Limites MVP assumées

Pas de BPMN graphique, pas de pilotage scanner natif, pas de DAM vidéo. Si exigé plus tard : évaluer Alfresco CE ou module custom via API Mayan, sans réécrire le cœur.
