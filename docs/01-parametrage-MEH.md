# 01 — Paramétrage MEH prêt à saisir

Ordre de saisie recommandé dans l'UI Mayan (http://localhost:8000).

## 1. Document Types + Metadata

- `Courrier-Entrant` : n°chrono, date_arrivée, expéditeur, objet, entité_source, motif, confidentialité
- `Courrier-Sortie` : n°chrono, destinataire, objet, signataire, date_envoi
- `Arrêté-Décision` : n°texte, date_signature, direction, statut (projet/validé/publié)
- `Contrat-Marché` : n°marché, attributaire, montant, dates début/fin, statut
- `Rapport-Etude` : projet (AMP/TRAC2), auteur, année, version
- `Archive-Physique` : cote, boîte, armoire, site, état, date_transfert

Tous : langue=fr, OCR auto, versioning ON, rétention selon règle MEH.

## 2. Cabinets (arborescence)

```
MEH/
  01-Courriers/Entrants/<année>/  + Sortants/<année>/
  02-Directions/DERH Dumont / DSI / DAF /
  03-Projets/AMP/ + TRAC2/
  04-Juridique/Arrêtés/ + Contrats/
  Public-MEH/  (lecture tous, écriture Validateurs seuls)
  Archives-Physiques/<site>/<armoire>/<boîte>/
```

Règle : un doc peut être lié à N cabinets (multi-classement TDR OK).

## 3. Rôles / Groupes / ACL

- `Admin-Fonc` : tout, gestion users/rôles/index
- `Validateur-Direction` : valider transitions workflow, publier
- `Indexeur` : créer/indexer, pas de suppression, pas de validation finale
- `Lecteur` : recherche + consultation seuls, download selon confidentialité
- `Auditeur` : events + export, lecture seule

Appliquer ACL par Cabinet + par Document Type + par état workflow (ex : Brouillon invisible Lecteur).

## 4. Workflows

`ACQ-MEH` (appliqué à Courrier-Entrant, Rapport) :
`Numérisé -> Indexé -> Vérifié -> Contrôlé -> Publié/Archivé`
- Numérisé->Indexé : action Indexeur
- Indexé->Vérifié : action Vérificateur, notif mail
- Vérifié->Contrôlé : contrôle qualité, retour arrière possible vers Indexé
- Contrôlé->Publié : Validateur seul, verrouille modifications (ACL état)

`CYCLE-COURRIER` : Création -> Vérification -> Approbation -> Publication -> Archivage, avec relances mail.

## 5. Sources

- Watch folder : `\\srv-meh\scan\<direction>` -> staging, OCR `fra+eng`
- IMAP Zimbra/Exchange : boîte `ged@meh.mg`, import pièces jointes PDF/images, suppression après import si validé
- Upload web + API REST avec compte service `svc-gex`

## 6. Recherche / Index

Index : `Par-Type-Année`, `Par-Entité`, `Par-Cote-Archive`
Saved searches : "Courriers non vérifiés", "Contrats expirant <90j", "Docs sans OCR"

## 7. Notifications / SMTP

SMTP MEH dans Mayan, événements : transition workflow, ajout cabinet, échec OCR. Dashboard : "Mes tâches" = docs en état à traiter par mon rôle.
