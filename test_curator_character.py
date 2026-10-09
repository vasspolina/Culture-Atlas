import os
import re
import subprocess
import json
import tempfile
import html as html_lib

def test_static_files():
    targets = [
        "index.html",
        "app/index.html",
        "app/standalone.html",
        "/Users/polinavasilyeva/.gemini/antigravity/brain/b997e616-4551-453e-83cc-4ba184f90abf/culture_atlas_app.html"
    ]
    for p in targets:
        assert os.path.exists(p), f"Target file must exist: {p}"
        content = open(p, "r", encoding="utf-8").read()
        
        # Verify complete eradication of slop / Yandex Alisa prompt leakage
        assert "Yandex Alisa" not in content, f"Found leaked 'Yandex Alisa' in {p}"
        assert "Alisa-style" not in content, f"Found leaked 'Alisa-style' in {p}"
        assert "Russian Yandex" not in content, f"Found leaked 'Russian Yandex' in {p}"
        assert "transatlantic art slang" not in content, f"Found leaked 'transatlantic art slang' in {p}"
        
        # Verify professional, researcher-grade persona and instructions
        assert "You are the Culture Atlas Curator. You are an independent, sharp, intellectually rigorous art researcher and guide." in content, f"Missing curator persona in {p}"
        assert "Auditing Form 990 & Trustee Interlocks" in content, f"Missing auditing thinking step in {p}"
        assert "Scanning Cultural Intelligence Dossiers" in content, f"Missing scanning dossier thinking step in {p}"
        assert "Analyzing inquiry against verified institutional archives" in content, f"Missing analytical default thought in {p}"
        
        # Check offline responses
        assert "Well, hello there! Welcome to the unvarnished side of the gallery." in content, f"Missing greeting in {p}"
        assert "Curator Critical Sparring Mode Active" in content, f"Missing Sparring mode in {p}"
        assert "Oh, you want to spar? Challenge accepted." in content, f"Missing sparring challenge in {p}"
        assert "Which cultural space are we interrogating today?" in content, f"Missing unselected check line in {p}"

    print("✅ All static files verified clean of prompt slop and loaded with researcher-grade curator persona!")

def test_headless_character_execution():
    app_path = os.path.abspath("index.html")
    with open(app_path, "r", encoding="utf-8") as f:
        html = f.read()

    test_script = """
    <script>
    window.addEventListener('DOMContentLoaded', () => {
      const results = [];
      function assert(name, condition, extra = '') {
        results.push({ name, pass: !!condition, extra: String(extra) });
      }

      try {
        // 1. Check thinking plan thoughts have researcher-grade analytical descriptions (no meta-slop)
        const defaultPlan = generateThinkingPlan("general inquiry");
        assert("Default thinking plan is analytical and slop-free", 
          defaultPlan.thought.includes('Analyzing inquiry against verified institutional archives') &&
          !defaultPlan.thought.includes('Alisa') &&
          !defaultPlan.thought.includes('slang'), defaultPlan.thought);

        const instPlan = generateThinkingPlan("Chisenhale Gallery");
        assert("Institution thinking plan audits filings", 
          instPlan.thought.includes('Auditing governance filings') && instPlan.thought.includes('Chisenhale Gallery'), instPlan.thought);

        const cityPlan = generateThinkingPlan("independent spaces in Berlin");
        assert("City thinking plan reviews registries", 
          cityPlan.thought.includes('Reviewing verified independent art spaces') && instPlan.thought.includes('Chisenhale Gallery'), cityPlan.thought);

        const crawlPlan = generateThinkingPlan("plan an art crawl");
        assert("Crawl thinking plan maps pedestrian corridors", 
          crawlPlan.thought.includes('Mapping pedestrian corridors'), crawlPlan.thought);

        const budgetPlan = generateThinkingPlan("museum budget 2026");
        assert("Budget thinking plan analyzes Form 990 disclosures", 
          budgetPlan.thought.includes('Analyzing Form 990 statutory disclosures'), budgetPlan.thought);

        const trusteePlan = generateThinkingPlan("trustee conflicts");
        assert("Trustee thinking plan examines board interlocks", 
          trusteePlan.thought.includes('Examining board interlocks'), trusteePlan.thought);

        // 2. Check queryAI criticalSystemPrompt contains clean independent curator persona
        const queryAiStr = typeof queryAI === 'function' ? queryAI.toString() : '';
        assert("queryAI does NOT contain Yandex Alisa", !queryAiStr.includes('Yandex Alisa'));
        assert("queryAI does NOT contain transatlantic art slang", !queryAiStr.includes('transatlantic art slang'));
        assert("queryAI contains independent researcher persona", queryAiStr.includes('independent, sharp, intellectually rigorous art researcher'));

        // 3. Check handleCuratorQuery contains clean curator greetings
        const handleStr = typeof handleCuratorQuery === 'function' ? handleCuratorQuery.toString() : '';
        assert("handleCuratorQuery does NOT contain Yandex Alisa", !handleStr.includes('Yandex Alisa'));
        assert("handleCuratorQuery contains greeting", handleStr.includes('Well, hello there! Welcome to the unvarnished side of the gallery'));
        assert("handleCuratorQuery sparring has challenge", handleStr.includes('Oh, you want to spar? Challenge accepted'));

        // 4. Test rendering of clean curator response in DOM
        appendCuratorMessage("<p>Hello! I am your Culture Atlas Curator. I navigate 441 verified independent spaces across 50 global cities.</p>");
        const msgs = document.querySelectorAll('.curator-message-wrap');
        const lastMsg = msgs[msgs.length - 1];
        assert("Curator message renders in DOM with clean text", lastMsg && lastMsg.textContent.includes('Culture Atlas Curator'));

      } catch (err) {
        results.push({ name: 'Exception in suite', pass: false, extra: err.toString() });
      }

      const out = document.createElement('div');
      out.id = 'test-results-output';
      out.setAttribute('data-results', JSON.stringify(results));
      document.body.appendChild(out);
    });
    </script>
    """

    harness_html = html.replace("</body>", f"{test_script}</body>")
    temp_file = os.path.join(tempfile.gettempdir(), "test_curator_character_harness.html")
    with open(temp_file, "w", encoding="utf-8") as f:
        f.write(harness_html)

    chrome_bin = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    cmd = [
        chrome_bin,
        "--headless=new",
        "--dump-dom",
        f"file://{temp_file}"
    ]

    print("\n--- RUNNING CURATOR CHARACTER & SLOP-FREE INTEGRATION SUITE ---")
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=30)
    out = proc.stdout

    marker = 'id="test-results-output" data-results="'
    if marker not in out:
        print("ERROR: Test marker not found in output. Stderr:")
        print(proc.stderr[:1000])
        raise AssertionError("Headless Chrome failed to run character test harness!")

    raw_json = out.split(marker)[1].split('"')[0]
    results = json.loads(html_lib.unescape(raw_json))

    all_passed = True
    for r in results:
        status = "PASS" if r['pass'] else "FAIL"
        extra = f" ({r['extra']})" if r.get('extra') else ""
        print(f"[{status}] {r['name']}{extra}")
        if not r['pass']:
            all_passed = False

    assert all_passed, "Some curator character tests failed!"
    print("\n🎉 ALL CURATOR INTEGRITY CHECKS PASSED: ZERO SLOP, 100% ANALYTICAL PRECISION!")

if __name__ == "__main__":
    test_static_files()
    test_headless_character_execution()
