import json

with open('/Users/polinavasilyeva/.gemini/antigravity/scratch/sponsor-atlas/app/world-topo.json') as f:
    topo = json.load(f)

with open('/Users/polinavasilyeva/.gemini/antigravity/scratch/sponsor-atlas/institutions.json') as f:
    institutions = json.load(f)

scale = topo['transform']['scale']
translate = topo['transform']['translate']

# Decode and downsample arcs
arcs_downsampled = []
for arc in topo['arcs']:
    curr_x, curr_y = 0, 0
    pts = []
    last_pt = None
    for dx, dy in arc:
        curr_x += dx
        curr_y += dy
        p = [round(curr_x * scale[0] + translate[0], 1), round(curr_y * scale[1] + translate[1], 1)]
        if last_pt is None or (abs(p[0] - last_pt[0]) >= 0.4 or abs(p[1] - last_pt[1]) >= 0.4):
            pts.append(p)
            last_pt = p
    if len(pts) > 1:
        arcs_downsampled.append(pts)

# Extract cities and normalize countries
city_data = {}
inst_countries = {}

for inst in institutions:
    parts = [p.strip() for p in inst['location'].split(',')]
    city = parts[0]
    c_name = parts[-1] if len(parts) > 1 else parts[0]
    if c_name in ['USA', 'United States']:
        c_name = 'USA'
    elif c_name in ['UK', 'United Kingdom', 'England', 'Scotland', 'Wales']:
        c_name = 'UK'
    inst['country'] = c_name
    inst['city'] = city
    inst_countries[c_name] = inst_countries.get(c_name, 0) + 1

    if city not in city_data:
        city_data[city] = {
            'name': city,
            'country': c_name,
            'lat': inst['lat'],
            'lon': inst['lon'],
            'count': 0
        }
    city_data[city]['count'] += 1

sorted_cities = sorted(city_data.values(), key=lambda x: (-x['count'], x['name']))

# Accurate country centroids for on-globe typography
COUNTRY_CENTROIDS = [
    {'name': 'UNITED STATES', 'lat': 38.0, 'lon': -97.0, 'country': 'USA'},
    {'name': 'UNITED KINGDOM', 'lat': 54.0, 'lon': -2.5, 'country': 'UK'},
    {'name': 'FRANCE', 'lat': 46.5, 'lon': 2.5, 'country': 'France'},
    {'name': 'GERMANY', 'lat': 51.2, 'lon': 10.4, 'country': 'Germany'},
    {'name': 'JAPAN', 'lat': 36.5, 'lon': 138.2, 'country': 'Japan'},
    {'name': 'DENMARK', 'lat': 56.0, 'lon': 9.5, 'country': 'Denmark'},
    {'name': 'AUSTRALIA', 'lat': -25.0, 'lon': 134.0, 'country': 'Australia'},
    {'name': 'CANADA', 'lat': 56.0, 'lon': -106.0, 'country': 'Canada'},
    {'name': 'ITALY', 'lat': 42.8, 'lon': 12.6, 'country': 'Italy'},
    {'name': 'SPAIN', 'lat': 40.2, 'lon': -3.7, 'country': 'Spain'},
    {'name': 'SWITZERLAND', 'lat': 46.8, 'lon': 8.2, 'country': 'Switzerland'},
    {'name': 'AUSTRIA', 'lat': 47.5, 'lon': 14.5, 'country': 'Austria'},
    {'name': 'NETHERLANDS', 'lat': 52.2, 'lon': 5.3, 'country': 'Netherlands'},
    {'name': 'SWEDEN', 'lat': 62.0, 'lon': 15.0, 'country': 'Sweden'},
    {'name': 'NORWAY', 'lat': 62.0, 'lon': 8.5, 'country': 'Norway'},
    {'name': 'BELGIUM', 'lat': 50.8, 'lon': 4.4, 'country': 'Belgium'},
    {'name': 'SOUTH AFRICA', 'lat': -30.5, 'lon': 25.0, 'country': 'South Africa'},
    {'name': 'NEW ZEALAND', 'lat': -41.0, 'lon': 174.0, 'country': 'New Zealand'},
    {'name': 'BRAZIL', 'lat': -14.2, 'lon': -51.9, 'country': 'Brazil'},
    {'name': 'ARGENTINA', 'lat': -38.4, 'lon': -63.6, 'country': 'Argentina'},
    {'name': 'IRELAND', 'lat': 53.4, 'lon': -8.2, 'country': 'Ireland'},
    {'name': 'FINLAND', 'lat': 64.0, 'lon': 26.0, 'country': 'Finland'},
    {'name': 'PORTUGAL', 'lat': 39.5, 'lon': -8.0, 'country': 'Portugal'},
    {'name': 'MEXICO', 'lat': 23.6, 'lon': -102.5, 'country': 'Mexico'},
    {'name': 'CHINA', 'lat': 35.8, 'lon': 104.1, 'country': 'China'},
    {'name': 'INDIA', 'lat': 20.6, 'lon': 78.9, 'country': 'India'},
    {'name': 'LEBANON', 'lat': 33.8, 'lon': 35.8, 'country': 'Lebanon'},
    {'name': 'UAE', 'lat': 24.0, 'lon': 54.0, 'country': 'UAE'},
    {'name': 'SENEGAL', 'lat': 14.5, 'lon': -14.4, 'country': 'Senegal'},
    {'name': 'THAILAND', 'lat': 15.8, 'lon': 100.9, 'country': 'Thailand'},
    {'name': 'MALAYSIA', 'lat': 4.2, 'lon': 101.9, 'country': 'Malaysia'},
    {'name': 'PERU', 'lat': -9.1, 'lon': -75.0, 'country': 'Peru'},
    {'name': 'GREECE', 'lat': 39.0, 'lon': 22.0, 'country': 'Greece'},
    {'name': 'RUSSIA', 'lat': 61.5, 'lon': 105.3, 'country': 'Russia'}
]

country_list = []
for c, cnt in sorted(inst_countries.items(), key=lambda x: (-x[1], x[0])):
    centroid = next((x for x in COUNTRY_CENTROIDS if x['country'] == c), None)
    if centroid:
        country_list.append({
            'name': c,
            'label': centroid['name'],
            'lat': centroid['lat'],
            'lon': centroid['lon'],
            'count': cnt
        })
    else:
        match_insts = [i for i in institutions if i['country'] == c]
        lat = sum(i['lat'] for i in match_insts) / len(match_insts)
        lon = sum(i['lon'] for i in match_insts) / len(match_insts)
        country_list.append({
            'name': c,
            'label': c.upper(),
            'lat': round(lat, 2),
            'lon': round(lon, 2),
            'count': cnt
        })

PENDING_MUSEUMS = {
    'british museum': {
        'name': 'The British Museum',
        'city': 'London',
        'country': 'UK',
        'location': 'London, UK',
        'lat': 51.5194,
        'lon': -0.127,
        'size': 'L',
        'tier': 'B',
        'funding': '£110M+ operating budget. Statutory Grant-in-Aid from DCMS (~45%), exhibition admissions, and corporate partnerships.',
        'watch': 'Historic 27-year sponsorship with BP triggered massive activist protests ("BP or not BP?"). After the contract expired in 2023, trustees sparked intense backlash by signing a new £50M 10-year masterplan deal with BP in December 2023. Additionally embroiled in major restitution disputes over the Parthenon Marbles and looted Benin Bronzes.',
        'why_not_on_map': 'Excluded from verified status due to active renewal of fossil fuel (BP) sponsorship and unresolved imperial restitution claims preventing ethical governance certification.',
        'status': 'Tier Review · High Controversy',
        'sources': [
            'https://www.britishmuseum.org',
            'https://www.theguardian.com/culture/2023/dec/19/british-museum-signs-50m-deal-with-bp-to-help-fund-masterplan'
        ]
    },
    'louvre': {
        'name': 'Musée du Louvre',
        'city': 'Paris',
        'country': 'France',
        'location': 'Paris, France',
        'lat': 48.8606,
        'lon': 2.3376,
        'size': 'L',
        'tier': 'B',
        'funding': '€230M operating budget. French Ministry of Culture statutory subsidies (~50%), ticketing receipts (9M+ visitors), commercial brand rentals, and retail.',
        'watch': 'Scrutiny over commercial brand licensing (private corporate takeovers and luxury galas) and historic patronage from oil giant Total (ended 2018). Associated with the Louvre Abu Dhabi franchise, which faced severe criticism from Human Rights Watch regarding migrant construction labor exploitation on Saadiyat Island.',
        'why_not_on_map': 'Flagged under Tier Review due to Gulf franchise labor ethics, past fossil fuel patronage, and commercial private leasing of public galleries.',
        'status': 'Tier Review · Franchise Scrutiny',
        'sources': [
            'https://www.louvre.fr',
            'https://www.hrw.org/news/2015/02/10/uae-migrant-workers-at-risk-on-saadiyat-island'
        ]
    },
    'lacma': {
        'name': 'Los Angeles County Museum of Art (LACMA)',
        'city': 'Los Angeles',
        'country': 'USA',
        'location': 'Los Angeles, USA',
        'lat': 34.0639,
        'lon': -118.3592,
        'size': 'L',
        'tier': 'B',
        'funding': '$100M+ operating budget. LA County taxpayer support, admissions, board patrons, and $750M Peter Zumthor building capital campaign.',
        'watch': 'Scrutiny over high-dollar billionaire patronage (entertainment executive David Geffen gifted $150M for building naming rights), past BP corporate title sponsorships, and trustee ties to commercial mega-galleries. Severe community and architectural backlash for spending $750M on a new building that reduced exhibition gallery square footage by over 30%.',
        'why_not_on_map': 'Awaiting final forensic audit of post-expansion capital bond liabilities, corporate naming rights covenants, and trustee commercial conflicts.',
        'status': 'Tier Review · Capital Campaign Scrutiny',
        'sources': [
            'https://www.lacma.org',
            'https://www.latimes.com/entertainment-arts/story/2020-04-08/lacma-david-geffen-galleries-demolition'
        ]
    },
    'hermitage': {
        'name': 'The State Hermitage Museum',
        'city': 'St. Petersburg',
        'country': 'Russia',
        'location': 'St. Petersburg, Russia',
        'lat': 59.9398,
        'lon': 30.3146,
        'size': 'L',
        'tier': 'U',
        'funding': 'Directly funded by the Russian federal state cultural budget and ticket sales.',
        'watch': 'Completely excluded from ethical mapping due to direct state political instrumentation and absence of curatorial independence. Following the 2022 invasion of Ukraine, director Mikhail Piotrovsky made public statements endorsing state military actions. International satellite institutions (such as Hermitage Amsterdam) completely severed ties, and the museum is subject to international cultural sanctions.',
        'why_not_on_map': 'Excluded due to state wartime propaganda alignment, total lack of curatorial autonomy, and comprehensive international cultural sanctions.',
        'status': 'Excluded · State-Instrumented',
        'sources': [
            'https://www.hermitagemuseum.org',
            'https://www.theartnewspaper.com/2022/03/03/hermitage-amsterdam-severs-ties-with-st-petersburg'
        ]
    },
    'rijksmuseum': {
        'name': 'Rijksmuseum',
        'city': 'Amsterdam',
        'country': 'Netherlands',
        'location': 'Amsterdam, Netherlands',
        'lat': 52.36,
        'lon': 4.8852,
        'size': 'L',
        'tier': 'B',
        'funding': '€115M annual budget. Dutch Ministry of Education, Culture and Science, BankGiro Loterij, ING Bank, Philips, private patrons.',
        'watch': 'Subject to ongoing Museumplein climate protests led by Fossil Free Culture NL, urging the museum to follow the Van Gogh Museum\'s lead and cut ties with ING Bank over ING\'s multibillion-euro investments in oil, gas, and high-emission infrastructure.',
        'why_not_on_map': 'Currently undergoing review pending the completion of the 2024 Dutch cultural sector climate review regarding fossil-financing banks.',
        'status': 'Under Review · Bank Sponsorship',
        'sources': [
            'https://www.rijksmuseum.nl',
            'https://fossilfreeculture.nl'
        ]
    },
    'v&a': {
        'name': 'Victoria and Albert Museum (V&A)',
        'city': 'London',
        'country': 'UK',
        'location': 'London, UK',
        'lat': 51.4966,
        'lon': -0.1722,
        'size': 'L',
        'tier': 'B',
        'funding': '£75M annual budget. DCMS statutory grant-in-aid, admissions, commercial income, philanthropic endowments.',
        'watch': 'Sits in post-crisis review after intense activist pressure (Nan Goldin and P.A.I.N.) over historic acceptance of Sackler family gifts for the Sackler Courtyard. Leadership initially resisted removing the family name despite widespread cultural boycotts, before finally dropping the Sackler branding in October 2022.',
        'why_not_on_map': 'Awaiting completion of its post-Sackler corporate gift policy review and revised ethical donation charter.',
        'status': 'Under Review · Post-Sackler Audit',
        'sources': [
            'https://www.vam.ac.uk',
            'https://www.theguardian.com/artanddesign/2022/oct/01/v-and-a-drops-sackler-name-from-galleries'
        ]
    }
}

