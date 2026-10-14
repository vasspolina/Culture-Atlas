#!/usr/bin/env python3
"""Apply the address audit to institutions.json, then run tools/clean_data.py and tools/embed_data.py.

Input: the rows the address-audit workflow returned (one JSON file per slice, each a list of
{id, a, b, agreed}) and data/web_research/address_audit_input.json (id, kind, existing).

  kind "verify": the record already has an address. One independent search pass looked for it without being shown it.
      pass finds the same address     -> kept, and its source URLs are recorded.
      pass finds a different address  -> a conflict. It is written to the conflicts file for a second pass; this script
                                         replaces the address only when that second pass agrees with the first.
      pass finds nothing              -> left as it was.
  kind "fill": the record has no address. Two independent passes must agree (same street number, same street word);
      the address is written with the institution's own site first among the source URLs.

Nothing is written that a search result did not state. A value that names only a city and a country is not an address.
Usage: python3 tools/apply_address_audit.py rows_a.json rows_b.json ... [--adjudicated rows_conflicts.json] [--date 2026-10-14]
"""
import html
import json
import re
import sys
import unicodedata
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
args = sys.argv[1:]
date = '2026-10-14'
adjud = None
files = []
while args:
    a = args.pop(0)
    if a == '--date':
        date = args.pop(0)
    elif a == '--adjudicated':
        adjud = args.pop(0)
    else:
        files.append(a)


def norm(t):
    t = unicodedata.normalize('NFKD', (t or '').lower())
    return re.sub(r'[^a-z0-9]+', ' ', ''.join(c for c in t if not unicodedata.combining(c))).strip()


def addr_match(a, b):
    ta, tb = norm(a).split(), norm(b).split()
    if not ta or not tb:
        return False
    da, db = [t for t in ta if re.search(r'\d', t)], [t for t in tb if re.search(r'\d', t)]
    words = lambda x: [t for t in x if len(t) >= 4 and not re.search(r'\d', t)]
    wa = set(words(ta))
    shared = [t for t in words(tb) if t in wa]
    if da and db:
        short, long_ = (da, set(db)) if len(da) <= len(db) else (db, set(da))
        return all(t in long_ for t in short) and len(shared) >= 1
    long_shared = [t for t in set(ta) & set(tb) if len(t) >= 5]
    return len(long_shared) >= 3 or len(set(ta) & set(tb)) / len(set(ta) | set(tb)) >= 0.6   # no street number on either side: name the same street or building


def city_only(addr, rec):
    known = set(norm(rec.get('city')).split()) | set(norm(rec.get('country')).split()) | {'united', 'kingdom', 'states', 'of', 'america', 'usa', 'uk', 'the', 'republic'}
    return set(norm(addr).split()) <= known


def host(u):
    return (urlparse(u).hostname or '').lower().removeprefix('www.')


def keep_urls(urls, site):
    sd = host(site) if site else ''
    seen, out = set(), []
    for u in urls or []:
        if not u.startswith('http') or u in seen:
            continue
        seen.add(u)
        h = host(u)
        if h in ('wikipedia.org', 'wikipedia.com') or h.split('.')[0] in ('dev', 'staging', 'test', 'stage'):
            continue
        out.append(u)

    def rank(u):
        h = host(u)
        if sd and (h == sd or h.endswith('.' + sd) or sd.endswith('.' + h)):
            return 0
        return 1 if 'wikipedia.org' in h else 2
    out.sort(key=rank)
    if out and rank(out[0]) == 0:
        out = [u for u in out if rank(u) == 0] + [u for u in out if rank(u) == 1][:1]
    return out[:3]


records = json.load(open(ROOT / 'institutions.json', encoding='utf-8'))
meta = {r['id']: r for r in json.load(open(ROOT / 'data/web_research/address_audit_input.json', encoding='utf-8'))}
by_id = {}
for r in records:
    by_id.setdefault(r['id'], []).append(r)
rows = {}
for f in files:
    for r in json.load(open(f, encoding='utf-8')):
        rows[r['id']] = r
second = {}
if adjud:
    for r in json.load(open(adjud, encoding='utf-8')):
        second[r['id']] = r

decisions, conflicts = [], []


