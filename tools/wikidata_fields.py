#!/usr/bin/env python3
"""Fill website, founding year and street address from Wikidata, for records that have none.

The OpenStreetMap passes of 4 Nov 2026 (tools/osm_addresses.py, tools/osm_visiting.py) left 647 records without a
website, 1,356 without a founding year and 756 without an address. Most of those records are matched to their
OpenStreetMap object, and that object often names the space's Wikidata item (its `wikidata` tag) and its own
`website`. A record with no such tag is searched on Wikidata by name.

An item is taken for a record only when both hold:
  - its coordinates (P625) are within 1 km of the record's pin (2 km when the names are equal), and
  - one of its names (label or alias) equals one of the record's, the common words (museum, art, the city) set aside,
    so a building's item is not taken for the institution inside it, nor a namesake in the same town.

Step 1 (default) writes data/web_research/wikidata_fields_<date>.json: for each record the item, how it was found and
the values read. Step 2 (--check-sites) opens each website found and records whether it answers, in
wikidata_fields_sites_<date>.json; run it where the network is open. Step 3 (--apply) writes into institutions.json, only where the record has nothing for the field:
  website       the item's official website (P856, not ended), or the OpenStreetMap object's website tag when the
                object was matched by name; taken only when the site answered in step 2, and never a social-media
                or Wikipedia address. When Wikidata and OpenStreetMap name different sites, the record is listed
                for a hand check and nothing is written.
  year_founded  the item's inception (P571) when it is given to the year, there is one year only, and the record's
                own text gives the same year beside a founding word (founded, established, opened ...). An inception the record's
                text does not repeat that way is listed, not written: on these items it is often the building's date.
  address       the item's street address (P6375) when it holds a number and the record's own text gives the same
                street and number (Wikidata's addresses hold slips); the record's city is added when the address
                does not name it.
Each value records the Wikidata item (or the OpenStreetMap object) under field_sources with the date it was read.
The query service answers one lookup at a time from one address: two runs side by side were both cut off.
Usage: python3 tools/wikidata_fields.py [--date 2026-11-20] [--check-sites | --apply [--dry]] [--limit N]
"""
import json
import math
import re
import subprocess
import sys
import time
import unicodedata
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
UA = 'culture-atlas-address/1 (vasspolina.github.io/Culture-Atlas)'
args = sys.argv[1:]
date = args[args.index('--date') + 1] if '--date' in args else '2026-11-20'
limit = int(args[args.index('--limit') + 1]) if '--limit' in args else None
out = ROOT / 'data' / 'web_research' / f'wikidata_fields_{date}.json'
path = ROOT / 'institutions.json'
records = json.load(open(path, encoding='utf-8'))
done = json.load(open(out, encoding='utf-8')) if out.exists() else {}
# Whether each website found answered, by address: kept apart from the lookups so the two steps can run side by side.
sites_path = ROOT / 'data' / 'web_research' / f'wikidata_fields_sites_{date}.json'
SITES = json.load(open(sites_path, encoding='utf-8')) if sites_path.exists() else {}
OSM_TAGS = {}
for f in sorted((ROOT / 'data' / 'web_research').glob('osm_visiting_*.json')):
    if 'decisions' not in f.name:
        OSM_TAGS.update(json.load(open(f, encoding='utf-8')))

OSM = re.compile(r'https://www\.openstreetmap\.org/(node|way|relation)/(\d+)$')
STOP = {'the', 'of', 'and', 'for', 'de', 'del', 'della', 'di', 'du', 'des', 'la', 'le', 'el', 'museum', 'museo',
        'musee', 'museu', 'art', 'arts', 'gallery', 'galerie', 'centre', 'center', 'contemporary', 'modern',
        'foundation', 'fondation', 'fundacion', 'kunst', 'national', 'institute', 'house', 'space', 'state', 'fine',
        'city', 'museums', 'galleria', 'galeria', 'arte', 'van', 'von', 'der', 'und', 'et', 'y', 'e', 'at', 'in',
        'theatre', 'theater', 'opera', 'library', 'festival', 'biennale', 'biennial', 'cultural', 'culture'}
