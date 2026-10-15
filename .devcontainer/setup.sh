#!/usr/bin/env bash
# Création du Codespace : secrets aléatoires propres à ce Codespace + dépendance de demo_data.py
set -euo pipefail
cd "$(dirname "$0")/.."

if [ ! -f .env ]; then
  rand() { python3 -c "import secrets; print(secrets.token_urlsafe($1))"; }
  sed -e "s/^POSTGRES_PASSWORD=.*/POSTGRES_PASSWORD=$(rand 24)/" \
      -e "s/^MAYAN_SECRET_KEY=.*/MAYAN_SECRET_KEY=$(rand 48)/" \
      -e "s/^MAYAN_ADMIN_PASSWORD=.*/MAYAN_ADMIN_PASSWORD=$(rand 12)/" \
      .env.example > .env
fi
[ -f config/mayan.env ] || cp config/mayan.env.example config/mayan.env
python3 -m pip install --quiet --user pillow
