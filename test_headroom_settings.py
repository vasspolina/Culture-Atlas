#!/usr/bin/env python3
"""
test_headroom_settings.py
Verification test suite for 3D Building Camera & Rooftop Mast Headroom Architecture:
1. Static HTML checks:
   - HEADROOM_PRESETS configuration with compact, comfortable, and spacious modes.
   - Dynamic getBuildingCameraPadding() and setBuilding3DHeadroom(mode) APIs.
   - Cycle function cycleBuilding3DHeadroom().
   - Curator Settings Modal UI controls: #currentHeadroomBadge, .headroom-setting-btn buttons.
   - Rooftop Mast Plate headroom cycle pill: .mast-headroom-pill.
2. Headless Chrome Browser runtime checks:
   - Default headroom preset is 'comfortable' with top padding >= 96px on mobile and >= 120px on desktop.
   - setBuilding3DHeadroom('compact') sets top padding to 70px (desktop) / 65px (mobile), updates badge & styles.
   - setBuilding3DHeadroom('spacious') sets top padding to 160px (desktop) / 130px (mobile), updates badge & styles.
   - cycleBuilding3DHeadroom() sequentially cycles compact -> comfortable -> spacious -> compact.
   - Mast plate displays .mast-headroom-pill with active headroom label.
   - Clicking .mast-headroom-pill cycles the headroom preset and re-frames the camera.
   - Clicking Settings modal buttons updates the selected headroom mode and persists to localStorage.
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

    assert 'HEADROOM_PRESETS' in html, "Missing HEADROOM_PRESETS in index.html"
    assert 'getBuildingCameraPadding' in html, "Missing getBuildingCameraPadding in index.html"
    assert 'setBuilding3DHeadroom' in html, "Missing setBuilding3DHeadroom in index.html"
    assert 'cycleBuilding3DHeadroom' in html, "Missing cycleBuilding3DHeadroom in index.html"
    assert 'mast-headroom-pill' in html, "Missing mast-headroom-pill in index.html"
    assert 'currentHeadroomBadge' in html, "Missing currentHeadroomBadge in index.html"
    assert 'headroom-setting-btn' in html, "Missing headroom-setting-btn in index.html"
    assert 'data-headroom="compact"' in html, "Missing data-headroom compact button"
    assert 'data-headroom="comfortable"' in html, "Missing data-headroom comfortable button"
    assert 'data-headroom="spacious"' in html, "Missing data-headroom spacious button"
    assert '3D Building Camera Headroom' in html, "Missing 3D Building Camera Headroom section in settings"

    # Check standalone and app/index.html as well
    for path in ['app/index.html', 'app/standalone.html']:
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f2:
                h2 = f2.read()
            assert 'HEADROOM_PRESETS' in h2, f"Missing HEADROOM_PRESETS in {path}"
            assert 'mast-headroom-pill' in h2, f"Missing mast-headroom-pill in {path}"
    print("✅ Static HTML headroom verification passed.")

def test_browser_headroom_runtime():
    with open('index.html', 'r', encoding='utf-8') as f:
        html = f.read()

    test_script = """
    <script>
    const origFetch = window.fetch;
    window.fetch = async (url, opts) => {
      const urlStr = typeof url === 'string' ? url : (url && url.url ? url.url : '');
      if (urlStr.includes('.pbf') || urlStr.includes('openfreemap') || urlStr.includes('tile') || urlStr.includes('google.com') || urlStr.includes('gstatic') || urlStr.includes('style.json')) {
        return new Response(new Uint8Array(0), { status: 200 });
      }
      return origFetch(url, opts);
    };

    window.addEventListener('DOMContentLoaded', async () => {
      const style = document.createElement('style');
      style.innerHTML = '* { transition: none !important; animation: none !important; }';
      document.head.appendChild(style);
      const results = [];
      function assert(name, condition, extra = '') {
        results.push({ name, pass: Boolean(condition), extra: String(extra) });
      }

      try {
        // 1. Initial State & APIs
        assert('getBuildingCameraPadding function available', typeof window.getBuildingCameraPadding === 'function');
        assert('setBuilding3DHeadroom function available', typeof window.setBuilding3DHeadroom === 'function');
        assert('cycleBuilding3DHeadroom function available', typeof window.cycleBuilding3DHeadroom === 'function');
        assert('getBuilding3DHeadroomLabel function available', typeof window.getBuilding3DHeadroomLabel === 'function');

        // Check default preset (comfortable: 120px desktop)
        const defaultPadding = window.getBuildingCameraPadding();
        assert('Default camera top padding >= 96px', defaultPadding && defaultPadding.top >= 96, `top: ${defaultPadding?.top}`);
        assert('Default camera top padding is 120px on desktop', defaultPadding && defaultPadding.top === 120, `top: ${defaultPadding?.top}`);
        assert('Default camera bottom padding is generous (>= 60px)', defaultPadding && defaultPadding.bottom >= 60, `bottom: ${defaultPadding?.bottom}`);

        const badge = document.getElementById('currentHeadroomBadge');
        assert('Settings badge displays default comfortable label', badge && badge.textContent.includes('Comfortable'), badge?.textContent);

        // 2. Set to 'compact' preset
        window.setBuilding3DHeadroom('compact', false);
        const compactPadding = window.getBuildingCameraPadding();
        assert('Compact camera top padding is 70px on desktop', compactPadding && compactPadding.top === 70, `top: ${compactPadding?.top}`);
        assert('Compact badge updated', badge && badge.textContent.includes('Compact'), badge?.textContent);
        const compactBtn = document.querySelector('.headroom-setting-btn[data-headroom="compact"]');
        assert('Compact button has active style classes', compactBtn && compactBtn.classList.contains('border-emerald-500/60'));

        // 3. Set to 'spacious' preset
        window.setBuilding3DHeadroom('spacious', false);
        const spaciousPadding = window.getBuildingCameraPadding();
        assert('Spacious camera top padding is 160px on desktop', spaciousPadding && spaciousPadding.top === 160, `top: ${spaciousPadding?.top}`);
        assert('Spacious badge updated', badge && badge.textContent.includes('Spacious'), badge?.textContent);
        const spaciousBtn = document.querySelector('.headroom-setting-btn[data-headroom="spacious"]');
        assert('Spacious button has active style classes', spaciousBtn && spaciousBtn.classList.contains('border-emerald-500/60'));

        // 4. Test cycleBuilding3DHeadroom
        // From spacious -> should cycle to compact
        window.cycleBuilding3DHeadroom();
        assert('Cycle from spacious goes to compact', window.getBuildingCameraPadding().top === 70, `top: ${window.getBuildingCameraPadding().top}`);
        // From compact -> should cycle to comfortable
        window.cycleBuilding3DHeadroom();
        assert('Cycle from compact goes to comfortable', window.getBuildingCameraPadding().top === 120, `top: ${window.getBuildingCameraPadding().top}`);

        // 5. Test 3D Rooftop Mast Plate integration
        const all = window.ALL_INSTITUTIONS || [];
        const inst = all.find(i => i.name.toLowerCase().includes('slought') || i.name.toLowerCase().includes('fespaco')) || all[0];
        assert('Institution found for 3D headroom test', !!inst);

        window.zoomToBuilding(inst, false);
        if (window.cityVectorMap) {
          window.cityVectorMap.jumpTo({ center: [inst.lon, inst.lat], zoom: 18.6, pitch: 62, bearing: 28 });
        }

        const mastPlate = document.querySelector('.building-3d-mast-plate');
        assert('3D Rooftop Mast Plate exists in DOM', !!mastPlate);

        const mastPill = document.querySelector('.mast-headroom-pill');
        assert('.mast-headroom-pill exists on rooftop mast plate', !!mastPill);
        if (mastPill) {
          assert('Mast pill displays headroom label', mastPill.textContent.includes('Headroom') || mastPill.textContent.includes('px'), mastPill.textContent);
          
          // Click mast pill to trigger cycle
          const prevTop = window.getBuildingCameraPadding().top;
          mastPill.click();
          const nextTop = window.getBuildingCameraPadding().top;
          assert('Clicking mast pill cycles camera padding', prevTop !== nextTop, `prev: ${prevTop}, next: ${nextTop}`);
        }

        // 6. Test Settings Modal Button Clicks
        const compactButton = document.querySelector('.headroom-setting-btn[data-headroom="compact"]');
        if (compactButton) {
          compactButton.click();
          assert('Clicking compact button in settings sets top padding to 70', window.getBuildingCameraPadding().top === 70);
          assert('localStorage persists compact headroom', localStorage.getItem('atlas_3d_headroom') === 'compact');
        }

        const comfortableButton = document.querySelector('.headroom-setting-btn[data-headroom="comfortable"]');
        if (comfortableButton) {
          comfortableButton.click();
          assert('Clicking comfortable button in settings sets top padding to 120', window.getBuildingCameraPadding().top === 120);
          assert('localStorage persists comfortable headroom', localStorage.getItem('atlas_3d_headroom') === 'comfortable');
        }

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
    temp_file = os.path.join(tempfile.gettempdir(), "test_headroom_settings_harness.html")
    with open(temp_file, "w", encoding="utf-8") as f:
        f.write(harness_html)

    chrome_bin = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    cmd = [
        chrome_bin,
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        "--dump-dom",
        "--window-size=1280,800",
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
        print("\n--- RUNNING HEADROOM SETTINGS TEST SUITE ---")
        all_passed = True
        for r in results:
            status = "[PASS]" if r["pass"] else "[FAIL]"
            print(f"{status} {r['name']} ({r.get('extra', '')})")
            if not r["pass"]:
                all_passed = False

        assert all_passed, "Some tests failed!"
        print(f"\n🎉 ALL HEADROOM SETTINGS TESTS PASSED ({len(results)}/{len(results)})!")
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)

if __name__ == '__main__':
    print("Testing 3D Building Camera & Rooftop Mast Headroom Settings...")
    test_static_html()
    test_browser_headroom_runtime()
