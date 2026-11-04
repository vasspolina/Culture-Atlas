# Leaving it on the table

A globe and a chat for looking up who funds museums and cultural spaces. Each record shows what is stated about its funding and links to where that comes from. Live: https://vasspolina.github.io/Culture-Atlas/

## What it does

- **Chat.** Laid out as a dialogue: set like an interview transcript: a two-letter speaker mark (ME, CA) in the margin wrapped lines hanging 1.6em in, and the first line of every paragraph, first or later, indented one em, your turns in green, one blank line between turns, no bubbles and no italics. Answers from the records only. It names the record and its source, and says when a record does not say. An optional API key in settings turns on open-ended replies.
- **Globe and map.** Click a space to see its record, or a city or country to filter. The globe is drawn in hairlines only (coastlines, borders, hollow rings for spaces) and fills its whole pane.
- **Money maps.** Each record has a map of what it states about its funding: the space in the middle, a circle for each funder, flag or documented tie, and lines between them. Circles that name the same funder link to other spaces. Open it from a record's Money map button, or go to `money-maps.html#<record id>`; `money-maps.html` on its own shows the big map of every space and sponsor. Drag to turn the map in 3D, pinch or scroll to fly through it, touch to make the circles sway. See "Money maps" below.
- **Typography.** Set after Jost Hochuli's *Detail in Typography*: kerning, ligatures and capital-height punctuation on; measure held to about 66 characters with a soft ragged right and no lone last words; leading rises with line length; tracking tightens as size grows; quotes, apostrophes, ellipses, en dashes and year ranges are corrected in the chat and the record by `assets/typeset.js`; acronyms are set a step smaller. Emphasis is set in Regular Italic. Bold and capitals are kept for one thing, the name of a space: the record's headline in Compressed Bold, the name on a map card, pop-up or street-map label and in a chat answer in Compact Bold, always in capitals. Every other heading and label is in the Regular, in normal case, and is told by its size and the space around it. In a record, the info text and the chat on a phone, the first paragraph of a run is flush and each one after it is indented one em, with no blank line; a source list or registry line is a break, so the paragraph after it starts flush. The desktop chat keeps its transcript setting, where every paragraph is indented. The fonts carry no small caps or old-style figures.
- **Street map.** Drawn in the same hairlines as the globe (0.8px, one ink, the same in light and dark), with its place names still set in PP Neue Gstaad Regular (the glyph files in assets/glyphs were made from it; the rest of the page is Jokker). The map host serves only its own fonts, so the glyphs for the Latin ranges are generated from the font file and kept in `assets/glyphs/` (regenerate them if the font changes). The Building view button appears only on records with a street address.
- **On a phone, like a maps app.** The globe fills the screen. The search and chat box floats over it at the bottom. A question typed there goes to the chat, the Chat button beside it opens the conversation where it was left, and its menu holds Gossip mode, Dark, Share information, Read answers aloud and New chat. The suggested questions sit over it as a row of chips that scrolls sideways. Layers is a round button at the top right that opens as a sheet from the bottom. A space's record is a sheet with three heights: peek, half and full. Peek holds the title and the description: for a space, its name, grade, place, the first three lines of its description and its actions; for a funder's record, its head (kind, name, place, source). It is set like a Google Maps place card: the name, a rating line (the funding grade's letter in a dot of its colour, with its words), the place, a row of pill actions with icons (the first filled), then tabs (Overview, Funding, Record, Sources) with the open one underlined; Overview lists the address, hours, admission and website as rows with an icon each. It follows the finger and snaps to the nearest height, a flick goes one height further, and a pull down from peek closes it. The map answers as a maps app does: drag to turn it, pinch to zoom, double-tap to zoom in where you tap, tap with two fingers to zoom out, and panning it lowers a half-open record to its peek. A location button at the bottom right flies to where you are and marks it with a blue dot. A Top story strip over the chips shows the newest dated report and opens a feed of the latest reports on the spaces, laid out after a news app: the top story with a poster block (kind and date, the space's name in capitals, its place and the report's status), the outlet, headline, when and where, what is said, the reply and outcome, a row of the sources and the status, and Share; then Near you (once the location is known) and Worldwide. It is built only from the dated items in each record's `gossip_data.gossip` and `case_notes` and follows `notes/gossip-criteria.md`: outside Gossip mode only what is confirmed or resolved, and the documented cases; in Gossip mode talk and denials too, each marked for what it is. On a phone the chat is part of the same app: a sheet over the map like the record, with a title, the map's ⋮ menu (Gossip mode, Dark, Share information, Read answers aloud, New chat) and one cross, the map's white pill as its composer, questions as rounded bubbles and the suggested ones as chips; the old bar across the top is gone. On a phone the record has one view: the sheet's tabs (Overview, Funding, Record, Sources) hold the whole record, sorted by subject, and the separate Full record page opens the sheet instead. The suggested questions follow the place: the visitor's city once the location button has found them, or the city the map is zoomed into. An alert now is the Top story, on the strip over the chips and at the head of the feed, with any other alerts after it. Alerts mark a protest, strike, dispute, allegation or similar at a space now (reported in the last 60 days and not resolved; outside Gossip mode only confirmed ones) with a red ring on the map and a section in the feed; Alert me sends a browser notification for a new one while the atlas is open. Every report says what kind of source it rests on and when the atlas last opened its links, and says outright when it is user-generated (anonymous posts, user reviews, the Personal accounts). Not every report is the press: the feed also carries the posts by staff and visitors on the records (Glassdoor, Reddit and the like), in a section of their own and marked user-generated and not verified, and the leaked documents on the records (WikiLeaks), with their dates. A staff or visitor post never raises an alert outside Gossip mode, and a document never does. The feed is checked every minute: `tools/build_live_feed.py` writes the records' dated, sourced items to `assets/live.json` and `assets/live-stamp.json` on every deploy, the page polls the stamp, and loads the new items without a reload. It is as current as the records, never ahead of them: an item reaches the page once the editor has checked it and it is deployed, and nothing without a date, a source address and a check date is shown (`tests/live-feed.test.mjs`). The box at the bottom asks and finds in one: a space's or a city's name on its own goes to the map, anything else to the chat, and with a conversation under way a tap on it goes back to the chat. The code is in `assets/phone-maps.js`, and the look is the "PHONE: MAPS APP" block at the end of `assets/atlas.css`.
- **Offline.** Installable as an app; the service worker caches the page.

Tiers describe how well a record is sourced, not a verdict on the museum: Clean (source cited), Flagged (a recorded reason), Unverified. See "What the page may show" below. Funding transparency ratings, A to F, summarize what each record shows about funding; see "Funding transparency ratings".

The Layers panel on the map has five boxes: **Funding connections** (one box for the lines between spaces that share a funder, flagged and right-wing funders, the funders around a space in focus and their head offices), **Epstein connections** (spaces whose funders or people appear in the files, and those people's offices), **Propaganda**, **Independent** and **Artist-run**. The records carry no field for the last two, so `assets/layers.js` reads each record's own words (summary, watch note, funding note, focus, name): "independent art space", "remains independent", "artist-run", "founded by artists" and the like. "Independently verified" or "independent audit" does not count.

## Design

Plain CSS, no framework: one stylesheet at `assets/atlas.css` (design layer plus a short generated block of layout helpers) and `assets/maplibre-gl.css` for the street map. The page loads no CSS or script from a CDN.

The look follows the It's a book fair site: a white page, a strip of tabs on hairlines, flat colour blocks (cobalt, orange, cyan, mustard, periwinkle, magenta), a black pill for the current filter, a yellow close mark, and a grey sheet with the facts as a ruled table. The names of spaces are Jokker Bold in capitals; everything else, headings included, is Jokker Regular in normal case, at 14px or larger. No monospace anywhere. The globe is unchanged and sits on black. Text on a colour block is black, except on cobalt, where it is white.

Contrast is measured, not assumed (WCAG 2.2: 4.5:1 for text under 24px, 3:1 for large text, UI components, focus rings and the marks that carry data). A mark is never told only by colour: a space's tier is a circle (clean), square (flagged) or triangle (unverified) on its pin and on its city and museum label; a funding grade is its letter inside the dot; funders on the money map are squares (public funding), hexagons (companies) and triangles (foundations); right-wing and Epstein-file marks are a shield and a star, the key shows each. On the white ground of light mode the pale layer colours are drawn as a deeper step of the same hue (`LINE_LIGHT` in `assets/layers.js`), and the pale originals stay as the fills of the name blocks, where the text on them is black. Around a space, each funder's name is a pill in the form of displaay.net/typefaces (fully rounded, a 1px edge, 10px of air either side): the name filled in its kind's colour, and the kind (Public funding, Company, Foundation) in an outlined pill beside it, on the outer side so the name stays next to its mark. The tip under the pointer is a stack of the same pills: the name in the mark's colour, what it is in outlined pills, and what a click does in a solid ink pill. The focus ring is `--focus` (cobalt on light, a lighter blue on dark).

**Buttons and corners after Displaay** (displaay.net/typeface/dazzed, 4 Nov 2026): every button is a rounded rectangle with 10px corners and a 1px ink edge, flat, no shadow, its label at 15px/1.3 +0.02em; the primary action is solid ink; what is chosen is solid ink; hover fills with 80% ink and paper text. Bars that hold buttons have 14px corners, panels, sheets and popups 20px. The shadows over the map are now the same 1px edge. "Ask the curator" is one line in one Displaay colour, a different one at each load. The record (Details) is set in Serrif Light (`fonts/Serrif-TRIAL-Light.woff2`, a Displaay trial file: check the terms before it ships for good), with section titles as small uppercase labels over a 1px rule. Titles stay on one line and are never cut: `fitTitles` in `assets/typeset.js` sets a long one smaller. Only the top and bottom edges of the map are fogged: they blur and fade into the paper, solid at the very edge and gone a quarter of the way in, on the globe and the street map alike, and the middle stays as it is ("FOG ON THE MAP" in `assets/atlas.css`). The selected space's label on the globe is set at 20px with its whole name. The card that opens over a space on hover is set like the info block on displaay.net/typeface/cassette: a paper card with a 1px ink edge and 20px corners, the place as a small uppercase label over a 1px rule, the name in capitals, the first line of the record's overview in Serrif Light 21px on a 24px line (up to three lines), and the website as a 10px-cornered button. The desktop chat column can be dragged wider by its left edge, up to full screen (double-click the edge to toggle; `assets/chat-resize.js`). The desktop map has no search box; the Top story badge is a newspaper. The rules are the "BUTTONS AND CORNERS: DISPLAAY" block at the end of `assets/atlas.css`.

The Details panel is the full record, with no separate record page on desktop; Share information sits in the chat composer and opens the form for a whistleblower review; the approved reviews of a place are listed at the foot of its record (see "Whistleblower reviews" below). On a desktop everything about a selected space, including what the building x-ray finds, is in the right column, not on the map.

---

## Run it locally

No build step and no dependencies. From the repository root:

```bash
python3 -m http.server 8080
```

Then open [http://localhost:8080](http://localhost:8080).

To try the Share information form against a local backend, run the report API (see "Prisma-backed whistleblower reports" below) and set `window.ATLAS_REPORT_API_URL` in `assets/config.js` to its local address; add the page's local origin to `ALLOWED_ORIGINS`.

---

## Using the chat

Open the chat, or press `Cmd+K` / `Ctrl+K`, and ask about a space, a city or a funder, for example "Which spaces in Tokyo are Clean?" or "What does the record for Te Papa say about funding?". An optional API key can be added under settings.

---

## Deploying

`main` is the source of truth. Every push to `main` runs
`.github/workflows/deploy.yml`, which copies `index.html`,
`reports-admin.html`, `sw.js`, `manifest.json`, `assets/` and `fonts/` to the `gh-pages` branch that GitHub
Pages serves. Do not push to `gh-pages` by hand. If the live site looks stale,
check the **Actions** tab for a failed "Deploy to GitHub Pages" run.

## Whistleblower reviews

The only notes the atlas holds are whistleblower reviews. They are written on one screen and read in one place.

**Writing:** Share information (in the chat composer, and on the map's control bar) opens the note screen, which is a form of filled blocks: the institution (the open record's, or chosen from the list of every space on the atlas), an optional name to show (blank shows "Whistleblower"), the note (10 to 2000 characters), and a box confirming that the sender has left out their name and anything that identifies them. Send for review is grey until the form could be sent and blue after; it posts to the report API. Enter inside the note starts a new line. If it cannot be sent, everything stays in the form and nothing is kept in the reader's browser. The page has no other way to add a note. There are no star ratings.

**Reading:** under the record of the space they are about, approved reviews are laid out like the reviews of a place on Google Maps: the count, then one entry per review with the name, date and text, newest first. The record only lists reviews; it has no form. Nothing is shown before they arrive or when there are none: no heading, no note on who writes them and no loading line (4 Nov 2026).

A review is sent to the report API below, held as waiting, and shows on the record only after the editor approves it on `reports-admin.html`. The map pin's hover card is drawn on the canvas and has no room for a list, so reviews appear on the record only. Reviews are not posted to Google Maps.

The Cloudflare Worker in `worker/` serves only the chat proxy (`/chat`). It takes no notes and no reviews; its setup is kept below.

### The report API (Express, SQLite and Prisma)

A review is stored as `PENDING` and is invisible to the public until it is approved. A review written before places had ids is matched to its place by name, so approved reviews already stored still show. A note that named only a city, which the old form allowed, no longer shows anywhere; its row stays in the database until the editor deletes it.

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

Set `window.ATLAS_REPORT_API_URL` in `assets/config.js` to the API origin, for example `http://localhost:4000`. The API reads `institutions.json` at start, so a review can be filed only under a record's id; keep it in the repository root where the API runs, or set `INSTITUTIONS_FILE` to its path. The API allows browser requests only from origins listed in `ALLOWED_ORIGINS`. The repository's GitHub Pages deployment serves static files only, so host this Node API separately and configure its public origin in `assets/config.js` before enabling submissions.

**Checks before anything is saved** (`server/validate.js`): the place comes from the address, `/api/places/<record id>/reviews`, and must be the id of a record in `institutions.json`; anything the body says about the place is ignored. The text is trimmed, HTML tags and control characters are removed, and it must be 10 to 2000 characters once cleaned. A rating sent by a client is ignored. The name to show, if sent, is plain text of at most 40 characters. Client-sent status, id and coordinates are ignored. Each sender may submit 5 reviews an hour (`REPORTS_PER_HOUR`); behind a proxy set `TRUST_PROXY=1` so the limit sees the sender and not the proxy. The limit is counted in memory under a salted hash of the address that is never written to the database or a log and disappears on restart. A database failure logs only its kind and code, never the request, so a review's text cannot reach the logs.

**What is stored:** the text, the place's id, name and city, the name to show if given, the status and two timestamps. No IP address, user agent, account or any other identifying data. The form tells the reader to leave out their name and anything that identifies them, because the connection itself is not a secure channel, and the editor checks the name to show before approving. The `latitude`, `longitude` and `rating` columns are never written; they remain only so an existing database needs no destructive change.

**Endpoints**

| Route | Who | What |
| --- | --- | --- |
| `POST /api/places/:placeId/reviews` | anyone | Validates and stores a `PENDING` review of that place |
| `GET /api/places/:placeId/reviews` | anyone | That place's approved reviews only (`id`, `authorLabel`, `content`, `createdAt`), newest first, at most 200; never cached |
| `GET /api/admin/reports?status=PENDING\|APPROVED\|REJECTED` | admin | Reviews in one state (`/api/admin/reports/pending` is kept) |
| `PATCH /api/admin/reports/:id/status` | admin | Set `APPROVED`, `REJECTED` or `PENDING` (takes a review off the atlas) |
| `DELETE /api/admin/reports/:id` | admin | Removes the review entirely |

Admin routes need `Authorization: Bearer <ADMIN_SECRET_KEY>`. The moderation page `reports-admin.html` asks for the token, keeps it in session storage only, and lists reviews, with the name each sender chose, under Waiting, On the atlas and Rejected, each with Approve, Reject or Take off the atlas, and Delete. `admin/AdminModerator.jsx` is the same page as a React component for a React host.

Tests: `npm test` (the API runs in-process against a throwaway SQLite file, so no port is opened; it covers validation, per-place listing, moderation, the rate limit and the logging rule). The Worker's tests are `node --test worker/test/*.test.mjs`.

#### Hosting the report API on Fly.io

The repository carries a `Dockerfile` and `fly.toml` for the API. The database is one SQLite file on a 1 GB Fly volume, so the app runs on a single machine. Once, from the repository root (install flyctl first: `brew install flyctl`, or see https://fly.io/docs/flyctl/install/):

```bash
fly auth signup            # or: fly auth login
fly launch --no-deploy --copy-config --name <a-free-app-name>
fly volumes create reports_data --size 1 --region ams
fly secrets set ADMIN_SECRET_KEY="$(openssl rand -hex 32)"
fly deploy --ha=false
```

`--ha=false` keeps the app on one machine, which SQLite needs. If the build stops at "Waiting for depot builder", stop it and run `fly deploy --ha=false --depot=false`. The live API is `https://culture-atlas-reports.fly.dev` (app `culture-atlas-reports`, region `ams`); its admin secret was generated into `~/culture-atlas-admin-secret.txt` on the editor's Mac. Later deploys after changing `server/`: `fly deploy` from the repository root.

Keep the secret: it is the password for `reports-admin.html`, and `fly secrets set` is the only place it is stored (print it once with `openssl rand -hex 32` before setting it if you want to keep a copy elsewhere). The API is then at `https://<app-name>.fly.dev`; `https://<app-name>.fly.dev/healthz` answers `{"ok":true}`. `fly.toml` already sets `ALLOWED_ORIGINS=https://vasspolina.github.io`, `TRUST_PROXY=1` (so the rate limit sees each sender, not Fly's proxy) and the database path on the volume. If you rename the app, update `app` in `fly.toml` to match.

Last step: set `window.ATLAS_REPORT_API_URL` in `assets/config.js` to `https://<app-name>.fly.dev` (no trailing slash), bump the release as usual, and merge through a PR. Then moderate at https://vasspolina.github.io/Culture-Atlas/reports-admin.html with the secret as the bearer token. Back up the database with `fly ssh sftp get /data/reports.db`.

### Live Claude answers

With a model connected the chat holds a conversation: every question that is not a plain list of spaces goes to Claude, with the earlier turns of the chat and the records on the page as grounding. Without one, it answers from the records alone.

What the model is given is written by `assets/grounding.js`. The record the question is about goes in full, in labelled sections (status, funding and audited figures, governance, overview, every reported case with its date and sources, employee and visitor accounts, critics and studies, visiting, sources), within a 14,000-character budget; the other records found for the question go in a 3,200-character form. A question about a city or country as a whole also gets a `<place_summary>`: the count, the grade tally, each flagged space with its reason, the funders named most and the largest audited incomes, counted on the page so the model does not count. Comparisons of places, a place asked about as a whole, employee accounts, critics and the reason for a grade go to the model first and fall back to the record answers when it is off or fails; plain lists and counts are always answered on the page. Tests: `node --test tests/grounding.test.mjs`.

The Cloudflare Worker in `worker/` serves it at `POST /chat`. The Anthropic key stays in the Worker and never reaches the browser. The Worker needs one KV namespace, bound as `SUBMISSIONS`, that holds only the hourly rate counters, and the variable `ALLOWED_ORIGINS` (`https://vasspolina.github.io`). From a terminal, in `worker/`: `npx wrangler kv namespace create SUBMISSIONS`, paste the id into `wrangler.toml`, then `npx wrangler deploy`. Tests: `node --test worker/test/*.test.mjs`.

1. In `worker/`, `npx wrangler secret put ANTHROPIC_API_KEY` and paste the key from console.anthropic.com. (In the dashboard: the Worker's **Settings → Variables and Secrets**.)
2. Put the Worker's address plus `/chat` in `assets/config.js`: `window.ATLAS_AI_PROXY_URL = 'https://culture-atlas-submissions.<you>.workers.dev/chat';` and push to `main`.

The page asks the Worker for Claude Sonnet 4.5 (`queryAI` in `index.html`; a visitor's own key uses the model chosen in settings). The Worker accepts only Claude Haiku 4.5 and Sonnet 4.5, caps a reply at 1,500 tokens and a conversation at 16 turns, refuses other origins than `ALLOWED_ORIGINS`, and gives each address 30 answers an hour. Raise or lower these at the top of `worker/index.js`. Every answer costs tokens on your Anthropic account.

## Studies

`studies.html` gathers the studies that read across many records: the Epstein cross-reference, what Democracy Now!,
Bellingcat and WikiLeaks show, Brazil's tax incentives, who connects the institutions (shared funders), small and
community-led spaces, who publishes what about their money, what the field says, the Tear Gas Biennial and MoMA.
They come from the Sponsor Atlas research page (its `CASES`) through `tools/build_studies.py`, which writes
`assets/studies.json` and links every institution a study names to its record (`./?inst=<name>`; an exact name wins).
`moma-money-map.html` is the interactive MoMA Money Map, kept here so the atlas is the one place it is published. Both
are linked from Map layers & legend, under Studies. Rebuild after each Sponsor Atlas import:
`python3 tools/build_studies.py`.

## Money maps

The page opens on **one big map of every space and every sponsor** (`#all`): each space is a white circle, each sponsor a circle coloured by group (public bodies, corporate, foundations and donors), bigger the more spaces it funds, joined by a line for each tie. Tap a circle to light up its ties and zoom to them; search a sponsor in the second bar; filter the groups with the pills. Sponsors are merged across records by name (for example "NEA" and "National Endowment for the Arts"); public bodies are told apart by country, and generic ones such as "City government" stay with their own record so they never become one false hub. Records that name no funder are not in the big map. Two filters highlight part of the map and grey out the rest: **Mentions in the Epstein files** (33 spaces whose record has Epstein entries or an Epstein-linked flag, joined to the 23 people named in those entries; a space with only the flag is joined to Jeffrey Epstein) and **Right-wing funders**. The atlas records have no political field, so the second is a short curated list in `tools/build_money_maps.py` (`RIGHT`): only funders that appear in the records (as a sponsor or named in a record's own text) and have a published source for predominantly Republican or conservative giving, with that source shown in the panel. Currently Koch, Ken Griffin / Citadel, Ronald Lauder, Steven Cohen and Rebekah Mercer. It is not a complete list; add a name to it with a source, or remove one, and re-run the script. Each record also has its own map, at `money-maps.html#<record id>`.

`money-maps.html` is a second page, with its own `assets/money-maps.css` and `assets/money-maps.js`, and a local copy of d3 (`assets/d3.min.js`, v7.9.0, ISC licence). It loads nothing from a CDN. Its data is `assets/money-maps.json`, built from `institutions.json` by:

```bash
python3 tools/build_money_maps.py
```

The script reads each record's funding text, `funder_links`, flags and the Epstein and WikiLeaks fields into a list of circles, and links records that name the same funder. It fetches nothing and does not change any record. Funders are picked out of free text, so a name can be split or filed under the wrong group (government, corporate, foundation); the record itself stays the authority, and the page says so. Records that state no funder, flag or tie show an empty map with a note. Re-run the script after the data changes, as with `tools/embed_data.py`.

Controls: one finger or a mouse drag turns the map; two fingers or the scroll wheel fly forward and back; two-finger drag or Shift-drag slides; arrow keys turn it and W and S fly. Fit returns to the start. The page respects the device's reduced-motion setting.

## Editing the page

`index.html` is edited directly. No script regenerates it. The records are not
in it: they live in `assets/institutions.js`, which `tools/clean_data.py` then
`tools/embed_data.py` rewrite from `institutions.json` (bump the `?v=` on its
script tag in `index.html` after a rewrite). Keeping them in their own file means a
new release of the page does not make every phone download the 10 MB of records
again, and the service worker caches them on their own. Everything else is
changed in the file itself.

A release is three numbers kept equal: `CACHE_NAME` in `sw.js`, `ATLAS_RELEASE`
in `index.html` and the `?v=` on the `sw.js` registration. If they drift apart,
every first visit reloads the page once before it draws.

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

The chat also answers "What do employees report?" with a summary of the 127 paraphrased accounts the records carry from Glassdoor, Kununu and Reddit (57 institutions, six countries): what they praise, what they report against, what a few allege, and how to read them. It is the constant `EMPLOYEE_REPORT` in `index.html`, dated 17 October 2026; rewrite it when the accounts change.
- `funder_links`: funders and trustees the map names at three or more
  institutions, only where the record's own text names them (230 links; 55
  where it does not are left out).

Notes saved in this browser are read back inside the chat ("Notes saved in this
browser" in the chat reply opens nothing).

## Gossip mode

Gossip mode shows what people are actually saying about a space on the internet: in the arts press, on Reddit, on accounts that collect staff complaints, in open letters, union statements and court filings, and in the comments under them. The rules for what counts, what never goes in, which sources are trusted and how an item is written are in `notes/gossip-criteria.md`; read them before adding anything.

The items live in `data/gossip_items.json`, one object each (schema in the rules, §4). `tools/attach_gossip.py` checks every item against the mechanical rules, marks `talk` items older than 36 months `stale`, drops rumours older than a year that no outlet picked up, and writes the rest onto the records as `gossip_data.gossip`, newest first; then `clean_data.py` and `embed_data.py` as usual. Re-running replaces the field. Items are reopened at least once a year; `retrieved_on` is the proof.

In Gossip mode the record page leads with the items (desktop: the Gossip row; phone: the cards at the top of the record), the globe marks a space with at least one item that is not stale, and the chat answers from the items first, naming who says each one and ending any item about a named person with the response line. The model gets them as the GOSSIP section of the grounding (`assets/grounding.js`) with the same instruction. Outside Gossip mode the items are not volunteered; asked directly, the chat answers from them with the same rules. Every gossip answer carries the line "Talk collected from the internet, with its sources. Unverified unless marked confirmed or resolved."

## What the page may show

The page shows what a record states and where it comes from, and says plainly that none of it has been independently verified.

- A field appears only if a record states it. Figures, hours, prices, exhibitions, architects and "chatter" are not generated to fill a gap. A text value shared by five or more records (after masking the name and city) is filler and is left out. Sentences that assert the absence of ties ("zero fossil fuel", "strict ethical charter") are left out.
- **Clean, source cited** needs at least one source outside the museum's own site. **Flagged** needs a recorded reason. Otherwise a space is **Unverified**.
- Anything reported about a space, such as a sponsor tie, an Epstein-related item, a WikiLeaks cable or a case file, is shown with its own source links.
- Anonymous staff reviews, the board network, the timeline, the filings registry, the itineraries and the generated 3D building interiors are not shown: they had no source, or were invented or generated. The building view draws only the outline OpenStreetMap holds for the building, through the map tiles, with the record's own material stacked inside it. Wikidata supplies only the building's photograph, with its credit, and the links to Wikidata and Wikipedia; its facts are not shown.

Rules live in `tools/clean_data.py`. To check records against their sources, run `tools/verify_claims.py` somewhere with network access, then `tools/apply_verification.py` and `tools/embed_data.py`. Wording corrected after checking is in `data/corrections.json`; the pilot of the three-check protocol is in `data/verification_pilot.json`.

## Project Structure

```
Culture-Atlas/
├── index.html          # The whole app, edited in place. The only copy of the atlas page.
├── money-maps.html     # The money maps page (assets/money-maps.*, built by tools/build_money_maps.py)
├── reports-admin.html # Moderation page for whistleblower reviews
├── worker/           # The chat proxy (Cloudflare Worker) and its tests
├── server/            # Express API for whistleblower reviews
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

Public money alone is never a flag, so a wholly public museum sits at A or B. Disclosure only moves a record up, from B to A. The record shows the rating on its colour block with the sentence that decided it (`grade_basis`); the map has no layer for the rating (removed 2 Nov 2026); the chat answers "What is its funding rating?", "Show grade A spaces in Berlin" and "How are spaces rated?".

## Verification & Methodology

- **Clean Status (Tier A)**: Institutions with no current fossil fuel, weapons/defense, opioid, tobacco, gambling, or sanctioned state sponsorship.
- **Data Cutoff**: Verified against annual reports, partner listings, and public disclosures up to late September 2026.
