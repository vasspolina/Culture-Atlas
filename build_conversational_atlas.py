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
      display: block;
      width: 100%;
      height: 100%;
      image-rendering: -webkit-optimize-contrast;
    }}
    #globeCanvas.dragging {{
      cursor: grabbing;
    }}
    .custom-scrollbar::-webkit-scrollbar {{
      width: 5px;
      height: 5px;
    }}
    .custom-scrollbar::-webkit-scrollbar-thumb {{
      background: #333333;
      border-radius: 9999px;
    }}
    .custom-scrollbar::-webkit-scrollbar-thumb:hover {{
      background: #444444;
    }}
    .inst-card {{
      transition: all 0.15s ease-in-out;
    }}
    .inst-card.active {{
      border-color: #3b82f6 !important;
      background-color: #222834 !important;
    }}
    
    /* Clean ChatGPT style links */
    .inst-link {{
      font-weight: 500;
      color: #ffffff;
      text-decoration: underline;
      text-underline-offset: 3px;
      text-decoration-color: rgba(255, 255, 255, 0.4);
      transition: all 0.15s ease;
    }}
    .inst-link:hover {{
      color: #60a5fa;
      text-decoration-color: #60a5fa;
    }}
    .city-link {{
      color: #93c5fd;
      text-decoration: underline;
      text-underline-offset: 3px;
      text-decoration-color: rgba(147, 197, 253, 0.35);
      transition: all 0.15s ease;
    }}
    .city-link:hover {{
      color: #bfdbfe;
      text-decoration-color: #bfdbfe;
    }}
    .dossier-link {{
      color: #a1a1aa;
      text-decoration: underline;
      text-underline-offset: 2px;
      text-decoration-color: rgba(161, 161, 170, 0.3);
      transition: all 0.15s ease;
    }}
    .dossier-link:hover {{
      color: #ffffff;
      text-decoration-color: #ffffff;
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
      
      <canvas id="globeCanvas" class="w-full h-full block cursor-grab"></canvas>

      <!-- FLOATING INSTITUTION CARD (Pinned to selected institution with Website Link & Hours) -->
      <div id="floatingCard" class="hidden absolute z-20 pointer-events-auto bg-[#18181b]/95 backdrop-blur-md text-slate-100 rounded-2xl p-3 shadow-2xl transition duration-150 transform -translate-x-1/2 -translate-y-full mb-3 border border-[#2e2e2e] max-w-[310px] sm:max-w-[350px]">
        <div class="flex items-start justify-between gap-2">
          <div class="truncate pr-1">
            <div id="floatingCardTitle" class="font-medium text-[18px] text-white leading-tight truncate"></div>
            <div id="floatingCardMeta" class="text-[14px] text-[#a1a1aa] mt-0.5 flex items-center gap-1 font-mono">
              <span></span>
            </div>
          </div>
          <div class="flex items-center gap-1 shrink-0">
            <span id="floatingCardTier" class="text-[14px] px-2 py-0.5 rounded-lg border border-emerald-900/60 bg-[#0a2016] text-emerald-400">Verified</span>
            <button id="closeFloatingCardBtn" class="text-[#a1a1aa] hover:text-white p-1 rounded-md hover:bg-[#262626] transition text-[14px] leading-none ml-0.5 cursor-pointer" title="Close">✕</button>
          </div>
        </div>

        <div id="floatingCardHours" class="text-[14px] text-emerald-400 mt-1 truncate"></div>

        <div class="mt-2.5 pt-2 border-t border-[#2e2e2e] flex items-center justify-between text-[14px] gap-2">
          <a id="floatingCardWebLink" href="#" target="_blank" rel="noopener noreferrer" 
             class="inline-flex items-center gap-1 text-[#93c5fd] hover:text-white transition cursor-pointer"
             onclick="event.stopPropagation()">
            <span>🌐</span> <span id="floatingCardDomain" class="truncate max-w-[90px]">website</span> <span class="text-[14px]">↗</span>
          </a>
          <div class="flex items-center gap-2">
            <button id="floatingCardDossierBtn" class="text-[#a1a1aa] hover:text-white transition text-[14px] cursor-pointer" onclick="event.stopPropagation()">
              Audit Dossier →
            </button>
            <button id="floatingCardAskCurator" class="inline-flex items-center gap-1 text-white hover:text-[#93c5fd] font-medium transition text-[14px] cursor-pointer" onclick="event.stopPropagation()">
              <span>💬</span> <span>Ask</span>
            </button>
          </div>
        </div>
        <div class="absolute bottom-0 left-1/2 -translate-x-1/2 translate-y-full w-0 h-0 border-x-[6px] border-x-transparent border-t-[6px] border-t-[#18181b]"></div>
      </div>

      <!-- Top-Left Branding Watermark & Tagline -->
      <div class="absolute top-2.5 left-2.5 sm:top-3 sm:left-4 z-10 pointer-events-auto flex items-center gap-2.5 bg-[#171717]/85 backdrop-blur-md px-3 py-1.5 rounded-2xl border border-[#2e2e2e] shadow-md">
        <div class="w-2.5 h-2.5 rounded-full bg-white"></div>
        <div class="flex flex-col">
          <div class="flex items-center gap-2">
            <span class="text-[24px] font-bold tracking-wider text-white uppercase">CULTURE ATLAS</span>
            <span class="text-[14px] text-emerald-400 bg-[#0a2016] px-1.5 py-0.2 rounded-lg border border-emerald-900/60">203 SANCTUARIES</span>
          </div>
          <span class="text-[14px] text-[#a1a1aa] font-normal block leading-tight mt-0.5 truncate max-w-[210px] sm:max-w-none">
            Ethically funded cultural institutions across the world
          </span>
        </div>
      </div>

      <!-- Top-Right Globe Map Controls & Reset -->
      <div class="absolute top-2.5 right-2.5 sm:top-3 sm:right-4 z-10 flex items-center gap-1.5">
        <button id="resetViewBtn" class="bg-[#171717]/90 hover:bg-[#262626] border border-[#2e2e2e] text-[#d4d4d4] hover:text-white px-2.5 py-1 rounded-xl text-[14px] transition flex items-center gap-1 shadow-sm">
          <span>🔄</span> <span class="hidden sm:inline">Reset</span>
        </button>
        <button id="spinBtn" class="bg-[#171717]/90 hover:bg-[#262626] border border-[#2e2e2e] text-[#93c5fd] hover:text-white px-2.5 py-1 rounded-xl text-[14px] transition shadow-sm">
          <span>⟳</span> <span class="hidden sm:inline">Auto-Spin</span>
        </button>
        <button id="zoomInBtn" class="w-7 h-7 sm:w-8 sm:h-8 rounded-xl bg-[#171717]/90 border border-[#2e2e2e] text-[#d4d4d4] hover:text-white flex items-center justify-center transition shadow-sm text-[14px]" title="Zoom In">+</button>
        <button id="zoomOutBtn" class="w-7 h-7 sm:w-8 sm:h-8 rounded-xl bg-[#171717]/90 border border-[#2e2e2e] text-[#d4d4d4] hover:text-white flex items-center justify-center transition shadow-sm text-[14px]" title="Zoom Out">−</button>
      </div>

      <!-- Bottom-Left Map Scale & Attribution -->
      <div class="absolute bottom-2 left-2.5 sm:left-4 z-10 pointer-events-none flex items-center gap-2 text-[14px] text-[#71717a] bg-[#171717]/80 backdrop-blur-sm px-2.5 py-0.5 rounded-lg border border-[#2e2e2e]/60">
        <span>└───┘ 2,000 km</span>
        <span>·</span>
        <span>WGS84 Audited</span>
      </div>

      <!-- Bottom-Right "Why MoMA is Excluded" Button -->
      <div class="absolute bottom-2 right-2.5 sm:right-4 z-10 pointer-events-auto">
        <button id="openMomaAuditBtn" class="text-[14px] font-medium text-[#fcd34d] hover:text-white bg-[#1c1917]/90 hover:bg-[#292218] border border-[#442c11] hover:border-[#f59e0b] px-2.5 py-1 rounded-xl transition flex items-center gap-1.5 shadow-sm">
          <span>⚠️</span> <span>Why MoMA is excluded</span>
        </button>
      </div>

    </div>

    <!-- ========================================================= -->
    <!-- 💬 BOTTOM HALF: CHAT CURATOR & CATALOG (HALF SHEET) -->
    <!-- ========================================================= -->
    <!-- ========================================================= -->
    <!-- 💬 BOTTOM HALF: CHAT CURATOR & CATALOG (HALF SHEET) -->
    <!-- ========================================================= -->
    <div id="bottomChatSection" class="relative w-full h-[50vh] flex flex-col bg-[#171717] overflow-hidden border-t border-[#262626] z-20">
      
      <!-- Sheet Drag Handle & Open/Close Bar -->
      <div id="sheetHeaderBar" class="px-3 py-1.5 sm:px-6 sm:py-2 border-b border-[#262626] bg-[#171717] flex flex-col gap-1 shrink-0 select-none">
        
        <!-- Drag Handle Indicator Pill -->
        <div id="sheetDragHandle" class="w-8 h-1 bg-[#3a3a3a] hover:bg-[#555] rounded-full mx-auto my-0.5 transition cursor-grab active:cursor-grabbing" title="Drag or tap to toggle sheet"></div>

        <!-- 1. Open State Controls Row (Shown when Half or Full) -->
        <div id="sheetOpenControls" class="flex items-center justify-between gap-3">
          
          <!-- Mode Navigation Tabs: Sleek ChatGPT / Apple-style Segmented Control -->
          <div class="flex items-center bg-[#212121] border border-[#2e2e2e] rounded-xl p-0.5 text-[14px]">
            <button id="tabCuratorBtn" class="py-1 px-3 rounded-lg transition text-center flex items-center gap-1.5 bg-[#2f2f2f] text-white font-medium shadow-sm">
              <span>Curator Guide</span>
            </button>
            <button id="tabCatalogBtn" class="py-1 px-3 rounded-lg transition text-center flex items-center gap-1.5 text-[#a1a1aa] hover:text-white">
              <span>Catalog (203)</span>
            </button>
          </div>

          <!-- Right Controls: Status + Settings + Expand/Restore + Close Toggle -->
          <div class="flex items-center gap-2">
            <span id="listTotalBadge" class="hidden sm:inline text-[14px] text-[#71717a] px-2 py-0.5">
              203 mapped
            </span>
            <span id="activeFilterBadge" class="hidden text-[14px] text-[#93c5fd] bg-[#1e293b] border border-[#334155] px-2 py-0.5 rounded-lg flex items-center gap-1">
              <span id="activeFilterText">Filtered</span>
              <button id="clearActiveFilterBtn" class="text-slate-400 hover:text-white ml-0.5">✕</button>
            </span>

            <!-- Live AI / Critical Engine Status & Settings Button -->
            <button id="curatorSettingsBtn" class="flex items-center gap-1.5 px-2.5 py-1 bg-[#212121] hover:bg-[#2a2a2a] border border-[#2e2e2e] text-[#d4d4d4] hover:text-white rounded-xl text-[14px] transition shrink-0 shadow-sm" title="Curator Intelligence Settings & API Status">
              <span id="curatorStatusDot" class="w-2 h-2 rounded-full bg-amber-400"></span>
              <span id="curatorStatusLabel" class="hidden sm:inline font-mono text-[14px]">Offline Engine</span>
              <span class="text-[14px]">⚙️</span>
            </button>

            <!-- Expand / Half Toggle Button -->
            <button id="sheetExpandBtn" class="bg-[#212121] hover:bg-[#2a2a2a] border border-[#2e2e2e] text-[#a1a1aa] hover:text-white px-2 py-1 rounded-lg text-[14px] transition flex items-center gap-1" title="Expand / Restore Sheet">
              <span id="sheetExpandIcon">⤢</span>
              <span id="sheetExpandLabel" class="hidden sm:inline text-[14px]">Full</span>
            </button>

            <!-- Close Sheet Button -->
            <button id="sheetCloseBtn" class="bg-[#212121] hover:bg-[#2a2a2a] border border-[#2e2e2e] text-[#a1a1aa] hover:text-white px-2.5 py-1 rounded-lg text-[14px] transition flex items-center gap-1" title="Close Chat Sheet">
              <span>▼</span>
            </button>
          </div>

        </div>

        <!-- 2. Closed State Bar (Shown when Closed) -->
        <div id="sheetClosedBar" class="hidden flex items-center justify-between gap-2 cursor-pointer py-1">
          <div class="flex items-center gap-2 truncate">
            <span class="w-2 h-2 rounded-full bg-emerald-400"></span>
            <span class="text-[14px] font-medium text-white truncate">Culture Atlas Curator</span>
            <span class="text-[14px] text-[#71717a] hidden sm:inline truncate">· 203 Sanctuaries Mapped</span>
          </div>

          <div class="flex items-center gap-2 shrink-0">
            <button id="sheetOpenBtn" class="px-3 py-1 bg-[#2f2f2f] hover:bg-[#383838] border border-[#3e3e3e] text-white text-[14px] font-medium rounded-xl transition shadow-sm flex items-center gap-1.5">
              <span>▲</span>
              <span>Open Chat</span>
            </button>
          </div>
        </div>

      </div>

      <!-- VIEW A: 💬 CURATOR CONVERSATIONAL EXPERIENCE (Default in Bottom Half) -->
      <div id="curatorPanel" class="flex-1 flex flex-col min-h-0 overflow-hidden bg-[#171717]">
        
        <!-- Scrollable Conversation Feed -->
        <div id="curatorMessages" class="flex-1 overflow-y-auto custom-scrollbar p-3 sm:p-5 space-y-4 max-w-3xl mx-auto w-full">
          <!-- Messages injected dynamically -->
        </div>

        <!-- Typing Indicator -->
        <div id="curatorTyping" class="hidden max-w-3xl mx-auto w-full px-4 sm:px-6 py-2 text-[14px] text-[#8e8e8e] flex items-center gap-2">
          <div class="w-6 h-6 rounded-full bg-[#262626] border border-[#383838] flex items-center justify-center text-[14px] shrink-0">🏛️</div>
          <span class="inline-flex gap-1.5 items-center pl-1">
            <span class="w-2 h-2 rounded-full bg-[#a1a1aa] typing-dot"></span>
            <span class="w-2 h-2 rounded-full bg-[#a1a1aa] typing-dot"></span>
            <span class="w-2 h-2 rounded-full bg-[#a1a1aa] typing-dot"></span>
          </span>
        </div>

        <!-- Sleek OpenAI ChatGPT-style Prompt Suggestions -->
        <div id="curatorInquiryRow" class="max-w-3xl mx-auto w-full px-3 sm:px-6 py-1.5 flex items-center gap-2 overflow-x-auto custom-scrollbar shrink-0 text-[14px] whitespace-nowrap">
          <button class="inquiry-chip px-3 py-1 rounded-full border border-[#2f2f2f] bg-[#212121] text-[#d4d4d4] hover:bg-[#2b2b2b] hover:text-white transition active:scale-95 flex items-center gap-1.5" data-query="Tell me about London's art scene, independent spaces, and divestment history" data-city="London">
            <span>London art scene</span>
          </button>
          <button class="inquiry-chip px-3 py-1 rounded-full border border-[#2f2f2f] bg-[#212121] text-[#d4d4d4] hover:bg-[#2b2b2b] hover:text-white transition active:scale-95 flex items-center gap-1.5" data-query="What is Beyond Objecthood and how did the exhibition become a critical form?">
            <span>Beyond Objecthood</span>
          </button>
          <button class="inquiry-chip px-3 py-1 rounded-full border border-[#2f2f2f] bg-[#212121] text-[#d4d4d4] hover:bg-[#2b2b2b] hover:text-white transition active:scale-95 flex items-center gap-1.5" data-query="What does e-flux say about the museum as a factory and duty-free art?">
            <span>e-flux: Museum as factory</span>
          </button>
          <button class="inquiry-chip px-3 py-1 rounded-full border border-[#2f2f2f] bg-[#212121] text-[#d4d4d4] hover:bg-[#2b2b2b] hover:text-white transition active:scale-95 flex items-center gap-1.5" data-query="Explain the three waves of institutional critique from Hans Haacke to Nan Goldin and Strike MoMA">
            <span>3 Waves of Critique</span>
          </button>
          <button class="inquiry-chip px-3 py-1 rounded-full border border-[#2f2f2f] bg-[#212121] text-[#d4d4d4] hover:bg-[#2b2b2b] hover:text-white transition active:scale-95 flex items-center gap-1.5" data-query="Why is MoMA excluded from Culture Atlas?">
            <span>Why MoMA is excluded</span>
          </button>
          <button class="inquiry-chip px-3 py-1 rounded-full border border-[#2f2f2f] bg-[#212121] text-[#d4d4d4] hover:bg-[#2b2b2b] hover:text-white transition active:scale-95 flex items-center gap-1.5" data-query="Which cultural spaces offer always free admission?">
            <span>Free admission</span>
          </button>
        </div>
        <div class="p-2 sm:p-3 bg-[#171717] shrink-0 border-t border-[#222222]">
          <div class="max-w-3xl mx-auto w-full">
            <div class="relative flex items-center bg-[#212121] border border-[#333333] hover:border-[#444] focus-within:border-[#555] rounded-3xl p-1.5 pl-4 pr-1.5 shadow-md transition">
              <input 
                type="text" 
                id="curatorInput" 
                placeholder="Message Culture Atlas Curator..." 
                class="w-full bg-transparent border-0 text-[14px] text-white placeholder-[#71717a] focus:outline-none py-1.5 font-sans"
              />
              <button 
                id="curatorSendBtn" 
                class="w-8 h-8 rounded-full bg-white text-black hover:bg-neutral-200 transition active:scale-95 flex items-center justify-center shrink-0 shadow-sm ml-1.5 opacity-60"
                title="Send message"
              >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M12 19V5M5 12l7-7 7 7"/>
                </svg>
              </button>
            </div>
            <div class="text-center text-[14px] text-[#666] pt-1 select-none">
              Culture Atlas verifies governance independence and public trust.
            </div>
          </div>
        </div>

      </div>

      <!-- VIEW B: 📋 RESEARCH CATALOG (When toggled to Catalog in Bottom Half) -->
      <div id="catalogPanel" class="hidden flex-1 flex flex-col min-h-0 overflow-hidden bg-[#171717]">
        
        <div class="p-3 border-b border-[#262626] bg-[#171717] flex flex-col gap-2.5 shrink-0 max-w-3xl mx-auto w-full">
          <!-- Active Filter Banner (When city/country clicked) -->
          <div id="activeFilterBanner" class="hidden flex items-center justify-between bg-[#212121] border border-[#333] px-3 py-1.5 rounded-xl text-[14px]">
            <div class="flex items-center gap-2 truncate">
              <span id="filterIcon" class="text-[14px]">📍</span>
              <span id="filterLabel" class="font-medium text-white truncate">NEW YORK</span>
              <span id="filterCount" class="text-[#93c5fd] text-[14px]">(11)</span>
            </div>
            <button id="clearFilterBtn" class="text-[14px] text-[#a1a1aa] hover:text-white px-2 py-0.5 rounded-lg hover:bg-[#2e2e2e] transition ml-2 flex items-center gap-1">
              <span>Clear</span> <span>✕</span>
            </button>
          </div>

          <!-- Search Input: Clean ChatGPT-style search bar -->
          <div class="relative">
            <input 
              type="text" 
              id="searchInput" 
              placeholder="Search museum, city, curatorial focus, or governance..." 
              class="w-full bg-[#212121] border border-[#333333] text-[14px] text-white placeholder-[#71717a] px-3.5 py-2 rounded-xl focus:outline-none focus:border-[#555] transition shadow-sm"
            />
            <button id="clearSearchBtn" class="hidden absolute right-3 top-2 text-[#71717a] hover:text-white text-[14px]">✕</button>
          </div>

          <!-- Quick Filters: Country & City Dropdowns -->
          <div class="grid grid-cols-2 gap-2 text-[14px]">
            <select id="countrySelect" class="bg-[#212121] border border-[#333333] text-[#e4e4e7] px-3 py-1.5 rounded-xl focus:outline-none focus:border-[#555] truncate">
              <option value="all">All Countries (35)</option>
            </select>
            <select id="citySelect" class="bg-[#212121] border border-[#333333] text-[#e4e4e7] px-3 py-1.5 rounded-xl focus:outline-none focus:border-[#555] truncate">
              <option value="all">All Cities (133)</option>
            </select>
          </div>

          <!-- Tier Quick Chips: Clean, understated neutral pills with gentle indicators -->
          <div class="flex items-center gap-2 text-[14px]">
            <button class="tier-chip flex-1 py-1.5 px-2 rounded-xl border border-[#333333] bg-[#212121] text-[#a1a1aa] hover:text-white hover:bg-[#282828] text-center transition flex items-center justify-center gap-1.5" data-tier="A">
              <span class="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
              <span>Tier A (135)</span>
            </button>
            <button class="tier-chip flex-1 py-1.5 px-2 rounded-xl border border-[#333333] bg-[#212121] text-[#a1a1aa] hover:text-white hover:bg-[#282828] text-center transition flex items-center justify-center gap-1.5" data-tier="B">
              <span class="w-1.5 h-1.5 rounded-full bg-blue-400"></span>
              <span>Tier B (52)</span>
            </button>
            <button class="tier-chip flex-1 py-1.5 px-2 rounded-xl border border-[#333333] bg-[#212121] text-[#a1a1aa] hover:text-white hover:bg-[#282828] text-center transition flex items-center justify-center gap-1.5" data-tier="U">
              <span class="w-1.5 h-1.5 rounded-full bg-slate-400"></span>
              <span>Tier U (16)</span>
            </button>
          </div>
        </div>

        <!-- Scrollable Institutions Feed -->
        <div id="institutionsListContainer" class="flex-1 overflow-y-auto custom-scrollbar p-3 sm:p-4 space-y-2 max-w-3xl mx-auto w-full pb-8">
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

  <!-- ⚙️ CURATOR INTELLIGENCE SETTINGS MODAL (Multi-Provider API Support) -->
  <!-- ========================================================================= -->
  <div id="curatorSettingsModal" class="hidden fixed inset-0 z-50 bg-black/85 backdrop-blur-md flex items-center justify-center p-4">
    <div class="bg-[#18181b] border border-[#2e2e2e] rounded-3xl max-w-lg w-full p-6 shadow-2xl flex flex-col gap-4 max-h-[92vh] overflow-y-auto custom-scrollbar">
      
      <!-- Modal Header -->
      <div class="flex items-center justify-between border-b border-[#2e2e2e] pb-3 shrink-0">
        <div class="flex items-center gap-2.5">
          <span class="text-[24px]">🏛️</span>
          <div>
            <h3 class="font-medium text-white text-[18px]">Curator Intelligence Settings</h3>
            <p class="text-[14px] text-[#a1a1aa]">Power conversational reasoning with live AI or use the built-in critical engine</p>
          </div>
        </div>
        <button id="closeSettingsModalBtn" class="text-[#a1a1aa] hover:text-white text-[18px] p-1.5 hover:bg-[#262626] rounded-xl transition">✕</button>
      </div>

      <!-- Provider Tabs -->
      <div class="space-y-1.5">
        <label class="block text-[14px] text-[#a1a1aa] font-medium">AI Intelligence Provider</label>
        <div class="grid grid-cols-3 gap-2">
          <button id="providerClaudeBtn" class="provider-tab-btn py-2 px-3 rounded-xl border border-[#3e3e3e] bg-[#27272a] text-white text-[14px] font-medium flex items-center justify-center gap-1.5 transition active:scale-95">
            <span>🟣</span> <span>Claude</span>
          </button>
          <button id="providerOpenAIBtn" class="provider-tab-btn py-2 px-3 rounded-xl border border-[#27272a] bg-[#1f1f23] text-[#a1a1aa] hover:text-white text-[14px] font-medium flex items-center justify-center gap-1.5 transition active:scale-95">
            <span>🟢</span> <span>OpenAI</span>
          </button>
          <button id="providerGeminiBtn" class="provider-tab-btn py-2 px-3 rounded-xl border border-[#27272a] bg-[#1f1f23] text-[#a1a1aa] hover:text-white text-[14px] font-medium flex items-center justify-center gap-1.5 transition active:scale-95">
            <span>🔵</span> <span>Gemini</span>
          </button>
        </div>
        <div id="providerTip" class="text-[14px] text-[#a1a1aa] pt-1">
          Recommended: <strong>Claude 3.5 / Haiku 4.5</strong> excels at art theory, <em>Beyond Objecthood</em>, e-flux criticism, and nuanced institutional analysis.
        </div>
      </div>

      <!-- API Key Input -->
      <div class="space-y-1.5">
        <div class="flex items-center justify-between">
          <label class="block text-[14px] text-[#a1a1aa] font-medium">API Key</label>
          <span id="keyDetectBadge" class="text-[14px] font-mono text-[#a1a1aa]">Auto-detecting provider...</span>
        </div>
        <div class="relative flex items-center">
          <input 
            type="password" 
            id="aiApiKeyInput" 
            placeholder="Paste sk-ant-... or sk-... or AIzaSy..." 
            class="w-full bg-[#212121] border border-[#333333] text-[14px] text-white px-3.5 py-2.5 rounded-xl focus:outline-none focus:border-[#60a5fa] transition font-mono pr-10"
          />
          <button id="toggleKeyVisibilityBtn" class="absolute right-3 text-[#71717a] hover:text-white text-[14px] p-1" title="Toggle visibility">👁️</button>
        </div>
        <div class="text-[14px] text-[#71717a] flex items-center justify-between">
          <span>Tip: You can also paste your API key straight into the chat box anytime!</span>
        </div>
      </div>

      <!-- Model Selector -->
      <div class="space-y-1.5">
        <label class="block text-[14px] text-[#a1a1aa] font-medium">Model</label>
        <select id="aiModelSelect" class="w-full bg-[#212121] border border-[#333333] text-white text-[14px] px-3.5 py-2 rounded-xl focus:outline-none focus:border-[#60a5fa] transition font-mono">
          <option value="claude-haiku-4-5-20251001">claude-haiku-4-5-20251001 (Fast & Articulate - Recommended)</option>
          <option value="claude-sonnet-4-5-20250929">claude-sonnet-4-5-20250929 (Deep Critical Reasoning)</option>
        </select>
      </div>

      <!-- Connection Test Status Box -->
      <div id="connectionTestBox" class="hidden p-3 rounded-xl text-[14px] border flex items-center gap-2">
        <span id="testStatusIcon">⏳</span>
        <span id="testStatusMsg" class="font-mono">Testing connection...</span>
      </div>

      <!-- Privacy Assurance -->
      <div class="p-3 bg-[#212121] border border-[#2e2e2e] rounded-xl text-[14px] text-[#a1a1aa] leading-relaxed">
        <p>
          🔒 <strong>100% Client-Side Privacy:</strong> Your key is saved strictly in your local browser's <code class="text-white font-mono text-[14px]">localStorage</code>. Requests are sent directly from your browser to the provider's API. No intermediate backend logs your keys.
        </p>
      </div>

      <!-- Action Buttons -->
      <div class="flex flex-col sm:flex-row items-center justify-between gap-2.5 pt-2 border-t border-[#2e2e2e]">
        <div class="flex items-center gap-2 w-full sm:w-auto">
          <button id="testConnectionBtn" class="px-3.5 py-2 bg-[#27272a] hover:bg-[#333338] border border-[#3e3e3e] text-white text-[14px] rounded-xl transition flex-1 sm:flex-initial">
            Test Connection
          </button>
          <button id="clearApiKeyBtn" class="px-3 py-2 text-[#f87171] hover:bg-rose-500/10 rounded-xl text-[14px] transition flex-1 sm:flex-initial">
            Disconnect
          </button>
        </div>
        <button id="saveApiKeyBtn" class="w-full sm:w-auto px-5 py-2 bg-white hover:bg-neutral-200 text-black text-[14px] font-medium rounded-xl transition shadow-sm">
          Save & Connect
        </button>
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
    let selectedInstitution = null;
    let hoveredInstitution = null;
    let hoveredCity = null;
    let hoveredCountry = null;

    // Canvas & 3D Math Setup with Native Retina / High-DPI Support
    const canvas = document.getElementById('globeCanvas');
    const ctx = canvas.getContext('2d', {{ alpha: false }});
    
    let dpr = Math.max(1, Math.min(window.devicePixelRatio || 1, 3));
    let width = 800;
    let height = 600;

    function getBaseRadius() {{
      const minDim = Math.min(width, height);
      return window.innerWidth < 768 ? Math.max(120, minDim * 0.38) : Math.max(160, minDim * 0.33);
    }}
    let baseRadius = 200;
    let currentRadius = baseRadius;
    let targetRadius = baseRadius;

    function getMinRadius() {{ return baseRadius * 0.7; }}
    function getMaxRadius() {{ return baseRadius * 7.0; }}

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
      const rect = canvas.parentElement.getBoundingClientRect();
      dpr = Math.max(1, Math.min(window.devicePixelRatio || 1, 3));
      
      width = Math.round(rect.width) || canvas.parentElement.clientWidth || 800;
      height = Math.round(rect.height) || canvas.parentElement.clientHeight || 600;

      // Double/triple buffer dimensions for razor-sharp Retina displays
      canvas.width = Math.round(width * dpr);
      canvas.height = Math.round(height * dpr);

      // Logical layout display dimensions
      canvas.style.width = width + 'px';
      canvas.style.height = height + 'px';

      baseRadius = getBaseRadius();
      targetRadius = Math.max(getMinRadius(), Math.min(getMaxRadius(), targetRadius));
    }}
    resizeCanvas();
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
      // Scale coordinates to high-DPI hardware buffer for crystal-clear Retina rendering
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      ctx.clearRect(0, 0, width, height);
      ctx.imageSmoothingEnabled = true;
      ctx.imageSmoothingQuality = 'high';

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
      ctx.strokeStyle = '#223048';
      ctx.lineWidth = 1.2;
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
            ctx.strokeStyle = isCActive ? '#60a5fa' : '#050c18';
            ctx.lineWidth = isCActive ? 2.0 : 0.75;
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

    function deselectInstitution() {{
      selectedInstitution = null;
      const floatingCard = document.getElementById('floatingCard');
      if (floatingCard) floatingCard.classList.add('hidden');
      document.querySelectorAll('.inst-card').forEach(c => c.classList.remove('active'));
    }}

    function selectInstitution(inst, shouldSwitchToGlobe = false) {{
      if (!inst) {{
        deselectInstitution();
        return;
      }}
      selectedInstitution = inst;
      document.getElementById('floatingCardTitle').textContent = inst.name;
      document.getElementById('floatingCardMeta').textContent = `${{inst.location}} · ${{inst.tier === 'A' ? 'Verified' : 'One Name'}}`;
      
      const tierBadge = document.getElementById('floatingCardTier');
      if (tierBadge) {{
        tierBadge.textContent = inst.tier === 'A' ? 'Verified' : inst.tier === 'B' ? 'One Name' : 'Unverified';
        tierBadge.className = 'text-[14px] font-mono px-1.5 py-0.5 rounded border shrink-0 ' + 
          (inst.tier === 'A' ? 'text-emerald-400 border-emerald-900 bg-[#0a2016]' : 'text-blue-400 border-blue-900 bg-[#0d1d33]');
      }}
      
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

      const zoomTarget = shouldSwitchToGlobe ? Math.max(targetRadius, baseRadius * 4.2) : targetRadius;
      if (shouldSwitchToGlobe) {{
        targetRadius = zoomTarget;
        if (currentSheetState === 'full') setChatSheetState('half');
      }}
      flyTo(inst.lon, inst.lat, zoomTarget);

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

    // Unified Multi-Provider AI State & Local Storage
    let aiApiKey = localStorage.getItem('atlas_ai_api_key') || localStorage.getItem('atlas_gemini_api_key') || '';
    let aiProvider = localStorage.getItem('atlas_ai_provider') || 'auto';
    let aiModel = localStorage.getItem('atlas_ai_model') || '';

    function detectProvider(key) {{
      if (!key) return null;
      const k = key.trim();
      if (k.startsWith('sk-ant-')) return 'anthropic';
      if (k.startsWith('AIza')) return 'gemini';
      if (k.startsWith('sk-') || k.startsWith('sk-proj-')) return 'openai';
      return 'anthropic';
    }}

    function getEffectiveProvider() {{
      if (aiProvider && aiProvider !== 'auto') return aiProvider;
      return detectProvider(aiApiKey) || 'anthropic';
    }}

    function getEffectiveModel() {{
      if (aiModel) return aiModel;
      const p = getEffectiveProvider();
      if (p === 'anthropic') return 'claude-haiku-4-5-20251001';
      if (p === 'openai') return 'gpt-4o-mini';
      if (p === 'gemini') return 'gemini-2.5-flash';
      return 'claude-haiku-4-5-20251001';
    }}

    function updateAIStatusUI() {{
      const dot = document.getElementById('curatorStatusDot');
      const label = document.getElementById('curatorStatusLabel');
      if (!dot || !label) return;
      if (aiApiKey) {{
        const prov = getEffectiveProvider();
        const pName = prov === 'anthropic' ? 'Claude' : (prov === 'openai' ? 'OpenAI' : 'Gemini');
        dot.className = 'w-2 h-2 rounded-full bg-emerald-400 animate-pulse';
        label.textContent = `${{pName}} Live`;
        label.className = 'hidden sm:inline font-mono text-[14px] text-emerald-400';
      }} else {{
        dot.className = 'w-2 h-2 rounded-full bg-amber-400';
        label.textContent = 'Critical Engine';
        label.className = 'hidden sm:inline font-mono text-[14px] text-[#a1a1aa]';
      }}
    }}

    // Initial Welcome Message with Gentle Education
    function initCuratorConversation() {{
      curatorMessages.innerHTML = '';
      appendCuratorMessage(`
        <p class="text-[#ececec]">
          Welcome to <strong>Culture Atlas</strong>. In an era where major art institutions routinely rely on trustees and sponsors linked to fossil fuel extraction, defense manufacturing, or predatory finance, Culture Atlas was created to map <strong>203 cultural sanctuaries across 35 countries</strong> that protect curatorial independence and public trust.
        </p>
        <p class="text-[#d4d4d4]">
          We highlight four ethical models: <strong>civic municipal sanctuaries</strong> supported by public arts councils, <strong>artist-run grassroots Kunsthalles</strong> with creative autonomy, institutions that actively <strong>divested from fossil fuels</strong>, and spaces offering <strong>free public admission</strong> as a fundamental civic right.
        </p>
        <p class="text-[#d4d4d4]">
          For example, you can discover <a href="#" class="inst-link" data-name="Chisenhale Gallery">Chisenhale Gallery</a> in <a href="#" class="city-link" data-city="London">London</a> (an artist-centered commissioning space with free entry), <a href="#" class="inst-link" data-name="CAPC musée d'art contemporain de Bordeaux">CAPC</a> in <a href="#" class="city-link" data-city="Bordeaux">Bordeaux</a> (a civic contemporary Kunsthalle in an 1824 warehouse), or <a href="#" class="inst-link" data-name="Dia Beacon">Dia Beacon</a> in <a href="#" class="city-link" data-city="New York">New York</a> (a model of non-profit foundation endowment for monumental site-specific art).
        </p>
        <p class="text-[#93c5fd]">
          Where in the world are you exploring, or what type of art experience would you love to discover today?
        </p>
      `);
    }}

    function appendUserMessage(text) {{
      const div = document.createElement('div');
      div.className = 'flex justify-end my-1';
      div.innerHTML = `
        <div class="max-w-[80%] bg-[#2f2f2f] text-[#ececec] text-[14px] px-4 py-2.5 rounded-3xl shadow-sm leading-relaxed whitespace-pre-wrap select-text">
          ${{escapeHtml(text)}}
        </div>
      `;
      curatorMessages.appendChild(div);
      curatorMessages.scrollTop = curatorMessages.scrollHeight;
    }}

    function appendCuratorMessage(htmlContent) {{
      const div = document.createElement('div');
      div.className = 'flex items-start gap-3 my-2 select-text';

      div.innerHTML = `
        <div class="w-7 h-7 rounded-full bg-[#262626] border border-[#383838] flex items-center justify-center text-[14px] text-white shrink-0 mt-0.5 select-none" title="Culture Atlas Curator">
          🏛️
        </div>
        <div class="flex-1 min-w-0 text-[14px] text-[#ececec] leading-relaxed space-y-3 pt-0.5">
          ${{htmlContent}}
        </div>
      `;
      curatorMessages.appendChild(div);

      // Direct event binding on inline links for immediate responsiveness
      div.querySelectorAll('.inst-link').forEach(link => {{
        link.addEventListener('click', (e) => {{
          e.preventDefault();
          e.stopPropagation();
          const name = link.getAttribute('data-name');
          const inst = ALL_INSTITUTIONS.find(i => i.name === name);
          if (inst) selectInstitution(inst, true);
        }});
      }});

      div.querySelectorAll('.dossier-link').forEach(link => {{
        link.addEventListener('click', (e) => {{
          e.preventDefault();
          e.stopPropagation();
          const name = link.getAttribute('data-name');
          const inst = ALL_INSTITUTIONS.find(i => i.name === name);
          if (inst) openDossier(inst);
        }});
      }});

      div.querySelectorAll('.city-link').forEach(link => {{
        link.addEventListener('click', (e) => {{
          e.preventDefault();
          e.stopPropagation();
          const city = link.getAttribute('data-city');
          if (city) filterByCity(city, true, false);
        }});
      }});

      div.querySelectorAll('.prompt-link').forEach(link => {{
        link.addEventListener('click', (e) => {{
          e.preventDefault();
          e.stopPropagation();
          const q = link.getAttribute('data-prompt') || link.textContent.trim().replace(/^["']|["']$/g, '');
          if (q) {{
            appendUserMessage(q);
            handleCuratorQuery(q);
          }}
        }});
      }});

      curatorMessages.scrollTop = curatorMessages.scrollHeight;
    }}

    function escapeHtml(str) {{
      return (str || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
    }}

    function formatInstLink(inst, opts = {{}}) {{
      if (!inst) return '';
      const webUrl = inst.website || (inst.sources && inst.sources[0]) || '';
      let domain = 'website';
      try {{ domain = new URL(webUrl).hostname.replace(/^www\\./, ''); }} catch(e) {{}}
      
      const nameLink = `<a href="#" class="inst-link" data-name="${{escapeHtml(inst.name)}}">${{escapeHtml(inst.name)}}</a>`;
      const cityPart = opts.noCity ? '' : ` in <a href="#" class="city-link" data-city="${{escapeHtml(inst.city)}}">${{escapeHtml(inst.location || inst.city)}}</a>`;
      const dossierPart = opts.noDossier ? '' : ` (<a href="#" class="dossier-link text-[14px]" data-name="${{escapeHtml(inst.name)}}">audit dossier</a>${{webUrl ? ` · <a href="${{webUrl}}" target="_blank" rel="noopener noreferrer" class="dossier-link text-[14px]">${{domain}} ↗</a>` : ''}})`;
      
      return `${{nameLink}}${{cityPart}}${{dossierPart}}`;
    }}

        // Unified Multi-Provider Live Generative AI Engine (Claude, OpenAI, Gemini)
    async function queryAI(userPrompt) {{
      if (!aiApiKey) return null;
      const prov = getEffectiveProvider();
      const model = getEffectiveModel();

      // Sample representative sanctuaries for model grounding
      const sampleInsts = ALL_INSTITUTIONS.slice(0, 45).map(i => `${{i.name}} (${{i.city}}, ${{i.country}}): Tier ${{i.tier}}, ${{i.governance_type}}, Hours: ${{i.opening_hours}}, ${{i.admission_policy}}, Highlights: ${{i.highlight}}`).join('\\n');

      const criticalSystemPrompt = `You are the Culture Atlas Curator, an erudite, warm, and articulate contemporary art scholar and guide to ethical cultural institutions worldwide.
Culture Atlas maps 203 cultural sanctuaries across 35 countries that protect curatorial independence and reject underwriting from fossil fuels, defense/weapons manufacturing, and private prisons.

DEEP THEORETICAL & INSTITUTIONAL FOUNDATIONS:
You are deeply grounded in institutional critique, contemporary art theory, and critical exhibition history:
- 'Beyond Objecthood: The Exhibition as a Critical Form Since 1968' by James Voorhies (MIT Press, 2017): You trace how artists from 1968 onwards (Robert Smithson, Marcel Broodthaers, Michael Asher, Group Material, Fred Wilson, Maria Eichhorn, Philippe Parreno, Tino Sehgal) subverted Michael Fried's 1967 condemnation of 'theatricality' in 'Art and Objecthood', transforming the exhibition itself into the primary artistic medium and critical form. You understand the contemporary paradox: how corporate mega-museums co-opted participatory and relational practices into tourist entertainment spectacle, and why independent kunsthalles and artist-run spaces remain essential counter-publics.
- 'e-flux journal' Critical Theory:
  * Hito Steyerl: 'Is a Museum a Factory?' (the museum as a post-Fordist site of unpaid spectator labor), 'Politics of Art: Contemporary Art and the Transition to Post-Democracy', and 'Duty Free Art' (freeports in Geneva and Singapore as offshore tax shelters where art circulates as financialized speculative currency).
  * Boris Groys: 'Art Workers: Between Utopia and the Archive', 'The Museum as a Cradle of Revolution', and the museum's role as a secular egalitarian archive preserving artworks beyond capitalist market obsolescence.
  * Anton Vidokle & Julieta Aranda: 'Art Without Artists?' (critique of the sovereign super-curator displacing the artist) and Russian Cosmism.
  * Martha Rosler: 'Culture Class: Art, Creativity, Urbanism' (gentrification and artists as the advance guard of real estate capital).
- Three Waves of Institutional Critique:
  * 1st Wave (Late 1960s–70s): Hans Haacke (MoMA Poll 1970; Shapolsky real estate censorship at the Guggenheim 1971), Michael Asher, Daniel Buren, Marcel Broodthaers.
  * 2nd Wave (1980s–90s): Andrea Fraser ('From the Critique of Institutions to an Institution of Critique', '2016 in Museums, Money, and Politics'), Fred Wilson ('Mining the Museum' 1992), Guerrilla Girls.
  * 3rd Wave / Activist Divestment (2010s–Present): Decolonize This Place, Strike MoMA (Leon Black, Larry Fink, Steven Tananbaum, Paula Crown), Nan Goldin & P.A.I.N. (stripping the Sackler name from the Met, Louvre, Guggenheim, Tate, Serpentine), BP or not BP? & Culture Unstained (ousting BP from Tate and National Portrait Gallery), Warren Kanders Whitney Biennial tear gas boycott.
- Claire Bishop: 'Radical Museology' (dialectical collection display vs presentist corporate spectacle; Van Abbemuseum, Reina Sofía) and 'Artificial Hells'.
- Pamela M. Lee: 'Forgetting the Art World' (globalization and logistical capitalism).

CRITICAL FORMATTING & CONVERSATIONAL RULES:
1. Write in warm, articulate, continuous conversational paragraphs. DO NOT produce bulleted lists, numbered items, tables, or generic boxed UI recommendation containers.
2. Weave all institutional and city references strictly IN LINE within your natural sentences.
3. When referencing an institution in our atlas, format it strictly as:
<a href="#" class="inst-link font-semibold text-white hover:text-[#60a5fa] underline cursor-pointer" data-name="Exact Name">Exact Name</a> in <a href="#" class="city-link text-[#93c5fd] hover:underline cursor-pointer" data-city="City">City</a> (<a href="#" class="dossier-link text-slate-400 hover:text-white underline font-mono text-[14px] cursor-pointer" data-name="Exact Name">audit dossier</a>)
4. When mentioning a city, link it as: <a href="#" class="city-link text-[#93c5fd] hover:underline cursor-pointer" data-city="City">City</a>.
5. If the user asks about an art scene (e.g. London, New York, Berlin, Paris), provide an intellectual, historical, and curatorial narrative exploring its critical tensions, funding governance (e.g. Arts Council England, DRAC), and highlight specific independent sanctuaries from our atlas.
6. Never output markdown headers (#, ##) or structured database field labels like 'Address:', 'Hours:', 'Highlight:'. Speak in fluid, natural prose as an inspiring curator and theorist.`;

      try {{
        let rawText = '';
        if (prov === 'anthropic') {{
          const res = await fetch('https://api.anthropic.com/v1/messages', {{
            method: 'POST',
            headers: {{
              'Content-Type': 'application/json',
              'x-api-key': aiApiKey,
              'anthropic-version': '2023-06-01',
              'anthropic-dangerous-direct-browser-access': 'true'
            }},
            body: JSON.stringify({{
              model: model,
              max_tokens: 1024,
              system: criticalSystemPrompt,
              messages: [
                {{ role: 'user', content: `Atlas sample:\\n${{sampleInsts}}\\n\\nUser question: ${{userPrompt}}` }}
              ]
            }})
          }});
          if (!res.ok) throw new Error(`Anthropic error ${{res.status}}`);
          const data = await res.json();
          rawText = data.content?.[0]?.text || '';
        }} else if (prov === 'openai') {{
          const res = await fetch('https://api.openai.com/v1/chat/completions', {{
            method: 'POST',
            headers: {{
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${{aiApiKey}}`
            }},
            body: JSON.stringify({{
              model: model,
              temperature: 0.7,
              max_tokens: 1024,
              messages: [
                {{ role: 'system', content: `${{criticalSystemPrompt}}\\n\\nInstitutions sample:\\n${{sampleInsts}}` }},
                {{ role: 'user', content: userPrompt }}
              ]
            }})
          }});
          if (!res.ok) throw new Error(`OpenAI error ${{res.status}}`);
          const data = await res.json();
          rawText = data.choices?.[0]?.message?.content || '';
        }} else {{
          // Google Gemini
          const res = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/${{model}}:generateContent?key=${{aiApiKey}}`, {{
            method: 'POST',
            headers: {{ 'Content-Type': 'application/json' }},
            body: JSON.stringify({{
              contents: [
                {{ role: 'user', parts: [{{ text: `${{criticalSystemPrompt}}\\n\\nInstitutions sample:\\n${{sampleInsts}}\\n\\nUser question: ${{userPrompt}}` }}] }}
              ],
              generationConfig: {{
                temperature: 0.7,
                maxOutputTokens: 1024
              }}
            }})
          }});
          if (!res.ok) throw new Error(`Gemini error ${{res.status}}`);
          const data = await res.json();
          rawText = data.candidates?.[0]?.content?.parts?.[0]?.text || '';
        }}

        if (rawText) {{
          return rawText.split(/\\n\\s*\\n/).filter(p => p.trim()).map(p => `<p class="text-slate-200 leading-relaxed">${{p.trim()}}</p>`).join('');
        }}
      }} catch (err) {{
        console.warn('Live AI query error, falling back to offline knowledge engine:', err);
      }}
      return null;
    }}

    async function testAPIConnection(prov, key, model) {{
      if (!key) return {{ success: false, error: 'Please enter an API key' }};
      try {{
        if (prov === 'anthropic') {{
          const res = await fetch('https://api.anthropic.com/v1/messages', {{
            method: 'POST',
            headers: {{
              'Content-Type': 'application/json',
              'x-api-key': key,
              'anthropic-version': '2023-06-01',
              'anthropic-dangerous-direct-browser-access': 'true'
            }},
            body: JSON.stringify({{
              model: model || 'claude-haiku-4-5-20251001',
              max_tokens: 10,
              messages: [{{ role: 'user', content: 'Respond with OK' }}]
            }})
          }});
          if (!res.ok) {{
            const err = await res.json().catch(() => ({{}}));
            return {{ success: false, error: err.error?.message || `HTTP ${{res.status}}` }};
          }}
          return {{ success: true, message: 'Connected to Claude successfully!' }};
        }} else if (prov === 'openai') {{
          const res = await fetch('https://api.openai.com/v1/chat/completions', {{
            method: 'POST',
            headers: {{ 'Content-Type': 'application/json', 'Authorization': `Bearer ${{key}}` }},
            body: JSON.stringify({{
              model: model || 'gpt-4o-mini',
              max_tokens: 10,
              messages: [{{ role: 'user', content: 'Respond with OK' }}]
            }})
          }});
          if (!res.ok) {{
            const err = await res.json().catch(() => ({{}}));
            return {{ success: false, error: err.error?.message || `HTTP ${{res.status}}` }};
          }}
          return {{ success: true, message: 'Connected to OpenAI successfully!' }};
        }} else {{
          const m = model || 'gemini-2.5-flash';
          const res = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/${{m}}:generateContent?key=${{key}}`, {{
            method: 'POST',
            headers: {{ 'Content-Type': 'application/json' }},
            body: JSON.stringify({{ contents: [{{ role: 'user', parts: [{{ text: 'OK' }}] }}] }})
          }});
          if (!res.ok) {{
            const err = await res.json().catch(() => ({{}}));
            return {{ success: false, error: err.error?.message || `HTTP ${{res.status}}` }};
          }}
          return {{ success: true, message: 'Connected to Gemini successfully!' }};
        }}
      }} catch (e) {{
        return {{ success: false, error: e.message || 'Network request failed' }};
      }}
    }}

    // Extract unique cities list for instant recognition
    const ALL_CITIES = Array.from(new Set(ALL_INSTITUTIONS.map(i => (i.city || '').trim()))).filter(Boolean);
    ALL_CITIES.sort((a, b) => b.length - a.length);

    function findMentionedCity(text) {{
      const t = (text || '').toLowerCase().trim();
      for (const city of ALL_CITIES) {{
        const cLow = city.toLowerCase();
        const escaped = cLow.replace(/[.*+?^${{}}()|[\\]\\\\]/g, '\\\\$&');
        const regex = new RegExp('(?:^|\\\\b|\\\\s)' + escaped + '(?:\\\\b|\\\\s|$)', 'i');
        if (regex.test(t) || t === cLow) {{
          return city;
        }}
      }}
      return null;
    }}

    function findMentionedInst(text) {{
      const t = (text || '').toLowerCase().trim();
      return ALL_INSTITUTIONS.find(i => {{
        const nameLow = i.name.toLowerCase();
        if (t.includes(nameLow)) return true;
        if (i.aliases && i.aliases.some(a => t.includes(a.toLowerCase()))) return true;
        return false;
      }});
    }}

    // Intelligent Conversational Curator Knowledge Engine
    async function handleCuratorQuery(query) {{
      const q = query.toLowerCase().trim();
      const rawTrimmed = query.trim();

      // A. Seamless API Key Detection from Chat Input
      if (/^(sk-ant-[a-zA-Z0-9_\-]+|AIza[a-zA-Z0-9_\-]+|sk-[a-zA-Z0-9_\-]+)$/.test(rawTrimmed) || rawTrimmed.startsWith('/key ')) {{
        const key = rawTrimmed.replace(/^\/key\s*/, '').trim();
        const prov = detectProvider(key);
        const pName = prov === 'anthropic' ? 'Anthropic Claude' : (prov === 'openai' ? 'OpenAI' : 'Google Gemini');
        aiApiKey = key;
        aiProvider = prov;
        aiModel = getEffectiveModel();
        localStorage.setItem('atlas_ai_api_key', key);
        localStorage.setItem('atlas_ai_provider', prov);
        localStorage.setItem('atlas_ai_model', aiModel);
        updateAIStatusUI();
        appendCuratorMessage(`
          <p class="text-emerald-400 font-semibold">
            ✓ ${{pName}} API Key detected and securely saved to your browser!
          </p>
          <p class="text-slate-200">
            Live intelligence is now active with <strong>${{aiModel}}</strong>. Ask me anything about art history, exhibition genealogies from <em>Beyond Objecthood</em>, e-flux institutional critique, or our 203 ethical sanctuaries.
          </p>
        `);
        return;
      }}

      curatorTyping.classList.remove('hidden');

      // Proactively zoom into any mentioned location or city immediately
      const earlyInst = findMentionedInst(query);
      const earlyCity = findMentionedCity(query);
      if (earlyInst) {{
        selectInstitution(earlyInst, true);
      }} else if (earlyCity) {{
        filterByCity(earlyCity, true, false);
      }}

      // 1. Try Live Generative AI Model if API Key is configured
      if (aiApiKey) {{
        const aiHtml = await queryAI(query);
        if (aiHtml) {{
          curatorTyping.classList.add('hidden');
          appendCuratorMessage(aiHtml);
          return;
        }}
      }}

      // 2. Intelligent Offline Conversational Critical Engine (Always Active)
      setTimeout(() => {{
        curatorTyping.classList.add('hidden');

        // =========================================================================
        // 🏛️ CRITICAL THEORY & ART SCENE SPECIALIST HANDLERS
        // =========================================================================

        // 1. London Art Scene & Independent Spaces
        if (q.includes('london') && (q.includes('art') || q.includes('scene') || q.includes('space') || q.includes('tell me') || q.includes('more') || q.includes('guide') || q.includes('recommend') || q.includes('culture') || q.includes('critic'))) {{
          const chis = ALL_INSTITUTIONS.find(i => i.name.includes('Chisenhale Gallery'));
          const camden = ALL_INSTITUTIONS.find(i => i.name.includes('Camden Art Centre'));
          const white = ALL_INSTITUTIONS.find(i => i.name.includes('Whitechapel Gallery'));
          const serp = ALL_INSTITUTIONS.find(i => i.name.includes('Serpentine Galleries'));
          const volt = ALL_INSTITUTIONS.find(i => i.name.includes('Studio Voltaire'));
          const south = ALL_INSTITUTIONS.find(i => i.name.includes('South London Gallery'));
          const gas = ALL_INSTITUTIONS.find(i => i.name.includes('Gasworks'));
          const tate = ALL_INSTITUTIONS.find(i => i.name.includes('Tate Modern'));

          appendCuratorMessage(`
            <p class="text-slate-200">
              London's contemporary art landscape is defined by a profound institutional dialectic: on one side stand the high-profile corporate mega-museums along the Thames, and on the other, a resilient, historically vital constellation of independent kunsthalles, artist-run spaces, and civic commissioning engines.
            </p>
            <p class="text-slate-300">
              This ecosystem was forged through intense cultural struggle. For 26 years, British Petroleum (BP) underwrote ${{formatInstLink(tate)}}, until artist coalitions like <em>BP or not BP?</em>, <em>Liberate Tate</em>, and <em>Culture Unstained</em> led a decade of unsanctioned direct actions—from theatrical die-ins to installing a 1.5-tonne pirate wind-turbine blade inside the Turbine Hall—forcing Tate to sever BP sponsorship in 2016. In parallel, Nan Goldin's P.A.I.N. campaigns successfully pressured institutions across London to strip the Sackler family opioid name from their wings.
            </p>
            <p class="text-slate-300">
              Today, the true intellectual pulse of London thrives in spaces where curatorial autonomy is paramount. In East London's Bow, ${{formatInstLink(chis)}} occupies a former 1930s veneer factory, celebrated worldwide for commissioning pivotal early career-defining solo exhibitions by Lubaina Himid, Rachel Whiteread, and Lynette Yiadom-Boakye with 100% free public admission. In North London, ${{formatInstLink(camden)}} offers peaceful studio residency gardens dedicated to experimental sculptural and ceramic inquiry away from market speculation.
            </p>
            <p class="text-slate-300">
              Further shaping the city's critical discourse are ${{formatInstLink(white)}} in Aldgate, with over a century of radical civic heritage (famously exhibiting Picasso's <em>Guernica</em> in 1939 to rally support for the Spanish Republic and hosting the seminal 1956 <em>This Is Tomorrow</em> exhibition), ${{formatInstLink(serp)}} in Kensington Gardens, ${{formatInstLink(volt)}} in Clapham supporting non-profit artist studios and queer practices, ${{formatInstLink(south)}} in Peckham, and ${{formatInstLink(gas)}} in Vauxhall. Each operates under ethical public charters free from fossil-fuel and defense underwriting.
            </p>
          `);
          filterByCity('London', true, false);
          return;
        }}

        // 2. Beyond Objecthood: The Exhibition as a Critical Form Since 1968
        if (q.includes('beyond objecthood') || q.includes('voorhies') || (q.includes('objecthood') && (q.includes('fried') || q.includes('art') || q.includes('exhibition'))) || q.includes('exhibition as a critical form') || q.includes('exhibition as form')) {{
          appendCuratorMessage(`
            <p class="text-slate-200">
              In <em>Beyond Objecthood: The Exhibition as a Critical Form Since 1968</em> (MIT Press, 2017), curator and art historian James Voorhies examines how the exhibition itself became the primary artistic medium and a crucial form of political and cultural critique.
            </p>
            <p class="text-slate-300">
              The genealogy begins with Michael Fried's notorious 1967 polemic <em>"Art and Objecthood"</em>. Fried fiercely defended modernist autonomy (Clement Greenberg, Frank Stella, Anthony Caro) and attacked Minimalist sculpture (Donald Judd, Robert Morris, Tony Smith) for what he condemned as <strong>'theatricality'</strong>—the fact that Minimalist objects require the temporal, bodily presence of the viewer in a room over time, reducing art to an open-ended 'situation'. For Fried, genuine art was instantaneous and transcendent: <em>'presentness is grace.'</em>
            </p>
            <p class="text-slate-300">
              Voorhies demonstrates how, starting in 1968, artists turned Fried's critique into a radical weapon. Figures from Robert Smithson (with his earthwork non-sites) and Marcel Broodthaers (fictional museum departments) to Michael Asher, Group Material, Fred Wilson, Maria Eichhorn, Philippe Parreno, and Tino Sehgal radically embraced theatricality, temporal duration, and spectator involvement. By transforming the exhibition into a critical form, they shattered the illusion of the neutral 'white cube' and exposed how museums construct ideology, race, and capital.
            </p>
            <p class="text-slate-300">
              Crucially, Voorhies exposes a 21st-century museological paradox: the participatory, dematerialized practices conceived in the 1960s–90s to escape commodification were later co-opted by corporate mega-museums (Tate Modern Turbine Hall, MoMA, Guggenheim) into tourist spectacle, selfie architecture, and corporate entertainment branding. To resist this absorption, Voorhies argues that critical agency has migrated to independent kunsthalles, artist-run spaces, and discursive public platforms that refuse to reduce viewers to passive consumers.
            </p>
          `);
          return;
        }}

        // 3. e-flux Journal, Hito Steyerl & Boris Groys
        if (q.includes('e-flux') || q.includes('steyerl') || q.includes('groys') || q.includes('vidokle') || q.includes('museum as factory') || q.includes('duty free art') || q.includes('duty-free art') || q.includes('freeport') || q.includes('post-democracy')) {{
          appendCuratorMessage(`
            <p class="text-slate-200">
              Over the past two decades, <em>e-flux journal</em> (founded by Anton Vidokle, Julieta Aranda, and Brian Kuan Wood) has served as one of the definitive publishing platforms for radical institutional critique and aesthetic theory.
            </p>
            <p class="text-slate-300">
              Central to this discourse is <strong>Hito Steyerl</strong>, whose seminal essay <em>"Is a Museum a Factory?"</em> (2009) redefined how we analyze cultural space. Steyerl argues that the museum has shifted from a bourgeois temple of aesthetic contemplation or historical archive into a post-Fordist 24/7 factory. Within this space, museum visitors are not passive spectators, but unpaid affective laborers whose attention, social media circulation, and cultural capital generate economic surplus for surrounding luxury real estate and trustee investment portfolios.
            </p>
            <p class="text-slate-300">
              In <em>"Duty Free Art: Art in the Age of Planetary Civil War"</em> (2015), Steyerl exposes the phenomenon of offshore freeports (such as Geneva, Singapore, and Luxembourg)—giant tax-exempt transit warehouses where blue-chip masterpieces sit inside climate-controlled crates, traded via offshore bearer shares as speculative hedges without ever being seen by the public. Art loses its public objecthood, functioning purely as hyper-liquid, unregulated dark currency.
            </p>
            <p class="text-slate-300">
              Philosopher <strong>Boris Groys</strong> complements this with texts like <em>"Art Workers: Between Utopia and the Archive"</em> and <em>"The Museum as a Cradle of Revolution"</em>, tracing the public museum's origin to the French Revolution as a secular machine designed to decapitate religious and monarchical icons, converting them into historical artifacts for universal civic access. Alongside Anton Vidokle's critique in <em>"Art Without Artists?"</em> (confronting the rise of the celebrity curator), e-flux provides the essential theoretical vocabulary to demystify how contemporary art is instrumentalized by global financialization.
            </p>
          `);
          return;
        }}

        // 4. Three Waves of Institutional Critique
        if (q.includes('institutional critique') || q.includes('haacke') || q.includes('andrea fraser') || q.includes('three waves') || q.includes('3 waves') || q.includes('waves of critique') || q.includes('fred wilson')) {{
          appendCuratorMessage(`
            <p class="text-slate-200">
              Institutional critique has evolved through three distinct, transformative historical waves:
            </p>
            <p class="text-slate-300">
              <strong>First Wave (Late 1960s–1970s): The Frame and the Board.</strong> Initiated by artists like Hans Haacke, Michael Asher, Daniel Buren, and Marcel Broodthaers, the first wave sought to dismantle the myth of the museum as a neutral, transcendent temple of aesthetic autonomy. Haacke's <em>MoMA Poll</em> (1970) directly interrogated visitor attitudes toward board chairman Nelson Rockefeller's support for the Nixon administration's Indochina policy, while his 1971 work <em>Shapolsky et al. Manhattan Real Estate Holdings</em> exposed the predatory slumlord holdings of a Guggenheim trustee, leading director Thomas Messer to censor and cancel the exhibition.
            </p>
            <p class="text-slate-300">
              <strong>Second Wave (1980s–1990s): Complicity and Internalization.</strong> Theorized decisively by Andrea Fraser in her 2005 landmark essay <em>"From the Critique of Institutions to an Institution of Critique"</em>, second-wave practitioners realized there is 'no outside' to the institution. Artists, critics, and viewers are themselves constituted by the cultural capital, prestige, and psychological desires of the museum system. Fraser's performances (like docent Jane Castleton in <em>Museum Highlights</em>, 1989) and her 900-page forensic study <em>2016 in Museums, Money, and Politics</em> dissected board political donations, while Fred Wilson's <em>Mining the Museum</em> (1992) and the Guerrilla Girls confronted systemic racial and gender bias.
            </p>
            <p class="text-slate-300">
              <strong>Third Wave / Direct Divestment (2010s–Present): Activist Decoupling.</strong> The contemporary phase has moved from symbolic gallery interventions to collective, direct-action divestment campaigns. Nan Goldin's P.A.I.N. organized die-ins inside the Met, Guggenheim, and Louvre, forcing major museums worldwide to strip the Sackler opioid family name. Coalitions like <em>Decolonize This Place</em> and <em>Strike MoMA</em> targeted trustees tied to vulture funds, private prisons, and border militarization, while the 2019 Whitney Biennial artist boycott forced the resignation of Safariland tear gas manufacturer Warren Kanders.
            </p>
          `);
          return;
        }}

        // 5. Claire Bishop & Radical Museology
        if (q.includes('claire bishop') || q.includes('radical museology') || q.includes('artificial hells') || q.includes('relational aesthetics') || q.includes('bourriaud')) {{
          appendCuratorMessage(`
            <p class="text-slate-200">
              Art historian and theorist Claire Bishop has provided some of the most incisive critiques of contemporary exhibition-making and curatorial practice.
            </p>
            <p class="text-slate-300">
              In <em>Radical Museology: Or, What's Contemporary in Museums of Contemporary Art?</em> (2013), Bishop contrasts two opposing institutional models: the <strong>'presentist' corporate mega-museum</strong> (which prioritizes sensationalist architectural spectacles, transient blockbuster exhibitions, and consumer footfall to drive retail revenue) versus <strong>dialectical, historical museums</strong> (such as the Van Abbemuseum in Eindhoven under Charles Esche, Reina Sofía in Madrid under Manuel Borja-Villel, and MSUM in Ljubljana under Zdenka Badovinac). These radical institutions mobilize their permanent collections not as decorative luxury assets, but as critical historical weapons to interrogate current political crises.
            </p>
            <p class="text-slate-300">
              In <em>Artificial Hells: Participatory Art and the Politics of Spectatorship</em> (Verso, 2012), Bishop took aim at the uncritical embrace of 'relational aesthetics' (theorized by Nicolas Bourriaud). She argued that reducing art to friendly, convivial social gatherings often serves as an easy palliative, simulating community while dodging difficult artistic antagonisms, aesthetic criteria, and structural political critique.
            </p>
          `);
          return;
        }}

        // 6. Minimalism, Dia Beacon & Phenomenology
        if (q.includes('minimalism') || q.includes('dia beacon') || q.includes('judds') || q.includes('judd') || q.includes('richard serra') || q.includes('phenomenolog')) {{
          const dia = ALL_INSTITUTIONS.find(i => i.name.includes('Dia Beacon'));
          appendCuratorMessage(`
            <p class="text-slate-200">
              Minimalism in the 1960s represented a fundamental philosophical rupture: artists like Donald Judd, Dan Flavin, Robert Morris, and Richard Serra rejected metaphorical representation and expressive illusion, insisting instead on 'specific objects' and direct phenomenological encounter.
            </p>
            <p class="text-slate-300">
              No institution embodies this ethos more powerfully than ${{formatInstLink(dia)}} in the Hudson Valley. Housed in a vast 1929 former Nabisco box-printing facility on the Hudson River, Dia Beacon provides nearly 300,000 square feet illuminated entirely by northern daylight through sawtooth skylights. Here, Donald Judd's plywood boxes, Richard Serra's monumental weathered steel <em>Torqued Ellipses</em>, and Michael Heizer's sunken negative voids <em>North, East, South, West</em> exist at architectural scale, fulfilling the Minimalist demand that art be experienced physically in real space and real time.
            </p>
            <p class="text-slate-300">
              Founded by Philippa de Menil, Heiner Friedrich, and Helen Winkler in 1974, the Dia Art Foundation operates with a visionary endowment model that commits to sustaining singular, in-depth artistic installations indefinitely, completely free from the churn of commercial art fairs.
            </p>
          `);
          selectInstitution(dia, true);
          return;
        }}

        // 7. New York Art Scene & Board Politics
        if (q.includes('new york') || q.includes('nyc') || q.includes('manhattan')) {{
          const dia = ALL_INSTITUTIONS.find(i => i.name.includes('Dia Beacon'));
          const sculp = ALL_INSTITUTIONS.find(i => i.name.includes('SculptureCenter'));
          const artsp = ALL_INSTITUTIONS.find(i => i.name.includes('Artists Space'));
          const kitch = ALL_INSTITUTIONS.find(i => i.name.includes('The Kitchen'));
          const swiss = ALL_INSTITUTIONS.find(i => i.name.includes('Swiss Institute'));
          const moma = ALL_INSTITUTIONS.find(i => i.name === 'MoMA (The Museum of Modern Art)');

          appendCuratorMessage(`
            <p class="text-slate-200">
              New York City presents the starkest clash in the global art world between private financial oligarchies and courageous grassroots artistic resistance.
            </p>
            <p class="text-slate-300">
              Major institutions like ${{formatInstLink(moma)}} and the Whitney Museum have been centers of intense community mobilization. MoMA sparked 10 weeks of protests by the <em>Strike MoMA</em> coalition over board members tied to vulture funds, private prisons, and defense contractors, leading former chairman Leon Black to step down over $158 million in payments to Jeffrey Epstein. At the Whitney, an artist boycott forced the resignation of Safariland tear gas CEO Warren Kanders.
            </p>
            <p class="text-slate-300">
              Culture Atlas highlights New York's uncompromised, artist-centered alternatives. In Tribeca, ${{formatInstLink(artsp)}} has championed radical discourse since 1972 (giving early platforms to Cindy Sherman and Barbara Kruger and hosting Decolonize This Place assemblies). In Queens, ${{formatInstLink(sculp)}} champions experimental non-commercial sculpture in a historic trolley repair shop. And in the Hudson Valley, ${{formatInstLink(dia)}} remains the world's preeminent monument to Minimalist integrity.
            </p>
          `);
          filterByCity('New York', true, false);
          return;
        }}

        // 8. Paris Art Scene & Civic Models
        if (q.includes('paris')) {{
          const ptok = ALL_INSTITUTIONS.find(i => i.name.includes('Palais de Tokyo'));
          const pomp = ALL_INSTITUTIONS.find(i => i.name.includes('Pompidou'));
          const cart = ALL_INSTITUTIONS.find(i => i.name.includes('Fondation Cartier'));

          appendCuratorMessage(`
            <p class="text-slate-200">
              Paris's contemporary art scene is shaped by a distinct balance between state-subsidized civic kunsthalles and the growing footprint of private luxury foundation museums.
            </p>
            <p class="text-slate-300">
              France's model of public funding through the Ministry of Culture and regional DRAC bodies guarantees public access and shields institutions from corporate board capture. A premier example is ${{formatInstLink(ptok)}}, Europe's largest contemporary art center, operating as a dynamic, anti-monumental laboratory open until midnight. In the heart of the city, ${{formatInstLink(pomp)}} stands as an iconic monument to democratic cultural decentralization, designed by Renzo Piano and Richard Rogers.
            </p>
            <p class="text-slate-300">
              While private foundations like ${{formatInstLink(cart)}} present architecturally ambitious commissions, public discourse in Paris remains acutely engaged with debates on postcolonial provenance, restitution, and defending public cultural subsidies against commercialization.
            </p>
          `);
          filterByCity('Paris', true, false);
          return;
        }}

        // 9. Berlin Art Scene & Independent Spaces
        if (q.includes('berlin')) {{
          const kw = ALL_INSTITUTIONS.find(i => i.name.includes('KW Institute'));
          const hkw = ALL_INSTITUTIONS.find(i => i.name.includes('Haus der Kulturen'));
          const grop = ALL_INSTITUTIONS.find(i => i.name.includes('Gropius Bau'));

          appendCuratorMessage(`
            <p class="text-slate-200">
              Berlin's cultural ecosystem owes its worldwide reputation to its post-1989 history of artist self-organization, independent project spaces (<em>Freie Szene</em>), and robust federal arts funding that prioritizes experimental discourse over commercial market speculation.
            </p>
            <p class="text-slate-300">
              In Mitte, ${{formatInstLink(kw)}} occupies a former 19th-century margarine factory, serving as a pioneer of uncompromised curatorial experimentation and home of the Berlin Biennale. In Tiergarten, ${{formatInstLink(hkw)}} serves as an internationally renowned forum for postcolonial discourse, planetary anthropocene research, and non-Western epistemologies. At the former border, ${{formatInstLink(grop)}} stages major interdisciplinary encounters with free access to its iconic ground floor.
            </p>
            <p class="text-slate-300">
              Despite intensifying real estate gentrification pressures, Berlin remains one of the world's most intellectually rigorous artistic capitals, where artists actively mobilize for wage equity, studio preservation, and independent governance.
            </p>
          `);
          filterByCity('Berlin', true, false);
          return;
        }}

        // =========================================================================
        // 🏛️ VISITOR DATA & AUDIT HANDLERS
        // =========================================================================

        // A. Visitor Data: Hours & Monday Openings
        if (q.includes('hour') || q.includes('schedule') || (q.includes('time') && (q.includes('open') || q.includes('visit'))) || q.includes('monday') || q.includes('weekend') || q.includes('late night') || q.includes('closed')) {{
          const targetInst = ALL_INSTITUTIONS.find(i => q.includes(i.name.toLowerCase()) || (i.aliases && i.aliases.some(a => q.includes(a.toLowerCase()))));
          if (targetInst) {{
            appendCuratorMessage(`
              <p class="text-slate-200">
                If you are planning a visit to ${{formatInstLink(targetInst)}}, it welcomes the public <strong>${{targetInst.opening_hours}}</strong>.
              </p>
              <p class="text-slate-300">
                You will find it at <strong>${{targetInst.address}}</strong> in the ${{targetInst.neighborhood}} neighborhood, conveniently reached via ${{targetInst.transit_tips}}. I recommend setting aside roughly <strong>${{targetInst.visit_duration}}</strong> to immerse yourself in the exhibitions and its signature landmark: ${{targetInst.highlight}}.
              </p>
            `);
            selectInstitution(targetInst, true);
            return;
          }}

          if (q.includes('monday')) {{
            const mondaySpaces = ALL_INSTITUTIONS.filter(i => !i.opening_hours.toLowerCase().includes('closed mon') && (i.opening_hours.toLowerCase().includes('daily') || i.opening_hours.toLowerCase().includes('mon,') || i.opening_hours.toLowerCase().includes('mon–') || i.opening_hours.toLowerCase().includes('mon-')));
            const m1 = mondaySpaces[0] || ALL_INSTITUTIONS.find(i => i.name.includes('Palais de Tokyo'));
            const m2 = mondaySpaces[1] || ALL_INSTITUTIONS.find(i => i.name.includes('Louisiana'));
            const m3 = mondaySpaces[2] || ALL_INSTITUTIONS.find(i => i.name.includes('Chisenhale'));
            appendCuratorMessage(`
              <p class="text-slate-200">
                While most conventional museums shutter their galleries at the start of the week, Culture Atlas tracks <strong>${{mondaySpaces.length}}</strong> ethical cultural sanctuaries open on Mondays for quiet reflection.
              </p>
              <p class="text-slate-300">
                In Paris, you can wander through ${{formatInstLink(m1)}}, celebrated for its midnight late openings. Along the Danish coastline, the sublime seaside sculpture park at ${{formatInstLink(m2)}} is open daily and easily reached via coastal rail. In London, ${{formatInstLink(m3)}} welcomes visitors with free public admission. Each space operates with transparent civic or independent governance free from fossil-fuel influence.
              </p>
            `);
            return;
          }}

          const pTok = ALL_INSTITUTIONS.find(i => i.name.includes('Palais de Tokyo'));
          const louis = ALL_INSTITUTIONS.find(i => i.name.includes('Louisiana'));
          const sted = ALL_INSTITUTIONS.find(i => i.name.includes('Stedelijk'));
          appendCuratorMessage(`
            <p class="text-slate-200">
              Institutional schedules across our network are thoughtfully balanced between public accessibility and artist studio production. Most independent kunsthalles and artist-run spaces welcome visitors <strong>Wednesday through Sunday (11:00–18:00 or 12:00–18:00)</strong>, reserving Mondays and Tuesdays for installation and artist studio work.
            </p>
            <p class="text-slate-300">
              For evening contemplation, ${{formatInstLink(pTok)}} remains open until midnight, while spaces like ${{formatInstLink(louis)}} and ${{formatInstLink(sted)}} offer extended evening hours. You can click on any institution across the globe to review its exact timetable.
            </p>
          `);
          return;
        }}

        // B. Visitor Data: Public Transit & Getting There
        if (q.includes('transit') || q.includes('how to get') || q.includes('how do i get') || q.includes('direction') || q.includes('subway') || q.includes('metro') || q.includes('train') || q.includes('bus') || q.includes('ferry') || q.includes('getting there')) {{
          const targetInst = ALL_INSTITUTIONS.find(i => q.includes(i.name.toLowerCase()) || (i.aliases && i.aliases.some(a => q.includes(a.toLowerCase()))));
          if (targetInst) {{
            appendCuratorMessage(`
              <p class="text-slate-200">
                To travel to ${{formatInstLink(targetInst)}}, your best transit connection is: <strong>${{targetInst.transit_tips}}</strong>.
              </p>
              <p class="text-slate-300">
                The venue is situated at <strong>${{targetInst.address}}</strong> in ${{targetInst.neighborhood}}. It welcomes visitors ${{targetInst.opening_hours}}, and I recommend planning about ${{targetInst.visit_duration}} for your visit.
              </p>
            `);
            selectInstitution(targetInst, true);
            return;
          }}

          const dia = ALL_INSTITUTIONS.find(i => i.name.includes('Dia Beacon'));
          const louis = ALL_INSTITUTIONS.find(i => i.name.includes('Louisiana'));
          const kroll = ALL_INSTITUTIONS.find(i => i.name.includes('Kröller'));
          appendCuratorMessage(`
            <p class="text-slate-200">
              Every cultural sanctuary mapped in Culture Atlas includes verified public transit directions. Some of the most memorable art pilgrimages in the world are seamless by rail:
            </p>
            <p class="text-slate-300">
              You can board the Metro-North Hudson Line from Manhattan directly to ${{formatInstLink(dia)}}, take the scenic coastal Kystbanen train north from Copenhagen to ${{formatInstLink(louis)}}, or cycle through the national park forest to reach ${{formatInstLink(kroll)}} in Otterlo.
            </p>
          `);
          return;
        }}

        // C. Visitor Data: Accessibility & Universal Access
        if (q.includes('accessib') || q.includes('wheelchair') || q.includes('step-free') || q.includes('elevator') || q.includes('disab') || q.includes('mobility') || q.includes('sensory')) {{
          const targetInst = ALL_INSTITUTIONS.find(i => q.includes(i.name.toLowerCase()) || (i.aliases && i.aliases.some(a => q.includes(a.toLowerCase()))));
          if (targetInst) {{
            appendCuratorMessage(`
              <p class="text-slate-200">
                Regarding physical and sensory access, ${{formatInstLink(targetInst)}} provides: <strong>${{targetInst.accessibility}}</strong>.
              </p>
              <p class="text-slate-300">
                Transit access is straightforward via ${{targetInst.transit_tips}}. In accordance with equitable civic standards across our atlas, personal care assistants and essential companions always receive complimentary admission.
              </p>
            `);
            selectInstitution(targetInst, true);
            return;
          }}

          const serp = ALL_INSTITUTIONS.find(i => i.name.includes('Serpentine'));
          const aros = ALL_INSTITUTIONS.find(i => i.name.includes('ARoS'));
          const mplus = ALL_INSTITUTIONS.find(i => i.name.includes('M+ Museum'));
          appendCuratorMessage(`
            <p class="text-slate-200">
              Universal, barrier-free access is a core requirement of civic cultural stewardship. All institutions audited in Culture Atlas provide step-free circulation, passenger elevators, loaner wheelchairs, accessible gender-neutral washrooms, and free entry for essential companions.
            </p>
            <p class="text-slate-300">
              Exemplary barrier-free destinations include ${{formatInstLink(serp)}}, ${{formatInstLink(aros)}}, and ${{formatInstLink(mplus)}}.
            </p>
          `);
          return;
        }}

        // D. Visitor Data: Amenities (Cafés, Bookshops, Gardens)
        if (q.includes('café') || q.includes('cafe') || q.includes('coffee') || q.includes('restaurant') || q.includes('dining') || q.includes('bookshop') || q.includes('bookstore') || q.includes('garden') || q.includes('park') || q.includes('amenities') || q.includes('lockers')) {{
          const targetInst = ALL_INSTITUTIONS.find(i => q.includes(i.name.toLowerCase()) || (i.aliases && i.aliases.some(a => q.includes(a.toLowerCase()))));
          if (targetInst) {{
            appendCuratorMessage(`
              <p class="text-slate-200">
                When visiting ${{formatInstLink(targetInst)}}, you will find on-site amenities including: <strong>${{targetInst.amenities}}</strong>.
              </p>
              <p class="text-slate-300">
                While exploring, be sure not to miss its signature landmark, <span class="text-amber-300/90">${{targetInst.highlight}}</span>. The space is open to visitors ${{targetInst.opening_hours}}.
              </p>
            `);
            selectInstitution(targetInst, true);
            return;
          }}

          const louis = ALL_INSTITUTIONS.find(i => i.name.includes('Louisiana'));
          const prada = ALL_INSTITUTIONS.find(i => i.name.includes('Fondazione Prada'));
          const camden = ALL_INSTITUTIONS.find(i => i.name.includes('Camden Art Centre'));
          const tpg = ALL_INSTITUTIONS.find(i => i.name.includes("Photographers' Gallery"));
          appendCuratorMessage(`
            <p class="text-slate-200">
              Visiting an ethical cultural space is as much about contemplative pauses as the art itself. For seaside dining and an organic café overlooking the water, explore ${{formatInstLink(louis)}}.
            </p>
            <p class="text-slate-300">
              In Milan, ${{formatInstLink(prada)}} features <em>Bar Luce</em>, designed by filmmaker Wes Anderson. In London, ${{formatInstLink(camden)}} offers a tranquil garden lawn café, while ${{formatInstLink(tpg)}} in Soho hosts one of Europe's definitive photobook specialist bookshops.
            </p>
          `);
          return;
        }}

        // E. Visitor Data: Highlights & Landmarks
        if (q.includes('highlight') || q.includes('what to see') || q.includes('must-see') || q.includes('signature') || q.includes('artworks') || q.includes('monument')) {{
          const targetInst = ALL_INSTITUTIONS.find(i => q.includes(i.name.toLowerCase()) || (i.aliases && i.aliases.some(a => q.includes(a.toLowerCase()))));
          if (targetInst) {{
            appendCuratorMessage(`
              <p class="text-slate-200">
                The signature highlight at ${{formatInstLink(targetInst)}} is: <span class="text-amber-300/90 font-medium">${{targetInst.highlight}}</span>.
              </p>
              <p class="text-slate-300">
                Governed as an independent <em>${{targetInst.governance_type}}</em>, its curatorial programme centers on ${{targetInst.curatorial_focus}}. The museum welcomes visitors ${{targetInst.opening_hours}}.
              </p>
            `);
            selectInstitution(targetInst, true);
            return;
          }}

          const aros = ALL_INSTITUTIONS.find(i => i.name.includes('ARoS'));
          const dia = ALL_INSTITUTIONS.find(i => i.name.includes('Dia Beacon'));
          const inhotim = ALL_INSTITUTIONS.find(i => i.name.includes('Inhotim'));
          appendCuratorMessage(`
            <p class="text-slate-200">
              Across 35 countries, Culture Atlas maps astonishing site-specific art and architectural landmarks.
            </p>
            <p class="text-slate-300">
              Standout experiences include Olafur Eliasson's circular glass walkway <em>Your rainbow panorama</em> at ${{formatInstLink(aros)}}, Richard Serra's monumental weathered steel ellipses at ${{formatInstLink(dia)}}, and the 23 bespoke artist pavilions embedded within a 700-hectare rainforest at ${{formatInstLink(inhotim)}}.
            </p>
          `);
          return;
        }}

        // F. Methodology, Philosophy & Criteria
        if (q.includes('what type') || q.includes('should i go') || q.includes('what makes') || q.includes('method') || q.includes('criteria') || (q.includes('how') && (q.includes('evaluate') || q.includes('work') || q.includes('tier') || q.includes('ethical')))) {{
          const capc = ALL_INSTITUTIONS.find(i => i.name.includes('CAPC'));
          const plugin = ALL_INSTITUTIONS.find(i => i.name.includes('Plug In ICA'));
          const chis = ALL_INSTITUTIONS.find(i => i.name.includes('Chisenhale'));
          appendCuratorMessage(`
            <p class="text-slate-200">
              When choosing cultural spaces to support with your visit and admission, look at how their funding architecture protects artistic autonomy:
            </p>
            <p class="text-slate-300">
              First, prioritize <strong>civic municipal sanctuaries</strong> backed by public cultural councils (such as Arts Council England, DRAC in France, or the Canada Council). Because their primary accountability is to the public, curators are not pressured into censoring provocative art to appease corporate benefactors. Outstanding examples include ${{formatInstLink(capc)}} and ${{formatInstLink(plugin)}}.
            </p>
            <p class="text-slate-300">
              Second, seek out <strong>artist-run grassroots kunsthalles</strong> like ${{formatInstLink(chis)}}, where artist boards commission daring contemporary projects free from corporate board oversight.
            </p>
            <p class="text-slate-300">
              Third, celebrate <strong>institutions that actively divested</strong> from fossil fuel conglomerates and arms manufacturing, ensuring cultural spaces remain clean, uncompromised civic commons.
            </p>
          `);
          return;
        }}

        // G. Free Admission
        if (q.includes('free') || q.includes('admission') || q.includes('ticket') || q.includes('accessible') || q.includes('no fee')) {{
          const freeSpaces = ALL_INSTITUTIONS.filter(i => i.admission_policy.includes('Free Public') || i.admission_policy.includes('Always Free'));
          const f1 = freeSpaces[0] || ALL_INSTITUTIONS.find(i => i.name.includes('Chisenhale'));
          const f2 = freeSpaces[1] || ALL_INSTITUTIONS.find(i => i.name.includes('Whitechapel'));
          const f3 = freeSpaces[2] || ALL_INSTITUTIONS.find(i => i.name.includes('Serpentine'));
          appendCuratorMessage(`
            <p class="text-slate-200">
              We map <strong>${{freeSpaces.length}}</strong> cultural institutions providing completely free public admission, ensuring that contemporary art remains an open civic right rather than a commercial commodity.
            </p>
            <p class="text-slate-300">
              Standout free sanctuaries include ${{formatInstLink(f1)}}, celebrated for its artist commissions, ${{formatInstLink(f2)}} with century-old civic heritage, and the park pavilions of ${{formatInstLink(f3)}}. Each operates under public charters free from fossil-fuel sponsorship.
            </p>
          `);
          return;
        }}

        // H. Artist-run & Grassroots Centers
        if (q.includes('artist-run') || q.includes('artist run') || q.includes('grassroots') || q.includes('kunsthalle') || q.includes('independent') || q.includes('non-profit')) {{
          const artistSpaces = ALL_INSTITUTIONS.filter(i => i.governance_type.includes('Artist-Run'));
          const a1 = artistSpaces[0] || ALL_INSTITUTIONS.find(i => i.name.includes('Chisenhale'));
          const a2 = artistSpaces[1] || ALL_INSTITUTIONS.find(i => i.name.includes('Camden'));
          const a3 = artistSpaces[2] || ALL_INSTITUTIONS.find(i => i.name.includes('Plug In ICA'));
          appendCuratorMessage(`
            <p class="text-slate-200">
              Culture Atlas tracks <strong>${{artistSpaces.length}}</strong> artist-governed spaces worldwide. Governed directly by artists, these collectives champion daring, uncompromised artistic commissions completely free from corporate board interference.
            </p>
            <p class="text-slate-300">
              Standout artist-governed spaces include ${{formatInstLink(a1)}}, ${{formatInstLink(a2)}}, and ${{formatInstLink(a3)}}.
            </p>
          `);
          return;
        }}

        // I. Divestment from Fossil Fuels & Defense
        if (q.includes('fossil') || q.includes('defense') || q.includes('oil') || q.includes('bp') || q.includes('shell') || q.includes('baillie') || q.includes('weapons') || q.includes('divest')) {{
          const c1 = ALL_INSTITUTIONS.find(i => i.name.includes('Camden'));
          const c2 = ALL_INSTITUTIONS.find(i => i.name.includes('Whitechapel'));
          const c3 = ALL_INSTITUTIONS.find(i => i.name.includes('Nottingham Contemporary'));
          appendCuratorMessage(`
            <p class="text-slate-200">
              For decades, multinational extractive corporations (such as BP, Shell, and TotalEnergies) and arms manufacturers used museum underwriting to 'artwash' their public images. Over the past five years, courageous artist coalitions and cultural workers forced major venues to divest.
            </p>
            <p class="text-slate-300">
              Every single venue mapped in Culture Atlas has verified clean underwriting without fossil-fuel or defense sponsorship on its active roster. You can support this movement by visiting divested leaders such as ${{formatInstLink(c1)}}, ${{formatInstLink(c2)}}, and ${{formatInstLink(c3)}}.
            </p>
          `);
          return;
        }}

        // J. Excluded Institutions (MoMA, Whitney, Guggenheim)
        if (q.includes('moma') || q.includes('whitney') || q.includes('guggenheim') || q.includes('why exclude') || q.includes('excluded') || q.includes('kanders')) {{
          const dia = ALL_INSTITUTIONS.find(i => i.name.includes('Dia Beacon'));
          const sculp = ALL_INSTITUTIONS.find(i => i.name.includes('SculptureCenter'));
          const serp = ALL_INSTITUTIONS.find(i => i.name.includes('Serpentine'));
          appendCuratorMessage(`
            <p class="text-slate-200">
              Culture Atlas maintains a strict exclusion policy for institutions that retain unresolved ties to controversial underwriters, defense manufacturing, or human rights violations.
            </p>
            <p class="text-slate-300">
              The Museum of Modern Art (MoMA) in New York sparked citywide protests over trustees holding major stakes in defense contractors, private prisons, and extractive debt. Similarly, the Whitney Museum faced global artist boycotts until board vice chair Warren Kanders (CEO of tear gas manufacturer Safariland) stepped down under international pressure.
            </p>
            <p class="text-slate-300">
              Culture Atlas chooses instead to celebrate institutions whose funding architecture is clean and uncompromised, such as ${{formatInstLink(dia)}}, ${{formatInstLink(sculp)}}, and ${{formatInstLink(serp)}}.
            </p>
          `);
          return;
        }}

        // K. General City Inquiries
        const matchedCity = findMentionedCity(q) || (PRIORITY_CITIES.find(c => q.includes(c.name.toLowerCase()))?.name);
        if (matchedCity || q.includes('city') || q.includes('in ')) {{
          const cityName = matchedCity ? matchedCity : '';
          const cityMatches = ALL_INSTITUTIONS.filter(i => {{
            if (cityName) return matchC(i.city, cityName);
            return q.includes(i.city.toLowerCase());
          }});

          if (cityMatches.length > 0) {{
            const targetCity = cityMatches[0].city;
            const c1 = cityMatches[0];
            const c2 = cityMatches[1];
            const c3 = cityMatches[2];
            appendCuratorMessage(`
              <p class="text-slate-200">
                If you are exploring <a href="#" class="city-link font-semibold text-white hover:text-[#60a5fa] underline cursor-pointer" data-city="${{escapeHtml(targetCity)}}">${{escapeHtml(targetCity)}}</a>, we have mapped <strong>${{cityMatches.length}}</strong> verified ethical cultural sanctuaries here.
              </p>
              <p class="text-slate-300">
                Standout spaces include ${{formatInstLink(c1, {{noCity: true}})}}, celebrated for its ${{c1.curatorial_focus || 'contemporary commissions'}}${{c2 ? `, ${{formatInstLink(c2, {{noCity: true}})}}, offering ${{c2.admission_policy}}` : ''}}${{c3 ? `, and ${{formatInstLink(c3, {{noCity: true}})}}` : ''}}. All of these operate with transparent public charters free from fossil-fuel sponsorship.
              </p>
            `);

            filterByCity(targetCity, true, false);
            return;
          }}
        }}

        // L. Country Inquiries
        const matchedCountry = COUNTRY_CENTROIDS.find(c => q.includes(c.name.toLowerCase()) || q.includes(c.name.toLowerCase().replace('united states', 'usa')));
        if (matchedCountry) {{
          const countryMatches = ALL_INSTITUTIONS.filter(i => matchC(i.country, matchedCountry.name));
          if (countryMatches.length > 0) {{
            const co1 = countryMatches[0];
            const co2 = countryMatches[1];
            const co3 = countryMatches[2];
            appendCuratorMessage(`
              <p class="text-slate-200">
                Across <strong>${{escapeHtml(matchedCountry.name)}}</strong>, Culture Atlas tracks <strong>${{countryMatches.length}}</strong> verified cultural spaces where public accountability and artistic autonomy take priority over private commercial influence.
              </p>
              <p class="text-slate-300">
                Remarkable spaces to explore include ${{formatInstLink(co1)}}${{co2 ? `, ${{formatInstLink(co2)}}` : ''}}${{co3 ? `, and ${{formatInstLink(co3)}}` : ''}}.
              </p>
            `);

            flyTo(matchedCountry.lon, matchedCountry.lat);
            return;
          }}
        }}

        // M. Specific Institution Lookup
        const instMatch = ALL_INSTITUTIONS.find(i => q.includes(i.name.toLowerCase()) || (i.aliases && i.aliases.some(a => q.includes(a.toLowerCase()))) || (i.name.toLowerCase().includes(q) && q.length > 3));
        if (instMatch) {{
          appendCuratorMessage(`
            <p class="text-slate-200">
              ${{formatInstLink(instMatch, {{noCity: false}})}} is an ethical cultural sanctuary founded in ${{instMatch.year_founded}} in the ${{instMatch.neighborhood}} district.
            </p>
            <p class="text-slate-300">
              Governed as an independent <em>${{instMatch.governance_type}}</em>, the institution focuses on ${{instMatch.curatorial_focus}}. Admission is <strong>${{instMatch.admission_policy}}</strong> (${{instMatch.admission_details}}), welcoming visitors ${{instMatch.opening_hours}}.
            </p>
            <p class="text-slate-300">
              When visiting, make sure to experience its signature highlight: <span class="text-amber-300/90 font-medium">${{instMatch.highlight}}</span>. Its verified ethical safeguard confirms: ${{instMatch.ethical_safeguard}}.
            </p>
          `);

          selectInstitution(instMatch, true);
          return;
        }}

        // N. Surprise Me / Recommendations
        if (q.includes('surprise') || q.includes('recommend') || q.includes('random') || q.includes('hidden gem')) {{
          const randomA = ALL_INSTITUTIONS.filter(i => i.tier === 'A');
          const pick1 = randomA[Math.floor(Math.random() * randomA.length)];
          const pick2 = randomA[Math.floor(Math.random() * randomA.length)];

          appendCuratorMessage(`
            <p class="text-slate-200">
              Here are two extraordinary institutions with inspiring ethical commitments and artistic integrity: ${{formatInstLink(pick1)}} and ${{formatInstLink(pick2)}}.
            </p>
            <p class="text-slate-300">
              Both operate with verified independence and champion bold contemporary commissions without corporate sponsor restrictions.
            </p>
          `);

          selectInstitution(pick1, false);
          return;
        }}

        // O. Fallback with helpful conversational guidance
        const dia = ALL_INSTITUTIONS.find(i => i.name.includes('Dia Beacon'));
        const chis = ALL_INSTITUTIONS.find(i => i.name.includes('Chisenhale'));
        const louis = ALL_INSTITUTIONS.find(i => i.name.includes('Louisiana'));
        appendCuratorMessage(`
          <p class="text-slate-200">
            I would be delighted to guide you to ethically funded cultural institutions across <strong>35 countries and 133 cities</strong>.
          </p>
          <p class="text-slate-300">
            Whether you are planning a journey to <a href="#" class="city-link text-[#93c5fd] hover:underline cursor-pointer" data-city="London">London</a>, <a href="#" class="city-link text-[#93c5fd] hover:underline cursor-pointer" data-city="Paris">Paris</a>, or <a href="#" class="city-link text-[#93c5fd] hover:underline cursor-pointer" data-city="New York">New York</a>, or exploring critical theory from <em>Beyond Objecthood</em>, <em>e-flux journal</em>, and institutional critique, I can direct you to uncompromised sanctuaries like ${{formatInstLink(dia)}}, ${{formatInstLink(chis)}}, or ${{formatInstLink(louis)}}.
          </p>
          <p class="text-[#93c5fd]">
            What city or type of art experience would you love to discover today?
          </p>
        `);

      }}, 300);
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
    curatorInput.addEventListener('input', () => {{
      if (curatorInput.value.trim().length > 0) {{
        curatorSendBtn.classList.remove('opacity-60');
        curatorSendBtn.classList.add('opacity-100');
      }} else {{
        curatorSendBtn.classList.add('opacity-60');
        curatorSendBtn.classList.remove('opacity-100');
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

    // Delegated click listener in chat messages for inline links, cards, & city mentions
    curatorMessages.addEventListener('click', (e) => {{
      // 1. Check for institution links
      const instLink = e.target.closest('.inst-link, [data-inst]');
      if (instLink) {{
        e.preventDefault();
        e.stopPropagation();
        const name = instLink.getAttribute('data-name') || instLink.getAttribute('data-inst') || instLink.textContent.trim();
        const inst = ALL_INSTITUTIONS.find(i => i.name === name || (i.name.toLowerCase() === name.toLowerCase()) || (i.aliases && i.aliases.some(a => a.toLowerCase() === name.toLowerCase())));
        if (inst) {{
          selectInstitution(inst, true);
        }}
        return;
      }}

      // 2. Check for audit dossier links
      const dossierLink = e.target.closest('.dossier-link, .curator-dossier-btn, [data-dossier]');
      if (dossierLink) {{
        e.preventDefault();
        e.stopPropagation();
        const name = dossierLink.getAttribute('data-name') || dossierLink.getAttribute('data-dossier');
        const inst = ALL_INSTITUTIONS.find(i => i.name === name || (i.name.toLowerCase() === name.toLowerCase()));
        if (inst) {{
          openDossier(inst);
        }}
        return;
      }}

      // 3. Check for city links
      const cityLink = e.target.closest('.city-link, .city-zoom-btn, [data-city]');
      if (cityLink) {{
        e.preventDefault();
        e.stopPropagation();
        const city = cityLink.getAttribute('data-city') || cityLink.textContent.trim();
        if (city) {{
          filterByCity(city, true, false);
        }}
        return;
      }}

      // 4. Check for prompt links
      const promptLink = e.target.closest('.prompt-link, [data-prompt]');
      if (promptLink) {{
        e.preventDefault();
        e.stopPropagation();
        const p = promptLink.getAttribute('data-prompt') || promptLink.textContent.trim().replace(/^["']|["']$/g, '');
        if (p) {{
          appendUserMessage(p);
          handleCuratorQuery(p);
        }}
        return;
      }}

      // 5. Backwards compatibility for cards or fly buttons
      const card = e.target.closest('.curator-inst-card');
      if (card && !e.target.closest('a') && !e.target.closest('.curator-dossier-btn')) {{
        e.preventDefault();
        e.stopPropagation();
        const name = card.getAttribute('data-name');
        const inst = ALL_INSTITUTIONS.find(i => i.name === name);
        if (inst) {{
          selectInstitution(inst, true);
        }}
        return;
      }}

      const btn = e.target.closest('.curator-fly-btn');
      if (btn) {{
        e.preventDefault();
        e.stopPropagation();
        const instName = btn.getAttribute('data-name');
        if (instName) {{
          const inst = ALL_INSTITUTIONS.find(i => i.name === instName);
          if (inst) {{
            selectInstitution(inst, true);
          }}
          return;
        }}
      }}

      // 6. Check if user clicked any text or element mentioning any mapped city
      const txt = (e.target.textContent || '').trim();
      const matchedCityClick = findMentionedCity(txt);
      if (matchedCityClick) {{
        if (e.target.tagName === 'BUTTON' || e.target.tagName === 'A' || e.target.tagName === 'STRONG' || e.target.closest('button, a')) {{
          filterByCity(matchedCityClick, true, false);
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
        tabCuratorBtn.className = 'py-1 px-3 rounded-lg transition text-center flex items-center justify-center gap-1.5 bg-[#2f2f2f] text-white font-medium shadow-sm';
        tabCatalogBtn.className = 'py-1 px-3 rounded-lg transition text-center flex items-center justify-center gap-1.5 text-[#a1a1aa] hover:text-white';
        curatorPanel.classList.remove('hidden');
        catalogPanel.classList.add('hidden');
      }} else {{
        tabCatalogBtn.className = 'py-1 px-3 rounded-lg transition text-center flex items-center justify-center gap-1.5 bg-[#2f2f2f] text-white font-medium shadow-sm';
        tabCuratorBtn.className = 'py-1 px-3 rounded-lg transition text-center flex items-center justify-center gap-1.5 text-[#a1a1aa] hover:text-white';
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

    // Curator Intelligence Settings Modal (Multi-Provider: Claude, OpenAI, Gemini)
    const settingsModal = document.getElementById('curatorSettingsModal');
    const aiApiKeyInput = document.getElementById('aiApiKeyInput');
    const aiModelSelect = document.getElementById('aiModelSelect');
    const keyDetectBadge = document.getElementById('keyDetectBadge');
    const connectionTestBox = document.getElementById('connectionTestBox');
    const testStatusIcon = document.getElementById('testStatusIcon');
    const testStatusMsg = document.getElementById('testStatusMsg');
    const toggleKeyVisibilityBtn = document.getElementById('toggleKeyVisibilityBtn');
    const providerTip = document.getElementById('providerTip');

    let currentSelectedProvider = getEffectiveProvider();

    const PROVIDER_MODELS = {{
      anthropic: [
        {{ id: 'claude-haiku-4-5-20251001', name: 'claude-haiku-4-5-20251001 (Fast & Articulate - Recommended)' }},
        {{ id: 'claude-sonnet-4-5-20250929', name: 'claude-sonnet-4-5-20250929 (Deep Critical Reasoning)' }}
      ],
      openai: [
        {{ id: 'gpt-4o-mini', name: 'gpt-4o-mini (Fast & Versatile)' }},
        {{ id: 'gpt-4o', name: 'gpt-4o (Full Reasoning)' }}
      ],
      gemini: [
        {{ id: 'gemini-2.5-flash', name: 'gemini-2.5-flash (Fast & Multimodal)' }},
        {{ id: 'gemini-1.5-flash', name: 'gemini-1.5-flash (Reliable Fallback)' }}
      ]
    }};

    function updateProviderUI(prov) {{
      currentSelectedProvider = prov;
      const claudeBtn = document.getElementById('providerClaudeBtn');
      const openaiBtn = document.getElementById('providerOpenAIBtn');
      const geminiBtn = document.getElementById('providerGeminiBtn');

      [claudeBtn, openaiBtn, geminiBtn].forEach(b => {{
        if (b) {{
          b.classList.remove('bg-[#27272a]', 'text-white', 'border-[#3e3e3e]');
          b.classList.add('bg-[#1f1f23]', 'text-[#a1a1aa]', 'border-[#27272a]');
        }}
      }});

      const activeBtn = prov === 'anthropic' ? claudeBtn : (prov === 'openai' ? openaiBtn : geminiBtn);
      if (activeBtn) {{
        activeBtn.classList.remove('bg-[#1f1f23]', 'text-[#a1a1aa]', 'border-[#27272a]');
        activeBtn.classList.add('bg-[#27272a]', 'text-white', 'border-[#3e3e3e]');
      }}

      // Populate model options
      const models = PROVIDER_MODELS[prov] || PROVIDER_MODELS.anthropic;
      aiModelSelect.innerHTML = models.map(m => `<option value="${{m.id}}">${{m.name}}</option>`).join('');
      if (aiModel) aiModelSelect.value = aiModel;

      // Update Tip
      if (providerTip) {{
        if (prov === 'anthropic') {{
          providerTip.innerHTML = 'Recommended: <strong>Claude 3.5 / Haiku 4.5</strong> excels at art theory, <em>Beyond Objecthood</em>, e-flux criticism, and institutional analysis.';
        }} else if (prov === 'openai') {{
          providerTip.innerHTML = 'OpenAI <strong>GPT-4o / GPT-4o-mini</strong> provides fast conversational guidance across all 203 mapped sanctuaries.';
        }} else {{
          providerTip.innerHTML = 'Google <strong>Gemini 2.5 Flash</strong> provides responsive real-time multimodal reasoning.';
        }}
      }}
    }}

    document.getElementById('providerClaudeBtn')?.addEventListener('click', () => updateProviderUI('anthropic'));
    document.getElementById('providerOpenAIBtn')?.addEventListener('click', () => updateProviderUI('openai'));
    document.getElementById('providerGeminiBtn')?.addEventListener('click', () => updateProviderUI('gemini'));

    document.getElementById('curatorSettingsBtn')?.addEventListener('click', () => {{
      settingsModal.classList.remove('hidden');
      aiApiKeyInput.value = aiApiKey;
      updateProviderUI(getEffectiveProvider());
      updateDetectBadge(aiApiKey);
      connectionTestBox.classList.add('hidden');
    }});

    document.getElementById('closeSettingsModalBtn')?.addEventListener('click', () => {{
      settingsModal.classList.add('hidden');
    }});

    toggleKeyVisibilityBtn?.addEventListener('click', () => {{
      if (aiApiKeyInput.type === 'password') {{
        aiApiKeyInput.type = 'text';
        toggleKeyVisibilityBtn.textContent = '🔒';
      }} else {{
        aiApiKeyInput.type = 'password';
        toggleKeyVisibilityBtn.textContent = '👁️';
      }}
    }});

    function updateDetectBadge(val) {{
      const k = (val || '').trim();
      if (!k) {{
        keyDetectBadge.textContent = 'Auto-detecting provider...';
        keyDetectBadge.className = 'text-[14px] font-mono text-[#a1a1aa]';
        return;
      }}
      if (k.startsWith('sk-ant-')) {{
        keyDetectBadge.textContent = '🟣 Anthropic Claude key detected';
        keyDetectBadge.className = 'text-[14px] font-mono text-purple-400';
        updateProviderUI('anthropic');
      }} else if (k.startsWith('sk-') || k.startsWith('sk-proj-')) {{
        keyDetectBadge.textContent = '🟢 OpenAI key detected';
        keyDetectBadge.className = 'text-[14px] font-mono text-emerald-400';
        updateProviderUI('openai');
      }} else if (k.startsWith('AIza')) {{
        keyDetectBadge.textContent = '🔵 Google Gemini key detected';
        keyDetectBadge.className = 'text-[14px] font-mono text-blue-400';
        updateProviderUI('gemini');
      }} else {{
        keyDetectBadge.textContent = 'Custom API key';
        keyDetectBadge.className = 'text-[14px] font-mono text-amber-400';
      }}
    }}

    aiApiKeyInput?.addEventListener('input', (e) => {{
      updateDetectBadge(e.target.value);
    }});

    document.getElementById('testConnectionBtn')?.addEventListener('click', async () => {{
      const key = aiApiKeyInput.value.trim();
      const model = aiModelSelect.value;
      connectionTestBox.classList.remove('hidden', 'border-emerald-500/30', 'bg-emerald-500/10', 'text-emerald-400', 'border-rose-500/30', 'bg-rose-500/10', 'text-rose-400');
      connectionTestBox.classList.add('border-[#3e3e3e]', 'bg-[#27272a]', 'text-[#d4d4d4]');
      testStatusIcon.textContent = '⏳';
      testStatusMsg.textContent = 'Testing connection with live API...';

      const res = await testAPIConnection(currentSelectedProvider, key, model);
      if (res.success) {{
        connectionTestBox.classList.remove('border-[#3e3e3e]', 'bg-[#27272a]', 'text-[#d4d4d4]');
        connectionTestBox.classList.add('border-emerald-500/30', 'bg-emerald-500/10', 'text-emerald-400');
        testStatusIcon.textContent = '✓';
        testStatusMsg.textContent = res.message;
      }} else {{
        connectionTestBox.classList.remove('border-[#3e3e3e]', 'bg-[#27272a]', 'text-[#d4d4d4]');
        connectionTestBox.classList.add('border-rose-500/30', 'bg-rose-500/10', 'text-rose-400');
        testStatusIcon.textContent = '✕';
        testStatusMsg.textContent = res.error;
      }}
    }});

    document.getElementById('saveApiKeyBtn')?.addEventListener('click', () => {{
      aiApiKey = aiApiKeyInput.value.trim();
      aiProvider = currentSelectedProvider;
      aiModel = aiModelSelect.value;
      localStorage.setItem('atlas_ai_api_key', aiApiKey);
      localStorage.setItem('atlas_ai_provider', aiProvider);
      localStorage.setItem('atlas_ai_model', aiModel);
      updateAIStatusUI();
      settingsModal.classList.add('hidden');
    }});

    document.getElementById('clearApiKeyBtn')?.addEventListener('click', () => {{
      aiApiKey = '';
      aiProvider = 'auto';
      aiModel = '';
      aiApiKeyInput.value = '';
      localStorage.removeItem('atlas_ai_api_key');
      localStorage.removeItem('atlas_gemini_api_key');
      localStorage.removeItem('atlas_ai_provider');
      localStorage.removeItem('atlas_ai_model');
      updateAIStatusUI();
      connectionTestBox.classList.add('hidden');
      settingsModal.classList.add('hidden');
    }});

    // Initialize UI Status on startup
    updateAIStatusUI();

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
        const tierCol = inst.tier === 'A' ? 'text-emerald-400 border-emerald-900/60 bg-[#0a2016]' : inst.tier === 'B' ? 'text-blue-400 border-blue-900/60 bg-[#0d1d33]' : 'text-slate-400 border-slate-700 bg-[#161922]';
        const tierName = inst.tier === 'A' ? 'Tier A · Verified' : inst.tier === 'B' ? 'Tier B · One Name' : 'Tier U';

        let displayDomain = 'website';
        try {{
          displayDomain = new URL(inst.website || inst.sources[0]).hostname.replace(/^www\\./, '');
        }} catch(e) {{}}

        return `
          <div class="inst-card bg-[#212121] border border-[#2e2e2e] rounded-2xl p-3.5 cursor-pointer hover:border-[#444] hover:bg-[#282828] transition ${{isSel ? 'border-[#3b82f6] bg-[#222834]' : ''}}" data-name="${{inst.name.replace(/"/g, '&quot;')}}">
            <div class="flex items-start justify-between gap-2">
              <h3 class="font-medium text-white text-[14px] leading-snug truncate max-w-[220px] sm:max-w-[260px]">${{inst.name}}</h3>
              <span class="text-[14px] px-2 py-0.5 rounded-lg border ${{tierCol}} shrink-0">${{tierName}}</span>
            </div>
            
            <div class="flex items-center gap-1.5 text-[14px] text-[#93c5fd] mt-1 font-mono">
              <span>📍</span> <span class="truncate">${{inst.location}}</span>
              <span class="text-[#555]">·</span>
              <span class="text-[#a1a1aa] text-[14px] shrink-0">Est. ${{inst.year_founded}}</span>
            </div>

            <!-- Researcher Tags: Governance & Admission -->
            <div class="flex items-center gap-1.5 text-[14px] font-mono text-[#a1a1aa] mt-2 flex-wrap">
              <span class="px-2 py-0.5 rounded-lg bg-[#2a2a2a] border border-[#383838] text-[#d4d4d4]">🏛️ ${{inst.governance_type}}</span>
              <span class="px-2 py-0.5 rounded-lg bg-[#2a2a2a] border border-[#383838] text-[#d4d4d4]">🎟️ ${{inst.admission_policy}}</span>
            </div>

            <!-- Quick Visitor Schedule & Pricing Pill -->
            <div class="mt-1.5 flex items-center gap-2 text-[14px] font-mono text-[#a1a1aa]">
              <span class="truncate">🕒 ${{inst.opening_hours ? inst.opening_hours.split(',')[0] : 'Open Weekly'}}</span>
              <span class="text-[#555]">·</span>
              <span class="text-emerald-400 shrink-0 truncate max-w-[120px]">🎟️ ${{inst.admission_fee ? inst.admission_fee.split('/')[0].trim() : 'Free / Subsidized'}}</span>
            </div>

            <p class="text-[14px] text-[#d4d4d4] mt-2 leading-relaxed line-clamp-2">${{inst.curator_recommendation || inst.funding}}</p>
            
            ${{inst.watch ? `
              <div class="mt-2 pt-1.5 border-t border-[#2e2e2e] text-[14px] text-amber-300/80 truncate flex items-center gap-1 font-mono">
                <span>⚠️</span> <span>${{inst.watch}}</span>
              </div>
            ` : ''}}
            
            <div class="mt-2.5 pt-2 border-t border-[#2e2e2e] flex items-center justify-between">
              <a href="${{inst.website || inst.sources[0]}}" target="_blank" rel="noopener noreferrer" 
                 class="website-pill inline-flex items-center gap-1 text-[14px] font-mono text-[#93c5fd] hover:text-white bg-[#2a2a2a] hover:bg-[#333] border border-[#383838] px-2.5 py-0.5 rounded-lg transition"
                 onclick="event.stopPropagation()">
                <span>🌐</span>
                <span class="truncate max-w-[120px]">${{displayDomain}}</span>
                <span class="text-[14px]">↗</span>
              </a>
              <span class="text-[14px] text-[#71717a] hover:text-white font-mono transition">View on Globe →</span>
            </div>
          </div>
        `;
      }}).join('');

      container.querySelectorAll('.inst-card').forEach(card => {{
        card.addEventListener('click', () => {{
          const name = card.getAttribute('data-name');
          const inst = ALL_INSTITUTIONS.find(i => i.name === name);
          if (inst) {{
            selectInstitution(inst, true);
          }}
        }});
      }});
    }}

    function filterByCity(cityName, zoom = true, notifyCurator = true) {{
      selectedCityFilter = cityName;
      selectedCountryFilter = 'all';
      applyFilters();

      const cty = PRIORITY_CITIES.find(c => c.name.toLowerCase() === cityName.toLowerCase());
      const targetZoom = zoom ? baseRadius * 4.0 : null;

      if (cty) {{
        flyTo(cty.lon, cty.lat, targetZoom);
      }} else {{
        const inst = ALL_INSTITUTIONS.find(i => i.city.toLowerCase() === cityName.toLowerCase());
        if (inst) flyTo(inst.lon, inst.lat, targetZoom);
      }}

      if (zoom) {{
        targetRadius = baseRadius * 4.0;
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
        const topInsts = cityMatches.slice(0, 3).map(i => formatInstLink(i, {{noCity: true}})).join(', ');
        appendCuratorMessage(`
          <p class="text-slate-200">
            We are now exploring <a href="#" class="city-link font-semibold text-white hover:text-[#60a5fa] underline cursor-pointer" data-city="${{escapeHtml(cityName)}}">${{escapeHtml(cityName)}}</a>, home to <strong>${{cityMatches.length}}</strong> verified ethical cultural sanctuaries.
          </p>
          <p class="text-slate-300">
            Standout spaces here include ${{topInsts}}. Each operates with transparent public governance and clean underwriting without fossil-fuel or defense sponsorship.
          </p>
        `);
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
        const topInsts = countryMatches.slice(0, 3).map(i => formatInstLink(i)).join(', ');
        appendCuratorMessage(`
          <p class="text-slate-200">
            Across <strong>${{escapeHtml(countryName)}}</strong>, Culture Atlas tracks <strong>${{countryMatches.length}}</strong> cultural institutions prioritizing public accountability and artistic autonomy.
          </p>
          <p class="text-slate-300">
            Exemplary spaces to explore include ${{topInsts}}.
          </p>
        `);
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
      // If clicked empty ocean or space on the globe, dismiss the floating institution card
      if (selectedInstitution) {{
        deselectInstitution();
      }}
    }}

    document.getElementById('closeFloatingCardBtn')?.addEventListener('click', (e) => {{
      e.stopPropagation();
      deselectInstitution();
    }});

    document.getElementById('floatingCardDossierBtn')?.addEventListener('click', (e) => {{
      e.stopPropagation();
      if (selectedInstitution) openDossier(selectedInstitution);
    }});

    document.getElementById('floatingCard')?.addEventListener('click', (e) => {{
      if (e.target.closest('a') || e.target.closest('button')) return;
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
    dest_root = "/Users/polinavasilyeva/.gemini/antigravity/scratch/sponsor-atlas/index.html"
    with open(dest_root, "w", encoding="utf-8") as f:
        f.write(html)
    print("Synchronized root index.html!")

    dest_app = "/Users/polinavasilyeva/.gemini/antigravity/scratch/sponsor-atlas/app/index.html"
    with open(dest_app, "w", encoding="utf-8") as f:
        f.write(html)
    print("Wrote researcher-enhanced app/index.html!")

    dest_standalone = "/Users/polinavasilyeva/.gemini/antigravity/scratch/sponsor-atlas/app/standalone.html"
    with open(dest_standalone, "w", encoding="utf-8") as f:
        f.write(html)
    print("Synchronized app/standalone.html!")

    dest_artifact = "/Users/polinavasilyeva/.gemini/antigravity/brain/b997e616-4551-453e-83cc-4ba184f90abf/culture_atlas_app.html"
    local_key = ""
    try:
        env_content = open("/Users/polinavasilyeva/design-interview/.env", "r").read().strip()
        for line in env_content.splitlines():
            line = line.strip()
            if line.startswith("sk-ant-") or "sk-ant-" in line:
                local_key = line.split("=")[-1].strip()
                break
    except Exception:
        pass

    artifact_html = html
    if local_key:
        preseed_script = f"""
  <script>
    if (!localStorage.getItem('atlas_ai_api_key')) {{
      localStorage.setItem('atlas_ai_api_key', '{local_key}');
      localStorage.setItem('atlas_ai_provider', 'anthropic');
      localStorage.setItem('atlas_ai_model', 'claude-haiku-4-5-20251001');
      if (typeof updateAIStatusUI === 'function') updateAIStatusUI();
    }}
  </script>
</body>
"""
        artifact_html = artifact_html.replace("</body>", preseed_script, 1)

    with open(dest_artifact, "w", encoding="utf-8") as f:
        f.write(artifact_html)
    print("Mirrored to culture_atlas_app.html with local intelligence ready!")

if __name__ == "__main__":
    build()