# Generate IBM Carbon App HTML
carbon_app_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Culture Atlas | IBM Carbon Design System</title>
  
  <!-- IBM Plex Fonts -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@300;400;500;600;700&display=swap" rel="stylesheet">
  
  <!-- Tailwind CSS CDN -->
  <script src="https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js"></script>
  
  <style>
    /* IBM Carbon Design System Tokens (Gray 100 Dark Theme) */
    :root {{
      --cds-background: #161616;
      --cds-layer-01: #262626;
      --cds-layer-02: #393939;
      --cds-border-subtle: #393939;
      --cds-border-strong: #525252;
      --cds-text-01: #f4f4f4;
      --cds-text-02: #c6c6c6;
      --cds-text-03: #8d8d8d;
      --cds-interactive: #0f62fe;
      --cds-interactive-hover: #0353e9;
      --cds-verified: #24a148;
      --cds-verified-bg: #132c1c;
      --cds-onename: #4589ff;
      --cds-onename-bg: #0f284c;
      --cds-unverified: #8d8d8d;
      --cds-unverified-bg: #262626;
      --cds-focus: #f1c21b;
    }}

    * {{
      box-sizing: border-box;
    }}

    body {{
      font-family: 'IBM Plex Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      background-color: var(--cds-background);
      color: var(--cds-text-01);
      margin: 0;
      padding: 0;
      overflow-x: hidden;
      -webkit-font-smoothing: antialiased;
    }}

    .font-mono {{
      font-family: 'IBM Plex Mono', monospace;
    }}

    #globeCanvas {{
      cursor: grab;
      touch-action: none;
    }}
    #globeCanvas.dragging {{
      cursor: grabbing;
    }}

    /* Carbon crisp scrollbar */
    ::-webkit-scrollbar {{
      width: 5px;
      height: 5px;
    }}
    ::-webkit-scrollbar-track {{
      background: #161616;
    }}
    ::-webkit-scrollbar-thumb {{
      background: #393939;
    }}
    ::-webkit-scrollbar-thumb:hover {{
      background: #525252;
    }}
  </style>
