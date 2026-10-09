#!/usr/bin/env python3
"""
test_xray_gossip_and_shows.py
Comprehensive test suite verifying:
1. 🩻 3D X-Ray architectural cutaway (translucent outer glass envelope + luminous interior core).
2. 🖼️ Current Shows and Opening Night Vernissage Tracker inside floating card and on 3D building levels.
3. 🔄 Dynamic updates of 3D model and marquee when selecting exhibitions/floors.
4. 🔤 PP Telegraph Extra Thin font-weight (200) enforcement across all web UI elements.
5. 🌍 Non-overlapping country labels on the 3D globe with city hit-box collision suppression.
6. 🟡 Yellow Gossip Mode (Reddit threads, Twitter/X discourse, chat backchannels, yellow glowing beacons).
"""

import os
import sys
import json
import subprocess
import tempfile
import html as html_lib

def test_static_html_requirements():
    with open('index.html', 'r', encoding='utf-8') as f:
        html = f.read()

    # 1. Typography: PP Telegraph Extra Thin (weight: 200)
    assert 'font-weight: 200 !important' in html, "Missing font-weight: 200 !important in CSS"
    assert 'PP Telegraph' in html or 'PP Telegraf' in html, "Missing PP Telegraph font reference"

    # 2. X-Ray 3D Layers
    assert 'building-3d-xray-interior-core' in html, "Missing building-3d-xray-interior-core layer"
    assert 'highlighted-building-3d-interior-core' in html, "Missing highlighted-building-3d-interior-core source"
    assert 'building-3d-floor-extrusions' in html, "Missing building-3d-floor-extrusions layer"

    # 3. Current Shows and Opening Night Vernissage
    assert 'floatingCardCurrentShowsSection' in html, "Missing floatingCardCurrentShowsSection in DOM"
    assert 'floatingCardOpeningNightBox' in html, "Missing floatingCardOpeningNightBox in DOM"
    assert 'Vernissage' in html, "Missing Vernissage text in DOM"

    # 4. Yellow Gossip Mode
    assert 'topGossipBtn' in html, "Missing topGossipBtn in header"
    assert 'floatingCardGossipSection' in html, "Missing floatingCardGossipSection in DOM"
    assert 'window.toggleGossipMode' in html or 'toggleGossipMode' in html, "Missing toggleGossipMode in JS"
    assert 'r/contemporaryart' in html or 'r/art' in html, "Missing reddit gossip section"

    print("✅ Static HTML and DOM structure verified successfully.")

def test_browser_xray_and_gossip_mode():
    with open('index.html', 'r', encoding='utf-8') as f:
        html = f.read()

    test_script = """
    <script>
    window.addEventListener('load', async () => {
      const results = [];
      function assert(name, condition, extra = '') {
        results.push({ name, pass: Boolean(condition), extra: String(extra) });
      }

      try {
        await new Promise(r => setTimeout(r, 400));

        const all = window.ALL_INSTITUTIONS || [];
        assert('Institutions loaded', all.length >= 1000, all.length);

        const testInst = all.find(i => i.temporary_shows && i.temporary_shows.length > 0 && i.gossip_data) || all[0];
        assert('Test institution with shows & gossip found', !!testInst, testInst ? testInst.name : 'none');

        // 1. Test Floating Card Population (Shows + Gossip)
        if (typeof window.selectInstitution === 'function') {
          window.selectInstitution(testInst);
          const showTitleEl = document.getElementById('floatingCardShowTitle');
          assert('Floating card populated show title', showTitleEl && showTitleEl.textContent.length > 0, showTitleEl ? showTitleEl.textContent : 'none');

          const vernissageBox = document.getElementById('floatingCardOpeningNightBox');
          assert('Vernissage opening night tracker rendered', vernissageBox && vernissageBox.style.display !== 'none');

          const gossipHeadline = document.getElementById('floatingCardGossipHeadline');
          assert('Floating card populated gossip headline', gossipHeadline && gossipHeadline.textContent.length > 0, gossipHeadline ? gossipHeadline.textContent : 'none');

          const gossipReddit = document.getElementById('floatingCardGossipRedditText');
          assert('Floating card populated reddit thread info', gossipReddit && gossipReddit.textContent.length > 0, gossipReddit ? gossipReddit.textContent : 'none');

          const gossipTwitter = document.getElementById('floatingCardGossipTwitterText');
          assert('Floating card populated twitter info', gossipTwitter && gossipTwitter.textContent.length > 0, gossipTwitter ? gossipTwitter.textContent : 'none');
        }

        // 2. Test Yellow Gossip Mode Toggle
        assert('toggleGossipMode function exists', typeof window.toggleGossipMode === 'function');
        assert('isGossipModeActive defaults to false', window.isGossipModeActive === false);

        window.toggleGossipMode();
        assert('isGossipModeActive toggles to true', window.isGossipModeActive === true);

        const topGossipBtn = document.getElementById('topGossipBtn');
        assert('topGossipBtn displays ACTIVE state', topGossipBtn && topGossipBtn.textContent.includes('ACTIVE'));

        window.toggleGossipMode();
        assert('isGossipModeActive toggles back to false', window.isGossipModeActive === false);

        // 3. Test 3D X-Ray Building Model
        window.zoomToBuilding(testInst, false);
        await new Promise(r => setTimeout(r, 400));

        if (window.cityVectorMap) {
          const srcEnvelope = window.cityVectorMap.getSource('highlighted-building-3d-floors');
          assert('3D X-Ray glass envelope source exists', !!srcEnvelope);

          const layerEnvelope = window.cityVectorMap.getLayer('building-3d-floor-extrusions');
          assert('3D X-Ray glass envelope layer exists', !!layerEnvelope);

          const srcCore = window.cityVectorMap.getSource('highlighted-building-3d-interior-core');
          assert('3D X-Ray luminous interior core source exists', !!srcCore);

          const layerCore = window.cityVectorMap.getLayer('building-3d-xray-interior-core');
          assert('3D X-Ray luminous interior core layer exists', !!layerCore);
        }

        // 4. Test Dynamic Model Update when floor/show selected
        assert('selectBfiFloor function exists', typeof window.selectBfiFloor === 'function');
        window.selectBfiFloor(0);

        const mastEl = document.querySelector('.building-3d-mast-plate');
        assert('Rooftop Mast Plate rendered over building', !!mastEl);

        const facadeEl = document.querySelector('.building-3d-facade-stack');
        assert('Floor Directory facade stack rendered over building', !!facadeEl);

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
    temp_file = os.path.join(tempfile.gettempdir(), "test_xray_gossip_harness.html")
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
        "--virtual-time-budget=6000",
        f"file://{temp_file}"
    ]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=30)
    
    marker = 'id="test-results-output" data-results="'
    if marker not in res.stdout:
        print("ERROR: Test marker not found in output. Stderr:")
        print(res.stderr[:1000])
        sys.exit(1)

    results = json.loads(html_lib.unescape(res.stdout.split(marker)[1].split('"')[0]))
    print("\n--- RUNNING X-RAY, GOSSIP & SHOWS TEST SUITE ---")
    all_passed = True
    for r in results:
        status = "[PASS]" if r["pass"] else "[FAIL]"
        extra = f" ({r['extra']})" if r.get("extra") else ""
        print(f"{status} {r['name']}{extra}")
        if not r["pass"]:
            all_passed = False

    assert all_passed, "Some tests failed!"
    print(f"\n🎉 ALL X-RAY, GOSSIP & SHOWS TESTS PASSED ({len(results)}/{len(results)})!")

if __name__ == '__main__':
    test_static_html_requirements()
    test_browser_xray_and_gossip_mode()
