# Pilot review, f022 (France) and f040 (Japan)

A second agent re-opened every cited source and compared each stored figure. Corrections made to
the out files before import:

- Séries Mania: "more than 108,000" is a lower bound, so visitors is null.
- La Friche: the finance block came from a monograph (turnover and equity), not a filing; null.
- Cité internationale des arts: the report gives operating lines only, no total; finance null.
- Nezu Museum: the 2025 report covers April 2025 to March 2026; both years labelled "2025-26".
- Villa Arson: 880 m2 is the art centre's area, not stated as exhibition space; area_kind null.
- Frac Centre: 26 permanent agents come from an undated recruitment notice; staff null.

Everything else matched its source. Per batch of 12 the pilots cost 93 to 111 tool calls and about
150,000 to 190,000 tokens, and gave scale figures for about half of the records.

# Stage 1 review, f000 to f009 (120 records)

Four checker agents re-opened every cited source for the 66 records that held a figure. Changes
made to the out files before import:

- Dropped for a weak source (Wikipedia, an unnamed press list, a director's biography, a news
  article naming no data): Museo Nacional de Bellas Artes and MAMBA visitors, MAMBA staff, Palacio
  Libertad, Heydar Aliyev Center, YARAT and Z33 floor areas, Dhaka Art Summit visitors.
- Dropped as not what the record is: Pinacoteca visitors (the count covers every APAC site),
  Fundacao Bienal visitors (one edition, rounded), Museum Dhondt-Dhaenens visitors (table does not add up).
