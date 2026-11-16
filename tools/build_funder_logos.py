"""Builds the logos the money map sets beside a company's name (assets/funder-logos.png and assets/funder-logos.json).

For each company with a head office on record (kind 'corp' in assets/hq.json) this looks the name up on Wikidata (one batch of queries to its query service), takes
its "small logo or icon" (P8972) or else its "logo image" (P154), and saves the file from Wikimedia Commons into a cache
folder. tools/pack_funder_logos.mjs then draws every file as a one-colour mask and packs them into one sheet; the page
tints the mask in the company colour, so no logo brings its own colours onto the map.

    python3 tools/build_funder_logos.py            # look up, download, pack
    python3 tools/build_funder_logos.py --pack     # pack again from the cache, no network

A name can match the wrong Wikidata item, so every match is written to data/funder_logos_sources.json with the item's
label and description: read it after a run. WRONG lists the names that must not take a logo (a wrong match, or a body
whose logo on Commons is not its own); PICK names the item for a name the search gets wrong.
The logos are trade marks of their owners, shown to identify the funder; the source file of each is in the sources file.
"""
import json, os, re, subprocess, sys, time, unicodedata, urllib.parse, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.environ.get('LOGO_CACHE') or os.path.join(ROOT, 'build', 'funder-logos')
SOURCES = os.path.join(ROOT, 'data', 'funder_logos_sources.json')
UA = 'funder-logo-lookup/1.0 (static site build script)'

# Names that take no logo, and names whose Wikidata item is given by hand. Filled in after reading the sources file.
# Checked by hand on 16 Nov 2026 against data/funder_logos_sources.json.
WRONG = {
    'KPBS Public Media (San Diego State University)',  # matched San Diego State University; the station has no logo on Wikidata
    'Vlaamse Gemeenschapscommissie (VGC)',  # matched Video Games Chronicle; the commission has no logo on Wikidata
}
PICK = {
    'Citadel (Ken Griffin)': 'Q2974366',  # Citadel LLC, not the television series
    'Global Media & Entertainment Limited (Global)': 'Q5570585',  # the British media company, not Canada's Global TV
    'UniCredit Bank S.A. (Romania)': 'Q4682050',  # UniCredit Bank Romania, not the Hungarian bank
}

SUFFIX = re.compile(r'(,?\s+(AG|SA|S\.A\.|S\.A\.B\. de C\.V\.|Inc\.?|LLC|Ltd\.?|Limited|Corporation|Company|Co\.|plc|S\.p\.A\.|SE|'
                    r'AG & Co\. KGaA|AKTIENGESELLSCHAFT|Aktiengesellschaft|N\.V\.|Nyrt\.|a\.s\.|A/S|AD|K\.S\.C\.P\.|U\.A\.|eG|Zrt\.|Kft\.))+$')


def norm(s):
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z0-9]', '', s)


def variants(name):
    """The spellings to search: the name, the name without its brackets, what the brackets hold, each without a legal form."""
    out = [name, re.sub(r'\s*\(.*?\)', '', name).strip()]
    for inner in re.findall(r'\((.*?)\)', name):
        inner = re.sub(r'^(now|formerly)\s+', '', inner.split(',')[0]).strip()
        if len(inner) > 2: out.append(inner)
    out += [SUFFIX.sub('', v).strip(' ,') for v in list(out)]
    seen, res = set(), []
    for v in out:
        if v and v.lower() not in seen: seen.add(v.lower()); res.append(v)
    return res


SPARQL = 'https://query.wikidata.org/sparql'
LANGS = ('en', 'mul', 'de', 'fr', 'es', 'it', 'nl', 'pt')


def sparql(q):
    data = urllib.parse.urlencode({'query': q}).encode()
    for attempt in range(6):
        try:
            req = urllib.request.Request(SPARQL, data=data, headers={'User-Agent': UA, 'Accept': 'application/sparql-results+json'})
            with urllib.request.urlopen(req, timeout=120) as r:
                return json.load(r)['results']['bindings']
        except Exception as e:
            if attempt == 5: raise
            print('  query retry', e); time.sleep(15 * (attempt + 1))


