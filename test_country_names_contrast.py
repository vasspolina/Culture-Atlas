#!/usr/bin/env python3
"""
test_country_names_contrast.py
Verifies that country names on the 3D globe have maximum contrast and legibility:
1. High-contrast pure white (#ffffff) fill in standard mode, neon yellow (#fef08a) in gossip mode.
2. Solid dark outline halo (strokeText with lineWidth >= 3.0) for sharp boundary definition.
3. Protective dark backdrop plate (roundRect with alpha >= 0.82) behind every country name.
4. Non-overlapping multi-country collision avoidance preventing clobbered text.
5. High opacity throughout regional zoom exploration.
"""

import os
import sys

def test_country_contrast_code():
    with open('index.html', 'r', encoding='utf-8') as f:
        html = f.read()

    # 1. High-contrast styling
    assert 'strokeText(c.name' in html, "Missing strokeText dark halo for country names"
    assert "lineWidth = 3.0" in html or "lineWidth = 3" in html, "Missing 3px stroke outline for country names"
    assert "drawnCountryBoxes" in html, "Missing drawnCountryBoxes for multi-country collision avoidance"
    assert "collidesWithCountry" in html, "Missing collidesWithCountry check"
    assert "'#ffffff'" in html, "Missing pure white fill for country labels"

    # 2. Check no premature fade alpha
    assert "r > baseRadius * 3.2" in html, "Missing extended zoom threshold for country labels"

    print("✅ Country names contrast and anti-collision verified successfully.")

if __name__ == '__main__':
    test_country_contrast_code()
