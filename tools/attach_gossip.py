#!/usr/bin/env python3
"""Write the gossip items from data/gossip_items.json onto the records they are about, as `gossip_data.gossip`.

The rules are in notes/gossip-criteria.md. This tool applies the mechanical ones and refuses the file when an item breaks them:
every required field present and of the right shape, `institution` matching one record (by name, id or alias), `urls` http(s)
addresses, `when` a date, `who_says`/`kind`/`status` from the lists, `headline` under 90 characters and free of
violent or criminal verbs of the editor's own (LOADED, outside quotation marks), `response` present when the
item names a person (any capitalised two-word name in `said` or `headline` — a rough net, so the editor checks §5 by hand).

Age (§6): an item whose `when` is more than 36 months before the run date and whose status is still `talk` is written with
status `stale`; a `rumour` older than 12 months with no rank-1/2 source is reported and left out. Re-running replaces the field.

Usage: python3 tools/attach_gossip.py [--check] && python3 tools/clean_data.py && python3 tools/embed_data.py
"""
import datetime as dt
import json
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ITEMS = ROOT / 'data' / 'gossip_items.json'
RECORDS = ROOT / 'institutions.json'

REQUIRED = ('id', 'institution', 'headline', 'said', 'who_says', 'where', 'when', 'urls', 'kind', 'status', 'retrieved_on')
WHO = {'press', 'court_or_regulator', 'union', 'open_letter', 'campaign', 'social_named', 'social_anonymous', 'review_platform', 'institution'}
KIND = {'rumour', 'report', 'allegation', 'dispute', 'departure', 'money', 'leak'}
STATUS = {'talk', 'denied', 'confirmed', 'resolved', 'stale'}
RANK12 = {'press', 'court_or_regulator'}
# Verbs that make a decision or a dispute sound like violence or a crime. A headline may carry one only inside a quotation.
# Crime terms a court, prosecutor or regulator uses (stolen, looting, seizures) are reported, not the editor's, so not listed.
LOADED = re.compile(r"\b(kill(?:s|ed|ing)?|axe[sd]?|axing|gut(?:s|ted|ting)?|slam(?:s|med|ming)?|blast(?:s|ed|ing)?|"
                    r"torpedo(?:es|ed|ing)?|destroy(?:s|ed|ing)?|wreck(?:s|ed|ing)?|sabotag\w*|hijack\w*|purge[sd]?|"
                    r"crack(?:s|ed)? down|crackdown|war on|bombshell)\b", re.I)
OUT_FIELDS = ('id', 'headline', 'said', 'told', 'who_says', 'where', 'when', 'urls', 'kind', 'status', 'response', 'outcome', 'retrieved_on')


def norm(s):
    s = unicodedata.normalize('NFKD', (s or '').lower())
    return re.sub(r'[^a-z0-9]+', ' ', ''.join(c for c in s if not unicodedata.combining(c))).strip()


def months_between(a, b):
    return (b.year - a.year) * 12 + (b.month - a.month)


# `told` is `said` retold in the voice of Gossip mode: an investigative journalist who talks the way a voice assistant with a
# character does (user, 21 Nov 2026: "Retell in gossip voice", after "it just not changing content to gossip"). It is optional,
# shown in place of `said` while Gossip mode is on, and written with tools/tell_gossip.py. It is a retelling and nothing else,
# so it is checked against the item it retells: no figure, quotation or name that the item does not carry, at least one of
# the item's sources named, no dash, no claim to a source of its own, and no longer than what it retells.
TOLD_DASH = re.compile(r'[\u2014\u2013]|\s-\s')
TOLD_OWN = re.compile(r"\b(?:my (?:own )?(?:sources?|reporting|investigation)|sources? (?:tell|told) me|"
                      r"I (?:have )?(?:obtained|interviewed|spoke(?:n)? (?:to|with)|uncovered|confirmed|verified))\b", re.I)


