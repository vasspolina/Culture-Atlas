import json

URL_REFINEMENTS = {
    "Ordrupgaard": {
        "website": "https://museumordrupgaard.dk/",
        "visit_url": "https://museumordrupgaard.dk/en/visit-ordrupgaard/"
    },
    "Museu Lasar Segall": {
        "website": "https://www.gov.br/museusegall/pt-br",
        "visit_url": "https://www.gov.br/museusegall/pt-br"
    },
    "Museo La Tertulia": {
        "website": "https://museolatertulia.com/",
        "visit_url": "https://museolatertulia.com/"
    },
    "National Gallery of Jamaica": {
        "website": "https://nationalgalleryofjamaica.wordpress.com/",
        "visit_url": "https://nationalgalleryofjamaica.wordpress.com/"
    },
    "Musée des Civilisations Noires": {
        "website": "http://mcn.sn/",
        "visit_url": "http://mcn.sn/"
    },
    "OCAT Shenzhen": {
        "website": "https://www.octloft.cn/",
        "visit_url": "https://www.octloft.cn/"
    },
    "Staatliche Museen zu Berlin": {
        "website": "https://www.smb.museum/home/",
        "visit_url": "https://www.smb.museum/besuch-planen/"
    },
    "Kunstmuseum Bern": {
        "website": "https://www.kunstmuseumbern.ch/de",
        "visit_url": "https://www.kunstmuseumbern.ch/de/besuch-planen-18.html"
    },
    "MAIIAM": {
        "website": "https://maiiam.com/en",
        "visit_url": "https://maiiam.com/en/visit/"
    },
    "Walker Art Center": {
        "website": "https://www.walkerart.org/",
        "visit_url": "https://www.walkerart.org/visit"
    },
    "SITE Santa Fe": {
        "website": "https://www.sitesantafe.org/en/",
        "visit_url": "https://www.sitesantafe.org/en/visit/"
    },
    "Kunstinstituut Melly": {
        "website": "https://www.kunstinstituutmelly.nl/en/",
        "visit_url": "https://www.kunstinstituutmelly.nl/en/visit"
    },
    "Neuer Berliner Kunstverein (n.b.k.)": {
        "website": "https://www.nbk.org/de",
        "visit_url": "https://www.nbk.org/de/information/besuch"
    },
    "Fondazione Antonio Ratti": {
        "website": "https://fondazioneratti.org/",
        "visit_url": "https://fondazioneratti.org/"
    },
    "Triple Canopy": {
        "website": "https://canopycanopycanopy.com/",
        "visit_url": "https://canopycanopycanopy.com/"
    },
    "Holburne Museum": {
        "website": "https://holburne.org/",
        "visit_url": "https://holburne.org/visit/"
    },
    "Scottsdale Museum of Contemporary Art": {
        "website": "https://scottsdalearts.org/explore-scottsdale-arts/smoca/",
        "visit_url": "https://scottsdalearts.org/explore-scottsdale-arts/smoca/"
    }
}

with open('institutions.json', 'r', encoding='utf-8') as f:
    institutions = json.load(f)

count = 0
for inst in institutions:
    name = inst.get('name')
    if name in URL_REFINEMENTS:
        patch = URL_REFINEMENTS[name]
        for k, v in patch.items():
            inst[k] = v
        count += 1

print(f"Applied final refinements to {count} institutions.")

with open('institutions.json', 'w', encoding='utf-8') as f:
    json.dump(institutions, f, indent=2, ensure_ascii=False)

print("Saved updated institutions.json")
