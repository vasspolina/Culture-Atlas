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

    import base64
    b64_reg = base64.b64encode(open('app/fonts/PPTelegraf-Regular.otf', 'rb').read()).decode('ascii')

    widget_html = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover" />
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
      background-color: transparent;
      color: #f8fafc;
      overflow: hidden;
    }}
    .font-mono {{
      font-family: 'PP Telegraf', 'PP Telegraph', sans-serif !important;
      letter-spacing: -0.01em;
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
      height: 3px;
    }}
    .custom-scroll::-webkit-scrollbar-thumb {{
      background: #232838;
      border-radius: 3px;
    }}
    .widget-item.active {{
      border-color: #3b82f6 !important;
      background-color: #101626 !important;
    }}
    #wGlobePanel {{
      transition: height 0.3s cubic-bezier(0.16, 1, 0.3, 1);
    }}
    #wCuratorPanel {{
      transition: height 0.3s cubic-bezier(0.16, 1, 0.3, 1);
    }}
  </style>
</head>
<body class="p-1 sm:p-2 antialiased">
  <div class="bg-[#171717] text-white border border-[#262626] rounded-3xl p-2.5 sm:p-3 shadow-2xl overflow-hidden flex flex-col gap-2 h-[500px]">
    
    <!-- Header with Tagline -->
    <div class="flex items-center justify-between border-b border-[#262626] pb-2 px-1 shrink-0">
      <div>
        <div class="flex items-center gap-2">
          <div class="w-2 h-2 rounded-full bg-white"></div>
          <span class="text-[18px] font-bold tracking-wider text-white uppercase">CULTURE ATLAS</span>
          <span class="text-[14px] text-emerald-400 bg-[#0a2016] px-1.5 py-0.2 rounded-lg border border-emerald-900/60">203 SANCTUARIES</span>
        </div>
        <p class="text-[14px] text-[#a1a1aa] font-normal leading-snug mt-0.5">
          Ethically funded cultural institutions across the world
        </p>
      </div>

      <!-- Globe Quick Controls -->
      <div class="flex items-center gap-1.5 text-[14px]">
        <button id="wResetBtn" class="px-2.5 py-1 rounded-xl bg-[#212121] hover:bg-[#282828] border border-[#2e2e2e] text-[#d4d4d4] hover:text-white transition">🔄 Reset</button>
        <button id="wSpinBtn" class="px-2.5 py-1 rounded-xl bg-[#212121] hover:bg-[#282828] border border-[#2e2e2e] text-[#93c5fd] hover:text-white transition">⟳ Spin</button>
      </div>
    </div>

    <!-- Active Filter Banner (When city/country clicked) -->
    <div id="wMobileFilterBanner" class="hidden flex items-center justify-between bg-[#212121] border border-[#333] px-3 py-1 rounded-xl text-[14px] shrink-0">
      <span id="wMobileFilterText" class="font-medium text-white truncate text-[14px]">📍 NEW YORK (11)</span>
      <button id="wMobileClearFilter" class="text-[14px] text-[#a1a1aa] hover:text-white">✕ Clear</button>
    </div>

    <!-- TOP HALF: 🌍 3D GLOBE PANEL (Half Screen) -->
    <div id="wGlobePanel" class="relative w-full h-[200px] flex items-center justify-center bg-[#000000] rounded-2xl border border-[#262626] overflow-hidden shrink-0">
      <canvas id="widgetCanvas" class="w-full h-full block cursor-grab"></canvas>

      <!-- Floating Dark Pin Card -->
      <div id="wCard" class="hidden absolute z-30 pointer-events-auto bg-[#18181b]/95 backdrop-blur-md text-slate-100 rounded-2xl p-2.5 shadow-xl transition transform -translate-x-1/2 -translate-y-full mb-2 cursor-pointer border border-[#2e2e2e] max-w-[240px]">
        <div class="flex items-start justify-between gap-1">
          <div class="truncate pr-1">
            <div class="text-[14px] font-medium text-white leading-tight truncate" id="wCardTitle"></div>
            <div class="text-[14px] text-[#a1a1aa] mt-0.5 truncate" id="wCardMeta"></div>
          </div>
          <button id="wCardCloseBtn" class="text-[#a1a1aa] hover:text-white p-0.5 rounded text-[14px] leading-none shrink-0 cursor-pointer" title="Close">✕</button>
        </div>
        <div class="mt-1.5 pt-1.5 border-t border-[#2e2e2e] flex items-center justify-between text-[14px]">
          <a id="wCardLink" href="#" target="_blank" rel="noopener noreferrer" 
             class="text-[#93c5fd] hover:text-white flex items-center gap-1 transition cursor-pointer" onclick="event.stopPropagation()">
            <span>🌐</span> <span id="wCardDom">website</span> <span>↗</span>
          </a>
          <button id="wCardCuratorBtn" class="text-white hover:text-[#93c5fd] font-medium transition cursor-pointer" onclick="event.stopPropagation()">
            💬 Ask
          </button>
        </div>
        <div class="absolute bottom-0 left-1/2 -translate-x-1/2 translate-y-full w-0 h-0 border-x-[5px] border-x-transparent border-t-[5px] border-t-[#18181b]"></div>
      </div>

      <div class="absolute bottom-1.5 left-2 text-[14px] text-[#71717a] pointer-events-none">
        <span>└───┘ 2,000 km</span>
      </div>

      <div class="absolute top-1.5 right-2 text-[14px] text-[#71717a] pointer-events-none bg-[#171717]/80 px-2 py-0.5 rounded-lg border border-[#2e2e2e]">
        Tap city or pin
      </div>
    </div>

    <!-- BOTTOM HALF: 💬 CHAT CONVERSATIONAL PANEL (Half Sheet) -->
    <div id="wCuratorPanel" class="flex-1 flex flex-col bg-[#171717] border border-[#262626] rounded-2xl overflow-hidden min-h-0">
      
      <!-- Sheet Header: Drag Handle & Open/Close Bar -->
      <div id="wSheetHeader" class="px-3 py-1.5 border-b border-[#262626] bg-[#171717] flex items-center justify-between gap-1.5 shrink-0 select-none cursor-pointer">
        <div class="flex items-center gap-2 truncate">
          <div class="w-6 h-1 bg-[#3a3a3a] rounded-full shrink-0"></div>
          <span class="text-[14px] font-medium text-white truncate">Curator Guide</span>
          <span id="wSheetBadge" class="text-[14px] text-emerald-400 bg-[#0a2016] px-1.5 py-0.2 rounded-lg border border-emerald-900/60 hidden xs:inline">Half Sheet</span>
        </div>
        <div class="flex items-center gap-1.5 text-[14px] text-[#a1a1aa] bg-[#212121] border border-[#2e2e2e] px-2 py-0.5 rounded-xl">
          <button id="wMinimizeBtn" class="hover:text-white transition cursor-pointer">Minimize</button>
          <span class="text-[#555]">·</span>
          <button id="wExpandBtn" class="hover:text-white transition cursor-pointer">Expand</button>
        </div>
      </div>

      <!-- Conversation Feed -->
      <div id="wCuratorMessages" class="flex-1 overflow-y-auto custom-scroll p-3 space-y-3 text-[14px]">
        <!-- Messages injected dynamically -->
      </div>

      <!-- Inquiry Prompt Chips: Sleek ChatGPT style (User Copywriting) -->
      <div id="wInquiryCarousel" class="px-3 py-1.5 border-t border-[#262626] bg-[#171717] flex items-center gap-1.5 overflow-x-auto custom-scroll text-[14px] whitespace-nowrap shrink-0">
        <button class="w-inquiry px-3 py-0.5 rounded-full border border-[#2e2e2e] bg-[#212121] text-[#d4d4d4] hover:bg-[#282828] hover:text-white transition" data-query="Find independent art spaces near me">
          Find spaces near me
        </button>
        <button class="w-inquiry px-3 py-0.5 rounded-full border border-[#2e2e2e] bg-[#212121] text-[#d4d4d4] hover:bg-[#282828] hover:text-white transition" data-query="Who funds this museum?">
          Who funds this museum?
        </button>
        <button class="w-inquiry px-3 py-0.5 rounded-full border border-[#2e2e2e] bg-[#212121] text-[#d4d4d4] hover:bg-[#282828] hover:text-white transition" data-query="What are the opening hours and ticket prices?">
          Hours & ticket prices
        </button>
        <button class="w-inquiry px-3 py-0.5 rounded-full border border-[#2e2e2e] bg-[#212121] text-[#d4d4d4] hover:bg-[#282828] hover:text-white transition" data-query="Find writing about this space in e-flux or MIT Press">
          e-flux & MIT Press
        </button>
        <button class="w-inquiry px-3 py-0.5 rounded-full border border-[#2e2e2e] bg-[#212121] text-[#d4d4d4] hover:bg-[#282828] hover:text-white transition" data-query="How does Culture Atlas research and audit museum funding?">
          Research method
        </button>
        <button class="w-inquiry px-3 py-0.5 rounded-full border border-[#2e2e2e] bg-[#212121] text-[#d4d4d4] hover:bg-[#282828] hover:text-white transition" data-query="What landmark exhibitions changed art history?">
          Landmark shows
        </button>
        <button class="w-inquiry px-3 py-0.5 rounded-full border border-[#2e2e2e] bg-[#212121] text-[#d4d4d4] hover:bg-[#282828] hover:text-white transition" data-query="How are museums handling stolen colonial artifacts?">
          Restitution
        </button>
        <button class="w-inquiry px-3 py-0.5 rounded-full border border-[#2e2e2e] bg-[#212121] text-[#d4d4d4] hover:bg-[#282828] hover:text-white transition" data-query="What are the essential MIT Press books on museums and art theory?">
          MIT Press books
        </button>
        <button class="w-inquiry px-3 py-0.5 rounded-full border border-[#2e2e2e] bg-[#212121] text-[#d4d4d4] hover:bg-[#282828] hover:text-white transition" data-query="Explain Rosalind Krauss's critique of the late capitalist museum">
          Late capitalist museum
        </button>
        <button class="w-inquiry px-3 py-0.5 rounded-full border border-[#2e2e2e] bg-[#212121] text-[#d4d4d4] hover:bg-[#282828] hover:text-white transition" data-query="Explain Miwon Kwon's 'One Place after Another' and site-specific art">
          Site-specific art
        </button>
        <button class="w-inquiry px-3 py-0.5 rounded-full border border-[#2e2e2e] bg-[#212121] text-[#d4d4d4] hover:bg-[#282828] hover:text-white transition" data-query="Which museums and galleries are free to enter?">
          Free admission
        </button>
        <button class="w-inquiry px-3 py-0.5 rounded-full border border-[#2e2e2e] bg-[#212121] text-[#d4d4d4] hover:bg-[#282828] hover:text-white transition" data-query="Which museums are open on Mondays?">
          Hours & Mondays
        </button>
        <button class="w-inquiry px-3 py-0.5 rounded-full border border-[#2e2e2e] bg-[#212121] text-[#d4d4d4] hover:bg-[#282828] hover:text-white transition" data-query="How do I get to Dia Beacon or Louisiana by train?">
          Transit tips
        </button>
        <button class="w-inquiry px-3 py-0.5 rounded-full border border-[#2e2e2e] bg-[#212121] text-[#d4d4d4] hover:bg-[#282828] hover:text-white transition" data-query="What are the best artist-run spaces to visit?">
          Artist-run centers
        </button>
        <button class="w-inquiry px-3 py-0.5 rounded-full border border-[#2e2e2e] bg-[#212121] text-[#d4d4d4] hover:bg-[#282828] hover:text-white transition" data-query="How do you decide if a museum has clean funding?">
          Clean funding
        </button>
      </div>

      <!-- Chat Input Bar: Sleek ChatGPT floating pill -->
      <div id="wInputBar" class="p-2 border-t border-[#262626] bg-[#171717] shrink-0">
        <div class="relative flex items-center bg-[#212121] border border-[#333333] hover:border-[#444] focus-within:border-[#555] rounded-3xl p-1 pl-3.5 pr-1 shadow-sm transition">
          <input id="wCuratorInput" type="text" placeholder="Ask about a museum or cultural space" class="w-full bg-transparent border-0 text-[14px] text-white placeholder-[#71717a] focus:outline-none py-1 font-sans" />
          <button id="wCuratorSend" class="w-7 h-7 rounded-full bg-white text-black hover:bg-neutral-200 transition active:scale-95 flex items-center justify-center shrink-0 shadow-sm ml-1" title="Send">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
              <path d="M12 19V5M5 12l7-7 7 7"/>
            </svg>
          </button>
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

    let filterCountry = 'all';
    let filterCity = 'all';
    let selectedInst = null;

    const canvas = document.getElementById('widgetCanvas');
    const ctx = canvas.getContext('2d', {{ alpha: false }});
    
    let dpr = Math.max(1, Math.min(window.devicePixelRatio || 1, 3));
    let width = 460;
    let height = 360;

    function resizeCanvas() {{
      if (!canvas.parentElement) return;
      const rect = canvas.parentElement.getBoundingClientRect();
      dpr = Math.max(1, Math.min(window.devicePixelRatio || 1, 3));
      width = Math.round(rect.width) || canvas.parentElement.clientWidth || 460;
      height = Math.round(rect.height) || canvas.parentElement.clientHeight || 360;

      canvas.width = Math.round(width * dpr);
      canvas.height = Math.round(height * dpr);
      canvas.style.width = width + 'px';
      canvas.style.height = height + 'px';

      baseRadius = Math.min(width, height) * 0.35;
      targetRadius = baseRadius;
    }}
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);

    let baseRadius = Math.min(width, height) * 0.35;
    let currentRadius = baseRadius;
    let targetRadius = baseRadius;

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

    function resize() {{
      if (!canvas.parentElement) return;
      width = canvas.width = canvas.parentElement.clientWidth || 460;
      height = canvas.height = canvas.parentElement.clientHeight || 360;
      baseRadius = Math.min(width, height) * 0.35;
      currentRadius = targetRadius = baseRadius;
    }}
    window.addEventListener('resize', resize);

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

    function easeInOutQuad(t) {{
      return t < 0.5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2;
    }}

    let cityBadgeHitboxes = [];
    let visibleDots = [];

    function render() {{
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

      ctx.beginPath();
      ctx.arc(cx, cy, r, 0, Math.PI * 2);
      ctx.fillStyle = '#010204';
      ctx.fill();
      ctx.strokeStyle = '#182030';
      ctx.lineWidth = 1;
      ctx.stroke();

      for (let i = 0; i < COUNTRY_POLYS.length; i++) {{
        const country = COUNTRY_POLYS[i];
        const isCActive = filterCountry !== 'all' && (country.n.toLowerCase() === filterCountry.toLowerCase());
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

      // Priority City Badges
      cityBadgeHitboxes = [];
      ctx.font = '14px "PP Telegraf", "PP Telegraph", sans-serif';
      PRIORITY_CITIES.forEach(city => {{
        const pt = project(city.lon, city.lat, r, cx, cy);
        if (pt.front && pt.depth > 0.08) {{
          const isSelected = filterCity.toLowerCase() === city.name.toLowerCase();
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
        }}
      }});

      // Dots
      visibleDots = [];
      const filteredData = DATA.filter(inst => {{
        if (wCategoryFilter === 'all') return true;
        if (wCategoryFilter === 'free') return (inst.admission_policy || '').toLowerCase().includes('free');
        if (wCategoryFilter === 'monday') {{
          const h = (inst.opening_hours || '').toLowerCase();
          return !h.includes('closed mon') && (h.includes('daily') || h.includes('mon'));
        }}
        if (wCategoryFilter === 'transit') return inst.transit_tips && inst.transit_tips.length > 5;
        if (wCategoryFilter === 'accessibility') {{
          const a = (inst.accessibility || '').toLowerCase();
          return a.includes('step-free') || a.includes('wheelchair') || a.includes('elevator') || a.includes('accessible');
        }}
        if (wCategoryFilter === 'amenities') {{
          const am = (inst.amenities || '').toLowerCase();
          return am.includes('caf') || am.includes('book') || am.includes('garden') || am.includes('dining');
        }}
        if (wCategoryFilter === 'ethical') return inst.tier === 'A' || inst.governance_type.includes('Civic') || inst.governance_type.includes('Public');
        if (wCategoryFilter === 'artist_run') return (inst.governance_type || '').toLowerCase().includes('artist');
        if (wCategoryFilter === 'fossil_free') {{
          const s = (inst.ethical_safeguard || '').toLowerCase();
          return inst.tier === 'A' || s.includes('divest') || s.includes('fossil') || s.includes('clean');
        }}
        if (wCategoryFilter === 'london') return inst.city.toLowerCase() === 'london';
        if (wCategoryFilter === 'nyc') return inst.city.toLowerCase().includes('new york') || inst.city.toLowerCase().includes('beacon');
        return true;
      }});

      filteredData.forEach(inst => {{
        const pt = project(inst.lon, inst.lat, r, cx, cy);
        if (pt.front && pt.depth > 0.05) {{
          visibleDots.push({{ inst, x: pt.x, y: pt.y }});
          const isSel = selectedInst && selectedInst.name === inst.name;
          ctx.beginPath();
          ctx.arc(pt.x, pt.y, isSel ? 4 : 2, 0, Math.PI * 2);
          ctx.fillStyle = inst.tier === 'A' ? '#10b981' : inst.tier === 'B' ? '#3b82f6' : '#94a3b8';
          ctx.fill();
        }}
      }});

      // Floating Card
      const card = document.getElementById('wCard');
      if (selectedInst) {{
        const pt = project(selectedInst.lon, selectedInst.lat, r, cx, cy);
        if (pt.front && pt.depth > 0.05) {{
          card.classList.remove('hidden');
          card.style.left = `${{pt.x}}px`;
          card.style.top = `${{pt.y}}px`;
        }} else {{
          card.classList.add('hidden');
        }}
      }} else {{
        card.classList.add('hidden');
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

    function deselect() {{
      selectedInst = null;
      const card = document.getElementById('wCard');
      if (card) card.classList.add('hidden');
    }}

    function select(inst, fly = true) {{
      if (!inst) {{
        deselect();
        return;
      }}
      selectedInst = inst;
      document.getElementById('wCardTitle').textContent = inst.name;
      const shortH = inst.opening_hours ? inst.opening_hours.split(',')[0] : '';
      const shortF = inst.admission_fee ? inst.admission_fee.split('/')[0].trim() : '';
      document.getElementById('wCardMeta').textContent = `${{inst.location}} · ${{shortH}} (${{shortF}})`;
      const webUrl = inst.website || (inst.sources && inst.sources[0]) || '';
      let dom = 'website';
      try {{ dom = new URL(webUrl).hostname.replace(/^www\\./, ''); }} catch(e) {{}}
      const link = document.getElementById('wCardLink');
      const domEl = document.getElementById('wCardDom');
      if (link && domEl) {{
        link.href = webUrl;
        domEl.textContent = dom;
      }}
      if (fly) {{
        targetRadius = baseRadius * 4.0;
        flyTo(inst.lon, inst.lat);
      }}
    }}

    // =========================================================
    // 💬 CONVERSATIONAL CURATOR LOGIC (Inline Widget)
    // =========================================================
    const wMessages = document.getElementById('wCuratorMessages');
    const wInput = document.getElementById('wCuratorInput');
    const wSend = document.getElementById('wCuratorSend');

    function escapeHtml(str) {{
      return (str || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
    }}

    function formatWInstLink(inst, opts = {{}}) {{
      if (!inst) return '';
      const webUrl = inst.website || '';
      let domain = 'website';
      try {{ domain = new URL(webUrl).hostname.replace(/^www\\./, ''); }} catch(e) {{}}
      const nameLink = `<a href="#" class="w-inst-link font-medium text-white hover:text-blue-300 underline underline-offset-4 decoration-neutral-500 hover:decoration-blue-400 transition cursor-pointer" data-name="${{escapeHtml(inst.name)}}">${{escapeHtml(inst.name)}}</a>`;
      const cityPart = opts.noCity ? '' : ` in <a href="#" class="w-city-link text-[#93c5fd] hover:text-[#bfdbfe] underline underline-offset-4 decoration-[#93c5fd]/30 hover:decoration-[#bfdbfe] transition cursor-pointer" data-city="${{escapeHtml(inst.city)}}">${{escapeHtml(inst.location || inst.city)}}</a>`;
      const webPart = webUrl ? ` (<a href="${{webUrl}}" target="_blank" rel="noopener noreferrer" class="text-[#a1a1aa] hover:text-white transition text-[14px]">${{domain}} ↗</a>)` : '';
      return `${{nameLink}}${{cityPart}}${{webPart}}`;
    }}

    function appendWCurator(html) {{
      const div = document.createElement('div');
      div.className = 'flex items-start gap-2.5 my-1.5 select-text';

      div.innerHTML = `
        <div class="w-6 h-6 rounded-full bg-[#262626] border border-[#383838] flex items-center justify-center text-[14px] text-white shrink-0 mt-0.5 select-none" title="Curator">
          🏛️
        </div>
        <div class="flex-1 min-w-0 text-[14px] text-[#ececec] leading-relaxed space-y-2 pt-0.5">
          ${{html}}
        </div>
      `;
      wMessages.appendChild(div);

      div.querySelectorAll('.w-inst-link, .w-fly-btn').forEach(btn => {{
        btn.addEventListener('click', (e) => {{
          e.preventDefault();
          const name = btn.getAttribute('data-name');
          const inst = DATA.find(i => i.name === name);
          if (inst) {{
            targetRadius = baseRadius * 4.0;
            select(inst, true);
            if (window.innerWidth < 640) showTab('globe');
          }}
        }});
      }});

      div.querySelectorAll('.w-city-link').forEach(btn => {{
        btn.addEventListener('click', (e) => {{
          e.preventDefault();
          const cityName = btn.getAttribute('data-city');
          const c = PRIORITY_CITIES.find(pc => pc.name.toLowerCase() === cityName.toLowerCase()) || DATA.find(i => i.city.toLowerCase() === cityName.toLowerCase());
          if (c) {{
            targetRadius = baseRadius * 3.8;
            flyTo(c.lon, c.lat);
          }}
          filterCity = cityName;
          if (window.innerWidth < 640) showTab('globe');
        }});
      }});

      wMessages.scrollTop = wMessages.scrollHeight;
    }}

    function appendWUser(text) {{
      const div = document.createElement('div');
      div.className = 'flex justify-end my-1';
      div.innerHTML = `
        <div class="max-w-[85%] bg-[#2f2f2f] text-[#ececec] text-[14px] px-3.5 py-2 rounded-2xl shadow-sm leading-relaxed whitespace-pre-wrap select-text">
          ${{escapeHtml(text)}}
        </div>
      `;
      wMessages.appendChild(div);
      wMessages.scrollTop = wMessages.scrollHeight;
    }}

    function initWConversation() {{
      wMessages.innerHTML = '';
      appendWCurator(`
        <p class="text-[#ececec]">
          How can I help you explore museums and art spaces today?
        </p>
      `);
    }}

    function handleWQuery(q) {{
      const query = q.toLowerCase();
      setTimeout(() => {{
        // Visitor Queries: Hours & Mondays
        if (query.includes('hour') || query.includes('schedule') || query.includes('open') || query.includes('monday') || query.includes('weekend')) {{
          const targetInst = DATA.find(i => query.includes(i.name.toLowerCase()));
          if (targetInst) {{
            appendWCurator(`
              <p class="text-slate-200">
                <strong>${{formatWInstLink(targetInst)}}</strong> is open <strong>${{targetInst.opening_hours}}</strong>.
              </p>
              <p class="text-slate-300">
                Address: ${{targetInst.address}}. Transit: ${{targetInst.transit_tips}}.
              </p>
            `);
            select(targetInst, true);
            return;
          }}

          const mSpaces = DATA.filter(i => !i.opening_hours.toLowerCase().includes('closed mon') && (i.opening_hours.toLowerCase().includes('daily') || i.opening_hours.toLowerCase().includes('mon,') || i.opening_hours.toLowerCase().includes('mon–') || i.opening_hours.toLowerCase().includes('mon-')));
          const m1 = mSpaces[0] || DATA[0];
          const m2 = mSpaces[1] || DATA[1];
          appendWCurator(`
            <p class="text-slate-200">
              Most museums are closed on Mondays, but Culture Atlas has <strong>${{mSpaces.length}}</strong> spaces open on Mondays:
            </p>
            <p class="text-slate-300">
              Check out ${{formatWInstLink(m1)}} or ${{formatWInstLink(m2)}}.
            </p>
          `);
          return;
        }}

        // Visitor Queries: Transit & Directions
        if (query.includes('transit') || query.includes('how to get') || query.includes('train') || query.includes('subway') || query.includes('direction')) {{
          const targetInst = DATA.find(i => query.includes(i.name.toLowerCase()));
          if (targetInst) {{
            appendWCurator(`
              <p class="text-slate-200">
                To reach <strong>${{formatWInstLink(targetInst)}}</strong>, take ${{targetInst.transit_tips}}.
              </p>
              <p class="text-slate-300">
                Address: ${{targetInst.address}} (${{targetInst.neighborhood}}). Suggested duration: ${{targetInst.visit_duration}}.
              </p>
            `);
            select(targetInst, true);
            return;
          }}

          const dia = DATA.find(i => i.name.includes('Dia Beacon'));
          const louis = DATA.find(i => i.name.includes('Louisiana'));
          appendWCurator(`
            <p class="text-slate-200">
              Every museum in Culture Atlas includes simple transit directions:
            </p>
            <p class="text-slate-300">
              Take the Metro-North train from Grand Central right to ${{formatWInstLink(dia)}}, or take the coastal train from Copenhagen to ${{formatWInstLink(louis)}}.
            </p>
          `);
          return;
        }}

        // Visitor Queries: Accessibility
        if (query.includes('accessib') || query.includes('wheelchair') || query.includes('step-free')) {{
          const serp = DATA.find(i => i.name.includes('Serpentine'));
          const aros = DATA.find(i => i.name.includes('ARoS'));
          appendWCurator(`
            <p class="text-slate-200">
              All mapped spaces have step-free access, elevators, wheelchairs to borrow, and free admission for companions.
            </p>
            <p class="text-slate-300">
              Great accessible venues include ${{formatWInstLink(serp)}} in London and ${{formatWInstLink(aros)}} in Denmark.
            </p>
          `);
          return;
        }}

        // Free admission
        if (query.includes('free') || query.includes('admission') || query.includes('ticket')) {{
          const freeSpaces = DATA.filter(i => (i.admission_policy || '').includes('Free'));
          const f1 = freeSpaces[0] || DATA[0];
          const f2 = freeSpaces[1] || DATA[1];
          appendWCurator(`
            <p class="text-slate-200">
              We map <strong>${{freeSpaces.length}}</strong> spaces with completely free admission.
            </p>
            <p class="text-slate-300">
              Top free places include ${{formatWInstLink(f1)}} and ${{formatWInstLink(f2)}}.
            </p>
          `);
          return;
        }}

        // Research: How Culture Atlas Audits Museums
        if (query.includes('research') || query.includes('how do you audit') || query.includes('form 990')) {{
          appendWCurator(`
            <p class="text-slate-200">
              We audit museums through official filings:
            </p>
            <p class="text-slate-300">
              1. <strong>Tax filings:</strong> US IRS Form 990, UK Charity Commission, French DRAC.<br>
              2. <strong>Board conflicts:</strong> Tracking trustees with ties to weapons, oil, or private prisons.<br>
              3. <strong>Watchdog evidence:</strong> Direct activist campaigns and investigative reporting.
            </p>
          `);
          return;
        }}

        // Research: Landmark Shows
        if (query.includes('landmark') || query.includes('szeemann') || query.includes('when attitudes') || query.includes('documenta')) {{
          appendWCurator(`
            <p class="text-slate-200">
              Milestone exhibitions in curatorial critique:
            </p>
            <p class="text-slate-300">
              - <em>When Attitudes Become Form</em> (1969, Szeemann): The exhibition itself as concept.<br>
              - <em>This Is Tomorrow</em> (1956, Whitechapel): Collaborative pop art environment.<br>
              - <em>Documenta 11</em> (2002, Enwezor): Decentering Western art history.<br>
              - <em>Mining the Museum</em> (1992, Fred Wilson): Exposing racial bias in collections.
            </p>
          `);
          return;
        }}

        // Research: Restitution
        if (query.includes('restitut') || query.includes('repatriat') || query.includes('benin') || query.includes('looted')) {{
          appendWCurator(`
            <p class="text-slate-200">
              Restitution of looted colonial heritage:
            </p>
            <p class="text-slate-300">
              Pioneering museums are returning stolen artifacts, like the Benin Bronzes transferred back to Nigeria by the Horniman Museum and German state museums.
            </p>
          `);
          return;
        }}

        // Research: MIT Press Canon
        if (query.includes('mit press') || query.includes('mit book') || query.includes('mit oress') || query.includes('theory book') || query.includes('reading list')) {{
          appendWCurator(`
            <p class="text-slate-200">
              Essential MIT Press books on museums and art theory:
            </p>
            <p class="text-slate-300">
              - <em>One Place after Another</em> (Miwon Kwon, 2002): How site-specific art changed.<br>
              - <em>Beyond Objecthood</em> (James Voorhies, 2017): The exhibition as an artwork.<br>
              - <em>Institutional Critique</em> (Alberro & Stimson, 2009): Artists questioning museum power.<br>
              - <em>The Cultural Logic of the Late Capitalist Museum</em> (Rosalind Krauss, 1990): Museums as spectacle machines.<br>
              - <em>Art Power</em> (Boris Groys, 2008): Why public museums protect art from the market.
            </p>
          `);
          return;
        }}

        // Research: Rosalind Krauss
        if (query.includes('krauss') || query.includes('late capitalist museum')) {{
          appendWCurator(`
            <p class="text-slate-200">
              Rosalind Krauss on the late capitalist museum (1990):
            </p>
            <p class="text-slate-300">
              She showed how modern mega-museums stopped being quiet libraries for studying individual paintings, turning into dramatic spectacle centers designed like luxury malls to sell bodily thrills and souvenirs.
            </p>
          `);
          return;
        }}

        // Research: Miwon Kwon
        if (query.includes('miwon kwon') || query.includes('kwon') || query.includes('site-specific') || query.includes('site specific') || query.includes('one place')) {{
          appendWCurator(`
            <p class="text-slate-200">
              Miwon Kwon on site-specific art (MIT Press, 2002):
            </p>
            <p class="text-slate-300">
              She tracks site-specificity in 3 stages: 1) physical ground (Serra), 2) museum critique (Haacke), and 3) traveling artists hired by biennials like temporary consultants to create projects about local communities.
            </p>
          `);
          return;
        }}

        if (query.includes('what makes') || query.includes('ethical') || query.includes('criteria') || query.includes('method')) {{
          const chis = DATA.find(i => i.name.includes('Chisenhale'));
          const capc = DATA.find(i => i.name.includes('CAPC'));
          appendWCurator(`
            <p class="text-slate-200">
              We rate museums based on clean funding:
            </p>
            <p class="text-slate-300">
              We prioritize public museums backed by arts councils like ${{formatWInstLink(capc)}}, artist-run spaces like ${{formatWInstLink(chis)}}, and spaces that don't take oil or weapons money.
            </p>
          `);
          return;
        }}

        if (query.includes('fossil') || query.includes('oil') || query.includes('bp') || query.includes('defense')) {{
          const cam = DATA.find(i => i.name.includes('Camden'));
          const white = DATA.find(i => i.name.includes('Whitechapel'));
          appendWCurator(`
            <p class="text-slate-200">
              Every museum in Culture Atlas has verified clean funding without oil or weapons sponsorships.
            </p>
            <p class="text-slate-300">
              Examples include ${{formatWInstLink(cam)}} and ${{formatWInstLink(white)}}.
            </p>
          `);
          return;
        }}

        if (query.includes('moma') || query.includes('whitney') || query.includes('why exclude')) {{
          const dia = DATA.find(i => i.name.includes('Dia Beacon'));
          const sculp = DATA.find(i => i.name.includes('SculptureCenter'));
          appendWCurator(`
            <p class="text-slate-200">
              MoMA trustees had ties to weapons companies and private prisons. Culture Atlas only maps spaces free from controversial sponsorships.
            </p>
            <p class="text-slate-300">
              Instead, we feature spaces like ${{formatWInstLink(dia)}} and ${{formatWInstLink(sculp)}}.
            </p>
          `);
          return;
        }}

        // City or general matches
        const matchCity = PRIORITY_CITIES.find(c => query.includes(c.name.toLowerCase())) || DATA.find(i => query.includes(i.city.toLowerCase()));
        if (matchCity) {{
          const cityName = matchCity.name || matchCity.city;
          const cObj = PRIORITY_CITIES.find(c => c.name.toLowerCase() === cityName.toLowerCase()) || matchCity;
          const list = DATA.filter(i => i.city.toLowerCase() === cityName.toLowerCase());
          const topSp = list.slice(0, 3).map(i => formatWInstLink(i, {{noCity: true}})).join(', ');
          appendWCurator(`
            <p class="text-slate-200">
              Found <strong>${{list.length}}</strong> spaces in <a href="#" class="w-city-link font-semibold text-white hover:text-[#60a5fa] underline cursor-pointer" data-city="${{escapeHtml(cityName)}}">${{escapeHtml(cityName)}}</a> with clean funding:
            </p>
            <p class="text-slate-300">
              Highlights include ${{topSp}}.
            </p>
          `);
          targetRadius = baseRadius * 3.8;
          flyTo(cObj.lon, cObj.lat);
          return;
        }}

        const rand = DATA.filter(i => i.tier === 'A');
        const p1 = rand[Math.floor(Math.random()*rand.length)];
        const p2 = rand[Math.floor(Math.random()*rand.length)];
        appendWCurator(`
          <p class="text-slate-200">
            Here are two great art spaces to check out: ${{formatWInstLink(p1)}} and ${{formatWInstLink(p2)}}.
          </p>
        `);
      }}, 250);
    }}

    function onSend() {{
      const text = wInput.value.trim();
      if (!text) return;
      wInput.value = '';
      appendWUser(text);
      handleWQuery(text);
    }}

    wSend.addEventListener('click', onSend);
    wInput.addEventListener('keydown', e => {{
      if (e.key === 'Enter') onSend();
    }});

        document.getElementById('wOpenMomaBtn')?.addEventListener('click', (e) => {{
      e.stopPropagation();
      if (!wSheetOpen) setWSheet(true);
      flyTo(-73.9776, 40.7614);
      appendWUser('Why is MoMA excluded from Culture Atlas?');
      handleWQuery('Why is MoMA excluded from Culture Atlas?');
    }});

    let wCategoryFilter = 'all';

    function updateWFilterChipsUI() {{
      document.querySelectorAll('.w-inquiry').forEach(b => {{
        const f = b.getAttribute('data-filter');
        if (f && f === wCategoryFilter && wCategoryFilter !== 'all') {{
          b.classList.add('border-[#38bdf8]', 'ring-1', 'ring-[#38bdf8]', 'bg-[#0c1a2e]', 'text-white', 'shadow-[0_0_10px_rgba(56,189,248,0.5)]');
          b.classList.remove('border-[#1b3324]', 'border-[#232a3c]', 'border-[#3b2b11]', 'bg-[#0c1f15]', 'bg-[#101522]', 'bg-[#221807]', 'text-[#6ee7b7]', 'text-[#93c5fd]', 'text-[#cbd5e1]', 'text-[#fcd34d]');
        }} else {{
          b.classList.remove('border-[#38bdf8]', 'ring-1', 'ring-[#38bdf8]', 'bg-[#0c1a2e]', 'text-white', 'shadow-[0_0_10px_rgba(56,189,248,0.5)]');
          const col = b.getAttribute('data-chip-color');
          if (col === 'green') {{
            b.classList.add('border-[#1b3324]', 'bg-[#0c1f15]', 'text-[#6ee7b7]');
          }} else if (col === 'amber') {{
            b.classList.add('border-[#3b2b11]', 'bg-[#221807]', 'text-[#fcd34d]');
          }} else if (col === 'blue') {{
            b.classList.add('border-[#232a3c]', 'bg-[#101522]', 'text-[#93c5fd]');
          }} else {{
            b.classList.add('border-[#232a3c]', 'bg-[#101522]', 'text-[#cbd5e1]');
          }}
        }}
      }});
    }}

    document.querySelectorAll('.w-inquiry').forEach(b => {{
      b.addEventListener('click', () => {{
        const f = b.getAttribute('data-filter') || 'all';
        const q = b.getAttribute('data-query');

        if (wCategoryFilter === f) {{
          wCategoryFilter = 'all';
          targetRadius = baseRadius;
        }} else {{
          wCategoryFilter = f;
          if (f === 'london') {{
            flyTo(-0.1278, 51.5074);
            targetRadius = baseRadius * 4.0;
          }} else if (f === 'nyc') {{
            flyTo(-73.9776, 40.7614);
            targetRadius = baseRadius * 4.0;
          }}
        }}

        updateWFilterChipsUI();

        if (q && wCategoryFilter !== 'all') {{
          appendWUser(q);
          handleWQuery(q);
        }}
      }});
    }});

    // Globe Controls & Curator interaction
    document.getElementById('wResetBtn')?.addEventListener('click', () => {{
      flyTo(-45, 35);
      isAutoSpinning = true;
      filterCountry = 'all';
      filterCity = 'all';
      document.getElementById('wMobileFilterBanner')?.classList.add('hidden');
    }});

    document.getElementById('wSpinBtn')?.addEventListener('click', () => {{
      isAutoSpinning = !isAutoSpinning;
      const b = document.getElementById('wSpinBtn');
      if (b) b.textContent = isAutoSpinning ? '⏸ Pause' : '⟳ Spin';
    }});

    // Half Sheet Open / Close Controller
    let wSheetOpen = true;
    document.getElementById('wMinimizeBtn')?.addEventListener('click', (e) => {{
      e.stopPropagation();
      setWSheet(false);
    }});
    document.getElementById('wExpandBtn')?.addEventListener('click', (e) => {{
      e.stopPropagation();
      setWSheet(true);
    }});

    function setWSheet(open) {{
      wSheetOpen = open;
      const globe = document.getElementById('wGlobePanel');
      const curator = document.getElementById('wCuratorPanel');
      const feed = document.getElementById('wCuratorMessages');
      const chips = document.getElementById('wInquiryCarousel');
      const input = document.getElementById('wInputBar');
      const toggleBtn = document.getElementById('wSheetToggleBtn');
      const badge = document.getElementById('wSheetBadge');

      if (open) {{
        globe.style.height = '195px';
        curator.classList.add('flex-1');
        curator.style.height = '';
        if (feed) feed.style.display = 'block';
        if (chips) chips.style.display = 'flex';
        if (input) input.style.display = 'flex';
        if (toggleBtn) toggleBtn.innerHTML = '<span>▼</span><span>Close</span>';
        if (badge) badge.textContent = 'Half Sheet';
      }} else {{
        globe.style.height = '420px';
        curator.classList.remove('flex-1');
        curator.style.height = '34px';
        if (feed) feed.style.display = 'none';
        if (chips) chips.style.display = 'none';
        if (input) input.style.display = 'none';
        if (toggleBtn) toggleBtn.innerHTML = '<span>▲</span><span>Open Half Sheet</span>';
        if (badge) badge.textContent = 'Tap to Open';
      }}
      setTimeout(resize, 40);
      setTimeout(resize, 180);
      setTimeout(resize, 320);
    }}

    document.getElementById('wSheetToggleBtn')?.addEventListener('click', (e) => {{
      e.stopPropagation();
      setWSheet(!wSheetOpen);
    }});

    document.getElementById('wSheetHeader')?.addEventListener('click', () => {{
      if (!wSheetOpen) setWSheet(true);
    }});

    document.getElementById('wCardCuratorBtn')?.addEventListener('click', () => {{
      if (selectedInst) {{
        if (!wSheetOpen) setWSheet(true);
        appendWUser(`Tell me about ${{selectedInst.name}}`);
        handleWQuery(selectedInst.name);
      }}
    }});

    // Pointer on Canvas
    canvas.addEventListener('pointerdown', e => {{
      isDragging = true;
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

    canvas.addEventListener('pointerup', e => {{
      isDragging = false;
      const dt = Date.now() - pointerDownTime;
      const dist = Math.hypot(e.clientX - pointerStartX, e.clientY - pointerStartY);
      if (dt < 300 && dist < 6) {{
        const rect = canvas.getBoundingClientRect();
        const mx = e.clientX - rect.left;
        const my = e.clientY - rect.top;

        for (let i = 0; i < cityBadgeHitboxes.length; i++) {{
          const b = cityBadgeHitboxes[i];
          if (mx >= b.x && mx <= b.x + b.w && my >= b.y && my <= b.y + b.h) {{
            filterCity = b.name;
            targetRadius = baseRadius * 3.8;
            flyTo(b.lon, b.lat);
            if (!wSheetOpen) setWSheet(true);
            const cityList = DATA.filter(inst => inst.city.toLowerCase() === b.name.toLowerCase());
            const topList = cityList.slice(0, 3).map(i => formatWInstLink(i, {{noCity: true}})).join(', ');
            appendWCurator(`
              <p class="text-slate-200">
                Now exploring <a href="#" class="w-city-link font-semibold text-white hover:text-[#60a5fa] underline cursor-pointer" data-city="${{escapeHtml(b.name)}}">${{escapeHtml(b.name)}}</a>, with <strong>${{cityList.length}}</strong> spaces with clean funding: ${{topList}}.
              </p>
            `);
            return;
          }}
        }}

        for (let i = 0; i < visibleDots.length; i++) {{
          const d = visibleDots[i];
          if (Math.hypot(d.x - mx, d.y - my) < 9) {{
            select(d.inst);
            return;
          }}
        }}

        if (selectedInst) {{
          deselect();
        }}
      }}
    }});

    document.getElementById('wCardCloseBtn')?.addEventListener('click', (e) => {{
      e.stopPropagation();
      deselect();
    }});

    initWConversation();
    if (selectedInst) select(selectedInst, false);
  </script>
</body>
</html>
"""

    widget_dest = "/Users/polinavasilyeva/.gemini/antigravity/brain/b997e616-4551-453e-83cc-4ba184f90abf/concierge_widget.html"
    with open(widget_dest, "w", encoding="utf-8") as f:
        f.write(widget_html)
    print("Wrote updated conversational concierge_widget.html!")

if __name__ == "__main__":
    update_widget()
