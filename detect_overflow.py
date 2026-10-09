import subprocess
import json
import html as html_lib

chrome_bin = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
index_path = "/Users/polinavasilyeva/.gemini/antigravity/scratch/sponsor-atlas/index.html"

test_script = """
<script>
window.addEventListener("load", () => {
  setTimeout(() => {
    const docWidth = document.documentElement.clientWidth;
    const overflowing = [];
    document.querySelectorAll("*").forEach(el => {
      const rect = el.getBoundingClientRect();
      if (rect.right > docWidth + 2 && el.offsetWidth > 0 && el.offsetHeight > 0) {
        overflowing.push({
          tag: el.tagName,
          id: el.id,
          className: el.className ? el.className.toString().slice(0, 80) : "",
          width: Math.round(rect.width),
          right: Math.round(rect.right),
          docWidth: Math.round(docWidth)
        });
      }
    });
    const div = document.createElement("div");
    div.id = "overflow-results";
    div.setAttribute("data-overflow", JSON.stringify(overflowing));
    document.body.appendChild(div);
  }, 1000);
});
</script>
"""

with open(index_path, "r", encoding="utf-8") as f:
    html = f.read()

harness = html.replace("</body>", f"{test_script}</body>")
with open("/tmp/test_mobile_overflow.html", "w", encoding="utf-8") as f:
    f.write(harness)

cmd = [
    chrome_bin,
    "--headless=new",
    "--dump-dom",
    "--window-size=390,844",
    "--virtual-time-budget=6000",
    "file:///tmp/test_mobile_overflow.html"
]
proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=60)
marker = 'id="overflow-results" data-overflow="'
if marker in proc.stdout:
    raw = proc.stdout.split(marker)[1].split('"')[0]
    data = json.loads(html_lib.unescape(raw))
    print(f"FOUND {len(data)} OVERFLOWING ELEMENTS:")
    seen = set()
    for item in data:
        key = (item["tag"], item["id"])
        if key not in seen:
            seen.add(key)
            tag = item["tag"]
            elem_id = item["id"]
            w = item["width"]
            r = item["right"]
            dw = item["docWidth"]
            cls = item["className"]
            print(f"Tag: {tag}, ID: {elem_id}, Width: {w}, Right: {r}, DocWidth: {dw}, Class: {cls}")
else:
    print("Marker not found! Stderr:", proc.stderr[:500])