# Items are read forty at a time, with their names in these languages.
STEP = 40
LANGS = 'en|de|fr|es|it|nl|pt|ru|ja|zh|ko|ar|tr|pl|sv|da|nb|fi|cs|hu|el|uk|he|id|ro|ca|hr|sr|bg|fa|hi|th|vi'
SOCIAL = ('facebook.com', 'instagram.com', 'twitter.com', 'x.com', 'linkedin.com', 'youtube.com', 'wikipedia.org',
          'wikimedia.org', 'tripadvisor.', 'google.', 'vk.com', 't.me', 'weibo.com', 'tiktok.com')


def fold(s):
    s = unicodedata.normalize('NFKD', s or '')
    return ''.join(c for c in s if not unicodedata.combining(c)).lower()


def words(s):
    return {w for w in re.findall(r'[^\W_]{3,}', fold(s)) if w not in STOP}


def km(a, b, c, d):
    p = math.pi / 180
    h = math.sin((c - a) * p / 2) ** 2 + math.cos(a * p) * math.cos(c * p) * math.sin((d - b) * p / 2) ** 2
    return 12742 * math.asin(math.sqrt(h))


def get(params):
    url = 'https://www.wikidata.org/w/api.php?' + urllib.parse.urlencode(dict(params, format='json'))
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': UA})
            with urllib.request.urlopen(req, timeout=60) as r:
                body = json.load(r)
            time.sleep(2)
            return body
        except Exception as e:  # network trouble: wait and try again, then give up on this request
            print('  retry', attempt + 1, e, file=sys.stderr)
            time.sleep(20 * (attempt + 1))
    return None


def save():
    out.write_text(json.dumps(done, ensure_ascii=False, indent=1), encoding='utf-8')


def osm_of(r):
    """The record's OpenStreetMap object, and whether it was matched by the space's name (not by its address)."""
    fs = r.get('field_sources') or {}
    for key in ('coordinates', 'address'):
        e = fs.get(key) or {}
        for u in e.get('urls') or []:
            m = OSM.match(u)
            if m:
                return m.group(1)[0].upper() + m.group(2), u, (e.get('basis') or '').startswith('OpenStreetMap, name')
    return None, None, False


QUERY = """SELECT ?item (SAMPLE(?coord) AS ?c) (GROUP_CONCAT(DISTINCT STR(?site); separator="||") AS ?sites)
 (GROUP_CONCAT(DISTINCT STR(?y); separator="||") AS ?years) (GROUP_CONCAT(DISTINCT CONCAT(LANG(?addr), ":", STR(?addr)); separator="||") AS ?addrs)
 (GROUP_CONCAT(DISTINCT STR(?name); separator="||") AS ?names) (SAMPLE(?en) AS ?label) WHERE {
 %s
 OPTIONAL { ?item wdt:P625 ?coord }
 OPTIONAL { ?item wdt:P856 ?site . FILTER NOT EXISTS { ?item p:P856 ?st . ?st ps:P856 ?site ; pq:P582 ?end } }
 OPTIONAL { ?item p:P571 ?is . ?is psv:P571 ?iv . ?iv wikibase:timeValue ?t ; wikibase:timePrecision ?prec .
            FILTER(?prec >= 9) FILTER NOT EXISTS { ?is wikibase:rank wikibase:DeprecatedRank } BIND(YEAR(?t) AS ?y) }
 OPTIONAL { ?item wdt:P6375 ?addr }
 OPTIONAL { ?item rdfs:label ?en . FILTER(LANG(?en) = "en") }
 OPTIONAL { { ?item rdfs:label ?name } UNION { ?item skos:altLabel ?name } FILTER(LANG(?name) IN (%s)) }
} GROUP BY ?item"""


