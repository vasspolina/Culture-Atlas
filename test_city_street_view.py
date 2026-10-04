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
    // Stub fetch for vector tiles and fonts so headless chrome doesn't wait for network
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
        // 1. Verify MapLibre GL library is loaded
        assert('MapLibre GL library is defined', typeof maplibregl !== 'undefined');
        assert('MapLibre map function exists', typeof maplibregl.Map === 'function');
        assert('GOOGLE_MAPS_DARK_STYLE is defined', typeof GOOGLE_MAPS_DARK_STYLE !== 'undefined' && GOOGLE_MAPS_DARK_STYLE.version === 8);

        // 2. Test openCityStreetView for Addis Ababa
        openCityStreetView('Addis Ababa');
        
        const mapContainer = document.getElementById('cityMapContainer');
        assert('cityMapContainer is not null', !!mapContainer);
        assert('cityMapContainer is visible (no hidden class)', !mapContainer.classList.contains('hidden'));
        assert('isCityStreetViewActive is true', isCityStreetViewActive === true);
        assert('cityVectorMap is initialized', !!cityVectorMap);
        assert('cityLeafletMap compatibility shim is initialized', !!cityLeafletMap);
        assert('Map has 3D tilt/pitch active (>= 30 deg)', cityVectorMap.getPitch() >= 30, `pitch: ${cityVectorMap.getPitch()}`);

        const banner = document.getElementById('cityViewControlBanner');
        assert('cityViewControlBanner is visible', banner && !banner.classList.contains('hidden'));

        const titleText = document.getElementById('cityViewTitleText')?.textContent || '';
        assert('Banner displays Addis Ababa', titleText.includes('ADDIS ABABA'), titleText);

        const markerCount = cityMarkersLayer ? cityMarkersLayer.getLayers().length : 0;
        assert('Addis Ababa has at least 1 cultural marker (Zoma Museum)', markerCount >= 1, `count: ${markerCount}`);

        // Check center coords of vector map
        const center = cityVectorMap.getCenter();
        assert('Vector map centered near Addis Ababa latitude ~8.98', Math.abs(center.lat - 8.985) < 0.1, `lat: ${center.lat}`);
        assert('Vector map centered near Addis Ababa longitude ~38.72', Math.abs(center.lng - 38.722) < 0.1, `lng: ${center.lng}`);

        // 3. Test exitCityStreetView
        exitCityStreetView();
        assert('isCityStreetViewActive is false after exit', isCityStreetViewActive === false);
        assert('cityMapContainer has hidden class after exit', mapContainer.classList.contains('hidden'));
        assert('cityViewControlBanner has hidden class after exit', banner.classList.contains('hidden'));

        // 4. Test filterByCity for London opens street view
        filterByCity('London', true, false);
        assert('filterByCity activates isCityStreetViewActive', isCityStreetViewActive === true);
        assert('cityMapContainer visible for London', !mapContainer.classList.contains('hidden'));
        const londonMarkers = cityMarkersLayer ? cityMarkersLayer.getLayers().length : 0;
        assert('London has multiple cultural markers', londonMarkers >= 3, `count: ${londonMarkers}`);

        // 5. Test exit button
        const exitBtn = document.getElementById('exitStreetViewBtn');
        assert('exitStreetViewBtn exists', !!exitBtn);
        exitBtn.click();
        assert('Clicking exitStreetViewBtn returns to 3D globe', isCityStreetViewActive === false && mapContainer.classList.contains('hidden'));

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
    temp_file = os.path.join(tempfile.gettempdir(), "test_street_view_harness.html")
    with open(temp_file, "w", encoding="utf-8") as f:
        f.write(harness_html)

    chrome_bin = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

    print("--- RUNNING HEADLESS CHROME STREET VIEW SUITE ---")
    cmd = [
        chrome_bin,
        "--headless=new",
        "--dump-dom",
        "--window-size=1280,800",
        "--virtual-time-budget=3000",
        f"file://{temp_file}"
    ]
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=45)
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
        print(f"\nALL CITY STREET VIEW TESTS PASSED ({len(results)}/{len(results)})!")
    else:
        print("\nSOME TESTS FAILED!")
        sys.exit(1)

    return all_passed

if __name__ == '__main__':
    run_tests()
