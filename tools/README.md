# tools/

The data pipeline. Scripts read research from `data/`, rewrite `institutions.json`, and generate the
files the site loads in `assets/`. Run from the repository root, for example
`python3 tools/clean_data.py`. Python 3 and the standard library; the `.mjs` scripts need Node.

Typical order after new research: an **importer** brings it in, an **attacher** adds it to records,
`clean_data.py` (which calls `grade_funding.py`) applies the display rules, `embed_data.py` writes the
result into the page, then the **builders** regenerate the derived files (money maps, live feed, studies).
Descriptions below are each script's own docstring; read the script for details. File paths in
`data/` are read by name, so see `data/README.md` before moving any.

## Importers

| Script | What it does |
|---|---|
| `import_bureaucracy.py` | Read the agents' output for data/bureaucracy_prompt.md into the records. |
| `import_details_reports.py` | Details card text from research reports written to data/details_prompt.md. |
| `import_financing_scale.py` | Read the agents' output for data/financing_scale_prompt.md into the records. |
| `import_gossip_accounts.py` | Attach the individual accounts retained by data/gossip_research.md (rows R01…, RD01…) to the Atlas records they name. |
| `import_gossip_findings.py` | Attach the OS01 findings (NS01 to NS14) from data/gossip_research.md to the Atlas records they name. |
| `import_propaganda.py` | Attach the propaganda layer's findings to the records they are about. |
| `import_propaganda_pins.py` | Add the institutions that the propaganda layer needed and the atlas did not hold, then attach their findings. |
| `import_research_reports.py` | Merge funding research into institutions.json, after review. |
| `import_sponsor_atlas.py` | Add institutions from the Sponsor Atlas study (data/sponsor_atlas.json) that institutions.json does not have yet. |
| `import_web_research.py` | Merge web-research findings into institutions.json, then run tools/clean_data.py and tools/embed_data.py. |

## Attachers

| Script | What it does |
|---|---|
| `attach_artifact_findings.py` | Carry what the Sponsor Atlas artifact of 19 Oct 2026 holds beyond the study lines into the records. |
| `attach_critiques.py` | Put the critical frames in data/research_attach/institutional_critiques.json on the records they apply to. |
| `attach_finance_scale.py` | Attach the structured accounts figures to records as `finance`. |
| `attach_closures.py` | Write the closing years in data/closures.json into institutions.json (year_closed, closed_note), then run tools/embed_data.py. No year is entered that the record's own text does not name. |
| `attach_flag_details.py` | Add the further detail found for "Why it is flagged" to each flagged record as flag_details: |
| `attach_gossip.py` | Write the gossip items from data/gossip_items.json onto the records they are about, as `gossip_data.gossip`. |
| `tell_gossip.py` | The gossip items retold in the voice of Gossip mode (`told`): lists the items still to retell, checks retellings against their items and writes them in. |
| `attach_lobbying_notes.py` | Add the case notes on funders' lobbying through a space (data/research_attach/lobbying_case_notes_*.json) to the records. |
| `attach_pin_layers.py` | Attach the Sponsor Atlas's per-pin research layers to the records they are about. |
| `attach_research.py` | Fold what the retired research library held into the museum records it is about. |
| `attach_space_lobbying.py` | Attach each space's own lobbying (data/space_lobbying.json) to its record as `lobbying`. |

## Appliers

