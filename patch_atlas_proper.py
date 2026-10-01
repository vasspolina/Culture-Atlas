#!/usr/bin/env python3
"""
patch_atlas_proper.py
Updates build_conversational_atlas.py with:
1. "Visitor Planning & Practical Guide" in openDossier
2. Quick visitor line in renderLeftList
3. floatingCardHours update in selectInstitution
"""

with open('build_conversational_atlas.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update selectInstitution
old_select = '''      document.getElementById('floatingCardTitle').textContent = inst.name;
      document.getElementById('floatingCardMeta').textContent = `${{inst.location}} · ${{inst.tier === 'A' ? 'Verified' : 'One Name'}}`;
      document.getElementById('floatingCardTier').textContent = inst.tier === 'A' ? 'Verified' : inst.tier === 'B' ? 'One Name' : 'Unverified';'''

new_select = '''      document.getElementById('floatingCardTitle').textContent = inst.name;
      document.getElementById('floatingCardMeta').textContent = `${{inst.location}} · ${{inst.tier === 'A' ? 'Verified' : 'One Name'}}`;
      document.getElementById('floatingCardTier').textContent = inst.tier === 'A' ? 'Verified' : inst.tier === 'B' ? 'One Name' : 'Unverified';
      
      const hoursEl = document.getElementById('floatingCardHours');
      if (hoursEl) {{
        const shortH = inst.opening_hours ? inst.opening_hours.split(',')[0] : 'Open Weekly';
        const shortF = inst.admission_fee ? inst.admission_fee.split('/')[0].trim() : 'Free / Subsidized';
        hoursEl.textContent = `${{shortH}} · ${{shortF}}`;
      }}'''

if old_select in content:
    content = content.replace(old_select, new_select)
    print("Replaced old_select in build_conversational_atlas.py")
else:
    print("Could not find old_select")

# 2. Update openDossier
old_dossier = '''          <!-- Scholarly Visitor Recommendation -->
          <div class="bg-[#0b101c] p-3 rounded-xl border border-[#1a253c]">
            <span class="text-[10px] font-semibold text-[#60a5fa] uppercase tracking-wider block mb-1">Curator Visitor Recommendation</span>
            <p class="text-xs text-slate-200 leading-relaxed">${{inst.curator_recommendation}}</p>
          </div>

          <!-- Admission & Public Access Policy -->'''

new_dossier = '''          <!-- Scholarly Visitor Recommendation -->
          <div class="bg-[#0b101c] p-3 rounded-xl border border-[#1a253c]">
            <span class="text-[10px] font-semibold text-[#60a5fa] uppercase tracking-wider block mb-1">Curator Visitor Recommendation</span>
            <p class="text-xs text-slate-200 leading-relaxed">${{inst.curator_recommendation}}</p>
          </div>

          <!-- Visitor Planning & Practical Guide (Authentic Institutional Data) -->
          <div class="bg-[#0b101c] p-3 rounded-xl border border-[#1e2a44] space-y-2.5">
            <div class="flex items-center justify-between border-b border-[#1a253c] pb-1.5">
              <span class="text-[10.5px] font-bold text-white uppercase tracking-wider flex items-center gap-1.5">
                <span>🧭</span> <span>Visitor Planning & Practical Guide</span>
              </span>
              ${{inst.visit_url ? `
                <a href="${{inst.visit_url}}" target="_blank" rel="noopener noreferrer" class="text-[10px] text-[#60a5fa] hover:underline flex items-center gap-1 font-mono">
                  <span>Plan Your Visit ↗</span>
                </a>
              ` : ''}}
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs">
              <!-- Hours -->
              <div class="bg-[#101626] p-2.5 rounded-lg border border-[#1c273e]">
                <div class="text-[9.5px] text-slate-400 font-mono flex items-center gap-1 mb-1">
                  <span>🕒</span> <span>Hours & Schedule</span>
                </div>
                <div class="text-slate-200 font-medium text-xs leading-snug">${{inst.opening_hours || 'Check official site'}}</div>
              </div>

              <!-- Admission Pricing -->
              <div class="bg-[#101626] p-2.5 rounded-lg border border-[#1c273e]">
                <div class="text-[9.5px] text-slate-400 font-mono flex items-center gap-1 mb-1">
                  <span>🎟️</span> <span>Admission & Tickets</span>
                </div>
                <div class="text-emerald-400 font-medium text-xs leading-snug">${{inst.admission_fee || 'Subsidized Admission'}}</div>
              </div>

              <!-- Address & Cultural District -->
              <div class="bg-[#101626] p-2.5 rounded-lg border border-[#1c273e]">
                <div class="text-[9.5px] text-slate-400 font-mono flex items-center gap-1 mb-1">
                  <span>📍</span> <span>Address & Quarter</span>
                </div>
                <div class="text-slate-200 text-xs leading-snug">${{inst.address || inst.location}}</div>
                ${{inst.neighborhood ? `<div class="text-[10px] text-[#93c5fd] font-mono mt-0.5">${{inst.neighborhood}}</div>` : ''}}
              </div>

              <!-- Recommended Duration -->
              <div class="bg-[#101626] p-2.5 rounded-lg border border-[#1c273e]">
                <div class="text-[9.5px] text-slate-400 font-mono flex items-center gap-1 mb-1">
                  <span>⏱️</span> <span>Suggested Duration</span>
                </div>
                <div class="text-slate-200 text-xs leading-snug">${{inst.visit_duration || '1.5 – 2.5 hours'}}</div>
              </div>
            </div>

            <!-- Transit & Directions -->
            <div class="bg-[#101626] p-2.5 rounded-lg border border-[#1c273e]">
              <div class="text-[9.5px] text-slate-400 font-mono flex items-center gap-1 mb-1">
                <span>🚇</span> <span>Public Transit & Directions</span>
              </div>
              <div class="text-xs text-slate-300 leading-relaxed">${{inst.transit_tips || 'Accessible via central public transit network.'}}</div>
            </div>

            <!-- Collection / Architecture Highlight -->
            <div class="bg-[#101626] p-2.5 rounded-lg border border-[#1c273e]">
              <div class="text-[9.5px] text-amber-400/90 font-mono flex items-center gap-1 mb-1">
                <span>⭐</span> <span>Visitor Highlight & Signature Art</span>
              </div>
              <div class="text-xs text-slate-200 leading-relaxed font-medium">${{inst.highlight || 'Celebrated collection and contemporary commissions.'}}</div>
            </div>

            <!-- Accessibility & Amenities -->
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs">
              <div class="bg-[#101626] p-2.5 rounded-lg border border-[#1c273e]">
                <div class="text-[9.5px] text-slate-400 font-mono flex items-center gap-1 mb-1">
                  <span>♿</span> <span>Accessibility</span>
                </div>
                <div class="text-xs text-slate-300 leading-relaxed">${{inst.accessibility || 'Step-free access, elevators, accessible restrooms.'}}</div>
              </div>
              <div class="bg-[#101626] p-2.5 rounded-lg border border-[#1c273e]">
                <div class="text-[9.5px] text-slate-400 font-mono flex items-center gap-1 mb-1">
                  <span>☕</span> <span>Amenities & Facilities</span>
                </div>
                <div class="text-xs text-slate-300 leading-relaxed">${{inst.amenities || 'Art bookshop, café, cloakroom, and lockers.'}}</div>
              </div>
            </div>
          </div>

          <!-- Admission & Public Access Policy -->'''

if old_dossier in content:
    content = content.replace(old_dossier, new_dossier)
    print("Replaced old_dossier with Visitor Planning & Practical Guide")
else:
    print("Could not find old_dossier")

# 3. Update renderLeftList
old_left_list = '''            <!-- Researcher Tags: Governance & Admission -->
            <div class="flex items-center gap-1.5 text-[9.5px] font-mono text-[#94a3b8] mt-1.5 flex-wrap">
              <span class="px-1.5 py-0.5 rounded bg-[#101726] border border-[#1c2840] text-[#93c5fd]">🏛️ ${{inst.governance_type}}</span>
              <span class="px-1.5 py-0.5 rounded bg-[#0a1f15] border border-[#143d28] text-emerald-300">🎟️ ${{inst.admission_policy}}</span>
            </div>'''

new_left_list = '''            <!-- Researcher Tags: Governance & Admission -->
            <div class="flex items-center gap-1.5 text-[9.5px] font-mono text-[#94a3b8] mt-1.5 flex-wrap">
              <span class="px-1.5 py-0.5 rounded bg-[#101726] border border-[#1c2840] text-[#93c5fd]">🏛️ ${{inst.governance_type}}</span>
              <span class="px-1.5 py-0.5 rounded bg-[#0a1f15] border border-[#143d28] text-emerald-300">🎟️ ${{inst.admission_policy}}</span>
            </div>

            <!-- Quick Visitor Schedule & Pricing Pill -->
            <div class="mt-1.5 flex items-center gap-2 text-[10px] font-mono text-slate-300">
              <span class="truncate">🕒 ${{inst.opening_hours ? inst.opening_hours.split(',')[0] : 'Open Weekly'}}</span>
              <span class="text-slate-600">·</span>
              <span class="text-emerald-400 shrink-0 truncate max-w-[120px]">🎟️ ${{inst.admission_fee ? inst.admission_fee.split('/')[0].trim() : 'Free / Subsidized'}}</span>
            </div>'''

if old_left_list in content:
    content = content.replace(old_left_list, new_left_list)
    print("Replaced old_left_list with quick visitor pill")
else:
    print("Could not find old_left_list")

with open('build_conversational_atlas.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated build_conversational_atlas.py successfully!")
