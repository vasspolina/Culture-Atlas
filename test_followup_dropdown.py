#!/usr/bin/env python3
import os
import sys
import json
import subprocess
import tempfile

def test_followup_dropdown():
    index_path = "/Users/polinavasilyeva/.gemini/antigravity/scratch/sponsor-atlas/index.html"
    assert os.path.exists(index_path), "index.html must exist"

    with open(index_path, "r", encoding="utf-8") as f:
        html = f.read()

    test_script = """
    <script>
    window.requestAnimationFrame = () => 1;
    window.cancelAnimationFrame = () => {};
    window.fetch = async () => new Response("{}", { status: 200, headers: { 'Content-Type': 'application/json' } });

    window.addEventListener('DOMContentLoaded', async () => {
      const results = [];
      function assert(name, cond, extra = '') {
        results.push({ name, pass: Boolean(cond), extra: String(extra) });
      }

      try {
        // Trigger a curator message with follow-up suggestions
        window.appendCuratorMessage('Test curator response', [
          'Who funds this museum?',
          'What do employees say about working here?',
          'Does this institution pay artists fairly?'
        ]);

        const dropdownWrap = document.querySelector('.curator-followups-dropdown-wrap');
        assert('Dropdown wrap exists in curator message', !!dropdownWrap);

        const toggleBtn = dropdownWrap ? dropdownWrap.querySelector('.curator-followups-toggle') : null;
        assert('Dropdown toggle button exists', !!toggleBtn);

        const menu = dropdownWrap ? dropdownWrap.querySelector('div[id^="followUpMenu_"]') : null;
        assert('Dropdown menu exists', !!menu);
        assert('Dropdown menu is initially hidden', menu && menu.classList.contains('hidden'));

        // Click to toggle open
        if (toggleBtn) toggleBtn.click();
        assert('Dropdown menu is visible after click', menu && !menu.classList.contains('hidden'));
        assert('Toggle aria-expanded is true', toggleBtn && toggleBtn.getAttribute('aria-expanded') === 'true');

        // Check items inside dropdown
        const items = menu ? menu.querySelectorAll('.curator-followup-pill') : [];
        assert('Dropdown contains 3 follow-up queries', items.length === 3, items.length);

        // Click to toggle closed
        if (toggleBtn) toggleBtn.click();
        assert('Dropdown menu is hidden after second click', menu && menu.classList.contains('hidden'));
        assert('Toggle aria-expanded is false', toggleBtn && toggleBtn.getAttribute('aria-expanded') === 'false');

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
    temp_file = os.path.join(tempfile.gettempdir(), "test_followup_dropdown_harness.html")
    with open(temp_file, "w", encoding="utf-8") as f:
        f.write(harness_html)

    chrome_bin = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    cmd = [
        chrome_bin,
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        "--window-size=1440,900",
        "--run-all-compositor-stages-before-draw",
        "--virtual-time-budget=4000",
        "--dump-dom",
        f"file://{temp_file}"
    ]

    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    dom_output = res.stdout

    marker = 'id="test-results-output" data-results="'
    idx = dom_output.find(marker)
    assert idx != -1, f"Could not find test output in DOM. Stderr: {res.stderr}"

    start_idx = idx + len(marker)
    end_idx = dom_output.find('"', start_idx)
    raw_json = dom_output[start_idx:end_idx]
    import html as html_lib
    unescaped_json = html_lib.unescape(raw_json)
    results = json.loads(unescaped_json)

    print("--- RUNNING FOLLOWUP DROPDOWN TEST ---")
    all_pass = True
    for r in results:
        status = "[PASS]" if r["pass"] else "[FAIL]"
        print(f"{status} {r['name']} ({r.get('extra', '')})")
        if not r["pass"]:
            all_pass = False

    print(f"\nTOTAL: {sum(1 for r in results if r['pass'])} passed, {sum(1 for r in results if not r['pass'])} failed")
    assert all_pass, "Some follow-up dropdown tests failed!"
    print("ALL FOLLOWUP DROPDOWN TESTS PASSED!")

if __name__ == "__main__":
    test_followup_dropdown()
