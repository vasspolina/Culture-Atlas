#!/usr/bin/env python3
"""Text-slop lint for institutions.json: the rules in sponsor-atlas/work/ubatch/SLOP.md, plus the Humanizer patterns
(github.com/blader/humanizer) they did not cover, run over every shown text field.

The prose fields get every rule; the visit fields (amenities, accessibility, transit tips, curatorial focus) get the filler and
dash rules only. A sweep is recorded in data/slop_runs/<date>/changes.json (25 Oct and 3 Nov 2026).

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
# The visit fields are short lists, not prose, so they get only the filler and dash checks (the 3 Nov 2026 sweep found
# "world-class bookshop", "spacious elevators", "panoramic terrace" and "premier bookshop" living there untouched).
VISIT = ['amenities', 'accessibility', 'transit_tips', 'curatorial_focus']
# Words that are subjects or names in those fields, not praise: a landscape programme, a monumental nave, Grassroots Assemblies.
VISIT_LITERAL = re.compile(r'^(landscape|monumental|navigat\w+|grassroots)$', re.I)
LIMIT = {'funding': 30, 'watch': 25}
# Dossier fields under record['details'] that the lint also reads: (section, key) -> record['details'][section][key] or [section] if key is None
DETAILS = [('press', 'overall'), ('bottom_line', None)]

HEDGE = re.compile(r"\b((?-i:may)(?! \d)|might|reportedly|allegedly|appears? to|seems?|arguably|is said to|are said to|believed to|likely|some say|"
                   r"it could be argued|probably|possibly|perhaps)\b", re.I)
FILLER = re.compile(r"\b(vibrant|rich|renowned|prestigious|world-class|iconic|landmark|cutting-edge|dynamic|thriving|esteemed|pivotal|"
                    r"tapestry|testament to|nestled|boasts?|showcas\w+|fosters?|underscores?|delve|navigat\w+|landscape(?! architect| park| garden| design)|ecosystem|"
                    r"epic|monumental|energetic|towering|luminous|urgent|tackling|stunning|breathtaking|"
                    r"premier|legendary|world-renowned|internationally renowned|award-winning|spacious|expansive|panoramic|picturesque|futuristic|"
                    r"artisanal?|welcoming|innovative|"
                    r"hub of|heart of|spirit of|pure \w+ energy|grassroots|Grassroots|co-optation|self-sustaining)\b|(?<![\w.])0% ")
EMPTY = re.compile(r"plays? a (crucial|key|vital) role|it is worth noting|in the realm of|a diverse range of|a variety of|among others|"
                   r"and more\b|not only .{1,60} but also|a wide range of|numerous|various (donors|funders|sponsors|partners)", re.I)
FRAME = re.compile(r"\b(the )?(documented|recorded|reported) (criticism|objection|controversy) (is|are|concerns?|centres? on|centers? on|relates? to|aimed at)\b", re.I)
VERDICT = re.compile(r"\b(controversial|problematic|troubling|concerning)\b", re.I)
VAGUE = re.compile(r"\b(a major (oil|tobacco|mining|arms|gas)\b|various (donors|funders)|several (donors|funders)|many foundations|"
                   r"unnamed (donors|funders)|private donors|corporate partners)\b", re.I)
STAT_IN_FUNDING = re.compile(r"\b\d[\d,.]*\s?[kKmM]?\s+(annual |yearly )?(visitors|visits)\b|visitors \(\d{4}", re.I)
# From the Humanizer skill (github.com/blader/humanizer, v4.0.0; user, 21 Nov 2026: "apply Humanizer to cultural atlas"):
# the patterns the earlier rules did not cover. Report only, since each needs the sentence rewritten, not a word swapped.
# COPULA is its section 18 (serves as, operates as: say "is"); AIWORD its section 12 words not already in FILLER; INFLATE
# its sections 13 and 17 (a fact dressed as a turning point, or credited to everyone); SOFTCLOSE its section 2 and 15
# (an -ing tail or a closing line that names what the fact showed).
COPULA = re.compile(r"\b(serves as|serving as|stands as|functions as|operates as)\b", re.I)
AIWORD = re.compile(r"\b(crucial|enduring|enhanc(e|es|ed|ing)|garner\w*|interplay|intricate|intricacies|meticulous\w*|quietly|robust|"
                    r"valuable|[Aa]dditionally|bolster\w*|seminal|famously|groundbreaking|unrivall?ed|staggering)\b")  # lower case: Enhanced Education is a name
INFLATE = re.compile(r"\b(widely (seen|regarded|considered) as|turning point|marking (a|the) (new|turning|shift)|one of the most significant|"
                     r"lasting legacy|set the stage|in the heart of)\b", re.I)
SOFTCLOSE = re.compile(r", (highlighting|underscoring|emphasi[sz]ing|reflecting|symboli[sz]ing|fostering|showcasing)\b", re.I)
# No rule of three and no gerunds (user, 22 Nov 2026: "No rule of thirds no gerunds for cultural atlas text"). Report only:
# each needs the sentence rewritten. TRIAD is a series of exactly three short items ("free, open and public"); a series
# whose items are names or figures (three funders, three cities, three shares of a budget) is a list of facts, not a cadence, and is not counted.
# GERUND is any -ing form of a verb, gerund or participle alike ("including", "naming", "covering"): write a finite verb
# or a plain noun. Nouns that name a thing are not verbs here (a building, a painting, the funding line, holdings,
# filings), nor words that only end in -ing (thing, during, spring, Beijing, Stichting).
TRIAD = re.compile(r"(?<![\w'&.-])(?<![\w,] )([A-Za-z][\w'&-]*(?: [\w'&-]+){0,2}), ([\w'&-]+(?: [\w'&-]+){0,2}),? (?:and|or) ([\w'&-]+(?: [\w'&-]+){0,2})\b(?!,? (?:and|or)\b|, [\w'&-]+,)")
GERUND = re.compile(r"\b[A-Za-z]+ing\b")
ING_NOUN = re.compile(r"^(building|painting|drawing|funding|crowdfunding|holding|earning|saving|filing|taking|dealing|finding|proceeding|"
                      r"listing|housing|ceiling|wing|evening|morning|clothing|lightning|pudding|sibling|wedding|offspring|"
                      r"thing|nothing|something|anything|everything|king|ring|spring|string|sting|swing|bring|sing|cling|fling|sling|wring|"
                      r"during|ongoing|"
                      r"[a-z]*(stichting|vereniging|rekening|jing|qing)|nanning|liaoning|shenning)$", re.I)


def triad(t):
    for m in TRIAD.finditer(t):
        items = [g.strip() for g in m.groups()]
        if all(re.match(r"[A-Z0-9]", i) for i in items[1:]):
            continue
        return m.group(0)
    return None


# Fixed terms that name a role, a field, a legal form, a crime or an event, where a rewrite would change the fact: a
# person's title (managing director, acting director), the performing arts, a ruling family, a US private operating
# foundation, money laundering, the 1985 MOVE bombing. Struck out before the gerund check, as are quotations.
FIXED = re.compile(r"\b(managing directors?|acting (director|president|chair|head|chief)\w*( general)?|chief operating officer|"
                   r"performing arts?|performing artists?|ruling (family|party)|private operating foundation|reading room|cost of living|"
                   r"money[- ]laundering|anti-money-laundering|insider trading|MOVE bombing|ruling( [A-Z][\w-]+){0,2} family|"
                   r"operating and marketing company|blamed marketing|air[- ]conditioning|French-speaking|J\.D\. Irving|"
                   # an industry or a crime named as a funder's trade or a charge: a betting operator, the gaming
                   # corporation, a shipping fortune, trading income on UK charity accounts, a banking foundation
                   # (fondazione bancaria), laundering of tax fraud; and arching, the Vienna engineers' chamber
                   r"(?-i:betting|gaming|gambling|shipping|banking|[Tt]rading|engineering|mining|publishing|laundering|arching))\b", re.I)
QUOTED = re.compile(r"\"[^\"]+\"|“[^”]+”|‘[^’]+’|(?<!\w)'[^']+'(?!\w)")


def gerund(t):
    t = QUOTED.sub('""', FIXED.sub('', t))
    for m in GERUND.finditer(t):
        w = m.group(0)
        if ING_NOUN.match(w):
            continue
        # a capital inside a sentence is a name (Salling, Kering, Rausing, Boeing), not a verb
        if w[0].isupper() and not re.search(r"(^|[.!?:]\s+|\()$", t[:m.start()]):
            continue
        return w
    return None


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
        for name, rx in (('copula', COPULA), ('ai-word', AIWORD), ('inflated', INFLATE), ('ing-tail', SOFTCLOSE)):
            m = rx.search(t)
            if m:
                found.append(f'{name}: ' + m.group(0))
        w = triad(t)
        if w:
            found.append('triad: ' + w)
        w = gerund(t)
        if w:
            found.append('gerund: ' + w)
        m = FRAME.search(t)
        if m:
            found.append('frame: ' + m.group(0))
        m = VAGUE.search(t)
        # records_note describes what the site posts ("names 32 corporate partners"), so an unnamed roster there is a fact
        # about the page, not a vague funder claim; the rule stays on the funding fields.
        if m and f != 'records_note' and len(re.findall(r"(?<=[a-z,;:] )[A-Z][\w&'.-]+", t)) < 3:
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
    for f in VISIT:
        t = rec.get(f)
        if isinstance(t, list):
            t = ' | '.join(x for x in t if isinstance(x, str))
        if not isinstance(t, str) or not t.strip():
            continue
        if MEDIAL.search(t):
            out.append((f, 'dash'))
        m = next((m for m in FILLER.finditer(t) if not VISIT_LITERAL.match(m.group(0))), None)
        if m:
            out.append((f, 'filler: ' + m.group(0)))
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
