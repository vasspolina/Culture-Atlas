"""Step 1 of the sender view: what a funder gets for its money, one entry per funder, space and kind of influence.

Reads institutions.json and writes data/influence_candidates.json: every sentence in a record that names one of the pilot
funders below beside a sign of influence (a name, a seat, a sponsored programme, a cancellation, access, licence to operate,
tax), with the record field it came from, the sources attached to that field, and a date where the sentence or case gives one.
Nothing is fetched and no record is changed. A candidate is not a finding: data/influence_review.json keeps the editor's
verdict on each one (keep with its kinds and a one-line summary, or drop with the reason), and only kept entries reach
assets/influence.json, which the Influence mode layer reads. Run:

    python3 -I tools/build_influence.py            # rebuild candidates, then assets/influence.json from the review
"""
import json, os, re, hashlib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# The pilot: private and corporate senders that appear in the most records, and the flagged ones the money maps already
# name. Public arts councils are left out on purpose: the question is what private money buys, and a public grant is
# accountable by other means. key = the funder key of assets/money-maps.json, so the layer can find the funder's record.
FUNDERS = [
    ('bp', 'BP', 'corp', r'\bBP\b|British Petroleum'),
    ('shell', 'Shell', 'corp', r'\bShell\b(?! ?fish)'),
    ('totalenergies', 'TotalEnergies', 'corp', r'TotalEnergies|\bTotal\b(?= (?:SA|S\.A\.|Foundation|Fondation|sponsor|oil|gas))|Fondation Total'),
    ('chevron', 'Chevron', 'corp', r'\bChevron\b'),
    ('equinor', 'Equinor', 'corp', r'\bEquinor\b|\bStatoil\b'),
    ('eni', 'Eni', 'corp', r'\bEni\b'),
    ('sacklerfamily', 'Sackler family', 'family', r'Sackler'),
    ('right:koch', 'Koch', 'family', r'\bKoch\b'),
    ('right:griffin', 'Ken Griffin / Citadel', 'family', r'\bGriffin\b|\bCitadel\b'),
    ('blavatnikfamily', 'Blavatnik Family Foundation', 'family', r'Blavatnik'),
    ('bloomberg', 'Bloomberg Philanthropies', 'family', r'Bloomberg'),   # a foundation, drawn as one; L.P. and Connects entries say so
    ('bankofamerica', 'Bank of America', 'corp', r'Bank of America'),
    ('jpmorganchase', 'JPMorganChase', 'corp', r'JPMorgan|J\.P\. Morgan|JP Morgan'),
    ('ubs', 'UBS', 'corp', r'\bUBS\b'),
    ('rbc', 'RBC', 'corp', r'\bRBC\b|Royal Bank of Canada'),
    ('bmo', 'BMO', 'corp', r'\bBMO\b|Bank of Montreal'),
    ('bailliegifford', 'Baillie Gifford', 'corp', r'Baillie Gifford'),
    ('bmw', 'BMW', 'corp', r'\bBMW\b'),
    ('hyundaimotor', 'Hyundai Motor', 'corp', r'Hyundai'),
    ('chanel', 'Chanel', 'corp', r'\bChanel\b'),
    ('jti', 'Japan Tobacco International', 'corp', r'Japan Tobacco|\bJTI\b'),
    ('philipmorris', 'Altria (Philip Morris USA)', 'corp', r'Philip Morris|Altria'),
    ('rheinmetall', 'Rheinmetall', 'corp', r'Rheinmetall'),
    ('leonardo', 'Leonardo', 'corp', r'\bLeonardo S\.?p\.?A|Leonardo \(defen'),
    ('glencore', 'Glencore', 'corp', r'Glencore'),
    ('riotinto', 'Rio Tinto', 'corp', r'Rio Tinto'),
    ('vale', 'Vale', 'corp', r'\bVale\b(?! of)'),
    ('lauder', 'Lauder family', 'family', r'\bLauder\b'),
]

