import json
import re

def build():
    print("Decoding topojson polygons...")
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

    # Exact palette matching reference screenshot
    # Greens: Canada, Greenland, Algeria, Libya, Sudan, Mongolia, Sweden, Norway, Finland, Chad, Niger, Mali, Mauritania, Egypt
    GREEN_SET = {'Canada', 'Greenland', 'Algeria', 'Libya', 'Sudan', 'Mongolia', 'Sweden', 'Norway', 'Finland', 'Chad', 'Niger', 'Mali', 'Mauritania', 'Egypt', 'Morocco', 'Namibia', 'Botswana', 'Zimbabwe', 'Zambia'}
    # Teals: Russia, India, China, Brazil, Australia, Angola, Dem. Rep. Congo, Congo, Indonesia, South Africa, Mozambique, Tanzania, Kenya, Ethiopia, Madagascar, Myanmar, Thailand, Vietnam
    TEAL_SET = {'Russia', 'India', 'China', 'Brazil', 'Australia', 'Angola', 'Dem. Rep. Congo', 'Congo', 'Indonesia', 'South Africa', 'Mozambique', 'Tanzania', 'Kenya', 'Ethiopia', 'Madagascar', 'Myanmar', 'Thailand', 'Vietnam'}
    # Blues: USA, Saudi Arabia, Iran, Kazakhstan, Mexico, Argentina, France, Spain, Germany, United Kingdom, Poland, Italy, Turkey, Ukraine, Uzbekistan, Turkmenistan, Pakistan, Afghanistan, Iraq, Syria, Jordan, Yemen, Oman
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
    print(f"Decoded {len(out_countries)} countries, size: {len(countries_json)} bytes")

    # Load institutions
    institutions_json = open('institutions.json', 'r', encoding='utf-8').read().strip()
    
    # Let's read the current app/index.html to extract any helper datasets or logic
    print("Building new app matching design reference...")

    # We will construct a complete, self-contained, standalone index.html
    # adhering 100% to the screenshot design reference!
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no" />
  <title>Culture Atlas</title>
  
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
      overflow-x: hidden;
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
    .toggle-switch {{
      position: relative;
      width: 32px;
      height: 18px;
      background: #282c38;
      border-radius: 9999px;
      transition: background 0.2s;
    }}
    .toggle-switch-handle {{
      position: absolute;
      top: 2px;
      left: 2px;
      width: 14px;
      height: 14px;
      background: #ffffff;
      border-radius: 9999px;
      transition: transform 0.2s;
    }}
    .toggle-switch.active .toggle-switch-handle {{
      transform: translateX(14px);
    }}
  </style>
