#!/usr/bin/env python3
"""Give records website links for the spaces they name that have no record of their own.

A record's text names other spaces. The page links a name to its record when the atlas has one (linkRecordSpaces in
index.html); a space with no record links to its website only when the record lists it under `links`. This script fills
`links` in three steps, each cached so a rerun only does what is new:

  extract  names of spaces in the text that the page does not already link, as written, with the records that use them
  lookup   each name in Wikidata: kept only when exactly one art institution carries that exact label or alias and it has
           an official website (P856). A generic name (National Museum, City Gallery) is never looked up.
  check    each website is fetched; kept only when it answers (2xx/3xx, or 401/403/429 from a site that blocks robots)
  apply    write the kept links into institutions.json (then run tools/embed_data.py)

Usage: python3 tools/space_websites.py extract|lookup|check|apply|report  [--cache DIR]
"""
import json, re, sys, time, collections, urllib.parse, urllib.request, concurrent.futures as cf
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ARGS = sys.argv[1:]
CACHE = Path(ARGS[ARGS.index('--cache') + 1]) if '--cache' in ARGS else ROOT / 'data' / 'space_websites'
CACHE.mkdir(parents=True, exist_ok=True)
UA = 'CultureAtlas/1.0 (https://vasspolina.github.io/Culture-Atlas/; link check)'

data = json.load(open(ROOT / 'institutions.json', encoding='utf-8'))

# The same labels and guards as linkRecordSpaces, so a name the page already links is not looked up again.
STOP = {'Collective', 'Chapter', 'Baltic', 'Void', 'Enjoy', 'Bloc', 'Kiosk', 'Guggenheim', 'National Gallery', 'Visual',
        'Basis', 'Fire Station', 'National Theatre'}
labels = {}
for x in data:
    for l in [x['name']] + (x.get('aliases') or []):
        t = re.sub(r'\s*\([^)]*\)\s*$', '', l); t = re.sub(r'\s*:.*$', '', t).strip()
        if len(t) < 4 or t == t.lower() or t in STOP: continue
        labels.setdefault(t, x['name'])
known = {k.lower() for k in labels} | {x['name'].lower() for x in data}
LABEL_RE = re.compile(r'(?<![\w-])(?:' + '|'.join(map(re.escape, sorted(labels, key=len, reverse=True))) + r')(?![\w-])')
BEFORE = re.compile(r"[A-ZÀ-Ý][\w'’.&-]* $")
AFTER = re.compile(r" (?:[A-ZÀ-Ý]|(?:of|de|del|der|di|du|des|für|for|voor|van) )")

# A space's name: capitalised words joined by short lowercase words, ending in or holding one of these.
KIND = (r"Museum|Museo|Musée|Museu|Muzeum|Múzeum|Muzej|Muzeul|Museet|Kunstmuseum|Kunsthalle|Kunstverein|Kunsthaus|"
        r"Gallery|Galerie|Galleria|Galería|Galeria|Galerija|Biennale|Biennial|Bienal|Triennale|Triennial|"
        r"Art Centre|Art Center|Arts Centre|Arts Center|Art Space|Artspace|Project Space|Kunstraum")
CAP = r"[A-ZÀ-ÝĀ-Ž0-9][\w'’&+-]*(?:\.\w[\w'’&+-]*)*"
JOIN = r"(?:of|de|del|della|dei|der|des|di|du|da|do|für|for|and|&|la|le|el|of the|de la|d'|the)"
NAME_RE = re.compile(rf"{CAP}(?: (?:{JOIN} )?{CAP})*")
KIND_RE = re.compile(rf"\b(?:{KIND})\b")
LEAD = re.compile(r"^(?:(?:Member of|Won|Renamed|Listed|The|In|At|From|With|And|By|For|Of|On|Its|His|Her|Their|A|An|When|While|After|Before|Since|As|"
                  r"Both|Former|Then|Like|Including|Unlike|Via|Under|Between|Per|Also|Only|Today|Now|Until|Through|"
                  r"During|Following|Against|About|Both|Each|Every|This|That|These|Those|Our|Your|New)\s+)+", re.I)