# Head offices for the funders assets/hq.json has no office for. City-level, as hq.json is: the publicly listed head office,
# or for a family the company its money came from. Influence mode draws each funder here instead of the spaces.
HQ_EXTRA = {
    'sacklerfamily': {'n': 'Purdue Pharma (Sackler family)', 'c': 'Stamford', 'co': 'United States', 'lat': 41.0534, 'lon': -73.5387},
    'vale': {'n': 'Vale', 'c': 'Rio de Janeiro', 'co': 'Brazil', 'lat': -22.9068, 'lon': -43.1729},
    'jti': {'n': 'Japan Tobacco International', 'c': 'Geneva', 'co': 'Switzerland', 'lat': 46.2044, 'lon': 6.1432},
    'eni': {'n': 'Eni', 'c': 'Rome', 'co': 'Italy', 'lat': 41.9028, 'lon': 12.4964},
    'equinor': {'n': 'Equinor', 'c': 'Stavanger', 'co': 'Norway', 'lat': 58.9700, 'lon': 5.7331},
    'riotinto': {'n': 'Rio Tinto', 'c': 'London', 'co': 'United Kingdom', 'lat': 51.5074, 'lon': -0.1278},
    'philipmorris': {'n': 'Altria', 'c': 'Richmond, Virginia', 'co': 'United States', 'lat': 37.5407, 'lon': -77.4360},
    'lauder': {'n': 'Lauder family', 'c': 'New York', 'co': 'United States', 'lat': 40.7128, 'lon': -74.0060},
}

# Kinds of influence, in the order the ledger lists them. Each is a pattern over one sentence that names the funder.
KINDS = [
    ('name',      'Name',               r"\bnam(?:e|ed|es|ing)\b|\bwing\b|\bgallery\b(?= (?:is |was )?named)|\bpavilion\b|\bprize\b|\baward\b|\bcentre\b|\bcenter\b|\bgalleries\b|\broom\b|\bhall\b|\bcourt\b|\bstaircase\b|\bgarden\b|\bschool\b|\bfellowship\b"),
    ('seat',      'Seat',               r"\btrustees?\b|\bboard\b|\bchair(?:man|woman|s|ed)?\b|\bpresident\b|\bpatron\b|\bdirector\b(?! of (?:the )?museum)|\bcouncil member\b|\bcommittee\b"),
    ('programme', 'Programme',          r"\bsponsor(?:s|ed|ing|ship)?\b|\bexhibitions?\b|\bshows?\b|\bseason\b|\bprogramme\b|\bprogram\b|\bfestival\b|\bcommission(?:s|ed)?\b|\bpartner(?:ship)?\b|\btour\b|\bresidenc"),
    ('silence',   'Silence',            r"\bcensor|\bcancel+(?:ed|ation)\b|\bwithdr[ae]w|\bpulled\b|\bremoved (?:a |the )?(?:work|artwork|piece)|\bself-censor|\bgag|\bnon-disclosure|\bconfidential(?:ity)?\b|\bwithh[eo]ld|\brefused to (?:disclose|release|name)"),
    ('access',    'Access',             r"\bgalas?\b|\bcorporate (?:member|membership|partner|event|hire|entertain)|\bprivate view|\bvenue hire|\breceptions?\b|\bdinners?\b|\bhospitality\b|\bentertain"),
    ('licence',   'Licence to operate', r"\blobb|\bpermits?\b|\blicen[cs]e to operate\b|\bsocial licen|\bgreenwash|\bartwash|\bwhitewash|\breputation|\blegitimacy\b|\bimage\b|\bdrilling\b|\bconcession"),
    ('tax',       'Tax',                r"\btax\b|\btaxes\b|\bRouanet\b|\bdeduct"),
    ('building',  'Building',           r"\bmasterplan\b|\brefurbish|\brenovat|\bconstruction\b|\bcapital (?:campaign|project|gift|donor)|\bendow|\bnew (?:wing|building|campus)\b|\bbuilt\b"),
    # Set by the review only: a tie the records state, with nothing said about what came with the money.
    ('money',     'Money only',         r"(?!x)x"),
]
# What happened to the tie. Not influence bought, but whether the funder kept it.
ENDED = r"\bdropp(?:ed|ing)\b|\bended\b|\bend(?:s|ing)? (?:its|the) (?:sponsor|partner|deal|relationship)|\bcut ties\b|\bsever|\bcame off\b|\btaken down\b|\bremov(?:ed|al) (?:of )?(?:the |its )?(?:\w+ )?name|\bname (?:came|was taken|was removed)|\bwill not renew|\bnot renew|\bstepped down\b|\bresigned\b|\breturn(?:ed)? (?:the )?(?:gift|money|donation)|\brefus(?:ed|e) (?:further |future )?(?:gifts|money|donations|funding)"
PROTEST = r"\bprotest|\bcampaign|\bboycott|\bopen letter|\bpetition|\bdie-in|\bactivists?\b|\boccup(?:y|ied|ation)\b"

