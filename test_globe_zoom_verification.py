import subprocess
import json
import os
import tempfile
import sys
import re

def run_tests():
    print("--- RUNNING GLOBE ZOOM & NAVIGATION VERIFICATION SUITE ---")
    index_path = "/Users/polinavasilyeva/.gemini/antigravity/scratch/sponsor-atlas/index.html"
    assert os.path.exists(index_path), "index.html must exist"
    with open(index_path, "r", encoding="utf-8") as f:
        html = f.read()

    # 1. Static HTML assertions
    assert 'id="globeCanvas"' in html, "globeCanvas missing in HTML"
    assert 'id="zoomInBtn"' in html, "zoomInBtn missing in HTML"
    assert 'id="zoomOutBtn"' in html, "zoomOutBtn missing in HTML"
    assert 'isCityZoom' not in html, "isCityZoom legacy code should be completely removed"
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
        const canvas = document.getElementById('globeCanvas');
        assert('globeCanvas exists', !!canvas);

        // Initial state checks
        assert('isCityStreetViewActive initially false', window.getIsCityStreetViewActive() === false);
        assert('baseRadius is positive number', typeof window.getBaseRadius() === 'number' && window.getBaseRadius() > 0);

        const initialRadius = window.getTargetRadius();

        // Test 1: Wheel zoom in
        const wheelEvent = new WheelEvent('wheel', {
          deltaY: -100,
          clientX: 400,
          clientY: 300,
          bubbles: true,
          cancelable: true
        });
        canvas.dispatchEvent(wheelEvent);

        const afterWheelRadius = window.getTargetRadius();
        assert('Wheel zoom increases targetRadius', afterWheelRadius > initialRadius, 'initial: ' + initialRadius + ', new: ' + afterWheelRadius);
        assert('Wheel zoom does NOT hijack into street view', window.getIsCityStreetViewActive() === false);

        for (let i = 0; i < 5; i++) {
          canvas.dispatchEvent(new WheelEvent('wheel', { deltaY: -500, bubbles: true, cancelable: true }));
        }
        const maxRadius = window.getMaxRadius();
        assert('Max radius is clamped to 25x baseRadius', Math.abs(maxRadius - window.getBaseRadius() * 25.0) < 0.01, 'got ' + maxRadius);
        assert('Deep zoom stays <= maxRadius', window.getTargetRadius() <= maxRadius + 0.1, 'targetRadius: ' + window.getTargetRadius());
        assert('Deep zoom does NOT trigger street view', window.getIsCityStreetViewActive() === false);

        // Test 3: HUD Zoom Buttons
        const zoomInBtn = document.getElementById('zoomInBtn');
        const zoomOutBtn = document.getElementById('zoomOutBtn');
        assert('zoomInBtn exists', !!zoomInBtn);
        assert('zoomOutBtn exists', !!zoomOutBtn);

        // Reset radius to baseRadius
        window.setTargetRadius(window.getBaseRadius());
        const rBeforeBtn = window.getTargetRadius();
        zoomInBtn.click();
        assert('zoomInBtn increases targetRadius', window.getTargetRadius() > rBeforeBtn, 'before: ' + rBeforeBtn + ', after: ' + window.getTargetRadius());

        zoomOutBtn.click();
        assert('zoomOutBtn decreases targetRadius', window.getTargetRadius() < rBeforeBtn * 1.35);

        // Test 4: Institution Click on Globe does NOT switch to street view
        const testInst = window.ALL_INSTITUTIONS.find(i => i.name.includes('Chisenhale') || i.city === 'London');
        assert('testInst exists', !!testInst);
        if (testInst) {
          window.selectInstitution(testInst, false);
          assert('selectedInstitution is set', window.getSelectedInstitution() && window.getSelectedInstitution().name === testInst.name);
          assert('Institution click does NOT switch to street view', window.getIsCityStreetViewActive() === false);
          const card = document.getElementById('floatingCard');
          assert('Floating card is shown', card && !card.classList.contains('hidden'));
          const cardTitle = document.getElementById('floatingCardTitle');
          assert('Floating card title matches', cardTitle && cardTitle.textContent === testInst.name);
        }

      } catch (err) {
        assert('Unhandled error during test execution', false, err.toString());
      }

      const out = document.createElement('div');
      out.id = 'zoom-verify-results';
      out.setAttribute('data-results', JSON.stringify(results));
      document.body.appendChild(out);
    });
    </script>
    """

    harness_html = html.replace('</body>', f'{test_script}</body>')
    temp_file = os.path.join(tempfile.gettempdir(), 'test_zoom_harness.html')
    with open(temp_file, 'w', encoding='utf-8') as f:
        f.write(harness_html)

    chrome_bin = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
    cmd = [
        chrome_bin,
        '--headless=new',
        '--dump-dom',
        f'file://{temp_file}'
    ]
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=20)
    dom = proc.stdout
    match = re.search(r'id="zoom-verify-results"\s+data-results="([^"]+)"', dom)
    if not match:
        print('[FAIL] Test results element not found in DOM!')
        print('Stderr:', proc.stderr[:500])
        sys.exit(1)

    raw_results = match.group(1).replace('&quot;', '"')
    test_results = json.loads(raw_results)
    failed = [r for r in test_results if not r['pass']]
    for r in test_results:
        status = 'PASS' if r['pass'] else 'FAIL'
        print(f"[{status}] {r['name']} {r['details']}")

    if failed:
        print(f"\n❌ {len(failed)} test(s) failed!")
        sys.exit(1)
    else:
        print(f"\n🎉 ALL {len(test_results)} GLOBE ZOOM ASSERTIONS PASSED PERFECTLY!")

if __name__ == '__main__':
    run_tests()
