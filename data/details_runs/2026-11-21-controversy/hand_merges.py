"""Record lines the checked findings of the controversy pass make out of date, changed by hand after the merge.

tools/add_controversy_findings.py only adds. These few lines said something a finding now corrects, or held the same
event from a weaker source. Each change is named in editor_notes.md under "To merge by hand".

Usage: python3 data/details_runs/2026-11-21-controversy/hand_merges.py institutions.json
"""
import json
import sys

p = sys.argv[1]
recs = json.load(open(p, encoding='utf-8'))
d = {r['id']: r for r in recs}
log = []

# Kassák Múzeum: the point that tied two reports about the parent museum to the Kassák said "Neither piece names the
# Kassák Museum". The Telex report added by the pass names its staff, so the tie now speaks of the two reports only
# and stands last, as a wider-context connection does.
wc = d['kassak-muzeum-budapest']['details']['wider_context']
old = next((x for x in wc if x.startswith('Neither piece names the Kassák Museum.')), None)
if old:
    wc.remove(old)
    wc.append(old.replace('Neither piece names the Kassák Museum.', 'The 444.hu and hvg.hu reports do not name the Kassák Museum.'))
    log.append('kassak-muzeum-budapest: connection point reworded and moved last')

# Temple Bar Gallery + Studios: the funding point carried the 2010 dismissal and the 2012 tribunal award from Wikipedia
# alone. The Irish Times now supports it in the wider context, so the funding point keeps only the funding.
fp = d['temple-bar-gallery-studios']['details']['funding']
i = next((k for k, x in enumerate(fp) if 'Employment Appeal Tribunal' in x), None)
if i is not None:
    fp[i] = 'Wikipedia says it relies heavily on Arts Council funding.'
    log.append('temple-bar-gallery-studios: tribunal sentence taken out of the funding point')

# Watch lines that still said "The pages read show no controversy." on records the pass gave a dispute.
for i in ('shakespeare-theatre-company', 'allen-memorial-art-museum', 'grand-rapids-art-museum'):
    w = d[i].get('watch') or ''
    if 'The pages read show no controversy.' in w:
        d[i]['watch'] = w.replace('The pages read show no controversy.', '').strip()
        log.append(f'{i}: "no controversy" sentence taken out of the watch line')

open(p, 'w', encoding='utf-8').write(json.dumps(recs, indent=2, ensure_ascii=True))
print('\n'.join(log))
