import re

path = "/Users/polinavasilyeva/.gemini/antigravity/scratch/sponsor-atlas/build_split_screen_atlas.py"
with open(path, "r", encoding="utf-8") as f:
    text = f.read()

# 1. Update Left List Card Template in main app
old_card_tpl = """          <div class="inst-card bg-[#0b0e16] border border-[#1b202d] rounded-xl p-3 cursor-pointer hover:border-[#3b82f6] hover:bg-[#101420] ${{isSel ? 'active' : ''}}" data-name="${{inst.name.replace(/"/g, '&quot;')}}">
            <div class="flex items-start justify-between gap-2">
              <h3 class="font-semibold text-white text-xs leading-snug truncate max-w-[240px]">${{inst.name}}</h3>
              <span class="text-[9px] font-mono px-1.5 py-0.5 rounded border ${{tierCol}} shrink-0">${{tierName}}</span>
            </div>
            <div class="flex items-center gap-1.5 text-[11px] text-[#60a5fa] mt-1 font-mono">
              <span>📍</span> <span>${{inst.location}}</span>
              <span class="text-slate-600">·</span>
              <span class="text-slate-400 text-[10px]">${{inst.size === 'L' ? 'Large (>$20M)' : 'Small/Mid'}}</span>
            </div>
            <p class="text-[11px] text-slate-400 mt-1.5 leading-relaxed line-clamp-2">${{inst.funding}}</p>
            ${{inst.watch ? `
              <div class="mt-2 pt-1.5 border-t border-[#161a26] text-[10px] text-amber-300/80 truncate flex items-center gap-1">
                <span>⚠️</span> <span>${{inst.watch}}</span>
              </div>
            ` : ''}}
          </div>"""

new_card_tpl = """          let displayDomain = '';
          try {{
            displayDomain = new URL(inst.website || inst.sources[0]).hostname.replace(/^www\\./, '');
          }} catch(e) {{
            displayDomain = 'website';
          }}

          return `
          <div class="inst-card bg-[#0b0e16] border border-[#1b202d] rounded-xl p-3 cursor-pointer hover:border-[#3b82f6] hover:bg-[#101420] ${{isSel ? 'active' : ''}}" data-name="${{inst.name.replace(/"/g, '&quot;')}}">
            <div class="flex items-start justify-between gap-2">
              <h3 class="font-semibold text-white text-xs leading-snug truncate max-w-[240px]">${{inst.name}}</h3>
              <span class="text-[9px] font-mono px-1.5 py-0.5 rounded border ${{tierCol}} shrink-0">${{tierName}}</span>
            </div>
            <div class="flex items-center gap-1.5 text-[11px] text-[#60a5fa] mt-1 font-mono">
              <span>📍</span> <span>${{inst.location}}</span>
              <span class="text-slate-600">·</span>
              <span class="text-slate-400 text-[10px]">${{inst.size === 'L' ? 'Large (>$20M)' : 'Small/Mid'}}</span>
            </div>
            <p class="text-[11px] text-slate-400 mt-1.5 leading-relaxed line-clamp-2">${{inst.funding}}</p>
            ${{inst.watch ? `
              <div class="mt-2 pt-1.5 border-t border-[#161a26] text-[10px] text-amber-300/80 truncate flex items-center gap-1">
                <span>⚠️</span> <span>${{inst.watch}}</span>
              </div>
            ` : ''}}
            <div class="mt-2.5 pt-2 border-t border-[#161b26] flex items-center justify-between">
              <a href="${{inst.website || inst.sources[0]}}" target="_blank" rel="noopener noreferrer" 
                 class="website-pill inline-flex items-center gap-1.5 text-[10.5px] font-mono text-[#60a5fa] hover:text-white bg-[#101726] hover:bg-[#1a253c] border border-[#1e2a42] hover:border-[#3b82f6] px-2 py-0.5 rounded transition"
                 onclick="event.stopPropagation()">
                <span>🌐</span>
                <span class="truncate max-w-[130px]">${{displayDomain}}</span>
                <span class="text-[9px]">↗</span>
              </a>
              <span class="text-[10px] text-slate-500 hover:text-slate-300 font-mono">View on Globe →</span>
            </div>
          </div>`;"""

