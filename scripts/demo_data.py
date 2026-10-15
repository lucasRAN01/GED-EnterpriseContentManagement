#!/usr/bin/env python3
"""Charge des documents FICTIFS de démonstration dans un Mayan paramétré par seed_meh.py.

Génère des courriers « scannés » (PDF image, donc passés à l'OCR français),
les dépose avec leurs métadonnées, les classe dans les cabinets, les étiquette
et fait avancer leur workflow. Pour une démo ou une formation, jamais en production.

Dépendance : Pillow (pip install pillow).

Usage :
    python scripts/demo_data.py --url http://localhost:8000 --user admin --password '...'
"""
import argparse
import io
import os
import sys
import time
import uuid

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from seed_meh import YEAR, Mayan  # noqa: E402

FONT_PATHS = [
    '/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf',
    '/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf',
    'C:/Windows/Fonts/times.ttf',
]

# libellé, type, métadonnées, cabinet (chemin), étiquettes, transitions à jouer, texte du courrier
DOCUMENTS = [
    (
        'Demande de raccordement mini-réseau Ampanihy', 'Courrier-Entrant',
        {'numero_chrono': f'CE-{YEAR}-0142', 'date_arrivee': f'{YEAR}-09-12', 'expediteur': 'Commune rurale d\'Ampanihy',
         'objet': 'Demande de raccordement au mini-réseau solaire', 'entite_source': 'Région Atsimo Andrefana',
         'motif': 'Accès à l\'électricité', 'confidentialite': 'Public'},
        ('MEH', '01-Courriers', 'Entrants', YEAR), ['À traiter'], ['Indexer', 'Vérifier'],
        ['Monsieur le Ministre,',
         'La commune rurale d\'Ampanihy sollicite le raccordement de ses',
         'quartiers nord au mini-réseau solaire prévu par le programme AMP.',
         'Plus de 1 200 ménages et deux centres de santé attendent',
         'l\'électricité pour la conservation des vaccins.',
         'Veuillez agréer, Monsieur le Ministre, nos salutations distinguées.'],
    ),
    (
        'Transmission du rapport trimestriel TRAC2', 'Courrier-Entrant',
        {'numero_chrono': f'CE-{YEAR}-0157', 'date_arrivee': f'{YEAR}-09-30', 'expediteur': 'Unité de gestion TRAC2',
         'objet': 'Rapport d\'avancement du troisième trimestre', 'entite_source': 'Projet TRAC2',
         'motif': 'Rapport périodique', 'confidentialite': 'Interne'},
        ('MEH', '01-Courriers', 'Entrants', YEAR), [], ['Indexer', 'Vérifier', 'Contrôle qualité OK', 'Publier'],
        ['Monsieur le Directeur général,',
         'Nous vous transmettons le rapport d\'avancement du projet TRAC2',
         'pour le troisième trimestre. Les travaux de la ligne de',
         'transport ont atteint 64 % de réalisation physique.',
         'Le comité de pilotage est proposé pour la fin du mois prochain.'],
    ),
    (
        'Réponse à la commune d\'Ampanihy', 'Courrier-Sortie',
        {'numero_chrono': f'CS-{YEAR}-0088', 'destinataire': 'Commune rurale d\'Ampanihy',
         'objet': 'Suite donnée à la demande de raccordement', 'signataire': 'Directeur général de l\'Énergie',
         'date_envoi': f'{YEAR}-10-03', 'confidentialite': 'Public'},
        ('MEH', '01-Courriers', 'Sortants', YEAR), [], ['Soumettre'],
        ['Monsieur le Maire,',
         'Le Ministère accuse réception de votre demande de raccordement.',
         'Une mission technique se rendra sur place pour évaluer la',
         'faisabilité de l\'extension du mini-réseau.',
         'Veuillez agréer, Monsieur le Maire, nos salutations distinguées.'],
    ),
    (
        'Arrêté portant création du comité de suivi ECM', 'Arrêté-Décision',
        {'numero_texte': f'ARR-{YEAR}-017', 'date_signature': f'{YEAR}-08-21', 'direction': 'DSI',
         'statut_texte': 'Validé', 'objet': 'Comité de suivi de la plateforme ECM'},
        ('MEH', '04-Juridique', 'Arrêtés'), ['Confidentiel'], ['Soumettre', 'Valider'],
        ['ARRÊTÉ portant création du comité de suivi de la plateforme ECM',
         'Article premier. Il est créé un comité de suivi chargé de',
         'superviser le déploiement de la gestion électronique des documents.',
         'Article 2. Le comité est présidé par le Directeur des systèmes',
         'd\'information et se réunit une fois par mois.'],
    ),
    (
        'Marché de fourniture de panneaux solaires', 'Contrat-Marché',
        {'numero_marche': f'MP-{YEAR}-031', 'attributaire': 'Société Solaire du Sud', 'montant': '1 250 000 000',
         'date_debut': f'{YEAR}-07-01', 'date_fin': f'{int(YEAR) + 1}-06-30', 'statut_contrat': 'En cours'},
        ('MEH', '04-Juridique', 'Contrats'), [], ['Soumettre', 'Valider', 'Approuver'],
        ['CONTRAT DE MARCHÉ PUBLIC',
         'Objet : fourniture et installation de panneaux solaires pour',
         'les mini-réseaux de la région Atsimo Andrefana.',
         'Montant : un milliard deux cent cinquante millions d\'ariary.',
         'Délai d\'exécution : douze mois à compter de l\'ordre de service.'],
    ),
    (
        'Étude de faisabilité mini-réseaux AMP', 'Rapport-Etude',
        {'projet': 'AMP', 'auteur': 'Cellule technique AMP', 'annee': YEAR, 'version_rapport': '1.2'},
        ('MEH', '03-Projets', 'AMP'), [], ['Indexer'],
        ['ÉTUDE DE FAISABILITÉ DES MINI-RÉSEAUX SOLAIRES',
         'Résumé : douze sites ont été évalués dans la région pilote.',
         'Huit sites présentent une demande suffisante et un coût',
         'de production compatible avec le tarif social.',
         'Recommandation : lancer la première vague sur quatre sites.'],
    ),
    (
        'Registre des courriers 2019, boîte 12', 'Archive-Physique',
        {'cote': 'MEH/ARCH/2019/012', 'boite': 'B-12', 'armoire': 'A-03', 'site': 'Antananarivo',
         'etat_physique': 'Bon', 'date_transfert': f'{YEAR}-02-14'},
        ('MEH', 'Archives-Physiques', 'Antananarivo'), [], [],
        ['FICHE DE VERSEMENT AUX ARCHIVES',
         'Contenu : registre des courriers arrivés, année 2019.',
         'Localisation : site d\'Antananarivo, armoire A-03, boîte B-12.',
         'Durée d\'utilité administrative : dix ans.'],
    ),
]


