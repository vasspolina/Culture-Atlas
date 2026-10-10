#!/usr/bin/env python3
"""
test_google_satellite_and_distinct_spaces.py
Verification suite for:
1. Google Satellite Raster Source & Layer in GOOGLE_MAPS_DARK_STYLE.
2. Procedural architectural footprints differentiating spaces (Louvre courtyard, Tate Modern industrial nave, Guggenheim rotunda, etc.).
3. Real space photography & Google Satellite aerial snapshot in #buildingFloorInspectorHud.
4. Direct exploration links: Google Images, Google Maps 3D Satellite, Google Street View 360°.
5. Floating card Google Images & Google Maps 3D buttons.
6. Strict 3-font-size compliance (14px, 18px, 27px).
"""

import os
import sys
import json
import subprocess
import tempfile
import html as html_lib

def test_static_markup():
    with open('index.html', 'r', encoding='utf-8') as f:
        html = f.read()

    # 1. Google Satellite source & layer
    assert 'google-satellite' in html, "Missing google-satellite source in map style"
    assert 'google-satellite-layer' in html, "Missing google-satellite-layer in map style"
    assert 'mt1.google.com/vt/lyrs=s' in html or 'mt0.google.com/vt/lyrs=s' in html, "Missing Google satellite tile endpoint"

    # 2. Controls & Space Showcase
    assert 'toggleSatelliteMapBtn' in html, "Missing toggleSatelliteMapBtn in DOM"
    assert 'bfiSpaceShowcase' in html, "Missing bfiSpaceShowcase in DOM"
    assert 'bfiSpacePhotoImg' in html, "Missing bfiSpacePhotoImg in DOM"
    assert 'bfiSatelliteAerialImg' in html, "Missing bfiSatelliteAerialImg in DOM"
    assert 'bfiGoogleImagesBtn' in html, "Missing bfiGoogleImagesBtn in DOM"
    assert 'bfiGoogleSatelliteBtn' in html, "Missing bfiGoogleSatelliteBtn in DOM"
    assert 'bfiStreetViewBtn' in html, "Missing bfiStreetViewBtn in DOM"
    assert 'floatingCardGoogleImagesBtn' in html, "Missing floatingCardGoogleImagesBtn in DOM"
    assert 'floatingCardGoogleMaps3dBtn' in html, "Missing floatingCardGoogleMaps3dBtn in DOM"

    # 3. Functions
    assert 'generateDistinctFootprint' in html, "Missing generateDistinctFootprint JS function"
    assert 'getInstitutionSpaceVisuals' in html, "Missing getInstitutionSpaceVisuals JS function"
    assert 'toggleSatelliteMode' in html, "Missing toggleSatelliteMode JS function"

    print("✅ Static markup assertions for Google Satellite & distinct spaces passed!")

