import json, collections, re
F = json.load(open('filings.json'))
A = {a['id']: a for a in json.load(open(__import__('os').path.join(__import__('os').path.dirname(__file__), '../../institutions.json')))}
DROP_ATLAS = {'recess-brooklyn-new-york', 'triple-canopy-new-york'}
DROP_NAME = {'FRESNO METROPOLITAN MUSEUM'}
rank = lambda t: (('A' in t) * 2 + ('T' in t))
S = {}
for cid, v in F.items():
    if v['atlas'] in DROP_ATLAS or v['name'] in DROP_NAME: continue
    for f in v['filings']:
        if f['type'].startswith('R'): continue
        key = (f['registrant'].upper(), f['year'], f['period'])
        s = S.setdefault(v['atlas'], {})
        if key not in s or rank(f['type']) >= rank(s[key]['type']): s[key] = f
out = {}
for aid, s in S.items():
    years = collections.defaultdict(lambda: {'self': 0, 'firms': 0, 'self_periods': set()})
    issues, gov, firms, descs = collections.Counter(), collections.Counter(), collections.Counter(), []
    for (reg, y, p), f in s.items():
        if f['expenses'] is not None:
            years[y]['self'] += float(f['expenses']); years[y]['self_periods'].add(p)
    for (reg, y, p), f in s.items():
        if f['expenses'] is None and f['income'] is not None and p not in years[y]['self_periods']:
            years[y]['firms'] += float(f['income'])
        if f['expenses'] is None: firms[f['registrant']] += 1
        for a in f['acts']:
            issues[a['issue']] += 1
            for g in a['gov']: gov[g] += 1
            if a['desc']: descs.append((y, a['desc'].strip()))
    for (reg, y, p) in s: years[y]
    tot = {y: d['self'] + d['firms'] for y, d in years.items()}
    out[aid] = {'name': A[aid]['name'], 'city': A[aid].get('city'), 'first': min(tot), 'last': max(tot),
        'total_usd': sum(tot.values()), 'by_year': {y: round(v) for y, v in sorted(tot.items())},
        'firms': firms.most_common(5), 'issues': issues.most_common(5), 'gov': gov.most_common(6),
        'recent_desc': sorted(set(descs), reverse=True)[:6], 'filings': len(s),
        'self_filer': any(f['expenses'] is not None for f in s.values())}
json.dump(out, open('summary.json', 'w'), indent=1, default=list)
for aid, o in sorted(out.items(), key=lambda kv: -kv[1]['total_usd']):
    print(f"{o['name'][:42]:42} {o['first']}-{o['last']}  ${o['total_usd']/1e3:8.0f}k  {o['filings']:3} reports  {', '.join(i for i, _ in o['issues'][:3])}")
