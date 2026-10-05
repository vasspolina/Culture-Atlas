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
        // 1. Open Amsterdam street view (the exact city from the user screenshot)
        openCityStreetView('Amsterdam');
        
        const mapContainer = document.getElementById('cityMapContainer');
        assert('cityMapContainer is visible', mapContainer && !mapContainer.classList.contains('hidden'));
        assert('cityMapContainer has map-zoomed-in class', mapContainer.classList.contains('map-zoomed-in'));

        // 2. Check that markers have inst-pin-label on top of dots
        const markers = cityMarkersLayer.getLayers();
        assert('Amsterdam has markers', markers.length >= 4, `count: ${markers.length}`);

        let labelsFound = 0;
        let sampleLabelText = '';
        markers.forEach(m => {
          const el = m.getElement();
          const label = el ? el.querySelector('.inst-pin-label') : null;
          if (label) {
            labelsFound++;
            const nameEl = label.querySelector('.inst-pin-label-name');
            if (nameEl && !sampleLabelText) sampleLabelText = nameEl.textContent;
          }
        });

        assert('All markers have floating inst-pin-label', labelsFound === markers.length, `${labelsFound}/${markers.length}`);
        assert('Sample label has valid text name', sampleLabelText.length > 2, sampleLabelText);

        // 3. Check CSS computed style of label when zoomed in
        const firstMarker = markers[0].getElement();
        const firstLabel = firstMarker.querySelector('.inst-pin-label');
        const computedStyle = window.getComputedStyle(firstLabel);
        assert('Label is visible when zoomed in', computedStyle.visibility === 'visible' || computedStyle.opacity === '1', `opacity: ${computedStyle.opacity}, visibility: ${computedStyle.visibility}`);

        // 4. Test clicking the label selects the institution
        const instName = firstLabel.getAttribute('data-name');
        firstLabel.click();
        assert('Clicking label selects institution', selectedInstitution && selectedInstitution.name === instName, `selected: ${selectedInstitution?.name}, expected: ${instName}`);

        // 5. Test Addis Ababa also has floating labels on top of dots
        openCityStreetView('Addis Ababa');
        const addisMarkers = cityMarkersLayer.getLayers();
        assert('Addis Ababa has at least 1 marker', addisMarkers.length >= 1);
        const addisLabel = addisMarkers[0].getElement().querySelector('.inst-pin-label');
        assert('Addis Ababa marker has label for Zoma Museum', addisLabel && addisLabel.textContent.includes('Zoma Museum'));

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
    temp_file = os.path.join(tempfile.gettempdir(), "test_zoomed_labels_harness.html")
    with open(temp_file, "w", encoding="utf-8") as f:
        f.write(harness_html)

    chrome_bin = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

    print("--- RUNNING HEADLESS CHROME ZOOMED PIN LABELS SUITE ---")
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
        print(f"\nALL ZOOMED PIN LABEL TESTS PASSED ({len(results)}/{len(results)})!")
    else:
        print("\nSOME TESTS FAILED!")
        sys.exit(1)

    return all_passed

if __name__ == '__main__':
    run_tests()