if old_card_tpl in text:
    text = text.replace(old_card_tpl, new_card_tpl)
    print("Replaced Left List Card Template")
else:
    print("WARNING: old_card_tpl not found")

# 2. Update Floating Card HTML in main app
old_floating_card = """      <!-- FLOATING WHITE CARD (Pinned to selected institution) -->
      <div id="floatingCard" class="absolute z-30 pointer-events-auto bg-white text-slate-900 rounded-lg px-3.5 py-2.5 shadow-2xl transition duration-150 transform -translate-x-1/2 -translate-y-full mb-3 cursor-pointer border border-slate-100 max-w-[240px]">
        <div class="flex items-center justify-between gap-2">
          <div id="floatingCardTitle" class="font-bold text-[13px] text-slate-950 leading-tight">Plug In ICA</div>
          <span id="floatingCardTier" class="text-[9px] font-semibold uppercase px-1.5 py-0.5 bg-emerald-100 text-emerald-800 rounded">Verified</span>
        </div>
        <div id="floatingCardMeta" class="text-[11px] text-slate-500 mt-0.5 flex items-center gap-1">
          <span>Winnipeg, Canada</span>
        </div>
        <div class="absolute bottom-0 left-1/2 -translate-x-1/2 translate-y-full w-0 h-0 border-x-[6px] border-x-transparent border-t-[6px] border-t-white"></div>
      </div>"""

new_floating_card = """      <!-- FLOATING WHITE CARD (Pinned to selected institution with Website link) -->
      <div id="floatingCard" class="absolute z-30 pointer-events-auto bg-white text-slate-900 rounded-lg px-3.5 py-2.5 shadow-2xl transition duration-150 transform -translate-x-1/2 -translate-y-full mb-3 cursor-pointer border border-slate-100 max-w-[250px]">
        <div class="flex items-center justify-between gap-2">
          <div id="floatingCardTitle" class="font-bold text-[13px] text-slate-950 leading-tight">Plug In ICA</div>
          <span id="floatingCardTier" class="text-[9px] font-semibold uppercase px-1.5 py-0.5 bg-emerald-100 text-emerald-800 rounded">Verified</span>
        </div>
        <div id="floatingCardMeta" class="text-[11px] text-slate-500 mt-0.5 flex items-center gap-1">
          <span>Winnipeg, Canada</span>
        </div>
        <div class="mt-1.5 pt-1.5 border-t border-slate-100 flex items-center justify-between text-[11px]">
          <a id="floatingCardWebLink" href="https://plugin.org" target="_blank" rel="noopener noreferrer" 
             class="inline-flex items-center gap-1 font-medium text-[#1d4ed8] hover:text-[#1e40af] hover:underline"
             onclick="event.stopPropagation()">
            <span>🌐</span> <span id="floatingCardDomain">plugin.org</span> <span class="text-[9px]">↗</span>
          </a>
          <span class="text-[10px] text-slate-400 font-mono">Dossier →</span>
        </div>
        <div class="absolute bottom-0 left-1/2 -translate-x-1/2 translate-y-full w-0 h-0 border-x-[6px] border-x-transparent border-t-[6px] border-t-white"></div>
      </div>"""

if old_floating_card in text:
    text = text.replace(old_floating_card, new_floating_card)
    print("Replaced Floating Card HTML")

# 3. Update selectInstitution to set floating card website link
old_select_inst = """    function selectInstitution(inst) {{
      selectedInstitution = inst;
      document.getElementById('floatingCardTitle').textContent = inst.name;
      document.getElementById('floatingCardMeta').textContent = `${{inst.location}} · ${{inst.tier === 'A' ? 'Verified' : 'One Name'}}`;
      document.getElementById('floatingCardTier').textContent = inst.tier === 'A' ? 'Verified' : inst.tier === 'B' ? 'One Name' : 'Unverified';"""

