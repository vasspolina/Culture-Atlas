#!/usr/bin/env python3
import os
import sys
import json
import subprocess
import tempfile

def test_collapse_and_close_buttons():
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
        const inst = window.ALL_INSTITUTIONS && window.ALL_INSTITUTIONS[0];
        assert('Institution exists', !!inst);

        // 1. Select institution to open dossier column
        window.selectInstitution(inst, false);
        const dCol = document.getElementById('desktopDossierColumn');
        const cCol = document.getElementById('curatorIntelligenceColumn');
        const collapseBtn = document.getElementById('collapseDossierBtn');
        const closeBtn = document.getElementById('closeDesktopDossierBtn');
        const tabChat = document.getElementById('workspaceTabChat');
        const tabDossier = document.getElementById('workspaceTabDossier');

        assert('desktopDossierColumn is open on select', dCol && !dCol.classList.contains('hidden') && window.getComputedStyle(dCol).display === 'flex');
        assert('collapseDossierBtn exists', !!collapseBtn);
        assert('closeDesktopDossierBtn exists', !!closeBtn);

        // 2. Click collapseDossierBtn
        collapseBtn.click();
        assert('After collapse click: desktopDossierColumn has hidden class', dCol.classList.contains('hidden'));
        assert('After collapse click: desktopDossierColumn display is none', window.getComputedStyle(dCol).display === 'none');
        assert('After collapse click: curatorIntelligenceColumn is visible', cCol && !cCol.classList.contains('hidden') && window.getComputedStyle(cCol).display === 'flex');
        assert('After collapse click: workspaceTabChat is active', tabChat && tabChat.className.includes('bg-[#262626]'));

        // 3. Re-open dossier column via toggleDesktopDossier(true) or selectInstitution
        window.toggleDesktopDossier(true);
        assert('Reopened: desktopDossierColumn is flex', !dCol.classList.contains('hidden') && window.getComputedStyle(dCol).display === 'flex');

        // 4. Click closeDesktopDossierBtn
        closeBtn.click();
        assert('After close click: desktopDossierColumn has hidden class', dCol.classList.contains('hidden'));
        assert('After close click: desktopDossierColumn display is none', window.getComputedStyle(dCol).display === 'none');
        assert('After close click: curatorIntelligenceColumn is visible', cCol && !cCol.classList.contains('hidden') && window.getComputedStyle(cCol).display === 'flex');
        assert('After close click: workspaceTabChat is active', tabChat && tabChat.className.includes('bg-[#262626]'));

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
    temp_file = os.path.join(tempfile.gettempdir(), "test_collapse_buttons_harness.html")
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

    print("--- RUNNING COLLAPSE & CLOSE BUTTONS TEST ---")
    all_pass = True
    for r in results:
        status = "[PASS]" if r["pass"] else "[FAIL]"
        print(f"{status} {r['name']} ({r.get('extra', '')})")
        if not r["pass"]:
            all_pass = False

    print(f"\nTOTAL: {sum(1 for r in results if r['pass'])} passed, {sum(1 for r in results if not r['pass'])} failed")
    assert all_pass, "Some button collapse tests failed!"
    print("ALL COLLAPSE & CLOSE BUTTON TESTS PASSED!")

if __name__ == "__main__":
    test_collapse_and_close_buttons()
