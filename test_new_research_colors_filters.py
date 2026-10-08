import os
import subprocess
import json
import tempfile
import html as html_lib

def run_tests():
    index_path = "/Users/polinavasilyeva/.gemini/antigravity/scratch/sponsor-atlas/index.html"
    assert os.path.exists(index_path), "index.html must exist"

    with open(index_path, "r", encoding="utf-8") as f:
        html = f.read()

    test_script = """
    <script>
    // Stub fetch so headless chrome does not wait for external tiles
    const origFetch = window.fetch;
    window.fetch = async (url, opts) => {
      const urlStr = typeof url === 'string' ? url : (url && url.url ? url.url : '');
      if (urlStr.includes('.pbf') || urlStr.includes('openfreemap') || urlStr.includes('tile')) {
        return new Response(new Uint8Array(0), { status: 200 });
      }
      return origFetch(url, opts);
    };

    window.addEventListener('load', async () => {
      const results = [];
      function assert(name, condition, extra = '') {
        results.push({ name, pass: !!condition, extra });
      }

      try {
        // =========================================================================
        // 1. DATASETS LOADED
        // =========================================================================
        const allLen = window.ALL_INSTITUTIONS ? window.ALL_INSTITUTIONS.length : 0;
        const arLen = window.ACADEMIC_RESEARCH ? window.ACADEMIC_RESEARCH.length : 0;
        assert('Total institutions loaded >= 1000', allLen >= 1000, `Found: ${allLen}`);
        assert('Academic studies loaded >= 80', arLen >= 80, `Found: ${arLen}`);

        // =========================================================================
        // 2. CLEAN FUNDING FILTER ON ON LOAD
        // =========================================================================
        const selectedTiers = Array.from(window.selectedTierFilter || []);
        assert('selectedTierFilter contains only Tier A on load', selectedTiers.length === 1 && selectedTiers[0] === 'A', JSON.stringify(selectedTiers));

        const filteredLen = window.filteredList ? window.filteredList.length : 0;
        const cleanCount = window.ALL_INSTITUTIONS.filter(i => i.tier === 'A').length;
        assert('filteredList matches Tier A clean count on load', filteredLen === cleanCount, `Filtered: ${filteredLen}, Clean count: ${cleanCount}`);

        const cleanPill = document.querySelector('.globe-filter-pill[data-type="tier"][data-value="A"]');
        assert('Clean funding pill exists in header bar', !!cleanPill);
        if (cleanPill) {
          const isPillActive = cleanPill.className.includes('bg-[#059669]') || cleanPill.className.includes('border-[#10b981]');
          assert('Clean funding pill is active on load', isPillActive, cleanPill.className);
        }

        // =========================================================================
        // 3. TOGGLING TO FLAGGED SPACES
        // =========================================================================
        const flaggedPill = document.querySelector('.globe-filter-pill[data-type="tier"][data-value="B"]');
        assert('Flagged spaces pill exists in header bar', !!flaggedPill);
        if (flaggedPill) {
          flaggedPill.click();
          await new Promise(r => setTimeout(r, 100));

          const currentTiers = Array.from(window.selectedTierFilter || []);
          assert('Clicking flagged pill sets selectedTierFilter to B', currentTiers.length === 1 && currentTiers[0] === 'B', JSON.stringify(currentTiers));

          const flaggedCount = window.ALL_INSTITUTIONS.filter(i => i.tier === 'B').length;
          assert('filteredList reflects flagged spaces', window.filteredList.length === flaggedCount, `Filtered: ${window.filteredList.length}, Flagged count: ${flaggedCount}`);
        }

        // =========================================================================
        // 4. CARBON COLORS FOR FLAGGED INSTITUTIONS (NO RED, NO YELLOW)
        // =========================================================================
        const flaggedInst = window.ALL_INSTITUTIONS.find(i => i.tier === 'B');
        assert('Found flagged institution for dossier test', !!flaggedInst, flaggedInst ? flaggedInst.name : '');
        if (flaggedInst) {
          window.atlasOpenDossier(flaggedInst.name);
          const detailBody = document.getElementById('detailBody');
          assert('Dossier opens for flagged institution', detailBody && detailBody.innerHTML.length > 50);

          const htmlContent = detailBody.innerHTML.toLowerCase();

          // Assert IBM Carbon purple palette is present
          assert('Dossier uses Carbon Purple #be95ff for flagged badge', htmlContent.includes('#be95ff'));
          assert('Dossier uses Carbon Purple border #8a3ffc', htmlContent.includes('#8a3ffc'));

          // Assert NO red and NO yellow
          const hasRedRose = htmlContent.includes('rose-') || htmlContent.includes('#da1e28') || htmlContent.includes('#ef4444') || htmlContent.includes('#280c12');
          const hasAmberYellow = htmlContent.includes('amber-') || htmlContent.includes('#f1c21b') || htmlContent.includes('#eab308') || htmlContent.includes('#26180a') || htmlContent.includes('yellow-');
          assert('Strictly NO red used for flagged entity dossier', !hasRedRose, 'Found red tokens in dossier');
          assert('Strictly NO yellow used for flagged entity dossier', !hasAmberYellow, 'Found yellow tokens in dossier');
        }

        // Close drawer
        const closeBtn = document.getElementById('closeDetailBtn');
        if (closeBtn) closeBtn.click();

        // =========================================================================
        // 5. ACADEMIC RESEARCH LIBRARY MODAL
        // =========================================================================
        const arModal = document.getElementById('academicResearchModal');
        assert('academicResearchModal exists in DOM', !!arModal);

        if (typeof window.openAcademicResearchModal === 'function') {
          window.openAcademicResearchModal();
          assert('openAcademicResearchModal displays modal', !arModal.classList.contains('hidden'));

          const papersList = document.getElementById('arPapersList');
          assert('Academic papers list is populated', papersList && papersList.children.length > 0, `Papers rendered: ${papersList ? papersList.children.length : 0}`);

          // Test search filtering in academic modal
          const searchInput = document.getElementById('arSearchInput');
          if (searchInput) {
            searchInput.value = 'fossil';
            searchInput.dispatchEvent(new Event('input', { bubbles: true }));
            await new Promise(r => setTimeout(r, 100));

            const filteredCount = papersList.children.length;
            assert('Search input filters academic papers', filteredCount > 0 && filteredCount < arLen, `Filtered count for "fossil": ${filteredCount}`);
          }

          if (typeof window.closeAcademicResearchModal === 'function') {
            window.closeAcademicResearchModal();
            assert('closeAcademicResearchModal hides modal', arModal.classList.contains('hidden'));
          }
        }

      } catch (err) {
        assert('JavaScript Execution Exception', false, err.stack || err.toString());
      }

      const out = document.createElement('div');
      out.id = 'test-results-output';
      out.setAttribute('data-results', JSON.stringify(results));
      document.body.appendChild(out);
    });
    </script>
    """

    harness_html = html.replace("</body>", f"{test_script}</body>")
    temp_file = os.path.join(tempfile.gettempdir(), "test_new_research_colors_filters_harness.html")
    with open(temp_file, "w", encoding="utf-8") as f:
        f.write(harness_html)

    chrome_bin = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

    print("--- RUNNING NEW RESEARCH, COLORS & FILTERS TEST SUITE ---")
    cmd = [
        chrome_bin,
        "--headless=new",
        "--dump-dom",
        "--window-size=1280,800",
        "--virtual-time-budget=6000",
        f"file://{temp_file}"
    ]
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=60)
    marker = 'id="test-results-output" data-results="'
    if marker not in proc.stdout:
        print("ERROR: Test marker not found in output. Stderr:")
        print(proc.stderr[:1000])
        return False

    results = json.loads(html_lib.unescape(proc.stdout.split(marker)[1].split('"')[0]))
    all_passed = True
    for r in results:
        status = "PASS" if r['pass'] else "FAIL"
        if not r['pass']:
            all_passed = False
        extra = f" ({r['extra']})" if r.get('extra') else ""
        print(f"[{status}] {r['name']}{extra}")

    if all_passed:
        print("\nALL NEW RESEARCH, COLORS & FILTERS TESTS PASSED!")
    return all_passed

if __name__ == "__main__":
    success = run_tests()
    if not success:
        exit(1)
