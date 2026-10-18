#!/usr/bin/env python3
"""Rules that decide what the page is allowed to show from institutions.json.

A field is kept only if a record states it and something outside the museum's own
marketing backs it. Run `python3 tools/clean_data.py` to rewrite institutions.json
in place. index.html embeds the same result.

What it does not do: it does not verify anything. Verification results live in
data/verification.json (see tools/verify_claims.py).
"""
import collections
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

CORRECTIONS = Path(__file__).resolve().parent.parent / 'data' / 'corrections.json'

# Free text where one value shared by 5+ records (after masking name and city) is filler.
TEXT = ['watch', 'funding', 'opening_hours', 'admission_fee', 'admission_policy', 'admission_details',
        'curator_recommendation', 'accessibility', 'amenities', 'transit_tips', 'highlight', 'visit_duration',
        'ethical_safeguard', 'governance_details', 'curatorial_focus', 'address', 'neighborhood']
# Invented or unsourced: generated figures and stories, and classification labels that assert verification.
DROP = ['financial_data', 'temporary_shows', 'floor_plans', 'archives_and_collections', 'building_architecture',
        'tier_label', 'transparency_grade', 'governance_classification', 'governance_type',
        'governance_details', 'ethical_safeguard',   # assertions with no source, one of them the same sentence on 36 records
        'curator_recommendation']   # written by the model, never shown
AGGREGATORS = {'propublica.org', 'findthatcharity.uk', 'charitycommission.gov.uk', 'web.archive.org', 'e-flux.com',
               'facebook.com', 'instagram.com', 'linkedin.com', 'twitter.com', 'x.com', 'wikipedia.org'}


LOST_AMOUNT = re.compile(r'(?<![\w$€£¥])\.\d+\s?[BMK]\b|(?<![\w$€£¥])M\+|^\s*\d+(?:\.\d+)?\s?[BMK]\.')
LOST_AMOUNT_FRAGMENT = re.compile(r'^\s*\d+(?:\.\d+)?\s?[BMK]\.\s*|[^.;]*(?:(?<![\w$€£¥])\.\d+\s?[BMK]\b|(?<![\w$€£¥])M\+)[^.;]*[.;]\s*')


# Sentences that assert the absence of ties or the strictness of a policy. Nobody has checked them, and a negative
# claim about a named organisation needs more than a note. The rest of the note stays.
ASSERTION = re.compile(
    r"\b(zero|no|without|free of|free from|clear of)\b[^.;]{0,40}\b(corporate|fossil|defen[cs]e|weapon|extractive|high-carbon|predatory|private equity|sponsor|underwrit|capture|naming rights|extraction|state|oligarch|subsid|ministr|government)"
    r"|\bclean\b[^.;]{0,20}\b(ethical|funding|governance|record|roster|underwriting|sponsorship)"
    r"|\b100% (independent|clean|municipal|public)"
    r"|\b(strict|strictly|rigorous|robust)\b"
    r"|\b(completely|fully|entirely|wholly|structurally) (independent|free)"
    r"|\bethical (sponsorship|review|fundraising|record|trading|giving|scrutiny|guidelines|policy|standards)"
    r"|\btransparent (donor|supporter|ledger|disclosure|roster)|\bvetted\b"
    r"|\b(sanctuary|beacon|bastion|heroic|indispensable|vanguard|cradle|cornerstone|iconic|world-famous|acclaimed|exemplary|unforgettable)\b", re.I)
# The public registries a record may link to. Anything else under the registry fields is dropped.
REGISTRIES = ('projects.propublica.org', 'register-of-charities.charitycommission.gov.uk', 'bundesanzeiger.de', 'openkvk.nl',
              'apps.cra-arc.gc.ca', 'journal-officiel.gouv.fr', 'acnc.gov.au', 'servizi.lavoro.gov.it', 'sede.mjusticia.gob.es', 'edi.admin.ch')
