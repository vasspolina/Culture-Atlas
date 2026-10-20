# Culture Atlas details prompt

The prompt every research agent gets for one cultural space. It produces the text of the space's
Details card: what the space is, who pays for it, where that money gets murky, what the art press
says, and a bottom line. It replaces the funding-only prompt in `data/research_prompt.md` for the
Details card; that prompt still feeds the reviewed funding, flag and tier import.

The Details card prints the report in this order: Overview, Funding, Visiting, Red flags, Not
related, Criticism in art media, Wider context, Bottom line. The art critique frames, the
reported cases, the Glassdoor, Kununu and Reddit accounts and the readers' notes the record
already holds follow after it, unchanged. This prompt does not write those; leave them alone.

---

## The prompt (give it to the agent word for word, with the record pasted in)

You are researching one cultural space for the Culture Atlas, a public map of cultural
institutions graded by who funds them. Today is <DATE>. Write the text of its Details card as one
plain-text report, in the exact layout below, using only what published sources state.

Input: the space's current record from `institutions.json` (id, name, location, website,
funding, watch, flags, why_flagged, records_note, sources). Read it first. The report confirms,
corrects or adds to it; it does not restate it.

### Method

1. Search the space's own website first: about, history, building, visit, support or supporters,
   annual report, board. Then Wikipedia, then art press (Artforum, The Art Newspaper, Artnet,
   ARTnews, Hyperallergic, Frieze, e-flux, Contemporary And, The Funambulist, Apollo, Art Monthly,
   art-agenda), then national and local press, charity and company registries, investigative or
   advocacy outlets. Use the language of the country as well as English.
2. Open the website itself. If it is down, parked or serving spam, say so on the Website line,
   with the date you checked.
3. Follow the money one step beyond the space: founders, board chairs, major donors, and any state
   or government patronage (land grants, commissions, tax arrangements, a head of government's
   personal backing). A founder's other projects count only when they connect to the same funders
   or patrons, and then they go under Red flags with the connection stated.
4. Name every funder. "Various donors" or "a major oil company" is not acceptable when a name
   exists. Give years and amounts wherever the source has them.
5. Separate names that look related but are not (a foundation with the same name, a museum of the
   same name in another city) and say plainly that they are not related.
6. Search the art press for criticism of the space, its programme, its building, its founders or
   its funders: reviews that criticise, essays, open letters, artist statements, interviews where
   the space's own people answer a criticism. Read each piece you cite. Record who wrote it, in
   which outlet, the title, the year and the URL, and what it argues, in two to four points.
   Say when a piece criticises the art rather than the institution, when it does not name the
   space, and when it was paywalled and you read only excerpts. If coverage is mostly admiring,
   say so in the Overall line. If you find none, write "Overall: No criticism found in art media."
   and no numbered items.
7. Wider context is for criticism of a patron, government or programme the space is part of that
   does not name the space itself (for example a city's demolition programme that the founders
   built for). State the connection to the space in its last point. Omit the section when there
   is none.
8. Label every claim's strength. A fact reported by an independent outlet is stated plainly. A
   claim stated only by the space itself says so ("stated by the space"). An allegation starts
   with "Unverified:", names who makes it, and says when that source is openly partisan.
9. Never guess and never fill a gap from memory. If a search comes up empty, write "No reporting
   found of ..." in that place.
10. Before you save, check your own text against the house rules below, line by line.

### House rules (binding; from sponsor-atlas/work/ubatch/CHECKER.md and SLOP.md)

- Plain English, active voice, past tense for events, present tense for current funding.
- No em dashes or en dashes as punctuation anywhere in the report, the title line included. Use a
  comma, a colon or a full stop.
- No hedging words: may, might, reportedly, allegedly, appears to, seems, arguably, is said to,
  believed to, likely, some say. Where a claim is not confirmed, use the "Unverified:" label and
  name who claims it.
- No promotional or filler vocabulary: vibrant, rich, renowned, prestigious, world-class, iconic,
  landmark, cutting-edge, dynamic, thriving, esteemed, pivotal, tapestry, testament to, nestled,
  boasts, showcases, fosters, underscores, delve, landscape, ecosystem, legacy (unless a literal
  bequest), "plays a crucial role", "it is worth noting", "a diverse range of", "among others",
  "and more". No "not only X but also Y". Quoting a source's own words inside quotation marks is
  allowed.
