"""Re-key data/influence_review.json after the records' wording has changed.

A verdict in the review is keyed by a candidate's cid, a hash of the record id, the funder key and the sentence
(tools/build_influence.py). When a sentence is reworded its hash changes and the verdict no longer finds it. This tool
moves each such verdict to the cid of the sentence its old one became. Run it BEFORE build_influence.py, while
data/influence_candidates.json still holds the old sentences:

    python3 -I tools/rekey_influence_review.py            # report only, nothing is written
    python3 -I tools/rekey_influence_review.py --write    # re-key the review and park what found no sentence
    python3 -I tools/build_influence.py                   # then rebuild the candidates and assets/influence.json
    python3 -I tools/build_art_periods.py                 # assets/art-periods.json keys its ties by cid too

A verdict moves only when the match is confident and one to one. The old and the new sentence must be in the same record
and the same field and name the same funder, each must be the other's closest sentence (difflib), and then either

  log   the rewrite logs (data/slop_runs/*/changes*.json, each entry a field's text before and after) show the field
        that held the old sentence now holds the new one, and the two are at least 60% alike (a sentence cut into
        two that both name the funder is left for the editor); or
  near  the two are at least 85% alike, no other sentence comes within 10 points, and they give the same numbers.

Every other verdict is parked, not dropped: data/influence_review_unmatched.json keeps it with the old sentence, where it
was, and the closest current sentence, for the editor to rule on. build_influence.py still shows a parked kept entry in
assets/influence.json, with the sentence as it was reviewed, until the editor moves or removes it. To settle one, set
"move_to" on it to the cid of a current candidate (or "remove": true) and run this tool with --write again.
Kinds, summaries and every other word of a verdict are carried as they are, and no record is written. Each move is
logged with both sentences in data/slop_runs/<today>/influence-rekey.json.
"""
import datetime, difflib, glob, json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_influence as B  # noqa: E402

ROOT = B.ROOT
REVIEW = os.path.join(ROOT, 'data', 'influence_review.json')
PARKED = os.path.join(ROOT, 'data', 'influence_review_unmatched.json')
PARKED_ABOUT = ('Verdicts of data/influence_review.json whose sentence is no longer in the records and that '
                'tools/rekey_influence_review.py could not pair with a current sentence with confidence. Each keeps its '
                'verdict, the sentence as reviewed ("was") and the closest current sentence for the same record and funder '
                '("closest", with how alike the two are). A kept one is still shown in assets/influence.json with its old '
                'sentence. To settle one: set "move_to" to the cid of a current candidate, or "remove": true, then run '
                'python3 -I tools/rekey_influence_review.py --write and python3 -I tools/build_influence.py.')
NUM = re.compile(r'\d+(?:[.,]\d+)*')


def ratio(a, b):
    return difflib.SequenceMatcher(None, a, b, autojunk=False).ratio()


def log_pairs(recs):
    """record id -> [(before, after)] from every rewrite log. The Details logs name the space, not its id."""
    by_name = {}
    for r in recs:
        by_name.setdefault(r['name'], []).append(r['id'])
    out = {}
    for path in sorted(glob.glob(os.path.join(ROOT, 'data', 'slop_runs', '*', 'changes*.json'))):
        try:
            rows = json.load(open(path))
        except ValueError:
            continue
        for e in rows if isinstance(rows, list) else []:
            if not isinstance(e, dict) or not isinstance(e.get('before'), str) or not isinstance(e.get('after'), str):
                continue
            ids = [e['id']] if e.get('id') else by_name.get(e.get('space'), [])
            for i in ids:
                out.setdefault(i, []).append((e['before'], e['after']))
    return out


def logged_after(old_text, pairs):
    """The sentences the logs say the field holding old_text was rewritten to, followed through later rewrites."""
    found, texts = set(), [old_text]
    for _ in range(4):
        nxt = []
        for t in texts:
            for before, after in pairs:
                if t in before and after not in found:
                    found.add(after)
                    nxt += [s.strip() for s in B.SENT.split(after)]
        if not nxt:
            break
        texts = nxt
    return {s.strip() for a in found for s in B.SENT.split(a)}


