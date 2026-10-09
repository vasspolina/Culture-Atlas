#!/usr/bin/env python3
"""
test_floor_click_no_info_popup.py
Verification test suite for:
"when i click on floor the info about museum pops back up"
1. Dismissing rooftop mast plate via closeBuildingMast() sets isBuildingMastDismissed = true.
2. Clicking floor levels via selectBfiFloor(idx) or 3D floor slabs updates floor highlight and room badges
   WITHOUT popping the museum info rooftop mast plate back up.
3. At building zoom (>= 16.0), 2D pins (.custom-inst-pin) and labels (.inst-pin-label) are hidden so
   no residual pins or text pills float over the 3D building floors.
4. Clicking on a pin or floor mesh at building zoom passes isFloorChange: true and prevents mast re-creation.
"""

import os
import sys
import json
import re
import subprocess

def test_static_html():
    print("--- 1. STATIC CODE & CLASS ASSERTIONS ---")
    with open("index.html", "r", encoding="utf-8") as f:
        html = f.read()

    assert "isBuildingMastDismissed" in html, "Missing isBuildingMastDismissed variable"
    assert "isBuildingFacadeDismissed" in html, "Missing isBuildingFacadeDismissed variable"
    assert "building-view-active" in html, "Missing building-view-active class in CSS/JS"
    assert "isFloorChange" in html, "Missing isFloorChange options handling"
    assert "highlightBuildingFootprint(inst, { isFloorChange: true })" in html or "isFloorChange: true" in html, "Missing isFloorChange call in selectBfiFloor"
    assert "#cityMapContainer.building-view-active .custom-inst-pin" in html, "Missing CSS rule for hiding custom-inst-pin in building-view-active"
    print("  [PASS] Static assertions confirmed.")

