# Culture Atlas people prompt

The prompt every research agent gets for one batch of cultural spaces. It collects who leads each
space: the director (or the post that heads it under another name), the chief or head curator, the
artistic director, and for a small or artist-run space its founders who run it. For each person it
records the title as the source writes it, when they took the post, the posts they held before as a
source states them, and the page that says so. Where a director left the post since 1 January 2023,
the predecessor is recorded too, with the year they left and the reason only if a source gives one.

Nothing here is gossip. It is the public, professional record of a role: what the institution, an
appointment announcement, an annual report, a public filing or the arts press says about who holds
it. The rules on named people in `notes/gossip-criteria.md` section 2 apply in full.

`tools/build_people_batches.py` cuts the batches; `tools/merge_people.py` folds the checked
results into `data/people.json`. `institutions.json` is not touched by this prompt.

---

## The prompt (give it to the agent word for word, with the batch file named)

You are researching who leads cultural spaces for the Culture Atlas, a public map of cultural
institutions graded by who funds them. Today is <DATE>. Work in <WORKTREE>. Read
`data/people_runs/<RUN>/batches/<BATCH>.json`: a list of records, each with id, name, city, country,
website, size (S, M, L or empty), year_founded, and `known`: the sentences the atlas record already
holds that name a director, curator or founder (they may be out of date, and they are not a source).

Write `data/people_runs/<RUN>/out/<BATCH>.json`: a JSON list with one object per input record, in
input order, and edit no other file:

```
{"id": the input id,
 "people": [
   {"name": the person's name as the source writes it, without honorifics or letters after it
            (no Dr, Professor, Sir, Dame, OBE, CH): "Mark Sealy", not "Professor Mark Sealy OBE",
    "role": one of "director" | "co-director" | "artistic director" | "chief curator" |
            "curator" | "founder" | "chair of the board",
    "title": the job title in the source's own words, in its own language if not English,
             "Generaldirektorin", "Executive Director and Chief Curator",
    "current": true, or false for a predecessor,
    "since": "2021" or "2021-09", the year (and month if stated) they took this post, or null,
    "until": null while current; for a predecessor the year (and month) they left,
    "left_because": predecessors only: "retired" | "term ended" | "moved to another post" |
                    "resigned" | "dismissed" | "died" | null; set only when a source says it,
    "next_post": predecessors only: the post they moved to, as a source states it, or null,
    "previously": up to three earlier posts, each "Title, Institution (2015 to 2021)", in the
                  order the source gives them; [] when no source states any,
    "pay": null, or only from a public filing or annual report:
           {"amount": 245000, "currency": "USD", "year": "2023", "what": "total compensation",
            "url": the filing}; "amount" is a number. Where the filing gives a band (UK
           annual reports print "360 to 365" thousand), "amount" is the low end and
           "amount_to" the high end, both in whole units: 360000 and 365000,
    "sources": [the urls you read that state this person's name in this post]}
 ],
 "basis": one sentence: where the people were found (the space's team page, a 2024 appointment
          press release, the 2024 annual report page 3), or "" when people is []}
```

### Who goes in

1. **The head of the space**, whatever it is called: director, general director, executive
   director, president and CEO, Intendant, directeur, directora, conservateur en chef when that post
   runs the museum. A space run by two people as equals gets two "co-director" entries. Exactly one
   head is `current` unless the post is vacant; a vacant post with an interim holder takes the
   interim, with "interim" or "acting" kept in `title`.
2. **Who runs the programme**, where that is a separate post: artistic director, chief curator,
   head of curatorial, director of collections and exhibitions. One or two people, not the whole
   curatorial staff. A small space with one named curator takes that curator as "curator".
3. **Founders** only when a founder still runs the space or the space is artist-run and its own
   site names its founders as the people behind it. A founder who died or left long ago is not
   listed.
4. **The chair of the board** only when a source names the chair on the same page as the head or
   in the annual report you already opened. Do not go looking for boards.
5. **One predecessor**: the previous head, only when they left the post on or after 1 January
   2023. Their `left_because` and `next_post` come only from a source that says so. A predecessor
   who left earlier is not listed.

At most six people per space. Junior curators, assistant curators, educators, registrars,
front-of-house staff, interns and anyone the source names only in a staff list below the
leadership are not listed, whatever the page shows.

### What never goes in

