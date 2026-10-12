#!/usr/bin/env python3
"""
test_space_click_and_dossier.py
Verifies:
1. Clicking a space updates #desktopDossierColumn with the clicked space's details.
2. #desktopDossierColumn is visible and properly sized (width >= 350px, height >= 400px).
3. #detailDrawer is hidden by default on desktop, and only opens upon explicit request.
4. #curatorIntelligenceColumn is visible side-by-side with #desktopDossierColumn.
5. curatorContext is updated with the active focus institution.
6. workspaceSelectedInstPill updates with the active institution name.
7. Successive selection across multiple institutions (Katuaq, Chisenhale, Raw Material Company, MoMA) updates cleanly.
"""

import os
import sys
import json
import subprocess
import tempfile
import html as html_lib

def run_tests():
    index_path = "/Users/polinavasilyeva/.gemini/antigravity/scratch/sponsor-atlas/index.html"
    assert os.path.exists(index_path), "index.html must exist"

    with open(index_path, "r", encoding="utf-8") as f:
        html = f.read()

    test_script = """
    <script>
    window.requestAnimationFrame = () => 1;
    window.cancelAnimationFrame = () => {};
    window.fetch = async (url, opts) => {
      const urlStr = String(url);
      if (urlStr.includes('.pbf') || urlStr.includes('openfreemap') || urlStr.includes('tile') || urlStr.includes('style.json')) {
        return new Response(new Uint8Array(0), { status: 200 });
      }
      return new Response("{}", { status: 200, headers: { 'Content-Type': 'application/json' } });
    };

    window.addEventListener('DOMContentLoaded', async () => {
      const results = [];
      function assert(name, cond, extra = '') {
        results.push({ name, pass: Boolean(cond), extra: String(extra) });
      }

      try {
        const testSpaces = [
          'Katuaq Greenland Cultural Centre',
          'Chisenhale Gallery',
          'Raw Material Company',
          'MoMA (The Museum of Modern Art)'
        ];

        for (const spaceName of testSpaces) {
          const inst = (window.ALL_INSTITUTIONS || []).find(i => i.name.toLowerCase().includes(spaceName.toLowerCase()));
          assert('Found ' + spaceName, !!inst);
          if (!inst) continue;

          window.selectInstitution(inst, false);

          const dCol = document.getElementById('desktopDossierColumn');
          const dName = document.getElementById('desktopDossierName');
          const dMeta = document.getElementById('desktopDossierMeta');
          const dBudget = document.getElementById('desktopDossierBudgetAmount');
          const dExhibition = document.getElementById('desktopDossierExhibitionTitle');
          const cCol = document.getElementById('curatorIntelligenceColumn');
          const pillName = document.getElementById('workspaceSelectedInstName');
          const detailDrawer = document.getElementById('detailDrawer');

          assert(spaceName + ': desktop dossier column is visible', dCol && !dCol.classList.contains('hidden') && window.getComputedStyle(dCol).display === 'flex');
          assert(spaceName + ': desktop dossier width >= 350px', dCol && dCol.offsetWidth >= 350, dCol ? dCol.offsetWidth : 0);
          assert(spaceName + ': desktop dossier height >= 400px', dCol && dCol.offsetHeight >= 400, dCol ? dCol.offsetHeight : 0);
          assert(spaceName + ': title matches space name', dName && dName.textContent === inst.name, dName ? dName.textContent : 'null');
          assert(spaceName + ': metadata populated', dMeta && dMeta.textContent.length > 5, dMeta ? dMeta.textContent : 'null');
          assert(spaceName + ': budget populated', dBudget && dBudget.textContent.length > 3, dBudget ? dBudget.textContent : 'null');
          assert(spaceName + ': exhibition populated', dExhibition && dExhibition.textContent.length > 5, dExhibition ? dExhibition.textContent : 'null');
          assert(spaceName + ': curator intelligence column visible side-by-side', cCol && window.getComputedStyle(cCol).display === 'flex');
          assert(spaceName + ': detail drawer overlay is hidden by default', detailDrawer && detailDrawer.classList.contains('hidden'));
          assert(spaceName + ': selected inst pill shows name', pillName && pillName.textContent === inst.name);
          assert(spaceName + ': curatorContext activeFocusInst updated', window.curatorContext && window.curatorContext.activeFocusInst && window.curatorContext.activeFocusInst.name === inst.name);
        }

        // Test explicit deep audit drawer opening
        const sample = window.ALL_INSTITUTIONS[0];
        window.openDossier(sample);
        const drawer = document.getElementById('detailDrawer');
        assert('Explicit openDossier unhides detailDrawer', drawer && !drawer.classList.contains('hidden'));
        assert('Explicit detailDrawer offsetWidth >= 500px', drawer && drawer.offsetWidth >= 500, drawer ? drawer.offsetWidth : 0);
        assert('Explicit detailDrawer offsetHeight >= 500px', drawer && drawer.offsetHeight >= 500, drawer ? drawer.offsetHeight : 0);

        // Test deselectInstitution
        window.deselectInstitution();
        assert('Deselect hides detailDrawer', drawer && drawer.classList.contains('hidden'));
        const dCol = document.getElementById('desktopDossierColumn');
        assert('Deselect collapses desktopDossierColumn', dCol && dCol.classList.contains('hidden'));

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
    temp_file = os.path.join(tempfile.gettempdir(), "test_space_click_harness.html")
    with open(temp_file, "w", encoding="utf-8") as f:
        f.write(harness_html)

    chrome_bin = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    cmd = [
        chrome_bin,
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        "--window-size=1440,900",
        "--virtual-time-budget=3000",
        "--dump-dom",
        f"file://{temp_file}"
    ]

    res = subprocess.run(cmd, capture_output=True, text=True)
    import re
    m = re.search(r'id="test-results-output" data-results="(.*?)"', res.stdout)
    if not m:
        print("FAIL: Could not extract test results from DOM")
        print("STDOUT tail:", res.stdout[-1000:])
        sys.exit(1)

    results = json.loads(html_lib.unescape(m.group(1)))
    passed = 0
    failed = 0

    print("--- RUNNING SPACE CLICK & DOSSIER SUITE ---")
    for r in results:
        if r['pass']:
            passed += 1
            print(f"[PASS] {r['name']} ({r.get('extra', '')})")
        else:
            failed += 1
            print(f"[FAIL] {r['name']} ({r.get('extra', '')})")

    print(f"\nTOTAL: {passed} passed, {failed} failed")
    if failed > 0:
        sys.exit(1)
    print("ALL SPACE CLICK & DOSSIER TESTS PASSED!")

if __name__ == '__main__':
    run_tests()
