#!/usr/bin/env python3
"""What kind of art each funder's money goes to: assets/art-periods.json.

Reader feedback, passed on by the user on 19 Nov 2026: "switch the perspective a little from the receivers to the senders,
and see what kind of influence they're buying. I.e. are they funding modern art, contemporary, or old masters?"

Nothing here is looked up or guessed. Each space is read from its own words in institutions.json:

  1. its name and the first sentence of its description (details.overview[0]), which say what the space is
     ("Contemporary art museum at ...", "Museum of early 20th-century German and Austrian art ...");
  2. failing that, any later sentence of the description that is about its collection (it says collection, holds, works
     by, devoted to, spanning and so on) and names a period ("The collection holds about 50,000 objects spanning more than
     5,000 years, including European Baroque art, French and American Impressionism ...").

The sentence that decided it is kept as `q`, and tests/art-periods.test.mjs fails if it is no longer in the record.
A sentence that gives a range ("from the fifteenth to the nineteenth century", "1500 to the present day") counts every
period in the range. A space that reaches four or more periods is an all-periods museum, not counted in each.

A tie whose own summary, in assets/influence.json, names the art it paid for ("While paying for Origins of
Impressionism ...", "Major partner of the contemporary galleries") is read the same way and kept under `ties`, so a
funder's record can say what the gift itself paid for where the gift says so.

Spaces that are not about visual art are given their field from the same words (performing arts, history, science,
books and film, design, several art forms). A space whose words name neither a period nor a field is left unread: the
atlas does not say, and the page says so rather than guessing.

    python3 -I tools/build_art_periods.py
    node --test tests/art-periods.test.mjs
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

PERIODS = [
    ('ancient', 'Ancient art and archaeology', 'before about 500'),
    ('old', 'Old masters', 'about 1200 to 1800'),
    ('c19', 'The 1800s', '1800 to 1900'),
    ('modern', 'Modern art', 'about 1900 to 1970'),
    ('contemporary', 'Contemporary art', 'about 1970 to now'),
]
ORDER = [k for k, _, _ in PERIODS]
FIELDS = [
    ('all', 'Every period', 'a museum whose collection runs across four or more of the periods'),
    ('art', 'Period not stated', 'an art museum or gallery whose description names no period'),
    ('mixed', 'Several art forms', 'an arts centre with stages, screens and galleries'),
    ('performing', 'Music, theatre and dance', ''),
    ('design', 'Design, craft and architecture', ''),
    ('photo', 'Photography and film', ''),
    ('books', 'Books and writing', ''),
    ('history', 'History and heritage', ''),
    ('science', 'Science and nature', ''),
]

# ---- Period markers. Each finds a period in a sentence; its index orders the periods for a range. ----
CENT = {'twelfth': 12, 'thirteenth': 13, 'fourteenth': 14, 'fifteenth': 15, 'sixteenth': 16, 'seventeenth': 17,
        'eighteenth': 18, 'nineteenth': 19, 'twentieth': 20, 'twenty-first': 21}


def century_bucket(c):
    if c <= 5:
        return 0
    if c <= 18:
        return 1
    if c == 19:
        return 2
    if c == 20:
        return 3
    return 4


def year_bucket(y):
    if y < 500:
        return 0
    if y < 1800:
        return 1
    if y < 1900:
        return 2
    if y < 1970:
        return 3
    return 4


WORD_MARKERS = [
    (0, r'\bantiquit(y|ies)\b|\bancient\b|\barchaeolog\w*|\bprehistor\w*|\bmillennium bc\b|\b(spanning|covering|over|more than|some) (more than )?\d{1,3},\d{3} years\b|\bpre-columbian\b|\bneolithic\b|\bbronze age\b|\biron age\b'
        r'|\b(greek|roman|egyptian|etruscan)\s+(art|antiquities|sculpture|vases?|artefacts|objects)\b|\bgreek, roman\b'),
    (1, r'(?<!the )\bold masters?\b|\balte meister\b|\bmedieval\b|\bmiddle ages\b|\brenaissance\b|\bbaroque\b|\bgothic (art|painting|sculpture)\b'
        r'|\bdutch golden age\b|\bbyzantine\b|\bming\b|\bmughal\b'),
    (2, r'\bimpressionis\w*|\bpre-raphaelite\w*|\b1800s\b|\bpost-impressionis\w*'),
    (3, r'\bmodern art\b|\bmodern and contemporary\b|\bmodernis[mt]\w*|\barte moderno\b|\bart moderne\b|\bmoderne kunst\b'
        r'|\bcubis[mt]\b|\bexpressionis[mt]\b|\bbauhaus\b|\bsurrealis[mt]\b|\bavant-garde\b|\barmory show\b|\bmuseum of modern\b|\bmodern museum\b'),
    (4, r'\bcontemporar\w*|\bzeitgen\w*|\bcontempor[aá]ne\w*|\bcontemporain\w*|\bgegenwart\b|\bliving artists\b|\bemerging artists\b'
        r'|\bnew media\b|\bmedia[- ]art\b|\bdigital art\b|\bpresent day\b|\btwenty-first century\b|\b21st[- ]century\b'),
]
CENTURY_RE = re.compile(r'\b(1[2-9]|2[01]|[5-9])(?:th|st|nd|rd)\b|\b(' + '|'.join(CENT) + r')\b', re.I)
# A century or a year only counts where the sentence is about art, and not where it dates a building.
ART_CONTEXT = re.compile(r'\b(art|arts|painting|paintings|sculpture|sculptures|works|objects|collection|drawings|prints|artists|pictures|masters)\b', re.I)
BUILDINGS = r'(building|buildings|palace|palacete|house|church|fortress|castle|villa|mansion|hall|monastery|convent|\w*klooster|\w*kirche|\w*kerk|warehouse|mill|station|tower|chapel|abbey|townhouse|estate|garden|mosque|temple|moats?|walls|main building|extension|premises|structure)'
# "16th-century palace", "a modernist main building", "in the medieval Agnietenklooster": the age of the building, not of the art.
BUILDING_AFTER = re.compile(r'^[- ]*(centur(y|ies))?[- ]*([\w-]+[- ]){0,2}' + BUILDINGS + r'\b', re.I)
RANGE_TO_NOW = re.compile(r'\bto (the )?(present|today|now)\b|\bpresent day\b|\bonwards?\b|\bto our time\b|\bcentury on\b', re.I)
RANGE = re.compile(r'\bfrom\b.*\bto\b|\bto the present\b|\bspanning\b|\bthrough\b|\bonwards?\b|\bto (the )?(\d|twent|nine|eight|seven|six|fif|four|thir)', re.I)
# A year dates a collection only in these phrasings, never as the date of a gift or an event.
YEAR_RANGE = re.compile(r'\b(?:art|works|artworks|objects|paintings?)\s+(?:made\s+)?(?:from|after)\s+(?:the\s+)?(?:\d{4}\s+\w+\s+\w+\s+)?(\d{4})s?\b|\b(\d{4})s?\s+(?:to the present|onwards?|to today)', re.I)

COLLECTION = re.compile(r'\bcollection|\bholds?\b|\bholdings\b|\bworks (by|from|of)\b|\bdevoted to\b|\bdedicated to\b|\bspeciali[sz]\w*|\bfocus\w*|\bcovering\b|\bspanning\b|\branges? from\b|\bruns from\b|\bwhat is there\b|\bshows\b|\bcovers\b|\bon site\b|\bgalleries\b', re.I)


NOT_PERIOD = re.compile(r'renaissance rom\b|\brenaissance society\b|\bmodernist (galleries|gallery|wing|block)\b|\bthe old masters? (gallery|galleries)\b', re.I)
# Another venue's name inside a sentence (the Prado "absorbed the Museo de Arte Moderno", the Scottish National Gallery of
# Modern Art among the bodies a group runs) says nothing about what this space shows. Matched with its capitals.
OTHER_VENUE = re.compile(r"\b(?:Museum|Gallery|Museo|Musée|Museu|Galleria|Galerie|Nationalgalerie)\s+(?:[A-Z][\w'’-]*\s+){0,2}(?:of|de|d'|da|di|für|der)\s+(?:Arte?\s+|l'Art\s+)?Modern\w*(?:\s+Art)?")


def markers(sentence, strict=False, own_name=''):
    """The periods a sentence names, as bucket indexes, with ranges filled. strict: words only, for a tie's summary."""
    s = NOT_PERIOD.sub(' ', sentence)
    s = OTHER_VENUE.sub(lambda m: m.group(0) if own_name and m.group(0) in own_name else ' ', s)
    low = s.lower()
    found = set()
    for b, pat in WORD_MARKERS:
        for m in re.finditer(pat, low):
            if BUILDING_AFTER.match(low[m.end():m.end() + 40]):
                continue
            found.add(b)
            break
    art = bool(ART_CONTEXT.search(s))
    if art and not strict:
        for m in CENTURY_RE.finditer(s):
            tail = s[m.end():m.end() + 40]
            if not re.match(r'^[- ]*(and|to|or|,)?[- ]*(\w+[- ]){0,2}centur', tail, re.I) and not re.match(r'^[- ]*centur', tail, re.I):
                continue  # "19th" in a date, not a century
            if BUILDING_AFTER.match(tail):
                continue
            c = int(m.group(1)) if m.group(1) else CENT[m.group(2).lower()]
            found.add(century_bucket(c))
        for m in YEAR_RANGE.finditer(s):
            y = int(m.group(1) or m.group(2))
            if 1000 <= y <= 2025:
                found.add(year_bucket(y))
    if not found:
        return []
    lo, hi = min(found), max(found)
    if RANGE_TO_NOW.search(s):
        hi = 4
    if hi > lo and (RANGE.search(s) or RANGE_TO_NOW.search(s)):
        found = set(range(lo, hi + 1))
    return sorted(found)


