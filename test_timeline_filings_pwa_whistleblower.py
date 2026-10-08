#!/usr/bin/env python3
"""
Test Suite for:
1. Interactive Timeline of Cultural Boycotts & Divestment Victories
2. Statutory IRS Form 990 & Charity Accounts Explorer
3. Cryptographic Whistleblower Receipt Pipeline
4. Offline PWA Manifest & Service Worker
"""

import os
import sys
import re
import tempfile
import subprocess
import json

HTML_FILE = os.path.abspath("index.html")

def test_pwa_files():
    print(">>> 1. Testing PWA manifest.json and sw.js...")
    assert os.path.exists("manifest.json"), "manifest.json does not exist"
    with open("manifest.json", "r", encoding="utf-8") as f:
        manifest = json.load(f)
    assert manifest.get("name"), "manifest.json missing name"
    assert manifest.get("short_name"), "manifest.json missing short_name"
    assert manifest.get("start_url"), "manifest.json missing start_url"
    assert manifest.get("icons"), "manifest.json missing icons"
    print("  ✓ manifest.json is valid and contains standard PWA fields")

    assert os.path.exists("sw.js"), "sw.js does not exist"
    with open("sw.js", "r", encoding="utf-8") as f:
        sw_code = f.read()
    assert "addEventListener('install'" in sw_code, "sw.js missing install listener"
    assert "addEventListener('fetch'" in sw_code, "sw.js missing fetch listener"
    print("  ✓ sw.js exists with service worker lifecycle handlers")

