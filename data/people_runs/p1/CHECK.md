# Checker job (run p1)

Follow the section "The checker prompt" of /home/user/Culture-Atlas/data/people_prompt.md exactly.
Read the whole file first. Substitutions: DATE = 2026-11-12, WORKTREE = /home/user/Culture-Atlas,
RUN = p1, BATCH = the batch id you were given, BUDGET = 8 web searches.

Write data/people_runs/p1/check/<BATCH>.json and edit no other file. Use WebFetch and curl via Bash;
read PDFs with `pdftotext`. Keep downloads under /tmp/claude-0/people-p1-check-<BATCH>/ and delete
that folder before your final reply. Final reply under 100 words.
