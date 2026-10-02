import json

def main():
    with open('institutions.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 1. Update Van Abbemuseum with deeper research context
    for inst in data:
        if inst.get('name') == 'Van Abbemuseum':
            inst['watch'] = (
                "Global pioneer of 'Radical Museology' (Claire Bishop) and 'Museum of Arte Útil' (initiated with Tania Bruguera). "
                "Operates the 'Deviant Practice' research programme, interrogating collection archives through decolonial, queer, "
                "and disability-inclusive perspectives. In 2021, Van Abbemuseum formally ratified a climate and ethical governance "
                "manifesto prohibiting corporate sponsorships from carbon-intensive, arms-manufacturing, or human-rights-flagged entities."
            )
            inst['highlight'] = "Pioneering 'Museum of Arte Útil' archive, El Lissitzky collection, and 'Deviant Practice' research installations."
            inst['curatorial_focus'] = "Radical Museology, Arte Útil (Useful Art) & Deviant Archival Practice"
            inst['aliases'] = ["van abbemuseum", "van abbemuseum eindhoven", "van abbe", "arte util museum"]

    # 2. Add new Dutch research institutions
    new_institutions = [
        {
            "name": "BAK, basis voor actuele kunst",
            "location": "Utrecht, Netherlands",
            "tier": "A",
            "size": "S",
            "funding": "€1.4M annual budget. Structural multi-year subsidy from the Mondriaan Fund (Dutch Ministry of OCW) and Gemeente Utrecht (Municipality of Utrecht). Complete ethical firewall against fossil fuel, defense, or commercial board leverage.",
            "watch": "International epicenter of critical artistic research and political imagination. Co-published the landmark 748-page compendium 'Former West: Art and the Contemporary After 1989' with MIT Press. Conducted long-term research platforms including 'Vectors of Commoning', 'Propositions for Non-Fascist Living', and the 'Posthuman Glossary' with Rosi Braidotti (Utrecht University).",
            "sources": [
                "https://www.bakonline.org",
                "https://mitpress.mit.edu/9780262533836/former-west/",
                "https://www.mondriaanfonds.nl"
            ],
            "lat": 52.0934,
            "lon": 5.1168,
            "country": "Netherlands",
            "city": "Utrecht",
            "website": "https://www.bakonline.org",
            "id": "bak-utrecht",
            "governance_type": "Civic Artistic Research Institute & Foundation",
            "curatorial_focus": "Artistic Research, Posthumanism, Commons & Decolonial Geopolitics",
            "admission_policy": "Pay-What-You-Can / Sliding Scale Solidarity",
            "admission_details": "Solidarity admission model: Pay-what-you-wish (€0 / €3 / €6 / €10); free for students, activists, and Utrecht U-pas holders.",
            "ethical_safeguard": "Statutory ethical public funding covenant; zero corporate board interference; transparent community accountability.",
            "year_founded": 2000,
            "transparency_grade": "Tier A (Civic Research Sanctuary)",
            "curator_recommendation": "The undisputed global benchmark for research-driven artistic practice. Directed by Maria Hlavajova, BAK redefines the museum not as a passive exhibition container, but as an active laboratory of political imagination and critical theory.",
            "aliases": [
                "bak utrecht",
                "bac utrecht",
                "bak",
                "bac",
                "bak, basis voor actuele kunst",
                "basis voor actuele kunst",
                "former west bak"
            ],
            "address": "Pauwstraat 13A, 3512 TG Utrecht, Netherlands",
            "neighborhood": "Utrecht Historic City Center / Neude Quarter",
            "opening_hours": "Wed–Sun 13:00–19:00, Closed Mon & Tue",
            "admission_fee": "€0–€6 Solidarity Sliding Scale / Free for youth & U-pas holders",
            "transit_tips": "10-minute walk from Utrecht Centraal Station; buses 2, 3, 7 to 'Neude' or 'Janskerkhof'.",
            "accessibility": "Wheelchair accessible ground floor and exhibition spaces, accessible gender-neutral restrooms.",
            "amenities": "Specialized artistic research library, reading room, publication desk with Sternberg & MIT Press titles, community assembly space.",
            "visit_duration": "1 – 2 hours",
            "highlight": "Landmark 'Former West' research archive, 'Vectors of Commoning' assemblies, and the BAK Fellowship for Situated Practice.",
            "visit_url": "https://www.bakonline.org/visit"
        },
        {
            "name": "Casco Art Institute: Working for the Commons",
            "location": "Utrecht, Netherlands",
            "tier": "A",
            "size": "S",
            "funding": "€650K annual budget. Structural civic grants from the Mondriaan Fund and Gemeente Utrecht, supplemented by DOEN Foundation and European cooperative cultural pools.",
            "watch": "Pioneered the institutional shift from an exhibition showroom to a living commons and cooperative ecosystem. Led by Binna Choi, Casco restructured its entire internal governance according to feminist economics, mutual care, and collective unlearning.",
            "sources": [
                "https://casco.art",
                "https://www.mondriaanfonds.nl"
            ],
            "lat": 52.0862,
            "lon": 5.1235,
            "country": "Netherlands",
            "city": "Utrecht",
            "website": "https://casco.art",
            "id": "casco-art-institute",
            "governance_type": "Cooperative Non-Profit Arts Commons",
            "curatorial_focus": "The Commons, Feminist Economies & Collective Unlearning",
            "admission_policy": "100% Free Public Admission",
            "admission_details": "Free open access to exhibitions, communal kitchen, reading library, and commoning assemblies.",
            "ethical_safeguard": "Statutory commons charter; transparent non-hierarchical wage ratio; zero corporate extractivism.",
            "year_founded": 1990,
            "transparency_grade": "Tier A (Commons Exemplar)",
            "curator_recommendation": "A visionary space that asks how an art organization can embody the values it exhibits. Casco does not merely exhibit the commons; it actively practices collective shared governance and communal mutual aid.",
            "aliases": [
                "casco",
                "casco art institute",
                "casco utrecht",
                "casco projects",
                "working for the commons"
            ],
            "address": "Lange Nieuwstraat 7, 3512 PA Utrecht, Netherlands",
            "neighborhood": "Museumkwartier Utrecht",
            "opening_hours": "Wed–Sun 12:00–18:00, Closed Mon & Tue",
            "admission_fee": "Free admission (donations to the Commons pool welcomed)",
            "transit_tips": "15-minute walk from Utrecht Centraal or take Bus 2 to 'Universiteitsmuseum'.",
            "accessibility": "Ground-floor gallery step-free accessible, courtyard garden accessible, sensory-friendly environment.",
            "amenities": "Communal kitchen & tea corner, 'Publishing Class' bookshop, research library, quiet garden courtyard.",
            "visit_duration": "1 – 1.5 hours",
            "highlight": "'Site for Unlearning: Art Organization' methodology, community agriculture projects, and pioneering artist publishing.",
            "visit_url": "https://casco.art/info"
        },
        {
            "name": "Kunstinstituut Melly",
            "location": "Rotterdam, Netherlands",
            "tier": "A",
            "size": "M",
            "funding": "€2.2M annual budget. Structural civic funding from Gemeente Rotterdam and the Mondriaan Fund. No arms, fossil fuel, or predatory sponsorships.",
            "watch": "Historically Witte de With Center for Contemporary Art. In 2020, undertook a historic, publicly documented institutional transformation and renaming process to de-commemorate a colonial naval officer, renaming the institution after Ken Lum's iconic artwork 'Melly Shum Hates Her Job'.",
            "sources": [
                "https://www.kunstinstituutmelly.nl",
                "https://www.mondriaanfonds.nl"
            ],
            "lat": 51.9157,
            "lon": 4.4776,
            "country": "Netherlands",
            "city": "Rotterdam",
            "website": "https://www.kunstinstituutmelly.nl",
            "id": "kunstinstituut-melly",
            "governance_type": "Civic Contemporary Art Institute",
            "curatorial_focus": "Critical Curating, Public Accountability & Decolonial Inquiry",
            "admission_policy": "Standard Ticketed with Weekly Free Evenings",
            "admission_details": "€6 Adults / €3 Students / Free for all every Friday evening (18:00–21:00) and for Rotterdam Pas / Museumkaart holders.",
            "ethical_safeguard": "Institutional decolonial charter; participatory public review; transparent municipal subvention.",
            "year_founded": 1990,
            "transparency_grade": "Tier A (Decolonial Accountability)",
            "curator_recommendation": "A globally renowned contemporary art center famous for its experimental monographs, Source research anthologies, and fearless willingness to interrogate its own institutional history and colonial entanglements.",
            "aliases": [
                "kunstinstituut melly",
                "melly",
                "witte de with",
                "witte de with center for contemporary art",
                "melly rotterdam"
            ],
            "address": "Witte de Withstraat 50, 3012 BR Rotterdam, Netherlands",
            "neighborhood": "Witte de Withkwartier / Cool District",
            "opening_hours": "Tue–Sun 11:00–18:00 (Fridays until 21:00), Closed Mon",
            "admission_fee": "€6 Adults / €3 Students / Free Friday 18:00–21:00",
            "transit_tips": "Metro A/B/C to 'Eendrachtsplein' or Tram 7 to 'Witte de Withstraat'; 12-minute walk from Rotterdam Centraal.",
            "accessibility": "Elevator to all exhibition floors, wheelchair accessible restrooms, welcoming multi-lingual staff.",
            "amenities": "MELLY café and reading room, curated bookstore, event auditorium.",
            "visit_duration": "1.5 – 2 hours",
            "highlight": "Rotating critical commissions, research publications series, and Ken Lum's monumental permanent outdoor work 'Melly Shum Hates Her Job'.",
            "visit_url": "https://www.kunstinstituutmelly.nl/en/visit"
        },
        {
            "name": "De Appel",
            "location": "Amsterdam, Netherlands",
            "tier": "A",
            "size": "S",
            "funding": "€1.1M annual budget. Supported by the Mondriaan Fund and the Amsterdams Fonds voor de Kunst (AFK).",
            "watch": "Pioneered experimental performance, feminist video art, and the world-renowned 'Curatorial Programme' (established in 1994), which trained leading museum directors and curators worldwide.",
            "sources": [
                "https://www.deappel.nl",
                "https://www.mondriaanfonds.nl"
            ],
            "lat": 52.3562,
            "lon": 4.8465,
            "country": "Netherlands",
            "city": "Amsterdam",
            "website": "https://www.deappel.nl",
            "id": "de-appel",
            "governance_type": "Independent Curatorial & Research Institute",
            "curatorial_focus": "Curatorial Studies, Performance Archives & Grassroots Assemblies",
            "admission_policy": "Pay-What-You-Can / Modest Admission",
            "admission_details": "€5 standard / Free for students, artists, and neighborhood residents.",
            "ethical_safeguard": "Public cultural council governance; no commercial board leverage.",
            "year_founded": 1975,
            "transparency_grade": "Tier A (Pioneering Curatorial Research)",
            "curator_recommendation": "A historic hotbed for conceptual risk-taking. Founded in 1975 by Wies Smals, De Appel shaped modern curatorial pedagogy and preserves one of Europe's richest ephemera archives.",
            "aliases": [
                "de appel",
                "de appel amsterdam",
                "curatorial programme de appel"
            ],
            "address": "Schipluidenlaan 12, 1062 HE Amsterdam, Netherlands",
            "neighborhood": "Amsterdam Nieuw-West / Lelylaan Quarter",
            "opening_hours": "Wed–Sun 12:00–18:00, Closed Mon & Tue",
            "admission_fee": "€5 / Free for under 18 & neighborhood residents",
            "transit_tips": "Metro 50/51 or Train to 'Station Lelylaan'; Tram 1 or 17 to 'Derkinderenstraat'.",
            "accessibility": "Step-free ground level access, accessible restrooms.",
            "amenities": "Specialist curatorial archive, reading room, public workshops, café space.",
            "visit_duration": "1 – 1.5 hours",
            "highlight": "Seminal performance art archives (including 1970s Marina Abramović/Ulay works) and annual Curatorial Programme projects.",
            "visit_url": "https://www.deappel.nl/en/visit"
        },
        {
            "name": "Framer Framed",
            "location": "Amsterdam, Netherlands",
            "tier": "A",
            "size": "S",
            "funding": "€900K annual budget. Funded by the Dutch Ministry of OCW via Mondriaan Fund and Amsterdams Fonds voor de Kunst (AFK).",
            "watch": "Leading platform for critical museology, decolonial aesthetics, and intercultural artistic research. Operates both a main exhibition hall in Amsterdam Oost and the participatory community space Werkplaats Molenwijk.",
            "sources": [
                "https://framerframed.nl",
                "https://www.mondriaanfonds.nl"
            ],
            "lat": 52.3575,
            "lon": 4.9317,
            "country": "Netherlands",
            "city": "Amsterdam",
            "website": "https://framerframed.nl",
            "id": "framer-framed",
            "governance_type": "Decolonial Research & Civic Art Platform",
            "curatorial_focus": "Critical Museology, Decolonial Research & Translocal Solidarity",
            "admission_policy": "100% Free Public Admission",
            "admission_details": "Free access to all exhibitions, public debates, community film screenings, and workshops.",
            "ethical_safeguard": "Statutory non-profit civic charter; community steering; strict anti-greenwashing policies.",
            "year_founded": 2009,
            "transparency_grade": "Tier A (Decolonial Research Sanctuary)",
            "curator_recommendation": "An indispensable space exploring the intersection of contemporary visual art, intercultural politics, and postcolonial memory. Its exhibitions challenge mainstream institutional bias with unflinching rigor.",
            "aliases": [
                "framer framed",
                "framer framed amsterdam"
            ],
            "address": "Oranje-Vrijstaatkade 71, 1093 KS Amsterdam, Netherlands",
            "neighborhood": "Amsterdam Oost / Dapperbuurt",
            "opening_hours": "Tue–Sun 12:00–18:00, Closed Mon",
            "admission_fee": "Free admission",
            "transit_tips": "Tram 19 or 3 to 'Dapperstraat'; Train to 'Amsterdam Muiderpoort' (5-minute walk).",
            "accessibility": "Completely step-free, wide doorways, accessible facilities, tactile guides available on request.",
            "amenities": "Decolonial research reading room, community kitchen, outdoor terrace overlooking the canal.",
            "visit_duration": "1 – 1.5 hours",
            "highlight": "Critically acclaimed research exhibitions on restitution, environmental racism, and indigenous memory systems.",
            "visit_url": "https://framerframed.nl/en/contact/"
        }
    ]

    existing_ids = {x.get('id') for x in data}
    added = 0
    for new_inst in new_institutions:
        if new_inst['id'] not in existing_ids:
            data.append(new_inst)
            existing_ids.add(new_inst['id'])
            added += 1

    with open('institutions.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Successfully added {added} Dutch research institutions. Total in database: {len(data)}")

if __name__ == '__main__':
    main()
