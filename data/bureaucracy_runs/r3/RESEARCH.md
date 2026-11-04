# Researcher job (run r3)

Follow the section "The prompt" of /Users/polinavasilyeva/culture-atlas/wt-bureaucracy-2/data/bureaucracy_prompt.md
exactly, with its method and house rules (not the checker prompt). Read that whole file first.
Substitutions: DATE = 2026-10-26, WORKTREE = /Users/polinavasilyeva/culture-atlas/wt-bureaucracy-2, RUN = r3,
BATCH = the batch id you were given, BUDGET = 14 web searches.
Read data/bureaucracy_runs/r3/batches/<BATCH>.json and write data/bureaucracy_runs/r3/out/<BATCH>.json.
Edit no other file. Use WebSearch, WebFetch and curl via Bash (if the sandbox refuses a curl host, retry
listing that host in allowed_domains); never the browser pane. WebFetch cannot read PDFs: use curl plus
`python3 tools/pdf_text.py`. Write only what a document you opened states. Final reply under 80 words:
the counts the prompt asks for.

Disk is scarce on this Mac: keep your downloads in one folder of your own under $TMPDIR, never download a file over 20 MB (read PDF pages from the first bytes you need or skip the source), and delete that folder before your final reply. Never delete anything else.

## Second pass

This batch holds spaces a first researcher could not place: no page it read stated a legal form. Do not repeat that search. Go registry-first: the national or regional register of companies, charities, foundations or associations (Companies House, Charity Commission, OSCR, ProPublica Nonprofit Explorer, Handelsregister or Stiftungsverzeichnis, KvK, Brønnøysund, ABN Lookup and ACNC, the corporate registries of the country), the law or decree that created a public museum, the ministry or city page that lists it as a unit, a statute PDF, and the Wayback copy of a page the live site blocks. The register must name this space or its operator, and a record whose only link is a similar name is null. If the space has no legal entity of its own (an event, a pavilion, a programme), the form is the organiser's only when a page says the organiser runs it. A null after a real registry search is a correct answer: write it and move on.
