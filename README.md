# Culture Atlas

A globe and a chat for looking up who funds museums and cultural spaces. Each record shows what is stated about its funding and links to where that comes from. Live: https://vasspolina.github.io/Culture-Atlas/

## What it does

- **Chat.** Laid out as a dialogue: set like an interview transcript: a two-letter speaker mark (ME, CA) in the margin wrapped lines hanging 1.6em in, and the first line of every paragraph, first or later, indented one em, your turns in green, one blank line between turns, no bubbles and no italics. Answers from the records only. It names the record and its source, and says when a record does not say. An optional API key in settings turns on open-ended replies.
- **Globe and map.** Click a space to see its record, or a city or country to filter. The globe is drawn in hairlines only (coastlines, borders, hollow rings for spaces) and fills its whole pane.
- **Money maps.** Each record has a map of what it states about its funding: the space in the middle, a circle for each funder, flag or documented tie, and lines between them. Circles that name the same funder link to other spaces. Open it from a record's Money map button, or go to `money-maps.html#<record id>`; `money-maps.html` on its own shows the big map of every space and sponsor. Drag to turn the map in 3D, pinch or scroll to fly through it, touch to make the circles sway. See "Money maps" below.
- **Typography.** Set after Jost Hochuli's *Detail in Typography*: kerning, ligatures and capital-height punctuation on; measure held to about 66 characters with a soft ragged right and no lone last words; leading rises with line length; tracking tightens as size grows; quotes, apostrophes, ellipses, en dashes and year ranges are corrected in the chat and the record by `assets/typeset.js`; acronyms are set a step smaller. Emphasis is set in Regular Italic. Bold and capitals are kept for one thing, the name of a space: the record's headline in Compressed Bold, the name on a map card, pop-up or street-map label and in a chat answer in Compact Bold, always in capitals. Every other heading and label is in the Regular, in normal case, and is told by its size and the space around it. In a record, the info text and the chat on a phone, the first paragraph of a run is flush and each one after it is indented one em, with no blank line; a source list or registry line is a break, so the paragraph after it starts flush. The desktop chat keeps its transcript setting, where every paragraph is indented. The fonts carry no small caps or old-style figures.
- **Street map.** Drawn in the same hairlines as the globe (0.8px, one ink, the same in light and dark), with its place names set in PP Neue Gstaad Regular. The map host serves only its own fonts, so the glyphs for the Latin ranges are generated from the font file and kept in `assets/glyphs/` (regenerate them if the font changes). The Building view button appears only on records with a street address.
- **Offline.** Installable as an app; the service worker caches the page.

Tiers describe how well a record is sourced, not a verdict on the museum: Clean (source cited), Flagged (a recorded reason), Unverified. See "What the page may show" below. Funding transparency ratings, A to F, summarize what each record shows about funding; see "Funding transparency ratings".

## Design

Plain CSS, no framework: one stylesheet at `assets/atlas.css` (design layer plus a short generated block of layout helpers) and `assets/maplibre-gl.css` for the street map. The page loads no CSS or script from a CDN.

The look follows the It's a book fair site: a white page, a strip of tabs on hairlines, flat colour blocks (cobalt, orange, cyan, mustard, periwinkle, magenta), a black pill for the current filter, a yellow close mark, and a grey sheet with the facts as a ruled table. The names of spaces are PP Neue Gstaad Compact (or Compressed) Bold in capitals; everything else, headings included, is PP Neue Gstaad Regular in normal case, at 14px or larger. No monospace anywhere. The globe is unchanged and sits on black. Text on a colour block is black, except on cobalt, where it is white.

The Details panel is the full record, with no separate record page on desktop; Share information sits in the chat composer and sends notes for review (see "Share information" below). On a desktop everything about a selected space, including what the building x-ray finds, is in the right column, not on the map.

---

## Run it locally

No build step and no dependencies. From the repository root:

```bash
python3 -m http.server 8080
```