def _plain_quotes(s):
    return s.replace('\u201c', '"').replace('\u201d', '"').replace('\u2018', "'").replace('\u2019', "'")


def told_errors(it):
    """What is wrong with an item's `told`, as a list of sentences; empty when it has none or it is sound."""
    t = it.get('told')
    if t in (None, ''):
        return []
    if not isinstance(t, str):
        return ['told must be text']
    errs = []
    said = str(it.get('said') or '')
    src = _plain_quotes(' '.join(str(it.get(f) or '') for f in ('headline', 'said', 'response', 'outcome', 'where', 'institution')))
    told = _plain_quotes(t)
    if len(t) < 80:
        errs.append('told is under 80 characters')
    if len(t) > len(said) * 1.2 + 80:
        errs.append('told is longer than what it retells')
    if TOLD_DASH.search(t):
        errs.append('told has a dash')
    if TOLD_OWN.search(t):
        errs.append('told claims a source of its own')
    figures = lambda x: set(re.findall(r'\d+(?:[.,]\d+)*', x))
    extra = figures(told) - figures(src)
    if extra:
        errs.append('told has figures the item does not: ' + ', '.join(sorted(extra)))
    for quote in re.findall(r'"([^"]+)"', told):
        if quote.rstrip('.,') not in src:
            errs.append('told quotes words the item does not: ' + repr(quote[:50]))
    # A capitalised word that does not open a sentence is a name, and the item must carry it.
    for m in re.finditer(r"[A-Z][A-Za-z\u00c0-\u024f]+", told):
        before = told[:m.start()].rstrip()
        opens = not before or before[-1] in '.!?:"\'' and not re.search(r"[a-z,;]\s*[\"']$", told[:m.start()])
        word = re.sub(r"'s$", '', m.group(0))
        if not opens and word not in src:
            errs.append('told names what the item does not: ' + word)
    sources = [w for w in re.findall(r"[A-Z][A-Za-z\u00c0-\u024f+&]{2,}", str(it.get('where') or '')) if w not in ('The', 'Museum', 'Museums', 'Art', 'News')]
    if sources and not any(w in told for w in sources):
        errs.append('told names none of the item\'s sources')
    return errs


def parse_when(s):
    for fmt in ('%Y-%m-%d', '%Y-%m'):
        try:
            return dt.datetime.strptime(s, fmt).date()
        except (ValueError, TypeError):
            pass
    return None


