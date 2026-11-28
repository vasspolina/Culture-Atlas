#!/usr/bin/env python3
"""Look for closing dates outside the records' own text. Nothing here writes institutions.json: each step writes a file
of findings under data/web_research/ for a person to read, and data/closures.json is where a finding is entered.

  wikidata   For every record with a Wikidata item (the matches kept by tools/wikidata_fields.py and tools/apply_wikidata_pins.py,
             and items named in a record's field_sources): dissolved/abolished date (P576), date of official closure (P3999),
             end time (P582), and what replaced it (P1366). -> closures_wikidata_<date>.json
  registers  For every record with statutory_filings_url: opens the register page and reads the status line where the page
             gives one (Charity Commission, ACNC, OpenKVK, ProPublica). A register dates the end of the legal entity, which is
             not the day the doors shut. -> closures_registers_<date>.json
  sites      For every record with a website: does it answer today? For one that does not, the year of the last capture the
             Internet Archive holds that answered 200. That year is "last seen", never a closing year.
             -> closures_sites_<date>.json

Usage: python3 tools/closure_sources.py wikidata|registers|sites [--date 2026-11-28] [--limit N]
"""
import json
import re
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
UA = 'culture-atlas-closures/1 (vasspolina.github.io/Culture-Atlas)'
BROWSER_UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'
args = sys.argv[1:]
step = args[0] if args else ''
date = args[args.index('--date') + 1] if '--date' in args else '2026-11-28'
limit = int(args[args.index('--limit') + 1]) if '--limit' in args else None
WEB = ROOT / 'data' / 'web_research'
records = json.load(open(ROOT / 'institutions.json', encoding='utf-8'))


def load(p):
    return json.load(open(p, encoding='utf-8')) if p.exists() else {}


def save(p, d):
    p.write_text(json.dumps(d, ensure_ascii=False, indent=1, sort_keys=True) + '\n', encoding='utf-8')


def fetch(url, ua=UA, timeout=25, data=None, accept=None):
    """(status, text). status 0 with the error's name when the request never got an answer."""
    headers = {'User-Agent': ua}
    if accept:
        headers['Accept'] = accept
    try:
        req = urllib.request.Request(url, data=data, headers=headers)
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read(600000).decode('utf-8', 'replace')
    except urllib.error.HTTPError as e:
        try:
            body = e.read(200000).decode('utf-8', 'replace')
        except Exception:
            body = ''
        return e.code, body
    except Exception as e:
        return 0, type(e).__name__ + ': ' + str(e)[:120]


# ---- wikidata -----------------------------------------------------------------------------------------------------
def qids():
    out = {}
    cache = load(WEB / 'wikidata_fields_2026-11-20.json')
    for rid, v in cache.items():
        if v.get('q') and v.get('fits'):
            out[rid] = v['q']
    pins = load(WEB / 'wikidata_pins_2026-11-03.json')
    by_name = {(r['name'], r.get('city')): r['id'] for r in records}
    for v in pins.values():
        rid = by_name.get((v.get('name'), v.get('city')))
        if rid and v.get('qid') and rid not in out and (v.get('km') or 0) <= 1:
            out[rid] = v['qid']
    for r in records:
        if r['id'] in out:
            continue
        m = re.findall(r'wikidata\.org/(?:wiki|entity)/(Q\d+)', json.dumps(r.get('field_sources') or {}))
        if len(set(m)) == 1:
            out[r['id']] = m[0]
    return out


Q = '''SELECT ?item ?label
 (GROUP_CONCAT(DISTINCT CONCAT(STR(YEAR(?d)), "/", STR(?dp)); separator="||") AS ?dissolved)
 (GROUP_CONCAT(DISTINCT STR(YEAR(?c)); separator="||") AS ?closed)
 (GROUP_CONCAT(DISTINCT STR(YEAR(?e)); separator="||") AS ?ended)
 (GROUP_CONCAT(DISTINCT ?sl; separator="||") AS ?replaced)
WHERE { VALUES ?item { %s }
 OPTIONAL { ?item rdfs:label ?label FILTER(LANG(?label) = "en") }
 OPTIONAL { ?item p:P576/psv:P576 [ wikibase:timeValue ?d ; wikibase:timePrecision ?dp ] }
 OPTIONAL { ?item wdt:P3999 ?c }
 OPTIONAL { ?item wdt:P582 ?e }
 OPTIONAL { ?item wdt:P1366 ?s . ?s rdfs:label ?sl FILTER(LANG(?sl) = "en") }
} GROUP BY ?item ?label'''


