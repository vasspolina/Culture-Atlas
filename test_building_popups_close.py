import os
import subprocess
import json
import re

def test_static_markup():
    with open("app/index.html", "r", encoding="utf-8") as f:
        html = f.read()

    assert "building-mast-close-btn" in html, "building-mast-close-btn missing in app/index.html"
    assert "window.closeBuildingMast()" in html, "window.closeBuildingMast() missing in app/index.html"
    assert "building-facade-close-btn" in html, "building-facade-close-btn missing in app/index.html"
    assert "window.closeBuildingFacade()" in html, "window.closeBuildingFacade() missing in app/index.html"
    assert "window.closeBuildingMast = closeBuildingMast" in html, "closeBuildingMast export missing"
    assert "window.closeBuildingFacade = closeBuildingFacade" in html, "closeBuildingFacade export missing"
    print("[PASS] Static markup and JS function signatures verified!")

def test_headless_execution():
    with open("app/index.html", "r", encoding="utf-8") as f:
        html = f.read()

    test_script = """
    <script>
    window.addEventListener('load', async () => {
      const results = [];
      function assert(name, condition, extra = '') {
        results.push({ name, pass: !!condition, extra });
      }

      try {
        await new Promise(r => setTimeout(r, 400));
        assert('closeBuildingMast is function', typeof window.closeBuildingMast === 'function');
        assert('closeBuildingFacade is function', typeof window.closeBuildingFacade === 'function');

        // Verify simulated building popup creation and close handlers
        let mast = document.createElement('div');
        mast.className = 'building-3d-mast-plate';
        mast.innerHTML = '<button type="button" class="building-mast-close-btn" onclick="window.closeBuildingMast();">x</button>';
        document.body.appendChild(mast);

        let facade = document.createElement('div');
        facade.className = 'building-3d-facade-stack';
        facade.innerHTML = '<button type="button" class="building-facade-close-btn" onclick="window.closeBuildingFacade();">x</button>';
        document.body.appendChild(facade);

        assert('Mast element exists in DOM', !!document.querySelector('.building-3d-mast-plate'));
        assert('Facade element exists in DOM', !!document.querySelector('.building-3d-facade-stack'));

        // Close Mast
        window.closeBuildingMast();
        assert('Mast element removed after closeBuildingMast()', !document.querySelector('.building-3d-mast-plate'));
        assert('Facade element persists when only mast is closed', !!document.querySelector('.building-3d-facade-stack'));

        // Close Facade
        window.closeBuildingFacade();
        assert('Facade element removed after closeBuildingFacade()', !document.querySelector('.building-3d-facade-stack'));

      } catch (err) {
        results.push({ name: 'Exception occurred', pass: false, extra: err.toString() });
      }

      const marker = document.createElement('div');
      marker.id = 'test-done';
      marker.textContent = JSON.stringify(results);
      document.body.appendChild(marker);
    });
    </script>
    """

    injected_html = html.replace("</body>", f"{test_script}</body>")
    temp_path = "/Users/polinavasilyeva/.gemini/antigravity/scratch/sponsor-atlas/test_close_harness.html"
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
        "--window-size=1200,900",
        "--virtual-time-budget=5000",
        "--dump-dom",
        f"file://{temp_path}"
    ]

    try:
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=20)
        dom = proc.stdout

        if "#test-done" in dom or 'id="test-done"' in dom:
            m = re.search(r'<div id="test-done"[^>]*>(.*?)</div>', dom)
            if m:
                res_str = m.group(1).replace("&quot;", '"').replace("&lt;", "<").replace("&gt;", ">")
                results = json.loads(res_str)
                all_pass = True
                for r in results:
                    status = "PASS" if r["pass"] else "FAIL"
                    print(f"[{status}] {r['name']} {r.get('extra', '')}")
                    if not r["pass"]:
                        all_pass = False
                assert all_pass, "Some building popup close tests failed"
                print("\n🎉 ALL BUILDING POPUP CLOSE BUTTON TESTS PASSED!")
        else:
            assert False, "Test did not finish within timeout"
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

if __name__ == "__main__":
    test_static_markup()
    test_headless_execution()