SEARCH = """SERVICE wikibase:mwapi { bd:serviceParam wikibase:endpoint "www.wikidata.org" ; wikibase:api "EntitySearch" ;
   mwapi:search "%s" ; mwapi:language "en" ; mwapi:limit 6 . ?item wikibase:apiOutputItem mwapi:item . }"""


def items(qs=None, search=None):
    """The values this tool uses for a list of Wikidata items, or for the items a name search finds, read through the
    query service: a full item is large (the Louvre's runs to megabytes), the answer to this query is a few lines an
    item, and the search runs inside the same request. None when the request failed."""
    where = 'VALUES ?item { %s }' % ' '.join('wd:' + x for x in qs) if qs else SEARCH % search.replace('\\', ' ').replace('"', ' ')
    q = QUERY % (where, ', '.join('"%s"' % x for x in LANGS.split('|')))
    data = urllib.parse.urlencode({'query': q, 'format': 'json'}).encode()
    for attempt in range(4):
        try:
            req = urllib.request.Request('https://query.wikidata.org/sparql', data=data,
                                         headers={'User-Agent': UA, 'Accept': 'application/sparql-results+json'})
            with urllib.request.urlopen(req, timeout=90) as r:
                body = json.load(r)
            time.sleep(2)
            break
        except Exception as e:
            print('  retry', attempt + 1, e, file=sys.stderr)
            time.sleep(20 * (attempt + 1))
    else:
        return None
    out = {}
    for b in body['results']['bindings']:
        g = lambda k: b.get(k, {}).get('value', '')
        v = {'q': g('item').rsplit('/', 1)[1], 'label': g('label'), 'names': sorted(x for x in g('names').split('||') if x)[:80]}
        m = re.match(r'Point\(([-\d.eE]+) ([-\d.eE]+)\)', g('c'))
        if m:
            v['lat'], v['lon'] = float(m.group(2)), float(m.group(1))
        v['websites'] = [x for x in g('sites').split('||') if x]
        v['inception'] = sorted({int(x) for x in g('years').split('||') if re.fullmatch(r'\d{3,4}', x)})
        v['addresses'] = [{'lang': x.split(':', 1)[0], 'text': x.split(':', 1)[1]} for x in g('addrs').split('||') if ':' in x]
        out[v['q']] = v
    return out


def fits(r, v):
    """Is this item the record's space? Distance from the pin, and one of the item's names equal to one of the record's
    once the common words (museum, art, the city) are set aside. A shared word alone is not enough: Lismore Castle Arts
    is not Lismore Castle, Kistefos is not the Kistefos wood pulp mill, and the Uffizi is not its square."""
    if 'lat' not in v or r.get('lat') is None:
        return False, 'no coordinates'
    dist = km(r['lat'], r['lon'], v['lat'], v['lon'])
    mine = [r['name']] + (r.get('aliases') or [])
    mine += [re.sub(r'\s*\(.*?\)\s*', ' ', x).strip() for x in mine if '(' in x] + re.findall(r'\(([^)]{3,})\)', r['name'])
    same = {fold(x).strip() for x in mine} & {fold(x).strip() for x in v['names']}
    city = words(r.get('city') or '')
    sets = [words(x) - city for x in mine]
    alike = [w for w in (words(x) - city for x in v['names']) if w and w in sets]
    if dist > (2 if same else 1):
        return False, f'{dist:.1f} km from the pin'
    if not same and not alike:
        return False, 'no name in common'
    return True, f'{dist * 1000:.0f} m from the pin; ' + ('same name' if same else 'same name but for common words: ' + ' '.join(sorted(alike[0])))


