import xml.etree.ElementTree as ET, json, re
from urllib.parse import urlparse
A = json.load(open(__import__('os').path.join(__import__('os').path.dirname(__file__), '../../institutions.json')))
def dom(u):
    if not u: return ''
    u = u if '://' in u else 'http://' + u
    h = urlparse(u.strip()).netloc.lower().split(':')[0]
    return re.sub(r'^(www\d?|en|de|fr|it|es|nl)\.', '', h)
def norm(s):
    s = s.lower().replace('&', ' and ')
    s = re.sub(r'[^\w ]', ' ', s)
    return ' '.join(w for w in s.split() if w not in {'the', 'de', 'der', 'die', 'das', 'la', 'le', 'les', 'el', 'of', 'et', 'und', 'and', 'van', 'del', 'di'})
ad = {}; an = {}
for a in A:
    d = dom(a.get('website'))
    if d: ad.setdefault(d, []).append(a)
    for n in [a['name']] + (a.get('aliases') or []) + re.findall(r'\((.*?)\)', a['name']):
        k = norm(re.sub(r'\s*\(.*?\)', '', n))
        if len(k) > 8: an.setdefault(k, []).append(a)
R = []
for ev, el in ET.iterparse('tr10.xml', events=('end',)):
    if el.tag != 'interestRepresentative': continue
    g = lambda p: (el.findtext(p) or '').strip()
    rec = {'id': g('identificationCode'), 'name': g('name/originalName'), 'acronym': g('acronym'), 'web': g('webSiteURL'),
           'cat': g('registrationCategory'), 'country': g('headOffice/country'), 'city': g('headOffice/city'), 'registered': g('registrationDate')[:10],
           'updated': g('lastUpdateDate')[:10], 'goals': g('goals'), 'proposals': g('EULegislativeProposals'),
           'interests': [i.text for i in el.findall('interests/interest/name')],
           'cost_min': g('financialData/closedYear/costs/range/min'), 'cost_max': g('financialData/closedYear/costs/range/max'),
           'cost_abs': g('financialData/closedYear/costs/absoluteCost'),
           'year': g('financialData/closedYear/startDate')[:4] + '–' + g('financialData/closedYear/endDate')[:4],
           'fte': g('members/membersFTE'), 'ep_passes': g('EPAccreditedNumber'),
           'grants': [(x.findtext('source'), x.findtext('amount')) for x in el.findall('financialData/closedYear/grants/grant')],
           'isMemberOf': g('structure/isMemberOf')}
    m = {}
    for a in ad.get(dom(rec['web']), []): m[a['id']] = 'website'
    for a in an.get(norm(rec['name']), []): m.setdefault(a['id'], 'name')
    if m: rec['atlas'] = m; R.append(rec)
    el.clear()
json.dump(R, open('eu_hits.json', 'w'), indent=1, ensure_ascii=False)
for r in R: print(r['id'], '|', r['name'][:55], '|', r['country'], '|', r['cat'][:30], '|', r['cost_min'], r['cost_max'], r['cost_abs'], '|', r['atlas'])
