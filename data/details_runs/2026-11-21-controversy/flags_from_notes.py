"""Record flags and tiers brought in line with the checked findings of the controversy pass of 21 Nov 2026.

Each change follows sponsor-atlas/work/ubatch/CHECKER.md (with the editor's rulings of 26 October 2026) and rests only on
the checked finding in data/details_runs/2026-11-21-controversy/findings/<id>.txt: its Red flags headings are the flag
bases; WIDER CONTEXT items are not flags. Only records named in editor_notes.md beside this file are touched.

What is flagged:
- Protest or boycott: a documented protest, open letter, petition, boycott call or artist withdrawal aimed at the space,
  its funders or its leadership, or a staff strike, walkout or union action at the space, since October 2021.
- State censorship or punishment: the state or funder that pays for or controls the space removed its director or
  stopped a show, or the space itself took down or forbade work, since October 2021.
- A name to know (tier B, no flag): a director or owner with a conviction or a regulator's fine.

What is left as text only, by the same rules (the editor can still rule otherwise; each is in editor_notes.md):
- Looted or contested holdings (returns, seizures, restitution rulings): a Red flags heading, not one of the map's flag
  categories, so the tier stays (Altes Museum, Gemäldegalerie, Glyptothek, the Morgan, Allen, RISD, San Antonio,
  Worcester, MAK, National Museum of Finland, Kunstmuseum Den Haag, Kunstmuseum Bern).
- Findings the checkers called weak or judgement calls: a single member's withdrawal (Akademie der Künste), a strike that
  the source does not show to be the house's own dispute (Deutsche Oper Berlin), a city-wide dispute of outsourced staff
  (Castello Sforzesco), unions that announced action without a recorded strike (Bargello), objections by a party or a
  campaign group with no protest, letter or petition (Piccolo Teatro, MANN Naples, Gallerie Estensi, Lothringer 13),
  a petition in defence of the museum against a government plan (Hong Kong Heritage Museum), a programme change over
  Russia's war that no artist contested on record (Tonhalle, Kölner Philharmonie), a claim resting on one partisan
  account (Teatro Tomás Terry), a committee vote that is not yet a budget law (Museo de la Memoria), a union's demand
  for an inquiry (Fries Museum), and dismissals over management with no censorship in them (MOCAK, MUNAM Guatemala).
- Perot Museum: its oil and gas donors gave to the 2008 to 2012 building campaign and the one documented objection is
  from 2014, so Fossil fuels needs a ruling on whether that money still counts as current.

Grades are recomputed afterwards by tools/clean_data.py.

Usage: python3 data/details_runs/2026-11-21-controversy/flags_from_notes.py institutions.json
"""
import json
import sys

p = sys.argv[1]
recs = json.load(open(p, encoding='utf-8'))
d = {r['id']: r for r in recs}
PLACEHOLDERS = ('No reason for the flag is recorded.', 'No source outside the museum is recorded.')
log = []


def put(i, **kw):
    r = d[i]
    for k, v in kw.items():
        if r.get(k) != v:
            r[k] = v
            log.append(f'{i}: {k} = {v if isinstance(v, (list, int)) else v[:80]}')
    if r.get('tier_note') in PLACEHOLDERS:
        r.pop('tier_note')
        log.append(f'{i}: removed placeholder tier_note')


PROTEST = ['Protest or boycott']
CENSOR = ['State censorship or punishment']

# Staff strikes, walkouts and union action at the space
put('teatro-carlo-felice', tier='B', flags=PROTEST,
    why_flagged='The union Slc Cgil struck over evening staff pay on 31 December 2022 and called a strike of the theatre\'s staff for 7 December 2025.')
put('museo-nacional-de-arte', tier='B', flags=PROTEST,
    why_flagged='Workers shut the museum in March 2023 in protest at cuts to its guards, and union demands closed it again on 9 September 2025.')
put('museo-picasso-malaga', tier='B', flags=PROTEST,
    why_flagged='Staff protested at the entrance from 20 May 2023 and voted to strike over a collective agreement after eleven years without a raise.')
put('buffalo-akg-art-museum', tier='B', flags=PROTEST,
    why_flagged='In 2025 it planned to lay off 13 unionised visitor staff; their union called it union busting and rallied against it.')
put('arts-centre-melbourne', tier='B', flags=PROTEST,
    why_flagged='Staff rejected a 3 per cent pay offer in 2026 and struck for 24 hours on 11 September, which cancelled or postponed shows.')

# Protests, open letters, petitions, boycott calls and withdrawals aimed at the space
put('opernhaus-zurich', tier='B', flags=PROTEST,
    why_flagged='In 2025 an open letter from Helvetia for Ukraine and a protest at the premiere opposed its casting of Anna Netrebko.')
