import os
import subprocess
import json
import tempfile
import html as html_lib

def test_chatgpt_thinking():
    files = [
        "/Users/polinavasilyeva/.gemini/antigravity/scratch/sponsor-atlas/index.html",
        "/Users/polinavasilyeva/.gemini/antigravity/scratch/sponsor-atlas/app/index.html",
        "/Users/polinavasilyeva/.gemini/antigravity/scratch/sponsor-atlas/app/standalone.html",
        "/Users/polinavasilyeva/.gemini/antigravity/brain/b997e616-4551-453e-83cc-4ba184f90abf/culture_atlas_app.html"
    ]

    for p in files:
        assert os.path.exists(p), f"Target file must exist: {p}"
        with open(p, "r", encoding="utf-8") as f:
            content = f.read()

        assert 'curatorThinkingTimer' in content, f"Missing curatorThinkingTimer in {p}"
        assert 'curatorThinkingThought' in content, f"Missing curatorThinkingThought in {p}"
        assert 'curatorThinkingStep' in content, f"Missing curatorThinkingStep in {p}"
        assert 'curatorThinkingStepLabel' in content, f"Missing curatorThinkingStepLabel in {p}"
        assert 'curator-thought-accordion' in content, f"Missing curator-thought-accordion in {p}"
        assert 'Working for' in content, f"Missing 'Working for' in {p}"
        assert 'Thought for' in content, f"Missing 'Thought for' in {p}"

    print("✅ Static markup checks passed across all target bundles!")

    # Headless Chrome runtime verification
    index_path = files[0]
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
        // 1. Verify thinking functions exist
        assert("generateThinkingPlan is a function", typeof generateThinkingPlan === 'function');
        assert("startCuratorThinking is a function", typeof startCuratorThinking === 'function');
        assert("stopCuratorThinking is a function", typeof stopCuratorThinking === 'function');

        // 2. Test generateThinkingPlan produces ChatGPT-like plans
        const defaultPlan = generateThinkingPlan("general inquiry");
        assert("Default plan has exact inspection sentence", defaultPlan.thought.includes("inspect the prepare job and workflow context, then propose the smallest reversible fix for review"), defaultPlan.thought);
        assert("Default plan has terminal scan step", defaultPlan.step.includes("Scanning Repository Configuration Files"), defaultPlan.step);

        const instPlan = generateThinkingPlan("Chisenhale Gallery");
        assert("Institution plan mentions governance / filings", instPlan.thought.includes("governance records"), instPlan.thought);
        assert("Institution step audits Form 990", instPlan.step.includes("Auditing Form 990"), instPlan.step);

        // 3. Test startCuratorThinking activates live UI
        startCuratorThinking("Find independent art spaces in London");
        const typingEl = document.getElementById('curatorTyping');
        const timerEl = document.getElementById('curatorThinkingTimer');
        const thoughtEl = document.getElementById('curatorThinkingThought');
        const stepEl = document.getElementById('curatorThinkingStep');
        const stepLabelEl = document.getElementById('curatorThinkingStepLabel');

        assert("curatorTyping is visible while thinking", typingEl && !typingEl.classList.contains('hidden'));
        assert("curatorThinkingTimer is initialized", timerEl && timerEl.textContent === '1');
        assert("curatorThinkingThought has inspection text", thoughtEl && thoughtEl.textContent.length > 10);
        assert("curatorThinkingStep has terminal icon", stepEl && !!stepEl.querySelector('svg'));
        assert("curatorThinkingStepLabel has step text", stepLabelEl && stepLabelEl.textContent.length > 5);

        // 4. Test stopCuratorThinking returns thinking data and hides UI
        const thinkingData = stopCuratorThinking();
        assert("stopCuratorThinking returns thinkingData object", !!thinkingData && typeof thinkingData.duration === 'number');
        assert("curatorTyping is hidden after stopCuratorThinking", typingEl.classList.contains('hidden'));

        // 5. Test appendCuratorMessage renders ChatGPT-style Thought accordion
        appendCuratorMessage("<p>Verified findings on London cultural spaces.</p>", [], null, thinkingData);
        const msgWraps = document.querySelectorAll('.curator-message-wrap');
        const lastMsg = msgWraps[msgWraps.length - 1];
        const accordion = lastMsg.querySelector('.curator-thought-accordion');
        const toggleBtn = lastMsg.querySelector('.curator-thought-toggle');
        const thoughtContent = lastMsg.querySelector('.curator-thought-content');
        const chevron = lastMsg.querySelector('.curator-thought-chevron');

        assert("Thought accordion rendered in message", !!accordion);
        assert("Accordion has data-exclude-speech for docent safety", accordion && accordion.getAttribute('data-exclude-speech') === 'true');
        assert("Toggle button shows 'Thought for Xs'", toggleBtn && toggleBtn.textContent.includes('Thought for'));
        assert("Thought content is initially collapsed (hidden)", thoughtContent && thoughtContent.classList.contains('hidden'));
        assert("Thought content has inspection sentence", thoughtContent && thoughtContent.textContent.includes(thinkingData.thought));
        assert("Thought content has terminal tool step", thoughtContent && thoughtContent.textContent.includes(thinkingData.step));

        // 6. Test clicking toggle expands accordion
        toggleBtn.click();
        assert("Clicking toggle unhides thought content", !thoughtContent.classList.contains('hidden'));
        assert("Clicking toggle rotates chevron", chevron && chevron.classList.contains('rotate-180'));

        // 7. Test clicking toggle collapses accordion
        toggleBtn.click();
        assert("Clicking toggle collapses thought content back to hidden", thoughtContent.classList.contains('hidden'));
        assert("Clicking toggle removes rotate-180 from chevron", !chevron.classList.contains('rotate-180'));

        // 8. Test cleanTextForSpeech ignores thought accordion
        const cleaned = window.cleanTextForSpeech(lastMsg);
        assert("cleanTextForSpeech excludes Thought text", !cleaned.includes('Thought for') && !cleaned.includes('Scanning Repository') && !cleaned.includes('inspect the prepare job'), cleaned);
        assert("cleanTextForSpeech includes actual narrative", cleaned.includes('Verified findings on London cultural spaces.'), cleaned);

      } catch (err) {
        results.push({ name: "Exception caught", pass: false, extra: err.toString() });
      }

      const out = document.createElement('div');
      out.id = 'test-results-output';
      out.setAttribute('data-results', JSON.stringify(results));
      document.body.appendChild(out);
    });
    </script>
    """

    harness_html = html.replace("</body>", f"{test_script}</body>")
    temp_file = os.path.join(tempfile.gettempdir(), "test_chatgpt_thinking_harness.html")
    with open(temp_file, "w", encoding="utf-8") as f:
        f.write(harness_html)

    chrome_bin = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    cmd = [
        chrome_bin,
        "--headless=new",
        "--dump-dom",
        f"file://{temp_file}"
    ]

    print("\n--- RUNNING CHATGPT THINKING MODEL HEADLESS SUITE ---")
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=30)
    out = proc.stdout

    marker = 'id="test-results-output" data-results="'
    if marker not in out:
        print("ERROR: Test marker not found in output. Stderr:")
        print(proc.stderr[:1000])
        return False

    raw_json = out.split(marker)[1].split('"')[0]
    results = json.loads(html_lib.unescape(raw_json))

    all_passed = True
    for r in results:
        status = "PASS" if r['pass'] else "FAIL"
        if not r['pass']:
            all_passed = False
        extra = f" ({r['extra']})" if r.get('extra') else ""
        print(f"[{status}] {r['name']}{extra}")

    if all_passed:
        print("\n🎉 ALL CHATGPT THINKING MODEL CHECKS PASSED PERFECTLY!")
    return all_passed

if __name__ == "__main__":
    success = test_chatgpt_thinking()
    if not success:
        exit(1)
