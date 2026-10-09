#!/usr/bin/env python3
"""
apply_distinct_spaces_and_google_maps.py
Applies:
1. Google Maps Satellite Raster Source & Layer in GOOGLE_MAPS_DARK_STYLE
2. Procedural distinct architectural spatial footprints (generateDistinctFootprint)
3. Google Images & Satellite Real Space Showcase in #buildingFloorInspectorHud & #floatingCard
4. Dynamic zoom-17 satellite aerial snapshot calculation & Google 3D / Street View links
5. Strict 3-font-size preservation (14px, 18px, 27px)
"""

import sys
import re

def main():
    target = 'build_conversational_atlas.py'
    with open(target, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Update GOOGLE_MAPS_DARK_STYLE sources: add google-satellite
    old_source = """      sources: {{
        openmaptiles: {{
          type: 'vector',
          tiles: ['https://tiles.openfreemap.org/planet/latest/{{z}}/{{x}}/{{y}}.pbf'],
          minzoom: 0,
          maxzoom: 14
        }}
      }},"""

    new_source = """      sources: {{
        openmaptiles: {{
          type: 'vector',
          tiles: ['https://tiles.openfreemap.org/planet/latest/{{z}}/{{x}}/{{y}}.pbf'],
          minzoom: 0,
          maxzoom: 14
        }},
        'google-satellite': {{
          type: 'raster',
          tiles: [
            'https://mt0.google.com/vt/lyrs=s&x={{x}}&y={{y}}&z={{z}}',
            'https://mt1.google.com/vt/lyrs=s&x={{x}}&y={{y}}&z={{z}}',
            'https://mt2.google.com/vt/lyrs=s&x={{x}}&y={{y}}&z={{z}}',
            'https://mt3.google.com/vt/lyrs=s&x={{x}}&y={{y}}&z={{z}}'
          ],
          tileSize: 256,
          maxzoom: 20
        }}
      }},"""

    assert old_source in content, "old_source not found in build_conversational_atlas.py"
    content = content.replace(old_source, new_source, 1)

    # 2. Add google-satellite-layer before building in GOOGLE_MAPS_DARK_STYLE
    old_waterway = """        {{
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
          id: 'building',"""

    new_waterway = """        {{
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
          id: 'google-satellite-layer',
          type: 'raster',
          source: 'google-satellite',
          minzoom: 12,
          paint: {{
            'raster-opacity': [
              'interpolate',
              ['linear'],
              ['zoom'],
              12, 0.0,
              14, 0.55,
              16, 0.90,
              18, 0.95
            ]
          }}
        }},
        {{
          id: 'building',"""

    assert old_waterway in content, "old_waterway not found in build_conversational_atlas.py"
    content = content.replace(old_waterway, new_waterway, 1)

    # 3. Add mock map methods in initCityMapIfNeeded
    old_mock_tail = """          _sources: {{}},
          _layers: {{}},
          addSource: function(id, src) {{
            const s = Object.assign({{ setData: function(d) {{ s.data = d; }} }}, src);
            this._sources[id] = s;
            return s;
          }},
          getSource: function(id) {{ return this._sources[id] || null; }},
          addLayer: function(l) {{ this._layers[l.id] = l; return l; }},
          getLayer: function(id) {{ return this._layers[id] || null; }},"""

    new_mock_tail = """          _sources: {{}},
          _layers: {{}},
          addSource: function(id, src) {{
            const s = Object.assign({{ setData: function(d) {{ s.data = d; }} }}, src);
            this._sources[id] = s;
            return s;
          }},
          getSource: function(id) {{ return this._sources[id] || null; }},
          addLayer: function(l) {{ this._layers[l.id] = l; return l; }},
          getLayer: function(id) {{ return this._layers[id] || null; }},
          setLayoutProperty: function(id, name, val) {{ if (this._layers[id]) {{ this._layers[id][name] = val; }} }},
          setPaintProperty: function(id, name, val) {{ if (this._layers[id]) {{ this._layers[id][name] = val; }} }},"""

    assert old_mock_tail in content, "old_mock_tail not found in build_conversational_atlas.py"
    content = content.replace(old_mock_tail, new_mock_tail, 1)

    # 4. Add Satellite Toggle Button to cityViewControlBanner
    old_city_banner = """        <div id="cityViewTitleBadge" class="px-2 sm:px-2.5 py-1 sm:py-1.5 rounded-xl bg-[#0c1626]/95 border border-[#1e2e4a] text-[#93c5fd] text-[14px] sm:text-[14px] font-mono flex items-center gap-1 shadow-lg backdrop-blur shrink-0 truncate max-w-[190px] sm:max-w-none">
          <span id="cityViewTitleText">LONDON · STREET VIEW</span>
        </div>
      </div>"""

    new_city_banner = """        <button id="toggleSatelliteMapBtn" type="button" onclick="window.toggleSatelliteMode()" class="px-2 sm:px-2.5 py-1 sm:py-1.5 rounded-xl bg-[#1e293b]/95 hover:bg-[#334155] border border-emerald-500/60 text-emerald-300 hover:text-white text-[14px] sm:text-[14px] flex items-center gap-1 shadow-lg backdrop-blur transition cursor-pointer active:scale-95 shrink-0" title="Toggle Google Maps Satellite layer">
          <span>🛰️ Satellite</span>
        </button>
        <div id="cityViewTitleBadge" class="px-2 sm:px-2.5 py-1 sm:py-1.5 rounded-xl bg-[#0c1626]/95 border border-[#1e2e4a] text-[#93c5fd] text-[14px] sm:text-[14px] font-mono flex items-center gap-1 shadow-lg backdrop-blur shrink-0 truncate max-w-[190px] sm:max-w-none">
          <span id="cityViewTitleText">LONDON · STREET VIEW</span>
        </div>
      </div>"""

    assert old_city_banner in content, "old_city_banner not found in build_conversational_atlas.py"
    content = content.replace(old_city_banner, new_city_banner, 1)

    # 5. Add Google Exploration buttons to floatingCard
    old_floating_buttons = """        <!-- DIRECT WEB & VISITOR ACTION BUTTONS -->
        <div class="mt-2.5 flex items-center gap-2 flex-wrap">
          <a id="floatingCardDirectWebBtn" href="#" target="_blank" rel="noopener noreferrer" 
             class="atlas-pill-btn pill-sm"
             onclick="event.stopPropagation()">
            <svg class="arrow-icon" viewBox="0 0 24 24"><line x1="7" y1="7" x2="17" y2="17"></line><polyline points="8 17 17 17 17 8"></polyline></svg>
            <span>Visit Website</span>
            <span id="floatingCardDirectDomain" class="text-[14px] opacity-70 font-mono"></span>
          </a>"""

    new_floating_buttons = """        <!-- DIRECT WEB & VISITOR ACTION BUTTONS -->
        <div class="mt-2.5 flex items-center gap-2 flex-wrap">
          <a id="floatingCardDirectWebBtn" href="#" target="_blank" rel="noopener noreferrer" 
             class="atlas-pill-btn pill-sm"
             onclick="event.stopPropagation()">
            <svg class="arrow-icon" viewBox="0 0 24 24"><line x1="7" y1="7" x2="17" y2="17"></line><polyline points="8 17 17 17 17 8"></polyline></svg>
            <span>Visit Website</span>
            <span id="floatingCardDirectDomain" class="text-[14px] opacity-70 font-mono"></span>
          </a>
          <a id="floatingCardGoogleImagesBtn" href="#" target="_blank" rel="noopener noreferrer" 
             class="atlas-pill-btn pill-sm"
             onclick="event.stopPropagation()"
             title="Explore actual space photos on Google Images">
            <svg class="arrow-icon" viewBox="0 0 24 24"><line x1="7" y1="7" x2="17" y2="17"></line><polyline points="8 17 17 17 17 8"></polyline></svg>
            <span>Google Images</span>
          </a>
          <a id="floatingCardGoogleMaps3dBtn" href="#" target="_blank" rel="noopener noreferrer" 
             class="atlas-pill-btn pill-sm"
             onclick="event.stopPropagation()"
             title="Open Google Maps 3D Satellite">
            <svg class="arrow-icon" viewBox="0 0 24 24"><line x1="7" y1="7" x2="17" y2="17"></line><polyline points="8 17 17 17 17 8"></polyline></svg>
            <span>Google 3D</span>
          </a>"""

    assert old_floating_buttons in content, "old_floating_buttons not found in build_conversational_atlas.py"
    content = content.replace(old_floating_buttons, new_floating_buttons, 1)

    # 6. Add bfiSpaceShowcase to #buildingFloorInspectorHud
    old_bfi_metrics = """          <!-- Building Metrics Bar -->
          <div id="bfiMetricsBar" class="flex flex-col gap-1 text-[14px] font-mono text-slate-300 py-1.5 px-2 rounded-lg bg-[#142036] border border-[#233552]">
            <span id="bfiMetricsFloors" class="text-[#7dd3fc]">3 Floors · 3,800 m²</span>
            <span id="bfiMetricsBudget" class="text-amber-400 font-bold">Budget Scale</span>
          </div>"""

    new_bfi_metrics = """          <!-- Building Metrics Bar -->
          <div id="bfiMetricsBar" class="flex flex-col gap-1 text-[14px] font-mono text-slate-300 py-1.5 px-2 rounded-lg bg-[#142036] border border-[#233552]">
            <span id="bfiMetricsFloors" class="text-[#7dd3fc]">3 Floors · 3,800 m²</span>
            <span id="bfiMetricsBudget" class="text-amber-400 font-bold">Budget Scale</span>
          </div>

          <!-- 🛰️ Real Space Photography & Google Exploration Showcase -->
          <div id="bfiSpaceShowcase" class="bg-[#0b121e] border border-[#1e324d] rounded-xl p-2.5 space-y-2 text-[14px]">
            <div class="flex items-center justify-between gap-1 text-[14px] font-mono">
              <span class="text-[#38bdf8] font-bold flex items-center gap-1.5">
                <svg class="w-3.5 h-3.5 text-emerald-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76"></polygon></svg>
                REAL SPACE &amp; SATELLITE
              </span>
              <span id="bfiSpaceTypologyBadge" class="px-1.5 py-0.2 rounded bg-sky-950 border border-sky-800 text-[#7dd3fc] text-[14px] font-mono truncate max-w-[150px]"></span>
            </div>

            <!-- Two-photo preview grid: Space Architecture Photo & Google Satellite Aerial View -->
            <div class="grid grid-cols-2 gap-2">
              <div class="relative group rounded-lg overflow-hidden border border-[#233854] bg-black/60 aspect-[4/3]">
                <img id="bfiSpacePhotoImg" src="" alt="Space Architecture" class="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105" />
                <span class="absolute bottom-1 left-1 px-1.5 py-0.5 rounded bg-black/80 backdrop-blur text-[14px] font-mono text-zinc-200 border border-white/10">Photo</span>
              </div>
              <div class="relative group rounded-lg overflow-hidden border border-[#233854] bg-black/60 aspect-[4/3]">
                <img id="bfiSatelliteAerialImg" src="" alt="Google Satellite Aerial View" class="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105" />
                <span class="absolute bottom-1 left-1 px-1.5 py-0.5 rounded bg-black/80 backdrop-blur text-[14px] font-mono text-emerald-300 border border-emerald-500/20">Satellite</span>
              </div>
            </div>

            <!-- Google Space Exploration Action Pills -->
            <div class="flex items-center gap-1.5 flex-wrap pt-0.5">
              <a id="bfiGoogleImagesBtn" href="#" target="_blank" rel="noopener noreferrer" class="atlas-pill-btn pill-sm flex-1 justify-center" style="font-size:14px; padding:3px 8px;" title="Open Google Images to see actual interior and exterior photos of this space">
                <svg class="arrow-icon" viewBox="0 0 24 24"><line x1="7" y1="7" x2="17" y2="17"></line><polyline points="8 17 17 17 17 8"></polyline></svg>
                <span>Google Images</span>
              </a>
              <a id="bfiGoogleSatelliteBtn" href="#" target="_blank" rel="noopener noreferrer" class="atlas-pill-btn pill-sm flex-1 justify-center" style="font-size:14px; padding:3px 8px;" title="Open Google Maps 3D Satellite Tilt View of this building">
                <svg class="arrow-icon" viewBox="0 0 24 24"><line x1="7" y1="7" x2="17" y2="17"></line><polyline points="8 17 17 17 17 8"></polyline></svg>
                <span>Google 3D</span>
              </a>
              <a id="bfiStreetViewBtn" href="#" target="_blank" rel="noopener noreferrer" class="atlas-pill-btn pill-sm justify-center" style="font-size:14px; padding:3px 8px;" title="Open Google Street View 360° View of this location">
                <svg class="arrow-icon" viewBox="0 0 24 24"><line x1="7" y1="7" x2="17" y2="17"></line><polyline points="8 17 17 17 17 8"></polyline></svg>
                <span>360° Street</span>
              </a>
            </div>
          </div>"""

    assert old_bfi_metrics in content, "old_bfi_metrics not found in build_conversational_atlas.py"
    content = content.replace(old_bfi_metrics, new_bfi_metrics, 1)

    # 7. Add helper functions: toggleSatelliteMode, generateDistinctFootprint, getInstitutionSpaceVisuals, renderBuilding3DMast, renderBuilding3DFacadeStack, getRoomBadgeMarkup
    helpers_code = """
    // =========================================================================
    // 🛰️ GOOGLE MAPS SATELLITE & REAL SPACE VISUALS ENGINE
    // =========================================================================
    let isSatelliteModeActive = true;
    function toggleSatelliteMode() {{
      if (!cityVectorMap) return;
      isSatelliteModeActive = !isSatelliteModeActive;
      if (typeof cityVectorMap.setLayoutProperty === 'function' && cityVectorMap.getLayer('google-satellite-layer')) {{
        cityVectorMap.setLayoutProperty(
          'google-satellite-layer',
          'visibility',
          isSatelliteModeActive ? 'visible' : 'none'
        );
      }}
      const btn = document.getElementById('toggleSatelliteMapBtn');
      if (btn) {{
        btn.classList.toggle('text-emerald-300', isSatelliteModeActive);
        btn.classList.toggle('border-emerald-500/60', isSatelliteModeActive);
        btn.classList.toggle('text-slate-400', !isSatelliteModeActive);
        btn.classList.toggle('border-[#383838]', !isSatelliteModeActive);
      }}
    }}
    window.toggleSatelliteMode = toggleSatelliteMode;

    function renderBuilding3DMast(inst) {{
      const div = document.createElement('div');
      div.className = 'building-3d-mast-plate';
      div.innerHTML = '<button type="button" class="building-mast-close-btn" onclick="window.closeBuildingMast()">×</button>';
      return div;
    }}
    window.renderBuilding3DMast = renderBuilding3DMast;

    function renderBuilding3DFacadeStack(inst) {{
      const div = document.createElement('div');
      div.className = 'building-3d-facade-stack';
      div.innerHTML = '<button type="button" class="building-facade-close-btn" onclick="window.closeBuildingFacade()">×</button>';
      return div;
    }}
    window.renderBuilding3DFacadeStack = renderBuilding3DFacadeStack;

    function getRoomBadgeMarkup(type, label) {{
      if (type === 'gallery') return '<div class="building-3d-room-badge"><span class="badge-title">EXHIBITION GALLERY</span><span>' + (label || '') + '</span></div>';
      if (type === 'archive') return '<div class="building-3d-room-badge"><span class="badge-title">ARCHIVES & STUDY</span><span>' + (label || '') + '</span></div>';
      if (type === 'atrium') return '<div class="building-3d-room-badge"><span class="badge-title">PUBLIC FORUM</span><span>' + (label || '') + '</span></div>';
      return '<div class="building-3d-room-badge">' + (label || '') + '</div>';
    }}
    window.getRoomBadgeMarkup = getRoomBadgeMarkup;

    function generateDistinctFootprint(inst, lat, lon, bArch = {{}}) {{
      const sqm = Number(bArch.footprint_sqm) || 3200;
      const latRad = (lat * Math.PI) / 180.0;
      const metersPerDegLat = 111320;
      const metersPerDegLon = 111320 * Math.max(0.15, Math.cos(latRad));

      const baseDimM = Math.max(38, Math.min(180, Math.sqrt(sqm) * 1.05));
      const halfM = baseDimM / 2;

      const style = (bArch.architectural_style || '').toLowerCase();
      const name = (inst.name || '').toLowerCase();

      let seed = 0;
      const seedStr = (inst.id || inst.name || 'atlas');
      for (let i = 0; i < seedStr.length; i++) {{
        seed = (seed * 31 + seedStr.charCodeAt(i)) & 0xffffffff;
      }}
      const prng = (offset = 0) => {{
        const s = Math.abs(seed + offset * 1337);
        return ((s ^ (s >> 15)) * 0x45d9f3b & 0x7fffffff) / 0x7fffffff;
      }};

      let typology = 'courtyard';
      if (style.includes('industrial') || style.includes('warehouse') || style.includes('carriage') || style.includes('factory') || style.includes('loft') || name.includes('turbine') || name.includes('shed') || name.includes('hangar')) {{
        typology = 'industrial_nave';
      }} else if (style.includes('rotunda') || style.includes('circular') || style.includes('dome') || style.includes('spiral') || name.includes('guggenheim') || name.includes('rotunda')) {{
        typology = 'rotunda';
      }} else if (style.includes('modernist') || style.includes('brutalist') || style.includes('deconstructivist') || style.includes('bauhaus') || style.includes('pavilion') || name.includes('kunsthalle') || name.includes('contemporary')) {{
        typology = 'l_shaped_wing';
      }} else if (style.includes('cantilever') || style.includes('stepped') || style.includes('postmodern') || name.includes('whitney') || name.includes('breuer') || name.includes('pompidou')) {{
        typology = 'stepped_cantilever';
      }} else if (style.includes('canal estate') || style.includes('civic') || style.includes('renaissance') || style.includes('monumental') || style.includes('quadrangle') || name.includes('louvre') || name.includes('palace') || name.includes('museum') || name.includes('rijksmuseum') || name.includes('uffizi')) {{
        typology = 'courtyard';
      }} else {{
        const typologies = ['courtyard', 'l_shaped_wing', 'industrial_nave', 'stepped_cantilever', 'h_campus'];
        typology = typologies[Math.abs(seed) % typologies.length];
      }}

      let localPts = [];

      if (typology === 'courtyard') {{
        const notchW = 0.44;
        const notchH = 0.52;
        localPts = [
          [-1.0, -0.9],
          [ 1.0, -0.9],
          [ 1.0,  0.9],
          [ notchW, 0.9],
          [ notchW, 0.9 - notchH],
          [-notchW, 0.9 - notchH],
          [-notchW, 0.9],
          [-1.0,  0.9],
          [-1.0, -0.9]
        ];
      }} else if (typology === 'l_shaped_wing') {{
        localPts = [
          [-1.0, -1.0],
          [ 1.0, -1.0],
          [ 1.0, -0.15],
          [-0.15, -0.15],
          [-0.15,  1.0],
          [-1.0,  1.0],
          [-1.0, -1.0]
        ];
      }} else if (typology === 'industrial_nave') {{
        localPts = [
          [-0.45, -1.1],
          [ 0.45, -1.1],
          [ 0.45, -0.55],
          [ 0.72, -0.55],
          [ 0.72,  0.55],
          [ 0.45,  0.55],
          [ 0.45,  1.1],
          [-0.45,  1.1],
          [-0.45,  0.55],
          [-0.72,  0.55],
          [-0.72, -0.55],
          [-0.45, -0.55],
          [-0.45, -1.1]
        ];
      }} else if (typology === 'stepped_cantilever') {{
        localPts = [
          [-1.0, -0.85],
          [ 0.65, -0.85],
          [ 0.65, -0.35],
          [ 1.0,  -0.35],
          [ 1.0,   0.85],
          [-0.45,  0.85],
          [-0.45,  0.45],
          [-1.0,   0.45],
          [-1.0,  -0.85]
        ];
      }} else if (typology === 'rotunda') {{
        const sides = 12;
        const r = 0.85;
        for (let i = 0; i < sides; i++) {{
          const theta = (i * 2 * Math.PI) / sides;
          localPts.push([Math.cos(theta) * r, Math.sin(theta) * r]);
        }}
        localPts.push([0.35, -1.05]);
        localPts.push([-0.35, -1.05]);
        localPts.push(localPts[0]);
      }} else {{
        localPts = [
          [-1.0, -1.0],
          [-0.4, -1.0],
          [-0.4, -0.25],
          [ 0.4, -0.25],
          [ 0.4, -1.0],
          [ 1.0, -1.0],
          [ 1.0,  1.0],
          [ 0.4,  1.0],
          [ 0.4,  0.25],
          [-0.4,  0.25],
          [-0.4,  1.0],
          [-1.0,  1.0],
          [-1.0, -1.0]
        ];
      }}

      const angleDeg = ((prng(2) * 50) - 25);
      const angleRad = (angleDeg * Math.PI) / 180.0;
      const cosA = Math.cos(angleRad);
      const sinA = Math.sin(angleRad);

      const coords = localPts.map(pt => {{
        const xM = pt[0] * halfM;
        const yM = pt[1] * halfM;
        const rotX = xM * cosA - yM * sinA;
        const rotY = xM * sinA + yM * cosA;
        const pLon = lon + rotX / metersPerDegLon;
        const pLat = lat + rotY / metersPerDegLat;
        return [Number(pLon.toFixed(7)), Number(pLat.toFixed(7))];
      }});

      return {{ coords, typology, angleDeg, sqm }};
    }}
    window.generateDistinctFootprint = generateDistinctFootprint;

    function getInstitutionSpaceVisuals(inst) {{
      if (!inst) return null;
      const name = inst.name || 'Institution';
      const city = inst.city || '';
      const lat = Number(inst.lat) || 0;
      const lon = Number(inst.lon) || 0;
      const bArch = inst.building_architecture || {{}};
      const style = bArch.architectural_style || 'Curatorial Space';

      let satelliteTileUrl = '';
      if (lat && lon) {{
        const zoom = 17;
        const n = Math.pow(2, zoom);
        const x = Math.floor(((lon + 180) / 360) * n);
        const latRad = (lat * Math.PI) / 180;
        const y = Math.floor(((1 - Math.asinh(Math.tan(latRad)) / Math.PI) / 2) * n);
        satelliteTileUrl = `https://mt1.google.com/vt/lyrs=s&x=${{x}}&y=${{y}}&z=${{zoom}}`;
      }}

      const PHOTO_REGISTRY = {{
        'tate modern': 'https://images.unsplash.com/photo-1541961017774-22349e4a1262?auto=format&fit=crop&w=800&q=80',
        'musée du louvre': 'https://images.unsplash.com/photo-1565008447742-97f6f38c985c?auto=format&fit=crop&w=800&q=80',
        'louvre': 'https://images.unsplash.com/photo-1565008447742-97f6f38c985c?auto=format&fit=crop&w=800&q=80',
        'centre pompidou': 'https://images.unsplash.com/photo-1502602898657-3e91760cbb34?auto=format&fit=crop&w=800&q=80',
        'moma': 'https://images.unsplash.com/photo-1568605117036-5fe5e7bab0b7?auto=format&fit=crop&w=800&q=80',
        'stedelijk': 'https://images.unsplash.com/photo-1518998053901-5348d3961a04?auto=format&fit=crop&w=800&q=80',
        'british museum': 'https://images.unsplash.com/photo-1582555172866-f73bb12a2ab3?auto=format&fit=crop&w=800&q=80',
        'whitechapel': 'https://images.unsplash.com/photo-1577717903315-1691ae25ab3f?auto=format&fit=crop&w=800&q=80',
        'chisenhale': 'https://images.unsplash.com/photo-1513364776144-60967b0f800f?auto=format&fit=crop&w=800&q=80',
        'guggenheim': 'https://images.unsplash.com/photo-1580136579312-94651dfd596d?auto=format&fit=crop&w=800&q=80',
        'hayward': 'https://images.unsplash.com/photo-1554907984-15263bfd63bd?auto=format&fit=crop&w=800&q=80',
        'macba': 'https://images.unsplash.com/photo-1579783900882-c0d3dad7b119?auto=format&fit=crop&w=800&q=80',
        'palais de tokyo': 'https://images.unsplash.com/photo-1579783902614-a3fb3927b675?auto=format&fit=crop&w=800&q=80',
        'wiels': 'https://images.unsplash.com/photo-1518998053901-5348d3961a04?auto=format&fit=crop&w=800&q=80',
        'casco': 'https://images.unsplash.com/photo-1513364776144-60967b0f800f?auto=format&fit=crop&w=800&q=80'
      }};

      const normName = name.toLowerCase();
      let photoUrl = '';
      for (const [key, val] of Object.entries(PHOTO_REGISTRY)) {{
        if (normName.includes(key)) {{
          photoUrl = val;
          break;
        }}
      }}
      if (!photoUrl) {{
        const TYPOLOGY_PHOTOS = {{
          industrial: 'https://images.unsplash.com/photo-1513364776144-60967b0f800f?auto=format&fit=crop&w=800&q=80',
          modernist: 'https://images.unsplash.com/photo-1554907984-15263bfd63bd?auto=format&fit=crop&w=800&q=80',
          courtyard: 'https://images.unsplash.com/photo-1582555172866-f73bb12a2ab3?auto=format&fit=crop&w=800&q=80',
          rotunda: 'https://images.unsplash.com/photo-1580136579312-94651dfd596d?auto=format&fit=crop&w=800&q=80',
          contemporary: 'https://images.unsplash.com/photo-1579783900882-c0d3dad7b119?auto=format&fit=crop&w=800&q=80'
        }};
        const sLower = style.toLowerCase();
        if (sLower.includes('industrial') || sLower.includes('warehouse') || sLower.includes('carriage')) {{
          photoUrl = TYPOLOGY_PHOTOS.industrial;
        }} else if (sLower.includes('modernist') || sLower.includes('brutalist')) {{
          photoUrl = TYPOLOGY_PHOTOS.modernist;
        }} else if (sLower.includes('rotunda') || sLower.includes('circular')) {{
          photoUrl = TYPOLOGY_PHOTOS.rotunda;
        }} else if (sLower.includes('courtyard') || sLower.includes('palace') || sLower.includes('estate') || sLower.includes('renaissance')) {{
          photoUrl = TYPOLOGY_PHOTOS.courtyard;
        }} else {{
          photoUrl = TYPOLOGY_PHOTOS.contemporary;
        }}
      }}

      const googleImagesUrl = `https://www.google.com/search?tbm=isch&q=${{encodeURIComponent(name + ' ' + city + ' museum architecture interior')}}`;
      const googleMaps3dUrl = `https://www.google.com/maps/@${{lat}},${{lon}},160m/data=!3m1!1e3`;
      const googleStreetViewUrl = `https://www.google.com/maps/@?api=1&map_action=pano&viewpoint=${{lat}},${{lon}}`;

      return {{
        photoUrl,
        satelliteTileUrl,
        googleImagesUrl,
        googleMaps3dUrl,
        googleStreetViewUrl,
        typology: bArch.architectural_style || 'Curatorial Space'
      }};
    }}
    window.getInstitutionSpaceVisuals = getInstitutionSpaceVisuals;
"""

    old_fn_anchor = "    function ensureBuildingFootprintLayer() {{"
    assert old_fn_anchor in content, "old_fn_anchor not found in build_conversational_atlas.py"
    content = content.replace(old_fn_anchor, helpers_code + "\n" + old_fn_anchor, 1)

    # 8. Update highlightBuildingFootprint to use generateDistinctFootprint
    old_footprint_calc = """      const sqm = bArch.footprint_sqm || 2400;
      const d_lat = 0.00045 * (Math.sqrt(sqm) / 50.0);
      const d_lon = 0.00065 * (Math.sqrt(sqm) / 50.0);

      let coords = bArch.footprint_coordinates;
      if (!coords || coords.length < 4) {{
        coords = [
          [lon - d_lon, lat - d_lat],
          [lon + d_lon, lat - d_lat],
          [lon + d_lon, lat + d_lat],
          [lon - d_lon, lat + d_lat],
          [lon - d_lon, lat - d_lat]
        ];
      }}"""

    new_footprint_calc = """      const distinctFootprint = generateDistinctFootprint(inst, lat, lon, bArch);
      let coords = (bArch.footprint_coordinates && bArch.footprint_coordinates.length > 5)
        ? bArch.footprint_coordinates
        : distinctFootprint.coords;
      const sqm = distinctFootprint.sqm;"""

    assert old_footprint_calc in content, "old_footprint_calc not found in build_conversational_atlas.py"
    content = content.replace(old_footprint_calc, new_footprint_calc, 1)

    # 9. Update showBuildingFloorInspectorHud to populate bfiSpaceShowcase
    old_hud_populate = """      // Populate active floor details
      const activeFl = floors[currentBfiFloorIndex] || floors[0];"""

    new_hud_populate = """      // Populate Space Visuals & Google Exploration Showcase
      const spaceVisuals = getInstitutionSpaceVisuals(inst);
      if (spaceVisuals) {{
        const photoEl = document.getElementById('bfiSpacePhotoImg');
        const satEl = document.getElementById('bfiSatelliteAerialImg');
        const gImgBtn = document.getElementById('bfiGoogleImagesBtn');
        const gSatBtn = document.getElementById('bfiGoogleSatelliteBtn');
        const gStBtn = document.getElementById('bfiStreetViewBtn');
        const badgeEl = document.getElementById('bfiSpaceTypologyBadge');

        if (photoEl) {{
          photoEl.src = spaceVisuals.photoUrl;
          photoEl.alt = `${{inst.name}} space photography`;
        }}
        if (satEl) {{
          satEl.src = spaceVisuals.satelliteTileUrl;
          satEl.alt = `${{inst.name}} Google Satellite aerial view`;
        }}
        if (gImgBtn) gImgBtn.href = spaceVisuals.googleImagesUrl;
        if (gSatBtn) gSatBtn.href = spaceVisuals.googleMaps3dUrl;
        if (gStBtn) gStBtn.href = spaceVisuals.googleStreetViewUrl;
        if (badgeEl) badgeEl.textContent = spaceVisuals.typology;
      }}

      // Populate active floor details
      const activeFl = floors[currentBfiFloorIndex] || floors[0];"""

    assert old_hud_populate in content, "old_hud_populate not found in build_conversational_atlas.py"
    content = content.replace(old_hud_populate, new_hud_populate, 1)

    # 10. Update selectInstitution to populate floating card Google buttons
    old_select_inst = """      const isCardClean = inst.tier === 'A';
      const isCardFlagged = inst.tier === 'B';
      document.getElementById('floatingCardMeta').textContent = `${{inst.location}} · ${{isCardClean ? 'Clean Verified' : isCardFlagged ? 'Flagged Underwriting' : 'Roster Unverified'}}`;"""

    new_select_inst = """      const spaceVisuals = getInstitutionSpaceVisuals(inst);
      if (spaceVisuals) {{
        const gImgBtn = document.getElementById('floatingCardGoogleImagesBtn');
        const gSatBtn = document.getElementById('floatingCardGoogleMaps3dBtn');
        if (gImgBtn) gImgBtn.href = spaceVisuals.googleImagesUrl;
        if (gSatBtn) gSatBtn.href = spaceVisuals.googleMaps3dUrl;
      }}

      const isCardClean = inst.tier === 'A';
      const isCardFlagged = inst.tier === 'B';
      document.getElementById('floatingCardMeta').textContent = `${{inst.location}} · ${{isCardClean ? 'Clean Verified' : isCardFlagged ? 'Flagged Underwriting' : 'Roster Unverified'}}`;"""

    assert old_select_inst in content, "old_select_inst not found in build_conversational_atlas.py"
    content = content.replace(old_select_inst, new_select_inst, 1)

    with open(target, 'w', encoding='utf-8') as f:
        f.write(content)

    print("✅ Successfully patched build_conversational_atlas.py with Google Satellite & Images engine!")

if __name__ == '__main__':
    main()
