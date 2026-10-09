import os

def test_plus_icons():
    files = [
        "/Users/polinavasilyeva/.gemini/antigravity/scratch/sponsor-atlas/index.html",
        "/Users/polinavasilyeva/.gemini/antigravity/scratch/sponsor-atlas/app/index.html",
        "/Users/polinavasilyeva/.gemini/antigravity/scratch/sponsor-atlas/app/standalone.html",
        "/Users/polinavasilyeva/.gemini/antigravity/brain/b997e616-4551-453e-83cc-4ba184f90abf/culture_atlas_app.html"
    ]

    for path in files:
        assert os.path.exists(path), f"File {path} does not exist"
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        # 1. workPlusBtn
        assert 'id="workPlusBtn"' in content, f"Missing workPlusBtn in {path}"
        idx = content.find('id="workPlusBtn"')
        end_idx = content.find('</button>', idx)
        btn_html = content[idx:end_idx]
        assert '<svg' in btn_html, f"workPlusBtn missing SVG in {path}"
        assert 'x1="12" y1="5" x2="12" y2="19"' in btn_html, f"workPlusBtn missing vertical line in {path}"
        assert 'x1="5" y1="12" x2="19" y2="12"' in btn_html, f"workPlusBtn missing horizontal line in {path}"

        # 2. topNewChatBtn
        assert 'id="topNewChatBtn"' in content, f"Missing topNewChatBtn in {path}"
        idx2 = content.find('id="topNewChatBtn"')
        end_idx2 = content.find('</button>', idx2)
        top_btn_html = content[idx2:end_idx2]
        assert '<svg' in top_btn_html, f"topNewChatBtn missing SVG in {path}"
        assert 'x1="12" y1="5" x2="12" y2="19"' in top_btn_html, f"topNewChatBtn missing plus line in {path}"

        # 3. mobileNewChatBtn
        assert 'id="mobileNewChatBtn"' in content, f"Missing mobileNewChatBtn in {path}"
        idx3 = content.find('id="mobileNewChatBtn"')
        end_idx3 = content.find('</button>', idx3)
        mobile_btn_html = content[idx3:end_idx3]
        assert '<svg' in mobile_btn_html, f"mobileNewChatBtn missing SVG in {path}"
        assert 'x1="12" y1="5" x2="12" y2="19"' in mobile_btn_html, f"mobileNewChatBtn missing plus line in {path}"

        # 4. zoomInBtn
        assert 'id="zoomInBtn"' in content, f"Missing zoomInBtn in {path}"
        idx4 = content.find('id="zoomInBtn"')
        end_idx4 = content.find('</button>', idx4)
        zoom_btn_html = content[idx4:end_idx4]
        assert '<svg' in zoom_btn_html, f"zoomInBtn missing SVG in {path}"

        # 5. trusteeZoomInBtn
        assert 'id="trusteeZoomInBtn"' in content, f"Missing trusteeZoomInBtn in {path}"
        idx5 = content.find('id="trusteeZoomInBtn"')
        end_idx5 = content.find('</button>', idx5)
        trustee_btn_html = content[idx5:end_idx5]
        assert '<svg' in trustee_btn_html, f"trusteeZoomInBtn missing SVG in {path}"

    print("✅ All plus icon verification tests passed successfully across all targets!")

if __name__ == "__main__":
    test_plus_icons()
