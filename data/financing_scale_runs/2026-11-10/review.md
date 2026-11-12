# Run 2026-11-10: the pins the first run never batched

The first run (2026-10-25, f000 to f100) was cut from 1,208 records. 256 pins added to main since then sat in no batch;
`tools/build_financing_batches.py 2026-11-10 --skip-run 2026-10-25` cuts them into 22 batches of 12 (f021 holds 4). All 256 need finance.

# Stage 11 review (f000 to f009)

Ten research agents, then four checker agents re-opened every cited source for the 29 records that held a figure.
- Dropped before checking: Cap Moderne finance (audited 2022 accounts, older than 2023).
- Dropped by the checkers: Haus der Kunst and Horta Museum finance (turnover and equity only; neither filing states total income or
  expenditure), Van Doesburghuis expenditure (the treasurer's report says the second half's property invoices had not arrived).
- Corrected: Villa Stiassni to the NPU 2025 report (18,483 visits); the Beijing War of Resistance museum's accounts to whole yuan; page
  references (AfricaMuseum PDF page 71); Porte Doree sponsorship 68,000 (Mecenat line of the same account).
- Kept with a note: Palais de la Porte Doree finance and staff cover the whole public body (museum, Aquarium, monument on one site), which
  the record names, while visitors are the museum's own; Didrichsen expenditure is EUR 1 off its component columns in the Finnish Heritage
  Agency return, read as rounding; Gallen-Kallela and Didrichsen finance come from that official statistics return, which states total
  income and expenditure in columns of its own (the foundations publish no accounts); Rose Seidler House counts general admissions (2,574)
  and leaves out 20 venue-hire admissions; National History Museum Tirana 2023 is its last full year (closed May 2024); Semler Residence
  7,344 is the house-museum's tour visits, its permanent display; INSTAR is its own unaudited one-page 2024 statement.
- Official statistics used as sources: Albania's tourism bulletin (Ministry of Culture table), the Finnish Heritage Agency's museum
  statistics, the Berlin Senate's museum table (final 2024, not provisional 2025), a Hong Kong LegCo written reply, the Beijing finance
  portal's final accounts, CRA T3010 open data, ACNC AIS data (confirming Boyd House II).
- Across the stage: 22 more records with scale (18 with visitors, 4 with an area, 1 with a dated staff count), 9 more finance blocks.
  The three Cuba batches (f003 to f005) gave one figure (INSTAR). 323 records with scale and 501 with finance in all.

# Stage 12 review (f010 to f021, the last batches of the run)

Twelve research agents, then four checker agents re-opened every cited source for the 41 records that held a figure. The four
North Korea batches (f012 to f015, 33 of their 48 records) gave nothing: no institution there publishes accounts or counts, and
state media are press.
- Dropped by the checkers: Museum Het Schip staff and finance (its own report calls it one museum on two sites, Het Schip and De
  Dageraad), La Pedrera finance (a segment row of the Fundacio Catalunya La Pedrera table whose rows add up to the foundation total,
  with central costs untraceable), Museum of Yugoslavia staff (32 permanent plus 3 fixed-term; the total is never printed), Ho Chi
  Minh Museum visitors (counted to the year-end review on 16 December 2025, so part-year), MNIR public (state subsidy only, leaving out
  EU programme money).
- Dropped by rule after checking: Cultuurhuis Bergeijk and De Nollen finance (both income totals are operating income that leaves out
  interest, and neither states total expenditure; their visitor counts stay).
- Corrected to newer reports: Padrao dos Descobrimentos to the final 2025 count (184,795), Panorama 1453 to 2025 (196,326), MNIR
  finance to the December 2025 execution accounts. Chiang Kai-shek Memorial Hall public set to the filed other operating income line
  (NT$192,742,093), which is the Ministry of Culture subsidy plus other government subsidies; the stored subsidy line alone was
  narrower. Vigeland Museum source moved to Kulturetaten's 2024 annual report. Four US source_kind labels set to 990-PF or 990-EZ.
- Kept with a note: Sunnylands income includes USD 32,992,418 of gains on asset sales and Frelinghuysen Morris income USD 3,528,054
  of securities gains (both as filed); the Frank Lloyd Wright Trust, the Paul Rudolph Institute and the Center for Cuban Studies run
  more than one programme, but each record names that body; Atelier Volten's 1,153 is the count for its only exhibition of 2025, the
  only time it opens to the public (75 group-tour visitors on a separate line); Ho Chi Minh Museum staff is the 124 the museum states
  at its 16 December 2025 review; Plecnik House 16,518 is the table's exact figure (the prose says "more than 16,500").
- US finance read from the IRS bulk e-file XML (14 filings) and re-read by two checkers against the same objects.
- Across the stage: 23 more records with scale, 23 more finance blocks. 346 records with scale and 524 with finance in all. All 22
  batches of the run are done.
