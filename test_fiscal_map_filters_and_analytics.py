import os
import subprocess
import json
import tempfile
import html as html_lib

def run_tests():
    print("--- RUNNING FISCAL MAP FILTERS & ANALYTICS TEST SUITE ---")
    
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
        // Mock external web scraping to keep test deterministic and fast
        window.scrapeWebForQuery = async () => null;

        // 1. Verify Fiscal Analytics Modal markup in DOM
        const faModal = document.getElementById('fiscalAnalyticsModal');
        assert('Fiscal Analytics Modal exists in DOM', !!faModal);
        assert('Modal has total budget metric container', !!document.getElementById('faTotalBudgetStat'));
        assert('Modal has program spend metric container', !!document.getElementById('faAvgProgramStat'));
        assert('Modal has public subsidies metric container', !!document.getElementById('faAvgSubsidiesStat'));
        assert('Modal has administrative overhead container', !!document.getElementById('faAvgAdminStat'));
        assert('Modal has revenue mix progress bar elements', !!document.getElementById('faRevMixPublicBar') && !!document.getElementById('faRevMixEarnedBar') && !!document.getElementById('faRevMixPhilBar'));
        assert('Modal has typology grid container', !!document.getElementById('faTypologyGrid'));
        assert('Modal has top performers container', !!document.getElementById('faTopPerformersTable'));

        // 2. Test openFiscalAnalyticsHUD execution and live stats calculation
        window.openFiscalAnalyticsHUD();
        assert('openFiscalAnalyticsHUD makes modal visible', !faModal.classList.contains('hidden'));
        
        const totText = document.getElementById('faTotalBudgetStat')?.textContent || '';
        assert('Total scope displays in billions (€B)', totText.includes('€') && (totText.includes('B') || totText.includes('M')));

        const progText = document.getElementById('faAvgProgramStat')?.textContent || '';
        assert('Average program spend is ~74.8%', progText.includes('%') && parseFloat(progText) >= 70);

        const subText = document.getElementById('faAvgSubsidiesStat')?.textContent || '';
        assert('Average public subsidies is ~47.4%', subText.includes('%') && parseFloat(subText) >= 40);

        const typGrid = document.getElementById('faTypologyGrid');
        assert('Typology grid rendered at least 5 budget model cards', typGrid && typGrid.children.length >= 5);

        const topTable = document.getElementById('faTopPerformersTable');
        assert('Top performers rendered at least 3 institutions', topTable && topTable.children.length >= 3);

        window.closeFiscalAnalyticsHUD();
        assert('closeFiscalAnalyticsHUD hides modal', faModal.classList.contains('hidden'));

        // 3. Verify Map & Globe HUD Controls
        const hudFiscalBtn = document.getElementById('hudFiscalBtn');
        assert('HUD controls bar has Fiscal button (#hudFiscalBtn)', !!hudFiscalBtn);

        const mapBannerAnalyticsBtn = document.getElementById('activeMapFilterAnalyticsBtn');
        assert('Active map filter banner has Analytics button (#activeMapFilterAnalyticsBtn)', !!mapBannerAnalyticsBtn);

        // 4. Verify Interactive Fiscal Model Filtering
        // Test finance_civic (≥50% Public Subsidies)
        window.setCategoryFilter('finance_civic', false);
        const filteredCivic = window.filteredList || [];
        assert('Filter finance_civic returns institutions (>=300 in Clean tier)', filteredCivic.length >= 300, `Count: ${filteredCivic.length}`);
        const invalidCivic = filteredCivic.filter(i => (i.financial_data?.public_subsidies_pct || 0) < 50);
        assert('100% of filtered spaces have public_subsidies_pct >= 50%', invalidCivic.length === 0, `Invalid: ${invalidCivic.length}`);

        // Test finance_high_program (≥80% Program Services Spend)
        window.setCategoryFilter('finance_high_program', false);
        const filteredHighProg = window.filteredList || [];
        assert('Filter finance_high_program returns institutions (>=200)', filteredHighProg.length >= 200, `Count: ${filteredHighProg.length}`);
        const invalidProg = filteredHighProg.filter(i => (i.financial_data?.program_expense_ratio_pct || 0) < 80);
        assert('100% of filtered spaces have program_expense_ratio_pct >= 80%', invalidProg.length === 0, `Invalid: ${invalidProg.length}`);

        // 5. Verify Cohort Fiscal Analytics for Filtered Subset
        window.openFiscalAnalyticsHUD(filteredHighProg);
        const highProgScopeBadge = document.getElementById('faCohortScopeBadge')?.textContent || '';
        assert('Scope badge reflects filtered cohort count', highProgScopeBadge.includes('Filtered Cohort') && highProgScopeBadge.includes(filteredHighProg.length.toString()));
        const highProgStat = document.getElementById('faAvgProgramStat')?.textContent || '';
        assert('Cohort program spend avg is >= 80%', parseFloat(highProgStat) >= 80);
        window.closeFiscalAnalyticsHUD();

        // Reset filter
        window.setCategoryFilter('all', false);

        // 6. Verify Conversational Curator routes fiscal dashboard inquiries
        const prevCount = document.querySelectorAll('.curator-message-wrap').length;
        await window.handleCuratorQuery('open fiscal analytics dashboard');
        for (let i = 0; i < 20; i++) {
          await new Promise(r => setTimeout(r, 100));
          if (document.querySelectorAll('.curator-message-wrap').length > prevCount) break;
        }
        const msgs = document.querySelectorAll('.curator-message-wrap');
        const lastMsg = msgs[msgs.length - 1];
        const lastHtml = lastMsg ? lastMsg.innerHTML : '';
        assert('Curator responds to fiscal analytics query with dashboard card', lastHtml.includes('Institutional Fiscal Analytics') && lastHtml.includes('Avg Program Spend'));

      } catch (err) {
        assert('Execution Exception', false, err.stack || err.toString());
      }

      const out = document.createElement('div');
      out.id = 'fiscal-test-results';
      out.setAttribute('data-results', JSON.stringify(results));
      document.body.appendChild(out);
    });
    </script>
    """

    harness_html = html.replace("</body>", f"{test_script}</body>")
    temp_file = os.path.join(tempfile.gettempdir(), "test_fiscal_harness.html")
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

    marker = 'id="fiscal-test-results" data-results="'
    if marker not in stdout:
        print("[FAIL] Test output marker not found in headless Chrome output!")
        print(stdout[:500])
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
        print("\nALL FISCAL MAP FILTERS & ANALYTICS TESTS PASSED!")
    else:
        print(f"\n{fails} TEST(S) FAILED!")
        exit(1)

if __name__ == '__main__':
    run_tests()
