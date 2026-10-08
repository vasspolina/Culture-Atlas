#!/usr/bin/env python3
"""
Test Suite for Institutional Trustee & Board Conflict Network
Verifies:
1. Static HTML structure:
   - #hudTrusteesBtn in bottom HUD controls bar
   - #globeBoardConflictsBtn in multi-row filter bar
   - #trusteeConflictNetworkModal, #trusteeNetworkCanvas, #trusteeInspectorPanel
   - #trusteeSearchInput, #trusteeInterlocksOnly, #trusteeResetGraphBtn, zoom controls, and sector pills
2. In-browser runtime execution:
   - BOARD_CONFLICT_NODES integrity (institutions & corporate entities)
   - BOARD_CONFLICT_EDGES integrity (documented interlocks & statutory filings)
   - Sackler dynasty 6-institution interlock mapping
   - Leon Black, Warren Kanders, Larry Fink, and BP forensic dossiers
   - openTrusteeConflictNetworkModal() and closeTrusteeConflictNetworkModal()
   - selectTrusteeGraphNode() inspector panel updates with harms, activist campaigns, and 990 filings
   - Sector filtering (defense, fossil, private_equity, pharma, banking, artwashing)
   - Interlocks-only toggle (>= 2 interlocks)
   - Live search filtering
   - Conversational Curator chat intent routing for board conflicts
"""

import os
import sys
import re
import tempfile
import subprocess
import json

HTML_FILE = os.path.abspath("index.html")