def put(rid, address, urls, how):
    (rec,) = by_id[rid]
    if address is not None:
        rec['address'] = html.unescape(address)
    fs = rec.setdefault('field_sources', {})
    fs['address'] = {'urls': urls, 'basis': 'address', 'retrieved': date}


for rid, row in rows.items():
    m = meta.get(rid)
    if not m or rid not in by_id or len(by_id[rid]) != 1:
        continue
    rec = by_id[rid][0]
    site = rec.get('website') or ''
    a = row.get('a') or {}
    b = row.get('b') or {}
    if m['kind'] == 'verify':
        found = (a.get('address') or '').strip()
        if not found or city_only(found, rec):
            decisions.append({'id': rid, 'result': 'unverified', 'existing': m['existing']})
        elif addr_match(found, m['existing']):
            urls = keep_urls(a.get('address_urls'), site)
            if urls:
                put(rid, None, urls, 'confirm')
                decisions.append({'id': rid, 'result': 'confirmed', 'existing': m['existing'], 'found': found})
            else:
                decisions.append({'id': rid, 'result': 'unverified', 'existing': m['existing'], 'found': found, 'why': 'no usable url'})
        else:
            s = second.get(rid)
            sb = (s.get('agreed') or ((s.get('a') or {}).get('address') or '')).strip() if s else ''
            if s and sb and addr_match(found, sb) and not city_only(found, rec):
                urls = keep_urls(a.get('address_urls') + ((s.get('a') or {}).get('address_urls') or []), site)
                if urls:
                    put(rid, found, urls, 'replace')
                    decisions.append({'id': rid, 'result': 'replaced', 'existing': m['existing'], 'found': found, 'second': sb})
                    continue
            if s and sb and addr_match(m['existing'], sb):
                urls = keep_urls((s.get('a') or {}).get('address_urls'), site)
                if urls:
                    put(rid, None, urls, 'confirm')
                    decisions.append({'id': rid, 'result': 'confirmed', 'existing': m['existing'], 'found': sb, 'first_pass_differed': found})
                    continue
            decisions.append({'id': rid, 'result': 'conflict', 'existing': m['existing'], 'found': found, 'second': sb})
            conflicts.append({'id': rid, 'existing': m['existing'], 'found': found, 'urls': a.get('address_urls')})
    else:
        agreed = row.get('agreed')
        if not agreed:
            addr_a, addr_b = (a.get('address') or '').strip(), (b.get('address') or '').strip()
            # One pass found an address on the institution's own site and the other found nothing: the institution's own page
            # stating it is enough. A second, different address from the other pass is a disagreement and stays out.
            only = a if (addr_a and not addr_b) else b if (addr_b and not addr_a) else None
            sd = host(site) if site else ''
            own = [u for u in (only or {}).get('address_urls') or [] if sd and (host(u) == sd or host(u).endswith('.' + sd) or sd.endswith('.' + host(u)))]
            if only and own and not city_only(only['address'], rec):
                put(rid, only['address'].strip(), keep_urls(only['address_urls'], site), 'fill')
                decisions.append({'id': rid, 'result': 'filled_own_site', 'address': only['address'].strip()})
                continue
            decisions.append({'id': rid, 'result': 'none' if not addr_a and not addr_b else 'disagree', 'a': addr_a, 'b': addr_b})
            continue
        if city_only(agreed, rec):
            decisions.append({'id': rid, 'result': 'city_only', 'agreed': agreed})
            continue
        ta, tb = set(norm(a['address']).split()), set(norm(b['address']).split())
        text = b['address'] if ta < tb else a['address']
        urls = keep_urls((a.get('address_urls') or []) + (b.get('address_urls') or []), site)
        if not urls:
            decisions.append({'id': rid, 'result': 'no_url', 'agreed': agreed})
            continue
        put(rid, text, urls, 'fill')
        decisions.append({'id': rid, 'result': 'filled', 'address': text})

json.dump(records, open(ROOT / 'institutions.json', 'w', encoding='utf-8'), indent=2, ensure_ascii=True)
json.dump(decisions, open(ROOT / 'data/web_research/address_audit_decisions.json', 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
if conflicts:
    json.dump(conflicts, open(ROOT / 'data/web_research/address_audit_conflicts.json', 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
tally = {}
for d in decisions:
    tally[d['result']] = tally.get(d['result'], 0) + 1
print(tally)
