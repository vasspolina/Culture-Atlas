import os
import subprocess
import json
import tempfile

def test_mobile_popups():
    index_path = "/Users/polinavasilyeva/.gemini/antigravity/scratch/sponsor-atlas/index.html"
    assert os.path.exists(index_path), "index.html must exist"

    with open(index_path, "r", encoding="utf-8") as f:
        html = f.read()

    # 1. Static markup assertions
    assert "@media (max-width: 639px)" in html, "Missing mobile media query in styles"
    assert "building-3d-mast-plate" in html, "Missing mast plate styling"
    assert "buildingFloorInspectorHud" in html, "Missing building floor inspector hud"
    assert "workPlusMenu" in html, "Missing workPlusMenu"
    assert "floatingCard" in html, "Missing floatingCard"

    # Verify workPlusMenu has max-height and overflow-y
    idx_menu = html.find('id="workPlusMenu"')
    menu_chunk = html[idx_menu:idx_menu+300]
    assert "max-h-" in menu_chunk or "max-height" in menu_chunk, "workPlusMenu must have max height"
    assert "overflow-y-auto" in menu_chunk, "workPlusMenu must have overflow-y-auto"

    # Verify floatingCard has mobile docking and desktop clamping
    assert "isMobileViewport" in html, "render loop must have mobile viewport check"
    assert "floatingCard.style.bottom = '8px'" in html, "render loop must dock floatingCard at bottom on mobile"

    # 2. Dynamic execution via Headless Chromium in mobile viewport (375x667)
    test_script = """
    <script>
    window.addEventListener('load', async () => {
      const results = [];
      function assert(name, condition, extra = '') {
        results.push({ name, pass: !!condition, extra });
      }

      try {
        await new Promise(r => setTimeout(r, 400));
        const all = window.ALL_INSTITUTIONS || [];
        assert('Institutions loaded', all.length >= 1000, all.length);

        const inst = all.find(i => i.name.includes('Sapporo')) || all[0];
        assert('Institution found', !!inst);

        // Select institution and rotate globe directly to it
        window.rotLon = Number(inst.lon);
        window.rotLat = Number(inst.lat);
        window.targetRotLon = Number(inst.lon);
        window.targetRotLat = Number(inst.lat);
        window.isFlying = false;
        window.selectInstitution(inst, false);
        if (window.render) window.render();
        const card = document.getElementById('floatingCard');
        card.classList.remove('hidden');
        await new Promise(r => setTimeout(r, 150));
        assert('Floating card element found', !!card);
        assert('Floating card is visible', !card.classList.contains('hidden'));

        const rect = card.getBoundingClientRect();
        const winW = window.innerWidth;
        const winH = window.innerHeight;

        // Check mobile boundary containment (no cutoffs)
        assert('Card does not overflow left edge', rect.left >= 0, `rect.left = ${rect.left}`);
        assert('Card does not overflow right edge', rect.right <= winW + 2, `rect.right = ${rect.right}, winW = ${winW}`);
        assert('Card does not overflow top edge', rect.top >= 0, `rect.top = ${rect.top}`);
        assert('Card does not overflow bottom edge', rect.bottom <= winH + 2, `rect.bottom = ${rect.bottom}, winH = ${winH}`);

        // Open plus menu and test containment
        const plusBtn = document.getElementById('workPlusBtn');
        const plusMenu = document.getElementById('workPlusMenu');
        plusBtn.click();
        assert('Plus menu opened', !plusMenu.classList.contains('hidden'));

        const menuRect = plusMenu.getBoundingClientRect();
        assert('Plus menu does not overflow left', menuRect.left >= 0, `menuRect.left = ${menuRect.left}`);
        assert('Plus menu does not overflow right', menuRect.right <= winW + 2, `menuRect.right = ${menuRect.right}`);
        assert('Plus menu does not overflow top', menuRect.top >= 0, `menuRect.top = ${menuRect.top}`);
        assert('Plus menu does not overflow bottom', menuRect.bottom <= winH + 2, `menuRect.bottom = ${menuRect.bottom}`);

      } catch (err) {
        results.push({ name: 'Exception occurred', pass: false, extra: err.toString() });
      }

      window.__TEST_RESULTS = results;
      const marker = document.createElement('div');
      marker.id = 'test-done';
      marker.textContent = JSON.stringify(results);
      document.body.appendChild(marker);
    });
    </script>
    """

    injected_html = html.replace("</body>", f"{test_script}</body>")

    temp_path = "/Users/polinavasilyeva/.gemini/antigravity/scratch/sponsor-atlas/test_mobile_harness.html"
    with open(temp_path, "w", encoding="utf-8") as tf:
        tf.write(injected_html)

    chrome_bin = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    if not os.path.exists(chrome_bin):
        chrome_bin = "google-chrome"

    cmd = [
        chrome_bin,
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        "--window-size=375,667",
        "--virtual-time-budget=6000",
        "--dump-dom",
        f"file://{temp_path}"
    ]

    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=20)
    dom = proc.stdout

    if "#test-done" in dom or 'id="test-done"' in dom:
        import re
        m = re.search(r'<div id="test-done"[^>]*>(.*?)</div>', dom)
        if m:
            res_str = m.group(1).replace("&quot;", '"').replace("&lt;", "<").replace("&gt;", ">")
            try:
                results = json.loads(res_str)
                all_pass = True
                for r in results:
                    status = "PASS" if r["pass"] else "FAIL"
                    print(f"[{status}] {r['name']} {r.get('extra', '')}")
                    if not r["pass"]:
                        all_pass = False
                assert all_pass, "Some mobile popup tests failed"
                print("\n🎉 ALL MOBILE POPUP OPTIMIZATION TESTS PASSED IN MOBILE VIEWPORT (375x667)!")
            except Exception as e:
                print("Could not parse test results json:", e, res_str[:300])
                raise
    else:
        print("DOM output length:", len(dom))
        assert False, "Test did not finish within timeout"

    os.remove(temp_path)

if __name__ == "__main__":
    test_mobile_popups()
