"""Record flags, tiers and summary lines brought in line with the checked Details reports of the 20 Nov 2026 run.

Each change follows sponsor-atlas/work/ubatch/CHECKER.md and rests on the checked report in
data/details_runs/2026-11-20/reports/<id>.txt. Grades are recomputed afterwards by tools/clean_data.py.
"""
import json
import sys

p = sys.argv[1]
recs = json.load(open(p, encoding='utf-8'))
d = {r['id']: r for r in recs}
PLACEHOLDER = 'No reason for the flag is recorded.'
log = []


def put(i, **kw):
    r = d[i]
    for k, v in kw.items():
        if v is None:
            if k in r:
                r.pop(k)
                log.append(f'{i}: removed {k}')
        else:
            if r.get(k) != v:
                r[k] = v
                log.append(f'{i}: {k} = {v if isinstance(v, (list, int)) else v[:70]}')
    if r.get('tier_note') == PLACEHOLDER:
        r.pop('tier_note')
        log.append(f'{i}: removed placeholder tier_note')


# Flags added
put('mitsubishi-ichigokan-museum', tier='B', flags=['Arms and defence', 'Fossil fuels'],
    funding='Run by Mitsubishi Estate as a corporate museum; Mitsubishi group companies lead its corporate members, among them MUFG Bank and Mitsubishi Corporation.',
    why_flagged='Its corporate members include the arms maker Mitsubishi Heavy Industries and the oil and gas group ENEOS Holdings (members page, 2026).',
    records_note=None, website='https://mimt.jp/')
put('national-centre-for-the-performing-arts-ncpa', tier='B', flags=['Fossil fuels'],
    funding="Beijing's budget and its own service income: 62.55% of its 1,178.75m yuan income in 2025 came from the city budget (final accounts).",
    why_flagged='Its foundation set up a joint culture fund with the natural gas group ENN under an April 2024 cooperation agreement (Xinhua).',
    tier_note=None, records_note=None, website='https://www.chncpa.org')
put('win-win-memorial', tier='B', flags=['Sanctions'],
    why_flagged='Land donor Ly Yong Phat, who paid the rest of its cost, was sanctioned by the US in September 2024 over forced labour in scam centres.',
    watch='Inaugurated by Hun Sen on 29 December 2018 in Chroy Changvar.')
put('national-museum-of-the-history-of-ukraine-in-the-second-world-war', tier='B', flags=['Fossil fuels'],
    why_flagged='Naftogaz, the oil and gas company, and the fuel station chain WOG were among the donors who paid for the new shield (Forbes Ukraine, 2023).')
put('museum-of-norilsk', flags=['Mining disaster', 'Sanctions'],
    why_flagged="Nornickel's president and biggest shareholder Vladimir Potanin has been under UK sanctions since June 2022 and US sanctions since December 2022.",
    records_note="AMMA's cost is from The Art Newspaper (2021).")
# Flags removed
put('antarctic-biennale', tier_note=None, flags=None,
    why_flagged='Main sponsor Eugene Kaspersky heads Kaspersky Lab, whose US sales were barred in June 2024; neither he nor the firm is on a sanctions list.',
    watch='Kaspersky Lab said it sponsored the voyage, and Eugene Kaspersky sailed with it (Kaspersky blog, 2017).',
    records_note='Main backer named as the Oceanic Project Foundation, chaired by Anna Somers Cocks of The Art Newspaper; its old web address now serves gambling spam.')
put('russia-my-history-vdnkh', tier_note=None, tier='B', flags=None,
    why_flagged='Gazprom Neft, the oil arm of its funder Gazprom, has been under UK and US sanctions since January 2025.')
put('great-northern-arts-festival-inuvik', tier='A', flags=None, tier_note=None)
put('svalbard-museum-longyearbyen', flags=None, tier_note=None,
    why_flagged="The coal company Store Norske is one of the foundation's five founders, who appoint the board; the chair sits for Store Norske (museum, 2025).",
    watch='Store Norske, which closed its last coal mine on 4 May 2026, holds a board seat; the museum keeps 10,000 of its photographs.')
put('festspillene-i-nord-norge-harstad', tier='A', flags=None, tier_note=None,
    funding='A foundation backed by the Ministry of Culture, three northern counties, Harstad Municipality and SpareBank 1 Nord-Norge, with UiT and local firms as partners. FY2023 income NOK 28.2M.',
    watch='An annual festival in Harstad since 1965, held over eight days around the summer solstice.')

# Names to know (tier B, no flag)
put('sarestoniemi-museum-kittila', tier_note=None, tier='B',
    why_flagged="Its 2025 centenary partner Agnico Eagle Finland was fined EUR 130,000 in 2021 over a worker's death at its Kittilä mine (Kaleva).",
    watch='Main partners of the 2025 centenary year: Kittilä Municipality, Agnico Eagle Finland and the art organisation Taideorganisaatio Hiljaisuus.',
    records_note="Figures are in the Finnish Heritage Agency's museum statistics.",
    website='https://www.sarestoniemimuseo.com')
