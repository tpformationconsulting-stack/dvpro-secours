# DV Pro, copie de secours du registre national des copropriétés (RNIC, ANAH, data.gouv.fr).
# Créé le 02/11/2026 à la demande de TP : quand le registre du jour ne répond pas, DV Pro lit cette copie, avec sa date.
# Données publiques seulement (fichier quotidien publié sur data.gouv.fr), colonnes utiles à DV Pro seulement.
#
# Usage :
#   python3 construire_registre.py site                 -> télécharge le fichier du jour et construit le dossier « site »
#   python3 construire_registre.py site --csv fichier.csv [--deps 06,83]   -> à partir d'un fichier déjà téléchargé (essais)
#
# Ce qui est produit (dossier « site », publié tel quel) :
#   meta.json                 date du fichier, date de construction, nombre de copropriétés, colonnes
#   c/<commune>.json          les copropriétés d'une commune (code INSEE), colonnes de meta.json
#   t/<case>.json             pour une case de 0,05 degré, les communes qui y ont une copropriété (recherche autour d'un point)
#   i/<4 premiers>.json       numéro d'immatriculation vers commune
#   n/communes.json           nom officiel de la commune (sans accents, en majuscules) vers codes INSEE
#   w/<2 lettres>.json        mots des noms de copropriétés (3 lettres et plus) vers codes INSEE (recherche par nom)
#   robots.txt, index.html    pas de référencement par les moteurs de recherche
import csv, datetime, io, json, math, os, re, shutil, sys, unicodedata, urllib.request

JEU = 'https://www.data.gouv.fr/api/1/datasets/registre-national-dimmatriculation-des-coproprietes/'
COLONNES = ['commune', 'numero_immatriculation', 'date_derniere_maj', 'type_syndic', 'raison_sociale_representant_legal',
            'nom_usage_copropriete', 'adresse_reference', 'code_postal_adresse', 'commune_adresse',
            'adresse_complementaire_1', 'adresse_complementaire_2', 'adresse_complementaire_3', 'longitude', 'latitude',
            'date_reglement_copropriete', 'nombre_total_lots', 'nombre_lots_habitation_bureaux_commerces', 'nombre_lots_habitation',
            'nombre_lots_stationnement', 'periode_construction', 'reference_cadastrale_1', 'reference_cadastrale_2',
            'reference_cadastrale_3', 'code_officiel_commune', 'nom_officiel_commune']
ENTIERS = {'nombre_total_lots', 'nombre_lots_habitation_bureaux_commerces', 'nombre_lots_habitation', 'nombre_lots_stationnement'}
REELS = {'longitude', 'latitude'}
PAS = 20  # cases de 1/20 de degré (environ 5,5 km sur 4 km)


def lire_json(u):
    with urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'DVPro-secours/1.0'}), timeout=60) as r:
        return json.load(r)


def fichier_du_jour():
    d = lire_json(JEU)
    res = [r for r in d.get('resources', []) if (r.get('format') or '').lower() == 'csv']
    q = [r for r in res if 'quotidien' in (r.get('title') or '').lower()]
    r = (q or sorted(res, key=lambda x: x.get('last_modified') or '', reverse=True))[0]
    return r['url'], (r.get('last_modified') or '')[:10], r.get('title') or ''


def valeur(c, v):
    v = (v or '').strip()
    if v == '':
        return None
    if c in ENTIERS:
        try: return int(float(v))
        except ValueError: return None
    if c in REELS:
        try: return float(v)
        except ValueError: return None
    return v


def nom_commune(s):
    s = unicodedata.normalize('NFD', s or '').encode('ascii', 'ignore').decode().upper()
    return re.sub(r'[^A-Z0-9]+', ' ', s).strip()