def fetch():
    need = [r for r in records if not (r.get('website') and r.get('year_founded') and r.get('address')) and r['id'] not in done]
    if limit:
        need = need[:limit]
    tagged, search = {}, []
    for r in need:
        o, url, by_name = osm_of(r)
        q = (OSM_TAGS.get(o) or {}).get('wikidata') if o else None
        basis = ((r.get('field_sources') or {}).get('coordinates') or {}).get('basis') or ''
        m = re.match(r'Wikidata (Q\d+)', basis)
        if q and re.fullmatch(r'Q\d+', q):
            tagged.setdefault(q, []).append((r, 'OpenStreetMap object ' + url))
        elif m:
            tagged.setdefault(m.group(1), []).append((r, 'pin'))
        else:
            search.append(r)
    print(len(need), 'records;', len(tagged), 'items named by OpenStreetMap or the pin;', len(search), 'to search by name')
    qs = list(tagged)
    for i in range(0, len(qs), STEP):
        got = items(qs[i:i + STEP])
        if got is None:
            continue                 # the request failed: these records are asked again on the next run
        for q in qs[i:i + STEP]:
            for r, how in tagged[q]:
                v = got.get(q)
                if not v or not (v['names'] or v['label']):
                    done[r['id']] = {'how': how, 'none': True}
                    continue
                ok, why = fits(r, v)
                done[r['id']] = dict(v, how=how, fits=ok, why=why)
        save()
        print(' read', min(i + STEP, len(qs)), 'of', len(qs), flush=True)
    for n, r in enumerate(search, 1):
        names = [r['name']] + [a for a in (r.get('aliases') or []) if a != r['name']][:1]
        short = re.sub(r'\s*\(.*?\)\s*', ' ', r['name']).strip()
        if short != r['name']:
            names.insert(1, short)
        found, failed = None, False
        for nm in names[:2]:
            got = items(search=nm)
            if got is None:
                failed = True
                continue
            for v in got.values():
                ok, why = fits(r, v)
                if ok:
                    found = dict(v, how='name search', fits=True, why=why)
                    break
            if found:
                break
        if failed and not found:
            continue                 # asked again on the next run
        done[r['id']] = found or {'how': 'name search', 'none': True}
        if n % 20 == 0 or n == len(search):
            save()
            print(' searched', n, 'of', len(search), flush=True)
    save()
    print('wrote', out.relative_to(ROOT), 'with', len(done), 'rows')


def host(u):
    h = (urllib.parse.urlparse(u).hostname or '').lower()
    return h[4:] if h.startswith('www.') else h


def site_candidates(r, v):
    """Websites offered for a record: Wikidata's, and the OpenStreetMap object's own when it was matched by name."""
    c = []
    if v.get('fits'):
        c += [(u, 'wikidata') for u in v.get('websites') or []]
    o, url, by_name = osm_of(r)
    t = OSM_TAGS.get(o) or {}
    if o and by_name:
        for k in ('website', 'contact:website'):
            if t.get(k):
                c.append((t[k].split(';')[0].strip(), 'osm'))
    keep = []
    for u, src in c:
        if not re.match(r'https?://', u):
            u = 'https://' + u
        if any(s in host(u) for s in SOCIAL) or not host(u) or '.' not in host(u):
            continue
        if (u, src) not in keep:
            keep.append((u, src))
    return keep


def check_sites():
    by_id = {r['id']: r for r in records}
    todo = []
    for rid, v in done.items():
        r = by_id.get(rid)
        if not r or r.get('website'):
            continue
        for u, src in site_candidates(r, v):
            if u not in SITES and u not in [x for _, x in todo]:
                todo.append((rid, u))
    print(len(todo), 'websites to open')
    for n, (rid, u) in enumerate(todo, 1):
        status = None
        for method in ('HEAD', 'GET'):
            try:
                req = urllib.request.Request(u, method=method, headers={'User-Agent': 'Mozilla/5.0 (compatible; culture-atlas-linkcheck/1)'})
                with urllib.request.urlopen(req, timeout=20) as resp:
                    status = {'status': resp.status, 'final': resp.geturl()}
                break
            except urllib.error.HTTPError as e:
                status = {'status': e.code}
                if e.code not in (403, 405, 406, 429, 501):
                    break
            except Exception as e:
                status = {'error': type(e).__name__ + ': ' + str(e)[:80]}
        SITES[u] = status
        if n % 25 == 0 or n == len(todo):
            sites_path.write_text(json.dumps(SITES, ensure_ascii=False, indent=1), encoding='utf-8')
            print(' opened', n, 'of', len(todo), flush=True)


