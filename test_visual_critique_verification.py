import subprocess
import json
import os
import tempfile
import sys
import re

def run_tests():
    print("--- RUNNING VISUAL CRITIQUE & ARTIST FEEDBACK TEST SUITE ---")
    index_path = "/Users/polinavasilyeva/.gemini/antigravity/scratch/sponsor-atlas/index.html"
    assert os.path.exists(index_path), "index.html must exist"
    with open(index_path, "r", encoding="utf-8") as f:
        html = f.read()

    # 1. Static HTML assertions
    assert 'id="globeVisualCritiqueBtn"' in html, "globeVisualCritiqueBtn missing in HTML"
    assert 'Visual Critique &amp; Artist Feedback' in html, "Visual Critique label missing in HTML"
    assert 'id="visualCritiqueSubBar"' in html, "visualCritiqueSubBar missing in HTML"
    assert 'id="floatingCardVisualCritiqueSection"' in html, "floatingCardVisualCritiqueSection missing in HTML"
    assert 'id="catFilterVisualCritiqueBtn"' in html, "catFilterVisualCritiqueBtn missing in HTML"
    assert 'data-topic="visual_critique"' in html, "data-topic='visual_critique' missing in HTML"
    print("[PASS] Static HTML assertions passed.")

    # 2. Browser DOM & Interactive assertions
    test_script = """
    <script>
    window.addEventListener('DOMContentLoaded', async () => {
      const results = [];
      const assert = (name, cond, details = '') => {
        results.push({ name, pass: !!cond, details });
        if (!cond) console.error('[FAIL]', name, details);
        else console.log('[PASS]', name);
      };

      try {
        // Test 1: Button existence and text
        const vcBtn = document.getElementById('globeVisualCritiqueBtn');
        assert('#globeVisualCritiqueBtn exists', !!vcBtn);
        assert('#globeVisualCritiqueBtn label includes Visual Critique', vcBtn && vcBtn.textContent.includes('Visual Critique'));

        // Test 2: Click Visual Critique Button
        if (vcBtn) vcBtn.click();
        const subBar = document.getElementById('visualCritiqueSubBar');
        assert('#visualCritiqueSubBar is visible after clicking Visual Critique', subBar && !subBar.classList.contains('hidden'));

        assert('selectedTierFilter has VISUAL_CRITIQUE', window.selectedTierFilter && window.selectedTierFilter.has('VISUAL_CRITIQUE'));
        assert('filteredList has >= 25 institutions with visual critiques', window.filteredList && window.filteredList.length >= 25, 'got ' + (window.filteredList ? window.filteredList.length : 'null'));

        // Test 3: Test sub-strategies
        const strats = [
          { id: 'direct_polling', match: 'MoMA', artist: 'Hans Haacke' },
          { id: 'parodic_museums', match: 'WIELS', artist: 'Marcel Broodthaers' },
          { id: 'environmental_satire', match: 'Crab Museum', artist: 'Crab Museum' },
          { id: 'physical_intervention', match: 'Orsay', artist: 'Deborah De Robertis' }
        ];

        for (const s of strats) {
          const pill = document.querySelector(`.vc-strat-pill[data-strategy="${s.id}"]`);
          assert(`Strategy pill ${s.id} exists`, !!pill);
          if (pill) {
            pill.click();
            const names = (window.filteredList || []).map(i => i.name).join(', ');
            assert(`Strategy ${s.id} filters list to match ${s.match}`, names.includes(s.match), `got names: ${names}`);

            // Find institution and test floating card
            const targetInst = (window.filteredList || []).find(i => i.name.includes(s.match));
            if (targetInst) {
              window.selectInstitution(targetInst, false);
              const cardSection = document.getElementById('floatingCardVisualCritiqueSection');
              assert(`Floating card shows visual critique section for ${s.match}`, cardSection && !cardSection.classList.contains('hidden'));
              
              const practiceEl = document.getElementById('floatingCardVcArtist');
              assert(`Floating card displays artist for ${s.match}`, practiceEl && practiceEl.textContent.includes(s.artist), `got: ${practiceEl ? practiceEl.textContent : ''}`);

              const imgEl = document.getElementById('floatingCardVcImg');
              assert(`Floating card has visual critique image for ${s.match}`, imgEl && imgEl.src && imgEl.src.includes('assets/visual_critique/'), `got src: ${imgEl ? imgEl.src : ''}`);
            }
          }
        }

        // Test 4: Academic Studies Topic Chip
        if (typeof window.openAcademicResearchModal === 'function') {
          window.openAcademicResearchModal('all');
          const chip = document.querySelector('.ar-topic-chip[data-topic="visual_critique"]');
          assert('Academic modal topic chip visual_critique exists', !!chip);
          if (chip) {
            chip.click();
            const list = document.getElementById('arPapersList');
            assert('Academic modal shows papers for visual critique', list && list.children.length >= 5, `got ${list ? list.children.length : 0} papers`);
          }
          window.closeAcademicResearchModal();
        }

        // Test 5: Curator Chat Query for Visual Critique
        if (typeof window.handleCuratorQuery === 'function') {
          await window.handleCuratorQuery('tell me about visual critique in museums');
          const chat = document.getElementById('curatorMessages');
          assert('Curator chat answers visual critique query', chat && chat.innerHTML.includes('Visual Critique &amp; Artist Feedback Corpus'));
          assert('Curator response mentions Consensus Study', chat && chat.innerHTML.includes('Consensus Study'));
          assert('Curator response mentions Direct Polling & Data', chat && chat.innerHTML.includes('Direct Polling &amp; Data'));
          assert('Curator response mentions Parodic Museums', chat && chat.innerHTML.includes('Parodic Museums'));
          assert('Curator response mentions Surrealist Reclassification', chat && chat.innerHTML.includes('Surrealist Reclassification'));
          assert('Curator response mentions Environmental Satire', chat && chat.innerHTML.includes('Environmental Satire'));
          assert('Curator response mentions Physical Intervention', chat && chat.innerHTML.includes('Physical Intervention'));
        }

      } catch (err) {
        assert('Unhandled error during test execution', false, err.toString());
      }

      const out = document.createElement('div');
      out.id = 'vc-verify-results';
      out.setAttribute('data-results', JSON.stringify(results));
      document.body.appendChild(out);
    });
    </script>
    """

    harness_html = html.replace("</body>", f"{test_script}</body>")
    temp_file = os.path.join(tempfile.gettempdir(), "test_vc_verify_harness.html")
    with open(temp_file, "w", encoding="utf-8") as f:
        f.write(harness_html)

    chrome_bin = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    cmd = [
        chrome_bin,
        "--headless=new",
        "--dump-dom",
        "--window-size=1280,800",
        "--virtual-time-budget=8000",
        f"file://{temp_file}"
    ]
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    dom = proc.stdout
    match = re.search(r'id="vc-verify-results"\s+data-results="([^"]+)"', dom)
    if not match:
        print("[FAIL] Test results element not found in DOM!")
        print("Stderr:", proc.stderr[:500])
        sys.exit(1)

    raw_results = match.group(1).replace("&quot;", '"')
    test_results = json.loads(raw_results)
    failed = [r for r in test_results if not r["pass"]]
    for r in test_results:
        status = "PASS" if r["pass"] else "FAIL"
        print(f"[{status}] {r['name']} {r['details']}")

    if failed:
        print(f"\n❌ {len(failed)} test(s) failed!")
        sys.exit(1)
    else:
        print(f"\n🎉 ALL {len(test_results)} VISUAL CRITIQUE & ARTIST FEEDBACK ASSERTIONS PASSED PERFECTLY!")

if __name__ == "__main__":
    run_tests()
