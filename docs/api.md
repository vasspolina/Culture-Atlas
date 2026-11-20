# Reports API and live answers

Whistleblower reviews, the Express/Prisma report API and the Claude chat proxy. Back to the [README](../README.md).

## Whistleblower reviews

The only notes the atlas holds are whistleblower reviews. They are written on one screen and read in one place.

**Writing:** Share information (in the chat composer, on the map's control bar, and as a button under every chat answer, named after the place in focus, with one sentence on how much of history was never written down; user, 18 Nov 2026) opens the note screen, which is a form of filled blocks: the place (the open record's, chosen from the list of every space on the atlas, or a place the atlas is missing: a name it does not have shows a City or town field and a line saying it goes to the editor as a new place), an optional name to show (blank shows "Whistleblower"), the note (10 to 2000 characters), and a box confirming that the sender has left out their name and anything that identifies them. Send for review is grey until the form could be sent and blue after; it posts to the report API. Enter inside the note starts a new line. If it cannot be sent, everything stays in the form and nothing is kept in the reader's browser. The page has no other way to add a note. There are no star ratings.

**Writing aids** (`assets/note-aids.js`, under the note box): the browser's own spell check underlines mistakes, and phone keyboards correct as usual. "Correct spelling as I type" (on by default for an English browser, remembered in that browser) fixes common misspellings and missing apostrophes when a word is finished (teh, recieved, musuem, thats, dont), writes a lone "i" as "I", and starts a sentence with a capital. It leaves links, addresses, abbreviations such as "e.g." and words with capitals of their own alone. Backspace straight after a correction puts the reader's spelling back, and that word is not corrected again. "Dictate" (in browsers with speech recognition) types what the reader says into the note at the cursor; it never sends the note. The first press says where the audio goes: Chrome, Edge and Safari send it to Google, Microsoft or Apple to turn it into text, unless the browser can do it on the device (Chrome 139 and later, when the language pack is installed), which is then used and said. No note text is sent anywhere to be checked.

**Attached files** (`assets/note-files.js`): Attach, a drop onto the note card, or a paste of an image into the note adds photos, screenshots or PDFs, up to 4 files of at most 5 MB each and 12 MB together. Each shows as a chip above the note box with a button to take it off. Photos are drawn again in the browser before they are sent (at most 2560 pixels on the long side; a screenshot stays PNG while it is small enough, anything else becomes a JPEG), which leaves only the picture: the camera, time and GPS position a phone writes into a photo do not survive, and the line under the chips says so. A photo the browser cannot read, such as a HEIC photo in Chrome, is refused with a reason. A PDF is sent as it is, and the form warns that its document properties can hold the name of whoever made it. No file name is sent. If the note cannot be sent, its files stay attached.

**Reading:** under the record of the space they are about, approved reviews are laid out like the reviews of a place on Google Maps: the count, then one entry per review with the name, date and text, newest first, and under the text the files the editor approved with it: photos as square thumbnails, a PDF as a "Document" link, each opening the file in a new tab. The record only lists reviews; it has no form. Nothing is shown before they arrive or when there are none: no heading, no note on who writes them and no loading line (4 Nov 2026).

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

**Checks on files** (`server/files.js`): the review route alone takes a body of up to 18 MB, since files arrive as base64 inside the JSON (`files: [{ data }]`); every other route keeps a 16 KB limit. At most 4 files, each at most 5 MB and 12 MB together. The type is read from the file's first bytes, and only JPEG, PNG, WebP and PDF pass; a name or type the client sends is ignored. Photos go through a second metadata pass on the server: EXIF, XMP, comments and every other metadata block are removed from JPEGs (the JFIF header, an ICC colour profile and Adobe's colour block stay), text, EXIF and time chunks from PNGs, and EXIF and XMP from WebP. A PDF must end with `%%EOF` and is stored as sent. A review with a file that fails any check is refused whole and nothing is stored.

**New places** (user, 18 Nov 2026): `POST /api/new-places` takes `placeName` (2 to 120 characters), `city` (up to 80), an optional `address` (up to 200; added 19 Nov 2026), the note and files under the same checks and rate limit as a review. A name the atlas already has (compared without case, accents or punctuation) is refused with 409 and that record's id. It is stored as `kind: "new-place"` with no `placeId`, is never shown as a review, and is marked on `reports-admin.html`, where approving it means the editor accepts it and adds the place to the atlas data by hand. Reviews are `kind: "review"`.

**What is stored:** the text, the place's id, name and city, the name to show if given, the status, two timestamps, and any files (their bytes after the metadata pass, type, size and order, in the `ReportFile` table of the same SQLite file; no file name). No IP address, user agent, account or any other identifying data. The form tells the reader to leave out their name and anything that identifies them, because the connection itself is not a secure channel, and the editor checks the name to show before approving. The `latitude`, `longitude` and `rating` columns are never written; they remain only so an existing database needs no destructive change.

**Endpoints**

