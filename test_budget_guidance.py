import os
import subprocess
import json
import tempfile
import html as html_lib

def run_tests():
    print("--- RUNNING BUDGET & FINANCIAL DATA GUIDANCE TEST SUITE ---")
    
    index_path = "/Users/polinavasilyeva/.gemini/antigravity/scratch/sponsor-atlas/index.html"
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
        // 1. Check Governance Methodology Modal has the budget timing section
        const govModal = document.getElementById('governanceMethodologyModal');
        assert('Governance Modal exists in DOM', !!govModal);
        const modalText = govModal ? (govModal.innerText || govModal.innerHTML) : '';
        assert('Modal includes 2026 budgets not published notice', modalText.includes("I don't have access to 2026 budget data") && modalText.includes("typically in the spring or summer"));
        assert('Modal includes IRS Form 990 Schedule O & Charity Commission accounts', modalText.includes("IRS Form 990") && modalText.includes("Schedule O") && modalText.includes("Charity Commission"));
        assert('Modal includes what documents show (overhead red flags)', modalText.includes("40% fundraising overhead") || modalText.includes("trustee consulting fees"));

        // 2. Query Curator: 'Do you have 2026 budget data for museums?'
        const prevCount = document.querySelectorAll('.curator-message-wrap').length;
        window.handleCuratorQuery('Do you have 2026 budget data for museums?');
        for (let i = 0; i < 20; i++) {
          await new Promise(r => setTimeout(r, 100));
          const msgs = document.querySelectorAll('.curator-message-wrap');
          if (msgs.length > prevCount) break;
        }

        let msgs = document.querySelectorAll('.curator-message-wrap');
        let lastMsg = msgs[msgs.length - 1];
        let text = lastMsg ? (lastMsg.innerText || lastMsg.textContent) : '';

        assert('Curator explains 2026 budget access & fiscal year close timing', 
          text.includes("I don't have access to 2026 budget data for any museums") && 
          text.includes("typically in the spring or summer following the year in question"), text);

        assert('Curator details where to find real budget information (Form 990 Schedule O & Charity Commission)', 
          text.includes("Where to find real budget information") && 
          text.includes("IRS Form 990") && 
          text.includes("Schedule O") && 
          text.includes("Charity Commission register"), text);

        assert('Curator details what those documents actually show & red flags', 
          text.includes("What those documents actually show") && 
          text.includes("restricted vs unrestricted gifts") && 
          text.includes("40% on fundraising overhead") && 
          text.includes("trustee siphoning consulting fees to their own firm"), text);

        assert('Curator details what to look for (program expenses vs overhead)', 
          text.includes("What you should look for") && 
          text.includes("Program expenses") && 
          text.includes("administrative overhead") && 
          text.includes("donor-named wings rather than flexible operations"), text);

        assert('Curator prompts user with closing question: Which museum are you looking into?', 
          text.includes("Which museum are you looking into?"), text);

        // 3. Query Curator: 'where to find budget information'
        const prevCount2 = document.querySelectorAll('.curator-message-wrap').length;
        window.handleCuratorQuery('where to find budget information');
        for (let i = 0; i < 20; i++) {
          await new Promise(r => setTimeout(r, 100));
          msgs = document.querySelectorAll('.curator-message-wrap');
          if (msgs.length > prevCount2) break;
        }

        lastMsg = msgs[msgs.length - 1];
        text = lastMsg ? (lastMsg.innerText || lastMsg.textContent) : '';

        assert('General budget search also routes to budget guidance', 
          text.includes("Where to find real budget information") && 
          text.includes("IRS Form 990"), text);

      } catch (err) {
        assert('Execution Exception', false, err.stack || err.toString());
      }

      const out = document.createElement('div');
      out.id = 'budget-guidance-results';
      out.setAttribute('data-results', JSON.stringify(results));
      document.body.appendChild(out);
    });
    </script>
    """

    harness_html = html.replace("</body>", f"{test_script}</body>")
    temp_file = os.path.join(tempfile.gettempdir(), "test_budget_guidance_harness.html")
    with open(temp_file, "w", encoding="utf-8") as f:
        f.write(harness_html)

    chrome_bin = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    cmd = [
        chrome_bin,
        "--headless=new",
        "--dump-dom",
        "--window-size=1280,800",
        "--virtual-time-budget=5000",
        f"file://{temp_file}"
    ]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=60)
    stdout = res.stdout

    marker = 'id="budget-guidance-results" data-results="'
    if marker not in stdout:
        print("[FAIL] Test output marker not found in headless Chrome output!")
        exit(1)

    raw_json = stdout.split(marker)[1].split('"')[0]
    raw_json = html_lib.unescape(raw_json)
    results = json.loads(raw_json)

    fails = 0
    for r in results:
        status = "[PASS]" if r["pass"] else "[FAIL]"
        print(f"{status} {r['name']}")
        if not r["pass"]:
            print(f"       Details: {r.get('details', '')}")
            fails += 1

    if fails == 0:
        print("\nALL BUDGET GUIDANCE TESTS PASSED!")
    else:
        print(f"\n{fails} TEST(S) FAILED!")
        exit(1)

if __name__ == '__main__':
    run_tests()
