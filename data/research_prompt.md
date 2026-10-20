# Culture Atlas funding research prompt

Research one cultural space and report who funds it, using only what published sources state. The output is one plain-text report per space, in the layout below.

## Input
- Record: the space's current entry from `institutions.json` (id, name, location, website, funding, watch, flags, sources).

## Method
1. Read the existing record first. Your job is to confirm, correct or add to it, not to restate it.
2. Search the web: the space's own site (about, annual report, supporters, board), Wikipedia, art press (Artforum, The Art Newspaper, Artnet, e-flux, Contemporary And), national and local press, charity or company registries, and investigative or advocacy outlets.
3. Check the website itself. If it is down, parked, or serving spam, say so.
4. Follow the money one step beyond the space: founders, board chairs, major donors, and any state or government patronage (land grants, commissions, tax arrangements). A founder's other projects count only when they connect to the same funders or patrons.
5. Separate names that look related but are not (a foundation with the same name, a different museum in another city) and say they are not related.
6. Label every claim's strength: reported by an independent outlet; stated by the space itself; or an allegation, naming who makes it and whether that source is openly partisan.
7. Never guess. If nothing is found, write "No reporting found".

## Output: report (plain text, this exact layout)

```
<NAME IN CAPITALS> – <City>, <Country>
Website: <url, or "unreachable / serves spam" and the date checked>

OVERVIEW
- What it is, where, who founded it, when it opened, building/site facts, programmes, access (opening days, discounts, accessibility)

FUNDING
<Name of space>: <one-line verdict, e.g. "appears self-funded", "mainly public", "corporate-sponsored">
- Each funding source with what it pays for, and where the money ultimately comes from
- "No reporting found of …" where a search came up empty

Red flags: <short heading for the issue>   (repeat per issue; omit if none)
- Each fact, with figures and dates; mark allegations "Unverified" and name the outlet's stance

Not related: <similarly named entity> — why it is a different organisation   (omit if none)

BOTTOM LINE
Two or three sentences: is the space itself clean, and what, if anything, is worth watching.

SOURCES
- <url> (add "(advocacy source)" or "(partisan)" where relevant)
```

## Example of a finished report

Match this layout exactly: the same headings in capitals, a dash at the start of each point, one "Red flags:" heading per issue, and a "Not related:" line where one applies.

```
ZOMA MUSEUM – Addis Ababa, Ethiopia
Website: https://www.zomamuseum.org

OVERVIEW
- Eco-conscious art and architecture complex in the Mekanisa neighborhood, southwestern Addis Ababa, about 10 min drive from Meskel Square
- Co-founded by curator/anthropologist Meskerem Assegued and artist Elias Sime
- Began in 2002 as Zoma Contemporary Art Center (ZCAC); opened as Zoma Museum on March 24, 2019
- Named after Zoma Shiferraw, a young Ethiopian artist who died of cancer in 1979
- About two acres, built on a reclaimed former rubbish dump
- Architecture: single-storey wattle-and-daub buildings (juniper poles, eucalyptus screens, fermented red soil/straw/water plaster) on drystone foundations; exterior walls hand-sculpted by Sime
- On site: earthen gallery, restaurant, circus school, primary school, library, organic garden, dairy, livestock
- Open daily except Monday; discounts for children 12 and under, over-65s and students; wheelchair accessible, though some outdoor paths are bumpy

FUNDING
Zoma Museum (Mekanisa): appears self-funded
- Land bought from 2013 with Assegued's income as a curator/anthropologist and sales of Sime's artwork
- Sime is represented by James Cohan Gallery, New York, so the money ultimately comes from the Western art market
- Privately funded; founders were working on a foundation to sustain it long-term
- No reporting found of dirty money behind the museum itself

Red flags: ties to PM Abiy Ahmed's government
- Unity Park: Abiy commissioned the founders to build a mini-Zoma there (opened Oct 2019). The park cost over $160M, funded by the UAE government plus wealthy Ethiopian donors
- Transparency: asked about the parks in parliament, Abiy said MPs couldn't question him because no government budget was used. Critics saw this as refusing to account for the money
- Unverified allegations (from an openly anti-Abiy outlet): undisclosed funding, blocked audits, contracts going to companies tied to Abiy or his allies
- Zoma Village Entoto: Abiy gave the founders the land; they say they paid for construction themselves (estimated "in the millions"). A free land grant from the head of government is still state patronage
- Timing: critics objected to spending on cosmetic projects while people were starving and dying, including during the Tigray war

Not related: the Colorado-based Zoma Foundation, criticized in 2020 for funding a Colorado state government position. It has nothing to do with the museum.

BOTTOM LINE
The museum itself looks clean. The founders' closeness to the Abiy government, and through Unity Park to opaque UAE money, is the part worth looking at.

SOURCES
- https://www.artforum.com/columns/ethiopian-art-crossroads-551671/
- https://www.theartnewspaper.com/2024/05/20/how-an-artist-and-curator-duo-are-transforming-addis-ababa-with-their-eco-driven-projects
- https://www.thereporterethiopia.com/10337/
- https://almariam.com/2020/02/03/unity-park-addis-ababa-the-story-of-all-of-us-in-the-city-upon-the-hill/
- https://curateoromia.com/ethiopia-at-a-crossroads-the-fragile-reign-of-prime-minister-abiy-ahmed (advocacy source)
- https://news.artnet.com/art-world/zoma-museum-opens-ethiopia-1501450
- https://www.influencewatch.org/non-profit/zoma-foundation/
- https://next.archnet.org/sites/21496
- https://ww2.aaa.com/tripcanvas/attraction/zoma-museum-VA103323
- https://contemporaryand.com/en/places/zoma-museum
```

## Importing into Culture Atlas

Save each report as a .txt file, named after the record id when the title might not match the record's name exactly (for example `zoma-museum-addis-ababa.txt`). Then:

```
python3 tools/import_research_reports.py <file or folder>            # dry run: writes a review file, changes nothing
python3 tools/import_research_reports.py <file or folder> --apply    # writes the records
```

Then run `tools/clean_data.py`, `tools/embed_data.py` and `tools/build_money_maps.py`.

Rules: write in plain English, no adjectives of judgement beyond what sources support; keep the report under 600 words.
