#!/usr/bin/env python3
"""Drop what only says something was not found.

The Details card shows what research found. "No criticism found in art media." or "No reporting found of
accessibility." says nothing about the space, so the card leaves it out. The filter works clause by clause: a
clause goes when its whole point is the absence ("No annual reports found", "Amounts were not verified", "the
page could not be read"); a clause that states something stays ("No annual reports found; accounts are on the
Charity Commission register" keeps the accounts). A sentence with nothing left disappears, and a note or field
with nothing left is removed.

Covers record.details and the plain-text funding line (a sentence that opens with "No ..." loses its absence
clauses; any other sentence goes only when all of it is absence) and the one-line notes (watch, why_flagged,
records_note), where the absence clauses of every mixed sentence go.

  python3 tools/absence.py            # dry run: counts, and sentences that lost only part of themselves
  python3 tools/absence.py --apply    # rewrite institutions.json
"""
import json
import re
import sys
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / 'institutions.json'

SENTENCE = re.compile(r'(?<=[.;])\s+(?=[A-Z0-9"“(])')
LABEL = re.compile(r"^([A-Z][\w'()/& -]{0,40}:\s+)(?=(?:No|None|Nothing|Neither)\b)")   # "Visiting: No reporting found of ..."
LEAD = re.compile(r'^(No|None|Nothing|Neither)\b', re.I)
# "No criticism found in art media." / "None of the funders was named."
ABSENT = re.compile(r'\b(found|located|published|reporting|reported|available|disclosed|named|stated|documented|'
                    r'listed|identified|given|readable|opened|exists?|seen|raised|mentioned|criticism|objection|'
                    r'protest|complaint|controversy|turned up|ties|tied|link|payment|source|page|list)\b', re.I)
# "Amounts were not verified." / "Accessibility details were not found."
PLAIN = re.compile(r"\b(?:(?:was|were|is|are|been)\s+not|could\s+not|cannot|couldn't|wasn't|weren't|isn't|aren't)\s+"
                   r"(?:be\s+)?(?:found|located|published|verified|confirmed|listed|named|stated|disclosed|readable|"
                   r"read|given|checked|opened|available|identified|on the page|on the pages)\b[^.:;]{0,60}$", re.I)
PROCESS = re.compile(r"\b(did not load|too large to open|no longer resolves|could not be (?:opened|read|checked|reached)|"
                     r"returned (?:an? )?(?:HTTP \d+|authorization error)|blocked access|refused (?:automated )?(?:access|requests?|the connection))\b", re.I)
# Why nothing was found, after the absence it explains.
EXCUSE = re.compile(r"\b(could not|couldn't|cannot|did not (?:load|show|open)|not (?:read|opened|readable|available|"
                    r"listed|named|shown|posted|on the)|blocked|refused|returned|unavailable|exceeded|403|404|500|"
                    r"names? (?:no|none)|gives? no|shows? no|lists? no|states? no|no (?:amounts?|names?|funders?|"
                    r"trustees?|figures?|reason|page|reporting|source|report|annual report)|(?:was|were) found|"
                    r"none could be|carries no|(?:un|not )disclosed|is not explained|(?:are|is) not shown|"
                    r"showed none|fails its certificate)\b", re.I)
SUBJECT_NOT_NAMED = re.compile(r"^[A-Z][\w'. -]{0,30} (?:was|were) not named\b")   # "Charleston was not named" in a campaign letter is the finding
CHECKED = re.compile(r'\b(confirmed|verified|read|shown|noted|recorded|released|posted|announced|included|mentions?|says|gives?|appears?|shows?)\b', re.I)
NOINFO = re.compile(r'\b(?:publishes|posts|gives|lists|names|states|shows|showed|has) no\b', re.I)   # "YARAT publishes no funder list"
UNCONFIRMED = re.compile(r'\b(unconfirmed|unverified|not (?:established|confirmed|verified|known|sourced))\b', re.I)
NOT_ABSENCE = re.compile(r'\b(guilty|liable|responsible|culpable|complicit|in breach|to have|to be|to contain)\b', re.I)
SHORT = 16   # words; a longer "not found" clause usually carries a fact as well
NOTES = ('watch', 'why_flagged', 'records_note')


