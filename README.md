# GED-EnterpriseContentManagement

> ECM MEH sur base Mayan EDMS (projet GED-ECM, isolé de `../GED` — référence architecture uniquement).

Base : **Mayan EDMS 4.12.2** (Django + PostgreSQL + Redis + Celery + Tesseract) en Docker.
Couvre ~85% du TDR RFP 719/RFP/AMP/2022 : acquisition, OCR FR, classement multi-niveaux, recherche plein-texte, versioning, cycle de vie / workflows, ACLs, audit, API REST, SSO OIDC, dashboard.

## Arborescence

```
GED-ECM/
  docker-compose.yml      # stack Mayan + Postgres + Redis (+ profils keycloak/metabase)
  .env.example            # à copier en .env
  config/
    mayan.env.example     # variables Mayan (OCR fra, API, OIDC)
  docs/
    00-mapping-TDR.md         # exigence TDR -> fonction Mayan -> config à faire
    01-parametrage-MEH.md     # types docs, cabinets, rôles, workflows MEH prêts à saisir
    02-deploiement.md         # install, SSO, sauvegarde, prod Madagascar
  scripts/
    init.ps1              # premier démarrage
    backup.ps1            # sauvegarde data + db
```

## Démarrage rapide (Windows PowerShell 5.1)

```powershell
Copy-Item ".env.example" ".env"
Copy-Item "config\mayan.env.example" "config\mayan.env"
docker compose up -d --build
docker compose logs -f app
# UI : http://localhost:8000  (admin / mot de passe du .env)
```

Ne jamais toucher à `../GED` depuis ce projet.

## Choix assumés

- Pas de code from-scratch : config Mayan uniquement.
- OCR : Tesseract `fra+eng` par défaut.
- Recherche : backend Django + possibilité OpenSearch plus tard.
- Stats avancées : Metabase en profil optionnel sur réplica Postgres (lecture seule).
- SSO : Keycloak OIDC en profil optionnel, sinon auth locale + LDAP.
- Archives physiques : modélisées en métadonnées + cabinets, pas de module RM lourd.
