#!/usr/bin/env bash
# Chaque démarrage du Codespace : lance Mayan, applique le paramétrage MEH et charge
# les documents fictifs (sans doublon si déjà fait), puis affiche l'accès.
set -uo pipefail
cd "$(dirname "$0")/.."
LOG=/tmp/ged-ecm-start.log
exec > >(tee -a "$LOG") 2>&1

set -a; . ./.env; set +a
docker compose up -d

echo "Démarrage de Mayan (5 à 10 min la première fois : téléchargement de l'image)..."
for _ in $(seq 1 120); do
  [ "$(docker inspect --format '{{.State.Health.Status}}' "$(docker compose ps -q app)" 2>/dev/null)" = healthy ] && break
  sleep 10
done

export MAYAN_URL=http://localhost:8000 MAYAN_USER="$MAYAN_ADMIN_USER" MAYAN_PASSWORD="$MAYAN_ADMIN_PASSWORD"
python3 scripts/seed_meh.py && python3 scripts/demo_data.py

cat <<MSG

============================================================
 GED-ECM est prêt.
 Ouvrez l'onglet PORTS puis le port 8000 (Mayan EDMS).
 Identifiant : $MAYAN_ADMIN_USER
 Mot de passe : $MAYAN_ADMIN_PASSWORD   (aussi dans le fichier .env)
 Journal : $LOG
============================================================
MSG
