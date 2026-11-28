"""Merge the reputation and status research (27 Nov 2026) into data/influence_found.json.

Reads data/influence_runs/2026-11-27-reputation-status/results/rs*.json and the checkers' verdicts in checks/*.json.
An entry is published only with a verdict: keep, fix (its `after` is published) or drop. Each one is linted with the
run's lint.py. The rows join the file's other rows, marked `run: reputation`, so a second run replaces only its own.
Then run tools/build_influence.py.

    python3 -I tools/merge_reputation.py
"""
import glob, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Each wave of the search has its own run folder; a row is marked with its wave's tag.
RUNS = [('reputation', '2026-11-27-reputation-status'), ('reputation-2', '2026-11-28-reputation-status-2'),
        ('reputation-3', '2026-11-28-reputation-status-3'),
        ('reputation-4', '2026-11-28-reputation-status-4'),
        ('reputation-5', '2026-11-28-reputation-status-5')]
sys.path.insert(0, os.path.join(ROOT, 'data', 'influence_runs', RUNS[0][1]))
from lint import check_entry  # noqa: E402

KEEP = ('kinds', 'summary', 'date', 'source', 'replaces', 'ended', 'protest')


def main():
    path = os.path.join(ROOT, 'data', 'influence_found.json')
    out = json.load(open(path))
    tags = {t for t, _ in RUNS}
    for k in list(out):
        if not k.startswith('_'):
            out[k] = [r for r in out[k] if r.get('run') not in tags]
    bad, n, unchecked = 0, 0, []
    for tag, folder in RUNS:
        RUN = os.path.join(ROOT, 'data', 'influence_runs', folder)
        checked = {}
        for p in sorted(glob.glob(os.path.join(RUN, 'checks', '*.json'))):
            for v in json.load(open(p)):
                checked[(v['file'], v['funder'], v['i'])] = v
        for p in sorted(glob.glob(os.path.join(RUN, 'results', 'rs*.json'))):
            name = os.path.basename(p)[:-5]
            batch = {r['funder']: r for r in json.load(open(os.path.join(RUN, 'batches', name + '.json')))}
            for r in json.load(open(p)):
                b = batch[r['funder']]
                spaces = {m['space']: m for m in b['museums']}
                cids = {o['cid'] for o in b['on_record']}
                by_space = {}
                for i, e in enumerate(r.get('entries') or []):
                    v = checked.get((name, r['funder'], i))
                    if not v:
                        unchecked.append(f"{tag} {name} {r['funder']} #{i}")
                        continue
                    if v['verdict'] == 'drop':
                        continue
                    e = v['after'] if v['verdict'] == 'fix' else e
                    probs = check_entry(e)
                    if e.get('space') not in spaces:
                        probs.append(f"space {e.get('space')!r} is not one of the funder's museums")
                    if e.get('replaces') and e['replaces'] not in cids:
                        probs.append(f"replaces {e['replaces']!r} is not a line of this funder")
                    for x in probs:
                        print(f"{tag} {name}: {r['funder']} #{i}: {x}")
                    bad += len(probs)
                    if not probs:
                        by_space.setdefault(e['space'], []).append({k: e[k] for k in KEEP if e.get(k) not in (None, '', False)} | {'kinds': e['kinds']})
                for sp, entries in by_space.items():
                    m = spaces[sp]
                    out.setdefault(r['funder'], []).append({'space': sp, 'space_name': m['space_name'], 'city': m['city'], 'run': tag, 'entries': entries})
                    n += len(entries)
    out = {k: v for k, v in out.items() if k.startswith('_') or v}
    if unchecked:
        print(f'{len(unchecked)} entries no checker saw, left out: {unchecked[:5]}')
    if bad:
        sys.exit(f'{bad} problems; nothing written')
    json.dump(out, open(path, 'w'), ensure_ascii=False, indent=1)
    print(f'{n} reputation and status entries merged into data/influence_found.json')


if __name__ == '__main__':
    main()