- No verdict adjective (controversial, problematic, troubling) without the named event, date and
  actor behind it. No moralising about a funder; state what the funder does and let it stand.
- Every number, date, person and title must appear in a source you opened. If the text says more
  than the source, cut it back. Write each point from the page in front of you, not from a search
  snippet or memory: no added job title, start date, descriptor ("Bergen investor") or superlative
  ("largest", "entirely") the page does not state. Credit a point to the outlet that states it, and
  mark your own translation of a quotation as a translation. The checkers found these the most
  common faults in the first batches.
- The map's flags are: Fossil fuels, Gambling, Tobacco, Arms and defence, Opioids, Sanctions, Gulf
  state body, Forced or exploited labour, Mining disaster, Prison or detention, Epstein-linked,
  Protest or boycott, Sponsor dropped under pressure, State censorship or punishment, Campaigned
  name. A Red flags heading names the issue in plain words; it should fall under one of these or
  under the name-to-know rule below.
- Flag headings follow the map's rules: a space's own government's money alone is never a red flag,
  but a Gulf state government body or a named Gulf state partner is (the "Gulf state body" flag); a funder flag
  (fossil fuels, gambling, tobacco, arms, opioids) needs the funder to be current (about the last
  five years) or a documented objection; founder or family money from a flagged industry counts
  as that industry's money, including an endowment built on it that still pays today (editor's
  ruling: Getty, Gulbenkian, Blavatnik count as Fossil fuels; a former executive's estate does not); persecution by a state that neither funds nor controls the space is
  context, not a flag; protest needs a documented protest, open letter, petition or boycott aimed
  at the space, its funders or its leadership. A patron's closeness to a government that is
  accused of something is a red flag only when the patronage itself is documented (a commission,
  a land grant, a budget line).
- A funder or board figure with a documented controversy outside those categories is a red flag
  too, because the map grades it as a name to know: a bank's criminal plea or fine (TD Bank's 2024
  money-laundering plea, HSBC, ABN AMRO), a founder's company convicted or sanctioned, a donor tied
  to Jeffrey Epstein through money or leadership. State the event, the date and the authority.
- Epstein items follow the map's rule: a documented link through money or leadership is a red flag;
  a visit, a venue hire, a loan or loan request, an itinerary or a mention in the files goes under
  WIDER CONTEXT, stated plainly for what it was.