# Read by hand on 20 Nov 2026 and not written, though the tests pass:
REJECTED_ADDRESS = {
    'muac-mexico-city': 'the postcode is cut to four digits (4510 for 04510)',
    'biblioteca-nacional-de-cuba-jose-marti': 'it holds a postal box',
    'texaf-bilembo': 'the country is written with a dash (Congo - Kinshasa)',
    'mca-denver-denver': 'the street is in capitals',
}
FOUNDING = r'(?:found(?:ed|ing)|established|set up|created|opened|inaugurated|began|started|incorporated)'
CJK = re.compile('[\u3000-\u9fff]')


def record_sentences(r):
    d = r.get('details') if isinstance(r.get('details'), dict) else {}
    parts = [r.get('watch') or '', r.get('highlight') or '', r.get('affiliations_note') or ''] + (d.get('overview') or [])
    return [sent for part in parts for sent in re.split(r'(?<=[.;])\s+', part)]


def names_year(r, year):
    """Does the record's own text give this year as the year the space was founded or opened? The year has to stand
    next to a founding word with no other year between them: "Established in 1993 and in its current building since
    2011" gives 1993, not 2011, and a year the text gives for the building alone is not the space's."""
    y = str(year)
    near = r'(?:(?!\b\d{4}\b)[^.;]){0,70}?'
    rx = re.compile(r'\b' + FOUNDING + r'\b' + near + r'\b' + y + r'\b|\b' + y + r'\b' + near + r'\b' + FOUNDING + r'\b', re.I)
    return any(rx.search(sent) for sent in record_sentences(r))


def names_address(r, a):
    """Does the record's own text give this street and number? Wikidata's street addresses hold slips (MASP at
    "Avenida Paulista, 157"), so one is written only where the record's sourced text agrees."""
    street = re.split(r',', a)[0]
    nums = re.findall(r'(?<![\w-])\d{1,5}[a-zA-Z]?(?![\w-])', street)
    names = [w for w in re.findall(r'[^\W\d_]{4,}', fold(street)) if w not in ('street', 'avenue', 'road', 'strasse', 'calle', 'avenida', 'place', 'plein', 'boulevard')]
    if not nums or not names:
        return False
    text = fold(' '.join(record_sentences(r)))
    return any(re.search(r'(?<![\w-])' + re.escape(n.lower()) + r'(?![\w-])', text) for n in nums) and any(w in text for w in names)


def site_url(u, status):
    """The address to store: where the site sent the visitor when that is the same site over https, else as given."""
    final = (status or {}).get('final') or ''
    if final.startswith('https://') and host(final) == host(u) and urllib.parse.urlparse(final).path in ('', '/', urllib.parse.urlparse(u).path):
        return final
    return u


