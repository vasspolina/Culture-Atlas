#!/usr/bin/env python3
"""Write the closing years in data/closures.json into institutions.json, then run tools/embed_data.py.

A closed space gets `closed_note` (one sentence, from the record's own text) and, when the record names the year,
`year_closed`. A record that is not in data/closures.json loses both fields, so the file is the one place a closure is
entered. No year is ever guessed here: an entry whose year the record's own text does not name is refused.

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
    closures = json.load(open(SRC, encoding='utf-8'))['closures']
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
        elif y is not None and str(y) not in own_text(r):
            problems.append(f"{c['id']}: the record's own text does not name {y}")
        elif y is not None and isinstance(r.get('year_founded'), int) and y < r['year_founded']:
            problems.append(f"{c['id']}: closed {y} before it was founded ({r['year_founded']})")
        if not (c.get('closed_note') or '').strip():
            problems.append(f"{c['id']}: no closed_note")
    if problems:
        print('\n'.join(problems))
        sys.exit(1)
    for r in records:
        r.pop('year_closed', None)
        r.pop('closed_note', None)
    for c in closures:
        r = by_id[c['id']]
        if c.get('year_closed') is not None:
            r['year_closed'] = c['year_closed']
        r['closed_note'] = c['closed_note'].strip()
    dated = [c for c in closures if c.get('year_closed') is not None]
    window = [c for c in dated if 2006 <= c['year_closed'] <= 2026]
    opened = sum(1 for r in records if isinstance(r.get('year_founded'), int))
    none = sum(1 for r in records if not isinstance(r.get('year_founded'), int) and 'year_closed' not in r)
    print(f"{len(records)} records: {opened} with an opening year, {len(dated)} with a closing year "
          f"({len(window)} of them 2006 to 2026), {len(closures) - len(dated)} closed with no year, {none} with no year at all")
    if check:
        return
    with open(DATA, 'w', encoding='utf-8') as fh:
        json.dump(records, fh, indent=2)
    subprocess.run([sys.executable, str(ROOT / 'tools' / 'embed_data.py')], check=True)


if __name__ == '__main__':
    main()
