import os
import subprocess
import json
import tempfile

def test_floating_card_budget_money():
    print("--- RUNNING FLOATING CARD BUDGET & MONEY TEST SUITE ---")
    index_path = "/Users/polinavasilyeva/.gemini/antigravity/scratch/sponsor-atlas/index.html"
    assert os.path.exists(index_path), "index.html must exist"

    with open(index_path, "r", encoding="utf-8") as f:
        html = f.read()

    test_script = """
    <script>
    window.addEventListener('load', async () => {
      const results = [];
      function assert(name, cond, extra = '') {
        results.push({ name, pass: !!cond, extra });
      }

      try {
        const insts = window.ALL_INSTITUTIONS || [];
        assert('ALL_INSTITUTIONS has data', insts.length >= 1000, `Found: ${insts.length}`);

        // 1. Test Slought (from user screenshot)
        const slought = insts.find(i => i.name.toLowerCase() === 'slought');
        assert('Slought exists in registry', !!slought);

        selectInstitution(slought);
        await new Promise(r => setTimeout(r, 200));

        const bSec = document.getElementById('floatingCardBudgetSection');
        assert('floatingCardBudgetSection is visible for Slought', bSec && !bSec.classList.contains('hidden'));

        const bAmt = document.getElementById('floatingCardBudgetAmount');
        assert('Budget amount displays for Slought', bAmt && bAmt.textContent.includes('$1.5M'), bAmt ? bAmt.textContent : 'none');

        const bTier = document.getElementById('floatingCardBudgetTier');
        assert('Budget tier displays Academic Research Endowment', bTier && bTier.textContent.includes('Academic Research Endowment'), bTier ? bTier.textContent : 'none');

        const fPub = document.getElementById('floatingCardPublicSubsidies');
        assert('Public subsidies displays 65%', fPub && fPub.textContent.includes('65%'), fPub ? fPub.textContent : 'none');

        const fPhil = document.getElementById('floatingCardPhilanthropy');
        assert('Philanthropy displays 20%', fPhil && fPhil.textContent.includes('20%'), fPhil ? fPhil.textContent : 'none');

        const fEarn = document.getElementById('floatingCardEarnedRevenue');
        assert('Earned revenue displays 15%', fEarn && fEarn.textContent.includes('15%'), fEarn ? fEarn.textContent : 'none');

        const fProg = document.getElementById('floatingCardProgramRatio');
        assert('Program ratio displays 82%', fProg && fProg.textContent.includes('82%'), fProg ? fProg.textContent : 'none');

        const fText = document.getElementById('floatingCardFundingText');
        assert('Funding source text displays for Slought', fText && fText.textContent.includes('University of Pennsylvania'), fText ? fText.textContent : 'none');

        const hours = document.getElementById('floatingCardHours');
        assert('Hours & Admission displays', hours && hours.textContent.includes('12:00-18:00') && hours.textContent.includes('Free'), hours ? hours.textContent : 'none');

        // 2. Test Stedelijk Museum Amsterdam
        const stedelijk = insts.find(i => i.name.includes('Stedelijk Museum Amsterdam'));
        assert('Stedelijk exists in registry', !!stedelijk);

        selectInstitution(stedelijk);
        await new Promise(r => setTimeout(r, 200));

        assert('Stedelijk budget displays €37.5M', bAmt && bAmt.textContent.includes('37.5M'), bAmt ? bAmt.textContent : 'none');
        assert('Stedelijk public subsidies displays 62%', fPub && fPub.textContent.includes('62%'), fPub ? fPub.textContent : 'none');
        assert('Stedelijk program ratio displays healthy pct', fProg && (fProg.textContent.includes('78%') || fProg.textContent.includes('76%')), fProg ? fProg.textContent : 'none');

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
    temp_file = os.path.join(tempfile.gettempdir(), "test_floating_card_budget_money_harness.html")
    with open(temp_file, "w", encoding="utf-8") as f:
        f.write(harness_html)

    chrome_bin = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    cmd = [
        chrome_bin,
        "--headless=new",
        "--dump-dom",
        "--virtual-time-budget=6000",
        f"file://{temp_file}"
    ]
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    import html as html_lib
    import sys
    marker = 'id="test-results-output" data-results="'
    if marker not in proc.stdout:
        print("ERROR: Test marker not found in output. Stderr:")
        print(proc.stderr[:1000])
        sys.exit(1)

    results = json.loads(html_lib.unescape(proc.stdout.split(marker)[1].split('"')[0]))
    all_passed = True
    for r in results:
        status = "[PASS]" if r["pass"] else "[FAIL]"
        print(f"{status} {r['name']} ({r.get('extra', '')})")
        if not r["pass"]:
            all_passed = False

    assert all_passed, "Some tests failed!"
    print(f"\n🎉 ALL FLOATING CARD BUDGET & MONEY TESTS PASSED ({len(results)}/{len(results)})!")

if __name__ == "__main__":
    test_floating_card_budget_money()
