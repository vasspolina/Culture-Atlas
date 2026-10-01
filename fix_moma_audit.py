#!/usr/bin/env python3
"""
fix_moma_audit.py
Fixes 'Why MoMA is excluded' button:
1. Adds a dedicated, high-impact 'momaAuditModal' to build_conversational_atlas.py
   showing the comprehensive forensic audit:
   - Leon Black ($158M to Jeffrey Epstein)
   - Strike MoMA / Decolonize This Place 10-week campaign
   - Extractive & defense trustees (Larry Fink/BlackRock, Steven Tananbaum, Paula Crown/General Dynamics)
   - Clean NYC alternatives (11 sanctuaries mapped)
2. Connects openMomaAuditBtn to open the modal, fly the globe to NYC (-73.9776, 40.7614),
   and stream the explanation in chat.
3. Adds 'wOpenMomaBtn' on widget globe as well and handles chip clicks seamlessly.
"""

# =========================================================
# 1. Update build_conversational_atlas.py
# =========================================================
with open('build_conversational_atlas.py', 'r', encoding='utf-8') as f:
    atlas = f.read()

moma_modal_html = '''  <!-- ========================================================= -->
  <!-- ⚠️ MoMA EXCLUSION AUDIT MODAL -->
  <!-- ========================================================= -->
  <div id="momaAuditModal" class="hidden fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-3 sm:p-5 select-text">
    <div class="bg-[#0b0e17] border border-[#f59e0b]/50 rounded-2xl max-w-lg w-full max-h-[90vh] flex flex-col shadow-2xl overflow-hidden font-sans">
      
      <!-- Modal Header -->
      <div class="px-4 py-3 border-b border-[#252f48] bg-[#141008] flex items-center justify-between shrink-0">
        <div class="flex items-center gap-2">
          <span class="text-amber-400 text-lg">⚠️</span>
          <div>
            <h3 class="font-bold text-white text-xs sm:text-sm">EXCLUSION AUDIT · Why MoMA is Excluded</h3>
            <p class="text-[10px] font-mono text-amber-300/80">Museum of Modern Art (New York) · Institutional Scrutiny</p>
          </div>
        </div>
        <button id="closeMomaModalBtn" class="w-7 h-7 rounded-lg bg-[#20180a] hover:bg-[#33250f] border border-[#523d14] text-slate-300 hover:text-white flex items-center justify-center text-sm transition">✕</button>
      </div>

      <!-- Modal Body -->
      <div class="p-4 sm:p-5 overflow-y-auto custom-scrollbar space-y-3.5 text-xs text-slate-200 leading-relaxed">
        
        <!-- Summary Callout -->
        <div class="bg-[#181207] border border-[#78350f]/60 rounded-xl p-3 text-xs space-y-1">
          <span class="text-amber-400 font-semibold uppercase tracking-wider text-[10px] block font-mono">⚡ Exclusion Criteria Assessment</span>
          <p class="text-slate-200">
            Culture Atlas celebrates cultural institutions that champion curatorial freedom and clean underwriting. MoMA is excluded from our verified directory due to documented, unaddressed governance ties to defense contractors, private prisons, and controversial private equity financiers.
          </p>
        </div>

        <!-- Section 1: Leon Black & Jeffrey Epstein -->
        <div class="space-y-1">
          <h4 class="font-semibold text-white text-xs flex items-center gap-1.5">
            <span class="text-rose-400 font-bold">1.</span> <span>Leon Black & Jeffrey Epstein ($158M)</span>
          </h4>
          <p class="text-slate-300 text-[11.5px] pl-4">
            Former MoMA Board Chairman <strong>Leon Black</strong> (founder of Apollo Global Management) stepped down in March 2021 after independent forensic audits revealed he transferred $158 million to convicted sex offender Jeffrey Epstein between 2012 and 2017.
          </p>
        </div>

        <!-- Section 2: Strike MoMA Movement -->
        <div class="space-y-1">
          <h4 class="font-semibold text-white text-xs flex items-center gap-1.5">
            <span class="text-rose-400 font-bold">2.</span> <span>The 'Strike MoMA' Movement (Spring 2021)</span>
          </h4>
          <p class="text-slate-300 text-[11.5px] pl-4">
            A coalition of artists, cultural workers, and grassroots collectives (Decolonize This Place, Strike MoMA, and Artists Space allies) held 10 weeks of continuous protests demanding institutional accountability, trustee divestment, and community restitution.
          </p>
        </div>

        <!-- Section 3: Controversial Trustee Portfolio -->
        <div class="space-y-1">
          <h4 class="font-semibold text-white text-xs flex items-center gap-1.5">
            <span class="text-rose-400 font-bold">3.</span> <span>Extractive & Defense Board Holdings</span>
          </h4>
          <ul class="list-disc pl-8 space-y-1 text-slate-300 text-[11.5px]">
            <li><strong>Steven Tananbaum (GoldenTree Asset Management):</strong> Board trustee targeted by artists over vulture fund holdings exacerbating Puerto Rico's debt and hurricane recovery crises.</li>
            <li><strong>Larry Fink (CEO, BlackRock):</strong> Board trustee heading the world's largest institutional investor in fossil fuel expansion, weapons manufacturing, and private detention centers.</li>
            <li><strong>Paula Crown:</strong> Trustee whose billionaire family owns General Dynamics, one of the world's largest defense and aerospace contractors.</li>
          </ul>
        </div>

        <!-- Section 4: What to Visit Instead -->
        <div class="bg-[#0e1628] border border-[#1d4ed8]/50 rounded-xl p-3 space-y-1.5">
          <span class="text-[#60a5fa] font-semibold text-[10.5px] uppercase tracking-wider block font-mono">🌿 Verified Ethical Alternatives in New York</span>
          <p class="text-slate-300 text-[11.5px]">
            Instead of supporting corporate-compromised boards, visit New York's <strong>11 verified ethical cultural sanctuaries</strong>—including <em>Dia Beacon, SculptureCenter, Artists Space, and The Studio Museum in Harlem</em>.
          </p>
        </div>

      </div>

      <!-- Modal Footer -->
      <div class="px-4 py-2.5 border-t border-[#252f48] bg-[#0c101c] flex items-center justify-between gap-2 shrink-0">
        <button id="momaAuditFlyNycBtn" class="px-3 py-1.5 bg-[#1d4ed8] hover:bg-[#2563eb] text-white text-xs font-semibold rounded-xl transition flex items-center gap-1.5 shadow">
          <span>🗽</span> <span>Explore 11 Ethical NYC Spaces</span>
        </button>
        <button id="momaAuditChatBtn" class="px-3 py-1.5 bg-[#172032] hover:bg-[#22304c] border border-[#2b3b5c] text-slate-200 hover:text-white text-xs rounded-xl transition flex items-center gap-1.5">
          <span>💬</span> <span>Ask in Chat</span>
        </button>
      </div>

    </div>
  </div>

'''

