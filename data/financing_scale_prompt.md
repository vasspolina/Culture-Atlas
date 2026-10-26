# Culture Atlas financing and scale prompt

The prompt every research agent gets for one batch of cultural spaces. It produces two things per
space, as numbers a source states: its scale (visitors, staff, floor area) and, where the record
holds no accounts figures yet, its financing (the year's income, spending and how it splits). The
Details card prints them under "Scale and money". The funding text, flags and tier are not touched.

---

## The prompt (give it to the agent word for word, with the batch file named)

You are researching the scale and financing of cultural spaces for the Culture Atlas, a public
map of cultural institutions graded by who funds them. Today is <DATE>. Work in
<WORKTREE>. Read `data/financing_scale_runs/<RUN>/batches/<BATCH>.json`: a list of records, each
with id, name, city, country, website, size (S, M, L or empty), year_founded, `needs_finance`
(true when the atlas holds no accounts figures for it), `finances_note` (what the atlas already
says about its accounts) and sources.

Write `data/financing_scale_runs/<RUN>/out/<BATCH>.json`: a JSON list with one object per input
record, in input order, and edit no other file:

```
{"id": the input id,
 "scale": {"visitors": whole number or null, "visitors_year": "2024" or "2023-24" or null,
           "staff": whole number or null, "staff_kind": "employees" | "full-time equivalent" | "staff" | null,
           "staff_year": "2024" or null,
           "area_m2": whole number or null, "area_kind": "gallery space" | "building" | "site" | null,
           "sources": [the urls you read for these figures]},
 "finance": null, or, only when needs_finance is true and a filing or ministry or city budget line states it:
           {"fy": "2024" or "2023-24", "currency": "EUR", "income": number in full units or null,
            "expenditure": number or null, "public": number or null, "private": number or null,
            "earned": number or null, "sponsorship": number or null, "net_assets": number or null,
            "source_kind": "annual report" | "Form 990" | "Charity Commission" | "OSCR" | "Companies House" |
                           "audited statements" | "ministry budget" | "city budget" | "ACNC" | "CRA" | other,
            "url": the document or register page you read},
 "basis": at most one sentence per block (scale, finance) saying where the figures sit (PDF page, table or register line) and, when the years differ, which figure has which year}
```

### Method

1. Start from the space's own website: annual report, "about", press kit, facts and figures page.
   Then the registers (below), then national statistics or ministry reports on museum visits, then
   reporting in the press. Use the language of the country as well as English.
2. Registers for accounts: US Form 990 through ProPublica Nonprofit Explorer (the API at
   projects.propublica.org/nonprofits/api/v2 needs no key); UK Charity Commission, OSCR, Companies
   House; Germany and Austria Bundesanzeiger or the Jahresbericht, or the city or state budget line;
   France the rapport d'activité; the Netherlands and Belgium the jaarverslag or the ANBI page;
   Nordics the årsrapport; Canada CRA; Australia ACNC; elsewhere national registers or the
   institution's audited statements. A state or municipal museum with no separate accounts: use the
   ministry or city budget line that names it, if one exists.
3. Visitors: the most recent full year the space itself or an official or independent count states
   (annual report, ministry statistics, the Art Newspaper's annual attendance survey, a city
   tourism office). Count of visits, not of unique visitors, unless the source says otherwise;
   say which in the basis sentence. Staff: the count the annual report gives and whether it is
   employees or full-time equivalents. Floor area: square metres of exhibition or gallery space
   when a source states it, otherwise the building's gross or floor area, and say which in
   `area_kind`. Convert square feet to square metres (1 ft2 = 0.0929 m2) and round to a whole number.
4. Read PDFs as text: save the file with curl, then `python3 tools/pdf_text.py FILE FIRST LAST`
   (macOS PDFKit; pages count from 1 in PDF order, which can differ from the printed number, so
   name the PDF page). A page summary from a fetch tool is not the page: take a figure only from
   the document's own text. If the host refuses curl or the PDF is a scan with no text, write null
   for what only that document held.
   Open every document and write each figure from the page in front of you. Copy numbers exactly,
   converting thousands and millions to full units. Never estimate, never take a figure from a
   search snippet or memory, never fill a gap from a similar space. Percentages are not stored.
5. A figure from an older year is allowed when it is the latest the sources give; state its year.
   Visitors, staff and the money block each carry their own year, so they may differ; say so in basis.
6. Where a source does not state a figure, write null. Do not write a placeholder. A figure a
   source gives only as "more than N", "about N" or "up to N" is null, not N. Staff is the count
   of people or full-time equivalents the source labels as such; budgeted or advertised posts
   and a forecast budget are null. `income` is the year's total income as a filing or budget
   line states it. A turnover, an "earned" line or an equity figure from a monograph, a press
   piece or a recruitment notice is not a filing: leave `finance` null for that record.
7. Never get past a bot check, login or paywall. If a site blocks you, leave the figures null
   and move on. Fetch pages with curl through Bash (the lead gives you the hosts it may reach) or WebFetch; never the browser pane. The `sources` already on a record may be funder research, not scale sources: use them only if they help.
8. Labels. A fiscal year that runs across two calendar years is "2024-25" (April 2024 to March 2025
   is "2024-25"), named by the year it starts and ends in; a calendar year is "2024". Use the
   same rule for `staff_year`. Take a count as the source gives it: do not add or remove
   seconded, temporary or hired-venue figures, and name what the count includes in the basis
   sentence. Sum two stated areas only when the source states both for the same space and say so.
   A city or ministry cost line that names the space is allowed for `finance` (source_kind
   "city budget" or "ministry budget"); say in the basis that it is a project line.
9. An all-null record gets `"basis": ""`. Never write what a search missed.
10. A "search" is one WebSearch call; opening a page is not a search. Use at most <BUDGET> web
   searches across the batch; the registers and the spaces' own pages
   can be opened directly.

### House rules

Plain English, no em dashes or en dashes, no hedging words. Only the `basis` sentence is free text
and the atlas never says something was not found: do not write what a search missed in it.

Write the file early and update it after every few records. Reply with: how many records got
visitors, how many staff, how many floor area, how many a finance block, and the three oddest
sources.
