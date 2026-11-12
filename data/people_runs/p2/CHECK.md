# Checker job (run p2)

Follow the section "The checker prompt" of /home/user/Culture-Atlas/data/people_prompt.md exactly.
Read the whole file first. Substitutions: DATE = 2026-11-12, WORKTREE = /home/user/Culture-Atlas,
RUN = p2, BATCH = the batch id you were given, BUDGET = 10 web searches.

Write data/people_runs/p2/check/<BATCH>.json and edit no other file. Use WebFetch and curl via Bash;
read PDFs with `pdftotext`. Keep downloads under /tmp/claude-0/people-p2-check-<BATCH>/ and delete
that folder before your final reply. Final reply under 100 words.
