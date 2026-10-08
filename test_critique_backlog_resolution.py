import os
import subprocess
import json
import tempfile
import html as html_lib

def run_tests():
    print("--- RUNNING CRITIQUE & SPECIFICITY TEST SUITE (6 ISSUES) ---")
    
    index_path = "/Users/polinavasilyeva/.gemini/antigravity/scratch/sponsor-atlas/index.html"
    with open(index_path, "r", encoding="utf-8") as f:
        html = f.read()

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
        const insts = window.ALL_INSTITUTIONS || [];
        assert('Catalog has at least 1000 institutions', insts.length >= 1000, `Found: ${insts.length}`);

        // ISSUE 1: Generic Highlights Elimination
        const boilerplateHls = [
          'Major historical/modern art collection.',
          'Rigorous contemporary commissions and non-commercial public programming.',
          'Permanent collection and special exhibitions at Dallas Museum of Art.',
          'Permanent collection and special exhibitions at MCA Denver.',
          'Permanent collection and special exhibitions at Portland Art Museum.'
        ];
        const genericHls = insts.filter(i => !i.highlight || boilerplateHls.includes(i.highlight) || i.highlight.startsWith('Signature collection and rotating'));
        assert('Zero generic or template highlights across catalog', genericHls.length === 0, `Found ${genericHls.length} generic`);

        const bern = insts.find(i => i.name.includes('Kunstmuseum Bern'));
        assert('Bern has specific Adolf Wolfli/Paul Klee highlight', bern && (bern.highlight.includes('Wölfli') || bern.highlight.includes('Paul Klee')), bern ? bern.highlight : 'Missing');

        const delawarr = insts.find(i => i.name.includes('De La Warr Pavilion'));
        assert('De La Warr has specific Mendelsohn & Chermayeff highlight', delawarr && (delawarr.highlight.includes('Mendelsohn') || delawarr.highlight.includes('Chermayeff')), delawarr ? delawarr.highlight : 'Missing');

        const bremen = insts.find(i => i.name.includes('Kunsthalle Bremen'));
        assert('Kunsthalle Bremen has specific Paula Modersohn-Becker / Cezanne highlight', bremen && (bremen.highlight.includes('Paula Modersohn-Becker') || bremen.highlight.includes('Bürgerverein') || bremen.highlight.includes('Cézanne')), bremen ? bremen.highlight : 'Missing');

        const dma = insts.find(i => i.name.includes('Dallas Museum of Art'));
        assert('Dallas Museum of Art has specific Edward Larrabee Barnes highlight', dma && dma.highlight.includes('Edward Larrabee Barnes'), dma ? dma.highlight : 'Missing');

        const proa = insts.find(i => i.name.includes('Fundación PROA'));
        assert('Fundacion PROA has specific La Boca / Riachuelo highlight', proa && (proa.highlight.includes('La Boca') || proa.highlight.includes('Riachuelo')), proa ? proa.highlight : 'Missing');

        // Check archives have zero remnants
        let archRemnants = 0;
        for (const i of insts) {
          const str = JSON.stringify(i.archives_and_collections || {});
          if (str.includes('Signature collection and rotating') || str.includes('Rigorous contemporary commissions and non-commercial public programming.')) {
            archRemnants++;
          }
        }
        assert('Archives collections have zero boilerplate remnants', archRemnants === 0, `Found ${archRemnants} remnants`);

        // ISSUE 2: Concrete Admission Categories
        const allowedPolicies = new Set([
          'Always Free Public Admission',
          'Free Permanent Collection / Ticketed Special Exhibitions (€12–16)',
          'Ticketed Exhibition Program (€12–18 / Concessions Available)',
          'Pay-What-You-Wish Civic Hours / Sliding Scale (€0–10)',
          'Subsidized Civic Admission (€6–10 / Free for Under-18s)',
          'Commercial Mega-Admission ($25–30+)'
        ]);
        const vaguePolicies = insts.filter(i => !allowedPolicies.has(i.admission_policy));
        assert('All institutions have crystal-clear admission policies (0 vague)', vaguePolicies.length === 0, `Found ${vaguePolicies.length} invalid: ${vaguePolicies.slice(0, 3).map(i => i.admission_policy).join(', ')}`);

        const emptyAdmDetails = insts.filter(i => !i.admission_details || i.admission_details.length < 15);
        assert('All institutions have detailed admission & concession pricing', emptyAdmDetails.length === 0, `Found ${emptyAdmDetails.length} missing`);

        // ISSUE 3: Governance Tiers Transparency & Why-Clean Rationale
        const noWhyClean = insts.filter(i => !i.governance_details || i.governance_details.length < 25);
        assert('All institutions have specific governance why-clean / why-flagged rationale', noWhyClean.length === 0, `Found ${noWhyClean.length} missing`);

        const noEthicalSafeguard = insts.filter(i => !i.ethical_safeguard || i.ethical_safeguard.length < 20);
        assert('All institutions have ethical safeguards documented', noEthicalSafeguard.length === 0, `Found ${noEthicalSafeguard.length} missing`);

        // ISSUE 4: Statutory Audit Dossier Links
        const missingAuditUrls = insts.filter(i => !i.audit_dossier_url || !i.audit_dossier_url.startsWith('http'));
        assert('100% of institutions link to statutory audit dossier (0 missing)', missingAuditUrls.length === 0, `Found ${missingAuditUrls.length} missing`);

        // Test UI elements for Audit Dossier
        const floatingAuditBtn = document.getElementById('floatingCardDirectAuditBtn');
        assert('Floating card has direct Audit Dossier button in DOM', !!floatingAuditBtn);

        // Select an institution and verify floating card & drawer links
        window.selectInstitution(delawarr);
        assert('Floating card Audit Dossier href is populated', floatingAuditBtn.href.includes('charitycommission') || floatingAuditBtn.href.startsWith('http'), floatingAuditBtn.href);

        window.openDossier(delawarr);
        const drawerBody = document.getElementById('detailBody');
        assert('Dossier drawer contains Audit Dossier button', drawerBody.innerHTML.includes('Audit Dossier ↗') || drawerBody.innerHTML.includes('Statutory Regulatory Filing Dossier'));

        // ISSUE 5: Standardized 7 Governance Categories
        const allowedGovTypes = new Set([
          'Artist-Run Collective & Non-Profit Kunsthalle',
          'Civic & Municipal Public Trust',
          'National / State Cultural Institution',
          'University & Academic Research Institute',
          'Endowed Independent Foundation',
          'Public-Civic Co-Governance Trust',
          'Private Commercial / Corporate Foundation'
        ]);
        const invalidGovTypes = insts.filter(i => !allowedGovTypes.has(i.governance_type));
        assert('All institutions map to the 7 standardized legal governance categories', invalidGovTypes.length === 0, `Found ${invalidGovTypes.length} invalid`);

        const govModal = document.getElementById('governanceMethodologyModal');
        assert('Governance Methodology Modal exists in DOM', !!govModal);
        assert('Governance Modal explains 7 Standardized Legal Governance Taxonomies', (govModal.innerText || govModal.innerHTML).includes('Standardized Legal Governance Taxonomy') && (govModal.innerText || govModal.innerHTML).includes('Artist-Run Collective'));

        // ISSUE 6: Realistic Varied Opening Hours
        const invalidHours = insts.filter(i => !i.opening_hours || i.opening_hours === 'Commercial hours' || i.opening_hours === 'See official site');
        assert('Zero empty or placeholder hours across catalog', invalidHours.length === 0, `Found ${invalidHours.length} invalid`);

        const distinctHours = new Set(insts.map(i => i.opening_hours));
        assert('Catalog has rich varied hours across typologies (>= 50 schedules)', distinctHours.size >= 50, `Found: ${distinctHours.size}`);

        // Curator check query verification with audit dossier link
        window.handleCuratorQuery('check it for me');
        await new Promise(r => setTimeout(r, 600));

        const msgs = document.querySelectorAll('.curator-message-wrap');
        const lastMsg = msgs[msgs.length - 1];
        const lastMsgText = lastMsg ? lastMsg.innerHTML : '';
        assert('Curator check query response contains clickable Audit Dossier button', lastMsgText.includes('Audit Dossier ↗') || lastMsgText.includes('Statutory Audit'));

      } catch (err) {
        assert('Execution Exception', false, err.stack || err.toString());
      }

      const out = document.createElement('div');
      out.id = 'critique-test-results';
      out.setAttribute('data-results', JSON.stringify(results));
      document.body.appendChild(out);
    });
    </script>
    """

    harness_html = html.replace("</body>", f"{test_script}</body>")
    temp_file = os.path.join(tempfile.gettempdir(), "test_critique_harness.html")
    with open(temp_file, "w", encoding="utf-8") as f:
        f.write(harness_html)

    chrome_bin = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    cmd = [
        chrome_bin,
        "--headless=new",
        "--dump-dom",
        "--window-size=1280,800",
        "--virtual-time-budget=5000",
        f"file://{temp_file}"
    ]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=60)
    stdout = res.stdout

    marker = 'id="critique-test-results" data-results="'
    if marker not in stdout:
        print("[FAIL] Test output marker not found in headless Chrome output!")
        exit(1)

    raw_json = stdout.split(marker)[1].split('"')[0]
    raw_json = html_lib.unescape(raw_json)
    results = json.loads(raw_json)

    fails = 0
    for r in results:
        status = "[PASS]" if r["pass"] else "[FAIL]"
        print(f"{status} {r['name']}")
        if not r["pass"]:
            print(f"       Details: {r.get('details', '')}")
            fails += 1

    if fails == 0:
        print("\nALL 6 CRITIQUE ISSUES SUCCESSFULLY RESOLVED & VERIFIED!")
    else:
        print(f"\n{fails} TEST(S) FAILED!")
        exit(1)

if __name__ == '__main__':
    run_tests()
