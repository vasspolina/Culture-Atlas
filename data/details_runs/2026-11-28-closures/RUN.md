# Closures run, 28 Nov 2026

Question for each space in your batch file (`cN.in.json`): is it still running, and if not, when did it stop?

Write `cN.out.json` in this folder: a list, one object per space, in the batch's order:

    {"id": "...", "status": "closed" | "active" | "last_seen" | "unknown",
     "year": 2021,                      # closed: the year it closed. last_seen: the year of the latest dated activity found. active: the year of that activity
     "what": "one plain sentence, in your own words, of what the source says",
     "quote": "under 15 words copied from the page that carry the fact",
     "url": "the page you opened that says it",
     "source_kind": "own site" | "press" | "register" | "archive" | "social" | "other",
     "also": [ {"url": "...", "what": "..."} ]   # optional second source
    }

Rules. They are binding.
- `closed` only when a page you opened says in words that the space closed for good, was dissolved, liquidated, evicted with
  no new home, or ended its activity, and gives or implies the year. A closure for renovation, a move to a new address, a
  paused programme, a dead website or a quiet year is NOT closed. If it closed one venue and carries on elsewhere, it is active.
- `active` when a page you opened shows dated activity in 2026 (an exhibition, event or post dated 2026). Give that page.
- `last_seen` when you find no statement of closure and no 2026 activity: give the latest dated activity you could find
  (year, page). This is a "last seen" year. It is never a closing year and you must not turn it into one.
- `unknown` when you found nothing dated at all. Say what you tried in `what`.
- Never guess a year. Never infer closure from silence. No source, no claim.
- A company or charity register entry (dissolved, struck off, removed) is the end of the legal body, not of the space:
  report it with source_kind "register" and say in `what` that it is the legal body.
- At most 3 web searches per space, then open the best 1 to 3 pages. Use WebSearch and WebFetch (or curl). Do not use the
  browser pane or any browser tool. If a page will not open, try the Internet Archive copy
  (https://web.archive.org/web/2026/<url>) once, then move on.
- Check the space's own website first if it has one: a programme page with 2026 dates settles "active" in one fetch.
- Plain words. No hedging words, no dashes used as punctuation in `what`.
- Write only your own cN.out.json. Do not edit any other file. Do not run git.
