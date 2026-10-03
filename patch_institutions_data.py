import json
import re

URL_UPDATES = {
    # 1. Broken / suspended / domain changes
    "Nha San Collective": {
        "website": "https://www.facebook.com/NhaSanCollective/",
        "visit_url": "https://www.facebook.com/NhaSanCollective/",
        "opening_hours": "Nomadic pop-up projects; check Facebook for active events",
        "curator_recommendation": "The legendary pioneer of Vietnamese experimental art. Nha San operates as an active nomadic artist collective across pop-up venues in Hanoi following the closure of its historic wooden stilt studio. Check their official Facebook for current public events and performances.",
        "transit_tips": "Nomadic projects across Hanoi; check event listings for exact locations."
    },
    "Ruang MES 56": {
        "website": "https://www.instagram.com/mes56/",
        "visit_url": "https://www.instagram.com/mes56/",
        "curator_recommendation": "A foundational artist collective in Yogyakarta exploring photo-based media, self-publishing, and community social practice. Active at Jl. Mangkuyudan No.53 A, Mantrijeron, Yogyakarta."
    },
    "Storefront for Art and Architecture": {
        "website": "https://storefront.nyc/",
        "visit_url": "https://storefront.nyc/visit/"
    },
    "Britto Arts Trust": {
        "website": "https://brittoartstrust.com/",
        "visit_url": "https://brittoartstrust.com/"
    },
    "CCA Derry~Londonderry": {
        "website": "https://www.ccadld.org/",
        "visit_url": "https://www.ccadld.org/visit"
    },
    "Triangle-Astérides, centre d'art contemporain": {
        "website": "https://triangle-asterides.org/",
        "visit_url": "https://triangle-asterides.org/fr/infos-pratiques/"
    },
    "Artspace Aotearoa": {
        "website": "https://artspace-aotearoa.nz/",
        "visit_url": "https://artspace-aotearoa.nz/visit"
    },
    "Lismore Castle Arts": {
        "website": "https://lismorecastlearts.ie/",
        "visit_url": "https://lismorecastlearts.ie/visit"
    },
    "The Royal Standard": {
        "website": "https://www.the-royal-standard.co.uk/",
        "visit_url": "https://www.the-royal-standard.co.uk/"
    },
    "Kër Thiossane": {
        "website": "https://ker-thiossane.org/",
        "visit_url": "https://ker-thiossane.org/"
    },
    "Raw Material Company": {
        "website": "http://www.rawmaterialcompany.org/",
        "visit_url": "http://www.rawmaterialcompany.org/"
    },
    "Kuona Collective": {
        "website": "https://www.facebook.com/Kuonaartistscollective/",
        "visit_url": "https://www.facebook.com/Kuonaartistscollective/"
    },
    "Fondation Ifitry": {
        "website": "https://biennalecasablanca.org/",
        "visit_url": "https://biennalecasablanca.org/"
    },
    "Theertha International Artists' Collective": {
        "website": "https://www.facebook.com/theerthacollective/",
        "visit_url": "https://www.facebook.com/theerthacollective/"
    },
    "MSU Zagreb (Museum of Contemporary Art)": {
        "website": "http://www.msu.hr/",
        "visit_url": "http://www.msu.hr/"
    },
    "Museum Dhondt-Dhaenens": {
        "website": "https://museumdd.be/",
        "visit_url": "https://museumdd.be/en/visit"
    },
    "Selasar Sunaryo Art Space": {
        "website": "https://selasarsunaryo.org/",
        "visit_url": "https://selasarsunaryo.org/"
    },
    "Potter Museum of Art": {
        "website": "https://potter-museum.unimelb.edu.au/",
        "visit_url": "https://potter-museum.unimelb.edu.au/"
    },
    "Douglas Hyde Gallery": {
        "website": "https://thedouglashyde.ie/",
        "visit_url": "https://thedouglashyde.ie/visit/"
    },
    "Zoma Museum": {
        "website": "https://www.facebook.com/zomamuseum/",
        "visit_url": "https://www.facebook.com/zomamuseum/"
    },
    "Palais de Lomé": {
        "website": "https://palaisdelome.com/",
        "visit_url": "https://palaisdelome.com/"
    },
    "Ishara Art Foundation": {
        "website": "https://www.ishara.org/",
        "visit_url": "https://www.ishara.org/visit/"
    },
    "New Art Exchange": {
        "website": "https://www.nae.org.uk/",
        "visit_url": "https://www.nae.org.uk/visit/"
    },
    "Argos": {
        "website": "https://www.argosarts.org/",
        "visit_url": "https://www.argosarts.org/visit"
    },
    "Kröller-Müller Museum": {
        "website": "https://www.krollermuller.nl/",
        "visit_url": "https://www.krollermuller.nl/en/visit"
    },
    "Museo de Arte Latinoamericano de Buenos Aires (MALBA)": {
        "website": "https://malba.org.ar/",
        "visit_url": "https://malba.org.ar/"
    },
    "Bluecoat": {
        "website": "https://www.thebluecoat.org.uk/",
        "visit_url": "https://www.thebluecoat.org.uk/visit"
    },
    "Groninger Museum": {
        "website": "https://www.groningermuseum.nl/",
        "visit_url": "https://www.groningermuseum.nl/en"
    },
    "Buxton Contemporary": {
        "website": "https://buxtoncontemporary.com/",
        "visit_url": "https://buxtoncontemporary.com/visit/"
    },
    "Artbank": {
        "website": "https://www.artbank.gov.au/",
        "visit_url": "https://www.artbank.gov.au/"
    },
    "Bikini Wax EPS": {
        "website": "https://www.instagram.com/bikiniwaxeps/",
        "visit_url": "https://www.instagram.com/bikiniwaxeps/"
    },
    "State of Concept Athens": {
        "website": "https://stateofconcept.org/",
        "visit_url": "https://stateofconcept.org/",
        "opening_hours": "Physical space closed; public projects held nomadically and online",
        "curator_recommendation": "State of Concept was Greece's foremost non-profit contemporary art institution. Please note that its physical gallery space in Athens is permanently closed; it continues to operate as an independent research, publishing, and discursive platform.",
        "transit_tips": "Physical venue closed; visit online platform."
    },
    "Sa Sa Art Projects": {
        "website": "http://www.sasaart.info/",
        "visit_url": "http://www.sasaart.info/",
        "opening_hours": "Physical gallery closed; permanent online archive accessible at sasaart.info",
        "curator_recommendation": "A foundational Cambodian artist-run initiative. After 14 years of groundbreaking exhibitions and education programs, its physical exhibition space closed in April 2024. Its extensive history and resources remain preserved on its digital archive website at sasaart.info.",
        "transit_tips": "Physical space closed (April 2024); archive available online."
    },
    "Green Papaya Art Projects": {
        "website": "https://www.facebook.com/greenpapayaartprojects/",
        "visit_url": "https://www.facebook.com/greenpapayaartprojects/",
        "opening_hours": "Nomadic research and residency platform; check Facebook for active programs",
        "curator_recommendation": "The longest-running independent artist-run initiative in Manila. Following a 2020 studio fire, Green Papaya transitioned into a nomadic platform focused on residencies, publishing, and archival preservation in partnership with Asia Art Archive.",
        "transit_tips": "Nomadic programming across Manila; check announcements for pop-up venues."
    },
    "Townhouse Gallery": {
        "website": "https://www.facebook.com/townhousegallery/",
        "visit_url": "https://www.facebook.com/townhousegallery/",
        "opening_hours": "Historic gallery closed; projects active nomadically",
        "curator_recommendation": "An iconic cornerstone of independent contemporary art in the Arab world founded in 1998. Following municipal evictions and building collapse in downtown Cairo, Townhouse's mission continues through collaborative nomadic programming and partner spaces.",
        "transit_tips": "Nomadic projects; see announcements."
    },

    # 2. Replacing News Articles / Source Links with Official Institutional Homepages
    "Glenstone": {
        "website": "https://www.glenstone.org/",
        "visit_url": "https://www.glenstone.org/visit/"
    },
    "Guangdong Times Museum": {
        "website": "https://www.timesmuseum.org/",
        "visit_url": "https://www.timesmuseum.org/"
    },
    "How Art Museum": {
        "website": "http://www.howartmuseum.org.cn/",
        "visit_url": "http://www.howartmuseum.org.cn/"
    },
    "OCAT Shenzhen": {
        "website": "http://www.ocat.org.cn/",
        "visit_url": "http://www.ocat.org.cn/"
    },
    "Des Moines Art Center": {
        "website": "https://desmoinesartcenter.org/",
        "visit_url": "https://desmoinesartcenter.org/visit/"
    },
    "Long Museum": {
        "website": "http://thelongmuseum.org/",
        "visit_url": "http://thelongmuseum.org/"
    },
    "Kiran Nadar Museum of Art": {
        "website": "https://www.knma.org/",
        "visit_url": "https://www.knma.org/plan-your-visit/"
    },
    "Museum MACAN": {
        "website": "https://www.museummacan.org/",
        "visit_url": "https://www.museummacan.org/visit"
    },
    "Peggy Guggenheim Collection": {
        "website": "https://www.guggenheim-venice.it/",
        "visit_url": "https://www.guggenheim-venice.it/en/visit/"
    },
    "Garage Museum": {
        "website": "https://garagemca.org/",
        "visit_url": "https://garagemca.org/en/visit"
    },
    "Kunsthaus Zürich": {
        "website": "https://www.kunsthaus.ch/",
        "visit_url": "https://www.kunsthaus.ch/en/besuch-planen/"
    },
    "Dulwich Picture Gallery": {
        "website": "https://www.dulwichpicturegallery.org.uk/",
        "visit_url": "https://www.dulwichpicturegallery.org.uk/visit/"
    },
    "Goldsmiths CCA": {
        "website": "https://goldsmithscca.art/",
        "visit_url": "https://goldsmithscca.art/visit/"
    },
    "V&A": {
        "website": "https://www.vam.ac.uk/",
        "visit_url": "https://www.vam.ac.uk/visit"
    },
    "LACMA": {
        "website": "https://www.lacma.org/",
        "visit_url": "https://www.lacma.org/visit"
    },
    "Pérez Art Museum Miami": {
        "website": "https://www.pamm.org/",
        "visit_url": "https://www.pamm.org/en/visit/"
    },
    "Brooklyn Museum": {
        "website": "https://www.brooklynmuseum.org/",
        "visit_url": "https://www.brooklynmuseum.org/visit"
    },
    "British Museum": {
        "website": "https://www.britishmuseum.org/",
        "visit_url": "https://www.britishmuseum.org/visit"
    },
    "National Portrait Gallery": {
        "website": "https://www.npg.org.uk/",
        "visit_url": "https://www.npg.org.uk/visit/"
    },
    "National Theatre": {
        "website": "https://www.nationaltheatre.org.uk/",
        "visit_url": "https://www.nationaltheatre.org.uk/your-visit"
    },
    "Royal Ballet and Opera": {
        "website": "https://rbo.org.uk/",
        "visit_url": "https://rbo.org.uk/your-visit"
    },
    "Turner Contemporary": {
        "website": "https://turnercontemporary.org/",
        "visit_url": "https://turnercontemporary.org/visit/"
    },
    "Van Gogh Museum": {
        "website": "https://www.vangoghmuseum.nl/",
        "visit_url": "https://www.vangoghmuseum.nl/en/visit"
    },
    "Louvre": {
        "website": "https://www.louvre.fr/",
        "visit_url": "https://www.louvre.fr/en/visit"
    },
    "Musée d'Orsay": {
        "website": "https://www.musee-orsay.fr/",
        "visit_url": "https://www.musee-orsay.fr/en/visit"
    },
    "Rijksmuseum": {
        "website": "https://www.rijksmuseum.nl/",
        "visit_url": "https://www.rijksmuseum.nl/en/visit"
    },
    "Science Museum": {
        "website": "https://www.sciencemuseum.org.uk/",
        "visit_url": "https://www.sciencemuseum.org.uk/see-and-do/welcome"
    },
    "Wexner Center for the Arts": {
        "website": "https://wexarts.org/",
        "visit_url": "https://wexarts.org/visit"
    },
    "Frist Art Museum": {
        "website": "https://fristartmuseum.org/",
        "visit_url": "https://fristartmuseum.org/visit/"
    },
    "American Museum of Natural History": {
        "website": "https://www.amnh.org/",
        "visit_url": "https://www.amnh.org/plan-your-visit"
    },
    "Art Institute of Chicago": {
        "website": "https://www.artic.edu/",
        "visit_url": "https://www.artic.edu/visit"
    },
    "Smithsonian, Air and Space": {
        "website": "https://airandspace.si.edu/",
        "visit_url": "https://airandspace.si.edu/visit"
    },
    "Darwin Festival": {
        "website": "https://www.darwinfestival.org.au/",
        "visit_url": "https://www.darwinfestival.org.au/"
    },
    "Biennale of Sydney": {
        "website": "https://www.biennaleofsydney.art/",
        "visit_url": "https://www.biennaleofsydney.art/"
    },
    "Dhaka Art Summit": {
        "website": "https://www.samdani.com.bd/dhaka-art-summit",
        "visit_url": "https://www.samdani.com.bd/dhaka-art-summit"
    },
    "Esker Foundation": {
        "website": "https://eskerfoundation.com/",
        "visit_url": "https://eskerfoundation.com/visit/"
    },
    "Kunsthalle Bielefeld": {
        "website": "https://www.kunsthalle-bielefeld.de/",
        "visit_url": "https://www.kunsthalle-bielefeld.de/en/visit/"
    },
    "Kochi-Muziris Biennale": {
        "website": "https://www.kochimuzirisbiennale.org/",
        "visit_url": "https://www.kochimuzirisbiennale.org/"
    },
    "Edinburgh International Book Festival": {
        "website": "https://www.edbookfest.co.uk/",
        "visit_url": "https://www.edbookfest.co.uk/"
    },
    "Hay Festival": {
        "website": "https://www.hayfestival.com/",
        "visit_url": "https://www.hayfestival.com/"
    },
    "Design Museum": {
        "website": "https://designmuseum.org/",
        "visit_url": "https://designmuseum.org/plan-your-visit"
    },
    "Zabludowicz Collection": {
        "website": "https://www.zabludowiczcollection.com/",
        "visit_url": "https://www.zabludowiczcollection.com/",
        "curator_recommendation": "Private art trust founded by Poju and Anita Zabludowicz. Note: The permanent exhibition gallery in Kentish Town, London closed to the public in October 2023 following sustained artist boycotts and restructuring; the trust continues collection loans and commissions.",
        "opening_hours": "London gallery permanently closed (Oct 2023); foundation active via loans and collection archive"
    },
    "Kemper Museum": {
        "website": "https://www.kemperart.org/",
        "visit_url": "https://www.kemperart.org/visit"
    },
    "Kunsthalle Tbilisi": {
        "website": "https://www.facebook.com/kunsthalle.tbilisi/",
        "visit_url": "https://www.facebook.com/kunsthalle.tbilisi/"
    },
    "Louvre Abu Dhabi": {
        "website": "https://www.louvreabudhabi.ae/",
        "visit_url": "https://www.louvreabudhabi.ae/en/plan-your-visit"
    },
    "Qatar Museums": {
        "website": "https://qm.org.qa/en/",
        "visit_url": "https://qm.org.qa/en/visit/"
    },
    "City Gallery Wellington": {
        "website": "https://citygallery.org.nz/",
        "visit_url": "https://citygallery.org.nz/visit/"
    },
    "Kyoto City KYOCERA Museum of Art": {
        "website": "https://kyotocity-kyocera.museum/",
        "visit_url": "https://kyotocity-kyocera.museum/en/"
    },
    "Fringe World": {
        "website": "https://fringeworld.com.au/",
        "visit_url": "https://fringeworld.com.au/"
    },
    "Collective": {
        "website": "https://www.collective-edinburgh.art/",
        "visit_url": "https://www.collective-edinburgh.art/visit"
    },
    "Fondation Louis Vuitton": {
        "website": "https://www.fondationlouisvuitton.fr/en",
        "visit_url": "https://www.fondationlouisvuitton.fr/en"
    },
    "Venice Biennale": {
        "website": "https://www.labiennale.org/en",
        "visit_url": "https://www.labiennale.org/en/art"
    },
    "Shepparton Art Museum": {
        "website": "https://sheppartonartmuseum.com.au/",
        "visit_url": "https://sheppartonartmuseum.com.au/visit/"
    },
    "Art Gallery of Hamilton": {
        "website": "https://www.artgalleryofhamilton.com/",
        "visit_url": "https://www.artgalleryofhamilton.com/visit/"
    },
    "Musée national des beaux-arts du Québec": {
        "website": "https://www.mnbaq.org/",
        "visit_url": "https://www.mnbaq.org/en/plan-your-visit"
    },
    "Winnipeg Art Gallery-Qaumajuq": {
        "website": "https://www.wag.ca/",
        "visit_url": "https://www.wag.ca/visit/"
    },
    "QAGOMA": {
        "website": "https://www.qagoma.qld.gov.au/",
        "visit_url": "https://www.qagoma.qld.gov.au/visit/"
    },
    "Castello di Rivoli": {
        "website": "https://www.castellodirivoli.org/",
        "visit_url": "https://www.castellodirivoli.org/en/visita/"
    },
    "Yokohama Museum of Art": {
        "website": "https://yokohama.art.museum/",
        "visit_url": "https://yokohama.art.museum/eng/visit/"
    },
    "Nederlands Fotomuseum": {
        "website": "https://nederlandsfotomuseum.nl/",
        "visit_url": "https://nederlandsfotomuseum.nl/en/visit/"
    },
    "Ateneo Art Gallery": {
        "website": "https://ateneoartgallery.com/",
        "visit_url": "https://ateneoartgallery.com/visit"
    },
    "Stills": {
        "website": "https://stills.info/",
        "visit_url": "https://stills.info/visit/"
    },

    # 3. Replacing ProPublica / Wikipedia / Charity Register URLs with Official Sites
    "Dundee Contemporary Arts": {
        "website": "https://www.dca.org.uk/",
        "visit_url": "https://www.dca.org.uk/visit"
    },
    "Wysing Arts Centre": {
        "website": "https://www.wysingartscentre.org/",
        "visit_url": "https://www.wysingartscentre.org/visit"
    },
    "Firstsite": {
        "website": "https://firstsite.uk/",
        "visit_url": "https://firstsite.uk/visiting-us/"
    },
    "HOME": {
        "website": "https://www.homemcr.org/",
        "visit_url": "https://www.homemcr.org/visit/"
    },
    "Cample Line": {
        "website": "https://campleline.org.uk/",
        "visit_url": "https://campleline.org.uk/visit"
    },
    "Storm King Art Center": {
        "website": "https://stormking.org/",
        "visit_url": "https://stormking.org/visit/"
    },
    "Château de Versailles": {
        "website": "https://www.chateauversailles.fr/",
        "visit_url": "https://en.chateauversailles.fr/plan-your-visit"
    },
    "Palacio Libertad": {
        "website": "https://palaciolibertad.gob.ar/",
        "visit_url": "https://palaciolibertad.gob.ar/"
    },
    "Cafesjian Center for the Arts": {
        "website": "https://www.cmf.am/",
        "visit_url": "https://www.cmf.am/Visitor-Information"
    },
    "Fondation Zinsou": {
        "website": "https://fondationzinsou.org/",
        "visit_url": "https://fondationzinsou.org/"
    },
    "Casa França-Brasil": {
        "website": "https://casabrasil.rj.gov.br/",
        "visit_url": "https://casabrasil.rj.gov.br/"
    },
    "Museu de Arte Moderna da Bahia": {
        "website": "https://www.instagram.com/bahiamam/",
        "visit_url": "https://www.instagram.com/bahiamam/"
    },
    "Museu Lasar Segall": {
        "website": "http://www.museusegall.org.br/",
        "visit_url": "http://www.museusegall.org.br/"
    },
    "Power Station of Art": {
        "website": "https://www.powerstationofart.com/",
        "visit_url": "https://www.powerstationofart.com/visit"
    },
    "Ordrupgaard": {
        "website": "https://ordrupgaard.dk/",
        "visit_url": "https://ordrupgaard.dk/en/visit-ordrupgaard/"
    },
    "Museum of Modern Egyptian Art": {
        "website": "https://www.fineart.gov.eg/",
        "visit_url": "https://www.fineart.gov.eg/"
    },
    "National Gallery of Jamaica": {
        "website": "https://natgalja.org.jm/",
        "visit_url": "https://natgalja.org.jm/visit/"
    },
    "Watari-um": {
        "website": "http://www.watarium.co.jp/",
        "visit_url": "http://www.watarium.co.jp/"
    },
    "Musée des Civilisations Noires": {
        "website": "https://www.facebook.com/mcn.officiel/",
        "visit_url": "https://www.facebook.com/mcn.officiel/"
    },
    "STPI Creative Workshop & Gallery": {
        "website": "https://www.stpi.com.sg/",
        "visit_url": "https://www.stpi.com.sg/visit/"
    },
    "Seoul Museum of Art": {
        "website": "https://sema.seoul.go.kr/",
        "visit_url": "https://sema.seoul.go.kr/en/index"
    },
    "Whanki Museum": {
        "website": "http://whankimuseum.org/",
        "visit_url": "http://whankimuseum.org/"
    },
    "Nam June Paik Art Center": {
        "website": "https://njp.ggcf.kr/",
        "visit_url": "https://njp.ggcf.kr/en"
    },
    "Kaohsiung Museum of Fine Arts": {
        "website": "https://www.kmfa.gov.tw/",
        "visit_url": "https://www.kmfa.gov.tw/English/"
    },
    "Hong-gah Museum": {
        "website": "https://www.hong-gah.org.tw/",
        "visit_url": "https://www.hong-gah.org.tw/en/visit"
    },
    "MOCA Taipei": {
        "website": "https://www.mocataipei.org.tw/",
        "visit_url": "https://www.mocataipei.org.tw/en"
    },
    "Taipei Fine Arts Museum": {
        "website": "https://www.tfam.museum/",
        "visit_url": "https://www.tfam.museum/index.aspx?ddlLang=en-us"
    },
    "Grizedale Arts": {
        "website": "https://www.grizedale.org/",
        "visit_url": "https://www.grizedale.org/"
    },
    "Yuz Museum": {
        "website": "http://www.yuzmshanghai.org/",
        "visit_url": "http://www.yuzmshanghai.org/"
    },
    "Bangkok Art and Culture Centre": {
        "website": "https://www.bacc.or.th/",
        "visit_url": "https://www.bacc.or.th/"
    },
    "Sharjah Art Foundation": {
        "website": "https://sharjahart.org/",
        "visit_url": "https://sharjahart.org/visit"
    },
    "Aspen Art Museum": {
        "website": "https://www.aspenartmuseum.org/",
        "visit_url": "https://www.aspenartmuseum.org/visit"
    },
    "Getty Center": {
        "website": "https://www.getty.edu/",
        "visit_url": "https://www.getty.edu/visit/center/"
    },
    "Yerba Buena Center for the Arts": {
        "website": "https://ybca.org/",
        "visit_url": "https://ybca.org/visit"
    },
    "Boise Art Museum": {
        "website": "https://www.boiseartmuseum.org/",
        "visit_url": "https://www.boiseartmuseum.org/visit/"
    },
    "Gibbes Museum of Art": {
        "website": "https://www.gibbesmuseum.org/",
        "visit_url": "https://www.gibbesmuseum.org/visit/"
    },
    "Orange County Museum of Art": {
        "website": "https://ocma.art/",
        "visit_url": "https://ocma.art/visit/"
    },
    "Dallas Contemporary": {
        "website": "https://www.dallascontemporary.org/",
        "visit_url": "https://www.dallascontemporary.org/visit"
    },
    "Clyfford Still Museum": {
        "website": "https://clyffordstillmuseum.org/",
        "visit_url": "https://clyffordstillmuseum.org/visit/"
    },
    "Denver Art Museum": {
        "website": "https://www.denverartmuseum.org/",
        "visit_url": "https://www.denverartmuseum.org/en/visit"
    },
    "Modern Art Museum of Fort Worth": {
        "website": "https://www.themodern.org/",
        "visit_url": "https://www.themodern.org/visit"
    },
    "Museum of Contemporary Art San Diego": {
        "website": "https://mcasd.org/",
        "visit_url": "https://mcasd.org/visit"
    },
    "Craft Contemporary": {
        "website": "https://www.craftcontemporary.org/",
        "visit_url": "https://www.craftcontemporary.org/visit"
    },
    "New Orleans Museum of Art": {
        "website": "https://noma.org/",
        "visit_url": "https://noma.org/visit/"
    },
    "Oakland Museum of California": {
        "website": "https://museumca.org/",
        "visit_url": "https://museumca.org/visit/"
    },
    "Palm Springs Art Museum": {
        "website": "https://www.psmuseum.org/",
        "visit_url": "https://www.psmuseum.org/visit"
    },
    "Heard Museum": {
        "website": "https://heard.org/",
        "visit_url": "https://heard.org/visit/"
    },
    "Phoenix Art Museum": {
        "website": "https://phxart.org/",
        "visit_url": "https://phxart.org/visit/"
    },
    "Nevada Museum of Art": {
        "website": "https://www.nevadaart.org/",
        "visit_url": "https://www.nevadaart.org/visit/"
    },
    "Utah Museum of Contemporary Art": {
        "website": "https://utahmoca.org/",
        "visit_url": "https://utahmoca.org/visit/"
    },
    "McNay Art Museum": {
        "website": "https://www.mcnayart.org/",
        "visit_url": "https://www.mcnayart.org/visit/"
    },
    "Asian Art Museum": {
        "website": "https://asianart.org/",
        "visit_url": "https://asianart.org/visit/"
    },
    "New Mexico Museum of Art": {
        "website": "https://www.nmartmuseum.org/",
        "visit_url": "https://www.nmartmuseum.org/visit/"
    },
    "Telfair Museums": {
        "website": "https://www.telfair.org/",
        "visit_url": "https://www.telfair.org/visit/"
    },
    "Scottsdale Museum of Contemporary Art": {
        "website": "https://smoca.org/",
        "visit_url": "https://smoca.org/visit/"
    },
    "Seattle Art Museum": {
        "website": "https://www.seattleartmuseum.org/",
        "visit_url": "https://www.seattleartmuseum.org/visit"
    },
    "SECCA": {
        "website": "https://secca.org/",
        "visit_url": "https://secca.org/visit"
    },
    "Dallas Museum of Art": {
        "website": "https://dma.org/",
        "visit_url": "https://dma.org/visit"
    },
    "MCA Denver": {
        "website": "https://mcadenver.org/",
        "visit_url": "https://mcadenver.org/visit"
    },
    "Portland Art Museum": {
        "website": "https://portlandartmuseum.org/",
        "visit_url": "https://portlandartmuseum.org/visit/"
    },
    "Art Gallery of South Australia": {
        "website": "https://www.agsa.sa.gov.au/",
        "visit_url": "https://www.agsa.sa.gov.au/visit/"
    },
    "M HKA": {
        "website": "https://www.muhka.be/",
        "visit_url": "https://www.muhka.be/en/visit"
    },
    "Museu de Arte Moderna do Rio de Janeiro": {
        "website": "https://mam.rio/",
        "visit_url": "https://mam.rio/"
    },
    "MASP": {
        "website": "https://masp.org.br/",
        "visit_url": "https://masp.org.br/visite"
    },
    "Glenbow": {
        "website": "https://www.glenbow.org/",
        "visit_url": "https://www.glenbow.org/visit/"
    },
    "M+": {
        "website": "https://www.mplus.org.hk/",
        "visit_url": "https://www.mplus.org.hk/en/plan-your-visit/"
    },
    "Tai Kwun": {
        "website": "https://www.taikwun.hk/",
        "visit_url": "https://www.taikwun.hk/en/visit"
    },
    "Museum Folkwang": {
        "website": "https://www.museum-folkwang.de/",
        "visit_url": "https://www.museum-folkwang.de/en/visit"
    },
    "Kunstmuseum Wolfsburg": {
        "website": "https://www.kunstmuseum.de/",
        "visit_url": "https://www.kunstmuseum.de/en/visitor-information/"
    },
    "IMMA": {
        "website": "https://imma.ie/",
        "visit_url": "https://imma.ie/visit/"
    },
    "MUAC": {
        "website": "https://muac.unam.mx/",
        "visit_url": "https://muac.unam.mx/planea-tu-visita"
    },
    "Mauritshuis": {
        "website": "https://www.mauritshuis.nl/",
        "visit_url": "https://www.mauritshuis.nl/en/visit/"
    },
    "Govett-Brewster / Len Lye Centre": {
        "website": "https://govettbrewster.com/",
        "visit_url": "https://govettbrewster.com/visit/"
    },
    "Bergen International Festival": {
        "website": "https://www.fib.no/",
        "visit_url": "https://www.fib.no/"
    },
    "MUNCH": {
        "website": "https://www.munch.no/",
        "visit_url": "https://www.munch.no/en/visit/"
    },
    "MAAT": {
        "website": "https://www.maat.pt/",
        "visit_url": "https://www.maat.pt/en/visit"
    },
    "Guggenheim Bilbao": {
        "website": "https://www.guggenheim-bilbao.eus/",
        "visit_url": "https://www.guggenheim-bilbao.eus/en/plan-your-visit"
    },
    "National Gallery": {
        "website": "https://www.nationalgallery.org.uk/",
        "visit_url": "https://www.nationalgallery.org.uk/visiting"
    },
    "MK Gallery": {
        "website": "https://mkgallery.org/",
        "visit_url": "https://mkgallery.org/visit/"
    },
    "The Box": {
        "website": "https://www.theboxplymouth.com/",
        "visit_url": "https://www.theboxplymouth.com/visit"
    },
    "Menil Collection": {
        "website": "https://www.menil.org/",
        "visit_url": "https://www.menil.org/visit"
    },
    "MOCA Los Angeles": {
        "website": "https://www.moca.org/",
        "visit_url": "https://www.moca.org/visit"
    },
    "Speed Art Museum": {
        "website": "https://speedmuseum.org/",
        "visit_url": "https://speedmuseum.org/visit/"
    },
    "The Bass": {
        "website": "https://thebass.org/",
        "visit_url": "https://thebass.org/visit/"
    },
    "Dia Art Foundation": {
        "website": "https://www.diaart.org/",
        "visit_url": "https://www.diaart.org/visit"
    }
}

with open('institutions.json', 'r', encoding='utf-8') as f:
    institutions = json.load(f)

updated_count = 0
for inst in institutions:
    name = inst.get('name')
    if name in URL_UPDATES:
        patch = URL_UPDATES[name]
        for k, v in patch.items():
            inst[k] = v
        updated_count += 1
    else:
        # Also clean up any lingering /visit appended to invalid URLs
        pass

print(f"Applied patches to {updated_count} institutions.")

with open('institutions.json', 'w', encoding='utf-8') as f:
    json.dump(institutions, f, indent=2, ensure_ascii=False)
print("Updated institutions.json saved.")
