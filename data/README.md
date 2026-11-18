# data/

Everything the atlas was built from, apart from the dataset itself. `institutions.json` (repository root)
is the published dataset; this folder holds the research behind it, the prompts that produced that
research, the editorial decisions applied to it, and the raw inputs the importers read.

Nothing in here is loaded by the site. The deploy workflow copies only `assets/` and `fonts/`. The files are
read by the scripts in `tools/` (and a few tests), which write their results into `institutions.json`
and the generated `assets/*.js` / `assets/*.json` files. **File paths are part of that contract**: the
scripts name these paths directly, so move or rename a file only together with the script that reads it.

How the data flows:

```
research agents (prompts below) -> data/*_runs/ -> tools/import_*.py / merge_*.py
   -> institutions.json -> tools/clean_data.py, grade_funding.py, embed_data.py -> assets/*
```

## Editorial decisions (small, hand-kept)

| File | What it is | Used by |
|---|---|---|
| `corrections.json` | Per-record fixes applied by hand (a wrong name, city or fact), keyed by record id. | `tools/clean_data.py` |
| `duplicates.json` | Record ids that are the same space entered twice, and which one survives. | `tools/clean_data.py` |
| `verification_pilot.json` | A ten-claim pilot of the three-check verification protocol (primary source, independent source, nothing contradicts). Documents the method and its limits; not a verification of the dataset. | read by people; no script |

## Research briefs and findings (large, append-only)

| File | What it is | Used by |
|---|---|---|
| `sponsor_atlas.json` | The Sponsor Atlas: 1,197 sponsor/space rows, the base list the first records were built from. | `tools/import_sponsor_atlas.py`, `update_sponsor_atlas.py`, `attach_pin_layers.py` |
| `finances_2026-10-18.json` | Budget and income figures per space, as collected on 18 Oct 2026. | `tools/attach_finance_scale.py` |
| `people.json`, `people.csv` | Who leads each space (directors, chief curators, founders), with titles, dates, predecessors and sources. The CSV is the same table flattened for review. | `tools/build_people_batches.py`, `merge_people.py` |
| `gossip_items.json` | Dated, sourced reports (press, staff and visitor posts, documents) that feed each record's Gossip data and the latest-reports feed. | `tools/add_reports.py`, `attach_gossip.py`, `build_live_feed.py` |
| `gossip_research.md` | Working notes behind the gossip items. | `tools/import_gossip_accounts.py`, `import_gossip_findings.py` |
| `culture-atlas-gossip-dataset.json`, `culture-atlas-gossip-research.md` | The expanded Gossip Mode research set of 9 Oct 2026 (25 cases, 22 institutions) with its methodology. Kept as the source document. | read by people; no script |
| `propaganda.json`, `propaganda_pins.json` | Cases of cultural funding used for state or corporate image-making, and the spaces they pin to. | `tools/import_propaganda.py`, `import_propaganda_pins.py` |
| `space_lobbying.json` | Lobbying records (US and EU) per space. | `tools/attach_space_lobbying.py` |
| `critique_additions.json` | The 29 additional artists' critique images (source page, credit, date, story) added after the original collection. | `tools/add_critique_images.py` |
| `visual_critique_refs.json` | Reference list for the visual critique images (id, artist, title, source URL). | read by people; no script |
| `funder_logos_sources.json` | Where each funder logo was fetched from. | `tools/build_funder_logos.py` |

### Influence map

| File | What it is | Used by |
|---|---|---|
| `influence_candidates.json` | 4,479 candidate funder/space links found automatically, before review. | `tools/build_influence.py`, `tests/influence.test.mjs` |
| `influence_review.json` | The review verdict on each candidate. | `tools/build_influence.py`, `build_money_maps.py`, `attach_lobbying_notes.py` |
| `influence_hq.json` | Head-office locations of funders. | `tools/build_influence.py` |
| `influence_senders.json` | Funders grouped by the sender they are drawn as on the map. | `tools/build_influence.py`, `assets/influence-mode.js` |

## Prompts (the instructions each research agent was given)

`bureaucracy_prompt.md`, `details_prompt.md`, `details_check.md`, `financing_scale_prompt.md`,
`people_prompt.md`, `research_prompt.md`. Each is the exact text given to the agents for one kind of
research; the `*_runs/` folder of the same name holds what came back. `details_check.md` is the
second-pass text checker for Details reports. Change a prompt only for a new run, never to rewrite history.

## Run folders (what the agents returned, grouped by run)

Each folder is dated or numbered per run, holds the batches sent out, the raw reports that came back and the
checker's verdicts, and is read only by its importer. They are a record: do not edit them to fix a record,
edit the record (or `corrections.json`).

| Folder | Contents | Importer |
|---|---|---|
| `research_runs/` | First-pass research reports per space (`2026-10-20`, plus `manual` one-offs). | `tools/import_research_reports.py` |
| `details_runs/` | Details cards (visitor facts, funding story) and their checks. | `tools/import_details_reports.py` |
| `bureaucracy_runs/` | `r1`–`r3`: governance and bureaucracy grading, each with `RESEARCH.md` and `CHECK.md`. | `tools/import_bureaucracy.py` |
| `financing_scale_runs/` | Budget-scale research (`2026-10-25`, `2026-11-10`), with batches and outputs. | `tools/import_financing_scale.py` |
| `people_runs/` | `p1`, `p2`: leadership research. | `tools/merge_people.py` |
| `slop_runs/` | Text-slop lint changes, by date. | `tools/lint_text.py` |
| `web_research/` | Audits against the web: address, coordinate and building-pin audits, geocoding, OpenStreetMap and Wikidata lookups, with their decisions. | `tools/apply_geocode.py`, `apply_osm_addresses.py`, `geocode_pins.py`, `apply_wikidata_pins.py`, `audit_pin_buildings.py` |
| `research_attach/` | Hand-prepared findings attached to records: case notes, new spaces, propaganda pins, institutional critiques, network funders. Dated in the filename. | `tools/attach_*.py`, `import_propaganda*.py` |

## Reference material

| Folder | Contents |
|---|---|
| `inputs/` | The research as first received: `user_research.csv` and `user_research_tables.csv` (the founding institution list), `academic_papers.json`, `incoming_research.txt`. |
| `library/` | `case_studies.json` (the MoMA and other case studies shown on the studies page) and `academic_research.json` (the paper summaries). Read by `tools/attach_research.py`. |
| `papers/` | Twelve CSV exports from the literature search (donor transparency, sponsor connections, controversies, governance). Source material for the library; not read by scripts. |

## Conventions

- Dates in file names are ISO (`YYYY-MM-DD`) and mean the day the research was collected.
- Record ids are the slugs used in `institutions.json` (for example `storm-king-art-center`).
- A fact enters a record only with a source URL and a check date; see "What the page may show" in the root README.
- Add new research as a new dated file or run folder; do not overwrite an earlier one.
