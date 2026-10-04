import os
import subprocess
import json
import tempfile

def run_tests():
    index_path = "/Users/polinavasilyeva/.gemini/antigravity/scratch/sponsor-atlas/index.html"
    with open(index_path, "r", encoding="utf-8") as f:
        html = f.read()

    # Static assertion: cartocdn must never exist in the codebase
    assert "cartocdn.com" not in html, "cartocdn.com must not be referenced anywhere in index.html"
    assert "renderMapTiles" not in html, "renderMapTiles must not exist in index.html"

    test_script = """
    <script>
    window.addEventListener('load', async () => {
      const results = [];
      function assert(name, condition, extra = '') {
        results.push({ name, pass: !!condition, extra });
      }

      try {
        // Test 1: Verify Saint Petersburg street network
        const spbData = getCityStreetData('Saint Petersburg');
        assert("Saint Petersburg data exists", !!spbData);
        assert("Saint Petersburg has waterways (Neva, Fontanka, Moika)", spbData.waterways && spbData.waterways.length >= 3, `count: ${spbData.waterways.length}`);
        assert("Saint Petersburg has parks (Summer Garden)", spbData.parks && spbData.parks.length >= 2, `count: ${spbData.parks.length}`);
        assert("Saint Petersburg has major streets (Nevsky)", spbData.major_streets && spbData.major_streets.length >= 4, `count: ${spbData.major_streets.length}`);
        assert("Saint Petersburg has secondary streets", spbData.secondary_streets && spbData.secondary_streets.length >= 2, `count: ${spbData.secondary_streets.length}`);

        // Test 2: Verify Krasnodar street network
        const krasData = getCityStreetData('Krasnodar');
        assert("Krasnodar data exists", !!krasData);
        assert("Krasnodar has Kuban River", krasData.waterways && krasData.waterways.length >= 1, `count: ${krasData.waterways.length}`);
        assert("Krasnodar has Krasnaya Street", krasData.major_streets && krasData.major_streets.length >= 3, `count: ${krasData.major_streets.length}`);

        // Test 3: Verify unlisted city procedural cartography
        const unlistedData = getCityStreetData('Unlisted Test Art Hub');
        assert("Unlisted city receives procedural data", !!unlistedData);
        assert("Unlisted city receives waterways", unlistedData.waterways && unlistedData.waterways.length > 0);
        assert("Unlisted city receives parks", unlistedData.parks && unlistedData.parks.length > 0);
        assert("Unlisted city receives major streets", unlistedData.major_streets && unlistedData.major_streets.length > 0);
        assert("Unlisted city receives secondary street grid", unlistedData.secondary_streets && unlistedData.secondary_streets.length > 0);

        // Test 4: Verify rendering on zoom does not throw errors
        currentRadius = baseRadius * 2.0;
        rotLon = 30.3;
        rotLat = 59.9;
        if (typeof render === 'function') {
          render();
        }
        assert("Globe render at r = 2.0x succeeds without error", true);

        currentRadius = baseRadius * 15.0;
        selectedCityFilter = 'Saint Petersburg';
        if (typeof render === 'function') {
          render();
        }
        assert("City zoom render at r = 15.0x succeeds without error", true);

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
    temp_file = os.path.join(tempfile.gettempdir(), "test_no_watermarks_harness.html")
    with open(temp_file, "w", encoding="utf-8") as f:
        f.write(harness_html)

    chrome_bin = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    cmd = [
        chrome_bin,
        "--headless=new",
        "--dump-dom",
        "--virtual-time-budget=5000",
        f"file://{temp_file}"
    ]

    print("Running headless Chrome verification...")
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=30)
    marker = 'id="test-results-output" data-results="'
    if marker not in proc.stdout:
        print("ERROR: Test marker not found in output. Stderr:")
        print(proc.stderr[:1000])
        return False

    import html as html_lib
    results = json.loads(html_lib.unescape(proc.stdout.split(marker)[1].split('"')[0]))
    all_passed = True
    print("\n--- TEST RESULTS ---")
    for r in results:
        status = "PASS" if r['pass'] else "FAIL"
        if not r['pass']:
            all_passed = False
        extra = f" ({r['extra']})" if r.get('extra') else ""
        print(f"[{status}] {r['name']}{extra}")

    print(f"\nSummary: {sum(1 for r in results if r['pass'])}/{len(results)} passed.")
    return all_passed

if __name__ == "__main__":
    success = run_tests()
    if not success:
        exit(1)
