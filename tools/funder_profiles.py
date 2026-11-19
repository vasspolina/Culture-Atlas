"""Funder profiles: who a funder is and where its money comes from, for the funder page (assets/hq-detail.js).

Two steps, run from anywhere:

  python3 tools/funder_profiles.py merge [batch ...]
      Reads the researched batches (sponsor-atlas/work/ubatch/fpN-result.json, written to ubatch/FUNDERS.md), lints the
      words (SLOP.md rules that a script can see: dashes, hedges, promo words, absence lines, length), and folds the clean
      rows into data/funder_profiles.json, keyed by office key. A row the lint stops is listed and left out until fixed.
      With no batch named it reads every fpN-result.json there.

  python3 tools/funder_profiles.py build
      Writes assets/funder-profiles.json for the page: per office key the profile's sentences and sources, plus the
      influence study's `made_from` line and dated facts (data/influence_senders.json) where that study read the funder.

data/funder_profiles.json is the truth; the asset is rebuilt from it. tools/build_hq.py takes a profile's official name,
address and best source over the older office fields.
"""
import json, os, re, sys, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UBATCH = os.path.join(os.path.dirname(ROOT), 'sponsor-atlas', 'work', 'ubatch')
if not os.path.isdir(UBATCH):
    UBATCH = os.path.expanduser('~/culture-atlas/sponsor-atlas/work/ubatch')
TRUTH = os.path.join(ROOT, 'data', 'funder_profiles.json')
ASSET = os.path.join(ROOT, 'assets', 'funder-profiles.json')
SENDERS = os.path.join(ROOT, 'data', 'influence_senders.json')
ALIASES = os.path.join(ROOT, 'tools', 'hq_aliases.json')

LIMIT = {'what': 30, 'money': 25, 'arts': 30}
HEDGE = re.compile(r"\b((?-i:may)|might|reportedly|allegedly|appears? to|seems?|arguably|is said to|believed to|likely|possibly|perhaps|some say)\b", re.I)
PROMO = re.compile(r"\b(vibrant|renowned|prestigious|world-class|iconic|landmark|cutting-edge|dynamic|thriving|esteemed|pivotal|tapestry|testament|nestled|boasts?|showcases?|(?-i:fosters?)|underscores?|delves?|navigates?|ecosystem|leading|dedicated to|committed to|passionate|plays? a (?:crucial|key|vital) role|a (?:diverse|wide) range|among others|and more)\b", re.I)
ABSENCE = re.compile(r"\b(not found|no (?:public |published )?(?:information|record|details|figures?|accounts?) (?:found|published|available)|could not (?:be )?(?:find|found|confirm|read|verify)|not (?:published|available|disclosed) online|unclear|unknown)\b", re.I)
DASH = re.compile(r"[–—]| - ")
WEAK = re.compile(r"fundraiso|causeiq|grantedai|bringo|mergerlinks|lei\.bloomberg|/jobs?[./]|indeed\.|glassdoor|zoominfo|dnb\.com|opencorporates", re.I)
KINDS = {'corp', 'found', 'gov', 'priv', 'person'}


def lint(row):
    """The problems a script can see in one researched row."""
    out = []
    for f, cap in LIMIT.items():
        t = (row.get(f) or '').strip()
        if not t: continue
        n = len(t.split())
        if n > cap: out.append(f'{f}: {n} words (max {cap})')
        for rx, what in ((HEDGE, 'hedge'), (PROMO, 'promo'), (ABSENCE, 'absence'), (DASH, 'dash')):
            m = rx.search(t)
            if m: out.append(f'{f}: {what} {m.group(0)!r}')
    if not (row.get('what') or '').strip(): out.append('what: empty')
    if row.get('kind') and row['kind'] not in KINDS: out.append(f"kind: {row['kind']!r}")
    srcs = [s for s in row.get('sources') or [] if isinstance(s, str) and s.startswith('http')]
    if not srcs: out.append('sources: none')
    return out


def key_map():
    """Batch keys are office keys; an office dropped as a repeat of another hands its profile to that one."""
    al = json.load(open(ALIASES))
    return {k: v[0] for k, v in al.items() if k != 'drop' and v}


