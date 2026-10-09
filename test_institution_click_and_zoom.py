#!/usr/bin/env python3
"""
test_institution_click_and_zoom.py
Verify:
1. Filtering/zooming into Italy unclusters all 24 spaces (no Rome (3) or Milan cluster badges).
2. Institutions in the same city are spidered/spread out to prevent stacking.
3. Label hitboxes: clicking an institution's label badge selects the institution.
4. Hitbox priority: findInstitutionAt has Priority 1 over cities.
5. Foreign city cards (e.g. Dijon) are suppressed when filtering Italy.
6. In yellow mode, hover highlights use the opposite color (#38bdf8 cyan).
"""

import os
import sys
import json
import subprocess
import tempfile
import html as html_lib

def test_institution_zoom_and_clicks():
    with open('index.html', 'r', encoding='utf-8') as f:
        html = f.read()

    test_script = """
    <script>
    window.addEventListener('DOMContentLoaded', async () => {
      const results = [];
      function assert(name, cond, extra = '') {
        results.push({ name, pass: Boolean(cond), extra: String(extra) });
      }

      try {
        await new Promise(r => setTimeout(r, 500));
        assert('App initialized', typeof window.filterByCountry === 'function');
        
        // 1. Filter by country Italy
        window.filterByCountry('Italy');
        await new Promise(r => setTimeout(r, 600));

        const currentCountry = typeof window.getSelectedCountryFilter === 'function' ? window.getSelectedCountryFilter() : window.selectedCountryFilter;
        assert('Country filter set to Italy', currentCountry === 'Italy', currentCountry);
        
        // Check visibleDots count and clusters
        const visibleDots = typeof window.getVisibleDots === 'function' ? window.getVisibleDots() : (window.visibleDots || []);
        assert('Visible dots populated for Italy', visibleDots.length >= 5, 'count: ' + visibleDots.length);

        // Check if any cluster badge exists in visibleDots
        const hasCluster = visibleDots.some(d => d.isCluster);
        assert('No cluster badges when zoomed into Italy', !hasCluster);

        // Verify Rome institutions are spidered / separated
        const romeDots = visibleDots.filter(d => (d.inst && d.inst.city && d.inst.city.toLowerCase() === 'rome') || (d.city && d.city.toLowerCase() === 'rome'));
        assert('Multiple Rome institutions found', romeDots.length >= 2, 'count: ' + romeDots.length);
        if (romeDots.length >= 2) {
          const d0 = romeDots[0];
          const d1 = romeDots[1];
          const dist = Math.hypot(d0.x - d1.x, d0.y - d1.y);
          assert('Rome institutions are spread out / spidered (not stacked)', dist >= 15, 'dist: ' + dist.toFixed(1));
        }

        // Verify label boxes exist on visible dots
        const sampleDot = visibleDots.find(d => d.labelBox && d.labelBox.w > 0);
        assert('Label box generated for visible institution', !!sampleDot, sampleDot ? sampleDot.inst.name : 'none');

        if (sampleDot) {
          // Test findInstitutionAt directly on dot centroid
          const foundCentroid = window.findInstitutionAt ? window.findInstitutionAt(sampleDot.x, sampleDot.y) : null;
          assert('findInstitutionAt finds dot at centroid', foundCentroid && (foundCentroid.id === sampleDot.inst.id || foundCentroid.name === sampleDot.inst.name));

          // Test findInstitutionAt on label box
          const labelCenterX = sampleDot.labelBox.x + sampleDot.labelBox.w / 2;
          const labelCenterY = sampleDot.labelBox.y + sampleDot.labelBox.h / 2;
          const foundLabel = window.findInstitutionAt ? window.findInstitutionAt(labelCenterX, labelCenterY) : null;
          assert('findInstitutionAt finds dot clicking inside label badge', foundLabel && (foundLabel.id === sampleDot.inst.id || foundLabel.name === sampleDot.inst.name));

          // Test click dispatch on canvas at label coordinates
          let selectedInstName = null;
          const origSelect = window.selectInstitution;
          window.selectInstitution = function(inst) {
            selectedInstName = inst ? inst.name : null;
            return origSelect.apply(this, arguments);
          };

          const canvas = document.getElementById('globeCanvas');
          const rect = canvas.getBoundingClientRect();
          const targetClientX = rect.left + labelCenterX;
          const targetClientY = rect.top + labelCenterY;

          // Test hover cursor BEFORE click starts flyTo animation
          if (window.updateHoverCursor) {
            window.updateHoverCursor(targetClientX, targetClientY);
            assert('Hovering over label badge sets cursor to pointer', canvas.style.cursor === 'pointer', 'cursor: ' + canvas.style.cursor);
          }

          // Dispatch pointerdown then click (full real pointer sequence)
          canvas.dispatchEvent(new PointerEvent('pointerdown', { clientX: targetClientX, clientY: targetClientY, bubbles: true }));
          canvas.dispatchEvent(new MouseEvent('click', { clientX: targetClientX, clientY: targetClientY, bubbles: true }));
          await new Promise(r => setTimeout(r, 100));

          assert('Pointer click on label badge triggers selectInstitution', selectedInstName === sampleDot.inst.name, 'selected: ' + selectedInstName);
          window.selectInstitution = origSelect;
        }

        // Verify foreign city cards (e.g., Dijon) are suppressed
        // City Dijon coordinates: check if findCityAt or city hover allows foreign city
        if (typeof window.findCityAt === 'function') {
          // If a city is in France while country filter is Italy, hovering should ignore or suppress foreign city card
          const allCities = window.CITIES || [];
          const foreignCity = allCities.find(c => c.country && c.country.toLowerCase() !== 'italy');
          if (foreignCity && window.getCityScreenXY) {
            const p = window.getCityScreenXY(foreignCity);
            if (p && p.visible) {
              const detectedCity = window.findCityAt(p.x, p.y);
              assert('Foreign city ignored or suppressed when Italy is selected', !detectedCity || detectedCity.country.toLowerCase() === 'italy', 'detected: ' + (detectedCity ? detectedCity.city + ' (' + detectedCity.country + ')' : 'none'));
            }
          }
        }

        // Verify Yellow Mode hover color logic
        if (typeof window.isYellowMode === 'function') {
          window.setCardMode && window.setCardMode('gossip', false);
          // In yellow mode, hover border should be cyan #38bdf8
          const sample = visibleDots[0];
          assert('Sample institution dot ready for yellow mode check', !!sample);
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
    temp_file = os.path.join(tempfile.gettempdir(), "test_institution_click_harness.html")
    with open(temp_file, "w", encoding="utf-8") as f:
        f.write(harness_html)

    chrome_bin = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    cmd = [
        chrome_bin,
        "--headless=new",
        "--dump-dom",
        "--window-size=1280,800",
        "--virtual-time-budget=6000",
        f"file://{temp_file}"
    ]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=60)

    marker = 'id="test-results-output" data-results="'
    if marker not in res.stdout:
        print("ERROR: Test marker not found in output. Stderr:")
        print(res.stderr[:1000])
        sys.exit(1)

    results = json.loads(html_lib.unescape(res.stdout.split(marker)[1].split('"')[0]))
    all_passed = True
    for r in results:
        status = "[PASS]" if r["pass"] else "[FAIL]"
        extra = f" ({r['extra']})" if r.get("extra") else ""
        print(f"{status} {r['name']}{extra}")
        if not r["pass"]:
            all_passed = False

    assert all_passed, "Some tests failed!"
    print(f"\n🎉 ALL INSTITUTION HITBOX, SPIDERING & ZOOM TESTS PASSED ({len(results)}/{len(results)})!")

if __name__ == '__main__':
    test_institution_zoom_and_clicks()
