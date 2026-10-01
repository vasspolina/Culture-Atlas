import re

def update_map_filters():
    with open("build_conversational_atlas.py", "r", encoding="utf-8") as f:
        src = f.read()

    # 1. Add activeMapFilterBanner on globeViewport (around line 433)
    old_top_controls = """      <!-- Top-Right Globe Map Controls & Reset -->
      <div class="absolute top-2.5 right-2.5 sm:top-3 sm:right-4 z-10 flex items-center gap-1.5">"""

    new_map_banner = """      <!-- Floating Active Map Filter Pill Banner (Appears when map is filtered) -->
      <div id="activeMapFilterBanner" class="hidden absolute top-2.5 sm:top-3 left-1/2 -translate-x-1/2 z-20 pointer-events-auto flex items-center gap-2 bg-[#0c1a2e]/95 border border-[#38bdf8]/70 text-white px-3.5 py-1.5 rounded-full backdrop-blur-md shadow-xl text-[14px]">
        <span id="activeMapFilterIcon" class="text-[14px]">🕒</span>
        <span id="activeMapFilterText" class="font-medium tracking-wide text-white text-[14px]">24 MONDAY OPENINGS ON MAP</span>
        <button id="clearMapFilterBtn" class="ml-1 text-[#93c5fd] hover:text-white hover:bg-white/10 rounded-full w-5 h-5 flex items-center justify-center transition text-[14px]" title="Clear filter">✕</button>
      </div>

      <!-- Top-Right Globe Map Controls & Reset -->
      <div class="absolute top-2.5 right-2.5 sm:top-3 sm:right-4 z-10 flex items-center gap-1.5">"""

    if old_top_controls in src:
        src = src.replace(old_top_controls, new_map_banner, 1)
        print("Added activeMapFilterBanner to globeViewport")
    else:
        print("Warning: old_top_controls not found in build_conversational_atlas.py")

    # 2. Update curatorInquiryRow with complete set of filter chips matching screenshot
    old_inquiry_start = src.find('<div id="curatorInquiryRow"')
    old_inquiry_end = src.find('<div class="p-2 sm:p-3 bg-[#171717] shrink-0 border-t border-[#222222]">', old_inquiry_start)

    if old_inquiry_start != -1 and old_inquiry_end != -1:
        new_inquiry_row = """<div id="curatorInquiryRow" class="max-w-3xl mx-auto w-full px-3 sm:px-6 py-2 flex items-center gap-1.5 overflow-x-auto custom-scrollbar shrink-0 text-[14px] whitespace-nowrap">
          <button class="inquiry-chip px-3 py-1 rounded-full border border-[#1b3324] bg-[#0c1f15] text-[#6ee7b7] hover:border-[#10b981] hover:bg-[#112d1e] transition active:scale-95 flex items-center gap-1.5" data-filter="free" data-chip-color="green" data-query="Which cultural spaces offer always free admission?">
            <span>🎟️ Free Admission</span>
          </button>
          <button class="inquiry-chip px-3 py-1 rounded-full border border-[#232a3c] bg-[#101522] text-[#93c5fd] hover:border-[#3b82f6] hover:bg-[#151c30] transition active:scale-95 flex items-center gap-1.5" data-filter="monday" data-chip-color="blue" data-query="What are typical museum opening hours and which institutions are open on Mondays?">
            <span>🕒 Hours & Mondays</span>
          </button>
          <button class="inquiry-chip px-3 py-1 rounded-full border border-[#232a3c] bg-[#101522] text-[#93c5fd] hover:border-[#3b82f6] hover:bg-[#151c30] transition active:scale-95 flex items-center gap-1.5" data-filter="transit" data-chip-color="blue" data-query="How do I get to destination museums like Dia Beacon or Louisiana by public transit?">
            <span>🚇 Public Transit Tips</span>
          </button>
          <button class="inquiry-chip px-3 py-1 rounded-full border border-[#232a3c] bg-[#101522] text-[#cbd5e1] hover:border-[#3b82f6] hover:bg-[#151c30] transition active:scale-95 flex items-center gap-1.5" data-filter="accessibility" data-chip-color="slate" data-query="Which museums offer step-free wheelchair accessibility and inclusive facilities?">
            <span>♿ Accessibility</span>
          </button>
          <button class="inquiry-chip px-3 py-1 rounded-full border border-[#232a3c] bg-[#101522] text-[#cbd5e1] hover:border-[#3b82f6] hover:bg-[#151c30] transition active:scale-95 flex items-center gap-1.5" data-filter="amenities" data-chip-color="slate" data-query="Which institutions feature outstanding cafés, sculpture gardens, and art bookshops?">
            <span>☕ Cafés & Bookshops</span>
          </button>
          <button class="inquiry-chip px-3 py-1 rounded-full border border-[#232a3c] bg-[#101522] text-[#93c5fd] hover:border-[#3b82f6] hover:bg-[#151c30] transition active:scale-95 flex items-center gap-1.5" data-filter="ethical" data-chip-color="blue" data-query="What makes an institution ethically funded and what is Tier A?">
            <span>🏛️ Ethical Criteria</span>
          </button>
          <button class="inquiry-chip px-3 py-1 rounded-full border border-[#232a3c] bg-[#101522] text-[#cbd5e1] hover:border-[#3b82f6] hover:bg-[#151c30] transition active:scale-95 flex items-center gap-1.5" data-filter="artist_run" data-chip-color="slate" data-query="Recommend independent artist-run centers and grassroots kunsthalles">
            <span>🎨 Artist-Run Spaces</span>
          </button>
          <button class="inquiry-chip px-3 py-1 rounded-full border border-[#1b3324] bg-[#0c1f15] text-[#6ee7b7] hover:border-[#10b981] hover:bg-[#112d1e] transition active:scale-95 flex items-center gap-1.5" data-filter="fossil_free" data-chip-color="green" data-query="Show institutions free from fossil fuels and defense sponsors">
            <span>🌿 Fossil & defense-free spaces</span>
          </button>
          <button class="inquiry-chip px-3 py-1 rounded-full border border-[#232a3c] bg-[#101522] text-[#93c5fd] hover:border-[#3b82f6] hover:bg-[#151c30] transition active:scale-95 flex items-center gap-1.5" data-filter="london" data-chip-color="blue" data-city="London" data-query="Tell me about London's art scene, independent spaces, and divestment history">
            <span>📍 London guide</span>
          </button>
          <button class="inquiry-chip px-3 py-1 rounded-full border border-[#232a3c] bg-[#101522] text-[#93c5fd] hover:border-[#3b82f6] hover:bg-[#151c30] transition active:scale-95 flex items-center gap-1.5" data-filter="nyc" data-chip-color="blue" data-city="New York" data-query="Tell me about New York's art scene and independent spaces">
            <span>📍 New York guide</span>
          </button>
          <button class="inquiry-chip px-3 py-1 rounded-full border border-[#232a3c] bg-[#101522] text-[#93c5fd] hover:border-[#3b82f6] hover:bg-[#151c30] transition active:scale-95 flex items-center gap-1.5" data-filter="paris" data-chip-color="blue" data-city="Paris" data-query="Tell me about Paris's contemporary art scene and civic spaces">
            <span>📍 Paris guide</span>
          </button>
          <button class="inquiry-chip px-3 py-1 rounded-full border border-[#3b2b11] bg-[#221807] text-[#fcd34d] hover:border-[#f59e0b] hover:bg-[#2d2009] transition active:scale-95 flex items-center gap-1.5" data-filter="moma" data-chip-color="amber" data-query="Why is MoMA excluded from Culture Atlas?">
            <span>⚠️ Why MoMA is excluded</span>
          </button>
          <button class="inquiry-chip px-3 py-1 rounded-full border border-[#2f2f2f] bg-[#212121] text-[#d4d4d4] hover:bg-[#2b2b2b] hover:text-white transition active:scale-95 flex items-center gap-1.5" data-filter="theory_objecthood" data-query="What is Beyond Objecthood and how did the exhibition become a critical form?">
            <span>📖 Beyond Objecthood</span>
          </button>
          <button class="inquiry-chip px-3 py-1 rounded-full border border-[#2f2f2f] bg-[#212121] text-[#d4d4d4] hover:bg-[#2b2b2b] hover:text-white transition active:scale-95 flex items-center gap-1.5" data-filter="theory_eflux" data-query="What does e-flux say about the museum as a factory and duty-free art?">
            <span>📑 e-flux: Museum as factory</span>
          </button>
          <button class="inquiry-chip px-3 py-1 rounded-full border border-[#2f2f2f] bg-[#212121] text-[#d4d4d4] hover:bg-[#2b2b2b] hover:text-white transition active:scale-95 flex items-center gap-1.5" data-filter="theory_critique" data-query="Explain the three waves of institutional critique from Hans Haacke to Nan Goldin and Strike MoMA">
            <span>⚡ 3 Waves of Critique</span>
          </button>
          <button class="inquiry-chip px-3 py-1 rounded-full border border-[#232a3c] bg-[#101522] text-[#cbd5e1] hover:border-[#3b82f6] hover:bg-[#151c30] transition active:scale-95 flex items-center gap-1.5" data-filter="surprise" data-chip-color="slate" data-query="Surprise me with a unique ethical cultural institution">
            <span>✨ Surprise me</span>
          </button>
        </div>\n        """
        src = src[:old_inquiry_start] + new_inquiry_row + src[old_inquiry_end:]
        print("Replaced curatorInquiryRow with complete screenshot matching filter bar")
    else:
        print("Warning: curatorInquiryRow boundaries not found")

    # 3. Update applyFilters() to apply category filters to filteredList
    old_apply_start = src.find("    function applyFilters() {")
    old_apply_end = src.find("    function renderLeftList() {", old_apply_start)

    if old_apply_start != -1 and old_apply_end != -1:
        new_apply = """    let selectedCategoryFilter = 'all';

    const FILTER_META = {{
      free: {{ icon: '🎟️', label: 'FREE ADMISSION' }},
      monday: {{ icon: '🕒', label: 'MONDAY OPENINGS' }},
      transit: {{ icon: '🚇', label: 'PUBLIC TRANSIT TIPS' }},
      accessibility: {{ icon: '♿', label: 'UNIVERSAL ACCESSIBILITY' }},
      amenities: {{ icon: '☕', label: 'CAFÉS, BOOKSHOPS & GARDENS' }},
      ethical: {{ icon: '🏛️', label: 'ETHICAL CIVIC CRITERIA' }},
      artist_run: {{ icon: '🎨', label: 'ARTIST-RUN KUNSTHALLES' }},
      fossil_free: {{ icon: '🌿', label: 'FOSSIL & DEFENSE-FREE SPACES' }},
      london: {{ icon: '📍', label: 'LONDON GUIDE' }},
      nyc: {{ icon: '📍', label: 'NEW YORK GUIDE' }},
      paris: {{ icon: '📍', label: 'PARIS GUIDE' }},
      moma: {{ icon: '⚠️', label: 'MOMA AUDIT & EXCLUSION' }}
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

      listTotalBadge.textContent = `${{filteredList.length}} mapped`;

      // Update Floating Map Filter Banner
      const activeMapBanner = document.getElementById('activeMapFilterBanner');
      const activeMapIcon = document.getElementById('activeMapFilterIcon');
      const activeMapText = document.getElementById('activeMapFilterText');

      if (activeMapBanner && activeMapText) {{
        if (selectedCategoryFilter !== 'all') {{
          activeMapBanner.classList.remove('hidden');
          const meta = FILTER_META[selectedCategoryFilter] || {{ icon: '📍', label: selectedCategoryFilter.toUpperCase() }};
          activeMapIcon.textContent = meta.icon;
          activeMapText.textContent = `${{meta.label}} · ${{filteredList.length}} SANCTUARIES ON MAP`;
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
    }}
\n"""
        src = src[:old_apply_start] + new_apply + src[old_apply_end:]
        print("Updated applyFilters() with category filter map support")
    else:
        print("Warning: applyFilters boundaries not found")

    # 4. Update inquiry-chip click listeners and add clearMapFilterBtn listener
    old_chips_listener = """    // Inquiry Chips
    document.querySelectorAll('.inquiry-chip').forEach(btn => {
      btn.addEventListener('click', () => {
        const q = btn.getAttribute('data-query');
        const city = btn.getAttribute('data-city');
        if (city) {
          filterByCity(city, true, false);
        } else if (q && q.toLowerCase().includes('london')) {
          filterByCity('London', true, false);
        }
        if (q) {
          if (q.toLowerCase().includes('moma')) {
            openMomaAuditModal();
          }
          appendUserMessage(q);
          handleCuratorQuery(q);
        }
      });
    });"""

    new_chips_listener = """    function updateFilterChipsUI() {{
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
    }});"""

    if old_chips_listener in src:
        src = src.replace(old_chips_listener, new_chips_listener, 1)
        print("Replaced old_chips_listener with setCategoryFilter and updateFilterChipsUI")
    else:
        print("Warning: old_chips_listener not found!")

    with open("build_conversational_atlas.py", "w", encoding="utf-8") as f:
        f.write(src)
    print("Saved build_conversational_atlas.py with map filter support!")

if __name__ == "__main__":
    update_map_filters()
