import os
import subprocess
import json
import tempfile
import html as html_lib
import sys

def run_tests():
    print("--- RUNNING IN-CHAT CONTRIBUTE INTEL & NO POPUP TEST SUITE ---")
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
        assert('Confidential Intake modal exists in DOM but stays hidden', !!modal && modal.classList.contains('hidden'));

        // 1. Verify Contribute button exists next to chat input in workBottomDock underneath
        const chatDock = document.getElementById('workBottomDock');
        assert('workBottomDock exists', !!chatDock);
        const chatContributeBtn = chatDock ? chatDock.querySelector('#chatContributeBtn') : null;
        assert('chatContributeBtn is located in workBottomDock next to chat input', !!chatContributeBtn);
        assert('chatContributeBtn has prominent pulse dot and label', chatContributeBtn && chatContributeBtn.innerHTML.includes('animate-pulse') && chatContributeBtn.textContent.includes('Contribute'));

        // 2. Click chatContributeBtn -> NO popup window, chat row above explains what to do
        const curatorMessages = document.getElementById('curatorMessages');
        const workInput = document.getElementById('workInput');

        chatContributeBtn.click();
        await new Promise(r => setTimeout(r, 100));

        assert('Clicking chatContributeBtn does NOT open pop up window', modal && modal.classList.contains('hidden'));
        assert('Chat row above explains what you need to do', curatorMessages && curatorMessages.innerHTML.includes('Confidential Field Intel') && curatorMessages.innerHTML.includes('How to submit right here'));
        assert('Chat input placeholder indicates confidential input active', workInput && workInput.placeholder.includes('🔒'));

        // 3. Verify Top Header Contribute button uses small chat window with NO popup window
        const topBtn = document.getElementById('topContributeBtn');
        assert('Top Contribute button exists (#topContributeBtn)', !!topBtn);
        topBtn.click();
        await new Promise(r => setTimeout(r, 100));
        assert('Clicking topContributeBtn does NOT open pop up window', modal && modal.classList.contains('hidden'));
        assert('Chat row above explains what to do after topBtn click', curatorMessages && curatorMessages.innerHTML.includes('Confidential Field Intel'));

        // 4. Verify Mobile Contribute button uses small chat window with NO popup window
        const mobileBtn = document.getElementById('mobileContributeBtn');
        assert('Mobile Contribute button exists (#mobileContributeBtn)', !!mobileBtn);
        mobileBtn.click();
        await new Promise(r => setTimeout(r, 100));
        assert('Clicking mobileContributeBtn does NOT open pop up window', modal && modal.classList.contains('hidden'));

        // 5. Verify Map Floating Badge uses small chat window with NO popup window
        const mapFloatBtn = document.getElementById('mapFloatingContributeBtn');
        assert('Map floating badge exists (#mapFloatingContributeBtn)', !!mapFloatBtn);
        mapFloatBtn.click();
        await new Promise(r => setTimeout(r, 100));
        assert('Clicking mapFloatingContributeBtn does NOT open pop up window', modal && modal.classList.contains('hidden'));

        // 6. Verify Map HUD Control uses small chat window with NO popup window
        const hudBtn = document.getElementById('hudContributeBtn');
        assert('Map HUD controls bar has Contribute button (#hudContributeBtn)', !!hudBtn);
        hudBtn.click();
        await new Promise(r => setTimeout(r, 100));
        assert('Clicking hudContributeBtn does NOT open pop up window', modal && modal.classList.contains('hidden'));

        // 7. Verify Globe Bar Filter Pill uses small chat window with NO popup window
        const globePill = document.getElementById('globeContributeIntelBtn');
        assert('Globe filter bar has Contribute Intel pill (#globeContributeIntelBtn)', !!globePill);
        globePill.click();
        await new Promise(r => setTimeout(r, 100));
        assert('Clicking globeContributeIntelBtn does NOT open pop up window', modal && modal.classList.contains('hidden'));

        // 8. Test in-chat submission of leak with cryptographic receipt
        await window.processInChatWhistleblowerSubmission('Confidential leak: undisclosed fossil fuel trustee ties at Modern Institute');
        await new Promise(r => setTimeout(r, 200));

        assert('In-chat submission generates Cryptographic Whistleblower Receipt card', curatorMessages && curatorMessages.innerHTML.includes('Cryptographic Whistleblower Receipt'));
        assert('In-chat receipt displays SHA-256 VERIFIED hash', curatorMessages && curatorMessages.innerHTML.includes('SHA-256 VERIFIED'));
        assert('In-chat receipt displays OpSec precautions', curatorMessages && curatorMessages.innerHTML.includes('OpSec &amp; Whistleblower Precautions') || curatorMessages.innerHTML.includes('OpSec & Whistleblower Precautions'));

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
        "--virtual-time-budget=4000",
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
        print("\n🎉 ALL IN-CHAT CONTRIBUTE CHECKS PASSED WITH NO POPUP WINDOW!")

if __name__ == '__main__':
    run_tests()
