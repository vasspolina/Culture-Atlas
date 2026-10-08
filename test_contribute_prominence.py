import os
import subprocess
import json
import tempfile
import html as html_lib
import sys

def run_tests():
    print("--- RUNNING CONTRIBUTE INTEL PROMINENCE & CHAT REMOVAL TEST SUITE ---")
    index_path = "/Users/polinavasilyeva/.gemini/antigravity/scratch/sponsor-atlas/index.html"
    assert os.path.exists(index_path), "index.html must exist"

    with open(index_path, "r", encoding="utf-8") as f:
        html = f.read()

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
        const modal = document.getElementById('confidentialIntakeChatModal');
        assert('Confidential Intake modal exists in DOM', !!modal);

        // 1. Verify Contribute Intel is completely REMOVED from chat window dock
        const chatDock = document.getElementById('workBottomDock');
        const chatBtnInDock = chatDock ? chatDock.querySelector('#chatContributeBtn') : null;
        assert('chatContributeBtn is NOT in workBottomDock', chatBtnInDock === null);
        const anyChatContributeBtn = document.getElementById('chatContributeBtn');
        assert('No chatContributeBtn exists anywhere in chat window', anyChatContributeBtn === null);

        // 2. Verify Top Header Desktop Contribute button
        const topBtn = document.getElementById('topContributeBtn');
        assert('Top Contribute button exists (#topContributeBtn)', !!topBtn);
        assert('Top Contribute button has prominent pulse indicator', topBtn && topBtn.innerHTML.includes('animate-pulse'));
        
        topBtn.click();
        assert('Clicking topContributeBtn opens confidential modal', modal && !modal.classList.contains('hidden'));
        document.getElementById('closeConfidentialChatBtn').click();
        assert('Clicking close button closes confidential modal', modal && modal.classList.contains('hidden'));

        // 3. Verify Top Mobile Contribute button
        const mobileBtn = document.getElementById('mobileContributeBtn');
        assert('Mobile Contribute button exists (#mobileContributeBtn)', !!mobileBtn);
        mobileBtn.click();
        assert('Clicking mobileContributeBtn opens confidential modal', modal && !modal.classList.contains('hidden'));
        document.getElementById('closeConfidentialChatBtn').click();
        assert('Modal closed after mobile test', modal && modal.classList.contains('hidden'));

        // 4. Verify Map Floating Badge (#mapFloatingContributeBtn)
        const mapFloatBtn = document.getElementById('mapFloatingContributeBtn');
        assert('Map floating badge exists (#mapFloatingContributeBtn)', !!mapFloatBtn);
        assert('Map floating badge contains prominent text', mapFloatBtn && mapFloatBtn.textContent.includes('Contribute Intel'));
        mapFloatBtn.click();
        assert('Clicking mapFloatingContributeBtn opens confidential modal', modal && !modal.classList.contains('hidden'));
        document.getElementById('closeConfidentialChatBtn').click();
        assert('Modal closed after map floating badge test', modal && modal.classList.contains('hidden'));

        // 5. Verify Bottom Map HUD Control (#hudContributeBtn)
        const hudBtn = document.getElementById('hudContributeBtn');
        assert('Map HUD controls bar has Contribute button (#hudContributeBtn)', !!hudBtn);
        hudBtn.click();
        assert('Clicking hudContributeBtn opens confidential modal', modal && !modal.classList.contains('hidden'));
        document.getElementById('closeConfidentialChatBtn').click();
        assert('Modal closed after HUD test', modal && modal.classList.contains('hidden'));

        // 6. Verify Globe Bar Filter Pill (#globeContributeIntelBtn)
        const globePill = document.getElementById('globeContributeIntelBtn');
        assert('Globe filter bar has Contribute Intel pill (#globeContributeIntelBtn)', !!globePill);
        globePill.click();
        assert('Clicking globeContributeIntelBtn opens confidential modal', modal && !modal.classList.contains('hidden'));
        document.getElementById('closeConfidentialChatBtn').click();
        assert('Modal closed after globe pill test', modal && modal.classList.contains('hidden'));

      } catch (err) {
        results.push({ name: 'Exception caught', pass: false, details: err.toString() });
      }

      const div = document.createElement('div');
      div.id = 'contribute-test-results';
      div.setAttribute('data-results', JSON.stringify(results));
      document.body.appendChild(div);
    });
    </script>
    """

    harness_html = html.replace("</body>", f"{test_script}</body>")
    temp_file = os.path.join(tempfile.gettempdir(), "test_contribute_prominence.html")
    with open(temp_file, "w", encoding="utf-8") as f:
        f.write(harness_html)

    chrome_cmd = [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        "--dump-dom",
        "--virtual-time-budget=3000",
        f"file://{temp_file}"
    ]

    proc = subprocess.run(chrome_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=15)
    stdout = proc.stdout

    marker = 'id="contribute-test-results" data-results="'
    if marker not in stdout:
        print("[FAIL] Test output marker not found in headless Chrome output!")
        sys.exit(1)

    raw_json = stdout.split(marker)[1].split('"')[0]
    raw_json = html_lib.unescape(raw_json)
    results = json.loads(raw_json)

    total = len(results)
    passed = sum(1 for r in results if r['pass'])
    failed = sum(1 for r in results if not r['pass'])

    print(f"\nRESULTS: {passed}/{total} checks PASSED.")
    for r in results:
        status = "PASS" if r['pass'] else "FAIL"
        print(f"[{status}] {r['name']}")
        if not r['pass']:
            print(f"       Details: {r.get('details', '')}")

    if failed > 0:
        sys.exit(1)
    else:
        print("\n🎉 ALL CONTRIBUTE PROMINENCE CHECKS PASSED PERFECTLY!")

if __name__ == '__main__':
    run_tests()
