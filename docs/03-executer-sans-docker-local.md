# 03 — Exécuter sans Docker local

Docker Desktop est en panne sur la machine : aucune étape ci-dessous n'exige le daemon local.
`docker compose config` reste la validation de référence (100% client, sans daemon).

## Option A — GitHub Codespaces (recommandée)

1. Pousser `main` (déjà fait), ouvrir le repo -> Code -> Codespaces -> Create.
2. Le `.devcontainer` démarre avec Docker-in-Docker.
3. Dans le terminal du Codespace :
```bash
cp -n .env.example .env
cp -n config/mayan.env.example config/mayan.env
# renseigner mots de passe dans .env
docker compose up -d
docker compose ps
docker compose logs -f app
```
4. Ouvrir le port forwardé `8000` -> Mayan. Login `admin` / mot de passe du `.env` du Codespace.

## Option B — VPS Ubuntu (proche prod MEH)

Prérequis : Ubuntu 22.04/24.04, 4 Go RAM mini, ports 8000/443.
```bash
# sur le VPS
git clone https://github.com/lucasRAN01/GED-EnterpriseContentManagement.git ged-ecm
cd ged-ecm
bash scripts/deploy-vps.sh
```
Le script installe Docker, copie les `.env`, lance `docker compose up -d`.

## Option C — Validation locale sans daemon (possible dès maintenant)

```powershell
docker compose config --quiet  # OK = YAML + interpolation valides
git status --porcelain         # .env doit rester invisible (ignoré)
```

## Checklist premier login (Codespace ou VPS)

- [ ] `http://<hôte>:8000` répond, login admin OK
- [ ] OCR réglé `fra+eng`, timezone `Indian/Antananarivo`
- [ ] Créer 1 type doc test + 1 cabinet test + upload 1 PDF FR + recherche plein-texte
- [ ] Créer 1 workflow test à 2 états + 1 transition
- [ ] `scripts/backup.ps1` (Windows) / dump Postgres testé
- [ ] Seulement après : appliquer `docs/01-parametrage-MEH.md` complet
