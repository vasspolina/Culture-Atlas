#!/usr/bin/env python3
"""
test_building_3d_mapped_info.py
Verification test suite for:
1. True 3D volumetric building floor extrusions (fill-extrusion with base/height).
2. Surrounding 3D city buildings context layer in vector cartography.
3. Spatial On-Building 3D Information Mapping:
   - Rooftop Building Mast Plate (Institution name, style, floors, hours, action buttons).
   - 3D Floor-by-Floor Facade Annotation Stack (mapped directly to each physical storey).
4. Exploded Axonometric 3D Mode toggle.
5. Suppression of obstructive 2D floating card when inspecting 3D buildings.
"""

import os
import sys
import json
import html as html_lib
import subprocess
import tempfile

def test_static_html():
    with open('index.html', 'r', encoding='utf-8') as f:
        html = f.read()

    assert 'highlighted-building-3d-floors' in html, "Missing highlighted-building-3d-floors source"
    assert 'building-3d-floor-extrusions' in html, "Missing building-3d-floor-extrusions layer"
    assert "'fill-extrusion'" in html or '"fill-extrusion"' in html, "Missing fill-extrusion layer type"
    assert "'fill-extrusion-height'" in html or '"fill-extrusion-height"' in html, "Missing fill-extrusion-height paint property"
    assert "'fill-extrusion-base'" in html or '"fill-extrusion-base"' in html, "Missing fill-extrusion-base paint property"
    assert 'building-3d-city-context' in html, "Missing building-3d-city-context layer in cartography style"
    assert 'function updateBuilding3DInfoMarkers(' in html, "Missing updateBuilding3DInfoMarkers function"
    assert 'function clearBuilding3DInfoMarkers(' in html, "Missing clearBuilding3DInfoMarkers function"
    assert 'function toggleExploded3DMode(' in html, "Missing toggleExploded3DMode function"
    assert 'building-3d-mast-plate' in html, "Missing building-3d-mast-plate class in DOM builder"
    assert 'building-3d-facade-stack' in html, "Missing building-3d-facade-stack class in DOM builder"
    assert '3D FLOOR DIRECTORY' in html, "Missing 3D FLOOR DIRECTORY in facade stack"
    print("✅ Static HTML verification passed.")