def match(old, new, review, logs):
    """(moves, unmatched): moves is {old cid: (new candidate, how, ratio)}, unmatched is {old cid: (closest or None, ratio)}."""
    live = {c['cid'] for c in new}
    missing = [k for k in review if not k.startswith('_') and k not in live]
    free = {}
    for c in new:
        if c['cid'] not in review:
            free.setdefault((c['space'], c['funder']), []).append(c)
    olds = {}
    for k in missing:
        o = old.get(k)
        if o:
            olds.setdefault((o['space'], o['funder']), []).append(o)
    moves, unmatched = {}, {k: (None, 0.0) for k in missing}
    for key, os_ in olds.items():
        ns = free.get(key, [])
        if not ns:
            continue
        score = {(o['cid'], n['cid']): ratio(o['text'], n['text']) for o in os_ for n in ns}
        for o in os_:
            ranked = sorted(ns, key=lambda n: -score[(o['cid'], n['cid'])])
            n, r = ranked[0], score[(o['cid'], ranked[0]['cid'])]
            second = score[(o['cid'], ranked[1]['cid'])] if len(ranked) > 1 else 0.0
            unmatched[o['cid']] = (n, r)
            # one to one: the new sentence's closest old sentence must be this one, and no other old sentence may tie
            back = sorted((score[(x['cid'], n['cid'])] for x in os_), reverse=True)
            if back[0] > r or (len(back) > 1 and back[1] >= r):
                continue
            if n['field'] != o['field']:
                continue
            how = None
            after = logged_after(o['text'], logs.get(o['space'], []))
            # a sentence cut in two, both halves naming the funder: which half the verdict reads is the editor's call
            halves = [x for x in ns if x is not n and x['text'] in after and score[(o['cid'], x['cid'])] >= 0.45]
            if r >= 0.6 and r > second and n['text'] in after and not halves:
                how = 'log'
            elif r >= 0.85 and r - second >= 0.1 and NUM.findall(o['text']) == NUM.findall(n['text']):
                how = 'near'
            if how:
                moves[o['cid']] = (n, how, r)
    # a new sentence may be claimed once
    claimed = {}
    for k, (n, how, r) in list(moves.items()):
        other = claimed.get(n['cid'])
        if other is None:
            claimed[n['cid']] = k
        else:
            moves.pop(k, None)
            moves.pop(other, None)
    for k in moves:
        unmatched.pop(k)
    return moves, unmatched


def main():
    write = '--write' in sys.argv
    recs = json.load(open(os.path.join(ROOT, 'institutions.json')))
    old = {c['cid']: c for c in json.load(open(os.path.join(ROOT, 'data', 'influence_candidates.json')))}
    new = B.find_candidates(recs)
    by_new = {c['cid']: c for c in new}
    review = json.load(open(REVIEW))
    parked = json.load(open(PARKED)) if os.path.exists(PARKED) else {}

    # The editor's rulings on parked verdicts first: move_to a current candidate, or remove.
    settled = 0
    for k, p in list(parked.items()):
        if k.startswith('_'):
            continue
        to = p.get('move_to')
        if p.get('remove'):
            del parked[k]
            settled += 1
        elif to:
            if to not in by_new:
                print(f'parked {k}: move_to {to} is not a current candidate, left parked')
            elif to in review:
                print(f'parked {k}: {to} already has a verdict, left parked')
            else:
                review[to] = p['verdict']
                del parked[k]
                settled += 1

    logs = log_pairs(recs)
    moves, unmatched = match(old, new, review, logs)
    out = {}
    for k, v in review.items():
        if k in moves:
            out[moves[k][0]['cid']] = v     # the verdict itself is not touched, and keeps its place in the file
        elif k in unmatched:
            was = old.get(k)
            closest, r = unmatched[k]
            parked[k] = {
                'verdict': v,
                'was': {f: was[f] for f in ('funder', 'funder_name', 'funder_kind', 'space', 'space_name', 'city', 'field', 'text', 'date', 'sources')} if was else None,
                'closest': ({'cid': closest['cid'], 'field': closest['field'], 'text': closest['text'], 'alike': round(r, 2)} if closest else None),
            }
        else:
            out[k] = v
    assert len(out) == len(review) - len(unmatched), 'two verdicts landed on one sentence'

    kept = lambda ks: sum(1 for k in ks if not review[k].get('drop'))
    how = [m[1] for m in moves.values()]
    print(f"{len(moves) + len(unmatched)} reviewed candidates are no longer in the records")
    print(f"  {len(moves)} re-keyed ({kept(moves)} kept entries): {how.count('log')} by the rewrite logs, {how.count('near')} by near-identical wording")
    print(f"  {len(unmatched)} with no confident match ({kept(unmatched)} kept entries), {'parked in' if write else 'to be parked in'} data/influence_review_unmatched.json")
    if settled:
        print(f"  {settled} parked verdicts settled by the editor")
    if not write:
        print('nothing written; run with --write')
        return
    json.dump(out, open(REVIEW, 'w'), ensure_ascii=False, indent=1)
    n_parked = sum(1 for k in parked if not k.startswith('_'))
    if n_parked:
        parked = {'_about': PARKED_ABOUT, **{k: v for k, v in parked.items() if not k.startswith('_')}}
        json.dump(parked, open(PARKED, 'w'), ensure_ascii=False, indent=1)
    elif os.path.exists(PARKED):
        os.remove(PARKED)
    if not moves:
        return
    # every move, old cid to new with both sentences, beside the rewrite logs of the day it answers
    day = os.path.join(ROOT, 'data', 'slop_runs', datetime.date.today().isoformat())
    os.makedirs(day, exist_ok=True)
    with open(os.path.join(day, 'influence-rekey.json'), 'w') as f:
        json.dump([{'from': k, 'to': n['cid'], 'how': h, 'alike': round(r, 2), 'space': n['space'], 'funder': n['funder'], 'field': n['field'],
                    'before': old[k]['text'], 'after': n['text']} for k, (n, h, r) in moves.items()], f, ensure_ascii=False, indent=1)


if __name__ == '__main__':
    main()
