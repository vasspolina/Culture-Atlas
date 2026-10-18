#!/usr/bin/env python3
"""Clean Funding Grade: one grade per record, 1 (cleanest) to 5, from what the record proves.

The grade says two things about the money: what it is, and whether the record shows it. Dirt and darkness are
different failings, so a record without an independently sourced funder roster is not graded; silence is not cleanliness.

  1  Clean, money shown      no flag-category funder and no documented objection, and the record shows figures
                             (amounts or shares in the funding text), or links accounts or a public registry filing
  2  Clean, roster shown     the same, but names only
  3  A name to know          a funder worth noting outside the flag categories (a Flagged record with no flag), or a
                             tie or objection with no flagged funder: Gulf state body, Epstein-linked, a campaigned
                             name, a protest, a sponsor dropped, censorship
  4  One flagged funder      one funder from a flag category: fossil fuels, tobacco, gambling, arms, opioids,
                             sanctions, forced labour, prisons, a mining disaster
  5  Several, or flagged     more than one flagged funder category, or a flagged funder plus a documented objection
     and contested
  -  not graded              No independently sourced funder roster is recorded

Rules the grade follows: public money alone is never a flag, so a wholly public museum sits at 1 or 2. A flag counts
only when the record carries it, which the Sponsor Atlas second checks decided. Disclosure only moves a record up,
from 2 to 1; nobody is marked down for it.

tools/clean_data.py calls apply() at the end, so every pipeline run grades the records. Run it alone with
`python3 tools/grade_funding.py` to regrade institutions.json and print the spread. Each graded record gets
`grade` (1 to 5) and `grade_basis` (one sentence saying what decided it); an ungraded record has neither.
"""
import collections
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent

HEAVY = ['Fossil fuels', 'Tobacco', 'Gambling', 'Arms and defence', 'Opioids', 'Sanctions',
         'Forced or exploited labour', 'Prison or detention', 'Mining disaster']
TIES = ['Gulf state body', 'Epstein-linked']
OBJECTIONS = ['Campaigned name', 'Protest or boycott', 'Sponsor dropped under pressure', 'State censorship or punishment']

LABEL = {1: 'Clean, money shown', 2: 'Clean, roster shown', 3: 'A name to know',
         4: 'One flagged funder', 5: 'Several, or flagged and contested'}

# Figures in the funding text: an amount with a currency, a figure in millions or billions, or a share.
FIGURE = re.compile(r"(?:[$£€¥]|\bUS\$|\bUSD|\bEUR|\bGBP|\bCHF|\bDKK|\bSEK|\bNOK|\bCAD|\bAUD|\bNZD|\bBRL|\bMXN|\bINR|\bJPY|\bKRW|\bPLN"
                    r"|\bCZK|\bHUF|\bZAR|\bTRY|\bRUB|\bR\$|\bS/|\bFCFA|\bCFA)\s?\d"
                    r"|\b\d[\d.,]*\s?(?:M|bn|million|billion|mn|m)\b"
                    r"|\b\d{1,3}\s?%")
# Public registries and published accounts a source may point to.
REGISTRY_HOSTS = ('projects.propublica.org', 'findthatcharity.uk', 'register-of-charities.charitycommission.gov.uk',
                  'charitycommission.gov.uk', 'find-and-update.company-information.service.gov.uk', 'bundesanzeiger.de',
                  'openkvk.nl', 'apps.cra-arc.gc.ca', 'journal-officiel.gouv.fr', 'acnc.gov.au', 'servizi.lavoro.gov.it',
                  'sede.mjusticia.gob.es', 'edi.admin.ch', 'candid.org', 'guidestar.org', 'north-data.de', 'zefix.ch',
                  'oscr.org.uk', 'charitiesregulator.ie', 'cro.ie', 'brreg.no', 'virk.dk', 'allabolag.se', 'prh.fi',
                  'register.gov.au', 'abr.business.gov.au', 'sam.gov', 'opencorporates.com')
ACCOUNTS_PATH = re.compile(r"annual[-_ ]?report|jahresbericht|aarsrapport|arsrapport|årsrapport|årsredovisning|jaarverslag|bilancio|"
                           r"rapport[-_ ]?annuel|rapport[-_ ]?d[-_ ]?activit|memoria[-_ ]?anual|financial[-_ ]?statement|"
                           r"annual[-_ ]?accounts|audited|form[-_ ]?990|\b990\b|relatorio|relatório|informe[-_ ]?anual|"
                           r"tilinpaatos|årsberetning|cuentas[-_ ]?anuales|comptes", re.I)


def host_of(url):
    h = (urlparse(url or '').hostname or '').lower()
    return h[4:] if h.startswith('www.') else h


def disclosure(rec):
    """Where the record shows the money: a phrase for the basis sentence, or '' when it shows names only."""
    if FIGURE.search(rec.get('funding') or ''):
        return 'figures are shown'
    for key, word in (('statutory_filings_url', 'filings'), ('audit_dossier_url', 'a registry entry')):
        if rec.get(key):
            return f'{word} are linked ({host_of(rec[key])})'
    for u in rec.get('sources') or []:
        h = host_of(u)
        if any(h == r or h.endswith('.' + r) for r in REGISTRY_HOSTS):
            return f'a registry filing is linked ({h})'
        if ACCOUNTS_PATH.search(urlparse(u).path or ''):
            return f'accounts are linked ({h})'
    return ''


def grade(rec):
    """(grade, basis) for one record, or (None, None) when the record cannot be graded."""
    flags = [f for f in rec.get('flags') or [] if f]
    heavy = [f for f in flags if f in HEAVY]
    ties = [f for f in flags if f in TIES]
    objections = [f for f in flags if f in OBJECTIONS]
    tier = rec.get('tier')
    if tier == 'U' and not flags:
        return None, None
    if heavy and (len(heavy) > 1 or objections):
        what = f"Flagged funders: {', '.join(heavy).lower()}" if len(heavy) > 1 else f"A flagged funder, {heavy[0].lower()}"
        why = f"; with a documented objection: {', '.join(objections).lower()}" if objections else ''
        return 5, f'{what}{why}.'
    if heavy:
        return 4, f'One flagged funder category on record: {heavy[0].lower()}.'
    if ties or objections:
        return 3, f"A tie or objection on record, with no flagged funder: {', '.join(ties + objections).lower()}."
    if tier == 'B':
        return 3, 'A funder worth noting, outside the flag categories.'
    shown = disclosure(rec)
    if shown:
        return 1, f'No flagged funder or objection on record, and {shown}.'
    return 2, 'No flagged funder or objection on record; funders are named, with no figures.'


def apply(records):
    counts = collections.Counter()
    for r in records:
        g, basis = grade(r)
        if g is None:
            r.pop('grade', None)
            r.pop('grade_basis', None)
            counts['not graded'] += 1
        else:
            r['grade'] = g
            r['grade_basis'] = basis
            counts[f'{g} {LABEL[g]}'] += 1
    return counts


if __name__ == '__main__':
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / 'institutions.json'
    data = json.load(open(path, encoding='utf-8'))
    for k, n in sorted(apply(data).items()):
        print(f'{n:5d}  {k}')
    json.dump(data, open(path, 'w', encoding='utf-8'), indent=2, ensure_ascii=True)
