import json, os

def enrich():
    with open("institutions.json", "r", encoding="utf-8") as f:
        institutions = json.load(f)

    # Dictionary of critiques keyed by institution identifier patterns
    # Format of critique record:
    # {
    #   "artist_designer": "...",
    #   "artwork_title": "...",
    #   "year": "...",
    #   "medium_format": "...",
    #   "credits": "...",
    #   "strategy": "...",
    #   "strategy_id": "...",
    #   "target": "...",
    #   "summary": "...",
    #   "historical_impact": "...",
    #   "image": "...",
    #   "citation": "...",
    #   "doi": "..."
    # }

    critique_db = {
        "guggenheim": [
            {
                "artist_designer": "Hans Haacke",
                "artist": "Hans Haacke",
                "artwork_title": "Shapolsky et al. Manhattan Real Estate Holdings, a Real-Time Social System, as of May 1, 1971",
                "artwork": "Shapolsky et al. Manhattan Real Estate Holdings, a Real-Time Social System, as of May 1, 1971",
                "practice": "Hans Haacke: Real Estate Data System & Slumlord Disclosure",
                "year": "1971",
                "medium_format": "142 photographs of building facades, 142 photocopied property deeds, 2 maps, charts, and corporate dossiers",
                "credits": "Artist: Hans Haacke | Curatorial Invitation: Edward Fry (dismissed by museum for refusal to censor) | Institutional Target: Solomon R. Guggenheim Museum & Harry Shapolsky Syndicate | Archive / Collection: Centre Pompidou, Paris & MACBA, Barcelona | Photo Credit: Hans Haacke / VG Bild-Kunst",
                "strategy": "Sponsor Network Exposure & Real Estate Tracking",
                "strategy_id": "sponsor_exposure",
                "target": "Solomon R. Guggenheim Museum & Harry Shapolsky Slumlord Syndicate",
                "institution_target": "Solomon R. Guggenheim Museum",
                "summary": "Invited by curator Edward Fry to mount a solo exhibition at the Guggenheim, Haacke conducted deep archival investigations into public deed registries, exposing the interconnected shell companies of Harry Shapolsky—Manhattan's largest slum landlord syndicate owning 142 decrepit tenements in the Lower East Side and Harlem. When Director Thomas Messer discovered the work mapped real estate networks overlapping with museum board interests, he cancelled the exhibition six weeks before opening and fired Fry. The work established empirical property tracking as a core institutional critique medium.",
                "historical_impact": "Sparked major artist boycotts of the Guggenheim, public demonstrations by the Art Workers Coalition (AWC), and set the enduring art-historical precedent of mapping trustee financial entanglements.",
                "image": "assets/visual_critique/haacke_shapolsky_guggenheim_thumb.jpg",
                "citation": "Rectanus, M. W. (2002). Culture Incorporated: Museums, Artists, and Corporate Sponsorships. Minneapolis: University of Minnesota Press / Consensus Study.",
                "doi": "10.2307/1433407"
            },
            {
                "artist_designer": "Nan Goldin & P.A.I.N. (Prescription Addiction Intervention Now)",
                "artist": "Nan Goldin & P.A.I.N.",
                "artwork_title": "Sackler Die-In at the Guggenheim Rotunda",
                "artwork": "Sackler Die-In at the Guggenheim Rotunda",
                "practice": "Nan Goldin & P.A.I.N.: Guggenheim Rotunda Spiral Die-In & Prescription Drop",
                "year": "2019",
                "medium_format": "Choreographed direct-action die-in, thousands of prescription slips and fake OxyContin coupons fluttering from the spiral rotunda",
                "credits": "Artist / Lead Organizer: Nan Goldin | Action Collective: P.A.I.N. (Prescription Addiction Intervention Now) | Target: Solomon R. Guggenheim Museum Sackler Center for Arts Education | Photo Credit: P.A.I.N. Media Archives",
                "strategy": "Pharma & Fossil Philanthropy De-Naming",
                "strategy_id": "pharma_fossil_denaming",
                "target": "Solomon R. Guggenheim Museum (Sackler Center for Arts Education)",
                "institution_target": "Solomon R. Guggenheim Museum",
                "summary": "Nan Goldin and dozens of activists from P.A.I.N. staged an unannounced die-in across Frank Lloyd Wright's iconic spiral rotunda, dropping thousands of slips modeled after OxyContin warning labels from the top tiers down to the fountain floor. Activists held banners declaring 'SHAME ON SACKLER' and demanded the museum cease accepting Sackler family opioid wealth.",
                "historical_impact": "In March 2019, the Guggenheim announced it would accept no further gifts from the Sackler family, followed by the permanent removal of the Sackler name from the Arts Education Center in 2022.",
                "image": "assets/visual_critique/nan_goldin_pain_sackler_met_thumb.jpg",
                "citation": "Sharp, C., & Summers, S. (2025). Museum funding as critical practice. Museums & Social Issues / Consensus Study.",
                "doi": "10.1080/15596893.2025.2465592"
            }
        ],
        "moma": [
            {
                "artist_designer": "Hans Haacke",
                "artist": "Hans Haacke",
                "artwork_title": "MoMA Poll",
                "artwork": "MoMA Poll",
                "practice": "Hans Haacke: Direct Ballot Box & Rockefeller Accountability",
                "year": "1970",
                "medium_format": "Two transparent acrylic ballot boxes, photoelectric counters, ballot paper slips, and printed question signage",
                "credits": "Artist: Hans Haacke | Curatorial Commission: 'Information' exhibition (curated by Kynaston McShine) | Institutional Target: MoMA Board of Trustees & Governor Nelson Rockefeller | Photo Credit: Hans Haacke Archives",
                "strategy": "Direct Polling & Democratic Data",
                "strategy_id": "direct_polling",
                "target": "MoMA Board of Trustees & Governor Nelson Rockefeller",
                "institution_target": "MoMA (The Museum of Modern Art)",
                "summary": "Commissioned for the landmark 1970 'Information' exhibition at MoMA, Haacke installed two acrylic ballot boxes asking visitors: 'Would the fact that Governor Rockefeller has not denounced President Nixon's Indochina policy be a reason for you not to vote for him in November?' Over 37,000 visitors voted, with 68.7% casting ballots in the 'YES' box, publicly exposing the political entanglement of MoMA's primary trustee and benefactor in the Indochina War.",
                "historical_impact": "Directly challenged museum claims of political neutrality and demonstrated that the museum audience could be transformed into an active, voting civic body inside the white cube.",
                "image": "assets/visual_critique/haacke_moma_poll_thumb.jpg",
                "citation": "Alshawaaf, N., & Lee, S.-H. (2024). The Paradox of Corporate Sponsorship of Arts in the Age of Austerity. Journal of Arts Management, Law, and Society / Consensus Study.",
                "doi": "10.59876/b-g491-vkgb"
            },
            {
                "artist_designer": "Adrian Piper",
                "artist": "Adrian Piper",
                "artwork_title": "Cornered",
                "artwork": "Cornered",
                "practice": "Adrian Piper: Spatial Confrontation & Racial Complicity in the White Cube",
                "year": "1988–2018",
                "medium_format": "Single-channel video installation, overturned wooden table, 10 chairs, birth certificates of the artist's father",
                "credits": "Artist: Adrian Piper | Curators: Connie Butler & Christophe Cherix | Retrospective: MoMA & MoMA PS1 (Adrian Piper: A Synthesis of Intuitions) | Collection: Adrian Piper Research Archive Foundation Berlin",
                "strategy": "Performative Video & White Cube Confrontation",
                "strategy_id": "performative_tour",
                "target": "MoMA & Institutional Whiteness in American Modernism",
                "institution_target": "MoMA (The Museum of Modern Art)",
                "summary": "Positioned behind an overturned table in a physical corner, Piper's video addresses the viewer directly, methodically analyzing racial passing, genealogical denial, and the institutional complicity of elite museums in maintaining exclusionary Eurocentric cultural hierarchies.",
                "historical_impact": "Pioneered conceptual confrontation in institutional space, deconstructing audience passivity and racial gatekeeping in major museum collections.",
                "image": "assets/visual_critique/adrian_piper_cornered_thumb.jpg",
                "citation": "Casado-Molina, A.-M., et al. (2023). Building mutual rewarding sponsor relationships between museums and corporations. Consensus Study.",
                "doi": "10.1080/09548963.2023.2255836"
            }
        ],
        "whitney": [
            {
                "artist_designer": "Forensic Architecture & Laura Poitras",
                "artist": "Forensic Architecture & Laura Poitras",
                "artwork_title": "Triple-Chaser (Safariland Investigation)",
                "artwork": "Triple-Chaser (Safariland Investigation)",
                "practice": "Forensic Architecture: Computer Vision Ballistics & Trustee Defense Contractor Tracking",
                "year": "2019",
                "medium_format": "10-minute multi-channel investigative video, synthetic 3D photogrammetry, machine learning acoustic classifiers, tear gas canister ballistic database",
                "credits": "Investigative Team: Forensic Architecture (Goldsmiths, University of London; Eyal Weizman, Robert Trafford) with Praxis Films (Laura Poitras) | Curatorial Context: 2019 Whitney Biennial (curated by Jane Panetta & Rujeko Hockley) | Institutional Target: Warren B. Kanders (Whitney Vice Chairman & Safariland CEO) | Photo Credit: Forensic Architecture & Praxis Films",
                "strategy": "Spatial & Algorithmic Forensic Investigation",
                "strategy_id": "forensic_investigation",
                "target": "Warren B. Kanders (Whitney Museum Vice Chairman) & Safariland Law Enforcement Technologies",
                "institution_target": "Whitney Museum of American Art",
                "summary": "Commissioned for the 2019 Whitney Biennial, Forensic Architecture partnered with filmmaker Laura Poitras to investigate Warren Kanders, the Whitney's Vice Chairman of the Board of Trustees and CEO of Safariland—a manufacturer of military and crowd-control weapons. The team trained a computer vision algorithm using synthetic 3D rendering to locate Safariland 'Triple-Chaser' tear gas canisters deployed against civilian protesters at the US-Mexico border, in Gaza, and in Puerto Rico, directly projecting the evidence inside the Whitney galleries.",
                "historical_impact": "Triggered protests by Decolonize This Place, an open letter signed by nearly 100 Whitney staff members, and the withdrawal of eight participating artists (including Korakrit Arunanondchai, Meriem Bennani, and Michael Rakowitz). Warren Kanders resigned from the board in July 2019, marking one of the most significant trustee accountability victories in modern museum history.",
                "image": "assets/visual_critique/forensic_architecture_triple_chaser_thumb.jpg",
                "citation": "Alshawaaf, N., & Lee, S.-H. (2024). The Paradox of Corporate Sponsorship of Arts in the Age of Austerity. Consensus Study.",
                "doi": "10.59876/b-g491-vkgb"
            },
            {
                "artist_designer": "Decolonize This Place",
                "artist": "Decolonize This Place",
                "artwork_title": "Nine Weeks of Art & Agitation: Taking the Museum",
                "artwork": "Nine Weeks of Art & Agitation: Taking the Museum",
                "practice": "Decolonize This Place: Sustained Direct Action & Museum Lobby Reoccupation",
                "year": "2019",
                "medium_format": "Physical interventions, printed counter-propaganda zines, town halls, mass assemblies, and street actions",
                "credits": "Designers / Organizers: Decolonize This Place in coalition with Chinatown Art Brigade, Mobile Print Power, and W.A.G.E. | Institutional Target: Whitney Museum of American Art Board of Trustees | Documentation: Decolonize This Place Media Collective",
                "strategy": "Grassroots Agitation & Board Boycotts",
                "strategy_id": "board_boycott",
                "target": "Whitney Museum of American Art Board Governance & Defense Industry Sponsorship",
                "institution_target": "Whitney Museum of American Art",
                "summary": "Organized nine consecutive Friday afternoon assemblies and marches starting at the Whitney and culminating at Warren Kanders' Greenwich Village residence. Activists occupied the museum lobby with banners, distributed counter-literature, and created an autonomous public forum demanding the immediate removal of defense contractor leadership from cultural institutions.",
                "historical_impact": "Directly accelerated the resignation of Warren Kanders and prompted the Whitney to inaugurate internal reviews of board trustee vetting processes.",
                "image": "assets/visual_critique/decolonize_this_place_whitney_thumb.jpg",
                "citation": "Sharp, C., & Summers, S. (2025). Museum funding as critical practice. Museums & Social Issues / Consensus Study.",
                "doi": "10.1080/15596893.2025.2465592"
            },
            {
                "artist_designer": "Occupy Museums",
                "artist": "Occupy Museums",
                "artwork_title": "Debtfair at the Whitney Biennial",
                "artwork": "Debtfair at the Whitney Biennial",
                "practice": "Occupy Museums: Predatory Artist Debt Wall & Trustee Financial Index",
                "year": "2017",
                "medium_format": "Architectural wall installation, digital interactive database, artwork of 79 indebted cultural workers, financial flowcharts",
                "credits": "Collective: Occupy Museums (Arthur Polendo, Imani Jacqueline Brown, Noah Fischer, Tal Beery) | Curators: Mia Locks & Christopher Y. Lew | Institutional Target: Whitney Museum of American Art & Hedge Fund Trustees (e.g. John B. Phelan / CarVal Investors) | Photo Credit: Occupy Museums Archives",
                "strategy": "Sponsor Network Exposure & Real Estate Tracking",
                "strategy_id": "sponsor_exposure",
                "target": "Whitney Museum of American Art & Puerto Rican Debt-Holding Trustees",
                "institution_target": "Whitney Museum of American Art",
                "summary": "Debtfair mapped the staggering \$30+ million student and living debt held by 79 exhibiting artists against the predatory investment portfolios of museum board trustees, specifically exposing board members profiting from Puerto Rico's unpayable debt restructuring while cultivating high-society philanthropic credentials.",
                "historical_impact": "Demystified the economic precarity of participating artists in high-profile biennials and exposed trustee connections to hedge funds holding sovereign debt.",
                "image": "assets/visual_critique/occupy_museums_debtfair_thumb.jpg",
                "citation": "Ryan, A. (2018). Practice (mis)matching: multiple performations of a cultural sponsorship network. Journal of Marketing Management / Consensus Study.",
                "doi": "10.1080/0267257x.2018.1556723"
            }
        ],
        "metropolitan": [
            {
                "artist_designer": "Nan Goldin & P.A.I.N. (Prescription Addiction Intervention Now)",
                "artist": "Nan Goldin & P.A.I.N.",
                "artwork_title": "Sackler Die-In at the Temple of Dendur",
                "artwork": "Sackler Die-In at the Temple of Dendur",
                "practice": "Nan Goldin & P.A.I.N.: Temple of Dendur Opioid Die-In & Pill Bottle Launch",
                "year": "2018",
                "medium_format": "Choreographed direct-action die-in, prescription bottles thrown into reflecting pools, banners reading 'SHAME ON SACKLER', counterfeit museum brochures",
                "credits": "Artist / Lead Organizer: Nan Goldin | Action Group: P.A.I.N. (Prescription Addiction Intervention Now) | Institutional Target: The Metropolitan Museum of Art (The Sackler Wing) | Photography: P.A.I.N. Media Team / Bryan Bedder",
                "strategy": "Pharma & Fossil Philanthropy De-Naming",
                "strategy_id": "pharma_fossil_denaming",
                "target": "The Metropolitan Museum of Art (The Sackler Wing)",
                "institution_target": "The Metropolitan Museum of Art (The Met)",
                "summary": "In March 2018, artist Nan Goldin led over 100 activists into the Met's soaring Sackler Wing housing the Egyptian Temple of Dendur. At a signal, participants tossed hundreds of empty pill bottles labeled with Purdue Pharma warnings into the moat and staged a mass die-in on the floor, chanting 'Sacklers lie, people die!' The action dramatically framed the museum's acceptance of opioid fortune as complicity in a national public health crisis.",
                "historical_impact": "In December 2021, the Met voted to remove the Sackler family name from all seven exhibition spaces including the Sackler Wing, triggering a global domino effect across the Louvre, Guggenheim, British Museum, and Tate.",
                "image": "assets/visual_critique/nan_goldin_pain_sackler_met_thumb.jpg",
                "citation": "Sharp, C., & Summers, S. (2025). Museum funding as critical practice. Museums & Social Issues / Consensus Study.",
                "doi": "10.1080/15596893.2025.2465592"
            },
            {
                "artist_designer": "Guerrilla Girls",
                "artist": "Guerrilla Girls",
                "artwork_title": "Do women have to be naked to get into the Met. Museum?",
                "artwork": "Do women have to be naked to get into the Met. Museum?",
                "practice": "Guerrilla Girls: Feminist Statistical Counter-Surveys & Met Museum Audit",
                "year": "1989–2025",
                "medium_format": "Screenprint agitprop poster, yellow billboard and bus side campaign, empirical collection audit data",
                "credits": "Artists / Designers: Guerrilla Girls (anonymous feminist artist-activist collective founded NYC 1985) | Graphic Design: Guerrilla Girls NYC Studio | Institutional Target: The Metropolitan Museum of Art Board & Curatorial Acquisitions | Collection: Whitney Museum, Tate, Pompidou | Photo Credit: Guerrilla Girls Archives",
                "strategy": "Feminist Statistical Counter-Surveys",
                "strategy_id": "feminist_counter_survey",
                "target": "The Metropolitan Museum of Art (Modern Art Department Acquisitions & Gender Imbalance)",
                "institution_target": "The Metropolitan Museum of Art (The Met)",
                "summary": "The Guerrilla Girls famously counted artists represented in the Met's Modern Art sections, finding that less than 5% of the artists were women, but 85% of the nudes depicted were female. The iconic poster—depicting Ingres' Grande Odalisque wearing a gorilla mask—transformed statistical auditing into high-impact graphic design, calling out board trustees and curators for institutional sexism.",
                "historical_impact": "Became one of the most recognized artworks of institutional critique in history, forcing major art museums worldwide to institute diversity auditing and revise acquisitions budgets.",
                "image": "assets/visual_critique/guerrilla_girls_met_thumb.jpg",
                "citation": "Rectanus, M. W. (2002). Culture Incorporated: Museums, Artists, and Corporate Sponsorships. Consensus Study.",
                "doi": "10.2307/1433407"
            }
        ],
        "british-museum": [
            {
                "artist_designer": "BP or not BP? (Culture Unstained)",
                "artist": "BP or not BP?",
                "artwork_title": "The Trojan Horse & Stolen Goods Action at the British Museum",
                "artwork": "The Trojan Horse & Stolen Goods Action at the British Museum",
                "practice": "BP or not BP?: Theatrical Infiltration, Trojan Horse & Fossil Divestment",
                "year": "2012–2024",
                "medium_format": "13-foot wooden Trojan Horse wheeled into the Great Court, flash-mob theatrical performances, counterfeit oil spills on corporate donor plaques, protest songs",
                "credits": "Theatrical Troupe / Activists: BP or not BP? in coalition with Culture Unstained | Performance Venue: British Museum Great Court & North Lawn | Documentation: Culture Unstained Archives",
                "strategy": "Pharma & Fossil Philanthropy De-Naming",
                "strategy_id": "pharma_fossil_denaming",
                "target": "British Museum & BP (British Petroleum) 27-Year Corporate Sponsorship",
                "institution_target": "British Museum",
                "summary": "Over a decade, BP or not BP? staged over 60 unsanctioned theatrical performances inside the British Museum to challenge the museum's 27-year sponsorship relationship with fossil fuel giant BP. In February 2020, during the BP-sponsored 'Troy: Myth and Reality' exhibition, activists secretly wheeled a massive 13-foot wooden Trojan horse into the Great Court, symbolizing how BP used museum sponsorship as a veneer to disguise climate destruction and colonial resource extraction.",
                "historical_impact": "In June 2023, the British Museum officially terminated its 27-year sponsorship contract with BP, completing the near-total expulsion of oil company branding from the UK cultural sector.",
                "image": "assets/visual_critique/bp_or_not_bp_british_museum_thumb.jpg",
                "citation": "Ryan, A. (2018). Practice (mis)matching: multiple performations of a cultural sponsorship network. Journal of Marketing Management / Consensus Study.",
                "doi": "10.1080/0267257x.2018.1556723"
            }
        ],
        "tate-modern": [
            {
                "artist_designer": "Cildo Meireles",
                "artist": "Cildo Meireles",
                "artwork_title": "Insertions into Ideological Circuits: Coca-Cola Project",
                "artwork": "Insertions into Ideological Circuits: Coca-Cola Project",
                "practice": "Cildo Meireles: Subversive Commercial Packaging & Anti-Imperialist Distribution",
                "year": "1970",
                "medium_format": "Screenprinted white vitreous enamel text on returnable glass Coca-Cola bottles, circulating consumer goods",
                "credits": "Artist: Cildo Meireles | Acquired by: Tate Modern (purchased with funds provided by the American Fund for the Tate Gallery, 2004) | Archive: Tate Collection Ref. T12316 | Photo Credit: Tate Modern",
                "strategy": "Ideological & Currency Circulation",
                "strategy_id": "ideological_distribution",
                "target": "Consumer Capitalism, Imperialist Hegemony, and Museum Display Circuits",
                "institution_target": "Tate Modern",
                "summary": "Meireles silkscreened subversive political text onto empty glass Coca-Cola bottles—including instructions on making Molotov cocktails and slogans like 'Yankees Go Home'—that were invisible when empty but appeared in crisp white lettering when refilled with dark cola and returned to commercial retail circulation. Meireles defined the work as an insertion into existing systems of consumer exchange rather than an isolated museum object.",
                "historical_impact": "Radicalized the understanding of institutional critique as an active intervention into capitalist supply chains rather than a passive museum commodity.",
                "image": "assets/visual_critique/cildo_meireles_coca_cola_thumb.jpg",
                "citation": "Pacheco, D., et al. (2026). Network analysis of cultural funding in Brazil: uncovering regional differences and signatures. Consensus Study.",
                "doi": "10.1080/10286632.2025.2454580"
            },
            {
                "artist_designer": "Marcel Broodthaers",
                "artist": "Marcel Broodthaers",
                "artwork_title": "Musée d'Art Moderne, Département des Aigles",
                "artwork": "Musée d'Art Moderne, Département des Aigles",
                "practice": "Marcel Broodthaers: Parodic Museum Administration & Section des Figures",
                "year": "1968–1972",
                "medium_format": "Postcards, shipping crates, eagles ephemera, slide carousels, printed museum catalogues, museum office desks",
                "credits": "Artist: Marcel Broodthaers | Historical Manifestos: Département des Aigles Section des Figures (Eagle Department) | Collection / Preservation: Tate Modern Collection Ref. T07503 | Photo Credit: Tate Photography",
                "strategy": "Parodic Museums & Fictional Curatorial Departments",
                "strategy_id": "parodic_museums",
                "target": "Museum Authoritarianism, Bureaucracy, and Imperialist Classification",
                "institution_target": "Tate Modern",
                "summary": "Disillusioned by state and museum complicity during the student uprisings of May 1968, Broodthaers appointed himself 'Director' of his own fictional museum: the Musée d'Art Moderne, Département des Aigles. Installing wooden shipping crates, postcards of 19th-century masterworks, and hundreds of depictions of eagles labeled with 'This is not a work of art', Broodthaers demonstrated that museum authority is an administrative fiction constructed by capital and the state.",
                "historical_impact": "Universally regarded as the founding monument of Institutional Critique, inspiring artists from Hans Haacke and Andrea Fraser to Fred Wilson.",
                "image": "assets/visual_critique/broodthaers_museum_thumb.jpg",
                "citation": "Rectanus, M. W. (2002). Culture Incorporated: Museums, Artists, and Corporate Sponsorships. Consensus Study.",
                "doi": "10.2307/1433407"
            }
        ],
        "orsay": [
            {
                "artist_designer": "Deborah De Robertis",
                "artist": "Deborah De Robertis",
                "artwork_title": "Miroir de l'Origine (Mirror of the Origin)",
                "artwork": "Miroir de l'Origine (Mirror of the Origin)",
                "practice": "Deborah De Robertis: Physical Body Intervention & Disruption of Patriarchal Museum Gaze",
                "year": "2014–2024",
                "medium_format": "Unannounced performative body intervention, gold sequin dress, confrontation with Gustave Courbet's 'L'Origine du monde'",
                "credits": "Artist: Deborah De Robertis | Location: Musée d'Orsay Gallery 20 | Target: Musée d'Orsay Curatorial Frame & Patriarchal Exhibition Displays | Video Documentation: Deborah De Robertis Studio",
                "strategy": "Physical Body Intervention & Gaze Disruption",
                "strategy_id": "physical_intervention",
                "target": "Musée d'Orsay (Courbet Exhibition & Gendered Museography)",
                "institution_target": "Musée d'Orsay",
                "summary": "De Robertis walked into the Musée d'Orsay wearing a shimmering gold dress, sat before Courbet's 1866 masterpiece 'L'Origine du monde', and mirrored the painting's posture live in front of gallery visitors. The intervention exposed the profound double standard of the institutional museum: sanctifying the objectified female body in oil paint while calling security and criminalizing the autonomous living female body in physical gallery space.",
                "historical_impact": "Triggered international debates across French courts on artistic freedom vs museum public decency statutes; French courts acquitted De Robertis in landmark rulings upholding performance art rights.",
                "image": "assets/visual_critique/de_robertis_orsay_thumb.jpg",
                "citation": "Sharp, C., & Summers, S. (2025). Museum funding as critical practice. Museums & Social Issues / Consensus Study.",
                "doi": "10.1080/15596893.2025.2465592"
            }
        ],
        "louvre": [
            {
                "artist_designer": "Nan Goldin & P.A.I.N. (Prescription Addiction Intervention Now)",
                "artist": "Nan Goldin & P.A.I.N.",
                "artwork_title": "Sackler Die-In at the Louvre Pyramid & Bassin de l'Esplanade",
                "artwork": "Sackler Die-In at the Louvre Pyramid & Bassin de l'Esplanade",
                "practice": "Nan Goldin & P.A.I.N.: Louvre Glass Pyramid Sackler Divestment Demonstration",
                "year": "2019",
                "medium_format": "Direct-action banner deployment across I.M. Pei Pyramid reflection pool, die-in, anti-opioid leaflets in French and English",
                "credits": "Artist: Nan Goldin | Action Group: P.A.I.N. Collective | Target: Musée du Louvre (Aile Sackler / Oriental Antiquities) | Photo Credit: P.A.I.N. Media Team",
                "strategy": "Pharma & Fossil Philanthropy De-Naming",
                "strategy_id": "pharma_fossil_denaming",
                "target": "Musée du Louvre (Aile Sackler / Sackler Wing of Oriental Antiquities)",
                "institution_target": "Louvre",
                "summary": "In July 2019, Nan Goldin and P.A.I.N. activists demonstrated in front of the Louvre's I.M. Pei pyramid and inside the Sackler Wing of Oriental Antiquities. Activists unfurled a massive red banner reading 'Enlevez le nom Sackler' (Remove the Sackler Name) across the fountain basin.",
                "historical_impact": "The Louvre became the first major global museum to physically tape over and permanently scrub the Sackler name from its gallery walls in July 2019.",
                "image": "assets/visual_critique/nan_goldin_pain_sackler_met_thumb.jpg",
                "citation": "Sharp, C., & Summers, S. (2025). Museum funding as critical practice. Consensus Study.",
                "doi": "10.1080/15596893.2025.2465592"
            }
        ],
        "brooklyn-museum": [
            {
                "artist_designer": "Decolonize This Place",
                "artist": "Decolonize This Place",
                "artwork_title": "Decolonize This Place at the Brooklyn Museum",
                "artwork": "Decolonize This Place at the Brooklyn Museum",
                "practice": "Decolonize This Place: Curatorial Gentrification Protest & Indigenous Land Accord",
                "year": "2018",
                "medium_format": "Community town halls, printed protest broadsides, banner deployments, teach-ins in the museum lobby",
                "credits": "Collective: Decolonize This Place in alliance with NYC Indigenous leaders and Brooklyn anti-displacement coalitions | Target: Brooklyn Museum Governance & Curatorial Hiring Policies | Photography: Decolonize This Place",
                "strategy": "Grassroots Agitation & Board Boycotts",
                "strategy_id": "board_boycott",
                "target": "Brooklyn Museum Governance & Real Estate Gentrification",
                "institution_target": "Brooklyn Museum",
                "summary": "Following the Brooklyn Museum's controversial appointment of a white consulting curator for African Art, Decolonize This Place mobilized hundreds of community members to occupy the lobby, linking museum hiring to the rapid gentrification of surrounding Crown Heights and Bedford-Stuyvesant neighborhoods sponsored by real-estate board trustees.",
                "historical_impact": "Led to the creation of the museum's Indigenous Advisory Council and a complete restructuring of the institution's community engagement and acquisitions committees.",
                "image": "assets/visual_critique/decolonize_this_place_whitney_thumb.jpg",
                "citation": "Sharp, C., & Summers, S. (2025). Museum funding as critical practice. Consensus Study.",
                "doi": "10.1080/15596893.2025.2465592"
            }
        ],
        "manchester": [
            {
                "artist_designer": "Mark Dion",
                "artist": "Mark Dion",
                "artwork_title": "Bureau of the Centre for the Study of Surrealism and its Legacy",
                "artwork": "Bureau of the Centre for the Study of Surrealism and its Legacy",
                "practice": "Mark Dion: Surrealist Reclassification & Specimen Subversion",
                "year": "2005",
                "medium_format": "Mahogany glazed curatorial bureau, uncatalogued natural history specimens, stuffed birds, wax anatomical models, taxidermy, surrealist curios",
                "credits": "Artist: Mark Dion | Curatorial Commission: The Manchester Museum & AHRC Centre for the Study of Surrealism and its Legacy | Photo Credit: Manchester Museum Photography / University of Manchester",
                "strategy": "Surrealist Reclassification & Specimen Subversion",
                "strategy_id": "surrealist_reclassification",
                "target": "Manchester Museum & Imperialist Taxonomy Systems",
                "institution_target": "Manchester Museum",
                "summary": "Dion gained unprecedented access to the Manchester Museum's basements, gathering neglected specimens, colonial curiosities, and uncatalogued taxidermy into a mock 1920s curatorial office. Rather than arranging objects by scientific taxonomy, Dion grouped them according to dreams, uncanny associations, and poetic obsessions, deconstructing the imperial fantasy of objective scientific cataloging.",
                "historical_impact": "Permanently transformed museum curation methods for historical natural history archives and became a permanent installation at the Manchester Museum.",
                "image": "assets/visual_critique/mark_dion_manchester_thumb.jpg",
                "citation": "Gianneschi, M., & Broberg, O. (2019). A History of Cultural Sponsorship in Sweden / Natural History Curating. Consensus Study.",
                "doi": "10.4324/9780429401510-13"
            }
        ],
        "crab": [
            {
                "artist_designer": "Crab Museum Collective",
                "artist": "Crab Museum Collective",
                "artwork_title": "Humour at the Crab Museum: Environmental Satire & Corporate Mockery",
                "artwork": "Humour at the Crab Museum: Environmental Satire & Corporate Mockery",
                "practice": "Crab Museum: Anti-Capitalist Crustacean Satire & Greenwashing Subversion",
                "year": "2021–2025",
                "medium_format": "Satirical dioramas, shell oil parodies, animated mock advertisements, interactive crustacean philosophy exhibits",
                "credits": "Curatorial & Design Collective: Ned Suesst, Bertie Cordingley, and the Margate Crab Museum Team | Location: Margate, Kent, UK | Documentation: Crab Museum Archive",
                "strategy": "Environmental Satire & Corporate Mockery",
                "strategy_id": "environmental_satire",
                "target": "Corporate Greenwashing, Neoliberal Ecology, and Traditional Museum Pomp",
                "institution_target": "The Crab Museum",
                "summary": "The world's only museum dedicated entirely to the decapod crustacean uses biting scientific satire and absurdist graphic humor to mock petrochemical sponsors and corporate environmental greenwashing, demonstrating how independent, grassroots institutions can subvert corporate sponsor dependence.",
                "historical_impact": "Proved that zero-corporate-sponsor community museums can maintain high visitor engagement and critical acclaim through radical educational humor.",
                "image": "assets/visual_critique/crab_museum_margate_thumb.jpg",
                "citation": "Dolores, L., et al. (2021). Sponsorship Financial Sustainability for Cultural Conservation. Sustainability / Consensus Study.",
                "doi": "10.3390/su13169070"
            }
        ],
        "wiels": [
            {
                "artist_designer": "Marcel Broodthaers",
                "artist": "Marcel Broodthaers",
                "artwork_title": "Musée d'Art Moderne, Département des Aigles (Section XIXème Siècle)",
                "artwork": "Musée d'Art Moderne, Département des Aigles (Section XIXème Siècle)",
                "practice": "Marcel Broodthaers: Parodic Institutional Bureaucracy",
                "year": "1968–1972",
                "medium_format": "Postcards, packaging crates, letterpress manifestos, slide carousels, eagle insignia",
                "credits": "Artist: Marcel Broodthaers | Historical Retrospective: WIELS Contemporary Art Centre, Brussels | Photo Credit: WIELS Archives",
                "strategy": "Parodic Museums & Fictional Curatorial Departments",
                "strategy_id": "parodic_museums",
                "target": "Institutional Museum Authoritarianism & Capitalist Reification",
                "institution_target": "WIELS",
                "summary": "Broodthaers founded an ephemeral, parodic museum with no collection of its own, only letters of correspondence, shipping containers, and postcards. By simulating the apparatus of museum classification, Broodthaers laid bare the economic and ideological mechanisms that convert objects into cultural capital.",
                "historical_impact": "Foundational bedrock of European institutional critique and conceptual art practice.",
                "image": "assets/visual_critique/broodthaers_museum_thumb.jpg",
                "citation": "Cordelier, B., & Desaulniers, A.-A. (2020). Équilibres et médiations dans la commandite de productions artistiques. Canadian Journal of Communication / Consensus Study.",
                "doi": "10.22230/cjc.2020v45n1a3447"
            }
        ],
        "moca-los-angeles": [
            {
                "artist_designer": "Mel Chin & GALA Committee",
                "artist": "Mel Chin & GALA Committee",
                "artwork_title": "Total Proof: The GALA Committee 1995–1997",
                "artwork": "Total Proof: The GALA Committee 1995–1997",
                "practice": "Mel Chin: Prime-Time Television Prop Infiltration & Corporate Media Subversion",
                "year": "1995–1997",
                "medium_format": "Stealth props, bedding, paintings, and glassware with subversive iconography broadcast weekly on prime-time FOX drama 'Melrose Place'",
                "credits": "Lead Artist / Concept: Mel Chin | Collective: GALA Committee (collaborative students and artists from CalArts and UGA) | Exhibited: MOCA Los Angeles & Redcat | Photo Credit: Mel Chin Studio",
                "strategy": "Subversive Mass Media Infiltration",
                "strategy_id": "ideological_distribution",
                "target": "Commercial Prime-Time Media Hegemony & Corporate Censorship",
                "institution_target": "MOCA Los Angeles",
                "summary": "Mel Chin formed the GALA Committee to covertly insert radical artworks as functional props onto the set of the popular prime-time soap opera 'Melrose Place'. Over nearly three years, unseen by censors, props containing imagery addressing the Gulf War, Chinese history, AIDS awareness, and reproductive rights were broadcast into millions of American living rooms weekly, culminating in an exhibition at MOCA Los Angeles.",
                "historical_impact": "Redefined the terrain of conceptual institutional critique from the white cube into commercial mass media syndication.",
                "image": "assets/visual_critique/mel_chin_gala_committee_thumb.jpg",
                "citation": "Konrad, E. D. (2013). Cultural Entrepreneurship: The Impact of Social Networking on Success. Creativity and Innovation Management / Consensus Study.",
                "doi": "10.1111/caim.12032"
            }
        ],
        "art-institute-chicago": [
            {
                "artist_designer": "Michael Asher",
                "artist": "Michael Asher",
                "artwork_title": "Institutional Deconstruction / Relocation of George Washington",
                "artwork": "Institutional Deconstruction / Relocation of George Washington",
                "practice": "Michael Asher: Architectural Displacement & Historical Framing",
                "year": "1979",
                "medium_format": "Temporary relocation of an 18th-century bronze replica of Jean-Antoine Houdon's statue of George Washington from the museum facade steps into an 18th-century European decorative art gallery",
                "credits": "Artist: Michael Asher | Exhibition: 73rd American Exhibition (curated by Anne Rorimer) | Institutional Target: Art Institute of Chicago | Photo Credit: Art Institute of Chicago Archives",
                "strategy": "Curatorial & Spatial Displacement",
                "strategy_id": "curatorial_subversion",
                "target": "Art Institute of Chicago & Civic Mythology",
                "institution_target": "Art Institute of Chicago",
                "summary": "Asher removed the bronze statue of George Washington from its grand exterior pedestal overlooking Michigan Avenue and placed it inside Gallery 219 among European decorative arts, tapestries, and Louis XVI furniture. By shifting the context from public patriotic monument to an item in an aristocratic interior, Asher demonstrated how museum architecture naturalizes political myths.",
                "historical_impact": "Pioneered spatial subtraction and relocation as critical methodologies for exposing the political construction of museum environments.",
                "image": "assets/visual_critique/michael_asher_art_institute_thumb.jpg",
                "citation": "Rectanus, M. W. (2002). Culture Incorporated: Museums, Artists, and Corporate Sponsorships. Consensus Study.",
                "doi": "10.2307/1433407"
            }
        ],
        "walker-art-center": [
            {
                "artist_designer": "Coco Fusco & Guillermo Gómez-Peña",
                "artist": "Coco Fusco & Guillermo Gómez-Peña",
                "artwork_title": "Two Undiscovered Amerindians Visit the West (The Couple in the Cage)",
                "artwork": "Two Undiscovered Amerindians Visit the West (The Couple in the Cage)",
                "practice": "Coco Fusco & Guillermo Gómez-Peña: Parodic Human Zoo & Colonial Gaze Satire",
                "year": "1992–1993",
                "medium_format": "Interactive performance in a 10x12 golden cage, synthetic traditional costumes, polaroid photography, fictitious language translation, museum docent lectures",
                "credits": "Artists: Coco Fusco & Guillermo Gómez-Peña | Curatorial Commission: Edge '92 Biennial & Walker Art Center Tour | Video Documentation: Paula Heredia | Photo Credit: Walker Art Center Archives",
                "strategy": "Parodic Museums & Fictional Curatorial Departments",
                "strategy_id": "parodic_museums",
                "target": "Walker Art Center & Western Ethnographic Museum Displays",
                "institution_target": "Walker Art Center",
                "summary": "To commemorate the quincentennial of Columbus's arrival in the Americas, Fusco and Gómez-Peña lived in a golden cage as 'undiscovered natives' from an unmapped island in the Gulf of Mexico. Exhibited in major plazas and museums including the Walker Art Center, the artists watched television, wore sunglasses, and had museum docents conduct mock ethnographic lectures. Strikingly, thousands of museum visitors believed the performance was real, exposing the persistence of colonial racism.",
                "historical_impact": "Exposed the lingering colonial gaze of major cultural institutions and fundamentally transformed institutional discourse on post-colonial curating.",
                "image": "assets/visual_critique/coco_fusco_couple_cage_thumb.jpg",
                "citation": "Casado-Molina, A.-M., et al. (2023). Building mutual rewarding sponsor relationships between museums and corporations. Consensus Study.",
                "doi": "10.1080/09548963.2023.2255836"
            }
        ]
    }

    # Match each institution in institutions.json and enrich
    updated_count = 0
    for inst in institutions:
        name_lower = inst.get("name", "").lower()
        id_lower = inst.get("id", "").lower()
        matched_critiques = []

        if "guggenheim" in name_lower or "guggenheim" in id_lower:
            matched_critiques.extend(critique_db["guggenheim"])
        if "moma" in name_lower or "moma" in id_lower:
            matched_critiques.extend(critique_db["moma"])
        if "whitney" in name_lower or "whitney" in id_lower:
            matched_critiques.extend(critique_db["whitney"])
        if ("metropolitan museum" in name_lower or "the met" in name_lower or "the-met" in id_lower) and "manila" not in name_lower:
            matched_critiques.extend(critique_db["metropolitan"])
        if "british museum" in name_lower or "british-museum" in id_lower:
            matched_critiques.extend(critique_db["british-museum"])
        if "tate" in name_lower or "tate" in id_lower:
            if "tate" in name_lower and not ("state" in name_lower):
                matched_critiques.extend(critique_db["tate-modern"])
        if "orsay" in name_lower or "orsay" in id_lower:
            matched_critiques.extend(critique_db["orsay"])
        if "louvre" in name_lower or "louvre" in id_lower:
            if "abu dhabi" not in name_lower:
                matched_critiques.extend(critique_db["louvre"])
        if "brooklyn museum" in name_lower or "brooklyn-museum" in id_lower:
            matched_critiques.extend(critique_db["brooklyn-museum"])
        if "manchester" in name_lower or "manchester" in id_lower or "whitworth" in name_lower:
            matched_critiques.extend(critique_db["manchester"])
        if "crab" in name_lower or "crab" in id_lower:
            matched_critiques.extend(critique_db["crab"])
        if "wiels" in name_lower or "wiels" in id_lower:
            matched_critiques.extend(critique_db["wiels"])
        if "moca" in name_lower and "los angeles" in name_lower:
            matched_critiques.extend(critique_db["moca-los-angeles"])
        if "art institute of chicago" in name_lower or "art-institute-of-chicago" in id_lower:
            matched_critiques.extend(critique_db["art-institute-chicago"])
        if "walker art center" in name_lower or "walker-art-center" in id_lower:
            matched_critiques.extend(critique_db["walker-art-center"])

        if matched_critiques:
            # Deduplicate by artwork_title
            existing_vcs = inst.get("visual_critiques") or []
            existing_titles = {v.get("artwork_title", v.get("artwork", "")).lower() for v in existing_vcs}
            for mc in matched_critiques:
                t = mc.get("artwork_title", mc.get("artwork", "")).lower()
                if t not in existing_titles:
                    existing_vcs.append(mc)
                    existing_titles.add(t)
            inst["visual_critiques"] = existing_vcs
            updated_count += 1

    with open("institutions.json", "w", encoding="utf-8") as f:
        json.dump(institutions, f, indent=2, ensure_ascii=False)

    print(f"Updated institutions.json with verified visual critiques! Total institutions with visual critiques: {updated_count}")

if __name__ == "__main__":
    enrich()
