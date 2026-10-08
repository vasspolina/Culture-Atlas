import os
import subprocess
import json
import tempfile
import html as html_lib

def run_tests():
    print("--- RUNNING BACKLOG RESOLUTION TEST SUITE ---")
    
    # 1. Dataset verification
    with open('institutions.json', 'r', encoding='utf-8') as f:
        institutions = json.load(f)
    
    assert len(institutions) >= 1000, f"Expected >= 1000 institutions, got {len(institutions)}"
    print(f"[PASS] Total institutions in dataset: {len(institutions)}")

    # Check 1: 0 template highlight descriptions
    template_highlights = [
        i for i in institutions 
        if "signature collection and rotating site-specific commissions dedicated to" in (i.get('highlights') or '').lower()
    ]
    assert len(template_highlights) == 0, f"Found {len(template_highlights)} template highlights remaining!"
    print(f"[PASS] Template highlights eliminated across all {len(institutions)} spaces (0 remaining)")

    # Check 2: Admission categories clarified
    vague_admissions = [
        i for i in institutions
        if i.get('admission') in ["Standard Ticketed with Civic Subsidies", "Free or Subsidized Admission", "Standard Admission"]
    ]
    assert len(vague_admissions) == 0, f"Found {len(vague_admissions)} vague admission classifications!"
    print(f"[PASS] Vague admission policies replaced with clear categories across all spaces (0 remaining)")

    # Check 3: Governance classifications and Tier A slop eradicated in data
    tier_a_labels = [
        i for i in institutions
        if "tier a" in (i.get('tier_label') or '').lower() or "tier b" in (i.get('tier_label') or '').lower()
    ]
    assert len(tier_a_labels) == 0, f"Found {len(tier_a_labels)} institutions with Tier A/B labels!"
    print(f"[PASS] 'Tier A' and 'Tier B' eliminated from dataset tier_label (0 remaining)")

    has_gov_class = [i for i in institutions if i.get('governance_classification') and i.get('governance_details')]
    assert len(has_gov_class) == len(institutions), f"Only {len(has_gov_class)}/{len(institutions)} have governance details!"
    print(f"[PASS] All {len(institutions)} institutions have governance_classification and governance_details")

    # Check 4: Zero Wikipedia links in sources
    wiki_links = [
        i for i in institutions
        if any('wikipedia.org' in s.lower() for s in i.get('sources', []))
    ]
    assert len(wiki_links) == 0, f"Found {len(wiki_links)} institutions with Wikipedia links in sources!"
    print(f"[PASS] Zero Wikipedia links in sources across all {len(institutions)} institutions")

    # 2. DOM & UI testing via headless Chrome
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
        // 1. Splitter styling
        const splitter = document.getElementById('globeSplitter');
        assert('Splitter element exists', !!splitter);
        const sClass = splitter ? splitter.className : '';
        assert('Splitter has neutral carbon dark tone', sClass.includes('bg-[#1c1c1f]'));
        assert('Splitter has subtle border', sClass.includes('border-[#27272a]'));
        assert('Splitter does not have harsh blue hover', !sClass.includes('hover:bg-[#3b82f6]'));

        // 2. Governance Legend buttons
        const topGovBtn = document.getElementById('topGovernanceBtn');
        assert('Top header Governance button exists', !!topGovBtn);

        const mobGovBtn = document.getElementById('mobileGovernanceBtn');
        assert('Mobile header Governance button exists', !!mobGovBtn);

        const workGovBtn = document.getElementById('workMenuGovernanceBtn');
        assert('Work menu Governance button exists', !!workGovBtn);

        const govPill = document.querySelector('.globe-filter-pill[data-type="governance"]');
        assert('Globe bar Governance Legend pill exists', !!govPill);

        // 3. Governance Methodology Modal
        const govModal = document.getElementById('governanceMethodologyModal');
        assert('Governance Methodology Modal exists in DOM', !!govModal);
        assert('Governance Modal is initially hidden', govModal.classList.contains('hidden'));

        // Test open function
        if (typeof window.openGovernanceMethodologyModal === 'function') {
          window.openGovernanceMethodologyModal();
          assert('openGovernanceMethodologyModal unhides modal', !govModal.classList.contains('hidden'));
        } else {
          assert('openGovernanceMethodologyModal function exists', false);
        }

        // Check content
        const mText = govModal.innerText || '';
        assert('Modal explains Verified Independent Space', mText.includes('Verified Independent Space'));
        assert('Modal explains Flagged Corporate Underwriting', mText.includes('Flagged Corporate Underwriting'));
        assert('Modal cites IRS Form 990 statutory disclosures', mText.includes('IRS Form 990'));
        assert('Modal cites UK Charity Commission register', mText.includes('Charity Commission'));
        assert('Modal cites European DRAC and ANBI registries', mText.includes('DRAC') && mText.includes('ANBI'));

        // Test close function
        if (typeof window.closeGovernanceMethodologyModal === 'function') {
          window.closeGovernanceMethodologyModal();
          assert('closeGovernanceMethodologyModal hides modal', govModal.classList.contains('hidden'));
        }

        // Test clicking top button opens modal
        if (topGovBtn) {
          topGovBtn.click();
          assert('Clicking topGovernanceBtn opens modal', !govModal.classList.contains('hidden'));
          const closeBtn = document.getElementById('closeGovernanceModalBtn');
          if (closeBtn) closeBtn.click();
          assert('Clicking closeGovernanceModalBtn closes modal', govModal.classList.contains('hidden'));
        }

        // 4. Curator query for governance methodology
        if (typeof window.handleCuratorQuery === 'function') {
          window.handleCuratorQuery('what is your governance methodology?');
          await new Promise(r => setTimeout(r, 500));
          const msgs = document.querySelectorAll('.curator-message-wrap');
          const lastMsg = msgs[msgs.length - 1];
          const chatText = lastMsg ? lastMsg.innerText : '';
          assert('Curator responds to governance methodology query', chatText.includes('Material Research') || chatText.includes('Forensic Methodology') || chatText.includes('Perjury') || chatText.includes('IRS Form 990'));
        }

      } catch (err) {
        assert('Execution Exception', false, err.stack || err.toString());
      }

      const out = document.createElement('div');
      out.id = 'backlog-test-results';
      out.setAttribute('data-results', JSON.stringify(results));
      document.body.appendChild(out);
    });
    </script>
    """

    harness_html = html.replace("</body>", f"{test_script}</body>")
    temp_file = os.path.join(tempfile.gettempdir(), "test_backlog_harness.html")
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
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=30)
    stdout = res.stdout

    marker = 'id="backlog-test-results" data-results="'
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
        print("\nALL BACKLOG RESOLUTION BROWSER TESTS PASSED!")
    else:
        print(f"\n{fails} TEST(S) FAILED!")
        exit(1)

if __name__ == '__main__':
    run_tests()
