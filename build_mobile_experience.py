import json

def build():
    print("Decoding topojson polygons for mobile atlas...")
    topo = json.load(open('app/world-topo.json'))
    scale = topo['transform']['scale']
    translate = topo['transform']['translate']
    arcs = topo['arcs']

    def decode_arc(arc_idx):
        if arc_idx >= 0:
            raw_arc = arcs[arc_idx]
            pts = []
            x, y = 0, 0
            for dx, dy in raw_arc:
                x += dx
                y += dy
                pts.append([round(x * scale[0] + translate[0], 2), round(y * scale[1] + translate[1], 2)])
            return pts
        else:
            raw_arc = arcs[~arc_idx]
            pts = []
            x, y = 0, 0
            for dx, dy in raw_arc:
                x += dx
                y += dy
                pts.append([round(x * scale[0] + translate[0], 2), round(y * scale[1] + translate[1], 2)])
            pts.reverse()
            return pts

    def stitch_arcs(arc_indices):
        ring = []
        for idx in arc_indices:
            pts = decode_arc(idx)
            if not ring:
                ring.extend(pts)
            else:
                ring.extend(pts[1:])
        return ring

    geometries = topo['objects']['world']['geometries']

    GREEN_SET = {'Canada', 'Greenland', 'Algeria', 'Libya', 'Sudan', 'Mongolia', 'Sweden', 'Norway', 'Finland', 'Chad', 'Niger', 'Mali', 'Mauritania', 'Egypt', 'Morocco', 'Namibia', 'Botswana', 'Zimbabwe', 'Zambia'}
    TEAL_SET = {'Russia', 'India', 'China', 'Brazil', 'Australia', 'Angola', 'Dem. Rep. Congo', 'Congo', 'Indonesia', 'South Africa', 'Mozambique', 'Tanzania', 'Kenya', 'Ethiopia', 'Madagascar', 'Myanmar', 'Thailand', 'Vietnam'}
    BLUE_SET = {'United States', 'USA', 'Saudi Arabia', 'Iran', 'Kazakhstan', 'Mexico', 'Argentina', 'France', 'Spain', 'Germany', 'United Kingdom', 'Poland', 'Italy', 'Turkey', 'Ukraine', 'Uzbekistan', 'Turkmenistan', 'Pakistan', 'Afghanistan', 'Iraq', 'Syria', 'Jordan', 'Yemen', 'Oman'}

    greens = ['#0d4d38', '#115840', '#15654a', '#197354', '#0f523c']
    teals = ['#0c4852', '#0f545f', '#12606d', '#156c7a', '#0d4e58']
    blues = ['#0c3674', '#10428a', '#144e9f', '#185bb4', '#0e3b7d']

    out_countries = []
    for idx, g in enumerate(geometries):
        name = g.get('properties', {}).get('name', '')
        gtype = g.get('type')
        polys = []
        if gtype == 'Polygon':
            for arc_list in g.get('arcs', []):
                polys.append(stitch_arcs(arc_list))
        elif gtype == 'MultiPolygon':
            for poly_arcs in g.get('arcs', []):
                for arc_list in poly_arcs:
                    polys.append(stitch_arcs(arc_list))

        if name in GREEN_SET:
            col = greens[idx % len(greens)]
        elif name in TEAL_SET:
            col = teals[idx % len(teals)]
        elif name in BLUE_SET:
            col = blues[idx % len(blues)]
        else:
            palette = [greens, teals, blues][idx % 3]
            col = palette[(idx // 3) % len(palette)]

        out_countries.append({'n': name, 'c': col, 'r': polys})

    countries_json = json.dumps(out_countries, separators=(',', ':'))
    institutions_json = open('institutions.json', 'r', encoding='utf-8').read().strip()

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover" />
  <meta name="theme-color" content="#000000" />
  <meta name="apple-mobile-web-app-capable" content="yes" />
  <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent" />
  <title>Culture Atlas — Ethically funded cultural institutions across the world</title>
  <meta name="description" content="Culture Atlas — Ethically funded cultural institutions across the world" />
  
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  
  <script src="https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js"></script>
  <style>
    body {{
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      background-color: #000000;
      color: #f8fafc;
      margin: 0;
      padding: 0;
      overflow: hidden;
      height: 100vh;
      height: 100dvh;
    }}
    .font-mono {{
      font-family: 'JetBrains Mono', monospace;
    }}
    #globeCanvas {{
      cursor: grab;
      touch-action: none;
    }}
    #globeCanvas.dragging {{
      cursor: grabbing;
    }}
    .custom-scrollbar::-webkit-scrollbar {{
      width: 4px;
    }}
    .custom-scrollbar::-webkit-scrollbar-thumb {{
      background: #262a34;
      border-radius: 4px;
    }}
    .inst-card {{
      transition: all 0.15s ease-in-out;
    }}
    .inst-card.active {{
      border-color: #3b82f6 !important;
      background-color: #111726 !important;
    }}
    
    /* Mobile Bottom Sheet Smooth Transitions */
    .bottom-sheet {{
      transition: height 0.32s cubic-bezier(0.16, 1, 0.3, 1), transform 0.32s cubic-bezier(0.16, 1, 0.3, 1);
    }}
    .sheet-peek {{
      height: 76px !important;
    }}
    .sheet-half {{
      height: 52vh !important;
    }}
    .sheet-full {{
      height: 88vh !important;
    }}
  </style>
