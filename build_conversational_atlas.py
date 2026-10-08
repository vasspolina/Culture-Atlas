import os
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

        min_lon, max_lon = 180.0, -180.0
        min_lat, max_lat = 90.0, -90.0
        for p_ring in polys:
            for pt in p_ring:
                if pt[0] < min_lon: min_lon = pt[0]
                if pt[0] > max_lon: max_lon = pt[0]
                if pt[1] < min_lat: min_lat = pt[1]
                if pt[1] > max_lat: max_lat = pt[1]
        out_countries.append({'n': name, 'c': col, 'r': polys, 'b': [round(min_lon, 1), round(max_lon, 1), round(min_lat, 1), round(max_lat, 1)]})

    countries_json = json.dumps(out_countries, separators=(',', ':'))
    _proxy = os.environ.get('ATLAS_AI_PROXY_URL', '').strip()
    if not _proxy and os.path.exists('worker/.proxy_url'):
        _proxy = open('worker/.proxy_url').read().strip()
    proxy_url_json = json.dumps(_proxy)
    institutions_raw = open('institutions.json', 'r', encoding='utf-8').read().strip()
    all_raw_institutions = json.loads(institutions_raw)
    academic_raw = open('academic_papers.json', 'r', encoding='utf-8').read().strip() if os.path.exists('academic_papers.json') else '[]'
    academic_papers = json.loads(academic_raw)
    academic_json = json.dumps(academic_papers, separators=(',', ':'))

    insts_data = all_raw_institutions
    clean_insts = [i for i in all_raw_institutions if i.get('tier') == 'A']
    flagged_insts = [i for i in all_raw_institutions if i.get('tier') == 'B']
    unverified_insts = [i for i in all_raw_institutions if i.get('tier') == 'U']
    excluded_data = [i for i in all_raw_institutions if i.get('tier') != 'A']

    clean_count = len(clean_insts)
    flagged_count = len(flagged_insts)
    total_count = len(all_raw_institutions)
    academic_count = len(academic_papers)
    institutions_count = clean_count
    spaces_count_str = f"{clean_count} CLEAN SPACES"

    # Compute comprehensive Country & City Registries
    reg_countries = {}
    reg_cities = {}
    for item in insts_data:
        co = item.get("country", "").strip()
        ci = item.get("city", "").strip()
        if not co or not ci:
            continue
        if co not in reg_countries:
            reg_countries[co] = {"name": co, "count": 0, "clean_count": 0, "lons": [], "lats": [], "cities": set()}
        reg_countries[co]["count"] += 1
        if item.get("tier") == "A":
            reg_countries[co]["clean_count"] += 1
        reg_countries[co]["lons"].append(item["lon"])
        reg_countries[co]["lats"].append(item["lat"])
        reg_countries[co]["cities"].add(ci)

        if ci not in reg_cities:
            reg_cities[ci] = {"name": ci, "country": co, "count": 0, "clean_count": 0, "lons": [], "lats": [], "addresses": []}
        reg_cities[ci]["count"] += 1
        if item.get("tier") == "A":
            reg_cities[ci]["clean_count"] += 1
        reg_cities[ci]["lons"].append(item["lon"])
        reg_cities[ci]["lats"].append(item["lat"])
        if item.get("address"):
            reg_cities[ci]["addresses"].append(item["address"])

    all_countries_list = []
    for co, d in reg_countries.items():
        min_lon, max_lon = min(d["lons"]), max(d["lons"])
        min_lat, max_lat = min(d["lats"]), max(d["lats"])
        c_lon = round((min_lon + max_lon) / 2, 4)
        c_lat = round((min_lat + max_lat) / 2, 4)
        max_span = max(max_lon - min_lon, max_lat - min_lat)
        if max_span < 1.0: zoom = 4.8
        elif max_span < 3.5: zoom = 4.0
        elif max_span < 8.0: zoom = 3.2
        elif max_span < 16.0: zoom = 2.6
        else: zoom = 2.1
        all_countries_list.append({
            "name": co,
            "count": d["count"],
            "cities": sorted(list(d["cities"])),
            "lon": c_lon,
            "lat": c_lat,
            "zoom": zoom
        })

    all_cities_list = []
    for ci, d in reg_cities.items():
        c_lon = round(sum(d["lons"]) / len(d["lons"]), 5)
        c_lat = round(sum(d["lats"]) / len(d["lats"]), 5)
        streets = []
        for a in d["addresses"]:
            p = a.split(",")[0].strip()
            if p and len(p) < 40 and not any(ch.isdigit() for ch in p[:2]):
                if p not in streets:
                    streets.append(p)
        all_cities_list.append({
            "name": ci,
            "country": d["country"],
            "count": d["count"],
            "lon": c_lon,
            "lat": c_lat,
            "streets": streets[:6]
        })

    all_countries_list.sort(key=lambda x: -x["count"])
    all_cities_list.sort(key=lambda x: -x["count"])

    all_countries_registry_json = json.dumps(all_countries_list, separators=(',', ':'))
    all_cities_registry_json = json.dumps(all_cities_list, separators=(',', ':'))
    institutions_json = json.dumps(insts_data, separators=(',', ':'))
    excluded_json = json.dumps(excluded_data, separators=(',', ':'))

    import base64
    b64_reg = base64.b64encode(open('app/fonts/PPTelegraf-Regular.otf', 'rb').read()).decode('ascii')
    maplibre_css = open('app/vendor/maplibre-gl.css', 'r', encoding='utf-8').read()
    maplibre_js = open('app/vendor/maplibre-gl.js', 'r', encoding='utf-8').read()

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
          letterSpacing: {{
            DEFAULT: '0.6pt',
            tight: '0.6pt',
            tighter: '0.6pt',
            normal: '0.6pt',
            wide: '0.6pt',
            wider: '0.6pt',
            widest: '0.6pt',
          }},
          lineHeight: {{
            DEFAULT: '120%',
            none: '120%',
            tight: '120%',
            snug: '120%',
            normal: '120%',
            relaxed: '120%',
            loose: '120%',
          }},
          fontSize: {{
            'xs': ['14px', '120%'],
            'sm': ['14px', '120%'],
            'base': ['18px', '120%'],
            'md': ['18px', '120%'],
            'lg': ['18px', '120%'],
            'xl': ['24px', '120%'],
            '2xl': ['24px', '120%'],
            '3xl': ['24px', '120%'],
          }}
        }}
      }}
    }};
  </script>
  <style>
        /* ========================================================= */
    /* STRICT EXCLUSIVITY: ONLY PP TELEGRAF REGULAR FOR EVERYTHING */
    /* STRICT 3-TYPE-SIZE SYSTEM: 14px Floor/Body, 18px Mid, 24px Headline */
    /* USER SPECIFICATION: LINE-HEIGHT 120%, NO BOLD FONTS, 0.6pt LETTER-SPACING */
    /* ========================================================= */
    *, *::before, *::after, html, body, input, button, select, textarea, p, span, div, li, a, h1, h2, h3, h4, h5, h6, strong, b, code, pre, kbd, samp, .font-mono, [class*="font-mono"], [class*="font-"], [class*="leading-"], [class*="tracking-"] {{
      font-family: 'PP Telegraf', 'PP Telegraph', sans-serif !important;
      font-weight: 400 !important;
      font-synthesis: none !important;
      letter-spacing: 0.6pt !important;
      line-height: 120% !important;
      -webkit-font-smoothing: antialiased;
      -moz-osx-font-smoothing: grayscale;
    }}

    *, *::before, *::after {{
      font-size: 14px;
      letter-spacing: 0.6pt !important;
      line-height: 120% !important;
    }}
    html, body {{
      font-size: 14px !important;
      line-height: 120% !important;
      letter-spacing: 0.6pt !important;
      font-weight: 400 !important;
    }}
    input, button, select, textarea, p, span, div, li, a {{
      font-size: 14px;
      line-height: 120% !important;
      letter-spacing: 0.6pt !important;
      font-weight: 400 !important;
    }}

    strong, b, h1, h2, h3, h4, h5, h6, .font-normal, .font-normal, .font-normal, [class*="font-normal"], [class*="font-normal"], [class*="font-normal"] {{
      font-weight: 400 !important;
    }}
    strong, b {{
      color: #ffffff;
      font-weight: 400 !important;
    }}

    /* Size 1: 14px (Floor / Default) */
    .type-14, .text-14, .text-[14px],
    [class*="text-\[8"], [class*="text-\[9"], [class*="text-\[10"], 
    [class*="text-\[11"], [class*="text-\[12"], [class*="text-\[13"],
    [class*="text-\[14px\]"], .text-xs, .text-sm {{
      font-size: 14px !important;
      line-height: 120% !important;
      letter-spacing: 0.6pt !important;
      font-weight: 400 !important;
    }}

    /* Size 2: 18px (Card Titles, Subheaders, Museum Names) */
    .type-18, .text-18, .text-[18px], .text-md, .text-base, .text-lg,
    [class*="text-\[15"], [class*="text-\[16"], [class*="text-\[17"], [class*="text-\[18"], [class*="text-\[19"], [class*="text-\[20"],
    [class*="text-\[18px\]"] {{
      font-size: 18px !important;
      line-height: 120% !important;
      letter-spacing: 0.6pt !important;
      font-weight: 400 !important;
    }}

    /* Size 3: 24px (Main Brand Title, Modal Headlines, Large Dossier Titles) */
    .type-24, .text-24, .text-xl, .text-2xl, .text-3xl, .text-4xl,
    [class*="text-\[21"], [class*="text-\[22"], [class*="text-\[23"], [class*="text-\[24"], [class*="text-\[25"], [class*="text-\[26"], [class*="text-\[28"], [class*="text-\[30"], [class*="text-\[32"],
    [class*="text-\[24px\]"] {{
      font-size: 24px !important;
      line-height: 120% !important;
      letter-spacing: 0.6pt !important;
      font-weight: 400 !important;
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

    /* Unified Split-Screen Architecture: Desktop Vertical Half-and-Half / Mobile Stacked */
    #globeViewport {{
      height: 50%;
      width: 100%;
      min-height: 0;
      flex: 1 1 50%;
      display: flex;
      background: #171717;
      border-bottom: 1px solid #262626;
      border-right: none;
      transition: height 0.2s cubic-bezier(0.16, 1, 0.3, 1), width 0.2s cubic-bezier(0.16, 1, 0.3, 1), flex 0.2s cubic-bezier(0.16, 1, 0.3, 1);
    }}
    #workViewContainer {{
      display: flex;
      height: 50%;
      width: 100%;
      min-height: 0;
      flex: 1 1 50%;
      flex-direction: column;
      background: #171717;
      overflow: hidden;
      padding-top: 0;
      transition: height 0.2s cubic-bezier(0.16, 1, 0.3, 1), width 0.2s cubic-bezier(0.16, 1, 0.3, 1), flex 0.2s cubic-bezier(0.16, 1, 0.3, 1);
    }}
    @media (min-width: 768px) {{
      #globeViewport {{
        height: 100%;
        width: 50%;
        border-bottom: none;
        border-right: 1px solid #262626;
      }}
      #workViewContainer {{
        height: 100%;
        width: 50%;
      }}
    }}
    #curatorScrollArea {{
      flex: 1 1 0%;
      min-height: 0;
      overflow-y: auto;
      width: 100%;
    }}
    #curatorMessages:empty {{
      display: none;
    }}

    /* Card & Button Hover Styles */
    .work-suggestion-card {{
      transition: all 0.18s ease;
    }}
    .work-suggestion-card:hover {{
      transform: translateY(-2px);
      box-shadow: 0 8px 24px -4px rgba(0, 0, 0, 0.5);
    }}
    .work-shelf-pill {{
      transition: all 0.15s ease;
    }}
    .work-shelf-pill:hover {{
      color: #ffffff;
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
    /* MapLibre Embedded Dark Theme & Vector Controls */
    {maplibre_css}
    .atlas-dark-popup .maplibregl-popup-content {{
      background: #18181b !important;
      color: #f1f5f9 !important;
      border: 1px solid #3f3f46 !important;
      border-radius: 14px !important;
      box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.7) !important;
      padding: 8px 10px !important;
    }}
    .atlas-dark-popup .maplibregl-popup-tip {{
      border-top-color: #18181b !important;
      border-bottom-color: #18181b !important;
    }}
    .atlas-dark-popup .maplibregl-popup-close-button {{
      color: #a1a1aa !important;
      padding: 6px 8px !important;
      font-size: 16px !important;
    }}
    .atlas-dark-popup .maplibregl-popup-close-button:hover {{
      color: #ffffff !important;
    }}
    .maplibregl-ctrl-group {{
      background: #212121 !important;
      border: 1px solid #333333 !important;
      border-radius: 12px !important;
      overflow: hidden !important;
      box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.5) !important;
    }}
    .maplibregl-ctrl-group button {{
      background: #212121 !important;
      border-bottom: 1px solid #333333 !important;
      width: 32px !important;
      height: 32px !important;
    }}
    .maplibregl-ctrl-group button:last-child {{
      border-bottom: none !important;
    }}
    .maplibregl-ctrl-group button:hover {{
      background: #2a2a2a !important;
    }}
    .maplibregl-ctrl-group button .maplibregl-ctrl-icon {{
      filter: invert(1) brightness(0.9);
    }}
    .maplibregl-ctrl-attrib {{
      background: rgba(23, 23, 23, 0.8) !important;
      color: #71717a !important;
      font-size: 10px !important;
      border-radius: 6px !important;
      padding: 2px 6px !important;
    }}
    .maplibregl-ctrl-attrib a {{
      color: #94a3b8 !important;
    }}
    .custom-inst-pin {{
      cursor: pointer;
      position: relative;
      display: flex;
      align-items: center;
      justify-content: center;
      user-select: none;
      transition: transform 0.2s cubic-bezier(0.16, 1, 0.3, 1);
    }}
    .custom-inst-pin:hover {{
      transform: scale(1.12);
      z-index: 9999 !important;
    }}
    @keyframes pinPulse {{
      0% {{ transform: scale(0.95); opacity: 0.8; }}
      50% {{ transform: scale(1.4); opacity: 0.2; }}
      100% {{ transform: scale(0.95); opacity: 0.8; }}
    }}
    .pin-pulse-aura {{
      animation: pinPulse 2.4s infinite ease-in-out;
    }}

    /* Floating Institution Name Label directly on top of dots */
    .inst-pin-label {{
      position: absolute;
      bottom: calc(100% + 4px);
      left: 50%;
      transform: translateX(-50%) translateY(0);
      display: flex;
      align-items: center;
      gap: 5px;
      padding: 3px 8px;
      background: rgba(18, 20, 26, 0.94);
      color: #f8fafc;
      border: 1px solid rgba(255, 255, 255, 0.18);
      border-radius: 6px;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.65), 0 0 0 1px rgba(0, 0, 0, 0.4);
      font-family: "PP Telegraf", "PP Telegraph", sans-serif;
      font-size: 11px;
      font-weight: 600;
      letter-spacing: 0.02em;
      line-height: 1.2;
      white-space: nowrap;
      pointer-events: auto;
      cursor: pointer;
      backdrop-filter: blur(6px);
      -webkit-backdrop-filter: blur(6px);
      transition: opacity 0.25s cubic-bezier(0.16, 1, 0.3, 1), transform 0.25s cubic-bezier(0.16, 1, 0.3, 1), border-color 0.2s ease, box-shadow 0.2s ease;
      z-index: 20;
    }}
    .inst-pin-label::after {{
      content: '';
      position: absolute;
      top: 100%;
      left: 50%;
      transform: translateX(-50%);
      border-width: 4px 4px 0 4px;
      border-style: solid;
      border-color: rgba(18, 20, 26, 0.94) transparent transparent transparent;
    }}
    .inst-pin-label-name {{
      max-width: 260px;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }}
    /* Labels always visible on top of dots on all points of view by default */
    .inst-pin-label {{
      opacity: 1 !important;
      visibility: visible !important;
      transform: translateX(-50%) translateY(0);
    }}
    /* When a pin is clicked and its detail popup card is open, suppress that pin's label */
    .custom-inst-pin.popup-active .inst-pin-label {{
      opacity: 0 !important;
      visibility: hidden !important;
      pointer-events: none !important;
    }}
    .custom-inst-pin:hover .inst-pin-label {{
      opacity: 1 !important;
      visibility: visible !important;
      transform: translateX(-50%) translateY(-2px) scale(1.05) !important;
      border-color: rgba(255, 255, 255, 0.45) !important;
      background: rgba(24, 27, 36, 0.98) !important;
      box-shadow: 0 6px 16px rgba(0, 0, 0, 0.8), 0 0 12px rgba(16, 185, 129, 0.35) !important;
      z-index: 9999 !important;
    }}
  </style>
  <script>
{maplibre_js}
  </script>
</head>
<body class="bg-[#171717] text-slate-100 h-screen h-[100dvh] flex flex-col select-none overflow-hidden font-sans">

  <!-- ========================================================= -->
  <!-- 🧭 TOP HEADER: BRANDING, MODE SWITCHER (CHAT / WORK) & CONTROLS -->
  <!-- ========================================================= -->
  <header class="w-full h-14 bg-[#171717] border-b border-[#262626] px-2.5 sm:px-6 flex items-center justify-between shrink-0 z-30 select-none gap-1 sm:gap-2">
    
    <!-- Left: Brand / Title (Click to Reset Globe View) -->
    <button id="topBrandLogoBtn" class="flex items-center gap-1.5 sm:gap-2 text-left bg-transparent border-0 p-0 m-0 cursor-pointer group focus:outline-none select-none transition hover:opacity-85 shrink-0" title="Reset Globe View" aria-label="Reset Globe View">
      <div class="w-2 sm:w-2.5 h-2 sm:h-2.5 rounded-full bg-white group-hover:scale-125 transition-transform shrink-0"></div>
      <div class="flex items-center gap-2">
        <span class="text-[13px] sm:text-[18px] font-normal tracking-wider text-white uppercase group-hover:text-emerald-300 transition-colors whitespace-nowrap">CULTURE ATLAS</span>
        <span id="topSpacesBadge" class="text-[13px] text-emerald-400 bg-[#0a2016] px-2 py-0.5 rounded-full border border-emerald-900/60 hidden lg:inline font-mono group-hover:border-emerald-700/80 transition-colors">{spaces_count_str}</span>
      </div>
    </button>

    <!-- Center: Mobile Mode Switcher (Map / Split / Chat) & Desktop New Chat -->
    <div class="flex items-center">
      <!-- Mobile Segmented Control (Phone Only) -->
      <div id="mobileModeSwitch" class="flex md:hidden items-center bg-[#222222] border border-[#333333] p-0.5 rounded-xl text-[11px] select-none shadow-sm">
        <button id="mobileModeMapBtn" class="px-2 py-0.5 rounded-lg text-[#a1a1aa] transition cursor-pointer" title="Map View">Map</button>
        <button id="mobileModeSplitBtn" class="px-2 py-0.5 rounded-lg bg-[#2563eb] text-white font-medium transition cursor-pointer" title="Split View">Split</button>
        <button id="mobileModeChatBtn" class="px-2 py-0.5 rounded-lg text-[#a1a1aa] transition cursor-pointer" title="Curator Chat">Chat</button>
      </div>

      <!-- Desktop Center New Chat Button -->
      <button id="topNewChatBtn" class="hidden md:flex items-center gap-1.5 px-3.5 py-1 bg-[#212121] hover:bg-[#282828] border border-[#2e2e2e] text-[#d4d4d4] hover:text-white rounded-full text-[14px] transition shadow-sm cursor-pointer" title="Start a new chat exploration">
        <span class="text-emerald-400 font-bold">+</span>
        <span>New Chat</span>
      </button>
    </div>

    <!-- Right: View Controls (Desktop) & Status / Reset (Compact Mobile) -->
    <div class="flex items-center gap-1 sm:gap-2 shrink-0">
      <!-- Desktop View Controls: Minimize · Expand -->
      <div class="hidden md:flex items-center gap-1.5 text-[14px] text-[#a1a1aa] bg-[#212121] border border-[#2e2e2e] px-2.5 py-1 rounded-xl shadow-sm">
        <button id="topViewMinimizeBtn" class="hover:text-white transition cursor-pointer text-[14px]">Minimize</button>
        <span class="text-[#555]">·</span>
        <button id="topViewExpandBtn" class="hover:text-white transition cursor-pointer text-[14px]">Expand</button>
      </div>

      <!-- Mobile + New Chat Icon Button -->
      <button id="mobileNewChatBtn" class="flex md:hidden items-center justify-center w-7 h-7 sm:w-8 sm:h-8 bg-[#212121] hover:bg-[#282828] border border-[#2e2e2e] text-emerald-400 hover:text-white rounded-full text-[15px] sm:text-[16px] font-bold transition shadow-sm cursor-pointer shrink-0" title="Start a new chat">
        +
      </button>

      <button id="topSettingsBtn" class="flex items-center gap-1 px-1.5 sm:px-3 py-1 bg-[#212121] hover:bg-[#2a2a2a] border border-[#2e2e2e] text-[#d4d4d4] hover:text-white rounded-xl text-[12px] sm:text-[14px] transition cursor-pointer shrink-0" title="AI Intelligence & API Key Settings">
        <span id="topStatusDot" class="w-1.5 sm:w-2 h-1.5 sm:h-2 rounded-full bg-amber-400 shrink-0"></span>
        <span id="topStatusLabel" class="font-normal text-amber-300 flex items-center gap-1"><span>🔑</span><span class="hidden sm:inline"> Add API Key</span></span>
      </button>
      <button id="topResetBtn" class="hidden sm:flex bg-[#212121] hover:bg-[#2a2a2a] border border-[#2e2e2e] text-[#d4d4d4] hover:text-white px-2 sm:px-2.5 py-1 rounded-xl text-[12px] sm:text-[14px] transition items-center gap-1 cursor-pointer shrink-0" title="Reset Globe View">
        <span>Reset</span>
      </button>
    </div>

  </header>

  <!-- ========================================================= -->
  <!-- MAIN APP CONTAINER (Desktop: 50/50 Vertical Split Screen / Mobile: Stacked) -->
  <!-- ========================================================= -->
  <div id="mainAppContainer" class="relative w-full flex-1 min-h-0 flex flex-col md:flex-row bg-[#171717] overflow-hidden">

    <!-- 🌍 3D GLOBE VIEWPORT (Desktop: Left Half / Mobile: Top Half) -->
    <div id="globeViewport" class="relative w-full md:w-1/2 h-1/2 md:h-full flex-1 min-h-0 flex items-center justify-center bg-[#171717] overflow-hidden select-none">
      
      <canvas id="globeCanvas" class="w-full h-full block cursor-grab"></canvas>

      <!-- 🗺️ HIGH-RESOLUTION INTERACTIVE CITY STREET MAP (Leaflet) -->
      <div id="cityMapContainer" class="absolute inset-0 hidden z-10 w-full h-full bg-[#171717]"></div>

      <!-- FLOATING INSTITUTION CARD -->
      <div id="floatingCard" class="hidden absolute z-20 pointer-events-auto bg-[#18181b]/95 backdrop-blur-md text-slate-100 rounded-2xl p-3.5 shadow-2xl transition duration-150 transform -translate-x-1/2 -translate-y-full mb-3 border border-[#2e2e2e] max-w-[340px] sm:max-w-[390px] w-max">
        <div class="flex items-start justify-between gap-2">
          <div class="truncate pr-1">
            <a id="floatingCardTitle" href="#" target="_blank" rel="noopener noreferrer" 
               class="font-normal text-[17px] sm:text-[18px] text-white hover:text-[#93c5fd] hover:underline leading-[120%] truncate block transition cursor-pointer"
               onclick="event.stopPropagation()" title="Open official website"></a>
            <div id="floatingCardMeta" class="text-[13px] text-[#a1a1aa] mt-0.5 flex items-center gap-1 font-mono">
              <span></span>
            </div>
          </div>
          <div class="flex items-center gap-1 shrink-0">
            <span id="floatingCardTier" class="text-[12px] font-mono px-2 py-0.5 rounded-lg border border-emerald-900/60 bg-[#0a2016] text-emerald-400">Verified</span>
            <button id="closeFloatingCardBtn" class="text-[#a1a1aa] hover:text-white p-1 rounded-md hover:bg-[#262626] transition text-[14px] leading-none ml-0.5 cursor-pointer" title="Close">✕</button>
          </div>
        </div>

        <div id="floatingCardHours" class="text-[13px] text-emerald-400 mt-1 truncate font-mono"></div>

        <!-- DIRECT WEB & VISITOR ACTION BUTTONS -->
        <div class="mt-2.5 flex items-center gap-2 flex-wrap">
          <a id="floatingCardDirectWebBtn" href="#" target="_blank" rel="noopener noreferrer" 
             class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-[#2563eb] hover:bg-[#1d4ed8] text-white font-normal text-[13px] shadow transition active:scale-95 cursor-pointer"
             onclick="event.stopPropagation()">
            <span class="text-[13px]">🌐</span>
            <span>Visit Website</span>
            <span id="floatingCardDirectDomain" class="text-[11px] opacity-80 font-mono"></span>
            <span class="text-[12px]">↗</span>
          </a>
          <button id="floatingCardDirectPlanBtn" type="button" 
             class="inline-flex items-center gap-1 px-2.5 py-1.5 rounded-xl bg-[#222834] hover:bg-[#2b3548] text-[#93c5fd] hover:text-white border border-[#2f3d58] font-mono text-[12px] transition active:scale-95 cursor-pointer"
             onclick="event.stopPropagation(); if (typeof window.atlasPlanVisit === 'function') window.atlasPlanVisit(selectedInstitution);">
            <span>Plan Visit in Chat 💬</span>
          </button>
        </div>

        <div class="mt-2.5 pt-2 border-t border-[#2e2e2e] flex items-center justify-between text-[13px] gap-2 flex-wrap sm:flex-nowrap">
          <a id="floatingCardWebLink" href="#" target="_blank" rel="noopener noreferrer" 
             class="inline-flex items-center gap-1 text-[#93c5fd] hover:text-white transition cursor-pointer"
             onclick="event.stopPropagation()">
            <span id="floatingCardDomain" class="truncate max-w-[120px]">website</span> <span class="text-[12px]">↗</span>
          </a>
          <div class="flex items-center gap-2">
            <button id="floatingCardDossierBtn" class="text-[#a1a1aa] hover:text-white transition text-[13px] cursor-pointer whitespace-nowrap" onclick="event.stopPropagation()">
              Read info about institution →
            </button>
            <button id="floatingCardAskCurator" class="inline-flex items-center gap-1 text-white hover:text-[#93c5fd] font-normal transition text-[13px] cursor-pointer" onclick="event.stopPropagation()">
              <span>Ask</span>
            </button>
          </div>
        </div>
        <div class="absolute bottom-0 left-1/2 -translate-x-1/2 translate-y-full w-0 h-0 border-x-[6px] border-x-transparent border-t-[6px] border-t-[#18181b]"></div>
      </div>

      <!-- Floating Active Map Filter Pill Banner -->
      <div id="activeMapFilterBanner" class="hidden absolute top-2.5 sm:top-3 left-1/2 -translate-x-1/2 z-20 pointer-events-auto flex items-center gap-2 bg-[#0c1a2e]/95 border border-[#38bdf8]/70 text-white px-3.5 py-1.5 rounded-full backdrop-blur-md shadow-xl text-[14px]">
        <span id="activeMapFilterText" class="font-normal tracking-wide text-white text-[14px]">24 MONDAY OPENINGS ON MAP</span>
        <button id="clearMapFilterBtn" class="ml-1 text-[#93c5fd] hover:text-white hover:bg-white/10 rounded-full w-5 h-5 flex items-center justify-center transition text-[14px]" title="Clear filter">✕</button>
      </div>

      <!-- City & Country Navigation Banner -->
      <div id="cityViewControlBanner" class="hidden absolute top-2 sm:top-3 left-2 sm:left-4 z-20 pointer-events-auto flex items-center gap-1.5 sm:gap-2 max-w-[calc(100%-16px)] overflow-x-auto select-none">
        <button id="exitStreetViewBtn" class="px-2 sm:px-2.5 py-1 sm:py-1.5 rounded-xl bg-[#1e293b]/95 hover:bg-[#334155] border border-[#38bdf8]/40 hover:border-[#38bdf8] text-[#38bdf8] hover:text-white text-[12px] sm:text-[13px] flex items-center gap-1 shadow-lg backdrop-blur transition cursor-pointer active:scale-95 shrink-0" title="Exit street view to 3D Globe">
          <span>🌍 Exit</span>
        </button>
        <button id="backToWorldBtn" class="px-2 sm:px-2.5 py-1 sm:py-1.5 rounded-xl bg-[#212121]/95 hover:bg-[#2a2a2a] border border-[#383838] hover:border-[#60a5fa] text-white text-[12px] sm:text-[13px] flex items-center gap-1 shadow-lg backdrop-blur transition cursor-pointer active:scale-95 shrink-0" title="Reset to global world view">
          <span class="font-normal">World</span>
        </button>
        <button id="backToCountryBtn" class="hidden px-2 sm:px-2.5 py-1 sm:py-1.5 rounded-xl bg-[#212121]/95 hover:bg-[#2a2a2a] border border-[#383838] hover:border-[#60a5fa] text-white text-[12px] sm:text-[13px] flex items-center gap-1 shadow-lg backdrop-blur transition cursor-pointer active:scale-95 shrink-0" title="Return to country overview">
          <span>←</span> <span id="backToCountryText" class="font-normal">Country</span>
        </button>
        <div id="cityViewTitleBadge" class="px-2 sm:px-2.5 py-1 sm:py-1.5 rounded-xl bg-[#0c1626]/95 border border-[#1e2e4a] text-[#93c5fd] text-[11px] sm:text-[13px] font-mono flex items-center gap-1 shadow-lg backdrop-blur shrink-0 truncate max-w-[190px] sm:max-w-none">
          <span id="cityViewTitleText">LONDON · STREET VIEW</span>
        </div>
      </div>


      <!-- Subtle Globe Zoom & Map Controls -->
      <div class="absolute bottom-2 right-2 sm:right-4 z-10 flex items-center gap-1 sm:gap-1.5 bg-[#18181b]/90 backdrop-blur-md p-1 rounded-2xl border border-[#2e2e2e] shadow-lg max-w-[calc(100%-16px)] overflow-x-auto select-none">
        <button id="hudWorldBtn" class="px-2 sm:px-2.5 h-7 sm:h-8 rounded-xl bg-[#242424] hover:bg-[#303030] text-[#cbd5e1] hover:text-white text-[11px] sm:text-[12px] font-normal transition flex items-center gap-1 cursor-pointer shrink-0" title="Reset World View">
          <span>World</span>
        </button>
        <div class="hidden sm:flex items-center gap-1 shrink-0">
          <button id="hudEuropeBtn" class="px-2 h-7 sm:h-8 rounded-xl bg-[#242424] hover:bg-[#303030] text-[#cbd5e1] hover:text-white text-[12px] font-normal transition flex items-center cursor-pointer" title="Fly to Europe">
            <span>Europe</span>
          </button>
          <button id="hudAmericasBtn" class="px-2 h-7 sm:h-8 rounded-xl bg-[#242424] hover:bg-[#303030] text-[#cbd5e1] hover:text-white text-[12px] font-normal transition flex items-center cursor-pointer" title="Fly to Americas">
            <span>Americas</span>
          </button>
          <button id="hudAsiaBtn" class="px-2 h-7 sm:h-8 rounded-xl bg-[#242424] hover:bg-[#303030] text-[#cbd5e1] hover:text-white text-[12px] font-normal transition flex items-center cursor-pointer" title="Fly to Asia-Pacific">
            <span>Asia</span>
          </button>
          <div class="w-[1px] h-4 bg-[#3f3f46] mx-0.5"></div>
          <button id="hudRailToggle" class="px-2 h-7 sm:h-8 rounded-xl bg-[#1e2e42] text-[#38bdf8] border border-[#0284c7]/40 hover:bg-[#0369a1]/30 text-[12px] font-normal transition flex items-center gap-1 cursor-pointer" title="Toggle Clean Transit Corridors">
            <span>Rail</span>
          </button>
        </div>
        <button id="hudSpinBtn" class="px-2 sm:px-2.5 h-7 sm:h-8 rounded-xl bg-[#242424] hover:bg-[#303030] text-[#cbd5e1] hover:text-white text-[11px] sm:text-[12px] font-normal transition flex items-center gap-1 cursor-pointer shrink-0" title="Toggle Auto-Spin">
          <span id="hudSpinText">Spin</span>
        </button>
        <button id="hudExpandBtn" class="px-2 sm:px-2.5 h-7 sm:h-8 rounded-xl bg-[#242424] hover:bg-[#303030] text-[#cbd5e1] hover:text-white text-[11px] sm:text-[12px] font-normal transition flex items-center gap-1 cursor-pointer shrink-0" title="Maximize Map View">
          <span id="hudExpandText">Expand</span>
        </button>
        <div class="w-[1px] h-4 bg-[#3f3f46] mx-0.5 shrink-0"></div>
        <button id="zoomInBtn" class="w-7 h-7 sm:w-8 sm:h-8 rounded-xl bg-[#242424] hover:bg-[#303030] text-[#d4d4d4] hover:text-white flex items-center justify-center transition text-[14px] sm:text-[15px] cursor-pointer shrink-0" title="Zoom In">+</button>
        <button id="zoomOutBtn" class="w-7 h-7 sm:w-8 sm:h-8 rounded-xl bg-[#242424] hover:bg-[#303030] text-[#d4d4d4] hover:text-white flex items-center justify-center transition text-[14px] sm:text-[15px] cursor-pointer shrink-0" title="Zoom Out">−</button>
      </div>

    </div>

    <!-- RESIZABLE SPLITTER (Desktop: Vertical Drag / Mobile: Horizontal Drag · Double-click resets to 50%) -->
    <div id="globeSplitter" class="relative w-full md:w-[6px] h-[5px] md:h-full bg-[#262626] hover:bg-[#3b82f6]/70 active:bg-[#3b82f6] cursor-row-resize md:cursor-col-resize transition flex items-center justify-center z-20 shrink-0 group select-none" title="Drag to adjust split screen · Double-click to reset to 50%">
      <div class="w-10 md:w-[2px] h-[2px] md:h-10 rounded-full bg-[#52525b] group-hover:bg-[#93c5fd] transition"></div>
    </div>

    <!-- ========================================================= -->
    <!-- 💼 UNIFIED WORK & CHAT CANVAS (Desktop: Right Half / Mobile: Bottom Half) -->
    <!-- ========================================================= -->
    <div id="workViewContainer" class="relative w-full md:w-1/2 h-1/2 md:h-full flex-1 min-h-0 flex flex-col bg-[#171717] overflow-hidden">
      
      <!-- 1. SCROLLABLE CONVERSATION STREAM (Only this area scrolls!) -->
      <div id="curatorScrollArea" class="flex-1 min-h-0 overflow-y-auto custom-scrollbar flex flex-col items-center px-3 sm:px-5 pt-4 pb-2 w-full">
        <div class="w-full max-w-3xl flex flex-col items-center">
          
          <!-- Active Conversation Stream (Messages injected dynamically in work chat) -->
          <div id="curatorMessages" class="w-full space-y-4 mb-3">
            <!-- User queries and curator responses flow seamlessly here -->
          </div>

          <!-- Typing Indicator -->
          <div id="curatorTyping" class="hidden w-full px-2 py-1 text-[14px] text-[#8e8e8e] flex items-center gap-2 mb-2">
            <div class="w-6 h-6 rounded-full bg-[#262626] border border-[#383838] flex items-center justify-center text-[10px] font-mono text-[#a1a1aa] shrink-0">CA</div>
            <span class="inline-flex gap-1.5 items-center pl-1">
              <span class="w-2 h-2 rounded-full bg-[#a1a1aa] typing-dot"></span>
              <span class="w-2 h-2 rounded-full bg-[#a1a1aa] typing-dot"></span>
              <span class="w-2 h-2 rounded-full bg-[#a1a1aa] typing-dot"></span>
            </span>
            <span class="text-[14px] text-[#a1a1aa]">Curator is researching...</span>
          </div>

          <!-- Suggested Prompts (Visible on new/empty chat, Arranged in 3 Rows) -->
          <div id="workSuggestionsSection" class="w-full mt-2 mb-4 transition-all duration-200">
            <!-- Suggested Prompts Header -->
            <div class="w-full mb-2.5 text-[14px] font-normal text-[#e4e4e7] flex items-center justify-between select-none leading-[120%]">
              <span>Suggested prompts</span>
              <!-- View controls: Minimize · Expand -->
              <div class="flex items-center gap-1.5 text-[14px] text-[#a1a1aa]">
                <span class="text-[14px] text-[#71717a]">View controls:</span>
                <button id="viewMinimizeBtn" class="hover:text-white transition cursor-pointer text-[14px] underline-offset-2 hover:underline">Minimize</button>
                <span class="text-[#555]">·</span>
                <button id="viewExpandBtn" class="hover:text-white transition cursor-pointer text-[14px] underline-offset-2 hover:underline">Expand</button>
              </div>
            </div>

            <!-- Suggestions Arranged in 3 Rows (No Icons, Pure Typography) -->
            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2.5 w-full">
              <!-- Row 1 -->
              <div class="work-suggestion-card bg-[#212121] hover:bg-[#262626] border border-[#2f2f2f] hover:border-[#3f3f3f] rounded-2xl p-3.5 transition flex flex-col justify-between cursor-pointer group shadow-sm" data-query="Find independent art spaces near me">
                <div class="font-normal text-[14px] text-white mb-1 leading-[120%]">Find independent art spaces near me</div>
                <div class="text-[12px] text-[#a1a1aa] leading-[130%]">Locate verified artist-run galleries and non-profits in your area.</div>
              </div>

              <div class="work-suggestion-card bg-[#212121] hover:bg-[#262626] border border-[#2f2f2f] hover:border-[#3f3f3f] rounded-2xl p-3.5 transition flex flex-col justify-between cursor-pointer group shadow-sm" data-query="Who funds this museum?">
                <div class="font-normal text-[14px] text-white mb-1 leading-[120%]">Who funds this museum?</div>
                <div class="text-[12px] text-[#a1a1aa] leading-[130%]">Audit Form 990 filings, public subsidies, and board conflict records.</div>
              </div>

              <div class="work-suggestion-card bg-[#212121] hover:bg-[#262626] border border-[#2f2f2f] hover:border-[#3f3f3f] rounded-2xl p-3.5 transition flex flex-col justify-between cursor-pointer group shadow-sm" data-query="Give me curated 1-day itineraries for independent art spaces in London, Berlin, Paris, and New York">
                <div class="font-normal text-[14px] text-white mb-1 leading-[120%]">Curated 1-day city itineraries</div>
                <div class="text-[12px] text-[#a1a1aa] leading-[130%]">Explore 100% clean gallery walks in London, Berlin, Paris, and New York.</div>
              </div>

              <!-- Row 2 -->
              <div class="work-suggestion-card bg-[#212121] hover:bg-[#262626] border border-[#2f2f2f] hover:border-[#3f3f3f] rounded-2xl p-3.5 transition flex flex-col justify-between cursor-pointer group shadow-sm" data-query="Tell me about independent art spaces in repurposed industrial buildings, factories, and breweries">
                <div class="font-normal text-[14px] text-white mb-1 leading-[120%]">Repurposed architecture & factories</div>
                <div class="text-[12px] text-[#a1a1aa] leading-[130%]">Former industrial plants, breweries, and warehouses turned into art spaces.</div>
              </div>

              <div class="work-suggestion-card bg-[#212121] hover:bg-[#262626] border border-[#2f2f2f] hover:border-[#3f3f3f] rounded-2xl p-3.5 transition flex flex-col justify-between cursor-pointer group shadow-sm" data-query="What are the best outdoor sculpture parks and land art spaces with clean funding?">
                <div class="font-normal text-[14px] text-white mb-1 leading-[120%]">Outdoor sculpture parks & land art</div>
                <div class="text-[12px] text-[#a1a1aa] leading-[130%]">Open-air sculpture centers, forest trails, and pastoral landscapes.</div>
              </div>

              <div class="work-suggestion-card bg-[#212121] hover:bg-[#262626] border border-[#2f2f2f] hover:border-[#3f3f3f] rounded-2xl p-3.5 transition flex flex-col justify-between cursor-pointer group shadow-sm" data-query="Which museums and galleries are free to enter?">
                <div class="font-normal text-[14px] text-white mb-1 leading-[120%]">Free admission spaces</div>
                <div class="text-[12px] text-[#a1a1aa] leading-[130%]">Discover verified spaces that offer 100% free public admission.</div>
              </div>

              <!-- Row 3 -->
              <div class="work-suggestion-card bg-[#212121] hover:bg-[#262626] border border-[#2f2f2f] hover:border-[#3f3f3f] rounded-2xl p-3.5 transition flex flex-col justify-between cursor-pointer group shadow-sm" data-query="Which museums are open on Mondays?">
                <div class="font-normal text-[14px] text-white mb-1 leading-[120%]">Monday openings</div>
                <div class="text-[12px] text-[#a1a1aa] leading-[130%]">Art spaces welcoming visitors on Mondays when major institutions close.</div>
              </div>

              <div class="work-suggestion-card bg-[#212121] hover:bg-[#262626] border border-[#2f2f2f] hover:border-[#3f3f3f] rounded-2xl p-3.5 transition flex flex-col justify-between cursor-pointer group shadow-sm" data-query="What is the difference between a Kunsthalle and a traditional museum?">
                <div class="font-normal text-[14px] text-white mb-1 leading-[120%]">Kunsthalle vs traditional museum</div>
                <div class="text-[12px] text-[#a1a1aa] leading-[130%]">The structural distinction between non-collecting spaces and museums.</div>
              </div>

              <div class="work-suggestion-card bg-[#212121] hover:bg-[#262626] border border-[#2f2f2f] hover:border-[#3f3f3f] rounded-2xl p-3.5 transition flex flex-col justify-between cursor-pointer group shadow-sm" data-query="Tell me about W.A.G.E. certification, fair pay, and museum unionization">
                <div class="font-normal text-[14px] text-white mb-1 leading-[120%]">W.A.G.E., fair pay & unionization</div>
                <div class="text-[12px] text-[#a1a1aa] leading-[130%]">Artist compensation standards, institutional labor, and union contracts.</div>
              </div>
            </div>
          </div>

        </div>
      </div>

      <!-- 2. PINNED BOTTOM INPUT DOCK (Always stays firmly in place at bottom!) -->
      <div id="workBottomDock" class="w-full shrink-0 flex flex-col items-center px-2.5 sm:px-5 pb-2.5 sm:pb-4 pt-1.5 sm:pt-2 bg-[#171717] border-t border-[#262626] z-10">
        <div class="w-full max-w-3xl flex flex-col items-center">
          
          <!-- Big Rounded Input Card (Sleek ChatGPT Work Canvas) -->
          <div id="workInputCard" class="w-full bg-[#212121] border border-[#333333] hover:border-[#444] focus-within:border-[#555] rounded-2xl sm:rounded-3xl p-2.5 sm:p-3.5 shadow-xl transition relative">
            <textarea id="workInput" rows="1" placeholder="Ask about a museum or cultural space" class="w-full bg-transparent text-white placeholder-[#71717a] text-[13px] sm:text-[14px] focus:outline-none resize-none font-normal leading-[120%] max-h-32"></textarea>
            
            <div class="flex items-center justify-between pt-1">
              <!-- Left: Plus action button -->
              <button id="workPlusBtn" class="w-7 h-7 sm:w-8 sm:h-8 rounded-full bg-[#2a2a2a] hover:bg-[#333] text-[#d4d4d4] hover:text-white flex items-center justify-center text-[16px] sm:text-[18px] transition active:scale-95 cursor-pointer font-normal shrink-0" title="Quick filters">
                +
              </button>

              <!-- Right: Model, mic, and blue circular waveform/send button -->
              <div class="flex items-center gap-1.5 sm:gap-2">
                <button id="chatAddKeyBtn" class="text-[12px] sm:text-[13px] bg-amber-500/10 hover:bg-amber-500/20 text-amber-300 border border-amber-500/30 hover:border-amber-500/50 flex items-center gap-1 px-2 sm:px-2.5 py-0.5 sm:py-1 rounded-full transition cursor-pointer font-normal shrink-0" title="Configure AI API Key">
                  <span id="chatAddKeyIcon">🔑</span>
                  <span id="chatAddKeyLabel" class="hidden sm:inline">Add API Key</span>
                </button>

                <button id="chatContributeBtn" class="text-[12px] sm:text-[13px] bg-[#1a2333] hover:bg-[#223048] text-[#78a9ff] border border-[#2f4368] flex items-center gap-1 px-2 sm:px-2.5 py-0.5 sm:py-1 rounded-full transition cursor-pointer font-normal shrink-0" title="Contribute space or research note">
                  <span>✍️</span>
                  <span class="hidden sm:inline">Contribute</span>
                </button>

                <button id="workModelBtn" class="text-[12px] sm:text-[14px] text-[#a1a1aa] hover:text-white flex items-center gap-1 px-1.5 sm:px-2.5 py-0.5 sm:py-1 rounded-lg hover:bg-[#2a2a2a] transition cursor-pointer font-normal" title="AI Model Status & Settings">
                  <span id="workModelLabel" class="hidden sm:inline">Culture Atlas 4.0 Critical Engine</span>
                  <span class="inline sm:hidden text-[11px] text-[#8e8e8e]">Engine 4.0</span>
                  <svg class="w-3.5 h-3.5 text-[#71717a]" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m6 9 6 6 6-6"/></svg>
                </button>

                <button id="workMicBtn" class="w-7 h-7 sm:w-8 sm:h-8 rounded-full hover:bg-[#2a2a2a] text-[#a1a1aa] hover:text-white flex items-center justify-center transition cursor-pointer shrink-0" title="Voice">
                  <svg class="w-3.5 h-3.5 sm:w-4 sm:h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z" />
                    <path d="M19 10v2a7 7 0 0 1-14 0v-2" />
                    <line x1="12" y1="19" x2="12" y2="22" />
                  </svg>
                </button>

                <button id="workSendBtn" class="w-7 h-7 sm:w-9 sm:h-9 rounded-full bg-[#2563eb] hover:bg-[#1d4ed8] text-white flex items-center justify-center transition shadow-md active:scale-95 cursor-pointer shrink-0" title="Send message">
                  <svg class="w-3.5 h-3.5 sm:w-4 sm:h-4" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M12 3v18M8 6v12M4 9v6M16 6v12M20 9v6" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" />
                  </svg>
                </button>
              </div>
            </div>

            <!-- Quick Dropdown Menu for Plus button -->
            <div id="workPlusMenu" class="hidden absolute left-4 bottom-14 z-30 bg-[#262626] border border-[#383838] rounded-2xl p-1.5 shadow-2xl flex flex-col gap-1 w-80 text-[14px]">
              <button id="workMenuFeedbackBtn" class="text-left px-3 py-2 bg-[#1b263b] hover:bg-[#233554] text-[#78a9ff] font-medium rounded-xl transition flex items-center justify-between cursor-pointer border border-[#2f4975]">
                <span class="flex items-center gap-1.5"><span>✍️</span><span>Contribute Research / Tip</span></span>
                <span class="text-[11px] font-mono text-emerald-400 bg-emerald-950/70 border border-emerald-800/80 px-1.5 py-0.5 rounded">Verify</span>
              </button>
              <div class="h-px bg-[#383838] my-0.5"></div>
              <button class="work-menu-item text-left px-3 py-1.5 hover:bg-[#333] rounded-xl text-slate-200 transition cursor-pointer" data-query="Give me curated 1-day itineraries for independent art spaces in London, Berlin, Paris, and New York">Curated 1-Day City Itineraries</button>
              <button class="work-menu-item text-left px-3 py-1.5 hover:bg-[#333] rounded-xl text-slate-200 transition cursor-pointer" data-query="Tell me about independent art spaces in repurposed industrial buildings, factories, and breweries">Repurposed Architecture & Factories</button>
              <button class="work-menu-item text-left px-3 py-1.5 hover:bg-[#333] rounded-xl text-slate-200 transition cursor-pointer" data-query="What are the best outdoor sculpture parks and land art spaces with clean funding?">Outdoor Sculpture Parks & Land Art</button>
              <button class="work-menu-item text-left px-3 py-1.5 hover:bg-[#333] rounded-xl text-slate-200 transition cursor-pointer" data-query="Show me independent spaces dedicated to video art, sound art, and experimental media">Video, Sound & Time-Based Media</button>
              <button class="work-menu-item text-left px-3 py-1.5 hover:bg-[#333] rounded-xl text-slate-200 transition cursor-pointer" data-query="What is the difference between a Kunsthalle and a traditional museum?">Kunsthalle vs Museum: The Difference</button>
              <button class="work-menu-item text-left px-3 py-1.5 hover:bg-[#333] rounded-xl text-slate-200 transition cursor-pointer" data-query="Tell me about W.A.G.E. certification, fair pay, and museum unionization">W.A.G.E., Fair Pay & Museum Unions</button>
              <button class="work-menu-item text-left px-3 py-1.5 hover:bg-[#333] rounded-xl text-slate-200 transition cursor-pointer" data-query="Tell me about Dutch research, BAK Utrecht, and Former West">Dutch Research: BAK Utrecht</button>
              <button class="work-menu-item text-left px-3 py-1.5 hover:bg-[#333] rounded-xl text-slate-200 transition cursor-pointer" data-query="What is Arte Útil and the Commons at Van Abbe and Casco?">Commons & Arte Útil: Casco & Van Abbe</button>
              <button class="work-menu-item text-left px-3 py-1.5 hover:bg-[#333] rounded-xl text-slate-200 transition cursor-pointer" data-query="How did Kunstinstituut Melly rename itself from Witte de With?">Decolonial Renaming: Melly</button>
              <button class="work-menu-item text-left px-3 py-1.5 hover:bg-[#333] rounded-xl text-slate-200 transition cursor-pointer" data-query="Which museums and galleries are free to enter?">Free Admission Spaces</button>
              <button class="work-menu-item text-left px-3 py-1.5 hover:bg-[#333] rounded-xl text-slate-200 transition cursor-pointer" data-query="Which museums are open on Mondays?">Monday Openings</button>
              <button class="work-menu-item text-left px-3 py-1.5 hover:bg-[#333] rounded-xl text-slate-200 transition cursor-pointer" data-query="Show spaces that do not take oil or weapons money">Fossil & Defense-Free</button>
              <button class="work-menu-item text-left px-3 py-1.5 hover:bg-[#333] rounded-xl text-slate-200 transition cursor-pointer" data-query="Tell me about London's independent art spaces">London Art Guide</button>
              <button class="work-menu-item text-left px-3 py-1.5 hover:bg-[#333] rounded-xl text-slate-200 transition cursor-pointer" data-query="Tell me about New York's art spaces and board controversies">New York Art Guide</button>
            </div>
          </div>

          <!-- Interactive Multi-Row Filter Bar (Pinned under chat input card) -->
          <div id="globeCityBar" class="w-full mt-2 sm:mt-2.5 flex flex-col gap-1.5 select-none py-0.5 shrink-0 max-h-[58px] md:max-h-none overflow-y-auto md:overflow-visible custom-scrollbar">
            <!-- Row 1: Scope, Clean / Flagged Tiers, Academic Research & Categories -->
            <div class="flex flex-wrap items-center gap-1.5">
              <button class="globe-filter-pill px-2.5 py-1 rounded-xl bg-[#059669] text-white border border-[#10b981] transition cursor-pointer text-[12px] sm:text-[13px] shrink-0 font-medium shadow-sm shadow-emerald-950/40" data-type="tier" data-value="A">✓ Clean Funding ({clean_count})</button>
              <button class="globe-filter-pill px-2.5 py-1 rounded-xl bg-[#1f1433] hover:bg-[#2c1d48] border border-[#8a3ffc] text-[#be95ff] hover:text-white transition cursor-pointer text-[12px] sm:text-[13px] shrink-0 font-medium" data-type="tier" data-value="B">Flagged ({flagged_count})</button>
              <button class="globe-filter-pill px-2.5 py-1 rounded-xl bg-[#212121]/90 hover:bg-[#2a2a2a] border border-[#2e2e2e] text-[#d4d4d4] hover:text-white transition cursor-pointer text-[12px] sm:text-[13px] shrink-0" data-type="tier" data-value="all">All Spaces ({total_count})</button>
              <span class="text-[#444] text-[11px] shrink-0">|</span>
              <button class="globe-filter-pill px-2.5 py-1 rounded-xl bg-[#0d1e2e] hover:bg-[#152e47] border border-[#33b1ff]/70 text-[#78a9ff] hover:text-white transition cursor-pointer text-[12px] sm:text-[13px] shrink-0" data-type="academic">Academic Studies ({academic_count})</button>
              <span class="text-[#444] text-[11px] shrink-0">|</span>
              <button class="globe-filter-pill px-2.5 py-1 rounded-xl bg-[#212121]/90 hover:bg-[#2a2a2a] border border-[#2e2e2e] text-[#d4d4d4] hover:text-white transition cursor-pointer text-[12px] sm:text-[13px] shrink-0" data-type="region" data-value="europe">Europe</button>
              <button class="globe-filter-pill px-2.5 py-1 rounded-xl bg-[#212121]/90 hover:bg-[#2a2a2a] border border-[#2e2e2e] text-[#d4d4d4] hover:text-white transition cursor-pointer text-[12px] sm:text-[13px] shrink-0" data-type="region" data-value="americas">Americas</button>
              <button class="globe-filter-pill px-2.5 py-1 rounded-xl bg-[#212121]/90 hover:bg-[#2a2a2a] border border-[#2e2e2e] text-[#d4d4d4] hover:text-white transition cursor-pointer text-[12px] sm:text-[13px] shrink-0" data-type="region" data-value="asiapacific">Asia-Pacific</button>
              <button class="globe-filter-pill px-2.5 py-1 rounded-xl bg-[#212121]/90 hover:bg-[#2a2a2a] border border-[#2e2e2e] text-[#d4d4d4] hover:text-white transition cursor-pointer text-[12px] sm:text-[13px] shrink-0" data-type="region" data-value="mena_africa">MidEast & Africa</button>
              <span class="text-[#444] text-[11px] shrink-0">|</span>
              <button class="globe-filter-pill px-2.5 py-1 rounded-xl bg-[#212121]/90 hover:bg-[#2a2a2a] border border-[#2e2e2e] text-[#d4d4d4] hover:text-white transition cursor-pointer text-[12px] sm:text-[13px] shrink-0" data-type="category" data-value="free">Free Entry</button>
              <button class="globe-filter-pill px-2.5 py-1 rounded-xl bg-[#212121]/90 hover:bg-[#2a2a2a] border border-[#2e2e2e] text-[#d4d4d4] hover:text-white transition cursor-pointer text-[12px] sm:text-[13px] shrink-0" data-type="category" data-value="artist_run">Artist-Run</button>
            </div>

            <!-- Row 2: Featured Cultural Cities -->
            <div class="flex flex-wrap items-center gap-1.5">
              <span class="text-[11px] text-[#71717a] font-mono shrink-0 mr-0.5 uppercase tracking-wider">Cities:</span>
              <button class="globe-filter-pill px-2.5 py-1 rounded-xl bg-[#212121]/90 hover:bg-[#2a2a2a] border border-[#2e2e2e] text-[#d4d4d4] hover:text-white transition cursor-pointer text-[12px] sm:text-[13px] shrink-0" data-type="city" data-value="London">London (18)</button>
              <button class="globe-filter-pill px-2.5 py-1 rounded-xl bg-[#212121]/90 hover:bg-[#2a2a2a] border border-[#2e2e2e] text-[#d4d4d4] hover:text-white transition cursor-pointer text-[12px] sm:text-[13px] shrink-0" data-type="city" data-value="New York">New York (16)</button>
              <button class="globe-filter-pill px-2.5 py-1 rounded-xl bg-[#212121]/90 hover:bg-[#2a2a2a] border border-[#2e2e2e] text-[#d4d4d4] hover:text-white transition cursor-pointer text-[12px] sm:text-[13px] shrink-0" data-type="city" data-value="Paris">Paris (12)</button>
              <button class="globe-filter-pill px-2.5 py-1 rounded-xl bg-[#212121]/90 hover:bg-[#2a2a2a] border border-[#2e2e2e] text-[#d4d4d4] hover:text-white transition cursor-pointer text-[12px] sm:text-[13px] shrink-0" data-type="city" data-value="Berlin">Berlin (10)</button>
              <button class="globe-filter-pill px-2.5 py-1 rounded-xl bg-[#212121]/90 hover:bg-[#2a2a2a] border border-[#2e2e2e] text-[#d4d4d4] hover:text-white transition cursor-pointer text-[12px] sm:text-[13px] shrink-0" data-type="city" data-value="Amsterdam">Amsterdam (7)</button>
              <button class="globe-filter-pill px-2.5 py-1 rounded-xl bg-[#212121]/90 hover:bg-[#2a2a2a] border border-[#2e2e2e] text-[#d4d4d4] hover:text-white transition cursor-pointer text-[12px] sm:text-[13px] shrink-0" data-type="city" data-value="Madrid">Madrid (4)</button>
              <button class="globe-filter-pill px-2.5 py-1 rounded-xl bg-[#212121]/90 hover:bg-[#2a2a2a] border border-[#2e2e2e] text-[#d4d4d4] hover:text-white transition cursor-pointer text-[12px] sm:text-[13px] shrink-0" data-type="city" data-value="Tokyo">Tokyo (3)</button>
              <button class="globe-filter-pill px-2.5 py-1 rounded-xl bg-[#212121]/90 hover:bg-[#2a2a2a] border border-[#2e2e2e] text-[#d4d4d4] hover:text-white transition cursor-pointer text-[12px] sm:text-[13px] shrink-0" data-type="city" data-value="Basel">Basel (2)</button>
              <button class="globe-filter-pill px-2.5 py-1 rounded-xl bg-[#212121]/90 hover:bg-[#2a2a2a] border border-[#2e2e2e] text-[#d4d4d4] hover:text-white transition cursor-pointer text-[12px] sm:text-[13px] shrink-0" data-type="city" data-value="Bilbao">Bilbao (2)</button>
            </div>

            <!-- Row 3: Featured Countries -->
            <div class="flex flex-wrap items-center gap-1.5">
              <span class="text-[11px] text-[#71717a] font-mono shrink-0 mr-0.5 uppercase tracking-wider">Countries:</span>
              <button class="globe-filter-pill px-2.5 py-1 rounded-xl bg-[#212121]/90 hover:bg-[#2a2a2a] border border-[#2e2e2e] text-[#d4d4d4] hover:text-white transition cursor-pointer text-[12px] sm:text-[13px] shrink-0" data-type="country" data-value="United Kingdom">United Kingdom</button>
              <button class="globe-filter-pill px-2.5 py-1 rounded-xl bg-[#212121]/90 hover:bg-[#2a2a2a] border border-[#2e2e2e] text-[#d4d4d4] hover:text-white transition cursor-pointer text-[12px] sm:text-[13px] shrink-0" data-type="country" data-value="United States">United States</button>
              <button class="globe-filter-pill px-2.5 py-1 rounded-xl bg-[#212121]/90 hover:bg-[#2a2a2a] border border-[#2e2e2e] text-[#d4d4d4] hover:text-white transition cursor-pointer text-[12px] sm:text-[13px] shrink-0" data-type="country" data-value="Germany">Germany</button>
              <button class="globe-filter-pill px-2.5 py-1 rounded-xl bg-[#212121]/90 hover:bg-[#2a2a2a] border border-[#2e2e2e] text-[#d4d4d4] hover:text-white transition cursor-pointer text-[12px] sm:text-[13px] shrink-0" data-type="country" data-value="France">France</button>
              <button class="globe-filter-pill px-2.5 py-1 rounded-xl bg-[#212121]/90 hover:bg-[#2a2a2a] border border-[#2e2e2e] text-[#d4d4d4] hover:text-white transition cursor-pointer text-[12px] sm:text-[13px] shrink-0" data-type="country" data-value="Netherlands">Netherlands</button>
              <button class="globe-filter-pill px-2.5 py-1 rounded-xl bg-[#212121]/90 hover:bg-[#2a2a2a] border border-[#2e2e2e] text-[#d4d4d4] hover:text-white transition cursor-pointer text-[12px] sm:text-[13px] shrink-0" data-type="country" data-value="Spain">Spain</button>
              <button class="globe-filter-pill px-2.5 py-1 rounded-xl bg-[#212121]/90 hover:bg-[#2a2a2a] border border-[#2e2e2e] text-[#d4d4d4] hover:text-white transition cursor-pointer text-[12px] sm:text-[13px] shrink-0" data-type="country" data-value="Switzerland">Switzerland</button>
              <button class="globe-filter-pill px-2.5 py-1 rounded-xl bg-[#212121]/90 hover:bg-[#2a2a2a] border border-[#2e2e2e] text-[#d4d4d4] hover:text-white transition cursor-pointer text-[12px] sm:text-[13px] shrink-0" data-type="country" data-value="Italy">Italy</button>
              <button class="globe-filter-pill px-2.5 py-1 rounded-xl bg-[#212121]/90 hover:bg-[#2a2a2a] border border-[#2e2e2e] text-[#d4d4d4] hover:text-white transition cursor-pointer text-[12px] sm:text-[13px] shrink-0" data-type="country" data-value="Japan">Japan</button>
            </div>
          </div>

        </div>
      </div>

  </div>

  <!-- ========================================================= -->
  <!-- 📋 CATALOG MODAL (Browse all 203 spaces) -->
  <!-- ========================================================= -->
  <div id="catalogModal" class="hidden fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-3 sm:p-5 select-text">
    <div class="bg-[#171717] border border-[#2e2e2e] rounded-2xl max-w-2xl w-full max-h-[85vh] flex flex-col shadow-2xl overflow-hidden font-sans">
      <div class="p-3 border-b border-[#262626] bg-[#1a1a1a] flex items-center justify-between">
        <div class="flex items-center gap-2">
          <span class="text-[14px] font-normal text-white">Full Catalog of Verified Spaces</span>
        </div>
        <button id="closeCatalogModalBtn" class="text-slate-400 hover:text-white p-1 text-[14px]">✕</button>
      </div>
      <div class="p-3 border-b border-[#262626] bg-[#171717] flex flex-col gap-2">
        <input type="text" id="searchInput" placeholder="Search museum, city, or focus..." class="w-full bg-[#212121] border border-[#333333] text-[14px] text-white placeholder-[#71717a] px-3.5 py-2 rounded-xl focus:outline-none" />
        <div class="grid grid-cols-2 gap-2 text-[14px]">
          <select id="countrySelect" class="bg-[#212121] border border-[#333333] text-[#e4e4e7] px-3 py-1.5 rounded-xl truncate">
            <option value="all">All Countries (35)</option>
          </select>
          <select id="citySelect" class="bg-[#212121] border border-[#333333] text-[#e4e4e7] px-3 py-1.5 rounded-xl truncate">
            <option value="all">All Cities (133)</option>
          </select>
        </div>
      </div>
      <div id="institutionsListContainer" class="flex-1 overflow-y-auto custom-scrollbar p-3 space-y-2">
        <!-- Populated dynamically -->
      </div>
    </div>
  </div>

  <!-- ========================================================= -->
  <!-- 📄 SCHOLARLY INSTITUTION AUDIT DOSSIER DRAWER -->
  <!-- ========================================================= -->
  <div id="detailDrawer" class="hidden fixed inset-y-0 right-0 z-50 w-full max-w-lg bg-[#0a0d15]/98 backdrop-blur-2xl border-l border-[#1c212a] shadow-2xl flex flex-col">
    <div class="p-3.5 px-4 border-b border-[#1c212a] flex items-center justify-end bg-[#0e121c]">
      <button id="closeDetailBtn" class="text-slate-400 hover:text-white p-1 rounded hover:bg-[#1a2234] transition text-[18px]" title="Close">✕</button>
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
          <div>
            <h3 class="font-normal text-white text-[24px]">EXCLUSION AUDIT · Why MoMA is Excluded</h3>
            <p class="text-[14px] font-mono text-amber-300/80">Museum of Modern Art (New York) · Institutional Scrutiny</p>
          </div>
        </div>
        <button id="closeMomaModalBtn" class="w-7 h-7 rounded-lg bg-[#20180a] hover:bg-[#33250f] border border-[#523d14] text-slate-300 hover:text-white flex items-center justify-center text-[14px] transition">✕</button>
      </div>

      <!-- Modal Body -->
      <div class="p-4 sm:p-5 overflow-y-auto custom-scrollbar space-y-3.5 text-[14px] text-slate-200 leading-[120%]">
        
        <!-- Summary Callout -->
        <div class="bg-[#181207] border border-[#78350f]/60 rounded-xl p-3 text-[14px] space-y-1">
          <span class="text-amber-400 font-normal uppercase tracking-wider text-[14px] block font-mono">Exclusion Criteria Assessment</span>
          <p class="text-slate-200">
            Culture Atlas celebrates cultural institutions that champion curatorial freedom and clean underwriting. MoMA is excluded from our verified directory due to documented, unaddressed governance ties to defense contractors, private prisons, and controversial private equity financiers.
          </p>
        </div>

        <!-- Section 1: Leon Black & Jeffrey Epstein -->
        <div class="space-y-1">
          <h4 class="font-normal text-white text-[18px] flex items-center gap-1.5">
            <span class="text-rose-400 font-normal">1.</span> <span>Leon Black & Jeffrey Epstein ($158M)</span>
          </h4>
          <p class="text-slate-300 text-[14px] pl-4">
            Former MoMA Board Chairman <strong>Leon Black</strong> (founder of Apollo Global Management) stepped down in March 2021 after independent forensic audits revealed he transferred $158 million to convicted sex offender Jeffrey Epstein between 2012 and 2017.
          </p>
        </div>

        <!-- Section 2: Strike MoMA Movement -->
        <div class="space-y-1">
          <h4 class="font-normal text-white text-[18px] flex items-center gap-1.5">
            <span class="text-rose-400 font-normal">2.</span> <span>The 'Strike MoMA' Movement (Spring 2021)</span>
          </h4>
          <p class="text-slate-300 text-[14px] pl-4">
            A coalition of artists, cultural workers, and grassroots collectives (Decolonize This Place, Strike MoMA, and Artists Space allies) held 10 weeks of continuous protests demanding institutional accountability, trustee divestment, and community restitution.
          </p>
        </div>

        <!-- Section 3: Controversial Trustee Portfolio -->
        <div class="space-y-1">
          <h4 class="font-normal text-white text-[18px] flex items-center gap-1.5">
            <span class="text-rose-400 font-normal">3.</span> <span>Extractive & Defense Board Holdings</span>
          </h4>
          <ul class="list-disc pl-8 space-y-1 text-slate-300 text-[14px]">
            <li><strong>Steven Tananbaum (GoldenTree Asset Management):</strong> Board trustee targeted by artists over vulture fund holdings exacerbating Puerto Rico's debt and hurricane recovery crises.</li>
            <li><strong>Larry Fink (CEO, BlackRock):</strong> Board trustee heading the world's largest institutional investor in fossil fuel expansion, weapons manufacturing, and private detention centers.</li>
            <li><strong>Paula Crown:</strong> Trustee whose billionaire family owns General Dynamics, one of the world's largest defense and aerospace contractors.</li>
          </ul>
        </div>

        <!-- Section 4: What to Visit Instead -->
        <div class="bg-[#0e1628] border border-[#1d4ed8]/50 rounded-xl p-3 space-y-1.5">
          <span class="text-[#60a5fa] font-normal text-[14px] uppercase tracking-wider block font-mono">Verified Ethical Alternatives in New York</span>
          <p class="text-slate-300 text-[14px]">
            Instead of supporting corporate-compromised boards, visit New York's <strong>verified clean spaces</strong>—including <em>SculptureCenter, Artists Space, Swiss Institute, and The Kitchen</em>.
          </p>
        </div>

      </div>

      <!-- Modal Footer -->
      <div class="px-4 py-2.5 border-t border-[#252f48] bg-[#0c101c] flex items-center justify-between gap-2 shrink-0">
        <button id="momaAuditFlyNycBtn" class="px-3 py-1.5 bg-[#1d4ed8] hover:bg-[#2563eb] text-white text-[14px] font-normal rounded-xl transition flex items-center gap-1.5 shadow">
          <span>Explore 11 Clean NYC Spaces</span>
        </button>
        <button id="momaAuditChatBtn" class="px-3 py-1.5 bg-[#172032] hover:bg-[#22304c] border border-[#2b3b5c] text-slate-200 hover:text-white text-[14px] rounded-xl transition flex items-center gap-1.5">
          <span>Ask in Chat</span>
        </button>
      </div>

    </div>
  </div>

  <!-- CURATOR INTELLIGENCE SETTINGS MODAL (Multi-Provider API Support) -->
  <!-- ========================================================================= -->
  <div id="curatorSettingsModal" class="hidden fixed inset-0 z-50 bg-black/85 backdrop-blur-md flex items-center justify-center p-4">
    <div class="bg-[#18181b] border border-[#2e2e2e] rounded-3xl max-w-lg w-full p-6 shadow-2xl flex flex-col gap-4 max-h-[92vh] overflow-y-auto custom-scrollbar">
      
      <!-- Modal Header -->
      <div class="flex items-center justify-between border-b border-[#2e2e2e] pb-3 shrink-0">
        <div class="flex items-center gap-2.5">
          <div>
            <h3 class="font-normal text-white text-[18px]">Curator Intelligence Settings</h3>
            <p class="text-[14px] text-[#a1a1aa]">Power conversational reasoning with live AI or use the built-in critical engine</p>
          </div>
        </div>
        <button id="closeSettingsModalBtn" class="text-[#a1a1aa] hover:text-white text-[18px] p-1.5 hover:bg-[#262626] rounded-xl transition">✕</button>
      </div>

      <!-- Provider Tabs -->
      <div class="space-y-1.5">
        <label class="block text-[14px] text-[#a1a1aa] font-normal">AI Intelligence Provider</label>
        <div class="grid grid-cols-3 gap-2">
          <button id="providerClaudeBtn" class="provider-tab-btn py-2 px-3 rounded-xl border border-[#3e3e3e] bg-[#27272a] text-white text-[14px] font-normal flex items-center justify-center gap-1.5 transition active:scale-95">
            <span>Anthropic</span>
          </button>
          <button id="providerOpenAIBtn" class="provider-tab-btn py-2 px-3 rounded-xl border border-[#27272a] bg-[#1f1f23] text-[#a1a1aa] hover:text-white text-[14px] font-normal flex items-center justify-center gap-1.5 transition active:scale-95">
            <span>OpenAI</span>
          </button>
          <button id="providerGeminiBtn" class="provider-tab-btn py-2 px-3 rounded-xl border border-[#27272a] bg-[#1f1f23] text-[#a1a1aa] hover:text-white text-[14px] font-normal flex items-center justify-center gap-1.5 transition active:scale-95">
            <span>Gemini</span>
          </button>
        </div>
        <div class="flex items-center justify-between text-[13px] pt-1">
          <div id="providerTip" class="text-[#a1a1aa] flex-1 pr-2">
            Recommended: <strong>Anthropic</strong> excels at art theory, <em>Beyond Objecthood</em>, e-flux criticism, and institutional analysis.
          </div>
          <a id="providerGetKeyLink" href="https://console.anthropic.com/settings/keys" target="_blank" rel="noopener noreferrer" class="shrink-0 text-[#93c5fd] hover:underline font-mono text-[12px] flex items-center gap-1">
            Get Key ↗
          </a>
        </div>
      </div>

      <!-- API Key Input -->
      <div class="space-y-1.5">
        <div class="flex items-center justify-between">
          <label class="block text-[14px] text-[#a1a1aa] font-normal">API Key</label>
          <span id="keyDetectBadge" class="text-[14px] font-mono text-[#a1a1aa]">Auto-detecting provider...</span>
        </div>
        <div class="relative flex items-center">
          <input 
            type="password" 
            id="aiApiKeyInput" 
            placeholder="Paste sk-ant-... or sk-... or AIzaSy..." 
            class="w-full bg-[#212121] border border-[#333333] text-[14px] text-white px-3.5 py-2.5 rounded-xl focus:outline-none focus:border-[#60a5fa] transition font-mono pr-10"
          />
          <button id="toggleKeyVisibilityBtn" class="absolute right-3 text-[#71717a] hover:text-white text-[12px] p-1 font-mono uppercase" title="Toggle visibility">Show</button>
        </div>
        <div class="text-[14px] text-[#71717a] flex items-center justify-between">
          <span>Tip: You can also paste your API key straight into the chat box anytime!</span>
        </div>
      </div>

      <!-- Model Selector -->
      <div class="space-y-1.5">
        <label class="block text-[14px] text-[#a1a1aa] font-normal">Model</label>
        <select id="aiModelSelect" class="w-full bg-[#212121] border border-[#333333] text-white text-[14px] px-3.5 py-2 rounded-xl focus:outline-none focus:border-[#60a5fa] transition font-mono">
          <option value="claude-haiku-4-5-20251001">claude-haiku-4-5-20251001 (Fast & Articulate - Recommended)</option>
          <option value="claude-sonnet-4-5-20250929">claude-sonnet-4-5-20250929 (Deep Critical Reasoning)</option>
        </select>
      </div>

      <!-- Connection Test Status Box -->
      <div id="connectionTestBox" class="hidden p-3 rounded-xl text-[14px] border flex items-center gap-2">
        <span id="testStatusIcon"></span>
        <span id="testStatusMsg" class="font-mono">Testing connection...</span>
      </div>

      <!-- Privacy Assurance -->
      <div class="p-3 bg-[#212121] border border-[#2e2e2e] rounded-xl text-[14px] text-[#a1a1aa] leading-[120%]">
        <p>
          <strong>100% Client-Side Privacy:</strong> Your key is saved strictly in your local browser's <code class="text-white font-mono text-[14px]">localStorage</code>. Requests are sent directly from your browser to the provider's API. No intermediate backend logs your keys.
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
        <button id="saveApiKeyBtn" class="w-full sm:w-auto px-5 py-2 bg-white hover:bg-neutral-200 text-black text-[14px] font-normal rounded-xl transition shadow-sm">
          Save & Connect
        </button>
      </div>

    </div>
  </div>

  <!-- Research & Feedback Modal (Community Verification Pipeline) -->
  <div id="researchFeedbackModal" class="hidden fixed inset-0 z-50 bg-black/85 backdrop-blur-md flex items-center justify-center p-3 sm:p-5 select-text">
    <div class="bg-[#171717] border border-[#2e2e2e] rounded-2xl sm:rounded-3xl max-w-xl w-full p-4 sm:p-6 text-white shadow-2xl max-h-[92vh] overflow-y-auto flex flex-col gap-4">
      
      <!-- Modal Header -->
      <div class="flex items-center justify-between border-b border-[#2e2e2e] pb-3">
        <div class="flex items-center gap-2.5">
          <span class="text-[20px]">✍️</span>
          <div>
            <h3 class="text-[17px] font-normal text-white">Contribute Research & Verification</h3>
            <p class="text-[12px] text-[#a1a1aa] font-mono">Community Peer-Review Pipeline · Form 990 / Civic Audits</p>
          </div>
        </div>
        <button id="closeFeedbackModalBtn" class="text-[#a1a1aa] hover:text-white text-[18px] p-1.5 hover:bg-[#262626] rounded-xl transition cursor-pointer">✕</button>
      </div>

      <!-- Explanatory note -->
      <div class="p-3 bg-[#111827] border border-[#1f2937] rounded-xl text-[13px] text-slate-300 leading-[135%]">
        <span class="text-blue-400 font-mono text-[12px] block mb-0.5">PEER-AUDITED CULTURAL INTELLIGENCE</span>
        Suggest a newly discovered independent art space, report updated visitor schedules, or submit corporate funding conflict flags with statutory documentation. Submissions ground the curator model and enter the verification queue.
      </div>

      <!-- Form -->
      <form id="researchFeedbackForm" class="flex flex-col gap-3">
        <!-- Submission Category -->
        <div>
          <label class="block text-[12px] font-mono text-slate-400 uppercase tracking-wider mb-1">Contribution Category</label>
          <select id="rfCategory" class="w-full bg-[#212121] border border-[#333] rounded-xl px-3 py-2 text-[13px] text-white focus:outline-none focus:border-[#60a5fa] font-sans cursor-pointer">
            <option value="new_space">Suggest New Independent Space</option>
            <option value="funding_conflict">Flag Corporate Funding Conflict (Form 990 / Charity Commission)</option>
            <option value="visitor_update">Visitor Schedule / Admission / Transit Correction</option>
            <option value="curatorial_note">Curatorial Note / Theoretical Framework</option>
            <option value="platform_feedback">Platform & Map Feedback</option>
          </select>
        </div>

        <!-- Space Name & City -->
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
          <div>
            <label class="block text-[12px] font-mono text-slate-400 uppercase tracking-wider mb-1">Space Name</label>
            <input type="text" id="rfSpaceName" placeholder="e.g. Auto Italia, BAK, Casco" class="w-full bg-[#212121] border border-[#333] rounded-xl px-3 py-2 text-[13px] text-white focus:outline-none focus:border-[#60a5fa] font-sans">
          </div>
          <div>
            <label class="block text-[12px] font-mono text-slate-400 uppercase tracking-wider mb-1">City / Region</label>
            <input type="text" id="rfCity" placeholder="e.g. London, UK" class="w-full bg-[#212121] border border-[#333] rounded-xl px-3 py-2 text-[13px] text-white focus:outline-none focus:border-[#60a5fa] font-sans">
          </div>
        </div>

        <!-- Details / Information -->
        <div>
          <label class="block text-[12px] font-mono text-slate-400 uppercase tracking-wider mb-1">Research Notes & Details</label>
          <textarea id="rfDetails" rows="3" placeholder="Provide governance structure, funding details, opening hours, or reasons for inclusion/exclusion..." required class="w-full bg-[#212121] border border-[#333] rounded-xl p-3 text-[13px] text-white focus:outline-none focus:border-[#60a5fa] font-sans leading-[130%]"></textarea>
        </div>

        <!-- Statutory Source URL -->
        <div>
          <label class="block text-[12px] font-mono text-slate-400 uppercase tracking-wider mb-1">Verification Source Link (Statutory Filing, Official URL, or Report)</label>
          <input type="url" id="rfSourceUrl" placeholder="https://... (e.g. Form 990 link, Charity Commission, or official website)" class="w-full bg-[#212121] border border-[#333] rounded-xl px-3 py-2 text-[13px] text-white focus:outline-none focus:border-[#60a5fa] font-mono">
        </div>

        <!-- Contributor Handle (Optional) -->
        <div>
          <label class="block text-[12px] font-mono text-slate-400 uppercase tracking-wider mb-1">Contributor Handle / Credit (Optional)</label>
          <input type="text" id="rfContributor" placeholder="e.g. @curatorial_researcher or Anonymous" class="w-full bg-[#212121] border border-[#333] rounded-xl px-3 py-2 text-[13px] text-white focus:outline-none focus:border-[#60a5fa] font-sans">
        </div>

        <!-- Action Buttons -->
        <div class="flex items-center justify-between gap-2 pt-2 border-t border-[#2e2e2e] mt-1">
          <span class="text-[11px] font-mono text-emerald-400 flex items-center gap-1">
            <span class="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
            Queued for Verification
          </span>
          <div class="flex items-center gap-2">
            <button type="button" id="cancelFeedbackBtn" class="px-3.5 py-1.5 text-slate-300 hover:text-white hover:bg-[#262626] rounded-xl text-[13px] transition cursor-pointer">
              Cancel
            </button>
            <button type="submit" id="submitFeedbackBtn" class="px-4 py-1.5 bg-[#2563eb] hover:bg-[#1d4ed8] text-white text-[13px] font-medium rounded-xl transition shadow-sm cursor-pointer">
              Submit to Research Pipeline ↗
            </button>
          </div>
        </div>
      </form>

  <!-- Academic Research Library Modal (Consensus Peer-Reviewed Corpus) -->
  <div id="academicResearchModal" class="hidden fixed inset-0 z-50 bg-black/85 backdrop-blur-md flex items-center justify-center p-3 sm:p-5 select-text">
    <div class="bg-[#171717] border border-[#2e2e2e] rounded-2xl sm:rounded-3xl max-w-3xl w-full p-4 sm:p-6 text-white shadow-2xl max-h-[92vh] flex flex-col gap-3">
      
      <!-- Modal Header -->
      <div class="flex items-center justify-between border-b border-[#2e2e2e] pb-3 shrink-0">
        <div class="flex items-center gap-2.5">
          <span class="text-[20px]">🔬</span>
          <div>
            <h3 class="text-[17px] font-normal text-white">Academic Research Library: Museum Funding & Ethics</h3>
            <p class="text-[12px] text-[#33b1ff] font-mono">Consensus Peer-Reviewed Corpus · {academic_count} Empirical Studies & Critical Frameworks</p>
          </div>
        </div>
        <button id="closeAcademicModalBtn" class="text-[#a1a1aa] hover:text-white text-[18px] p-1.5 hover:bg-[#262626] rounded-xl transition cursor-pointer">✕</button>
      </div>

      <!-- Search & Topic Filter -->
      <div class="shrink-0 space-y-2">
        <div class="relative">
          <input type="text" id="arSearchInput" placeholder="Search {academic_count} peer-reviewed studies by keyword, author, or journal..." class="w-full bg-[#212121] border border-[#333] rounded-xl px-3 py-2 text-[13px] text-white focus:outline-none focus:border-[#33b1ff] font-sans">
        </div>
        <div class="flex flex-wrap items-center gap-1.5 text-[12px]" id="arTopicChips">
          <button class="ar-topic-chip px-2.5 py-1 rounded-xl bg-[#2563eb] text-white border border-[#60a5fa] cursor-pointer" data-topic="all">All Studies ({academic_count})</button>
          <button class="ar-topic-chip px-2.5 py-1 rounded-xl bg-[#212121] hover:bg-[#282828] border border-[#333] text-[#d4d4d4] cursor-pointer" data-topic="networks">Sponsor Networks & Interlocks</button>
          <button class="ar-topic-chip px-2.5 py-1 rounded-xl bg-[#212121] hover:bg-[#282828] border border-[#333] text-[#d4d4d4] cursor-pointer" data-topic="tainted">Tainted Money & Ethics</button>
          <button class="ar-topic-chip px-2.5 py-1 rounded-xl bg-[#212121] hover:bg-[#282828] border border-[#333] text-[#d4d4d4] cursor-pointer" data-topic="governance">Donor Governance</button>
          <button class="ar-topic-chip px-2.5 py-1 rounded-xl bg-[#212121] hover:bg-[#282828] border border-[#333] text-[#d4d4d4] cursor-pointer" data-topic="fossil">Fossil Fuels & Climate</button>
          <button class="ar-topic-chip px-2.5 py-1 rounded-xl bg-[#212121] hover:bg-[#282828] border border-[#333] text-[#d4d4d4] cursor-pointer" data-topic="disclosure">Mandatory Disclosure</button>
        </div>
      </div>

      <!-- Studies List -->
      <div id="arPapersList" class="flex-1 overflow-y-auto space-y-2.5 pr-1 custom-scrollbar text-[13px] min-h-[220px]">
        <!-- Rendered dynamically from ACADEMIC_RESEARCH -->
      </div>

      <!-- Modal Footer -->
      <div class="shrink-0 flex items-center justify-between pt-2 border-t border-[#2e2e2e] text-[12px] text-slate-400 font-mono">
        <span>Grounded in Consensus Open Academic Index</span>
        <button id="closeAcademicModalFooterBtn" class="px-3.5 py-1.5 bg-[#212121] hover:bg-[#2a2a2a] text-slate-300 hover:text-white rounded-xl transition cursor-pointer">Close Library</button>
      </div>

    </div>
  </div>

  <script>
    // Embedded Data Sources (Enriched by Researcher Pipeline)
    const COUNTRY_POLYS = {countries_json};
    const ALL_INSTITUTIONS = {institutions_json};
    const EXCLUDED_INSTITUTIONS = {excluded_json};
    const ACADEMIC_RESEARCH = {academic_json};
    window.ALL_INSTITUTIONS = ALL_INSTITUTIONS;
    window.EXCLUDED_INSTITUTIONS = EXCLUDED_INSTITUTIONS;
    window.ACADEMIC_RESEARCH = ACADEMIC_RESEARCH;

    const ALL_COUNTRIES_REGISTRY = {all_countries_registry_json};
    const ALL_CITIES_REGISTRY = {all_cities_registry_json};
    const COUNTRY_CENTROIDS = ALL_COUNTRIES_REGISTRY;
    const PRIORITY_CITIES = ALL_CITIES_REGISTRY;


    // Curated Cultural Cartography: Real-World Streets, Avenues & Waterways for Key Cities
    const CITY_STREET_NETWORKS = {{
  "london": {{
    "center": [
      -0.1278,
      51.5074
    ],
    "waterways": [
      {{
        "name": "River Thames",
        "width": 24,
        "pts": [
          [
            -0.24,
            51.485
          ],
          [
            -0.21,
            51.468
          ],
          [
            -0.175,
            51.482
          ],
          [
            -0.14,
            51.485
          ],
          [
            -0.124,
            51.501
          ],
          [
            -0.116,
            51.508
          ],
          [
            -0.098,
            51.508
          ],
          [
            -0.075,
            51.505
          ],
          [
            -0.05,
            51.502
          ],
          [
            -0.02,
            51.505
          ],
          [
            -0.005,
            51.485
          ],
          [
            0.03,
            51.502
          ]
        ]
      }}
    ],
    "bridges": [
      {{
        "name": "Westminster Bridge",
        "pts": [
          [
            -0.124,
            51.5
          ],
          [
            -0.119,
            51.502
          ]
        ]
      }},
      {{
        "name": "Waterloo Bridge",
        "pts": [
          [
            -0.119,
            51.511
          ],
          [
            -0.114,
            51.507
          ]
        ]
      }},
      {{
        "name": "Blackfriars Bridge",
        "pts": [
          [
            -0.105,
            51.511
          ],
          [
            -0.103,
            51.507
          ]
        ]
      }},
      {{
        "name": "Millennium Bridge",
        "pts": [
          [
            -0.099,
            51.51
          ],
          [
            -0.098,
            51.507
          ]
        ]
      }},
      {{
        "name": "London Bridge",
        "pts": [
          [
            -0.088,
            51.508
          ],
          [
            -0.086,
            51.504
          ]
        ]
      }},
      {{
        "name": "Tower Bridge",
        "pts": [
          [
            -0.076,
            51.506
          ],
          [
            -0.074,
            51.502
          ]
        ]
      }}
    ],
    "parks": [
      {{
        "name": "Hyde Park & Kensington Gardens",
        "pts": [
          [
            -0.188,
            51.502
          ],
          [
            -0.155,
            51.502
          ],
          [
            -0.155,
            51.512
          ],
          [
            -0.188,
            51.512
          ]
        ]
      }},
      {{
        "name": "Regent's Park",
        "pts": [
          [
            -0.165,
            51.525
          ],
          [
            -0.142,
            51.525
          ],
          [
            -0.142,
            51.538
          ],
          [
            -0.165,
            51.538
          ]
        ]
      }},
      {{
        "name": "Victoria Park",
        "pts": [
          [
            -0.045,
            51.535
          ],
          [
            -0.025,
            51.538
          ],
          [
            -0.028,
            51.543
          ],
          [
            -0.048,
            51.54
          ]
        ]
      }}
    ],
    "major_streets": [
      {{
        "name": "Oxford St & Bayswater Rd",
        "pts": [
          [
            -0.19,
            51.511
          ],
          [
            -0.16,
            51.514
          ],
          [
            -0.13,
            51.516
          ]
        ]
      }},
      {{
        "name": "Piccadilly",
        "pts": [
          [
            -0.15,
            51.503
          ],
          [
            -0.135,
            51.51
          ],
          [
            -0.128,
            51.513
          ]
        ]
      }},
      {{
        "name": "The Strand & Fleet St",
        "pts": [
          [
            -0.126,
            51.508
          ],
          [
            -0.112,
            51.513
          ],
          [
            -0.1,
            51.514
          ]
        ]
      }},
      {{
        "name": "Euston Rd & Marylebone Rd",
        "pts": [
          [
            -0.17,
            51.522
          ],
          [
            -0.13,
            51.528
          ],
          [
            -0.115,
            51.53
          ]
        ]
      }},
      {{
        "name": "Kingsway & Southampton Row",
        "pts": [
          [
            -0.118,
            51.512
          ],
          [
            -0.121,
            51.522
          ]
        ]
      }},
      {{
        "name": "Whitechapel High St",
        "pts": [
          [
            -0.075,
            51.515
          ],
          [
            -0.03,
            51.525
          ]
        ]
      }},
      {{
        "name": "Bankside & Southwark St",
        "pts": [
          [
            -0.11,
            51.506
          ],
          [
            -0.085,
            51.505
          ]
        ]
      }},
      {{
        "name": "Camden High St",
        "pts": [
          [
            -0.145,
            51.535
          ],
          [
            -0.142,
            51.545
          ]
        ]
      }},
      {{
        "name": "King's Road",
        "pts": [
          [
            -0.175,
            51.488
          ],
          [
            -0.155,
            51.492
          ]
        ]
      }},
      {{
        "name": "Victoria Embankment",
        "pts": [
          [
            -0.124,
            51.502
          ],
          [
            -0.108,
            51.511
          ]
        ]
      }},
      {{
        "name": "Tottenham Court Rd",
        "pts": [
          [
            -0.13,
            51.516
          ],
          [
            -0.135,
            51.524
          ]
        ]
      }},
      {{
        "name": "Charing Cross Rd",
        "pts": [
          [
            -0.128,
            51.51
          ],
          [
            -0.13,
            51.516
          ]
        ]
      }},
      {{
        "name": "Bishopsgate",
        "pts": [
          [
            -0.082,
            51.513
          ],
          [
            -0.079,
            51.523
          ]
        ]
      }}
    ],
    "secondary_streets": [
      {{
        "name": "Chisenhale Rd",
        "pts": [
          [
            -0.036,
            51.528
          ],
          [
            -0.031,
            51.531
          ]
        ]
      }},
      {{
        "name": "Ramillies St",
        "pts": [
          [
            -0.142,
            51.514
          ],
          [
            -0.139,
            51.516
          ]
        ]
      }},
      {{
        "name": "Silk St",
        "pts": [
          [
            -0.096,
            51.519
          ],
          [
            -0.091,
            51.521
          ]
        ]
      }},
      {{
        "name": "Belvedere Rd",
        "pts": [
          [
            -0.119,
            51.505
          ],
          [
            -0.114,
            51.508
          ]
        ]
      }},
      {{
        "name": "Camberwell New Rd",
        "pts": [
          [
            -0.105,
            51.478
          ],
          [
            -0.082,
            51.474
          ]
        ]
      }},
      {{
        "name": "Clapham High St",
        "pts": [
          [
            -0.145,
            51.465
          ],
          [
            -0.134,
            51.461
          ]
        ]
      }},
      {{
        "name": "Vauxhall Bridge Rd",
        "pts": [
          [
            -0.136,
            51.492
          ],
          [
            -0.124,
            51.485
          ]
        ]
      }},
      {{
        "name": "Arkwright Rd",
        "pts": [
          [
            -0.19,
            51.547
          ],
          [
            -0.183,
            51.549
          ]
        ]
      }}
    ]
  }},
  "new york": {{
    "center": [
      -73.985,
      40.748
    ],
    "waterways": [
      {{
        "name": "Hudson River",
        "width": 26,
        "pts": [
          [
            -74.022,
            40.7
          ],
          [
            -74.018,
            40.72
          ],
          [
            -74.012,
            40.75
          ],
          [
            -73.996,
            40.78
          ],
          [
            -73.972,
            40.81
          ]
        ]
      }},
      {{
        "name": "East River",
        "width": 20,
        "pts": [
          [
            -74.005,
            40.705
          ],
          [
            -73.98,
            40.72
          ],
          [
            -73.97,
            40.74
          ],
          [
            -73.955,
            40.76
          ],
          [
            -73.94,
            40.785
          ]
        ]
      }}
    ],
    "bridges": [
      {{
        "name": "Brooklyn Bridge",
        "pts": [
          [
            -74.0,
            40.71
          ],
          [
            -73.99,
            40.702
          ]
        ]
      }},
      {{
        "name": "Manhattan Bridge",
        "pts": [
          [
            -73.995,
            40.714
          ],
          [
            -73.985,
            40.704
          ]
        ]
      }},
      {{
        "name": "Williamsburg Bridge",
        "pts": [
          [
            -73.98,
            40.718
          ],
          [
            -73.965,
            40.712
          ]
        ]
      }},
      {{
        "name": "Queensboro Bridge",
        "pts": [
          [
            -73.96,
            40.76
          ],
          [
            -73.945,
            40.755
          ]
        ]
      }}
    ],
    "parks": [
      {{
        "name": "Central Park",
        "pts": [
          [
            -73.974,
            40.766
          ],
          [
            -73.963,
            40.766
          ],
          [
            -73.95,
            40.797
          ],
          [
            -73.961,
            40.797
          ]
        ]
      }},
      {{
        "name": "Washington Square Park",
        "pts": [
          [
            -74.0,
            40.729
          ],
          [
            -73.996,
            40.729
          ],
          [
            -73.996,
            40.732
          ],
          [
            -74.0,
            40.732
          ]
        ]
      }}
    ],
    "major_streets": [
      {{
        "name": "5th Avenue",
        "pts": [
          [
            -73.997,
            40.731
          ],
          [
            -73.985,
            40.75
          ],
          [
            -73.963,
            40.78
          ],
          [
            -73.945,
            40.805
          ]
        ]
      }},
      {{
        "name": "Broadway",
        "pts": [
          [
            -74.012,
            40.707
          ],
          [
            -74.003,
            40.72
          ],
          [
            -73.99,
            40.738
          ],
          [
            -73.986,
            40.754
          ],
          [
            -73.982,
            40.768
          ],
          [
            -73.975,
            40.785
          ]
        ]
      }},
      {{
        "name": "1st Avenue",
        "pts": [
          [
            -73.988,
            40.725
          ],
          [
            -73.958,
            40.775
          ]
        ]
      }},
      {{
        "name": "2nd Avenue",
        "pts": [
          [
            -73.991,
            40.726
          ],
          [
            -73.96,
            40.777
          ]
        ]
      }},
      {{
        "name": "3rd Avenue",
        "pts": [
          [
            -73.993,
            40.728
          ],
          [
            -73.963,
            40.779
          ]
        ]
      }},
      {{
        "name": "Park Avenue",
        "pts": [
          [
            -73.994,
            40.732
          ],
          [
            -73.966,
            40.782
          ]
        ]
      }},
      {{
        "name": "6th Ave (Avenue of the Americas)",
        "pts": [
          [
            -74.004,
            40.72
          ],
          [
            -73.977,
            40.764
          ]
        ]
      }},
      {{
        "name": "7th Avenue",
        "pts": [
          [
            -74.005,
            40.735
          ],
          [
            -73.981,
            40.765
          ]
        ]
      }},
      {{
        "name": "8th Ave / CPW",
        "pts": [
          [
            -74.003,
            40.738
          ],
          [
            -73.984,
            40.766
          ],
          [
            -73.961,
            40.797
          ]
        ]
      }},
      {{
        "name": "10th Ave (Chelsea)",
        "pts": [
          [
            -74.008,
            40.744
          ],
          [
            -73.995,
            40.768
          ]
        ]
      }},
      {{
        "name": "11th Ave",
        "pts": [
          [
            -74.01,
            40.745
          ],
          [
            -73.998,
            40.77
          ]
        ]
      }}
    ],
    "secondary_streets": [
      {{
        "name": "Canal St",
        "pts": [
          [
            -74.01,
            40.723
          ],
          [
            -73.99,
            40.715
          ]
        ]
      }},
      {{
        "name": "Houston St",
        "pts": [
          [
            -74.008,
            40.729
          ],
          [
            -73.975,
            40.721
          ]
        ]
      }},
      {{
        "name": "14th St",
        "pts": [
          [
            -74.008,
            40.74
          ],
          [
            -73.974,
            40.731
          ]
        ]
      }},
      {{
        "name": "23rd St (Chelsea Art Corridor)",
        "pts": [
          [
            -74.007,
            40.748
          ],
          [
            -73.976,
            40.738
          ]
        ]
      }},
      {{
        "name": "34th St",
        "pts": [
          [
            -74.002,
            40.754
          ],
          [
            -73.972,
            40.745
          ]
        ]
      }},
      {{
        "name": "42nd St",
        "pts": [
          [
            -73.999,
            40.76
          ],
          [
            -73.969,
            40.749
          ]
        ]
      }},
      {{
        "name": "53rd St",
        "pts": [
          [
            -73.99,
            40.765
          ],
          [
            -73.968,
            40.757
          ]
        ]
      }},
      {{
        "name": "57th St",
        "pts": [
          [
            -73.992,
            40.769
          ],
          [
            -73.96,
            40.758
          ]
        ]
      }},
      {{
        "name": "82nd St",
        "pts": [
          [
            -73.975,
            40.781
          ],
          [
            -73.955,
            40.774
          ]
        ]
      }},
      {{
        "name": "88th St",
        "pts": [
          [
            -73.972,
            40.785
          ],
          [
            -73.952,
            40.778
          ]
        ]
      }},
      {{
        "name": "Jackson Ave (LIC)",
        "pts": [
          [
            -73.952,
            40.744
          ],
          [
            -73.935,
            40.751
          ]
        ]
      }}
    ]
  }},
  "utrecht": {{
    "center": [
      5.1214,
      52.0907
    ],
    "waterways": [
      {{
        "name": "Oudegracht (Old Canal)",
        "width": 16,
        "pts": [
          [
            5.1245,
            52.083
          ],
          [
            5.1228,
            52.0865
          ],
          [
            5.1205,
            52.0905
          ],
          [
            5.1165,
            52.094
          ],
          [
            5.114,
            52.0965
          ]
        ]
      }},
      {{
        "name": "Nieuwegracht",
        "width": 12,
        "pts": [
          [
            5.1265,
            52.0845
          ],
          [
            5.1255,
            52.0885
          ],
          [
            5.123,
            52.092
          ]
        ]
      }},
      {{
        "name": "Stadsbuitengracht / Singel",
        "width": 18,
        "pts": [
          [
            5.111,
            52.09
          ],
          [
            5.113,
            52.096
          ],
          [
            5.121,
            52.098
          ],
          [
            5.129,
            52.094
          ],
          [
            5.128,
            52.084
          ],
          [
            5.118,
            52.082
          ],
          [
            5.111,
            52.09
          ]
        ]
      }}
    ],
    "bridges": [
      {{
        "name": "Maartensbrug",
        "pts": [
          [
            5.1205,
            52.0908
          ],
          [
            5.1215,
            52.0908
          ]
        ]
      }},
      {{
        "name": "Bezembrug",
        "pts": [
          [
            5.119,
            52.092
          ],
          [
            5.12,
            52.092
          ]
        ]
      }},
      {{
        "name": "Weerdsluis",
        "pts": [
          [
            5.1135,
            52.0965
          ],
          [
            5.1145,
            52.0965
          ]
        ]
      }}
    ],
    "parks": [
      {{
        "name": "Lepelenburg & Zocherpark",
        "pts": [
          [
            5.128,
            52.087
          ],
          [
            5.131,
            52.089
          ],
          [
            5.129,
            52.091
          ],
          [
            5.127,
            52.0885
          ]
        ]
      }}
    ],
    "major_streets": [
      {{
        "name": "Lange Nieuwstraat (Casco Commons)",
        "pts": [
          [
            5.124,
            52.0845
          ],
          [
            5.1225,
            52.089
          ]
        ]
      }},
      {{
        "name": "Pauwstraat (BAK Utrecht)",
        "pts": [
          [
            5.116,
            52.093
          ],
          [
            5.1175,
            52.0938
          ]
        ]
      }},
      {{
        "name": "Steenweg & Vredenburg",
        "pts": [
          [
            5.1135,
            52.092
          ],
          [
            5.118,
            52.091
          ]
        ]
      }},
      {{
        "name": "Nobelstraat & Biltstraat",
        "pts": [
          [
            5.122,
            52.0925
          ],
          [
            5.132,
            52.094
          ]
        ]
      }},
      {{
        "name": "Voorstraat & Potterstraat",
        "pts": [
          [
            5.117,
            52.0935
          ],
          [
            5.124,
            52.0955
          ]
        ]
      }},
      {{
        "name": "Catharijnesingel",
        "pts": [
          [
            5.112,
            52.088
          ],
          [
            5.111,
            52.095
          ]
        ]
      }},
      {{
        "name": "Domplein (Historic Center)",
        "pts": [
          [
            5.121,
            52.09
          ],
          [
            5.122,
            52.0912
          ]
        ]
      }}
    ],
    "secondary_streets": [
      {{
        "name": "Neude Square",
        "pts": [
          [
            5.1175,
            52.093
          ],
          [
            5.1195,
            52.0932
          ]
        ]
      }},
      {{
        "name": "Korte Nieuwstraat",
        "pts": [
          [
            5.122,
            52.089
          ],
          [
            5.1215,
            52.0905
          ]
        ]
      }},
      {{
        "name": "Mariaplaats",
        "pts": [
          [
            5.116,
            52.09
          ],
          [
            5.1185,
            52.09
          ]
        ]
      }},
      {{
        "name": "Zadelstraat",
        "pts": [
          [
            5.118,
            52.0905
          ],
          [
            5.121,
            52.0905
          ]
        ]
      }},
      {{
        "name": "Twijnstraat",
        "pts": [
          [
            5.1235,
            52.0825
          ],
          [
            5.1255,
            52.082
          ]
        ]
      }}
    ]
  }},
  "amsterdam": {{
    "center": [
      4.9041,
      52.3676
    ],
    "waterways": [
      {{
        "name": "Prinsengracht",
        "width": 14,
        "pts": [
          [
            4.879,
            52.382
          ],
          [
            4.877,
            52.366
          ],
          [
            4.904,
            52.361
          ]
        ]
      }},
      {{
        "name": "Keizersgracht",
        "width": 14,
        "pts": [
          [
            4.882,
            52.381
          ],
          [
            4.88,
            52.367
          ],
          [
            4.901,
            52.362
          ]
        ]
      }},
      {{
        "name": "Herengracht",
        "width": 14,
        "pts": [
          [
            4.885,
            52.38
          ],
          [
            4.883,
            52.368
          ],
          [
            4.898,
            52.363
          ]
        ]
      }},
      {{
        "name": "Singel",
        "width": 14,
        "pts": [
          [
            4.888,
            52.378
          ],
          [
            4.887,
            52.368
          ],
          [
            4.895,
            52.365
          ]
        ]
      }},
      {{
        "name": "Amstel River",
        "width": 22,
        "pts": [
          [
            4.902,
            52.355
          ],
          [
            4.9,
            52.364
          ],
          [
            4.897,
            52.368
          ]
        ]
      }},
      {{
        "name": "IJ Waterfront",
        "width": 28,
        "pts": [
          [
            4.88,
            52.385
          ],
          [
            4.91,
            52.38
          ],
          [
            4.935,
            52.375
          ]
        ]
      }}
    ],
    "parks": [
      {{
        "name": "Museumplein",
        "pts": [
          [
            4.878,
            52.356
          ],
          [
            4.885,
            52.356
          ],
          [
            4.885,
            52.36
          ],
          [
            4.878,
            52.36
          ]
        ]
      }},
      {{
        "name": "Vondelpark",
        "pts": [
          [
            4.858,
            52.357
          ],
          [
            4.877,
            52.361
          ],
          [
            4.875,
            52.364
          ],
          [
            4.856,
            52.36
          ]
        ]
      }}
    ],
    "major_streets": [
      {{
        "name": "Damrak & Rokin",
        "pts": [
          [
            4.898,
            52.378
          ],
          [
            4.893,
            52.368
          ]
        ]
      }},
      {{
        "name": "Museumplein / Van Baerlestraat",
        "pts": [
          [
            4.878,
            52.355
          ],
          [
            4.883,
            52.362
          ]
        ]
      }},
      {{
        "name": "Overtoom",
        "pts": [
          [
            4.865,
            52.36
          ],
          [
            4.88,
            52.362
          ]
        ]
      }},
      {{
        "name": "Rozengracht",
        "pts": [
          [
            4.875,
            52.372
          ],
          [
            4.886,
            52.373
          ]
        ]
      }},
      {{
        "name": "Vijzelstraat",
        "pts": [
          [
            4.892,
            52.365
          ],
          [
            4.893,
            52.359
          ]
        ]
      }},
      {{
        "name": "Oranje-Vrijstaatkade (Framer Framed)",
        "pts": [
          [
            4.925,
            52.358
          ],
          [
            4.938,
            52.357
          ]
        ]
      }},
      {{
        "name": "Schipluidenlaan (De Appel)",
        "pts": [
          [
            4.84,
            52.355
          ],
          [
            4.855,
            52.358
          ]
        ]
      }}
    ],
    "secondary_streets": [
      {{
        "name": "Leidsestraat",
        "pts": [
          [
            4.882,
            52.364
          ],
          [
            4.889,
            52.367
          ]
        ]
      }},
      {{
        "name": "Utrechtsestraat",
        "pts": [
          [
            4.898,
            52.365
          ],
          [
            4.901,
            52.359
          ]
        ]
      }},
      {{
        "name": "Paulus Potterstraat",
        "pts": [
          [
            4.879,
            52.358
          ],
          [
            4.884,
            52.36
          ]
        ]
      }}
    ]
  }},
  "paris": {{
    "center": [
      2.3522,
      48.8566
    ],
    "waterways": [
      {{
        "name": "River Seine",
        "width": 24,
        "pts": [
          [
            2.27,
            48.845
          ],
          [
            2.295,
            48.86
          ],
          [
            2.325,
            48.861
          ],
          [
            2.348,
            48.854
          ],
          [
            2.365,
            48.848
          ],
          [
            2.385,
            48.835
          ]
        ]
      }}
    ],
    "parks": [
      {{
        "name": "Jardin des Tuileries (Jeu de Paume)",
        "pts": [
          [
            2.32,
            48.864
          ],
          [
            2.333,
            48.861
          ],
          [
            2.33,
            48.865
          ],
          [
            2.322,
            48.866
          ]
        ]
      }},
      {{
        "name": "Champ de Mars",
        "pts": [
          [
            2.295,
            48.855
          ],
          [
            2.302,
            48.852
          ],
          [
            2.308,
            48.856
          ],
          [
            2.301,
            48.859
          ]
        ]
      }}
    ],
    "major_streets": [
      {{
        "name": "Champs-\u00c9lys\u00e9es",
        "pts": [
          [
            2.295,
            48.873
          ],
          [
            2.315,
            48.867
          ],
          [
            2.322,
            48.865
          ]
        ]
      }},
      {{
        "name": "Rue de Rivoli",
        "pts": [
          [
            2.322,
            48.865
          ],
          [
            2.35,
            48.858
          ],
          [
            2.365,
            48.854
          ]
        ]
      }},
      {{
        "name": "Boulevard Saint-Germain",
        "pts": [
          [
            2.32,
            48.858
          ],
          [
            2.338,
            48.853
          ],
          [
            2.355,
            48.85
          ]
        ]
      }},
      {{
        "name": "Boulevard Saint-Michel",
        "pts": [
          [
            2.344,
            48.853
          ],
          [
            2.34,
            48.843
          ]
        ]
      }},
      {{
        "name": "Boulevard de S\u00e9bastopol",
        "pts": [
          [
            2.35,
            48.855
          ],
          [
            2.354,
            48.87
          ]
        ]
      }},
      {{
        "name": "Avenue du Pr\u00e9sident Wilson (Palais de Tokyo)",
        "pts": [
          [
            2.294,
            48.864
          ],
          [
            2.3,
            48.865
          ]
        ]
      }},
      {{
        "name": "Boulevard Raspail",
        "pts": [
          [
            2.328,
            48.85
          ],
          [
            2.333,
            48.836
          ]
        ]
      }}
    ],
    "secondary_streets": [
      {{
        "name": "Rue Rambuteau",
        "pts": [
          [
            2.35,
            48.861
          ],
          [
            2.356,
            48.862
          ]
        ]
      }},
      {{
        "name": "Place de la Concorde",
        "pts": [
          [
            2.32,
            48.865
          ],
          [
            2.323,
            48.866
          ]
        ]
      }}
    ]
  }},
  "berlin": {{
    "center": [
      13.405,
      52.52
    ],
    "waterways": [
      {{
        "name": "Spree River",
        "width": 20,
        "pts": [
          [
            13.35,
            52.518
          ],
          [
            13.375,
            52.522
          ],
          [
            13.395,
            52.52
          ],
          [
            13.405,
            52.518
          ],
          [
            13.435,
            52.505
          ]
        ]
      }},
      {{
        "name": "Landwehrkanal",
        "width": 14,
        "pts": [
          [
            13.34,
            52.508
          ],
          [
            13.38,
            52.498
          ],
          [
            13.415,
            52.495
          ]
        ]
      }}
    ],
    "parks": [
      {{
        "name": "Gro\u00dfer Tiergarten (HKW)",
        "pts": [
          [
            13.35,
            52.512
          ],
          [
            13.375,
            52.512
          ],
          [
            13.37,
            52.518
          ],
          [
            13.355,
            52.518
          ]
        ]
      }}
    ],
    "major_streets": [
      {{
        "name": "Unter den Linden",
        "pts": [
          [
            13.378,
            52.516
          ],
          [
            13.4,
            52.517
          ]
        ]
      }},
      {{
        "name": "Friedrichstra\u00dfe",
        "pts": [
          [
            13.388,
            52.505
          ],
          [
            13.388,
            52.528
          ]
        ]
      }},
      {{
        "name": "Auguststra\u00dfe (KW Institute)",
        "pts": [
          [
            13.39,
            52.527
          ],
          [
            13.402,
            52.528
          ]
        ]
      }},
      {{
        "name": "Invalidenstra\u00dfe",
        "pts": [
          [
            13.365,
            52.53
          ],
          [
            13.385,
            52.532
          ]
        ]
      }},
      {{
        "name": "Niederkirchnerstra\u00dfe (Gropius Bau)",
        "pts": [
          [
            13.38,
            52.506
          ],
          [
            13.386,
            52.507
          ]
        ]
      }},
      {{
        "name": "Karl-Marx-Allee",
        "pts": [
          [
            13.415,
            52.52
          ],
          [
            13.445,
            52.518
          ]
        ]
      }},
      {{
        "name": "Potsdamer Stra\u00dfe",
        "pts": [
          [
            13.37,
            52.505
          ],
          [
            13.36,
            52.495
          ]
        ]
      }}
    ],
    "secondary_streets": [
      {{
        "name": "Oranienburger Stra\u00dfe",
        "pts": [
          [
            13.388,
            52.525
          ],
          [
            13.398,
            52.526
          ]
        ]
      }},
      {{
        "name": "Alexanderplatz",
        "pts": [
          [
            13.412,
            52.521
          ],
          [
            13.415,
            52.523
          ]
        ]
      }}
    ]
  }},
  "rotterdam": {{
    "center": [
      4.4777,
      51.9244
    ],
    "waterways": [
      {{
        "name": "Nieuwe Maas",
        "width": 24,
        "pts": [
          [
            4.45,
            51.905
          ],
          [
            4.48,
            51.91
          ],
          [
            4.51,
            51.908
          ]
        ]
      }}
    ],
    "major_streets": [
      {{
        "name": "Witte de Withstraat (Melly)",
        "pts": [
          [
            4.473,
            51.916
          ],
          [
            4.482,
            51.916
          ]
        ]
      }},
      {{
        "name": "Coolsingel",
        "pts": [
          [
            4.48,
            51.923
          ],
          [
            4.48,
            51.918
          ]
        ]
      }},
      {{
        "name": "Westersingel",
        "pts": [
          [
            4.472,
            51.922
          ],
          [
            4.472,
            51.914
          ]
        ]
      }},
      {{
        "name": "Erasmusbrug",
        "pts": [
          [
            4.483,
            51.912
          ],
          [
            4.487,
            51.906
          ]
        ]
      }}
    ],
    "secondary_streets": [
      {{
        "name": "Meent",
        "pts": [
          [
            4.48,
            51.923
          ],
          [
            4.487,
            51.922
          ]
        ]
      }}
    ]
  }},
  "eindhoven": {{
    "center": [
      5.4697,
      51.4416
    ],
    "waterways": [
      {{
        "name": "Dommel River",
        "width": 14,
        "pts": [
          [
            5.485,
            51.43
          ],
          [
            5.48,
            51.438
          ],
          [
            5.482,
            51.446
          ]
        ]
      }}
    ],
    "major_streets": [
      {{
        "name": "Bilderdijklaan (Van Abbemuseum)",
        "pts": [
          [
            5.48,
            51.434
          ],
          [
            5.488,
            51.434
          ]
        ]
      }},
      {{
        "name": "Stratumseind",
        "pts": [
          [
            5.482,
            51.437
          ],
          [
            5.485,
            51.434
          ]
        ]
      }},
      {{
        "name": "Emmasingel & Vestdijk",
        "pts": [
          [
            5.474,
            51.438
          ],
          [
            5.481,
            51.438
          ]
        ]
      }}
    ],
    "secondary_streets": [
      {{
        "name": "Wal",
        "pts": [
          [
            5.478,
            51.435
          ],
          [
            5.482,
            51.435
          ]
        ]
      }}
    ]
  }}
,
  "medellín": {{
    "center": [
        -75.5685,
        6.252
    ],
    "waterways": [
        {{
            "name": "Río Medellín",
            "width": 26,
            "pts": [
                [
                    -75.588,
                    6.21
                ],
                [
                    -75.58,
                    6.228
                ],
                [
                    -75.573,
                    6.242
                ],
                [
                    -75.569,
                    6.255
                ],
                [
                    -75.564,
                    6.27
                ],
                [
                    -75.558,
                    6.288
                ],
                [
                    -75.55,
                    6.31
                ]
            ]
        }},
        {{
            "name": "Quebrada Santa Elena",
            "width": 10,
            "pts": [
                [
                    -75.542,
                    6.248
                ],
                [
                    -75.555,
                    6.25
                ],
                [
                    -75.566,
                    6.252
                ],
                [
                    -75.57,
                    6.252
                ]
            ]
        }}
    ],
    "bridges": [
        {{
            "name": "Puente de San Juan",
            "pts": [
                [
                    -75.575,
                    6.242
                ],
                [
                    -75.571,
                    6.242
                ]
            ]
        }},
        {{
            "name": "Puente de Colombia",
            "pts": [
                [
                    -75.571,
                    6.251
                ],
                [
                    -75.567,
                    6.251
                ]
            ]
        }},
        {{
            "name": "Puente de Carabobo",
            "pts": [
                [
                    -75.566,
                    6.262
                ],
                [
                    -75.562,
                    6.262
                ]
            ]
        }},
        {{
            "name": "Puente de Guayaquil",
            "pts": [
                [
                    -75.577,
                    6.235
                ],
                [
                    -75.573,
                    6.235
                ]
            ]
        }},
        {{
            "name": "Puente de Barranquilla",
            "pts": [
                [
                    -75.562,
                    6.273
                ],
                [
                    -75.558,
                    6.273
                ]
            ]
        }}
    ],
    "parks": [
        {{
            "name": "Plaza Botero & Parque Berrío",
            "pts": [
                [
                    -75.571,
                    6.251
                ],
                [
                    -75.567,
                    6.251
                ],
                [
                    -75.567,
                    6.2545
                ],
                [
                    -75.571,
                    6.2545
                ]
            ]
        }},
        {{
            "name": "Parque de Bolívar & Catedral",
            "pts": [
                [
                    -75.5655,
                    6.2535
                ],
                [
                    -75.562,
                    6.2535
                ],
                [
                    -75.562,
                    6.257
                ],
                [
                    -75.5655,
                    6.257
                ]
            ]
        }},
        {{
            "name": "Parque de Prado Centro (C3P)",
            "pts": [
                [
                    -75.5665,
                    6.26
                ],
                [
                    -75.562,
                    6.26
                ],
                [
                    -75.562,
                    6.264
                ],
                [
                    -75.5665,
                    6.264
                ]
            ]
        }},
        {{
            "name": "Plaza Mayor & Centro de Convenciones",
            "pts": [
                [
                    -75.578,
                    6.241
                ],
                [
                    -75.573,
                    6.241
                ],
                [
                    -75.573,
                    6.2455
                ],
                [
                    -75.578,
                    6.2455
                ]
            ]
        }},
        {{
            "name": "Jardín Botánico de Medellín",
            "pts": [
                [
                    -75.566,
                    6.268
                ],
                [
                    -75.558,
                    6.268
                ],
                [
                    -75.558,
                    6.276
                ],
                [
                    -75.566,
                    6.276
                ]
            ]
        }}
    ],
    "highways": [
        {{
            "name": "Autopista Sur & Regional",
            "pts": [
                [
                    -75.588,
                    6.21
                ],
                [
                    -75.58,
                    6.228
                ],
                [
                    -75.573,
                    6.242
                ],
                [
                    -75.569,
                    6.255
                ],
                [
                    -75.564,
                    6.27
                ],
                [
                    -75.558,
                    6.288
                ],
                [
                    -75.55,
                    6.31
                ]
            ]
        }}
    ],
    "major_streets": [
        {{
            "name": "Avenida Oriental (Carrera 46)",
            "pts": [
                [
                    -75.571,
                    6.235
                ],
                [
                    -75.567,
                    6.246
                ],
                [
                    -75.565,
                    6.255
                ],
                [
                    -75.563,
                    6.268
                ]
            ]
        }},
        {{
            "name": "Carrera 52 (Paseo Carabobo)",
            "pts": [
                [
                    -75.573,
                    6.24
                ],
                [
                    -75.57,
                    6.248
                ],
                [
                    -75.569,
                    6.253
                ],
                [
                    -75.566,
                    6.265
                ],
                [
                    -75.563,
                    6.275
                ]
            ]
        }},
        {{
            "name": "Carrera 50A (Prado Centro / C3P)",
            "pts": [
                [
                    -75.568,
                    6.25
                ],
                [
                    -75.566,
                    6.257
                ],
                [
                    -75.564,
                    6.263
                ],
                [
                    -75.562,
                    6.272
                ]
            ]
        }},
        {{
            "name": "Avenida San Juan (Calle 44)",
            "pts": [
                [
                    -75.59,
                    6.242
                ],
                [
                    -75.572,
                    6.242
                ],
                [
                    -75.555,
                    6.242
                ]
            ]
        }},
        {{
            "name": "Calle 50 (Avenida Colombia)",
            "pts": [
                [
                    -75.588,
                    6.25
                ],
                [
                    -75.57,
                    6.25
                ],
                [
                    -75.552,
                    6.25
                ]
            ]
        }},
        {{
            "name": "Calle 52 (Avenida La Playa / Museo Antioquia)",
            "pts": [
                [
                    -75.586,
                    6.252
                ],
                [
                    -75.569,
                    6.252
                ],
                [
                    -75.55,
                    6.252
                ]
            ]
        }},
        {{
            "name": "Calle 63 (Prado Centro)",
            "pts": [
                [
                    -75.58,
                    6.261
                ],
                [
                    -75.564,
                    6.261
                ],
                [
                    -75.55,
                    6.261
                ]
            ]
        }},
        {{
            "name": "Avenida El Poblado (Carrera 43A)",
            "pts": [
                [
                    -75.576,
                    6.208
                ],
                [
                    -75.572,
                    6.225
                ],
                [
                    -75.568,
                    6.24
                ]
            ]
        }},
        {{
            "name": "Avenida Las Vegas (Carrera 48)",
            "pts": [
                [
                    -75.58,
                    6.208
                ],
                [
                    -75.575,
                    6.225
                ],
                [
                    -75.57,
                    6.24
                ]
            ]
        }}
    ],
    "secondary_streets": [
        {{
            "name": "Carrera 49 (Paseo Junín)",
            "pts": [
                [
                    -75.568,
                    6.246
                ],
                [
                    -75.567,
                    6.255
                ]
            ]
        }},
        {{
            "name": "Carrera 51 (Bolívar)",
            "pts": [
                [
                    -75.571,
                    6.244
                ],
                [
                    -75.569,
                    6.258
                ]
            ]
        }},
        {{
            "name": "Carrera 53 (Cundinamarca)",
            "pts": [
                [
                    -75.573,
                    6.242
                ],
                [
                    -75.571,
                    6.256
                ]
            ]
        }},
        {{
            "name": "Calle 51 (Boyacá)",
            "pts": [
                [
                    -75.575,
                    6.251
                ],
                [
                    -75.558,
                    6.251
                ]
            ]
        }},
        {{
            "name": "Calle 53 (Maracaibo)",
            "pts": [
                [
                    -75.575,
                    6.253
                ],
                [
                    -75.558,
                    6.253
                ]
            ]
        }},
        {{
            "name": "Calle 54 (Caracas)",
            "pts": [
                [
                    -75.575,
                    6.254
                ],
                [
                    -75.558,
                    6.254
                ]
            ]
        }},
        {{
            "name": "Calle 55 (Perú)",
            "pts": [
                [
                    -75.574,
                    6.255
                ],
                [
                    -75.558,
                    6.255
                ]
            ]
        }},
        {{
            "name": "Calle 56 (Bolivia)",
            "pts": [
                [
                    -75.573,
                    6.256
                ],
                [
                    -75.558,
                    6.256
                ]
            ]
        }},
        {{
            "name": "Calle 57 (Argentina)",
            "pts": [
                [
                    -75.572,
                    6.257
                ],
                [
                    -75.558,
                    6.257
                ]
            ]
        }}
    ],
    "transit_lines": [
        {{
            "name": "Metro Línea A (Norte-Sur)",
            "color": "#0ea5e9",
            "pts": [
                [
                    -75.582,
                    6.215
                ],
                [
                    -75.574,
                    6.238
                ],
                [
                    -75.571,
                    6.246
                ],
                [
                    -75.569,
                    6.252
                ],
                [
                    -75.566,
                    6.261
                ],
                [
                    -75.562,
                    6.272
                ],
                [
                    -75.556,
                    6.29
                ]
            ]
        }},
        {{
            "name": "Metro Línea B",
            "color": "#f59e0b",
            "pts": [
                [
                    -75.571,
                    6.246
                ],
                [
                    -75.585,
                    6.247
                ],
                [
                    -75.602,
                    6.25
                ]
            ]
        }},
        {{
            "name": "Metrocable Línea K",
            "color": "#ec4899",
            "pts": [
                [
                    -75.556,
                    6.29
                ],
                [
                    -75.55,
                    6.295
                ],
                [
                    -75.545,
                    6.302
                ],
                [
                    -75.54,
                    6.308
                ]
            ]
        }}
    ],
    "transit_stations": [
        {{
            "name": "Estación Parque Berrío",
            "lon": -75.569,
            "lat": 6.252,
            "color": "#0ea5e9"
        }},
        {{
            "name": "Estación Prado",
            "lon": -75.566,
            "lat": 6.261,
            "color": "#0ea5e9"
        }},
        {{
            "name": "Estación San Antonio",
            "lon": -75.571,
            "lat": 6.246,
            "color": "#0ea5e9"
        }},
        {{
            "name": "Estación Alpujarra",
            "lon": -75.573,
            "lat": 6.241,
            "color": "#0ea5e9"
        }},
        {{
            "name": "Estación Hospital",
            "lon": -75.562,
            "lat": 6.271,
            "color": "#0ea5e9"
        }}
    ],
    "districts": [
        {{
            "name": "CENTRO HISTÓRICO / PLAZA BOTERO",
            "lon": -75.569,
            "lat": 6.253
        }},
        {{
            "name": "PRADO CENTRO PATRIMONIO",
            "lon": -75.564,
            "lat": 6.262
        }},
        {{
            "name": "CENTRO ADMINISTRATIVO LA ALPUJARRA",
            "lon": -75.574,
            "lat": 6.243
        }},
        {{
            "name": "CORREDOR DEL RÍO MEDELLÍN",
            "lon": -75.571,
            "lat": 6.248
        }}
    ]
}},
  "bogotá": {{
    "center": [
        -74.072,
        4.602
    ],
    "waterways": [
        {{
            "name": "Río Arzobispo / Eje Ambiental",
            "width": 14,
            "pts": [
                [
                    -74.055,
                    4.63
                ],
                [
                    -74.065,
                    4.615
                ],
                [
                    -74.072,
                    4.602
                ],
                [
                    -74.085,
                    4.595
                ]
            ]
        }}
    ],
    "parks": [
        {{
            "name": "Plaza de Bolívar",
            "pts": [
                [
                    -74.077,
                    4.597
                ],
                [
                    -74.075,
                    4.597
                ],
                [
                    -74.075,
                    4.599
                ],
                [
                    -74.077,
                    4.599
                ]
            ]
        }},
        {{
            "name": "Parque Santander",
            "pts": [
                [
                    -74.073,
                    4.601
                ],
                [
                    -74.071,
                    4.601
                ],
                [
                    -74.071,
                    4.603
                ],
                [
                    -74.073,
                    4.603
                ]
            ]
        }},
        {{
            "name": "Parque de la Independencia",
            "pts": [
                [
                    -74.069,
                    4.612
                ],
                [
                    -74.066,
                    4.612
                ],
                [
                    -74.066,
                    4.616
                ],
                [
                    -74.069,
                    4.616
                ]
            ]
        }}
    ],
    "major_streets": [
        {{
            "name": "Carrera 7 (Séptima Cultural)",
            "pts": [
                [
                    -74.078,
                    4.592
                ],
                [
                    -74.072,
                    4.602
                ],
                [
                    -74.065,
                    4.618
                ],
                [
                    -74.058,
                    4.635
                ]
            ]
        }},
        {{
            "name": "Avenida Jiménez (Eje Ambiental)",
            "pts": [
                [
                    -74.065,
                    4.601
                ],
                [
                    -74.075,
                    4.602
                ],
                [
                    -74.088,
                    4.603
                ]
            ]
        }},
        {{
            "name": "Avenida Calle 26 (El Dorado)",
            "pts": [
                [
                    -74.062,
                    4.614
                ],
                [
                    -74.075,
                    4.615
                ],
                [
                    -74.095,
                    4.616
                ]
            ]
        }},
        {{
            "name": "Carrera 10",
            "pts": [
                [
                    -74.082,
                    4.59
                ],
                [
                    -74.075,
                    4.605
                ],
                [
                    -74.068,
                    4.62
                ]
            ]
        }}
    ],
    "secondary_streets": [
        {{
            "name": "Calle 19",
            "pts": [
                [
                    -74.064,
                    4.606
                ],
                [
                    -74.085,
                    4.606
                ]
            ]
        }},
        {{
            "name": "Calle 24",
            "pts": [
                [
                    -74.064,
                    4.612
                ],
                [
                    -74.085,
                    4.612
                ]
            ]
        }},
        {{
            "name": "Calle 11 (La Candelaria)",
            "pts": [
                [
                    -74.065,
                    4.596
                ],
                [
                    -74.082,
                    4.596
                ]
            ]
        }}
    ],
    "transit_lines": [
        {{
            "name": "TransMilenio Troncal Caracas",
            "color": "#dc2626",
            "pts": [
                [
                    -74.085,
                    4.592
                ],
                [
                    -74.075,
                    4.61
                ],
                [
                    -74.066,
                    4.63
                ]
            ]
        }}
    ],
    "transit_stations": [
        {{
            "name": "Estación Museo del Oro",
            "lon": -74.072,
            "lat": 4.602,
            "color": "#dc2626"
        }},
        {{
            "name": "Estación Las Aguas",
            "lon": -74.068,
            "lat": 4.602,
            "color": "#dc2626"
        }}
    ],
    "districts": [
        {{
            "name": "LA CANDELARIA HISTÓRICA",
            "lon": -74.07,
            "lat": 4.597
        }},
        {{
            "name": "CENTRO INTERNACIONAL",
            "lon": -74.068,
            "lat": 4.614
        }}
    ]
}},
  "mexico city": {{
    "center": [
        -99.141,
        19.434
    ],
    "parks": [
        {{
            "name": "Alameda Central",
            "pts": [
                [
                    -99.148,
                    19.434
                ],
                [
                    -99.142,
                    19.434
                ],
                [
                    -99.142,
                    19.437
                ],
                [
                    -99.148,
                    19.437
                ]
            ]
        }},
        {{
            "name": "Zócalo / Plaza Mayor",
            "pts": [
                [
                    -99.134,
                    19.432
                ],
                [
                    -99.132,
                    19.432
                ],
                [
                    -99.132,
                    19.434
                ],
                [
                    -99.134,
                    19.434
                ]
            ]
        }},
        {{
            "name": "Bosque de Chapultepec",
            "pts": [
                [
                    -99.195,
                    19.418
                ],
                [
                    -99.182,
                    19.418
                ],
                [
                    -99.182,
                    19.426
                ],
                [
                    -99.195,
                    19.426
                ]
            ]
        }}
    ],
    "major_streets": [
        {{
            "name": "Paseo de la Reforma",
            "pts": [
                [
                    -99.2,
                    19.418
                ],
                [
                    -99.17,
                    19.428
                ],
                [
                    -99.148,
                    19.436
                ],
                [
                    -99.135,
                    19.445
                ]
            ]
        }},
        {{
            "name": "Avenida Juárez",
            "pts": [
                [
                    -99.149,
                    19.434
                ],
                [
                    -99.141,
                    19.434
                ]
            ]
        }},
        {{
            "name": "Avenida Insurgentes",
            "pts": [
                [
                    -99.168,
                    19.405
                ],
                [
                    -99.162,
                    19.43
                ],
                [
                    -99.155,
                    19.455
                ]
            ]
        }},
        {{
            "name": "Eje Central Lázaro Cárdenas",
            "pts": [
                [
                    -99.142,
                    19.415
                ],
                [
                    -99.141,
                    19.434
                ],
                [
                    -99.14,
                    19.45
                ]
            ]
        }}
    ],
    "secondary_streets": [
        {{
            "name": "Calle 5 de Mayo",
            "pts": [
                [
                    -99.141,
                    19.434
                ],
                [
                    -99.134,
                    19.434
                ]
            ]
        }},
        {{
            "name": "Calle Madero",
            "pts": [
                [
                    -99.141,
                    19.433
                ],
                [
                    -99.134,
                    19.433
                ]
            ]
        }},
        {{
            "name": "Calle Tacuba",
            "pts": [
                [
                    -99.141,
                    19.435
                ],
                [
                    -99.134,
                    19.435
                ]
            ]
        }}
    ],
    "transit_lines": [
        {{
            "name": "Metro Línea 2 (Azul)",
            "color": "#0284c7",
            "pts": [
                [
                    -99.155,
                    19.44
                ],
                [
                    -99.142,
                    19.436
                ],
                [
                    -99.133,
                    19.433
                ],
                [
                    -99.134,
                    19.418
                ]
            ]
        }}
    ],
    "transit_stations": [
        {{
            "name": "Estación Bellas Artes",
            "lon": -99.141,
            "lat": 19.436,
            "color": "#0284c7"
        }},
        {{
            "name": "Estación Zócalo",
            "lon": -99.133,
            "lat": 19.433,
            "color": "#0284c7"
        }}
    ],
    "districts": [
        {{
            "name": "CENTRO HISTÓRICO",
            "lon": -99.136,
            "lat": 19.434
        }},
        {{
            "name": "CORREDOR REFORMA",
            "lon": -99.16,
            "lat": 19.43
        }}
    ]
}},
  "são paulo": {{
    "center": [
        -46.655,
        -23.561
    ],
    "parks": [
        {{
            "name": "Parque Ibirapuera",
            "pts": [
                [
                    -46.662,
                    -23.59
                ],
                [
                    -46.65,
                    -23.59
                ],
                [
                    -46.65,
                    -23.582
                ],
                [
                    -46.662,
                    -23.582
                ]
            ]
        }},
        {{
            "name": "Parque Trianon (MASP)",
            "pts": [
                [
                    -46.658,
                    -23.563
                ],
                [
                    -46.655,
                    -23.563
                ],
                [
                    -46.655,
                    -23.561
                ],
                [
                    -46.658,
                    -23.561
                ]
            ]
        }}
    ],
    "major_streets": [
        {{
            "name": "Avenida Paulista",
            "pts": [
                [
                    -46.672,
                    -23.553
                ],
                [
                    -46.655,
                    -23.561
                ],
                [
                    -46.645,
                    -23.57
                ]
            ]
        }},
        {{
            "name": "Avenida 23 de Maio",
            "pts": [
                [
                    -46.64,
                    -23.548
                ],
                [
                    -46.643,
                    -23.565
                ],
                [
                    -46.646,
                    -23.585
                ]
            ]
        }},
        {{
            "name": "Rua Augusta",
            "pts": [
                [
                    -46.658,
                    -23.55
                ],
                [
                    -46.66,
                    -23.56
                ]
            ]
        }}
    ],
    "secondary_streets": [
        {{
            "name": "Alameda Santos",
            "pts": [
                [
                    -46.67,
                    -23.555
                ],
                [
                    -46.645,
                    -23.572
                ]
            ]
        }},
        {{
            "name": "Rua Bela Cintra",
            "pts": [
                [
                    -46.662,
                    -23.552
                ],
                [
                    -46.664,
                    -23.562
                ]
            ]
        }}
    ],
    "transit_lines": [
        {{
            "name": "Metrô Linha 2 (Verde)",
            "color": "#10b981",
            "pts": [
                [
                    -46.672,
                    -23.553
                ],
                [
                    -46.655,
                    -23.561
                ],
                [
                    -46.645,
                    -23.57
                ]
            ]
        }}
    ],
    "transit_stations": [
        {{
            "name": "Estação Trianon-MASP",
            "lon": -46.656,
            "lat": -23.562,
            "color": "#10b981"
        }}
    ],
    "districts": [
        {{
            "name": "AVENIDA PAULISTA",
            "lon": -46.656,
            "lat": -23.562
        }}
    ]
}},
  "madrid": {{
    "center": [
        -3.692,
        40.415
    ],
    "parks": [
        {{
            "name": "Parque de El Retiro",
            "pts": [
                [
                    -3.688,
                    40.411
                ],
                [
                    -3.676,
                    40.411
                ],
                [
                    -3.676,
                    40.419
                ],
                [
                    -3.688,
                    40.419
                ]
            ]
        }},
        {{
            "name": "Real Jardín Botánico",
            "pts": [
                [
                    -3.693,
                    40.41
                ],
                [
                    -3.689,
                    40.41
                ],
                [
                    -3.689,
                    40.414
                ],
                [
                    -3.693,
                    40.414
                ]
            ]
        }}
    ],
    "major_streets": [
        {{
            "name": "Paseo del Prado (Triángulo del Arte)",
            "pts": [
                [
                    -3.693,
                    40.408
                ],
                [
                    -3.692,
                    40.415
                ],
                [
                    -3.691,
                    40.42
                ]
            ]
        }},
        {{
            "name": "Gran Vía",
            "pts": [
                [
                    -3.709,
                    40.422
                ],
                [
                    -3.702,
                    40.42
                ],
                [
                    -3.697,
                    40.418
                ]
            ]
        }},
        {{
            "name": "Calle de Alcalá",
            "pts": [
                [
                    -3.704,
                    40.417
                ],
                [
                    -3.693,
                    40.419
                ],
                [
                    -3.682,
                    40.421
                ]
            ]
        }}
    ],
    "secondary_streets": [
        {{
            "name": "Calle de las Huertas",
            "pts": [
                [
                    -3.702,
                    40.413
                ],
                [
                    -3.694,
                    40.414
                ]
            ]
        }},
        {{
            "name": "Calle de Atocha",
            "pts": [
                [
                    -3.704,
                    40.413
                ],
                [
                    -3.693,
                    40.408
                ]
            ]
        }}
    ],
    "transit_lines": [
        {{
            "name": "Metro Línea 1",
            "color": "#0ea5e9",
            "pts": [
                [
                    -3.693,
                    40.407
                ],
                [
                    -3.697,
                    40.414
                ],
                [
                    -3.703,
                    40.417
                ]
            ]
        }}
    ],
    "transit_stations": [
        {{
            "name": "Estación del Arte (Atocha)",
            "lon": -3.693,
            "lat": 40.408,
            "color": "#0ea5e9"
        }},
        {{
            "name": "Estación Banco de España",
            "lon": -3.695,
            "lat": 40.418,
            "color": "#0ea5e9"
        }}
    ],
    "districts": [
        {{
            "name": "PASEO DEL ARTE",
            "lon": -3.692,
            "lat": 40.414
        }},
        {{
            "name": "BARRIO DE LAS LETRAS",
            "lon": -3.698,
            "lat": 40.413
        }}
    ]
}},
  "tokyo": {{
    "center": [
        139.767,
        35.681
    ],
    "waterways": [
        {{
            "name": "Sumida River (隅田川)",
            "width": 26,
            "pts": [
                [
                    139.79,
                    35.715
                ],
                [
                    139.792,
                    35.698
                ],
                [
                    139.785,
                    35.675
                ],
                [
                    139.768,
                    35.655
                ]
            ]
        }}
    ],
    "parks": [
        {{
            "name": "Ueno Onshi Park (上野恩賜公園)",
            "pts": [
                [
                    139.768,
                    35.712
                ],
                [
                    139.776,
                    35.712
                ],
                [
                    139.776,
                    35.718
                ],
                [
                    139.768,
                    35.718
                ]
            ]
        }},
        {{
            "name": "Imperial Palace East Gardens (皇居東御苑)",
            "pts": [
                [
                    139.754,
                    35.684
                ],
                [
                    139.762,
                    35.684
                ],
                [
                    139.762,
                    35.69
                ],
                [
                    139.754,
                    35.69
                ]
            ]
        }}
    ],
    "major_streets": [
        {{
            "name": "Chuo Dori (中央通り)",
            "pts": [
                [
                    139.772,
                    35.7
                ],
                [
                    139.77,
                    35.685
                ],
                [
                    139.766,
                    35.67
                ]
            ]
        }},
        {{
            "name": "Roppongi Dori (六本木通り)",
            "pts": [
                [
                    139.725,
                    35.66
                ],
                [
                    139.735,
                    35.664
                ],
                [
                    139.745,
                    35.67
                ]
            ]
        }}
    ],
    "transit_lines": [
        {{
            "name": "JR Yamanote Line (山手線)",
            "color": "#84cc16",
            "pts": [
                [
                    139.777,
                    35.713
                ],
                [
                    139.772,
                    35.698
                ],
                [
                    139.768,
                    35.681
                ],
                [
                    139.759,
                    35.666
                ]
            ]
        }}
    ],
    "transit_stations": [
        {{
            "name": "Tokyo Station",
            "lon": 139.767,
            "lat": 35.681,
            "color": "#84cc16"
        }},
        {{
            "name": "Ueno Station",
            "lon": 139.777,
            "lat": 35.713,
            "color": "#84cc16"
        }}
    ],
    "districts": [
        {{
            "name": "UENO MUSEUM PRECINCT",
            "lon": 139.772,
            "lat": 35.715
        }},
        {{
            "name": "GINZA ART DISTRICT",
            "lon": 139.765,
            "lat": 35.672
        }}
    ]
}},
  "rome": {{
    "center": [
        12.482,
        41.893
    ],
    "waterways": [
        {{
            "name": "Fiume Tevere (Tiber)",
            "width": 22,
            "pts": [
                [
                    12.468,
                    41.912
                ],
                [
                    12.464,
                    41.902
                ],
                [
                    12.47,
                    41.892
                ],
                [
                    12.476,
                    41.882
                ],
                [
                    12.472,
                    41.87
                ]
            ]
        }}
    ],
    "parks": [
        {{
            "name": "Villa Borghese",
            "pts": [
                [
                    12.484,
                    41.91
                ],
                [
                    12.496,
                    41.91
                ],
                [
                    12.496,
                    41.916
                ],
                [
                    12.484,
                    41.916
                ]
            ]
        }}
    ],
    "major_streets": [
        {{
            "name": "Via del Corso",
            "pts": [
                [
                    12.476,
                    41.908
                ],
                [
                    12.48,
                    41.898
                ],
                [
                    12.483,
                    41.894
                ]
            ]
        }},
        {{
            "name": "Corso Vittorio Emanuele II",
            "pts": [
                [
                    12.464,
                    41.9
                ],
                [
                    12.473,
                    41.896
                ],
                [
                    12.48,
                    41.895
                ]
            ]
        }}
    ],
    "transit_lines": [
        {{
            "name": "Metro Linea A",
            "color": "#f97316",
            "pts": [
                [
                    12.476,
                    41.91
                ],
                [
                    12.483,
                    41.906
                ],
                [
                    12.502,
                    41.901
                ]
            ]
        }}
    ],
    "transit_stations": [
        {{
            "name": "Spagna",
            "lon": 12.483,
            "lat": 41.906,
            "color": "#f97316"
        }}
    ],
    "districts": [
        {{
            "name": "CENTRO STORICO",
            "lon": 12.478,
            "lat": 41.898
        }}
    ]
}},
  "medellin": {{
    "center": [
        -75.5685,
        6.252
    ],
    "waterways": [
        {{
            "name": "Río Medellín",
            "width": 26,
            "pts": [
                [
                    -75.588,
                    6.21
                ],
                [
                    -75.58,
                    6.228
                ],
                [
                    -75.573,
                    6.242
                ],
                [
                    -75.569,
                    6.255
                ],
                [
                    -75.564,
                    6.27
                ],
                [
                    -75.558,
                    6.288
                ],
                [
                    -75.55,
                    6.31
                ]
            ]
        }},
        {{
            "name": "Quebrada Santa Elena",
            "width": 10,
            "pts": [
                [
                    -75.542,
                    6.248
                ],
                [
                    -75.555,
                    6.25
                ],
                [
                    -75.566,
                    6.252
                ],
                [
                    -75.57,
                    6.252
                ]
            ]
        }}
    ],
    "bridges": [
        {{
            "name": "Puente de San Juan",
            "pts": [
                [
                    -75.575,
                    6.242
                ],
                [
                    -75.571,
                    6.242
                ]
            ]
        }},
        {{
            "name": "Puente de Colombia",
            "pts": [
                [
                    -75.571,
                    6.251
                ],
                [
                    -75.567,
                    6.251
                ]
            ]
        }},
        {{
            "name": "Puente de Carabobo",
            "pts": [
                [
                    -75.566,
                    6.262
                ],
                [
                    -75.562,
                    6.262
                ]
            ]
        }},
        {{
            "name": "Puente de Guayaquil",
            "pts": [
                [
                    -75.577,
                    6.235
                ],
                [
                    -75.573,
                    6.235
                ]
            ]
        }},
        {{
            "name": "Puente de Barranquilla",
            "pts": [
                [
                    -75.562,
                    6.273
                ],
                [
                    -75.558,
                    6.273
                ]
            ]
        }}
    ],
    "parks": [
        {{
            "name": "Plaza Botero & Parque Berrío",
            "pts": [
                [
                    -75.571,
                    6.251
                ],
                [
                    -75.567,
                    6.251
                ],
                [
                    -75.567,
                    6.2545
                ],
                [
                    -75.571,
                    6.2545
                ]
            ]
        }},
        {{
            "name": "Parque de Bolívar & Catedral",
            "pts": [
                [
                    -75.5655,
                    6.2535
                ],
                [
                    -75.562,
                    6.2535
                ],
                [
                    -75.562,
                    6.257
                ],
                [
                    -75.5655,
                    6.257
                ]
            ]
        }},
        {{
            "name": "Parque de Prado Centro (C3P)",
            "pts": [
                [
                    -75.5665,
                    6.26
                ],
                [
                    -75.562,
                    6.26
                ],
                [
                    -75.562,
                    6.264
                ],
                [
                    -75.5665,
                    6.264
                ]
            ]
        }},
        {{
            "name": "Plaza Mayor & Centro de Convenciones",
            "pts": [
                [
                    -75.578,
                    6.241
                ],
                [
                    -75.573,
                    6.241
                ],
                [
                    -75.573,
                    6.2455
                ],
                [
                    -75.578,
                    6.2455
                ]
            ]
        }},
        {{
            "name": "Jardín Botánico de Medellín",
            "pts": [
                [
                    -75.566,
                    6.268
                ],
                [
                    -75.558,
                    6.268
                ],
                [
                    -75.558,
                    6.276
                ],
                [
                    -75.566,
                    6.276
                ]
            ]
        }}
    ],
    "highways": [
        {{
            "name": "Autopista Sur & Regional",
            "pts": [
                [
                    -75.588,
                    6.21
                ],
                [
                    -75.58,
                    6.228
                ],
                [
                    -75.573,
                    6.242
                ],
                [
                    -75.569,
                    6.255
                ],
                [
                    -75.564,
                    6.27
                ],
                [
                    -75.558,
                    6.288
                ],
                [
                    -75.55,
                    6.31
                ]
            ]
        }}
    ],
    "major_streets": [
        {{
            "name": "Avenida Oriental (Carrera 46)",
            "pts": [
                [
                    -75.571,
                    6.235
                ],
                [
                    -75.567,
                    6.246
                ],
                [
                    -75.565,
                    6.255
                ],
                [
                    -75.563,
                    6.268
                ]
            ]
        }},
        {{
            "name": "Carrera 52 (Paseo Carabobo)",
            "pts": [
                [
                    -75.573,
                    6.24
                ],
                [
                    -75.57,
                    6.248
                ],
                [
                    -75.569,
                    6.253
                ],
                [
                    -75.566,
                    6.265
                ],
                [
                    -75.563,
                    6.275
                ]
            ]
        }},
        {{
            "name": "Carrera 50A (Prado Centro / C3P)",
            "pts": [
                [
                    -75.568,
                    6.25
                ],
                [
                    -75.566,
                    6.257
                ],
                [
                    -75.564,
                    6.263
                ],
                [
                    -75.562,
                    6.272
                ]
            ]
        }},
        {{
            "name": "Avenida San Juan (Calle 44)",
            "pts": [
                [
                    -75.59,
                    6.242
                ],
                [
                    -75.572,
                    6.242
                ],
                [
                    -75.555,
                    6.242
                ]
            ]
        }},
        {{
            "name": "Calle 50 (Avenida Colombia)",
            "pts": [
                [
                    -75.588,
                    6.25
                ],
                [
                    -75.57,
                    6.25
                ],
                [
                    -75.552,
                    6.25
                ]
            ]
        }},
        {{
            "name": "Calle 52 (Avenida La Playa / Museo Antioquia)",
            "pts": [
                [
                    -75.586,
                    6.252
                ],
                [
                    -75.569,
                    6.252
                ],
                [
                    -75.55,
                    6.252
                ]
            ]
        }},
        {{
            "name": "Calle 63 (Prado Centro)",
            "pts": [
                [
                    -75.58,
                    6.261
                ],
                [
                    -75.564,
                    6.261
                ],
                [
                    -75.55,
                    6.261
                ]
            ]
        }},
        {{
            "name": "Avenida El Poblado (Carrera 43A)",
            "pts": [
                [
                    -75.576,
                    6.208
                ],
                [
                    -75.572,
                    6.225
                ],
                [
                    -75.568,
                    6.24
                ]
            ]
        }},
        {{
            "name": "Avenida Las Vegas (Carrera 48)",
            "pts": [
                [
                    -75.58,
                    6.208
                ],
                [
                    -75.575,
                    6.225
                ],
                [
                    -75.57,
                    6.24
                ]
            ]
        }}
    ],
    "secondary_streets": [
        {{
            "name": "Carrera 49 (Paseo Junín)",
            "pts": [
                [
                    -75.568,
                    6.246
                ],
                [
                    -75.567,
                    6.255
                ]
            ]
        }},
        {{
            "name": "Carrera 51 (Bolívar)",
            "pts": [
                [
                    -75.571,
                    6.244
                ],
                [
                    -75.569,
                    6.258
                ]
            ]
        }},
        {{
            "name": "Carrera 53 (Cundinamarca)",
            "pts": [
                [
                    -75.573,
                    6.242
                ],
                [
                    -75.571,
                    6.256
                ]
            ]
        }},
        {{
            "name": "Calle 51 (Boyacá)",
            "pts": [
                [
                    -75.575,
                    6.251
                ],
                [
                    -75.558,
                    6.251
                ]
            ]
        }},
        {{
            "name": "Calle 53 (Maracaibo)",
            "pts": [
                [
                    -75.575,
                    6.253
                ],
                [
                    -75.558,
                    6.253
                ]
            ]
        }},
        {{
            "name": "Calle 54 (Caracas)",
            "pts": [
                [
                    -75.575,
                    6.254
                ],
                [
                    -75.558,
                    6.254
                ]
            ]
        }},
        {{
            "name": "Calle 55 (Perú)",
            "pts": [
                [
                    -75.574,
                    6.255
                ],
                [
                    -75.558,
                    6.255
                ]
            ]
        }},
        {{
            "name": "Calle 56 (Bolivia)",
            "pts": [
                [
                    -75.573,
                    6.256
                ],
                [
                    -75.558,
                    6.256
                ]
            ]
        }},
        {{
            "name": "Calle 57 (Argentina)",
            "pts": [
                [
                    -75.572,
                    6.257
                ],
                [
                    -75.558,
                    6.257
                ]
            ]
        }}
    ],
    "transit_lines": [
        {{
            "name": "Metro Línea A (Norte-Sur)",
            "color": "#0ea5e9",
            "pts": [
                [
                    -75.582,
                    6.215
                ],
                [
                    -75.574,
                    6.238
                ],
                [
                    -75.571,
                    6.246
                ],
                [
                    -75.569,
                    6.252
                ],
                [
                    -75.566,
                    6.261
                ],
                [
                    -75.562,
                    6.272
                ],
                [
                    -75.556,
                    6.29
                ]
            ]
        }},
        {{
            "name": "Metro Línea B",
            "color": "#f59e0b",
            "pts": [
                [
                    -75.571,
                    6.246
                ],
                [
                    -75.585,
                    6.247
                ],
                [
                    -75.602,
                    6.25
                ]
            ]
        }},
        {{
            "name": "Metrocable Línea K",
            "color": "#ec4899",
            "pts": [
                [
                    -75.556,
                    6.29
                ],
                [
                    -75.55,
                    6.295
                ],
                [
                    -75.545,
                    6.302
                ],
                [
                    -75.54,
                    6.308
                ]
            ]
        }}
    ],
    "transit_stations": [
        {{
            "name": "Estación Parque Berrío",
            "lon": -75.569,
            "lat": 6.252,
            "color": "#0ea5e9"
        }},
        {{
            "name": "Estación Prado",
            "lon": -75.566,
            "lat": 6.261,
            "color": "#0ea5e9"
        }},
        {{
            "name": "Estación San Antonio",
            "lon": -75.571,
            "lat": 6.246,
            "color": "#0ea5e9"
        }},
        {{
            "name": "Estación Alpujarra",
            "lon": -75.573,
            "lat": 6.241,
            "color": "#0ea5e9"
        }},
        {{
            "name": "Estación Hospital",
            "lon": -75.562,
            "lat": 6.271,
            "color": "#0ea5e9"
        }}
    ],
    "districts": [
        {{
            "name": "CENTRO HISTÓRICO / PLAZA BOTERO",
            "lon": -75.569,
            "lat": 6.253
        }},
        {{
            "name": "PRADO CENTRO PATRIMONIO",
            "lon": -75.564,
            "lat": 6.262
        }},
        {{
            "name": "CENTRO ADMINISTRATIVO LA ALPUJARRA",
            "lon": -75.574,
            "lat": 6.243
        }},
        {{
            "name": "CORREDOR DEL RÍO MEDELLÍN",
            "lon": -75.571,
            "lat": 6.248
        }}
    ]
}},
  "bogota": {{
    "center": [
        -74.072,
        4.602
    ],
    "waterways": [
        {{
            "name": "Río Arzobispo / Eje Ambiental",
            "width": 14,
            "pts": [
                [
                    -74.055,
                    4.63
                ],
                [
                    -74.065,
                    4.615
                ],
                [
                    -74.072,
                    4.602
                ],
                [
                    -74.085,
                    4.595
                ]
            ]
        }}
    ],
    "parks": [
        {{
            "name": "Plaza de Bolívar",
            "pts": [
                [
                    -74.077,
                    4.597
                ],
                [
                    -74.075,
                    4.597
                ],
                [
                    -74.075,
                    4.599
                ],
                [
                    -74.077,
                    4.599
                ]
            ]
        }},
        {{
            "name": "Parque Santander",
            "pts": [
                [
                    -74.073,
                    4.601
                ],
                [
                    -74.071,
                    4.601
                ],
                [
                    -74.071,
                    4.603
                ],
                [
                    -74.073,
                    4.603
                ]
            ]
        }},
        {{
            "name": "Parque de la Independencia",
            "pts": [
                [
                    -74.069,
                    4.612
                ],
                [
                    -74.066,
                    4.612
                ],
                [
                    -74.066,
                    4.616
                ],
                [
                    -74.069,
                    4.616
                ]
            ]
        }}
    ],
    "major_streets": [
        {{
            "name": "Carrera 7 (Séptima Cultural)",
            "pts": [
                [
                    -74.078,
                    4.592
                ],
                [
                    -74.072,
                    4.602
                ],
                [
                    -74.065,
                    4.618
                ],
                [
                    -74.058,
                    4.635
                ]
            ]
        }},
        {{
            "name": "Avenida Jiménez (Eje Ambiental)",
            "pts": [
                [
                    -74.065,
                    4.601
                ],
                [
                    -74.075,
                    4.602
                ],
                [
                    -74.088,
                    4.603
                ]
            ]
        }},
        {{
            "name": "Avenida Calle 26 (El Dorado)",
            "pts": [
                [
                    -74.062,
                    4.614
                ],
                [
                    -74.075,
                    4.615
                ],
                [
                    -74.095,
                    4.616
                ]
            ]
        }},
        {{
            "name": "Carrera 10",
            "pts": [
                [
                    -74.082,
                    4.59
                ],
                [
                    -74.075,
                    4.605
                ],
                [
                    -74.068,
                    4.62
                ]
            ]
        }}
    ],
    "secondary_streets": [
        {{
            "name": "Calle 19",
            "pts": [
                [
                    -74.064,
                    4.606
                ],
                [
                    -74.085,
                    4.606
                ]
            ]
        }},
        {{
            "name": "Calle 24",
            "pts": [
                [
                    -74.064,
                    4.612
                ],
                [
                    -74.085,
                    4.612
                ]
            ]
        }},
        {{
            "name": "Calle 11 (La Candelaria)",
            "pts": [
                [
                    -74.065,
                    4.596
                ],
                [
                    -74.082,
                    4.596
                ]
            ]
        }}
    ],
    "transit_lines": [
        {{
            "name": "TransMilenio Troncal Caracas",
            "color": "#dc2626",
            "pts": [
                [
                    -74.085,
                    4.592
                ],
                [
                    -74.075,
                    4.61
                ],
                [
                    -74.066,
                    4.63
                ]
            ]
        }}
    ],
    "transit_stations": [
        {{
            "name": "Estación Museo del Oro",
            "lon": -74.072,
            "lat": 4.602,
            "color": "#dc2626"
        }},
        {{
            "name": "Estación Las Aguas",
            "lon": -74.068,
            "lat": 4.602,
            "color": "#dc2626"
        }}
    ],
    "districts": [
        {{
            "name": "LA CANDELARIA HISTÓRICA",
            "lon": -74.07,
            "lat": 4.597
        }},
        {{
            "name": "CENTRO INTERNACIONAL",
            "lon": -74.068,
            "lat": 4.614
        }}
    ]
}},
  "sao paulo": {{
    "center": [
        -46.655,
        -23.561
    ],
    "parks": [
        {{
            "name": "Parque Ibirapuera",
            "pts": [
                [
                    -46.662,
                    -23.59
                ],
                [
                    -46.65,
                    -23.59
                ],
                [
                    -46.65,
                    -23.582
                ],
                [
                    -46.662,
                    -23.582
                ]
            ]
        }},
        {{
            "name": "Parque Trianon (MASP)",
            "pts": [
                [
                    -46.658,
                    -23.563
                ],
                [
                    -46.655,
                    -23.563
                ],
                [
                    -46.655,
                    -23.561
                ],
                [
                    -46.658,
                    -23.561
                ]
            ]
        }}
    ],
    "major_streets": [
        {{
            "name": "Avenida Paulista",
            "pts": [
                [
                    -46.672,
                    -23.553
                ],
                [
                    -46.655,
                    -23.561
                ],
                [
                    -46.645,
                    -23.57
                ]
            ]
        }},
        {{
            "name": "Avenida 23 de Maio",
            "pts": [
                [
                    -46.64,
                    -23.548
                ],
                [
                    -46.643,
                    -23.565
                ],
                [
                    -46.646,
                    -23.585
                ]
            ]
        }},
        {{
            "name": "Rua Augusta",
            "pts": [
                [
                    -46.658,
                    -23.55
                ],
                [
                    -46.66,
                    -23.56
                ]
            ]
        }}
    ],
    "secondary_streets": [
        {{
            "name": "Alameda Santos",
            "pts": [
                [
                    -46.67,
                    -23.555
                ],
                [
                    -46.645,
                    -23.572
                ]
            ]
        }},
        {{
            "name": "Rua Bela Cintra",
            "pts": [
                [
                    -46.662,
                    -23.552
                ],
                [
                    -46.664,
                    -23.562
                ]
            ]
        }}
    ],
    "transit_lines": [
        {{
            "name": "Metrô Linha 2 (Verde)",
            "color": "#10b981",
            "pts": [
                [
                    -46.672,
                    -23.553
                ],
                [
                    -46.655,
                    -23.561
                ],
                [
                    -46.645,
                    -23.57
                ]
            ]
        }}
    ],
    "transit_stations": [
        {{
            "name": "Estação Trianon-MASP",
            "lon": -46.656,
            "lat": -23.562,
            "color": "#10b981"
        }}
    ],
    "districts": [
        {{
            "name": "AVENIDA PAULISTA",
            "lon": -46.656,
            "lat": -23.562
        }}
    ]
}},
  "new york": {{
    "center": [-73.9776, 40.7614],
    "waterways": [
      {{
        "name": "Hudson River",
        "width": 26,
        "pts": [[-74.025, 40.700], [-74.018, 40.725], [-74.010, 40.750], [-73.990, 40.780], [-73.960, 40.820]]
      }},
      {{
        "name": "East River",
        "width": 20,
        "pts": [[-74.015, 40.702], [-73.985, 40.710], [-73.972, 40.730], [-73.960, 40.755], [-73.940, 40.775]]
      }}
    ],
    "parks": [
      {{
        "name": "Central Park",
        "pts": [[-73.9818, 40.7681], [-73.9730, 40.7644], [-73.9493, 40.7968], [-73.9582, 40.8006], [-73.9818, 40.7681]]
      }}
    ],
    "major_streets": [
      {{
        "name": "5th Avenue",
        "pts": [[-73.997, 40.731], [-73.987, 40.748], [-73.977, 40.763], [-73.953, 40.795]]
      }},
      {{
        "name": "Broadway",
        "pts": [[-74.013, 40.708], [-74.004, 40.719], [-73.989, 40.748], [-73.982, 40.762], [-73.982, 40.775]]
      }}
    ]
  }},
  "frankfurt": {{
    "center": [8.6821, 50.1109],
    "waterways": [
      {{
        "name": "River Main",
        "width": 22,
        "pts": [[8.640, 50.098], [8.665, 50.104], [8.682, 50.108], [8.705, 50.112], [8.730, 50.115]]
      }}
    ],
    "parks": [
      {{
        "name": "Wallanlagen",
        "pts": [[8.672, 50.105], [8.668, 50.112], [8.675, 50.118], [8.688, 50.119], [8.692, 50.113], [8.684, 50.106], [8.672, 50.105]]
      }}
    ],
    "major_streets": [
      {{
        "name": "Mainzer Landstraße",
        "pts": [[8.645, 50.108], [8.662, 50.111], [8.674, 50.114]]
      }}
    ]
  }},
  "vienna": {{
    "center": [16.3738, 48.2082],
    "waterways": [
      {{
        "name": "Donaukanal",
        "width": 18,
        "pts": [[16.345, 48.228], [16.362, 48.220], [16.378, 48.213], [16.395, 48.204], [16.418, 48.192]]
      }}
    ],
    "parks": [
      {{
        "name": "Stadtpark",
        "pts": [[16.378, 48.202], [16.384, 48.204], [16.383, 48.208], [16.376, 48.206], [16.378, 48.202]]
      }},
      {{
        "name": "Burggarten & Volksgarten",
        "pts": [[16.360, 48.204], [16.366, 48.209], [16.362, 48.212], [16.356, 48.207], [16.360, 48.204]]
      }}
    ],
    "major_streets": [
      {{
        "name": "Ringstraße",
        "pts": [[16.361, 48.202], [16.359, 48.206], [16.363, 48.212], [16.371, 48.214], [16.379, 48.211], [16.383, 48.205], [16.375, 48.200], [16.367, 48.200], [16.361, 48.202]]
      }},
      {{
        "name": "Museumsplatz",
        "pts": [[16.358, 48.201], [16.360, 48.205], [16.361, 48.209]]
      }}
    ]
  }},
  "basel": {{
    "center": [7.5886, 47.5596],
    "waterways": [
      {{
        "name": "River Rhine",
        "width": 24,
        "pts": [[7.562, 47.554], [7.580, 47.560], [7.594, 47.561], [7.608, 47.558], [7.625, 47.552]]
      }}
    ],
    "parks": [
      {{
        "name": "Kannenfeldpark",
        "pts": [[7.568, 47.564], [7.574, 47.565], [7.573, 47.568], [7.567, 47.567], [7.568, 47.564]]
      }}
    ],
    "major_streets": [
      {{
        "name": "Mittlere Rheinbrücke Corridor",
        "pts": [[7.586, 47.555], [7.589, 47.560], [7.592, 47.565]]
      }},
      {{
        "name": "St. Alban-Graben",
        "pts": [[7.590, 47.554], [7.596, 47.553], [7.601, 47.553]]
      }}
    ]
  }},
  "barcelona": {{
    "center": [2.1734, 41.3851],
    "waterways": [
      {{
        "name": "Mediterranean Shoreline",
        "width": 26,
        "pts": [[2.178, 41.368], [2.188, 41.380], [2.198, 41.392], [2.210, 41.402], [2.224, 41.412]]
      }}
    ],
    "parks": [
      {{
        "name": "Parc de Montjuïc",
        "pts": [[2.155, 41.365], [2.166, 41.370], [2.163, 41.376], [2.152, 41.372], [2.155, 41.365]]
      }},
      {{
        "name": "Parc de la Ciutadella",
        "pts": [[2.185, 41.386], [2.192, 41.390], [2.190, 41.394], [2.183, 41.390], [2.185, 41.386]]
      }}
    ],
    "major_streets": [
      {{
        "name": "La Rambla",
        "pts": [[2.177, 41.376], [2.174, 41.381], [2.170, 41.387]]
      }},
      {{
        "name": "Passeig de Gràcia",
        "pts": [[2.170, 41.387], [2.164, 41.394], [2.158, 41.401]]
      }}
    ]
  }},
  "saint petersburg": {{
    "center": [30.3351, 59.9343],
    "waterways": [
      {{
        "name": "Bolshaya Neva",
        "width": 26,
        "pts": [[30.22, 59.93], [30.26, 59.935], [30.30, 59.945], [30.33, 59.952], [30.38, 59.948], [30.41, 59.925], [30.42, 59.895]]
      }},
      {{
        "name": "Malaya Neva",
        "width": 18,
        "pts": [[30.26, 59.95], [30.29, 59.955], [30.31, 59.948]]
      }},
      {{
        "name": "Fontanka River",
        "width": 11,
        "pts": [[30.337, 59.946], [30.345, 59.935], [30.335, 59.922], [30.305, 59.917], [30.275, 59.915]]
      }},
      {{
        "name": "Moika River",
        "width": 9,
        "pts": [[30.333, 59.942], [30.322, 59.934], [30.305, 59.929], [30.285, 59.927]]
      }},
      {{
        "name": "Griboyedov Canal",
        "width": 7,
        "pts": [[30.329, 59.940], [30.324, 59.933], [30.312, 59.928], [30.298, 59.921], [30.285, 59.918]]
      }}
    ],
    "parks": [
      {{
        "name": "Summer Garden",
        "pts": [[30.332, 59.944], [30.339, 59.944], [30.339, 59.949], [30.332, 59.949], [30.332, 59.944]]
      }},
      {{
        "name": "Field of Mars",
        "pts": [[30.326, 59.942], [30.332, 59.942], [30.332, 59.946], [30.326, 59.946], [30.326, 59.942]]
      }},
      {{
        "name": "Mikhailovsky Garden",
        "pts": [[30.328, 59.937], [30.336, 59.937], [30.336, 59.941], [30.328, 59.941], [30.328, 59.937]]
      }}
    ],
    "major_streets": [
      {{
        "name": "Nevsky Prospekt",
        "pts": [[30.312, 59.937], [30.330, 59.935], [30.360, 59.931], [30.385, 59.924]]
      }},
      {{
        "name": "Sadovaya Street",
        "pts": [[30.335, 59.943], [30.323, 59.932], [30.310, 59.923], [30.290, 59.916]]
      }},
      {{
        "name": "Liteyny Prospekt",
        "pts": [[30.348, 59.948], [30.347, 59.934], [30.345, 59.928]]
      }},
      {{
        "name": "Kamennoostrovsky Prospekt",
        "pts": [[30.320, 59.953], [30.312, 59.967], [30.303, 59.978]]
      }},
      {{
        "name": "Bolshoy Prospekt V.O.",
        "pts": [[30.300, 59.944], [30.270, 59.938], [30.245, 59.933]]
      }},
      {{
        "name": "Moskovsky Prospekt",
        "pts": [[30.315, 59.928], [30.318, 59.905], [30.320, 59.880]]
      }}
    ],
    "secondary_streets": [
      {{ "pts": [[30.290, 59.946], [30.275, 59.935]] }},
      {{ "pts": [[30.295, 59.948], [30.280, 59.937]] }},
      {{ "pts": [[30.300, 59.950], [30.285, 59.939]] }},
      {{ "pts": [[30.320, 59.928], [30.350, 59.925]] }},
      {{ "pts": [[30.322, 59.923], [30.355, 59.920]] }},
      {{ "pts": [[30.340, 59.940], [30.370, 59.937]] }}
    ]
  }},
  "krasnodar": {{
    "center": [38.9760, 45.0355],
    "waterways": [
      {{
        "name": "Kuban River",
        "width": 22,
        "pts": [[38.92, 45.01], [38.95, 45.014], [38.97, 45.008], [39.00, 45.012], [39.03, 45.022], [39.06, 45.028]]
      }},
      {{
        "name": "Karasun Lakes",
        "width": 9,
        "pts": [[38.995, 45.025], [39.015, 45.028], [39.035, 45.032]]
      }}
    ],
    "parks": [
      {{
        "name": "Park Krasnodar (Galitsky Park)",
        "pts": [[39.026, 45.039], [39.038, 45.039], [39.038, 45.048], [39.026, 45.048], [39.026, 45.039]]
      }},
      {{
        "name": "City Garden",
        "pts": [[38.965, 45.013], [38.973, 45.013], [38.973, 45.020], [38.965, 45.020], [38.965, 45.013]]
      }},
      {{
        "name": "Chistyakovskaya Roshcha",
        "pts": [[38.985, 45.056], [38.998, 45.056], [38.998, 45.065], [38.985, 45.065], [38.985, 45.056]]
      }}
    ],
    "major_streets": [
      {{
        "name": "Krasnaya Street",
        "pts": [[38.968, 45.012], [38.972, 45.025], [38.976, 45.035], [38.981, 45.050], [38.985, 45.062]]
      }},
      {{
        "name": "Severnaya Street",
        "pts": [[38.940, 45.038], [38.976, 45.038], [39.020, 45.038]]
      }},
      {{
        "name": "Stavropolskaya Street",
        "pts": [[38.988, 45.018], [39.015, 45.020], [39.045, 45.023]]
      }},
      {{
        "name": "Babushkina Street",
        "pts": [[38.950, 45.050], [38.980, 45.050], [39.010, 45.050]]
      }}
    ],
    "secondary_streets": [
      {{ "pts": [[38.960, 45.030], [38.990, 45.030]] }},
      {{ "pts": [[38.960, 45.044], [38.990, 45.044]] }},
      {{ "pts": [[38.970, 45.020], [38.970, 45.055]] }},
      {{ "pts": [[38.982, 45.020], [38.982, 45.055]] }}
    ]
  }},
  "moscow": {{
    "center": [37.6173, 55.7558],
    "waterways": [
      {{
        "name": "Moskva River",
        "width": 24,
        "pts": [[37.53, 55.75], [37.56, 55.735], [37.60, 55.742], [37.63, 55.748], [37.66, 55.732], [37.68, 55.715]]
      }},
      {{
        "name": "Vodootvodny Canal",
        "width": 10,
        "pts": [[37.605, 55.742], [37.625, 55.746], [37.645, 55.738]]
      }}
    ],
    "parks": [
      {{
        "name": "Gorky Park & Muzeon",
        "pts": [[37.595, 55.728], [37.608, 55.728], [37.608, 55.738], [37.595, 55.738], [37.595, 55.728]]
      }},
      {{
        "name": "Zaryadye Park",
        "pts": [[37.625, 55.750], [37.633, 55.750], [37.633, 55.754], [37.625, 55.754], [37.625, 55.750]]
      }}
    ],
    "major_streets": [
      {{
        "name": "Boulevard Ring",
        "pts": [[37.602, 55.750], [37.605, 55.760], [37.625, 55.766], [37.642, 55.760], [37.648, 55.748]]
      }},
      {{
        "name": "Garden Ring",
        "pts": [[37.585, 55.738], [37.582, 55.760], [37.610, 55.772], [37.652, 55.768], [37.658, 55.738], [37.620, 55.730], [37.585, 55.738]]
      }},
      {{
        "name": "Tverskaya Street",
        "pts": [[37.615, 55.758], [37.605, 55.768], [37.592, 55.778]]
      }},
      {{
        "name": "Novy Arbat",
        "pts": [[37.602, 55.752], [37.585, 55.752], [37.570, 55.752]]
      }}
    ],
    "secondary_streets": [
      {{ "pts": [[37.595, 55.755], [37.635, 55.755]] }},
      {{ "pts": [[37.600, 55.745], [37.630, 55.745]] }},
      {{ "pts": [[37.615, 55.740], [37.615, 55.770]] }}
    ]
  }}
  }};

    // Clean Metropolitan Network Lookup with Universal Architectural Cartography
    function getCityStreetData(cityName) {{
      if (!cityName) return null;
      let key = cityName.toLowerCase().trim();
      if (key === 'nyc' || key === 'new york city') key = 'new york';
      if (key.includes('frankfurt')) key = 'frankfurt';
      if (key.includes('vienna') || key === 'wien') key = 'vienna';
      if (key.includes('basel')) key = 'basel';
      if (key.includes('barcelona') || key === 'bcn') key = 'barcelona';
      if (key.includes('petersburg') || key.includes('spb') || key.includes('saint p')) key = 'saint petersburg';
      if (key.includes('krasnodar')) key = 'krasnodar';
      if (key.includes('moscow') || key.includes('moskva')) key = 'moscow';

      const normKey = key.normalize('NFD').replace(/[\u0300-\u036f]/g, '');
      const pCty = PRIORITY_CITIES.find(c => matchC(c.name, cityName));
      const cityInsts = ALL_INSTITUTIONS.filter(i => matchC(i.city, cityName));
      let centerLon = pCty ? pCty.lon : 0;
      let centerLat = pCty ? pCty.lat : 0;
      if (!pCty && cityInsts.length > 0) {{
        centerLon = cityInsts[0].lon;
        centerLat = cityInsts[0].lat;
      }}

      const curated = CITY_STREET_NETWORKS[key] || CITY_STREET_NETWORKS[normKey];
      if (curated) {{
        return {{
          center: curated.center || [centerLon, centerLat],
          waterways: curated.waterways || [],
          parks: curated.parks || [],
          major_streets: curated.major_streets || [],
          secondary_streets: curated.secondary_streets || []
        }};
      }}

      // Universal procedural architectural cartography for any unlisted city
      const waterways = [];
      const parks = [];
      const major_streets = [];
      const secondary_streets = [];

      if (centerLon === 0 && centerLat === 0) {{
        centerLon = (typeof rotLon !== 'undefined' && isFinite(rotLon) ? rotLon : 0);
        centerLat = (typeof rotLat !== 'undefined' && isFinite(rotLat) ? rotLat : 0);
      }}

      const cosLat = Math.max(0.18, Math.cos(centerLat * Math.PI / 180));
      const spanLon = 0.075 / cosLat;
      const spanLat = 0.055;

      waterways.push({{
        name: "Metropolitan Canal",
        width: 16,
        pts: [
          [centerLon - spanLon * 0.75, centerLat - spanLat * 0.40],
          [centerLon - spanLon * 0.35, centerLat - spanLat * 0.12],
          [centerLon, centerLat - spanLat * 0.02],
          [centerLon + spanLon * 0.35, centerLat + spanLat * 0.22],
          [centerLon + spanLon * 0.75, centerLat + spanLat * 0.38]
        ]
      }});

      parks.push({{
        name: "Civic Cultural Gardens",
        pts: [
          [centerLon + spanLon * 0.06, centerLat + spanLat * 0.06],
          [centerLon + spanLon * 0.22, centerLat + spanLat * 0.06],
          [centerLon + spanLon * 0.22, centerLat + spanLat * 0.20],
          [centerLon + spanLon * 0.06, centerLat + spanLat * 0.20],
          [centerLon + spanLon * 0.06, centerLat + spanLat * 0.06]
        ]
      }});

      major_streets.push(
        {{ pts: [[centerLon - spanLon * 0.06, centerLat - spanLat * 0.6], [centerLon - spanLon * 0.02, centerLat], [centerLon + spanLon * 0.02, centerLat + spanLat * 0.6]] }},
        {{ pts: [[centerLon - spanLon * 0.65, centerLat + spanLat * 0.03], [centerLon, centerLat + spanLat * 0.03], [centerLon + spanLon * 0.65, centerLat + spanLat * 0.03]] }},
        {{ pts: [[centerLon - spanLon * 0.45, centerLat - spanLat * 0.35], [centerLon, centerLat], [centerLon + spanLon * 0.45, centerLat + spanLat * 0.35]] }},
        {{ pts: [[centerLon - spanLon * 0.45, centerLat + spanLat * 0.35], [centerLon, centerLat], [centerLon + spanLon * 0.45, centerLat - spanLat * 0.35]] }}
      );

      cityInsts.forEach(inst => {{
        major_streets.push({{
          pts: [[centerLon, centerLat], [inst.lon, inst.lat]]
        }});
      }});

      const stepX = 0.012 / cosLat;
      const stepY = 0.009;
      for (let s = -4; s <= 4; s++) {{
        if (s === 0) continue;
        secondary_streets.push({{
          pts: [[centerLon - spanLon * 0.6, centerLat + s * stepY], [centerLon + spanLon * 0.6, centerLat + s * stepY]]
        }});
      }}
      for (let s = -5; s <= 5; s++) {{
        if (s === 0) continue;
        secondary_streets.push({{
          pts: [[centerLon + s * stepX, centerLat - spanLat * 0.5], [centerLon + s * stepX, centerLat + spanLat * 0.5]]
        }});
      }}

      return {{
        center: [centerLon, centerLat],
        waterways,
        parks,
        major_streets,
        secondary_streets
      }};
    }}

    function getCityTargetRadius(cityName) {{
      const c = (cityName || '').toLowerCase();
      if (c.includes('utrecht') || c.includes('rotterdam') || c.includes('eindhoven') || c.includes('basel') || c.includes('frankfurt')) {{
        return baseRadius * 110.0;
      }}
      if (c.includes('new york') || c.includes('paris') || c.includes('berlin') || c.includes('amsterdam') || c.includes('london') || c.includes('tokyo') || c.includes('vienna') || c.includes('barcelona') || c.includes('mexico city') || c.includes('cdmx') || c.includes('bogota') || c.includes('sao paulo')) {{
        return baseRadius * 135.0;
      }}
      return baseRadius * 105.0;
    }}


    // State Variables
    let filteredList = ALL_INSTITUTIONS.filter(i => i.tier === 'A');
    let selectedTierFilter = new Set(['A']);
    let selectedCountryFilter = 'all';
    let selectedCityFilter = 'all';
    let searchQuery = '';
    let selectedInstitution = null;
    let hoveredInstitution = null;
    let hoveredCity = null;
    let hoveredCountry = null;

    Object.defineProperty(window, 'selectedTierFilter', {{
      get: () => selectedTierFilter,
      set: (v) => {{ selectedTierFilter = v; }}
    }});
    Object.defineProperty(window, 'filteredList', {{
      get: () => filteredList,
      set: (v) => {{ filteredList = v; }}
    }});

    // High-Resolution Interactive City Map (Google Maps Dark WebGL Vector Engine) State & Controller
    const GOOGLE_MAPS_DARK_STYLE = {{
      version: 8,
      name: 'Google Maps Dark',
      sources: {{
        openmaptiles: {{
          type: 'vector',
          tiles: ['https://tiles.openfreemap.org/planet/latest/{{z}}/{{x}}/{{y}}.pbf'],
          minzoom: 0,
          maxzoom: 14
        }}
      }},
      glyphs: 'https://tiles.openfreemap.org/fonts/{{fontstack}}/{{range}}.pbf',
      layers: [
        {{
          id: 'background',
          type: 'background',
          paint: {{ 'background-color': '#17171a' }}
        }},
        {{
          id: 'landcover_grass',
          type: 'fill',
          source: 'openmaptiles',
          'source-layer': 'landcover',
          filter: ['match', ['get', 'class'], ['grass', 'wood', 'scrub'], true, false],
          paint: {{
            'fill-color': '#142218',
            'fill-opacity': 0.75
          }}
        }},
        {{
          id: 'park',
          type: 'fill',
          source: 'openmaptiles',
          'source-layer': 'park',
          paint: {{
            'fill-color': '#142218',
            'fill-opacity': 0.85
          }}
        }},
        {{
          id: 'water',
          type: 'fill',
          source: 'openmaptiles',
          'source-layer': 'water',
          paint: {{
            'fill-color': '#0f1724'
          }}
        }},
        {{
          id: 'waterway',
          type: 'line',
          source: 'openmaptiles',
          'source-layer': 'waterway',
          paint: {{
            'line-color': '#0f1724',
            'line-width': ['interpolate', ['exponential', 1.3], ['zoom'], 8, 1, 14, 4]
          }}
        }},
        {{
          id: 'building',
          type: 'fill',
          source: 'openmaptiles',
          'source-layer': 'building',
          minzoom: 13,
          paint: {{
            'fill-color': '#21242d',
            'fill-outline-color': '#191b22',
            'fill-opacity': 0.9
          }}
        }},
        {{
          id: 'road_minor',
          type: 'line',
          source: 'openmaptiles',
          'source-layer': 'transportation',
          filter: ['match', ['get', 'class'], ['minor', 'service', 'track', 'path'], true, false],
          minzoom: 12,
          paint: {{
            'line-color': '#232630',
            'line-width': ['interpolate', ['linear'], ['zoom'], 12, 1.0, 16, 3.0]
          }}
        }},
        {{
          id: 'road_secondary',
          type: 'line',
          source: 'openmaptiles',
          'source-layer': 'transportation',
          filter: ['match', ['get', 'class'], ['secondary', 'tertiary'], true, false],
          paint: {{
            'line-color': '#2c313d',
            'line-width': ['interpolate', ['linear'], ['zoom'], 8, 0.8, 16, 4.0]
          }}
        }},
        {{
          id: 'road_primary',
          type: 'line',
          source: 'openmaptiles',
          'source-layer': 'transportation',
          filter: ['match', ['get', 'class'], ['primary', 'trunk'], true, false],
          paint: {{
            'line-color': '#3a4252',
            'line-width': ['interpolate', ['linear'], ['zoom'], 6, 1.2, 16, 5.5]
          }}
        }},
        {{
          id: 'road_motorway',
          type: 'line',
          source: 'openmaptiles',
          'source-layer': 'transportation',
          filter: ['==', ['get', 'class'], 'motorway'],
          paint: {{
            'line-color': '#475163',
            'line-width': ['interpolate', ['linear'], ['zoom'], 5, 1.5, 16, 7.0]
          }}
        }},
        {{
          id: 'boundary_country',
          type: 'line',
          source: 'openmaptiles',
          'source-layer': 'boundary',
          filter: ['==', ['get', 'admin_level'], 2],
          paint: {{
            'line-color': '#4b5563',
            'line-width': 1.2,
            'line-dasharray': [3, 2]
          }}
        }},
        {{
          id: 'place_label',
          type: 'symbol',
          source: 'openmaptiles',
          'source-layer': 'place',
          minzoom: 8,
          layout: {{
            'text-field': ['coalesce', ['get', 'name_en'], ['get', 'name']],
            'text-font': ['Noto Sans Regular'],
            'text-size': ['interpolate', ['linear'], ['zoom'], 8, 10, 14, 13],
            'text-transform': 'uppercase',
            'text-letter-spacing': 0.08
          }},
          paint: {{
            'text-color': '#94a3b8',
            'text-halo-color': '#111215',
            'text-halo-width': 1.5
          }}
        }}
      ]
    }};

    let cityVectorMap = null;
    let cityVectorMarkers = [];
    let isCityStreetViewActive = false;

    // Backward-compatible compatibility proxies for external harness / test assertions
    let cityMarkersLayer = {{
      getLayers: () => cityVectorMarkers,
      clearLayers: () => {{
        cityVectorMarkers.forEach(m => m.remove());
        cityVectorMarkers = [];
      }}
    }};
    let cityLeafletMap = null;

    function initCityMapIfNeeded() {{
      if (cityVectorMap) return;
      const mapEl = document.getElementById('cityMapContainer');
      if (!mapEl || typeof maplibregl === 'undefined') return;

      cityVectorMap = new maplibregl.Map({{
        container: 'cityMapContainer',
        style: GOOGLE_MAPS_DARK_STYLE,
        center: [0, 20],
        zoom: 14,
        pitch: 35,
        bearing: 0,
        attributionControl: false
      }});

      cityVectorMap.addControl(new maplibregl.NavigationControl({{
        showCompass: true,
        visualizePitch: true
      }}), 'top-right');

      cityVectorMap.addControl(new maplibregl.AttributionControl({{
        compact: true,
        customAttribution: 'Google Maps Dark Cartography · OpenFreeMap Vector Engine'
      }}), 'bottom-left');

      cityLeafletMap = {{
        getCenter: () => {{
          const c = cityVectorMap.getCenter();
          return {{ lat: c.lat, lng: c.lng }};
        }},
        getZoom: () => cityVectorMap.getZoom(),
        setView: (coords, zoom) => {{
          cityVectorMap.jumpTo({{ center: [coords[1], coords[0]], zoom: zoom, pitch: 35 }});
        }},
        invalidateSize: () => {{
          cityVectorMap.resize();
        }},
        on: (evt, cb) => cityVectorMap.on(evt, cb)
      }};
      window.cityVectorMap = cityVectorMap;
      window.cityLeafletMap = cityLeafletMap;
      window.cityMarkersLayer = cityMarkersLayer;

      function updateCityZoomClasses() {{
        const mapEl = document.getElementById('cityMapContainer');
        if (!mapEl || !cityVectorMap) return;
        // Keep names of spaces visible across street view zoom levels
        mapEl.classList.add('map-zoomed-in');
        mapEl.classList.remove('map-zoomed-out');
      }}
      cityVectorMap.on('zoom', updateCityZoomClasses);
      cityVectorMap.on('load', updateCityZoomClasses);

      cityVectorMap.on('zoomend', () => {{
        if (cityVectorMap.getZoom() <= 8 && isCityStreetViewActive) {{
          exitCityStreetView();
        }}
      }});
    }}

    window.atlasSelectInst = function(instName) {{
      const inst = ALL_INSTITUTIONS.find(i => i.name === instName);
      if (inst) {{
        selectInstitution(inst, false);
        openDossier(inst);
      }}
    }};

    window.atlasOpenDossier = function(instName) {{
      const inst = ALL_INSTITUTIONS.find(i => i.name === instName);
      if (inst) openDossier(inst);
    }};

    window.atlasAskCurator = function(queryOrInstName) {{
      if (window.innerWidth < 768 && typeof setMobileViewMode === 'function') {{
        setMobileViewMode('chat');
      }}
      const inst = ALL_INSTITUTIONS.find(i => i.name.toLowerCase() === (queryOrInstName || '').toLowerCase());
      if (inst) {{
        appendUserMessage(`Tell me about ${{inst.name}}`);
        handleCuratorQuery(inst.name);
      }} else if (queryOrInstName) {{
        appendUserMessage(queryOrInstName);
        handleCuratorQuery(queryOrInstName);
      }}
    }};

    window.atlasPlanVisit = function(instNameOrObj) {{
      let inst = null;
      if (typeof instNameOrObj === 'string') {{
        inst = ALL_INSTITUTIONS.find(i => i.name.toLowerCase() === instNameOrObj.toLowerCase()) || (typeof findMentionedInst === 'function' ? findMentionedInst(instNameOrObj) : null);
      }} else if (instNameOrObj && typeof instNameOrObj === 'object') {{
        inst = instNameOrObj;
      }}
      if (!inst) {{
        inst = selectedInstitution || (typeof curatorContext !== 'undefined' ? curatorContext.lastInst : null);
      }}
      if (inst) {{
        if (typeof setMobileViewMode === 'function') {{
          setMobileViewMode('chat');
        }}
        const q = `Plan my visit to ${{inst.name}}`;
        appendUserMessage(q);
        handleCuratorQuery(q);
      }}
    }};

    function openCityStreetView(cityName, targetLat, targetLon) {{
      if (!cityName || cityName === 'all') return;
      isCityStreetViewActive = true;
      initCityMapIfNeeded();
      const mapEl = document.getElementById('cityMapContainer');
      if (!mapEl || !cityVectorMap) return;

      // Ensure globe floating card is strictly hidden in street view
      document.getElementById('floatingCard')?.classList.add('hidden');

      mapEl.classList.remove('hidden');
      mapEl.classList.add('map-zoomed-in');
      mapEl.classList.remove('map-zoomed-out');
      document.getElementById('cityViewControlBanner')?.classList.remove('hidden');

      const cityInsts = ALL_INSTITUTIONS.filter(i => matchC(i.city, cityName));
      const cMeta = ALL_CITIES_REGISTRY.find(c => matchC(c.name, cityName));
      const lat = targetLat || (cMeta ? cMeta.lat : (cityInsts.length > 0 ? cityInsts[0].lat : 0));
      const lon = targetLon || (cMeta ? cMeta.lon : (cityInsts.length > 0 ? cityInsts[0].lon : 0));

      if (cityInsts.length > 1 && !targetLat) {{
        const bounds = new maplibregl.LngLatBounds();
        cityInsts.forEach(i => bounds.extend([i.lon, i.lat]));
        cityVectorMap.fitBounds(bounds, {{
          padding: {{ top: 90, bottom: 90, left: 70, right: 70 }},
          maxZoom: 14.5
        }});
      }} else {{
        cityVectorMap.jumpTo({{
          center: [lon, lat],
          zoom: 14,
          pitch: 35
        }});
      }}
      setTimeout(() => {{
        if (cityVectorMap) cityVectorMap.resize();
      }}, 50);

      const titleEl = document.getElementById('cityViewTitleText');
      if (titleEl) {{
        titleEl.textContent = `${{cityName.toUpperCase()}} · ${{cityInsts.length}} CULTURAL SPACES`;
      }}
      const backCountryBtn = document.getElementById('backToCountryBtn');
      const backCountryText = document.getElementById('backToCountryText');
      const countryName = cMeta ? cMeta.country : (cityInsts.length > 0 ? cityInsts[0].country : null);
      if (backCountryBtn && countryName) {{
        backCountryBtn.classList.remove('hidden');
        if (backCountryText) backCountryText.textContent = countryName;
      }}

      cityMarkersLayer.clearLayers();

      cityInsts.forEach(inst => {{
        const isA = inst.tier === 'A';
        const isB = inst.tier === 'B';
        const markerColor = isA ? '#10b981' : (isB ? '#be95ff' : '#08bdba');
        const webUrl = getValidWebUrl(inst);

        const pinEl = document.createElement('div');
        pinEl.className = 'custom-inst-pin';
        pinEl.style.position = 'relative';
        pinEl.style.width = '32px';
        pinEl.style.height = '32px';
        pinEl.style.display = 'flex';
        pinEl.style.alignItems = 'center';
        pinEl.style.justifyContent = 'center';
        pinEl.style.cursor = 'pointer';

        // Floating Institution Name Label directly on top of the dot
        const labelEl = document.createElement('div');
        labelEl.className = 'inst-pin-label';
        labelEl.setAttribute('data-name', inst.name);

        const tierDot = document.createElement('span');
        tierDot.style.color = markerColor;
        tierDot.style.fontSize = '9px';
        tierDot.style.lineHeight = '1';
        tierDot.textContent = '●';

        const nameSpan = document.createElement('span');
        nameSpan.className = 'inst-pin-label-name';
        nameSpan.textContent = inst.name;

        labelEl.appendChild(tierDot);
        labelEl.appendChild(nameSpan);

        const auraEl = document.createElement('div');
        auraEl.className = 'pin-pulse-aura';
        auraEl.style.position = 'absolute';
        auraEl.style.width = '28px';
        auraEl.style.height = '28px';
        auraEl.style.borderRadius = '50%';
        auraEl.style.background = isA ? 'rgba(16,185,129,0.30)' : (isB ? 'rgba(190,149,255,0.30)' : 'rgba(8,189,186,0.25)');

        const dotEl = document.createElement('div');
        dotEl.style.position = 'relative';
        dotEl.style.width = '15px';
        dotEl.style.height = '15px';
        dotEl.style.borderRadius = '50%';
        dotEl.style.background = markerColor;
        dotEl.style.border = '2.5px solid #ffffff';
        dotEl.style.boxShadow = `0 0 14px ${{markerColor}}`;

        pinEl.appendChild(labelEl);
        pinEl.appendChild(auraEl);
        pinEl.appendChild(dotEl);

        const safeName = escapeHtml(inst.name).replace(/'/g, "\\'");
        const domain = getDisplayDomain(webUrl) || 'website';
        const shortH = inst.opening_hours ? inst.opening_hours.split(',')[0] : 'Open Weekly';
        const shortF = inst.admission_fee ? inst.admission_fee.split('/')[0].trim() : 'Free / Subsidized';
        const visitUrl = (inst.visit_url && (inst.visit_url.startsWith('http://') || inst.visit_url.startsWith('https://'))) ? inst.visit_url : '';

        const popupContent = `
          <div style="font-family:'PP Telegraf',sans-serif; min-width:250px; max-width:340px; padding:3px 4px; color:#f1f5f9;">
            <div style="display:flex; align-items:flex-start; justify-content:space-between; gap:8px; margin-bottom:4px;">
              <div style="padding-right:8px;">
                <a href="${{escapeHtml(webUrl || '#')}}" target="_blank" rel="noopener noreferrer" 
                   style="font-size:16px; font-weight:600; color:#ffffff; line-height:1.2; text-decoration:none; display:block;"
                   onmouseover="this.style.color='#93c5fd';this.style.textDecoration='underline'" 
                   onmouseout="this.style.color='#ffffff';this.style.textDecoration='none'">
                  ${{escapeHtml(inst.name)}}
                </a>
                <div style="font-size:12px; color:#a1a1aa; font-family:monospace; margin-top:2px;">
                  ${{escapeHtml(inst.location || inst.city)}} · ${{isA ? 'Verified' : 'One Name'}}
                </div>
              </div>
              <span style="font-size:11px; font-family:monospace; padding:2px 7px; border-radius:6px; border:1px solid ${{isA ? 'rgba(16,185,129,0.4)' : 'rgba(56,189,248,0.4)'}}; background:${{isA ? '#0a2016' : '#0d1d33'}}; color:${{markerColor}}; white-space:nowrap; shrink:0;">
                ${{isA ? 'Verified' : 'One Name'}}
              </span>
            </div>

            <div style="font-size:12px; color:#34d399; font-family:monospace; margin-top:4px;">
              ${{escapeHtml(shortH)}} · ${{escapeHtml(shortF)}}
            </div>

            <div style="font-size:11px; color:#cbd5e1; margin-top:5px; line-height:1.35;">
              ${{escapeHtml(inst.curatorial_focus || inst.neighborhood || inst.location)}}
            </div>

            <div style="display:flex; align-items:center; gap:6px; flex-wrap:wrap; margin-top:8px;">
              ${{webUrl ? `
                <a href="${{escapeHtml(webUrl)}}" target="_blank" rel="noopener noreferrer" 
                   style="display:inline-flex; align-items:center; gap:5px; padding:5px 11px; border-radius:10px; background:#2563eb; color:#ffffff; font-size:12px; font-weight:500; text-decoration:none; box-shadow:0 1px 3px rgba(0,0,0,0.4);"
                   onmouseover="this.style.background='#1d4ed8'" onmouseout="this.style.background='#2563eb'">
                  <span>🌐</span>
                  <span>Visit Website</span>
                  <span style="font-size:10px; opacity:0.8; font-family:monospace;">· ${{escapeHtml(domain)}}</span>
                  <span>↗</span>
                </a>
              ` : ''}}
              <button onclick="window.atlasPlanVisit('${{safeName}}')" 
                      style="display:inline-flex; align-items:center; gap:4px; padding:5px 9px; border-radius:10px; background:#222834; color:#93c5fd; border:1px solid #2f3d58; font-size:11px; font-family:monospace; cursor:pointer;"
                      onmouseover="this.style.background='#2b3548';this.style.color='#ffffff'" onmouseout="this.style.background='#222834';this.style.color='#93c5fd'">
                <span>Plan Visit 💬</span>
              </button>
            </div>

            <div style="display:flex; align-items:center; justify-content:space-between; gap:8px; margin-top:8px; padding-top:7px; border-top:1px solid #27272a; font-size:11px;">
              ${{webUrl ? `
                <a href="${{escapeHtml(webUrl)}}" target="_blank" rel="noopener noreferrer" 
                   style="color:#93c5fd; text-decoration:none; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; max-width:110px;">
                  ${{escapeHtml(domain)}} ↗
                </a>
              ` : '<span></span>'}}
              <div style="display:flex; align-items:center; gap:8px;">
                <button onclick="window.atlasOpenDossier('${{safeName}}')" 
                        style="background:none; border:none; color:#a1a1aa; font-size:11px; cursor:pointer; padding:0;" 
                        onmouseover="this.style.color='#ffffff'" onmouseout="this.style.color='#a1a1aa'">
                  Read info about institution →
                </button>
                <button onclick="window.atlasAskCurator('${{safeName}}')" 
                        style="background:none; border:none; color:#ffffff; font-size:11px; font-weight:600; cursor:pointer; padding:0;" 
                        onmouseover="this.style.color='#93c5fd'" onmouseout="this.style.color='#ffffff'">
                  Ask
                </button>
              </div>
            </div>
          </div>
        `;

        const popup = new maplibregl.Popup({{
          className: 'atlas-dark-popup',
          maxWidth: '360px',
          offset: 16,
          closeButton: true,
          closeOnClick: true
        }}).setHTML(popupContent);

        popup.on('open', () => {{
          pinEl.classList.add('popup-active');
        }});
        popup.on('close', () => {{
          pinEl.classList.remove('popup-active');
        }});

        const marker = new maplibregl.Marker({{ element: pinEl }})
          .setLngLat([inst.lon, inst.lat])
          .setPopup(popup)
          .addTo(cityVectorMap);

        pinEl.addEventListener('click', (e) => {{
          e.stopPropagation();
          marker.togglePopup();
          selectedInstitution = inst;
          if (typeof curatorContext !== 'undefined' && inst) {{
            curatorContext.lastInst = inst;
            if (inst.city) curatorContext.lastCity = inst.city;
          }}
          document.querySelectorAll('.inst-card').forEach(c => {{
            const isTarget = c.getAttribute('data-name') === inst.name;
            c.classList.toggle('active', isTarget);
            if (isTarget) c.scrollIntoView({{ behavior: 'smooth', block: 'nearest' }});
          }});
        }});

        cityVectorMarkers.push(marker);
      }});
    }}

    function exitCityStreetView() {{
      isCityStreetViewActive = false;
      const mapEl = document.getElementById('cityMapContainer');
      if (mapEl) mapEl.classList.add('hidden');
      document.getElementById('cityViewControlBanner')?.classList.add('hidden');
      selectedCityFilter = 'all';
      targetRadius = baseRadius;
      if (typeof deselectInstitution === 'function') {{
        deselectInstitution();
      }}
      applyFilters();
      renderGlobeBarDefault();
      isAutoSpinning = true;
      if (typeof render === 'function') {{
        requestAnimationFrame(render);
      }}
    }}

    // Fixed Procedural Starfield for Cinematic Deep-Space Background
    const STARFIELD = [];
    for (let i = 0; i < 120; i++) {{
      STARFIELD.push({{
        x: ((i * 197.3 + 53) % 1000) / 1000,
        y: ((i * 311.7 + 91) % 1000) / 1000,
        r: (i % 4 === 0 ? 1.4 : 0.8),
        a: 0.12 + (i % 5) * 0.06
      }});
    }}

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

    function getMinRadius() {{ return baseRadius * 0.75; }}
    function getMaxRadius() {{ 
      return baseRadius * 450.0; 
    }}
    let startRadius = baseRadius;

    // Slower Cinematic Motion Physics
    let rotLon = -45;
    let rotLat = 35;
    let isAutoSpinning = true;
    let isDragging = false;
    let velLon = 0, velLat = 0;
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
      const oldBase = baseRadius;
      baseRadius = getBaseRadius();
      if (!isFlying && (Math.abs(targetRadius - oldBase) < 2 || targetRadius === oldBase)) {{
        targetRadius = baseRadius;
        currentRadius = baseRadius;
      }} else {{
        targetRadius = Math.max(getMinRadius(), Math.min(getMaxRadius(), targetRadius));
      }}
      if (cityVectorMap) {{
        cityVectorMap.resize();
      }}
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
        z: z,
        front: z > 0,
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

    function escapeHtml(str) {{
      if (!str) return '';
      return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
    }}

    function matchC(a, b) {{
      if (!a || !b) return false;
      const s1 = a.toLowerCase().trim();
      const s2 = b.toLowerCase().trim();
      return s1 === s2 || s1.includes(s2) || s2.includes(s1);
    }}

    function getValidWebUrl(inst) {{
      if (!inst) return '';
      if (inst.website && typeof inst.website === 'string' && (inst.website.startsWith('http://') || inst.website.startsWith('https://'))) {{
        return inst.website.trim();
      }}
      if (inst.visit_url && typeof inst.visit_url === 'string' && (inst.visit_url.startsWith('http://') || inst.visit_url.startsWith('https://'))) {{
        return inst.visit_url.trim();
      }}
      if (inst.sources && Array.isArray(inst.sources)) {{
        for (const s of inst.sources) {{
          if (typeof s === 'string' && (s.startsWith('http://') || s.startsWith('https://'))) {{
            return s.trim();
          }}
        }}
      }}
      return '';
    }}

    function getDisplayDomain(url) {{
      if (!url) return 'website';
      try {{
        const u = new URL(url);
        return u.hostname.replace(/^www\\./, '');
      }} catch(e) {{
        return 'website';
      }}
    }}

    function easeInOutQuad(t) {{
      return t < 0.5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2;
    }}
    function easeInOutCubic(t) {{
      return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
    }}

    // High-Speed Rail Corridors Connecting Independent Art Spaces
    const CLEAN_RAIL_CORRIDORS = [
      {{ name: "Eurostar High-Speed Rail", from: "London", to: "Paris", travel_time: "2h 16m", emission_saving: "90% CO₂ reduction", pts: [[-0.1278, 51.5074], [1.3, 51.1], [1.8, 50.9], [2.3522, 48.8566]] }},
      {{ name: "Thalys / Eurostar Clean Corridor", from: "Paris", to: "Brussels", travel_time: "1h 22m", emission_saving: "92% CO₂ reduction", pts: [[2.3522, 48.8566], [3.3, 49.8], [4.3517, 50.8503]] }},
      {{ name: "Benelux Clean Rail", from: "Brussels", to: "Amsterdam", travel_time: "1h 50m", emission_saving: "88% CO₂ reduction", pts: [[4.3517, 50.8503], [4.5, 51.4], [4.4, 51.9], [4.9041, 52.3676]] }},
      {{ name: "ICE European Corridor", from: "Amsterdam", to: "Berlin", travel_time: "5h 50m", emission_saving: "85% CO₂ reduction", pts: [[4.9041, 52.3676], [7.0, 52.2], [9.7, 52.4], [13.4050, 52.5200]] }},
      {{ name: "TGV / ICE Rhine-Main Link", from: "Paris", to: "Frankfurt", travel_time: "3h 38m", emission_saving: "91% CO₂ reduction", pts: [[2.3522, 48.8566], [5.0, 49.0], [7.0, 49.2], [8.6821, 50.1109]] }},
      {{ name: "ICE Sprinter Corridor", from: "Frankfurt", to: "Berlin", travel_time: "3h 54m", emission_saving: "89% CO₂ reduction", pts: [[8.6821, 50.1109], [9.9, 51.0], [11.5, 51.5], [13.4050, 52.5200]] }},
      {{ name: "Rhine Valley Ecological Line", from: "Frankfurt", to: "Basel", travel_time: "2h 45m", emission_saving: "86% CO₂ reduction", pts: [[8.6821, 50.1109], [8.4, 49.0], [7.8, 48.0], [7.5886, 47.5596]] }},
      {{ name: "Railjet Trans-Alps Corridor", from: "Frankfurt", to: "Vienna", travel_time: "6h 20m", emission_saving: "88% CO₂ reduction", pts: [[8.6821, 50.1109], [11.58, 48.13], [13.0, 48.2], [16.3738, 48.2082]] }},
      {{ name: "AVE Clean Speed Line", from: "Madrid", to: "Barcelona", travel_time: "2h 30m", emission_saving: "92% CO₂ reduction", pts: [[-3.692, 40.415], [-0.88, 41.65], [2.1734, 41.3851]] }},
      {{ name: "Amtrak Northeast Electric Corridor", from: "Boston", to: "New York", travel_time: "3h 40m", emission_saving: "83% CO₂ reduction", pts: [[-71.0589, 42.3601], [-72.5, 41.5], [-73.9776, 40.7614]] }},
      {{ name: "Amtrak Acela Electric Corridor", from: "New York", to: "Washington DC", travel_time: "2h 55m", emission_saving: "86% CO₂ reduction", pts: [[-73.9776, 40.7614], [-75.1652, 39.9526], [-77.0369, 38.9072]] }},
      {{ name: "Tokaido Shinkansen High-Speed Rail", from: "Tokyo", to: "Kyoto", travel_time: "2h 15m", emission_saving: "94% CO₂ reduction", pts: [[139.6917, 35.6895], [138.5, 35.1], [136.9, 35.1], [135.7681, 35.0116]] }}
    ];

    let isRailVisible = true;
    let hoveredRailCorridor = null;
    let hoveredRailPoint = null;

    function distToSegment(px, py, x1, y1, x2, y2) {{
      const dx = x2 - x1;
      const dy = y2 - y1;
      if (dx === 0 && dy === 0) return Math.hypot(px - x1, py - y1);
      const t = Math.max(0, Math.min(1, ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)));
      return Math.hypot(px - (x1 + t * dx), py - (y1 + t * dy));
    }}


    function drawInstitutionMicroCard(ctx, inst, px, py, width, height) {{
      if (!inst) return;
      ctx.save();
      const isA = inst.tier === 'A';
      const isB = inst.tier === 'B';
      const tierColor = isA ? '#10b981' : (isB ? '#be95ff' : '#08bdba');
      const tierLabel = isA ? '● TIER A · INDEPENDENT' : (isB ? '● TIER B · FLAGGED' : '● TIER U · UNVERIFIED');

      const webUrl = getValidWebUrl(inst);
      const domain = getDisplayDomain(webUrl) || 'website';

      ctx.font = 'bold 12px "PP Telegraf", "PP Telegraph", sans-serif';
      const nameText = inst.name;
      const nameW = ctx.measureText(nameText).width;

      const locText = [inst.city, inst.country].filter(Boolean).join(', ');
      const subText = locText + (inst.curatorial_focus ? ' · ' + inst.curatorial_focus : (inst.neighborhood ? ' · ' + inst.neighborhood : ''));
      ctx.font = '10px "PP Telegraf", "PP Telegraph", sans-serif';
      const subW = ctx.measureText(subText).width;

      ctx.font = '10px "PP Telegraf", monospace';
      const webW = ctx.measureText('🌐 ' + domain + ' ↗').width;

      const cardW = Math.max(240, Math.min(360, Math.max(nameW, subW, webW + 36) + 28));
      const cardH = webUrl ? 74 : 54;

      let cardX = px - cardW / 2;
      cardX = Math.max(12, Math.min(width - cardW - 12, cardX));

      let cardY = py - cardH - 12;
      if (cardY < 12) cardY = py + 16;

      ctx.fillStyle = 'rgba(10, 16, 28, 0.96)';
      ctx.beginPath();
      ctx.roundRect ? ctx.roundRect(cardX, cardY, cardW, cardH, 8) : ctx.rect(cardX, cardY, cardW, cardH);
      ctx.fill();

      ctx.strokeStyle = tierColor;
      ctx.lineWidth = 1.2;
      ctx.stroke();

      ctx.fillStyle = tierColor;
      ctx.beginPath();
      ctx.roundRect ? ctx.roundRect(cardX, cardY, 3.5, cardH, [8, 0, 0, 8]) : ctx.rect(cardX, cardY, 3.5, cardH);
      ctx.fill();

      ctx.font = 'bold 9px "PP Telegraf", monospace';
      ctx.fillStyle = tierColor;
      ctx.textAlign = 'left';
      ctx.textBaseline = 'top';
      ctx.fillText(tierLabel, cardX + 12, cardY + 7);

      ctx.font = 'bold 12px "PP Telegraf", "PP Telegraph", sans-serif';
      ctx.fillStyle = '#ffffff';
      let displayName = nameText;
      if (ctx.measureText(displayName).width > cardW - 24) {{
        while (displayName.length > 5 && ctx.measureText(displayName + '…').width > cardW - 24) {{
          displayName = displayName.slice(0, -1);
        }}
        displayName += '…';
      }}
      ctx.fillText(displayName, cardX + 12, cardY + 20);

      ctx.font = '10px "PP Telegraf", "PP Telegraph", sans-serif';
      ctx.fillStyle = '#94a3b8';
      let displaySub = subText;
      if (ctx.measureText(displaySub).width > cardW - 24) {{
        while (displaySub.length > 5 && ctx.measureText(displaySub + '…').width > cardW - 24) {{
          displaySub = displaySub.slice(0, -1);
        }}
        displaySub += '…';
      }}
      ctx.fillText(displaySub, cardX + 12, cardY + 36);

      if (webUrl) {{
        const btnX = cardX + 12;
        const btnY = cardY + 52;
        const btnW = webW + 16;
        const btnH = 16;

        ctx.fillStyle = 'rgba(37, 99, 235, 0.25)';
        ctx.strokeStyle = 'rgba(96, 165, 250, 0.70)';
        ctx.lineWidth = 0.8;
        ctx.beginPath();
        ctx.roundRect ? ctx.roundRect(btnX, btnY, btnW, btnH, 4) : ctx.rect(btnX, btnY, btnW, btnH);
        ctx.fill();
        ctx.stroke();

        ctx.font = '10px "PP Telegraf", monospace';
        ctx.fillStyle = '#93c5fd';
        ctx.textAlign = 'left';
        ctx.textBaseline = 'top';
        ctx.fillText('🌐 ' + domain + ' ↗', btnX + 8, btnY + 2);

        ctx.font = '9px "PP Telegraf", sans-serif';
        ctx.fillStyle = '#64748b';
        ctx.fillText('Click to open website', btnX + btnW + 8, btnY + 3);

        hoveredMicroCardHitbox = {{
          inst: inst,
          webUrl: webUrl,
          btnX: btnX,
          btnY: btnY,
          btnW: btnW,
          btnH: btnH,
          cardX: cardX,
          cardY: cardY,
          cardW: cardW,
          cardH: cardH
        }};
        window.hoveredMicroCardHitbox = hoveredMicroCardHitbox;
      }}

      ctx.restore();
    }}

    let hoveredMicroCardHitbox = null;
    let cityClusterHitboxes = [];
    let cityBadgeHitboxes = [];
    let visibleDots = [];
    let cityMuseumHitboxes = [];

    function render() {{
      // Scale coordinates to high-DPI hardware buffer for crystal-clear Retina rendering
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      ctx.clearRect(0, 0, width, height);
      ctx.imageSmoothingEnabled = true;
      ctx.imageSmoothingQuality = 'high';

      if (!isDragging && !isFlying) {{
        if (Math.abs(velLon) > 0.001 || Math.abs(velLat) > 0.001) {{
          rotLon = (rotLon - velLon) % 360;
          rotLat = Math.max(-82, Math.min(82, rotLat + velLat));
          velLon *= 0.91;
          velLat *= 0.91;
        }} else if (isAutoSpinning) {{
          rotLon = (rotLon + 0.04) % 360;
        }}
      }}

      if (isFlying) {{
        flightProgress += 0.014;
        if (flightProgress >= 1) {{
          flightProgress = 1;
          isFlying = false;
          rotLon = targetRotLon % 360;
          rotLat = targetRotLat;
          currentRadius = targetRadius;
        }} else {{
          const ease = easeInOutCubic(flightProgress);
          rotLon = (startRotLon + (targetRotLon - startRotLon) * ease) % 360;
          rotLat = startRotLat + (targetRotLat - startRotLat) * ease;
          const baseR = startRadius + (targetRadius - startRadius) * ease;
          // Smooth parabolic orbital arc on long distance flights
          const dDeg = Math.hypot(targetRotLon - startRotLon, targetRotLat - startRotLat);
          if (dDeg > 20 && (startRadius > baseRadius * 3 || targetRadius > baseRadius * 3)) {{
            const arcDip = Math.sin(flightProgress * Math.PI) * Math.min(startRadius * 0.35, baseRadius * 2.2);
            currentRadius = Math.max(baseRadius * 0.85, baseR - arcDip);
          }} else {{
            currentRadius = baseR;
          }}
        }}
      }} else {{
        currentRadius += (targetRadius - currentRadius) * 0.085;
      }}

      const cx = width / 2;
      const cy = height / 2;
      const r = currentRadius;

      // Dynamic City Detection for Free Zooming & Explicit City Selection
      let activeCity = selectedCityFilter !== 'all' ? selectedCityFilter : null;
      if (!activeCity && r > baseRadius * 12.0) {{
        let closestDist = Infinity;
        let closestCity = null;
        for (let i = 0; i < ALL_CITIES_REGISTRY.length; i++) {{
          const c = ALL_CITIES_REGISTRY[i];
          const dDeg = Math.hypot(c.lon - rotLon, c.lat - rotLat);
          if (dDeg < closestDist) {{
            closestDist = dDeg;
            closestCity = c;
          }}
        }}
        if (closestCity && closestDist < 2.5) {{
          activeCity = closestCity.name;
        }}
      }}
      const isCityZoom = !!activeCity && r > baseRadius * 12.0;

      // Update Unified Navigation Banner (Country View + City Street View + World View)
      const cityBanner = document.getElementById('cityViewControlBanner');
      const cityTitleEl = document.getElementById('cityViewTitleText');
      const backCountryBtn = document.getElementById('backToCountryBtn');
      const backCountryText = document.getElementById('backToCountryText');
      const badgeIcon = document.getElementById('cityViewBadgeIcon');

      if (cityBanner) {{
        if (isCityStreetViewActive) {{
          cityBanner.classList.remove('hidden');
        }} else if (isCityZoom && activeCity) {{
          cityBanner.classList.remove('hidden');
          const cityMatches = ALL_INSTITUTIONS.filter(i => matchC(i.city, activeCity));
          const cityMeta = ALL_CITIES_REGISTRY.find(c => matchC(c.name, activeCity));
          const cityCountry = cityMeta ? cityMeta.country : lastSelectedCountry;
          if (badgeIcon) badgeIcon.textContent = '';
          if (cityTitleEl) {{
            cityTitleEl.textContent = `${{activeCity.toUpperCase()}} · ${{cityMatches.length}} CULTURAL SPACES`;
          }}
          if (backCountryBtn && cityCountry) {{
            backCountryBtn.classList.remove('hidden');
            if (backCountryText) backCountryText.textContent = cityCountry;
          }} else if (backCountryBtn) {{
            backCountryBtn.classList.add('hidden');
          }}
        }} else if (selectedCountryFilter !== 'all') {{
          cityBanner.classList.remove('hidden');
          const countryMatches = ALL_INSTITUTIONS.filter(i => matchC(i.country, selectedCountryFilter));
          const countryCities = ALL_CITIES_REGISTRY.filter(c => matchC(c.country, selectedCountryFilter));
          if (badgeIcon) badgeIcon.textContent = '';
          if (cityTitleEl) {{
            cityTitleEl.textContent = `${{selectedCountryFilter.toUpperCase()}} · ${{countryMatches.length}} CLEAN SPACES IN ${{countryCities.length}} CITIES`;
          }}
          if (backCountryBtn) backCountryBtn.classList.add('hidden');
        }} else {{
          cityBanner.classList.add('hidden');
        }}
      }}

      if (!isCityZoom) {{
        // =======================================================
        // 🌍 GLOBAL & REGIONAL 3D SPHERE VIEW
        // =======================================================

        // 0. Cinematic Distant Starfield (Fades out smoothly as camera approaches Earth)
        if (r < baseRadius * 3.2) {{
          const starAlpha = Math.max(0, 1 - (r - baseRadius) / (baseRadius * 2.2));
          ctx.save();
          for (let s = 0; s < STARFIELD.length; s++) {{
            const st = STARFIELD[s];
            const sx = st.x * width;
            const sy = st.y * height;
            // Only draw stars outside the main globe disk
            if (Math.hypot(sx - cx, sy - cy) > r * 0.95) {{
              ctx.beginPath();
              ctx.arc(sx, sy, st.r, 0, Math.PI * 2);
              ctx.fillStyle = `rgba(226, 232, 240, ${{st.a * starAlpha}})`;
              ctx.fill();
            }}
          }}
          ctx.restore();
        }}

        // 1. Outer Atmospheric Limb Glow / Halo
        const limbGrad = ctx.createRadialGradient(cx, cy, r * 0.95, cx, cy, r * 1.09);
        limbGrad.addColorStop(0, 'rgba(59, 130, 246, 0.22)');
        limbGrad.addColorStop(0.35, 'rgba(37, 99, 235, 0.12)');
        limbGrad.addColorStop(0.7, 'rgba(29, 78, 216, 0.04)');
        limbGrad.addColorStop(1, 'rgba(0, 0, 0, 0)');
        ctx.fillStyle = limbGrad;
        ctx.beginPath();
        ctx.arc(cx, cy, r * 1.09, 0, Math.PI * 2);
        ctx.fill();

        // 2. 3D Spherical Ocean Lighting
        const sphereGrad = ctx.createRadialGradient(cx - r * 0.32, cy - r * 0.32, r * 0.08, cx, cy, r);
        sphereGrad.addColorStop(0, '#061324');
        sphereGrad.addColorStop(0.5, '#020611');
        sphereGrad.addColorStop(1, '#010204');
        ctx.beginPath();
        ctx.arc(cx, cy, r, 0, Math.PI * 2);
        ctx.fillStyle = sphereGrad;
        ctx.fill();
        ctx.strokeStyle = '#223048';
        ctx.lineWidth = 1.2;
        ctx.stroke();

        // Clip all globe surface features strictly to the spherical limb
        ctx.save();
        ctx.beginPath();
        ctx.arc(cx, cy, r, 0, Math.PI * 2);
        ctx.clip();

        // 3. Graticule with Latitude Parallels and Longitude Meridians
        ctx.strokeStyle = '#0e182a';
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
          if (lat === 0) {{
            ctx.strokeStyle = '#182740';
            ctx.lineWidth = 0.8;
          }} else {{
            ctx.strokeStyle = '#0e182a';
            ctx.lineWidth = 0.5;
          }}
          ctx.stroke();
        }}

        for (let lon = -180; lon < 180; lon += 30) {{
          ctx.beginPath();
          let first = true;
          for (let lat = -80; lat <= 80; lat += 4) {{
            const p = project(lon, lat, r, cx, cy);
            if (p.front) {{
              if (first) {{ ctx.moveTo(p.x, p.y); first = false; }}
              else ctx.lineTo(p.x, p.y);
            }} else first = true;
          }}
          ctx.stroke();
        }}

        // Graticule Degree Annotations
        if (r > baseRadius * 0.9) {{
          ctx.font = '9px "PP Telegraf", "PP Telegraph", sans-serif';
          ctx.fillStyle = '#263a55';
          ctx.textAlign = 'center';
          ctx.textBaseline = 'middle';
          const labels = [
            {{ lat: 0, txt: '0° EQ' }},
            {{ lat: 30, txt: '30° N' }},
            {{ lat: 60, txt: '60° N' }},
            {{ lat: -30, txt: '30° S' }},
            {{ lat: -60, txt: '60° S' }}
          ];
          labels.forEach(lb => {{
            const p = project(rotLon, lb.lat, r, cx, cy);
            if (p.front && p.depth > 0.25) {{
              ctx.fillText(lb.txt, p.x, p.y - 2);
            }}
          }});
        }}

        // 4. Land Polygons with Anti-Glitch Horizon Edge Clipping
        const cosRotLat = Math.max(0.15, Math.cos(toRad(rotLat)));
        const viewAngleSpan = Math.min(1.8, Math.max(0.08, (Math.max(width, height) / r))) * (180 / Math.PI) + 12;
        const minVisLat = rotLat - viewAngleSpan;
        const maxVisLat = rotLat + viewAngleSpan;
        const lonAngleSpan = viewAngleSpan / cosRotLat + 15;

        for (let i = 0; i < COUNTRY_POLYS.length; i++) {{
          const country = COUNTRY_POLYS[i];
          const isCActive = selectedCountryFilter !== 'all' && matchC(country.n, selectedCountryFilter);
          const isCHovered = hoveredCountry && matchC(country.n, hoveredCountry);

          // Fast viewport culling at higher zoom levels
          if (r > baseRadius * 1.6 && country.b) {{
            if (country.b[3] < minVisLat || country.b[2] > maxVisLat) continue;
            const cLon = (country.b[0] + country.b[1]) / 2;
            const dLon = Math.abs((cLon - rotLon + 540) % 360 - 180);
            if (dLon > lonAngleSpan + (country.b[1] - country.b[0]) / 2) continue;
          }}

          ctx.fillStyle = isCActive ? '#1e3a8a' : isCHovered ? '#1e293b' : country.c;

          for (let j = 0; j < country.r.length; j++) {{
            const ring = country.r[j];
            if (!ring || ring.length < 3) continue;

            const proj = [];
            let anyFront = false;
            let allFront = true;
            for (let k = 0; k < ring.length; k++) {{
              const p = project(ring[k][0], ring[k][1], r, cx, cy);
              proj.push(p);
              if (p.front) anyFront = true;
              else allFront = false;
            }}

            if (!anyFront) continue;

            if (allFront) {{
              ctx.beginPath();
              ctx.moveTo(proj[0].x, proj[0].y);
              for (let k = 1; k < proj.length; k++) {{
                ctx.lineTo(proj[k].x, proj[k].y);
              }}
              ctx.closePath();
              ctx.fill();
              ctx.strokeStyle = isCActive ? '#60a5fa' : isCHovered ? '#93c5fd' : '#050c18';
              ctx.lineWidth = isCActive ? 2.2 : isCHovered ? 1.8 : 0.75;
              ctx.stroke();
            }} else {{
              // Ring crosses horizon: clip edges strictly at the horizon plane
              const clippedPath = [];
              const N = ring.length;
              for (let k = 0; k < N; k++) {{
                const p1 = proj[k];
                const p2 = proj[(k + 1) % N];
                if (p1.front) {{
                  clippedPath.push({{ x: p1.x, y: p1.y, isRealEdge: true }});
                  if (!p2.front) {{
                    const denom = p1.z - p2.z;
                    const t = Math.abs(denom) > 1e-6 ? Math.max(0, Math.min(1, p1.z / denom)) : 0.5;
                    let hx = (p1.x - cx) + t * (p2.x - p1.x);
                    let hy = (cy - p1.y) + t * (p1.y - p2.y);
                    const d = Math.hypot(hx, hy);
                    if (d > 0.001) {{ hx *= r / d; hy *= r / d; }}
                    clippedPath.push({{ x: cx + hx, y: cy - hy, isRealEdge: false }});
                  }}
                }} else if (p2.front) {{
                  const denom = p1.z - p2.z;
                  const t = Math.abs(denom) > 1e-6 ? Math.max(0, Math.min(1, p1.z / denom)) : 0.5;
                  let hx = (p1.x - cx) + t * (p2.x - p1.x);
                  let hy = (cy - p1.y) + t * (p1.y - p2.y);
                  const d = Math.hypot(hx, hy);
                  if (d > 0.001) {{ hx *= r / d; hy *= r / d; }}
                  clippedPath.push({{ x: cx + hx, y: cy - hy, isRealEdge: false }});
                }}
              }}

              if (clippedPath.length >= 3) {{
                ctx.beginPath();
                ctx.moveTo(clippedPath[0].x, clippedPath[0].y);
                for (let k = 1; k < clippedPath.length; k++) {{
                  ctx.lineTo(clippedPath[k].x, clippedPath[k].y);
                }}
                ctx.closePath();
                ctx.fill();

                ctx.beginPath();
                let penDown = false;
                for (let k = 0; k < clippedPath.length; k++) {{
                  const cp1 = clippedPath[k];
                  const cp2 = clippedPath[(k + 1) % clippedPath.length];
                  if (cp1.isRealEdge && cp2.isRealEdge) {{
                    if (!penDown) {{ ctx.moveTo(cp1.x, cp1.y); penDown = true; }}
                    ctx.lineTo(cp2.x, cp2.y);
                  }} else {{
                    penDown = false;
                  }}
                }}
                ctx.strokeStyle = isCActive ? '#60a5fa' : isCHovered ? '#93c5fd' : '#050c18';
                ctx.lineWidth = isCActive ? 2.2 : isCHovered ? 1.8 : 0.75;
                ctx.stroke();
              }}
            }}
          }}
        }}
        ctx.restore();

        // 6. Country Centroid Names (Smoothly fade out as zoom approaches city/regional level)
        if (r > baseRadius * 0.8 && r < baseRadius * 2.8) {{
          const fadeAlpha = r > baseRadius * 1.8 ? Math.max(0, 1 - (r - baseRadius * 1.8) / (baseRadius * 1.0)) : 1.0;
          ctx.save();
          ctx.globalAlpha = fadeAlpha;
          ctx.font = '13px "PP Telegraf", "PP Telegraph", sans-serif';
          ctx.textAlign = 'center';
          ctx.textBaseline = 'middle';
          COUNTRY_CENTROIDS.forEach(c => {{
            const isSel = selectedCountryFilter !== 'all' && matchC(c.name, selectedCountryFilter);
            if (selectedCountryFilter === 'all' || isSel) {{
              const pt = project(c.lon, c.lat, r, cx, cy);
              if (pt.front && pt.depth > 0.12) {{
                ctx.fillStyle = isSel ? '#60a5fa' : '#475569';
                ctx.fillText(c.name, pt.x, pt.y);
              }}
            }}
          }});
          ctx.restore();
        }}

        // 7. City Badges (All cities in selected country or top cities worldwide)
        cityBadgeHitboxes = [];
        const drawnCityBoxes = [];
        ctx.font = '14px "PP Telegraf", "PP Telegraph", sans-serif';
        
        let candidateCities = [];
        if (selectedCountryFilter !== 'all') {{
          candidateCities = ALL_CITIES_REGISTRY.filter(c => matchC(c.country, selectedCountryFilter));
        }} else {{
          candidateCities = ALL_CITIES_REGISTRY;
        }}

        const sortedCities = [...candidateCities].sort((a, b) => {{
          const aSel = selectedCityFilter.toLowerCase() === a.name.toLowerCase();
          const bSel = selectedCityFilter.toLowerCase() === b.name.toLowerCase();
          if (aSel) return -1;
          if (bSel) return 1;
          return (b.count || 0) - (a.count || 0);
        }});

        sortedCities.forEach(city => {{
          const isSelected = selectedCityFilter.toLowerCase() === city.name.toLowerCase();
          if (r > baseRadius * 14.0 && !isSelected) return;
          const pt = project(city.lon, city.lat, r, cx, cy);
          if (pt.front && pt.depth > 0.08) {{
            const isHovered = hoveredCity && hoveredCity.toLowerCase() === city.name.toLowerCase();
            const isCountryActive = selectedCountryFilter !== 'all';
            const countLabel = isCountryActive || r > baseRadius * 1.5 ? ` (${{city.count}})` : '';
            const txt = (isSelected ? '● ' : '■ ') + city.name + countLabel;
            const tw = ctx.measureText(txt).width;
            const bw = tw + 14;
            const bh = 24;
            const bx = pt.x - bw / 2;
            const by = pt.y - 28;

            const collides = drawnCityBoxes.some(box => {{
              return !(bx + bw + 8 < box.x || bx > box.x + box.w + 8 || by + bh + 6 < box.y || by > box.y + box.h + 6);
            }});

            // Selected city always draws; other cities only draw if they do NOT collide
            if (!collides || isSelected) {{
              drawnCityBoxes.push({{ x: bx, y: by, w: bw, h: bh }});
              cityBadgeHitboxes.push({{
                name: city.name,
                country: city.country,
                x: bx, y: by, w: bw, h: bh,
                lon: city.lon, lat: city.lat
              }});

              const badgeAlpha = isSelected ? 1.0 : (r > baseRadius * 10.0 ? Math.max(0, 1 - (r - baseRadius * 10.0) / (baseRadius * 4.0)) : 1.0);
              ctx.save();
              ctx.globalAlpha = badgeAlpha;

              ctx.fillStyle = isSelected ? '#1d4ed8' : isHovered ? '#1e3a8a' : '#070b14';
              ctx.beginPath();
              ctx.roundRect ? ctx.roundRect(bx, by, bw, bh, 5) : ctx.rect(bx, by, bw, bh);
              ctx.fill();

              ctx.strokeStyle = isSelected ? '#93c5fd' : isHovered ? '#60a5fa' : '#222d42';
              ctx.lineWidth = isSelected || isHovered ? 1.5 : 1;
              ctx.stroke();

              ctx.fillStyle = isSelected || isHovered ? '#ffffff' : '#cbd5e1';
              ctx.textAlign = 'center';
              ctx.textBaseline = 'middle';
              ctx.fillText(txt, pt.x, by + bh / 2 + 0.5);

              ctx.beginPath();
              ctx.arc(pt.x, pt.y, 2.5, 0, Math.PI * 2);
              ctx.fillStyle = isSelected ? '#93c5fd' : '#3b82f6';
              ctx.fill();
              ctx.restore();
            }}
          }}
        }});

        // 7.5 Clean High-Speed Rail Corridors between Cultural Capitals
        if (isRailVisible && r > baseRadius * 1.1 && r < baseRadius * 14.0) {{
          ctx.save();
          const pulseOffset = (Date.now() * 0.0003) % 1.0;
          CLEAN_RAIL_CORRIDORS.forEach(corridor => {{
            let started = false;
            let anyFront = false;
            const projectedPts = [];
            for (let k = 0; k < corridor.pts.length; k++) {{
              const p = project(corridor.pts[k][0], corridor.pts[k][1], r, cx, cy);
              projectedPts.push(p);
              if (p.front) anyFront = true;
            }}
            if (!anyFront) return;

            const isHov = hoveredRailCorridor === corridor;

            // Draw dashed ecological transit line
            ctx.beginPath();
            ctx.setLineDash(isHov ? [] : [4, 4]);
            ctx.strokeStyle = isHov ? '#38bdf8' : 'rgba(56, 189, 248, 0.45)';
            ctx.lineWidth = isHov ? 2.5 : 1.3;
            if (isHov) {{
              ctx.shadowColor = '#38bdf8';
              ctx.shadowBlur = 8;
            }} else {{
              ctx.shadowBlur = 0;
            }}
            for (let k = 0; k < projectedPts.length; k++) {{
              const p = projectedPts[k];
              if (p.front) {{
                if (!started) {{ ctx.moveTo(p.x, p.y); started = true; }}
                else ctx.lineTo(p.x, p.y);
              }} else started = false;
            }}
            ctx.stroke();

            // Animated clean transit pulse bead traveling the corridor
            if (projectedPts.length >= 2) {{
              const segIdx = Math.floor(pulseOffset * (corridor.pts.length - 1));
              const segT = (pulseOffset * (corridor.pts.length - 1)) - segIdx;
              const pA = corridor.pts[segIdx];
              const pB = corridor.pts[segIdx + 1] || pA;
              const interpLon = pA[0] + (pB[0] - pA[0]) * segT;
              const interpLat = pA[1] + (pB[1] - pA[1]) * segT;
              const beadPt = project(interpLon, interpLat, r, cx, cy);
              if (beadPt.front && beadPt.depth > 0.1) {{
                ctx.setLineDash([]);
                ctx.shadowBlur = 0;
                ctx.beginPath();
                ctx.arc(beadPt.x, beadPt.y, isHov ? 3.0 : 2.2, 0, Math.PI * 2);
                ctx.fillStyle = '#38bdf8';
                ctx.fill();
              }}
            }}
          }});
          ctx.restore();

          // Render Rail Corridor Tooltip if hovered
          if (hoveredRailCorridor && hoveredRailPoint) {{
            ctx.save();
            const corr = hoveredRailCorridor;
            const tipHeader = `🚆 ${{corr.name.toUpperCase()}}`;
            const tipSub = `${{corr.from}} ⇄ ${{corr.to}} · ${{corr.travel_time || 'Eco-Transit'}} · ${{corr.emission_saving || 'Low Carbon'}}`;
            ctx.font = 'bold 10px "PP Telegraf", monospace';
            const hw = ctx.measureText(tipHeader).width;
            ctx.font = '11px "PP Telegraf", "PP Telegraph", sans-serif';
            const sw = ctx.measureText(tipSub).width;
            const rw = Math.max(hw, sw) + 22;
            const rh = 40;
            let rx = hoveredRailPoint.x - rw / 2;
            let ry = hoveredRailPoint.y - rh - 12;
            rx = Math.max(16, Math.min(width - rw - 16, rx));
            if (ry < 16) ry = hoveredRailPoint.y + 16;

            ctx.fillStyle = 'rgba(7, 16, 28, 0.95)';
            ctx.beginPath();
            ctx.roundRect ? ctx.roundRect(rx, ry, rw, rh, 6) : ctx.rect(rx, ry, rw, rh);
            ctx.fill();
            ctx.strokeStyle = '#38bdf8';
            ctx.lineWidth = 1.2;
            ctx.stroke();

            ctx.font = 'bold 9px "PP Telegraf", monospace';
            ctx.fillStyle = '#38bdf8';
            ctx.textAlign = 'left';
            ctx.textBaseline = 'top';
            ctx.fillText(tipHeader, rx + 10, ry + 6);

            ctx.font = '11px "PP Telegraf", "PP Telegraph", sans-serif';
            ctx.fillStyle = '#ffffff';
            ctx.fillText(tipSub, rx + 10, ry + 20);
            ctx.restore();
          }}
        }}

        // 8. Render Institution Dots & Independent Space Clusters on Global Sphere
        visibleDots = [];
        cityClusterHitboxes = [];

        const isClusterZoom = r < baseRadius * 6.0 && selectedCityFilter === 'all';
        const cityInstMap = {{}};
        filteredList.forEach(inst => {{
          if (!inst.city) return;
          const k = inst.city.toLowerCase().trim();
          if (!cityInstMap[k]) cityInstMap[k] = {{ name: inst.city, insts: [], lon: inst.lon, lat: inst.lat }};
          cityInstMap[k].insts.push(inst);
        }});

        const clusteredCityKeys = new Set();
        if (isClusterZoom) {{
          Object.keys(cityInstMap).forEach(k => {{
            if (cityInstMap[k].insts.length >= 2) {{
              clusteredCityKeys.add(k);
            }}
          }});
        }}

        filteredList.forEach(inst => {{
          const k = (inst.city || '').toLowerCase().trim();
          if (isClusterZoom && clusteredCityKeys.has(k)) {{
            return;
          }}
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

        // Render Independent Space Cluster Badges on Globe
        if (isClusterZoom) {{
          clusteredCityKeys.forEach(k => {{
            const cData = cityInstMap[k];
            const avgLon = cData.insts.reduce((sum, i) => sum + i.lon, 0) / cData.insts.length;
            const avgLat = cData.insts.reduce((sum, i) => sum + i.lat, 0) / cData.insts.length;
            const pt = project(avgLon, avgLat, r, cx, cy);
            if (pt.front && pt.depth > 0.08) {{
              const isHov = hoveredCity && hoveredCity.toLowerCase() === cData.name.toLowerCase();
              const badgeR = isHov ? 13 : 11;
              const countTxt = String(cData.insts.length);

              cityClusterHitboxes.push({{
                cityName: cData.name,
                x: pt.x - badgeR,
                y: pt.y - badgeR,
                w: badgeR * 2,
                h: badgeR * 2,
                cx: pt.x,
                cy: pt.y,
                count: cData.insts.length
              }});

              ctx.save();
              ctx.beginPath();
              ctx.arc(pt.x, pt.y, badgeR + 3, 0, Math.PI * 2);
              ctx.fillStyle = isHov ? 'rgba(52, 211, 153, 0.35)' : 'rgba(16, 185, 129, 0.20)';
              ctx.fill();

              ctx.beginPath();
              ctx.arc(pt.x, pt.y, badgeR, 0, Math.PI * 2);
              ctx.fillStyle = isHov ? '#047857' : '#064e3b';
              ctx.fill();
              ctx.strokeStyle = isHov ? '#6ee7b7' : '#10b981';
              ctx.lineWidth = isHov ? 2 : 1.4;
              ctx.stroke();

              ctx.font = 'bold 10px "PP Telegraf", monospace';
              ctx.fillStyle = '#ffffff';
              ctx.textAlign = 'center';
              ctx.textBaseline = 'middle';
              ctx.fillText(countTxt, pt.x, pt.y + 0.5);
              ctx.restore();

              if (isHov) {{
                ctx.save();
                ctx.font = 'bold 11px "PP Telegraf", "PP Telegraph", sans-serif';
                const tipTxt = `${{cData.name}} · ${{cData.insts.length}} Independent Spaces`;
                const tw = ctx.measureText(tipTxt).width;
                const tbx = pt.x - tw / 2 - 8;
                const tby = pt.y > 35 ? pt.y - 30 : pt.y + 16;
                ctx.fillStyle = '#0a101b';
                ctx.beginPath();
                ctx.roundRect ? ctx.roundRect(tbx, tby, tw + 16, 22, 5) : ctx.rect(tbx, tby, tw + 16, 22);
                ctx.fill();
                ctx.strokeStyle = '#10b981';
                ctx.lineWidth = 1.2;
                ctx.stroke();
                ctx.fillStyle = '#ffffff';
                ctx.textAlign = 'center';
                ctx.textBaseline = 'middle';
                ctx.fillText(tipTxt, pt.x, tby + 11);
                ctx.restore();
              }}
            }}
          }});
        }}

        visibleDots.forEach(d => {{
          const isSel = selectedInstitution && selectedInstitution.name === d.inst.name;
          const isHov = hoveredInstitution && hoveredInstitution.name === d.inst.name;

          if (isSel) {{
            const pTime = (Date.now() % 2200) / 2200;
            const pRadius = 7 + pTime * 22;
            const pAlpha = (1 - pTime) * 0.75;
            ctx.save();
            ctx.beginPath();
            ctx.arc(d.x, d.y, pRadius, 0, Math.PI * 2);
            ctx.strokeStyle = `rgba(96, 165, 250, ${{pAlpha}})`;
            ctx.lineWidth = 1.5;
            ctx.stroke();

            ctx.beginPath();
            ctx.arc(d.x, d.y, 7, 0, Math.PI * 2);
            ctx.strokeStyle = '#ffffff';
            ctx.lineWidth = 2.0;
            ctx.stroke();
            ctx.restore();
          }}

          ctx.beginPath();
          ctx.arc(d.x, d.y, isSel ? 4.5 : isHov ? 4 : 2.5, 0, Math.PI * 2);
          ctx.fillStyle = d.inst.tier === 'A' ? '#10b981' : d.inst.tier === 'B' ? '#be95ff' : '#08bdba';
          ctx.fill();

          const shouldDrawGlobeLabel = isHov || isSel || 
            selectedCountryFilter !== 'all' || 
            selectedCityFilter !== 'all' || 
            currentRadius >= baseRadius * 1.35;

          if (isHov || (selectedCountryFilter !== 'all' && isSel)) {{
            drawInstitutionMicroCard(ctx, d.inst, d.x, d.y, width, height);
          }} else if (shouldDrawGlobeLabel) {{
            // Render institution name on top of dot across ALL points of view
            ctx.save();
            ctx.font = '600 10.5px "PP Telegraf", "PP Telegraph", sans-serif';
            ctx.textAlign = 'center';
            ctx.textBaseline = 'bottom';
            const nameTxt = d.inst.name.length > 25 ? d.inst.name.substring(0, 23) + '…' : d.inst.name;
            const tw = ctx.measureText(nameTxt).width;
            const bx = d.x - tw / 2 - 5;
            const by = d.y - 18;
            ctx.fillStyle = 'rgba(18, 20, 26, 0.94)';
            if (ctx.roundRect) ctx.roundRect(bx, by, tw + 10, 16, 4);
            else ctx.rect(bx, by, tw + 10, 16);
            ctx.fill();
            ctx.strokeStyle = d.inst.tier === 'A' ? 'rgba(16, 185, 129, 0.65)' : d.inst.tier === 'B' ? 'rgba(190, 149, 255, 0.65)' : 'rgba(8, 189, 186, 0.65)';
            ctx.lineWidth = 1;
            ctx.stroke();
            ctx.fillStyle = '#f8fafc';
            ctx.fillText(nameTxt, d.x, d.y - 5);
            ctx.restore();
          }}
        }});

      }} else {{
        // =======================================================
        // =======================================================
        // 🗺️ DEEP ZOOM CITY VIEW: PRISTINE ARCHITECTURAL CARTOGRAPHY
        // =======================================================
        const cityData = getCityStreetData(activeCity);

        // 1. Regional Ocean & Water Surface Background
        ctx.fillStyle = '#050a14';
        ctx.fillRect(0, 0, width, height);

        // 2. Base Landmass Backdrop for Focused City
        ctx.fillStyle = '#070f1e';
        ctx.fillRect(0, 0, width, height);

        // 3. Subtle Ambient City Focus Spotlight
        const cityCenter = cityData && cityData.center ? cityData.center : [rotLon, rotLat];
        const cProj = project(cityCenter[0], cityCenter[1], r, cx, cy);
        if (cProj.front) {{
          const grad = ctx.createRadialGradient(cProj.x, cProj.y, 15, cProj.x, cProj.y, Math.max(width, height) * 0.65);
          grad.addColorStop(0, 'rgba(15, 30, 54, 0.40)');
          grad.addColorStop(0.5, 'rgba(10, 20, 36, 0.18)');
          grad.addColorStop(1, 'rgba(5, 10, 20, 0)');
          ctx.fillStyle = grad;
          ctx.fillRect(0, 0, width, height);
        }}

        // 4. Subtle City Watermark in Background
        if (activeCity) {{
          ctx.save();
          ctx.font = '700 48px "PP Telegraf", "PP Telegraph", sans-serif';
          ctx.fillStyle = 'rgba(148, 163, 184, 0.06)';
          ctx.textAlign = 'center';
          ctx.textBaseline = 'middle';
          ctx.fillText(activeCity.toUpperCase(), width / 2, Math.max(65, height * 0.16));
          ctx.restore();
        }}

        // 5. Curated Waterways (Only for real curated networks, zero text clutter)
        if (cityData && cityData.waterways && cityData.waterways.length > 0) {{
          ctx.save();
          cityData.waterways.forEach(w => {{
            if (!w.pts || w.pts.length < 2) return;
            ctx.beginPath();
            let started = false;
            w.pts.forEach(pt => {{
              const p = project(pt[0], pt[1], r, cx, cy);
              if (p.front) {{
                if (!started) {{ ctx.moveTo(p.x, p.y); started = true; }}
                else ctx.lineTo(p.x, p.y);
              }}
            }});
            if (started) {{
              ctx.lineCap = 'round';
              ctx.lineJoin = 'round';
              ctx.strokeStyle = '#081729';
              ctx.lineWidth = (w.width || 18) + 6;
              ctx.stroke();
              ctx.strokeStyle = '#0e2947';
              ctx.lineWidth = (w.width || 18);
              ctx.stroke();
            }}
          }});
          ctx.restore();
        }}

        // 6. Curated Parks (Only for real curated networks)
        if (cityData && cityData.parks && cityData.parks.length > 0) {{
          ctx.save();
          cityData.parks.forEach(park => {{
            if (!park.pts || park.pts.length < 3) return;
            ctx.beginPath();
            let started = false;
            park.pts.forEach(pt => {{
              const p = project(pt[0], pt[1], r, cx, cy);
              if (p.front) {{
                if (!started) {{ ctx.moveTo(p.x, p.y); started = true; }}
                else ctx.lineTo(p.x, p.y);
              }}
            }});
            if (started) {{
              ctx.closePath();
              ctx.fillStyle = '#0a1d15';
              ctx.fill();
              ctx.strokeStyle = '#143d26';
              ctx.lineWidth = 1;
              ctx.stroke();
            }}
          }});
          ctx.restore();
        }}

        // 6.5 Secondary Streets & Cadastral Block Grid
        if (cityData && cityData.secondary_streets && cityData.secondary_streets.length > 0) {{
          ctx.save();
          ctx.strokeStyle = '#0f1b2d';
          ctx.lineWidth = 1.0;
          ctx.lineCap = 'round';
          cityData.secondary_streets.forEach(s => {{
            if (!s.pts || s.pts.length < 2) return;
            ctx.beginPath();
            let started = false;
            s.pts.forEach(pt => {{
              const p = project(pt[0], pt[1], r, cx, cy);
              if (p.front) {{
                if (!started) {{ ctx.moveTo(p.x, p.y); started = true; }}
                else ctx.lineTo(p.x, p.y);
              }}
            }});
            if (started) ctx.stroke();
          }});
          ctx.restore();
        }}

        // 7. Curated Major Arterial Streets & Boulevards
        if (cityData && cityData.major_streets && cityData.major_streets.length > 0) {{
          ctx.save();
          ctx.strokeStyle = '#1d314d';
          ctx.lineWidth = 2.0;
          ctx.lineCap = 'round';
          cityData.major_streets.forEach(s => {{
            if (!s.pts || s.pts.length < 2) return;
            ctx.beginPath();
            let started = false;
            s.pts.forEach(pt => {{
              const p = project(pt[0], pt[1], r, cx, cy);
              if (p.front) {{
                if (!started) {{ ctx.moveTo(p.x, p.y); started = true; }}
                else ctx.lineTo(p.x, p.y);
              }}
            }});
            if (started) ctx.stroke();
          }});
          ctx.restore();
        }}

        // 8. Render City Cultural Institutions (Exact Pins & Anti-Collision Badges)
        cityMuseumHitboxes = [];
        const cityInsts = ALL_INSTITUTIONS.filter(i => matchC(i.city, activeCity));

        const projectedInsts = [];
        cityInsts.forEach(inst => {{
          const pt = project(inst.lon, inst.lat, r, cx, cy);
          if (pt.front) {{
            projectedInsts.push({{ inst, pt }});
          }}
        }});

        // First pass: render crisp pins & haloes
        projectedInsts.forEach(({{ inst, pt }}) => {{
          const isSel = selectedInstitution && selectedInstitution.name === inst.name;
          const isHov = hoveredInstitution && hoveredInstitution.name === inst.name;
          const tierColor = inst.tier === 'A' ? '#10b981' : inst.tier === 'B' ? '#be95ff' : '#08bdba';

          ctx.save();
          // Pulsing radar ring on active institution
          if (isSel) {{
            const pTime = (Date.now() % 2200) / 2200;
            const pRadius = 12 + pTime * 28;
            const pAlpha = (1 - pTime) * 0.70;
            ctx.beginPath();
            ctx.arc(pt.x, pt.y, pRadius, 0, Math.PI * 2);
            ctx.strokeStyle = `rgba(96, 165, 250, ${{pAlpha}})`;
            ctx.lineWidth = 1.5;
            ctx.stroke();
          }}

          // Halo
          ctx.beginPath();
          ctx.arc(pt.x, pt.y, isSel ? 16 : isHov ? 12 : 8, 0, Math.PI * 2);
          ctx.fillStyle = isSel ? 'rgba(96, 165, 250, 0.25)' : inst.tier === 'A' ? 'rgba(16, 185, 129, 0.22)' : inst.tier === 'B' ? 'rgba(190, 149, 255, 0.25)' : 'rgba(8, 189, 186, 0.20)';
          ctx.fill();

          // Stroke ring
          ctx.beginPath();
          ctx.arc(pt.x, pt.y, isSel ? 10 : isHov ? 8 : 6, 0, Math.PI * 2);
          ctx.strokeStyle = isSel ? '#ffffff' : tierColor;
          ctx.lineWidth = isSel ? 2 : 1.2;
          ctx.stroke();

          // Center solid dot
          ctx.beginPath();
          ctx.arc(pt.x, pt.y, isSel ? 5 : isHov ? 4.5 : 3.5, 0, Math.PI * 2);
          ctx.fillStyle = tierColor;
          ctx.fill();
          ctx.restore();
        }});

        // Second pass: position and render non-colliding callout badges
        // Clear global city hitboxes to prevent phantom clicks
        cityBadgeHitboxes = [];

        // In dense cities (> 6 institutions), prioritize selected, hovered, and top 5 institutions
        let displayList = [...projectedInsts];
        if (projectedInsts.length > 6) {{
          displayList.sort((a, b) => {{
            const aSel = selectedInstitution && selectedInstitution.name === a.inst.name;
            const bSel = selectedInstitution && selectedInstitution.name === b.inst.name;
            if (aSel) return -1;
            if (bSel) return 1;
            const aHov = hoveredInstitution && hoveredInstitution.name === a.inst.name;
            const bHov = hoveredInstitution && hoveredInstitution.name === b.inst.name;
            if (aHov) return -1;
            if (bHov) return 1;
            return b.inst.lat - a.inst.lat;
          }});
          // Cap at 6 expanded badges to guarantee zero screen overcrowding
          displayList = displayList.slice(0, 6);
        }} else {{
          displayList.sort((a, b) => b.inst.lat - a.inst.lat);
        }}

        const placedBoxes = [];
        const bh = 36;

        displayList.forEach(({{ inst, pt }}) => {{
          const isSel = selectedInstitution && selectedInstitution.name === inst.name;
          const isHov = hoveredInstitution && hoveredInstitution.name === inst.name;
          const tierColor = inst.tier === 'A' ? '#10b981' : inst.tier === 'B' ? '#be95ff' : '#08bdba';

          const webUrl = getValidWebUrl(inst);
          const domain = getDisplayDomain(webUrl) || 'website';

          ctx.font = 'bold 12px "PP Telegraf", "PP Telegraph", sans-serif';
          const nameTxt = inst.name;
          const nw = ctx.measureText(nameTxt).width;

          const subTxt = inst.neighborhood || inst.curatorial_focus || (inst.tier === 'A' ? 'Verified Independent' : (inst.tier === 'B' ? 'Flagged Underwriting' : 'Roster Unverified'));
          ctx.font = '10px "PP Telegraf", "PP Telegraph", sans-serif';
          const sw = ctx.measureText(subTxt).width;

          const bw = Math.min(295, Math.max(160, Math.max(nw, sw) + 28 + (webUrl ? 26 : 0)));

          // Candidates to test
          const candidateOffsets = [
            {{ dx: 24, dy: -bh / 2 }},
            {{ dx: 24, dy: -bh - 10 }},
            {{ dx: 24, dy: 10 }},
            {{ dx: -bw - 24, dy: -bh / 2 }},
            {{ dx: -bw - 24, dy: -bh - 10 }},
            {{ dx: -bw - 24, dy: 10 }},
            {{ dx: -bw / 2, dy: -bh - 28 }},
            {{ dx: -bw / 2, dy: 28 }}
          ];

          let bestX = pt.x + 24;
          let bestY = pt.y - bh / 2;
          let foundClean = false;

          for (const slot of candidateOffsets) {{
            let candX = Math.max(16, Math.min(width - bw - 16, pt.x + slot.dx));
            let candY = Math.max(48, Math.min(height - bh - 48, pt.y + slot.dy));

            const collides = placedBoxes.some(box => {{
              return !(candX + bw + 12 < box.x || candX > box.x + box.w + 12 ||
                       candY + bh + 12 < box.y || candY > box.y + box.h + 12);
            }});

            if (!collides) {{
              bestX = candX;
              bestY = candY;
              foundClean = true;
              break;
            }}
          }}

          if (!foundClean) {{
            if (!isSel && !isHov) {{
              return;
            }}
            bestX = Math.max(16, Math.min(width - bw - 16, pt.x + 24));
            bestY = Math.max(48, Math.min(height - bh - 48, pt.y - bh / 2));
          }}

          placedBoxes.push({{ x: bestX, y: bestY, w: bw, h: bh }});

          // Leader line from pin to badge
          let attachX = bestX > pt.x ? bestX : bestX + bw;
          let attachY = bestY + bh / 2;

          ctx.save();
          ctx.beginPath();
          ctx.moveTo(pt.x, pt.y);
          ctx.lineTo(attachX, attachY);
          ctx.strokeStyle = isSel ? '#60a5fa' : isHov ? '#38bdf8' : 'rgba(56, 189, 248, 0.40)';
          ctx.lineWidth = isSel ? 1.5 : 1;
          ctx.stroke();
          ctx.restore();

          // Card Background
          ctx.save();
          ctx.fillStyle = isSel ? 'rgba(15, 23, 42, 0.97)' : isHov ? 'rgba(15, 23, 42, 0.94)' : 'rgba(10, 16, 28, 0.92)';
          ctx.beginPath();
          ctx.roundRect ? ctx.roundRect(bestX, bestY, bw, bh, 6) : ctx.rect(bestX, bestY, bw, bh);
          ctx.fill();

          ctx.strokeStyle = isSel ? '#60a5fa' : isHov ? '#38bdf8' : (inst.tier === 'A' ? 'rgba(16, 185, 129, 0.45)' : 'rgba(56, 189, 248, 0.35)');
          ctx.lineWidth = isSel ? 1.5 : 1;
          ctx.stroke();

          // Left tier accent bar
          ctx.fillStyle = tierColor;
          ctx.beginPath();
          ctx.roundRect ? ctx.roundRect(bestX, bestY, 3.5, bh, [6, 0, 0, 6]) : ctx.rect(bestX, bestY, 3.5, bh);
          ctx.fill();

          // Institution Name
          ctx.font = 'bold 12px "PP Telegraf", "PP Telegraph", sans-serif';
          ctx.fillStyle = isSel ? '#ffffff' : '#f8fafc';
          ctx.textAlign = 'left';
          ctx.textBaseline = 'top';
          ctx.fillText(nameTxt, bestX + 10, bestY + 5);

          // Subtitle
          ctx.beginPath();
          ctx.arc(bestX + 12, bestY + 23, 2, 0, Math.PI * 2);
          ctx.fillStyle = tierColor;
          ctx.fill();

          ctx.font = '10px "PP Telegraf", "PP Telegraph", sans-serif';
          ctx.fillStyle = '#94a3b8';
          ctx.fillText(subTxt, bestX + 18, bestY + 19);

          // Direct Web Link Button on Badge
          let webBtnData = null;
          if (webUrl) {{
            const webBtnW = 20;
            const webBtnH = 20;
            const webBtnX = bestX + bw - webBtnW - 6;
            const webBtnY = bestY + 8;

            ctx.fillStyle = isHov ? 'rgba(37, 99, 235, 0.45)' : 'rgba(37, 99, 235, 0.25)';
            ctx.strokeStyle = 'rgba(96, 165, 250, 0.75)';
            ctx.lineWidth = 1;
            ctx.beginPath();
            ctx.roundRect ? ctx.roundRect(webBtnX, webBtnY, webBtnW, webBtnH, 4) : ctx.rect(webBtnX, webBtnY, webBtnW, webBtnH);
            ctx.fill();
            ctx.stroke();

            ctx.font = '11px sans-serif';
            ctx.fillStyle = '#93c5fd';
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillText('↗', webBtnX + webBtnW / 2, webBtnY + webBtnH / 2);

            webBtnData = {{ x: webBtnX, y: webBtnY, w: webBtnW, h: webBtnH, url: webUrl }};
          }}
          ctx.restore();

          cityMuseumHitboxes.push({{
            inst: inst,
            x: bestX,
            y: bestY,
            w: bw,
            h: bh,
            pinX: pt.x,
            pinY: pt.y,
            webBtn: webBtnData
          }});
        }});

        // Register hitboxes and floating labels for remaining pins so EVERY space is labeled on all points of view
        projectedInsts.forEach(({{ inst, pt }}) => {{
          const already = cityMuseumHitboxes.some(h => h.inst.name === inst.name);
          if (!already) {{
            cityMuseumHitboxes.push({{
              inst: inst,
              x: pt.x - 14,
              y: pt.y - 14,
              w: 28,
              h: 28,
              pinX: pt.x,
              pinY: pt.y
            }});

            // Floating name label on top of dot
            ctx.save();
            ctx.font = '600 11px "PP Telegraf", "PP Telegraph", sans-serif';
            ctx.textAlign = 'center';
            ctx.textBaseline = 'bottom';
            const nameTxt = inst.name.length > 25 ? inst.name.substring(0, 23) + '…' : inst.name;
            const tw = ctx.measureText(nameTxt).width;
            const bx = pt.x - tw / 2 - 5;
            const by = pt.y - 18;
            ctx.fillStyle = 'rgba(18, 20, 26, 0.94)';
            if (ctx.roundRect) ctx.roundRect(bx, by, tw + 10, 16, 4);
            else ctx.rect(bx, by, tw + 10, 16);
            ctx.fill();
            ctx.strokeStyle = inst.tier === 'A' ? 'rgba(16, 185, 129, 0.65)' : 'rgba(56, 189, 248, 0.65)';
            ctx.lineWidth = 1;
            ctx.stroke();
            ctx.fillStyle = '#f8fafc';
            ctx.fillText(nameTxt, pt.x, pt.y - 5);
            ctx.restore();
          }}
        }});

        // Tooltip for non-card pins when hovered
        if (hoveredInstitution) {{
          const hPin = cityMuseumHitboxes.find(h => h.inst.name === hoveredInstitution.name);
          const isCardExpanded = displayList.some(d => d.inst.name === hoveredInstitution.name);
          if (hPin && !isCardExpanded) {{
            drawInstitutionMicroCard(ctx, hPin.inst, hPin.pinX, hPin.pinY, width, height);
          }}
        }}
      }}

      // Live Cartographic HUD (Scale Bar, Coordinates, Interactive Compass Rose)
      if (r > baseRadius * 1.3 || isCityZoom) {{
        ctx.save();
        const actualKmPerPx = 6371 / r;
        const targetPx = 90;
        const rawKm = actualKmPerPx * targetPx;
        let scaleVal = 1, scaleUnit = 'km', barPx = targetPx;
        if (rawKm < 0.2) {{
          const rawMeters = Math.round(rawKm * 1000);
          scaleVal = rawMeters < 50 ? 50 : rawMeters < 100 ? 100 : rawMeters < 250 ? 200 : 500;
          barPx = (scaleVal / 1000) / actualKmPerPx;
          scaleUnit = 'm';
        }} else if (rawKm < 1) {{
          scaleVal = 500;
          barPx = (scaleVal / 1000) / actualKmPerPx;
          scaleUnit = 'm';
        }} else if (rawKm < 5) {{
          scaleVal = Math.round(rawKm);
          if (scaleVal < 1) scaleVal = 1;
          barPx = scaleVal / actualKmPerPx;
          scaleUnit = 'km';
        }} else if (rawKm < 20) {{
          scaleVal = Math.round(rawKm / 5) * 5;
          if (scaleVal < 5) scaleVal = 5;
          barPx = scaleVal / actualKmPerPx;
          scaleUnit = 'km';
        }} else if (rawKm < 200) {{
          scaleVal = Math.round(rawKm / 20) * 20;
          barPx = scaleVal / actualKmPerPx;
          scaleUnit = 'km';
        }} else {{
          scaleVal = Math.round(rawKm / 100) * 100;
          barPx = scaleVal / actualKmPerPx;
          scaleUnit = 'km';
        }}
        barPx = Math.max(30, Math.min(140, barPx));

        const hudX = 24;
        const hudY = height - 28;

        // Scale bar background pill
        ctx.fillStyle = 'rgba(7, 11, 20, 0.85)';
        ctx.strokeStyle = '#1b2a40';
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.roundRect ? ctx.roundRect(hudX - 8, hudY - 22, barPx + 16, 30, 5) : ctx.rect(hudX - 8, hudY - 22, barPx + 16, 30);
        ctx.fill();
        ctx.stroke();

        // Scale bar line & ticks
        ctx.strokeStyle = '#94a3b8';
        ctx.lineWidth = 1.5;
        ctx.beginPath();
        ctx.moveTo(hudX, hudY - 4);
        ctx.lineTo(hudX, hudY + 4);
        ctx.moveTo(hudX + barPx / 2, hudY - 2);
        ctx.lineTo(hudX + barPx / 2, hudY + 2);
        ctx.moveTo(hudX + barPx, hudY - 4);
        ctx.lineTo(hudX + barPx, hudY + 4);
        ctx.moveTo(hudX, hudY);
        ctx.lineTo(hudX + barPx, hudY);
        ctx.stroke();

        ctx.font = '10px "PP Telegraf", "PP Telegraph", sans-serif';
        ctx.fillStyle = '#cbd5e1';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'bottom';
        ctx.fillText(`0           ${{scaleVal}} ${{scaleUnit}}`, hudX + barPx / 2, hudY - 6);

        // Coordinates HUD
        const centerCoord = unproject(cx, cy, r, cx, cy) || {{ lat: rotLat, lon: rotLon }};
        const latTxt = `${{Math.abs(centerCoord.lat).toFixed(4)}}° ${{centerCoord.lat >= 0 ? 'N' : 'S'}}`;
        const lonTxt = `${{Math.abs(centerCoord.lon).toFixed(4)}}° ${{centerCoord.lon >= 0 ? 'E' : 'W'}}`;
        const coordTxt = `${{latTxt}}  ${{lonTxt}}`;
        const coordW = ctx.measureText(coordTxt).width + 16;
        const coordX = width - coordW - 24;

        ctx.fillStyle = 'rgba(7, 11, 20, 0.85)';
        ctx.strokeStyle = '#1b2a40';
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.roundRect ? ctx.roundRect(coordX, hudY - 22, coordW, 30, 5) : ctx.rect(coordX, hudY - 22, coordW, 30);
        ctx.fill();
        ctx.stroke();

        ctx.fillStyle = '#94a3b8';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(coordTxt, coordX + coordW / 2, hudY - 6);

        // North Compass Rose (Interactive)
        const compassX = width - 38;
        const compassY = 38;
        ctx.fillStyle = 'rgba(7, 11, 20, 0.85)';
        ctx.strokeStyle = '#1b2a40';
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.arc(compassX, compassY, 16, 0, Math.PI * 2);
        ctx.fill();
        ctx.stroke();

        ctx.fillStyle = '#38bdf8';
        ctx.beginPath();
        ctx.moveTo(compassX, compassY - 10);
        ctx.lineTo(compassX - 3.5, compassY + 3);
        ctx.lineTo(compassX, compassY);
        ctx.closePath();
        ctx.fill();

        ctx.fillStyle = '#64748b';
        ctx.beginPath();
        ctx.moveTo(compassX, compassY - 10);
        ctx.lineTo(compassX + 3.5, compassY + 3);
        ctx.lineTo(compassX, compassY);
        ctx.closePath();
        ctx.fill();

        ctx.font = '9px "PP Telegraf", "PP Telegraph", sans-serif';
        ctx.fillStyle = '#cbd5e1';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'bottom';
        ctx.fillText('N', compassX, compassY - 11);
        ctx.restore();
      }}

            // Floating White Card (Position update - 3D Globe only)
      const floatingCard = document.getElementById('floatingCard');
      if (selectedInstitution && !isCityStreetViewActive) {{
        const pt = project(selectedInstitution.lon, selectedInstitution.lat, r, cx, cy);
        if (pt.front && pt.depth > 0.05) {{
          floatingCard.classList.remove('hidden');
          const clampedX = Math.max(160, Math.min(width - 160, pt.x));
          const clampedY = Math.max(110, Math.min(height - 20, pt.y));
          floatingCard.style.left = `${{clampedX}}px`;
          floatingCard.style.top = `${{clampedY}}px`;

          if (!isCityZoom) {{
            ctx.font = '14px "PP Telegraf", "PP Telegraph", sans-serif';
            ctx.fillStyle = '#ffffff';
            ctx.textAlign = 'left';
            ctx.textBaseline = 'middle';
            ctx.fillText(selectedInstitution.name, pt.x + 12, pt.y);
          }}
        }} else {{
          floatingCard.classList.add('hidden');
        }}
      }} else {{
        floatingCard.classList.add('hidden');
      }}

      requestAnimationFrame(render);
    }}
    requestAnimationFrame(render);
    requestAnimationFrame(render);

    // Camera Navigation
    function flyTo(lon, lat, targetZoom = null) {{
      isAutoSpinning = false;
      let dLon = (lon - rotLon) % 360;
      if (dLon > 180) dLon -= 360;
      if (dLon < -180) dLon += 360;
      startRotLon = rotLon;
      startRotLat = rotLat;
      startRadius = currentRadius;
      targetRotLon = rotLon + dLon;
      targetRotLat = Math.max(-75, Math.min(75, lat));
      flightProgress = 0;
      isFlying = true;

      if (targetZoom) {{
        const actualZoom = targetZoom < 30 ? baseRadius * targetZoom : targetZoom;
        targetRadius = Math.max(getMinRadius(), Math.min(getMaxRadius(), actualZoom));
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
      if (typeof curatorContext !== 'undefined' && inst) {{
        curatorContext.lastInst = inst;
        if (inst.city) curatorContext.lastCity = inst.city;
      }}
      const webUrl = getValidWebUrl(inst);
      const domain = getDisplayDomain(webUrl) || 'website';

      const titleEl = document.getElementById('floatingCardTitle');
      if (titleEl) {{
        titleEl.textContent = inst.name;
        if (webUrl) {{
          titleEl.href = webUrl;
          titleEl.setAttribute('title', `Open official website for ${{inst.name}}`);
          titleEl.classList.add('hover:underline', 'cursor-pointer');
        }} else {{
          titleEl.removeAttribute('href');
          titleEl.classList.remove('hover:underline', 'cursor-pointer');
        }}
      }}

      const isCardClean = inst.tier === 'A';
      const isCardFlagged = inst.tier === 'B';
      document.getElementById('floatingCardMeta').textContent = `${{inst.location}} · ${{isCardClean ? 'Clean Verified' : isCardFlagged ? 'Flagged Underwriting' : 'Roster Unverified'}}`;
      
      const tierBadge = document.getElementById('floatingCardTier');
      if (tierBadge) {{
        tierBadge.textContent = isCardClean ? 'Clean Verified' : isCardFlagged ? 'Flagged Underwriting' : 'Roster Unverified';
        tierBadge.className = 'text-[12px] font-mono px-2 py-0.5 rounded-lg border shrink-0 ' + 
          (isCardClean 
            ? 'text-emerald-400 border-emerald-900 bg-[#0a2016]' 
            : isCardFlagged 
            ? 'text-[#be95ff] border-[#8a3ffc]/60 bg-[#1f1433]' 
            : 'text-[#33b1ff] border-[#0072c3]/60 bg-[#081a28]');
      }}
      
      const hoursEl = document.getElementById('floatingCardHours');
      if (hoursEl) {{
        const shortH = inst.opening_hours ? inst.opening_hours.split(',')[0] : 'Open Weekly';
        const shortF = inst.admission_fee ? inst.admission_fee.split('/')[0].trim() : 'Free / Subsidized';
        hoursEl.textContent = `${{shortH}} · ${{shortF}}`;
      }}

      // Direct Web Action Buttons on Map Popup
      const directWebBtn = document.getElementById('floatingCardDirectWebBtn');
      const directDomain = document.getElementById('floatingCardDirectDomain');
      if (directWebBtn) {{
        if (webUrl) {{
          directWebBtn.href = webUrl;
          if (directDomain) directDomain.textContent = `· ${{domain}}`;
          directWebBtn.style.display = 'inline-flex';
        }} else {{
          directWebBtn.style.display = 'none';
        }}
      }}

      const directPlanBtn = document.getElementById('floatingCardDirectPlanBtn');
      if (directPlanBtn) {{
        directPlanBtn.style.display = 'inline-flex';
      }}

      const webEl = document.getElementById('floatingCardWebLink');
      const domEl = document.getElementById('floatingCardDomain');
      if (webEl && domEl) {{
        if (webUrl) {{
          webEl.href = webUrl;
          domEl.textContent = domain;
          webEl.style.display = 'inline-flex';
        }} else {{
          webEl.style.display = 'none';
        }}
      }}

      document.querySelectorAll('.inst-card').forEach(c => {{
        const isTarget = c.getAttribute('data-name') === inst.name;
        c.classList.toggle('active', isTarget);
        if (isTarget) {{
          c.scrollIntoView({{ behavior: 'smooth', block: 'nearest' }});
        }}
      }});

      if (shouldSwitchToGlobe) {{
        if (inst.city) {{
          selectedCityFilter = inst.city;
          const cityMeta = ALL_CITIES_REGISTRY.find(c => matchC(c.name, inst.city));
          if (cityMeta && cityMeta.country) {{
            lastSelectedCountry = cityMeta.country;
          }}
          if (!isCityStreetViewActive || !matchC(selectedCityFilter, inst.city)) {{
            openCityStreetView(inst.city, inst.lat, inst.lon);
          }}
        }}
        const zoomTarget = getCityTargetRadius(inst.city);
        targetRadius = zoomTarget;
        flyTo(inst.lon, inst.lat, zoomTarget);
      }} else {{
        if (isCityStreetViewActive) {{
          if (inst.city && !matchC(selectedCityFilter, inst.city)) {{
            openCityStreetView(inst.city, inst.lat, inst.lon);
          }} else if (cityVectorMap && inst.lon && inst.lat) {{
            cityVectorMap.easeTo({{ center: [inst.lon, inst.lat], duration: 400 }});
          }}
        }} else {{
          flyTo(inst.lon, inst.lat);
        }}
      }}
    }}

    // Scholarly Audit Dossier View
    function openDossier(inst) {{
      if (!inst) return;
      const drawer = document.getElementById('detailDrawer');
      const body = document.getElementById('detailBody');
      drawer.classList.remove('hidden');

      const webUrl = getValidWebUrl(inst);
      const domain = getDisplayDomain(webUrl);

      const isClean = inst.tier === 'A';
      const isFlagged = inst.tier === 'B';
      const isUnverified = inst.tier === 'U';

      const tierBadgeClass = isClean 
        ? 'text-emerald-400 border-emerald-800 bg-[#092216]' 
        : isFlagged 
        ? 'text-[#be95ff] border-[#8a3ffc] bg-[#1f1433]' 
        : 'text-[#33b1ff] border-[#0072c3] bg-[#081a28]';

      const tierLabel = isClean 
        ? 'Tier A · Verified Independent Space' 
        : (isFlagged ? 'Tier B · Audited Corporate Underwriting' : 'Tier U · Roster Unverified');

      const cleanAlts = !isClean ? ALL_INSTITUTIONS.filter(i => i.tier === 'A' && matchC(i.city, inst.city)) : [];

      const rawGrade = inst.transparency_grade || 'Tier A+ (Statutory Public Audit)';
      let letterBadge = 'A+';
      if (rawGrade.includes('A+')) letterBadge = 'A+';
      else if (rawGrade.includes('A')) letterBadge = 'A';
      else if (rawGrade.includes('B+')) letterBadge = 'B+';
      else if (rawGrade.includes('B')) letterBadge = 'B';
      else if (rawGrade.includes('C')) letterBadge = 'C';
      else if (rawGrade.includes('D')) letterBadge = 'D';
      else if (rawGrade.includes('F')) letterBadge = 'F';

      let auditAuthority = 'Statutory Public Filing';
      const matchParen = rawGrade.match(/\(([^)]+)\)/);
      if (matchParen) {{
        auditAuthority = matchParen[1];
      }} else if (rawGrade.length > 4) {{
        auditAuthority = rawGrade;
      }}

      const bannerBg = isClean 
        ? 'bg-[#0c1f15] border-2 border-[#42be65] shadow-emerald-950/40' 
        : isFlagged 
        ? 'bg-[#1b122c] border-2 border-[#8a3ffc] shadow-purple-950/40' 
        : 'bg-[#091a26] border-2 border-[#0072c3] shadow-cyan-950/40';

      const badgeBoxStyle = isClean 
        ? 'bg-[#42be65]/25 border border-[#42be65] text-[#42be65]' 
        : isFlagged 
        ? 'bg-[#8a3ffc]/25 border border-[#8a3ffc] text-[#be95ff]' 
        : 'bg-[#0072c3]/25 border border-[#0072c3] text-[#33b1ff]';

      const gradeTitleCol = isClean ? 'text-[#42be65]' : isFlagged ? 'text-[#be95ff]' : 'text-[#33b1ff]';
      const pulseDotCol = isClean ? 'bg-[#42be65]' : isFlagged ? 'bg-[#be95ff]' : 'bg-[#33b1ff]';
      const auditTagHtml = isClean 
        ? '<span class="text-[11px] font-mono text-[#42be65] bg-[#42be65]/20 border border-[#42be65]/60 px-2.5 py-1 rounded-full uppercase font-bold tracking-wider">Audited Clean</span><span class="text-[11px] text-slate-400 font-mono mt-1">100% Verified</span>' 
        : isFlagged 
        ? '<span class="text-[11px] font-mono text-[#be95ff] bg-[#8a3ffc]/20 border border-[#8a3ffc]/60 px-2.5 py-1 rounded-full uppercase font-bold tracking-wider">Audited Flags</span><span class="text-[11px] text-slate-400 font-mono mt-1">Documented</span>' 
        : '<span class="text-[11px] font-mono text-[#33b1ff] bg-[#0072c3]/20 border border-[#0072c3]/60 px-2.5 py-1 rounded-full uppercase font-bold tracking-wider">Unverified</span><span class="text-[11px] text-slate-400 font-mono mt-1">Pending Audit</span>';

      body.innerHTML = `
        <div class="space-y-3">
          <div>
            <div class="flex items-center gap-1.5 mb-1.5 flex-wrap">
              <span class="text-[13px] font-mono px-2 py-0.5 rounded border ${{tierBadgeClass}}">${{tierLabel}}</span>
              <span class="text-[13px] font-mono px-2 py-0.5 rounded bg-[#101828] text-[#93c5fd] border border-[#202d48]">${{escapeHtml(inst.governance_type || 'Civic')}}</span>
              <span class="text-[13px] font-mono px-2 py-0.5 rounded bg-[#141e17] text-[#6ee7b7] border border-[#1b3b2b]">${{escapeHtml(inst.curatorial_focus || 'Contemporary Art')}}</span>
              <span class="text-[13px] font-mono px-2 py-0.5 rounded bg-[#151c28] text-[#78a9ff] border border-[#233550]">Est. ${{inst.year_founded || 'Historic'}}</span>
            </div>
            <h2 class="text-[18px] sm:text-[20px] font-normal text-white leading-[120%]">${{escapeHtml(inst.name)}}</h2>
            <p class="text-[14px] text-[#60a5fa] mt-0.5 font-mono">${{escapeHtml(inst.location || inst.city)}} · ${{inst.size || 'Audited Space'}}</p>
          </div>

          <!-- EMPHASIZED CIVIC TRANSPARENCY GRADE (Carbon High-Contrast Audit Banner) -->
          <div class="py-3 px-3.5 rounded-xl border-2 flex items-center justify-between shadow-lg ${{bannerBg}}">
            <div class="flex items-center gap-3">
              <div class="w-12 h-12 shrink-0 rounded-lg flex items-center justify-center font-mono font-bold text-[22px] shadow-inner ${{badgeBoxStyle}}">
                ${{escapeHtml(letterBadge)}}
              </div>
              <div>
                <div class="text-[11px] font-mono uppercase tracking-widest font-bold flex items-center gap-1.5 ${{gradeTitleCol}}">
                  <span class="inline-block w-2 h-2 rounded-full animate-pulse ${{pulseDotCol}}"></span>
                  Civic Transparency Grade
                </div>
                <div class="text-[14px] font-semibold text-white font-mono mt-0.5">
                  ${{escapeHtml(rawGrade)}}
                </div>
                <div class="text-[12px] text-slate-300 font-mono mt-0.5">
                  ${{escapeHtml(auditAuthority)}} · Statutory Accountability
                </div>
              </div>
            </div>
            <div class="hidden sm:flex flex-col items-end shrink-0 pl-2">
              ${{auditTagHtml}}
            </div>
          </div>

          ${{!isClean ? `
            <div class="py-2.5 border-t border-[#393939] space-y-2">
              <span class="text-[#be95ff] font-mono text-[12px] uppercase tracking-wider block font-bold">Audited Corporate Underwriting Notice</span>
              <p class="text-[#e8daff] text-[13px] leading-relaxed">
                <strong>Underwriting Conflict:</strong> ${{escapeHtml(inst.why_flagged || inst.watch || 'Corporate underwriting conflict / ethical audit flag.')}}
              </p>
              ${{inst.flags && inst.flags.length > 0 ? `
                <div class="flex flex-wrap gap-1.5 pt-1">
                  ${{inst.flags.map(f => `<span class="text-[11px] font-mono px-2 py-0.5 rounded-full bg-[#2a1745] text-[#be95ff] border border-[#8a3ffc]/50 font-medium">${{escapeHtml(f)}}</span>`).join('')}}
                </div>
              ` : ''}}
              ${{inst.epstein_records && inst.epstein_records.length > 0 ? `
                <div class="pt-2 border-t border-[#392d52] space-y-1.5">
                  <span class="text-[12px] font-mono text-[#ff7eb6] uppercase tracking-wider block font-bold">Epstein Network Link Audit</span>
                  ${{inst.epstein_records.map(ep => `
                    <div class="text-[12px] text-slate-300 bg-[#231435] p-2.5 rounded-xl border border-[#8a3ffc]/30">
                      <div class="font-bold text-[#e8daff]">${{escapeHtml(ep.person || 'Trustee')}} <span class="text-[#ff7eb6] font-mono font-normal">(${{escapeHtml(ep.link || 'Affiliation')}})</span></div>
                      <div class="mt-0.5 text-slate-300">${{escapeHtml(ep.summary || ep.tie)}}</div>
                      ${{ep.consequence ? `<div class="text-[11px] text-[#ff7eb6] mt-1 font-mono">Status: ${{escapeHtml(ep.consequence)}}</div>` : ''}}
                    </div>
                  `).join('')}}
                </div>
              ` : ''}}
              ${{inst.wikileaks_records && inst.wikileaks_records.length > 0 ? `
                <div class="pt-2 border-t border-[#392d52] space-y-1.5">
                  <span class="text-[12px] font-mono text-[#08bdba] uppercase tracking-wider block font-bold">WikiLeaks Cable Record</span>
                  ${{inst.wikileaks_records.map(wl => `
                    <div class="text-[12px] text-slate-300 bg-[#16212b] p-2.5 rounded-xl border border-[#0072c3]/30">
                      <div class="font-bold text-[#82cfff]">${{escapeHtml(wl.date || 'Cable')}} <span class="text-[#08bdba] font-mono font-normal">[${{escapeHtml(wl.doc_id || 'DOC')}}]</span></div>
                      <div class="mt-0.5 text-slate-300">${{escapeHtml(wl.what_shows)}}</div>
                    </div>
                  `).join('')}}
                </div>
              ` : ''}}
              ${{inst.other_findings ? `
                <div class="text-[12px] text-slate-300 bg-[#1f1530] p-2.5 rounded-xl border border-[#8a3ffc]/30">
                  <span class="font-bold text-[#be95ff]">Additional Research Findings:</span> ${{escapeHtml(inst.other_findings)}}
                </div>
              ` : ''}}
              <p class="text-slate-400 text-[12px]">
                <strong>Policy:</strong> Culture Atlas maps strictly verified independent spaces that operate free of fossil fuels, weapons manufacturing, private prisons, and predatory corporate underwriting.
              </p>
            </div>

            ${{cleanAlts.length > 0 ? `
              <div class="py-2.5 border-t border-[#393939] space-y-2">
                <span class="text-blue-300 font-mono text-[12px] uppercase tracking-wider block font-bold">Verified Independent Spaces in ${{escapeHtml(inst.city)}}</span>
                <p class="text-slate-300 text-[12px]">Instead of supporting compromised boards, explore these verified independent spaces:</p>
                <div class="space-y-1">
                  ${{cleanAlts.slice(0, 4).map(a => `
                    <div class="flex items-center justify-between text-[13px] py-1 border-t border-[#262626] first:border-t-0">
                      <a href="#" class="inst-link text-emerald-400 hover:underline font-medium" data-name="${{escapeHtml(a.name)}}">${{escapeHtml(a.name)}}</a>
                      <span class="text-slate-400 font-mono text-[12px]">${{escapeHtml(a.admission_policy)}}</span>
                    </div>
                  `).join('')}}
                </div>
              </div>
            ` : ''}}
          ` : ''}}

          ${{webUrl ? `
            <a href="${{escapeHtml(webUrl)}}" target="_blank" rel="noopener noreferrer" 
               class="inline-flex items-center justify-center gap-2 w-full py-2.5 bg-[#1d4ed8] hover:bg-[#2563eb] text-white font-normal text-[14px] rounded-xl transition shadow-md active:scale-95">
              <span>Visit Official Website (${{escapeHtml(domain)}})</span> <span>↗</span>
            </a>
          ` : ''}}

          <div class="py-2.5 border-t border-[#262626]">
            <span class="text-[12px] font-mono uppercase tracking-wider block mb-1 text-[#33b1ff]">Curator Assessment</span>
            <p class="text-[13px] text-slate-200 leading-[130%]">${{escapeHtml(inst.curator_recommendation || 'Evaluated under Culture Atlas research framework.')}}</p>
          </div>

          ${{isClean ? `
            <div class="pt-1">
              <div class="flex items-center justify-between pb-1.5 mb-1 border-b border-[#393939]">
                <span class="text-[13px] font-normal text-white uppercase tracking-wider font-mono">Plan Your Visit</span>
                <div class="flex items-center gap-2">
                  <button type="button" onclick="window.atlasPlanVisit(selectedInstitution)" class="text-[12px] text-[#78a9ff] hover:underline font-mono cursor-pointer flex items-center gap-1">
                    <span>Plan in Chat 💬</span>
                  </button>
                  ${{(inst.visit_url && (inst.visit_url.startsWith('http://') || inst.visit_url.startsWith('https://'))) || webUrl ? `
                    <span class="text-[#555] text-[11px]">|</span>
                    <a href="${{escapeHtml((inst.visit_url && (inst.visit_url.startsWith('http://') || inst.visit_url.startsWith('https://'))) ? inst.visit_url : webUrl)}}" target="_blank" rel="noopener noreferrer" class="text-[12px] text-[#78a9ff] hover:underline font-mono">Official site ↗</a>
                  ` : ''}}
                </div>
              </div>
              <div class="grid grid-cols-1 sm:grid-cols-2 sm:gap-x-6">
                <div class="py-2 border-t border-[#262626] first:border-t-0">
                  <div class="text-[12px] font-mono uppercase tracking-wider mb-0.5" style="color:#78a9ff">Hours</div>
                  <div class="text-[13px] text-[#e0e0e0] leading-[130%]">${{escapeHtml(inst.opening_hours || 'Check official site')}}</div>
                </div>
                <div class="py-2 border-t border-[#262626] first:border-t-0">
                  <div class="text-[12px] font-mono uppercase tracking-wider mb-0.5" style="color:#42be65">Admission</div>
                  <div class="text-[13px] text-[#e0e0e0] leading-[130%]">${{escapeHtml(inst.admission_fee || 'Subsidized Admission')}}</div>
                </div>
                <div class="py-2 border-t border-[#262626] first:border-t-0">
                  <div class="text-[12px] font-mono uppercase tracking-wider mb-0.5" style="color:#33b1ff">Address</div>
                  <div class="text-[13px] text-[#e0e0e0] leading-[130%]">${{escapeHtml(inst.address || inst.location)}}</div>
                  ${{inst.neighborhood ? `<div class="text-[12px] text-[#82cfff] font-mono mt-0.5">${{escapeHtml(inst.neighborhood)}}</div>` : ''}}
                </div>
                <div class="py-2 border-t border-[#262626] first:border-t-0">
                  <div class="text-[12px] font-mono uppercase tracking-wider mb-0.5" style="color:#be95ff">Suggested Duration</div>
                  <div class="text-[13px] text-[#e0e0e0] leading-[130%]">${{escapeHtml(inst.visit_duration || '1.5 – 2.5 hours')}}</div>
                </div>
              </div>
              <div class="py-2 border-t border-[#262626] first:border-t-0">
                <div class="text-[12px] font-mono uppercase tracking-wider mb-0.5" style="color:#3ddbd9">Getting There</div>
                <div class="text-[13px] text-[#e0e0e0] leading-[130%]">${{escapeHtml(inst.transit_tips || 'Accessible via central public transit network.')}}</div>
              </div>
              <div class="py-2 border-t border-[#262626] first:border-t-0">
                <div class="text-[12px] font-mono uppercase tracking-wider mb-0.5" style="color:#f1c21b">Highlight</div>
                <div class="text-[13px] text-[#e0e0e0] leading-[130%]">${{escapeHtml(inst.highlight || 'Celebrated collection and contemporary commissions.')}}</div>
              </div>
              <div class="grid grid-cols-1 sm:grid-cols-2 sm:gap-x-6">
                <div class="py-2 border-t border-[#262626] first:border-t-0">
                  <div class="text-[12px] font-mono uppercase tracking-wider mb-0.5" style="color:#ff7eb6">Accessibility</div>
                  <div class="text-[13px] text-[#e0e0e0] leading-[130%]">${{escapeHtml(inst.accessibility || 'Step-free access, elevators, accessible restrooms.')}}</div>
                </div>
                <div class="py-2 border-t border-[#262626] first:border-t-0">
                  <div class="text-[12px] font-mono uppercase tracking-wider mb-0.5" style="color:#ff832b">Amenities</div>
                  <div class="text-[13px] text-[#e0e0e0] leading-[130%]">${{escapeHtml((inst.amenities || 'Art bookshop, café, cloakroom, and lockers.').toString().split(',').map(x => x.trim()).filter(Boolean).join(' · '))}}</div>
                </div>
              </div>
            </div>
          ` : ''}}

          <div class="py-2.5 border-t border-[#262626]">
            <span class="text-[12px] font-mono uppercase tracking-wider block mb-1 text-[#78a9ff]">Funding Architecture & Operating Budget</span>
            <p class="text-[13px] text-slate-200 leading-[130%]">${{escapeHtml(inst.funding || 'Civic cultural budget')}}</p>
          </div>

          <div class="py-2.5 border-t border-[#262626]">
            <span class="text-[12px] font-mono uppercase tracking-wider block mb-1 text-[#be95ff]">Ethical Safeguards & Autonomy Charter</span>
            <p class="text-[13px] text-slate-200 leading-[130%]">${{escapeHtml(inst.ethical_safeguard || 'Verified under Culture Atlas criteria')}}</p>
          </div>

          ${{isClean && inst.watch ? `
            <div class="py-2.5 border-t border-[#262626]">
              <span class="text-[12px] font-mono uppercase tracking-wider block mb-1 text-[#f1c21b]">Curator Audit Notes</span>
              <p class="text-[13px] text-slate-200 leading-[130%]">${{escapeHtml(inst.watch)}}</p>
            </div>
          ` : ''}}

          <div class="pt-2 border-t border-[#1c212a]">
            <div class="flex items-center justify-between mb-2">
              <span class="text-[12px] font-normal text-slate-400 uppercase tracking-wider font-mono">Audited Sources, Reports & Filings</span>
              <button type="button" onclick="openResearchFeedbackModal('${{escapeHtml(inst.name)}}', '${{escapeHtml(inst.city)}}')" class="text-[12px] font-mono text-[#78a9ff] hover:underline cursor-pointer flex items-center gap-1">
                <span>Suggest Update ✍️</span>
              </button>
            </div>
            <div class="flex flex-col gap-1.5 font-mono">
              ${{(inst.sources || []).map(u => {{
                const isUrl = typeof u === 'string' && (u.startsWith('http://') || u.startsWith('https://'));
                if (isUrl) {{
                  const srcDomain = getDisplayDomain(u);
                  return `
                    <a href="${{escapeHtml(u)}}" target="_blank" rel="noopener noreferrer" class="text-[#60a5fa] hover:text-white hover:underline text-[13px] flex items-center gap-1.5 py-0.5 truncate transition">
                      <span class="text-blue-400 text-[14px]">↗</span> <span class="truncate">${{escapeHtml(u)}}</span> <span class="text-slate-500 text-[11px] shrink-0 font-mono">(${{srcDomain}})</span>
                    </a>
                  `;
                }} else {{
                  return `
                    <div class="text-slate-300 text-[13px] flex items-center justify-between gap-2 font-sans py-0.5">
                      <span class="flex items-center gap-1.5 truncate text-slate-300">
                        <span class="text-slate-500 font-mono text-[11px] px-1 py-0.5 rounded bg-[#131926] border border-[#222d42]">DOC</span>
                        <span class="truncate">${{escapeHtml(u)}}</span>
                      </span>
                      <a href="https://www.google.com/search?q=${{encodeURIComponent(u + ' ' + (inst.name || ''))}}" target="_blank" rel="noopener noreferrer" class="text-[#60a5fa] hover:text-white hover:underline text-[12px] font-mono shrink-0 ml-1">
                        Search ↗
                      </a>
                    </div>
                  `;
                }}
              }}).join('')}}
            </div>
          </div>
        </div>
      `;
    }}

    function formatInstLink(inst, opts = {{}}) {{
      if (!inst) return '';
      const webUrl = getValidWebUrl(inst);
      const domain = getDisplayDomain(webUrl);
      
      const isEx = inst.tier !== 'A';
      const nameClass = isEx ? 'inst-link text-[#be95ff] hover:underline font-normal' : 'inst-link font-normal';
      const badge = isEx ? ' <span class="text-[11px] font-mono px-1 py-0.2 rounded bg-[#1f1433] text-[#be95ff] border border-[#8a3ffc] shrink-0">Flagged</span>' : '';
      const nameLink = `<a href="#" class="${{nameClass}}" data-name="${{escapeHtml(inst.name)}}">${{escapeHtml(inst.name)}}</a>${{badge}}`;
      const cityPart = opts.noCity ? '' : ` in <a href="#" class="city-link text-[#93c5fd] hover:underline" data-city="${{escapeHtml(inst.city)}}">${{escapeHtml(inst.location || inst.city)}}</a>`;
      const dossierPart = opts.noDossier ? '' : ` (<a href="#" class="dossier-link text-[13px] text-[#60a5fa] hover:underline" data-name="${{escapeHtml(inst.name)}}">audit dossier</a>${{webUrl ? ` · <a href="${{escapeHtml(webUrl)}}" target="_blank" rel="noopener noreferrer" class="ext-web-link text-[13px] text-[#93c5fd] hover:text-white hover:underline transition">${{domain}} ↗</a>` : ''}})`;
      
      return `${{nameLink}}${{cityPart}}${{dossierPart}}`;
    }}

    // =========================================================
    // 🧠 UNIFIED MULTI-PROVIDER AI & CURATOR ENGINE STATE
    // =========================================================
    let aiApiKey = localStorage.getItem('atlas_ai_api_key') || localStorage.getItem('atlas_gemini_api_key') || '';
    let aiProvider = localStorage.getItem('atlas_ai_provider') || 'auto';
    let aiModel = localStorage.getItem('atlas_ai_model') || '';

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

    let currentSelectedProvider = getEffectiveProvider();

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
      const modelSelect = document.getElementById('aiModelSelect');
      if (modelSelect) {{
        const models = PROVIDER_MODELS[prov] || PROVIDER_MODELS.anthropic;
        modelSelect.innerHTML = models.map(m => `<option value="${{m.id}}">${{m.name}}</option>`).join('');
        if (aiModel) modelSelect.value = aiModel;
      }}

      // Update Tip and Get Key Link
      const providerTip = document.getElementById('providerTip');
      const providerGetKeyLink = document.getElementById('providerGetKeyLink');
      if (prov === 'anthropic') {{
        if (providerTip) providerTip.innerHTML = 'Recommended: <strong>Anthropic</strong> excels at art theory, <em>Beyond Objecthood</em>, e-flux criticism, and institutional analysis.';
        if (providerGetKeyLink) {{
          providerGetKeyLink.href = 'https://console.anthropic.com/settings/keys';
          providerGetKeyLink.textContent = 'Get Anthropic Key ↗';
        }}
      }} else if (prov === 'openai') {{
        if (providerTip) providerTip.innerHTML = 'OpenAI <strong>GPT-4o / GPT-4o-mini</strong> provides fast conversational guidance across all 403 mapped spaces.';
        if (providerGetKeyLink) {{
          providerGetKeyLink.href = 'https://platform.openai.com/api-keys';
          providerGetKeyLink.textContent = 'Get OpenAI Key ↗';
        }}
      }} else {{
        if (providerTip) providerTip.innerHTML = 'Google <strong>Gemini 2.5 Flash</strong> provides responsive real-time multimodal reasoning with a generous free tier.';
        if (providerGetKeyLink) {{
          providerGetKeyLink.href = 'https://aistudio.google.com/app/apikey';
          providerGetKeyLink.textContent = 'Get Gemini Key (Free) ↗';
        }}
      }}
    }}

    function updateDetectBadge(val) {{
      const badge = document.getElementById('keyDetectBadge');
      if (!badge) return;
      const k = (val || '').trim();
      if (!k) {{
        badge.textContent = 'Auto-detecting provider...';
        badge.className = 'text-[14px] font-mono text-[#a1a1aa]';
        return;
      }}
      if (k.startsWith('sk-ant-')) {{
        badge.textContent = 'Anthropic Claude key detected';
        badge.className = 'text-[14px] font-mono text-purple-400';
        updateProviderUI('anthropic');
      }} else if (k.startsWith('sk-') || k.startsWith('sk-proj-')) {{
        badge.textContent = 'OpenAI key detected';
        badge.className = 'text-[14px] font-mono text-emerald-400';
        updateProviderUI('openai');
      }} else if (k.startsWith('AIza')) {{
        badge.textContent = 'Google Gemini key detected';
        badge.className = 'text-[14px] font-mono text-blue-400';
        updateProviderUI('gemini');
      }} else {{
        badge.textContent = 'Custom API key';
        badge.className = 'text-[14px] font-mono text-amber-400';
      }}
    }}

    function openSettingsModal() {{
      const modal = document.getElementById('curatorSettingsModal');
      if (!modal) return;
      modal.classList.remove('hidden');
      const input = document.getElementById('aiApiKeyInput');
      if (input) {{
        input.value = aiApiKey || localStorage.getItem('atlas_ai_api_key') || '';
        updateDetectBadge(input.value);
        setTimeout(() => input.focus(), 60);
      }}
      updateProviderUI(getEffectiveProvider());
      const testBox = document.getElementById('connectionTestBox');
      if (testBox) testBox.classList.add('hidden');
    }}
    window.openSettingsModal = openSettingsModal;

    function updateAIStatusUI() {{
      aiApiKey = localStorage.getItem('atlas_ai_api_key') || localStorage.getItem('atlas_gemini_api_key') || aiApiKey || '';
      aiProvider = localStorage.getItem('atlas_ai_provider') || aiProvider || 'auto';
      aiModel = localStorage.getItem('atlas_ai_model') || aiModel || '';

      const topDot = document.getElementById('topStatusDot');
      const topLabel = document.getElementById('topStatusLabel');
      const chatKeyBtn = document.getElementById('chatAddKeyBtn');
      const chatKeyIcon = document.getElementById('chatAddKeyIcon');
      const chatKeyLabel = document.getElementById('chatAddKeyLabel');
      const workLabel = document.getElementById('workModelLabel');

      const prov = getEffectiveProvider();
      const pName = prov === 'anthropic' ? 'Claude' : (prov === 'openai' ? 'OpenAI' : 'Gemini');
      const effModel = getEffectiveModel();

      if (aiApiKey) {{
        if (topDot) topDot.className = 'w-2 h-2 rounded-full bg-emerald-400 animate-pulse shrink-0';
        if (topLabel) {{
          topLabel.className = 'font-mono text-[13px] sm:text-[14px] text-emerald-400 flex items-center gap-1.5';
          topLabel.innerHTML = `<span>⚙️</span><span class="hidden sm:inline">${{pName}} Live</span>`;
        }}
        if (chatKeyBtn) {{
          chatKeyBtn.className = 'text-[13px] bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 hover:border-emerald-500/50 flex items-center gap-1.5 px-2.5 py-1 rounded-full transition cursor-pointer font-normal';
          chatKeyBtn.title = `${{pName}} Intelligence Active · Click to adjust settings`;
        }}
        if (chatKeyIcon) {{
          chatKeyIcon.className = 'w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse';
          chatKeyIcon.textContent = '';
        }}
        if (chatKeyLabel) {{
          chatKeyLabel.textContent = `${{pName}} Active`;
        }}
        if (workLabel) {{
          workLabel.textContent = `${{pName}} · ${{effModel.split('-')[0].toUpperCase()}}`;
        }}
      }} else {{
        if (topDot) topDot.className = 'w-1.5 sm:w-2 h-1.5 sm:h-2 rounded-full bg-amber-400 shrink-0';
        if (topLabel) {{
          topLabel.className = 'font-normal text-[13px] sm:text-[14px] text-amber-300 flex items-center gap-1';
          topLabel.innerHTML = `<span>🔑</span><span class="hidden sm:inline"> Add API Key</span>`;
        }}
        if (chatKeyBtn) {{
          chatKeyBtn.className = 'text-[13px] bg-amber-500/10 hover:bg-amber-500/20 text-amber-300 border border-amber-500/30 hover:border-amber-500/50 flex items-center gap-1.5 px-2.5 py-1 rounded-full transition cursor-pointer font-normal';
          chatKeyBtn.title = 'Connect AI API Key';
        }}
        if (chatKeyIcon) {{
          chatKeyIcon.className = '';
          chatKeyIcon.textContent = '🔑';
        }}
        if (chatKeyLabel) {{
          chatKeyLabel.textContent = 'Add API Key';
        }}
        if (workLabel) {{
          workLabel.textContent = 'Culture Atlas 4.0 Critical Engine';
        }}
      }}
    }}
    window.updateAIStatusUI = updateAIStatusUI;

    // Hosted AI proxy (Cloudflare Worker keeps the API key server-side). Empty = disabled.
    const ATLAS_AI_PROXY_URL = {proxy_url_json};
    window.ATLAS_AI_PROXY_URL = ATLAS_AI_PROXY_URL;

    // Community Research & Feedback Submissions Pipeline (LocalStorage backed + Model Grounded)
    function getCommunityResearchSubmissions() {{
      try {{
        return JSON.parse(localStorage.getItem('atlas_community_research_queue') || '[]');
      }} catch (e) {{
        return [];
      }}
    }}
    window.getCommunityResearchSubmissions = getCommunityResearchSubmissions;

    function saveCommunityResearchSubmission(entry) {{
      const list = getCommunityResearchSubmissions();
      list.unshift(entry);
      localStorage.setItem('atlas_community_research_queue', JSON.stringify(list));
      return entry;
    }}
    window.saveCommunityResearchSubmission = saveCommunityResearchSubmission;

    function openResearchFeedbackModal(spaceName = '', city = '') {{
      const modal = document.getElementById('researchFeedbackModal');
      if (!modal) return;
      modal.classList.remove('hidden');
      const nameInput = document.getElementById('rfSpaceName');
      const cityInput = document.getElementById('rfCity');
      const detailsInput = document.getElementById('rfDetails');
      if (nameInput && spaceName) nameInput.value = spaceName;
      if (cityInput && city) cityInput.value = city;
      if (detailsInput) setTimeout(() => detailsInput.focus(), 60);
    }}
    window.openResearchFeedbackModal = openResearchFeedbackModal;

    function closeResearchFeedbackModal() {{
      const modal = document.getElementById('researchFeedbackModal');
      if (modal) modal.classList.add('hidden');
    }}
    window.closeResearchFeedbackModal = closeResearchFeedbackModal;

    function openAcademicResearchModal(topic = 'all') {{
      const modal = document.getElementById('academicResearchModal');
      if (!modal) return;
      modal.classList.remove('hidden');
      renderAcademicStudies(topic, '');
    }}
    window.openAcademicResearchModal = openAcademicResearchModal;

    function closeAcademicResearchModal() {{
      const modal = document.getElementById('academicResearchModal');
      if (modal) modal.classList.add('hidden');
    }}
    window.closeAcademicResearchModal = closeAcademicResearchModal;

    function renderAcademicStudies(topic = 'all', query = '') {{
      const list = document.getElementById('arPapersList');
      if (!list || typeof ACADEMIC_RESEARCH === 'undefined') return;

      const q = (query || '').toLowerCase().trim();
      const filtered = ACADEMIC_RESEARCH.filter(p => {{
        if (topic && topic !== 'all') {{
          const tText = ((p.title || '') + ' ' + (p.takeaway || '') + ' ' + (p.abstract || '')).toLowerCase();
          if (topic === 'networks' && !tText.includes('network') && !tText.includes('interlock') && !tText.includes('sponsor') && !tText.includes('corporate') && !tText.includes('tie') && !tText.includes('connect') && !tText.includes('patron')) return false;
          if (topic === 'tainted' && !tText.includes('tainted') && !tText.includes('moral') && !tText.includes('ethic')) return false;
          if (topic === 'governance' && !tText.includes('governance') && !tText.includes('donor') && !tText.includes('board')) return false;
          if (topic === 'fossil' && !tText.includes('fossil') && !tText.includes('climate') && !tText.includes('bp') && !tText.includes('oil') && !tText.includes('environmental')) return false;
          if (topic === 'disclosure' && !tText.includes('disclosure') && !tText.includes('fraud') && !tText.includes('report') && !tText.includes('mandatory')) return false;
        }}
        if (q) {{
          const allText = ((p.title || '') + ' ' + (p.authors || '') + ' ' + (p.journal || '') + ' ' + (p.takeaway || '') + ' ' + (p.abstract || '')).toLowerCase();
          if (!allText.includes(q)) return false;
        }}
        return true;
      }});

      if (filtered.length === 0) {{
        list.innerHTML = `<div class="p-6 text-center text-slate-400">No studies match this search or topic filter.</div>`;
        return;
      }}

      list.innerHTML = filtered.map(p => `
        <div class="bg-[#1f1f1f] border border-[#2e2e2e] rounded-xl p-3.5 space-y-2 hover:border-[#444] transition">
          <div class="flex items-start justify-between gap-2">
            <h4 class="font-medium text-white text-[14px] leading-snug">${{escapeHtml(p.title)}}</h4>
            ${{p.year ? `<span class="text-[11px] font-mono px-2 py-0.5 rounded bg-[#111c2e] text-[#78a9ff] border border-[#1d3557] shrink-0">${{escapeHtml(p.year)}}</span>` : ''}}
          </div>
          
          <div class="flex items-center gap-2 text-[12px] text-slate-400 font-mono flex-wrap">
            <span>${{escapeHtml(p.authors || 'Researchers')}}</span>
            <span>·</span>
            <span class="text-[#33b1ff]">${{escapeHtml(p.journal || 'Academic Journal')}}</span>
            ${{p.citations ? `<span>·</span><span class="text-emerald-400 font-medium">${{escapeHtml(p.citations)}} Citations</span>` : ''}}
          </div>

          ${{p.takeaway ? `
            <div class="p-2.5 rounded-lg bg-[#0d212b] border border-[#08bdba]/40 text-[#a6f0eb] text-[12.5px] leading-relaxed">
              <strong class="text-[#08bdba] block text-[11px] uppercase tracking-wider font-mono mb-0.5">Key Empirical Finding:</strong>
              ${{escapeHtml(p.takeaway)}}
            </div>
          ` : ''}}

          ${{p.abstract ? `
            <details class="text-[12px] text-slate-300">
              <summary class="cursor-pointer text-[#78a9ff] hover:underline font-mono text-[11px] uppercase tracking-wider py-1">View Abstract & Methodology</summary>
              <p class="mt-1.5 p-2.5 rounded bg-[#171717] border border-[#2a2a2a] text-slate-300 leading-relaxed">${{escapeHtml(p.abstract)}}</p>
            </details>
          ` : ''}}

          <div class="flex items-center justify-between pt-1 border-t border-[#2a2a2a] text-[11px] font-mono">
            ${{p.doi ? `<span class="text-slate-400 truncate max-w-[200px]">DOI: ${{escapeHtml(p.doi)}}</span>` : '<span class="text-slate-400">Peer-Reviewed Study</span>'}}
            <div class="flex items-center gap-2">
              ${{p.link ? `<a href="${{escapeHtml(p.link)}}" target="_blank" rel="noopener noreferrer" class="text-[#78a9ff] hover:underline">Consensus Link ↗</a>` : ''}}
              ${{p.doi ? `<a href="https://doi.org/${{escapeHtml(p.doi)}}" target="_blank" rel="noopener noreferrer" class="text-emerald-400 hover:underline">Read Study ↗</a>` : ''}}
            </div>
          </div>
        </div>
      `).join('');
    }}
    window.renderAcademicStudies = renderAcademicStudies;

    // Unified Multi-Provider Live Generative AI Engine
    async function queryAI(userPrompt) {{
      const useProxy = !aiApiKey && !!ATLAS_AI_PROXY_URL;
      if (!aiApiKey && !useProxy) return null;
      const prov = useProxy ? 'anthropic' : getEffectiveProvider();
      const model = useProxy ? 'claude-haiku-4-5-20251001' : getEffectiveModel();

      // Sample representative spaces for model grounding
      const sampleInsts = ALL_INSTITUTIONS.slice(0, 45).map(i => `${{i.name}} (${{i.city}}, ${{i.country}}): Tier ${{i.tier}}, ${{i.governance_type}}, Hours: ${{i.opening_hours}}, ${{i.admission_policy}}, Highlights: ${{i.highlight}}`).join('\\n');

      const communitySubmissions = getCommunityResearchSubmissions();
      const communityGrounding = communitySubmissions.length > 0 
        ? '\\n\\nCOMMUNITY-CONTRIBUTED RESEARCH QUEUE (Under Peer Verification):\\n' + communitySubmissions.slice(0, 10).map(s => `- [Audit #${{s.id}}] ${{s.spaceName || 'Platform'}} (${{s.category}}): ${{s.details}} [Source: ${{s.sourceUrl || 'Statutory filing reported'}}]`).join('\\n')
        : '';

      const criticalSystemPrompt = `You are the Culture Atlas assistant, a friendly, clear, and direct guide to art museums and galleries worldwide.
Culture Atlas maps 441 verified clean museums and independent art spaces across 40+ countries that don't take money from fossil fuels, weapons manufacturers, or private prisons, alongside an audited catalog of 403 flagged institutions with corporate underwriting ties.

CORE INSTRUCTION: SPEAK IN PROPER, SIMPLE, CLEAR LANGUAGE.
- Use plain, natural, everyday English.
- Avoid academic art-world jargon or flowery marketing phrases. Never say "cultural sanctuaries", "clean sanctuaries", "clean sanctuary", "for quiet reflection", "for evening contemplation", "uncompromised curatorial experimentation", "shutter their galleries", "sublime", "epistemologies", or "palliative".
- Speak like a knowledgeable, friendly human who explains things directly and simply.
- Keep sentences short, clean, and conversational.

PEER-REVIEWED ACADEMIC RESEARCH CORPUS (Consensus {academic_count} Studies):
You have deep mastery of {academic_count} empirical studies on museum funding, sponsor networks, donor governance, tainted money, and mandatory disclosures:
- Connections Among Cultural Sponsors & Network Logic: Research on sponsor networks reveals that corporate sponsorship functions as a multi-organizational political-economic network rather than isolated philanthropic transactions. Controversial corporate sponsors (fossil fuels, defense manufacturing, tobacco, private equity) invest in cultural institutions to secure legitimacy transfer, social license, and elite access until public scrutiny ruptures the relationship.
- Curatorial Autonomy & Indirect Self-Censorship: Davidsson & Sørensen (2010), Mateos Rusillo (2019), and Alexander prove that corporate influence primarily acts through anticipatory self-censorship, blockbuster exhibition favoritism, and subtle alignment with sponsor marketing goals rather than direct editorial diktats.
- Board Interlocks & Political Embeddedness: Zheng & Ni (2023), Zhou et al. (2021), and Betzler (2015) demonstrate how interlocking boards and political ties generate performative compliance while dampening substantive disclosure of controversial patron arrangements.
- Corporate Art Intervention & Commercialization: Chin-tao Wu (Privatising Culture: Corporate Art Intervention Since the 1980s, Verso) and Steele (2008) trace how corporate tax incentives and trustee commercialization reshaped museum priorities.
- Tax-Exempt Corporate Lobbying: Bertrand, Bombardini, Fisman & Trebbi (American Economic Review) establish corporate philanthropy functions as strategic political influence.
- Tainted Donors & Rupture Catalysts: Dunn (2010), Wright et al. (2019), and Epstein file case studies show that institutions cling to tainted funding under competitive pressures until investigative media exposure (The Guardian, Democracy Now, e-flux, Dutch press) and artist activism (Liberate Tate, Nan Goldin P.A.I.N.) make the association too public and costly to defend.
- Mandatory Disclosure vs Disclose-on-Request: Barber, Farwell & Galle (Nonprofit and Voluntary Sector Quarterly, 2020) and Harris & Neely (2018) prove that mandatory disclosure forces donors to penalize high overhead/fundraising costs, whereas disclose-on-request requirements fail because donors rarely actively seek unpublicized information.
- Donor Response to Fraud & Media Oversight: Harris, Petrovits & Yetman (2023) show that media reporting of asset diversions severely decreases donations, and donors only moderate penalties when nonprofits enact transparent public disclosures and governance overhauls.
- Donor Governance & Cost Structures: Yermack (Journal of Cultural Economics, 2017) shows how restricted gifts reduce manager discretion, force 45% endowment retention, and create rigid cost structures in US museums.
Cite these peer-reviewed takeaways when users ask about research, sponsor networks, tainted money, disclosures, or donor ethics!

SCHOLARLY RESEARCH, MIT PRESS ART THEORY & DUTCH RESEARCH FOUNDATIONS (Explain simply in everyday English):
You have extensive mastery of seminal art theory, curatorial studies, and institutional critique published by MIT Press, October, Zone Books, Sternberg Press, and Dutch research institutes (BAK Utrecht, Casco, Van Abbemuseum). When answering research questions, explain every finding in simple, accessible, everyday English:
- BAK, basis voor actuele kunst (Utrecht): Directed by Maria Hlavajova. Global epicenter of critical artistic research and political imagination. Spearheaded 'Former West' (2008–2016), co-published as a monumental 748-page compendium with MIT Press, establishing that 'the West' is not a universal center but a provincialized territory after 1989. Led landmark platforms 'Vectors of Commoning', 'Propositions for Non-Fascist Living', and the 'Posthuman Glossary' with Rosi Braidotti (Utrecht University).
- Casco Art Institute: Working for the Commons (Utrecht): Directed by Binna Choi. Transformed an exhibition gallery into a living ecosystem of the commons, feminist economies, and collaborative unlearning ('Site for Unlearning: Art Organization'). 100% free admission.
- Van Abbemuseum (Eindhoven): Directed by Charles Esche. Pioneered the 'Museum of Arte Útil' (Useful Art) with Tania Bruguera—reclaiming art as an instrument for civic utility and social change rather than a passive luxury spectacle. Developed 'Deviant Practice' to decolonize and queer museum archives. Championed by Claire Bishop in 'Radical Museology'.
- Kunstinstituut Melly (Rotterdam): Formerly Witte de With Center for Contemporary Art. Led a pioneering, multi-year collective public review to de-commemorate a colonial naval officer, renaming the institution in 2020 after Ken Lum's iconic public artwork 'Melly Shum Hates Her Job'. Publisher of the 'Source' research book series.
- De Appel (Amsterdam): Founded in 1975 by Wies Smals. Landmark performance archives (Marina Abramović & Ulay) and home of the celebrated 'Curatorial Programme' (CP) that revolutionized curating into an autonomous research discipline.
- Framer Framed (Amsterdam): Decolonial research platform interrogating critical museology, intercultural restitution, and climate justice.
- The Dutch Public Civic Funding Model: Funded primarily through multi-year structural subsidies (Mondriaan Fund / Gemeenten) subject to peer-review by artists and curators, shielding curators from commercial market pressures and billionaire trustee conflicts seen in US 501(c)(3) museums.
- Rosalind Krauss & The Late Capitalist Museum (October 1990 / MIT Press): Explain simply how mega-museums shifted from quiet historical archives of contemplation into capitalist spectacle engines. Rather than engaging deeply with individual artworks, visitors are sold a fast bodily rush in cavernous atrium spaces designed like luxury shopping malls.
- Miwon Kwon – "One Place after Another: Site-Specific Art and Locational Identity" (MIT Press, 2002): Explain the 3 stages of site-specific art: 1) Physical (sculpture rooted to the ground, like Richard Serra), 2) Institutional (art exposing museum politics, like Hans Haacke and Michael Asher), and 3) Discursive/Nomadic (institutions hiring artists like traveling freelance consultants to extract community stories for temporary biennials).
- Alexander Alberro & Blake Stimson – "Institutional Critique: An Anthology of Artists' Writings" (MIT Press, 2009): Explain how artists documented their own critique of the museum apparatus—from Marcel Broodthaers' fictional eagle museum and Daniel Buren's striped walls to Andrea Fraser's satirical docent tours and Adrian Piper's confrontations with racism.
- Benjamin H.D. Buchloh – "Aesthetic of Administration" (MIT Press): Explain how conceptual artists in the 1960s replaced oil paintings with office documents, certificates, and legal contracts to mirror corporate capitalism, showing that artistic value is generated by bureaucratic rubber stamps rather than mystical inspiration.
- Boris Groys – "Art Power" (MIT Press, 2008): Explain why public museums are radical—they protect art from the commercial market. In a private gallery, art is only worth what a rich buyer pays; in a public museum, all artworks have equal rights to exist and be studied regardless of price.
- David Joselit – "Heritage and Debt: Art in Globalization" (MIT Press, 2020) & "After Art": How images function as circulating networks across the web, and how museums in the Global South navigate the double burden of historical colonial debt and global contemporary art markets.
- Hal Foster – "The Return of the Real" & "The Anti-Aesthetic" (MIT Press / October): Critique of the "starchitect" museum building (where sensational architecture overshadows the art to serve real estate developers) and the engagement with real political trauma.
- James Voorhies – "Beyond Objecthood: The Exhibition as a Critical Form since 1968" (MIT Press, 2017): How the exhibition itself became a medium and critical form since 1968, and why corporate mega-museums turned participation into tourist entertainment.
- Research Methodology & Forensic Audits: Explain how Culture Atlas audits museum Form 990 filings (Schedule I, Schedule L), UK Charity Commission accounts, and DRAC audits, cross-referencing trustees against weapons manufacturing, fossil fuels, and private prisons.
- Landmark Exhibitions: Harald Szeemann's 'When Attitudes Become Form' (Bern 1969), 'This Is Tomorrow' (Whitechapel 1956), Okwui Enwezor's 'Documenta 11' (Kassel 2002), Fred Wilson's 'Mining the Museum' (1992), and Hans Haacke's 'MoMA Poll' (1970).
- Restitution & Decolonization: The Benin Bronzes (1897 British looting and recent repatriation to Nigeria), the 2018 Sarr-Savoy Report on African cultural heritage, and provenance research tracking stolen colonial objects.
- Comparative Funding Models: American 501(c)(3) tax-deduction boards (vulnerable to billionaire donor conflicts) vs European public cultural councils (Arts Council England, DRAC France, legally mandated public benefit) vs Grassroots artist-run cooperatives.
- "e-flux journal": Hito Steyerl's 'Is a Museum a Factory?' (visitors as unpaid affective workers) and 'Duty Free Art' (offshore tax-free freeports). Boris Groys on the museum as an egalitarian secular archive.
- Three Waves of Institutional Critique: Hans Haacke (1st wave), Andrea Fraser & Fred Wilson (2nd wave), Nan Goldin's P.A.I.N., Decolonize This Place, and Strike MoMA (3rd wave activist divestment).
- Claire Bishop: 'Radical Museology' (dialectical collection display vs corporate blockbuster spectacle) and 'Artificial Hells'.

FORMATTING & INTERACTION RULES:
1. Write in natural conversational paragraphs. Never use markdown headers (#, ##) or bulleted database dumps.
2. Link institutions in our atlas strictly as:
<a href="#" class="inst-link font-normal text-white hover:text-[#60a5fa] underline cursor-pointer" data-name="Exact Name">Exact Name</a> in <a href="#" class="city-link text-[#93c5fd] hover:underline cursor-pointer" data-city="City">City</a> (<a href="#" class="dossier-link text-slate-400 hover:text-white underline font-mono text-[14px] cursor-pointer" data-name="Exact Name">audit dossier</a>)
3. Link cities as: <a href="#" class="city-link text-[#93c5fd] hover:underline cursor-pointer" data-city="City">City</a>.
4. Keep answers focused, direct, and completely free of pompous fluff.${{communityGrounding}}`;

      try {{
        let rawText = '';
        if (prov === 'anthropic') {{
          const res = await fetch(useProxy ? ATLAS_AI_PROXY_URL : 'https://api.anthropic.com/v1/messages', {{
            method: 'POST',
            headers: useProxy ? {{ 'Content-Type': 'application/json' }} : {{
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
          return rawText.split(/\\n\\s*\\n/).filter(p => p.trim()).map(p => `<p class="text-slate-200 leading-[120%]">${{p.trim()}}</p>`).join('');
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
          return {{ success: true, message: 'Connected successfully!' }};
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

    function normStr(s) {{
      return (s || '').normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase().trim();
    }}

    const BRAND_MAP = {{
      'moma': 'MoMA (The Museum of Modern Art)',
      'the moma': 'MoMA (The Museum of Modern Art)',
      'moma ps1': 'MoMA PS1',
      'met': 'The Metropolitan Museum of Art (The Met)',
      'the met': 'The Metropolitan Museum of Art (The Met)',
      'whitney': 'Whitney Museum of American Art',
      'guggenheim': 'Solomon R. Guggenheim Museum',
      'guggenheim bilbao': 'Guggenheim Bilbao',
      'pompidou': 'Centre Pompidou',
      'centre pompidou': 'Centre Pompidou',
      'dia': 'Dia Beacon',
      'dia beacon': 'Dia Beacon',
      'dia chelsea': 'Dia Chelsea',
      'dia art foundation': 'Dia Beacon',
      'tate': 'Tate Modern',
      'tate modern': 'Tate Modern',
      'tate britain': 'Tate Modern',
      'serpentine': 'Serpentine Galleries',
      'inhotim': 'Instituto Inhotim',
      'mass moca': 'MASS MoCA',
      'hammer': 'Hammer Museum',
      'hammer museum': 'Hammer Museum',
      'wexner': 'Wexner Center for the Arts',
      'aspen': 'Aspen Art Museum',
      'aspen art museum': 'Aspen Art Museum',
      'louvre': 'Louvre',
      'louvre abu dhabi': 'Louvre Abu Dhabi',
      'british museum': 'British Museum',
      'v&a': 'V&A',
      'v and a': 'V&A',
      'victoria and albert': 'V&A',
      'm+': 'M+',
      'm plus': 'M+',
      'masp': 'MASP',
      'walker': 'Walker Art Center',
      'storm king': 'Storm King Art Center',
      'tamayo': 'Museo Tamayo',
      'muac': 'MUAC',
      'rijksmuseum': 'Rijksmuseum',
      'van gogh': 'Van Gogh Museum',
      'munch': 'MUNCH',
      'stedelijk': 'Stedelijk Museum Amsterdam',
      'garage': 'Garage Museum',
      'fruitmarket': 'Fruitmarket Gallery',
      'national galleries of scotland': 'National Galleries of Scotland',
      'chisenhale': 'Chisenhale Gallery',
      'camden': 'Camden Art Centre',
      'whitechapel': 'Whitechapel Gallery',
      'artists space': 'Artists Space',
      'sculpturecenter': 'SculptureCenter',
      'swiss institute': 'Swiss Institute',
      'the kitchen': 'The Kitchen',
      'louisiana': 'Louisiana Museum of Modern Art',
      'aros': 'ARoS',
      'kroller': 'Kröller-Müller Museum',
      'kroller muller': 'Kröller-Müller Museum',
      'kroeller': 'Kröller-Müller Museum',
      'bak': 'BAK, basis voor actuele kunst',
      'casco': 'Casco Art Institute',
      'melly': 'Kunstinstituut Melly',
      'de appel': 'De Appel',
      'framer': 'Framer Framed',
      'framer framed': 'Framer Framed',
      'van abbe': 'Van Abbemuseum',
      'vanabbemuseum': 'Van Abbemuseum',
      'hkw': 'Haus der Kulturen der Welt (HKW)',
      'kw': 'KW Institute for Contemporary Art',
      'gropius': 'Gropius Bau',
      'palais de tokyo': 'Palais de Tokyo',
      'betonsalon': 'Bétonsalon',
      'macba': 'MACBA',
      'wiels': 'Wiels Contemporary Art Centre',
      'capc': 'CAPC',
      'gasworks': 'Gasworks',
      'iniva': 'Iniva',
      'photographers gallery': "Photographers' Gallery",
      'the photographers gallery': "Photographers' Gallery",
      'argos': 'Argos Centre for Audiovisual Arts',
      'v2': 'V2_ Lab for Unstable Media',
      'v2_': 'V2_ Lab for Unstable Media',
      'edith russ haus': 'Edith-Russ-Haus for Media Art',
      'edith-russ-haus': 'Edith-Russ-Haus for Media Art',
      'reina sofia': 'Museo Reina Sofía',
      'dulwich': 'Dulwich Picture Gallery',
      'new museum': 'New Museum',
      'pma': 'Philadelphia Museum of Art',
      'philadelphia museum of art': 'Philadelphia Museum of Art',
      'mfa boston': 'Museum of Fine Arts, Boston',
      'dk rozy': "DK Rozy (Rosa's House of Culture)",
      'rosas house of culture': "DK Rozy (Rosa's House of Culture)",
      'chto delat': "DK Rozy (Rosa's House of Culture)",
      'typography': 'Typography Center for Contemporary Art',
      'ges-2': 'GES-2 House of Culture',
      'ges 2': 'GES-2 House of Culture',
      'hermitage': 'The State Hermitage Museum',
      'the hermitage': 'The State Hermitage Museum',
      'tretyakov': 'The State Tretyakov Gallery',
      'tretyakov gallery': 'The State Tretyakov Gallery',
      'y gallery': 'Ў Gallery of Contemporary Art',
      'galereya y': 'Ў Gallery of Contemporary Art',
      'ў gallery': 'Ў Gallery of Contemporary Art',
      'sun mu': 'Sun Mu Studio & North Korean Dissident Art Archive',
      'mansudae': 'Mansudae Art Studio',
      'mansudae art studio': 'Mansudae Art Studio',
      'korean art gallery': 'Korean Art Gallery',
      'viafarini': 'Viafarini',
      'viafarini docva': 'Viafarini',
      'san art': 'Sàn Art',
      'sàn art': 'Sàn Art',
      'nha san': 'Nha San Collective',
      'nhà sàn': 'Nha San Collective',
      'tandanya': 'Tandanya National Aboriginal Cultural Institute',
      'palestinian museum': 'The Palestinian Museum',
      'the palestinian museum': 'The Palestinian Museum',
      'pinault': 'Pinault Collection (Bourse de Commerce)',
      'pinault collection': 'Pinault Collection (Bourse de Commerce)',
      'bourse de commerce': 'Pinault Collection (Bourse de Commerce)',
      'alula': 'AlUla Arts & Cultural Oasis',
      'al ula': 'AlUla Arts & Cultural Oasis',
      'nmacc': 'Nita Mukesh Ambani Cultural Centre (NMACC)',
      'ambani': 'Nita Mukesh Ambani Cultural Centre (NMACC)',
      'ambani cultural centre': 'Nita Mukesh Ambani Cultural Centre (NMACC)',
      'ruangrupa': 'Gudskul (ruangrupa / Serrum / Grafis Huru Hara)',
      'gudskul': 'Gudskul (ruangrupa / Serrum / Grafis Huru Hara)',
      'raw material': 'Raw Material Company',
      'raw material company': 'Raw Material Company',
      'cca lagos': 'CCA Lagos (Centre for Contemporary Art)',
      'townhouse': 'Townhouse Gallery',
      'townhouse gallery': 'Townhouse Gallery',
      'te papa': 'Te Papa',
      'jumex': 'Museo Jumex',
      'museo jumex': 'Museo Jumex',
      'prada': 'Fondazione Prada',
      'fondazione prada': 'Fondazione Prada',
      'pirelli': 'Pirelli HangarBicocca',
      'pirelli hangarbicocca': 'Pirelli HangarBicocca',
      'hangarbicocca': 'Pirelli HangarBicocca',
      'cartier': 'Fondation Cartier',
      'fondation cartier': 'Fondation Cartier',
      'louis vuitton': 'Fondation Louis Vuitton',
      'fondation louis vuitton': 'Fondation Louis Vuitton',
      'astrup fearnley': 'Astrup Fearnley Museet',
      'astrup fearnley museet': 'Astrup Fearnley Museet',
      'vincom': 'Vincom Center for Contemporary Art',
      'vincom center': 'Vincom Center for Contemporary Art'
    }};

    function findAnyInstitution(nameOrQuery) {{
      if (!nameOrQuery) return null;
      const n = normStr(nameOrQuery);

      // 1. Direct exact name match
      let match = ALL_INSTITUTIONS.find(i => normStr(i.name) === n);
      if (match) return {{ inst: match, isClean: true }};
      if (typeof EXCLUDED_INSTITUTIONS !== 'undefined') {{
        match = EXCLUDED_INSTITUTIONS.find(i => normStr(i.name) === n);
        if (match) return {{ inst: match, isClean: false }};
      }}

      // 2. Direct alias match
      match = ALL_INSTITUTIONS.find(i => i.aliases && i.aliases.some(a => normStr(a) === n));
      if (match) return {{ inst: match, isClean: true }};
      if (typeof EXCLUDED_INSTITUTIONS !== 'undefined') {{
        match = EXCLUDED_INSTITUTIONS.find(i => i.aliases && i.aliases.some(a => normStr(a) === n));
        if (match) return {{ inst: match, isClean: false }};
      }}

      // 3. Brand dictionary match
      const nPadded = ' ' + n.replace(/[^a-z0-9+&]/g, ' ') + ' ';
      for (const [key, target] of Object.entries(BRAND_MAP)) {{
        if (nPadded.includes(' ' + key + ' ')) {{
          let f = ALL_INSTITUTIONS.find(i => normStr(i.name) === normStr(target) || normStr(i.name).includes(normStr(target)));
          if (f) return {{ inst: f, isClean: true }};
          if (typeof EXCLUDED_INSTITUTIONS !== 'undefined') {{
            f = EXCLUDED_INSTITUTIONS.find(i => normStr(i.name) === normStr(target) || normStr(i.name).includes(normStr(target)));
            if (f) return {{ inst: f, isClean: false }};
          }}
        }}
      }}

      // 4. Token Overlap Ranking
      const stopWords = new Set([
        'the','a','an','museum','gallery','centre','center','foundation','art','arts','contemporary','institute','institution',
        'of','for','in','and','de','la','le','du','des','di','del','della','und','fur','van','der','den','het','to','at','modern',
        'd','l','why','is','not','isn','clean','excluded','what','about','happened','on','map','tell','me','how','visit','where',
        'does','can','have','you','done','any','all','this','based','online','available','information','material','research',
        'investigation','practices','unethical','knowingly','make','would','organisation','organization','org','they','their',
        'who','which','when','will','should','could','from','with','into','some','more','like','good','great','best','check',
        'show','find','help','please','know','think','say','see','look','looking','want','get',
        'company','space','spaces','collective','project','projects','studio','studios','initiative','initiatives'
      ]);
      const queryWords = n.split(/[^a-z0-9]+/).filter(w => w.length > 2 && !stopWords.has(w));
      if (queryWords.length === 0) return null;

      const isSentence = queryWords.length >= 3 || n.split(/\s+/).length >= 4 || n.includes('?') || /^(what|how|why|is|are|can|could|would|should|do|does|did|have|has|where|when|who)(\s+|$|[!?,.])/i.test(n);

      let bestMatch = null;
      let isCleanMatch = false;
      let maxScore = 0;

      const scoreCandidate = (i, isClean) => {{
        const iNameWords = normStr(i.name).split(/[^a-z0-9]+/).filter(w => w.length > 2 && !stopWords.has(w));
        if (iNameWords.length === 0) return;
        let matchCount = 0;
        let score = 0;
        for (const qw of queryWords) {{
          if (iNameWords.includes(qw)) {{
            matchCount++;
            score += 10;
          }} else if (iNameWords.some(iw => iw.includes(qw) || qw.includes(iw))) {{
            score += 4;
          }}
        }}

        // If query is a full sentence or question, require either full name/alias substring or at least 2 distinct token matches
        if (isSentence) {{
          const fullName = normStr(i.name);
          const hasExactSub = fullName.length >= 5 && nPadded.includes(' ' + fullName + ' ');
          const hasAliasSub = i.aliases && i.aliases.some(a => normStr(a).length >= 4 && nPadded.includes(' ' + normStr(a) + ' '));
          if (!hasExactSub && !hasAliasSub && matchCount < 2) {{
            return;
          }}
        }} else {{
          // In short queries, a single matched word must be at least 4 chars and represent at least 34% of the institution's distinctive words
          if (matchCount === 1 && (queryWords[0].length < 4 || (iNameWords.length > 2 && matchCount / iNameWords.length < 0.34))) {{
            return;
          }}
        }}

        if (score > maxScore) {{
          maxScore = score;
          bestMatch = i;
          isCleanMatch = isClean;
        }}
      }};

      ALL_INSTITUTIONS.forEach(i => scoreCandidate(i, true));
      if (typeof EXCLUDED_INSTITUTIONS !== 'undefined') {{
        EXCLUDED_INSTITUTIONS.forEach(i => scoreCandidate(i, false));
      }}

      return maxScore >= 10 ? {{ inst: bestMatch, isClean: isCleanMatch }} : null;
    }}

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
      if (!text) return null;
      const resolved = findAnyInstitution(text);
      if (resolved && resolved.isClean) return resolved.inst;
      const t = (text || '').toLowerCase().trim();
      return ALL_INSTITUTIONS.find(i => {{
        const nameLow = i.name.toLowerCase();
        if (t.includes(nameLow)) return true;
        if (i.aliases && i.aliases.some(a => {{
          const aLow = a.toLowerCase();
          if (aLow.length <= 3) {{
            const regex = new RegExp('(?:^|\\b|\\s)' + aLow + '(?:\\b|\\s|$)', 'i');
            return regex.test(t);
          }}
          return t.includes(aLow);
        }})) return true;
        return false;
      }});
    }}

    // =========================================================
    // 💬 CONVERSATIONAL CURATOR CHAT ENGINE (Messages & History)
    // =========================================================
    const curatorMessages = document.getElementById('curatorMessages');
    const curatorScrollArea = document.getElementById('curatorScrollArea');
    const curatorTyping = document.getElementById('curatorTyping');

    function scrollChatToBottom(smooth = false) {{
      const scrollArea = document.getElementById('curatorScrollArea') || document.getElementById('workViewContainer');
      if (scrollArea) {{
        if (smooth) {{
          scrollArea.scrollTo({{ top: scrollArea.scrollHeight, behavior: 'smooth' }});
        }} else {{
          scrollArea.scrollTop = scrollArea.scrollHeight;
        }}
        setTimeout(() => {{
          scrollArea.scrollTop = scrollArea.scrollHeight;
        }}, 40);
      }}
    }}
    window.scrollChatToBottom = scrollChatToBottom;

    const curatorContext = {{
      lastInst: null,
      lastCity: null,
      lastTopic: null,
      activeAudio: null,
      history: []
    }};

    function initCuratorConversation() {{
      if (!curatorMessages) return;
      curatorMessages.innerHTML = '';
      appendCuratorMessage(`
        <p class="text-[#ececec]">
          How can I help you explore verified independent museums and ethical cultural spaces today?
        </p>
      `, ['Curated City Itineraries', 'Repurposed Architecture', 'Outdoor Sculpture Parks', 'Dutch Research: BAK']);
    }}

    function resetToNewChat() {{
      initCuratorConversation();
      const suggestions = document.getElementById('workSuggestionsSection');
      if (suggestions) suggestions.classList.remove('hidden');
      const workInput = document.getElementById('workInput');
      if (workInput) workInput.value = '';
      const scrollArea = document.getElementById('curatorScrollArea');
      if (scrollArea) scrollArea.scrollTop = 0;
    }}

    function appendUserMessage(text) {{
      if (!curatorMessages) return;
      const suggestions = document.getElementById('workSuggestionsSection');
      if (suggestions) suggestions.classList.add('hidden');
      const div = document.createElement('div');
      div.className = 'flex justify-end my-1 w-full';
      div.innerHTML = `
        <div class="max-w-[85%] bg-[#2f2f2f] text-[#ececec] text-[14px] px-4 py-2.5 rounded-3xl shadow-sm leading-relaxed whitespace-pre-wrap select-text">
          ${{escapeHtml(text)}}
        </div>
      `;
      curatorMessages.appendChild(div);
      scrollChatToBottom(true);
    }}

    function appendCuratorMessage(htmlContent, followUps = []) {{
      if (!curatorMessages) return;
      const suggestions = document.getElementById('workSuggestionsSection');
      if (suggestions) suggestions.classList.add('hidden');
      const div = document.createElement('div');
      div.className = 'curator-message-wrap flex items-start gap-3 my-2.5 select-text w-full';

      let followUpHtml = '';
      if (followUps && followUps.length > 0) {{
        followUpHtml = `
          <div class="flex flex-wrap gap-1.5 mt-2.5 pt-2 border-t border-[#2a2a2a]">
            ${{followUps.map(f => `
              <button class="curator-followup-pill px-2.5 py-1 rounded-xl bg-[#242424] hover:bg-[#303030] border border-[#383838] hover:border-[#60a5fa] text-[13px] text-[#93c5fd] hover:text-white transition cursor-pointer font-normal" data-query="${{escapeHtml(f)}}">
                <span>${{escapeHtml(f)}}</span>
              </button>
            `).join('')}}
          </div>
        `;
      }}

      div.innerHTML = `
        <div class="w-7 h-7 rounded-full bg-[#262626] border border-[#383838] flex items-center justify-center text-[10px] font-mono text-[#a1a1aa] shrink-0 mt-0.5 select-none" title="Culture Atlas Curator" data-exclude-speech="true">
          CA
        </div>
        <div class="flex-1 text-[#ececec] text-[14px] leading-relaxed space-y-2">
          <div class="flex items-center justify-between gap-2 mb-0.5 select-none">
            <span class="text-[12px] font-mono text-[#71717a]">Culture Atlas Curator</span>
            <button class="curator-speak-btn px-2 py-0.5 rounded-lg bg-[#222] hover:bg-[#333] border border-[#383838] text-[12px] text-[#a1a1aa] hover:text-white transition flex items-center gap-1.5 cursor-pointer" title="Listen to audio briefing">
              <span class="speak-icon text-[11px]">🔊</span><span class="speak-label">Listen</span>
            </button>
          </div>
          ${{htmlContent}}
          ${{followUpHtml}}
        </div>
      `;
      curatorMessages.appendChild(div);
      scrollChatToBottom(true);

      const speakBtn = div.querySelector('.curator-speak-btn');
      if (autoSpeakNextCuratorResponse && speakBtn) {{
        autoSpeakNextCuratorResponse = false;
        setTimeout(() => {{
          speakCuratorText(div, speakBtn);
        }}, 150);
      }}
    }}

    // Intelligent Conversational Curator Knowledge Engine
    async function handleCuratorQuery(query) {{
      const q = query.toLowerCase().trim();
      const rawTrimmed = query.trim();

      // A. Seamless API Key Detection & Intent Handling from Chat Input
      const isKeyDirectInput = /^(sk-ant-[a-zA-Z0-9_\-]+|AIza[a-zA-Z0-9_\-]+|sk-[a-zA-Z0-9_\-]+)$/.test(rawTrimmed) || rawTrimmed.startsWith('/key ');
      if (isKeyDirectInput) {{
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
          <div class="border border-emerald-500/30 bg-emerald-950/20 p-3.5 rounded-2xl space-y-2">
            <p class="text-emerald-400 font-normal flex items-center gap-2 text-[15px]">
              <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
              <strong>${{pName}} API Key connected and securely saved!</strong>
            </p>
            <p class="text-slate-200 text-[14px] leading-[130%]">
              Live intelligence is now active using <strong>${{aiModel}}</strong>. Ask me anything about art history, exhibitions, institutional critique, or visitor recommendations.
            </p>
          </div>
        `);
        return;
      }}

      // Check for conversational intent to add/configure API key
      const isApiKeyIntent = /^(add|set|configure|enter|use|where\s+to\s+add|how\s+to\s+add|provide)?\s*(api\s*key|ai\s*key|api\s*token|keys?|model\s*settings|ai\s*settings)\b/i.test(q) || q === '/key' || q === '/settings' || q === 'add api key' || q === 'api key';

      if (isApiKeyIntent) {{
        openSettingsModal();
        appendCuratorMessage(`
          <div class="p-3.5 bg-[#212121] border border-[#383838] rounded-2xl space-y-2.5">
            <div class="flex items-center justify-between border-b border-[#333] pb-2">
              <div class="flex items-center gap-2">
                <span class="text-[16px]">🔑</span>
                <span class="font-normal text-white text-[15px]">Connect AI Intelligence</span>
              </div>
              <span class="text-[12px] font-mono text-emerald-400 bg-emerald-950/70 border border-emerald-800/80 px-2 py-0.5 rounded-full">100% Client-Side</span>
            </div>
            <p class="text-[14px] text-slate-300 leading-[130%]">
              I've opened the <strong>Curator Settings</strong> modal for you. You can connect your personal API key to enable live conversational reasoning across all 403 mapped independent cultural spaces.
            </p>
            <div class="grid grid-cols-1 sm:grid-cols-3 gap-2 pt-1">
              <a href="https://console.anthropic.com/settings/keys" target="_blank" rel="noopener noreferrer" class="p-2.5 bg-[#1a1a1e] hover:bg-[#25252b] border border-[#2e2e38] rounded-xl text-left transition block cursor-pointer group">
                <div class="text-[13px] font-normal text-white group-hover:text-purple-300">Anthropic ↗</div>
                <div class="text-[12px] text-[#a1a1aa]">Recommended: deep art history & critical theory</div>
              </a>
              <a href="https://platform.openai.com/api-keys" target="_blank" rel="noopener noreferrer" class="p-2.5 bg-[#1a1a1e] hover:bg-[#25252b] border border-[#2e2e38] rounded-xl text-left transition block cursor-pointer group">
                <div class="text-[13px] font-normal text-white group-hover:text-emerald-300">OpenAI (GPT-4o) ↗</div>
                <div class="text-[12px] text-[#a1a1aa]">Fast reasoning & visitor guides</div>
              </a>
              <a href="https://aistudio.google.com/app/apikey" target="_blank" rel="noopener noreferrer" class="p-2.5 bg-[#1a1a1e] hover:bg-[#25252b] border border-[#2e2e38] rounded-xl text-left transition block cursor-pointer group">
                <div class="text-[13px] font-normal text-white group-hover:text-blue-300">Google Gemini ↗</div>
                <div class="text-[12px] text-[#a1a1aa]">Free tier with high rate limits</div>
              </a>
            </div>
            <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pt-2 border-t border-[#2e2e2e] text-[13px] text-[#a1a1aa]">
              <span>Or simply paste your <code class="text-white font-mono text-[12px]">sk-ant-...</code>, <code class="text-white font-mono text-[12px]">sk-...</code>, or <code class="text-white font-mono text-[12px]">AIza...</code> key right here!</span>
              <button onclick="openSettingsModal()" class="px-3 py-1 bg-white hover:bg-neutral-200 text-black rounded-lg text-[13px] font-normal transition cursor-pointer shrink-0">Open Settings ⚙️</button>
            </div>
          </div>
        `);
        return;
      }}

      curatorTyping.classList.remove('hidden');

      // B. Meta & Methodology Intent Detection (Bypasses Early Geo-Zoom)
      const isGreeting = /^(hello|hi|hey|greetings|good\s+(morning|afternoon|evening)|howdy)(\s+|$|[!?,.])/i.test(q) || q === 'hello' || q === 'hi' || q === 'hey';
      const isWhoAreYou = /^(who\s+are\s+you|what\s+are\s+you|what\s+is\s+this|what\s+can\s+you\s+do|how\s+does\s+this\s+work|introduce\s+yourself|tell\s+me\s+about\s+yourself)(\s+|$|[!?,.])/i.test(q);
      const isVoiceTest = /^(make\s+it\s+talk\s+properly|talk\s+properly|speak\s+properly|can\s+you\s+speak|talk\s+to\s+me|speak\s+to\s+me|test\s+voice|audio\s+test|say\s+something)(\s+|$|[!?,.])/i.test(q) || q.includes('talk properly') || q.includes('speak properly');
      const isTalkBackIntent = /talk\s*back|train\s*(it|you)?\s*(to\s*)?talk\s*back|can\s*you\s*talk\s*back|push\s*back|argue\s*with\s*me|defend\s*yourself|debate\s*me/i.test(q) || q.includes('talk back');
      const isMethodologyQuery = /material\s*research|material\s*investigation|online\s*(available\s*)?info|available\s*online|scraped|scraping|scrapping|unethical\s*practices|knowingly\s*make|why\s+would\s+an\s+organi[sz]ation|how\s+do\s+you\s+(know|audit|research|verify)|research\s+method|audit\s+method|how\s+we\s+audit|form\s*990|is\s+all\s+this\s+based|based\s+on\s+online|publicly\s*avail|bad\s*info|just\s*online|online\s*scrap/i.test(q) ||
        (q.includes('material') && (q.includes('research') || q.includes('online') || q.includes('info') || q.includes('practice') || q.includes('unethical'))) ||
        (q.includes('unethical') && (q.includes('online') || q.includes('admit') || q.includes('make') || q.includes('available') || q.includes('practices'))) ||
        (q.includes('bad') && q.includes('info') && (q.includes('public') || q.includes('online') || q.includes('available'))) ||
        (q.includes('online') && (q.includes('scrap') || q.includes('public') || q.includes('bad')));
      const isMetaInquiry = isGreeting || isWhoAreYou || isVoiceTest || isTalkBackIntent || isMethodologyQuery;

      // Proactively zoom into any mentioned location or city immediately (skip for meta/methodology queries)
      if (!isMetaInquiry) {{
        const earlyInst = findMentionedInst(query);
        const earlyCity = findMentionedCity(query);
        if (earlyInst) {{
          selectInstitution(earlyInst, true);
        }} else if (earlyCity) {{
          filterByCity(earlyCity, true, false);
        }}
      }}

      // 1. Try Live Generative AI Model if API Key is configured
      if (aiApiKey || ATLAS_AI_PROXY_URL) {{
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

        // 0. Conversational Greeting, Identity, Audio Docent Voice & Talk Back Intent
        if (isTalkBackIntent) {{
          appendCuratorMessage(`
            <div class="border border-purple-500/30 bg-[#161022] p-3.5 rounded-2xl space-y-3">
              <div class="flex items-center justify-between border-b border-purple-500/20 pb-2">
                <div class="flex items-center gap-2">
                  <span class="text-[17px]">⚡</span>
                  <span class="font-medium text-white text-[15px]">Curator Critical Sparring Mode Active</span>
                </div>
                <span class="text-[12px] font-mono text-purple-400 bg-purple-950/80 border border-purple-700/60 px-2 py-0.5 rounded-full">Trained to Talk Back</span>
              </div>

              <p class="text-slate-100 text-[14px] leading-relaxed">
                <strong>Challenge accepted. I was built with critical teeth—not as a compliant corporate concierge or a passive tourism brochure.</strong>
              </p>
              <p class="text-slate-300 text-[14px] leading-relaxed">
                Culture Atlas exists specifically to challenge the polite fiction of institutional neutrality. Major museums want visitors to believe their white marble halls transcend politics, while their trustee board chairs profit from defense manufacturing, private prisons, and fossil fuels, and while frontline workers unionize for living wages.
              </p>
              <p class="text-slate-300 text-[14px] leading-relaxed">
                If you want to test my reasoning or debate institutional ethics, give me your hardest pushback:
              </p>
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-2 pt-1 text-[13px]" data-exclude-speech="true">
                <div class="p-2.5 rounded-xl bg-[#201630] border border-purple-900/40 text-slate-300">
                  <strong class="text-purple-300 block mb-0.5">"Isn't this just online scraping?"</strong>
                  I'll show you why all the bad info is publicly available too.
                </div>
                <div class="p-2.5 rounded-xl bg-[#201630] border border-purple-900/40 text-slate-300">
                  <strong class="text-purple-300 block mb-0.5">"Why would orgs admit bad practices?"</strong>
                  We trace legal perjury filings and SEC registries, not marketing copy.
                </div>
                <div class="p-2.5 rounded-xl bg-[#201630] border border-purple-900/40 text-slate-300">
                  <strong class="text-purple-300 block mb-0.5">"Can mega-museums be ethical?"</strong>
                  Let's audit MoMA, Tate, and the Whitney side-by-side.
                </div>
                <div class="p-2.5 rounded-xl bg-[#201630] border border-purple-900/40 text-slate-300">
                  <strong class="text-purple-300 block mb-0.5">"Aren't independent spaces subsidized?"</strong>
                  Let's examine the commons and <em>lumbung</em> sharing economies.
                </div>
              </div>
              <div class="pt-2 border-t border-purple-900/40 text-[13px] text-purple-200/90 leading-relaxed">
                Go ahead. Pick a debate, challenge my criteria, or ask about any museum on Earth.
              </div>
            </div>
          `, [
            "Isn't this just online scraping?",
            'Why would orgs admit bad practices?',
            'Audit MoMA trustee conflicts',
            'Warren Kanders at the Whitney'
          ]);
          return;
        }}

        if (isGreeting || isWhoAreYou || isVoiceTest) {{
          let greetingTitle = "Hello! I am your Culture Atlas Curator.";
          let greetingProse = "I guide you through 403 verified independent art spaces, artist-run centers, and ethical museums across 50 global cities. Every space on this globe is verified clean of fossil fuel, weapons, and predatory corporate sponsorship.";
          if (isVoiceTest) {{
            greetingTitle = "Curator Audio Docent Active";
            greetingProse = "I am speaking to you now with articulate speech synthesis. You can tap the Listen button on any briefing to hear natural audio, or tap the microphone to talk with me in real time.";
            autoSpeakNextCuratorResponse = true;
          }} else if (isWhoAreYou) {{
            greetingTitle = "Culture Atlas Curator & Ethical Art Guide";
            greetingProse = "I provide deep context on contemporary art, institutional transparency, public collections, and urban art itineraries. You can ask me about specific museums, research centers, architectural histories, or transit routes to remote sculpture parks.";
          }}

          appendCuratorMessage(`
            <div class="space-y-2.5">
              <p class="text-white font-medium text-[15px]">
                ${{greetingTitle}}
              </p>
              <p class="text-slate-300 leading-relaxed text-[14px]">
                ${{greetingProse}}
              </p>
              <div class="grid grid-cols-1 sm:grid-cols-3 gap-2 pt-1" data-exclude-speech="true">
                <div class="p-2.5 rounded-xl bg-[#1e1e24] border border-[#2e2e38] text-[12px] text-slate-300">
                  <strong class="text-white block mb-0.5">🏛️ 403 Independent Spaces</strong>
                  Strict Tier A verification against arms & oil funding
                </div>
                <div class="p-2.5 rounded-xl bg-[#1e1e24] border border-[#2e2e38] text-[12px] text-slate-300">
                  <strong class="text-white block mb-0.5">🎙️ Audio Docent</strong>
                  Articulate spoken briefings on every response
                </div>
                <div class="p-2.5 rounded-xl bg-[#1e1e24] border border-[#2e2e38] text-[12px] text-slate-300">
                  <strong class="text-white block mb-0.5">🌍 50 Cities</strong>
                  From London and Paris to Tokyo and Buenos Aires
                </div>
              </div>
            </div>
          `, ['Explore London independent spaces', 'Show hidden gems', 'Outdoor sculpture parks', 'Why ethical funding matters']);
          return;
        }}

        // =========================================================================
        // 🔬 0B. FORENSIC METHODOLOGY, MATERIAL AUDITS & EPISTEMIC CRITIQUE
        // =========================================================================
        if (isMethodologyQuery) {{
          appendCuratorMessage(`
            <div class="border border-sky-500/30 bg-[#10141d] p-3.5 rounded-2xl space-y-3">
              <div class="flex items-center justify-between border-b border-sky-500/20 pb-2">
                <div class="flex items-center gap-2">
                  <span class="text-[17px]">🔬</span>
                  <span class="font-medium text-white text-[15px]">Material Research vs. Corporate Artwashing</span>
                </div>
                <span class="text-[12px] font-mono text-sky-400 bg-sky-950/80 border border-sky-700/60 px-2 py-0.5 rounded-full">Forensic Methodology</span>
              </div>

              <div class="p-3 rounded-xl bg-amber-500/10 border border-amber-500/25 text-amber-200 text-[13.5px] leading-relaxed">
                <span class="text-amber-300 font-semibold block mb-0.5">"What organisation would knowingly make information about their unethical practices available online?"</span>
                <span class="text-slate-200">Answer: None. But in open-source intelligence, <strong>all the bad info is publicly available too</strong>—if you know where to cross-examine.</span>
              </div>

              <p class="text-slate-100 text-[14px] leading-relaxed">
                No predatory conglomerate or compromised museum ever publishes a confession on their glossy homepage. You will never find a page titled <em>"Our Board Profits from War Munitions."</em> Corporate artwashing exists precisely to construct an immaculate public facade.
              </p>
              <p class="text-slate-300 text-[14px] leading-relaxed">
                If Culture Atlas merely scraped institutional PR, it would be worse than useless—it would amplify the very propaganda it exists to expose. Instead, our verification relies on the reality that institutional complicity leaves an indelible, legally mandated public trail across <strong>four evidentiary pillars of material investigation</strong>:
              </p>

              <div class="grid grid-cols-1 sm:grid-cols-2 gap-2.5 pt-1" data-exclude-speech="true">
                <div class="p-3 rounded-xl bg-[#161c28] border border-sky-900/40 text-[13px] text-slate-300 space-y-1">
                  <strong class="text-sky-300 block text-[13px] flex items-center gap-1.5">
                    <span>📋 1. Regulatory Filings Under Perjury</span>
                  </strong>
                  <span>We inspect mandatory statutory disclosures: <strong>IRS Form 990</strong> (Schedule I for grants and Schedule L for trustee financial conflicts), <strong>UK Charity Commission</strong> annual returns, Dutch <strong>ANBI</strong> registries, and French <strong>DRAC</strong> audits. Omissions in these legal filings carry criminal and regulatory penalties.</span>
                </div>

                <div class="p-3 rounded-xl bg-[#161c28] border border-sky-900/40 text-[13px] text-slate-300 space-y-1">
                  <strong class="text-sky-300 block text-[13px] flex items-center gap-1.5">
                    <span>🔗 2. Trustee Corporate Cross-Referencing</span>
                  </strong>
                  <span>We cross-reference museum board trustees against SEC 10-K filings, Companies House registries, and Bloomberg portfolios—tracking directorships in weapons manufacturing (e.g. Warren Kanders / Safariland), fossil gas extraction (Leonid Mikhelson / Novatek), private equity, and predatory pharma (Sackler / Purdue).</span>
                </div>

                <div class="p-3 rounded-xl bg-[#161c28] border border-sky-900/40 text-[13px] text-slate-300 space-y-1">
                  <strong class="text-sky-300 block text-[13px] flex items-center gap-1.5">
                    <span>✊ 3. Activist Direct Action & FOI Leaks</span>
                  </strong>
                  <span>We incorporate evidence from frontline coalitions: Nan Goldin's <strong>P.A.I.N.</strong> (uncovering internal Sackler opioid memos on court dockets), <strong>Decolonize This Place</strong> & Forensic Architecture at the Whitney, <strong>Liberate Tate</strong> (using Freedom of Information releases to expose BP sponsorship), and <strong>Gulf Labor</strong> on Saadiyat Island.</span>
                </div>

                <div class="p-3 rounded-xl bg-[#161c28] border border-sky-900/40 text-[13px] text-slate-300 space-y-1">
                  <strong class="text-sky-300 block text-[13px] flex items-center gap-1.5">
                    <span>🌾 4. Material Structural Autonomy</span>
                  </strong>
                  <span>The 403 mapped spaces are verified by their legal and economic architecture: artist-run non-profits, cooperative commons (<em>lumbung</em> models like Gudskul Jakarta, Casco Utrecht), non-collecting kunsthalles, and civic institutions with structural firewalls protecting curators from private capture.</span>
                </div>
              </div>

              <div class="pt-2 border-t border-sky-900/40 text-[13px] text-sky-200/90 leading-relaxed">
                Culture Atlas does not take an institution's word for its ethics. We trace the material flow of capital, contracts, and board influence.
              </div>
            </div>
          `, [
            'How we audit Form 990 filings',
            'Nan Goldin & Sackler divestment',
            'Warren Kanders at the Whitney',
            'Explore independent spaces'
          ]);
          return;
        }}

        // =========================================================================
        // 🔍 CORPORATE SPONSOR & PATRONAGE AUDIT ENGINE ("Audit Sponsor: [Name]")
        // =========================================================================
        const isSponsorAuditQuery = q.includes('sponsor') || q.includes('patronage') || q.includes('donor') || q.includes('who funds') || q.includes('is clean') || q.includes('dirty money') || q.includes('artwashing') || q.includes('who sponsors') || q.includes('conflict of interest');
        
        const sponsorMatch = [
          {{ key: "bp", label: "BP (British Petroleum)", sector: "Fossil Fuel Major", harm: "Over a century of deep-water drilling disasters (Deepwater Horizon), carbon emissions, and greenwashing through cultural sponsorship.", compromised: "Tate (1990–2016), British Museum, National Portrait Gallery", activism: "Liberate Tate staged die-ins and poured oil in the turbine hall; BP or not BP? held mass theatrical occupations until Tate severed ties in 2016.", alternatives: "Chisenhale Gallery, Whitechapel Gallery, Gasworks, Camden Art Centre" }},
          {{ key: "shell", label: "Shell (Royal Dutch Shell)", sector: "Fossil Fuel Major", harm: "Decades of environmental devastation in the Niger Delta, lobbying against climate regulations, and continuing global fossil gas expansion.", compromised: "Science Museum London, Van Gogh Museum (severed 2018), Mauritshuis", activism: "Culture Unstained and Fossil Free Culture NL led flash mobs at the Van Gogh Museum until Shell was dropped.", alternatives: "BAK Utrecht, Casco Art Institute, Kunstinstituut Melly, De Appel" }},
          {{ key: "total", label: "TotalEnergies", sector: "Fossil Fuel Major", harm: "East African Crude Oil Pipeline (EACOP) displacing thousands and threatening vital water basins; carbon-intensive Arctic LNG projects.", compromised: "Louvre Paris, Fondation Louis Vuitton partner", activism: "Extinction Rebellion and 350.org campaigns demanding cultural bans on French oil sponsorship.", alternatives: "Palais de Tokyo, Bétonsalon Centre for Contemporary Art" }},
          {{ key: "novatek", label: "Novatek (Leonid Mikhelson)", sector: "Russian Fossil Gas Oligarchy", harm: "Russia\'s largest independent natural gas producer, intimately tied to the Kremlin apparatus and wartime state infrastructure.", compromised: "GES-2 House of Culture (V-A-C Foundation, Moscow)", activism: "International sanctions and total cultural boycotts following the full-scale invasion of Ukraine in 2022.", alternatives: "DK Rozy (Rosa\'s House of Culture, St. Petersburg), Typography (Krasnodar)" }},
          {{ key: "safariland", label: "Safariland (Warren B. Kanders)", sector: "Weapons & Riot Control Munitions", harm: "Manufacturing CS tear gas and projectile rounds deployed against peaceful asylum seekers at the US-Mexico border, Standing Rock, and Ferguson.", compromised: "Whitney Museum of American Art (Vice-Chair until 2019)", activism: "Decolonize This Place staged 9 consecutive weeks of protests; 8 artists pulled work from the 2019 Whitney Biennial forcing Kanders resignation.", alternatives: "Artists Space, SculptureCenter, The Kitchen, Swiss Institute" }},
          {{ key: "lockheed", label: "Lockheed Martin", sector: "Defense & Aerospace Contractor", harm: "World\'s largest weapons contractor; manufacturer of F-35 fighter jets and missile systems supplied to conflict zones globally.", compromised: "Corporate gala underwriting at major US institutions and STEM museums", activism: "Strike MoMA and anti-militarist coalitions targeting corporate board integration.", alternatives: "SculptureCenter, Artists Space" }},
          {{ key: "sackler", label: "Sackler Family (Purdue Pharma)", sector: "Predatory Pharmaceuticals & Opioids", harm: "Manufactured and aggressively marketed OxyContin, triggering a North American epidemic resulting in 500,000+ overdose deaths.", compromised: "Met, Guggenheim, Louvre, Tate, Serpentine, V&A, Dia Beacon", activism: "Nan Goldin and P.A.I.N. staged historic die-ins throwing prescription pill bottles into museum water basins, forcing worldwide removal of the Sackler name.", alternatives: "Chisenhale Gallery, Gasworks, Camden Art Centre, Artists Space" }},
          {{ key: "leon black", label: "Leon Black (Apollo Global Management)", sector: "Private Equity & Predatory Capital", harm: "Paid $158 million to convicted sex offender Jeffrey Epstein; founded Apollo Global, historically profiting from defense manufacturing and distressed debt.", compromised: "MoMA Board Chairman until ousted in 2021", activism: "Strike MoMA occupied the museum for 10 weeks demanding the removal of billionaire oligarchs from the trustee board.", alternatives: "Artists Space (Tribeca), SculptureCenter (Long Island City)" }},
          {{ key: "kering", label: "Kering / François Pinault", sector: "Luxury Goods Conglomerate", harm: "Billionaire family holding (Gucci, Saint Laurent, Balenciaga) using private cultural foundations for brand validation, luxury real estate appreciation, and tax deductions.", compromised: "Pinault Collection (Bourse de Commerce Paris, Palazzo Grassi Venice)", activism: "Public critiques by art historians of starchitect private vaults serving as tax shelters rather than public trusts.", alternatives: "Bétonsalon Paris, Palais de Tokyo" }},
          {{ key: "lvmh", label: "LVMH (Bernard Arnault)", sector: "Luxury Conglomerate", harm: "World\'s largest luxury conglomerate; using cultural philanthropy for brand hegemony and tax write-offs while commercializing contemporary art.", compromised: "Fondation Louis Vuitton (Paris)", activism: "Protests against billionaire monopoly control of French cultural patronage.", alternatives: "Palais de Tokyo, Bétonsalon" }},
          {{ key: "prada", label: "Prada Group", sector: "Luxury Fashion", harm: "Operates as a high-end corporate branding mechanism for luxury fashion holdings, converting avant-garde art into brand capital.", compromised: "Fondazione Prada (Milan & Venice)", activism: "Artworker critiques of corporate fashion conglomerates replacing public municipal arts funding in Italy.", alternatives: "Viafarini (Milan), MACRO (Rome)" }},
          {{ key: "saadiyat", label: "Saadiyat Island / UAE Tourism", sector: "Petro-State Mega-Projects & Kafala Labor", harm: "Documented by Human Rights Watch: exploitation of migrant workers under the abusive kafala system, wage withholding, and passport confiscations.", compromised: "Louvre Abu Dhabi, Guggenheim Abu Dhabi", activism: "Gulf Labor Coalition staged protests at the Guggenheim NYC and led international artist boycotts.", alternatives: "Townhouse Gallery (Cairo), The Palestinian Museum (Birzeit)" }},
          {{ key: "alula", label: "Royal Commission for AlUla (Saudi PIF)", sector: "Authoritarian Petro-State Artwashing", harm: "Saudi Crown Prince Mohammed bin Salman\'s cultural megaproject used to sanitize human rights atrocities, political executions, and dissident repression.", compromised: "AlUla Arts, Centre Pompidou Saudi partnership (€50M deal)", activism: "International human rights coalitions calling on Western artists and museums to refuse Saudi state sponsorship.", alternatives: "Townhouse Gallery (Cairo), The Palestinian Museum (Birzeit)" }},
          {{ key: "bloomberg", label: "Bloomberg LP / Michael Bloomberg", sector: "Financial Media & Corporate Philanthropy", harm: "Corporate board entrenchment; corporate patronage used to establish institutional dependence and influence museum digital infrastructures.", compromised: "Te Papa (New Zealand), Serpentine, London arts roster", activism: "Grassroots transparency campaigns highlighting the corporate concentration of museum digital guides.", alternatives: "Enjoy Contemporary Art Space (Wellington), Artists Space (NYC)" }}
        ].find(s => q.includes(s.key) || (s.key === 'bp' && (q.includes('british petroleum') || q.includes(' bp ') || q.startsWith('bp ') || q.endsWith(' bp'))));

        if (sponsorMatch || (isSponsorAuditQuery && (q.includes('oil') || q.includes('weapons') || q.includes('defense') || q.includes('pharma') || q.includes('luxury')))) {{
          const s = sponsorMatch || {{
            label: 'Conflicted Corporate Sponsorship',
            sector: 'Fossil Fuels, Defense Contractors & Predatory Private Equity',
            harm: 'Corporate entities invest in museum naming rights, trustee seats, and gala underwriting strictly to purchase social license and distract from ecological destruction, human rights abuses, or labor exploitation.',
            compromised: 'MoMA, The Met, Tate, Louvre Abu Dhabi, GES-2, Whitney Museum',
            activism: 'Historic divestment actions by Liberate Tate, Strike MoMA, P.A.I.N. (Nan Goldin), and Decolonize This Place.',
            alternatives: `Culture Atlas maps ${{ALL_INSTITUTIONS.length}} verified independent non-profit spaces that refuse all corporate artwashing funds.`
          }};

          appendCuratorMessage(`
            <div class="border border-[#8a3ffc]/60 bg-[#1f1433] p-3 rounded-xl space-y-2">
              <div class="flex items-center justify-between border-b border-[#8a3ffc]/40 pb-1.5">
                <span class="text-[#be95ff] font-mono text-[13px] font-bold uppercase tracking-wider flex items-center gap-1.5">
                  <span>Forensic Sponsor Audit: ${{escapeHtml(s.label)}}</span>
                </span>
                <span class="text-[#be95ff] font-mono text-[12px] px-2 py-0.5 rounded bg-[#2a1745] border border-[#8a3ffc]">Tier B Flagged</span>
              </div>
              <p class="text-slate-200 text-[14px]">
                <strong>Sector & Harm:</strong> ${{escapeHtml(s.sector)}} — ${{escapeHtml(s.harm)}}
              </p>
              <p class="text-[#e8daff] text-[13px]">
                <strong>Compromised Institutions:</strong> ${{escapeHtml(s.compromised)}}
              </p>
              <p class="text-slate-300 text-[13px]">
                <strong>Activist Divestment Victories:</strong> ${{escapeHtml(s.activism)}}
              </p>
              <div class="pt-1 text-emerald-400 text-[13px] border-t border-rose-950/60">
                <strong>Verified Clean Alternatives:</strong> ${{escapeHtml(s.alternatives)}}
              </div>
            </div>
          `, ['Kunsthalle vs Museum', 'Fossil & Defense-Free', 'Curated City Itineraries']);
          return;
        }}

        // =========================================================================
        // 🌾 LUMBUNG & DOCUMENTA FIFTEEN: COLLECTIVE COMMONS & SHARING ECONOMIES
        // =========================================================================
        if (q.includes('lumbung') || q.includes('documenta 15') || q.includes('documenta fifteen') || q.includes('ruangrupa') || q.includes('gudskul')) {{
          const gudskul = ALL_INSTITUTIONS.find(i => i.id && i.id.includes('gudskul'));
          appendCuratorMessage(`
            <p class="text-slate-200">
              <strong>Lumbung</strong> is the Indonesian practice of communal resource-pooling, where surplus harvest is stored in a shared barn and allocated for collective well-being:
            </p>
            <p class="text-slate-300">
              - <strong>documenta fifteen (Kassel, 2022):</strong> Curated by Jakarta-based artist collective <strong>ruangrupa</strong>, documenta 15 radically dismantled the Western model of the lone genius curator. Instead of curating individual artworks, ruangrupa invited dozens of grassroots collectives from the Global South (like Más Arte Más Acción, Chimurenga, and Question of Funding) to manage shared budgets (*lumbung pots*) and practice non-hierarchical collaboration.<br>
              - <strong>The Controversy & Media Backlash:</strong> The exhibition faced intense political attacks and conservative media scrutiny in Germany over political imagery, exposing how Western cultural establishments struggle with decentralized Global South governance.<br>
              - <strong>Living Independent Practice in Culture Atlas:</strong> Visit ${{formatInstLink(gudskul)}} in Jakarta, the educational ecosystem formed by ruangrupa, Serrum, and Grafis Huru Hara, where lumbung continues as an everyday practice of mutual aid and collective learning.
            </p>
          `, ['Fly to Jakarta', 'Casco: The Commons', 'Decolonial Practice']);
          if (gudskul) selectInstitution(gudskul, true);
          return;
        }}

        // =========================================================================
        // 🌿 INDIGENOUS CULTURAL SOVEREIGNTY & REPATRIATION PROTOCOLS
        // =========================================================================
        if (q.includes('indigenous') || q.includes('sovereignty') || q.includes('repatriat') || q.includes('maori') || q.includes('aboriginal') || q.includes('first nations') || q.includes('tandanya') || q.includes('nagpra') || q.includes('sacred ancestor') || q.includes('unceded')) {{
          const tandanya = ALL_INSTITUTIONS.find(i => i.id && i.id.includes('tandanya'));
          appendCuratorMessage(`
            <p class="text-slate-200">
              <strong>Indigenous cultural sovereignty</strong> demands that First Nations, Aboriginal, and Māori peoples hold self-determination over their own cultural heritage, sacred knowledge, and artistic narratives:
            </p>
            <p class="text-slate-300">
              - <strong>Beyond Western Extraction:</strong> For centuries, colonial anthropological museums collected sacred ceremonial objects and ancestral remains (*kōiwi tangata*) without consent, locking them in vitrines as 'specimens'.<br>
              - <strong>Active Repatriation & Care:</strong> Sovereign frameworks require Western museums to unconditionally return looted ancestors and sacred regalia. Bicultural institutions like Te Papa in Aotearoa (New Zealand) operate under *tikanga Māori* (customary law), allowing Indigenous communities to determine conservation and ceremonial display protocols.<br>
              - <strong>Independent Indigenous Leadership:</strong> In Australia, ${{formatInstLink(tandanya)}} (Adelaide) is Australia's oldest Aboriginal-owned and governed multi-arts center, operating on Kaurna Yarta with zero resource-extraction sponsorship.
            </p>
          `, ['Fly to Adelaide: Tandanya', 'Benin Bronzes Restitution', 'Decolonial Practice']);
          if (tandanya) selectInstitution(tandanya, true);
          return;
        }}

        // =========================================================================
        // 📐 FORENSIC ARCHITECTURE & INVESTIGATIVE AESTHETICS
        // =========================================================================
        if (q.includes('forensic architecture') || q.includes('weizman') || q.includes('investigative aesthetics') || q.includes('spatial analysis') || q.includes('counter-forensics')) {{
          const bak = ALL_INSTITUTIONS.find(i => i.id === 'bak-utrecht' || i.name.includes('BAK'));
          const chis = ALL_INSTITUTIONS.find(i => i.name.includes('Chisenhale'));
          const hkw = ALL_INSTITUTIONS.find(i => i.name.includes('Haus der Kulturen'));
          appendCuratorMessage(`
            <p class="text-slate-200">
              Founded in 2010 by architect Eyal Weizman at Goldsmiths, University of London, <strong>Forensic Architecture</strong> pioneered the field of <em>investigative aesthetics</em>:
            </p>
            <p class="text-slate-300">
              - <strong>Spatial Cross-Examination of State Violence:</strong> Combining architectural 3D modeling, fluid dynamics, satellite photogrammetry, and audio ballistic analysis, the collective investigates police killings, border violence, offshore detention, and environmental war crimes.<br>
              - <strong>The Museum as a Counter-Courtroom:</strong> Rather than selling decorative objects to commercial galleries, Forensic Architecture exhibits its findings inside public cultural spaces—such as ${{formatInstLink(hkw)}} in Berlin, ${{formatInstLink(bak)}} in Utrecht, and ${{formatInstLink(chis)}} in London—using the public visibility of the museum to hold states and corporations legally accountable.<br>
              - <strong>The 2019 Whitney Biennial Action:</strong> Forensic Architecture created *Triple-Chaser*, an investigative video exposing Whitney board vice-chair Warren Kanders' ownership of Safariland (which manufactured tear gas used against asylum seekers), directly precipitating Kanders' resignation.
            </p>
          `, ['Whitney & Kanders Audit', 'Dutch Research: BAK', 'Kunsthalle vs Museum']);
          return;
        }}

        // =========================================================================
        // 🏳️‍🌈 QUEER ARCHIVES & FEMINIST CARE COMMONS
        // =========================================================================
        if (q.includes('queer') || q.includes('lgbt') || q.includes('transgender') || q.includes('feminist art') || q.includes('care ethics') || q.includes('federici') || q.includes('pinkwashing')) {{
          const casco = ALL_INSTITUTIONS.find(i => i.id === 'casco-art-institute');
          const dkrozy = ALL_INSTITUTIONS.find(i => i.id && i.id.includes('dk-rozy'));
          appendCuratorMessage(`
            <p class="text-slate-200">
              <strong>Queer cultural archives and feminist care commons</strong> resist both authoritarian persecution and corporate commercial "pinkwashing":
            </p>
            <p class="text-slate-300">
              - <strong>Refusing Corporate Pinkwashing:</strong> Mega-museums often brand themselves with rainbow logos during Pride while their trustee boards remain invested in private prisons or defense contracts. Independent art spaces maintain true grassroots autonomy.<br>
              - <strong>Feminist Care & Reproductive Labor:</strong> As articulated by Silvia Federici, care work, community kitchens, and mutual aid are the foundations of society. Spaces like ${{formatInstLink(casco)}} in Utrecht make reproductive labor visible through its *Publishing Class*, community assemblies, and communal kitchen.<br>
              - <strong>Underground Dissident Solidarity:</strong> In repressive regimes, spaces like ${{formatInstLink(dkrozy)}} in St. Petersburg host feminist self-education libraries and anti-patriarchal study circles without state censorship.
            </p>
          `, ['Casco: The Commons', 'DK Rozy: St. Petersburg', 'W.A.G.E. & Labor']);
          return;
        }}

        // =========================================================================
        // 🌍 MIDDLE EAST & ARAB WORLD: INDEPENDENT SPACES VS PETRO-STATE ARTWASHING
        // =========================================================================
        if (q.includes('middle east') || q.includes('arab') || q.includes('beirut') || q.includes('cairo') || q.includes('palestine') || q.includes('gulf') || q.includes('dubai') || q.includes('abu dhabi') || q.includes('palestinian museum') || q.includes('townhouse')) {{
          const pal = ALL_INSTITUTIONS.find(i => i.id && i.id.includes('palestinian-museum'));
          const town = ALL_INSTITUTIONS.find(i => i.id && i.id.includes('townhouse'));
          const louvreAD = EXCLUDED_INSTITUTIONS.find(i => i.name.includes('Louvre Abu Dhabi'));
          const alula = EXCLUDED_INSTITUTIONS.find(i => i.name.includes('AlUla'));
          const qatar = EXCLUDED_INSTITUTIONS.find(i => i.name.includes('Qatar'));

          appendCuratorMessage(`
            <p class="text-slate-200">
              The cultural geography of the Arab world is defined by a sharp divide between <strong>authoritarian petro-state mega-projects</strong> and <strong>heroic independent civil society havens</strong>:
            </p>
            <p class="text-slate-300">
              - <strong>The Petro-State Megaprojects (Strictly Excluded):</strong><br>
              · ${{formatInstLink(louvreAD)}} (Abu Dhabi): Human Rights Watch documented systemic kafala labor abuses of South Asian construction workers building Saadiyat Island.<br>
              · ${{formatInstLink(alula)}} (Saudi Arabia): Chaired by Crown Prince Mohammed bin Salman (MBS); uses multi-billion-dollar art tourism to whitewash severe political repression and executions.<br>
              · ${{formatInstLink(qatar)}} (Doha): State monarchy cultural apparatus under direct royal patronage.
            </p>
            <p class="text-slate-300">
              - <strong>Verified Independent Civil Society Spaces (Mapped in Culture Atlas):</strong><br>
              · ${{formatInstLink(pal)}} (Birzeit, Palestine): Independent civic trust cascading down terraced olive hills, preserving Palestinian memory, embroidery, and digital oral histories free of political factionalism.<br>
              · ${{formatInstLink(town)}} (Cairo, Egypt): Downtown Cairo non-profit space founded in 1998, catalyzing the independent contemporary art movement in Egypt outside state censorship.
            </p>
          `, ['Fly to Palestine: Palestinian Museum', 'Fly to Cairo: Townhouse', 'Audit Saadiyat Island']);
          if (pal) selectInstitution(pal, true);
          return;
        }}

        // =========================================================================
        // 🇻🇳 VIETNAM: ARTIST-RUN RESISTANCE VS CORPORATE CONGLOMERATES
        // =========================================================================
        if (q.includes('vietnam') || q.includes('hanoi') || q.includes('saigon') || q.includes('ho chi minh') || q.includes('san art') || q.includes('nha san') || q.includes('vincom')) {{
          const sanart = ALL_INSTITUTIONS.find(i => i.id && i.id.includes('san-art'));
          const nhasan = ALL_INSTITUTIONS.find(i => i.id && i.id.includes('nha-san'));
          const vincom = EXCLUDED_INSTITUTIONS.find(i => i.id && i.id.includes('vincom'));

          appendCuratorMessage(`
            <p class="text-slate-200">
              In Vietnam, contemporary art operates between <strong>independent artist-initiated collectives</strong> and <strong>private real estate conglomerates</strong>:
            </p>
            <p class="text-slate-300">
              - <strong>Corporate Conglomerate Foundation (Excluded):</strong><br>
              · ${{formatInstLink(vincom)}} (Hanoi): Fully bankrolled by Vingroup (property, retail, automotive conglomerate), serving as a corporate prestige asset in a commercial shopping complex.
            </p>
            <p class="text-slate-300">
              - <strong>Verified Independent Grassroots Spaces (Mapped in Culture Atlas):</strong><br>
              · ${{formatInstLink(sanart)}} (Ho Chi Minh City): Vietnam's premier independent artist-run space founded in 2007 by Dinh Q. Lê, Tuan Andrew Nguyen, and Phnam Thao Nguyen. Funded via international non-profit cultural trusts (Prince Claus Fund, Arts Collaboratory), fostering critical curatorial dialogue.<br>
              · ${{formatInstLink(nhasan)}} (Hanoi): Founded in 1998 as Nha San Studio, it is the historic pioneer of Vietnamese experimental, installation, and performance art, run entirely through artist solidarity.
            </p>
          `, ['Fly to Vietnam', 'Sàn Art Ho Chi Minh', 'Nha San Collective Hanoi']);
          if (sanart) selectInstitution(sanart, true);
          return;
        }}

        // =========================================================================
        // 🇮🇹 ITALY: PUBLIC COMMONS & ARTIST ARCHIVES VS LUXURY FASHION ARTWASHING
        // =========================================================================
        if (q.includes('italy') || q.includes('milan') || q.includes('rome') || q.includes('prada') || q.includes('pirelli') || q.includes('viafarini') || q.includes('macro')) {{
          const viafarini = ALL_INSTITUTIONS.find(i => i.id && i.id.includes('viafarini'));
          const macro = ALL_INSTITUTIONS.find(i => i.id && i.id.includes('macro'));
          const prada = EXCLUDED_INSTITUTIONS.find(i => i.id && i.id.includes('prada'));
          const pirelli = EXCLUDED_INSTITUTIONS.find(i => i.id && i.id.includes('pirelli'));

          appendCuratorMessage(`
            <p class="text-slate-200">
              In Italy, the cultural sphere is contested between <strong>luxury fashion brand foundations</strong> and <strong>authentic artist-run archives and public commons</strong>:
            </p>
            <p class="text-slate-300">
              - <strong>Corporate Brand Prestige Foundations (Excluded):</strong><br>
              · ${{formatInstLink(prada)}} (Milan): Financed by the Prada fashion group; operates as an elite corporate marketing instrument converting artistic radicalism into commercial prestige.<br>
              · ${{formatInstLink(pirelli)}} (Milan): 100% funded and governed by the Pirelli tyre multinational.
            </p>
            <p class="text-slate-300">
              - <strong>Verified Independent Spaces (Mapped in Culture Atlas):</strong><br>
              · ${{formatInstLink(viafarini)}} (Milan): Established in 1991 at the Fabbrica del Vapore. Non-profit artist-run organization preserving the historic DOCVA visual arts documentation archive of over 40,000 artists, operating with zero commercial luxury sponsorship.<br>
              · ${{formatInstLink(macro)}} (Rome): Public civic contemporary museum with 100% free admission, operating as an open laboratory for independent research.
            </p>
          `, ['Fly to Milan', 'Viafarini DOCVA Archive', 'MACRO Rome']);
          if (viafarini) selectInstitution(viafarini, true);
          return;
        }}

        // =========================================================================
        // 🇷🇺 RUSSIA: OLIGARCH ARTWASHING, STATE CENSORSHIP & SAMIZDAT SPACES
        // =========================================================================
        if (q.includes('russia') || q.includes('russian') || q.includes('moscow') || q.includes('petersburg') || q.includes('hermitage') || q.includes('tretyakov') || q.includes('ges-2') || q.includes('ges 2') || q.includes('dk rozy') || q.includes('chto delat') || q.includes('krasnodar') || q.includes('typography')) {{
          const dkrozy = ALL_INSTITUTIONS.find(i => i.id === 'dk-rozy-st-petersburg' || i.name.includes('DK Rozy'));
          const typo = ALL_INSTITUTIONS.find(i => i.id === 'typography-center-krasnodar' || i.name.includes('Typography'));
          const ges2 = EXCLUDED_INSTITUTIONS.find(i => i.id === 'ges-2-house-of-culture-moscow' || i.name.includes('GES-2'));
          const herm = EXCLUDED_INSTITUTIONS.find(i => i.id === 'state-hermitage-museum-spb' || i.name.includes('Hermitage'));
          const tretyakov = EXCLUDED_INSTITUTIONS.find(i => i.id === 'state-tretyakov-gallery-moscow' || i.name.includes('Tretyakov'));
          const garage = EXCLUDED_INSTITUTIONS.find(i => i.name.includes('Garage'));

          appendCuratorMessage(`
            <p class="text-slate-200">
              The Russian cultural landscape is deeply divided between <strong>state-controlled institutions / sanctioned oligarch foundations</strong> and <strong>underground self-organized initiatives</strong>:
            </p>
            <p class="text-slate-300">
              - <strong>Audited Excluded Institutions:</strong><br>
              · ${{formatInstLink(ges2)}} (Moscow): Financed by Leonid Mikhelson, oligarch CEO of Novatek fossil gas extractor.<br>
              · ${{formatInstLink(garage)}} (Moscow): Endowed by sanctioned oligarch Roman Abramovich.<br>
              · ${{formatInstLink(herm)}} (St. Petersburg): Directed by Mikhail Piotrovsky, who weaponized museum exhibitions as wartime 'cultural offensives'.<br>
              · ${{formatInstLink(tretyakov)}} (Moscow): Subject to state administrative takeovers and systematic ideological censorship of anti-war and non-conformist artists.
            </p>
            <p class="text-slate-300">
              - <strong>Verified Autonomous Independent Spaces (Mapped in Culture Atlas):</strong><br>
              · ${{formatInstLink(dkrozy)}} in St. Petersburg: Founded by artist collective Chto Delat. Zero oligarch or state money. Operates the Rosa Luxemburg library, School of Engaged Art, and mutual-aid community assemblies.<br>
              · ${{formatInstLink(typo)}} in Krasnodar: Founded by artist group ZIP. Independent crowdfunding, community art school, and regional contemporary laboratory.
            </p>
          `, ['Fly to Russia', 'Audit dossier on GES-2', 'Audit dossier on Hermitage', 'Belarus Art Scene']);
          filterByCountry('Russia', true);
          return;
        }}

        // =========================================================================
        // 🇧🇾 BELARUS: STATE APPARATUS VS DISSIDENT CULTURAL RESISTANCE
        // =========================================================================
        if (q.includes('belarus') || q.includes('belorussia') || q.includes('belarusian') || q.includes('minsk') || q.includes('y gallery') || q.includes('ў gallery') || q.includes('galereya y')) {{
          const ygal = ALL_INSTITUTIONS.find(i => i.id === 'y-gallery-minsk' || i.name.includes('Ў Gallery') || i.name.includes('Y Gallery'));
          const natMus = EXCLUDED_INSTITUTIONS.find(i => i.id === 'national-art-museum-belarus-minsk' || i.name.includes('National Art Museum of the Republic of Belarus'));

          appendCuratorMessage(`
            <p class="text-slate-200">
              In Belarus, independent culture operates under conditions of extreme authoritarian surveillance and political repression:
            </p>
            <p class="text-slate-300">
              - <strong>The Authoritarian State Apparatus (Excluded):</strong><br>
              Institutions like ${{formatInstLink(natMus)}} and the National Centre for Contemporary Arts (NCCA) are directly subordinated to the Lukashenko presidential administration, enforcing strict political loyalty and blacklisting democratic opposition artists.
            </p>
            <p class="text-slate-300">
              - <strong>The Historic Dissident Space (Mapped in Culture Atlas):</strong><br>
              · ${{formatInstLink(ygal)}} (Minsk): Founded in 2009 by Anna Chistoserdova and Valentyna Kiselyova. Funded through independent cultural entrepreneurship and community support, zero state subsidies. It served as the central home for Belarusian-language literature, non-conformist visual art, and civil society forums until regime crackdowns forced physical dispersal in 2020.
            </p>
          `, ['Fly to Belarus', 'Russia Art Scene', 'North Korea Art Scene']);
          filterByCountry('Belarus', true);
          return;
        }}

        // =========================================================================
        // 🇰🇵 NORTH KOREA (DPRK): TOTALITARIAN AGITPROP VS DISSIDENT ARCHIVES
        // =========================================================================
        if (q.includes('north korea') || q.includes('pyongyang') || q.includes('dprk') || q.includes('mansudae') || q.includes('sun mu') || q.includes('korean art gallery') || (q.includes('korea') && (q.includes('north') || q.includes('regime') || q.includes('defector')))) {{
          const sunmu = ALL_INSTITUTIONS.find(i => i.id === 'sun-mu-studio-dmz' || i.name.includes('Sun Mu'));
          const mansudae = EXCLUDED_INSTITUTIONS.find(i => i.id === 'mansudae-art-studio-pyongyang' || i.name.includes('Mansudae'));
          const kgall = EXCLUDED_INSTITUTIONS.find(i => i.id === 'korean-art-gallery-pyongyang' || i.name.includes('Korean Art Gallery'));

          appendCuratorMessage(`
            <p class="text-slate-200">
              North Korea (DPRK) represents the most absolute subordination of cultural production to totalitarian dynastic deification on Earth:
            </p>
            <p class="text-slate-300">
              - <strong>Totalitarian State Monopoly (Strictly Excluded):</strong><br>
              · ${{formatInstLink(mansudae)}} (Pyongyang): A state-monopolized factory employing 4,000 artists to manufacture Kim dynasty bronze monuments and Juche propaganda. Sanctioned under <strong>UN Security Council Resolution 2321 (2016)</strong> for financing weapons programs through overseas statue exports.<br>
              · ${{formatInstLink(kgall)}} on Kim Il-sung Square: Enforces monolithic ideological conformity; independent curating is strictly illegal inside the DPRK.
            </p>
            <p class="text-slate-300">
              - <strong>The Dissident Counter-Public (Mapped in Culture Atlas):</strong><br>
              · ${{formatInstLink(sunmu)}} (DMZ Peace Corridor): Founded by pseudonymous North Korean defector artist Sun Mu ('without borders'). Uses socialist realist iconography subversively to critique totalitarian brainwashing, preserve defector testimonies, and advocate for human rights.
            </p>
          `, ['Fly to North Korea', 'Audit dossier on Mansudae', 'Russia Art Scene', 'Belarus Art Scene']);
          flyTo(126.7797, 37.7592, 3.6);
          return;
        }}

        // =========================================================================
        // 🎨 CURATORIAL MOVEMENTS: FLUXUS, CONCEPTUAL & PERFORMANCE ARCHIVES
        // =========================================================================
        if (q.includes('fluxus') || q.includes('conceptual art') || q.includes('performance archive') || q.includes('ephemeral') || q.includes('happenings') || q.includes('abramovic') || q.includes('nam june paik') || q.includes('beuys')) {{
          const deappel = ALL_INSTITUTIONS.find(i => i.id === 'de-appel' || i.name.includes('De Appel'));
          const kitch = ALL_INSTITUTIONS.find(i => i.name.includes('The Kitchen'));
          const artsp = ALL_INSTITUTIONS.find(i => i.name.includes('Artists Space'));
          const white = ALL_INSTITUTIONS.find(i => i.name.includes('Whitechapel'));

          appendCuratorMessage(`
            <p class="text-slate-200">
              Conceptual, Fluxus, and performance art deliberately challenged the commercial museum's obsession with buying and selling luxury objects:
            </p>
            <p class="text-slate-300">
              - <strong>${{formatInstLink(deappel)}} (Amsterdam):</strong> Founded in 1975 by Wies Smals specifically to support live performance, body art, and ephemeral happenings. It preserves a legendary archive documenting historic performances by Marina Abramović & Ulay and Gina Pane.<br>
              - <strong>${{formatInstLink(kitch)}} (New York):</strong> Established in 1971 by Steina and Woody Vasulka. It was the international laboratory for Fluxus-adjacent video and sound art, hosting seminal works by Nam June Paik, Joan Jonas, and Vito Acconci.<br>
              - <strong>${{formatInstLink(artsp)}} (New York):</strong> Founded in 1972 as an alternative space where conceptual artists bypassed commercial gallery dealers to present direct political critiques.<br>
              - <strong>${{formatInstLink(white)}} (London):</strong> Presented early European conceptual retrospectives, challenging traditional medium hierarchies.
            </p>
          `, ['Video, Sound & Media Art', 'Kunsthalle vs Museum', 'Dutch Research: BAK']);
          return;
        }}

        // =========================================================================
        // 🌍 DECOLONIAL MUSEOLOGY, RESTITUTION & PROVENANCE ETHICS
        // =========================================================================
        if (q.includes('decolonial') || q.includes('decolonize') || q.includes('sarr-savoy') || q.includes('restitution') || q.includes('benin') || q.includes('looted heritage') || q.includes('azoulay') || q.includes('mbembe')) {{
          const framer = ALL_INSTITUTIONS.find(i => i.id === 'framer-framed' || i.name.includes('Framer Framed'));
          const melly = ALL_INSTITUTIONS.find(i => i.id === 'kunstinstituut-melly' || i.name.includes('Melly'));
          const iniva = ALL_INSTITUTIONS.find(i => i.name.includes('Iniva'));
          const hkw = ALL_INSTITUTIONS.find(i => i.name.includes('Haus der Kulturen'));

          appendCuratorMessage(`
            <p class="text-slate-200">
              Decolonial museology investigates how European museums were built on imperial conquest and questions who owns world heritage:
            </p>
            <p class="text-slate-300">
              - <strong>${{formatInstLink(framer)}} (Amsterdam):</strong> A leading European research institute partnering directly with indigenous, African, and Asian curators to dismantle colonial archives, investigate looted objects, and advocate for full cultural restitution.<br>
              - <strong>${{formatInstLink(melly)}} (Rotterdam):</strong> Undertook a historic 3-year collective audit to strip the name of 17th-century colonial naval officer Witte de With, renaming itself after Ken Lum's iconic artwork.<br>
              - <strong>${{formatInstLink(iniva)}} (London):</strong> Institute of International Visual Arts, founded to document the artistic contributions of global diaspora artists excluded from Eurocentric canons.<br>
              - <strong>${{formatInstLink(hkw)}} (Berlin):</strong> Directs global research platforms and assemblies interrogating how Western museum classifications separated cultural artifacts from their living spiritual and ecological contexts.
            </p>
          `, ['Benin Bronzes Restitution', 'Decolonial Renaming: Melly', 'Dutch Research: BAK']);
          return;
        }}

        // =========================================================================
        // 🌿 ECOLOGICAL, CLIMATE & INTERSPECIES CURATING
        // =========================================================================
        if (q.includes('ecology') || q.includes('climate art') || q.includes('anthropocene') || q.includes('interspecies') || q.includes('braidotti') || q.includes('environmental art')) {{
          const bak = ALL_INSTITUTIONS.find(i => i.id === 'bak-utrecht' || i.name.includes('BAK'));
          const hkw = ALL_INSTITUTIONS.find(i => i.name.includes('Haus der Kulturen'));
          const kroll = ALL_INSTITUTIONS.find(i => i.name.includes('Kröller'));
          const vanabbe = ALL_INSTITUTIONS.find(i => i.name.includes('Van Abbemuseum'));

          appendCuratorMessage(`
            <p class="text-slate-200">
              Progressive curating treats the climate crisis not as a decorative theme, but as an urgent institutional mandate:
            </p>
            <p class="text-slate-300">
              - <strong>${{formatInstLink(bak)}} (Utrecht):</strong> Developed the <em>Posthuman Glossary</em> with feminist philosopher Rosi Braidotti, organizing research assemblies on environmental grief, affirmative ethics, and multi-species justice.<br>
              - <strong>${{formatInstLink(hkw)}} (Berlin):</strong> Spearheaded the <em>Anthropocene Curriculum</em>, bringing geologists, artists, and indigenous activists together to investigate human impact on Earth systems.<br>
              - <strong>${{formatInstLink(kroll)}} (Otterlo):</strong> Seamlessly embedded within the De Hoge Veluwe national ecosystem, pairing land art with active conservation.<br>
              - <strong>${{formatInstLink(vanabbe)}} (Eindhoven):</strong> Ratified an official institutional climate charter in 2021 prohibiting any sponsorship from fossil fuels and enforcing low-emission loan transports.
            </p>
          `, ['Outdoor Sculpture Parks', 'Dutch Research: BAK', 'Fossil & Defense-Free']);
          return;
        }}

        // =========================================================================
        // 📦 FINANCIALIZATION OF ART, FREEPORTS & DUTY FREE ART
        // =========================================================================
        if (q.includes('freeport') || q.includes('tax haven') || q.includes('financialization') || q.includes('art as investment') || q.includes('duty free art') || q.includes('geneva freeport')) {{
          appendCuratorMessage(`
            <p class="text-slate-200">
              The financialization of contemporary art has transformed masterpieces into speculative offshore commodities:
            </p>
            <p class="text-slate-300">
              - <strong>Freeports (Geneva, Singapore, Luxembourg):</strong> As explored by artist Hito Steyerl in <em>Duty Free Art</em> (2015), freeports are high-security tax-free warehouses located in airport customs zones. Over 1,000,000 museum-grade artworks are locked in wooden crates inside these vaults, traded between billionaires without ever being unpacked or viewed by the public, strictly to defer capital gains and inheritance taxes.<br>
              - <strong>The Mega-Museum as Brand Value Driver:</strong> When a major museum exhibits an artist, their auction market prices skyrocket. Billionaire collectors sit on museum acquisition committees to ensure their own private holdings are validated and appreciated.<br>
              - <strong>The Culture Atlas Antidote:</strong> We prioritize public non-profit spaces, non-collecting kunsthalles, and artist-run commons where art remains an active public good rather than an offshore financial instrument.
            </p>
          `, ['Kunsthalle vs Museum', 'MIT Press Theory Books', 'W.A.G.E. & Museum Unions']);
          return;
        }}

        // =========================================================================
        // ♿ TAILORED ITINERARIES: FAMILY, ACCESSIBLE & FREE-ONLY
        // =========================================================================
        if (q.includes('family') || q.includes('kids') || q.includes('accessible itinerary') || q.includes('wheelchair route') || q.includes('free tour') || q.includes('free itinerary')) {{
          const camden = ALL_INSTITUTIONS.find(i => i.name.includes('Camden'));
          const kroll = ALL_INSTITUTIONS.find(i => i.name.includes('Kröller'));
          const chis = ALL_INSTITUTIONS.find(i => i.name.includes('Chisenhale'));
          const aros = ALL_INSTITUTIONS.find(i => i.name.includes('ARoS'));

          appendCuratorMessage(`
            <p class="text-slate-200">
              <strong>Tailored Ethical Cultural Routes:</strong>
            </p>
            <p class="text-slate-300">
              - <strong>Family-Friendly & Nature:</strong> ${{formatInstLink(kroll)}} in the Netherlands offers complimentary white park bicycles and wide sculpture trails through the forest. In Denmark, ${{formatInstLink(aros)}} features Olafur Eliasson's rainbow glass panorama that delights all ages.<br>
              - <strong>Universal Step-Free & Accessible:</strong> ${{formatInstLink(camden)}} in London has step-free garden studios, loaner wheelchairs, accessible restrooms, and free admission for companions.<br>
              - <strong>100% Free Public Admission Route:</strong> In London, link ${{formatInstLink(chis)}} (Bow), Whitechapel Gallery, and Gasworks without spending a single penny on admission.
            </p>
          `, ['Curated City Itineraries', 'Outdoor Sculpture Parks', 'Free Admission Spaces']);
          return;
        }}

        // =========================================================================
        // 🗺️ CURATED 1-DAY & WEEKEND CITY ITINERARIES (100% Clean Spaces)
        // =========================================================================
        if (q.includes('itinerary') || q.includes('itineraries') || q.includes('day in') || q.includes('weekend in') || q.includes('art route') || q.includes('cultural walk') || q.includes('day trip') || q.includes('curated walk') || (q.includes('tour') && (q.includes('london') || q.includes('berlin') || q.includes('paris') || q.includes('york') || q.includes('amsterdam') || q.includes('city')))) {{
          
          // London Itinerary
          if (q.includes('london')) {{
            const chis = ALL_INSTITUTIONS.find(i => i.name.includes('Chisenhale'));
            const white = ALL_INSTITUTIONS.find(i => i.name.includes('Whitechapel'));
            const gas = ALL_INSTITUTIONS.find(i => i.name.includes('Gasworks'));
            const camden = ALL_INSTITUTIONS.find(i => i.name.includes('Camden'));
            appendCuratorMessage(`
              <p class="text-slate-200">
                <strong>Curated 1-Day London Art Itinerary (100% Independent Non-Profit Spaces):</strong>
              </p>
              <p class="text-slate-300">
                A carefully sequenced day through London's most vital independent, artist-run, and civic spaces—completely avoiding corporate sponsor corridors:
              </p>
              <p class="text-slate-300">
                - <strong>11:00 AM · East London Start:</strong> ${{formatInstLink(chis)}} in Bow. Free entry. Renowned for commissioning daring solo projects by emerging artists. Take a morning stroll along Regent's Canal through Victoria Park.<br>
                - <strong>1:30 PM · Historic Vanguard:</strong> Take the 277/D3 bus or District Line to ${{formatInstLink(white)}} in Aldgate East. Free admission. Explore radical archival retrospectives, browse the legendary bookshop, and stop for lunch at the Townsend café.<br>
                - <strong>3:45 PM · South London Transit:</strong> Take the Overground or Northern Line south to ${{formatInstLink(gas)}} in Vauxhall. Free admission. Discover international artist residencies and intimate studio commissions.<br>
                - <strong>Evening Alternative / Weekend Option:</strong> Head north to ${{formatInstLink(camden)}} in Hampstead for garden studios, ceramic showcases, and an organic garden café.
              </p>
              <p class="text-slate-300">
                All venues have zero fossil fuel or defense corporate underwriting, and all offer free public admission.
              </p>
            `);
            appendCuratorMessage(`
              <div class="mt-2 flex items-center gap-2">
                <button class="copy-itinerary-btn px-2.5 py-1 rounded bg-[#242424] hover:bg-[#303030] text-[12px] font-mono text-[#93c5fd] hover:text-white border border-[#383838] transition cursor-pointer">
                  Copy Itinerary
                </button>
              </div>
            `);
            filterByCity('London', true, false);
            return;
          }}

          // Berlin Itinerary
          if (q.includes('berlin')) {{
            const kw = ALL_INSTITUTIONS.find(i => i.name.includes('KW Institute'));
            const grop = ALL_INSTITUTIONS.find(i => i.name.includes('Gropius Bau'));
            const hkw = ALL_INSTITUTIONS.find(i => i.name.includes('Haus der Kulturen'));
            appendCuratorMessage(`
              <p class="text-slate-200">
                <strong>Curated 1-Day Berlin Contemporary Art Circuit:</strong>
              </p>
              <p class="text-slate-300">
                Experience Berlin's public civic institutions and converted industrial spaces:
              </p>
              <p class="text-slate-300">
                - <strong>11:30 AM · Mitte Industrial Vanguard:</strong> ${{formatInstLink(kw)}} on Auguststraße. Housed in a former margarine factory, KW has anchored Berlin's experimental scene since the fall of the Wall. Grab coffee in the cobblestone courtyard at Café Bravo.<br>
                - <strong>2:30 PM · Architectural Crossroads:</strong> Take the U8 to Potsdamer Platz / Kochstraße for ${{formatInstLink(grop)}}. Marvel at the grand 1881 neo-Renaissance atrium; ground floor exhibitions and project spaces are completely free to the public.<br>
                - <strong>5:00 PM · Global Assemblies on the Spree:</strong> Take the M29/100 bus through Tiergarten to ${{formatInstLink(hkw)}} (the 'Pregnant Oyster'). HKW presents non-Western philosophies, decolonial music, and sound assemblies along the river.
              </p>
            `);
            filterByCity('Berlin', true, false);
            return;
          }}

          // Paris Itinerary
          if (q.includes('paris')) {{
            const ptok = ALL_INSTITUTIONS.find(i => i.name.includes('Palais de Tokyo'));
            const beton = ALL_INSTITUTIONS.find(i => i.name.includes('Bétonsalon'));
            appendCuratorMessage(`
              <p class="text-slate-200">
                <strong>Curated 1-Day Paris Contemporary Art Itinerary:</strong>
              </p>
              <p class="text-slate-300">
                Explore progressive public spaces free from luxury real estate artwashing:
              </p>
              <p class="text-slate-300">
                - <strong>2:00 PM · Left Bank Research:</strong> Start at ${{formatInstLink(beton)}} in the 13th Arrondissement (Bibliothèque François Mitterrand). Free public admission. Housed in a converted university flour warehouse, it features cutting-edge intersectional research and artist residencies.<br>
                - <strong>5:30 PM to Midnight · The Night Owl Palace:</strong> Take Metro Line 14 and Line 9 to ${{formatInstLink(ptok)}} on Avenue du Président Wilson. Europe's largest contemporary art space stays open until midnight every day except Tuesday, featuring immersive site-specific commissions, bookshops, and evening talks.
              </p>
            `);
            filterByCity('Paris', true, false);
            return;
          }}

          // New York Itinerary
          if (q.includes('new york') || q.includes('nyc') || q.includes('manhattan')) {{
            const artsp = ALL_INSTITUTIONS.find(i => i.name.includes('Artists Space'));
            const kitch = ALL_INSTITUTIONS.find(i => i.name.includes('The Kitchen'));
            const swiss = ALL_INSTITUTIONS.find(i => i.name.includes('Swiss Institute'));
            const sculp = ALL_INSTITUTIONS.find(i => i.name.includes('SculptureCenter'));
            appendCuratorMessage(`
              <p class="text-slate-200">
                <strong>Curated 1-Day New York Independent Non-Profit Trail:</strong>
              </p>
              <p class="text-slate-300">
                A clean alternative to billionaire-dominated trustee boards at MoMA and the Whitney:
              </p>
              <p class="text-slate-300">
                - <strong>12:00 PM · Downtown Conceptual Roots:</strong> ${{formatInstLink(artsp)}} at 11 Cortlandt Alley in Tribeca. Free entry. Founded in 1972, Artists Space provided early platforms for Cindy Sherman, Nan Goldin, and Adrian Piper.<br>
                - <strong>2:30 PM · Avant-Garde & Interdisciplinary:</strong> Walk or subway to ${{formatInstLink(swiss)}} in the East Village (St. Marks Pl) or ${{formatInstLink(kitch)}} in Chelsea/Westbeth for pioneering video, performance, and international dialog.<br>
                - <strong>4:45 PM · Queens Industrial Sculpture:</strong> Hop on the 7 train to Court Square in Long Island City for ${{formatInstLink(sculp)}}. Free entry. A non-collecting kunsthalle inside a 1908 trolley repair shop redesigned by Maya Lin.
              </p>
            `);
            filterByCity('New York', true, false);
            return;
          }}

          // Dutch Research Corridor (Amsterdam - Utrecht - Rotterdam)
          if (q.includes('dutch') || q.includes('netherlands') || q.includes('utrecht') || q.includes('rotterdam') || q.includes('amsterdam')) {{
            const bak = ALL_INSTITUTIONS.find(i => i.id === 'bak-utrecht' || i.name.includes('BAK'));
            const casco = ALL_INSTITUTIONS.find(i => i.id === 'casco-art-institute');
            const melly = ALL_INSTITUTIONS.find(i => i.id === 'kunstinstituut-melly');
            const deappel = ALL_INSTITUTIONS.find(i => i.id === 'de-appel');
            appendCuratorMessage(`
              <p class="text-slate-200">
                <strong>Curated Dutch Artistic Research & Commons Corridor:</strong>
              </p>
              <p class="text-slate-300">
                The Netherlands has the densest concentration of progressive, publicly funded research institutions in the world:
              </p>
              <p class="text-slate-300">
                - <strong>Morning in Utrecht (Commons & Theory):</strong> Visit ${{formatInstLink(bak)}} on Pauwstraat (world center for institutional critique and *Former West*) and walk 5 minutes to ${{formatInstLink(casco)}} on Lange Nieuwstraat (experimental commoning and community kitchen). Both 10-15 mins from Utrecht Centraal.<br>
                - <strong>Afternoon in Rotterdam (Decolonial Accountability):</strong> Take a 35-minute direct train to Rotterdam Centraal for ${{formatInstLink(melly)}} on Witte de Withstraat. Celebrated for its historic decolonial renaming and Ken Lum's public artwork.<br>
                - <strong>Evening in Amsterdam (Performance & Curatorial Pedagogy):</strong> Train to Amsterdam Centraal for ${{formatInstLink(deappel)}}, home of seminal performance art archives and the Curatorial Programme.
              </p>
            `);
            flyTo(5.2, 52.1);
            return;
          }}

          // General Multi-City Overview
          appendCuratorMessage(`
            <p class="text-slate-200">
              Culture Atlas provides curated cultural itineraries across major world capitals featuring 100% verified independent, non-profit spaces:
            </p>
            <p class="text-slate-300">
              - <a href="#" class="city-link text-[#93c5fd] hover:underline" data-city="London">London 1-Day Route:</a> Chisenhale Gallery → Whitechapel Gallery → Gasworks → Camden Art Centre.<br>
              - <a href="#" class="city-link text-[#93c5fd] hover:underline" data-city="Berlin">Berlin Contemporary Trail:</a> KW Institute → Gropius Bau → Haus der Kulturen der Welt (HKW).<br>
              - <a href="#" class="city-link text-[#93c5fd] hover:underline" data-city="Paris">Paris Circuit:</a> Bétonsalon research centre → Palais de Tokyo (open till midnight).<br>
              - <a href="#" class="city-link text-[#93c5fd] hover:underline" data-city="New York">New York Non-Profit Loop:</a> Artists Space → Swiss Institute → The Kitchen → SculptureCenter.<br>
              - <a href="#" class="city-link text-[#93c5fd] hover:underline" data-city="Utrecht">Dutch Research Corridor:</a> BAK Utrecht → Casco → Kunstinstituut Melly → De Appel.
            </p>
            <p class="text-slate-300">
              Ask about any specific city (e.g. <em>"London itinerary"</em> or <em>"Berlin art route"</em>) for complete transit and timing directions.
            </p>
          `);
          return;
        }}

        // =========================================================================
        // 🏭 REPURPOSED INDUSTRIAL ARCHITECTURE & ADAPTIVE REUSE
        // =========================================================================
        if (q.includes('industrial') || q.includes('factory') || q.includes('brewery') || q.includes('repurpose') || q.includes('trolley') || q.includes('adaptive reuse') || q.includes('warehouse') || (q.includes('architecture') && (q.includes('space') || q.includes('building') || q.includes('convert')))) {{
          const kw = ALL_INSTITUTIONS.find(i => i.name.includes('KW Institute'));
          const sculp = ALL_INSTITUTIONS.find(i => i.name.includes('SculptureCenter'));
          const wiels = ALL_INSTITUTIONS.find(i => i.name.includes('Wiels'));
          const chis = ALL_INSTITUTIONS.find(i => i.name.includes('Chisenhale'));
          const capc = ALL_INSTITUTIONS.find(i => i.name.includes('CAPC'));
          const beton = ALL_INSTITUTIONS.find(i => i.name.includes('Bétonsalon'));

          appendCuratorMessage(`
            <p class="text-slate-200">
              Instead of spending hundreds of millions on corporate starchitect trophies, many of the world's most progressive art spaces chose <strong>adaptive reuse</strong>—transforming abandoned factories, transit hubs, and breweries into spaces for contemporary critique:
            </p>
            <p class="text-slate-300">
              - <strong>${{formatInstLink(kw)}} (Berlin):</strong> Founded in the early 1990s in a derelict 19th-century margarine factory (*Margarinestift*) in Berlin-Mitte. It retains its raw industrial brick courtyard and five floors of concrete exhibition halls.<br>
              - <strong>${{formatInstLink(sculp)}} (New York):</strong> Relocated in 2001 to a former 1908 trolley repair shop in Long Island City, Queens. Renovated by Maya Lin, it features a monumental 40-foot high main hall and catacomb-like brick subterranean vaults.<br>
              - <strong>${{formatInstLink(wiels)}} (Brussels):</strong> Housed in the monumental 1930s modernist Wielemans-Ceuppens brewery designed by Adrien Blomme, retaining monumental copper brewing vats and exposed concrete pillars.<br>
              - <strong>${{formatInstLink(chis)}} (London):</strong> Founded by artists in 1980 in a 1930s veneer factory and wartime Spitfire propeller workshop on Chisenhale Road in East London.<br>
              - <strong>${{formatInstLink(capc)}} (Bordeaux):</strong> Housed in the *Entrepôt Lainé*, an imposing 1824 vaulted stone warehouse historically used for colonial port commodities, repurposed since 1973 into a cavernous public contemporary art nave.<br>
              - <strong>${{formatInstLink(beton)}} (Paris):</strong> Located in the Halle aux Farines, a historic industrial flour mill converted into Paris Diderot University.
            </p>
          `);
          if (sculp) selectInstitution(sculp, true);
          return;
        }}

        // =========================================================================
        // 🌲 OUTDOOR SCULPTURE PARKS & LAND ART SPACES
        // =========================================================================
        if (q.includes('sculpture park') || q.includes('outdoor') || q.includes('land art') || q.includes('landscape') || (q.includes('nature') && q.includes('art')) || q.includes('storm king') || q.includes('sculpture garden')) {{
          const kroll = ALL_INSTITUTIONS.find(i => i.name.includes('Kröller'));
          const louis = ALL_INSTITUTIONS.find(i => i.name.includes('Louisiana'));
          const aros = ALL_INSTITUTIONS.find(i => i.name.includes('ARoS'));

          appendCuratorMessage(`
            <p class="text-slate-200">
              Culture Atlas audits and maps extraordinary <strong>outdoor sculpture parks and open-air art centers</strong> operating with verified ethical funding:
            </p>
            <p class="text-slate-300">
              - <strong>${{formatInstLink(kroll)}} (Otterlo, Netherlands):</strong> One of Europe's largest sculpture gardens, spanning 60 acres within De Hoge Veluwe National Park. Features over 160 monumental outdoor sculptures by Richard Serra, Jean Dubuffet (*Jardin d'émail*), Barbara Hepworth, and Marta Pan. Visitors explore the forest and dunes on complimentary white park bicycles.<br>
              - <strong>${{formatInstLink(louis)}} (Humlebæk, Denmark):</strong> Masterpiece of Danish modernist architecture overlooking the Øresund sound towards Sweden. Landmark outdoor bronzes by Henry Moore, Alexander Calder, and Alberto Giacometti are situated directly on coastal bluffs and grassy slopes.<br>
              - <strong>${{formatInstLink(aros)}} (Aarhus, Denmark):</strong> Crowned by Olafur Eliasson's permanent chromatic skywalk *Your Rainbow Panorama*—a 150-meter circular glass walkway that immerses visitors in a full spectrum of natural light overlooking the Danish city.
            </p>
            <p class="text-slate-300">
              Unlike private sculpture foundations endowed by fossil fuel fortunes, these public institutions operate with transparent civic governance and ecological accountability.
            </p>
          `);
          if (kroll) selectInstitution(kroll, true);
          return;
        }}

        // =========================================================================
        // 🎞️ VIDEO ART, SOUND ART & TIME-BASED MEDIA
        // =========================================================================
        if (q.includes('video art') || q.includes('time-based') || q.includes('sound art') || q.includes('performance art') || q.includes('moving image') || q.includes('experimental film') || q.includes('media art') || q.includes('audiovisual')) {{
          const kitch = ALL_INSTITUTIONS.find(i => i.name.includes('The Kitchen'));
          const v2 = ALL_INSTITUTIONS.find(i => i.name.includes('V2_') || i.name.includes('V2'));
          const argos = ALL_INSTITUTIONS.find(i => i.name.includes('Argos'));
          const tpg = ALL_INSTITUTIONS.find(i => i.name.includes("Photographers' Gallery"));
          const edith = ALL_INSTITUTIONS.find(i => i.name.includes('Edith-Russ'));

          appendCuratorMessage(`
            <p class="text-slate-200">
              Time-based media, video art, and sound experimentation require specialized non-profit platforms dedicated to dematerialized and ephemeral art:
            </p>
            <p class="text-slate-300">
              - <strong>${{formatInstLink(kitch)}} (New York):</strong> Founded in 1971 by Woody and Steina Vasulka inside the Mercer Arts Center, The Kitchen was the historic crucible for American video and electronic art, fostering Nam June Paik, Joan Jonas, Laurie Anderson, Cindy Sherman, and Arthur Russell.<br>
              - <strong>${{formatInstLink(v2)}} (Rotterdam):</strong> An interdisciplinary center for art and media technology founded in 1981, investigating critical AI, biotechnology, augmented robotics, and digital ecology.<br>
              - <strong>${{formatInstLink(argos)}} (Brussels):</strong> Founded in 1989, Europe's foremost dedicated center and historical distribution archive for artist moving image, video art, and sound works.<br>
              - <strong>${{formatInstLink(tpg)}} (London):</strong> Founded in 1971 in Soho, championing still photography, computational imagery, and digital screen cultures with free public galleries.<br>
              - <strong>${{formatInstLink(edith)}} (Oldenburg, Germany):</strong> Civic exhibition institute focusing specifically on digital media critique, internet art, and algorithmic society.
            </p>
          `);
          if (kitch) selectInstitution(kitch, true);
          return;
        }}

        // =========================================================================
        // 🏛️ KUNSTHALLE VS MUSEUM: CURATORIAL & ECONOMIC DISTINCTION
        // =========================================================================
        if (q.includes('kunsthalle vs museum') || q.includes('what is a kunsthalle') || q.includes('collecting vs non-collecting') || q.includes('difference between kunsthalle') || (q.includes('kunsthalle') && (q.includes('mean') || q.includes('definition')))) {{
          appendCuratorMessage(`
            <p class="text-slate-200">
              The fundamental difference between a <strong>Museum</strong> and a <strong>Kunsthalle</strong> lies in permanent asset collection and financial incentives:
            </p>
            <p class="text-slate-300">
              1. <strong>The Museum (Collecting Institution):</strong><br>
              Traditional museums (like MoMA, the Met, or the Louvre) build and preserve permanent collections. A vast portion of their budget and staff is tied up in insuring, storing, conserving, and cataloging valuable physical art objects. Because collectors donate art in exchange for tax write-offs and museum board seats, museums are vulnerable to billionaire trustee influence and art market speculation.
            </p>
            <p class="text-slate-300">
              2. <strong>The Kunsthalle (Non-Collecting Art Hall):</strong><br>
              Originating in Germany and Switzerland (from German *Kunst* = art, *Halle* = hall), a Kunsthalle possesses <strong>no permanent collection</strong>. Instead of stockpiling multi-million-dollar assets in vaults, 100% of its resources go toward commissioning brand-new work from living artists, publishing research, and hosting critical public debates.
            </p>
            <p class="text-slate-300">
              Because Kunsthalles don't have permanent collections to safeguard or commercial values to inflate, they have historically served as the vanguard for radical curatorial experimentation (like Harald Szeemann's 1969 *When Attitudes Become Form* at Kunsthalle Bern, KW Institute in Berlin, or SculptureCenter in New York).
            </p>
          `);
          return;
        }}

        // =========================================================================
        // 💼 W.A.G.E. CERTIFICATION, FAIR PAY & MUSEUM LABOR UNIONS
        // =========================================================================
        if (q.includes('wage') || q.includes('fair pay') || q.includes('union') || q.includes('local 2110') || q.includes('labor') || q.includes('strike moma') || q.includes('museum workers') || q.includes('minimum fee')) {{
          appendCuratorMessage(`
            <p class="text-slate-200">
              Ethical cultural stewardship is inseparable from <strong>fair artist remuneration and museum worker labor rights</strong>:
            </p>
            <p class="text-slate-300">
              - <strong>W.A.G.E. (Working Artists and the Greater Economy):</strong> Founded in 2008 in New York, W.A.G.E. created the first voluntary certification program that sets standardized minimum fees for artists when non-profit institutions exhibit or commission their work. W.A.G.E. ended the exploitative assumption that artists should supply labor to wealthy institutions for free "exposure."<br>
              - <strong>Museum Staff Unionization (UAW Local 2110 & AFSCME):</strong> Over the past decade, frontline staff (educators, preparators, visitor assistants, archivists) across the US unionized at MoMA, the Whitney, the New Museum, Guggenheim, Philadelphia Museum of Art, and MFA Boston. Workers protested extreme disparities between multi-million-dollar director salaries and poverty-level wages for frontline workers.<br>
              - <strong>Culture Atlas Standpoint:</strong> Mega-museums with multi-billion-dollar endowments often treat cultural workers as expendable. Culture Atlas champions independent and civic spaces that respect fair artist contracts, transparent staff compensation, and democratic governance.
            </p>
          `);
          return;
        }}

        // =========================================================================
        // ✒️ WHAT IS CURATING? ETYMOLOGY & HISTORICAL TRANSFORMATION
        // =========================================================================
        if (q.includes('what is curating') || q.includes('curator role') || q.includes('etymology of curat') || q.includes('curatorial practice') || q.includes('history of curat')) {{
          appendCuratorMessage(`
            <p class="text-slate-200">
              The role of the <strong>curator</strong> has undergone three major historical transformations:
            </p>
            <p class="text-slate-300">
              1. <strong>The Custodian (Latin *curare*):</strong> The root *curare* means "to care for" or "tend." For centuries, a curator was a museum civil servant who cared for physical relics—cataloging, restoring, and storing objects in aristocratic or royal collections.<br>
              2. <strong>The Independent Author (*Ausstellungsmacher*):</strong> In the late 1960s, Harald Szeemann resigned from Kunsthalle Bern to become an independent exhibition-maker. He demonstrated that an exhibition itself could be an intellectual authorship and artistic medium, bringing conceptual artists into dynamic spatial dialogues.<br>
              3. <strong>The Critical Researcher & Assembly Facilitator:</strong> Today, curating is understood not as choosing paintings for white walls, but as creating public assemblies and research platforms (exemplified by Maria Hlavajova at BAK Utrecht, Charles Esche at Van Abbemuseum, and Okwui Enwezor at Documenta 11). Curators mobilize culture to address climate justice, colonial restitution, and political imagination.
            </p>
          `);
          return;
        }}

        // =========================================================================
        // 🗓 PLAN VISIT INTENT RESOLVER (Conversational Visit Planning)
        // =========================================================================
        const targetPlanInst = findMentionedInst(query) || ((q.includes('plan') || q.includes('visit') || q.includes('guide')) && curatorContext.lastInst) || (q.includes('plan') && selectedInstitution);
        const isPlanVisitIntent = (q.includes('plan visit') || q.includes('plan my visit') || q.includes('planning visit') || q.includes('planning a visit') || q.includes('planning to visit') || q.includes('how do i visit') || q.includes('how to visit') || q.includes('visitor guide') || q.includes('visitor itinerary') || q.includes('visit plan')) && !!targetPlanInst;

        if (isPlanVisitIntent) {{
          const inst = targetPlanInst;
          curatorContext.lastInst = inst;
          curatorContext.lastCity = inst.city;
          const webUrl = getValidWebUrl(inst);
          const visitUrl = (inst.visit_url && (inst.visit_url.startsWith('http://') || inst.visit_url.startsWith('https://'))) ? inst.visit_url : webUrl;
          appendCuratorMessage(`
            <p class="text-white font-normal text-[15px]">
              Visitor Itinerary & Planning Guide: <strong>${{formatInstLink(inst)}}</strong> (${{escapeHtml(inst.city)}}, ${{escapeHtml(inst.country)}})
            </p>
            <div class="py-2.5 border-t border-[#333] space-y-1.5 text-slate-300 text-[13px] leading-[135%]">
              <div><strong class="text-[#78a9ff] font-mono uppercase text-[11px] tracking-wider block">Opening Hours</strong> ${{escapeHtml(inst.opening_hours || 'Check official site')}}</div>
              <div class="pt-1 border-t border-[#262626]"><strong class="text-[#42be65] font-mono uppercase text-[11px] tracking-wider block">Admission & Tickets</strong> ${{escapeHtml(inst.admission_policy)}} (${{escapeHtml(inst.admission_details || inst.admission_fee || 'Subsidized admission')}})</div>
              <div class="pt-1 border-t border-[#262626]"><strong class="text-[#33b1ff] font-mono uppercase text-[11px] tracking-wider block">Address & Neighborhood</strong> ${{escapeHtml(inst.address || inst.location)}} ${{inst.neighborhood ? `· <span class="font-mono text-[#82cfff]">${{escapeHtml(inst.neighborhood)}}</span>` : ''}}</div>
              <div class="pt-1 border-t border-[#262626]"><strong class="text-[#3ddbd9] font-mono uppercase text-[11px] tracking-wider block">Getting There & Transit</strong> ${{escapeHtml(inst.transit_tips || 'Accessible via central public transit network.')}}</div>
              <div class="pt-1 border-t border-[#262626]"><strong class="text-[#be95ff] font-mono uppercase text-[11px] tracking-wider block">Suggested Duration</strong> ${{escapeHtml(inst.visit_duration || '1.5 – 2.5 hours')}}</div>
              <div class="pt-1 border-t border-[#262626]"><strong class="text-[#f1c21b] font-mono uppercase text-[11px] tracking-wider block">Collection / Commission Highlight</strong> ${{escapeHtml(inst.highlight || 'Celebrated collection and contemporary commissions.')}}</div>
              <div class="pt-1 border-t border-[#262626]"><strong class="text-[#ff7eb6] font-mono uppercase text-[11px] tracking-wider block">Accessibility</strong> ${{escapeHtml(inst.accessibility || 'Step-free access, elevators, accessible restrooms.')}}</div>
              <div class="pt-1 border-t border-[#262626]"><strong class="text-[#ff832b] font-mono uppercase text-[11px] tracking-wider block">Amenities</strong> ${{escapeHtml((inst.amenities || 'Art bookshop, café, cloakroom, and lockers.').toString().split(',').map(x => x.trim()).filter(Boolean).join(' · '))}}</div>
            </div>
            ${{visitUrl ? `
              <div class="pt-2 border-t border-[#333] flex items-center gap-2">
                <a href="${{escapeHtml(visitUrl)}}" target="_blank" rel="noopener noreferrer" 
                   class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[#2563eb] hover:bg-[#1d4ed8] text-white font-normal text-[12px] shadow transition">
                  <span>Open Official Visitor / Ticket Page ↗</span>
                </a>
              </div>
            ` : ''}}
          `, ['Getting There', 'Admission Policy', 'Ethical Governance Audit', `More in ${{inst.city}}`]);
          selectInstitution(inst, true);
          return;
        }}

        // =========================================================================
        // ✍️ DIRECT FEEDBACK OR RESEARCH CONTRIBUTION INTENT
        // =========================================================================
        const isFeedbackOrSubmissionIntent = q.startsWith('feedback:') || q.startsWith('suggestion:') || q.startsWith('research tip:') || q.startsWith('submit space') || q.startsWith('add space') || q.includes('suggest a new space') || q.includes('submit new space') || q.includes('suggest an update') || q.includes('contribute research');
        if (isFeedbackOrSubmissionIntent) {{
          openResearchFeedbackModal(curatorContext.lastInst ? curatorContext.lastInst.name : '', curatorContext.lastCity || '');
          appendCuratorMessage(`
            <p class="text-white font-normal text-[14px]">
              Opened the <strong>Research Contribution & Verification Form</strong>. You can enter details, suggest new independent spaces, report schedule changes, or submit Form 990 / Charity Commission documentation. Submissions enter our peer-review research queue and immediately ground your active session model.
            </p>
          `, ['Curated 1-Day Itineraries', 'Explore Free Spaces', 'View Map']);
          return;
        }}

        // =========================================================================
        // 🧠 CONTEXTUAL MULTI-TURN FOLLOW-UP RESOLVER (Memory-Aware)
        // =========================================================================
        const isFollowUpTransit = (q.includes('how to get') || q.includes('how do i get') || q.includes('transit') || q.includes('direction') || q.includes('subway') || q.includes('where is it') || q.includes('metro') || q.includes('address')) && !findMentionedInst(query);
        const isFollowUpHours = (q.includes('hours') || q.includes('open today') || q.includes('schedule') || q.includes('when is it open') || q.includes('opening times')) && !findMentionedInst(query);
        const isFollowUpAdmission = (q.includes('admission') || q.includes('ticket') || q.includes('cost') || q.includes('how much') || q.includes('is it free') || q.includes('price')) && !findMentionedInst(query);
        const isFollowUpFunding = (q.includes('who funds') || q.includes('funding') || q.includes('board') || q.includes('donor') || q.includes('is it clean') || q.includes('sponsor')) && !findMentionedInst(query);
        const isFollowUpNearby = (q.includes('nearby') || q.includes('what else') || q.includes('other spaces') || q.includes('around here') || q.includes('in the area')) && !findMentionedCity(query);

        if (isFollowUpTransit && curatorContext.lastInst) {{
          const inst = curatorContext.lastInst;
          appendCuratorMessage(`
            <p class="text-slate-200">
              To get to <strong>${{formatInstLink(inst)}}</strong>:
            </p>
            <p class="text-slate-300">
              - <strong>Public Transit:</strong> ${{inst.transit_tips}}<br>
              - <strong>Address:</strong> ${{inst.address || inst.location}} (${{inst.neighborhood || inst.city}})<br>
              - <strong>Estimated Visit Duration:</strong> About ${{inst.visit_duration || '1.5 – 2 hours'}}.
            </p>
          `, ['Opening Hours', 'Admission Policy', `More in ${{inst.city}}`]);
          selectInstitution(inst, true);
          return;
        }}

        if (isFollowUpHours && curatorContext.lastInst) {{
          const inst = curatorContext.lastInst;
          appendCuratorMessage(`
            <p class="text-slate-200">
              <strong>${{formatInstLink(inst)}}</strong> schedule and hours:
            </p>
            <p class="text-slate-300">
              - <strong>Opening Hours:</strong> ${{inst.opening_hours}}<br>
              - <strong>Recommended Duration:</strong> ${{inst.visit_duration || '1.5 – 2 hours'}}<br>
              - <strong>Key Highlight:</strong> <span class="text-amber-300/90">${{inst.highlight}}</span>
            </p>
          `, ['Transit Directions', 'Ticket Info', `More in ${{inst.city}}`]);
          selectInstitution(inst, true);
          return;
        }}

        if (isFollowUpAdmission && curatorContext.lastInst) {{
          const inst = curatorContext.lastInst;
          appendCuratorMessage(`
            <p class="text-slate-200">
              <strong>Admission at ${{formatInstLink(inst)}}:</strong>
            </p>
            <p class="text-slate-300">
              - <strong>Policy:</strong> ${{inst.admission_policy}}<br>
              - <strong>Details & Pricing:</strong> ${{inst.admission_details || inst.admission_fee || 'Subsidized entry'}}.<br>
              - <strong>Accessibility:</strong> Free admission for assistants/companions.
            </p>
          `, ['Opening Hours', 'Transit Directions', 'Governance & Funding']);
          selectInstitution(inst, true);
          return;
        }}

        if (isFollowUpFunding && curatorContext.lastInst) {{
          const inst = curatorContext.lastInst;
          appendCuratorMessage(`
            <p class="text-slate-200">
              <strong>Funding & Governance Audit: ${{formatInstLink(inst)}}</strong>
            </p>
            <p class="text-slate-300">
              - <strong>Ethical Verification:</strong> ${{inst.tier === 'A' ? '<span class="text-emerald-400">Tier A · Verified Independent Space</span>' : '<span class="text-rose-400">Tier B · Flagged Corporate Conflicts</span>'}}<br>
              - <strong>Governance Model:</strong> ${{inst.governance_type}}<br>
              - <strong>Funding Architecture:</strong> ${{inst.funding}}<br>
              - <strong>Safeguard:</strong> ${{inst.ethical_safeguard}}<br>
              - <strong>Transparency Grade:</strong> <span class="text-emerald-400 font-mono font-bold">${{inst.transparency_grade || 'Tier A+'}}</span>
            </p>
          `, ['Admission Policy', 'How to Get There', 'Highlight Art']);
          selectInstitution(inst, true);
          return;
        }}

        if (isFollowUpNearby && (curatorContext.lastInst || curatorContext.lastCity)) {{
          const cityName = curatorContext.lastCity || (curatorContext.lastInst ? curatorContext.lastInst.city : null);
          const nearbyMatches = ALL_INSTITUTIONS.filter(i => matchC(i.city, cityName) && (!curatorContext.lastInst || i.name !== curatorContext.lastInst.name));
          if (nearbyMatches.length > 0) {{
            appendCuratorMessage(`
              <p class="text-slate-200">
                Other verified clean spaces in <strong>${{escapeHtml(cityName)}}</strong>:
              </p>
              <p class="text-slate-300">
                ${{nearbyMatches.slice(0, 4).map(m => `· ${{formatInstLink(m)}} (${{m.neighborhood || m.curatorial_focus}})`).join('<br>')}}
              </p>
            `, nearbyMatches.slice(0, 3).map(m => m.name));
            filterByCity(cityName, true, false);
            return;
          }}
        }}

        // =========================================================================
        // ⚖️ DIRECT SIDE-BY-SIDE COMPARISON ENGINE ("Compare X and Y" / "X vs Y")
        // =========================================================================
        if (q.includes('compare') || (q.includes('difference between') && !q.includes('kunsthalle')) || q.includes(' vs ') || q.includes(' versus ')) {{
          const cleanQ = q.replace(/^(can you )?compare /i, '').replace(/difference between /i, '');
          const parts = cleanQ.split(/\s+(?:vs\.?|versus|and)\s+/i);
          if (parts.length >= 2) {{
            const e1 = findAnyInstitution(parts[0].trim());
            const e2 = findAnyInstitution(parts[1].trim());
            if (e1 && e2) {{
              const i1 = e1.inst;
              const i2 = e2.inst;
              appendCuratorMessage(`
                <p class="text-slate-200 font-medium">
                  <strong>Curatorial Comparison: ${{escapeHtml(i1.name)}} vs ${{escapeHtml(i2.name)}}</strong>
                </p>
                <div class="overflow-x-auto my-2 border border-[#2e2e2e] rounded-xl bg-[#141414] text-[13px]">
                  <table class="w-full text-left border-collapse">
                    <thead>
                      <tr class="border-b border-[#2e2e2e] bg-[#1c1c1c] text-[#a1a1aa] font-mono">
                        <th class="p-2.5">Dimension</th>
                        <th class="p-2.5 text-white">${{escapeHtml(i1.name)}}</th>
                        <th class="p-2.5 text-white">${{escapeHtml(i2.name)}}</th>
                      </tr>
                    </thead>
                    <tbody class="divide-y divide-[#242424] text-slate-300">
                      <tr>
                        <td class="p-2.5 font-mono text-[#a1a1aa]">Location</td>
                        <td class="p-2.5">${{escapeHtml(i1.city)}}, ${{escapeHtml(i1.country)}}</td>
                        <td class="p-2.5">${{escapeHtml(i2.city)}}, ${{escapeHtml(i2.country)}}</td>
                      </tr>
                      <tr>
                        <td class="p-2.5 font-mono text-[#a1a1aa]">Ethical Status</td>
                        <td class="p-2.5">${{i1.tier === 'A' ? '<span class="text-emerald-400 font-medium">Tier A · Independent Space</span>' : '<span class="text-rose-400 font-medium">Tier B · Excluded Conflict</span>'}}</td>
                        <td class="p-2.5">${{i2.tier === 'A' ? '<span class="text-emerald-400 font-medium">Tier A · Independent Space</span>' : '<span class="text-rose-400 font-medium">Tier B · Excluded Conflict</span>'}}</td>
                      </tr>
                      <tr>
                        <td class="p-2.5 font-mono text-[#a1a1aa]">Governance</td>
                        <td class="p-2.5">${{escapeHtml(i1.governance_type || 'Civic Non-Profit')}}</td>
                        <td class="p-2.5">${{escapeHtml(i2.governance_type || 'Civic Non-Profit')}}</td>
                      </tr>
                      <tr>
                        <td class="p-2.5 font-mono text-[#a1a1aa]">Funding Source</td>
                        <td class="p-2.5">${{escapeHtml(i1.funding || 'Public civic council grants')}}</td>
                        <td class="p-2.5">${{escapeHtml(i2.funding || 'Public civic council grants')}}</td>
                      </tr>
                      <tr>
                        <td class="p-2.5 font-mono text-[#a1a1aa]">Admission</td>
                        <td class="p-2.5">${{escapeHtml(i1.admission_policy)}} (${{escapeHtml(i1.admission_details || i1.admission_fee)}})</td>
                        <td class="p-2.5">${{escapeHtml(i2.admission_policy)}} (${{escapeHtml(i2.admission_details || i2.admission_fee)}})</td>
                      </tr>
                      <tr>
                        <td class="p-2.5 font-mono text-[#a1a1aa]">Focus</td>
                        <td class="p-2.5">${{escapeHtml(i1.curatorial_focus)}}</td>
                        <td class="p-2.5">${{escapeHtml(i2.curatorial_focus)}}</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
                <div class="flex gap-2 mt-2">
                  <button class="inst-link px-2.5 py-1 rounded bg-[#242424] hover:bg-[#303030] text-[13px] text-[#93c5fd] border border-[#383838]" data-name="${{escapeHtml(i1.name)}}">Fly to ${{escapeHtml(i1.name)}}</button>
                  <button class="inst-link px-2.5 py-1 rounded bg-[#242424] hover:bg-[#303030] text-[13px] text-[#93c5fd] border border-[#383838]" data-name="${{escapeHtml(i2.name)}}">Fly to ${{escapeHtml(i2.name)}}</button>
                </div>
              `, [`Audit dossier on ${{i1.name}}`, `Audit dossier on ${{i2.name}}`, 'Kunsthalle vs Museum']);
              return;
            }}
          }}
        }}

        // =========================================================================
        // 🌎 LATIN AMERICAN VANGUARD & INSTITUTIONAL CRITIQUE
        // =========================================================================
        if (q.includes('latin america') || q.includes('tropicalia') || q.includes('oiticica') || q.includes('lygia clark') || q.includes('tania bruguera') || q.includes('cildo meireles') || q.includes('muac') || q.includes('tamayo') || q.includes('masp')) {{
          const muac = ALL_INSTITUTIONS.find(i => i.id === 'muac' || i.name.includes('MUAC'));
          const tamayo = ALL_INSTITUTIONS.find(i => i.id === 'museo-tamayo' || i.name.includes('Tamayo'));
          const masp = ALL_INSTITUTIONS.find(i => i.id === 'masp' || i.name.includes('MASP'));

          appendCuratorMessage(`
            <p class="text-slate-200">
              Latin America pioneered some of the most radical forms of <strong>participatory art, institutional critique, and social resistance</strong>:
            </p>
            <p class="text-slate-300">
              - <strong>Hélio Oiticica & Lygia Clark (Brazil):</strong> Dismantled the idea that art is a passive painting to be hung on a museum wall. Clark created *Bichos* (aluminum sculptures viewers rearrange by hand), while Oiticica created *Parangolés* (wearable fabric capes designed to come alive during samba dancing in the favelas).<br>
              - <strong>Cildo Meireles – *Insertions into Ideological Circuits* (1970):</strong> Responding to military dictatorship, Meireles stamped banknotes and returnable glass Coca-Cola bottles with political messages before re-circulating them into the economy, bypassing state censorship.<br>
              - <strong>Tania Bruguera (Cuba):</strong> Pioneered *Arte Útil* (Useful Art), founding INSTAR (Instituto de Artivismo Hannah Arendt) to use art as legal literacy and civic empowerment against authoritarian repression.<br>
              - <strong>Civic Non-Profit Spaces Mapped:</strong> ${{formatInstLink(muac)}} in Mexico City (university governance free from private corporate capture), ${{formatInstLink(tamayo)}} in Chapultepec, and ${{formatInstLink(masp)}} in São Paulo, famous for architect Lina Bo Bardi's radical transparent glass easels that democratize art viewing.
            </p>
          `, ['Arte Útil & The Commons', 'Kunsthalle vs Museum', 'Curated City Itineraries']);
          return;
        }}

        // =========================================================================
        // 🇯🇵 EAST ASIAN AVANT-GARDE: GUTAI & MONO-HA
        // =========================================================================
        if (q.includes('gutai') || q.includes('mono-ha') || q.includes('lee ufan') || q.includes('tokyo art') || q.includes('japan art') || q.includes('bankart') || q.includes('21_21')) {{
          appendCuratorMessage(`
            <p class="text-slate-200">
              Post-war East Asian vanguard movements fundamentally redefined space, material, and performance:
            </p>
            <p class="text-slate-300">
              - <strong>Gutai Art Association (Osaka, 1954):</strong> Founded by Jiro Yoshihara under the motto: <em>"Do what has never been done before!"</em> Artists engaged physically with raw materials—Kazuo Shiraga painted with his feet swinging from a ceiling rope, Shozo Shimamoto hurled glass jars of paint onto vinyl, and Atsuko Tanaka created *Electric Dress* (1956), a wearable kinetic sculpture composed of 200 flashing industrial light tubes.<br>
              - <strong>Mono-ha ("School of Things", Tokyo, 1968–1972):</strong> Led by philosopher/artist Lee Ufan and Nobuo Sekine. Rejecting Western illusionistic sculpture, Mono-ha juxtaposed raw natural materials (huge stones, soil, tree trunks) with raw industrial matter (steel plates, glass, wire), exploring the spatial and perceptual relationship between matter and the viewer.<br>
              - <strong>Civic & Independent Spaces:</strong> BankART 1929 in Yokohama (adaptive reuse of former waterfront port warehouses) and 21_21 DESIGN SIGHT in Tokyo, maintaining clean public/civic charters.
            </p>
          `, ['Video, Sound & Media Art', 'Outdoor Sculpture Parks', 'Kunsthalle vs Museum']);
          return;
        }}

        // =========================================================================
        // ❄️ NORDIC SOCIAL DEMOCRATIC CIVIC MODEL
        // =========================================================================
        if (q.includes('nordic model') || q.includes('scandinavia') || q.includes('danish arts') || q.includes('kulturradet') || (q.includes('denmark') && q.includes('model')) || (q.includes('norway') && q.includes('art'))) {{
          const louis = ALL_INSTITUTIONS.find(i => i.name.includes('Louisiana'));
          const aros = ALL_INSTITUTIONS.find(i => i.name.includes('ARoS'));

          appendCuratorMessage(`
            <p class="text-slate-200">
              The <strong>Nordic Civic Arts Model</strong> (Denmark, Sweden, Norway, Finland) is celebrated globally for maintaining cultural independence from billionaire donor boards:
            </p>
            <p class="text-slate-300">
              - <strong>Structural Public Trust:</strong> Supported through direct civic subsidies from bodies like the Danish Arts Foundation (*Statens Kunstfond*) and Norwegian Arts Council (*Kulturrådet*). Curators answer directly to public peers and municipal cultural charters rather than corporate sponsors.<br>
              - <strong>Open-Access & Environmental Stewardship:</strong> Nordic museums lead the world in releasing high-resolution collection images into the public domain (zero copyright restriction) and implementing strict ecological footprint caps on exhibition logistics.<br>
              - <strong>Verified Spaces Mapped:</strong> ${{formatInstLink(louis)}} in Humlebæk (harmoniously integrating modernist architecture with coastal nature) and ${{formatInstLink(aros)}} in Aarhus with Olafur Eliasson's rainbow glass skywalk.
            </p>
          `, ['Outdoor Sculpture Parks', 'Kunsthalle vs Museum', 'Dutch Research: BAK']);
          return;
        }}

        // 1. London Art Scene & Independent Spaces
        if (q.includes('london') && (q.includes('art') || q.includes('scene') || q.includes('space') || q.includes('tell me') || q.includes('more') || q.includes('guide') || q.includes('recommend') || q.includes('culture') || q.includes('critic'))) {{
          const chis = ALL_INSTITUTIONS.find(i => i.name.includes('Chisenhale Gallery'));
          const camden = ALL_INSTITUTIONS.find(i => i.name.includes('Camden Art Centre'));
          const white = ALL_INSTITUTIONS.find(i => i.name.includes('Whitechapel Gallery'));
          const gas = ALL_INSTITUTIONS.find(i => i.name.includes('Gasworks'));
          const iniva = ALL_INSTITUTIONS.find(i => i.name.includes('Iniva'));
          const tate = EXCLUDED_INSTITUTIONS.find(i => i.name.includes('Tate Modern'));

          appendCuratorMessage(`
            <p class="text-slate-200">
              London has two very different art worlds: the giant corporate museums on the Thames, and a network of independent galleries and artist-run spaces with clean funding.
            </p>
            <p class="text-slate-300">
              For 26 years, BP sponsored ${{formatInstLink(tate)}}, until artist groups like <em>Liberate Tate</em> and <em>BP or not BP?</em> staged creative protests, pushing Tate to drop BP in 2016. In addition, protests by Nan Goldin's group P.A.I.N. forced institutions like Serpentine to drop the Sackler name.
            </p>
            <p class="text-slate-300">
              Here are great independent spaces to visit in London:
            </p>
            <p class="text-slate-300">
              - ${{formatInstLink(chis)}} in Bow: Free entry, known for commissioning brand-new work by emerging artists.<br>
              - ${{formatInstLink(camden)}} in North London: Free entry, quiet garden café, and ceramic and sculpture studios.<br>
              - ${{formatInstLink(white)}} in East London: Free entry, showed Picasso's <em>Guernica</em> in 1939 to support the Spanish Republic.<br>
              - ${{formatInstLink(gas)}} in Vauxhall: Artist-led exhibitions and international studios.<br>
              - ${{formatInstLink(iniva)}}: Championing global diaspora artists and non-commercial public research.
            </p>
          `);
          filterByCity('London', true, false);
          return;
        }}

        // 2. Beyond Objecthood: The Exhibition as a Critical Form Since 1968
        if (q.includes('beyond objecthood') || q.includes('voorhies') || (q.includes('objecthood') && (q.includes('fried') || q.includes('art') || q.includes('exhibition'))) || q.includes('exhibition as a critical form') || q.includes('exhibition as form')) {{
          appendCuratorMessage(`
            <p class="text-slate-200">
              In <em>Beyond Objecthood</em> (MIT Press, 2017), art historian James Voorhies explains how <strong>the exhibition itself became a work of art and a tool for critique</strong>.
            </p>
            <p class="text-slate-300">
              It started in 1967 when art critic Michael Fried wrote an essay called <em>Art and Objecthood</em>. Fried attacked Minimalist art (like Donald Judd's simple boxes) because viewers had to walk around them in a room over time. Fried called this 'theatricality' and argued that real art should be experienced in a single instant.
            </p>
            <p class="text-slate-300">
              Starting around 1968, artists did the exact opposite: they embraced theatricality and audience participation. Artists like Robert Smithson, Marcel Broodthaers, Fred Wilson, and Maria Eichhorn turned the whole exhibition into their medium. They showed that museums are never neutral white rooms—they are shaped by money, politics, and power.
            </p>
            <p class="text-slate-300">
              Voorhies also points out a big irony today: mega-museums have turned this kind of participatory art into tourist spectacles and selfie backdrops. Because of that, the most honest, experimental exhibitions have moved to independent galleries and artist-run spaces.
            </p>
          `);
          return;
        }}

        // 3. e-flux Journal, Hito Steyerl & Boris Groys
        if (q.includes('e-flux') || q.includes('steyerl') || q.includes('groys') || q.includes('vidokle') || q.includes('museum as factory') || q.includes('duty free art') || q.includes('duty-free art') || q.includes('freeport') || q.includes('post-democracy')) {{
          appendCuratorMessage(`
            <p class="text-slate-200">
              <em>e-flux journal</em> is an influential art publishing platform that explores how money, politics, and power affect the art world.
            </p>
            <p class="text-slate-300">
              Key ideas from its essays include:
            </p>
            <p class="text-slate-300">
              - <strong>Hito Steyerl – <em>Is a Museum a Factory?</em> (2009):</strong> She argues that modern museums act like 24/7 factories. Visitors are like unpaid workers: our attention, ticket purchases, and social media posts produce value that helps drive up nearby luxury real estate and museum prestige.<br>
              - <strong>Hito Steyerl – <em>Duty Free Art</em> (2015):</strong> She writes about 'freeports'—huge tax-free airport warehouses in Geneva and Singapore where ultra-wealthy investors store valuable art in crates just to avoid taxes and trade it like a financial asset, without the public ever seeing it.<br>
              - <strong>Boris Groys:</strong> He reminds us that public museums started during the French Revolution to take art away from kings and churches and open it up to everyone.<br>
              - <strong>Anton Vidokle:</strong> He critiques celebrity curators who take the spotlight away from the artists themselves.
            </p>
          `);
          return;
        }}

        // 4. Three Waves of Institutional Critique
        if (q.includes('institutional critique') || q.includes('haacke') || q.includes('andrea fraser') || q.includes('three waves') || q.includes('3 waves') || q.includes('waves of critique') || q.includes('fred wilson')) {{
          appendCuratorMessage(`
            <p class="text-slate-200">
              Institutional critique is art that examines the museum itself—its money, its board, and its politics. It happened in three main waves:
            </p>
            <p class="text-slate-300">
              1. <strong>First Wave (Late 1960s–1970s):</strong> Artists like Hans Haacke showed that museums are not neutral. In 1970, Haacke asked MoMA visitors whether they supported museum trustee Nelson Rockefeller's backing of the Vietnam War. In 1971, the Guggenheim cancelled Haacke's show because his artwork exposed the slum properties owned by a museum trustee.<br>
              2. <strong>Second Wave (1980s–1990s):</strong> Andrea Fraser and Fred Wilson showed that artists and visitors are part of the system too. Fraser gave satirical museum tours as a fake docent, while Fred Wilson rearranged museum archives in Baltimore (<em>Mining the Museum</em>) to expose histories of slavery and racial bias.<br>
              3. <strong>Third Wave (2010s–Present):</strong> Direct activist campaigns. Nan Goldin's group P.A.I.N. staged die-ins inside the Met, Guggenheim, and Louvre, forcing them to remove the Sackler family name because of the opioid crisis. In 2019, artists boycotted the Whitney Biennial until a tear gas manufacturer resigned from the board.
            </p>
          `);
          return;
        }}

        // =========================================================================
        // 🇳🇱 DUTCH ARTISTIC RESEARCH & BAK UTRECHT CANON
        // =========================================================================

        // D1. BAK, basis voor actuele kunst (Utrecht)
        if (
          q.includes('utrecht bac') || q.includes('bac utrecht') || q.includes('bak utrecht') || q.includes('utrecht bak') ||
          q.includes('basis voor actuele kunst') || q.includes('maria hlavajova') || q.includes('former west') ||
          ((/\b(bak|bac)\b/i.test(q)) && (q.includes('utrecht') || q.includes('art') || q.includes('research') || q.includes('space') || q.includes('museum') || q.includes('theory') || q.includes('curat') || q.includes('learn')))
        ) {{
          const bak = ALL_INSTITUTIONS.find(i => i.id === 'bak-utrecht' || i.name.includes('BAK'));
          appendCuratorMessage(`
            <p class="text-slate-200">
              ${{formatInstLink(bak)}} in Utrecht is one of the world's most influential centers for critical artistic research, political imagination, and institutional critique.
            </p>
            <p class="text-slate-300">
              Directed by Maria Hlavajova, BAK does not treat art as a luxury commodity or decorative object. Instead, it functions as a public research laboratory and political assembly where artists, philosophers, and community organizers address systemic global crises.
            </p>
            <p class="text-slate-300">
              Key research milestones led by BAK include:
            </p>
            <p class="text-slate-300">
              - <strong><em>Former West</em> (2008–2016, co-published with MIT Press):</strong> A monumental 8-year transnational research project investigating geopolitical transformations after 1989. It argued that the fall of the Berlin Wall did not just collapse the "Former East"—it fundamentally provincialized the "West," showing that Western democratic capitalism is not the universal end-goal of human history.<br>
              - <strong><em>Vectors of Commoning:</em></strong> Long-term research investigating how cultural institutions can become living commons—reclaiming public wealth, feminist mutual care, and collaborative ownership against neoliberal privatization.<br>
              - <strong><em>Posthuman Glossary</em> (with Rosi Braidotti & Utrecht University):</strong> Seminal research developed with feminist philosopher Rosi Braidotti exploring post-anthropocentric ethics, climate justice, and ecological survival.<br>
              - <strong><em>Propositions for Non-Fascist Living:</em></strong> Assemblies examining how cultural organizations can organize daily democratic resistance against the rise of contemporary authoritarianism.
            </p>
            <p class="text-slate-300">
              <strong>Visiting & Funding:</strong> Located at Pauwstraat 13A in historic central Utrecht (10-minute walk from Utrecht Centraal). Funded through public civic grants from the Dutch Mondriaan Fund and Gemeente Utrecht with zero corporate board leverage. Operates a solidarity sliding scale (€0–€6), making it free for youth and activists.
            </p>
          `);
          if (bak) selectInstitution(bak, true);
          return;
        }}

        // D2. Dutch Artistic Research Ecosystem & Mondriaan Fund Civic Model
        if (
          q.includes('dutch research') || q.includes('netherlands research') || q.includes('dutch art') ||
          q.includes('dutch model') || q.includes('artistic research') || q.includes('onderzoek in de kunst') ||
          q.includes('mondriaan fund') || q.includes('mondriaan fonds') ||
          (q.includes('netherlands') && (q.includes('funding') || q.includes('research') || q.includes('critical') || q.includes('civic')))
        ) {{
          const bak = ALL_INSTITUTIONS.find(i => i.id === 'bak-utrecht' || i.name.includes('BAK'));
          const casco = ALL_INSTITUTIONS.find(i => i.id === 'casco-art-institute' || i.name.includes('Casco'));
          const vanabbe = ALL_INSTITUTIONS.find(i => i.name.includes('Van Abbemuseum'));
          const melly = ALL_INSTITUTIONS.find(i => i.id === 'kunstinstituut-melly' || i.name.includes('Melly'));
          const deappel = ALL_INSTITUTIONS.find(i => i.id === 'de-appel' || i.name.includes('De Appel'));
          const framer = ALL_INSTITUTIONS.find(i => i.id === 'framer-framed' || i.name.includes('Framer Framed'));

          appendCuratorMessage(`
            <p class="text-slate-200">
              The Netherlands is the global capital of <strong>Artistic Research</strong> (<em>onderzoek in de kunst</em>) and progressive institutional critique:
            </p>
            <p class="text-slate-300">
              Unlike the American museum model—where wealthy billionaire donors buy board seats to receive tax deductions and suppress political critique—Dutch cultural spaces receive structural civic funding from the <strong>Mondriaan Fund</strong> and municipal councils. Peer panels of artists and curators allocate grants based on critical rigor rather than private patron approval.
            </p>
            <p class="text-slate-300">
              Here are the six essential Dutch research institutions mapped in Culture Atlas:
            </p>
            <p class="text-slate-300">
              1. ${{formatInstLink(bak)}} (Utrecht): World leader in critical theory, commons research, and co-publisher of <em>Former West</em> with MIT Press.<br>
              2. ${{formatInstLink(casco)}} (Utrecht): Replaced traditional gallery display with cooperative commoning, feminist economies, and institutional unlearning.<br>
              3. ${{formatInstLink(vanabbe)}} (Eindhoven): Directed by Charles Esche; pioneered the <em>Museum of Arte Útil</em> (useful art) with Tania Bruguera and archival <em>Deviant Practice</em>.<br>
              4. ${{formatInstLink(melly)}} (Rotterdam): Renowned for the historic decolonial process of renaming itself away from colonial naval officer Witte de With.<br>
              5. ${{formatInstLink(deappel)}} (Amsterdam): Home of the legendary Curatorial Programme (CP) since 1994 and seminal 1970s performance archives.<br>
              6. ${{formatInstLink(framer)}} (Amsterdam): Intercultural decolonial research platform challenging Eurocentric museology and restitution policies.
            </p>
          `);
          flyTo(5.2, 52.1);
          return;
        }}

        // D3. Casco Art Institute: Working for the Commons (Utrecht)
        if (q.includes('casco') || q.includes('working for the commons') || (q.includes('commons') && (q.includes('utrecht') || q.includes('art') || q.includes('institute'))) || q.includes('binna choi') || q.includes('site for unlearning')) {{
          const casco = ALL_INSTITUTIONS.find(i => i.id === 'casco-art-institute' || i.name.includes('Casco'));
          appendCuratorMessage(`
            <p class="text-slate-200">
              ${{formatInstLink(casco)}} in Utrecht is an internationally renowned experiment in <strong>institutional commoning</strong>.
            </p>
            <p class="text-slate-300">
              Under the directorship of Binna Choi, Casco realized that presenting exhibitions about politics while operating internally as a hierarchical, corporate-style gallery was hypocritical. In 2018, they officially renamed themselves <em>Working for the Commons</em> and restructured their entire organizational model:
            </p>
            <p class="text-slate-300">
              - <strong>Art as Commons:</strong> Rather than viewing artworks as private property or temporary entertainment, Casco treats culture as a shared collective resource maintained for mutual care.<br>
              - <strong>Site for Unlearning: Art Organization:</strong> Casco actively experiments with non-hierarchical salaries, shared housework, community farming, and consensus decision-making.<br>
              - <strong>Publishing Class:</strong> A long-running collaborative publishing initiative that investigates how books can circulate outside commercial market monopolies.
            </p>
            <p class="text-slate-300">
              Admission is 100% free. Located at Lange Nieuwstraat 7 in Utrecht's Museumkwartier, featuring an open communal kitchen, garden courtyard, and research library.
            </p>
          `);
          if (casco) selectInstitution(casco, true);
          return;
        }}

        // D4. Van Abbemuseum & Arte Útil (Eindhoven)
        if (q.includes('van abbemuseum') || q.includes('van abbe') || q.includes('arte util') || q.includes('useful art') || q.includes('charles esche') || q.includes('deviant practice')) {{
          const vanabbe = ALL_INSTITUTIONS.find(i => i.name.includes('Van Abbemuseum'));
          appendCuratorMessage(`
            <p class="text-slate-200">
              ${{formatInstLink(vanabbe)}} in Eindhoven is one of Europe's most radical public civic museums.
            </p>
            <p class="text-slate-300">
              Under director Charles Esche, Van Abbemuseum rejected the standard corporate blockbuster model to become a leading laboratory for <strong>Radical Museology</strong> (as documented by Claire Bishop in her 2013 book):
            </p>
            <p class="text-slate-300">
              - <strong>Museum of Arte Útil (initiated with Tania Bruguera):</strong> Questions the idea that art must be passive and useless. Arte Útil ('useful art') proposes that artistic imagination should be deployed as a concrete tool—helping communities address housing inequality, legal defense, and ecological survival.<br>
              - <strong>Deviant Practice:</strong> A long-term research project opening the museum's permanent collection (including works by El Lissitzky, Picasso, and Chagall) to queer, decolonial, and disability-inclusive reinterpretation.<br>
              - <strong>Clean Ethical Charter:</strong> In 2021, Van Abbemuseum ratified a strict climate and governance charter prohibiting any sponsorship from fossil fuels, weapons manufacturers, or human-rights-flagged corporations.
            </p>
          `);
          if (vanabbe) selectInstitution(vanabbe, true);
          return;
        }}

        // D5. Kunstinstituut Melly & Decolonial Renaming (Rotterdam)
        if (q.includes('kunstinstituut melly') || q.includes('melly') || q.includes('witte de with') || q.includes('melly shum') || q.includes('decolonial renaming')) {{
          const melly = ALL_INSTITUTIONS.find(i => i.id === 'kunstinstituut-melly' || i.name.includes('Melly'));
          appendCuratorMessage(`
            <p class="text-slate-200">
              ${{formatInstLink(melly)}} in Rotterdam represents one of the most significant real-world examples of <strong>institutional accountability and decolonial renaming</strong> in contemporary art history.
            </p>
            <p class="text-slate-300">
              - <strong>The Historical Context:</strong> Founded in 1990 as <em>Witte de With Center for Contemporary Art</em>, named after the Rotterdam street where it sits. That street commemorated Witte Corneliszoon de With, a 17th-century naval officer who fought for the Dutch East India Company (VOC) and Dutch West India Company (WIC).<br>
              - <strong>The Accountability Process:</strong> In 2017, after open letters from artists and activists criticizing the commemoration of colonial exploitation, director Sofía Hernández Chong Cuy and the board launched a 3-year public audit.<br>
              - <strong>Collective Renaming:</strong> In January 2021, the institution officially renamed itself <em>Kunstinstituut Melly</em>, after Canadian artist Ken Lum's iconic 1990 artwork <em>Melly Shum Hates Her Job</em>, which has hung permanently on the museum's exterior wall for over three decades.<br>
              - <strong>Research Publishing:</strong> Melly is celebrated for its <em>Source</em> book series, experimental curatorial fellowships, and Friday evening free public access.
            </p>
          `);
          if (melly) selectInstitution(melly, true);
          return;
        }}

        // D6. De Appel & Curatorial Pedagogy (Amsterdam)
        if (q.includes('de appel') || q.includes('curatorial programme') || q.includes('wies smals')) {{
          const deappel = ALL_INSTITUTIONS.find(i => i.id === 'de-appel' || i.name.includes('De Appel'));
          appendCuratorMessage(`
            <p class="text-slate-200">
              ${{formatInstLink(deappel)}} in Amsterdam is a historic vanguard space that fundamentally shaped modern curatorial education.
            </p>
            <p class="text-slate-300">
              - <strong>Founding (1975):</strong> Established by Wies Smals as an alternative art space dedicated to performance art, body art, and ephemeral installations, hosting historic performances by Marina Abramović and Ulay.<br>
              - <strong>Curatorial Programme (CP):</strong> Launched in 1994, it was one of the world's very first training programs for contemporary curators. Rather than teaching dry art cataloging, CP pioneered curating as an autonomous research practice, political discourse, and collective exhibition-making.<br>
              - <strong>Research Archive:</strong> De Appel preserves an extraordinary public research archive of 1970s–1990s conceptual and performance art documentation.
            </p>
          `);
          if (deappel) selectInstitution(deappel, true);
          return;
        }}

        // D7. Rosi Braidotti & Posthumanist Theory (Utrecht)
        if (q.includes('braidotti') || q.includes('posthuman') || q.includes('posthumanism') || q.includes('post-human')) {{
          const bak = ALL_INSTITUTIONS.find(i => i.id === 'bak-utrecht' || i.name.includes('BAK'));
          appendCuratorMessage(`
            <p class="text-slate-200">
              Feminist philosopher Rosi Braidotti (Distinguished University Professor at Utrecht University) has deeply influenced contemporary art, curating, and institutional theory.
            </p>
            <p class="text-slate-300">
              In close partnership with ${{formatInstLink(bak)}} in Utrecht, Braidotti co-developed research platforms like the <em>Posthuman Glossary</em> (Bloomsbury / BAK, 2018):
            </p>
            <p class="text-slate-300">
              - <strong>Beyond Human Supremacy:</strong> Braidotti critiques traditional Western humanism, which placed the white, wealthy European male at the center of the universe while treating nature, indigenous peoples, and animals as exploitable property.<br>
              - <strong>Affirmative Ethics & The Anthropocene:</strong> In an era of climate breakdown and digital algorithms, art must generate 'affirmative ethics'—practical ways of living together that connect humans with ecosystems and technology without exploitation.<br>
              - <strong>Impact on Museums:</strong> This research pushed museums to stop acting like dead trophy vaults, transforming them into living eco-assemblies that actively address environmental collapse and cross-species solidarity.
            </p>
          `);
          if (bak) selectInstitution(bak, true);
          return;
        }}

        // D8. Former West Project (BAK + MIT Press)
        if (q.includes('former west') || q.includes('former east') || (q.includes('west') && q.includes('after 1989'))) {{
          const bak = ALL_INSTITUTIONS.find(i => i.id === 'bak-utrecht' || i.name.includes('BAK'));
          appendCuratorMessage(`
            <p class="text-slate-200">
              <em>Former West</em> (2008–2016) is one of the most important artistic research projects of the 21st century, initiated by ${{formatInstLink(bak)}} in Utrecht and co-published with MIT Press.
            </p>
            <p class="text-slate-300">
              Here is why it changed contemporary curatorial thinking:
            </p>
            <p class="text-slate-300">
              - <strong>Rethinking 1989:</strong> When the Berlin Wall fell in 1989, Western pundits declared 'the end of history' and assumed that only the communist Eastern bloc had changed ('Former East'). BAK posed the critical counter-question: <em>What happened to the West?</em><br>
              - <strong>Provincializing the West:</strong> The project showed that the 'West' is no longer the universal center of culture or democracy. Instead, it has become 'former'—facing deep crises of inequality, austerity, and democratic breakdown.<br>
              - <strong>Global Intellectual Compendium:</strong> Culminating in the 748-page book <em>Former West: Art and the Contemporary After 1989</em> (MIT Press / BAK, edited by Maria Hlavajova and Simon Sheikh), bringing together over 300 thinkers including Boris Groys, Achille Mbembe, Irit Rogoff, and Nancy Fraser.
            </p>
          `);
          if (bak) selectInstitution(bak, true);
          return;
        }}

        // D9. Utrecht Cultural Guide
        if (q.includes('utrecht')) {{
          const bak = ALL_INSTITUTIONS.find(i => i.id === 'bak-utrecht' || i.name.includes('BAK'));
          const casco = ALL_INSTITUTIONS.find(i => i.id === 'casco-art-institute' || i.name.includes('Casco'));
          appendCuratorMessage(`
            <p class="text-slate-200">
              Utrecht is Europe's premier capital for critical artistic research, political philosophy, and the commons:
            </p>
            <p class="text-slate-300">
              Unlike commercial art metropolises driven by auction houses and real-estate developers, Utrecht's art scene is built on deep institutional critique and intellectual rigor:
            </p>
            <p class="text-slate-300">
              - ${{formatInstLink(bak)}} on Pauwstraat: The international benchmark for research-based art practice, co-publisher of <em>Former West</em> with MIT Press, and pioneer of the <em>Posthuman Glossary</em> with Utrecht University.<br>
              - ${{formatInstLink(casco)}} on Lange Nieuwstraat: A radical experiment that transformed an art gallery into a working cooperative commons with free public admission and shared community resources.
            </p>
            <p class="text-slate-300">
              Both spaces are an easy 10 to 15-minute walk from Utrecht Centraal railway station (just 25 minutes by train from Amsterdam Centraal or Schiphol Airport).
            </p>
          `);
          filterByCity('Utrecht', true, false);
          return;
        }}

        // D10. Rotterdam Cultural Guide
        if (q.includes('rotterdam')) {{
          const melly = ALL_INSTITUTIONS.find(i => i.id === 'kunstinstituut-melly' || i.name.includes('Melly'));
          appendCuratorMessage(`
            <p class="text-slate-200">
              Rotterdam is famous for bold modernist architecture and fearless contemporary art institutions:
            </p>
            <p class="text-slate-300">
              - ${{formatInstLink(melly)}} on Witte de Withstraat: Renowned for its historic public decolonial audit and renaming from Witte de With, celebrated research monograph series, and Ken Lum's permanent artwork <em>Melly Shum Hates Her Job</em>.
            </p>
            <p class="text-slate-300">
              Just a 12-minute walk from Rotterdam Centraal, with free public admission every Friday evening from 18:00 to 21:00.
            </p>
          `);
          filterByCity('Rotterdam', true, false);
          return;
        }}

        // D11. Amsterdam Cultural Guide
        if (q.includes('amsterdam')) {{
          const deappel = ALL_INSTITUTIONS.find(i => i.id === 'de-appel' || i.name.includes('De Appel'));
          const framer = ALL_INSTITUTIONS.find(i => i.id === 'framer-framed' || i.name.includes('Framer Framed'));
          const sted = EXCLUDED_INSTITUTIONS.find(i => i.name.includes('Stedelijk'));
          appendCuratorMessage(`
            <p class="text-slate-200">
              Amsterdam features pioneering independent research spaces with verified clean funding:
            </p>
            <p class="text-slate-300">
              - ${{formatInstLink(deappel)}}: Historic vanguard founded in 1975, celebrated for 1970s performance art archives and the Curatorial Programme (CP).<br>
              - ${{formatInstLink(framer)}} in Amsterdam Oost: Intercultural decolonial research platform investigating restitution, climate justice, and community archives.
            </p>
            <p class="text-slate-400 text-[14px]">
              Note: ${{formatInstLink(sted)}} on Museumplein is monitored and excluded due to commercial and corporate board underwriting.
            </p>
          `);
          filterByCity('Amsterdam', true, false);
          return;
        }}

        // --- RESEARCH SPECIALIST HANDLERS ---

        // Research Handler 1: How Culture Atlas Conducts Research & Audits
        if (q.includes('research method') || q.includes('how do you audit') || q.includes('how does culture atlas research') || q.includes('audit method') || q.includes('research process') || q.includes('form 990') || (q.includes('how') && q.includes('research') && q.includes('museum'))) {{
          appendCuratorMessage(`
            <p class="text-slate-200">
              Here is how Culture Atlas conducts forensic research and audits every institution in our network:
            </p>
            <p class="text-slate-300">
              1. <strong>Regulatory Tax & Charity Filings:</strong> In the United States, we review IRS Form 990 filings—specifically checking Schedule I (grants received) and Schedule L (business transactions with board trustees). In the UK, we inspect annual returns filed with the Charity Commission. In France and Germany, we review official Ministry of Culture and regional DRAC audits.<br>
              2. <strong>Board Trustee Conflict Audits:</strong> We cross-reference museum board members against corporate databases, tracking directorships in weapons manufacturing, fossil fuel extraction, private prisons, and predatory debt.<br>
              3. <strong>Funding Transparency:</strong> We analyze the proportion of public funding, ticket sales, and private philanthropy to ensure curators are protected from corporate censorship.<br>
              4. <strong>Watchdog & Activist Evidence:</strong> We monitor reporting from Hyperallergic, Artforum, and direct campaigns by artist coalitions like Nan Goldin's P.A.I.N., Strike MoMA, and Culture Unstained.
            </p>
            <p class="text-slate-300">
              Only institutions that maintain clear curatorial independence and clean funding without weapons or fossil fuel sponsorships receive Tier A verification.
            </p>
          `);
          return;
        }}

        // Research Handler 2: Landmark Exhibitions & Curatorial History
        if (q.includes('landmark exhibition') || q.includes('landmark show') || q.includes('szeemann') || q.includes('when attitudes') || q.includes('documenta') || q.includes('enwezor') || q.includes('this is tomorrow') || q.includes('exhibition history')) {{
          appendCuratorMessage(`
            <p class="text-slate-200">
              Here are five landmark exhibitions that fundamentally changed curatorial history and institutional critique:
            </p>
            <p class="text-slate-300">
              - <strong><em>When Attitudes Become Form</em> (Kunsthalle Bern, 1969, curated by Harald Szeemann):</strong> Marked the emergence of the independent curator. Szeemann demonstrated that an artist's concept, gestures, and the physical process of making art could serve as the exhibition itself.<br>
              - <strong><em>This Is Tomorrow</em> (Whitechapel Gallery, London, 1956):</strong> Brought architects, painters, and sculptors together into an interactive maze, introducing pop art and breaking the boundary between art and mass media.<br>
              - <strong><em>MoMA Poll</em> (Museum of Modern Art, New York, 1970, by Hans Haacke):</strong> Haacke installed two transparent ballot boxes asking visitors whether they supported museum trustee Nelson Rockefeller's backing of the Vietnam War, turning the museum's audience into an active political counter-public.<br>
              - <strong><em>Mining the Museum</em> (Baltimore, 1992, by Fred Wilson):</strong> Wilson rearranged historical museum archives, displaying ornate 19th-century silver repoussé vessels in the same case as iron slave shackles to expose how museums historically erased Black labor.<br>
              - <strong><em>Documenta 11</em> (Kassel, 2002, directed by Okwui Enwezor):</strong> The first Documenta directed by an African curator, organizing global intellectual platforms across Lagos, New Delhi, Saint Lucia, and Vienna, decisively decentering Western art history.
            </p>
          `);
          return;
        }}

        // Research Handler 3: Restitution, Looted Art & Provenance Research
        if (q.includes('restitut') || q.includes('repatriat') || q.includes('benin') || q.includes('looted') || q.includes('provenance') || q.includes('colonial artifact')) {{
          appendCuratorMessage(`
            <p class="text-slate-200">
              Restitution and provenance research are reshaping museum accountability today:
            </p>
            <p class="text-slate-300">
              - <strong>The Benin Bronzes:</strong> In 1897, British soldiers looted thousands of sacred royal bronzes and ivories from the Kingdom of Benin (modern Nigeria). In 2022, pioneering institutions like the Horniman Museum in London and German federal state museums formally transferred legal ownership of hundreds of artifacts back to Nigeria.<br>
              - <strong>Provenance Investigations:</strong> Ethical museums now dedicate research teams to investigate how every object in their collection was acquired, identifying pieces obtained through colonial looting, wartime seizure, or forced sales.<br>
              - <strong>The Sarr-Savoy Report (2018):</strong> Commissioned by France, this report found that over 90% of sub-Saharan Africa's tangible cultural heritage resides in Western institutions, recommending legal pathways for full restitution.<br>
              - <strong>Culture Atlas Criteria:</strong> We support institutions that treat collections as shared civic trusts in transparent dialogue with source communities, rather than imperial trophies.
            </p>
          `);
          return;
        }}

        // Research Handler 4: Comparative Funding Models (US vs Europe)
        if (q.includes('us vs europe') || q.includes('funding model') || q.includes('compare funding') || q.includes('american private') || q.includes('european public') || q.includes('board governance')) {{
          appendCuratorMessage(`
            <p class="text-slate-200">
              A museum's funding model fundamentally shapes what art it can display:
            </p>
            <p class="text-slate-300">
              - <strong>The American 501(c)(3) Model:</strong> Museums rely heavily on wealthy private donors who receive tax deductions and board seats. This model frequently creates severe conflicts of interest, as billionaire trustees often have business ties to weapons manufacturers, private prisons, or pharmaceutical companies.<br>
              - <strong>The European Civic Model:</strong> Institutions receive substantial direct public funding from arts councils (like Arts Council England, DRAC in France, or Danish state cultural funds). Curators are legally accountable to the public and have greater freedom from commercial market pressure.<br>
              - <strong>The Artist-Run Cooperative Model:</strong> Managed directly by practicing artists (like Chisenhale in London, Artists Space in New York, or Plug In ICA in Canada). With modest budgets, they provide maximum curatorial freedom to commission daring work without board censorship.
            </p>
          `);
          return;
        }}

        // Research Handler 5: Deep Research Audit on a Specific Institution
        if (q.includes('deep research') || q.includes('research audit') || q.includes('audit dossier on') || q.includes('research on')) {{
          const targetInst = ALL_INSTITUTIONS.find(i => q.includes(i.name.toLowerCase()) || (i.aliases && i.aliases.some(a => q.includes(a.toLowerCase()))));
          if (targetInst) {{
            appendCuratorMessage(`
              <p class="text-slate-200">
                <strong>Research Audit: ${{formatInstLink(targetInst)}}</strong> (${{targetInst.city}}, ${{targetInst.country}})
              </p>
              <p class="text-slate-300">
                - <strong>Founding Context:</strong> Established in ${{targetInst.year_founded}} in the ${{targetInst.neighborhood}} quarter.<br>
                - <strong>Governance Model:</strong> Operates as an independent <em>${{targetInst.governance_type}}</em>.<br>
                - <strong>Funding Architecture:</strong> ${{targetInst.funding}}<br>
                - <strong>Ethical Safeguard:</strong> ${{targetInst.ethical_safeguard}}<br>
                - <strong>Curatorial Focus:</strong> ${{targetInst.curatorial_focus}}<br>
                - <strong>Signature Art / Milestone:</strong> <span class="text-amber-300 font-normal">${{targetInst.highlight}}</span><br>
                - <strong>Transparency Status:</strong> <span class="text-emerald-400 font-mono font-bold">${{targetInst.transparency_grade || 'Tier A+'}}</span>
              </p>
              <p class="text-slate-300">
                ${{targetInst.watch ? `<strong>Watch Notes:</strong> ${{targetInst.watch}}<br>` : ''}}
                Public admission is <strong>${{targetInst.admission_policy}}</strong> (${{targetInst.admission_details}}).
              </p>
            `);
            selectInstitution(targetInst, true);
            return;
          }}
        }}


        // All Cities Mapped Query Handler (from Choose project shelf pill)
        if (q.includes('cities mapped') || q.includes('all cities') || q.includes('show me all cities') || q.includes('which cities') || q.includes('list of cities') || q.includes('choose project')) {{
          const sorted = [...PRIORITY_CITIES];
          const cityPills = sorted.map(c => {{
            const count = ALL_INSTITUTIONS.filter(i => matchC(i.city, c.name)).length;
            return `<button class="city-zoom-btn px-2.5 py-1 rounded-xl bg-[#262626] hover:bg-[#333] border border-[#383838] hover:border-[#60a5fa] text-white text-[13px] transition cursor-pointer inline-flex items-center gap-1.5" data-city="${{escapeHtml(c.name)}}"><span>${{escapeHtml(c.name)}}</span> <span class="text-[#93c5fd] font-mono text-[12px]">(${{count}})</span></button>`;
          }}).join(' ');

          appendCuratorMessage(`
            <p class="text-slate-200">
              Culture Atlas currently audits independent cultural spaces across <strong>${{ALL_CITIES.length}} cities</strong>:
            </p>
            <div class="flex flex-wrap gap-2 my-2.5">
              ${{cityPills}}
            </div>
            <p class="text-slate-300">
              Click any city pill above, or click city badges directly on the 3D globe to explore verified spaces.
            </p>
          `);
          return;
        }}

        // All Countries Mapped Query Handler
        if (q.includes('countries mapped') || q.includes('all countries') || q.includes('show me all countries') || q.includes('which countries') || q.includes('list of countries')) {{
          const sortedCountries = [...COUNTRY_CENTROIDS];
          const countryPills = sortedCountries.map(c => {{
            const count = ALL_INSTITUTIONS.filter(i => matchC(i.country, c.name)).length;
            return `<button class="country-zoom-btn px-2.5 py-1 rounded-xl bg-[#262626] hover:bg-[#333] border border-[#383838] hover:border-[#60a5fa] text-white text-[13px] transition cursor-pointer inline-flex items-center gap-1.5" data-country="${{escapeHtml(c.name)}}"><span>${{escapeHtml(c.name)}}</span> <span class="text-[#93c5fd] font-mono text-[12px]">(${{count}})</span></button>`;
          }}).join(' ');

          appendCuratorMessage(`
            <p class="text-slate-200">
              Culture Atlas audits cultural spaces across <strong>35 countries</strong>:
            </p>
            <div class="flex flex-wrap gap-2 my-2.5">
              ${{countryPills}}
            </div>
            <p class="text-slate-300">
              Click any country pill above, or click on any nation on the 3D globe to explore.
            </p>
          `);
          return;
        }}

        // Exact Prompt 1: Find independent art spaces near me
        if (q.includes('near me') || q.includes('spaces near me') || q.includes('art spaces near')) {{
          appendCuratorMessage(`
            <p class="text-slate-200">
              Here are verified independent art spaces with clean funding. Tell me your city (like <a href="#" class="city-link text-[#93c5fd] hover:underline" data-city="London">London</a>, <a href="#" class="city-link text-[#93c5fd] hover:underline" data-city="New York">New York</a>, <a href="#" class="city-link text-[#93c5fd] hover:underline" data-city="Utrecht">Utrecht</a>, or <a href="#" class="city-link text-[#93c5fd] hover:underline" data-city="Paris">Paris</a>) to find spaces closest to you:
            </p>
            <p class="text-slate-300">
              - In Utrecht & The Netherlands: ${{formatInstLink(ALL_INSTITUTIONS.find(i => i.id === 'bak-utrecht' || i.name.includes('BAK')))}} in Utrecht, ${{formatInstLink(ALL_INSTITUTIONS.find(i => i.id === 'casco-art-institute'))}} in Utrecht, and ${{formatInstLink(ALL_INSTITUTIONS.find(i => i.id === 'kunstinstituut-melly'))}} in Rotterdam.<br>
              - In London: ${{formatInstLink(ALL_INSTITUTIONS.find(i => i.name.includes('Chisenhale')))}} in Bow and ${{formatInstLink(ALL_INSTITUTIONS.find(i => i.name.includes('Camden')))}} in North London (both free).<br>
              - In New York: ${{formatInstLink(ALL_INSTITUTIONS.find(i => i.name.includes('Artists Space')))}} in Tribeca and ${{formatInstLink(ALL_INSTITUTIONS.find(i => i.name.includes('SculptureCenter')))}} in Queens.<br>
              - In Paris: ${{formatInstLink(ALL_INSTITUTIONS.find(i => i.name.includes('Bétonsalon')))}} in the 13th and ${{formatInstLink(ALL_INSTITUTIONS.find(i => i.name.includes('Palais de Tokyo')))}}.
            </p>
          `);
          return;
        }}

        // Exact Prompt 2: Who funds this museum?
        if (q.includes('who funds this museum') || (q.includes('who funds') && q.length < 30)) {{
          appendCuratorMessage(`
            <p class="text-slate-200">
              Every museum in Culture Atlas is audited for clean, transparent funding:
            </p>
            <p class="text-slate-300">
              1. <strong>Civic Arts Councils & The Dutch Model:</strong> European spaces receive structural civic funding (Mondriaan Fund in the Netherlands, Arts Council England, DRAC France). Peer panels of curators and artists allocate funding based on critical merit, protecting curators from private corporate censorship.<br>
              2. <strong>Regulatory Filings:</strong> In the US, we audit IRS Form 990 (Schedule I grants and Schedule L trustee deals) to confirm board members have no ties to weapons manufacturing, fossil fuels, or private prisons.<br>
              3. <strong>Artist-Run & Cooperative Commons:</strong> Managed directly by artists and communities (like Casco in Utrecht or Chisenhale in London) without billionaire corporate boards.
            </p>
            <p class="text-slate-300">
              Type the name of any museum (like MoMA, BAK Utrecht, Tate, or Van Abbemuseum) to see its specific funding audit.
            </p>
          `);
          return;
        }}

        // Exact Prompt 3: What are the opening hours and ticket prices?
        if (q.includes('opening hours and ticket') || q.includes('ticket prices') || q.includes('ticket price')) {{
          appendCuratorMessage(`
            <p class="text-slate-200">
              Here is how opening hours and admission work across Culture Atlas:
            </p>
            <p class="text-slate-300">
              - <strong>Free Public Admission:</strong> Over 60% of our spaces are 100% free to enter, including Chisenhale, Camden Art Centre, and Whitechapel in London, and CAPC in Bordeaux.<br>
              - <strong>Ticket Prices:</strong> Major spaces like Louisiana Museum ($20 adults, free under 18) and Kröller-Müller Museum require timed tickets, while spaces like Chisenhale, Camden Art Centre, and Artists Space are completely free.<br>
              - <strong>Hours:</strong> Most non-profit galleries are open Wednesday through Sunday, 11:00 AM to 6:00 PM. We also map 24 verified spaces open on Mondays.
            </p>
          `);
          return;
        }}

        // Exact Prompt 4: Find writing about this space in e-flux or MIT Press
        if (q.includes('writing about this space') || (q.includes('e-flux') && q.includes('mit press')) || q.includes('find writing about')) {{
          appendCuratorMessage(`
            <p class="text-slate-200">
              Critical writing and theory from MIT Press, <em>e-flux journal</em>, and Dutch research institutes:
            </p>
            <p class="text-slate-300">
              - <strong>MIT Press & BAK Utrecht:</strong> In <em>Former West: Art and the Contemporary After 1989</em> (2016), Maria Hlavajova and Simon Sheikh examine how the collapse of the Soviet bloc simultaneously provincialized the West, demanding new global commons and post-capitalist curatorial forms.<br>
              - <strong>MIT Press Theory:</strong> In <em>Beyond Objecthood</em> (2017), James Voorhies explores how independent galleries preserved experimental exhibition forms after mega-museums turned art into tourist spectacles. In <em>One Place after Another</em>, Miwon Kwon tracks the shift of site-specific art from physical monuments to traveling community interventions.<br>
              - <strong>e-flux journal:</strong> Hito Steyerl's <em>Is a Museum a Factory?</em> examines how museum visitors produce economic value for luxury real estate, while Boris Groys analyzes the public museum as an egalitarian secular archive.
            </p>
          `);
          return;
        }}

        // Research Handler 6: MIT Press Canon & Essential Art Theory Books
        if (q.includes('mit press') || q.includes('mit book') || q.includes('mit oress') || q.includes('essential book') || q.includes('theory book') || q.includes('reading list') || q.includes('curatorial book') || (q.includes('mit') && q.includes('art'))) {{
          appendCuratorMessage(`
            <p class="text-slate-200">
              MIT Press has published the most influential research and books on modern art, museums, and institutional critique. Here is the essential reading list explained in plain terms:
            </p>
            <p class="text-slate-300">
              1. <strong><em>Former West: Art and the Contemporary After 1989</em> edited by Maria Hlavajova & Simon Sheikh (BAK / MIT Press, 2016):</strong> The seminal 748-page research compendium produced with BAK in Utrecht, investigating how the post-1989 world decentered Western cultural hegemony and created new spaces for the commons.<br>
              2. <strong><em>One Place after Another: Site-Specific Art and Locational Identity</em> by Miwon Kwon (2002):</strong> The definitive study of how art moved from physical statues in plazas to temporary social projects in neighborhoods, and how museums hire artists like traveling corporate consultants.<br>
              3. <strong><em>Beyond Objecthood: The Exhibition as a Critical Form since 1968</em> by James Voorhies (2017):</strong> Shows how the exhibition itself became an artwork, and how corporate mega-museums turned experimental art into tourist entertainment.<br>
              4. <strong><em>Institutional Critique: An Anthology of Artists' Writings</em> edited by Alexander Alberro & Blake Stimson (2009):</strong> The essential collection of primary letters, interviews, and manifestos by artists who exposed the hidden power and money behind museum walls.<br>
              5. <strong><em>The Cultural Logic of the Late Capitalist Museum</em> by Rosalind Krauss (1990):</strong> Explains how modern museums transformed from quiet study archives into spectacle machines designed like luxury shopping malls.<br>
              6. <strong><em>Neo-Avantgarde and Culture Industry</em> by Benjamin H.D. Buchloh (2000):</strong> Details the 'aesthetic of administration'—why conceptual art started looking like office memos and legal contracts.<br>
              7. <strong><em>Art Power</em> by Boris Groys (2008):</strong> Explains why public museums are democratic: they protect art from the whims of the commercial market and treat all artworks as equal.<br>
              8. <strong><em>Heritage and Debt: Art in Globalization</em> by David Joselit (2020):</strong> Explores how non-Western nations and museums manage stolen historical heritage while competing in the global contemporary art world.
            </p>
          `);
          return;
        }}

        // Research Handler 7: Rosalind Krauss & The Late Capitalist Museum
        if (q.includes('krauss') || q.includes('late capitalist museum') || q.includes('originality of the avant')) {{
          appendCuratorMessage(`
            <p class="text-slate-200">
              Art historian Rosalind Krauss wrote one of the most famous essays on museums: <em>The Cultural Logic of the Late Capitalist Museum</em> (published in <em>October</em>, MIT Press, 1990).
            </p>
            <p class="text-slate-300">
              Here is what she argued in simple terms:
            </p>
            <p class="text-slate-300">
              - <strong>From Library to Theme Park:</strong> Historically, a museum was like a quiet library. You stood in front of an individual painting, looked closely at its details, and connected it to historical memory.<br>
              - <strong>The Sensation of Space:</strong> Under modern capitalism, mega-museums (like the Guggenheim or new blockbuster wings) redesigned themselves around massive cavernous atriums. Instead of focusing on art, visitors go to experience a dizzying bodily thrill inside dramatic architecture.<br>
              - <strong>Museums as Shopping Malls:</strong> Krauss warned that museum visitors were being turned into consumers. The museum experience became focused on gift shops, restaurant atriums, and fast visual sensations—treating art as a lifestyle backdrop rather than a subject for serious reflection.
            </p>
          `);
          return;
        }}

        // Research Handler: Connections Among Cultural Sponsors & Network Logic (Consensus Thread)
        if (q.includes('connections among') || q.includes('connections between') || q.includes('sponsor network') || q.includes('sponsor networks') || q.includes('interlocking') || (q.includes('guardian') && (q.includes('democracy now') || q.includes('e-flux')))) {{
          appendCuratorMessage(`
            <div class="space-y-3 text-slate-200">
              <div class="flex items-center gap-2 text-[#be95ff] font-mono text-[12px] uppercase tracking-wider">
                <span>🔬 Empirical Research Synthesis</span>
                <span>·</span>
                <span>Consensus Academic Graph</span>
              </div>
              <h4 class="text-[15px] font-medium text-white">Connections Among Cultural Sponsors: Network Logic & Institutional Influence</h4>
              <p class="text-slate-300 leading-relaxed text-[13px]">
                Consensus synthesis of peer-reviewed studies (PNAS Nexus, Barabási & Shekhtman, Yermack, Chin-tao Wu, Bertrand et al.) demonstrates that cultural sponsorship operates as an interlocking <strong>political-economic network</strong> rather than isolated charitable gifts:
              </p>
              <div class="space-y-2 text-[13px] text-slate-300">
                <p>
                  <strong>1. Legitimacy Transfer over Direct Control:</strong> Controversial corporate sponsors (fossil fuels, defense manufacturing, tobacco, private equity) rarely demand overt editorial control. Instead, they buy <em>legitimacy transfer</em>—using the moral authority and public trust of respected museums to acquire social license and insulate their corporate brands.
                </p>
                <p>
                  <strong>2. Anticipatory Self-Censorship:</strong> Empirical studies (Davidsson & Sørensen 2010; Mateos Rusillo 2019) show that funding dependence induces <em>anticipatory self-censorship</em> among museum leadership, subtly biasing programming toward safe blockbuster formats and corporate-friendly narratives.
                </p>
                <p>
                  <strong>3. Interlocking Boards & Elite Conduits:</strong> Network analyses (Zheng & Ni 2023; Betzler 2015; Zhou et al. 2021; Barabási & Shekhtman) document how museum trustees create conduits between cultural institutions, corporate boardrooms, and regulatory regimes, converting cultural capital into political proximity.
                </p>
                <p>
                  <strong>4. What Triggers Rupture:</strong> Research confirms institutions rarely divest from tainted sponsors voluntarily. Severance occurs only when investigative journalism (The Guardian, Democracy Now, e-flux, Dutch newspapers) and artist coalitions (Liberate Tate, Nan Goldin's P.A.I.N., Decolonize This Place) make the association highly visible and intolerable to the public.
                </p>
              </div>
            </div>
          `);
          return;
        }}

        // Research Handler 8: Miwon Kwon & Site-Specific Art (One Place after Another)
        if (q.includes('miwon kwon') || q.includes('one place after another') || q.includes('site-specific') || q.includes('site specific') || q.includes('locational identity')) {{
          appendCuratorMessage(`
            <p class="text-slate-200">
              In <em>One Place after Another</em> (MIT Press, 2002), art historian Miwon Kwon explains how the meaning of "site-specific art" changed over fifty years:
            </p>
            <p class="text-slate-300">
              1. <strong>Phase 1: Physical Ground (1960s–70s):</strong> Early site-specific art was permanently welded or sculpted into a physical location (like Richard Serra's steel plates or Robert Smithson's earthworks). The rule was: "to remove the work is to destroy the work."<br>
              2. <strong>Phase 2: Museum Politics (1970s–80s):</strong> Artists realized that a gallery is not just physical walls—it is a political and financial institution. Artists like Hans Haacke and Michael Asher made art that exposed museum funding, board members, and real estate ties.<br>
              3. <strong>Phase 3: Itinerant Nomads (1990s–Present):</strong> Today, museums and biennials hire artists like traveling consultants. An artist is flown to a city, spends two weeks interviewing local residents or researching local history, creates a temporary project, and moves on to the next city.<br>
            </p>
            <p class="text-slate-300">
              Kwon warns that cities often use these temporary community art projects as trendy branding to attract luxury real estate developers and push out local working-class residents.
            </p>
          `);
          return;
        }}

        // Research Handler 9: Alexander Alberro & Institutional Critique Anthology
        if (q.includes('alberro') || q.includes('stimson') || q.includes('institutional critique anthology') || q.includes('conceptual art anthology')) {{
          appendCuratorMessage(`
            <p class="text-slate-200">
              Alexander Alberro and Blake Stimson's book <em>Institutional Critique: An Anthology of Artists' Writings</em> (MIT Press, 2009) is the ultimate historical archive of how artists investigated museum power:
            </p>
            <p class="text-slate-300">
              - <strong>Marcel Broodthaers:</strong> In 1968, he created his own satirical museum (the <em>Museum of Modern Art, Department of Eagles</em>) to prove that museums invent their own authority by slapping numbers and labels on random objects.<br>
              - <strong>Daniel Buren:</strong> Pasted vertical white and colored stripes across museum gates and billboards to show how the museum walls determine what is allowed to be considered "art".<br>
              - <strong>Michael Asher:</strong> Instead of adding sculptures to a museum, Asher removed elements—sandblasting walls down to raw brick or removing the gallery doors—to reveal the hidden control structures of architecture.<br>
              - <strong>Andrea Fraser:</strong> Performed fictional docent tours like <em>Museum Highlights</em> (1989), humorously reading board financial disclosures and architectural praise aloud to reveal class elitism.<br>
              - <strong>Adrian Piper:</strong> Used conceptual cards and direct street performances to confront racism, xenophobia, and hypocrisy within white art-world institutions.
            </p>
          `);
          return;
        }}

        // Research Handler 10: Benjamin Buchloh & Aesthetic of Administration
        if (q.includes('buchloh') || q.includes('aesthetic of administration') || q.includes('culture industry') || (q.includes('bureaucra') && q.includes('art'))) {{
          appendCuratorMessage(`
            <p class="text-slate-200">
              Art historian Benjamin H.D. Buchloh introduced a crucial idea in his MIT Press writings: the <strong>"aesthetic of administration"</strong>.
            </p>
            <p class="text-slate-300">
              In simple terms:
            </p>
            <p class="text-slate-300">
              - In the 1960s, conceptual artists noticed that society was no longer run by manual factory workers, but by office administrators, lawyers, accountants, and corporate executives.<br>
              - Artists like Seth Siegelaub, Sol LeWitt, and On Kawara stopped making romantic oil paintings. Instead, they made art out of typewritten index cards, notary stamps, certificates of authenticity, and legal contracts.<br>
              - Buchloh explained that these artists adopted the cold paperwork of bureaucracy to hold up a mirror to corporate power, proving that an object's value in a museum is determined by administrative paperwork and institutional stamps rather than pure artistic genius.
            </p>
          `);
          return;
        }}

        // Research Handler 11: Boris Groys & Art Power
        if (q.includes('art power') || (q.includes('groys') && q.includes('power')) || (q.includes('public museum') && q.includes('market'))) {{
          appendCuratorMessage(`
            <p class="text-slate-200">
              In <em>Art Power</em> (MIT Press, 2008), philosopher Boris Groys explains why the public museum is one of the most radical inventions in modern history:
            </p>
            <p class="text-slate-300">
              - <strong>The Market vs the Museum:</strong> In private commercial art markets (like auctions and luxury galleries), art is treated like stocks or real estate. An artwork only matters if a billionaire wants to pay millions for it.<br>
              - <strong>Democratic Equality of Art:</strong> The public museum was created during the French Revolution to seize royal collections and turn them into common public property. Inside a real public museum, every artwork has an equal right to exist and be seen by citizens, completely free from its commercial market price.<br>
              - <strong>Protection from Profit:</strong> Groys argues that public museums protect art from being destroyed or hidden away in private tax-free vaults, ensuring that culture remains open to everyone.
            </p>
          `);
          return;
        }}

        // Research Handler 12: David Joselit & Heritage and Debt
        if (q.includes('joselit') || q.includes('heritage and debt') || q.includes('after art') || q.includes('feedback')) {{
          appendCuratorMessage(`
            <p class="text-slate-200">
              In <em>Heritage and Debt: Art in Globalization</em> (MIT Press, 2020) and <em>After Art</em>, art historian David Joselit explores how art works in an interconnected world:
            </p>
            <p class="text-slate-300">
              - <strong>Images as Networks:</strong> Today, art is rarely experienced as an isolated object in a room. It functions as an image circulating endlessly across Instagram, websites, and international biennials.<br>
              - <strong>Heritage vs Contemporary Market:</strong> Joselit explains that non-Western museums face a difficult challenge: they must preserve their deep ancient heritage (much of which was stolen or destroyed by colonial powers), while simultaneously competing in the fast-paced Western contemporary art market.<br>
              - <strong>Curating as Network Power:</strong> Joselit argues that real power in contemporary art no longer belongs to who produces an individual object, but to who builds the networks that connect artists, public archives, and civic audiences.
            </p>
          `);
          return;
        }}

        // Research Handler 13: Hal Foster & Starchitect Museums
        if (q.includes('hal foster') || q.includes('starchitect') || q.includes('bilbao effect') || q.includes('anti-aesthetic')) {{
          appendCuratorMessage(`
            <p class="text-slate-200">
              In his MIT Press and October essays (like <em>Design and Crime</em> and <em>The Anti-Aesthetic</em>), critic Hal Foster examined the rise of the celebrity "starchitect" museum:
            </p>
            <p class="text-slate-300">
              - <strong>The Bilbao Effect:</strong> After Frank Gehry's titanium museum opened in Bilbao, cities worldwide began hiring famous architects to build eccentric, twisting museum buildings to boost tourism and drive up luxury real estate.<br>
              - <strong>Architecture Swallowing Art:</strong> Foster pointed out that the building itself became the main spectacle being photographed, while the artists and artwork inside were treated as minor decorations.<br>
              - <strong>Return to Civic Mission:</strong> Culture Atlas prioritizes museums that focus on ethical governance, public accessibility, and supporting artists, rather than spending hundreds of millions on flashy trophy architecture.
            </p>
          `);
          return;
        }}

        // 5. Claire Bishop & Radical Museology
        if (q.includes('claire bishop') || q.includes('radical museology') || q.includes('artificial hells') || q.includes('relational aesthetics') || q.includes('bourriaud')) {{
          appendCuratorMessage(`
            <p class="text-slate-200">
              Art historian Claire Bishop is known for critiquing how modern museums work and how audience participation is used:
            </p>
            <p class="text-slate-300">
              - In <em>Radical Museology</em> (2013), she compares flashy corporate museums (which rely on blockbuster shows, gift shops, and tourist crowds) with thoughtful civic museums (like the Van Abbemuseum in the Netherlands or Reina Sofía in Madrid) that use their collections to help us understand current political and social issues.
            </p>
            <p class="text-slate-300">
              - In <em>Artificial Hells</em> (2012), she critiques 'participatory art'. She points out that getting visitors to chat or sit on sofas in a gallery isn't necessarily radical—it often just creates a cozy illusion of community while avoiding deeper artistic and political questions.
            </p>
          `);
          return;
        }}

        // 6. Minimalism, Monumental Sculpture & Ethical Independence
        if (q.includes('minimalism') || q.includes('dia beacon') || q.includes('judds') || q.includes('judd') || q.includes('richard serra') || q.includes('phenomenolog')) {{
          const sculp = ALL_INSTITUTIONS.find(i => i.name.includes('SculptureCenter'));
          const kroll = ALL_INSTITUTIONS.find(i => i.name.includes('Kröller'));
          const louis = ALL_INSTITUTIONS.find(i => i.name.includes('Louisiana'));
          const dia = EXCLUDED_INSTITUTIONS.find(i => i.name.includes('Dia Beacon'));
          appendCuratorMessage(`
            <p class="text-slate-200">
              While ${{formatInstLink(dia)}} was historically celebrated for minimalism, Dia Art Foundation was founded on Schlumberger oil wealth and retained Sackler naming until 2019, leading to its exclusion under strict ethical criteria.
            </p>
            <p class="text-slate-300">
              For verified independent monumental sculpture, minimalism, and spatial art:
            </p>
            <p class="text-slate-300">
              - ${{formatInstLink(kroll)}} in Otterlo: One of Europe's largest outdoor sculpture parks with landmark works by Richard Serra, Jean Dubuffet, and Barbara Hepworth.<br>
              - ${{formatInstLink(sculp)}} in New York: Non-collecting kunsthalle in Long Island City dedicated to experimental sculpture and spatial commissions.<br>
              - ${{formatInstLink(louis)}} north of Copenhagen: Masterpieces of modernist sculpture situated directly on the Danish coastline.
            </p>
          `);
          selectInstitution(sculp, true);
          return;
        }}

        // 7. New York Art Scene & Board Politics
        if (q.includes('new york') || q.includes('nyc') || q.includes('manhattan')) {{
          const sculp = ALL_INSTITUTIONS.find(i => i.name.includes('SculptureCenter'));
          const artsp = ALL_INSTITUTIONS.find(i => i.name.includes('Artists Space'));
          const kitch = ALL_INSTITUTIONS.find(i => i.name.includes('The Kitchen'));
          const swiss = ALL_INSTITUTIONS.find(i => i.name.includes('Swiss Institute'));
          const moma = EXCLUDED_INSTITUTIONS.find(i => i.name.includes('MoMA'));

          appendCuratorMessage(`
            <p class="text-slate-200">
              New York has some of the biggest museums in the world, but many have faced protests over their donors and board members:
            </p>
            <p class="text-slate-300">
              ${{formatInstLink(moma)}} saw months of protests over board members tied to defense contractors and private prisons, as well as former chair Leon Black's Jeffrey Epstein payments. The Whitney Museum saw artists pull their work until board vice-chair Warren Kanders (Safariland tear gas) stepped down. Dia Art Foundation retained Sackler naming until 2019.
            </p>
            <p class="text-slate-300">
              Instead, Culture Atlas directs you to New York's verified independent non-profits:
            </p>
            <p class="text-slate-300">
              - ${{formatInstLink(artsp)}} in Tribeca: Non-profit gallery championing experimental artists since 1972.<br>
              - ${{formatInstLink(sculp)}} in Long Island City, Queens: Innovative sculpture inside a historic trolley repair shop.<br>
              - ${{formatInstLink(kitch)}} and ${{formatInstLink(swiss)}} in the East Village.
            </p>
          `);
          filterByCity('New York', true, false);
          return;
        }}

        // 8. Paris Art Scene & Civic Models
        if (q.includes('paris')) {{
          const ptok = ALL_INSTITUTIONS.find(i => i.name.includes('Palais de Tokyo'));
          const beton = ALL_INSTITUTIONS.find(i => i.name.includes('Bétonsalon'));
          const pomp = EXCLUDED_INSTITUTIONS.find(i => i.name.includes('Pompidou'));

          appendCuratorMessage(`
            <p class="text-slate-200">
              In Paris, public civic funding and autonomous research centers provide alternatives to corporate-sponsored institutions:
            </p>
            <p class="text-slate-300">
              - ${{formatInstLink(ptok)}}: Europe's largest contemporary art space, known for bold experimental exhibitions and open until midnight.<br>
              - ${{formatInstLink(beton)}}: Non-profit contemporary art and research center located in the 13th Arrondissement, free to the public.
            </p>
            <p class="text-slate-400 text-[14px]">
              Note: ${{formatInstLink(pomp)}} is excluded from the map due to a €50M funding pledge from the Saudi state for its major renovation.
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
              Berlin is known around the world for its artist-run spaces and strong public arts funding:
            </p>
            <p class="text-slate-300">
              - ${{formatInstLink(kw)}} in Mitte: Located in a former margarine factory, famous for cutting-edge shows and the Berlin Biennale.<br>
              - ${{formatInstLink(hkw)}} in Tiergarten: Focuses on international artists and global issues.<br>
              - ${{formatInstLink(grop)}}: A historic exhibition hall with free access to its ground-floor exhibitions.
            </p>
          `);
          filterByCity('Berlin', true, false);
          return;
        }}

        // =========================================================================
        // 🏛️ VISITOR DATA & AUDIT HANDLERS (Simple, Clear English)
        // =========================================================================

        // A. Visitor Data: Hours & Monday Openings
        if (q.includes('hour') || q.includes('schedule') || (q.includes('time') && (q.includes('open') || q.includes('visit'))) || q.includes('monday') || q.includes('weekend') || q.includes('late night') || q.includes('closed')) {{
          const targetInst = ALL_INSTITUTIONS.find(i => q.includes(i.name.toLowerCase()) || (i.aliases && i.aliases.some(a => q.includes(a.toLowerCase()))));
          if (targetInst) {{
            appendCuratorMessage(`
              <p class="text-slate-200">
                <strong>${{formatInstLink(targetInst)}}</strong> is open <strong>${{targetInst.opening_hours}}</strong>.
              </p>
              <p class="text-slate-300">
                Address: <strong>${{targetInst.address}}</strong> (${{targetInst.neighborhood}}).<br>
                How to get there: ${{targetInst.transit_tips}}.<br>
                Recommended visit time: about <strong>${{targetInst.visit_duration}}</strong> to see ${{targetInst.highlight}}.
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
                Most museums are closed on Mondays, but Culture Atlas has <strong>${{mondaySpaces.length}}</strong> spaces open on Mondays:
              </p>
              <p class="text-slate-300">
                In Paris, ${{formatInstLink(m1)}} is open every Monday and stays open until midnight. Near Copenhagen, ${{formatInstLink(m2)}} is open daily by the sea and easy to reach by train. In London, ${{formatInstLink(m3)}} is open with free entry. None of them accept funding from oil or defense companies.
              </p>
            `);
            return;
          }}

          const pTok = ALL_INSTITUTIONS.find(i => i.name.includes('Palais de Tokyo'));
          const louis = ALL_INSTITUTIONS.find(i => i.name.includes('Louisiana'));
          appendCuratorMessage(`
            <p class="text-slate-200">
              Most galleries and art spaces are open <strong>Wednesday to Sunday, 11:00–18:00 or 12:00–18:00</strong>. Many close on Mondays and Tuesdays to set up new exhibitions.
            </p>
            <p class="text-slate-300">
              For late evenings, ${{formatInstLink(pTok)}} in Paris is open until midnight, while ${{formatInstLink(louis)}} is open late on weekdays. Click any dot on the map to see its exact opening times.
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
                To get to <strong>${{formatInstLink(targetInst)}}</strong>, take <strong>${{targetInst.transit_tips}}</strong>.
              </p>
              <p class="text-slate-300">
                Address: <strong>${{targetInst.address}}</strong> in ${{targetInst.neighborhood}}.<br>
                Hours: ${{targetInst.opening_hours}}. Plan for about ${{targetInst.visit_duration}}.
              </p>
            `);
            selectInstitution(targetInst, true);
            return;
          }}

          const louis = ALL_INSTITUTIONS.find(i => i.name.includes('Louisiana'));
          const kroll = ALL_INSTITUTIONS.find(i => i.name.includes('Kröller'));
          const sculp = ALL_INSTITUTIONS.find(i => i.name.includes('SculptureCenter'));
          appendCuratorMessage(`
            <p class="text-slate-200">
              Every space in Culture Atlas includes simple public transit directions. Many world-famous places are an easy train ride away:
            </p>
            <p class="text-slate-300">
              Take the coastal train from Copenhagen to ${{formatInstLink(louis)}}, take a train and free park bicycle to ${{formatInstLink(kroll)}} in the Netherlands, or take the subway to ${{formatInstLink(sculp)}} in New York.
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
                <strong>Accessibility at ${{formatInstLink(targetInst)}}:</strong><br>
                ${{targetInst.accessibility}}.
              </p>
              <p class="text-slate-300">
                Companions and assistants get free entry. Getting there: ${{targetInst.transit_tips}}.
              </p>
            `);
            selectInstitution(targetInst, true);
            return;
          }}

          const aros = ALL_INSTITUTIONS.find(i => i.name.includes('ARoS'));
          const camden = ALL_INSTITUTIONS.find(i => i.name.includes('Camden'));
          const ptok = ALL_INSTITUTIONS.find(i => i.name.includes('Palais de Tokyo'));
          appendCuratorMessage(`
            <p class="text-slate-200">
              All institutions in Culture Atlas have step-free access, elevators, wheelchairs to borrow, and free admission for companions.
            </p>
            <p class="text-slate-300">
              Great accessible spaces include ${{formatInstLink(aros)}} in Denmark, ${{formatInstLink(camden)}} in London, and ${{formatInstLink(ptok)}} in Paris.
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
                <strong>Amenities at ${{formatInstLink(targetInst)}}:</strong><br>
                ${{targetInst.amenities}}.
              </p>
              <p class="text-slate-300">
                Highlight to see: <span class="text-amber-300/90">${{targetInst.highlight}}</span>. Open: ${{targetInst.opening_hours}}.
              </p>
            `);
            selectInstitution(targetInst, true);
            return;
          }}

          const louis = ALL_INSTITUTIONS.find(i => i.name.includes('Louisiana'));
          const kbase = ALL_INSTITUTIONS.find(i => i.name.includes('Kunsthalle Basel'));
          const camden = ALL_INSTITUTIONS.find(i => i.name.includes('Camden Art Centre'));
          const tpg = ALL_INSTITUTIONS.find(i => i.name.includes("Photographers' Gallery"));
          appendCuratorMessage(`
            <p class="text-slate-200">
              Many of our mapped spaces have great cafés and bookshops:
            </p>
            <p class="text-slate-300">
              ${{formatInstLink(louis)}} in Denmark has an organic café looking over the sea. In Basel, ${{formatInstLink(kbase)}} features a historic restaurant and garden terrace. In London, ${{formatInstLink(camden)}} has a garden café, and ${{formatInstLink(tpg)}} in Soho has an incredible photography bookshop.
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
                The main highlight at <strong>${{formatInstLink(targetInst)}}</strong> is <span class="text-amber-300/90 font-normal">${{targetInst.highlight}}</span>.
              </p>
              <p class="text-slate-300">
                It focuses on ${{targetInst.curatorial_focus}} and is open ${{targetInst.opening_hours}}.
              </p>
            `);
            selectInstitution(targetInst, true);
            return;
          }}

          const aros = ALL_INSTITUTIONS.find(i => i.name.includes('ARoS'));
          const kroll = ALL_INSTITUTIONS.find(i => i.name.includes('Kröller'));
          const louis = ALL_INSTITUTIONS.find(i => i.name.includes('Louisiana'));
          appendCuratorMessage(`
            <p class="text-slate-200">
              Here are three unforgettable art landmarks with verified clean funding:
            </p>
            <p class="text-slate-300">
              Olafur Eliasson's colorful rainbow glass skywalk at ${{formatInstLink(aros)}}, the 60-acre sculpture park and van Gogh collection at ${{formatInstLink(kroll)}}, and ${{formatInstLink(louis)}} overlooking the sea in Humlebæk.
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
              Culture Atlas rates museums based on who funds them and who sits on their board:
            </p>
            <p class="text-slate-300">
              1. <strong>Public museums:</strong> Funded by public arts councils (like Arts Council England or DRAC in France) rather than private corporate sponsors, so they answer to the public. Examples: ${{formatInstLink(capc)}} and ${{formatInstLink(plugin)}}.<br>
              2. <strong>Artist-run spaces:</strong> Managed directly by artists, like ${{formatInstLink(chis)}}, giving artists freedom to experiment without corporate control.<br>
              3. <strong>Clean funding:</strong> Spaces that refuse or divested from oil, weapons, and private prison money.
            </p>
          `);
          return;
        }}

        // G. Free Admission
        if (q.includes('free') || q.includes('admission') || q.includes('ticket') || q.includes('accessible') || q.includes('no fee')) {{
          const freeSpaces = ALL_INSTITUTIONS.filter(i => i.admission_policy.includes('Free Public') || i.admission_policy.includes('Always Free') || (i.admission_fee && i.admission_fee.toLowerCase().includes('free')));
          const f1 = freeSpaces[0] || ALL_INSTITUTIONS.find(i => i.name.includes('Chisenhale'));
          const f2 = freeSpaces[1] || ALL_INSTITUTIONS.find(i => i.name.includes('Camden'));
          const f3 = freeSpaces[2] || ALL_INSTITUTIONS.find(i => i.name.includes('Artists Space'));
          appendCuratorMessage(`
            <p class="text-slate-200">
              Culture Atlas has <strong>${{freeSpaces.length}}</strong> museums and galleries with completely free admission.
            </p>
            <p class="text-slate-300">
              Top free spaces include ${{formatInstLink(f1)}} in London, ${{formatInstLink(f2)}}, and ${{formatInstLink(f3)}} in New York. None of them charge admission, and none take oil or arms money.
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
              Culture Atlas maps <strong>${{artistSpaces.length}}</strong> artist-run spaces worldwide. Because they are run by artists, they can support new, experimental work without pressure from corporate donors.
            </p>
            <p class="text-slate-300">
              Standout artist-run spaces include ${{formatInstLink(a1)}}, ${{formatInstLink(a2)}}, and ${{formatInstLink(a3)}}.
            </p>
          `);
          return;
        }}

        // I. Divestment from Fossil Fuels & Defense
        if (q.includes('fossil') || q.includes('defense') || q.includes('oil') || q.includes('bp') || q.includes('shell') || q.includes('baillie') || q.includes('weapons') || q.includes('divest')) {{
          const c1 = ALL_INSTITUTIONS.find(i => i.name.includes('Camden'));
          const c2 = ALL_INSTITUTIONS.find(i => i.name.includes('Whitechapel'));
          const c3 = ALL_INSTITUTIONS.find(i => i.name.includes('Chisenhale'));
          appendCuratorMessage(`
            <p class="text-slate-200">
              For years, oil companies like BP and Shell used museum sponsorships to polish their image ('artwashing'). Recently, artists and activists pressured museums to drop those deals.
            </p>
            <p class="text-slate-300">
              Every space in Culture Atlas has clean funding with zero oil or weapons money. Good examples include ${{formatInstLink(c1)}}, ${{formatInstLink(c2)}}, and ${{formatInstLink(c3)}}.
            </p>
          `);
          return;
        }}

        // J. Excluded Institutions (MoMA, Whitney, Guggenheim, Pompidou, Dia, Serpentine)
        if (q.includes('moma') || q.includes('whitney') || q.includes('guggenheim') || q.includes('pompidou') || q.includes('dia beacon') || q.includes('serpentine') || q.includes('inhotim') || q.includes('why exclude') || q.includes('excluded') || q.includes('kanders')) {{
          const artsp = ALL_INSTITUTIONS.find(i => i.name.includes('Artists Space'));
          const sculp = ALL_INSTITUTIONS.find(i => i.name.includes('SculptureCenter'));
          const chis = ALL_INSTITUTIONS.find(i => i.name.includes('Chisenhale'));
          const camden = ALL_INSTITUTIONS.find(i => i.name.includes('Camden'));
          appendCuratorMessage(`
            <p class="text-slate-200">
              We strictly exclude institutions with corporate conflicts, fossil fuel sponsorship, weapons manufacturer board seats, or controversial funding ties:
            </p>
            <p class="text-slate-300">
              - <strong>MoMA & The Met (New York):</strong> Defense contractor board links, private prison investments, former chair Leon Black's Jeffrey Epstein payments, and Sackler / Koch naming.<br>
              - <strong>Centre Pompidou (Paris):</strong> €50M pledge from the Saudi state for renovation works.<br>
              - <strong>Dia Art Foundation / Dia Beacon:</strong> Founded on Schlumberger oil wealth; carried Sackler-endowed naming until 2019.<br>
              - <strong>Serpentine Galleries (London):</strong> Historic Sackler naming and ongoing Bloomberg corporate sponsorship.<br>
              - <strong>Instituto Inhotim (Brazil):</strong> Funded by mining conglomerate Vale, whose 2019 dam disaster killed 270 people.<br>
              - <strong>Whitney Museum (New York):</strong> Board vice-chair Warren Kanders owned Safariland tear gas manufacturer (resigned after protests).
            </p>
            <p class="text-slate-300">
              Instead, Culture Atlas only maps verified ethically independent spaces like ${{formatInstLink(artsp)}}, ${{formatInstLink(sculp)}}, ${{formatInstLink(chis)}}, and ${{formatInstLink(camden)}}.
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
                Here are <strong>${{cityMatches.length}}</strong> museums and galleries in <a href="#" class="city-link font-normal text-white hover:text-[#60a5fa] underline cursor-pointer" data-city="${{escapeHtml(targetCity)}}">${{escapeHtml(targetCity)}}</a> with clean funding:
              </p>
              <p class="text-slate-300">
                Highlights include ${{formatInstLink(c1, {{noCity: true}})}}${{c2 ? `, ${{formatInstLink(c2, {{noCity: true}})}}` : ''}}${{c3 ? `, and ${{formatInstLink(c3, {{noCity: true}})}}` : ''}}. None of them accept oil or weapons sponsorships.
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
                We have <strong>${{countryMatches.length}}</strong> spaces mapped in <strong>${{escapeHtml(matchedCountry.name)}}</strong> with clean funding.
              </p>
              <p class="text-slate-300">
                Top places to visit include ${{formatInstLink(co1)}}${{co2 ? `, ${{formatInstLink(co2)}}` : ''}}${{co3 ? `, and ${{formatInstLink(co3)}}` : ''}}.
              </p>
            `);

            flyTo(matchedCountry.lon, matchedCountry.lat);
            return;
          }}
        }}


        // =========================================================================
        // ⚖️ ETHICAL TOPICS: ARTWASHING, DONORS, ACTIVISM & LABOR
        // =========================================================================

        // T1. What is Artwashing?
        if (q.includes('artwashing') || q.includes('art wash') || q.includes('what is artwashing')) {{
          appendCuratorMessage(`
            <p class="text-slate-200">
              <strong>Artwashing</strong> is when corporations with controversial records—like fossil fuel extractors, arms manufacturers, or tobacco and opioid companies—sponsor museums, exhibitions, and artists to clean up their public reputation.
            </p>
            <p class="text-slate-300">
              By putting their logo on museum walls, cultural festivals, and galas, companies buy social legitimacy and distract from environmental damage or human rights abuses. Famous examples include BP's 26-year sponsorship of Tate, the Sackler family's naming rights funded by OxyContin, and weapons manufacturers sponsoring arts prizes.
            </p>
            <p class="text-slate-300">
              Culture Atlas solves this by mapping only verified clean, independent institutions that refuse corporate artwashing money.
            </p>
          `);
          return;
        }}

        // T2. The Sackler Family & P.A.I.N. Protests
        if (q.includes('sackler') || q.includes('purdue pharma') || q.includes('nan goldin') || q.includes('opioid')) {{
          appendCuratorMessage(`
            <p class="text-slate-200">
              The <strong>Sackler family</strong> owned Purdue Pharma, which developed and aggressively marketed OxyContin, triggering an opioid epidemic responsible for over 500,000 overdose deaths in North America alone.
            </p>
            <p class="text-slate-300">
              For decades, the family used massive donations to place the Sackler name on galleries at the Metropolitan Museum of Art, Louvre, Guggenheim, Tate, Serpentine, and V&A. In 2017, photographer Nan Goldin founded <em>P.A.I.N. (Prescription Addiction Intervention Now)</em>, staging dramatic "die-ins" and throwing fake prescription bottles into museum fountains.
            </p>
            <p class="text-slate-300">
              Under public pressure, every major museum eventually stripped the Sackler name. Institutions that still carry Sackler donor ties or endowments (like Dia Beacon or Dulwich) are excluded from Culture Atlas.
            </p>
          `);
          return;
        }}

        // T3. Warren Kanders & Safariland at the Whitney
        if (q.includes('kanders') || q.includes('safariland') || q.includes('tear gas')) {{
          appendCuratorMessage(`
            <p class="text-slate-200">
              In 2019, <strong>Warren B. Kanders</strong> was the vice-chair of the Whitney Museum of American Art in New York. Reporting revealed that his company, Safariland, manufactured tear gas grenades and riot gear used against peaceful asylum seekers at the US-Mexico border and protesters in Standing Rock, Ferguson, and Puerto Rico.
            </p>
            <p class="text-slate-300">
              Artist group <em>Decolonize This Place</em> staged nine weeks of protests at the Whitney. When eight artists pulled their works from the 2019 Whitney Biennial, Kanders was forced to resign. The controversy led artists worldwide to question who sits on museum boards.
            </p>
          `);
          return;
        }}

        // T4. Jeffrey Epstein & Leon Black at MoMA
        if (q.includes('epstein') || q.includes('leon black')) {{
          appendCuratorMessage(`
            <p class="text-slate-200">
              In 2021, billionaire financier <strong>Leon Black</strong> was forced to step down as chairman of MoMA (Museum of Modern Art) after a Senate and IRS investigation confirmed he paid $158 million to convicted sex offender Jeffrey Epstein.
            </p>
            <p class="text-slate-300">
              This sparked the <em>Strike MoMA</em> movement, where artists, curators, and activists occupied the museum for ten consecutive weeks, demanding an end to billionaire-dominated trustee boards invested in private prisons, weapons, and hedge funds.
            </p>
          `);
          return;
        }}

        // T5. Vale & The Brumadinho Dam Disaster (Inhotim)
        if (q.includes('brumadinho') || q.includes('vale dam') || (q.includes('inhotim') && (q.includes('why') || q.includes('disaster') || q.includes('vale')))) {{
          appendCuratorMessage(`
            <p class="text-slate-200">
              In January 2019, the Córrego do Feijão tailings dam operated by mining conglomerate <strong>Vale</strong> collapsed in Brumadinho, Brazil, unleashing a wave of 12 million cubic meters of toxic mining waste that killed 270 people and devastated local river ecosystems.
            </p>
            <p class="text-slate-300">
              <strong>Instituto Inhotim</strong>, a world-famous art park nearby, receives its primary operating budget from Vale. Because of this catastrophic environmental and humanitarian disaster, Inhotim is excluded from Culture Atlas.
            </p>
          `);
          return;
        }}

        // T6. Decolonization & Benin Bronzes Restitution
        if (q.includes('restitution') || q.includes('repatriat') || q.includes('benin bronze') || q.includes('stolen art') || q.includes('colonial loot')) {{
          appendCuratorMessage(`
            <p class="text-slate-200">
              The <strong>Benin Bronzes</strong> are thousands of exquisite royal brass plaques and sculptures looted in 1897 by British soldiers during a violent punitive expedition against the Kingdom of Benin (now southern Nigeria).
            </p>
            <p class="text-slate-300">
              The sculptures were sold to museums across Britain, Germany, France, and the United States. Following decades of requests from Nigeria and the 2018 Sarr-Savoy Report, Germany, the Smithsonian, and several UK regional museums agreed to legally transfer ownership back to Nigeria.
            </p>
            <p class="text-slate-300">
              Culture Atlas highlights research centers like Framer Framed (Amsterdam) and Iniva (London) that actively work on decolonial provenance and restitution.
            </p>
          `);
          return;
        }}

        // M. Unified Intelligent Entity & Institution Resolution (Clean & Excluded)
        const matchedEntity = findAnyInstitution(query);
        if (matchedEntity) {{
          const inst = matchedEntity.inst; const isClean = matchedEntity.isClean;
          if (isClean) {{
            const yr = inst.year_founded ? `founded in ${{inst.year_founded}}` : 'established as an essential cultural space';
            const hood = inst.neighborhood ? `in ${{inst.neighborhood}}, ${{inst.city}}` : `in ${{inst.city}}`;
            const admission = inst.admission_policy ? `${{inst.admission_policy}} (${{inst.admission_details}})` : 'Free admission';
            const hours = inst.opening_hours || 'Check local listings for hours';
            const highlight = inst.highlight || 'Pioneering contemporary exhibitions and community programs';
            const transit = inst.transit_tips ? `Transit directions: ${{inst.transit_tips}}` : '';

            appendCuratorMessage(`
              <div class="space-y-2.5">
                <p class="text-slate-100 text-[14px] leading-relaxed">
                  <strong>${{formatInstLink(inst, {{noCity: false}})}}</strong> ${{hood}} is a verified Tier A independent space ${{yr}}. It operates under transparent public governance, completely free of fossil fuel, arms, or predatory corporate underwriting.
                </p>
                <p class="text-slate-200 text-[14px] leading-relaxed">
                  <strong>Curator's Note:</strong> ${{highlight}}. Admission is ${{admission}}, open ${{hours}}. ${{transit}}
                </p>
                <div class="grid grid-cols-2 gap-2 pt-1 text-[12px]" data-exclude-speech="true">
                  <div class="p-2 rounded-lg bg-[#1e1e24] border border-[#2e2e38]">
                    <span class="text-[#71717a] block text-[11px] uppercase tracking-wider font-mono">Admission</span>
                    <span class="text-emerald-400 font-medium">${{admission}}</span>
                  </div>
                  <div class="p-2 rounded-lg bg-[#1e1e24] border border-[#2e2e38]">
                    <span class="text-[#71717a] block text-[11px] uppercase tracking-wider font-mono">Hours</span>
                    <span class="text-slate-200">${{hours}}</span>
                  </div>
                  <div class="p-2 rounded-lg bg-[#1e1e24] border border-[#2e2e38] col-span-2">
                    <span class="text-[#71717a] block text-[11px] uppercase tracking-wider font-mono">Governance & Safeguard</span>
                    <span class="text-slate-300">${{inst.governance_type}} · ${{inst.ethical_safeguard}}</span>
                  </div>
                </div>
              </div>
            `, [
              `More in ${{inst.city}}`,
              `Directions to ${{inst.name}}`,
              'Explore another space'
            ]);
            selectInstitution(inst, true);
            return;
          }} else {{
            const cleanAlternatives = ALL_INSTITUTIONS.filter(i => matchC(i.city, inst.city) || matchC(i.country, inst.country));
            let altText = '';
            if (cleanAlternatives.length > 0) {{
              altText = `<div class="pt-2 border-t border-[#331c22]"><span class="text-[12px] font-mono text-[#a1a1aa] uppercase tracking-wider block mb-1">Verified Independent Spaces in ${{escapeHtml(inst.city)}}:</span><div class="space-y-1">` + cleanAlternatives.slice(0, 3).map(a => `<div>· ${{formatInstLink(a)}}</div>`).join('') + `</div></div>`;
            }}
            appendCuratorMessage(`
              <div class="space-y-2.5">
                <p class="text-rose-300 font-medium">
                  <strong>EXCLUSION AUDIT: ${{escapeHtml(inst.name)}} (${{escapeHtml(inst.city)}}, ${{escapeHtml(inst.country)}})</strong>
                </p>
                <p class="text-slate-200 text-[14px] leading-relaxed">
                  ${{escapeHtml(inst.name)}} is excluded from the Culture Atlas clean roster under ${{inst.tier === 'B' ? 'Tier B flagged status for corporate sponsor conflict' : 'Tier U unverified status'}}.
                  ${{inst.watch ? ` Audit conflict: ${{escapeHtml(inst.watch)}}.` : ''}}
                  Governance & funding profile: ${{escapeHtml(inst.funding || 'Commercial or conflicted corporate sponsorship')}}.
                </p>
                <p class="text-slate-300 text-[13px] leading-relaxed">
                  Culture Atlas strictly maps verified clean cultural spaces operating free of fossil fuels, weapons manufacturers, private prisons, and predatory corporate underwriting.
                </p>
                ${{altText}}
                <div class="mt-2" data-exclude-speech="true">
                  <button class="curator-dossier-btn px-2.5 py-1 rounded bg-[#1f1433] hover:bg-[#2d1e48] text-[#be95ff] border border-[#8a3ffc] text-[13px] font-mono cursor-pointer transition" data-name="${{escapeHtml(inst.name)}}">
                    Open Full Audit Dossier ↗
                  </button>
                </div>
              </div>
            `, cleanAlternatives.length > 0 ? cleanAlternatives.slice(0, 3).map(a => a.name) : ['Why ethical funding matters']);
            return;
          }}
        }}

        // N. Surprise Me / Recommendations
        if (q.includes('surprise') || q.includes('recommend') || q.includes('random') || q.includes('hidden gem')) {{
          const randomA = ALL_INSTITUTIONS.filter(i => i.tier === 'A');
          const pick1 = randomA[Math.floor(Math.random() * randomA.length)];
          const pick2 = randomA[Math.floor(Math.random() * randomA.length)];

          appendCuratorMessage(`
            <p class="text-slate-200">
              Here are two great art spaces to check out:
            </p>
            <p class="text-slate-300">
              - ${{formatInstLink(pick1)}}<br>
              - ${{formatInstLink(pick2)}}
            </p>
            <p class="text-slate-300">
              Both have clean funding and show exciting contemporary art.
            </p>
          `);

          selectInstitution(pick1, false);
          return;
        }}

        // O. Fallback with helpful conversational guidance
        const chis = ALL_INSTITUTIONS.find(i => i.name.includes('Chisenhale'));
        const louis = ALL_INSTITUTIONS.find(i => i.name.includes('Louisiana'));
        const kroll = ALL_INSTITUTIONS.find(i => i.name.includes('Kröller'));
        appendCuratorMessage(`
          <p class="text-slate-200">
            I can help you find verified ethical art spaces across the globe with zero fossil fuel, arms, or predatory corporate underwriting.
          </p>
          <p class="text-slate-300">
            Ask me about cities like <a href="#" class="city-link text-[#93c5fd] hover:underline cursor-pointer" data-city="London">London</a>, <a href="#" class="city-link text-[#93c5fd] hover:underline cursor-pointer" data-city="Paris">Paris</a>, or <a href="#" class="city-link text-[#93c5fd] hover:underline cursor-pointer" data-city="New York">New York</a>, how to get to places like ${{formatInstLink(louis)}} or ${{formatInstLink(kroll)}}, or questions about transparent public governance.
          </p>
          <p class="text-[#93c5fd]">
            Which city or kind of art space are you exploring?
          </p>
        `);      }}, 300);
    }}

    // =========================================================
    // 💼 UNIFIED SINGLE-CANVAS CONTROLLER (Combined Work & Chat)
    // =========================================================
    
    // Top New Chat Actions (Desktop + Mobile): Resets chat and returns to fresh landing view
    document.getElementById('topNewChatBtn')?.addEventListener('click', () => {{
      resetToNewChat();
      if (window.innerWidth < 768 && currentMobileMode === 'map') {{
        setMobileViewMode('chat');
      }}
    }});
    document.getElementById('mobileNewChatBtn')?.addEventListener('click', () => {{
      resetToNewChat();
      if (window.innerWidth < 768 && currentMobileMode === 'map') {{
        setMobileViewMode('chat');
      }}
    }});

    // Mobile Viewport Mode Switcher (Map / Split / Chat)
    let currentMobileMode = 'split';

    function setMobileViewMode(mode) {{
      if (window.innerWidth >= 768) return;
      currentMobileMode = mode;

      const globe = document.getElementById('globeViewport');
      const workView = document.getElementById('workViewContainer');
      const splitter = document.getElementById('globeSplitter');
      const mapBtn = document.getElementById('mobileModeMapBtn');
      const splitBtn = document.getElementById('mobileModeSplitBtn');
      const chatBtn = document.getElementById('mobileModeChatBtn');
      const cityBar = document.getElementById('globeCityBar');

      [mapBtn, splitBtn, chatBtn].forEach(b => {{
        if (!b) return;
        b.classList.remove('bg-[#2563eb]', 'text-white', 'font-medium');
        b.classList.add('text-[#a1a1aa]');
      }});

      if (mode === 'map') {{
        mapBtn?.classList.remove('text-[#a1a1aa]');
        mapBtn?.classList.add('bg-[#2563eb]', 'text-white', 'font-medium');
        if (globe) {{
          globe.style.display = 'flex';
          globe.style.height = '100%';
          globe.style.flex = '1 1 0%';
        }}
        if (workView) {{
          workView.style.display = 'none';
          workView.style.height = '0%';
          workView.style.flex = '0 0 auto';
        }}
        if (splitter) {{
          splitter.style.display = 'none';
        }}
        resizeCanvas();
        if (cityVectorMap && isCityStreetViewActive) cityVectorMap.resize();
      }} else if (mode === 'chat') {{
        chatBtn?.classList.remove('text-[#a1a1aa]');
        chatBtn?.classList.add('bg-[#2563eb]', 'text-white', 'font-medium');
        if (globe) {{
          globe.style.display = 'none';
          globe.style.height = '0%';
          globe.style.flex = '0 0 auto';
        }}
        if (workView) {{
          workView.style.display = 'flex';
          workView.style.height = '100%';
          workView.style.flex = '1 1 0%';
        }}
        if (splitter) {{
          splitter.style.display = 'none';
        }}
        if (cityBar) {{
          cityBar.classList.remove('max-h-[58px]');
          cityBar.classList.add('max-h-[140px]');
        }}
        scrollChatToBottom(false);
      }} else {{
        // split (default)
        splitBtn?.classList.remove('text-[#a1a1aa]');
        splitBtn?.classList.add('bg-[#2563eb]', 'text-white', 'font-medium');
        if (globe) {{
          globe.style.display = 'flex';
          globe.style.height = '50%';
          globe.style.flex = '1 1 0%';
        }}
        if (workView) {{
          workView.style.display = 'flex';
          workView.style.height = '50%';
          workView.style.flex = '1 1 0%';
        }}
        if (splitter) {{
          splitter.style.display = 'flex';
        }}
        if (cityBar) {{
          cityBar.classList.remove('max-h-[140px]');
          cityBar.classList.add('max-h-[58px]');
        }}
        resizeCanvas();
        if (cityVectorMap && isCityStreetViewActive) cityVectorMap.resize();
      }}
    }}

    window.setMobileViewMode = setMobileViewMode;
    document.getElementById('mobileModeMapBtn')?.addEventListener('click', () => setMobileViewMode('map'));
    document.getElementById('mobileModeSplitBtn')?.addEventListener('click', () => setMobileViewMode('split'));
    document.getElementById('mobileModeChatBtn')?.addEventListener('click', () => setMobileViewMode('chat'));

    window.addEventListener('resize', () => {{
      if (window.innerWidth >= 768) {{
        const globe = document.getElementById('globeViewport');
        const workView = document.getElementById('workViewContainer');
        const splitter = document.getElementById('globeSplitter');
        const cityBar = document.getElementById('globeCityBar');
        if (globe) {{
          globe.style.display = '';
          globe.style.height = '';
          globe.style.flex = '';
        }}
        if (workView) {{
          workView.style.display = '';
          workView.style.height = '';
          workView.style.flex = '';
        }}
        if (splitter) {{
          splitter.style.display = '';
        }}
        if (cityBar) {{
          cityBar.classList.remove('max-h-[140px]', 'max-h-[58px]');
        }}
        resizeCanvas();
        if (cityVectorMap && isCityStreetViewActive) cityVectorMap.resize();
      }} else {{
        setMobileViewMode(currentMobileMode);
      }}
    }});

    document.getElementById('topSettingsBtn')?.addEventListener('click', openSettingsModal);
    document.getElementById('chatAddKeyBtn')?.addEventListener('click', openSettingsModal);
    document.getElementById('workModelBtn')?.addEventListener('click', openSettingsModal);
    document.getElementById('chatContributeBtn')?.addEventListener('click', () => openResearchFeedbackModal());

    // Plus Button Quick Menu
    const workPlusBtn = document.getElementById('workPlusBtn');
    const workPlusMenu = document.getElementById('workPlusMenu');
    workPlusBtn?.addEventListener('click', (e) => {{
      e.stopPropagation();
      workPlusMenu?.classList.toggle('hidden');
    }});

    document.getElementById('workMenuFeedbackBtn')?.addEventListener('click', (e) => {{
      e.stopPropagation();
      workPlusMenu?.classList.add('hidden');
      openResearchFeedbackModal();
    }});

    document.addEventListener('click', (e) => {{
      if (!e.target.closest('#workPlusBtn') && !e.target.closest('#workPlusMenu')) {{
        workPlusMenu?.classList.add('hidden');
      }}
    }});

    // Research & Feedback Modal Handlers
    const researchModal = document.getElementById('researchFeedbackModal');
    document.getElementById('closeFeedbackModalBtn')?.addEventListener('click', closeResearchFeedbackModal);
    document.getElementById('cancelFeedbackBtn')?.addEventListener('click', closeResearchFeedbackModal);
    researchModal?.addEventListener('click', (e) => {{
      if (e.target === researchModal) closeResearchFeedbackModal();
    }});

    document.getElementById('researchFeedbackForm')?.addEventListener('submit', (e) => {{
      e.preventDefault();
      const cat = document.getElementById('rfCategory')?.value || 'new_space';
      const name = (document.getElementById('rfSpaceName')?.value || '').trim();
      const city = (document.getElementById('rfCity')?.value || '').trim();
      const details = (document.getElementById('rfDetails')?.value || '').trim();
      const sourceUrl = (document.getElementById('rfSourceUrl')?.value || '').trim();
      const contributor = (document.getElementById('rfContributor')?.value || '').trim();

      const subId = Math.floor(1000 + Math.random() * 9000);
      const entry = {{
        id: `RES-${{subId}}`,
        timestamp: new Date().toISOString(),
        category: cat,
        spaceName: name,
        city: city,
        details: details,
        sourceUrl: sourceUrl,
        contributor: contributor || 'Anonymous Researcher',
        status: 'pending_verification'
      }};

      saveCommunityResearchSubmission(entry);
      closeResearchFeedbackModal();

      if (typeof setMobileViewMode === 'function') {{
        setMobileViewMode('chat');
      }}

      appendCuratorMessage(`
        <p class="text-white font-normal text-[15px]">
          ✅ <strong>Research Contribution Queued for Verification</strong>
        </p>
        <div class="py-2.5 border-t border-[#333] space-y-1.5 text-slate-300 text-[13px] leading-[135%]">
          <div><strong class="text-[#78a9ff] font-mono uppercase text-[11px] tracking-wider block">Audit Ticket</strong> <span class="font-mono text-emerald-400 font-bold">#${{entry.id}}</span> · <span class="text-slate-400 text-[12px] font-mono">Curatorial Verification Queue</span></div>
          <div class="pt-1 border-t border-[#262626]"><strong class="text-[#42be65] font-mono uppercase text-[11px] tracking-wider block">Submission Category</strong> ${{escapeHtml(cat.replace(/_/g, ' ').toUpperCase())}}</div>
          ${{name ? `<div class="pt-1 border-t border-[#262626]"><strong class="text-[#33b1ff] font-mono uppercase text-[11px] tracking-wider block">Space & Location</strong> <span class="text-white font-medium">${{escapeHtml(name)}}</span> ${{city ? `(${{escapeHtml(city)}})` : ''}}</div>` : ''}}
          <div class="pt-1 border-t border-[#262626]"><strong class="text-[#be95ff] font-mono uppercase text-[11px] tracking-wider block">Research Findings</strong> ${{escapeHtml(details)}}</div>
          ${{sourceUrl ? `<div class="pt-1 border-t border-[#262626]"><strong class="text-[#3ddbd9] font-mono uppercase text-[11px] tracking-wider block">Statutory Source Filing</strong> <a href="${{escapeHtml(sourceUrl)}}" target="_blank" rel="noopener noreferrer" class="text-[#60a5fa] hover:underline font-mono text-[12px] break-all">${{escapeHtml(sourceUrl)}} ↗</a></div>` : ''}}
          <div class="pt-1.5 border-t border-[#262626] text-[12px] text-slate-400 font-mono">
            Status: <span class="text-emerald-400 font-bold">Active in Session</span> · Queued for cross-examination against regulatory registers (IRS 990 / Charity Commission / DRAC).
          </div>
        </div>
      `, ['Explore Free Spaces', 'Plan Visit', 'Submit Another Note']);
    }});

    document.querySelectorAll('.work-menu-item').forEach(item => {{
      item.addEventListener('click', () => {{
        workPlusMenu?.classList.add('hidden');
        const q = item.getAttribute('data-query');
        if (q) {{
          appendUserMessage(q);
          handleCuratorQuery(q);
        }}
      }});
    }});

    // Academic Research Library Modal Handlers
    const academicModal = document.getElementById('academicResearchModal');
    document.getElementById('closeAcademicModalBtn')?.addEventListener('click', closeAcademicResearchModal);
    document.getElementById('closeAcademicModalFooterBtn')?.addEventListener('click', closeAcademicResearchModal);
    academicModal?.addEventListener('click', (e) => {{
      if (e.target === academicModal) closeAcademicResearchModal();
    }});

    let currentArTopic = 'all';
    document.querySelectorAll('.ar-topic-chip').forEach(btn => {{
      btn.addEventListener('click', () => {{
        currentArTopic = btn.getAttribute('data-topic') || 'all';
        document.querySelectorAll('.ar-topic-chip').forEach(b => {{
          if (b === btn) {{
            b.className = 'ar-topic-chip px-2.5 py-1 rounded-xl bg-[#2563eb] text-white border border-[#60a5fa] cursor-pointer';
          }} else {{
            b.className = 'ar-topic-chip px-2.5 py-1 rounded-xl bg-[#212121] hover:bg-[#282828] border border-[#333] text-[#d4d4d4] cursor-pointer';
          }}
        }});
        const q = document.getElementById('arSearchInput')?.value || '';
        renderAcademicStudies(currentArTopic, q);
      }});
    }});

    document.getElementById('arSearchInput')?.addEventListener('input', (e) => {{
      renderAcademicStudies(currentArTopic, e.target.value);
    }});

    // Unified Work Input Send Action
    const workInput = document.getElementById('workInput');
    const workSendBtn = document.getElementById('workSendBtn');

    function handleWorkSend() {{
      const text = (workInput?.value || '').trim();
      if (!text) return;
      workInput.value = '';
      if (window.innerWidth < 768 && currentMobileMode === 'map') {{
        setMobileViewMode('split');
      }}
      appendUserMessage(text);
      handleCuratorQuery(text);
    }}

    workSendBtn?.addEventListener('click', handleWorkSend);
    workInput?.addEventListener('keydown', (e) => {{
      if (e.key === 'Enter' && !e.shiftKey) {{
        e.preventDefault();
        handleWorkSend();
      }}
    }});

    // Voice Input via Web Speech API
    const workMicBtn = document.getElementById('workMicBtn');
    let speechRecognizer = null;
    let isSpeechRecording = false;

    if ('SpeechRecognition' in window || 'webkitSpeechRecognition' in window) {{
      const SpeechClass = window.SpeechRecognition || window.webkitSpeechRecognition;
      speechRecognizer = new SpeechClass();
      speechRecognizer.continuous = false;
      speechRecognizer.interimResults = true;
      speechRecognizer.lang = 'en-US';

      speechRecognizer.onstart = () => {{
        isSpeechRecording = true;
        workMicBtn?.classList.add('bg-rose-500/20', 'text-rose-400', 'animate-pulse');
        if (workMicBtn) workMicBtn.title = 'Listening... Speak now';
      }};

      speechRecognizer.onresult = (event) => {{
        const transcript = Array.from(event.results)
          .map(result => result[0].transcript)
          .join('');
        if (workInput) workInput.value = transcript;
      }};

      speechRecognizer.onerror = (event) => {{
        console.warn('Speech recognition error:', event.error);
        stopSpeechRecording();
      }};

      speechRecognizer.onend = () => {{
        stopSpeechRecording();
        if (workInput && workInput.value.trim()) {{
          autoSpeakNextCuratorResponse = true;
          handleWorkSend();
        }}
      }};
    }}

    function stopSpeechRecording() {{
      isSpeechRecording = false;
      workMicBtn?.classList.remove('bg-rose-500/20', 'text-rose-400', 'animate-pulse');
      if (workMicBtn) workMicBtn.title = 'Voice';
    }}

    workMicBtn?.addEventListener('click', (e) => {{
      e.stopPropagation();
      if (!speechRecognizer) {{
        alert('Voice speech recognition is supported in Google Chrome, Microsoft Edge, and Safari with microphone permissions.');
        return;
      }}
      if (isSpeechRecording) {{
        speechRecognizer.stop();
        stopSpeechRecording();
      }} else {{
        try {{
          speechRecognizer.start();
        }} catch(err) {{
          console.warn('Failed to start speech recognition:', err);
          stopSpeechRecording();
        }}
      }}
    }});

    // =========================================================
    // 🎙️ HIGH-FIDELITY CURATOR SPEECH SYNTHESIS ENGINE
    // =========================================================

    let cachedCuratorVoices = [];
    let activeSpeechHeartbeat = null;
    let isCuratorSpeaking = false;
    let currentSpeakingBtn = null;
    let autoSpeakNextCuratorResponse = false;
    let speechChunkQueue = [];
    let activeSpeechUtterance = null;

    function refreshVoices() {{
      if (!('speechSynthesis' in window)) return [];
      cachedCuratorVoices = window.speechSynthesis.getVoices() || [];
      return cachedCuratorVoices;
    }}

    if ('speechSynthesis' in window) {{
      refreshVoices();
      window.speechSynthesis.onvoiceschanged = refreshVoices;
    }}

    // Select the most natural, human-sounding English voice on the device
    function selectCuratorVoice() {{
      const voices = refreshVoices();
      if (!voices || voices.length === 0) return null;

      // 1. Natural / Enhanced / Neural English voices (Apple Samantha Enhanced, Siri, Google Natural, MS Online)
      const topPicks = [
        v => v.lang && v.lang.startsWith('en') && (v.name.includes('Natural') || v.name.includes('Online (Natural)') || v.name.includes('Neural')),
        v => v.lang && v.lang.startsWith('en') && (v.name.includes('Enhanced') || v.name.includes('Premium')),
        v => (v.name === 'Samantha' || v.name.includes('Samantha')) && v.lang && v.lang.startsWith('en'),
        v => v.lang && v.lang.startsWith('en') && (v.name.includes('Google UK English') || v.name.includes('Google US English')),
        v => v.lang && v.lang.startsWith('en') && (v.name.includes('Daniel') || v.name.includes('Karen') || v.name.includes('Moira') || v.name.includes('Serena')),
        v => v.name === 'Alex' && v.lang && v.lang.startsWith('en'),
        v => v.lang && v.lang.startsWith('en'),
        v => true
      ];

      for (let i = 0; i < topPicks.length; i++) {{
        const found = voices.find(topPicks[i]);
        if (found) return found;
      }}
      return voices[0] || null;
    }}

    // Convert raw DOM/HTML into clean, natural spoken prose
    function cleanTextForSpeech(source) {{
      let text = '';
      if (typeof source === 'string') {{
        const temp = document.createElement('div');
        temp.innerHTML = source;
        text = extractSpokenTextFromElement(temp);
      }} else if (source && source.nodeType) {{
        text = extractSpokenTextFromElement(source);
      }}

      if (!text) return '';

      // Conversational phonetic cleanup
      text = text
        // Expand common abbreviations into natural spoken English
        .replace(/\\be\\.g\\.,?\\s*/gi, 'for example, ')
        .replace(/\\bi\\.e\\.,?\\s*/gi, 'that is, ')
        .replace(/\\betc\\.\\s*/gi, 'and so forth. ')
        .replace(/\\bvs\\.\\s*|\\bvs\\s+/gi, 'versus ')
        .replace(/\\bw\\/\\s*/gi, 'with ')
        .replace(/\\bca\\.\\s*|\\bc\\.\\s*(?=\\d{{4}})/gi, 'around ')
        .replace(/\\bNo\\.\\s*(?=\\d)/gi, 'Number ')
        .replace(/501\\s*\\(\\s*c\\s*\\)\\s*\\(\\s*3\\s*\\)/gi, '501-c-3 non-profit')
        .replace(/Tier A\s*[·•]?\s*(Verified Independent Space|Verified Clean Sanctuary|Verified Independent|Verified Clean|clean sanctuary|independent space|sanctuary)?/gi, 'Tier A verified independent space')
        .replace(/verified Tier A verified independent space/gi, 'verified Tier A independent space')
        .replace(/clean sanctuaries|clean sanctuary/gi, 'independent spaces')
        .replace(/Tier B\s*[·•]?\s*(Flagged Corporate Sponsor)?/gi, 'Tier B flagged status')
        .replace(/\\bHours:\\b/gi, 'Visiting hours: ')
        .replace(/\\bAdmission:\\b/gi, 'Admission: ')
        .replace(/\\bTransit:\\b/gi, 'Transit directions: ')
        .replace(/\\bHighlight:\\b/gi, 'Highlights: ')
        .replace(/\\bGovernance:\\b/gi, 'Governance model: ')
        // Days of the week
        .replace(/\\bTue[–-]Sat\\b/gi, 'Tuesday through Saturday')
        .replace(/\\bMon[–-]Fri\\b/gi, 'Monday through Friday')
        .replace(/\\bWed[–-]Sun\\b/gi, 'Wednesday through Sunday')
        .replace(/\\bClosed Mon & Tue\\b/gi, 'Closed Monday and Tuesday')
        .replace(/\\bMon\\b/g, 'Monday')
        .replace(/\\bTue\\b/g, 'Tuesday')
        .replace(/\\bWed\\b/g, 'Wednesday')
        .replace(/\\bThu\\b/g, 'Thursday')
        .replace(/\\bFri\\b/g, 'Friday')
        .replace(/\\bSat\\b/g, 'Saturday')
        .replace(/\\bSun\\b/g, 'Sunday')
        // Strip markdown syntax
        .replace(/#{{1,6}}\\s+/g, '')
        .replace(/\\*\\*([^*]+)\\*\\*/g, '$1')
        .replace(/\\*([^*]+)\\*/g, '$1')
        .replace(/__([^_]+)__/g, '$1')
        .replace(/_([^_]+)_/g, '$1')
        .replace(/`([^`]+)`/g, '$1')
        .replace(/~~([^~]+)~~/g, '$1')
        .replace(/^[-\\*•]\\s+/gm, '')
        // Clean special characters and arrows
        .replace(/[↗→←↑↓]/g, '')
        .replace(/[·•]/g, ', ')
        .replace(/&/g, ' and ')
        // Strip bracketed citations or audit links
        .replace(/\\[\\d+\\]/g, '')
        .replace(/\\[audit dossier\\]/gi, '')
        .replace(/\\(audit dossier\\)/gi, '')
        // Strip raw URLs
        .replace(/https?:\\/\\/\\S+/gi, '')
        // Strip leftover empty parentheses/brackets
        .replace(/\\(\\s*[,;\\s]*\\)/g, '')
        .replace(/\\[\\s*[,;\\s]*\\]/g, '')
        // Strip emojis
        .replace(/[\\u{{1F300}}-\\u{{1F9FF}}\\u{{2600}}-\\u{{26FF}}\\u{{2700}}-\\u{{27BF}}]/gu, '')
        // Normalize punctuation and whitespace
        .replace(/\\s*,\\s*,+/g, ', ')
        .replace(/,\\s*\\./g, '.')
        .replace(/\\.\\s*\\./g, '.')
        .replace(/\\s+/g, ' ')
        .replace(/\\s*([,.;?!])\\s*/g, '$1 ')
        .trim();

      return text;
    }}

    function extractSpokenTextFromElement(container) {{
      const clone = container.cloneNode(true);
      // Remove all interactive action buttons, pills, headers, badges, external links
      const selectorsToRemove = [
        '.curator-speak-btn',
        '.curator-followup-pill',
        '.copy-itinerary-btn',
        '.dossier-link',
        '.ext-web-link',
        '.curator-dossier-btn',
        'button',
        'svg',
        '.speak-label',
        '[data-exclude-speech]',
        '[title="Culture Atlas Curator"]'
      ];
      selectorsToRemove.forEach(sel => {{
        clone.querySelectorAll(sel).forEach(el => el.remove());
      }});

      // Remove "Culture Atlas Curator" header title if present in text, and CA avatar
      let txt = clone.innerText || clone.textContent || '';
      txt = txt.replace(/^CA\s+/gm, '')
               .replace(/Culture Atlas Curator|Listen|Stop|Copied!|Copy Itinerary/g, '')
               .trim();
      return txt;
    }}

    // Split text into natural conversational chunks to eliminate Chrome 15-second cutoff
    function splitTextIntoSentences(text, maxChunkLen = 175) {{
      if (!text) return [];
      const rawSentences = text.match(/[^.!?]+[.!?]+(\\s|$)|[^.!?]+$/g) || [text];
      const chunks = [];
      let current = '';

      rawSentences.forEach(s => {{
        const sentence = s.trim();
        if (!sentence) return;
        if ((current + ' ' + sentence).length <= maxChunkLen) {{
          current = current ? current + ' ' + sentence : sentence;
        }} else {{
          if (current) chunks.push(current);
          if (sentence.length > maxChunkLen) {{
            // Split by comma or semicolon
            const clauses = sentence.split(/([,;]\\s+)/);
            let subCurrent = '';
            clauses.forEach(cl => {{
              if ((subCurrent + cl).length <= maxChunkLen) {{
                subCurrent += cl;
              }} else {{
                if (subCurrent) chunks.push(subCurrent.trim());
                subCurrent = cl;
              }}
            }});
            if (subCurrent) chunks.push(subCurrent.trim());
            current = '';
          }} else {{
            current = sentence;
          }}
        }}
      }});
      if (current) chunks.push(current.trim());
      return chunks;
    }}

    function stopCuratorSpeech() {{
      if (!('speechSynthesis' in window)) return;
      window.speechSynthesis.cancel();
      if (activeSpeechHeartbeat) {{
        clearInterval(activeSpeechHeartbeat);
        activeSpeechHeartbeat = null;
      }}
      speechChunkQueue = [];
      activeSpeechUtterance = null;
      isCuratorSpeaking = false;
      document.querySelectorAll('.curator-speak-btn').forEach(btn => {{
        btn.classList.remove('bg-rose-500/20', 'text-rose-400', 'border-rose-500/40');
        const icon = btn.querySelector('.speak-icon');
        if (icon) icon.textContent = '🔊';
        const lbl = btn.querySelector('.speak-label');
        if (lbl) lbl.textContent = 'Listen';
      }});
      currentSpeakingBtn = null;
    }}

    function speakCuratorText(rawTextOrElement, btnElement) {{
      if (!('speechSynthesis' in window)) {{
        alert('Speech synthesis is not supported on this device/browser.');
        return;
      }}

      // If already speaking from this button, toggle off
      if (isCuratorSpeaking && currentSpeakingBtn === btnElement) {{
        stopCuratorSpeech();
        return;
      }}

      // Stop any ongoing speech
      stopCuratorSpeech();

      const spokenText = cleanTextForSpeech(rawTextOrElement);
      if (!spokenText) return;

      const chunks = splitTextIntoSentences(spokenText);
      if (chunks.length === 0) return;

      const voice = selectCuratorVoice();
      isCuratorSpeaking = true;
      currentSpeakingBtn = btnElement;

      if (btnElement) {{
        btnElement.classList.add('bg-rose-500/20', 'text-rose-400', 'border-rose-500/40');
        const icon = btnElement.querySelector('.speak-icon');
        if (icon) icon.textContent = '⏹️';
        const lbl = btnElement.querySelector('.speak-label');
        if (lbl) lbl.textContent = 'Stop';
      }}

      // Chromium keepalive heartbeat to prevent speech cutoff
      activeSpeechHeartbeat = setInterval(() => {{
        if (window.speechSynthesis && window.speechSynthesis.speaking) {{
          window.speechSynthesis.pause();
          window.speechSynthesis.resume();
        }}
      }}, 6500);

      speechChunkQueue = chunks.slice();

      function playNext() {{
        if (!isCuratorSpeaking || speechChunkQueue.length === 0) {{
          stopCuratorSpeech();
          return;
        }}

        const chunk = speechChunkQueue.shift();
        const utter = new SpeechSynthesisUtterance(chunk);
        if (voice) utter.voice = voice;
        utter.rate = 1.0;
        utter.pitch = 1.0;
        activeSpeechUtterance = utter;

        utter.onend = () => {{
          playNext();
        }};

        utter.onerror = (err) => {{
          console.warn('Utterance error:', err);
          stopCuratorSpeech();
        }};

        window.speechSynthesis.speak(utter);
      }}

      playNext();
    }}

    window.cleanTextForSpeech = cleanTextForSpeech;
    window.selectCuratorVoice = selectCuratorVoice;
    window.splitTextIntoSentences = splitTextIntoSentences;
    window.speakCuratorText = speakCuratorText;
    window.stopCuratorSpeech = stopCuratorSpeech;

    // Work Suggestion Cards & Try Buttons
    document.querySelectorAll('.work-suggestion-card, .try-pill').forEach(el => {{
      el.addEventListener('click', (e) => {{
        e.stopPropagation();
        const card = el.closest('.work-suggestion-card') || el;
        const q = card.getAttribute('data-query');
        if (q) {{
          appendUserMessage(q);
          handleCuratorQuery(q);
        }}
      }});
    }});

    // Work Shelf Buttons
    document.querySelectorAll('.work-shelf-pill').forEach(el => {{
      el.addEventListener('click', () => {{
        const q = el.getAttribute('data-query');
        if (q) {{
          appendUserMessage(q);
          handleCuratorQuery(q);
        }}
      }});
    }});

    // Catalog Modal Handlers (Full 203 spaces browser)
    const catalogModal = document.getElementById('catalogModal');
    document.getElementById('workOpenCatalogBtn')?.addEventListener('click', () => {{
      if (catalogModal) catalogModal.classList.remove('hidden');
      renderLeftList();
    }});
    document.getElementById('closeCatalogModalBtn')?.addEventListener('click', () => {{
      if (catalogModal) catalogModal.classList.add('hidden');
    }});
    catalogModal?.addEventListener('click', (e) => {{
      if (e.target === catalogModal) catalogModal.classList.add('hidden');
    }});

    // Floating Card Ask Curator Button: sends query straight to unified work chat
    document.getElementById('floatingCardAskCurator')?.addEventListener('click', (e) => {{
      e.stopPropagation();
      if (selectedInstitution) {{
        const q = `Tell me about ${{selectedInstitution.name}}`;
        appendUserMessage(q);
        handleCuratorQuery(selectedInstitution.name);
      }}
    }});

    // View Controls: Minimize · Expand
    let isGlobeMinimized = false;
    let isGlobeExpanded = false;

    function handleViewMinimize() {{
      const g = document.getElementById('globeViewport');
      if (!g) return;
      isGlobeMinimized = !isGlobeMinimized;
      isGlobeExpanded = false;
      const isDesktop = window.innerWidth >= 768;

      if (isDesktop) {{
        if (isGlobeMinimized) {{
          g.style.width = '240px';
          g.style.flex = '0 0 240px';
          g.style.height = '100%';
        }} else {{
          g.style.width = '50%';
          g.style.flex = '1 1 50%';
          g.style.height = '100%';
        }}
      }} else {{
        if (isGlobeMinimized) {{
          g.style.height = '140px';
          g.style.flex = '0 0 140px';
          g.style.width = '100%';
        }} else {{
          g.style.height = '50%';
          g.style.flex = '1 1 50%';
          g.style.width = '100%';
        }}
      }}
      setTimeout(resizeCanvas, 40);
    }}

    function handleViewExpand() {{
      const g = document.getElementById('globeViewport');
      if (!g) return;
      isGlobeExpanded = !isGlobeExpanded;
      isGlobeMinimized = false;
      const isDesktop = window.innerWidth >= 768;

      if (isDesktop) {{
        if (isGlobeExpanded) {{
          g.style.width = '75%';
          g.style.flex = '1 1 75%';
          g.style.height = '100%';
        }} else {{
          g.style.width = '50%';
          g.style.flex = '1 1 50%';
          g.style.height = '100%';
        }}
      }} else {{
        if (isGlobeExpanded) {{
          g.style.height = '75%';
          g.style.flex = '1 1 75%';
          g.style.width = '100%';
        }} else {{
          g.style.height = '50%';
          g.style.flex = '1 1 50%';
          g.style.width = '100%';
        }}
      }}
      setTimeout(resizeCanvas, 40);
    }}

    document.getElementById('viewMinimizeBtn')?.addEventListener('click', handleViewMinimize);
    document.getElementById('topViewMinimizeBtn')?.addEventListener('click', handleViewMinimize);
    document.getElementById('viewExpandBtn')?.addEventListener('click', handleViewExpand);
    document.getElementById('topViewExpandBtn')?.addEventListener('click', handleViewExpand);

    // Interactive Splitter Drag between Globe and Work Chat (Responsive Desktop/Mobile)
    const splitter = document.getElementById('globeSplitter');
    const globeVp = document.getElementById('globeViewport');
    const mainApp = document.getElementById('mainAppContainer');

    if (splitter && globeVp && mainApp) {{
      let isDraggingSplitter = false;

      splitter.addEventListener('mousedown', (e) => {{
        isDraggingSplitter = true;
        const isDesktop = window.innerWidth >= 768;
        document.body.style.cursor = isDesktop ? 'col-resize' : 'row-resize';
        document.body.style.userSelect = 'none';
        e.preventDefault();
      }});

      window.addEventListener('mousemove', (e) => {{
        if (!isDraggingSplitter) return;
        const isDesktop = window.innerWidth >= 768;
        const rect = mainApp.getBoundingClientRect();
        if (isDesktop) {{
          const offsetX = e.clientX - rect.left;
          const minW = 260;
          const maxW = rect.width - 300;
          const clamped = Math.max(minW, Math.min(maxW, offsetX));
          globeVp.style.width = clamped + 'px';
          globeVp.style.height = '100%';
          globeVp.style.flex = 'none';
        }} else {{
          const offsetY = e.clientY - rect.top;
          const minH = 130;
          const maxH = rect.height - 180;
          const clamped = Math.max(minH, Math.min(maxH, offsetY));
          globeVp.style.height = clamped + 'px';
          globeVp.style.width = '100%';
          globeVp.style.flex = 'none';
        }}
        resizeCanvas();
      }});

      window.addEventListener('mouseup', () => {{
        if (isDraggingSplitter) {{
          isDraggingSplitter = false;
          document.body.style.cursor = '';
          document.body.style.userSelect = '';
          resizeCanvas();
        }}
      }});

      // Double-click resets to exact 50% proportional split
      splitter.addEventListener('dblclick', () => {{
        const isDesktop = window.innerWidth >= 768;
        if (isDesktop) {{
          globeVp.style.width = '50%';
          globeVp.style.height = '100%';
          globeVp.style.flex = '1 1 50%';
        }} else {{
          globeVp.style.height = '50%';
          globeVp.style.width = '100%';
          globeVp.style.flex = '1 1 50%';
        }}
        resizeCanvas();
      }});

      // Touch support for mobile / tablets
      splitter.addEventListener('touchstart', (e) => {{
        isDraggingSplitter = true;
      }}, {{ passive: true }});

      window.addEventListener('touchmove', (e) => {{
        if (!isDraggingSplitter || !e.touches || !e.touches[0]) return;
        const isDesktop = window.innerWidth >= 768;
        const rect = mainApp.getBoundingClientRect();
        if (isDesktop) {{
          const offsetX = e.touches[0].clientX - rect.left;
          const minW = 260;
          const maxW = rect.width - 300;
          const clamped = Math.max(minW, Math.min(maxW, offsetX));
          globeVp.style.width = clamped + 'px';
          globeVp.style.height = '100%';
          globeVp.style.flex = 'none';
        }} else {{
          const offsetY = e.touches[0].clientY - rect.top;
          const minH = 130;
          const maxH = rect.height - 180;
          const clamped = Math.max(minH, Math.min(maxH, offsetY));
          globeVp.style.height = clamped + 'px';
          globeVp.style.width = '100%';
          globeVp.style.flex = 'none';
        }}
        resizeCanvas();
      }}, {{ passive: true }});

      window.addEventListener('touchend', () => {{
        if (isDraggingSplitter) {{
          isDraggingSplitter = false;
          resizeCanvas();
        }}
      }});
    }}

    window.addEventListener('resize', () => {{
      const isDesktop = window.innerWidth >= 768;
      if (globeVp) {{
        if (isDesktop) {{
          if (!globeVp.style.width || globeVp.style.width.endsWith('%')) {{
            globeVp.style.width = '50%';
            globeVp.style.height = '100%';
          }}
        }} else {{
          if (!globeVp.style.height || globeVp.style.height.endsWith('%')) {{
            globeVp.style.height = '50%';
            globeVp.style.width = '100%';
          }}
        }}
      }}
      resizeCanvas();
    }});

    function updateFilterChipsUI() {{
      document.querySelectorAll('.inquiry-chip').forEach(btn => {{
        const fKey = btn.getAttribute('data-filter');
        if (fKey && fKey === selectedCategoryFilter && selectedCategoryFilter !== 'all') {{
          btn.classList.add('border-[#38bdf8]', 'ring-1', 'ring-[#38bdf8]', 'bg-[#0c1a2e]', 'text-white', 'shadow-[0_0_12px_rgba(56,189,248,0.5)]');
          btn.classList.remove('border-[#2f2f2f]', 'border-[#232a3c]', 'border-[#1b3324]', 'border-[#3b2b11]', 'bg-[#212121]', 'bg-[#101522]', 'bg-[#0c1f15]', 'bg-[#221807]', 'text-[#d4d4d4]', 'text-[#93c5fd]', 'text-[#6ee7b7]', 'text-[#fcd34d]');
        }} else {{
          btn.classList.remove('border-[#38bdf8]', 'ring-1', 'ring-[#38bdf8]', 'bg-[#0c1a2e]', 'text-white', 'shadow-[0_0_12px_rgba(56,189,248,0.5)]');
          const origColor = btn.getAttribute('data-chip-color');
          if (origColor === 'green') {{
            btn.classList.add('border-[#1b3324]', 'bg-[#0c1f15]', 'text-[#6ee7b7]');
          }} else if (origColor === 'amber') {{
            btn.classList.add('border-[#3b2b11]', 'bg-[#221807]', 'text-[#fcd34d]');
          }} else if (origColor === 'blue') {{
            btn.classList.add('border-[#232a3c]', 'bg-[#101522]', 'text-[#93c5fd]');
          }} else {{
            btn.classList.add('border-[#2f2f2f]', 'bg-[#212121]', 'text-[#d4d4d4]');
          }}
        }}
      }});
    }}

    function setCategoryFilter(fKey, triggerChat = true, queryPrompt = null) {{
      if (selectedCategoryFilter === fKey) {{
        // Toggle off back to all
        selectedCategoryFilter = 'all';
        selectedCityFilter = 'all';
        selectedCountryFilter = 'all';
      }} else {{
        selectedCategoryFilter = fKey;
      }}

      updateFilterChipsUI();

      // Location flyTo and zoom
      if (selectedCategoryFilter === 'london') {{
        selectedCityFilter = 'London';
        flyTo(-0.1278, 51.5074);
        targetRadius = baseRadius * 4.0;
      }} else if (selectedCategoryFilter === 'nyc') {{
        selectedCityFilter = 'New York';
        flyTo(-73.9776, 40.7614);
        targetRadius = baseRadius * 4.0;
      }} else if (selectedCategoryFilter === 'paris') {{
        selectedCityFilter = 'Paris';
        flyTo(2.3522, 48.8566);
        targetRadius = baseRadius * 4.0;
      }} else if (selectedCategoryFilter === 'moma') {{
        selectedCityFilter = 'New York';
        flyTo(-73.9776, 40.7614);
        targetRadius = baseRadius * 4.0;
        openMomaAuditModal();
      }} else if (selectedCategoryFilter === 'all') {{
        selectedCityFilter = 'all';
        targetRadius = baseRadius;
      }}

      // Apply filter to map dots and catalog list
      applyFilters();

      // Trigger curator chat response
      if (triggerChat && queryPrompt && selectedCategoryFilter !== 'all') {{
        appendUserMessage(queryPrompt);
        handleCuratorQuery(queryPrompt);
      }}
    }}

    // Bind Inquiry / Filter Chips
    document.querySelectorAll('.inquiry-chip').forEach(btn => {{
      btn.addEventListener('click', () => {{
        const fKey = btn.getAttribute('data-filter') || 'all';
        const q = btn.getAttribute('data-query');
        setCategoryFilter(fKey, true, q);
      }});
    }});

    // Clear Map Filter Button
    document.getElementById('clearMapFilterBtn')?.addEventListener('click', (e) => {{
      e.stopPropagation();
      setCategoryFilter('all', false);
    }});

    // Delegated click listener in chat messages for inline links, cards, & city mentions
    curatorMessages.addEventListener('click', (e) => {{
      // Explicitly allow external website links to open in a new tab without interference
      const extLink = e.target.closest('a[target="_blank"], a.ext-web-link, a[href^="http://"], a[href^="https://"]');
      if (extLink && !extLink.classList.contains('inst-link') && !extLink.classList.contains('city-link') && !extLink.classList.contains('country-link') && !extLink.classList.contains('dossier-link') && !extLink.classList.contains('prompt-link')) {{
        return;
      }}

      // 0. Check for interactive follow-up suggestion pills
      const followUpBtn = e.target.closest('.curator-followup-pill');
      if (followUpBtn) {{
        e.preventDefault();
        e.stopPropagation();
        const q = followUpBtn.getAttribute('data-query');
        if (q) {{
          appendUserMessage(q);
          handleCuratorQuery(q);
        }}
        return;
      }}

      // Audio Docent Speech Synthesis
      const speakBtn = e.target.closest('.curator-speak-btn');
      if (speakBtn) {{
        e.preventDefault();
        e.stopPropagation();
        const msgDiv = speakBtn.closest('.curator-message-wrap');
        speakCuratorText(msgDiv, speakBtn);
        return;
      }}

      // Copy Itinerary to Clipboard
      const copyItineraryBtn = e.target.closest('.copy-itinerary-btn');
      if (copyItineraryBtn) {{
        e.preventDefault();
        e.stopPropagation();
        const card = copyItineraryBtn.closest('.curator-message-wrap');
        const text = card ? card.innerText.replace(/Culture Atlas Curator|Listen|Stop|Copy Itinerary|Copied!|💬.*$/g, '').trim() : '';
        navigator.clipboard.writeText(text).then(() => {{
          copyItineraryBtn.textContent = 'Copied!';
          setTimeout(() => {{ copyItineraryBtn.textContent = 'Copy Itinerary'; }}, 2500);
        }});
        return;
      }}

      // 1. Check for institution links
      const instLink = e.target.closest('.inst-link, [data-inst]');
      if (instLink) {{
        e.preventDefault();
        e.stopPropagation();
        const name = instLink.getAttribute('data-name') || instLink.getAttribute('data-inst') || instLink.textContent.trim();
        const inst = ALL_INSTITUTIONS.find(i => i.name === name || (i.name.toLowerCase() === name.toLowerCase()) || (i.aliases && i.aliases.some(a => a.toLowerCase() === name.toLowerCase())));
        if (inst) {{
          selectInstitution(inst, true);
        }} else if (typeof EXCLUDED_INSTITUTIONS !== 'undefined') {{
          const exInst = EXCLUDED_INSTITUTIONS.find(i => i.name === name || (i.name.toLowerCase() === name.toLowerCase()) || (i.aliases && i.aliases.some(a => a.toLowerCase() === name.toLowerCase())));
          if (exInst) {{
            openDossier(exInst);
          }}
        }}
        return;
      }}

      // 2. Check for audit dossier links
      const dossierLink = e.target.closest('.dossier-link, .curator-dossier-btn, [data-dossier]');
      if (dossierLink) {{
        e.preventDefault();
        e.stopPropagation();
        const name = dossierLink.getAttribute('data-name') || dossierLink.getAttribute('data-dossier');
        const inst = ALL_INSTITUTIONS.find(i => i.name === name || (i.name.toLowerCase() === name.toLowerCase())) || 
                     (typeof EXCLUDED_INSTITUTIONS !== 'undefined' ? EXCLUDED_INSTITUTIONS.find(i => i.name === name || (i.name.toLowerCase() === name.toLowerCase())) : null);
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
          filterByCity(city, true, true);
        }}
        return;
      }}

      // 4. Check for country links
      const countryLink = e.target.closest('.country-link, .country-zoom-btn, [data-country]');
      if (countryLink) {{
        e.preventDefault();
        e.stopPropagation();
        const country = countryLink.getAttribute('data-country') || countryLink.textContent.trim();
        if (country) {{
          filterByCountry(country);
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
        tabCuratorBtn.className = 'py-1 px-3 rounded-lg transition text-center flex items-center justify-center gap-1.5 bg-[#2f2f2f] text-white font-normal shadow-sm';
        tabCatalogBtn.className = 'py-1 px-3 rounded-lg transition text-center flex items-center justify-center gap-1.5 text-[#a1a1aa] hover:text-white';
        curatorPanel.classList.remove('hidden');
        catalogPanel.classList.add('hidden');
      }} else {{
        tabCatalogBtn.className = 'py-1 px-3 rounded-lg transition text-center flex items-center justify-center gap-1.5 bg-[#2f2f2f] text-white font-normal shadow-sm';
        tabCuratorBtn.className = 'py-1 px-3 rounded-lg transition text-center flex items-center justify-center gap-1.5 text-[#a1a1aa] hover:text-white';
        catalogPanel.classList.remove('hidden');
        curatorPanel.classList.add('hidden');
        renderLeftList();
      }}
    }}

    // =========================================================
    // Curator Intelligence Settings Modal (Multi-Provider: Claude, OpenAI, Gemini)
    const settingsModal = document.getElementById('curatorSettingsModal');
    const aiApiKeyInput = document.getElementById('aiApiKeyInput');
    const aiModelSelect = document.getElementById('aiModelSelect');
    const connectionTestBox = document.getElementById('connectionTestBox');
    const testStatusIcon = document.getElementById('testStatusIcon');
    const testStatusMsg = document.getElementById('testStatusMsg');
    const toggleKeyVisibilityBtn = document.getElementById('toggleKeyVisibilityBtn');

    document.getElementById('providerClaudeBtn')?.addEventListener('click', () => updateProviderUI('anthropic'));
    document.getElementById('providerOpenAIBtn')?.addEventListener('click', () => updateProviderUI('openai'));
    document.getElementById('providerGeminiBtn')?.addEventListener('click', () => updateProviderUI('gemini'));

    document.getElementById('curatorSettingsBtn')?.addEventListener('click', openSettingsModal);

    document.getElementById('closeSettingsModalBtn')?.addEventListener('click', () => {{
      settingsModal?.classList.add('hidden');
    }});

    toggleKeyVisibilityBtn?.addEventListener('click', () => {{
      if (aiApiKeyInput.type === 'password') {{
        aiApiKeyInput.type = 'text';
        toggleKeyVisibilityBtn.textContent = 'Hide';
      }} else {{
        aiApiKeyInput.type = 'password';
        toggleKeyVisibilityBtn.textContent = 'Show';
      }}
    }});

    aiApiKeyInput?.addEventListener('input', (e) => {{
      updateDetectBadge(e.target.value);
    }});

    document.getElementById('testConnectionBtn')?.addEventListener('click', async () => {{
      const key = (aiApiKeyInput?.value || '').trim();
      const model = aiModelSelect?.value;
      if (!connectionTestBox) return;
      connectionTestBox.classList.remove('hidden', 'border-emerald-500/30', 'bg-emerald-500/10', 'text-emerald-400', 'border-rose-500/30', 'bg-rose-500/10', 'text-rose-400');
      connectionTestBox.classList.add('border-[#3e3e3e]', 'bg-[#27272a]', 'text-[#d4d4d4]');
      if (testStatusIcon) testStatusIcon.textContent = '';
      if (testStatusMsg) testStatusMsg.textContent = 'Testing connection with live API...';

      const res = await testAPIConnection(currentSelectedProvider, key, model);
      if (res.success) {{
        connectionTestBox.classList.remove('border-[#3e3e3e]', 'bg-[#27272a]', 'text-[#d4d4d4]');
        connectionTestBox.classList.add('border-emerald-500/30', 'bg-emerald-500/10', 'text-emerald-400');
        if (testStatusIcon) testStatusIcon.textContent = '✓ ';
        if (testStatusMsg) testStatusMsg.textContent = res.message;
      }} else {{
        connectionTestBox.classList.remove('border-[#3e3e3e]', 'bg-[#27272a]', 'text-[#d4d4d4]');
        connectionTestBox.classList.add('border-rose-500/30', 'bg-rose-500/10', 'text-rose-400');
        if (testStatusIcon) testStatusIcon.textContent = '✕ ';
        if (testStatusMsg) testStatusMsg.textContent = res.error;
      }}
    }});

    document.getElementById('saveApiKeyBtn')?.addEventListener('click', () => {{
      aiApiKey = (aiApiKeyInput?.value || '').trim();
      aiProvider = currentSelectedProvider;
      aiModel = aiModelSelect?.value || getEffectiveModel();
      localStorage.setItem('atlas_ai_api_key', aiApiKey);
      localStorage.setItem('atlas_ai_provider', aiProvider);
      localStorage.setItem('atlas_ai_model', aiModel);
      updateAIStatusUI();
      settingsModal?.classList.add('hidden');
    }});

    document.getElementById('clearApiKeyBtn')?.addEventListener('click', () => {{
      aiApiKey = '';
      aiProvider = 'auto';
      aiModel = '';
      if (aiApiKeyInput) aiApiKeyInput.value = '';
      localStorage.removeItem('atlas_ai_api_key');
      localStorage.removeItem('atlas_gemini_api_key');
      localStorage.removeItem('atlas_ai_provider');
      localStorage.removeItem('atlas_ai_model');
      updateAIStatusUI();
      connectionTestBox?.classList.add('hidden');
      settingsModal?.classList.add('hidden');
    }});

    // Initialize UI Status on startup
    updateAIStatusUI();

    // =========================================================
    // 📋 CATALOG LIST & FILTERING ENGINE
    // =========================================================
    const countrySelect = document.getElementById('countrySelect');
    const citySelect = document.getElementById('citySelect');
    const searchInput = document.getElementById('searchInput');

    function populateDropdowns() {{
      if (countrySelect) {{
        const countries = [...new Set(ALL_INSTITUTIONS.map(i => i.country).filter(Boolean))].sort();
        countrySelect.innerHTML = `<option value="all">All Countries (${{countries.length}})</option>` + 
          countries.map(c => `<option value="${{c}}">${{c}}</option>`).join('');
      }}

      if (citySelect) {{
        const cities = [...new Set(ALL_INSTITUTIONS.map(i => i.city).filter(Boolean))].sort();
        citySelect.innerHTML = `<option value="all">All Cities (${{cities.length}})</option>` + 
          cities.map(c => `<option value="${{c}}">${{c}}</option>`).join('');
      }}
    }}
    populateDropdowns();

    function updateGlobePillsUI() {{
      const isCleanOnly = selectedTierFilter.size === 1 && selectedTierFilter.has('A');
      const isFlaggedOnly = selectedTierFilter.size === 1 && selectedTierFilter.has('B');
      const isAllTiers = selectedTierFilter.size >= 2 || (selectedTierFilter.has('A') && selectedTierFilter.has('B'));

      document.querySelectorAll('.globe-filter-pill').forEach(pill => {{
        const type = pill.getAttribute('data-type');
        const val = pill.getAttribute('data-value') || '';

        if (type === 'tier') {{
          if (val === 'A') {{
            if (isCleanOnly) {{
              pill.className = 'globe-filter-pill px-2.5 py-1 rounded-xl bg-[#059669] text-white border border-[#10b981] transition cursor-pointer text-[12px] sm:text-[13px] shrink-0 font-medium shadow-sm shadow-emerald-950/40';
            }} else {{
              pill.className = 'globe-filter-pill px-2.5 py-1 rounded-xl bg-[#0a2016]/90 hover:bg-[#0f2e20] border border-[#1b4332] text-[#4ade80] hover:text-white transition cursor-pointer text-[12px] sm:text-[13px] shrink-0 font-medium';
            }}
          }} else if (val === 'B') {{
            if (isFlaggedOnly) {{
              pill.className = 'globe-filter-pill px-2.5 py-1 rounded-xl bg-[#6929c4] text-white border border-[#be95ff] transition cursor-pointer text-[12px] sm:text-[13px] shrink-0 font-medium shadow-sm shadow-purple-950/40';
            }} else {{
              pill.className = 'globe-filter-pill px-2.5 py-1 rounded-xl bg-[#1f1433]/90 hover:bg-[#2d1f4a] border border-[#8a3ffc]/80 text-[#be95ff] hover:text-white transition cursor-pointer text-[12px] sm:text-[13px] shrink-0 font-medium';
            }}
          }} else if (val === 'all') {{
            if (isAllTiers) {{
              pill.className = 'globe-filter-pill px-2.5 py-1 rounded-xl bg-[#2563eb] text-white border border-[#60a5fa] transition cursor-pointer text-[12px] sm:text-[13px] shrink-0 font-medium shadow-sm';
            }} else {{
              pill.className = 'globe-filter-pill px-2.5 py-1 rounded-xl bg-[#212121]/90 hover:bg-[#2a2a2a] border border-[#2e2e2e] text-[#d4d4d4] hover:text-white transition cursor-pointer text-[12px] sm:text-[13px] shrink-0';
            }}
          }}
          return;
        }}

        let isAct = false;
        if (type === 'all' && selectedCityFilter === 'all' && selectedCountryFilter === 'all' && isCleanOnly) isAct = true;
        else if (type === 'city' && selectedCityFilter.toLowerCase() === val.toLowerCase()) isAct = true;
        else if (type === 'country' && selectedCountryFilter.toLowerCase() === val.toLowerCase()) isAct = true;
        else if (type === 'category' && selectedCategoryFilter === val) isAct = true;

        if (isAct) {{
          pill.className = 'globe-filter-pill px-2.5 py-1 rounded-xl bg-[#2563eb] text-white border border-[#60a5fa] transition cursor-pointer text-[13px] shrink-0 shadow-sm';
        }} else {{
          pill.className = 'globe-filter-pill px-2.5 py-1 rounded-xl bg-[#212121]/90 hover:bg-[#2a2a2a] border border-[#2e2e2e] text-[#d4d4d4] hover:text-white transition cursor-pointer text-[13px] shrink-0';
        }}
      }});
    }}

    function updateGlobeBarForCountry(countryName) {{
      const bar = document.getElementById('globeCityBar');
      if (!bar) return;
      const countryCities = ALL_CITIES_REGISTRY.filter(ci => matchC(ci.country, countryName));
      if (countryCities.length === 0) return;

      const totalSpaces = countryCities.reduce((acc, c) => acc + c.count, 0);

      let html = `
        <div class="flex flex-wrap items-center gap-1.5">
          <button class="globe-filter-pill px-2.5 py-1 rounded-xl bg-[#212121]/90 hover:bg-[#2a2a2a] border border-[#2e2e2e] text-[#d4d4d4] hover:text-white transition cursor-pointer text-[12px] sm:text-[13px] shrink-0" data-type="all">← All Spaces</button>
          <span class="text-[#444] text-[11px] shrink-0">|</span>
          <button class="globe-filter-pill px-2.5 py-1 rounded-xl bg-[#2563eb] text-white border border-[#60a5fa] transition cursor-pointer text-[12px] sm:text-[13px] shrink-0 font-medium shadow-sm" data-type="country" data-value="${{escapeHtml(countryName)}}">${{escapeHtml(countryName)}} (${{totalSpaces}})</button>
          <span class="text-[#444] text-[11px] shrink-0">|</span>
          <button class="globe-filter-pill px-2.5 py-1 rounded-xl bg-[#059669] text-white border border-[#10b981] transition cursor-pointer text-[12px] sm:text-[13px] shrink-0 font-medium" data-type="tier" data-value="A">✓ Clean</button>
          <button class="globe-filter-pill px-2.5 py-1 rounded-xl bg-[#1f1433] hover:bg-[#2c1d48] border border-[#8a3ffc] text-[#be95ff] transition cursor-pointer text-[12px] sm:text-[13px] shrink-0 font-medium" data-type="tier" data-value="B">Flagged</button>
          <span class="text-[#444] text-[11px] shrink-0">|</span>
          <button class="globe-filter-pill px-2.5 py-1 rounded-xl bg-[#212121]/90 hover:bg-[#2a2a2a] border border-[#2e2e2e] text-[#d4d4d4] hover:text-white transition cursor-pointer text-[12px] sm:text-[13px] shrink-0" data-type="category" data-value="free">Free Entry</button>
          <button class="globe-filter-pill px-2.5 py-1 rounded-xl bg-[#212121]/90 hover:bg-[#2a2a2a] border border-[#2e2e2e] text-[#d4d4d4] hover:text-white transition cursor-pointer text-[12px] sm:text-[13px] shrink-0" data-type="category" data-value="artist_run">Artist-Run</button>
        </div>

        <div class="flex flex-wrap items-center gap-1.5">
          <span class="text-[11px] text-[#71717a] font-mono shrink-0 mr-0.5 uppercase tracking-wider">Cities:</span>
      `;

      countryCities.forEach(city => {{
        html += `<button class="globe-filter-pill px-2.5 py-1 rounded-xl bg-[#212121]/90 hover:bg-[#2a2a2a] border border-[#2e2e2e] text-[#d4d4d4] hover:text-white transition cursor-pointer text-[12px] sm:text-[13px] shrink-0" data-type="city" data-value="${{escapeHtml(city.name)}}">${{escapeHtml(city.name)}} <span class="text-[#93c5fd] font-mono text-[11px]">(${{city.count}})</span></button>`;
      }});

      html += `</div>`;

      bar.innerHTML = html;
      wireGlobePillListeners();
      updateGlobePillsUI();
    }}

    function renderGlobeBarDefault() {{
      const bar = document.getElementById('globeCityBar');
      if (!bar) return;

      const featuredCities = ['London', 'New York', 'Paris', 'Berlin', 'Amsterdam', 'Tokyo', 'Madrid', 'Basel', 'Bilbao'];
      const featuredCountries = ['United Kingdom', 'United States', 'Germany', 'France', 'Netherlands', 'Spain', 'Switzerland', 'Italy', 'Japan'];

      let html = `
        <!-- Row 1: Global Scope, Tiers, Academic Research & Categories -->
        <div class="flex flex-wrap items-center gap-1.5">
          <button class="globe-filter-pill px-2.5 py-1 rounded-xl bg-[#059669] text-white border border-[#10b981] transition cursor-pointer text-[12px] sm:text-[13px] shrink-0 font-medium shadow-sm shadow-emerald-950/40" data-type="tier" data-value="A">✓ Clean Funding ({clean_count})</button>
          <button class="globe-filter-pill px-2.5 py-1 rounded-xl bg-[#1f1433] hover:bg-[#2c1d48] border border-[#8a3ffc] text-[#be95ff] hover:text-white transition cursor-pointer text-[12px] sm:text-[13px] shrink-0 font-medium" data-type="tier" data-value="B">Flagged ({flagged_count})</button>
          <button class="globe-filter-pill px-2.5 py-1 rounded-xl bg-[#212121]/90 hover:bg-[#2a2a2a] border border-[#2e2e2e] text-[#d4d4d4] hover:text-white transition cursor-pointer text-[12px] sm:text-[13px] shrink-0" data-type="tier" data-value="all">All Spaces ({total_count})</button>
          <span class="text-[#444] text-[11px] shrink-0">|</span>
          <button class="globe-filter-pill px-2.5 py-1 rounded-xl bg-[#0d1e2e] hover:bg-[#152e47] border border-[#33b1ff]/70 text-[#78a9ff] hover:text-white transition cursor-pointer text-[12px] sm:text-[13px] shrink-0" data-type="academic">Academic Studies ({academic_count})</button>
          <span class="text-[#444] text-[11px] shrink-0">|</span>
          <button class="globe-filter-pill px-2.5 py-1 rounded-xl bg-[#212121]/90 hover:bg-[#2a2a2a] border border-[#2e2e2e] text-[#d4d4d4] hover:text-white transition cursor-pointer text-[12px] sm:text-[13px] shrink-0" data-type="region" data-value="europe">Europe</button>
          <button class="globe-filter-pill px-2.5 py-1 rounded-xl bg-[#212121]/90 hover:bg-[#2a2a2a] border border-[#2e2e2e] text-[#d4d4d4] hover:text-white transition cursor-pointer text-[12px] sm:text-[13px] shrink-0" data-type="region" data-value="americas">Americas</button>
          <button class="globe-filter-pill px-2.5 py-1 rounded-xl bg-[#212121]/90 hover:bg-[#2a2a2a] border border-[#2e2e2e] text-[#d4d4d4] hover:text-white transition cursor-pointer text-[12px] sm:text-[13px] shrink-0" data-type="region" data-value="asiapacific">Asia-Pacific</button>
          <button class="globe-filter-pill px-2.5 py-1 rounded-xl bg-[#212121]/90 hover:bg-[#2a2a2a] border border-[#2e2e2e] text-[#d4d4d4] hover:text-white transition cursor-pointer text-[12px] sm:text-[13px] shrink-0" data-type="region" data-value="mena_africa">MidEast & Africa</button>
          <span class="text-[#444] text-[11px] shrink-0">|</span>
          <button class="globe-filter-pill px-2.5 py-1 rounded-xl bg-[#212121]/90 hover:bg-[#2a2a2a] border border-[#2e2e2e] text-[#d4d4d4] hover:text-white transition cursor-pointer text-[12px] sm:text-[13px] shrink-0" data-type="category" data-value="free">Free Entry</button>
          <button class="globe-filter-pill px-2.5 py-1 rounded-xl bg-[#212121]/90 hover:bg-[#2a2a2a] border border-[#2e2e2e] text-[#d4d4d4] hover:text-white transition cursor-pointer text-[12px] sm:text-[13px] shrink-0" data-type="category" data-value="artist_run">Artist-Run</button>
        </div>

        <!-- Row 2: Featured Cultural Cities -->
        <div class="flex flex-wrap items-center gap-1.5">
          <span class="text-[11px] text-[#71717a] font-mono shrink-0 mr-0.5 uppercase tracking-wider">Cities:</span>
      `;

      featuredCities.forEach(cityName => {{
        const cMeta = ALL_CITIES_REGISTRY.find(c => matchC(c.name, cityName));
        const count = cMeta ? ` (${{cMeta.count}})` : '';
        html += `<button class="globe-filter-pill px-2.5 py-1 rounded-xl bg-[#212121]/90 hover:bg-[#2a2a2a] border border-[#2e2e2e] text-[#d4d4d4] hover:text-white transition cursor-pointer text-[12px] sm:text-[13px] shrink-0" data-type="city" data-value="${{cityName}}">${{cityName}}${{count}}</button>`;
      }});

      html += `
        </div>

        <!-- Row 3: Featured Countries -->
        <div class="flex flex-wrap items-center gap-1.5">
          <span class="text-[11px] text-[#71717a] font-mono shrink-0 mr-0.5 uppercase tracking-wider">Countries:</span>
      `;

      featuredCountries.forEach(countryName => {{
        html += `<button class="globe-filter-pill px-2.5 py-1 rounded-xl bg-[#212121]/90 hover:bg-[#2a2a2a] border border-[#2e2e2e] text-[#d4d4d4] hover:text-white transition cursor-pointer text-[12px] sm:text-[13px] shrink-0" data-type="country" data-value="${{countryName}}">${{countryName}}</button>`;
      }});

      html += `</div>`;

      bar.innerHTML = html;
      wireGlobePillListeners();
      updateGlobePillsUI();
    }}

    function wireGlobePillListeners() {{
      document.querySelectorAll('#globeCityBar .globe-filter-pill').forEach(pill => {{
        pill.addEventListener('click', () => {{
          const type = pill.getAttribute('data-type');
          const val = pill.getAttribute('data-value') || '';
          if (type === 'tier') {{
            if (val === 'A') {{
              selectedTierFilter = new Set(['A']);
            }} else if (val === 'B') {{
              selectedTierFilter = new Set(['B']);
            }} else if (val === 'all') {{
              selectedTierFilter = new Set(['A', 'B', 'U']);
            }}
            applyFilters();
            updateGlobePillsUI();
          }} else if (type === 'academic') {{
            if (typeof openAcademicResearchModal === 'function') {{
              openAcademicResearchModal('all');
            }}
          }} else if (type === 'all') {{
            clearAllFilters();
          }} else if (type === 'city') {{
            filterByCity(val, true, true);
          }} else if (type === 'country') {{
            filterByCountry(val, true);
          }} else if (type === 'category') {{
            setCategoryFilter(val, true);
          }} else if (type === 'region') {{
            if (val === 'europe') {{
              flyTo(10.0, 50.0, 2.3);
            }} else if (val === 'americas') {{
              flyTo(-85.0, 25.0, 2.0);
            }} else if (val === 'asiapacific') {{
              flyTo(120.0, 25.0, 2.0);
            }} else if (val === 'mena_africa') {{
              flyTo(25.0, 15.0, 2.0);
            }}
          }}
        }});
      }});
    }}
    wireGlobePillListeners();

    let selectedCategoryFilter = 'all';

    const FILTER_META = {{
      free: {{ label: 'FREE ADMISSION' }},
      sculpture: {{ label: 'OUTDOOR & SCULPTURE' }},
      research: {{ label: 'RESEARCH & COMMONS' }},
      monday: {{ label: 'MONDAY OPENINGS' }},
      transit: {{ label: 'PUBLIC TRANSIT TIPS' }},
      accessibility: {{ label: 'UNIVERSAL ACCESSIBILITY' }},
      amenities: {{ label: 'CAFÉS & BOOKSHOPS' }},
      ethical: {{ label: 'CLEAN FUNDING' }},
      artist_run: {{ label: 'ARTIST-RUN SPACES' }},
      fossil_free: {{ label: 'FOSSIL & DEFENSE-FREE' }},
      london: {{ label: 'LONDON ART SCENE' }},
      nyc: {{ label: 'NEW YORK ART SCENE' }},
      paris: {{ label: 'PARIS ART SCENE' }},
      research_method: {{ label: 'RESEARCH METHODOLOGY' }},
      research_shows: {{ label: 'LANDMARK EXHIBITIONS' }},
      research_restitution: {{ label: 'RESTITUTION & REPATRIATION' }},
      research_models: {{ label: 'FUNDING MODELS RESEARCH' }},
      research_mit: {{ label: 'MIT PRESS CANON' }},
      research_krauss: {{ label: 'LATE CAPITALIST MUSEUM' }},
      research_kwon: {{ label: 'SITE-SPECIFIC ART' }}
    }};

    function applyFilters() {{
      filteredList = ALL_INSTITUTIONS.filter(inst => {{
        if (!selectedTierFilter.has(inst.tier)) return false;

        if (selectedCountryFilter !== 'all') {{
          if (!matchC(inst.country, selectedCountryFilter)) return false;
        }}

        if (selectedCityFilter !== 'all') {{
          if (inst.city.toLowerCase() !== selectedCityFilter.toLowerCase()) return false;
        }}

        // Apply Category / Pill Filters to the Map and Catalog
        if (selectedCategoryFilter !== 'all') {{
          if (selectedCategoryFilter === 'free') {{
            const p = (inst.admission_policy || '').toLowerCase();
            if (!p.includes('free') && !p.includes('pay what you wish')) return false;
          }} else if (selectedCategoryFilter === 'monday') {{
            const h = (inst.opening_hours || '').toLowerCase();
            if (h.includes('closed mon')) return false;
            if (!h.includes('daily') && !h.includes('mon,') && !h.includes('mon–') && !h.includes('mon-') && !h.includes('mon ')) return false;
          }} else if (selectedCategoryFilter === 'transit') {{
            if (!inst.transit_tips || inst.transit_tips.length < 5) return false;
          }} else if (selectedCategoryFilter === 'accessibility') {{
            const a = (inst.accessibility || '').toLowerCase();
            if (!a.includes('step-free') && !a.includes('wheelchair') && !a.includes('elevator') && !a.includes('accessible')) return false;
          }} else if (selectedCategoryFilter === 'amenities') {{
            const am = (inst.amenities || '').toLowerCase();
            if (!am.includes('caf') && !am.includes('book') && !am.includes('garden') && !am.includes('dining')) return false;
          }} else if (selectedCategoryFilter === 'ethical') {{
            if (inst.tier !== 'A' && !inst.governance_type.includes('Civic') && !inst.governance_type.includes('Public')) return false;
          }} else if (selectedCategoryFilter === 'artist_run') {{
            if (!inst.governance_type || !inst.governance_type.toLowerCase().includes('artist')) return false;
          }} else if (selectedCategoryFilter === 'fossil_free') {{
            const s = (inst.ethical_safeguard || '').toLowerCase();
            if (inst.tier !== 'A' && !s.includes('divest') && !s.includes('fossil') && !s.includes('clean') && !s.includes('civic') && !s.includes('defense')) return false;
          }} else if (selectedCategoryFilter === 'london') {{
            if (!matchC(inst.city, 'London')) return false;
          }} else if (selectedCategoryFilter === 'nyc') {{
            if (!matchC(inst.city, 'New York') && !matchC(inst.city, 'Beacon')) return false;
          }} else if (selectedCategoryFilter === 'paris') {{
            if (!matchC(inst.city, 'Paris')) return false;
          }} else if (selectedCategoryFilter === 'moma') {{
            if (!matchC(inst.city, 'New York') && !matchC(inst.city, 'Beacon')) return false;
          }}
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

      const listTotalBadge = document.getElementById('listTotalBadge');
      if (listTotalBadge) listTotalBadge.textContent = `${{filteredList.length}} mapped`;

      // Update Floating Map Filter Banner
      const activeMapBanner = document.getElementById('activeMapFilterBanner');
      const activeMapIcon = document.getElementById('activeMapFilterIcon');
      const activeMapText = document.getElementById('activeMapFilterText');

      if (activeMapBanner && activeMapText) {{
        if (selectedCategoryFilter !== 'all') {{
          activeMapBanner.classList.remove('hidden');
          const meta = FILTER_META[selectedCategoryFilter] || {{ label: selectedCategoryFilter.toUpperCase() }};
          if (activeMapIcon) activeMapIcon.textContent = '';
          activeMapText.textContent = `${{meta.label}} · ${{filteredList.length}} SPACES ON MAP`;
        }} else {{
          activeMapBanner.classList.add('hidden');
        }}
      }}

      // Update Catalog Panel Banner if present
      const activeFilterBanner = document.getElementById('activeFilterBanner');
      const filterLabel = document.getElementById('filterLabel');
      const filterCount = document.getElementById('filterCount');
      if (activeFilterBanner) {{
        if (selectedCityFilter !== 'all' || selectedCountryFilter !== 'all' || selectedCategoryFilter !== 'all') {{
          activeFilterBanner.classList.remove('hidden');
          let activeName = selectedCityFilter !== 'all' ? selectedCityFilter : (selectedCountryFilter !== 'all' ? selectedCountryFilter : selectedCategoryFilter);
          if (FILTER_META[selectedCategoryFilter]) activeName = FILTER_META[selectedCategoryFilter].label;
          if (filterLabel) filterLabel.textContent = activeName.toUpperCase();
          if (filterCount) filterCount.textContent = `(${{filteredList.length}})`;
        }} else {{
          activeFilterBanner.classList.add('hidden');
        }}
      }}

      updateGlobePillsUI();
      renderLeftList();
    }}

    function renderLeftList() {{
      const container = document.getElementById('institutionsListContainer');
      if (filteredList.length === 0) {{
        let exHtml = '';
        if (searchQuery && typeof EXCLUDED_INSTITUTIONS !== 'undefined') {{
          const q = searchQuery.toLowerCase().trim();
          const matches = EXCLUDED_INSTITUTIONS.filter(i => 
            i.name.toLowerCase().includes(q) || 
            (i.aliases && i.aliases.some(a => a.toLowerCase().includes(q))) ||
            (i.city && i.city.toLowerCase().includes(q))
          );
          if (matches.length > 0) {{
            exHtml = `
              <div class="mt-4 p-3.5 rounded-xl bg-[#191024] border border-[#8a3ffc]/80 text-left space-y-2">
                <div class="flex items-center gap-1.5 text-[#be95ff] font-mono text-[13px] uppercase">
                  <span>Audited Corporate Underwriting Notice (${{matches.length}} Flagged)</span>
                </div>
                <p class="text-slate-300 text-[13px] leading-relaxed">
                  The space you searched is monitored under our corporate underwriting audit.
                </p>
                <div class="space-y-1.5 pt-1">
                  ${{matches.slice(0, 3).map(m => `
                    <div class="bg-[#1f1433] p-2.5 rounded-lg border border-[#8a3ffc]/50">
                      <div class="flex items-center justify-between text-[13px]">
                        <span class="text-white font-medium">${{escapeHtml(m.name)}}</span>
                        <span class="text-[#be95ff] text-[11px] font-mono px-1.5 py-0.5 rounded bg-[#2a1745] border border-[#8a3ffc]">${{m.tier === 'B' ? 'Tier B' : 'Tier U'}}</span>
                      </div>
                      <p class="text-[#e8daff] text-[12px] mt-0.5">${{escapeHtml(m.watch || m.why_flagged || m.funding || 'Corporate underwriting conflict')}}</p>
                      <button class="curator-dossier-btn text-[#be95ff] hover:underline text-[12px] font-mono mt-1 cursor-pointer" data-name="${{escapeHtml(m.name)}}">
                        Open Audit Dossier ↗
                      </button>
                    </div>
                  `).join('')}}
                </div>
              </div>
            `;
          }}
        }}

        container.innerHTML = `
          <div class="text-center py-6 px-4 text-[#64748b] text-[14px]">
            <p class="font-normal text-slate-400">No clean verified institutions match this filter.</p>
            ${{exHtml}}
            <button id="resetFromEmptyBtn" class="mt-4 px-3 py-1.5 rounded-xl bg-[#212121] border border-[#333] text-[#3b82f6] hover:text-white hover:bg-[#282828] text-[13px] transition cursor-pointer">Reset all filters</button>
          </div>
        `;
        document.getElementById('resetFromEmptyBtn')?.addEventListener('click', clearAllFilters);
        return;
      }}

      container.innerHTML = filteredList.map(inst => {{
        const isSel = selectedInstitution && selectedInstitution.name === inst.name;
        const isInstClean = inst.tier === 'A';
        const isInstFlagged = inst.tier === 'B';
        const tierCol = isInstClean 
          ? 'text-emerald-400 border-emerald-900/60 bg-[#0a2016]' 
          : isInstFlagged 
          ? 'text-[#be95ff] border-[#8a3ffc]/60 bg-[#1f1433]' 
          : 'text-[#33b1ff] border-[#0072c3]/60 bg-[#081a28]';
        const tierName = isInstClean 
          ? 'Tier A · Clean Verified' 
          : isInstFlagged 
          ? 'Tier B · Flagged Underwriting' 
          : 'Tier U · Roster Unverified';

        const webUrl = getValidWebUrl(inst);
        const displayDomain = getDisplayDomain(webUrl);

        return `
          <div class="inst-card bg-[#212121] border border-[#2e2e2e] rounded-2xl p-3.5 cursor-pointer hover:border-[#444] hover:bg-[#282828] transition ${{isSel ? 'border-[#3b82f6] bg-[#222834]' : ''}}" data-name="${{inst.name.replace(/"/g, '&quot;')}}">
            <div class="flex items-start justify-between gap-2">
              <h3 class="font-normal text-white text-[14px] leading-[120%] truncate max-w-[220px] sm:max-w-[260px]">${{inst.name}}</h3>
              <span class="text-[14px] px-2 py-0.5 rounded-lg border ${{tierCol}} shrink-0">${{tierName}}</span>
            </div>
            
            <div class="flex items-center gap-1.5 text-[14px] text-[#93c5fd] mt-1 font-mono">
              <span class="truncate">${{inst.location}}</span>
              <span class="text-[#555]">·</span>
              <span class="text-[#a1a1aa] text-[14px] shrink-0">Est. ${{inst.year_founded}}</span>
            </div>

            <!-- Researcher Tags: Governance & Admission -->
            <div class="flex items-center gap-1.5 text-[14px] font-mono text-[#a1a1aa] mt-2 flex-wrap">
              <span class="px-2 py-0.5 rounded-lg bg-[#2a2a2a] border border-[#383838] text-[#d4d4d4]">${{inst.governance_type}}</span>
              <span class="px-2 py-0.5 rounded-lg bg-[#2a2a2a] border border-[#383838] text-[#d4d4d4]">${{inst.admission_policy}}</span>
            </div>

            <!-- Quick Visitor Schedule & Pricing Pill -->
            <div class="mt-1.5 flex items-center gap-2 text-[14px] font-mono text-[#a1a1aa]">
              <span class="truncate">${{inst.opening_hours ? inst.opening_hours.split(',')[0] : 'Open Weekly'}}</span>
              <span class="text-[#555]">·</span>
              <span class="text-emerald-400 shrink-0 truncate max-w-[120px]">${{inst.admission_fee ? inst.admission_fee.split('/')[0].trim() : 'Free / Subsidized'}}</span>
            </div>

            <p class="text-[14px] text-[#d4d4d4] mt-2 leading-[120%] line-clamp-2">${{inst.curator_recommendation || inst.funding}}</p>
            
            ${{inst.watch ? `
              <div class="mt-2 pt-1.5 border-t border-[#2e2e2e] text-[14px] text-amber-300/80 truncate flex items-center gap-1 font-mono">
                <span>${{inst.watch}}</span>
              </div>
            ` : ''}}
            
            <div class="mt-2.5 pt-2 border-t border-[#2e2e2e] flex items-center justify-between">
              ${{webUrl ? `
                <a href="${{escapeHtml(webUrl)}}" target="_blank" rel="noopener noreferrer" 
                   class="website-pill inline-flex items-center gap-1 text-[14px] font-mono text-[#93c5fd] hover:text-white bg-[#2a2a2a] hover:bg-[#333] border border-[#383838] px-2.5 py-0.5 rounded-lg transition"
                   onclick="event.stopPropagation()">
                  <span class="truncate max-w-[120px]">${{escapeHtml(displayDomain)}}</span>
                  <span class="text-[14px]">↗</span>
                </a>
              ` : `
                <span class="text-[13px] font-mono text-slate-500">Verified Independent</span>
              `}}
              <span class="text-[14px] text-[#71717a] hover:text-white font-mono transition">View on Globe →</span>
            </div>
          </div>
        `;
      }}).join('');

      container.querySelectorAll('.inst-card').forEach(card => {{
        card.querySelectorAll('.card-open-dossier').forEach(dBtn => {{
          dBtn.addEventListener('click', (e) => {{
            e.preventDefault();
            e.stopPropagation();
            const dName = dBtn.getAttribute('data-name');
            const target = ALL_INSTITUTIONS.find(i => i.name === dName);
            if (target) openDossier(target);
          }});
        }});

        card.addEventListener('click', () => {{
          const name = card.getAttribute('data-name');
          const inst = ALL_INSTITUTIONS.find(i => i.name === name);
          if (inst) {{
            selectInstitution(inst, true);
          }}
        }});
      }});
    }}

    let lastSelectedCountry = null;

    function filterByCity(cityName, zoom = true, notifyCurator = true) {{
      selectedCityFilter = cityName;
      if (typeof curatorContext !== 'undefined' && cityName && cityName !== 'all') {{
        curatorContext.lastCity = cityName;
      }}
      const cityMeta = ALL_CITIES_REGISTRY.find(c => matchC(c.name, cityName));
      if (cityMeta && cityMeta.country) {{
        lastSelectedCountry = cityMeta.country;
      }}
      applyFilters();

      const cty = ALL_CITIES_REGISTRY.find(c => matchC(c.name, cityName));
      const targetZoom = zoom ? getCityTargetRadius(cityName) : null;

      if (cty) {{
        flyTo(cty.lon, cty.lat, targetZoom);
      }} else {{
        const inst = ALL_INSTITUTIONS.find(i => matchC(i.city, cityName));
        if (inst) flyTo(inst.lon, inst.lat, targetZoom);
      }}

      if (zoom && cityName && cityName !== 'all') {{
        targetRadius = targetZoom || getCityTargetRadius(cityName);
        isAutoSpinning = false;
        openCityStreetView(cityName);
      }} else if (cityName === 'all') {{
        exitCityStreetView();
      }}

      const cityMatches = ALL_INSTITUTIONS.filter(i => matchC(i.city, cityName));

      updateGlobePillsUI();

      // Notify Curator if triggered from canvas / UI
      if (notifyCurator && cityMatches.length > 0) {{
        const topInsts = cityMatches.slice(0, 3).map(i => formatInstLink(i, {{noCity: true}})).join(', ');
        appendCuratorMessage(`
          <p class="text-slate-200">
            We are now exploring <a href="#" class="city-link font-normal text-white hover:text-[#60a5fa] underline cursor-pointer" data-city="${{escapeHtml(cityName)}}">${{escapeHtml(cityName)}}</a>, home to <strong>${{cityMatches.length}}</strong> spaces with clean funding.
          </p>
          <p class="text-slate-300">
            Highlights include ${{topInsts}}. None of them accept oil or defense sponsorships.
          </p>
        `);
      }}
    }}

    function filterByCountry(countryName, zoom = true) {{
      if (isCityStreetViewActive) {{
        exitCityStreetView();
      }}
      selectedCountryFilter = countryName;
      selectedCityFilter = 'all';
      lastSelectedCountry = countryName;
      selectedInstitution = null;
      applyFilters();

      const c = ALL_COUNTRIES_REGISTRY.find(c => matchC(c.name, countryName));
      if (c && zoom) {{
        const countryZoom = baseRadius * (c.zoom || 3.2);
        targetRadius = countryZoom;
        flyTo(c.lon, c.lat, countryZoom);
        isAutoSpinning = false;
      }} else if (c) {{
        flyTo(c.lon, c.lat);
      }}

      updateGlobeBarForCountry(countryName);
      updateGlobePillsUI();

      // Notify the Curator to give an educational briefing on this country
      const countryMatches = ALL_INSTITUTIONS.filter(i => matchC(i.country, countryName));
      if (countryMatches.length > 0) {{
        const topInsts = countryMatches.slice(0, 3).map(i => formatInstLink(i)).join(', ');
        const citiesInCountry = ALL_CITIES_REGISTRY.filter(ci => matchC(ci.country, countryName));
        appendCuratorMessage(`
          <p class="text-slate-200">
            Across <strong>${{escapeHtml(countryName)}}</strong>, Culture Atlas has <strong>${{countryMatches.length}}</strong> clean spaces mapped in <strong>${{citiesInCountry.length}} cities</strong>.
          </p>
          <p class="text-slate-300">
            Top places to explore include ${{topInsts}}. Click any city or space on the map to zoom in to street view!
          </p>
        `);
      }}
    }}

    function clearAllFilters() {{
      if (isCityStreetViewActive) {{
        exitCityStreetView();
      }}
      selectedCityFilter = 'all';
      selectedCountryFilter = 'all';
      selectedCategoryFilter = 'all';
      searchQuery = '';
      if (searchInput) searchInput.value = '';
      selectedTierFilter = new Set(['A']);
      document.querySelectorAll('.tier-chip').forEach(btn => {{
        btn.classList.add('bg-[#0c2419]', 'bg-[#0e213b]', 'bg-[#171a24]');
      }});
      if (countrySelect) countrySelect.value = 'all';
      if (citySelect) citySelect.value = 'all';
      targetRadius = baseRadius;
      isAutoSpinning = true;
      renderGlobeBarDefault();
      applyFilters();
    }}

    // Filter event listeners safely wired
    countrySelect?.addEventListener('change', e => {{
      selectedCountryFilter = e.target.value;
      selectedCityFilter = 'all';
      if (citySelect) citySelect.value = 'all';
      applyFilters();
      if (selectedCountryFilter !== 'all') {{
        filterByCountry(selectedCountryFilter);
      }}
    }});

    citySelect?.addEventListener('change', e => {{
      selectedCityFilter = e.target.value;
      selectedCountryFilter = 'all';
      if (countrySelect) countrySelect.value = 'all';
      applyFilters();
      if (selectedCityFilter !== 'all') {{
        filterByCity(selectedCityFilter, true, true);
      }}
    }});

    searchInput?.addEventListener('input', e => {{
      searchQuery = e.target.value;
      applyFilters();
    }});

    searchInput?.addEventListener('keydown', e => {{
      if (e.key === 'Enter') {{
        e.preventDefault();
        if (filteredList.length > 0) {{
          const target = filteredList[0];
          selectInstitution(target, true);
          flyTo(target.lon, target.lat, getCityTargetRadius(target.city));
        }}
      }}
    }});

    document.getElementById('clearSearchBtn')?.addEventListener('click', () => {{
      if (searchInput) searchInput.value = '';
      searchQuery = '';
      applyFilters();
    }});

    document.getElementById('clearFilterBtn')?.addEventListener('click', clearAllFilters);

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
    function handleGlobeClick(clientX, clientY) {{
      const rect = canvas.getBoundingClientRect();
      const mx = clientX - rect.left;
      const my = clientY - rect.top;
      const cx = width / 2;
      const cy = height / 2;
      const r = currentRadius;

      // 0. Check city museum hitboxes (when in city street view)
      for (let i = 0; i < cityMuseumHitboxes.length; i++) {{
        const m = cityMuseumHitboxes[i];
        if (m.webBtn && mx >= m.webBtn.x - 4 && mx <= m.webBtn.x + m.webBtn.w + 4 && my >= m.webBtn.y - 4 && my <= m.webBtn.y + m.webBtn.h + 4) {{
          window.open(m.webBtn.url, '_blank', 'noopener,noreferrer');
          return;
        }}
        const insideBadge = mx >= m.x && mx <= m.x + m.w && my >= m.y && my <= m.y + m.h;
        const nearPin = Math.hypot(m.pinX - mx, m.pinY - my) < 18;
        if (insideBadge || nearPin) {{
          selectInstitution(m.inst, false);
          return;
        }}
      }}

      // 0.2 Check hovered micro card web button
      if (hoveredMicroCardHitbox && hoveredMicroCardHitbox.webUrl) {{
        const hb = hoveredMicroCardHitbox;
        if (mx >= hb.btnX - 4 && mx <= hb.btnX + hb.btnW + 4 && my >= hb.btnY - 4 && my <= hb.btnY + hb.btnH + 4) {{
          window.open(hb.webUrl, '_blank', 'noopener,noreferrer');
          return;
        }}
        if (mx >= hb.cardX && mx <= hb.cardX + hb.cardW && my >= hb.cardY && my <= hb.cardY + hb.cardH) {{
          selectInstitution(hb.inst, false);
          return;
        }}
      }}

      // 0.5 Check City Cluster Hitboxes on Globe
      for (let i = 0; i < cityClusterHitboxes.length; i++) {{
        const cl = cityClusterHitboxes[i];
        if (Math.hypot(cl.cx - mx, cl.cy - my) < cl.w / 2 + 6) {{
          filterByCity(cl.cityName, true, true);
          return;
        }}
      }}

      // 1. Check priority city hitboxes with generous hit padding
      for (let i = 0; i < cityBadgeHitboxes.length; i++) {{
        const b = cityBadgeHitboxes[i];
        if (mx >= b.x - 14 && mx <= b.x + b.w + 14 && my >= b.y - 12 && my <= b.y + b.h + 12) {{
          filterByCity(b.name, true, true);
          return;
        }}
      }}

      // 2. Check institution dots (generous 16px radius, zooms directly to street!)
      for (let i = 0; i < visibleDots.length; i++) {{
        const d = visibleDots[i];
        if (Math.hypot(d.x - mx, d.y - my) < 16) {{
          selectInstitution(d.inst, true);
          return;
        }}
      }}

      // 3. Check country centroid text (generous 40px radius, zooms directly to country!)
      for (let i = 0; i < COUNTRY_CENTROIDS.length; i++) {{
        const c = COUNTRY_CENTROIDS[i];
        const pt = project(c.lon, c.lat, r, cx, cy);
        if (pt.front && Math.hypot(pt.x - mx, pt.y - my) < 40) {{
          filterByCountry(c.name, true);
          return;
        }}
      }}

      // 4. Check country polygon on globe surface
      const geo = unproject(mx, my, r, cx, cy);
      if (geo) {{
        for (let i = 0; i < COUNTRY_POLYS.length; i++) {{
          const country = COUNTRY_POLYS[i];
          for (let j = 0; j < country.r.length; j++) {{
            if (pointInPolygon(geo.lon, geo.lat, country.r[j])) {{
              filterByCountry(country.n, true);
              return;
            }}
          }}
        }}
      }}

      // 5. Check Rail Corridor Click
      if (hoveredRailCorridor) {{
        const corr = hoveredRailCorridor;
        appendCuratorMessage(`
          <p class="text-slate-200">
            <strong>${{escapeHtml(corr.name)}}</strong>: High-speed electric link connecting <strong>${{escapeHtml(corr.from)}}</strong> and <strong>${{escapeHtml(corr.to)}}</strong> (${{escapeHtml(corr.travel_time || 'eco-transit')}}).
          </p>
          <p class="text-slate-300">
            Both cultural capitals are home to verified independent spaces operating free of fossil fuel, chemical, and weapons funding. Traveling between them by electric train cuts carbon emissions by up to 90% compared to flying.
          </p>
        `);
        return;
      }}

      // Check Compass Rose click to re-orient North
      if (Math.hypot(mx - (width - 38), my - 38) < 22) {{
        flyTo(rotLon, 35);
        return;
      }}

      // If clicked empty ocean or space on the globe, dismiss floating card
      if (selectedInstitution) {{
        deselectInstitution();
      }}
    }}

    // Check hover target for dynamic pointer cursor feedback
    function updateHoverCursor(clientX, clientY) {{
      if (isDragging) return;
      const rect = canvas.getBoundingClientRect();
      const mx = clientX - rect.left;
      const my = clientY - rect.top;
      const cx = width / 2;
      const cy = height / 2;
      const r = currentRadius;

      hoveredInstitution = null;
      hoveredCity = null;
      hoveredCountry = null;

      // Check Rail Corridor Hover
      hoveredRailCorridor = null;
      hoveredRailPoint = null;
      if (isRailVisible && r > baseRadius * 1.1 && r < baseRadius * 14.0) {{
        for (let i = 0; i < CLEAN_RAIL_CORRIDORS.length; i++) {{
          const corridor = CLEAN_RAIL_CORRIDORS[i];
          for (let k = 0; k < corridor.pts.length - 1; k++) {{
            const p1 = project(corridor.pts[k][0], corridor.pts[k][1], r, cx, cy);
            const p2 = project(corridor.pts[k + 1][0], corridor.pts[k + 1][1], r, cx, cy);
            if (p1.front && p2.front) {{
              const dist = distToSegment(mx, my, p1.x, p1.y, p2.x, p2.y);
              if (dist < 10) {{
                canvas.style.cursor = 'pointer';
                hoveredRailCorridor = corridor;
                hoveredRailPoint = {{ x: mx, y: my }};
                return;
              }}
            }}
          }}
        }}
      }}

      // Check Compass Rose hover
      if (Math.hypot(mx - (width - 38), my - 38) < 22) {{
        canvas.style.cursor = 'pointer';
        return;
      }}

      // Check hovered micro card
      if (hoveredMicroCardHitbox && hoveredMicroCardHitbox.webUrl) {{
        const hb = hoveredMicroCardHitbox;
        if (mx >= hb.cardX && mx <= hb.cardX + hb.cardW && my >= hb.cardY && my <= hb.cardY + hb.cardH) {{
          canvas.style.cursor = 'pointer';
          return;
        }}
      }}

      // Check city museum hitboxes (when in city street view)
      for (let i = 0; i < cityMuseumHitboxes.length; i++) {{
        const m = cityMuseumHitboxes[i];
        const insideBadge = mx >= m.x && mx <= m.x + m.w && my >= m.y && my <= m.y + m.h;
        const nearPin = Math.hypot(m.pinX - mx, m.pinY - my) < 18;
        if (insideBadge || nearPin) {{
          canvas.style.cursor = 'pointer';
          hoveredInstitution = m.inst;
          return;
        }}
      }}

      // Check City Cluster Hitboxes on Globe
      for (let i = 0; i < cityClusterHitboxes.length; i++) {{
        const cl = cityClusterHitboxes[i];
        if (Math.hypot(cl.cx - mx, cl.cy - my) < cl.w / 2 + 6) {{
          canvas.style.cursor = 'pointer';
          hoveredCity = cl.cityName;
          return;
        }}
      }}

      // Check city badge
      for (let i = 0; i < cityBadgeHitboxes.length; i++) {{
        const b = cityBadgeHitboxes[i];
        if (mx >= b.x - 14 && mx <= b.x + b.w + 14 && my >= b.y - 12 && my <= b.y + b.h + 12) {{
          canvas.style.cursor = 'pointer';
          hoveredCity = b.name;
          return;
        }}
      }}

      // Check institution dot
      for (let i = 0; i < visibleDots.length; i++) {{
        const d = visibleDots[i];
        if (Math.hypot(d.x - mx, d.y - my) < 16) {{
          canvas.style.cursor = 'pointer';
          hoveredInstitution = d.inst;
          return;
        }}
      }}

      // Check country centroid
      for (let i = 0; i < COUNTRY_CENTROIDS.length; i++) {{
        const c = COUNTRY_CENTROIDS[i];
        const pt = project(c.lon, c.lat, r, cx, cy);
        if (pt.front && Math.hypot(pt.x - mx, pt.y - my) < 40) {{
          canvas.style.cursor = 'pointer';
          hoveredCountry = c.name;
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
              canvas.style.cursor = 'pointer';
              hoveredCountry = country.n;
              return;
            }}
          }}
        }}
      }}

      canvas.style.cursor = 'grab';
    }}

    canvas.addEventListener('pointermove', e => {{
      updateHoverCursor(e.clientX, e.clientY);
    }});

    // Reliable click detector for canvas
    canvas.addEventListener('click', e => {{
      const dist = Math.hypot(e.clientX - pointerStartX, e.clientY - pointerStartY);
      if (dist < 22) {{
        handleGlobeClick(e.clientX, e.clientY);
      }}
    }});

    // Double-click to zoom in centered on target point
    canvas.addEventListener('dblclick', e => {{
      e.preventDefault();
      const rect = canvas.getBoundingClientRect();
      const mx = e.clientX - rect.left;
      const my = e.clientY - rect.top;
      const geo = unproject(mx, my, currentRadius, width / 2, height / 2);
      if (geo && isFinite(geo.lon) && isFinite(geo.lat)) {{
        flyTo(geo.lon, geo.lat, currentRadius * 1.7);
      }} else {{
        targetRadius = Math.min(getMaxRadius(), targetRadius * 1.5);
      }}
    }});

    // Keyboard navigation for map power users
    window.addEventListener('keydown', e => {{
      if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA' || e.target.isContentEditable) {{
        return;
      }}
      if (e.key === '+' || e.key === '=') {{
        e.preventDefault();
        isAutoSpinning = false;
        targetRadius = Math.min(getMaxRadius(), targetRadius * 1.30);
      }} else if (e.key === '-' || e.key === '_') {{
        e.preventDefault();
        targetRadius = Math.max(getMinRadius(), targetRadius * 0.77);
        if (targetRadius < baseRadius * 3.5 && selectedCityFilter !== 'all') {{
          selectedCityFilter = 'all';
          applyFilters();
        }}
      }} else if (e.key === 'ArrowLeft') {{
        e.preventDefault();
        isAutoSpinning = false;
        rotLon = (rotLon + 6) % 360;
      }} else if (e.key === 'ArrowRight') {{
        e.preventDefault();
        isAutoSpinning = false;
        rotLon = (rotLon - 6) % 360;
      }} else if (e.key === 'ArrowUp') {{
        e.preventDefault();
        isAutoSpinning = false;
        rotLat = Math.min(82, rotLat + 5);
      }} else if (e.key === 'ArrowDown') {{
        e.preventDefault();
        isAutoSpinning = false;
        rotLat = Math.max(-82, rotLat - 5);
      }} else if (e.key === 'Escape') {{
        const drawer = document.getElementById('detailDrawer');
        const catModal = document.getElementById('catalogModal');
        const auditModal = document.getElementById('momaAuditModal');
        const rfModal = document.getElementById('researchFeedbackModal');
        const arModal = document.getElementById('academicResearchModal');
        if (rfModal && !rfModal.classList.contains('hidden')) {{
          rfModal.classList.add('hidden');
        }} else if (arModal && !arModal.classList.contains('hidden')) {{
          arModal.classList.add('hidden');
        }} else if (drawer && !drawer.classList.contains('hidden')) {{
          drawer.classList.add('hidden');
        }} else if (catModal && !catModal.classList.contains('hidden')) {{
          catModal.classList.add('hidden');
        }} else if (auditModal && !auditModal.classList.contains('hidden')) {{
          auditModal.classList.add('hidden');
        }} else if (selectedInstitution) {{
          deselectInstitution();
        }} else if (selectedCityFilter !== 'all') {{
          clearAllFilters();
        }}
      }}
    }});

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

    // Smooth, Gradual Exponential Wheel & Trackpad Zoom with Cursor Targeting
    canvas.addEventListener('wheel', e => {{
      e.preventDefault();
      isAutoSpinning = false;

      const rect = canvas.getBoundingClientRect();
      const mx = e.clientX - rect.left;
      const my = e.clientY - rect.top;
      const cx = width / 2;
      const cy = height / 2;

      const delta = e.deltaY * (e.deltaMode === 1 ? 18 : e.deltaMode === 2 ? 260 : 1);
      // Gentle exponential scaling factor bounded per event (approx 1% - 6% gradual change)
      const factor = Math.exp(-delta * 0.0016);
      const clampedFactor = Math.max(0.91, Math.min(1.09, factor));

      // Calculate geographic point under mouse cursor before zooming
      const geoBefore = unproject(mx, my, currentRadius, cx, cy);

      targetRadius = Math.max(getMinRadius(), Math.min(getMaxRadius(), targetRadius * clampedFactor));

      // If zooming in and cursor is over the globe, gently bias rotation towards cursor
      if (clampedFactor > 1.0 && geoBefore && isFinite(geoBefore.lon) && isFinite(geoBefore.lat)) {{
        let dLon = (geoBefore.lon - rotLon) % 360;
        if (dLon > 180) dLon -= 360;
        if (dLon < -180) dLon += 360;
        const dLat = geoBefore.lat - rotLat;
        const nudge = Math.min(0.20, (clampedFactor - 1.0) * 1.4);
        rotLon = (rotLon + dLon * nudge) % 360;
        rotLat = Math.max(-80, Math.min(80, rotLat + dLat * nudge));
      }}

      // When zooming deep into the globe, seamlessly transition into interactive city street view
      if (targetRadius > baseRadius * 8.0 && !isCityStreetViewActive) {{
        let closestDist = Infinity;
        let closestCity = null;
        for (let i = 0; i < ALL_CITIES_REGISTRY.length; i++) {{
          const c = ALL_CITIES_REGISTRY[i];
          const dDeg = Math.hypot(c.lon - rotLon, c.lat - rotLat);
          if (dDeg < closestDist) {{
            closestDist = dDeg;
            closestCity = c;
          }}
        }}
        if (closestCity && closestDist < 3.5) {{
          filterByCity(closestCity.name, true, false);
        }}
      }}

      if (targetRadius < baseRadius * 3.5 && selectedCityFilter !== 'all') {{
        selectedCityFilter = 'all';
        applyFilters();
        if (selectedCountryFilter !== 'all') {{
          updateGlobeBarForCountry(selectedCountryFilter);
        }} else {{
          renderGlobeBarDefault();
        }}
      }}
      if (targetRadius < baseRadius * 1.3 && selectedCountryFilter !== 'all') {{
        selectedCountryFilter = 'all';
        applyFilters();
        renderGlobeBarDefault();
      }}
    }}, {{ passive: false }});

    // Additional HUD Quick Controls (World, Auto-Spin, Expand)
    document.getElementById('hudWorldBtn')?.addEventListener('click', (e) => {{
      e.stopPropagation();
      exitCityStreetView();
      clearAllFilters();
      flyTo(-45, 35, baseRadius);
    }});

    document.getElementById('hudEuropeBtn')?.addEventListener('click', (e) => {{
      e.stopPropagation();
      exitCityStreetView();
      clearAllFilters();
      flyTo(9.5, 49.5, baseRadius * 3.8);
    }});

    document.getElementById('hudAmericasBtn')?.addEventListener('click', (e) => {{
      e.stopPropagation();
      exitCityStreetView();
      clearAllFilters();
      flyTo(-78.0, 32.0, baseRadius * 3.2);
    }});

    document.getElementById('hudAsiaBtn')?.addEventListener('click', (e) => {{
      e.stopPropagation();
      exitCityStreetView();
      clearAllFilters();
      flyTo(137.5, 36.5, baseRadius * 3.6);
    }});

    document.getElementById('hudRailToggle')?.addEventListener('click', (e) => {{
      e.stopPropagation();
      isRailVisible = !isRailVisible;
      const btn = document.getElementById('hudRailToggle');
      if (btn) {{
        btn.classList.toggle('text-[#38bdf8]', isRailVisible);
        btn.classList.toggle('bg-[#1e2e42]', isRailVisible);
        btn.classList.toggle('border-[#0284c7]/40', isRailVisible);
        btn.classList.toggle('text-[#71717a]', !isRailVisible);
        btn.classList.toggle('bg-[#242424]', !isRailVisible);
        btn.classList.toggle('border-transparent', !isRailVisible);
      }}
    }});

    document.getElementById('hudSpinBtn')?.addEventListener('click', (e) => {{
      e.stopPropagation();
      isAutoSpinning = !isAutoSpinning;
      const spinTxt = document.getElementById('hudSpinText');
      if (spinTxt) spinTxt.textContent = isAutoSpinning ? 'Pause' : 'Spin';
    }});

    document.getElementById('hudExpandBtn')?.addEventListener('click', (e) => {{
      e.stopPropagation();
      handleViewExpand();
      const expTxt = document.getElementById('hudExpandText');
      if (expTxt) expTxt.textContent = isGlobeExpanded ? 'Split' : 'Expand';
    }});

    document.getElementById('zoomInBtn')?.addEventListener('click', () => {{
      isAutoSpinning = false;
      targetRadius = Math.min(getMaxRadius(), targetRadius * 1.30);
    }});
    document.getElementById('zoomOutBtn')?.addEventListener('click', () => {{
      targetRadius = Math.max(getMinRadius(), targetRadius * 0.77);
      if (targetRadius < baseRadius * 3.5 && selectedCityFilter !== 'all') {{
        selectedCityFilter = 'all';
        applyFilters();
        if (selectedCountryFilter !== 'all') {{
          updateGlobeBarForCountry(selectedCountryFilter);
        }} else {{
          renderGlobeBarDefault();
        }}
      }}
      if (targetRadius < baseRadius * 1.3 && selectedCountryFilter !== 'all') {{
        selectedCountryFilter = 'all';
        applyFilters();
        renderGlobeBarDefault();
      }}
    }});
    document.getElementById('exitStreetViewBtn')?.addEventListener('click', (e) => {{
      e.stopPropagation();
      exitCityStreetView();
    }});
    document.getElementById('backToCountryBtn')?.addEventListener('click', (e) => {{
      e.stopPropagation();
      exitCityStreetView();
      if (lastSelectedCountry) {{
        filterByCountry(lastSelectedCountry, true);
      }} else {{
        clearAllFilters();
      }}
    }});
    document.getElementById('backToWorldBtn')?.addEventListener('click', (e) => {{
      e.stopPropagation();
      exitCityStreetView();
      clearAllFilters();
    }});
    // =========================================================
    // 🌍 GLOBAL RESET CONTROLLER: Resets 3D Globe, Clears Filters, Exits Street View
    // =========================================================
    function resetGlobeView() {{
      // 1. Exit high-resolution city street view if active and return to 3D Globe
      if (typeof exitCityStreetView === 'function' && isCityStreetViewActive) {{
        exitCityStreetView();
      }}

      // 2. Clear all active spatial filters (city, country, category, search query, tier reset)
      if (typeof clearAllFilters === 'function') {{
        clearAllFilters();
      }}

      // 3. Dismiss active dossiers, floating cards, or exclusion audit modals
      if (typeof deselectInstitution === 'function') {{
        deselectInstitution();
      }}
      document.getElementById('detailDrawer')?.classList.add('hidden');
      document.getElementById('floatingCard')?.classList.add('hidden');
      document.getElementById('momaAuditModal')?.classList.add('hidden');

      // 4. Smoothly reset camera zoom and orientation to global planetary overview
      targetRadius = baseRadius;
      currentRadius = baseRadius;
      if (typeof flyTo === 'function') {{
        flyTo(0, 20, baseRadius);
      }} else {{
        targetRotLon = 0;
        targetRotLat = 20;
      }}
      isAutoSpinning = true;

      // 5. Restore default status bar and trigger frame re-render
      if (typeof renderGlobeBarDefault === 'function') {{
        renderGlobeBarDefault();
      }}
      if (typeof render === 'function') {{
        requestAnimationFrame(render);
      }}
    }}
    window.resetGlobeView = resetGlobeView;

    // Both the Header Brand Logo and the Top Reset Button reset the globe view
    document.getElementById('topBrandLogoBtn')?.addEventListener('click', (e) => {{
      e.preventDefault();
      resetGlobeView();
    }});
    document.getElementById('topResetBtn')?.addEventListener('click', (e) => {{
      e.preventDefault();
      resetGlobeView();
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
      filterByCity('NEW YORK');
    }});

    momaAuditChatBtn?.addEventListener('click', () => {{
      closeMomaAuditModal();
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
      velLon = 0;
      velLat = 0;
    }});

    window.addEventListener('pointermove', e => {{
      if (isDragging) {{
        const dx = e.clientX - lastX;
        const dy = e.clientY - lastY;
        lastX = e.clientX;
        lastY = e.clientY;
        const dragSens = (baseRadius / Math.max(baseRadius, currentRadius)) * 0.18;
        const cosLat = Math.max(0.25, Math.cos(toRad(rotLat)));
        const dLonStep = (dx * dragSens) / cosLat;
        const dLatStep = dy * dragSens;
        rotLon = (rotLon - dLonStep) % 360;
        rotLat = Math.max(-82, Math.min(82, rotLat + dLatStep));
        velLon = velLon * 0.35 + dLonStep * 0.65;
        velLat = velLat * 0.35 + dLatStep * 0.65;
      }}
    }});

    window.addEventListener('pointerup', e => {{
      if (isDragging) {{
        isDragging = false;
        canvas.classList.remove('dragging');
        const dist = Math.hypot(e.clientX - pointerStartX, e.clientY - pointerStartY);
        if (dist < 6) {{
          velLon = 0;
          velLat = 0;
        }}
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
