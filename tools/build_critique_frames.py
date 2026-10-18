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
# Three frames written from single authors rather than from the notes folder; each quotation was fetched and string-matched against its page.
EFLUX50 = 'e-flux.com/journal/50/59974/entering-the-flow-museum-between-archive-and-gesamtkunstwerk/'
GROYS = {'author': 'Boris Groys', 'title': 'Entering the Flow: Museum between Archive and Gesamtkunstwerk', 'publication': 'e-flux journal #50',
         'date': 'December 2013', 'url': 'https://www.' + EFLUX50}
ZIZEK = {'author': 'Slavoj Žižek', 'title': 'Nobody has to be vile', 'publication': 'London Review of Books 28/7', 'date': '6 April 2006',
         'url': 'https://www.lrb.co.uk/the-paper/v28/n07/slavoj-zizek/nobody-has-to-be-vile'}
VAROUFAKIS_TAN = {'author': 'Yanis Varoufakis', 'title': 'Artists should be ‘feared by the powerful’, says former Greek finance minister',
                  'publication': 'The Art Newspaper', 'date': '3 October 2015',
                  'url': 'https://www.theartnewspaper.com/2015/10/03/artists-should-be-feared-by-the-powerful-says-former-greek-finance-minister'}
VAROUFAKIS_EFLUX = {'author': 'Yanis Varoufakis', 'title': '“We Come Bearing Gifts”—iLiana Fokianaki and Yanis Varoufakis on Documenta 14 Athens',
                    'publication': 'art-agenda / e-flux Criticism', 'date': 'June 2017',
                    'url': 'https://www.e-flux.com/criticism/240266/we-come-bearing-gifts-iliana-fokianaki-and-yanis-varoufakis-on-documenta-14-athens'}
frames += [
    {'id': 'archive_and_stage', 'strategy': 'The archive and the stage', 'target': 'Museums of modern and contemporary art, biennials and festivals',
     'impact': 'Read a museum’s event calendar and curatorial turnover against what it actually keeps, conserves and pays for.',
     'applies': {'type': ['contemp', 'bien'], 'size': ['L', 'M']},
     'quotes': [
         dict(GROYS, text='Thus, our art museums became huge garbage cans of history in which things were kept and exhibited that had no use anymore in real life: sacral images of past religions or status objects of past lifestyles.'),
         dict(GROYS, text='A new curator is a new dictator who erases the traces of the previous dictatorship. In this way, contemporary museums continually morph from spaces for permanent collections into stages for temporary curatorial projects—temporary Gesamtkunstwerks.'),
     ]},
    {'id': 'gift_after_taking', 'strategy': 'The gift that follows the taking', 'target': 'Institutions funded by donors whose money carries a flag',
     'impact': 'Where a flag names an industry, ask what the gift was repairing, and for whom.',
     'applies': {'grade': [4, 5]},
     'quotes': [
         dict(ZIZEK, text='Remember Andrew Carnegie, who employed a private army to suppress organised labour in his steelworks and then distributed large parts of his wealth for educational, cultural and humanitarian causes, proving that, although a man of steel, he had a heart of gold? In the same way, today’s liberal communists give away with one hand what they grabbed with the other.'),
         dict(ZIZEK, text='According to liberal communist ethics, the ruthless pursuit of profit is counteracted by charity: charity is part of the game, a humanitarian mask hiding the underlying economic exploitation.'),
     ]},
    {'id': 'art_the_powerful_fear', 'strategy': 'Art the powerful should fear', 'target': 'Biennials, festivals and touring exhibitions, and the cities that host them',
     'impact': 'Read a festival’s balance with its host city, and its critique against its sponsor list.',
     'applies': [{'type': 'bien'}, {'name': 'festival'}, {'city': ['Athens', 'Kassel']}],
     'quotes': [
         dict(VAROUFAKIS_TAN, context='Closing the sixth Moscow Biennale, he began by asking the hall to look at the money in their pockets:',
              text='Take a euro note out and have a look at it. […] Just look at it aesthetically. What do you see? A very boring design.'),
         dict(VAROUFAKIS_TAN, context='The bridges and arches on the notes are ‘figments of some second-rate artist’s imagination’, he said, because the EU’s members could not agree on whose cultural treasures should appear on them. Worse than art created by committee, though, are the attempts of bureaucrats and big businesses to appropriate it:',
              text='Art must not be anodyne, culture cannot be decorative. [Artists] should be feared by the powerful in our society; if you are not, you are not doing your job properly.'),
         dict(VAROUFAKIS_TAN, context='In an aside, he also knocked',
              text='forums in which the stars are the postmodernist curators inviting economists to give a lecture to artists.'),
         dict(VAROUFAKIS_EFLUX, context='In conversation with iLiana Fokianaki on Documenta 14 in Athens.',
              text='Documenta took a great deal more from Athens—from both its private and public sector—than it gave. […] When Documenta comes here and talks about neoliberalism with no mention of Deutsche Bank, Société Générale, the awful Troika process, the Eurogroup, etc., it is choosing to be irrelevant.'),
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