put('national-museum-prague', tier='B', flags=PROTEST,
    why_flagged='Several hundred people demanded in March 2023 that it take down its Ukrainian flag; in October 2025 others protested its removal.')
put('museum-der-bildenden-kunste-leipzig', tier='B', flags=PROTEST,
    why_flagged='After racist terms were spoken at a May 2023 opening, Black activists objected and cooperation partners withdrew from working with it.')
put('thalia-theater', tier='B', flags=PROTEST,
    why_flagged="In April 2024 the association Pro Quote Bühne called for a boycott of Joachim Lux's farewell season over its near absence of women.")
put('tower-of-david-museum', tier='B', flags=PROTEST,
    why_flagged="In June 2023 Jerusalem's Chief Sephardi Rabbi called on Jews to boycott it over a conference on attacks on Christians.")
put('laboral-centro-de-arte-y-creaci-n-industrial-gij-n', tier='B', flags=PROTEST,
    why_flagged='More than 700 professionals signed a letter against the dismissal of its director in February 2025, and three members of its scientific commission resigned.')
put('anu-museum-of-the-jewish-people', tier='B', flags=PROTEST,
    why_flagged="In December 2025 the group Yad L'Achim called on the public to stay away over displays on mixed marriage.")
put('mambo-bologna', tier='B', flags=PROTEST,
    why_flagged='In August 2025 the animal rights group LAV called for a boycott of its show "Facile ironia" over stuffed animals.')
put('luma-arles', tier='B', flags=PROTEST,
    why_flagged='On 11 September 2025 protesters gathered at the foot of its tower with a banner addressed to its founder, Maja Hoffmann.')
put('the-mac', tier='B', flags=PROTEST,
    why_flagged='A former councillor and others protested outside on 31 July 2022 against its drag storytime event; a larger counter-protest backed it.')
put('printed-matter-new-york', tier='B', flags=PROTEST,
    why_flagged="At its 2024 New York Art Book Fair, participants circulated a petition urging it to join the cultural boycott of Israel.")
put('museo-nacional-del-ecuador-muna-quito', tier='B', flags=PROTEST,
    why_flagged='A petition of almost 3,000 signatures and a protest at the July 2026 presentation opposed the winning design for its new building.')

# The state or funder that controls the space removed its director or stopped a show
put('centro-andaluz-de-arte-contemporaneo', tier='B', flags=CENSOR + PROTEST,
    why_flagged="The Junta de Andalucía removed its director of 14 years in October 2023; its technical commission resigned in protest and CIMAM objected.")
put('museo-de-arte-costarricense-mac-san-jos', tier='B', flags=CENSOR,
    why_flagged="Costa Rica's culture minister dismissed its deputy director in November 2024 and its director in December 2025.")
put('montgomery-museum-of-fine-arts', tier='B', flags=CENSOR,
    why_flagged='City officials put its director on leave in February 2023 and the mayor named an interim director without consulting its boards.')
put('konsthall-c-stockholm', tier='B', flags=CENSOR,
    why_flagged='A Stockholm district director cancelled a show it co-curated at Sergels torg in June 2022 as too political.')

# The space itself took down or forbade work
put('sadler-s-wells', tier='B', flags=CENSOR + PROTEST,
    why_flagged="Its director forbade Maguy Marin's statement on Gaza in May 2024; associate artist Michael Keegan-Dolan left in 2025 over its Barclays partnership.")
put('ploshchad-mira-museum-centre-krasnoyarsk', tier='B', flags=CENSOR,
    why_flagged="Before its Museum Night on 1 November 2025 the portrait of the convicted artist Vasily Slonov was taken off its board of honour.")
put('festival-internacional-jazz-plaza', tier='B', flags=CENSOR,
    why_flagged="Its 2025 edition cancelled a screening of Pavel Giroud's documentary without explanation, the filmmaker said; a cultural rights group called it censorship.")
put('yorkshire-sculpture-park', tier='B', flags=CENSOR,
    why_flagged="It left Erwin Wurm's Fat Car works out of his 2023 show; Wurm said the park did not want to show them.")

# Names to know (tier B, no flag)
put('national-museum-of-the-republic-of-kazakhstan-astana', tier='B',
    why_flagged='An Astana court convicted its former director Arystanbek Mukhamediuly in June 2023 of organising the embezzlement of exhibition money.')
put('colección-femsa-monterrey', tier='B',
    why_flagged="Mexico's telecoms regulator fined its owner FEMSA's OXXO chain in 2025 for blocking a rival's SIM cards; FEMSA is appealing.")

open(p, 'w', encoding='utf-8').write(json.dumps(recs, indent=2, ensure_ascii=True))
print('\n'.join(log))
print(len(log), 'changes')
