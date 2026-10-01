import json

with open('/Users/polinavasilyeva/.gemini/antigravity/scratch/sponsor-atlas/app/world-topo.json') as f:
    topo = json.load(f)

with open('/Users/polinavasilyeva/.gemini/antigravity/scratch/sponsor-atlas/institutions.json') as f:
    institutions = json.load(f)

scale = topo['transform']['scale']
translate = topo['transform']['translate']

arcs_downsampled = []
for arc in topo['arcs']:
    curr_x, curr_y = 0, 0
    pts = []
    last_pt = None
    for dx, dy in arc:
        curr_x += dx
        curr_y += dy
        p = [round(curr_x * scale[0] + translate[0], 1), round(curr_y * scale[1] + translate[1], 1)]
        if last_pt is None or (abs(p[0] - last_pt[0]) >= 0.5 or abs(p[1] - last_pt[1]) >= 0.5):
            pts.append(p)
            last_pt = p
    if len(pts) > 1:
        arcs_downsampled.append(pts)

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
    {'name': 'RUSSIA', 'lat': 61.5, 'lon': 105.3, 'country': 'Russia'}
]

country_list = []
for c, cnt in sorted(inst_countries.items(), key=lambda x: (-x[1], x[0])):
    centroid = next((x for x in COUNTRY_CENTROIDS if x['country'] == c), None)
    lat = centroid['lat'] if centroid else 0
    lon = centroid['lon'] if centroid else 0
    country_list.append({
        'name': c,
        'label': centroid['name'] if centroid else c.upper(),
        'lat': lat,
        'lon': lon,
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
        'status': 'Tier Review · High Controversy'
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
        'status': 'Tier Review · Franchise Scrutiny'
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
        'status': 'Tier Review · Capital Campaign Scrutiny'
    }
}

