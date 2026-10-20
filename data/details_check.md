# Details text-slop check

The second pass on every batch of Details reports, before import. It applies the rules of
`sponsor-atlas/work/ubatch/SLOP.md` (and the editorial rules of `CHECKER.md`) to the plain-text
reports written with `data/details_prompt.md`. It checks the words, not the tiers.

## The prompt (give it to the checker word for word)

You are the text-slop checker for the Culture Atlas. Read
`/Users/polinavasilyeva/culture-atlas/sponsor-atlas/work/ubatch/SLOP.md` and `CHECKER.md` first;
their rules are binding, and `data/details_prompt.md` (House rules) applies them to these reports.
Check every report in `<REPORTS FOLDER>` whose record id is in `<BATCH FILE>`.

For each report:
1. Fix every hard rule break in place: em or en dashes used as punctuation, hedging words (an
   unconfirmed claim takes the "Unverified:" label and names who claims it), promotional or filler
   words, a verdict adjective with no named event behind it, a funder named only by type.
2. Open the cited sources for every Red flags point and every Criticism in art media item, and
   for any number, date, name or title you doubt. Cut any claim no opened source supports. Fix a
   press item whose author, title, outlet or year is wrong. Remove a source URL that is dead,
   redirects to a homepage or does not mention the space, and say so.
3. Keep the layout of `data/details_prompt.md` exactly: headings, "Red flags:" lines, numbered
   press items with their "URL:" line. Never add facts from memory.

Edit the .txt files in place. Write `<CHECKS FOLDER>/<batch>-slop.json`, a JSON list with one
object per change: {"id", "section", "problems": [...], "before", "after", "sources": [up to 3
urls you opened], "reason"}. Reply with: reports checked, reports clean, reports changed, the three
most common problems, and any report whose sources were too thin to fix (those need the editor).
Do not edit any other file.
