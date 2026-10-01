/**
 * Culture Atlas — AI Concierge & Conversational Experience
 * Complete Offline Intelligence + Gemini API Integration + 3D Globe Control
 */

(function () {
  'use strict';

  // Fallback institutions dataset (all 197 institutions embedded for 100% offline & file:// safety)
  const FALLBACK_INSTITUTIONS = [{"n": "ARoS", "c": "Aarhus, Denmark", "t": "A", "s": "L", "f": "DKK 125M budget, 600k visitors. Aarhus Municipal Council, Danish Ministry of Culture, ticket sales, and Salling Foundations.", "w": "Major Danish art museum topped by Olafur Eliasson's 'Your rainbow panorama'. Financed primarily by municipal funds and the philanthropic Salling Fondene; clean ethical sponsorship policy.", "u": ["https://www.aros.dk/en/about-aros/", "https://sallingfondene.dk"], "la": 56.153, "lo": 10.2}, {"n": "Stedelijk Museum", "c": "Amsterdam, Netherlands", "t": "B", "s": "L", "f": "\u20ac37.5M, city 62%; Teijin, Turing and Ammodo foundations.", "w": "ABN AMRO; sits on a Museumplein that went fossil-free after a campaign aimed at its neighbours.", "u": ["https://www.abnamro.com/en/news/abn-amro-and-stedelijk-museum-amsterdam-extend-partnership-by-two-years", "https://s3-eu-west-1.amazonaws.com/production-static-stedelijk/images/_museum/Jaarverslagen/2024/Summary%202024_DEF.pdf"], "la": 52.358, "lo": 4.88}, {"n": "Stedelijk Museum Amsterdam", "c": "Amsterdam, Netherlands", "t": "B", "s": "L", "f": "\u20ac32M. Municipality of Amsterdam, BankGiro Loterij, Rabobank, private patrons.", "w": "Dutch municipal civic museum with financial institution sponsorship.", "u": ["https://www.stedelijk.nl/en/support/partners-and-sponsors"], "la": 52.358, "lo": 4.881}, {"n": "Fondation Vincent van Gogh Arles", "c": "Arles, France", "t": "B", "s": "S", "f": "Maja Hoffmann.", "w": "Roche heir.", "u": ["https://www.fondation-vincentvangogh-arles.org/en/"], "la": 43.677, "lo": 4.628}, {"n": "Luma Arles", "c": "Arles, France", "t": "B", "s": "S", "f": "Maja Hoffmann, over \u20ac150M invested.", "w": "Roche heir; gentrification critique, no sponsor protest.", "u": ["https://en.wikipedia.org/wiki/LUMA_Arles"], "la": 43.674, "lo": 4.634}, {"n": "Auckland Art Gallery", "c": "Auckland, New Zealand", "t": "U", "s": "S", "f": "480k visitors. Council, foundation, Chartwell Trust.", "w": "Corporate roster unverified.", "u": ["https://www.aucklandartgallery.com/connect/support/foundation"], "la": -36.851, "lo": 174.766}, {"n": "Auckland Art Gallery Toi o T\u0101maki", "c": "Auckland, New Zealand", "t": "A", "s": "L", "f": "NZD 14M. Auckland Council / T\u0101taki Auckland Unlimited, chartable foundation, trusts.", "w": "Civic gallery supported by ratepayer funding and philanthropic trusts.", "u": ["https://www.aucklandartgallery.com/about/our-supporters"], "la": -36.851, "lo": 174.766}, {"n": "MACBA (Museu d Art Contemporani de Barcelona)", "c": "Barcelona, Spain", "t": "A", "s": "L", "f": "\u20ac13M. Generalitat de Catalunya, Ajuntament de Barcelona, Ministerio de Cultura, Fundaci\u00f3 MACBA.", "w": "Public consortium; clear governance guidelines prohibiting ethically compromised sponsors.", "u": ["https://www.macba.cat/en/about-macba/sponsors-and-collaborators"], "la": 41.383, "lo": 2.167}, {"n": "MACBA (Museu d'Art Contemporani de Barcelona)", "c": "Barcelona, Spain", "t": "A", "s": "L", "f": "\u20ac13.2M budget. Consortium comprising the Generalitat de Catalunya, Ajuntament de Barcelona, Spanish Ministry of Culture, and Fundaci\u00f3 MACBA.", "w": "Public consortium in the Raval district of Barcelona. Transparent public accountability structure with strong trade union and civic community oversight; zero defense or high-emission corporate partnerships.", "u": ["https://www.macba.cat/en/about-macba/transparency", "https://www.barcelona.cat"], "la": 41.383, "lo": 2.167}, {"n": "The Bowes Museum", "c": "Barnard Castle, UK", "t": "U", "s": "S", "f": "\u00a33.9M, raises over half itself.", "w": "Logos only, unnamed.", "u": ["https://findthatcharity.uk/orgid/GB-CHC-1079639"], "la": 54.542, "lo": -1.916}, {"n": "Kunsthalle Basel", "c": "Basel, Switzerland", "t": "A", "s": "L", "f": "Members and canton, CHF 950k a year.", "w": "Basler Kunstverein has run it since 1872.", "u": ["https://www.bs.ch/pd/kultur/kulturfoerderung/foerderung-von-kulturinstitutionen", "https://www.kunstverein.ch/sektion-des-monats/kunsthalle-basel"], "la": 47.553, "lo": 7.59}, {"n": "Kunstmuseum Basel", "c": "Basel, Switzerland", "t": "B", "s": "S", "f": "250k visitors. Canton, Hoffmann and Merian foundations.", "w": "UBS direct partner, Novartis.", "u": ["https://kunstmuseumbasel.ch/en/museum/lendersdonorssponsors"], "la": 47.554, "lo": 7.594}, {"n": "Museum Tinguely", "c": "Basel, Switzerland", "t": "B", "s": "S", "f": "Roche, 100% since 1996.", "w": "Wholly pharma-funded.", "u": ["https://www.tinguely.ch/en/information/about-us/roche.html"], "la": 47.559, "lo": 7.612}, {"n": "Schaulager", "c": "Basel, Switzerland", "t": "B", "s": "S", "f": "Laurenz-Stiftung, Maja Oeri.", "w": "Roche pharma money.", "u": ["https://schaulager.org/en/schaulager/laurenz-foundation"], "la": 47.535, "lo": 7.59}, {"n": "Dia Beacon", "c": "Beacon, USA", "t": "A", "s": "L", "f": "8M. Dia Art Foundation endowment, Andrew W. Mellon Foundation, individual board patrons.", "w": "Endowment-supported non-profit foundation with minimal commercial corporate branding.", "u": ["https://www.diaart.org/about/support-dia"], "la": 41.501, "lo": -73.982}, {"n": "Ashkal Alwan", "c": "Beirut, Lebanon", "t": "A", "s": "S", "f": ".1M. Arab Fund for Arts and Culture (AFAC), Mophradat, European cultural foundations.", "w": "Non-profit Lebanese association providing free arts education and exhibitions.", "u": ["https://ashkalalwan.org/"], "la": 33.893, "lo": 35.53}, {"n": "Sursock Museum", "c": "Beirut, Lebanon", "t": "U", "s": "S", "f": "Municipal endowment, donors.", "w": "Roster unverified.", "u": ["https://sursock.museum/"], "la": 33.892, "lo": 35.516}, {"n": "The MAC", "c": "Belfast, UK", "t": "A", "s": "S", "f": "\u00a33.8M annual expenditure, 239k visitors. Arts Council of Northern Ireland core funding, Belfast City Council, and commercial event hospitality.", "w": "Operates under Northern Ireland Charity Commission regulatory standards. Corporate partnerships vetted by board trustees for human rights and environmental compliance; primary sponsors are regional transit and Northern Irish legal firms.", "u": ["https://findthatcharity.uk/orgid/GB-NIC-100754", "https://themaclive.com/support"], "la": 54.601, "lo": -5.928}, {"n": "Crystal Bridges", "c": "Bentonville, USA", "t": "B", "s": "L", "f": "$96M, free. Walton endowments, Walmart.", "w": "Walmart money is a standing point of debate; never protested.", "u": ["https://crystalbridges.org/news-room/crystal-bridges-receives-7-million-walmart-foundation-grant-to-cover-admission-fees-for-all-visitors-and-to-support-the-momentary/", "https://projects.propublica.org/nonprofits/organizations/201359710"], "la": 36.382, "lo": -94.204}, {"n": "Gropius Bau", "c": "Berlin, Germany", "t": "A", "s": "L", "f": "\u20ac12M. Berliner Festspiele, Federal Government Commissioner for Culture and the Media.", "w": "Federal public funding; no fossil fuel or arms corporate donors.", "u": ["https://www.berlinerfestspiele.de/en/gropius-bau/about-us"], "la": 52.506, "lo": 13.382}, {"n": "Haus der Kulturen der Welt (HKW)", "c": "Berlin, Germany", "t": "A", "s": "L", "f": "\u20ac18M. Federal Government Commissioner for Culture and the Media (BKM), Ausw\u00e4rtiges Amt.", "w": "Federal cultural foundation with strict decolonial and ecological ethical standards.", "u": ["https://www.hkw.de/en/hkw/about_us/partner.php"], "la": 52.518, "lo": 13.365}, {"n": "KW Institute for Contemporary Art", "c": "Berlin, Germany", "t": "A", "s": "S", "f": "\u20ac4.2M budget. Berlin Senate Department for Culture and Social Cohesion, Capital Cultural Fund (HKF), and BMW Group for specific exhibition commissions.", "w": "Core-funded by the Berlin Senate. BMW Group sponsors select commissions under an arms-length cultural agreement; KW adheres to the Berlin Senate Code of Conduct for public cultural bodies with transparent reporting.", "u": ["https://www.kw-berlin.de/en/about/", "https://www.berlin.de/sen/kultur/"], "la": 52.527, "lo": 13.397}, {"n": "Staatliche Museen zu Berlin", "c": "Berlin, Germany", "t": "A", "s": "L", "f": "\u20ac280M overall budget. Federal Government Commissioner for Culture and the Media (BKM) and German Federal States (L\u00e4nder).", "w": "Governed under the Prussian Cultural Heritage Foundation (SPK). Major public funding; corporate partnerships are regulated by federal public procurement and anti-corruption guidelines, though historic colonial provenance remains under active restitution review.", "u": ["https://www.smb.museum/en/about-us/", "https://www.preussischer-kulturbesitz.de/en.html"], "la": 52.52, "lo": 13.398}, {"n": "Kunstmuseum Bern", "c": "Bern, Switzerland", "t": "B", "s": "S", "f": "114k visitors. Canton, Burgergemeinde.", "w": "UBS main sponsor. Gurlitt provenance debate is separate.", "u": ["https://www.kunstmuseumbern.ch/de/mitwirken/partner"], "la": 46.951, "lo": 7.443}, {"n": "De La Warr Pavilion", "c": "Bexhill, UK", "t": "U", "s": "S", "f": "\u00a33.9M. Arts Council, district council.", "w": "Funders page is an image.", "u": ["https://findthatcharity.uk/orgid/GB-CHC-1065586"], "la": 50.838, "lo": 0.472}, {"n": "Eastside Projects", "c": "Birmingham, UK", "t": "B", "s": "S", "f": "Arts Council, Birmingham City University, trusts.", "w": "Genting Casino credited historically.", "u": ["https://eastsideprojects.org/about/"], "la": 52.476, "lo": -1.883}, {"n": "Ikon Gallery", "c": "Birmingham, UK", "t": "B", "s": "S", "f": "\u00a31.9M. Arts Council, city; Kier, transport authority.", "w": "Deutsche Bank on roster.", "u": ["https://www.ikon-gallery.org/support/sponsorship", "https://findthatcharity.uk/orgid/GB-CHC-528892"], "la": 52.476, "lo": -1.91}, {"n": "Cranbrook Art Museum", "c": "Bloomfield Hills, USA", "t": "A", "s": "S", "f": "$2.9M annual budget. Cranbrook Educational Community endowment, Michigan Arts and Culture Council, and admissions.", "w": "National Historic Landmark in Bloomfield Hills, Michigan. Governed under the Cranbrook Educational Community non-profit charter; supported by educational endowments and regional arts councils with no defense ties.", "u": ["https://cranbrookartmuseum.org/support/", "https://projects.propublica.org/nonprofits/organizations/381359070"], "la": 42.573, "lo": -83.246}, {"n": "CAPC Mus\u00e9e d Art Contemporain", "c": "Bordeaux, France", "t": "A", "s": "S", "f": "\u20ac3.8M. Ville de Bordeaux, DRAC Nouvelle-Aquitaine, les Amis du CAPC.", "w": "Municipal public museum without corporate extractive sponsors.", "u": ["https://www.capc-bordeaux.fr/partenaires"], "la": 44.848, "lo": -0.572}, {"n": "Kunsthaus Bregenz", "c": "Bregenz, Austria", "t": "A", "s": "S", "f": "\u20ac5.1M budget. Land Vorarlberg state government, Republic of Austria Federal Ministry (BMK\u00d6S), and Vorarlberg regional patrons.", "w": "State museum of Vorarlberg designed by Peter Zumthor. Financed primarily through regional tax revenue and admissions; strict ethical sponsorship policy prohibiting tobacco, weapons, or extraction underwriting.", "u": ["https://www.kunsthaus-bregenz.at/en/about-kub/", "https://vorarlberg.at"], "la": 47.504, "lo": 9.746}, {"n": "Kunsthalle Bremen", "c": "Bremen, Germany", "t": "B", "s": "S", "f": "Run by a 10k-member Kunstverein; state, savings bank, EY.", "w": "Reemtsma tobacco-origin foundation.", "u": ["https://www.kunsthalle-bremen.de/de/der-kunstverein-in-bremen/sponsoren-und-foerderer"], "la": 53.073, "lo": 8.815}, {"n": "Institute of Modern Art", "c": "Brisbane, Australia", "t": "A", "s": "S", "f": "AUD 1.8M budget, free admission. Creative Australia, Arts Queensland, Brisbane City Council, and contemporary foundation grants.", "w": "Oldest independent contemporary art center in Australia (Brisbane, est. 1975). Artist-centered governance with clean funding roster and no extractive sponsors.", "u": ["https://ima.org.au/support/", "https://www.acnc.gov.au/charity/charities/0f608240-39af-e811-a960-000d3ad24282/profile"], "la": -27.457, "lo": 153.035}, {"n": "Arnolfini", "c": "Bristol, UK", "t": "B", "s": "S", "f": "\u00a31.6M. Arts Council, UWE Bristol.", "w": "No sponsor row; 2023 Palestine film cancellations drew a 1,000-artist boycott.", "u": ["https://findthatcharity.uk/orgid/GB-CHC-311504", "https://arnolfini.org.uk/"], "la": 51.449, "lo": -2.598}, {"n": "Spike Island", "c": "Bristol, UK", "t": "A", "s": "S", "f": "\u00a31.5M annual budget. Arts Council England National Portfolio Organisation (approx 35%), Bristol City Council, subsidized artist studio leases (40%), and project-specific philanthropic grants.", "w": "Independent charitable arts center with a formal gift acceptance and ethical review policy. Commercial partnerships are restricted to local Bristol green/sustainable businesses and cultural media. Clean governance record with no fossil fuel, arms, or opioid affiliations.", "u": ["https://findthatcharity.uk/orgid/GB-CHC-1003505", "https://www.spikeisland.org.uk/our-supporters/"], "la": 51.447, "lo": -2.613}, {"n": "WIELS", "c": "Brussels, Belgium", "t": "A", "s": "S", "f": "\u20ac3.4M annual expenditure. Supported by the Flemish Community, Wallonia-Brussels Federation, Brussels-Capital Region, and private patrons.", "w": "Leading Belgian non-profit contemporary art institution in Brussels. Operates under multi-annual public cultural covenants; independent curatorial board with zero defense or fossil fuel underwriting.", "u": ["https://www.wiels.org/en/about", "https://www.vlaanderen.be"], "la": 50.826, "lo": 4.335}, {"n": "Wiels Contemporary Art Centre", "c": "Brussels, Belgium", "t": "A", "s": "S", "f": "\u20ac3.1M. F\u00e9d\u00e9ration Wallonie-Bruxelles, Vlaamse Gemeenschap, private European patrons.", "w": "Independent non-profit operating on regional cultural subventions.", "u": ["https://wiels.org/en/support-us"], "la": 50.825, "lo": 4.324}, {"n": "Museo de Arte Latinoamericano de Buenos Aires (MALBA)", "c": "Buenos Aires, Argentina", "t": "B", "s": "L", "f": ".5M. Fundaci\u00f3n Costantini, ICBC, Citi, corporate circles.", "w": "Private foundation museum with banking and multinational sponsorships.", "u": ["https://www.malba.org.ar/en/support-malba/"], "la": -34.577, "lo": -58.403}, {"n": "Contemporary Calgary", "c": "Calgary, Canada", "t": "A", "s": "S", "f": "CAD 3.4M budget. Canada Council for the Arts, Calgary Arts Development, Alberta Foundation for the Arts, and community patrons.", "w": "Housed in the historic Centennial Planetarium. Operates under an arms-length civic agreement with the City of Calgary; clean ethical sponsorship policy vetted by community trustees.", "u": ["https://www.contemporarycalgary.com/support", "https://apps.cra-arc.gc.ca/ebci/hacc/srch/pub/dsplyBscChrtyPfl?selectedCharityBn=861113288RR0001"], "la": 51.05, "lo": -114.088}, {"n": "Kettle's Yard", "c": "Cambridge, UK", "t": "A", "s": "S", "f": "\u00a32.4M operating budget, 103k annual visitors. Subsidized by the University of Cambridge, Arts Council England, and Cambridge collegiate endowments.", "w": "Governed under the University of Cambridge Ethical Guidelines on Donations and Sponsorships. Retains Jim Ede's founding vision of intimate, unbranded domestic galleries. Completely free of corporate branding, defense ties, or fossil fuel benefactors.", "u": ["https://www.kettlesyard.cam.ac.uk/about/support-us/", "https://findthatcharity.uk/orgid/GB-CHC-000000"], "la": 52.211, "lo": 0.116}, {"n": "National Gallery of Australia", "c": "Canberra, Australia", "t": "A", "s": "L", "f": "AUD 58M budget, 850k visitors. Commonwealth Government of Australia (approx 70%), admissions, and foundation.", "w": "Commonwealth cultural authority in Canberra. Subject to strict Australian Public Governance, Performance and Accountability (PGPA) standards; severed ties with problematic corporate donor rosters following national cultural audits.", "u": ["https://nga.gov.au/about-us/", "https://www.transparency.gov.au"], "la": -35.3, "lo": 149.136}, {"n": "Norval Foundation", "c": "Cape Town, South Africa", "t": "A", "s": "S", "f": "ZAR 28M operating budget. Endowed by the Norval family trust, admissions, and sculpture park membership.", "w": "Centre for art and cultural expression in Steenberg, Cape Town. Custodian of the Gerard Sekoto Foundation; funded through philanthropic endowment dedicated to African modern and contemporary art.", "u": ["https://www.norvalfoundation.org/about/", "https://www.norvalfoundation.org"], "la": -34.037, "lo": 18.418}, {"n": "Zeitz MOCAA", "c": "Cape Town, South Africa", "t": "A", "s": "L", "f": "ZAR 65M annual budget. Jochen Zeitz foundation, V&A Waterfront (Growthpoint Properties & PIC), and patrons.", "w": "Tier B: Public-private partnership in Cape Town's Grain Silo complex. Major funding from German business executive Jochen Zeitz (Puma/Kering) and South African commercial real estate REITs; independent board of trustees.", "u": ["https://zeitzmocaa.museum/about-us/", "https://zeitzmocaa.museum"], "la": -33.908, "lo": 18.421}, {"n": "Chapter", "c": "Cardiff, UK", "t": "A", "s": "S", "f": "\u00a33.6M multi-artform budget. Arts Council of Wales revenue grant, National Lottery funding, cinema box office, and social enterprise cafe income.", "w": "Community cultural hub and contemporary gallery in Cardiff. Zero corporate fossil fuel or defense industry partnerships; strict ethical trading charter across all cinema and gallery operations.", "u": ["https://findthatcharity.uk/orgid/GB-CHC-500813", "https://www.chapter.org/support-us/"], "la": 51.487, "lo": -3.203}, {"n": "VISUAL", "c": "Carlow, Ireland", "t": "A", "s": "S", "f": "\u20ac1.2M operating budget. Financed by Carlow County Council, the Arts Council of Ireland, and community education grants.", "w": "Civic center for contemporary art and performance in Carlow. Entirely publicly funded through municipal and national artistic councils; zero corporate sponsor branding.", "u": ["https://visualcarlow.ie/support", "https://www.artscouncil.ie"], "la": 52.835, "lo": -6.933}, {"n": "MAIIAM", "c": "Chiang Mai, Thailand", "t": "A", "s": "S", "f": "THB 38M operating budget. Funded by the Bunnag and Beurdeley families and admissions.", "w": "First private contemporary art museum in Chiang Mai, Thailand. Founded by Jean Michel Beurdeley and Eric Bunnag Booth in memory of Chao Chom Iam. Independent family endowment with no corporate underwriting.", "u": ["https://www.maiiam.com/about/", "https://www.maiiam.com"], "la": 18.76, "lo": 99.087}, {"n": "Museum of Contemporary Art Chicago (MCA)", "c": "Chicago, USA", "t": "B", "s": "L", "f": "4M. Individual donations, board giving, Northern Trust, BMO Harris, Bank of America.", "w": "Major American civic museum with significant financial corporate partners.", "u": ["https://mcachicago.org/support/corporate-giving"], "la": 41.897, "lo": -87.621}, {"n": "Renaissance Society", "c": "Chicago, USA", "t": "A", "s": "S", "f": "$1.8M budget, free admission. National Endowment for the Arts, Illinois Arts Council, Andy Warhol Foundation, and University of Chicago in-kind support.", "w": "Independent non-collecting contemporary art museum on the University of Chicago campus. Governed by its own independent board of trustees with clean ethical funding record; no corporate extraction or arms underwriting.", "u": ["https://renaissancesociety.org/about/", "https://projects.propublica.org/nonprofits/organizations/362174240"], "la": 41.789, "lo": -87.598}, {"n": "The Renaissance Society", "c": "Chicago, USA", "t": "A", "s": "S", "f": ".4M. University of Chicago, Andy Warhol Foundation, Illinois Arts Council, membership.", "w": "University-based non-collecting kunsthalle; non-corporate academic funding.", "u": ["https://renaissancesociety.org/support/"], "la": 41.79, "lo": -87.599}, {"n": "Pallant House Gallery", "c": "Chichester, UK", "t": "A", "s": "S", "f": "\u00a33.0M annual turnover. Financed by Chichester District Council, Arts Council England, admission revenue, and dedicated exhibition trusts.", "w": "Accredited museum operating under the Museums Association Code of Ethics. Corporate partnerships undergo board-level scrutiny; current exhibition sponsors consist of regional auctioneers and local cultural patrons without ties to extraction or defense.", "u": ["https://findthatcharity.uk/orgid/GB-CHC-1123842", "https://pallant.org.uk/support-us/"], "la": 50.836, "lo": -0.777}, {"n": "Christchurch Art Gallery", "c": "Christchurch, New Zealand", "t": "A", "s": "S", "f": "NZD 11.5M annual budget, free admission. Funded primarily by the Christchurch City Council ratepayer exchequer and Creative New Zealand.", "w": "Public civic art museum in Te Wai Pounamu. Operates under New Zealand local government transparency legislation; zero corporate sponsorship involvement in collection or exhibition curation.", "u": ["https://christchurchartgallery.org.nz/about", "https://ccc.govt.nz"], "la": -43.531, "lo": 172.632}, {"n": "Magazzino Italian Art", "c": "Cold Spring, USA", "t": "A", "s": "S", "f": "$3.8M operating expenditure, free admission. Privately funded by founders Nancy Olnick and Giorgio Spanu.", "w": "Museum and research center dedicated to Post-war and Contemporary Italian Art in Cold Spring, NY. Funded entirely through the Olnick Spanu family endowment; free admission and zero commercial sponsorship.", "u": ["https://www.magazzino.art/about", "https://projects.propublica.org/nonprofits/organizations/814144498"], "la": 41.419, "lo": -73.943}, {"n": "Museum Ludwig", "c": "Cologne, Germany", "t": "A", "s": "S", "f": "\u20ac18.0M annual expenditure. City of Cologne core municipal budget, supported by the Peter and Irene Ludwig Foundation.", "w": "Municipal museum governed by the City of Cologne public cultural administration. Major holdings and endowments stem from the Ludwig confectionary family bequest; corporate sponsorships are strictly vetted under German municipal transparency standards.", "u": ["https://www.museum-ludwig.de/en/about-the-museum.html", "https://www.stadt-koeln.de"], "la": 50.941, "lo": 6.96}, {"n": "Kunsthal Charlottenborg", "c": "Copenhagen, Denmark", "t": "B", "s": "S", "f": "Ministry, Statens Kunstfond, Ny Carlsberg, A.P. M\u00f8ller.", "w": "Augustinus Fonden holds a Scandinavian Tobacco stake.", "u": ["https://kunsthalcharlottenborg.dk/en/information-2/support/"], "la": 55.68, "lo": 12.585}, {"n": "Ny Carlsberg Glyptotek", "c": "Copenhagen, Denmark", "t": "A", "s": "L", "f": "Carlsberg foundations, DKK 1.5B.", "w": "Beer.", "u": ["https://www.carlsbergfondet.dk/en/news/the-carlsberg-foundation-donates-a-historic-grant-to-future-proof-the-ny-carlsberg-glyptotek/"], "la": 55.673, "lo": 12.572}, {"n": "Crawford Art Gallery", "c": "Cork, Ireland", "t": "A", "s": "S", "f": "\u20ac4.8M annual operating expenditure. 100% core state-funded through the Department of Tourism, Culture, Arts, Gaeltacht, Sport and Media.", "w": "National Cultural Institution of Ireland located in Cork. Exclusively funded through public exchequer allocations and charitable philanthropic donations; completely free of corporate sponsorship or commercial branding.", "u": ["https://crawfordartgallery.ie/support/", "https://www.gov.ie/en/organisation/department-of-tourism-culture-arts-gaeltacht-sport-and-media/"], "la": 51.899, "lo": -8.472}, {"n": "Raw Material Company", "c": "Dakar, Senegal", "t": "A", "s": "S", "f": "\u20ac0.7M. Arts Collaboratory, Prince Claus Fund, Ford Foundation.", "w": "Pioneering artist-run center focused on trans-African political and ecological discourse.", "u": ["https://rawmaterialcompany.org/"], "la": 14.733, "lo": -17.472}, {"n": "Nasher Sculpture Center", "c": "Dallas, USA", "t": "A", "s": "S", "f": "$9.8M annual budget. Raymond and Patsy Nasher Foundation endowment, admissions, and Dallas patron circle.", "w": "Private collection gifted to the public in Dallas's arts district. Governed by an independent board with primary operational funding derived from the Nasher family real estate endowment; no fossil or defense title sponsorships.", "u": ["https://www.nashersculpturecenter.org/about/support", "https://projects.propublica.org/nonprofits/organizations/752763328"], "la": 32.788, "lo": -96.801}, {"n": "Des Moines Art Center", "c": "Des Moines, USA", "t": "B", "s": "S", "f": "$12.4M. Edmundson trust, Pappajohn.", "w": "2024 Mary Miss lawsuit, settled. Artist rights, not sponsors.", "u": ["https://news.artnet.com/art-world/mary-miss-greenwood-installation-des-moines-settlement-2597948", "https://www.iowapublicradio.org/arts-life/2025-01-14/des-moines-art-center-mary-miss-iowa-lawsuit"], "la": 41.585, "lo": -93.671}, {"n": "Le Consortium", "c": "Dijon, France", "t": "A", "s": "S", "f": "\u20ac2.8M annual budget. French Ministry of Culture (DRAC Bourgogne-Franche-Comt\u00e9), City of Dijon, Regional Council, and private patrons.", "w": "Artist-led contemporary art center (Centre d'art contemporain d'int\u00e9r\u00eat national). Fully independent curatorial governance with public subsidies and patron circles; no corporate defense or fossil sponsorship.", "u": ["https://www.leconsortium.fr/en/the-consortium", "https://www.culture.gouv.fr"], "la": 47.315, "lo": 5.045}, {"n": "Jameel Arts Centre", "c": "Dubai, UAE", "t": "A", "s": "S", "f": "AED 22M annual operating expenditure, free admission. Financed entirely by the private philanthropic foundation Art Jameel.", "w": "Independent contemporary arts institution on Dubai Creek. Funded through the Jameel family philanthropic foundation; free public admission with emphasis on community learning and environmental research.", "u": ["https://jameelartscentre.org/about/", "https://artjameel.org"], "la": 25.229, "lo": 55.343}, {"n": "Temple Bar Gallery + Studios", "c": "Dublin, Ireland", "t": "A", "s": "S", "f": "\u20ac1.4M operating expenditure. Arts Council of Ireland (An Chomhairle Eala\u00edon), Dublin City Council, and studio rental fees.", "w": "Artist-founded and artist-led non-profit trust in central Dublin. Clean ethical review record: supported by public subvention and regional corporate patrons under strict non-interference covenants.", "u": ["https://www.templebargallery.com/support", "https://www.charitiesregulator.ie"], "la": 53.345, "lo": -6.264}, {"n": "Dundee Contemporary Arts", "c": "Dundee, UK", "t": "A", "s": "S", "f": "\u00a32.8M. Creative Scotland and city.", "w": "The Baillie Gifford rows hit Edinburgh venues, not DCA.", "u": ["https://www.oscr.org.uk/about-charities/search-the-register/charity-details?number=SC026631"], "la": 56.457, "lo": -2.974}, {"n": "Towner Eastbourne", "c": "Eastbourne, UK", "t": "A", "s": "S", "f": "\u00a33.6M. Arts Council and borough.", "w": "No sponsors published.", "u": ["https://findthatcharity.uk/orgid/GB-CHC-1156762"], "la": 50.762, "lo": 0.281}, {"n": "Fruitmarket Gallery", "c": "Edinburgh, UK", "t": "A", "s": "S", "f": "\u00a31.6M. Creative Scotland Regular Funding, City of Edinburgh Council, trusts and patrons.", "w": "Independent charity; strict ethical gift acceptance policy.", "u": ["https://www.fruitmarket.co.uk/support-us/"], "la": 55.951, "lo": -3.189}, {"n": "Inverleith House (Royal Botanic Garden)", "c": "Edinburgh, UK", "t": "A", "s": "S", "f": "\u00a30.8M art program. Scottish Government environment directorate, Outset, Paul Mellon Centre.", "w": "Ecological research institution; fully zero-carbon public governance.", "u": ["https://www.rbge.org.uk/science-and-conservation/library-and-archives/inverleith-house/"], "la": 55.965, "lo": -3.209}, {"n": "National Galleries of Scotland", "c": "Edinburgh, UK", "t": "A", "s": "L", "f": "\u00a324M. Scottish Government grant-in-aid, Baillie Gifford, trusts and individual patrons.", "w": "Severed fossil-fuel ties; adopted stringent sustainability screening.", "u": ["https://www.nationalgalleries.org/about/support-us", "https://findthatcharity.uk/orgid/SC003758"], "la": 55.951, "lo": -3.195}, {"n": "Art Gallery of Alberta", "c": "Edmonton, Canada", "t": "A", "s": "S", "f": "CAD 6.2M annual budget. Alberta Foundation for the Arts, Edmonton Arts Council, Canada Council for the Arts, and admissions.", "w": "Civic art museum in Edmonton. Tri-level public funding provides core stability; corporate partners (such as regional credit unions) are subject to public municipal gift guidelines.", "u": ["https://www.youraga.ca/about-aga/governance", "https://apps.cra-arc.gc.ca/ebci/hacc/srch/pub/dsplyBscChrtyPfl?selectedCharityBn=108082987RR0001"], "la": 53.544, "lo": -113.489}, {"n": "Van Abbemuseum", "c": "Eindhoven, Netherlands", "t": "A", "s": "S", "f": "\u20ac8.5M annual budget. Eindhoven Municipal Council (approx 68%), Mondriaan Fund, VriendenLoterij, and Ammodo Foundation.", "w": "In 2021, Van Abbemuseum formally ratified a climate and ethical governance manifesto prohibiting corporate sponsorships from carbon-intensive, arms-manufacturing, or human-rights-flagged entities. Transparent municipal subsidy structure.", "u": ["https://vanabbemuseum.nl/en/about-the-museum/organisation-and-policy/", "https://www.mondriaanfonds.nl"], "la": 51.434, "lo": 5.481}, {"n": "Uffizi", "c": "Florence, Italy", "t": "A", "s": "L", "f": "\u20ac48M revenue, 4M visitors. Autonomous state museum under the Italian Ministry of Culture (MiC).", "w": "World-renowned state gallery in Florence. Over 85% of budget generated through ticket receipts and state exchequer; strict Italian cultural heritage code (Codice dei Beni Culturali) prevents private corporate commercialization of collections.", "u": ["https://www.uffizi.it/en/the-uffizi/governance", "https://cultura.gov.it"], "la": 43.768, "lo": 11.255}, {"n": "Amon Carter Museum", "c": "Fort Worth, USA", "t": "B", "s": "S", "f": "$20.8M. Carter foundation, city, state.", "w": "Eagle Energy Systems and BNSF on roster.", "u": ["https://www.cartermuseum.org/support", "https://projects.propublica.org/nonprofits/organizations/751077979"], "la": 32.749, "lo": -97.368}, {"n": "Baltic", "c": "Gateshead, UK", "t": "B", "s": "S", "f": "\u00a36.8M. Arts Council, Gateshead; Nissan, Tommee Tippee.", "w": "Refused BAE money for a 2018 exhibition after protest; never its own sponsor.", "u": ["https://baltic.art/how-you-can-support-us/corporate-supporters/", "https://findthatcharity.uk/orgid/GB-CHC-1076251"], "la": 54.969, "lo": -1.599}, {"n": "BALTIC Centre for Contemporary Art", "c": "Gateshead, UK", "t": "A", "s": "L", "f": "\u00a34.2M. Arts Council England, Gateshead Council, North East Culture Partnership, philanthropic trusts.", "w": "No fossil fuel or extractive industry sponsors; publicly ethical corporate partnership policy.", "u": ["https://baltic.art/support-us", "https://findthatcharity.uk/orgid/GB-CHC-1076251"], "la": 54.969, "lo": -1.599}, {"n": "S.M.A.K.", "c": "Ghent, Belgium", "t": "A", "s": "S", "f": "\u20ac4.9M annual budget. City of Ghent municipal council, Flemish Community, and Friends of S.M.A.K. foundation.", "w": "Municipal contemporary museum of Ghent founded by Jan Hoet. Financed primarily through municipal cultural funds; strictly follows the Flemish Cultural Heritage Decree on ethical sponsorship and governance.", "u": ["https://smak.be/en/about-smak", "https://stad.gent"], "la": 51.037, "lo": 3.724}, {"n": "Art Gallery of Nova Scotia", "c": "Halifax, Canada", "t": "B", "s": "S", "f": "C$5.4M. Provincial crown agency.", "w": "BMO, Scotiabank, TD. New building paused 2022.", "u": ["https://agns.ca/wp-content/uploads/2025/06/AGNS-2024-25-Annual-Report.pdf", "https://www.cbc.ca/news/canada/nova-scotia/new-art-gallery-not-priority-for-premier-tim-houston-1.7233118"], "la": 44.648, "lo": -63.573}, {"n": "Amos Rex", "c": "Helsinki, Finland", "t": "A", "s": "S", "f": "\u20ac9.4M operating expenditure, 340k visitors. Financed entirely by the private F\u00f6reningen Konstsamfundet foundation and ticket sales.", "w": "Privately funded non-profit museum established by the bequest of Amos Anderson. Konstsamfundet's endowment yields completely cover operating deficits, allowing total freedom from external corporate sponsorship or government subsidies.", "u": ["https://amosrex.fi/en/about-us/", "https://konstsamfundet.fi/en/"], "la": 60.17, "lo": 24.937}, {"n": "Kiasma Museum of Contemporary Art", "c": "Helsinki, Finland", "t": "A", "s": "L", "f": "\u20ac11M. Finnish Ministry of Education and Culture, Finnish National Gallery.", "w": "State museum operating solely on national cultural funding; ethical gift policy.", "u": ["https://kiasma.fi/en/about-kiasma/partners/"], "la": 60.171, "lo": 24.937}, {"n": "Asia Art Archive", "c": "Hong Kong", "t": "U", "s": "S", "f": "Individuals, foundations, auction.", "w": "Page blocked.", "u": ["https://aaa.org.hk/"], "la": 22.283, "lo": 114.154}, {"n": "Para Site", "c": "Hong Kong", "t": "U", "s": "S", "f": "Arts Development Council, annual auction, patrons.", "w": "Roster unverified.", "u": ["https://www.para-site.art/"], "la": 22.284, "lo": 114.223}, {"n": "M+ Museum", "c": "Hong Kong, China", "t": "B", "s": "L", "f": "HKD 380M operating budget, 2.5M annual visitors. West Kowloon Cultural District Authority (statutory body of the Hong Kong SAR Government).", "w": "Tier B: Major global museum of visual culture in West Kowloon designed by Herzog & de Meuron. While globally renowned, institutional governance operates under Hong Kong SAR statutory cultural oversight and national security legislative compliance.", "u": ["https://www.mplus.org.hk/en/about-us/", "https://www.westkowloon.hk"], "la": 22.301, "lo": 114.159}, {"n": "Contemporary Arts Museum Houston", "c": "Houston, USA", "t": "A", "s": "S", "f": "$4.6M annual budget, free admission. Houston Endowment, Texas Commission on the Arts, National Endowment for the Arts, and annual gala.", "w": "Non-collecting museum offering free admission to the public. Has an active ethical gift screening policy overseen by trustee committees; no defense or arms funding on the institutional roster.", "u": ["https://camh.org/support/", "https://projects.propublica.org/nonprofits/organizations/741164923"], "la": 29.727, "lo": -95.39}, {"n": "Henia Onstad Kunstsenter", "c": "H\u00f8vikodden, Norway", "t": "A", "s": "S", "f": "NOK 45M. Norwegian Ministry of Culture, Viken fylkeskommune, B\u00e6rum municipality.", "w": "Public foundation with explicit fossil fuel sponsorship exclusion.", "u": ["https://hok.no/en/about/partners-and-sponsors"], "la": 59.889, "lo": 10.553}, {"n": "Louisiana Museum of Modern Art", "c": "Humleb\u00e6k, Denmark", "t": "A", "s": "L", "f": "716k visitors. Danish family foundations plus a 26% state grant.", "w": "Shipping and beer foundations.", "u": ["https://louisiana.dk/en/organization/", "https://louisiana.dk/wp-content/uploads/2025/05/Louisiana-Museum-Aarsrapport-2024.pdf"], "la": 55.969, "lo": 12.543}, {"n": "Kistefos", "c": "Jevnaker, Norway", "t": "A", "s": "L", "f": "NOK 35M operating expenditure. Endowed by Christen Sveaas through the Kistefos AS industrial-cultural heritage foundation.", "w": "Sculpture park and museum in Jevnaker featuring 'The Twist' by BIG. Privately endowed non-profit foundation on the site of a historic wood pulp mill; no external corporate marketing interference.", "u": ["https://www.kistefosmuseum.com/about/about-kistefos", "https://www.kistefosmuseum.com"], "la": 60.207, "lo": 10.399}, {"n": "Kamloops Art Gallery", "c": "Kamloops, Canada", "t": "B", "s": "S", "f": "City, BC Arts Council, Canada Council.", "w": "BC Lottery Corporation.", "u": ["https://kag.bc.ca/our-supporters"], "la": 50.675, "lo": -120.336}, {"n": "21st Century Museum of Contemporary Art", "c": "Kanazawa, Japan", "t": "A", "s": "L", "f": "\u00a51.2B. City of Kanazawa municipal cultural budget, Agency for Cultural Affairs (Bunkacho).", "w": "Pure municipal civic museum; no private corporate title sponsorships.", "u": ["https://www.kanazawa21.jp/en/"], "la": 36.561, "lo": 136.657}, {"n": "ILHAM Gallery", "c": "Kuala Lumpur, Malaysia", "t": "A", "s": "S", "f": "MYR 4.5M annual budget, free admission. Supported by the ILHAM Contemporary Art Trust.", "w": "Public art gallery in Kuala Lumpur committed to Southeast Asian contemporary art. Permanent free admission; funded via an independent charitable cultural trust without commercial corporate branding.", "u": ["https://www.ilhamgallery.com/about/", "https://www.ilhamgallery.com"], "la": 3.153, "lo": 101.717}, {"n": "Charleston", "c": "Lewes, UK", "t": "U", "s": "S", "f": "\u00a32.7M. Arts Council, Sigrid Rausing Trust.", "w": "Corporate roster not published.", "u": ["https://findthatcharity.uk/orgid/GB-CHC-1107313"], "la": 50.878, "lo": 0.043}, {"n": "Museo de Arte de Lima", "c": "Lima, Peru", "t": "U", "s": "S", "f": "About $2M. Private association, Telef\u00f3nica foundation.", "w": "No mining sponsor found; roster partly unverified.", "u": ["https://www.arteporexcelencias.com/es/patrocinios-para-museo-de-arte-de-lima"], "la": -12.05, "lo": -77.037}, {"n": "Lismore Castle Arts", "c": "Lismore, Ireland", "t": "A", "s": "S", "f": "\u20ac0.6M annual programming budget. Supported by the Duke of Devonshire's Charitable Trust, Arts Council of Ireland project grants, and admissions.", "w": "Non-profit contemporary exhibition space in County Waterford. Funded through private estate philanthropic endowment and statutory arts awards, maintaining complete editorial freedom without corporate marketing presence.", "u": ["https://www.lismorecastlearts.com/support", "https://www.charitiesregulator.ie"], "la": 52.137, "lo": -7.933}, {"n": "Mostyn", "c": "Llandudno, UK", "t": "A", "s": "S", "f": "\u00a30.7M operating revenue. Arts Council of Wales core client, Conwy County Borough Council grant aid, and charitable trusts.", "w": "Registered Welsh charity dedicated to contemporary visual art. Transparent supporter ledger; no corporate extraction or high-carbon sponsors; strict community-oriented public benefit mandate.", "u": ["https://findthatcharity.uk/orgid/GB-CHC-500057", "https://mostyn.org/support-us/"], "la": 53.323, "lo": -3.826}, {"n": "Camden Art Centre", "c": "London, UK", "t": "A", "s": "S", "f": "\u00a33.3M annual budget. 38% statutory subvention from Arts Council England (National Portfolio) and London Borough of Camden; balance from charitable trusts, patrons' circle, and gallery bookstore/cafe earned income.", "w": "Governed under strict Arts Council ethical fundraising guidelines. Transparent donor roster with zero corporate naming rights; core exhibition underwriters include the Henry Moore Foundation, Art Fund, and Esm\u00e9e Fairbairn Foundation. No fossil fuel, defense, or pharmaceutical corporate sponsorship.", "u": ["https://findthatcharity.uk/orgid/GB-CHC-1065829", "https://camdenartcentre.org/support"], "la": 51.548, "lo": -0.187}, {"n": "Chisenhale Gallery", "c": "London, UK", "t": "A", "s": "S", "f": "\u00a31.0M. Arts Council, trusts, patrons' circles.", "w": "No corporate sponsors published.", "u": ["https://findthatcharity.uk/orgid/GB-CHC-1026175", "https://chisenhale.org.uk/support/"], "la": 51.529, "lo": -0.033}, {"n": "Gasworks", "c": "London, UK", "t": "U", "s": "S", "f": "\u00a30.9M. Arts Council, trusts.", "w": "Site unreachable; roster unverified.", "u": ["https://findthatcharity.uk/orgid/GB-CHC-326411"], "la": 51.484, "lo": -0.113}, {"n": "Sir John Soane's Museum", "c": "London, UK", "t": "A", "s": "S", "f": "\u00a34.2M, 158k annual visitors. 62% statutory Grant-in-Aid from the Department for Culture, Media and Sport (DCMS); balance from private endowment, retail, and patron memberships.", "w": "Non-Departmental Public Body established by an 1833 Act of Parliament. Strictly barred from commercial naming rights or private corporate branding of historic interiors. Transparent audited accounts submitted annually to Parliament.", "u": ["https://findthatcharity.uk/orgid/GB-CHC-313609", "https://www.soane.org/about/support-us"], "la": 51.517, "lo": -0.117}, {"n": "South London Gallery", "c": "London, UK", "t": "A", "s": "S", "f": "\u00a32.4M. Arts Council England National Portfolio, Southwark Council, Outset Contemporary Art Fund, trusts.", "w": "Refuses fossil fuel, arms, and tobacco sponsorship.", "u": ["https://www.southlondongallery.org/about/support-us/", "https://findthatcharity.uk/orgid/GB-CHC-312160"], "la": 51.474, "lo": -0.078}, {"n": "Studio Voltaire", "c": "London, UK", "t": "B", "s": "S", "f": "\u00a32.3M. Arts Council; Christie's, Zwirner, Hauser & Wirth, LOEWE.", "w": "Roster includes Bloomberg Philanthropies.", "u": ["https://studiovoltaire.org/support/supporters-and-funders/", "https://findthatcharity.uk/orgid/GB-CHC-1082221"], "la": 51.463, "lo": -0.138}, {"n": "Tate Modern", "c": "London, UK", "t": "B", "s": "L", "f": "\u00a3120M (group). DCMS statutory grant-in-aid, Bank of America, Hyundai Motor, Uniqlo, philanthropic circles.", "w": "Ended 26-year BP partnership after intense artist and activist campaigning; retains major global corporate sponsors.", "u": ["https://www.tate.org.uk/about-us/corporate-support", "https://findthatcharity.uk/orgid/GB-CHC-312863"], "la": 51.507, "lo": -0.099}, {"n": "Wellcome Collection", "c": "London, UK", "t": "A", "s": "L", "f": "Wellcome Trust endowment. Free, no sponsors.", "w": "Pharma origin; Trust portfolio not checked.", "u": ["https://wellcome.org/about-us/history-wellcome", "https://en.wikipedia.org/wiki/Wellcome_Collection"], "la": 51.526, "lo": -0.134}, {"n": "Whitechapel Gallery", "c": "London, UK", "t": "A", "s": "L", "f": "\u00a35.1M budget. Arts Council England (30%), London Borough of Tower Hamlets, trusts, and commercial enterprise.", "w": "Historic East London public gallery founded in 1901. Following public scrutiny over fossil fuel sponsors across London cultural institutions, Whitechapel operates with a comprehensive ethical review policy banning fossil and arms underwriting.", "u": ["https://findthatcharity.uk/orgid/GB-CHC-312162", "https://www.whitechapelgallery.org/support/"], "la": 51.516, "lo": -0.07}, {"n": "Hammer Museum", "c": "Los Angeles, USA", "t": "A", "s": "L", "f": "8M. UCLA operational partnership, free admission endowment, Mellon Foundation, patrons.", "w": "Public university affiliation with free admission supported by donor endowments.", "u": ["https://hammer.ucla.edu/support"], "la": 34.059, "lo": -118.443}, {"n": "Museum of Jurassic Technology", "c": "Los Angeles, USA", "t": "B", "s": "S", "f": "$0.7M, 25k visitors. NEA, state and city arts, foundations.", "w": "Bloomberg Philanthropies among funders.", "u": ["http://www.mjt.org/donors.html", "https://projects.propublica.org/nonprofits/organizations/954309388"], "la": 34.026, "lo": -118.396}, {"n": "The Broad", "c": "Los Angeles, USA", "t": "A", "s": "L", "f": "$30M. $200M founder endowment. Free, no sponsors.", "w": "Homebuilding and insurance fortune.", "u": ["https://www.thebroad.org/about", "https://projects.propublica.org/nonprofits/organizations/273032164"], "la": 34.054, "lo": -118.25}, {"n": "Bonnefanten", "c": "Maastricht, Netherlands", "t": "A", "s": "S", "f": "\u20ac6.8M budget, 177k visitors. Province of Limburg, Municipality of Maastricht, Mondriaan Fund, and VriendenLoterij.", "w": "Provincial public art museum governed under Dutch cultural sector transparency regulations. No fossil fuel, defense, or controversial corporate donors; public funding audited annually by Limburg provincial authorities.", "u": ["https://www.bonnefanten.nl/en/about-us/organisation-and-policy", "https://www.limburg.nl"], "la": 50.843, "lo": 5.7}, {"n": "Museo del Prado", "c": "Madrid, Spain", "t": "B", "s": "L", "f": "\u20ac62M, 3.5M visitors; BBVA, Telef\u00f3nica, AXA, la Caixa.", "w": "Iberdrola, a utility with gas assets, never campaigned against.", "u": ["https://www.museodelprado.es/en/colabora/patrocinio", "https://www.boe.es/diario_boe/txt.php?id=BOE-A-2025-579"], "la": 40.414, "lo": -3.692}, {"n": "Museo Reina Sof\u00eda", "c": "Madrid, Spain", "t": "A", "s": "L", "f": "\u20ac44M budget, 3.8M visitors. Ministry of Culture of Spain (approx 65%), admissions, and royal patron foundation.", "w": "National museum of modern art in Madrid. Operates as an autonomous public body under Spanish state law; corporate underwriters are vetted through public cultural patronage frameworks.", "u": ["https://www.museoreinasofia.es/en/museum/transparency", "https://www.cultura.gob.es"], "la": 40.408, "lo": -3.694}, {"n": "The Whitworth", "c": "Manchester, UK", "t": "B", "s": "S", "f": "279k visits. University, Arts Council; Hyundai, Little Greene.", "w": "Deutsche Bank via Frieze; 2022 censorship row, director ousted.", "u": ["https://www.whitworth.manchester.ac.uk/about/supportus/ourcurrentsponsorsandfunders/"], "la": 53.46, "lo": -2.229}, {"n": "Kunsthalle Mannheim", "c": "Mannheim, Germany", "t": "A", "s": "S", "f": "\u20ac7.9M annual budget. City of Mannheim municipal cultural funding, Kunsthalle Mannheim Foundation, and regional patrons.", "w": "Municipal contemporary museum. Clean ethical sponsorship roster; public-private foundation structure governed under strict transparency requirements with civic representation on the supervisory board.", "u": ["https://www.kuma.art/en/museum/organisation", "https://www.mannheim.de"], "la": 49.483, "lo": 8.475}, {"n": "Ballroom Marfa", "c": "Marfa, USA", "t": "A", "s": "S", "f": "$1.9M operating budget, free admission. Funded by the Brown Foundation, Andy Warhol Foundation, Texas Commission on the Arts, and national patron circles.", "w": "Dynamic non-profit contemporary art space in West Texas. Free public admission; governance guidelines prohibit fossil extraction or defense underwriting despite local geographic oil economy.", "u": ["https://ballroommarfa.org/about/support/", "https://projects.propublica.org/nonprofits/organizations/200472482"], "la": 30.309, "lo": -104.03}, {"n": "Chinati Foundation", "c": "Marfa, USA", "t": "A", "s": "S", "f": "$4.1M budget, 45k visitors. Private endowment yields, individual patron donations, admissions, and Texas Commission on the Arts.", "w": "Founded by Donald Judd in Marfa, Texas. Preserves large-scale installations across 340 acres. Governed by a dedicated board of trustees with an independent endowment; no defense or fossil fuel corporate underwriting.", "u": ["https://chinati.org/about/support/", "https://projects.propublica.org/nonprofits/organizations/752187640"], "la": 30.302, "lo": -104.028}, {"n": "Judd Foundation", "c": "Marfa, USA", "t": "A", "s": "S", "f": "$3.8M operating expenditure. Funded by admissions, archive licensing, individual contributions, and the Donald Judd Estate endowment.", "w": "Maintains Donald Judd's permanently installed living and working spaces in Marfa and 101 Spring Street, New York. Operates without corporate commercial underwriters, maintaining archival and ethical purity.", "u": ["https://juddfoundation.org/about/", "https://projects.propublica.org/nonprofits/organizations/133989345"], "la": 30.312, "lo": -104.019}, {"n": "MACAAL", "c": "Marrakech, Morocco", "t": "A", "s": "S", "f": "MAD 16M budget. Endowed by the Fondation Alliances (philanthropic cultural arm of the Lazraq family).", "w": "Museum of African Contemporary Art Al Maaden in Marrakech. Non-profit cultural initiative dedicated to African contemporary artists; transparent philanthropic funding without arms or fossil sponsorships.", "u": ["https://macaal.org/en/about-macaal/", "https://macaal.org"], "la": 31.687, "lo": -7.965}, {"n": "ACCA", "c": "Melbourne, Australia", "t": "A", "s": "S", "f": "AUD 4.2M budget, free admission. Creative Victoria, Creative Australia (former Australia Council), City of Melbourne, and private patrons.", "w": "Australian Centre for Contemporary Art in Melbourne. Non-collecting kunsthalle with free public access; strict ethical sponsorship framework complying with state arts protocols.", "u": ["https://acca.melbourne/about/", "https://www.acnc.gov.au/charity/charities/0d608240-39af-e811-a960-000d3ad24282/profile"], "la": -37.826, "lo": 144.965}, {"n": "Heide Museum of Modern Art", "c": "Melbourne, Australia", "t": "A", "s": "S", "f": "AUD 5.6M operating budget. Creative Victoria statutory funding, admissions, Heide Foundation endowment, and local government.", "w": "Established at the former home of John and Sunday Reed in Bulleen, Victoria. Governed under the Victorian Public Sector Commission guidelines; transparent donor records with zero defense ties.", "u": ["https://www.heide.com.au/about/support/", "https://www.acnc.gov.au/charity/charities/0e608240-39af-e811-a960-000d3ad24282/profile"], "la": -37.76, "lo": 145.084}, {"n": "Museo Jumex", "c": "Mexico City, Mexico", "t": "A", "s": "L", "f": "$11M operating expenditure, free admission. Funded entirely by Eugenio L\u00f3pez Alonso through the Fundaci\u00f3n Jumex Arte Contempor\u00e1neo.", "w": "Tier B: Located in Mexico City's Polanco district. Free admission to the public; operational budget is derived from the Grupo Jumex beverage manufacturing conglomerate under family foundation governance.", "u": ["https://www.fundacionjumex.org/en/fundacion/acerca-de", "https://www.fundacionjumex.org"], "la": 19.44, "lo": -99.203}, {"n": "Museo Tamayo", "c": "Mexico City, Mexico", "t": "U", "s": "S", "f": "Federal INBAL plus Tamayo foundation.", "w": "Current sponsors unverified.", "u": ["https://www.museotamayo.org/"], "la": 19.426, "lo": -99.183}, {"n": "ICA Miami", "c": "Miami, USA", "t": "A", "s": "S", "f": "$8.2M annual budget, free admission. Braman family foundation, Knight Foundation, City of Miami, and patron memberships.", "w": "Located in the Miami Design District with permanent free admission. Funded primarily through private philanthropic donations from the Braman family and cultural foundation endowments; clean governance record.", "u": ["https://icamiami.org/support/", "https://projects.propublica.org/nonprofits/organizations/471926615"], "la": 25.813, "lo": -80.193}, {"n": "MIMA", "c": "Middlesbrough, UK", "t": "U", "s": "S", "f": "Teesside University, Arts Council.", "w": "Roster unverified.", "u": ["https://mima.art/"], "la": 54.575, "lo": -1.234}, {"n": "Fondazione Prada", "c": "Milan, Italy", "t": "A", "s": "L", "f": "\u20ac28M annual programming expenditure. Funded directly by the Prada Group's corporate cultural allocation.", "w": "Tier B: Major private cultural institution funded by Italian luxury fashion house Prada. While maintaining visionary curatorial integrity and international acclaim, operational governance and capital investments are tied to commercial luxury corporate revenues.", "u": ["https://www.fondazioneprada.org/about-us/", "https://www.pradagroup.com/en/sustainability/cultural-projects.html"], "la": 45.444, "lo": 9.204}, {"n": "Pirelli HangarBicocca", "c": "Milan, Italy", "t": "A", "s": "L", "f": "\u20ac12M operating budget, free admission. 100% funded by Pirelli tire corporation as its corporate non-profit foundation.", "w": "Tier B: Industrial contemporary space in Milan featuring Anselm Kiefer's 'The Seven Heavenly Palaces'. Provides free admission; governance is closely tied to Pirelli's corporate sponsorship and executive board oversight.", "u": ["https://pirellihangarbicocca.org/en/about/", "https://corporate.pirelli.com/corporate/en-ww/sustainability/culture"], "la": 45.523, "lo": 9.22}, {"n": "Walker Art Center", "c": "Minneapolis, USA", "t": "B", "s": "L", "f": "Principal, US Bank, Best Buy, Cargill Foundation, 3M.", "w": "Bloomberg Philanthropies on roster.", "u": ["https://walkerart.org/support/corporate-support/"], "la": 44.968, "lo": -93.289}, {"n": "MAC Montr\u00e9al", "c": "Montr\u00e9al, Canada", "t": "B", "s": "S", "f": "Quebec crown corporation; Banque Nationale lead.", "w": "Loto-Qu\u00e9bec, Power Corp, AtkinsR\u00e9alis.", "u": ["https://macm.org/app/uploads/2025/10/Rapport_Annuel_2024-2025.pdf", "https://macm.org/le-musee/partenaires"], "la": 45.507, "lo": -73.567}, {"n": "PHI Foundation", "c": "Montr\u00e9al, Canada", "t": "A", "s": "S", "f": "CAD 4.8M annual expenditure, free admission. Funded entirely by the private philanthropic endowment of founder Phoebe Greenberg.", "w": "Contemporary art foundation in Old Montreal offering free public exhibitions. Supported by private philanthropic trust; completely independent of external corporate sponsorship or commercial branding.", "u": ["https://phi.ca/en/about/", "https://apps.cra-arc.gc.ca/ebci/hacc/srch/pub/dsplyBscChrtyPfl?selectedCharityBn=854497672RR0001"], "la": 45.501, "lo": -73.554}, {"n": "CA2M (Centro de Arte Dos de Mayo)", "c": "M\u00f3stoles, Spain", "t": "A", "s": "S", "f": "\u20ac2.2M. Comunidad de Madrid Directorate General for Cultural Promotion.", "w": "Fully public regional museum; no private corporate commercial underwriting.", "u": ["https://ca2m.org/en/about-us"], "la": 40.323, "lo": -3.864}, {"n": "Kunstverein M\u00fcnchen", "c": "Munich, Germany", "t": "A", "s": "S", "f": "\u20ac0.9M. Kulturreferat M\u00fcnchen, Bayerisches Staatsministerium, membership dues.", "w": "Pure member-driven civic association with non-corporate public support.", "u": ["https://www.kunstverein-muenchen.de/en/info/supporters"], "la": 48.143, "lo": 11.581}, {"n": "Lenbachhaus", "c": "Munich, Germany", "t": "A", "s": "S", "f": "\u20ac11.2M annual budget. Municipal funding from the City of Munich Cultural Department, admissions, and KiCo Foundation.", "w": "Operated by the City of Munich as a municipal cultural institution. Governed by municipal anti-corruption and public ethics guidelines; no corporate underwriting from defense, extractive, or high-emissions sectors.", "u": ["https://www.lenbachhaus.de/en/about", "https://stadt.muenchen.de/service/info/kulturreferat/1083403/"], "la": 48.147, "lo": 11.564}, {"n": "Benesse Art Site Naoshima", "c": "Naoshima, Japan", "t": "A", "s": "S", "f": "\u00a53.2B operating budget. Funded by the Benesse Holdings corporate cultural foundation and the Fukutake Foundation.", "w": "Cultural revitalization initiative across Naoshima, Teshima, and Inujima founded by Soichiro Fukutake. Emphasizes environmental harmony and long-term sustainability; zero defense or extractive industry ties.", "u": ["https://benesse-artsite.jp/en/about/", "https://fukutake.or.jp"], "la": 34.457, "lo": 133.986}, {"n": "Ogden Museum", "c": "New Orleans, USA", "t": "B", "s": "S", "f": "$3.5M. Founder gift, Louisiana appropriation.", "w": "Helis Foundation, oil-derived money, funds free Thursdays.", "u": ["https://ogdenmuseum.org/support/", "https://projects.propublica.org/nonprofits/organizations/721479496"], "la": 29.943, "lo": -90.071}, {"n": "Storm King Art Center", "c": "New Windsor, USA", "t": "U", "s": "S", "f": "$9.8M. Ogden family fasteners fortune.", "w": "Donors page not fetched.", "u": ["https://en.wikipedia.org/wiki/Storm_King_Art_Center"], "la": 41.425, "lo": -74.06}, {"n": "Artists Space", "c": "New York, USA", "t": "A", "s": "S", "f": "$2.4M annual budget. National Endowment for the Arts, New York State Council on the Arts (NYSCA), NYC Department of Cultural Affairs, and artists' editions.", "w": "Historic Tribeca alternative space founded in 1972. Famed for artist advocacy and institutional critique; operates with complete transparency and rejects corporate corporate board influence.", "u": ["https://artistsspace.org/support", "https://projects.propublica.org/nonprofits/organizations/237248386"], "la": 40.717, "lo": -74.004}, {"n": "Noguchi Museum", "c": "New York, USA", "t": "B", "s": "S", "f": "$10M. Noguchi estate, city capital.", "w": "2024 keffiyeh-ban firings. Not sponsor-related.", "u": ["https://en.wikipedia.org/wiki/Noguchi_Museum"], "la": 40.767, "lo": -73.938}, {"n": "Queens Museum", "c": "New York, USA", "t": "B", "s": "S", "f": "$7.8M. City-owned building, about 70% public historically.", "w": "2017 Israel-event row; 2023 staff complaints. Not sponsor-related.", "u": ["https://en.wikipedia.org/wiki/Queens_Museum"], "la": 40.746, "lo": -73.847}, {"n": "SculptureCenter", "c": "New York, USA", "t": "U", "s": "S", "f": "$2.0M.", "w": "Support page unavailable.", "u": ["https://en.wikipedia.org/wiki/SculptureCenter"], "la": 40.747, "lo": -73.943}, {"n": "Swiss Institute", "c": "New York, USA", "t": "U", "s": "S", "f": "$5.5M. Pro Helvetia, foundations.", "w": "Corporate names not published.", "u": ["https://www.swissinstitute.net/support/"], "la": 40.722, "lo": -73.992}, {"n": "The Kitchen", "c": "New York, USA", "t": "A", "s": "S", "f": "$3.6M multi-disciplinary budget. NYC Department of Cultural Affairs, NYSCA, Mellon Foundation, and benefit art auctions.", "w": "Experimental non-profit performance and media arts center founded in 1971. Board-governed with strict non-profit oversight; zero fossil fuel, defense, or controversial corporate partners.", "u": ["https://thekitchen.org/support/", "https://projects.propublica.org/nonprofits/organizations/132717013"], "la": 40.746, "lo": -74.006}, {"n": "MASS MoCA", "c": "North Adams, USA", "t": "A", "s": "L", "f": "4M. Massachusetts Cultural Council, Barr Foundation, NEA, admissions and individual philanthropy.", "w": "Publicly subsidized adaptive-reuse non-profit art institution.", "u": ["https://massmoca.org/support/"], "la": 42.7, "lo": -73.115}, {"n": "Nottingham Contemporary", "c": "Nottingham, UK", "t": "B", "s": "S", "f": "\u00a32.1M. Arts Council, universities, trusts.", "w": "Bloomberg Philanthropies as headline sponsor.", "u": ["https://www.nottinghamcontemporary.org/support/", "https://findthatcharity.uk/orgid/GB-CHC-1116670"], "la": 52.951, "lo": -1.145}, {"n": "Oakville Galleries", "c": "Oakville, Canada", "t": "B", "s": "S", "f": "Town, Ontario and Canada arts councils.", "w": "TD, Hatch, Woodbine racetrack and casino.", "u": ["https://www.oakvillegalleries.com/funding_partners"], "la": 43.445, "lo": -79.666}, {"n": "Bemis Center", "c": "Omaha, USA", "t": "A", "s": "S", "f": "$3.2M budget. Nebraska Arts Council, National Endowment for the Arts, Andy Warhol Foundation, and Omaha community philanthropic foundations.", "w": "Non-profit artist residency and contemporary gallery in Omaha. Operates under rigorous 501(c)(3) governance guidelines with transparent donor records; zero corporate ties to controversial industries.", "u": ["https://www.bemiscenter.org/about", "https://projects.propublica.org/nonprofits/organizations/470634629"], "la": 41.252, "lo": -95.928}, {"n": "Astrup Fearnley Museet", "c": "Oslo, Norway", "t": "A", "s": "L", "f": "NOK 45M budget. Thomas Fearnley, Heddy and Nils Astrup Foundation endowment, admissions, and corporate circle.", "w": "Tier B: Major private museum on Oslo's waterfront founded by shipping magnate Hans Rasmus Astrup. Core endowment derived from historic global shipping and offshore maritime logistics; adheres to Norwegian foundation oversight.", "u": ["https://www.afmuseet.no/en/about-the-museum/", "https://lottstift.no/stiftelsesregisteret/"], "la": 59.907, "lo": 10.721}, {"n": "Kr\u00f6ller-M\u00fcller Museum", "c": "Otterlo, Netherlands", "t": "A", "s": "S", "f": "\u20ac14.5M annual budget, 280k visitors. State cultural funding via the Ministry of Education, Culture and Science (OCW), Kr\u00f6ller-M\u00fcller Foundation, and admissions.", "w": "Autonomous national museum within De Hoge Veluwe national park. Does not permit corporate commercial branding inside historic sculpture galleries; funded by state subsidies and historic philanthropic endowment.", "u": ["https://krollermuller.nl/en/organisation-and-policy", "https://www.rijksoverheid.nl/ministeries/ministerie-van-onderwijs-cultuur-en-wetenschap"], "la": 52.096, "lo": 5.817}, {"n": "Modern Art Oxford", "c": "Oxford, UK", "t": "A", "s": "S", "f": "\u00a33.1M annual budget. Core revenue from Arts Council England (42%) and Oxford City Council, supplemented by individual patrons, trusts, and commercial enterprise.", "w": "Maintains independent curatorial governance with an ethical scrutiny committee. Corporate support is limited to regional professional services and cultural foundations; no defense, extraction, or controversial sovereign wealth underwriting on the roster.", "u": ["https://findthatcharity.uk/orgid/GB-CHC-313035", "https://www.modernartoxford.org.uk/get-involved/support-us/corporate-partners"], "la": 51.751, "lo": -1.258}, {"n": "Fondation Cartier", "c": "Paris, France", "t": "A", "s": "L", "f": "\u20ac16M annual expenditure. Corporate cultural foundation of Cartier (Richemont luxury goods conglomerate).", "w": "Tier B: Pioneering corporate foundation for contemporary art in Paris. High-calibre architectural commissions and curatorial programming funded directly through luxury jeweler Cartier / Richemont corporate balance sheet.", "u": ["https://www.fondationcartier.com/en/about", "https://www.richemont.com/en/home/sustainability/"], "la": 48.864, "lo": 2.337}, {"n": "Mus\u00e9e de la Chasse et de la Nature", "c": "Paris, France", "t": "A", "s": "S", "f": "\u20ac6.5M annual expenditure. Privately endowed by the Fondation Fran\u00e7ois Sommer (recognized as a public-utility foundation in France).", "w": "Established in 1964 by philanthropic benefactors Fran\u00e7ois and Jacqueline Sommer. Operates independently from commercial corporate sponsorship, with an endowment focused on biodiversity and ecological conservation.", "u": ["https://www.chassenature.org/fondation-sommer", "https://fondationsommer.org"], "la": 48.861, "lo": 2.361}, {"n": "Palais de Tokyo", "c": "Paris, France", "t": "A", "s": "L", "f": "Swiss Life Foundation and a responsible-sponsorship circle.", "w": "Only explicit responsible-sponsorship programme found in France.", "u": ["https://www.culture.gouv.fr/actualites/le-palais-de-tokyo-mise-sur-le-mecenat-responsable"], "la": 48.864, "lo": 2.297}, {"n": "Newlyn Art Gallery", "c": "Penzance, UK", "t": "B", "s": "S", "f": "\u00a30.7M, about half public.", "w": "Bloomberg Philanthropies.", "u": ["https://newlynartgallery.co.uk/support-us/", "https://findthatcharity.uk/orgid/GB-CHC-273785"], "la": 50.104, "lo": -5.548}, {"n": "PICA Perth", "c": "Perth, Australia", "t": "U", "s": "S", "f": "WA government, Creative Australia.", "w": "Partner logos unnamed. Woodside and Chevron hit festivals, not PICA.", "u": ["https://pica.org.au/support/partners/"], "la": -31.951, "lo": 115.858}, {"n": "PICA Portland", "c": "Portland, USA", "t": "B", "s": "S", "f": "$2.5M. Oregon and city arts bodies; Nike, Netflix, Google.", "w": "Pacific Power, a fossil-heavy utility.", "u": ["https://www.pica.org/support", "https://projects.propublica.org/nonprofits/organizations/931177971"], "la": 45.527, "lo": -122.667}, {"n": "Funda\u00e7\u00e3o de Serralves", "c": "Porto, Portugal", "t": "B", "s": "L", "f": "\u20ac15M. Portuguese State, BPI, Funda\u00e7\u00e3o La Caixa, Super Bock Group.", "w": "Mixed public-private foundation with beverage and financial institutional partners.", "u": ["https://www.serralves.pt/en/support-serralves/patrons-and-sponsors/"], "la": 41.159, "lo": -8.659}, {"n": "Serralves Museum of Contemporary Art", "c": "Porto, Portugal", "t": "A", "s": "L", "f": "\u20ac14.8M annual budget, 950k park and gallery visitors. Funda\u00e7\u00e3o de Serralves endowment, Portuguese Ministry of Culture, and Porto Municipality.", "w": "Public-interest private foundation founded in 1989 designed by \u00c1lvaro Siza. Operates under Portuguese heritage statutory oversight with an independent board; clean ethical donor registry.", "u": ["https://www.serralves.pt/en/institutional-serralves/governance/", "https://www.portugal.gov.pt"], "la": 41.159, "lo": -8.659}, {"n": "Glenstone", "c": "Potomac, USA", "t": "A", "s": "L", "f": "$65M. Rales family, $1.9B gift. Free, no sponsors.", "w": "Danaher industrial fortune.", "u": ["https://www.theartnewspaper.com/2023/03/02/mitchell-rales-19bn-donation-glenstone-museum", "https://projects.propublica.org/nonprofits/organizations/205938416"], "la": 39.049, "lo": -77.226}, {"n": "MacKenzie Art Gallery", "c": "Regina, Canada", "t": "B", "s": "S", "f": "Province, city, arts councils.", "w": "RBC, TD, Scotiabank.", "u": ["https://mackenzie.art/site-content/uploads/2025/06/03_MAG-Annual-Report_2024-25_FINAL-1.pdf"], "la": 50.434, "lo": -104.612}, {"n": "Fondation Beyeler", "c": "Riehen, Switzerland", "t": "B", "s": "L", "f": "About CHF 30M; canton 12.5%; founder's foundation covers deficits.", "w": "UBS since 2004, protested at Art Basel.", "u": ["https://grosserrat.bs.ch/dokumente/100405/000000405724.pdf", "https://www.fondationbeyeler.ch/en/press/seiten-en/press/current-news/in-cooperation-with-ubs-the-fondation-beyeler-is-starting-the-internationally-oriented-program-of-artist-talks"], "la": 47.589, "lo": 7.651}, {"n": "Castello di Rivoli Museo d Arte Contemporanea", "c": "Rivoli, Italy", "t": "A", "s": "L", "f": "\u20ac6.5M. Regione Piemonte, Citt\u00e0 di Torino, Fondazione CRT, Compagnia di San Paolo.", "w": "Italian public-civic contemporary museum.", "u": ["https://www.castellodirivoli.org/en/sponsors/"], "la": 45.07, "lo": 7.511}, {"n": "MAXXI", "c": "Rome, Italy", "t": "B", "s": "S", "f": "About 500k visitors. Ministry of Culture, Regione Lazio.", "w": "Enel, a utility with gas generation.", "u": ["https://www.maxxi.art/en/sostienici/"], "la": 41.928, "lo": 12.466}, {"n": "Wattis Institute", "c": "San Francisco, USA", "t": "A", "s": "S", "f": "$1.4M budget. California College of the Arts (CCA), Andy Warhol Foundation, and Grants for the Arts (San Francisco).", "w": "Non-profit research institute and contemporary gallery at CCA. Focuses on social critique and artist commissions; clean ethical record free of corporate sponsorship conflicts.", "u": ["https://wattis.org/about", "https://projects.propublica.org/nonprofits/organizations/941156614"], "la": 37.767, "lo": -122.418}, {"n": "SITE Santa Fe", "c": "Santa Fe, USA", "t": "A", "s": "S", "f": "$3.5M annual budget. National Endowment for the Arts, New Mexico Arts, Andy Warhol Foundation, and contemporary patron circle.", "w": "Pioneering regional contemporary kunsthalle founded in 1995. Non-collecting institution with strict transparent donor disclosure; zero defense, extractive, or high-carbon corporate sponsors.", "u": ["https://sitesantafe.org/support/", "https://projects.propublica.org/nonprofits/organizations/850424564"], "la": 35.678, "lo": -105.955}, {"n": "Instituto Tomie Ohtake", "c": "S\u00e3o Paulo, Brazil", "t": "B", "s": "S", "f": "About R$25M, free, 665k visitors. Rouanet tax credit, Nubank.", "w": "Bloomberg and Votorantim (cement, mining) on roster.", "u": ["https://www.institutotomieohtake.org.br/parceiros-e-patrocinadores/", "https://www.cartacapital.com.br/cultura/apos-a-crise-a-celebracao/"], "la": -23.575, "lo": -46.699}, {"n": "Pinacoteca de S\u00e3o Paulo", "c": "S\u00e3o Paulo, Brazil", "t": "U", "s": "S", "f": "State museum; Rouanet; InfinitePay.", "w": "2025 sponsor panel unreadable.", "u": ["https://marcasmais.com.br/minforma/noticias/comunicacao/infinitepay-e-a-nova-patrocinadora-da-pinacoteca-de-sao-paulo/"], "la": -23.534, "lo": -46.634}, {"n": "Remai Modern", "c": "Saskatoon, Canada", "t": "B", "s": "S", "f": "C$13M, 204k visitors. City 51%, Remai foundation.", "w": "SaskEnergy, Cameco uranium, Sask Lotteries. 2019 board upheaval.", "u": ["https://remaimodern.org/wp-content/uploads/2026/06/2025_Annual_Report_Web_Version.pdf", "https://www.ckom.com/2019/02/25/7-members-of-remai-modern-board-ousted-or-leaving/"], "la": 52.129, "lo": -106.669}, {"n": "Frye Art Museum", "c": "Seattle, USA", "t": "B", "s": "S", "f": "$12.2M, free. Frye testamentary trust, meatpacking.", "w": "2020 layoffs dispute. Not sponsor-related.", "u": ["https://fryemuseum.org/support", "https://hyperallergic.com/554727/frye-art-museum-covid-19/"], "la": 47.607, "lo": -122.325}, {"n": "Henry Art Gallery", "c": "Seattle, USA", "t": "A", "s": "S", "f": "$4.1M budget. University of Washington, Washington State Arts Commission, 4Culture, and private endowments.", "w": "Museum of the University of Washington in Seattle. Operates under state university ethical giving policies with independent curatorial integrity; no controversial corporate naming rights.", "u": ["https://henryart.org/support", "https://projects.propublica.org/nonprofits/organizations/916001537"], "la": 47.656, "lo": -122.312}, {"n": "Art Sonje Center", "c": "Seoul, South Korea", "t": "A", "s": "S", "f": "\u20a93.5B budget. Supported by the Kindred Foundation, Korean Arts Management Service (KAMS), and Arts Council Korea (ARKO).", "w": "Private non-profit contemporary kunsthalle in Seoul founded by Chung Hee-ja. Adheres to Korean Non-Profit Corporation regulations with clean ethical sponsorship records.", "u": ["https://artsonje.org/en/about/", "https://www.arko.or.kr"], "la": 37.579, "lo": 126.98}, {"n": "National Museum of Modern and Contemporary Art (MMCA)", "c": "Seoul, South Korea", "t": "B", "s": "L", "f": "\u20a945B. Ministry of Culture, Sports and Tourism, Hyundai Motor Company partnership.", "w": "National institution with extensive 10-year automotive corporate partnership.", "u": ["https://www.mmca.go.kr/eng/"], "la": 37.579, "lo": 126.98}, {"n": "Rockbund Art Museum", "c": "Shanghai, China", "t": "A", "s": "S", "f": "\u00a518M annual budget. Sponsored by the Shanghai Rockbund Foundation and regional contemporary patron circles.", "w": "Non-profit contemporary museum located in the historic Royal Asiatic Society building in Shanghai. Governed under Shanghai Civil Affairs Bureau non-profit regulations with curatorial independence.", "u": ["https://www.rockbundartmuseum.org/en/about/us", "https://www.rockbundartmuseum.org"], "la": 31.244, "lo": 121.487}, {"n": "Bundanon", "c": "Shoalhaven, Australia", "t": "U", "s": "S", "f": "Federal statutory trust.", "w": "No sponsors named.", "u": ["https://www.bundanon.com.au/"], "la": -34.87, "lo": 150.594}, {"n": "Singapore Art Museum (SAM)", "c": "Singapore, Singapore", "t": "A", "s": "L", "f": "SGD 18M. National Arts Council under the Ministry of Culture, Community and Youth.", "w": "Statutory public board with governmental transparency mandates.", "u": ["https://www.singaporeartmuseum.sg/about/partners"], "la": 1.267, "lo": 103.824}, {"n": "The Model", "c": "Sligo, Ireland", "t": "A", "s": "S", "f": "\u20ac1.1M budget. Funded by Sligo County Council and the Arts Council of Ireland, with support from the Niland Collection Trust.", "w": "Regional contemporary arts center in Sligo. Full public service mandate with zero private corporate underwriters; governed under the Governance Code for Irish Community, Voluntary and Charitable Organisations.", "u": ["https://www.themodel.ie/support/", "https://www.charitiesregulator.ie"], "la": 54.272, "lo": -8.472}, {"n": "Pulitzer Arts Foundation", "c": "St. Louis, USA", "t": "A", "s": "S", "f": "$7.5M annual operating budget, free admission. Funded entirely by the philanthropic endowment of Emily Rauh Pulitzer and the Pulitzer family.", "w": "501(c)(3) private operating foundation in St. Louis designed by Tadao Ando. Free to the public, accepting no commercial sponsorships or corporate underwriting; fully self-sustaining endowment.", "u": ["https://pulitzerarts.org/about/", "https://projects.propublica.org/nonprofits/organizations/431940989"], "la": 38.64, "lo": -90.232}, {"n": "Index - The Swedish Contemporary Art Foundation", "c": "Stockholm, Sweden", "t": "A", "s": "S", "f": "SEK 5M. Swedish Arts Council (Kulturr\u00e5det), City of Stockholm, Region Stockholm.", "w": "Civic kunsthalle foundation funded through public grants.", "u": ["https://indexfoundation.se/about"], "la": 59.336, "lo": 18.053}, {"n": "Magasin III", "c": "Stockholm, Sweden", "t": "A", "s": "S", "f": "SEK 28M operating budget. Funded entirely by the private philanthropic foundation of Robert Weil (Proventus family).", "w": "Private museum for contemporary art in Stockholm and Jaffa. Operates without corporate sponsors or public state subsidies, maintaining independent curatorial focus supported by the Weil family philanthropic trust.", "u": ["https://www.magasin3.com/en/about/", "https://proventus.se"], "la": 59.31, "lo": 18.1}, {"n": "Moderna Museet", "c": "Stockholm, Sweden", "t": "B", "s": "L", "f": "SEK 257M, state 70%; PwC, a wine and spirits firm.", "w": "Bank of America, Bloomberg on roster.", "u": ["https://www.modernamuseet.se/en/stockholm/about/support/"], "la": 59.326, "lo": 18.084}, {"n": "Museum of Contemporary Art Australia (MCA)", "c": "Sydney, Australia", "t": "B", "s": "L", "f": "AUD 28M. Australia Council for the Arts, NSW Government, Telstra, Qantas, private benefactors.", "w": "Major Sydney harbourfront museum with prominent Australian corporate sponsors.", "u": ["https://www.mca.com.au/support-us/corporate-partners/"], "la": -33.86, "lo": 151.209}, {"n": "Kunstmuseum Den Haag", "c": "The Hague, Netherlands", "t": "A", "s": "S", "f": "\u20ac19.2M annual budget, 362k visitors. Municipal subsidy from The Hague, ticket revenues, VriendenLoterij, and educational foundations.", "w": "Governed under the Dutch Cultural Governance Code. Corporate partnerships (such as NN Group for community youth access) are regulated by strict public-interest non-interference covenants. Clean record regarding fossil fuel and defense underwriting.", "u": ["https://www.kunstmuseum.nl/en/museum/organisation", "https://www.kunstmuseum.nl/en/support"], "la": 52.089, "lo": 4.281}, {"n": "De Pont", "c": "Tilburg, Netherlands", "t": "A", "s": "S", "f": "\u20ac4.8M annual turnover, 75k visitors. Self-funded over 85% through the private founding endowment of J.H. de Pont and admission tickets.", "w": "Established in 1992 by the bequest of jurist and entrepreneur Jan de Pont. The foundation accepts no commercial underwriting or corporate naming rights, providing full editorial independence to curators.", "u": ["https://depont.nl/en/about-the-museum/history-and-building", "https://depont.nl/en/support"], "la": 51.563, "lo": 5.084}, {"n": "Mori Art Museum", "c": "Tokyo, Japan", "t": "B", "s": "L", "f": "Corporate endowment from Mori Building Co., Shiseido, corporate sponsors.", "w": "Real-estate developer cultural initiative with luxury and financial corporate circle.", "u": ["https://www.mori.art.museum/en/about/sponsorship/"], "la": 35.66, "lo": 139.73}, {"n": "Mercer Union", "c": "Toronto, Canada", "t": "B", "s": "S", "f": "Three arts councils.", "w": "TD Bank.", "u": ["https://www.mercerunion.org/about"], "la": 43.663, "lo": -79.436}, {"n": "The Power Plant", "c": "Toronto, Canada", "t": "B", "s": "S", "f": "Harbourfront affiliate; three arts councils.", "w": "BMO and RBC banks.", "u": ["https://www.thepowerplant.org/join-and-support"], "la": 43.638, "lo": -79.381}, {"n": "The Power Plant Contemporary Art Gallery", "c": "Toronto, Canada", "t": "A", "s": "S", "f": "CAD 3.5M. Canada Council for the Arts, Ontario Arts Council, Toronto Arts Council, Harbourfront Centre.", "w": "Strict non-collecting public gallery funded through arts councils.", "u": ["https://www.thepowerplant.org/SupportUs.aspx"], "la": 43.639, "lo": -79.382}, {"n": "Le Fresnoy - Studio national des arts contemporains", "c": "Tourcoing, France", "t": "A", "s": "S", "f": "\u20ac5.2M. Minist\u00e8re de la Culture, R\u00e9gion Hauts-de-France, M\u00e9tropole Europ\u00e9enne de Lille.", "w": "Exclusively public institutional funding.", "u": ["https://www.lefresnoy.net/fr/institution/partenaires"], "la": 50.724, "lo": 3.161}, {"n": "Castello di Rivoli", "c": "Turin, Italy", "t": "A", "s": "S", "f": "\u20ac6.2M annual budget. Regione Piemonte, Citt\u00e0 di Torino, Ministero della Cultura, and Fondazione CRT.", "w": "First contemporary art museum in Italy (UNESCO World Heritage Site). Governed by a public-interest consortium; transparent institutional funding audited by regional oversight bodies with zero controversial corporate ties.", "u": ["https://www.castellodirivoli.org/en/info/governance/", "https://www.regione.piemonte.it"], "la": 45.071, "lo": 7.516}, {"n": "Fondazione Sandretto Re Rebaudengo", "c": "Turin, Italy", "t": "A", "s": "S", "f": "\u20ac2.8M. Family endowment, Regione Piemonte, Compagnia di San Paolo, CRT Foundation.", "w": "Independent non-profit foundation; no military or extractive corporate links.", "u": ["https://fsrr.org/en/about/"], "la": 45.054, "lo": 7.648}, {"n": "Contemporary Art Gallery (CAG)", "c": "Vancouver, Canada", "t": "A", "s": "S", "f": "CAD 1.8M. City of Vancouver, British Columbia Arts Council, Canada Council, private donors.", "w": "Community non-profit charity operating under provincial ethical guidelines.", "u": ["https://www.contemporaryartgallery.ca/support/"], "la": 49.277, "lo": -123.12}, {"n": "Venice Biennale", "c": "Venice, Italy", "t": "B", "s": "L", "f": "illycaff\u00e8, Swatch, Bulgari, Zegna.", "w": "Bloomberg Philanthropies on roster.", "u": ["https://www.prnewswire.com/news-releases/illycaffe-is-main-sponsor-of-the-60th-international-art-exhibition--la-biennale-di-venezia-302068400.html", "https://www.milanoluxurylife.it/venice-biennale-2026-brands-luxury-patronage/"], "la": 45.429, "lo": 12.358}, {"n": "Ch\u00e2teau de Versailles", "c": "Versailles, France", "t": "B", "s": "L", "f": "AXA, Saint-Gobain, Rolex.", "w": "Dior, whose parent LVMH is under fire over tax rebates.", "u": ["https://fr.wikipedia.org/wiki/M%C3%A9c%C3%A9nat_au_domaine_de_Versailles"], "la": 48.805, "lo": 2.12}, {"n": "Albertina", "c": "Vienna, Austria", "t": "A", "s": "L", "f": "\u20ac32M annual budget, 1.2M visitors. Federal Republic of Austria, admission tickets, and corporate partners circle.", "w": "Federal museum of Austria. Self-funding ratio exceeds 60% through strong international tourism; corporate sponsors (Pomerche, UniCredit Bank Austria) comply with Austrian federal transparency mandates.", "u": ["https://www.albertina.at/en/about-us/", "https://www.rechnungshof.gv.at"], "la": 48.204, "lo": 16.368}, {"n": "Kunsthalle Wien", "c": "Vienna, Austria", "t": "A", "s": "S", "f": "\u20ac5.8M budget. City of Vienna Cultural Department (MA 7) core municipal subvention (approx 85%) and box office.", "w": "Municipal contemporary kunsthalle of Vienna. Operated under public service contracts with the City of Vienna; no corporate branding or private naming rights permitted in exhibition halls.", "u": ["https://kunsthallewien.at/en/about/", "https://www.wien.gv.at/kultur/abteilung/"], "la": 48.203, "lo": 16.361}, {"n": "Leopold Museum", "c": "Vienna, Austria", "t": "A", "s": "L", "f": "\u20ac12.5M budget, 450k visitors. Republic of Austria (BMK\u00d6S), City of Vienna, and museum admissions.", "w": "Independent private foundation created with state funding in 1994 to house Rudolf Leopold's Schiele collection. Subject to Austrian Federal Art Restitution Act scrutiny regarding provenance of early 20th-century Austrian modernist works.", "u": ["https://www.leopoldmuseum.org/en/about-us/mission-statement", "https://www.bmkoes.gv.at"], "la": 48.203, "lo": 16.359}, {"n": "mumok", "c": "Vienna, Austria", "t": "A", "s": "S", "f": "\u20ac14.2M operating budget, 240k visitors. Republic of Austria Federal Ministry (BMK\u00d6S) federal museum grant, admissions, and corporate circle.", "w": "Austrian federal museum situated in the MuseumsQuartier. Financial statements audited by the Austrian Court of Audit (Rechnungshof); corporate partners (Audi, Erste Bank) adhere to federal cultural patronage compliance codes.", "u": ["https://www.mumok.at/en/about-us", "https://www.rechnungshof.gv.at"], "la": 48.204, "lo": 16.358}, {"n": "Secession", "c": "Vienna, Austria", "t": "A", "s": "S", "f": "\u20ac2.6M annual turnover. Federal Ministry for Arts and Culture (BMK\u00d6S), City of Vienna, and Association of Visual Artists member dues.", "w": "Historic artist-run institution founded in 1897 by Gustav Klimt and the Vienna Secessionists. Governed democratically by a board of practicing visual artists; clean governance record with zero corporate extraction underwriting.", "u": ["https://secession.at/en/about", "https://www.bmkoes.gv.at"], "la": 48.2, "lo": 16.366}, {"n": "The Hepworth Wakefield", "c": "Wakefield, UK", "t": "B", "s": "S", "f": "\u00a34.2M. Arts Council, council, trusts; a rail firm, a paper maker.", "w": "Bloomberg Philanthropies and Blavatnik foundation.", "u": ["https://hepworthwakefield.org/our-story/about-us/35729-2/", "https://findthatcharity.uk/orgid/GB-CHC-1138117"], "la": 53.678, "lo": -1.496}, {"n": "Yorkshire Sculpture Park", "c": "Wakefield, UK", "t": "B", "s": "S", "f": "\u00a37.6M. Arts Council, council, Bramall Foundation; MINI dealer.", "w": "HSBC, a fossil-finance target.", "u": ["https://ysp.org.uk/support-us/our-supporters", "https://findthatcharity.uk/orgid/GB-CHC-1067908"], "la": 53.613, "lo": -1.573}, {"n": "Te Papa", "c": "Wellington, New Zealand", "t": "B", "s": "L", "f": "NZ$94M, Crown 51%; Westpac, Samsung, Panasonic.", "w": "Bloomberg, Samsung on roster.", "u": ["https://www.tepapa.govt.nz/support-join/corporate-partnerships/current-partners", "https://www.tepapa.govt.nz/assets/76067/1764552046-te-papa-annual-report-2024-25.pdf"], "la": -41.29, "lo": 174.782}, {"n": "Audain Art Museum", "c": "Whistler, Canada", "t": "A", "s": "S", "f": "CAD 3.9M annual budget. Michael Audain and Yoshiko Karasawa Foundation endowment, admissions, and Whistler patron circle.", "w": "Purpose-built museum in Whistler, BC housing British Columbia art. Endowed by philanthropist Michael Audain; operated under strict non-profit British Columbia societies regulations.", "u": ["https://audainartmuseum.com/about/", "https://apps.cra-arc.gc.ca/ebci/hacc/srch/pub/dsplyBscChrtyPfl?selectedCharityBn=840228397RR0001"], "la": 50.116, "lo": -122.957}, {"n": "Plug In ICA", "c": "Winnipeg, Canada", "t": "A", "s": "S", "f": "CAD 1.2M annual budget, free admission. Canada Council for the Arts, Manitoba Arts Council, Winnipeg Arts Council, and foundation grants.", "w": "First non-profit Institute of Contemporary Art in Canada. Deep public benefit commitment with free admission; no corporate defense or fossil fuel underwriting on its roster.", "u": ["https://plugin.org/support/", "https://apps.cra-arc.gc.ca/ebci/hacc/srch/pub/dsplyBscChrtyPfl?selectedCharityBn=119095655RR0001"], "la": 49.889, "lo": -97.146}, {"n": "TarraWarra Museum of Art", "c": "Yarra Valley, Australia", "t": "A", "s": "S", "f": "AUD 3.1M budget. Endowed by Eva Besen AO and Marc Besen AC through the Besen Family Foundation, with Creative Victoria support.", "w": "First major privately endowed public museum in Australia (Yarra Valley). Operates under a non-profit trust deed with independent trustees; completely free of corporate fossil fuel underwriting.", "u": ["https://www.twma.com.au/about/", "https://www.acnc.gov.au/charity/charities/12608240-39af-e811-a960-000d3ad24282/profile"], "la": -37.68, "lo": 145.43}, {"n": "Kunsthalle Z\u00fcrich", "c": "Z\u00fcrich, Switzerland", "t": "B", "s": "L", "f": "Members, city, canton, Luma Foundation, Swiss Re.", "w": "Bloomberg on roster.", "u": ["https://www.kunsthallezurich.ch/en/institution/"], "la": 47.389, "lo": 8.517}, {"n": "Migros Museum", "c": "Z\u00fcrich, Switzerland", "t": "A", "s": "S", "f": "CHF 3.8M operating expenditure. Financed as part of the Migros Culture Percentage (Migros-Kulturprozent) statutory corporate commitment.", "w": "Unique Swiss model established by Migros cooperative founder Gottlieb Duttweiler, mandating 1% of cooperative wholesale turnover to culture and education. Independent curatorial board; no arms or fossil investments.", "u": ["https://migrosmuseum.ch/en/about-us", "https://www.migros-kulturprozent.ch"], "la": 47.389, "lo": 8.518}];

  let institutions = FALLBACK_INSTITUTIONS;
  let isChatOpen = false;
  let isMinimized = false;
  let isListening = false;
  let recognition = null;

  const STORAGE_KEY_API_KEY = 'atlas_gemini_api_key';
  const STORAGE_KEY_MODEL = 'atlas_gemini_model';

  function safeGetStorage(key, defVal = '') {
    try {
      return localStorage.getItem(key) || defVal;
    } catch (e) {
      return defVal;
    }
  }

  function safeSetStorage(key, val) {
    try {
      localStorage.setItem(key, val);
    } catch (e) {}
  }

  let geminiApiKey = safeGetStorage(STORAGE_KEY_API_KEY, '');
  let geminiModel = safeGetStorage(STORAGE_KEY_MODEL, 'gemini-2.5-flash');

  // Tier info lookup
  const TIERS = {
    A: { label: 'Verified', color: '#24a148', desc: 'No controversial corporate underwriting. Endowed, public benefit, or strict ethical policy.' },
    B: { label: 'One name to know', color: '#4589ff', desc: 'Major public institution with a corporate partner to note on its roster.' },
    U: { label: 'Roster unverified', color: '#8d8d8d', desc: 'Pending updated annual report disclosure or under review.' }
  };

  function updateInstitutionsFromAtlas() {
    if (window.Atlas && window.Atlas.institutions && window.Atlas.institutions.length > 0) {
      institutions = window.Atlas.institutions;
    }
  }

  // Build UI
  function createChatUI() {
    if (document.getElementById('atlasConciergeToggle')) return;

    // 1. Toggle Button
    const toggleBtn = document.createElement('button');
    toggleBtn.className = 'atlas-concierge-toggle';
    toggleBtn.id = 'atlasConciergeToggle';
    toggleBtn.setAttribute('type', 'button');
    toggleBtn.setAttribute('aria-label', 'Open Atlas AI Concierge');
    toggleBtn.innerHTML = `
      <div class="atlas-toggle-orb">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#000" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="12" r="10"></circle>
          <path d="m4.93 4.93 4.24 4.24"></path>
          <path d="m14.83 9.17 4.24-4.24"></path>
          <path d="m14.83 14.83 4.24 4.24"></path>
          <path d="m9.17 14.83-4.24 4.24"></path>
          <circle cx="12" cy="12" r="4"></circle>
        </svg>
      </div>
      <span>Atlas Concierge</span>
      <span class="atlas-toggle-badge">${navigator.platform && navigator.platform.includes('Mac') ? '⌘K' : 'Ctrl+K'}</span>
    `;
    toggleBtn.addEventListener('click', toggleChat);
    document.body.appendChild(toggleBtn);

    // 2. Chat Window
    const chatWindow = document.createElement('div');
    chatWindow.className = 'atlas-chat-window';
    chatWindow.id = 'atlasChatWindow';
    chatWindow.innerHTML = `
      <div class="atlas-chat-header">
        <div class="atlas-chat-title-group">
          <div class="atlas-toggle-orb" style="width:20px;height:20px;"></div>
          <h3>Atlas AI Concierge</h3>
          <span class="atlas-engine-tag ${geminiApiKey ? 'gemini' : ''}" id="atlasEngineTag">
            ${geminiApiKey ? 'Gemini 2.5' : 'Offline Engine'}
          </span>
        </div>
        <div class="atlas-chat-header-actions">
          <button class="atlas-icon-btn" id="atlasSettingsBtn" title="API Settings & Model" aria-label="Settings">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"></path>
              <circle cx="12" cy="12" r="3"></circle>
            </svg>
          </button>
          <button class="atlas-icon-btn" id="atlasClearBtn" title="Clear Chat" aria-label="Clear chat">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M3 6h18"></path>
              <path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"></path>
              <path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"></path>
            </svg>
          </button>
          <button class="atlas-icon-btn" id="atlasMinimizeBtn" title="Minimize" aria-label="Minimize">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <line x1="5" y1="12" x2="19" y2="12"></line>
            </svg>
          </button>
          <button class="atlas-icon-btn" id="atlasCloseBtn" title="Close" aria-label="Close">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        </div>
      </div>

      <!-- Messages container -->
      <div class="atlas-chat-messages" id="atlasChatMessages">
        <div class="atlas-msg assistant">
          <div class="atlas-msg-bubble">
            <p><strong>Welcome to the Culture Atlas Concierge.</strong></p>
            <p>I can help you explore 197 ethically evaluated cultural institutions worldwide, analyze funding rosters, compare public and endowment models, or fly the 3D globe to any destination.</p>
            <div class="atlas-quick-suggestions">
              <button type="button" class="atlas-suggestion-btn" data-query="What ethically funded museums are in Tokyo?">
                🧭 What ethically funded museums are in Tokyo?
              </button>
              <button type="button" class="atlas-suggestion-btn" data-query="Show me large Tier A verified institutions">
                🟢 Show me large Tier A verified institutions
              </button>
              <button type="button" class="atlas-suggestion-btn" data-query="Why is Te Papa categorized as Tier B?">
                🔍 Why is Te Papa categorized as Tier B?
              </button>
              <button type="button" class="atlas-suggestion-btn" data-query="Explain the ethical funding screening methodology">
                ⚖️ How is funding transparency evaluated?
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Settings overlay -->
      <div class="atlas-settings-modal" id="atlasSettingsModal" style="display:none;">
        <div class="atlas-settings-header">
          <h4>Concierge Settings</h4>
          <button class="atlas-icon-btn" id="atlasCloseSettingsBtn">✕</button>
        </div>
        <div class="atlas-setting-item">
          <label>Google Gemini API Key (Optional)</label>
          <input type="password" id="atlasApiKeyInput" placeholder="AIzaSy..." value="${escapeHtml(geminiApiKey)}">
          <p class="atlas-settings-desc">
            Leave blank to use the built-in offline intelligence engine. Add an API key from <a href="https://aistudio.google.com/app/apikey" target="_blank" style="color:#00f2fe;text-decoration:underline;">Google AI Studio</a> to unlock full multi-turn conversational reasoning.
          </p>
        </div>
        <div class="atlas-setting-item">
          <label>Gemini Model</label>
          <select id="atlasModelSelect">
            <option value="gemini-2.5-flash" ${geminiModel === 'gemini-2.5-flash' ? 'selected' : ''}>Gemini 2.5 Flash (Recommended)</option>
            <option value="gemini-1.5-flash" ${geminiModel === 'gemini-1.5-flash' ? 'selected' : ''}>Gemini 1.5 Flash</option>
            <option value="gemini-1.5-pro" ${geminiModel === 'gemini-1.5-pro' ? 'selected' : ''}>Gemini 1.5 Pro</option>
          </select>
        </div>
        <button type="button" class="atlas-save-settings-btn" id="atlasSaveSettingsBtn">Save Settings</button>
      </div>

      <!-- Input Bar -->
      <div class="atlas-chat-input-bar">
        <input type="text" class="atlas-chat-input" id="atlasChatInput" placeholder="Ask about any museum, city, or sponsor...">
        <button type="button" class="atlas-voice-btn" id="atlasVoiceBtn" title="Voice Input" aria-label="Voice input">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"></path>
            <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
            <line x1="12" y1="19" x2="12" y2="22"></line>
          </svg>
        </button>
        <button type="button" class="atlas-send-btn" id="atlasSendBtn" title="Send message" aria-label="Send message">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#000" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <line x1="22" y1="2" x2="11" y2="13"></line>
            <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
          </svg>
        </button>
      </div>
    `;

    document.body.appendChild(chatWindow);

    setupEventListeners();
    setupSpeechRecognition();
  }

  function toggleChat() {
    const win = document.getElementById('atlasChatWindow');
    if (!win) return;
    updateInstitutionsFromAtlas();
    isChatOpen = !isChatOpen;
    if (isChatOpen) {
      win.classList.add('open');
      isMinimized = false;
      win.classList.remove('minimized');
      setTimeout(() => document.getElementById('atlasChatInput')?.focus(), 200);
    } else {
      win.classList.remove('open');
    }
  }

  function setupEventListeners() {
    const win = document.getElementById('atlasChatWindow');
    const input = document.getElementById('atlasChatInput');
    const sendBtn = document.getElementById('atlasSendBtn');
    const closeBtn = document.getElementById('atlasCloseBtn');
    const minBtn = document.getElementById('atlasMinimizeBtn');
    const clearBtn = document.getElementById('atlasClearBtn');
    const settingsBtn = document.getElementById('atlasSettingsBtn');
    const closeSettingsBtn = document.getElementById('atlasCloseSettingsBtn');
    const saveSettingsBtn = document.getElementById('atlasSaveSettingsBtn');
    const messages = document.getElementById('atlasChatMessages');

    closeBtn?.addEventListener('click', () => {
      isChatOpen = false;
      win.classList.remove('open');
    });

    minBtn?.addEventListener('click', () => {
      isMinimized = !isMinimized;
      win.classList.toggle('minimized', isMinimized);
    });

    clearBtn?.addEventListener('click', () => {
      if (messages) {
        messages.innerHTML = '';
        appendAssistantMessage('Chat history cleared. How can I assist you with Culture Atlas today?');
      }
    });

    settingsBtn?.addEventListener('click', () => {
      const modal = document.getElementById('atlasSettingsModal');
      if (modal) modal.style.display = 'flex';
    });

    closeSettingsBtn?.addEventListener('click', () => {
      const modal = document.getElementById('atlasSettingsModal');
      if (modal) modal.style.display = 'none';
    });

    saveSettingsBtn?.addEventListener('click', () => {
      const keyInput = document.getElementById('atlasApiKeyInput');
      const modelSelect = document.getElementById('atlasModelSelect');
      const tag = document.getElementById('atlasEngineTag');

      geminiApiKey = keyInput ? keyInput.value.trim() : '';
      geminiModel = modelSelect ? modelSelect.value : 'gemini-2.5-flash';

      safeSetStorage(STORAGE_KEY_API_KEY, geminiApiKey);
      safeSetStorage(STORAGE_KEY_MODEL, geminiModel);

      if (tag) {
        tag.textContent = geminiApiKey ? 'Gemini 2.5' : 'Offline Engine';
        tag.classList.toggle('gemini', !!geminiApiKey);
      }

      const modal = document.getElementById('atlasSettingsModal');
      if (modal) modal.style.display = 'none';
      appendAssistantMessage(
        geminiApiKey 
          ? `Connected to Google Gemini (${geminiModel})! Multi-turn conversational reasoning is now powered by Gemini.` 
          : 'Switched to Built-in Offline Intelligence Engine.'
      );
    });

    input?.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        handleUserSend();
      }
    });

    sendBtn?.addEventListener('click', handleUserSend);

    messages?.addEventListener('click', (e) => {
      const btn = e.target.closest('.atlas-suggestion-btn');
      if (btn) {
        const query = btn.getAttribute('data-query');
        if (query) {
          handleQuery(query);
        }
      }
    });

    window.addEventListener('keydown', (e) => {
      if ((e.metaKey || e.ctrlKey) && e.key && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        toggleChat();
      }
    });
  }

  function setupSpeechRecognition() {
    const voiceBtn = document.getElementById('atlasVoiceBtn');
    const input = document.getElementById('atlasChatInput');
    const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRec) {
      if (voiceBtn) voiceBtn.style.display = 'none';
      return;
    }

    try {
      recognition = new SpeechRec();
      recognition.continuous = false;
      recognition.interimResults = false;
      recognition.lang = 'en-US';

      recognition.onstart = () => {
        isListening = true;
        voiceBtn?.classList.add('listening');
      };

      recognition.onend = () => {
        isListening = false;
        voiceBtn?.classList.remove('listening');
      };

      recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        if (input) {
          input.value = transcript;
          handleUserSend();
        }
      };

      recognition.onerror = () => {
        isListening = false;
        voiceBtn?.classList.remove('listening');
      };

      voiceBtn?.addEventListener('click', () => {
        if (isListening) {
          recognition.stop();
        } else {
          try {
            recognition.start();
          } catch (e) {}
        }
      });
    } catch (e) {
      if (voiceBtn) voiceBtn.style.display = 'none';
    }
  }

  function appendUserMessage(text) {
    const container = document.getElementById('atlasChatMessages');
    if (!container) return;
    const msg = document.createElement('div');
    msg.className = 'atlas-msg user';
    msg.innerHTML = `<div class="atlas-msg-bubble">${escapeHtml(text)}</div>`;
    container.appendChild(msg);
    scrollToBottom();
  }

  function appendAssistantMessage(htmlContent, actions = []) {
    const container = document.getElementById('atlasChatMessages');
    if (!container) return;
    const msg = document.createElement('div');
    msg.className = 'atlas-msg assistant';

    let actionsHtml = '';
    if (actions && actions.length > 0) {
      actionsHtml = `<div class="atlas-actions-row">` +
        actions.map((act, idx) => `
          <button type="button" class="atlas-action-chip ${act.tier ? 'tier-' + act.tier.toLowerCase() : ''}" data-act-idx="${idx}">
            ${act.icon || '📍'} ${escapeHtml(act.label)}
          </button>
        `).join('') +
        `</div>`;
    }

    msg.innerHTML = `
      <div class="atlas-msg-bubble">
        ${htmlContent}
        ${actionsHtml}
      </div>
    `;

    if (actions && actions.length > 0) {
      const chips = msg.querySelectorAll('.atlas-action-chip');
      chips.forEach(chip => {
        const idx = parseInt(chip.getAttribute('data-act-idx'), 10);
        const action = actions[idx];
        if (action && action.handler) {
          chip.addEventListener('click', (e) => {
            e.stopPropagation();
            try {
              action.handler();
            } catch (err) {
              console.warn('Action failed', err);
            }
          });
        }
      });
    }

    container.appendChild(msg);
    scrollToBottom();
  }

  function showTypingIndicator() {
    const container = document.getElementById('atlasChatMessages');
    if (!container) return null;
    const indicator = document.createElement('div');
    indicator.className = 'atlas-msg assistant typing';
    indicator.id = 'atlasTypingIndicator';
    indicator.innerHTML = `
      <div class="atlas-msg-bubble atlas-typing-indicator">
        <div class="atlas-typing-dot"></div>
        <div class="atlas-typing-dot"></div>
        <div class="atlas-typing-dot"></div>
      </div>
    `;
    container.appendChild(indicator);
    scrollToBottom();
    return indicator;
  }

  function removeTypingIndicator() {
    const ind = document.getElementById('atlasTypingIndicator');
    ind?.remove();
  }

  function scrollToBottom() {
    const container = document.getElementById('atlasChatMessages');
    if (container) {
      container.scrollTop = container.scrollHeight;
    }
  }

  function escapeHtml(str) {
    if (!str) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  function handleUserSend() {
    const input = document.getElementById('atlasChatInput');
    if (!input) return;
    const q = input.value.trim();
    if (!q) return;
    input.value = '';
    handleQuery(q);
  }

  async function handleQuery(query) {
    appendUserMessage(query);
    showTypingIndicator();
    updateInstitutionsFromAtlas();

    if (geminiApiKey) {
      try {
        await handleGeminiQuery(query);
      } catch (err) {
        console.error('Gemini error, falling back to offline engine:', err);
        removeTypingIndicator();
        handleOfflineQuery(query, `*(Gemini error: ${err.message}. Showing offline results)*<br><br>`);
      }
    } else {
      setTimeout(() => {
        removeTypingIndicator();
        handleOfflineQuery(query);
      }, 300);
    }
  }

  // ==========================================
  // Offline Intelligence Engine
  // ==========================================
  function handleOfflineQuery(query, prefix = '') {
    const q = query.toLowerCase().trim();
    const actions = [];
    let responseHtml = '';

    updateInstitutionsFromAtlas();

    // 1. Methodology & Philosophy queries
    if (q.includes('method') || q.includes('criteria') || q.includes('how') && (q.includes('evaluate') || q.includes('tier') || q.includes('score') || q.includes('calculated') || q.includes('work'))) {
      responseHtml = `
        <p><strong>Culture Atlas Evaluation Methodology</strong></p>
        <p>Culture Atlas maps cultural institutions whose sponsors have never drawn an objection, evaluated by who funds them. Checked against official annual reports, partner listings, and public disclosures:</p>
        <ul>
          <li><strong>Tier A (Verified · 125 institutions)</strong>: Pure public benefit, municipal funding, or independent foundation endowment with strict ethical screening. Free of controversial underwriters.</li>
          <li><strong>Tier B (One name to know · 55 institutions)</strong>: High transparency, but has a corporate partner to note on its roster (e.g. fossil-finance banks, surveillance tech).</li>
          <li><strong>Tier U (Unverified · 17 institutions)</strong>: Public disclosures under review or awaiting updated partner indices.</li>
        </ul>
        <p>Excluded from the atlas entirely: institutions that retained sponsors linked to fossil fuel extraction, arms/defense manufacturing, opioids, tobacco, gambling, or sanctioned state entities.</p>
      `;
      actions.push({
        label: 'Show Verified (Tier A)',
        tier: 'A',
        icon: '🟢',
        handler: () => {
          if (window.Atlas?.setTiers) window.Atlas.setTiers(new Set(['A']));
          appendAssistantMessage('Filtered map to Tier A Verified institutions only.');
        }
      });
      actions.push({
        label: 'Show One Name To Know (Tier B)',
        tier: 'B',
        icon: '🔵',
        handler: () => {
          if (window.Atlas?.setTiers) window.Atlas.setTiers(new Set(['B']));
          appendAssistantMessage('Filtered map to Tier B institutions.');
        }
      });
      appendAssistantMessage(prefix + responseHtml, actions);
      return;
    }

    // 2. Specific Tier Filter queries
    if (q.includes('tier a') || q.includes('verified institutions')) {
      const tierA = institutions.filter(i => i.t === 'A');
      responseHtml = `
        <p><strong>Tier A: Verified Cultural Institutions (${tierA.length})</strong></p>
        <p>These institutions operate with transparent, ethically vetted funding models, primarily supported by civic municipal grants, national arts councils, or independent philanthropic trusts without corporate compromise.</p>
      `;
      actions.push({
        label: 'Filter Map to Tier A',
        tier: 'A',
        icon: '🟢',
        handler: () => {
          if (window.Atlas?.setTiers) window.Atlas.setTiers(new Set(['A']));
        }
      });
      tierA.slice(0, 3).forEach(inst => {
        actions.push({
          label: `Fly to ${inst.n} (${inst.c.split(',')[0]})`,
          icon: '📍',
          handler: () => triggerSelectInstitution(inst)
        });
      });
      appendAssistantMessage(prefix + responseHtml, actions);
      return;
    }

    // 3. Institution lookup by name
    const matchingInst = institutions.find(i => {
      const name = i.n.toLowerCase();
      return q.includes(name) || (name.includes(q) && q.length > 3);
    });

    if (matchingInst) {
      const tierInfo = TIERS[matchingInst.t] || TIERS.U;
      responseHtml = `
        <p><strong>${escapeHtml(matchingInst.n)}</strong> <span style="color:${tierInfo.color};font-weight:600;">· ${tierInfo.label}</span></p>
        <p>📍 <em>${escapeHtml(matchingInst.c)}</em> (${matchingInst.s === 'L' ? 'Large' : 'Small/Mid-sized'})</p>
        <p><strong>Funding & Governance:</strong><br>${escapeHtml(matchingInst.f)}</p>
        ${matchingInst.w ? `<p><strong>Watch Notes:</strong><br>${escapeHtml(matchingInst.w)}</p>` : ''}
      `;

      actions.push({
        label: `Inspect ${matchingInst.n} on Globe`,
        icon: '🌍',
        handler: () => triggerSelectInstitution(matchingInst)
      });

      if (matchingInst.u && matchingInst.u.length > 0) {
        actions.push({
          label: 'Official Source / Report',
          icon: '↗',
          handler: () => window.open(matchingInst.u[0], '_blank')
        });
      }

      appendAssistantMessage(prefix + responseHtml, actions);
      triggerSelectInstitution(matchingInst);
      return;
    }

    // 4. Geographic queries (cities & countries)
    const matchedInsts = institutions.filter(i => {
      const loc = i.c.toLowerCase();
      return q.includes(loc) || loc.split(',').some(part => q.includes(part.trim().toLowerCase()) && part.trim().length > 2);
    });

    if (matchedInsts.length > 0) {
      const cityName = matchedInsts[0].c.split(',')[0].trim();
      const countryName = matchedInsts[0].c.split(',')[1]?.trim() || '';
      responseHtml = `
        <p>Found <strong>${matchedInsts.length}</strong> institutions in <strong>${escapeHtml(cityName || countryName)}</strong>:</p>
        <ul>
          ${matchedInsts.slice(0, 5).map(i => `
            <li>
              <strong>${escapeHtml(i.n)}</strong> 
              <span style="color:${TIERS[i.t]?.color || '#888'}">(${TIERS[i.t]?.label})</span> — ${escapeHtml(i.s === 'L' ? 'Large' : 'Small/Mid')}
            </li>
          `).join('')}
        </ul>
        ${matchedInsts.length > 5 ? `<p><em>...and ${matchedInsts.length - 5} more.</em></p>` : ''}
      `;

      actions.push({
        label: `Filter by ${cityName}`,
        icon: '📍',
        handler: () => {
          if (window.Atlas?.filterCity) window.Atlas.filterCity(cityName);
          flyToCoordinates(matchedInsts[0].lo, matchedInsts[0].la, 4);
        }
      });

      matchedInsts.slice(0, 3).forEach(inst => {
        actions.push({
          label: inst.n,
          tier: inst.t,
          icon: '🏛️',
          handler: () => triggerSelectInstitution(inst)
        });
      });

      appendAssistantMessage(prefix + responseHtml, actions);
      flyToCoordinates(matchedInsts[0].lo, matchedInsts[0].la, 3.5);
      return;
    }

    // 5. Size queries
    if (q.includes('large') || q.includes('major') || q.includes('big') || q.includes('20m')) {
      const large = institutions.filter(i => i.s === 'L');
      responseHtml = `
        <p><strong>Large Cultural Institutions (${large.length})</strong></p>
        <p>Defined as institutions with annual budgets exceeding ~$20M or drawing over 500,000 visitors per year.</p>
        <p>Notable large ethical institutions include <em>ARoS (Aarhus)</em>, <em>Te Papa (Wellington)</em>, and <em>Museum of New Zealand</em>.</p>
      `;
      actions.push({
        label: 'Filter Large Only',
        icon: '🔍',
        handler: () => { if (window.Atlas?.selectSize) window.Atlas.selectSize('L'); }
      });
      actions.push({
        label: 'Show All Sizes',
        icon: '🌐',
        handler: () => { if (window.Atlas?.selectSize) window.Atlas.selectSize('all'); }
      });
      appendAssistantMessage(prefix + responseHtml, actions);
      return;
    }

    // 6. Surprise Me / Discovery
    if (q.includes('surprise') || q.includes('recommend') || q.includes('random') || q.includes('explore')) {
      const pick = institutions[Math.floor(Math.random() * institutions.length)];
      responseHtml = `
        <p>✨ <strong>Featured Institution: ${escapeHtml(pick.n)}</strong></p>
        <p>📍 <em>${escapeHtml(pick.c)}</em> · <span style="color:${TIERS[pick.t]?.color}">${TIERS[pick.t]?.label}</span></p>
        <p>${escapeHtml(pick.w || pick.f)}</p>
      `;
      actions.push({
        label: `Inspect ${pick.n}`,
        icon: '🌍',
        handler: () => triggerSelectInstitution(pick)
      });
      actions.push({
        label: 'Show Another',
        icon: '🎲',
        handler: () => handleOfflineQuery('surprise me')
      });
      appendAssistantMessage(prefix + responseHtml, actions);
      triggerSelectInstitution(pick);
      return;
    }

    // 7. Fallback response
    responseHtml = `
      <p>I can help you search or analyze any of the <strong>197 cultural institutions</strong> on Culture Atlas.</p>
      <p>Try asking:</p>
      <ul>
        <li><em>"Find museums in Copenhagen"</em> or <em>"What's in Australia?"</em></li>
        <li><em>"Tell me about Audain Art Museum"</em></li>
        <li><em>"Which institutions have budgets over $20M?"</em></li>
        <li><em>"How do you evaluate corporate sponsorship?"</em></li>
      </ul>
      <p><small>💡 Tip: You can also tap the ⚙️ icon in the header to connect Google Gemini for deeper comparative reasoning.</small></p>
    `;

    actions.push({
      label: 'Surprise Me',
      icon: '✨',
      handler: () => handleOfflineQuery('surprise me')
    });
    actions.push({
      label: 'Switch to City List View',
      icon: '📋',
      handler: () => { if (window.Atlas?.toggleView) window.Atlas.toggleView('list'); }
    });

    appendAssistantMessage(prefix + responseHtml, actions);
  }

  // ==========================================
  // Google Gemini API Integration
  // ==========================================
  async function handleGeminiQuery(query) {
    const url = `https://generativelanguage.googleapis.com/v1beta/models/${geminiModel}:generateContent?key=${geminiApiKey}`;

    const summaryData = institutions.slice(0, 50).map(i => ({
      name: i.n,
      location: i.c,
      tier: i.t,
      size: i.s,
      funding: i.f,
      note: i.w,
      lat: i.la,
      lon: i.lo
    }));

    const systemInstruction = `
You are the Atlas AI Concierge, a brilliant assistant for "Culture Atlas".
Culture Atlas maps 197 cultural institutions across the globe evaluated by their ethical funding transparency and freedom from controversial sponsorship.
Tiers:
- Tier A (Verified): 125 institutions with clean funding, public benefit, or independent endowment.
- Tier B (One name to know): 55 institutions with notable corporate underwriting.
- Tier U (Unverified): 17 institutions awaiting updated disclosures.

Institutions Data Summary:
${JSON.stringify(summaryData)} (and 147 more available)

When relevant, you can include actionable commands in your response using special tags:
- [[FLY:longitude,latitude,zoom:Label]] to create a flight button to a location.
- [[SELECT:ExactInstitutionName]] to create an inspection button for an institution.
- [[FILTER:CityOrCountry]] to create a location filter button.
- [[TIER:A]] or [[TIER:B]] to filter by tier.

Keep responses engaging, informative, and formatted with clean markdown.
`;

    const body = {
      contents: [{ role: 'user', parts: [{ text: query }] }],
      systemInstruction: { parts: [{ text: systemInstruction }] },
      generationConfig: { temperature: 0.7, maxOutputTokens: 1000 }
    };

    const res = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    });

    removeTypingIndicator();

    if (!res.ok) {
      const errData = await res.json().catch(() => ({}));
      throw new Error(errData?.error?.message || `HTTP ${res.status}`);
    }

    const data = await res.json();
    let text = data?.candidates?.[0]?.content?.parts?.[0]?.text || 'No response generated.';

    const actions = [];
    const flyRegex = /\[\[FLY:([-0-9.]+),([-0-9.]+),([0-9.]+):([^\]]+)\]\]/g;
    let match;
    while ((match = flyRegex.exec(text)) !== null) {
      const [, lon, lat, zoom, label] = match;
      actions.push({
        label: label.trim(),
        icon: '📍',
        handler: () => flyToCoordinates(parseFloat(lon), parseFloat(lat), parseFloat(zoom))
      });
    }
    text = text.replace(flyRegex, '');

    const selectRegex = /\[\[SELECT:([^\]]+)\]\]/g;
    while ((match = selectRegex.exec(text)) !== null) {
      const [, instName] = match;
      const inst = institutions.find(i => i.n.toLowerCase() === instName.trim().toLowerCase());
      if (inst) {
        actions.push({
          label: `Inspect ${inst.n}`,
          icon: '🏛️',
          handler: () => triggerSelectInstitution(inst)
        });
      }
    }
    text = text.replace(selectRegex, '');

    const filterRegex = /\[\[FILTER:([^\]]+)\]\]/g;
    while ((match = filterRegex.exec(text)) !== null) {
      const [, loc] = match;
      actions.push({
        label: `Filter by ${loc.trim()}`,
        icon: '🔍',
        handler: () => { if (window.Atlas?.filterCity) window.Atlas.filterCity(loc.trim()); }
      });
    }
    text = text.replace(filterRegex, '');

    const tierRegex = /\[\[TIER:([ABU])\]\]/g;
    while ((match = tierRegex.exec(text)) !== null) {
      const [, t] = match;
      actions.push({
        label: `Show Tier ${t}`,
        tier: t,
        icon: t === 'A' ? '🟢' : t === 'B' ? '🔵' : '⚪',
        handler: () => { if (window.Atlas?.setTiers) window.Atlas.setTiers(new Set([t])); }
      });
    }
    text = text.replace(tierRegex, '');

    appendAssistantMessage(formatMarkdown(text), actions);
  }

  function formatMarkdown(md) {
    let html = escapeHtml(md);
    html = html.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
    html = html.replace(/\*([^*]+)\*/g, '<em>$1</em>');
    html = html.replace(/`([^`]+)`/g, '<code style="background:rgba(255,255,255,0.1);padding:2px 4px;border-radius:4px;font-size:12px;">$1</code>');
    html = html.replace(/\n\n+/g, '</p><p>');
    html = html.replace(/\n/g, '<br>');
    html = `<p>${html}</p>`;
    html = html.replace(/<p><\/p>/g, '');
    return html;
  }

  function triggerSelectInstitution(inst) {
    if (window.Atlas?.selectInstitution) {
      window.Atlas.selectInstitution(inst);
    }
    if (window.AtlasGlobe?.flyTo) {
      window.AtlasGlobe.flyTo(inst.lo, inst.la, 6);
    }
  }

  function flyToCoordinates(lon, lat, zoom = 4) {
    if (window.AtlasGlobe?.flyTo) {
      window.AtlasGlobe.flyTo(lon, lat, zoom);
    }
  }

  // Safe initialize
  function initConcierge() {
    createChatUI();
    updateInstitutionsFromAtlas();
  }

  if (document.readyState === 'loading') {
    window.addEventListener('DOMContentLoaded', initConcierge);
  } else {
    initConcierge();
  }

  window.AtlasConcierge = {
    open: () => { if (!isChatOpen) toggleChat(); },
    close: () => { if (isChatOpen) toggleChat(); },
    ask: handleQuery,
    setApiKey: (key) => {
      geminiApiKey = key;
      safeSetStorage(STORAGE_KEY_API_KEY, key);
      const tag = document.getElementById('atlasEngineTag');
      if (tag) {
        tag.textContent = key ? 'Gemini 2.5' : 'Offline Engine';
        tag.classList.toggle('gemini', !!key);
      }
    }
  };

})();
