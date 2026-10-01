import json
import re

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

# Extract country centroids
country_list = []
for geom in topo['objects']['world']['geometries']:
    name = geom.get('properties', {}).get('name', '')
    if not name:
        continue
    all_lons, all_lats = [], []
    arcs_ref = geom['arcs']
    if geom['type'] == 'Polygon':
        for ring in arcs_ref:
            for a_idx in ring:
                arc = arcs_downsampled[a_idx % len(arcs_downsampled)]
                for p in arc:
                    all_lons.append(p[0])
                    all_lats.append(p[1])
    elif geom['type'] == 'MultiPolygon':
        for poly in arcs_ref:
            for ring in poly:
                for a_idx in ring:
                    arc = arcs_downsampled[a_idx % len(arcs_downsampled)]
                    for p in arc:
                        all_lons.append(p[0])
                        all_lats.append(p[1])
    if all_lons and all_lats:
        avg_lon = round(sum(all_lons) / len(all_lons), 1)
        avg_lat = round(sum(all_lats) / len(all_lats), 1)
        matched_c = None
        for c in inst_countries:
            if c.lower() in name.lower() or name.lower() in c.lower():
                matched_c = c
                break
        cnt = inst_countries.get(matched_c, 0) if matched_c else 0
        country_list.append({
            'name': matched_c or name,
            'lon': avg_lon,
            'lat': avg_lat,
            'count': cnt
        })

unique_countries = {}
for c in country_list:
    n = c['name']
    if n not in unique_countries or c['count'] > unique_countries[n]['count']:
        unique_countries[n] = c

for c, cnt in inst_countries.items():
    if c not in unique_countries:
        match_insts = [i for i in institutions if i['country'] == c]
        lat = sum(i['lat'] for i in match_insts) / len(match_insts)
        lon = sum(i['lon'] for i in match_insts) / len(match_insts)
        unique_countries[c] = {
            'name': c,
            'lon': round(lon, 1),
            'lat': round(lat, 1),
            'count': cnt
        }

final_countries = sorted(unique_countries.values(), key=lambda x: (-x['count'], x['name']))

# Build app/index.html
app_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Culture Atlas | Global Cultural Institutions & Ethical Sponsorship Tracker</title>
  <!-- Tailwind CSS CDN -->
  <script src="https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js"></script>
  <style>
    :root {{
      --bg: #030712;
      --card-bg: rgba(15, 23, 42, 0.75);
      --border-color: rgba(51, 65, 85, 0.6);
      --accent: #00ff87;
      --cyan: #60efff;
    }}

    body {{
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
      background-color: var(--bg);
      color: #f1f5f9;
      margin: 0;
      padding: 0;
      overflow-x: hidden;
      -webkit-font-smoothing: antialiased;
    }}

    #globeCanvas {{
      cursor: grab;
      touch-action: none;
    }}
    #globeCanvas.dragging {{
      cursor: grabbing;
    }}

    ::-webkit-scrollbar {{
      width: 6px;
      height: 6px;
    }}
    ::-webkit-scrollbar-track {{
      background: rgba(0, 0, 0, 0.2);
    }}
    ::-webkit-scrollbar-thumb {{
      background: rgba(255, 255, 255, 0.15);
      border-radius: 9999px;
    }}
  </style>
