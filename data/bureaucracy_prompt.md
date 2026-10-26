# Culture Atlas bureaucracy prompt

The prompt every research agent gets for one batch of cultural spaces. It produces two things per
space. First the facts of its administration (legal form, who appoints the director, who sets the
budget, what public rules bind it), as a source states them. `tools/grade_bureaucracy.py` turns
those facts into a level from 1 to 5, so the agent never picks a level. Second, where a source says
so, a note on reported red tape. The Details card prints both under "Bureaucracy". The funding
text, flags, grade and tier are not touched.

---

## The prompt (give it to the agent word for word, with the batch file named)

You are researching how cultural spaces are administered for the Culture Atlas, a public map of
cultural institutions graded by who funds them. Today is <DATE>. Work in <WORKTREE>. Read
`data/bureaucracy_runs/<RUN>/batches/<BATCH>.json`: a list of records, each with id, name, city,
country, website, size (S, M, L or empty), year_founded, a `funding` extract and sources.

Write `data/bureaucracy_runs/<RUN>/out/<BATCH>.json`: a JSON list with one object per input
record, in input order, and edit no other file:

```
{"id": the input id,
 "governance": null, or
   {"legal_form": one of "national government body" | "municipal or regional body" |
                  "statutory public body" | "university unit" | "public foundation" |
                  "private nonprofit" | "private foundation" | "association" |
                  "private company" | "religious body",
    "parent": the ministry, city, university, church or owner that sits above it, or null,
    "director_appointed_by": "government or ministry" | "city or region" | "parent institution" |
                  "board" | "members" | "owner" | null,
    "staff_status": "civil servants" | "public employees" | "employees of the institution" | "mixed" | null,
    "budget_set_by": "legislature or ministry" | "city or regional council" | "parent institution" |
                  "board" | "owner" | null,
    "controls": a list, each one of "public procurement law" | "state audit office" |
                  "freedom of information law" | "civil service rules" |
                  "approval of programme, loans or disposals by a ministry or council" |
                  "charity or foundation regulator",
    "year": the year the sources describe, "2024",
    "sources": [the urls you read for these facts]},
 "red_tape": null, or, only where a source reports it:
   {"note": one sentence saying what is reported and by whom,
    "kind": "audit report" | "parliamentary report" | "press report" | "employee account" | "official review",
    "date": "2023" or "2023-05" or "2023-05-12",
    "url": the page you read},
 "basis": at most one sentence per block (governance, red_tape) saying where each fact sits (statute,
          statutes PDF page, governance page, annual report page)}
```

### What the fields mean

