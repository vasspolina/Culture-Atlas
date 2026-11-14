# Gossip mode: the rules

Gossip mode shows what people are actually saying about a space on the internet: in the arts press, on Reddit, on Instagram accounts that collect staff complaints, in open letters, in union statements, in court filings and in the comments under all of them. It is talk, not findings. Every item on the map names where the talk was found and when, and the page says so next to it.

These rules decide what goes into `data/gossip_items.json`, how it is written, and how the chat and the record page use it. `tools/attach_gossip.py` applies the mechanical parts and refuses an item that breaks them.

## 1. What counts as gossip

An item is gossip when **all four** hold:

1. **It is about the space, or about a named public person in their role at the space**: a director, a trustee, a sponsor, a curator, an artist in the programme, a union, a contractor. The space's own announcements are not gossip; what people say about them is.
2. **Someone other than the space said it in public, on the internet**, at an address anyone can open. Private messages, screenshots whose origin cannot be opened, and "a friend who works there" do not count. Reddit, Instagram, X, Glassdoor, Kununu, open letters, union pages, the arts press and the general press all do.
3. **It is talk about conduct, money, power or drama**: who is leaving and why, who fell out with whom, which sponsor is being pushed out, what a leaked memo said, what staff complain about, what a lawsuit alleges, what the board did, what the artist withdrew over. A review of an exhibition is criticism, not gossip, unless it is about the institution's conduct.
4. **It has a date** (of the post, the article or the event), so it can age.

## 2. What never goes in

- Anything about a **private person**: a named front-of-house worker, a junior employee, an intern, a visitor. Staff talk is quoted by role or anonymously ("a former curator writes"), never by name, unless the person has put their name to it in public themselves (a signed open letter, a byline, a press statement).
- A public person's **health, sexuality, family, relationships, religion, immigration status, home address** or anything else about their life outside the role. Being a museum director does not make a divorce gossip for this map.
- **Children**, in any form.
- A claim that **only one anonymous account** makes, with nothing else pointing the same way. One Reddit comment is not an item. The same thing from two separate places (two threads, a thread and a review, a post and a press report), or from one account that is itself reported on by the press, is.
- A claim the source has **retracted or deleted**. If the post is gone and nothing else carries it, the item goes.
- **Allegations of a crime** against a named person unless they appear in a court filing, a regulator's decision, or a named news outlet's reporting. Reddit alone is not enough for that.
- Anything the editor cannot open and read at the address given. No item rests on memory.
- Dead links, archive-only copies of pages removed by their author, paywalled pages the editor has not read.

## 3. Sources, in the order they are trusted