def wikidata():
    out_path = WEB / f'closures_wikidata_{date}.json'
    done = load(out_path)
    ids = qids()
    todo = [(rid, q) for rid, q in sorted(ids.items()) if rid not in done][:limit]
    print(len(ids), 'records with an item,', len(todo), 'to read')
    for i in range(0, len(todo), 150):
        chunk = todo[i:i + 150]
        q = Q % ' '.join('wd:' + x for x in sorted({q for _, q in chunk}))
        body = None
        for attempt in range(4):
            st, text = fetch('https://query.wikidata.org/sparql', data=urllib.parse.urlencode({'query': q, 'format': 'json'}).encode(),
                             accept='application/sparql-results+json', timeout=90)
            if st == 200:
                body = json.loads(text)
                break
            print('  retry', attempt + 1, st, text[:100], file=sys.stderr)
            time.sleep(20 * (attempt + 1))
        if body is None:
            print('gave up at', i)
            break
        got = {}
        for b in body['results']['bindings']:
            g = lambda k: b.get(k, {}).get('value', '')
            got[g('item').rsplit('/', 1)[1]] = {
                'label': g('label'),
                # precision 9 is a year, 10 a month, 11 a day; a decade or a century is not a year
                'dissolved': sorted({int(x.split('/')[0]) for x in g('dissolved').split('||') if x and int(x.split('/')[1]) >= 9}),
                'closed': sorted({int(x) for x in g('closed').split('||') if x}),
                'ended': sorted({int(x) for x in g('ended').split('||') if x}),
                'replaced_by': [x for x in g('replaced').split('||') if x],
            }
        for rid, qn in chunk:
            done[rid] = dict(got.get(qn, {}), q=qn)
        save(out_path, done)
        print(' ', i + len(chunk), 'read')
        time.sleep(3)
    hits = {k: v for k, v in done.items() if v.get('dissolved') or v.get('closed') or v.get('ended')}
    print(len(done), 'items read,', len(hits), 'with a closing, dissolution or end date')


# ---- registers ----------------------------------------------------------------------------------------------------
def read_register(url, text):
    host = urllib.parse.urlparse(url).netloc
    t = re.sub(r'<[^>]+>', ' ', text)
    t = re.sub(r'\s+', ' ', t)
    found = []
    pats = [
        r'(removed charity|Removed on[^.]{0,40}\d{4}|ceased to exist[^.]{0,60}|This charity (?:was|has been) removed[^.]{0,80})',
        r'(Charity status:? ?(?:Revoked|Voluntarily Revoked)[^.]{0,80}|Revocation[^.]{0,60}\d{4})',
        r'(Status:? ?(?:Dissolved|Liquidat\w+|Struck off|Deregistered|Uitgeschreven|Ontbonden|Revoked|Terminated)[^.]{0,80})',
        r'(tax-exempt status was (?:automatically )?revoked[^.]{0,80}|Terminated[^.]{0,40}\d{4})',
        r'(dissolved on[^.]{0,40}\d{4}|Dissolution[^.]{0,40}\d{4}|[Oo]ntbonden[^.]{0,40}\d{4}|uitgeschreven[^.]{0,40}\d{4})',
    ]
    for p in pats:
        for m in re.finditer(p, t, flags=re.I):
            s = m.group(1).strip()
            if s not in found:
                found.append(s[:160])
    return host, found[:4]


def registers():
    out_path = WEB / f'closures_registers_{date}.json'
    done = load(out_path)
    todo = [r for r in records if r.get('statutory_filings_url') and r['id'] not in done][:limit]
    print(len(todo), 'register pages to open')

    def one(r):
        url = r['statutory_filings_url']
        st, text = fetch(url, ua=BROWSER_UA)
        host, found = read_register(url, text) if st == 200 else (urllib.parse.urlparse(url).netloc, [])
        return r['id'], {'url': url, 'host': host, 'status': st, 'error': text[:120] if st == 0 else '', 'lines': found}

    with ThreadPoolExecutor(6) as ex:
        for n, (rid, v) in enumerate(ex.map(one, todo), 1):
            done[rid] = v
            if n % 40 == 0:
                save(out_path, done)
                print(' ', n)
    save(out_path, done)
    ok = [v for v in done.values() if v['status'] == 200]
    print(len(done), 'opened,', len(ok), 'answered,', sum(1 for v in ok if v['lines']), 'with a status line that says ended')


# ---- companies house ----------------------------------------------------------------------------------------------
def co_name(s):
    s = re.sub(r'\([^)]*\)', ' ', s.upper().replace('&AMP;', '&'))
    s = re.sub(r'\b(LIMITED|LTD|THE|TRUST|CIC|C\.I\.C\.|COMPANY|FOUNDATION)\b', ' ', s)
    return re.sub(r'[^A-Z0-9]+', ' ', s).strip()


