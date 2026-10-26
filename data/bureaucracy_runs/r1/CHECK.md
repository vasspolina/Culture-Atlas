# Checker job (run r1)

Follow "The checker prompt" at the end of /Users/polinavasilyeva/culture-atlas/wt-bureaucracy/data/bureaucracy_prompt.md.
Read that whole file first. Substitutions: DATE = 2026-10-26, WORKTREE = /Users/polinavasilyeva/culture-atlas/wt-bureaucracy,
RUN = r1, BATCH = the batch id you were given, BUDGET = 8 web searches.
Write data/bureaucracy_runs/r1/check/<BATCH>.json, one entry per record that has a governance or red_tape
block; a fault record carries the full `corrected` record. Edit no other file. If the sandbox refuses a
curl host, retry listing that host in allowed_domains; WebFetch cannot read PDFs. Final reply under 60 words:
how many ok, how many fault, and the faults in a few words each.
