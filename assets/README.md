# assets/

Everything `index.html` and the other pages load at runtime. The deploy workflow copies this folder
(with `fonts/`) to `gh-pages` as is, and `index.html`, `sw.js` and the other pages reference these files
by path, so keep names and locations stable. Several files are **generated** by `tools/` from
`institutions.json` and `data/`; edit the source and rerun the tool rather than editing them by hand.

| Group | Files | Notes |
|---|---|---|
| Look | `sheet.css`, `atlas.css`, `maplibre-gl.css` | `sheet.css` is the design; `atlas.css` is the layout underneath. See `docs/design.md`. |
| App scripts | `layers.js`, `desktop-maps.js`, `phone-maps.js`, `bubbles.js`, `funding-views.js`, `influence-mode.js`, `hq-detail.js`, `chat-resize.js`, `tab-suggest.js`, `intro-narration.js`, `typeset.js`, `subtopic.js`, `grounding.js`, `names.js`, `repeats.js`, `note-aids.js`, `note-files.js`, `analytics.js`, `reports-admin.js`, `config.js` | Hand-written. `config.js` holds the API addresses. |
| Artists' images | `critique-gallery.js`, `critique-captions.js`, `critique-stories.js`, `load-image.js`; folders `critique_gallery/`, `critique_additions/`, `visual_critique/` | Images are built by `tools/build_critique_gallery.py` and `tools/add_critique_images.py`. |
| Generated data | `institutions.js`, `money-maps.json`, `money-ids.js`, `influence.json`, `moma-influence.json`, `hq.json`, `sites.json`, `studies.json`, `funder-logos.json`, `funder-logos.png`, `live.json`, `live-stamp.json`, `critique-*-data.js`, `load-image-data.js` | Written by `tools/` (see `tools/README.md`). `live*.json` is rebuilt on every deploy and daily. |
| Map type | `glyphs/`, `icons/` | Glyph files for the street map; regenerate if the font changes. |