def test_static_html_structure():
    print(">>> Testing static HTML markup in index.html...")
    with open(HTML_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. HUD & Globe Filter Pills
    assert 'id="hudTrusteesBtn"' in content, "Missing #hudTrusteesBtn in bottom HUD control bar"
    assert 'id="globeBoardConflictsBtn"' in content, "Missing #globeBoardConflictsBtn in globe filter pills"
    print("  ✓ HUD button #hudTrusteesBtn and globe pill #globeBoardConflictsBtn verified")

    # 2. Trustee & Board Conflict Network Modal
    assert 'id="trusteeConflictNetworkModal"' in content, "Missing #trusteeConflictNetworkModal"
    assert 'id="closeTrusteeModalBtn"' in content, "Missing #closeTrusteeModalBtn"
    assert 'id="trusteeSearchInput"' in content, "Missing #trusteeSearchInput"
    assert 'id="trusteeInterlocksOnly"' in content, "Missing #trusteeInterlocksOnly"
    assert 'id="trusteeResetGraphBtn"' in content, "Missing #trusteeResetGraphBtn"
    assert 'id="trusteeZoomInBtn"' in content, "Missing #trusteeZoomInBtn"
    assert 'id="trusteeZoomOutBtn"' in content, "Missing #trusteeZoomOutBtn"
    assert 'id="trusteeNetworkCanvas"' in content, "Missing #trusteeNetworkCanvas"
    assert 'id="trusteeInspectorPanel"' in content, "Missing #trusteeInspectorPanel"
    assert 'id="trusteeNetworkTooltip"' in content, "Missing #trusteeNetworkTooltip"
    print("  ✓ Modal container, Canvas, and Inspector Panel elements verified")

    # 3. Sector filter buttons
    for sec in ["all", "defense", "fossil", "private_equity", "pharma", "banking", "artwashing"]:
        assert f'data-sector="{sec}"' in content, f"Missing sector pill data-sector='{sec}'"
    print("  ✓ Sector filter pills verified")

    # 4. Engine functions in script
    for fn in ["initTrusteeNetworkGraph", "openTrusteeConflictNetworkModal", "closeTrusteeConflictNetworkModal",
               "selectTrusteeGraphNode", "filterTrusteeGraph", "renderTrusteeInspectorUI",
               "renderTrusteeNetworkCanvas", "highlightConnectedInstitutionsOnMap"]:
        assert fn in content, f"Missing function {fn} in script"
    print("  ✓ Engine functions presence verified in script")

def test_browser_runtime():
    print("\n>>> Testing in-browser runtime execution via headless Chrome...")

    test_script = """
    <script>
    window.addEventListener('load', async () => {
        const results = [];
        function assert(desc, passed, detail = '') {
            results.push({ desc, passed: Boolean(passed), detail: String(detail) });
            console.log((passed ? '✓ PASS: ' : '✗ FAIL: ') + desc + (detail ? ' (' + detail + ')' : ''));
        }

        try {
            // Mock network calls to avoid virtual time budget deadlocks
            window.scrapeWebForQuery = async () => null;
            window.queryAI = async () => null;

            // 1. Dataset Integrity
            assert('BOARD_CONFLICT_NODES is an array', Array.isArray(window.BOARD_CONFLICT_NODES));
            assert('Has >= 30 documented nodes', window.BOARD_CONFLICT_NODES && window.BOARD_CONFLICT_NODES.length >= 30, window.BOARD_CONFLICT_NODES ? window.BOARD_CONFLICT_NODES.length : 0);
            assert('BOARD_CONFLICT_EDGES is an array', Array.isArray(window.BOARD_CONFLICT_EDGES));
            assert('Has >= 30 documented edges', window.BOARD_CONFLICT_EDGES && window.BOARD_CONFLICT_EDGES.length >= 30, window.BOARD_CONFLICT_EDGES ? window.BOARD_CONFLICT_EDGES.length : 0);

            // Key Institutions Check
            const nodeIds = (window.BOARD_CONFLICT_NODES || []).map(n => n.id);
            ['moma', 'whitney', 'the_met', 'guggenheim', 'tate', 'british_museum', 'louvre', 'pompidou', 'macba', 'van_gogh', 'basel_kunstmuseum'].forEach(id => {
                assert('Institution node exists: ' + id, nodeIds.includes(id));
            });

            // Key Trustees Check
            ['leon_black', 'warren_kanders', 'larry_fink', 'steven_tananbaum', 'glenn_dubin', 'sackler_family', 'ken_griffin', 'david_koch', 'bp', 'shell', 'totalenergies', 'maja_hoffmann'].forEach(id => {
                assert('Trustee / Corporation node exists: ' + id, nodeIds.includes(id));
            });

            // 2. Sackler Dynasty Interlock Forensics
            const sacklerNode = window.BOARD_CONFLICT_NODES.find(n => n.id === 'sackler_family');
            assert('Sackler node documented with OxyContin epidemic', sacklerNode && sacklerNode.org.includes('Purdue Pharma'));
            const sacklerEdges = window.BOARD_CONFLICT_EDGES.filter(e => e.source === 'sackler_family' || e.target === 'sackler_family');
            assert('Sackler dynasty connected to >= 6 institutions', sacklerEdges.length >= 6, sacklerEdges.length);
            const sacklerTargets = sacklerEdges.map(e => e.source === 'sackler_family' ? e.target : e.source);
            ['the_met', 'guggenheim', 'tate', 'louvre', 'british_museum', 'dia'].forEach(instId => {
                assert('Sackler edge connects to ' + instId, sacklerTargets.includes(instId));
            });

            // 3. Warren Kanders / Safariland Tear Gas Forensics
            const kandersNode = window.BOARD_CONFLICT_NODES.find(n => n.id === 'warren_kanders');
            assert('Kanders harms mention Safariland / tear gas', kandersNode && kandersNode.harms.some(h => h.toLowerCase().includes('tear gas')));
            const kandersEdges = window.BOARD_CONFLICT_EDGES.filter(e => e.source === 'warren_kanders');
            assert('Kanders connected to Whitney Museum', kandersEdges.some(e => e.target === 'whitney'));

            // 4. Leon Black / Apollo Global / Epstein Forensics
            const blackNode = window.BOARD_CONFLICT_NODES.find(n => n.id === 'leon_black');
            assert('Leon Black harms mention Jeffrey Epstein advisory fees', blackNode && blackNode.harms.some(h => h.includes('Epstein')));
            const blackEdges = window.BOARD_CONFLICT_EDGES.filter(e => e.source === 'leon_black');
            assert('Leon Black connected to MoMA (ousted) and Met', blackEdges.some(e => e.target === 'moma' && e.status === 'ousted'));

            // 5. Modal Lifecycle
            window.openTrusteeConflictNetworkModal();
            const modal = document.getElementById('trusteeConflictNetworkModal');
            assert('trusteeConflictNetworkModal opens', modal && !modal.classList.contains('hidden'));

            // 6. Inspector Panel Render on Node Selection
            window.selectTrusteeGraphNode('sackler_family');
            const inspector = document.getElementById('trusteeInspectorPanel');
            assert('Inspector displays Sackler Dynasty title', inspector && inspector.innerHTML.includes('Sackler Dynasty'));
            assert('Inspector displays P.A.I.N. activist campaign', inspector && inspector.innerHTML.includes('P.A.I.N.'));
            assert('Inspector displays statutory filings citation', inspector && inspector.innerHTML.includes('Settlement Protocols') || inspector.innerHTML.includes('Renaming Resolutions'));

            window.selectTrusteeGraphNode('warren_kanders');
            assert('Inspector displays Warren Kanders dossier', inspector && inspector.innerHTML.includes('Warren B. Kanders'));
            assert('Inspector displays 2019 Whitney Biennial boycott', inspector && inspector.innerHTML.includes('Whitney Biennial'));

            // 7. Sector Filter Execution
            const secPillDefense = document.querySelector('.trustee-sector-pill[data-sector="defense"]');
            if (secPillDefense) secPillDefense.click();
            const defenseKanders = window.BOARD_CONFLICT_NODES.find(n => n.id === 'warren_kanders');
            const fossilShell = window.BOARD_CONFLICT_NODES.find(n => n.id === 'shell');
            assert('Defense filter keeps Kanders visible', defenseKanders && defenseKanders.visible);
            assert('Defense filter hides Shell', fossilShell && !fossilShell.visible);

            // Reset Sector
            const secPillAll = document.querySelector('.trustee-sector-pill[data-sector="all"]');
            if (secPillAll) secPillAll.click();
            assert('All sectors resets Shell to visible', fossilShell && fossilShell.visible);

            // 8. Interlocks Only Filter
            const interlocksCheck = document.getElementById('trusteeInterlocksOnly');
            if (interlocksCheck) {
                interlocksCheck.checked = true;
                interlocksCheck.dispatchEvent(new Event('change'));
            }
            const dubinNode = window.BOARD_CONFLICT_NODES.find(n => n.id === 'glenn_dubin');
            assert('Interlocks-only keeps Sackler visible (degree 6)', sacklerNode && sacklerNode.visible);
            assert('Interlocks-only hides Dubin (degree 1)', dubinNode && !dubinNode.visible);

            if (interlocksCheck) {
                interlocksCheck.checked = false;
                interlocksCheck.dispatchEvent(new Event('change'));
            }

            // 9. Search Filtering
            const searchInput = document.getElementById('trusteeSearchInput');
            if (searchInput) {
                searchInput.value = 'BlackRock';
                searchInput.dispatchEvent(new Event('input'));
            }
            const finkNode = window.BOARD_CONFLICT_NODES.find(n => n.id === 'larry_fink');
            assert('Search "BlackRock" keeps Larry Fink visible', finkNode && finkNode.visible);
            assert('Search "BlackRock" hides Warren Kanders', kandersNode && !kandersNode.visible);

            if (searchInput) {
                searchInput.value = '';
                searchInput.dispatchEvent(new Event('input'));
            }

            // Close Modal
            window.closeTrusteeConflictNetworkModal();
            assert('trusteeConflictNetworkModal closes', modal && modal.classList.contains('hidden'));

            // 10. Curator Chat Intent Routing for Board Conflicts
            const prevMsgCount = document.querySelectorAll('.curator-message-wrap').length;
            await window.handleCuratorQuery("who is on the board of MoMA and what are the conflicts?");
            for (let i = 0; i < 20; i++) {
                await new Promise(r => setTimeout(r, 100));
                if (document.querySelectorAll('.curator-message-wrap').length > prevMsgCount) break;
            }
            const chatBody = document.getElementById('curatorMessages');
            assert('Chat handles board conflict query with Relational Graph card', chatBody && (chatBody.innerHTML.includes('Board Conflict Network') || chatBody.innerHTML.includes('Relational Graph')));
            assert('Chat card includes 1-click button to launch graph', chatBody && chatBody.innerHTML.includes('openTrusteeConflictNetworkModal'));

        } catch (err) {
            assert('Execution Exception', false, err.stack || err.toString());
        }

        const out = document.createElement('div');
        out.id = 'board-network-test-results';
        out.setAttribute('data-results', JSON.stringify(results));
        document.body.appendChild(out);
    });
    </script>
    """

    with open(HTML_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    harness_html = content.replace("</body>", f"{test_script}</body>")
    temp_file = os.path.join(tempfile.gettempdir(), "test_board_network_harness.html")
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

    marker = 'id="board-network-test-results"'
    if marker not in dom:
        print("✗ FAIL: Test results marker not found in DOM output.")
        sys.exit(1)

    import html
    match = re.search(r'data-results="([^"]+)"', dom[dom.find(marker):dom.find(marker)+10000])
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
    test_static_html_structure()
    test_browser_runtime()
    print("\n🎉 ALL INSTITUTIONAL TRUSTEE & BOARD CONFLICT NETWORK TESTS PASSED!")
