# DV Pro, copie de secours de la liste des communes (geo.api.gouv.fr, découpage administratif, données publiques).
# Créé le 12/11/2026 à la demande de TP : le 12/11 au matin, le service des communes a répondu en 10 à 14 secondes,
# ou pas du tout. Quand il ne répond pas, DV Pro lit cette copie, avec sa date.
#
# Usage :
#   python3 construire_communes.py site [adresse de la copie en ligne]
#     -> écrit site/geo/communes.json. Si le service des communes ne répond pas, la copie déjà en ligne est reprise
#        telle quelle (avec sa date d'origine) ; si elle est introuvable aussi, le programme s'arrête en erreur.
#
# Ce qui est produit :
#   site/geo/communes.json   { "fichier_du": "AAAA-MM-JJ", "source": "...", "communes": N, "colonnes": [...], "C": [[...], ...] }
#   une ligne par commune : code INSEE, nom, codes postaux, longitude et latitude du centre, rectangle (lon min, lat min, lon max, lat max), population
import datetime, json, os, sys, time, urllib.request

SOURCE = 'https://geo.api.gouv.fr/communes?fields=nom,code,codesPostaux,centre,bbox,population&format=json'
COLONNES = ['code', 'nom', 'codesPostaux', 'lon', 'lat', 'lonMin', 'latMin', 'lonMax', 'latMax', 'population']

def lire(url, delai=120):
    req = urllib.request.Request(url, headers={'User-Agent': 'DVPro-secours/1.0'})
    with urllib.request.urlopen(req, timeout=delai) as r:
        return r.read()

def depuis_service():
    err = None
    for essai in range(3):
        try:
            L = json.loads(lire(SOURCE))
            break
        except Exception as e:
            err = e; time.sleep(20 * (essai + 1))
    else:
        raise err
    C = []
    for c in L:
        try:
            lon, lat = c['centre']['coordinates'][:2]
            R = c['bbox']['coordinates'][0]; xs = [p[0] for p in R]; ys = [p[1] for p in R]
            C.append([c['code'], c['nom'], sorted(c.get('codesPostaux') or []), round(lon, 5), round(lat, 5),
                      round(min(xs), 5), round(min(ys), 5), round(max(xs), 5), round(max(ys), 5), int(c.get('population') or 0)])
        except Exception:
            continue  # commune sans centre ou sans rectangle : laissée de côté
    C.sort(key=lambda x: x[0])
    return {'fichier_du': datetime.date.today().isoformat(), 'source': 'geo.api.gouv.fr (découpage administratif, Licence Ouverte 2.0)',
            'communes': len(C), 'colonnes': COLONNES, 'C': C}

def controle(d):
    C = d.get('C') or []
    codes = {c[0] for c in C}
    assert len(C) > 30000, 'trop peu de communes : %d' % len(C)
    assert len(codes) == len(C), 'codes en double'
    for code in ('06069', '83081', '75056', '13055', '69123', '2A004', '97411'):
        assert code in codes, 'commune absente : ' + code
    g = next(c for c in C if c[0] == '06069')
    assert g[1] == 'Grasse' and '06130' in g[2] and g[5] < g[3] < g[7] and g[6] < g[4] < g[8], 'Grasse mal lue : %r' % (g,)

def main():
    site = sys.argv[1] if len(sys.argv) > 1 else 'site'
    en_ligne = sys.argv[2] if len(sys.argv) > 2 else ''
    try:
        d = depuis_service(); controle(d); origine = 'service des communes'
    except Exception as e:
        print('Service des communes : échec (%s).' % str(e)[:200])
        if not en_ligne: raise
        d = json.loads(lire(en_ligne.rstrip('/') + '/geo/communes.json', 60)); controle(d); origine = 'copie déjà en ligne, reprise telle quelle'
    os.makedirs(os.path.join(site, 'geo'), exist_ok=True)
    with open(os.path.join(site, 'geo', 'communes.json'), 'w', encoding='utf-8') as f:
        json.dump(d, f, ensure_ascii=False, separators=(',', ':'))
    print('Communes : %d, fichier du %s (%s), %.1f Mo.' % (d['communes'], d['fichier_du'], origine, os.path.getsize(os.path.join(site, 'geo', 'communes.json')) / 1e6))

if __name__ == '__main__':
    main()
