import os
import subprocess
import json
import tempfile
import html as html_lib
import sys

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
        // 1. Verify topBrandLogoBtn exists and is interactive
        const logoBtn = document.getElementById('topBrandLogoBtn');
        assert('topBrandLogoBtn exists in DOM', !!logoBtn);
        assert('topBrandLogoBtn has title attribute', logoBtn && logoBtn.getAttribute('title') === 'Reset Globe View');
        assert('topBrandLogoBtn contains CULTURE ATLAS', logoBtn && logoBtn.textContent.includes('CULTURE ATLAS'));
        assert('topBrandLogoBtn contains clean spaces badge', logoBtn && logoBtn.textContent.includes('CLEAN SPACES'));
        assert('resetGlobeView function is globally defined', typeof window.resetGlobeView === 'function');

        // 2. Test resetting when in City Street View
        openCityStreetView('Addis Ababa');
        assert('City street view is active before logo click', isCityStreetViewActive === true);
        const mapContainer = document.getElementById('cityMapContainer');
        assert('cityMapContainer is visible', mapContainer && !mapContainer.classList.contains('hidden'));

        // Click the logo to reset
        logoBtn.click();
        assert('isCityStreetViewActive is false after logo click', isCityStreetViewActive === false);
        assert('cityMapContainer has hidden class after logo click', mapContainer && mapContainer.classList.contains('hidden'));
        assert('targetRadius reset to baseRadius', targetRadius === baseRadius, `targetRadius: ${targetRadius}, baseRadius: ${baseRadius}`);
        assert('isAutoSpinning restored to true', isAutoSpinning === true);

        // 3. Test resetting when search and country filters are active
        selectedCountryFilter = 'Japan';
        selectedCityFilter = 'Tokyo';
        searchQuery = 'contemporary';
        if (searchInput) searchInput.value = 'contemporary';
        targetRadius = baseRadius * 3; // zoomed in

        logoBtn.click();
        assert('selectedCountryFilter reset to all', selectedCountryFilter === 'all');
        assert('selectedCityFilter reset to all', selectedCityFilter === 'all');
        assert('searchQuery reset to empty', searchQuery === '');
        if (searchInput) assert('searchInput value reset to empty', searchInput.value === '');
        assert('targetRadius reset back to baseRadius after zoom', targetRadius === baseRadius);

        // 4. Test resetting when an institution dossier drawer is open
        const sampleInst = ALL_INSTITUTIONS[0];
        selectInstitution(sampleInst, false);
        openDossier(sampleInst);
        const drawer = document.getElementById('detailDrawer');
        assert('detailDrawer is open before logo click', drawer && !drawer.classList.contains('hidden'));
        assert('selectedInstitution is set before logo click', selectedInstitution !== null);

        logoBtn.click();
        assert('detailDrawer is closed after logo click', drawer && drawer.classList.contains('hidden'));
        assert('selectedInstitution is null after logo click', selectedInstitution === null);

        // 5. Test topResetBtn triggers the same reset
        openCityStreetView('London');
        assert('City street view active before topResetBtn click', isCityStreetViewActive === true);
        const resetBtn = document.getElementById('topResetBtn');
        assert('topResetBtn exists', !!resetBtn);
        resetBtn.click();
        assert('isCityStreetViewActive is false after topResetBtn click', isCityStreetViewActive === false);
        assert('cityMapContainer hidden after topResetBtn click', mapContainer && mapContainer.classList.contains('hidden'));

      } catch (err) {
        results.push({ name: 'Exception caught', pass: false, extra: err.toString() });
      }

      const div = document.createElement('div');
      div.id = 'test-results-output';
      div.setAttribute('data-results', JSON.stringify(results));
      document.body.appendChild(div);
    });
    </script>
    """

    harness_html = html.replace("</body>", f"{test_script}</body>")
    temp_file = os.path.join(tempfile.gettempdir(), "test_logo_reset_harness.html")
    with open(temp_file, "w", encoding="utf-8") as f:
        f.write(harness_html)

    chrome_bin = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

    print("--- RUNNING HEADLESS CHROME LOGO RESET SUITE ---")
    cmd = [
        chrome_bin,
        "--headless=new",
        "--dump-dom",
        "--window-size=1280,800",
        "--virtual-time-budget=6000",
        f"file://{temp_file}"
    ]
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=75)
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
        print(f"\nALL LOGO RESET TESTS PASSED ({len(results)}/{len(results)})!")
    else:
        print("\nSOME TESTS FAILED!")
        sys.exit(1)

    return all_passed

if __name__ == '__main__':
    run_tests()