def test_jsc_floor_click_behavior():
    print("\n--- 2. FLOOR CLICK BEHAVIORAL VERIFICATION (JSC) ---")
    with open("index.html", "r", encoding="utf-8") as f:
        html = f.read()

    jsc_bin = "/System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Helpers/jsc"
    if not os.path.exists(jsc_bin):
        print("  [SKIP] jsc binary not found")
        return

    # Extract functions
    def extract_fn(name):
        idx = html.find(f'function {name}(')
        if idx == -1:
            raise Exception(f'Function {name} not found')
        paren_depth = 0
        i = idx + len(f'function {name}')
        body_start = -1
        while i < len(html):
            if html[i] == '(':
                paren_depth += 1
            elif html[i] == ')':
                paren_depth -= 1
                if paren_depth == 0:
                    body_start = html.find('{', i)
                    break
            i += 1
        depth = 1
        i = body_start + 1
        in_str = None
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
                        return html[idx:i+1]
            i += 1
        raise Exception(f'Unclosed function {name}')

    clear_fn = extract_fn('clearBuilding3DInfoMarkers')
    close_mast_fn = extract_fn('closeBuildingMast')
    close_facade_fn = extract_fn('closeBuildingFacade')
    dismiss_badge_fn = extract_fn('dismissBuildingRoomBadge')
    update_markers_fn = extract_fn('updateBuilding3DInfoMarkers')
    select_floor_fn = extract_fn('selectBfiFloor')

    test_js = f"""
    var window = this;
    var __popups = [];
    var __badges = [];
    var __mastPlates = [];
    var __facadeStacks = [];
    var building3DInfoMarkers = [];
    var currentBuildingMastMarker = null;
    var currentBuildingFacadeMarker = null;
    var isBuildingMastDismissed = false;
    var isBuildingFacadeDismissed = false;
    var isCityStreetViewActive = true;
    var isExploded3DMode = false;
    var currentBfiFloorIndex = 0;
    var selectedInstitution = null;
    var currentHighlightedBuildingInst = null;

    var escapeHtml = function(s) {{ return s ? String(s) : ''; }};
    var showBuildingFloorInspectorHud = function(inst) {{}};
    var highlightBuildingFootprint = function(inst, opts) {{
      currentHighlightedBuildingInst = inst;
      updateBuilding3DInfoMarkers(inst, opts);
    }};

    var maplibregl = {{
      Marker: function(opts) {{
        this.element = opts && opts.element;
        this.removed = false;
        this.setLngLat = function(ll) {{ this.lngLat = ll; return this; }};
        this.addTo = function(m) {{
          if (this.element && this.element.className) {{
            if (this.element.className.indexOf('building-3d-mast-plate') !== -1) __mastPlates.push(this.element);
            if (this.element.className.indexOf('building-3d-facade-stack') !== -1) __facadeStacks.push(this.element);
            if (this.element.className.indexOf('building-3d-room-badge') !== -1) __badges.push(this.element);
          }}
          return this;
        }};
        this.remove = function() {{
          this.removed = true;
          if (this.element && this.element.remove) this.element.remove();
        }};
      }}
    }};

    var cityVectorMap = {{
      getZoom: function() {{ return 18.6; }},
      flyTo: function() {{}}
    }};

    var document = {{
      body: {{
        classList: {{ add: function(){{}}, remove: function(){{}} }}
      }},
      createElement: function(tag) {{
        var el = {{
          tagName: tag,
          className: '',
          style: {{}},
          parentElement: null,
          children: [],
          appendChild: function(c) {{ c.parentElement = this; this.children.push(c); }},
          remove: function() {{
            this.removed = true;
            if (this.parentElement) {{
              this.parentElement.children = this.parentElement.children.filter(x => x !== this);
            }}
          }},
          closest: function(sel) {{
            var cur = this;
            while (cur) {{
              if (cur.className && cur.className.indexOf(sel.replace('.', '')) !== -1) return cur;
              cur = cur.parentElement;
            }}
            return null;
          }}
        }};
        return el;
      }},
      getElementById: function(id) {{ return null; }},
      querySelectorAll: function(sel) {{
        var res = [];
        if (sel.indexOf('.maplibregl-popup') !== -1) res = res.concat(__popups);
        if (sel.indexOf('.building-3d-mast-plate') !== -1) res = res.concat(__mastPlates);
        if (sel.indexOf('.building-3d-facade-stack') !== -1) res = res.concat(__facadeStacks);
        if (sel.indexOf('.building-3d-room-badge') !== -1) res = res.concat(__badges);
        return res.filter(x => !x.removed);
      }}
    }};

    {clear_fn}
    {close_mast_fn}
    {close_facade_fn}
    {dismiss_badge_fn}
    {update_markers_fn}
    {select_floor_fn}

    // Mock institution with 3 floors
    var testInst = {{
      name: 'Bishop Museum (Bernice Pauahi Bishop Museum)',
      city: 'Honolulu',
      country: 'United States',
      lat: 21.3328,
      lon: -157.8712,
      tier: 'A',
      hours: 'Wed–Sun 11:00–19:00',
      admission: 'Free Admission',
      floor_plans: [
        {{ level: 0, level_code: 'L0', floor_name: 'Ground Floor', current_shows: [{{ title: 'Pacific Hall Main' }}] }},
        {{ level: 1, level_code: 'L1', floor_name: 'First Floor', current_shows: [{{ title: 'Hawaiian Hall Gallery' }}] }},
        {{ level: 2, level_code: 'L2', floor_name: 'Second Floor', current_shows: [{{ title: 'Kāhili Room Archives' }}] }}
      ]
    }};
    selectedInstitution = testInst;

    // STEP 1: Initial Building Entry
    print('Testing initial building load...');
    updateBuilding3DInfoMarkers(testInst);
    var mastCountInitial = document.querySelectorAll('.building-3d-mast-plate').length;
    var roomBadgesInitial = document.querySelectorAll('.building-3d-room-badge').length;
    print('Initial mast count: ' + mastCountInitial + ', room badges: ' + roomBadgesInitial);
    if (mastCountInitial !== 1) throw new Error('Mast plate was not created on initial load');
    if (roomBadgesInitial < 2) throw new Error('Room badges were not created on initial load');
    print('[PASS] Initial building view properly mounts mast plate and room badges');

    // STEP 2: User explicitly dismisses rooftop mast plate (clicks 'x' on card)
    print('Testing closeBuildingMast() dismissal...');
    closeBuildingMast();
    if (isBuildingMastDismissed !== true) throw new Error('isBuildingMastDismissed was not set to true');
    if (currentBuildingMastMarker !== null) throw new Error('currentBuildingMastMarker was not cleared');
    if (document.querySelectorAll('.building-3d-mast-plate').length !== 0) throw new Error('Mast plate still in DOM after close');
    print('[PASS] Rooftop mast card dismissed cleanly');

    // STEP 3: User clicks on a floor (e.g., Level 1)
    print('Testing selectBfiFloor(1) after mast was closed...');
    selectBfiFloor(1);

    var mastCountAfterFloorClick = document.querySelectorAll('.building-3d-mast-plate').length;
    var roomBadgesAfterFloorClick = document.querySelectorAll('.building-3d-room-badge').length;
    print('After clicking floor: mast count = ' + mastCountAfterFloorClick + ', room badges = ' + roomBadgesAfterFloorClick);

    if (mastCountAfterFloorClick !== 0) {{
      throw new Error('BUG REPRODUCED: Info about museum mast card popped back up after floor was clicked!');
    }}
    if (roomBadgesAfterFloorClick < 2) {{
      throw new Error('Room badges for Level 1 were not rendered!');
    }}
    print('[PASS] Clicking floor successfully updates room badges without museum info popping back up!');

    // STEP 4: User clicks on another floor (e.g., Level 2)
    print('Testing selectBfiFloor(2)...');
    selectBfiFloor(2);
    if (document.querySelectorAll('.building-3d-mast-plate').length !== 0) {{
      throw new Error('Mast card popped back up on Level 2!');
    }}
    print('[PASS] Level 2 floor click maintains zero mast card popups');

    print('\\n🎉 ALL FLOOR CLICK NO-POPUP TESTS PASSED!');
    """

    test_file = "/tmp/test_floor_click_jsc.js"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(test_js)

    res = subprocess.run([jsc_bin, test_file], capture_output=True, text=True)
    if res.stdout:
        print(res.stdout)
    if res.stderr:
        print("STDERR:", res.stderr)
    assert res.returncode == 0, f"jsc test failed with code {res.returncode}"

if __name__ == '__main__':
    test_static_html()
    test_jsc_floor_click_behavior()
