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
    // Stub fetch and animation frames so headless chrome does not hang on external network or loops
    window.requestAnimationFrame = () => 1;
    window.cancelAnimationFrame = () => {};
    window.fetch = async (url, opts) => {
      return new Response("{}", { status: 200, headers: { 'Content-Type': 'application/json' } });
    };

    window.addEventListener('DOMContentLoaded', async () => {
      const results = [];
      function assert(name, condition, extra = '') {
        results.push({ name, pass: !!condition, extra });
      }

      try {
        // =========================================================================
        // 1. DATA ENRICHMENT INTEGRITY (Archives, Collections, Building Architecture)
        // =========================================================================
        const all = window.ALL_INSTITUTIONS || [];
        assert('Total institutions >= 1000', all.length >= 1000, `Found: ${all.length}`);

        const enrichedBuildings = all.filter(i => i.building_architecture && i.building_architecture.footprint_sqm);
        assert('All institutions have building_architecture footprint', enrichedBuildings.length === all.length, `${enrichedBuildings.length}/${all.length}`);

        const enrichedArchives = all.filter(i => i.archives_and_collections && i.archives_and_collections.primary_holdings && i.archives_and_collections.primary_holdings.length > 0);
        assert('All institutions have archives_and_collections with primary holdings', enrichedArchives.length === all.length, `${enrichedArchives.length}/${all.length}`);

        const landmarkChisenhale = all.find(i => i.name.toLowerCase().includes('chisenhale'));
        assert('Landmark Chisenhale Gallery has curated building architecture', !!landmarkChisenhale && landmarkChisenhale.building_architecture.architectural_style.includes('Industrial Brick Warehouse'));
        assert('Landmark Chisenhale has curated archive holding', !!landmarkChisenhale && landmarkChisenhale.archives_and_collections.primary_holdings.some(h => h.category.includes('Artist Commission Dossiers')));

        const landmarkKitchen = all.find(i => i.name.toLowerCase() === 'the kitchen' || i.name.includes('The Kitchen'));
        assert('Landmark The Kitchen has curated video master archives', !!landmarkKitchen && landmarkKitchen.archives_and_collections.archive_name.includes('The Kitchen Video'));

        const landmarkArtistsSpace = all.find(i => i.name.toLowerCase().includes('artists space'));
        assert('Landmark Artists Space has Artists File slide registry', !!landmarkArtistsSpace && landmarkArtistsSpace.archives_and_collections.summary.includes('Pictures Generation'));

        // =========================================================================
        // 2. ZOOM TO BUILDING & VECTOR MAP INTEGRATION
        // =========================================================================
        assert('zoomToBuilding function is exposed on window', typeof window.zoomToBuilding === 'function');
        assert('openBuildingArchivesModal function is exposed on window', typeof window.openBuildingArchivesModal === 'function');

        // Test zoomToBuilding execution on a space
        const testInst = landmarkChisenhale || all[0];
        window.zoomToBuilding(testInst, false);

        const mapEl = document.getElementById('cityMapContainer');
        assert('cityMapContainer is unhidden after zoomToBuilding', !mapEl.classList.contains('hidden'));
        assert('cityMapContainer has map-zoomed-in class', mapEl.classList.contains('map-zoomed-in'));

        if (window.cityVectorMap) {
          const z = window.cityVectorMap.getZoom();
          assert('cityVectorMap zoomed to building level (zoom >= 17.0)', z >= 17.0, `Zoom: ${z}`);
          const p = window.cityVectorMap.getPitch();
          assert('cityVectorMap has 3D architectural pitch >= 50 deg', p >= 50, `Pitch: ${p}`);
        } else {
          assert('cityVectorMap initialized', false, 'cityVectorMap is null');
        }

        // =========================================================================
        // 3. IN-DEPTH BUILDING ARCHITECTURE & ARCHIVES INSPECTOR MODAL
        // =========================================================================
        const modal = document.getElementById('buildingArchivesModal');
        assert('buildingArchivesModal exists in DOM', !!modal);

        window.openBuildingArchivesModal(testInst);
        assert('buildingArchivesModal is visible after openBuildingArchivesModal()', !modal.classList.contains('hidden'));

        const bamTitle = document.getElementById('bamTitle');
        assert('Modal displays correct institution name', bamTitle && bamTitle.textContent.includes(testInst.name));

        const bamBody = document.getElementById('bamBody');
        assert('Modal body contains Architectural Profile section', bamBody && bamBody.textContent.includes('Architectural Footprint'));
        assert('Modal body displays Building Layout Wings', bamBody && bamBody.textContent.includes('Building Wings'));
        assert('Modal body displays In-Depth Archives', bamBody && bamBody.textContent.includes('Primary Research Holdings'));
        assert('Modal body displays Reading Room Policy', bamBody && bamBody.textContent.includes('Reading Room Policy'));
        assert('Modal body displays Ethical Provenance Integrity', bamBody && bamBody.textContent.includes('Ethical Provenance'));

        // Test modal closing
        const closeBtn = document.getElementById('closeBuildingArchivesBtn');
        if (closeBtn) closeBtn.click();
        assert('Modal hides on close button click', modal.classList.contains('hidden'));

        // =========================================================================
        // 4. DOSSIER IN-DEPTH ARCHIVES & ZOOM BUTTON
        // =========================================================================
        assert('openDossier is available', typeof window.atlasOpenDossier === 'function');
        window.atlasOpenDossier(testInst.name);

        const drawer = document.getElementById('detailDrawer');
        assert('Detail drawer is unhidden', !drawer.classList.contains('hidden'));

        const detailBody = document.getElementById('detailBody');
        assert('Dossier body contains Archives & Collections in Depth section', detailBody && detailBody.textContent.includes('Archives & Collections in Depth'));
        const hasZoomBtn = detailBody && (detailBody.innerHTML.includes('Zoom to Building') || detailBody.innerHTML.includes('zoomToBuilding'));
        assert('Dossier body contains Zoom to Building & Archives button', hasZoomBtn, detailBody ? detailBody.innerHTML.slice(0, 300) : 'null');
        assert('Dossier body contains Reading Room & Access Policy', detailBody && detailBody.textContent.includes('Reading Room & Access Policy'));
        assert('Dossier body contains Building Style and Footprint sqm', detailBody && detailBody.textContent.includes('BUILDING STYLE'));

        // =========================================================================
        // 5. CATALOG LIST CARDS "ZOOM TO BUILDING" ACTION
        // =========================================================================
        const listCards = document.querySelectorAll('.inst-card');
        assert('Institutions catalog rendered cards', listCards.length > 0);

        const zoomButtons = document.querySelectorAll('.card-zoom-building');
        assert('Catalog cards have Zoom to Building action buttons', zoomButtons.length > 0, `Found: ${zoomButtons.length}`);

        // =========================================================================
        // 6. CURATOR AI DOCENT ROUTING FOR ARCHIVES & SPECIAL COLLECTIONS
        // =========================================================================
        window.atlasAskCurator('What archives and collections does Chisenhale Gallery have?');
        await new Promise(r => setTimeout(r, 600));

        const curatorMsgs = Array.from(document.querySelectorAll('.curator-message-wrap'));
        const lastMsg = curatorMsgs[curatorMsgs.length - 1];
        assert('Curator responds to archives inquiry', !!lastMsg, `Total curator messages: ${curatorMsgs.length}`);
        if (lastMsg) {
          const msgText = lastMsg.textContent;
          assert('Curator response mentions Architectural Profile & Archival Repository', msgText.includes('Architectural Profile') || msgText.includes('Archival Repository') || msgText.includes('Chisenhale'), msgText.slice(0, 100));
          assert('Curator response provides Zoom to 3D Building button', lastMsg.innerHTML.includes('Zoom to 3D Building') || lastMsg.innerHTML.includes('zoomToBuilding'), lastMsg.innerHTML.slice(0, 100));
        }

      } catch (err) {
        results.push({ name: 'UNHANDLED_TEST_ERROR', pass: false, extra: err.toString() });
      }

      const outEl = document.createElement('div');
      outEl.id = 'test-results-output';
      outEl.setAttribute('data-results', JSON.stringify(results));
      document.body.appendChild(outEl);
    });
    </script>
    """

    injected_html = html.replace("</body>", f"{test_script}</body>")

    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False) as tf:
        tf.write(injected_html)
        temp_file = tf.name

    chrome_cmd = [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        "--dump-dom",
        "--virtual-time-budget=6000",
        f"file://{temp_file}"
    ]

    try:
        proc = subprocess.run(chrome_cmd, capture_output=True, text=True, timeout=120)
        dom = proc.stdout

        marker = 'id="test-results-output" data-results="'
        if marker not in dom:
            print("ERROR: Test results marker not found in DOM!")
            print("STDOUT preview:", dom[:500])
            print("STDERR preview:", proc.stderr[:500])
            return False

        json_str = dom.split(marker)[1].split('"')[0]
        decoded_json = html_lib.unescape(json_str)
        results = json.loads(decoded_json)

        print("--- RUNNING BUILDING ZOOM & IN-DEPTH ARCHIVES TEST SUITE ---")
        all_passed = True
        for r in results:
            status = "[PASS]" if r["pass"] else "[FAIL]"
            extra = f" ({r['extra']})" if r.get("extra") else ""
            print(f"{status} {r['name']}{extra}")
            if not r["pass"]:
                all_passed = False

        if all_passed:
            print("\nALL BUILDING ZOOM & IN-DEPTH ARCHIVES TESTS PASSED!")
            return True
        else:
            print("\nSOME TESTS FAILED.")
            return False

    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)

if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)
