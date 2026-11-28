"""Merge the "What came with the money" research (27 Nov 2026) into data/influence_found.json.

Reads data/influence_runs/2026-11-27-came-with/results/cw*.json (after the checkers' fixes are applied to them), lints
every entry with the run's lint.py, and writes the entries keyed by funder, with the space's name from the batch. Rows
with no entries are kept out: a funder with nothing found keeps its "Money only" row and gets no "What came with the
money" section. Then run tools/build_influence.py.

    python3 -I tools/merge_came_with.py
"""
import glob, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUN = os.path.join(ROOT, 'data', 'influence_runs', '2026-11-27-came-with')
sys.path.insert(0, RUN)
from lint import check_entry  # noqa: E402

KEEP = ('kinds', 'summary', 'date', 'source', 'replaces', 'ended', 'protest')


def verdicts():
    """The checkers' verdicts (checks/*.json), by (file, funder, space, index)."""
    out = {}
    for p in sorted(glob.glob(os.path.join(RUN, 'checks', '*.json'))):
        for v in json.load(open(p)):
            out[(v['file'], v['funder'], v['space'], v['i'])] = v
    return out


def main():
    out, bad, n = {'_about': __doc__.strip().splitlines()[0]}, 0, 0
    checked = verdicts()
    unchecked = []
    for p in sorted(glob.glob(os.path.join(RUN, 'results', 'cw*.json'))):
        name = os.path.basename(p)[:-5]
        batch = {(r['funder'], r['space']): r for r in json.load(open(os.path.join(RUN, 'batches', os.path.basename(p))))}
        rows = json.load(open(p))
        # A checker's verdict decides each entry: keep, fix (its `after` is published) or drop. An entry no checker saw
        # is not published.
        for r in rows:
            done = []
            for i, e in enumerate(r.get('entries') or []):
                v = checked.get((name, r['funder'], r['space'], i))
                if not v:
                    unchecked.append(f"{name} {r['funder']} / {r['space']} #{i}")
                elif v['verdict'] != 'drop':
                    done.append(v['after'] if v['verdict'] == 'fix' else e)
            r['entries'] = done
        for r in rows:
            b = batch.get((r['funder'], r['space']))
            if not b:
                print(f"{p}: {r['funder']} / {r['space']} is not in its batch"); bad += 1
                continue
            entries = []
            for e in r.get('entries') or []:
                if e.get('drop'):
                    continue
                probs = check_entry(e)
                for x in probs:
                    print(f"{p}: {r['funder']} / {r['space']}: {x}")
                bad += len(probs)
                entries.append({k: e[k] for k in KEEP if e.get(k) not in (None, '')} | {'kinds': e['kinds']})
            if entries:
                out.setdefault(r['funder'], []).append({'space': r['space'], 'space_name': b['space_name'], 'city': b['city'], 'entries': entries})
                n += len(entries)
    if unchecked:
        print(f'{len(unchecked)} entries no checker saw, left out: {unchecked[:5]}')
    if bad:
        sys.exit(f'{bad} problems; nothing written')
    # Rows another run merged into the file (tools/merge_reputation.py marks its own with `run`) are kept.
    path = os.path.join(ROOT, 'data', 'influence_found.json')
    if os.path.exists(path):
        for k, rows in json.load(open(path)).items():
            if not k.startswith('_'):
                out.setdefault(k, []).extend(r for r in rows if r.get('run'))
    # Plain rewordings of entries that quoted a critic's slogan (data/influence_runs/plain_summaries.json) are applied last.
    ppath = os.path.join(ROOT, 'data', 'influence_runs', 'plain_summaries.json')
    plain = json.load(open(ppath))['plain'] if os.path.exists(ppath) else {}
    for k, rows in out.items():
        if not k.startswith('_'):
            for r in rows:
                for e in r['entries']:
                    e['summary'] = plain.get(e['summary'], e['summary'])
    json.dump(out, open(path, 'w'), ensure_ascii=False, indent=1)
    print(f"{n} entries for {len(out) - 1} funders in data/influence_found.json")


if __name__ == '__main__':
    main()