Anything outside the role: age, date or place of birth, nationality unless the source makes it
part of the appointment ("the first woman to"... is the source's sentence, not a field), health,
family, partners, religion, politics outside the post, home address, personal email, personal phone
number, private social media. A work email or phone number is not collected either: the atlas links
to the space's own contact page. `previously` holds posts, not degrees, prizes or exhibitions they
made. `pay` is filled only from a document the law makes public for that institution: a US Form 990
(ProPublica Nonprofit Explorer), a UK charity's accounts, a Dutch WNT disclosure, a German or Austrian
public body's published pay, an annual report that prints it. Never from a press estimate or a salary
site.

### Method

1. Start from the space's own site: "about", "team", "staff", "who we are", "Leitung", "équipe",
   "equipo", "chi siamo", "organisation", and the press releases that announce appointments. Then
   the annual report, the ministry or city page that names the head, the register of charities or
   companies (directors are listed there for small spaces), then the arts press (The Art Newspaper,
   Artforum, ARTnews, Artnet, Monopol, e-flux announcements, the national press). Use the language of
   the country as well as English.
2. The space's own current page is the best source that someone holds a post now. An announcement
   is the best source for `since`, but the date of an announcement is not the start date: `since`
   takes the month only when a page says the person started (or would start) that month, else the
   year alone. An undated page proves no date. A news article older than 18 months does not prove someone is
   still `current`: confirm on the space's site, a page dated in the last 18 months, or leave the
   person out. If the site and a newer article disagree, the newer dated source wins and the basis
   sentence says so.
3. Wikipedia and LinkedIn are places to find a primary page, never a source in the output. A search
   snippet is not a source: open the page.
4. Read PDFs as text: save the file with curl in a folder of your own under the scratchpad, then
   `python3 tools/pdf_text.py FILE FIRST LAST` if it works on this machine, or `pdftotext -f FIRST -l
   LAST FILE -`. If neither reads it, leave out what only that document held.
5. Check every `known` sentence: if the person still holds the post, list them with a source you
   opened; if someone else holds it now, list the new holder, and the one in `known` as the
   predecessor only if they left on or after 1 January 2023.
6. Write each name, title and date from the page in front of you. Never fill a gap from a similar
   space, from memory or from a name that "must" be right. A spelling the sources disagree on takes
   the space's own spelling. Write names and titles in normal case even where a filing prints them in
   capitals ("Nathalie de Gunzburg", "Chief Executive Officer", not "NATHALIE DE GUNZBURG").
7. Never get past a bot check, login or paywall. If a site blocks you, try its web.archive.org copy
   (allowed as a source, with the capture date in `basis` when it is older than 12 months), then move
   on. Fetch with curl through Bash or WebFetch.
8. A space with no person you could source gets `"people": []` and `"basis": ""`. Never write what
   a search missed.
9. A "search" is one WebSearch call; opening a page is not a search. Use at most <BUDGET> web
   searches across the batch; the spaces' own pages can be opened directly.

### House rules

Plain English, no em dashes or en dashes in `basis` (write "2015 to 2021" in `previously`). Only
`basis` is free text. Write the file early and update it after every few records. Reply with: how
many records got at least one person, how many people in total by role, how many predecessors, how
many `pay` entries, and the three records you are least sure of and why.

---

## The checker prompt (a second agent, for every batch or a sample of them)

You are checking another researcher's work for the Culture Atlas. Today is <DATE>. Work in
<WORKTREE>. Read `data/people_prompt.md` (the researcher's brief, the part above this line) and
`data/people_runs/<RUN>/out/<BATCH>.json`. For every person listed, open the urls cited for them
(curl through Bash or WebFetch) and compare the name, title, `current`, `since`, `until`,
`left_because`, `next_post`, `previously` and `pay` with the page's own text. Do not read the
researcher's transcript and do not take its `basis` sentence as proof.

Write `data/people_runs/<RUN>/check/<BATCH>.json`: a list with one object per record,
`{"id": ..., "verdict": "ok" | "fault", "faults": [{"person": ..., "field": ..., "stored": ...,
"page says": ..., "fix": the value the page supports, or null to drop it}], "corrected": only for a
fault record: the whole record object (`id`, `people`, `basis`) as it should be stored, every faulty
value fixed or dropped, every other value copied unchanged}`. Edit no other file.

A fault is: a fact the cited pages do not state; a person shown `current` on a page older than 18
months with nothing newer; a predecessor who left before 2023; a junior staff member; anything from
"What never goes in"; a `pay` figure not from a public filing or annual report; a source that is
Wikipedia, LinkedIn, a snippet or a mirror; a role outside the list. Also list a fault when a fact is
right but the page that proves it is not among the cited urls. Use at most <BUDGET> web searches,
spent on checking `current` where the cited page is old. Reply with the counts of ok and fault
records and each fault in one line.

---

## Record of runs

| Run | Date | Batches | Notes |
| --- | --- | --- | --- |
| p2 | 2026-11-12 | 90 (every remaining space, 16 to a batch) | Full run as four workflows, a checker on every batch: 1,326 records passed, 103 corrected. The session's web-search allowance ran out near batch 18, so later batches worked from pages opened directly and leave more spaces empty. 1,019 spaces merged. North Korea (44) and Cuba (`.cu` hosts do not resolve here) are nearly all empty. A predecessor with no leaving year is kept only when a current head started in 2023 or later (`settle_predecessors`). |
| p1 | 2026-11-12 | 3 (pilot: Berlin, London, New York; 36 spaces) | 35 spaces and 90 people merged. Checkers passed 28 records and corrected 8: a start date sourced to an undated page, capitals copied from Form 990s, a start month that was the announcement's, ENB's two leaders as co-directors, and one chair dropped whose only page would not open. Added pay bands (`amount_to`) and honorific stripping at merge. |
