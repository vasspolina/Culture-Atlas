# Researcher job (run r2)

Follow the section "The prompt" of /Users/polinavasilyeva/culture-atlas/wt-bureaucracy/data/bureaucracy_prompt.md
exactly, with its method and house rules (not the checker prompt). Read that whole file first.
Substitutions: DATE = 2026-10-26, WORKTREE = /Users/polinavasilyeva/culture-atlas/wt-bureaucracy, RUN = r2,
BATCH = the batch id you were given, BUDGET = 14 web searches.
Read data/bureaucracy_runs/r2/batches/<BATCH>.json and write data/bureaucracy_runs/r2/out/<BATCH>.json.
Edit no other file. Use WebSearch, WebFetch and curl via Bash (if the sandbox refuses a curl host, retry
listing that host in allowed_domains); never the browser pane. WebFetch cannot read PDFs: use curl plus
`python3 tools/pdf_text.py`. Write only what a document you opened states. Final reply under 80 words:
the counts the prompt asks for.

Disk is scarce on this Mac: keep your downloads in one folder of your own under $TMPDIR, never download a file over 20 MB (read PDF pages from the first bytes you need or skip the source), and delete that folder before your final reply. Never delete anything else.
