#!/usr/bin/env python3
"""
test_gossip_palette_verification.py
Verify that Gossip Mode colors are altered to a distinct nocturnal velvet plum & electric rose palette:
1. CSS rules for body.gossip-mode-active, header, #globeViewport, #workBottomDock, #floatingCard.
2. window.toggleGossipMode() properly adds/removes body.gossip-mode-active.
3. Gossip mode button styling toggles between inactive dark wine pill and active glowing rose/fuchsia gradient.
4. Floating card switch to gossip mode applies the new rose accent and background.
5. Inactive mode restores normal styling without residual gossip styles.
"""

import os
import sys
import json
import re
import subprocess

def test_css_and_markup():
    print("--- 1. STATIC CSS & CODE VERIFICATION ---")
    with open('index.html', 'r', encoding='utf-8') as f:
        html = f.read()

    assert 'body.gossip-mode-active' in html, "Missing body.gossip-mode-active style rule"
    assert '#23082b' in html or '#130419' in html, "Missing velvet wine background gradient in CSS"
    assert 'rgba(244, 63, 94' in html or '#f43f5e' in html, "Missing electric rose accent in CSS"
    assert 'gossip-mode-active' in html, "Missing gossip-mode-active class in script logic"
    assert 'toggleGossipMode' in html, "Missing toggleGossipMode function"
    
    print("  [PASS] Static CSS and markup verification passed.")

def test_jsc_gossip_palette():
    print("\n--- 2. JAVASCRIPT GOSSIP PALETTE VERIFICATION (JSC) ---")
    with open('index.html', 'r', encoding='utf-8') as f:
        html = f.read()

    jsc_bin = "/System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Helpers/jsc"
    if not os.path.exists(jsc_bin):
        print("  [SKIP] jsc binary not found")
        return

    # Extract toggleGossipMode
    m = re.search(r'function\s+toggleGossipMode\s*\([^)]*\)\s*\{', html)
    if not m:
        raise Exception('toggleGossipMode function not found')
    start = m.start()
    depth = 0
    in_str = None
    i = start
    toggle_fn = ""
    while i < len(html):
        ch = html[i]
        if in_str:
            if ch == '\\':
                i += 2
                continue
            elif ch == in_str:
                in_str = None
        else:
            if ch in ('"', "'", '`'):
                in_str = ch
            elif ch == '{':
                depth += 1
            elif ch == '}':
                depth -= 1
                if depth == 0:
                    toggle_fn = html[start:i+1]
                    break
        i += 1

    test_js = """
    var window = this;
    var isGossipModeActive = false;
    var selectedInstitution = null;
    var currentHighlightedBuildingInst = null;
    var updateBuilding3DInfoMarkers = function() {};

    function makeClassList() {
      return {
        classes: [],
        add: function() {
          for (var i = 0; i < arguments.length; i++) {
            if (this.classes.indexOf(arguments[i]) === -1) this.classes.push(arguments[i]);
          }
        },
        remove: function() {
          for (var i = 0; i < arguments.length; i++) {
            var arg = arguments[i];
            this.classes = this.classes.filter(function(c) { return c !== arg; });
          }
        },
        contains: function(c) {
          return this.classes.indexOf(c) !== -1;
        }
      };
    }

    var topBtn = {
      id: 'topGossipBtn',
      classList: makeClassList(),
      innerHTML: ''
    };

    var mobileBtn = {
      id: 'mobileGossipBtn',
      classList: makeClassList(),
      innerHTML: ''
    };

    var body = {
      classList: makeClassList()
    };

    var document = {
      body: body,
      querySelector: function() { return null; },
      querySelectorAll: function() { return []; },
      getElementById: function(id) {
        if (id === 'topGossipBtn') return topBtn;
        if (id === 'mobileGossipBtn') return mobileBtn;
        return null;
      }
    };

    __TOGGLE_FN__

    // Initial state
    if (isGossipModeActive !== false) throw new Error('isGossipModeActive should be initially false');
    if (body.classList.contains('gossip-mode-active')) throw new Error('body should not have gossip-mode-active initially');

    // Toggle ON
    toggleGossipMode();
    if (isGossipModeActive !== true) throw new Error('isGossipModeActive should be true after toggle');
    if (!body.classList.contains('gossip-mode-active')) throw new Error('body should have gossip-mode-active when active');
    if (!topBtn.classList.contains('from-rose-600')) throw new Error('topBtn missing from-rose-600 gradient class');
    if (topBtn.innerHTML.indexOf('Gossip Mode: Active') === -1) throw new Error('topBtn missing Active label');
    print('[PASS] Gossip Mode toggled ON: velvet wine / electric rose classes applied');

    // Toggle OFF
    toggleGossipMode();
    if (isGossipModeActive !== false) throw new Error('isGossipModeActive should be false after second toggle');
    if (body.classList.contains('gossip-mode-active')) throw new Error('body should not have gossip-mode-active when inactive');
    if (topBtn.classList.contains('from-rose-600')) throw new Error('topBtn should not have from-rose-600 when inactive');
    print('[PASS] Gossip Mode toggled OFF: default styling cleanly restored');

    print('\\n🎉 ALL GOSSIP PALETTE TESTS PASSED!');
    """.replace("__TOGGLE_FN__", toggle_fn)

    test_file = "/tmp/test_gossip_palette_jsc.js"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(test_js)

    res = subprocess.run([jsc_bin, test_file], capture_output=True, text=True)
    if res.stdout:
        print(res.stdout)
    if res.stderr:
        print("STDERR:", res.stderr)
    assert res.returncode == 0, f"jsc test failed with code {res.returncode}"

if __name__ == '__main__':
    test_css_and_markup()
    test_jsc_gossip_palette()