ORD = re.compile(r"^(?:\d{4}|\d+(?:st|nd|rd|th)|[IVXL]+\.?|First|Second|Third|Fourth|Fifth|Sixth|Seventh|Eighth|Ninth|Tenth)\s+")
# Words that say what a place is, not which: a name made only of these and a kind word is generic.
GENERIC = set('national state city municipal regional provincial county town public royal central international '
              'contemporary modern art arts fine decorative applied history historical natural science sciences '
              'design craft crafts photography photo film cinema music theatre literature literary folk ethnographic '
              'ethnography ethnology archaeological archaeology military war maritime railway transport children '
              'jewish islamic african american asian european latin indigenous new old young great little grand '
              'museum museo musée museu muzeum gallery galerie galleria galería galeria biennale biennial bienal '
              'triennale triennial centre center space project kunsthalle kunstverein kunsthaus foundation fondation '
              'house hall palace collection collections institute of for and the de del la le des der di du da do '
              'el y e et und für arte kunst nacional nazionale nationale national-museum year district local '
              'university college school library libraries archive archives memorial sports space internet'.split())

def strings(v, key=''):
    if key in ('url', 'urls', 'sources', 'source', 'href', 'id', 'outlet', 'cite', 'links'): return
    if isinstance(v, str): yield v
    elif isinstance(v, list):
        for i in v: yield from strings(i)
    elif isinstance(v, dict):
        for k, i in v.items(): yield from strings(i, k)

SKIP = {'name', 'aliases', 'id', 'sources', 'lat', 'lon', 'city', 'country', 'location', 'website', 'url', 'links'}

def masked(s, own):
    """The text with every name the page already links blanked out."""
    out = list(s)
    for m in LABEL_RE.finditer(s):
        if labels[m.group(0)] == own and False: pass
        if BEFORE.search(s[max(0, m.start() - 40):m.start()]) or AFTER.match(s[m.end():m.end() + 6]): continue
        for i in range(m.start(), m.end()): out[i] = ' '
    return ''.join(out)

def is_generic(name):
    words = re.findall(r"[\w'’-]+", name.lower())
    return all(w in GENERIC for w in words)

def extract():
    uses = collections.defaultdict(set)
    for x in data:
        for k, v in x.items():
            if k in SKIP: continue
            for s in strings(v, k):
                s = re.sub(r'"[^"]*"|“[^”]*”|‘[^’]*’|«[^»]*»', lambda m: ' ' * len(m.group(0)), s)  # quoted titles are works
                s = masked(s, x['name'])
                for m in NAME_RE.finditer(s):
                    t = m.group(0)
                    if not KIND_RE.search(t): continue
                    t = ORD.sub('', LEAD.sub('', t)).strip(" ,.;:'’&-")
                    t = re.sub(r"\s+(?:of|de|del|der|des|di|du|da|do|for|für|and|&|the|la|le)$", '', t)
                    t = re.sub(r"'s$|’s$", '', t)
                    t = re.sub(r"(?:\s+(?:\d+|Inc|Ltd|Partners?|Grant|Day|Drive|Committee|Coalition))+$", '', t)
                    t = re.sub(r"^(?:the|and|for|of|or|to|at)\s+", '', t)
                    if len(t.split()) < 2 or not KIND_RE.search(t) or is_generic(t) or t.lower() in known: continue
                    # A piece of a longer name in the same sentence is the longer name's, not its own.
                    uses[t].add(x['name'])
    out = {t: sorted(r) for t, r in sorted(uses.items(), key=lambda kv: (-len(kv[1]), kv[0]))}
    json.dump(out, open(CACHE / 'names.json', 'w'), ensure_ascii=False, indent=1)
    print('names', len(out), 'records', len(set().union(*map(set, out.values()))))

def get(url, tries=8):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': UA})
            return json.load(urllib.request.urlopen(req, timeout=30))
        except Exception as e:
            if i == tries - 1: raise
            # Wikidata asks a client that goes too fast to wait; it says how long.
            wait = int(getattr(e, 'headers', {}).get('Retry-After', 0) or 0) if getattr(e, 'code', 0) == 429 else 0
            time.sleep(max(wait, 5 * (i + 1)))

