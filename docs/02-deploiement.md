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
```

Première connexion : `http://localhost:8000` avec `MAYAN_ADMIN_USER/PASSWORD`.

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
- Montée en charge : augmenter workers B/C (OCR), passer recherche sur OpenSearch si >500k pages
- Sécurité : HTTPS obligatoire, OIDC dès que possible, comptes service à portée minimale, audit exporté

## Limites MVP assumées

Pas de BPMN graphique, pas de pilotage scanner natif, pas de DAM vidéo. Si exigé plus tard : évaluer Alfresco CE ou module custom via API Mayan, sans réécrire le cœur.
