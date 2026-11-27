"""Lint a result file of the "What came with the money" run (BRIEF.md). Prints one line per problem; silent when clean.

    python3 -I lint.py results/cw1.json [more files]

tools/build_influence.py imports check_entry from here, so the merged file (data/influence_found.json) is held to the
same rules as the batches.
"""
import json, os, re, sys

KINDS = {'name', 'seat', 'programme', 'building', 'access', 'silence', 'licence', 'tax'}
HEDGE = re.compile(r"\b(may|might|reportedly|allegedly|appears? to|seems?|arguably|is said to|believed to|likely|some say|could be argued|possibly|perhaps)\b", re.I)
PROMO = re.compile(r"\b(vibrant|renowned|prestigious|world-class|iconic|landmark|cutting-edge|dynamic|thriving|esteemed|pivotal|tapestry|testament|nestled|boasts|showcases?|fosters?|underscores?|delve|navigates?|landscape|ecosystem|legacy|controversial|problematic|troubling)\b", re.I)
ABSENCE = re.compile(r"\b(no|not) (?:\w+ ){0,4}(found|published|stated|disclosed|given|available|named|on record)\b|\bcould not be\b|\bunknown\b|\bunclear\b", re.I)
DASH = re.compile(r"[–—]| - ")
DATE = re.compile(r"^(?:(?:19|20)\d\d(?:-(?:0[1-9]|1[0-2]))?)?$")


def check_entry(e):
    """Problems of one entry, as short strings."""
    out = []
    s = e.get('summary') or ''
    ks = e.get('kinds')
    if not isinstance(ks, list) or any(k not in KINDS for k in ks):
        out.append(f'kinds: {ks!r}')
    elif not ks and not (e.get('ended') or e.get('protest')):
        out.append('no kind, and neither ended nor protest')
    if not s.strip():
        out.append('empty summary')
    n = len(s.split())
    if n > 35:
        out.append(f'{n} words (35 at most)')
    for name, rx in (('hedge', HEDGE), ('promo', PROMO), ('absence', ABSENCE), ('dash', DASH)):
        m = rx.search(s)
        if m:
            out.append(f'{name}: {m.group(0)!r}')
    if s.count(';') > 1:
        out.append('semicolon chain')
    if s and s.strip()[-1] not in '.)':
        out.append('summary does not end with a full stop')
    if not re.match(r'^https?://\S+$', e.get('source') or ''):
        out.append('source is not a URL')
    if not DATE.match(str(e.get('date') or '')):
        out.append(f"date: {e.get('date')!r}")
    ev = e.get('evidence') or ''
    if not ev.strip():
        out.append('no evidence')
    elif len(ev.split()) > 15:
        out.append(f'evidence is {len(ev.split())} words (15 at most)')
    return out


def main(paths):
    here = os.path.dirname(os.path.abspath(__file__))
    bad = 0
    for p in paths:
        rows = json.load(open(p))
        batch = os.path.join(here, 'batches', os.path.basename(p))
        want = [(r['funder'], r['space']) for r in json.load(open(batch))] if os.path.exists(batch) else None
        got = [(r.get('funder'), r.get('space')) for r in rows]
        if want is not None and got != want:
            missing = [x for x in want if x not in got]
            print(f'{p}: rows differ from the batch; missing {missing[:5]}'); bad += 1
        cids = {o['cid'] for r in (json.load(open(batch)) if os.path.exists(batch) else []) for o in r['on_record']}
        for r in rows:
            if not isinstance(r.get('entries'), list) or not isinstance(r.get('looked'), list):
                print(f"{p}: {r.get('funder')} / {r.get('space')}: entries and looked must be lists"); bad += 1
                continue
            if not r['looked']:
                print(f"{p}: {r['funder']} / {r['space']}: looked is empty"); bad += 1
            seen = set()
            for e in r['entries']:
                probs = check_entry(e)
                if e.get('replaces') and cids and e['replaces'] not in cids:
                    probs.append(f"replaces: {e['replaces']!r} is not a cid of the batch")
                if e.get('summary') in seen:
                    probs.append('same summary twice')
                seen.add(e.get('summary'))
                for x in probs:
                    print(f"{p}: {r['funder']} / {r['space']}: {x}"); bad += 1
    return bad


if __name__ == '__main__':
    sys.exit(1 if main(sys.argv[1:]) else 0)
