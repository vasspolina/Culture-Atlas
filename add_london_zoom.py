#!/usr/bin/env python3
"""
add_london_zoom.py
Adds smooth camera fly-to and zoom-in (targetRadius = baseRadius * 2.5) when London (or any city) is clicked in chat.
"""
import re

with open('build_conversational_atlas.py', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Update inquiry chip for London (and other cities) with data-city
text = text.replace(
    'data-query="Recommend verified cultural spaces in London">',
    'data-query="Recommend verified cultural spaces in London" data-city="London">'
)
text = text.replace(
    'data-query="Recommend verified cultural spaces in New York">',
    'data-query="Recommend verified cultural spaces in New York" data-city="New York">'
)
text = text.replace(
    'data-query="Recommend verified cultural spaces in Tokyo">',
    'data-query="Recommend verified cultural spaces in Tokyo" data-city="Tokyo">'
)
text = text.replace(
    'data-query="Recommend verified cultural spaces in Paris">',
    'data-query="Recommend verified cultural spaces in Paris" data-city="Paris">'
)

# 2. Update flyTo function to support optional targetZoom
old_flyto = """    function flyTo(lon, lat) {
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
    }"""

new_flyto = """    function flyTo(lon, lat, targetZoom = null) {
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

      if (targetZoom) {
        targetRadius = Math.max(getMinRadius(), Math.min(getMaxRadius(), targetZoom));
      }
    }"""

# Handle {{ and }} in python f-string
old_flyto_escaped = old_flyto.replace("{", "{{").replace("}", "}}")
new_flyto_escaped = new_flyto.replace("{", "{{").replace("}", "}}")

if old_flyto_escaped in text:
    text = text.replace(old_flyto_escaped, new_flyto_escaped)
    print("Updated flyTo function")
else:
    print("Warning: old_flyto not found exactly, using regex")
    text = re.sub(
        r'function flyTo\(lon,\s*lat\)\s*\{\{.*?isFlying = true;\s*\}\}',
        new_flyto_escaped.strip(),
        text,
        flags=re.DOTALL
    )

# 3. Update selectInstitution to support zoom
old_select = """      flyTo(inst.lon, inst.lat);"""
new_select = """      if (shouldSwitchToGlobe) {{
        targetRadius = Math.max(targetRadius, baseRadius * 2.5);
        if (currentSheetState === 'full') setChatSheetState('half');
      }}
      flyTo(inst.lon, inst.lat, shouldSwitchToGlobe ? baseRadius * 2.5 : null);"""

if old_select in text:
    text = text.replace(old_select, new_select, 1)
    print("Updated selectInstitution to zoom in when requested")

# 4. Update filterByCity function to zoom in on the city and support notifyCurator flag
old_filter_city = """    function filterByCity(cityName) {{
      selectedCityFilter = cityName;
      selectedCountryFilter = 'all';
      applyFilters();

      const cty = PRIORITY_CITIES.find(c => c.name.toLowerCase() === cityName.toLowerCase());
      if (cty) flyTo(cty.lon, cty.lat);
      else {{
        const inst = ALL_INSTITUTIONS.find(i => i.city.toLowerCase() === cityName.toLowerCase());
        if (inst) flyTo(inst.lon, inst.lat);
      }}

      // Notify the Curator to give an educational briefing on this city
      const cityMatches = ALL_INSTITUTIONS.filter(i => matchC(i.city, cityName));
      if (cityMatches.length > 0) {{
        appendCuratorMessage(`
          <p>📍 <strong>${{cityName.toUpperCase()}} Cultural Landscape:</strong></p>
          <p>You selected <strong>${{cityName}}</strong> with ${{cityMatches.length}} mapped institutions. These spaces lead in ethical funding and independent programming.</p>
        `, cityMatches.slice(0, 3));
      }}
    }}"""

new_filter_city = """    function filterByCity(cityName, zoom = true, notifyCurator = true) {{
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
    }}"""

if old_filter_city in text:
    text = text.replace(old_filter_city, new_filter_city)
    print("Updated filterByCity with zoom support")
else:
    print("Warning: old_filter_city not found exactly")

# 5. In handleCuratorQuery: city branch should call filterByCity(targetCity, true, false) and have zoom button
old_city_query = """          if (cityMatches.length > 0) {{
            const targetCity = cityMatches[0].city;
            appendCuratorMessage(`
              <p>📍 <strong>Ethical Cultural Guide for ${{escapeHtml(targetCity)}}:</strong></p>
              <p>We have <strong>${{cityMatches.length}}</strong> ethically vetted cultural institutions mapped in ${{escapeHtml(targetCity)}}. These spaces operate with transparent public funding and verified independence from controversial corporate donors.</p>
              <p class="text-slate-300">Here are our top recommendations to explore:</p>
            `, cityMatches.slice(0, 4));

            flyTo(cityMatches[0].lon, cityMatches[0].lat);
            return;
          }}"""

new_city_query = """          if (cityMatches.length > 0) {{
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
          }}"""

if old_city_query in text:
    text = text.replace(old_city_query, new_city_query)
    print("Updated handleCuratorQuery city branch with automatic zoom")
else:
    print("Warning: old_city_query not found exactly")

# 6. Update inquiry chips listener to zoom immediately if city is present or mentioned
old_inquiry_listener = """    // Inquiry Chips
    document.querySelectorAll('.inquiry-chip').forEach(btn => {{
      btn.addEventListener('click', () => {{
        const q = btn.getAttribute('data-query');
        if (q) {{
          if (q.toLowerCase().includes('moma')) {{
            openMomaAuditModal();
          }}
          appendUserMessage(q);
          handleCuratorQuery(q);
        }}
      }});
    }});"""

new_inquiry_listener = """    // Inquiry Chips
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
    }});"""

if old_inquiry_listener in text:
    text = text.replace(old_inquiry_listener, new_inquiry_listener)
    print("Updated inquiry chips and added chat delegated click listener for London zoom")
else:
    print("Warning: old_inquiry_listener not found exactly")

with open('build_conversational_atlas.py', 'w', encoding='utf-8') as f:
    f.write(text)

print("build_conversational_atlas.py updated with London zoom capability!")
