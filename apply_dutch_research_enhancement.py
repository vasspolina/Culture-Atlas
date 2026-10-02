import re
import sys

def patch():
    with open('build_conversational_atlas.py', 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Update workPlusMenu
    old_menu = """          <!-- Quick Dropdown Menu for Plus button -->
          <div id="workPlusMenu" class="hidden absolute left-4 bottom-14 z-30 bg-[#262626] border border-[#383838] rounded-2xl p-1.5 shadow-2xl flex flex-col gap-1 w-52 text-[14px]">
            <button class="work-menu-item text-left px-3 py-1.5 hover:bg-[#333] rounded-xl text-slate-200 transition cursor-pointer" data-query="Which museums and galleries are free to enter?">🎟️ Free Admission Spaces</button>
            <button class="work-menu-item text-left px-3 py-1.5 hover:bg-[#333] rounded-xl text-slate-200 transition cursor-pointer" data-query="Which museums are open on Mondays?">🕒 Monday Openings</button>
            <button class="work-menu-item text-left px-3 py-1.5 hover:bg-[#333] rounded-xl text-slate-200 transition cursor-pointer" data-query="Show spaces that do not take oil or weapons money">🌿 Fossil & Defense-Free</button>
            <button class="work-menu-item text-left px-3 py-1.5 hover:bg-[#333] rounded-xl text-slate-200 transition cursor-pointer" data-query="Tell me about London's independent art spaces">📍 London Art Guide</button>
            <button class="work-menu-item text-left px-3 py-1.5 hover:bg-[#333] rounded-xl text-slate-200 transition cursor-pointer" data-query="Tell me about New York's art spaces and board controversies">📍 New York Art Guide</button>
          </div>"""

    new_menu = """          <!-- Quick Dropdown Menu for Plus button -->
          <div id="workPlusMenu" class="hidden absolute left-4 bottom-14 z-30 bg-[#262626] border border-[#383838] rounded-2xl p-1.5 shadow-2xl flex flex-col gap-1 w-72 text-[14px]">
            <button class="work-menu-item text-left px-3 py-1.5 hover:bg-[#333] rounded-xl text-slate-200 transition cursor-pointer" data-query="Tell me about Dutch research, BAK Utrecht, and Former West">🇳🇱 Dutch Research: BAK Utrecht</button>
            <button class="work-menu-item text-left px-3 py-1.5 hover:bg-[#333] rounded-xl text-slate-200 transition cursor-pointer" data-query="What is Arte Útil and the Commons at Van Abbe and Casco?">⚖️ Commons & Arte Útil: Casco & Van Abbe</button>
            <button class="work-menu-item text-left px-3 py-1.5 hover:bg-[#333] rounded-xl text-slate-200 transition cursor-pointer" data-query="How did Kunstinstituut Melly rename itself from Witte de With?">🏛️ Decolonial Renaming: Melly</button>
            <button class="work-menu-item text-left px-3 py-1.5 hover:bg-[#333] rounded-xl text-slate-200 transition cursor-pointer" data-query="Which museums and galleries are free to enter?">🎟️ Free Admission Spaces</button>
            <button class="work-menu-item text-left px-3 py-1.5 hover:bg-[#333] rounded-xl text-slate-200 transition cursor-pointer" data-query="Which museums are open on Mondays?">🕒 Monday Openings</button>
            <button class="work-menu-item text-left px-3 py-1.5 hover:bg-[#333] rounded-xl text-slate-200 transition cursor-pointer" data-query="Show spaces that do not take oil or weapons money">🌿 Fossil & Defense-Free</button>
            <button class="work-menu-item text-left px-3 py-1.5 hover:bg-[#333] rounded-xl text-slate-200 transition cursor-pointer" data-query="Tell me about London's independent art spaces">📍 London Art Guide</button>
            <button class="work-menu-item text-left px-3 py-1.5 hover:bg-[#333] rounded-xl text-slate-200 transition cursor-pointer" data-query="Tell me about New York's art spaces and board controversies">📍 New York Art Guide</button>
          </div>"""

    if old_menu in content:
        content = content.replace(old_menu, new_menu)
        print("Updated workPlusMenu")
    else:
        print("WARNING: old_menu not found")

    # 2. Update PRIORITY_CITIES
    old_cities = """    const PRIORITY_CITIES = [
      {{ name: 'NEW YORK', lon: -74.006, lat: 40.7128 }},
      {{ name: 'LONDON', lon: -0.1278, lat: 51.5074 }},"""

    new_cities = """    const PRIORITY_CITIES = [
      {{ name: 'NEW YORK', lon: -74.006, lat: 40.7128 }},
      {{ name: 'LONDON', lon: -0.1278, lat: 51.5074 }},
      {{ name: 'UTRECHT', lon: 5.1214, lat: 52.0907 }},
      {{ name: 'AMSTERDAM', lon: 4.9041, lat: 52.3676 }},
      {{ name: 'ROTTERDAM', lon: 4.4777, lat: 51.9244 }},
      {{ name: 'EINDHOVEN', lon: 5.4697, lat: 51.4416 }},"""

    if old_cities in content:
        content = content.replace(old_cities, new_cities)
        print("Updated PRIORITY_CITIES")
    else:
        print("WARNING: old_cities not found")

    # 3. Update findMentionedInst with regex word boundaries for short names
    old_inst_finder = """    function findMentionedInst(text) {{
      const t = (text || '').toLowerCase().trim();
      return ALL_INSTITUTIONS.find(i => {{
        const nameLow = i.name.toLowerCase();
        if (t.includes(nameLow)) return true;
        if (i.aliases && i.aliases.some(a => t.includes(a.toLowerCase()))) return true;
        return false;
      }});
    }}"""

    new_inst_finder = """    function findMentionedInst(text) {{
      const t = (text || '').toLowerCase().trim();
      return ALL_INSTITUTIONS.find(i => {{
        const nameLow = i.name.toLowerCase();
        if (t.includes(nameLow)) return true;
        if (i.aliases && i.aliases.some(a => {{
          const aLow = a.toLowerCase();
          if (aLow.length <= 3) {{
            const regex = new RegExp('(?:^|\\\\b|\\\\s)' + aLow + '(?:\\\\b|\\\\s|$)', 'i');
            return regex.test(t);
          }}
          return t.includes(aLow);
        }})) return true;
        return false;
      }});
    }}"""

    if old_inst_finder in content:
        content = content.replace(old_inst_finder, new_inst_finder)
        print("Updated findMentionedInst")
    else:
        print("WARNING: old_inst_finder not found")

    # 4. Update AI System Prompt with Dutch Research, BAK Utrecht, Former West, Rosi Braidotti, etc.
    old_system_prompt_target = """SCHOLARLY RESEARCH & MIT PRESS ART THEORY FOUNDATIONS (Explain simply in everyday English):
You have extensive mastery of the seminal art theory, curatorial studies, and institutional critique published by MIT Press, October, Zone Books, and Sternberg Press. When answering research questions, explain every finding in simple, accessible, everyday English:"""

    new_system_prompt = """SCHOLARLY RESEARCH, MIT PRESS ART THEORY & DUTCH RESEARCH FOUNDATIONS (Explain simply in everyday English):
You have extensive mastery of seminal art theory, curatorial studies, and institutional critique published by MIT Press, October, Zone Books, Sternberg Press, and Dutch research institutes (BAK Utrecht, Casco, Van Abbemuseum). When answering research questions, explain every finding in simple, accessible, everyday English:
- BAK, basis voor actuele kunst (Utrecht): Directed by Maria Hlavajova. Global epicenter of critical artistic research and political imagination. Spearheaded 'Former West' (2008–2016), co-published as a monumental 748-page compendium with MIT Press, establishing that 'the West' is not a universal center but a provincialized territory after 1989. Led landmark platforms 'Vectors of Commoning', 'Propositions for Non-Fascist Living', and the 'Posthuman Glossary' with Rosi Braidotti (Utrecht University).
- Casco Art Institute: Working for the Commons (Utrecht): Directed by Binna Choi. Transformed an exhibition gallery into a living ecosystem of the commons, feminist economies, and collaborative unlearning ('Site for Unlearning: Art Organization'). 100% free admission.
- Van Abbemuseum (Eindhoven): Directed by Charles Esche. Pioneered the 'Museum of Arte Útil' (Useful Art) with Tania Bruguera—reclaiming art as an instrument for civic utility and social change rather than a passive luxury spectacle. Developed 'Deviant Practice' to decolonize and queer museum archives. Championed by Claire Bishop in 'Radical Museology'.
- Kunstinstituut Melly (Rotterdam): Formerly Witte de With Center for Contemporary Art. Led a pioneering, multi-year collective public review to de-commemorate a colonial naval officer, renaming the institution in 2020 after Ken Lum's iconic public artwork 'Melly Shum Hates Her Job'. Publisher of the 'Source' research book series.
- De Appel (Amsterdam): Founded in 1975 by Wies Smals. Landmark performance archives (Marina Abramović & Ulay) and home of the celebrated 'Curatorial Programme' (CP) that revolutionized curating into an autonomous research discipline.
- Framer Framed (Amsterdam): Decolonial research platform interrogating critical museology, intercultural restitution, and climate justice.
- The Dutch Public Civic Funding Model: Funded primarily through multi-year structural subsidies (Mondriaan Fund / Gemeenten) subject to peer-review by artists and curators, shielding curators from commercial market pressures and billionaire trustee conflicts seen in US 501(c)(3) museums."""

    if old_system_prompt_target in content:
        content = content.replace(old_system_prompt_target, new_system_prompt)
        print("Updated AI System Prompt")
    else:
        print("WARNING: old_system_prompt_target not found")

    # 5. Insert Dutch Research Specialist Handlers in Offline Conversational Engine
    old_critique_block = """        // 4. Three Waves of Institutional Critique
        if (q.includes('institutional critique') || q.includes('haacke') || q.includes('andrea fraser') || q.includes('three waves') || q.includes('3 waves') || q.includes('waves of critique') || q.includes('fred wilson')) {{
          appendCuratorMessage(`
            <p class="text-slate-200">
              Institutional critique is art that examines the museum itself—its money, its board, and its politics. It happened in three main waves:
            </p>
            <p class="text-slate-300">
              1. <strong>First Wave (Late 1960s–1970s):</strong> Artists like Hans Haacke showed that museums are not neutral. In 1970, Haacke asked MoMA visitors whether they supported museum trustee Nelson Rockefeller's backing of the Vietnam War. In 1971, the Guggenheim cancelled Haacke's show because his artwork exposed the slum properties owned by a museum trustee.<br>
              2. <strong>Second Wave (1980s–1990s):</strong> Andrea Fraser and Fred Wilson showed that artists and visitors are part of the system too. Fraser gave satirical museum tours as a fake docent, while Fred Wilson rearranged museum archives in Baltimore (<em>Mining the Museum</em>) to expose histories of slavery and racial bias.<br>
              3. <strong>Third Wave (2010s–Present):</strong> Direct activist campaigns. Nan Goldin's group P.A.I.N. staged die-ins inside the Met, Guggenheim, and Louvre, forcing them to remove the Sackler family name because of the opioid crisis. In 2019, artists boycotted the Whitney Biennial until a tear gas manufacturer resigned from the board.
            </p>
          `);
          return;
        }}"""

    dutch_handlers = """        // 4. Three Waves of Institutional Critique
        if (q.includes('institutional critique') || q.includes('haacke') || q.includes('andrea fraser') || q.includes('three waves') || q.includes('3 waves') || q.includes('waves of critique') || q.includes('fred wilson')) {{
          appendCuratorMessage(`
            <p class="text-slate-200">
              Institutional critique is art that examines the museum itself—its money, its board, and its politics. It happened in three main waves:
            </p>
            <p class="text-slate-300">
              1. <strong>First Wave (Late 1960s–1970s):</strong> Artists like Hans Haacke showed that museums are not neutral. In 1970, Haacke asked MoMA visitors whether they supported museum trustee Nelson Rockefeller's backing of the Vietnam War. In 1971, the Guggenheim cancelled Haacke's show because his artwork exposed the slum properties owned by a museum trustee.<br>
              2. <strong>Second Wave (1980s–1990s):</strong> Andrea Fraser and Fred Wilson showed that artists and visitors are part of the system too. Fraser gave satirical museum tours as a fake docent, while Fred Wilson rearranged museum archives in Baltimore (<em>Mining the Museum</em>) to expose histories of slavery and racial bias.<br>
              3. <strong>Third Wave (2010s–Present):</strong> Direct activist campaigns. Nan Goldin's group P.A.I.N. staged die-ins inside the Met, Guggenheim, and Louvre, forcing them to remove the Sackler family name because of the opioid crisis. In 2019, artists boycotted the Whitney Biennial until a tear gas manufacturer resigned from the board.
            </p>
          `);
          return;
        }}

        // =========================================================================
        // 🇳🇱 DUTCH ARTISTIC RESEARCH & BAK UTRECHT CANON
        // =========================================================================

        // D1. BAK, basis voor actuele kunst (Utrecht)
        if (
          q.includes('utrecht bac') || q.includes('bac utrecht') || q.includes('bak utrecht') || q.includes('utrecht bak') ||
          q.includes('basis voor actuele kunst') || q.includes('maria hlavajova') || q.includes('former west') ||
          ((/\\b(bak|bac)\\b/i.test(q)) && (q.includes('utrecht') || q.includes('art') || q.includes('research') || q.includes('space') || q.includes('museum') || q.includes('theory') || q.includes('curat') || q.includes('learn')))
        ) {{
          const bak = ALL_INSTITUTIONS.find(i => i.id === 'bak-utrecht' || i.name.includes('BAK'));
          appendCuratorMessage(`
            <p class="text-slate-200">
              ${{formatInstLink(bak)}} in Utrecht is one of the world's most influential centers for critical artistic research, political imagination, and institutional critique.
            </p>
            <p class="text-slate-300">
              Directed by Maria Hlavajova, BAK does not treat art as a luxury commodity or decorative object. Instead, it functions as a public research laboratory and political assembly where artists, philosophers, and community organizers address systemic global crises.
            </p>
            <p class="text-slate-300">
              Key research milestones led by BAK include:
            </p>
            <p class="text-slate-300">
              - <strong><em>Former West</em> (2008–2016, co-published with MIT Press):</strong> A monumental 8-year transnational research project investigating geopolitical transformations after 1989. It argued that the fall of the Berlin Wall did not just collapse the "Former East"—it fundamentally provincialized the "West," showing that Western democratic capitalism is not the universal end-goal of human history.<br>
              - <strong><em>Vectors of Commoning:</em></strong> Long-term research investigating how cultural institutions can become living commons—reclaiming public wealth, feminist mutual care, and collaborative ownership against neoliberal privatization.<br>
              - <strong><em>Posthuman Glossary</em> (with Rosi Braidotti & Utrecht University):</strong> Seminal research developed with feminist philosopher Rosi Braidotti exploring post-anthropocentric ethics, climate justice, and ecological survival.<br>
              - <strong><em>Propositions for Non-Fascist Living:</em></strong> Assemblies examining how cultural organizations can organize daily democratic resistance against the rise of contemporary authoritarianism.
            </p>
            <p class="text-slate-300">
              <strong>Visiting & Funding:</strong> Located at Pauwstraat 13A in historic central Utrecht (10-minute walk from Utrecht Centraal). Funded through public civic grants from the Dutch Mondriaan Fund and Gemeente Utrecht with zero corporate board leverage. Operates a solidarity sliding scale (€0–€6), making it free for youth and activists.
            </p>
          `);
          if (bak) selectInstitution(bak, true);
          return;
        }}

        // D2. Dutch Artistic Research Ecosystem & Mondriaan Fund Civic Model
        if (
          q.includes('dutch research') || q.includes('netherlands research') || q.includes('dutch art') ||
          q.includes('dutch model') || q.includes('artistic research') || q.includes('onderzoek in de kunst') ||
          q.includes('mondriaan fund') || q.includes('mondriaan fonds') ||
          (q.includes('netherlands') && (q.includes('funding') || q.includes('research') || q.includes('critical') || q.includes('civic')))
        ) {{
          const bak = ALL_INSTITUTIONS.find(i => i.id === 'bak-utrecht' || i.name.includes('BAK'));
          const casco = ALL_INSTITUTIONS.find(i => i.id === 'casco-art-institute' || i.name.includes('Casco'));
          const vanabbe = ALL_INSTITUTIONS.find(i => i.name.includes('Van Abbemuseum'));
          const melly = ALL_INSTITUTIONS.find(i => i.id === 'kunstinstituut-melly' || i.name.includes('Melly'));
          const deappel = ALL_INSTITUTIONS.find(i => i.id === 'de-appel' || i.name.includes('De Appel'));
          const framer = ALL_INSTITUTIONS.find(i => i.id === 'framer-framed' || i.name.includes('Framer Framed'));

          appendCuratorMessage(`
            <p class="text-slate-200">
              The Netherlands is the global capital of <strong>Artistic Research</strong> (<em>onderzoek in de kunst</em>) and progressive institutional critique:
            </p>
            <p class="text-slate-300">
              Unlike the American museum model—where wealthy billionaire donors buy board seats to receive tax deductions and suppress political critique—Dutch cultural spaces receive structural civic funding from the <strong>Mondriaan Fund</strong> and municipal councils. Peer panels of artists and curators allocate grants based on critical rigor rather than private patron approval.
            </p>
            <p class="text-slate-300">
              Here are the six essential Dutch research institutions mapped in Culture Atlas:
            </p>
            <p class="text-slate-300">
              1. ${{formatInstLink(bak)}} (Utrecht): World leader in critical theory, commons research, and co-publisher of <em>Former West</em> with MIT Press.<br>
              2. ${{formatInstLink(casco)}} (Utrecht): Replaced traditional gallery display with cooperative commoning, feminist economies, and institutional unlearning.<br>
              3. ${{formatInstLink(vanabbe)}} (Eindhoven): Directed by Charles Esche; pioneered the <em>Museum of Arte Útil</em> (useful art) with Tania Bruguera and archival <em>Deviant Practice</em>.<br>
              4. ${{formatInstLink(melly)}} (Rotterdam): Renowned for the historic decolonial process of renaming itself away from colonial naval officer Witte de With.<br>
              5. ${{formatInstLink(deappel)}} (Amsterdam): Home of the legendary Curatorial Programme (CP) since 1994 and seminal 1970s performance archives.<br>
              6. ${{formatInstLink(framer)}} (Amsterdam): Intercultural decolonial research platform challenging Eurocentric museology and restitution policies.
            </p>
          `);
          flyTo(5.2, 52.1);
          return;
        }}

        // D3. Casco Art Institute: Working for the Commons (Utrecht)
        if (q.includes('casco') || q.includes('working for the commons') || (q.includes('commons') && (q.includes('utrecht') || q.includes('art') || q.includes('institute'))) || q.includes('binna choi') || q.includes('site for unlearning')) {{
          const casco = ALL_INSTITUTIONS.find(i => i.id === 'casco-art-institute' || i.name.includes('Casco'));
          appendCuratorMessage(`
            <p class="text-slate-200">
              ${{formatInstLink(casco)}} in Utrecht is an internationally renowned experiment in <strong>institutional commoning</strong>.
            </p>
            <p class="text-slate-300">
              Under the directorship of Binna Choi, Casco realized that presenting exhibitions about politics while operating internally as a hierarchical, corporate-style gallery was hypocritical. In 2018, they officially renamed themselves <em>Working for the Commons</em> and restructured their entire organizational model:
            </p>
            <p class="text-slate-300">
              - <strong>Art as Commons:</strong> Rather than viewing artworks as private property or temporary entertainment, Casco treats culture as a shared collective resource maintained for mutual care.<br>
              - <strong>Site for Unlearning: Art Organization:</strong> Casco actively experiments with non-hierarchical salaries, shared housework, community farming, and consensus decision-making.<br>
              - <strong>Publishing Class:</strong> A long-running collaborative publishing initiative that investigates how books can circulate outside commercial market monopolies.
            </p>
            <p class="text-slate-300">
              Admission is 100% free. Located at Lange Nieuwstraat 7 in Utrecht's Museumkwartier, featuring an open communal kitchen, garden courtyard, and research library.
            </p>
          `);
          if (casco) selectInstitution(casco, true);
          return;
        }}

        // D4. Van Abbemuseum & Arte Útil (Eindhoven)
        if (q.includes('van abbemuseum') || q.includes('van abbe') || q.includes('arte util') || q.includes('useful art') || q.includes('charles esche') || q.includes('deviant practice')) {{
          const vanabbe = ALL_INSTITUTIONS.find(i => i.name.includes('Van Abbemuseum'));
          appendCuratorMessage(`
            <p class="text-slate-200">
              ${{formatInstLink(vanabbe)}} in Eindhoven is one of Europe's most radical public civic museums.
            </p>
            <p class="text-slate-300">
              Under director Charles Esche, Van Abbemuseum rejected the standard corporate blockbuster model to become a leading laboratory for <strong>Radical Museology</strong> (as documented by Claire Bishop in her 2013 book):
            </p>
            <p class="text-slate-300">
              - <strong>Museum of Arte Útil (initiated with Tania Bruguera):</strong> Questions the idea that art must be passive and useless. Arte Útil ('useful art') proposes that artistic imagination should be deployed as a concrete tool—helping communities address housing inequality, legal defense, and ecological survival.<br>
              - <strong>Deviant Practice:</strong> A long-term research project opening the museum's permanent collection (including works by El Lissitzky, Picasso, and Chagall) to queer, decolonial, and disability-inclusive reinterpretation.<br>
              - <strong>Clean Ethical Charter:</strong> In 2021, Van Abbemuseum ratified a strict climate and governance charter prohibiting any sponsorship from fossil fuels, weapons manufacturers, or human-rights-flagged corporations.
            </p>
          `);
          if (vanabbe) selectInstitution(vanabbe, true);
          return;
        }}

        // D5. Kunstinstituut Melly & Decolonial Renaming (Rotterdam)
        if (q.includes('kunstinstituut melly') || q.includes('melly') || q.includes('witte de with') || q.includes('melly shum') || q.includes('decolonial renaming')) {{
          const melly = ALL_INSTITUTIONS.find(i => i.id === 'kunstinstituut-melly' || i.name.includes('Melly'));
          appendCuratorMessage(`
            <p class="text-slate-200">
              ${{formatInstLink(melly)}} in Rotterdam represents one of the most significant real-world examples of <strong>institutional accountability and decolonial renaming</strong> in contemporary art history.
            </p>
            <p class="text-slate-300">
              - <strong>The Historical Context:</strong> Founded in 1990 as <em>Witte de With Center for Contemporary Art</em>, named after the Rotterdam street where it sits. That street commemorated Witte Corneliszoon de With, a 17th-century naval officer who fought for the Dutch East India Company (VOC) and Dutch West India Company (WIC).<br>
              - <strong>The Accountability Process:</strong> In 2017, after open letters from artists and activists criticizing the commemoration of colonial exploitation, director Sofía Hernández Chong Cuy and the board launched a 3-year public audit.<br>
              - <strong>Collective Renaming:</strong> In January 2021, the institution officially renamed itself <em>Kunstinstituut Melly</em>, after Canadian artist Ken Lum's iconic 1990 artwork <em>Melly Shum Hates Her Job</em>, which has hung permanently on the museum's exterior wall for over three decades.<br>
              - <strong>Research Publishing:</strong> Melly is celebrated for its <em>Source</em> book series, experimental curatorial fellowships, and Friday evening free public access.
            </p>
          `);
          if (melly) selectInstitution(melly, true);
          return;
        }}

        // D6. De Appel & Curatorial Pedagogy (Amsterdam)
        if (q.includes('de appel') || q.includes('curatorial programme') || q.includes('wies smals')) {{
          const deappel = ALL_INSTITUTIONS.find(i => i.id === 'de-appel' || i.name.includes('De Appel'));
          appendCuratorMessage(`
            <p class="text-slate-200">
              ${{formatInstLink(deappel)}} in Amsterdam is a historic vanguard space that fundamentally shaped modern curatorial education.
            </p>
            <p class="text-slate-300">
              - <strong>Founding (1975):</strong> Established by Wies Smals as an alternative art space dedicated to performance art, body art, and ephemeral installations, hosting historic performances by Marina Abramović and Ulay.<br>
              - <strong>Curatorial Programme (CP):</strong> Launched in 1994, it was one of the world's very first training programs for contemporary curators. Rather than teaching dry art cataloging, CP pioneered curating as an autonomous research practice, political discourse, and collective exhibition-making.<br>
              - <strong>Research Archive:</strong> De Appel preserves an extraordinary public research archive of 1970s–1990s conceptual and performance art documentation.
            </p>
          `);
          if (deappel) selectInstitution(deappel, true);
          return;
        }}

        // D7. Rosi Braidotti & Posthumanist Theory (Utrecht)
        if (q.includes('braidotti') || q.includes('posthuman') || q.includes('posthumanism') || q.includes('post-human')) {{
          const bak = ALL_INSTITUTIONS.find(i => i.id === 'bak-utrecht' || i.name.includes('BAK'));
          appendCuratorMessage(`
            <p class="text-slate-200">
              Feminist philosopher Rosi Braidotti (Distinguished University Professor at Utrecht University) has deeply influenced contemporary art, curating, and institutional theory.
            </p>
            <p class="text-slate-300">
              In close partnership with ${{formatInstLink(bak)}} in Utrecht, Braidotti co-developed research platforms like the <em>Posthuman Glossary</em> (Bloomsbury / BAK, 2018):
            </p>
            <p class="text-slate-300">
              - <strong>Beyond Human Supremacy:</strong> Braidotti critiques traditional Western humanism, which placed the white, wealthy European male at the center of the universe while treating nature, indigenous peoples, and animals as exploitable property.<br>
              - <strong>Affirmative Ethics & The Anthropocene:</strong> In an era of climate breakdown and digital algorithms, art must generate 'affirmative ethics'—practical ways of living together that connect humans with ecosystems and technology without exploitation.<br>
              - <strong>Impact on Museums:</strong> This research pushed museums to stop acting like dead trophy vaults, transforming them into living eco-assemblies that actively address environmental collapse and cross-species solidarity.
            </p>
          `);
          if (bak) selectInstitution(bak, true);
          return;
        }}

        // D8. Former West Project (BAK + MIT Press)
        if (q.includes('former west') || q.includes('former east') || (q.includes('west') && q.includes('after 1989'))) {{
          const bak = ALL_INSTITUTIONS.find(i => i.id === 'bak-utrecht' || i.name.includes('BAK'));
          appendCuratorMessage(`
            <p class="text-slate-200">
              <em>Former West</em> (2008–2016) is one of the most important artistic research projects of the 21st century, initiated by ${{formatInstLink(bak)}} in Utrecht and co-published with MIT Press.
            </p>
            <p class="text-slate-300">
              Here is why it changed contemporary curatorial thinking:
            </p>
            <p class="text-slate-300">
              - <strong>Rethinking 1989:</strong> When the Berlin Wall fell in 1989, Western pundits declared 'the end of history' and assumed that only the communist Eastern bloc had changed ('Former East'). BAK posed the critical counter-question: <em>What happened to the West?</em><br>
              - <strong>Provincializing the West:</strong> The project showed that the 'West' is no longer the universal center of culture or democracy. Instead, it has become 'former'—facing deep crises of inequality, austerity, and democratic breakdown.<br>
              - <strong>Global Intellectual Compendium:</strong> Culminating in the 748-page book <em>Former West: Art and the Contemporary After 1989</em> (MIT Press / BAK, edited by Maria Hlavajova and Simon Sheikh), bringing together over 300 thinkers including Boris Groys, Achille Mbembe, Irit Rogoff, and Nancy Fraser.
            </p>
          `);
          if (bak) selectInstitution(bak, true);
          return;
        }}

        // D9. Utrecht Cultural Guide
        if (q.includes('utrecht')) {{
          const bak = ALL_INSTITUTIONS.find(i => i.id === 'bak-utrecht' || i.name.includes('BAK'));
          const casco = ALL_INSTITUTIONS.find(i => i.id === 'casco-art-institute' || i.name.includes('Casco'));
          appendCuratorMessage(`
            <p class="text-slate-200">
              Utrecht is Europe's premier capital for critical artistic research, political philosophy, and the commons:
            </p>
            <p class="text-slate-300">
              Unlike commercial art metropolises driven by auction houses and real-estate developers, Utrecht's art scene is built on deep institutional critique and intellectual rigor:
            </p>
            <p class="text-slate-300">
              - ${{formatInstLink(bak)}} on Pauwstraat: The international benchmark for research-based art practice, co-publisher of <em>Former West</em> with MIT Press, and pioneer of the <em>Posthuman Glossary</em> with Utrecht University.<br>
              - ${{formatInstLink(casco)}} on Lange Nieuwstraat: A radical experiment that transformed an art gallery into a working cooperative commons with free public admission and shared community resources.
            </p>
            <p class="text-slate-300">
              Both spaces are an easy 10 to 15-minute walk from Utrecht Centraal railway station (just 25 minutes by train from Amsterdam Centraal or Schiphol Airport).
            </p>
          `);
          filterByCity('Utrecht', true, false);
          return;
        }}

        // D10. Rotterdam Cultural Guide
        if (q.includes('rotterdam')) {{
          const melly = ALL_INSTITUTIONS.find(i => i.id === 'kunstinstituut-melly' || i.name.includes('Melly'));
          appendCuratorMessage(`
            <p class="text-slate-200">
              Rotterdam is famous for bold modernist architecture and fearless contemporary art institutions:
            </p>
            <p class="text-slate-300">
              - ${{formatInstLink(melly)}} on Witte de Withstraat: Renowned for its historic public decolonial audit and renaming from Witte de With, celebrated research monograph series, and Ken Lum's permanent artwork <em>Melly Shum Hates Her Job</em>.
            </p>
            <p class="text-slate-300">
              Just a 12-minute walk from Rotterdam Centraal, with free public admission every Friday evening from 18:00 to 21:00.
            </p>
          `);
          filterByCity('Rotterdam', true, false);
          return;
        }}

        // D11. Amsterdam Cultural Guide
        if (q.includes('amsterdam')) {{
          const sted = ALL_INSTITUTIONS.find(i => i.name.includes('Stedelijk'));
          const deappel = ALL_INSTITUTIONS.find(i => i.id === 'de-appel' || i.name.includes('De Appel'));
          const framer = ALL_INSTITUTIONS.find(i => i.id === 'framer-framed' || i.name.includes('Framer Framed'));
          appendCuratorMessage(`
            <p class="text-slate-200">
              Amsterdam features historic modern collections alongside pioneering independent research spaces:
            </p>
            <p class="text-slate-300">
              - ${{formatInstLink(deappel)}}: Historic vanguard founded in 1975, celebrated for 1970s performance art archives and the Curatorial Programme (CP).<br>
              - ${{formatInstLink(framer)}} in Amsterdam Oost: Intercultural decolonial research platform investigating restitution, climate justice, and community archives.<br>
              - ${{formatInstLink(sted)}} on Museumplein: The civic modern and contemporary art museum, housed in its iconic futuristic 'Bathtub' wing.
            </p>
          `);
          filterByCity('Amsterdam', true, false);
          return;
        }}"""

    if old_critique_block in content:
        content = content.replace(old_critique_block, dutch_handlers)
        print("Inserted Dutch research handlers")
    else:
        print("WARNING: old_critique_block not found")

    # 6. Update Exact Prompt 1, 2, 4 and MIT Press Canon
    old_p1 = """        // Exact Prompt 1: Find independent art spaces near me
        if (q.includes('near me') || q.includes('spaces near me') || q.includes('art spaces near')) {{
          appendCuratorMessage(`
            <p class="text-slate-200">
              Here are verified independent art spaces with clean funding. Tell me your city (like <a href="#" class="city-link text-[#93c5fd] hover:underline" data-city="London">London</a>, <a href="#" class="city-link text-[#93c5fd] hover:underline" data-city="New York">New York</a>, or <a href="#" class="city-link text-[#93c5fd] hover:underline" data-city="Paris">Paris</a>) to find spaces closest to you:
            </p>
            <p class="text-slate-300">
              - In London: ${{formatInstLink(ALL_INSTITUTIONS.find(i => i.name.includes('Chisenhale')))}} in Bow and ${{formatInstLink(ALL_INSTITUTIONS.find(i => i.name.includes('Camden')))}} in North London (both free).<br>
              - In New York: ${{formatInstLink(ALL_INSTITUTIONS.find(i => i.name.includes('Artists Space')))}} in Tribeca and ${{formatInstLink(ALL_INSTITUTIONS.find(i => i.name.includes('SculptureCenter')))}} in Queens.<br>
              - In Paris: ${{formatInstLink(ALL_INSTITUTIONS.find(i => i.name.includes('Bétonsalon')))}} in the 13th and ${{formatInstLink(ALL_INSTITUTIONS.find(i => i.name.includes('Palais de Tokyo')))}}.
            </p>
          `);
          return;
        }}"""

    new_p1 = """        // Exact Prompt 1: Find independent art spaces near me
        if (q.includes('near me') || q.includes('spaces near me') || q.includes('art spaces near')) {{
          appendCuratorMessage(`
            <p class="text-slate-200">
              Here are verified independent art spaces with clean funding. Tell me your city (like <a href="#" class="city-link text-[#93c5fd] hover:underline" data-city="London">London</a>, <a href="#" class="city-link text-[#93c5fd] hover:underline" data-city="New York">New York</a>, <a href="#" class="city-link text-[#93c5fd] hover:underline" data-city="Utrecht">Utrecht</a>, or <a href="#" class="city-link text-[#93c5fd] hover:underline" data-city="Paris">Paris</a>) to find spaces closest to you:
            </p>
            <p class="text-slate-300">
              - In Utrecht & The Netherlands: ${{formatInstLink(ALL_INSTITUTIONS.find(i => i.id === 'bak-utrecht' || i.name.includes('BAK')))}} in Utrecht, ${{formatInstLink(ALL_INSTITUTIONS.find(i => i.id === 'casco-art-institute')))}} in Utrecht, and ${{formatInstLink(ALL_INSTITUTIONS.find(i => i.id === 'kunstinstituut-melly')))}} in Rotterdam.<br>
              - In London: ${{formatInstLink(ALL_INSTITUTIONS.find(i => i.name.includes('Chisenhale')))}} in Bow and ${{formatInstLink(ALL_INSTITUTIONS.find(i => i.name.includes('Camden')))}} in North London (both free).<br>
              - In New York: ${{formatInstLink(ALL_INSTITUTIONS.find(i => i.name.includes('Artists Space')))}} in Tribeca and ${{formatInstLink(ALL_INSTITUTIONS.find(i => i.name.includes('SculptureCenter')))}} in Queens.<br>
              - In Paris: ${{formatInstLink(ALL_INSTITUTIONS.find(i => i.name.includes('Bétonsalon')))}} in the 13th and ${{formatInstLink(ALL_INSTITUTIONS.find(i => i.name.includes('Palais de Tokyo')))}}.
            </p>
          `);
          return;
        }}"""

    if old_p1 in content:
        content = content.replace(old_p1, new_p1)
        print("Updated Exact Prompt 1")
    else:
        print("WARNING: old_p1 not found")

    old_p2 = """        // Exact Prompt 2: Who funds this museum?
        if (q.includes('who funds this museum') || (q.includes('who funds') && q.length < 30)) {{
          appendCuratorMessage(`
            <p class="text-slate-200">
              Every museum in Culture Atlas is audited for clean, transparent funding:
            </p>
            <p class="text-slate-300">
              1. <strong>Civic Arts Councils:</strong> European institutions receive direct public funding (Arts Council England, DRAC France, Danish State), ensuring curators are accountable to the public rather than corporate sponsors.<br>
              2. <strong>Regulatory Filings:</strong> In the US, we audit IRS Form 990 (Schedule I grants and Schedule L trustee deals) to confirm board members have no ties to weapons manufacturing, fossil fuels, or private prisons.<br>
              3. <strong>Artist-Run Cooperatives:</strong> Managed directly by artists without billionaire corporate boards.
            </p>
            <p class="text-slate-300">
              Type the name of any museum (like MoMA, Tate, Chisenhale, or CAPC) to see its specific funding audit.
            </p>
          `);
          return;
        }}"""

    new_p2 = """        // Exact Prompt 2: Who funds this museum?
        if (q.includes('who funds this museum') || (q.includes('who funds') && q.length < 30)) {{
          appendCuratorMessage(`
            <p class="text-slate-200">
              Every museum in Culture Atlas is audited for clean, transparent funding:
            </p>
            <p class="text-slate-300">
              1. <strong>Civic Arts Councils & The Dutch Model:</strong> European spaces receive structural civic funding (Mondriaan Fund in the Netherlands, Arts Council England, DRAC France). Peer panels of curators and artists allocate funding based on critical merit, protecting curators from private corporate censorship.<br>
              2. <strong>Regulatory Filings:</strong> In the US, we audit IRS Form 990 (Schedule I grants and Schedule L trustee deals) to confirm board members have no ties to weapons manufacturing, fossil fuels, or private prisons.<br>
              3. <strong>Artist-Run & Cooperative Commons:</strong> Managed directly by artists and communities (like Casco in Utrecht or Chisenhale in London) without billionaire corporate boards.
            </p>
            <p class="text-slate-300">
              Type the name of any museum (like MoMA, BAK Utrecht, Tate, or Van Abbemuseum) to see its specific funding audit.
            </p>
          `);
          return;
        }}"""

    if old_p2 in content:
        content = content.replace(old_p2, new_p2)
        print("Updated Exact Prompt 2")
    else:
        print("WARNING: old_p2 not found")

    old_p4 = """        // Exact Prompt 4: Find writing about this space in e-flux or MIT Press
        if (q.includes('writing about this space') || (q.includes('e-flux') && q.includes('mit press')) || q.includes('find writing about')) {{
          appendCuratorMessage(`
            <p class="text-slate-200">
              Critical writing and theory from MIT Press and <em>e-flux journal</em> on these spaces:
            </p>
            <p class="text-slate-300">
              - <strong>MIT Press:</strong> In <em>Beyond Objecthood</em> (2017), James Voorhies explores how independent galleries preserved experimental exhibition forms after mega-museums turned art into tourist spectacles. In <em>One Place after Another</em>, Miwon Kwon examines how site-specific art transformed from sculptures to community projects.<br>
              - <strong>e-flux journal:</strong> Hito Steyerl's <em>Is a Museum a Factory?</em> examines how museum visitors produce economic value for luxury real estate, while Boris Groys analyzes the public museum as an egalitarian secular archive.
            </p>
          `);
          return;
        }}"""

    new_p4 = """        // Exact Prompt 4: Find writing about this space in e-flux or MIT Press
        if (q.includes('writing about this space') || (q.includes('e-flux') && q.includes('mit press')) || q.includes('find writing about')) {{
          appendCuratorMessage(`
            <p class="text-slate-200">
              Critical writing and theory from MIT Press, <em>e-flux journal</em>, and Dutch research institutes:
            </p>
            <p class="text-slate-300">
              - <strong>MIT Press & BAK Utrecht:</strong> In <em>Former West: Art and the Contemporary After 1989</em> (2016), Maria Hlavajova and Simon Sheikh examine how the collapse of the Soviet bloc simultaneously provincialized the West, demanding new global commons and post-capitalist curatorial forms.<br>
              - <strong>MIT Press Theory:</strong> In <em>Beyond Objecthood</em> (2017), James Voorhies explores how independent galleries preserved experimental exhibition forms after mega-museums turned art into tourist spectacles. In <em>One Place after Another</em>, Miwon Kwon tracks the shift of site-specific art from physical monuments to traveling community interventions.<br>
              - <strong>e-flux journal:</strong> Hito Steyerl's <em>Is a Museum a Factory?</em> examines how museum visitors produce economic value for luxury real estate, while Boris Groys analyzes the public museum as an egalitarian secular archive.
            </p>
          `);
          return;
        }}"""

    if old_p4 in content:
        content = content.replace(old_p4, new_p4)
        print("Updated Exact Prompt 4")
    else:
        print("WARNING: old_p4 not found")

    old_mit_canon = """        // Research Handler 6: MIT Press Canon & Essential Art Theory Books
        if (q.includes('mit press') || q.includes('mit book') || q.includes('mit oress') || q.includes('essential book') || q.includes('theory book') || q.includes('reading list') || q.includes('curatorial book') || (q.includes('mit') && q.includes('art'))) {{
          appendCuratorMessage(`
            <p class="text-slate-200">
              MIT Press has published the most influential research and books on modern art, museums, and institutional critique. Here is the essential reading list explained in plain terms:
            </p>
            <p class="text-slate-300">
              1. <strong><em>One Place after Another: Site-Specific Art and Locational Identity</em> by Miwon Kwon (2002):</strong> The definitive study of how art moved from physical statues in plazas to temporary social projects in neighborhoods, and how museums hire artists like traveling corporate consultants.<br>
              2. <strong><em>Beyond Objecthood: The Exhibition as a Critical Form since 1968</em> by James Voorhies (2017):</strong> Shows how the exhibition itself became an artwork, and how corporate mega-museums turned experimental art into tourist entertainment.<br>
              3. <strong><em>Institutional Critique: An Anthology of Artists' Writings</em> edited by Alexander Alberro & Blake Stimson (2009):</strong> The essential collection of primary letters, interviews, and manifestos by artists who exposed the hidden power and money behind museum walls.<br>
              4. <strong><em>The Cultural Logic of the Late Capitalist Museum</em> by Rosalind Krauss (1990):</strong> Explains how modern museums transformed from quiet study archives into spectacle machines designed like luxury shopping malls.<br>
              5. <strong><em>Neo-Avantgarde and Culture Industry</em> by Benjamin H.D. Buchloh (2000):</strong> Details the 'aesthetic of administration'—why conceptual art started looking like office memos and legal contracts.<br>
              6. <strong><em>Art Power</em> by Boris Groys (2008):</strong> Explains why public museums are democratic: they protect art from the whims of the commercial market and treat all artworks as equal.<br>
              7. <strong><em>Heritage and Debt: Art in Globalization</em> by David Joselit (2020):</strong> Explores how non-Western nations and museums manage stolen historical heritage while competing in the global contemporary art world.
            </p>
          `);
          return;
        }}"""

    new_mit_canon = """        // Research Handler 6: MIT Press Canon & Essential Art Theory Books
        if (q.includes('mit press') || q.includes('mit book') || q.includes('mit oress') || q.includes('essential book') || q.includes('theory book') || q.includes('reading list') || q.includes('curatorial book') || (q.includes('mit') && q.includes('art'))) {{
          appendCuratorMessage(`
            <p class="text-slate-200">
              MIT Press has published the most influential research and books on modern art, museums, and institutional critique. Here is the essential reading list explained in plain terms:
            </p>
            <p class="text-slate-300">
              1. <strong><em>Former West: Art and the Contemporary After 1989</em> edited by Maria Hlavajova & Simon Sheikh (BAK / MIT Press, 2016):</strong> The seminal 748-page research compendium produced with BAK in Utrecht, investigating how the post-1989 world decentered Western cultural hegemony and created new spaces for the commons.<br>
              2. <strong><em>One Place after Another: Site-Specific Art and Locational Identity</em> by Miwon Kwon (2002):</strong> The definitive study of how art moved from physical statues in plazas to temporary social projects in neighborhoods, and how museums hire artists like traveling corporate consultants.<br>
              3. <strong><em>Beyond Objecthood: The Exhibition as a Critical Form since 1968</em> by James Voorhies (2017):</strong> Shows how the exhibition itself became an artwork, and how corporate mega-museums turned experimental art into tourist entertainment.<br>
              4. <strong><em>Institutional Critique: An Anthology of Artists' Writings</em> edited by Alexander Alberro & Blake Stimson (2009):</strong> The essential collection of primary letters, interviews, and manifestos by artists who exposed the hidden power and money behind museum walls.<br>
              5. <strong><em>The Cultural Logic of the Late Capitalist Museum</em> by Rosalind Krauss (1990):</strong> Explains how modern museums transformed from quiet study archives into spectacle machines designed like luxury shopping malls.<br>
              6. <strong><em>Neo-Avantgarde and Culture Industry</em> by Benjamin H.D. Buchloh (2000):</strong> Details the 'aesthetic of administration'—why conceptual art started looking like office memos and legal contracts.<br>
              7. <strong><em>Art Power</em> by Boris Groys (2008):</strong> Explains why public museums are democratic: they protect art from the whims of the commercial market and treat all artworks as equal.<br>
              8. <strong><em>Heritage and Debt: Art in Globalization</em> by David Joselit (2020):</strong> Explores how non-Western nations and museums manage stolen historical heritage while competing in the global contemporary art world.
            </p>
          `);
          return;
        }}"""

    if old_mit_canon in content:
        content = content.replace(old_mit_canon, new_mit_canon)
        print("Updated MIT Press Canon")
    else:
        print("WARNING: old_mit_canon not found")

    with open('build_conversational_atlas.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Successfully wrote updated build_conversational_atlas.py!")

if __name__ == '__main__':
    patch()
