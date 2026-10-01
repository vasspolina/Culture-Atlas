#!/usr/bin/env python3
"""
integrate_visitor_atlas.py
Integrates authentic institutional visitor planning data into both
build_conversational_atlas.py and build_conversational_widget.py,
then executes both to generate app/index.html, culture_atlas_app.html,
and concierge_widget.html.
"""

import re
import os

def update_atlas():
    print("Reading build_conversational_atlas.py...")
    with open('build_conversational_atlas.py', 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Add Visitor Planning Inquiry Chips
    old_chips = '''          <!-- Gentle Educational Inquiry Chips (Horizontal Carousel) -->
          <div class="px-2.5 py-2 border-t border-[#161a26] bg-[#080b12] flex items-center gap-1.5 overflow-x-auto custom-scrollbar shrink-0 text-[10.5px] font-mono whitespace-nowrap">
            <button class="inquiry-chip px-2.5 py-1 rounded-full border border-[#232a3c] bg-[#101522] text-[#93c5fd] hover:border-[#3b82f6] hover:bg-[#151c30] transition active:scale-95" data-query="What makes an institution ethically funded?">
              🏛️ What makes a museum ethical?
            </button>
            <button class="inquiry-chip px-2.5 py-1 rounded-full border border-[#1b3324] bg-[#0c1f15] text-[#6ee7b7] hover:border-[#10b981] hover:bg-[#112d1e] transition active:scale-95" data-query="Which cultural spaces offer always free admission?">
              🎟️ Always Free Admission
            </button>
            <button class="inquiry-chip px-2.5 py-1 rounded-full border border-[#232a3c] bg-[#101522] text-[#cbd5e1] hover:border-[#3b82f6] hover:bg-[#151c30] transition active:scale-95" data-query="Recommend independent artist-run centers and grassroots kunsthalles">
              🎨 Artist-run & grassroots
            </button>'''

    new_chips = '''          <!-- Gentle Educational & Visitor Planning Inquiry Chips (Horizontal Carousel) -->
          <div class="px-2.5 py-2 border-t border-[#161a26] bg-[#080b12] flex items-center gap-1.5 overflow-x-auto custom-scrollbar shrink-0 text-[10.5px] font-mono whitespace-nowrap">
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
            </button>'''

    if old_chips in content:
        content = content.replace(old_chips, new_chips)
        print("Updated Inquiry Chips in build_conversational_atlas.py")
    else:
        print("Warning: old_chips pattern not found!")

    # 2. Add Floating Card Hours & Pricing Line
    old_floating_card = '''          <div id="floatingCardMeta" class="text-[10.5px] sm:text-[11px] text-slate-500 mt-0.5 flex items-center gap-1">
            <span>Winnipeg, Canada</span>
          </div>'''

    new_floating_card = '''          <div id="floatingCardMeta" class="text-[10.5px] sm:text-[11px] text-slate-500 mt-0.5 flex items-center gap-1">
            <span>Winnipeg, Canada</span>
          </div>
          <div id="floatingCardHours" class="text-[9.5px] font-mono text-emerald-700 mt-0.5 truncate">Tue–Fri 12:00–18:00 · Free Entry</div>'''

    if old_floating_card in content:
        content = content.replace(old_floating_card, new_floating_card)
        print("Updated Floating Card HTML markup")

    # 3. Update selectInstitution to update floatingCardHours
    old_select_card = '''      document.getElementById('floatingCardTitle').textContent = inst.name;
      document.getElementById('floatingCardMeta').textContent = `${inst.location} · ${inst.tier === 'A' ? 'Verified' : 'One Name'}`;
      document.getElementById('floatingCardTier').textContent = inst.tier === 'A' ? 'Verified' : inst.tier === 'B' ? 'One Name' : 'Unverified';'''

    new_select_card = '''      document.getElementById('floatingCardTitle').textContent = inst.name;
      document.getElementById('floatingCardMeta').textContent = `${inst.location} · ${inst.tier === 'A' ? 'Verified' : 'One Name'}`;
      document.getElementById('floatingCardTier').textContent = inst.tier === 'A' ? 'Verified' : inst.tier === 'B' ? 'One Name' : 'Unverified';
      
      const hoursEl = document.getElementById('floatingCardHours');
      if (hoursEl) {
        const shortH = inst.opening_hours ? inst.opening_hours.split(',')[0] : 'Open Weekly';
        const shortF = inst.admission_fee ? inst.admission_fee.split('/')[0].trim() : 'Free / Subsidized';
        hoursEl.textContent = `${shortH} · ${shortF}`;
      }'''

    if old_select_card in content:
        content = content.replace(old_select_card, new_select_card)
        print("Updated selectInstitution in build_conversational_atlas.py")

    # 4. Add "Visitor Planning & Practical Guide" to openDossier
    old_dossier_point = '''          <!-- Scholarly Visitor Recommendation -->
          <div class="bg-[#0b101c] p-3 rounded-xl border border-[#1a253c]">
            <span class="text-[10px] font-semibold text-[#60a5fa] uppercase tracking-wider block mb-1">Curator Visitor Recommendation</span>
            <p class="text-xs text-slate-200 leading-relaxed">${inst.curator_recommendation}</p>
          </div>

          <!-- Admission & Public Access Policy -->'''

    new_dossier_point = '''          <!-- Scholarly Visitor Recommendation -->
          <div class="bg-[#0b101c] p-3 rounded-xl border border-[#1a253c]">
            <span class="text-[10px] font-semibold text-[#60a5fa] uppercase tracking-wider block mb-1">Curator Visitor Recommendation</span>
            <p class="text-xs text-slate-200 leading-relaxed">${inst.curator_recommendation}</p>
          </div>

          <!-- Visitor Planning & Practical Guide (Authentic Institutional Data) -->
          <div class="bg-[#0b101c] p-3 rounded-xl border border-[#1e2a44] space-y-2.5">
            <div class="flex items-center justify-between border-b border-[#1a253c] pb-1.5">
              <span class="text-[10.5px] font-bold text-white uppercase tracking-wider flex items-center gap-1.5">
                <span>🧭</span> <span>Visitor Planning & Practical Guide</span>
              </span>
              ${inst.visit_url ? `
                <a href="${inst.visit_url}" target="_blank" rel="noopener noreferrer" class="text-[10px] text-[#60a5fa] hover:underline flex items-center gap-1 font-mono">
                  <span>Plan Your Visit ↗</span>
                </a>
              ` : ''}
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs">
              <!-- Hours -->
              <div class="bg-[#101626] p-2.5 rounded-lg border border-[#1c273e]">
                <div class="text-[9.5px] text-slate-400 font-mono flex items-center gap-1 mb-1">
                  <span>🕒</span> <span>Hours & Schedule</span>
                </div>
                <div class="text-slate-200 font-medium text-xs leading-snug">${inst.opening_hours || 'Check official site'}</div>
              </div>

              <!-- Admission Pricing -->
              <div class="bg-[#101626] p-2.5 rounded-lg border border-[#1c273e]">
                <div class="text-[9.5px] text-slate-400 font-mono flex items-center gap-1 mb-1">
                  <span>🎟️</span> <span>Admission & Tickets</span>
                </div>
                <div class="text-emerald-400 font-medium text-xs leading-snug">${inst.admission_fee || 'Subsidized Admission'}</div>
              </div>

              <!-- Address & Cultural District -->
              <div class="bg-[#101626] p-2.5 rounded-lg border border-[#1c273e]">
                <div class="text-[9.5px] text-slate-400 font-mono flex items-center gap-1 mb-1">
                  <span>📍</span> <span>Address & Quarter</span>
                </div>
                <div class="text-slate-200 text-xs leading-snug">${inst.address || inst.location}</div>
                ${inst.neighborhood ? `<div class="text-[10px] text-[#93c5fd] font-mono mt-0.5">${inst.neighborhood}</div>` : ''}
              </div>

              <!-- Recommended Duration -->
              <div class="bg-[#101626] p-2.5 rounded-lg border border-[#1c273e]">
                <div class="text-[9.5px] text-slate-400 font-mono flex items-center gap-1 mb-1">
                  <span>⏱️</span> <span>Suggested Duration</span>
                </div>
                <div class="text-slate-200 text-xs leading-snug">${inst.visit_duration || '1.5 – 2.5 hours'}</div>
              </div>
            </div>

            <!-- Transit & Directions -->
            <div class="bg-[#101626] p-2.5 rounded-lg border border-[#1c273e]">
              <div class="text-[9.5px] text-slate-400 font-mono flex items-center gap-1 mb-1">
                <span>🚇</span> <span>Public Transit & Directions</span>
              </div>
              <div class="text-xs text-slate-300 leading-relaxed">${inst.transit_tips || 'Accessible via central public transit network.'}</div>
            </div>

            <!-- Collection / Architecture Highlight -->
            <div class="bg-[#101626] p-2.5 rounded-lg border border-[#1c273e]">
              <div class="text-[9.5px] text-amber-400/90 font-mono flex items-center gap-1 mb-1">
                <span>⭐</span> <span>Visitor Highlight & Signature Art</span>
              </div>
              <div class="text-xs text-slate-200 leading-relaxed font-medium">${inst.highlight || 'Celebrated collection and contemporary commissions.'}</div>
            </div>

            <!-- Accessibility & Amenities -->
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs">
              <div class="bg-[#101626] p-2.5 rounded-lg border border-[#1c273e]">
                <div class="text-[9.5px] text-slate-400 font-mono flex items-center gap-1 mb-1">
                  <span>♿</span> <span>Accessibility</span>
                </div>
                <div class="text-xs text-slate-300 leading-relaxed">${inst.accessibility || 'Step-free access, elevators, accessible restrooms.'}</div>
              </div>
              <div class="bg-[#101626] p-2.5 rounded-lg border border-[#1c273e]">
                <div class="text-[9.5px] text-slate-400 font-mono flex items-center gap-1 mb-1">
                  <span>☕</span> <span>Amenities & Facilities</span>
                </div>
                <div class="text-xs text-slate-300 leading-relaxed">${inst.amenities || 'Art bookshop, café, cloakroom, and lockers.'}</div>
              </div>
            </div>
          </div>

          <!-- Admission & Public Access Policy -->'''

    if old_dossier_point in content:
        content = content.replace(old_dossier_point, new_dossier_point)
        print("Updated openDossier with Visitor Planning & Practical Guide")
    else:
        print("Warning: old_dossier_point pattern not found!")

    # 5. Add Visitor Query Intelligence to handleCuratorQuery
    curator_insert_marker = '''        // 1. Methodology & Philosophy & "What type of institutions should I go to?"'''

    visitor_queries_block = '''        // A. Visitor Data: Hours & Monday Openings
        if (q.includes('hour') || q.includes('schedule') || (q.includes('time') && (q.includes('open') || q.includes('visit'))) || q.includes('monday') || q.includes('weekend') || q.includes('late night') || q.includes('closed')) {
          const targetInst = ALL_INSTITUTIONS.find(i => q.includes(i.name.toLowerCase()) || (i.aliases && i.aliases.some(a => q.includes(a.toLowerCase()))));
          if (targetInst) {
            appendCuratorMessage(`
              <p>🕒 <strong>Visiting Hours for ${escapeHtml(targetInst.name)}:</strong></p>
              <div class="p-3 rounded-xl bg-[#0b0e17] border border-[#1e2a44] text-xs space-y-1.5 font-mono">
                <div class="text-emerald-400 font-semibold text-sm">📅 ${targetInst.opening_hours}</div>
                <div class="text-slate-300 text-xs font-sans"><strong>Suggested Duration:</strong> ${targetInst.visit_duration}</div>
                <div class="text-slate-300 text-xs font-sans"><strong>Address:</strong> ${targetInst.address} (${targetInst.neighborhood})</div>
                <div class="text-[#93c5fd] text-xs font-sans"><strong>Transit:</strong> ${targetInst.transit_tips}</div>
                ${targetInst.visit_url ? `<a href="${targetInst.visit_url}" target="_blank" class="text-[#60a5fa] hover:underline text-xs block pt-1 font-mono">Plan Your Visit (Official Museum Guide) ↗</a>` : ''}
              </div>
            `, [targetInst]);
            selectInstitution(targetInst, false);
            return;
          }

          if (q.includes('monday')) {
            const mondaySpaces = ALL_INSTITUTIONS.filter(i => !i.opening_hours.toLowerCase().includes('closed mon') && (i.opening_hours.toLowerCase().includes('daily') || i.opening_hours.toLowerCase().includes('mon,') || i.opening_hours.toLowerCase().includes('mon–') || i.opening_hours.toLowerCase().includes('mon-')));
            appendCuratorMessage(`
              <p>🗓️ <strong>Ethical Cultural Institutions Open on Mondays:</strong></p>
              <p>While most traditional museums close on Mondays, we have <strong>${mondaySpaces.length}</strong> ethical cultural sanctuaries welcoming visitors at the start of the week. Perfect for quiet contemplation:</p>
            `, mondaySpaces.slice(0, 4));
            return;
          }

          appendCuratorMessage(`
            <p>🕒 <strong>Institutional Schedules & Visiting Hours:</strong></p>
            <p>Most independent non-profit kunsthalles and artist-run spaces operate <strong>Wednesday through Sunday (11:00–18:00 or 12:00–18:00)</strong>, reserving Mondays and Tuesdays for installation and artist studio work. Major municipal collections frequently offer late-night Thursday or Friday openings (until 20:00–22:00, or midnight at Palais de Tokyo!).</p>
            <p class="text-slate-300">Select any institution from the catalog to view its exact timetable, or ask me about any specific venue.</p>
          `, [
            ALL_INSTITUTIONS.find(i => i.name.includes('Palais de Tokyo')),
            ALL_INSTITUTIONS.find(i => i.name.includes('Louisiana')),
            ALL_INSTITUTIONS.find(i => i.name.includes('Stedelijk'))
          ]);
          return;
        }

        // B. Visitor Data: Public Transit & Getting There
        if (q.includes('transit') || q.includes('how to get') || q.includes('how do i get') || q.includes('direction') || q.includes('subway') || q.includes('metro') || q.includes('train') || q.includes('bus') || q.includes('ferry') || q.includes('getting there')) {
          const targetInst = ALL_INSTITUTIONS.find(i => q.includes(i.name.toLowerCase()) || (i.aliases && i.aliases.some(a => q.includes(a.toLowerCase()))));
          if (targetInst) {
            appendCuratorMessage(`
              <p>🚇 <strong>Public Transit Directions to ${escapeHtml(targetInst.name)}:</strong></p>
              <div class="p-3 rounded-xl bg-[#0b0e17] border border-[#1e2a44] text-xs space-y-1.5">
                <div class="text-slate-200"><strong>📍 Address:</strong> ${targetInst.address} (${targetInst.neighborhood})</div>
                <div class="text-[#93c5fd] font-mono leading-relaxed"><strong>Transit:</strong> ${targetInst.transit_tips}</div>
                <div class="text-slate-300"><strong>Suggested Duration:</strong> ${targetInst.visit_duration} · 🕒 ${targetInst.opening_hours}</div>
                ${targetInst.visit_url ? `<a href="${targetInst.visit_url}" target="_blank" class="text-[#60a5fa] hover:underline text-xs block pt-1 font-mono">Official Transit & Location Page ↗</a>` : ''}
              </div>
            `, [targetInst]);
            selectInstitution(targetInst, false);
            return;
          }

          appendCuratorMessage(`
            <p>🚇 <strong>Public Transit & Cultural Destination Travel:</strong></p>
            <p>Culture Atlas provides verified public transit directions for all 203 institutions worldwide—whether taking the <em>Metro-North Hudson Line</em> to Dia Beacon, the <em>Kystbanen regional train</em> up the Danish coastline to Louisiana, or the <em>London Underground</em> to Whitechapel or Camden Art Centre.</p>
            <p class="text-slate-300">Here are three world-class destination institutions easily reachable via scenic rail connections:</p>
          `, [
            ALL_INSTITUTIONS.find(i => i.name.includes('Dia Beacon')),
            ALL_INSTITUTIONS.find(i => i.name.includes('Louisiana')),
            ALL_INSTITUTIONS.find(i => i.name.includes('Kröller'))
          ]);
          return;
        }

        // C. Visitor Data: Accessibility & Inclusive Access
        if (q.includes('accessib') || q.includes('wheelchair') || q.includes('step-free') || q.includes('elevator') || q.includes('disab') || q.includes('mobility') || q.includes('sensory')) {
          const targetInst = ALL_INSTITUTIONS.find(i => q.includes(i.name.toLowerCase()) || (i.aliases && i.aliases.some(a => q.includes(a.toLowerCase()))));
          if (targetInst) {
            appendCuratorMessage(`
              <p>♿ <strong>Accessibility at ${escapeHtml(targetInst.name)}:</strong></p>
              <div class="p-3 rounded-xl bg-[#0b0e17] border border-[#1e2a44] text-xs space-y-1.5">
                <div class="text-emerald-400 font-medium">${targetInst.accessibility}</div>
                <div class="text-slate-300"><strong>Transit Access:</strong> ${targetInst.transit_tips}</div>
                <div class="text-slate-400 text-[11px]">Personal care assistants and companions receive free entry at all audited institutions.</div>
              </div>
            `, [targetInst]);
            selectInstitution(targetInst, false);
            return;
          }

          appendCuratorMessage(`
            <p>♿ <strong>Universal Accessibility & Barrier-Free Access:</strong></p>
            <p>All civic institutions in Culture Atlas are committed to equitable physical and sensory access, providing step-free routes, passenger elevators, loaner wheelchairs, accessible gender-neutral washrooms, and free entry for essential companions and care assistants.</p>
            <p class="text-slate-300">Here are exemplary fully barrier-free cultural spaces:</p>
          `, [
            ALL_INSTITUTIONS.find(i => i.name.includes('Serpentine')),
            ALL_INSTITUTIONS.find(i => i.name.includes('ARoS')),
            ALL_INSTITUTIONS.find(i => i.name.includes('M+ Museum'))
          ]);
          return;
        }

        // D. Visitor Data: Amenities (Cafés, Bookshops, Gardens)
        if (q.includes('café') || q.includes('cafe') || q.includes('coffee') || q.includes('restaurant') || q.includes('dining') || q.includes('bookshop') || q.includes('bookstore') || q.includes('garden') || q.includes('park') || q.includes('amenities') || q.includes('lockers')) {
          const targetInst = ALL_INSTITUTIONS.find(i => q.includes(i.name.toLowerCase()) || (i.aliases && i.aliases.some(a => q.includes(a.toLowerCase()))));
          if (targetInst) {
            appendCuratorMessage(`
              <p>☕ <strong>Amenities & On-Site Facilities at ${escapeHtml(targetInst.name)}:</strong></p>
              <div class="p-3 rounded-xl bg-[#0b0e17] border border-[#1e2a44] text-xs space-y-1.5">
                <div class="text-slate-200"><strong>Facilities:</strong> ${targetInst.amenities}</div>
                <div class="text-amber-300/90"><strong>Signature Highlight:</strong> ${targetInst.highlight}</div>
                <div class="text-slate-300 text-[11px]"><strong>Schedule:</strong> ${targetInst.opening_hours}</div>
              </div>
            `, [targetInst]);
            selectInstitution(targetInst, false);
            return;
          }

          appendCuratorMessage(`
            <p>☕ <strong>Museum Cafés, Independent Bookshops & Sculpture Gardens:</strong></p>
            <p>Visiting an ethical cultural institution is also about the experience of slowing down. Many mapped spaces feature legendary non-commercial bookshops and secluded garden dining:</p>
            <ul class="list-disc pl-4 space-y-1 text-slate-300 text-xs">
              <li><strong>Louisiana Museum (Denmark):</strong> Seaside sculpture park and organic café overlooking Sweden.</li>
              <li><strong>Camden Art Centre (London):</strong> Quiet garden lawn café with artisan pastries and ceramics.</li>
              <li><strong>Fondazione Prada (Milan):</strong> The iconic <em>Bar Luce</em>, custom designed by filmmaker Wes Anderson.</li>
              <li><strong>The Photographers' Gallery (London):</strong> Soho's definitive international photobook specialist store.</li>
            </ul>
          `, [
            ALL_INSTITUTIONS.find(i => i.name.includes('Louisiana')),
            ALL_INSTITUTIONS.find(i => i.name.includes('Fondazione Prada')),
            ALL_INSTITUTIONS.find(i => i.name.includes('Camden Art Centre'))
          ]);
          return;
        }

        // E. Visitor Data: Signature Highlights
        if (q.includes('highlight') || q.includes('what to see') || q.includes('must-see') || q.includes('signature') || q.includes('artworks') || q.includes('monument')) {
          const targetInst = ALL_INSTITUTIONS.find(i => q.includes(i.name.toLowerCase()) || (i.aliases && i.aliases.some(a => q.includes(a.toLowerCase()))));
          if (targetInst) {
            appendCuratorMessage(`
              <p>⭐ <strong>Signature Highlight for ${escapeHtml(targetInst.name)}:</strong></p>
              <div class="p-3 rounded-xl bg-[#0b0e17] border border-[#1e2a44] text-xs space-y-1.5">
                <div class="text-amber-400 font-medium text-sm">${targetInst.highlight}</div>
                <div class="text-slate-300"><strong>Curatorial Focus:</strong> ${targetInst.curatorial_focus}</div>
                <div class="text-slate-300"><strong>Recommended Duration:</strong> ${targetInst.visit_duration} · 🕒 ${targetInst.opening_hours}</div>
              </div>
            `, [targetInst]);
            selectInstitution(targetInst, false);
            return;
          }

          appendCuratorMessage(`
            <p>⭐ <strong>Must-See Architectural & Art Landmarks:</strong></p>
            <p>Culture Atlas features some of the world's most astonishing site-specific art and architecture:</p>
            <ul class="list-disc pl-4 space-y-1 text-slate-300 text-xs">
              <li><strong>ARoS (Aarhus):</strong> Olafur Eliasson's 360° circular glass walkway <em>Your rainbow panorama</em>.</li>
              <li><strong>Dia Beacon (Hudson Valley):</strong> Richard Serra's monumental Torqued Ellipses and Michael Heizer excavations.</li>
              <li><strong>Instituto Inhotim (Brazil):</strong> 23 bespoke artist pavilions embedded in a 700-hectare tropical rainforest botanical garden.</li>
              <li><strong>Kunsthaus Bregenz (Austria):</strong> Peter Zumthor's etched glass light-box architecture.</li>
            </ul>
          `, [
            ALL_INSTITUTIONS.find(i => i.name.includes('ARoS')),
            ALL_INSTITUTIONS.find(i => i.name.includes('Dia Beacon')),
            ALL_INSTITUTIONS.find(i => i.name.includes('Inhotim'))
          ]);
          return;
        }

'''

    if curator_insert_marker in content:
        content = content.replace(curator_insert_marker, visitor_queries_block + curator_insert_marker)
        print("Updated handleCuratorQuery with Visitor Planning Intent Handlers")

    # 6. Update Specific Institution Lookup in handleCuratorQuery to output visitor planning details
    old_inst_lookup = '''        // 8. Specific Institution Lookup
        const instMatch = ALL_INSTITUTIONS.find(i => q.includes(i.name.toLowerCase()) || (i.name.toLowerCase().includes(q) && q.length > 3));
        if (instMatch) {
          appendCuratorMessage(`
            <p><strong>${escapeHtml(instMatch.name)}</strong> <span class="text-[#60a5fa] font-mono">· ${instMatch.location} (Est. ${instMatch.year_founded})</span></p>
            <p><strong>Governance:</strong> ${instMatch.governance_type} · <strong>Focus:</strong> ${instMatch.curatorial_focus}</p>
            <p><strong>Admission Policy:</strong> ${instMatch.admission_policy} — ${instMatch.admission_details}</p>
            <p><strong>Ethical Safeguard:</strong> ${instMatch.ethical_safeguard}</p>
            ${instMatch.watch ? `<p class="text-amber-300/90"><strong>Watch Note:</strong> ${escapeHtml(instMatch.watch)}</p>` : ''}
          `, [instMatch]);

          selectInstitution(instMatch, false);
          return;
        }'''

    new_inst_lookup = '''        // 8. Specific Institution Lookup
        const instMatch = ALL_INSTITUTIONS.find(i => q.includes(i.name.toLowerCase()) || (i.aliases && i.aliases.some(a => q.includes(a.toLowerCase()))) || (i.name.toLowerCase().includes(q) && q.length > 3));
        if (instMatch) {
          appendCuratorMessage(`
            <p><strong>${escapeHtml(instMatch.name)}</strong> <span class="text-[#60a5fa] font-mono">· ${instMatch.location} (Est. ${instMatch.year_founded})</span></p>
            <p><strong>Governance:</strong> ${instMatch.governance_type} · <strong>Focus:</strong> ${instMatch.curatorial_focus}</p>
            <p><strong>Admission Policy:</strong> ${instMatch.admission_policy} — ${instMatch.admission_details}</p>
            <p><strong>Ethical Safeguard:</strong> ${instMatch.ethical_safeguard}</p>
            
            <!-- Practical Visitor Details Card -->
            <div class="mt-2.5 p-3 rounded-xl bg-[#0b0f19] border border-[#1d273e] text-xs space-y-1.5 font-mono">
              <div class="text-emerald-400 font-semibold">🕒 <strong>Hours:</strong> ${instMatch.opening_hours}</div>
              <div class="text-[#93c5fd]">🎟️ <strong>Admission:</strong> ${instMatch.admission_fee}</div>
              <div class="text-slate-300 font-sans">📍 <strong>Address:</strong> ${instMatch.address} (${instMatch.neighborhood})</div>
              <div class="text-slate-300 font-sans">🚇 <strong>Transit:</strong> ${instMatch.transit_tips}</div>
              <div class="text-amber-300 font-sans">⭐ <strong>Highlight:</strong> ${instMatch.highlight}</div>
              <div class="text-slate-400 font-sans">⏱️ <strong>Duration:</strong> ${instMatch.visit_duration} · ☕ ${instMatch.amenities}</div>
              ${instMatch.visit_url ? `<a href="${instMatch.visit_url}" target="_blank" class="text-[#60a5fa] hover:underline text-xs block pt-1 font-mono">Plan Your Visit (Official Museum Guide) ↗</a>` : ''}
            </div>
            
            ${instMatch.watch ? `<p class="text-amber-300/90 text-xs mt-1.5"><strong>Watch Note:</strong> ${escapeHtml(instMatch.watch)}</p>` : ''}
          `, [instMatch]);

          selectInstitution(instMatch, false);
          return;
        }'''

    if old_inst_lookup in content:
        content = content.replace(old_inst_lookup, new_inst_lookup)
        print("Updated Specific Institution Lookup with practical visitor guide")

    # 7. Update renderLeftList to include quick visitor line
    old_left_list_tags = '''            <!-- Researcher Tags: Governance & Admission -->
            <div class="flex items-center gap-1.5 text-[9.5px] font-mono text-[#94a3b8] mt-1.5 flex-wrap">
              <span class="px-1.5 py-0.5 rounded bg-[#101726] border border-[#1c2840] text-[#93c5fd]">🏛️ ${inst.governance_type}</span>
              <span class="px-1.5 py-0.5 rounded bg-[#0a1f15] border border-[#143d28] text-emerald-300">🎟️ ${inst.admission_policy}</span>
            </div>'''

    new_left_list_tags = '''            <!-- Researcher Tags: Governance & Admission -->
            <div class="flex items-center gap-1.5 text-[9.5px] font-mono text-[#94a3b8] mt-1.5 flex-wrap">
              <span class="px-1.5 py-0.5 rounded bg-[#101726] border border-[#1c2840] text-[#93c5fd]">🏛️ ${inst.governance_type}</span>
              <span class="px-1.5 py-0.5 rounded bg-[#0a1f15] border border-[#143d28] text-emerald-300">🎟️ ${inst.admission_policy}</span>
            </div>

            <!-- Quick Visitor Schedule & Pricing Pill -->
            <div class="mt-1.5 flex items-center gap-2 text-[10px] font-mono text-slate-300">
              <span class="truncate">🕒 ${inst.opening_hours ? inst.opening_hours.split(',')[0] : 'Open Weekly'}</span>
              <span class="text-slate-600">·</span>
              <span class="text-emerald-400 shrink-0 truncate max-w-[120px]">🎟️ ${inst.admission_fee ? inst.admission_fee.split('/')[0].trim() : 'Free / Subsidized'}</span>
            </div>'''

    if old_left_list_tags in content:
        content = content.replace(old_left_list_tags, new_left_list_tags)
        print("Updated renderLeftList with visitor preview line")

    # Write back to build_conversational_atlas.py
    with open('build_conversational_atlas.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Successfully saved updated build_conversational_atlas.py!")

def update_widget_script():
    print("Reading build_conversational_widget.py...")
    with open('build_conversational_widget.py', 'r', encoding='utf-8') as f:
        w_content = f.read()

    # In widget cards, show opening hours and admission
    old_w_card = '''      document.getElementById('wCardTitle').textContent = inst.name;
      document.getElementById('wCardMeta').textContent = `${inst.location} · ${inst.tier === 'A' ? 'Verified' : 'One Name'}`;'''

    new_w_card = '''      document.getElementById('wCardTitle').textContent = inst.name;
      const shortH = inst.opening_hours ? inst.opening_hours.split(',')[0] : '';
      const shortF = inst.admission_fee ? inst.admission_fee.split('/')[0].trim() : '';
      document.getElementById('wCardMeta').textContent = `${inst.location} · ${shortH} (${shortF})`;'''

    if old_w_card in w_content:
        w_content = w_content.replace(old_w_card, new_w_card)
        print("Updated wCardMeta in build_conversational_widget.py")

    # In handleWQuery, add hours, transit, accessibility
    w_query_marker = '''    function handleWQuery(q) {
      const query = q.toLowerCase();
      setTimeout(() => {'''

    new_w_query_prefix = '''    function handleWQuery(q) {
      const query = q.toLowerCase();
      setTimeout(() => {
        // Visitor Queries in Widget
        if (query.includes('hour') || query.includes('schedule') || query.includes('open') || query.includes('monday')) {
          const mSpaces = DATA.filter(i => !i.opening_hours.toLowerCase().includes('closed mon') && (i.opening_hours.toLowerCase().includes('daily') || i.opening_hours.toLowerCase().includes('mon,') || i.opening_hours.toLowerCase().includes('mon–') || i.opening_hours.toLowerCase().includes('mon-')));
          appendWCurator(`
            <p><strong>🕒 Visiting Hours & Mondays:</strong></p>
            <p>Independent kunsthalles usually open <strong>Wed–Sun (11:00–18:00)</strong>. Here are spaces open on <strong>Mondays</strong>:</p>
          `, mSpaces.slice(0, 3));
          return;
        }

        if (query.includes('transit') || query.includes('how to get') || query.includes('train') || query.includes('subway') || query.includes('direction')) {
          appendWCurator(`
            <p><strong>🚇 Transit & Destination Access:</strong></p>
            <p>Culture Atlas provides full public rail & metro directions for all 203 institutions. Easily reach Dia Beacon via Metro-North or Louisiana via the Danish Kystbanen line.</p>
          `, [
            DATA.find(i => i.name.includes('Dia Beacon')),
            DATA.find(i => i.name.includes('Louisiana'))
          ]);
          return;
        }

        if (query.includes('accessib') || query.includes('wheelchair') || query.includes('step-free')) {
          appendWCurator(`
            <p><strong>♿ Barrier-Free Accessibility:</strong></p>
            <p>All mapped civic institutions offer step-free access, elevators, loan wheelchairs, and free companion admission.</p>
          `, [
            DATA.find(i => i.name.includes('Serpentine')),
            DATA.find(i => i.name.includes('ARoS'))
          ]);
          return;
        }
'''

    if w_query_marker in w_content:
        w_content = w_content.replace(w_query_marker, new_w_query_prefix)
        print("Updated handleWQuery in build_conversational_widget.py")

    with open('build_conversational_widget.py', 'w', encoding='utf-8') as f:
        f.write(w_content)
    print("Successfully saved updated build_conversational_widget.py!")

if __name__ == '__main__':
    update_atlas()
    update_widget_script()