YEAR = re.compile(r"\b(19[5-9]\d|20[0-2]\d)\b")
SENT = re.compile(r"(?<=[.!?])\s+(?=[A-Z\"'‘“(])")


def segments(r):
    """Each piece of a record's own text, with the field it is in, its sources and a date if the field carries one."""
    base = [u for u in (r.get('sources') or []) if isinstance(u, str)]
    det = r.get('details') if isinstance(r.get('details'), dict) else {}
    det_src = [s if isinstance(s, str) else (s.get('url') if isinstance(s, dict) else None) for s in (det.get('sources') or [])]
    det_src = [u for u in det_src if u]
    base = base or det_src   # a record with no top-level sources still cites its details' sources
    for f in ('funding', 'watch', 'why_flagged', 'highlight', 'tier_note', 'affiliations_note', 'records_note', 'finances_note', 'other_findings'):
        v = r.get(f)
        if isinstance(v, str) and v.strip():
            yield f, v, base, None
    for f in ('overview', 'funding', 'red_flags', 'press', 'wider_context'):
        v = det.get(f)
        for t in (v if isinstance(v, list) else [v] if isinstance(v, str) else []):
            if isinstance(t, str) and t.strip():
                yield 'details.' + f, t, det_src or base, None
    g = r.get('gossip_data') or {}
    for c in g.get('real_cases', []) or []:
        src = [s.get('url') for s in c.get('sources', []) if isinstance(s, dict) and s.get('url')]
        parts = [c.get('title') or ''] + list(c.get('facts') or []) + [c.get('response') or '', c.get('outcome') or '']
        for t in parts:
            if t:
                yield 'case', t, src or base, c.get('event_date')
    for it in g.get('gossip', []) or []:
        if it.get('status') not in ('confirmed', 'resolved', 'documented'):
            continue   # outside Gossip mode only what is confirmed or resolved (notes/gossip-criteria.md); the same holds here
        src = [u for u in (it.get('urls') or []) if isinstance(u, str)]
        for t in (it.get('headline'), it.get('said'), it.get('outcome')):
            if t:
                yield 'report', t, src or base, it.get('when')
    for c in r.get('case_notes', []) or []:
        if c.get('text'):
            yield 'case_note', c['text'], c.get('sources') or base, c.get('meta')


def urls(src):
    out = []
    for u in src or []:
        u = u.get('url') if isinstance(u, dict) else u
        if isinstance(u, str) and u.startswith('http') and u not in out:
            out.append(u)
    return out[:6]


def main():
    recs = json.load(open(os.path.join(ROOT, 'institutions.json')))
    fun = [(k, n, kind, re.compile(p)) for k, n, kind, p in FUNDERS]
    kinds = [(k, lab, re.compile(p, re.I)) for k, lab, p in KINDS]
    ended, protest = re.compile(ENDED, re.I), re.compile(PROTEST, re.I)
    out, seen = [], set()
    for r in recs:
        for field, text, src, date in segments(r):
            for s in SENT.split(text):
                s = s.strip()
                for fk, fname, fkind, fre in fun:
                    if not fre.search(s):
                        continue
                    ks = [k for k, _, kre in kinds if kre.search(s)]
                    key = (r['id'], fk, s)
                    if key in seen:
                        continue
                    seen.add(key)
                    y = YEAR.findall(s)
                    out.append({
                        'cid': hashlib.sha1(f"{r['id']}|{fk}|{s}".encode()).hexdigest()[:10],
                        'funder': fk, 'funder_name': fname, 'funder_kind': fkind,
                        'space': r['id'], 'space_name': r['name'], 'city': r.get('city', ''),
                        'field': field, 'text': s, 'kinds': ks,
                        'ended': bool(ended.search(s)), 'protest': bool(protest.search(s)),
                        'date': (str(date) if date else (y[0] if y else '')),
                        'sources': urls(src),
                    })
    out.sort(key=lambda c: (c['funder'], c['space'], c['field']))
    json.dump(out, open(os.path.join(ROOT, 'data', 'influence_candidates.json'), 'w'), ensure_ascii=False, indent=1)
    print(f'{len(out)} candidate sentences')
    build_layer(out)


