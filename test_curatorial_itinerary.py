#!/usr/bin/env python3
"""
Test Suite for Curatorial Itinerary & Art Crawl Generator
Verifies:
1. Static structure of itinerary modals, HUD buttons, route banner, and globe filter pills.
2. In-browser runtime execution of:
   - SIGNATURE_ITINERARIES data and integrity (London, Berlin, New York, Paris, Amsterdam, Basel)
   - compileCuratorialRoute() for signature and custom cities
   - GeoJSON line generation & Haversine distance calculations
   - launchCuratorialRoute() map layer activation, stop markers, and #activeRouteBanner HUD
   - jumpToRouteStop() stop progression and prev/next controls
   - clearCuratorialRoute() cleanup
   - openCuratorialItineraryModal() and modal tab switching
   - Conversational Curator chat intent routing for itineraries & art crawls
"""

import os
import sys
import re
import tempfile
import html
import subprocess
import json

HTML_FILE = os.path.abspath("index.html")

def test_static_html_structure():
    print(">>> Testing static HTML markup in index.html...")
    with open(HTML_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Active route HUD banner
    assert 'id="activeRouteBanner"' in content, "Missing #activeRouteBanner element"
    assert 'id="activeRouteTitle"' in content, "Missing #activeRouteTitle element"
    assert 'id="activeRouteStats"' in content, "Missing #activeRouteStats element"
    assert 'id="activeRouteStopName"' in content, "Missing #activeRouteStopName element"
    assert 'id="activeRouteStopHours"' in content, "Missing #activeRouteStopHours element"
    assert 'id="activeRouteStopFee"' in content, "Missing #activeRouteStopFee element"
    assert 'id="routePrevStopBtn"' in content, "Missing #routePrevStopBtn element"
    assert 'id="routeNextStopBtn"' in content, "Missing #routeNextStopBtn element"
    assert 'id="routeOverviewBtn"' in content, "Missing #routeOverviewBtn element"
    assert 'id="closeActiveRouteBtn"' in content, "Missing #closeActiveRouteBtn element"
    print("  ✓ Active route HUD banner structure verified")

    # 2. Bottom map HUD button & globe filter pill
    assert 'id="hudRouteBtn"' in content, "Missing #hudRouteBtn in map controls bar"
    assert 'id="globeItinerariesBtn"' in content, "Missing #globeItinerariesBtn in filter pills"
    print("  ✓ HUD route button and globe filter pill verified")

    # 3. Curatorial Itinerary Modal
    assert 'id="curatorialItineraryModal"' in content, "Missing #curatorialItineraryModal"
    assert 'id="closeItineraryModalBtn"' in content, "Missing #closeItineraryModalBtn"
    assert 'id="itineraryTabSignature"' in content, "Missing #itineraryTabSignature"
    assert 'id="itineraryTabCustom"' in content, "Missing #itineraryTabCustom"
    assert 'id="itineraryModalBody"' in content, "Missing #itineraryModalBody"
    print("  ✓ Curatorial Itinerary Modal structure verified")

    # 4. Engine functions in script
    for fn in ["compileCuratorialRoute", "launchCuratorialRoute", "jumpToRouteStop",
               "clearCuratorialRoute", "ensureCuratorialRouteLayer", "openCuratorialItineraryModal"]:
        assert fn in content, f"Missing function {fn} in script"
    print("  ✓ Engine functions presence verified in script")

def test_browser_runtime():
    print("\n>>> Testing in-browser runtime execution via headless Chrome...")

    test_script = """
    <script>
    window.addEventListener('load', async () => {
        const results = [];
        function assert(desc, passed, detail = '') {
            results.push({ desc, passed: Boolean(passed), detail: String(detail) });
            console.log((passed ? '✓ PASS: ' : '✗ FAIL: ') + desc + (detail ? ' (' + detail + ')' : ''));
        }

        try {
            // Mock network calls to avoid virtual time budget deadlocks
            window.scrapeWebForQuery = async () => null;
            window.queryAI = async () => null;

            // 1. Signature itineraries
            assert('SIGNATURE_ITINERARIES is an array', Array.isArray(window.SIGNATURE_ITINERARIES));
            assert('Has at least 6 signature itineraries', window.SIGNATURE_ITINERARIES && window.SIGNATURE_ITINERARIES.length >= 6);

            const cities = (window.SIGNATURE_ITINERARIES || []).map(s => s.city);
            ['London', 'Berlin', 'New York', 'Paris', 'Amsterdam', 'Basel'].forEach(c => {
                assert('Signature itinerary exists for ' + c, cities.includes(c));
            });

            // 2. Compilation of Signature Route (London)
            const londonRoute = window.compileCuratorialRoute('london-east-vanguard');
            assert('London route compiled successfully', londonRoute !== null);
            assert('London route has 5 stops', londonRoute && londonRoute.stops.length === 5);
            assert('London totalKm is reasonable (> 1.0 km)', londonRoute && londonRoute.totalKm > 1.0, londonRoute ? londonRoute.totalKm + ' km' : '');
            assert('London total walk minutes computed (> 10 min)', londonRoute && londonRoute.totalWalkMinutes > 10, londonRoute ? londonRoute.totalWalkMinutes + ' min' : '');
            assert('GeoJSON LineString generated', londonRoute && londonRoute.geojson && londonRoute.geojson.features[0].geometry.type === 'LineString');
            assert('GeoJSON coordinates count matches stop count', londonRoute && londonRoute.geojson.features[0].geometry.coordinates.length === 5);

            // 3. Dynamic compilation for city (Berlin)
            const berlinRoute = window.compileCuratorialRoute('Berlin', { pace: 'half', cleanOnly: true });
            assert('Berlin dynamic route compiled', berlinRoute !== null);
            assert('Half-day pace restricts stops <= 3', berlinRoute && berlinRoute.stops.length <= 3, berlinRoute ? berlinRoute.stops.length : '');
            assert('Clean-only filter applied (all Tier A)', berlinRoute && berlinRoute.stops.every(s => s.tier === 'A'));

            // 4. Test launchCuratorialRoute and HUD activation
            window.launchCuratorialRoute('london-east-vanguard');
            const activeBanner = document.getElementById('activeRouteBanner');
            assert('activeRouteBanner is visible after route launch', activeBanner && !activeBanner.classList.contains('hidden'));
            const bannerTitle = document.getElementById('activeRouteTitle')?.textContent || '';
            assert('Banner title reflects London route', bannerTitle.includes('East London') || bannerTitle.includes('London'));
            const stopBadge = document.getElementById('activeRouteStopBadge')?.textContent || '';
            assert('Initial stop is Stop 1', stopBadge.includes('STOP 1'));
            assert('window.activeCuratorialRoute is populated', window.activeCuratorialRoute !== null);

            // 5. Test jumpToRouteStop
            window.jumpToRouteStop(2);
            const stop3Badge = document.getElementById('activeRouteStopBadge')?.textContent || '';
            assert('Jumped to Stop 3', stop3Badge.includes('STOP 3'));
            const prevBtn = document.getElementById('routePrevStopBtn');
            assert('Prev stop button is enabled on Stop 3', prevBtn && !prevBtn.disabled);

            // 6. Test clearCuratorialRoute
            window.clearCuratorialRoute();
            assert('activeRouteBanner is hidden after clearCuratorialRoute', activeBanner && activeBanner.classList.contains('hidden'));
            assert('activeCuratorialRoute is null after clearing', window.activeCuratorialRoute === null);

            // 7. Test openCuratorialItineraryModal and tab switching
            window.openCuratorialItineraryModal('London');
            const itinModal = document.getElementById('curatorialItineraryModal');
            assert('curatorialItineraryModal opens on openCuratorialItineraryModal()', itinModal && !itinModal.classList.contains('hidden'));
            
            const modalBody = document.getElementById('itineraryModalBody');
            assert('Signature route cards rendered in modal', modalBody && (modalBody.innerHTML.includes('London: East Vanguard') || modalBody.innerHTML.includes('East London')));

            window.switchItineraryTab('custom');
            assert('Custom city selector rendered in custom tab', modalBody && modalBody.innerHTML.includes('customCrawlCitySelect'));

            window.closeCuratorialItineraryModal();
            assert('curatorialItineraryModal closes on closeCuratorialItineraryModal()', itinModal && itinModal.classList.contains('hidden'));

            // 8. Test Curator chat intent routing for itineraries
            const prevMsgCount = document.querySelectorAll('.curator-message-wrap').length;
            await window.handleCuratorQuery("art crawl in Berlin");
            for (let i = 0; i < 20; i++) {
                await new Promise(r => setTimeout(r, 100));
                if (document.querySelectorAll('.curator-message-wrap').length > prevMsgCount) break;
            }
            const chatBody = document.getElementById('curatorMessages');
            assert('Chat handles "art crawl in Berlin" with curated itinerary card', chatBody && (chatBody.innerHTML.includes('Berlin Mitte-to-Kreuzberg') || chatBody.innerHTML.includes('Route Timeline')));

            const prevMsgCount2 = document.querySelectorAll('.curator-message-wrap').length;
            await window.handleCuratorQuery("suggest a curatorial itinerary");
            for (let i = 0; i < 20; i++) {
                await new Promise(r => setTimeout(r, 100));
                if (document.querySelectorAll('.curator-message-wrap').length > prevMsgCount2) break;
            }
            assert('Chat handles generic itinerary query with Showcase card', chatBody && (chatBody.innerHTML.includes('Curatorial Itineraries') || chatBody.innerHTML.includes('Art Crawls')));

        } catch (err) {
            assert('Execution Exception', false, err.stack || err.toString());
        }

        const out = document.createElement('div');
        out.id = 'itinerary-test-results';
        out.setAttribute('data-results', JSON.stringify(results));
        document.body.appendChild(out);
    });
    </script>
    """

    with open(HTML_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    harness_html = content.replace("</body>", f"{test_script}</body>")
    temp_file = os.path.join(tempfile.gettempdir(), "test_itinerary_harness.html")
    with open(temp_file, "w", encoding="utf-8") as f:
        f.write(harness_html)

    chrome_cmd = [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "--headless=new",
        "--dump-dom",
        "--window-size=1280,800",
        "--virtual-time-budget=8000",
        f"file://{temp_file}"
    ]

    res = subprocess.run(chrome_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=30)
    stdout = res.stdout

    if os.path.exists(temp_file):
        os.remove(temp_file)

    marker = 'id="itinerary-test-results" data-results="'
    if marker not in stdout:
        print("[FAIL] Test output marker not found in headless Chrome output!")
        print(stdout[:500])
        sys.exit(1)

    raw_json = stdout.split(marker)[1].split('"')[0]
    results = json.loads(html.unescape(raw_json))

    passed = [r for r in results if r["passed"]]
    failed = [r for r in results if not r["passed"]]

    print(f"\nBrowser Test Results: {len(passed)} passed, {len(failed)} failed")
    for p in passed:
        print(f"  ✓ {p['desc']}" + (f" ({p['detail']})" if p['detail'] else ""))
    for f in failed:
        print(f"  ✗ FAIL: {f['desc']}" + (f" ({f['detail']})" if f['detail'] else ""))

    assert len(failed) == 0, f"{len(failed)} browser tests failed"
    print("\n  >>> All browser runtime tests PASSED successfully!")

if __name__ == "__main__":
    test_static_html_structure()
    test_browser_runtime()
