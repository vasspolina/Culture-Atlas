import re

def update_widget():
    with open("build_conversational_widget.py", "r", encoding="utf-8") as f:
        src = f.read()

    # 1. Update wInquiryCarousel with data-filter attributes
    old_carousel_pattern = r'(<div id="wInquiryCarousel".*?)(<div class="p-2 bg-\[#171717\] shrink-0)'
    new_carousel = """<div id="wInquiryCarousel" class="px-3 py-1.5 border-t border-[#262626] bg-[#171717] flex items-center gap-1.5 overflow-x-auto custom-scroll text-[14px] whitespace-nowrap shrink-0">
        <button class="w-inquiry px-3 py-0.5 rounded-full border border-[#1b3324] bg-[#0c1f15] text-[#6ee7b7] hover:border-[#10b981] transition active:scale-95" data-filter="free" data-chip-color="green" data-query="Which cultural spaces offer always free admission?">
          🎟️ Free Admission
        </button>
        <button class="w-inquiry px-3 py-0.5 rounded-full border border-[#232a3c] bg-[#101522] text-[#93c5fd] hover:border-[#3b82f6] transition active:scale-95" data-filter="monday" data-chip-color="blue" data-query="What are typical museum opening hours and which institutions are open on Mondays?">
          🕒 Hours & Mondays
        </button>
        <button class="w-inquiry px-3 py-0.5 rounded-full border border-[#232a3c] bg-[#101522] text-[#93c5fd] hover:border-[#3b82f6] transition active:scale-95" data-filter="transit" data-chip-color="blue" data-query="How do I get to destination museums like Dia Beacon or Louisiana by public transit?">
          🚇 Public Transit Tips
        </button>
        <button class="w-inquiry px-3 py-0.5 rounded-full border border-[#232a3c] bg-[#101522] text-[#cbd5e1] hover:border-[#3b82f6] transition active:scale-95" data-filter="accessibility" data-chip-color="slate" data-query="Which museums offer step-free wheelchair accessibility and inclusive facilities?">
          ♿ Accessibility
        </button>
        <button class="w-inquiry px-3 py-0.5 rounded-full border border-[#232a3c] bg-[#101522] text-[#cbd5e1] hover:border-[#3b82f6] transition active:scale-95" data-filter="amenities" data-chip-color="slate" data-query="Which institutions feature outstanding cafés, sculpture gardens, and art bookshops?">
          ☕ Cafés & Bookshops
        </button>
        <button class="w-inquiry px-3 py-0.5 rounded-full border border-[#232a3c] bg-[#101522] text-[#93c5fd] hover:border-[#3b82f6] transition active:scale-95" data-filter="ethical" data-chip-color="blue" data-query="What makes an institution ethically funded and what is Tier A?">
          🏛️ Ethical Criteria
        </button>
        <button class="w-inquiry px-3 py-0.5 rounded-full border border-[#232a3c] bg-[#101522] text-[#cbd5e1] hover:border-[#3b82f6] transition active:scale-95" data-filter="artist_run" data-chip-color="slate" data-query="Recommend independent artist-run centers and grassroots kunsthalles">
          🎨 Artist-Run Spaces
        </button>
        <button class="w-inquiry px-3 py-0.5 rounded-full border border-[#1b3324] bg-[#0c1f15] text-[#6ee7b7] hover:border-[#10b981] transition active:scale-95" data-filter="fossil_free" data-chip-color="green" data-query="Show institutions free from fossil fuels and defense sponsors">
          🌿 Fossil & defense-free spaces
        </button>
        <button class="w-inquiry px-3 py-0.5 rounded-full border border-[#232a3c] bg-[#101522] text-[#93c5fd] hover:border-[#3b82f6] transition active:scale-95" data-filter="london" data-chip-color="blue" data-query="Tell me about London's art scene, independent spaces, and divestment history">
          📍 London guide
        </button>
        <button class="w-inquiry px-3 py-0.5 rounded-full border border-[#232a3c] bg-[#101522] text-[#93c5fd] hover:border-[#3b82f6] transition active:scale-95" data-filter="nyc" data-chip-color="blue" data-query="Tell me about New York's art scene and independent spaces">
          📍 New York guide
        </button>
        <button class="w-inquiry px-3 py-0.5 rounded-full border border-[#3b2b11] bg-[#221807] text-[#fcd34d] hover:border-[#f59e0b] transition active:scale-95" data-filter="moma" data-chip-color="amber" data-query="Why is MoMA excluded from Culture Atlas?">
          ⚠️ Why MoMA is excluded
        </button>
      </div>\n      """

    src = re.sub(old_carousel_pattern, new_carousel + r'\2', src, flags=re.DOTALL)

    # 2. Update render() in widget to filter DATA by wCategoryFilter
    old_dots_pattern = """      // Dots
      visibleDots = [];
      DATA.forEach(inst => {"""

    new_dots_pattern = """      // Dots
      visibleDots = [];
      const filteredData = DATA.filter(inst => {
        if (wCategoryFilter === 'all') return true;
        if (wCategoryFilter === 'free') return (inst.admission_policy || '').toLowerCase().includes('free');
        if (wCategoryFilter === 'monday') {
          const h = (inst.opening_hours || '').toLowerCase();
          return !h.includes('closed mon') && (h.includes('daily') || h.includes('mon'));
        }
        if (wCategoryFilter === 'transit') return inst.transit_tips && inst.transit_tips.length > 5;
        if (wCategoryFilter === 'accessibility') {
          const a = (inst.accessibility || '').toLowerCase();
          return a.includes('step-free') || a.includes('wheelchair') || a.includes('elevator') || a.includes('accessible');
        }
        if (wCategoryFilter === 'amenities') {
          const am = (inst.amenities || '').toLowerCase();
          return am.includes('caf') || am.includes('book') || am.includes('garden') || am.includes('dining');
        }
        if (wCategoryFilter === 'ethical') return inst.tier === 'A' || inst.governance_type.includes('Civic') || inst.governance_type.includes('Public');
        if (wCategoryFilter === 'artist_run') return (inst.governance_type || '').toLowerCase().includes('artist');
        if (wCategoryFilter === 'fossil_free') {
          const s = (inst.ethical_safeguard || '').toLowerCase();
          return inst.tier === 'A' || s.includes('divest') || s.includes('fossil') || s.includes('clean');
        }
        if (wCategoryFilter === 'london') return inst.city.toLowerCase() === 'london';
        if (wCategoryFilter === 'nyc') return inst.city.toLowerCase().includes('new york') || inst.city.toLowerCase().includes('beacon');
        return true;
      });

      filteredData.forEach(inst => {"""

    if old_dots_pattern in src:
        src = src.replace(old_dots_pattern, new_dots_pattern, 1)
        print("Updated dot filtering in widget render()")
    else:
        print("Warning: old_dots_pattern not found in widget")

    # 3. Add wCategoryFilter variable and click handler in widget
    old_click_listener = """    document.querySelectorAll('.w-inquiry').forEach(b => {
      b.addEventListener('click', () => {
        const q = b.getAttribute('data-query');
        appendWUser(q);
        handleWQuery(q);
      });
    });"""

    new_click_listener = """    let wCategoryFilter = 'all';

    function updateWFilterChipsUI() {
      document.querySelectorAll('.w-inquiry').forEach(b => {
        const f = b.getAttribute('data-filter');
        if (f && f === wCategoryFilter && wCategoryFilter !== 'all') {
          b.classList.add('border-[#38bdf8]', 'ring-1', 'ring-[#38bdf8]', 'bg-[#0c1a2e]', 'text-white', 'shadow-[0_0_10px_rgba(56,189,248,0.5)]');
          b.classList.remove('border-[#1b3324]', 'border-[#232a3c]', 'border-[#3b2b11]', 'bg-[#0c1f15]', 'bg-[#101522]', 'bg-[#221807]', 'text-[#6ee7b7]', 'text-[#93c5fd]', 'text-[#cbd5e1]', 'text-[#fcd34d]');
        } else {
          b.classList.remove('border-[#38bdf8]', 'ring-1', 'ring-[#38bdf8]', 'bg-[#0c1a2e]', 'text-white', 'shadow-[0_0_10px_rgba(56,189,248,0.5)]');
          const col = b.getAttribute('data-chip-color');
          if (col === 'green') {
            b.classList.add('border-[#1b3324]', 'bg-[#0c1f15]', 'text-[#6ee7b7]');
          } else if (col === 'amber') {
            b.classList.add('border-[#3b2b11]', 'bg-[#221807]', 'text-[#fcd34d]');
          } else if (col === 'blue') {
            b.classList.add('border-[#232a3c]', 'bg-[#101522]', 'text-[#93c5fd]');
          } else {
            b.classList.add('border-[#232a3c]', 'bg-[#101522]', 'text-[#cbd5e1]');
          }
        }
      });
    }

    document.querySelectorAll('.w-inquiry').forEach(b => {
      b.addEventListener('click', () => {
        const f = b.getAttribute('data-filter') || 'all';
        const q = b.getAttribute('data-query');

        if (wCategoryFilter === f) {
          wCategoryFilter = 'all';
          targetRadius = baseRadius;
        } else {
          wCategoryFilter = f;
          if (f === 'london') {
            flyTo(-0.1278, 51.5074);
            targetRadius = baseRadius * 4.0;
          } else if (f === 'nyc') {
            flyTo(-73.9776, 40.7614);
            targetRadius = baseRadius * 4.0;
          }
        }

        updateWFilterChipsUI();

        if (q && wCategoryFilter !== 'all') {
          appendWUser(q);
          handleWQuery(q);
        }
      });
    });"""

    if old_click_listener in src:
        src = src.replace(old_click_listener, new_click_listener, 1)
        print("Updated w-inquiry listener in widget")
    else:
        print("Warning: old_click_listener not found in widget")

    with open("build_conversational_widget.py", "w", encoding="utf-8") as f:
        f.write(src)
    print("Saved build_conversational_widget.py with map filter support!")

if __name__ == "__main__":
    update_widget()