new_select_inst = """    function selectInstitution(inst) {{
      selectedInstitution = inst;
      document.getElementById('floatingCardTitle').textContent = inst.name;
      document.getElementById('floatingCardMeta').textContent = `${{inst.location}} · ${{inst.tier === 'A' ? 'Verified' : 'One Name'}}`;
      document.getElementById('floatingCardTier').textContent = inst.tier === 'A' ? 'Verified' : inst.tier === 'B' ? 'One Name' : 'Unverified';

      // Update website link
      const webUrl = inst.website || (inst.sources && inst.sources[0]) || '';
      let domain = 'website';
      try {{ domain = new URL(webUrl).hostname.replace(/^www\\./, ''); }} catch(e) {{}}
      const webEl = document.getElementById('floatingCardWebLink');
      const domEl = document.getElementById('floatingCardDomain');
      if (webEl && domEl) {{
        webEl.href = webUrl;
        domEl.textContent = domain;
      }}"""

if old_select_inst in text:
    text = text.replace(old_select_inst, new_select_inst)
    print("Updated selectInstitution with website link")

# 4. Update openDossier with website button
old_open_dossier = """        <div>
          <h2 class="text-lg font-bold text-white leading-snug">${{inst.name}}</h2>
          <p class="text-xs text-[#3b82f6] mt-0.5 font-mono">${{inst.location}} · ${{inst.size === 'L' ? 'Large (>$20M)' : 'Small/Mid'}}</p>
        </div>"""

new_open_dossier = """        let domain = 'website';
        const webUrl = inst.website || (inst.sources && inst.sources[0]) || '';
        try {{ domain = new URL(webUrl).hostname.replace(/^www\\./, ''); }} catch(e) {{}}

        body.innerHTML = `
        <div>
          <h2 class="text-lg font-bold text-white leading-snug">${{inst.name}}</h2>
          <p class="text-xs text-[#3b82f6] mt-0.5 font-mono">${{inst.location}} · ${{inst.size === 'L' ? 'Large (>$20M)' : 'Small/Mid'}}</p>
        </div>
        ${{webUrl ? `
          <a href="${{webUrl}}" target="_blank" rel="noopener noreferrer" 
             class="inline-flex items-center justify-center gap-2 w-full py-2 bg-[#1d4ed8] hover:bg-[#2563eb] text-white font-semibold text-xs rounded-lg transition shadow-md">
            <span>🌐</span> <span>Visit Official Website (${{domain}})</span> <span>↗</span>
          </a>
        ` : ''}}"""

if old_open_dossier in text:
    text = text.replace(old_open_dossier, new_open_dossier)
    print("Updated openDossier with official website button")

# 5. Also update widget card template
old_w_card = """          <div class="widget-item bg-[#0d1017] border border-[#1a202c] rounded-lg p-2 cursor-pointer hover:border-[#3b82f6] ${{isSel ? 'active' : ''}}" data-name="${{inst.name.replace(/"/g, '&quot;')}}">
            <div class="flex items-center justify-between">
              <span class="font-semibold text-white text-[11px] truncate max-w-[140px]">${{inst.name}}</span>
              <span class="text-[9px] px-1 py-0.2 rounded border ${{inst.tier === 'A' ? 'bg-[#092015] text-emerald-400 border-emerald-900' : 'bg-[#0a1b30] text-blue-400 border-blue-900'}}">${{inst.tier === 'A' ? 'Verified' : 'One Name'}}</span>
            </div>
            <div class="text-[10px] text-[#60a5fa] mt-0.5 truncate">${{inst.location}}</div>
          </div>"""

new_w_card = """          let dom = 'website';
          try {{ dom = new URL(inst.website || inst.sources[0]).hostname.replace(/^www\\./, ''); }} catch(e) {{}}
          return `
          <div class="widget-item bg-[#0d1017] border border-[#1a202c] rounded-lg p-2 cursor-pointer hover:border-[#3b82f6] ${{isSel ? 'active' : ''}}" data-name="${{inst.name.replace(/"/g, '&quot;')}}">
            <div class="flex items-center justify-between">
              <span class="font-semibold text-white text-[11px] truncate max-w-[140px]">${{inst.name}}</span>
              <span class="text-[9px] px-1 py-0.2 rounded border ${{inst.tier === 'A' ? 'bg-[#092015] text-emerald-400 border-emerald-900' : 'bg-[#0a1b30] text-blue-400 border-blue-900'}}">${{inst.tier === 'A' ? 'Verified' : 'One Name'}}</span>
            </div>
            <div class="flex items-center justify-between mt-1 text-[10px]">
              <span class="text-[#60a5fa] truncate max-w-[110px]">${{inst.location}}</span>
              <a href="${{inst.website || inst.sources[0]}}" target="_blank" rel="noopener noreferrer" 
                 class="text-[#3b82f6] hover:underline flex items-center gap-0.5" onclick="event.stopPropagation()">
                <span>🌐</span> <span class="truncate max-w-[70px]">${{dom}}</span> <span>↗</span>
              </a>
            </div>
          </div>`;"""

