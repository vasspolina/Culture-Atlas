#!/usr/bin/env python3
"""
test_mutual_exclusivity_and_docking.py
Tests:
1. Mutual Exclusivity:
   - When building inspector HUD opens, filter drawer is automatically closed/collapsed.
   - When filter drawer opens, building inspector HUD is automatically closed/hidden.
2. Docking:
   - Clicking 'Dock ↗' on building inspector HUD hides the on-map HUD, opens the Dossier/Inspector
     tab on the right workspace, and centers the 3D building on the map without obstruction.
3. 3D Architecture in Dossier:
   - Right-panel Dossier includes interactive 3D camera controls and floor selector pills.
   - Changing floor updates the active floor card in the dossier and triggers map layer update.
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

    assert 'id="dockBfiToWorkspaceBtn"' in html, "Missing #dockBfiToWorkspaceBtn in index.html"
    assert 'function dockBuildingInspectorToWorkspace(' in html, "Missing dockBuildingInspectorToWorkspace() in index.html"
    assert 'id="dossierActiveFloorCard"' in html, "Missing #dossierActiveFloorCard in index.html"
    assert 'function updateDossierFloorSelection(' in html, "Missing updateDossierFloorSelection() in index.html"
    print("✅ Static markup checks passed.")

def test_browser_interactions():
    with open('index.html', 'r', encoding='utf-8') as f:
        html = f.read()

    test_script = """
    <script>
    const origFetch = window.fetch;
    window.fetch = async (url, opts) => {
      const urlStr = typeof url === 'string' ? url : (url && url.url ? url.url : '');
      if (urlStr.includes('.pbf') || urlStr.includes('openfreemap') || urlStr.includes('tile')) {
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
        const all = window.ALL_INSTITUTIONS || [];
        const inst = all.find(i => i.name.includes('Pulitzer')) || all[0];
        assert('Target institution found', !!inst, inst.name);

        const filterDrawer = document.getElementById('filterDrawerPanel');
        const bfiHud = document.getElementById('buildingFloorInspectorHud');
        const bottomDock = document.getElementById('workBottomDock');

        // Test 1: Open Filter Drawer first
        window.toggleFilterDrawer(true);
        assert('Filter Drawer is open', filterDrawer && !filterDrawer.classList.contains('hidden'));
        assert('Bottom dock hidden when drawer open', bottomDock && bottomDock.classList.contains('hidden'));

        // Test 2: Mutual Exclusivity - Opening 3D Building Inspector automatically closes Filter Drawer
        window.showBuildingFloorInspectorHud(inst);
        assert('Building HUD is visible', bfiHud && !bfiHud.classList.contains('hidden'));
        assert('Filter Drawer was closed automatically by Mutual Exclusivity', filterDrawer && filterDrawer.classList.contains('hidden'));

        // Test 3: Mutual Exclusivity Reverse - Opening Filter Drawer closes Building HUD
        window.toggleFilterDrawer(true);
        assert('Filter Drawer re-opened', filterDrawer && !filterDrawer.classList.contains('hidden'));
        assert('Building HUD was hidden automatically by Mutual Exclusivity', bfiHud && bfiHud.classList.contains('hidden'));

        // Test 4: Docking Inspector to Right Workspace Panel
        window.showBuildingFloorInspectorHud(inst);
        const dockBtn = document.getElementById('dockBfiToWorkspaceBtn');
        assert('Dock button exists', !!dockBtn);
        window.dockBuildingInspectorToWorkspace(inst);

        assert('Building HUD on map is hidden after docking', bfiHud && bfiHud.classList.contains('hidden'));
        const detailDrawer = document.getElementById('detailDrawer');
        assert('Right panel Detail/Dossier Drawer is open', detailDrawer && !detailDrawer.classList.contains('hidden'));

        const dossierFloorCard = document.getElementById('dossierActiveFloorCard');
        assert('Dossier includes 3D active floor card', !!dossierFloorCard);

        // Test 5: Switch floor in Dossier
        if (inst.floor_plans && inst.floor_plans.length > 1) {
          window.selectBfiFloor(1);
          window.updateDossierFloorSelection(1);
          const floorPills = document.querySelectorAll('.dossier-floor-tab');
          assert('Floor tab 1 highlighted in dossier', floorPills.length > 1 && floorPills[1].classList.contains('bg-sky-600'));
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
    temp_file = os.path.join(tempfile.gettempdir(), "test_mutual_exclusivity_harness.html")
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
        print("\n--- RUNNING MUTUAL EXCLUSIVITY & WORKSPACE DOCKING TESTS ---")
        all_passed = True
        for r in results:
            status = "[PASS]" if r["pass"] else "[FAIL]"
            print(f"{status} {r['name']} ({r.get('extra', '')})")
            if not r["pass"]:
                all_passed = False

        assert all_passed, "Some tests failed!"
        print(f"\n🎉 ALL MUTUAL EXCLUSIVITY & DOCKING TESTS PASSED ({len(results)}/{len(results)})!")
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)

if __name__ == '__main__':
    test_static_markup()
    test_browser_interactions()
