import os
import subprocess
import json
import tempfile
import html as html_lib

def run_tests():
    index_path = "/Users/polinavasilyeva/.gemini/antigravity/scratch/sponsor-atlas/index.html"
    assert os.path.exists(index_path), "index.html must exist"

    with open(index_path, "r", encoding="utf-8") as f:
        html = f.read()

    test_script = """
    <script>
    // Stub fetch so headless chrome does not wait for external tiles
    const origFetch = window.fetch;
    window.fetch = async (url, opts) => {
      const urlStr = typeof url === 'string' ? url : (url && url.url ? url.url : '');
      if (urlStr.includes('.pbf') || urlStr.includes('openfreemap') || urlStr.includes('tile')) {
        return new Response(new Uint8Array(0), { status: 200 });
      }
      return origFetch(url, opts);
    };

    window.addEventListener('load', async () => {
      const results = [];
      function assert(name, condition, extra = '') {
        results.push({ name, pass: !!condition, extra });
      }

      try {
        // 1. cleanTextForSpeech exists
        assert('cleanTextForSpeech is available on window', typeof window.cleanTextForSpeech === 'function');

        // 2. cleanTextForSpeech expands abbreviations, strips markdown, URLs, arrows, emojis
        const rawSample = `
          ### Chisenhale Gallery
          **Chisenhale Gallery** is a 501(c)(3) Tier A · Verified Clean Sanctuary.
          Open Tue–Sat, e.g., for public viewings.
          - Admission: Free (audit dossier · https://chisenhale.org.uk ↗)
          🎨 Visit today!
        `;
        const cleaned = window.cleanTextForSpeech(rawSample);
        assert('cleanTextForSpeech expands 501(c)(3)', cleaned.includes('501-c-3 non-profit'), cleaned);
        assert('cleanTextForSpeech expands Tue-Sat', cleaned.includes('Tuesday through Saturday'), cleaned);
        assert('cleanTextForSpeech expands e.g.', cleaned.includes('for example'), cleaned);
        assert('cleanTextForSpeech expands Tier A sanctuary', cleaned.includes('Tier A verified clean sanctuary'), cleaned);
        assert('cleanTextForSpeech strips markdown headers', !cleaned.includes('#'), cleaned);
        assert('cleanTextForSpeech strips markdown bold', !cleaned.includes('**'), cleaned);
        assert('cleanTextForSpeech strips raw URLs', !cleaned.includes('https://'), cleaned);
        assert('cleanTextForSpeech strips emojis', !cleaned.includes('🎨'), cleaned);
        assert('cleanTextForSpeech strips arrows', !cleaned.includes('↗'), cleaned);

        // 3. DOM extraction excludes action buttons, links and data-exclude-speech
        const testDom = document.createElement('div');
        testDom.innerHTML = `
          <div class="curator-speak-btn"><span class="speak-label">Listen</span></div>
          <p>Serpentine North is an essential independent arts pavilion.</p>
          <div data-exclude-speech="true">
            <span>Admission: Free</span>
            <button class="curator-dossier-btn">Dossier ↗</button>
          </div>
          <div class="curator-followup-pill">Followup Pill</div>
        `;
        const domCleaned = window.cleanTextForSpeech(testDom);
        assert('DOM extraction includes core prose', domCleaned.includes('Serpentine North is an essential independent arts pavilion.'), domCleaned);
        assert('DOM extraction strips Listen button label', !domCleaned.includes('Listen'), domCleaned);
        assert('DOM extraction strips Dossier button', !domCleaned.includes('Dossier'), domCleaned);
        assert('DOM extraction strips Followup pills', !domCleaned.includes('Followup Pill'), domCleaned);
        assert('DOM extraction strips data-exclude-speech content', !domCleaned.includes('Admission: Free'), domCleaned);

        // 4. splitTextIntoSentences exists and correctly chunks long paragraphs
        assert('splitTextIntoSentences is available on window', typeof window.splitTextIntoSentences === 'function');
        const longDocentText = "Chisenhale Gallery was founded by artists in 1980 in a former veneer factory in London's East End. It has produced over two hundred newly commissioned solo exhibitions by artists from across the world. The gallery operates completely free of fossil fuel sponsorship, weapons manufacturers, and predatory corporate underwriting. Admission is completely free, making contemporary art widely accessible to the local Bow community and international visitors.";
        const chunks = window.splitTextIntoSentences(longDocentText, 150);
        assert('splitTextIntoSentences chunks long text', chunks.length >= 2, `chunks: ${chunks.length}`);
        const allUnderLimit = chunks.every(c => c.length <= 175);
        assert('splitTextIntoSentences keeps chunks <= 175 chars to avoid Chrome cutoff bug', allUnderLimit, JSON.stringify(chunks));

        // 5. selectCuratorVoice prioritizes natural/enhanced voices
        assert('selectCuratorVoice is available on window', typeof window.selectCuratorVoice === 'function');
        const origGetVoices = window.speechSynthesis ? window.speechSynthesis.getVoices : null;
        if (!window.speechSynthesis) {
          window.speechSynthesis = { getVoices: () => [], speak: () => {}, cancel: () => {}, pause: () => {}, resume: () => {} };
        }
        window.speechSynthesis.getVoices = () => [
          { name: 'Bad Voice', lang: 'es-ES' },
          { name: 'Alex', lang: 'en-US' },
          { name: 'Daniel (Natural)', lang: 'en-GB' },
          { name: 'Samantha (Enhanced)', lang: 'en-US' }
        ];
        const chosenVoice = window.selectCuratorVoice();
        assert('selectCuratorVoice selects enhanced/natural voice', chosenVoice && (chosenVoice.name.includes('Samantha') || chosenVoice.name.includes('Natural') || chosenVoice.name.includes('Enhanced')), chosenVoice ? chosenVoice.name : 'null');
        if (origGetVoices) window.speechSynthesis.getVoices = origGetVoices;

        // 6. Initial curator message has speak button with speak-icon and Listen label
        const initialSpeakBtn = document.querySelector('.curator-speak-btn');
        assert('Initial curator message has curator-speak-btn', !!initialSpeakBtn);
        const speakIcon = initialSpeakBtn ? initialSpeakBtn.querySelector('.speak-icon') : null;
        const speakLabel = initialSpeakBtn ? initialSpeakBtn.querySelector('.speak-label') : null;
        assert('curator-speak-btn has .speak-icon', !!speakIcon && speakIcon.textContent === '🔊');
        assert('curator-speak-btn has .speak-label with "Listen"', !!speakLabel && speakLabel.textContent === 'Listen');

        // 7. speakCuratorText toggles between speaking Stop (⏹️) and idle Listen (🔊)
        let speakCalled = false;
        let cancelCalled = false;
        window.speechSynthesis.speak = (u) => {
          speakCalled = true;
          setTimeout(() => { if (u && u.onend) u.onend(); }, 15);
        };
        window.speechSynthesis.cancel = () => {
          cancelCalled = true;
        };

        const testMsgDiv = initialSpeakBtn.closest('.curator-message-wrap');
        window.speakCuratorText(testMsgDiv, initialSpeakBtn);
        assert('speakCuratorText adds active class to button', initialSpeakBtn.classList.contains('text-rose-400'));
        assert('speakCuratorText changes label to Stop', speakLabel.textContent === 'Stop');
        assert('speakCuratorText changes icon to ⏹️', speakIcon.textContent === '⏹️');
        assert('speakCuratorText calls window.speechSynthesis.speak', speakCalled);

        // Clicking again toggles off
        window.speakCuratorText(testMsgDiv, initialSpeakBtn);
        assert('speakCuratorText removes active class on stop', !initialSpeakBtn.classList.contains('text-rose-400'));
        assert('speakCuratorText reverts label to Listen', speakLabel.textContent === 'Listen');
        assert('speakCuratorText reverts icon to 🔊', speakIcon.textContent === '🔊');
        assert('speakCuratorText calls window.speechSynthesis.cancel', cancelCalled);

        // 8. Conversational greeting "hello"
        const workInput = document.getElementById('workInput');
        const workSendBtn = document.getElementById('workSendBtn');
        workInput.value = 'hello';
        workSendBtn.click();

        await new Promise(r => setTimeout(r, 450));
        let msgs = document.querySelectorAll('.curator-message-wrap');
        let lastMsg = msgs[msgs.length - 1];
        assert('Greeting returns "Hello! I am your Culture Atlas Curator."', lastMsg.innerText.includes('Hello! I am your Culture Atlas Curator.'), lastMsg.innerText);

        // 9. Conversational intent "make it talk properly"
        workInput.value = 'make it talk properly';
        workSendBtn.click();

        await new Promise(r => setTimeout(r, 450));
        msgs = document.querySelectorAll('.curator-message-wrap');
        lastMsg = msgs[msgs.length - 1];
        assert('Intent "make it talk properly" activates docent', lastMsg.innerText.includes('Curator Audio Docent Active'), lastMsg.innerText);

        // 10. Entity query returns articulate narrative + structured card with data-exclude-speech
        workInput.value = 'Chisenhale Gallery';
        workSendBtn.click();

        await new Promise(r => setTimeout(r, 450));
        msgs = document.querySelectorAll('.curator-message-wrap');
        lastMsg = msgs[msgs.length - 1];
        const instCleaned = window.cleanTextForSpeech(lastMsg);
        const hasCard = !!lastMsg.querySelector('.grid');
        const hasExcluded = !!lastMsg.querySelector('[data-exclude-speech="true"]');

        assert('Institution query renders structured data grid card', hasCard);
        assert('Institution query data card has data-exclude-speech', hasExcluded);
        assert('Spoken text contains articulate narrative overview', instCleaned.includes('verified Tier A clean sanctuary'), instCleaned);
        assert('Spoken text omits raw database bullets', !instCleaned.includes('- Ethical Status:'), instCleaned);

        // 11. Material Research Inquiry does NOT false-match Raw Material Company and provides forensic methodology response
        curatorContext.lastInst = null;
        workInput.value = 'have you done any material research, or is all this based on online available information?';
        workSendBtn.click();

        await new Promise(r => setTimeout(r, 450));
        msgs = document.querySelectorAll('.curator-message-wrap');
        lastMsg = msgs[msgs.length - 1];

        assert('Material research inquiry does not match Raw Material Company', !lastMsg.innerText.includes('Raw Material Company'), lastMsg.innerText);
        assert('Material research inquiry does not set curatorContext.lastInst to Raw Material Company', !curatorContext.lastInst || !curatorContext.lastInst.name.includes('Raw Material'), curatorContext.lastInst ? curatorContext.lastInst.name : 'null');
        assert('Material research inquiry returns forensic methodology card', lastMsg.innerText.includes('Material Research vs. Corporate Artwashing'), lastMsg.innerText);
        assert('Methodology explains IRS Form 990 statutory disclosures', lastMsg.innerText.includes('IRS Form 990'), lastMsg.innerText);
        assert('Methodology explains regulatory perjury penalties', lastMsg.innerText.includes('penalties'), lastMsg.innerText);
        assert('Methodology explains trustee corporate cross-referencing', lastMsg.innerText.includes('Trustee Corporate Cross-Referencing'), lastMsg.innerText);
        assert('Methodology explains activist direct action and FOI leaks', lastMsg.innerText.includes('Activist Direct Action & FOI Leaks'), lastMsg.innerText);
        assert('Methodology explains material structural autonomy', lastMsg.innerText.includes('Material Structural Autonomy'), lastMsg.innerText);

        // 12. Rhetorical Inquiry: "what organisation would knowingly make information about their unethical practices available online?"
        workInput.value = 'what organisation would knowingly make information about their unethical practices available online?';
        workSendBtn.click();

        await new Promise(r => setTimeout(r, 450));
        msgs = document.querySelectorAll('.curator-message-wrap');
        lastMsg = msgs[msgs.length - 1];

        assert('Unethical practices online inquiry returns forensic critique', lastMsg.innerText.includes('Material Research vs. Corporate Artwashing'), lastMsg.innerText);
        assert('Affirms all the bad info is publicly available too', lastMsg.innerText.includes('all the bad info is publicly available too'), lastMsg.innerText);
        assert('Unethical practices inquiry does not set curatorContext.lastInst to Raw Material Company', !curatorContext.lastInst || !curatorContext.lastInst.name.includes('Raw Material'), curatorContext.lastInst ? curatorContext.lastInst.name : 'null');

        // 13. "i need to train it to talk back" activates Critical Sparring Mode
        workInput.value = 'i need to train it to talk back';
        workSendBtn.click();

        await new Promise(r => setTimeout(r, 450));
        msgs = document.querySelectorAll('.curator-message-wrap');
        lastMsg = msgs[msgs.length - 1];

        assert('Talk back inquiry activates critical sparring mode', lastMsg.innerText.includes('Curator Critical Sparring Mode Active'), lastMsg.innerText);
        assert('Sparring mode shows Trained to Talk Back badge', lastMsg.innerText.includes('Trained to Talk Back'), lastMsg.innerText);
        assert('Sparring mode accepts challenge with critical teeth', lastMsg.innerText.includes('built with critical teeth'), lastMsg.innerText);

        // 14. "and all bad info is also publicly availiable" returns the open-source intelligence cross-examination
        workInput.value = 'and all bad info is also publicly availiable';
        workSendBtn.click();

        await new Promise(r => setTimeout(r, 450));
        msgs = document.querySelectorAll('.curator-message-wrap');
        lastMsg = msgs[msgs.length - 1];

        assert('Publicly available bad info query returns forensic methodology', lastMsg.innerText.includes('Material Research vs. Corporate Artwashing'), lastMsg.innerText);
        assert('Explicitly states all bad info is publicly available too', lastMsg.innerText.includes('all the bad info is publicly available too'), lastMsg.innerText);

        window.stopCuratorSpeech();

      } catch (err) {
        assert('JavaScript Execution Exception', false, err.stack || err.toString());
      }

      const out = document.createElement('div');
      out.id = 'test-results-output';
      out.setAttribute('data-results', JSON.stringify(results));
      document.body.appendChild(out);
    });
    </script>
    """

    harness_html = html.replace("</body>", f"{test_script}</body>")
    temp_file = os.path.join(tempfile.gettempdir(), "test_talk_properly_harness.html")
    with open(temp_file, "w", encoding="utf-8") as f:
        f.write(harness_html)

    chrome_bin = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

    print("--- RUNNING TALK PROPERLY & AUDIO DOCENT SUITE ---")
    cmd = [
        chrome_bin,
        "--headless=new",
        "--dump-dom",
        "--window-size=1280,800",
        "--virtual-time-budget=5000",
        f"file://{temp_file}"
    ]
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=60)
    marker = 'id="test-results-output" data-results="'
    if marker not in proc.stdout:
        print("ERROR: Test marker not found in output. Stderr:")
        print(proc.stderr[:1000])
        return False

    results = json.loads(html_lib.unescape(proc.stdout.split(marker)[1].split('"')[0]))
    all_passed = True
    for r in results:
        status = "PASS" if r['pass'] else "FAIL"
        if not r['pass']:
            all_passed = False
        extra = f" ({r['extra']})" if r.get('extra') else ""
        print(f"[{status}] {r['name']}{extra}")

    if all_passed:
        print("\nALL TALK PROPERLY & AUDIO DOCENT TESTS PASSED!")
    return all_passed

if __name__ == "__main__":
    success = run_tests()
    if not success:
        exit(1)
