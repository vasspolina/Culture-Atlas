import subprocess
import tempfile
import html as html_lib
import json
import os

def test_show_only_on_click():
    index_path = os.path.abspath("index.html")
    with open(index_path, "r", encoding="utf-8") as f:
        html = f.read()

    test_script = """
    <script>
    window.addEventListener('load', async () => {
      const results = [];
      function assert(name, condition, extra = '') {
        results.push({ name, pass: !!condition, extra: String(extra) });
      }

      try {
        // Step 1: Open city street view for Bilbao
        filterByCity('Bilbao', true, false);
        await new Promise(r => setTimeout(r, 600));

        const cityContainer = document.getElementById('cityMapContainer');
        assert('cityMapContainer is visible for Bilbao', cityContainer && !cityContainer.classList.contains('hidden'));
        assert('isCityStreetViewActive is true', isCityStreetViewActive === true);

        // Verify NO popups or floating cards show automatically on city navigation!
        const floatingCard = document.getElementById('floatingCard');
        assert('floatingCard is HIDDEN initially on city navigation', floatingCard && floatingCard.classList.contains('hidden'));
        
        let popups = document.querySelectorAll('.maplibregl-popup');
        assert('ZERO MapLibre popups open automatically on city navigation', popups.length === 0, `found: ${popups.length}`);

        // Step 2: Find the pin for Bulegoa z/b
        const pin = document.querySelector('.custom-inst-pin');
        assert('Pin element exists in DOM', !!pin);

        // Click the pin
        pin.click();
        await new Promise(r => setTimeout(r, 400));

        // Verify exactly ONE popup opens on explicit click
        popups = document.querySelectorAll('.maplibregl-popup');
        assert('Exactly 1 MapLibre popup opens ON CLICK', popups.length === 1, `found: ${popups.length}`);

        // Verify floatingCard remains hidden (NO duplicate popup!)
        assert('floatingCard remains HIDDEN on city street view (no duplicate)', floatingCard.classList.contains('hidden'));

        // Verify popup content
        const popupText = popups[0] ? popups[0].textContent : '';
        assert('Popup contains Bulegoa z/b', popupText.includes('Bulegoa z/b'));
        assert('Popup contains Visit Website', popupText.includes('Visit Website'));
        assert('Popup contains Plan Visit or Hours', popupText.includes('16:30') || popupText.includes('Visit'));
        assert('Popup contains Read info about institution', popupText.includes('Read info about institution'));
        assert('Popup contains Ask', popupText.includes('Ask'));

        // Step 3: Test dismissing on close button
        const closeBtn = document.querySelector('.maplibregl-popup-close-button');
        assert('Close button exists on popup', !!closeBtn);
        if (closeBtn) {
          closeBtn.click();
          await new Promise(r => setTimeout(r, 300));
          popups = document.querySelectorAll('.maplibregl-popup');
          assert('Popup is dismissed after clicking close button', popups.length === 0, `found: ${popups.length}`);
        }

        // Step 4: Click the pin label to verify clicking label also opens popup
        const label = document.querySelector('.inst-pin-label');
        assert('inst-pin-label exists', !!label);
        if (label) {
          label.click();
          await new Promise(r => setTimeout(r, 400));
          popups = document.querySelectorAll('.maplibregl-popup');
          assert('Popup opens on clicking institution name label', popups.length === 1, `found: ${popups.length}`);
        }

        // Step 5: Exit street view back to globe
        exitCityStreetView();
        await new Promise(r => setTimeout(r, 400));
        assert('isCityStreetViewActive is false after exit', isCityStreetViewActive === false);
        assert('cityMapContainer is hidden', cityContainer.classList.contains('hidden'));
        assert('floatingCard is hidden after exit', floatingCard.classList.contains('hidden'));

      } catch (err) {
        results.push({ name: 'Exception caught', pass: false, extra: err.toString() });
      }

      const div = document.createElement('div');
      div.id = 'test-results-output';
      div.setAttribute('data-results', JSON.stringify(results));
      document.body.appendChild(div);
    });
    </script>
    """

    harness_html = html.replace("</body>", f"{test_script}</body>")
    temp_file = os.path.join(tempfile.gettempdir(), "test_show_only_on_click_harness.html")
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

    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=25)
    marker = 'id="test-results-output" data-results="'
    assert marker in proc.stdout, f"Marker not found in stdout: {proc.stdout[:400]}"

    results = json.loads(html_lib.unescape(proc.stdout.split(marker)[1].split('"')[0]))
    print("\n--- RUNNING SHOW ONLY ON CLICK HEADLESS SUITE ---")
    all_pass = True
    for r in results:
        status = "PASS" if r["pass"] else "FAIL"
        extra = f" ({r['extra']})" if r.get("extra") else ""
        print(f"[{status}] {r['name']}{extra}")
        if not r["pass"]:
            all_pass = False

    assert all_pass, "Some tests failed!"
    print(f"\nALL SHOW ONLY ON CLICK TESTS PASSED ({len(results)}/{len(results)})!\n")

if __name__ == "__main__":
    test_show_only_on_click()
