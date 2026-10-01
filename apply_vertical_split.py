#!/usr/bin/env python3
"""
apply_vertical_split.py
Refactors build_conversational_atlas.py into:
- TOP HALF: 3D Globe map (50% screen height)
- BOTTOM HALF: Curator Chat & Catalog (50% screen height)
Exactly as requested: "do a chat at the bottom and globe on top half screen chat half map"
"""

import re

with open('build_conversational_atlas.py', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Update CSS style block
old_style_snippet = '''.bottom-sheet {
      transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1);
    }
    .sheet-peek {
      transform: translateY(calc(100% - 72px));
    }
    .sheet-half {
      transform: translateY(calc(100% - 46vh));
    }
    .sheet-full {
      transform: translateY(0);
    }'''

new_style_snippet = '''/* Half screen Globe on top, half screen Chat at bottom */
    #globeViewport {
      height: 48vh;
      height: 48dvh;
      min-height: 240px;
    }
    @media (min-width: 768px) {
      #globeViewport {
        height: 50vh;
        height: 50dvh;
      }
    }
    #bottomChatSection {
      height: 52vh;
      height: 52dvh;
      min-height: 240px;
    }
    @media (min-width: 768px) {
      #bottomChatSection {
        height: 50vh;
        height: 50dvh;
      }
    }'''

if old_style_snippet in text:
    text = text.replace(old_style_snippet, new_style_snippet)
    print("Updated CSS style snippet for 50/50 split!")
else:
    print("Warning: old_style_snippet not found, continuing...")

# 2. Find and replace main layout container
layout_start_marker = '<!-- MAIN APP CONTAINER (Responsive Desktop Split + Mobile Map)-->'
layout_end_marker = '<!-- ========================================================= -->\n  <!-- 📄 SCHOLARLY INSTITUTION AUDIT DOSSIER DRAWER -->'

start_idx = text.find(layout_start_marker)
end_idx = text.find(layout_end_marker)

print(f"start_idx: {start_idx}, end_idx: {end_idx}")

new_layout = '''<!-- MAIN APP CONTAINER (Top Half: 3D Globe / Bottom Half: Conversational Chat) -->
  <!-- ========================================================= -->
  <div class="relative w-full h-full flex flex-col bg-[#020408] overflow-hidden">

    <!-- ========================================================= -->
    <!-- 🌍 TOP HALF: 3D GLOBE MAP (HALF SCREEN) -->
    <!-- ========================================================= -->
    <div id="globeViewport" class="relative w-full flex items-center justify-center bg-[#020408] overflow-hidden shrink-0 border-b border-[#1c212a]">
      
      <canvas id="globeCanvas" width="900" height="700" class="w-full h-full object-contain cursor-grab"></canvas>

      <!-- FLOATING WHITE CARD (Pinned to selected institution with Website Link & Hours) -->
      <div id="floatingCard" class="absolute z-20 pointer-events-auto bg-white text-slate-900 rounded-lg px-3 py-2 shadow-2xl transition duration-150 transform -translate-x-1/2 -translate-y-full mb-3 cursor-pointer border border-slate-100 max-w-[240px] sm:max-w-[280px]">
        <div class="flex items-center justify-between gap-1.5">
          <div id="floatingCardTitle" class="font-bold text-[12px] sm:text-[13px] text-slate-950 leading-tight truncate">Plug In ICA</div>
          <span id="floatingCardTier" class="text-[8.5px] sm:text-[9px] font-semibold uppercase px-1.5 py-0.5 bg-emerald-100 text-emerald-800 rounded shrink-0">Verified</span>
        </div>
        <div id="floatingCardMeta" class="text-[10.5px] sm:text-[11px] text-slate-500 mt-0.5 flex items-center gap-1">
          <span>Winnipeg, Canada</span>
        </div>
        <div id="floatingCardHours" class="text-[9.5px] font-mono text-emerald-700 mt-0.5 truncate">Tue–Fri 12:00–18:00 · Free Entry</div>
        <div class="mt-1.5 pt-1.5 border-t border-slate-100 flex items-center justify-between text-[10px] sm:text-[10.5px] gap-2">
          <a id="floatingCardWebLink" href="https://plugin.org" target="_blank" rel="noopener noreferrer" 
             class="inline-flex items-center gap-1 font-medium text-[#1d4ed8] hover:text-[#1e40af] hover:underline"
             onclick="event.stopPropagation()">
            <span>🌐</span> <span id="floatingCardDomain" class="truncate max-w-[80px]">plugin.org</span> <span class="text-[9px]">↗</span>
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
            <span class="text-[11px] sm:text-xs font-bold tracking-wider text-[#cbd5e1] uppercase">CULTURE ATLAS</span>
            <span class="text-[9px] sm:text-[10px] font-mono text-emerald-400 bg-[#0a2016] px-1.5 rounded border border-emerald-900/60">203 SANCTUARIES</span>
          </div>
          <span class="text-[9.5px] sm:text-[10.5px] text-[#94a3b8] font-normal hidden sm:inline leading-none mt-0.5">
            Ethically funded cultural institutions across the world
          </span>
        </div>
      </div>

      <!-- Top-Right Globe Map Controls & Reset -->
      <div class="absolute top-2.5 right-2.5 sm:top-3 sm:right-4 z-10 flex items-center gap-1.5">
        <button id="resetViewBtn" class="bg-[#0e1320]/90 hover:bg-[#1b233a] border border-[#222c42] text-slate-300 px-2 sm:px-2.5 py-1 rounded-lg text-[10px] sm:text-xs font-mono transition flex items-center gap-1 shadow">
          <span>🔄</span> <span class="hidden sm:inline">Reset</span>
        </button>
        <button id="spinBtn" class="bg-[#0e1320]/90 hover:bg-[#1b233a] border border-[#222c42] text-[#3b82f6] hover:text-white px-2 sm:px-2.5 py-1 rounded-lg text-[10px] sm:text-xs font-mono transition shadow">
          <span>⟳</span> <span class="hidden sm:inline">Auto-Spin</span>
        </button>
        <button id="zoomInBtn" class="w-7 h-7 sm:w-8 sm:h-8 rounded-lg bg-[#0e1320]/90 border border-[#222c42] text-slate-300 hover:text-white flex items-center justify-center transition shadow text-xs sm:text-sm font-mono" title="Zoom In">+</button>
        <button id="zoomOutBtn" class="w-7 h-7 sm:w-8 sm:h-8 rounded-lg bg-[#0e1320]/90 border border-[#222c42] text-slate-300 hover:text-white flex items-center justify-center transition shadow text-xs sm:text-sm font-mono" title="Zoom Out">−</button>
      </div>

      <!-- Bottom-Left Map Scale & Attribution -->
      <div class="absolute bottom-2 left-2.5 sm:left-4 z-10 pointer-events-none flex items-center gap-2 text-[9.5px] sm:text-[10px] text-[#64748b] font-mono bg-[#070a12]/75 px-2 py-0.5 rounded border border-[#161d2d]/60">
        <span>└───┘ 2,000 km</span>
        <span>·</span>
        <span>WGS84 Audited</span>
      </div>

      <!-- Bottom-Right "Why MoMA is Excluded" Button -->
      <div class="absolute bottom-2 right-2.5 sm:right-4 z-10 pointer-events-auto">
        <button id="openMomaAuditBtn" class="text-[9.5px] sm:text-[10px] font-semibold text-[#f1c21b] hover:text-white bg-[#1a1406]/90 border border-[#4d3d0f] hover:border-[#f1c21b] px-2 sm:px-2.5 py-0.5 rounded-lg transition flex items-center gap-1 shadow">
          <span>⚠️</span> <span>Why MoMA is excluded</span>
        </button>
      </div>

    </div>

    <!-- ========================================================= -->
    <!-- 💬 BOTTOM HALF: CHAT CURATOR & CATALOG (HALF SCREEN) -->
    <!-- ========================================================= -->
    <div id="bottomChatSection" class="relative w-full flex-1 min-h-0 flex flex-col bg-[#07090e] overflow-hidden">
      
      <!-- Sub-Header: Mode Navigation Tabs (💬 Curator Guide / 📋 Research Catalog) -->
      <div class="px-3 py-1.5 sm:px-4 sm:py-2 border-b border-[#1c212a] bg-[#0a0d14]/95 flex items-center justify-between gap-2 shrink-0">
        <div class="flex items-center bg-[#101420] border border-[#1e2434] rounded-lg p-0.5 text-xs font-medium">
          <button id="tabCuratorBtn" class="py-1 px-3 rounded-md transition text-center flex items-center gap-1.5 bg-[#1d4ed8] text-white font-semibold shadow">
            <span>💬</span>
            <span>Curator Guide</span>
          </button>
          <button id="tabCatalogBtn" class="py-1 px-3 rounded-md transition text-center flex items-center gap-1.5 text-[#94a3b8] hover:text-white">
            <span>📋</span>
            <span>Research Catalog (203)</span>
          </button>
        </div>

        <div class="flex items-center gap-2">
          <span id="listTotalBadge" class="text-[10px] sm:text-[11px] font-mono text-[#94a3b8] bg-[#161821] px-2 py-0.5 rounded border border-[#282c38]">
            203 mapped
          </span>
          <span id="activeFilterBadge" class="hidden text-[10px] sm:text-[10.5px] font-mono text-[#60a5fa] bg-[#0d1d36] border border-[#1d4ed8] px-2 py-0.5 rounded flex items-center gap-1">
            <span id="activeFilterText">Filtered</span>
            <button id="clearActiveFilterBtn" class="text-slate-400 hover:text-white ml-0.5">✕</button>
          </span>
        </div>
      </div>

      <!-- VIEW A: 💬 CURATOR CONVERSATIONAL EXPERIENCE (Default in Bottom Half) -->
      <div id="curatorPanel" class="flex-1 flex flex-col min-h-0 overflow-hidden">
        
        <!-- Scrollable Conversation Feed -->
        <div id="curatorMessages" class="flex-1 overflow-y-auto custom-scrollbar p-3 sm:p-4 space-y-3 pb-2">
          <!-- Messages injected dynamically -->
        </div>

        <!-- Typing Indicator -->
        <div id="curatorTyping" class="hidden px-3 sm:px-4 py-1 text-xs text-[#94a3b8] flex items-center gap-2">
          <span class="text-[11px]">Curator is searching scholarly audit records</span>
          <span class="inline-flex gap-1">
            <span class="w-1.5 h-1.5 rounded-full bg-[#3b82f6] typing-dot"></span>
            <span class="w-1.5 h-1.5 rounded-full bg-[#3b82f6] typing-dot"></span>
            <span class="w-1.5 h-1.5 rounded-full bg-[#3b82f6] typing-dot"></span>
          </span>
        </div>

        <!-- Gentle Educational & Visitor Planning Inquiry Chips (Horizontal Carousel) -->
        <div class="px-2.5 py-1.5 border-t border-[#161a26] bg-[#080b12] flex items-center gap-1.5 overflow-x-auto custom-scrollbar shrink-0 text-[10.5px] font-mono whitespace-nowrap">
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
          <button class="inquiry-chip px-2.5 py-1 rounded-full border border-[#232a3c] bg-[#101522] text-[#93c5fd] hover:border-[#3b82f6] hover:bg-[#151c30] transition active:scale-95" data-query="Recommend verified cultural spaces in London">
            📍 London guide
          </button>
          <button class="inquiry-chip px-2.5 py-1 rounded-full border border-[#232a3c] bg-[#101522] text-[#93c5fd] hover:border-[#3b82f6] hover:bg-[#151c30] transition active:scale-95" data-query="Recommend verified cultural spaces in New York">
            📍 New York guide
          </button>
          <button class="inquiry-chip px-2.5 py-1 rounded-full border border-[#232a3c] bg-[#101522] text-[#93c5fd] hover:border-[#3b82f6] hover:bg-[#151c30] transition active:scale-95" data-query="Recommend verified cultural spaces in Tokyo">
            📍 Tokyo guide
          </button>
          <button class="inquiry-chip px-2.5 py-1 rounded-full border border-[#232a3c] bg-[#101522] text-[#93c5fd] hover:border-[#3b82f6] hover:bg-[#151c30] transition active:scale-95" data-query="Recommend verified cultural spaces in Paris">
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
              class="w-full bg-[#121622] border border-[#232a3c] rounded-xl px-3 sm:px-3.5 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-[#3b82f6] transition shadow-inner font-sans"
            />
          </div>
          <button 
            id="curatorSendBtn" 
            class="px-4 py-2 bg-[#1d4ed8] hover:bg-[#2563eb] text-white text-xs font-semibold rounded-xl transition shadow active:scale-95 flex items-center gap-1 shrink-0"
          >
            <span>Ask</span>
            <span class="text-[10px]">↵</span>
          </button>
          <button id="curatorSettingsBtn" class="p-2 bg-[#121622] hover:bg-[#1c2234] border border-[#232938] text-[#94a3b8] hover:text-white rounded-xl text-xs transition shrink-0" title="Curator Settings">
            <span>⚙️</span>
          </button>
        </div>

      </div>

      <!-- VIEW B: 📋 RESEARCH CATALOG (When toggled to Catalog in Bottom Half) -->
      <div id="catalogPanel" class="hidden flex-1 flex flex-col min-h-0 overflow-hidden">
        
        <div class="p-2.5 sm:p-3 border-b border-[#1c212a] bg-[#0a0d14] flex flex-col gap-2 shrink-0">
          <!-- Active Filter Banner (When city/country clicked) -->
          <div id="activeFilterBanner" class="hidden flex items-center justify-between bg-[#0e1628] border border-[#1d4ed8] px-2.5 py-1.5 rounded-lg text-xs">
            <div class="flex items-center gap-1.5 truncate">
              <span id="filterIcon" class="text-sm">📍</span>
              <span id="filterLabel" class="font-semibold text-white truncate">NEW YORK</span>
              <span id="filterCount" class="text-[#60a5fa] font-mono text-[11px]">(11)</span>
            </div>
            <button id="clearFilterBtn" class="text-xs text-[#94a3b8] hover:text-white px-1.5 py-0.5 rounded hover:bg-[#1a253c] transition ml-2 flex items-center gap-1">
              <span>Clear</span> <span>✕</span>
            </button>
          </div>

          <!-- Search Input -->
          <div class="relative">
            <input 
              type="text" 
              id="searchInput" 
              placeholder="Search museum, city, focus, or governance..." 
              class="w-full bg-[#141722] border border-[#262a38] text-xs text-white placeholder-[#64748b] px-3 py-1.5 rounded-lg focus:outline-none focus:border-[#3b82f6] transition"
            />
            <button id="clearSearchBtn" class="hidden absolute right-2.5 top-1.5 text-[#64748b] hover:text-white text-xs">✕</button>
          </div>

          <!-- Quick Filters: Country & City Dropdowns -->
          <div class="grid grid-cols-2 gap-1.5 text-[11px] font-mono">
            <select id="countrySelect" class="bg-[#141722] border border-[#262a38] text-[#e2e8f0] px-2 py-1 rounded focus:outline-none focus:border-[#3b82f6] truncate">
              <option value="all">All Countries (35)</option>
            </select>
            <select id="citySelect" class="bg-[#141722] border border-[#262a38] text-[#e2e8f0] px-2 py-1 rounded focus:outline-none focus:border-[#3b82f6] truncate">
              <option value="all">All Cities (133)</option>
            </select>
          </div>

          <!-- Tier Quick Chips -->
          <div class="flex items-center gap-1.5 text-[10px] font-mono">
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

  '''

if start_idx != -1 and end_idx != -1:
    text = text[:start_idx] + new_layout + text[end_idx:]
    print("Replaced main layout container with vertical 50/50 split!")
else:
    print("Error: Could not find layout markers!")

# 3. Clean up old mobile sheet JS handlers if present
old_mobile_sheet_js = '''    // =========================================================
    // 📱 MOBILE INTERACTION (Tabs & Bottom Sheet)
    // =========================================================
    const bottomSheet = document.getElementById('bottomSheet');
    const sheetDragHandle = document.getElementById('sheetDragHandle');
    const mobileSheetToggleBtn = document.getElementById('mobileSheetToggleBtn');
    const sheetToggleText = document.getElementById('sheetToggleText');
    const sheetToggleArrow = document.getElementById('sheetToggleArrow');
    const mobileModeCurator = document.getElementById('mobileModeCurator');
    const mobileModeGlobe = document.getElementById('mobileModeGlobe');

    function setSheetState(state) {
      currentSheetState = state;
      bottomSheet.classList.remove('sheet-peek', 'sheet-half', 'sheet-full');
      bottomSheet.classList.add(`sheet-${state}`);

      if (state === 'peek') {
        sheetToggleText.textContent = 'Expand';
        sheetToggleArrow.textContent = '▲';
      } else if (state === 'half') {
        sheetToggleText.textContent = 'Full';
        sheetToggleArrow.textContent = '▲';
      } else {
        sheetToggleText.textContent = 'Minimize';
        sheetToggleArrow.textContent = '▼';
      }
    }

    function setMobileView(view) {
      if (view === 'globe') {
        setSheetState('peek');
        mobileModeGlobe.className = 'px-3 py-1 rounded-full bg-[#1d4ed8] text-white transition flex items-center gap-1';
        mobileModeCurator.className = 'px-3 py-1 rounded-full text-[#94a3b8] hover:text-white transition flex items-center gap-1';
      } else {
        setSheetState('half');
        switchTab('curator');
        mobileModeCurator.className = 'px-3 py-1 rounded-full bg-[#1d4ed8] text-white transition flex items-center gap-1';
        mobileModeGlobe.className = 'px-3 py-1 rounded-full text-[#94a3b8] hover:text-white transition flex items-center gap-1';
      }
    }

    mobileModeGlobe.addEventListener('click', () => setMobileView('globe'));
    mobileModeCurator.addEventListener('click', () => setMobileView('curator'));

    mobileSheetToggleBtn.addEventListener('click', () => {
      if (currentSheetState === 'peek') setSheetState('half');
      else if (currentSheetState === 'half') setSheetState('full');
      else setSheetState('peek');
    });

    // Drag / Touch gestures on handle
    let dragStartY = 0;
    sheetDragHandle.addEventListener('touchstart', e => {
      dragStartY = e.touches[0].clientY;
    }, { passive: true });

    sheetDragHandle.addEventListener('touchend', e => {
      const deltaY = e.changedTouches[0].clientY - dragStartY;
      if (deltaY < -40) {
        if (currentSheetState === 'peek') setSheetState('half');
        else if (currentSheetState === 'half') setSheetState('full');
      } else if (deltaY > 40) {
        if (currentSheetState === 'full') setSheetState('half');
        else if (currentSheetState === 'half') setSheetState('peek');
      }
    });'''

# Notice double braces in python file
old_mobile_sheet_doubled = old_mobile_sheet_js.replace('{', '{{').replace('}', '}}')

new_mobile_sheet_clean = '''    // Safe view switcher stub for dual-split layout
    function setMobileView(view) {{
      if (view === 'curator') switchTab('curator');
      else if (view === 'catalog') switchTab('catalog');
    }}'''

if old_mobile_sheet_doubled in text:
    text = text.replace(old_mobile_sheet_doubled, new_mobile_sheet_clean)
    print("Replaced old mobile sheet JS handlers!")
else:
    print("Notice: old mobile sheet doubled string not found directly, checking partial...")

# Check any lingering setMobileView('globe') in selectInstitution
text = text.replace("if (shouldSwitchToGlobe && window.innerWidth < 768) {\n        setMobileView('globe');\n      }", "// Top half globe is always visible")
text = text.replace("if (shouldSwitchToGlobe && window.innerWidth < 768) {{\n        setMobileView('globe');\n      }}", "// Top half globe is always visible")

with open('build_conversational_atlas.py', 'w', encoding='utf-8') as f:
    f.write(text)

print("Saved build_conversational_atlas.py with split screen layout!")
