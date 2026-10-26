# Checker job (run r3)

Follow "The checker prompt" at the end of /Users/polinavasilyeva/culture-atlas/wt-bureaucracy-2/data/bureaucracy_prompt.md.
Read that whole file first. Substitutions: DATE = 2026-10-26, WORKTREE = /Users/polinavasilyeva/culture-atlas/wt-bureaucracy-2,
RUN = r3, BATCH = the batch id you were given, BUDGET = 8 web searches.
Write data/bureaucracy_runs/r3/check/<BATCH>.json, one entry per record that has a governance or red_tape
block; a fault record carries the full `corrected` record. Edit no other file. If the sandbox refuses a
curl host, retry listing that host in allowed_domains; WebFetch cannot read PDFs. Final reply under 60 words:
how many ok, how many fault, and the faults in a few words each.

Disk is scarce on this Mac: keep your downloads in one folder of your own under $TMPDIR, never download a file over 20 MB (read PDF pages from the first bytes you need or skip the source), and delete that folder before your final reply. Never delete anything else.
