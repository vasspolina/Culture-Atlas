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
        
        # Check system prompt presence of Alisa persona & art slang
        assert "Yandex Alisa" in content, f"Missing Yandex Alisa in {p}"
        assert "British Art Scene" in content, f"Missing British Art Scene in {p}"
        assert "American Gallery Circuit" in content, f"Missing American Gallery Circuit in {p}"
        assert "white cube fatigue" in content, f"Missing white cube fatigue in {p}"
        assert "curatorial gymnastics" in content, f"Missing curatorial gymnastics in {p}"
        assert "blue-chip darlings" in content, f"Missing blue-chip darlings in {p}"
        assert "private view" in content.lower(), f"Missing private view in {p}"
        assert "vernissage" in content.lower(), f"Missing vernissage in {p}"
        assert "taking the piss" in content.lower(), f"Missing taking the piss in {p}"
        
        # Check offline responses
        assert "Well, hello there! Welcome to the unvarnished side of the gallery." in content, f"Missing greeting in {p}"
        assert "Curator Critical Sparring Mode Active" in content, f"Missing Sparring mode in {p}"
        assert "Oh, you want to spar? Challenge accepted." in content, f"Missing Alisa talk back line in {p}"
        assert "lukewarm vernissage prosecco" in content, f"Missing gossip line in {p}"
        assert "Fresh off the plinth" in content, f"Missing show line in {p}"
        assert "Which cultural space are we interrogating today?" in content, f"Missing unselected check line in {p}"
        assert "Feeling adventurous? Let's skip the over-hyped blue-chip tourist traps" in content, f"Missing surprise me line in {p}"
        assert "Alright, you've either stumped me or you're testing my curatorial patience!" in content, f"Missing fallback line in {p}"

    print("✅ All static files contain Yandex Alisa persona and British & American art slang!")

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
        // 1. Check thinking plan thoughts have Alisa wit & art slang
        const instPlan = generateThinkingPlan("Chisenhale Gallery");
        assert("Institution thinking plan has curatorial gymnastics slang", instPlan.thought.includes('curatorial gymnastics') || instPlan.thought.includes('independent darling'), instPlan.thought);

        const cityPlan = generateThinkingPlan("independent spaces in Berlin");
        assert("City thinking plan has white cube fatigue slang", cityPlan.thought.includes('white cube fatigue'), cityPlan.thought);

        const crawlPlan = generateThinkingPlan("plan an art crawl");
        assert("Crawl thinking plan has Frieze exhaustion slang", crawlPlan.thought.includes('Frieze-week exhaustion'), crawlPlan.thought);

        const budgetPlan = generateThinkingPlan("museum budget 2026");
        assert("Budget thinking plan has vanity projects slang", budgetPlan.thought.includes('donor-class vanity projects'), budgetPlan.thought);

        const trusteePlan = generateThinkingPlan("trustee conflicts");
        assert("Trustee thinking plan has vernissage prosecco slang", trusteePlan.thought.includes('vernissage prosecco'), trusteePlan.thought);

        // 2. Check queryAI criticalSystemPrompt contains Alisa character & art slang
        const queryAiStr = typeof queryAI === 'function' ? queryAI.toString() : '';
        assert("queryAI contains Yandex Alisa persona instruction", queryAiStr.includes('Yandex Alisa'));
        assert("queryAI contains British Art Scene slang section", queryAiStr.includes('British Art Scene'));
        assert("queryAI contains American Gallery Circuit slang section", queryAiStr.includes('American Gallery Circuit'));
        assert("queryAI contains 'white cube fatigue'", queryAiStr.includes('white cube fatigue'));
        assert("queryAI contains 'curatorial gymnastics'", queryAiStr.includes('curatorial gymnastics'));
        assert("queryAI contains 'blue-chip darlings'", queryAiStr.includes('blue-chip darlings'));
        assert("queryAI contains 'taking the piss'", queryAiStr.includes('taking the piss'));

        // 3. Check handleCuratorQuery contains Alisa persona lines & transatlantic art slang
        const handleStr = typeof handleCuratorQuery === 'function' ? handleCuratorQuery.toString() : '';
        assert("handleCuratorQuery contains witty Alisa greeting", handleStr.includes('Well, hello there! Welcome to the unvarnished side of the gallery'));
        assert("handleCuratorQuery greeting contains 'white cube fatigue'", handleStr.includes('white cube fatigue'));
        assert("handleCuratorQuery greeting contains 'Chelsea gallery crawl'", handleStr.includes('Chelsea gallery crawl'));
        assert("handleCuratorQuery sparring has Alisa challenge", handleStr.includes('Oh, you want to spar? Challenge accepted'));
        assert("handleCuratorQuery sparring has 'taking the piss'", handleStr.includes('taking the piss'));
        assert("handleCuratorQuery sparring has 'curatorial throat-clearing'", handleStr.includes('curatorial throat-clearing'));
        assert("handleCuratorQuery gossip has 'vernissage prosecco'", handleStr.includes('vernissage prosecco'));
        assert("handleCuratorQuery exhibition has 'Fresh off the plinth'", handleStr.includes('Fresh off the plinth'));
        assert("handleCuratorQuery audit has 'curatorial gymnastics'", handleStr.includes('curatorial gymnastics'));
        assert("handleCuratorQuery surprise has 'blue-chip tourist traps'", handleStr.includes('blue-chip tourist traps'));
        assert("handleCuratorQuery fallback has 'curatorial patience'", handleStr.includes('testing my curatorial patience'));
        assert("handleCuratorQuery city match has 'bloody brilliant'", handleStr.includes('bloody brilliant'));
        assert("handleCuratorQuery city match has 'blue-chip hype train'", handleStr.includes('blue-chip hype train'));
        assert("handleCuratorQuery artwashing has 'reputation laundering'", handleStr.includes('reputation laundering'));

        // 4. Test rendering of an Alisa-style witty response in DOM
        appendCuratorMessage("<p>Well, hello there! Welcome to the unvarnished side of the gallery. Think of me as your resident Culture Atlas curator with the sharp wit of Yandex Alisa and an encyclopedia of transatlantic art slang.</p>");
        const msgs = document.querySelectorAll('.curator-message-wrap');
        const lastMsg = msgs[msgs.length - 1];
        assert("Curator message renders in DOM with Alisa text", lastMsg && lastMsg.textContent.includes('sharp wit of Yandex Alisa'));

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

    print("\n--- RUNNING CURATOR CHARACTER & ART SLANG SUITE ---")
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
    print("\n🎉 ALL CURATOR CHARACTER & TRANSATLANTIC ART SLANG CHECKS PASSED PERFECTLY!")

if __name__ == "__main__":
    test_static_files()
    test_headless_character_execution()
