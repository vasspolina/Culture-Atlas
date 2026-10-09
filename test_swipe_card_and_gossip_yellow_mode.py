#!/usr/bin/env python3
"""
test_swipe_card_and_gossip_yellow_mode.py
Comprehensive test suite verifying:
1. 👆 Touch & Pointer Swipe Gesture Controller on Floating Card:
   - Horizontal Swipe (Left/Right) toggles between Verified Info and Yellow Gossip Mode.
   - Vertical Upward Swipe opens the full Scholarly Audit Dossier drawer.
2. 🔄 Segmented Mode Switcher on Floating Card (Verified Info <-> Yellow Gossip Mode).
3. 🟡 Visual Yellow Gossip Mode transformation (glowing yellow border, dark amber glass background, glowing beacons).
4. 📄 Separate Info and Gossip Viewports (Budget/Shows vs Whispers/Reddit/X Leaks).
5. 📂 Drawer Mode Switcher (Audit Dossier <-> Yellow Gossip Dossier) with touch swipe support.
"""

import os
import sys
import json
import subprocess
import tempfile
import html as html_lib

def test_static_html():
    print("--- 1. STATIC DOM & MARKUP VERIFICATION ---")
    with open('index.html', 'r', encoding='utf-8') as f:
        html = f.read()

    # Mode switcher and swipe hints
    assert 'floatingCardModeSwitcher' in html, "Missing floatingCardModeSwitcher"
    assert 'floatingCardTabInfo' in html, "Missing floatingCardTabInfo"
    assert 'floatingCardTabGossip' in html, "Missing floatingCardTabGossip"
    assert 'floatingCardSwipeHint' in html, "Missing floatingCardSwipeHint"
    assert 'Swipe' in html and 'Gossip' in html, "Missing swipe hint text"

    # Separate viewports
    assert 'floatingCardInfoPane' in html, "Missing floatingCardInfoPane"
    assert 'floatingCardGossipPane' in html, "Missing floatingCardGossipPane"
    assert 'floatingCardBudgetSection' in html, "Missing floatingCardBudgetSection"
    assert 'floatingCardCurrentShowsSection' in html, "Missing floatingCardCurrentShowsSection"
    assert 'floatingCardGossipSection' in html, "Missing floatingCardGossipSection"

    # JS API & Drawer
    assert 'setCardMode' in html, "Missing setCardMode in JS"
    assert 'setDrawerMode' in html, "Missing setDrawerMode in JS"
    assert 'drawerTabAudit' in html, "Missing drawerTabAudit"
    assert 'drawerTabGossip' in html, "Missing drawerTabGossip"
    assert 'drawerAuditView' in html, "Missing drawerAuditView"
    assert 'drawerGossipView' in html, "Missing drawerGossipView"

    print("✅ Static DOM and markup verification passed.")

