import os
import subprocess
import json
import tempfile
import time

def run_tests():
    index_path = "/Users/polinavasilyeva/.gemini/antigravity/scratch/sponsor-atlas/index.html"
    artifact_path = "/Users/polinavasilyeva/.gemini/antigravity/brain/b997e616-4551-453e-83cc-4ba184f90abf/culture_atlas_app.html"

    assert os.path.exists(index_path), "index.html must exist"
    assert os.path.exists(artifact_path), "culture_atlas_app.html must exist"

    # Create a test harness page that embeds the index.html logic and runs assertions
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
        // Test 1: Initial state without key
        localStorage.clear();
        if (typeof updateAIStatusUI === 'function') updateAIStatusUI();

        const topBtn = document.getElementById('topSettingsBtn');
        const topLabel = document.getElementById('topStatusLabel');
        const topDot = document.getElementById('topStatusDot');
        const modal = document.getElementById('curatorSettingsModal');
        const keyInput = document.getElementById('aiApiKeyInput');
        const modelLabel = document.getElementById('workModelLabel');

        assert("Top settings button exists", topBtn !== null);
        assert("Top label shows live system status initially", topLabel && (topLabel.textContent.includes('Anthropic Live') || topLabel.textContent.includes('Add API Key')), topLabel?.textContent);
        assert("Redundant chat Add Key button is deleted", document.getElementById('chatAddKeyBtn') === null);
        assert("Modal exists and is hidden initially", modal && modal.classList.contains('hidden'));

        // Test 2: Click topSettingsBtn opens modal
        topBtn.click();
        assert("Clicking topSettingsBtn opens modal", modal && !modal.classList.contains('hidden'));

        // Test 3: Close modal
        document.getElementById('closeSettingsModalBtn').click();
        assert("Clicking close button closes modal", modal && modal.classList.contains('hidden'));

        // Test 4: Click workModelBtn opens modal
        document.getElementById('workModelBtn').click();
        assert("Clicking workModelBtn opens modal", modal && !modal.classList.contains('hidden'));
        document.getElementById('closeSettingsModalBtn').click();

        // Test 6: Conversational intent 'add api key'
        await handleCuratorQuery("add api key");
        assert("Querying 'add api key' opens modal", modal && !modal.classList.contains('hidden'));
        const messages = document.getElementById('curatorMessages').innerHTML;
        assert("Curator response contains Anthropic link", messages.includes('console.anthropic.com'));
        assert("Curator response contains OpenAI link", messages.includes('platform.openai.com'));
        assert("Curator response contains Gemini link", messages.includes('aistudio.google.com'));

        // Test 7: Enter Claude key via chat
        await handleCuratorQuery("sk-ant-test-key-mock-12345");
        assert("API key saved in localStorage", localStorage.getItem('atlas_ai_api_key') === 'sk-ant-test-key-mock-12345');
        assert("Top status updated to Anthropic Live", topLabel && topLabel.textContent.includes('Anthropic Live'), topLabel?.textContent);
        assert("Work model updated with Anthropic", modelLabel && modelLabel.textContent.includes('Anthropic'), modelLabel?.textContent);

        // Test 8: Disconnect / Clear key
        document.getElementById('clearApiKeyBtn').click();
        assert("API key cleared from localStorage", !localStorage.getItem('atlas_ai_api_key'));
        assert("Top status reverted to default system Anthropic Live", topLabel && (topLabel.textContent.includes('Anthropic Live') || topLabel.textContent.includes('Add API Key')), topLabel?.textContent);

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
    temp_file = os.path.join(tempfile.gettempdir(), "test_culture_atlas_harness.html")
    with open(temp_file, "w", encoding="utf-8") as f:
        f.write(harness_html)

    chrome_bin = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    cmd = [
        chrome_bin,
        "--headless=new",
        "--dump-dom",
        "--virtual-time-budget=6000",
        f"file://{temp_file}"
    ]

    print("Running headless Chrome verification...")
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=60)
    out = proc.stdout

    marker = 'id="test-results-output" data-results="'
    if marker not in out:
        print("ERROR: Test marker not found in output. Stderr:")
        print(proc.stderr[:1000])
        return False

    raw_json = out.split(marker)[1].split('"')[0]
    import html as html_lib
    results = json.loads(html_lib.unescape(raw_json))

    all_passed = True
    print("\n--- TEST RESULTS ---")
    for r in results:
        status = "PASS" if r['pass'] else "FAIL"
        if not r['pass']:
            all_passed = False
        extra = f" ({r['extra']})" if r.get('extra') else ""
        print(f"[{status}] {r['name']}{extra}")

    print(f"\nSummary: {sum(1 for r in results if r['pass'])}/{len(results)} passed.")
    return all_passed

if __name__ == "__main__":
    success = run_tests()
    if not success:
        exit(1)
