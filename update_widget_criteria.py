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

country_list = []
for c, cnt in sorted(inst_countries.items(), key=lambda x: (-x[1], x[0])):
    match_insts = [i for i in institutions if i['country'] == c]
    lat = sum(i['lat'] for i in match_insts) / len(match_insts)
    lon = sum(i['lon'] for i in match_insts) / len(match_insts)
    country_list.append({
        'name': c,
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
        'status': 'Excluded · State-Instrumented'
    }
}

widget_html = f'''<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <script src="https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js"></script>
  <style>
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
      background: rgba(255, 255, 255, 0.2);
      border-radius: 4px;
    }}
  </style>
</head>
<body class="bg-transparent text-[var(--foreground)] antialiased p-2 selection:bg-cyan-500 selection:text-white">
  
  <div class="bg-slate-950 text-slate-100 border border-cyan-500/30 rounded-2xl p-3 shadow-2xl overflow-hidden flex flex-col gap-2.5 max-h-[530px]">
    
    <!-- Header -->
    <div class="flex flex-wrap items-center justify-between border-b border-slate-800 pb-2 px-1 gap-2">
      <div class="flex items-center gap-2">
        <span class="w-2.5 h-2.5 rounded-full bg-emerald-400 shadow-[0_0_8px_#00ff87] animate-pulse"></span>
        <h2 class="text-xs font-bold tracking-wider text-white flex items-center gap-1.5 uppercase">
          Culture Atlas <span class="text-cyan-400 font-normal">{len(inst_countries)} Countries · {len(sorted_cities)} Cities · {len(institutions)} Museums</span>
        </h2>
      </div>
      <div class="flex items-center gap-1.5 text-[11px] font-mono text-slate-400">
        <!-- Quick Country Filter Dropdown -->
        <select id="widgetCountrySelect" class="bg-slate-900 border border-slate-700 rounded px-1.5 py-0.5 text-[10.5px] text-cyan-300 focus:outline-none focus:border-cyan-400">
          <option value="all">🌍 All Countries ({len(inst_countries)})</option>
        </select>
        <!-- Quick City Filter Dropdown -->
        <select id="widgetCitySelect" class="bg-slate-900 border border-slate-700 rounded px-1.5 py-0.5 text-[10.5px] text-amber-300 focus:outline-none focus:border-amber-400">
          <option value="all">🏙️ All Cities ({len(sorted_cities)})</option>
        </select>
      </div>
    </div>

    <!-- Main 2-Column Interface -->
    <div class="grid grid-cols-1 sm:grid-cols-12 gap-3 flex-1 min-h-[360px] overflow-hidden">
      
      <!-- Left Column: Interactive 3D Canvas Globe with Country Borders & Cities -->
      <div class="sm:col-span-5 bg-slate-900/80 rounded-xl border border-slate-800 p-2 flex flex-col items-center justify-center relative overflow-hidden">
        <canvas id="widgetGlobeCanvas" width="220" height="220" class="max-w-full"></canvas>
        
        <div class="absolute bottom-2 left-2 flex items-center gap-1 text-[10px] text-slate-400 font-mono">
          <button id="widgetSpinBtn" class="px-1.5 py-0.5 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 transition">↻ Spin</button>
          <button id="widgetResetBtn" class="px-1.5 py-0.5 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 transition">◎ Center</button>
        </div>

        <div class="absolute top-2 right-2 text-[10px] font-mono text-cyan-400 bg-slate-950/70 px-1.5 py-0.5 rounded border border-slate-800 max-w-[130px] truncate" id="globeHoverLabel">
          3D Globe & Cities
        </div>
      </div>

      <!-- Right Column: Conversational Concierge & Dossier -->
      <div class="sm:col-span-7 bg-slate-900/60 rounded-xl border border-slate-800 flex flex-col overflow-hidden">
        
        <!-- Tab Bar -->
        <div class="flex items-center justify-between bg-slate-950/60 border-b border-slate-800 px-3 py-1.5 text-[11px]">
          <div class="flex gap-2">
            <button id="tabChatBtn" class="font-semibold text-cyan-400 border-b-2 border-cyan-400 pb-0.5">Concierge Chat</button>
            <button id="tabDossierBtn" class="font-medium text-slate-400 hover:text-white pb-0.5">Dossier Card</button>
          </div>
          <span id="activeSelectionIndicator" class="text-[10px] text-emerald-400 truncate max-w-[120px]">All Locations</span>
        </div>

        <!-- Chat View -->
        <div id="widgetChatView" class="flex-1 flex flex-col overflow-hidden p-2">
          
          <div id="widgetChatHistory" class="flex-1 overflow-y-auto custom-scrollbar space-y-2 text-xs pr-1">
            <div class="bg-slate-800/80 p-2.5 rounded-xl text-slate-300 leading-relaxed border border-slate-700/60">
              <p class="font-semibold text-white mb-1">Hello! Ask me about any museum, controversy, or why institutions are missing:</p>
              <div class="mt-2 flex flex-wrap gap-1">
                <button class="widget-preset px-2 py-0.5 rounded bg-amber-950/60 hover:bg-amber-900/80 border border-amber-600/50 text-[10.5px] text-amber-300 hover:text-amber-100 transition font-medium">
                  🔍 Why not on the map?
                </button>
                <button class="widget-preset px-2 py-0.5 rounded bg-slate-900 hover:bg-amber-950 border border-slate-700 hover:border-amber-500/50 text-[10.5px] text-amber-300 hover:text-amber-200 transition">
                  🇬🇧 British Museum
                </button>
                <button class="widget-preset px-2 py-0.5 rounded bg-slate-900 hover:bg-amber-950 border border-slate-700 hover:border-amber-500/50 text-[10.5px] text-amber-300 hover:text-amber-200 transition">
                  🇫🇷 Musée du Louvre
                </button>
                <button class="widget-preset px-2 py-0.5 rounded bg-slate-900 hover:bg-emerald-950 border border-slate-700 hover:border-emerald-500/50 text-[10.5px] text-slate-300 hover:text-white transition">
                  🏛️ MoMA Research
                </button>
              </div>
            </div>
          </div>

          <div class="mt-2 flex items-center gap-1.5 pt-1.5 border-t border-slate-800">
            <input type="text" id="widgetChatInput" placeholder="Ask: 'why not on the map', 'British Museum', 'Louvre'..." class="flex-1 bg-slate-950 border border-slate-700 rounded-lg px-2.5 py-1.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-400" />
            <button id="widgetChatSend" class="px-3 py-1.5 rounded-lg bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-xs shadow transition">
              Ask
            </button>
          </div>

        </div>

        <!-- Dossier View -->
        <div id="widgetDossierView" class="hidden flex-1 overflow-y-auto custom-scrollbar p-3 text-xs space-y-2.5">
          <div id="widgetDossierEmpty" class="text-center py-10 text-slate-500">
            <p class="text-xl mb-1">🏛️</p>
            <p>Click any dot on the 3D globe to inspect its ethical funding dossier.</p>
          </div>
          <div id="widgetDossierBody" class="hidden space-y-2">
            <div class="flex items-center justify-between">
              <h3 id="dossierName" class="font-bold text-white text-sm"></h3>
              <span id="dossierTier" class="text-[10px] px-2 py-0.5 rounded-full border"></span>
            </div>
            <p id="dossierLoc" class="text-[11px] text-cyan-400"></p>
            <div class="bg-slate-950/70 p-2 rounded-lg border border-slate-800">
              <span class="text-[10px] text-emerald-400 font-bold uppercase tracking-wider block mb-0.5">Funding</span>
              <p id="dossierFunding" class="text-[11px] text-slate-300 leading-relaxed"></p>
            </div>
            <div id="dossierWatchBox" class="bg-slate-950/70 p-2 rounded-lg border border-slate-800">
              <span class="text-[10px] text-cyan-400 font-bold uppercase tracking-wider block mb-0.5">Watch Notes</span>
              <p id="dossierWatch" class="text-[11px] text-slate-300 leading-relaxed"></p>
            </div>
            <div id="dossierWhyNotBox" class="bg-amber-950/40 p-2 rounded-lg border border-amber-600/40 hidden">
              <span class="text-[10px] text-amber-400 font-bold uppercase tracking-wider block mb-0.5">⚠️ Why Not On Map</span>
              <p id="dossierWhyNot" class="text-[11px] text-slate-200 leading-relaxed"></p>
            </div>
            <div id="dossierSources" class="pt-1 text-[11px]"></div>
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

    let selectedCountry = 'all';
    let selectedCity = 'all';

    // Populate dropdowns
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

    countrySelect.addEventListener('change', e => {{
      setWidgetCountry(e.target.value);
    }});

    citySelect.addEventListener('change', e => {{
      setWidgetCity(e.target.value);
    }});

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

    // Globe Renderer
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
        rotLon = (rotLon + 0.3) % 360;
      }}

      // Outer glow
      const glow = ctx.createRadialGradient(cx, cy, r * 0.8, cx, cy, r * 1.25);
      glow.addColorStop(0, 'rgba(0, 242, 254, 0.25)');
      glow.addColorStop(1, 'transparent');
      ctx.fillStyle = glow;
      ctx.beginPath();
      ctx.arc(cx, cy, r * 1.25, 0, Math.PI * 2);
      ctx.fill();

      // Sphere base
      const ocean = ctx.createRadialGradient(cx - r * 0.3, cy - r * 0.3, r * 0.1, cx, cy, r);
      ocean.addColorStop(0, '#002b5c');
      ocean.addColorStop(0.7, '#00142e');
      ocean.addColorStop(1, '#000714');
      ctx.fillStyle = ocean;
      ctx.beginPath();
      ctx.arc(cx, cy, r, 0, Math.PI * 2);
      ctx.fill();

      // Clip inside globe for country borders
      ctx.save();
      ctx.beginPath();
      ctx.arc(cx, cy, r, 0, Math.PI * 2);
      ctx.clip();

      // Graticules
      ctx.strokeStyle = 'rgba(0, 255, 135, 0.1)';
      ctx.lineWidth = 0.6;
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

      // Draw Country Boundaries & Coastlines
      ctx.strokeStyle = 'rgba(0, 242, 254, 0.42)';
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

      // City halo markers if a specific city is selected
      if (selectedCity !== 'all') {{
        const cty = CITIES.find(c => c.name.toLowerCase() === selectedCity.toLowerCase());
        if (cty) {{
          const pt = project(cty.lon, cty.lat, r, cx, cy);
          if (pt) {{
            ctx.beginPath();
            ctx.arc(pt.x, pt.y, 9, 0, Math.PI * 2);
            ctx.strokeStyle = '#f59e0b';
            ctx.lineWidth = 2;
            ctx.stroke();
          }}
        }}
      }}

      ctx.restore();

      // Rim
      ctx.strokeStyle = 'rgba(0, 242, 254, 0.5)';
      ctx.lineWidth = 1.5;
      ctx.beginPath();
      ctx.arc(cx, cy, r, 0, Math.PI * 2);
      ctx.stroke();

      // Institution Dots
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
        const dotR = (isSel ? 6 : isHov ? 5 : inst.size === 'L' ? 4 : 2.5) * Math.min(1.5, Math.max(0.7, pt.depth));

        let col = '#24a148';
        if (inst.tier === 'B') col = '#4589ff';
        if (inst.tier === 'U') col = '#8d8d8d';
        if (inst.why_not_on_map) col = '#f59e0b';

        if (isSel) {{
          ctx.beginPath();
          ctx.arc(pt.x, pt.y, dotR * 2.2, 0, Math.PI * 2);
          ctx.strokeStyle = '#00ff87';
          ctx.lineWidth = 1.5;
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
      tierBadge.className = `text-[10px] px-2 py-0.5 rounded-full border ${{inst.tier === 'A' ? 'bg-emerald-950 text-emerald-400 border-emerald-600' : inst.tier === 'B' ? 'bg-blue-950 text-blue-400 border-blue-600' : 'bg-slate-800 text-slate-300 border-slate-600'}}`;

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
        return `<a href="${{u}}" target="_blank" class="inline-block mr-2 text-cyan-400 hover:underline">↗ ${{domain}}</a>`;
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
          lbl.className = 'absolute top-2 right-2 text-[10px] font-mono text-emerald-400 bg-slate-950/90 px-1.5 py-0.5 rounded border border-emerald-600/50 shadow max-w-[140px] truncate';
        }} else {{
          lbl.textContent = '3D Globe & Cities';
          lbl.className = 'absolute top-2 right-2 text-[10px] font-mono text-cyan-400 bg-slate-950/70 px-1.5 py-0.5 rounded border border-slate-800 max-w-[130px] truncate';
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
      tabChatBtn.className = 'font-semibold text-cyan-400 border-b-2 border-cyan-400 pb-0.5';
      tabDossierBtn.className = 'font-medium text-slate-400 hover:text-white pb-0.5';
      widgetChatView.classList.remove('hidden');
      widgetDossierView.classList.add('hidden');
    }});

    tabDossierBtn.addEventListener('click', () => {{
      tabDossierBtn.className = 'font-semibold text-cyan-400 border-b-2 border-cyan-400 pb-0.5';
      tabChatBtn.className = 'font-medium text-slate-400 hover:text-white pb-0.5';
      widgetDossierView.classList.remove('hidden');
      widgetChatView.classList.add('hidden');
    }});

    // Match institution by acronyms, aliases, or clean tokens
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

    // Chat processing
    const chatHistory = document.getElementById('widgetChatHistory');
    const chatInput = document.getElementById('widgetChatInput');
    const chatSend = document.getElementById('widgetChatSend');

    function appendChat(role, text, actions = []) {{
      const div = document.createElement('div');
      div.className = role === 'user' ? 'flex justify-end' : 'flex justify-start';

      let actionsHtml = '';
      if (actions.length > 0) {{
        actionsHtml = `<div class="mt-2 flex flex-wrap gap-1">` +
          actions.map((act, i) => `
            <button class="widget-act px-2 py-0.5 rounded text-[10px] font-semibold border ${{act.tier === 'A' ? 'bg-emerald-950 text-emerald-300 border-emerald-600' : 'bg-slate-900 text-cyan-300 border-slate-700'}} hover:scale-105 transition" data-idx="${{i}}">
              ${{act.label}}
            </button>
          `).join('') + `</div>`;
      }}

      div.innerHTML = `
        <div class="${{role === 'user' ? 'bg-emerald-600 text-white' : 'bg-slate-800 text-slate-200 border border-slate-700'}} p-2.5 rounded-xl max-w-[92%] text-[11.5px] leading-relaxed shadow">
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

      // Check if user is asking why museums are not on the map
      const isGeneralCriteriaQuery = (q.includes('why') && (q.includes('not on the map') || q.includes('not on map') || q.includes('missing') || q.includes('criteria') || q.includes('how are') || q.includes('included') || q.includes('selection'))) || q.includes('criteria for') || q.includes('why it is not') || q.includes('why is it not') || q.includes('why not on the map') || q.includes('or any other museum');

      // Check pending unmapped museums
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
          <div class="space-y-1.5">
            <div class="flex items-center justify-between border-b border-slate-700/60 pb-1">
              <strong>${{p.name}}</strong>
              <span class="text-[9.5px] px-1.5 py-0.5 rounded bg-amber-950 text-amber-300 border border-amber-600">${{p.status}}</span>
            </div>
            <p class="text-[10.5px] text-cyan-300">📍 ${{p.city}}, ${{p.country}}</p>
            <div class="bg-amber-950/40 p-2 rounded text-[11px] space-y-0.5 border border-amber-600/40">
              <span class="text-amber-400 font-bold uppercase tracking-wider text-[9px] block">🔍 Why Not On Map</span>
              <p class="text-slate-200 leading-relaxed">${{p.why_not_on_map}}</p>
            </div>
            <div class="bg-slate-950/80 p-2 rounded text-[11px] space-y-0.5 border border-slate-800">
              <span class="text-emerald-400 font-bold uppercase tracking-wider text-[9px] block">Funding Architecture</span>
              <p class="text-slate-300">${{p.funding}}</p>
            </div>
          </div>
        `, [
          {{
            label: `➕ Plot on Globe & Inspect`,
            handler: () => addAndPlotWidgetInst(p)
          }},
          {{
            label: `❓ Why are some museums not on map?`,
            handler: () => processQuery('why are museums not on the map')
          }}
        ]);
        return;
      }}

      if (isGeneralCriteriaQuery) {{
        appendChat('bot', `
          <div class="space-y-1.5">
            <div class="flex items-center justify-between border-b border-slate-700/60 pb-1">
              <strong>Why Some Museums Are Not On The Map</strong>
              <span class="text-[9px] px-1.5 py-0.5 rounded bg-cyan-950 text-cyan-300 border border-cyan-700">Atlas Criteria</span>
            </div>
            <p class="text-[11px] text-slate-300">Museums missing from the map usually meet 1 of 4 criteria:</p>
            <div class="space-y-1 text-[10.5px]">
              <div class="bg-slate-950/80 p-1.5 rounded border border-slate-800">
                <span class="text-emerald-400 font-bold">1. Opaque Donor Roster:</span> Uncredited corporate logos without 990 / Charity filings.
              </div>
              <div class="bg-slate-950/80 p-1.5 rounded border border-slate-800">
                <span class="text-amber-400 font-bold">2. Extractive & Defense Benefactors:</span> E.g. British Museum's 2023 £50M BP deal.
              </div>
              <div class="bg-slate-950/80 p-1.5 rounded border border-slate-800">
                <span class="text-cyan-400 font-bold">3. Provenance & Restitution:</span> Contested looted artifacts (Benin Bronzes, Parthenon).
              </div>
              <div class="bg-slate-950/80 p-1.5 rounded border border-slate-800">
                <span class="text-purple-400 font-bold">4. Research Pipeline:</span> 203 verified museums mapped; expanding continuously.
              </div>
            </div>
          </div>
        `, [
          {{
            label: `🇬🇧 British Museum`,
            handler: () => processQuery('British Museum')
          }},
          {{
            label: `🇫🇷 Musée du Louvre`,
            handler: () => processQuery('Louvre')
          }},
          {{
            label: `🇺🇸 LACMA`,
            handler: () => processQuery('LACMA')
          }}
        ]);
        return;
      }}

      // Check mapped institution
      const matchInst = findWidgetInst(q);
      if (matchInst) {{
        if (matchInst.name.toLowerCase().includes('moma')) {{
          appendChat('bot', `
            <div class="space-y-1.5">
              <div class="flex items-center justify-between border-b border-slate-700/60 pb-1">
                <strong>MoMA (Museum of Modern Art)</strong>
                <span class="text-[9.5px] px-1.5 py-0.5 rounded bg-blue-950 text-blue-300 border border-blue-600">Tier B · Scrutiny</span>
              </div>
              <p class="text-[10.5px] text-cyan-300">📍 Midtown Manhattan, NY · $180M+ Budget, $1.2B Endowment</p>
              <div class="bg-slate-950/80 p-2 rounded text-[11px] space-y-1 border border-slate-800">
                <span class="text-emerald-400 font-bold uppercase tracking-wider text-[9.5px] block">Funding Architecture</span>
                <p class="text-slate-300">Admissions (~30%), endowment income (~35%), Bloomberg Philanthropies, Hyundai Card, UNIQLO (UNIQLO NYC Nights), Cartier, Bank of America.</p>
              </div>
              <div class="bg-amber-950/40 p-2 rounded text-[11px] space-y-1 border border-amber-600/40">
                <span class="text-amber-400 font-bold uppercase tracking-wider text-[9.5px] block">⚠️ Watch Notes & Protests</span>
                <p class="text-slate-200">• <strong>Leon Black:</strong> Resigned 2021 after scrutiny over $158M paid to Jeffrey Epstein.<br>• <strong>'Strike MoMA':</strong> 10 weeks of direct-action protests targeting toxic trustees.<br>• <strong>Trustees:</strong> Steven Tananbaum (Puerto Rico debt), Larry Fink (BlackRock fossil fuels), Paula Crown (General Dynamics).</p>
              </div>
            </div>
          `, [
            {{
              label: `📍 Inspect on Globe`,
              tier: matchInst.tier,
              handler: () => showDossier(matchInst)
            }},
            {{
              label: `🗽 Fly to New York`,
              handler: () => setWidgetCity('New York')
            }}
          ]);
        }} else {{
          appendChat('bot', `
            <strong>${{matchInst.name}}</strong> · <span class="${{matchInst.tier === 'A' ? 'text-emerald-400' : 'text-blue-400'}}">${{matchInst.tier === 'A' ? 'Verified' : 'One Name'}}</span><br>
            📍 ${{matchInst.location}}<br>
            <span class="text-slate-300">${{matchInst.funding}}</span>
            ${{matchInst.watch ? `<br><span class="text-amber-300 text-[10.5px]">⚠️ ${{matchInst.watch}}</span>` : ''}}
          `, [{{
            label: `📍 Inspect on Globe`,
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
          🏙️ <strong>${{matchCity.name}}, ${{matchCity.country}}</strong> (${{cityInsts.length}} institution${{cityInsts.length > 1 ? 's' : ''}}):<br>
          ${{cityInsts.slice(0, 4).map(i => `• <strong>${{i.name}}</strong> (${{i.tier === 'A' ? 'Verified' : 'One Name'}})`).join('<br>')}}
        `, [
          {{
            label: `Fly to ${{matchCity.name}}`,
            handler: () => setWidgetCity(matchCity.name)
          }},
          ...cityInsts.slice(0, 2).map(inst => ({{
            label: `🏛️ ${{inst.name}}`,
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
          🌍 <strong>${{matchCountry.name}}</strong> (${{cInsts.length}} institutions mapped):<br>
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
        Ask about any museum or topic (e.g. <em>"MoMA"</em>, <em>"British Museum"</em>, <em>"why not on the map"</em>, or <em>"London"</em>).
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

print("Updated concierge_widget.html successfully!")