| Rank | Source | How it is used |
| --- | --- | --- |
| 1 | Court filings, regulator decisions, charity-commission records, parliamentary questions | The item may state what the document says as fact, with the document's date. |
| 2 | Named reporting in the arts press (The Art Newspaper, ARTnews, Artnet, Hyperallergic, Museums Journal, Frieze, Monopol, Le Quotidien de l'Art, El País Cultura, NRC) and the general press (Guardian, NYT, FT, Le Monde, Tagesspiegel, Süddeutsche, de Volkskrant) | "X reported that…" with the outlet and date. The outlet is named in the text. |
| 3 | Open letters, union statements, campaign sites, petitions, the space's own published reply | Attributed to who signed it: "The PCS union says…", "An open letter signed by 300 artists says…". |
| 4 | Instagram accounts that collect staff accounts (@changethemuseum, @cancelartgalleries and the like), Reddit threads, X posts by named critics or journalists | "On Reddit, posters say…", "An account relayed on @changethemuseum says…". Always marked unverified. Never the only source for a claim of a crime. |
| 5 | Glassdoor, Kununu, Indeed reviews | Counted and summarised, never quoted by name; role and date only. These feed `gossip_data.accounts`, not this file, unless the press picks them up. |

Wikipedia is never a source. A blog is a source only when the author is named and reachable. A screenshot is not a source; the page it shows is.

## 4. How an item is written

Every item has these fields. The tool rejects an item missing any of the first seven.

| Field | Rule |
| --- | --- |
| `id` | `G` plus a number, unique in the file. Never reused after deletion. |
| `institution` | The record's `name` or `id` in `institutions.json`, exact. One item, one space; a story about two spaces is two items. |
| `headline` | One line, under 90 characters, in the present tense of what is being said: "Staff say the director's exit was not voluntary". Not a verdict. In the source's own register: a government that "scraps" a plan is not said to "kill" it. No violent or criminal verb (kills, axes, guts, slams, torpedoes, wrecks) unless it is quoted from someone on record; a crime word only as a court, prosecutor or regulator uses it. |
| `said` | What is being said, in two to four sentences, in reported speech. Starts with who says it. Dates inside the text. No adjectives the source did not use. The editor's own view does not appear. |
| `who_says` | One of: `press`, `court_or_regulator`, `union`, `open_letter`, `campaign`, `social_named` (a named person on social media), `social_anonymous` (Reddit, staff-complaint accounts, anonymous posts), `review_platform`, `institution` (the space's own reply, only ever as `response`). |
| `where` | The outlet, platform or document, as a reader would name it: "The Art Newspaper", "r/museumpros", "@changethemuseum", "Employment Tribunal judgment". |
| `when` | The date of the post, article or document: `YYYY-MM-DD`, or `YYYY-MM` when a day is not given. The event's date goes in `said`. |
| `urls` | One to four addresses, every one opened by the editor on `retrieved_on`. The first is the one the item rests on. |
| `kind` | `rumour` (nobody has put a name to it), `report` (a named outlet or document carries it), `allegation` (someone accuses someone), `dispute` (two sides on record), `departure` (a leaving or sacking), `money` (a sponsor, donor, grant or pay story), `leak` (an internal document made public). |
| `status` | `talk` (nothing confirmed), `denied` (the space or the person denied it, see `response`), `confirmed` (the space or a rank-1/2 source later confirmed it), `resolved` (there was an outcome; say it in `outcome`), `stale` (set by the tool, see §6). |
| `response` | What the space or the person said in reply, with its date and address, when there is one. An item about a named person with no reply recorded says so: "No reply found." |
| `outcome` | What happened next, if anything is on record. |
| `retrieved_on` | The day the editor last opened every address in `urls`. |
| `rule` | Which line of §1 and §3 the item passes under, in a few words: "§1 all; §3 rank 2 + rank 4". For the editor's own trail. |

The text is written for the map's reader, in English, in the same plain register as the rest of the records: no exclamation marks, no winks, no "allegedly" sprinkled as a charm. Reported speech does the work: "Posters on r/museumpros say…" is a true sentence whether or not what they say is true.

## 5. Named people

A named person appears only in their public role, only for what they are reported to have done in it, and only with a rank-1, rank-2 or rank-3 source for the naming. If the naming comes from rank-4 sources alone the item is written by role ("the then director").

Every item that names a person carries a `response` field, even if its content is "No reply found." When a person or the space asks for an item to be corrected or removed, the editor opens the sources again; if they still say what the item says, the item stays and the request is added to `response` with its date. If they do not, the item goes.

## 6. Age

Talk goes stale. The tool marks an item `stale` when `when` is more than 36 months before the run date and `status` is still `talk`; stale items stay on the record page under the fold and leave the chat's first answer. A `resolved` or `confirmed` item never goes stale: it is history. A `rumour` that has not been picked up by a rank-1 or rank-2 source within 12 months is deleted on the next pass, not marked.

Every item is reopened at least once a year; `retrieved_on` is the proof. An item whose first address no longer opens is reopened against the others; if none opens, it goes.

## 7. What the page does with it

- **The record page in Gossip mode** leads with the gossip items, newest first, each with its headline, `said`, who says it, where, when, the response, and its sources as links. Documented cases, Epstein and WikiLeaks records and the employee-account summary follow, as now. Items marked `stale` sit after them.
- **The globe** marks a space in Gossip mode when it has at least one item that is not stale, or anything the older `hasGossip` test already counted.
- **The chat in Gossip mode** answers from the gossip items first: the newest item's headline and `said`, with who says it and where, then the response when there is one, then the source host. It never adds a claim the items do not carry, never states a `talk` item as fact, and always ends a turn about a named person with the response line. A space with no items falls back to the documented cases and the watch line, as before. The model is given the items in a `GOSSIP` section of the grounding and told the same.
- **The chat outside Gossip mode** does not volunteer gossip. Asked directly ("what's the drama at X"), it answers from the same items with the same rules.
- Every gossip answer carries the line "Talk collected from the internet, with its sources. Unverified unless marked confirmed or resolved."

## 8. Removal

A request from a named person or a space goes to the editor by the report form. The editor replies within 14 days. The item is not taken down while the request is checked, but `response` gets the fact that a request was received and its date. The editor's decision and its date are added to `response` when made.

## 9. Record of changes

| Date | Change |
| --- | --- |
| 2026-11-02 | Rules written. First batch of items researched from the internet for the London, New York, Paris, Berlin, Amsterdam and Madrid spaces. |
| 2026-11-13 | Second batch, G190 to G251: 62 items for 52 spaces, most of them tier-A spaces that had none (UK and Ireland, North America, Western, Southern, Nordic and Eastern Europe, Asia-Pacific, Latin America and Havana, Africa, Israel), plus 2026 stories at the British Museum, V&A, Kennedy Center, LACMA and Brooklyn Museum. Every address opened on the day. Left out: boycott-signatory listings resting only on the campaign's own page, a complaint resting only on the complainant's site, a lawsuit resting on a docket mirror and the space's own release, a space's own funding warnings, and items that were not about conduct, money or power. |
| 2026-11-14 | Third batch, G252 to G472 (103 items, ids not continuous): the large spaces that had no item (North America, Western and Eastern Europe, Russia, the Gulf, Asia-Pacific, Latin America, Africa), and items for 47 well-known spaces that had no record until this day and were added with it. Every address opened on the day. Left out after review: a merger story with no dispute in it, a signed opinion column, a decree with nobody's objection on the opened pages, an undated page, a row that belonged to a biennial and not to its host, a ministry's reply on reopening dates, a corruption arrest attached to a space only by association, a labour-board listing with nothing else, a government pricing plan, a security contractor's shortfall, and three items from 2012 to 2021 that rested on one page. M+ was on the map twice; the thin record is folded into the full one (`data/duplicates.json`). |
| 2026-11-14 | Fourth batch, G500 to G662 (31 items, ids not continuous), for 99 more spaces that had no record and were added with it, each with a Details card (funding, controversies, and what is in the collection and the archive). The 47 spaces of the third batch got their Details cards the same day, and two of their items (G401, G412) got the outcome a reopened source gave. Left out after review: an item with a year but no month, three from 2012 to 2016 whose outcome could not be opened, talks between a government and another museum, a museum president's own reply to critics, and a director's own statement to parliament. |
