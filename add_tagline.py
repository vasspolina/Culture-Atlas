path = "/Users/polinavasilyeva/.gemini/antigravity/scratch/sponsor-atlas/build_mobile_experience.py"
with open(path, "r", encoding="utf-8") as f:
    text = f.read()

# 1. Update Title and Meta
old_title = "  <title>Culture Atlas</title>"
new_title = """  <title>Culture Atlas — Ethically funded cultural institutions across the world</title>
  <meta name="description" content="Culture Atlas — Ethically funded cultural institutions across the world, mapped by who pays for them." />"""
if old_title in text:
    text = text.replace(old_title, new_title)
    print("Updated title and meta description")

# 2. Update Left List Header with the prominent mission statement
old_header = """          <div class="flex items-center justify-between">
            <div class="flex items-center gap-2">
              <div class="w-2.5 h-2.5 rounded-full bg-[#1d4ed8]"></div>
              <h1 class="text-xs font-bold tracking-wider text-[#cbd5e1] uppercase">CULTURE ATLAS</h1>
            </div>
            
            <div class="flex items-center gap-2">
              <span id="listTotalBadge" class="text-[11px] font-mono text-[#94a3b8] bg-[#161821] px-2 py-0.5 rounded border border-[#282c38]">
                203 mapped
              </span>
              <!-- Mobile Sheet Expand/Collapse Toggle Button -->
              <button id="mobileSheetToggleBtn" class="md:hidden text-xs text-[#94a3b8] hover:text-white bg-[#161821] border border-[#282c38] px-2 py-0.5 rounded flex items-center gap-1">
                <span id="sheetToggleText">Expand</span>
                <span id="sheetToggleArrow">▲</span>
              </button>
            </div>
          </div>"""

new_header = """          <div class="flex items-start justify-between gap-2">
            <div>
              <div class="flex items-center gap-2">
                <div class="w-2.5 h-2.5 rounded-full bg-[#1d4ed8] shadow-[0_0_8px_#1d4ed8]"></div>
                <h1 class="text-xs font-bold tracking-wider text-[#cbd5e1] uppercase">CULTURE ATLAS</h1>
              </div>
              <p class="text-[11px] text-[#94a3b8] mt-0.5 leading-snug font-normal">
                Ethically funded cultural institutions across the world, mapped by who pays for them.
              </p>
            </div>
            
            <div class="flex items-center gap-1.5 shrink-0 pt-0.5">
              <span id="listTotalBadge" class="text-[11px] font-mono text-[#94a3b8] bg-[#161821] px-2 py-0.5 rounded border border-[#282c38]">
                203 mapped
              </span>
              <!-- Mobile Sheet Expand/Collapse Toggle Button -->
              <button id="mobileSheetToggleBtn" class="md:hidden text-xs text-[#94a3b8] hover:text-white bg-[#161821] border border-[#282c38] px-2 py-0.5 rounded flex items-center gap-1">
                <span id="sheetToggleText">Expand</span>
                <span id="sheetToggleArrow">▲</span>
              </button>
            </div>
          </div>"""

if old_header in text:
    text = text.replace(old_header, new_header)
    print("Updated left list header with mission statement")
else:
    print("WARNING: old_header not found")

# 3. Update bottom footer banner
old_footer = """        <!-- Excluded Research / MoMA Audit Footer Button -->
        <div class="p-2.5 border-t border-[#1c212a] bg-[#0a0d14] flex items-center justify-between text-xs shrink-0">
          <span class="text-[11px] text-[#64748b]">Investigative audit:</span>
          <button id="openMomaAuditBtn" class="text-[11px] font-semibold text-[#f1c21b] hover:text-white bg-[#221c08] border border-[#4d3d0f] hover:border-[#f1c21b] px-2.5 py-1 rounded transition flex items-center gap-1.5">
            <span>⚠️</span> <span>MoMA Research Dossier</span>
          </button>
        </div>"""

new_footer = """        <!-- Mission & Criteria Bar -->
        <div class="p-2.5 border-t border-[#1c212a] bg-[#0a0d14] flex flex-col gap-1.5 text-xs shrink-0">
          <div class="flex items-center justify-between">
            <span class="text-[10.5px] text-[#94a3b8] flex items-center gap-1">
              <span>🛡️</span> <span>Zero defense & fossil fuel underwriting</span>
            </span>
            <button id="openMomaAuditBtn" class="text-[10.5px] font-semibold text-[#f1c21b] hover:text-white bg-[#221c08] border border-[#4d3d0f] hover:border-[#f1c21b] px-2 py-0.5 rounded transition flex items-center gap-1">
              <span>⚠️</span> <span>Why MoMA is excluded</span>
            </button>
          </div>
        </div>"""

if old_footer in text:
    text = text.replace(old_footer, new_footer)
    print("Updated footer with mission & criteria bar")

# 4. Update the bottom-left on the globe to show tagline as well
old_scale_bar = """        <!-- Bottom-Left Scale Bar -->
        <div class="absolute bottom-20 md:bottom-4 left-4 z-10 pointer-events-none flex flex-col gap-1 text-[10px] text-[#64748b] font-mono">
          <div class="flex items-center gap-1.5">
            <div class="w-14 sm:w-16 h-1 border-b border-l border-r border-[#64748b]"></div>
            <span>2,000 km</span>
          </div>
        </div>"""

new_scale_bar = """        <!-- Bottom-Left Title & Scale Bar -->
        <div class="absolute bottom-20 md:bottom-4 left-4 z-10 pointer-events-none flex flex-col gap-1 text-[10px] text-[#64748b] font-mono">
          <div class="text-[11px] text-[#94a3b8] font-sans font-medium hidden sm:block">
            Ethically funded cultural institutions across the world
          </div>
          <div class="flex items-center gap-1.5">
            <div class="w-14 sm:w-16 h-1 border-b border-l border-r border-[#64748b]"></div>
            <span>2,000 km</span>
          </div>
        </div>"""

if old_scale_bar in text:
    text = text.replace(old_scale_bar, new_scale_bar)
    print("Updated bottom-left title & scale bar")

with open(path, "w", encoding="utf-8") as f:
    f.write(text)

print("Saved updated build_mobile_experience.py!")
