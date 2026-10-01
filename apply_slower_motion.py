import re

# Update build_split_screen_atlas.py
path = "/Users/polinavasilyeva/.gemini/antigravity/scratch/sponsor-atlas/build_split_screen_atlas.py"
with open(path, "r", encoding="utf-8") as f:
    text = f.read()

# Replace flying and spinning in main app
old_flying_main = """      if (isFlying) {{
        flightProgress += 0.04;
        if (flightProgress >= 1) {{
          flightProgress = 1;
          isFlying = false;
        }}
        const ease = 1 - Math.pow(1 - flightProgress, 3);
        rotLon = rotLon + (targetRotLon - rotLon) * ease;
        rotLat = rotLat + (targetRotLat - rotLat) * ease;
      }} else if (isAutoSpinning && !isDragging) {{
        rotLon = (rotLon + 0.22) % 360;
      }}"""

new_flying_main = """      if (isFlying) {{
        // Slower, smooth cinematic glide (~1.6s easeInOut)
        flightProgress += 0.011;
        if (flightProgress >= 1) {{
          flightProgress = 1;
          isFlying = false;
          rotLon = targetRotLon;
          rotLat = targetRotLat;
        }} else {{
          // Smooth cubic easeInOut curve
          const t = flightProgress;
          const ease = t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
          rotLon = startRotLon + (targetRotLon - startRotLon) * ease;
          rotLat = startRotLat + (targetRotLat - startRotLat) * ease;
        }}
      }} else if (isAutoSpinning && !isDragging) {{
        // Serene, slow hypnotic drift (0.04 deg/frame)
        rotLon = (rotLon + 0.04) % 360;
      }}"""

if old_flying_main in text:
    text = text.replace(old_flying_main, new_flying_main)
    print("Replaced main render flying animation")
else:
    print("WARNING: old_flying_main not found")

# Replace radius lerp
text = text.replace("globeRadius += (targetRadius - globeRadius) * 0.15;", "globeRadius += (targetRadius - globeRadius) * 0.065;")

# Replace flyTo variables and function
old_flyTo_main = """    let rotLon = -45;
    let rotLat = 35;
    let targetRotLon = -45;
    let targetRotLat = 35;
    let isFlying = false;
    let flightProgress = 0;"""

new_flyTo_main = """    let rotLon = -45;
    let rotLat = 35;
    let startRotLon = -45;
    let startRotLat = 35;
    let targetRotLon = -45;
    let targetRotLat = 35;
    let isFlying = false;
    let flightProgress = 0;"""

if old_flyTo_main in text:
    text = text.replace(old_flyTo_main, new_flyTo_main)
    print("Replaced main flyTo variables")

old_flyTo_fn = """    function flyTo(lon, lat) {{
      isAutoSpinning = false;
      let dLon = (lon - rotLon) % 360;
      if (dLon > 180) dLon -= 360;
      if (dLon < -180) dLon += 360;
      targetRotLon = rotLon + dLon;
      targetRotLat = Math.max(-75, Math.min(75, lat));
      flightProgress = 0;
      isFlying = true;
    }}"""

new_flyTo_fn = """    function flyTo(lon, lat) {{
      isAutoSpinning = false;
      let dLon = (lon - rotLon) % 360;
      if (dLon > 180) dLon -= 360;
      if (dLon < -180) dLon += 360;
      startRotLon = rotLon;
      startRotLat = rotLat;
      targetRotLon = rotLon + dLon;
      targetRotLat = Math.max(-75, Math.min(75, lat));
      flightProgress = 0;
      isFlying = true;
    }}"""

if old_flyTo_fn in text:
    text = text.replace(old_flyTo_fn, new_flyTo_fn)
    print("Replaced main flyTo function")

# Replace drag sensitivity
old_drag_main = """        rotLon = (rotLon - dx * 0.5) % 360;
        rotLat = Math.max(-75, Math.min(75, rotLat + dy * 0.5));"""

