def update_widget_script():
    with open('build_conversational_widget.py', 'r', encoding='utf-8') as f:
        content = f.read()

    target = """        // Research: Landmark Shows
        if (query.includes('landmark') || query.includes('szeemann') || query.includes('when attitudes') || query.includes('documenta')) {{"""

    dutch_widget_block = """        // Research: BAK Utrecht & Former West
        if (
          query.includes('utrecht bac') || query.includes('bac utrecht') || query.includes('bak utrecht') || query.includes('utrecht bak') ||
          query.includes('basis voor actuele kunst') || query.includes('maria hlavajova') || query.includes('former west') ||
          ((/\\b(bak|bac)\\b/i.test(query)) && (query.includes('utrecht') || query.includes('art') || query.includes('research') || query.includes('space') || query.includes('museum') || query.includes('theory') || query.includes('curat') || query.includes('learn')))
        ) {{
          const bak = DATA.find(i => i.id === 'bak-utrecht' || i.name.includes('BAK'));
          appendWCurator(`
            <p class="text-slate-200">
              ${{formatWInstLink(bak)}} in Utrecht is one of the world's most influential centers for critical artistic research, political imagination, and institutional critique.
            </p>
            <p class="text-slate-300">
              Directed by Maria Hlavajova, BAK does not treat art as a luxury commodity. Instead, it functions as a public research laboratory and political assembly where artists and philosophers address global crises.
            </p>
            <p class="text-slate-300">
              Key research milestones include:
            </p>
            <p class="text-slate-300">
              - <strong><em>Former West</em> (2008–2016, co-published with MIT Press):</strong> Landmark 8-year transnational research project showing that the fall of the Berlin Wall provincialized the West, proving that Western capitalism is not the universal end-goal of human history.<br>
              - <strong><em>Vectors of Commoning:</em></strong> Long-term research into transforming art institutions into shared civic commons rather than privatized speculative assets.<br>
              - <strong><em>Posthuman Glossary</em> (with Rosi Braidotti, Utrecht University):</strong> Groundbreaking research exploring post-anthropocentric ethics and ecological survival.<br>
              - <strong><em>Propositions for Non-Fascist Living:</em></strong> Assemblies examining collective democratic resistance against rising authoritarianism.
            </p>
            <p class="text-slate-300">
              Located at Pauwstraat 13A in central Utrecht. Backed by public civic grants from the Dutch Mondriaan Fund with a solidarity sliding scale (€0–€6).
            </p>
          `);
          if (bak) selectWInstitution(bak, true);
          return;
        }}

        // Research: Dutch Artistic Research & Ecosystem
        if (query.includes('dutch research') || query.includes('netherlands research') || query.includes('dutch art') || query.includes('artistic research') || query.includes('mondriaan fund')) {{
          const bak = DATA.find(i => i.id === 'bak-utrecht' || i.name.includes('BAK'));
          const casco = DATA.find(i => i.id === 'casco-art-institute' || i.name.includes('Casco'));
          const vanabbe = DATA.find(i => i.name.includes('Van Abbemuseum'));
          const melly = DATA.find(i => i.id === 'kunstinstituut-melly' || i.name.includes('Melly'));
          appendWCurator(`
            <p class="text-slate-200">
              The Netherlands is the global capital of <strong>Artistic Research</strong> (<em>onderzoek in de kunst</em>):
            </p>
            <p class="text-slate-300">
              Funded primarily through structural public grants from the <strong>Mondriaan Fund</strong> rather than private billionaire boards, Dutch spaces operate with fearless curatorial independence:
            </p>
            <p class="text-slate-300">
              - ${{formatWInstLink(bak)}} (Utrecht): World leader in critical theory and co-publisher of <em>Former West</em> with MIT Press.<br>
              - ${{formatWInstLink(casco)}} (Utrecht): Replaced traditional exhibitions with cooperative commoning and feminist economies.<br>
              - ${{formatWInstLink(vanabbe)}} (Eindhoven): Pioneered the <em>Museum of Arte Útil</em> (useful art) with Tania Bruguera and archival <em>Deviant Practice</em>.<br>
              - ${{formatWInstLink(melly)}} (Rotterdam): Historic public decolonial audit and renaming away from colonial officer Witte de With.
            </p>
          `);
          return;
        }}

        // Research: Landmark Shows
        if (query.includes('landmark') || query.includes('szeemann') || query.includes('when attitudes') || query.includes('documenta')) {{"""

    if target in content:
        content = content.replace(target, dutch_widget_block)
        with open('build_conversational_widget.py', 'w', encoding='utf-8') as f:
            f.write(content)
        print("Updated build_conversational_widget.py!")
    else:
        print("WARNING: target not found in build_conversational_widget.py")

if __name__ == '__main__':
    update_widget_script()