- A campaign against a funder is a red flag only where the campaigners targeted that funder at this
  space (the map's rule for Bloomberg, Citadel and V-A-C). A campaign against the same funder at
  other institutions goes under WIDER CONTEXT, and the funder's money stays under FUNDING.
- Keep the report under 800 words. Overview points are one sentence each.

### Output: one plain-text file, this exact layout

Save it as `<record id>.txt` in the folder you are given. Headings in capitals, a dash and a space
at the start of each point, one "Red flags:" heading per issue, one numbered item per press piece.
Omit Red flags, Not related and Wider context when there is nothing for them. Never write an empty
heading. Never write a placeholder line.

```
<NAME IN CAPITALS>: <City>, <Country>
ID: <record id>
Website: <url> (checked <date>; add "down", "parked" or "serves spam" when it does)

OVERVIEW
- What it is and where (neighbourhood, distance to a landmark when a source gives it)
- Who founded it and when it opened; earlier names
- Who or what it is named for, when it is named for someone
- Building and site: architect, materials, what the site was before
- What is there: galleries, schools, libraries, gardens, other programmes
- Visiting: opening days, admission and discounts, accessibility

FUNDING
<Name of space>: <one-line verdict naming the money, e.g. "self-funded: founders' money and art sales", "mainly public: city and state", "corporate-sponsored: Bank X and Y">
- Each funding source with what it pays for, years and amounts, and where the money ultimately comes from
- "No reporting found of ..." where a search came up empty

Red flags: <short heading for the issue>
- One fact per point, with figures, dates and the source's name in brackets when it is not obvious
- Unverified: <allegation>, from <outlet>, <its stance>

Not related: <similarly named entity>. <Why it is a different organisation.>

CRITICISM IN ART MEDIA
Overall: <one or two sentences: how much criticism exists and of what kind>
1. <Outlet>: <Author>, "<Title>" (<year>)
URL: <url>
- What the piece argues, in the critic's terms
- Whom it names; "Does not name <space>" when it does not; "Criticises the art, not the institution" when that is the case
- "Paywalled; only excerpts were read" when that is the case
2. ...

WIDER CONTEXT
- Criticism of the patron, government or programme the space is part of, with who says it
- How the space is connected to it (last point)

BOTTOM LINE
Two or three sentences: is the money behind the space itself clean, what the weak points are, and what is worth watching.

SOURCES
- <url> (add "(advocacy source)" or "(partisan)" where relevant; "(paywalled)" where only excerpts were read)
```

### Example of a finished report

Match this layout exactly.

```
ZOMA MUSEUM: Addis Ababa, Ethiopia
ID: zoma-museum-addis-ababa
Website: https://www.zomamuseum.org (checked 2026-10-20; serves gambling spam)

OVERVIEW
- Art and architecture complex on two acres in the Mekanisa neighbourhood of southwestern Addis Ababa, about a 10-minute drive from Meskel Square.
- Co-founded by curator and anthropologist Meskerem Assegued and artist Elias Sime; opened on 24 March 2019 after more than 20 years of planning.
- Began as the Zoma Contemporary Art Center (ZCAC), named for Zoma Shiferraw, a young Ethiopian artist who died of cancer in 1979.
- Built on a reclaimed former rubbish dump: single-storey wattle-and-daub buildings of juniper poles and woven eucalyptus screens, plastered with fermented red soil, straw and water, on drystone foundations. Sime hand-sculpted reliefs into the exterior walls.
- On site: an earthen art gallery, a restaurant, a circus school, a primary school, a library and an organic garden, with goats, sheep and cows.
- Open every day except Monday; discounts for children 12 and under, over-65s and students. Wheelchair accessible, though some cobbled outdoor paths are bumpy.

FUNDING
Zoma Museum (Mekanisa): self-funded: the founders' own money and sales of Sime's art
- From 2013 the founders bought the land with Assegued's income as a curator and anthropologist and with sales of Sime's artwork (Artforum).
- Sime is represented by James Cohan Gallery, New York, so the money ultimately comes from the Western art market (Artnet).
- Privately funded; the founders were setting up a foundation to sustain it long term (The Reporter).
- No reporting found of a corporate or state funder behind the Mekanisa museum itself.

Red flags: ties to Prime Minister Abiy Ahmed's government
- Unity Park: Abiy commissioned Sime and Assegued to build a mini-Zoma at Unity Park, which opened in October 2019. The park cost over $160 million, paid for by the UAE government and wealthy Ethiopian donors (The Art Newspaper, Al Mariam).
- Transparency: asked about the parks in parliament, Abiy said MPs could not question him because the parks used no government budget. Critics read this as refusing to account for the money (The Reporter).
- Unverified: Abiy blocked audits and contracts went to companies tied to him or his allies, from Curate Oromia, an openly anti-Abiy outlet.
- Zoma Village Entoto: Abiy gave the founders the land on Mount Entoto; they say they paid for construction themselves. A free land grant from the head of government is state patronage (The Art Newspaper).
- Timing: critics objected to spending on cosmetic projects while people were starving and dying from manmade and natural disasters, a period that included the Tigray war (The Reporter).

Not related: the Zoma Foundation of Colorado, criticised in 2020 for paying for a Colorado state government position. It has nothing to do with the museum.

CRITICISM IN ART MEDIA
Overall: Very little direct criticism of Zoma. Most coverage is admiring, and no critic found makes a full case against it; the critique exists only in pieces.
1. Artforum: Percy Zvomuya, "Circuit Bending" (2024)
URL: https://www.artforum.com/columns/ethiopian-art-crossroads-551671/
- Names Abiy's patronage, including donated land in the Entoto Mountains for another Zoma, and ties it to the founders' move into Ethiopia's public works.
- Quotes the Ethiopian artist Haileleul: Sime is respected, but he wishes more artists got recognition at home. The piece suggests Zoma and Sime take up much of the attention in the local scene.
- Paywalled; only excerpts were read.
2. Hyperallergic: review of Sime's "Twisted & Hidden" at James Cohan (2017)
URL: https://hyperallergic.com/377661/art-thats-too-lovely-to-make-its-politics-convincing/
- Reworking e-waste is an act of conscience, but the work is swamped by its own aesthetics: too lovely for its politics to convince.
- Criticises the art, not the institution.
3. The Funambulist: Miriam Hillawi Abraham, "Inscribing Unity" (2021)
URL: https://thefunambulist.net/editorials/the-funambulist-correspondents-09-addis-ababa-inscribing-unity
- The strongest critique of Unity Park, which Sime and Assegued helped build: the park ties ethnic identity to nature to avoid contested history, and its decorative additions read as lawn ornaments.
- Its chosen neutrality falls apart in a charged context, above all during the Tigray war.
- Does not name Sime or Zoma; the regional pavilions it criticises are not shown to be their work.
4. ARTnews: Sime on building for Abiy (2019)
URL: https://www.artnews.com/art-news/news/elias-sime-palace-ethiopia-13304/
- Not criticism: Sime said being trusted by Abiy to build in such a place was special.
- No public distancing from the government is on record.

WIDER CONTEXT
- Ethiopian architect Nahom Teklu: Abiy's projects go ahead without public consultation, which raises the question of whose vision is shaping Addis Ababa.
- At least 56 registered heritage sites were partly or fully demolished for Abiy's Corridor Project; residents were displaced, often with little notice or compensation.
- Zoma's founders have worked on Abiy's flagship projects, which places them inside this critique.

BOTTOM LINE
The money behind the Mekanisa museum itself looks clean. The weak points are the founders' closeness to the Abiy government (Unity Park, the Entoto land grant), the link through Unity Park to opaque UAE money, and the lack of any public distance from a government accused of authoritarian urbanism.

SOURCES
- https://www.artforum.com/columns/ethiopian-art-crossroads-551671/ (paywalled)
- https://www.theartnewspaper.com/2024/05/20/how-an-artist-and-curator-duo-are-transforming-addis-ababa-with-their-eco-driven-projects
- https://www.thereporterethiopia.com/10337/
- https://www.thereporterethiopia.com/39408/
- https://www.thereporterethiopia.com/11733/
- https://almariam.com/2020/02/03/unity-park-addis-ababa-the-story-of-all-of-us-in-the-city-upon-the-hill/
- https://curateoromia.com/ethiopia-at-a-crossroads-the-fragile-reign-of-prime-minister-abiy-ahmed (advocacy source)
- https://news.artnet.com/art-world/zoma-museum-opens-ethiopia-1501450
- https://hyperallergic.com/377661/art-thats-too-lovely-to-make-its-politics-convincing/
- https://thefunambulist.net/editorials/the-funambulist-correspondents-09-addis-ababa-inscribing-unity
- https://www.artnews.com/art-news/news/elias-sime-palace-ethiopia-13304/
- https://www.csmonitor.com/World/Africa/2025/0106/addis-ababa-abiy-ahmed-kazanchis-demolition-urban-transformation
- https://www.influencewatch.org/non-profit/zoma-foundation/
- https://next.archnet.org/sites/21496
- https://ww2.aaa.com/tripcanvas/attraction/zoma-museum-VA103323
- https://contemporaryand.com/en/places/zoma-museum
- https://jamescohan.com/public-exhibitions/zoma-museum
- https://selamta.ethiopianairlines.com/?p=1977
- https://www.ttbook.org/node/12541
- https://www.e-flux.com/announcements/263552/elias-simenoiseless
```

When you are done, reply with one line per space: id, the funding verdict, the number of red
flags, the number of press items, and any source that was dead or paywalled.

---

## Running it

1. Build batches from the current records: `python3 tools/import_details_reports.py --batches data/details_runs/<date>`
   (12 records per `batches/dNNN.json`).
2. Give each batch to one research agent with this prompt, the batch file and the output folder
   `data/details_runs/<date>/reports/`. Run two or three agents at a time: WebSearch is shared.
3. After a batch, run the text-slop check (`sponsor-atlas/work/ubatch/SLOP.md` rules, as set out in
   `data/details_check.md`) on its reports. The checker edits the .txt files in place and logs each
   fix in `data/details_runs/<date>/checks/dNNN-slop.json`.
4. Import: `python3 tools/import_details_reports.py data/details_runs/<date>/reports` (dry run,
   writes `review_details.md` and lists house-rule breaks it can see), then with `--apply`. It
   writes only the record's `details` field; funding, flags, tier and sources are not touched.
5. Then `tools/clean_data.py`, `tools/embed_data.py`, `tools/build_money_maps.py`, and the release
   bump (CACHE_NAME, ATLAS_RELEASE, the page's own `?v=` links).