def merge(paths):
    truth = json.load(open(TRUTH)) if os.path.exists(TRUTH) else {}
    dropped = set(json.load(open(ALIASES)).get('drop', []))
    stopped, added = [], 0
    for p in paths:
        rows = json.load(open(p))
        for r in rows:
            k = r.get('key')
            if not k: continue
            if k in dropped: continue          # the office it repeated holds the profile
            probs = lint(r)
            if probs:
                stopped.append((os.path.basename(p), k, probs)); continue
            srcs = [s for s in r.get('sources') or [] if isinstance(s, str) and s.startswith('http')]
            # The best source first, with register scrapers last: the page links the first one.
            srcs.sort(key=lambda s: bool(WEAK.search(s)))
            # A wrong match the editor read as a rename (the profile names the body the museum sentences mean) stays published.
            renamed = (truth.get(k) or {}).get('renamed')
            truth[k] = {f: (r.get(f) or '').strip() for f in ('name', 'short', 'kind', 'what', 'money', 'arts', 'site', 'city', 'country', 'address', 'wrong_match', 'status')}
            truth[k]['sources'] = srcs[:5]
            truth[k]['batch'] = os.path.basename(p).replace('-result.json', '')
            if renamed and truth[k].get('wrong_match'): truth[k]['renamed'] = truth[k].pop('wrong_match')
            truth[k] = {f: v for f, v in truth[k].items() if v}
            added += 1
    json.dump(dict(sorted(truth.items())), open(TRUTH, 'w'), ensure_ascii=False, indent=1)
    print(f'{added} profiles merged, {len(truth)} in {os.path.relpath(TRUTH, ROOT)}')
    if stopped:
        print(f'{len(stopped)} rows stopped by the lint (fix in the batch file, then merge again):')
        for b, k, probs in stopped: print(f'  {b} {k}: ' + '; '.join(probs))


def build():
    truth = json.load(open(TRUTH)) if os.path.exists(TRUTH) else {}
    senders = json.load(open(SENDERS)) if os.path.exists(SENDERS) else {}
    # One body under several office keys (Arts Council England as 'artscouncilengland|UK', 'acenpo', 'artscouncilnpo|UK')
    # reads the same on every page: each key takes the profile of the first batch that researched that name.
    order = lambda p: int(re.sub(r'\D', '', p.get('batch', '')) or 999)
    first = {}
    for k, p in sorted(truth.items(), key=lambda kv: (order(kv[1]), kv[0])):
        n = (p.get('name') or '').strip().lower()
        if n and not p.get('wrong_match'): first.setdefault(n, p)
    out = {}
    for k, p in truth.items():
        if not p.get('wrong_match'): p = first.get((p.get('name') or '').strip().lower(), p)
        if p.get('wrong_match'): continue
        e = {'what': p.get('what', ''), 'money': p.get('money', ''), 'arts': p.get('arts', ''), 'site': p.get('site', ''), 'src': p.get('sources', [])}
        out[k] = {f: v for f, v in e.items() if v}
    for k, s in senders.items():
        if not isinstance(s, dict): continue
        e = out.setdefault(k, {})
        if s.get('made_from') and not e.get('money'): e['money'] = s['made_from']
        facts = [{'t': f['text'], 'd': f.get('date', ''), 's': f.get('source', '')} for f in s.get('facts') or [] if f.get('text')]
        if facts: e['facts'] = facts
    json.dump(dict(sorted(out.items())), open(ASSET, 'w'), ensure_ascii=False, separators=(',', ':'))
    print(f'{len(out)} funders in {os.path.relpath(ASSET, ROOT)} ({os.path.getsize(ASSET) // 1024} KB)')


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else ''
    if cmd == 'merge':
        paths = sys.argv[2:] or sorted(glob.glob(os.path.join(UBATCH, 'fp*-result.json')), key=lambda s: int(re.search(r'fp(\d+)', s).group(1)))
        merge(paths)
    elif cmd == 'build':
        build()
    else:
        print(__doc__)