def lookup_all(names):
    """Every name's Wikidata item in one batch of queries: an item whose label or alias is one of the name's spellings
    and that has a logo. Where several match, the one with the most Wikipedia articles, a small logo before a big one."""
    spell = {}
    for n in names:
        for v in ([PICK[n]] if n in PICK else variants(n)):
            spell.setdefault(v, set()).add(n)
    best, strings = {}, sorted(s for s in spell if not re.fullmatch(r'Q\d+', s))
    for i in range(0, len(strings), 60):
        vals = ' '.join(json.dumps(v, ensure_ascii=False) + '@' + l for v in strings[i:i + 60] for l in LANGS)
        rows = sparql(f"""SELECT ?s ?i ?small ?logo ?links ?label ?desc WHERE {{
          VALUES ?s {{ {vals} }}
          {{ ?i rdfs:label ?s }} UNION {{ ?i skos:altLabel ?s }}
          OPTIONAL {{ ?i wdt:P8972 ?small }} OPTIONAL {{ ?i wdt:P154 ?logo }}
          FILTER(BOUND(?small) || BOUND(?logo))
          ?i wikibase:sitelinks ?links.
          OPTIONAL {{ ?i rdfs:label ?label FILTER(LANG(?label) = "en") }}
          OPTIONAL {{ ?i schema:description ?desc FILTER(LANG(?desc) = "en") }} }}""")
        for r in rows:
            f = urllib.parse.unquote((r.get('small') or r['logo'])['value'].rsplit('/', 1)[1]).replace('_', ' ')
            m = {'item': r['i']['value'].rsplit('/', 1)[1], 'label': r.get('label', {}).get('value', ''),
                 'description': r.get('desc', {}).get('value', ''), 'file': f, 'links': int(r['links']['value'])}
            for n in spell.get(r['s']['value'], ()):
                if n not in best or m['links'] > best[n]['links']: best[n] = m
        time.sleep(2)
    picked = [n for n in names if n in PICK]
    if picked:
        ids = ' '.join('wd:' + PICK[n] for n in picked)
        for r in sparql(f"""SELECT ?i ?small ?logo ?label ?desc WHERE {{ VALUES ?i {{ {ids} }}
          OPTIONAL {{ ?i wdt:P8972 ?small }} OPTIONAL {{ ?i wdt:P154 ?logo }}
          OPTIONAL {{ ?i rdfs:label ?label FILTER(LANG(?label) = "en") }}
          OPTIONAL {{ ?i schema:description ?desc FILTER(LANG(?desc) = "en") }} }}"""):
            if not (r.get('small') or r.get('logo')): continue
            q = r['i']['value'].rsplit('/', 1)[1]
            f = urllib.parse.unquote((r.get('small') or r['logo'])['value'].rsplit('/', 1)[1]).replace('_', ' ')
            for n in picked:
                if PICK[n] == q: best[n] = {'item': q, 'label': r.get('label', {}).get('value', ''), 'description': r.get('desc', {}).get('value', ''), 'file': f, 'links': 0}
    return best


def download(fname, dest):
    # A thumbnail in one of the sizes Wikimedia keeps ready (500 px), never the original: the original of an SVG is
    # rendered on request and the servers turn away clients that ask for many of those.
    url = 'https://commons.wikimedia.org/wiki/Special:FilePath/' + urllib.parse.quote(fname.replace(' ', '_')) + '?width=500'
    for attempt in range(6):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': UA}), timeout=60) as r:
                data = r.read()
            with open(dest, 'wb') as f: f.write(data)
            return True
        except Exception as e:
            if attempt == 5: print('  could not download', fname, e); return False
            time.sleep(20 * (attempt + 1))


def main():
    os.makedirs(CACHE, exist_ok=True)
    orgs = json.load(open(os.path.join(ROOT, 'assets', 'hq.json'), encoding='utf-8'))['org']
    if '--pack' not in sys.argv:
        names = sorted({o['n'] for o in orgs.values() if o['k'] == 'corp'} - WRONG)
        matches = lookup_all(names)
        found = {}
        for n in names:
            m = matches.get(n)
            if not m: print('no logo:', n); continue
            dest = os.path.join(CACHE, norm(n) + '.img')
            if not os.path.exists(dest):
                if not download(m['file'], dest): continue
                time.sleep(1.5)
            found[n] = m
            print('ok:', n, '=', m['label'], '|', m['description'], '|', m['file'])
            with open(SOURCES, 'w', encoding='utf-8') as f:
                json.dump(found, f, ensure_ascii=False, indent=1, sort_keys=True); f.write('\n')
    src = json.load(open(SOURCES, encoding='utf-8'))
    # One line per office key for the packer: the key the map knows the funder by, and the cached file of its logo.
    jobs = []
    for key, o in orgs.items():
        m = src.get(o['n'])
        if o['k'] != 'corp' or not m or o['n'] in WRONG: continue
        path = os.path.join(CACHE, norm(o['n']) + '.img')
        if os.path.exists(path): jobs.append({'key': key, 'name': o['n'], 'path': path})
    jobs_path = os.path.join(CACHE, 'jobs.json')
    json.dump(jobs, open(jobs_path, 'w', encoding='utf-8'))
    subprocess.run(['node', os.path.join(ROOT, 'tools', 'pack_funder_logos.mjs'), jobs_path, os.path.join(ROOT, 'assets')], check=True)


if __name__ == '__main__':
    main()
