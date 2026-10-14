# Culture Atlas

A globe and a chat for looking up who funds museums and cultural spaces. Each record shows what is stated about its funding and links to where that comes from. Live: https://vasspolina.github.io/Culture-Atlas/

## What it does

- **Chat.** Answers from the records only. It names the record and its source, and says when a record does not say. An optional API key in settings turns on open-ended replies.
- **Globe and map.** Click a space to see its record, or a city or country to filter. The studies and community notes open in the research library.
- **Offline.** Installable as an app; the service worker caches the page.

Tiers describe how well a record is sourced, not a verdict on the museum: Clean (source cited), Flagged (a recorded reason), Unverified. See "What the page may show" below.

## Design

Plain CSS, no framework: one stylesheet at `assets/atlas.css` (design layer plus a short generated block of layout helpers) and `assets/maplibre-gl.css` for the street map. The page loads no CSS or script from a CDN.

The look follows the It's a book fair site: a white page, a strip of tabs on hairlines, flat colour blocks (cobalt, orange, cyan, mustard, periwinkle, magenta), a black pill for the current filter, a yellow close mark, and a grey sheet with the facts as a ruled table. Titles are PP Neue Gstaad Compact Bold in capitals, body is PP Neue Gstaad Regular, labels and buttons are monospace. The globe is unchanged and sits on black. Text on a colour block is black, except on cobalt, where it is white.

---

## Run it locally

No build step and no dependencies. From the repository root:

```bash
python3 -m http.server 8080
```

Then open [http://localhost:8080](http://localhost:8080).

---

## Using the chat

Open the chat, or press `Cmd+K` / `Ctrl+K`, and ask about a space, a city or a funder, for example "Which spaces in Tokyo are Clean?" or "What does the record for Te Papa say about funding?". An optional API key can be added under settings.

---

## Deploying

`main` is the source of truth. Every push to `main` runs
`.github/workflows/deploy.yml`, which copies `index.html`, `sw.js`,
`manifest.json`, `assets/` and `fonts/` to the `gh-pages` branch that GitHub
Pages serves. Do not push to `gh-pages` by hand. If the live site looks stale,
check the **Actions** tab for a failed "Deploy to GitHub Pages" run.

## Editing the page

`index.html` is edited directly. No script regenerates it: the data inside it
is rewritten by `tools/clean_data.py` then `tools/embed_data.py`, and everything
else is changed in the file itself.

The design tool's generator, patch and test scripts that used to sit in the
repository root were removed on 13 October 2026: the page had been edited
directly for a long time, and the generators would have overwritten it with
older text and fonts. The research they ingested is kept under `data/inputs/`
(the Consensus library export, the user research tables and the incoming
research notes). One of the removed scripts carried a working Anthropic API
key in base64 pieces; it is still in the git history and must be revoked.

The Academic Research Library window was removed on 14 October 2026. Its 183
studies and eight case studies are kept in `data/library/`, the Gossip Mode
research and the visual critique reference list stay in `data/`, and none of
them is shipped in the page. What belongs to one institution now sits on that
institution's own record. `tools/attach_research.py` writes four fields, and
re-running it replaces them:

- `study_notes`: a line from a study's abstract that states something specific
  about that institution (9 lines from 7 studies). Each was checked three times
  and keeps the quote it rests on in `data/research_attach/study_findings.json`.
  The other 176 studies name no institution on the map, or only as a passing
  example, and are not shown.
- `case_notes`: case study table rows that the record did not already state,
  copied word for word (74 rows, 88 record entries because a few museums have
  two pins). Rows the record already states are listed with the quote that
  shows it in `data/research_attach/case_decisions.json`.
- `case_study`: the MoMA and Whitney case studies, whole.
- `funder_links`: funders and trustees the map names at three or more
  institutions, only where the record's own text names them (230 links; 55
  where it does not are left out).

Notes saved in this browser are read back inside the chat ("Notes saved in this
browser" in the chat reply opens nothing).

## What the page may show

The page shows what a record states and where it comes from, and says plainly that none of it has been independently verified.

- A field appears only if a record states it. Figures, hours, prices, exhibitions, architects and "chatter" are not generated to fill a gap. A text value shared by five or more records (after masking the name and city) is filler and is left out. Sentences that assert the absence of ties ("zero fossil fuel", "strict ethical charter") are left out.
- **Clean, source cited** needs at least one source outside the museum's own site. **Flagged** needs a recorded reason. Otherwise a space is **Unverified**.
- Anything reported about a space, such as a sponsor tie, an Epstein-related item, a WikiLeaks cable or a case file, is shown with its own source links under "Reported, not independently verified".
- Anonymous staff reviews, the board network, the timeline, the filings registry, the itineraries and the generated 3D building interiors are not shown: they had no source, or were invented or generated. The building view draws only the outline OpenStreetMap holds for the building, through the map tiles, with the record's own material stacked inside it, and says where any Wikidata fact came from.

Rules live in `tools/clean_data.py`. To check records against their sources, run `tools/verify_claims.py` somewhere with network access, then `tools/apply_verification.py` and `tools/embed_data.py`. Wording corrected after checking is in `data/corrections.json`; the pilot of the three-check protocol is in `data/verification_pilot.json`.

## Project Structure

```
Culture-Atlas/
├── index.html          # The whole app, edited in place. The only HTML copy.
├── sw.js               # Service worker (network-first for the page, same-origin cache only)
├── manifest.json       # PWA manifest
├── assets/ fonts/      # atlas.css, maplibre-gl.css, images and the typefaces the page loads
├── institutions.json   # Dataset
├── data/               # Research sources, papers, corrections and the inputs behind the dataset
├── tools/              # Data pipeline: clean_data, embed_data, the importers and verify_claims
└── .github/workflows/  # Deploy to gh-pages on push to main
```

---

## Dataset Schema

Each entry in `institutions.json` has the following fields:

```json
{
  "name": "ARoS",
  "location": "Aarhus, Denmark",
  "tier": "A",
  "size": "L",
  "funding": "DKK 125M budget, 600k visitors. Aarhus Municipal Council, Danish Ministry of Culture, ticket sales, and Salling Foundations.",
  "watch": "Major Danish art museum topped by Olafur Eliasson's 'Your rainbow panorama'. Financed primarily by municipal funds and the philanthropic Salling Fondene; clean ethical sponsorship policy.",
  "sources": [
    "https://www.aros.dk/en/about-aros/",
    "https://sallingfondene.dk"
  ],
  "lat": 56.153,
  "lon": 10.2
}
```

---

## Verification & Methodology

- **Clean Status (Tier A)**: Institutions with no current fossil fuel, weapons/defense, opioid, tobacco, gambling, or sanctioned state sponsorship.
- **Data Cutoff**: Verified against annual reports, partner listings, and public disclosures up to late September 2026.