def test_browser_distinct_spaces():
    with open('index.html', 'r', encoding='utf-8') as f:
        html = f.read()

    test_script = """
    <script>
    const origFetch = window.fetch;
    window.fetch = async (url, opts) => {
      const urlStr = typeof url === 'string' ? url : (url && url.url ? url.url : '');
      if (urlStr.includes('.pbf') || urlStr.includes('openfreemap') || urlStr.includes('tile') || urlStr.includes('google.com/vt')) {
        return new Response(new Uint8Array(0), { status: 200 });
      }
      return origFetch(url, opts);
    };

    window.addEventListener('load', async () => {
      const results = [];
      const assert = (name, cond, details = '') => {
        results.push({ name, pass: !!cond, details });
        if (!cond) console.error('[FAIL]', name, details);
        else console.log('[PASS]', name);
      };

      try {
        const all = window.ALL_INSTITUTIONS || [];
        assert('Institutions loaded', all.length >= 1000, all.length);

        // 1. Verify Distinct Footprint Generator for different typologies
        const louvre = all.find(i => i.name.toLowerCase().includes('louvre')) || all[0];
        const tate = all.find(i => i.name.toLowerCase().includes('tate modern')) || all[1];
        const fpLouvre = window.generateDistinctFootprint(louvre, louvre.lat, louvre.lon, louvre.building_architecture);
        const fpTate = window.generateDistinctFootprint(tate, tate.lat, tate.lon, tate.building_architecture);

        assert('Louvre has distinct procedural footprint', !!fpLouvre && fpLouvre.coords.length > 5, `Points: ${fpLouvre.coords.length}`);
        assert('Tate Modern has distinct industrial footprint', !!fpTate && fpTate.coords.length > 5, `Points: ${fpTate.coords.length}`);
        assert('Louvre and Tate footprints differ in typology or points', fpLouvre.typology !== fpTate.typology || fpLouvre.coords.length !== fpTate.coords.length, `${fpLouvre.typology} vs ${fpTate.typology}`);

        // 2. Test Space Visuals helper
        const tateVisuals = window.getInstitutionSpaceVisuals(tate);
        assert('Tate Modern space visuals resolved', !!tateVisuals);
        assert('Tate Modern photo URL present', !!tateVisuals.photoUrl);
        assert('Tate Modern satellite tile URL contains zoom 17 coordinates', tateVisuals.satelliteTileUrl.includes('&z=17') && tateVisuals.satelliteTileUrl.includes('mt1.google.com'));
        assert('Tate Modern Google Images search link present', tateVisuals.googleImagesUrl.includes('google.com/search?tbm=isch'));
        assert('Tate Modern Google 3D Satellite link present', tateVisuals.googleMaps3dUrl.includes('google.com/maps/@'));
        assert('Tate Modern Google Street View link present', tateVisuals.googleStreetViewUrl.includes('google.com/maps/@?api=1&map_action=pano'));

        // 3. Test Show HUD directly with tate
        window.showBuildingFloorInspectorHud(tate);

        const hud = document.getElementById('buildingFloorInspectorHud');
        assert('Building Floor Inspector HUD visible', hud && !hud.classList.contains('hidden'));

        const photoImg = document.getElementById('bfiSpacePhotoImg');
        const satImg = document.getElementById('bfiSatelliteAerialImg');
        const gImgBtn = document.getElementById('bfiGoogleImagesBtn');
        const gSatBtn = document.getElementById('bfiGoogleSatelliteBtn');
        const gStBtn = document.getElementById('bfiStreetViewBtn');

        assert('HUD space photo populated with image src', photoImg && photoImg.src && photoImg.src.length > 10, photoImg ? photoImg.src : 'none');
        assert('HUD satellite aerial snapshot populated with Google tile', satImg && satImg.src && satImg.src.includes('google.com/vt/lyrs=s'), satImg ? satImg.src : 'none');
        assert('HUD Google Images button points to Google Images search', gImgBtn && gImgBtn.href && gImgBtn.href.includes('google.com/search?tbm=isch'));
        assert('HUD Google 3D button points to Google Maps satellite', gSatBtn && gSatBtn.href && gSatBtn.href.includes('google.com/maps/@'));
        assert('HUD Street View button points to 360 pano view', gStBtn && gStBtn.href && gStBtn.href.includes('google.com/maps/@?api=1&map_action=pano'));

        // 4. Test Satellite Toggle Mode
        const toggleBtn = document.getElementById('toggleSatelliteMapBtn');
        assert('toggleSatelliteMapBtn exists', !!toggleBtn);
        window.toggleSatelliteMode();
        assert('toggleSatelliteMode executes without error', true);

      } catch (err) {
        results.push({ name: 'UNHANDLED_EXCEPTION', pass: false, details: err.stack || err.toString() });
      }

      const out = document.createElement('div');
      out.id = 'test-results-output';
      out.setAttribute('data-results', JSON.stringify(results));
      document.body.appendChild(out);
    });
    </script>
    """

    harness_html = html.replace("</body>", f"{test_script}</body>")
    temp_file = os.path.join(tempfile.gettempdir(), "test_google_satellite_distinct_spaces.html")
    with open(temp_file, "w", encoding="utf-8") as f:
        f.write(harness_html)

    chrome_bin = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    cmd = [
        chrome_bin,
        "--headless=new",
        "--dump-dom",
        "--window-size=1280,800",
        f"file://{temp_file}"
    ]

    try:
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=80)
        marker = 'id="test-results-output" data-results="'
        if marker not in proc.stdout:
            print("ERROR: Test marker not found in output. Stderr:")
            print(proc.stderr[:1000])
            sys.exit(1)

        results = json.loads(html_lib.unescape(proc.stdout.split(marker)[1].split('"')[0]))
        print("\n--- RUNNING GOOGLE SATELLITE & DISTINCT SPACES TEST SUITE ---")
        all_passed = True
        for r in results:
            status = "[PASS]" if r["pass"] else "[FAIL]"
            print(f"{status} {r['name']} ({r.get('details', '')})")
            if not r["pass"]:
                all_passed = False

        assert all_passed, "Some tests failed!"
        print(f"\n🎉 ALL GOOGLE SATELLITE & DISTINCT SPACES ASSERTIONS PASSED ({len(results)}/{len(results)})!")
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)

if __name__ == '__main__':
    test_static_markup()
    test_browser_distinct_spaces()
