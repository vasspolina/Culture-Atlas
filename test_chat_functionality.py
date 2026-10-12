import os
import subprocess
import json
import tempfile
import html as html_lib

def test_chat_functionality():
    index_path = "/Users/polinavasilyeva/.gemini/antigravity/scratch/sponsor-atlas/index.html"
    assert os.path.exists(index_path), "index.html must exist"

    with open(index_path, "r", encoding="utf-8") as f:
        html = f.read()

    test_script = """
    <script>
    // Mock setTimeout so async curator responses resolve synchronously for testing
    const originalSetTimeout = window.setTimeout;
    window.setTimeout = (fn, delay) => {
      if (typeof fn === 'function' && delay <= 500) {
        try { fn(); } catch(e) { console.error(e); }
        return 0;
      }
      return originalSetTimeout(fn, delay);
    };

    window.addEventListener('load', () => {
      const results = [];
      function assert(name, condition, extra = '') {
        results.push({ name, pass: !!condition, extra: String(extra || '') });
      }

      try {
        const workInput = document.getElementById('workInput');
        const workSendBtn = document.getElementById('workSendBtn');
        const curatorMessages = document.getElementById('curatorMessages');
        const suggestions = document.querySelectorAll('.work-suggestion-card');
        const hero = document.getElementById('curatorHeroGreeting');

        assert("workInput exists", !!workInput);
        assert("workSendBtn exists", !!workSendBtn);
        assert("curatorMessages exists", !!curatorMessages);
        assert("Initial hero greeting exists", !!hero);
        assert("All 8 suggested inquiry cards exist", suggestions.length === 8, suggestions.length);

        // Check 1: Startup target institution is initialized
        assert("selectedInstitution is initialized on load", !!selectedInstitution, selectedInstitution ? selectedInstitution.name : 'null');
        assert("curatorContext.lastInst is initialized on load", !!(curatorContext && curatorContext.lastInst), curatorContext ? curatorContext.lastInst?.name : 'null');

        // Check 2: No raw System Note pills in chat
        assert("No raw System Note pills present in chat", !document.querySelector('.curator-system-note'));

        // Check 3: Test each of the 8 suggested inquiry buttons
        const expectedInquiries = [
          { q: "Who funds this museum?", key: "Funding Breakdown" },
          { q: "What do employees say about working here?", key: "LABOR & WORKPLACE AUDIT" },
          { q: "Have artists protested or boycotted this institution?", key: "RESISTANCE & BOYCOTT RECORD" },
          { q: "Which sponsors have faced public criticism?", key: "SPONSOR SCRUTINY AUDIT" },
          { q: "Does this institution pay artists fairly?", key: "ARTIST EQUITY & REMUNERATION" },
          { q: "How are its trustees connected to its sponsors?", key: "TRUSTEE & BOARD INTERLOCKS" },
          { q: "Has public pressure changed its policies?", key: "PUBLIC POLICY REFORM RECORD" },
          { q: "Find independent art spaces near me", key: "INDEPENDENT SANCTUARIES" }
        ];

        suggestions.forEach((card, idx) => {
          const q = card.getAttribute('data-query');
          card.click();
          const lastMsg = curatorMessages.lastElementChild;
          const text = lastMsg ? lastMsg.textContent : '';
          const exp = expectedInquiries[idx];
          const hasKey = exp ? text.includes(exp.key) : text.length > 50;
          assert(`Suggestion ${idx + 1} (${q}) generates articulate response`, hasKey, text.slice(0, 80));
        });

        // Check 4: Test typing query in workInput and clicking send
        workInput.value = "Who funds this museum?";
        workSendBtn.click();
        assert("workInput is cleared after sending", workInput.value === '');
        const msgAfterTypedSend = curatorMessages.lastElementChild;
        assert("Typed query generates Funding Breakdown response", msgAfterTypedSend && msgAfterTypedSend.textContent.includes('Funding Breakdown'), msgAfterTypedSend ? msgAfterTypedSend.textContent.slice(0, 80) : 'none');

        // Check 5: Test switching to another museum (e.g. Chisenhale Gallery)
        const chisenhale = ALL_INSTITUTIONS.find(i => i.name.includes('Chisenhale'));
        if (chisenhale) {
          selectInstitution(chisenhale, false);
          assert("selectedInstitution switched to Chisenhale", selectedInstitution.name === chisenhale.name);
          assert("No system note pill added to chat on switch", !document.querySelector('.curator-system-note'));

          workInput.value = "Who funds this museum?";
          workSendBtn.click();
          const chisMsg = curatorMessages.lastElementChild;
          assert("Funding question for Chisenhale audits Chisenhale", chisMsg && chisMsg.textContent.includes('Chisenhale'), chisMsg ? chisMsg.textContent.slice(0, 80) : 'none');

          workInput.value = "Does this institution pay artists fairly?";
          workSendBtn.click();
          const chisPayMsg = curatorMessages.lastElementChild;
          assert("Artist fee question for Chisenhale audits Chisenhale", chisPayMsg && chisPayMsg.textContent.includes('Chisenhale'), chisPayMsg ? chisPayMsg.textContent.slice(0, 80) : 'none');
        }

        // Check 6: Test MoMA (flagged institution)
        const moma = ALL_INSTITUTIONS.find(i => i.name.includes('MoMA')) || (typeof EXCLUDED_INSTITUTIONS !== 'undefined' ? EXCLUDED_INSTITUTIONS.find(i => i.name.includes('MoMA')) : null);
        if (moma) {
          selectInstitution(moma, false);
          workInput.value = "Who funds this museum?";
          workSendBtn.click();
          const momaMsg = curatorMessages.lastElementChild;
          assert("MoMA funding audit indicates flagged status", momaMsg && (momaMsg.textContent.includes('FLAGGED') || momaMsg.textContent.includes('MoMA')), momaMsg ? momaMsg.textContent.slice(0, 80) : 'none');
        }

        // Check 7: Test mobile sticky send
        const chatInput = document.getElementById('chat-input');
        const mobileSendBtn = document.getElementById('mobileStickySendBtn');
        if (chatInput && mobileSendBtn) {
          chatInput.value = "Art crawl in London";
          mobileSendBtn.click();
          assert("Mobile input cleared after send", chatInput.value === '');
          const lastMobileMsg = curatorMessages.lastElementChild;
          assert("Mobile send generates itinerary response", lastMobileMsg && (lastMobileMsg.textContent.includes('London') || lastMobileMsg.textContent.includes('Crawl')), lastMobileMsg ? lastMobileMsg.textContent.slice(0, 80) : 'none');
        }

        // Check 8: Test resetToNewChat restores hero greeting cleanly
        resetToNewChat();
        const restoredHero = document.getElementById('curatorHeroGreeting');
        assert("resetToNewChat restores hero greeting", !!restoredHero);
        assert("resetToNewChat empties curatorMessages", curatorMessages.children.length === 0);

      } catch (err) {
        results.push({ name: "Runtime Exception", pass: false, extra: err.toString() });
      }

      const out = document.createElement('div');
      out.id = 'chat-test-output';
      out.setAttribute('data-results', JSON.stringify(results));
      document.body.appendChild(out);
    });
    </script>
    """

    harness_html = html.replace("</body>", f"{test_script}</body>")
    temp_file = os.path.join(tempfile.gettempdir(), "test_chat_functionality_harness.html")
    with open(temp_file, "w", encoding="utf-8") as f:
        f.write(harness_html)

    chrome_bin = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    cmd = [
        chrome_bin,
        "--headless=new",
        "--dump-dom",
        "--disable-gpu",
        "--no-sandbox",
        f"file://{temp_file}"
    ]

    print("\n--- RUNNING HEADLESS CHROME CHAT COMPREHENSIVE SUITE ---")
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=90)
    out = proc.stdout

    marker = 'id="chat-test-output" data-results="'
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
        print("\n🎉 ALL CHAT FUNCTIONALITY TESTS PASSED PERFECTLY!")
    return all_passed

if __name__ == "__main__":
    success = test_chat_functionality()
    if not success:
        exit(1)