ASSERTION_FIELDS = ['watch', 'funding', 'curator_recommendation', 'highlight']
PUFF = re.compile(r"\b(beating heart|extraordinary|daring|fearless|legendary|renowned|celebrated|world-class|cultural anchor|cultural destination|"
                  r"dramatic|breathtaking|stunning|vibrant|dynamic|progressive voices|landmark holdings|sublime|iconic|epicenter|epicentre|"
                  r"marvel|paradise|nestled|pioneer|pioneering|radical|powerhouse|gem|jewel|must-see|world-renowned|globally renowned)\b", re.I)
# Templates the generator stamped on many records, and internal triage text.
DROP_PREFIX = {'curator_recommendation': ['Excluded from Culture Atlas'],
               'highlight': ['Audited institution', 'Founded in Independent', 'Founded in Established',
                             'Specialist research repository', 'Open-air cultural destination'],
               'accessibility': ['Check venue site', 'Step-free accessible'],
               'transit_tips': ['Centrally']}
STRIP_PREFIX = ['Flagged institution: ']


def drop_assertions(text):
    parts = [x for x in re.split(r'(?<=\.)\s+', text.strip()) if x]   # whole sentences only, so no fragment is left behind
    kept = [x for x in parts if not ASSERTION.search(x) and not PUFF.search(x)]
    out = ' '.join(kept).strip().rstrip(';,').strip()
    return out if len(out) >= 12 else ''


def reg(host):
    parts = (host or '').lower().removeprefix('www.').split('.')
    if len(parts) > 2 and parts[-2] in ('co', 'com', 'org', 'ac', 'gov'):
        return '.'.join(parts[-3:])
    return '.'.join(parts[-2:])


def full_host(url):
    return (urlparse(url or '').hostname or '').lower().removeprefix('www.')


def host_of(url):
    p = urlparse(url or '')
    if not p.netloc:
        return None
    h = reg(p.netloc)
    if h == 'web.archive.org':
        m = re.search(r'web\.archive\.org/web/\d+[a-z_]*/(https?://[^/]+)', url)
        return reg(urlparse(m.group(1)).netloc) if m else h
    return h


def norm(value, rec):
    t = str(value).lower()
    for x in [rec.get('name'), rec.get('city'), rec.get('country'), rec.get('neighborhood'),
              (rec.get('location') or '').split(',')[0]]:
        if x and len(x) > 2:
            t = t.replace(x.lower(), '@')
    return re.sub(r'\d+', '#', t).strip()


def independent_sources(rec):
    own = host_of(rec.get('website'))
    urls = [u for u in rec.get('sources') or [] if re.match(r'https?://', u)]
    return [u for u in urls if host_of(u) and host_of(u) != own
            and host_of(u) not in ('facebook.com', 'instagram.com', 'linkedin.com', 'twitter.com', 'x.com')]


def has_reason(rec):
    g = rec.get('gossip_data') or {}
    # A note alone is not a reason: "flagged" needs a recorded reason.
    return bool(rec.get('why_flagged') or rec.get('flags') or rec.get('other_findings') or rec.get('epstein_records')
                or rec.get('wikileaks_records') or g.get('real_cases'))


def generic_link(rec, key):
    url = rec.get(key) or ''
    if not url:
        return True
    # Keep only registry searches and registry pages. A link into the museum's own site is not an audit.
    h, own = host_of(url), host_of(rec.get('website'))
    return h == own or h == 'edi.admin.ch' or not urlparse(url).path.strip('/') and not urlparse(url).query