ARTY = re.compile(r"museum|gallery|galler|art|kunst|biennial|biennale|bienal|triennial|triennale|exhibition|cultural|"
                  r"culture|foundation|collection|arts", re.I)

def lookup():
    names = json.load(open(CACHE / 'names.json'))
    path = CACHE / 'wikidata.json'
    done = json.load(open(path)) if path.exists() else {}
    todo = [n for n in names if n not in done]
    API = 'https://www.wikidata.org/w/api.php?'
    def one(n):
        q = API + urllib.parse.urlencode({'action': 'wbsearchentities', 'search': n, 'language': 'en', 'uselang': 'en',
                                          'type': 'item', 'limit': 10, 'format': 'json', 'strictlanguage': 0})
        hits = get(q).get('search', [])
        exact = [h for h in hits if (h.get('match', {}).get('text', '').lower() == n.lower())
                 and h.get('match', {}).get('type') in ('label', 'alias')]
        return n, [{'id': h['id'], 'label': h.get('label', ''), 'desc': h.get('description', '')} for h in exact]
    with cf.ThreadPoolExecutor(2) as ex:
        for i, (n, hits) in enumerate(ex.map(one, todo)):
            done[n] = {'hits': hits}
            if i % 50 == 0:
                json.dump(done, open(path, 'w'), ensure_ascii=False, indent=1); print('searched', i, '/', len(todo), flush=True)
    json.dump(done, open(path, 'w'), ensure_ascii=False, indent=1)
    # The official website and the item's kind, for every exact hit.
    ids = sorted({h['id'] for v in done.values() for h in v['hits']})
    ents = {}
    epath = CACHE / 'entities.json'
    if epath.exists(): ents = json.load(open(epath))
    need = [i for i in ids if i not in ents]
    for k in range(0, len(need), 50):
        q = API + urllib.parse.urlencode({'action': 'wbgetentities', 'ids': '|'.join(need[k:k + 50]), 'props': 'claims|sitelinks',
                                          'format': 'json'})
        for qid, e in get(q).get('entities', {}).items():
            c = e.get('claims', {})
            site = [s['mainsnak'].get('datavalue', {}).get('value') for s in c.get('P856', [])
                    if s.get('rank') != 'deprecated' and s['mainsnak'].get('datavalue')]
            pref = [s['mainsnak']['datavalue']['value'] for s in c.get('P856', []) if s.get('rank') == 'preferred' and s['mainsnak'].get('datavalue')]
            ended = bool(c.get('P576') or c.get('P582'))
            ents[qid] = {'site': (pref or site or [None])[0], 'ended': ended,
                         'enwiki': e.get('sitelinks', {}).get('enwiki', {}).get('title')}
        print('entities', min(k + 50, len(need)), '/', len(need), flush=True)
        json.dump(ents, open(epath, 'w'), ensure_ascii=False, indent=1)
    json.dump(ents, open(epath, 'w'), ensure_ascii=False, indent=1)

def picked():
    """Name -> (qid, label, desc, site) where exactly one art institution with a website carries the name."""
    wd = json.load(open(CACHE / 'wikidata.json')); ents = json.load(open(CACHE / 'entities.json'))
    out, why = {}, collections.Counter()
    for n, v in wd.items():
        arty = [h for h in v['hits'] if ARTY.search(h['desc'] or '') and not re.search(r'painting|sculpture|artwork|'
                r'album|song|film\b|novel|book|journal|magazine|person|painter|artist|human|family name|given name|'
                r'disambiguation|street|station|building in|ship|edition of|exhibition held', h['desc'] or '', re.I)]
        if not v['hits']: why['no exact match'] += 1; continue
        if not arty: why['not an art place'] += 1; continue
        if len(arty) > 1: why['ambiguous'] += 1; continue
        h = arty[0]; e = ents.get(h['id'], {})
        if not e.get('site'): why['no website'] += 1; continue
        out[n] = {'qid': h['id'], 'label': h['label'], 'desc': h['desc'], 'site': e['site'], 'ended': e.get('ended')}
    return out, why

