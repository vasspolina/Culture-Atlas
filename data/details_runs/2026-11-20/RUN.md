# Details run of 20 November 2026: the 150 thinnest records

Run-specific rules. Where they differ from `data/details_prompt.md`, these win.

## Why this run

A reader opened a museum on a phone and found one dispute told five times and two funding lines.
These 150 spaces are the thinnest on the atlas: 96 have no Details report at all, 54 have a report
with one funding point or none. The aim is a fuller record for each: what the space is, who runs
it, who pays and how much, and each dispute under its own plain title.

## What a fuller record holds

- OVERVIEW: founding, building, collection or programme, who directs it now, visitor numbers and
  the current or next season, wherever an opened source states them.
- FUNDING: aim for four or more points where sources allow. Who owns and operates it; who pays the
  running costs, with amounts and years; who paid for the building and for any renovation or
  extension; friends' associations and what they buy; sponsors and what each pays for; the backers
  named on single shows. A short honest report beats a padded one: never pad.
- Red flags: one heading per issue. The heading names its subject and year in plain words
  ("2024 dispute over a Nan Goldin slide", "Cost and delay of the berlin modern extension"). A cost
  overrun or audit criticism of public money is its own heading. Never fold two issues into one.

## Records that already have a report

A batch row with a `details` key already has a report on the atlas. Your report replaces it whole,
so carry over every point that still holds, then add to it. Re-open the source of a point you
doubt. Never drop an existing Red flags section or press item unless a source shows it is wrong,
and say so in your reply.

## Rules that override the prompt

- No "not found" lines, anywhere. Never write "No reporting found of ...", "No criticism found in
  art media", "The pages read did not state ...", "no X was found" or any sentence that reports an
  empty search. Leave the point out. When no criticism exists, leave the CRITICISM IN ART MEDIA
  section out. (Standing ruling of the atlas's editor; it overrides Method steps 6 and 9.)
- No statement twice. A fact, figure or funder appears once in the report, in the section where it
  belongs.
- Buyers of a space's services (paid announcements, venue hire, ticket buyers) are clients, not
  funders.
- Propaganda-layer and Antarctic pins carry `propaganda`, `operator` or `claim` fields. Treat them
  as leads to verify, not as text to copy. FUNDING names the operator and who pays.
- Hard-to-source places (North Korea, closed or exiled spaces): use what exists and stop there.

## Tools

- WebSearch, and `curl` through Bash (name each host in `allowed_domains`) or WebFetch.
- Never the browser tools (`mcp__Claude_Browser__*`, `mcp__claude-in-chrome__*`,
  `mcp__computer-use__*`).
- If `curl` fails on a certificate, do not pass `-k`; use another source.
- Scratch files go in `$TMPDIR`, never in the repository.
- Write only `data/details_runs/2026-11-20/reports/<record id>.txt` (research) or edit those files
  and write `checks/<batch>-slop.json` (checking). Touch no other file, and never
  `institutions.json`.
