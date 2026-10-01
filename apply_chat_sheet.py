#!/usr/bin/env python3
"""
apply_chat_sheet.py
Updates build_conversational_atlas.py to implement:
- Half sheet default for chat (50/50 split)
- Open and Close controls:
  - '▼ Close' button collapses chat to sleek 46px bottom dock (globe gets full screen)
  - '▲ Open Half Sheet' opens chat to 50% half sheet
  - '⤢ Full' / '⤡ Half' toggle for optional full-height catalog reading
  - Drag handle with touch swipe gestures (swipe down to close, swipe up to open)
- Real-time synchronization: clicking city/museum or 'Ask Curator' opens half sheet automatically.
"""

with open('build_conversational_atlas.py', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Update CSS style block
old_css_marker = '''    /* Mobile Bottom Sheet Smooth Transitions */
    .bottom-sheet {{
      transition: height 0.32s cubic-bezier(0.16, 1, 0.3, 1), transform 0.32s cubic-bezier(0.16, 1, 0.3, 1);
    }}
    .sheet-peek {{
      height: 76px !important;
    }}
    .sheet-half {{
      height: 52vh !important;
    }}
    .sheet-full {{
      height: 88vh !important;
    }}'''

new_css = '''    /* Mobile & Desktop Bottom Half Sheet Smooth Transitions */
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
    }}'''

if old_css_marker in text:
    text = text.replace(old_css_marker, new_css)
    print("Replaced CSS style block!")
else:
    print("Warning: old_css_marker not found, skipping CSS block replacement...")

# 2. Main container id
text = text.replace(
    '<div class="relative w-full h-full flex flex-col bg-[#020408] overflow-hidden">',
    '<div id="mainAppContainer" class="sheet-half relative w-full h-full flex flex-col bg-[#020408] overflow-hidden">'
)
print("Updated mainAppContainer class!")

# 3. Replace bottomChatSection header
old_chat_header = '''    <!-- ========================================================= -->
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
      </div>'''

new_chat_header = '''    <!-- ========================================================= -->
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
          <div class="flex items-center bg-[#101420] border border-[#1e2434] rounded-lg p-0.5 text-xs font-medium">
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
            <span id="listTotalBadge" class="text-[10px] sm:text-[11px] font-mono text-[#94a3b8] bg-[#161821] px-2 py-0.5 rounded border border-[#282c38]">
              203 mapped
            </span>
            <span id="activeFilterBadge" class="hidden text-[10px] sm:text-[10.5px] font-mono text-[#60a5fa] bg-[#0d1d36] border border-[#1d4ed8] px-2 py-0.5 rounded flex items-center gap-1">
              <span id="activeFilterText">Filtered</span>
              <button id="clearActiveFilterBtn" class="text-slate-400 hover:text-white ml-0.5">✕</button>
            </span>

            <!-- Expand / Half Toggle Button -->
            <button id="sheetExpandBtn" class="bg-[#121622] hover:bg-[#1c2336] border border-[#222a3c] text-slate-300 hover:text-white px-2 py-1 rounded-lg text-xs font-mono transition flex items-center gap-1" title="Expand / Restore Sheet">
              <span id="sheetExpandIcon">⤢</span>
              <span id="sheetExpandLabel" class="hidden sm:inline text-[11px]">Full</span>
            </button>

            <!-- Close Sheet Button -->
            <button id="sheetCloseBtn" class="bg-[#182032] hover:bg-[#202c46] border border-[#283654] text-[#60a5fa] hover:text-white px-2.5 py-1 rounded-lg text-xs font-semibold transition flex items-center gap-1 shadow" title="Close Chat Sheet">
              <span>▼</span>
              <span class="text-[11px]">Close</span>
            </button>
          </div>

        </div>

        <!-- 2. Closed State Bar (Shown when Closed) -->
        <div id="sheetClosedBar" class="hidden flex items-center justify-between gap-2 cursor-pointer py-0.5">
          <div class="flex items-center gap-2 truncate">
            <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            <span class="text-xs font-semibold text-white truncate">💬 Conversational Curator</span>
            <span class="text-[10.5px] text-[#94a3b8] font-mono hidden sm:inline truncate">· 203 Sanctuaries Mapped</span>
          </div>

          <div class="flex items-center gap-2 shrink-0">
            <span class="text-[10px] font-mono text-emerald-400 bg-[#0a2016] px-2 py-0.5 rounded border border-emerald-900/60 hidden xs:inline">
              Tap to Ask
            </span>
            <button id="sheetOpenBtn" class="px-3 py-1 bg-[#1d4ed8] hover:bg-[#2563eb] text-white text-xs font-semibold rounded-lg transition shadow flex items-center gap-1">
              <span>▲</span>
              <span>Open Half Sheet</span>
            </button>
          </div>
        </div>

      </div>'''

if old_chat_header in text:
    text = text.replace(old_chat_header, new_chat_header)
    print("Replaced bottomChatSection header!")
else:
    print("Warning: old_chat_header not found, continuing...")

# 4. Add JS sheet controller logic
js_target = "    tabCuratorBtn.addEventListener('click', () => switchTab('curator'));"
js_controller = '''    // =========================================================
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

    tabCuratorBtn.addEventListener('click', () => switchTab('curator'));'''

if js_target in text:
    text = text.replace(js_target, js_controller)
    print("Injected JS sheet controller!")
else:
    print("Warning: js_target not found!")

# 5. Ensure clicking 'Ask Curator' on floating card opens half sheet
text = text.replace(
    "switchTab('curator');\n        appendUserMessage(`Tell me about ${selectedInstitution.name} and its funding`);",
    "setChatSheetState('half');\n        switchTab('curator');\n        appendUserMessage(`Tell me about ${selectedInstitution.name} and its funding`);"
)

# 6. Ensure clicking Why MoMA opens half sheet
text = text.replace(
    "switchTab('curator');\n      appendUserMessage('Why is MoMA excluded from Culture Atlas?');",
    "setChatSheetState('half');\n      switchTab('curator');\n      appendUserMessage('Why is MoMA excluded from Culture Atlas?');"
)

# 7. Ensure filterByCity and filterByCountry open half sheet if closed
text = text.replace(
    "if (cityMatches.length > 0) {\n        appendCuratorMessage(",
    "if (currentSheetState === 'closed') setChatSheetState('half');\n      if (cityMatches.length > 0) {\n        appendCuratorMessage("
)
text = text.replace(
    "if (countryMatches.length > 0) {\n        appendCuratorMessage(",
    "if (currentSheetState === 'closed') setChatSheetState('half');\n      if (countryMatches.length > 0) {\n        appendCuratorMessage("
)

with open('build_conversational_atlas.py', 'w', encoding='utf-8') as f:
    f.write(text)

print("Successfully applied open/close half sheet to build_conversational_atlas.py!")
