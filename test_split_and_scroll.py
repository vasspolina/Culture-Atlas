import os
import subprocess
import json
import tempfile

def run_tests():
    index_path = "/Users/polinavasilyeva/.gemini/antigravity/scratch/sponsor-atlas/index.html"
    assert os.path.exists(index_path), "index.html must exist"

    with open(index_path, "r", encoding="utf-8") as f:
        html = f.read()

    test_script = """
    <script>
    window.addEventListener('load', async () => {
      const results = [];
      function assert(name, condition, extra = '') {
        results.push({ name, pass: !!condition, extra });
      }

      try {
        const isDesktop = window.innerWidth >= 768;
        const main = document.getElementById('mainAppContainer');
        const globe = document.getElementById('globeViewport');
        const splitter = document.getElementById('globeSplitter');
        const workView = document.getElementById('workViewContainer');
        const scrollArea = document.getElementById('curatorScrollArea');
        const dock = document.getElementById('workBottomDock');
        const inputCard = document.getElementById('workInputCard');
        const messages = document.getElementById('curatorMessages');

        assert("Main container exists", !!main);
        assert("Globe viewport exists", !!globe);
        assert("Splitter exists", !!splitter);
        assert("Work view container exists", !!workView);
        assert("Curator scroll area exists", !!scrollArea);
        assert("Work bottom dock exists", !!dock);
        assert("Work input card inside dock", dock.contains(inputCard));

        const mainRect = main.getBoundingClientRect();
        const globeRect = globe.getBoundingClientRect();
        const workRect = workView.getBoundingClientRect();
        const dockRect = dock.getBoundingClientRect();

        if (isDesktop) {
          const mainStyle = window.getComputedStyle(main);
          assert("Desktop main container has flex-direction row", mainStyle.flexDirection === 'row', mainStyle.flexDirection);
          
          const globeRatio = globeRect.width / mainRect.width;
          const workRatio = workRect.width / mainRect.width;
          assert("Globe viewport width is ~50% (between 40% and 60%)", globeRatio >= 0.40 && globeRatio <= 0.60, `${(globeRatio*100).toFixed(1)}%`);
          assert("Work view width is ~50% (between 40% and 60%)", workRatio >= 0.40 && workRatio <= 0.60, `${(workRatio*100).toFixed(1)}%`);
          assert("Globe height fills main container height", Math.abs(globeRect.height - mainRect.height) < 10, `${globeRect.height} vs ${mainRect.height}`);
          assert("Work view height fills main container height", Math.abs(workRect.height - mainRect.height) < 10, `${workRect.height} vs ${mainRect.height}`);
        }

        // Test scrolling behavior with multiple messages
        for (let i = 1; i <= 20; i++) {
          appendUserMessage(`Test user message query #${i} exploring contemporary art spaces and sponsorship dossiers.`);
          appendCuratorMessage(`Test curator response #${i}: Detailed findings on institution #${i}, funding bodies, patron circles, and exhibition timelines.`);
        }

        // Scroll to bottom test
        if (typeof scrollChatToBottom === 'function') {
          scrollChatToBottom(false);
        }

        const scrollAreaAfter = document.getElementById('curatorScrollArea');
        const isScrollable = scrollAreaAfter.scrollHeight > scrollAreaAfter.clientHeight;
        assert("Curator scroll area is scrollable after 20 messages", isScrollable, `scrollHeight: ${scrollAreaAfter.scrollHeight}, clientHeight: ${scrollAreaAfter.clientHeight}`);
        assert("Curator scroll area scrolled down", scrollAreaAfter.scrollTop > 0, `scrollTop: ${scrollAreaAfter.scrollTop}`);

        // Verify dock remains pinned at bottom of workView
        const dockRectAfter = dock.getBoundingClientRect();
        const workRectAfter = workView.getBoundingClientRect();
        const dockAtBottom = Math.abs(dockRectAfter.bottom - workRectAfter.bottom) <= 2;
        assert("Bottom dock remains pinned to the bottom of workViewContainer", dockAtBottom, `dockBottom: ${dockRectAfter.bottom}, workBottom: ${workRectAfter.bottom}`);

      } catch (err) {
        results.push({ name: 'Exception caught', pass: false, extra: err.toString() });
      }

      const div = document.createElement('div');
      div.id = 'test-results-output';
      div.setAttribute('data-results', JSON.stringify(results));
      document.body.appendChild(div);
    });
    </script>
    """

    harness_html = html.replace("</body>", f"{test_script}</body>")
    temp_file = os.path.join(tempfile.gettempdir(), "test_split_scroll_harness.html")
    with open(temp_file, "w", encoding="utf-8") as f:
        f.write(harness_html)

    chrome_bin = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

    # 1. Desktop Test (1280x800)
    print("--- RUNNING DESKTOP (1280x800) SUITE ---")
    cmd_desktop = [
        chrome_bin,
        "--headless=new",
        "--dump-dom",
        "--window-size=1280,800",
        "--virtual-time-budget=6000",
        f"file://{temp_file}"
    ]
    proc = subprocess.run(cmd_desktop, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=60)
    marker = 'id="test-results-output" data-results="'
    if marker not in proc.stdout:
        print("ERROR: Test marker not found in desktop output. Stderr:")
        print(proc.stderr[:1000])
        return False

    import html as html_lib
    results_desktop = json.loads(html_lib.unescape(proc.stdout.split(marker)[1].split('"')[0]))
    all_passed = True
    for r in results_desktop:
        status = "PASS" if r['pass'] else "FAIL"
        if not r['pass']:
            all_passed = False
        extra = f" ({r['extra']})" if r.get('extra') else ""
        print(f"[{status}] {r['name']}{extra}")

    # 2. Mobile Test (375x667)
    print("\n--- RUNNING MOBILE (375x667) SUITE ---")
    cmd_mobile = [
        chrome_bin,
        "--headless=new",
        "--dump-dom",
        "--window-size=375,667",
        "--virtual-time-budget=6000",
        f"file://{temp_file}"
    ]
    proc_mobile = subprocess.run(cmd_mobile, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=60)
    if marker not in proc_mobile.stdout:
        print("ERROR: Test marker not found in mobile output. Stderr:")
        print(proc_mobile.stderr[:1000])
        return False

    results_mobile = json.loads(html_lib.unescape(proc_mobile.stdout.split(marker)[1].split('"')[0]))
    for r in results_mobile:
        status = "PASS" if r['pass'] else "FAIL"
        if not r['pass']:
            all_passed = False
        extra = f" ({r['extra']})" if r.get('extra') else ""
        print(f"[{status}] {r['name']}{extra}")

    return all_passed

if __name__ == "__main__":
    success = run_tests()
    if not success:
        exit(1)
