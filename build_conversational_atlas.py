import json
import re

def build():
    print("Decoding topojson polygons for researcher-grade conversational atlas...")
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

    import base64
    b64_reg = base64.b64encode(open('app/fonts/PPTelegraf-Regular.otf', 'rb').read()).decode('ascii')

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
<script src="https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js"></script>
  <script>
    tailwind.config = {{
      theme: {{
        extend: {{
          fontFamily: {{
            sans: ['"PP Telegraf"', '"PP Telegraph"', 'sans-serif'],
            mono: ['"PP Telegraf"', '"PP Telegraph"', 'sans-serif'],
          }},
          fontSize: {{
            'xs': ['14px', '1.45'],
            'sm': ['14px', '1.45'],
            'base': ['18px', '1.35'],
            'md': ['18px', '1.35'],
            'lg': ['18px', '1.35'],
            'xl': ['24px', '1.25'],
            '2xl': ['24px', '1.25'],
            '3xl': ['24px', '1.25'],
          }}
        }}
      }}
    }};
  </script>
  <style>
        /* ========================================================= */
    /* STRICT EXCLUSIVITY: ONLY PP TELEGRAF REGULAR FOR EVERYTHING */
    /* STRICT 3-TYPE-SIZE SYSTEM: 14px Floor/Body, 18px Mid, 24px Headline */
    /* ========================================================= */
    *, *::before, *::after, html, body, input, button, select, textarea, p, span, div, li, a, h1, h2, h3, h4, h5, h6, strong, b, code, pre, kbd, samp, .font-mono, [class*="font-mono"], [class*="font-"] {{
      font-family: 'PP Telegraf', 'PP Telegraph', sans-serif !important;
      font-weight: 400 !important;
      font-synthesis: none !important;
      -webkit-font-smoothing: antialiased;
      -moz-osx-font-smoothing: grayscale;
    }}

    *, *::before, *::after {{
      font-size: 14px;
    }}
    html, body {{
      font-size: 14px !important;
      line-height: 1.45;
    }}
    input, button, select, textarea, p, span, div, li, a {{
      font-size: 14px;
    }}

    /* Size 1: 14px (Floor / Default) */
    .type-14, .text-14, .text-[14px],
    [class*="text-\[8"], [class*="text-\[9"], [class*="text-\[10"], 
    [class*="text-\[11"], [class*="text-\[12"], [class*="text-\[13"],
    [class*="text-\[14px\]"], .text-xs, .text-sm {{
      font-size: 14px !important;
      line-height: 1.45 !important;
    }}

    /* Size 2: 18px (Card Titles, Subheaders, Museum Names) */
    .type-18, .text-18, .text-[18px], .text-md, .text-base, .text-lg,
    [class*="text-\[15"], [class*="text-\[16"], [class*="text-\[17"], [class*="text-\[18"], [class*="text-\[19"], [class*="text-\[20"],
    [class*="text-\[18px\]"] {{
      font-size: 18px !important;
      line-height: 1.35 !important;
    }}

    /* Size 3: 24px (Main Brand Title, Modal Headlines, Large Dossier Titles) */
    .type-24, .text-24, .text-xl, .text-2xl, .text-3xl, .text-4xl,
    [class*="text-\[21"], [class*="text-\[22"], [class*="text-\[23"], [class*="text-\[24"], [class*="text-\[25"], [class*="text-\[26"], [class*="text-\[28"], [class*="text-\[30"], [class*="text-\[32"],
    [class*="text-\[24px\]"] {{
      font-size: 24px !important;
      line-height: 1.25 !important;
    }}

    @font-face {{
      font-family: 'PP Telegraph';
      src: url('data:font/otf;base64,{b64_reg}') format('opentype'),
           local('PP Telegraf Regular'), local('PPTelegraf-Regular'), local('PP Telegraph Regular'), local('PP Telegraph');
      font-weight: 400;
      font-style: normal;
      font-display: swap;
    }}
    @font-face {{
      font-family: 'PP Telegraph';
      src: url('data:font/otf;base64,{b64_reg}') format('opentype'),
           local('PP Telegraf Regular'), local('PPTelegraf-Regular'), local('PP Telegraph Regular');
      font-weight: 500;
      font-style: normal;
      font-display: swap;
    }}
    @font-face {{
      font-family: 'PP Telegraph';
      src: url('data:font/otf;base64,{b64_reg}') format('opentype'),
           local('PP Telegraf Regular'), local('PPTelegraf-Regular'), local('PP Telegraph Regular');
      font-weight: 600;
      font-style: normal;
      font-display: swap;
    }}
    @font-face {{
      font-family: 'PP Telegraph';
      src: url('data:font/otf;base64,{b64_reg}') format('opentype'),
           local('PP Telegraf Regular'), local('PPTelegraf-Regular'), local('PP Telegraph Regular');
      font-weight: 700;
      font-style: normal;
      font-display: swap;
    }}
    @font-face {{
      font-family: 'PP Telegraf';
      src: url('data:font/otf;base64,{b64_reg}') format('opentype'),
           local('PP Telegraf Regular'), local('PPTelegraf-Regular'), local('PP Telegraph Regular'), local('PP Telegraph');
      font-weight: 400;
      font-style: normal;
      font-display: swap;
    }}
    @font-face {{
      font-family: 'PP Telegraf';
      src: url('data:font/otf;base64,{b64_reg}') format('opentype'),
           local('PP Telegraf Regular'), local('PPTelegraf-Regular'), local('PP Telegraph Regular');
      font-weight: 500;
      font-style: normal;
      font-display: swap;
    }}
    @font-face {{
      font-family: 'PP Telegraf';
      src: url('data:font/otf;base64,{b64_reg}') format('opentype'),
           local('PP Telegraf Regular'), local('PPTelegraf-Regular'), local('PP Telegraph Regular');
      font-weight: 600;
      font-style: normal;
      font-display: swap;
    }}
    @font-face {{
      font-family: 'PP Telegraf';
      src: url('data:font/otf;base64,{b64_reg}') format('opentype'),
           local('PP Telegraf Regular'), local('PPTelegraf-Regular'), local('PP Telegraph Regular');
      font-weight: 700;
      font-style: normal;
      font-display: swap;
    }}

    body {{
      font-family: 'PP Telegraf', 'PP Telegraph', sans-serif !important;
      background-color: #000000;
      color: #f8fafc;
      margin: 0;
      padding: 0;
      overflow: hidden;
      height: 100vh;
      height: 100dvh;
    }}
    .font-mono {{
      font-family: 'PP Telegraf', 'PP Telegraph', sans-serif !important;
      letter-spacing: -0.01em;
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
      height: 4px;
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
    
    /* Mobile & Desktop Bottom Half Sheet Smooth Transitions */
    #globeViewport {{
      transition: height 0.32s cubic-bezier(0.16, 1, 0.3, 1);
    }}
    #bottomChatSection {{
      transition: height 0.32s cubic-bezier(0.16, 1, 0.3, 1);
    }}
    .sheet-closed #globeViewport {{
      height: calc(100% - 46px) !important;
    }}
    .sheet-closed #bottomChatSection {{
      height: 46px !important;
    }}
    .sheet-half #globeViewport {{
      height: 50vh !important;
      height: 50dvh !important;
    }}
    .sheet-half #bottomChatSection {{
      height: 50vh !important;
      height: 50dvh !important;
    }}
    .sheet-full #globeViewport {{
      height: 12vh !important;
      height: 12dvh !important;
    }}
    .sheet-full #bottomChatSection {{
      height: 88vh !important;
      height: 88dvh !important;
    }}
    .sheet-closed #curatorPanel,
    .sheet-closed #catalogPanel {{
      display: none !important;
    }}
    .sheet-closed #sheetClosedBar {{
      display: flex !important;
    }}
    .sheet-half #sheetClosedBar,
    .sheet-full #sheetClosedBar {{
      display: none !important;
    }}
    .sheet-closed #sheetOpenControls {{
      display: none !important;
    }}
    .sheet-half #sheetOpenControls,
    .sheet-full #sheetOpenControls {{
      display: flex !important;
    }}

    /* Message Bubble Typing Animation */
    .typing-dot {{
      animation: typingBounce 1.4s infinite ease-in-out both;
    }}
    .typing-dot:nth-child(1) {{ animation-delay: -0.32s; }}
    .typing-dot:nth-child(2) {{ animation-delay: -0.16s; }}
    @keyframes typingBounce {{
      0%, 80%, 100% {{ transform: scale(0); opacity: 0.3; }}
      40% {{ transform: scale(1); opacity: 1; }}
    }}
  </style>
