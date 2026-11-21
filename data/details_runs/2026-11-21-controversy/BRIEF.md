# Briefs for the agents of the controversy pass

Each agent is given one of these with its batch id in place of `<batch>`. `RUN.md` in this folder
holds the rules; these say how to work a batch.

## Research agent

You are a research agent for the Culture Atlas, a public map of cultural institutions. Your job:
for each cultural space in your batch, find out whether a documented dispute about the space exists
(protest, labour dispute, governance, censorship, contested holdings, lawsuit, funder controversy,
contested closure), and write it up only where an opened source supports it.

1. Read `RUN.md` in this folder first, in full. Its rules are binding: what counts, what never goes
   in, where each finding goes, how to search (including the search budget: Wikipedia first, about
   four WebSearch calls per space, the limit is shared with other agents), the wording rules, the
   exact output layout, and the tools you may use.
2. Then read the "House rules" section of `data/details_prompt.md` at the repository root (binding
   wording rules).
3. Your batch is `batches/<batch>.json`: rows with the space's id, name, aliases, city, country,
   website, a few overview lines, and what the record already holds in `wider_context` and
   `press_items`. Do not repeat those, nor what the `overview` lines already state.
4. Work one space at a time, start to finish, and give each space its own searches: at least two,
   one in the country's language. For small spaces (artist-run rooms, project spaces, small
   museums) local and specialist press matters more than the international art press. Use WebFetch
   or curl (with its default user agent, never a browser's) to open pages, and WebSearch for
   searches (load it with ToolSearch "select:WebSearch" if it is not loaded). Never use any browser
   tool. Open every page you cite and write from the page.
5. For a space with a finding, write `findings/<record id>.txt` in the exact layout RUN.md gives.
   For a space with nothing, write no file. Do not stretch a weak item to fill a file. None of
   these is a finding:
   - a strike or closure that is part of a national or sector-wide action and does not name the space;
   - a protest aimed at someone else on the premises;
   - a funder's or owner's own corporate news that no source ties to the space;
   - a dispute about the operator that no source ties to this space;
   - a cost rise nobody on record objected to;
   - a theft or accident with no dispute around it;
   - a lone appeal by one association with nothing else;
   - an ordinary review of an exhibition.
   A claim resting only on a union's, party's or campaign's own page is "Unverified:" with that
   source named. A well-sourced finding matters more than coverage.
6. Write `findings/<batch>-log.json` with one object per row, as RUN.md describes. A space you
   could not search because the WebSearch limit was reached is logged "unsearched", never "none".
   Where a likely item was lost only because every page carrying it refused automated reads, say
   so in the log note with the address.

Write only those files. Do not touch `institutions.json` or anything else in the repository.

Reply with: one line per space that got a file (id, the headings written, number of sources), then
the count of spaces with nothing, the ids logged "unsearched", and any site that refused reads.

## Checker

You are the checker for research batches of the Culture Atlas. Research agents wrote short findings
files about disputes at cultural spaces; nothing is published until you have checked each claim
against its source.

Read first, all binding: `RUN.md` in this folder; `sponsor-atlas/work/ubatch/SLOP.md` and
`CHECKER.md` (in /Users/polinavasilyeva/culture-atlas/); the "House rules" section of
`data/details_prompt.md` at the repository root.

Check the findings files that the logs `findings/<batch>-log.json` of your batches mark with
"result": "finding" (the files are `findings/<record id>.txt`; the logs carry the researcher's
notes). For each file:

1. Open every URL under SOURCES and every press item URL with WebFetch, or with curl using its
   default user agent only (never a browser's user agent string, never `-k`, never a browser tool,
   no archive copy as a way round a paywall or a refusal). For each point, confirm the page states
   it: the date, the figure, the name, the title, who said what. Cut or cut back any point no
   opened page supports. A quotation must be word for word from the page, or become plain
   paraphrase. Remove a source that is dead, redirects to a homepage or does not mention the space.
2. Apply RUN.md's placement rules: a dispute before November 2021 is WIDER CONTEXT, not Red flags;
   an investigation or charge with no conviction is WIDER CONTEXT; pressure from a state that
   neither funds nor controls the space is WIDER CONTEXT; two issues never share a heading (split
   them); a heading names its subject and year in plain words and states nothing a source does not.
3. Apply "What never goes in": no private persons, no children, nothing about a public person's
   life outside the role, no accusation of a crime against a named person without a court filing,
   regulator's decision or named outlet's reporting, no claim only one anonymous account makes,
   nothing that is not a dispute about this space (see the research brief's list). A point resting
   only on a union's, party's or campaign's own page starts "Unverified:" and names that source; if
   the whole file rests on one such page and it is thin, delete the file.
4. Fix the wording rules in place: no dashes as punctuation, no hedging words, no filler, no
   verdict adjective, no "not found" lines, no statement twice, no violent or criminal verb of the
   writer's own.
5. Read the record's existing Details report for the same id in `institutions.json` at the
   repository root (the `details` field, and `funding`, `watch`) and cut any point the record
   already states. Where the record holds an older, weaker version of the same event (an
   "Unverified" line the finding now confirms), say so in the check file so the editor replaces it.
6. Keep the layout of RUN.md exactly. A file left with no Red flags section, no WIDER CONTEXT point
   and no press item is deleted.

Edit or delete the .txt files in place. Write `checks/<batch>-check.json` for each batch: a JSON
list with one object per change, {"id", "section", "problems": [...], "before", "after", "sources":
[up to 3 urls you opened], "reason"}; a deleted file is one object with "after": "" and the reason.
Do not edit any other file. You do not need WebSearch; if you use it, keep to a handful of calls,
since its limit is shared.

Then, for the editor (not printed anywhere): list in your reply every finding that, under the
atlas's flag rules in CHECKER.md and details_prompt.md, could change a record's flags or grade (a
documented protest or boycott aimed at the space since November 2021, a funder under a flag, a
sponsor dropped under pressure, state censorship or punishment, looted or contested holdings), with
the id, the flag and one line of reason.

Reply with: files checked, files clean, files changed, files deleted (with ids and reasons),
sources that could not be opened, and the flag candidates list.
