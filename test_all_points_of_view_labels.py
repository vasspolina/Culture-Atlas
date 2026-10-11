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
    // Stub fetch for vector tiles, raster tiles, and remote network calls
    window.fetch = async (url, opts) => {
      const urlStr = String(url && url.url ? url.url : url);
      if (urlStr.includes('.pbf') || urlStr.includes('openfreemap') || urlStr.includes('tile') || urlStr.includes('google.com') || urlStr.includes('gstatic') || urlStr.includes('style.json')) {
        return new Response(new Uint8Array(0), { status: 200 });
      }
      return new Response("{}", { status: 200, headers: { 'Content-Type': 'application/json' } });
    };

    window.addEventListener('DOMContentLoaded', async () => {
      const style = document.createElement('style');
      style.innerHTML = '* { transition: none !important; animation: none !important; }';
      document.head.appendChild(style);
      const results = [];
      function assert(name, condition, extra = '') {
        results.push({ name, pass: !!condition, extra });
      }

      try {
        // 1. Buenos Aires street view
        openCityStreetView('Buenos Aires');

        const baMarkers = cityMarkersLayer.getLayers();
        assert('Buenos Aires has markers', baMarkers.length >= 2, 'count: ' + baMarkers.length);

        let baLabels = [];
        baMarkers.forEach(m => {
          const el = m.getElement();
          const label = el ? el.querySelector('.inst-pin-label') : null;
          if (label) {
            const style = window.getComputedStyle(label);
            if (style.display !== 'none' && style.visibility !== 'hidden' && style.opacity !== '0') {
              baLabels.push(label.textContent.trim());
            }
          }
        });
        assert('All Buenos Aires markers have visible labels', baLabels.length === baMarkers.length, `${baLabels.length}/${baMarkers.length}`);
        assert('Label contains Bellas Artes', baLabels.some(l => l.includes('Bellas Artes')));
        assert('Label contains Palacio Libertad', baLabels.some(l => l.includes('Palacio Libertad')));

        // 2. Zoomed-out street view (zoom 10)
        cityVectorMap.setZoom(10);
        if (typeof updateCityZoomClasses === 'function') updateCityZoomClasses();
        let baLabelsZoom10 = [];
        baMarkers.forEach(m => {
          const el = m.getElement();
          const label = el ? el.querySelector('.inst-pin-label') : null;
          if (label) {
            const style = window.getComputedStyle(label);
            if (style.display !== 'none' && style.visibility !== 'hidden' && style.opacity !== '0') {
              baLabelsZoom10.push(label.textContent.trim());
            }
          }
        });
        assert('Labels remain visible even when zoomed out to 10', baLabelsZoom10.length === baMarkers.length);

        // 3. Zoomed-in street view (zoom 16)
        cityVectorMap.setZoom(16);
        if (typeof updateCityZoomClasses === 'function') updateCityZoomClasses();
        let baLabelsZoom16 = [];
        baMarkers.forEach(m => {
          const el = m.getElement();
          const label = el ? el.querySelector('.inst-pin-label') : null;
          if (label) {
            const style = window.getComputedStyle(label);
            if (style.display !== 'none' && style.visibility !== 'hidden' && style.opacity !== '0') {
              baLabelsZoom16.push(label.textContent.trim());
            }
          }
        });
        assert('Labels remain visible when zoomed in to 16', baLabelsZoom16.length === baMarkers.length);

        // 4. Exit to globe and check globe view
        exitCityStreetView();
        assert('City street view is inactive after exit', !isCityStreetViewActive);

        // 5. Test another city: Bilbao
        openCityStreetView('Bilbao');
        const bilbaoMarkers = cityMarkersLayer.getLayers();
        assert('Bilbao has markers', bilbaoMarkers.length >= 2, 'count: ' + bilbaoMarkers.length);
        let bilbaoLabels = [];
        bilbaoMarkers.forEach(m => {
          const el = m.getElement();
          const label = el ? el.querySelector('.inst-pin-label') : null;
          if (label) {
            const style = window.getComputedStyle(label);
            if (style.display !== 'none' && style.visibility !== 'hidden' && style.opacity !== '0') {
              bilbaoLabels.push(label.textContent.trim());
            }
          }
        });
        assert('All Bilbao markers have visible labels', bilbaoLabels.length === bilbaoMarkers.length, `${bilbaoLabels.length}/${bilbaoMarkers.length}`);
        assert('Bilbao label contains Bulegoa z/b', bilbaoLabels.some(l => l.includes('Bulegoa z/b')));

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
    temp_file = os.path.join(tempfile.gettempdir(), "test_all_points_harness.html")
    with open(temp_file, "w", encoding="utf-8") as f:
        f.write(harness_html)

    chrome_bin = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

    print("--- RUNNING HEADLESS CHROME ALL POINTS OF VIEW LABELS SUITE ---")
    cmd = [
        chrome_bin,
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        "--dump-dom",
        "--window-size=1280,800",
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
        print(f"\nALL ALL-POINTS-OF-VIEW LABEL TESTS PASSED ({len(results)}/{len(results)})!")
    return all_passed

if __name__ == "__main__":
    success = run_tests()
    if not success:
        exit(1)