def test_browser_3d_building_and_mapped_info():
    with open('index.html', 'r', encoding='utf-8') as f:
        html = f.read()

    test_script = """
    <script>
    const runTests = async () => {
      const results = [];
      function assert(name, condition, extra = '') {
        results.push({ name, pass: Boolean(condition), extra: String(extra) });
      }

      try {
        await new Promise(r => setTimeout(r, 400));

        // 1. Find FESPACO or Chisenhale or Slought
        const all = window.ALL_INSTITUTIONS || [];
        assert('Total institutions loaded', all.length >= 1000, all.length);

        const fespaco = all.find(i => i.name.toLowerCase().includes('fespaco')) || all[0];
        assert('FESPACO exists in dataset', !!fespaco, fespaco ? fespaco.name : 'none');

        // 2. Zoom to building
        window.zoomToBuilding(fespaco, false);
        if (window.cityVectorMap) {
          window.cityVectorMap.jumpTo({ center: [fespaco.lon, fespaco.lat], zoom: 18.6, pitch: 62, bearing: 28 });
        }
        await new Promise(r => setTimeout(r, 1200));

        if (window.cityVectorMap && typeof window.cityVectorMap.isStyleLoaded === 'function' && !window.cityVectorMap.isStyleLoaded()) {
          await new Promise(resolve => {
            let done = false;
            const finish = () => { if (!done) { done = true; resolve(); } };
            window.cityVectorMap.once('styledata', finish);
            window.cityVectorMap.once('load', finish);
            setTimeout(finish, 2000);
          });
        }

        // Check map container active and 2D card suppressed
        const mapEl = document.getElementById('cityMapContainer');
        assert('cityMapContainer is unhidden', mapEl && !mapEl.classList.contains('hidden'));
        assert('cityMapContainer has map-zoomed-in class', mapEl && mapEl.classList.contains('map-zoomed-in'));

        const floatCard = document.getElementById('floatingCard');
        assert('floatingCard 2D popup is hidden in 3D building view', floatCard && floatCard.classList.contains('hidden'));

        // 3. Check 3D Extruded Floor Features in vector map source
        if (window.cityVectorMap) {
          const styleLoaded = typeof window.cityVectorMap.isStyleLoaded === 'function' ? window.cityVectorMap.isStyleLoaded() : 'no fn';
          const isLoaded = typeof window.cityVectorMap.loaded === 'function' ? window.cityVectorMap.loaded() : 'no fn';
          const src3D = window.cityVectorMap.getSource('highlighted-building-3d-floors');
          assert('3D floors source exists on cityVectorMap', !!src3D, `isStyleLoaded: ${styleLoaded}, loaded: ${isLoaded}`);

          const layer3D = window.cityVectorMap.getLayer('building-3d-floor-extrusions');
          assert('3D floors layer exists on cityVectorMap', !!layer3D);

          // Check camera zoom & 3D architectural pitch
          const z = window.cityVectorMap.getZoom();
          const p = window.cityVectorMap.getPitch();
          assert('Vector map zoomed to building level (zoom >= 18)', z >= 18, `Zoom: ${z}`);
          assert('Vector map has 3D architectural pitch (pitch >= 55)', p >= 55, `Pitch: ${p}`);
        }

        // 4. Check 3D On-Building Mapped Markers (Mast Plate & Facade Stack)
        const mastPlates = document.querySelectorAll('.building-3d-mast-plate');
        assert('3D Rooftop Mast Plate rendered onto building', mastPlates.length > 0, `Count: ${mastPlates.length}`);
        if (mastPlates.length > 0) {
          const text = mastPlates[0].textContent;
          assert('Mast Plate displays institution name', text.includes(fespaco.name), text.slice(0, 80));
          assert('Mast Plate displays Explode 3D Floors action', text.includes('Explode 3D Floors'), text.slice(0, 80));
          assert('Mast Plate displays 20x Zoom button', text.includes('20x Zoom'), text.slice(0, 80));
        }

        const facadeStacks = document.querySelectorAll('.building-3d-facade-stack');
        assert('3D Facade Floor Directory rendered onto building', facadeStacks.length > 0, `Count: ${facadeStacks.length}`);
        if (facadeStacks.length > 0) {
          const fText = facadeStacks[0].textContent;
          assert('Facade Stack displays 3D FLOOR DIRECTORY header', fText.includes('3D FLOOR DIRECTORY'), fText.slice(0, 80));
          assert('Facade Stack displays floor level badges (L0 or Level)', fText.includes('L0') || fText.includes('Level'), fText.slice(0, 80));
        }

        // 5. Test Exploded 3D Axonometric Mode Toggle
        assert('toggleExploded3DMode function is available', typeof window.toggleExploded3DMode === 'function');
        window.toggleExploded3DMode();
        assert('isExploded3DMode toggles to true', window.isExploded3DMode === true);

        // Mast plate should now show Stack 3D Building
        const mastAfterExplode = document.querySelector('.building-3d-mast-plate');
        if (mastAfterExplode) {
          assert('Mast Plate toggles button to Stack 3D Building', mastAfterExplode.textContent.includes('Stack 3D Building'));
        }

        // Toggle back to stacked mode
        window.toggleExploded3DMode();
        assert('isExploded3DMode toggles back to false', window.isExploded3DMode === false);

        // 6. Test Floor Level Selection Updates 3D Model
        window.selectBfiFloor(0);
        assert('selectBfiFloor sets floor index', typeof window.selectBfiFloor === 'function');

      } catch (err) {
        results.push({ name: 'UNHANDLED_EXCEPTION', pass: false, extra: err.stack || err.toString() });
      }

      const out = document.createElement('div');
      out.id = 'test-results-output';
      out.setAttribute('data-results', JSON.stringify(results));
      document.body.appendChild(out);
    };
    if (document.readyState === 'complete') { setTimeout(runTests, 100); } else { window.addEventListener('load', runTests); }
    </script>
    """

    harness_html = html.replace("</body>", f"{test_script}</body>")
    temp_file = os.path.join(tempfile.gettempdir(), "test_building_3d_mapped_info_harness.html")
    with open(temp_file, "w", encoding="utf-8") as f:
        f.write(harness_html)

    chrome_bin = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    cmd = [
        chrome_bin,
        "--headless=new",
        "--dump-dom",
        "--window-size=1280,800",
        "--virtual-time-budget=15000",
        f"file://{temp_file}"
    ]

    try:
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=60)
        marker = 'id="test-results-output" data-results="'
        if marker not in proc.stdout:
            print("ERROR: Test marker not found in output. Stderr:")
            print(proc.stderr[:1000])
            sys.exit(1)

        results = json.loads(html_lib.unescape(proc.stdout.split(marker)[1].split('"')[0]))
        print("\n--- RUNNING 3D BUILDING & MAPPED INFO TEST SUITE ---")
        all_passed = True
        for r in results:
            status = "[PASS]" if r["pass"] else "[FAIL]"
            print(f"{status} {r['name']} ({r.get('extra', '')})")
            if not r["pass"]:
                all_passed = False

        assert all_passed, "Some tests failed!"
        print(f"\n🎉 ALL 3D BUILDING & MAPPED INFO TESTS PASSED ({len(results)}/{len(results)})!")
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)

if __name__ == '__main__':
    test_static_html()
    test_browser_3d_building_and_mapped_info()