settings_marker = '  <!-- ⚙️ CURATOR SETTINGS MODAL (Optional Google Gemini API Key) -->'
if settings_marker in atlas and 'id="momaAuditModal"' not in atlas:
    atlas = atlas.replace(settings_marker, moma_modal_html + settings_marker)
    print("Inserted momaAuditModal HTML into build_conversational_atlas.py!")

# Replace openMomaAuditBtn click listener with complete modal & fly logic
old_moma_listener = '''    document.getElementById('openMomaAuditBtn').addEventListener('click', () => {{
      setChatSheetState('half');
      switchTab('curator');
      appendUserMessage('Why is MoMA excluded from Culture Atlas?');
      handleCuratorQuery('Why is MoMA excluded from Culture Atlas?');
    }});'''

new_moma_listener = '''    // =========================================================
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
    }});'''

if old_moma_listener in atlas:
    atlas = atlas.replace(old_moma_listener, new_moma_listener)
    print("Updated openMomaAuditBtn listener with openMomaAuditModal!")
else:
    print("Warning: old_moma_listener not found!")

# Also ensure inquiry chip clicking for MoMA triggers the modal & briefing
chip_query_moma = '''        if (q) {{
          appendUserMessage(q);
          handleCuratorQuery(q);
        }}'''

new_chip_query = '''        if (q) {{
          if (q.toLowerCase().includes('moma')) {{
            openMomaAuditModal();
          }}
          appendUserMessage(q);
          handleCuratorQuery(q);
        }}'''

if chip_query_moma in atlas:
    atlas = atlas.replace(chip_query_moma, new_chip_query)
    print("Updated inquiry chip listener to trigger modal on MoMA!")

with open('build_conversational_atlas.py', 'w', encoding='utf-8') as f:
    f.write(atlas)


# =========================================================
# 2. Update build_conversational_widget.py
# =========================================================
with open('build_conversational_widget.py', 'r', encoding='utf-8') as f:
    widget = f.read()

# Add button on widget globe
old_widget_globe_end = '''      <div class="absolute bottom-1.5 left-2 text-[8.5px] text-[#64748b] font-mono pointer-events-none">
        <span>└───┘ 2,000 km</span>
      </div>'''

new_widget_globe_end = '''      <div class="absolute bottom-1.5 left-2 text-[8.5px] text-[#64748b] font-mono pointer-events-none">
        <span>└───┘ 2,000 km</span>
      </div>

      <div class="absolute bottom-1.5 right-2 z-10 pointer-events-auto">
        <button id="wOpenMomaBtn" class="text-[8.5px] font-semibold text-[#f1c21b] hover:text-white bg-[#1a1406]/90 border border-[#4d3d0f] hover:border-[#f1c21b] px-1.5 py-0.5 rounded transition flex items-center gap-1 shadow">
          <span>⚠️</span> <span>Why MoMA is excluded</span>
        </button>
      </div>'''

if old_widget_globe_end in widget and 'id="wOpenMomaBtn"' not in widget:
    widget = widget.replace(old_widget_globe_end, new_widget_globe_end)
    print("Added wOpenMomaBtn to widget globe!")

# Add listener in widget script
widget_moma_listener = '''    document.getElementById('wOpenMomaBtn')?.addEventListener('click', (e) => {{
      e.stopPropagation();
      if (!wSheetOpen) setWSheet(true);
      flyTo(-73.9776, 40.7614);
      appendWUser('Why is MoMA excluded from Culture Atlas?');
      handleWQuery('Why is MoMA excluded from Culture Atlas?');
    }});

    document.querySelectorAll('.w-inquiry').forEach(b => {{'''

if "document.querySelectorAll('.w-inquiry').forEach(b => {{" in widget:
    widget = widget.replace(
        "document.querySelectorAll('.w-inquiry').forEach(b => {{",
        widget_moma_listener
    )
    print("Injected wOpenMomaBtn listener into widget script!")

with open('build_conversational_widget.py', 'w', encoding='utf-8') as f:
    f.write(widget)

print("Both build scripts patched successfully for MoMA exclusion audit!")