def test_static_html_structure():
    print("\n>>> 2. Testing static HTML markup in index.html...")
    with open(HTML_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    # PWA link
    assert '<link rel="manifest" href="manifest.json">' in content, "Missing manifest.json link in <head>"

    # HUD Buttons
    assert 'id="hudTimelineBtn"' in content, "Missing #hudTimelineBtn in HUD"
    assert 'id="hudFilingsBtn"' in content, "Missing #hudFilingsBtn in HUD"
    print("  ✓ HUD buttons #hudTimelineBtn and #hudFilingsBtn verified")

    # Globe Pills
    assert 'id="globeTimelineBtn"' in content, "Missing #globeTimelineBtn in filter bar"
    assert 'id="globeFilingsBtn"' in content, "Missing #globeFilingsBtn in filter bar"
    print("  ✓ Globe filter pills #globeTimelineBtn and #globeFilingsBtn verified")

    # Modals
    assert 'id="resistanceTimelineModal"' in content, "Missing #resistanceTimelineModal"
    assert 'id="closeTimelineModalBtn"' in content, "Missing #closeTimelineModalBtn"
    assert 'id="timelineSearchInput"' in content, "Missing #timelineSearchInput"
    assert 'id="timelineEventsContainer"' in content, "Missing #timelineEventsContainer"

    assert 'id="statutoryFilingsModal"' in content, "Missing #statutoryFilingsModal"
    assert 'id="closeFilingsModalBtn"' in content, "Missing #closeFilingsModalBtn"
    assert 'id="filingInstitutionSelect"' in content, "Missing #filingInstitutionSelect"
    assert 'id="statutoryFilingsBody"' in content, "Missing #statutoryFilingsBody"
    print("  ✓ Modals #resistanceTimelineModal and #statutoryFilingsModal verified")

def test_browser_runtime():
    print("\n>>> 3. Testing in-browser runtime execution via headless Chrome...")

    test_script = """
    <script>
    window.addEventListener('load', async () => {
        const results = [];
        function assert(desc, passed, detail = '') {
            results.push({ desc, passed: Boolean(passed), detail: String(detail) });
            console.log((passed ? '✓ PASS: ' : '✗ FAIL: ') + desc + (detail ? ' (' + detail + ')' : ''));
        }

        try {
            window.scrapeWebForQuery = async () => null;
            window.queryAI = async () => null;

            // 1. Cultural Resistance Timeline Tests
            assert('CULTURAL_RESISTANCE_TIMELINE is an array', Array.isArray(window.CULTURAL_RESISTANCE_TIMELINE));
            assert('Timeline contains >= 15 milestones', window.CULTURAL_RESISTANCE_TIMELINE && window.CULTURAL_RESISTANCE_TIMELINE.length >= 15, window.CULTURAL_RESISTANCE_TIMELINE ? window.CULTURAL_RESISTANCE_TIMELINE.length : 0);

            const titles = (window.CULTURAL_RESISTANCE_TIMELINE || []).map(t => t.title);
            assert('Timeline includes Nan Goldin / P.A.I.N. Met die-in', titles.some(t => t.includes('Nan Goldin') || t.includes('P.A.I.N.')));
            assert('Timeline includes Liberate Tate victory', titles.some(t => t.includes('Tate') && t.includes('BP')));
            assert('Timeline includes Warren Kanders Whitney resignation', titles.some(t => t.includes('Kanders')));
            assert('Timeline includes Leon Black MoMA stepping down', titles.some(t => t.includes('Leon Black')));

            // Open Timeline Modal
            window.openResistanceTimelineModal();
            const timeModal = document.getElementById('resistanceTimelineModal');
            assert('resistanceTimelineModal is visible', timeModal && !timeModal.classList.contains('hidden'));

            const timeContainer = document.getElementById('timelineEventsContainer');
            assert('Timeline cards rendered in container', timeContainer && timeContainer.innerHTML.includes('Temple of Dendur'));

            // Search Filter in Timeline
            const timeInput = document.getElementById('timelineSearchInput');
            if (timeInput) {
                timeInput.value = 'Shell';
                timeInput.dispatchEvent(new Event('input'));
            }
            assert('Timeline search for "Shell" displays Van Gogh Shell victory', timeContainer && timeContainer.innerHTML.includes('Van Gogh Museum Drops Shell'));

            window.closeResistanceTimelineModal();
            assert('resistanceTimelineModal is hidden after close', timeModal && timeModal.classList.contains('hidden'));

            // 2. Statutory Filings & 990 Explorer Tests
            assert('INSTITUTIONAL_FILINGS_REGISTRY is an array', Array.isArray(window.INSTITUTIONAL_FILINGS_REGISTRY));
            assert('Registry contains >= 8 institutions', window.INSTITUTIONAL_FILINGS_REGISTRY && window.INSTITUTIONAL_FILINGS_REGISTRY.length >= 8);

            const momaFiling = window.INSTITUTIONAL_FILINGS_REGISTRY.find(f => f.id === 'moma');
            assert('MoMA Form 990 EIN documented (13-1628424)', momaFiling && momaFiling.ein === '13-1628424');
            assert('MoMA Schedule L conflicts documented', momaFiling && momaFiling.scheduleLConflicts.length >= 3);
            assert('MoMA Executive Compensation documented', momaFiling && momaFiling.directorComp.includes('Glenn Lowry'));

            window.openStatutoryFilingsModal('moma');
            const filingModal = document.getElementById('statutoryFilingsModal');
            assert('statutoryFilingsModal is visible', filingModal && !filingModal.classList.contains('hidden'));

            const filingBody = document.getElementById('statutoryFilingsBody');
            assert('Filing body displays MoMA budget and program ratio', filingBody && filingBody.innerHTML.includes('72.4%'));

            // Switch to Schedule L tab
            const schedLTab = document.getElementById('filingTabScheduleL');
            if (schedLTab) schedLTab.click();
            assert('Schedule L tab displays Apollo and BlackRock conflicts', filingBody && filingBody.innerHTML.includes('Apollo Global') && filingBody.innerHTML.includes('BlackRock'));

            // Switch to Executive Comp tab
            const compTab = document.getElementById('filingTabExecComp');
            if (compTab) compTab.click();
            assert('Exec Comp tab displays Director salary', filingBody && filingBody.innerHTML.includes('Glenn Lowry'));

            window.closeStatutoryFilingsModal();
            assert('statutoryFilingsModal is hidden after close', filingModal && filingModal.classList.contains('hidden'));

            // 3. Cryptographic Whistleblower Receipt Pipeline
            assert('generateWhistleblowerReceipt function exists', typeof window.generateWhistleblowerReceipt === 'function');
            const receipt = await window.generateWhistleblowerReceipt('Test non-public donor agreement disclosure');
            assert('Receipt has SHA-256 hash (64 hex characters)', receipt && receipt.hash && receipt.hash.length === 64, receipt ? receipt.hash : '');
            assert('Receipt code follows LEAK-XXXX-XXXX format', receipt && receipt.receipt && receipt.receipt.startsWith('LEAK-'), receipt ? receipt.receipt : '');

            // Test confidential intake modal submission
            window.openConfidentialIntakeModal();
            const confModal = document.getElementById('confidentialIntakeChatModal');
            assert('confidentialIntakeChatModal is open', confModal && !confModal.classList.contains('hidden'));

            const initialMsgCount = document.querySelectorAll('#confidentialChatBody > div').length;
            await window.handleConfidentialSubmission('Internal memo: undisclosed weapons sponsor at modern wing');
            await new Promise(r => setTimeout(r, 600));

            const confBody = document.getElementById('confidentialChatBody');
            assert('Whistleblower response rendered with Cryptographic Receipt badge', confBody && confBody.innerHTML.includes('Cryptographic Receipt'));
            assert('Whistleblower response displays SHA-256 fingerprint', confBody && confBody.innerHTML.includes('SHA-256 VERIFIED'));
            assert('Whistleblower response includes OpSec checklist', confBody && confBody.innerHTML.includes('OpSec &amp; Whistleblower Precautions') || confBody.innerHTML.includes('OpSec & Whistleblower Precautions'));

            window.closeConfidentialIntakeModal();
            assert('confidentialIntakeChatModal is closed', confModal && confModal.classList.contains('hidden'));

            // 4. Curator Chat Intent Routing
            const prevCount1 = document.querySelectorAll('.curator-message-wrap').length;
            await window.handleCuratorQuery('what is the divestment timeline and boycott victories?');
            for (let i = 0; i < 20; i++) {
                await new Promise(r => setTimeout(r, 100));
                if (document.querySelectorAll('.curator-message-wrap').length > prevCount1) break;
            }
            const chatBody = document.getElementById('curatorMessages');
            assert('Chat handles timeline query with Resistance Timeline card', chatBody && (chatBody.innerHTML.includes('Timeline of Cultural Boycotts') || chatBody.innerHTML.includes('Divestment Victories')));

            const prevCount2 = document.querySelectorAll('.curator-message-wrap').length;
            await window.handleCuratorQuery('show me IRS Form 990 and Schedule L disclosures');
            for (let i = 0; i < 20; i++) {
                await new Promise(r => setTimeout(r, 100));
                if (document.querySelectorAll('.curator-message-wrap').length > prevCount2) break;
            }
            assert('Chat handles 990 query with Statutory Filings card', chatBody && (chatBody.innerHTML.includes('Statutory Filings') || chatBody.innerHTML.includes('IRS Form 990 Explorer')));

        } catch (err) {
            assert('Execution Exception', false, err.stack || err.toString());
        }

        const out = document.createElement('div');
        out.id = 'suite4-test-results';
        out.setAttribute('data-results', JSON.stringify(results));
        document.body.appendChild(out);
    });
    </script>
    """

    with open(HTML_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    harness_html = content.replace("</body>", f"{test_script}</body>")
    temp_file = os.path.join(tempfile.gettempdir(), "test_suite4_harness.html")
    with open(temp_file, "w", encoding="utf-8") as f:
        f.write(harness_html)

    chrome_cmd = [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "--headless",
        "--disable-gpu",
        "--dump-dom",
        "--virtual-time-budget=12000",
        f"file://{temp_file}"
    ]

    try:
        proc = subprocess.run(chrome_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=25, check=True)
        dom = proc.stdout.decode("utf-8")
    except Exception as e:
        print(f"Failed to execute Chrome: {e}")
        sys.exit(1)
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)

    marker = 'id="suite4-test-results"'
    if marker not in dom:
        print("✗ FAIL: Test results marker not found in DOM output.")
        sys.exit(1)

    import html
    match = re.search(r'data-results="([^"]+)"', dom[dom.find(marker):dom.find(marker)+12000])
    if not match:
        print("✗ FAIL: Could not extract test results attribute.")
        sys.exit(1)

    results_json = html.unescape(match.group(1))
    results = json.loads(results_json)

    passed = 0
    failed = 0
    for r in results:
        if r["passed"]:
            passed += 1
            print(f"  ✓ PASS: {r['desc']}" + (f" ({r['detail']})" if r.get("detail") else ""))
        else:
            failed += 1
            print(f"  ✗ FAIL: {r['desc']}" + (f" ({r['detail']})" if r.get("detail") else ""))

    print(f"\n>>> Total Browser Tests: {passed + failed} | Passed: {passed} | Failed: {failed}")
    if failed > 0:
        sys.exit(1)

if __name__ == "__main__":
    test_pwa_files()
    test_static_html_structure()
    test_browser_runtime()
    print("\n🎉 ALL TIMELINE, 990 FILINGS, CRYPTOGRAPHIC WHISTLEBLOWER, AND PWA TESTS PASSED!")
