# Controversy pass of 21 November 2026: the 860 records with no dispute on them

Run-specific rules. Where they differ from `data/details_prompt.md`, these win. The house rules of
that prompt (plain English, no dashes as punctuation, no hedging, no filler, every claim from an
opened page) and the rulings of `data/details_runs/2026-11-20b/RUN.md` all apply.

## Why this run

860 of the 2,116 records carry no Red flags section, no flag, no reported case and no reported
story. Each already has a Details report whose research was mostly about money. This pass looks for
one thing only: a documented dispute about the space. It does not rewrite the report. It adds
sections to it, and only where a source supports them. Most spaces will have nothing, and for those
no file is written.

## What counts

A dispute about the space itself, its leadership in their public role, its funders or its holdings,
that an opened source documents with a date:

- a protest, boycott, open letter, petition or artist withdrawal aimed at the space;
- a labour dispute: a strike, contested layoffs, a union complaint, a tribunal or labour-court ruling;
- governance: a director dismissed or suspended, board resignations in protest, a finding of
  mismanagement, an audit office's criticism, a cost overrun on public money;
- censorship: a show, work, artist or event cancelled, removed or altered under pressure, by the
  space or by a state;
- looted or contested holdings: a restitution claim, a return, a provenance ruling, a seizure;
- a lawsuit, court ruling or regulator's decision about the space;
- a funder controversy under the atlas's flags (fossil fuels, gambling, tobacco, arms and defence,
  opioids, sanctions, Gulf state body, forced or exploited labour, Epstein-linked), or a funder or
  board figure with a conviction, plea or regulatory fine;
- a contested closure, eviction, merger or relocation that someone on record opposed.

## What never goes in

- An ordinary bad review of an exhibition. A piece that criticises the institution's conduct can be
  a CRITICISM IN ART MEDIA item.
- The space's own announcement with nobody objecting. A budget cut with no dispute around it.
- Anything about a private person (front-of-house staff, a junior employee, an intern, a visitor),
  about children, or about a public person's life outside the role (health, family, relationships,
  religion, immigration status).
- An accusation of a crime against a named person unless a court filing, a regulator's decision or a
  named news outlet's reporting carries it.
- A claim only one anonymous account makes. Wikipedia as the only source. A page you could not open.
- A dispute about a different institution of a similar name, or about the operator's other venues,
  unless the source ties it to this space.
- Anything already in the row's `wider_context` or `press_items`.

## Where each finding goes

- `Red flags: <heading>` for a dispute dated November 2021 or later, and for a court order,
  conviction, restitution or audit finding of any date within the last five years. One heading per
  issue, naming its subject and year in plain words ("2023 strike over pay", "2024 return of a
  Nazi-looted painting", "2022 dismissal of the director"). Two issues never share a heading.
- `WIDER CONTEXT` for a dispute before November 2021; an investigation or charge that has not ended
  in a conviction; pressure from a state that neither funds nor controls the space; a dispute about
  the operator or patron that does not name the space, with the connection stated in the last point.
- `CRITICISM IN ART MEDIA` for a signed piece that criticises the institution: outlet, author,
  title, year, URL and two to four points in the critic's terms.

## How to search

For each row, in English and in the language of the country: the space's name (and aliases) with
protest, boycott, open letter, strike, union, layoffs, dismissed, resigned, censorship, cancelled,
lawsuit, court, ruling, restitution, looted, audit, scandal, investigation, eviction, closure. Then
the art press (The Art Newspaper, ARTnews, Artnet, Hyperallergic, Artforum, Frieze, Museums Journal,
Monopol, Le Quotidien de l'Art, Le Journal des Arts, Il Giornale dell'Arte, El País, Metropolis M)
and the national and local press. Open every page you cite and write from the page, not the search
snippet.

Search budget (added after batches c000 to c004): WebSearch allows 200 calls a turn, shared by every
agent running, and the first batches ran out. So:

- Start each space with its Wikipedia article in English and in the country's language (WebFetch,
  no search cost). Read any section on disputes, criticism or history and open the sources it
  cites. Wikipedia is never the source.
- Then about four searches per space: one combined English query (the name with protest strike
  lawsuit restitution dismissed censorship; the search tool takes no OR operator), one in the
  country's language, and one or
  two follow-ups only where the first two point at something.
- When WebSearch says its limit is reached, stop searching. Finish the spaces already searched and
  log every space you could not search with `"result": "unsearched"`, never `"none"`.
- A general search engine is never queried through curl or WebFetch.

## Wording rules

- No "not found" lines anywhere. A space with nothing gets no file.
- Credit each point to the outlet that states it, in brackets, and state only what that outlet
  states: no added descriptor, job title, superlative or changed detail. Dates and amounts as given.
- An allegation starts "Unverified:" and names who makes it. A documented act (a ruling, a
  dismissal, a return) is stated plainly with its date and authority. Give the space's or the
  person's reply where a source has it.
- Quotations are word for word from the page; mark your own translation as "(translated)" and give
  the original alongside. A paywalled piece: "Paywalled; only excerpts were read".
- No verdict adjective (controversial, problematic, troubling). No hedging words. No dashes as
  punctuation. No statement twice.
- No violent or criminal verb of your own (kills, axes, guts, slams); a crime word only as a court,
  prosecutor or regulator uses it.

## Output

For a space with a finding, write `findings/<record id>.txt` in exactly this layout. Leave out any
section that has nothing. Never write an empty heading.

```
ID: <record id>

Red flags: <heading>
- <one fact per point, with date, figure and the outlet's name in brackets>
- Unverified: <allegation>, from <outlet>

WIDER CONTEXT
- <point>

CRITICISM IN ART MEDIA
1. <Outlet>: <Author>, "<Title>" (<year>)
URL: <url>
- <what the piece argues>

SOURCES
- <url> (add "(paywalled)", "(advocacy source)" or "(state outlet)" where it applies)
```

Also write `findings/<batch>-log.json`: a JSON list with one object per row of the batch,
`{"id", "result": "finding" | "none" | "unsearched", "searches": <number run>, "note": "<what the searches turned
up and why it was kept or left out, one line>"}`. The log is the editor's trail and is not printed.

## Tools

- WebSearch, and `curl` through Bash (name each host in `allowed_domains`) or WebFetch.
- Never the browser tools (`mcp__Claude_Browser__*`, `mcp__claude-in-chrome__*`, `mcp__computer-use__*`).
- Never pass `-k` to curl and never disguise curl as a browser. If a site refuses, use another source.
- A site that sends WebFetch to a pay wall for automated readers (a "tollbit" redirect, as ARTnews,
  Artforum and the Dallas Morning News do) has refused the read. Do not fetch the same page with
  curl instead; use another outlet or leave the point out.
- An archive copy (web.archive.org) may stand in for a page that is gone or down; it is not a way
  round a site that refuses automated reads or sits behind a paywall or registration wall.
- Scratch files go in `$TMPDIR`, never in the repository.
- Research agents write only `findings/<record id>.txt` and `findings/<batch>-log.json` in this
  folder. Checkers edit those .txt files and write `checks/<batch>-check.json`. Nobody touches
  `institutions.json` or any other file.
