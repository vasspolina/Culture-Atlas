# Design and editing the page

The sheet (look), the layout underneath, and how to change the page. Back to the [README](../README.md).

## Design

**The design is `assets/sheet.css`, and only that** (the sheet, user, 10 Nov 2026; "delete the other design version so there is no confusion and all changes done to new design", 13 Nov 2026). The atlas is set as one sheet: Times New Roman ("Atlas Serif", from the reader's machine, with Liberation Serif, Tinos and EB Garamond behind it) in two sizes, black on white, a lime stone bar at the head and the foot (#e2f86c), 1px grey rules between the columns, lists and actions that open with an en dash, no boxes, corners, shadows or bold. Under the pointer a word turns blue (#59a0f1); what is chosen (the open tab, a pressed toggle) is in italic and in that blue. Every rule in it is inside `@layer sheet` and `!important`, so it wins over `assets/atlas.css` whatever the selector. The head bar takes a new colour on every load (user, 16 Nov 2026): a pale ground from displaay.net/typefaces on the light sheet, a dark one on the dark sheet, picked by a short script after the theme script in `index.html` and drawn by the "COLOUR ON LOAD" block at the end of `sheet.css`. The filter pills have no ground and no dot: ink words inside an outline in each filter's own colour (user, 16 Nov 2026). Every name on the map (cities, spaces, the picked space, layer, funder and office names) is plain type with no block, pill or frame, on a halo of the map's ground, and is never cut short (user, 16 Nov 2026). No map dot glows (user, 16 Nov 2026): the halos under flagged, Epstein, right-wing, propaganda, independent and open-books marks are gone.

`assets/atlas.css` is the layout underneath: the panes, the map, the sheets on a phone, the order of things. Its own look (Jokker, the Displaay buttons and corners, Serrif in the record, colour blocks) is the earlier design and is not what anyone sees: do not add look to it or describe it as the design. **Every change to how the page looks goes in `sheet.css`.** New pieces are drawn there alone (the artists' images, the Images link and the load image have no rule in `atlas.css`). `index.html`, `studies.html`, `reports-admin.html` and `artists-images.html` all load `sheet.css`. `assets/maplibre-gl.css` styles the street map. No CSS or script comes from a CDN.

Contrast is measured, not assumed (WCAG 2.2: 4.5:1 for text under 24px, 3:1 for large text, UI components, focus rings and the marks that carry data). A mark is never told only by colour: a space's tier is a circle (clean), square (flagged) or triangle (unverified) on its pin and on its city and museum label; a funding grade is its letter inside the dot; funders on the money map are squares (public funding), hexagons (companies) and triangles (foundations); right-wing and Epstein-file marks are a shield and a star, the key shows each. On the white ground of light mode the pale layer colours are drawn as a deeper step of the same hue (`LINE_LIGHT` in `assets/layers.js`), and the pale originals stay as the fills of the name blocks, where the text on them is black. Around a space, each funder's name is a pill in the form of displaay.net/typefaces (fully rounded, a 1px edge, 10px of air either side): the name filled in its kind's colour, and the kind (Public funding, Company, Foundation) in an outlined pill beside it, on the outer side so the name stays next to its mark. The tip under the pointer is a stack of the same pills: the name in the mark's colour, what it is in outlined pills, and what a click does in a solid ink pill. The focus ring is `--focus` (cobalt on light, a lighter blue on dark).

Behaviour that holds whatever the look: titles stay on one line and are never cut (`fitTitles` in `assets/typeset.js` sets a long one smaller); only the top and bottom edges of the map are fogged; the selected space's label on the globe carries its whole name; there are no hover cards on the map (11 Nov 2026) except the Artists' images layer's, which shows only while that layer is on; the desktop chat column can be dragged wider by its left edge, up to full screen (double-click the edge to toggle; `assets/chat-resize.js`).

The Details panel is the full record, with no separate record page on desktop; Share information sits in the chat composer and opens the form for a whistleblower review; the approved reviews of a place are listed at the foot of its record (see [Whistleblower reviews](api.md)). On a desktop everything about a selected space, including what the building x-ray finds, is in the right column, not on the map.

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
