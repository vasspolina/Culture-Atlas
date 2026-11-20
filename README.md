# Leaving it on the table

A globe and a chat for looking up who funds museums and cultural spaces. Each record shows what is stated about its funding and links to where that comes from. Live: https://vasspolina.github.io/Culture-Atlas/

## Run it locally

No build step and no dependencies. From the repository root:

```bash
python3 -m http.server 8080
```

Then open [http://localhost:8080](http://localhost:8080).

To try the Share information form against a local backend, run the report API (see [docs/api.md](docs/api.md)) and set `window.ATLAS_REPORT_API_URL` in `assets/config.js` to its local address; add the page's local origin to `ALLOWED_ORIGINS`.

## Project Structure

```
Culture-Atlas/
├── index.html          # The whole app, edited in place. The only copy of the atlas page.
├── money-maps.html     # The money maps page (assets/money-maps.*, built by tools/build_money_maps.py)
├── reports-admin.html # Moderation page for whistleblower reviews
├── worker/           # The chat proxy (Cloudflare Worker) and its tests
├── server/            # Express API for whistleblower reviews
├── prisma/            # Prisma schema and SQLite database (database file is ignored)
├── editor/            # The data editor for institutions.json (run tools/editor.py; not deployed)
├── sw.js               # Service worker (network-first for the page, same-origin cache only)
├── manifest.json       # PWA manifest
├── assets/ fonts/      # atlas.css, maplibre-gl.css, images and the typefaces the page loads
├── institutions.json   # Dataset
├── docs/               # Feature, design, API, data and deploy documentation
├── data/               # Research sources, papers, corrections and the inputs behind the dataset (see data/README.md for what every file is)
├── tools/              # Data pipeline: clean_data (which calls grade_funding), embed_data, build_money_maps, the importers and verify_claims
└── .github/workflows/  # Deploy to gh-pages on push to main
```

## Documentation

| Doc | Covers |
|---|---|
| [docs/features.md](docs/features.md) | What the atlas does: chat, globe and map, money maps, studies, influence and gossip modes |
| [docs/design.md](docs/design.md) | The design sheet, layout rules, and how to edit the page |
| [docs/api.md](docs/api.md) | Whistleblower reviews, the report API, the Claude chat proxy |
| [docs/data.md](docs/data.md) | Dataset schema, what the page may show, ratings, verification, the data editor |
| [docs/deploying.md](docs/deploying.md) | Deploying to GitHub Pages |
| [data/README.md](data/README.md) | Every research file behind the dataset |
| [tools/README.md](tools/README.md) | The data pipeline scripts |