</head>
<body class="min-h-screen flex flex-col bg-[#161616] text-[#f4f4f4]">

  <!-- TOP HEADER (IBM Carbon Header Bar) -->
  <header class="border-b border-[#393939] bg-[#262626] sticky top-0 z-40 px-4 py-2.5">
    <div class="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-3">
      
      <div class="flex items-center gap-3">
        <!-- Carbon Style Square App Icon -->
        <div class="w-7 h-7 bg-[#0f62fe] flex items-center justify-center text-white font-mono font-bold text-xs tracking-wider">
          CA
        </div>
        <div>
          <h1 class="text-sm font-semibold tracking-wide text-[#f4f4f4] flex items-center gap-2">
            <span>CULTURE ATLAS</span>
            <span class="text-[11px] font-mono font-normal px-2 py-0.5 bg-[#393939] text-[#c6c6c6] border border-[#525252]">
              {len(inst_countries)} Countries · {len(sorted_cities)} Cities · {len(institutions)} Institutions
            </span>
          </h1>
          <p class="text-[11px] text-[#8d8d8d] hidden sm:block">Ethically audited cultural institutions mapped by institutional capital & governance.</p>
        </div>
      </div>

      <div class="flex items-center gap-2 flex-wrap">
        <!-- Carbon View Switcher -->
        <div class="flex bg-[#161616] border border-[#393939] p-0.5 text-xs font-mono">
          <button id="viewGlobeBtn" class="px-3 py-1 font-medium transition bg-[#0f62fe] text-white">
            3D Globe
          </button>
          <button id="viewListBtn" class="px-3 py-1 font-medium text-[#c6c6c6] hover:text-white transition">
            Table View
          </button>
        </div>

        <!-- AI Concierge Toggle -->
        <button id="toggleConciergeBtn" class="flex items-center gap-1.5 px-3 py-1.5 bg-[#0f62fe] hover:bg-[#0353e9] text-white font-medium text-xs border border-[#0f62fe] transition">
          <span>✨</span>
          <span>Atlas Concierge</span>
          <span class="hidden md:inline text-[10px] text-white/80 font-mono">⌘K</span>
        </button>
      </div>

    </div>
  </header>

  <!-- FILTER & LOCATION SELECTOR BAR (Carbon Toolbar) -->
  <section class="border-b border-[#393939] bg-[#1c1c1c] px-4 py-2 text-xs">
    <div class="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-3">
      
      <!-- Left Filters: Country & City Selectors -->
      <div class="flex items-center gap-2.5 flex-wrap">
        
        <!-- Country Selector -->
        <div class="flex items-center gap-1.5">
          <span class="text-[#8d8d8d] font-mono text-[11px]">COUNTRY:</span>
          <select id="countrySelect" class="bg-[#262626] border border-[#525252] px-2 py-1 text-xs text-[#f4f4f4] focus:outline-none focus:border-[#0f62fe] font-mono">
            <option value="all">All Countries ({len(inst_countries)})</option>
          </select>
        </div>

        <!-- City Selector -->
        <div class="flex items-center gap-1.5">
          <span class="text-[#8d8d8d] font-mono text-[11px]">CITY:</span>
          <select id="citySelect" class="bg-[#262626] border border-[#525252] px-2 py-1 text-xs text-[#f4f4f4] focus:outline-none focus:border-[#0f62fe] font-mono">
            <option value="all">All Cities ({len(sorted_cities)})</option>
          </select>
        </div>

        <div class="h-4 w-[1px] bg-[#393939] hidden sm:block"></div>

        <!-- Carbon Tier Chips (No glow, flat Carbon status colors) -->
        <div class="flex items-center gap-1.5 flex-wrap font-mono text-[11px]">
          <button id="tierABtn" class="tier-chip flex items-center gap-1.5 px-2.5 py-0.5 border border-[#24a148] bg-[#132c1c] text-[#24a148] hover:bg-[#194025] transition" data-tier="A">
            <span class="w-1.5 h-1.5 bg-[#24a148]"></span>
            <span>Verified</span>
            <span class="text-[#c6c6c6] text-[10px] ml-0.5">{len([i for i in institutions if i['tier'] == 'A'])}</span>
          </button>
          <button id="tierBBtn" class="tier-chip flex items-center gap-1.5 px-2.5 py-0.5 border border-[#4589ff] bg-[#0f284c] text-[#4589ff] hover:bg-[#183968] transition" data-tier="B">
            <span class="w-1.5 h-1.5 bg-[#4589ff]"></span>
            <span>One Name</span>
            <span class="text-[#c6c6c6] text-[10px] ml-0.5">{len([i for i in institutions if i['tier'] == 'B'])}</span>
          </button>
          <button id="tierUBtn" class="tier-chip flex items-center gap-1.5 px-2.5 py-0.5 border border-[#525252] bg-[#262626] text-[#8d8d8d] hover:bg-[#333333] transition" data-tier="U">
            <span class="w-1.5 h-1.5 bg-[#8d8d8d]"></span>
            <span>Unverified</span>
            <span class="text-[#c6c6c6] text-[10px] ml-0.5">{len([i for i in institutions if i['tier'] == 'U'])}</span>
          </button>
        </div>

      </div>

      <!-- Right Filters: Size & Search -->
      <div class="flex items-center gap-3 flex-wrap">
        <div class="flex items-center bg-[#262626] border border-[#393939] text-xs font-mono">
          <button id="sizeAllBtn" class="px-2.5 py-0.5 text-white bg-[#0f62fe] font-medium">All</button>
          <button id="sizeLargeBtn" class="px-2.5 py-0.5 text-[#c6c6c6] hover:text-white">Large (&gt;$20M)</button>
          <button id="sizeSmallBtn" class="px-2.5 py-0.5 text-[#c6c6c6] hover:text-white">Small/Mid</button>
        </div>

        <div class="relative w-44 sm:w-56">
          <input type="text" id="searchInput" placeholder="Search museum, city..." class="w-full bg-[#262626] border border-[#525252] px-2.5 py-1 text-xs text-[#f4f4f4] placeholder-[#8d8d8d] focus:outline-none focus:border-[#0f62fe] transition" />
          <button id="clearSearchBtn" class="hidden absolute right-2 top-1 text-[#8d8d8d] hover:text-white text-xs">✕</button>
        </div>
      </div>

    </div>
  </section>

  <!-- ACTIVE FILTER TAGS -->
  <section id="filterTagsBar" class="hidden px-4 py-1.5 bg-[#161616] border-b border-[#393939] text-xs font-mono">
    <div class="max-w-7xl mx-auto flex items-center gap-2 flex-wrap">
      <span class="text-[#8d8d8d] text-[11px]">ACTIVE:</span>
      <div id="filterTagsContainer" class="flex items-center gap-1.5 flex-wrap"></div>
      <button id="clearAllFiltersBtn" class="text-[#78a9ff] hover:underline text-[11px] ml-2">Reset all</button>
    </div>
  </section>

  <!-- MAIN AREA -->
  <main class="flex-1 flex flex-col relative overflow-hidden bg-[#161616]">
    
    <!-- 3D GLOBE VIEW -->
    <div id="globeViewContainer" class="flex-1 flex flex-col md:flex-row relative">
      
      <!-- Interactive 3D Canvas Area (No Glow, Clean Precision Cartography) -->
      <div class="flex-1 relative flex items-center justify-center bg-[#161616] overflow-hidden min-h-[500px]">
        <canvas id="globeCanvas" width="900" height="700" class="max-w-full max-h-full"></canvas>

        <!-- Top Cities Quick Navigation Toolbar -->
        <div class="absolute top-3 left-4 right-4 flex items-center gap-1.5 overflow-x-auto pb-1 z-20 pointer-events-auto font-mono text-[11px]">
          <span class="text-[#8d8d8d] whitespace-nowrap bg-[#262626] px-2 py-0.5 border border-[#393939]">
            CITIES:
          </span>
          <div class="flex items-center gap-1 flex-nowrap">
            <button class="city-shortcut px-2 py-0.5 bg-[#262626] hover:bg-[#393939] border border-[#393939] hover:border-[#0f62fe] text-[#f4f4f4] transition flex items-center gap-1" data-city="New York">
              <span>New York</span> <span class="text-[#0f62fe] text-[10px]">11</span>
            </button>
            <button class="city-shortcut px-2 py-0.5 bg-[#262626] hover:bg-[#393939] border border-[#393939] hover:border-[#0f62fe] text-[#f4f4f4] transition flex items-center gap-1" data-city="London">
              <span>London</span> <span class="text-[#0f62fe] text-[10px]">8</span>
            </button>
            <button class="city-shortcut px-2 py-0.5 bg-[#262626] hover:bg-[#393939] border border-[#393939] hover:border-[#0f62fe] text-[#f4f4f4] transition flex items-center gap-1" data-city="Berlin">
              <span>Berlin</span> <span class="text-[#0f62fe] text-[10px]">4</span>
            </button>
            <button class="city-shortcut px-2 py-0.5 bg-[#262626] hover:bg-[#393939] border border-[#393939] hover:border-[#0f62fe] text-[#f4f4f4] transition flex items-center gap-1" data-city="Paris">
              <span>Paris</span> <span class="text-[#0f62fe] text-[10px]">4</span>
            </button>
            <button class="city-shortcut px-2 py-0.5 bg-[#262626] hover:bg-[#393939] border border-[#393939] hover:border-[#0f62fe] text-[#f4f4f4] transition flex items-center gap-1" data-city="Tokyo">
              <span>Tokyo</span> <span class="text-[#0f62fe] text-[10px]">3</span>
            </button>
          </div>
        </div>

        <!-- Carbon Controls (Sharp square buttons) -->
        <div class="absolute bottom-4 left-4 flex flex-col gap-1 bg-[#262626] border border-[#393939] p-1 z-20">
          <button id="zoomInBtn" class="w-7 h-7 bg-[#161616] hover:bg-[#393939] text-[#f4f4f4] flex items-center justify-center font-bold text-xs transition" title="Zoom In">+</button>
          <button id="zoomOutBtn" class="w-7 h-7 bg-[#161616] hover:bg-[#393939] text-[#f4f4f4] flex items-center justify-center font-bold text-xs transition" title="Zoom Out">−</button>
          <button id="resetViewBtn" class="w-7 h-7 bg-[#161616] hover:bg-[#393939] text-[#f4f4f4] flex items-center justify-center text-xs transition" title="Center View">◎</button>
          <button id="spinToggleBtn" class="w-7 h-7 bg-[#161616] hover:bg-[#393939] text-[#0f62fe] flex items-center justify-center text-xs transition" title="Toggle Auto-Spin">↻</button>
        </div>

        <!-- Carbon Metrics Footer -->
        <div class="absolute bottom-4 right-4 hidden sm:flex items-center gap-3 bg-[#262626] border border-[#393939] px-3 py-1 text-[11px] font-mono text-[#8d8d8d] z-20">
          <span id="globeStatus">Drag to rotate · City & Country labels visible</span>
          <span class="text-[#393939]">|</span>
          <span id="visibleCount" class="text-[#f4f4f4] font-medium">{len(institutions)} mapped</span>
        </div>

        <!-- Tooltip -->
        <div id="globeTooltip" class="absolute pointer-events-none hidden z-30 bg-[#262626] border border-[#525252] text-[#f4f4f4] px-2.5 py-1.5 text-xs shadow-lg font-mono">
          <div id="tooltipName" class="font-semibold text-white"></div>
          <div id="tooltipMeta" class="text-[11px] text-[#c6c6c6]"></div>
        </div>
      </div>

      <!-- Right Dossier Panel (Carbon Layer 01) -->
      <aside id="dossierPanel" class="w-full md:w-96 border-t md:border-t-0 md:border-l border-[#393939] bg-[#262626] flex flex-col z-20">
        <div class="p-3 border-b border-[#393939] flex items-center justify-between bg-[#1f1f1f]">
          <h2 class="text-xs font-semibold uppercase tracking-wider text-[#f4f4f4] flex items-center gap-1.5 font-mono">
            <span>🏛️</span> Institutional Dossier
          </h2>
          <span id="dossierTierBadge" class="hidden text-[10px] font-mono font-semibold px-2 py-0.5 border"></span>
        </div>

        <div id="dossierContent" class="p-4 flex-1 flex flex-col justify-center text-[#8d8d8d] text-xs overflow-y-auto">
          <div class="text-center py-10">
            <div class="w-10 h-10 mx-auto bg-[#161616] border border-[#393939] flex items-center justify-center text-base mb-2 text-[#0f62fe]">
              🏛️
            </div>
            <p class="font-medium text-[#f4f4f4]">No institution selected</p>
            <p class="text-[11px] text-[#8d8d8d] mt-1 max-w-[220px] mx-auto">
              Select any city pill, country, or institution dot on the globe to inspect its ethical funding profile.
            </p>
          </div>
        </div>
      </aside>

    </div>

    <!-- TABLE / LIST VIEW (Carbon Data Table) -->
    <div id="listViewContainer" class="hidden flex-1 overflow-auto p-4 max-w-7xl mx-auto w-full">
      <div class="border border-[#393939] bg-[#262626] overflow-hidden">
        <table class="w-full text-left text-xs text-[#c6c6c6]">
          <thead class="bg-[#1f1f1f] text-[#f4f4f4] uppercase font-semibold text-[11px] border-b border-[#393939] font-mono">
            <tr>
              <th class="p-3">Institution</th>
              <th class="p-3">City</th>
              <th class="p-3">Country</th>
              <th class="p-3">Tier</th>
              <th class="p-3">Size</th>
              <th class="p-3">Funding Breakdown</th>
              <th class="p-3">Watch / Notes</th>
              <th class="p-3">Sources</th>
            </tr>
          </thead>
          <tbody id="tableBody" class="divide-y divide-[#393939]">
            <!-- populated by JS -->
          </tbody>
        </table>
      </div>
    </div>

  </main>

  <!-- CONCIERGE CHAT OVERLAY (Carbon Modal) -->
  <div id="conciergeModal" class="fixed bottom-5 right-5 w-[92vw] sm:w-[470px] h-[600px] max-h-[85vh] bg-[#262626] border border-[#525252] shadow-2xl flex flex-col z-50 transition-all duration-200 transform translate-y-3 opacity-0 pointer-events-none">
    
    <div class="p-3 border-b border-[#393939] flex items-center justify-between bg-[#1f1f1f]">
      <div class="flex items-center gap-2">
        <div class="w-2.5 h-2.5 bg-[#0f62fe]"></div>
        <div>
          <h3 class="text-xs font-semibold text-white tracking-wide font-mono">Atlas Concierge</h3>
          <span class="text-[9px] uppercase px-1.5 py-0.2 bg-[#161616] text-[#c6c6c6] border border-[#393939] font-mono">
            IBM Carbon Engine
          </span>
        </div>
      </div>
      <div class="flex items-center gap-1">
        <button id="chatClearBtn" class="text-[#8d8d8d] hover:text-white px-1.5 py-0.5 text-xs font-mono" title="Clear chat">Clear</button>
        <button id="chatCloseBtn" class="text-[#8d8d8d] hover:text-white px-1.5 py-0.5 text-xs font-mono" title="Close">✕</button>
      </div>
    </div>

    <div id="chatMessages" class="flex-1 overflow-y-auto p-3.5 space-y-3 text-xs bg-[#161616]">
      <div class="flex flex-col gap-1 items-start">
        <div class="bg-[#262626] border border-[#393939] text-[#f4f4f4] p-3 max-w-[94%] leading-relaxed">
          <p class="font-semibold text-white mb-1">Hello. I am the Culture Atlas Concierge.</p>
          <p class="text-[#c6c6c6]">
            Ask for research on <strong>MoMA</strong>, query institutions across <strong>{len(sorted_cities)} cities</strong>, or inquire why museums like the <strong>British Museum</strong> or <strong>Louvre</strong> are flagged or omitted.
          </p>
          <div class="mt-3 flex flex-col gap-1.5 font-mono text-[11px]">
            <button class="chat-preset text-left px-2.5 py-1.5 bg-[#161616] hover:bg-[#333333] border border-[#525252] text-[#f1c21b] transition">
              🔍 Why are some museums not on the map?
            </button>
            <button class="chat-preset text-left px-2.5 py-1.5 bg-[#161616] hover:bg-[#333333] border border-[#393939] text-[#f4f4f4] transition">
              🏛️ Tell research about MoMA
            </button>
            <button class="chat-preset text-left px-2.5 py-1.5 bg-[#161616] hover:bg-[#333333] border border-[#393939] text-[#c6c6c6] transition">
              🇬🇧 British Museum (BP / Restitution)
            </button>
            <button class="chat-preset text-left px-2.5 py-1.5 bg-[#161616] hover:bg-[#333333] border border-[#393939] text-[#c6c6c6] transition">
              🇫🇷 Musée du Louvre (Franchise Scrutiny)
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Chat Input Bar -->
    <div class="p-2.5 border-t border-[#393939] bg-[#262626] flex items-center gap-1.5">
      <input type="text" id="chatInput" placeholder="Ask: 'MoMA', 'why not on the map', 'London'..." class="flex-1 bg-[#161616] border border-[#525252] px-3 py-1.5 text-xs text-[#f4f4f4] placeholder-[#8d8d8d] focus:outline-none focus:border-[#0f62fe] transition" />
      <button id="chatSendBtn" class="px-3.5 py-1.5 bg-[#0f62fe] hover:bg-[#0353e9] text-white font-medium text-xs transition font-mono">
        Send
      </button>
    </div>

  </div>

  <!-- APPLICATION SCRIPTS -->
  <script>
    const ALL_INSTITUTIONS = {json.dumps(institutions)};
    const WORLD_ARCS = {json.dumps(arcs_downsampled)};
    const COUNTRY_LIST = {json.dumps(country_list)};
    const CITY_LIST = {json.dumps(sorted_cities)};
    const PENDING_MUSEUMS = {json.dumps(PENDING_MUSEUMS)};
    const COUNTRY_CENTROIDS = {json.dumps(COUNTRY_CENTROIDS)};

    let selectedTier = 'all';
    let selectedSize = 'all';
    let selectedCountry = 'all';
    let selectedCity = 'all';
    let searchQuery = '';
    let selectedInstitution = null;
    let hoveredInstitution = null;

    // View Switching
    const viewGlobeBtn = document.getElementById('viewGlobeBtn');
    const viewListBtn = document.getElementById('viewListBtn');
    const globeViewContainer = document.getElementById('globeViewContainer');
    const listViewContainer = document.getElementById('listViewContainer');

    viewGlobeBtn.addEventListener('click', () => {{
      viewGlobeBtn.className = 'px-3 py-1 font-medium transition bg-[#0f62fe] text-white';
      viewListBtn.className = 'px-3 py-1 font-medium text-[#c6c6c6] hover:text-white transition';
      globeViewContainer.classList.remove('hidden');
      listViewContainer.classList.add('hidden');
    }});

    viewListBtn.addEventListener('click', () => {{
      viewListBtn.className = 'px-3 py-1 font-medium transition bg-[#0f62fe] text-white';
      viewGlobeBtn.className = 'px-3 py-1 font-medium text-[#c6c6c6] hover:text-white transition';
      listViewContainer.classList.remove('hidden');
      globeViewContainer.classList.add('hidden');
      renderTable();
    }});

    // Populate Dropdowns
    const countrySelect = document.getElementById('countrySelect');
    COUNTRY_LIST.filter(c => c.count > 0).forEach(c => {{
      const opt = document.createElement('option');
      opt.value = c.name;
      opt.textContent = `${{c.name}} (${{c.count}})`;
      countrySelect.appendChild(opt);
    }});

    const citySelect = document.getElementById('citySelect');
    CITY_LIST.forEach(cty => {{
      const opt = document.createElement('option');
      opt.value = cty.name;
      opt.textContent = `${{cty.name}} (${{cty.count}})`;
      citySelect.appendChild(opt);
    }});

    countrySelect.addEventListener('change', e => setCountryFilter(e.target.value));
    citySelect.addEventListener('change', e => setCityFilter(e.target.value));

    document.querySelectorAll('.city-shortcut').forEach(btn => {{
      btn.addEventListener('click', () => setCityFilter(btn.getAttribute('data-city')));
    }});

    function setCountryFilter(countryName) {{
      selectedCountry = countryName;
      countrySelect.value = countryName;
      if (countryName !== 'all') {{
        selectedCity = 'all';
        citySelect.value = 'all';
        const c = COUNTRY_LIST.find(x => x.name.toLowerCase() === countryName.toLowerCase());
        if (c) flyTo(c.lon, c.lat);
      }}
      applyFilters();
    }}

    function setCityFilter(cityName) {{
      selectedCity = cityName;
      citySelect.value = cityName;
      if (cityName !== 'all') {{
        const cty = CITY_LIST.find(x => x.name.toLowerCase() === cityName.toLowerCase());
        if (cty) {{
          selectedCountry = 'all';
          countrySelect.value = 'all';
          flyTo(cty.lon, cty.lat);
        }}
      }}
      applyFilters();
    }}

    // Tier filtering
    const tierChips = document.querySelectorAll('.tier-chip');
    tierChips.forEach(chip => {{
      chip.addEventListener('click', () => {{
        const t = chip.getAttribute('data-tier');
        selectedTier = (selectedTier === t) ? 'all' : t;
        updateTierButtons();
        applyFilters();
      }});
    }});

    function updateTierButtons() {{
      tierChips.forEach(chip => {{
        const t = chip.getAttribute('data-tier');
        chip.style.opacity = (selectedTier === 'all' || selectedTier === t) ? '1' : '0.35';
      }});
    }}

    // Size filtering
    const sizeAllBtn = document.getElementById('sizeAllBtn');
    const sizeLargeBtn = document.getElementById('sizeLargeBtn');
    const sizeSmallBtn = document.getElementById('sizeSmallBtn');

    function setSizeFilter(size) {{
      selectedSize = size;
      [sizeAllBtn, sizeLargeBtn, sizeSmallBtn].forEach(b => {{
        b.className = 'px-2.5 py-0.5 text-[#c6c6c6] hover:text-white';
      }});
      if (size === 'all') sizeAllBtn.className = 'px-2.5 py-0.5 text-white bg-[#0f62fe] font-medium';
      if (size === 'L') sizeLargeBtn.className = 'px-2.5 py-0.5 text-white bg-[#0f62fe] font-medium';
      if (size === 'S') sizeSmallBtn.className = 'px-2.5 py-0.5 text-white bg-[#0f62fe] font-medium';
      applyFilters();
    }}

    sizeAllBtn.addEventListener('click', () => setSizeFilter('all'));
    sizeLargeBtn.addEventListener('click', () => setSizeFilter('L'));
    sizeSmallBtn.addEventListener('click', () => setSizeFilter('S'));

    // Search query
    const searchInput = document.getElementById('searchInput');
    const clearSearchBtn = document.getElementById('clearSearchBtn');

    searchInput.addEventListener('input', e => {{
      searchQuery = e.target.value.toLowerCase().trim();
      clearSearchBtn.classList.toggle('hidden', searchQuery === '');
      applyFilters();
    }});

    clearSearchBtn.addEventListener('click', () => {{
      searchInput.value = '';
      searchQuery = '';
      clearSearchBtn.classList.add('hidden');
      applyFilters();
    }});

    const filterTagsBar = document.getElementById('filterTagsBar');
    const filterTagsContainer = document.getElementById('filterTagsContainer');
    const clearAllFiltersBtn = document.getElementById('clearAllFiltersBtn');

    clearAllFiltersBtn.addEventListener('click', () => {{
      selectedTier = 'all';
      selectedSize = 'all';
      selectedCountry = 'all';
      selectedCity = 'all';
      countrySelect.value = 'all';
      citySelect.value = 'all';
      searchQuery = '';
      searchInput.value = '';
      clearSearchBtn.classList.add('hidden');
      updateTierButtons();
      setSizeFilter('all');
      applyFilters();
    }});

    let filteredInstitutions = ALL_INSTITUTIONS.slice();

    function applyFilters() {{
      filteredInstitutions = ALL_INSTITUTIONS.filter(inst => {{
        if (selectedTier !== 'all' && inst.tier !== selectedTier) return false;
        if (selectedSize !== 'all' && inst.size !== selectedSize) return false;
        if (selectedCountry !== 'all' && inst.country.toLowerCase() !== selectedCountry.toLowerCase()) return false;
        if (selectedCity !== 'all' && inst.city.toLowerCase() !== selectedCity.toLowerCase()) return false;
        if (searchQuery) {{
          const q = searchQuery;
          const matchName = inst.name.toLowerCase().includes(q);
          const matchLoc = inst.location.toLowerCase().includes(q);
          const matchFunding = (inst.funding || '').toLowerCase().includes(q);
          const matchWatch = (inst.watch || '').toLowerCase().includes(q);
          const matchAliases = (inst.aliases || []).some(a => a.toLowerCase().includes(q));
          if (!matchName && !matchLoc && !matchFunding && !matchWatch && !matchAliases) return false;
        }}
        return true;
      }});

      document.getElementById('visibleCount').textContent = `${{filteredInstitutions.length}} mapped`;

      const tags = [];
      if (selectedCountry !== 'all') tags.push({{ label: `COUNTRY: ${{selectedCountry}}`, clear: () => setCountryFilter('all') }});
      if (selectedCity !== 'all') tags.push({{ label: `CITY: ${{selectedCity}}`, clear: () => setCityFilter('all') }});
      if (selectedTier !== 'all') tags.push({{ label: `TIER: ${{selectedTier === 'A' ? 'Verified' : selectedTier === 'B' ? 'One Name' : 'Unverified'}}`, clear: () => {{ selectedTier = 'all'; updateTierButtons(); applyFilters(); }} }});
      if (selectedSize !== 'all') tags.push({{ label: `SIZE: ${{selectedSize === 'L' ? 'Large' : 'Small/Mid'}}`, clear: () => setSizeFilter('all') }});
      if (searchQuery) tags.push({{ label: `QUERY: "${{searchQuery}}"`, clear: () => {{ searchInput.value = ''; searchQuery = ''; clearSearchBtn.classList.add('hidden'); applyFilters(); }} }});

      if (tags.length > 0) {{
        filterTagsBar.classList.remove('hidden');
        filterTagsContainer.innerHTML = tags.map((t, idx) => `
          <span class="inline-flex items-center gap-1.5 px-2 py-0.5 bg-[#262626] text-[#f4f4f4] border border-[#525252] text-[10.5px]">
            ${{t.label}}
            <button class="remove-tag text-[#8d8d8d] hover:text-white" data-idx="${{idx}}">✕</button>
          </span>
        `).join('');
        filterTagsContainer.querySelectorAll('.remove-tag').forEach(b => {{
          b.addEventListener('click', () => {{
            const idx = parseInt(b.getAttribute('data-idx'), 10);
            tags[idx].clear();
          }});
        }});
      }} else {{
        filterTagsBar.classList.add('hidden');
      }}

      if (!listViewContainer.classList.contains('hidden')) {{
        renderTable();
      }}
    }}

    // Table Renderer
    function renderTable() {{
      const tbody = document.getElementById('tableBody');
      if (filteredInstitutions.length === 0) {{
        tbody.innerHTML = `<tr><td colspan="8" class="text-center py-10 text-[#8d8d8d]">No institutions match filters.</td></tr>`;
        return;
      }}
      tbody.innerHTML = filteredInstitutions.map(inst => `
        <tr class="hover:bg-[#262626] transition cursor-pointer" onclick="handleTableSelect('${{inst.name.replace(/'/g, "\\\\'")}}')">
          <td class="p-3 font-semibold text-white">${{inst.name}}</td>
          <td class="p-3 text-[#c6c6c6] font-mono text-[11px]">${{inst.city}}</td>
          <td class="p-3 text-[#8d8d8d] font-mono text-[11px]">${{inst.country}}</td>
          <td class="p-3">
            <span class="inline-block px-2 py-0.5 text-[10px] font-mono font-bold border ${{inst.tier === 'A' ? 'bg-[#132c1c] text-[#24a148] border-[#24a148]' : inst.tier === 'B' ? 'bg-[#0f284c] text-[#4589ff] border-[#4589ff]' : 'bg-[#262626] text-[#8d8d8d] border-[#525252]'}}">
              ${{inst.tier === 'A' ? 'Verified' : inst.tier === 'B' ? 'One Name' : 'Unverified'}}
            </span>
          </td>
          <td class="p-3 text-[#8d8d8d] text-xs font-mono">${{inst.size === 'L' ? 'Large' : 'Small/Mid'}}</td>
          <td class="p-3 text-[#c6c6c6] max-w-xs truncate" title="${{inst.funding}}">${{inst.funding}}</td>
          <td class="p-3 text-[#8d8d8d] max-w-xs truncate" title="${{inst.watch || ''}}">${{inst.watch || '—'}}</td>
          <td class="p-3 font-mono">
            ${{(inst.sources || []).map(u => `<a href="${{u}}" target="_blank" class="text-[#78a9ff] hover:underline mr-1 text-xs">↗</a>`).join('')}}
          </td>
        </tr>
      `).join('');
    }}

    window.handleTableSelect = function(name) {{
      const inst = ALL_INSTITUTIONS.find(i => i.name === name);
      if (inst) {{
        viewGlobeBtn.click();
        selectInstitution(inst);
      }}
    }};

    function addAndPlotInstitution(instData) {{
      let existing = ALL_INSTITUTIONS.find(i => i.name.toLowerCase() === instData.name.toLowerCase());
      if (!existing) {{
        ALL_INSTITUTIONS.push(instData);
        filteredInstitutions.push(instData);
        existing = instData;
        const vc = document.getElementById('visibleCount');
        if (vc) vc.textContent = `${{filteredInstitutions.length}} mapped`;
      }}
      viewGlobeBtn.click();
      selectInstitution(existing);
    }}

    // 3D Canvas Globe (Pure IBM Carbon Colors - No Glow - Names Cities & Countries)
    const canvas = document.getElementById('globeCanvas');
    const ctx = canvas.getContext('2d');
    let rotLon = 0;
    let rotLat = 20;
    let targetRotLon = 0;
    let targetRotLat = 20;
    let isFlying = false;
    let flightProgress = 0;
    let isAutoSpinning = true;
    let isDragging = false;
    let lastX = 0, lastY = 0;
    let globeRadius = 260;

    function resizeCanvas() {{
      const rect = canvas.parentElement.getBoundingClientRect();
      const w = Math.min(rect.width, 1100);
      const h = Math.max(500, rect.height);
      canvas.width = w;
      canvas.height = h;
      globeRadius = Math.min(w, h) * 0.42;
    }}
    window.addEventListener('resize', resizeCanvas);
    resizeCanvas();

    function project(lon, lat, r, cx, cy) {{
      const rad = Math.PI / 180;
      const lambda = (lon - rotLon) * rad;
      const phi = lat * rad;
      const phi0 = rotLat * rad;

      const cosC = Math.sin(phi0) * Math.sin(phi) + Math.cos(phi0) * Math.cos(phi) * Math.cos(lambda);
      if (cosC < 0) return null;

      const x = cx + r * Math.cos(phi) * Math.sin(lambda);
      const y = cy - r * (Math.cos(phi0) * Math.sin(phi) - Math.sin(phi0) * Math.cos(phi) * Math.cos(lambda));
      return {{ x, y, depth: cosC }};
    }}

    function renderGlobe() {{
      const w = canvas.width;
      const h = canvas.height;
      const cx = w / 2;
      const cy = h / 2;
      const r = globeRadius;

      ctx.clearRect(0, 0, w, h);

      if (isFlying) {{
        flightProgress += 0.04;
        if (flightProgress >= 1) {{
          flightProgress = 1;
          isFlying = false;
        }}
        const ease = 1 - Math.pow(1 - flightProgress, 3);
        rotLon = rotLon + (targetRotLon - rotLon) * ease;
        rotLat = rotLat + (targetRotLat - rotLat) * ease;
      }} else if (isAutoSpinning && !isDragging) {{
        rotLon = (rotLon + 0.22) % 360;
      }}

      // Solid IBM Carbon Sphere (NO glow, NO outer radial haze)
      ctx.fillStyle = '#121619';
      ctx.beginPath();
      ctx.arc(cx, cy, r, 0, Math.PI * 2);
      ctx.fill();

      // Clip inside globe
      ctx.save();
      ctx.beginPath();
      ctx.arc(cx, cy, r, 0, Math.PI * 2);
      ctx.clip();

      // Faint Carbon Graticules
      ctx.strokeStyle = 'rgba(141, 141, 141, 0.12)';
      ctx.lineWidth = 0.5;
      [-60, -30, 0, 30, 60].forEach(lat => {{
        ctx.beginPath();
        let first = true;
        for (let lon = -180; lon <= 180; lon += 8) {{
          const pt = project(lon, lat, r, cx, cy);
          if (pt) {{
            if (first) {{ ctx.moveTo(pt.x, pt.y); first = false; }}
            else {{ ctx.lineTo(pt.x, pt.y); }}
          }} else {{ first = true; }}
        }}
        ctx.stroke();
      }});

      for (let lon = -180; lon < 180; lon += 30) {{
        ctx.beginPath();
        let first = true;
        for (let lat = -80; lat <= 80; lat += 8) {{
          const pt = project(lon, lat, r, cx, cy);
          if (pt) {{
            if (first) {{ ctx.moveTo(pt.x, pt.y); first = false; }}
            else {{ ctx.lineTo(pt.x, pt.y); }}
          }} else {{ first = true; }}
        }}
        ctx.stroke();
      }}

      // 🌍 Draw Country Boundaries (Sharp 0.8px, NO glow)
      ctx.strokeStyle = '#525252';
      ctx.lineWidth = 0.85;
      WORLD_ARCS.forEach(arc => {{
        ctx.beginPath();
        let first = true;
        for (let i = 0; i < arc.length; i++) {{
          const pt = project(arc[i][0], arc[i][1], r, cx, cy);
          if (pt) {{
            if (first) {{ ctx.moveTo(pt.x, pt.y); first = false; }}
            else {{ ctx.lineTo(pt.x, pt.y); }}
          }} else {{
            first = true;
          }}
        }}
        ctx.stroke();
      }});

      // 🏷️ NAME COUNTRIES on the Globe
      COUNTRY_CENTROIDS.forEach(c => {{
        const pt = project(c.lon, c.lat, r, cx, cy);
        if (pt && pt.depth > 0.22) {{
          ctx.font = '600 9.5px "IBM Plex Sans", sans-serif';
          ctx.fillStyle = 'rgba(141, 141, 141, 0.65)'; // Carbon Gray 50
          ctx.textAlign = 'center';
          ctx.textBaseline = 'middle';
          ctx.fillText(c.name, pt.x, pt.y);
        }}
      }});

      // 🏙️ NAME CITIES on the Globe
      CITY_LIST.forEach(cty => {{
        const pt = project(cty.lon, cty.lat, r, cx, cy);
        if (pt && pt.depth > 0.28) {{
          const isSelected = selectedCity.toLowerCase() === cty.name.toLowerCase();
          const isMajor = cty.count >= 3 || isSelected;

          if (isMajor || globeRadius > 320) {{
            // Carbon square marker
            ctx.fillStyle = isSelected ? '#f1c21b' : '#8d8d8d';
            ctx.fillRect(pt.x - 1.5, pt.y - 1.5, 3, 3);

            // City label
            ctx.font = (isSelected ? '600 11px' : '500 9.5px') + ' "IBM Plex Sans", sans-serif';
            ctx.fillStyle = isSelected ? '#ffffff' : '#c6c6c6';
            ctx.textAlign = 'left';
            ctx.textBaseline = 'middle';
            ctx.fillText(cty.name, pt.x + 5, pt.y);
          }}
        }}
      }});

      // Selected City Square Highlight
      if (selectedCity !== 'all') {{
        const cty = CITY_LIST.find(c => c.name.toLowerCase() === selectedCity.toLowerCase());
        if (cty) {{
          const pt = project(cty.lon, cty.lat, r, cx, cy);
          if (pt) {{
            ctx.strokeStyle = '#f1c21b'; // Carbon Yellow 30
            ctx.lineWidth = 1.5;
            ctx.strokeRect(pt.x - 8, pt.y - 8, 16, 16);
          }}
        }}
      }}

      ctx.restore();

      // Sharp Carbon Globe Rim (NO glowing bloom)
      ctx.strokeStyle = '#393939';
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.arc(cx, cy, r, 0, Math.PI * 2);
      ctx.stroke();

      // Institution Dots (Solid IBM Carbon colors, zero shadowBlur)
      filteredInstitutions.forEach(inst => {{
        const pt = project(inst.lon, inst.lat, r, cx, cy);
        if (!pt) return;

        const isSel = selectedInstitution && selectedInstitution.name === inst.name;
        const isHov = hoveredInstitution && hoveredInstitution.name === inst.name;
        const dotR = (isSel ? 6.5 : isHov ? 5.5 : inst.size === 'L' ? 4 : 2.8) * Math.min(1.3, Math.max(0.7, pt.depth));

        // Carbon Data Palette
        let col = '#24a148'; // Verified: Carbon Green 50
        if (inst.tier === 'B') col = '#4589ff'; // One Name: Carbon Blue 50
        if (inst.tier === 'U') col = '#8d8d8d'; // Unverified: Carbon Gray 50
        if (inst.why_not_on_map) col = '#f1c21b'; // Audited/Pending: Carbon Yellow 30

        if (isSel) {{
          ctx.beginPath();
          ctx.arc(pt.x, pt.y, dotR + 3, 0, Math.PI * 2);
          ctx.strokeStyle = '#ffffff';
          ctx.lineWidth = 1.5;
          ctx.stroke();
        }}

        ctx.beginPath();
        ctx.arc(pt.x, pt.y, dotR, 0, Math.PI * 2);
        ctx.fillStyle = col;
        ctx.fill();
      }});

      requestAnimationFrame(renderGlobe);
    }}
    requestAnimationFrame(renderGlobe);

    function flyTo(lon, lat) {{
      isAutoSpinning = false;
      let dLon = (lon - rotLon) % 360;
      if (dLon > 180) dLon -= 360;
      if (dLon < -180) dLon += 360;
      targetRotLon = rotLon + dLon;
      targetRotLat = Math.max(-75, Math.min(75, lat));
      flightProgress = 0;
      isFlying = true;
    }}

    function selectInstitution(inst) {{
      selectedInstitution = inst;
      flyTo(inst.lon, inst.lat);

      const dossierContent = document.getElementById('dossierContent');
      const badge = document.getElementById('dossierTierBadge');

      badge.classList.remove('hidden');
      badge.textContent = inst.tier === 'A' ? 'Tier A · Verified' : inst.tier === 'B' ? 'Tier B · One Name' : 'Tier U · Unverified';
      badge.className = `text-[10px] font-mono font-bold px-2 py-0.5 border ${{inst.tier === 'A' ? 'bg-[#132c1c] text-[#24a148] border-[#24a148]' : inst.tier === 'B' ? 'bg-[#0f284c] text-[#4589ff] border-[#4589ff]' : 'bg-[#262626] text-[#8d8d8d] border-[#525252]'}}`;

      dossierContent.innerHTML = `
        <div class="space-y-3.5">
          <div>
            <h3 class="font-bold text-white text-base leading-snug">${{inst.name}}</h3>
            <p class="text-xs text-[#0f62fe] mt-1 flex items-center gap-1 font-mono">
              <span>📍</span> <span>${{inst.location}}</span>
              <span class="text-[#525252]">·</span>
              <span class="text-[#c6c6c6]">${{inst.size === 'L' ? 'Large (>$20M)' : 'Small/Mid'}}</span>
            </p>
          </div>

          <div class="bg-[#161616] p-3 border border-[#393939] space-y-1">
            <span class="text-[10px] font-mono font-bold text-[#24a148] uppercase tracking-wider block">Funding Architecture</span>
            <p class="text-xs text-[#c6c6c6] leading-relaxed">${{inst.funding}}</p>
          </div>

          ${{inst.watch ? `
            <div class="bg-[#161616] p-3 border border-[#393939] space-y-1">
              <span class="text-[10px] font-mono font-bold text-[#4589ff] uppercase tracking-wider block">Watch Notes & Scrutiny</span>
              <p class="text-xs text-[#c6c6c6] leading-relaxed">${{inst.watch}}</p>
            </div>
          ` : ''}}

          ${{inst.why_not_on_map ? `
            <div class="bg-[#161616] p-3 border border-[#f1c21b] space-y-1">
              <span class="text-[10px] font-mono font-bold text-[#f1c21b] uppercase tracking-wider block">⚠️ Atlas Inclusion Status</span>
              <p class="text-xs text-[#f4f4f4] leading-relaxed">${{inst.why_not_on_map}}</p>
            </div>
          ` : ''}}

          <div class="pt-2 border-t border-[#393939]">
            <span class="text-[10px] font-mono font-bold text-[#8d8d8d] uppercase tracking-wider block mb-2">Sources & Filings</span>
            <div class="flex flex-col gap-1.5 font-mono">
              ${{(inst.sources || []).map(u => {{
                let domain = u;
                try {{ domain = new URL(u).hostname.replace(/^www\\./, ''); }} catch(e){{}}
                return `<a href="${{u}}" target="_blank" class="text-[#78a9ff] hover:underline text-xs flex items-center gap-1"><span>↗</span> <span>${{domain}}</span></a>`;
              }}).join('')}}
            </div>
          </div>
        </div>
      `;
    }}

    // Pointer events
    canvas.addEventListener('pointerdown', e => {{
      isDragging = true;
      canvas.classList.add('dragging');
      lastX = e.clientX;
      lastY = e.clientY;
      isFlying = false;
      isAutoSpinning = false;
    }});

    window.addEventListener('pointermove', e => {{
      const rect = canvas.getBoundingClientRect();
      const mx = e.clientX - rect.left;
      const my = e.clientY - rect.top;

      if (isDragging) {{
        const dx = e.clientX - lastX;
        const dy = e.clientY - lastY;
        lastX = e.clientX;
        lastY = e.clientY;

        rotLon = (rotLon - dx * 0.5) % 360;
        rotLat = Math.max(-75, Math.min(75, rotLat + dy * 0.5));
      }} else {{
        const cx = canvas.width / 2;
        const cy = canvas.height / 2;
        const r = globeRadius;

        let hit = null;
        for (let i = 0; i < filteredInstitutions.length; i++) {{
          const inst = filteredInstitutions[i];
          const pt = project(inst.lon, inst.lat, r, cx, cy);
          if (pt && Math.hypot(pt.x - mx, pt.y - my) < 9) {{
            hit = inst;
            break;
          }}
        }}

        hoveredInstitution = hit;
        const tooltip = document.getElementById('globeTooltip');
        if (hit) {{
          tooltip.classList.remove('hidden');
          tooltip.style.left = `${{mx + 12}}px`;
          tooltip.style.top = `${{my + 8}}px`;
          document.getElementById('tooltipName').textContent = hit.name;
          document.getElementById('tooltipMeta').textContent = `${{hit.city}}, ${{hit.country}} · ${{hit.tier === 'A' ? 'Verified' : 'One Name'}}`;
          canvas.style.cursor = 'pointer';
        }} else {{
          tooltip.classList.add('hidden');
          canvas.style.cursor = 'grab';
        }}
      }}
    }});

    window.addEventListener('pointerup', () => {{
      if (isDragging) {{
        isDragging = false;
        canvas.classList.remove('dragging');
      }}
    }});

    canvas.addEventListener('click', () => {{
      if (hoveredInstitution) {{
        selectInstitution(hoveredInstitution);
      }}
    }});

    // Controls
    document.getElementById('zoomInBtn').addEventListener('click', () => {{
      globeRadius = Math.min(canvas.width, canvas.height) * 0.7;
    }});
    document.getElementById('zoomOutBtn').addEventListener('click', () => {{
      globeRadius = Math.min(canvas.width, canvas.height) * 0.3;
    }});
    document.getElementById('resetViewBtn').addEventListener('click', () => {{
      globeRadius = Math.min(canvas.width, canvas.height) * 0.42;
      flyTo(0, 20);
      setCountryFilter('all');
      setCityFilter('all');
    }});
    document.getElementById('spinToggleBtn').addEventListener('click', () => {{
      isAutoSpinning = !isAutoSpinning;
    }});

    // Concierge Dialog
    const conciergeModal = document.getElementById('conciergeModal');
    const toggleConciergeBtn = document.getElementById('toggleConciergeBtn');
    const chatCloseBtn = document.getElementById('chatCloseBtn');
    const chatMessages = document.getElementById('chatMessages');
    const chatInput = document.getElementById('chatInput');
    const chatSendBtn = document.getElementById('chatSendBtn');
    const chatClearBtn = document.getElementById('chatClearBtn');

    function openConcierge() {{
      conciergeModal.classList.remove('pointer-events-none', 'opacity-0', 'translate-y-3');
      conciergeModal.classList.add('opacity-100', 'translate-y-0');
      setTimeout(() => chatInput.focus(), 150);
    }}

    function closeConcierge() {{
      conciergeModal.classList.add('pointer-events-none', 'opacity-0', 'translate-y-3');
      conciergeModal.classList.remove('opacity-100', 'translate-y-0');
    }}

    toggleConciergeBtn.addEventListener('click', openConcierge);
    chatCloseBtn.addEventListener('click', closeConcierge);

    window.addEventListener('keydown', e => {{
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') {{
        e.preventDefault();
        if (conciergeModal.classList.contains('opacity-100')) {{
          closeConcierge();
        }} else {{
          openConcierge();
        }}
      }}
    }});

    chatClearBtn.addEventListener('click', () => {{
      chatMessages.innerHTML = '';
      appendBotMessage("Chat history cleared. Inquire about any museum, controversy, or inclusion criteria.");
    }});

    document.querySelectorAll('.chat-preset').forEach(btn => {{
      btn.addEventListener('click', () => {{
        const text = btn.textContent.replace(/^[^\w]+/, '').trim();
        handleUserQuery(text);
      }});
    }});

    function appendUserMessage(text) {{
      const div = document.createElement('div');
      div.className = 'flex justify-end';
      div.innerHTML = `
        <div class="bg-[#0f62fe] text-white p-2.5 max-w-[85%] text-xs leading-relaxed font-mono">
          ${{text}}
        </div>
      `;
      chatMessages.appendChild(div);
      chatMessages.scrollTop = chatMessages.scrollHeight;
    }}

    function appendBotMessage(html, actions = []) {{
      const div = document.createElement('div');
      div.className = 'flex flex-col gap-1 items-start';

      let actionsHtml = '';
      if (actions.length > 0) {{
        actionsHtml = `
          <div class="mt-2.5 flex flex-wrap gap-1.5 font-mono">
            ${{actions.map((act, i) => `
              <button class="chat-act-btn px-2.5 py-1 text-[11px] font-medium flex items-center gap-1 border border-[#393939] bg-[#161616] text-[#f4f4f4] hover:bg-[#333333] transition" data-act-idx="${{i}}">
                ${{act.icon || '📍'}} ${{act.label}}
              </button>
            `).join('')}}
          </div>
        `;
      }}

      div.innerHTML = `
        <div class="bg-[#262626] border border-[#393939] text-[#f4f4f4] p-3 max-w-[94%] leading-relaxed">
          ${{html}}
          ${{actionsHtml}}
        </div>
      `;

      if (actions.length > 0) {{
        div.querySelectorAll('.chat-act-btn').forEach(btn => {{
          const idx = parseInt(btn.getAttribute('data-act-idx'), 10);
          btn.addEventListener('click', () => {{
            if (actions[idx] && actions[idx].handler) {{
              actions[idx].handler();
            }}
          }});
        }});
      }}

      chatMessages.appendChild(div);
      chatMessages.scrollTop = chatMessages.scrollHeight;
    }}

    function handleUserQuery(query) {{
      appendUserMessage(query);

      const typing = document.createElement('div');
      typing.id = 'typingIndicator';
      typing.className = 'p-2 bg-[#262626] text-[#8d8d8d] text-xs font-mono';
      typing.textContent = 'Auditing...';
      chatMessages.appendChild(typing);
      chatMessages.scrollTop = chatMessages.scrollHeight;

      setTimeout(() => {{
        typing.remove();
        runOfflineLogic(query);
      }}, 200);
    }}

    function findInstitution(rawQuery) {{
      const raw = rawQuery.toLowerCase().trim();

      for (const inst of ALL_INSTITUTIONS) {{
        const names = [inst.name.toLowerCase(), ...(inst.aliases || [])];
        for (const a of names) {{
          if (raw.includes(a) || (raw.length > 3 && a.includes(raw))) {{
            return inst;
          }}
        }}
      }}

      const stopWords = new Set(['tell', 'research', 'about', 'museum', 'the', 'a', 'an', 'what', 'who', 'how', 'is', 'are', 'in', 'at', 'on', 'show', 'me', 'details', 'info', 'it', 'need', 'to', 'give', 'any', 'why', 'map', 'not']);
      const tokens = raw.replace(/[?!.,;:'"()]/g, ' ').split(/\\s+/).filter(w => w.length >= 3 && !stopWords.has(w));

      for (const t of tokens) {{
        for (const inst of ALL_INSTITUTIONS) {{
          const names = [inst.name.toLowerCase(), ...(inst.aliases || [])];
          if (names.some(a => a.includes(t) || t.includes(a))) {{
            return inst;
          }}
        }}
      }}
      return null;
    }}

    function runOfflineLogic(query) {{
      const q = query.toLowerCase().trim();
      const actions = [];
      let response = '';

      const isGeneralCriteriaQuery = (q.includes('why') && (q.includes('not on the map') || q.includes('not on map') || q.includes('missing') || q.includes('criteria') || q.includes('how are') || q.includes('included') || q.includes('selection'))) || q.includes('criteria for') || q.includes('why it is not') || q.includes('why is it not') || q.includes('why not on the map') || q.includes('or any other museum');

      let matchPendingKey = null;
      for (const k of Object.keys(PENDING_MUSEUMS)) {{
        if (q.includes(k) || (k === 'v&a' && (q.includes('v&a') || q.includes('victoria and albert')))) {{
          matchPendingKey = k;
          break;
        }}
      }}

      if (matchPendingKey) {{
        const p = PENDING_MUSEUMS[matchPendingKey];
        response = `
          <div class="space-y-2">
            <div class="flex items-center justify-between border-b border-[#393939] pb-1.5 font-mono">
              <div>
                <h3 class="font-bold text-white text-sm">${{p.name}}</h3>
                <p class="text-[11px] text-[#0f62fe]">📍 ${{p.city}}, ${{p.country}}</p>
              </div>
              <span class="px-2 py-0.5 text-[10px] font-bold bg-[#161616] text-[#f1c21b] border border-[#f1c21b]">
                ${{p.status}}
              </span>
            </div>

            <div class="bg-[#161616] p-2.5 border border-[#f1c21b] text-xs space-y-1">
              <span class="text-[#f1c21b] font-mono font-bold uppercase tracking-wider text-[10px] block">
                🔍 Why It Is Not On The Atlas Map
              </span>
              <p class="text-[#f4f4f4] leading-relaxed">${{p.why_not_on_map}}</p>
            </div>

            <div class="bg-[#161616] p-2.5 border border-[#393939] text-xs space-y-1">
              <span class="text-[#24a148] font-mono font-bold uppercase tracking-wider text-[10px] block">Funding Architecture</span>
              <p class="text-[#c6c6c6] leading-relaxed">${{p.funding}}</p>
            </div>

            <div class="bg-[#161616] p-2.5 border border-[#393939] text-xs space-y-1">
              <span class="text-[#4589ff] font-mono font-bold uppercase tracking-wider text-[10px] block">Controversies & Scrutiny</span>
              <p class="text-[#c6c6c6] leading-relaxed">${{p.watch}}</p>
            </div>
          </div>
        `;

        actions.push({{
          label: `Plot & Add ${{p.name}} to Globe`,
          icon: '➕',
          handler: () => addAndPlotInstitution(p)
        }});

        actions.push({{
          label: `Inclusion Criteria Overview`,
          icon: '❓',
          handler: () => runOfflineLogic('why are museums not on the map')
        }});

        appendBotMessage(response, actions);
        return;
      }}

      if (isGeneralCriteriaQuery) {{
        response = `
          <div class="space-y-2.5">
            <div class="border-b border-[#393939] pb-1.5 flex items-center justify-between font-mono">
              <h3 class="font-bold text-white text-sm">Why Some Museums Are Not On The Map</h3>
              <span class="px-2 py-0.5 text-[10px] font-bold bg-[#161616] text-[#0f62fe] border border-[#0f62fe]">Atlas Criteria</span>
            </div>
            
            <p class="text-xs text-[#c6c6c6] leading-relaxed">
              Culture Atlas tracks cultural capital and the ethical transparency of institutional funding. Omitted institutions fall under <strong>4 structural criteria</strong>:
            </p>

            <div class="space-y-1.5 text-xs">
              <div class="bg-[#161616] p-2 border border-[#393939]">
                <span class="text-[#24a148] font-mono font-bold block mb-0.5">1. Opaque Corporate Rosters (Tier U)</span>
                <p class="text-[#c6c6c6] text-[11px] leading-relaxed">
                  Many museums display donor logos without disclosing contribution amounts, gift acceptance policies, or Form 990 / Charity Commission schedules.
                </p>
              </div>

              <div class="bg-[#161616] p-2 border border-[#393939]">
                <span class="text-[#f1c21b] font-mono font-bold block mb-0.5">2. Extractive & Defense Benefactors</span>
                <p class="text-[#c6c6c6] text-[11px] leading-relaxed">
                  Institutions actively partnered with fossil fuels (e.g. <strong>British Museum\'s</strong> 2023 £50M BP deal) or defense contractors are placed under review dossiers.
                </p>
              </div>

              <div class="bg-[#161616] p-2 border border-[#393939]">
                <span class="text-[#4589ff] font-mono font-bold block mb-0.5">3. Imperial Provenance & Restitution Disputes</span>
                <p class="text-[#c6c6c6] text-[11px] leading-relaxed">
                  Institutions facing contested international claims over looted heritage (Parthenon Marbles, Benin Bronzes) sit outside standard ethical certification.
                </p>
              </div>

              <div class="bg-[#161616] p-2 border border-[#393939]">
                <span class="text-[#8d8d8d] font-mono font-bold block mb-0.5">4. Research Pipeline</span>
                <p class="text-[#c6c6c6] text-[11px] leading-relaxed">
                  Civic research tracker actively auditing beyond 203 verified institutions. Unlisted museums can be nominated and plotted dynamically.
                </p>
              </div>
            </div>
          </div>
        `;

        actions.push({{
          label: `British Museum (BP / Restitution)`,
          icon: '🏛️',
          handler: () => runOfflineLogic('tell me about British Museum')
        }});
        actions.push({{
          label: `Musée du Louvre (Franchise Scrutiny)`,
          icon: '🏛️',
          handler: () => runOfflineLogic('tell me about Louvre')
        }});
        actions.push({{
          label: `LACMA ($750M Rebuild Scrutiny)`,
          icon: '🏛️',
          handler: () => runOfflineLogic('tell me about LACMA')
        }});

        appendBotMessage(response, actions);
        return;
      }}

      // Check Mapped Institution
      const matchInst = findInstitution(q);
      if (matchInst) {{
        if (matchInst.name.toLowerCase().includes('moma')) {{
          response = `
            <div class="space-y-2">
              <div class="flex items-center justify-between border-b border-[#393939] pb-1.5 font-mono">
                <div>
                  <h3 class="font-bold text-white text-sm">MoMA (The Museum of Modern Art)</h3>
                  <p class="text-[11px] text-[#0f62fe]">📍 Midtown Manhattan, New York, USA</p>
                </div>
                <span class="px-2 py-0.5 text-[10px] font-bold bg-[#0f284c] text-[#4589ff] border border-[#4589ff]">
                  Tier B · High Scrutiny
                </span>
              </div>

              <div class="bg-[#161616] p-2.5 border border-[#393939] text-xs space-y-1">
                <span class="text-[#24a148] font-mono font-bold uppercase tracking-wider text-[10px] block">Funding Structure</span>
                <p class="text-[#c6c6c6] leading-relaxed">
                  <strong>Budget & Endowment:</strong> Operating budget of ~$180M+ annually with an endowment exceeding $1.2 Billion. 
                </p>
                <p class="text-[#c6c6c6] leading-relaxed">
                  <strong>Corporate Underwriters:</strong> Bloomberg Philanthropies, Hyundai Card, UNIQLO (title partner for free Friday <em>'UNIQLO NYC Nights'</em>), Cartier, Bank of America, Chanel, Volkswagen Group, Allianz.
                </p>
              </div>

              <div class="bg-[#161616] p-2.5 border border-[#f1c21b] text-xs space-y-1.5">
                <span class="text-[#f1c21b] font-mono font-bold uppercase tracking-wider text-[10px] flex items-center gap-1">
                  ⚠️ Critical Ethical Research & Controversies
                </span>
                <p class="text-[#f4f4f4] leading-relaxed">
                  • <strong>Leon Black & Jeffrey Epstein:</strong> MoMA former Board Chairman Leon Black stepped down in March 2021 after scrutiny over $158 million paid to Jeffrey Epstein between 2012 and 2017.
                </p>
                <p class="text-[#f4f4f4] leading-relaxed">
                  • <strong>'Strike MoMA' (Spring 2021):</strong> Activist coalition (Decolonize This Place, Strike MoMA, Artists Space allies) launched 10 weeks of protests demanding trustee removal and structural reform.
                </p>
                <p class="text-[#f4f4f4] leading-relaxed">
                  • <strong>Controversial Board Members:</strong> 
                  <span class="text-[#c6c6c6]">Steven Tananbaum (GoldenTree hedge fund / Puerto Rico sovereign debt crisis), Larry Fink (BlackRock CEO / fossil fuel investments), Paula Crown (General Dynamics defense family).</span>
                </p>
              </div>
            </div>
          `;
        }} else {{
          response = `
            <div class="space-y-2">
              <div class="flex items-center justify-between border-b border-[#393939] pb-1.5 font-mono">
                <div>
                  <h3 class="font-bold text-white text-sm">${{matchInst.name}}</h3>
                  <p class="text-[11px] text-[#0f62fe]">📍 ${{matchInst.location}} (${{matchInst.size === 'L' ? 'Large >$20M' : 'Small/Mid'}})</p>
                </div>
                <span class="px-2 py-0.5 text-[10px] font-bold border ${{matchInst.tier === 'A' ? 'bg-[#132c1c] text-[#24a148] border-[#24a148]' : matchInst.tier === 'B' ? 'bg-[#0f284c] text-[#4589ff] border-[#4589ff]' : 'bg-[#262626] text-[#8d8d8d] border-[#525252]'}}">
                  ${{matchInst.tier === 'A' ? 'Tier A · Verified' : matchInst.tier === 'B' ? 'Tier B · One Name' : 'Tier U · Unverified'}}
                </span>
              </div>
              <div class="bg-[#161616] p-2.5 border border-[#393939] text-xs">
                <span class="text-[#24a148] font-mono font-bold uppercase tracking-wider text-[10px] block mb-0.5">Funding Breakdown</span>
                <p class="text-[#c6c6c6] leading-relaxed">${{matchInst.funding}}</p>
              </div>
              ${{matchInst.watch ? `
                <div class="bg-[#161616] p-2.5 border border-[#393939] text-xs">
                  <span class="text-[#4589ff] font-mono font-bold uppercase tracking-wider text-[10px] block mb-0.5">⚠️ Watch Notes & Governance</span>
                  <p class="text-[#c6c6c6] leading-relaxed">${{matchInst.watch}}</p>
                </div>
              ` : ''}}
            </div>
          `;
        }}

        actions.push({{
          label: `Center on Globe`,
          icon: '📍',
          tier: matchInst.tier,
          handler: () => {{
            viewGlobeBtn.click();
            selectInstitution(matchInst);
          }}
        }});
        actions.push({{
          label: `Filter by ${{matchInst.city}}`,
          icon: '🏙️',
          handler: () => {{
            viewGlobeBtn.click();
            setCityFilter(matchInst.city);
          }}
        }});

        appendBotMessage(response, actions);
        viewGlobeBtn.click();
        selectInstitution(matchInst);
        return;
      }}

      // Check City
      const matchCity = CITY_LIST.find(c => q.includes(c.name.toLowerCase()));
      if (matchCity) {{
        const cityInsts = ALL_INSTITUTIONS.filter(i => i.city.toLowerCase() === matchCity.name.toLowerCase());
        response = `
          <p class="font-bold text-white font-mono">🏙️ ${{matchCity.name}}, ${{matchCity.country}} (${{cityInsts.length}} institution${{cityInsts.length > 1 ? 's' : ''}})</p>
          <ul class="mt-1.5 space-y-1 text-[#c6c6c6] text-xs font-mono">
            ${{cityInsts.map(i => `
              <li><strong>${{i.name}}</strong> <span class="${{i.tier === 'A' ? 'text-[#24a148]' : 'text-[#4589ff]'}}">(${{i.tier === 'A' ? 'Verified' : 'One Name'}})</span> · ${{i.size === 'L' ? 'Large' : 'Small/Mid'}}</li>
            `).join('')}}
          </ul>
        `;
        actions.push({{
          label: `Fly to ${{matchCity.name}}`,
          icon: '📍',
          handler: () => {{
            viewGlobeBtn.click();
            setCityFilter(matchCity.name);
          }}
        }});
        cityInsts.slice(0, 2).forEach(inst => {{
          actions.push({{
            label: inst.name,
            icon: '🏛️',
            tier: inst.tier,
            handler: () => {{
              viewGlobeBtn.click();
              selectInstitution(inst);
            }}
          }});
        }});
        appendBotMessage(response, actions);
        viewGlobeBtn.click();
        setCityFilter(matchCity.name);
        return;
      }}

      // Check Country
      const matchCountry = COUNTRY_LIST.find(c => {{
        const cLow = c.name.toLowerCase();
        return q.includes(cLow) || (cLow === 'usa' && (q.includes('united states') || q.includes('america'))) || (cLow === 'uk' && (q.includes('united kingdom') || q.includes('britain')));
      }});

      if (matchCountry && (q.includes('country') || q.includes('in ') || q.includes(matchCountry.name.toLowerCase()))) {{
        const countryInsts = ALL_INSTITUTIONS.filter(i => i.country.toLowerCase() === matchCountry.name.toLowerCase());
        response = `
          <p class="font-bold text-white font-mono">🌍 ${{matchCountry.name}} (${{countryInsts.length}} institutions mapped)</p>
          <ul class="mt-1.5 space-y-1 text-[#c6c6c6] text-xs font-mono">
            ${{countryInsts.slice(0, 4).map(i => `
              <li><strong>${{i.name}}</strong> <span class="${{i.tier === 'A' ? 'text-[#24a148]' : 'text-[#4589ff]'}}">(${{i.tier === 'A' ? 'Verified' : 'One Name'}})</span> — ${{i.city}}</li>
            `).join('')}}
          </ul>
          ${{countryInsts.length > 4 ? `<p class="text-[11px] text-[#8d8d8d] mt-1">...and ${{countryInsts.length - 4}} more.</p>` : ''}}
        `;
        actions.push({{
          label: `Fly to ${{matchCountry.name}}`,
          icon: '📍',
          handler: () => {{
            viewGlobeBtn.click();
            setCountryFilter(matchCountry.name);
          }}
        }});
        appendBotMessage(response, actions);
        viewGlobeBtn.click();
        setCountryFilter(matchCountry.name);
        return;
      }}

      // Fallback
      response = `
        <div class="space-y-2">
          <p class="font-bold text-white font-mono">Atlas Concierge</p>
          <p class="text-xs text-[#c6c6c6]">
            Query unindexed or pending institutions:
          </p>
          <div class="bg-[#161616] p-2.5 border border-[#393939] text-xs space-y-1">
            <span class="text-[#0f62fe] font-mono font-bold block">Why is this museum not on the map?</span>
            <p class="text-[#8d8d8d] text-[11px] leading-relaxed">
              Requires audited public disclosure of benefactor contributions, a formal code excluding weapons/fossil fuels, or active verification of public 990 / Charity Commission returns.
            </p>
          </div>
        </div>
      `;
      actions.push({{
        label: 'Inclusion Criteria Overview',
        icon: '❓',
        handler: () => runOfflineLogic('why are museums not on the map')
      }});
      actions.push({{
        label: 'British Museum Audit',
        handler: () => runOfflineLogic('tell me about British Museum')
      }});
      actions.push({{
        label: 'Musée du Louvre Audit',
        handler: () => runOfflineLogic('tell me about Louvre')
      }});
      appendBotMessage(response, actions);
    }}

    chatSendBtn.addEventListener('click', () => {{
      const val = chatInput.value.trim();
      if (val) {{
        chatInput.value = '';
        handleUserQuery(val);
      }}
    }});

    chatInput.addEventListener('keydown', e => {{
      if (e.key === 'Enter') {{
        const val = chatInput.value.trim();
        if (val) {{
          chatInput.value = '';
          handleUserQuery(val);
        }}
      }}
    }});

  </script>
</body>
</html>
'''

with open('/Users/polinavasilyeva/.gemini/antigravity/scratch/sponsor-atlas/app/index.html', 'w') as f:
    f.write(carbon_app_html)

with open('/Users/polinavasilyeva/.gemini/antigravity/brain/b997e616-4551-453e-83cc-4ba184f90abf/culture_atlas_app.html', 'w') as f:
    f.write(carbon_app_html)

print("Updated app/index.html and culture_atlas_app.html with IBM Carbon Design System, no glow, and on-globe country and city labels!")
