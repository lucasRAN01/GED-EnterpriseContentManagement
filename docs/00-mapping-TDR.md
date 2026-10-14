# 00 — Mapping TDR -> Mayan EDMS

Source : RFP 719/RFP/AMP/2022, section V Spécifications techniques. Objectif : zéro code, que de la config.

| Exigence TDR | Mayan 4.12 natif | Config à faire dans GED-ECM |
|---|---|---|
| Numérisation : ajustement résolution/luminosité, retouche, redressement, assemblage pages | Partiel — Mayan ne pilote pas le scanner. Retouche à la source (scanner / NAPS2) puis import | Procédure scan : 300 dpi PDF, redressement auto côté scanner, dépôt dossier surveillé / upload |
| Import/export JPEG/GIF/BMP, compression, conversion PDF | Oui — transform + viewer + download PDF | Activer transformations, définir types autorisés |
| 2 modes capture : OCR / manuel image | Oui — OCR auto Tesseract + version image d'origine conservée | `fra+eng` dans `config/mayan.env`, file d'attente OCR dédiée |
| Chaîne acquisition : Numérisation -> Indexation -> Vérification -> Contrôle Qualité | Oui via Workflows à états | Créer workflow `ACQ-MEH` à 4 états, transitions par rôle (voir 01-parametrage) |
| Import fichier/email, compat scanners, lots, points décentralisés + traitement central | Oui — Sources : web, staging, watch folder, IMAP, API | 1 watch folder par direction + 1 boîte IMAP Zimbra/Exchange + staging central |
| Indexation & classement multi-niveaux, multi-dossiers | Oui — Document Types + Metadata + Cabinets + Tags + Index | Créer arborescence Cabinets MEH, Index par type/année/entité |
| Recherche : formulaires paramétrables, plein-texte, FR, date, transverse, sécurisée | Oui — recherche plein-texte + filtres + ACL appliquées | Créer saved searches par type doc, tester droits |
| Consultation viewer JPEG/BMP/GIF/PDF/HTML, modification | Oui — viewer + versions (toute nouvelle version historisée) | Activer versions, interdire suppression versions archivées par ACL |
| Stockage : scanner direct, upload, copier-coller, mail, MS Office, imagerie | Oui sauf copier-coller direct et save-from-Office | Procédure : drag-drop web + dossier réseau + IMAP ; Office via PDF/api |
| Traçabilité : ajout/remplacement/up/down/consult/modif/suppr | Oui — Events / audit log par document | Activer rétention events, export audit mensuel |
| Cycle de vie paramétrable par type | Oui — Workflows par Document Type | 1 workflow par type sensible (courrier, arrêté, contrat) |
| Collaboratif : verrouillage, commentaires, notifs, espaces public/privé, dashboard | Partiel — checkout/lock, commentaires, favoris, dashboard, ACL cabinets | Cabinet `Public-MEH` lecture tous + cabinets privés par direction ; notifs mail SMTP |
| Notifications email + tableau de bord activités | Oui — notifications + events + mails workflow | Configurer SMTP MEH, abonnements events |
| Workflow moteur paramétrable + modélisation graphique + suivi + fiches réutilisables | Partiel — workflow états/transitions/actions, pas de BPMN graphique | Rester en états simples ; si BPMN exigé -> Alfresco, hors MVP |
| Archives physiques : cheminement, inventaire, flux E/S, localisation, stats | Partiel — modélisé en métadonnées | Champs : cote, boîte, armoire, site, statut (voir 01) + cabinet `Archives-Physiques` |
| Stats / tableaux de bord : entrées/sorties, motifs, entité, modifications | Partiel — compteurs + index ; avancé via Metabase | Profil `stats` : Metabase lecture seule sur Postgres |
| API dev + API REST + connecteurs + SSO | Oui — REST OpenAPI 3 complète, webhooks ; OIDC/Keycloak, LDAP | Documenter tokens + créer compte service ; configurer Keycloak realm `meh` |
| Admin : droits par profil/groupe/objet, notif modifs, non-modif archivé, web/images/vidéos, arborescence, full-text + mots-clés, OCR, publication intranet | Oui sauf publication intranet mise en forme | Rôles : Admin-Fonc, Validateur, Indexeur, Lecteur ; publication via lien partage + export |

Non couvert en MVP et assumé : modélisation BPMN graphique, pilotage scanner natif, DAM vidéo avancée, conversion modèles intranet uniformes.