new_drag_main = """        // Weighted, slower, controlled drag rotation
        rotLon = (rotLon - dx * 0.18) % 360;
        rotLat = Math.max(-75, Math.min(75, rotLat + dy * 0.18));"""

if old_drag_main in text:
    text = text.replace(old_drag_main, new_drag_main)
    print("Replaced main drag sensitivity")

# Replace wheel zoom sensitivity
old_wheel = "const factor = e.deltaY < 0 ? 1.14 : 0.88;"
new_wheel = "const factor = e.deltaY < 0 ? 1.07 : 0.93; // Slower, gradual zoom"
if old_wheel in text:
    text = text.replace(old_wheel, new_wheel)
    print("Replaced wheel zoom factor")

# Now update the widget section in build_split_screen_atlas.py
old_widget_vars = """    let rotLon = -45;
    let rotLat = 35;
    let targetRotLon = -45;
    let targetRotLat = 35;
    let isFlying = false;
    let flightProgress = 0;"""

new_widget_vars = """    let rotLon = -45;
    let rotLat = 35;
    let startRotLon = -45;
    let startRotLat = 35;
    let targetRotLon = -45;
    let targetRotLat = 35;
    let isFlying = false;
    let flightProgress = 0;"""

if old_widget_vars in text:
    text = text.replace(old_widget_vars, new_widget_vars)

old_widget_flying = """      if (isFlying) {{
        flightProgress += 0.05;
        if (flightProgress >= 1) {{ flightProgress = 1; isFlying = false; }}
        const ease = 1 - Math.pow(1 - flightProgress, 3);
        rotLon = rotLon + (targetRotLon - rotLon) * ease;
        rotLat = rotLat + (targetRotLat - rotLat) * ease;
      }}"""

new_widget_flying = """      if (isFlying) {{
        flightProgress += 0.012;
        if (flightProgress >= 1) {{
          flightProgress = 1;
          isFlying = false;
          rotLon = targetRotLon;
          rotLat = targetRotLat;
        }} else {{
          const t = flightProgress;
          const ease = t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
          rotLon = startRotLon + (targetRotLon - startRotLon) * ease;
          rotLat = startRotLat + (targetRotLat - startRotLat) * ease;
        }}
      }}"""

if old_widget_flying in text:
    text = text.replace(old_widget_flying, new_widget_flying)

old_widget_flyTo = """    function flyTo(lon, lat) {{
      let dLon = (lon - rotLon) % 360;
      if (dLon > 180) dLon -= 360;
      if (dLon < -180) dLon += 360;
      targetRotLon = rotLon + dLon;
      targetRotLat = Math.max(-75, Math.min(75, lat));
      flightProgress = 0;
      isFlying = true;
    }}"""

new_widget_flyTo = """    function flyTo(lon, lat) {{
      let dLon = (lon - rotLon) % 360;
      if (dLon > 180) dLon -= 360;
      if (dLon < -180) dLon += 360;
      startRotLon = rotLon;
      startRotLat = rotLat;
      targetRotLon = rotLon + dLon;
      targetRotLat = Math.max(-75, Math.min(75, lat));
      flightProgress = 0;
      isFlying = true;
    }}"""

if old_widget_flyTo in text:
    text = text.replace(old_widget_flyTo, new_widget_flyTo)

old_widget_drag = """        rotLon = (rotLon - dx * 0.6) % 360;
        rotLat = Math.max(-75, Math.min(75, rotLat + dy * 0.6));"""

new_widget_drag = """        rotLon = (rotLon - dx * 0.2) % 360;
        rotLat = Math.max(-75, Math.min(75, rotLat + dy * 0.2));"""

if old_widget_drag in text:
    text = text.replace(old_widget_drag, new_widget_drag)

with open(path, "w", encoding="utf-8") as f:
    f.write(text)

print("Saved updated build_split_screen_atlas.py with slower motion!")
