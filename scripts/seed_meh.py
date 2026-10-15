#!/usr/bin/env python3
"""Paramétrage MEH de Mayan EDMS via l'API REST (docs/01-parametrage-MEH.md).

Crée, sans doublon si on le relance : types de métadonnées, types de documents,
arborescence des cabinets, groupes et rôles avec leurs permissions, workflows
ACQ-MEH et CYCLE-COURRIER (transitions réservées par rôle), index et étiquettes.

Python 3.8+, bibliothèque standard uniquement : tourne sur le serveur, sur un
poste Windows ou dans un Codespace, du moment que l'URL Mayan est joignable.

Usage :
    python scripts/seed_meh.py --url http://localhost:8000 --user admin --password '...'
    (ou variables MAYAN_URL, MAYAN_USER, MAYAN_PASSWORD)
"""
import argparse
import base64
import datetime
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

DATE_VALIDATOR = 'mayan.apps.metadata.metadata_validators.DateValidator'
DATE_PARSER = 'mayan.apps.metadata.metadata_parsers.DateParser'

# nom technique -> (libellé, options) ; options : lookup (liste fermée) ou date
METADATA_TYPES = {
    'numero_chrono': ('N° chrono', {}),
    'date_arrivee': ("Date d'arrivée", {'date': True}),
    'expediteur': ('Expéditeur', {}),
    'objet': ('Objet', {}),
    'entite_source': ('Entité source', {}),
    'motif': ('Motif', {}),
    'confidentialite': ('Confidentialité', {'lookup': 'Public,Interne,Confidentiel'}),
    'destinataire': ('Destinataire', {}),
    'signataire': ('Signataire', {}),
    'date_envoi': ("Date d'envoi", {'date': True}),
    'numero_texte': ('N° texte', {}),
    'date_signature': ('Date de signature', {'date': True}),
    'direction': ('Direction', {'lookup': 'DERH,DSI,DAF,DGE,DGH'}),
    'statut_texte': ('Statut du texte', {'lookup': 'Projet,Validé,Publié'}),
    'numero_marche': ('N° marché', {}),
    'attributaire': ('Attributaire', {}),
    'montant': ('Montant (MGA)', {}),
    'date_debut': ('Date de début', {'date': True}),
    'date_fin': ('Date de fin', {'date': True}),
    'statut_contrat': ('Statut du contrat', {'lookup': 'En préparation,En cours,Clos,Résilié'}),
    'projet': ('Projet', {'lookup': 'AMP,TRAC2'}),
    'auteur': ('Auteur', {}),
    'annee': ('Année', {}),
    'version_rapport': ('Version', {}),
    'cote': ('Cote', {}),
    'boite': ('Boîte', {}),
    'armoire': ('Armoire', {}),
    'site': ('Site', {}),
    'etat_physique': ('État', {'lookup': 'Bon,Abîmé,À restaurer'}),
    'date_transfert': ('Date de transfert', {'date': True}),
}

# type de document -> [(métadonnée, obligatoire)]
DOCUMENT_TYPES = {
    'Courrier-Entrant': [
        ('numero_chrono', True), ('date_arrivee', True), ('expediteur', True),
        ('objet', True), ('entite_source', False), ('motif', False),
        ('confidentialite', True),
    ],
    'Courrier-Sortie': [
        ('numero_chrono', True), ('destinataire', True), ('objet', True),
        ('signataire', False), ('date_envoi', False), ('confidentialite', True),
    ],
    'Arrêté-Décision': [
        ('numero_texte', True), ('date_signature', False), ('direction', True),
        ('statut_texte', True), ('objet', False),
    ],
    'Contrat-Marché': [
        ('numero_marche', True), ('attributaire', True), ('montant', False),
        ('date_debut', False), ('date_fin', False), ('statut_contrat', True),
    ],
    'Rapport-Etude': [
        ('projet', True), ('auteur', False), ('annee', True),
        ('version_rapport', False),
    ],
    'Archive-Physique': [
        ('cote', True), ('boite', True), ('armoire', True), ('site', True),
        ('etat_physique', False), ('date_transfert', False),
    ],
}

YEAR = str(datetime.date.today().year)