def sentences(text):
    return [x.strip() for x in re.split(r'(?<=[.;])\s+(?=[A-Z"“(])', text or '') if x.strip()]


# ---- Fields, for spaces whose words name no period. First match wins. ----
FIELD_RES = [
    ('mixed', r'\barts? cent(re|er)s?\b|\bcultural cent(re|er)\b|\bkulturzentrum\b|\bcentro cultural\b|\bcentre culturel\b|\bmulti-?disciplinary\b|\bperforming and visual\b|\btheatre, dance, music, visual art\b'),
    ('photo', r'\bphotograph\w*|\bcinema\w*|\bfilm\b|\bfilms\b|\bcinémathèque\b|\bcinematheque\b|\bmoving image\b'),
    ('design', r'\bdesign\b|\barchitecture\b|\bdecorative arts?\b|\bapplied arts?\b|\bcrafts?\b|\bfashion\b|\bfolk art\b|\btextiles?\b|\bceramics?\b|\bglass museum\b'),
    ('performing', r'\btheat(re|er|ro)s?\b|\bopera\b|\bballet\b|\bdance\b|\borchestra\b|\bphilharmoni\w*|\bsymphon\w*|\bconcert\w*|\bmusic\w*|\bjazz\b|\bperforming arts\b|\bschauspiel\w*|\bsinfonie\w*|\bchoir\b|\bfestival of (music|theatre)\b|\bplayhouse\b'),
    ('books', r'\blibrar(y|ies)\b|\bliterat\w*|\bpoetry\b|\bbooks?\b|\bwriters?\b|\bbook fair\b'),
    ('science', r'\bscience\w*|\bnatural history\b|\bplanetarium\b|\baquarium\b|\bzoo\b|\bbotanic\w*|\btechnolog\w*|\bspace cent(re|er)\b|\bnaturkunde\b'),
    ('history', r'\bhistor\w*|\bheritage\b|\bwar\b|\bmemorial\b|\bpalace\b|\bcastle\b|\bhouse museum\b|\bethnograph\w*|\banthropolog\w*|\barchive\w*|\bmonument\w*|\bcathedral\b|\bchurch\b|\bheimat\w*|\bfolk\w* museum\b|\bmuseum of the city\b|\bcity museum\b|\bindigenous\b|\bcultural centre of\b'),
    ('art', r'\bart\b|\barts\b|\bgallery\b|\bgalleries\b|\bgalerie\b|\bgaleria\b|\bkunst\w*|\barte\b|\bbellas artes\b|\bbeaux-arts\b|\bfine arts?\b|\bsculpture\w*|\bdrawing\b|\bpainting\w*|\bbienna?l\w*|\btriennal\w*|\bpinacoteca\b|\bkunsthalle\b|\bartists?\b|\bexhibition\w*'),
]