| Script | What it does |
|---|---|
| `apply_address_audit.py` | Apply the address audit to institutions.json, then run tools/clean_data.py and tools/embed_data.py. |
| `apply_coordinates.py` | Give the records that have no coordinates (0, 0: |
| `apply_geocode.py` | Move pins to the building OpenStreetMap found for them (tools/geocode_pins.py), then rerun clean and embed. |
| `apply_osm_addresses.py` | Write the addresses tools/osm_addresses.py found into institutions.json, then run tools/clean_data.py and tools/embed_data.py. |
| `apply_verification.py` | Copy results from data/verification.json into institutions.json. |
| `apply_wikidata_pins.py` | Move the pins OpenStreetMap could not place to the coordinate location (P625) Wikidata gives them (tools/wikidata_pins.py), then rerun clean and embed. |

## Builders

| Script | What it does |
|---|---|
| `build_art_periods.py` | What kind of art each funder's money goes to: writes `assets/art-periods.json` from each space's own words (run after `build_influence.py`). |
| `funder_profiles.py` | Funder profiles for the funder page: who a funder is and where its money comes from; merges researched batches into `data/funder_profiles.json` and writes `assets/funder-profiles.json`. |
| `build_bureaucracy_batches.py` | Cut institutions.json into research batches for data/bureaucracy_prompt.md. |
| `build_critique_frames.py` | Write data/research_attach/institutional_critiques.json from verified quotations. |
| `build_critique_gallery.py` | Build the artists' image gallery layer from the cultural space critique collection (references 1801-2000). |
| `build_financing_batches.py` | Cut institutions.json into research batches for data/financing_scale_prompt.md. |
| `build_funder_logos.py` | Builds the logos the money map sets beside a company's name (assets/funder-logos.png and assets/funder-logos.json). |
| `build_hq.py` | Builds assets/hq.json: |
| `build_influence.py` | Step 1 of the sender view: |
| `build_live_feed.py` | Write assets/live.json, the latest reports on the spaces, from institutions.json. |
| `build_moma_influence.mjs` | Copies what the MoMA Influence Map study says about each funder, trustee, agency and protest into the Influence map (user, 17 Nov 2026: |
| `build_money_maps.py` | Build assets/money-maps.json, the data behind money-maps.html. |
| `build_people_batches.py` | Cut institutions.json into research batches for data/people_prompt.md. |
| `build_studies.py` | Build assets/studies.json, the data behind studies.html, from the Sponsor Atlas case studies. |

## Other

| Script | What it does |
|---|---|
| `absence.py` | Drop what only says something was not found. |
| `accept_web_research.py` | Turn raw two-pass web-research rows into accepted claims for tools/import_web_research.py. |
| `add_critique_images.py` | Add artists' critiques of art spaces to the images page, beside the cultural space critique collection. |
| `add_reports.py` | Add newly researched reports to the atlas in one step, for the daily update (notes/daily-reports.md). |
| `audit_pin_buildings.py` | Is there a building under each space's pin on the street map? |
| `check_repetition.py` | No statement twice in one record: |
| `unlabel_repeats.py` | No label that its own line says again: the label check for the text of institutions.json. |
| `clean_data.py` | Rules that decide what the page is allowed to show from institutions.json. |
| `editor.py` | The data editor: |
| `embed_data.py` | Rewrite assets/institutions.js, the institution data the page loads, from institutions.json (after tools/clean_data.py). |
| `geocode_pins.py` | Look up every record's building on OpenStreetMap (Nominatim) and write what it finds to a review file. |
| `grade_bureaucracy.py` | The bureaucracy level (1 to 5) of a record, worked out from the facts in its `bureaucracy` block. |
| `grade_funding.py` | Funding transparency rating: |
| `lint_text.py` | Text-slop lint for institutions.json: |
| `merge_people.py` | Fold one run of data/people_prompt.md into data/people.json and data/people.csv. |
| `osm_addresses.py` | Fetch the street address OpenStreetMap holds for every record that has none, and write it to a review file. |
| `osm_visiting.py` | Fill opening hours and free admission from OpenStreetMap, for records whose building is already matched to an OpenStreetMap object (named in field_sources, by the pin audit or tools/apply_osm_addresse |
| `pack_funder_logos.mjs` | Packs the logos tools/build_funder_logos.py saved into one sheet of one-colour masks: |
| `pdf_text.py` | Print a PDF's text, one "=====PAGE n=====" header per page (macOS PDFKit; no extra packages). |
| `site_outlines.py` | The outline of each space's own ground, from OpenStreetMap, for the street map. |
| `update_sponsor_atlas.py` | Bring a newer Sponsor Atlas study into the records. |
| `verify_claims.py` | Check what each record says against the sources it cites. |
| `wikidata_pins.py` | Second pass for the pins tools/geocode_pins.py could not place: |

