import os
import subprocess
import json
import tempfile
import html as html_lib

def test_centered_chat_greeting():
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

        # 1. Ensure NO circular CA avatar badge exists in chat or typing indicator
        assert 'rounded-full bg-[#262626] border border-[#383838] flex items-center justify-center text-[10px] font-mono text-[#a1a1aa] shrink-0 mt-0.5 select-none' not in content, f"CA avatar badge found in {p}"
        assert '>CA</div>' not in content, f"CA text avatar found in {p}"

        # 2. Ensure NO 'Culture Atlas Curator' header title text is rendered inside chat bubbles
        assert '<span class="text-[12px] font-mono text-[#71717a]">Culture Atlas Curator</span>' not in content, f"Curator header title found in {p}"

        # 3. Ensure 'What should we work on?' hero heading is present in initCuratorConversation
        assert 'What should we work on?' in content, f"Missing 'What should we work on?' hero heading in {p}"
        assert 'curatorHeroGreeting' in content, f"Missing curatorHeroGreeting in {p}"
        assert 'curatorScrollContent' in content, f"Missing curatorScrollContent in {p}"

    print("✅ Static markup & code checks passed across all targets!")

    # 4. Headless Chrome runtime validation
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
        const scrollArea = document.getElementById('curatorScrollArea');
        const scrollContent = document.getElementById('curatorScrollContent');
        const hero = document.getElementById('curatorHeroGreeting');
        const heading = hero ? hero.querySelector('h1') : null;
        const speakBtn = hero ? hero.querySelector('.curator-speak-btn') : null;
        const suggestions = document.getElementById('workSuggestionsSection');

        // Check 1: Initial state on load
        assert("Hero greeting container exists on load", !!hero);
        assert("Heading exists and text is 'What should we work on?'", heading && heading.textContent.trim() === 'What should we work on?', heading ? heading.textContent : 'none');
        assert("Heading has centered text classes", heading && heading.className.includes('text-center'), heading?.className);
        assert("Scroll content has my-auto class for vertical centering in the middle", scrollContent && scrollContent.classList.contains('my-auto'));
        assert("Curator speak button exists on hero greeting", !!speakBtn);
        assert("Suggestions section is visible on load", suggestions && !suggestions.classList.contains('hidden'));

        // Check 2: Verify absolute absence of CA avatar or Curator header title
        const allCaBadges = document.querySelectorAll('.curator-message-wrap .rounded-full');
        const hasCaText = Array.from(allCaBadges).some(b => b.textContent.trim() === 'CA');
        assert("No CA avatar badge in initial greeting", !hasCaText);

        const allTitles = document.querySelectorAll('.curator-message-wrap span');
        const hasCuratorTitle = Array.from(allTitles).some(t => t.textContent.includes('Culture Atlas Curator'));
        assert("No 'Culture Atlas Curator' header in initial greeting", !hasCuratorTitle);

        // Check 3: Check appendCuratorMessage also does not have avatar or logo
        appendCuratorMessage("<p>Test curator intelligence narrative without logo.</p>");
        const msgWraps = document.querySelectorAll('.curator-message-wrap');
        const lastMsg = msgWraps[msgWraps.length - 1];

        const lastMsgCa = Array.from(lastMsg.querySelectorAll('.rounded-full')).some(b => b.textContent.trim() === 'CA');
        assert("Subsequent curator message has NO CA avatar badge", !lastMsgCa);

        const lastMsgTitle = Array.from(lastMsg.querySelectorAll('span')).some(t => t.textContent.includes('Culture Atlas Curator'));
        assert("Subsequent curator message has NO 'Culture Atlas Curator' title", !lastMsgTitle);

        assert("Subsequent curator message has curator-speak-btn", !!lastMsg.querySelector('.curator-speak-btn'));

        // Check 4: On sending message, my-auto is removed so chat flows naturally
        assert("scrollContent my-auto is removed after message appended", !scrollContent.classList.contains('my-auto'));

        // Check 5: resetToNewChat restores centered hero greeting
        resetToNewChat();
        const resetHero = document.getElementById('curatorHeroGreeting');
        assert("resetToNewChat restores centered hero greeting", !!resetHero);
        assert("resetToNewChat restores scrollContent my-auto class", scrollContent.classList.contains('my-auto'));

      } catch (err) {
        results.push({ name: "Runtime Exception", pass: false, extra: err.toString() });
      }

      const out = document.createElement('div');
      out.id = 'test-results-output';
      out.setAttribute('data-results', JSON.stringify(results));
      document.body.appendChild(out);
    });
    </script>
    """

    harness_html = html.replace("</body>", f"{test_script}</body>")
    temp_file = os.path.join(tempfile.gettempdir(), "test_centered_greeting_harness.html")
    with open(temp_file, "w", encoding="utf-8") as f:
        f.write(harness_html)

    chrome_bin = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    cmd = [
        chrome_bin,
        "--headless=new",
        "--dump-dom",
        f"file://{temp_file}"
    ]

    print("\n--- RUNNING HEADLESS CHROME CENTERED CHAT GREETING SUITE ---")
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=50)
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
        print("\n🎉 ALL CENTERED CHAT GREETING & AVATAR REMOVAL TESTS PASSED PERFECTLY!")
    return all_passed

if __name__ == "__main__":
    success = test_centered_chat_greeting()
    if not success:
        exit(1)