Then open [http://localhost:8080](http://localhost:8080).

To try Share information against a local backend, run the Worker with `npx wrangler dev` in `worker/` and set `window.ATLAS_SUBMIT_URL` in `assets/config.js` to `http://localhost:8787` (local addresses are always allowed). The separate Prisma-backed whistleblower API is documented below.

---

## Using the chat

Open the chat, or press `Cmd+K` / `Ctrl+K`, and ask about a space, a city or a funder, for example "Which spaces in Tokyo are Clean?" or "What does the record for Te Papa say about funding?". An optional API key can be added under settings.

---

## Deploying

`main` is the source of truth. Every push to `main` runs
`.github/workflows/deploy.yml`, which copies `index.html`, `admin.html`,
`reports-admin.html`, `sw.js`, `manifest.json`, `assets/` and `fonts/` to the `gh-pages` branch that GitHub
Pages serves. Do not push to `gh-pages` by hand. If the live site looks stale,
check the **Actions** tab for a failed "Deploy to GitHub Pages" run.

## Share information: notes wait for approval

Share information sends a reader's note to a small backend, a Cloudflare Worker in `worker/` with one KV store. Every note is kept as waiting and shows nowhere until the editor approves it on `admin.html` (the review page, behind a password). There the text, the space it belongs to and a source link can be corrected before approving; a rejected note is deleted. An approved note appears on its space's record under "Shared by readers and approved by the editor", within a minute. No name, email or IP address is stored; the only trace of a sender is a salted hash of their address, kept for an hour to allow ten notes an hour.

While `window.ATLAS_SUBMIT_URL` in `assets/config.js` is empty, information and gossip notes stay in the reader's browser. Whistleblower reports are never saved locally: configure `window.ATLAS_REPORT_API_URL` to enable their database-backed submission, or the page will tell the reader that report service is unavailable.

### Prisma-backed whistleblower reports

The optional Express API stores whistleblower reports in SQLite with Prisma. Unlike the Worker note flow above, reports submitted through this API are not copied into browser storage. They remain private while pending, and approved reports are loaded into the matching institution record (or records in the same city when no institution was supplied).

From the repository root:

```bash
npm install
cp .env.example .env
```

Set `DATABASE_URL`, a long random `ADMIN_SECRET_KEY` (for example, generate one with `openssl rand -hex 32`), and `ALLOWED_ORIGINS` in `.env`. The API refuses to start if the admin secret is missing. Then initialize the database and start the API:

```bash
npm run db:push
npm start
```

Set `window.ATLAS_REPORT_API_URL` in `assets/config.js` to the API origin, for example `http://localhost:4000`. Whistleblower notes then use `POST /api/reports`; information and gossip notes keep using the existing Share information Worker/browser flow. The report moderation page is `reports-admin.html` and is linked from `admin.html`; it asks for the admin bearer token and does not embed a secret in the page. `admin/AdminModerator.jsx` provides the requested React moderation component for a React host. The API allows browser requests only from origins listed in `ALLOWED_ORIGINS`. The repository's GitHub Pages deployment serves static files only, so host this Node API separately and configure its public origin in `assets/config.js` before enabling submissions.

Setting it up once (free Cloudflare plan), in the Cloudflare dashboard, no install needed:

1. **Workers & Pages → Create → Worker**, name it `culture-atlas-submissions`, deploy the starter, then **Edit code**, replace it with `worker/index.js` and deploy.
2. **Storage & Databases → KV → Create**, name it `culture-atlas-submissions`.
3. In the Worker's **Settings → Bindings**, add a KV namespace binding called `SUBMISSIONS` pointing at that store.
4. In **Settings → Variables and Secrets**, add a secret `ADMIN_TOKEN` (the review page password; make it long) and a text variable `ALLOWED_ORIGINS` = `https://vasspolina.github.io`.
5. Copy the Worker's address (`https://culture-atlas-submissions.<you>.workers.dev`) into `assets/config.js` and push to `main`.

Or from a terminal: in `worker/`, `npx wrangler kv namespace create SUBMISSIONS`, paste the id into `wrangler.toml`, `npx wrangler secret put ADMIN_TOKEN`, `npx wrangler deploy`.

Review page: https://vasspolina.github.io/Culture-Atlas/admin.html. Tests for the Worker: `node --test worker/test/*.test.mjs`.

### Live Claude answers

With a model connected the chat holds a conversation: every question that is not a plain list of spaces goes to Claude, with the earlier turns of the chat and the records on the page as grounding. Without one, it answers from the records alone.

The same Worker serves it at `POST /chat`. The Anthropic key stays in the Worker and never reaches the browser.

1. In `worker/`, `npx wrangler secret put ANTHROPIC_API_KEY` and paste the key from console.anthropic.com. (In the dashboard: the Worker's **Settings → Variables and Secrets**.)
2. Put the Worker's address plus `/chat` in `assets/config.js`: `window.ATLAS_AI_PROXY_URL = 'https://culture-atlas-submissions.<you>.workers.dev/chat';` and push to `main`.

The Worker accepts only Claude Haiku 4.5 and Sonnet 4.5, caps a reply at 1,500 tokens and a conversation at 16 turns, refuses other origins than `ALLOWED_ORIGINS`, and gives each address 30 answers an hour. Raise or lower these at the top of `worker/index.js`. Every answer costs tokens on your Anthropic account.

## Money maps

The page opens on **one big map of every space and every sponsor** (`#all`): each space is a white circle, each sponsor a circle coloured by group (public bodies, corporate, foundations and donors), bigger the more spaces it funds, joined by a line for each tie. Tap a circle to light up its ties and zoom to them; search a sponsor in the second bar; filter the groups with the pills. Sponsors are merged across records by name (for example "NEA" and "National Endowment for the Arts"); public bodies are told apart by country, and generic ones such as "City government" stay with their own record so they never become one false hub. Records that name no funder are not in the big map. Two filters highlight part of the map and grey out the rest: **Mentions in the Epstein files** (33 spaces whose record has Epstein entries or an Epstein-linked flag, joined to the 23 people named in those entries; a space with only the flag is joined to Jeffrey Epstein) and **Right-wing funders**. The atlas records have no political field, so the second is a short curated list in `tools/build_money_maps.py` (`RIGHT`): only funders that appear in the records (as a sponsor or named in a record's own text) and have a published source for predominantly Republican or conservative giving, with that source shown in the panel. Currently Koch, Ken Griffin / Citadel, Ronald Lauder, Steven Cohen and Rebekah Mercer. It is not a complete list; add a name to it with a source, or remove one, and re-run the script. Each record also has its own map, at `money-maps.html#<record id>`.

`money-maps.html` is a second page, with its own `assets/money-maps.css` and `assets/money-maps.js`, and a local copy of d3 (`assets/d3.min.js`, v7.9.0, ISC licence). It loads nothing from a CDN. Its data is `assets/money-maps.json`, built from `institutions.json` by:

```bash
python3 tools/build_money_maps.py
```

The script reads each record's funding text, `funder_links`, flags and the Epstein and WikiLeaks fields into a list of circles, and links records that name the same funder. It fetches nothing and does not change any record. Funders are picked out of free text, so a name can be split or filed under the wrong group (government, corporate, foundation); the record itself stays the authority, and the page says so. Records that state no funder, flag or tie show an empty map with a note. Re-run the script after the data changes, as with `tools/embed_data.py`.

Controls: one finger or a mouse drag turns the map; two fingers or the scroll wheel fly forward and back; two-finger drag or Shift-drag slides; arrow keys turn it and W and S fly. Fit returns to the start. The page respects the device's reduced-motion setting.

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

Three **critical frames** on cultural institutions sit beside the artists' critiques on the records they speak to: the museum as archive turned stage, philanthropy as the gift that follows the taking, and art the powerful should fear. They are paraphrases of published theory and, by the editor's decision, the page names no author and shows no citation; the works each frame rests on are listed in `data/research_attach/institutional_critiques.json` under `rests_on`. `tools/attach_critiques.py` writes them (as `visual_critiques` entries of kind `theory`) by rules in that file: by name or focus and size, by funding transparency rating, or by host city; re-running replaces them. The chat answers "What do critics say?" and "What critics say about this space?".

The chat also answers "What do employees report?" with a summary of the 127 paraphrased accounts the records carry from Glassdoor, Kununu and Reddit (58 institutions, eight countries): what they praise, what they report against, what a few allege, and how to read them. It is the constant `EMPLOYEE_REPORT` in `index.html`, dated 17 October 2026; rewrite it when the accounts change.
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
├── index.html          # The whole app, edited in place. The only copy of the atlas page.
├── money-maps.html     # The money maps page (assets/money-maps.*, built by tools/build_money_maps.py)
├── admin.html        # Review page for notes sent with Share information
├── reports-admin.html # Moderation page for Prisma-backed whistleblower reports
├── worker/           # The submissions backend (Cloudflare Worker) and its tests
├── server/            # Optional Express API for whistleblower reports
├── prisma/            # Prisma schema and SQLite database (database file is ignored)
├── admin/             # Reusable React AdminModerator component
├── sw.js               # Service worker (network-first for the page, same-origin cache only)
├── manifest.json       # PWA manifest
├── assets/ fonts/      # atlas.css, maplibre-gl.css, images and the typefaces the page loads
├── institutions.json   # Dataset
├── data/               # Research sources, papers, corrections and the inputs behind the dataset
├── tools/              # Data pipeline: clean_data (which calls grade_funding), embed_data, build_money_maps, the importers and verify_claims
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
  "grade": 1,
  "grade_basis": "No flagged funder or objection on record, and figures are shown.",
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

## Funding transparency ratings

Each record with an independently sourced funder roster carries a rating from A to F, with no E (stored as 1 to 5), computed by `tools/grade_funding.py` at the end of `tools/clean_data.py`, from what the record proves and nothing else. A record whose funder roster is not independently sourced is unrated.

| Rating | Summary | Rule |
|---|---|---|
| A | Funding amounts disclosed; no funders flagged | No flag-category funder and no documented objection, and the record shows figures (amounts or shares in the funding text) or links accounts or a public registry filing |
| B | Funders listed; no funders flagged | The same, names only |
| C | Funder identified; details limited | A funder worth noting outside the flag categories, or a tie or objection with no flagged funder: Gulf state body, Epstein-linked, a campaigned name, a protest, a sponsor dropped, censorship |
| D | One flagged funder | One funder from a flag category: fossil fuels, tobacco, gambling, arms, opioids, sanctions, forced labour, prisons, a mining disaster |
| F | Multiple flagged funders, or a flagged funder with a disputed record | More than one flagged funder category, or a flagged funder plus a documented objection |

Public money alone is never a flag, so a wholly public museum sits at A or B. Disclosure only moves a record up, from B to A. The record shows the rating on its colour block with the sentence that decided it (`grade_basis`); the Layers panel has a Funding transparency ratings layer that fills each rated dot with its colour; the chat answers "What is its funding rating?", "Show grade A spaces in Berlin" and "How are spaces rated?".

## Verification & Methodology

- **Clean Status (Tier A)**: Institutions with no current fossil fuel, weapons/defense, opioid, tobacco, gambling, or sanctioned state sponsorship.
- **Data Cutoff**: Verified against annual reports, partner listings, and public disclosures up to late September 2026.