def check():
    p, why = picked()
    path = CACHE / 'checked.json'
    done = json.load(open(path)) if path.exists() else {}
    sites = sorted({v['site'] for v in p.values()} - set(done))
    if '--hosts' in ARGS:  # one batch of hosts at a time, for a sandbox that allows only named hosts
        hs = set(json.load(open(ARGS[ARGS.index('--hosts') + 1])))
        sites = [u for u in sites if urllib.parse.urlsplit(u).netloc.split(':')[0].lower() in hs]
    import ssl, http.client
    ctx = ssl.create_default_context()
    def one(u):
        for method in ('HEAD', 'GET'):
            try:
                req = urllib.request.Request(u, method=method, headers={'User-Agent': 'Mozilla/5.0 (Macintosh) CultureAtlas link check'})
                r = urllib.request.urlopen(req, timeout=25, context=ctx)
                return u, {'status': r.status, 'final': r.geturl()}
            except urllib.error.HTTPError as e:
                if method == 'HEAD' and e.code in (403, 405, 404, 400, 500, 501): continue
                return u, {'status': e.code, 'final': u}
            except Exception as e:
                if method == 'HEAD': continue
                return u, {'status': 0, 'error': type(e).__name__ + ': ' + str(e)[:80]}
    with cf.ThreadPoolExecutor(12) as ex:
        for i, (u, r) in enumerate(ex.map(one, sites)):
            done[u] = r
            if i % 50 == 0: json.dump(done, open(path, 'w'), indent=1); print('checked', i, '/', len(sites), flush=True)
    json.dump(done, open(path, 'w'), indent=1)

# Read by a person before apply (3 Nov 2026). Not a space: an agency, an award, a database, a group of museums. The wrong place:
# Wikidata's only match for the name is another institution than the one the sentence means (the Kenneth C. Griffin Gallery is a
# room at PAMM, the Museum für Neue Kunst at ZKM is not Freiburg's, the Museo Nacional de Historia Natural in the Havana record is
# Cuba's). Too close to a longer name in the same record (Neues Museum beside Neues Museum Nürnberg).
DROP = {'Institute of Museum and Library Services', 'Art Fund Museum of the Year', 'European Museum of the Year Award',
        'Digital Gallery', 'Science Museum Group', 'Griffin Gallery', 'Museum für Neue Kunst',
        'Museo Nacional de Historia Natural', 'Museo Nacional de Historia', 'Museo de Arte Moderno', 'Museo Rufino Tamayo',
        'Museum of Local Lore', 'Neues Museum'}
# A former name of the record it appears in, on another host than the record's own site: the record's own subject, no link.
SELF = {'Dakar Biennale', 'Dowse Art Gallery', 'Dowse Art Museum', 'Duke University Museum of Art', 'Nasher Museum of Art',
        'Geelong Art Gallery', 'Lewis Glucksman Gallery', 'National Gallery of Iceland', 'Presidential Palace Museum',
        'Zoma Contemporary Art Center', 'Iraq Museum', 'Gallery 4A'}

# Rechecked by hand with curl on 3 Nov 2026, after the checker failed on a redirect to a new domain: Wikidata's address -> where
# the site now lives. Each answered 200 there.
MOVED = {'http://barrickmuseum.unlv.edu/': 'https://www.unlv.edu/barrickmuseum', 'http://museum.ge/': 'https://museum.ge/',
         'http://museum.ge/index.php?lang_id=ENG&sec_id=46': 'https://museum.ge/', 'http://nonmuseum.ru/': 'https://nonmuseum.ru/',
         'http://thepacegallery.com': 'https://www.pacegallery.com/', 'http://www.hbww.org/': 'https://www.hbww.org.cn/',
         'http://www.johannjacobs.com': 'https://www.museumoflearning.org/de/about-us/johann-jacobs-museum/',
         'http://www.kerlin.ie/': 'https://www.kerlingallery.com/', 'http://www.lissongallery.com/': 'https://lisson.com/',
         'http://www.museobilbao.com/': 'https://bilbaomuseoa.eus/', 'http://www.museumhetvalkhof.nl': 'https://valkhofmuseum.nl/',
         'https://www.galerialuisastrina.com.br': 'https://www.luisastrina.com.br/',
         'https://www.kansallismuseo.fi/': 'https://suomenkansallismuseo.fi/', 'https://musee-monod.sn/': 'https://musee-monod.sn/',
         'http://www.rogerraveelmuseum.be': 'https://rogerraveelmuseum.be/'}
