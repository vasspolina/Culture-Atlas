// Captions for Artists' images, by hand (user, 13 Nov 2026: "proper captions with artists names and occasion").
// tools/build_critique_gallery.py rewrites critique-collection-data.js, so these live apart from it and survive a rebuild.
// Keyed by the work's artist and project as that file has them. `who` is the people, named; `occasion` is what the image
// was made for or shown at, with place and year. Both are taken from the image's own credit, note and source page; where
// the source names no exhibition, the occasion is left out and the caption falls back to the kind of work. The
// photographer is not here: the page reads it from each image's credit, since it changes picture to picture.
window.CRITIQUE_CAPTIONS = {
  "Farida Sedoc / Eline Mul / exhibition contributors|Non-Profit at All Cost":
    { who: "Curated by Farida Sedoc; graphic design and scenography by Eline Mul", occasion: "Exhibition at Nest, The Hague, 2022" },
  "Farida Sedoc / Erik de Hart / Platform BK|People’s Forum":
    { who: "Farida Sedoc; graphic and spatial design by Erik de Hart (Heavy Bones); curated by Claudio Ritfeld", occasion: "Exhibition at W139, Amsterdam, with Platform BK in residence" },
  "Annelys de Vet / Tessa Meeus / Alex Walker|Design Dedication":
    { who: "Edited by Annelys de Vet; designed by Tessa Meeus and Alex Walker", occasion: "Book, Valiz and Sandberg Instituut, Amsterdam, 2020" },
  "Bureau d’études / Brian Holmes / Freek Lomme|An Atlas of Agendas":
    { who: "Bureau d’études, with Brian Holmes and Freek Lomme", occasion: "Book, Onomatopee, Eindhoven, 2015; later edition by Set Margins" },
  "ArtLeaks / contributors|ArtLeaks Gazette":
    { who: "ArtLeaks and contributing artists", occasion: "ArtLeaks Gazette" },
  "Artist Placement Group|Offer for Sale":
    { who: "John Latham and the Artist Placement Group" },
  "Andrea Francke / Eva Weinmayr|The Piracy Project":
    { who: "Andrea Francke and Eva Weinmayr" },
  "Carole Condé / Karl Beveridge|It’s Still Privileged Art":
    { who: "Carole Condé and Karl Beveridge", occasion: "1975, edited version" },
  "Goran Trbuljak|Retrospective (1981)":
    { who: "Goran Trbuljak", occasion: "1981" },
  "General Idea|The Miss General Idea Pageant Entry Kit":
    { who: "General Idea", occasion: "The Miss General Idea Pageant" },
  "Designers + Cultural Workers / UVW|Artworkers of the World Unite":
    { who: "Designers + Cultural Workers, United Voices of the World", occasion: "Union campaign" },
  "Meschac Gaba|Museum of Contemporary African Art":
    { who: "Meschac Gaba", occasion: "Counter-museum begun after his time at the Rijksakademie, Amsterdam" },
  "Alice Creischer|In the Stomach of the Predators":
    { who: "Alice Creischer" },
  "W.A.G.E.|Artist fees — development materials":
    { who: "W.A.G.E. (Working Artists and the Greater Economy)", occasion: "Campaign for artist fees" },
  "Cameron Rowland|Disgorgement":
    { who: "Cameron Rowland", occasion: "2016" },
  "Andreas Siekmann|Trickle Down — Public Space in the Era of Its Privatization":
    { who: "Andreas Siekmann", occasion: "Taipei Biennial, 2012" },
  "Rietlanden Women’s Office|Banners for Heresies / Printworks":
    { who: "Rietlanden Women’s Office: Johanna Ehde and Elisabeth Rafstedt" },
  "Goran Trbuljak|Gallery intervention (2001)":
    { who: "Goran Trbuljak", occasion: "2001" },
  "General Idea|Cornucopia: Fragments from the Room of the Unknown Function":
    { who: "General Idea" },
  "Rietlanden Women’s Office|Handwerk":
    { who: "Rietlanden Women’s Office: Johanna Ehde and Elisabeth Rafstedt" },
  "Bureau d’études|Electromagnetic Propaganda":
    { who: "Bureau d’études: Léonore Bonaccini and Xavier Fourt" },
  "General Idea|The 1970 Miss General Idea Pageant":
    { who: "General Idea", occasion: "The Miss General Idea Pageant, 1970" },
  "Bureau d’études|Power maps — files, databases and social directories":
    { who: "Bureau d’études: Léonore Bonaccini and Xavier Fourt" },
  "Goran Trbuljak|Before and After Retrospective — exhibition view (2018)":
    { who: "Goran Trbuljak", occasion: "Exhibition Before and After Retrospective, 2018" },
  "General Idea|Yen Boutique":
    { who: "General Idea" },
  "Rietlanden Women’s Office|MsHeresies 6 — A Manager":
    { who: "Rietlanden Women’s Office: Johanna Ehde and Elisabeth Rafstedt", occasion: "MsHeresies, issue 6" },
  "Bureau d’études|Power maps — the economy of the self":
    { who: "Bureau d’études: Léonore Bonaccini and Xavier Fourt" },
  "General Idea|FILE Megazine — Glamour Issue":
    { who: "General Idea", occasion: "FILE Megazine, Glamour Issue" },
  "W.A.G.E. / Common Space Studio / William Powhida|2010 Artist Survey":
    { who: "W.A.G.E.; designed by Common Space Studio; drawing by William Powhida", occasion: "W.A.G.E. 2010 Artist Survey, poster printed 2012" },
  "General Idea|Showcard Series (1975)":
    { who: "General Idea", occasion: "1975" },
  "W.A.G.E. / Sherry X. Xian|2010 Artist Survey":
    { who: "W.A.G.E.; analysis by Sherry X. Xian, Survey Research Institute, Cornell University", occasion: "W.A.G.E. 2010 Artist Survey, report" },
  "Bureau d’études|World Government, 2013":
    { who: "Bureau d’études: Léonore Bonaccini and Xavier Fourt", occasion: "2013" },
  "General Idea|Test Tube":
    { who: "General Idea" },
  "A.K. Burns / W.A.G.E.|W.A.G.E. Wo/manifesto":
    { who: "A.K. Burns with W.A.G.E.", occasion: "2008" },
  "Bureau d’études|Media ownership — 2004 map":
    { who: "Bureau d’études: Léonore Bonaccini and Xavier Fourt", occasion: "2004" },
  "Artist Placement Group|The Individual and the Organisation":
    { who: "Artist Placement Group; exhibition graphics by John Morgan Studio", occasion: "Exhibition at Raven Row, London, 2012" },
  "General Idea|The Boutique from the 1984 Miss General Idea Pavilion":
    { who: "General Idea", occasion: "The 1984 Miss General Idea Pavilion" },
  "W.A.G.E.|W.A.G.E. Certification":
    { who: "W.A.G.E. (Working Artists and the Greater Economy)", occasion: "Campaign for artist fees" },
  "Rietlanden Women’s Office|MsHeresies 5 — We Are Going to Lose":
    { who: "Rietlanden Women’s Office: Johanna Ehde and Elisabeth Rafstedt", occasion: "MsHeresies, issue 5" },
  "Bureau d’études|Lagardère — 2004 map":
    { who: "Bureau d’études: Léonore Bonaccini and Xavier Fourt", occasion: "2004" },
  "Rietlanden Women’s Office|MsHeresies 4 — Daffodils":
    { who: "Rietlanden Women’s Office: Johanna Ehde and Elisabeth Rafstedt", occasion: "MsHeresies, issue 4" },
  "Rietlanden Women’s Office|MsHeresies 3 — Amniotechnics":
    { who: "Rietlanden Women’s Office: Johanna Ehde and Elisabeth Rafstedt", occasion: "MsHeresies, issue 3" },
  "Rietlanden Women’s Office|Everybody Everything, Other Birds Walk This Way Too":
    { who: "Rietlanden Women’s Office: Johanna Ehde and Elisabeth Rafstedt" },
  "Rietlanden Women’s Office|Reproductive Labour and Graphic Design":
    { who: "Rietlanden Women’s Office: Johanna Ehde and Elisabeth Rafstedt" },
  "Rietlanden Women’s Office|Drafting a Manifesto":
    { who: "Rietlanden Women’s Office: Johanna Ehde and Elisabeth Rafstedt" },
  "Rietlanden Women’s Office|MsHeresies 2 — Useful Work Versus Useless Toil":
    { who: "Rietlanden Women’s Office: Johanna Ehde and Elisabeth Rafstedt", occasion: "MsHeresies, issue 2" },
  "Rietlanden Women’s Office|MsHeresies 1 — Conditions for Work":
    { who: "Rietlanden Women’s Office: Johanna Ehde and Elisabeth Rafstedt", occasion: "MsHeresies, issue 1" },
  "Rietlanden Women’s Office|Banners for Heresies":
    { who: "Rietlanden Women’s Office: Johanna Ehde and Elisabeth Rafstedt" },
  "Pablo Helguera|Artoons — Metadrama":
    { who: "Pablo Helguera", occasion: "Exhibition at PROA21, Fundación Proa, 2023" }
};
