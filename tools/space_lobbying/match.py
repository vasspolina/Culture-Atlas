import json, re
A = json.load(open(__import__('os').path.join(__import__('os').path.dirname(__file__), '../../institutions.json')))
C = json.load(open('clients.json'))
def norm(s):
    s = s.lower().replace('&', ' and ')
    s = re.sub(r"\b(the|inc|incorporated|corp|corporation|d/b/a|dba|of|a)\b", ' ', s)
    s = re.sub(r'[^a-z0-9 ]', ' ', s)
    return ' '.join(s.split())
us = [a for a in A if a.get('country') == 'USA']
cn = {}
for c in C.values(): cn.setdefault(norm(c['name']), []).append(c)
hits = {}
for a in us:
    names = [a['name']] + (a.get('aliases') or [])
    for n in names:
        k = norm(n)
        for ck, cs in cn.items():
            if k and (k == ck or (len(k) > 12 and (k in ck))):
                for c in cs: hits.setdefault(a['id'], {})[c['id']] = c['name']
for aid, cs in hits.items():
    a = next(x for x in us if x['id'] == aid)
    print(a['name'], '|', a.get('city'), '=>', list(cs.values())[:6])
print(len(hits), 'of', len(us))