# Never linked: the domain now redirects to a gambling site (bassmuseum.org) or a parked search page (ugandatourism.org).
HIJACKED = {'http://www.bassmuseum.org/', 'http://www.ugandatourism.org/Uganda%20Museum.php'}

def norm(u):
    if not u: return None
    p = urllib.parse.urlsplit(u.strip()); h = p.netloc.lower().removeprefix('www.').split(':')[0]
    path = re.sub(r'/(en|it|de|fr|es|zh_TW|kr|eng|sv|nl)(/|$)', '/', p.path.lower()).rstrip('/')
    return h + re.sub(r'/(index\.(html?|php)|home(\.html)?)$', '', path)

def good():
    """Name -> pick with the records that use it, and name -> atlas record for a name that is another record's other name."""
    p, why = picked()
    chk = json.load(open(CACHE / 'checked.json'))
    names = json.load(open(CACHE / 'names.json'))
    sites = {}
    for x in data:
        for k in ('website', 'visit_url'):
            if norm(x.get(k)): sites.setdefault(norm(x.get(k)), x['name'])
    keep, alias = {}, {}
    for n, v in p.items():
        if n in DROP: why['read and dropped'] += 1; continue
        if n in SELF: why['the record itself'] += 1; continue
        rec = sites.get(norm(v['site']))
        if rec:
            others = [r for r in names[n] if r != rec]
            if others: alias[n] = rec; why['another record\'s other name'] += 1
            else: why['the record itself'] += 1
            continue
        if v['site'] in HIJACKED: why['website hijacked'] += 1; continue
        if v['site'] in MOVED:
            keep[n] = dict(v, site=MOVED[v['site']], records=names[n]); continue
        c = chk.get(v['site'], {})
        st = c.get('status', 0)
        if not (200 <= st < 400 or st in (401, 403, 429)): why['website does not answer'] += 1; continue
        keep[n] = dict(v, records=names[n])
    return keep, alias, why

def apply():
    keep, alias, why = good()
    byrec = collections.defaultdict(dict)
    for n, v in keep.items():
        for r in v['records']: byrec[r][n] = v['site']
    n = a = 0
    for x in data:
        if x['name'] in byrec:
            links = dict(x.get('links') or {})
            # A name inside the record's own name is the record itself (Museum of Fine Arts Budapest / Hungarian National Gallery).
            for k, u in byrec[x['name']].items():
                if k.lower() not in x['name'].lower(): links.setdefault(k, u)
            x['links'] = dict(sorted(links.items())); n += 1
        for name, rec in alias.items():
            if x['name'] == rec and name not in (x.get('aliases') or []):
                x['aliases'] = (x.get('aliases') or []) + [name]; a += 1
    open(ROOT / 'institutions.json', 'w', encoding='utf-8').write(json.dumps(data, ensure_ascii=True, indent=2))
    print('website links', sum(len(v['records']) for v in keep.values()), 'names', len(keep), 'records', n, 'aliases', a)

def report():
    names = json.load(open(CACHE / 'names.json'))
    keep, alias, why = good()
    print('names', len(names), 'kept', len(keep), 'aliases', alias, dict(why))

def review():
    """Every pick, for a person to read before apply: name | Wikidata label | description | website | records."""
    p, why = picked()
    print(len(p), 'picked;', dict(why))
    for n, v in p.items():
        print(f"{n} | {v['label']} | {v['desc'][:60]} | {v['site']}{' | ENDED' if v['ended'] else ''} | {v['qid']}")

{'extract': extract, 'lookup': lookup, 'check': check, 'apply': apply, 'report': report, 'review': review}[ARGS[0]]()
