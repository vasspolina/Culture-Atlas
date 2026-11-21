#!/usr/bin/env python3
"""Retell the gossip items in the voice of Gossip mode: the `told` field of data/gossip_items.json.

In Gossip mode the page shows an item's `told` in place of its `said` (user, 21 Nov 2026: "Retell in gossip voice", after
"it just not changing content to gossip"). `said` stays the record: the chat model is given it, and the page shows it
outside Gossip mode and wherever an item has no `told` yet.

The voice: an investigative journalist who talks the way a voice assistant with a character does. Quick and dry, a little
ironic, never sweet, short sentences that land when read aloud. A retelling carries the same claims as `said`, each still
with who says it and when, in the same reported speech; talk stays talk. Figures, dates, names and quotations are kept
exactly. The irony is for institutions and money, never for a named person, and it adds no fact and no verdict. No dash.
The voice never claims a source, a document or an interview of its own. tools/attach_gossip.py (told_errors) checks each
retelling against the item it retells and refuses one that adds a figure, a quotation or a name.

  python3 tools/tell_gossip.py --todo 40          the next 40 items with no retelling, newest first, to write from
  python3 tools/tell_gossip.py --merge told.json  take {"G123": "retelling", ...}, check each, write them in
  python3 tools/tell_gossip.py --count            how many items are retold

--merge writes the retellings into data/gossip_items.json and onto the same items in institutions.json, and nothing else, so
the diff holds only them. Then run tools/embed_data.py and bump the ?v= on assets/institutions.js in index.html.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from attach_gossip import ITEMS, RECORDS, told_errors  # noqa: E402


def load_items():
    return json.load(open(ITEMS, encoding='utf-8'))


def todo(n):
    items = sorted((it for it in load_items() if not it.get('told')), key=lambda it: str(it.get('when')), reverse=True)
    for it in items[:n]:
        print(f"## {it['id']} | {it['status']} | {it['institution']} | {it['where']} | {it['when']}")
        print(f"H: {it['headline']}")
        print(f"S: {it['said']}")
        print()
    print(f'{len(items)} items have no retelling yet.')


def merge(path):
    new = json.load(open(path, encoding='utf-8'))
    items = load_items()
    by_id = {it['id']: it for it in items}
    errors = []
    for iid, told in new.items():
        if iid not in by_id:
            errors.append(f'{iid}: no such item')
            continue
        errors.extend(f'{iid}: {e}' for e in told_errors({**by_id[iid], 'told': told}))
    for e in errors:
        print('ERROR', e)
    if errors:
        print(f'{len(errors)} error(s); nothing written.')
        sys.exit(1)
    for iid, told in new.items():
        it = by_id[iid]
        # `told` sits after `said`, where a reader of the file looks for it.
        rest = {k: v for k, v in it.items() if k != 'told'}
        it.clear()
        for k, v in rest.items():
            it[k] = v
            if k == 'said':
                it['told'] = told
    # Each file is written back as it was found (the items: one-space indent; the records: as tools/clean_data.py leaves them).
    with open(ITEMS, 'w', encoding='utf-8') as f:
        f.write(json.dumps(items, ensure_ascii=False, indent=1) + '\n')
    recs = json.load(open(RECORDS, encoding='utf-8'))
    on_records = 0
    for r in recs:
        for g in ((r.get('gossip_data') or {}).get('gossip') or []):
            if g.get('id') in new:
                rest = {k: v for k, v in g.items() if k != 'told'}
                g.clear()
                for k, v in rest.items():
                    g[k] = v
                    if k == 'said':
                        g['told'] = new[g['id']]
                on_records += 1
    with open(RECORDS, 'w', encoding='utf-8') as f:
        f.write(json.dumps(recs, ensure_ascii=True, indent=2))
    print(f'wrote {len(new)} retellings ({on_records} on the records). Now: python3 tools/embed_data.py, and bump ?v= on assets/institutions.js')


def count():
    items = load_items()
    print(f"{sum(1 for it in items if it.get('told'))} of {len(items)} items are retold.")


if __name__ == '__main__':
    args = sys.argv[1:]
    if args[:1] == ['--todo']:
        todo(int(args[1]) if len(args) > 1 else 40)
    elif args[:1] == ['--merge'] and len(args) > 1:
        merge(args[1])
    elif args[:1] == ['--count']:
        count()
    else:
        print(__doc__)
