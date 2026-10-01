import json
from collections import Counter

# Load TopoJSON
with open('/Users/polinavasilyeva/.gemini/antigravity/scratch/sponsor-atlas/app/world-topo.json') as f:
    topo = json.load(f)

# Load institutions
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

# Normalize institutions country
inst_countries = {}
for inst in institutions:
    parts = [p.strip() for p in inst['location'].split(',')]
    c_name = parts[-1] if len(parts) > 1 else parts[0]
    if c_name in ['USA', 'United States']:
        c_name = 'USA'
    elif c_name in ['UK', 'United Kingdom', 'England', 'Scotland', 'Wales']:
        c_name = 'UK'
    inst['country'] = c_name
    inst_countries[c_name] = inst_countries.get(c_name, 0) + 1

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
        
        # Match country alias
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

# Keep unique countries that have institutions + top global countries
unique_countries = {}
for c in country_list:
    n = c['name']
    if n not in unique_countries or c['count'] > unique_countries[n]['count']:
        unique_countries[n] = c

sorted_countries = sorted(unique_countries.values(), key=lambda x: (-x['count'], x['name']))

# Serialize
arcs_json = json.dumps(arcs_downsampled)
insts_json = json.dumps(institutions)
countries_json = json.dumps(sorted_countries)

print(f"Serialized {len(arcs_downsampled)} arcs, {len(institutions)} institutions, {len(sorted_countries)} countries")

