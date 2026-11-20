"""Record flags, tiers and summary lines brought in line with the checked Details reports of the second part of the
20 Nov 2026 run (the 208 records with two funding points).

Each change follows sponsor-atlas/work/ubatch/CHECKER.md (with the editor's rulings) and
data/details_runs/2026-11-20b/RUN.md, and rests only on the checked report in
data/details_runs/2026-11-20b/reports/<id>.txt: its Red flags headings are the flag bases; WIDER CONTEXT items are
not flags. Only records named in data/details_runs/2026-11-20b/editor_notes.md are touched. A tier-B record carries
its reason in why_flagged; a Red flag that fits no flag category and involves no funder or board figure (an artist
dispute, colonial holdings, a building cost rise) leaves the record at A. Grades are recomputed afterwards by
tools/clean_data.py.

Usage: python3 data/details_runs/2026-11-20b/flags_from_notes.py institutions.json
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



# Flags added (or flags brought in line with the report's Red flags headings)
# Red flags: run by Abu Dhabi's government culture department since the 2018 reopening (Gulf state body)
put('qasr-al-hosn', tier='B', flags=['Gulf state body'],
    funding="Paid for by the Abu Dhabi government: its Department of Culture and Tourism reopened the fort in 2018 and runs the site.",
    why_flagged="Abu Dhabi's government culture department runs it, a Gulf state body.",
    records_note=None)
# Red flags: run by the Sharjah Museums Authority, a government body set up in 2006 (Gulf state body)
put('sharjah-museum-of-islamic-civilization', tier='B', flags=['Gulf state body'],
    funding='The Sharjah government pays for it through the Sharjah Museums Authority, set up in 2006.',
    why_flagged="A Sharjah government body runs it; the ruler's daughter Hoor Al Qasimi has headed that body by Emiri Decree since July 2026.",
    records_note=None)
# Red flags: 2024 protest and loan withdrawals over a cancelled Gaza lecture; 2026 open letter over the departure of its arts director
put('barbican-centre-london', tier='B', flags=['Protest or boycott'],
    why_flagged="Artists withdrew work in 2024 after it dropped a Gaza lecture; in 2026 over 170 cultural figures questioned its arts director's departure.")
# Red flags: founder's Koç Holding fortune, led by oil refining in 2024 (CHECKER.md ruling: Pera Museum, Koç)
put('rahmi-m-koc-museum', tier='B', flags=['Fossil fuels'],
    funding="Run on the Koç family's private money by the Rahmi M. Koç Museology and Cultural Foundation, which bought and restored the buildings.",
    why_flagged="Founder Rahmi Koç's fortune is Koç Holding, whose energy segment, with the refiner Tüpraş, made 41 percent of group operating profit in 2024.",
    records_note=None)
# Red flags: Gulf Labor Coalition artist boycott, still standing in July 2026 (with government ownership and the 2015 HRW labour findings)
put('guggenheim-abu-dhabi', flags=['Gulf state body', 'Forced or exploited labour', 'Protest or boycott'],
    funding="Abu Dhabi's Department of Culture and Tourism develops it with the Guggenheim Foundation, which runs the programme; the Abu Dhabi government owns the collection.",
    why_flagged="Abu Dhabi state ownership; Human Rights Watch documented abuse of Saadiyat migrant workers in 2015; Gulf Labor's artist boycott still stands in 2026.")
# Red flags: 2022 child labour at Hyundai Motor's Alabama suppliers (Hyundai Motor partners the 2026 Korean Pavilion)
put('arko-art-center-seoul', tier='B', flags=['Forced or exploited labour'],
    why_flagged="Hyundai Motor partners the 2026 Korean Pavilion it runs; US labour officials found children working at Hyundai's Alabama suppliers in 2022.")
# Red flags: 2025 arts bodies' protest over the missing public call for the director's post
put('centre-dart-la-panera-lleida', tier='B', flags=['Protest or boycott'], tier_note=None,
    why_flagged="In 2025 Catalan critics', artists' and museum professionals' bodies protested that Lleida fills the director's post without a public call.")
# Red flags: 2024 keffiyeh ban and the firing of three gallery attendants; 2024 protests against the dress code; entered at 9-01 33rd Road
put('noguchi-museum', flags=['Protest or boycott'],
    why_flagged='In 2024 staff petitioned and walked out over a keffiyeh ban; it fired three attendants, and Jhumpa Lahiri turned down its award.',
    highlight='Isamu Noguchi designed and created this museum and sculpture garden in Long Island City, entered at 9-01 33rd Road.')
# Red flags: Gazprom sponsorship, 2022; 2026 sponsorship by sanctioned state bank Sber; EU sanctions on the director, 2026; 2022 boycott by foreign partners; 2026 Accounts Chamber finding
put('state-hermitage-museum-spb', tier='B', flags=['Fossil fuels', 'Sanctions', 'Protest or boycott'],
    funding='Paid for from a separate federal budget line since 1997; Gazprom, Magnit and Sber have sponsored galleries and shows since 2022.',
    why_flagged='Gazprom sponsored a gallery in 2022 and sanctioned state bank Sber a 2026 show; the EU sanctioned director Mikhail Piotrovsky in April 2026.')
# Red flags: owner's gas fortune, current in 2026; owner under UK sanctions since 2022. The Campaigned name campaign targeted V-A-C (WIDER CONTEXT)
put('victoria-gallery-samara', flags=['Fossil fuels', 'Sanctions'],
    why_flagged="Owner Leonid Mikhelson's fortune comes from the gas company Novatek and from Sibur; the UK has sanctioned him since April 2022.")
# Red flags: Gulf state body in charge since 2017; FUNDING: RCU aims for 40 per cent private money
put('alula-arts-cultural-oasis', tier='B', flags=['Gulf state body'],
    funding='Paid for by the Saudi state through the Royal Commission for AlUla, which aims to raise 40 per cent of its funding from private investors.',
    why_flagged='The Royal Commission for AlUla, a Saudi government body chaired by Crown Prince Mohammed bin Salman since 2017, pays for and directs it.')
# Red flags: Galp Energia 2021 to 2024; REN Portgás 2021 to 2025; Tabaqueira tobacco money 2021 and 2022 (and a July 2025 conference)
put('serralves-foundation-porto', flags=['Fossil fuels', 'Tobacco'],
    funding='Co-funded by the Portuguese state: the Ministry of Culture gave 36 per cent of its €17.8M income in 2025, with patronage and sales making up most of the rest.',
    why_flagged="Gas distributor REN Portgás has been a Patron Founder since 2021 and Galp was one to 2024; Philip Morris's Tabaqueira paid in 2021 and 2022.",
    watch='Galp left the Patron Founders list in 2025; REN Portgás stayed on it.',
    records_note='Serralves posts yearly reports with audited accounts from 1989 to 2025 and names its founders.')
# Red flags: Gulf state body: Qatari government foundation set up in 2010 (Amiri Decision No. 38 of 2010)
put('katara-cultural-village', tier='B', flags=['Gulf state body'],
    funding='A government-funded complex run by the Cultural Village Foundation, created by Amiri Decision No. 38 of 2010; private partners build its commercial projects.',
    why_flagged="A Qatari government foundation created by decree of the Emir runs it.",
    records_note=None)
# Red flags: Gulf state body: owned by Qatar Foundation and, since 2025, the Qatar Investment Authority
put('msheireb-museums', tier='B', flags=['Gulf state body'],
    funding='Msheireb Properties owns the museums as part of its 5.5 billion dollar Msheireb Downtown Doha scheme; Qatar Foundation and the Qatar Investment Authority own the developer.',
    why_flagged="Its owner is held by Qatar Foundation and Qatar's sovereign wealth fund.",
    records_note=None)
# Red flags: 2022 removal of director Jarosław Suchan
put('muzeum-sztuki-lodz', tier='B', flags=['State censorship or punishment'],
    funding='A cultural institution of the Łódź Voivodeship self-government, co-financed by the Ministry of Culture and National Heritage.',
    why_flagged='At the end of April 2022 deputy culture minister Jarosław Sellin dismissed director Jarosław Suchan without explanation.',
    watch=None)
# Red flags: 2022 abolition of the civic museums' director post (open letter); 2023 strikes by contract attendants; 2026 union protest
put('museo-revoltella', tier='B', flags=['Protest or boycott'],
    funding='Civic museum operated by the Comune di Trieste, founded on the bequest of Baron Pasquale Revoltella, who left his palace, art collection and a substantial income to the city.',
    why_flagged='A 2022 open letter with over 200 signatures asked Trieste to restore a museum director; contract attendants struck in 2023 and protested in 2026.')
# Red flags: 2025 protest over felling 750 holm oaks in the park; interim director Antonio Tarasco since June 2026
put('reggia-di-caserta', tier='B', flags=['Protest or boycott'],
    funding='A Culture Ministry museum that earns most of its €8.49M income (2024) from tickets, concessions and rents.',
    why_flagged="In 2025 local committees and environmental groups protested its felling of the 750 holm oaks on the park's central avenue.",
    watch="Antonio Tarasco, the Culture Ministry's director general for archives, has been interim director since June 2026.",
    records_note='Its 2024 accounts are in the Amministrazione trasparente section of its site.')
# Red flags: 2025 sponsorship by Japan Tobacco; citizen petitions of 2021 and 2022 over executive producer Yasuharu Ishikawa
put('okayama-art-summit-okayama', tier='B', flags=['Tobacco', 'Protest or boycott'],
    funding='Okayama City, Okayama Prefecture and the Ishikawa Foundation lead the executive committee; 2025 sponsors included Ishikawa Holdings, Chugin Financial Group, JR West and Japan Tobacco.',
    why_flagged='Japan Tobacco sponsored the 2025 edition; citizens petitioned in 2021 and 2022 to replace executive producer Yasuharu Ishikawa over harassment accusations.',
    watch='Philippe Parreno directed the 2025 edition, with Taro Nasu as executive director and Ishikawa as executive producer.')
# Red flags: 2024 support from defence contractor Mitsubishi Heavy Industries; FUNDING: 2024 accounts
put('new-national-theatre-tokyo-nntt', tier='B', flags=['Arms and defence'], tier_note=None,
    funding='Mainly state money: government funds placed in trust gave 4.27 billion of its 7.71 billion yen income in 2024, with tickets and corporate sponsors.',
    why_flagged='Arms maker Mitsubishi Heavy Industries is one of its 14 top tier corporate guarantors; an MHI unit co-sponsored a 2024 children\'s ballet.')
# Red flags: INAH researchers' 2026 complaint over the FIFA gala dinner in the castle (a staff objection)
put('museo-nacional-de-historia-castillo-de-chapultepec', tier='B', flags=['Protest or boycott'], tier_note=None,
    funding='Federal: INAH runs it on the government budget, with an INAH patronato, a friends\' association and a Bank of America restoration gift.',
    why_flagged='In 2026 INAH researchers filed a complaint of misuse after FIFA held a private World Cup gala dinner in the castle.',
    records_note=None)
# Red flags: Gulf state body: Royal Court Affairs board, 2023 (Royal Decree 15/2023)
put('oman-across-ages-museum', tier='B', flags=['Gulf state body'],
    funding='Set up by Royal Decree 15/2023 as a public body under Royal Court Affairs, which oversaw its building and passed it the museum\'s allocations and staff.',
    why_flagged="A board chaired by the Secretary General of Royal Court Affairs runs it.",
    watch='Opened in Manah on 13 March 2023 by Sultan Haitham, on a 300,000 square metre site; Sultan Qaboos laid its foundation stone in 2015.',
    records_note=None)
# Red flags: Gulf state body: royal decree and state leadership, 2010 (Royal Decree 105/2010)
put('royal-opera-house-muscat', tier='B', flags=['Gulf state body'],
    funding="A public body set up by Royal Decree 105/2010 under the Sultan's patronage, with financial and administrative independence.",
    why_flagged="Royal court officials sit on its board, under a Higher Committee led by the Deputy Prime Minister for the Council of Ministers.",
    watch='A 1,100-seat opera house designed by WATG, ordered by Sultan Qaboos in 2001 and opened in October 2011 with Puccini\'s Turandot.',
    records_note=None)
# Red flags: 2025 Marisa Merz show cancelled over the documenta code of conduct: the lender withdrew (a boycott aimed at the institution, not state censorship)
put('fridericianum-kassel', flags=['Protest or boycott'],
    why_flagged='In 2025 the Fondazione Merz withdrew a planned Marisa Merz show, objecting to the code of conduct its operator adopted after documenta fifteen.',
    website='https://fridericianum.org/')
# Red flags: 2024 money-laundering plea by TD Bank, the fellowship's sponsor; 2024 protests over closing the Yarmouth branch (petition and two protests)
put('art-gallery-of-nova-scotia', tier='B', flags=['Protest or boycott'],
    why_flagged='Fellowship sponsor TD Bank pleaded guilty to money laundering conspiracy in 2024; closing its Yarmouth branch that year drew two protests and a petition.')
# Red flags: 2026 bp sponsorship of the "Geyzer" exhibition; Trend named Rena Mammadova director in October 2026
put('baku-museum-of-modern-art-baku', tier='B', flags=['Fossil fuels'],
    why_flagged='bp sponsored the 2025 to 2026 festival whose exhibition Geyzer was held at the museum.',
    watch='The news agency Trend named Rena Mammadova as director in October 2026.')
# Red flags: 2026 strike over cuts to contracted mediators' hours (a staff strike at the museum); Website: lacasadelaarquitectura.es
put('casa-de-la-arquitectura-madrid', flags=['Protest or boycott'],
    why_flagged="Contracted mediators and information staff struck from 5 March 2026 over cut working hours, closing the museum for eight days.",
    website='https://lacasadelaarquitectura.es')
# Red flags: 2024 refusals of DAAD fellowships over the president's Nancy Fraser decision; the Kreuzberg gallery closed on 30 September 2026
put('daadgalerie-berlin', tier='B', flags=['Protest or boycott'], tier_note=None,
    why_flagged="In 2024 Jonas Staal and Joanna Walsh refused DAAD fellowships in open letters over its president's withdrawal of Nancy Fraser's Cologne professorship.",
    highlight="Works by current and former fellows of the Berliner Künstlerprogramm were shown at the daadgalerie in Kreuzberg until 30 September 2026; its season now runs in the Volksbühne's Grüner Salon.")
# Red flags: 2025 Chefket concert cancelled after the federal culture minister's call (the funder); FUNDING: the imprint names only the BKM
put('haus-der-kulturen-der-welt-hkw', tier='B', flags=['State censorship or punishment'], tier_note=None,
    funding='Institutionally funded by the Federal Government Commissioner for Culture and the Media (BKM).',
    why_flagged="In September 2025 a Chefket concert at HKW was cancelled after the federal culture minister, Wolfram Weimer, who chairs its parent's supervisory board, objected.")

# Flags or names to know removed (basis moved to WIDER CONTEXT or cut, or not a flag category)
# No Red flags: the 2015 divestment call and the 2022 share sales are WIDER CONTEXT; FUNDING verdict gives £39.9bn
put('wellcome-collection', tier='A', why_flagged=None, watch=None, tier_note=None,
    funding='Part of Wellcome, a charitable foundation; the Wellcome Trust endowment that pays for it was worth about £39.9bn in 2025.',
    website='https://wellcomecollection.org')
# Red flags: Black and Dubin (Epstein), 2024 Gaza sit-in, 2024 climate protest; no campaign over a name (Strike MoMA 2021 is WIDER CONTEXT)
put('moma-the-museum-of-modern-art', flags=['Epstein-linked', 'Protest or boycott'],
    funding='Private: in the year to June 2025, 41% of its $362.0 million revenue came from sales of assets and 27% from contributions (Form 990).',
    why_flagged='Trustees Leon Black, who paid Jeffrey Epstein at least $158 million, and Glenn Dubin; 2024 Gaza and climate protests targeted its board.',
    watch='Black and Dubin keep their trustee seats in 2026, after Senator Ron Wyden questioned Black\'s Epstein payments.')
# Red flags: 2023 ministry audit finding 16 irregular practices; Hyundai's sponsorship moved to WIDER CONTEXT; director Ki Hey-kyung from 13 November 2026
put('national-museum-of-modern-and-contemporary-art-mmca', tier='B', flags=None,
    why_flagged='A 2023 Ministry of Culture audit found 16 illegal or inappropriate practices under former director Youn Bum-mo.',
    watch='Culture Minister Chae Hwi-young named Ki Hey-kyung director on 13 November 2026.')
# Red flags: only the 2023 reuse of a Xaviera Simmons structure, a dispute with an artist that involves no funder; the 2023 staff letter and strike are WIDER CONTEXT
put('queens-museum', tier='A', flags=None,
    watch='In 2017 the museum cancelled, then reinstated, an event organised by Israel\'s UN Mission.',
    finances_note='FY2024-25 income USD 7.79M, of which USD 7.45M came as contributions and grants (Form 990).')
# No Red flag left: Kryvorizhstal, the 2019 to 2020 guides dispute and the Trump Foundation payment are WIDER CONTEXT
put('pinchukartcentre', tier='A', why_flagged=None,
    watch="Pinchuk's fortune grew while his father-in-law Leonid Kuchma was president; the 2004 Kryvorizhstal sale to him was reversed in 2005.")
# No Red flag left: the 2002 overrun and builder Mansudae's 2016 to 2017 sanctions are WIDER CONTEXT
put('heroes-acre-windhoek', tier='A', why_flagged=None,
    watch="The builder, North Korea's Mansudae, came under US sanctions in December 2016, years after it finished the site as a contractor.")
# Red flags: only the 2023 to 2024 collection-ownership dispute, which involves no funder; the 2014 Bozzi case is WIDER CONTEXT; the BDO-audited annual report is an outside source
put('national-art-gallery-of-namibia-windhoek', tier='A', tier_note=None, why_flagged=None, watch=None)
# No Red flags: RGE's gas business and Asian Agri's 2012 tax ruling are WIDER CONTEXT; Website: tanotoartfoundation.org
put('tanoto-art-foundation-singapore', tier='A', why_flagged=None,
    watch="Trustee Anderson Tanoto runs the family's RGE group, whose energy arm Pacific Energy explores for gas in Canada.",
    website='https://www.tanotoartfoundation.org')
# No Red flags: the 2022 Getty grant is a note (Getty ruling); the Bloomberg campaign concerned London theatres; board vice president Eduardo Hochschild Beeck
put('mac-lima-lima', tier='A', why_flagged=None,
    funding='A private non-profit on land from the Municipality of Barranco, run on its own income, friends and donors; Fundación Telefónica Movistar and a one-off 2022 Getty grant paid for shows.',
    watch='Meg de Romaña chairs its board for 2022 to 2025, with Eduardo Hochschild Beeck, of the Hochschild Mining family, as vice president.')
# Red flags: 2022 artists' appeal against the Fredriksen agreement (Protest); no campaign over a funder's name
put('nasjonalmuseet-national-museum-of-norway', flags=['Protest or boycott'],
    why_flagged='In June 2022 artists showing at the museum called on it to end its agreement with the Fredriksen Family Art Company.')
# No Red flags: GAESA and Habaguanex are on the US Cuba Restricted List, but museum fees stayed with the Historian's Office (WIDER CONTEXT); why_flagged held the opening date
put('museo-de-arte-colonial', tier='A', why_flagged=None)
# Red flags: asset freezes (2019, 2020), Luanda court ruling (2020), US corruption designation (2021), London freezing order (2023); no flag category. Sonangol (2016 to 2017) is WIDER CONTEXT; old domain serves spam
put('fundação-sindika-dokolo-luanda', tier='B', flags=None,
    why_flagged='Its money came from Sindika Dokolo and Isabel dos Santos, whose assets courts froze in Angola (2019), Portugal (2020) and London (2023).',
    website=None)
# No Red flags: the Heumarkt dispute and the WKStA investigation of Wertinvest's owner are WIDER CONTEXT
put('margarete-schutte-lihotzky-zentrum', tier='A', why_flagged=None)
# No Red flags: the ACC charge sheet against Abul Khair Litu has not ended in a conviction (WIDER CONTEXT)
put('bengal-foundation', tier='A', why_flagged=None)

# Names to know (tier B, no flag)
# Red flags: 2024 Bank of England fine on sponsor HSBC; FUNDING: Emaar Entertainment runs it; Lara Ewing head for 2026 to 2027 (Arab News)
put('dubai-opera', tier='B',
    funding='Built by the listed developer Emaar for 1.2 billion dirhams and run by Emaar Entertainment; HSBC and American Express are official partners.',
    why_flagged='Sponsor HSBC: in January 2024 the Bank of England fined two HSBC banks £57.4 million over depositor protection failures.',
    watch='A 2,000-seat venue in the Opera District of Downtown Dubai; Lara Ewing heads it for the 2026 to 2027 season.',
    records_note=None)
# Red flags: 2026 audit finding against chairman Baek Seung-joo; FUNDING: state and local subsidy allowed, minister approves budget and receives audited accounts
put('the-war-memorial-of-korea', tier='B',
    funding='Run by the Korea War Memorial Organization under its own Act; the state and local governments may subsidise it, and the Defense Minister approves its budget.',
    why_flagged='In January 2026 the Board of Audit found chairman Baek Seung-joo misused his post, including 25 private trips in his official car.',
    records_note='The Defense Minister receives its audited accounts.')
# Red flags: 2022 US criminal plea by Stellantis's FCA US over diesel emissions; FUNDING: foundation, Stellantis, Lingotto IM
put('pinacoteca-agnelli', tier='B',
    funding='Run by an Agnelli family foundation, with Stellantis as main partner and the Exor-owned Lingotto Investment Management as official sponsor since 2024.',
    why_flagged='Main partner Stellantis: its unit FCA US pleaded guilty in 2022 to a US diesel emissions fraud conspiracy and was fined $96.1 million.')
# Red flags: Auditor-General's audit of the parent body, National Museums of Kenya, December 2022
put('nairobi-national-museum', tier='B',
    why_flagged='In December 2022 the Auditor-General reported a Sh434.66 million deficit and stalled works at its parent body, National Museums of Kenya.')
# Red flags: 2025 regulatory fines on China Minsheng Bank
put('minsheng-art-museum', tier='B', tier_note=None,
    funding='China Minsheng Bank set up the museum in 2008 within its corporate responsibility platform and pays for it; the Jing\'an district government paid for archive books.',
    why_flagged='Its founder and funder China Minsheng Bank was fined 58.65 million yuan by the national financial regulator in October 2025.',
    records_note=None)

# Record fields the checked reports show to be wrong, and summary lines with no reason or a "not found" line
# FUNDING: "a legally independent public body established by Emiri Decree"; the 2011 removal and dismissal are WIDER CONTEXT
put('sharjah-art-foundation-sharjah',
    funding='A public body set up by Emiri Decree in 2009, paid for by the Sharjah government, nonprofit grants, corporate sponsors and patrons.',
    why_flagged="Sharjah government money; Hoor Al Qasimi, the ruler's daughter, founded and runs it.",
    watch=None)
# Red flags: 2025 operating grant from the Sid W. Richardson Foundation, an oil fortune; 2025 police seizure of Sally Mann photographs
put('modern-art-museum-of-fort-worth-fort-worth', tier='B',
    why_flagged='The oil fortune Sid W. Richardson Foundation gave $750,000 in 2025; police of Fort Worth, a funder, seized Sally Mann photographs from a show.')
# No Red flags (the conversion is WIDER CONTEXT); FUNDING verdict: owned by the General Directorate of Foundations; Website: none
put('chora-museum-kariye', tier='A', tier_note=None, website=None, records_note=None,
    funding="Turkish state property: the culture ministry's foundations directorate owns it, and the state religious affairs body runs it as a mosque.")
# Red flags: 2024 protest by artn't; the Team page names six donors (FUNDING)
put('bangkok-kunsthalle',
    funding="Founded by Marisa Chearavanont through Khao Yai Art; six private donors are named on its Team page, without amounts.",
    why_flagged="In 2024 two artn't performers protested inside Korakrit Arunanondchai's show, calling for scrutiny of where its art money comes from.",
    watch="Founder Marisa Chearavanont is married to Soopakij Chearavanont, chairman of CP Group, whose CP Foods faced slavery claims in its prawn feed chain in 2014.")
# Red flags: 2022 child labour at Hyundai Motor's Alabama suppliers (flag kept; stale tier_note)
put('nam-june-paik-art-center-yongin', tier_note=None)
# Red flags: Sanctions since 2014 on the Donetsk People's Republic, which claims the museum
put('kuindzhi-art-museum',
    why_flagged="Claimed since 2022 by the culture ministry of the Donetsk People's Republic, on US, EU and UK sanctions lists since 2014.",
    records_note=None)
# No text source names Deutsche Bank (logo file name only); FUNDING: Nigerian Breweries, LagosPhoto's foundation and corporate sponsors
put('african-artists-foundation-lagos', why_flagged=None, watch=None,
    funding='Nigerian Breweries sponsors its National Art Competition; LagosPhoto names the Open Society Foundations, the Ford Foundation and Tecno Mobile as principal sponsors.')
# Red flags: US sanctions on the state and army that own the studio (from 2016)
put('april-25-film-studio',
    why_flagged="It belongs to the Korean People's Army, on the US sanctions list since June 2017, under a state the US has blocked since 2016.")
# Red flags: US sanctions on the party, state and army that use the house (from 2016)
put('april-25-house-of-culture',
    why_flagged="The North Korean government and Workers' Party, blocked by US order since 2016, hold congresses here; the sanctioned army keeps its cultural office here.")
# Red flags: US sanctions on the North Korean government and Workers' Party (2016)
put('foreign-languages-publishing-house',
    why_flagged="Run under the Workers' Party of Korea, whose property the US has blocked since March 2016 (Executive Order 13722).")
# Red flags: founder's husband's oil and gas fortune, reported in 2016 and 2025; the separate gallery closed in October 2026
put('ruarts-foundation-moscow',
    why_flagged="Founder Marianna Sardarova is married to Rashid Sardarov, whose South Ural Industrial Company extracts and processes oil and gas (Transparency International Russia, 2025).",
    watch='The separate Ruarts gallery held its last show in October 2026; the team now works only through the foundation.')
# Red flags: 2023 protest over the Cecilia Orta Allende gallery; FUNDING: fiscal 2025 Form 990
put('museo-de-arte-de-puerto-rico',
    funding='Private nonprofit: half of its $7.31M revenue in fiscal 2025 came from contributions and grants, with federal IMLS money and earned income.',
    why_flagged="Afro Puerto Rican activists picketed it in November 2023 after it took Cecilia Orta Allende's name off a gallery.")
# No Red flag (2019 cases are WIDER CONTEXT); Website: https://artmuseum.kg
put('gapar-aitiev-kyrgyz-national-museum-of-fine-arts-bishkek', website='https://artmuseum.kg', records_note=None)
# Red flags: 2012 US sanctions listing of the owning ministry
put('tehran-museum-of-contemporary-art-tmoca',
    why_flagged="Its owner, Iran's Ministry of Culture and Islamic Guidance, has been on the US Specially Designated Nationals list since November 2012.")
# Red flags: 2025 Extinction Rebellion occupation in Turin; 2026 privacy fines against the owner (name to know)
put('gallerie-d-italia',
    why_flagged="Extinction Rebellion occupied its Turin site in 2025 over owner Intesa Sanpaolo's fossil lending; Italy's privacy authority fined Intesa in 2026.")
# No current flag (all disputes before 2021); FUNDING: a Tel Aviv-Yafo municipal corporation since 24 March 2022
put('habima-theatre',
    funding='A municipal corporation of Tel Aviv-Yafo since 24 March 2022, with Culture Ministry funding; the city and the ministry saved it from a deficit of over NIS 100 million.',
    watch="Israel's national theatre, in Tel Aviv. It performed in the Kiryat Arba settlement on 10 November 2016, to Culture Minister Miri Regev's praise.",
    records_note=None)
# No current Red flag (the 2014 Fatmi case is WIDER CONTEXT); director Nadia Sabri since October 2025
put('mus-e-mohammed-vi-d-art-moderne-et-contemporain-mmvi-rabat', tier='A',
    watch="Morocco's first national museum of modern and contemporary art, opened by the king in October 2014; Nadia Sabri has directed it since October 2025.",
    website='https://fnm.ma/museums/31')
# No Red flags (Latchford is WIDER CONTEXT); FUNDING: Ministry of Culture and Fine Arts with French aid
put('national-museum-of-cambodia',
    funding='Run under the Ministry of Culture and Fine Arts, with foreign aid: France is paying 900,000 euros for a feasibility study from 2024 to 2026.',
    records_note=None)
# No Red flags (2013 and 2019 cases are WIDER CONTEXT); website field held an exhibition page
put('ludwig-museum-budapest-budapest', website='https://www.ludwigmuseum.hu')
# Red flags: 2024 protest by the jailed artist Luis Manuel Otero Alcántara aimed at the 15th Biennial
put('centro-de-arte-contemporaneo-wifredo-lam',
    why_flagged='In November 2024 the jailed artist Luis Manuel Otero Alcántara invited visitors to its 15th Biennial to visit him in prison, as a protest work.')
# Red flags: 2024 removal of Orlando Mora's short; 2023 exclusion of La Habana de Fito and Llamadas desde Moscú
put('festival-internacional-del-nuevo-cine-latinoamericano-de-la-habana',
    why_flagged="It dropped two documentaries in 2023 and Orlando Mora's short in 2024; the Asamblea de Cineastas Cubanos objected both times.")
# No red flag remains (the May 2021 artists' letter is WIDER CONTEXT)
put('museo-nacional-de-bellas-artes-de-la-habana-havana')
# FUNDING: endowed by the Folgers' bequest, administered by the Trustees of Amherst College
put('folger-shakespeare-library',
    funding="Endowed by Henry Clay and Emily Folger's bequest, which Amherst College's trustees administer; endowment returns pay most of its costs, with private gifts on top.",
    records_note='Its annual reports carry financial statements; its tax filings fall under the Trustees of Amherst College.')
# Red flags: Benin holdings with no return (fits no flag category, involves no funder); FUNDING: a state museum of Bavaria
put('museum-funf-kontinente',
    funding="A state museum of the Free State of Bavaria under its Ministry of Science and Arts, with a friends' association and the Preetorius-Stiftung.",
    records_note=None)
# FUNDING: a directorate of the Ministry of Culture and Tourism; phases two and three (Classical building 2021, Ancient Orient 6 July 2026); Website: muze.gov.tr
put('istanbul-archaeology-museums',
    funding='A state museum: a directorate of the Ministry of Culture and Tourism runs it, and admission fees bring in income.',
    watch='Restored in phases from 2011: the main building reopened in 2019, the Classical building in 2021 and the Ancient Orient museum in July 2026.',
    records_note=None, website='https://muze.gov.tr/muze-detay?SectionId=IAR01&DistId=IAR')
# OVERVIEW: the festival's About page says Munuwa founded it in 2021
put('dar-foto-festival',
    watch='Founded in 2021, the festival says; the 2025 edition showed 15 artists from Congo, Sudan, Kenya and Tanzania in Dar es Salaam and Zanzibar.')
# FUNDING: built and run by the Ministry of Culture and Tourism through the Gaziantep museum directorate; Website: muze.gov.tr
put('zeugma-mosaic-museum',
    funding='A state museum built by the Ministry of Culture and Tourism and run through its Gaziantep museum directorate.',
    records_note=None, website='https://muze.gov.tr/muze-detay?SectionId=GZN01&DistId=GZN')
# Website: https://cabildoccr.gov.py
put('centro-cultural-de-la-republica-el-cabildo', website='https://cabildoccr.gov.py')
# Red flags: US sanctions on the North Korean government, 2016; FUNDING: rebuilt in 2013 on Kim Jong Un's initiative (KCNA); the move date is disputed (1963 or 1974)
put('victorious-fatherland-liberation-war-museum',
    funding="State-funded: KCNA says the party and state rebuilt it in 2013 on Kim Jong Un's initiative. It shows the captured USS Pueblo.",
    why_flagged='The North Korean government, which pays for it, has been blocked under US Executive Order 13722 since March 2016.')
# Gallery Climate Coalition membership is not confirmed by the report
put('busan-museum-of-contemporary-art-busan',
    affiliations_note="The city's second municipal art museum after Busan Museum of Art, and a venue of the 2026 Busan Biennale.")
# Website: factoryartscentre.com serves a football-streaming spam page
put('the-factory-contemporary-arts-centre-ho-chi-minh-city',
    records_note='Its domain factoryartscentre.com served an unrelated football streaming page on 20 November 2026.')
# OVERVIEW: François Gianadda president of the board (commercial register, 19 November 2025); FUNDING: founder's money, earned income, friends and sponsors
put('fondation-pierre-gianadda',
    funding='Built on Léonard Gianadda\'s money and run on admissions, its shop and restaurant, friends\' fees and sponsors such as UBS and Banque Raiffeisen.',
    watch='Léonard Gianadda died on 3 December 2023; in November 2025 the commercial register listed François Gianadda as board president.',
    records_note=None)
# OVERVIEW: Valentín Roma directed it from 2016 to May 2026, then the MACBA
put('la-virreina-barcelona',
    watch='Public visual culture centre in an 18th-century Baroque palace on La Rambla. Valentín Roma, director from 2016, left in May 2026 to run the MACBA.')
# FUNDING: Madrid Destino's 2025 budget plans a City Council operating subsidy of 98,992,097 euros
put('teatro-espanol',
    funding='Owned by Madrid City Council and run by its company Madrid Destino, whose 2025 budget plans a council operating subsidy of about €99M.',
    records_note=None)
# FUNDING: City of Zurich 2026 budget; the Benin Red flag fits no flag category and involves no funder
put('museum-rietberg',
    funding='A City of Zurich museum: the 2026 city budget sets its spending at 18.7 million francs, of which the city carries a net 14.1 million.',
    records_note=None)
# FUNDING: NT$681,048,554 from the treasury of NT$776,752,075 in 2025, NT$74,994,150 in donations; Website: https://www.ntmofa.gov.tw
put('national-taiwan-museum-of-fine-arts-taichung',
    finances_note='FY2025 income NT$776.8M: NT$681.0M (87.7 percent) from the treasury and NT$75.0M in donations and gifts (audited final accounts 2025).',
    website='https://www.ntmofa.gov.tw')
# FUNDING: the public procurement register lists it as a state institution; "under the president's office" is not confirmed
put('national-museum-of-tajikistan',
    records_note='Registered as a state institution with the public procurement system.')
# OVERVIEW: at the Rond-point Place ONU, Dakar (culture ministry page); founder Boubacar Koné has since died
put('musee-boribana',
    watch='Dakar museum of contemporary African art at the Rond-point Place ONU, with artist studios and a residency; its co-founder Boubacar Koné has since died.',
    records_note=None)
# FUNDING: China paid more than 30 million euros (AFP); director Abdou Simbandy Diatta since 1 July 2026
put('musée-des-civilisations-noires-dakar',
    funding='A Senegalese national museum in a building China paid for, with more than 30 million euros by AFP\'s count; its own revenue was CFA 353.9 million in 2025.',
    watch='Abdou Simbandy Diatta, formerly Director General of Culture, has directed it since 1 July 2026.',
    records_note=None)
# FUNDING: the institute's 2025 income was 751,157 euros
put('kapelica-gallery-kersnikova-institute-ljubljana',
    funding="Run by the Kersnikova Institute, whose 2025 income was €751,157, mostly EU funds, with grants from Slovenia's Ministry of Culture and the City of Ljubljana.")
# FUNDING: 2024 subsidies of PLN 4,996,626 from the city; Lisowski chosen director in February 2026
put('wroc-aw-contemporary-museum',
    funding='A municipal cultural institution of the City of Wrocław, which gave it PLN 5.0M in subsidies in 2024; the Culture Ministry co-finances acquisitions.',
    watch='Museum at pl. Strzegomski 2. Piotr Lisowski, acting director from January 2020, was chosen director by a city panel in February 2026.',
    records_note=None)
# FUNDING: Tokyu Corporation gave two donations of 90,000,000 yen in FY2025; business reports and accounts filed with the Cabinet Office
put('gotoh-museum',
    funding='Tokyu Corporation pays for almost all of it: two donations of 90 million yen each in FY2025, with Tokyu Group sponsorship of exhibitions.',
    records_note='It posts its business plans, reports and accounts, which it files with the Cabinet Office.')
# FUNDING: the foundation was set up with the personal assets of Suzuki Tsuneshi (museum website)
put('pola-museum-of-art-hakone',
    funding='Pola Art Foundation, set up in May 1996 with the personal assets of Tsuneshi Suzuki of the Pola founding family; a public-interest foundation since July 2010.')
# FUNDING: operator the Tokyo Metropolitan Foundation for History and Culture, chosen again in September 2026 for 2027 to 2037
put('tokyo-metropolitan-art-museum',
    funding='Run for the Tokyo Metropolitan Government by its Tokyo Metropolitan Foundation for History and Culture, chosen again in September 2026 for 2027 to 2037.',
    records_note=None)
# Red flags: 2025 protest and lawsuit against Fabián Cháirez's exhibition; why_flagged repeated the funding line
put('museo-de-la-ciudad-de-méxico-mexico-city', tier_note=None,
    why_flagged="Seven people protested outside its 2025 Fabián Cháirez show, and religious groups won a court order that made it remove the exhibition.")
# Website: the state press release returns HTTP 500
put('museo-de-los-pintores-oaxaqueños-oaxaca', website=None)
# OVERVIEW: the Juan Gabriel show opened to the public hours later; Henaro cited an administrative matter
put('museo-universitario-del-chopo-mexico-city',
    watch='Sol Henaro has directed it since 2024. Its Juan Gabriel show, postponed on 28 May 2026, opened hours later; Henaro cited an administrative matter.')
# zanabazarmuseum.mn returns 404; records_note held a not-found line
put('zanabazar-museum-of-fine-art-ulaanbaatar', records_note=None)
# OVERVIEW: the cooperative's own site and MUAC give 2011
put('crater-invertido-mexico-city', year_founded=2011)
# OVERVIEW: about thirty artists a year, about half an hour's drive from Marrakech (Arterritory)
put('montresso-art-foundation-jardin-rouge-marrakech',
    watch="Residency among olive groves about half an hour's drive from Marrakech, hosting about thirty artists a year (Arterritory, 2020); visits by appointment.")
# Red flags: US sanctions on the North Korean government, 2016; website (kcnawatch.org) is not the museum's
put('sinchon-museum-of-american-war-atrocities-sinchon', website=None,
    why_flagged='The North Korean state, which built and pays for it, has been blocked under US Executive Order 13722 since March 2016.')
# FUNDING: Sámi Parliament direct grant; county and Arts Council funders appear only as logos; director post advertised in February 2026
put('s-mi-center-for-contemporary-art-s-mi-d-iddaguovdd-karasjok',
    funding='2025 revenue NOK 7.9M; Sámi Parliament direct grant NOK 6.09M (2025).',
    watch='Sámi contemporary art centre, founded 1986, a foundation since 2013. The board advertised the director post again in February 2026.',
    records_note="Audited accounts for 2023 to 2025 are in Norway's accounts register; the site lists the full board.")
# OVERVIEW: KEBAL main show 4 to 28 October 2026, programmes to 24 November; FUNDING: partner names came from logos only
put('jakarta-biennale',
    funding='Run since 2024 by Majelis Jakarta, which the Jakarta Arts Council set up; the Creative Economy Ministry offered its support in 2026.',
    watch="Founded in 1974. KEBAL, the 2026 edition, showed at Taman Ismail Marzuki from 4 to 28 October, with programmes to 24 November.")
# Red flags: 2024 cancellation of Yos Suprapto's exhibition (the ministry's own gallery); closed since 12 October 2026 for revitalisation
put('galeri-nasional-indonesia',
    why_flagged='The Culture Ministry\'s gallery cancelled Yos Suprapto\'s show ten minutes before its December 2024 opening, after he refused to remove paintings of Joko Widodo.',
    watch='The whole site closed on 12 October 2026 for a revitalisation, with no reopening date.')
# No Red flags; tier_note out of date: oddweb.org and photography-now.com are outside sources
put('ruang-mes-56-yogyakarta', tier='A', tier_note=None)
# FUNDING: Ministry of Culture museum; state money for the 2009 to 2016 renovation, PNRR money for new lighting
put('museo-archeologico-nazionale-di-reggio-calabria-marrc',
    funding='A Ministry of Culture museum; the state paid for its 2009 to 2016 renovation, and EU recovery funds paid for new lighting in 2024 and 2025.',
    records_note=None)
# FUNDING: one of the ministry's autonomous museums; Volotea paid 50,000 euros for the Green Bike Area
put('museo-archeologico-nazionale-di-napoli',
    funding="One of the Ministry of Culture's autonomous museums, paid for by the ministry, with small sponsorships such as Volotea's 50,000 euros for a bike area.")
# FUNDING: a public service agency (BLU) under the Indonesian Heritage Agency that keeps ticket income; the colonial-loot Red flag involves no funder
put('museum-nasional-indonesia',
    funding='Run by the Indonesian Heritage Agency for the Ministry of Culture as a public service agency, which keeps its ticket income.',
    records_note=None)
# FUNDING: CBK's 2025 accounts: City of Rotterdam structural subsidy EUR 4.021m of EUR 4.459m; cbkrotterdam.nl is an outside source
put('tent-rotterdam', tier='A', tier_note=None,
    funding="Run by CBK Rotterdam, which received €4.021m of its €4.459m income in 2025 as the City of Rotterdam's structural subsidy.")
# FUNDING: a volunteer-run foundation on tour donations and friends' gifts; on the market for EUR 1,900,000 in March 2026
put('van-schijndel-house',
    funding='The volunteer-run Mart van Schijndel Foundation, set up in 2008, opens the house on tour donations and friends\' gifts.',
    watch='Mart van Schijndel designed it for himself and finished it in 1993. In March 2026 it was offered for sale at EUR 1,900,000.')
# OVERVIEW: the Sala Covarrubias has 850 seats (EcuRed); the 41st Jazz Plaza opening at the Sala Avellaneda is not confirmed
put('teatro-nacional-de-cuba',
    funding='State theatre run by the Consejo Nacional de las Artes Escénicas under the Ministry of Culture. Built from 1951 and opened in 1979; its two halls seat 2,254 and 850.',
    watch=None)
# FUNDING: commissioned by Mubarak and run by the armed forces; the National Military Museums Department rested on unreferenced Wikipedia text
put('6th-of-october-war-panorama',
    funding='Commissioned under President Mubarak and run by the Egyptian armed forces; Koreans built it over five years. Tickets cost 3 to 30 Egyptian pounds in 2010.',
    affiliations_note='Run by the Egyptian armed forces.')
# Red flags: 2024 expulsion of the historian Alina Bárbara López; 2025 protest resignation of Laideliz Herrera Laza
put('union-de-escritores-y-artistas-de-cuba-uneac',
    why_flagged='It expelled the historian Alina Bárbara López in September 2024 for criticising the leadership; two writers resigned in protest in 2024 and 2025.')
# Red flags: 2025 protests over the ministry's annulment of a Bienal prize; 2025 boycott over unpublished Bienal catalogues
put('museo-de-arte-moderno-de-santo-domingo',
    why_flagged="An open letter with 155 signatures protested the ministry's 2025 annulment of a prize at the Bienal held here; a photographer boycotted the Bienal.")
# FUNDING: Ford Foundation grants of $775,000 (2009 to 2017), British Council library money, a 2024 AFAC grant; website field held a dead AFAC page
put('contemporary-image-collective-cairo', tier='A', tier_note=None, website=None,
    funding='Ford Foundation grants totalling $775,000 from 2009 to 2017, British Council money for its library and a 2024 project grant from the Arab Fund for Arts and Culture.')
# tier_note out of date: AFAC, Ford's grants database, Contemporary And and DutchCulture are outside sources
put('medrar-for-contemporary-art-cairo', tier='A', tier_note=None)
# Red flags: US sanctions on the North Korean government, 2016; website is the Foreign Languages Publishing House site
put('korean-art-gallery-pyongyang', website=None,
    funding="A state art institution of North Korea's Ministry of Culture, paid from the state budget.",
    why_flagged="The North Korean government, which runs it through the Ministry of Culture, has been blocked under US Executive Order 13722 since March 2016.")
# Red flags: US sanctions on the North Korean government, 2016; website is a Koryo Tours blog page; the 1,000+ artefact count is disputed
put('kaesong-koryo-museum-kaesong', website=None,
    why_flagged='A North Korean state museum; the US has blocked the North Korean government under Executive Order 13722 since March 2016.')
# Red flags: US sanctions on the North Korean government, 2016
put('international-friendship-exhibition',
    why_flagged='The North Korean government, which pays for it, has been blocked under US Executive Order 13722 since March 2016.')
# Red flags: US sanctions on the North Korean government and the Workers' Party, 2016
put('mansudae-art-theatre',
    why_flagged="The Workers' Party, which supervises its resident troupe, and the North Korean government have been blocked under US Executive Order 13722 since 2016.")
# OVERVIEW: Kryshtapovich director 2018 to 2025; Russian Wikipedia gives 29 October 2026 as its closing date
put('national-centre-for-contemporary-arts-minsk',
    watch="State body formed 1 Oct 2015. Siarhei Kryshtapovich, director from 2018 to 2025, was commissioner of Belarus's last official Venice pavilion, 'Exit' (2019).",
    records_note='A state-budget body, closed on 29 October 2026 under a Council of Ministers resolution of 3 August 2026.')
# affiliations_note: that the council also runs the Teatro Nacional de Cuba is not confirmed
put('gran-teatro-de-la-habana-alicia-alonso',
    affiliations_note="Home of the Ballet Nacional de Cuba and the Teatro Lírico Nacional's opera seasons.")
# FUNDING: accounts for 2025 filed with the National Bank of Belgium
put('argos-brussels',
    records_note='Its accounts are filed with the National Bank of Belgium, and it lists its seven-person board.')
# FUNDING: the Flemish government received the house as a gift in 1999
put('braemhuis-renaat-braem-huis',
    watch='Renaat Braem gave the house and its contents to the Flemish government in 1999. Herita has worked since 2024 to open it to the public.')
# Website: a Contemporary And page (Website: none); HB Botswana partnership from 2023
put('thapong-visual-arts-centre-gaborone', website=None,
    funding='Board-run centre funded by the Ministry of Youth, Sport and Culture (P2.2M for the 2014 refit). Partners: HB Botswana (2023), BTC Foundation (2018), DTC Botswana and FNB Foundation (2014).',
    records_note='News items name partners and a 2014 board chair.')
# FUNDING: the 88.5 million euro renovation was paid by the EU, the State, the Region, the Département, the City and Nantes Métropole; the Cube's size differs by source
put('musee-d-arts-de-nantes',
    funding='Owned and run by Nantes Métropole; the EU, the State, the Region, the Département and the city paid for the 88.5 million euro renovation that reopened it in 2017.',
    watch='Founded in 1800, in a nineteenth-century palace and a seventeenth-century chapel; a new building for contemporary art, the Cube, was added in 2017.')
# FUNDING: the Deutsche Oper's share of the state grant is 56,159,100 euros in 2026 (final budget)
put('deutsche-oper-berlin',
    funding="Funded by the State of Berlin through the Stiftung Oper in Berlin; the Deutsche Oper's share of the foundation's grant is €56.2M for 2026.",
    records_note=None)
# FUNDING: Staatliche Museen zu Berlin within the SPK; federal government 75 percent, states 25 percent of the operating budget
put('altes-museum',
    funding='One of the Staatliche Museen zu Berlin, paid for through the Stiftung Preußischer Kulturbesitz: three quarters federal money, one quarter from the states.',
    records_note=None)
# FUNDING: Free State of Bavaria; Landtag printed paper 19/10025 (tickets, donations and sponsorship); BMW main partner. The Poing cost rise involves the State's own building, no funder misconduct
put('bayerische-staatsoper',
    funding='Carried by the Free State of Bavaria; in 2025 tickets brought in €29.7M and donations and sponsorship €5.4M, with BMW as its main corporate partner.')
# FUNDING: own chapter in the Berlin budget, 2,038,200 euros planned for 2026; the colonial-objects Red flag involves no funder
put('brucke-museum',
    funding='A State of Berlin museum with its own budget chapter, planning €2.04M of spending for 2026; two private foundations and a friends\' association add money.',
    records_note=None)
# FUNDING: a budget unit of the Beijing Municipal Cultural Heritage Bureau; the building is credited to CADG with AREP; closed on Tuesdays
put('capital-museum',
    funding='One of 17 budget units of the Beijing Municipal Cultural Heritage Bureau, paid from the city budget; admission is free with a timed reservation.',
    watch='A Beijing museum founded in 1981 inside the Confucius Temple and moved in 2006 to a new building in Xicheng.',
    opening_hours='Open 9:00 to 17:00, last entry 16:00; closed Tuesdays (museum website).',
    records_note=None)
# Founded in 1960 (museum website); Website: szmuseum.com; FUNDING: the Pei building cost 339 million yuan, commissioned by Suzhou city bodies
put('suzhou-museum', tier='A', tier_note=None, year_founded=1960, website='https://www.szmuseum.com',
    funding='Built by Suzhou city bodies, with 339 million yuan invested in the Pei building; admission is free with a real-name timed reservation.',
    watch='A museum founded in 1960, in a building by I.M. Pei beside the Humble Administrator\'s Garden since 2006.',
    records_note=None)
# FUNDING: Zhang Baoquan's money (about 10 million yuan a year at first), then sponsorship and earned income; Website: todayartmuseum.com
put('today-art-museum', website='http://www.todayartmuseum.com',
    funding="Founded on Zhang Baoquan's money, about 10 million yuan a year at first; by 2012 sponsorship, the shop and other income brought in 40 million yuan a year.",
    records_note=None)
# OVERVIEW: two main sites, Gushan and Zhijiang (opened 29 August 2023); FUNDING: centrally and locally co-built since 2009, free since 2004
put('zhejiang-museum',
    funding='A Zhejiang provincial museum, co-funded by the central state since 2009 and free to enter since 2004.',
    watch='A Hangzhou museum opened in 1929; its main sites are Gushan by West Lake and the Zhijiang site, opened on 29 August 2023.',
    records_note=None)
# affiliations_note on the Prix Marcel Duchamp is not confirmed by the report
put('red-brick-art-museum', affiliations_note=None)
# OVERVIEW: the house opened on 20 June 1952 (1968 is steirischer herbst's year)
put('halle-fuer-kunst-steiermark-graz', year_founded=1952)
# FUNDING: supported by the City, the Province, the Republic and Dornbirner Sparkasse
put('kunstraum-dornbirn-dornbirn',
    funding='Supported by the City of Dornbirn, Land Vorarlberg and the Republic of Austria, with Dornbirner Sparkasse and its members.',
    watch=None,
    records_note='Lists its six-member managing board.')
# OVERVIEW: it "works in association with, yet independent from, KNUST" (e-flux)
put('blaxtarlines-kumasi',
    funding="An artist-run network housed at KNUST's Department of Painting and Sculpture in Kumasi, working with the university but independent of it.",
    records_note=None)
# FUNDING: Ministry of Culture grants (Rs 31.34 crore for 2023-24); the CAG audit concerns its own management, not a funder
put('victoria-memorial-hall',
    funding="Funded by India's Ministry of Culture, which budgeted Rs 31.34 crore for it in 2023-24, plus its own ticket income.",
    records_note=None)
# FUNDING: Tatjana Cragg chairs the Cragg Foundation's board
put('skulpturenpark-waldfrieden',
    funding='The Cragg Foundation, set up by the Cragg family in 2005 and chaired by Tatjana Cragg, runs the park Tony Cragg bought in 2006.')
# Website: js-foundation.art does not connect; the live domain is jsfoundation.art (Brose's Nazi-era forced labour is WIDER CONTEXT)
put('julia-stoschek-foundation', website='https://jsfoundation.art')
# FUNDING: the Education Ministry and Erasmus "supporters" rested on logo file names
put('villa-rothmayer',
    funding='Run by the Museum of Prague, which the City of Prague funds with a CZK 227.9M subsidy (2024).')
# OVERVIEW: the 41st edition ran 25 January to 1 February 2026; Prensa Latina reported its closing gala in the Sala Avellaneda
put('festival-internacional-jazz-plaza',
    funding="A state festival run through the Ministry of Culture's Instituto Cubano de la Música.",
    watch='The 41st edition ran from 25 January to 1 February 2026; organisers say over 120 US artists have confirmed for the 42nd, in January 2027.',
    affiliations_note='Organised by the Instituto Cubano de la Música, part of the Ministry of Culture system. Prensa Latina reported the 41st edition\'s closing gala in the Sala Avellaneda of the Teatro Nacional.')
# Website: the museum's site is listasafnreykjavikur.is (listasafn.is is the National Gallery of Iceland)
put('reykjavík-art-museum-reykjavík', website='https://listasafnreykjavikur.is')

open(p, 'w', encoding='utf-8').write(json.dumps(recs, indent=2, ensure_ascii=True))
print('\n'.join(log))
print(len(log), 'changes')