| Route | Who | What |
| --- | --- | --- |
| `POST /api/places/:placeId/reviews` | anyone | Validates and stores a `PENDING` review of that place |
| `GET /api/places/:placeId/reviews` | anyone | That place's approved reviews only (`id`, `authorLabel`, `content`, `createdAt`, `files: [{ id, type, size }]`), newest first, at most 200; never cached |
| `GET /api/files/:fileId` | anyone | One file, only while its review is `APPROVED` (404 otherwise); sent with `nosniff`, and an image with a sandboxing `Content-Security-Policy` |
| `GET /api/admin/reports?status=PENDING\|APPROVED\|REJECTED` | admin | Reviews in one state (`/api/admin/reports/pending` is kept) |
| `PATCH /api/admin/reports/:id/status` | admin | Set `APPROVED`, `REJECTED` or `PENDING` (takes a review off the atlas) |
| `DELETE /api/admin/reports/:id` | admin | Removes the review and its files entirely |
| `GET /api/admin/files/:fileId` | admin | One file, whatever the state of its review |
| `DELETE /api/admin/files/:fileId` | admin | Removes one file and keeps the review |

Admin routes need `Authorization: Bearer <ADMIN_SECRET_KEY>`. The moderation page `reports-admin.html` asks for the token, keeps it in session storage only, and lists reviews, with the name each sender chose, under Waiting, On the atlas and Rejected, each with Approve, Reject or Take off the atlas, and Delete. The files of each note are shown under its text, loaded with the token, each with Remove file, so the editor can approve the text and keep a file that identifies someone off the atlas. `admin/AdminModerator.jsx` is the same page as a React component for a React host.

Tests: `npm test` (the API runs in-process against a throwaway SQLite file, so no port is opened; it covers validation, per-place listing, files and their metadata pass, moderation, the rate limit and the logging rule). The Worker's tests are `node --test worker/test/*.test.mjs`.

#### Hosting the report API on Fly.io

The repository carries a `Dockerfile` and `fly.toml` for the API. The database is one SQLite file on a 1 GB Fly volume, so the app runs on a single machine. Attached files are stored in that file too; when it fills, grow the volume with `fly volumes extend <volume id> --size <GB>`. Once, from the repository root (install flyctl first: `brew install flyctl`, or see https://fly.io/docs/flyctl/install/):

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

### Live model answers

With a model connected the chat holds a conversation: every question that is not a plain list of spaces goes to the model, with the earlier turns of the chat and the records on the page as grounding. Without one, it answers from the records alone.

What the model is given is written by `assets/grounding.js`. The record the question is about goes in full, in labelled sections (status, funding and audited figures, governance, overview, every reported case with its date and sources, employee and visitor accounts, critics and studies, visiting, sources), within a 14,000-character budget; the other records found for the question go in a 3,200-character form. A question about a city or country as a whole also gets a `<place_summary>`: the count, the grade tally, each flagged space with its reason, the funders named most and the largest audited incomes, counted on the page so the model does not count. Comparisons of places, a place asked about as a whole, employee accounts, critics and the reason for a grade go to the model first and fall back to the record answers when it is off or fails; plain lists and counts are always answered on the page. Tests: `node --test tests/grounding.test.mjs`.

The Cloudflare Worker in `worker/` serves it at `POST /chat` and answers with a small open model on Workers AI: IBM Granite 4.0 H Micro (`@cf/ibm-granite/granite-4.0-h-micro`, 3B parameters, 131,000-token context), since 18 Nov 2026. There is no API key: the Worker reaches the model through its `AI` binding and Workers AI bills the Cloudflare account: 10,000 Neurons a day are free (about 250 questions at the size of the page's grounding), and more than that needs the Workers Paid plan, at $0.017 per million input tokens and $0.112 per million output tokens. The Worker also needs one KV namespace, bound as `SUBMISSIONS`, that holds only the hourly rate counters, and the variable `ALLOWED_ORIGINS` (`https://vasspolina.github.io`). From a terminal, in `worker/`: `npx wrangler kv namespace create SUBMISSIONS`, paste the id into `wrangler.toml`, then `npx wrangler deploy` (the `[ai]` block in `wrangler.toml` adds the binding). In the dashboard: the Worker's **Settings → Bindings → Add → Workers AI**, variable name `AI`. Tests: `node --test worker/test/*.test.mjs`.

Put the Worker's address plus `/chat` in `assets/config.js`: `window.ATLAS_AI_PROXY_URL = 'https://culture-atlas-submissions.<you>.workers.dev/chat';` and push to `main`.

The Worker uses its one model whatever the page names (`queryAI` in `index.html` still sends a Claude model id, which only a visitor's own key uses). It caps a reply at 2,000 tokens and a conversation at 16 turns and 150,000 characters, refuses other origins than `ALLOWED_ORIGINS`, and gives each address 30 answers an hour. Change the model or these limits at the top of `worker/index.js`; Llama 3.1 8B and Llama 3.2 3B were passed over because Workers AI retires them on 20 Nov 2026.