# arborescence : chaque entrée est un chemin de libellés
CABINETS = [
    ('MEH', '01-Courriers', 'Entrants', YEAR),
    ('MEH', '01-Courriers', 'Sortants', YEAR),
    ('MEH', '02-Directions', 'DERH'),
    ('MEH', '02-Directions', 'DSI'),
    ('MEH', '02-Directions', 'DAF'),
    ('MEH', '03-Projets', 'AMP'),
    ('MEH', '03-Projets', 'TRAC2'),
    ('MEH', '04-Juridique', 'Arrêtés'),
    ('MEH', '04-Juridique', 'Contrats'),
    ('MEH', 'Public-MEH'),
    ('MEH', 'Archives-Physiques', 'Antananarivo'),
]

PERMS_READ = [
    'documents.document_view', 'documents.document_file_view',
    'documents.document_version_view', 'cabinets.cabinet_view',
    'document_indexing.document_index_instance_view',
    'metadata.metadata_document_view', 'tags.tag_view',
    'comments.comment_view', 'document_states.workflow_view',
    'document_parsing.content_view', 'ocr.ocr_content_view',
    'dashboards.dashboard_view',
]
PERMS_DOWNLOAD = ['document_downloads.document_file_download']
PERMS_INDEX = [
    'documents.document_create', 'documents.document_edit',
    'documents.document_properties_edit', 'documents.document_file_new',
    'metadata.metadata_document_add', 'metadata.metadata_document_edit',
    'cabinets.cabinet_add_document', 'tags.tag_attach',
    'comments.comment_create', 'checkouts.checkout_document',
    'checkouts.checkin_document', 'sources.document_create_from_source',
]
PERMS_VALIDATE = ['cabinets.cabinet_remove_document', 'tags.tag_remove']
PERMS_AUDIT = ['events.events_view', 'events.events_export']

ROLES = {
    'Admin-Fonc': None,  # toutes les permissions
    'Validateur-Direction': PERMS_READ + PERMS_DOWNLOAD + PERMS_INDEX + PERMS_VALIDATE,
    'Indexeur': PERMS_READ + PERMS_DOWNLOAD + PERMS_INDEX,
    'Lecteur': PERMS_READ,
    'Auditeur': PERMS_READ + PERMS_AUDIT,
}

# workflow : états (libellé, initial, final, % achèvement), transitions
# (libellé, origine, destination, rôles autorisés), types de documents
WORKFLOWS = {
    'ACQ-MEH': {
        'internal_name': 'acq_meh',
        'states': [
            ('Numérisé', True, False, 10), ('Indexé', False, False, 30),
            ('Vérifié', False, False, 60), ('Contrôlé', False, False, 80),
            ('Publié', False, True, 100),
        ],
        'transitions': [
            ('Indexer', 'Numérisé', 'Indexé', ['Indexeur']),
            ('Vérifier', 'Indexé', 'Vérifié', ['Indexeur', 'Validateur-Direction']),
            ('Contrôle qualité OK', 'Vérifié', 'Contrôlé', ['Validateur-Direction']),
            ('Renvoyer en indexation', 'Vérifié', 'Indexé', ['Validateur-Direction']),
            ('Renvoyer en indexation', 'Contrôlé', 'Indexé', ['Validateur-Direction']),
            ('Publier', 'Contrôlé', 'Publié', ['Validateur-Direction']),
        ],
        'document_types': ['Courrier-Entrant', 'Rapport-Etude'],
    },
    'CYCLE-COURRIER': {
        'internal_name': 'cycle_courrier',
        'states': [
            ('Création', True, False, 10), ('Vérification', False, False, 30),
            ('Approbation', False, False, 60), ('Publication', False, False, 80),
            ('Archivage', False, True, 100),
        ],
        'transitions': [
            ('Soumettre', 'Création', 'Vérification', ['Indexeur']),
            ('Valider', 'Vérification', 'Approbation', ['Validateur-Direction']),
            ('Rejeter', 'Vérification', 'Création', ['Validateur-Direction']),
            ('Approuver', 'Approbation', 'Publication', ['Validateur-Direction']),
            ('Archiver', 'Publication', 'Archivage', ['Validateur-Direction']),
        ],
        'document_types': ['Courrier-Sortie', 'Arrêté-Décision', 'Contrat-Marché'],
    },
}

