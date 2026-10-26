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
