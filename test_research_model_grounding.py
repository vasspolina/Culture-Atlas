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
        // 1. DATASET & CORPUS INTEGRITY
        // =========================================================================
        const arLen = window.ACADEMIC_RESEARCH ? window.ACADEMIC_RESEARCH.length : 0;
        assert('Academic studies loaded >= 100', arLen >= 100, `Found: ${arLen}`);

        // Verify key papers are in window.ACADEMIC_RESEARCH
        const yatesPaper = window.ACADEMIC_RESEARCH.find(p => (p.title || '').toLowerCase().includes('reputation laundering'));
        assert('Yates & Graham paper present in ACADEMIC_RESEARCH', !!yatesPaper, yatesPaper ? yatesPaper.title : 'Not found');

        const sharpPaper = window.ACADEMIC_RESEARCH.find(p => (p.title || '').toLowerCase().includes('spirit sings'));
        assert('Sharp Spirit Sings paper present in ACADEMIC_RESEARCH', !!sharpPaper, sharpPaper ? sharpPaper.title : 'Not found');

        const velthuisPaper = window.ACADEMIC_RESEARCH.find(p => (p.title || '').toLowerCase().includes('fragility of cultural philanthropy'));
        assert('Velthuis & Gera fragility paper present in ACADEMIC_RESEARCH', !!velthuisPaper, velthuisPaper ? velthuisPaper.title : 'Not found');

        const silvaPaper = window.ACADEMIC_RESEARCH.find(p => (p.title || '').toLowerCase().includes('tax incentives in brazilian'));
        assert('Silva Brazilian tax incentives paper present in ACADEMIC_RESEARCH', !!silvaPaper, silvaPaper ? silvaPaper.title : 'Not found');

        const chenPaper = window.ACADEMIC_RESEARCH.find(p => (p.title || '').toLowerCase().includes('identified donor effect'));
        assert('Chen & Gao identified donor effect paper present in ACADEMIC_RESEARCH', !!chenPaper, chenPaper ? chenPaper.title : 'Not found');

        const kugelPaper = window.ACADEMIC_RESEARCH.find(p => (p.title || '').toLowerCase().includes('voluntary nonprofit fraud'));
        assert('Kugel & Mercado voluntary fraud paper present in ACADEMIC_RESEARCH', !!kugelPaper, kugelPaper ? kugelPaper.title : 'Not found');

        const bergPaper = window.ACADEMIC_RESEARCH.find(p => (p.title || '').toLowerCase().includes('fredriksen'));
        assert('Berg & Larsen Fredriksen paper present in ACADEMIC_RESEARCH', !!bergPaper, bergPaper ? bergPaper.title : 'Not found');

        const parkPaper = window.ACADEMIC_RESEARCH.find(p => (p.title || '').toLowerCase().includes('donation of the century'));
        assert('Park & Kim donation of the century paper present in ACADEMIC_RESEARCH', !!parkPaper, parkPaper ? parkPaper.title : 'Not found');

        const prokupekPaper = window.ACADEMIC_RESEARCH.find(p => (p.title || '').toLowerCase().includes('czech republic'));
        assert('Prokupek Czech ethics paper present in ACADEMIC_RESEARCH', !!prokupekPaper, prokupekPaper ? prokupekPaper.title : 'Not found');

        // =========================================================================
        // 2. MODAL TOPIC CHIPS & FILTERING
        // =========================================================================
        const modal = document.getElementById('academicResearchModal');
        assert('Academic Research Modal exists', !!modal);

        const repChip = document.querySelector('.ar-topic-chip[data-topic="reputation"]');
        assert('Reputation & Provenance topic chip exists', !!repChip);

        const fragChip = document.querySelector('.ar-topic-chip[data-topic="fragility"]');
        assert('Private Museum Fragility topic chip exists', !!fragChip);

        const polChip = document.querySelector('.ar-topic-chip[data-topic="policy"]');
        assert('Tax Policy & Inequality topic chip exists', !!polChip);

        // Test reputation topic filter
        if (repChip && typeof window.renderAcademicStudies === 'function') {
          repChip.click();
          await new Promise(r => setTimeout(r, 100));
          const list = document.getElementById('arPapersList');
          assert('Reputation chip filters list', list && list.textContent.toLowerCase().includes('reputation laundering'));
        }

        // Test fragility topic filter
        if (fragChip && typeof window.renderAcademicStudies === 'function') {
          fragChip.click();
          await new Promise(r => setTimeout(r, 100));
          const list = document.getElementById('arPapersList');
          assert('Fragility chip filters list', list && list.textContent.toLowerCase().includes('fragility'));
        }

        // =========================================================================
        // 3. OFFLINE CURATOR GROUNDING TESTS
        // =========================================================================
        // Helper to get last curator message text
        function getLastCuratorMsg() {
          const msgs = document.querySelectorAll('.curator-message-wrap');
          return msgs.length > 0 ? msgs[msgs.length - 1].textContent : '';
        }

        // Test 1: Academic Research Corpus Overview
        await window.handleCuratorQuery('what academic research is in the model?');
        await new Promise(r => setTimeout(r, 500));
        let lastMsg = getLastCuratorMsg();
        assert('Curator responds to academic research overview inquiry', lastMsg.includes('Peer-Reviewed Academic Corpus') && lastMsg.includes('Empirical Studies'));
        assert('Curator overview mentions key pillars', lastMsg.includes('Sponsor Networks') && lastMsg.includes('Reputation Laundering') && lastMsg.includes('Private Museum Fragility'));

        // Test 2: Reputation Laundering in Antiquities
        await window.handleCuratorQuery('tell me about reputation laundering in antiquities collections');
        await new Promise(r => setTimeout(r, 500));
        lastMsg = getLastCuratorMsg();
        assert('Curator responds to reputation laundering inquiry', (lastMsg.includes('Yates & Graham') || lastMsg.includes('YATES & GRAHAM')) && lastMsg.includes('low-value antiquities'));

        // Test 3: The Spirit Sings & Shell Oil PR
        await window.handleCuratorQuery('what is the spirit sings exhibition controversy?');
        await new Promise(r => setTimeout(r, 500));
        lastMsg = getLastCuratorMsg();
        assert('Curator responds to Spirit Sings inquiry', lastMsg.includes('Glenbow Museum') && lastMsg.includes('Shell') && lastMsg.includes('Lubicon Lake Cree'));

        // Test 4: Fragility of Private Art Museums
        await window.handleCuratorQuery('why do private art museums close?');
        await new Promise(r => setTimeout(r, 500));
        lastMsg = getLastCuratorMsg();
        assert('Curator responds to private museum closure inquiry', (lastMsg.includes('Velthuis & Gera') || lastMsg.includes('VELTHUIS & GERA')) && lastMsg.includes('less than 10 years'));

        // Test 5: The Identified Donor Effect
        await window.handleCuratorQuery('explain the identified donor effect in museums');
        await new Promise(r => setTimeout(r, 500));
        lastMsg = getLastCuratorMsg();
        assert('Curator responds to identified donor effect inquiry', (lastMsg.includes('Chen & Gao') || lastMsg.includes('CHEN & GAO')) && lastMsg.includes('obligation'));

        // Test 6: Voluntary Fraud Disclosures & Backlash
        await window.handleCuratorQuery('how do donors respond to voluntary nonprofit fraud disclosures?');
        await new Promise(r => setTimeout(r, 500));
        lastMsg = getLastCuratorMsg();
        assert('Curator responds to fraud disclosure inquiry', (lastMsg.includes('Kugel & Mercado') || lastMsg.includes('KUGEL & MERCADO')) && lastMsg.includes('board of directors'));

        // Test 7: Brazilian Tax Incentives & Inequality
        await window.handleCuratorQuery('how do tax incentives in brazilian contemporary art create inequality?');
        await new Promise(r => setTimeout(r, 500));
        lastMsg = getLastCuratorMsg();
        assert('Curator responds to Brazilian tax incentives inquiry', lastMsg.includes('Sara de Andrade Silva') && lastMsg.includes('resource inequality'));

        // Test 8: Norwegian Public-Private Collaborations & Fredriksen
        await window.handleCuratorQuery('tell me about the fredriksen collaboration with the national museum in norway');
        await new Promise(r => setTimeout(r, 500));
        lastMsg = getLastCuratorMsg();
        assert('Curator responds to Fredriksen collaboration inquiry', (lastMsg.includes('Berg & Larsen') || lastMsg.includes('BERG & LARSEN')) && (lastMsg.includes('Fredriksen') || lastMsg.includes('FREDRIKSEN')));

        // Test 9: Samsung Collection Actor-Network Theory
        await window.handleCuratorQuery('how does actor-network theory explain the donation of the century in south korea?');
        await new Promise(r => setTimeout(r, 500));
        lastMsg = getLastCuratorMsg();
        assert('Curator responds to Samsung mega-donation inquiry', (lastMsg.includes('Park & Kim') || lastMsg.includes('PARK & KIM')) && lastMsg.includes('Samsung'));

        // Test 10: Czech Republic Museum Fundraising Ethics
        await window.handleCuratorQuery('what are the ethics of museum fundraising in the czech republic?');
        await new Promise(r => setTimeout(r, 500));
        lastMsg = getLastCuratorMsg();
        assert('Curator responds to Czech fundraising inquiry', (lastMsg.includes('Prokůpek') || lastMsg.includes('Prokupek') || lastMsg.includes('PROKŮPEK')) && lastMsg.includes('Czech Republic'));

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

    harness_html = html.replace("</body>", f"{test_script}\n</body>")
    
    temp_file = os.path.join(tempfile.gettempdir(), "test_research_model_grounding_harness.html")
    with open(temp_file, "w", encoding="utf-8") as tf:
        tf.write(harness_html)

    try:
        chrome_bin = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        cmd = [
            chrome_bin,
            "--headless=new",
            "--dump-dom",
            "--window-size=1280,800",
            "--virtual-time-budget=10000",
            f"file://{temp_file}"
        ]
        
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=30)
        marker = 'id="test-results-output" data-results="'
        if marker not in proc.stdout:
            print("ERROR: Test marker not found in output. Stderr:")
            print(proc.stderr[:1000])
            return False

        results = json.loads(html_lib.unescape(proc.stdout.split(marker)[1].split('"')[0]))
        print("--- RUNNING RESEARCH GROUNDING TEST SUITE ---")
        failed = 0
        for r in results:
            status = "[PASS]" if r["pass"] else "[FAIL]"
            if not r["pass"]:
                failed += 1
            extra = f" ({r['extra']})" if not r["pass"] and r.get("extra") else ""
            print(f"{status} {r['name']}{extra}")

        if failed > 0:
            print(f"\n{failed} TEST(S) FAILED!")
            return False
        else:
            print("\nALL RESEARCH GROUNDING TESTS PASSED!")
            return True

    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)

if __name__ == "__main__":
    success = run_tests()
    if not success:
        exit(1)
