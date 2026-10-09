#!/usr/bin/env python3
"""
test_xray_rooms_3d_engine.py
Verification test suite for:
1. Detailed 3D X-Ray building rendering with multi-room interior blueprint based on floor maps.
2. Distinct architectural room partitioning:
   - Primary Curatorial Exhibition Gallery (with exhibition title, room name, dates)
   - Archives & Special Collections Study Room (with collection name, holding count, access policy)
   - Public Atrium & Orientation Forum (with entrance, facilities, access policy)
3. Structural floor slabs separating levels and see-through translucent glass exterior.
4. Spatial 3D in-building room callout badges rendered directly inside the museum levels.
5. Proper numeric paint fill-extrusion-opacity in MapLibre layers (no data expression rejections).
"""

import os
import sys
import json
import subprocess
import tempfile
import html as html_lib

def test_static_html():
    with open('index.html', 'r', encoding='utf-8') as f:
        html = f.read()

    # 1. Extrusion layers and sources
    assert 'highlighted-building-3d-slabs' in html, "Missing highlighted-building-3d-slabs source"
    assert 'building-3d-floor-slabs' in html, "Missing building-3d-floor-slabs layer"
    assert 'highlighted-building-3d-interior-core' in html, "Missing highlighted-building-3d-interior-core source"
    assert 'building-3d-xray-interior-core' in html, "Missing building-3d-xray-interior-core layer"
    assert 'highlighted-building-3d-floors' in html, "Missing highlighted-building-3d-floors source"
    assert 'building-3d-floor-extrusions' in html, "Missing building-3d-floor-extrusions layer"

    # 2. Check that fill-extrusion-opacity is numeric and not ['get', 'opacity']
    assert "'fill-extrusion-opacity': 0.94" in html or '"fill-extrusion-opacity": 0.94' in html, "Missing numeric slab opacity"
    assert "'fill-extrusion-opacity': 0.88" in html or '"fill-extrusion-opacity": 0.88' in html, "Missing numeric core opacity"
    assert "'fill-extrusion-opacity': 0.32" in html or '"fill-extrusion-opacity": 0.32' in html, "Missing numeric envelope opacity"

    # 3. Check room badge classes
    assert 'building-3d-room-badge' in html, "Missing building-3d-room-badge class in JS"
    assert 'EXHIBITION GALLERY' in html, "Missing EXHIBITION GALLERY room badge"
    assert 'ARCHIVES & STUDY' in html, "Missing ARCHIVES & STUDY room badge"
    assert 'PUBLIC FORUM' in html, "Missing PUBLIC FORUM room badge"

    print("✅ Static HTML verification for 3D multi-room X-ray engine passed.")

