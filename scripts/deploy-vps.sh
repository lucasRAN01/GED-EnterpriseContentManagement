#!/usr/bin/env bash
# GED-ECM — provision VPS Ubuntu 22.04/24.04 + démarrage Mayan EDMS
# Usage : bash scripts/deploy-vps.sh  (à exécuter sur le VPS, pas en local)
set -euo pipefail

if [ ! -f .env ]; then cp .env.example .env; echo "!! Renseignez les mots de passe dans .env puis relancez."; exit 1; fi
if [ ! -f config/mayan.env ]; then cp config/mayan.env.example config/mayan.env; fi

if ! command -v docker >/dev/null 2>&1; then
  sudo apt-get update
  sudo apt-get install -y ca-certificates curl gnupg
  sudo install -m 0755 -d /etc/apt/keyrings
  curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
  echo "deb [signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list
  sudo apt-get update
  sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
fi

# Sur un serveur neuf, l'utilisateur n'est pas encore dans le groupe docker
DOCKER="docker"
if ! docker info >/dev/null 2>&1; then DOCKER="sudo docker"; fi

$DOCKER compose version
$DOCKER compose up -d
$DOCKER compose ps
echo "Mayan : http://$(hostname -I | awk '{print $1}'):8000 (2 à 5 min au premier lancement)"
echo "Paramétrage MEH : python3 scripts/seed_meh.py --password <MAYAN_ADMIN_PASSWORD>"
