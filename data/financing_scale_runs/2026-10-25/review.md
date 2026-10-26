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