</head>
<body class="min-h-screen flex flex-col bg-slate-950 text-slate-100">

  <!-- TOP HEADER -->
  <header class="border-b border-slate-800 bg-slate-900/90 backdrop-blur sticky top-0 z-40 px-4 py-3">
    <div class="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-3">
      
      <div class="flex items-center gap-3">
        <div>
          <h1 class="text-base font-bold tracking-wide text-white flex items-center gap-2">
            CULTURE ATLAS
            <span class="text-[10px] font-mono uppercase px-2 py-0.5 rounded-full bg-cyan-950 text-cyan-400 border border-cyan-800">
              35 Countries · {len(sorted_cities)} Cities · {len(institutions)} Institutions
            </span>
          </h1>
          <p class="text-xs text-slate-400 hidden sm:block">Ethically funded cultural institutions across the world, mapped by who pays for them.</p>
        </div>
      </div>

      <div class="flex items-center gap-2 flex-wrap">
        <!-- View Toggle -->
        <div class="flex bg-slate-800/80 p-0.5 rounded-lg border border-slate-700 text-xs">
          <button id="viewGlobeBtn" class="px-3 py-1 rounded-md font-medium transition bg-cyan-600 text-white shadow">
            3D Globe
          </button>
          <button id="viewListBtn" class="px-3 py-1 rounded-md font-medium text-slate-400 hover:text-white transition">
            Table View
          </button>
        </div>

        <!-- AI Concierge Toggle -->
        <button id="toggleConciergeBtn" class="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-emerald-600/90 hover:bg-emerald-500 text-slate-950 font-bold text-xs shadow-lg transition">
          <span>✨</span>
          <span>Ask Concierge</span>
          <span class="hidden md:inline text-[10px] opacity-75 font-mono">⌘K</span>
        </button>
      </div>

    </div>
  </header>

  <!-- FILTER & LOCATION SELECTOR BAR -->
  <section class="border-b border-slate-800/80 bg-slate-900/50 px-4 py-2 text-xs">
    <div class="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-3">
      
      <!-- Left Filters: Country & City Selectors -->
      <div class="flex items-center gap-2.5 flex-wrap">
        
        <!-- Country Selector -->
        <div class="flex items-center gap-1">
          <span class="text-slate-400 font-medium">🌍</span>
          <select id="countrySelect" class="bg-slate-950 border border-slate-700 rounded-lg px-2 py-1 text-xs text-cyan-300 focus:outline-none focus:border-cyan-400 font-medium">
            <option value="all">All Countries ({len(inst_countries)})</option>
          </select>
        </div>

        <!-- City Selector -->
        <div class="flex items-center gap-1">
          <span class="text-slate-400 font-medium">🏙️</span>
          <select id="citySelect" class="bg-slate-950 border border-slate-700 rounded-lg px-2 py-1 text-xs text-emerald-300 focus:outline-none focus:border-emerald-400 font-medium">
            <option value="all">All Cities ({len(sorted_cities)})</option>
          </select>
        </div>

        <div class="h-4 w-[1px] bg-slate-800 hidden sm:block"></div>

        <!-- Tier Chips -->
        <div class="flex items-center gap-1.5 flex-wrap">
          <button id="tierABtn" class="tier-chip flex items-center gap-1 px-2 py-0.5 rounded-full border border-emerald-500/40 bg-emerald-950/40 text-emerald-300 hover:bg-emerald-900/60 transition" data-tier="A">
            <span class="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
            <span>Verified</span>
            <span class="font-mono text-[10px] opacity-75 ml-0.5">{len([i for i in institutions if i['tier'] == 'A'])}</span>
          </button>
          <button id="tierBBtn" class="tier-chip flex items-center gap-1 px-2 py-0.5 rounded-full border border-blue-500/40 bg-blue-950/40 text-blue-300 hover:bg-blue-900/60 transition" data-tier="B">
            <span class="w-1.5 h-1.5 rounded-full bg-blue-400"></span>
            <span>One Name</span>
            <span class="font-mono text-[10px] opacity-75 ml-0.5">{len([i for i in institutions if i['tier'] == 'B'])}</span>
          </button>
          <button id="tierUBtn" class="tier-chip flex items-center gap-1 px-2 py-0.5 rounded-full border border-slate-500/40 bg-slate-900/40 text-slate-300 hover:bg-slate-800 transition" data-tier="U">
            <span class="w-1.5 h-1.5 rounded-full bg-slate-400"></span>
            <span>Unverified</span>
            <span class="font-mono text-[10px] opacity-75 ml-0.5">{len([i for i in institutions if i['tier'] == 'U'])}</span>
          </button>
        </div>

      </div>

      <!-- Right Filters: Size & Search -->
      <div class="flex items-center gap-3 flex-wrap">
        <div class="flex items-center gap-1 bg-slate-800/80 px-1 py-0.5 rounded-lg border border-slate-700 text-xs">
          <button id="sizeAllBtn" class="px-2 py-0.5 rounded text-white bg-slate-700 font-medium">All</button>
          <button id="sizeLargeBtn" class="px-2 py-0.5 rounded text-slate-400 hover:text-white">Large (&gt;$20M)</button>
          <button id="sizeSmallBtn" class="px-2 py-0.5 rounded text-slate-400 hover:text-white">Small/Mid</button>
        </div>

        <div class="relative w-44 sm:w-56">
          <input type="text" id="searchInput" placeholder="Search museum, city..." class="w-full bg-slate-950 border border-slate-700 rounded-lg px-2.5 py-1 text-xs text-white focus:outline-none focus:border-cyan-400 transition" />
          <button id="clearSearchBtn" class="hidden absolute right-2 top-1 text-slate-400 hover:text-white text-xs">✕</button>
        </div>
      </div>

    </div>
  </section>

  <!-- ACTIVE FILTER CHIPS BAR -->
  <section id="filterTagsBar" class="hidden px-4 py-1.5 bg-slate-950 border-b border-slate-800 text-xs">
    <div class="max-w-7xl mx-auto flex items-center gap-2 flex-wrap">
      <span class="text-slate-500 text-[11px]">Active Filters:</span>
      <div id="filterTagsContainer" class="flex items-center gap-1.5 flex-wrap"></div>
      <button id="clearAllFiltersBtn" class="text-cyan-400 hover:underline text-[11px] ml-2">Reset all</button>
    </div>
  </section>

  <!-- MAIN INTERACTION AREA -->
  <main class="flex-1 flex flex-col relative overflow-hidden">
    
    <!-- 3D GLOBE VIEW -->
    <div id="globeViewContainer" class="flex-1 flex flex-col md:flex-row relative">
      
      <!-- Interactive 3D Canvas Area -->
      <div class="flex-1 relative flex items-center justify-center bg-slate-950 overflow-hidden min-h-[500px]">
        <canvas id="globeCanvas" width="900" height="700" class="max-w-full max-h-full"></canvas>

        <!-- City Quick-Fly Overlay Bar -->
        <div class="absolute top-4 left-4 right-4 flex items-center gap-1.5 overflow-x-auto custom-scrollbar pb-1 z-20 pointer-events-auto">
          <span class="text-[11px] font-mono text-slate-400 whitespace-nowrap bg-slate-900/80 px-2 py-0.5 rounded-md border border-slate-800">
            Top Cities:
          </span>
          <div class="flex items-center gap-1 flex-nowrap">
            <button class="city-shortcut px-2 py-0.5 rounded-full bg-slate-900/80 hover:bg-emerald-950 border border-slate-800 hover:border-emerald-500/50 text-[11px] text-emerald-300 backdrop-blur transition flex items-center gap-1" data-city="New York">
              <span>New York</span> <span class="text-emerald-400 font-mono text-[10px]">11</span>
            </button>
            <button class="city-shortcut px-2 py-0.5 rounded-full bg-slate-900/80 hover:bg-emerald-950 border border-slate-800 hover:border-emerald-500/50 text-[11px] text-emerald-300 backdrop-blur transition flex items-center gap-1" data-city="London">
              <span>London</span> <span class="text-emerald-400 font-mono text-[10px]">8</span>
            </button>
            <button class="city-shortcut px-2 py-0.5 rounded-full bg-slate-900/80 hover:bg-emerald-950 border border-slate-800 hover:border-emerald-500/50 text-[11px] text-emerald-300 backdrop-blur transition flex items-center gap-1" data-city="Berlin">
              <span>Berlin</span> <span class="text-emerald-400 font-mono text-[10px]">4</span>
            </button>
            <button class="city-shortcut px-2 py-0.5 rounded-full bg-slate-900/80 hover:bg-emerald-950 border border-slate-800 hover:border-emerald-500/50 text-[11px] text-emerald-300 backdrop-blur transition flex items-center gap-1" data-city="Paris">
              <span>Paris</span> <span class="text-emerald-400 font-mono text-[10px]">4</span>
            </button>
            <button class="city-shortcut px-2 py-0.5 rounded-full bg-slate-900/80 hover:bg-emerald-950 border border-slate-800 hover:border-emerald-500/50 text-[11px] text-emerald-300 backdrop-blur transition flex items-center gap-1" data-city="Tokyo">
              <span>Tokyo</span> <span class="text-emerald-400 font-mono text-[10px]">3</span>
            </button>
          </div>
        </div>

        <!-- Globe Tools Overlay -->
        <div class="absolute bottom-5 left-5 flex flex-col gap-2 bg-slate-900/80 border border-slate-800 p-1.5 rounded-xl shadow-xl backdrop-blur z-20">
          <button id="zoomInBtn" class="w-8 h-8 rounded-lg bg-slate-800 hover:bg-slate-700 text-white flex items-center justify-center font-bold transition" title="Zoom In">+</button>
          <button id="zoomOutBtn" class="w-8 h-8 rounded-lg bg-slate-800 hover:bg-slate-700 text-white flex items-center justify-center font-bold transition" title="Zoom Out">−</button>
          <button id="resetViewBtn" class="w-8 h-8 rounded-lg bg-slate-800 hover:bg-slate-700 text-white flex items-center justify-center transition" title="Reset View">◎</button>
          <button id="spinToggleBtn" class="w-8 h-8 rounded-lg bg-emerald-950/70 border border-emerald-600/50 hover:bg-emerald-900 text-emerald-300 flex items-center justify-center transition" title="Toggle Auto-Spin">↻</button>
        </div>

        <!-- Coordinates & Status -->
        <div class="absolute bottom-5 right-5 hidden sm:flex items-center gap-3 bg-slate-900/80 border border-slate-800 px-3 py-1.5 rounded-xl text-[11px] font-mono text-slate-400 backdrop-blur z-20">
          <span id="globeStatus">Drag to rotate · Click city to explore</span>
          <span class="text-slate-600">|</span>
          <span id="visibleCount" class="text-cyan-400">{len(institutions)} visible</span>
        </div>

        <!-- Tooltip -->
        <div id="globeTooltip" class="absolute pointer-events-none hidden z-30 bg-slate-900/95 border border-cyan-500/50 text-white px-3 py-2 rounded-lg shadow-xl text-xs max-w-xs backdrop-blur">
          <div id="tooltipName" class="font-semibold text-white"></div>
          <div id="tooltipMeta" class="text-[11px] text-slate-300"></div>
        </div>
      </div>

      <!-- Right Dossier Panel -->
      <aside id="dossierPanel" class="w-full md:w-96 border-t md:border-t-0 md:border-l border-slate-800 bg-slate-900/60 backdrop-blur flex flex-col z-20">
        <div class="p-3.5 border-b border-slate-800 flex items-center justify-between">
          <h2 class="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
            <span>🏛️</span> Institutional Dossier
          </h2>
          <span id="dossierTierBadge" class="hidden text-[10px] font-semibold px-2 py-0.5 rounded-full border"></span>
        </div>

        <div id="dossierContent" class="p-4 flex-1 flex flex-col justify-center text-slate-400 text-xs">
          <div class="text-center py-8">
            <div class="w-12 h-12 mx-auto rounded-full bg-slate-800/80 border border-slate-700 flex items-center justify-center text-xl mb-3 text-cyan-400">
              🏛️
            </div>
            <p class="font-medium text-slate-300">No institution selected</p>
            <p class="text-[11px] text-slate-500 mt-1 max-w-[200px] mx-auto">
              Click any city pill or institution dot on the globe to inspect its ethical funding profile.
            </p>
          </div>
        </div>
      </aside>

    </div>

    <!-- TABLE / LIST VIEW -->
    <div id="listViewContainer" class="hidden flex-1 overflow-auto p-4 max-w-7xl mx-auto w-full">
      <div class="rounded-xl border border-slate-800 bg-slate-900/80 overflow-hidden shadow-2xl">
        <table class="w-full text-left text-xs text-slate-300">
          <thead class="bg-slate-800/90 text-slate-400 uppercase font-semibold text-[11px] border-b border-slate-700">
            <tr>
              <th class="p-3.5">Institution</th>
              <th class="p-3.5">City</th>
              <th class="p-3.5">Country</th>
              <th class="p-3.5">Tier</th>
              <th class="p-3.5">Size</th>
              <th class="p-3.5">Funding Breakdown</th>
              <th class="p-3.5">Watch / Notes</th>
              <th class="p-3.5">Sources</th>
            </tr>
          </thead>
          <tbody id="tableBody" class="divide-y divide-slate-800/60 font-sans">
            <!-- populated by JS -->
          </tbody>
        </table>
      </div>
    </div>

  </main>

  <!-- CONCIERGE CHAT OVERLAY MODAL -->
  <div id="conciergeModal" class="fixed bottom-5 right-5 w-[92vw] sm:w-[460px] h-[580px] max-h-[85vh] bg-slate-950/95 border border-cyan-500/40 rounded-2xl shadow-2xl backdrop-blur-xl flex flex-col z-50 transition-all duration-300 transform translate-y-4 opacity-0 pointer-events-none">
    
    <div class="p-3.5 border-b border-slate-800 flex items-center justify-between bg-slate-900/80 rounded-t-2xl">
      <div class="flex items-center gap-2.5">
        <div class="w-2.5 h-2.5 rounded-full bg-emerald-400 shadow-[0_0_8px_#00ff87] animate-pulse"></div>
        <div>
          <h3 class="text-xs font-semibold text-white tracking-wide">Atlas AI Concierge</h3>
          <span id="chatModeTag" class="text-[9px] uppercase px-1.5 py-0.5 rounded bg-emerald-950 text-emerald-400 border border-emerald-800 font-mono">
            {len(sorted_cities)} Cities Ready
          </span>
        </div>
      </div>
      <div class="flex items-center gap-1.5">
        <button id="chatSettingsBtn" class="text-slate-400 hover:text-white p-1 rounded" title="Settings / API Key">⚙️</button>
        <button id="chatClearBtn" class="text-slate-400 hover:text-white p-1 rounded" title="Clear chat">🗑️</button>
        <button id="chatCloseBtn" class="text-slate-400 hover:text-white p-1 rounded text-base" title="Close">✕</button>
      </div>
    </div>

    <div id="chatMessages" class="flex-1 overflow-y-auto p-4 space-y-3.5 text-xs">
      <div class="flex flex-col gap-1 items-start">
        <div class="bg-slate-800/90 border border-slate-700/80 text-slate-200 p-3.5 rounded-2xl rounded-tl-sm max-w-[92%] leading-relaxed shadow-md">
          <p class="font-semibold text-white mb-1">Hello! I am your Culture Atlas Concierge.</p>
          <p class="text-slate-300">
            Ask me for research on <strong>MoMA</strong>, examine funding for any museum, or explore across <strong>{len(sorted_cities)} cities</strong> worldwide.
          </p>
          <div class="mt-3 flex flex-col gap-1.5">
            <button class="chat-preset text-left px-2.5 py-1.5 rounded-lg bg-amber-950/60 hover:bg-amber-900/70 border border-amber-600/50 text-amber-300 hover:text-amber-100 transition font-medium">
              🏛️ Tell research about MoMA
            </button>
            <button class="chat-preset text-left px-2.5 py-1.5 rounded-lg bg-slate-900/80 hover:bg-emerald-950/60 border border-slate-700 hover:border-emerald-600/50 text-slate-300 hover:text-white transition">
              🏙️ What museums are in London or New York?
            </button>
            <button class="chat-preset text-left px-2.5 py-1.5 rounded-lg bg-slate-900/80 hover:bg-emerald-950/60 border border-slate-700 hover:border-emerald-600/50 text-slate-300 hover:text-white transition">
              🇩🇰 Explore museums in Aarhus & Copenhagen
            </button>
            <button class="chat-preset text-left px-2.5 py-1.5 rounded-lg bg-slate-900/80 hover:bg-emerald-950/60 border border-slate-700 hover:border-emerald-600/50 text-slate-300 hover:text-white transition">
              ⚖️ How is funding transparency evaluated?
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Settings Overlay -->
    <div id="settingsOverlay" class="absolute inset-0 bg-slate-950/95 backdrop-blur-md p-4 rounded-2xl hidden flex-col gap-3 z-20">
      <div class="flex items-center justify-between border-b border-slate-800 pb-2">
        <h4 class="text-xs font-semibold text-white uppercase tracking-wider">Concierge Settings</h4>
        <button id="closeSettingsOverlay" class="text-slate-400 hover:text-white">✕</button>
      </div>
      <div class="flex flex-col gap-1 text-xs">
        <label class="text-slate-300 font-medium">Google Gemini API Key (Optional)</label>
        <input type="password" id="geminiApiKeyInput" placeholder="AIzaSy..." class="bg-slate-900 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-white focus:outline-none focus:border-cyan-400" />
        <p class="text-[11px] text-slate-500 mt-1">
          Add your key from <a href="https://aistudio.google.com/app/apikey" target="_blank" class="text-cyan-400 underline">Google AI Studio</a> for advanced open-ended reasoning.
        </p>
      </div>
      <button id="saveSettingsBtn" class="mt-2 w-full py-1.5 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white font-medium text-xs transition">
        Save Settings
      </button>
    </div>

    <!-- Chat Input Bar -->
    <div class="p-3 border-t border-slate-800 bg-slate-950/80 rounded-b-2xl flex items-center gap-2">
      <input type="text" id="chatInput" placeholder="Ask: 'research about MoMA', 'London', 'Te Papa'..." class="flex-1 bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-emerald-400 transition" />
      <button id="chatVoiceBtn" class="p-2 text-slate-400 hover:text-cyan-400 rounded-lg border border-slate-800 hover:border-slate-700 transition" title="Voice Input">
        🎙️
      </button>
      <button id="chatSendBtn" class="px-3 py-2 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-xs transition shadow-lg">
        Send
      </button>
    </div>

  </div>

  <!-- APPLICATION SCRIPTS -->
  <script>
    // Embed the complete dataset directly
    const ALL_INSTITUTIONS = {json.dumps(institutions)};
    const WORLD_ARCS = {json.dumps(arcs_downsampled)};
    const COUNTRY_LIST = {json.dumps(final_countries)};
    const CITY_LIST = {json.dumps(sorted_cities)};

    // App State
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
      viewGlobeBtn.className = 'px-3 py-1 rounded-md font-medium transition bg-cyan-600 text-white shadow';
      viewListBtn.className = 'px-3 py-1 rounded-md font-medium text-slate-400 hover:text-white transition';
      globeViewContainer.classList.remove('hidden');
      listViewContainer.classList.add('hidden');
    }});

    viewListBtn.addEventListener('click', () => {{
      viewListBtn.className = 'px-3 py-1 rounded-md font-medium transition bg-cyan-600 text-white shadow';
      viewGlobeBtn.className = 'px-3 py-1 rounded-md font-medium text-slate-400 hover:text-white transition';
      listViewContainer.classList.remove('hidden');
      globeViewContainer.classList.add('hidden');
      renderTable();
    }});

    // Populate Country & City Dropdowns
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

    countrySelect.addEventListener('change', e => {{
      setCountryFilter(e.target.value);
    }});

    citySelect.addEventListener('change', e => {{
      setCityFilter(e.target.value);
    }});

    // City Quick Shortcut buttons
    document.querySelectorAll('.city-shortcut').forEach(btn => {{
      btn.addEventListener('click', () => {{
        const cityName = btn.getAttribute('data-city');
        setCityFilter(cityName);
      }});
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
        if (selectedTier === 'all' || selectedTier === t) {{
          chip.style.opacity = '1';
        }} else {{
          chip.style.opacity = '0.35';
        }}
      }});
    }}

    // Size filtering
    const sizeAllBtn = document.getElementById('sizeAllBtn');
    const sizeLargeBtn = document.getElementById('sizeLargeBtn');
    const sizeSmallBtn = document.getElementById('sizeSmallBtn');

    function setSizeFilter(size) {{
      selectedSize = size;
      [sizeAllBtn, sizeLargeBtn, sizeSmallBtn].forEach(b => {{
        b.className = 'px-2 py-0.5 rounded text-slate-400 hover:text-white';
      }});
      if (size === 'all') sizeAllBtn.className = 'px-2 py-0.5 rounded text-white bg-slate-700 font-medium';
      if (size === 'L') sizeLargeBtn.className = 'px-2 py-0.5 rounded text-white bg-slate-700 font-medium';
      if (size === 'S') sizeSmallBtn.className = 'px-2 py-0.5 rounded text-white bg-slate-700 font-medium';
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

    // Active filters bar
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

      document.getElementById('visibleCount').textContent = `${{filteredInstitutions.length}} visible`;

      // Render tags
      const tags = [];
      if (selectedCountry !== 'all') tags.push({{ label: `Country: ${{selectedCountry}}`, clear: () => setCountryFilter('all') }});
      if (selectedCity !== 'all') tags.push({{ label: `City: ${{selectedCity}}`, clear: () => setCityFilter('all') }});
      if (selectedTier !== 'all') tags.push({{ label: `Tier: ${{selectedTier === 'A' ? 'Verified' : selectedTier === 'B' ? 'One Name' : 'Unverified'}}`, clear: () => {{ selectedTier = 'all'; updateTierButtons(); applyFilters(); }} }});
      if (selectedSize !== 'all') tags.push({{ label: `Size: ${{selectedSize === 'L' ? 'Large' : 'Small/Mid'}}`, clear: () => setSizeFilter('all') }});
      if (searchQuery) tags.push({{ label: `"${{searchQuery}}"`, clear: () => {{ searchInput.value = ''; searchQuery = ''; clearSearchBtn.classList.add('hidden'); applyFilters(); }} }});

      if (tags.length > 0) {{
        filterTagsBar.classList.remove('hidden');
        filterTagsContainer.innerHTML = tags.map((t, idx) => `
          <span class="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-slate-800 text-cyan-300 border border-slate-700 text-[11px]">
            ${{t.label}}
            <button class="remove-tag text-slate-400 hover:text-white" data-idx="${{idx}}">✕</button>
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

    // Table View Renderer
    function renderTable() {{
      const tbody = document.getElementById('tableBody');
      if (filteredInstitutions.length === 0) {{
        tbody.innerHTML = `<tr><td colspan="8" class="text-center py-12 text-slate-500">No institutions match the current filters.</td></tr>`;
        return;
      }}
      tbody.innerHTML = filteredInstitutions.map(inst => `
        <tr class="hover:bg-slate-800/50 transition cursor-pointer" onclick="handleTableSelect('${{inst.name.replace(/'/g, "\\\\'")}}')">
          <td class="p-3.5 font-semibold text-white">${{inst.name}}</td>
          <td class="p-3.5 text-cyan-300 font-mono text-[11px]">${{inst.city}}</td>
          <td class="p-3.5 text-slate-400 font-mono text-[11px]">${{inst.country}}</td>
          <td class="p-3.5">
            <span class="inline-block px-2 py-0.5 rounded-full text-[10px] font-bold border ${{inst.tier === 'A' ? 'bg-emerald-950/80 text-emerald-400 border-emerald-600' : inst.tier === 'B' ? 'bg-blue-950/80 text-blue-400 border-blue-600' : 'bg-slate-800 text-slate-400 border-slate-700'}}">
              ${{inst.tier === 'A' ? 'Verified' : inst.tier === 'B' ? 'One Name' : 'Unverified'}}
            </span>
          </td>
          <td class="p-3.5 text-slate-400 text-xs">${{inst.size === 'L' ? 'Large' : 'Small/Mid'}}</td>
          <td class="p-3.5 text-slate-300 max-w-xs truncate" title="${{inst.funding}}">${{inst.funding}}</td>
          <td class="p-3.5 text-slate-400 max-w-xs truncate" title="${{inst.watch || ''}}">${{inst.watch || '—'}}</td>
          <td class="p-3.5">
            ${{(inst.sources || []).map(u => `<a href="${{u}}" target="_blank" class="text-cyan-400 hover:underline mr-1 text-xs">↗</a>`).join('')}}
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

    // 3D Canvas Globe
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
        rotLon = (rotLon + 0.25) % 360;
      }}

      // Glow atmosphere
      const glow = ctx.createRadialGradient(cx, cy, r * 0.85, cx, cy, r * 1.25);
      glow.addColorStop(0, 'rgba(0, 242, 254, 0.22)');
      glow.addColorStop(0.5, 'rgba(0, 255, 135, 0.08)');
      glow.addColorStop(1, 'transparent');
      ctx.fillStyle = glow;
      ctx.beginPath();
      ctx.arc(cx, cy, r * 1.25, 0, Math.PI * 2);
      ctx.fill();

      // Deep Ocean Sphere
      const ocean = ctx.createRadialGradient(cx - r * 0.35, cy - r * 0.35, r * 0.1, cx, cy, r);
      ocean.addColorStop(0, '#022144');
      ocean.addColorStop(0.65, '#001124');
      ocean.addColorStop(1, '#000814');
      ctx.fillStyle = ocean;
      ctx.beginPath();
      ctx.arc(cx, cy, r, 0, Math.PI * 2);
      ctx.fill();

      // Clip inside globe for graticules & borders
      ctx.save();
      ctx.beginPath();
      ctx.arc(cx, cy, r, 0, Math.PI * 2);
      ctx.clip();

      // Graticules
      ctx.strokeStyle = 'rgba(0, 255, 135, 0.12)';
      ctx.lineWidth = 0.65;
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

      // 🌍 Draw 591 Country Boundaries & Coastlines
      ctx.strokeStyle = 'rgba(0, 242, 254, 0.45)';
      ctx.lineWidth = 0.9;
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
        const cty = CITY_LIST.find(c => c.name.toLowerCase() === selectedCity.toLowerCase());
        if (cty) {{
          const pt = project(cty.lon, cty.lat, r, cx, cy);
          if (pt) {{
            ctx.beginPath();
            ctx.arc(pt.x, pt.y, 14, 0, Math.PI * 2);
            ctx.strokeStyle = '#f59e0b';
            ctx.lineWidth = 2.5;
            ctx.stroke();
          }}
        }}
      }}

      ctx.restore();

      // Atmospheric Rim
      ctx.strokeStyle = 'rgba(0, 242, 254, 0.65)';
      ctx.lineWidth = 1.8;
      ctx.beginPath();
      ctx.arc(cx, cy, r, 0, Math.PI * 2);
      ctx.stroke();

      // Institution Dots
      filteredInstitutions.forEach(inst => {{
        const pt = project(inst.lon, inst.lat, r, cx, cy);
        if (!pt) return;

        const isSel = selectedInstitution && selectedInstitution.name === inst.name;
        const isHov = hoveredInstitution && hoveredInstitution.name === inst.name;
        const dotR = (isSel ? 7.5 : isHov ? 6 : inst.size === 'L' ? 4.5 : 3.2) * Math.min(1.4, Math.max(0.65, pt.depth));

        let col = '#00ff87'; // Tier A Verified
        if (inst.tier === 'B') col = '#4589ff'; // Tier B One Name
        if (inst.tier === 'U') col = '#8d8d8d'; // Tier U Unverified

        if (isSel) {{
          ctx.beginPath();
          ctx.arc(pt.x, pt.y, dotR * 2.4, 0, Math.PI * 2);
          ctx.strokeStyle = '#ffffff';
          ctx.lineWidth = 2;
          ctx.stroke();

          ctx.beginPath();
          ctx.arc(pt.x, pt.y, dotR * 3.4, 0, Math.PI * 2);
          ctx.strokeStyle = 'rgba(0, 255, 135, 0.5)';
          ctx.lineWidth = 1.2;
          ctx.stroke();
        }}

        ctx.beginPath();
        ctx.arc(pt.x, pt.y, dotR, 0, Math.PI * 2);
        ctx.fillStyle = col;
        ctx.shadowColor = col;
        ctx.shadowBlur = isSel ? 15 : isHov ? 10 : 4;
        ctx.fill();
        ctx.shadowBlur = 0;
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

      // Populate right dossier panel
      const dossierContent = document.getElementById('dossierContent');
      const badge = document.getElementById('dossierTierBadge');

      badge.classList.remove('hidden');
      badge.textContent = inst.tier === 'A' ? 'Verified Tier A' : inst.tier === 'B' ? 'One Name Tier B' : 'Unverified Tier U';
      badge.className = `text-[10px] font-semibold px-2 py-0.5 rounded-full border ${{inst.tier === 'A' ? 'bg-emerald-950/80 text-emerald-400 border-emerald-600' : inst.tier === 'B' ? 'bg-blue-950/80 text-blue-400 border-blue-600' : 'bg-slate-800 text-slate-300 border-slate-700'}}`;

      dossierContent.innerHTML = `
        <div class="space-y-4">
          <div>
            <h3 class="font-bold text-white text-base leading-snug">${{inst.name}}</h3>
            <p class="text-xs text-cyan-400 mt-1 flex items-center gap-1">
              <span>📍</span> <span>${{inst.location}}</span>
              <span class="text-slate-500">·</span>
              <span class="text-slate-300">${{inst.size === 'L' ? 'Large (>$20M)' : 'Small/Mid'}}</span>
            </p>
          </div>

          <div class="bg-slate-950/80 p-3 rounded-xl border border-slate-800 space-y-1">
            <span class="text-[10px] font-bold text-emerald-400 uppercase tracking-wider block">Funding Architecture</span>
            <p class="text-xs text-slate-300 leading-relaxed">${{inst.funding}}</p>
          </div>

          ${{inst.watch ? `
            <div class="bg-slate-950/80 p-3 rounded-xl border border-slate-800 space-y-1">
              <span class="text-[10px] font-bold text-cyan-400 uppercase tracking-wider block">Watch Notes & Scrutiny</span>
              <p class="text-xs text-slate-300 leading-relaxed">${{inst.watch}}</p>
            </div>
          ` : ''}}

          <div class="pt-2 border-t border-slate-800">
            <span class="text-[10px] font-bold text-slate-400 uppercase tracking-wider block mb-2">Sources & Filings</span>
            <div class="flex flex-col gap-1.5">
              ${{(inst.sources || []).map(u => {{
                let domain = u;
                try {{ domain = new URL(u).hostname.replace(/^www\\./, ''); }} catch(e){{}}
                return `<a href="${{u}}" target="_blank" class="text-cyan-400 hover:underline text-xs flex items-center gap-1"><span>↗</span> <span>${{domain}}</span></a>`;
              }}).join('')}}
            </div>
          </div>
        </div>
      `;
    }}

    // Pointer events for Canvas
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
          if (pt && Math.hypot(pt.x - mx, pt.y - my) < 10) {{
            hit = inst;
            break;
          }}
        }}

        hoveredInstitution = hit;
        const tooltip = document.getElementById('globeTooltip');
        if (hit) {{
          tooltip.classList.remove('hidden');
          tooltip.style.left = `${{mx + 15}}px`;
          tooltip.style.top = `${{my + 10}}px`;
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

    // AI CONCIERGE LOGIC
    const conciergeModal = document.getElementById('conciergeModal');
    const toggleConciergeBtn = document.getElementById('toggleConciergeBtn');
    const chatCloseBtn = document.getElementById('chatCloseBtn');
    const chatMessages = document.getElementById('chatMessages');
    const chatInput = document.getElementById('chatInput');
    const chatSendBtn = document.getElementById('chatSendBtn');
    const chatClearBtn = document.getElementById('chatClearBtn');

    function openConcierge() {{
      conciergeModal.classList.remove('pointer-events-none', 'opacity-0', 'translate-y-4');
      conciergeModal.classList.add('opacity-100', 'translate-y-0');
      setTimeout(() => chatInput.focus(), 150);
    }}

    function closeConcierge() {{
      conciergeModal.classList.add('pointer-events-none', 'opacity-0', 'translate-y-4');
      conciergeModal.classList.remove('opacity-100', 'translate-y-0');
    }}

    toggleConciergeBtn.addEventListener('click', openConcierge);
    chatCloseBtn.addEventListener('click', closeConcierge);

    // Keyboard shortcut Cmd+K / Ctrl+K
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
      appendBotMessage("Chat history cleared. How can I help you explore cultural funding?");
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
        <div class="bg-emerald-600 text-white p-3 rounded-2xl rounded-tr-sm max-w-[85%] text-xs leading-relaxed shadow">
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
          <div class="mt-2.5 flex flex-wrap gap-1.5">
            ${{actions.map((act, i) => `
              <button class="chat-act-btn px-2.5 py-1 rounded-full text-[11px] font-semibold flex items-center gap-1 border transition ${{act.tier === 'A' ? 'bg-emerald-950/80 text-emerald-300 border-emerald-600 hover:bg-emerald-900' : act.tier === 'B' ? 'bg-blue-950/80 text-blue-300 border-blue-600 hover:bg-blue-900' : 'bg-slate-800 text-cyan-300 border-slate-700 hover:bg-slate-700'}}" data-act-idx="${{i}}">
                ${{act.icon || '📍'}} ${{act.label}}
              </button>
            `).join('')}}
          </div>
        `;
      }}

      div.innerHTML = `
        <div class="bg-slate-800/90 border border-slate-700/80 text-slate-200 p-3 rounded-2xl rounded-tl-sm max-w-[92%] leading-relaxed shadow-md">
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
      typing.className = 'flex gap-1.5 p-2 bg-slate-800/60 rounded-xl w-14';
      typing.innerHTML = '<span class="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-ping"></span><span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping"></span>';
      chatMessages.appendChild(typing);
      chatMessages.scrollTop = chatMessages.scrollHeight;

      setTimeout(() => {{
        typing.remove();
        runOfflineLogic(query);
      }}, 250);
    }}

    // Match institution by acronyms, aliases, or clean tokens
    function findInstitution(rawQuery) {{
      const raw = rawQuery.toLowerCase().trim();

      // 1. Direct match on name or explicit aliases
      for (const inst of ALL_INSTITUTIONS) {{
        const names = [inst.name.toLowerCase(), ...(inst.aliases || [])];
        for (const a of names) {{
          if (raw.includes(a) || (raw.length > 3 && a.includes(raw))) {{
            return inst;
          }}
        }}
      }}

      // 2. Token match after filtering common query words
      const stopWords = new Set(['tell', 'research', 'about', 'museum', 'the', 'a', 'an', 'what', 'who', 'how', 'is', 'are', 'in', 'at', 'on', 'show', 'me', 'details', 'info', 'it', 'need', 'to', 'give', 'any']);
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

      // 1. Specific institution check (MoMA, Te Papa, Met, ARoS, etc.)
      const matchInst = findInstitution(q);

      if (matchInst) {{
        if (matchInst.name.toLowerCase().includes('moma')) {{
          response = `
            <div class="space-y-2">
              <div class="flex items-center justify-between border-b border-slate-700/60 pb-1.5">
                <div>
                  <h3 class="font-bold text-white text-sm">MoMA (The Museum of Modern Art)</h3>
                  <p class="text-[11px] text-cyan-300">📍 Midtown Manhattan, New York, USA</p>
                </div>
                <span class="px-2 py-0.5 rounded text-[10px] font-bold bg-blue-950 text-blue-300 border border-blue-600">
                  Tier B · High Scrutiny
                </span>
              </div>

              <!-- Funding Scale -->
              <div class="bg-slate-900/90 p-2.5 rounded-xl border border-slate-700/70 text-xs space-y-1">
                <span class="text-emerald-400 font-bold uppercase tracking-wider text-[10px] block">💰 Funding Structure & Scale</span>
                <p class="text-slate-300 leading-relaxed">
                  <strong>Budget & Endowment:</strong> Operating budget of ~$180M+ annually with an endowment exceeding $1.2 Billion. 
                </p>
                <p class="text-slate-300 leading-relaxed">
                  <strong>Revenue Mix:</strong> Admissions & membership (~30%), endowment income (~35%), philanthropic board gifts (~20%), retail/licensing (~15%).
                </p>
                <p class="text-slate-300 leading-relaxed">
                  <strong>Corporate Underwriters:</strong> Bloomberg Philanthropies, Hyundai Card, UNIQLO (title partner for free Friday <em>'UNIQLO NYC Nights'</em>), Cartier, Bank of America, Chanel, Volkswagen Group, Allianz.
                </p>
              </div>

              <!-- Ethical Scrutiny & Watch Notes -->
              <div class="bg-amber-950/30 p-2.5 rounded-xl border border-amber-500/40 text-xs space-y-1.5">
                <span class="text-amber-400 font-bold uppercase tracking-wider text-[10px] flex items-center gap-1">
                  ⚠️ Critical Ethical Research & Controversies
                </span>
                <p class="text-slate-200 leading-relaxed">
                  • <strong>Leon Black & Jeffrey Epstein:</strong> MoMA former Board Chairman Leon Black stepped down in March 2021 after intense public outrage over $158 million paid to Jeffrey Epstein between 2012 and 2017.
                </p>
                <p class="text-slate-200 leading-relaxed">
                  • <strong>'Strike MoMA' (Spring 2021):</strong> Activist coalition (Decolonize This Place, Strike MoMA, Artists Space allies) launched 10 weeks of protests demanding the removal of ethically compromised trustees and institutional transformation.
                </p>
                <p class="text-slate-200 leading-relaxed">
                  • <strong>Controversial Board Members:</strong> 
                  <span class="text-slate-300">Steven Tananbaum (GoldenTree hedge fund / Puerto Rico sovereign debt crisis), Larry Fink (BlackRock CEO / fossil fuel & defense investments), Paula Crown (General Dynamics defense family).</span>
                </p>
              </div>
            </div>
          `;
        }} else {{
          response = `
            <div class="space-y-2">
              <div class="flex items-center justify-between border-b border-slate-700/60 pb-1.5">
                <div>
                  <h3 class="font-bold text-white text-sm">${{matchInst.name}}</h3>
                  <p class="text-[11px] text-cyan-300">📍 ${{matchInst.location}} (${{matchInst.size === 'L' ? 'Large >$20M' : 'Small/Mid'}})</p>
                </div>
                <span class="px-2 py-0.5 rounded text-[10px] font-bold border ${{matchInst.tier === 'A' ? 'bg-emerald-950 text-emerald-300 border-emerald-600' : matchInst.tier === 'B' ? 'bg-blue-950 text-blue-300 border-blue-600' : 'bg-slate-800 text-slate-300 border-slate-600'}}">
                  ${{matchInst.tier === 'A' ? 'Tier A · Verified' : matchInst.tier === 'B' ? 'Tier B · One Name' : 'Tier U · Unverified'}}
                </span>
              </div>
              <div class="bg-slate-900/90 p-2.5 rounded-xl border border-slate-700/70 text-xs">
                <span class="text-emerald-400 font-bold uppercase tracking-wider text-[10px] block mb-0.5">Funding Breakdown</span>
                <p class="text-slate-300 leading-relaxed">${{matchInst.funding}}</p>
              </div>
              ${{matchInst.watch ? `
                <div class="bg-amber-950/30 p-2.5 rounded-xl border border-amber-500/40 text-xs">
                  <span class="text-amber-400 font-bold uppercase tracking-wider text-[10px] block mb-0.5">⚠️ Watch Notes & Governance</span>
                  <p class="text-slate-300 leading-relaxed">${{matchInst.watch}}</p>
                </div>
              ` : ''}}
            </div>
          `;
        }}

        actions.push({{
          label: `Fly to ${{matchInst.name}} on Globe`,
          icon: '📍',
          tier: matchInst.tier,
          handler: () => {{
            viewGlobeBtn.click();
            selectInstitution(matchInst);
          }}
        }});
        actions.push({{
          label: `Explore ${{matchInst.city}} (${{matchInst.country}})`,
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

      // 2. Check City query
      const matchCity = CITY_LIST.find(c => q.includes(c.name.toLowerCase()));
      if (matchCity) {{
        const cityInsts = ALL_INSTITUTIONS.filter(i => i.city.toLowerCase() === matchCity.name.toLowerCase());
        response = `
          <p class="font-bold text-white">🏙️ ${{matchCity.name}}, ${{matchCity.country}} (${{cityInsts.length}} institution${{cityInsts.length > 1 ? 's' : ''}})</p>
          <ul class="mt-1.5 space-y-1 text-slate-300 text-xs">
            ${{cityInsts.map(i => `
              <li><strong>${{i.name}}</strong> <span class="${{i.tier === 'A' ? 'text-emerald-400' : 'text-blue-400'}}">(${{i.tier === 'A' ? 'Verified' : 'One Name'}})</span> · ${{i.size === 'L' ? 'Large' : 'Small/Mid'}}</li>
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

      // 3. Check Country query
      const matchCountry = COUNTRY_LIST.find(c => {{
        const cLow = c.name.toLowerCase();
        return q.includes(cLow) || (cLow === 'usa' && (q.includes('united states') || q.includes('america'))) || (cLow === 'uk' && (q.includes('united kingdom') || q.includes('britain')));
      }});

      if (matchCountry && (q.includes('country') || q.includes('in ') || q.includes(matchCountry.name.toLowerCase()))) {{
        const countryInsts = ALL_INSTITUTIONS.filter(i => i.country.toLowerCase() === matchCountry.name.toLowerCase());
        response = `
          <p class="font-bold text-white">🌍 ${{matchCountry.name}} (${{countryInsts.length}} institutions mapped)</p>
          <ul class="mt-1.5 space-y-1 text-slate-300 text-xs">
            ${{countryInsts.slice(0, 4).map(i => `
              <li><strong>${{i.name}}</strong> <span class="${{i.tier === 'A' ? 'text-emerald-400' : 'text-blue-400'}}">(${{i.tier === 'A' ? 'Verified' : 'One Name'}})</span> — ${{i.city}}</li>
            `).join('')}}
          </ul>
          ${{countryInsts.length > 4 ? `<p class="text-[11px] text-slate-400 mt-1">...and ${{countryInsts.length - 4}} more.</p>` : ''}}
        `;
        actions.push({{
          label: `Fly to ${{matchCountry.name}}`,
          icon: '📍',
          handler: () => {{
            viewGlobeBtn.click();
            setCountryFilter(matchCountry.name);
          }}
        }});
        countryInsts.slice(0, 2).forEach(inst => {{
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
        setCountryFilter(matchCountry.name);
        return;
      }}

      // 4. Fallback
      response = `
        <p class="font-bold text-white">Culture Atlas Concierge</p>
        <p class="text-xs text-slate-300 mt-1">Ask me about any museum, city, or sponsor:</p>
        <ul class="mt-1 space-y-1 text-xs text-cyan-300">
          <li>• "Tell research about MoMA"</li>
          <li>• "What museums are in London, Paris, or Tokyo?"</li>
          <li>• "Show institutions in Vienna or Berlin"</li>
          <li>• "Tell me about Te Papa or ARoS"</li>
        </ul>
      `;
      actions.push({{
        label: 'Surprise Me',
        icon: '✨',
        handler: () => {{
          const pick = ALL_INSTITUTIONS[Math.floor(Math.random() * ALL_INSTITUTIONS.length)];
          runOfflineLogic(`Tell me about ${{pick.name}}`);
        }}
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
    f.write(app_html)

with open('/Users/polinavasilyeva/.gemini/antigravity/brain/b997e616-4551-453e-83cc-4ba184f90abf/culture_atlas_app.html', 'w') as f:
    f.write(app_html)

print("Updated app/index.html and culture_atlas_app.html with MoMA research and enhanced query matching!")
