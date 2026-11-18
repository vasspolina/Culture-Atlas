# Leaving it on the table

A globe and a chat for looking up who funds museums and cultural spaces. Each record shows what is stated about its funding and links to where that comes from.

**Live:** https://vasspolina.github.io/Culture-Atlas/

The full guide (what every feature does, the design rules, the data pipeline, the record schema, grading and methodology) is in [`docs/GUIDE.md`](docs/GUIDE.md).

## Quick start

The site is static: no build step and no dependencies. From the repository root:

```bash
python3 -m http.server 8080
```

Then open http://localhost:8080.

## Tests

```bash
npm install
npx prisma generate
npm test
```

`npm test` runs the site and data tests in `tests/` and the report API tests in `server/test/`. The chat proxy has its own tests: `node --test worker/test/*.test.mjs`. The same checks run on every pull request (`.github/workflows/test.yml`).

## Deploying

`main` is the source of truth. Every push to `main`, and a daily scheduled run, triggers `.github/workflows/deploy.yml`: it checks the records for repetition, rebuilds the latest-reports feed and publishes the site to the `gh-pages` branch that GitHub Pages serves. Never push to `gh-pages` by hand.

The report API (`server/`, `prisma/`) is deployed separately as a container (`Dockerfile`, `fly.toml`). The chat proxy (`worker/`) is a Cloudflare Worker (`worker/wrangler.toml`). See `docs/GUIDE.md` for both.

## Repository layout

```
.
├── index.html             The atlas: globe, map, chat and records (edited in place)
├── artists-images.html    Artists' images of cultural institutions
├── moma-money-map.html    The MoMA money map study
├── studies.html           Studies index
├── reports-admin.html     Moderation page for whistleblower reviews
├── sw.js, manifest.json   Service worker and app manifest
├── institutions.json      The dataset: one record per space
├── assets/                Styles, scripts, generated data and images the pages load
├── fonts/                 Typefaces the pages load
├── data/                  Research sources, research runs and inputs behind the dataset
├── tools/                 Data pipeline: importers, graders, builders and checks (Python and Node)
├── editor/                Local data editor for institutions.json (run tools/editor.py; not deployed)
├── server/, prisma/       Report API for whistleblower reviews (Express, Prisma, SQLite)
├── admin/                 React moderation component
├── worker/                Chat proxy (Cloudflare Worker)
├── tests/                 Site and data tests (node --test)
├── notes/                 Editorial rules and the daily-reports log
├── docs/                  The full guide
└── .github/workflows/     Deploy to GitHub Pages; tests on pull requests
```

The pages load files by these paths, and so do the service worker, the deploy workflow and the tools, so moving a top-level file means updating all of them.

## Configuration

Copy `.env.example` to `.env` to run the report API locally. `.env` is ignored by git; never commit it.