- Dropped as rounded: 4A visitors ("56K"). Dropped as unlabelled: MASP area kind.
- Held until the source can be read: National Gallery of Australia (report blocked for the checker).
- Corrected: MAM Rio income and spending were operating lines; totals now 6,113,917.70 and
  10,375,678.40 BRL (the statement's deficit agrees). Malba visitors now the 2022 figure, 347,588,
  the latest in Malba's own table.
- Five Belgian finance blocks carry only turnover or equity, so the importer drops them.

# Stage 2 review, f010 to f019 (120 records)

Four checker agents re-opened every cited source for the 53 records that held a figure.
Rule applied to floor areas: a figure stays only when the institution or the architect's own site states
it; magazine, press, travel-list and aggregator pages are dropped (this also removes 21_21 Design Sight
from stage 1, which came from Arquitectura Viva).

- Dropped as rounded or estimated: Power Station of Art and Louisiana visitors (tables in 10,000s and
  1,000s), Ordrupgaard visitors (partly estimated), MeetFactory public, private, earned and net assets
  (printed in thousands), Trapholt staff (31.3 FTE).
- Dropped for scope: Sesc Sao Paulo staff and area (whole network of 47 units), Allende museum visitors
  (include touring exhibitions), WHW finance (whole association, not Galerija Nova), The Rooms staff
  (excludes seasonal and hourly staff).
- Dropped for source: Power Station of Art, National Art Museum of China, He Art Museum, HOW Art Museum,
  Long Museum, Hubei, MOCA Yinchuan and Centro Leon areas (press or magazine); OCAT Shenzhen (page may
  describe another building); DOX (a programme-plan line); Pivo (rental floors); Copenhagen Contemporary
  keeps 7,000 m2 with no kind.
- Dropped as unreliable: Power Plant finance (the statement is marked draft), Dazibao finance (the charity
  number could not be tied to the gallery).
- Corrected: MeetFactory income and spending now the exact figures from its financial overview.

# Stage 3 review, f020 to f021 and f023 to f030 (f022 was the France pilot)

Four checker agents re-opened every cited source for the 44 records that held a figure; the 8 figures in
f027 to f030 passed unchanged.

- Dropped, wider or narrower than the record: Humboldt Forum area (a heading figure covering partners'
  rooms), Tallinn Art Hall public (one ministry line), Grand Palais visitors (excludes the Olympic events),
  Palais de Tokyo visitors (exhibition tickets only).
- Dropped as unreliable: Humboldt Forum finance (income is an unlabelled subtotal), Louvre finance (operating
  lines rounded to 0.1 million), Versailles visitors (the source's total disagrees with its own components
  by 5,000), Jeu de Paume staff (54 in one table, 57 in another).
- Replaced: four Berlin visitor counts were provisional 2025 figures; the final 2024 figures from the same
  Senate table are stored. Palais de Tokyo income, spending, public and sponsorship are the exact figures
  of its budget table, not the rounded text.
- Le Fresnoy keeps 11,000 m2 with no kind.

# Stage 4 review (f031 to f039 and f041), in part

f035 to f037 checked so far (the f031 to f034 and f038 to f041 checks follow in a later entry).
- Dropped as wider or narrower than the record: Uffizi visitors (whole autonomous institute), Fondazione Prada
  area and staff (one site; 2019 count), Palazzo Strozzi area (only the part used for 2025 projects), Centro Pecci
  visitors (users of several services whose lines do not add up).
- Dropped for source: Tel Aviv visitors (a news article relaying a list), Pirelli HangarBicocca area (page
  unreadable), Triennale Milano area (rooms and public spaces together, no kind).
- Dropped as turnover not total income: Project Arts Centre finance.
- The two Castello di Rivoli records are the same institution (duplicate pins); both carry the staff count.

f038, f039, f041 checked:
- Dropped as users of several services or a wider group: Aomori visitors (rental halls, library and exhibitions in one
  total), Sapporo festival visitors (69 percent at the Snow Festival site), Kanazawa 21 area (the museum line inside
  a larger total with a car park).
- Dropped as round: Fondazione Sandretto Re Rebaudengo visitors ("70.000" among other round indicators).
- Replaced: Kanazawa 21 visitors now the FY2025-26 figure, 2,079,288, from its 2025 annual report.

f031 to f034 checked:
- Replaced: Reykjavik Art Museum now its 2024 report (257,669 visitors, 42 staff), the museum's own newest.
- Kept at 2024: Ludwig Museum Budapest (88,249); its 2025 report's total disagrees with its own ticket categories.
- Dropped: Crawford Art Gallery visitors (a trade-magazine list is the only source). Area kinds the sources do not
  state were removed for CHAT and Museum MACAN; the numbers stay.
- The Reykjavik Art Museum record's website field points to the National Gallery of Iceland (a different body);
  the museum's site is listasafnreykjavikur.is. Not changed here.

# Stage 5 review (f042 to f051)

Four checker agents re-opened every cited source for the 40 records that held a figure.
- Dropped as users of several services, attendees or wider scope: Mediamatic visitors, V2_ visitors (activity
  attendees including partner events), Marres visitors (includes projects on location), Cervantino festival attendance
  (a press release is the only source).
- Dropped as operating lines or conflicting totals: Het Concertgebouw finance (operating lines before interest), Framer Framed
  finance (the form's table and narrative disagree on total income), Mediamatic public (one unclear line).
- Dropped for an undated, unstated or narrower area or count: Groninger Museum staff (the factsheet gives no date), Te Papa
  area (public floor space, not building area), MOWAA area (one building of the campus), Museo Soumaya area (no kind).
  Mudam keeps 4,000 m2 without a kind.
- Kept at an older labelled year where a newer report exists but could not be read: Het Concertgebouw staff (FY2025 is a scan),
  Mudam visitors (2024), Sonic Acts visitors (2024), Museum Beelden aan Zee (2024; the 2025 report says "over 102,000").

# Stage 6 review (f052 to f061)

Four checker agents re-opened every cited source for the 29 records that held a figure.
- Dropped as operating lines or a total budget: Fotogalleriet and UKS finance (operating lines before financial items), BWA Wroclaw
  finance (a year-end total budget, not income).
- Dropped as a draft or a press source: Serralves visitors and staff (the report cover reads "pre-design version"), Hermitage and
  Russian Museum visitors (a press survey on a third party's host), MAC/CCB visitors (a press note quoting a survey),
  Ayala Museum visitors (a counter widget), Oman staff (a news report of a media briefing), Kistefos visitors (a sector
  association table; the museum's own figure is round).
- Dropped as agent-made or unstated: Museum of Islamic Art area (a sum of two lines; the page is the interior designer's),
  Erarta area (a round figure of unstated kind).
- Corrected: Manege area is the institution's total of three buildings, 9,500 m2 (9,499.8), not one building; MUNCH staff
  relabelled 2026 (count on 1 January 2026).
- Kept at an older labelled year: Bergen International Festival (2023; the 2024 report is a Canva page).

# Stage 7 review (f062 to f071)

Four checker agents re-opened every cited source for the 38 records that held a figure.
- Dropped as an edition count, not a year of visits: Busan Biennale and Changwon Sculpture Biennale visitors (2018 ministry release,
  one edition each, eight years old).
- Dropped as wider scope: Es Baluard visitors (the statistics cover the museum and the whole cultural complex), Tabakalera visitors
  (building visitors across six bodies), Chillida Leku area (a whole-hectare garden figure, and the garden is not the site).
- Dropped as a draft or an unclean period: MMCA staff (a business plan marked draft, civil-service posts only), Kunst Halle
  Sankt Gallen visitors (five shows from November 2023 to March 2025, not a calendar year), Fondation Beyeler earned (only the
  tickets and events line, not total earned income).
- Corrected: Fundacio Joan Miro visitors now its 2025 report (311,704) and staff 81 from the 2024 report's dated count (the 118 came
  from an environmental chart that includes collaborators); Centro Botin visitors now the 142,582 who attended exhibitions (the
  184,727 headline adds 42,145 activity participants).
- Kept with a note: Slovak National Gallery area (5,385 m2 is the Bratislava complex; visitors and staff cover all its sites);
  HEK, Museum Tinguely, Kunsthaus Baselland and Fondation Beyeler visitors come from the Basel-Stadt and Basel-Landschaft museum
  visit tables (official cantonal statistics, "Angaben der einzelnen Museen"; Kunstmuseum Basel's own report differs from the table,
  so its own figure is used); CaixaForum Madrid stays at 2024 (no 2025 release found); Moderna Galerija stays at 2023 (the 2024
  report is a scan); Fondation Beyeler finance is FY2022, the latest accounts that could be opened.

# Stage 8 review (f072 to f081)

Four checker agents re-opened every cited source for the 52 records that held a figure.
- Dropped as an average or FTE count of staff (the accounts label the line "average", "average monthly" or "FTE"): Kunsthaus Zurich,
  De La Warr Pavilion, Pallant House, Grizedale Arts, Towner, BALTIC, Compton Verney, Charleston, FACT, Mostyn, Autograph, Camden Art
  Centre, Delfina, Design Museum, Dulwich Picture Gallery, English National Ballet, British Museum, National Gallery, National Portrait
  Gallery, Somerset House, Zabludowicz, HOME, Turner Contemporary, MK Gallery, New Art Exchange and Nottingham Contemporary.
- Dropped as a trade-body table only: GoMA and the Whitworth visitors (ALVA league table, no figure from Glasgow Life or the University).
- Dropped as rounded or not clean: Science Museum visitors (every cell of the table ends in 000), Arter area (18.000 m2), Shedhalle
  visitors (includes off-site event attendees), Kettle's Yard (total attendance across concerts and learning), C-LAB area (a 7.15 hectare
  site shared with other tenants), Nottingham Contemporary area (the architect's credit gives no kind).
- Corrected to a newer report: Tate Modern 4,538,061 (2025-26), V&A South Kensington 3,349,300 (2025-26), Taipei Fine Arts Museum
  1,001,773 (2025), SALT 606,666 (2025, both buildings), Chisenhale staff 13 (2025-26, salaried employees).
- Kept with a note: The MAC (door count of the building, 2025), Towner (the report also calls the number visitors and participants),
  Henry Moore Institute (a year shortened by closure until 12 July 2024), Manchester Museum (University of Manchester release, Museum
  alone), Modern Art Oxford staff 40 (trustees' report staff demographics, 21 full-time and 19 part-time), National Galleries of Scotland
  (2023-24 exact figure; the 2024-25 report gives only 2.63 million), Gasworks (2023-24; later reports give rounded figures), National
  Portrait Gallery (exact value of a table in thousands).

# Stage 9 review (f082 to f091)

Two checker agents re-opened every cited source for the 20 records that held a figure.
- Dropped as a round figure: The Broad area (120,000 sq ft on both its own page and the architect's), Yorkshire Sculpture Park site
  area (the accounts say "500 acres" throughout).
- Dropped as not a clean count: ICP staff (376 individuals employed during calendar 2023, a cumulative count with no dated snapshot),
  Eskenazi Museum area (119,318 gross sq ft is the building before the 2018 renovation and includes space taken from another body).
- Dropped as stale: New Orleans Museum of Art visitors (2019, and the museum's later reports could not be opened).
- Corrected to a newer report: Kemper Museum visitors 52,461 (2025), Ackland Art Museum visitors 52,745 (2025-26), Amon Carter Museum
  year label (fiscal year 2024-25, not calendar 2025).
- Joslyn Art Museum: the impact page calls 206,546 "total attendance"; the museum's own By the Numbers sheet calls it visitors to the
  museum and counts program participants separately, so it is kept and cites the sheet.
- Kept with a note: Walker Art Center (132,300 gallery visits; garden and event attendance are separate lines), Frist Art Museum
  (208,350 guests read as visits), Birmingham Museum of Art (2022-23; the museum's site blocked the check for a newer report),
  Wave Hill (28 acres stated three times in its own report), The Bass and Madison Museum of Contemporary Art (areas in square feet
  that are not round thousands).
- Across the stage: staff counts were almost all dropped before checking (averages, FTE, "nearly" or undated); no finance blocks.

# Stage 10 review (f092 to f100, the last batches)

Four checker agents re-opened every cited source for the 41 records that held a figure. The IRS e-file route (below) was reproduced.
- Dropped before checking under the standing rules: all nine Form 990 "individuals employed in the year" staff counts (cumulative, not a
  dated headcount), Telfair Museums visitors (2020), American Folk Art Museum visitors (2017-18), Skowhegan site area (350 acres, round).
- Dropped by the checkers: REDCAT exhibition area (3,000 sq ft, round thousand); Royal Academy area (18,365 m2 is the denominator of a
  carbon ratio over the main buildings and warehouses, several sites); NewBridge Project visitors (exhibitions only, counted per
  exhibition, other programmes counted apart); the four Barbican Centre lines (a management table that leaves Barbican Renewal out of
  public funding and buildings, unaudited, and a department of the City of London with no separate accounts); New Museum and Galeria de la
  Raza "earned" (mostly membership councils, and a "Misc income" line).
- Corrected to a newer filing: Transmission Gallery 2025-26 (OSCR), The NewBridge Project 2025-26 (Companies House, filed 14 Oct 2026),
  Primary 2024-25 (Charity Commission copy, image only, read from the rendered pages), The Showroom income 408,830 (the trustees' review
  prints 408,290, a digit slip), Printed Matter earned 277,502, Catalyst Arts source (Companies House copy of the accounts).
- Kept with a note: ICA and London Museum finance are group accounts (the ICA charity alone reports gross income 3,791,092; London Museum
  income includes 106.6M of New Museum project funding); Raven Row 31,396 visitors is stated for its exhibitions, which are its programme;
  Phillips Collection 135,301 (the report does not say whether the Phillips@THEARC site is included; it holds 620 gallery visitors);
  BAM FY2022-23 (the newest year on bam.org; 990 totals differ from the audited operating lines, net assets agree); EAC Montevideo 1,400 m2
  from a 2016 presentation (no newer source could be opened).
- IRS e-file route: ProPublica serves a bot check on every 990 PDF, so the nine US blocks (New Museum, Printed Matter, Recess, Smack Mellon,
  Storefront, Triple Canopy, Artpace, Galeria de la Raza, Southern Exposure) were read from the IRS bulk e-file XML (apps.irs.gov) by byte
  range, matched to each organisation by EIN, name, address and website, and re-read by the checker. Storefront and Smack Mellon use the
  amended returns of record. Where the batch listed a ProPublica page, `finance.url` is that page; otherwise it is the IRS zip, and the
  basis names the XML object.
- Across the stage: 9 more records with scale (5 with visitors, 4 with an area, no staff), 21 more finance blocks (12 UK, 9 US); f100 (Vietnam, Zambia, Zimbabwe) held no figure. 301 records with scale and 492 with finance in all.
