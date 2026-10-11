import os
import subprocess
import json
import tempfile

def run_tests():
    index_path = "/Users/polinavasilyeva/.gemini/antigravity/scratch/sponsor-atlas/index.html"
    assert os.path.exists(index_path), "index.html must exist"

    with open(index_path, "r", encoding="utf-8") as f:
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
        results.push({ name, pass: !!condition, extra });
      }

      try {
        // 1. Verify absence of user-facing Google 3D links
        const allText = document.body.innerText;
        assert('Zero user-facing occurrences of Google 3D', !allText.includes('Google 3D'), allText.includes('Google 3D') ? 'Found Google 3D in text' : 'Clean');

        // 2. Mobile Quick 3D button on top filter chips
        const quick3DBtn = document.getElementById('mobileQuick3DBtn');
        assert('mobileQuick3DBtn exists', !!quick3DBtn);
        assert('mobileQuick3DBtn has 3D label', quick3DBtn && quick3DBtn.innerText.includes('3D'));

        // 3. Dossier sheet 3D Building button
        const sheet3DBtn = document.getElementById('dossier-sheet-link-3d');
        assert('dossier-sheet-link-3d exists', !!sheet3DBtn);
        assert('dossier-sheet-link-3d has 3D Building label', sheet3DBtn && sheet3DBtn.innerText.includes('3D Building'));
        assert('dossier-sheet-link-3d does not say Google 3D', sheet3DBtn && !sheet3DBtn.innerText.includes('Google 3D'));

        // 4. Dossier bottom sheet and 3D Active Indicator
        const bottomSheet = document.getElementById('dossier-bottom-sheet');
        const indicator = document.getElementById('mobile3DActiveIndicator');
        const backBtn = document.getElementById('mobile3DBackToDossierBtn');
        assert('dossier-bottom-sheet exists', !!bottomSheet);
        assert('mobile3DActiveIndicator exists', !!indicator);
        assert('mobile3DBackToDossierBtn exists', !!backBtn);

        // Initial state on mobile
        assert('Indicator initially hidden', indicator && indicator.classList.contains('hidden'));

        // Click 3D Building button on sheet
        sheet3DBtn.click();

        // Check that bottom sheet is hidden and 3D indicator is revealed
        assert('Bottom sheet hidden after 3D Building click', bottomSheet && bottomSheet.classList.contains('hidden'));
        assert('3D Active Indicator revealed after 3D Building click', indicator && !indicator.classList.contains('hidden'));

        // Click Back To Dossier
        backBtn.click();
        assert('Bottom sheet restored after Back To Dossier click', bottomSheet && !bottomSheet.classList.contains('hidden'));
        assert('3D Active Indicator hidden after Back To Dossier click', indicator && indicator.classList.contains('hidden'));

        // Verify PP Museum font is applied
        const btnStyle = window.getComputedStyle(sheet3DBtn);
        assert('sheet3DBtn uses PP Museum font', btnStyle.fontFamily.includes('PP Museum'), btnStyle.fontFamily);

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
    temp_file = os.path.join(tempfile.gettempdir(), "test_mobile_3d_in_map.html")
    with open(temp_file, "w", encoding="utf-8") as f:
        f.write(harness_html)

    chrome_bin = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    cmd = [
        chrome_bin,
        "--headless=new",
        "--dump-dom",
        "--window-size=390,844",
        f"file://{temp_file}"
    ]

    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    import re
    match = re.search(r'data-results="([^"]+)"', res.stdout)
    assert match, "Could not find test-results-output in DOM dump"

    raw_json = match.group(1).replace("&quot;", '"')
    results = json.loads(raw_json)

    all_passed = True
    print("\n--- RUNNING MOBILE 3D IN-MAP ENGINE & NO GOOGLE 3D TESTS ---")
    for r in results:
        status = "PASS" if r["pass"] else "FAIL"
        extra = f" ({r['extra']})" if r.get("extra") else ""
        print(f"[{status}] {r['name']}{extra}")
        if not r["pass"]:
            all_passed = False

    if not all_passed:
        print("\n❌ SOME MOBILE 3D IN-MAP TESTS FAILED!")
        exit(1)
    else:
        print(f"\n🎉 ALL MOBILE 3D IN-MAP ASSERTIONS PASSED ({len(results)}/{len(results)})!")

if __name__ == "__main__":
    run_tests()