def font(size):
    for path in FONT_PATHS:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def render(title, lines):
    """Une page A4 à 150 dpi, comme un courrier scanné, enregistrée en PDF image."""
    page = Image.new('L', (1240, 1754), 248)
    draw = ImageDraw.Draw(page)
    draw.text((110, 100), 'REPOBLIKAN\'I MADAGASIKARA', font=font(30), fill=20)
    draw.text((110, 145), 'Ministère de l\'Énergie et des Hydrocarbures', font=font(26), fill=20)
    draw.text((110, 250), title, font=font(30), fill=0)
    y = 360
    for line in lines:
        draw.text((110, y), line, font=font(28), fill=10)
        y += 56
    draw.text((110, 1620), 'DOCUMENT FICTIF DE DÉMONSTRATION', font=font(22), fill=90)
    buffer = io.BytesIO()
    page.convert('RGB').save(buffer, format='PDF', resolution=150)
    return buffer.getvalue()


def upload(api, document_type_id, label, payload):
    boundary = uuid.uuid4().hex
    parts = []
    for name, value in (('document_type_id', str(document_type_id)), ('label', label), ('language', 'fra')):
        parts.append('--{}\r\nContent-Disposition: form-data; name="{}"\r\n\r\n{}\r\n'.format(boundary, name, value).encode())
    parts.append('--{}\r\nContent-Disposition: form-data; name="file"; filename="{}.pdf"\r\nContent-Type: application/pdf\r\n\r\n'.format(boundary, uuid.uuid4().hex[:8]).encode())
    parts.append(payload + b'\r\n--' + boundary.encode() + b'--\r\n')
    headers = dict(api.headers, **{'Content-Type': 'multipart/form-data; boundary=' + boundary})
    import urllib.request
    import json
    request = urllib.request.Request(api.base + 'documents/upload/', data=b''.join(parts), method='POST', headers=headers)
    with urllib.request.urlopen(request) as response:
        return json.loads(response.read())


def by(items, key):
    return {item[key]: item for item in items}


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--url', default=os.environ.get('MAYAN_URL', 'http://localhost:8000'))
    parser.add_argument('--user', default=os.environ.get('MAYAN_USER', 'admin'))
    parser.add_argument('--password', default=os.environ.get('MAYAN_PASSWORD'))
    args = parser.parse_args()
    if not args.password:
        sys.exit('Mot de passe manquant : --password ou MAYAN_PASSWORD')
    api = Mayan(args.url, args.user, args.password)

    document_types = by(api.all('document_types/'), 'label')
    metadata_types = by(api.all('metadata_types/'), 'name')
    tags = by(api.all('tags/'), 'label')
    cabinets = {tuple(c['full_path'].split(' / ')): c['id'] for c in api.all('cabinets/')}
    existing = {d['label'] for d in api.all('documents/')}

    for label, type_label, metadata, cabinet, tag_labels, transitions, lines in DOCUMENTS:
        if label in existing:
            print('  = document : ' + label)
            continue
        document = upload(api, document_types[type_label]['id'], label, render(label, lines))
        document_id = document['id']
        print('  + document : ' + label)
        for name, value in metadata.items():
            api.call('POST', 'documents/{}/metadata/'.format(document_id), {
                'metadata_type_id': metadata_types[name]['id'], 'value': value,
            })
        api.call('POST', 'cabinets/{}/documents/add/'.format(cabinets[cabinet]), {'document': document_id})
        for tag_label in tag_labels:
            api.call('POST', 'documents/{}/tags/attach/'.format(document_id), {'tag': tags[tag_label]['id']})
        if transitions:
            # le workflow démarre en tâche de fond juste après le dépôt
            for _ in range(30):
                instances = api.all('documents/{}/workflow_instances/'.format(document_id))
                if instances:
                    break
                time.sleep(2)
            instance = instances[0]
            for transition_label in transitions:
                available = api.all('documents/{}/workflow_instances/{}/log_entries/transitions/'.format(document_id, instance['id']))
                transition = next(t for t in available if t['label'] == transition_label)
                api.call('POST', 'documents/{}/workflow_instances/{}/log_entries/'.format(document_id, instance['id']), {
                    'transition_id': transition['id'], 'comment': 'Démonstration',
                })
    print('Documents de démonstration chargés.')


if __name__ == '__main__':
    main()
