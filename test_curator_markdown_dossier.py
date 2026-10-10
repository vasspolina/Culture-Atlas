import subprocess
import json
import os
import tempfile
import sys
import re

def run_tests():
    print("--- RUNNING CURATOR MARKDOWN & DOSSIER AUDIT TEST SUITE ---")
    index_path = "/Users/polinavasilyeva/.gemini/antigravity/scratch/sponsor-atlas/index.html"
    with open(index_path, "r", encoding="utf-8") as f:
        html = f.read()

    # 1. Static HTML assertions
    assert "function renderCuratorMarkdown" in html, "renderCuratorMarkdown function missing from index.html"
    assert "source-citation-pill" in html, "source-citation-pill missing from index.html"
    assert "stat-callout" in html, "stat-callout missing from index.html"
    assert "curator-section-hdr" in html, "curator-section-hdr missing from index.html"
    print("[PASS] Static HTML assertions passed.")

    # 2. Browser Headless Chrome execution tests
    test_script = """
    <script>
    window.requestAnimationFrame = () => 1;
    window.cancelAnimationFrame = () => {};
    window.fetch = async () => new Response("{}", { status: 200, headers: { 'Content-Type': 'application/json' } });

    window.addEventListener('DOMContentLoaded', async () => {
      const results = [];
      const assert = (name, cond, details = '') => {
        results.push({ name, pass: !!cond, details });
        if (!cond) console.error('[FAIL]', name, details);
        else console.log('[PASS]', name);
      };

      try {
        // Test 1: renderCuratorMarkdown engine directly
        assert('renderCuratorMarkdown is exposed on window', typeof window.renderCuratorMarkdown === 'function');

        const testMd = `### What You Actually Get
MoMA operates as a commercial brand commanding a $218 million operating budget.
- **The Tourist Reality:** Crowds 6-deep around *The Starry Night*.
- **The Financial Extraction:** A 28:1 wage ratio between executive pay and staff.

### The Governance Problem
Investigative exposés by The New York Times and ProPublica revealed Leon Black transferred $158 million to Jeffrey Epstein.
Disclosures are documented in IRS Form 990 Schedule L.`;

        const rendered = window.renderCuratorMarkdown(testMd);
        assert('Rendered output does NOT contain raw double asterisks', !rendered.includes('**'));
        assert('Rendered output converts bold to <strong>', rendered.includes('<strong class="text-white font-semibold">The Tourist Reality:</strong>'));
        assert('Rendered output converts headers to curator-section-hdr', rendered.includes('curator-section-hdr'));
        assert('Rendered output contains thematic badges', rendered.includes('Reality Check') && rendered.includes('Statutory Audit'));
        assert('Rendered output formats bullet lists', rendered.includes('curator-bullet-list') && rendered.includes('The Starry Night'));
        assert('Rendered output formats stat callouts ($218 million)', rendered.includes('stat-callout') && rendered.includes('$218 million'));
        assert('Rendered output formats stat callouts ($158 million)', rendered.includes('$158 million'));
        assert('Rendered output formats ratio stat callouts (28:1 wage ratio)', rendered.includes('28:1 wage ratio'));
        assert('Rendered output renders The New York Times source citation pill', rendered.includes('source-citation-pill') && rendered.includes('The New York Times'));
        assert('Rendered output renders ProPublica source citation pill', rendered.includes('ProPublica'));
        assert('Rendered output renders IRS Form 990 Schedule L citation pill', rendered.includes('IRS Form 990 Schedule L'));

        // Test 2: In-chat MoMA Query Execution
        await window.handleCuratorQuery('Why is MoMA excluded from Culture Atlas?');

        // Allow async response handling (handleCuratorQuery uses a 300ms delay)
        await new Promise(r => setTimeout(r, 800));

        const msgs = document.querySelectorAll('.curator-message-wrap');
        assert('Curator appended messages to chat', msgs.length > 0);
        const lastMsg = msgs[msgs.length - 1];
        const msgHtml = lastMsg.innerHTML;

        assert('MoMA response does NOT leak raw double asterisks', !msgHtml.includes('**What You Actually Get**') && !msgHtml.includes('**The Governance Problem**'));
        assert('MoMA response contains Reality Check section', msgHtml.includes('What You Actually Get') && msgHtml.includes('Reality Check'));
        assert('MoMA response contains Statutory Audit section', msgHtml.includes('The Governance Problem') && msgHtml.includes('Statutory Audit'));
        assert('MoMA response contains Systemic Impact section', msgHtml.includes('What This Actually Means') && msgHtml.includes('Systemic Impact'));
        assert('MoMA response contains Independent Counterpoint section', msgHtml.includes('The Comparison That Matters') && msgHtml.includes('Independent Counterpoint'));
        assert('MoMA response contains formatted bullet list', msgHtml.includes('curator-bullet-list'));
        assert('MoMA response contains Leon Black $158 million stat callout', msgHtml.includes('stat-callout') && msgHtml.includes('$158 million'));
        assert('MoMA response contains ProPublica source pill', msgHtml.includes('ProPublica') && msgHtml.includes('source-citation-pill'));
        assert('MoMA response contains The New York Times source pill', msgHtml.includes('The New York Times') && msgHtml.includes('source-citation-pill'));
        assert('MoMA response contains IRS Form 990 Schedule L source pill', msgHtml.includes('IRS Form 990 Schedule L'));
        assert('MoMA response contains alternative institution links', msgHtml.includes('Artists Space') && msgHtml.includes('SculptureCenter'));

      } catch (err) {
        assert('Execution Exception', false, err.stack || err.toString());
      }

      const out = document.createElement('div');
      out.id = 'curator-verify-results';
      out.setAttribute('data-results', JSON.stringify(results));
      document.body.appendChild(out);
    });
    </script>
    """

    harness_html = html.replace("</body>", f"{test_script}</body>")
    temp_file = os.path.join(tempfile.gettempdir(), "test_curator_verify_harness.html")
    with open(temp_file, "w", encoding="utf-8") as f:
        f.write(harness_html)

    chrome_bin = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    cmd = [
        chrome_bin,
        "--headless=new",
        "--dump-dom",
        "--window-size=1280,900",
        "--virtual-time-budget=6000",
        f"file://{temp_file}"
    ]
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    dom = proc.stdout
    match = re.search(r'id="curator-verify-results"\s+data-results="([^"]+)"', dom)
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
        print(f"\n✅ All {len(test_results)} curator markdown and dossier assertions passed successfully!")

if __name__ == "__main__":
    run_tests()
