import json

def update_widget():
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

    widget_html = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover" />
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  <script src="https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js"></script>
  <style>
    body {{
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      background-color: transparent;
      color: #f8fafc;
      overflow: hidden;
    }}
    #widgetCanvas {{
      cursor: grab;
      touch-action: none;
    }}
    #widgetCanvas.dragging {{
      cursor: grabbing;
    }}
    .custom-scroll::-webkit-scrollbar {{
      width: 3px;
    }}
    .custom-scroll::-webkit-scrollbar-thumb {{
      background: #232838;
      border-radius: 3px;
    }}
    .widget-item.active {{
      border-color: #3b82f6 !important;
      background-color: #101626 !important;
    }}
  </style>
</head>
<body class="p-1 sm:p-2 antialiased">
  <div class="bg-[#020408] text-white border border-[#1c212a] rounded-2xl p-2 sm:p-2.5 shadow-2xl overflow-hidden flex flex-col gap-2 max-h-[550px]">
    
    <!-- Header with Mobile View Switcher & Active Filter Pill -->
    <div class="flex items-center justify-between border-b border-[#1c212a] pb-2 px-1">
      <div class="flex items-center gap-2">
        <div class="w-2.5 h-2.5 rounded-full bg-[#1d4ed8]"></div>
        <span class="text-xs font-bold tracking-wider text-[#cbd5e1] uppercase">CULTURE ATLAS</span>
      </div>

      <!-- Mobile Tab Switcher: Globe / List -->
      <div class="flex sm:hidden items-center bg-[#101420] border border-[#232a3c] rounded-full p-0.5 text-[10px] font-mono">
        <button id="wTabGlobe" class="px-2 py-0.5 rounded-full bg-[#1d4ed8] text-white">Globe</button>
        <button id="wTabList" class="px-2 py-0.5 rounded-full text-[#94a3b8]">List (<span id="wListCount">203</span>)</button>
      </div>

      <div id="wFilterBadge" class="hidden sm:flex text-[11px] font-mono text-[#3b82f6] bg-[#0c1424] border border-[#1d4ed8] px-2 py-0.5 rounded items-center gap-1.5">
        <span id="wFilterText">All Institutions (203)</span>
        <button id="wClearFilter" class="hidden text-[#94a3b8] hover:text-white">✕</button>
      </div>
    </div>

    <!-- Active Filter Mobile Banner -->
    <div id="wMobileFilterBanner" class="hidden flex items-center justify-between bg-[#0e1628] border border-[#1d4ed8] px-2 py-1 rounded text-xs">
      <span id="wMobileFilterText" class="font-semibold text-white truncate">📍 NEW YORK (11)</span>
      <button id="wMobileClearFilter" class="text-[11px] text-[#94a3b8] hover:text-white">✕ Clear</button>
    </div>

    <!-- 2-Panel Layout (Tabs on Mobile, Side-by-Side on Desktop) -->
    <div class="grid grid-cols-1 sm:grid-cols-12 gap-2 flex-1 min-h-[420px] overflow-hidden">
      
      <!-- LEFT LIST (Filtered when clicking city or country) -->
      <div id="wListPanel" class="hidden sm:flex sm:col-span-5 flex-col bg-[#07090e] border border-[#1c212a] rounded-xl p-2 overflow-hidden h-full">
        <div class="flex items-center gap-1 mb-2">
          <input id="wSearch" type="text" placeholder="Filter list or search..." class="w-full bg-[#121622] border border-[#202535] text-[11px] text-white px-2 py-1 rounded focus:outline-none focus:border-[#3b82f6]" />
        </div>
        <div id="wListContainer" class="flex-1 overflow-y-auto custom-scroll space-y-1.5 pr-0.5">
          <!-- Items injected dynamically -->
        </div>
      </div>

      <!-- RIGHT 3D GLOBE (Interactive: Click City Badge or Country) -->
      <div id="wGlobePanel" class="col-span-1 sm:col-span-7 relative flex items-center justify-center bg-[#000000] rounded-xl border border-[#1c212a] overflow-hidden min-h-[360px] h-full">
        <canvas id="widgetCanvas" width="520" height="420" class="w-full h-full object-contain"></canvas>

        <!-- Floating White Card -->
        <div id="wCard" class="absolute z-30 pointer-events-auto bg-white text-slate-900 rounded-lg px-2.5 py-1.5 shadow-xl transition transform -translate-x-1/2 -translate-y-full mb-2 cursor-pointer border border-slate-100 max-w-[200px]">
          <div class="font-bold text-[11px] text-slate-950 leading-tight truncate" id="wCardTitle">Plug In ICA</div>
          <div class="text-[9.5px] text-slate-500 mt-0.5 truncate" id="wCardMeta">Winnipeg, Canada · Verified</div>
          <div class="mt-1 pt-1 border-t border-slate-100 flex items-center justify-between text-[9.5px]">
            <a id="wCardLink" href="https://plugin.org" target="_blank" rel="noopener noreferrer" 
               class="text-[#1d4ed8] hover:underline flex items-center gap-1 font-medium" onclick="event.stopPropagation()">
              <span>🌐</span> <span id="wCardDom">plugin.org</span> <span>↗</span>
            </a>
            <span class="text-[9px] text-slate-400 font-mono">Dossier →</span>
          </div>
          <div class="absolute bottom-0 left-1/2 -translate-x-1/2 translate-y-full w-0 h-0 border-x-[5px] border-x-transparent border-t-[5px] border-t-white"></div>
        </div>

        <div class="absolute bottom-2 left-2 text-[9px] text-[#64748b] font-mono pointer-events-none">
          <span>└───┘ 2,000 km</span>
        </div>

        <!-- Touch Hint on Mobile -->
        <div class="sm:hidden absolute top-2 right-2 text-[9px] text-[#64748b] font-mono pointer-events-none bg-[#090d18]/80 px-1.5 py-0.5 rounded border border-[#1e2434]">
          Tap city badge to filter
        </div>
      </div>

    </div>
  </div>

  <script>
    const DATA = {institutions_json};
    const COUNTRY_POLYS = {countries_json};

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

    const NORM = {{ 'united states': 'usa', 'united kingdom': 'uk', 'usa': 'usa', 'uk': 'uk' }};
    function matchC(a, b) {{
      if (!a || !b) return false;
      const s1 = a.toLowerCase().trim();
      const s2 = b.toLowerCase().trim();
      const n1 = NORM[s1] || s1;
      const n2 = NORM[s2] || s2;
      return n1 === n2 || s1.includes(s2) || s2.includes(s1);
    }}

    let filterCity = 'all';
    let filterCountry = 'all';
    let searchQ = '';
    let filtered = DATA.slice();
    let selectedInst = DATA.find(i => i.name.toLowerCase().includes('plug in')) || DATA[0];

    // Mobile tabs
    const wTabGlobe = document.getElementById('wTabGlobe');
    const wTabList = document.getElementById('wTabList');
    const wListPanel = document.getElementById('wListPanel');
    const wGlobePanel = document.getElementById('wGlobePanel');

    wTabGlobe.addEventListener('click', () => {{
      wTabGlobe.className = 'px-2 py-0.5 rounded-full bg-[#1d4ed8] text-white';
      wTabList.className = 'px-2 py-0.5 rounded-full text-[#94a3b8]';
      wListPanel.classList.add('hidden');
      wListPanel.classList.remove('flex');
      wGlobePanel.classList.remove('hidden');
    }});

    wTabList.addEventListener('click', () => {{
      wTabList.className = 'px-2 py-0.5 rounded-full bg-[#1d4ed8] text-white';
      wTabGlobe.className = 'px-2 py-0.5 rounded-full text-[#94a3b8]';
      wGlobePanel.classList.add('hidden');
      wListPanel.classList.remove('hidden');
      wListPanel.classList.add('flex');
    }});

    function applyWFilters() {{
      filtered = DATA.filter(inst => {{
        if (filterCity !== 'all' && inst.city.toLowerCase() !== filterCity.toLowerCase()) return false;
        if (filterCountry !== 'all' && !matchC(inst.country, filterCountry)) return false;
        if (searchQ) {{
          const q = searchQ.toLowerCase();
          if (!inst.name.toLowerCase().includes(q) && !inst.location.toLowerCase().includes(q)) return false;
        }}
        return true;
      }});

      document.getElementById('wListCount').textContent = `${{filtered.length}}`;
      const badge = document.getElementById('wFilterText');
      const clearBtn = document.getElementById('wClearFilter');
      const mBanner = document.getElementById('wMobileFilterBanner');
      const mText = document.getElementById('wMobileFilterText');

      if (filterCity !== 'all') {{
        badge.textContent = `📍 ${{filterCity.toUpperCase()}} (${{filtered.length}})`;
        clearBtn.classList.remove('hidden');
        mBanner.classList.remove('hidden');
        mText.textContent = `📍 CITY: ${{filterCity.toUpperCase()}} (${{filtered.length}})`;
      }} else if (filterCountry !== 'all') {{
        badge.textContent = `🌍 ${{filterCountry.toUpperCase()}} (${{filtered.length}})`;
        clearBtn.classList.remove('hidden');
        mBanner.classList.remove('hidden');
        mText.textContent = `🌍 COUNTRY: ${{filterCountry.toUpperCase()}} (${{filtered.length}})`;
      }} else {{
        badge.textContent = `All Institutions (${{filtered.length}})`;
        clearBtn.classList.add('hidden');
        mBanner.classList.add('hidden');
      }}

      renderWList();
    }}

    function renderWList() {{
      const container = document.getElementById('wListContainer');
      container.innerHTML = filtered.map(inst => {{
        const isSel = selectedInst && selectedInst.name === inst.name;
        let dom = 'website';
        try {{ dom = new URL(inst.website || inst.sources[0]).hostname.replace(/^www\\./, ''); }} catch(e) {{}}
        return `
          <div class="widget-item bg-[#0d1017] border border-[#1a202c] rounded-lg p-2 cursor-pointer hover:border-[#3b82f6] ${{isSel ? 'active' : ''}}" data-name="${{inst.name.replace(/"/g, '&quot;')}}">
            <div class="flex items-center justify-between">
              <span class="font-semibold text-white text-[11px] truncate max-w-[140px]">${{inst.name}}</span>
              <span class="text-[9px] px-1 py-0.2 rounded border ${{inst.tier === 'A' ? 'bg-[#092015] text-emerald-400 border-emerald-900' : 'bg-[#0a1b30] text-blue-400 border-blue-900'}}">${{inst.tier === 'A' ? 'Verified' : 'One Name'}}</span>
            </div>
            <div class="flex items-center justify-between mt-1 text-[10px]">
              <span class="text-[#60a5fa] truncate max-w-[110px]">${{inst.location}}</span>
              <a href="${{inst.website || inst.sources[0]}}" target="_blank" rel="noopener noreferrer" 
                 class="text-[#3b82f6] hover:underline flex items-center gap-0.5" onclick="event.stopPropagation()">
                <span>🌐</span> <span class="truncate max-w-[70px]">${{dom}}</span> <span>↗</span>
              </a>
            </div>
          </div>
        `;
      }}).join('');

      container.querySelectorAll('.widget-item').forEach(el => {{
        el.addEventListener('click', () => {{
          const n = el.getAttribute('data-name');
          const target = DATA.find(i => i.name === n);
          if (target) {{
            selectInst(target);
            if (window.innerWidth < 640) wTabGlobe.click();
          }}
        }});
      }});
    }}

    document.getElementById('wClearFilter').addEventListener('click', clearFilters);
    document.getElementById('wMobileClearFilter').addEventListener('click', clearFilters);

    function clearFilters() {{
      filterCity = 'all';
      filterCountry = 'all';
      searchQ = '';
      document.getElementById('wSearch').value = '';
      applyWFilters();
    }}

    document.getElementById('wSearch').addEventListener('input', e => {{
      searchQ = e.target.value.trim();
      applyWFilters();
    }});

    // Canvas
    const canvas = document.getElementById('widgetCanvas');
    const ctx = canvas.getContext('2d');
    let rotLon = -45;
    let rotLat = 35;
    let startRotLon = -45;
    let startRotLat = 35;
    let targetRotLon = -45;
    let targetRotLat = 35;
    let isFlying = false;
    let flightProgress = 0;
    let isDragging = false;
    let lastX = 0, lastY = 0;
    let pointerStartX = 0, pointerStartY = 0, pointerDownTime = 0;

    let cityBadges = [];

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
      cityBadges = [];

      if (isFlying) {{
        flightProgress += 0.012;
        if (flightProgress >= 1) {{ flightProgress = 1; isFlying = false; rotLon = targetRotLon; rotLat = targetRotLat; }}
        else {{
          const t = flightProgress;
          const ease = t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
          rotLon = startRotLon + (targetRotLon - startRotLon) * ease;
          rotLat = startRotLat + (targetRotLat - startRotLat) * ease;
        }}
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

      // Country polygons
      COUNTRY_POLYS.forEach(country => {{
        const isCActive = filterCountry !== 'all' && matchC(country.n, filterCountry);
        ctx.fillStyle = isCActive ? '#2563eb' : country.c;
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
          ctx.strokeStyle = isCActive ? '#93c5fd' : '#020b18';
          ctx.lineWidth = 0.5;
          ctx.stroke();
        }}
      }});

      // City Badges (Clickable!)
      PRIORITY_CITIES.forEach(cty => {{
        const pt = project(cty.lon, cty.lat, r, cx, cy);
        if (pt.front && pt.depth > 0.35) {{
          const isSel = filterCity.toLowerCase() === cty.name.toLowerCase();
          ctx.font = '600 8px "Inter", sans-serif';
          const tw = ctx.measureText(cty.name).width;
          const badgeW = tw + 15;
          const badgeH = 14;
          const bx = pt.x - 2;
          const by = pt.y - badgeH / 2;

          cityBadges.push({{ name: cty.name, x: bx, y: by, w: badgeW, h: badgeH, lon: cty.lon, lat: cty.lat }});

          ctx.fillStyle = isSel ? '#1d4ed8' : 'rgba(9, 14, 24, 0.9)';
          roundRect(ctx, bx, by, badgeW, badgeH, 3);
          ctx.fill();

          ctx.strokeStyle = isSel ? '#ffffff' : 'rgba(59, 130, 246, 0.45)';
          ctx.lineWidth = 0.8;
          ctx.stroke();

          ctx.fillStyle = isSel ? '#f1c21b' : '#ffffff';
          ctx.fillRect(bx + 3.5, by + 5, 2.5, 2.5);

          ctx.fillStyle = '#ffffff';
          ctx.textAlign = 'left';
          ctx.textBaseline = 'middle';
          ctx.fillText(cty.name, bx + 9.5, by + badgeH / 2 + 0.5);
        }}
      }});

      ctx.restore();

      // Rim
      ctx.strokeStyle = '#1d4ed8';
      ctx.lineWidth = 1.2;
      ctx.beginPath();
      ctx.arc(cx, cy, r, 0, Math.PI * 2);
      ctx.stroke();

      // Institution Dots
      filtered.forEach(inst => {{
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

      // Card
      const card = document.getElementById('wCard');
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

    function flyTo(lon, lat) {{
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

    function selectInst(inst) {{
      selectedInst = inst;
      document.getElementById('wCardTitle').textContent = inst.name;
      document.getElementById('wCardMeta').textContent = `${{inst.location}} · ${{inst.tier === 'A' ? 'Verified' : 'One Name'}}`;
      const webUrl = inst.website || (inst.sources && inst.sources[0]) || '';
      let dom = 'website';
      try {{ dom = new URL(webUrl).hostname.replace(/^www\\./, ''); }} catch(e) {{}}
      const lk = document.getElementById('wCardLink');
      const dm = document.getElementById('wCardDom');
      if (lk && dm) {{
        lk.href = webUrl;
        dm.textContent = dom;
      }}
      flyTo(inst.lon, inst.lat);
      applyWFilters();
    }}

    canvas.addEventListener('pointerdown', e => {{
      isDragging = true;
      canvas.classList.add('dragging');
      lastX = e.clientX;
      lastY = e.clientY;
      pointerStartX = e.clientX;
      pointerStartY = e.clientY;
      pointerDownTime = Date.now();
    }});

    window.addEventListener('pointermove', e => {{
      if (isDragging) {{
        const dx = e.clientX - lastX;
        const dy = e.clientY - lastY;
        lastX = e.clientX;
        lastY = e.clientY;
        rotLon = (rotLon - dx * 0.2) % 360;
        rotLat = Math.max(-75, Math.min(75, rotLat + dy * 0.2));
      }}
    }});

    window.addEventListener('pointerup', e => {{
      if (isDragging) {{
        isDragging = false;
        canvas.classList.remove('dragging');
      }}

      const dist = Math.hypot(e.clientX - pointerStartX, e.clientY - pointerStartY);
      const dur = Date.now() - pointerDownTime;
      if (dist < 5 && dur < 350) {{
        const rect = canvas.getBoundingClientRect();
        const mx = e.clientX - rect.left;
        const my = e.clientY - rect.top;

        for (let i = 0; i < cityBadges.length; i++) {{
          const b = cityBadges[i];
          if (mx >= b.x && mx <= b.x + b.w && my >= b.y && my <= b.y + b.h) {{
            if (filterCity.toLowerCase() === b.name.toLowerCase()) {{
              filterCity = 'all';
            }} else {{
              filterCity = b.name;
              filterCountry = 'all';
              flyTo(b.lon, b.lat);
            }}
            applyWFilters();
            return;
          }}
        }}

        const cx = canvas.width / 2;
        const cy = canvas.height / 2;
        const r = Math.min(canvas.width, canvas.height) * 0.44;
        for (let i = 0; i < COUNTRY_CENTROIDS.length; i++) {{
          const c = COUNTRY_CENTROIDS[i];
          const pt = project(c.lon, c.lat, r, cx, cy);
          if (pt.front && Math.hypot(pt.x - mx, pt.y - my) < 18) {{
            if (filterCountry.toLowerCase() === c.name.toLowerCase()) {{
              filterCountry = 'all';
            }} else {{
              filterCountry = c.name;
              filterCity = 'all';
              flyTo(c.lon, c.lat);
            }}
            applyWFilters();
            return;
          }}
        }}
      }}
    }});

    applyWFilters();
  </script>
</body>
</html>
"""
    dest_widget = "/Users/polinavasilyeva/.gemini/antigravity/brain/b997e616-4551-453e-83cc-4ba184f90abf/concierge_widget.html"
    with open(dest_widget, "w", encoding="utf-8") as f:
        f.write(widget_html)
    print("Updated concierge_widget.html with mobile-optimized layout!")

if __name__ == "__main__":
    update_widget()
