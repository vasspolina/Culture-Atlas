#!/usr/bin/env python3
"""Write the closing years in data/closures.json into institutions.json, then run tools/embed_data.py.

A closed space gets `closed_note` (one sentence) and, when a source names the year, `year_closed`. A closure comes
either from the record's own text (the entry names the `field`) or from a page outside it (the entry gives `source`, the
page's address, and `basis`, "press" or "own site"); the second kind also writes `closed_source`. No year is ever guessed
here: an entry with no `source` whose year the record's own text does not name is refused.

Two other kinds of date are kept apart from a closing year and never drawn as one:
  last_seen     the year of the latest dated activity a search found, where no page says the space closed
                (`year_last_seen`, `last_seen_note`, `last_seen_source`);
  entity_ended  the year a register says the legal body ended, which is not the day the doors shut
                (`year_entity_ended`, `entity_ended_note`, `entity_ended_source`).
A record that is not in data/closures.json loses all of these fields, so the file is the one place they are entered.

  python3 tools/attach_closures.py          write and embed
  python3 tools/attach_closures.py --check  report only
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / 'data' / 'closures.json'
DATA = ROOT / 'institutions.json'


def own_text(r):
    parts = [json.dumps(r.get(k), ensure_ascii=False) for k in r if k not in ('year_closed', 'closed_note', 'id')]
    return ' '.join(parts)


def main():
    check = '--check' in sys.argv
    src = json.load(open(SRC, encoding='utf-8'))
    closures, last_seen, ended = src['closures'], src.get('last_seen', []), src.get('entity_ended', [])
    records = json.load(open(DATA, encoding='utf-8'))
    by_id = {r['id']: r for r in records}
    problems, seen = [], set()
    for c in closures:
        r = by_id.get(c['id'])
        if not r:
            problems.append(f"{c['id']}: no such record")
            continue
        if c['id'] in seen:
            problems.append(f"{c['id']}: entered twice")
        seen.add(c['id'])
        y = c.get('year_closed')
        if y is not None and not (isinstance(y, int) and 1500 <= y <= 2100):
            problems.append(f"{c['id']}: year_closed {y!r} is not a year")
        elif y is not None and not str(c.get('source', '')).startswith('http') and str(y) not in own_text(r):
            problems.append(f"{c['id']}: the record's own text does not name {y}")
        elif y is not None and isinstance(r.get('year_founded'), int) and y < r['year_founded']:
            problems.append(f"{c['id']}: closed {y} before it was founded ({r['year_founded']})")
        if not (c.get('closed_note') or '').strip():
            problems.append(f"{c['id']}: no closed_note")
    closed_ids = {c['id'] for c in closures}
    for kind, rows in (('last_seen', last_seen), ('entity_ended', ended)):
        for c in rows:
            if c['id'] not in by_id:
                problems.append(f"{c['id']}: no such record ({kind})")
            elif not (isinstance(c.get('year'), int) and str(c.get('source', '')).startswith('http') and (c.get('note') or '').strip()):
                problems.append(f"{c['id']}: {kind} needs a year, a note and a source address")
            elif kind == 'last_seen' and c['id'] in closed_ids:
                problems.append(f"{c['id']}: last seen and closed at once")
    if problems:
        print('\n'.join(problems))
        sys.exit(1)
    FIELDS = ('year_closed', 'closed_note', 'closed_source', 'year_last_seen', 'last_seen_note', 'last_seen_source',
              'year_entity_ended', 'entity_ended_note', 'entity_ended_source')
    for r in records:
        for k in FIELDS:
            r.pop(k, None)
    for c in last_seen:
        by_id[c['id']].update(year_last_seen=c['year'], last_seen_note=c['note'].strip(), last_seen_source=c['source'])
    for c in ended:
        by_id[c['id']].update(year_entity_ended=c['year'], entity_ended_note=c['note'].strip(), entity_ended_source=c['source'])
    for c in closures:
        r = by_id[c['id']]
        if c.get('year_closed') is not None:
            r['year_closed'] = c['year_closed']
        r['closed_note'] = c['closed_note'].strip()
        if str(c.get('source', '')).startswith('http'):
            r['closed_source'] = c['source']
    dated = [c for c in closures if c.get('year_closed') is not None]
    window = [c for c in dated if 2006 <= c['year_closed'] <= 2026]
    opened = sum(1 for r in records if isinstance(r.get('year_founded'), int))
    none = sum(1 for r in records if not isinstance(r.get('year_founded'), int) and 'year_closed' not in r)
    print(f"{len(records)} records: {opened} with an opening year, {len(dated)} with a closing year "
          f"({len(window)} of them 2006 to 2026), {len(closures) - len(dated)} closed with no year, {none} with no year at all; "
          f"{sum(1 for c in closures if c.get('source'))} closures from outside the record, {len(last_seen)} last seen, {len(ended)} legal bodies ended")
    if check:
        return
    with open(DATA, 'w', encoding='utf-8') as fh:
        json.dump(records, fh, indent=2)
    subprocess.run([sys.executable, str(ROOT / 'tools' / 'embed_data.py')], check=True)


if __name__ == '__main__':
    main()