# index : libellé, slug, niveaux (expressions de gabarit), types de documents
INDEXES = [
    ('Par type et année', 'par-type-annee', [
        '{{ document.document_type.label }}',
        '{{ document.datetime_created|date:"Y" }}',
    ], list(DOCUMENT_TYPES)),
    ('Par entité source', 'par-entite', [
        '{{ document.metadata_value_of.entite_source }}',
    ], ['Courrier-Entrant']),
    ('Par direction', 'par-direction', [
        '{{ document.metadata_value_of.direction }}',
    ], ['Arrêté-Décision']),
    ('Par cote archive', 'par-cote-archive', [
        '{{ document.metadata_value_of.site }}',
        '{{ document.metadata_value_of.armoire }}',
        '{{ document.metadata_value_of.boite }}',
    ], ['Archive-Physique']),
]

TAGS = [('Urgent', '#d9534f'), ('Confidentiel', '#6f42c1'), ('À traiter', '#f0ad4e')]


class Mayan:
    def __init__(self, url, user, password):
        self.base = url.rstrip('/') + '/api/v4/'
        token = base64.b64encode('{}:{}'.format(user, password).encode()).decode()
        self.headers = {'Authorization': 'Basic ' + token, 'Content-Type': 'application/json'}

    def call(self, method, path, data=None):
        url = path if path.startswith('http') else self.base + path
        body = json.dumps(data).encode() if data is not None else None
        request = urllib.request.Request(url, data=body, method=method, headers=self.headers)
        try:
            with urllib.request.urlopen(request) as response:
                raw = response.read()
        except urllib.error.HTTPError as error:
            raise SystemExit('{} {} -> {} {}'.format(method, url, error.code, error.read().decode()[:400]))
        return json.loads(raw) if raw else None

    def all(self, path):
        url = path if path.startswith('http') else self.base + path
        items = []
        while url:
            page = self.call('GET', url)
            items.extend(page['results'])
            url = page.get('next')
        return items

    def get_or_create(self, path, key, value, data):
        for item in self.all(path):
            if item.get(key) == value:
                return item, False
        return self.call('POST', path, data), True


def log(created, kind, label):
    print('  {} {} : {}'.format('+' if created else '=', kind, label))


