import re

def update_widget_script():
    with open("build_conversational_widget.py", "r", encoding="utf-8") as f:
        src = f.read()

    # 1. Update Inquiry Carousel in widget
    old_carousel_pattern = r'(<div id="wInquiryCarousel".*?)(<div class="p-2 bg-\[#171717\] shrink-0)'
    new_carousel = """<div id="wInquiryCarousel" class="px-3 py-1.5 border-t border-[#262626] bg-[#171717] flex items-center gap-1.5 overflow-x-auto custom-scroll text-[14px] whitespace-nowrap shrink-0">
        <button class="w-inquiry px-3 py-0.5 rounded-full border border-[#2e2e2e] bg-[#212121] text-[#d4d4d4] hover:bg-[#282828] hover:text-white transition" data-query="Tell me about London's art scene, independent spaces, and divestment history">
          London art scene
        </button>
        <button class="w-inquiry px-3 py-0.5 rounded-full border border-[#2e2e2e] bg-[#212121] text-[#d4d4d4] hover:bg-[#282828] hover:text-white transition" data-query="What is Beyond Objecthood and how did the exhibition become a critical form?">
          Beyond Objecthood
        </button>
        <button class="w-inquiry px-3 py-0.5 rounded-full border border-[#2e2e2e] bg-[#212121] text-[#d4d4d4] hover:bg-[#282828] hover:text-white transition" data-query="What does e-flux say about the museum as a factory and duty-free art?">
          e-flux: Museum as factory
        </button>
        <button class="w-inquiry px-3 py-0.5 rounded-full border border-[#2e2e2e] bg-[#212121] text-[#d4d4d4] hover:bg-[#282828] hover:text-white transition" data-query="Explain the three waves of institutional critique from Hans Haacke to Nan Goldin and Strike MoMA">
          3 Waves of Critique
        </button>
        <button class="w-inquiry px-3 py-0.5 rounded-full border border-[#2e2e2e] bg-[#212121] text-[#d4d4d4] hover:bg-[#282828] hover:text-white transition" data-query="Which cultural spaces offer always free admission?">
          Free admission
        </button>
      </div>\n      """

    src = re.sub(old_carousel_pattern, new_carousel + r'\2', src, flags=re.DOTALL)
    print("Updated carousel in build_conversational_widget.py")

    # 2. Update handleWQuery in build_conversational_widget.py
    old_query_start = src.find("    function handleWQuery(text) {")
    old_query_end = src.find("    function onSend() {", old_query_start)

    if old_query_start != -1 and old_query_end != -1:
        new_wquery = """    function handleWQuery(text) {{
      const query = text.toLowerCase().trim();
      wTyping.classList.remove('hidden');

      setTimeout(() => {{
        wTyping.classList.add('hidden');

        // London Art Scene & Independent Spaces
        if (query.includes('london') && (query.includes('art') || query.includes('scene') || query.includes('space') || query.includes('tell me') || query.includes('more') || query.includes('guide') || query.includes('recommend') || query.includes('culture') || query.includes('critic'))) {{
          const chis = DATA.find(i => i.name.includes('Chisenhale Gallery'));
          const camden = DATA.find(i => i.name.includes('Camden Art Centre'));
          const white = DATA.find(i => i.name.includes('Whitechapel Gallery'));
          const serp = DATA.find(i => i.name.includes('Serpentine Galleries'));
          const volt = DATA.find(i => i.name.includes('Studio Voltaire'));
          const south = DATA.find(i => i.name.includes('South London Gallery'));
          const tate = DATA.find(i => i.name.includes('Tate Modern'));

          appendWCurator(`
            <p class="text-slate-200">
              London's contemporary art landscape is defined by an essential dialectic: on one side stand the corporate-sponsored mega-museums along the Thames, and on the other, a resilient, historically vital constellation of independent kunsthalles, artist-run spaces, and civic commissioning engines.
            </p>
            <p class="text-slate-300">
              For 26 years, British Petroleum (BP) underwrote ${{formatWInstLink(tate)}}, until artist coalitions like <em>BP or not BP?</em>, <em>Liberate Tate</em>, and <em>Culture Unstained</em> waged a 10-year campaign of unsanctioned direct actions—from theatrical die-ins to unleashing pirate wind-turbine blades inside the Turbine Hall—forcing Tate to sever BP ties in 2016. In parallel, Nan Goldin's P.A.I.N. campaigns successfully forced the removal of the Sackler family opioid name across London venues.
            </p>
            <p class="text-slate-300">
              Today, London's critical pulse thrives in independent spaces. In Bow, ${{formatWInstLink(chis)}} occupies a former 1930s veneer factory, internationally celebrated for commissioning early career-defining solo exhibitions by Lubaina Himid and Rachel Whiteread with 100% free admission. In North London, ${{formatWInstLink(camden)}} offers peaceful studio residency gardens dedicated to experimental sculptural inquiry.
            </p>
            <p class="text-slate-300">
              Further shaping the city's critical discourse are ${{formatWInstLink(white)}} in Aldgate (which exhibited Picasso's <em>Guernica</em> in 1939 to support Spanish anti-fascists and hosted the 1956 <em>This Is Tomorrow</em> exhibition), ${{formatWInstLink(serp)}} in Kensington Gardens, ${{formatWInstLink(volt)}} in Clapham, and ${{formatWInstLink(south)}} in Peckham.
            </p>
          `);
          targetRadius = baseRadius * 4.0;
          flyTo(-0.1278, 51.5074);
          return;
        }}

        // Beyond Objecthood: The Exhibition as a Critical Form Since 1968
        if (query.includes('beyond objecthood') || query.includes('voorhies') || (query.includes('objecthood') && (query.includes('fried') || query.includes('art') || query.includes('exhibition'))) || query.includes('exhibition as a critical form') || query.includes('exhibition as form')) {{
          appendWCurator(`
            <p class="text-slate-200">
              In <em>Beyond Objecthood: The Exhibition as a Critical Form Since 1968</em> (MIT Press, 2017), James Voorhies examines how the exhibition itself became the primary artistic medium and a crucial form of political and cultural critique.
            </p>
            <p class="text-slate-300">
              Tracing genealogy to Michael Fried's 1967 essay <em>"Art and Objecthood"</em>—which condemned Minimalist sculpture for 'theatricality' and requiring the temporal duration of the viewer—Voorhies shows how artists from 1968 onward (Robert Smithson, Marcel Broodthaers, Michael Asher, Group Material, Fred Wilson, Maria Eichhorn, Philippe Parreno, Tino Sehgal) turned theatricality into a weapon to dismantle the illusion of the neutral white cube.
            </p>
            <p class="text-slate-300">
              Voorhies exposes how 21st-century mega-museums co-opted participatory and relational forms into corporate entertainment spectacles and tourist branding exercises, arguing that critical agency has migrated to independent kunsthalles and artist-run spaces that refuse to treat visitors as passive consumers.
            </p>
          `);
          return;
        }}

        // e-flux Journal, Hito Steyerl & Boris Groys
        if (query.includes('e-flux') || query.includes('steyerl') || query.includes('groys') || query.includes('vidokle') || query.includes('museum as factory') || query.includes('duty free art') || query.includes('duty-free art') || query.includes('freeport') || query.includes('post-democracy')) {{
          appendWCurator(`
            <p class="text-slate-200">
              Over the past two decades, <em>e-flux journal</em> has served as one of the definitive publishing platforms for radical institutional critique and aesthetic theory.
            </p>
            <p class="text-slate-300">
              In <em>"Is a Museum a Factory?"</em> (2009), <strong>Hito Steyerl</strong> argued that the museum has shifted from a temple of contemplation into a post-Fordist 24/7 factory, where spectators are unpaid affective laborers whose attention generates economic surplus for luxury real estate and trustee portfolios. In <em>"Duty Free Art"</em> (2015), she exposes offshore freeports (Geneva, Luxembourg, Singapore) where blue-chip masterworks sit in climate-controlled storage crates as hyper-liquid, unregulated dark currency.
            </p>
            <p class="text-slate-300">
              Philosopher <strong>Boris Groys</strong> complements this in <em>"Art Workers: Between Utopia and the Archive"</em>, analyzing the public museum's origin in the French Revolution as a secular machine designed to decapitate religious and monarchical icons for universal civic access.
            </p>
          `);
          return;
        }}

        // Three Waves of Institutional Critique
        if (query.includes('institutional critique') || query.includes('haacke') || query.includes('andrea fraser') || query.includes('three waves') || query.includes('3 waves') || query.includes('waves of critique') || query.includes('fred wilson')) {{
          appendWCurator(`
            <p class="text-slate-200">
              Institutional critique has evolved through three transformative historical waves:
            </p>
            <p class="text-slate-300">
              <strong>First Wave (Late 1960s–70s): The Frame and the Board.</strong> Hans Haacke (<em>MoMA Poll</em> 1970; <em>Shapolsky Real Estate</em> 1971 censored by the Guggenheim), Michael Asher, and Daniel Buren dismantled the myth of the neutral, transcendent museum, exposing architectural and board politics.
            </p>
            <p class="text-slate-300">
              <strong>Second Wave (1980s–90s): Complicity and Internalization.</strong> Andrea Fraser (<em>"From the Critique of Institutions to an Institution of Critique"</em>, <em>Museum Highlights</em>, <em>2016 in Museums, Money, and Politics</em>) revealed that there is 'no outside'—we are constituted by institutional desires. Fred Wilson (<em>Mining the Museum</em> 1992) and the Guerrilla Girls confronted systemic erasure.
            </p>
            <p class="text-slate-300">
              <strong>Third Wave (2010s–Present): Direct Divestment.</strong> Nan Goldin's P.A.I.N. forcing the removal of the Sackler opioid name, Decolonize This Place and Strike MoMA confronting board members over vulture funds and weapons manufacturing, and the 2019 Whitney Biennial tear gas boycott forcing Warren Kanders out.
            </p>
          `);
          return;
        }}

        // Visitor Queries: Hours & Monday Openings
        if (query.includes('hour') || query.includes('schedule') || (query.includes('time') && query.includes('open')) || query.includes('monday')) {{
          const mondaySpaces = DATA.filter(i => !i.opening_hours.toLowerCase().includes('closed mon') && (i.opening_hours.toLowerCase().includes('daily') || i.opening_hours.toLowerCase().includes('mon')));
          const m1 = mondaySpaces[0] || DATA.find(i => i.name.includes('Palais de Tokyo'));
          const m2 = mondaySpaces[1] || DATA.find(i => i.name.includes('Louisiana'));
          appendWCurator(`
            <p class="text-slate-200">
              Culture Atlas tracks <strong>${{mondaySpaces.length}}</strong> ethical cultural sanctuaries open on Mondays for quiet reflection.
            </p>
            <p class="text-slate-300">
              In Paris, ${{formatWInstLink(m1)}} stays open until midnight. Along the Danish coastline, ${{formatWInstLink(m2)}} is open daily.
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
        }} else {{
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
            targetRadius = baseRadius * 4.0;
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
    }}
\n"""
        src = src[:old_query_start] + new_wquery + src[old_query_end:]
        print("Updated handleWQuery in build_conversational_widget.py")

    with open("build_conversational_widget.py", "w", encoding="utf-8") as f:
        f.write(src)
    print("Saved build_conversational_widget.py!")

if __name__ == "__main__":
    update_widget_script()
