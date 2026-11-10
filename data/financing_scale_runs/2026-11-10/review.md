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
