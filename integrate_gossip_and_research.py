#!/usr/bin/env python3
"""
integrate_gossip_and_research.py
Integrates:
1. Academic studies from 'make a gossip rearch about cultural institutions - Oct 09, 2026.csv' into 'academic_papers.json'.
2. 25 investigation cases, 77 employee review leads, and 126 linked sources from
   'culture-atlas-gossip-dataset.json' and 'culture-atlas-gossip-research.md' into 'institutions.json'.
3. Adds any missing institutions into 'institutions.json' with precise coordinates, governance, and audit dossier links.
"""

import json
import csv
import os
import re

def run_integration():
    print("--- 1. MERGING ACADEMIC PAPERS CSV INTO ACADEMIC_PAPERS.JSON ---")
    academic_path = "academic_papers.json"
    csv_path = "/Users/polinavasilyeva/Downloads/make a gossip rearch about cultural institutions - Oct 09, 2026.csv"
    
    with open(academic_path, "r", encoding="utf-8") as f:
        academic_papers = json.load(f)
    
    existing_dois = {p.get("doi", "").strip().lower() for p in academic_papers if p.get("doi")}
    existing_titles = {p.get("title", "").strip().lower() for p in academic_papers if p.get("title")}
    
    new_paper_count = 0
    if os.path.exists(csv_path):
        with open(csv_path, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                title = (row.get("Title") or "").strip()
                doi = (row.get("DOI") or "").strip()
                if not title:
                    continue
                if title.lower() in existing_titles or (doi and doi.lower() in existing_dois):
                    continue
                
                academic_papers.append({
                    "title": title,
                    "takeaway": (row.get("Takeaway") or "").strip(),
                    "authors": (row.get("Authors") or "").strip(),
                    "year": (row.get("Year") or "").strip(),
                    "citations": (row.get("Citations") or "0").strip(),
                    "abstract": (row.get("Abstract") or "").strip(),
                    "journal": (row.get("Journal") or "").strip(),
                    "doi": doi,
                    "link": (row.get("Consensus Link") or "").strip(),
                    "study_type": (row.get("Study Type") or "").strip()
                })
                existing_titles.add(title.lower())
                if doi:
                    existing_dois.add(doi.lower())
                new_paper_count += 1
                
    with open(academic_path, "w", encoding="utf-8") as f:
        json.dump(academic_papers, f, indent=2, ensure_ascii=False)
    print(f"✅ Academic papers updated: +{new_paper_count} new papers, total {len(academic_papers)}.")

    print("\n--- 2. LOADING GOSSIP RESEARCH DATASET & INSTITUTIONS ---")
    gossip_dataset_path = "data/culture-atlas-gossip-dataset.json"
    with open(gossip_dataset_path, "r", encoding="utf-8") as f:
        gossip_data = json.load(f)

    with open("institutions.json", "r", encoding="utf-8") as f:
        institutions = json.load(f)

    sources_map = {s["id"]: s for s in gossip_data.get("sources", [])}

    # Ensure all institutions have an ID
    for i in institutions:
        if "id" not in i or not i["id"]:
            i["id"] = re.sub(r'[^a-z0-9]+', '-', i["name"].lower()).strip('-')

    # Map existing institutions by lowercase normalized name and ID
    inst_by_id = {i["id"]: i for i in institutions}
    inst_by_name = {i["name"].lower().strip(): i for i in institutions}

    # Define missing institutions to add
    new_institutions = [
        {
            "name": "London Museum",
            "city": "London",
            "country": "United Kingdom",
            "location": "London, United Kingdom",
            "lat": 51.5186,
            "lon": -0.0967,
            "tier": "B",
            "tier_label": "Flagged",
            "size": "Large",
            "governance_type": "Trust-Operated City Museum",
            "governance_classification": "City & Heritage Trust",
            "website": "https://www.londonmuseum.org.uk",
            "funding": "City of London Corporation and Greater London Authority public funding; admission free.",
            "watch": "3.5% pay agreement reached with Prospect in April 2026; contested pigeon logo attribution claim.",
            "sources": ["Museums Association", "Prospect Union", "May Wild Studio Statement"],
            "curatorial_focus": "Social history of London, archaeology, contemporary urban culture",
            "admission_policy": "Always Free Public Admission",
            "admission_details": "Universal free public admission to permanent galleries.",
            "ethical_safeguard": "Audited local government accountability standards.",
            "year_founded": 1976,
            "transparency_grade": "B+",
            "curator_recommendation": "Historic chronicle of London's civic transformation from Roman times to the present.",
            "id": "london-museum"
        },
        {
            "name": "American Folk Art Museum",
            "city": "New York",
            "country": "United States",
            "location": "New York, United States",
            "lat": 40.7725,
            "lon": -73.9822,
            "tier": "B",
            "tier_label": "Flagged",
            "size": "Medium",
            "governance_type": "Private Non-Profit Museum",
            "governance_classification": "Non-Profit 501(c)(3)",
            "website": "https://folkartmuseum.org",
            "funding": "Private philanthropy, grants, and public foundation support; always free admission.",
            "watch": "First UAW Local 2110 collective bargaining contract ratified on 2 October 2026 averting strike.",
            "sources": ["UAW Local 2110", "Hyperallergic", "IRS Form 990"],
            "curatorial_focus": "Self-taught art, vernacular craft, historical and contemporary folk art",
            "admission_policy": "Always Free Public Admission",
            "admission_details": "Free admission to all exhibitions at Lincoln Square.",
            "ethical_safeguard": "Union representation across administrative and curatorial staff.",
            "year_founded": 1961,
            "transparency_grade": "A-",
            "curator_recommendation": "Crucial institution celebrating idiosyncratic self-taught creators and vernacular artistry.",
            "id": "american-folk-art-museum"
        },
        {
            "name": "Neue Nationalgalerie",
            "city": "Berlin",
            "country": "Germany",
            "location": "Berlin, Germany",
            "lat": 52.5069,
            "lon": 13.3675,
            "tier": "B",
            "tier_label": "Flagged",
            "size": "Large",
            "governance_type": "Staatliche Museen zu Berlin / SPK",
            "governance_classification": "Federal Cultural Foundation",
            "website": "https://www.smb.museum/museen-einrichtungen/neue-nationalgalerie",
            "funding": "Federal Government Commissioner for Culture and the Media (BKM) and Land Berlin.",
            "watch": "Nan Goldin retrospective controversy over disputed slide removal; completed in April 2025.",
            "sources": ["Staatliche Museen zu Berlin", "Der Tagesspiegel", "SMB Annual Report"],
            "curatorial_focus": "20th-century classical modernism, Mies van der Rohe architecture, modern sculpture",
            "admission_policy": "Paid / Subsidised Concessions",
            "admission_details": "Standard timed entry ticket with federal museum pass access.",
            "ethical_safeguard": "Federal public governance under Stiftung Preußischer Kulturbesitz.",
            "year_founded": 1968,
            "transparency_grade": "B+",
            "curator_recommendation": "Iconic Mies van der Rohe pavilion housing monumental masterpieces of 20th-century art.",
            "id": "neue-nationalgalerie-berlin"
        },
        {
            "name": "Hamburger Bahnhof – Nationalgalerie der Gegenwart",
            "city": "Berlin",
            "country": "Germany",
            "location": "Berlin, Germany",
            "lat": 52.5284,
            "lon": 13.3719,
            "tier": "B",
            "tier_label": "Flagged",
            "size": "Large",
            "governance_type": "Staatliche Museen zu Berlin / SPK",
            "governance_classification": "Federal Cultural Foundation",
            "website": "https://www.smb.museum/museen-einrichtungen/hamburger-bahnhof",
            "funding": "Federal Government Commissioner for Culture and the Media (BKM).",
            "watch": "Tania Bruguera 100-hour reading performance concluded early following protest disruption.",
            "sources": ["The Art Newspaper", "Staatliche Museen zu Berlin", "SPK Disclosures"],
            "curatorial_focus": "Contemporary art from 1960 to the present, Joseph Beuys archive, site-specific installations",
            "admission_policy": "Paid / Subsidised Concessions",
            "admission_details": "Standard admission ticket with Berlin Museum Pass concessions.",
            "ethical_safeguard": "Federal public governance under SPK.",
            "year_founded": 1996,
            "transparency_grade": "B+",
            "curator_recommendation": "Vast neo-Renaissance railway terminus converted into Berlin's premier museum for cutting-edge contemporary art.",
            "id": "hamburger-bahnhof-berlin"
        },
        {
            "name": "Oyoun",
            "city": "Berlin",
            "country": "Germany",
            "location": "Berlin, Germany",
            "lat": 52.4820,
            "lon": 13.4338,
            "tier": "A",
            "tier_label": "Clean",
            "size": "Medium",
            "governance_type": "Non-Profit Cultural Centre & Co-Operative",
            "governance_classification": "Grassroots Independent Non-Profit",
            "website": "https://oyoun.de",
            "funding": "Community support, independent non-profit foundation grants (Supporting Act Foundation), collective donations.",
            "watch": "Contested Berlin Senate funding withdrawal; July 2024 constitutional court procedural remand.",
            "sources": ["Oyoun Press Statement", "Verfassungsgerichtshof Berlin", "Berlin Senate Cultural Administration"],
            "curatorial_focus": "Decolonial, queer, diasporic, and intersectional contemporary arts and community programming",
            "admission_policy": "Sliding Scale / Free Community Entry",
            "admission_details": "Accessible solidarity pricing and free entry for community discussions.",
            "ethical_safeguard": "Independent community-directed governance without corporate underwriting.",
            "year_founded": 2020,
            "transparency_grade": "A",
            "curator_recommendation": "Independent anti-disciplinary cultural hub championing decolonial artistic inquiry.",
            "id": "oyoun-berlin"
        },
        {
            "name": "Het Concertgebouw",
            "city": "Amsterdam",
            "country": "Netherlands",
            "location": "Amsterdam, Netherlands",
            "lat": 52.3563,
            "lon": 4.8791,
            "tier": "B",
            "tier_label": "Flagged",
            "size": "Large",
            "governance_type": "Private Foundation Concert Hall",
            "governance_classification": "Cultural Foundation",
            "website": "https://www.concertgebouw.nl",
            "funding": "Ticket sales, private sponsorships, endowment support, and public grants.",
            "watch": "Parliamentary debate in May 2026 over new programming guidelines and exclusions.",
            "sources": ["Tweede Kamer der Staten-Generaal", "Concertgebouw Annual Report", "Dutch Ministry of OCW"],
            "curatorial_focus": "Symphonic acoustics, classical music, recitals, and contemporary orchestral works",
            "admission_policy": "Ticketed Concert Venue",
            "admission_details": "Concert ticket required; free lunchtime concerts on selected Wednesdays.",
            "ethical_safeguard": "Subject to Dutch cultural governance codes and parliamentary oversight.",
            "year_founded": 1888,
            "transparency_grade": "B+",
            "curator_recommendation": "One of the world's most acoustically renowned concert halls.",
            "id": "het-concertgebouw-amsterdam"
        },
        {
            "name": "Casa de la Arquitectura",
            "city": "Madrid",
            "country": "Spain",
            "location": "Madrid, Spain",
            "lat": 40.4439,
            "lon": -3.6922,
            "tier": "B",
            "tier_label": "Flagged",
            "size": "Medium",
            "governance_type": "Public National Museum / MITMA",
            "governance_classification": "National Public Museum",
            "website": "https://casadelaarquitectura.gob.es",
            "funding": "Ministry of Housing and Urban Agenda (MIVAU / MITMA) public appropriations.",
            "watch": "SUT union agreement resolved contractor Magmacultura hours dispute and retroactive pay.",
            "sources": ["Sindicato SUT", "MIVAU Official Register", "Boletín Oficial del Estado"],
            "curatorial_focus": "Contemporary Spanish architecture, urbanism, landscape, and spatial design",
            "admission_policy": "Always Free Public Admission",
            "admission_details": "Universal free entry to all exhibition halls at Paseo de la Castellana.",
            "ethical_safeguard": "Public ministry administration with negotiated union collective standards.",
            "year_founded": 2023,
            "transparency_grade": "A-",
            "curator_recommendation": "Spain's dedicated national institution highlighting sustainable spatial design and architectural history.",
            "id": "casa-de-la-arquitectura-madrid"
        },
        {
            "name": "CaixaForum Madrid",
            "city": "Madrid",
            "country": "Spain",
            "location": "Madrid, Spain",
            "lat": 40.4111,
            "lon": -3.6936,
            "tier": "B",
            "tier_label": "Flagged",
            "size": "Large",
            "governance_type": "Corporate Foundation Cultural Center",
            "governance_classification": "Corporate Foundation (Fundación 'la Caixa')",
            "website": "https://caixaforum.org/es/madrid",
            "funding": "Fundación 'la Caixa' banking foundation endowment and exhibition tickets.",
            "watch": "SUT agreement in December 2025 restored guaranteed hours for Magmacultura contractor staff.",
            "sources": ["Sindicato SUT", "Fundación 'la Caixa' Annual Report", "Herzog & de Meuron Archive"],
            "curatorial_focus": "International museum loans, ancient civilizations, photography, modern art, Herzog & de Meuron vertical garden",
            "admission_policy": "Subsidised Entry / Free for CaixaBank Clients & Under 16",
            "admission_details": "€6 general entry; complimentary for customers of CaixaBank and youth.",
            "ethical_safeguard": "Audited corporate foundation disclosures under Spanish foundation law.",
            "year_founded": 2008,
            "transparency_grade": "B",
            "curator_recommendation": "Spectacular Herzog & de Meuron converted power station featuring Patrick Blanc's lush vertical garden.",
            "id": "caixaforum-madrid"
        },
        {
            "name": "Museo Nacional del Prado",
            "city": "Madrid",
            "country": "Spain",
            "location": "Madrid, Spain",
            "lat": 40.4138,
            "lon": -3.6921,
            "tier": "B",
            "tier_label": "Flagged",
            "size": "Large",
            "governance_type": "National Public Cultural Institution",
            "governance_classification": "Organismo Autónomo / Ministerio de Cultura",
            "website": "https://www.museodelprado.es",
            "funding": "Spanish Ministry of Culture appropriations, box office, corporate patron sponsors (Santander, Telefónica, AXA).",
            "watch": "Major national museum subject to statutory civil service examinations; workplace reviews on competitive exams.",
            "sources": ["Boletín Oficial del Estado", "Prado Annual Accounts", "Glassdoor Reviews"],
            "curatorial_focus": "Spanish Royal Collection, Velázquez, Goya, El Greco, Hieronymus Bosch, Italian and Flemish masters",
            "admission_policy": "Paid / Free Daily Evening Hours",
            "admission_details": "Free entry Monday to Saturday 18:00–20:00 and Sunday 17:00–19:00.",
            "ethical_safeguard": "Statutory public transparency audits under Ley Reguladora del Museo del Prado.",
            "year_founded": 1819,
            "transparency_grade": "B+",
            "curator_recommendation": "Unrivalled royal collection housing Las Meninas and The Garden of Earthly Delights.",
            "id": "museo-nacional-del-prado"
        },
        {
            "name": "Museo Nacional Thyssen-Bornemisza",
            "city": "Madrid",
            "country": "Spain",
            "location": "Madrid, Spain",
            "lat": 40.4160,
            "lon": -3.6949,
            "tier": "B",
            "tier_label": "Flagged",
            "size": "Large",
            "governance_type": "Public Foundation Museum",
            "governance_classification": "Fundación Colección Thyssen-Bornemisza",
            "website": "https://www.museothyssen.org",
            "funding": "Ministry of Culture operating subsidies, ticket sales, commercial retail, private patrons.",
            "watch": "Workplace reviews regarding freelance classification, unpaid internships, and government lease terms.",
            "sources": ["Ministerio de Cultura", "Thyssen Foundation Accounts", "Glassdoor Reviews"],
            "curatorial_focus": "Eight centuries of European painting, Impressionism, German Expressionism, Russian Constructivism",
            "admission_policy": "Paid / Free Monday Access",
            "admission_details": "Complimentary entry on Mondays 12:00–16:00 sponsored by Mastercard.",
            "ethical_safeguard": "Joint state and foundation board governance.",
            "year_founded": 1992,
            "transparency_grade": "B",
            "curator_recommendation": "Fabulous survey spanning eight centuries of Western painting bridging the Prado and Reina Sofía.",
            "id": "museo-thyssen-bornemisza"
        },
        {
            "name": "Teatro Real",
            "city": "Madrid",
            "country": "Spain",
            "location": "Madrid, Spain",
            "lat": 40.4183,
            "lon": -3.7106,
            "tier": "B",
            "tier_label": "Flagged",
            "size": "Large",
            "governance_type": "Public Opera Foundation",
            "governance_classification": "Fundación del Teatro Lírico",
            "website": "https://www.teatroreal.es",
            "funding": "Ministry of Culture, Comunidad de Madrid, ticket subscriptions, and corporate sponsor board.",
            "watch": "Staff accounts concerning technical scheduling, internship remuneration, and corporate patron underwriting.",
            "sources": ["Fundación Teatro Real", "Ministerio de Cultura", "Glassdoor Reviews"],
            "curatorial_focus": "Grand opera, international co-productions, classical ballet, symphony concerts",
            "admission_policy": "Ticketed Opera House",
            "admission_details": "Ticket required for performances; guided architectural tours available daily.",
            "ethical_safeguard": "Public foundation oversight with joint municipal and ministry trustees.",
            "year_founded": 1850,
            "transparency_grade": "B",
            "curator_recommendation": "Spain's premier lyric theatre facing the Palacio Real.",
            "id": "teatro-real-madrid"
        },
        {
            "name": "Barbican Centre",
            "city": "London",
            "country": "United Kingdom",
            "location": "London, United Kingdom",
            "lat": 51.5202,
            "lon": -0.0938,
            "tier": "B",
            "tier_label": "Flagged",
            "size": "Large",
            "governance_type": "City of London Corporation Arts Centre",
            "governance_classification": "Municipal Cultural Centre",
            "website": "https://www.barbican.org.uk",
            "funding": "City of London Corporation funding, box office revenue, venue hire, commercial leases.",
            "watch": "Employee accounts regarding management restructuring, intern support, and living costs in London.",
            "sources": ["City of London Corporation", "Barbican Annual Review", "Glassdoor Reviews"],
            "curatorial_focus": "Brutalist architecture, contemporary art gallery, London Symphony Orchestra home, international cinema",
            "admission_policy": "Free Foyers & Public Spaces / Ticketed Exhibitions",
            "admission_details": "Free public access to brutalist foyers, conservatory, and library; ticketed exhibitions.",
            "ethical_safeguard": "City of London statutory committees and equality audits.",
            "year_founded": 1982,
            "transparency_grade": "B+",
            "curator_recommendation": "Monumental utopian brutalist performing arts centre with extraordinary conservatory and cinema.",
            "id": "barbican-centre-london"
        },
        {
            "name": "Royal Academy of Arts",
            "city": "London",
            "country": "United Kingdom",
            "location": "London, United Kingdom",
            "lat": 51.5091,
            "lon": -0.1396,
            "tier": "B",
            "tier_label": "Flagged",
            "size": "Large",
            "governance_type": "Independent Privately Funded Society of Artists",
            "governance_classification": "Royal Charter Charity",
            "website": "https://www.royalacademy.org.uk",
            "funding": "Privately funded without core government grant; ticket sales, Royal Academicians, corporate patrons, Summer Exhibition.",
            "watch": "Staff accounts alleging wage suppression, restructuring redundancies, and donor dependence.",
            "sources": ["Charity Commission for England and Wales", "RA Annual Report", "Glassdoor Reviews"],
            "curatorial_focus": "Artist-led academy exhibitions, Summer Exhibition, RA Schools, architectural forums",
            "admission_policy": "Free Public Courtyard & Collection / Ticketed Temporary Shows",
            "admission_details": "Free entry to Burlington Gardens permanent displays; ticketed major loan shows.",
            "ethical_safeguard": "Governed by practicing artist Academicians under Royal Charter.",
            "year_founded": 1768,
            "transparency_grade": "B",
            "curator_recommendation": "Britain's historic artist-run academy housed in magnificent Burlington House.",
            "id": "royal-academy-of-arts-london"
        },
        {
            "name": "Institute of Contemporary Arts (ICA)",
            "city": "London",
            "country": "United Kingdom",
            "location": "London, United Kingdom",
            "lat": 51.5065,
            "lon": -0.1302,
            "tier": "B",
            "tier_label": "Flagged",
            "size": "Medium",
            "governance_type": "Registered Educational Charity",
            "governance_classification": "Arts Council England NPO",
            "website": "https://www.ica.art",
            "funding": "Arts Council England National Portfolio funding, membership, cinema tickets, foundation grants.",
            "watch": "Historic contemporary arts institute; employee reports regarding building infrastructure and compensation.",
            "sources": ["Arts Council England", "Charity Commission", "Glassdoor Reviews"],
            "curatorial_focus": "Radical contemporary art, avant-garde cinema, experimental music, performance, political forums",
            "admission_policy": "Day Membership / Paid Cinema & Exhibitions",
            "admission_details": "Modest £1 day membership for gallery access; concession tickets for students.",
            "ethical_safeguard": "Charity Commission oversight; no fossil fuel or defense corporate patrons.",
            "year_founded": 1946,
            "transparency_grade": "A-",
            "curator_recommendation": "The historic crucible of British post-war avant-garde culture located on The Mall.",
            "id": "ica-london"
        },
        {
            "name": "New Museum of Contemporary Art",
            "city": "New York",
            "country": "United States",
            "location": "New York, United States",
            "lat": 40.7223,
            "lon": -73.9929,
            "tier": "B",
            "tier_label": "Flagged",
            "size": "Medium",
            "governance_type": "Non-Profit Museum",
            "governance_classification": "Non-Profit 501(c)(3)",
            "website": "https://www.newmuseum.org",
            "funding": "Trustee donations, gala, foundation grants, admission tickets, SANAA expansion capital campaign.",
            "watch": "UAW Local 2110 unionised staff; workplace reviews on organizational hierarchy and resource allocation.",
            "sources": ["UAW Local 2110", "New York Charities Bureau", "Glassdoor Reviews"],
            "curatorial_focus": "Living contemporary artists, Triennial, global digital art, SANAA architecture on the Bowery",
            "admission_policy": "Paid / Pay-What-You-Wish Thursday Evenings",
            "admission_details": "Pay-what-you-wish admission on Thursday evenings 19:00–21:00.",
            "ethical_safeguard": "Unionised staff contract with UAW Local 2110.",
            "year_founded": 1977,
            "transparency_grade": "B",
            "curator_recommendation": "Marcia Tucker's radical creation dedicated exclusively to new art and new ideas.",
            "id": "new-museum-new-york"
        },
        {
            "name": "Brooklyn Academy of Music (BAM)",
            "city": "New York",
            "country": "United States",
            "location": "New York, United States",
            "lat": 40.6865,
            "lon": -73.9777,
            "tier": "B",
            "tier_label": "Flagged",
            "size": "Large",
            "governance_type": "Non-Profit Multi-Arts Center",
            "governance_classification": "Non-Profit 501(c)(3)",
            "website": "https://www.bam.org",
            "funding": "New York City Department of Cultural Affairs, corporate sponsorships, box office, private philanthropy.",
            "watch": "Staff reviews tracking management support and career progression across theatre and cinema.",
            "sources": ["NYC DCLA", "IRS Form 990", "Glassdoor Reviews"],
            "curatorial_focus": "Next Wave Festival, avant-garde performing arts, independent cinema, opera, dance",
            "admission_policy": "Ticketed Performance Halls / Free Public Cinema Programs",
            "admission_details": "Ticket required for mainstage productions; discounted community rush seats.",
            "ethical_safeguard": "Audited non-profit governance under New York state oversight.",
            "year_founded": 1861,
            "transparency_grade": "B+",
            "curator_recommendation": "America's oldest continuously operating performing arts center, home to the Next Wave Festival.",
            "id": "bam-new-york"
        },
        {
            "name": "Berlinische Galerie",
            "city": "Berlin",
            "country": "Germany",
            "location": "Berlin, Germany",
            "lat": 52.5036,
            "lon": 13.3989,
            "tier": "B",
            "tier_label": "Flagged",
            "size": "Medium",
            "governance_type": "Public Law Foundation (Land Berlin)",
            "governance_classification": "Stiftung Öffentlichen Rechts",
            "website": "https://berlinischegalerie.de",
            "funding": "Senatsverwaltung für Kultur und Gesellschaftlichen Zusammenhalt Berlin.",
            "watch": "State museum for modern art, photography, and architecture; freelance contractor representation reports.",
            "sources": ["Land Berlin Cultural Budget", "Berlinische Galerie Jahresbericht", "Kununu Reviews"],
            "curatorial_focus": "Berlin art from 1870 to the present, Berlin Dada, Eastern European avant-garde, architecture, photography",
            "admission_policy": "Paid / Free First Sunday of the Month",
            "admission_details": "Complimentary entry on Museumssonntag (first Sunday of each month).",
            "ethical_safeguard": "Public foundation statutes under Land Berlin.",
            "year_founded": 1975,
            "transparency_grade": "A-",
            "curator_recommendation": "Essential museum documenting Berlin's turbulent artistic transformations from Dada to post-wall subculture.",
            "id": "berlinische-galerie"
        },
        {
            "name": "Museum für Naturkunde",
            "city": "Berlin",
            "country": "Germany",
            "location": "Berlin, Germany",
            "lat": 52.5303,
            "lon": 13.3797,
            "tier": "B",
            "tier_label": "Flagged",
            "size": "Large",
            "governance_type": "Leibniz Association Public Law Foundation",
            "governance_classification": "Stiftung des Öffentlichen Rechts",
            "website": "https://www.museumfuernaturkunde.berlin",
            "funding": "Federal Ministry of Education and Research (BMBF) and State of Berlin joint financing.",
            "watch": "Leibniz Institute natural history museum; employee Kununu accounts detailing administrative workload.",
            "sources": ["Leibniz-Gemeinschaft", "BMBF Public Research Register", "Kununu Reviews"],
            "curatorial_focus": "Evolutionary research, biodiversity, palaeontology, Tristan Otto T-rex, wet collections",
            "admission_policy": "Paid / Subsidised Family & Student Rates",
            "admission_details": "Standard entry tickets; free for children under 6 and school groups.",
            "ethical_safeguard": "Leibniz Association research ethics and scientific governance codes.",
            "year_founded": 1810,
            "transparency_grade": "B+",
            "curator_recommendation": "World-class natural history research museum housing the world's largest mounted dinosaur skeleton.",
            "id": "museum-fuer-naturkunde-berlin"
        },
        {
            "name": "Jüdisches Museum Berlin",
            "city": "Berlin",
            "country": "Germany",
            "location": "Berlin, Germany",
            "lat": 52.5022,
            "lon": 13.3953,
            "tier": "B",
            "tier_label": "Flagged",
            "size": "Large",
            "governance_type": "Federal Direct Public Law Foundation",
            "governance_classification": "Bundesunmittelbare Stiftung des Öffentlichen Rechts",
            "website": "https://www.jmberlin.de",
            "funding": "Federal Government Commissioner for Culture and the Media (BKM) public budget.",
            "watch": "Federal foundation museum; employee reviews regarding flexible working and administration.",
            "sources": ["BKM Bundeshaushalt", "JMB Annual Report", "Kununu Reviews"],
            "curatorial_focus": "Jewish-German history, Holocaust memorialisation, Daniel Libeskind architecture, contemporary diaspora",
            "admission_policy": "Free Permanent Exhibition / Ticketed Temporary Shows",
            "admission_details": "Universal free admission to Daniel Libeskind permanent exhibition.",
            "ethical_safeguard": "Federal parliament oversight and public foundation transparency.",
            "year_founded": 2001,
            "transparency_grade": "A-",
            "curator_recommendation": "Daniel Libeskind's masterpiece of deconstructivist architecture presenting two millennia of German-Jewish history.",
            "id": "juedisches-museum-berlin"
        },
        {
            "name": "Humboldt Forum",
            "city": "Berlin",
            "country": "Germany",
            "location": "Berlin, Germany",
            "lat": 52.5175,
            "lon": 13.4028,
            "tier": "B",
            "tier_label": "Flagged",
            "size": "Large",
            "governance_type": "Federal Government Cultural Foundation",
            "governance_classification": "Stiftung Humboldt Forum im Berliner Schloss",
            "website": "https://www.humboldtforum.org",
            "funding": "Federal Government Commissioner for Culture and the Media (BKM).",
            "watch": "Restitution debates (Benin bronzes) and freelance contractor payment processing reviews at the reconstructed Schloss.",
            "sources": ["Bundeshaushalt BKM", "Stiftung Humboldt Forum", "Kununu Reviews"],
            "curatorial_focus": "Ethnological collections, Asian art, world cultures, Franco Stella architecture",
            "admission_policy": "Free Permanent Collections / Ticketed Special Exhibitions",
            "admission_details": "Free entry to Ethnological Museum and Museum of Asian Art permanent displays.",
            "ethical_safeguard": "Federal governance and international restitution task force oversight.",
            "year_founded": 2020,
            "transparency_grade": "B",
            "curator_recommendation": "Monumental cultural complex uniting Berlin's global collections inside the reconstructed Baroque palace.",
            "id": "humboldt-forum-berlin"
        },
        {
            "name": "Deutsches Historisches Museum",
            "city": "Berlin",
            "country": "Germany",
            "location": "Berlin, Germany",
            "lat": 52.5178,
            "lon": 13.3970,
            "tier": "B",
            "tier_label": "Flagged",
            "size": "Large",
            "governance_type": "Federal Government Public Law Foundation",
            "governance_classification": "Stiftung Deutsches Historisches Museum",
            "website": "https://www.dhm.de",
            "funding": "Federal Government Commissioner for Culture and the Media (BKM) financing.",
            "watch": "Federal history museum; employee reports on institutional hierarchy and digital infrastructure.",
            "sources": ["BKM Public Register", "DHM Annual Report", "Kununu Reviews"],
            "curatorial_focus": "German history in European context, Zeughaus baroque armoury, I.M. Pei exhibition hall",
            "admission_policy": "Paid / Free for Under 18",
            "admission_details": "Standard admission ticket; free entry for youth under 18.",
            "ethical_safeguard": "Federal foundation statutes and academic advisory board.",
            "year_founded": 1987,
            "transparency_grade": "B+",
            "curator_recommendation": "Germany's national historical museum housed in Berlin's oldest preserved Baroque structure and I.M. Pei's luminous wing.",
            "id": "deutsches-historisches-museum-berlin"
        },
        {
            "name": "Bourse de Commerce – Pinault Collection",
            "city": "Paris",
            "country": "France",
            "location": "Paris, France",
            "lat": 48.8628,
            "lon": 2.3429,
            "tier": "B",
            "tier_label": "Flagged",
            "size": "Large",
            "governance_type": "Private Corporate Collection",
            "governance_classification": "Corporate Foundation (Kering / François Pinault)",
            "website": "https://www.pinaultcollection.com/fr/boursedecommerce",
            "funding": "Financière Pinault / Artémis private equity and luxury conglomerate capital.",
            "watch": "Private luxury conglomerate foundation; employee accounts regarding turnover and contractor transitions.",
            "sources": ["Pinault Collection Disclosures", "City of Paris 50-year lease", "Glassdoor Reviews"],
            "curatorial_focus": "Contemporary Pinault Collection, Tadao Ando concrete cylinder, rotunda dome, post-war sculpture",
            "admission_policy": "Paid / Free First Saturday Evening",
            "admission_details": "Standard timed ticket; free admission on the first Saturday of each month from 17:00 to 21:00.",
            "ethical_safeguard": "Regulated under 50-year municipal lease with the City of Paris.",
            "year_founded": 2021,
            "transparency_grade": "B",
            "curator_recommendation": "Tadao Ando's dramatic intervention within the historic circular grain exchange displaying the Pinault contemporary collection.",
            "id": "bourse-de-commerce-paris"
        },
        {
            "name": "Grand Palais (Rmn–Grand Palais)",
            "city": "Paris",
            "country": "France",
            "location": "Paris, France",
            "lat": 48.8661,
            "lon": 2.3125,
            "tier": "B",
            "tier_label": "Flagged",
            "size": "Large",
            "governance_type": "Public Cultural Establishment (Rmn-GP)",
            "governance_classification": "Établissement Public Culturel",
            "website": "https://www.grandpalais.fr",
            "funding": "French Ministry of Culture, commercial exhibition production, Olympic renovations, patron underwriting.",
            "watch": "Multi-site French museum organisation; employee reviews regarding restructuring and cafeteria/remote working conditions.",
            "sources": ["Ministère de la Culture", "Rmn-Grand Palais Rapport Annuel", "Glassdoor Reviews"],
            "curatorial_focus": "Universal exhibition palace, monumental nave, contemporary international art fairs (Art Basel Paris), historical retrospectives",
            "admission_policy": "Paid / Subsidised National Passes",
            "admission_details": "Ticketed admission depending on current temporary exhibition and fair.",
            "ethical_safeguard": "National public cultural establishment statutory oversight.",
            "year_founded": 1900,
            "transparency_grade": "B+",
            "curator_recommendation": "Beaux-Arts glass and iron exhibition palace featuring Europe's largest historic glass roof.",
            "id": "grand-palais-paris"
        },
        {
            "name": "Deutsches Spionagemuseum",
            "city": "Berlin",
            "country": "Germany",
            "location": "Berlin, Germany",
            "lat": 52.5103,
            "lon": 13.3794,
            "tier": "B",
            "tier_label": "Flagged",
            "size": "Medium",
            "governance_type": "Private Commercial Museum",
            "governance_classification": "Private Museum (GmbH)",
            "website": "https://www.deutsches-spionagemuseum.de",
            "funding": "Private commercial museum funded exclusively by ticket sales and retail; no public subsidies.",
            "watch": "Private commercial espionage exhibition; employee reviews requesting fixed hours and higher guide pay.",
            "sources": ["Handelsregister Berlin", "Kununu Reviews", "TripAdvisor Records"],
            "curatorial_focus": "History of espionage, Cold War Berlin surveillance, cryptography, Enigma machines, interactive laser maze",
            "admission_policy": "Commercial Timed Ticket",
            "admission_details": "Standard commercial ticket required for entry.",
            "ethical_safeguard": "Private enterprise operating under German commercial law.",
            "year_founded": 2015,
            "transparency_grade": "C+",
            "curator_recommendation": "High-tech interactive museum of global espionage and Cold War covert operations on Leipziger Platz.",
            "id": "deutsches-spionagemuseum-berlin"
        },
        {
            "name": "Stiftung Stadtmuseum Berlin",
            "city": "Berlin",
            "country": "Germany",
            "location": "Berlin, Germany",
            "lat": 52.5165,
            "lon": 13.4074,
            "tier": "B",
            "tier_label": "Flagged",
            "size": "Large",
            "governance_type": "Public Law Foundation (Land Berlin)",
            "governance_classification": "Landesstiftung Öffentlichen Rechts",
            "website": "https://www.stadtmuseum.de",
            "funding": "Senatsverwaltung für Kultur und Gesellschaftlichen Zusammenhalt Berlin funding across Märkisches Museum, Nikolaikirche, and Ephraim-Palais.",
            "watch": "Regional museum network for Berlin history; employee accounts regarding management and progression.",
            "sources": ["Land Berlin Cultural Budget", "Stadtmuseum Berlin Jahresbericht", "Kununu Reviews"],
            "curatorial_focus": "Berlin culture, urban history, Märkisches Museum collections, Nikolaiviertel architecture",
            "admission_policy": "Paid / Free First Sunday of the Month",
            "admission_details": "Free entry on Museumssonntag.",
            "ethical_safeguard": "Public foundation oversight under the Berlin state parliament.",
            "year_founded": 1995,
            "transparency_grade": "B+",
            "curator_recommendation": "State foundation preserving Berlin's rich material culture, architecture, and civic memory.",
            "id": "stiftung-stadtmuseum-berlin"
        },
        {
            "name": "DDR Museum Berlin",
            "city": "Berlin",
            "country": "Germany",
            "location": "Berlin, Germany",
            "lat": 52.5194,
            "lon": 13.4027,
            "tier": "B",
            "tier_label": "Flagged",
            "size": "Medium",
            "governance_type": "Private Interactive Museum",
            "governance_classification": "Private Enterprise",
            "website": "https://www.ddr-museum.de",
            "funding": "Private museum financed through admissions; rebuilt following 2022 AquaDom flood.",
            "watch": "Workplace reviews regarding management, employee support, and safety.",
            "sources": ["Handelsregister", "Kununu Reviews", "Museum Association of Berlin"],
            "curatorial_focus": "Everyday life in East Germany, Stasi surveillance, Trabant driving simulator, Plattenbau apartment",
            "admission_policy": "Commercial Admission Ticket",
            "admission_details": "Paid timed entry ticket.",
            "ethical_safeguard": "Private museum operator subject to German workplace regulations.",
            "year_founded": 2006,
            "transparency_grade": "B",
            "curator_recommendation": "Hands-on interactive immersion into daily life, domestic culture, and surveillance in former East Germany.",
            "id": "ddr-museum-berlin"
        },
        {
            "name": "Paris Musées (Réseau des Musées de la Ville de Paris)",
            "city": "Paris",
            "country": "France",
            "location": "Paris, France",
            "lat": 48.8553,
            "lon": 2.3602,
            "tier": "B",
            "tier_label": "Flagged",
            "size": "Large",
            "governance_type": "Public Municipal Establishment",
            "governance_classification": "Établissement Public de la Ville de Paris",
            "website": "https://www.parismusees.paris.fr",
            "funding": "City of Paris municipal budget covering 14 city museums (Carnavalet, MAM, Petit Palais, Catacombes, etc.).",
            "watch": "City museum network; employee reviews alleging management disorganisation and workload pressures.",
            "sources": ["Ville de Paris", "Paris Musées Rapport d'Activité", "Glassdoor Reviews"],
            "curatorial_focus": "Municipal collections of the City of Paris, modern art, Parisian history, literary houses, catacombs",
            "admission_policy": "Always Free Permanent Collections / Ticketed Temporary Exhibitions",
            "admission_details": "Universal free admission to permanent collections of all 14 municipal museums.",
            "ethical_safeguard": "City of Paris democratic municipal oversight.",
            "year_founded": 2013,
            "transparency_grade": "A-",
            "curator_recommendation": "The extraordinary network of 14 municipal museums of the City of Paris offering free access to permanent treasures.",
            "id": "paris-musees-reseau"
        }
    ]

    added_count = 0
    for ni in new_institutions:
        if ni["id"] not in inst_by_id and ni["name"].lower() not in inst_by_name:
            # Set default architecture and empty gossip data
            ni["audit_dossier_url"] = f"#{ni['id']}-audit"
            ni["statutory_filings_url"] = f"https://www.google.com/search?q={ni['name'].replace(' ', '+')}+annual+report"
            ni["gossip_data"] = {
                "has_gossip": True,
                "intensity": "ACTIVE",
                "rumor_score": 75,
                "headline": f"{ni['name']}: Governance audits, workplace reviews, and institutional transparency.",
                "tag": "#InstitutionalAudit",
                "real_cases": [],
                "review_leads": []
            }
            institutions.append(ni)
            inst_by_id[ni["id"]] = ni
            inst_by_name[ni["name"].lower().strip()] = ni
            added_count += 1
            print(f"  + Added new institution: {ni['name']} ({ni['city']})")

    print(f"✅ Added {added_count} missing institutions. Total institutions in catalog: {len(institutions)}.")

    # Re-index institutions
    inst_by_id = {i["id"]: i for i in institutions}
    inst_by_name = {i["name"].lower().strip(): i for i in institutions}

    # Helper matching function
    def find_institution_for(raw_name, city=None):
        r_low = raw_name.lower().strip()
        # Direct key lookup
        if r_low in inst_by_name:
            return inst_by_name[r_low]
        # Specific aliases mapping
        alias_map = {
            "v&a": "va-london",
            "the noguchi museum": "noguchi-museum",
            "noguchi museum": "noguchi-museum",
            "musée du louvre": "louvre-paris",
            "louvre": "louvre-paris",
            "moma": "moma-the-museum-of-modern-art",
            "museum of modern art (moma)": "moma-the-museum-of-modern-art",
            "moma (the museum of modern art)": "moma-the-museum-of-modern-art",
            "the metropolitan museum of art (the met)": "the-metropolitan-museum-of-art-the-met",
            "metropolitan museum of art": "the-metropolitan-museum-of-art-the-met",
            "tate": "tate-modern",
            "the national gallery": "national-gallery",
            "national gallery": "national-gallery",
            "staatliche museen zu berlin / preußischer kulturbesitz": "staatliche-museen-zu-berlin",
            "kw institute for contemporary art – kunst-werke berlin e. v.": "kw-institute-for-contemporary-art",
            "kw institute for contemporary art": "kw-institute-for-contemporary-art",
            "science museum group": "science-museum-london",
            "science museum": "science-museum-london",
            "london museum": "london-museum",
            "american folk art museum": "american-folk-art-museum",
            "neue nationalgalerie": "neue-nationalgalerie-berlin",
            "hamburger bahnhof": "hamburger-bahnhof-berlin",
            "hamburger bahnhof – nationalgalerie der gegenwart": "hamburger-bahnhof-berlin",
            "oyoun": "oyoun-berlin",
            "het concertgebouw": "het-concertgebouw-amsterdam",
            "casa de la arquitectura": "casa-de-la-arquitectura-madrid",
            "caixaforum madrid": "caixaforum-madrid",
            "museo nacional del prado": "museo-nacional-del-prado",
            "museo nacional thyssen-bornemisza": "museo-thyssen-bornemisza",
            "teatro real": "teatro-real-madrid",
            "barbican centre": "barbican-centre-london",
            "royal academy of arts": "royal-academy-of-arts-london",
            "institute of contemporary arts": "ica-london",
            "new museum of contemporary art": "new-museum-new-york",
            "brooklyn academy of music": "bam-new-york",
            "musée d'orsay": "mus-e-d-orsay",
            "bourse de commerce – pinault collection": "bourse-de-commerce-paris",
            "berlinische galerie": "berlinische-galerie",
            "museum für naturkunde": "museum-fuer-naturkunde-berlin",
            "jüdisches museum berlin": "juedisches-museum-berlin",
            "humboldt forum": "humboldt-forum-berlin",
            "deutsches historisches museum": "deutsches-historisches-museum-berlin",
            "stedelijk museum amsterdam": "stedelijk-museum-amsterdam",
            "museo reina sofía": "museo-reina-sof-a",
            "bak, basis voor actuele kunst": "bak-utrecht",
            "solomon r. guggenheim museum": "solomon-r-guggenheim-museum",
            "brooklyn museum": "brooklyn-museum-new-york",
            "whitney museum of american art": "whitney-museum-of-american-art",
            "centre pompidou": "centre-pompidou",
            "palais de Tokyo": "palais-de-tokyo",
            "palais de tokyo": "palais-de-tokyo",
            "rijksmuseum": "rijksmuseum-amsterdam",
            "van gogh museum": "van-gogh-museum-amsterdam",
            "serpentine galleries": "serpentine-galleries"
        }
        if r_low in alias_map:
            target_id = alias_map[r_low]
            if target_id in inst_by_id:
                return inst_by_id[target_id]
        
        # Fuzzy match
        for name, inst in inst_by_name.items():
            if r_low == name or (len(r_low) > 4 and r_low in name) or (len(name) > 4 and name in r_low):
                if not city or (inst.get("city") and city.lower() in inst["city"].lower()):
                    return inst
        return None

    print("\n--- 3. ATTACHING REAL RESEARCH CASES TO INSTITUTIONS ---")
    attached_cases = 0
    for case in gossip_data.get("cases", []):
        raw_name = case["institution"]["name"]
        city = case["institution"].get("city")
        inst = find_institution_for(raw_name, city)
        if not inst:
            print(f"  ⚠️ Warning: Could not match case {case['id']} for {raw_name}")
            continue

        if "gossip_data" not in inst or not isinstance(inst["gossip_data"], dict):
            inst["gossip_data"] = {}
        
        g = inst["gossip_data"]
        g["has_gossip"] = True
        if "real_cases" not in g:
            g["real_cases"] = []

        # Resolve sources with titles and URLs
        resolved_sources = []
        all_sids = set()
        for f in case.get("facts", []):
            all_sids.update(f.get("source_ids", []))
        for c in case.get("attributed_claims", []):
            all_sids.update(c.get("source_ids", []))
        if case.get("response"):
            all_sids.update(case["response"].get("source_ids", []))
        if case.get("outcome"):
            all_sids.update(case["outcome"].get("source_ids", []))
            
        for sid in sorted(all_sids):
            if sid in sources_map:
                s = sources_map[sid]
                resolved_sources.append({
                    "id": sid,
                    "title": s.get("title", sid),
                    "url": s.get("url", ""),
                    "publisher": s.get("publisher", ""),
                    "published": s.get("published", "")
                })

        enriched_case = {
            "case_id": case["id"],
            "title": case["title"],
            "topics": case.get("topics", []),
            "event_date": case.get("event_date", ""),
            "status": case.get("status", ""),
            "latest_source_date": case.get("latest_source_date", ""),
            "facts": [f.get("text", "") for f in case.get("facts", [])],
            "claims": [c.get("text", "") for c in case.get("attributed_claims", [])],
            "response": case.get("response", {}).get("text", "") if case.get("response") else "",
            "outcome": case.get("outcome", {}).get("text", "") if case.get("outcome") else "",
            "limits": case.get("limits", []),
            "follow_up": case.get("follow_up", ""),
            "sources": resolved_sources
        }

        # Avoid duplicate case id
        if not any(c.get("case_id") == case["id"] for c in g["real_cases"]):
            g["real_cases"].append(enriched_case)
            attached_cases += 1

        # Elevate headline and metadata
        g["intensity"] = "HOT" if "strike" in case["title"].lower() or "bp" in case["title"].lower() or "dispute" in case["title"].lower() else "ACTIVE"
        g["headline"] = f"{inst['name']}: {case['title']}"
        topic_tag = case.get("topics", ["Governance"])[0].capitalize()
        g["tag"] = f"#{topic_tag}Audit"

        # Update reddit snippet with real facts
        if enriched_case["facts"]:
            g["reddit"] = {
                "subreddit": "r/contemporaryart",
                "snippet": f"Documented case {case['id']}: {enriched_case['facts'][0]} Outcome: {enriched_case['outcome']}"
            }
        if enriched_case["claims"]:
            g["twitter_x"] = {
                "handle": "@culture_watch",
                "snippet": f"Public claim: {enriched_case['claims'][0]} Latest evidence ({enriched_case['latest_source_date']}): {enriched_case['outcome']}"
            }

    print(f"✅ Successfully attached {attached_cases} investigation cases across institutions.")

    print("\n--- 4. ATTACHING VERIFIED REVIEW LEADS TO INSTITUTIONS ---")
    attached_reviews = 0
    for rlead in gossip_data.get("review_leads", []):
        raw_name = rlead.get("institution", {}).get("name") if rlead.get("institution") else None
        city = rlead.get("institution", {}).get("city") if rlead.get("institution") else None
        eid = rlead.get("employer_entity_id")

        target_insts = []
        if eid == "E17":  # Magmacultura
            target_insts = [find_institution_for("Casa de la Arquitectura"), find_institution_for("CaixaForum Madrid")]
        elif eid == "E42":  # KBB
            target_insts = [find_institution_for("Gropius Bau"), find_institution_for("Haus der Kulturen der Welt (HKW)")]
        elif eid == "E37":  # Rmn–Grand Palais
            target_insts = [find_institution_for("Grand Palais (Rmn–Grand Palais)")]
        elif eid == "E38":  # Paris Musées
            target_insts = [find_institution_for("Paris Musées (Réseau des Musées de la Ville de Paris)")]
        elif eid == "E20":  # Deutsches Spionagemuseum
            target_insts = [find_institution_for("Deutsches Spionagemuseum")]
        elif eid == "E22":  # Stiftung Stadtmuseum Berlin
            target_insts = [find_institution_for("Stiftung Stadtmuseum Berlin")]
        elif eid == "E24":  # DDR Museum Berlin
            target_insts = [find_institution_for("DDR Museum Berlin")]
        elif raw_name:
            single = find_institution_for(raw_name, city)
            if single:
                target_insts = [single]

        target_insts = [t for t in target_insts if t]
        if not target_insts:
            print(f"  ⚠️ Review lead {rlead['id']} unmapped: {raw_name} ({city}) eid={eid}")
            continue

        for inst in target_insts:
            if "gossip_data" not in inst or not isinstance(inst["gossip_data"], dict):
                inst["gossip_data"] = {}
            g = inst["gossip_data"]
            g["has_gossip"] = True
            if "review_leads" not in g:
                g["review_leads"] = []

        # Find source
        src_url = ""
        src_id = rlead.get("source_ids", [""])[0] if rlead.get("source_ids") else ""
        if src_id and src_id in sources_map:
            src_url = sources_map[src_id].get("url", "")

        review_entry = {
            "lead_id": rlead["id"],
            "platform": rlead.get("platform", "Review"),
            "role": rlead.get("reviewer", {}).get("role", "Staff"),
            "review_date": rlead.get("review_date", ""),
            "summary": rlead.get("summary", ""),
            "positive_themes": rlead.get("positive_themes", []),
            "concern_themes": rlead.get("concern_themes", []),
            "limits": rlead.get("limits", []),
            "source_id": src_id,
            "source_url": src_url,
            "historical": rlead.get("historical_experience", False)
        }

        if not any(r.get("lead_id") == rlead["id"] for r in g["review_leads"]):
            g["review_leads"].append(review_entry)
            attached_reviews += 1

    print(f"✅ Successfully attached {attached_reviews} employee/visitor review leads across institutions.")

    # Save updated institutions.json
    with open("institutions.json", "w", encoding="utf-8") as f:
        json.dump(institutions, f, indent=2, ensure_ascii=False)
    print("🎉 institutions.json saved with enriched research, cases, and reviews!")

if __name__ == "__main__":
    run_integration()
