# tests/

Node's built-in test runner, no extra dependencies. From the repository root: `npm test` (this folder plus
`server/test/`), or `node --test tests/*.test.mjs`. The page scripts in `assets/` are plain browser
scripts, so most tests load them into a `vm` context and call what they set on the global.

| Test | Checks |
|---|---|
| `art-periods.test.mjs` | Every art period rests on a sentence of its record, and every tie is a ledger tie. |
| `analytics.test.mjs` | `assets/analytics.js` is off without an address or when the browser says not to track. |
| `data-noise.test.mjs` | The records carry no broken links or empty points. |
| `editor.test.mjs`, `editor-structure.test.mjs` | The data editor (`tools/editor.py`, `editor/`): a save writes only the edited record. |
| `gossip-ahead.test.mjs` | In Gossip mode a money question is answered with the space's gossip first; gossip is upright; the 10% on the line height. |
| `gossip-kind.test.mjs` | A question about a kind of story is answered from the gossip data. |
| `gossip-place.test.mjs` | Gossip mode tells the stories of the place in view first: the space, its city, its country. |
| `gossip-told.test.mjs` | The retellings shown in Gossip mode (`told`) add no figure or quotation to their items, and show only while the mode is on. |
| `gossip-voice.test.mjs` | Gossip mode's voice: a journalist who claims no source of its own, read aloud in a woman's voice from the device. |
| `grounding.test.mjs` | The chat's grounding in the records. |
| `influence.test.mjs` | Influence mode shows only what `data/influence_review.json` keeps, plus the kept verdicts parked in `data/influence_review_unmatched.json`. |
| `live-feed.test.mjs` | `assets/live.json`: dated, sourced items only. |
| `name-request.test.mjs`, `names.test.mjs` | Matching a typed space or city name to a record. |
| `release.test.mjs` | The page reloads itself when its release differs from the live one. |
| `repeats.test.mjs` | A sentence is never shown twice. Also run by the deploy workflow. |
| `subtopic.test.mjs`, `tab-suggest.test.mjs` | Question topics and the Tab suggestion in the chat box. |
