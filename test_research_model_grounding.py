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
    // Stub fetch completely so headless chrome does not hang on external network
    window.requestAnimationFrame = () => 1;
    window.cancelAnimationFrame = () => {};
    window.fetch = async (url, opts) => {
      return new Response("{}", { status: 200, headers: { 'Content-Type': 'application/json' } });
    };

    
const runAllTests = async () => {

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

        async function queryCurator(query) {
          await window.handleCuratorQuery(query);
          await new Promise(r => setTimeout(r, 600));
          const msgs = document.querySelectorAll('.curator-message-wrap');
          return msgs.length > 0 ? msgs[msgs.length - 1].textContent : '';
        }


        // Test 1: Academic Research Corpus Overview
        lastMsg = await queryCurator('what academic research is in the model?');
        assert('Curator responds to academic research overview inquiry', lastMsg.includes('Peer-Reviewed Academic Corpus') && lastMsg.includes('Empirical Studies'));
        assert('Curator overview mentions key pillars', lastMsg.includes('Sponsor Networks') && lastMsg.includes('Reputation Laundering') && lastMsg.includes('Private Museum Fragility'));

        // Test 2: Reputation Laundering in Antiquities
        lastMsg = await queryCurator('tell me about reputation laundering in antiquities collections');
        assert('Curator responds to reputation laundering inquiry', (lastMsg.includes('Yates & Graham') || lastMsg.includes('YATES & GRAHAM')) && lastMsg.includes('low-value antiquities'));

        // Test 3: The Spirit Sings & Shell Oil PR
        lastMsg = await queryCurator('what is the spirit sings exhibition controversy?');
        assert('Curator responds to Spirit Sings inquiry', lastMsg.includes('Glenbow Museum') && lastMsg.includes('Shell') && lastMsg.includes('Lubicon Lake Cree'));

        // Test 4: Fragility of Private Art Museums
        lastMsg = await queryCurator('why do private art museums close?');
        assert('Curator responds to private museum closure inquiry', (lastMsg.includes('Velthuis & Gera') || lastMsg.includes('VELTHUIS & GERA')) && lastMsg.includes('less than 10 years'));

        // Test 5: The Identified Donor Effect
        lastMsg = await queryCurator('explain the identified donor effect in museums');
        assert('Curator responds to identified donor effect inquiry', (lastMsg.includes('Chen & Gao') || lastMsg.includes('CHEN & GAO')) && lastMsg.includes('obligation'));

        // Test 6: Voluntary Fraud Disclosures & Backlash
        lastMsg = await queryCurator('how do donors respond to voluntary nonprofit fraud disclosures?');
        assert('Curator responds to fraud disclosure inquiry', (lastMsg.includes('Kugel & Mercado') || lastMsg.includes('KUGEL & MERCADO')) && lastMsg.includes('board of directors'));

        // Test 7: Brazilian Tax Incentives & Inequality
        lastMsg = await queryCurator('how do tax incentives in brazilian contemporary art create inequality?');
        assert('Curator responds to Brazilian tax incentives inquiry', lastMsg.includes('Sara de Andrade Silva') && lastMsg.includes('resource inequality'));

        // Test 8: Norwegian Public-Private Collaborations & Fredriksen
        lastMsg = await queryCurator('tell me about the fredriksen collaboration with the national museum in norway');
        assert('Curator responds to Fredriksen collaboration inquiry', (lastMsg.includes('Berg & Larsen') || lastMsg.includes('BERG & LARSEN')) && (lastMsg.includes('Fredriksen') || lastMsg.includes('FREDRIKSEN')));

        // Test 9: Samsung Collection Actor-Network Theory
        lastMsg = await queryCurator('how does actor-network theory explain the donation of the century in south korea?');
        assert('Curator responds to Samsung mega-donation inquiry', (lastMsg.includes('Park & Kim') || lastMsg.includes('PARK & KIM')) && lastMsg.includes('Samsung'));

        // Test 10: Czech Republic Museum Fundraising Ethics
        lastMsg = await queryCurator('what are the ethics of museum fundraising in the czech republic?');
        assert('Curator responds to Czech fundraising inquiry', (lastMsg.includes('Prokůpek') || lastMsg.includes('Prokupek') || lastMsg.includes('PROKŮPEK')) && lastMsg.includes('Czech Republic'));

        // Test 11: Special Autonomy & Competitive Funding (Cavalieri et al. 2025)
        lastMsg = await queryCurator('how does special autonomy shape museum behaviour and competitive funding?');
        assert('Curator responds to Cavalieri special autonomy inquiry', (lastMsg.includes('Cavalieri') || lastMsg.includes('CAVALIERI')) && lastMsg.includes('special autonomy'));

        // Test 12: Web-Based Accountability in National Museums (Dainelli et al. 2012)
        lastMsg = await queryCurator('explain national museum web accountability and stakeholder theory');
        assert('Curator responds to Dainelli national museum accountability inquiry', (lastMsg.includes('Dainelli') || lastMsg.includes('DAINELLI')) && lastMsg.includes('134 national museums'));

        // Test 13: Public Benefit or Private Gain (Keeney et al. 2025)
        lastMsg = await queryCurator('what does research say about public benefit or private gain in art museums?');
        assert('Curator responds to Keeney public benefit inquiry', (lastMsg.includes('Keeney') || lastMsg.includes('KEENEY')) && lastMsg.includes('Cultural Data Profile'));

        // Test 14: Board Composition & Web Transparency (Benito-Esteban et al. 2023)
        lastMsg = await queryCurator('how does having female board members affect web transparency in nonprofits?');
        assert('Curator responds to Benito-Esteban board gender diversity inquiry', (lastMsg.includes('Benito-Esteban') || lastMsg.includes('BENITO-ESTEBAN')) && lastMsg.includes('793 board directors'), 'GOT_TEXT: ' + (document.querySelectorAll('.curator-message-wrap').length ? document.querySelectorAll('.curator-message-wrap')[document.querySelectorAll('.curator-message-wrap').length - 1].innerText.replace(/\s+/g, ' ').slice(0, 150) : 'none'));

        // Test 15: Volunteer Commitment as an Insider Signal (Beck et al. 2024)
        lastMsg = await queryCurator('do donors value volunteer commitment as a signal of effectiveness?');
        assert('Curator responds to Beck volunteer commitment inquiry', (lastMsg.includes('Beck') || lastMsg.includes('BECK')) && lastMsg.includes('insiders'));

        // Test 16: Decision-Useful Financial Disclosures (Ghoorah et al. 2021, 2025)
        lastMsg = await queryCurator('how do decision-useful financial disclosures impact donor trust?');
        assert('Curator responds to Ghoorah financial disclosure inquiry', (lastMsg.includes('Ghoorah') || lastMsg.includes('GHOORAH')) && lastMsg.includes('donor trust'));

        // Test 17: Donor-Imposed Reporting Logics (Goncharenko 2020)
        lastMsg = await queryCurator('how do donor-imposed reporting practices reshape nonprofit identity?');
        assert('Curator responds to Goncharenko donor-imposed reporting inquiry', (lastMsg.includes('Goncharenko') || lastMsg.includes('GONCHARENKO')) && lastMsg.includes('institutional identities'));

        // Test 18: Swiss Museum Fundraising Governance (Betzler 2012, 2015)
        lastMsg = await queryCurator('what factors drive board governance and fundraising success in swiss museums?');
        assert('Curator responds to Betzler Swiss museum inquiry', (lastMsg.includes('Betzler') || lastMsg.includes('BETZLER')) && lastMsg.includes('98 Swiss museums'), 'GOT: ' + lastMsg.slice(0, 120));

        // Test 19: Corporate Governance in Nonprofits (Blevins et al. 2020)
        lastMsg = await queryCurator('how does corporate governance logic improve mission allocation in charities?');
        assert('Curator responds to Blevins corporate governance inquiry', (lastMsg.includes('Blevins') || lastMsg.includes('BLEVINS')) && lastMsg.includes('6,853'));

        // Test 20: Board of Trustees in China vs US (Dong Qin 2021)
        lastMsg = await queryCurator('compare museum board of trustees governance in china and the us');
        assert('Curator responds to Dong Qin board governance inquiry', (lastMsg.includes('Dong Qin') || lastMsg.includes('DONG QIN')) && lastMsg.includes('China'), 'GOT: ' + lastMsg.slice(0, 120));

        // Test 21: Slavoj Zizek & Cultural Capitalism
        lastMsg = await queryCurator('what does slavoj zizek write about cultural capitalism and philanthropy?');
        assert('Curator responds to Slavoj Zizek inquiry', (lastMsg.includes('Žižek') || lastMsg.includes('Zizek')) && lastMsg.includes('Cultural Capitalism'));

        // Test 22: Boris Groys & Art Power
        lastMsg = await queryCurator('tell me about boris groys and art power');
        assert('Curator responds to Boris Groys inquiry', (lastMsg.includes('Groys') || lastMsg.includes('GROYS')) && lastMsg.includes('Art Power'), 'GOT: ' + lastMsg.slice(0, 150));

        // Test 23: Yanis Varoufakis & Technofeudalism
        lastMsg = await queryCurator('how does yanis varoufakis explain technofeudalism and cloud capital in culture?');
        assert('Curator responds to Yanis Varoufakis inquiry', (lastMsg.includes('Varoufakis') || lastMsg.includes('VAROUFAKIS')) && lastMsg.includes('Technofeudalism'));

        // Test 24: Hito Steyerl & Duty-Free Art / Freeports
        lastMsg = await queryCurator('tell me about hito steyerl duty free art and freeports');
        assert('Curator responds to Hito Steyerl inquiry', (lastMsg.includes('Steyerl') || lastMsg.includes('STEYERL')) && lastMsg.includes('Duty Free Art'));

        // Test 25: Institutional Critique Artists (Rosler, Eichhorn, Rowland)
        lastMsg = await queryCurator('tell me about martha rosler maria eichhorn and cameron rowland criticizing institutions');
        assert('Curator responds to Institutional Critique Artists inquiry', lastMsg.includes('Eichhorn') && lastMsg.includes('Rosler'));

        // Test 26: Zero Claude References in UI labels
        const statusLabel = document.getElementById('topStatusLabel');
        const statusTxt = statusLabel ? statusLabel.textContent : '';
        assert('No Claude mentions in UI status', !statusTxt.toLowerCase().includes('claude'));

        // Test 27: Zero "Tier A" references in UI badges
        const bamBadge = document.getElementById('bamTierBadge');
        const bamBadgeTxt = bamBadge ? bamBadge.textContent : '';
        assert('No Tier A slop in bamTierBadge', !bamBadgeTxt.includes('Tier A'));

        // Test 28: Zero Wikipedia links in active institutions data
        let wikiFound = 0;
        if (window.ALL_INSTITUTIONS) {
          window.ALL_INSTITUTIONS.forEach(inst => {
            if (typeof inst.website === 'string' && inst.website.includes('wikipedia.org')) wikiFound++;
            if (typeof inst.visit_url === 'string' && inst.visit_url.includes('wikipedia.org')) wikiFound++;
            if (Array.isArray(inst.sources)) {
              inst.sources.forEach(s => {
                if (typeof s === 'string' && s.includes('wikipedia.org')) wikiFound++;
              });
            }
          });
        }
        assert('Zero Wikipedia URLs in ALL_INSTITUTIONS', wikiFound === 0, `Found: ${wikiFound}`);

        // Test 29: Separate Contribute Button & Confidential Intake Chat Modal
        const topContributeBtn = document.getElementById('topContributeBtn');
        const chatContributeBtn = document.getElementById('chatContributeBtn');
        const confModal = document.getElementById('confidentialIntakeChatModal');
        assert('Top Contribute button exists', !!topContributeBtn);
        assert('Chat Contribute button exists', !!chatContributeBtn);
        assert('Confidential Intake Chat Modal exists', !!confModal);

        // Test 30: Open Confidential Intake Modal and verify guidance
        window.openConfidentialIntakeModal();
        const confBody = document.getElementById('confidentialChatBody');
        const confTxt = confBody ? confBody.textContent : '';
        assert('Confidential intake guidance prompts for private internal info', confTxt.includes('private or internal information') && confTxt.includes('not publicly available'));

        // =========================================================================
        // 5. DEDICATED ARCHIVES & SPECIAL COLLECTIONS DIRECTORY
        // =========================================================================
        const archModal = document.getElementById('archivesDirectoryModal');
        const topArchBtn = document.getElementById('topArchivesBtn');
        const mobileArchBtn = document.getElementById('mobileArchivesBtn');
        const workMenuArchBtn = document.getElementById('workMenuArchivesBtn');
        const globeArchPill = document.querySelector('.globe-filter-pill[data-type="archives"]');

        assert('Archives Directory Modal exists', !!archModal);
        assert('Top Archives button exists', !!topArchBtn);
        assert('Mobile Archives button exists', !!mobileArchBtn);
        assert('Work Menu Archives button exists', !!workMenuArchBtn);
        assert('Globe Bar Archives filter pill exists', !!globeArchPill);

        // Open Archives Directory Modal
        window.openArchivesDirectoryModal('all');
        assert('Archives Modal opens and unhides', !archModal.classList.contains('hidden'));

        const archList = document.getElementById('archivesDirectoryList');
        const archCards = archList ? archList.querySelectorAll('.archive-card') : [];
        assert('Archives Directory renders catalog cards', archCards.length > 0, `Rendered: ${archCards.length}`);

        const firstCardText = archCards[0] ? archCards[0].textContent : '';
        assert('Archives Card contains reading room policy and holdings', firstCardText.includes('Reading Room Policy') && (firstCardText.includes('Dossiers') || firstCardText.includes('Ephemera') || firstCardText.includes('Audio') || firstCardText.includes('Holdings')));

        // Test search filter
        const sInput = document.getElementById('archivesSearchInput');
        if (sInput) {
          sInput.value = 'zines';
          sInput.dispatchEvent(new Event('input', { bubbles: true }));
        }
        const filteredArchCards = archList ? archList.querySelectorAll('.archive-card') : [];
        assert('Archives search filters by keyword', filteredArchCards.length > 0 && filteredArchCards.length <= archCards.length);

        // Test Curator Archives Query handler
        const archResMsg = await queryCurator('Show me the archives directory and special collections');
        assert('Curator responds to archives directory query', archResMsg.includes('Dedicated Archives Directory'));


      } catch (err) {
        assert('JavaScript Execution Exception', false, err.stack || err.toString());
      }

      const out = document.createElement('div');
      out.id = 'test-results-output';
      out.setAttribute('data-results', JSON.stringify(results));
      document.body.appendChild(out);
    };
    if (document.readyState === 'complete') { setTimeout(runAllTests, 100); } else { window.addEventListener('load', runAllTests); }
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
            "--virtual-time-budget=18000",
            f"file://{temp_file}"
        ]
        
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=60)
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
