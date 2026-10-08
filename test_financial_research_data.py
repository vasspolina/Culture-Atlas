import os
import subprocess
import json
import tempfile
import html as html_lib

def run_tests():
    print("--- RUNNING FINANCIAL RESEARCH DATA TEST SUITE ---")
    
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
        const insts = window.ALL_INSTITUTIONS || [];
        assert('Catalog has at least 1000 institutions', insts.length >= 1000, `Found: ${insts.length}`);

        // 1. Verify structured financial_data on all institutions
        const missingFin = insts.filter(i => !i.financial_data || !i.financial_data.operating_budget_display || typeof i.financial_data.program_expense_ratio_pct !== 'number');
        assert('100% of institutions have structured financial_data', missingFin.length === 0, `Missing in ${missingFin.length} items`);

        const stedelijk = insts.find(i => i.name.includes('Stedelijk Museum Amsterdam'));
        assert('Stedelijk has specific financial profile', stedelijk && !!stedelijk.financial_data, stedelijk ? JSON.stringify(stedelijk.financial_data) : 'Missing');
        if (stedelijk && stedelijk.financial_data) {
          assert('Stedelijk operating budget display includes €37.5M', stedelijk.financial_data.operating_budget_display.includes('37.5M'), stedelijk.financial_data.operating_budget_display);
          assert('Stedelijk public subsidies pct is 62%', stedelijk.financial_data.public_subsidies_pct === 62, `${stedelijk.financial_data.public_subsidies_pct}%`);
          assert('Stedelijk program expense ratio is healthy (>70%)', stedelijk.financial_data.program_expense_ratio_pct >= 70, `${stedelijk.financial_data.program_expense_ratio_pct}%`);
        }

        // 2. Verify Academic Research Library finance papers
        const papers = window.ACADEMIC_RESEARCH || [];
        assert('Academic Research corpus has at least 110 studies', papers.length >= 110, `Found: ${papers.length}`);

        const finPapers = papers.filter(p => {
          const str = ((p.title || '') + ' ' + (p.takeaway || '') + ' ' + (p.abstract || '')).toLowerCase();
          return str.includes('financ') || str.includes('budget') || str.includes('endow') || str.includes('revenue') || str.includes('overhead') || str.includes('expense') || str.includes('subsid');
        });
        assert('Academic Research corpus has substantial finance studies (>= 40)', finPapers.length >= 40, `Found: ${finPapers.length}`);

        // Test filtering by topic 'finance' in DOM
        if (typeof window.renderAcademicStudies === 'function') {
          window.renderAcademicStudies('finance', '');
          const pList = document.getElementById('arPapersList');
          assert('Rendering academic studies with finance topic populates papers list', pList && pList.children.length > 0, `Children: ${pList ? pList.children.length : 0}`);
          assert('List contains Calabrese Form 990 or Oster endowment paper', pList && (pList.innerHTML.includes('Calabrese') || pList.innerHTML.includes('Endowment') || pList.innerHTML.includes('Overhead')));
        }

        // 3. Verify openDossier renders Financial & Operating Research Profile
        if (typeof window.openDossier === 'function' && stedelijk) {
          window.openDossier(stedelijk);
          const detailBody = document.getElementById('detailBody');
          assert('Detail body contains Financial & Operating Research Profile card', detailBody && detailBody.innerHTML.includes('Financial &amp; Operating Research Profile') || detailBody.innerHTML.includes('Financial & Operating Research Profile'));
          assert('Detail body displays Operating Budget Scale banner', detailBody && (detailBody.innerHTML.includes('Operating Budget Scale') && detailBody.innerHTML.includes('37.5M')));
          assert('Detail body displays Revenue Mix Architecture', detailBody && detailBody.innerHTML.includes('Revenue Mix Architecture'));
          assert('Detail body displays Program Spend Ratio', detailBody && detailBody.innerHTML.includes('PROGRAM SPEND RATIO'));
        }

        // Mock external web scraping and live AI calls to test offline financial knowledge engine deterministically
        window.scrapeWebForQuery = async () => null;
        window.queryAI = async () => null;

        // 4. Verify Curator academic finance research query
        let prevCount = document.querySelectorAll('.curator-message-wrap').length;
        await window.handleCuratorQuery('improve research by adding finance data');
        for (let i = 0; i < 20; i++) {
          await new Promise(r => setTimeout(r, 100));
          if (document.querySelectorAll('.curator-message-wrap').length > prevCount) break;
        }
        let msgs = document.querySelectorAll('.curator-message-wrap');
        let lastMsg = msgs[msgs.length - 1];
        let lastMsgHtml = lastMsg ? lastMsg.innerHTML : '';
        assert('Curator responds to academic finance query with research synthesis', lastMsgHtml.includes('Academic Research: Museum Finance') || lastMsgHtml.includes('Form 990 Program Ratios') || lastMsgHtml.includes('Expansion Debt Trap'));

        // 5. Verify Curator specific institution finance diagnostic query
        prevCount = document.querySelectorAll('.curator-message-wrap').length;
        await window.handleCuratorQuery('Stedelijk Museum Amsterdam finances');
        for (let i = 0; i < 20; i++) {
          await new Promise(r => setTimeout(r, 100));
          if (document.querySelectorAll('.curator-message-wrap').length > prevCount) break;
        }
        msgs = document.querySelectorAll('.curator-message-wrap');
        lastMsg = msgs[msgs.length - 1];
        let lastMsg2Html = lastMsg ? lastMsg.innerHTML : '';
        assert('Curator responds to specific museum finance query with diagnostic card', lastMsg2Html.includes('Stedelijk Museum Amsterdam') && (lastMsg2Html.includes('37.5M') || lastMsg2Html.includes('Financial Diagnostic')));

        // 6. Verify Curator general budget query still retains 2026 notice and Form 990 guidance
        prevCount = document.querySelectorAll('.curator-message-wrap').length;
        await window.handleCuratorQuery('where to find museum budgets');
        for (let i = 0; i < 20; i++) {
          await new Promise(r => setTimeout(r, 100));
          if (document.querySelectorAll('.curator-message-wrap').length > prevCount) break;
        }
        msgs = document.querySelectorAll('.curator-message-wrap');
        lastMsg = msgs[msgs.length - 1];
        let lastMsg3Html = lastMsg ? lastMsg.innerHTML : '';
        assert('Curator retains 2026 budget timing notice in general inquiry', lastMsg3Html.includes('2026 budget data') && lastMsg3Html.includes('Schedule O'));

      } catch (err) {
        assert('Execution Exception', false, err.stack || err.toString());
      }

      const out = document.createElement('div');
      out.id = 'fin-test-results';
      out.setAttribute('data-results', JSON.stringify(results));
      document.body.appendChild(out);
    });
    </script>
    """

    harness_html = html.replace("</body>", f"{test_script}</body>")
    temp_file = os.path.join(tempfile.gettempdir(), "test_fin_harness.html")
    with open(temp_file, "w", encoding="utf-8") as f:
        f.write(harness_html)

    chrome_bin = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    cmd = [
        chrome_bin,
        "--headless",
        "--disable-gpu",
        "--dump-dom",
        "--virtual-time-budget=12000",
        f"file://{temp_file}"
    ]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=60)
    stdout = res.stdout

    marker = 'id="fin-test-results" data-results="'
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
        print("\nALL FINANCIAL RESEARCH DATA TESTS PASSED!")
    else:
        print(f"\n{fails} TEST(S) FAILED!")
        exit(1)

if __name__ == '__main__':
    run_tests()
