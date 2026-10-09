import json, os

def test_data():
    with open("academic_papers.json", "r", encoding="utf-8") as f:
        papers = json.load(f)
    print(f"[TEST 1] academic_papers.json total count: {len(papers)}")
    assert len(papers) >= 170, f"Expected >= 170 papers, got {len(papers)}"

    # Check for the Consensus link paper: Mark W. Rectanus
    rectanus = [p for p in papers if "rectanus" in (p.get("authors") or "").lower() or "culture incorporated" in (p.get("title") or "").lower()]
    assert len(rectanus) > 0, "Rectanus paper missing!"
    print(f"  ✓ Found Rectanus Consensus study: {rectanus[0]['title']}")

    # Check for Lund & Greyser paper
    lund = [p for p in papers if "lund" in (p.get("authors") or "").lower() or "integrated partnerships in cultural sponsorship" in (p.get("title") or "").lower()]
    assert len(lund) > 0, "Lund paper missing!"
    print(f"  ✓ Found Lund & Greyser Consensus study: {lund[0]['title']}")

    # Check for Alshawaaf & Lee
    alshawaaf = [p for p in papers if "alshawaaf" in (p.get("authors") or "").lower() or "paradox of corporate sponsorship" in (p.get("title") or "").lower()]
    assert len(alshawaaf) > 0, "Alshawaaf & Lee paper missing!"
    print(f"  ✓ Found Alshawaaf & Lee Consensus study: {alshawaaf[0]['title']}")

    with open("institutions.json", "r", encoding="utf-8") as f:
        insts = json.load(f)
    
    vc_insts = [i for i in insts if i.get("visual_critiques")]
    print(f"[TEST 2] Institutions with visual critiques: {len(vc_insts)}")
    assert len(vc_insts) >= 25, f"Expected >= 25 institutions with visual critiques, got {len(vc_insts)}"

    test_names = ["Guggenheim", "Whitney", "MoMA", "Metropolitan", "British Museum", "Tate", "Louvre", "Orsay"]
    for t in test_names:
        matched = [i for i in vc_insts if t.lower() in i.get("name", "").lower()]
        assert len(matched) > 0, f"Missing visual critique for {t}"
        inst = matched[0]
        vc = inst["visual_critiques"][0]
        artist = vc.get("artist_designer") or vc.get("artist")
        work = vc.get("artwork_title") or vc.get("artwork")
        credits = vc.get("credits")
        citation = vc.get("citation")
        print(f"  ✓ {inst['name']}:")
        print(f"      Artist: {artist}")
        print(f"      Work: {work} ({vc.get('year')})")
        print(f"      Credits: {credits[:60]}...")
        print(f"      Citation: {citation[:50]}...")
        assert artist, f"Missing artist for {inst['name']}"
        assert work, f"Missing work for {inst['name']}"
        assert credits, f"Missing credits for {inst['name']}"
        assert citation, f"Missing citation for {inst['name']}"

def test_html_files():
    files = [
        "index.html", 
        "app/index.html", 
        "app/standalone.html",
        "/Users/polinavasilyeva/.gemini/antigravity/brain/b997e616-4551-453e-83cc-4ba184f90abf/culture_atlas_app.html"
    ]
    for fn in files:
        with open(fn, "r", encoding="utf-8") as f:
            html = f.read()
        print(f"[TEST 3] Checking {os.path.basename(fn)} ({len(html)} bytes)...")
        assert "🎨 ARTIST &amp; DESIGNER VISUAL CRITIQUE" in html or "🎨 Artist &amp; Designer Visual Critique" in html
        assert "floatingCardVcCredits" in html
        assert "floatingCardVcArtist" in html
        assert "visualCritiqueSubBar" in html
        assert "data-strategy=\"sponsor_exposure\"" in html
        assert "data-strategy=\"forensic_investigation\"" in html
        assert "data-strategy=\"pharma_fossil_denaming\"" in html
        assert "Consensus Empirical Research Archive" in html
        print(f"  ✓ {os.path.basename(fn)} verified with all visual critique UI components!")

if __name__ == "__main__":
    test_data()
    test_html_files()
    print("\nALL TESTS PASSED! Visual Critique layer & Consensus research fully integrated.")