def read_space(x):
    name = x.get('name', '')
    ov = (x.get('details') or {}).get('overview') or []
    first = sentences(ov[0])[0] if ov and sentences(ov[0]) else ''
    head = f'{name}. {first}' if first else name
    # 1. The name and the first sentence say what the space is.
    for text, src in ((name, 'name'), (first, 'overview')):
        if not text:
            continue
        b = markers(text, own_name=name)
        if b:
            return {'p': b, 'q': [text], 's': src}
    low = head.lower()
    # The field its first words name first: "Art museum in the Villahermosa Palace" is art, "State history and culture
    # museum" is history, "National art and history museum" is art.
    hits = [(m.start(), i, key) for i, (key, pat) in enumerate(FIELD_RES) for m in [re.search(pat, low)] if m]
    field = min(hits)[2] if hits else None
    is_art = bool(re.search(dict(FIELD_RES)['art'], low))
    # 2. For an art space, or one whose first words say nothing, every later sentence about the collection that names a
    #    period; all of them, so a museum whose description gives its medieval founding gift and its contemporary
    #    holdings in two sentences counts both. A library, a theatre or a history museum stays what its first words say.
    #    The description's library and archive sentences are about books, not the collection.
    if field is None or is_art or field in ('mixed', 'design', 'photo'):
        got, qs = set(), []
        for para in ov:
            for sent in sentences(para):
                if sent == first or re.match(r'^(Archive|Library|Archives)\b', sent):
                    continue
                if COLLECTION.search(sent):
                    b = markers(sent, own_name=name)
                    if b and not set(b) <= got:
                        got |= set(b)
                        qs.append(sent)
        if got:
            return {'p': sorted(got), 'q': qs, 's': 'overview'}
    # 3. No period: the field its name and first sentence give.
    if field:
        return {'f': field, 'q': [first or name], 's': 'overview' if first else 'name'}
    return None