def build_layer(cands):
    """assets/influence.json from the candidates the review keeps, grouped by funder."""
    path = os.path.join(ROOT, 'data', 'influence_review.json')
    review = json.load(open(path)) if os.path.exists(path) else {}
    byc = {c['cid']: c for c in cands}
    missing = [cid for cid in review if cid not in byc and not cid.startswith('_')]
    if missing:
        print(f'warning: {len(missing)} reviewed candidates no longer in the records: {missing[:5]}')
    names = {k: (n, kind) for k, n, kind, _ in FUNDERS}
    offices = json.load(open(os.path.join(ROOT, 'assets', 'hq.json')))['org']
    funders = {}
    for cid, v in review.items():
        if cid.startswith('_') or cid not in byc or v.get('drop'):
            continue
        c = byc[cid]
        n, kind = names[c['funder']]
        if c['funder'] not in funders:
            o = offices.get(c['funder']) or HQ_EXTRA.get(c['funder'])
            hq = {k: o[k] for k in ('n', 'c', 'co', 'lat', 'lon', 'a') if o and k in o} if o else None
            funders[c['funder']] = {'key': c['funder'], 'name': n, 'kind': kind, 'hq': hq, 'ties': []}
        f = funders[c['funder']]
        f['ties'].append({
            'space': c['space'], 'space_name': c['space_name'], 'city': c['city'],
            # Only what the review states: the keyword flags of a candidate are a reading aid, not a finding.
            'kinds': v.get('kinds', []), 'ended': bool(v.get('ended')), 'protest': bool(v.get('protest')),
            'summary': v['summary'], 'quote': c['text'], 'field': c['field'],
            'date': v.get('date', c['date']), 'sources': c['sources'],
            'check': v.get('check', 'record'),
            # What ties a money measure to this space (assets/influence-mode.js shows US lobbying, EU lobbying or political
            # giving only at a space a record links it to): [{measure: 'us' | 'eu' | 'politics', text, source}].
            **({'links': v['links']} if v.get('links') else {}),
        })
    for f in funders.values():
        f['ties'].sort(key=lambda t: (t['space_name'], t['date']))
    # The sender's side (user, 17 Nov 2026: "If the money doesn't go to culture it doesn't disappear so who is at fault?"):
    # what each funder's money is made from and what else it pays for beside culture. Hand-sourced, one source per fact,
    # read on that page; keyed by the same funder keys. A funder with no entry simply has no such rows.
    spath = os.path.join(ROOT, 'data', 'influence_senders.json')
    senders = json.load(open(spath)) if os.path.exists(spath) else {}
    for k, v in senders.items():
        if k.startswith('_') or k not in funders:
            continue
        funders[k]['sender'] = {'made_from': v.get('made_from', ''), 'facts': v.get('facts', []), 'figures': v.get('figures', {})}
    data = {
        'about': 'What each pilot funder is stated to have got for its money, from the atlas records. Built by tools/build_influence.py from data/influence_review.json.',
        'kinds': [{'key': k, 'label': lab} for k, lab, _ in KINDS],
        'funders': sorted(funders.values(), key=lambda f: -len(f['ties'])),
    }
    json.dump(data, open(os.path.join(ROOT, 'assets', 'influence.json'), 'w'), ensure_ascii=False, separators=(',', ':'))
    print(f"{sum(len(f['ties']) for f in funders.values())} entries for {len(funders)} funders in assets/influence.json")


if __name__ == '__main__':
    main()
