import re

def main():
    with open('build_conversational_atlas.py', 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Add #globeCityBar inside #globeViewport right before <!-- Subtle Globe Zoom Controls -->
    old_zoom_html = """      <!-- Subtle Globe Zoom Controls -->
      <div class="absolute bottom-2 right-2.5 sm:right-4 z-10 flex items-center gap-1.5">
        <button id="zoomInBtn" class="w-7 h-7 sm:w-8 sm:h-8 rounded-xl bg-[#212121]/90 border border-[#2e2e2e] text-[#d4d4d4] hover:text-white flex items-center justify-center transition shadow-sm text-[14px] cursor-pointer" title="Zoom In">+</button>
        <button id="zoomOutBtn" class="w-7 h-7 sm:w-8 sm:h-8 rounded-xl bg-[#212121]/90 border border-[#2e2e2e] text-[#d4d4d4] hover:text-white flex items-center justify-center transition shadow-sm text-[14px] cursor-pointer" title="Zoom Out">−</button>
      </div>"""

    new_city_bar_and_zoom = """      <!-- Interactive City & Country Quick Bar -->
      <div id="globeCityBar" class="absolute bottom-2 left-2.5 sm:left-4 right-20 sm:right-24 z-10 flex items-center overflow-x-auto custom-scrollbar whitespace-nowrap gap-1.5 select-none pointer-events-auto">
        <button class="globe-filter-pill px-2.5 py-1 rounded-xl bg-[#2563eb] text-white border border-[#60a5fa] transition cursor-pointer text-[13px] shrink-0" data-type="all">🌐 All</button>
        <span class="text-[#555] shrink-0">·</span>
        <button class="globe-filter-pill px-2.5 py-1 rounded-xl bg-[#212121]/90 hover:bg-[#2a2a2a] border border-[#2e2e2e] text-[#d4d4d4] hover:text-white transition cursor-pointer text-[13px] shrink-0" data-type="city" data-value="Utrecht">🇳🇱 Utrecht</button>
        <button class="globe-filter-pill px-2.5 py-1 rounded-xl bg-[#212121]/90 hover:bg-[#2a2a2a] border border-[#2e2e2e] text-[#d4d4d4] hover:text-white transition cursor-pointer text-[13px] shrink-0" data-type="city" data-value="Amsterdam">🇳🇱 Amsterdam</button>
        <button class="globe-filter-pill px-2.5 py-1 rounded-xl bg-[#212121]/90 hover:bg-[#2a2a2a] border border-[#2e2e2e] text-[#d4d4d4] hover:text-white transition cursor-pointer text-[13px] shrink-0" data-type="city" data-value="Rotterdam">🇳🇱 Rotterdam</button>
        <button class="globe-filter-pill px-2.5 py-1 rounded-xl bg-[#212121]/90 hover:bg-[#2a2a2a] border border-[#2e2e2e] text-[#d4d4d4] hover:text-white transition cursor-pointer text-[13px] shrink-0" data-type="city" data-value="London">🇬🇧 London</button>
        <button class="globe-filter-pill px-2.5 py-1 rounded-xl bg-[#212121]/90 hover:bg-[#2a2a2a] border border-[#2e2e2e] text-[#d4d4d4] hover:text-white transition cursor-pointer text-[13px] shrink-0" data-type="city" data-value="New York">🇺🇸 New York</button>
        <button class="globe-filter-pill px-2.5 py-1 rounded-xl bg-[#212121]/90 hover:bg-[#2a2a2a] border border-[#2e2e2e] text-[#d4d4d4] hover:text-white transition cursor-pointer text-[13px] shrink-0" data-type="city" data-value="Paris">🇫🇷 Paris</button>
        <button class="globe-filter-pill px-2.5 py-1 rounded-xl bg-[#212121]/90 hover:bg-[#2a2a2a] border border-[#2e2e2e] text-[#d4d4d4] hover:text-white transition cursor-pointer text-[13px] shrink-0" data-type="city" data-value="Berlin">🇩🇪 Berlin</button>
        <button class="globe-filter-pill px-2.5 py-1 rounded-xl bg-[#212121]/90 hover:bg-[#2a2a2a] border border-[#2e2e2e] text-[#d4d4d4] hover:text-white transition cursor-pointer text-[13px] shrink-0" data-type="city" data-value="Tokyo">🇯🇵 Tokyo</button>
        <span class="text-[#555] shrink-0">·</span>
        <button class="globe-filter-pill px-2.5 py-1 rounded-xl bg-[#212121]/90 hover:bg-[#2a2a2a] border border-[#2e2e2e] text-[#d4d4d4] hover:text-white transition cursor-pointer text-[13px] shrink-0" data-type="country" data-value="Netherlands">Netherlands</button>
        <button class="globe-filter-pill px-2.5 py-1 rounded-xl bg-[#212121]/90 hover:bg-[#2a2a2a] border border-[#2e2e2e] text-[#d4d4d4] hover:text-white transition cursor-pointer text-[13px] shrink-0" data-type="country" data-value="United Kingdom">United Kingdom</button>
        <button class="globe-filter-pill px-2.5 py-1 rounded-xl bg-[#212121]/90 hover:bg-[#2a2a2a] border border-[#2e2e2e] text-[#d4d4d4] hover:text-white transition cursor-pointer text-[13px] shrink-0" data-type="country" data-value="United States">United States</button>
        <button class="globe-filter-pill px-2.5 py-1 rounded-xl bg-[#212121]/90 hover:bg-[#2a2a2a] border border-[#2e2e2e] text-[#d4d4d4] hover:text-white transition cursor-pointer text-[13px] shrink-0" data-type="country" data-value="France">France</button>
        <button class="globe-filter-pill px-2.5 py-1 rounded-xl bg-[#212121]/90 hover:bg-[#2a2a2a] border border-[#2e2e2e] text-[#d4d4d4] hover:text-white transition cursor-pointer text-[13px] shrink-0" data-type="country" data-value="Germany">Germany</button>
      </div>

      <!-- Subtle Globe Zoom Controls -->
      <div class="absolute bottom-2 right-2.5 sm:right-4 z-10 flex items-center gap-1.5">
        <button id="zoomInBtn" class="w-7 h-7 sm:w-8 sm:h-8 rounded-xl bg-[#212121]/90 border border-[#2e2e2e] text-[#d4d4d4] hover:text-white flex items-center justify-center transition shadow-sm text-[14px] cursor-pointer" title="Zoom In">+</button>
        <button id="zoomOutBtn" class="w-7 h-7 sm:w-8 sm:h-8 rounded-xl bg-[#212121]/90 border border-[#2e2e2e] text-[#d4d4d4] hover:text-white flex items-center justify-center transition shadow-sm text-[14px] cursor-pointer" title="Zoom Out">−</button>
      </div>"""

    if old_zoom_html in content:
        content = content.replace(old_zoom_html, new_city_bar_and_zoom)
        print("Added #globeCityBar")
    else:
        print("WARNING: old_zoom_html not found")

    # 2. Add query handler for "Show me all cities mapped in Culture Atlas" and "countries"
    old_shelf_target = """        // Exact Prompt 1: Find independent art spaces near me"""

    new_shelf_handlers = """        // All Cities Mapped Query Handler (from Choose project shelf pill)
        if (q.includes('cities mapped') || q.includes('all cities') || q.includes('show me all cities') || q.includes('which cities') || q.includes('list of cities') || q.includes('choose project')) {{
          const sorted = [...PRIORITY_CITIES];
          const cityPills = sorted.map(c => {{
            const count = ALL_INSTITUTIONS.filter(i => matchC(i.city, c.name)).length;
            return `<button class="city-zoom-btn px-2.5 py-1 rounded-xl bg-[#262626] hover:bg-[#333] border border-[#383838] hover:border-[#60a5fa] text-white text-[13px] transition cursor-pointer inline-flex items-center gap-1.5" data-city="${{escapeHtml(c.name)}}"><span>📍</span> <span>${{escapeHtml(c.name)}}</span> <span class="text-[#93c5fd] font-mono text-[12px]">(${{count}})</span></button>`;
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
            return `<button class="country-zoom-btn px-2.5 py-1 rounded-xl bg-[#262626] hover:bg-[#333] border border-[#383838] hover:border-[#60a5fa] text-white text-[13px] transition cursor-pointer inline-flex items-center gap-1.5" data-country="${{escapeHtml(c.name)}}"><span>🌍</span> <span>${{escapeHtml(c.name)}}</span> <span class="text-[#93c5fd] font-mono text-[12px]">(${{count}})</span></button>`;
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

        // Exact Prompt 1: Find independent art spaces near me"""

    if old_shelf_target in content:
        content = content.replace(old_shelf_target, new_shelf_handlers)
        print("Added cities/countries query handlers")
    else:
        print("WARNING: old_shelf_target not found")

    # 3. Add country-link handler in curatorMessages delegation
    old_delegation_city = """      // 3. Check for city links
      const cityLink = e.target.closest('.city-link, .city-zoom-btn, [data-city]');
      if (cityLink) {{
        e.preventDefault();
        e.stopPropagation();
        const city = cityLink.getAttribute('data-city') || cityLink.textContent.trim();
        if (city) {{
          filterByCity(city, true, false);
        }}
        return;
      }}"""

    new_delegation_city_and_country = """      // 3. Check for city links
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
      }}"""

    if old_delegation_city in content:
        content = content.replace(old_delegation_city, new_delegation_city_and_country)
        print("Added country-link handler in curatorMessages")
    else:
        print("WARNING: old_delegation_city not found")

    # 4. Clean up missing variable bindings and apply safe null guards in catalog list & filtering engine
    old_catalog_engine = """    // =========================================================
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
    populateDropdowns();"""

    new_catalog_engine = """    // =========================================================
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
      document.querySelectorAll('.globe-filter-pill').forEach(pill => {{
        const type = pill.getAttribute('data-type');
        const val = pill.getAttribute('data-value') || '';
        let isAct = false;
        if (type === 'all' && selectedCityFilter === 'all' && selectedCountryFilter === 'all') isAct = true;
        else if (type === 'city' && selectedCityFilter.toLowerCase() === val.toLowerCase()) isAct = true;
        else if (type === 'country' && selectedCountryFilter.toLowerCase() === val.toLowerCase()) isAct = true;

        if (isAct) {{
          pill.className = 'globe-filter-pill px-2.5 py-1 rounded-xl bg-[#2563eb] text-white border border-[#60a5fa] transition cursor-pointer text-[13px] shrink-0 shadow-sm';
        }} else {{
          pill.className = 'globe-filter-pill px-2.5 py-1 rounded-xl bg-[#212121]/90 hover:bg-[#2a2a2a] border border-[#2e2e2e] text-[#d4d4d4] hover:text-white transition cursor-pointer text-[13px] shrink-0';
        }}
      }});
    }}

    // Wire Globe Filter Pills (Quick click city or country)
    document.querySelectorAll('.globe-filter-pill').forEach(pill => {{
      pill.addEventListener('click', () => {{
        const type = pill.getAttribute('data-type');
        const val = pill.getAttribute('data-value') || '';
        if (type === 'all') {{
          clearAllFilters();
        }} else if (type === 'city') {{
          filterByCity(val, true, true);
        }} else if (type === 'country') {{
          filterByCountry(val);
        }}
      }});
    }});"""

    if old_catalog_engine in content:
        content = content.replace(old_catalog_engine, new_catalog_engine)
        print("Updated catalog engine and added globe pills UI")
    else:
        print("WARNING: old_catalog_engine not found")

    # 5. Fix applyFilters and renderLeftList to safely guard missing elements
    old_apply_tail = """      listTotalBadge.textContent = `${{filteredList.length}} mapped`;

      // Update Floating Map Filter Banner
      const activeMapBanner = document.getElementById('activeMapFilterBanner');
      const activeMapIcon = document.getElementById('activeMapFilterIcon');
      const activeMapText = document.getElementById('activeMapFilterText');

      if (activeMapBanner && activeMapText) {{
        if (selectedCategoryFilter !== 'all') {{
          activeMapBanner.classList.remove('hidden');
          const meta = FILTER_META[selectedCategoryFilter] || {{ icon: '📍', label: selectedCategoryFilter.toUpperCase() }};
          activeMapIcon.textContent = meta.icon;
          activeMapText.textContent = `${{meta.label}} · ${{filteredList.length}} SPACES ON MAP`;
        }} else {{
          activeMapBanner.classList.add('hidden');
        }}
      }}

      // Update Catalog Panel Banner
      if (selectedCityFilter !== 'all' || selectedCountryFilter !== 'all' || selectedCategoryFilter !== 'all') {{
        activeFilterBanner.classList.remove('hidden');
        let activeName = selectedCityFilter !== 'all' ? selectedCityFilter : (selectedCountryFilter !== 'all' ? selectedCountryFilter : selectedCategoryFilter);
        if (FILTER_META[selectedCategoryFilter]) activeName = FILTER_META[selectedCategoryFilter].label;
        filterLabel.textContent = activeName.toUpperCase();
        filterCount.textContent = `(${{filteredList.length}})`;
      }} else {{
        activeFilterBanner.classList.add('hidden');
      }}

      renderLeftList();
    }}"""

    new_apply_tail = """      const listTotalBadge = document.getElementById('listTotalBadge');
      if (listTotalBadge) listTotalBadge.textContent = `${{filteredList.length}} mapped`;

      // Update Floating Map Filter Banner
      const activeMapBanner = document.getElementById('activeMapFilterBanner');
      const activeMapIcon = document.getElementById('activeMapFilterIcon');
      const activeMapText = document.getElementById('activeMapFilterText');

      if (activeMapBanner && activeMapText) {{
        if (selectedCategoryFilter !== 'all') {{
          activeMapBanner.classList.remove('hidden');
          const meta = FILTER_META[selectedCategoryFilter] || {{ icon: '📍', label: selectedCategoryFilter.toUpperCase() }};
          activeMapIcon.textContent = meta.icon;
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
    }}"""

    if old_apply_tail in content:
        content = content.replace(old_apply_tail, new_apply_tail)
        print("Guarded applyFilters missing element references")
    else:
        print("WARNING: old_apply_tail not found")

    # 6. Fix clearAllFilters, filter event listeners, and clearFilterBtn
    old_filter_listeners = """    function clearAllFilters() {{
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

    clearFilterBtn.addEventListener('click', clearAllFilters);"""

    new_filter_listeners = """    function clearAllFilters() {{
      selectedCityFilter = 'all';
      selectedCountryFilter = 'all';
      selectedCategoryFilter = 'all';
      searchQuery = '';
      if (searchInput) searchInput.value = '';
      selectedTierFilter = new Set(['A', 'B', 'U']);
      document.querySelectorAll('.tier-chip').forEach(btn => {{
        btn.classList.add('bg-[#0c2419]', 'bg-[#0e213b]', 'bg-[#171a24]');
      }});
      if (countrySelect) countrySelect.value = 'all';
      if (citySelect) citySelect.value = 'all';
      targetRadius = baseRadius;
      isAutoSpinning = true;
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

    document.getElementById('clearSearchBtn')?.addEventListener('click', () => {{
      if (searchInput) searchInput.value = '';
      searchQuery = '';
      applyFilters();
    }});

    document.getElementById('clearFilterBtn')?.addEventListener('click', clearAllFilters);"""

    if old_filter_listeners in content:
        content = content.replace(old_filter_listeners, new_filter_listeners)
        print("Updated filter listeners and clearAllFilters")
    else:
        print("WARNING: old_filter_listeners not found")

    # 7. Fix canvas pointer events, click handler, and hit-testing
    old_pointer_block = """    // =========================================================
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
        if (Math.hypot(d.x - mx, d.y - my) < 9) {{
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
    }}"""

    new_pointer_block = """    // =========================================================
    // 🌐 CANVAS POINTER & HIT-TESTING (Click City / Country)
    // =========================================================
    function handleGlobeClick(clientX, clientY) {{
      const rect = canvas.getBoundingClientRect();
      const mx = clientX - rect.left;
      const my = clientY - rect.top;
      const cx = width / 2;
      const cy = height / 2;
      const r = currentRadius;

      // 1. Check priority city hitboxes with generous 12px hit padding
      for (let i = 0; i < cityBadgeHitboxes.length; i++) {{
        const b = cityBadgeHitboxes[i];
        if (mx >= b.x - 12 && mx <= b.x + b.w + 12 && my >= b.y - 10 && my <= b.y + b.h + 10) {{
          if (selectedCityFilter.toLowerCase() === b.name.toLowerCase()) {{
            clearAllFilters();
          }} else {{
            filterByCity(b.name, true, true);
          }}
          return;
        }}
      }}

      // 2. Check institution dots (14px radius)
      for (let i = 0; i < visibleDots.length; i++) {{
        const d = visibleDots[i];
        if (Math.hypot(d.x - mx, d.y - my) < 14) {{
          selectInstitution(d.inst);
          return;
        }}
      }}

      // 3. Check country centroid text (generous 36px radius for easy clicking)
      for (let i = 0; i < COUNTRY_CENTROIDS.length; i++) {{
        const c = COUNTRY_CENTROIDS[i];
        const pt = project(c.lon, c.lat, r, cx, cy);
        if (pt.front && Math.hypot(pt.x - mx, pt.y - my) < 36) {{
          if (selectedCountryFilter.toLowerCase() === c.name.toLowerCase()) {{
            clearAllFilters();
          }} else {{
            filterByCountry(c.name);
          }}
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

      // Check city badge
      for (let i = 0; i < cityBadgeHitboxes.length; i++) {{
        const b = cityBadgeHitboxes[i];
        if (mx >= b.x - 12 && mx <= b.x + b.w + 12 && my >= b.y - 10 && my <= b.y + b.h + 10) {{
          canvas.style.cursor = 'pointer';
          return;
        }}
      }}

      // Check institution dot
      for (let i = 0; i < visibleDots.length; i++) {{
        const d = visibleDots[i];
        if (Math.hypot(d.x - mx, d.y - my) < 14) {{
          canvas.style.cursor = 'pointer';
          return;
        }}
      }}

      // Check country centroid
      for (let i = 0; i < COUNTRY_CENTROIDS.length; i++) {{
        const c = COUNTRY_CENTROIDS[i];
        const pt = project(c.lon, c.lat, r, cx, cy);
        if (pt.front && Math.hypot(pt.x - mx, pt.y - my) < 36) {{
          canvas.style.cursor = 'pointer';
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
    }});"""

    if old_pointer_block in content:
        content = content.replace(old_pointer_block, new_pointer_block)
        print("Updated pointer and click handlers on canvas")
    else:
        print("WARNING: old_pointer_block not found")

    # 8. Fix window pointermove, pointerdown, and zoom buttons at end of script
    old_tail = """    document.getElementById('zoomInBtn').addEventListener('click', () => {{
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
    }});"""

    new_tail = """    document.getElementById('zoomInBtn')?.addEventListener('click', () => {{
      targetRadius = Math.min(getMaxRadius(), targetRadius * 1.32);
    }});
    document.getElementById('zoomOutBtn')?.addEventListener('click', () => {{
      targetRadius = Math.max(getMinRadius(), targetRadius * 0.76);
    }});
    document.getElementById('topResetBtn')?.addEventListener('click', () => {{
      targetRadius = baseRadius;
      flyTo(5.2, 52.1);
      clearAllFilters();
    }});"""

    if old_tail in content:
        content = content.replace(old_tail, new_tail)
        print("Updated zoom and reset button listeners safely")
    else:
        print("WARNING: old_tail not found")

    # 9. Fix pointerup in drag section to avoid strict distance/time drop
    old_pointer_down_block = """    canvas.addEventListener('pointerdown', e => {{
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
    }});"""

    new_pointer_down_block = """    canvas.addEventListener('pointerdown', e => {{
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

    window.addEventListener('pointerup', e => {{
      if (isDragging) {{
        isDragging = false;
        canvas.classList.remove('dragging');
      }}
    }});"""

    if old_pointer_down_block in content:
        content = content.replace(old_pointer_down_block, new_pointer_down_block)
        print("Updated pointerdown and pointermove window listeners")
    else:
        print("WARNING: old_pointer_down_block not found")

    with open('build_conversational_atlas.py', 'w', encoding='utf-8') as f:
        f.write(content)

    print("SUCCESS: Patched build_conversational_atlas.py!")

if __name__ == '__main__':
    main()