def seed(api):
    print('Types de métadonnées')
    metadata = {}
    for name, (label, options) in METADATA_TYPES.items():
        data = {'name': name, 'label': label}
        if options.get('lookup'):
            data['lookup'] = options['lookup']
        if options.get('date'):
            data['validation'] = DATE_VALIDATOR
            data['parser'] = DATE_PARSER
        item, created = api.get_or_create('metadata_types/', 'name', name, data)
        metadata[name] = item['id']
        log(created, 'métadonnée', label)

    print('Types de documents')
    document_types = {}
    for label, fields in DOCUMENT_TYPES.items():
        item, created = api.get_or_create('document_types/', 'label', label, {'label': label})
        document_types[label] = item['id']
        log(created, 'type', label)
        path = 'document_types/{}/metadata_types/'.format(item['id'])
        linked = {entry['metadata_type']['id'] for entry in api.all(path)}
        for name, required in fields:
            if metadata[name] not in linked:
                api.call('POST', path, {'metadata_type_id': metadata[name], 'required': required})

    print('Cabinets')
    cabinets = {tuple(c['full_path'].split(' / ')): c['id'] for c in api.all('cabinets/')}
    for chain in CABINETS:
        parent = None
        for depth in range(1, len(chain) + 1):
            path = chain[:depth]
            if path not in cabinets:
                cabinets[path] = api.call('POST', 'cabinets/', {'label': path[-1], 'parent': parent})['id']
                log(True, 'cabinet', '/'.join(path))
            parent = cabinets[path]

    print('Groupes et rôles')
    all_permissions = [p['pk'] for p in api.all('permissions/')]
    roles = {}
    for label, permissions in ROLES.items():
        group, _ = api.get_or_create('groups/', 'name', label, {'name': label})
        role, created = api.get_or_create('roles/', 'label', label, {'label': label})
        roles[label] = role['id']
        log(created, 'rôle', label)
        if group['id'] not in {g['id'] for g in api.all('roles/{}/groups/'.format(role['id']))}:
            api.call('POST', 'roles/{}/groups/add/'.format(role['id']), {'group': group['id']})
        granted = {p['pk'] for p in api.all('roles/{}/permissions/'.format(role['id']))}
        wanted = all_permissions if permissions is None else [p for p in permissions if p in all_permissions]
        for permission in wanted:
            if permission not in granted:
                api.call('POST', 'roles/{}/permissions/add/'.format(role['id']), {'permission': permission})

    print('Workflows')
    for label, spec in WORKFLOWS.items():
        workflow, created = api.get_or_create('workflow_templates/', 'internal_name', spec['internal_name'], {
            'label': label, 'internal_name': spec['internal_name'], 'auto_launch': True,
        })
        log(created, 'workflow', label)
        base = 'workflow_templates/{}/'.format(workflow['id'])
        states = {s['label']: s['id'] for s in api.all(base + 'states/')}
        for state, initial, final, completion in spec['states']:
            if state not in states:
                states[state] = api.call('POST', base + 'states/', {
                    'label': state, 'initial': initial, 'final': final, 'completion': completion,
                })['id']
        existing = {
            (t['label'], t['origin_state']['id'], t['destination_state']['id']): t['id']
            for t in api.all(base + 'transitions/')
        }
        for transition, origin, destination, allowed in spec['transitions']:
            key = (transition, states[origin], states[destination])
            if key not in existing:
                existing[key] = api.call('POST', base + 'transitions/', {
                    'label': transition, 'origin_state_id': states[origin],
                    'destination_state_id': states[destination],
                })['id']
            # transition réservée aux rôles listés (ACL sur l'objet transition)
            acl_path = 'objects/document_states/workflowtransition/{}/acls/'.format(existing[key])
            acls = {a['role']['id']: a for a in api.all(acl_path)}
            for role_label in allowed:
                acl = acls.get(roles[role_label]) or api.call('POST', acl_path, {'role_id': roles[role_label]})
                current = {p['pk'] for p in api.all(acl['permissions_url'])}
                if 'document_states.workflow_transition' not in current:
                    api.call('POST', acl['permissions_add_url'], {'permission': 'document_states.workflow_transition'})
        linked = {d['id'] for d in api.all(base + 'document_types/')}
        for document_type in spec['document_types']:
            if document_types[document_type] not in linked:
                api.call('POST', base + 'document_types/add/', {'document_type_id': document_types[document_type]})

    print('Index')
    for label, slug, levels, types in INDEXES:
        index, created = api.get_or_create('index_templates/', 'slug', slug, {'label': label, 'slug': slug, 'enabled': True})
        log(created, 'index', label)
        base = 'index_templates/{}/'.format(index['id'])
        if created:
            parent = index['index_template_root_node_id']
            for depth, expression in enumerate(levels):
                parent = api.call('POST', base + 'nodes/', {
                    'expression': expression, 'parent': parent, 'enabled': True,
                    'link_documents': depth == len(levels) - 1,
                })['id']
        linked = {d['id'] for d in api.all(base + 'document_types/')}
        for document_type in types:
            if document_types[document_type] not in linked:
                api.call('POST', base + 'document_types/add/', {'document_type': document_types[document_type]})

    print('Étiquettes')
    for label, color in TAGS:
        _, created = api.get_or_create('tags/', 'label', label, {'label': label, 'color': color})
        log(created, 'étiquette', label)

    print('Paramétrage MEH terminé.')


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--url', default=os.environ.get('MAYAN_URL', 'http://localhost:8000'))
    parser.add_argument('--user', default=os.environ.get('MAYAN_USER', 'admin'))
    parser.add_argument('--password', default=os.environ.get('MAYAN_PASSWORD'))
    args = parser.parse_args()
    if not args.password:
        sys.exit('Mot de passe manquant : --password ou MAYAN_PASSWORD')
    seed(Mayan(args.url, args.user, args.password))


if __name__ == '__main__':
    main()