def companies():
    """UK records: the Companies House search by the record's name. Only a company whose name equals the record's
    (Limited, The, Trust and brackets set aside) is kept, with its status line as the register prints it."""
    out_path = WEB / f'closures_companies_{date}.json'
    done = load(out_path)
    todo = [r for r in records if r.get('country') in ('UK', 'United Kingdom') and r['id'] not in done][:limit]
    print(len(todo), 'UK records to search')
    for n, r in enumerate(todo, 1):
        url = 'https://find-and-update.company-information.service.gov.uk/search/companies?q=' + urllib.parse.quote(re.sub(r'\([^)]*\)', '', r['name']).strip())
        st, text = fetch(url, ua=BROWSER_UA)
        hits = []
        if st == 200:
            for m in re.finditer(r'<li class="type-company">(.*?)</li>', text, flags=re.S):
                li = m.group(1)
                a = re.search(r'href="(/company/[A-Z0-9]+)"[^>]*>\s*(.*?)\s*</a>', li, flags=re.S)
                meta = re.search(r'<p class="meta crumbtrail">\s*(.*?)\s*</p>', li, flags=re.S)
                if a and co_name(re.sub(r'<[^>]+>', '', a.group(2))) == co_name(r['name']):
                    hits.append({'company': 'https://find-and-update.company-information.service.gov.uk' + a.group(1),
                                 'name': re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', a.group(2))).strip(),
                                 'status': re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', meta.group(1))).strip() if meta else ''})
        done[r['id']] = {'search': url, 'http': st, 'matches': hits}
        if n % 25 == 0:
            save(out_path, done)
            print(' ', n)
        time.sleep(1.2)
    save(out_path, done)
    m = {k: v for k, v in done.items() if v['matches']}
    print(len(done), 'searched,', len(m), 'with a company of the same name,',
          sum(1 for v in m.values() if any('Dissolved' in x['status'] for x in v['matches'])), 'with one dissolved')


# ---- sites --------------------------------------------------------------------------------------------------------
CTX = ssl.create_default_context()


def answers(url):
    """'up' when the address answers with a page, 'dead' when the name does not resolve or nothing listens, else what came."""
    last = ''
    for attempt in range(2):
        st, text = fetch(url, ua=BROWSER_UA, timeout=20)
        if 200 <= st < 400:
            return 'up', st
        if st in (401, 403, 405, 406, 429, 503, 999):
            return 'refused', st   # a site that turns a script away is there
        last = (st, text[:100])
        if st == 0 and ('getaddrinfo' in text or 'Name or service' in text or 'nodename' in text):
            return 'dead-dns', text[:100]
        time.sleep(2)
    if last[0] in (404, 410):
        return 'gone', last[0]
    return 'error', last


def last_capture(url):
    host = urllib.parse.urlparse(url).netloc or url
    api = 'https://web.archive.org/cdx/search/cdx?' + urllib.parse.urlencode(
        {'url': host, 'output': 'json', 'filter': 'statuscode:200', 'fl': 'timestamp,original', 'limit': '-1', 'fastLatest': 'true'})
    st, text = fetch(api, timeout=40)
    if st != 200:
        return {'error': st}
    try:
        rows = json.loads(text or '[]')
    except ValueError:
        return {'error': 'unreadable'}
    if len(rows) < 2:
        return {'none': True}
    ts, orig = rows[-1]
    return {'timestamp': ts, 'year': int(ts[:4]), 'capture': f'https://web.archive.org/web/{ts}/{orig}'}


def sites():
    out_path = WEB / f'closures_sites_{date}.json'
    done = load(out_path)
    todo = [r for r in records if r.get('website') and r['id'] not in done][:limit]
    print(len(todo), 'websites to open')

    def one(r):
        state, detail = answers(r['website'])
        return r['id'], {'website': r['website'], 'state': state, 'detail': detail}

    with ThreadPoolExecutor(12) as ex:
        for n, (rid, v) in enumerate(ex.map(one, todo), 1):
            done[rid] = v
            if n % 100 == 0:
                save(out_path, done)
                print(' ', n)
    save(out_path, done)
    down = [rid for rid, v in done.items() if v['state'] in ('dead-dns', 'gone', 'error') and 'archive' not in v]
    print(len(done), 'opened,', len(down), 'did not answer; asking the Internet Archive for their last capture')
    for n, rid in enumerate(down, 1):
        done[rid]['archive'] = last_capture(done[rid]['website'])
        time.sleep(1.5)
        if n % 20 == 0:
            save(out_path, done)
    save(out_path, done)
    import collections
    print(collections.Counter(v['state'] for v in done.values()))


if __name__ == '__main__':
    {'wikidata': wikidata, 'registers': registers, 'sites': sites, 'companies': companies}.get(step, lambda: print(__doc__))()
