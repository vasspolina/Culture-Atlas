#!/usr/bin/env python3
"""Apply a claim-by-claim source check to the records. Run clean_data.py and embed_data.py afterwards.

    python3 tools/apply_source_check.py data/source_checks/2026-11-15

The folder holds claims.json: for each checked record, its claims with a verdict (backed, backed_new, wrong, outdated,
not_found), the page that states the claim and the words quoted from it. `quote_check` is 'yes' where the page was
fetched again afterwards and the quote found on it; only those verdicts are acted on.

  sources     a page that backs a claim and is not yet cited is added to the record's sources
  wikipedia   a Wikipedia source is replaced by the page found to state the same thing
  dead        a source that answers 404 is removed, or replaced by the address it moved to; a source listed in
              fixes.json under `drop_sources` (a page about another institution) is removed, `swap_sources` replaced
  wording     corrected why_flagged and watch lines go to data/corrections.json, which clean_data.py applies
  labels      fixes.json `drop_flags` and `drop_fields`: a label or field with nothing behind it, checked by hand

Nothing is removed for being not_found: those claims are listed in to-review.md for an editor. Writes changes.json.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
run = Path(sys.argv[1])
claims = json.load(open(run / 'claims.json', encoding='utf-8'))
fixes = json.load(open(run / 'fixes.json', encoding='utf-8'))
recs = json.load(open(ROOT / 'institutions.json', encoding='utf-8'))
by_id = {r['id']: r for r in recs}
corr_path = ROOT / 'data' / 'corrections.json'
corrections = json.load(open(corr_path, encoding='utf-8'))
ok = lambda q: str(q or '').startswith('yes')
changes, review = [], []

for c in claims:
    r = by_id.get(c['id'])
    if not r:
        continue
    src = list(r.get('sources') or [])
    before = list(src)
    for w in c.get('wikipedia') or []:
        if w.get('new') and ok(w.get('quote_check')) and w['old'] in src:
            src[src.index(w['old'])] = w['new']
    for d in c.get('dead') or []:
        if d.get('gone') and d['url'] in src:
            if d.get('moved_ok') and d.get('moved_to'):
                src[src.index(d['url'])] = d['moved_to']
            else:
                src.remove(d['url'])
    for u in fixes.get('drop_sources', {}).get(c['id'], []):
        if u in src:
            src.remove(u)
    for old, new in fixes.get('swap_sources', {}).get(c['id'], {}).items():
        if old in src:
            src[src.index(old)] = new
    for cl in c['claims']:
        if cl['verdict'] == 'backed_new' and ok(cl.get('quote_check')) and 'wikipedia.org' not in cl['url']:
            src.append(cl['url'])
        if cl['verdict'] == 'not_found':
            review.append((r['name'], c['id'], cl.get('field'), cl.get('flag'), cl['claim'], cl.get('note') or ''))
    src = list(dict.fromkeys(src))
    if src != before:
        r['sources'] = src
        changes.append({'id': c['id'], 'field': 'sources', 'added': [u for u in src if u not in before],
                        'removed': [u for u in before if u not in src]})
    for field, text in (c.get('suggested') or {}).items():
        if field in ('why_flagged', 'watch') and text and c['id'] in fixes.get('accept_wording', []):
            corrections.setdefault(c['id'], {})[field] = text
            changes.append({'id': c['id'], 'field': field, 'before': r.get(field), 'after': text})
    for f in fixes.get('drop_flags', {}).get(c['id'], []):
        if f in (r.get('flags') or []):
            r['flags'].remove(f)
            changes.append({'id': c['id'], 'field': 'flags', 'removed': [f]})
    for f in fixes.get('drop_fields', {}).get(c['id'], []):
        if r.get(f):
            changes.append({'id': c['id'], 'field': f, 'removed': r.pop(f)})

json.dump(recs, open(ROOT / 'institutions.json', 'w', encoding='utf-8'), indent=2, ensure_ascii=True)
json.dump(corrections, open(corr_path, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
json.dump(changes, open(run / 'changes.json', 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
lines = ['# Claims no source was found for', '',
         'Checked on the date of this folder. Nothing here was changed on the record. Each line needs an editor: find a',
         'source, reword the claim to what a source states, or take it off the record.', '']
last = None
for name, rid, field, flag, claim, note in sorted(review, key=lambda t: tuple(str(x) for x in t)):
    if rid != last:
        lines += ['', f'## {name} (`{rid}`)', '']
        last = rid
    lines.append(f'- **{field}{" · " + flag if flag else ""}:** {claim}' + (f'  \n  {note}' if note else ''))
(run / 'to-review.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
print(len(changes), 'changes on', len({c['id'] for c in changes}), 'records;', len(review), 'claims left for review')
