#!/usr/bin/env python3
"""
test_building_floor_by_floor.py
Verification test suite for deep 20x architectural zoom and floor-by-floor
current shows and archival holdings exploration.
"""

import json
import re
import sys

def test_institutions_floor_plans():
    with open('institutions.json', 'r', encoding='utf-8') as f:
        insts = json.load(f)

    assert len(insts) > 1000, f"Expected >1000 institutions, got {len(insts)}"

    for inst in insts:
        slug = inst.get('slug', inst.get('name', 'Unknown'))
        assert 'floor_plans' in inst, f"Institution {slug} missing floor_plans"
        assert len(inst['floor_plans']) > 0, f"Institution {slug} has empty floor_plans"

        # Check structure of each floor
        for fl in inst['floor_plans']:
            assert 'level' in fl, f"Floor in {slug} missing level"
            assert 'floor_name' in fl, f"Floor in {slug} missing floor_name"
            assert 'current_shows' in fl, f"Floor in {slug} missing current_shows"
            assert isinstance(fl['current_shows'], list), f"current_shows must be a list in {slug}"
            assert len(fl['current_shows']) > 0, f"current_shows empty in {slug}"
            show = fl['current_shows'][0]
            assert 'title' in show, f"Show in {slug} missing title"
            assert 'dates' in show, f"Show in {slug} missing dates"

            assert 'archive_holdings' in fl, f"Floor in {slug} missing archive_holdings"
            arch = fl['archive_holdings']
            assert 'collection_title' in arch, f"Archive holding in {slug} missing collection_title"

    print(f"✅ Verified floor_plans across all {len(insts)} institutions in dataset.")

def test_index_html_floor_inspector_hud():
    with open('index.html', 'r', encoding='utf-8') as f:
        html = f.read()

    # Verify buildingFloorInspectorHud markup
    assert 'id="buildingFloorInspectorHud"' in html, "Missing #buildingFloorInspectorHud in index.html"
    assert 'id="bfiFloorTabs"' in html, "Missing #bfiFloorTabs in index.html"
    assert 'id="bfiFloorCard"' in html, "Missing #bfiFloorCard in index.html"
    assert 'id="bfiShowTitle"' in html, "Missing #bfiShowTitle in index.html"
    assert 'id="bfiArchiveTitle"' in html, "Missing #bfiArchiveTitle in index.html"
    assert 'id="bfiZoomCloserBtn"' in html, "Missing #bfiZoomCloserBtn in index.html"
    assert 'id="bfiResetZoomBtn"' in html, "Missing #bfiResetZoomBtn in index.html"
    assert 'id="bfiOpenModalBtn"' in html, "Missing #bfiOpenModalBtn in index.html"

    # Verify JS functions
    assert 'function zoomCloserToBuilding(' in html, "Missing zoomCloserToBuilding() in index.html"
    assert 'function showBuildingFloorInspectorHud(' in html, "Missing showBuildingFloorInspectorHud() in index.html"
    assert 'function selectBfiFloor(' in html, "Missing selectBfiFloor() in index.html"
    assert 'function hideBuildingFloorInspectorHud(' in html, "Missing hideBuildingFloorInspectorHud() in index.html"
    assert 'function filterBamFloorLevel(' in html, "Missing filterBamFloorLevel() in index.html"

    # Check ultra-deep zoom parameter
    assert 'targetZoom = 20.0' in html or 'zoom: 20' in html or 'targetZoom = 20' in html, "Missing 20x target zoom"

    # Verify Modal Floor-by-Floor Directory
    assert 'Floor-by-Floor Directory: Current Shows & Archival Holdings' in html or 'Floor-by-Floor Directory' in html, "Missing Floor-by-Floor Directory header in modal"
    assert 'bamFloorFilterTabs' in html, "Missing bamFloorFilterTabs in index.html"
    assert 'bam-floor-card' in html, "Missing bam-floor-card classes in index.html"
    assert 'ARCHIVE HOLDING ON THIS LEVEL' in html or 'ARCHIVAL HOLDING' in html, "Missing ARCHIVE HOLDING in modal"

    # Verify Curator Chat integration
    assert "q.includes('floor')" in html, "Missing floor query check in curator chat"
    assert "Floor-by-Floor Current Shows & Archival Holdings" in html, "Missing floor breakdown in curator response"

    print("✅ Verified HTML markup, HUD inspector, Modal floor directory, and Curator chat in index.html.")

def test_app_and_standalone():
    for filename in ['app/index.html', 'app/standalone.html']:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        assert 'id="buildingFloorInspectorHud"' in content, f"Missing #buildingFloorInspectorHud in {filename}"
        assert 'function zoomCloserToBuilding(' in content, f"Missing zoomCloserToBuilding in {filename}"
        assert 'Floor-by-Floor Directory: Current Shows & Archival Holdings' in content or 'Floor-by-Floor Directory' in content, f"Missing Floor directory in {filename}"
        print(f"✅ Verified {filename}")

if __name__ == '__main__':
    try:
        test_institutions_floor_plans()
        test_index_html_floor_inspector_hud()
        test_app_and_standalone()
        print("\n🎉 ALL 4/4 FLOOR-BY-FLOOR AND 20X ZOOM SUITES PASSED!")
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
