#!/usr/bin/env python3
"""
patch_widget_simple_language.py
Updates build_conversational_widget.py to use proper simple language.
"""

def patch():
    path = "/Users/polinavasilyeva/.gemini/antigravity/scratch/sponsor-atlas/build_conversational_widget.py"
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Update Welcome Message
    old_welcome = """    function initWConversation() {{
      wMessages.innerHTML = '';
      appendWCurator(`
        <p class="text-[#ececec]">
          Welcome to <strong>Culture Atlas</strong>. We map 203 verified ethical cultural sanctuaries across 35 countries—institutions that operate with transparent public funding and clean underwriting without fossil-fuel or defense sponsorship.
        </p>
        <p class="text-[#d4d4d4]">
          For example, explore <a href="#" class="w-inst-link" data-name="Chisenhale Gallery">Chisenhale Gallery</a> in London (free admission), <a href="#" class="w-inst-link" data-name="CAPC musée d'art contemporain de Bordeaux">CAPC</a> in Bordeaux, or <a href="#" class="w-inst-link" data-name="Dia Beacon">Dia Beacon</a> in New York.
        </p>
        <p class="text-[#93c5fd]">
          Which city or type of art experience would you like to discover today?
        </p>
      `);
    }}"""

    new_welcome = """    function initWConversation() {{
      wMessages.innerHTML = '';
      appendWCurator(`
        <p class="text-[#ececec]">
          Welcome to <strong>Culture Atlas</strong>. We map <strong>203 museums and art spaces across 35 countries</strong> that do not take money from oil companies, weapons makers, or private prisons.
        </p>
        <p class="text-[#d4d4d4]">
          For example, check out <a href="#" class="w-inst-link" data-name="Chisenhale Gallery">Chisenhale Gallery</a> in London (free admission), <a href="#" class="w-inst-link" data-name="CAPC musée d'art contemporain de Bordeaux">CAPC</a> in Bordeaux, or <a href="#" class="w-inst-link" data-name="Dia Beacon">Dia Beacon</a> in New York.
        </p>
        <p class="text-[#93c5fd]">
          Where would you like to go, or what kind of art are you looking for?
        </p>
      `);
    }}"""

    if old_welcome in content:
        content = content.replace(old_welcome, new_welcome)
        print("Updated initWConversation to simple language!")
    else:
        print("WARNING: Could not find old_welcome in widget!")

    # 2. Update handleWQuery
    old_query_block = """    function handleWQuery(q) {{
      const query = q.toLowerCase();
      setTimeout(() => {{
        // Visitor Queries: Hours & Mondays
        if (query.includes('hour') || query.includes('schedule') || query.includes('open') || query.includes('monday') || query.includes('weekend')) {{
          const targetInst = DATA.find(i => query.includes(i.name.toLowerCase()));
          if (targetInst) {{
            appendWCurator(`
              <p class="text-slate-200">
                ${{formatWInstLink(targetInst)}} welcomes visitors <strong>${{targetInst.opening_hours}}</strong>.
              </p>
              <p class="text-slate-300">
                Admission is ${{targetInst.admission_fee}}. Located at ${{targetInst.address}}, easily reached via ${{targetInst.transit_tips}}.
              </p>
            `);
            select(targetInst, true);
            return;
          }}

          const mSpaces = DATA.filter(i => !i.opening_hours.toLowerCase().includes('closed mon') && (i.opening_hours.toLowerCase().includes('daily') || i.opening_hours.toLowerCase().includes('mon,') || i.opening_hours.toLowerCase().includes('mon–') || i.opening_hours.toLowerCase().includes('mon-')));
          const m1 = mSpaces[0] || DATA[0];
          const m2 = mSpaces[1] || DATA[1];
          appendWCurator(`
            <p class="text-slate-200">
              While many traditional museums close Mondays, we map <strong>${{mSpaces.length}}</strong> spaces welcoming visitors at the start of the week.
            </p>
            <p class="text-slate-300">
              For quiet Monday contemplation, consider ${{formatWInstLink(m1)}} or ${{formatWInstLink(m2)}}.
            </p>
          `);
          return;
        }}

        // Visitor Queries: Transit & Directions
        if (query.includes('transit') || query.includes('how to get') || query.includes('train') || query.includes('subway') || query.includes('direction')) {{
          const targetInst = DATA.find(i => query.includes(i.name.toLowerCase()));
          if (targetInst) {{
            appendWCurator(`
              <p class="text-slate-200">
                To reach ${{formatWInstLink(targetInst)}}, take ${{targetInst.transit_tips}}.
              </p>
              <p class="text-slate-300">
                Located at ${{targetInst.address}} (${{targetInst.neighborhood}}). Suggested duration: ${{targetInst.visit_duration}}.
              </p>
            `);
            select(targetInst, true);
            return;
          }}

          const dia = DATA.find(i => i.name.includes('Dia Beacon'));
          const louis = DATA.find(i => i.name.includes('Louisiana'));
          appendWCurator(`
            <p class="text-slate-200">
              Culture Atlas provides public transit directions for all 203 institutions.
            </p>
            <p class="text-slate-300">
              You can easily reach ${{formatWInstLink(dia)}} via Metro-North rail from Manhattan, or take Denmark's coastal train up to ${{formatWInstLink(louis)}}.
            </p>
          `);
          return;
        }}

        // Visitor Queries: Accessibility
        if (query.includes('accessib') || query.includes('wheelchair') || query.includes('step-free')) {{
          const serp = DATA.find(i => i.name.includes('Serpentine'));
          const aros = DATA.find(i => i.name.includes('ARoS'));
          appendWCurator(`
            <p class="text-slate-200">
              All mapped civic institutions offer step-free access, elevators, loan wheelchairs, and free entry for essential companions.
            </p>
            <p class="text-slate-300">
              Exemplary accessible venues include ${{formatWInstLink(serp)}} and ${{formatWInstLink(aros)}}.
            </p>
          `);
          return;
        }}

        if (query.includes('what makes') || query.includes('ethical') || query.includes('criteria') || query.includes('method')) {{
          const chis = DATA.find(i => i.name.includes('Chisenhale'));
          const capc = DATA.find(i => i.name.includes('CAPC'));
          appendWCurator(`
            <p class="text-slate-200">
              We evaluate whether museums protect curatorial independence by looking at their funding architecture:
            </p>
            <p class="text-slate-300">
              Prioritizing civic municipal sanctuaries backed by public councils like ${{formatWInstLink(capc)}}, artist-governed kunsthalles like ${{formatWInstLink(chis)}}, and spaces that divested from fossil-fuel extraction.
            </p>
          `);
        }} else if (query.includes('fossil') || query.includes('oil') || query.includes('bp') || query.includes('defense')) {{
          const cam = DATA.find(i => i.name.includes('Camden'));
          const white = DATA.find(i => i.name.includes('Whitechapel'));
          appendWCurator(`
            <p class="text-slate-200">
              Every museum in Culture Atlas has verified clean underwriting without oil or weapons money on its roster.
            </p>
            <p class="text-slate-300">
              Standout divested leaders include ${{formatWInstLink(cam)}} and ${{formatWInstLink(white)}}.
            </p>
          `);
        }} else if (query.includes('moma') || query.includes('whitney') || query.includes('why exclude')) {{
          const dia = DATA.find(i => i.name.includes('Dia Beacon'));
          const sculp = DATA.find(i => i.name.includes('SculptureCenter'));
          appendWCurator(`
            <p class="text-slate-200">
              MoMA trustees held major stakes in defense contractors and private prisons. Culture Atlas only maps spaces free from unresolved sponsorship conflicts.
            </p>
            <p class="text-slate-300">
              Instead, we celebrate uncompromised sanctuaries like ${{formatWInstLink(dia)}} and ${{formatWInstLink(sculp)}}.
            </p>
          `);
          // City or general matches
          const matchCity = PRIORITY_CITIES.find(c => query.includes(c.name.toLowerCase())) || DATA.find(i => query.includes(i.city.toLowerCase()));
          if (matchCity) {{
            const cityName = matchCity.name || matchCity.city;
            const cObj = PRIORITY_CITIES.find(c => c.name.toLowerCase() === cityName.toLowerCase()) || matchCity;
            const list = DATA.filter(i => i.city.toLowerCase() === cityName.toLowerCase());
            const topSp = list.slice(0, 3).map(i => formatWInstLink(i, {{noCity: true}})).join(', ');
            appendWCurator(`
              <p class="text-slate-200">
                Found <strong>${{list.length}}</strong> verified ethical spaces in <a href="#" class="w-city-link font-semibold text-white hover:text-[#60a5fa] underline cursor-pointer" data-city="${{escapeHtml(cityName)}}">${{escapeHtml(cityName)}}</a>.
              </p>
              <p class="text-slate-300">
                Notable venues include ${{topSp}}.
              </p>
            `);
            targetRadius = baseRadius * 3.8;
            flyTo(cObj.lon, cObj.lat);
          }} else {{
            const rand = DATA.filter(i => i.tier === 'A');
            const p1 = rand[Math.floor(Math.random()*rand.length)];
            const p2 = rand[Math.floor(Math.random()*rand.length)];
            appendWCurator(`
              <p class="text-slate-200">
                Here are two recommended verified spaces to discover: ${{formatWInstLink(p1)}} and ${{formatWInstLink(p2)}}.
              </p>
            `);
          }}
        }}
      }}, 250);
    }}"""

    new_query_block = """    function handleWQuery(q) {{
      const query = q.toLowerCase();
      setTimeout(() => {{
        // Visitor Queries: Hours & Mondays
        if (query.includes('hour') || query.includes('schedule') || query.includes('open') || query.includes('monday') || query.includes('weekend')) {{
          const targetInst = DATA.find(i => query.includes(i.name.toLowerCase()));
          if (targetInst) {{
            appendWCurator(`
              <p class="text-slate-200">
                <strong>${{formatWInstLink(targetInst)}}</strong> is open <strong>${{targetInst.opening_hours}}</strong>.
              </p>
              <p class="text-slate-300">
                Address: ${{targetInst.address}}. Transit: ${{targetInst.transit_tips}}.
              </p>
            `);
            select(targetInst, true);
            return;
          }}

          const mSpaces = DATA.filter(i => !i.opening_hours.toLowerCase().includes('closed mon') && (i.opening_hours.toLowerCase().includes('daily') || i.opening_hours.toLowerCase().includes('mon,') || i.opening_hours.toLowerCase().includes('mon–') || i.opening_hours.toLowerCase().includes('mon-')));
          const m1 = mSpaces[0] || DATA[0];
          const m2 = mSpaces[1] || DATA[1];
          appendWCurator(`
            <p class="text-slate-200">
              Most museums are closed on Mondays, but Culture Atlas has <strong>${{mSpaces.length}}</strong> spaces open on Mondays:
            </p>
            <p class="text-slate-300">
              Check out ${{formatWInstLink(m1)}} or ${{formatWInstLink(m2)}}.
            </p>
          `);
          return;
        }}

        // Visitor Queries: Transit & Directions
        if (query.includes('transit') || query.includes('how to get') || query.includes('train') || query.includes('subway') || query.includes('direction')) {{
          const targetInst = DATA.find(i => query.includes(i.name.toLowerCase()));
          if (targetInst) {{
            appendWCurator(`
              <p class="text-slate-200">
                To reach <strong>${{formatWInstLink(targetInst)}}</strong>, take ${{targetInst.transit_tips}}.
              </p>
              <p class="text-slate-300">
                Address: ${{targetInst.address}} (${{targetInst.neighborhood}}). Suggested duration: ${{targetInst.visit_duration}}.
              </p>
            `);
            select(targetInst, true);
            return;
          }}

          const dia = DATA.find(i => i.name.includes('Dia Beacon'));
          const louis = DATA.find(i => i.name.includes('Louisiana'));
          appendWCurator(`
            <p class="text-slate-200">
              Every museum in Culture Atlas includes simple transit directions:
            </p>
            <p class="text-slate-300">
              Take the Metro-North train from Grand Central right to ${{formatWInstLink(dia)}}, or take the coastal train from Copenhagen to ${{formatWInstLink(louis)}}.
            </p>
          `);
          return;
        }}

        // Visitor Queries: Accessibility
        if (query.includes('accessib') || query.includes('wheelchair') || query.includes('step-free')) {{
          const serp = DATA.find(i => i.name.includes('Serpentine'));
          const aros = DATA.find(i => i.name.includes('ARoS'));
          appendWCurator(`
            <p class="text-slate-200">
              All mapped spaces have step-free access, elevators, wheelchairs to borrow, and free admission for companions.
            </p>
            <p class="text-slate-300">
              Great accessible venues include ${{formatWInstLink(serp)}} in London and ${{formatWInstLink(aros)}} in Denmark.
            </p>
          `);
          return;
        }}

        // Free admission
        if (query.includes('free') || query.includes('admission') || query.includes('ticket')) {{
          const freeSpaces = DATA.filter(i => (i.admission_policy || '').includes('Free'));
          const f1 = freeSpaces[0] || DATA[0];
          const f2 = freeSpaces[1] || DATA[1];
          appendWCurator(`
            <p class="text-slate-200">
              We map <strong>${{freeSpaces.length}}</strong> spaces with completely free admission.
            </p>
            <p class="text-slate-300">
              Top free places include ${{formatWInstLink(f1)}} and ${{formatWInstLink(f2)}}.
            </p>
          `);
          return;
        }}

        if (query.includes('what makes') || query.includes('ethical') || query.includes('criteria') || query.includes('method')) {{
          const chis = DATA.find(i => i.name.includes('Chisenhale'));
          const capc = DATA.find(i => i.name.includes('CAPC'));
          appendWCurator(`
            <p class="text-slate-200">
              We rate museums based on clean funding:
            </p>
            <p class="text-slate-300">
              We prioritize public museums backed by arts councils like ${{formatWInstLink(capc)}}, artist-run spaces like ${{formatWInstLink(chis)}}, and spaces that don't take oil or weapons money.
            </p>
          `);
          return;
        }}

        if (query.includes('fossil') || query.includes('oil') || query.includes('bp') || query.includes('defense')) {{
          const cam = DATA.find(i => i.name.includes('Camden'));
          const white = DATA.find(i => i.name.includes('Whitechapel'));
          appendWCurator(`
            <p class="text-slate-200">
              Every museum in Culture Atlas has verified clean funding without oil or weapons sponsorships.
            </p>
            <p class="text-slate-300">
              Examples include ${{formatWInstLink(cam)}} and ${{formatWInstLink(white)}}.
            </p>
          `);
          return;
        }}

        if (query.includes('moma') || query.includes('whitney') || query.includes('why exclude')) {{
          const dia = DATA.find(i => i.name.includes('Dia Beacon'));
          const sculp = DATA.find(i => i.name.includes('SculptureCenter'));
          appendWCurator(`
            <p class="text-slate-200">
              MoMA trustees had ties to weapons companies and private prisons. Culture Atlas only maps spaces free from controversial sponsorships.
            </p>
            <p class="text-slate-300">
              Instead, we feature spaces like ${{formatWInstLink(dia)}} and ${{formatWInstLink(sculp)}}.
            </p>
          `);
          return;
        }}

        // City or general matches
        const matchCity = PRIORITY_CITIES.find(c => query.includes(c.name.toLowerCase())) || DATA.find(i => query.includes(i.city.toLowerCase()));
        if (matchCity) {{
          const cityName = matchCity.name || matchCity.city;
          const cObj = PRIORITY_CITIES.find(c => c.name.toLowerCase() === cityName.toLowerCase()) || matchCity;
          const list = DATA.filter(i => i.city.toLowerCase() === cityName.toLowerCase());
          const topSp = list.slice(0, 3).map(i => formatWInstLink(i, {{noCity: true}})).join(', ');
          appendWCurator(`
            <p class="text-slate-200">
              Found <strong>${{list.length}}</strong> spaces in <a href="#" class="w-city-link font-semibold text-white hover:text-[#60a5fa] underline cursor-pointer" data-city="${{escapeHtml(cityName)}}">${{escapeHtml(cityName)}}</a> with clean funding:
            </p>
            <p class="text-slate-300">
              Highlights include ${{topSp}}.
            </p>
          `);
          targetRadius = baseRadius * 3.8;
          flyTo(cObj.lon, cObj.lat);
          return;
        }}

        const rand = DATA.filter(i => i.tier === 'A');
        const p1 = rand[Math.floor(Math.random()*rand.length)];
        const p2 = rand[Math.floor(Math.random()*rand.length)];
        appendWCurator(`
          <p class="text-slate-200">
            Here are two great art spaces to check out: ${{formatWInstLink(p1)}} and ${{formatWInstLink(p2)}}.
          </p>
        `);
      }}, 250);
    }}"""

    if old_query_block in content:
        content = content.replace(old_query_block, new_query_block)
        print("Updated handleWQuery in widget!")
    else:
        print("WARNING: Could not find old_query_block in widget!")

    # 3. Canvas city click
    content = content.replace(
        "with <strong>${{cityList.length}}</strong> verified ethical cultural sanctuaries.\n              </p>\n              <p class=\"text-slate-300\">\n                Standout spaces include ${{topList}}.",
        "with <strong>${{cityList.length}}</strong> spaces with clean funding: ${{topList}}."
    )

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("Successfully patched build_conversational_widget.py!")

if __name__ == "__main__":
    patch()
