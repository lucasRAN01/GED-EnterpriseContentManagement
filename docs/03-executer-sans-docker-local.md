# 03 — Exécuter sans Docker local

Docker Desktop est en panne sur la machine : aucune étape ci-dessous n'exige le daemon local.
`docker compose config` reste la validation de référence (100% client, sans daemon).

## Option A — GitHub Codespaces (recommandée, gratuite)

Codespaces est inclus gratuitement dans un compte GitHub personnel : 120 heures-cœur par mois,
soit 60 heures d'utilisation sur la machine 2 cœurs, et 15 Go de stockage. Arrêtez le Codespace
après usage (il s'arrête seul après 30 min d'inactivité) pour rester dans le quota.

1. Ouvrir https://codespaces.new/lucasRAN01/GED-EnterpriseContentManagement
   (choisir la branche voulue, machine 2 cœurs / 8 Go) -> Create codespace.
2. Attendre 5 à 10 minutes la première fois. Le Codespace tout seul :
   - génère des mots de passe aléatoires dans `.env` ;
   - lance Mayan (`docker compose up -d`) ;
   - applique le paramétrage MEH (`seed_meh.py`) et charge 7 documents fictifs (`demo_data.py`) ;
   - affiche l'identifiant et le mot de passe admin dans le terminal.
3. Onglet PORTS -> port `8000` -> ouvrir dans le navigateur. Le port reste privé à votre compte GitHub.
4. Pour revenir plus tard : github.com/codespaces -> relancer le même Codespace. Les données sont conservées
   et `.devcontainer/start.sh` relance tout sans créer de doublons.

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
- [ ] `python3 scripts/seed_meh.py` applique `docs/01-parametrage-MEH.md` ; `demo_data.py` ajoute des documents fictifs