</head>
<body class="bg-black text-slate-100 min-h-screen flex flex-col p-2 sm:p-4 select-none">

  <!-- MAIN GLOBE CARD CONTAINER (Matching Reference: rounded-2xl, border, dark black background) -->
  <div class="relative w-full max-w-[1240px] mx-auto bg-[#020408] border border-[#1c212a] rounded-2xl overflow-hidden flex flex-col shadow-2xl flex-1 min-h-[580px] sm:min-h-[660px]">

    <!-- TOP-LEFT SEARCH BAR -->
    <div class="absolute top-4 left-4 z-20 pointer-events-auto flex items-center gap-2">
      <div class="relative w-56 sm:w-72">
        <input 
          type="text" 
          id="searchInput" 
          placeholder="Search institutions and cities" 
          class="w-full bg-[#161922] bg-opacity-90 border border-[#282c38] text-xs text-white placeholder-[#6b7280] px-3.5 py-2 rounded-lg focus:outline-none focus:border-[#3b82f6] transition shadow-md"
        />
        <button id="clearSearchBtn" class="hidden absolute right-2.5 top-2 text-[#6b7280] hover:text-white text-xs">✕</button>
      </div>

      <!-- Quick Concierge MoMA Button -->
      <button id="openConciergeBtn" class="hidden sm:flex items-center gap-1.5 px-3 py-2 bg-[#161922] hover:bg-[#202533] border border-[#282c38] hover:border-[#3b82f6] text-xs text-[#94a3b8] hover:text-white rounded-lg transition shadow-md" title="Investigative Museum Research">
        <span>🔍</span>
        <span class="font-medium">MoMA Research</span>
      </button>
    </div>

    <!-- 3D GLOBE CANVAS (Centered, Clean Vector Cartography) -->
    <div id="canvasWrapper" class="flex-1 w-full h-full relative flex items-center justify-center min-h-[520px]">
      <canvas id="globeCanvas" width="960" height="720" class="max-w-full max-h-full"></canvas>

      <!-- FLOATING WHITE CARD (Matching Plug In ICA in Reference) -->
      <div id="floatingCard" class="absolute z-30 pointer-events-auto bg-white text-slate-900 rounded-lg px-3.5 py-2.5 shadow-2xl transition duration-150 transform -translate-x-1/2 -translate-y-full mb-3 cursor-pointer border border-slate-100 max-w-[240px]">
        <div class="flex items-center justify-between gap-2">
          <div id="floatingCardTitle" class="font-bold text-[13px] text-slate-950 leading-tight">Plug In ICA</div>
          <span id="floatingCardTier" class="text-[9px] font-semibold uppercase px-1.5 py-0.5 bg-emerald-100 text-emerald-800 rounded">Verified</span>
        </div>
        <div id="floatingCardMeta" class="text-[11px] text-slate-500 mt-0.5 flex items-center gap-1">
          <span>Winnipeg, Canada</span>
        </div>
        <!-- Little down arrow pointing to location -->
        <div class="absolute bottom-0 left-1/2 -translate-x-1/2 translate-y-full w-0 h-0 border-x-[6px] border-x-transparent border-t-[6px] border-t-white"></div>
      </div>
    </div>

    <!-- BOTTOM-LEFT BAR: CULTURE ATLAS + VIEW TOGGLE + SCALE BAR -->
    <div class="absolute bottom-4 left-4 z-20 pointer-events-auto flex flex-col gap-2">
      <div class="flex items-center gap-3">
        <span class="text-xs font-semibold tracking-wider text-[#cbd5e1] uppercase">CULTURE ATLAS</span>
        
        <!-- Segmented Toggle: GLOBE VIEW | CITY LIST -->
        <div id="viewToggle" class="flex items-center gap-2 bg-[#161821] border border-[#282c38] px-2.5 py-1 rounded-full text-[10px] cursor-pointer">
          <span id="labelGlobe" class="text-[#e2e8f0] font-medium tracking-wide">GLOBE VIEW</span>
          <div id="toggleSwitch" class="toggle-switch">
            <div class="toggle-switch-handle"></div>
          </div>
          <span id="labelCity" class="text-[#64748b] font-medium tracking-wide">CITY LIST</span>
        </div>
      </div>

      <!-- 2,000 km Scale Bar (Exact from reference) -->
      <div class="flex items-center gap-1.5 text-[10px] text-[#64748b] font-mono select-none">
        <div class="flex flex-col items-center">
          <div class="w-16 h-1 border-b border-l border-r border-[#64748b]"></div>
        </div>
        <span>2,000 km</span>
      </div>
    </div>

    <!-- BOTTOM-RIGHT FLOATING CONTROLS: [+], [-], [target], [spin] -->
    <div class="absolute bottom-4 right-4 z-20 pointer-events-auto flex flex-col gap-1.5">
      <button id="zoomInBtn" class="w-8 h-8 bg-[#161821] hover:bg-[#232838] border border-[#282c38] hover:border-[#3b82f6] text-[#94a3b8] hover:text-white rounded-lg flex items-center justify-center font-bold text-sm transition shadow-md" title="Zoom In">+</button>
      <button id="zoomOutBtn" class="w-8 h-8 bg-[#161821] hover:bg-[#232838] border border-[#282c38] hover:border-[#3b82f6] text-[#94a3b8] hover:text-white rounded-lg flex items-center justify-center font-bold text-sm transition shadow-md" title="Zoom Out">−</button>
      <button id="resetViewBtn" class="w-8 h-8 bg-[#161821] hover:bg-[#232838] border border-[#282c38] hover:border-[#3b82f6] text-[#94a3b8] hover:text-white rounded-lg flex items-center justify-center text-xs transition shadow-md" title="Recenter View">◎</button>
      <button id="spinBtn" class="w-8 h-8 bg-[#161821] hover:bg-[#232838] border border-[#282c38] hover:border-[#3b82f6] text-[#3b82f6] rounded-lg flex items-center justify-center text-xs transition shadow-md" title="Toggle Auto-Spin">↻</button>
    </div>

    <!-- CITY LIST OVERLAY (When user flips toggle switch) -->
    <div id="cityListModal" class="hidden absolute inset-0 z-40 bg-[#020408] bg-opacity-95 p-6 overflow-y-auto custom-scrollbar">
      <div class="max-w-4xl mx-auto space-y-4">
        <div class="flex items-center justify-between border-b border-[#1c212a] pb-3">
          <div>
            <h2 class="text-base font-bold text-white uppercase tracking-wider">Indexed Cultural Institutions</h2>
            <p class="text-xs text-[#64748b]">203 mapped organizations by municipal jurisdiction and funding architecture</p>
          </div>
          <button id="closeCityListBtn" class="text-xs bg-[#161821] border border-[#282c38] text-white px-3 py-1.5 rounded-lg hover:bg-[#222635]">Back to Globe</button>
        </div>
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2.5" id="cityListContainer">
          <!-- Populated dynamically -->
        </div>
      </div>
    </div>

    <!-- INVESTIGATIVE DOSSIER DRAWER (MoMA, Jeffrey Epstein, Leon Black, etc.) -->
    <div id="dossierDrawer" class="hidden absolute right-0 top-0 bottom-0 w-full sm:w-[380px] z-50 bg-[#0b0e14] border-l border-[#1c212a] p-5 flex flex-col shadow-2xl overflow-y-auto custom-scrollbar">
      <div class="flex items-center justify-between border-b border-[#1c212a] pb-3">
        <span class="text-[10px] font-mono uppercase text-[#3b82f6] tracking-wider font-semibold">Institutional Dossier</span>
        <button id="closeDossierBtn" class="text-[#64748b] hover:text-white text-xs px-2 py-1">✕</button>
      </div>
      <div id="dossierBody" class="mt-4 space-y-4 flex-1">
        <!-- Injected dynamically -->
      </div>
    </div>

  </div>

  <!-- BOTTOM FOOTER (Matching Reference: "Every institution on the globe (1)") -->
  <div class="max-w-[1240px] mx-auto w-full pt-3 px-1 flex items-center justify-between text-xs text-[#94a3b8]">
    <div class="flex items-center gap-2">
      <span>Every institution on the globe</span>
      <span id="footerCountBadge" class="inline-flex items-center justify-center w-5 h-5 rounded-full bg-[#10243e] text-[#60a5fa] text-[11px] font-semibold border border-[#1d4ed8]">1</span>
    </div>
    <div class="flex items-center gap-3 text-[11px] text-[#64748b]">
      <span>35 Countries</span>
      <span>·</span>
      <span>133 Cities</span>
      <span>·</span>
      <span class="text-emerald-400">126 Verified Tier A</span>
    </div>
  </div>

  <script>
    // -------------------------------------------------------------
    // DATASETS
    // -------------------------------------------------------------
    const ALL_INSTITUTIONS = {institutions_json};
    const COUNTRY_POLYS = {countries_json};

    // Country centroids for label placement (matching reference screenshot)
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
      {{ name: 'JAPAN', lon: 138.2, lat: 36.2 }},
      {{ name: 'BRAZIL', lon: -51.9, lat: -14.2 }},
      {{ name: 'AUSTRALIA', lon: 133.7, lat: -25.2 }}
    ];

    // Priority city list for badges (Exact cities from screenshot: MADRID, LONDON, STOCKHOLM, NEW YORK, CHICAGO, MARFA, LOS ANGELES, HONG KONG, TOKYO)
    const PRIORITY_CITIES = [
      {{ name: 'NEW YORK', lon: -74.006, lat: 40.7128, count: 11 }},
      {{ name: 'LONDON', lon: -0.1278, lat: 51.5074, count: 8 }},
      {{ name: 'MADRID', lon: -3.7038, lat: 40.4168, count: 3 }},
      {{ name: 'CHICAGO', lon: -87.6298, lat: 41.8781, count: 3 }},
      {{ name: 'MARFA', lon: -104.030, lat: 30.309, count: 3 }},
      {{ name: 'LOS ANGELES', lon: -118.2437, lat: 34.0522, count: 3 }},
      {{ name: 'STOCKHOLM', lon: 18.0686, lat: 59.3293, count: 2 }},
      {{ name: 'TOKYO', lon: 139.6917, lat: 35.6895, count: 3 }},
      {{ name: 'HONG KONG', lon: 114.1694, lat: 22.3193, count: 2 }},
      {{ name: 'PARIS', lon: 2.3522, lat: 48.8566, count: 4 }},
      {{ name: 'BERLIN', lon: 13.4050, lat: 52.5200, count: 4 }},
      {{ name: 'BASEL', lon: 7.5886, lat: 47.5596, count: 3 }},
      {{ name: 'AMSTERDAM', lon: 4.9041, lat: 52.3676, count: 2 }}
    ];

    // Find default institution (Plug In ICA)
    let selectedInstitution = ALL_INSTITUTIONS.find(i => i.name.toLowerCase().includes('plug in')) || ALL_INSTITUTIONS[0];
    let hoveredInstitution = null;

    // -------------------------------------------------------------
    // 3D CANVAS GLOBE CARTOGRAPHY
    // -------------------------------------------------------------
    const canvas = document.getElementById('globeCanvas');
    const ctx = canvas.getContext('2d');

    // Initial camera rotation matches the exact reference screenshot (looking from North-West angle)
    let rotLon = -45;
    let rotLat = 35;
    let targetRotLon = -45;
    let targetRotLat = 35;
    let isFlying = false;
    let flightProgress = 0;
    let isAutoSpinning = false;
    let isDragging = false;
    let lastX = 0, lastY = 0;
    let globeRadius = 260;
    let baseRadius = 260;
    let targetRadius = 260;

    const getMinRadius = () => Math.min(canvas.width, canvas.height) * 0.25;
    const getMaxRadius = () => Math.min(canvas.width, canvas.height) * 2.5;

    function resizeCanvas() {{
      const wrapper = document.getElementById('canvasWrapper');
      const w = wrapper.clientWidth;
      const h = wrapper.clientHeight;
      canvas.width = w;
      canvas.height = h;
      baseRadius = Math.min(w, h) * 0.44;
      if (!targetRadius || targetRadius === 260) {{
        targetRadius = baseRadius;
        globeRadius = baseRadius;
      }}
    }}
    window.addEventListener('resize', resizeCanvas);
    resizeCanvas();

    // Orthographic projection with horizon limb clamping
    function project(lon, lat, r, cx, cy) {{
      const rad = Math.PI / 180;
      const lam = (lon - rotLon) * rad;
      const phi = lat * rad;
      const phi0 = rotLat * rad;

      const cosC = Math.sin(phi0) * Math.sin(phi) + Math.cos(phi0) * Math.cos(phi) * Math.cos(lam);
      const x = r * Math.cos(phi) * Math.sin(lam);
      const y = -r * (Math.cos(phi0) * Math.sin(phi) - Math.sin(phi0) * Math.cos(phi) * Math.cos(lam));

      if (cosC >= 0) {{
        return {{ x: cx + x, y: cy + y, depth: cosC, front: true }};
      }} else {{
        const angle = Math.atan2(y, x);
        return {{ x: cx + r * Math.cos(angle), y: cy + r * Math.sin(angle), depth: cosC, front: false }};
      }}
    }}

    // Anti-collision occupancy manager
    const occupiedBoxes = [];
    function clearOccupancy() {{
      occupiedBoxes.length = 0;
    }}
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

    let visibleDots = [];

    function render() {{
      const w = canvas.width;
      const h = canvas.height;
      const cx = w / 2;
      const cy = h / 2;

      // Smooth zoom transition
      globeRadius += (targetRadius - globeRadius) * 0.15;
      const r = globeRadius;

      ctx.clearRect(0, 0, w, h);
      clearOccupancy();

      // Camera flight interpolation
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

      // 1. OCEAN SPHERE: Deep midnight navy blue (#020d20 to #041630)
      ctx.fillStyle = '#030f24';
      ctx.beginPath();
      ctx.arc(cx, cy, r, 0, Math.PI * 2);
      ctx.fill();

      // Clip inside globe disc
      ctx.save();
      ctx.beginPath();
      ctx.arc(cx, cy, r, 0, Math.PI * 2);
      ctx.clip();

      // 2. LATITUDE & LONGITUDE GRATICULES (Electric Blue Grid lines)
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
          }} else {{
            first = true;
          }}
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
          }} else {{
            first = true;
          }}
        }}
        ctx.stroke();
      }}

      // 3. FILLED COUNTRY POLYGONS (Forest Green, Teal, Cobalt Blue Mosaic from Reference)
      COUNTRY_POLYS.forEach(country => {{
        ctx.fillStyle = country.c;
        ctx.beginPath();
        let anyVisible = false;

        country.r.forEach(ring => {{
          let anyFrontInRing = false;
          for (let i = 0; i < ring.length; i++) {{
            const pt = project(ring[i][0], ring[i][1], r, cx, cy);
            if (pt.front) {{
              anyFrontInRing = true;
              break;
            }}
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
          ctx.strokeStyle = '#020b18'; // Dark separation lines
          ctx.lineWidth = 0.65;
          ctx.stroke();
        }}
      }});

      // 4. COUNTRY CENTROID LABELS (Sage green / slate uppercase: ALGERIA, CANADA, etc.)
      ctx.font = '600 9.5px "Inter", sans-serif';
      COUNTRY_CENTROIDS.forEach(c => {{
        const pt = project(c.lon, c.lat, r, cx, cy);
        if (pt.front && pt.depth > 0.28) {{
          const tw = ctx.measureText(c.name).width;
          const box = {{ x: pt.x - tw / 2, y: pt.y - 5.5, w: tw, h: 11 }};

          if (!isColliding(box, 3)) {{
            ctx.fillStyle = '#5c8477'; // Muted sage green from reference
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillText(c.name, pt.x, pt.y);
            registerBox(box.x, box.y, box.w, box.h, 3);
          }}
        }}
      }});

      // 5. CITY PILL BADGES (Matching Reference: ■ MADRID, ■ LONDON, ■ NEW YORK, etc.)
      PRIORITY_CITIES.forEach(cty => {{
        const pt = project(cty.lon, cty.lat, r, cx, cy);
        if (pt.front && pt.depth > 0.3) {{
          ctx.font = '600 9.5px "Inter", sans-serif';
          const tw = ctx.measureText(cty.name).width;
          const badgeW = tw + 18;
          const badgeH = 17;
          const bx = pt.x - 2;
          const by = pt.y - badgeH / 2;

          const box = {{ x: bx, y: by, w: badgeW, h: badgeH }};
          if (!isColliding(box, 2)) {{
            // Dark navy semi-transparent pill container
            ctx.fillStyle = 'rgba(9, 14, 24, 0.92)';
            ctx.beginPath();
            roundRect(ctx, bx, by, badgeW, badgeH, 4);
            ctx.fill();

            // Subtle blue border
            ctx.strokeStyle = 'rgba(59, 130, 246, 0.45)';
            ctx.lineWidth = 1;
            ctx.stroke();

            // White square pip (■)
            ctx.fillStyle = '#ffffff';
            ctx.fillRect(bx + 4.5, by + 6, 3, 3);

            // City name in white
            ctx.fillStyle = '#ffffff';
            ctx.textAlign = 'left';
            ctx.textBaseline = 'middle';
            ctx.fillText(cty.name, bx + 12, by + badgeH / 2 + 0.5);

            registerBox(box.x, box.y, box.w, box.h, 2);
          }}
        }}
      }});

      ctx.restore();

      // 6. CRISP ELECTRIC COBALT BLUE GLOBE PERIMETER RING (#1d4ed8, 1.5px)
      ctx.strokeStyle = '#1d4ed8';
      ctx.lineWidth = 1.5;
      ctx.beginPath();
      ctx.arc(cx, cy, r, 0, Math.PI * 2);
      ctx.stroke();

      // 7. INSTITUTION DOTS (Spiderfy dispersal on close zoom so they NEVER overlap)
      visibleDots = [];
      ALL_INSTITUTIONS.forEach(inst => {{
        const pt = project(inst.lon, inst.lat, r, cx, cy);
        if (pt.front && pt.depth > 0.1) {{
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

      // Cluster detection & radial spiderfy
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

      // Draw Dots
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

      // 8. UPDATE FLOATING WHITE CARD POSITION (Pinned to selected institution)
      const floatingCard = document.getElementById('floatingCard');
      if (selectedInstitution) {{
        const pt = project(selectedInstitution.lon, selectedInstitution.lat, r, cx, cy);
        if (pt.front && pt.depth > 0.05) {{
          floatingCard.classList.remove('hidden');
          floatingCard.style.left = `${{pt.x}}px`;
          floatingCard.style.top = `${{pt.y}}px`;

          // Also draw plain white text next to location (as shown in reference: "Plug In ICA")
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
      document.getElementById('floatingCardTitle').textContent = inst.name;
      document.getElementById('floatingCardMeta').textContent = `${{inst.location}} · ${{inst.tier === 'A' ? 'Verified' : 'One Name'}}`;
      document.getElementById('floatingCardTier').textContent = inst.tier === 'A' ? 'Verified' : inst.tier === 'B' ? 'One Name' : 'Unverified';
      document.getElementById('footerCountBadge').textContent = '1';
      flyTo(inst.lon, inst.lat);
    }}

    function openDossier(inst) {{
      const drawer = document.getElementById('dossierDrawer');
      const body = document.getElementById('dossierBody');
      drawer.classList.remove('hidden');

      body.innerHTML = `
        <div>
          <h2 class="text-lg font-bold text-white leading-snug">${{inst.name}}</h2>
          <p class="text-xs text-[#3b82f6] mt-0.5 font-mono">${{inst.location}} · ${{inst.size === 'L' ? 'Large (>$20M)' : 'Small/Mid'}}</p>
        </div>
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

    // POINTER & TOUCH INTERACTIONS
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
        let hit = null;
        for (let i = 0; i < visibleDots.length; i++) {{
          const d = visibleDots[i];
          if (Math.hypot(d.renderX - mx, d.renderY - my) < 9) {{
            hit = d.inst;
            break;
          }}
        }}
        hoveredInstitution = hit;
        canvas.style.cursor = hit ? 'pointer' : 'grab';
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

    document.getElementById('floatingCard').addEventListener('click', () => {{
      if (selectedInstitution) openDossier(selectedInstitution);
    }});

    // WHEEL & BUTTON ZOOM CONTROLS
    canvas.addEventListener('wheel', e => {{
      e.preventDefault();
      const factor = e.deltaY < 0 ? 1.14 : 0.88;
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
    }});
    document.getElementById('spinBtn').addEventListener('click', () => {{
      isAutoSpinning = !isAutoSpinning;
      document.getElementById('spinBtn').classList.toggle('text-[#3b82f6]', isAutoSpinning);
      document.getElementById('spinBtn').classList.toggle('text-[#94a3b8]', !isAutoSpinning);
    }});

    // SEARCH INPUT
    const searchInput = document.getElementById('searchInput');
    const clearSearchBtn = document.getElementById('clearSearchBtn');

    searchInput.addEventListener('input', e => {{
      const q = e.target.value.toLowerCase().trim();
      clearSearchBtn.classList.toggle('hidden', q === '');
      if (!q) return;

      const found = ALL_INSTITUTIONS.find(i => 
        i.name.toLowerCase().includes(q) || 
        i.location.toLowerCase().includes(q) || 
        i.city.toLowerCase().includes(q)
      );
      if (found) {{
        selectInstitution(found);
      }}
    }});

    clearSearchBtn.addEventListener('click', () => {{
      searchInput.value = '';
      clearSearchBtn.classList.add('hidden');
    }});

    // VIEW TOGGLE (GLOBE VIEW / CITY LIST)
    const viewToggle = document.getElementById('viewToggle');
    const toggleSwitch = document.getElementById('toggleSwitch');
    const cityListModal = document.getElementById('cityListModal');
    const labelGlobe = document.getElementById('labelGlobe');
    const labelCity = document.getElementById('labelCity');

    let isCityListView = false;
    viewToggle.addEventListener('click', () => {{
      isCityListView = !isCityListView;
      toggleSwitch.classList.toggle('active', isCityListView);
      cityListModal.classList.toggle('hidden', !isCityListView);
      labelGlobe.className = isCityListView ? 'text-[#64748b] font-medium tracking-wide' : 'text-[#e2e8f0] font-medium tracking-wide';
      labelCity.className = isCityListView ? 'text-[#e2e8f0] font-medium tracking-wide' : 'text-[#64748b] font-medium tracking-wide';
      if (isCityListView) populateCityList();
    }});

    document.getElementById('closeCityListBtn').addEventListener('click', () => {{
      viewToggle.click();
    }});

    function populateCityList() {{
      const container = document.getElementById('cityListContainer');
      const citiesMap = {{}};
      ALL_INSTITUTIONS.forEach(i => {{
        if (!citiesMap[i.city]) citiesMap[i.city] = [];
        citiesMap[i.city].push(i);
      }});

      const sorted = Object.keys(citiesMap).sort();
      container.innerHTML = sorted.map(city => `
        <div class="bg-[#12151f] border border-[#202535] p-3 rounded-lg hover:border-[#3b82f6] transition cursor-pointer" onclick="handleCityClick('${{city.replace(/'/g, "\\\\\\'")}}')">
          <div class="flex items-center justify-between">
            <h4 class="font-semibold text-white text-xs">${{city}}</h4>
            <span class="text-[10px] text-[#3b82f6] font-mono">${{citiesMap[city].length}} inst.</span>
          </div>
          <div class="mt-1.5 space-y-1">
            ${{citiesMap[city].slice(0, 3).map(inst => `
              <div class="text-[11px] text-[#94a3b8] truncate">• ${{inst.name}}</div>
            `).join('')}}
          </div>
        </div>
      `).join('');
    }}

    window.handleCityClick = function(cityName) {{
      const inst = ALL_INSTITUTIONS.find(i => i.city.toLowerCase() === cityName.toLowerCase());
      if (inst) {{
        viewToggle.click();
        selectInstitution(inst);
      }}
    }};

    // DOSSIER CLOSING
    document.getElementById('closeDossierBtn').addEventListener('click', () => {{
      document.getElementById('dossierDrawer').classList.add('hidden');
    }});

    // QUICK CONCIERGE BUTTON FOR MOMA
    document.getElementById('openConciergeBtn').addEventListener('click', () => {{
      const moma = ALL_INSTITUTIONS.find(i => i.name.toLowerCase().includes('museum of modern art') || i.name.toLowerCase().includes('moma'));
      if (moma) {{
        selectInstitution(moma);
        openDossier(moma);
      }}
    }});

    // Initial state: select Plug In ICA as in reference
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
    print("Wrote updated app/index.html")

    dest_artifact = "/Users/polinavasilyeva/.gemini/antigravity/brain/b997e616-4551-453e-83cc-4ba184f90abf/culture_atlas_app.html"
    with open(dest_artifact, "w", encoding="utf-8") as f:
        f.write(html)
    print("Mirrored to culture_atlas_app.html")

    # Now let's build the inline widget concierge_widget.html matching this exact design
    build_widget_matching_ref(institutions_json, countries_json)

def build_widget_matching_ref(institutions_json, countries_json):
    widget_html = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  <script src="https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js"></script>
  <style>
    body {{
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      background-color: transparent;
      color: #f8fafc;
    }}
    #widgetGlobeCanvas {{
      cursor: grab;
      touch-action: none;
    }}
    #widgetGlobeCanvas.dragging {{
      cursor: grabbing;
    }}
  </style>
</head>
<body class="p-2 antialiased">
  <div class="bg-[#020408] text-white border border-[#1c212a] rounded-2xl p-3 shadow-2xl overflow-hidden flex flex-col gap-2.5 max-h-[540px]">
    
    <!-- Header matching reference -->
    <div class="flex items-center justify-between border-b border-[#1c212a] pb-2 px-1">
      <div class="flex items-center gap-2">
        <div class="w-2.5 h-2.5 rounded-full bg-[#1d4ed8]"></div>
        <span class="text-xs font-semibold tracking-wider text-[#cbd5e1] uppercase">CULTURE ATLAS</span>
      </div>
      <div class="flex items-center gap-2 text-[11px] text-[#64748b]">
        <input id="widgetSearch" type="text" placeholder="Search..." class="bg-[#161922] border border-[#282c38] px-2 py-0.5 text-xs text-white rounded focus:outline-none w-32" />
        <span class="text-[#3b82f6]">Plug In ICA · Canada</span>
      </div>
    </div>

    <!-- 2-Column Interface: Globe on Left, Research / Dossier on Right -->
    <div class="grid grid-cols-1 sm:grid-cols-12 gap-2.5 flex-1 min-h-[380px] overflow-hidden">
      <!-- 3D Globe Visualizer -->
      <div class="sm:col-span-7 relative flex items-center justify-center bg-[#000000] rounded-xl border border-[#1c212a] overflow-hidden min-h-[340px]">
        <canvas id="widgetGlobeCanvas" width="500" height="420" class="max-w-full max-h-full"></canvas>

        <!-- Floating White Card (Plug In ICA) -->
        <div id="widgetCard" class="absolute z-30 pointer-events-auto bg-white text-slate-900 rounded-lg px-2.5 py-1.5 shadow-xl transition transform -translate-x-1/2 -translate-y-full mb-2 cursor-pointer border border-slate-100 max-w-[190px]">
          <div class="font-bold text-[11px] text-slate-950 leading-tight" id="widgetCardTitle">Plug In ICA</div>
          <div class="text-[9.5px] text-slate-500 mt-0.5" id="widgetCardMeta">Winnipeg, Canada · Verified</div>
          <div class="absolute bottom-0 left-1/2 -translate-x-1/2 translate-y-full w-0 h-0 border-x-[5px] border-x-transparent border-t-[5px] border-t-white"></div>
        </div>

        <!-- Scale bar -->
        <div class="absolute bottom-2 left-2 text-[9px] text-[#64748b] font-mono pointer-events-none">
          <span>└───┘ 2,000 km</span>
        </div>
      </div>

      <!-- Research Concierge / Dossier Panel -->
      <div class="sm:col-span-5 flex flex-col bg-[#0b0e14] border border-[#1c212a] rounded-xl p-3 overflow-hidden">
        <div class="flex items-center justify-between border-b border-[#1c212a] pb-1.5 mb-2">
          <span class="text-[10px] font-semibold uppercase tracking-wider text-[#3b82f6]">Research Dossier</span>
          <span class="text-[9px] px-1.5 py-0.5 bg-emerald-950 text-emerald-400 border border-emerald-800 rounded">Verified</span>
        </div>

        <div id="widgetDossier" class="flex-1 overflow-y-auto space-y-2.5 text-xs pr-1">
          <div>
            <h3 class="font-bold text-white text-sm" id="dossierName">Plug In ICA</h3>
            <p class="text-[11px] text-[#3b82f6] font-mono" id="dossierLoc">Winnipeg, Canada · Small/Mid</p>
          </div>
          <div class="bg-[#121622] p-2.5 rounded-lg border border-[#202535]">
            <span class="text-[9px] font-semibold text-emerald-400 uppercase tracking-wider block mb-0.5">Funding Architecture</span>
            <p class="text-[11px] text-slate-300 leading-relaxed" id="dossierFunding">CAD 1.2M annual budget, free admission. Canada Council for the Arts, Manitoba Arts Council, Winnipeg Arts Council, and foundation grants.</p>
          </div>
          <div class="bg-[#121622] p-2.5 rounded-lg border border-[#202535]">
            <span class="text-[9px] font-semibold text-blue-400 uppercase tracking-wider block mb-0.5">Watch & Governance</span>
            <p class="text-[11px] text-slate-300 leading-relaxed" id="dossierWatch">First non-profit Institute of Contemporary Art in Canada. Deep public benefit commitment with free admission; no corporate defense or fossil fuel underwriting on its roster.</p>
          </div>
          <div class="pt-2 border-t border-[#1c212a]">
            <span class="text-[9.5px] font-semibold text-slate-400 uppercase tracking-wider block mb-1">MoMA & Excluded Museums Research:</span>
            <div class="flex flex-wrap gap-1">
              <button class="moma-chip px-2 py-0.5 bg-[#161922] hover:bg-[#202533] border border-[#282c38] text-[10px] text-slate-300 rounded" data-target="moma">MoMA Audit</button>
              <button class="moma-chip px-2 py-0.5 bg-[#161922] hover:bg-[#202533] border border-[#282c38] text-[10px] text-slate-300 rounded" data-target="guggenheim">Guggenheim</button>
              <button class="moma-chip px-2 py-0.5 bg-[#161922] hover:bg-[#202533] border border-[#282c38] text-[10px] text-slate-300 rounded" data-target="sackler">Sackler/Met</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <script>
    const DATA = {institutions_json};
    const COUNTRY_POLYS = {countries_json};

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
      {{ name: 'UNITED STATES', lon: -98.5, lat: 39.5 }}
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
      {{ name: 'HONG KONG', lon: 114.1694, lat: 22.3193 }}
    ];

    const canvas = document.getElementById('widgetGlobeCanvas');
    const ctx = canvas.getContext('2d');
    let rotLon = -45;
    let rotLat = 35;
    let targetRotLon = -45;
    let targetRotLat = 35;
    let isFlying = false;
    let flightProgress = 0;
    let isDragging = false;
    let lastX = 0, lastY = 0;
    let globeRadius = 145;

    let selectedInst = DATA.find(i => i.name.toLowerCase().includes('plug in')) || DATA[0];

    function project(lon, lat, r, cx, cy) {{
      const rad = Math.PI / 180;
      const lam = (lon - rotLon) * rad;
      const phi = lat * rad;
      const phi0 = rotLat * rad;

      const cosC = Math.sin(phi0) * Math.sin(phi) + Math.cos(phi0) * Math.cos(phi) * Math.cos(lam);
      const x = r * Math.cos(phi) * Math.sin(lam);
      const y = -r * (Math.cos(phi0) * Math.sin(phi) - Math.sin(phi0) * Math.cos(phi) * Math.cos(lam));

      if (cosC >= 0) {{
        return {{ x: cx + x, y: cy + y, depth: cosC, front: true }};
      }} else {{
        const angle = Math.atan2(y, x);
        return {{ x: cx + r * Math.cos(angle), y: cy + r * Math.sin(angle), depth: cosC, front: false }};
      }}
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
      }}

      // Ocean
      ctx.fillStyle = '#030f24';
      ctx.beginPath();
      ctx.arc(cx, cy, r, 0, Math.PI * 2);
      ctx.fill();

      // Clip inside globe
      ctx.save();
      ctx.beginPath();
      ctx.arc(cx, cy, r, 0, Math.PI * 2);
      ctx.clip();

      // Graticules
      ctx.strokeStyle = 'rgba(29, 78, 216, 0.22)';
      ctx.lineWidth = 0.5;
      [-45, 0, 45, 70].forEach(lat => {{
        ctx.beginPath();
        let first = true;
        for (let lon = -180; lon <= 180; lon += 8) {{
          const pt = project(lon, lat, r, cx, cy);
          if (pt.front) {{
            if (first) {{ ctx.moveTo(pt.x, pt.y); first = false; }}
            else {{ ctx.lineTo(pt.x, pt.y); }}
          }} else {{ first = true; }}
        }}
        ctx.stroke();
      }});

      // Country Polygons
      COUNTRY_POLYS.forEach(country => {{
        ctx.fillStyle = country.c;
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
          ctx.strokeStyle = '#020b18';
          ctx.lineWidth = 0.5;
          ctx.stroke();
        }}
      }});

      // Country Centroids
      ctx.font = '600 8.5px "Inter", sans-serif';
      COUNTRY_CENTROIDS.forEach(c => {{
        const pt = project(c.lon, c.lat, r, cx, cy);
        if (pt.front && pt.depth > 0.3) {{
          ctx.fillStyle = '#5c8477';
          ctx.textAlign = 'center';
          ctx.textBaseline = 'middle';
          ctx.fillText(c.name, pt.x, pt.y);
        }}
      }});

      // City Badges (■ CITY)
      PRIORITY_CITIES.forEach(cty => {{
        const pt = project(cty.lon, cty.lat, r, cx, cy);
        if (pt.front && pt.depth > 0.35) {{
          ctx.font = '600 8px "Inter", sans-serif';
          const tw = ctx.measureText(cty.name).width;
          const badgeW = tw + 15;
          const badgeH = 14;
          const bx = pt.x - 2;
          const by = pt.y - badgeH / 2;

          ctx.fillStyle = 'rgba(9, 14, 24, 0.9)';
          roundRect(ctx, bx, by, badgeW, badgeH, 3);
          ctx.fill();

          ctx.strokeStyle = 'rgba(59, 130, 246, 0.45)';
          ctx.lineWidth = 0.8;
          ctx.stroke();

          ctx.fillStyle = '#ffffff';
          ctx.fillRect(bx + 3.5, by + 5, 2.5, 2.5);

          ctx.fillStyle = '#ffffff';
          ctx.textAlign = 'left';
          ctx.textBaseline = 'middle';
          ctx.fillText(cty.name, bx + 9.5, by + badgeH / 2 + 0.5);
        }}
      }});

      ctx.restore();

      // Blue Rim
      ctx.strokeStyle = '#1d4ed8';
      ctx.lineWidth = 1.2;
      ctx.beginPath();
      ctx.arc(cx, cy, r, 0, Math.PI * 2);
      ctx.stroke();

      // Institution Dots
      DATA.forEach(inst => {{
        const pt = project(inst.lon, inst.lat, r, cx, cy);
        if (pt.front && pt.depth > 0.1) {{
          const isSel = selectedInst && selectedInst.name === inst.name;
          if (isSel) {{
            ctx.beginPath();
            ctx.arc(pt.x, pt.y, 6, 0, Math.PI * 2);
            ctx.strokeStyle = '#ffffff';
            ctx.lineWidth = 1.2;
            ctx.stroke();
          }}
          ctx.beginPath();
          ctx.arc(pt.x, pt.y, isSel ? 3.8 : 2, 0, Math.PI * 2);
          ctx.fillStyle = inst.tier === 'A' ? '#10b981' : inst.tier === 'B' ? '#3b82f6' : '#94a3b8';
          ctx.fill();
        }}
      }});

      // Update Card Position
      const card = document.getElementById('widgetCard');
      if (selectedInst) {{
        const pt = project(selectedInst.lon, selectedInst.lat, r, cx, cy);
        if (pt.front && pt.depth > 0.05) {{
          card.classList.remove('hidden');
          card.style.left = `${{pt.x}}px`;
          card.style.top = `${{pt.y}}px`;

          ctx.font = '500 11px "Inter", sans-serif';
          ctx.fillStyle = '#ffffff';
          ctx.textAlign = 'left';
          ctx.textBaseline = 'middle';
          ctx.fillText(selectedInst.name, pt.x + 10, pt.y);
        }} else {{
          card.classList.add('hidden');
        }}
      }}

      requestAnimationFrame(render);
    }}
    requestAnimationFrame(render);

    // Pointer events
    canvas.addEventListener('pointerdown', e => {{
      isDragging = true;
      canvas.classList.add('dragging');
      lastX = e.clientX;
      lastY = e.clientY;
      isFlying = false;
    }});

    window.addEventListener('pointermove', e => {{
      if (isDragging) {{
        const dx = e.clientX - lastX;
        const dy = e.clientY - lastY;
        lastX = e.clientX;
        lastY = e.clientY;
        rotLon = (rotLon - dx * 0.6) % 360;
        rotLat = Math.max(-75, Math.min(75, rotLat + dy * 0.6));
      }}
    }});

    window.addEventListener('pointerup', () => {{
      isDragging = false;
      canvas.classList.remove('dragging');
    }});

    // Chips
    document.querySelectorAll('.moma-chip').forEach(btn => {{
      btn.addEventListener('click', () => {{
        const t = btn.getAttribute('data-target');
        if (t === 'moma') {{
          document.getElementById('dossierName').textContent = 'Museum of Modern Art (MoMA)';
          document.getElementById('dossierLoc').textContent = 'New York, USA · Flagship';
          document.getElementById('dossierFunding').textContent = '$1.1B endowment, $65M gate revenue. High corporate underwriting concentration (Steven Tananbaum, Larry Fink / BlackRock).';
          document.getElementById('dossierWatch').textContent = 'Scrutinized by Strike MoMA movement; former board chair Leon Black stepped down after paying $158M to Jeffrey Epstein.';
        }} else if (t === 'guggenheim') {{
          document.getElementById('dossierName').textContent = 'Solomon R. Guggenheim Museum';
          document.getElementById('dossierLoc').textContent = 'New York, USA · Flagship';
          document.getElementById('dossierFunding').textContent = '$130M endowment. Trustee conflict-of-interest scrutiny (Nancy Spector / Chauncey Hare audit).';
          document.getElementById('dossierWatch').textContent = 'Under scrutiny for labor union negotiations (Local 30 IUOE) and board accountability audits.';
        }} else if (t === 'sackler') {{
          document.getElementById('dossierName').textContent = 'The Sackler Wing (The Met)';
          document.getElementById('dossierLoc').textContent = 'New York, USA · De-accessioned Name';
          document.getElementById('dossierFunding').textContent = 'Purdue Pharma / OxyContin philanthropic funding removed after Nan Goldin / P.A.I.N. protests.';
          document.getElementById('dossierWatch').textContent = 'Metropolitan Museum of Art officially stripped the Sackler family name from seven exhibition spaces in December 2021.';
        }}
      }});
    }});
  </script>
</body>
</html>
"""
    dest_widget = "/Users/polinavasilyeva/.gemini/antigravity/brain/b997e616-4551-453e-83cc-4ba184f90abf/concierge_widget.html"
    with open(dest_widget, "w", encoding="utf-8") as f:
        f.write(widget_html)
    print("Wrote updated concierge_widget.html")

if __name__ == "__main__":
    build()
