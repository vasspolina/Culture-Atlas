#!/usr/bin/env python3
"""
Test Suite for Guardian Investigative Reporting Additions:
1. Milestone events in CULTURAL_RESISTANCE_TIMELINE (Science Museum Adani, Zabludowicz closure, British Museum BP renewal, ACE censorship U-turn, Baillie Gifford divestment).
2. Science Museum Group in INSTITUTIONAL_FILINGS_REGISTRY with Adani/Shell contract gagging clauses.
3. Trustee Board Conflict Network nodes & edges (George Osborne, Adani Group, Baillie Gifford, Poju Zabludowicz, Science Museum).
4. Chat handling of Guardian queries with interactive Guardian Investigative Cultural Dossier card.
"""

import os
import sys
import re
import tempfile
import subprocess
import json
import html

HTML_FILE = os.path.abspath("index.html")

def test_static_html():
    print(">>> 1. Testing static HTML markup in index.html...")
    with open(HTML_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    # Timeline milestones
    assert 'science_museum_adani_resignations' in content, "Missing science_museum_adani_resignations"
    assert 'zabludowicz_london_closure' in content, "Missing zabludowicz_london_closure"
    assert 'british_museum_bp_50m_backlash' in content, "Missing british_museum_bp_50m_backlash"
    assert 'ace_political_guidance_uturn' in content, "Missing ace_political_guidance_uturn"
    assert 'baillie_gifford_festival_boycott' in content, "Missing baillie_gifford_festival_boycott"
    print("  ✓ All 5 Guardian divestment milestones verified in HTML source")

    # Filings registry
    assert 'UK Charity Reg 1062085' in content, "Missing Science Museum Charity Commission reg"
    assert 'Clause 11 gagging' in content, "Missing Clause 11 gagging disclosure in filings"
    print("  ✓ Science Museum Group statutory filing verified in HTML source")

    # Board conflict network nodes
    assert 'george_osborne' in content, "Missing george_osborne in board conflict nodes"
    assert 'adani_group' in content, "Missing adani_group in board conflict nodes"
    assert 'baillie_gifford' in content, "Missing baillie_gifford in board conflict nodes"
    assert 'poju_zabludowicz' in content, "Missing poju_zabludowicz in board conflict nodes"
    print("  ✓ Guardian trustee and corporate conflict nodes verified in HTML source")


def test_browser_runtime():
    print("\n>>> 2. Testing in-browser runtime execution via headless Chrome...")
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
            assert('Timeline contains >= 22 milestones', window.CULTURAL_RESISTANCE_TIMELINE && window.CULTURAL_RESISTANCE_TIMELINE.length >= 22, window.CULTURAL_RESISTANCE_TIMELINE ? window.CULTURAL_RESISTANCE_TIMELINE.length : 0);

            const timelineIds = (window.CULTURAL_RESISTANCE_TIMELINE || []).map(t => t.id);
            assert('Timeline includes Science Museum Adani resignations', timelineIds.includes('science_museum_adani_resignations'));
            assert('Timeline includes Zabludowicz London closure', timelineIds.includes('zabludowicz_london_closure'));
            assert('Timeline includes British Museum BP £50M renewal', timelineIds.includes('british_museum_bp_50m_backlash'));
            assert('Timeline includes Arts Council England U-turn', timelineIds.includes('ace_political_guidance_uturn'));
            assert('Timeline includes Baillie Gifford festival boycott', timelineIds.includes('baillie_gifford_festival_boycott'));

            // 2. Statutory Filings Registry Tests
            assert('INSTITUTIONAL_FILINGS_REGISTRY is an array', Array.isArray(window.INSTITUTIONAL_FILINGS_REGISTRY));
            assert('Registry contains >= 10 institutions', window.INSTITUTIONAL_FILINGS_REGISTRY && window.INSTITUTIONAL_FILINGS_REGISTRY.length >= 10);

            const smgFiling = (window.INSTITUTIONAL_FILINGS_REGISTRY || []).find(f => f.id === 'science_museum');
            assert('Science Museum filing exists', Boolean(smgFiling));
            assert('Science Museum filing has UK Charity Reg 1062085', smgFiling && smgFiling.ein.includes('1062085'));
            assert('Science Museum filing documents Adani & Shell gagging conflicts', smgFiling && smgFiling.scheduleLConflicts.some(c => c.includes('Adani')) && smgFiling.scheduleLConflicts.some(c => c.includes('Clause 11')));

            // 3. Board Conflict Network Graph Tests
            assert('BOARD_CONFLICT_NODES is an array', Array.isArray(window.BOARD_CONFLICT_NODES));
            assert('BOARD_CONFLICT_NODES contains >= 38 nodes', window.BOARD_CONFLICT_NODES && window.BOARD_CONFLICT_NODES.length >= 38, window.BOARD_CONFLICT_NODES ? window.BOARD_CONFLICT_NODES.length : 0);

            const nodeIds = (window.BOARD_CONFLICT_NODES || []).map(n => n.id);
            assert('Network includes george_osborne', nodeIds.includes('george_osborne'));
            assert('Network includes adani_group', nodeIds.includes('adani_group'));
            assert('Network includes baillie_gifford', nodeIds.includes('baillie_gifford'));
            assert('Network includes poju_zabludowicz', nodeIds.includes('poju_zabludowicz'));
            assert('Network includes science_museum', nodeIds.includes('science_museum'));

            const edgeSources = (window.BOARD_CONFLICT_EDGES || []).map(e => e.source + '->' + e.target);
            assert('Edge connects george_osborne to british_museum', edgeSources.includes('george_osborne->british_museum'));
            assert('Edge connects adani_group to science_museum', edgeSources.includes('adani_group->science_museum'));
            assert('Edge connects shell to science_museum', edgeSources.includes('shell->science_museum'));

            // 4. Curator Query for Guardian Investigative Reporting
            const prevCount = document.querySelectorAll('.curator-message-wrap').length;
            await window.handleCuratorQuery("what has the Guardian reported on museum sponsorship?");
            for (let i = 0; i < 20; i++) {
                await new Promise(r => setTimeout(r, 100));
                if (document.querySelectorAll('.curator-message-wrap').length > prevCount) break;
            }

            const chatBody = document.getElementById('curatorMessages');
            assert('Chat handles Guardian query with Investigative Cultural Dossier card', chatBody && chatBody.innerHTML.includes('The Guardian Investigative Cultural Dossier'));
            assert('Dossier card mentions British Museum £50M BP Renewal', chatBody && chatBody.innerHTML.includes('British Museum £50M BP Renewal'));
            assert('Dossier card mentions George Osborne', chatBody && chatBody.innerHTML.includes('George Osborne'));
            assert('Dossier card mentions Science Museum Adani / Shell gagging clauses', chatBody && chatBody.innerHTML.includes('Science Museum &amp; Adani / Shell') && chatBody.innerHTML.includes('Gagging Clauses'));
            assert('Dossier card mentions Baillie Gifford Literary Boycotts', chatBody && chatBody.innerHTML.includes('Baillie Gifford Literary Boycotts'));
            assert('Dossier card mentions Zabludowicz Gallery London Closure', chatBody && chatBody.innerHTML.includes('Zabludowicz Gallery London Closure'));

        } catch (err) {
            assert('Execution Exception', false, err.stack || err.toString());
        }

        const out = document.createElement('div');
        out.id = 'guardian-test-results';
        out.setAttribute('data-results', JSON.stringify(results));
        document.body.appendChild(out);
    });
    </script>
    """

    with open(HTML_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    harness_html = content.replace("</body>", f"{test_script}</body>")
    temp_file = os.path.join(tempfile.gettempdir(), "test_guardian_harness.html")
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

    marker = 'id="guardian-test-results"'
    if marker not in dom:
        print("✗ FAIL: Test results marker not found in DOM output.")
        sys.exit(1)

    match = re.search(r'data-results="([^"]+)"', dom[dom.find(marker):dom.find(marker)+14000])
    if not match:
        print("✗ FAIL: Could not extract test results attribute.")
        sys.exit(1)

    raw_json = html.unescape(match.group(1))
    test_results = json.loads(raw_json)

    passed_count = sum(1 for r in test_results if r['passed'])
    failed_count = sum(1 for r in test_results if not r['passed'])

    for r in test_results:
        mark = "✓ PASS:" if r['passed'] else "✗ FAIL:"
        detail = f" ({r['detail']})" if r.get('detail') else ""
        print(f"  {mark} {r['desc']}{detail}")

    print(f"\n>>> Total Browser Tests: {len(test_results)} | Passed: {passed_count} | Failed: {failed_count}")

    if failed_count > 0:
        print("\n❌ SOME TESTS FAILED.")
        sys.exit(1)
    else:
        print("\n🎉 ALL GUARDIAN INVESTIGATIVE REPORTING TESTS PASSED!")

if __name__ == '__main__':
    test_static_html()
    test_browser_runtime()
