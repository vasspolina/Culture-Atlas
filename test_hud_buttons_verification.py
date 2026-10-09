import subprocess
import json
import os
import tempfile
import sys

def run_tests():
    print("--- RUNNING HUD BUTTONS VERIFICATION TEST SUITE ---")
    index_path = "/Users/polinavasilyeva/.gemini/antigravity/scratch/sponsor-atlas/index.html"
    with open(index_path, "r", encoding="utf-8") as f:
        html = f.read()

    # 1. Static assertions
    assert 'id="hudFiscalBtn" type="button" onclick="window.openFiscalAnalyticsHUD();' in html, "hudFiscalBtn missing inline onclick"
    assert 'id="hudTimelineBtn" type="button" onclick="window.openResistanceTimelineModal();' in html, "hudTimelineBtn missing inline onclick"
    assert 'id="hudFilingsBtn" type="button" onclick="window.openStatutoryFilingsModal();' in html, "hudFilingsBtn missing inline onclick"
    assert 'id="hudTrusteesBtn" type="button" onclick="window.openTrusteeConflictNetworkModal();' in html, "hudTrusteesBtn missing inline onclick"
    assert 'id="hudRouteBtn" type="button" onclick="window.openCuratorialItineraryModal();' in html, "hudRouteBtn missing inline onclick"
    assert 'id="hudRailToggle" type="button" onclick="window.toggleRailCorridors(event);"' in html, "hudRailToggle missing inline onclick"
    assert 'id="hudContributeBtn" type="button" onclick="window.triggerInChatContributeFlow();' in html, "hudContributeBtn missing inline onclick"
    assert 'window.toggleRailCorridors = toggleRailCorridors;' in html, "window.toggleRailCorridors missing"
    print("[PASS] Static HTML markup assertions passed.")

    # 2. Browser assertions
    test_script = """
    <script>
    window.addEventListener('DOMContentLoaded', async () => {
      const results = [];
      const assert = (name, cond, details = '') => {
        results.push({ name, pass: !!cond, details });
        if (!cond) console.error('[FAIL]', name, details);
        else console.log('[PASS]', name);
      };

      try {
        // Test hudFiscalBtn
        const fiscalBtn = document.getElementById('hudFiscalBtn');
        assert('hudFiscalBtn exists', !!fiscalBtn);
        fiscalBtn.click();
        const fiscalModal = document.getElementById('fiscalAnalyticsModal');
        assert('hudFiscalBtn opens fiscalAnalyticsModal', fiscalModal && !fiscalModal.classList.contains('hidden'));
        window.closeFiscalAnalyticsHUD();
        assert('fiscalAnalyticsModal closes properly', fiscalModal && fiscalModal.classList.contains('hidden'));

        // Test hudTimelineBtn (Victories)
        const timelineBtn = document.getElementById('hudTimelineBtn');
        assert('hudTimelineBtn exists', !!timelineBtn);
        timelineBtn.click();
        const timelineModal = document.getElementById('resistanceTimelineModal');
        assert('hudTimelineBtn opens resistanceTimelineModal', timelineModal && !timelineModal.classList.contains('hidden'));
        window.closeResistanceTimelineModal();
        assert('resistanceTimelineModal closes properly', timelineModal && timelineModal.classList.contains('hidden'));

        // Test hudFilingsBtn (990s)
        const filingsBtn = document.getElementById('hudFilingsBtn');
        assert('hudFilingsBtn exists', !!filingsBtn);
        filingsBtn.click();
        const filingsModal = document.getElementById('statutoryFilingsModal');
        assert('hudFilingsBtn opens statutoryFilingsModal', filingsModal && !filingsModal.classList.contains('hidden'));
        window.closeStatutoryFilingsModal();
        assert('statutoryFilingsModal closes properly', filingsModal && filingsModal.classList.contains('hidden'));

        // Test hudTrusteesBtn (Boards)
        const trusteesBtn = document.getElementById('hudTrusteesBtn');
        assert('hudTrusteesBtn exists', !!trusteesBtn);
        trusteesBtn.click();
        const trusteesModal = document.getElementById('trusteeConflictNetworkModal');
        assert('hudTrusteesBtn opens trusteeConflictNetworkModal', trusteesModal && !trusteesModal.classList.contains('hidden'));
        window.closeTrusteeConflictNetworkModal();
        assert('trusteeConflictNetworkModal closes properly', trusteesModal && trusteesModal.classList.contains('hidden'));

        // Test hudRouteBtn (Crawls)
        const routeBtn = document.getElementById('hudRouteBtn');
        assert('hudRouteBtn exists', !!routeBtn);
        routeBtn.click();
        const routeModal = document.getElementById('curatorialItineraryModal');
        assert('hudRouteBtn opens curatorialItineraryModal', routeModal && !routeModal.classList.contains('hidden'));
        window.closeCuratorialItineraryModal();
        assert('curatorialItineraryModal closes properly', routeModal && routeModal.classList.contains('hidden'));

        // Test hudRailToggle (Rail)
        const railBtn = document.getElementById('hudRailToggle');
        assert('hudRailToggle exists', !!railBtn);
        const prevText = railBtn.classList.contains('text-[#38bdf8]');
        railBtn.click();
        const nextText = railBtn.classList.contains('text-[#38bdf8]');
        assert('hudRailToggle toggles active visual classes', prevText !== nextText);

        // Test hudContributeBtn (Intel)
        const contributeBtn = document.getElementById('hudContributeBtn');
        assert('hudContributeBtn exists', !!contributeBtn);
        contributeBtn.click();
        const msgs = document.querySelectorAll('.curator-message-wrap');
        const lastMsg = msgs[msgs.length - 1];
        assert('hudContributeBtn appends whistleblower intake prompt in chat', lastMsg && lastMsg.innerHTML.includes('Confidential Field Intel'));

      } catch (err) {
        assert('Execution Exception', false, err.stack || err.toString());
      }

      const out = document.createElement('div');
      out.id = 'hud-verify-results';
      out.setAttribute('data-results', JSON.stringify(results));
      document.body.appendChild(out);
    });
    </script>
    """

    harness_html = html.replace("</body>", f"{test_script}</body>")
    temp_file = os.path.join(tempfile.gettempdir(), "test_hud_verify_harness.html")
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
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    dom = proc.stdout
    import re
    match = re.search(r'id="hud-verify-results"\s+data-results="([^"]+)"', dom)
    if not match:
        print("[FAIL] Test results element not found in DOM!")
        print("Stderr:", proc.stderr[:500])
        sys.exit(1)

    raw_results = match.group(1).replace("&quot;", '"')
    test_results = json.loads(raw_results)
    failed = [r for r in test_results if not r["pass"]]
    for r in test_results:
        status = "PASS" if r["pass"] else "FAIL"
        print(f"[{status}] {r['name']} {r['details']}")

    if failed:
        print(f"\n❌ {len(failed)} test(s) failed!")
        sys.exit(1)
    else:
        print(f"\n✅ All {len(test_results)} browser verification assertions passed successfully!")

if __name__ == "__main__":
    run_tests()
