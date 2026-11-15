// Captions and dates for Artists' images, by hand (user, 13 Nov 2026: "proper captions with artists names and occasion";
// 15 Nov 2026: "rearrange it starting from the oldest criticism" and "make sure image captions make sense").
// tools/build_critique_gallery.py rewrites critique-collection-data.js, so these live apart from it and survive a rebuild.
// Keyed by the work's artist and project as that file has them.
//   year   the date of the work as a reader sees it; from is its first year, which the images page sorts by, oldest first.
//   title  the work's title where the collection's own carries a note in it ("exhibition view (2018)").
//   who    the people, named.
//   what   one line saying what the picture is and where: the default for every image of the work.
//   views  the same line for single images, by reference number, where a picture is something else (a poster among
//          exhibition views, a cover among spreads). Written after looking at each picture.
// A caption is title, who, that one line, then the photographer, which the pages read from each image's credit. The
// collection's type label ("Graphic design / artist-run exhibition") is not printed anywhere: it is a filing category,
// and read as filler under a picture (user, 15 Nov 2026: "slop?").
// Dates come from the image's own credit or what it shows (a poster's dates, a gazette's masthead) and from the source
// page: rietlanden.womensoffice.nl for the MsHeresies issues, wageforwork.com for the W.A.G.E. materials,
// flattimeho.org.uk for Offer for Sale, bureaudetudes.org for the 2010 map.
window.CRITIQUE_CAPTIONS = {
  "General Idea|The Miss General Idea Pageant Entry Kit":
    { year: "1971", from: 1971, who: "General Idea", what: "Entry kit mailed to artists for the 1971 Miss General Idea Pageant, Toronto" },
  "Artist Placement Group|Offer for Sale":
    { year: "1974", from: 1974, who: "John Latham and the Artist Placement Group",
      what: "View of the reconstruction at Flat Time House, London, 2019; first shown at The Gallery, London, 1974",
      views: {
        1808: "Diagram from Offer for Sale, 1974",
        1827: "Invitation to Offer for Sale at The Gallery, London, 19 November to 17 December 1974",
        1841: "Poster for the Artist Placement Group at the Hayward Gallery, London, December 1971",
        1869: "Typed page with handwritten corrections, shown at Flat Time House, London, 2019",
        1882: "Panel of the display, shown at Flat Time House, London, 2019" } },
  "Carole Condé / Karl Beveridge|It’s Still Privileged Art":
    { year: "1975", from: 1975, who: "Carole Condé and Karl Beveridge", what: "Drawing with caption from the series, 1975",
      views: { 1810: "Title image of the series, 1975" } },
  "Goran Trbuljak|Retrospective (1981)":
    { year: "1981", from: 1981, title: "Retrospective", who: "Goran Trbuljak", what: "Poster for his retrospective, 1981" },
  "General Idea|Cornucopia: Fragments from the Room of the Unknown Function":
    { year: "1982–1983", from: 1982, who: "General Idea", what: "Installation with video, 1982–1983" },
  "General Idea|Yen Boutique":
    { year: "1989", from: 1989, title: "¥en Boutique", who: "General Idea", what: "Installation, 1989" },
  "Meschac Gaba|Museum of Contemporary African Art":
    { year: "1997–2002", from: 1997, who: "Meschac Gaba", what: "Room of the museum installed at Tate Modern, London, 2013" },
  "Goran Trbuljak|Gallery intervention (2001)":
    { year: "2001", from: 2001, title: "Gallery intervention", who: "Goran Trbuljak", what: "Framed photograph, 2001" },
  "A.K. Burns / W.A.G.E.|W.A.G.E. Wo/manifesto":
    { year: "2008", from: 2008, who: "A.K. Burns with W.A.G.E. (Working Artists and the Greater Economy)", what: "Poster, 2008" },
  "Bureau d’études|Electromagnetic Propaganda":
    { year: "2010", from: 2010, who: "Bureau d’études: Léonore Bonaccini and Xavier Fourt", what: "Map, 2010" },
  "W.A.G.E. / Common Space Studio / William Powhida|2010 Artist Survey":
    { year: "2010–2012", from: 2010, title: "W.A.G.E. Artist Survey", who: "W.A.G.E.; designed by Common Space Studio; drawing by William Powhida",
      what: "Poster of what the survey found, published 2012; the survey ran from September 2010 to May 2011" },
  "W.A.G.E. / Sherry X. Xian|2010 Artist Survey":
    { year: "2010–2012", from: 2010, title: "W.A.G.E. Artist Survey", who: "W.A.G.E.; analysis by Sherry X. Xian, Survey Research Institute, Cornell University",
      what: "Page of the survey report" },
  "Alice Creischer|In the Stomach of the Predators":
    { year: "2012–2015", from: 2012, who: "Alice Creischer", what: "Installation view. Courtesy KOW, Berlin",
      views: {
        1846: "Detail of a sequinned textile. Courtesy KOW, Berlin", 1860: "Detail of a sequinned textile. Courtesy KOW, Berlin",
        1886: "Detail of the installation. Courtesy KOW, Berlin",
        1898: "The installation seen from the street at night. Courtesy KOW, Berlin",
        1919: "Still from the film. Courtesy KOW, Berlin", 1927: "Still from the film. Courtesy KOW, Berlin",
        1941: "Still from the film. Courtesy KOW, Berlin", 1955: "Still from the film. Courtesy KOW, Berlin",
        1961: "Still from the film. Courtesy KOW, Berlin",
        1967: "Drawings. Courtesy KOW, Berlin" } },
  "Artist Placement Group|The Individual and the Organisation":
    { year: "2012", from: 2012, who: "Artist Placement Group; exhibition graphics by John Morgan Studio", what: "Exhibition view, Raven Row, London, 2012",
      views: { 1940: "Vitrine in the exhibition, Raven Row, London, 2012", 1960: "Vitrine in the exhibition, Raven Row, London, 2012",
               1966: "Work in the exhibition, Raven Row, London, 2012", 1972: "Work in the exhibition, Raven Row, London, 2012" } },
  "W.A.G.E.|Artist fees — development materials":
    { year: "2012–2014", from: 2012, title: "W.A.G.E. Certification, development materials", who: "W.A.G.E. (Working Artists and the Greater Economy)",
      what: "Graphic made for public talks while W.A.G.E. Certification was being drafted",
      views: { 1817: "Fee In Relation To, graphic for public talks, 2012", 1833: "Fee In Relation To, graphic for public talks, 2012",
               1847: "W.A.G.E. T.H.R.O.B., graphic for public talks, 2013", 1861: "MISSING, poster, 2013" } },
  "W.A.G.E.|W.A.G.E. Certification":
    { year: "2014", from: 2014, who: "W.A.G.E. (Working Artists and the Greater Economy)", what: "Statement of the campaign for artist fees" },
  "ArtLeaks / contributors|ArtLeaks Gazette":
    { year: "2014–2017", from: 2014, who: "ArtLeaks and contributing artists", what: "Drawing for ArtLeaks",
      views: {
        1807: "Cover of ArtLeaks Gazette 2, June 2014",
        1826: "Section title in ArtLeaks Gazette 2, June 2014", 1840: "Section title in ArtLeaks Gazette 2, June 2014",
        1854: "Section title in ArtLeaks Gazette 2, June 2014",
        1868: "Comic in the ArtLeaks Gazette", 1881: "Comic in the ArtLeaks Gazette", 1893: "Comic in the ArtLeaks Gazette",
        1905: "Comic in the ArtLeaks Gazette",
        1916: "Page of ArtLeaks Gazette 2, June 2014", 1925: "Page of ArtLeaks Gazette 2, June 2014", 1932: "Page of ArtLeaks Gazette 2, June 2014",
        1982: "Cover of ArtLeaks Gazette 4, September 2017" } },
  "Bureau d’études / Brian Holmes / Freek Lomme|An Atlas of Agendas":
    { year: "2015", from: 2015, who: "Bureau d’études, with Brian Holmes and Freek Lomme",
      what: "Spread of the book, in the Set Margins edition; first published by Onomatopee, Eindhoven, 2015" },
  "Cameron Rowland|Disgorgement":
    { year: "2016", from: 2016, who: "Cameron Rowland", what: "Framed documents, 2016. Collection of The Museum of Modern Art, New York" },
  "Rietlanden Women’s Office|MsHeresies 1 — Conditions for Work":
    { year: "2018", from: 2018, title: "MsHeresies 1: Conditions for Work", who: "Rietlanden Women’s Office: Johanna Ehde and Elisabeth Rafstedt",
      what: "Spread of the issue, an essay by Adrienne Rich, Amsterdam, 2018", views: { 1977: "Cover of the issue, an essay by Adrienne Rich, Amsterdam, 2018" } },
  "Goran Trbuljak|Before and After Retrospective — exhibition view (2018)":
    { year: "2018", from: 2018.5, title: "Before and After Retrospective", who: "Goran Trbuljak", what: "Exhibition view, 2018" },
  "Rietlanden Women’s Office|MsHeresies 2 — Useful Work Versus Useless Toil":
    { year: "2019", from: 2019, title: "MsHeresies 2: Useful Work Versus Useless Toil", who: "Rietlanden Women’s Office: Johanna Ehde and Elisabeth Rafstedt",
      what: "Spread of the issue, William Morris’s lecture of 1884, Amsterdam, 2019", views: { 1973: "Cover of the issue, William Morris’s lecture of 1884, Amsterdam, 2019" } },
  "Rietlanden Women’s Office|Drafting a Manifesto":
    { year: "2019", from: 2019.5, who: "Rietlanden Women’s Office: Johanna Ehde and Elisabeth Rafstedt", what: "Pages made for Girls Like Us magazine, issue 12, 2019" },
  "Annelys de Vet / Tessa Meeus / Alex Walker|Design Dedication":
    { year: "2020", from: 2020, who: "Edited by Annelys de Vet; designed by Tessa Meeus and Alex Walker",
      what: "Spread of the book, Valiz and Sandberg Instituut, Amsterdam, 2020", views: { 1804: "Cover of the book, Valiz and Sandberg Instituut, Amsterdam, 2020" } },
  "Rietlanden Women’s Office|Everybody Everything, Other Birds Walk This Way Too":
    { year: "2020", from: 2020.2, who: "Rietlanden Women’s Office: Johanna Ehde and Elisabeth Rafstedt",
      what: "Poster with lines from a poem by Bernadette Mayer, group exhibition at Kalverstraat 28, Amsterdam, 2020" },
  "Rietlanden Women’s Office|MsHeresies 3 — Amniotechnics":
    { year: "2020", from: 2020.4, title: "MsHeresies 3: Amniotechnics", who: "Rietlanden Women’s Office: Johanna Ehde and Elisabeth Rafstedt",
      what: "Cover of the issue, an essay by Sophie Lewis, Amsterdam, 2020" },
  // The collective's page records no date for the graphic; its earliest entry there is from July 2020, so it sits at 2020
  // in the order and the caption gives no year.
  "Designers + Cultural Workers / UVW|Artworkers of the World Unite":
    { year: "", from: 2020.6, who: "Designers + Cultural Workers, a branch of the union United Voices of the World", what: "Campaign graphic" },
  "Rietlanden Women’s Office|MsHeresies 4 — Daffodils":
    { year: "2021", from: 2021, title: "MsHeresies 4: Daffodils", who: "Rietlanden Women’s Office: Johanna Ehde and Elisabeth Rafstedt",
      what: "Cover of the issue, a text by Rosalind Belben, Amsterdam, 2021" },
  "Farida Sedoc / Eline Mul / exhibition contributors|Non-Profit at All Cost":
    { year: "2022", from: 2022, who: "Curated by Farida Sedoc; graphic design and scenography by Eline Mul", what: "Exhibition view, Nest, The Hague, 2022",
      views: {
        1821: "Work in the exhibition, Nest, The Hague, 2022", 1835: "Work in the exhibition, Nest, The Hague, 2022",
        1921: "Work in the exhibition, Nest, The Hague, 2022", 1943: "Works in the exhibition, Nest, The Hague, 2022",
        1957: "Work in the exhibition, Nest, The Hague, 2022", 1963: "Work in the exhibition, Nest, The Hague, 2022",
        1969: "Work in the exhibition, Nest, The Hague, 2022",
        1863: "Visitors at a table in the exhibition, Nest, The Hague, 2022", 1876: "Talk in the exhibition, Nest, The Hague, 2022",
        1901: "Workshop in the exhibition, Nest, The Hague, 2022" } },
  "Rietlanden Women’s Office|MsHeresies 5 — We Are Going to Lose":
    { year: "2022", from: 2022.5, title: "MsHeresies 5: We Are Going to Lose", who: "Rietlanden Women’s Office: Johanna Ehde and Elisabeth Rafstedt",
      what: "Spread of the issue, texts by Lola Olufemi, Amsterdam, 2022", views: { 1911: "Cover of the issue, texts by Lola Olufemi, Amsterdam, 2022" } },
  "Farida Sedoc / Erik de Hart / Platform BK|People’s Forum":
    { year: "2023", from: 2023, who: "Farida Sedoc; graphic and spatial design by Erik de Hart (Heavy Bones); curated by Claudio Ritfeld",
      what: "Exhibition view, W139, Amsterdam, 2023",
      views: { 1822: "Poster for the workshop programme, W139, Amsterdam, 2023", 1922: "Poster for the exhibition, W139, Amsterdam, 18 November to 17 December 2023",
               1836: "Art market in the exhibition, W139, Amsterdam, 2023" } },
  "Pablo Helguera|Artoons — Metadrama":
    { year: "2023", from: 2023.5, title: "Artoons: Metadrama", who: "Pablo Helguera", what: "Exhibition view, PROA21, Fundación Proa, Buenos Aires, 2023" },
  "Rietlanden Women’s Office|MsHeresies 6 — A Manager":
    { year: "2024", from: 2024, title: "MsHeresies 6: A Manager", who: "Rietlanden Women’s Office: Johanna Ehde and Elisabeth Rafstedt",
      what: "Cover of the issue, a chapter by Caren Beilin, Amsterdam, 2024" },
  "Rietlanden Women’s Office|Handwerk":
    { year: "2025", from: 2025, who: "Rietlanden Women’s Office: Johanna Ehde and Elisabeth Rafstedt",
      what: "Specimen for the typeface Handwerk by Hammer and Philipp Herrmann, 2025" },
  "Rietlanden Women’s Office|Banners for Heresies":
    { year: "2025", from: 2025.5, who: "Rietlanden Women’s Office: Johanna Ehde and Elisabeth Rafstedt",
      what: "Monotype banner from their exhibition at Museum Folkwang, Essen, 2025" }
};
// One caption for both pages: the map layer's gallery (assets/critique-gallery.js) and artists-images.html.
window.critiqueCaption = function (im) {
  const c = window.CRITIQUE_CAPTIONS[im.artist + '|' + im.project] || {};
  const photo = (/Photo(?:graph|graphy)?: (.+?[^\s.]{2})\.(?:\s|$)/.exec(im.credit || '') || [])[1];
  return { title: c.title || im.title || im.project, who: c.who || im.artist, year: c.year != null ? c.year : (im.year || ''),
           line: (c.views && c.views[im.n]) || im.kind || c.what || '', photo: photo ? `Photograph: ${photo}` : '' };
};
