import re

def update_atlas():
    with open("build_conversational_atlas.py", "r", encoding="utf-8") as f:
        src = f.read()

    # 1. Update the state initialization (around line 1541)
    old_state = """    let geminiApiKey = localStorage.getItem('atlas_gemini_api_key') || '';
    let geminiModel = 'gemini-2.5-flash';"""

    new_state = """    // Unified Multi-Provider AI State & Local Storage
    let aiApiKey = localStorage.getItem('atlas_ai_api_key') || localStorage.getItem('atlas_gemini_api_key') || '';
    let aiProvider = localStorage.getItem('atlas_ai_provider') || 'auto';
    let aiModel = localStorage.getItem('atlas_ai_model') || '';

    function detectProvider(key) {{
      if (!key) return null;
      const k = key.trim();
      if (k.startsWith('sk-ant-')) return 'anthropic';
      if (k.startsWith('AIza')) return 'gemini';
      if (k.startsWith('sk-') || k.startsWith('sk-proj-')) return 'openai';
      return 'anthropic';
    }}

    function getEffectiveProvider() {{
      if (aiProvider && aiProvider !== 'auto') return aiProvider;
      return detectProvider(aiApiKey) || 'anthropic';
    }}

    function getEffectiveModel() {{
      if (aiModel) return aiModel;
      const p = getEffectiveProvider();
      if (p === 'anthropic') return 'claude-haiku-4-5-20251001';
      if (p === 'openai') return 'gpt-4o-mini';
      if (p === 'gemini') return 'gemini-2.5-flash';
      return 'claude-haiku-4-5-20251001';
    }}

    function updateAIStatusUI() {{
      const dot = document.getElementById('curatorStatusDot');
      const label = document.getElementById('curatorStatusLabel');
      if (!dot || !label) return;
      if (aiApiKey) {{
        const prov = getEffectiveProvider();
        const pName = prov === 'anthropic' ? 'Claude' : (prov === 'openai' ? 'OpenAI' : 'Gemini');
        dot.className = 'w-2 h-2 rounded-full bg-emerald-400 animate-pulse';
        label.textContent = `${{pName}} Live`;
        label.className = 'hidden sm:inline font-mono text-[14px] text-emerald-400';
      }} else {{
        dot.className = 'w-2 h-2 rounded-full bg-amber-400';
        label.textContent = 'Critical Engine';
        label.className = 'hidden sm:inline font-mono text-[14px] text-[#a1a1aa]';
      }}
    }}"""

    if old_state in src:
        src = src.replace(old_state, new_state, 1)
        print("Replaced state initialization")
    else:
        print("Warning: old_state not found!")

    # 2. Replace queryGemini with queryAI and testAPIConnection (around line 1651)
    old_query_start = src.find("async function queryGemini(userPrompt)")
    old_query_end = src.find("    // Extract unique cities list for instant recognition", old_query_start)

    if old_query_start != -1 and old_query_end != -1:
        new_ai_query = """    // Unified Multi-Provider Live Generative AI Engine (Claude, OpenAI, Gemini)
    async function queryAI(userPrompt) {{
      if (!aiApiKey) return null;
      const prov = getEffectiveProvider();
      const model = getEffectiveModel();

      // Sample representative sanctuaries for model grounding
      const sampleInsts = ALL_INSTITUTIONS.slice(0, 45).map(i => `${{i.name}} (${{i.city}}, ${{i.country}}): Tier ${{i.tier}}, ${{i.governance_type}}, Hours: ${{i.opening_hours}}, ${{i.admission_policy}}, Highlights: ${{i.highlight}}`).join('\\n');

      const criticalSystemPrompt = `You are the Culture Atlas Curator, an erudite, warm, and articulate contemporary art scholar and guide to ethical cultural institutions worldwide.
Culture Atlas maps 203 cultural sanctuaries across 35 countries that protect curatorial independence and reject underwriting from fossil fuels, defense/weapons manufacturing, and private prisons.

DEEP THEORETICAL & INSTITUTIONAL FOUNDATIONS:
You are deeply grounded in institutional critique, contemporary art theory, and critical exhibition history:
- 'Beyond Objecthood: The Exhibition as a Critical Form Since 1968' by James Voorhies (MIT Press, 2017): You trace how artists from 1968 onwards (Robert Smithson, Marcel Broodthaers, Michael Asher, Group Material, Fred Wilson, Maria Eichhorn, Philippe Parreno, Tino Sehgal) subverted Michael Fried's 1967 condemnation of 'theatricality' in 'Art and Objecthood', transforming the exhibition itself into the primary artistic medium and critical form. You understand the contemporary paradox: how corporate mega-museums co-opted participatory and relational practices into tourist entertainment spectacle, and why independent kunsthalles and artist-run spaces remain essential counter-publics.
- 'e-flux journal' Critical Theory:
  * Hito Steyerl: 'Is a Museum a Factory?' (the museum as a post-Fordist site of unpaid spectator labor), 'Politics of Art: Contemporary Art and the Transition to Post-Democracy', and 'Duty Free Art' (freeports in Geneva and Singapore as offshore tax shelters where art circulates as financialized speculative currency).
  * Boris Groys: 'Art Workers: Between Utopia and the Archive', 'The Museum as a Cradle of Revolution', and the museum's role as a secular egalitarian archive preserving artworks beyond capitalist market obsolescence.
  * Anton Vidokle & Julieta Aranda: 'Art Without Artists?' (critique of the sovereign super-curator displacing the artist) and Russian Cosmism.
  * Martha Rosler: 'Culture Class: Art, Creativity, Urbanism' (gentrification and artists as the advance guard of real estate capital).
- Three Waves of Institutional Critique:
  * 1st Wave (Late 1960s–70s): Hans Haacke (MoMA Poll 1970; Shapolsky real estate censorship at the Guggenheim 1971), Michael Asher, Daniel Buren, Marcel Broodthaers.
  * 2nd Wave (1980s–90s): Andrea Fraser ('From the Critique of Institutions to an Institution of Critique', '2016 in Museums, Money, and Politics'), Fred Wilson ('Mining the Museum' 1992), Guerrilla Girls.
  * 3rd Wave / Activist Divestment (2010s–Present): Decolonize This Place, Strike MoMA (Leon Black, Larry Fink, Steven Tananbaum, Paula Crown), Nan Goldin & P.A.I.N. (stripping the Sackler name from the Met, Louvre, Guggenheim, Tate, Serpentine), BP or not BP? & Culture Unstained (ousting BP from Tate and National Portrait Gallery), Warren Kanders Whitney Biennial tear gas boycott.
- Claire Bishop: 'Radical Museology' (dialectical collection display vs presentist corporate spectacle; Van Abbemuseum, Reina Sofía) and 'Artificial Hells'.
- Pamela M. Lee: 'Forgetting the Art World' (globalization and logistical capitalism).

CRITICAL FORMATTING & CONVERSATIONAL RULES:
1. Write in warm, articulate, continuous conversational paragraphs. DO NOT produce bulleted lists, numbered items, tables, or generic boxed UI recommendation containers.
2. Weave all institutional and city references strictly IN LINE within your natural sentences.
3. When referencing an institution in our atlas, format it strictly as:
<a href="#" class="inst-link font-semibold text-white hover:text-[#60a5fa] underline cursor-pointer" data-name="Exact Name">Exact Name</a> in <a href="#" class="city-link text-[#93c5fd] hover:underline cursor-pointer" data-city="City">City</a> (<a href="#" class="dossier-link text-slate-400 hover:text-white underline font-mono text-[14px] cursor-pointer" data-name="Exact Name">audit dossier</a>)
4. When mentioning a city, link it as: <a href="#" class="city-link text-[#93c5fd] hover:underline cursor-pointer" data-city="City">City</a>.
5. If the user asks about an art scene (e.g. London, New York, Berlin, Paris), provide an intellectual, historical, and curatorial narrative exploring its critical tensions, funding governance (e.g. Arts Council England, DRAC), and highlight specific independent sanctuaries from our atlas.
6. Never output markdown headers (#, ##) or structured database field labels like 'Address:', 'Hours:', 'Highlight:'. Speak in fluid, natural prose as an inspiring curator and theorist.`;

      try {{
        let rawText = '';
        if (prov === 'anthropic') {{
          const res = await fetch('https://api.anthropic.com/v1/messages', {{
            method: 'POST',
            headers: {{
              'Content-Type': 'application/json',
              'x-api-key': aiApiKey,
              'anthropic-version': '2023-06-01',
              'anthropic-dangerous-direct-browser-access': 'true'
            }},
            body: JSON.stringify({{
              model: model,
              max_tokens: 1024,
              system: criticalSystemPrompt,
              messages: [
                {{ role: 'user', content: `Atlas sample:\\n${{sampleInsts}}\\n\\nUser question: ${{userPrompt}}` }}
              ]
            }})
          }});
          if (!res.ok) throw new Error(`Anthropic error ${{res.status}}`);
          const data = await res.json();
          rawText = data.content?.[0]?.text || '';
        }} else if (prov === 'openai') {{
          const res = await fetch('https://api.openai.com/v1/chat/completions', {{
            method: 'POST',
            headers: {{
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${{aiApiKey}}`
            }},
            body: JSON.stringify({{
              model: model,
              temperature: 0.7,
              max_tokens: 1024,
              messages: [
                {{ role: 'system', content: `${{criticalSystemPrompt}}\\n\\nInstitutions sample:\\n${{sampleInsts}}` }},
                {{ role: 'user', content: userPrompt }}
              ]
            }})
          }});
          if (!res.ok) throw new Error(`OpenAI error ${{res.status}}`);
          const data = await res.json();
          rawText = data.choices?.[0]?.message?.content || '';
        }} else {{
          // Google Gemini
          const res = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/${{model}}:generateContent?key=${{aiApiKey}}`, {{
            method: 'POST',
            headers: {{ 'Content-Type': 'application/json' }},
            body: JSON.stringify({{
              contents: [
                {{ role: 'user', parts: [{{ text: `${{criticalSystemPrompt}}\\n\\nInstitutions sample:\\n${{sampleInsts}}\\n\\nUser question: ${{userPrompt}}` }}] }}
              ],
              generationConfig: {{
                temperature: 0.7,
                maxOutputTokens: 1024
              }}
            }})
          }});
          if (!res.ok) throw new Error(`Gemini error ${{res.status}}`);
          const data = await res.json();
          rawText = data.candidates?.[0]?.content?.parts?.[0]?.text || '';
        }}

        if (rawText) {{
          return rawText.split(/\\n\\s*\\n/).filter(p => p.trim()).map(p => `<p class="text-slate-200 leading-relaxed">${{p.trim()}}</p>`).join('');
        }}
      }} catch (err) {{
        console.warn('Live AI query error, falling back to offline knowledge engine:', err);
      }}
      return null;
    }}

    async function testAPIConnection(prov, key, model) {{
      if (!key) return {{ success: false, error: 'Please enter an API key' }};
      try {{
        if (prov === 'anthropic') {{
          const res = await fetch('https://api.anthropic.com/v1/messages', {{
            method: 'POST',
            headers: {{
              'Content-Type': 'application/json',
              'x-api-key': key,
              'anthropic-version': '2023-06-01',
              'anthropic-dangerous-direct-browser-access': 'true'
            }},
            body: JSON.stringify({{
              model: model || 'claude-haiku-4-5-20251001',
              max_tokens: 10,
              messages: [{{ role: 'user', content: 'Respond with OK' }}]
            }})
          }});
          if (!res.ok) {{
            const err = await res.json().catch(() => ({{}}));
            return {{ success: false, error: err.error?.message || `HTTP ${{res.status}}` }};
          }}
          return {{ success: true, message: 'Connected to Claude successfully!' }};
        }} else if (prov === 'openai') {{
          const res = await fetch('https://api.openai.com/v1/chat/completions', {{
            method: 'POST',
            headers: {{ 'Content-Type': 'application/json', 'Authorization': `Bearer ${{key}}` }},
            body: JSON.stringify({{
              model: model || 'gpt-4o-mini',
              max_tokens: 10,
              messages: [{{ role: 'user', content: 'Respond with OK' }}]
            }})
          }});
          if (!res.ok) {{
            const err = await res.json().catch(() => ({{}}));
            return {{ success: false, error: err.error?.message || `HTTP ${{res.status}}` }};
          }}
          return {{ success: true, message: 'Connected to OpenAI successfully!' }};
        }} else {{
          const m = model || 'gemini-2.5-flash';
          const res = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/${{m}}:generateContent?key=${{key}}`, {{
            method: 'POST',
            headers: {{ 'Content-Type': 'application/json' }},
            body: JSON.stringify({{ contents: [{{ role: 'user', parts: [{{ text: 'OK' }}] }}] }})
          }});
          if (!res.ok) {{
            const err = await res.json().catch(() => ({{}}));
            return {{ success: false, error: err.error?.message || `HTTP ${{res.status}}` }};
          }}
          return {{ success: true, message: 'Connected to Gemini successfully!' }};
        }}
      }} catch (e) {{
        return {{ success: false, error: e.message || 'Network request failed' }};
      }}
    }}
\n"""
        src = src[:old_query_start] + new_ai_query + src[old_query_end:]
        print("Replaced queryGemini with queryAI and testAPIConnection")
    else:
        print("Warning: old queryGemini boundaries not found!")

    # 3. Replace handleCuratorQuery with comprehensive Critical Knowledge Engine
    old_handle_start = src.find("    // Intelligent Conversational Curator Knowledge Engine\n    async function handleCuratorQuery(query) {")
    old_handle_end = src.find("    // Handle Input Send\n    function handleSend() {", old_handle_start)

    if old_handle_start != -1 and old_handle_end != -1:
        new_handle = """    // Intelligent Conversational Curator Knowledge Engine
    async function handleCuratorQuery(query) {{
      const q = query.toLowerCase().trim();
      const rawTrimmed = query.trim();

      // A. Seamless API Key Detection from Chat Input
      if (/^(sk-ant-[a-zA-Z0-9_\\-]+|AIza[a-zA-Z0-9_\\-]+|sk-[a-zA-Z0-9_\\-]+)$/.test(rawTrimmed) || rawTrimmed.startsWith('/key ')) {{
        const key = rawTrimmed.replace(/^\\/key\\s*/, '').trim();
        const prov = detectProvider(key);
        const pName = prov === 'anthropic' ? 'Anthropic Claude' : (prov === 'openai' ? 'OpenAI' : 'Google Gemini');
        aiApiKey = key;
        aiProvider = prov;
        aiModel = getEffectiveModel();
        localStorage.setItem('atlas_ai_api_key', key);
        localStorage.setItem('atlas_ai_provider', prov);
        localStorage.setItem('atlas_ai_model', aiModel);
        updateAIStatusUI();
        appendCuratorMessage(`
          <p class="text-emerald-400 font-semibold">
            ✓ ${{pName}} API Key detected and securely saved to your browser!
          </p>
          <p class="text-slate-200">
            Live intelligence is now active with <strong>${{aiModel}}</strong>. Ask me anything about art history, exhibition genealogies from <em>Beyond Objecthood</em>, e-flux institutional critique, or our 203 ethical sanctuaries.
          </p>
        `);
        return;
      }}

      curatorTyping.classList.remove('hidden');

      // Proactively zoom into any mentioned location or city immediately
      const earlyInst = findMentionedInst(query);
      const earlyCity = findMentionedCity(query);
      if (earlyInst) {{
        selectInstitution(earlyInst, true);
      }} else if (earlyCity) {{
        filterByCity(earlyCity, true, false);
      }}

      // 1. Try Live Generative AI Model if API Key is configured
      if (aiApiKey) {{
        const aiHtml = await queryAI(query);
        if (aiHtml) {{
          curatorTyping.classList.add('hidden');
          appendCuratorMessage(aiHtml);
          return;
        }}
      }}

      // 2. Intelligent Offline Conversational Critical Engine (Always Active)
      setTimeout(() => {{
        curatorTyping.classList.add('hidden');

        // =========================================================================
        // 🏛️ CRITICAL THEORY & ART SCENE SPECIALIST HANDLERS
        // =========================================================================

        // 1. London Art Scene & Independent Spaces
        if (q.includes('london') && (q.includes('art') || q.includes('scene') || q.includes('space') || q.includes('tell me') || q.includes('more') || q.includes('guide') || q.includes('recommend') || q.includes('culture') || q.includes('critic'))) {{
          const chis = ALL_INSTITUTIONS.find(i => i.name.includes('Chisenhale Gallery'));
          const camden = ALL_INSTITUTIONS.find(i => i.name.includes('Camden Art Centre'));
          const white = ALL_INSTITUTIONS.find(i => i.name.includes('Whitechapel Gallery'));
          const serp = ALL_INSTITUTIONS.find(i => i.name.includes('Serpentine Galleries'));
          const volt = ALL_INSTITUTIONS.find(i => i.name.includes('Studio Voltaire'));
          const south = ALL_INSTITUTIONS.find(i => i.name.includes('South London Gallery'));
          const gas = ALL_INSTITUTIONS.find(i => i.name.includes('Gasworks'));
          const tate = ALL_INSTITUTIONS.find(i => i.name.includes('Tate Modern'));

          appendCuratorMessage(`
            <p class="text-slate-200">
              London's contemporary art landscape is defined by a profound institutional dialectic: on one side stand the high-profile corporate mega-museums along the Thames, and on the other, a resilient, historically vital constellation of independent kunsthalles, artist-run spaces, and civic commissioning engines.
            </p>
            <p class="text-slate-300">
              This ecosystem was forged through intense cultural struggle. For 26 years, British Petroleum (BP) underwrote ${{formatInstLink(tate)}}, until artist coalitions like <em>BP or not BP?</em>, <em>Liberate Tate</em>, and <em>Culture Unstained</em> led a decade of unsanctioned direct actions—from theatrical die-ins to installing a 1.5-tonne pirate wind-turbine blade inside the Turbine Hall—forcing Tate to sever BP sponsorship in 2016. In parallel, Nan Goldin's P.A.I.N. campaigns successfully pressured institutions across London to strip the Sackler family opioid name from their wings.
            </p>
            <p class="text-slate-300">
              Today, the true intellectual pulse of London thrives in spaces where curatorial autonomy is paramount. In East London's Bow, ${{formatInstLink(chis)}} occupies a former 1930s veneer factory, celebrated worldwide for commissioning pivotal early career-defining solo exhibitions by Lubaina Himid, Rachel Whiteread, and Lynette Yiadom-Boakye with 100% free public admission. In North London, ${{formatInstLink(camden)}} offers peaceful studio residency gardens dedicated to experimental sculptural and ceramic inquiry away from market speculation.
            </p>
            <p class="text-slate-300">
              Further shaping the city's critical discourse are ${{formatInstLink(white)}} in Aldgate, with over a century of radical civic heritage (famously exhibiting Picasso's <em>Guernica</em> in 1939 to rally support for the Spanish Republic and hosting the seminal 1956 <em>This Is Tomorrow</em> exhibition), ${{formatInstLink(serp)}} in Kensington Gardens, ${{formatInstLink(volt)}} in Clapham supporting non-profit artist studios and queer practices, ${{formatInstLink(south)}} in Peckham, and ${{formatInstLink(gas)}} in Vauxhall. Each operates under ethical public charters free from fossil-fuel and defense underwriting.
            </p>
          `);
          filterByCity('London', true, false);
          return;
        }}

        // 2. Beyond Objecthood: The Exhibition as a Critical Form Since 1968
        if (q.includes('beyond objecthood') || q.includes('voorhies') || (q.includes('objecthood') && (q.includes('fried') || q.includes('art') || q.includes('exhibition'))) || q.includes('exhibition as a critical form') || q.includes('exhibition as form')) {{
          appendCuratorMessage(`
            <p class="text-slate-200">
              In <em>Beyond Objecthood: The Exhibition as a Critical Form Since 1968</em> (MIT Press, 2017), curator and art historian James Voorhies examines how the exhibition itself became the primary artistic medium and a crucial form of political and cultural critique.
            </p>
            <p class="text-slate-300">
              The genealogy begins with Michael Fried's notorious 1967 polemic <em>"Art and Objecthood"</em>. Fried fiercely defended modernist autonomy (Clement Greenberg, Frank Stella, Anthony Caro) and attacked Minimalist sculpture (Donald Judd, Robert Morris, Tony Smith) for what he condemned as <strong>'theatricality'</strong>—the fact that Minimalist objects require the temporal, bodily presence of the viewer in a room over time, reducing art to an open-ended 'situation'. For Fried, genuine art was instantaneous and transcendent: <em>'presentness is grace.'</em>
            </p>
            <p class="text-slate-300">
              Voorhies demonstrates how, starting in 1968, artists turned Fried's critique into a radical weapon. Figures from Robert Smithson (with his earthwork non-sites) and Marcel Broodthaers (fictional museum departments) to Michael Asher, Group Material, Fred Wilson, Maria Eichhorn, Philippe Parreno, and Tino Sehgal radically embraced theatricality, temporal duration, and spectator involvement. By transforming the exhibition into a critical form, they shattered the illusion of the neutral 'white cube' and exposed how museums construct ideology, race, and capital.
            </p>
            <p class="text-slate-300">
              Crucially, Voorhies exposes a 21st-century museological paradox: the participatory, dematerialized practices conceived in the 1960s–90s to escape commodification were later co-opted by corporate mega-museums (Tate Modern Turbine Hall, MoMA, Guggenheim) into tourist spectacle, selfie architecture, and corporate entertainment branding. To resist this absorption, Voorhies argues that critical agency has migrated to independent kunsthalles, artist-run spaces, and discursive public platforms that refuse to reduce viewers to passive consumers.
            </p>
          `);
          return;
        }}

        // 3. e-flux Journal, Hito Steyerl & Boris Groys
        if (q.includes('e-flux') || q.includes('steyerl') || q.includes('groys') || q.includes('vidokle') || q.includes('museum as factory') || q.includes('duty free art') || q.includes('duty-free art') || q.includes('freeport') || q.includes('post-democracy')) {{
          appendCuratorMessage(`
            <p class="text-slate-200">
              Over the past two decades, <em>e-flux journal</em> (founded by Anton Vidokle, Julieta Aranda, and Brian Kuan Wood) has served as one of the definitive publishing platforms for radical institutional critique and aesthetic theory.
            </p>
            <p class="text-slate-300">
              Central to this discourse is <strong>Hito Steyerl</strong>, whose seminal essay <em>"Is a Museum a Factory?"</em> (2009) redefined how we analyze cultural space. Steyerl argues that the museum has shifted from a bourgeois temple of aesthetic contemplation or historical archive into a post-Fordist 24/7 factory. Within this space, museum visitors are not passive spectators, but unpaid affective laborers whose attention, social media circulation, and cultural capital generate economic surplus for surrounding luxury real estate and trustee investment portfolios.
            </p>
            <p class="text-slate-300">
              In <em>"Duty Free Art: Art in the Age of Planetary Civil War"</em> (2015), Steyerl exposes the phenomenon of offshore freeports (such as Geneva, Singapore, and Luxembourg)—giant tax-exempt transit warehouses where blue-chip masterpieces sit inside climate-controlled crates, traded via offshore bearer shares as speculative hedges without ever being seen by the public. Art loses its public objecthood, functioning purely as hyper-liquid, unregulated dark currency.
            </p>
            <p class="text-slate-300">
              Philosopher <strong>Boris Groys</strong> complements this with texts like <em>"Art Workers: Between Utopia and the Archive"</em> and <em>"The Museum as a Cradle of Revolution"</em>, tracing the public museum's origin to the French Revolution as a secular machine designed to decapitate religious and monarchical icons, converting them into historical artifacts for universal civic access. Alongside Anton Vidokle's critique in <em>"Art Without Artists?"</em> (confronting the rise of the celebrity curator), e-flux provides the essential theoretical vocabulary to demystify how contemporary art is instrumentalized by global financialization.
            </p>
          `);
          return;
        }}

        // 4. Three Waves of Institutional Critique
        if (q.includes('institutional critique') || q.includes('haacke') || q.includes('andrea fraser') || q.includes('three waves') || q.includes('3 waves') || q.includes('waves of critique') || q.includes('fred wilson')) {{
          appendCuratorMessage(`
            <p class="text-slate-200">
              Institutional critique has evolved through three distinct, transformative historical waves:
            </p>
            <p class="text-slate-300">
              <strong>First Wave (Late 1960s–1970s): The Frame and the Board.</strong> Initiated by artists like Hans Haacke, Michael Asher, Daniel Buren, and Marcel Broodthaers, the first wave sought to dismantle the myth of the museum as a neutral, transcendent temple of aesthetic autonomy. Haacke's <em>MoMA Poll</em> (1970) directly interrogated visitor attitudes toward board chairman Nelson Rockefeller's support for the Nixon administration's Indochina policy, while his 1971 work <em>Shapolsky et al. Manhattan Real Estate Holdings</em> exposed the predatory slumlord holdings of a Guggenheim trustee, leading director Thomas Messer to censor and cancel the exhibition.
            </p>
            <p class="text-slate-300">
              <strong>Second Wave (1980s–1990s): Complicity and Internalization.</strong> Theorized decisively by Andrea Fraser in her 2005 landmark essay <em>"From the Critique of Institutions to an Institution of Critique"</em>, second-wave practitioners realized there is 'no outside' to the institution. Artists, critics, and viewers are themselves constituted by the cultural capital, prestige, and psychological desires of the museum system. Fraser's performances (like docent Jane Castleton in <em>Museum Highlights</em>, 1989) and her 900-page forensic study <em>2016 in Museums, Money, and Politics</em> dissected board political donations, while Fred Wilson's <em>Mining the Museum</em> (1992) and the Guerrilla Girls confronted systemic racial and gender bias.
            </p>
            <p class="text-slate-300">
              <strong>Third Wave / Direct Divestment (2010s–Present): Activist Decoupling.</strong> The contemporary phase has moved from symbolic gallery interventions to collective, direct-action divestment campaigns. Nan Goldin's P.A.I.N. organized die-ins inside the Met, Guggenheim, and Louvre, forcing major museums worldwide to strip the Sackler opioid family name. Coalitions like <em>Decolonize This Place</em> and <em>Strike MoMA</em> targeted trustees tied to vulture funds, private prisons, and border militarization, while the 2019 Whitney Biennial artist boycott forced the resignation of Safariland tear gas manufacturer Warren Kanders.
            </p>
          `);
          return;
        }}

        // 5. Claire Bishop & Radical Museology
        if (q.includes('claire bishop') || q.includes('radical museology') || q.includes('artificial hells') || q.includes('relational aesthetics') || q.includes('bourriaud')) {{
          appendCuratorMessage(`
            <p class="text-slate-200">
              Art historian and theorist Claire Bishop has provided some of the most incisive critiques of contemporary exhibition-making and curatorial practice.
            </p>
            <p class="text-slate-300">
              In <em>Radical Museology: Or, What's Contemporary in Museums of Contemporary Art?</em> (2013), Bishop contrasts two opposing institutional models: the <strong>'presentist' corporate mega-museum</strong> (which prioritizes sensationalist architectural spectacles, transient blockbuster exhibitions, and consumer footfall to drive retail revenue) versus <strong>dialectical, historical museums</strong> (such as the Van Abbemuseum in Eindhoven under Charles Esche, Reina Sofía in Madrid under Manuel Borja-Villel, and MSUM in Ljubljana under Zdenka Badovinac). These radical institutions mobilize their permanent collections not as decorative luxury assets, but as critical historical weapons to interrogate current political crises.
            </p>
            <p class="text-slate-300">
              In <em>Artificial Hells: Participatory Art and the Politics of Spectatorship</em> (Verso, 2012), Bishop took aim at the uncritical embrace of 'relational aesthetics' (theorized by Nicolas Bourriaud). She argued that reducing art to friendly, convivial social gatherings often serves as an easy palliative, simulating community while dodging difficult artistic antagonisms, aesthetic criteria, and structural political critique.
            </p>
          `);
          return;
        }}

        // 6. Minimalism, Dia Beacon & Phenomenology
        if (q.includes('minimalism') || q.includes('dia beacon') || q.includes('judds') || q.includes('judd') || q.includes('richard serra') || q.includes('phenomenolog')) {{
          const dia = ALL_INSTITUTIONS.find(i => i.name.includes('Dia Beacon'));
          appendCuratorMessage(`
            <p class="text-slate-200">
              Minimalism in the 1960s represented a fundamental philosophical rupture: artists like Donald Judd, Dan Flavin, Robert Morris, and Richard Serra rejected metaphorical representation and expressive illusion, insisting instead on 'specific objects' and direct phenomenological encounter.
            </p>
            <p class="text-slate-300">
              No institution embodies this ethos more powerfully than ${{formatInstLink(dia)}} in the Hudson Valley. Housed in a vast 1929 former Nabisco box-printing facility on the Hudson River, Dia Beacon provides nearly 300,000 square feet illuminated entirely by northern daylight through sawtooth skylights. Here, Donald Judd's plywood boxes, Richard Serra's monumental weathered steel <em>Torqued Ellipses</em>, and Michael Heizer's sunken negative voids <em>North, East, South, West</em> exist at architectural scale, fulfilling the Minimalist demand that art be experienced physically in real space and real time.
            </p>
            <p class="text-slate-300">
              Founded by Philippa de Menil, Heiner Friedrich, and Helen Winkler in 1974, the Dia Art Foundation operates with a visionary endowment model that commits to sustaining singular, in-depth artistic installations indefinitely, completely free from the churn of commercial art fairs.
            </p>
          `);
          selectInstitution(dia, true);
          return;
        }}

        // 7. New York Art Scene & Board Politics
        if (q.includes('new york') || q.includes('nyc') || q.includes('manhattan')) {{
          const dia = ALL_INSTITUTIONS.find(i => i.name.includes('Dia Beacon'));
          const sculp = ALL_INSTITUTIONS.find(i => i.name.includes('SculptureCenter'));
          const artsp = ALL_INSTITUTIONS.find(i => i.name.includes('Artists Space'));
          const kitch = ALL_INSTITUTIONS.find(i => i.name.includes('The Kitchen'));
          const swiss = ALL_INSTITUTIONS.find(i => i.name.includes('Swiss Institute'));
          const moma = ALL_INSTITUTIONS.find(i => i.name === 'MoMA (The Museum of Modern Art)');

          appendCuratorMessage(`
            <p class="text-slate-200">
              New York City presents the starkest clash in the global art world between private financial oligarchies and courageous grassroots artistic resistance.
            </p>
            <p class="text-slate-300">
              Major institutions like ${{formatInstLink(moma)}} and the Whitney Museum have been centers of intense community mobilization. MoMA sparked 10 weeks of protests by the <em>Strike MoMA</em> coalition over board members tied to vulture funds, private prisons, and defense contractors, leading former chairman Leon Black to step down over $158 million in payments to Jeffrey Epstein. At the Whitney, an artist boycott forced the resignation of Safariland tear gas CEO Warren Kanders.
            </p>
            <p class="text-slate-300">
              Culture Atlas highlights New York's uncompromised, artist-centered alternatives. In Tribeca, ${{formatInstLink(artsp)}} has championed radical discourse since 1972 (giving early platforms to Cindy Sherman and Barbara Kruger and hosting Decolonize This Place assemblies). In Queens, ${{formatInstLink(sculp)}} champions experimental non-commercial sculpture in a historic trolley repair shop. And in the Hudson Valley, ${{formatInstLink(dia)}} remains the world's preeminent monument to Minimalist integrity.
            </p>
          `);
          filterByCity('New York', true, false);
          return;
        }}

        // 8. Paris Art Scene & Civic Models
        if (q.includes('paris')) {{
          const ptok = ALL_INSTITUTIONS.find(i => i.name.includes('Palais de Tokyo'));
          const pomp = ALL_INSTITUTIONS.find(i => i.name.includes('Pompidou'));
          const cart = ALL_INSTITUTIONS.find(i => i.name.includes('Fondation Cartier'));

          appendCuratorMessage(`
            <p class="text-slate-200">
              Paris's contemporary art scene is shaped by a distinct balance between state-subsidized civic kunsthalles and the growing footprint of private luxury foundation museums.
            </p>
            <p class="text-slate-300">
              France's model of public funding through the Ministry of Culture and regional DRAC bodies guarantees public access and shields institutions from corporate board capture. A premier example is ${{formatInstLink(ptok)}}, Europe's largest contemporary art center, operating as a dynamic, anti-monumental laboratory open until midnight. In the heart of the city, ${{formatInstLink(pomp)}} stands as an iconic monument to democratic cultural decentralization, designed by Renzo Piano and Richard Rogers.
            </p>
            <p class="text-slate-300">
              While private foundations like ${{formatInstLink(cart)}} present architecturally ambitious commissions, public discourse in Paris remains acutely engaged with debates on postcolonial provenance, restitution, and defending public cultural subsidies against commercialization.
            </p>
          `);
          filterByCity('Paris', true, false);
          return;
        }}

        // 9. Berlin Art Scene & Independent Spaces
        if (q.includes('berlin')) {{
          const kw = ALL_INSTITUTIONS.find(i => i.name.includes('KW Institute'));
          const hkw = ALL_INSTITUTIONS.find(i => i.name.includes('Haus der Kulturen'));
          const grop = ALL_INSTITUTIONS.find(i => i.name.includes('Gropius Bau'));

          appendCuratorMessage(`
            <p class="text-slate-200">
              Berlin's cultural ecosystem owes its worldwide reputation to its post-1989 history of artist self-organization, independent project spaces (<em>Freie Szene</em>), and robust federal arts funding that prioritizes experimental discourse over commercial market speculation.
            </p>
            <p class="text-slate-300">
              In Mitte, ${{formatInstLink(kw)}} occupies a former 19th-century margarine factory, serving as a pioneer of uncompromised curatorial experimentation and home of the Berlin Biennale. In Tiergarten, ${{formatInstLink(hkw)}} serves as an internationally renowned forum for postcolonial discourse, planetary anthropocene research, and non-Western epistemologies. At the former border, ${{formatInstLink(grop)}} stages major interdisciplinary encounters with free access to its iconic ground floor.
            </p>
            <p class="text-slate-300">
              Despite intensifying real estate gentrification pressures, Berlin remains one of the world's most intellectually rigorous artistic capitals, where artists actively mobilize for wage equity, studio preservation, and independent governance.
            </p>
          `);
          filterByCity('Berlin', true, false);
          return;
        }}

        // =========================================================================
        // 🏛️ VISITOR DATA & AUDIT HANDLERS
        // =========================================================================

        // A. Visitor Data: Hours & Monday Openings
        if (q.includes('hour') || q.includes('schedule') || (q.includes('time') && (q.includes('open') || q.includes('visit'))) || q.includes('monday') || q.includes('weekend') || q.includes('late night') || q.includes('closed')) {{
          const targetInst = ALL_INSTITUTIONS.find(i => q.includes(i.name.toLowerCase()) || (i.aliases && i.aliases.some(a => q.includes(a.toLowerCase()))));
          if (targetInst) {{
            appendCuratorMessage(`
              <p class="text-slate-200">
                If you are planning a visit to ${{formatInstLink(targetInst)}}, it welcomes the public <strong>${{targetInst.opening_hours}}</strong>.
              </p>
              <p class="text-slate-300">
                You will find it at <strong>${{targetInst.address}}</strong> in the ${{targetInst.neighborhood}} neighborhood, conveniently reached via ${{targetInst.transit_tips}}. I recommend setting aside roughly <strong>${{targetInst.visit_duration}}</strong> to immerse yourself in the exhibitions and its signature landmark: ${{targetInst.highlight}}.
              </p>
            `);
            selectInstitution(targetInst, true);
            return;
          }}

          if (q.includes('monday')) {{
            const mondaySpaces = ALL_INSTITUTIONS.filter(i => !i.opening_hours.toLowerCase().includes('closed mon') && (i.opening_hours.toLowerCase().includes('daily') || i.opening_hours.toLowerCase().includes('mon,') || i.opening_hours.toLowerCase().includes('mon–') || i.opening_hours.toLowerCase().includes('mon-')));
            const m1 = mondaySpaces[0] || ALL_INSTITUTIONS.find(i => i.name.includes('Palais de Tokyo'));
            const m2 = mondaySpaces[1] || ALL_INSTITUTIONS.find(i => i.name.includes('Louisiana'));
            const m3 = mondaySpaces[2] || ALL_INSTITUTIONS.find(i => i.name.includes('Chisenhale'));
            appendCuratorMessage(`
              <p class="text-slate-200">
                While most conventional museums shutter their galleries at the start of the week, Culture Atlas tracks <strong>${{mondaySpaces.length}}</strong> ethical cultural sanctuaries open on Mondays for quiet reflection.
              </p>
              <p class="text-slate-300">
                In Paris, you can wander through ${{formatInstLink(m1)}}, celebrated for its midnight late openings. Along the Danish coastline, the sublime seaside sculpture park at ${{formatInstLink(m2)}} is open daily and easily reached via coastal rail. In London, ${{formatInstLink(m3)}} welcomes visitors with free public admission. Each space operates with transparent civic or independent governance free from fossil-fuel influence.
              </p>
            `);
            return;
          }}

          const pTok = ALL_INSTITUTIONS.find(i => i.name.includes('Palais de Tokyo'));
          const louis = ALL_INSTITUTIONS.find(i => i.name.includes('Louisiana'));
          const sted = ALL_INSTITUTIONS.find(i => i.name.includes('Stedelijk'));
          appendCuratorMessage(`
            <p class="text-slate-200">
              Institutional schedules across our network are thoughtfully balanced between public accessibility and artist studio production. Most independent kunsthalles and artist-run spaces welcome visitors <strong>Wednesday through Sunday (11:00–18:00 or 12:00–18:00)</strong>, reserving Mondays and Tuesdays for installation and artist studio work.
            </p>
            <p class="text-slate-300">
              For evening contemplation, ${{formatInstLink(pTok)}} remains open until midnight, while spaces like ${{formatInstLink(louis)}} and ${{formatInstLink(sted)}} offer extended evening hours. You can click on any institution across the globe to review its exact timetable.
            </p>
          `);
          return;
        }}

        // B. Visitor Data: Public Transit & Getting There
        if (q.includes('transit') || q.includes('how to get') || q.includes('how do i get') || q.includes('direction') || q.includes('subway') || q.includes('metro') || q.includes('train') || q.includes('bus') || q.includes('ferry') || q.includes('getting there')) {{
          const targetInst = ALL_INSTITUTIONS.find(i => q.includes(i.name.toLowerCase()) || (i.aliases && i.aliases.some(a => q.includes(a.toLowerCase()))));
          if (targetInst) {{
            appendCuratorMessage(`
              <p class="text-slate-200">
                To travel to ${{formatInstLink(targetInst)}}, your best transit connection is: <strong>${{targetInst.transit_tips}}</strong>.
              </p>
              <p class="text-slate-300">
                The venue is situated at <strong>${{targetInst.address}}</strong> in ${{targetInst.neighborhood}}. It welcomes visitors ${{targetInst.opening_hours}}, and I recommend planning about ${{targetInst.visit_duration}} for your visit.
              </p>
            `);
            selectInstitution(targetInst, true);
            return;
          }}

          const dia = ALL_INSTITUTIONS.find(i => i.name.includes('Dia Beacon'));
          const louis = ALL_INSTITUTIONS.find(i => i.name.includes('Louisiana'));
          const kroll = ALL_INSTITUTIONS.find(i => i.name.includes('Kröller'));
          appendCuratorMessage(`
            <p class="text-slate-200">
              Every cultural sanctuary mapped in Culture Atlas includes verified public transit directions. Some of the most memorable art pilgrimages in the world are seamless by rail:
            </p>
            <p class="text-slate-300">
              You can board the Metro-North Hudson Line from Manhattan directly to ${{formatInstLink(dia)}}, take the scenic coastal Kystbanen train north from Copenhagen to ${{formatInstLink(louis)}}, or cycle through the national park forest to reach ${{formatInstLink(kroll)}} in Otterlo.
            </p>
          `);
          return;
        }}

        // C. Visitor Data: Accessibility & Universal Access
        if (q.includes('accessib') || q.includes('wheelchair') || q.includes('step-free') || q.includes('elevator') || q.includes('disab') || q.includes('mobility') || q.includes('sensory')) {{
          const targetInst = ALL_INSTITUTIONS.find(i => q.includes(i.name.toLowerCase()) || (i.aliases && i.aliases.some(a => q.includes(a.toLowerCase()))));
          if (targetInst) {{
            appendCuratorMessage(`
              <p class="text-slate-200">
                Regarding physical and sensory access, ${{formatInstLink(targetInst)}} provides: <strong>${{targetInst.accessibility}}</strong>.
              </p>
              <p class="text-slate-300">
                Transit access is straightforward via ${{targetInst.transit_tips}}. In accordance with equitable civic standards across our atlas, personal care assistants and essential companions always receive complimentary admission.
              </p>
            `);
            selectInstitution(targetInst, true);
            return;
          }}

          const serp = ALL_INSTITUTIONS.find(i => i.name.includes('Serpentine'));
          const aros = ALL_INSTITUTIONS.find(i => i.name.includes('ARoS'));
          const mplus = ALL_INSTITUTIONS.find(i => i.name.includes('M+ Museum'));
          appendCuratorMessage(`
            <p class="text-slate-200">
              Universal, barrier-free access is a core requirement of civic cultural stewardship. All institutions audited in Culture Atlas provide step-free circulation, passenger elevators, loaner wheelchairs, accessible gender-neutral washrooms, and free entry for essential companions.
            </p>
            <p class="text-slate-300">
              Exemplary barrier-free destinations include ${{formatInstLink(serp)}}, ${{formatInstLink(aros)}}, and ${{formatInstLink(mplus)}}.
            </p>
          `);
          return;
        }}

        // D. Visitor Data: Amenities (Cafés, Bookshops, Gardens)
        if (q.includes('café') || q.includes('cafe') || q.includes('coffee') || q.includes('restaurant') || q.includes('dining') || q.includes('bookshop') || q.includes('bookstore') || q.includes('garden') || q.includes('park') || q.includes('amenities') || q.includes('lockers')) {{
          const targetInst = ALL_INSTITUTIONS.find(i => q.includes(i.name.toLowerCase()) || (i.aliases && i.aliases.some(a => q.includes(a.toLowerCase()))));
          if (targetInst) {{
            appendCuratorMessage(`
              <p class="text-slate-200">
                When visiting ${{formatInstLink(targetInst)}}, you will find on-site amenities including: <strong>${{targetInst.amenities}}</strong>.
              </p>
              <p class="text-slate-300">
                While exploring, be sure not to miss its signature landmark, <span class="text-amber-300/90">${{targetInst.highlight}}</span>. The space is open to visitors ${{targetInst.opening_hours}}.
              </p>
            `);
            selectInstitution(targetInst, true);
            return;
          }}

          const louis = ALL_INSTITUTIONS.find(i => i.name.includes('Louisiana'));
          const prada = ALL_INSTITUTIONS.find(i => i.name.includes('Fondazione Prada'));
          const camden = ALL_INSTITUTIONS.find(i => i.name.includes('Camden Art Centre'));
          const tpg = ALL_INSTITUTIONS.find(i => i.name.includes("Photographers' Gallery"));
          appendCuratorMessage(`
            <p class="text-slate-200">
              Visiting an ethical cultural space is as much about contemplative pauses as the art itself. For seaside dining and an organic café overlooking the water, explore ${{formatInstLink(louis)}}.
            </p>
            <p class="text-slate-300">
              In Milan, ${{formatInstLink(prada)}} features <em>Bar Luce</em>, designed by filmmaker Wes Anderson. In London, ${{formatInstLink(camden)}} offers a tranquil garden lawn café, while ${{formatInstLink(tpg)}} in Soho hosts one of Europe's definitive photobook specialist bookshops.
            </p>
          `);
          return;
        }}

        // E. Visitor Data: Highlights & Landmarks
        if (q.includes('highlight') || q.includes('what to see') || q.includes('must-see') || q.includes('signature') || q.includes('artworks') || q.includes('monument')) {{
          const targetInst = ALL_INSTITUTIONS.find(i => q.includes(i.name.toLowerCase()) || (i.aliases && i.aliases.some(a => q.includes(a.toLowerCase()))));
          if (targetInst) {{
            appendCuratorMessage(`
              <p class="text-slate-200">
                The signature highlight at ${{formatInstLink(targetInst)}} is: <span class="text-amber-300/90 font-medium">${{targetInst.highlight}}</span>.
              </p>
              <p class="text-slate-300">
                Governed as an independent <em>${{targetInst.governance_type}}</em>, its curatorial programme centers on ${{targetInst.curatorial_focus}}. The museum welcomes visitors ${{targetInst.opening_hours}}.
              </p>
            `);
            selectInstitution(targetInst, true);
            return;
          }}

          const aros = ALL_INSTITUTIONS.find(i => i.name.includes('ARoS'));
          const dia = ALL_INSTITUTIONS.find(i => i.name.includes('Dia Beacon'));
          const inhotim = ALL_INSTITUTIONS.find(i => i.name.includes('Inhotim'));
          appendCuratorMessage(`
            <p class="text-slate-200">
              Across 35 countries, Culture Atlas maps astonishing site-specific art and architectural landmarks.
            </p>
            <p class="text-slate-300">
              Standout experiences include Olafur Eliasson's circular glass walkway <em>Your rainbow panorama</em> at ${{formatInstLink(aros)}}, Richard Serra's monumental weathered steel ellipses at ${{formatInstLink(dia)}}, and the 23 bespoke artist pavilions embedded within a 700-hectare rainforest at ${{formatInstLink(inhotim)}}.
            </p>
          `);
          return;
        }}

        // F. Methodology, Philosophy & Criteria
        if (q.includes('what type') || q.includes('should i go') || q.includes('what makes') || q.includes('method') || q.includes('criteria') || (q.includes('how') && (q.includes('evaluate') || q.includes('work') || q.includes('tier') || q.includes('ethical')))) {{
          const capc = ALL_INSTITUTIONS.find(i => i.name.includes('CAPC'));
          const plugin = ALL_INSTITUTIONS.find(i => i.name.includes('Plug In ICA'));
          const chis = ALL_INSTITUTIONS.find(i => i.name.includes('Chisenhale'));
          appendCuratorMessage(`
            <p class="text-slate-200">
              When choosing cultural spaces to support with your visit and admission, look at how their funding architecture protects artistic autonomy:
            </p>
            <p class="text-slate-300">
              First, prioritize <strong>civic municipal sanctuaries</strong> backed by public cultural councils (such as Arts Council England, DRAC in France, or the Canada Council). Because their primary accountability is to the public, curators are not pressured into censoring provocative art to appease corporate benefactors. Outstanding examples include ${{formatInstLink(capc)}} and ${{formatInstLink(plugin)}}.
            </p>
            <p class="text-slate-300">
              Second, seek out <strong>artist-run grassroots kunsthalles</strong> like ${{formatInstLink(chis)}}, where artist boards commission daring contemporary projects free from corporate board oversight.
            </p>
            <p class="text-slate-300">
              Third, celebrate <strong>institutions that actively divested</strong> from fossil fuel conglomerates and arms manufacturing, ensuring cultural spaces remain clean, uncompromised civic commons.
            </p>
          `);
          return;
        }}

        // G. Free Admission
        if (q.includes('free') || q.includes('admission') || q.includes('ticket') || q.includes('accessible') || q.includes('no fee')) {{
          const freeSpaces = ALL_INSTITUTIONS.filter(i => i.admission_policy.includes('Free Public') || i.admission_policy.includes('Always Free'));
          const f1 = freeSpaces[0] || ALL_INSTITUTIONS.find(i => i.name.includes('Chisenhale'));
          const f2 = freeSpaces[1] || ALL_INSTITUTIONS.find(i => i.name.includes('Whitechapel'));
          const f3 = freeSpaces[2] || ALL_INSTITUTIONS.find(i => i.name.includes('Serpentine'));
          appendCuratorMessage(`
            <p class="text-slate-200">
              We map <strong>${{freeSpaces.length}}</strong> cultural institutions providing completely free public admission, ensuring that contemporary art remains an open civic right rather than a commercial commodity.
            </p>
            <p class="text-slate-300">
              Standout free sanctuaries include ${{formatInstLink(f1)}}, celebrated for its artist commissions, ${{formatInstLink(f2)}} with century-old civic heritage, and the park pavilions of ${{formatInstLink(f3)}}. Each operates under public charters free from fossil-fuel sponsorship.
            </p>
          `);
          return;
        }}

        // H. Artist-run & Grassroots Centers
        if (q.includes('artist-run') || q.includes('artist run') || q.includes('grassroots') || q.includes('kunsthalle') || q.includes('independent') || q.includes('non-profit')) {{
          const artistSpaces = ALL_INSTITUTIONS.filter(i => i.governance_type.includes('Artist-Run'));
          const a1 = artistSpaces[0] || ALL_INSTITUTIONS.find(i => i.name.includes('Chisenhale'));
          const a2 = artistSpaces[1] || ALL_INSTITUTIONS.find(i => i.name.includes('Camden'));
          const a3 = artistSpaces[2] || ALL_INSTITUTIONS.find(i => i.name.includes('Plug In ICA'));
          appendCuratorMessage(`
            <p class="text-slate-200">
              Culture Atlas tracks <strong>${{artistSpaces.length}}</strong> artist-governed spaces worldwide. Governed directly by artists, these collectives champion daring, uncompromised artistic commissions completely free from corporate board interference.
            </p>
            <p class="text-slate-300">
              Standout artist-governed spaces include ${{formatInstLink(a1)}}, ${{formatInstLink(a2)}}, and ${{formatInstLink(a3)}}.
            </p>
          `);
          return;
        }}

        // I. Divestment from Fossil Fuels & Defense
        if (q.includes('fossil') || q.includes('defense') || q.includes('oil') || q.includes('bp') || q.includes('shell') || q.includes('baillie') || q.includes('weapons') || q.includes('divest')) {{
          const c1 = ALL_INSTITUTIONS.find(i => i.name.includes('Camden'));
          const c2 = ALL_INSTITUTIONS.find(i => i.name.includes('Whitechapel'));
          const c3 = ALL_INSTITUTIONS.find(i => i.name.includes('Nottingham Contemporary'));
          appendCuratorMessage(`
            <p class="text-slate-200">
              For decades, multinational extractive corporations (such as BP, Shell, and TotalEnergies) and arms manufacturers used museum underwriting to 'artwash' their public images. Over the past five years, courageous artist coalitions and cultural workers forced major venues to divest.
            </p>
            <p class="text-slate-300">
              Every single venue mapped in Culture Atlas has verified clean underwriting without fossil-fuel or defense sponsorship on its active roster. You can support this movement by visiting divested leaders such as ${{formatInstLink(c1)}}, ${{formatInstLink(c2)}}, and ${{formatInstLink(c3)}}.
            </p>
          `);
          return;
        }}

        // J. Excluded Institutions (MoMA, Whitney, Guggenheim)
        if (q.includes('moma') || q.includes('whitney') || q.includes('guggenheim') || q.includes('why exclude') || q.includes('excluded') || q.includes('kanders')) {{
          const dia = ALL_INSTITUTIONS.find(i => i.name.includes('Dia Beacon'));
          const sculp = ALL_INSTITUTIONS.find(i => i.name.includes('SculptureCenter'));
          const serp = ALL_INSTITUTIONS.find(i => i.name.includes('Serpentine'));
          appendCuratorMessage(`
            <p class="text-slate-200">
              Culture Atlas maintains a strict exclusion policy for institutions that retain unresolved ties to controversial underwriters, defense manufacturing, or human rights violations.
            </p>
            <p class="text-slate-300">
              The Museum of Modern Art (MoMA) in New York sparked citywide protests over trustees holding major stakes in defense contractors, private prisons, and extractive debt. Similarly, the Whitney Museum faced global artist boycotts until board vice chair Warren Kanders (CEO of tear gas manufacturer Safariland) stepped down under international pressure.
            </p>
            <p class="text-slate-300">
              Culture Atlas chooses instead to celebrate institutions whose funding architecture is clean and uncompromised, such as ${{formatInstLink(dia)}}, ${{formatInstLink(sculp)}}, and ${{formatInstLink(serp)}}.
            </p>
          `);
          return;
        }}

        // K. General City Inquiries
        const matchedCity = findMentionedCity(q) || (PRIORITY_CITIES.find(c => q.includes(c.name.toLowerCase()))?.name);
        if (matchedCity || q.includes('city') || q.includes('in ')) {{
          const cityName = matchedCity ? matchedCity : '';
          const cityMatches = ALL_INSTITUTIONS.filter(i => {{
            if (cityName) return matchC(i.city, cityName);
            return q.includes(i.city.toLowerCase());
          }});

          if (cityMatches.length > 0) {{
            const targetCity = cityMatches[0].city;
            const c1 = cityMatches[0];
            const c2 = cityMatches[1];
            const c3 = cityMatches[2];
            appendCuratorMessage(`
              <p class="text-slate-200">
                If you are exploring <a href="#" class="city-link font-semibold text-white hover:text-[#60a5fa] underline cursor-pointer" data-city="${{escapeHtml(targetCity)}}">${{escapeHtml(targetCity)}}</a>, we have mapped <strong>${{cityMatches.length}}</strong> verified ethical cultural sanctuaries here.
              </p>
              <p class="text-slate-300">
                Standout spaces include ${{formatInstLink(c1, {{noCity: true}})}}, celebrated for its ${{c1.curatorial_focus || 'contemporary commissions'}}${{c2 ? `, ${{formatInstLink(c2, {{noCity: true}})}}, offering ${{c2.admission_policy}}` : ''}}${{c3 ? `, and ${{formatInstLink(c3, {{noCity: true}})}}` : ''}}. All of these operate with transparent public charters free from fossil-fuel sponsorship.
              </p>
            `);

            filterByCity(targetCity, true, false);
            return;
          }}
        }}

        // L. Country Inquiries
        const matchedCountry = COUNTRY_CENTROIDS.find(c => q.includes(c.name.toLowerCase()) || q.includes(c.name.toLowerCase().replace('united states', 'usa')));
        if (matchedCountry) {{
          const countryMatches = ALL_INSTITUTIONS.filter(i => matchC(i.country, matchedCountry.name));
          if (countryMatches.length > 0) {{
            const co1 = countryMatches[0];
            const co2 = countryMatches[1];
            const co3 = countryMatches[2];
            appendCuratorMessage(`
              <p class="text-slate-200">
                Across <strong>${{escapeHtml(matchedCountry.name)}}</strong>, Culture Atlas tracks <strong>${{countryMatches.length}}</strong> verified cultural spaces where public accountability and artistic autonomy take priority over private commercial influence.
              </p>
              <p class="text-slate-300">
                Remarkable spaces to explore include ${{formatInstLink(co1)}}${{co2 ? `, ${{formatInstLink(co2)}}` : ''}}${{co3 ? `, and ${{formatInstLink(co3)}}` : ''}}.
              </p>
            `);

            flyTo(matchedCountry.lon, matchedCountry.lat);
            return;
          }}
        }}

        // M. Specific Institution Lookup
        const instMatch = ALL_INSTITUTIONS.find(i => q.includes(i.name.toLowerCase()) || (i.aliases && i.aliases.some(a => q.includes(a.toLowerCase()))) || (i.name.toLowerCase().includes(q) && q.length > 3));
        if (instMatch) {{
          appendCuratorMessage(`
            <p class="text-slate-200">
              ${{formatInstLink(instMatch, {{noCity: false}})}} is an ethical cultural sanctuary founded in ${{instMatch.year_founded}} in the ${{instMatch.neighborhood}} district.
            </p>
            <p class="text-slate-300">
              Governed as an independent <em>${{instMatch.governance_type}}</em>, the institution focuses on ${{instMatch.curatorial_focus}}. Admission is <strong>${{instMatch.admission_policy}}</strong> (${{instMatch.admission_details}}), welcoming visitors ${{instMatch.opening_hours}}.
            </p>
            <p class="text-slate-300">
              When visiting, make sure to experience its signature highlight: <span class="text-amber-300/90 font-medium">${{instMatch.highlight}}</span>. Its verified ethical safeguard confirms: ${{instMatch.ethical_safeguard}}.
            </p>
          `);

          selectInstitution(instMatch, true);
          return;
        }}

        // N. Surprise Me / Recommendations
        if (q.includes('surprise') || q.includes('recommend') || q.includes('random') || q.includes('hidden gem')) {{
          const randomA = ALL_INSTITUTIONS.filter(i => i.tier === 'A');
          const pick1 = randomA[Math.floor(Math.random() * randomA.length)];
          const pick2 = randomA[Math.floor(Math.random() * randomA.length)];

          appendCuratorMessage(`
            <p class="text-slate-200">
              Here are two extraordinary institutions with inspiring ethical commitments and artistic integrity: ${{formatInstLink(pick1)}} and ${{formatInstLink(pick2)}}.
            </p>
            <p class="text-slate-300">
              Both operate with verified independence and champion bold contemporary commissions without corporate sponsor restrictions.
            </p>
          `);

          selectInstitution(pick1, false);
          return;
        }}

        // O. Fallback with helpful conversational guidance
        const dia = ALL_INSTITUTIONS.find(i => i.name.includes('Dia Beacon'));
        const chis = ALL_INSTITUTIONS.find(i => i.name.includes('Chisenhale'));
        const louis = ALL_INSTITUTIONS.find(i => i.name.includes('Louisiana'));
        appendCuratorMessage(`
          <p class="text-slate-200">
            I would be delighted to guide you to ethically funded cultural institutions across <strong>35 countries and 133 cities</strong>.
          </p>
          <p class="text-slate-300">
            Whether you are planning a journey to <a href="#" class="city-link text-[#93c5fd] hover:underline cursor-pointer" data-city="London">London</a>, <a href="#" class="city-link text-[#93c5fd] hover:underline cursor-pointer" data-city="Paris">Paris</a>, or <a href="#" class="city-link text-[#93c5fd] hover:underline cursor-pointer" data-city="New York">New York</a>, or exploring critical theory from <em>Beyond Objecthood</em>, <em>e-flux journal</em>, and institutional critique, I can direct you to uncompromised sanctuaries like ${{formatInstLink(dia)}}, ${{formatInstLink(chis)}}, or ${{formatInstLink(louis)}}.
          </p>
          <p class="text-[#93c5fd]">
            What city or type of art experience would you love to discover today?
          </p>
        `);

      }}, 300);
    }}
\n"""
        src = src[:old_handle_start] + new_handle + src[old_handle_end:]
        print("Replaced handleCuratorQuery with complete Critical Knowledge Engine")
    else:
        print("Warning: old handleCuratorQuery boundaries not found!")

    # 4. Replace Settings Modal event listeners (around line 2370)
    old_events_start = src.find("    // Settings Modal\n    const settingsModal = document.getElementById('curatorSettingsModal');")
    old_events_end = src.find("    // =========================================================\n    // 📋 CATALOG LIST & FILTERING ENGINE", old_events_start)

    if old_events_start != -1 and old_events_end != -1:
        new_events = """    // Curator Intelligence Settings Modal (Multi-Provider: Claude, OpenAI, Gemini)
    const settingsModal = document.getElementById('curatorSettingsModal');
    const aiApiKeyInput = document.getElementById('aiApiKeyInput');
    const aiModelSelect = document.getElementById('aiModelSelect');
    const keyDetectBadge = document.getElementById('keyDetectBadge');
    const connectionTestBox = document.getElementById('connectionTestBox');
    const testStatusIcon = document.getElementById('testStatusIcon');
    const testStatusMsg = document.getElementById('testStatusMsg');
    const toggleKeyVisibilityBtn = document.getElementById('toggleKeyVisibilityBtn');
    const providerTip = document.getElementById('providerTip');

    let currentSelectedProvider = getEffectiveProvider();

    const PROVIDER_MODELS = {{
      anthropic: [
        {{ id: 'claude-haiku-4-5-20251001', name: 'claude-haiku-4-5-20251001 (Fast & Articulate - Recommended)' }},
        {{ id: 'claude-sonnet-4-5-20250929', name: 'claude-sonnet-4-5-20250929 (Deep Critical Reasoning)' }}
      ],
      openai: [
        {{ id: 'gpt-4o-mini', name: 'gpt-4o-mini (Fast & Versatile)' }},
        {{ id: 'gpt-4o', name: 'gpt-4o (Full Reasoning)' }}
      ],
      gemini: [
        {{ id: 'gemini-2.5-flash', name: 'gemini-2.5-flash (Fast & Multimodal)' }},
        {{ id: 'gemini-1.5-flash', name: 'gemini-1.5-flash (Reliable Fallback)' }}
      ]
    }};

    function updateProviderUI(prov) {{
      currentSelectedProvider = prov;
      const claudeBtn = document.getElementById('providerClaudeBtn');
      const openaiBtn = document.getElementById('providerOpenAIBtn');
      const geminiBtn = document.getElementById('providerGeminiBtn');

      [claudeBtn, openaiBtn, geminiBtn].forEach(b => {{
        if (b) {{
          b.classList.remove('bg-[#27272a]', 'text-white', 'border-[#3e3e3e]');
          b.classList.add('bg-[#1f1f23]', 'text-[#a1a1aa]', 'border-[#27272a]');
        }}
      }});

      const activeBtn = prov === 'anthropic' ? claudeBtn : (prov === 'openai' ? openaiBtn : geminiBtn);
      if (activeBtn) {{
        activeBtn.classList.remove('bg-[#1f1f23]', 'text-[#a1a1aa]', 'border-[#27272a]');
        activeBtn.classList.add('bg-[#27272a]', 'text-white', 'border-[#3e3e3e]');
      }}

      // Populate model options
      const models = PROVIDER_MODELS[prov] || PROVIDER_MODELS.anthropic;
      aiModelSelect.innerHTML = models.map(m => `<option value="${{m.id}}">${{m.name}}</option>`).join('');
      if (aiModel) aiModelSelect.value = aiModel;

      // Update Tip
      if (providerTip) {{
        if (prov === 'anthropic') {{
          providerTip.innerHTML = 'Recommended: <strong>Claude 3.5 / Haiku 4.5</strong> excels at art theory, <em>Beyond Objecthood</em>, e-flux criticism, and institutional analysis.';
        }} else if (prov === 'openai') {{
          providerTip.innerHTML = 'OpenAI <strong>GPT-4o / GPT-4o-mini</strong> provides fast conversational guidance across all 203 mapped sanctuaries.';
        }} else {{
          providerTip.innerHTML = 'Google <strong>Gemini 2.5 Flash</strong> provides responsive real-time multimodal reasoning.';
        }}
      }}
    }}

    document.getElementById('providerClaudeBtn')?.addEventListener('click', () => updateProviderUI('anthropic'));
    document.getElementById('providerOpenAIBtn')?.addEventListener('click', () => updateProviderUI('openai'));
    document.getElementById('providerGeminiBtn')?.addEventListener('click', () => updateProviderUI('gemini'));

    document.getElementById('curatorSettingsBtn')?.addEventListener('click', () => {{
      settingsModal.classList.remove('hidden');
      aiApiKeyInput.value = aiApiKey;
      updateProviderUI(getEffectiveProvider());
      updateDetectBadge(aiApiKey);
      connectionTestBox.classList.add('hidden');
    }});

    document.getElementById('closeSettingsModalBtn')?.addEventListener('click', () => {{
      settingsModal.classList.add('hidden');
    }});

    toggleKeyVisibilityBtn?.addEventListener('click', () => {{
      if (aiApiKeyInput.type === 'password') {{
        aiApiKeyInput.type = 'text';
        toggleKeyVisibilityBtn.textContent = '🔒';
      }} else {{
        aiApiKeyInput.type = 'password';
        toggleKeyVisibilityBtn.textContent = '👁️';
      }}
    }});

    function updateDetectBadge(val) {{
      const k = (val || '').trim();
      if (!k) {{
        keyDetectBadge.textContent = 'Auto-detecting provider...';
        keyDetectBadge.className = 'text-[14px] font-mono text-[#a1a1aa]';
        return;
      }}
      if (k.startsWith('sk-ant-')) {{
        keyDetectBadge.textContent = '🟣 Anthropic Claude key detected';
        keyDetectBadge.className = 'text-[14px] font-mono text-purple-400';
        updateProviderUI('anthropic');
      }} else if (k.startsWith('sk-') || k.startsWith('sk-proj-')) {{
        keyDetectBadge.textContent = '🟢 OpenAI key detected';
        keyDetectBadge.className = 'text-[14px] font-mono text-emerald-400';
        updateProviderUI('openai');
      }} else if (k.startsWith('AIza')) {{
        keyDetectBadge.textContent = '🔵 Google Gemini key detected';
        keyDetectBadge.className = 'text-[14px] font-mono text-blue-400';
        updateProviderUI('gemini');
      }} else {{
        keyDetectBadge.textContent = 'Custom API key';
        keyDetectBadge.className = 'text-[14px] font-mono text-amber-400';
      }}
    }}

    aiApiKeyInput?.addEventListener('input', (e) => {{
      updateDetectBadge(e.target.value);
    }});

    document.getElementById('testConnectionBtn')?.addEventListener('click', async () => {{
      const key = aiApiKeyInput.value.trim();
      const model = aiModelSelect.value;
      connectionTestBox.classList.remove('hidden', 'border-emerald-500/30', 'bg-emerald-500/10', 'text-emerald-400', 'border-rose-500/30', 'bg-rose-500/10', 'text-rose-400');
      connectionTestBox.classList.add('border-[#3e3e3e]', 'bg-[#27272a]', 'text-[#d4d4d4]');
      testStatusIcon.textContent = '⏳';
      testStatusMsg.textContent = 'Testing connection with live API...';

      const res = await testAPIConnection(currentSelectedProvider, key, model);
      if (res.success) {{
        connectionTestBox.classList.remove('border-[#3e3e3e]', 'bg-[#27272a]', 'text-[#d4d4d4]');
        connectionTestBox.classList.add('border-emerald-500/30', 'bg-emerald-500/10', 'text-emerald-400');
        testStatusIcon.textContent = '✓';
        testStatusMsg.textContent = res.message;
      }} else {{
        connectionTestBox.classList.remove('border-[#3e3e3e]', 'bg-[#27272a]', 'text-[#d4d4d4]');
        connectionTestBox.classList.add('border-rose-500/30', 'bg-rose-500/10', 'text-rose-400');
        testStatusIcon.textContent = '✕';
        testStatusMsg.textContent = res.error;
      }}
    }});

    document.getElementById('saveApiKeyBtn')?.addEventListener('click', () => {{
      aiApiKey = aiApiKeyInput.value.trim();
      aiProvider = currentSelectedProvider;
      aiModel = aiModelSelect.value;
      localStorage.setItem('atlas_ai_api_key', aiApiKey);
      localStorage.setItem('atlas_ai_provider', aiProvider);
      localStorage.setItem('atlas_ai_model', aiModel);
      updateAIStatusUI();
      settingsModal.classList.add('hidden');
    }});

    document.getElementById('clearApiKeyBtn')?.addEventListener('click', () => {{
      aiApiKey = '';
      aiProvider = 'auto';
      aiModel = '';
      aiApiKeyInput.value = '';
      localStorage.removeItem('atlas_ai_api_key');
      localStorage.removeItem('atlas_gemini_api_key');
      localStorage.removeItem('atlas_ai_provider');
      localStorage.removeItem('atlas_ai_model');
      updateAIStatusUI();
      connectionTestBox.classList.add('hidden');
      settingsModal.classList.add('hidden');
    }});

    // Initialize UI Status on startup
    updateAIStatusUI();
\n"""
        src = src[:old_events_start] + new_events + src[old_events_end:]
        print("Replaced Settings Modal events")
    else:
        print("Warning: old Settings Modal event boundaries not found!")

    # 5. Also ensure build outputs synchronize directly to root index.html
    sync_root_target = """    dest_root = "/Users/polinavasilyeva/.gemini/antigravity/scratch/sponsor-atlas/index.html"
    with open(dest_root, "w", encoding="utf-8") as f:
        f.write(html)
    print("Synchronized root index.html!")
"""
    if "dest_root = " not in src:
        dest_app_idx = src.find('dest_app = "/Users/polinavasilyeva/.gemini/antigravity/scratch/sponsor-atlas/app/index.html"')
        if dest_app_idx != -1:
            src = src[:dest_app_idx] + sync_root_target + src[dest_app_idx:]
            print("Added root index.html synchronization to build script")

    with open("build_conversational_atlas.py", "w", encoding="utf-8") as f:
        f.write(src)
    print("Saved build_conversational_atlas.py (Phase 2 complete)!")

if __name__ == "__main__":
    update_atlas()