</head>
<body class="bg-black text-slate-100 h-screen h-[100dvh] flex flex-col select-none overflow-hidden">

  <!-- ========================================================= -->
  <!-- MAIN APP CONTAINER (Top Half: 3D Globe / Bottom Half: Conversational Chat) -->
  <!-- ========================================================= -->
  <div id="mainAppContainer" class="sheet-half relative w-full h-full flex flex-col bg-[#020408] overflow-hidden">

    <!-- ========================================================= -->
    <!-- 🌍 TOP HALF: 3D GLOBE MAP (HALF SCREEN) -->
    <!-- ========================================================= -->
    <div id="globeViewport" class="relative w-full h-[48vh] sm:h-[50vh] flex items-center justify-center bg-[#020408] overflow-hidden shrink-0 border-b border-[#1c212a]">
      
      <canvas id="globeCanvas" width="900" height="700" class="w-full h-full object-contain cursor-grab"></canvas>

      <!-- FLOATING WHITE CARD (Pinned to selected institution with Website Link & Hours) -->
      <div id="floatingCard" class="absolute z-20 pointer-events-auto bg-white text-slate-900 rounded-lg px-3 py-2 shadow-2xl transition duration-150 transform -translate-x-1/2 -translate-y-full mb-3 cursor-pointer border border-slate-100 max-w-[300px] sm:max-w-[340px]">
        <div class="flex items-center justify-between gap-1.5">
          <div id="floatingCardTitle" class="font-bold text-[18px] text-slate-950 leading-tight truncate">Plug In ICA</div>
          <span id="floatingCardTier" class="text-[14px] sm:text-[14px] font-semibold uppercase px-1.5 py-0.5 bg-emerald-100 text-emerald-800 rounded shrink-0">Verified</span>
        </div>
        <div id="floatingCardMeta" class="text-[14px] sm:text-[14px] text-slate-500 mt-0.5 flex items-center gap-1">
          <span>Winnipeg, Canada</span>
        </div>
        <div id="floatingCardHours" class="text-[14px] font-mono text-emerald-700 mt-0.5 truncate">Tue–Fri 12:00–18:00 · Free Entry</div>
        <div class="mt-1.5 pt-1.5 border-t border-slate-100 flex items-center justify-between text-[14px] sm:text-[14px] gap-2">
          <a id="floatingCardWebLink" href="https://plugin.org" target="_blank" rel="noopener noreferrer" 
             class="inline-flex items-center gap-1 font-medium text-[#1d4ed8] hover:text-[#1e40af] hover:underline"
             onclick="event.stopPropagation()">
            <span>🌐</span> <span id="floatingCardDomain" class="truncate max-w-[80px]">plugin.org</span> <span class="text-[14px]">↗</span>
          </a>
          <button id="floatingCardAskCurator" class="inline-flex items-center gap-1 text-[#0f62fe] font-semibold hover:underline" onclick="event.stopPropagation()">
            <span>💬</span> <span>Ask Curator</span>
          </button>
        </div>
        <div class="absolute bottom-0 left-1/2 -translate-x-1/2 translate-y-full w-0 h-0 border-x-[6px] border-x-transparent border-t-[6px] border-t-white"></div>
      </div>

      <!-- Top-Left Branding Watermark & Tagline -->
      <div class="absolute top-2.5 left-2.5 sm:top-3 sm:left-4 z-10 pointer-events-auto flex items-center gap-2 bg-[#070a12]/85 backdrop-blur-md px-2.5 py-1.5 rounded-xl border border-[#1e2638]">
        <div class="w-2.5 h-2.5 rounded-full bg-[#1d4ed8]"></div>
        <div class="flex flex-col">
          <div class="flex items-center gap-1.5">
            <span class="text-[24px] font-bold tracking-wider text-[#cbd5e1] uppercase">CULTURE ATLAS</span>
            <span class="text-[14px] sm:text-[14px] font-mono text-emerald-400 bg-[#0a2016] px-1.5 rounded border border-emerald-900/60">203 SANCTUARIES</span>
          </div>
          <span class="text-[14px] sm:text-[14px] text-[#94a3b8] font-normal block leading-tight mt-0.5 truncate max-w-[210px] sm:max-w-none">
            Ethically funded cultural institutions across the world
          </span>
        </div>
      </div>

      <!-- Top-Right Globe Map Controls & Reset -->
      <div class="absolute top-2.5 right-2.5 sm:top-3 sm:right-4 z-10 flex items-center gap-1.5">
        <button id="resetViewBtn" class="bg-[#0e1320]/90 hover:bg-[#1b233a] border border-[#222c42] text-slate-300 px-2 sm:px-2.5 py-1 rounded-lg text-[14px] sm:text-[14px] font-mono transition flex items-center gap-1 shadow">
          <span>🔄</span> <span class="hidden sm:inline">Reset</span>
        </button>
        <button id="spinBtn" class="bg-[#0e1320]/90 hover:bg-[#1b233a] border border-[#222c42] text-[#3b82f6] hover:text-white px-2 sm:px-2.5 py-1 rounded-lg text-[14px] sm:text-[14px] font-mono transition shadow">
          <span>⟳</span> <span class="hidden sm:inline">Auto-Spin</span>
        </button>
        <button id="zoomInBtn" class="w-7 h-7 sm:w-8 sm:h-8 rounded-lg bg-[#0e1320]/90 border border-[#222c42] text-slate-300 hover:text-white flex items-center justify-center transition shadow text-[14px] sm:text-[14px] font-mono" title="Zoom In">+</button>
        <button id="zoomOutBtn" class="w-7 h-7 sm:w-8 sm:h-8 rounded-lg bg-[#0e1320]/90 border border-[#222c42] text-slate-300 hover:text-white flex items-center justify-center transition shadow text-[14px] sm:text-[14px] font-mono" title="Zoom Out">−</button>
      </div>

      <!-- Bottom-Left Map Scale & Attribution -->
      <div class="absolute bottom-2 left-2.5 sm:left-4 z-10 pointer-events-none flex items-center gap-2 text-[14px] sm:text-[14px] text-[#64748b] font-mono bg-[#070a12]/75 px-2 py-0.5 rounded border border-[#161d2d]/60">
        <span>└───┘ 2,000 km</span>
        <span>·</span>
        <span>WGS84 Audited</span>
      </div>

      <!-- Bottom-Right "Why MoMA is Excluded" Button -->
      <div class="absolute bottom-2 right-2.5 sm:right-4 z-10 pointer-events-auto">
        <button id="openMomaAuditBtn" class="text-[14px] sm:text-[14px] font-semibold text-[#f1c21b] hover:text-white bg-[#1a1406]/90 border border-[#4d3d0f] hover:border-[#f1c21b] px-2 sm:px-2.5 py-0.5 rounded-lg transition flex items-center gap-1 shadow">
          <span>⚠️</span> <span>Why MoMA is excluded</span>
        </button>
      </div>

    </div>

    <!-- ========================================================= -->
    <!-- 💬 BOTTOM HALF: CHAT CURATOR & CATALOG (HALF SHEET) -->
    <!-- ========================================================= -->
    <div id="bottomChatSection" class="relative w-full h-[50vh] flex flex-col bg-[#07090e] overflow-hidden border-t border-[#1c212a] z-20">
      
      <!-- Sheet Drag Handle & Open/Close Bar -->
      <div id="sheetHeaderBar" class="px-2.5 py-1.5 sm:px-4 sm:py-2 border-b border-[#1c212a] bg-[#0a0d14]/95 flex flex-col gap-1 shrink-0 select-none">
        
        <!-- Drag Handle Indicator Pill -->
        <div id="sheetDragHandle" class="w-10 h-1 bg-slate-600 hover:bg-slate-400 rounded-full mx-auto my-0.5 transition cursor-grab active:cursor-grabbing" title="Drag or tap to toggle sheet"></div>

        <!-- 1. Open State Controls Row (Shown when Half or Full) -->
        <div id="sheetOpenControls" class="flex items-center justify-between gap-2">
          
          <!-- Mode Navigation Tabs (💬 Curator Guide / 📋 Research Catalog) -->
          <div class="flex items-center bg-[#101420] border border-[#1e2434] rounded-lg p-0.5 text-[14px] font-medium">
            <button id="tabCuratorBtn" class="py-1 px-2.5 sm:px-3 rounded-md transition text-center flex items-center gap-1.5 bg-[#1d4ed8] text-white font-semibold shadow">
              <span>💬</span>
              <span>Curator Guide</span>
            </button>
            <button id="tabCatalogBtn" class="py-1 px-2.5 sm:px-3 rounded-md transition text-center flex items-center gap-1.5 text-[#94a3b8] hover:text-white">
              <span>📋</span>
              <span>Catalog (203)</span>
            </button>
          </div>

          <!-- Right Controls: Status + Expand/Restore + Close Toggle -->
          <div class="flex items-center gap-1.5">
            <span id="listTotalBadge" class="text-[14px] sm:text-[14px] font-mono text-[#94a3b8] bg-[#161821] px-2 py-0.5 rounded border border-[#282c38]">
              203 mapped
            </span>
            <span id="activeFilterBadge" class="hidden text-[14px] sm:text-[14px] font-mono text-[#60a5fa] bg-[#0d1d36] border border-[#1d4ed8] px-2 py-0.5 rounded flex items-center gap-1">
              <span id="activeFilterText">Filtered</span>
              <button id="clearActiveFilterBtn" class="text-slate-400 hover:text-white ml-0.5">✕</button>
            </span>

            <!-- Expand / Half Toggle Button -->
            <button id="sheetExpandBtn" class="bg-[#121622] hover:bg-[#1c2336] border border-[#222a3c] text-slate-300 hover:text-white px-2 py-1 rounded-lg text-[14px] font-mono transition flex items-center gap-1" title="Expand / Restore Sheet">
              <span id="sheetExpandIcon">⤢</span>
              <span id="sheetExpandLabel" class="hidden sm:inline text-[14px]">Full</span>
            </button>

            <!-- Close Sheet Button -->
            <button id="sheetCloseBtn" class="bg-[#182032] hover:bg-[#202c46] border border-[#283654] text-[#60a5fa] hover:text-white px-2.5 py-1 rounded-lg text-[14px] font-semibold transition flex items-center gap-1 shadow" title="Close Chat Sheet">
              <span>▼</span>
              <span class="text-[14px]">Close</span>
            </button>
          </div>

        </div>

        <!-- 2. Closed State Bar (Shown when Closed) -->
        <div id="sheetClosedBar" class="hidden flex items-center justify-between gap-2 cursor-pointer py-0.5">
          <div class="flex items-center gap-2 truncate">
            <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            <span class="text-[14px] font-semibold text-white truncate">💬 Conversational Curator</span>
            <span class="text-[14px] text-[#94a3b8] font-mono hidden sm:inline truncate">· 203 Sanctuaries Mapped</span>
          </div>

          <div class="flex items-center gap-2 shrink-0">
            <span class="text-[14px] font-mono text-emerald-400 bg-[#0a2016] px-2 py-0.5 rounded border border-emerald-900/60 hidden xs:inline">
              Tap to Ask
            </span>
            <button id="sheetOpenBtn" class="px-3 py-1 bg-[#1d4ed8] hover:bg-[#2563eb] text-white text-[14px] font-semibold rounded-lg transition shadow flex items-center gap-1">
              <span>▲</span>
              <span>Open Half Sheet</span>
            </button>
          </div>
        </div>

      </div>

      <!-- VIEW A: 💬 CURATOR CONVERSATIONAL EXPERIENCE (Default in Bottom Half) -->
      <div id="curatorPanel" class="flex-1 flex flex-col min-h-0 overflow-hidden">
        
        <!-- Scrollable Conversation Feed -->
        <div id="curatorMessages" class="flex-1 overflow-y-auto custom-scrollbar p-3 sm:p-4 space-y-3 pb-2">
          <!-- Messages injected dynamically -->
        </div>

        <!-- Typing Indicator -->
        <div id="curatorTyping" class="hidden px-3 sm:px-4 py-1 text-[14px] text-[#94a3b8] flex items-center gap-2">
          <span class="text-[14px]">Curator is searching scholarly audit records</span>
          <span class="inline-flex gap-1">
            <span class="w-1.5 h-1.5 rounded-full bg-[#3b82f6] typing-dot"></span>
            <span class="w-1.5 h-1.5 rounded-full bg-[#3b82f6] typing-dot"></span>
            <span class="w-1.5 h-1.5 rounded-full bg-[#3b82f6] typing-dot"></span>
          </span>
        </div>

        <!-- Gentle Educational & Visitor Planning Inquiry Chips (Horizontal Carousel) -->
        <div class="px-2.5 py-1.5 border-t border-[#161a26] bg-[#080b12] flex items-center gap-1.5 overflow-x-auto custom-scrollbar shrink-0 text-[14px] font-mono whitespace-nowrap">
          <button class="inquiry-chip px-2.5 py-1 rounded-full border border-[#1b3324] bg-[#0c1f15] text-[#6ee7b7] hover:border-[#10b981] hover:bg-[#112d1e] transition active:scale-95" data-query="Which cultural spaces offer always free admission?">
            🎟️ Free Admission
          </button>
          <button class="inquiry-chip px-2.5 py-1 rounded-full border border-[#232a3c] bg-[#101522] text-[#93c5fd] hover:border-[#3b82f6] hover:bg-[#151c30] transition active:scale-95" data-query="What are typical museum opening hours and which institutions are open on Mondays?">
            🕒 Hours & Mondays
          </button>
          <button class="inquiry-chip px-2.5 py-1 rounded-full border border-[#232a3c] bg-[#101522] text-[#93c5fd] hover:border-[#3b82f6] hover:bg-[#151c30] transition active:scale-95" data-query="How do I get to destination museums like Dia Beacon or Louisiana by public transit?">
            🚇 Public Transit Tips
          </button>
          <button class="inquiry-chip px-2.5 py-1 rounded-full border border-[#232a3c] bg-[#101522] text-[#cbd5e1] hover:border-[#3b82f6] hover:bg-[#151c30] transition active:scale-95" data-query="Which museums offer step-free wheelchair accessibility and inclusive facilities?">
            ♿ Accessibility
          </button>
          <button class="inquiry-chip px-2.5 py-1 rounded-full border border-[#232a3c] bg-[#101522] text-[#cbd5e1] hover:border-[#3b82f6] hover:bg-[#151c30] transition active:scale-95" data-query="Which institutions feature outstanding cafés, sculpture gardens, and art bookshops?">
            ☕ Cafés & Bookshops
          </button>
          <button class="inquiry-chip px-2.5 py-1 rounded-full border border-[#232a3c] bg-[#101522] text-[#93c5fd] hover:border-[#3b82f6] hover:bg-[#151c30] transition active:scale-95" data-query="What makes an institution ethically funded?">
            🏛️ Ethical Criteria
          </button>
          <button class="inquiry-chip px-2.5 py-1 rounded-full border border-[#232a3c] bg-[#101522] text-[#cbd5e1] hover:border-[#3b82f6] hover:bg-[#151c30] transition active:scale-95" data-query="Recommend independent artist-run centers and grassroots kunsthalles">
            🎨 Artist-Run Spaces
          </button>
          <button class="inquiry-chip px-2.5 py-1 rounded-full border border-[#1b3324] bg-[#0c1f15] text-[#6ee7b7] hover:border-[#10b981] hover:bg-[#112d1e] transition active:scale-95" data-query="Show institutions free from fossil fuels and defense sponsors">
            🌿 Fossil & defense-free spaces
          </button>
          <button class="inquiry-chip px-2.5 py-1 rounded-full border border-[#232a3c] bg-[#101522] text-[#93c5fd] hover:border-[#3b82f6] hover:bg-[#151c30] transition active:scale-95" data-query="Recommend verified cultural spaces in London" data-city="London">
            📍 London guide
          </button>
          <button class="inquiry-chip px-2.5 py-1 rounded-full border border-[#232a3c] bg-[#101522] text-[#93c5fd] hover:border-[#3b82f6] hover:bg-[#151c30] transition active:scale-95" data-query="Recommend verified cultural spaces in New York" data-city="New York">
            📍 New York guide
          </button>
          <button class="inquiry-chip px-2.5 py-1 rounded-full border border-[#232a3c] bg-[#101522] text-[#93c5fd] hover:border-[#3b82f6] hover:bg-[#151c30] transition active:scale-95" data-query="Recommend verified cultural spaces in Tokyo" data-city="Tokyo">
            📍 Tokyo guide
          </button>
          <button class="inquiry-chip px-2.5 py-1 rounded-full border border-[#232a3c] bg-[#101522] text-[#93c5fd] hover:border-[#3b82f6] hover:bg-[#151c30] transition active:scale-95" data-query="Recommend verified cultural spaces in Paris" data-city="Paris">
            📍 Paris guide
          </button>
          <button class="inquiry-chip px-2.5 py-1 rounded-full border border-[#3b2b11] bg-[#221807] text-[#fcd34d] hover:border-[#f59e0b] hover:bg-[#2d2009] transition active:scale-95" data-query="Why is MoMA excluded from Culture Atlas?">
            ⚠️ Why MoMA is excluded
          </button>
          <button class="inquiry-chip px-2.5 py-1 rounded-full border border-[#232a3c] bg-[#101522] text-[#cbd5e1] hover:border-[#3b82f6] hover:bg-[#151c30] transition active:scale-95" data-query="Surprise me with a unique ethical cultural institution">
            ✨ Surprise me
          </button>
        </div>

        <!-- Sticky Chat Input Bar -->
        <div class="p-2.5 sm:p-3 border-t border-[#1c212a] bg-[#0a0d14] flex items-center gap-2 shrink-0">
          <div class="relative flex-1">
            <input 
              type="text" 
              id="curatorInput" 
              placeholder="Ask curator: 'Where should I go in London?', 'Hours for Dia Beacon', 'Artist-run spaces'..." 
              class="w-full bg-[#121622] border border-[#232a3c] rounded-xl px-3 sm:px-3.5 py-2 text-[14px] text-white placeholder-slate-500 focus:outline-none focus:border-[#3b82f6] transition shadow-inner font-sans"
            />
          </div>
          <button 
            id="curatorSendBtn" 
            class="px-4 py-2 bg-[#1d4ed8] hover:bg-[#2563eb] text-white text-[14px] font-semibold rounded-xl transition shadow active:scale-95 flex items-center gap-1 shrink-0"
          >
            <span>Ask</span>
            <span class="text-[14px]">↵</span>
          </button>
          <button id="curatorSettingsBtn" class="p-2 bg-[#121622] hover:bg-[#1c2234] border border-[#232938] text-[#94a3b8] hover:text-white rounded-xl text-[14px] transition shrink-0" title="Curator Settings">
            <span>⚙️</span>
          </button>
        </div>

      </div>

      <!-- VIEW B: 📋 RESEARCH CATALOG (When toggled to Catalog in Bottom Half) -->
      <div id="catalogPanel" class="hidden flex-1 flex flex-col min-h-0 overflow-hidden">
        
        <div class="p-2.5 sm:p-3 border-b border-[#1c212a] bg-[#0a0d14] flex flex-col gap-2 shrink-0">
          <!-- Active Filter Banner (When city/country clicked) -->
          <div id="activeFilterBanner" class="hidden flex items-center justify-between bg-[#0e1628] border border-[#1d4ed8] px-2.5 py-1.5 rounded-lg text-[14px]">
            <div class="flex items-center gap-1.5 truncate">
              <span id="filterIcon" class="text-[14px]">📍</span>
              <span id="filterLabel" class="font-semibold text-white truncate">NEW YORK</span>
              <span id="filterCount" class="text-[#60a5fa] font-mono text-[14px]">(11)</span>
            </div>
            <button id="clearFilterBtn" class="text-[14px] text-[#94a3b8] hover:text-white px-1.5 py-0.5 rounded hover:bg-[#1a253c] transition ml-2 flex items-center gap-1">
              <span>Clear</span> <span>✕</span>
            </button>
          </div>

          <!-- Search Input -->
          <div class="relative">
            <input 
              type="text" 
              id="searchInput" 
              placeholder="Search museum, city, focus, or governance..." 
              class="w-full bg-[#141722] border border-[#262a38] text-[14px] text-white placeholder-[#64748b] px-3 py-1.5 rounded-lg focus:outline-none focus:border-[#3b82f6] transition"
            />
            <button id="clearSearchBtn" class="hidden absolute right-2.5 top-1.5 text-[#64748b] hover:text-white text-[14px]">✕</button>
          </div>

          <!-- Quick Filters: Country & City Dropdowns -->
          <div class="grid grid-cols-2 gap-1.5 text-[14px] font-mono">
            <select id="countrySelect" class="bg-[#141722] border border-[#262a38] text-[#e2e8f0] px-2 py-1 rounded focus:outline-none focus:border-[#3b82f6] truncate">
              <option value="all">All Countries (35)</option>
            </select>
            <select id="citySelect" class="bg-[#141722] border border-[#262a38] text-[#e2e8f0] px-2 py-1 rounded focus:outline-none focus:border-[#3b82f6] truncate">
              <option value="all">All Cities (133)</option>
            </select>
          </div>

          <!-- Tier Quick Chips -->
          <div class="flex items-center gap-1.5 text-[14px] font-mono">
            <button class="tier-chip flex-1 py-1 px-1.5 rounded border border-emerald-900 bg-[#0c2419] text-emerald-400 font-semibold text-center hover:bg-[#113324] transition" data-tier="A">
              Tier A (135)
            </button>
            <button class="tier-chip flex-1 py-1 px-1.5 rounded border border-blue-900 bg-[#0e213b] text-blue-400 font-semibold text-center hover:bg-[#132d52] transition" data-tier="B">
              Tier B (52)
            </button>
            <button class="tier-chip flex-1 py-1 px-1.5 rounded border border-slate-700 bg-[#171a24] text-slate-400 font-semibold text-center hover:bg-[#202534] transition" data-tier="U">
              Tier U (16)
            </button>
          </div>
        </div>

        <!-- Scrollable Institutions Feed -->
        <div id="institutionsListContainer" class="flex-1 overflow-y-auto custom-scrollbar p-3 space-y-2 pb-6">
          <!-- Populated dynamically -->
        </div>

      </div>

    </div>

  </div>

  <!-- ========================================================= -->
  <!-- 📄 SCHOLARLY INSTITUTION AUDIT DOSSIER DRAWER -->
  <!-- ========================================================= -->
  <div id="detailDrawer" class="hidden fixed inset-y-0 right-0 z-50 w-full max-w-lg bg-[#0a0d15]/98 backdrop-blur-2xl border-l border-[#1c212a] shadow-2xl flex flex-col">
    <div class="p-4 border-b border-[#1c212a] flex items-center justify-between bg-[#0e121c]">
      <div class="flex items-center gap-2">
        <span class="text-[14px]">🔍</span>
        <span class="text-[14px] font-mono font-semibold text-[#60a5fa] uppercase tracking-wider">Scholarly Governance & Funding Audit</span>
      </div>
      <button id="closeDetailBtn" class="text-slate-400 hover:text-white p-1 rounded hover:bg-[#1a2234] transition text-[18px]">✕</button>
    </div>
    <div id="detailBody" class="flex-1 overflow-y-auto custom-scrollbar p-5 space-y-4 text-[14px]">
      <!-- Injected dynamically -->
    </div>
  </div>

  <!-- ========================================================= -->
  <!-- ========================================================= -->
  <!-- ⚠️ MoMA EXCLUSION AUDIT MODAL -->
  <!-- ========================================================= -->
  <div id="momaAuditModal" class="hidden fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-3 sm:p-5 select-text">
    <div class="bg-[#0b0e17] border border-[#f59e0b]/50 rounded-2xl max-w-lg w-full max-h-[90vh] flex flex-col shadow-2xl overflow-hidden font-sans">
      
      <!-- Modal Header -->
      <div class="px-4 py-3 border-b border-[#252f48] bg-[#141008] flex items-center justify-between shrink-0">
        <div class="flex items-center gap-2">
          <span class="text-amber-400 text-[18px]">⚠️</span>
          <div>
            <h3 class="font-bold text-white text-[24px]">EXCLUSION AUDIT · Why MoMA is Excluded</h3>
            <p class="text-[14px] font-mono text-amber-300/80">Museum of Modern Art (New York) · Institutional Scrutiny</p>
          </div>
        </div>
        <button id="closeMomaModalBtn" class="w-7 h-7 rounded-lg bg-[#20180a] hover:bg-[#33250f] border border-[#523d14] text-slate-300 hover:text-white flex items-center justify-center text-[14px] transition">✕</button>
      </div>

      <!-- Modal Body -->
      <div class="p-4 sm:p-5 overflow-y-auto custom-scrollbar space-y-3.5 text-[14px] text-slate-200 leading-relaxed">
        
        <!-- Summary Callout -->
        <div class="bg-[#181207] border border-[#78350f]/60 rounded-xl p-3 text-[14px] space-y-1">
          <span class="text-amber-400 font-semibold uppercase tracking-wider text-[14px] block font-mono">⚡ Exclusion Criteria Assessment</span>
          <p class="text-slate-200">
            Culture Atlas celebrates cultural institutions that champion curatorial freedom and clean underwriting. MoMA is excluded from our verified directory due to documented, unaddressed governance ties to defense contractors, private prisons, and controversial private equity financiers.
          </p>
        </div>

        <!-- Section 1: Leon Black & Jeffrey Epstein -->
        <div class="space-y-1">
          <h4 class="font-semibold text-white text-[18px] flex items-center gap-1.5">
            <span class="text-rose-400 font-bold">1.</span> <span>Leon Black & Jeffrey Epstein ($158M)</span>
          </h4>
          <p class="text-slate-300 text-[14px] pl-4">
            Former MoMA Board Chairman <strong>Leon Black</strong> (founder of Apollo Global Management) stepped down in March 2021 after independent forensic audits revealed he transferred $158 million to convicted sex offender Jeffrey Epstein between 2012 and 2017.
          </p>
        </div>

        <!-- Section 2: Strike MoMA Movement -->
        <div class="space-y-1">
          <h4 class="font-semibold text-white text-[18px] flex items-center gap-1.5">
            <span class="text-rose-400 font-bold">2.</span> <span>The 'Strike MoMA' Movement (Spring 2021)</span>
          </h4>
          <p class="text-slate-300 text-[14px] pl-4">
            A coalition of artists, cultural workers, and grassroots collectives (Decolonize This Place, Strike MoMA, and Artists Space allies) held 10 weeks of continuous protests demanding institutional accountability, trustee divestment, and community restitution.
          </p>
        </div>

        <!-- Section 3: Controversial Trustee Portfolio -->
        <div class="space-y-1">
          <h4 class="font-semibold text-white text-[18px] flex items-center gap-1.5">
            <span class="text-rose-400 font-bold">3.</span> <span>Extractive & Defense Board Holdings</span>
          </h4>
          <ul class="list-disc pl-8 space-y-1 text-slate-300 text-[14px]">
            <li><strong>Steven Tananbaum (GoldenTree Asset Management):</strong> Board trustee targeted by artists over vulture fund holdings exacerbating Puerto Rico's debt and hurricane recovery crises.</li>
            <li><strong>Larry Fink (CEO, BlackRock):</strong> Board trustee heading the world's largest institutional investor in fossil fuel expansion, weapons manufacturing, and private detention centers.</li>
            <li><strong>Paula Crown:</strong> Trustee whose billionaire family owns General Dynamics, one of the world's largest defense and aerospace contractors.</li>
          </ul>
        </div>

        <!-- Section 4: What to Visit Instead -->
        <div class="bg-[#0e1628] border border-[#1d4ed8]/50 rounded-xl p-3 space-y-1.5">
          <span class="text-[#60a5fa] font-semibold text-[14px] uppercase tracking-wider block font-mono">🌿 Verified Ethical Alternatives in New York</span>
          <p class="text-slate-300 text-[14px]">
            Instead of supporting corporate-compromised boards, visit New York's <strong>11 verified ethical cultural sanctuaries</strong>—including <em>Dia Beacon, SculptureCenter, Artists Space, and The Studio Museum in Harlem</em>.
          </p>
        </div>

      </div>

      <!-- Modal Footer -->
      <div class="px-4 py-2.5 border-t border-[#252f48] bg-[#0c101c] flex items-center justify-between gap-2 shrink-0">
        <button id="momaAuditFlyNycBtn" class="px-3 py-1.5 bg-[#1d4ed8] hover:bg-[#2563eb] text-white text-[14px] font-semibold rounded-xl transition flex items-center gap-1.5 shadow">
          <span>🗽</span> <span>Explore 11 Ethical NYC Spaces</span>
        </button>
        <button id="momaAuditChatBtn" class="px-3 py-1.5 bg-[#172032] hover:bg-[#22304c] border border-[#2b3b5c] text-slate-200 hover:text-white text-[14px] rounded-xl transition flex items-center gap-1.5">
          <span>💬</span> <span>Ask in Chat</span>
        </button>
      </div>

    </div>
  </div>

  <!-- ⚙️ CURATOR SETTINGS MODAL (Optional Google Gemini API Key) -->
  <!-- ========================================================= -->
  <div id="curatorSettingsModal" class="hidden fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
    <div class="bg-[#0e1320] border border-[#222a3e] rounded-2xl max-w-md w-full p-5 shadow-2xl flex flex-col gap-4">
      <div class="flex items-center justify-between border-b border-[#1c2336] pb-3">
        <div class="flex items-center gap-2">
          <span class="text-[18px]">⚙️</span>
          <h3 class="font-semibold text-white text-[24px]">Curator Intelligence Settings</h3>
        </div>
        <button id="closeSettingsModalBtn" class="text-slate-400 hover:text-white text-[14px] p-1">✕</button>
      </div>
      <div class="text-[14px] text-slate-300 leading-relaxed space-y-3">
        <p>
          Culture Atlas features a <strong>Built-in Offline Intelligence Engine</strong> with deep knowledge of all 203 institutions, funding governance, divestment history, and cultural geographies.
        </p>
        <p>
          Optionally, you can enter your <strong>Google Gemini API Key</strong> to activate live multi-turn Gemini 2.5 reasoning:
        </p>
        <div>
          <label class="block text-[14px] font-mono text-slate-400 mb-1">Gemini API Key (Optional)</label>
          <input 
            type="password" 
            id="geminiApiKeyInput" 
            placeholder="AIzaSy..." 
            class="w-full bg-[#141a2a] border border-[#263148] text-[14px] text-white px-3 py-2 rounded-lg focus:outline-none focus:border-[#3b82f6]"
          />
        </div>
        <div class="flex items-center justify-between pt-2">
          <span id="geminiStatusTag" class="text-[14px] font-mono text-emerald-400">Offline Engine Active</span>
          <button id="saveApiKeyBtn" class="px-3.5 py-1.5 bg-[#1d4ed8] hover:bg-[#2563eb] text-white text-[14px] font-semibold rounded-lg transition">
            Save Settings
          </button>
        </div>
      </div>
    </div>
  </div>

  <script>
    // Embedded Data Sources (Enriched by Researcher Pipeline)
    const COUNTRY_POLYS = {countries_json};
    const ALL_INSTITUTIONS = {institutions_json};

    const COUNTRY_CENTROIDS = [
      {{ name: 'UNITED STATES', lon: -98.5, lat: 39.8 }},
      {{ name: 'UNITED KINGDOM', lon: -2.2, lat: 53.5 }},
      {{ name: 'FRANCE', lon: 2.2, lat: 46.2 }},
      {{ name: 'GERMANY', lon: 10.4, lat: 51.1 }},
      {{ name: 'JAPAN', lon: 138.2, lat: 36.2 }},
      {{ name: 'AUSTRALIA', lon: 133.7, lat: -25.2 }},
      {{ name: 'CANADA', lon: -106.3, lat: 56.1 }},
      {{ name: 'SPAIN', lon: -3.7, lat: 40.4 }},
      {{ name: 'DENMARK', lon: 9.5, lat: 56.2 }},
      {{ name: 'NORWAY', lon: 8.4, lat: 60.4 }},
      {{ name: 'NETHERLANDS', lon: 5.2, lat: 52.1 }},
      {{ name: 'SOUTH AFRICA', lon: 22.9, lat: -30.5 }},
      {{ name: 'MOROCCO', lon: -7.0, lat: 31.7 }},
      {{ name: 'MEXICO', lon: -102.5, lat: 23.6 }},
      {{ name: 'SOUTH KOREA', lon: 127.7, lat: 35.9 }}
    ];

    const PRIORITY_CITIES = [
      {{ name: 'NEW YORK', lon: -74.006, lat: 40.7128 }},
      {{ name: 'LONDON', lon: -0.1278, lat: 51.5074 }},
      {{ name: 'TOKYO', lon: 139.6917, lat: 35.6895 }},
      {{ name: 'PARIS', lon: 2.3522, lat: 48.8566 }},
      {{ name: 'BERLIN', lon: 13.405, lat: 52.52 }},
      {{ name: 'CHICAGO', lon: -87.6298, lat: 41.8781 }},
      {{ name: 'TORONTO', lon: -79.3832, lat: 43.6532 }},
      {{ name: 'SAN FRANCISCO', lon: -122.4194, lat: 37.7749 }},
      {{ name: 'MELBOURNE', lon: 144.9631, lat: -37.8136 }},
      {{ name: 'SYDNEY', lon: 151.2093, lat: -33.8688 }},
      {{ name: 'VANCOUVER', lon: -123.1207, lat: 49.2827 }},
      {{ name: 'MONTREAL', lon: -73.5673, lat: 45.5017 }},
      {{ name: 'COPENHAGEN', lon: 12.5683, lat: 55.6761 }},
      {{ name: 'AMSTERDAM', lon: 4.9041, lat: 52.3676 }},
      {{ name: 'MADRID', lon: -3.7038, lat: 40.4168 }},
      {{ name: 'BARCELONA', lon: 2.1734, lat: 41.3851 }},
      {{ name: 'EDINBURGH', lon: -3.1883, lat: 55.9533 }},
      {{ name: 'OSLO', lon: 10.7522, lat: 59.9139 }},
      {{ name: 'STOCKHOLM', lon: 18.0686, lat: 59.3293 }},
      {{ name: 'SEOUL', lon: 126.978, lat: 37.5665 }},
      {{ name: 'MEXICO CITY', lon: -99.1332, lat: 19.4326 }},
      {{ name: 'BORDEAUX', lon: -0.5792, lat: 44.8378 }},
      {{ name: 'MARRAKECH', lon: -7.9811, lat: 31.6295 }},
      {{ name: 'CAPE TOWN', lon: 18.4241, lat: -33.9249 }},
      {{ name: 'WINNIPEG', lon: -97.1384, lat: 49.8951 }},
      {{ name: 'AARHUS', lon: 10.2039, lat: 56.1629 }}
    ];

    // State Variables
    let filteredList = [...ALL_INSTITUTIONS];
    let selectedTierFilter = new Set(['A', 'B', 'U']);
    let selectedCountryFilter = 'all';
    let selectedCityFilter = 'all';
    let searchQuery = '';
    let selectedInstitution = ALL_INSTITUTIONS.find(i => i.name === 'Plug In ICA') || ALL_INSTITUTIONS[0];
    let hoveredInstitution = null;
    let hoveredCity = null;
    let hoveredCountry = null;

    // Canvas & 3D Math Setup
    const canvas = document.getElementById('globeCanvas');
    const ctx = canvas.getContext('2d');
    let width = canvas.width = canvas.parentElement.clientWidth;
    let height = canvas.height = canvas.parentElement.clientHeight;

    function getBaseRadius() {{
      const minDim = Math.min(width, height);
      return window.innerWidth < 768 ? Math.max(120, minDim * 0.38) : Math.max(160, minDim * 0.33);
    }}
    let baseRadius = getBaseRadius();
    let currentRadius = baseRadius;
    let targetRadius = baseRadius;

    function getMinRadius() {{ return baseRadius * 0.7; }}
    function getMaxRadius() {{ return baseRadius * 4.5; }}

    // Slower Cinematic Motion Physics
    let rotLon = -45;
    let rotLat = 35;
    let isAutoSpinning = true;
    let isDragging = false;
    let lastX = 0, lastY = 0;
    let pointerStartX = 0, pointerStartY = 0;
    let pointerDownTime = 0;

    let isFlying = false;
    let flightProgress = 0;
    let startRotLon = 0, startRotLat = 0;
    let targetRotLon = 0, targetRotLat = 0;

    function resizeCanvas() {{
      if (!canvas.parentElement) return;
      width = canvas.width = canvas.parentElement.clientWidth;
      height = canvas.height = canvas.parentElement.clientHeight;
      baseRadius = getBaseRadius();
      targetRadius = Math.max(getMinRadius(), Math.min(getMaxRadius(), targetRadius));
    }}
    window.addEventListener('resize', resizeCanvas);

    function toRad(deg) {{ return deg * Math.PI / 180; }}
    function toDeg(rad) {{ return rad * 180 / Math.PI; }}

    function project(lon, lat, r, cx, cy) {{
      const lambda = toRad(lon - rotLon);
      const phi = toRad(lat);
      const theta = toRad(rotLat);

      const cosPhi = Math.cos(phi);
      const x = r * cosPhi * Math.sin(lambda);
      const y = r * (Math.cos(theta) * Math.sin(phi) - Math.sin(theta) * cosPhi * Math.cos(lambda));
      const z = r * (Math.sin(theta) * Math.sin(phi) + Math.cos(theta) * cosPhi * Math.cos(lambda));

      return {{
        x: cx + x,
        y: cy - y,
        front: z > -r * 0.15,
        depth: (z + r) / (2 * r)
      }};
    }}

    function unproject(px, py, r, cx, cy) {{
      const x = (px - cx) / r;
      const y = -(py - cy) / r;
      const d2 = x * x + y * y;
      if (d2 > 1) return null;
      const z = Math.sqrt(Math.max(0, 1 - d2));

      const theta = toRad(rotLat);
      const sinTheta = Math.sin(theta);
      const cosTheta = Math.cos(theta);

      const yPrime = y * cosTheta + z * sinTheta;
      const zPrime = -y * sinTheta + z * cosTheta;

      const phi = Math.asin(Math.max(-1, Math.min(1, yPrime)));
      const lambda = Math.atan2(x, zPrime);

      return {{
        lat: toDeg(phi),
        lon: (toDeg(lambda) + rotLon + 540) % 360 - 180
      }};
    }}

    function pointInPolygon(px, py, poly) {{
      let inside = false;
      for (let i = 0, j = poly.length - 1; i < poly.length; j = i++) {{
        const xi = poly[i][0], yi = poly[i][1];
        const xj = poly[j][0], yj = poly[j][1];
        const intersect = ((yi > py) !== (yj > py)) && (px < (xj - xi) * (py - yi) / (yj - yi) + xi);
        if (intersect) inside = !inside;
      }}
      return inside;
    }}

    function matchC(a, b) {{
      if (!a || !b) return false;
      const s1 = a.toLowerCase().trim();
      const s2 = b.toLowerCase().trim();
      return s1 === s2 || s1.includes(s2) || s2.includes(s1);
    }}

    function easeInOutQuad(t) {{
      return t < 0.5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2;
    }}

    let cityBadgeHitboxes = [];
    let visibleDots = [];

    function render() {{
      ctx.clearRect(0, 0, width, height);

      if (isAutoSpinning && !isDragging && !isFlying) {{
        rotLon = (rotLon + 0.04) % 360;
      }}

      if (isFlying) {{
        flightProgress += 0.011;
        if (flightProgress >= 1) {{
          flightProgress = 1;
          isFlying = false;
          rotLon = targetRotLon % 360;
          rotLat = targetRotLat;
        }} else {{
          const ease = easeInOutQuad(flightProgress);
          rotLon = (startRotLon + (targetRotLon - startRotLon) * ease) % 360;
          rotLat = startRotLat + (targetRotLat - startRotLat) * ease;
        }}
      }}

      currentRadius += (targetRadius - currentRadius) * 0.08;

      const cx = width / 2;
      const cy = height / 2;
      const r = currentRadius;

      // Dark space / ocean sphere
      ctx.beginPath();
      ctx.arc(cx, cy, r, 0, Math.PI * 2);
      ctx.fillStyle = '#010204';
      ctx.fill();
      ctx.strokeStyle = '#182030';
      ctx.lineWidth = 1;
      ctx.stroke();

      // Graticule
      ctx.strokeStyle = '#0a101d';
      ctx.lineWidth = 0.5;
      for (let lat = -60; lat <= 60; lat += 30) {{
        ctx.beginPath();
        let first = true;
        for (let lon = -180; lon <= 180; lon += 6) {{
          const p = project(lon, lat, r, cx, cy);
          if (p.front) {{
            if (first) {{ ctx.moveTo(p.x, p.y); first = false; }}
            else ctx.lineTo(p.x, p.y);
          }} else first = true;
        }}
        ctx.stroke();
      }}

      // Land Polygons
      for (let i = 0; i < COUNTRY_POLYS.length; i++) {{
        const country = COUNTRY_POLYS[i];
        const isCActive = selectedCountryFilter !== 'all' && matchC(country.n, selectedCountryFilter);
        ctx.fillStyle = isCActive ? '#1d4ed8' : country.c;

        for (let j = 0; j < country.r.length; j++) {{
          const ring = country.r[j];
          if (!ring || ring.length < 3) continue;
          ctx.beginPath();
          let started = false;
          for (let k = 0; k < ring.length; k++) {{
            const p = project(ring[k][0], ring[k][1], r, cx, cy);
            if (p.front) {{
              if (!started) {{ ctx.moveTo(p.x, p.y); started = true; }}
              else ctx.lineTo(p.x, p.y);
            }}
          }}
          if (started) {{
            ctx.closePath();
            ctx.fill();
            ctx.strokeStyle = isCActive ? '#60a5fa' : '#040b17';
            ctx.lineWidth = isCActive ? 1.5 : 0.4;
            ctx.stroke();
          }}
        }}
      }}

      // Country Centroid Names
      if (r > baseRadius * 0.8) {{
        ctx.font = '14px "PP Telegraf", "PP Telegraph", sans-serif';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        COUNTRY_CENTROIDS.forEach(c => {{
          const pt = project(c.lon, c.lat, r, cx, cy);
          if (pt.front && pt.depth > 0.15) {{
            const isSel = selectedCountryFilter !== 'all' && matchC(c.name, selectedCountryFilter);
            ctx.fillStyle = isSel ? '#60a5fa' : '#475569';
            ctx.fillText(c.name, pt.x, pt.y);
          }}
        }});
      }}

      // Priority City Badges
      cityBadgeHitboxes = [];
      ctx.font = '14px "PP Telegraf", "PP Telegraph", sans-serif';
      PRIORITY_CITIES.forEach(city => {{
        const pt = project(city.lon, city.lat, r, cx, cy);
        if (pt.front && pt.depth > 0.08) {{
          const isSelected = selectedCityFilter.toLowerCase() === city.name.toLowerCase();
          const txt = (isSelected ? '● ' : '■ ') + city.name;
          const tw = ctx.measureText(txt).width;
          const bw = tw + 12;
          const bh = 22;
          const bx = pt.x - bw / 2;
          const by = pt.y - 26;

          cityBadgeHitboxes.push({{
            name: city.name,
            x: bx, y: by, w: bw, h: bh,
            lon: city.lon, lat: city.lat
          }});

          ctx.fillStyle = isSelected ? '#1d4ed8' : '#070b14';
          ctx.beginPath();
          ctx.roundRect ? ctx.roundRect(bx, by, bw, bh, 4) : ctx.rect(bx, by, bw, bh);
          ctx.fill();

          ctx.strokeStyle = isSelected ? '#93c5fd' : '#222d42';
          ctx.lineWidth = 1;
          ctx.stroke();

          ctx.fillStyle = isSelected ? '#ffffff' : '#cbd5e1';
          ctx.textAlign = 'center';
          ctx.textBaseline = 'middle';
          ctx.fillText(txt, pt.x, by + bh / 2 + 0.5);

          ctx.beginPath();
          ctx.arc(pt.x, pt.y, 2, 0, Math.PI * 2);
          ctx.fillStyle = isSelected ? '#93c5fd' : '#3b82f6';
          ctx.fill();
        }}
      }});

      // Render Institution Dots
      visibleDots = [];
      filteredList.forEach(inst => {{
        const pt = project(inst.lon, inst.lat, r, cx, cy);
        if (pt.front && pt.depth > 0.05) {{
          visibleDots.push({{
            inst,
            x: pt.x,
            y: pt.y,
            renderX: pt.x,
            renderY: pt.y,
            depth: pt.depth
          }});
        }}
      }});

      // Prevent dot overlaps
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

          ctx.font = '14px "PP Telegraf", "PP Telegraph", sans-serif';
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

    // Camera Navigation
    function flyTo(lon, lat, targetZoom = null) {{
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

      if (targetZoom) {{
        targetRadius = Math.max(getMinRadius(), Math.min(getMaxRadius(), targetZoom));
      }}
    }}

    function selectInstitution(inst, shouldSwitchToGlobe = false) {{
      selectedInstitution = inst;
      document.getElementById('floatingCardTitle').textContent = inst.name;
      document.getElementById('floatingCardMeta').textContent = `${{inst.location}} · ${{inst.tier === 'A' ? 'Verified' : 'One Name'}}`;
      document.getElementById('floatingCardTier').textContent = inst.tier === 'A' ? 'Verified' : inst.tier === 'B' ? 'One Name' : 'Unverified';
      
      const hoursEl = document.getElementById('floatingCardHours');
      if (hoursEl) {{
        const shortH = inst.opening_hours ? inst.opening_hours.split(',')[0] : 'Open Weekly';
        const shortF = inst.admission_fee ? inst.admission_fee.split('/')[0].trim() : 'Free / Subsidized';
        hoursEl.textContent = `${{shortH}} · ${{shortF}}`;
      }}

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

      if (shouldSwitchToGlobe) {{
        targetRadius = Math.max(targetRadius, baseRadius * 2.5);
        if (currentSheetState === 'full') setChatSheetState('half');
      }}
      flyTo(inst.lon, inst.lat, shouldSwitchToGlobe ? baseRadius * 2.5 : null);

      // Top half globe is always visible
    }}

    // Scholarly Audit Dossier View
    function openDossier(inst) {{
      const drawer = document.getElementById('detailDrawer');
      const body = document.getElementById('detailBody');
      drawer.classList.remove('hidden');

      let domain = 'website';
      const webUrl = inst.website || (inst.sources && inst.sources[0]) || '';
      try {{ domain = new URL(webUrl).hostname.replace(/^www\\./, ''); }} catch(e) {{}}

      const tierBadgeClass = inst.tier === 'A' 
        ? 'text-emerald-400 border-emerald-800 bg-[#092216]' 
        : inst.tier === 'B' 
        ? 'text-blue-400 border-blue-800 bg-[#0d1e36]' 
        : 'text-slate-400 border-slate-700 bg-[#171a24]';

      const tierLabel = inst.tier === 'A' ? 'Tier A · Verified Clean' : inst.tier === 'B' ? 'Tier B · Transparent with Commercial Co-Sponsor' : 'Tier U · Under Evaluation';

      body.innerHTML = `
        <div class="space-y-3">
          <div>
            <div class="flex items-center gap-1.5 mb-1.5 flex-wrap">
              <span class="text-[14px] font-mono px-2 py-0.5 rounded border ${{tierBadgeClass}}">${{tierLabel}}</span>
              <span class="text-[14px] font-mono px-2 py-0.5 rounded bg-[#101828] text-[#93c5fd] border border-[#202d48]">🏛️ ${{inst.governance_type}}</span>
              <span class="text-[14px] font-mono px-2 py-0.5 rounded bg-[#141e17] text-[#6ee7b7] border border-[#1b3b2b]">🎨 ${{inst.curatorial_focus}}</span>
              <span class="text-[14px] font-mono px-2 py-0.5 rounded bg-[#1f1910] text-amber-300 border border-[#3e2e18]">📅 Est. ${{inst.year_founded}}</span>
            </div>
            <h2 class="text-[18px] sm:text-[18px] font-bold text-white leading-snug">${{inst.name}}</h2>
            <p class="text-[14px] text-[#60a5fa] mt-0.5 font-mono">${{inst.location}} · ${{inst.size === 'L' ? 'Large Institution (>$20M / >500k visitors)' : 'Small / Mid-sized Kunsthalle'}}</p>
          </div>

          ${{webUrl ? `
            <a href="${{webUrl}}" target="_blank" rel="noopener noreferrer" 
               class="inline-flex items-center justify-center gap-2 w-full py-2.5 bg-[#1d4ed8] hover:bg-[#2563eb] text-white font-semibold text-[14px] rounded-xl transition shadow-md active:scale-95">
              <span>🌐</span> <span>Visit Official Museum Website (${{domain}})</span> <span>↗</span>
            </a>
          ` : ''}}

          <!-- Scholarly Visitor Recommendation -->
          <div class="bg-[#0b101c] p-3 rounded-xl border border-[#1a253c]">
            <span class="text-[14px] font-semibold text-[#60a5fa] uppercase tracking-wider block mb-1">Curator Visitor Recommendation</span>
            <p class="text-[14px] text-slate-200 leading-relaxed">${{inst.curator_recommendation}}</p>
          </div>

          <!-- Visitor Planning & Practical Guide (Authentic Institutional Data) -->
          <div class="bg-[#0b101c] p-3 rounded-xl border border-[#1e2a44] space-y-2.5">
            <div class="flex items-center justify-between border-b border-[#1a253c] pb-1.5">
              <span class="text-[14px] font-bold text-white uppercase tracking-wider flex items-center gap-1.5">
                <span>🧭</span> <span>Visitor Planning & Practical Guide</span>
              </span>
              ${{inst.visit_url ? `
                <a href="${{inst.visit_url}}" target="_blank" rel="noopener noreferrer" class="text-[14px] text-[#60a5fa] hover:underline flex items-center gap-1 font-mono">
                  <span>Plan Your Visit ↗</span>
                </a>
              ` : ''}}
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-2 gap-2 text-[14px]">
              <!-- Hours -->
              <div class="bg-[#101626] p-2.5 rounded-lg border border-[#1c273e]">
                <div class="text-[14px] text-slate-400 font-mono flex items-center gap-1 mb-1">
                  <span>🕒</span> <span>Hours & Schedule</span>
                </div>
                <div class="text-slate-200 font-medium text-[14px] leading-snug">${{inst.opening_hours || 'Check official site'}}</div>
              </div>

              <!-- Admission Pricing -->
              <div class="bg-[#101626] p-2.5 rounded-lg border border-[#1c273e]">
                <div class="text-[14px] text-slate-400 font-mono flex items-center gap-1 mb-1">
                  <span>🎟️</span> <span>Admission & Tickets</span>
                </div>
                <div class="text-emerald-400 font-medium text-[14px] leading-snug">${{inst.admission_fee || 'Subsidized Admission'}}</div>
              </div>

              <!-- Address & Cultural District -->
              <div class="bg-[#101626] p-2.5 rounded-lg border border-[#1c273e]">
                <div class="text-[14px] text-slate-400 font-mono flex items-center gap-1 mb-1">
                  <span>📍</span> <span>Address & Quarter</span>
                </div>
                <div class="text-slate-200 text-[14px] leading-snug">${{inst.address || inst.location}}</div>
                ${{inst.neighborhood ? `<div class="text-[14px] text-[#93c5fd] font-mono mt-0.5">${{inst.neighborhood}}</div>` : ''}}
              </div>

              <!-- Recommended Duration -->
              <div class="bg-[#101626] p-2.5 rounded-lg border border-[#1c273e]">
                <div class="text-[14px] text-slate-400 font-mono flex items-center gap-1 mb-1">
                  <span>⏱️</span> <span>Suggested Duration</span>
                </div>
                <div class="text-slate-200 text-[14px] leading-snug">${{inst.visit_duration || '1.5 – 2.5 hours'}}</div>
              </div>
            </div>

            <!-- Transit & Directions -->
            <div class="bg-[#101626] p-2.5 rounded-lg border border-[#1c273e]">
              <div class="text-[14px] text-slate-400 font-mono flex items-center gap-1 mb-1">
                <span>🚇</span> <span>Public Transit & Directions</span>
              </div>
              <div class="text-[14px] text-slate-300 leading-relaxed">${{inst.transit_tips || 'Accessible via central public transit network.'}}</div>
            </div>

            <!-- Collection / Architecture Highlight -->
            <div class="bg-[#101626] p-2.5 rounded-lg border border-[#1c273e]">
              <div class="text-[14px] text-amber-400/90 font-mono flex items-center gap-1 mb-1">
                <span>⭐</span> <span>Visitor Highlight & Signature Art</span>
              </div>
              <div class="text-[14px] text-slate-200 leading-relaxed font-medium">${{inst.highlight || 'Celebrated collection and contemporary commissions.'}}</div>
            </div>

            <!-- Accessibility & Amenities -->
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-2 text-[14px]">
              <div class="bg-[#101626] p-2.5 rounded-lg border border-[#1c273e]">
                <div class="text-[14px] text-slate-400 font-mono flex items-center gap-1 mb-1">
                  <span>♿</span> <span>Accessibility</span>
                </div>
                <div class="text-[14px] text-slate-300 leading-relaxed">${{inst.accessibility || 'Step-free access, elevators, accessible restrooms.'}}</div>
              </div>
              <div class="bg-[#101626] p-2.5 rounded-lg border border-[#1c273e]">
                <div class="text-[14px] text-slate-400 font-mono flex items-center gap-1 mb-1">
                  <span>☕</span> <span>Amenities & Facilities</span>
                </div>
                <div class="text-[14px] text-slate-300 leading-relaxed">${{inst.amenities || 'Art bookshop, café, cloakroom, and lockers.'}}</div>
              </div>
            </div>
          </div>

          <!-- Admission & Public Access Policy -->
          <div class="bg-[#101420] p-3 rounded-xl border border-[#1e273a]">
            <div class="flex items-center justify-between mb-1">
              <span class="text-[14px] font-semibold text-emerald-400 uppercase tracking-wider">Admission & Access Policy</span>
              <span class="text-[14px] font-mono text-[#6ee7b7] bg-[#0c1f14] px-1.5 py-0.5 rounded border border-[#154028]">${{inst.admission_policy}}</span>
            </div>
            <p class="text-[14px] text-slate-300 leading-relaxed">${{inst.admission_details}}</p>
          </div>

          <!-- Funding Architecture -->
          <div class="bg-[#101420] p-3 rounded-xl border border-[#1e273a]">
            <span class="text-[14px] font-semibold text-blue-400 uppercase tracking-wider block mb-1">Funding Architecture & Operating Budget</span>
            <p class="text-[14px] text-slate-300 leading-relaxed">${{inst.funding}}</p>
          </div>

          <!-- Ethical Safeguard Policy -->
          <div class="bg-[#101420] p-3 rounded-xl border border-[#1e273a]">
            <span class="text-[14px] font-semibold text-purple-400 uppercase tracking-wider block mb-1">Ethical Safeguards & Autonomy Charter</span>
            <p class="text-[14px] text-slate-300 leading-relaxed">${{inst.ethical_safeguard}}</p>
          </div>

          <!-- Governance Scrutiny -->
          ${{inst.watch ? `
            <div class="bg-[#1a150b] p-3 rounded-xl border border-[#382b13]">
              <span class="text-[14px] font-semibold text-amber-400 uppercase tracking-wider block mb-1">Governance Scrutiny & Watch Notes</span>
              <p class="text-[14px] text-slate-300 leading-relaxed">${{inst.watch}}</p>
            </div>
          ` : ''}}

          <!-- Financial Transparency Rating -->
          <div class="bg-[#0c121e] p-2.5 rounded-xl border border-[#1a2538] flex items-center justify-between">
            <span class="text-[14px] text-slate-400 font-mono">Transparency Grade:</span>
            <span class="text-[14px] font-semibold text-[#60a5fa] font-mono">${{inst.transparency_grade}}</span>
          </div>

          <!-- Sources & Filings -->
          <div class="pt-2 border-t border-[#1c212a]">
            <span class="text-[14px] font-semibold text-slate-400 uppercase tracking-wider block mb-2">Audited Sources, Reports & Filings</span>
            <div class="flex flex-col gap-1.5 font-mono">
              ${{(inst.sources || []).map(u => `
                <a href="${{u}}" target="_blank" class="text-[#60a5fa] hover:underline text-[14px] flex items-center gap-1">
                  <span>↗</span> <span class="truncate">${{u}}</span>
                </a>
              `).join('')}}
            </div>
          </div>
        </div>
      `;
    }}

    // =========================================================
    // 💬 CONVERSATIONAL CURATOR LOGIC & RESEARCH-GRADE ENGINE
    // =========================================================
    const curatorMessages = document.getElementById('curatorMessages');
    const curatorInput = document.getElementById('curatorInput');
    const curatorSendBtn = document.getElementById('curatorSendBtn');
    const curatorTyping = document.getElementById('curatorTyping');

    let geminiApiKey = localStorage.getItem('atlas_gemini_api_key') || '';
    let geminiModel = 'gemini-2.5-flash';

    // Initial Welcome Message with Gentle Education
    function initCuratorConversation() {{
      curatorMessages.innerHTML = '';
      appendCuratorMessage(`
        <p class="text-slate-200">
          Welcome to <strong>Culture Atlas</strong>. In an era where major art institutions routinely rely on trustees and sponsors linked to fossil fuel extraction, defense manufacturing, or predatory finance, Culture Atlas was created to map <strong>203 cultural sanctuaries across 35 countries</strong> that protect curatorial independence and public trust.
        </p>
        <p class="text-slate-300 pt-1">
          When deciding which spaces you should visit, we gently recommend four types of ethical institutions:
        </p>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-2 pt-1 text-[14px] font-sans">
          <div class="p-2.5 rounded-xl bg-[#0b0f19] border border-[#1d263b]">
            <span class="font-semibold text-emerald-400 flex items-center gap-1 mb-0.5">
              <span>🏛️</span> <span>Civic Sanctuaries</span>
            </span>
            <span class="text-slate-400 text-[14px] leading-relaxed block">
              Supported by public taxpayers and municipal arts councils with zero corporate strings or toxic board seats.
            </span>
          </div>
          <div class="p-2.5 rounded-xl bg-[#0b0f19] border border-[#1d263b]">
            <span class="font-semibold text-blue-400 flex items-center gap-1 mb-0.5">
              <span>🎨</span> <span>Grassroots Kunsthalles</span>
            </span>
            <span class="text-slate-400 text-[14px] leading-relaxed block">
              Artist-governed centers offering daring, critical contemporary exhibitions free from commercial censorship.
            </span>
          </div>
          <div class="p-2.5 rounded-xl bg-[#0b0f19] border border-[#1d263b]">
            <span class="font-semibold text-amber-400 flex items-center gap-1 mb-0.5">
              <span>🌿</span> <span>Divested Spaces</span>
            </span>
            <span class="text-slate-400 text-[14px] leading-relaxed block">
              Museums that actively divested from BP, Shell, or Baillie Gifford to keep their galleries ethically uncompromised.
            </span>
          </div>
          <div class="p-2.5 rounded-xl bg-[#0b0f19] border border-[#1d263b]">
            <span class="font-semibold text-purple-400 flex items-center gap-1 mb-0.5">
              <span>🎟️</span> <span>Free Public Access</span>
            </span>
            <span class="text-slate-400 text-[14px] leading-relaxed block">
              Spaces that eliminate ticket barriers, proving that art is a fundamental civic right rather than a luxury commodity.
            </span>
          </div>
        </div>
        <p class="pt-1.5 text-[#93c5fd] font-medium">
          Where in the world are you exploring, or what type of art experience would you love to discover today?
        </p>
      `, [
        ALL_INSTITUTIONS.find(i => i.name.includes('Chisenhale')) || ALL_INSTITUTIONS[0],
        ALL_INSTITUTIONS.find(i => i.name.includes('CAPC')) || ALL_INSTITUTIONS[1],
        ALL_INSTITUTIONS.find(i => i.name.includes('Dia Beacon')) || ALL_INSTITUTIONS[2]
      ]);
    }}

    function appendUserMessage(text) {{
      const div = document.createElement('div');
      div.className = 'flex flex-col items-end gap-1';
      div.innerHTML = `
        <div class="flex items-center gap-1.5 text-[14px] font-mono text-[#94a3b8]">
          <span>You</span>
        </div>
        <div class="max-w-[85%] bg-[#1d4ed8] text-white text-[14px] px-3.5 py-2 rounded-2xl rounded-tr-sm shadow-md leading-relaxed">
          ${{escapeHtml(text)}}
        </div>
      `;
      curatorMessages.appendChild(div);
      curatorMessages.scrollTop = curatorMessages.scrollHeight;
    }}

    function appendCuratorMessage(htmlContent, recommendedInsts = []) {{
      const div = document.createElement('div');
      div.className = 'flex flex-col gap-1.5';

      let cardsHtml = '';
      if (recommendedInsts && recommendedInsts.length > 0) {{
        cardsHtml = `
          <div class="flex flex-col gap-2 mt-2 pt-2 border-t border-[#1c2234]">
            <span class="text-[14px] font-mono uppercase tracking-wider text-[#60a5fa] flex items-center gap-1">
              <span>📍</span> <span>Recommended Cultural Institutions:</span>
            </span>
            ${{recommendedInsts.filter(Boolean).map(inst => {{
              const webUrl = inst.website || (inst.sources && inst.sources[0]) || '';
              let domain = 'website';
              try {{ domain = new URL(webUrl).hostname.replace(/^www\\./, ''); }} catch(e) {{}}
              const tierBadge = inst.tier === 'A' 
                ? '<span class="text-[14px] font-mono px-1.5 py-0.5 rounded border border-emerald-900 bg-[#0a2016] text-emerald-400">Tier A · Verified</span>'
                : '<span class="text-[14px] font-mono px-1.5 py-0.5 rounded border border-blue-900 bg-[#0d1d33] text-blue-400">Tier B · One Name</span>';

              return `
                <div class="bg-[#0b0e17] border border-[#1c2336] hover:border-[#3b82f6] rounded-xl p-3 transition shadow-sm">
                  <div class="flex items-start justify-between gap-2">
                    <div>
                      <h4 class="font-semibold text-white text-[14px]">${{inst.name}}</h4>
                      <p class="text-[14px] text-[#60a5fa] font-mono mt-0.5">${{inst.location}}</p>
                    </div>
                    ${{tierBadge}}
                  </div>

                  <div class="flex items-center gap-1.5 text-[14px] font-mono text-[#94a3b8] mt-1.5 flex-wrap">
                    <span class="px-1.5 py-0.5 rounded bg-[#101726] border border-[#1c2840] text-[#93c5fd]">🏛️ ${{inst.governance_type}}</span>
                    <span class="px-1.5 py-0.5 rounded bg-[#0a1f15] border border-[#143d28] text-emerald-300">🎟️ ${{inst.admission_policy}}</span>
                  </div>

                  <p class="text-[14px] text-slate-300 mt-2 leading-relaxed line-clamp-2">${{inst.curator_recommendation || inst.funding}}</p>
                  
                  <div class="mt-2.5 pt-2 border-t border-[#161d2d] flex items-center justify-between gap-2">
                    <button class="curator-fly-btn px-2.5 py-1 bg-[#1d4ed8] hover:bg-[#2563eb] text-white text-[14px] font-medium rounded-lg transition flex items-center gap-1 active:scale-95" data-name="${{inst.name.replace(/"/g, '&quot;')}}">
                      <span>🌍</span> <span>Fly on Globe</span>
                    </button>
                    <div class="flex items-center gap-1.5">
                      ${{webUrl ? `
                        <a href="${{webUrl}}" target="_blank" rel="noopener noreferrer" 
                           class="px-2 py-1 bg-[#121726] hover:bg-[#1a233c] border border-[#222e48] hover:border-[#3b82f6] text-[#60a5fa] hover:text-white text-[14px] font-mono rounded-lg transition flex items-center gap-1"
                           onclick="event.stopPropagation()">
                          <span>🌐</span> <span class="max-w-[90px] truncate">${{domain}}</span> <span>↗</span>
                        </a>
                      ` : ''}}
                      <button class="curator-dossier-btn px-2 py-1 text-slate-400 hover:text-white text-[14px] font-mono rounded hover:bg-[#151a28] transition" data-name="${{inst.name.replace(/"/g, '&quot;')}}">
                        Audit Dossier →
                      </button>
                    </div>
                  </div>
                </div>
              `;
            }}).join('')}}
          </div>
        `;
      }}

      div.innerHTML = `
        <div class="flex items-center gap-1.5 text-[14px] font-mono text-[#60a5fa]">
          <span>🏛️</span> <span class="font-semibold text-slate-200">Atlas Curator</span>
          <span class="text-slate-600">·</span>
          <span class="text-[14px] text-slate-400 font-sans">Guide to Ethical Culture</span>
        </div>
        <div class="bg-[#101420] border border-[#1e2538] text-[14px] text-slate-200 p-3 sm:p-3.5 rounded-2xl rounded-tl-sm shadow-md leading-relaxed space-y-2">
          ${{htmlContent}}
          ${{cardsHtml}}
        </div>
      `;
      curatorMessages.appendChild(div);

      // Bind fly buttons
      div.querySelectorAll('.curator-fly-btn').forEach(btn => {{
        btn.addEventListener('click', () => {{
          const name = btn.getAttribute('data-name');
          const inst = ALL_INSTITUTIONS.find(i => i.name === name);
          if (inst) {{
            selectInstitution(inst, true);
          }}
        }});
      }});

      div.querySelectorAll('.curator-dossier-btn').forEach(btn => {{
        btn.addEventListener('click', () => {{
          const name = btn.getAttribute('data-name');
          const inst = ALL_INSTITUTIONS.find(i => i.name === name);
          if (inst) openDossier(inst);
        }});
      }});

      curatorMessages.scrollTop = curatorMessages.scrollHeight;
    }}

    function escapeHtml(str) {{
      return (str || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
    }}

    // Intelligent Offline Curator Knowledge Engine
    function handleCuratorQuery(query) {{
      const q = query.toLowerCase().trim();
      curatorTyping.classList.remove('hidden');

      setTimeout(() => {{
        curatorTyping.classList.add('hidden');

        // A. Visitor Data: Hours & Monday Openings
        if (q.includes('hour') || q.includes('schedule') || (q.includes('time') && (q.includes('open') || q.includes('visit'))) || q.includes('monday') || q.includes('weekend') || q.includes('late night') || q.includes('closed')) {{
          const targetInst = ALL_INSTITUTIONS.find(i => q.includes(i.name.toLowerCase()) || (i.aliases && i.aliases.some(a => q.includes(a.toLowerCase()))));
          if (targetInst) {{
            appendCuratorMessage(`
              <p>🕒 <strong>Visiting Hours for ${{escapeHtml(targetInst.name)}}:</strong></p>
              <div class="p-3 rounded-xl bg-[#0b0e17] border border-[#1e2a44] text-[14px] space-y-1.5 font-mono">
                <div class="text-emerald-400 font-semibold text-[14px]">📅 ${{targetInst.opening_hours}}</div>
                <div class="text-slate-300 text-[14px] font-sans"><strong>Suggested Duration:</strong> ${{targetInst.visit_duration}}</div>
                <div class="text-slate-300 text-[14px] font-sans"><strong>Address:</strong> ${{targetInst.address}} (${{targetInst.neighborhood}})</div>
                <div class="text-[#93c5fd] text-[14px] font-sans"><strong>Transit:</strong> ${{targetInst.transit_tips}}</div>
                ${{targetInst.visit_url ? `<a href="${{targetInst.visit_url}}" target="_blank" class="text-[#60a5fa] hover:underline text-[14px] block pt-1 font-mono">Plan Your Visit (Official Museum Guide) ↗</a>` : ''}}
              </div>
            `, [targetInst]);
            selectInstitution(targetInst, false);
            return;
          }}

          if (q.includes('monday')) {{
            const mondaySpaces = ALL_INSTITUTIONS.filter(i => !i.opening_hours.toLowerCase().includes('closed mon') && (i.opening_hours.toLowerCase().includes('daily') || i.opening_hours.toLowerCase().includes('mon,') || i.opening_hours.toLowerCase().includes('mon–') || i.opening_hours.toLowerCase().includes('mon-')));
            appendCuratorMessage(`
              <p>🗓️ <strong>Ethical Cultural Institutions Open on Mondays:</strong></p>
              <p>While most traditional museums close on Mondays, we have <strong>${{mondaySpaces.length}}</strong> ethical cultural sanctuaries welcoming visitors at the start of the week. Perfect for quiet contemplation:</p>
            `, mondaySpaces.slice(0, 4));
            return;
          }}

          appendCuratorMessage(`
            <p>🕒 <strong>Institutional Schedules & Visiting Hours:</strong></p>
            <p>Most independent non-profit kunsthalles and artist-run spaces operate <strong>Wednesday through Sunday (11:00–18:00 or 12:00–18:00)</strong>, reserving Mondays and Tuesdays for installation and artist studio work. Major municipal collections frequently offer late-night Thursday or Friday openings (until 20:00–22:00, or midnight at Palais de Tokyo!).</p>
            <p class="text-slate-300">Select any institution from the catalog to view its exact timetable, or ask me about any specific venue.</p>
          `, [
            ALL_INSTITUTIONS.find(i => i.name.includes('Palais de Tokyo')),
            ALL_INSTITUTIONS.find(i => i.name.includes('Louisiana')),
            ALL_INSTITUTIONS.find(i => i.name.includes('Stedelijk'))
          ]);
          return;
        }}

        // B. Visitor Data: Public Transit & Getting There
        if (q.includes('transit') || q.includes('how to get') || q.includes('how do i get') || q.includes('direction') || q.includes('subway') || q.includes('metro') || q.includes('train') || q.includes('bus') || q.includes('ferry') || q.includes('getting there')) {{
          const targetInst = ALL_INSTITUTIONS.find(i => q.includes(i.name.toLowerCase()) || (i.aliases && i.aliases.some(a => q.includes(a.toLowerCase()))));
          if (targetInst) {{
            appendCuratorMessage(`
              <p>🚇 <strong>Public Transit Directions to ${{escapeHtml(targetInst.name)}}:</strong></p>
              <div class="p-3 rounded-xl bg-[#0b0e17] border border-[#1e2a44] text-[14px] space-y-1.5">
                <div class="text-slate-200"><strong>📍 Address:</strong> ${{targetInst.address}} (${{targetInst.neighborhood}})</div>
                <div class="text-[#93c5fd] font-mono leading-relaxed"><strong>Transit:</strong> ${{targetInst.transit_tips}}</div>
                <div class="text-slate-300"><strong>Suggested Duration:</strong> ${{targetInst.visit_duration}} · 🕒 ${{targetInst.opening_hours}}</div>
                ${{targetInst.visit_url ? `<a href="${{targetInst.visit_url}}" target="_blank" class="text-[#60a5fa] hover:underline text-[14px] block pt-1 font-mono">Official Transit & Location Page ↗</a>` : ''}}
              </div>
            `, [targetInst]);
            selectInstitution(targetInst, false);
            return;
          }}

          appendCuratorMessage(`
            <p>🚇 <strong>Public Transit & Cultural Destination Travel:</strong></p>
            <p>Culture Atlas provides verified public transit directions for all 203 institutions worldwide—whether taking the <em>Metro-North Hudson Line</em> to Dia Beacon, the <em>Kystbanen regional train</em> up the Danish coastline to Louisiana, or the <em>London Underground</em> to Whitechapel or Camden Art Centre.</p>
            <p class="text-slate-300">Here are three world-class destination institutions easily reachable via scenic rail connections:</p>
          `, [
            ALL_INSTITUTIONS.find(i => i.name.includes('Dia Beacon')),
            ALL_INSTITUTIONS.find(i => i.name.includes('Louisiana')),
            ALL_INSTITUTIONS.find(i => i.name.includes('Kröller'))
          ]);
          return;
        }}

        // C. Visitor Data: Accessibility & Inclusive Access
        if (q.includes('accessib') || q.includes('wheelchair') || q.includes('step-free') || q.includes('elevator') || q.includes('disab') || q.includes('mobility') || q.includes('sensory')) {{
          const targetInst = ALL_INSTITUTIONS.find(i => q.includes(i.name.toLowerCase()) || (i.aliases && i.aliases.some(a => q.includes(a.toLowerCase()))));
          if (targetInst) {{
            appendCuratorMessage(`
              <p>♿ <strong>Accessibility at ${{escapeHtml(targetInst.name)}}:</strong></p>
              <div class="p-3 rounded-xl bg-[#0b0e17] border border-[#1e2a44] text-[14px] space-y-1.5">
                <div class="text-emerald-400 font-medium">${{targetInst.accessibility}}</div>
                <div class="text-slate-300"><strong>Transit Access:</strong> ${{targetInst.transit_tips}}</div>
                <div class="text-slate-400 text-[14px]">Personal care assistants and companions receive free entry at all audited institutions.</div>
              </div>
            `, [targetInst]);
            selectInstitution(targetInst, false);
            return;
          }}

          appendCuratorMessage(`
            <p>♿ <strong>Universal Accessibility & Barrier-Free Access:</strong></p>
            <p>All civic institutions in Culture Atlas are committed to equitable physical and sensory access, providing step-free routes, passenger elevators, loaner wheelchairs, accessible gender-neutral washrooms, and free entry for essential companions and care assistants.</p>
            <p class="text-slate-300">Here are exemplary fully barrier-free cultural spaces:</p>
          `, [
            ALL_INSTITUTIONS.find(i => i.name.includes('Serpentine')),
            ALL_INSTITUTIONS.find(i => i.name.includes('ARoS')),
            ALL_INSTITUTIONS.find(i => i.name.includes('M+ Museum'))
          ]);
          return;
        }}

        // D. Visitor Data: Amenities (Cafés, Bookshops, Gardens)
        if (q.includes('café') || q.includes('cafe') || q.includes('coffee') || q.includes('restaurant') || q.includes('dining') || q.includes('bookshop') || q.includes('bookstore') || q.includes('garden') || q.includes('park') || q.includes('amenities') || q.includes('lockers')) {{
          const targetInst = ALL_INSTITUTIONS.find(i => q.includes(i.name.toLowerCase()) || (i.aliases && i.aliases.some(a => q.includes(a.toLowerCase()))));
          if (targetInst) {{
            appendCuratorMessage(`
              <p>☕ <strong>Amenities & On-Site Facilities at ${{escapeHtml(targetInst.name)}}:</strong></p>
              <div class="p-3 rounded-xl bg-[#0b0e17] border border-[#1e2a44] text-[14px] space-y-1.5">
                <div class="text-slate-200"><strong>Facilities:</strong> ${{targetInst.amenities}}</div>
                <div class="text-amber-300/90"><strong>Signature Highlight:</strong> ${{targetInst.highlight}}</div>
                <div class="text-slate-300 text-[14px]"><strong>Schedule:</strong> ${{targetInst.opening_hours}}</div>
              </div>
            `, [targetInst]);
            selectInstitution(targetInst, false);
            return;
          }}

          appendCuratorMessage(`
            <p>☕ <strong>Museum Cafés, Independent Bookshops & Sculpture Gardens:</strong></p>
            <p>Visiting an ethical cultural institution is also about the experience of slowing down. Many mapped spaces feature legendary non-commercial bookshops and secluded garden dining:</p>
            <ul class="list-disc pl-4 space-y-1 text-slate-300 text-[14px]">
              <li><strong>Louisiana Museum (Denmark):</strong> Seaside sculpture park and organic café overlooking Sweden.</li>
              <li><strong>Camden Art Centre (London):</strong> Quiet garden lawn café with artisan pastries and ceramics.</li>
              <li><strong>Fondazione Prada (Milan):</strong> The iconic <em>Bar Luce</em>, custom designed by filmmaker Wes Anderson.</li>
              <li><strong>The Photographers' Gallery (London):</strong> Soho's definitive international photobook specialist store.</li>
            </ul>
          `, [
            ALL_INSTITUTIONS.find(i => i.name.includes('Louisiana')),
            ALL_INSTITUTIONS.find(i => i.name.includes('Fondazione Prada')),
            ALL_INSTITUTIONS.find(i => i.name.includes('Camden Art Centre'))
          ]);
          return;
        }}

        // E. Visitor Data: Signature Highlights
        if (q.includes('highlight') || q.includes('what to see') || q.includes('must-see') || q.includes('signature') || q.includes('artworks') || q.includes('monument')) {{
          const targetInst = ALL_INSTITUTIONS.find(i => q.includes(i.name.toLowerCase()) || (i.aliases && i.aliases.some(a => q.includes(a.toLowerCase()))));
          if (targetInst) {{
            appendCuratorMessage(`
              <p>⭐ <strong>Signature Highlight for ${{escapeHtml(targetInst.name)}}:</strong></p>
              <div class="p-3 rounded-xl bg-[#0b0e17] border border-[#1e2a44] text-[14px] space-y-1.5">
                <div class="text-amber-400 font-medium text-[14px]">${{targetInst.highlight}}</div>
                <div class="text-slate-300"><strong>Curatorial Focus:</strong> ${{targetInst.curatorial_focus}}</div>
                <div class="text-slate-300"><strong>Recommended Duration:</strong> ${{targetInst.visit_duration}} · 🕒 ${{targetInst.opening_hours}}</div>
              </div>
            `, [targetInst]);
            selectInstitution(targetInst, false);
            return;
          }}

          appendCuratorMessage(`
            <p>⭐ <strong>Must-See Architectural & Art Landmarks:</strong></p>
            <p>Culture Atlas features some of the world's most astonishing site-specific art and architecture:</p>
            <ul class="list-disc pl-4 space-y-1 text-slate-300 text-[14px]">
              <li><strong>ARoS (Aarhus):</strong> Olafur Eliasson's 360° circular glass walkway <em>Your rainbow panorama</em>.</li>
              <li><strong>Dia Beacon (Hudson Valley):</strong> Richard Serra's monumental Torqued Ellipses and Michael Heizer excavations.</li>
              <li><strong>Instituto Inhotim (Brazil):</strong> 23 bespoke artist pavilions embedded in a 700-hectare tropical rainforest botanical garden.</li>
              <li><strong>Kunsthaus Bregenz (Austria):</strong> Peter Zumthor's etched glass light-box architecture.</li>
            </ul>
          `, [
            ALL_INSTITUTIONS.find(i => i.name.includes('ARoS')),
            ALL_INSTITUTIONS.find(i => i.name.includes('Dia Beacon')),
            ALL_INSTITUTIONS.find(i => i.name.includes('Inhotim'))
          ]);
          return;
        }}

        // 1. Methodology & Philosophy & "What type of institutions should I go to?"
        if (q.includes('what type') || q.includes('should i go') || q.includes('what makes') || q.includes('method') || q.includes('criteria') || q.includes('how') && (q.includes('evaluate') || q.includes('work') || q.includes('tier') || q.includes('ethical'))) {{
          appendCuratorMessage(`
            <p><strong>How to Choose an Ethically Funded Institution:</strong></p>
            <p>When selecting a cultural space to support with your visit and admission, look for how its funding protects artistic autonomy:</p>
            <ul class="list-disc pl-4 space-y-1.5 text-slate-300">
              <li><strong>Prioritize Civic & Municipal Spaces (Tier A):</strong> These museums are backed directly by public cultural councils (like Arts Council England, DRAC in France, Canada Council). Because their primary accountability is to the public, curators are not coerced into censoring provocative art to appease corporate sponsors.</li>
              <li><strong>Seek Artist-Run Centers & Grassroots Kunsthalles:</strong> These nimble non-profits are governed by artists. They commission challenging contemporary projects without corporate board oversight.</li>
              <li><strong>Check for Clean Philanthropic Charters:</strong> Endowed foundations established with strict ethical covenants rejecting fossil fuels, arms manufacturing, and private prison wealth.</li>
              <li><strong>Be Aware of 'One Name to Know' Spaces (Tier B):</strong> Major civic collections where one corporate partner is noted on the donor wall, but whose public integrity remains strong.</li>
            </ul>
            <p class="pt-1 text-[#93c5fd]">Here are three quintessential spaces exemplifying these ethical models:</p>
          `, [
            ALL_INSTITUTIONS.find(i => i.name.includes('Chisenhale')),
            ALL_INSTITUTIONS.find(i => i.name.includes('CAPC')),
            ALL_INSTITUTIONS.find(i => i.name.includes('Plug In ICA'))
          ]);
          return;
        }}

        // 2. Free Admission & Public Access
        if (q.includes('free') || q.includes('admission') || q.includes('ticket') || q.includes('accessible') || q.includes('no fee')) {{
          const freeSpaces = ALL_INSTITUTIONS.filter(i => i.admission_policy.includes('Free Public') || i.admission_policy.includes('Always Free'));
          appendCuratorMessage(`
            <p><strong>Always Free Public Admission:</strong></p>
            <p>We have <strong>${{freeSpaces.length}}</strong> cultural institutions mapped that provide completely free public admission. Eliminating ticket barriers treats contemporary art as a vital civic commons rather than a luxury commodity.</p>
            <p class="text-slate-300">Here are top verified spaces offering completely free admission:</p>
          `, freeSpaces.slice(0, 4));
          return;
        }}

        // 3. Artist-run & Grassroots Centers
        if (q.includes('artist-run') || q.includes('artist run') || q.includes('grassroots') || q.includes('kunsthalle') || q.includes('independent') || q.includes('non-profit')) {{
          const artistSpaces = ALL_INSTITUTIONS.filter(i => i.governance_type.includes('Artist-Run'));
          appendCuratorMessage(`
            <p><strong>Artist-Run Centers & Grassroots Kunsthalles:</strong></p>
            <p>We map <strong>${{artistSpaces.length}}</strong> artist-governed centers. Operating outside corporate pressures, these collectives champion daring, uncompromised artistic commissions.</p>
            <p class="text-slate-300">Here are standout artist-governed spaces worldwide:</p>
          `, artistSpaces.slice(0, 4));
          return;
        }}

        // 4. Divestment & Fossil Fuels & Defense
        if (q.includes('fossil') || q.includes('defense') || q.includes('oil') || q.includes('bp') || q.includes('shell') || q.includes('baillie') || q.includes('weapons') || q.includes('divest')) {{
          appendCuratorMessage(`
            <p><strong>Divestment & The Push for Fossil-Free Galleries:</strong></p>
            <p>For decades, extractive corporations (BP, Shell, TotalEnergies) and arms manufacturers used cultural sponsorship to 'artwash' their public standing. Over the past five years, courageous artist coalitions and cultural workers forced major venues to divest.</p>
            <p>Every single space mapped in Culture Atlas has clean underwriting without fossil-fuel or defense sponsorship on its active roster. By visiting these institutions, you directly support cultural independence.</p>
          `, [
            ALL_INSTITUTIONS.find(i => i.name.includes('Camden')),
            ALL_INSTITUTIONS.find(i => i.name.includes('Whitechapel')),
            ALL_INSTITUTIONS.find(i => i.name.includes('Nottingham Contemporary'))
          ]);
          return;
        }}

        // 5. Why MoMA / Whitney / Guggenheim are Excluded
        if (q.includes('moma') || q.includes('whitney') || q.includes('guggenheim') || q.includes('why exclude') || q.includes('excluded') || q.includes('kanders')) {{
          appendCuratorMessage(`
            <p><strong>Why MoMA and Certain Major Museums are Excluded:</strong></p>
            <p>Culture Atlas maintains a strict exclusion policy for institutions that retain unresolved ties to controversial underwriters, defense manufacturing, or human rights violations:</p>
            <ul class="list-disc pl-4 space-y-1 text-slate-300">
              <li><strong>Museum of Modern Art (MoMA, NY):</strong> Sparked citywide protests over trustees with major equity in defense manufacturing, private prisons, and extractive debt.</li>
              <li><strong>Whitney Museum (NY):</strong> Faced global artist boycotts and withdrawals until vice chair Warren Kanders (CEO of Safariland, tear gas manufacturer) stepped down.</li>
            </ul>
            <p>Culture Atlas only celebrates institutions whose funding architecture is clean and uncompromised.</p>
          `, [
            ALL_INSTITUTIONS.find(i => i.name.includes('Dia Beacon')),
            ALL_INSTITUTIONS.find(i => i.name.includes('SculptureCenter')),
            ALL_INSTITUTIONS.find(i => i.name.includes('Serpentine'))
          ]);
          return;
        }}

        // 6. Specific City Inquiries
        const matchedCity = PRIORITY_CITIES.find(c => q.includes(c.name.toLowerCase()));
        if (matchedCity || q.includes('city') || q.includes('in ')) {{
          const cityName = matchedCity ? matchedCity.name : '';
          const cityMatches = ALL_INSTITUTIONS.filter(i => {{
            if (cityName) return matchC(i.city, cityName);
            return q.includes(i.city.toLowerCase());
          }});

          if (cityMatches.length > 0) {{
            const targetCity = cityMatches[0].city;
            appendCuratorMessage(`
              <div class="flex items-center justify-between gap-2 p-2.5 bg-[#0d1627] border border-[#203254] rounded-xl mb-2">
                <div class="flex items-center gap-2">
                  <span class="text-[18px]">📍</span>
                  <div>
                    <h4 class="font-semibold text-white text-[18px] leading-tight">${{escapeHtml(targetCity)}}</h4>
                    <p class="text-[14px] text-[#60a5fa]">${{cityMatches.length}} Ethically Mapped Sanctuaries</p>
                  </div>
                </div>
                <button class="city-zoom-btn px-3 py-1.5 bg-[#1d4ed8] hover:bg-[#2563eb] text-white text-[14px] rounded-lg transition flex items-center gap-1.5 shadow active:scale-95 cursor-pointer shrink-0" data-city="${{escapeHtml(targetCity)}}">
                  <span>🔍</span> <span>Zoom to ${{escapeHtml(targetCity)}}</span>
                </button>
              </div>
              <p>📍 <strong>Ethical Cultural Guide for ${{escapeHtml(targetCity)}}:</strong></p>
              <p>We have <strong>${{cityMatches.length}}</strong> ethically vetted cultural institutions mapped in <strong>${{escapeHtml(targetCity)}}</strong>. These spaces operate with transparent public funding and verified independence from controversial corporate donors.</p>
              <p class="text-slate-300">Tap <em>Zoom to ${{escapeHtml(targetCity)}}</em> or click any space below to inspect on the 3D globe:</p>
            `, cityMatches.slice(0, 4));

            filterByCity(targetCity, true, false);
            return;
          }}
        }}

        // 7. Specific Country Inquiries
        const matchedCountry = COUNTRY_CENTROIDS.find(c => q.includes(c.name.toLowerCase()) || q.includes(c.name.toLowerCase().replace('united states', 'usa')));
        if (matchedCountry) {{
          const countryMatches = ALL_INSTITUTIONS.filter(i => matchC(i.country, matchedCountry.name));
          if (countryMatches.length > 0) {{
            appendCuratorMessage(`
              <p>🌍 <strong>Ethical Culture in ${{escapeHtml(matchedCountry.name)}}:</strong></p>
              <p>We track <strong>${{countryMatches.length}}</strong> verified cultural spaces in ${{escapeHtml(matchedCountry.name)}}. Funding models here emphasize civic accountability and public grants.</p>
              <p class="text-slate-300">Here are standout institutions worth your journey:</p>
            `, countryMatches.slice(0, 4));

            flyTo(matchedCountry.lon, matchedCountry.lat);
            return;
          }}
        }}

        // 8. Specific Institution Lookup
        const instMatch = ALL_INSTITUTIONS.find(i => q.includes(i.name.toLowerCase()) || (i.aliases && i.aliases.some(a => q.includes(a.toLowerCase()))) || (i.name.toLowerCase().includes(q) && q.length > 3));
        if (instMatch) {{
          appendCuratorMessage(`
            <p><strong>${{escapeHtml(instMatch.name)}}</strong> <span class="text-[#60a5fa] font-mono">· ${{instMatch.location}} (Est. ${{instMatch.year_founded}})</span></p>
            <p><strong>Governance:</strong> ${{instMatch.governance_type}} · <strong>Focus:</strong> ${{instMatch.curatorial_focus}}</p>
            <p><strong>Admission Policy:</strong> ${{instMatch.admission_policy}} — ${{instMatch.admission_details}}</p>
            <p><strong>Ethical Safeguard:</strong> ${{instMatch.ethical_safeguard}}</p>
            
            <!-- Practical Visitor Details Card -->
            <div class="mt-2.5 p-3 rounded-xl bg-[#0b0f19] border border-[#1d273e] text-[14px] space-y-1.5 font-mono">
              <div class="text-emerald-400 font-semibold">🕒 <strong>Hours:</strong> ${{instMatch.opening_hours}}</div>
              <div class="text-[#93c5fd]">🎟️ <strong>Admission:</strong> ${{instMatch.admission_fee}}</div>
              <div class="text-slate-300 font-sans">📍 <strong>Address:</strong> ${{instMatch.address}} (${{instMatch.neighborhood}})</div>
              <div class="text-slate-300 font-sans">🚇 <strong>Transit:</strong> ${{instMatch.transit_tips}}</div>
              <div class="text-amber-300 font-sans">⭐ <strong>Highlight:</strong> ${{instMatch.highlight}}</div>
              <div class="text-slate-400 font-sans">⏱️ <strong>Duration:</strong> ${{instMatch.visit_duration}} · ☕ ${{instMatch.amenities}}</div>
              ${{instMatch.visit_url ? `<a href="${{instMatch.visit_url}}" target="_blank" class="text-[#60a5fa] hover:underline text-[14px] block pt-1 font-mono">Plan Your Visit (Official Museum Guide) ↗</a>` : ''}}
            </div>
            
            ${{instMatch.watch ? `<p class="text-amber-300/90 text-[14px] mt-1.5"><strong>Watch Note:</strong> ${{escapeHtml(instMatch.watch)}}</p>` : ''}}
          `, [instMatch]);

          selectInstitution(instMatch, false);
          return;
        }}

        // 9. Surprise Me / Recommendations
        if (q.includes('surprise') || q.includes('recommend') || q.includes('random') || q.includes('hidden gem')) {{
          const randomA = ALL_INSTITUTIONS.filter(i => i.tier === 'A');
          const pick1 = randomA[Math.floor(Math.random() * randomA.length)];
          const pick2 = randomA[Math.floor(Math.random() * randomA.length)];

          appendCuratorMessage(`
            <p>✨ <strong>Curator's Selected Discoveries:</strong></p>
            <p>Here are two extraordinary institutions with inspiring ethical commitments and artistic integrity:</p>
          `, [pick1, pick2]);

          selectInstitution(pick1, false);
          return;
        }}

        // 10. Fallback with helpful gentle guidance
        const genericPicks = [
          ALL_INSTITUTIONS.find(i => i.name.includes('Dia Beacon')),
          ALL_INSTITUTIONS.find(i => i.name.includes('Chisenhale')),
          ALL_INSTITUTIONS.find(i => i.name.includes('Louisiana'))
        ];

        appendCuratorMessage(`
          <p>I would be delighted to guide you to ethically funded cultural institutions across <strong>35 countries and 133 cities</strong>.</p>
          <p class="text-slate-300">You can ask me questions like:</p>
          <ul class="list-disc pl-4 space-y-1 text-slate-300">
            <li><em>"Which spaces offer always free admission?"</em></li>
            <li><em>"Show me independent artist-run centers"</em></li>
            <li><em>"Where should I go in London, Paris, or Tokyo?"</em></li>
            <li><em>"What makes a museum ethically funded?"</em></li>
            <li><em>"Tell me about Dia Beacon or Louisiana Museum"</em></li>
          </ul>
        `, genericPicks);

      }}, 350);
    }}

    // Handle Input Send
    function handleSend() {{
      const text = curatorInput.value.trim();
      if (!text) return;
      curatorInput.value = '';
      appendUserMessage(text);
      handleCuratorQuery(text);
    }}

    curatorSendBtn.addEventListener('click', handleSend);
    curatorInput.addEventListener('keydown', e => {{
      if (e.key === 'Enter' && !e.shiftKey) {{
        e.preventDefault();
        handleSend();
      }}
    }});

    // Inquiry Chips
    document.querySelectorAll('.inquiry-chip').forEach(btn => {{
      btn.addEventListener('click', () => {{
        const q = btn.getAttribute('data-query');
        const city = btn.getAttribute('data-city');
        if (city) {{
          filterByCity(city, true, false);
        }} else if (q && q.toLowerCase().includes('london')) {{
          filterByCity('London', true, false);
        }}
        if (q) {{
          if (q.toLowerCase().includes('moma')) {{
            openMomaAuditModal();
          }}
          appendUserMessage(q);
          handleCuratorQuery(q);
        }}
      }});
    }});

    // Delegated click listener in chat messages for city zoom buttons & city mentions
    curatorMessages.addEventListener('click', (e) => {{
      const btn = e.target.closest('.city-zoom-btn, .curator-fly-btn, [data-city]');
      if (btn) {{
        const city = btn.getAttribute('data-city');
        if (city) {{
          e.preventDefault();
          e.stopPropagation();
          filterByCity(city, true, false);
          return;
        }}
        const instName = btn.getAttribute('data-name');
        if (instName) {{
          e.preventDefault();
          e.stopPropagation();
          const inst = ALL_INSTITUTIONS.find(i => i.name === instName);
          if (inst) {{
            selectInstitution(inst, true);
          }}
          return;
        }}
      }}

      // Check if user clicked any text or element mentioning London
      const txt = (e.target.textContent || '').trim().toLowerCase();
      if (txt === 'london' || txt.includes('london')) {{
        if (e.target.tagName === 'BUTTON' || e.target.tagName === 'A' || e.target.tagName === 'STRONG' || e.target.closest('button')) {{
          filterByCity('London', true, false);
        }}
      }}
    }});

    // Tab Switching: Curator Guide vs Catalog
    const tabCuratorBtn = document.getElementById('tabCuratorBtn');
    const tabCatalogBtn = document.getElementById('tabCatalogBtn');
    const curatorPanel = document.getElementById('curatorPanel');
    const catalogPanel = document.getElementById('catalogPanel');

    function switchTab(tab) {{
      if (tab === 'curator') {{
        tabCuratorBtn.className = 'flex-1 py-1 px-2.5 rounded-md transition text-center flex items-center justify-center gap-1.5 bg-[#1d4ed8] text-white font-semibold shadow';
        tabCatalogBtn.className = 'flex-1 py-1 px-2.5 rounded-md transition text-center flex items-center justify-center gap-1.5 text-[#94a3b8] hover:text-white';
        curatorPanel.classList.remove('hidden');
        catalogPanel.classList.add('hidden');
      }} else {{
        tabCatalogBtn.className = 'flex-1 py-1 px-2.5 rounded-md transition text-center flex items-center justify-center gap-1.5 bg-[#1d4ed8] text-white font-semibold shadow';
        tabCuratorBtn.className = 'flex-1 py-1 px-2.5 rounded-md transition text-center flex items-center justify-center gap-1.5 text-[#94a3b8] hover:text-white';
        catalogPanel.classList.remove('hidden');
        curatorPanel.classList.add('hidden');
        renderLeftList();
      }}
    }}

    // =========================================================
    // 📱 OPEN / CLOSE & HALF SHEET CONTROLLER
    // =========================================================
    let currentSheetState = 'half';
    const mainAppContainer = document.getElementById('mainAppContainer');
    const sheetCloseBtn = document.getElementById('sheetCloseBtn');
    const sheetOpenBtn = document.getElementById('sheetOpenBtn');
    const sheetClosedBar = document.getElementById('sheetClosedBar');
    const sheetExpandBtn = document.getElementById('sheetExpandBtn');
    const sheetExpandIcon = document.getElementById('sheetExpandIcon');
    const sheetExpandLabel = document.getElementById('sheetExpandLabel');
    const sheetDragHandle = document.getElementById('sheetDragHandle');
    const sheetHeaderBar = document.getElementById('sheetHeaderBar');

    function setChatSheetState(state) {{
      currentSheetState = state;
      if (!mainAppContainer) return;
      mainAppContainer.classList.remove('sheet-closed', 'sheet-half', 'sheet-full');
      mainAppContainer.classList.add(`sheet-${{state}}`);

      if (state === 'full') {{
        if (sheetExpandIcon) sheetExpandIcon.textContent = '⤡';
        if (sheetExpandLabel) sheetExpandLabel.textContent = 'Half';
      }} else {{
        if (sheetExpandIcon) sheetExpandIcon.textContent = '⤢';
        if (sheetExpandLabel) sheetExpandLabel.textContent = 'Full';
      }}

      // Smoothly trigger canvas resize during and after CSS transition
      setTimeout(resizeCanvas, 50);
      setTimeout(resizeCanvas, 160);
      setTimeout(resizeCanvas, 340);
    }}

    sheetCloseBtn?.addEventListener('click', (e) => {{
      e.stopPropagation();
      setChatSheetState('closed');
    }});

    sheetOpenBtn?.addEventListener('click', (e) => {{
      e.stopPropagation();
      setChatSheetState('half');
    }});

    sheetClosedBar?.addEventListener('click', () => {{
      setChatSheetState('half');
    }});

    sheetDragHandle?.addEventListener('click', (e) => {{
      e.stopPropagation();
      if (currentSheetState === 'closed') setChatSheetState('half');
      else if (currentSheetState === 'half') setChatSheetState('closed');
      else setChatSheetState('half');
    }});

    sheetExpandBtn?.addEventListener('click', (e) => {{
      e.stopPropagation();
      if (currentSheetState === 'full') {{
        setChatSheetState('half');
      }} else {{
        setChatSheetState('full');
      }}
    }});

    // Touch Swipe Gesture for Sheet Header
    let touchSheetStartY = 0;
    sheetHeaderBar?.addEventListener('touchstart', (e) => {{
      touchSheetStartY = e.touches[0].clientY;
    }}, {{ passive: true }});

    sheetHeaderBar?.addEventListener('touchend', (e) => {{
      const deltaY = e.changedTouches[0].clientY - touchSheetStartY;
      if (deltaY > 35) {{
        // Dragged down
        if (currentSheetState === 'full') setChatSheetState('half');
        else if (currentSheetState === 'half') setChatSheetState('closed');
      }} else if (deltaY < -35) {{
        // Dragged up
        if (currentSheetState === 'closed') setChatSheetState('half');
        else if (currentSheetState === 'half') setChatSheetState('full');
      }}
    }}, {{ passive: true }});

    // Global aliases
    window.setChatSheetState = setChatSheetState;
    window.setSheetState = setChatSheetState;
    window.setMobileView = function(view) {{
      switchTab(view);
      setChatSheetState('half');
    }};

    tabCuratorBtn.addEventListener('click', () => switchTab('curator'));
    tabCatalogBtn.addEventListener('click', () => switchTab('catalog'));

    // Floating Card Ask Curator button
    document.getElementById('floatingCardAskCurator')?.addEventListener('click', () => {{
      if (selectedInstitution) {{
        switchTab('curator');
        appendUserMessage(`Tell me about ${{selectedInstitution.name}} and its funding`);
        handleCuratorQuery(selectedInstitution.name);
      }}
    }});

    // Settings Modal
    const settingsModal = document.getElementById('curatorSettingsModal');
    document.getElementById('curatorSettingsBtn')?.addEventListener('click', () => {{
      settingsModal.classList.remove('hidden');
      document.getElementById('geminiApiKeyInput').value = geminiApiKey;
    }});
    document.getElementById('closeSettingsModalBtn')?.addEventListener('click', () => {{
      settingsModal.classList.add('hidden');
    }});
    document.getElementById('saveApiKeyBtn')?.addEventListener('click', () => {{
      geminiApiKey = document.getElementById('geminiApiKeyInput').value.trim();
      localStorage.setItem('atlas_gemini_api_key', geminiApiKey);
      document.getElementById('geminiStatusTag').textContent = geminiApiKey ? 'Gemini 2.5 Active' : 'Offline Engine Active';
      settingsModal.classList.add('hidden');
    }});

    // =========================================================
    // 📋 CATALOG LIST & FILTERING ENGINE
    // =========================================================
    const countrySelect = document.getElementById('countrySelect');
    const citySelect = document.getElementById('citySelect');
    const searchInput = document.getElementById('searchInput');
    const clearSearchBtn = document.getElementById('clearSearchBtn');
    const activeFilterBanner = document.getElementById('activeFilterBanner');
    const filterLabel = document.getElementById('filterLabel');
    const filterCount = document.getElementById('filterCount');
    const clearFilterBtn = document.getElementById('clearFilterBtn');
    const listTotalBadge = document.getElementById('listTotalBadge');

    function populateDropdowns() {{
      const countries = [...new Set(ALL_INSTITUTIONS.map(i => i.country).filter(Boolean))].sort();
      countrySelect.innerHTML = `<option value="all">All Countries (${{countries.length}})</option>` + 
        countries.map(c => `<option value="${{c}}">${{c}}</option>`).join('');

      const cities = [...new Set(ALL_INSTITUTIONS.map(i => i.city).filter(Boolean))].sort();
      citySelect.innerHTML = `<option value="all">All Cities (${{cities.length}})</option>` + 
        cities.map(c => `<option value="${{c}}">${{c}}</option>`).join('');
    }}
    populateDropdowns();

    function applyFilters() {{
      filteredList = ALL_INSTITUTIONS.filter(inst => {{
        if (!selectedTierFilter.has(inst.tier)) return false;

        if (selectedCountryFilter !== 'all') {{
          if (!matchC(inst.country, selectedCountryFilter)) return false;
        }}

        if (selectedCityFilter !== 'all') {{
          if (inst.city.toLowerCase() !== selectedCityFilter.toLowerCase()) return false;
        }}

        if (searchQuery) {{
          const q = searchQuery.toLowerCase();
          const matchName = inst.name.toLowerCase().includes(q);
          const matchLoc = inst.location.toLowerCase().includes(q);
          const matchFund = inst.funding.toLowerCase().includes(q);
          const matchFocus = (inst.curatorial_focus || '').toLowerCase().includes(q);
          const matchGov = (inst.governance_type || '').toLowerCase().includes(q);
          if (!matchName && !matchLoc && !matchFund && !matchFocus && !matchGov) return false;
        }}

        return true;
      }});

      listTotalBadge.textContent = `${{filteredList.length}} mapped`;

      if (selectedCityFilter !== 'all' || selectedCountryFilter !== 'all') {{
        activeFilterBanner.classList.remove('hidden');
        const activeName = selectedCityFilter !== 'all' ? selectedCityFilter : selectedCountryFilter;
        filterLabel.textContent = activeName.toUpperCase();
        filterCount.textContent = `(${{filteredList.length}})`;
      }} else {{
        activeFilterBanner.classList.add('hidden');
      }}

      renderLeftList();
    }}

    function renderLeftList() {{
      const container = document.getElementById('institutionsListContainer');
      if (filteredList.length === 0) {{
        container.innerHTML = `
          <div class="text-center py-8 px-4 text-[#64748b] text-[14px]">
            <p class="font-medium text-slate-400">No institutions match this filter.</p>
            <button id="resetFromEmptyBtn" class="mt-3 text-[#3b82f6] hover:underline text-[14px]">Reset filters</button>
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
              <h3 class="font-semibold text-white text-[14px] leading-snug truncate max-w-[220px] sm:max-w-[260px]">${{inst.name}}</h3>
              <span class="text-[14px] font-mono px-1.5 py-0.5 rounded border ${{tierCol}} shrink-0">${{tierName}}</span>
            </div>
            
            <div class="flex items-center gap-1.5 text-[14px] text-[#60a5fa] mt-1 font-mono">
              <span>📍</span> <span class="truncate">${{inst.location}}</span>
              <span class="text-slate-600">·</span>
              <span class="text-slate-400 text-[14px] shrink-0">Est. ${{inst.year_founded}}</span>
            </div>

            <!-- Researcher Tags: Governance & Admission -->
            <div class="flex items-center gap-1.5 text-[14px] font-mono text-[#94a3b8] mt-1.5 flex-wrap">
              <span class="px-1.5 py-0.5 rounded bg-[#101726] border border-[#1c2840] text-[#93c5fd]">🏛️ ${{inst.governance_type}}</span>
              <span class="px-1.5 py-0.5 rounded bg-[#0a1f15] border border-[#143d28] text-emerald-300">🎟️ ${{inst.admission_policy}}</span>
            </div>

            <!-- Quick Visitor Schedule & Pricing Pill -->
            <div class="mt-1.5 flex items-center gap-2 text-[14px] font-mono text-slate-300">
              <span class="truncate">🕒 ${{inst.opening_hours ? inst.opening_hours.split(',')[0] : 'Open Weekly'}}</span>
              <span class="text-slate-600">·</span>
              <span class="text-emerald-400 shrink-0 truncate max-w-[120px]">🎟️ ${{inst.admission_fee ? inst.admission_fee.split('/')[0].trim() : 'Free / Subsidized'}}</span>
            </div>

            <p class="text-[14px] text-slate-300 mt-2 leading-relaxed line-clamp-2">${{inst.curator_recommendation || inst.funding}}</p>
            
            ${{inst.watch ? `
              <div class="mt-2 pt-1.5 border-t border-[#161a26] text-[14px] text-amber-300/80 truncate flex items-center gap-1">
                <span>⚠️</span> <span>${{inst.watch}}</span>
              </div>
            ` : ''}}
            
            <div class="mt-2.5 pt-2 border-t border-[#161b26] flex items-center justify-between">
              <a href="${{inst.website || inst.sources[0]}}" target="_blank" rel="noopener noreferrer" 
                 class="website-pill inline-flex items-center gap-1 text-[14px] font-mono text-[#60a5fa] hover:text-white bg-[#101726] hover:bg-[#1a253c] border border-[#1e2a42] hover:border-[#3b82f6] px-2 py-0.5 rounded transition"
                 onclick="event.stopPropagation()">
                <span>🌐</span>
                <span class="truncate max-w-[120px]">${{displayDomain}}</span>
                <span class="text-[14px]">↗</span>
              </a>
              <span class="text-[14px] text-slate-500 hover:text-slate-300 font-mono">View on Globe →</span>
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
          }}
        }});
      }});
    }}

    function filterByCity(cityName, zoom = true, notifyCurator = true) {{
      selectedCityFilter = cityName;
      selectedCountryFilter = 'all';
      applyFilters();

      const cty = PRIORITY_CITIES.find(c => c.name.toLowerCase() === cityName.toLowerCase());
      const targetZoom = zoom ? baseRadius * 2.5 : null;

      if (cty) {{
        flyTo(cty.lon, cty.lat, targetZoom);
      }} else {{
        const inst = ALL_INSTITUTIONS.find(i => i.city.toLowerCase() === cityName.toLowerCase());
        if (inst) flyTo(inst.lon, inst.lat, targetZoom);
      }}

      if (zoom) {{
        targetRadius = baseRadius * 2.5;
        if (currentSheetState === 'full') {{
          setChatSheetState('half');
        }}
      }}

      // Select top institution in this city
      const cityMatches = ALL_INSTITUTIONS.filter(i => matchC(i.city, cityName));
      if (cityMatches.length > 0) {{
        selectInstitution(cityMatches[0], false);
      }}

      // Notify Curator if triggered from canvas / UI
      if (notifyCurator && cityMatches.length > 0) {{
        appendCuratorMessage(`
          <div class="flex items-center justify-between gap-2 p-2 bg-[#0c1322] border border-[#1e2e4a] rounded-xl mb-2">
            <div>
              <h4 class="font-semibold text-white text-[18px] leading-tight">📍 ${{cityName.toUpperCase()}}</h4>
              <p class="text-[14px] text-[#60a5fa]">${{cityMatches.length}} Ethically Mapped Sanctuaries</p>
            </div>
            <button class="city-zoom-btn px-3 py-1.5 bg-[#1d4ed8] hover:bg-[#2563eb] text-white text-[14px] rounded-lg transition flex items-center gap-1.5 shadow active:scale-95 cursor-pointer shrink-0" data-city="${{escapeHtml(cityName)}}">
              <span>🔍</span> <span>Zoom to ${{escapeHtml(cityName)}}</span>
            </button>
          </div>
          <p>You zoomed in on <strong>${{cityName}}</strong> with ${{cityMatches.length}} mapped institutions. These spaces lead in ethical funding and independent programming.</p>
        `, cityMatches.slice(0, 4));
      }}
    }}

    function filterByCountry(countryName) {{
      selectedCountryFilter = countryName;
      selectedCityFilter = 'all';
      applyFilters();

      const c = COUNTRY_CENTROIDS.find(c => matchC(c.name, countryName));
      if (c) flyTo(c.lon, c.lat);

      // Notify the Curator to give an educational briefing on this country
      const countryMatches = ALL_INSTITUTIONS.filter(i => matchC(i.country, countryName));
      if (countryMatches.length > 0) {{
        appendCuratorMessage(`
          <p>🌍 <strong>${{countryName.toUpperCase()}} Ethical Cultural Institutions:</strong></p>
          <p>Culture Atlas maps ${{countryMatches.length}} spaces across ${{countryName}}. Public grants and community trusts safeguard their curatorial independence.</p>
        `, countryMatches.slice(0, 3));
      }}
    }}

    function clearAllFilters() {{
      selectedCityFilter = 'all';
      selectedCountryFilter = 'all';
      searchQuery = '';
      searchInput.value = '';
      clearSearchBtn.classList.add('hidden');
      selectedTierFilter = new Set(['A', 'B', 'U']);
      document.querySelectorAll('.tier-chip').forEach(btn => {{
        btn.classList.add('bg-[#0c2419]', 'bg-[#0e213b]', 'bg-[#171a24]');
      }});
      countrySelect.value = 'all';
      citySelect.value = 'all';
      applyFilters();
    }}

    // Filter event listeners
    countrySelect.addEventListener('change', e => {{
      selectedCountryFilter = e.target.value;
      selectedCityFilter = 'all';
      citySelect.value = 'all';
      applyFilters();
      if (selectedCountryFilter !== 'all') {{
        filterByCountry(selectedCountryFilter);
      }}
    }});

    citySelect.addEventListener('change', e => {{
      selectedCityFilter = e.target.value;
      selectedCountryFilter = 'all';
      countrySelect.value = 'all';
      applyFilters();
      if (selectedCityFilter !== 'all') {{
        filterByCity(selectedCityFilter);
      }}
    }});

    searchInput.addEventListener('input', e => {{
      searchQuery = e.target.value;
      clearSearchBtn.classList.toggle('hidden', !searchQuery);
      applyFilters();
    }});

    clearSearchBtn.addEventListener('click', () => {{
      searchInput.value = '';
      searchQuery = '';
      clearSearchBtn.classList.add('hidden');
      applyFilters();
    }});

    clearFilterBtn.addEventListener('click', clearAllFilters);

    document.querySelectorAll('.tier-chip').forEach(btn => {{
      btn.addEventListener('click', () => {{
        const tier = btn.getAttribute('data-tier');
        if (selectedTierFilter.has(tier)) {{
          if (selectedTierFilter.size > 1) selectedTierFilter.delete(tier);
        }} else {{
          selectedTierFilter.add(tier);
        }}
        btn.classList.toggle('opacity-50', !selectedTierFilter.has(tier));
        applyFilters();
      }});
    }});

    // Safe view switcher stub for dual-split layout
    function setMobileView(view) {{
      if (view === 'curator') switchTab('curator');
      else if (view === 'catalog') switchTab('catalog');
    }}
    function setSheetState(s) {{}}

    // =========================================================
    // 🌐 CANVAS POINTER & HIT-TESTING (Click City / Country)
    // =========================================================
    canvas.addEventListener('pointerup', e => {{
      isDragging = false;
      canvas.classList.remove('dragging');

      const dt = Date.now() - pointerDownTime;
      const dist = Math.hypot(e.clientX - pointerStartX, e.clientY - pointerStartY);

      if (dt < 300 && dist < 6) {{
        handleGlobeClick(e.clientX, e.clientY);
      }}
    }});

    function handleGlobeClick(clientX, clientY) {{
      const rect = canvas.getBoundingClientRect();
      const mx = clientX - rect.left;
      const my = clientY - rect.top;
      const cx = width / 2;
      const cy = height / 2;
      const r = currentRadius;

      // Check priority city hitboxes
      for (let i = 0; i < cityBadgeHitboxes.length; i++) {{
        const b = cityBadgeHitboxes[i];
        if (mx >= b.x && mx <= b.x + b.w && my >= b.y && my <= b.y + b.h) {{
          if (selectedCityFilter.toLowerCase() === b.name.toLowerCase()) {{
            clearAllFilters();
          }} else {{
            filterByCity(b.name);
          }}
          return;
        }}
      }}

      // Check institution dot
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

    // =========================================================
    // ⚠️ MoMA EXCLUSION AUDIT MODAL CONTROLLER
    // =========================================================
    const momaAuditModal = document.getElementById('momaAuditModal');
    const closeMomaModalBtn = document.getElementById('closeMomaModalBtn');
    const momaAuditFlyNycBtn = document.getElementById('momaAuditFlyNycBtn');
    const momaAuditChatBtn = document.getElementById('momaAuditChatBtn');

    function openMomaAuditModal() {{
      if (momaAuditModal) momaAuditModal.classList.remove('hidden');
      flyTo(-73.9776, 40.7614); // Fly globe smoothly to MoMA NYC coordinates
    }}

    function closeMomaAuditModal() {{
      if (momaAuditModal) momaAuditModal.classList.add('hidden');
    }}

    document.getElementById('openMomaAuditBtn')?.addEventListener('click', (e) => {{
      e.preventDefault();
      e.stopPropagation();
      openMomaAuditModal();
    }});

    closeMomaModalBtn?.addEventListener('click', (e) => {{
      e.stopPropagation();
      closeMomaAuditModal();
    }});

    momaAuditModal?.addEventListener('click', (e) => {{
      if (e.target === momaAuditModal) closeMomaAuditModal();
    }});

    momaAuditFlyNycBtn?.addEventListener('click', () => {{
      closeMomaAuditModal();
      setChatSheetState('half');
      filterByCity('NEW YORK');
    }});

    momaAuditChatBtn?.addEventListener('click', () => {{
      closeMomaAuditModal();
      setChatSheetState('half');
      switchTab('curator');
      appendUserMessage('Why is MoMA excluded from Culture Atlas?');
      handleCuratorQuery('Why is MoMA excluded from Culture Atlas?');
    }});

    // Touch & Pointer Drag for Globe
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
      if (isDragging) {{
        const dx = e.clientX - lastX;
        const dy = e.clientY - lastY;
        lastX = e.clientX;
        lastY = e.clientY;
        rotLon = (rotLon - dx * 0.18) % 360;
        rotLat = Math.max(-75, Math.min(75, rotLat + dy * 0.18));
      }}
    }});

    // Initialize Curator & App
    initCuratorConversation();
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
    print("Wrote researcher-enhanced app/index.html!")

    dest_standalone = "/Users/polinavasilyeva/.gemini/antigravity/scratch/sponsor-atlas/app/standalone.html"
    with open(dest_standalone, "w", encoding="utf-8") as f:
        f.write(html)
    print("Synchronized app/standalone.html!")

    dest_artifact = "/Users/polinavasilyeva/.gemini/antigravity/brain/b997e616-4551-453e-83cc-4ba184f90abf/culture_atlas_app.html"
    with open(dest_artifact, "w", encoding="utf-8") as f:
        f.write(html)
    print("Mirrored to culture_atlas_app.html!")

if __name__ == "__main__":
    build()