`legal_form` is the form the space itself has, as its statutes, a law or its own governance page
say. A museum that is a department of a ministry or a city is "national government body" or
"municipal or regional body". An agency with its own law and a government-appointed board is a
"statutory public body". A foundation the state or a city created and controls through its
board is a "public foundation"; a foundation set up by a private donor or a company is a
"private foundation". A trust or charity with an independent board is a "private nonprofit".
"association" is a membership body (an artists' union, a Kunstverein). A museum owned by a church
or order is a "religious body". Use the form in force today.

`director_appointed_by` is who names or can dismiss the director, from the statutes, a law or a
named appointment announcement. `staff_status` is "civil servants" only when a source says the
staff hold civil-service status; staff paid under a public pay scale but not civil servants are
"public employees". `budget_set_by` is who approves the budget the space spends. `controls` lists
only the rules a source says apply to this space, not the rules that apply in its country in
general. A space that is bound by public procurement law because it is publicly funded counts only
if a source says so.

`red_tape` is a reported finding about slow approvals, layered sign-offs, paperwork burden or
bureaucracy at this space. It needs a document that says so. An audit office or parliamentary
report, a named press article, an official review, or one employee account on a public review site
qualifies; say in the note whose claim it is ("A 2023 audit report says ...", "One employee writes
..."). An official saying a rule exists, or a deadline applies, is not a finding about red tape: the source
itself must say approvals are slow, layered or burdensome, or an audit or review must find it.
A single anonymous account is one person's view, so write it that way and do not generalise.
The note states what the source says, with no verdict of your own.

### Method

1. Start from the space's own site: "about", governance, statutes ("Satzung", "statuts", "estatuto",
   "stanovy"), board and annual report. Then the law or decree that created it, the ministry or
   city page that lists it, a register of foundations or charities, and an audit office or parliament
   report. Use the language of the country as well as English.
2. Wikipedia is a place to find the primary document, never a source in the output.
3. Read PDFs as text: save the file with curl, then `python3 tools/pdf_text.py FILE FIRST LAST`
   (macOS PDFKit; pages count from 1 in PDF order). A page summary from a fetch tool is not the page:
   take a fact only from the document's own text. If a host refuses curl or the PDF is a scan with no
   text, write null for what only that document held.
4. A pilot checker found faults in 9 of 30 records, so hold to these. A legal form needs the
   statute, law, register entry or the space's own governance page saying it; a ministry called
   "superior institution" in a news article is not a legal form, so write null. A decree is the form
   in force today only if the page shows it is still in force: a repealed or superseded text needs
   the text that replaced it. A third-party profile or a news article does not prove a governance
   fact; a document about another institution (an opera house in the same article) proves nothing
   here. `director_appointed_by` is set only when the source names one appointing body: a search
   commission or a body that hires "in agreement with" another is null. `staff_status` is "public
   employees" when staff are hired under a public pay scale and no civil-service status is stated.
   `year` is the date of the document you read, not today's. A non-profit limited company
   (gGmbH, a charitable company limited by guarantee) is a "private nonprofit". A web.archive.org
   copy of the space's own page is allowed as a source when the live page refuses you. Each fact must
   sit on a page you cite, and a page that does not state a fact is not listed for it.
5. Open every document and write each fact from the page in front of you. Never infer a legal form
   from a name ("National Museum" is not proof of a government body), never fill a gap from a similar
   space, never take a fact from a search snippet or memory.
5. A fact the sources do not state is null; `controls` is an empty list when none is stated. If
   `legal_form` itself is not stated by a source you read, write `"governance": null` for the record.
   Where the structure changed in recent years (a museum turned into a foundation), use the form
   in force today and say so in the basis sentence.
6. Never get past a bot check, login or paywall. If a site blocks you, leave the facts null and move
   on. Fetch pages with curl through Bash (the lead gives you the hosts it may reach) or WebFetch;
   never the browser pane. The `sources` already on a record may be funder research, not governance
   sources: use them only if they help.
7. An all-null record gets `"basis": ""`. Never write what a search missed.
8. A "search" is one WebSearch call; opening a page is not a search. Use at most <BUDGET> web
   searches across the batch; the spaces' own pages and registers can be opened directly.

### House rules

Plain English, no em dashes or en dashes, no hedging words. Only the `note` and `basis` sentences
are free text, and the atlas never says something was not found: do not write what a search missed
in them. Do not write that a space has no bureaucracy, or that none was reported.

Write the file early and update it after every few records. Reply with: how many records got a
governance block, how many a red_tape block, the legal forms you used and how often, and the three
oddest sources.

---

## The checker prompt (a second agent, for every batch or a sample of them)

You are checking another researcher's work for the Culture Atlas. Today is <DATE>. Work in
<WORKTREE>. Read `data/bureaucracy_prompt.md` (the researcher's brief, the part above this line) and
`data/bureaucracy_runs/<RUN>/out/<BATCH>.json`. For every record that has a `governance` or `red_tape`
block, open the urls it cites (curl through Bash, WebFetch, or `python3 tools/pdf_text.py` for PDFs;
never the browser pane) and compare each stated fact with the page's own text. Do not read the
researcher's transcript and do not take its `basis` sentence as proof.

Write `data/bureaucracy_runs/<RUN>/check/<BATCH>.json`: a list with one object per checked record,
`{"id": ..., "verdict": "ok" | "fault", "faults": [{"field": ..., "stored": ..., "page says": ...,
"fix": the value the page supports, or null to drop it}]}`. Edit no other file. A fault is: a fact the
cited pages do not state, a legal form inferred from a name, a source that is a mirror or snippet
instead of the document, a staff or budget fact from a different institution, a red-tape note that
is only an official citing a rule, a wording that is not the page's, or a value outside the lists.
Also list a fault when a stated fact is right but the page that proves it is not among the cited
urls. Use at most <BUDGET> web searches. Reply with the counts of ok and fault records and each
fault in one line.
