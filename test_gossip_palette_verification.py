#!/usr/bin/env python3
"""
test_gossip_palette_verification.py
Verify that Gossip Mode colors are altered to a distinct nocturnal velvet plum & electric rose palette:
1. CSS rules for body.gossip-mode-active, header, #globeViewport, #workBottomDock, #floatingCard.
2. window.toggleGossipMode() properly adds/removes body.gossip-mode-active.
3. Gossip mode button styling toggles between inactive dark wine pill and active glowing rose/fuchsia gradient.
4. Floating card switch to gossip mode applies the new rose accent and background.
5. Inactive mode restores normal styling without residual gossip styles.
"""

import os
import sys
import json
import subprocess
import tempfile
import html as html_lib

def test_css_and_markup():
    print("--- 1. STATIC CSS & CODE VERIFICATION ---")
    with open('index.html', 'r', encoding='utf-8') as f:
        html = f.read()

    assert 'body.gossip-mode-active' in html, "Missing body.gossip-mode-active style rule"
    assert '#23082b' in html or '#130419' in html, "Missing velvet wine background gradient in CSS"
    assert 'rgba(244, 63, 94' in html or '#f43f5e' in html, "Missing electric rose accent in CSS"
    assert 'gossip-mode-active' in html, "Missing gossip-mode-active class in script logic"
    assert 'toggleGossipMode' in html, "Missing toggleGossipMode function"
    
    print("✅ Static CSS and markup verification passed.")

def test_browser_gossip_palette():
    print("--- 2. HEADLESS CHROME GOSSIP PALETTE VERIFICATION ---")
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
        await new Promise(r => setTimeout(r, 400));
        
        const body = document.body;
        const topGossipBtn = document.getElementById('topGossipBtn');
        const floatingCard = document.getElementById('floatingCard');
        
        assert('Top Gossip button exists', !!topGossipBtn);
        assert('Body initially does not have gossip-mode-active', !body.classList.contains('gossip-mode-active'));
        assert('isGossipModeActive is false initially', window.isGossipModeActive === false);

        // Toggle Gossip Mode ON
        window.toggleGossipMode();
        await new Promise(r => setTimeout(r, 100));

        assert('Body has gossip-mode-active class when active', body.classList.contains('gossip-mode-active'));
        assert('isGossipModeActive is true when active', window.isGossipModeActive === true);
        assert('Top Gossip button shows active text', topGossipBtn.textContent.toLowerCase().includes('active'));
        assert('Top Gossip button has active gradient class', topGossipBtn.className.includes('from-rose-600') || topGossipBtn.className.includes('rose'));

        // Check computed styles on body or elements under gossip-mode-active
        const bodyBg = window.getComputedStyle(body).backgroundImage || window.getComputedStyle(body).background;
        assert('Body has custom background gradient in gossip mode', bodyBg.includes('gradient') || bodyBg.includes('rgb'));

        // Test floating card in gossip mode
        const all = window.ALL_INSTITUTIONS || [];
        const testInst = all.find(i => i.gossip_data) || all[0];
        if (testInst && window.selectInstitution) {
          window.selectInstitution(testInst);
          floatingCard.classList.remove('hidden');
          await new Promise(r => setTimeout(r, 100));
          
          window.setCardMode('gossip', false);
          assert('Card has gossip mode class', floatingCard.classList.contains('gossip-active-card') || floatingCard.classList.contains('gossip-yellow-card'));
          
          const tabGossip = document.getElementById('floatingCardTabGossip');
          assert('Gossip tab active styling', tabGossip && tabGossip.className.includes('rose'));
        }

        // Toggle Gossip Mode OFF
        window.toggleGossipMode();
        await new Promise(r => setTimeout(r, 100));

        assert('Body removed gossip-mode-active class when deactivated', !body.classList.contains('gossip-mode-active'));
        assert('isGossipModeActive is false when deactivated', window.isGossipModeActive === false);
        assert('Top Gossip button restored inactive text', !topGossipBtn.textContent.includes('ACTIVE'));
        assert('Top Gossip button restored dark wine pill class', topGossipBtn.className.includes('bg-[#1f0a1c]') || topGossipBtn.className.includes('rose-300'));

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
    temp_file = os.path.join(tempfile.gettempdir(), "test_gossip_palette_harness.html")
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
    print(f"\n🎉 ALL GOSSIP PALETTE TESTS PASSED ({len(results)}/{len(results)})!")

if __name__ == '__main__':
    test_css_and_markup()
    test_browser_gossip_palette()