</head>
<body class="bg-black text-slate-100 h-screen h-[100dvh] flex flex-col select-none overflow-hidden">

  <!-- ========================================================= -->
  <!-- MAIN APP CONTAINER (Responsive Desktop Split + Mobile Map)-->
  <!-- ========================================================= -->
  <div class="relative w-full h-full flex flex-col md:flex-row bg-[#020408] overflow-hidden md:p-3">

    <div class="relative w-full h-full max-w-[1560px] mx-auto flex flex-col md:flex-row bg-[#020408] md:border md:border-[#1c212a] md:rounded-2xl overflow-hidden shadow-2xl flex-1">

      <!-- ========================================================= -->
      <!-- 📋 INSTITUTIONS LIST PANEL (Desktop Left List / Mobile Sheet) -->
      <!-- ========================================================= -->
      <aside id="bottomSheet" class="bottom-sheet absolute md:relative z-30 bottom-0 left-0 right-0 md:bottom-auto md:left-auto md:right-auto w-full md:w-[380px] lg:w-[430px] flex flex-col bg-[#07090e]/95 backdrop-blur-md md:bg-[#07090e] border-t md:border-t-0 md:border-r border-[#1c212a] rounded-t-2xl md:rounded-none shadow-2xl md:shadow-none sheet-peek md:h-full">
        
        <!-- Mobile Swipe/Drag Handle Pill -->
        <div id="sheetDragHandle" class="md:hidden w-full flex flex-col items-center pt-2 pb-1 cursor-pointer touch-none">
          <div class="w-12 h-1.5 bg-[#2d3548] rounded-full"></div>
        </div>

        <!-- Left List Header & Search/Filters -->
        <div class="p-3 sm:p-3.5 border-b border-[#1c212a] bg-[#0a0d14]/90 flex flex-col gap-2 shrink-0">
          <div class="flex items-start justify-between gap-2">
            <div>
              <div class="flex items-center gap-2">
                <div class="w-2.5 h-2.5 rounded-full bg-[#1d4ed8] shadow-[0_0_8px_#1d4ed8]"></div>
                <h1 class="text-xs font-bold tracking-wider text-[#cbd5e1] uppercase">CULTURE ATLAS</h1>
              </div>
              <p class="text-[11px] text-[#94a3b8] mt-0.5 leading-snug font-normal">
                Ethically funded cultural institutions across the world
              </p>
            </div>
            
            <div class="flex items-center gap-1.5 shrink-0 pt-0.5">
              <span id="listTotalBadge" class="text-[11px] font-mono text-[#94a3b8] bg-[#161821] px-2 py-0.5 rounded border border-[#282c38]">
                203 mapped
              </span>
              <!-- Mobile Sheet Expand/Collapse Toggle Button -->
              <button id="mobileSheetToggleBtn" class="md:hidden text-xs text-[#94a3b8] hover:text-white bg-[#161821] border border-[#282c38] px-2 py-0.5 rounded flex items-center gap-1">
                <span id="sheetToggleText">Expand</span>
                <span id="sheetToggleArrow">▲</span>
              </button>
            </div>
          </div>

          <!-- Active Filter Banner (When city/country clicked) -->
          <div id="activeFilterBanner" class="hidden flex items-center justify-between bg-[#0e1628] border border-[#1d4ed8] px-2.5 py-1.5 rounded-lg text-xs">
            <div class="flex items-center gap-1.5 truncate">
              <span id="filterIcon" class="text-sm">📍</span>
              <span id="filterLabel" class="font-semibold text-white truncate">NEW YORK</span>
              <span id="filterCount" class="text-[#60a5fa] font-mono text-[11px]">(11)</span>
            </div>
            <button id="clearFilterBtn" class="text-xs text-[#94a3b8] hover:text-white px-1.5 py-0.5 rounded hover:bg-[#1a253c] transition ml-2 flex items-center gap-1">
              <span>Clear</span> <span>✕</span>
            </button>
          </div>

          <!-- Search Input -->
          <div class="relative">
            <input 
              type="text" 
              id="searchInput" 
              placeholder="Search museum, city, or sponsor..." 
              class="w-full bg-[#141722] border border-[#262a38] text-xs text-white placeholder-[#64748b] px-3 py-1.5 rounded-lg focus:outline-none focus:border-[#3b82f6] transition"
            />
            <button id="clearSearchBtn" class="hidden absolute right-2.5 top-1.5 text-[#64748b] hover:text-white text-xs">✕</button>
          </div>

          <!-- Quick Filters: Country & City Dropdowns -->
          <div class="grid grid-cols-2 gap-1.5 text-[11px] font-mono">
            <select id="countrySelect" class="bg-[#141722] border border-[#262a38] text-[#e2e8f0] px-2 py-1 rounded focus:outline-none focus:border-[#3b82f6] truncate">
              <option value="all">All Countries (35)</option>
            </select>
            <select id="citySelect" class="bg-[#141722] border border-[#262a38] text-[#e2e8f0] px-2 py-1 rounded focus:outline-none focus:border-[#3b82f6] truncate">
              <option value="all">All Cities (133)</option>
            </select>
          </div>

          <!-- Tier Quick Chips -->
          <div class="flex items-center gap-1.5 text-[10px] font-mono">
            <button class="tier-chip flex-1 py-1 px-1.5 rounded border border-emerald-900 bg-[#0c2419] text-emerald-400 font-semibold text-center hover:bg-[#113324] transition" data-tier="A">
              Tier A (126)
            </button>
            <button class="tier-chip flex-1 py-1 px-1.5 rounded border border-blue-900 bg-[#0e213b] text-blue-400 font-semibold text-center hover:bg-[#132d52] transition" data-tier="B">
              Tier B (60)
            </button>
            <button class="tier-chip flex-1 py-1 px-1.5 rounded border border-slate-700 bg-[#171a24] text-slate-400 font-semibold text-center hover:bg-[#202534] transition" data-tier="U">
              Tier U (17)
            </button>
          </div>
        </div>

        <!-- Scrollable Institutions Feed -->
        <div id="institutionsListContainer" class="flex-1 overflow-y-auto custom-scrollbar p-3 space-y-2 pb-16 md:pb-3">
          <!-- Populated dynamically -->
        </div>

        <!-- Mission & Criteria Bar -->
        <div class="p-2.5 border-t border-[#1c212a] bg-[#0a0d14] flex flex-col gap-1.5 text-xs shrink-0">
          <div class="flex items-center justify-between">
            <span class="text-[10.5px] text-[#94a3b8] flex items-center gap-1">
              <span>🛡️</span> <span>Zero defense & fossil fuel underwriting</span>
            </span>
            <button id="openMomaAuditBtn" class="text-[10.5px] font-semibold text-[#f1c21b] hover:text-white bg-[#221c08] border border-[#4d3d0f] hover:border-[#f1c21b] px-2 py-0.5 rounded transition flex items-center gap-1">
              <span>⚠️</span> <span>Why MoMA is excluded</span>
            </button>
          </div>
        </div>

      </aside>

      <!-- ========================================================= -->
      <!-- 🌍 3D GLOBE VIEWPORT (Fullscreen on Mobile, Split on Desktop) -->
      <!-- ========================================================= -->
      <main id="globeViewport" class="flex-1 relative flex items-center justify-center bg-[#020408] overflow-hidden w-full h-full min-h-[300px]">
        
        <canvas id="globeCanvas" width="900" height="700" class="w-full h-full object-contain"></canvas>

        <!-- FLOATING WHITE CARD (Pinned to selected institution with Website Link) -->
        <div id="floatingCard" class="absolute z-20 pointer-events-auto bg-white text-slate-900 rounded-lg px-3 py-2 shadow-2xl transition duration-150 transform -translate-x-1/2 -translate-y-full mb-3 cursor-pointer border border-slate-100 max-w-[220px] sm:max-w-[250px]">
          <div class="flex items-center justify-between gap-1.5">
            <div id="floatingCardTitle" class="font-bold text-[12px] sm:text-[13px] text-slate-950 leading-tight truncate">Plug In ICA</div>
            <span id="floatingCardTier" class="text-[8.5px] sm:text-[9px] font-semibold uppercase px-1.5 py-0.5 bg-emerald-100 text-emerald-800 rounded shrink-0">Verified</span>
          </div>
          <div id="floatingCardMeta" class="text-[10.5px] sm:text-[11px] text-slate-500 mt-0.5 flex items-center gap-1">
            <span>Winnipeg, Canada</span>
          </div>
          <div class="mt-1.5 pt-1.5 border-t border-slate-100 flex items-center justify-between text-[10.5px] sm:text-[11px]">
            <a id="floatingCardWebLink" href="https://plugin.org" target="_blank" rel="noopener noreferrer" 
               class="inline-flex items-center gap-1 font-medium text-[#1d4ed8] hover:text-[#1e40af] hover:underline"
               onclick="event.stopPropagation()">
              <span>🌐</span> <span id="floatingCardDomain" class="truncate max-w-[90px]">plugin.org</span> <span class="text-[9px]">↗</span>
            </a>
            <span class="text-[9.5px] text-slate-400 font-mono">Dossier →</span>
          </div>
          <div class="absolute bottom-0 left-1/2 -translate-x-1/2 translate-y-full w-0 h-0 border-x-[6px] border-x-transparent border-t-[6px] border-t-white"></div>
        </div>

        <!-- Floating Mobile Mode Switcher Pill (Matching Reference: GLOBE VIEW | CITY LIST) -->
        <div class="md:hidden absolute top-3 left-1/2 -translate-x-1/2 z-20 pointer-events-auto flex items-center bg-[#101420]/90 backdrop-blur-md border border-[#232a3c] rounded-full p-0.5 shadow-xl text-[11px] font-medium font-mono">
          <button id="mobileModeGlobe" class="px-3 py-1 rounded-full bg-[#1d4ed8] text-white transition flex items-center gap-1">
            <span>🌐</span> <span>Globe</span>
          </button>
          <button id="mobileModeList" class="px-3 py-1 rounded-full text-[#94a3b8] hover:text-white transition flex items-center gap-1">
            <span>📋</span> <span>List (<span id="mobileCountBadge">203</span>)</span>
          </button>
        </div>

        <!-- Bottom-Left Title & Scale Bar -->
        <div class="absolute bottom-20 md:bottom-4 left-4 z-10 pointer-events-none flex flex-col gap-1 text-[10px] text-[#64748b] font-mono">
          <div class="text-[11px] text-[#94a3b8] font-sans font-medium hidden sm:block">
            Ethically funded cultural institutions across the world
          </div>
          <div class="flex items-center gap-1.5">
            <div class="w-14 sm:w-16 h-1 border-b border-l border-r border-[#64748b]"></div>
            <span>2,000 km</span>
          </div>
        </div>

        <!-- Floating Zoom Controls (Ergonomic mobile positioning) -->
        <div class="absolute bottom-20 md:bottom-4 right-4 z-20 pointer-events-auto flex flex-col gap-1.5">
          <button id="zoomInBtn" class="w-8 h-8 sm:w-8 sm:h-8 bg-[#161821]/90 backdrop-blur-sm hover:bg-[#232838] border border-[#282c38] hover:border-[#3b82f6] text-[#94a3b8] hover:text-white rounded-lg flex items-center justify-center font-bold text-sm transition shadow-lg active:scale-95" title="Zoom In">+</button>
          <button id="zoomOutBtn" class="w-8 h-8 sm:w-8 sm:h-8 bg-[#161821]/90 backdrop-blur-sm hover:bg-[#232838] border border-[#282c38] hover:border-[#3b82f6] text-[#94a3b8] hover:text-white rounded-lg flex items-center justify-center font-bold text-sm transition shadow-lg active:scale-95" title="Zoom Out">−</button>
          <button id="resetViewBtn" class="w-8 h-8 sm:w-8 sm:h-8 bg-[#161821]/90 backdrop-blur-sm hover:bg-[#232838] border border-[#282c38] hover:border-[#3b82f6] text-[#94a3b8] hover:text-white rounded-lg flex items-center justify-center text-xs transition shadow-lg active:scale-95" title="Recenter View">◎</button>
          <button id="spinBtn" class="w-8 h-8 sm:w-8 sm:h-8 bg-[#161821]/90 backdrop-blur-sm hover:bg-[#232838] border border-[#282c38] hover:border-[#3b82f6] text-[#94a3b8] rounded-lg flex items-center justify-center text-xs transition shadow-lg active:scale-95" title="Toggle Auto-Spin">↻</button>
        </div>

      </main>

      <!-- DETAIL / RESEARCH MODAL DRAWER -->
      <div id="detailDrawer" class="hidden absolute inset-0 md:inset-y-0 md:left-auto md:right-0 w-full md:w-[420px] z-50 bg-[#090c14] border-l border-[#1c212a] p-5 flex flex-col shadow-2xl overflow-y-auto custom-scrollbar">
        <div class="flex items-center justify-between border-b border-[#1c212a] pb-3">
          <span class="text-[10px] font-mono uppercase text-[#3b82f6] tracking-wider font-semibold">Institutional Dossier</span>
          <button id="closeDetailBtn" class="text-[#64748b] hover:text-white text-base p-1">✕</button>
        </div>
        <div id="detailBody" class="mt-4 space-y-4 flex-1">
          <!-- Rendered dynamically -->
        </div>
      </div>

    </div>
  </div>

  <script>
    // -------------------------------------------------------------
    // DATASETS
    // -------------------------------------------------------------
    const ALL_INSTITUTIONS = {institutions_json};
    const COUNTRY_POLYS = {countries_json};

    const COUNTRY_NORM = {{
      'united states': 'usa',
      'united states of america': 'usa',
      'usa': 'usa',
      'united kingdom': 'uk',
      'uk': 'uk',
      'england': 'uk',
      'scotland': 'uk',
      'wales': 'uk',
      'united arab emirates': 'uae',
      'uae': 'uae',
      'hong kong': 'hong kong',
      'china': 'china',
      'south korea': 'south korea',
      'korea': 'south korea',
      'republic of korea': 'south korea'
    }};

    function matchCountry(c1, c2) {{
      if (!c1 || !c2) return false;
      const s1 = c1.toLowerCase().trim();
      const s2 = c2.toLowerCase().trim();
      const n1 = COUNTRY_NORM[s1] || s1;
      const n2 = COUNTRY_NORM[s2] || s2;
      return n1 === n2 || s1.includes(s2) || s2.includes(s1);
    }}

    const COUNTRY_CENTROIDS = [
      {{ name: 'ALGERIA', lon: 2.6, lat: 28.0 }},
      {{ name: 'LIBYA', lon: 17.2, lat: 26.3 }},
      {{ name: 'SUDAN', lon: 30.2, lat: 12.8 }},
      {{ name: 'SAUDI ARABIA', lon: 45.0, lat: 23.8 }},
      {{ name: 'IRAN', lon: 53.6, lat: 32.4 }},
      {{ name: 'KAZAKHSTAN', lon: 66.9, lat: 48.0 }},
      {{ name: 'INDIA', lon: 78.9, lat: 20.5 }},
      {{ name: 'RUSSIA', lon: 95.0, lat: 60.0 }},
      {{ name: 'MONGOLIA', lon: 103.8, lat: 46.8 }},
      {{ name: 'CHINA', lon: 104.1, lat: 35.8 }},
      {{ name: 'CANADA', lon: -106.3, lat: 56.1 }},
      {{ name: 'UNITED STATES', lon: -98.5, lat: 39.5 }},
      {{ name: 'FRANCE', lon: 2.2, lat: 46.2 }},
      {{ name: 'GERMANY', lon: 10.4, lat: 51.1 }},
      {{ name: 'UNITED KINGDOM', lon: -1.5, lat: 54.0 }},
      {{ name: 'SPAIN', lon: -3.7, lat: 40.4 }},
      {{ name: 'ITALY', lon: 12.5, lat: 41.9 }},
      {{ name: 'JAPAN', lon: 138.2, lat: 36.2 }},
      {{ name: 'BRAZIL', lon: -51.9, lat: -14.2 }},
      {{ name: 'AUSTRALIA', lon: 133.7, lat: -25.2 }}
    ];

    const PRIORITY_CITIES = [
      {{ name: 'NEW YORK', lon: -74.006, lat: 40.7128 }},
      {{ name: 'LONDON', lon: -0.1278, lat: 51.5074 }},
      {{ name: 'MADRID', lon: -3.7038, lat: 40.4168 }},
      {{ name: 'CHICAGO', lon: -87.6298, lat: 41.8781 }},
      {{ name: 'MARFA', lon: -104.030, lat: 30.309 }},
      {{ name: 'LOS ANGELES', lon: -118.2437, lat: 34.0522 }},
      {{ name: 'STOCKHOLM', lon: 18.0686, lat: 59.3293 }},
      {{ name: 'TOKYO', lon: 139.6917, lat: 35.6895 }},
      {{ name: 'HONG KONG', lon: 114.1694, lat: 22.3193 }},
      {{ name: 'PARIS', lon: 2.3522, lat: 48.8566 }},
      {{ name: 'BERLIN', lon: 13.4050, lat: 52.5200 }},
      {{ name: 'BASEL', lon: 7.5886, lat: 47.5596 }},
      {{ name: 'AMSTERDAM', lon: 4.9041, lat: 52.3676 }}
    ];

    let selectedCountryFilter = 'all';
    let selectedCityFilter = 'all';
    let selectedTierFilter = 'all';
    let searchQuery = '';

    let filteredList = ALL_INSTITUTIONS.slice();
    let selectedInstitution = ALL_INSTITUTIONS.find(i => i.name.toLowerCase().includes('plug in')) || ALL_INSTITUTIONS[0];
    let hoveredInstitution = null;

    // -------------------------------------------------------------
    // MOBILE BOTTOM SHEET LOGIC (Peek / Half / Full States)
    // -------------------------------------------------------------
    const bottomSheet = document.getElementById('bottomSheet');
    const sheetDragHandle = document.getElementById('sheetDragHandle');
    const mobileSheetToggleBtn = document.getElementById('mobileSheetToggleBtn');
    const sheetToggleText = document.getElementById('sheetToggleText');
    const sheetToggleArrow = document.getElementById('sheetToggleArrow');
    const mobileModeGlobe = document.getElementById('mobileModeGlobe');
    const mobileModeList = document.getElementById('mobileModeList');
    const mobileCountBadge = document.getElementById('mobileCountBadge');

    let sheetState = 'peek'; // 'peek', 'half', 'full'

    function setSheetState(state) {{
      if (window.innerWidth >= 768) return; // Desktop maintains split layout
      sheetState = state;
      bottomSheet.classList.remove('sheet-peek', 'sheet-half', 'sheet-full');
      if (state === 'peek') {{
        bottomSheet.classList.add('sheet-peek');
        sheetToggleText.textContent = 'Expand';
        sheetToggleArrow.textContent = '▲';
        mobileModeGlobe.className = 'px-3 py-1 rounded-full bg-[#1d4ed8] text-white transition flex items-center gap-1';
        mobileModeList.className = 'px-3 py-1 rounded-full text-[#94a3b8] hover:text-white transition flex items-center gap-1';
      }} else if (state === 'half') {{
        bottomSheet.classList.add('sheet-half');
        sheetToggleText.textContent = 'Full';
        sheetToggleArrow.textContent = '▲';
      }} else if (state === 'full') {{
        bottomSheet.classList.add('sheet-full');
        sheetToggleText.textContent = 'Collapse';
        sheetToggleArrow.textContent = '▼';
        mobileModeGlobe.className = 'px-3 py-1 rounded-full text-[#94a3b8] hover:text-white transition flex items-center gap-1';
        mobileModeList.className = 'px-3 py-1 rounded-full bg-[#1d4ed8] text-white transition flex items-center gap-1';
      }}
    }}

    sheetDragHandle.addEventListener('click', () => {{
      if (sheetState === 'peek') setSheetState('half');
      else if (sheetState === 'half') setSheetState('full');
      else setSheetState('peek');
    }});

    mobileSheetToggleBtn.addEventListener('click', () => {{
      if (sheetState === 'peek') setSheetState('half');
      else if (sheetState === 'half') setSheetState('full');
      else setSheetState('peek');
    }});

    mobileModeGlobe.addEventListener('click', () => {{
      setSheetState('peek');
    }});

    mobileModeList.addEventListener('click', () => {{
      setSheetState('full');
    }});

    // Populate dropdowns
    const countrySelect = document.getElementById('countrySelect');
    const citySelect = document.getElementById('citySelect');
    const countryMap = {{}};
    const cityMap = {{}};
    ALL_INSTITUTIONS.forEach(i => {{
      countryMap[i.country] = (countryMap[i.country] || 0) + 1;
      cityMap[i.city] = (cityMap[i.city] || 0) + 1;
    }});

    Object.keys(countryMap).sort().forEach(c => {{
      const opt = document.createElement('option');
      opt.value = c;
      opt.textContent = `${{c}} (${{countryMap[c]}})`;
      countrySelect.appendChild(opt);
    }});

    Object.keys(cityMap).sort().forEach(c => {{
      const opt = document.createElement('option');
      opt.value = c;
      opt.textContent = `${{c}} (${{cityMap[c]}})`;
      citySelect.appendChild(opt);
    }});

    function applyFilters() {{
      filteredList = ALL_INSTITUTIONS.filter(inst => {{
        if (selectedCountryFilter !== 'all' && !matchCountry(inst.country, selectedCountryFilter)) return false;
        if (selectedCityFilter !== 'all' && inst.city.toLowerCase() !== selectedCityFilter.toLowerCase()) return false;
        if (selectedTierFilter !== 'all' && inst.tier !== selectedTierFilter) return false;
        if (searchQuery) {{
          const q = searchQuery.toLowerCase();
          const mName = inst.name.toLowerCase().includes(q);
          const mLoc = inst.location.toLowerCase().includes(q);
          const mFund = (inst.funding || '').toLowerCase().includes(q);
          const mWatch = (inst.watch || '').toLowerCase().includes(q);
          if (!mName && !mLoc && !mFund && !mWatch) return false;
        }}
        return true;
      }});

      document.getElementById('listTotalBadge').textContent = `${{filteredList.length}} mapped`;
      mobileCountBadge.textContent = `${{filteredList.length}}`;

      const banner = document.getElementById('activeFilterBanner');
      const fIcon = document.getElementById('filterIcon');
      const fLabel = document.getElementById('filterLabel');
      const fCount = document.getElementById('filterCount');

      if (selectedCityFilter !== 'all') {{
        banner.classList.remove('hidden');
        fIcon.textContent = '📍';
        fLabel.textContent = `CITY: ${{selectedCityFilter.toUpperCase()}}`;
        fCount.textContent = `(${{filteredList.length}})`;
      }} else if (selectedCountryFilter !== 'all') {{
        banner.classList.remove('hidden');
        fIcon.textContent = '🌍';
        fLabel.textContent = `COUNTRY: ${{selectedCountryFilter.toUpperCase()}}`;
        fCount.textContent = `(${{filteredList.length}})`;
      }} else if (searchQuery) {{
        banner.classList.remove('hidden');
        fIcon.textContent = '🔍';
        fLabel.textContent = `"${{searchQuery}}"`;
        fCount.textContent = `(${{filteredList.length}})`;
      }} else {{
        banner.classList.add('hidden');
      }}

      countrySelect.value = selectedCountryFilter;
      citySelect.value = selectedCityFilter;

      renderLeftList();
    }}

    function renderLeftList() {{
      const container = document.getElementById('institutionsListContainer');
      if (filteredList.length === 0) {{
        container.innerHTML = `
          <div class="text-center py-8 px-4 text-[#64748b] text-xs">
            <p class="font-medium text-slate-400">No institutions match this filter.</p>
            <button id="resetFromEmptyBtn" class="mt-3 text-[#3b82f6] hover:underline text-xs">Reset filters</button>
          </div>
        `;
        document.getElementById('resetFromEmptyBtn')?.addEventListener('click', clearAllFilters);
        return;
      }}

      container.innerHTML = filteredList.map(inst => {{
        const isSel = selectedInstitution && selectedInstitution.name === inst.name;
        const tierCol = inst.tier === 'A' ? 'text-emerald-400 border-emerald-900 bg-[#0a2016]' : inst.tier === 'B' ? 'text-blue-400 border-blue-900 bg-[#0d1d33]' : 'text-slate-400 border-slate-700 bg-[#161922]';
        const tierName = inst.tier === 'A' ? 'Tier A · Verified' : inst.tier === 'B' ? 'Tier B · One Name' : 'Tier U';

        let displayDomain = 'website';
        try {{
          displayDomain = new URL(inst.website || inst.sources[0]).hostname.replace(/^www\\./, '');
        }} catch(e) {{}}

        return `
          <div class="inst-card bg-[#0b0e16] border border-[#1b202d] rounded-xl p-3 cursor-pointer hover:border-[#3b82f6] hover:bg-[#101420] ${{isSel ? 'active' : ''}}" data-name="${{inst.name.replace(/"/g, '&quot;')}}">
            <div class="flex items-start justify-between gap-2">
              <h3 class="font-semibold text-white text-xs leading-snug truncate max-w-[220px] sm:max-w-[260px]">${{inst.name}}</h3>
              <span class="text-[9px] font-mono px-1.5 py-0.5 rounded border ${{tierCol}} shrink-0">${{tierName}}</span>
            </div>
            <div class="flex items-center gap-1.5 text-[11px] text-[#60a5fa] mt-1 font-mono">
              <span>📍</span> <span class="truncate">${{inst.location}}</span>
              <span class="text-slate-600">·</span>
              <span class="text-slate-400 text-[10px] shrink-0">${{inst.size === 'L' ? 'Large (>$20M)' : 'Small/Mid'}}</span>
            </div>
            <p class="text-[11px] text-slate-400 mt-1.5 leading-relaxed line-clamp-2">${{inst.funding}}</p>
            ${{inst.watch ? `
              <div class="mt-2 pt-1.5 border-t border-[#161a26] text-[10px] text-amber-300/80 truncate flex items-center gap-1">
                <span>⚠️</span> <span>${{inst.watch}}</span>
              </div>
            ` : ''}}
            <div class="mt-2.5 pt-2 border-t border-[#161b26] flex items-center justify-between">
              <a href="${{inst.website || inst.sources[0]}}" target="_blank" rel="noopener noreferrer" 
                 class="website-pill inline-flex items-center gap-1 text-[10.5px] font-mono text-[#60a5fa] hover:text-white bg-[#101726] hover:bg-[#1a253c] border border-[#1e2a42] hover:border-[#3b82f6] px-2 py-0.5 rounded transition"
                 onclick="event.stopPropagation()">
                <span>🌐</span>
                <span class="truncate max-w-[120px]">${{displayDomain}}</span>
                <span class="text-[9px]">↗</span>
              </a>
              <span class="text-[10px] text-slate-500 hover:text-slate-300 font-mono">View on Globe →</span>
            </div>
          </div>
        `;
      }}).join('');

      container.querySelectorAll('.inst-card').forEach(card => {{
        card.addEventListener('click', () => {{
          const name = card.getAttribute('data-name');
          const inst = ALL_INSTITUTIONS.find(i => i.name === name);
          if (inst) {{
            selectInstitution(inst);
            // On mobile, collapse to peek so user sees globe!
            if (window.innerWidth < 768) setSheetState('peek');
          }}
        }});
      }});
    }}

    function filterByCity(cityName) {{
      selectedCityFilter = cityName;
      selectedCountryFilter = 'all';
      applyFilters();

      const cty = PRIORITY_CITIES.find(c => c.name.toLowerCase() === cityName.toLowerCase());
      if (cty) flyTo(cty.lon, cty.lat);
      else {{
        const inst = ALL_INSTITUTIONS.find(i => i.city.toLowerCase() === cityName.toLowerCase());
        if (inst) flyTo(inst.lon, inst.lat);
      }}

      // On mobile, automatically show the matching items in half sheet!
      if (window.innerWidth < 768) setSheetState('half');
    }}

    function filterByCountry(countryName) {{
      selectedCountryFilter = countryName;
      selectedCityFilter = 'all';
      applyFilters();

      const c = COUNTRY_CENTROIDS.find(x => matchCountry(x.name, countryName));
      if (c) flyTo(c.lon, c.lat);
      else {{
        const inst = ALL_INSTITUTIONS.find(i => matchCountry(i.country, countryName));
        if (inst) flyTo(inst.lon, inst.lat);
      }}

      // On mobile, automatically show matching items in half sheet!
      if (window.innerWidth < 768) setSheetState('half');
    }}

    function clearAllFilters() {{
      selectedCityFilter = 'all';
      selectedCountryFilter = 'all';
      selectedTierFilter = 'all';
      searchQuery = '';
      searchInput.value = '';
      clearSearchBtn.classList.add('hidden');
      document.querySelectorAll('.tier-chip').forEach(b => b.style.opacity = '1');
      applyFilters();
    }}

    document.getElementById('clearFilterBtn').addEventListener('click', clearAllFilters);
    document.getElementById('countrySelect').addEventListener('change', e => {{
      if (e.target.value === 'all') clearAllFilters();
      else filterByCountry(e.target.value);
    }});
    document.getElementById('citySelect').addEventListener('change', e => {{
      if (e.target.value === 'all') clearAllFilters();
      else filterByCity(e.target.value);
    }});

    document.querySelectorAll('.tier-chip').forEach(chip => {{
      chip.addEventListener('click', () => {{
        const t = chip.getAttribute('data-tier');
        selectedTierFilter = (selectedTierFilter === t) ? 'all' : t;
        document.querySelectorAll('.tier-chip').forEach(c => {{
          const ct = c.getAttribute('data-tier');
          c.style.opacity = (selectedTierFilter === 'all' || selectedTierFilter === ct) ? '1' : '0.4';
        }});
        applyFilters();
      }});
    }});

    searchInput.addEventListener('input', e => {{
      searchQuery = e.target.value.trim();
      clearSearchBtn.classList.toggle('hidden', searchQuery === '');
      applyFilters();
      if (searchQuery && window.innerWidth < 768 && sheetState === 'peek') {{
        setSheetState('half');
      }}
    }});
    clearSearchBtn.addEventListener('click', () => {{
      searchInput.value = '';
      searchQuery = '';
      clearSearchBtn.classList.add('hidden');
      applyFilters();
    }});

    // -------------------------------------------------------------
    // 3D CANVAS GLOBE CARTOGRAPHY & TOUCH/POINTER GESTURES
    // -------------------------------------------------------------
    const canvas = document.getElementById('globeCanvas');
    const ctx = canvas.getContext('2d');

    let rotLon = -45;
    let rotLat = 35;
    let startRotLon = -45;
    let startRotLat = 35;
    let targetRotLon = -45;
    let targetRotLat = 35;
    let isFlying = false;
    let flightProgress = 0;
    let isAutoSpinning = false;
    let isDragging = false;
    let lastX = 0, lastY = 0;
    let pointerStartX = 0, pointerStartY = 0, pointerDownTime = 0;

    let globeRadius = 260;
    let baseRadius = 260;
    let targetRadius = 260;

    const getMinRadius = () => Math.min(canvas.width, canvas.height) * 0.25;
    const getMaxRadius = () => Math.min(canvas.width, canvas.height) * 2.5;

    function resizeCanvas() {{
      const wrapper = document.getElementById('globeViewport');
      const w = wrapper.clientWidth;
      const h = wrapper.clientHeight;
      canvas.width = w;
      canvas.height = h;
      baseRadius = Math.min(w, h) * (window.innerWidth < 768 ? 0.40 : 0.44);
      if (!targetRadius || targetRadius === 260) {{
        targetRadius = baseRadius;
        globeRadius = baseRadius;
      }}
    }}
    window.addEventListener('resize', resizeCanvas);
    resizeCanvas();

    function project(lon, lat, r, cx, cy) {{
      const rad = Math.PI / 180;
      const lam = (lon - rotLon) * rad;
      const phi = lat * rad;
      const phi0 = rotLat * rad;

      const cosC = Math.sin(phi0) * Math.sin(phi) + Math.cos(phi0) * Math.cos(phi) * Math.cos(lam);
      const x = r * Math.cos(phi) * Math.sin(lam);
      const y = -r * (Math.cos(phi0) * Math.sin(phi) - Math.sin(phi0) * Math.cos(phi) * Math.cos(lam));

      if (cosC >= 0) return {{ x: cx + x, y: cy + y, depth: cosC, front: true }};
      const angle = Math.atan2(y, x);
      return {{ x: cx + r * Math.cos(angle), y: cy + r * Math.sin(angle), depth: cosC, front: false }};
    }}

    function unproject(screenX, screenY, r, cx, cy) {{
      const dx = (screenX - cx) / r;
      const dy = -(screenY - cy) / r;
      const rho2 = dx * dx + dy * dy;
      if (rho2 > 1) return null;

      const c = Math.asin(Math.sqrt(rho2));
      const sinc = Math.sin(c);
      const cosc = Math.cos(c);
      const phi0 = rotLat * (Math.PI / 180);
      const lambda0 = rotLon * (Math.PI / 180);

      let phi, lambda;
      if (rho2 < 1e-6) {{
        phi = phi0;
        lambda = lambda0;
      }} else {{
        const rho = Math.sqrt(rho2);
        phi = Math.asin(cosc * Math.sin(phi0) + (dy * sinc * Math.cos(phi0)) / rho);
        lambda = lambda0 + Math.atan2(dx * sinc, rho * Math.cos(phi0) * cosc - dy * Math.sin(phi0) * sinc);
      }}

      return {{ lat: phi * (180 / Math.PI), lon: lambda * (180 / Math.PI) }};
    }}

    function pointInPolygon(lon, lat, poly) {{
      let inside = false;
      const n = poly.length;
      for (let i = 0, j = n - 1; i < n; j = i++) {{
        const xi = poly[i][0], yi = poly[i][1];
        const xj = poly[j][0], yj = poly[j][1];
        const intersect = ((yi > lat) !== (yj > lat)) &&
          (lon < (xj - xi) * (lat - yi) / (yj - yi) + xi);
        if (intersect) inside = !inside;
      }}
      return inside;
    }}

    let renderedCityBadges = [];
    let visibleDots = [];
    const occupiedBoxes = [];
    function clearOccupancy() {{ occupiedBoxes.length = 0; }}
    function isColliding(box, pad = 3) {{
      const x1 = box.x - pad;
      const y1 = box.y - pad;
      const x2 = box.x + box.w + pad;
      const y2 = box.y + box.h + pad;
      for (let i = 0; i < occupiedBoxes.length; i++) {{
        const b = occupiedBoxes[i];
        if (x1 < b.x2 && x2 > b.x1 && y1 < b.y2 && y2 > b.y1) return true;
      }}
      return false;
    }}
    function registerBox(x, y, w, h, pad = 3) {{
      occupiedBoxes.push({{ x1: x - pad, y1: y - pad, x2: x + w + pad, y2: y + h + pad }});
    }}

    function roundRect(ctx, x, y, width, height, radius) {{
      ctx.beginPath();
      ctx.moveTo(x + radius, y);
      ctx.lineTo(x + width - radius, y);
      ctx.quadraticCurveTo(x + width, y, x + width, y + radius);
      ctx.lineTo(x + width, y + height - radius);
      ctx.quadraticCurveTo(x + width, y + height, x + width - radius, y + height);
      ctx.lineTo(x + radius, y + height);
      ctx.quadraticCurveTo(x, y + height, x, y + height - radius);
      ctx.lineTo(x, y + radius);
      ctx.quadraticCurveTo(x, y, x + radius, y);
      ctx.closePath();
    }}

    function render() {{
      const w = canvas.width;
      const h = canvas.height;
      const cx = w / 2;
      const cy = h / 2;

      globeRadius += (targetRadius - globeRadius) * 0.065;
      const r = globeRadius;

      ctx.clearRect(0, 0, w, h);
      clearOccupancy();
      renderedCityBadges = [];

      if (isFlying) {{
        flightProgress += 0.011;
        if (flightProgress >= 1) {{
          flightProgress = 1;
          isFlying = false;
          rotLon = targetRotLon;
          rotLat = targetRotLat;
        }} else {{
          const t = flightProgress;
          const ease = t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
          rotLon = startRotLon + (targetRotLon - startRotLon) * ease;
          rotLat = startRotLat + (targetRotLat - startRotLat) * ease;
        }}
      }} else if (isAutoSpinning && !isDragging) {{
        rotLon = (rotLon + 0.04) % 360;
      }}

      // Ocean
      ctx.fillStyle = '#030f24';
      ctx.beginPath();
      ctx.arc(cx, cy, r, 0, Math.PI * 2);
      ctx.fill();

      ctx.save();
      ctx.beginPath();
      ctx.arc(cx, cy, r, 0, Math.PI * 2);
      ctx.clip();

      // Electric blue graticules
      ctx.strokeStyle = 'rgba(29, 78, 216, 0.25)';
      ctx.lineWidth = 0.6;
      [-60, -30, 0, 30, 60, 75].forEach(lat => {{
        ctx.beginPath();
        let first = true;
        for (let lon = -180; lon <= 180; lon += 6) {{
          const pt = project(lon, lat, r, cx, cy);
          if (pt.front) {{
            if (first) {{ ctx.moveTo(pt.x, pt.y); first = false; }}
            else {{ ctx.lineTo(pt.x, pt.y); }}
          }} else {{ first = true; }}
        }}
        ctx.stroke();
      }});

      for (let lon = -180; lon < 180; lon += 30) {{
        ctx.beginPath();
        let first = true;
        for (let lat = -80; lat <= 80; lat += 6) {{
          const pt = project(lon, lat, r, cx, cy);
          if (pt.front) {{
            if (first) {{ ctx.moveTo(pt.x, pt.y); first = false; }}
            else {{ ctx.lineTo(pt.x, pt.y); }}
          }} else {{ first = true; }}
        }}
        ctx.stroke();
      }}

      // Multi-tone Country Polygons
      COUNTRY_POLYS.forEach(country => {{
        const isCountryActive = selectedCountryFilter !== 'all' && matchCountry(country.n, selectedCountryFilter);
        ctx.fillStyle = isCountryActive ? '#2563eb' : country.c;
        ctx.beginPath();
        let anyVisible = false;

        country.r.forEach(ring => {{
          let anyFrontInRing = false;
          for (let i = 0; i < ring.length; i++) {{
            const pt = project(ring[i][0], ring[i][1], r, cx, cy);
            if (pt.front) {{ anyFrontInRing = true; break; }}
          }}
          if (!anyFrontInRing) return;

          anyVisible = true;
          let first = true;
          for (let i = 0; i < ring.length; i++) {{
            const pt = project(ring[i][0], ring[i][1], r, cx, cy);
            if (first) {{ ctx.moveTo(pt.x, pt.y); first = false; }}
            else {{ ctx.lineTo(pt.x, pt.y); }}
          }}
          ctx.closePath();
        }});

        if (anyVisible) {{
          ctx.fill();
          ctx.strokeStyle = isCountryActive ? '#93c5fd' : '#020b18';
          ctx.lineWidth = isCountryActive ? 1.2 : 0.65;
          ctx.stroke();
        }}
      }});

      // Country Centroid Labels
      ctx.font = '600 9.5px "Inter", sans-serif';
      COUNTRY_CENTROIDS.forEach(c => {{
        const pt = project(c.lon, c.lat, r, cx, cy);
        if (pt.front && pt.depth > 0.28) {{
          const isSelected = selectedCountryFilter !== 'all' && matchCountry(c.name, selectedCountryFilter);
          const tw = ctx.measureText(c.name).width;
          const box = {{ x: pt.x - tw / 2, y: pt.y - 5.5, w: tw, h: 11 }};

          if (!isColliding(box, 3)) {{
            ctx.fillStyle = isSelected ? '#ffffff' : '#5c8477';
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillText(c.name, pt.x, pt.y);
            registerBox(box.x, box.y, box.w, box.h, 3);
          }}
        }}
      }});

      // City Badges (■ CITY)
      PRIORITY_CITIES.forEach(cty => {{
        const pt = project(cty.lon, cty.lat, r, cx, cy);
        if (pt.front && pt.depth > 0.3) {{
          const isSelected = selectedCityFilter.toLowerCase() === cty.name.toLowerCase();
          
          ctx.font = (isSelected ? '700 10px' : '600 9.5px') + ' "Inter", sans-serif';
          const tw = ctx.measureText(cty.name).width;
          const badgeW = tw + 18;
          const badgeH = 17;
          const bx = pt.x - 2;
          const by = pt.y - badgeH / 2;

          const box = {{ x: bx, y: by, w: badgeW, h: badgeH }};
          if (!isColliding(box, 2) || isSelected) {{
            renderedCityBadges.push({{
              name: cty.name,
              x: bx,
              y: by,
              w: badgeW,
              h: badgeH,
              lon: cty.lon,
              lat: cty.lat
            }});

            ctx.fillStyle = isSelected ? '#1d4ed8' : 'rgba(9, 14, 24, 0.92)';
            roundRect(ctx, bx, by, badgeW, badgeH, 4);
            ctx.fill();

            ctx.strokeStyle = isSelected ? '#ffffff' : 'rgba(59, 130, 246, 0.45)';
            ctx.lineWidth = isSelected ? 1.4 : 1;
            ctx.stroke();

            ctx.fillStyle = isSelected ? '#f1c21b' : '#ffffff';
            ctx.fillRect(bx + 4.5, by + 6, 3, 3);

            ctx.fillStyle = '#ffffff';
            ctx.textAlign = 'left';
            ctx.textBaseline = 'middle';
            ctx.fillText(cty.name, bx + 12, by + badgeH / 2 + 0.5);

            registerBox(box.x, box.y, box.w, box.h, 2);
          }}
        }}
      }});

      ctx.restore();

      // Perimeter Ring
      ctx.strokeStyle = '#1d4ed8';
      ctx.lineWidth = 1.5;
      ctx.beginPath();
      ctx.arc(cx, cy, r, 0, Math.PI * 2);
      ctx.stroke();

      // Institution Dots (Dispersal)
      visibleDots = [];
      filteredList.forEach(inst => {{
        const pt = project(inst.lon, inst.lat, r, cx, cy);
        if (pt.front && pt.depth > 0.08) {{
          visibleDots.push({{
            inst,
            x: pt.x,
            y: pt.y,
            depth: pt.depth,
            renderX: pt.x,
            renderY: pt.y
          }});
        }}
      }});

      const clusters = [];
      const visited = new Uint8Array(visibleDots.length);
      for (let i = 0; i < visibleDots.length; i++) {{
        if (visited[i]) continue;
        visited[i] = 1;
        const grp = [visibleDots[i]];
        for (let j = i + 1; j < visibleDots.length; j++) {{
          if (visited[j]) continue;
          if (Math.hypot(visibleDots[i].x - visibleDots[j].x, visibleDots[i].y - visibleDots[j].y) < 12) {{
            visited[j] = 1;
            grp.push(visibleDots[j]);
          }}
        }}
        clusters.push(grp);
      }}

      clusters.forEach(grp => {{
        if (grp.length > 1) {{
          let cxG = 0, cyG = 0;
          grp.forEach(d => {{ cxG += d.x; cyG += d.y; }});
          cxG /= grp.length; cyG /= grp.length;
          const sR = Math.min(32, Math.max(8, (grp.length * 12) / (2 * Math.PI)));
          grp.forEach((d, idx) => {{
            const ang = (idx / grp.length) * Math.PI * 2 - Math.PI / 2;
            d.renderX = cxG + Math.cos(ang) * sR;
            d.renderY = cyG + Math.sin(ang) * sR;
          }});
        }}
      }});

      visibleDots.forEach(d => {{
        const isSel = selectedInstitution && selectedInstitution.name === d.inst.name;
        const isHov = hoveredInstitution && hoveredInstitution.name === d.inst.name;

        if (isSel) {{
          ctx.beginPath();
          ctx.arc(d.renderX, d.renderY, 7, 0, Math.PI * 2);
          ctx.strokeStyle = '#ffffff';
          ctx.lineWidth = 1.5;
          ctx.stroke();
        }}

        ctx.beginPath();
        ctx.arc(d.renderX, d.renderY, isSel ? 4.5 : isHov ? 4 : 2.5, 0, Math.PI * 2);
        ctx.fillStyle = d.inst.tier === 'A' ? '#10b981' : d.inst.tier === 'B' ? '#3b82f6' : '#94a3b8';
        ctx.fill();
      }});

      // Floating White Card
      const floatingCard = document.getElementById('floatingCard');
      if (selectedInstitution) {{
        const pt = project(selectedInstitution.lon, selectedInstitution.lat, r, cx, cy);
        if (pt.front && pt.depth > 0.05) {{
          floatingCard.classList.remove('hidden');
          floatingCard.style.left = `${{pt.x}}px`;
          floatingCard.style.top = `${{pt.y}}px`;

          ctx.font = '500 13px "Inter", sans-serif';
          ctx.fillStyle = '#ffffff';
          ctx.textAlign = 'left';
          ctx.textBaseline = 'middle';
          ctx.fillText(selectedInstitution.name, pt.x + 12, pt.y);
        }} else {{
          floatingCard.classList.add('hidden');
        }}
      }} else {{
        floatingCard.classList.add('hidden');
      }}

      requestAnimationFrame(render);
    }}
    requestAnimationFrame(render);

    function flyTo(lon, lat) {{
      isAutoSpinning = false;
      let dLon = (lon - rotLon) % 360;
      if (dLon > 180) dLon -= 360;
      if (dLon < -180) dLon += 360;
      startRotLon = rotLon;
      startRotLat = rotLat;
      targetRotLon = rotLon + dLon;
      targetRotLat = Math.max(-75, Math.min(75, lat));
      flightProgress = 0;
      isFlying = true;
    }}

    function selectInstitution(inst) {{
      selectedInstitution = inst;
      document.getElementById('floatingCardTitle').textContent = inst.name;
      document.getElementById('floatingCardMeta').textContent = `${{inst.location}} · ${{inst.tier === 'A' ? 'Verified' : 'One Name'}}`;
      document.getElementById('floatingCardTier').textContent = inst.tier === 'A' ? 'Verified' : inst.tier === 'B' ? 'One Name' : 'Unverified';

      const webUrl = inst.website || (inst.sources && inst.sources[0]) || '';
      let domain = 'website';
      try {{ domain = new URL(webUrl).hostname.replace(/^www\\./, ''); }} catch(e) {{}}
      const webEl = document.getElementById('floatingCardWebLink');
      const domEl = document.getElementById('floatingCardDomain');
      if (webEl && domEl) {{
        webEl.href = webUrl;
        domEl.textContent = domain;
      }}

      document.querySelectorAll('.inst-card').forEach(c => {{
        const isTarget = c.getAttribute('data-name') === inst.name;
        c.classList.toggle('active', isTarget);
        if (isTarget) {{
          c.scrollIntoView({{ behavior: 'smooth', block: 'nearest' }});
        }}
      }});

      flyTo(inst.lon, inst.lat);
    }}

    function openDossier(inst) {{
      const drawer = document.getElementById('detailDrawer');
      const body = document.getElementById('detailBody');
      drawer.classList.remove('hidden');

      let domain = 'website';
      const webUrl = inst.website || (inst.sources && inst.sources[0]) || '';
      try {{ domain = new URL(webUrl).hostname.replace(/^www\\./, ''); }} catch(e) {{}}

      body.innerHTML = `
        <div>
          <h2 class="text-base sm:text-lg font-bold text-white leading-snug">${{inst.name}}</h2>
          <p class="text-xs text-[#3b82f6] mt-0.5 font-mono">${{inst.location}} · ${{inst.size === 'L' ? 'Large (>$20M)' : 'Small/Mid'}}</p>
        </div>
        ${{webUrl ? `
          <a href="${{webUrl}}" target="_blank" rel="noopener noreferrer" 
             class="inline-flex items-center justify-center gap-2 w-full py-2.5 bg-[#1d4ed8] hover:bg-[#2563eb] text-white font-semibold text-xs rounded-lg transition shadow-md active:scale-95">
            <span>🌐</span> <span>Visit Official Website (${{domain}})</span> <span>↗</span>
          </a>
        ` : ''}}
        <div class="bg-[#121622] p-3 rounded-lg border border-[#202535]">
          <span class="text-[10px] font-semibold text-emerald-400 uppercase tracking-wider block mb-1">Funding Architecture</span>
          <p class="text-xs text-slate-300 leading-relaxed">${{inst.funding}}</p>
        </div>
        ${{inst.watch ? `
          <div class="bg-[#121622] p-3 rounded-lg border border-[#202535]">
            <span class="text-[10px] font-semibold text-blue-400 uppercase tracking-wider block mb-1">Watch Notes & Scrutiny</span>
            <p class="text-xs text-slate-300 leading-relaxed">${{inst.watch}}</p>
          </div>
        ` : ''}}
        <div class="pt-2 border-t border-[#1c212a]">
          <span class="text-[10px] font-semibold text-slate-400 uppercase tracking-wider block mb-2">Sources & Filings</span>
          <div class="flex flex-col gap-1.5 font-mono">
            ${{(inst.sources || []).map(u => `
              <a href="${{u}}" target="_blank" class="text-[#60a5fa] hover:underline text-xs flex items-center gap-1">
                <span>↗</span> <span class="truncate">${{u}}</span>
              </a>
            `).join('')}}
          </div>
        </div>
      `;
    }}

    // -------------------------------------------------------------
    // TOUCH, POINTER & PINCH-TO-ZOOM HANDLING
    // -------------------------------------------------------------
    let touchDistance = 0;
    let initialZoomRadius = 0;

    canvas.addEventListener('touchstart', e => {{
      if (e.touches.length === 2) {{
        touchDistance = Math.hypot(
          e.touches[0].clientX - e.touches[1].clientX,
          e.touches[0].clientY - e.touches[1].clientY
        );
        initialZoomRadius = targetRadius;
      }}
    }}, {{ passive: true }});

    canvas.addEventListener('touchmove', e => {{
      if (e.touches.length === 2 && touchDistance > 0) {{
        const currentDist = Math.hypot(
          e.touches[0].clientX - e.touches[1].clientX,
          e.touches[0].clientY - e.touches[1].clientY
        );
        const scale = currentDist / touchDistance;
        targetRadius = Math.max(getMinRadius(), Math.min(getMaxRadius(), initialZoomRadius * scale));
      }}
    }}, {{ passive: true }});

    canvas.addEventListener('touchend', () => {{
      touchDistance = 0;
    }});

    canvas.addEventListener('pointerdown', e => {{
      isDragging = true;
      canvas.classList.add('dragging');
      lastX = e.clientX;
      lastY = e.clientY;
      pointerStartX = e.clientX;
      pointerStartY = e.clientY;
      pointerDownTime = Date.now();
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
        rotLon = (rotLon - dx * 0.18) % 360;
        rotLat = Math.max(-75, Math.min(75, rotLat + dy * 0.18));
      }} else {{
        let hitBadge = null;
        for (let i = 0; i < renderedCityBadges.length; i++) {{
          const b = renderedCityBadges[i];
          if (mx >= b.x && mx <= b.x + b.w && my >= b.y && my <= b.y + b.h) {{
            hitBadge = b;
            break;
          }}
        }}

        let hitDot = null;
        for (let i = 0; i < visibleDots.length; i++) {{
          const d = visibleDots[i];
          if (Math.hypot(d.renderX - mx, d.renderY - my) < 9) {{
            hitDot = d.inst;
            break;
          }}
        }}

        hoveredInstitution = hitDot;
        canvas.style.cursor = (hitBadge || hitDot) ? 'pointer' : 'grab';
      }}
    }});

    window.addEventListener('pointerup', e => {{
      if (isDragging) {{
        isDragging = false;
        canvas.classList.remove('dragging');
      }}

      const dist = Math.hypot(e.clientX - pointerStartX, e.clientY - pointerStartY);
      const duration = Date.now() - pointerDownTime;
      if (dist < 6 && duration < 350) {{
        handleCanvasClick(e);
      }}
    }});

    function handleCanvasClick(e) {{
      const rect = canvas.getBoundingClientRect();
      const mx = e.clientX - rect.left;
      const my = e.clientY - rect.top;
      const cx = canvas.width / 2;
      const cy = canvas.height / 2;
      const r = globeRadius;

      // Check city badge
      for (let i = 0; i < renderedCityBadges.length; i++) {{
        const b = renderedCityBadges[i];
        if (mx >= b.x && mx <= b.x + b.w && my >= b.y && my <= b.y + b.h) {{
          if (selectedCityFilter.toLowerCase() === b.name.toLowerCase()) {{
            clearAllFilters();
          }} else {{
            filterByCity(b.name);
          }}
          return;
        }}
      }}

      // Check dot
      for (let i = 0; i < visibleDots.length; i++) {{
        const d = visibleDots[i];
        if (Math.hypot(d.renderX - mx, d.renderY - my) < 9) {{
          selectInstitution(d.inst);
          return;
        }}
      }}

      // Check country centroid
      for (let i = 0; i < COUNTRY_CENTROIDS.length; i++) {{
        const c = COUNTRY_CENTROIDS[i];
        const pt = project(c.lon, c.lat, r, cx, cy);
        if (pt.front && Math.hypot(pt.x - mx, pt.y - my) < 22) {{
          if (selectedCountryFilter.toLowerCase() === c.name.toLowerCase()) {{
            clearAllFilters();
          }} else {{
            filterByCountry(c.name);
          }}
          return;
        }}
      }}

      // Check country polygon
      const geo = unproject(mx, my, r, cx, cy);
      if (geo) {{
        for (let i = 0; i < COUNTRY_POLYS.length; i++) {{
          const country = COUNTRY_POLYS[i];
          for (let j = 0; j < country.r.length; j++) {{
            if (pointInPolygon(geo.lon, geo.lat, country.r[j])) {{
              if (selectedCountryFilter.toLowerCase() === country.n.toLowerCase()) {{
                clearAllFilters();
              }} else {{
                filterByCountry(country.n);
              }}
              return;
            }}
          }}
        }}
      }}
    }}

    document.getElementById('floatingCard').addEventListener('click', () => {{
      if (selectedInstitution) openDossier(selectedInstitution);
    }});
    document.getElementById('closeDetailBtn').addEventListener('click', () => {{
      document.getElementById('detailDrawer').classList.add('hidden');
    }});

    // Wheel Zoom
    canvas.addEventListener('wheel', e => {{
      e.preventDefault();
      const factor = e.deltaY < 0 ? 1.07 : 0.93;
      targetRadius = Math.max(getMinRadius(), Math.min(getMaxRadius(), targetRadius * factor));
    }}, {{ passive: false }});

    document.getElementById('zoomInBtn').addEventListener('click', () => {{
      targetRadius = Math.min(getMaxRadius(), targetRadius * 1.32);
    }});
    document.getElementById('zoomOutBtn').addEventListener('click', () => {{
      targetRadius = Math.max(getMinRadius(), targetRadius * 0.76);
    }});
    document.getElementById('resetViewBtn').addEventListener('click', () => {{
      targetRadius = baseRadius;
      flyTo(-45, 35);
      clearAllFilters();
    }});
    document.getElementById('spinBtn').addEventListener('click', () => {{
      isAutoSpinning = !isAutoSpinning;
      document.getElementById('spinBtn').classList.toggle('text-[#3b82f6]', isAutoSpinning);
      document.getElementById('spinBtn').classList.toggle('text-[#94a3b8]', !isAutoSpinning);
    }});

    document.getElementById('openMomaAuditBtn').addEventListener('click', () => {{
      const moma = ALL_INSTITUTIONS.find(i => i.name.toLowerCase().includes('museum of modern art') || i.name.toLowerCase().includes('moma'));
      if (moma) {{
        selectInstitution(moma);
        openDossier(moma);
      }}
    }});

    // Initial render
    applyFilters();
    if (selectedInstitution) {{
      selectInstitution(selectedInstitution);
    }}
  </script>
</body>
</html>
"""

    dest_app = "/Users/polinavasilyeva/.gemini/antigravity/scratch/sponsor-atlas/app/index.html"
    with open(dest_app, "w", encoding="utf-8") as f:
        f.write(html)
    print("Wrote mobile-optimized app/index.html!")

    dest_artifact = "/Users/polinavasilyeva/.gemini/antigravity/brain/b997e616-4551-453e-83cc-4ba184f90abf/culture_atlas_app.html"
    with open(dest_artifact, "w", encoding="utf-8") as f:
        f.write(html)
    print("Mirrored to culture_atlas_app.html!")

if __name__ == "__main__":
    build()
