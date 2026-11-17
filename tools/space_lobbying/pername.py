import json, re, time, urllib.request, urllib.parse, sys
A = json.load(open(__import__('os').path.join(__import__('os').path.dirname(__file__), '../../institutions.json')))
C = json.load(open('clients.json'))
done = set()
try: done = set(json.load(open('pername_done.json')))
except: pass
us = [a for a in A if a.get('country') == 'USA']
def q(t):
    url = 'https://lda.gov/api/v1/clients/?' + urllib.parse.urlencode({'client_name': t, 'page_size': 25})
    res = []
    while url:
        for a in range(6):
            try: d = json.load(urllib.request.urlopen(url, timeout=60)); break
            except Exception as e: time.sleep(10 * (a + 1))
        else: return res
        res += d['results']; url = d.get('next') if len(res) < 100 else None; time.sleep(1.2)
    return res
for a in us:
    if a['id'] in done: continue
    names = {re.sub(r'\s*\(.*?\)', '', a['name']).strip()} | {re.sub(r'\s*\(.*?\)', '', x).strip() for x in re.findall(r'\((.*?)\)', a['name'])}
    for n in names:
        n = re.sub(r'^the\s+', '', n, flags=re.I)
        if len(n) < 4: continue
        for x in q(n):
            C[str(x['id'])] = {k: x.get(k) for k in ('id', 'client_id', 'name', 'general_description', 'state', 'country', 'effective_date', 'registrant')}
    done.add(a['id'])
    json.dump(C, open('clients.json', 'w')); json.dump(sorted(done), open('pername_done.json', 'w'))
print(len(done), len(C))