widget_html = f'''<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <!-- IBM Plex Fonts -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
  
  <script src="https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js"></script>
  <style>
    /* IBM Carbon Design System Tokens */
    body {{
      font-family: 'IBM Plex Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      background-color: transparent;
      color: #f4f4f4;
    }}
    .font-mono {{
      font-family: 'IBM Plex Mono', monospace;
    }}
    #widgetGlobeCanvas {{
      cursor: grab;
      touch-action: none;
    }}
    #widgetGlobeCanvas.dragging {{
      cursor: grabbing;
    }}
    .custom-scrollbar::-webkit-scrollbar {{
      width: 4px;
    }}
    .custom-scrollbar::-webkit-scrollbar-thumb {{
      background: #393939;
    }}
  </style>
</head>
<body class="p-2 antialiased">
  
  <div class="bg-[#161616] text-[#f4f4f4] border border-[#393939] p-3 shadow-xl overflow-hidden flex flex-col gap-2.5 max-h-[530px]">
    
    <!-- Header (IBM Carbon Header Bar) -->
    <div class="flex flex-wrap items-center justify-between border-b border-[#393939] pb-2 px-1 gap-2 bg-[#262626] -m-3 mb-0 p-3">
      <div class="flex items-center gap-2">
        <div class="w-3 h-3 bg-[#0f62fe]"></div>
        <h2 class="text-xs font-semibold tracking-wider text-white flex items-center gap-1.5 uppercase font-mono">
          Culture Atlas <span class="text-[#8d8d8d] font-normal">IBM Carbon · {len(inst_countries)} Countries · {len(sorted_cities)} Cities</span>
        </h2>
      </div>
      <div class="flex items-center gap-1.5 text-[11px] font-mono text-[#8d8d8d]">
        <select id="widgetCountrySelect" class="bg-[#161616] border border-[#525252] px-1.5 py-0.5 text-[10.5px] text-[#f4f4f4] focus:outline-none focus:border-[#0f62fe]">
          <option value="all">Countries ({len(inst_countries)})</option>
        </select>
        <select id="widgetCitySelect" class="bg-[#161616] border border-[#525252] px-1.5 py-0.5 text-[10.5px] text-[#f4f4f4] focus:outline-none focus:border-[#0f62fe]">
          <option value="all">Cities ({len(sorted_cities)})</option>
        </select>
      </div>
    </div>

    <!-- Main 2-Column Interface -->
    <div class="grid grid-cols-1 sm:grid-cols-12 gap-2.5 flex-1 min-h-[360px] overflow-hidden pt-1">
      
      <!-- Left Column: Interactive 3D Canvas Globe (No Glow, Clean Carbon Geometry) -->
      <div class="sm:col-span-5 bg-[#161616] border border-[#393939] p-1 flex flex-col items-center justify-center relative overflow-hidden">
        <canvas id="widgetGlobeCanvas" width="220" height="220" class="max-w-full"></canvas>
        
        <div class="absolute bottom-2 left-2 flex items-center gap-1 text-[10px] text-[#8d8d8d] font-mono">
          <button id="widgetSpinBtn" class="px-1.5 py-0.5 bg-[#262626] hover:bg-[#393939] border border-[#393939] text-[#f4f4f4] transition">↻ Spin</button>
          <button id="widgetResetBtn" class="px-1.5 py-0.5 bg-[#262626] hover:bg-[#393939] border border-[#393939] text-[#f4f4f4] transition">◎ Center</button>
        </div>

        <div class="absolute top-2 right-2 text-[9.5px] font-mono text-[#8d8d8d] bg-[#262626] px-1.5 py-0.5 border border-[#393939] max-w-[130px] truncate" id="globeHoverLabel">
          Carbon Globe
        </div>
      </div>

      <!-- Right Column: Conversational Concierge & Dossier (Carbon Layer 01) -->
      <div class="sm:col-span-7 bg-[#262626] border border-[#393939] flex flex-col overflow-hidden">
        
        <!-- Tab Bar -->
        <div class="flex items-center justify-between bg-[#1f1f1f] border-b border-[#393939] px-3 py-1.5 text-[11px] font-mono">
          <div class="flex gap-3">
            <button id="tabChatBtn" class="font-semibold text-white border-b-2 border-[#0f62fe] pb-0.5">Concierge Chat</button>
            <button id="tabDossierBtn" class="font-medium text-[#8d8d8d] hover:text-white pb-0.5">Dossier Card</button>
          </div>
          <span id="activeSelectionIndicator" class="text-[10px] text-[#0f62fe] truncate max-w-[120px]">All Locations</span>
        </div>

        <!-- Chat View -->
        <div id="widgetChatView" class="flex-1 flex flex-col overflow-hidden p-2.5 bg-[#161616]">
          
          <div id="widgetChatHistory" class="flex-1 overflow-y-auto custom-scrollbar space-y-2 text-xs pr-1">
            <div class="bg-[#262626] border border-[#393939] p-2.5 text-[#f4f4f4] leading-relaxed">
              <p class="font-semibold text-white mb-1 font-mono">Atlas Concierge (IBM Carbon Theme)</p>
              <p class="text-[#c6c6c6] text-[11px]">Country & city names are rendered on the globe without glow. Inquire about any institution or inclusion criteria:</p>
              <div class="mt-2 flex flex-wrap gap-1 font-mono text-[10.5px]">
                <button class="widget-preset px-2 py-0.5 bg-[#161616] hover:bg-[#333333] border border-[#525252] text-[#f1c21b] transition">
                  🔍 Why not on the map?
                </button>
                <button class="widget-preset px-2 py-0.5 bg-[#161616] hover:bg-[#333333] border border-[#393939] text-[#f4f4f4] transition">
                  🏛️ MoMA Research
                </button>
                <button class="widget-preset px-2 py-0.5 bg-[#161616] hover:bg-[#333333] border border-[#393939] text-[#c6c6c6] transition">
                  🇬🇧 British Museum
                </button>
                <button class="widget-preset px-2 py-0.5 bg-[#161616] hover:bg-[#333333] border border-[#393939] text-[#c6c6c6] transition">
                  🇫🇷 Musée du Louvre
                </button>
              </div>
            </div>
          </div>

          <div class="mt-2 flex items-center gap-1.5 pt-1.5 border-t border-[#393939]">
            <input type="text" id="widgetChatInput" placeholder="Ask: 'MoMA', 'why not on the map', 'London'..." class="flex-1 bg-[#262626] border border-[#525252] px-2.5 py-1 text-xs text-[#f4f4f4] placeholder-[#8d8d8d] focus:outline-none focus:border-[#0f62fe]" />
            <button id="widgetChatSend" class="px-3 py-1 bg-[#0f62fe] hover:bg-[#0353e9] text-white font-medium text-xs font-mono transition">
              Send
            </button>
          </div>

        </div>

        <!-- Dossier View -->
        <div id="widgetDossierView" class="hidden flex-1 overflow-y-auto custom-scrollbar p-3 text-xs space-y-2 bg-[#161616]">
          <div id="widgetDossierEmpty" class="text-center py-10 text-[#8d8d8d]">
            <p class="text-base mb-1">🏛️</p>
            <p class="font-mono text-[11px]">Select any city, country, or institution dot on the globe.</p>
          </div>
          <div id="widgetDossierBody" class="hidden space-y-2">
            <div class="flex items-center justify-between border-b border-[#393939] pb-1 font-mono">
              <h3 id="dossierName" class="font-bold text-white text-xs"></h3>
              <span id="dossierTier" class="text-[9.5px] px-1.5 py-0.5 border font-mono"></span>
            </div>
            <p id="dossierLoc" class="text-[10.5px] text-[#0f62fe] font-mono"></p>
            <div class="bg-[#262626] p-2 border border-[#393939]">
              <span class="text-[9.5px] text-[#24a148] font-mono font-bold uppercase tracking-wider block mb-0.5">Funding</span>
              <p id="dossierFunding" class="text-[11px] text-[#c6c6c6] leading-relaxed"></p>
            </div>
            <div id="dossierWatchBox" class="bg-[#262626] p-2 border border-[#393939]">
              <span class="text-[9.5px] text-[#4589ff] font-mono font-bold uppercase tracking-wider block mb-0.5">Watch Notes</span>
              <p id="dossierWatch" class="text-[11px] text-[#c6c6c6] leading-relaxed"></p>
            </div>
            <div id="dossierWhyNotBox" class="bg-[#262626] p-2 border border-[#f1c21b] hidden">
              <span class="text-[9.5px] text-[#f1c21b] font-mono font-bold uppercase tracking-wider block mb-0.5">⚠️ Why Not On Map</span>
              <p id="dossierWhyNot" class="text-[11px] text-[#f4f4f4] leading-relaxed"></p>
            </div>
            <div id="dossierSources" class="pt-1 text-[11px] font-mono"></div>
          </div>
        </div>

      </div>

    </div>

  </div>

  <script>
    const DATA = {json.dumps(institutions)};
    const WORLD_ARCS = {json.dumps(arcs_downsampled)};
    const COUNTRY_LIST = {json.dumps(country_list)};
    const CITIES = {json.dumps(sorted_cities)};
    const PENDING_MUSEUMS = {json.dumps(PENDING_MUSEUMS)};
    const COUNTRY_CENTROIDS = {json.dumps(COUNTRY_CENTROIDS)};

    let selectedCountry = 'all';
    let selectedCity = 'all';

    const countrySelect = document.getElementById('widgetCountrySelect');
    COUNTRY_LIST.forEach(c => {{
      const opt = document.createElement('option');
      opt.value = c.name;
      opt.textContent = `${{c.name}} (${{c.count}})`;
      countrySelect.appendChild(opt);
    }});

    const citySelect = document.getElementById('widgetCitySelect');
    CITIES.forEach(cty => {{
      const opt = document.createElement('option');
      opt.value = cty.name;
      opt.textContent = `${{cty.name}} (${{cty.count}})`;
      citySelect.appendChild(opt);
    }});

    countrySelect.addEventListener('change', e => setWidgetCountry(e.target.value));
    citySelect.addEventListener('change', e => setWidgetCity(e.target.value));

    function setWidgetCountry(cName) {{
      selectedCountry = cName;
      countrySelect.value = cName;
      if (cName !== 'all') {{
        selectedCity = 'all';
        citySelect.value = 'all';
        const c = COUNTRY_LIST.find(x => x.name.toLowerCase() === cName.toLowerCase());
        if (c) flyTo(c.lon, c.lat);
        document.getElementById('activeSelectionIndicator').textContent = cName;
      }} else {{
        document.getElementById('activeSelectionIndicator').textContent = 'All Countries';
      }}
    }}

    function setWidgetCity(cityName) {{
      selectedCity = cityName;
      citySelect.value = cityName;
      if (cityName !== 'all') {{
        const cty = CITIES.find(x => x.name.toLowerCase() === cityName.toLowerCase());
        if (cty) {{
          selectedCountry = 'all';
          countrySelect.value = 'all';
          flyTo(cty.lon, cty.lat);
          document.getElementById('activeSelectionIndicator').textContent = cty.name;
        }}
      }} else {{
        document.getElementById('activeSelectionIndicator').textContent = 'All Cities';
      }}
    }}

    function addAndPlotWidgetInst(instData) {{
      let existing = DATA.find(i => i.name.toLowerCase() === instData.name.toLowerCase());
      if (!existing) {{
        DATA.push(instData);
        existing = instData;
      }}
      showDossier(existing);
    }}

    // Globe Renderer (IBM Carbon Solid - No Glow - Names Cities & Countries)
    const canvas = document.getElementById('widgetGlobeCanvas');
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
    let hoveredInst = null;
    let selectedInst = null;

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

    function render() {{
      const w = canvas.width;
      const h = canvas.height;
      const cx = w / 2;
      const cy = h / 2;
      const r = Math.min(w, h) * 0.44;

      ctx.clearRect(0, 0, w, h);

      if (isFlying) {{
        flightProgress += 0.05;
        if (flightProgress >= 1) {{
          flightProgress = 1;
          isFlying = false;
        }}
        const ease = 1 - Math.pow(1 - flightProgress, 3);
        rotLon = rotLon + (targetRotLon - rotLon) * ease;
        rotLat = rotLat + (targetRotLat - rotLat) * ease;
      }} else if (isAutoSpinning && !isDragging) {{
        rotLon = (rotLon + 0.25) % 360;
      }}

      // Solid Carbon Sphere (NO glow, NO atmospheric haze)
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
      [-45, 0, 45].forEach(lat => {{
        ctx.beginPath();
        let first = true;
        for (let lon = -180; lon <= 180; lon += 12) {{
          const pt = project(lon, lat, r, cx, cy);
          if (pt) {{
            if (first) {{ ctx.moveTo(pt.x, pt.y); first = false; }}
            else {{ ctx.lineTo(pt.x, pt.y); }}
          }} else {{ first = true; }}
        }}
        ctx.stroke();
      }});

      // Draw Country Boundaries (Sharp 0.8px, NO glow)
      ctx.strokeStyle = '#525252';
      ctx.lineWidth = 0.8;
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
        if (pt && pt.depth > 0.25) {{
          ctx.font = '600 8.5px "IBM Plex Sans", sans-serif';
          ctx.fillStyle = 'rgba(141, 141, 141, 0.6)'; // Carbon Gray 50
          ctx.textAlign = 'center';
          ctx.textBaseline = 'middle';
          ctx.fillText(c.name, pt.x, pt.y);
        }}
      }});

      // 🏙️ NAME CITIES on the Globe
      CITIES.slice(0, 25).forEach(cty => {{
        const pt = project(cty.lon, cty.lat, r, cx, cy);
        if (pt && pt.depth > 0.3) {{
          const isSelected = selectedCity.toLowerCase() === cty.name.toLowerCase();
          
          // Carbon square marker
          ctx.fillStyle = isSelected ? '#f1c21b' : '#8d8d8d';
          ctx.fillRect(pt.x - 1, pt.y - 1, 2.5, 2.5);

          // City label
          ctx.font = (isSelected ? '600 9.5px' : '500 8.5px') + ' "IBM Plex Sans", sans-serif';
          ctx.fillStyle = isSelected ? '#ffffff' : '#c6c6c6';
          ctx.textAlign = 'left';
          ctx.textBaseline = 'middle';
          ctx.fillText(cty.name, pt.x + 4, pt.y);
        }}
      }});

      ctx.restore();

      // Sharp Carbon Globe Rim (NO glow)
      ctx.strokeStyle = '#393939';
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.arc(cx, cy, r, 0, Math.PI * 2);
      ctx.stroke();

      // Institution Dots (Solid IBM Carbon colors, zero shadowBlur)
      const filtered = DATA.filter(inst => {{
        if (selectedCountry !== 'all' && inst.country.toLowerCase() !== selectedCountry.toLowerCase()) return false;
        if (selectedCity !== 'all' && inst.city.toLowerCase() !== selectedCity.toLowerCase()) return false;
        return true;
      }});

      filtered.forEach(inst => {{
        const pt = project(inst.lon, inst.lat, r, cx, cy);
        if (!pt) return;

        const isSel = selectedInst && selectedInst.name === inst.name;
        const isHov = hoveredInst && hoveredInst.name === inst.name;
        const dotR = (isSel ? 5.5 : isHov ? 4.5 : inst.size === 'L' ? 3.5 : 2.2) * Math.min(1.4, Math.max(0.7, pt.depth));

        // Carbon Data Palette
        let col = '#24a148'; // Verified: Carbon Green 50
        if (inst.tier === 'B') col = '#4589ff'; // One Name: Carbon Blue 50
        if (inst.tier === 'U') col = '#8d8d8d'; // Unverified: Carbon Gray 50
        if (inst.why_not_on_map) col = '#f1c21b'; // Carbon Yellow 30

        if (isSel) {{
          ctx.beginPath();
          ctx.arc(pt.x, pt.y, dotR + 2.5, 0, Math.PI * 2);
          ctx.strokeStyle = '#ffffff';
          ctx.lineWidth = 1.2;
          ctx.stroke();
        }}

        ctx.beginPath();
        ctx.arc(pt.x, pt.y, dotR, 0, Math.PI * 2);
        ctx.fillStyle = col;
        ctx.fill();
      }});

      requestAnimationFrame(render);
    }}
    requestAnimationFrame(render);

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

    function showDossier(inst) {{
      selectedInst = inst;
      flyTo(inst.lon, inst.lat);

      document.getElementById('dossierName').textContent = inst.name;
      document.getElementById('dossierLoc').textContent = `📍 ${{inst.location}} (${{inst.size === 'L' ? 'Large' : 'Small/Mid'}})`;
      
      const tierBadge = document.getElementById('dossierTier');
      tierBadge.textContent = inst.tier === 'A' ? 'Verified' : inst.tier === 'B' ? 'One Name' : 'Unverified';
      tierBadge.className = `text-[9.5px] px-1.5 py-0.5 border font-mono ${{inst.tier === 'A' ? 'bg-[#132c1c] text-[#24a148] border-[#24a148]' : inst.tier === 'B' ? 'bg-[#0f284c] text-[#4589ff] border-[#4589ff]' : 'bg-[#262626] text-[#8d8d8d] border-[#525252]'}}`;

      document.getElementById('dossierFunding').textContent = inst.funding;

      const watchBox = document.getElementById('dossierWatchBox');
      if (inst.watch) {{
        document.getElementById('dossierWatch').textContent = inst.watch;
        watchBox.classList.remove('hidden');
      }} else {{
        watchBox.classList.add('hidden');
      }}

      const whyNotBox = document.getElementById('dossierWhyNotBox');
      if (inst.why_not_on_map) {{
        document.getElementById('dossierWhyNot').textContent = inst.why_not_on_map;
        whyNotBox.classList.remove('hidden');
      }} else {{
        whyNotBox.classList.add('hidden');
      }}

      const sourcesDiv = document.getElementById('dossierSources');
      sourcesDiv.innerHTML = (inst.sources || []).map(u => {{
        let domain = u;
        try {{ domain = new URL(u).hostname.replace(/^www\\./, ''); }} catch(e){{}}
        return `<a href="${{u}}" target="_blank" class="inline-block mr-2 text-[#78a9ff] hover:underline">↗ ${{domain}}</a>`;
      }}).join('');

      document.getElementById('widgetDossierEmpty').classList.add('hidden');
      document.getElementById('widgetDossierBody').classList.remove('hidden');
      
      tabDossierBtn.click();
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

        rotLon = (rotLon - dx * 0.6) % 360;
        rotLat = Math.max(-75, Math.min(75, rotLat + dy * 0.6));
      }} else {{
        const cx = canvas.width / 2;
        const cy = canvas.height / 2;
        const r = Math.min(canvas.width, canvas.height) * 0.44;

        let hit = null;
        for (let i = 0; i < DATA.length; i++) {{
          const inst = DATA[i];
          const pt = project(inst.lon, inst.lat, r, cx, cy);
          if (pt && Math.hypot(pt.x - mx, pt.y - my) < 9) {{
            hit = inst;
            break;
          }}
        }}
        hoveredInst = hit;
        const lbl = document.getElementById('globeHoverLabel');
        if (hit) {{
          lbl.textContent = `${{hit.city}}: ${{hit.name}}`;
          lbl.className = 'absolute top-2 right-2 text-[9.5px] font-mono text-[#f4f4f4] bg-[#262626] px-1.5 py-0.5 border border-[#0f62fe] max-w-[140px] truncate';
        }} else {{
          lbl.textContent = 'Carbon Globe';
          lbl.className = 'absolute top-2 right-2 text-[9.5px] font-mono text-[#8d8d8d] bg-[#262626] px-1.5 py-0.5 border border-[#393939] max-w-[130px] truncate';
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
      if (hoveredInst) {{
        showDossier(hoveredInst);
      }}
    }});

    document.getElementById('widgetSpinBtn').addEventListener('click', () => {{
      isAutoSpinning = !isAutoSpinning;
    }});
    document.getElementById('widgetResetBtn').addEventListener('click', () => {{
      flyTo(0, 20);
      setWidgetCountry('all');
      setWidgetCity('all');
    }});

    // Tabs
    const tabChatBtn = document.getElementById('tabChatBtn');
    const tabDossierBtn = document.getElementById('tabDossierBtn');
    const widgetChatView = document.getElementById('widgetChatView');
    const widgetDossierView = document.getElementById('widgetDossierView');

    tabChatBtn.addEventListener('click', () => {{
      tabChatBtn.className = 'font-semibold text-white border-b-2 border-[#0f62fe] pb-0.5';
      tabDossierBtn.className = 'font-medium text-[#8d8d8d] hover:text-white pb-0.5';
      widgetChatView.classList.remove('hidden');
      widgetDossierView.classList.add('hidden');
    }});

    tabDossierBtn.addEventListener('click', () => {{
      tabDossierBtn.className = 'font-semibold text-white border-b-2 border-[#0f62fe] pb-0.5';
      tabChatBtn.className = 'font-medium text-[#8d8d8d] hover:text-white pb-0.5';
      widgetDossierView.classList.remove('hidden');
      widgetChatView.classList.add('hidden');
    }});

    function findWidgetInst(rawQuery) {{
      const raw = rawQuery.toLowerCase().trim();

      for (const inst of DATA) {{
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
        for (const inst of DATA) {{
          const names = [inst.name.toLowerCase(), ...(inst.aliases || [])];
          if (names.some(a => a.includes(t) || t.includes(a))) {{
            return inst;
          }}
        }}
      }}
      return null;
    }}

    const chatHistory = document.getElementById('widgetChatHistory');
    const chatInput = document.getElementById('widgetChatInput');
    const chatSend = document.getElementById('widgetChatSend');

    function appendChat(role, text, actions = []) {{
      const div = document.createElement('div');
      div.className = role === 'user' ? 'flex justify-end' : 'flex justify-start';

      let actionsHtml = '';
      if (actions.length > 0) {{
        actionsHtml = `<div class="mt-2 flex flex-wrap gap-1 font-mono">` +
          actions.map((act, i) => `
            <button class="widget-act px-2 py-0.5 text-[10px] font-medium border border-[#393939] bg-[#161616] text-[#f4f4f4] hover:bg-[#333333] transition" data-idx="${{i}}">
              ${{act.label}}
            </button>
          `).join('') + `</div>`;
      }}

      div.innerHTML = `
        <div class="${{role === 'user' ? 'bg-[#0f62fe] text-white font-mono' : 'bg-[#262626] text-[#f4f4f4] border border-[#393939]'}} p-2.5 max-w-[94%] text-[11.5px] leading-relaxed">
          ${{text}}
          ${{actionsHtml}}
        </div>
      `;

      if (actions.length > 0) {{
        div.querySelectorAll('.widget-act').forEach(btn => {{
          const idx = parseInt(btn.getAttribute('data-idx'), 10);
          btn.addEventListener('click', () => actions[idx].handler());
        }});
      }}

      chatHistory.appendChild(div);
      chatHistory.scrollTop = chatHistory.scrollHeight;
    }}

    function processQuery(query) {{
      appendChat('user', query);
      const q = query.toLowerCase().trim();

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
        appendChat('bot', `
          <div class="space-y-1.5 font-mono">
            <div class="flex items-center justify-between border-b border-[#393939] pb-1">
              <strong>${{p.name}}</strong>
              <span class="text-[9.5px] px-1.5 py-0.2 bg-[#161616] text-[#f1c21b] border border-[#f1c21b]">${{p.status}}</span>
            </div>
            <p class="text-[10px] text-[#0f62fe]">📍 ${{p.city}}, ${{p.country}}</p>
            <div class="bg-[#161616] p-2 border border-[#f1c21b] text-[11px] space-y-0.5">
              <span class="text-[#f1c21b] font-bold uppercase tracking-wider text-[9px] block">🔍 Why Not On Map</span>
              <p class="text-[#f4f4f4] leading-relaxed">${{p.why_not_on_map}}</p>
            </div>
            <div class="bg-[#161616] p-2 border border-[#393939] text-[11px] space-y-0.5">
              <span class="text-[#24a148] font-bold uppercase tracking-wider text-[9px] block">Funding</span>
              <p class="text-[#c6c6c6]">${{p.funding}}</p>
            </div>
          </div>
        `, [
          {{
            label: `➕ Plot on Globe & Inspect`,
            handler: () => addAndPlotWidgetInst(p)
          }},
          {{
            label: `Inclusion Criteria Overview`,
            handler: () => processQuery('why are museums not on the map')
          }}
        ]);
        return;
      }}

      if (isGeneralCriteriaQuery) {{
        appendChat('bot', `
          <div class="space-y-1.5">
            <div class="flex items-center justify-between border-b border-[#393939] pb-1 font-mono">
              <strong>Why Some Museums Are Not On The Map</strong>
              <span class="text-[9px] px-1.5 py-0.2 bg-[#161616] text-[#0f62fe] border border-[#0f62fe]">Criteria</span>
            </div>
            <p class="text-[11px] text-[#c6c6c6]">Omitted institutions fall under 4 structural criteria:</p>
            <div class="space-y-1 text-[10.5px]">
              <div class="bg-[#161616] p-1.5 border border-[#393939]">
                <span class="text-[#24a148] font-mono font-bold">1. Opaque Rosters:</span> Uncredited logos without 990 / Charity Commission returns.
              </div>
              <div class="bg-[#161616] p-1.5 border border-[#393939]">
                <span class="text-[#f1c21b] font-mono font-bold">2. Extractive Partners:</span> E.g. British Museum's 2023 £50M BP deal.
              </div>
              <div class="bg-[#161616] p-1.5 border border-[#393939]">
                <span class="text-[#4589ff] font-mono font-bold">3. Provenance & Restitution:</span> Contested looted artifacts (Benin, Parthenon).
              </div>
              <div class="bg-[#161616] p-1.5 border border-[#393939]">
                <span class="text-[#8d8d8d] font-mono font-bold">4. Scope:</span> 203 verified institutions; continually expanding.
              </div>
            </div>
          </div>
        `, [
          {{
            label: `British Museum`,
            handler: () => processQuery('British Museum')
          }},
          {{
            label: `Musée du Louvre`,
            handler: () => processQuery('Louvre')
          }},
          {{
            label: `LACMA`,
            handler: () => processQuery('LACMA')
          }}
        ]);
        return;
      }}

      const matchInst = findWidgetInst(q);
      if (matchInst) {{
        if (matchInst.name.toLowerCase().includes('moma')) {{
          appendChat('bot', `
            <div class="space-y-1.5 font-mono">
              <div class="flex items-center justify-between border-b border-[#393939] pb-1">
                <strong>MoMA (Museum of Modern Art)</strong>
                <span class="text-[9.5px] px-1.5 py-0.2 bg-[#0f284c] text-[#4589ff] border border-[#4589ff]">Tier B · Scrutiny</span>
              </div>
              <p class="text-[10px] text-[#0f62fe]">📍 Midtown Manhattan, NY · $180M+ Budget, $1.2B Endowment</p>
              <div class="bg-[#161616] p-2 border border-[#393939] text-[11px] space-y-0.5">
                <span class="text-[#24a148] font-bold uppercase tracking-wider text-[9px] block">Funding Architecture</span>
                <p class="text-[#c6c6c6]">Admissions (~30%), endowment income (~35%), Bloomberg Philanthropies, Hyundai Card, UNIQLO, Cartier, Bank of America.</p>
              </div>
              <div class="bg-[#161616] p-2 border border-[#f1c21b] text-[11px] space-y-0.5">
                <span class="text-[#f1c21b] font-bold uppercase tracking-wider text-[9px] block">⚠️ Watch Notes & Protests</span>
                <p class="text-[#f4f4f4]">• <strong>Leon Black:</strong> Resigned 2021 after scrutiny over $158M paid to Jeffrey Epstein.<br>• <strong>'Strike MoMA':</strong> 10 weeks of direct action.<br>• <strong>Trustees:</strong> Steven Tananbaum, Larry Fink, Paula Crown.</p>
              </div>
            </div>
          `, [
            {{
              label: `Inspect on Globe`,
              tier: matchInst.tier,
              handler: () => showDossier(matchInst)
            }},
            {{
              label: `Filter New York`,
              handler: () => setWidgetCity('New York')
            }}
          ]);
        }} else {{
          appendChat('bot', `
            <strong>${{matchInst.name}}</strong> · <span class="${{matchInst.tier === 'A' ? 'text-[#24a148]' : 'text-[#4589ff]'}}">${{matchInst.tier === 'A' ? 'Verified' : 'One Name'}}</span><br>
            📍 ${{matchInst.location}}<br>
            <span class="text-[#c6c6c6]">${{matchInst.funding}}</span>
            ${{matchInst.watch ? `<br><span class="text-[#f1c21b] text-[10.5px]">⚠️ ${{matchInst.watch}}</span>` : ''}}
          `, [{{
            label: `Inspect on Globe`,
            tier: matchInst.tier,
            handler: () => showDossier(matchInst)
          }}]);
        }}
        showDossier(matchInst);
        return;
      }}

      // Check city
      const matchCity = CITIES.find(c => q.includes(c.name.toLowerCase()));
      if (matchCity) {{
        const cityInsts = DATA.filter(i => i.city.toLowerCase() === matchCity.name.toLowerCase());
        appendChat('bot', `
          <span class="font-mono">🏙️ <strong>${{matchCity.name}}, ${{matchCity.country}}</strong> (${{cityInsts.length}} institution${{cityInsts.length > 1 ? 's' : ''}}):</span><br>
          ${{cityInsts.slice(0, 4).map(i => `• <strong>${{i.name}}</strong> (${{i.tier === 'A' ? 'Verified' : 'One Name'}})`).join('<br>')}}
        `, [
          {{
            label: `Fly to ${{matchCity.name}}`,
            handler: () => setWidgetCity(matchCity.name)
          }},
          ...cityInsts.slice(0, 2).map(inst => ({{
            label: inst.name,
            tier: inst.tier,
            handler: () => showDossier(inst)
          }}))
        ]);
        setWidgetCity(matchCity.name);
        return;
      }}

      // Check country
      const matchCountry = COUNTRY_LIST.find(c => {{
        const cLow = c.name.toLowerCase();
        return q.includes(cLow) || (cLow === 'usa' && (q.includes('united states') || q.includes('america'))) || (cLow === 'uk' && (q.includes('united kingdom') || q.includes('britain')));
      }});

      if (matchCountry && (q.includes('country') || q.includes('in ') || q.includes(matchCountry.name.toLowerCase()))) {{
        const cInsts = DATA.filter(i => i.country.toLowerCase() === matchCountry.name.toLowerCase());
        appendChat('bot', `
          <span class="font-mono">🌍 <strong>${{matchCountry.name}}</strong> (${{cInsts.length}} institutions mapped):</span><br>
          ${{cInsts.slice(0, 3).map(i => `• ${{i.name}} (${{i.tier === 'A' ? 'Verified' : 'One Name'}}) — ${{i.city}}`).join('<br>')}}
        `, [{{
          label: `Fly to ${{matchCountry.name}}`,
          handler: () => setWidgetCountry(matchCountry.name)
        }}]);
        setWidgetCountry(matchCountry.name);
        return;
      }}

      // Fallback
      appendChat('bot', `
        Query any museum, criteria, or city (e.g. <em>"MoMA"</em>, <em>"British Museum"</em>, <em>"why not on the map"</em>, or <em>"London"</em>).
      `);
    }}

    chatSend.addEventListener('click', () => {{
      const v = chatInput.value.trim();
      if (v) {{
        chatInput.value = '';
        processQuery(v);
      }}
    }});

    chatInput.addEventListener('keydown', e => {{
      if (e.key === 'Enter') {{
        const v = chatInput.value.trim();
        if (v) {{
          chatInput.value = '';
          processQuery(v);
        }}
      }}
    }});

    document.querySelectorAll('.widget-preset').forEach(btn => {{
      btn.addEventListener('click', () => {{
        processQuery(btn.textContent.replace(/^[^\w]+/, '').trim());
      }});
    }});

  </script>
</body>
</html>
'''

target_path = '/Users/polinavasilyeva/.gemini/antigravity/brain/b997e616-4551-453e-83cc-4ba184f90abf/concierge_widget.html'
with open(target_path, 'w') as f:
    f.write(widget_html)

print("Updated concierge_widget.html with IBM Carbon Design System, no glow, and on-globe country and city labels!")
