# Researcher job (run p2)

Follow the section "The prompt" of /home/user/Culture-Atlas/data/people_prompt.md exactly, with its
"Who goes in", "What never goes in", method and house rules (not the checker prompt). Read that whole
file first. Substitutions: DATE = 2026-11-12, WORKTREE = /home/user/Culture-Atlas, RUN = p2,
BATCH = the batch id you were given, BUDGET = 18 web searches.

Read data/people_runs/p2/batches/<BATCH>.json and write data/people_runs/p2/out/<BATCH>.json. Edit no
other file. Use WebSearch, WebFetch and curl via Bash. tools/pdf_text.py needs macOS and does not run
here: read PDFs with `pdftotext -f FIRST -l LAST FILE -`. Keep downloads in one folder of your own
under /tmp/claude-0/people-p2-<BATCH>/ and delete it before your final reply; never download a file
over 20 MB. Write only what a page you opened states. Final reply under 100 words: the counts the
prompt asks for.
