# Culture Atlas

A globe and a chat for looking up who funds museums and cultural spaces. Each record shows what is stated about its funding and links to where that comes from. Live: https://vasspolina.github.io/Culture-Atlas/

## What it does

- **Chat.** Answers from the records only. It names the record and its source, and says when a record does not say. An optional API key in settings turns on open-ended replies.
- **Globe and map.** Click a space to see its record. City and country filters.
- **Filters & lenses.** Filter the globe by tier, region and category, or type a country or city. The studies and community notes open in the research library.
- **Offline.** Installable as an app; the service worker caches the page.

Tiers describe how well a record is sourced, not a verdict on the museum: Clean (source cited), Flagged (a recorded reason), Unverified. See "What the page may show" below.

Type is PP Mori Extralight at 14, 18 and 26px; body text is 18px, labels 14px, titles 26px. PP Eiko Light Italic is used only for links and call-outs.

Buttons are off-white pills with black text and no outline; a pressed one inverts. Lines are single rules, never boxes around content; nothing is grey and nothing is set in capitals. On a desktop everything about a selected space, including what the building x-ray finds, is in the right column, not on the map.

---

## Quick Start

### Option 1: Python HTTP Server (Zero Dependencies)

Run the included server script:

```bash
cd app
python3 serve.py
```

Or using Python's built-in module:

```bash
cd app
python3 -m http.server 8080
```

Then open [http://localhost:8080](http://localhost:8080) in your browser.

---

### Option 2: Node.js / npx

```bash
cd app
npx serve . -p 8080
```

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
├── assets/ fonts/      # Images and typefaces the page loads
├── institutions.json   # Dataset
├── data/               # Research sources, papers, corrections and the inputs behind the dataset
├── tools/              # Data pipeline: clean_data, embed_data, the importers and verify_claims
├── src/ app/ public/   # Older Vite/React sources and build output, not used by the page
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
