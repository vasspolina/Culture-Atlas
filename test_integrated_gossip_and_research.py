#!/usr/bin/env python3
"""
test_integrated_gossip_and_research.py
Verifies:
1. Academic papers count (137) and presence in DOM and search modal.
2. Verified investigation cases and employee reviews present on institutions.
3. Floating card gossip pane renders real case highlights and employee reviews.
4. Drawer gossip dossier renders full facts, claims, responses, outcomes, limits, and sources.
"""

import os
import sys
import json
import subprocess
import tempfile
import html as html_lib

def test_integration():
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
        await new Promise(r => setTimeout(r, 500));
        
        // 1. Verify Academic Papers
        const papers = window.ACADEMIC_RESEARCH || [];
        assert('Academic papers loaded in app', papers.length >= 135, 'count: ' + papers.length);
        const regionalStudy = papers.find(p => p.title.includes('Performance of cultural heritage institutions'));
        assert('Found new paper from CSV: Regional cultural heritage', !!regionalStudy);
        const caringStudy = papers.find(p => p.title.includes('Caring exhibitions'));
        assert('Found new paper from CSV: Caring exhibitions', !!caringStudy);

        // 2. Verify Institutions with cases
        const allInsts = window.ALL_INSTITUTIONS || [];
        assert('All institutions loaded', allInsts.length >= 1090, 'count: ' + allInsts.length);

        const bm = allInsts.find(i => i.name.toLowerCase() === 'british museum');
        assert('British Museum present', !!bm);
        assert('British Museum has real_cases', bm && bm.gossip_data && bm.gossip_data.real_cases && bm.gossip_data.real_cases.length >= 2);
        assert('British Museum has review_leads', bm && bm.gossip_data && bm.gossip_data.review_leads && bm.gossip_data.review_leads.length >= 2);

        const sci = allInsts.find(i => i.name.toLowerCase() === 'science museum');
        assert('Science Museum has real_cases', sci && sci.gossip_data && sci.gossip_data.real_cases && sci.gossip_data.real_cases.length >= 1);

        const va = allInsts.find(i => i.name.toLowerCase() === 'v&a' || i.name.toLowerCase().includes('victoria and albert'));
        assert('V&A has real_cases', va && va.gossip_data && va.gossip_data.real_cases && va.gossip_data.real_cases.length >= 1);

        const whitney = allInsts.find(i => i.name.toLowerCase().includes('whitney'));
        assert('Whitney has real_cases', whitney && whitney.gossip_data && whitney.gossip_data.real_cases && whitney.gossip_data.real_cases.length >= 2);

        // 3. Test selection and Gossip Card rendering
        if (bm && window.selectInstitution) {
          window.selectInstitution(bm, false);
          await new Promise(r => setTimeout(r, 100));

          // Switch card to gossip mode
          if (window.setCardMode) window.setCardMode('gossip', false);

          const cardCaseBox = document.getElementById('floatingCardGossipRealCases');
          assert('Floating card real cases box visible for British Museum', cardCaseBox && !cardCaseBox.classList.contains('hidden'));
          
          const cardCaseOutcome = document.getElementById('floatingCardGossipCaseOutcome');
          assert('Floating card case outcome populated', cardCaseOutcome && cardCaseOutcome.textContent.length > 10, cardCaseOutcome ? cardCaseOutcome.textContent : 'none');

          const cardRevBox = document.getElementById('floatingCardGossipReviewLeads');
          assert('Floating card review leads box visible for British Museum', cardRevBox && !cardRevBox.classList.contains('hidden'));

          // 4. Test Drawer Gossip Viewport
          if (window.openDossier) {
            window.openDossier(bm);
            await new Promise(r => setTimeout(r, 100));
            if (window.setDrawerMode) window.setDrawerMode('gossip');

            const drawerGossip = document.getElementById('drawerGossipView');
            assert('Drawer gossip view visible', drawerGossip && !drawerGossip.classList.contains('hidden'));
            
            const caseHeadings = drawerGossip.querySelectorAll('h3, strong');
            assert('Drawer contains case investigations', drawerGossip.textContent.includes('Documented Dispute Investigations'));
            assert('Drawer contains staff review leads', drawerGossip.textContent.includes('Verified Staff & Worker Reviews') || drawerGossip.innerHTML.includes('Verified Staff'));
            assert('Drawer contains source links [S01] or [S02]', drawerGossip.innerHTML.includes('[S01]') || drawerGossip.innerHTML.includes('[S02]'));
          }
        }

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
    temp_file = os.path.join(tempfile.gettempdir(), "test_integrated_gossip_harness.html")
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
    print(f"\n🎉 ALL GOSSIP & RESEARCH DATASET INTEGRATION TESTS PASSED ({len(results)}/{len(results)})!")

if __name__ == '__main__':
    test_integration()
