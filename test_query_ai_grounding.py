import os
import subprocess
import json
import tempfile
import html as html_lib

def run_tests():
    print("--- RUNNING SPECIFICITY & ANTI-HALLUCINATION TEST SUITE ---")
    
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
        // Test 1: Query 'check it for me' with NO active institution selected
        window.selectedInstitution = null;
        if (typeof window.curatorContext !== 'undefined') window.curatorContext.lastInst = null;
        
        window.handleCuratorQuery('check it for me');
        await new Promise(r => setTimeout(r, 600));

        let msgs = document.querySelectorAll('.curator-message-wrap');
        let lastMsg = msgs[msgs.length - 1];
        let text = lastMsg ? lastMsg.innerText : '';

        assert('No dataset review hallucination', !text.includes("sample atlas data you provided") && !text.includes("Generic highlight descriptions are killing"));
        assert('Prompts with concrete spaces to check', text.includes("Which cultural space") && text.includes("Chisenhale") && text.includes("Kunstmuseum Bern"));

        // Test 2: Query 'check it for me' WITH active selected institution (Kunstmuseum Bern)
        const bern = window.ALL_INSTITUTIONS.find(i => i.name.includes('Kunstmuseum Bern'));
        assert('Kunstmuseum Bern exists in catalog', !!bern);
        
        if (typeof window.selectInstitution === 'function') {
          window.selectInstitution(bern);
        }
        window.selectedInstitution = bern;
        if (typeof window.curatorContext !== 'undefined') {
          window.curatorContext.lastInst = bern;
          window.curatorContext.lastCity = bern.city;
        }

        const prevCount = document.querySelectorAll('.curator-message-wrap').length;
        window.handleCuratorQuery('check it for me');
        for (let i = 0; i < 20; i++) {
          await new Promise(r => setTimeout(r, 100));
          msgs = document.querySelectorAll('.curator-message-wrap');
          if (msgs.length > prevCount) break;
        }

        lastMsg = msgs[msgs.length - 1];
        text = lastMsg ? lastMsg.innerText : '';

        assert('Bern audit does not hallucinate dataset critique', !text.includes("sample atlas data you provided") && !text.includes("Generic highlight"));
        assert('Bern audit includes specific Adolf Wolfli or Gurlitt provenance highlight', text.includes("Wölfli") || text.includes("Wolfli") || text.includes("Gurlitt") || text.includes("Paul Klee"), text);
        assert('Bern audit includes specific governance details', text.includes("Flagged Corporate Conflict") || text.includes("Audited funding conflict") || text.includes("fossil fuel") || text.includes("trustee board"), text);
        assert('Bern audit includes specific admission model', text.includes("Ticketed") || text.includes("Concessions") || text.includes("Opening Schedule"), text);
        assert('Bern audit includes architecture details', text.includes("Architectural Footprint") || text.includes("12,000 sqm") || text.includes("sqm") || text.includes("Civic"), text);

        // Test 3: Specificity of highlights across catalog (Kunstmuseum Bern, De La Warr Pavilion, Kunsthalle Bremen)
        const delawarr = window.ALL_INSTITUTIONS.find(i => i.name.includes('De La Warr Pavilion'));
        const bremen = window.ALL_INSTITUTIONS.find(i => i.name.includes('Kunsthalle Bremen'));

        assert('De La Warr has specific Mendelsohn/Chermayeff modernist highlights', delawarr && (delawarr.highlight.includes('Mendelsohn') || delawarr.highlight.includes('Chermayeff') || delawarr.highlight.includes('modernist')));
        assert('Kunsthalle Bremen has specific Bürgerverein / Paula Modersohn-Becker highlights', bremen && (bremen.highlight.includes('Bürgerverein') || bremen.highlight.includes('Paula Modersohn-Becker') || bremen.highlight.includes('Cage')));

      } catch (err) {
        assert('Execution Exception', false, err.stack || err.toString());
      }

      const out = document.createElement('div');
      out.id = 'anti-hallucination-results';
      out.setAttribute('data-results', JSON.stringify(results));
      document.body.appendChild(out);
    });
    </script>
    """

    harness_html = html.replace("</body>", f"{test_script}</body>")
    temp_file = os.path.join(tempfile.gettempdir(), "test_anti_hallucination_harness.html")
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

    marker = 'id="anti-hallucination-results" data-results="'
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
        print("\nALL ANTI-HALLUCINATION & SPECIFICITY TESTS PASSED!")
    else:
        print(f"\n{fails} TEST(S) FAILED!")
        exit(1)

if __name__ == '__main__':
    run_tests()