def construire(sortie, flux, date_fichier, source, deps=None):
    if os.path.isdir(sortie):
        shutil.rmtree(sortie)
    for s in ('c', 't', 'i', 'n', 'w'):
        os.makedirs(os.path.join(sortie, s))
    par_com, cases, imm, noms, mots, n = {}, {}, {}, {}, {}, 0
    for row in csv.DictReader(flux):
        com = (row.get('commune') or '').strip()
        if not re.fullmatch(r'[0-9AB]{5}', com):
            continue
        if deps and com[:2] not in deps and com[:3] not in deps:
            continue
        ligne = [valeur(c, row.get(c)) for c in COLONNES]
        par_com.setdefault(com, []).append(ligne)
        n += 1
        im = (row.get('numero_immatriculation') or '').strip()
        if im:
            imm.setdefault(im[:4].upper(), {})[im] = com
        la, lo = valeur('latitude', row.get('latitude')), valeur('longitude', row.get('longitude'))
        if la is not None and lo is not None:
            cases.setdefault('%d_%d' % (math.floor(la * PAS), math.floor(lo * PAS)), set()).add(com)
        for m in set(nom_commune(row.get('nom_usage_copropriete')).split()):
            if len(m) >= 3:
                mots.setdefault(m[:2], {}).setdefault(m, set()).add(com)
        nc = nom_commune(row.get('nom_officiel_commune'))
        if nc:
            noms.setdefault(nc, set()).add(com)
    ecr = lambda chemin, obj: open(os.path.join(sortie, chemin), 'w', encoding='utf-8').write(json.dumps(obj, ensure_ascii=False, separators=(',', ':')))
    for com, L in par_com.items():
        ecr('c/%s.json' % com, L)
    for k, s in cases.items():
        ecr('t/%s.json' % k, sorted(s))
    for k, m in imm.items():
        ecr('i/%s.json' % k, m)
    ecr('n/communes.json', {k: sorted(v) for k, v in noms.items()})
    for k, d in mots.items():
        ecr('w/%s.json' % k, {m: sorted(v) for m, v in d.items()})
    meta = {'version': 1, 'fichier_du': date_fichier, 'construit_le': datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%MZ'),
            'source': source, 'licence': 'Licence Ouverte (data.gouv.fr), producteur : ANAH', 'coproprietes': n,
            'communes': len(par_com), 'pas_des_cases': PAS, 'colonnes': COLONNES}
    ecr('meta.json', meta)
    open(os.path.join(sortie, 'robots.txt'), 'w').write('User-agent: *\nDisallow: /\n')
    open(os.path.join(sortie, 'index.html'), 'w', encoding='utf-8').write(
        '<!doctype html><meta charset="utf-8"><meta name="robots" content="noindex,nofollow"><title>DV Pro, copie de secours</title>'
        '<p>Copie de secours technique du registre national des copropriétés (données publiques, ANAH, data.gouv.fr), lue par DV Pro Immo '
        'seulement quand le service public ne répond pas. Fichier du ' + date_fichier + '.</p>')
    open(os.path.join(sortie, '.nojekyll'), 'w').write('')
    return meta


if __name__ == '__main__':
    a = sys.argv[1:]
    if not a:
        sys.exit(__doc__ if __doc__ else 'usage : construire_registre.py <dossier> [--csv f] [--deps 06,83]')
    sortie = a[0]
    deps = set(a[a.index('--deps') + 1].split(',')) if '--deps' in a else None
    if '--csv' in a:
        f = a[a.index('--csv') + 1]
        flux = open(f, encoding='utf-8', errors='replace', newline='')
        meta = construire(sortie, flux, datetime.date.fromtimestamp(os.path.getmtime(f)).isoformat(), 'fichier local ' + os.path.basename(f), deps)
    else:
        url, date_fichier, titre = fichier_du_jour()
        with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'DVPro-secours/1.0'}), timeout=900) as r:
            meta = construire(sortie, io.TextIOWrapper(r, encoding='utf-8', errors='replace', newline=''), date_fichier, titre + ' : ' + url, deps)
    if meta['coproprietes'] < (1000 if deps else 500000):
        sys.exit('ARRET : seulement %d copropriétés lues, la copie précédente est gardée' % meta['coproprietes'])
    print(json.dumps(meta, ensure_ascii=False))