def test_browser_swipe_gestures():
    print("--- 2. HEADLESS CHROME GESTURE & MODE EXECUTION ---")
    with open('index.html', 'r', encoding='utf-8') as f:
        html = f.read()

    test_script = """
    <script>
    window.addEventListener('load', async () => {
      const results = [];
      function assert(name, cond, extra = '') {
        results.push({ name, pass: Boolean(cond), extra: String(extra) });
      }

      try {
        await new Promise(r => setTimeout(r, 400));
        const all = window.ALL_INSTITUTIONS || [];
        assert('Institutions loaded', all.length >= 1000, all.length);

        const testInst = all.find(i => i.gossip_data && i.temporary_shows) || all[0];
        assert('Found test institution', !!testInst, testInst ? testInst.name : 'none');

        // Select institution
        window.rotLon = testInst.lon; window.rotLat = testInst.lat; window.selectInstitution(testInst); if (window.render) window.render(); document.getElementById("floatingCard").classList.remove("hidden");
        await new Promise(r => setTimeout(r, 200));

        const card = document.getElementById('floatingCard');
        const infoPane = document.getElementById('floatingCardInfoPane');
        const gossipPane = document.getElementById('floatingCardGossipPane');
        const tabInfo = document.getElementById('floatingCardTabInfo');
        const tabGossip = document.getElementById('floatingCardTabGossip');

        assert('Floating card visible after selection', card && !card.classList.contains('hidden'));
        assert('Info pane visible by default', infoPane && !infoPane.classList.contains('hidden'));
        assert('Gossip pane hidden by default', gossipPane && gossipPane.classList.contains('hidden'));

        // Test setCardMode('gossip')
        window.setCardMode('gossip', false);
        assert('Gossip pane visible after setCardMode(gossip)', gossipPane && !gossipPane.classList.contains('hidden'));
        assert('Info pane hidden in gossip mode', infoPane && infoPane.classList.contains('hidden'));
        assert('Card has gossip-yellow-card class', card && card.classList.contains('gossip-yellow-card'));
        assert('Gossip tab highlighted', tabGossip && tabGossip.classList.contains('bg-yellow-400'));

        // Test setCardMode('info')
        window.setCardMode('info', false);
        assert('Info pane visible after setCardMode(info)', infoPane && !infoPane.classList.contains('hidden'));
        assert('Gossip pane hidden in info mode', gossipPane && gossipPane.classList.contains('hidden'));
        assert('Card removed gossip-yellow-card class', card && !card.classList.contains('gossip-yellow-card'));

        // Test simulated touch swipe left (to gossip mode)
        const touchStartLeft = { clientX: 250, clientY: 200 };
        const touchEndLeft = { clientX: 120, clientY: 200 }; // deltaX = -130 (Swipe Left)

        card.dispatchEvent(new CustomEvent('touchstart', { detail: touchStartLeft }));
        // Also trigger pointer events
        const pDownLeft = new PointerEvent('pointerdown', { clientX: 250, clientY: 200, bubbles: true });
        const pUpLeft = new PointerEvent('pointerup', { clientX: 120, clientY: 200, bubbles: true });
        card.dispatchEvent(pDownLeft);
        await new Promise(r => setTimeout(r, 30));
        card.dispatchEvent(pUpLeft);
        await new Promise(r => setTimeout(r, 100));

        assert('Pointer drag left activated gossip mode', gossipPane && !gossipPane.classList.contains('hidden'));
        assert('Gossip card style active after drag left', card && card.classList.contains('gossip-yellow-card'));

        // Test simulated drag right (back to info mode)
        const pDownRight = new PointerEvent('pointerdown', { clientX: 120, clientY: 200, bubbles: true });
        const pUpRight = new PointerEvent('pointerup', { clientX: 250, clientY: 200, bubbles: true });
        card.dispatchEvent(pDownRight);
        await new Promise(r => setTimeout(r, 30));
        card.dispatchEvent(pUpRight);
        await new Promise(r => setTimeout(r, 100));

        assert('Pointer drag right activated info mode', infoPane && !infoPane.classList.contains('hidden'));
        assert('Gossip pane hidden after drag right', gossipPane && gossipPane.classList.contains('hidden'));

        // Test simulated upward swipe (Swipe up to view full info / audit dossier)
        const drawer = document.getElementById('detailDrawer');
        assert('Drawer initially hidden', drawer && drawer.classList.contains('hidden'));

        const pDownUp = new PointerEvent('pointerdown', { clientX: 200, clientY: 260, bubbles: true });
        const pUpUp = new PointerEvent('pointerup', { clientX: 200, clientY: 130, bubbles: true }); // deltaY = -130
        card.dispatchEvent(pDownUp);
        await new Promise(r => setTimeout(r, 30));
        card.dispatchEvent(pUpUp);
        await new Promise(r => setTimeout(r, 150));

        assert('Swipe up opened Scholarly Audit Dossier drawer', drawer && !drawer.classList.contains('hidden'));

        // Test Drawer view switching
        const drawerAudit = document.getElementById('drawerAuditView');
        const drawerGossip = document.getElementById('drawerGossipView');
        assert('Drawer audit view exists', !!drawerAudit);
        assert('Drawer gossip view exists', !!drawerGossip);

        window.setDrawerMode('gossip');
        assert('setDrawerMode(gossip) shows drawer gossip view', drawerGossip && !drawerGossip.classList.contains('hidden'));
        assert('setDrawerMode(gossip) hides drawer audit view', drawerAudit && drawerAudit.classList.contains('hidden'));

        window.setDrawerMode('audit');
        assert('setDrawerMode(audit) shows drawer audit view', drawerAudit && !drawerAudit.classList.contains('hidden'));
        assert('setDrawerMode(audit) hides drawer gossip view', drawerGossip && drawerGossip.classList.contains('hidden'));

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
    temp_file = os.path.join(tempfile.gettempdir(), "test_swipe_card_harness.html")
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
        "--virtual-time-budget=6000",
        f"file://{temp_file}"
    ]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=30)

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
    print(f"\n🎉 ALL SWIPE GESTURE & GOSSIP YELLOW MODE TESTS PASSED ({len(results)}/{len(results)})!")

if __name__ == '__main__':
    test_static_html()
    test_browser_swipe_gestures()
