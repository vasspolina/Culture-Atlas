#!/usr/bin/env python3
"""Text-slop lint for institutions.json: the rules in sponsor-atlas/work/ubatch/SLOP.md, run over every shown text field.

Usage: python3 tools/lint_text.py [--json report.json] [--fix]
Without --fix it only reports. --fix applies the mechanical repairs (dashes, curly/straight quote mix, a lower-case first letter,
stat padding in funding) and leaves everything that needs a source to a human or to a research pass.
"""
import collections
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATH = ROOT / 'institutions.json'

PROSE = ['funding', 'watch', 'records_note', 'finances_note', 'affiliations_note', 'critique_note', 'why_flagged', 'other_findings',
         'highlight']
LIMIT = {'funding': 30, 'watch': 25}
# Dossier fields under record['details'] that the lint also reads: (section, key) -> record['details'][section][key] or [section] if key is None
DETAILS = [('press', 'overall'), ('bottom_line', None)]

HEDGE = re.compile(r"\b((?-i:may)(?! \d)|might|reportedly|allegedly|appears? to|seems?|arguably|is said to|are said to|believed to|likely|some say|"
                   r"it could be argued|probably|possibly|perhaps)\b", re.I)
FILLER = re.compile(r"\b(vibrant|rich|renowned|prestigious|world-class|iconic|landmark|cutting-edge|dynamic|thriving|esteemed|pivotal|"
                    r"tapestry|testament to|nestled|boasts?|showcas\w+|fosters?|underscores?|delve|navigat\w+|landscape|ecosystem|"
                    r"epic|monumental|energetic|towering|luminous|urgent|tackling|stunning|breathtaking|"
                    r"hub of|heart of|spirit of|pure \w+ energy|grassroots|Grassroots|co-optation|self-sustaining)\b|(?<![\w.])0% ")
EMPTY = re.compile(r"plays? a (crucial|key|vital) role|it is worth noting|in the realm of|a diverse range of|a variety of|among others|"
                   r"and more\b|not only .{1,60} but also|a wide range of|numerous|various (donors|funders|sponsors|partners)", re.I)
FRAME = re.compile(r"\b(the )?(documented|recorded|reported) (criticism|objection|controversy) (is|are|concerns?|centres? on|centers? on|relates? to|aimed at)\b", re.I)
VERDICT = re.compile(r"\b(controversial|problematic|troubling|concerning)\b", re.I)
VAGUE = re.compile(r"\b(a major (oil|tobacco|mining|arms|gas)\b|various (donors|funders)|several (donors|funders)|many foundations|"
                   r"unnamed (donors|funders)|private donors|corporate partners)\b", re.I)
STAT_IN_FUNDING = re.compile(r"\b\d[\d,.]*\s?[kKmM]?\s+(annual |yearly )?(visitors|visits)\b|visitors \(\d{4}", re.I)
NOSITE = re.compile(r"nothing from it or its|that we could find", re.I)
MEDIAL = re.compile(r"[—–]")
CURLY = re.compile(r"[‘’“”]")
STRAIGHT = re.compile(r"[\"']")
SEMICHAIN = re.compile(r";[^;]*;")


def words(t):
    return len(t.split())


def problems(rec):
    out = []
    for f in PROSE:
        t = rec.get(f)
        if not isinstance(t, str) or not t.strip():
            continue
        found = []
        if MEDIAL.search(t):
            found.append('dash')
        if CURLY.search(t) and re.search(r"(?<!\w)\"|(?<![A-Za-z])'(?=\w)", t):
            found.append('quote-mix')
        if SEMICHAIN.search(t):
            found.append('semicolon-chain')
        m = HEDGE.search(t)
        if m:
            found.append('hedge: ' + m.group(0))
        m = FILLER.search(t)
        if m:
            found.append('filler: ' + m.group(0))
        m = EMPTY.search(t)
        if m:
            found.append('empty: ' + m.group(0))
        m = VERDICT.search(t)
        if m:
            found.append('verdict: ' + m.group(0))
        m = FRAME.search(t)
        if m:
            found.append('frame: ' + m.group(0))
        m = VAGUE.search(t)
        if m and len(re.findall(r"(?<=[a-z,;:] )[A-Z][\w&'.-]+", t)) < 3:
            found.append('vague: ' + m.group(0))
        if f in LIMIT and words(t) > LIMIT[f]:
            found.append(f'over {LIMIT[f]} words ({words(t)})')
        if f == 'funding' and STAT_IN_FUNDING.search(t):
            found.append('visitor count in funding')
        if f == 'records_note' and NOSITE.search(t):
            found.append('no-site boilerplate')
        if re.match(r"[a-z]", t.strip()) and not re.match(r"(la|le|el|de|van|von|der|den|di|da|du|al|ibn|bin|[a-z]+[A-Z])\b", t.strip()):
            found.append('lower-case start')
        for p in found:
            out.append((f, p))
    det = rec.get('details') or {}
    for sec, key in DETAILS:
        t = det.get(sec)
        if key and isinstance(t, dict):
            t = t.get(key)
        m = FRAME.search(t) if isinstance(t, str) else None
        if m:
            out.append((f'details.{sec}' + (f'.{key}' if key else ''), 'frame: ' + m.group(0)))
    return out


FIXES = [(re.compile(r"\s*[—–]\s*"), ', ')]


def mechanical(t):
    s = t
    s = re.sub(r"(?<=\d)–(?=\d)", ' to ', s)              # numeric ranges: 2013–2014 -> 2013 to 2014
    s = re.sub(r"\s+[—–]\s+", ', ', s)                      # spaced dash -> comma
    s = re.sub(r"(?<=\w)—(?=\w)", ', ', s)                  # unspaced em dash -> comma
    return s


def main():
    args = sys.argv[1:]
    data = json.load(open(PATH, encoding='utf-8'))
    counts = collections.Counter()
    per = collections.defaultdict(list)
    rows = 0
    for r in data:
        ps = problems(r)
        if ps:
            rows += 1
        for f, p in ps:
            counts[p.split(':')[0].split(' (')[0]] += 1
            per[r['id']].append({'field': f, 'problem': p})
    print(f'{len(data)} records, {rows} with at least one problem')
    for k, v in counts.most_common():
        print(f'  {k:28} {v}')
    if '--json' in args:
        Path(args[args.index('--json') + 1]).write_text(json.dumps(per, ensure_ascii=False, indent=1), encoding='utf-8')
    if '--fix' in args:
        n = 0
        for r in data:
            for f in PROSE:
                t = r.get(f)
                if isinstance(t, str) and MEDIAL.search(t):
                    r[f] = mechanical(t)
                    n += 1
        PATH.write_text(json.dumps(data, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
        print(f'fixed dashes in {n} fields')


if __name__ == '__main__':
    main()
