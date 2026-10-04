import json
import subprocess
import tempfile
import html as html_lib
import os

def test_pm():
    # 1. Check institutions.json
    insts = json.load(open('institutions.json'))
    pm = [i for i in insts if i.get('id') == 'printed-matter-new-york'][0]
    assert pm['tier'] == 'B', f"Expected Tier B, got {pm['tier']}"
    assert 'Philip Aarons' in pm['watch'], "Expected Philip Aarons in watch"
    assert 'Millennium Partners' in pm['watch'], "Expected Millennium Partners in watch"
    print("[PASS] institutions.json: Printed Matter reclassified to Tier B with full ethical audit")

    # 2. Check compiled index.html via Headless Chrome
    index_path = os.path.abspath("index.html")
    with open(index_path, "r", encoding="utf-8") as f:
        html = f.read()

    test_script = """
    <script>
    window.addEventListener('load', async () => {
      const results = [];
      function assert(name, condition, extra = '') {
        results.push({ name, pass: !!condition, extra });
      }

      try {
        const inA = ALL_INSTITUTIONS.find(i => i.name.includes('Printed Matter'));
        assert('Printed Matter is NOT in Tier A (ALL_INSTITUTIONS)', !inA);

        const inEx = EXCLUDED_INSTITUTIONS.find(i => i.name.includes('Printed Matter'));
        assert('Printed Matter IS in EXCLUDED_INSTITUTIONS', !!inEx);
        assert('Tier is B', inEx && inEx.tier === 'B');
        assert('Watch mentions Philip Aarons', inEx && inEx.watch.includes('Philip Aarons'));

        // Test Curator query
        handleCuratorQuery('What about Printed Matter?');
        await new Promise(r => setTimeout(r, 600));
        const msgs = document.getElementById('curatorMessages')?.textContent || '';
        assert('Curator response mentions EXCLUSION AUDIT', msgs.includes('EXCLUSION AUDIT') || msgs.includes('Audit Conflict'));
        assert('Curator response mentions Philip Aarons', msgs.includes('Philip Aarons'));
        assert('Curator response mentions Millennium Partners', msgs.includes('Millennium Partners'));

      } catch (err) {
        results.push({ name: 'Exception caught', pass: false, extra: err.toString() });
      }

      const div = document.createElement('div');
      div.id = 'test-results-output';
      div.setAttribute('data-results', JSON.stringify(results));
      document.body.appendChild(div);
    });
    </script>
    """

    harness_html = html.replace("</body>", f"{test_script}</body>")
    temp_file = os.path.join(tempfile.gettempdir(), "test_pm_harness.html")
    with open(temp_file, "w", encoding="utf-8") as f:
        f.write(harness_html)

    chrome_bin = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    cmd = [
        chrome_bin,
        "--headless=new",
        "--dump-dom",
        "--window-size=1280,800",
        "--virtual-time-budget=4000",
        f"file://{temp_file}"
    ]
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=20)
    marker = 'id="test-results-output" data-results="'
    assert marker in proc.stdout, "Marker not in stdout"

    results = json.loads(html_lib.unescape(proc.stdout.split(marker)[1].split('"')[0]))
    for r in results:
        status = "PASS" if r['pass'] else "FAIL"
        extra = f" ({r['extra']})" if r.get('extra') else ""
        print(f"[{status}] {r['name']}{extra}")
        assert r['pass']

    print("\nALL PRINTED MATTER RECLASSIFICATION TESTS PASSED!")

if __name__ == '__main__':
    test_pm()
