# Culture Atlas funding research prompt

Research one cultural space and report who funds it, using only what published sources state.

## Input
- Record: the space's current entry from `institutions.json` (id, name, location, website, funding, watch, flags, sources).

## Method
1. Read the existing record first. Your job is to confirm, correct or add to it, not to restate it.
2. Search the web: the space's own site (about, annual report, supporters, board), Wikipedia, art press (Artforum, The Art Newspaper, Artnet, e-flux, Contemporary And), national and local press, charity or company registries, and investigative or advocacy outlets.
3. Check the website itself. If it is down, parked, or serving spam, say so.
4. Follow the money one step beyond the space: founders, board chairs, major donors, and any state or government patronage (land grants, commissions, tax arrangements). A founder's other projects count only when they connect to the same funders or patrons.
5. Separate names that look related but are not (a foundation with the same name, a different museum in another city) and say they are not related.
6. Label every claim's strength: reported by an independent outlet; stated by the space itself; or an allegation, naming who makes it and whether that source is openly partisan.
7. Never guess. If nothing is found, write "No reporting found".

## Output — part 1: report (plain text, this exact layout)

```
<NAME IN CAPITALS> – <City>, <Country>
Website: <url, or "unreachable / serves spam" and the date checked>

OVERVIEW
- What it is, where, who founded it, when it opened, building/site facts, programmes, access (opening days, discounts, accessibility)

FUNDING
<Name of space>: <one-line verdict, e.g. "appears self-funded", "mainly public", "corporate-sponsored">
- Each funding source with what it pays for, and where the money ultimately comes from
- "No reporting found of …" where a search came up empty

Red flags: <short heading for the issue>   (repeat per issue; omit if none)
- Each fact, with figures and dates; mark allegations "Unverified" and name the outlet's stance

Not related: <similarly named entity> — why it is a different organisation   (omit if none)

BOTTOM LINE
Two or three sentences: is the space itself clean, and what, if anything, is worth watching.

SOURCES
- <url> (add "(advocacy source)" or "(partisan)" where relevant)
```

## Output — part 2: record update (JSON, for the importer)

```json
{
  "id": "<record id, exactly as given>",
  "retrieved": "<YYYY-MM-DD>",
  "website": "<url or null>",
  "website_status": "ok | down | spam | parked",
  "funding": "<one or two sentences, the funding as stated now>",
  "tier": "A (clean, source cited) | B (flagged, with a reason) | U (unverified)",
  "flags": ["<short flag names, or empty>"],
  "why_flagged": "<one sentence, or empty>",
  "other_findings": ["<each red-flag fact as one sentence, prefixed 'Unverified:' for allegations>"],
  "funders": ["<named funders, sponsors, patrons>"],
  "bottom_line": "<the BOTTOM LINE text>",
  "not_related": ["<similarly named entities that are not this space>"],
  "sources": ["<every url used>"],
  "changes": ["<each way this differs from the existing record, one line each>"]
}
```

Rules: write in plain English, no adjectives of judgement beyond what sources support; tiers describe how well the record is sourced, not a verdict on the space; keep the report under 600 words.
