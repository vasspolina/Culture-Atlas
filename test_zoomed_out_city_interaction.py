import os
import subprocess
import json
import tempfile

def test_zoomed_out_city_interaction():
    index_path = "/Users/polinavasilyeva/.gemini/antigravity/scratch/sponsor-atlas/index.html"
    assert os.path.exists(index_path), "index.html must exist"

    with open(index_path, "r", encoding="utf-8") as f:
        html = f.read()

    test_script = """
    <script>
    window.addEventListener('load', async () => {
      const results = [];
      function assert(name, cond, extra = '') {
        results.push({ name, pass: !!cond, extra });
      }

      try {
        // 1. Verify findCityAt is exposed on window
        assert('findCityAt is exposed on window', typeof window.findCityAt === 'function');

        // 2. Fly to Europe (London centered) on zoomed-out globe
        flyTo(-0.1276, 51.5072, baseRadius);
        isAutoSpinning = false;
        await new Promise(r => setTimeout(r, 600));

        // 3. Project London on current globe
        const london = ALL_CITIES_REGISTRY.find(c => c.name.toLowerCase() === 'london');
        assert('London is in ALL_CITIES_REGISTRY', !!london);

        const r = currentRadius;
        const cx = width / 2;
        const cy = height / 2;
        const pt = project(london.lon, london.lat, r, cx, cy);
        assert('London projects on front of globe', pt.front === true && pt.depth > 0.05);

        // 4. Test findCityAt directly at London's coordinates
        const cityFound = window.findCityAt(pt.x, pt.y);
        assert('findCityAt at exact pin finds London', cityFound && cityFound.name.toLowerCase() === 'london', JSON.stringify(cityFound));

        // 5. Test findCityAt with 5px offset (mouse jitter within city pin)
        const cityOffset = window.findCityAt(pt.x + 4, pt.y + 4);
        assert('findCityAt with 5px offset finds London', cityOffset && cityOffset.name.toLowerCase() === 'london', JSON.stringify(cityOffset));

        // 6. Test hover simulation on canvas
        const canvas = document.getElementById('globeCanvas');
        const rect = canvas.getBoundingClientRect();

        window.updateHoverCursor(rect.left + pt.x, rect.top + pt.y);
        assert('hoveredCity is set to London', typeof hoveredCity === 'string' && hoveredCity.toLowerCase() === 'london', `hoveredCity: ${hoveredCity}`);
        assert('canvas cursor is set to pointer', canvas.style.cursor === 'pointer', `cursor: ${canvas.style.cursor}`);

        // 7. Test clicking London when zoomed out zooms into city street view
        window.handleGlobeClick(rect.left + pt.x, rect.top + pt.y);
        await new Promise(r => setTimeout(r, 500));

        assert('Clicking London activates isCityStreetViewActive', isCityStreetViewActive === true);
        assert('selectedCityFilter is London', selectedCityFilter.toLowerCase() === 'london', selectedCityFilter);

        // 8. Exit city view and test Paris
        exitCityStreetView();
        await new Promise(r => setTimeout(r, 300));
        assert('After exit, isCityStreetViewActive is false', isCityStreetViewActive === false);

        flyTo(2.3522, 48.8566, baseRadius);
        targetRotX = -(48.8566 * Math.PI / 180);
        rotX = targetRotX;
        targetRotY = (2.3522 * Math.PI / 180);
        rotY = targetRotY;
        isAutoSpinning = false;
        await new Promise(r => setTimeout(r, 600));

        const paris = ALL_CITIES_REGISTRY.find(c => c.name.toLowerCase() === 'paris');
        const ptParis = project(paris.lon, paris.lat, currentRadius, width / 2, height / 2);
        assert('Paris projects on front of globe', ptParis.front === true);

        const parisFound = window.findCityAt(ptParis.x, ptParis.y);
        assert('findCityAt finds Paris', parisFound && parisFound.name.toLowerCase() === 'paris', JSON.stringify(parisFound));

      } catch (err) {
        results.push({ name: 'UNHANDLED_EXCEPTION', pass: false, extra: err.stack || err.toString() });
      }

      const out = document.createElement('div');
      out.id = 'test-results-output';
      out.setAttribute('data-results', JSON.stringify(results));
      document.body.appendChild(out);
    });
    </script>
    """

    harness_html = html.replace("</body>", f"{test_script}</body>")
    temp_file = os.path.join(tempfile.gettempdir(), "test_zoomed_out_city_harness.html")
    with open(temp_file, "w", encoding="utf-8") as f:
        f.write(harness_html)

    chrome_bin = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    cmd = [
        chrome_bin,
        "--headless=new",
        "--dump-dom",
        "--window-size=1280,800",
        "--virtual-time-budget=6000",
        f"file://{temp_file}"
    ]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=30)
    
    import html as html_lib
    import sys
    marker = 'id="test-results-output" data-results="'
    if marker not in res.stdout:
        print("ERROR: Test marker not found in output. Stderr:")
        print(res.stderr[:1000])
        sys.exit(1)

    results = json.loads(html_lib.unescape(res.stdout.split(marker)[1].split('"')[0]))
    print("\n--- ZOOMED OUT CITY HOVER & CLICK TEST RESULTS ---")
    all_passed = True
    for r in results:
        status = "[PASS]" if r["pass"] else "[FAIL]"
        extra = f" ({r['extra']})" if r.get("extra") else ""
        print(f"{status} {r['name']}{extra}")
        if not r["pass"]:
            all_passed = False

    assert all_passed, "Some tests failed!"
    print(f"\n🎉 ALL ZOOMED OUT CITY INTERACTION TESTS PASSED ({len(results)}/{len(results)})!")

if __name__ == "__main__":
    test_zoomed_out_city_interaction()
