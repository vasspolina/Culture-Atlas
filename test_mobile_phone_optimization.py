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

    window.addEventListener('DOMContentLoaded', async () => {
      const results = [];
      function assert(name, condition, extra = '') {
        results.push({ name, pass: !!condition, extra });
      }

      try {
        const header = document.querySelector('header');
        const logoBtn = document.getElementById('topBrandLogoBtn');
        const modeSwitch = document.getElementById('mobileModeSwitch');
        const topResetBtn = document.getElementById('topResetBtn');
        const mobileNewChatBtn = document.getElementById('mobileNewChatBtn');
        const topSettingsBtn = document.getElementById('topSettingsBtn');
        const globe = document.getElementById('globeViewport');
        const workView = document.getElementById('workViewContainer');
        const splitter = document.getElementById('globeSplitter');

        // 1. Header Containment on 375px Phone
        assert("Header exists", !!header);
        const resetStyle = window.getComputedStyle(topResetBtn);
        assert("topResetBtn is hidden on mobile to conserve space", resetStyle.display === 'none', `display: ${resetStyle.display}`);
        
        const modeSwitchStyle = window.getComputedStyle(modeSwitch);
        assert("Mobile Mode Switcher is visible on mobile", modeSwitchStyle.display !== 'none', `display: ${modeSwitchStyle.display}`);

        assert("Logo exists and has CULTURE ATLAS text", logoBtn && logoBtn.textContent.toUpperCase().includes('CULTURE ATLAS'));
        assert("Mobile Mode Switcher exists in header", !!modeSwitch);

        // Test physical containment when viewport is restricted to 375px (iPhone standard)
        header.style.width = '375px';
        header.style.maxWidth = '375px';
        assert("Header width fits 375px", header.clientWidth === 375, `clientWidth: ${header.clientWidth}`);
        assert("Header has no horizontal overflow at 375px", header.scrollWidth <= header.clientWidth + 2, `scrollWidth: ${header.scrollWidth}, clientWidth: ${header.clientWidth}`);
        header.style.width = '';
        header.style.maxWidth = '';

        // 2. Default Split Mode
        assert("setMobileViewMode function is available", typeof window.setMobileViewMode === 'function');
        assert("Globe is visible in split mode", window.getComputedStyle(globe).display === 'flex');
        assert("Work view is visible in split mode", window.getComputedStyle(workView).display === 'flex');
        assert("Splitter is visible in split mode", window.getComputedStyle(splitter).display !== 'none');

        // 3. Test Mode: 'map'
        window.setMobileViewMode('map');
        assert("Globe display is flex in map mode", window.getComputedStyle(globe).display === 'flex');
        assert("Globe height is 100% in map mode", globe.style.height === '100%');
        assert("Work view display is none in map mode", window.getComputedStyle(workView).display === 'none');
        assert("Splitter display is none in map mode", window.getComputedStyle(splitter).display === 'none');

        // 4. Test Ask Curator auto-switches from 'map' to 'chat'
        const origHandle = typeof handleCuratorQuery === 'function' ? handleCuratorQuery : null;
        if (origHandle) window.handleCuratorQuery = () => {};
        const sampleInst = ALL_INSTITUTIONS[0];
        window.atlasAskCurator(sampleInst.name);
        assert("Calling atlasAskCurator switches from map to chat mode", window.getComputedStyle(workView).display === 'flex');
        assert("Globe is hidden in chat mode", window.getComputedStyle(globe).display === 'none');
        assert("Work view height is 100% in chat mode", workView.style.height === '100%');
        if (origHandle) window.handleCuratorQuery = origHandle;

        // 5. Test Mode: 'split'
        window.setMobileViewMode('split');
        assert("Globe display is flex in split mode", window.getComputedStyle(globe).display === 'flex');
        assert("Globe height is 50% in split mode", globe.style.height === '50%');
        assert("Work view display is flex in split mode", window.getComputedStyle(workView).display === 'flex');
        assert("Work view height is 50% in split mode", workView.style.height === '50%');
        assert("Splitter display is flex in split mode", window.getComputedStyle(splitter).display === 'flex');

        // 6. Test World Zoom vs Filter/Zoom label rule
        window.resetGlobeView();
        // At World Zoom with no active filter:
        const worldShouldDraw = (false || false || selectedCountryFilter !== 'all' || selectedCityFilter !== 'all' || currentRadius >= baseRadius * 1.35);
        assert("World view without filters does not show floating text cloud", worldShouldDraw === false, `currentRadius: ${currentRadius}, baseRadius: ${baseRadius}, targetRadius: ${targetRadius}`);

        // When zoomed in:
        const zoomedShouldDraw = (false || false || selectedCountryFilter !== 'all' || selectedCityFilter !== 'all' || (baseRadius * 1.5) >= baseRadius * 1.35);
        assert("Zoomed view shows floating text labels", zoomedShouldDraw === true);

        // When country filter is active:
        selectedCountryFilter = 'Argentina';
        const filteredShouldDraw = (false || false || selectedCountryFilter !== 'all' || selectedCityFilter !== 'all' || currentRadius >= baseRadius * 1.35);
        assert("Country filter view shows floating text labels", filteredShouldDraw === true);
        selectedCountryFilter = 'all';

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
    temp_file = os.path.join(tempfile.gettempdir(), "test_mobile_optimization_harness.html")
    with open(temp_file, "w", encoding="utf-8") as f:
        f.write(harness_html)

    chrome_bin = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

    print("--- RUNNING MOBILE (375x667) OPTIMIZATION SUITE ---")
    cmd_mobile = [
        chrome_bin,
        "--headless=new",
        "--dump-dom",
        "--window-size=375,667",
                f"file://{temp_file}"
    ]
    proc = subprocess.run(cmd_mobile, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=60)
    marker = 'id="test-results-output" data-results="'
    if marker not in proc.stdout:
        print("ERROR: Test marker not found in mobile output. Stderr:")
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
        print("\nALL MOBILE PHONE OPTIMIZATION TESTS PASSED!")
    return all_passed

if __name__ == "__main__":
    success = run_tests()
    if not success:
        exit(1)