def apply(dry):
    written = {'website': [], 'year_founded': [], 'address': []}
    review = {'website: Wikidata and OpenStreetMap differ': [], 'website: did not answer': [],
              'year_founded: the record does not name this year': [], 'year_founded: more than one year': [],
              'address: no number': [], 'address: the record does not give this street and number': []}
    for r in records:
        v = done.get(r['id'])
        if not v or v.get('none'):
            continue
        fs = r.get('field_sources')
        fs = dict(fs) if isinstance(fs, dict) else {}
        item = 'https://www.wikidata.org/wiki/' + v['q'] if v.get('q') else None
        o, osm_url, by_name = osm_of(r)
        if not r.get('website'):
            cands = site_candidates(r, v)
            live = []
            for u, src in cands:
                s = SITES.get(u) or {}
                if s.get('status') and 200 <= s['status'] < 400:
                    final = s.get('final') or u
                    # A site that answers by sending the visitor to another host (a parked domain, a ministry portal) is not taken.
                    if host(final).split('.')[-2:] == host(u).split('.')[-2:]:
                        live.append((u, src))
                elif cands:
                    review['website: did not answer'].append(f"{r['id']}: {u} {s.get('status') or s.get('error') or 'not opened'}")
            hosts = {'.'.join(host(u).split('.')[-2:]) for u, _ in live}
            if len(hosts) > 1:
                review['website: Wikidata and OpenStreetMap differ'].append(f"{r['id']}: " + ', '.join(u for u, _ in live))
            elif live:
                # One site given in several languages (kanazawa21.jp/tc/, /en/ ...): the English page, else the shortest address.
                live.sort(key=lambda x: ('/en' not in urllib.parse.urlparse(x[0]).path, len(x[0])))
                u, src = live[0]
                r['website'] = site_url(u, SITES.get(u))
                fs['website'] = {'urls': [item if src == 'wikidata' else osm_url],
                                 'basis': ('Wikidata, official website (P856)' if src == 'wikidata' else 'OpenStreetMap, website tag')
                                 + '; the site answered on ' + date, 'retrieved': date}
                written['website'].append(r['id'])
        if not v.get('fits'):
            if fs != (r.get('field_sources') or {}):
                r['field_sources'] = fs
            continue
        if not r.get('year_founded') and v.get('inception'):
            if len(v['inception']) > 1:
                review['year_founded: more than one year'].append(f"{r['id']}: {v['inception']}")
            elif names_year(r, v['inception'][0]):
                r['year_founded'] = v['inception'][0]
                fs['year_founded'] = {'urls': [item], 'basis': 'inception (Wikidata, P571); the record\'s own text names the same year',
                                      'retrieved': date}
                written['year_founded'].append(r['id'])
            else:
                review['year_founded: the record does not name this year'].append(f"{r['id']}: {v['inception'][0]}")
        if not r.get('address') and v.get('addresses'):
            a = next((x for x in v['addresses'] if x['lang'] == 'en'), v['addresses'][0])['text'].strip()
            if not re.search(r'\d', a) or len(a) <= 8 or CJK.search(a):
                review['address: no number'].append(f"{r['id']}: {a}")
            elif r['id'] in REJECTED_ADDRESS:
                review['address: the record does not give this street and number'].append(f"{r['id']}: {a} ({REJECTED_ADDRESS[r['id']]})")
            elif len({x['text'] for x in v['addresses'] if not CJK.search(x['text'])}) > 2 or not names_address(r, a):
                review['address: the record does not give this street and number'].append(f"{r['id']}: {a}")
            else:
                city = r.get('city') or ''
                if city and fold(city) not in fold(a):     # "600 Museum Way" alone does not say where
                    a = f'{a}, {city}'
                r['address'] = a
                fs['address'] = {'urls': [item], 'basis': 'Wikidata, street address (P6375); the record\'s own text gives the same street and number',
                                 'retrieved': date}
                written['address'].append(r['id'])
        if fs != (r.get('field_sources') or {}):
            r['field_sources'] = fs
    for k, ids in written.items():
        print(k, 'written on', len(ids), 'records')
    for k, rows in review.items():
        print(k + ':', len(rows))
    decisions = ROOT / 'data' / 'web_research' / f'wikidata_fields_decisions_{date}.json'
    if dry:
        print('dry run: nothing written')
        return
    decisions.write_text(json.dumps({'written': written, 'for a hand check': review}, ensure_ascii=False, indent=1), encoding='utf-8')
    path.write_text(json.dumps(records, ensure_ascii=True, indent=2), encoding='utf-8')
    subprocess.run([sys.executable, str(ROOT / 'tools' / 'clean_data.py')], check=True)
    subprocess.run([sys.executable, str(ROOT / 'tools' / 'embed_data.py')], check=True)


if __name__ == '__main__':
    if '--check-sites' in args:
        check_sites()
    elif '--apply' in args:
        apply('--dry' in args)
    else:
        fetch()
