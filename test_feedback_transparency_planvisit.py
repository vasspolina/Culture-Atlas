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
        // =========================================================================
        // 1. EMPHASIZED TRANSPARENCY GRADE & NO BOXES WITHIN BOXES
        // =========================================================================
        const testInst = window.ALL_INSTITUTIONS.find(i => i.name.includes('Chisenhale')) || window.ALL_INSTITUTIONS[0];
        assert('Found test institution', !!testInst);

        window.atlasOpenDossier(testInst.name);
        const detailBody = document.getElementById('detailBody');
        assert('detailBody exists and is populated', detailBody && detailBody.innerHTML.length > 50);

        // Check Transparency Grade emphasis
        assert('Transparency Grade title is emphasized', detailBody.textContent.includes('Civic Transparency Grade') || detailBody.textContent.includes('Transparency Grade'), detailBody.textContent.slice(0, 200));
        assert('Transparency Grade badge exists with high contrast styling', detailBody.innerHTML.includes('#42be65') && detailBody.innerHTML.includes('text-[22px]'));
        assert('Transparency Grade shows audit verification', detailBody.textContent.includes('Audited') || detailBody.textContent.includes('Statutory Accountability'));

        // Check no nested boxes (no bg-[#101420] or bg-[#101626] or bg-[#0b101c] or bg-[#0c121e])
        const hasOldNestedBoxes = detailBody.innerHTML.includes('bg-[#101420]') || detailBody.innerHTML.includes('bg-[#101626]') || detailBody.innerHTML.includes('bg-[#0b101c]') || detailBody.innerHTML.includes('bg-[#0c121e]');
        assert('Dossier has NO nested boxes (flat divider rows)', !hasOldNestedBoxes, detailBody.innerHTML.slice(0, 300));

        // =========================================================================
        // 2. PLAN VISIT IN CHAT EXPERIENCE
        // =========================================================================
        assert('window.atlasPlanVisit is defined', typeof window.atlasPlanVisit === 'function');
        assert('Floating card Direct Plan button exists', !!document.getElementById('floatingCardDirectPlanBtn'));
        assert('Floating card Direct Plan button says Plan Visit in Chat', document.getElementById('floatingCardDirectPlanBtn').textContent.includes('Plan Visit in Chat') || document.getElementById('floatingCardDirectPlanBtn').textContent.includes('Plan Visit'));

        // Test calling atlasPlanVisit
        window.atlasPlanVisit(testInst.name);
        await new Promise(r => setTimeout(r, 400));

        let msgs = document.querySelectorAll('.curator-message-wrap');
        let lastMsg = msgs[msgs.length - 1];
        assert('Plan Visit creates conversational visitor guide in chat', lastMsg && (lastMsg.textContent.includes('Visitor Itinerary') || lastMsg.textContent.includes('Opening Hours') || lastMsg.textContent.includes('Visitor Guide')), lastMsg ? lastMsg.textContent : '');
        assert('Plan Visit chat briefing includes transit directions', lastMsg && (lastMsg.textContent.includes('Transit') || lastMsg.textContent.includes('Getting There')), lastMsg ? lastMsg.textContent : '');
        assert('Plan Visit chat briefing includes admission details', lastMsg && (lastMsg.textContent.includes('Admission') || lastMsg.textContent.includes('Tickets')), lastMsg ? lastMsg.textContent : '');

        // =========================================================================
        // 3. RESEARCH & FEEDBACK INPUT MODAL & VERIFICATION QUEUE
        // =========================================================================
        const feedbackModal = document.getElementById('researchFeedbackModal');
        assert('researchFeedbackModal exists in DOM', !!feedbackModal);
        assert('chatContributeBtn exists in input dock', !!document.getElementById('chatContributeBtn'));
        assert('workMenuFeedbackBtn exists in plus dropdown menu', !!document.getElementById('workMenuFeedbackBtn'));

        // Open modal
        window.openResearchFeedbackModal('Auto Italia South East', 'London');
        assert('openResearchFeedbackModal opens modal', !feedbackModal.classList.contains('hidden'));
        assert('Space name input is pre-populated', document.getElementById('rfSpaceName').value === 'Auto Italia South East');
        assert('City input is pre-populated', document.getElementById('rfCity').value === 'London');

        // Submit form
        document.getElementById('rfDetails').value = 'Artist-run space focused on non-commercial experimental commissions and public research.';
        document.getElementById('rfSourceUrl').value = 'https://autoitaliasoutheast.org';
        document.getElementById('rfContributor').value = 'TestCurator';

        const submitEvent = new Event('submit', { cancelable: true });
        document.getElementById('researchFeedbackForm').dispatchEvent(submitEvent);

        assert('Submitting form closes modal', feedbackModal.classList.contains('hidden'));

        // Check localStorage storage
        const savedSubmissions = window.getCommunityResearchSubmissions();
        assert('Submission is stored in localStorage queue', savedSubmissions.length > 0);
        assert('Saved submission has correct space name', savedSubmissions[0].spaceName === 'Auto Italia South East');
        assert('Saved submission has pending_verification status', savedSubmissions[0].status === 'pending_verification');

        // Check confirmation in chat
        await new Promise(r => setTimeout(r, 200));
        msgs = document.querySelectorAll('.curator-message-wrap');
        lastMsg = msgs[msgs.length - 1];
        assert('Curator confirms research contribution queued for verification', lastMsg && lastMsg.textContent.includes('Research Contribution Queued for Verification'), lastMsg ? lastMsg.textContent : '');
        assert('Confirmation includes audit ticket ID', lastMsg && lastMsg.textContent.includes('#RES-'), lastMsg ? lastMsg.textContent : '');

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
    temp_file = os.path.join(tempfile.gettempdir(), "test_feedback_transparency_planvisit_harness.html")
    with open(temp_file, "w", encoding="utf-8") as f:
        f.write(harness_html)

    chrome_bin = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

    print("--- RUNNING FEEDBACK, TRANSPARENCY & PLAN VISIT SUITE ---")
    cmd = [
        chrome_bin,
        "--headless=new",
        "--dump-dom",
        "--window-size=1280,800",
        "--virtual-time-budget=6000",
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
        print("\nALL FEEDBACK, TRANSPARENCY & PLAN VISIT TESTS PASSED!")
    return all_passed

if __name__ == "__main__":
    success = run_tests()
    if not success:
        exit(1)