# Build the complete standalone app template
def generate_full_html():
    return '''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <title>Culture Atlas — Countries & 3D Interactive Globe</title>
  <script src="https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js"></script>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
    
    :root {
      --bg: #030712;
      --card-bg: rgba(15, 23, 42, 0.88);
      --accent: #00ff87;
      --cyan: #00f2fe;
      --tier-a: #24a148;
      --tier-b: #4589ff;
      --tier-u: #8d8d8d;
    }

    body {
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
      background-color: var(--bg);
      color: #f1f5f9;
      margin: 0;
      padding: 0;
      overflow-x: hidden;
      -webkit-font-smoothing: antialiased;
    }

    #globeCanvas {
      cursor: grab;
      touch-action: none;
    }
    #globeCanvas.dragging {
      cursor: grabbing;
    }

    ::-webkit-scrollbar {
      width: 6px;
      height: 6px;
    }
    ::-webkit-scrollbar-track {
      background: rgba(0, 0, 0, 0.2);
    }
    ::-webkit-scrollbar-thumb {
      background: rgba(255, 255, 255, 0.15);
      border-radius: 9999px;
    }
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
              35 Countries Mapped
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
          <button id="viewListBtn" class="px-3 py-1 rounded-md font-medium transition text-slate-400 hover:text-white">
            Ledger Table
          </button>
        </div>

        <!-- Chat Concierge Toggle -->
        <button id="headerChatToggle" class="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-emerald-950/80 hover:bg-emerald-900 border border-emerald-600/50 text-xs text-emerald-300 font-medium transition shadow-[0_0_12px_rgba(0,255,135,0.25)]">
          <span class="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span>
          <span>Atlas AI Concierge</span>
          <span class="hidden md:inline text-[10px] opacity-75 font-mono">⌘K</span>
        </button>
      </div>

    </div>
  </header>

  <!-- FILTER & COUNTRY SELECTOR BAR -->
  <section class="border-b border-slate-800/80 bg-slate-900/50 px-4 py-2 text-xs">
    <div class="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-3">
      
      <!-- Left Filters: Tiers & Countries -->
      <div class="flex items-center gap-3 flex-wrap">
        
        <!-- Country Selector Dropdown -->
        <div class="flex items-center gap-1.5">
          <span class="text-slate-400 font-medium flex items-center gap-1">
            <span>🌍</span> Country:
          </span>
          <select id="countrySelect" class="bg-slate-950 border border-slate-700 rounded-lg px-2.5 py-1 text-xs text-white focus:outline-none focus:border-cyan-400 font-medium">
            <option value="all">All Countries (35)</option>
          </select>
        </div>

        <div class="h-4 w-[1px] bg-slate-800 hidden sm:block"></div>

        <!-- Tier Chips -->
        <div class="flex items-center gap-1.5 flex-wrap">
          <button id="tierABtn" class="tier-chip flex items-center gap-1 px-2 py-0.5 rounded-full border border-emerald-500/40 bg-emerald-950/40 text-emerald-300 hover:bg-emerald-900/60 transition" data-tier="A">
            <span class="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
            <span>Verified</span>
            <span class="font-mono text-[10px] opacity-75 ml-0.5">125</span>
          </button>
          <button id="tierBBtn" class="tier-chip flex items-center gap-1 px-2 py-0.5 rounded-full border border-blue-500/40 bg-blue-950/40 text-blue-300 hover:bg-blue-900/60 transition" data-tier="B">
            <span class="w-1.5 h-1.5 rounded-full bg-blue-400"></span>
            <span>One Name</span>
            <span class="font-mono text-[10px] opacity-75 ml-0.5">55</span>
          </button>
          <button id="tierUBtn" class="tier-chip flex items-center gap-1 px-2 py-0.5 rounded-full border border-slate-500/40 bg-slate-900/40 text-slate-300 hover:bg-slate-800 transition" data-tier="U">
            <span class="w-1.5 h-1.5 rounded-full bg-slate-400"></span>
            <span>Unverified</span>
            <span class="font-mono text-[10px] opacity-75 ml-0.5">17</span>
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

  <!-- ACTIVE FILTER CHIPS BAR (Dynamic) -->
  <div id="activeFilterBar" class="hidden border-b border-slate-800/60 bg-slate-950/70 px-4 py-1.5 text-xs">
    <div class="max-w-7xl mx-auto flex items-center gap-2">
      <span class="text-slate-400 text-[11px]">Filtered:</span>
      <span id="activeCountryBadge" class="hidden items-center gap-1.5 px-2 py-0.5 rounded-full bg-cyan-950 text-cyan-300 border border-cyan-800 text-[11px]">
        <span id="activeCountryLabel"></span>
        <button id="clearCountryBtn" class="hover:text-white">✕</button>
      </span>
      <button id="clearAllFiltersBtn" class="text-slate-500 hover:text-slate-300 underline text-[11px] ml-auto">Clear all filters</button>
    </div>
  </div>

  <!-- MAIN VIEWPORT -->
  <main class="flex-1 flex flex-col relative overflow-hidden">
    
    <!-- 3D GLOBE VIEW -->
    <div id="globeViewContainer" class="flex-1 flex flex-col md:flex-row h-full min-h-[550px] relative">
      
      <!-- Globe canvas wrapper -->
      <div class="relative flex-1 bg-slate-950 flex items-center justify-center overflow-hidden min-h-[420px]">
        <canvas id="globeCanvas" class="w-full h-full max-h-[85vh]"></canvas>

        <!-- Quick Country Shortcuts (Top Left of Globe) -->
        <div class="absolute top-4 left-4 hidden lg:flex flex-wrap gap-1.5 max-w-sm z-20 pointer-events-auto">
          <button class="country-shortcut px-2 py-1 rounded-lg bg-slate-900/80 hover:bg-slate-800 border border-slate-800 hover:border-cyan-500/50 text-[11px] text-slate-300 backdrop-blur transition flex items-center gap-1" data-country="USA">
            <span>🇺🇸</span> USA <span class="text-cyan-400 font-mono text-[10px]">36</span>
          </button>
          <button class="country-shortcut px-2 py-1 rounded-lg bg-slate-900/80 hover:bg-slate-800 border border-slate-800 hover:border-cyan-500/50 text-[11px] text-slate-300 backdrop-blur transition flex items-center gap-1" data-country="UK">
            <span>🇬🇧</span> UK <span class="text-cyan-400 font-mono text-[10px]">35</span>
          </button>
          <button class="country-shortcut px-2 py-1 rounded-lg bg-slate-900/80 hover:bg-slate-800 border border-slate-800 hover:border-cyan-500/50 text-[11px] text-slate-300 backdrop-blur transition flex items-center gap-1" data-country="Canada">
            <span>🇨🇦</span> Canada <span class="text-cyan-400 font-mono text-[10px]">15</span>
          </button>
          <button class="country-shortcut px-2 py-1 rounded-lg bg-slate-900/80 hover:bg-slate-800 border border-slate-800 hover:border-cyan-500/50 text-[11px] text-slate-300 backdrop-blur transition flex items-center gap-1" data-country="France">
            <span>🇫🇷</span> France <span class="text-cyan-400 font-mono text-[10px]">9</span>
          </button>
          <button class="country-shortcut px-2 py-1 rounded-lg bg-slate-900/80 hover:bg-slate-800 border border-slate-800 hover:border-cyan-500/50 text-[11px] text-slate-300 backdrop-blur transition flex items-center gap-1" data-country="Germany">
            <span>🇩🇪</span> Germany <span class="text-cyan-400 font-mono text-[10px]">9</span>
          </button>
          <button class="country-shortcut px-2 py-1 rounded-lg bg-slate-900/80 hover:bg-slate-800 border border-slate-800 hover:border-cyan-500/50 text-[11px] text-slate-300 backdrop-blur transition flex items-center gap-1" data-country="Japan">
            <span>🇯🇵</span> Japan <span class="text-cyan-400 font-mono text-[10px]">3</span>
          </button>
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
          <span id="globeStatus">Drag to rotate · Scroll to zoom</span>
          <span class="text-slate-600">|</span>
          <span id="visibleCount" class="text-cyan-400">197 visible</span>
        </div>

        <!-- Tooltip -->
        <div id="globeTooltip" class="absolute pointer-events-none hidden z-30 bg-slate-900/95 border border-cyan-500/50 text-white px-3 py-2 rounded-lg shadow-xl text-xs max-w-xs backdrop-blur">
          <div id="tooltipName" class="font-semibold text-white"></div>
          <div id="tooltipMeta" class="text-[11px] text-slate-300"></div>
        </div>

      </div>

      <!-- Detail & Inspection Side Drawer -->
      <aside id="detailDrawer" class="w-full md:w-96 border-t md:border-t-0 md:border-l border-slate-800 bg-slate-900/95 flex flex-col z-30 max-h-[50vh] md:max-h-none overflow-y-auto">
        <div class="p-4 border-b border-slate-800 flex items-center justify-between">
          <h2 class="text-xs font-semibold uppercase tracking-wider text-slate-400">Institution Dossier</h2>
          <span id="dossierTierBadge" class="hidden text-[10px] font-bold px-2 py-0.5 rounded-full border"></span>
        </div>

        <div id="dossierContent" class="p-4 flex-1 flex flex-col justify-center text-slate-400 text-xs">
          <div class="text-center py-8">
            <div class="w-12 h-12 mx-auto rounded-full bg-slate-800/80 border border-slate-700 flex items-center justify-center text-xl mb-3 text-cyan-400">
              🏛️
            </div>
            <p class="font-medium text-slate-300">No institution selected</p>
            <p class="text-[11px] text-slate-500 mt-1 max-w-[200px] mx-auto">
              Click any country outline or institution dot on the globe to inspect its ethical funding profile.
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
              <th class="p-3.5">Location</th>
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

  <!-- CONVERSATIONAL AI CONCIERGE -->
  <div id="chatDrawer" class="fixed bottom-5 right-5 w-96 max-w-[calc(100vw-2rem)] h-[580px] max-h-[85vh] bg-slate-900/95 border border-cyan-500/40 rounded-2xl shadow-2xl backdrop-blur-xl flex flex-col z-50 transition-all duration-300 transform translate-y-4 opacity-0 pointer-events-none">
    
    <div class="px-4 py-3 border-b border-slate-800 flex items-center justify-between bg-slate-950/70 rounded-t-2xl">
      <div class="flex items-center gap-2.5">
        <div class="w-6 h-6 rounded-full bg-emerald-500/20 border border-emerald-500/50 flex items-center justify-center text-xs">
          ✨
        </div>
        <div>
          <h3 class="text-xs font-semibold text-white tracking-wide">Atlas AI Concierge</h3>
          <span id="chatModeTag" class="text-[9px] uppercase px-1.5 py-0.5 rounded bg-emerald-950 text-emerald-400 border border-emerald-800 font-mono">
            35 Countries Ready
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
            I can guide you across <strong>35 countries</strong> and <strong>197 institutions</strong>. Ask me to fly to any country or analyze its ethical funding landscape!
          </p>
          <div class="mt-3 flex flex-col gap-1.5">
            <button class="chat-preset text-left px-2.5 py-1.5 rounded-lg bg-slate-900/80 hover:bg-emerald-950/60 border border-slate-700 hover:border-emerald-600/50 text-slate-300 hover:text-white transition">
              🌍 Which countries have the most Tier A institutions?
            </button>
            <button class="chat-preset text-left px-2.5 py-1.5 rounded-lg bg-slate-900/80 hover:bg-emerald-950/60 border border-slate-700 hover:border-emerald-600/50 text-slate-300 hover:text-white transition">
              🇩🇰 Show ethically funded museums in Denmark
            </button>
            <button class="chat-preset text-left px-2.5 py-1.5 rounded-lg bg-slate-900/80 hover:bg-emerald-950/60 border border-slate-700 hover:border-emerald-600/50 text-slate-300 hover:text-white transition">
              🇯🇵 What institutions are mapped in Japan?
            </button>
            <button class="chat-preset text-left px-2.5 py-1.5 rounded-lg bg-slate-900/80 hover:bg-emerald-950/60 border border-slate-700 hover:border-emerald-600/50 text-slate-300 hover:text-white transition">
              🏛️ Why is Te Papa categorized as Tier B?
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
      <input type="text" id="chatInput" placeholder="Ask about any country, city, or museum..." class="flex-1 bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-emerald-400 transition" />
      <button id="chatVoiceBtn" class="p-2 text-slate-400 hover:text-cyan-400 rounded-lg border border-slate-800 hover:border-slate-700 transition" title="Voice Input">
        🎙️
      </button>
      <button id="chatSendBtn" class="p-2 bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold rounded-lg transition shadow-md" title="Send">
        ➤
      </button>
    </div>

  </div>

  <!-- FLOATING CHAT BUTTON -->
  <button id="floatingChatBtn" class="fixed bottom-5 right-5 z-40 flex items-center gap-2 px-3.5 py-2 rounded-full bg-gradient-to-r from-slate-900 to-slate-950 border border-emerald-500/50 text-white text-xs font-semibold shadow-2xl hover:scale-105 transition shadow-[0_0_15px_rgba(0,255,135,0.3)]">
    <span class="w-2.5 h-2.5 rounded-full bg-emerald-400 shadow-[0_0_8px_#00ff87] animate-pulse"></span>
    <span>Atlas Concierge</span>
  </button>

  <script>
    const ALL_INSTITUTIONS = ''' + insts_json + ''';
    const COUNTRY_LIST = ''' + countries_json + ''';
    const WORLD_ARCS = ''' + arcs_json + ''';

    // State
    let activeTiers = new Set(['A', 'B', 'U']);
    let activeSize = 'all';
    let selectedCountry = 'all';
    let searchQuery = '';
    let selectedInstitution = null;
    let activeView = 'globe';

    // Globe Physics
    let rotLon = 0;
    let rotLat = 20;
    let targetRotLon = 0;
    let targetRotLat = 20;
    let isFlying = false;
    let flightProgress = 0;
    let startRotLon = 0, startRotLat = 0;

    let zoom = 1.0;
    let targetZoom = 1.0;
    let isDragging = false;
    let lastMouseX = 0, lastMouseY = 0;
    let velLon = 0.2;
    let velLat = 0;
    let isAutoSpinning = true;

    let hoveredInstitution = null;

    // Populate Country Select
    const countrySelect = document.getElementById('countrySelect');
    COUNTRY_LIST.filter(c => c.count > 0).forEach(c => {
      const opt = document.createElement('option');
      opt.value = c.name;
      opt.textContent = `${c.name} (${c.count})`;
      countrySelect.appendChild(opt);
    });

    countrySelect.addEventListener('change', e => {
      setCountryFilter(e.target.value);
    });

    function setCountryFilter(cName) {
      selectedCountry = cName;
      countrySelect.value = cName;

      const bar = document.getElementById('activeFilterBar');
      const badge = document.getElementById('activeCountryBadge');
      const label = document.getElementById('activeCountryLabel');

      if (cName !== 'all') {
        bar.classList.remove('hidden');
        badge.classList.remove('hidden');
        badge.classList.add('flex');
        label.textContent = cName;

        // Fly to country centroid
        const cData = COUNTRY_LIST.find(c => c.name.toLowerCase() === cName.toLowerCase());
        if (cData) {
          flyTo(cData.lon, cData.lat, 1.8);
        }
      } else {
        badge.classList.add('hidden');
        badge.classList.remove('flex');
        if (!searchQuery && activeTiers.size === 3 && activeSize === 'all') {
          bar.classList.add('hidden');
        }
      }

      renderTable();
    }

    document.getElementById('clearCountryBtn').addEventListener('click', () => {
      setCountryFilter('all');
    });

    document.getElementById('clearAllFiltersBtn').addEventListener('click', () => {
      setCountryFilter('all');
      activeTiers = new Set(['A', 'B', 'U']);
      ['A', 'B', 'U'].forEach(t => document.getElementById(`tier${t}Btn`).classList.remove('opacity-40'));
      activeSize = 'all';
      Object.keys(sizeButtons).forEach(k => {
        sizeButtons[k].classList.toggle('bg-slate-700', k === 'all');
        sizeButtons[k].classList.toggle('text-white', k === 'all');
        sizeButtons[k].classList.toggle('text-slate-400', k !== 'all');
      });
      searchInput.value = '';
      searchQuery = '';
      clearSearchBtn.classList.add('hidden');
      document.getElementById('activeFilterBar').classList.add('hidden');
      renderTable();
    });

    // Quick country shortcuts
    document.querySelectorAll('.country-shortcut').forEach(btn => {
      btn.addEventListener('click', () => {
        const c = btn.getAttribute('data-country');
        setCountryFilter(c);
      });
    });

    // Canvas
    const canvas = document.getElementById('globeCanvas');
    const ctx = canvas.getContext('2d');
    const tooltip = document.getElementById('globeTooltip');
    const tooltipName = document.getElementById('tooltipName');
    const tooltipMeta = document.getElementById('tooltipMeta');

    function resizeCanvas() {
      const rect = canvas.getBoundingClientRect();
      const dpr = window.devicePixelRatio || 1;
      canvas.width = rect.width * dpr;
      canvas.height = rect.height * dpr;
      ctx.scale(dpr, dpr);
    }
    window.addEventListener('resize', resizeCanvas);
    resizeCanvas();

    function project(lon, lat, r, cx, cy) {
      const rad = Math.PI / 180;
      const lambda = (lon - rotLon) * rad;
      const phi = lat * rad;
      const phi0 = rotLat * rad;

      const cosC = Math.sin(phi0) * Math.sin(phi) + Math.cos(phi0) * Math.cos(phi) * Math.cos(lambda);
      if (cosC < 0) return null;

      const x = cx + r * Math.cos(phi) * Math.sin(lambda);
      const y = cy - r * (Math.cos(phi0) * Math.sin(phi) - Math.sin(phi0) * Math.cos(phi) * Math.cos(lambda));
      return { x, y, depth: cosC };
    }

    function getFilteredInstitutions() {
      return ALL_INSTITUTIONS.filter(i => {
        if (!activeTiers.has(i.tier)) return false;
        if (activeSize === 'L' && i.size !== 'L') return false;
        if (activeSize === 'S' && i.size !== 'S') return false;
        if (selectedCountry !== 'all') {
          if (i.country.toLowerCase() !== selectedCountry.toLowerCase()) return false;
        }
        if (searchQuery) {
          const q = searchQuery.toLowerCase();
          const match = i.name.toLowerCase().includes(q) || i.location.toLowerCase().includes(q) || i.country.toLowerCase().includes(q);
          if (!match) return false;
        }
        return true;
      });
    }

    function renderGlobe() {
      const rect = canvas.getBoundingClientRect();
      const w = rect.width;
      const h = rect.height;
      const cx = w / 2;
      const cy = h / 2;
      const radius = Math.min(w, h) * 0.42 * zoom;

      ctx.clearRect(0, 0, w, h);

      if (isFlying) {
        flightProgress += 0.04;
        if (flightProgress >= 1) {
          flightProgress = 1;
          isFlying = false;
        }
        const ease = 1 - Math.pow(1 - flightProgress, 3);
        rotLon = startRotLon + (targetRotLon - startRotLon) * ease;
        rotLat = startRotLat + (targetRotLat - startRotLat) * ease;
        zoom += (targetZoom - zoom) * 0.1;
      } else if (isAutoSpinning && !isDragging) {
        rotLon = (rotLon + velLon) % 360;
      } else if (!isDragging) {
        rotLon = (rotLon + velLon) % 360;
        rotLat = Math.max(-80, Math.min(80, rotLat + velLat));
        velLon *= 0.94;
        velLat *= 0.94;
      }

      // Outer glow
      const glowGrad = ctx.createRadialGradient(cx, cy, radius * 0.85, cx, cy, radius * 1.25);
      glowGrad.addColorStop(0, 'rgba(0, 242, 254, 0.22)');
      glowGrad.addColorStop(0.5, 'rgba(0, 255, 135, 0.08)');
      glowGrad.addColorStop(1, 'transparent');
      ctx.fillStyle = glowGrad;
      ctx.beginPath();
      ctx.arc(cx, cy, radius * 1.25, 0, Math.PI * 2);
      ctx.fill();

      // Deep Ocean Sphere
      const oceanGrad = ctx.createRadialGradient(cx - radius * 0.3, cy - radius * 0.3, radius * 0.1, cx, cy, radius);
      oceanGrad.addColorStop(0, '#00264d');
      oceanGrad.addColorStop(0.7, '#001124');
      oceanGrad.addColorStop(1, '#00050d');
      ctx.fillStyle = oceanGrad;
      ctx.beginPath();
      ctx.arc(cx, cy, radius, 0, Math.PI * 2);
      ctx.fill();

      ctx.save();
      ctx.beginPath();
      ctx.arc(cx, cy, radius, 0, Math.PI * 2);
      ctx.clip();

      // Graticules
      ctx.strokeStyle = 'rgba(0, 255, 135, 0.08)';
      ctx.lineWidth = 0.8;
      [-60, -30, 0, 30, 60].forEach(lat => {
        ctx.beginPath();
        let first = true;
        for (let lon = -180; lon <= 180; lon += 8) {
          const pt = project(lon, lat, radius, cx, cy);
          if (pt) {
            if (first) { ctx.moveTo(pt.x, pt.y); first = false; }
            else { ctx.lineTo(pt.x, pt.y); }
          } else { first = true; }
        }
        ctx.stroke();
      });

      // 🌍 RENDER ALL COUNTRY BORDERS & COASTLINES!
      ctx.strokeStyle = 'rgba(0, 242, 254, 0.42)';
      ctx.lineWidth = 0.9;
      WORLD_ARCS.forEach(arc => {
        ctx.beginPath();
        let first = true;
        for (let i = 0; i < arc.length; i++) {
          const pt = project(arc[i][0], arc[i][1], radius, cx, cy);
          if (pt) {
            if (first) { ctx.moveTo(pt.x, pt.y); first = false; }
            else { ctx.lineTo(pt.x, pt.y); }
          } else {
            first = true;
          }
        }
        ctx.stroke();
      });

      // Render Country Labels when zoomed in
      if (zoom > 1.3) {
        ctx.fillStyle = 'rgba(0, 255, 135, 0.55)';
        ctx.font = '10px JetBrains Mono, monospace';
        ctx.textAlign = 'center';
        COUNTRY_LIST.filter(c => c.count > 0).forEach(c => {
          const pt = project(c.lon, c.lat, radius, cx, cy);
          if (pt && pt.depth > 0.4) {
            ctx.fillText(c.name, pt.x, pt.y - 12);
          }
        });
      }

      ctx.restore();

      // Sphere Rim Highlight
      ctx.strokeStyle = 'rgba(0, 242, 254, 0.5)';
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.arc(cx, cy, radius, 0, Math.PI * 2);
      ctx.stroke();

      // Render Institution Dots
      const filtered = getFilteredInstitutions();
      document.getElementById('visibleCount').textContent = `${filtered.length} visible`;

      filtered.forEach(inst => {
        const pt = project(inst.lon, inst.lat, radius, cx, cy);
        if (!pt) return;

        const isSelected = selectedInstitution && selectedInstitution.name === inst.name;
        const isHovered = hoveredInstitution && hoveredInstitution.name === inst.name;

        const baseR = inst.size === 'L' ? 5.5 : 3.5;
        const dotR = (isSelected ? baseR * 1.6 : isHovered ? baseR * 1.3 : baseR) * Math.min(1.8, Math.max(0.6, pt.depth));

        let dotColor = '#24a148';
        if (inst.tier === 'B') dotColor = '#4589ff';
        if (inst.tier === 'U') dotColor = '#8d8d8d';

        ctx.beginPath();
        ctx.arc(pt.x, pt.y, dotR * 2, 0, Math.PI * 2);
        ctx.fillStyle = inst.tier === 'A' ? 'rgba(0, 255, 135, 0.25)' : inst.tier === 'B' ? 'rgba(0, 242, 254, 0.25)' : 'rgba(255, 255, 255, 0.15)';
        ctx.fill();

        if (isSelected) {
          ctx.beginPath();
          ctx.arc(pt.x, pt.y, dotR * 3, 0, Math.PI * 2);
          ctx.strokeStyle = '#00ff87';
          ctx.lineWidth = 2;
          ctx.stroke();
        }

        ctx.beginPath();
        ctx.arc(pt.x, pt.y, dotR, 0, Math.PI * 2);
        ctx.fillStyle = dotColor;
        ctx.fill();
        ctx.strokeStyle = '#ffffff';
        ctx.lineWidth = 1;
        ctx.stroke();
      });

      requestAnimationFrame(renderGlobe);
    }
    requestAnimationFrame(renderGlobe);

    function flyTo(lon, lat, targetZ = 1.4) {
      isAutoSpinning = false;
      document.getElementById('spinToggleBtn').classList.remove('bg-emerald-950/70', 'text-emerald-300');
      document.getElementById('spinToggleBtn').classList.add('bg-slate-800', 'text-slate-400');

      startRotLon = rotLon;
      startRotLat = rotLat;
      
      let dLon = (lon - startRotLon) % 360;
      if (dLon > 180) dLon -= 360;
      if (dLon < -180) dLon += 360;
      targetRotLon = startRotLon + dLon;
      targetRotLat = Math.max(-75, Math.min(75, lat));
      targetZoom = targetZ;

      flightProgress = 0;
      isFlying = true;
    }

    function selectInstitution(inst) {
      selectedInstitution = inst;
      const drawer = document.getElementById('dossierContent');
      const badge = document.getElementById('dossierTierBadge');

      const tierLabels = { A: 'Verified', B: 'One Name To Know', U: 'Unverified' };
      const tierColors = {
        A: 'bg-emerald-950 text-emerald-400 border-emerald-600',
        B: 'bg-blue-950 text-blue-400 border-blue-600',
        U: 'bg-slate-800 text-slate-300 border-slate-600'
      };

      badge.className = `text-[10px] font-bold px-2 py-0.5 rounded-full border ${tierColors[inst.tier]}`;
      badge.textContent = tierLabels[inst.tier];
      badge.classList.remove('hidden');

      drawer.innerHTML = `
        <div class="space-y-4">
          <div>
            <h3 class="text-base font-bold text-white">${inst.name}</h3>
            <p class="text-xs text-cyan-400 flex items-center gap-1 mt-0.5">
              <span>📍</span> <span>${inst.location}</span>
              <span class="text-slate-600">·</span>
              <span class="text-slate-400">${inst.size === 'L' ? 'Large' : 'Small/Mid'}</span>
            </p>
          </div>

          <div class="bg-slate-950/60 p-3 rounded-xl border border-slate-800">
            <h4 class="text-[10px] font-bold uppercase tracking-wider text-emerald-400 mb-1">Funding & Governance</h4>
            <p class="text-xs text-slate-200 leading-relaxed">${inst.funding}</p>
          </div>

          ${inst.watch ? `
            <div class="bg-slate-950/60 p-3 rounded-xl border border-slate-800">
              <h4 class="text-[10px] font-bold uppercase tracking-wider text-cyan-400 mb-1">Watch Notes</h4>
              <p class="text-xs text-slate-300 leading-relaxed">${inst.watch}</p>
            </div>
          ` : ''}

          <div>
            <h4 class="text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-2">Sources</h4>
            <div class="flex flex-col gap-1.5">
              ${(inst.sources || []).map(url => {
                let domain = url;
                try { domain = new URL(url).hostname.replace(/^www\\./, ''); } catch(e){}
                return `
                  <a href="${url}" target="_blank" rel="noopener noreferrer" class="flex items-center justify-between px-2.5 py-1.5 rounded-lg bg-slate-800/60 hover:bg-slate-700/80 text-[11px] text-cyan-300 hover:text-white transition">
                    <span class="truncate">${domain}</span>
                    <span>↗</span>
                  </a>
                `;
              }).join('')}
            </div>
          </div>
        </div>
      `;

      flyTo(inst.lon, inst.lat, Math.max(zoom, 1.5));
    }

    // Pointer events
    canvas.addEventListener('pointerdown', e => {
      isDragging = true;
      canvas.classList.add('dragging');
      lastMouseX = e.clientX;
      lastMouseY = e.clientY;
      velLon = 0;
      velLat = 0;
      isFlying = false;
    });

    window.addEventListener('pointermove', e => {
      const rect = canvas.getBoundingClientRect();
      const mouseX = e.clientX - rect.left;
      const mouseY = e.clientY - rect.top;

      if (isDragging) {
        const dx = e.clientX - lastMouseX;
        const dy = e.clientY - lastMouseY;
        lastMouseX = e.clientX;
        lastMouseY = e.clientY;

        const sens = 0.35 / zoom;
        rotLon = (rotLon - dx * sens) % 360;
        rotLat = Math.max(-80, Math.min(80, rotLat + dy * sens));
        velLon = -dx * sens * 0.4;
        velLat = dy * sens * 0.4;
      } else {
        const cx = rect.width / 2;
        const cy = rect.height / 2;
        const radius = Math.min(rect.width, rect.height) * 0.42 * zoom;

        let hit = null;
        const filtered = getFilteredInstitutions();
        for (let i = 0; i < filtered.length; i++) {
          const inst = filtered[i];
          const pt = project(inst.lon, inst.lat, radius, cx, cy);
          if (pt) {
            const dist = Math.hypot(pt.x - mouseX, pt.y - mouseY);
            if (dist < 12) {
              hit = inst;
              break;
            }
          }
        }

        hoveredInstitution = hit;
        if (hit) {
          tooltip.style.left = `${mouseX + 12}px`;
          tooltip.style.top = `${mouseY + 12}px`;
          tooltipName.textContent = hit.name;
          tooltipMeta.textContent = `${hit.location} · ${hit.tier === 'A' ? 'Verified' : hit.tier === 'B' ? 'One Name' : 'Unverified'}`;
          tooltip.classList.remove('hidden');
        } else {
          tooltip.classList.add('hidden');
        }
      }
    });

    window.addEventListener('pointerup', () => {
      if (isDragging) {
        isDragging = false;
        canvas.classList.remove('dragging');
      }
    });

    canvas.addEventListener('click', () => {
      if (hoveredInstitution) {
        selectInstitution(hoveredInstitution);
      }
    });

    canvas.addEventListener('wheel', e => {
      e.preventDefault();
      const factor = e.deltaY < 0 ? 1.15 : 0.87;
      zoom = Math.max(0.6, Math.min(3.5, zoom * factor));
    }, { passive: false });

    // Controls
    document.getElementById('zoomInBtn').addEventListener('click', () => { zoom = Math.min(3.5, zoom * 1.25); });
    document.getElementById('zoomOutBtn').addEventListener('click', () => { zoom = Math.max(0.6, zoom / 1.25); });
    document.getElementById('resetViewBtn').addEventListener('click', () => { flyTo(0, 20, 1.0); });
    document.getElementById('spinToggleBtn').addEventListener('click', () => {
      isAutoSpinning = !isAutoSpinning;
      const btn = document.getElementById('spinToggleBtn');
      if (isAutoSpinning) {
        btn.classList.add('bg-emerald-950/70', 'text-emerald-300');
        btn.classList.remove('bg-slate-800', 'text-slate-400');
        velLon = 0.2;
      } else {
        btn.classList.remove('bg-emerald-950/70', 'text-emerald-300');
        btn.classList.add('bg-slate-800', 'text-slate-400');
      }
    });

    // Tier filters
    ['A', 'B', 'U'].forEach(t => {
      const btn = document.getElementById(`tier${t}Btn`);
      btn.addEventListener('click', () => {
        if (activeTiers.has(t)) {
          if (activeTiers.size > 1) activeTiers.delete(t);
        } else {
          activeTiers.add(t);
        }
        btn.classList.toggle('opacity-40', !activeTiers.has(t));
        renderTable();
      });
    });

    // Size filters
    const sizeButtons = {
      all: document.getElementById('sizeAllBtn'),
      L: document.getElementById('sizeLargeBtn'),
      S: document.getElementById('sizeSmallBtn'),
    };
    Object.keys(sizeButtons).forEach(sz => {
      sizeButtons[sz].addEventListener('click', () => {
        activeSize = sz;
        Object.keys(sizeButtons).forEach(k => {
          sizeButtons[k].classList.toggle('bg-slate-700', k === sz);
          sizeButtons[k].classList.toggle('text-white', k === sz);
          sizeButtons[k].classList.toggle('text-slate-400', k !== sz);
        });
        renderTable();
      });
    });

    // Search input
    const searchInput = document.getElementById('searchInput');
    const clearSearchBtn = document.getElementById('clearSearchBtn');
    searchInput.addEventListener('input', e => {
      searchQuery = e.target.value.trim();
      clearSearchBtn.classList.toggle('hidden', !searchQuery);
      renderTable();
    });
    clearSearchBtn.addEventListener('click', () => {
      searchInput.value = '';
      searchQuery = '';
      clearSearchBtn.classList.add('hidden');
      renderTable();
    });

    // View toggle
    const viewGlobeBtn = document.getElementById('viewGlobeBtn');
    const viewListBtn = document.getElementById('viewListBtn');
    const globeViewContainer = document.getElementById('globeViewContainer');
    const listViewContainer = document.getElementById('listViewContainer');

    viewGlobeBtn.addEventListener('click', () => {
      activeView = 'globe';
      viewGlobeBtn.className = 'px-3 py-1 rounded-md font-medium transition bg-cyan-600 text-white shadow';
      viewListBtn.className = 'px-3 py-1 rounded-md font-medium transition text-slate-400 hover:text-white';
      globeViewContainer.classList.remove('hidden');
      listViewContainer.classList.add('hidden');
      resizeCanvas();
    });

    viewListBtn.addEventListener('click', () => {
      activeView = 'list';
      viewListBtn.className = 'px-3 py-1 rounded-md font-medium transition bg-cyan-600 text-white shadow';
      viewGlobeBtn.className = 'px-3 py-1 rounded-md font-medium transition text-slate-400 hover:text-white';
      listViewContainer.classList.remove('hidden');
      globeViewContainer.classList.add('hidden');
      renderTable();
    });

    function renderTable() {
      const tbody = document.getElementById('tableBody');
      const filtered = getFilteredInstitutions();

      tbody.innerHTML = filtered.map(inst => `
        <tr class="hover:bg-slate-800/40 transition cursor-pointer" onclick="selectAndShow('${inst.name.replace(/'/g, "\\\\'")}')">
          <td class="p-3.5 font-semibold text-white">${inst.name}</td>
          <td class="p-3.5 text-slate-300 whitespace-nowrap">${inst.location}</td>
          <td class="p-3.5 text-cyan-400 whitespace-nowrap font-medium">${inst.country}</td>
          <td class="p-3.5 whitespace-nowrap">
            <span class="px-2 py-0.5 rounded-full text-[10px] font-bold border ${inst.tier === 'A' ? 'bg-emerald-950 text-emerald-400 border-emerald-600' : inst.tier === 'B' ? 'bg-blue-950 text-blue-400 border-blue-600' : 'bg-slate-800 text-slate-300 border-slate-600'}">
              ${inst.tier === 'A' ? 'Verified' : inst.tier === 'B' ? 'One Name' : 'Unverified'}
            </span>
          </td>
          <td class="p-3.5 text-slate-400">${inst.size === 'L' ? 'Large' : 'Small/Mid'}</td>
          <td class="p-3.5 max-w-xs text-slate-300">${inst.funding}</td>
          <td class="p-3.5 max-w-xs text-slate-400">${inst.watch || '—'}</td>
          <td class="p-3.5 whitespace-nowrap">
            ${(inst.sources || []).slice(0, 1).map(u => `
              <a href="${u}" target="_blank" onclick="event.stopPropagation()" class="text-cyan-400 hover:underline">Link ↗</a>
            `).join('')}
          </td>
        </tr>
      `).join('');
    }
    renderTable();

    window.selectAndShow = function(name) {
      const inst = ALL_INSTITUTIONS.find(i => i.name === name);
      if (inst) {
        viewGlobeBtn.click();
        selectInstitution(inst);
      }
    };

    // ==========================================
    // AI CONCIERGE CHAT ENGINE
    // ==========================================
    const chatDrawer = document.getElementById('chatDrawer');
    const floatingChatBtn = document.getElementById('floatingChatBtn');
    const headerChatToggle = document.getElementById('headerChatToggle');
    const chatCloseBtn = document.getElementById('chatCloseBtn');
    const chatClearBtn = document.getElementById('chatClearBtn');
    const chatMessages = document.getElementById('chatMessages');
    const chatInput = document.getElementById('chatInput');
    const chatSendBtn = document.getElementById('chatSendBtn');

    function toggleChatDrawer() {
      const isOpen = chatDrawer.classList.contains('opacity-100');
      if (isOpen) {
        chatDrawer.classList.remove('opacity-100', 'translate-y-0', 'pointer-events-auto');
        chatDrawer.classList.add('opacity-0', 'translate-y-4', 'pointer-events-none');
      } else {
        chatDrawer.classList.remove('opacity-0', 'translate-y-4', 'pointer-events-none');
        chatDrawer.classList.add('opacity-100', 'translate-y-0', 'pointer-events-auto');
        setTimeout(() => chatInput.focus(), 150);
      }
    }

    floatingChatBtn.addEventListener('click', toggleChatDrawer);
    headerChatToggle.addEventListener('click', toggleChatDrawer);
    chatCloseBtn.addEventListener('click', toggleChatDrawer);

    window.addEventListener('keydown', e => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        toggleChatDrawer();
      }
    });

    chatClearBtn.addEventListener('click', () => {
      chatMessages.innerHTML = '';
      appendBotMessage('Conversation cleared. Ask me about any country, museum, or funding model!');
    });

    chatMessages.addEventListener('click', e => {
      const preset = e.target.closest('.chat-preset');
      if (preset) {
        handleUserQuery(preset.textContent.trim());
      }
    });

    function appendUserMessage(text) {
      const div = document.createElement('div');
      div.className = 'flex flex-col gap-1 items-end';
      div.innerHTML = `
        <div class="bg-gradient-to-r from-emerald-600 to-teal-600 text-white p-3 rounded-2xl rounded-tr-sm max-w-[85%] shadow-md">
          ${text}
        </div>
      `;
      chatMessages.appendChild(div);
      chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function appendBotMessage(html, actions = []) {
      const div = document.createElement('div');
      div.className = 'flex flex-col gap-1 items-start';

      let actionsHtml = '';
      if (actions.length > 0) {
        actionsHtml = `
          <div class="mt-2.5 flex flex-wrap gap-1.5">
            ${actions.map((act, i) => `
              <button class="chat-act-btn px-2.5 py-1 rounded-full text-[11px] font-semibold flex items-center gap-1 border transition ${act.tier === 'A' ? 'bg-emerald-950/80 text-emerald-300 border-emerald-600 hover:bg-emerald-900' : act.tier === 'B' ? 'bg-blue-950/80 text-blue-300 border-blue-600 hover:bg-blue-900' : 'bg-slate-800 text-cyan-300 border-slate-700 hover:bg-slate-700'}" data-act-idx="${i}">
                ${act.icon || '📍'} ${act.label}
              </button>
            `).join('')}
          </div>
        `;
      }

      div.innerHTML = `
        <div class="bg-slate-800/90 border border-slate-700/80 text-slate-200 p-3 rounded-2xl rounded-tl-sm max-w-[90%] leading-relaxed shadow-md">
          ${html}
          ${actionsHtml}
        </div>
      `;

      if (actions.length > 0) {
        div.querySelectorAll('.chat-act-btn').forEach(btn => {
          const idx = parseInt(btn.getAttribute('data-act-idx'), 10);
          btn.addEventListener('click', () => {
            if (actions[idx] && actions[idx].handler) {
              actions[idx].handler();
            }
          });
        });
      }

      chatMessages.appendChild(div);
      chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function handleUserQuery(query) {
      appendUserMessage(query);

      const typing = document.createElement('div');
      typing.id = 'typingIndicator';
      typing.className = 'flex gap-1.5 p-2 bg-slate-800/60 rounded-xl w-14';
      typing.innerHTML = '<span class="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-ping"></span><span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping"></span>';
      chatMessages.appendChild(typing);
      chatMessages.scrollTop = chatMessages.scrollHeight;

      setTimeout(() => {
        typing.remove();
        runOfflineLogic(query);
      }, 250);
    }

    function runOfflineLogic(query) {
      const q = query.toLowerCase().trim();
      const actions = [];
      let response = '';

      // 1. Check country query
      const matchCountry = COUNTRY_LIST.find(c => {
        const cLow = c.name.toLowerCase();
        return q.includes(cLow) || (cLow === 'usa' && (q.includes('united states') || q.includes('america'))) || (cLow === 'uk' && (q.includes('united kingdom') || q.includes('britain')));
      });

      if (matchCountry && (q.includes('country') || q.includes('in ') || q.includes(matchCountry.name.toLowerCase()))) {
        const countryInsts = ALL_INSTITUTIONS.filter(i => i.country.toLowerCase() === matchCountry.name.toLowerCase());
        response = `
          <p class="font-bold text-white">🌍 ${matchCountry.name} (${countryInsts.length} institutions mapped)</p>
          <ul class="mt-1.5 space-y-1 text-slate-300 text-xs">
            ${countryInsts.slice(0, 4).map(i => `
              <li><strong>${i.name}</strong> <span class="${i.tier === 'A' ? 'text-emerald-400' : 'text-blue-400'}">(${i.tier === 'A' ? 'Verified' : 'One Name'})</span> — ${i.location.split(',')[0]}</li>
            `).join('')}
          </ul>
          ${countryInsts.length > 4 ? `<p class="text-[11px] text-slate-400 mt-1">...and ${countryInsts.length - 4} more.</p>` : ''}
        `;
        actions.push({
          label: `Fly to ${matchCountry.name}`,
          icon: '📍',
          handler: () => {
            viewGlobeBtn.click();
            setCountryFilter(matchCountry.name);
          }
        });
        countryInsts.slice(0, 2).forEach(inst => {
          actions.push({
            label: inst.name,
            icon: '🏛️',
            tier: inst.tier,
            handler: () => {
              viewGlobeBtn.click();
              selectInstitution(inst);
            }
          });
        });
        appendBotMessage(response, actions);
        viewGlobeBtn.click();
        setCountryFilter(matchCountry.name);
        return;
      }

      // 2. Specific institution check
      const matchInst = ALL_INSTITUTIONS.find(i => {
        const n = i.name.toLowerCase();
        return q.includes(n) || (n.includes(q) && q.length > 3);
      });

      if (matchInst) {
        response = `
          <p class="font-bold text-white">${matchInst.name} <span class="text-xs ${matchInst.tier === 'A' ? 'text-emerald-400' : matchInst.tier === 'B' ? 'text-blue-400' : 'text-slate-400'}">· ${matchInst.tier === 'A' ? 'Verified' : matchInst.tier === 'B' ? 'One Name to Know' : 'Unverified'}</span></p>
          <p class="text-xs text-cyan-300 mt-0.5">📍 ${matchInst.location} (${matchInst.size === 'L' ? 'Large' : 'Small/Mid'})</p>
          <p class="text-xs text-slate-300 mt-2"><strong>Funding:</strong> ${matchInst.funding}</p>
          ${matchInst.watch ? `<p class="text-xs text-slate-400 mt-1"><strong>Watch Notes:</strong> ${matchInst.watch}</p>` : ''}
        `;
        actions.push({
          label: `Inspect ${matchInst.name}`,
          icon: '🌍',
          tier: matchInst.tier,
          handler: () => {
            viewGlobeBtn.click();
            selectInstitution(matchInst);
          }
        });
        appendBotMessage(response, actions);
        viewGlobeBtn.click();
        selectInstitution(matchInst);
        return;
      }

      // 3. Country rankings or summary
      if (q.includes('which countr') || q.includes('most') || q.includes('all countr') || q.includes('countries represented')) {
        const top5 = COUNTRY_LIST.filter(c => c.count > 0).slice(0, 5);
        response = `
          <p class="font-bold text-white">Top Represented Countries:</p>
          <ol class="mt-1.5 space-y-1 text-slate-300 text-xs list-decimal pl-4">
            ${top5.map(c => `<li><strong>${c.name}</strong>: ${c.count} institutions</li>`).join('')}
          </ol>
          <p class="text-[11px] text-slate-400 mt-1.5">35 countries in total have verified or mapped institutions on the globe.</p>
        `;
        top5.slice(0, 3).forEach(c => {
          actions.push({
            label: `Fly to ${c.name}`,
            icon: '🌍',
            handler: () => setCountryFilter(c.name)
          });
        });
        appendBotMessage(response, actions);
        return;
      }

      // 4. Fallback
      response = `
        <p class="font-bold text-white">Culture Atlas Concierge</p>
        <p class="text-xs text-slate-300 mt-1">Ask me about any of the <strong>35 countries</strong> or <strong>197 cultural spaces</strong>:</p>
        <ul class="mt-1 space-y-1 text-xs text-cyan-300">
          <li>• "Show museums in Denmark, Canada, or Japan"</li>
          <li>• "Tell me about Te Papa or ARoS"</li>
          <li>• "Which countries have the most Tier A institutions?"</li>
        </ul>
      `;
      actions.push({
        label: 'Surprise Me',
        icon: '✨',
        handler: () => {
          const pick = ALL_INSTITUTIONS[Math.floor(Math.random() * ALL_INSTITUTIONS.length)];
          runOfflineLogic(`Tell me about ${pick.name}`);
        }
      });
      appendBotMessage(response, actions);
    }

    chatSendBtn.addEventListener('click', () => {
      const val = chatInput.value.trim();
      if (val) {
        chatInput.value = '';
        handleUserQuery(val);
      }
    });

    chatInput.addEventListener('keydown', e => {
      if (e.key === 'Enter') {
        const val = chatInput.value.trim();
        if (val) {
          chatInput.value = '';
          handleUserQuery(val);
        }
      }
    });

  </script>
</body>
</html>
'''

# Write full HTML app
full_html = generate_full_html()

with open('/Users/polinavasilyeva/.gemini/antigravity/scratch/sponsor-atlas/app/index.html', 'w') as f:
    f.write(full_html)

with open('/Users/polinavasilyeva/.gemini/antigravity/brain/b997e616-4551-453e-83cc-4ba184f90abf/culture_atlas_app.html', 'w') as f:
    f.write(full_html)

print("Updated app/index.html and culture_atlas_app.html with countries!")