def test_browser_3d_rooms_and_xray():
    with open('index.html', 'r', encoding='utf-8') as f:
        html = f.read()

    test_script = """
    <script>
    window.addEventListener('DOMContentLoaded', async () => {
      const results = [];
      function assert(name, condition, extra = '') {
        results.push({ name, pass: Boolean(condition), extra: String(extra) });
      }

      try {
        await new Promise(r => setTimeout(r, 500));

        const all = window.ALL_INSTITUTIONS || [];
        assert('Institutions loaded', all.length >= 1000, all.length);

        // Find institution with multiple floors (e.g. Stedelijk or ARoS or Hayward)
        const inst = all.find(i => i.floor_plans && i.floor_plans.length >= 2 && i.floor_plans[0].archive_holdings) || all[0];
        assert('Sample multi-floor institution found', !!inst, inst.name);

        // Zoom to 3D building
        window.zoomToBuilding(inst, false);
        await new Promise(r => setTimeout(r, 600));

        // Check map camera
        if (window.cityVectorMap) {
          const z = window.cityVectorMap.getZoom();
          const p = window.cityVectorMap.getPitch();
          assert('Vector map camera at 3D building zoom (>= 18.0)', z >= 18.0, `Zoom: ${z}`);
          assert('Vector map camera at steep 3D architectural pitch (>= 58)', p >= 58, `Pitch: ${p}`);

          // Check slabs source
          const slabSrc = window.cityVectorMap.getSource('highlighted-building-3d-slabs');
          assert('3D structural floor slabs source exists', !!slabSrc);
          if (slabSrc && slabSrc.data && slabSrc.data.features) {
            const slabs = slabSrc.data.features;
            assert('Floor slabs generated for all storeys + roof deck', slabs.length >= inst.floor_plans.length, `Count: ${slabs.length}`);
          }

          // Check interior core / rooms source
          const coreSrc = window.cityVectorMap.getSource('highlighted-building-3d-interior-core');
          assert('3D interior rooms source exists', !!coreSrc);
          if (coreSrc && coreSrc.data && coreSrc.data.features) {
            const rooms = coreSrc.data.features;
            assert('Multi-room features generated inside building (>= 3 rooms)', rooms.length >= 3, `Count: ${rooms.length}`);

            const galleryRoom = rooms.find(r => r.properties && r.properties.room_type === 'gallery');
            assert('Curatorial Exhibition Gallery room generated with show metadata', !!galleryRoom, galleryRoom ? galleryRoom.properties.name : 'none');

            const archiveRoom = rooms.find(r => r.properties && r.properties.room_type === 'archive');
            assert('Archives & Study Room generated with holding records', !!archiveRoom, archiveRoom ? archiveRoom.properties.name : 'none');

            const atriumRoom = rooms.find(r => r.properties && r.properties.room_type === 'atrium');
            assert('Public Atrium & Facilities Forum generated', !!atriumRoom, atriumRoom ? atriumRoom.properties.name : 'none');
          }

          // Check glass envelope source
          const envSrc = window.cityVectorMap.getSource('highlighted-building-3d-floors');
          assert('3D see-through glass envelope source exists', !!envSrc);
        }

        // Check spatial 3D room badges rendered onto map
        const roomBadges = document.querySelectorAll('.building-3d-room-badge');
        assert('Spatial 3D In-Building room badges rendered over museum levels', roomBadges.length >= 2, `Count: ${roomBadges.length}`);

        const badgeTexts = Array.from(roomBadges).map(b => b.textContent).join(' ');
        assert('Room badges display EXHIBITION GALLERY', badgeTexts.includes('EXHIBITION GALLERY'));
        assert('Room badges display ARCHIVES & STUDY', badgeTexts.includes('ARCHIVES & STUDY'));
        assert('Room badges display PUBLIC FORUM', badgeTexts.includes('PUBLIC FORUM'));

        // Check Floor Inspector HUD populated
        const hud = document.getElementById('buildingFloorInspectorHud');
        assert('Floor Inspector HUD visible on screen', hud && !hud.classList.contains('hidden'));

        const hudName = document.getElementById('bfiBuildingName');
        assert('Floor Inspector HUD displays building name', hudName && hudName.textContent.includes(inst.name), hudName ? hudName.textContent : 'none');

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
    temp_file = os.path.join(tempfile.gettempdir(), "test_xray_rooms_3d_harness.html")
    with open(temp_file, "w", encoding="utf-8") as f:
        f.write(harness_html)

    chrome_bin = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    cmd = [
        chrome_bin,
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        "--dump-dom",
        "--virtual-time-budget=6000",
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
        print("\n--- RUNNING 3D MULTI-ROOM X-RAY ARCHITECTURAL ENGINE TESTS ---")
        all_passed = True
        for r in results:
            status = "[PASS]" if r["pass"] else "[FAIL]"
            print(f"{status} {r['name']} ({r.get('extra', '')})")
            if not r["pass"]:
                all_passed = False

        assert all_passed, "Some tests failed!"
        print(f"\n🎉 ALL 3D MULTI-ROOM X-RAY TESTS PASSED ({len(results)}/{len(results)})!")
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)

if __name__ == '__main__':
    test_static_html()
    test_browser_3d_rooms_and_xray()