if old_w_card in text:
    text = text.replace(old_w_card, new_w_card)
    print("Updated widget card template with website link")

# 6. Update widget floating card
old_w_float = """        <div id="wCard" class="absolute z-30 pointer-events-auto bg-white text-slate-900 rounded-lg px-2.5 py-1.5 shadow-xl transition transform -translate-x-1/2 -translate-y-full mb-2 cursor-pointer border border-slate-100 max-w-[190px]">
          <div class="font-bold text-[11px] text-slate-950 leading-tight" id="wCardTitle">Plug In ICA</div>
          <div class="text-[9.5px] text-slate-500 mt-0.5" id="wCardMeta">Winnipeg, Canada · Verified</div>
          <div class="absolute bottom-0 left-1/2 -translate-x-1/2 translate-y-full w-0 h-0 border-x-[5px] border-x-transparent border-t-[5px] border-t-white"></div>
        </div>"""

new_w_float = """        <div id="wCard" class="absolute z-30 pointer-events-auto bg-white text-slate-900 rounded-lg px-2.5 py-1.5 shadow-xl transition transform -translate-x-1/2 -translate-y-full mb-2 cursor-pointer border border-slate-100 max-w-[200px]">
          <div class="font-bold text-[11px] text-slate-950 leading-tight" id="wCardTitle">Plug In ICA</div>
          <div class="text-[9.5px] text-slate-500 mt-0.5" id="wCardMeta">Winnipeg, Canada · Verified</div>
          <div class="mt-1 pt-1 border-t border-slate-100 flex items-center justify-between text-[9.5px]">
            <a id="wCardLink" href="https://plugin.org" target="_blank" rel="noopener noreferrer" 
               class="text-[#1d4ed8] hover:underline flex items-center gap-1 font-medium" onclick="event.stopPropagation()">
              <span>🌐</span> <span id="wCardDom">plugin.org</span> <span>↗</span>
            </a>
          </div>
          <div class="absolute bottom-0 left-1/2 -translate-x-1/2 translate-y-full w-0 h-0 border-x-[5px] border-x-transparent border-t-[5px] border-t-white"></div>
        </div>"""

if old_w_float in text:
    text = text.replace(old_w_float, new_w_float)
    print("Updated widget floating card")

# 7. Update widget selectInst
old_w_select = """    function selectInst(inst) {{
      selectedInst = inst;
      document.getElementById('wCardTitle').textContent = inst.name;
      document.getElementById('wCardMeta').textContent = `${{inst.location}} · ${{inst.tier === 'A' ? 'Verified' : 'One Name'}}`;
      flyTo(inst.lon, inst.lat);
      applyWFilters();
    }}"""

new_w_select = """    function selectInst(inst) {{
      selectedInst = inst;
      document.getElementById('wCardTitle').textContent = inst.name;
      document.getElementById('wCardMeta').textContent = `${{inst.location}} · ${{inst.tier === 'A' ? 'Verified' : 'One Name'}}`;
      const webUrl = inst.website || (inst.sources && inst.sources[0]) || '';
      let dom = 'website';
      try {{ dom = new URL(webUrl).hostname.replace(/^www\\./, ''); }} catch(e) {{}}
      const lk = document.getElementById('wCardLink');
      const dm = document.getElementById('wCardDom');
      if (lk && dm) {{
        lk.href = webUrl;
        dm.textContent = dom;
      }}
      flyTo(inst.lon, inst.lat);
      applyWFilters();
    }}"""

if old_w_select in text:
    text = text.replace(old_w_select, new_w_select)
    print("Updated widget selectInst")

with open(path, "w", encoding="utf-8") as f:
    f.write(text)

print("Saved updated build_split_screen_atlas.py with website integrations!")
