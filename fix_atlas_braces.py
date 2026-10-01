#!/usr/bin/env python3
"""
fix_atlas_braces.py
Doubles all curly braces in the visitor queries snippet in build_conversational_atlas.py
so that Python's f-string parsing succeeds cleanly.
"""

with open('build_conversational_atlas.py', 'r', encoding='utf-8') as f:
    text = f.read()

start_marker = '// A. Visitor Data: Hours & Monday Openings'
end_marker = '// 1. Methodology & Philosophy & "What type of institutions should I go to?"'

start_idx = text.find(start_marker)
end_idx = text.find(end_marker)

if start_idx != -1 and end_idx != -1:
    snippet = text[start_idx:end_idx]
    # In snippet, double all { and }
    # First normalize: if any {{ or }}, convert to single first, then double all
    snippet_fixed = snippet.replace('{{', '{').replace('}}', '}')
    snippet_fixed = snippet_fixed.replace('{', '{{').replace('}', '}}')
    
    text = text[:start_idx] + snippet_fixed + text[end_idx:]
    print("Fixed curly braces in visitor queries snippet!")

# Also enhance Specific Institution Lookup with doubled braces
old_lookup = '''        // 8. Specific Institution Lookup
        const instMatch = ALL_INSTITUTIONS.find(i => q.includes(i.name.toLowerCase()) || (i.name.toLowerCase().includes(q) && q.length > 3));
        if (instMatch) {{
          appendCuratorMessage(`
            <p><strong>${{escapeHtml(instMatch.name)}}</strong> <span class="text-[#60a5fa] font-mono">· ${{instMatch.location}} (Est. ${{instMatch.year_founded}})</span></p>
            <p><strong>Governance:</strong> ${{instMatch.governance_type}} · <strong>Focus:</strong> ${{instMatch.curatorial_focus}}</p>
            <p><strong>Admission Policy:</strong> ${{instMatch.admission_policy}} — ${{instMatch.admission_details}}</p>
            <p><strong>Ethical Safeguard:</strong> ${{instMatch.ethical_safeguard}}</p>
            ${{instMatch.watch ? `<p class="text-amber-300/90"><strong>Watch Note:</strong> ${{escapeHtml(instMatch.watch)}}</p>` : ''}}
          `, [instMatch]);

          selectInstitution(instMatch, false);
          return;
        }}'''

new_lookup = '''        // 8. Specific Institution Lookup
        const instMatch = ALL_INSTITUTIONS.find(i => q.includes(i.name.toLowerCase()) || (i.aliases && i.aliases.some(a => q.includes(a.toLowerCase()))) || (i.name.toLowerCase().includes(q) && q.length > 3));
        if (instMatch) {{
          appendCuratorMessage(`
            <p><strong>${{escapeHtml(instMatch.name)}}</strong> <span class="text-[#60a5fa] font-mono">· ${{instMatch.location}} (Est. ${{instMatch.year_founded}})</span></p>
            <p><strong>Governance:</strong> ${{instMatch.governance_type}} · <strong>Focus:</strong> ${{instMatch.curatorial_focus}}</p>
            <p><strong>Admission Policy:</strong> ${{instMatch.admission_policy}} — ${{instMatch.admission_details}}</p>
            <p><strong>Ethical Safeguard:</strong> ${{instMatch.ethical_safeguard}}</p>
            
            <!-- Practical Visitor Details Card -->
            <div class="mt-2.5 p-3 rounded-xl bg-[#0b0f19] border border-[#1d273e] text-xs space-y-1.5 font-mono">
              <div class="text-emerald-400 font-semibold">🕒 <strong>Hours:</strong> ${{instMatch.opening_hours}}</div>
              <div class="text-[#93c5fd]">🎟️ <strong>Admission:</strong> ${{instMatch.admission_fee}}</div>
              <div class="text-slate-300 font-sans">📍 <strong>Address:</strong> ${{instMatch.address}} (${{instMatch.neighborhood}})</div>
              <div class="text-slate-300 font-sans">🚇 <strong>Transit:</strong> ${{instMatch.transit_tips}}</div>
              <div class="text-amber-300 font-sans">⭐ <strong>Highlight:</strong> ${{instMatch.highlight}}</div>
              <div class="text-slate-400 font-sans">⏱️ <strong>Duration:</strong> ${{instMatch.visit_duration}} · ☕ ${{instMatch.amenities}}</div>
              ${{instMatch.visit_url ? `<a href="${{instMatch.visit_url}}" target="_blank" class="text-[#60a5fa] hover:underline text-xs block pt-1 font-mono">Plan Your Visit (Official Museum Guide) ↗</a>` : ''}}
            </div>
            
            ${{instMatch.watch ? `<p class="text-amber-300/90 text-xs mt-1.5"><strong>Watch Note:</strong> ${{escapeHtml(instMatch.watch)}}</p>` : ''}}
          `, [instMatch]);

          selectInstitution(instMatch, false);
          return;
        }}'''

if old_lookup in text:
    text = text.replace(old_lookup, new_lookup)
    print("Replaced old_lookup with enriched visitor guide!")
else:
    print("Could not find old_lookup")

with open('build_conversational_atlas.py', 'w', encoding='utf-8') as f:
    f.write(text)

print("Saved build_conversational_atlas.py with fixed braces!")