put('vdnkh-exhibition-of-achievements-of-national-economy', tier_note=None, tier='B',
    why_flagged='Companies of Gennady Timchenko, under UK sanctions since February 2022, invested in its 2019 reconstruction (Snob, citing Vedomosti).')
put('victory-museum-central-museum-of-the-great-patriotic-war', tier_note=None, tier='B',
    funding="Federal museum under Russia's Ministry of Culture. Putin honoured its director Alexander Shkolnik in 2021 for patriotic education.",
    why_flagged='Its director Alexander Shkolnik has been under UK and Australian sanctions since 2022.',
    watch='Opened on Poklonnaya Hill on 9 May 1995; the 2022 exhibition Ordinary Nazism drew 150,000 visitors in its first month.')
put('patriot-park', tier_note=None, tier='B',
    why_flagged='Canada put the park on its Russia sanctions list in February 2024 (SOR/2024-32).')
put('deutsches-hygiene-museum', tier_note=None, tier='B',
    why_flagged="Exhibition backer Beisheim Stiftung bears the name of Otto Beisheim, whom Bavaria's Culture Ministry named in 2005 as a former stormtrooper and SS member (JTA).")
put('haus-der-kunst', tier_note=None, tier='B',
    why_flagged="Supporter Beisheim Stiftung bears the name of Otto Beisheim, whom Bavaria's Culture Ministry named in 2005 as a former stormtrooper and SS member (JTA).")

# Record fields the checked reports show to be wrong
NZ = ('Antarctic Heritage Trust (NZ charity CC24071) took NZ$3.43M in the year to June 2025, NZ$1.54M of it government grants; '
      'the Ministry for Culture and Heritage is its core funder.')
put('scotts-discovery-hut-hut-point', funding=NZ, watch='The hut stands 300m from the US McMurdo station.')
put('shackletons-nimrod-hut-cape-royds', funding=NZ)
put('bangabandhu-memorial-museum',
    funding='The Bangabandhu Memorial Trust ran it from 1994; in 2017, 37 banks gave over Tk 136 crore to it and two other bodies. The National Board of Revenue revoked its tax exemption.',
    tier_note=None)
put('crac-valparaiso', website=None)
put('nanjing-museum',
    funding='The Jiangsu provincial government and its culture bodies supervise it (China Daily).',
    watch='In February 2026 a probe into the 1959 donation of 137 paintings by the Pang family found works sold off in the 1990s; the museum apologised and 29 people were implicated.',
    records_note=None, website='https://www.njmuseum.com')
put('alta-museum-world-heritage-rock-art-centre', year_founded=1978)
put('museum-of-the-macedonian-struggle',
    watch='The government counted over 200,000 visitors in its first five years; it shows 109 wax figures and 85 history paintings, now with individual visits as well as guided tours.')
put('kaviar-factory-henningsvaer',
    records_note="KaviarFactory Drift AS files accounts in Norway's register; Venke Hoff chairs its board. On 17 Nov 2026 kaviarfactory.com served casino spam beside the venue's name.")
put('palazzo-delle-esposizioni',
    funding='Owned by Roma Capitale and run under a city service contract by Azienda Speciale Palaexpo, a 1998 municipal body that also runs MACRO and the Museo delle Periferie.')
put('chiang-kai-shek-memorial-hall',
    watch='Built from 31 October 1976 and opened 4 April 1980 with a 6.3 metre bronze statue of Chiang; the changing of the guard draws tourists.')
put('ajtte-jokkmokk',
    funding='Owned by a foundation of the Swedish state, Norrbotten Region, Jokkmokk Municipality and two Sámi organisations.',
    watch="Opened in June 1989 as Sweden's main museum and archive of Sámi culture.", records_note=None)
put('padrao-dos-descobrimentos',
    funding='Managed since 2003 by EGEAC, the Lisbon city company that runs the municipal cultural venues.')
put('museum-of-the-second-world-war',
    watch='Opened 23 March 2017 in Gdańsk; 533,455 visitors by 28 November 2024 (museum).')
put('cuartel-de-la-montana-4f-chavez-mausoleum',
    funding='State-owned, controlled by the Ministry of Defense and the Bolivarian National Militia, based there since 2002. The state organises visits and an honour guard watches the sarcophagus.',
    watch="Built in 1906 in 23 de Enero. Acting president Delcy Rodríguez reaffirmed her loyalty at the tomb on 6 January 2026 after Maduro's capture.")
put('war-remnants-museum',
    funding='A public institution of the Ho Chi Minh City government, which has covered its running costs from its own income since 2014 (Báo Văn Hóa, 2025).')
put('joseph-stalin-museum',
    funding='A Georgian state museum, funded by the Ministry of Culture and Monuments and listed as a heritage monument; restoration tenders run through the State Procurement Agency.',
    watch='The 1957 complex holds about 40,000 items. A room on repressions was added in 2010.')
put('quadriennale-di-roma',
    funding="Fondazione La Quadriennale di Roma is funded by its partners: the Ministry of Culture, Roma Capitale's Department of Culture and the Lazio Region.")

open(p, 'w', encoding='utf-8').write(json.dumps(recs, indent=2, ensure_ascii=True))
print('\n'.join(log))
print(len(log), 'changes')
