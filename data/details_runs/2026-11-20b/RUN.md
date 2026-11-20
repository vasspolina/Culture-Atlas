# Details run of 20 November 2026, second part: the 208 records with two funding points

Run-specific rules. Where they differ from `data/details_prompt.md`, these win. They are the rules of
the first part (`data/details_runs/2026-11-20/RUN.md`) plus the rulings its checkers applied.

## Why this run

The first part (PR #811) gave fuller records to the 150 thinnest spaces. These 208 are the next
thinnest: each has a Details report with exactly two funding points. The aim is the same: what the
space is, who runs it, who pays and how much, and each dispute under its own plain title.

## What a fuller record holds

- OVERVIEW: founding, building, collection or programme, who directs it now, visitor numbers and
  the current or next season, wherever an opened source states them.
- FUNDING: aim for four or more points where sources allow. Who owns and operates it; who pays the
  running costs, with amounts and years; who paid for the building and any renovation or extension;
  friends' associations and what they buy; sponsors and what each pays for; the backers named on
  single shows. A short honest report beats a padded one: never pad.
- Red flags: one heading per issue, naming its subject and year in plain words ("2024 dispute over a
  Nan Goldin slide"). A cost overrun or audit criticism of public money is its own heading. Two
  issues never share a heading.

## Every row already has a report

Every batch row carries a `details` key: the report on the atlas now. Yours replaces it whole, so
carry over every point that still holds, re-opening its source, then add to it. Never drop an
existing Red flags section or press item unless a source shows it is wrong; say so in your reply.

## Rulings (from CHECKER.md, as the first part's checkers applied them)

- Protests, open letters, censorship cases and staff disputes before November 2021 go to WIDER
  CONTEXT, not Red flags, unless a newer one of the same kind exists.
- Pressure from a state that neither funds nor controls the space is WIDER CONTEXT.
- A government funder (a ministry, city, region or army) never takes a sanctions flag because its
  officials are sanctioned: that is WIDER CONTEXT. Sanctions on the space's own director, or on a
  private funder or a person who controls one, stay as Red flags. A listing only by a country other
  than the US, EU, UK or UN is a name to know, stated plainly.
- Funder flags (fossil fuels, gambling, tobacco, arms, opioids) need the funding to be current
  (within about five years) or a documented objection. Older funding is history under FUNDING.
- A dispute about a different institution goes under WIDER CONTEXT with the connection stated.
- Buyers of a space's services (paid announcements, venue hire, tickets) are clients, not funders.

## Wording rules

- No "not found" lines anywhere: never "No reporting found", "No criticism found", "The pages read
  did not state", "in the sources read", "is not known", "Website: none found" (write "Website:
  none"). Leave the point out. With no criticism, leave the section out.
- No statement twice. BOTTOM LINE gives the verdict only and repeats no fact stated above it.
- Credit each point to the outlet that states it, and state only what that outlet states: no added
  descriptor, job title, superlative or changed detail. A restoration's cost is not a donor's gift.
- A point resting only on a search snippet, a cached copy nobody could open, a logo image, a URL slug
  or a summarising fetcher's paraphrase is not sourced: confirm it from the page or leave it out.
  Quotations are word for word from the page, or become plain paraphrase without quotation marks.
- Mark your own translations and romanisations as such (give the original script alongside), a
  paywalled piece as "Paywalled; only excerpts were read", an abstract-only read as such, and a
  partisan or state outlet in SOURCES. An allegation starts "Unverified:" and names who makes it; a
  documented act (a ruling, a dismissal, a freeze) is stated plainly with its date and authority.
- Prefer the space's own pages, official registers and press over Wikipedia; a Wikipedia-only
  figure must be on the cited page itself.

## Tools

- WebSearch, and `curl` through Bash (name each host in `allowed_domains`) or WebFetch.
- Never the browser tools (`mcp__Claude_Browser__*`, `mcp__claude-in-chrome__*`, `mcp__computer-use__*`).
- Never pass `-k` to curl and never disguise curl as a browser. If a site refuses, use another source.
- Scratch files go in `$TMPDIR`, never in the repository.
- Write only `data/details_runs/2026-11-20b/reports/<record id>.txt` (research) or edit those files
  and write `checks/<batch>-slop.json` (checking). Never touch `institutions.json` or any other file.
