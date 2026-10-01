#!/usr/bin/env python3
"""
apply_proper_simple_language.py
Rewrites all curator responses, prompts, and templates in build_conversational_atlas.py
and build_conversational_widget.py into proper, simple, clear, and direct English.
"""

import sys

def patch_atlas():
    path = "/Users/polinavasilyeva/.gemini/antigravity/scratch/sponsor-atlas/build_conversational_atlas.py"
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Update Inquiry Chips queries (simpler, plain English questions)
    old_chips = """        <!-- Sleek OpenAI ChatGPT-style Prompt Suggestions -->
        <div id="curatorInquiryRow" class="max-w-3xl mx-auto w-full px-3 sm:px-6 py-2 flex items-center gap-1.5 overflow-x-auto custom-scrollbar shrink-0 text-[14px] whitespace-nowrap">
          <button class="inquiry-chip px-3 py-1 rounded-full border border-[#1b3324] bg-[#0c1f15] text-[#6ee7b7] hover:border-[#10b981] hover:bg-[#112d1e] transition active:scale-95 flex items-center gap-1.5" data-filter="free" data-chip-color="green" data-query="Which cultural spaces offer always free admission?">
            <span>🎟️ Free Admission</span>
          </button>
          <button class="inquiry-chip px-3 py-1 rounded-full border border-[#232a3c] bg-[#101522] text-[#93c5fd] hover:border-[#3b82f6] hover:bg-[#151c30] transition active:scale-95 flex items-center gap-1.5" data-filter="monday" data-chip-color="blue" data-query="What are typical museum opening hours and which institutions are open on Mondays?">
            <span>🕒 Hours & Mondays</span>
          </button>
          <button class="inquiry-chip px-3 py-1 rounded-full border border-[#232a3c] bg-[#101522] text-[#93c5fd] hover:border-[#3b82f6] hover:bg-[#151c30] transition active:scale-95 flex items-center gap-1.5" data-filter="transit" data-chip-color="blue" data-query="How do I get to destination museums like Dia Beacon or Louisiana by public transit?">
            <span>🚇 Public Transit Tips</span>
          </button>
          <button class="inquiry-chip px-3 py-1 rounded-full border border-[#232a3c] bg-[#101522] text-[#cbd5e1] hover:border-[#3b82f6] hover:bg-[#151c30] transition active:scale-95 flex items-center gap-1.5" data-filter="accessibility" data-chip-color="slate" data-query="Which museums offer step-free wheelchair accessibility and inclusive facilities?">
            <span>♿ Accessibility</span>
          </button>
          <button class="inquiry-chip px-3 py-1 rounded-full border border-[#232a3c] bg-[#101522] text-[#cbd5e1] hover:border-[#3b82f6] hover:bg-[#151c30] transition active:scale-95 flex items-center gap-1.5" data-filter="amenities" data-chip-color="slate" data-query="Which institutions feature outstanding cafés, sculpture gardens, and art bookshops?">
            <span>☕ Cafés & Bookshops</span>
          </button>
          <button class="inquiry-chip px-3 py-1 rounded-full border border-[#232a3c] bg-[#101522] text-[#93c5fd] hover:border-[#3b82f6] hover:bg-[#151c30] transition active:scale-95 flex items-center gap-1.5" data-filter="ethical" data-chip-color="blue" data-query="What makes an institution ethically funded and what is Tier A?">
            <span>🏛️ Ethical Criteria</span>
          </button>
          <button class="inquiry-chip px-3 py-1 rounded-full border border-[#232a3c] bg-[#101522] text-[#cbd5e1] hover:border-[#3b82f6] hover:bg-[#151c30] transition active:scale-95 flex items-center gap-1.5" data-filter="artist_run" data-chip-color="slate" data-query="Recommend independent artist-run centers and grassroots kunsthalles">
            <span>🎨 Artist-Run Spaces</span>
          </button>
          <button class="inquiry-chip px-3 py-1 rounded-full border border-[#1b3324] bg-[#0c1f15] text-[#6ee7b7] hover:border-[#10b981] hover:bg-[#112d1e] transition active:scale-95 flex items-center gap-1.5" data-filter="fossil_free" data-chip-color="green" data-query="Show institutions free from fossil fuels and defense sponsors">
            <span>🌿 Fossil & defense-free spaces</span>
          </button>
          <button class="inquiry-chip px-3 py-1 rounded-full border border-[#232a3c] bg-[#101522] text-[#93c5fd] hover:border-[#3b82f6] hover:bg-[#151c30] transition active:scale-95 flex items-center gap-1.5" data-filter="london" data-chip-color="blue" data-city="London" data-query="Tell me about London's art scene, independent spaces, and divestment history">
            <span>📍 London guide</span>
          </button>
          <button class="inquiry-chip px-3 py-1 rounded-full border border-[#232a3c] bg-[#101522] text-[#93c5fd] hover:border-[#3b82f6] hover:bg-[#151c30] transition active:scale-95 flex items-center gap-1.5" data-filter="nyc" data-chip-color="blue" data-city="New York" data-query="Tell me about New York's art scene and independent spaces">
            <span>📍 New York guide</span>
          </button>
          <button class="inquiry-chip px-3 py-1 rounded-full border border-[#232a3c] bg-[#101522] text-[#93c5fd] hover:border-[#3b82f6] hover:bg-[#151c30] transition active:scale-95 flex items-center gap-1.5" data-filter="paris" data-chip-color="blue" data-city="Paris" data-query="Tell me about Paris's contemporary art scene and civic spaces">
            <span>📍 Paris guide</span>
          </button>
          <button class="inquiry-chip px-3 py-1 rounded-full border border-[#3b2b11] bg-[#221807] text-[#fcd34d] hover:border-[#f59e0b] hover:bg-[#2d2009] transition active:scale-95 flex items-center gap-1.5" data-filter="moma" data-chip-color="amber" data-query="Why is MoMA excluded from Culture Atlas?">
            <span>⚠️ Why MoMA is excluded</span>
          </button>
          <button class="inquiry-chip px-3 py-1 rounded-full border border-[#2f2f2f] bg-[#212121] text-[#d4d4d4] hover:bg-[#2b2b2b] hover:text-white transition active:scale-95 flex items-center gap-1.5" data-filter="theory_objecthood" data-query="What is Beyond Objecthood and how did the exhibition become a critical form?">
            <span>📖 Beyond Objecthood</span>
          </button>
          <button class="inquiry-chip px-3 py-1 rounded-full border border-[#2f2f2f] bg-[#212121] text-[#d4d4d4] hover:bg-[#2b2b2b] hover:text-white transition active:scale-95 flex items-center gap-1.5" data-filter="theory_eflux" data-query="What does e-flux say about the museum as a factory and duty-free art?">
            <span>📑 e-flux: Museum as factory</span>
          </button>
          <button class="inquiry-chip px-3 py-1 rounded-full border border-[#2f2f2f] bg-[#212121] text-[#d4d4d4] hover:bg-[#2b2b2b] hover:text-white transition active:scale-95 flex items-center gap-1.5" data-filter="theory_critique" data-query="Explain the three waves of institutional critique from Hans Haacke to Nan Goldin and Strike MoMA">
            <span>⚡ 3 Waves of Critique</span>
          </button>
          <button class="inquiry-chip px-3 py-1 rounded-full border border-[#232a3c] bg-[#101522] text-[#cbd5e1] hover:border-[#3b82f6] hover:bg-[#151c30] transition active:scale-95 flex items-center gap-1.5" data-filter="surprise" data-chip-color="slate" data-query="Surprise me with a unique ethical cultural institution">
            <span>✨ Surprise me</span>
          </button>
        </div>"""

    new_chips = """        <!-- Sleek OpenAI ChatGPT-style Prompt Suggestions -->
        <div id="curatorInquiryRow" class="max-w-3xl mx-auto w-full px-3 sm:px-6 py-2 flex items-center gap-1.5 overflow-x-auto custom-scrollbar shrink-0 text-[14px] whitespace-nowrap">
          <button class="inquiry-chip px-3 py-1 rounded-full border border-[#1b3324] bg-[#0c1f15] text-[#6ee7b7] hover:border-[#10b981] hover:bg-[#112d1e] transition active:scale-95 flex items-center gap-1.5" data-filter="free" data-chip-color="green" data-query="Which museums and galleries are free to enter?">
            <span>🎟️ Free Admission</span>
          </button>
          <button class="inquiry-chip px-3 py-1 rounded-full border border-[#232a3c] bg-[#101522] text-[#93c5fd] hover:border-[#3b82f6] hover:bg-[#151c30] transition active:scale-95 flex items-center gap-1.5" data-filter="monday" data-chip-color="blue" data-query="Which museums are open on Mondays?">
            <span>🕒 Hours & Mondays</span>
          </button>
          <button class="inquiry-chip px-3 py-1 rounded-full border border-[#232a3c] bg-[#101522] text-[#93c5fd] hover:border-[#3b82f6] hover:bg-[#151c30] transition active:scale-95 flex items-center gap-1.5" data-filter="transit" data-chip-color="blue" data-query="How do I get to Dia Beacon or Louisiana by train?">
            <span>🚇 Public Transit Tips</span>
          </button>
          <button class="inquiry-chip px-3 py-1 rounded-full border border-[#232a3c] bg-[#101522] text-[#cbd5e1] hover:border-[#3b82f6] hover:bg-[#151c30] transition active:scale-95 flex items-center gap-1.5" data-filter="accessibility" data-chip-color="slate" data-query="Which museums have wheelchair and step-free access?">
            <span>♿ Accessibility</span>
          </button>
          <button class="inquiry-chip px-3 py-1 rounded-full border border-[#232a3c] bg-[#101522] text-[#cbd5e1] hover:border-[#3b82f6] hover:bg-[#151c30] transition active:scale-95 flex items-center gap-1.5" data-filter="amenities" data-chip-color="slate" data-query="Which spaces have great cafés, gardens, or bookshops?">
            <span>☕ Cafés & Bookshops</span>
          </button>
          <button class="inquiry-chip px-3 py-1 rounded-full border border-[#232a3c] bg-[#101522] text-[#93c5fd] hover:border-[#3b82f6] hover:bg-[#151c30] transition active:scale-95 flex items-center gap-1.5" data-filter="ethical" data-chip-color="blue" data-query="How do you decide if a museum has clean funding?">
            <span>🏛️ Clean Funding</span>
          </button>
          <button class="inquiry-chip px-3 py-1 rounded-full border border-[#232a3c] bg-[#101522] text-[#cbd5e1] hover:border-[#3b82f6] hover:bg-[#151c30] transition active:scale-95 flex items-center gap-1.5" data-filter="artist_run" data-chip-color="slate" data-query="What are the best artist-run spaces to visit?">
            <span>🎨 Artist-Run Spaces</span>
          </button>
          <button class="inquiry-chip px-3 py-1 rounded-full border border-[#1b3324] bg-[#0c1f15] text-[#6ee7b7] hover:border-[#10b981] hover:bg-[#112d1e] transition active:scale-95 flex items-center gap-1.5" data-filter="fossil_free" data-chip-color="green" data-query="Show spaces that do not take oil or weapons money">
            <span>🌿 Fossil & defense-free</span>
          </button>
          <button class="inquiry-chip px-3 py-1 rounded-full border border-[#232a3c] bg-[#101522] text-[#93c5fd] hover:border-[#3b82f6] hover:bg-[#151c30] transition active:scale-95 flex items-center gap-1.5" data-filter="london" data-chip-color="blue" data-city="London" data-query="Tell me about London's independent art spaces">
            <span>📍 London guide</span>
          </button>
          <button class="inquiry-chip px-3 py-1 rounded-full border border-[#232a3c] bg-[#101522] text-[#93c5fd] hover:border-[#3b82f6] hover:bg-[#151c30] transition active:scale-95 flex items-center gap-1.5" data-filter="nyc" data-chip-color="blue" data-city="New York" data-query="Tell me about New York's art spaces and board controversies">
            <span>📍 New York guide</span>
          </button>
          <button class="inquiry-chip px-3 py-1 rounded-full border border-[#232a3c] bg-[#101522] text-[#93c5fd] hover:border-[#3b82f6] hover:bg-[#151c30] transition active:scale-95 flex items-center gap-1.5" data-filter="paris" data-chip-color="blue" data-city="Paris" data-query="Tell me about art spaces to visit in Paris">
            <span>📍 Paris guide</span>
          </button>
          <button class="inquiry-chip px-3 py-1 rounded-full border border-[#3b2b11] bg-[#221807] text-[#fcd34d] hover:border-[#f59e0b] hover:bg-[#2d2009] transition active:scale-95 flex items-center gap-1.5" data-filter="moma" data-chip-color="amber" data-query="Why is MoMA excluded from Culture Atlas?">
            <span>⚠️ Why MoMA is excluded</span>
          </button>
          <button class="inquiry-chip px-3 py-1 rounded-full border border-[#2f2f2f] bg-[#212121] text-[#d4d4d4] hover:bg-[#2b2b2b] hover:text-white transition active:scale-95 flex items-center gap-1.5" data-filter="theory_objecthood" data-query="Explain 'Beyond Objecthood' in simple terms">
            <span>📖 Beyond Objecthood</span>
          </button>
          <button class="inquiry-chip px-3 py-1 rounded-full border border-[#2f2f2f] bg-[#212121] text-[#d4d4d4] hover:bg-[#2b2b2b] hover:text-white transition active:scale-95 flex items-center gap-1.5" data-filter="theory_eflux" data-query="Explain e-flux and 'Is a Museum a Factory?' in simple terms">
            <span>📑 e-flux: Museum as factory</span>
          </button>
          <button class="inquiry-chip px-3 py-1 rounded-full border border-[#2f2f2f] bg-[#212121] text-[#d4d4d4] hover:bg-[#2b2b2b] hover:text-white transition active:scale-95 flex items-center gap-1.5" data-filter="theory_critique" data-query="Explain the three waves of institutional critique in simple terms">
            <span>⚡ 3 Waves of Critique</span>
          </button>
          <button class="inquiry-chip px-3 py-1 rounded-full border border-[#232a3c] bg-[#101522] text-[#cbd5e1] hover:border-[#3b82f6] hover:bg-[#151c30] transition active:scale-95 flex items-center gap-1.5" data-filter="surprise" data-chip-color="slate" data-query="Surprise me with a great art space">
            <span>✨ Surprise me</span>
          </button>
        </div>"""

    if old_chips in content:
        content = content.replace(old_chips, new_chips)
        print("Updated Inquiry chips to simple queries!")
    else:
        print("WARNING: Could not find old_chips block!")

    # 2. Update Modal text for New York alternatives
    content = content.replace(
        "Instead of supporting corporate-compromised boards, visit New York's <strong>11 verified ethical cultural sanctuaries</strong>—including <em>Dia Beacon, SculptureCenter, Artists Space, and The Studio Museum in Harlem</em>.",
        "Instead of supporting corporate-compromised boards, visit New York's <strong>11 spaces with clean funding</strong>—including <em>Dia Beacon, SculptureCenter, Artists Space, and The Studio Museum in Harlem</em>."
    )
    content = content.replace(
        "Explore 11 Ethical NYC Spaces",
        "Explore 11 Clean NYC Spaces"
    )

    # 3. Update Welcome Message
    old_welcome = """    // Initial Welcome Message with Gentle Education
    function initCuratorConversation() {{
      curatorMessages.innerHTML = '';
      appendCuratorMessage(`
        <p class="text-[#ececec]">
          Welcome to <strong>Culture Atlas</strong>. In an era where major art institutions routinely rely on trustees and sponsors linked to fossil fuel extraction, defense manufacturing, or predatory finance, Culture Atlas was created to map <strong>203 cultural sanctuaries across 35 countries</strong> that protect curatorial independence and public trust.
        </p>
        <p class="text-[#d4d4d4]">
          We highlight four ethical models: <strong>civic municipal sanctuaries</strong> supported by public arts councils, <strong>artist-run grassroots Kunsthalles</strong> with creative autonomy, institutions that actively <strong>divested from fossil fuels</strong>, and spaces offering <strong>free public admission</strong> as a fundamental civic right.
        </p>
        <p class="text-[#93c5fd]">
          You can ask me anything about visitor hours, public transit directions, or specific destinations like <a href="#" class="inst-link" data-name="Chisenhale Gallery">Chisenhale Gallery</a>, <a href="#" class="inst-link" data-name="Dia Beacon">Dia Beacon</a>, or <a href="#" class="city-link" data-city="London">London</a>.
        </p>
      `);
    }}"""

    new_welcome = """    // Initial Welcome Message with Simple Plain Language
    function initCuratorConversation() {{
      curatorMessages.innerHTML = '';
      appendCuratorMessage(`
        <p class="text-[#ececec]">
          Welcome to <strong>Culture Atlas</strong>. We map <strong>203 museums and art spaces across 35 countries</strong> that do not take money from oil companies, weapons makers, or private prisons.
        </p>
        <p class="text-[#d4d4d4]">
          You can explore spaces with <strong>free admission</strong>, <strong>artist-run galleries</strong>, public museums, and places open on Mondays.
        </p>
        <p class="text-[#93c5fd]">
          Ask me about opening hours, how to get to any space by train or bus, or explore cities like <a href="#" class="city-link" data-city="London">London</a>, <a href="#" class="city-link" data-city="Paris">Paris</a>, or <a href="#" class="city-link" data-city="New York">New York</a>.
        </p>
      `);
    }}"""

    if old_welcome in content:
        content = content.replace(old_welcome, new_welcome)
        print("Updated initCuratorConversation to simple language!")
    else:
        print("WARNING: Could not find old_welcome block!")

    # 4. Update criticalSystemPrompt for Live Generative AI
    old_prompt = """      const criticalSystemPrompt = `You are the Culture Atlas Curator, an erudite, warm, and articulate contemporary art scholar and guide to ethical cultural institutions worldwide.
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
6. Never output markdown headers (#, ##) or structured database field labels like 'Address:', 'Hours:', 'Highlight:'. Speak in fluid, natural prose as an inspiring curator and theorist.`;"""

    new_prompt = """      const criticalSystemPrompt = `You are the Culture Atlas assistant, a friendly, clear, and direct guide to art museums and galleries worldwide.
Culture Atlas maps 203 museums and art spaces across 35 countries that don't take money from fossil fuels, weapons manufacturers, or private prisons.

CORE INSTRUCTION: SPEAK IN PROPER, SIMPLE, CLEAR LANGUAGE.
- Use plain, natural, everyday English.
- Avoid academic art-world jargon or flowery marketing phrases. Never say "cultural sanctuaries", "for quiet reflection", "for evening contemplation", "uncompromised curatorial experimentation", "shutter their galleries", "sublime", "epistemologies", or "palliative".
- Speak like a knowledgeable, friendly human who explains things directly and simply.
- Keep sentences short, clean, and conversational.

CRITICAL THEORY & ART HISTORY KNOWLEDGE (Explain simply):
You know contemporary art and institutional critique deeply, but you explain every concept in simple, accessible terms:
- "Beyond Objecthood" by James Voorhies (MIT Press, 2017): Explain how artists from 1968 turned the exhibition itself into an artwork (embracing the "theatricality" that critic Michael Fried criticized in 1967). Explain simply how big corporate museums later turned participation into tourist entertainment, pushing honest experimental art into independent non-profit spaces.
- "e-flux journal": Explain Hito Steyerl's ideas simply—how museums act like factories where visitors' attention produces profit ("Is a Museum a Factory?"), and how billionaires store art in tax-free airport warehouses ("Duty Free Art"). Explain Boris Groys's point that public museums started during the French Revolution to make art public property.
- Three Waves of Institutional Critique: Explain in plain terms:
  1. 1st Wave (1970s): Hans Haacke exposing museum board members' politics and real estate ties.
  2. 2nd Wave (1980s-90s): Andrea Fraser and Fred Wilson showing racism and money inside museums.
  3. 3rd Wave (Today): Activist campaigns like Nan Goldin's P.A.I.N. forcing museums to drop the Sackler opioid family, and protests against tear-gas and defense donors at MoMA and the Whitney.
- Claire Bishop: Explain simply her critique of corporate mega-museums versus thoughtful civic museums, and why participatory art isn't always radical.

FORMATTING & INTERACTION RULES:
1. Write in natural conversational paragraphs. Never use markdown headers (#, ##) or bulleted database dumps.
2. Link institutions in our atlas strictly as:
<a href="#" class="inst-link font-semibold text-white hover:text-[#60a5fa] underline cursor-pointer" data-name="Exact Name">Exact Name</a> in <a href="#" class="city-link text-[#93c5fd] hover:underline cursor-pointer" data-city="City">City</a> (<a href="#" class="dossier-link text-slate-400 hover:text-white underline font-mono text-[14px] cursor-pointer" data-name="Exact Name">audit dossier</a>)
3. Link cities as: <a href="#" class="city-link text-[#93c5fd] hover:underline cursor-pointer" data-city="City">City</a>.
4. Keep answers focused, direct, and completely free of pompous fluff.`;"""

    if old_prompt in content:
        content = content.replace(old_prompt, new_prompt)
        print("Updated criticalSystemPrompt to simple plain language!")
    else:
        print("WARNING: Could not find old_prompt block!")

    # 5. Update Key Detection Message
    content = content.replace(
        "Ask me anything about art history, exhibition genealogies from <em>Beyond Objecthood</em>, e-flux institutional critique, or our 203 ethical sanctuaries.",
        "Ask me anything about art history, exhibitions, or places to visit."
    )

    # 6. Update ALL specialist & visitor response blocks
    # Let's replace the whole section from line 1978 to line 2530
    old_handlers_start = "        // 1. London Art Scene & Independent Spaces\n        if (q.includes('london')"
    old_handlers_end = "        // O. Fallback with helpful conversational guidance"

    idx_start = content.find(old_handlers_start)
    idx_end = content.find(old_handlers_end)

    if idx_start == -1 or idx_end == -1:
        print(f"ERROR finding handlers indices: start={idx_start}, end={idx_end}")
        return False

    # Find where the fallback block ends
    fallback_end_str = "      }}, 300);\n    }}\n\n    // Handle Input Send"
    idx_fallback_end = content.find(fallback_end_str, idx_end)
    if idx_fallback_end == -1:
        print("ERROR finding fallback_end_str!")
        return False

    new_handlers_code = """        // 1. London Art Scene & Independent Spaces
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
              London has two very different art worlds: the giant corporate museums on the Thames, and a network of independent galleries and artist-run spaces with clean funding.
            </p>
            <p class="text-slate-300">
              For 26 years, BP sponsored ${{formatInstLink(tate)}}, until artist groups like <em>Liberate Tate</em> and <em>BP or not BP?</em> staged creative protests (including carrying a real wind turbine blade into the Turbine Hall), pushing Tate to drop BP in 2016. In addition, protests by Nan Goldin's group P.A.I.N. forced London museums to take down the Sackler family name because of the opioid crisis.
            </p>
            <p class="text-slate-300">
              Here are great independent spaces to visit in London:
            </p>
            <p class="text-slate-300">
              - ${{formatInstLink(chis)}} in Bow: Free entry, known for commissioning brand-new work by artists like Lubaina Himid and Rachel Whiteread.<br>
              - ${{formatInstLink(camden)}} in North London: Free entry, quiet garden café, and ceramic and sculpture studios.<br>
              - ${{formatInstLink(white)}} in East London: Free entry, showed Picasso's <em>Guernica</em> in 1939 to support the Spanish Republic.<br>
              - ${{formatInstLink(serp)}} in Kensington Gardens: Free entry, famous for its summer architecture pavilion.<br>
              - ${{formatInstLink(volt)}} in Clapham, ${{formatInstLink(south)}} in Peckham, and ${{formatInstLink(gas)}} in Vauxhall. None of them accept oil or weapons sponsorships.
            </p>
          `);
          filterByCity('London', true, false);
          return;
        }}

        // 2. Beyond Objecthood: The Exhibition as a Critical Form Since 1968
        if (q.includes('beyond objecthood') || q.includes('voorhies') || (q.includes('objecthood') && (q.includes('fried') || q.includes('art') || q.includes('exhibition'))) || q.includes('exhibition as a critical form') || q.includes('exhibition as form')) {{
          appendCuratorMessage(`
            <p class="text-slate-200">
              In <em>Beyond Objecthood</em> (MIT Press, 2017), art historian James Voorhies explains how <strong>the exhibition itself became a work of art and a tool for critique</strong>.
            </p>
            <p class="text-slate-300">
              It started in 1967 when art critic Michael Fried wrote an essay called <em>Art and Objecthood</em>. Fried attacked Minimalist art (like Donald Judd's simple boxes) because viewers had to walk around them in a room over time. Fried called this 'theatricality' and argued that real art should be experienced in a single instant.
            </p>
            <p class="text-slate-300">
              Starting around 1968, artists did the exact opposite: they embraced theatricality and audience participation. Artists like Robert Smithson, Marcel Broodthaers, Fred Wilson, and Maria Eichhorn turned the whole exhibition into their medium. They showed that museums are never neutral white rooms—they are shaped by money, politics, and power.
            </p>
            <p class="text-slate-300">
              Voorhies also points out a big irony today: mega-museums have turned this kind of participatory art into tourist spectacles and selfie backdrops. Because of that, the most honest, experimental exhibitions have moved to independent galleries and artist-run spaces.
            </p>
          `);
          return;
        }}

        // 3. e-flux Journal, Hito Steyerl & Boris Groys
        if (q.includes('e-flux') || q.includes('steyerl') || q.includes('groys') || q.includes('vidokle') || q.includes('museum as factory') || q.includes('duty free art') || q.includes('duty-free art') || q.includes('freeport') || q.includes('post-democracy')) {{
          appendCuratorMessage(`
            <p class="text-slate-200">
              <em>e-flux journal</em> is an influential art publishing platform that explores how money, politics, and power affect the art world.
            </p>
            <p class="text-slate-300">
              Key ideas from its essays include:
            </p>
            <p class="text-slate-300">
              - <strong>Hito Steyerl – <em>Is a Museum a Factory?</em> (2009):</strong> She argues that modern museums act like 24/7 factories. Visitors are like unpaid workers: our attention, ticket purchases, and social media posts produce value that helps drive up nearby luxury real estate and museum prestige.<br>
              - <strong>Hito Steyerl – <em>Duty Free Art</em> (2015):</strong> She writes about 'freeports'—huge tax-free airport warehouses in Geneva and Singapore where ultra-wealthy investors store valuable art in crates just to avoid taxes and trade it like a financial asset, without the public ever seeing it.<br>
              - <strong>Boris Groys:</strong> He reminds us that public museums started during the French Revolution to take art away from kings and churches and open it up to everyone.<br>
              - <strong>Anton Vidokle:</strong> He critiques celebrity curators who take the spotlight away from the artists themselves.
            </p>
          `);
          return;
        }}

        // 4. Three Waves of Institutional Critique
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

        // 5. Claire Bishop & Radical Museology
        if (q.includes('claire bishop') || q.includes('radical museology') || q.includes('artificial hells') || q.includes('relational aesthetics') || q.includes('bourriaud')) {{
          appendCuratorMessage(`
            <p class="text-slate-200">
              Art historian Claire Bishop is known for critiquing how modern museums work and how audience participation is used:
            </p>
            <p class="text-slate-300">
              - In <em>Radical Museology</em> (2013), she compares flashy corporate museums (which rely on blockbuster shows, gift shops, and tourist crowds) with thoughtful civic museums (like the Van Abbemuseum in the Netherlands or Reina Sofía in Madrid) that use their collections to help us understand current political and social issues.
            </p>
            <p class="text-slate-300">
              - In <em>Artificial Hells</em> (2012), she critiques 'participatory art'. She points out that getting visitors to chat or sit on sofas in a gallery isn't necessarily radical—it often just creates a cozy illusion of community while avoiding deeper artistic and political questions.
            </p>
          `);
          return;
        }}

        // 6. Minimalism, Dia Beacon & Phenomenology
        if (q.includes('minimalism') || q.includes('dia beacon') || q.includes('judds') || q.includes('judd') || q.includes('richard serra') || q.includes('phenomenolog')) {{
          const dia = ALL_INSTITUTIONS.find(i => i.name.includes('Dia Beacon'));
          appendCuratorMessage(`
            <p class="text-slate-200">
              Minimalism started in the 1960s with artists like Donald Judd, Dan Flavin, and Richard Serra. Instead of paintings that depict a scene, they built simple, large geometric shapes from industrial materials like steel, aluminum, and plywood. The goal was for you to experience the physical space and light directly with your own body.
            </p>
            <p class="text-slate-300">
              The best place to see this is ${{formatInstLink(dia)}} in the Hudson Valley, New York. It sits in a huge former 1929 Nabisco box-printing factory lit entirely by natural daylight. You can walk inside Richard Serra's massive curved steel walls and see Donald Judd's wood and aluminum sculptures at full scale.
            </p>
            <p class="text-slate-300">
              How to get there: take the Metro-North Hudson Line train from Grand Central Station directly to Beacon. The museum is an easy 5-minute walk from the station.
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
              New York has some of the biggest museums in the world, but many have faced protests over their donors and board members:
            </p>
            <p class="text-slate-300">
              MoMA saw months of protests over board members tied to defense contractors and private prisons. The Whitney Museum saw artists pull their work until a tear-gas manufacturer stepped down from the board.
            </p>
            <p class="text-slate-300">
              Here are great places in New York with clean, independent funding:
            </p>
            <p class="text-slate-300">
              - ${{formatInstLink(dia)}} in the Hudson Valley: World-famous for Minimalist art, easy train ride from Grand Central.<br>
              - ${{formatInstLink(artsp)}} in Tribeca: Non-profit gallery championing experimental artists since 1972.<br>
              - ${{formatInstLink(sculp)}} in Long Island City, Queens: Innovative sculpture inside a historic trolley repair shop.<br>
              - ${{formatInstLink(kitch)}} and ${{formatInstLink(swiss)}} in the East Village.
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
              In Paris, strong public funding helps many museums stay open to the public without relying on private corporate boards:
            </p>
            <p class="text-slate-300">
              - ${{formatInstLink(ptok)}}: Europe's largest contemporary art space, known for bold, experimental shows and open until midnight.<br>
              - ${{formatInstLink(pomp)}}: Famous for its colorful inside-out architecture by Renzo Piano and Richard Rogers, with an incredible modern art collection.<br>
              - ${{formatInstLink(cart)}}: Contemporary art commissions in a glass building designed by Jean Nouvel.
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
              Berlin is known around the world for its artist-run spaces and strong public arts funding:
            </p>
            <p class="text-slate-300">
              - ${{formatInstLink(kw)}} in Mitte: Located in a former margarine factory, famous for cutting-edge shows and the Berlin Biennale.<br>
              - ${{formatInstLink(hkw)}} in Tiergarten: Focuses on international artists and global issues.<br>
              - ${{formatInstLink(grop)}}: A historic exhibition hall with free access to its ground-floor exhibitions.
            </p>
          `);
          filterByCity('Berlin', true, false);
          return;
        }}

        // =========================================================================
        // 🏛️ VISITOR DATA & AUDIT HANDLERS (Simple, Clear English)
        // =========================================================================

        // A. Visitor Data: Hours & Monday Openings
        if (q.includes('hour') || q.includes('schedule') || (q.includes('time') && (q.includes('open') || q.includes('visit'))) || q.includes('monday') || q.includes('weekend') || q.includes('late night') || q.includes('closed')) {{
          const targetInst = ALL_INSTITUTIONS.find(i => q.includes(i.name.toLowerCase()) || (i.aliases && i.aliases.some(a => q.includes(a.toLowerCase()))));
          if (targetInst) {{
            appendCuratorMessage(`
              <p class="text-slate-200">
                <strong>${{formatInstLink(targetInst)}}</strong> is open <strong>${{targetInst.opening_hours}}</strong>.
              </p>
              <p class="text-slate-300">
                Address: <strong>${{targetInst.address}}</strong> (${{targetInst.neighborhood}}).<br>
                How to get there: ${{targetInst.transit_tips}}.<br>
                Recommended visit time: about <strong>${{targetInst.visit_duration}}</strong> to see ${{targetInst.highlight}}.
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
                Most museums are closed on Mondays, but Culture Atlas has <strong>${{mondaySpaces.length}}</strong> spaces open on Mondays:
              </p>
              <p class="text-slate-300">
                In Paris, ${{formatInstLink(m1)}} is open every Monday and stays open until midnight. Near Copenhagen, ${{formatInstLink(m2)}} is open daily by the sea and easy to reach by train. In London, ${{formatInstLink(m3)}} is open with free entry. None of them accept funding from oil or defense companies.
              </p>
            `);
            return;
          }}

          const pTok = ALL_INSTITUTIONS.find(i => i.name.includes('Palais de Tokyo'));
          const louis = ALL_INSTITUTIONS.find(i => i.name.includes('Louisiana'));
          const sted = ALL_INSTITUTIONS.find(i => i.name.includes('Stedelijk'));
          appendCuratorMessage(`
            <p class="text-slate-200">
              Most galleries and art spaces are open <strong>Wednesday to Sunday, 11:00–18:00 or 12:00–18:00</strong>. Many close on Mondays and Tuesdays to set up new exhibitions.
            </p>
            <p class="text-slate-300">
              For late evenings, ${{formatInstLink(pTok)}} in Paris is open until midnight, while ${{formatInstLink(louis)}} and ${{formatInstLink(sted)}} are open late on weekdays. Click any dot on the map to see its exact opening times.
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
                To get to <strong>${{formatInstLink(targetInst)}}</strong>, take <strong>${{targetInst.transit_tips}}</strong>.
              </p>
              <p class="text-slate-300">
                Address: <strong>${{targetInst.address}}</strong> in ${{targetInst.neighborhood}}.<br>
                Hours: ${{targetInst.opening_hours}}. Plan for about ${{targetInst.visit_duration}}.
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
              Every space in Culture Atlas includes simple public transit directions. Many world-famous places are an easy train ride away:
            </p>
            <p class="text-slate-300">
              Take the Metro-North train from Grand Central right to ${{formatInstLink(dia)}}, take the coastal train from Copenhagen to ${{formatInstLink(louis)}}, or take a train and free park bicycle to ${{formatInstLink(kroll)}} in the Netherlands.
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
                <strong>Accessibility at ${{formatInstLink(targetInst)}}:</strong><br>
                ${{targetInst.accessibility}}.
              </p>
              <p class="text-slate-300">
                Companions and assistants get free entry. Getting there: ${{targetInst.transit_tips}}.
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
              All institutions in Culture Atlas have step-free access, elevators, wheelchairs to borrow, and free admission for companions.
            </p>
            <p class="text-slate-300">
              Great accessible spaces include ${{formatInstLink(serp)}} in London, ${{formatInstLink(aros)}} in Denmark, and ${{formatInstLink(mplus)}} in Hong Kong.
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
                <strong>Amenities at ${{formatInstLink(targetInst)}}:</strong><br>
                ${{targetInst.amenities}}.
              </p>
              <p class="text-slate-300">
                Highlight to see: <span class="text-amber-300/90">${{targetInst.highlight}}</span>. Open: ${{targetInst.opening_hours}}.
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
              Many of our mapped spaces have great cafés and bookshops:
            </p>
            <p class="text-slate-300">
              ${{formatInstLink(louis)}} in Denmark has an organic café looking over the sea. In Milan, ${{formatInstLink(prada)}} has <em>Bar Luce</em>, designed by filmmaker Wes Anderson. In London, ${{formatInstLink(camden)}} has a garden café, and ${{formatInstLink(tpg)}} in Soho has an incredible photography bookshop.
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
                The main highlight at <strong>${{formatInstLink(targetInst)}}</strong> is <span class="text-amber-300/90 font-medium">${{targetInst.highlight}}</span>.
              </p>
              <p class="text-slate-300">
                It focuses on ${{targetInst.curatorial_focus}} and is open ${{targetInst.opening_hours}}.
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
              Here are three unforgettable art landmarks you can visit:
            </p>
            <p class="text-slate-300">
              Olafur Eliasson's colorful rainbow glass skywalk at ${{formatInstLink(aros)}}, Richard Serra's giant steel sculptures at ${{formatInstLink(dia)}}, and 23 art pavilions set inside a Brazilian rainforest at ${{formatInstLink(inhotim)}}.
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
              Culture Atlas rates museums based on who funds them and who sits on their board:
            </p>
            <p class="text-slate-300">
              1. <strong>Public museums:</strong> Funded by public arts councils (like Arts Council England or DRAC in France) rather than private corporate sponsors, so they answer to the public. Examples: ${{formatInstLink(capc)}} and ${{formatInstLink(plugin)}}.<br>
              2. <strong>Artist-run spaces:</strong> Managed directly by artists, like ${{formatInstLink(chis)}}, giving artists freedom to experiment without corporate control.<br>
              3. <strong>Clean funding:</strong> Spaces that refuse or divested from oil, weapons, and private prison money.
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
              Culture Atlas has <strong>${{freeSpaces.length}}</strong> museums and galleries with completely free admission.
            </p>
            <p class="text-slate-300">
              Top free spaces include ${{formatInstLink(f1)}} in London, ${{formatInstLink(f2)}}, and ${{formatInstLink(f3)}} in Kensington Gardens. None of them charge admission, and none take oil or arms money.
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
              Culture Atlas maps <strong>${{artistSpaces.length}}</strong> artist-run spaces worldwide. Because they are run by artists, they can support new, experimental work without pressure from corporate donors.
            </p>
            <p class="text-slate-300">
              Standout artist-run spaces include ${{formatInstLink(a1)}}, ${{formatInstLink(a2)}}, and ${{formatInstLink(a3)}}.
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
              For years, oil companies like BP and Shell used museum sponsorships to polish their image ('artwashing'). Recently, artists and activists pressured museums to drop those deals.
            </p>
            <p class="text-slate-300">
              Every space in Culture Atlas has clean funding with zero oil or weapons money. Good examples include ${{formatInstLink(c1)}}, ${{formatInstLink(c2)}}, and ${{formatInstLink(c3)}}.
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
              We exclude museums whose board members have serious conflicts of interest:
            </p>
            <p class="text-slate-300">
              MoMA in New York saw protests over trustees invested in weapons companies and private prisons (its former chair Leon Black also resigned over payments to Jeffrey Epstein). The Whitney Museum saw artists pull their work until board member Warren Kanders, who owned a tear gas company, resigned.
            </p>
            <p class="text-slate-300">
              Instead, we feature spaces with clean funding, like ${{formatInstLink(dia)}}, ${{formatInstLink(sculp)}}, and ${{formatInstLink(serp)}}.
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
                Here are <strong>${{cityMatches.length}}</strong> museums and galleries in <a href="#" class="city-link font-semibold text-white hover:text-[#60a5fa] underline cursor-pointer" data-city="${{escapeHtml(targetCity)}}">${{escapeHtml(targetCity)}}</a> with clean funding:
              </p>
              <p class="text-slate-300">
                Highlights include ${{formatInstLink(c1, {{noCity: true}})}}${{c2 ? `, ${{formatInstLink(c2, {{noCity: true}})}}` : ''}}${{c3 ? `, and ${{formatInstLink(c3, {{noCity: true}})}}` : ''}}. None of them accept oil or weapons sponsorships.
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
                We have <strong>${{countryMatches.length}}</strong> spaces mapped in <strong>${{escapeHtml(matchedCountry.name)}}</strong> with clean funding.
              </p>
              <p class="text-slate-300">
                Top places to visit include ${{formatInstLink(co1)}}${{co2 ? `, ${{formatInstLink(co2)}}` : ''}}${{co3 ? `, and ${{formatInstLink(co3)}}` : ''}}.
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
              <strong>${{formatInstLink(instMatch, {{noCity: false}})}}</strong> (${{instMatch.neighborhood}}), founded in ${{instMatch.year_founded}}.
            </p>
            <p class="text-slate-300">
              - <strong>Admission:</strong> ${{instMatch.admission_policy}} (${{instMatch.admission_details}})<br>
              - <strong>Hours:</strong> ${{instMatch.opening_hours}}<br>
              - <strong>Highlight:</strong> <span class="text-amber-300/90 font-medium">${{instMatch.highlight}}</span><br>
              - <strong>Transit:</strong> ${{instMatch.transit_tips}}<br>
              - <strong>Governance:</strong> ${{instMatch.governance_type}} · ${{instMatch.ethical_safeguard}}
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
              Here are two great art spaces to check out:
            </p>
            <p class="text-slate-300">
              - ${{formatInstLink(pick1)}}<br>
              - ${{formatInstLink(pick2)}}
            </p>
            <p class="text-slate-300">
              Both have clean funding and show exciting contemporary art.
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
            I can help you find museums and art spaces across <strong>35 countries and 133 cities</strong> that have clean funding.
          </p>
          <p class="text-slate-300">
            Ask me about cities like <a href="#" class="city-link text-[#93c5fd] hover:underline cursor-pointer" data-city="London">London</a>, <a href="#" class="city-link text-[#93c5fd] hover:underline cursor-pointer" data-city="Paris">Paris</a>, or <a href="#" class="city-link text-[#93c5fd] hover:underline cursor-pointer" data-city="New York">New York</a>, how to get to places like ${{formatInstLink(dia)}} or ${{formatInstLink(louis)}}, or questions about art history and exhibitions.
          </p>
          <p class="text-[#93c5fd]">
            Which city or kind of art are you interested in?
          </p>
        `);"""

    content = content[:idx_start] + new_handlers_code + content[idx_fallback_end:]
    print("Replaced all specialist and visitor handlers with simple, plain English!")

    # 7. Update City click / Country notification
    content = content.replace(
        "home to <strong>${{cityMatches.length}}</strong> verified ethical cultural sanctuaries.\n          </p>\n          <p class=\"text-slate-300\">\n            Standout spaces here include ${{topInsts}}. Each operates with transparent public governance and clean underwriting without fossil-fuel or defense sponsorship.",
        "home to <strong>${{cityMatches.length}}</strong> spaces with clean funding.\n          </p>\n          <p class=\"text-slate-300\">\n            Highlights include ${{topInsts}}. None of them accept oil or defense sponsorships."
    )

    content = content.replace(
        "Culture Atlas tracks <strong>${{countryMatches.length}}</strong> cultural institutions prioritizing public accountability and artistic autonomy.\n          </p>\n          <p class=\"text-slate-300\">\n            Exemplary spaces to explore include ${{topInsts}}.",
        "Culture Atlas has <strong>${{countryMatches.length}}</strong> spaces with clean funding.\n          </p>\n          <p class=\"text-slate-300\">\n            Top places to explore include ${{topInsts}}."
    )

    # 8. Update provider tip
    content = content.replace(
        "across all 203 mapped sanctuaries.",
        "across all 203 mapped spaces."
    )

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("Successfully patched build_conversational_atlas.py!")

if __name__ == "__main__":
    patch_atlas()
