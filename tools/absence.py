#!/usr/bin/env python3
"""Drop sentences that only say something was not found.

The Details card shows what research found. "No criticism found in art media." or "No reporting found of
accessibility." says nothing about the space, so the card leaves it out. A sentence goes only when its whole
point is the absence; a sentence that also states something ("No flagged funder was found: its pages name the
City of Arles ...") stays, and `strip_details` reports it so someone can reword it by hand.

  python3 tools/absence.py            # dry run: counts, and the sentences it would keep for review
  python3 tools/absence.py --apply    # rewrite institutions.json
"""
import json
import re
import sys
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / 'institutions.json'

SENTENCE = re.compile(r'(?<=[.;])\s+(?=[A-Z"“(])')
# "No criticism found in art media." / "None of the funders was named."
LABEL = re.compile(r"^[A-Z][\w'()/& -]{0,40}:\s+(?=(?:No|None|Nothing|Neither)\b)")   # "Visiting: No reporting found of ..."
LEAD = re.compile(r'^(No|None|Nothing|Neither)\b', re.I)
ABSENT = re.compile(r'\b(found|located|published|reporting|reported|available|disclosed|named|stated|documented|'
                    r'listed|identified|given|readable|opened|exists?|seen|raised|mentioned|criticism|objection|protest|complaint|controversy)\b', re.I)
# "Amounts were not verified." / "Accessibility details were not found."
PLAIN = re.compile(r"\b(?:(?:was|were|is|are|been)\s+not|could\s+not|cannot|couldn't|wasn't|weren't|isn't|aren't)\s+"
                   r"(?:be\s+)?(?:found|located|published|verified|confirmed|listed|named|stated|disclosed|readable|"
                   r"read|given|checked|opened|available|identified|on the page|on the pages)\b[^.:;]{0,60}$", re.I)
PROCESS = re.compile(r"\b(did not load|no longer resolves|could not be (?:opened|read|checked|reached))\b", re.I)
NOT_ABSENCE = re.compile(r'\b(guilty|liable|responsible|culpable|complicit|in breach|to have|to be|to contain)\b', re.I)
SHORT = 16   # words; a longer "not found" sentence usually carries a fact as well
# After the colon or semicolon: why nothing was found. That is still only the absence.
EXCUSE = re.compile(r"\b(could not|couldn't|cannot|did not (?:load|show|open)|not (?:read|opened|readable|available|listed|named|"
                    r"shown|posted|on the)|blocked|refused|returned|unavailable|exceeded|403|404|500|names? (?:no|none)|"
                    r"gives? no|shows? no|lists? no|states? no|no (?:amounts?|names?|funders?|trustees?|figures?|reason)|"
                    r"only (?:the )?\d{4} \w+ (?:form|report) is linked|links? (?:only|an annual report)|no (?:page|reporting|source|report|"
                    r"annual report)|(?:was|were) found|none could be|carries no|(?:un|not )disclosed|is not explained|"
                    r"(?:are|is) not shown|showed none)\b", re.I)


def is_absence(s):
    t = LABEL.sub('', s.strip()).rstrip('.;')
    if NOT_ABSENCE.search(t):
        return False
    if LEAD.match(t) and ABSENT.search(t):
        m = re.search(r'[:;]', t)
        return not m or bool(EXCUSE.search(t[m.end():]))
    return len(t.split()) <= SHORT and bool(PLAIN.search(t) or PROCESS.search(t))


def strip_text(text, kept=None):
    """The text without its absence sentences; kept collects "No ..." sentences that state something too."""
    if '\n' in text:
        return '\n'.join(x for x in (strip_text(l, kept) for l in text.split('\n')) if x)
    out = []
    for s in SENTENCE.split(text.strip()):
        if is_absence(s):
            continue
        if kept is not None and LEAD.match(LABEL.sub('', s)) and ABSENT.search(s):
            kept.append(s)
        out.append(s)
    r = ' '.join(out).strip()
    return re.sub(r';$', '.', r)


def strip_details(d, kept=None):
    """Rewrite one `details` dict in place; returns how many sentences were dropped."""
    before = json.dumps(d, ensure_ascii=False)
    n = [0]

    def one(t):
        r = strip_text(t, kept)
        if r != t.strip():
            n[0] += len(SENTENCE.split(t.strip())) - len(SENTENCE.split(r)) if r else len(SENTENCE.split(t.strip()))
        return r

    for k in ('overview', 'funding', 'wider_context', 'not_related'):
        d[k] = [x for x in (one(t) for t in d.get(k, [])) if x]
    for k in ('bottom_line',):
        d[k] = one(d.get(k, '')) if d.get(k) else d.get(k, '')
    for f in d.get('red_flags', []):
        f['points'] = [x for x in (one(t) for t in f['points']) if x]
    d['red_flags'] = [f for f in d.get('red_flags', []) if f['points']]
    p = d.get('press') or {}
    if p:
        p['overall'] = one(p['overall']) if p.get('overall') else ''
        for it in p.get('items', []):
            it['points'] = [x for x in (one(t) for t in it.get('points', [])) if x]
    return n[0] if json.dumps(d, ensure_ascii=False) != before else 0


def strip_record(r, kept=None):
    """details and the plain-text funding line of one record; returns the sentences dropped."""
    n = strip_details(r['details'], kept) if 'details' in r else 0
    if isinstance(r.get('funding'), str):
        before = r['funding']
        r['funding'] = strip_text(before, kept)
        n += before.strip() != r['funding']
    return n


def main():
    apply = '--apply' in sys.argv
    recs = json.loads(DATA.read_text())
    total, touched, kept = 0, 0, []
    for r in recs:
        n = strip_record(r, kept)
        total += n
        touched += bool(n)
    print(f'{total} sentences dropped from {touched} records')
    print(f'{len(kept)} sentences start "No ..." but state something too, so they stay:')
    for s in kept:
        print('  -', s[:200])
    if apply:
        DATA.write_text(json.dumps(recs, ensure_ascii=True, indent=2))
        print('institutions.json rewritten')


if __name__ == '__main__':
    main()
