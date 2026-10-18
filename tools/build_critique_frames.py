#!/usr/bin/env python3
"""Write data/research_attach/institutional_critiques.json from verified quotations.

Each frame is a museum type (or, for funding, a Clean Funding Grade) with word-for-word quotations from e-flux, L'Internationale Online
(the publishing platform of the museum confederation BAK belongs to) and similar press, each with its author, title, publication, date and
address. The quotes themselves live in the research notes folder as quotes-<type>.json, one file per type, each checked by fetching the page
and finding the string in its text; this script only chooses among them and attaches the display fields.
Usage: python3 tools/build_critique_frames.py <notes folder> && python3 tools/attach_critiques.py && python3 tools/clean_data.py && python3 tools/embed_data.py
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NOTES = Path(sys.argv[1])
LIO = 'L’Internationale Online'


def pick(name, i, publication, date, only=None, context=None, title=None):
    q = json.load(open(NOTES / f'quotes-{name}.json', encoding='utf-8'))[i]
    out = {'text': q['quote'], 'author': q['author'], 'title': title or q['title'], 'publication': publication, 'date': date, 'url': q['url']}
    if only:
        out['only'] = only
    if context:
        out['context'] = context
    return out


FIFTH = 'The Fifth Estate: On Museums, Public Imagination and the Vanishing Space for Collectivity'
frames = [
    {'id': 'history', 'strategy': 'The nation’s story', 'target': 'National, city and war museums, and museums of history',
     'impact': 'Ask whose past the permanent display tells, who paid for the telling, and what the galleries leave out.',
     'applies': {'type': 'history'}, 'quotes': []},
    {'id': 'natural', 'strategy': 'Nature as inventory', 'target': 'Natural history museums',
     'impact': 'Ask how the collection was acquired, whose land the specimens came from, and who pays for the displays.',
     'applies': {'type': 'natural'},
     'quotes': [
         pick('natural', 0, LIO + ', Ecologising Museums', 'June 2016'),
         pick('natural', 2, LIO + ', Ecologising Museums', 'June 2016'),
         pick('natural', 3, LIO + ', Ecologising Museums', 'November 2015', context='On the Natural History Museum, London.'),
     ]},
    {'id': 'colonial', 'strategy': 'The colonial collection', 'target': 'Ethnographic, world-culture and universal museums',
     'impact': 'Ask how the objects arrived, who claims them, and what the museum says about that in its own galleries and accounts.',
     'applies': {'type': 'ethno'},
     'quotes': [
         pick('ethnographic', 0, 'e-flux Criticism', 'June 2018'),
         pick('ethnographic', 1, LIO + ', Decolonising Museums', 'June 2015'),
         pick('ethnographic', 3, LIO + ', Decolonising Museums', 'September 2015', only=r'Tropenmuseum',
              context='On the Dutch state’s cuts to the Tropenmuseum and its colonial collection.'),
     ]},
    {'id': 'patron', 'strategy': 'Freedom on a patron’s terms', 'target': 'Museums and centres of modern and contemporary art',
     'impact': 'Read the board and the donor list against the programme: whose dissent has room here, and whose does not.',
     'applies': {'type': 'contemp'},
     'quotes': [
         pick('contemporary', 0, LIO + ', Situated Organizations', 'December 2025', title=FIFTH),
         pick('contemporary', 4, 'e-flux journal #21', 'December 2010'),
         pick('contemporary', 2, 'e-flux journal #107', 'March 2020', only=r'Whitney|MoMA|Museum of Modern Art'),
     ]},
    {'id': 'pavilion', 'strategy': 'The pavilion and the nation', 'target': 'Biennials, triennials and large periodic exhibitions',
     'impact': 'Read who pays for each national or sponsored presentation, and what the host city is left with.',
     'applies': {'type': 'bien'},
     'quotes': [
         pick('contemporary', 4, 'e-flux journal #21', 'December 2010'),
         pick('contemporary', 5, 'e-flux journal #52', 'February 2014', only=r'Venice|Venezia'),
         pick('contemporary', 6, 'e-flux Criticism', 'June 2016', only=r'Venice|Venezia',
              context='On the Venice Architecture Biennale.'),
         pick('contemporary', 2, 'e-flux journal #107', 'March 2020', only=r'Whitney'),
     ]},
    {'id': 'gift', 'strategy': 'The gift and its givers', 'target': 'Museums whose funders carry a flag',
     'impact': 'Where a flag names an industry, ask what the gift buys the giver, and who sits on the board that accepts it.',
     'applies': {'grade': [4, 5]},
     'quotes': [
         pick('funding', 0, 'e-flux Notes', 'January 2026'),
         pick('funding', 1, LIO + ', Ecologising Museums', 'November 2015'),
         pick('funding', 3, 'e-flux Architecture', 'November 2023'),
     ]},
]
hist = NOTES / 'quotes-history.json'
if hist.exists() and len(sys.argv) > 2:
    sel = json.loads(sys.argv[2])   # [[index, publication, date, only-or-null, context-or-null], ...]
    h = next(f for f in frames if f['id'] == 'history')
    h['quotes'] = [pick('history', i, p, d, only=o, context=c) for i, p, d, o, c in sel]
json.dump({'_about': 'Critical frames on cultural institutions, one per museum type or funding situation. Each frame carries word-for-word quotations with author, title, publication, date and address, written by tools/build_critique_frames.py from quotes checked against the source page. tools/attach_critiques.py puts them on the records they apply to as critiques of kind theory.',
           'frames': frames}, open(ROOT / 'data/research_attach/institutional_critiques.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print({f['id']: len(f['quotes']) for f in frames})
