#!/usr/bin/env python3
"""The bureaucracy level (1 to 5) of a record, worked out from the facts in its `bureaucracy` block.

The research agents report facts only (data/bureaucracy_prompt.md); this module turns them into a
level so every record is judged by the same ladder. The first rule that matches wins:

  5 State-run     a government or municipal body, that is a department of a ministry or a city.
  4 Administered  a public body (government, municipal, statutory, university unit, or a public
                  foundation whose director the state or city names) bound by two or more public
                  controls.
  3 Supervised    a public foundation or statutory body, or any space whose director is named by a
                  government, city or parent body, or that is bound by two or more public controls.
  2 Light         a private nonprofit, foundation, association or religious body with its own board
                  (it answers to the register or regulator of its form), whether or not a page names it.
  1 Independent   a private company or owner-run space.

A record with no stated legal form gets no level. The facts are the fields of record['bureaucracy'].

Usage: python3 tools/grade_bureaucracy.py        (prints the spread; clean_data.py imports level())
"""
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

LABELS = {1: 'Independent', 2: 'Light oversight', 3: 'Supervised', 4: 'Administered', 5: 'State-run'}
STATE_FORMS = {'national government body', 'municipal or regional body'}
PUBLIC_FORMS = STATE_FORMS | {'statutory public body', 'university unit'}
PRIVATE_FORMS = {'private nonprofit', 'private foundation', 'association', 'private company', 'religious body'}
PUBLIC_CONTROLS = {
    'public procurement law', 'state audit office', 'freedom of information law', 'civil service rules',
    'approval of programme, loans or disposals by a ministry or council',
    'ministry or city seat on the governing board',
}
STATE_DIRECTOR = {'government or ministry', 'city or region'}
STATE_BUDGET = {'legislature or ministry', 'city or regional council'}


def level(g):
    """Return (level, basis sentence) for a governance block, or (None, '') without a legal form."""
    form = (g or {}).get('legal_form')
    if not form:
        return None, ''
    public = [c for c in (g.get('controls') or []) if c in PUBLIC_CONTROLS]
    regulator = 'charity or foundation regulator' in (g.get('controls') or [])
    state_director = g.get('director_appointed_by') in STATE_DIRECTOR
    parent_director = g.get('director_appointed_by') == 'parent institution'
    if form in STATE_FORMS:
        return 5, 'Its staff are civil servants.' if g.get('staff_status') == 'civil servants' else ''
    if (form in PUBLIC_FORMS or (form == 'public foundation' and state_director)) and len(public) >= 2:
        return 4, 'Bound by ' + ' and '.join(public[:2]) + '.'
    if form in ('public foundation', 'statutory public body') or form in PUBLIC_FORMS:
        return 3, ''
    if state_director or parent_director or len(public) >= 2:
        if state_director or parent_director:
            why = 'its director is named by ' + ('the government or city' if state_director else 'a parent body')
        else:
            why = 'it is bound by ' + ' and '.join(public[:2])
        return 3, why[0].upper() + why[1:] + '.'
    if form == 'private company':
        return 1, ''
    # A nonprofit, foundation, association or religious body answers to the register or regulator of its own form,
    # whether or not a source page names it, so it is never rated as free of oversight.
    if regulator:
        return 2, ''
    return 2, ''


def main():
    records = json.load(open(ROOT / 'institutions.json', encoding='utf-8'))
    c = Counter()
    for r in records:
        b = r.get('bureaucracy')
        c[level(b)[0] if b else 'none'] += 1
    for k in sorted(c, key=str):
        print(k, LABELS.get(k, ''), c[k])


if __name__ == '__main__':
    main()