def main(check_only=False):
    today = dt.date.today()
    items = json.load(open(ITEMS, encoding='utf-8'))
    recs = json.load(open(RECORDS, encoding='utf-8'))
    by_key = {}
    for r in recs:
        for k in [r.get('name'), r.get('id')] + list(r.get('aliases') or []):
            if k and r not in by_key.setdefault(norm(k), []):
                by_key[norm(k)].append(r)

    errors, dropped, attached = [], [], {}
    seen_ids = set()
    for it in items:
        iid = it.get('id', '?')
        for f in REQUIRED:
            if f not in it or it[f] in ('', None, []):
                errors.append(f'{iid}: missing {f}')
        if iid in seen_ids:
            errors.append(f'{iid}: duplicate id')
        seen_ids.add(iid)
        if not re.fullmatch(r'G\d+', str(iid)):
            errors.append(f'{iid}: id must be G plus a number')
        if it.get('who_says') not in WHO:
            errors.append(f'{iid}: who_says {it.get("who_says")!r} not in {sorted(WHO)}')
        if it.get('kind') not in KIND:
            errors.append(f'{iid}: kind {it.get("kind")!r} not in {sorted(KIND)}')
        if it.get('status') not in STATUS:
            errors.append(f'{iid}: status {it.get("status")!r} not in {sorted(STATUS)}')
        if len(str(it.get('headline', ''))) > 90:
            errors.append(f'{iid}: headline over 90 characters')
        # A headline is said in the source's own register (user, 4 Nov 2026: "do not make alerts criminal, the article has
        # neutral language"): no violent or criminal verb of the editor's own. Words inside quotation marks are the source's.
        unquoted = re.sub(r"(?<!\w)'[^']*'(?!\w)|\"[^\"]*\"|‘[^’]*’|“[^”]*”", '', str(it.get('headline', '')))
        loaded = LOADED.findall(unquoted)
        if loaded:
            errors.append(f'{iid}: headline uses {", ".join(sorted(set(w.lower() for w in loaded)))!r}; say what the source says '
                          '(scraps, cancels, halts, ends), or quote whoever used the word')
        urls = it.get('urls') or []
        if not isinstance(urls, list) or not 1 <= len(urls) <= 4 or any(not re.match(r'https?://', str(u)) for u in urls):
            errors.append(f'{iid}: urls must be one to four http(s) addresses')
        if any('wikipedia.org' in str(u) for u in urls):
            errors.append(f'{iid}: Wikipedia is never a source')
        when = parse_when(it.get('when'))
        if not when:
            errors.append(f'{iid}: when must be YYYY-MM-DD or YYYY-MM')
        if not parse_when(it.get('retrieved_on')):
            errors.append(f'{iid}: retrieved_on must be a date')
        text = f"{it.get('headline', '')} {it.get('said', '')}"
        names_person = bool(re.search(r"\b[A-Z][a-z]+(?:-[A-Z][a-z]+)? [A-Z][a-z]+(?:-[A-Z][a-z]+)?\b", re.sub(r"\b(The|Museum|Gallery|Centre|Center|Art|Modern|Foundation|Institute|National|Royal|Reddit|Instagram|Union|Trust|Board|Museo|Musée|Palais|Fondation|Haus|Staatliche|British|New York|Los Angeles)\b", '', text)))
        if names_person and not str(it.get('response', '')).strip():
            errors.append(f'{iid}: names a person but has no response (write "No reply found." if so)')
        errors.extend(f'{iid}: {e}' for e in told_errors(it))
        key = norm(it.get('institution'))
        hits = by_key.get(key) or []
        exact = [r for r in hits if norm(r.get('name')) == key or norm(r.get('id')) == key]
        if len(hits) > 1 and len(exact) == 1:
            hits = exact                       # a record's own name or id wins over another record's alias
        if len(hits) != 1:
            errors.append(f'{iid}: institution {it.get("institution")!r} matches {len(hits)} records')
            continue
        if errors:
            continue
        status = it['status']
        age = months_between(when, today)
        if it['kind'] == 'rumour' and status == 'talk' and age > 12 and it['who_says'] not in RANK12:
            dropped.append(f'{iid}: rumour older than 12 months with no rank-1/2 source (§6), left out')
            continue
        if status == 'talk' and age > 36:
            status = 'stale'
        out = {f: it.get(f) for f in OUT_FIELDS if it.get(f) not in (None, '')}
        out['status'] = status
        attached.setdefault(id(hits[0]), (hits[0], []))[1].append(out)

    for e in errors:
        print('ERROR', e)
    for d in dropped:
        print('NOTE', d)
    if errors:
        print(f'{len(errors)} error(s); nothing written.')
        sys.exit(1)

    n_recs = 0
    for r in recs:
        g = r.get('gossip_data')
        if isinstance(g, dict) and 'gossip' in g:
            del g['gossip']
            if not g:
                del r['gossip_data']
    for _, (rec, lst) in attached.items():
        lst.sort(key=lambda x: (x['status'] == 'stale', ''), reverse=False)
        lst.sort(key=lambda x: x['when'], reverse=True)
        lst.sort(key=lambda x: x['status'] == 'stale')
        rec.setdefault('gossip_data', {})['gossip'] = lst
        n_recs += 1
    total = sum(len(v[1]) for v in attached.values())
    if check_only:
        print(f'ok: {total} items on {n_recs} records (not written)')
        return
    json.dump(recs, open(RECORDS, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    print(f'wrote {total} items on {n_recs} records')


if __name__ == '__main__':
    main('--check' in sys.argv)