def main():
    insts = json.loads((ROOT / 'institutions.json').read_text())
    layer = json.loads((ROOT / 'assets/influence.json').read_text())

    spaces = {}
    for x in insts:
        r = read_space(x)
        if not r:
            continue
        if 'p' in r:
            p = r['p']
            r['p'] = [ORDER[i] for i in p]
            if len(p) >= 4:
                r['f'] = 'all'
            else:
                r['f'] = 'art'
        spaces[x['id']] = r

    # A tie's own summary, where it names the art the gift paid for.
    ties = {}
    for f in layer['funders']:
        for t in f['ties']:
            b = markers(t.get('summary', ''), strict=True)
            if b and t.get('cid'):
                ties[t['cid']] = {'p': [ORDER[i] for i in b], 'q': t['summary']}

    # Counts, by distinct space, over each ledger funder's ties: the gift's own words first, the space's otherwise.
    def bucket_of(t):
        g = ties.get(t.get('cid'))
        if g:
            return ('gift', g['p'] if len(g['p']) < 4 else ['all'])
        s = spaces.get(t['space'])
        if not s:
            return ('none', [])
        if s['f'] == 'all':
            return ('space', ['all'])
        if s.get('p'):
            return ('space', s['p'])
        return ('space', [s['f']])

    totals = {}
    by_kind = {}
    funders = {}
    for f in layer['funders']:
        if not f['ties']:
            continue
        seen = {}
        for t in f['ties']:
            how, keys = bucket_of(t)
            prev = seen.get(t['space'])
            # A gift's own words win over the space's for that space.
            if prev is None or (how == 'gift' and prev[0] != 'gift'):
                seen[t['space']] = (how, keys)
        n = {}
        for sid, (how, keys) in seen.items():
            for k in (keys or ['unread']):
                n[k] = n.get(k, 0) + 1
        funders[f['key']] = n
        for sid, (how, keys) in seen.items():
            for k in (keys or ['unread']):
                totals.setdefault(k, set()).add(sid)
                by_kind.setdefault(f['kind'], {}).setdefault(k, set()).add(sid)

    out = {
        'about': ('What kind of art each funder\'s money goes to, read from each space\'s own description in '
                  'institutions.json, or from the tie\'s own summary where it names the art. Built by '
                  'tools/build_art_periods.py; nothing is looked up or guessed. funders, totals and by_kind count the '
                  'ledger ties only (distinct spaces); the page counts every space the map joins to a funder.'),
        'periods': [{'key': k, 'label': l, 'span': s} for k, l, s in PERIODS],
        'fields': [{'key': k, 'label': l, 'note': n} for k, l, n in FIELDS],
        'spaces': spaces,
        'ties': ties,
        'funders': funders,
        'totals': {k: len(v) for k, v in totals.items()},
        'by_kind': {kind: {k: len(v) for k, v in d.items()} for kind, d in by_kind.items()},
    }
    (ROOT / 'assets/art-periods.json').write_text(json.dumps(out, ensure_ascii=False, separators=(',', ':')) + '\n')
    read_n = sum(1 for x in insts if x['id'] in spaces)
    tied = {t['space'] for f in layer['funders'] for t in f['ties']}
    tied_read = sum(1 for s in tied if s in spaces and spaces[s].get('p'))
    print(f'{read_n} of {len(insts)} spaces read; {len(ties)} ties name the art they paid for')
    print(f'of {len(tied)} spaces in the ledger, {tied_read} have a period')
    print('ledger spaces by what they show:', json.dumps(out['totals']))


if __name__ == '__main__':
    main()
