#!/usr/bin/env python3
"""
patch_widget_proper.py
Updates build_conversational_widget.py with visitor planning intelligence and card info.
"""

with open('build_conversational_widget.py', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Update wCardMeta in select()
old_w_card = '''      document.getElementById('wCardTitle').textContent = inst.name;
      document.getElementById('wCardMeta').textContent = `${{inst.location}} · ${{inst.tier === 'A' ? 'Verified' : 'One Name'}}`;'''

new_w_card = '''      document.getElementById('wCardTitle').textContent = inst.name;
      const shortH = inst.opening_hours ? inst.opening_hours.split(',')[0] : '';
      const shortF = inst.admission_fee ? inst.admission_fee.split('/')[0].trim() : '';
      document.getElementById('wCardMeta').textContent = `${{inst.location}} · ${{shortH}} (${{shortF}})`;'''

if old_w_card in text:
    text = text.replace(old_w_card, new_w_card)
    print("Updated wCardMeta in select()")
else:
    print("Could not find old_w_card")

# 2. Add Visitor Queries to handleWQuery
old_w_query = '''    function handleWQuery(q) {{
      const query = q.toLowerCase();
      setTimeout(() => {{
        if (query.includes('what makes') || query.includes('ethical') || query.includes('criteria') || query.includes('method')) {{'''

new_w_query = '''    function handleWQuery(q) {{
      const query = q.toLowerCase();
      setTimeout(() => {{
        // Visitor Queries: Hours & Mondays
        if (query.includes('hour') || query.includes('schedule') || query.includes('open') || query.includes('monday') || query.includes('weekend')) {{
          const targetInst = DATA.find(i => query.includes(i.name.toLowerCase()));
          if (targetInst) {{
            appendWCurator(`
              <p>🕒 <strong>Hours for ${{targetInst.name}}:</strong></p>
              <p class="text-emerald-400 font-mono text-[10.5px]">📅 ${{targetInst.opening_hours}}</p>
              <p class="text-slate-300 text-[10px]">🎟️ ${{targetInst.admission_fee}}</p>
              <p class="text-slate-300 text-[10px]">📍 ${{targetInst.address}}</p>
              <p class="text-[#93c5fd] text-[10px] font-mono">🚇 ${{targetInst.transit_tips}}</p>
            `, [targetInst]);
            select(targetInst, true);
            return;
          }}

          const mSpaces = DATA.filter(i => !i.opening_hours.toLowerCase().includes('closed mon') && (i.opening_hours.toLowerCase().includes('daily') || i.opening_hours.toLowerCase().includes('mon,') || i.opening_hours.toLowerCase().includes('mon–') || i.opening_hours.toLowerCase().includes('mon-')));
          appendWCurator(`
            <p><strong>🕒 Visiting Hours & Mondays:</strong></p>
            <p>Independent spaces generally open <strong>Wed–Sun (11:00–18:00)</strong>. Here are ethical venues open on <strong>Mondays</strong>:</p>
          `, mSpaces.slice(0, 3));
          return;
        }}

        // Visitor Queries: Transit & Directions
        if (query.includes('transit') || query.includes('how to get') || query.includes('train') || query.includes('subway') || query.includes('direction')) {{
          const targetInst = DATA.find(i => query.includes(i.name.toLowerCase()));
          if (targetInst) {{
            appendWCurator(`
              <p>🚇 <strong>Transit Directions to ${{targetInst.name}}:</strong></p>
              <p class="text-[#93c5fd] font-mono text-[10.5px]">${{targetInst.transit_tips}}</p>
              <p class="text-slate-300 text-[10px]">📍 ${{targetInst.address}} (${{targetInst.neighborhood}})</p>
              <p class="text-slate-400 text-[10px]">⏱️ Suggested Duration: ${{targetInst.visit_duration}}</p>
            `, [targetInst]);
            select(targetInst, true);
            return;
          }}

          appendWCurator(`
            <p><strong>🚇 Transit & Destination Access:</strong></p>
            <p>Culture Atlas provides full public rail & metro directions for all 203 institutions. Easily reach Dia Beacon via Metro-North or Louisiana via the Danish Kystbanen line.</p>
          `, [
            DATA.find(i => i.name.includes('Dia Beacon')),
            DATA.find(i => i.name.includes('Louisiana'))
          ]);
          return;
        }}

        // Visitor Queries: Accessibility
        if (query.includes('accessib') || query.includes('wheelchair') || query.includes('step-free')) {{
          appendWCurator(`
            <p><strong>♿ Barrier-Free Accessibility:</strong></p>
            <p>All mapped civic institutions offer step-free access, elevators, loan wheelchairs, and free companion admission.</p>
          `, [
            DATA.find(i => i.name.includes('Serpentine')),
            DATA.find(i => i.name.includes('ARoS'))
          ]);
          return;
        }}

        if (query.includes('what makes') || query.includes('ethical') || query.includes('criteria') || query.includes('method')) {{'''

if old_w_query in text:
    text = text.replace(old_w_query, new_w_query)
    print("Updated handleWQuery in build_conversational_widget.py")
else:
    print("Could not find old_w_query")

with open('build_conversational_widget.py', 'w', encoding='utf-8') as f:
    f.write(text)

print("Saved build_conversational_widget.py!")
