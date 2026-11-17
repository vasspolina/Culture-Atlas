import json, re, time, urllib.request, urllib.parse, sys
exec(open('match.py').read().split('for aid, cs in hits.items()')[0])
MANUAL = {'lacma-los-angeles': ['LOS ANGELES COUNTY MUSEUM OF ART'], 'moca-cleveland-cleveland': ['MUSEUM OF CONTEMPORARY ART - CLEVELAND', 'MUSEUM OF CONTEMPORARY ART-CLEVELAND'], 'dia-art-foundation-beacon': ['DIA ART FOUNDATION']}
for aid, names in MANUAL.items():
    for c in C.values():
        if c['name'] in names: hits.setdefault(aid, {})[c['id']] = c['name']
F = {}
try: F = json.load(open('filings.json'))
except: pass
def get(url):
    for a in range(8):
        try: return json.load(urllib.request.urlopen(url, timeout=90))
        except Exception as e: time.sleep(8 * (a + 1))
for aid, cs in hits.items():
    for cid in cs:
        if str(cid) in F: continue
        url = 'https://lda.gov/api/v1/filings/?' + urllib.parse.urlencode({'client_id': cid, 'page_size': 25})
        rows = []
        while url:
            d = get(url); time.sleep(1.2)
            for f in d['results']:
                rows.append({'uuid': f['filing_uuid'], 'year': f['filing_year'], 'period': f['filing_period'], 'type': f['filing_type'],
                    'income': f.get('income'), 'expenses': f.get('expenses'), 'registrant': f['registrant']['name'], 'client': f['client']['name'],
                    'self': f['registrant']['name'].upper() == f['client']['name'].upper() or f.get('expenses') is not None,
                    'url': f.get('filing_document_url'),
                    'acts': [{'issue': a.get('general_issue_code_display'), 'desc': a.get('description'), 'gov': [g.get('name') for g in a.get('government_entities') or []]} for a in f.get('lobbying_activities') or []]})
            url = d.get('next')
        F[str(cid)] = {'atlas': aid, 'name': cs[cid], 'filings': rows}
        json.dump(F, open('filings.json', 'w'))
        print(aid, cs[cid], len(rows), file=sys.stderr)
json.dump({k: list(v.keys()) for k, v in hits.items()}, open('hits.json', 'w'))
