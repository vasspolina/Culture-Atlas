import json, time, urllib.request, urllib.parse, sys
terms = sys.argv[1:]
out = {}
try: out = json.load(open('clients.json'))
except: pass
for t in terms:
    url = 'https://lda.gov/api/v1/clients/?' + urllib.parse.urlencode({'client_name': t, 'page_size': 25})
    n = 0
    while url:
        for a in range(5):
            try:
                d = json.load(urllib.request.urlopen(url, timeout=60)); break
            except Exception as e:
                print('retry', e, file=sys.stderr); time.sleep(5 * (a + 1))
        for x in d['results']:
            out[str(x['id'])] = {k: x.get(k) for k in ('id', 'client_id', 'name', 'general_description', 'state', 'country', 'effective_date', 'registrant')}
            n += 1
        url = d.get('next'); time.sleep(0.7)
    print(t, n, file=sys.stderr)
    json.dump(out, open('clients.json', 'w'))
print(len(out))