def clean(records, report=None):
    report = {} if report is None else report
    bump = lambda k, n=1: report.__setitem__(k, report.get(k, 0) + n)
    # one record per museum: a later record with the same name is dropped; one with the same id is the same museum under
    # a shorter name, and is folded into the first: empty fields filled, lists joined, its name kept as an alias.
    LISTS = ('sources', 'flags', 'aliases', 'funder_links', 'epstein_records', 'wikileaks_records', 'case_notes', 'other_findings')
    seen, by_id, kept = {}, {}, []
    for r in records:
        key = r['name'].lower()
        if key in seen or 'Record was wrong' in (r.get('watch') or ''):
            bump('duplicate_or_retracted_records')
            continue
        first = by_id.get(r.get('id'))
        if first is not None:
            for k, v in r.items():
                if v in (None, '', [], {}):
                    continue
                if k in LISTS:
                    have = first.get(k) or []
                    keys = {json.dumps(x, sort_keys=True) for x in have}
                    first[k] = have + [x for x in v if json.dumps(x, sort_keys=True) not in keys]
                elif first.get(k) in (None, '', [], {}):
                    first[k] = v
                elif k in ('funding', 'watch') and v != first[k]:
                    report.setdefault('merged_text_dropped', []).append({'id': r['id'], 'field': k, 'text': v})
            if r['name'] != first['name']:
                first['aliases'] = list(dict.fromkeys((first.get('aliases') or []) + [r['name']]))
            bump('merged_same_id_records')
            continue
        seen[key] = r
        by_id[r.get('id')] = r
        kept.append(r)
    records[:] = kept
    for f in TEXT:
        counts = collections.Counter(norm(r[f], r) for r in records if r.get(f))
        for r in records:
            if r.get(f) and counts[norm(r[f], r)] >= 5:
                del r[f]
                bump(f)
    for r in records:
        for k in DROP:
            if k in r:
                del r[k]
                bump(k)
        g = r.get('gossip_data')
        if g is not None:                      # keep sourced case files only
            keep = {k: g[k] for k in ('real_cases', 'accounts') if g.get(k)}
            if keep:
                r['gossip_data'] = keep
            else:
                del r['gossip_data']
            if g.get('review_leads'):
                bump('review_leads')           # anonymous staff reviews cannot be checked
        for key in ('epstein_records', 'wikileaks_records'):   # the source data lists some items twice
            if r.get(key):
                unique = list({json.dumps(x, sort_keys=True): x for x in r[key]}.values())
                if len(unique) != len(r[key]):
                    bump('duplicate_' + key, len(r[key]) - len(unique))
                r[key] = unique
        if not isinstance(r.get('year_founded'), int):
            r.pop('year_founded', None)
        for key in ('website', 'visit_url'):   # a registry page is not the museum's website
            if r.get(key) and host_of(r[key]) in AGGREGATORS:
                del r[key]
                bump(key + '_was_a_registry_page')
        for key in ('audit_dossier_url', 'statutory_filings_url'):
            if key in r and generic_link(r, key):
                del r[key]
                bump(key + '_was_the_museums_own_about_page')
            elif key in r and not any(full_host(r[key]) == h or full_host(r[key]).endswith('.' + h) for h in REGISTRIES):
                del r[key]                     # a web search, a Facebook page or a listing site is not a public registry
                bump(key + '_was_not_a_registry')
        if r.get('watch'):                     # internal triage notes are not for readers
            w = re.sub(r'\s*\(Previous note:.*$', '', r['watch'])
            r['watch'] = re.sub(r'^(WATCH / ETHICAL AUDIT|WATCH / EXCLUDED|WATCH|EXCLUDED):\s*', '', w)
        if re.search(r'\b(employee|workplace|staff) (reviews?|accounts?)\b', r.get('watch') or '', re.I):
            del r['watch']                     # summarised anonymous staff reviews, which are no longer shown
            bump('watch_summarising_staff_reviews')
        for f in ASSERTION_FIELDS:
            v = r.get(f)
            if isinstance(v, str) and (ASSERTION.search(v) or PUFF.search(v)):
                v2 = drop_assertions(v)
                bump('unchecked_assertion_in_' + f)
                if v2:
                    r[f] = v2
                else:
                    del r[f]
        for f in TEXT:                         # amounts whose currency symbol and digits were lost upstream ("M+ annual budget; .2B endowment")
            v = r.get(f)
            if isinstance(v, str) and LOST_AMOUNT.search(v):
                v = LOST_AMOUNT_FRAGMENT.sub('', v).strip()
                if v:
                    r[f] = v
                else:
                    del r[f]
                bump('damaged_amount_removed')
        r['sources'] = [u for u in r.get('sources') or [] if re.match(r'https?://', u)]
        if r['tier'] == 'A' and not independent_sources(r):
            r['tier'] = 'U'
            r['tier_note'] = 'No source outside the museum is recorded.'
            bump('tier_A_to_unverified')
        elif r['tier'] == 'B' and not has_reason(r):
            r['tier'] = 'U'
            r['tier_note'] = 'No reason for the flag is recorded.'
            bump('tier_B_to_unverified')
    corrections = json.load(open(CORRECTIONS, encoding='utf-8')) if CORRECTIONS.exists() else {}
    # a search page is not a source
    for r in records:
        if r.get('sources'):
            kept = [u for u in r['sources'] if not re.search(r'(^|//)(www\.)?(search\.brave\.com|duckduckgo\.com|bing\.com/search|google\.[a-z.]+/search)|[?&/]search\b', u)]
            if len(kept) != len(r['sources']):
                bump('search_page_sources', len(r['sources']) - len(kept))
                r['sources'] = kept
    # a founding year shared by dozens of unrelated museums is a default, not a fact
    years = collections.Counter(str(r['year_founded']) for r in records if r.get('year_founded'))
    for r in records:
        if r.get('year_founded') and years[str(r['year_founded'])] >= 25:
            del r['year_founded']
            bump('year_founded')
    for r in records:
        for f, prefixes in DROP_PREFIX.items():
            if r.get(f) and any(r[f].startswith(x) for x in prefixes):
                del r[f]
                bump('template_' + f)
        for pre in STRIP_PREFIX:
            if (r.get('curator_recommendation') or '').startswith(pre):
                r['curator_recommendation'] = r['curator_recommendation'][len(pre):]
        if r.get('size') not in ('S', 'M', 'L'):
            m = {'Small': 'S', 'Medium': 'M', 'Large': 'L'}.get(r.get('size'))
            if m:
                r['size'] = m
            else:
                r.pop('size', None)
                bump('size')
    for f in ('highlight', 'curator_recommendation', 'curatorial_focus'):
        starts = collections.Counter(' '.join(norm(r[f], r).split()[:4]) for r in records if r.get(f))
        for r in records:
            if r.get(f) and starts[' '.join(norm(r[f], r).split()[:4])] >= 4:
                del r[f]
                bump('shared_opening_' + f)
    # "Consensus Study" is the name of the search tool the citation came through, not a citation
    for r in records:
        for v in r.get('visual_critiques') or []:
            if v.get('citation'):
                cleaned = re.sub(r'\s*[/;.,]?\s*Consensus Study\.?\s*$', '', v['citation']).strip()
                if cleaned != v['citation']:
                    v['citation'] = cleaned
                    bump('citation_tool_name')
    for r in records:
        for field, text in (corrections.get(r['id']) or {}).items():
            r[field] = text
            bump('corrected_after_checking')
    # The Clean Funding Grade is computed last, from the cleaned flags and sources (tools/grade_funding.py).
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import grade_funding
    for k, n in grade_funding.apply(records).items():
        report['grade ' + k] = n
    return report


if __name__ == '__main__':
    path = sys.argv[1] if len(sys.argv) > 1 else 'institutions.json'
    data = json.load(open(path, encoding='utf-8'))
    print(json.dumps(clean(data), indent=1))
    json.dump(data, open(path, 'w', encoding='utf-8'), indent=2, ensure_ascii=True)
