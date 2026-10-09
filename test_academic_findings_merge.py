import os
import subprocess
import json
import tempfile
import html as html_lib

def run_tests():
    print("--- RUNNING ACADEMIC FINDINGS MERGE TEST SUITE ---")
    index_path = "/Users/polinavasilyeva/.gemini/antigravity/scratch/sponsor-atlas/index.html"
    assert os.path.exists(index_path), "index.html must exist"

    with open(index_path, "r", encoding="utf-8") as f:
        html = f.read()

    test_script = """
    <script>
    window.requestAnimationFrame = () => 1;
    window.cancelAnimationFrame = () => {};
    window.fetch = async (url, opts) => {
      return new Response("{}", { status: 200, headers: { 'Content-Type': 'application/json' } });
    };

    const runMergeTests = async () => {
      const results = [];
      const assert = (name, cond, details = '') => {
        results.push({ name, pass: !!cond, details });
        if (!cond) console.error('[FAIL]', name, details);
        else console.log('[PASS]', name);
      };

      try {
        // 1. Dataset Verification
        const allSpacesCount = typeof ALL_INSTITUTIONS !== 'undefined' ? ALL_INSTITUTIONS.length : 0;
        const academicCount = typeof ACADEMIC_RESEARCH !== 'undefined' ? ACADEMIC_RESEARCH.length : 0;
        const totalExpected = allSpacesCount + academicCount;
        assert('ALL_INSTITUTIONS loaded (1074 spaces)', allSpacesCount === 1074, `Got: ${allSpacesCount}`);
        assert('ACADEMIC_RESEARCH loaded (112 studies)', academicCount === 112, `Got: ${academicCount}`);
        assert('Total findings = 1186', totalExpected === 1186, `Got: ${totalExpected}`);

        // 2. getAcademicResearchAsFindings helper
        assert('getAcademicResearchAsFindings is defined', typeof getAcademicResearchAsFindings === 'function');
        const academicFindings = getAcademicResearchAsFindings();
        assert('getAcademicResearchAsFindings returns 112 findings', academicFindings.length === 112, `Got: ${academicFindings.length}`);
        assert('First study has isAcademicStudy flag', academicFindings[0] && academicFindings[0].isAcademicStudy === true);

        // 3. Default "All Findings" contains both institutions and academic studies
        selectedTierFilter = new Set(['A', 'B', 'U', 'ACADEMIC']);
        selectedCityFilter = 'all';
        selectedCountryFilter = 'all';
        selectedCategoryFilter = 'all';
        searchQuery = '';
        applyFilters();

        assert('filteredList has 1186 findings by default', filteredList.length === 1186, `Got: ${filteredList.length}`);
        const spacesInList = filteredList.filter(i => !i.isAcademicStudy);
        const studiesInList = filteredList.filter(i => i.isAcademicStudy);
        assert('Both spaces and studies are in default list', spacesInList.length === 1074 && studiesInList.length === 112, `Spaces: ${spacesInList.length}, Studies: ${studiesInList.length}`);

        // 4. Rendered DOM list contains both regular inst-card and academic-card
        const container = document.getElementById('institutionsListContainer');
        assert('institutionsListContainer exists', !!container);
        const academicCards = container ? container.querySelectorAll('.academic-card') : [];
        assert('DOM renders academic cards', academicCards.length === 112, `Rendered: ${academicCards.length}`);
        const firstAcadCard = academicCards[0];
        assert('Academic card has Academic Study badge', firstAcadCard && firstAcadCard.textContent.includes('Academic Study'));
        assert('Academic card has Ask Curator button', firstAcadCard && firstAcadCard.querySelector('.academic-ask-btn'));

        // 5. Search filtering matches both spaces and academic studies
        const searchInput = document.getElementById('searchInput');
        assert('searchInput exists', !!searchInput);

        // Search for academic author "Velthuis"
        searchQuery = 'velthuis';
        applyFilters();
        const velthuisMatches = filteredList.filter(i => i.isAcademicStudy);
        assert('Search by author "Velthuis" finds study', velthuisMatches.length > 0 && velthuisMatches[0].name.toLowerCase().includes('fragility'));

        // Search for space "Chisenhale"
        searchQuery = 'chisenhale';
        applyFilters();
        const chisenhaleMatches = filteredList.filter(i => !i.isAcademicStudy);
        assert('Search by space name "Chisenhale" finds institution', chisenhaleMatches.length > 0 && chisenhaleMatches[0].name.toLowerCase().includes('chisenhale'));

        // Reset search
        searchQuery = '';
        applyFilters();

        // 6. User filter: Academic Studies chip
        const catFilterAcademicBtn = document.getElementById('catFilterAcademicBtn');
        assert('catFilterAcademicBtn exists in catalog modal', !!catFilterAcademicBtn);
        if (catFilterAcademicBtn) {
          catFilterAcademicBtn.click();
          await new Promise(r => setTimeout(r, 50));
        }
        assert('Filtering by Academic Studies sets filteredList to 112 studies', filteredList.length === 112 && filteredList.every(i => i.isAcademicStudy), `Count: ${filteredList.length}`);

        // 7. User filter: Clean Spaces chip
        const catFilterCleanBtn = document.getElementById('catFilterCleanBtn');
        assert('catFilterCleanBtn exists in catalog modal', !!catFilterCleanBtn);
        if (catFilterCleanBtn) {
          catFilterCleanBtn.click();
          await new Promise(r => setTimeout(r, 50));
        }
        assert('Filtering by Clean Spaces sets filteredList to 441 clean spaces', filteredList.length === 441 && filteredList.every(i => i.tier === 'A'), `Count: ${filteredList.length}`);

        // 8. User filter: Flagged chip
        const catFilterFlaggedBtn = document.getElementById('catFilterFlaggedBtn');
        assert('catFilterFlaggedBtn exists in catalog modal', !!catFilterFlaggedBtn);
        if (catFilterFlaggedBtn) {
          catFilterFlaggedBtn.click();
          await new Promise(r => setTimeout(r, 50));
        }
        assert('Filtering by Flagged Spaces sets filteredList to 403 flagged spaces', filteredList.length === 403 && filteredList.every(i => i.tier === 'B'), `Count: ${filteredList.length}`);

        // 9. User filter: Back to All Findings
        const catFilterAllBtn = document.getElementById('catFilterAllBtn');
        assert('catFilterAllBtn exists in catalog modal', !!catFilterAllBtn);
        if (catFilterAllBtn) {
          catFilterAllBtn.click();
          await new Promise(r => setTimeout(r, 50));
        }
        assert('Clicking All Findings restores all 1186 findings', filteredList.length === 1186, `Count: ${filteredList.length}`);

        // 10. Globe canvas draw projection safety (no NaN or exception with merged findings)
        let canvasError = false;
        try {
          if (typeof render === 'function') {
            render();
          }
        } catch (e) {
          canvasError = true;
        }
        assert('Canvas globe projection runs safely without error on merged findings', !canvasError);

        // 11. Top catalog button and Work menu catalog button existence and labels
        const topCatalogBtn = document.getElementById('topCatalogBtn');
        const mobileCatalogBtn = document.getElementById('mobileCatalogBtn');
        const workMenuCatalogBtn = document.getElementById('workMenuCatalogBtn');
        assert('topCatalogBtn exists and shows 1186 findings', topCatalogBtn && topCatalogBtn.textContent.includes('1186'));
        assert('mobileCatalogBtn exists and has Findings label', mobileCatalogBtn && mobileCatalogBtn.textContent.includes('Findings'));
        assert('workMenuCatalogBtn exists and shows 1186 findings', workMenuCatalogBtn && workMenuCatalogBtn.textContent.includes('1186'));

      } catch (err) {
        results.push({ name: 'Exception caught', pass: false, details: err.stack || err.toString() });
      }

      const div = document.createElement('div');
      div.id = 'merge-test-results';
      div.setAttribute('data-results', JSON.stringify(results));
      document.body.appendChild(div);
    };

    if (document.readyState === 'complete') { setTimeout(runMergeTests, 100); } else { window.addEventListener('load', runMergeTests); }
    </script>
    """

    harness_html = html.replace("</body>", f"{test_script}</body>")
    temp_file = os.path.join(tempfile.gettempdir(), "test_academic_findings_merge.html")
    with open(temp_file, "w", encoding="utf-8") as f:
        f.write(harness_html)

    chrome_cmd = [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        "--dump-dom",
        "--virtual-time-budget=10000",
        f"file://{temp_file}"
    ]

    try:
        proc = subprocess.run(chrome_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=30)
        stdout = proc.stdout

        marker = 'id="merge-test-results" data-results="'
        if marker not in stdout:
            print("[FAIL] Test output marker not found in headless Chrome output!")
            print(stdout[:500])
            return False

        raw_json = stdout.split(marker)[1].split('"')[0]
        raw_json = html_lib.unescape(raw_json)
        results = json.loads(raw_json)

        total = len(results)
        passed = sum(1 for r in results if r['pass'])
        failed = sum(1 for r in results if not r['pass'])

        print(f"\nRESULTS: {passed}/{total} checks PASSED.")
        for r in results:
            status = "PASS" if r['pass'] else "FAIL"
            print(f"[{status}] {r['name']}")
            if not r['pass']:
                print(f"       Details: {r.get('details', '')}")

        if failed > 0:
            return False
        else:
            print("\n🎉 ALL ACADEMIC FINDINGS MERGE CHECKS PASSED PERFECTLY!")
            return True
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)

if __name__ == '__main__':
    ok = run_tests()
    if not ok:
        exit(1)