def absent(c, after_absent):
    c = c.strip().rstrip('.;')
    if not c:
        return True
    if NOT_ABSENCE.search(c) or SUBJECT_NOT_NAMED.match(c):
        return False
    if LEAD.match(c) and (after_absent or ((ABSENT.search(c) or CHECKED.search(c)) and len(c.split()) <= 30)):
        return True
    n = len(c.split())
    if n <= SHORT and (PLAIN.search(c) or PROCESS.search(c) or NOINFO.search(c)):
        return True
    return after_absent and n <= 14 and bool(EXCUSE.search(c) or UNCONFIRMED.search(c) or NOINFO.search(c))


def clean_sentence(s, kept=None, partial=True, lead_only=False):
    """The sentence without its absence clauses ('' when nothing is left). With partial=False a sentence that
    still states something is returned whole; 'lead' trims only sentences that open with No/None/Neither."""
    if lead_only and not LEAD.match(s.strip()):
        return s
    end = s.rstrip()[-1:] if s.rstrip()[-1:] in '.;' else ''
    m = LABEL.match(s.strip())
    label, body = (m.group(1), s.strip()[m.end():]) if m else ('', s.strip())
    masked = re.sub(r'\([^()]*\)', lambda m: m.group(0).replace(';', '\x00').replace(',', '\x01'), body.rstrip('.;'))   # a ; inside brackets is not a clause break
    parts = [x.replace('\x00', ';').replace('\x01', ',') for x in re.split(r';\s+|,\s+(?:though|but|while|although|and|so)\s+', masked)]
    if LEAD.match(parts[0]) and re.search(r':\s+', parts[0]):   # "No flagged funder was found: its pages name ..."
        parts[0:1] = re.split(r':\s+', parts[0], maxsplit=1)
    out, prev = [], False
    for p in parts:
        gone = absent(p, prev)
        if not gone:
            out.append(p)
        prev = gone
    if not out:
        return ''
    if len(out) == len(parts) or not (partial is True or (partial == 'lead' and LEAD.match(body))):
        return s
    if kept is not None:
        kept.append(s)
    r = '; '.join(out)
    return label + r[:1].upper() + r[1:] + end


def strip_text(text, kept=None, partial=True, lead_only=False):
    if '\n' in text:
        return '\n'.join(x for x in (strip_text(l, kept, partial, lead_only) for l in text.split('\n')) if x)
    r = ' '.join(x for x in (clean_sentence(s, kept, partial, lead_only) for s in SENTENCE.split(text.strip())) if x).strip()
    return re.sub(r';$', '.', r)


def strip_details(d, kept=None):
    """Rewrite one `details` dict in place; returns 1 if anything changed."""
    before = json.dumps(d, ensure_ascii=False)

    def lines(items):
        return [x for x in (strip_text(t, kept, 'lead') for t in items) if x]

    for k in ('overview', 'funding', 'wider_context', 'not_related'):
        d[k] = lines(d.get(k, []))
    if d.get('bottom_line'):
        d['bottom_line'] = strip_text(d['bottom_line'], kept, False, True)   # "The weak point is ..." is the analysis, not a search result
    for f in d.get('red_flags', []):
        f['points'] = lines(f['points'])
    d['red_flags'] = [f for f in d.get('red_flags', []) if f['points']]
    p = d.get('press') or {}
    if p:
        p['overall'] = strip_text(p['overall'], kept, 'lead') if p.get('overall') else ''
        for it in p.get('items', []):
            it['points'] = lines(it.get('points', []))
    return int(json.dumps(d, ensure_ascii=False) != before)


def strip_record(r, kept=None):
    """details, the funding line and the notes of one record; returns how many fields changed."""
    n = strip_details(r['details'], kept) if 'details' in r else 0
    for f in ('funding',) + NOTES:
        if isinstance(r.get(f), str) and r[f].strip():
            before = r[f]
            r[f] = strip_text(before, kept, True if f in NOTES else 'lead')
            n += before.strip() != r[f]
            if not r[f]:
                del r[f]
    return n


def main():
    apply = '--apply' in sys.argv
    recs = json.loads(DATA.read_text())
    touched, kept = 0, []
    for r in recs:
        touched += bool(strip_record(r, kept))
    print(f'{touched} records changed; {len(kept)} sentences lost only part of themselves:')
    for s in kept:
        print('  -', s[:220])
    if apply:
        DATA.write_text(json.dumps(recs, ensure_ascii=True, indent=2))
        print('institutions.json rewritten')


if __name__ == '__main__':
    main()
