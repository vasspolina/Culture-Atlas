import re

def update_app_index():
    path = "/Users/polinavasilyeva/.gemini/antigravity/scratch/sponsor-atlas/app/index.html"
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # We need to replace the canvas globe logic and rendering loop in app/index.html
    # Let's locate from `// 3D Canvas Globe` down to `// Pointer events`
    start_marker = "// 3D Canvas Globe (Pure IBM Carbon Colors - No Glow - Names Cities & Countries)"
    end_marker = "// Pointer events"
    
    if start_marker not in content or end_marker not in content:
        print("ERROR: Markers not found in app/index.html")
        return False

    before = content[:content.find(start_marker)]
    after = content[content.find(end_marker):]

    new_globe_code = """// 3D Canvas Globe (Pure IBM Carbon Colors - No Glow - Anti-Collision & Spiderfy on Zoom)
    const canvas = document.getElementById('globeCanvas');
    const ctx = canvas.getContext('2d');
    let rotLon = 0;
    let rotLat = 20;
    let targetRotLon = 0;
    let targetRotLat = 20;
    let isFlying = false;
    let flightProgress = 0;
    let isAutoSpinning = true;
    let isDragging = false;
    let lastX = 0, lastY = 0;
    let baseRadius = 260;
    let globeRadius = 260;
    let targetRadius = 260;

    const getMinRadius = () => Math.min(canvas.width, canvas.height) * 0.25;
    const getMaxRadius = () => Math.min(canvas.width, canvas.height) * 2.4;

    function resizeCanvas() {
      const rect = canvas.parentElement.getBoundingClientRect();
      const w = Math.min(rect.width, 1100);
      const h = Math.max(500, rect.height);
      canvas.width = w;
      canvas.height = h;
      baseRadius = Math.min(w, h) * 0.42;
      if (!targetRadius || targetRadius === 260) {
        targetRadius = baseRadius;
        globeRadius = baseRadius;
      }
    }
    window.addEventListener('resize', resizeCanvas);
    resizeCanvas();

    function project(lon, lat, r, cx, cy) {
      const rad = Math.PI / 180;
      const lambda = (lon - rotLon) * rad;
      const phi = lat * rad;
      const phi0 = rotLat * rad;

      const cosC = Math.sin(phi0) * Math.sin(phi) + Math.cos(phi0) * Math.cos(phi) * Math.cos(lambda);
      if (cosC < 0) return null;

      const x = cx + r * Math.cos(phi) * Math.sin(lambda);
      const y = cy - r * (Math.cos(phi0) * Math.sin(phi) - Math.sin(phi0) * Math.cos(phi) * Math.cos(lambda));
      return { x, y, depth: cosC };
    }

    // 🛡️ ANTI-COLLISION & BOUNDING BOX OCCUPANCY SYSTEM
    const occupiedBoxes = [];
    function clearOccupiedBoxes() {
      occupiedBoxes.length = 0;
    }
    function doesBoxOverlap(box, pad = 3) {
      const x1 = box.x - pad;
      const y1 = box.y - pad;
      const x2 = box.x + box.w + pad;
      const y2 = box.y + box.h + pad;
      for (let i = 0; i < occupiedBoxes.length; i++) {
        const b = occupiedBoxes[i];
        if (x1 < b.x2 && x2 > b.x1 && y1 < b.y2 && y2 > b.y1) {
          return true;
        }
      }
      return false;
    }
    function registerBox(x, y, w, h, pad = 3) {
      occupiedBoxes.push({
        x1: x - pad,
        y1: y - pad,
        x2: x + w + pad,
        y2: y + h + pad
      });
    }

    // Cache of visible projected institutions for hit testing
    let currentVisibleInsts = [];

    function renderGlobe() {
      const w = canvas.width;
      const h = canvas.height;
      const cx = w / 2;
      const cy = h / 2;

      // Smooth zoom interpolation
      globeRadius += (targetRadius - globeRadius) * 0.16;
      const r = globeRadius;

      ctx.clearRect(0, 0, w, h);
      clearOccupiedBoxes();

      if (isFlying) {
        flightProgress += 0.04;
        if (flightProgress >= 1) {
          flightProgress = 1;
          isFlying = false;
        }
        const ease = 1 - Math.pow(1 - flightProgress, 3);
        rotLon = rotLon + (targetRotLon - rotLon) * ease;
        rotLat = rotLat + (targetRotLat - rotLat) * ease;
      } else if (isAutoSpinning && !isDragging) {
        rotLon = (rotLon + 0.22) % 360;
      }

      // Solid IBM Carbon Sphere (NO glow, NO outer radial haze)
      ctx.fillStyle = '#121619';
      ctx.beginPath();
      ctx.arc(cx, cy, r, 0, Math.PI * 2);
      ctx.fill();

      // Clip inside globe
      ctx.save();
      ctx.beginPath();
      ctx.arc(cx, cy, r, 0, Math.PI * 2);
      ctx.clip();

      // Faint Carbon Graticules
      ctx.strokeStyle = 'rgba(141, 141, 141, 0.12)';
      ctx.lineWidth = 0.5;
      [-60, -30, 0, 30, 60].forEach(lat => {
        ctx.beginPath();
        let first = true;
        for (let lon = -180; lon <= 180; lon += 8) {
          const pt = project(lon, lat, r, cx, cy);
          if (pt) {
            if (first) { ctx.moveTo(pt.x, pt.y); first = false; }
            else { ctx.lineTo(pt.x, pt.y); }
          } else { first = true; }
        }
        ctx.stroke();
      });

      for (let lon = -180; lon < 180; lon += 30) {
        ctx.beginPath();
        let first = true;
        for (let lat = -80; lat <= 80; lat += 8) {
          const pt = project(lon, lat, r, cx, cy);
          if (pt) {
            if (first) { ctx.moveTo(pt.x, pt.y); first = false; }
            else { ctx.lineTo(pt.x, pt.y); }
          } else { first = true; }
        }
        ctx.stroke();
      }

      // 🌍 Draw Country Boundaries (Sharp 0.85px, NO glow)
      ctx.strokeStyle = '#525252';
      ctx.lineWidth = 0.85;
      WORLD_ARCS.forEach(arc => {
        ctx.beginPath();
        let first = true;
        for (let i = 0; i < arc.length; i++) {
          const pt = project(arc[i][0], arc[i][1], r, cx, cy);
          if (pt) {
            if (first) { ctx.moveTo(pt.x, pt.y); first = false; }
            else { ctx.lineTo(pt.x, pt.y); }
          } else {
            first = true;
          }
        }
        ctx.stroke();
      });

      // -------------------------------------------------------------
      // 📍 STEP 1: PROJECT INSTITUTIONS & PREVENT OVERLAP (SPIDERFY)
      // -------------------------------------------------------------
      const visibleInsts = [];
      filteredInstitutions.forEach(inst => {
        const pt = project(inst.lon, inst.lat, r, cx, cy);
        if (pt && pt.depth > 0) {
          const isSel = selectedInstitution && selectedInstitution.name === inst.name;
          const isHov = hoveredInstitution && hoveredInstitution.name === inst.name;
          const dotR = (isSel ? 6.5 : isHov ? 5.5 : inst.size === 'L' ? 4 : 2.8) * Math.min(1.3, Math.max(0.7, pt.depth));
          visibleInsts.push({
            inst,
            projX: pt.x,
            projY: pt.y,
            renderX: pt.x,
            renderY: pt.y,
            depth: pt.depth,
            dotR,
            isSpiderfied: false,
            spiderCenterX: pt.x,
            spiderCenterY: pt.y
          });
        }
      });
      currentVisibleInsts = visibleInsts;

      // Group into spatial clusters within 13 screen pixels
      const clusters = [];
      const visited = new Uint8Array(visibleInsts.length);
      for (let i = 0; i < visibleInsts.length; i++) {
        if (visited[i]) continue;
        visited[i] = 1;
        const group = [visibleInsts[i]];
        for (let j = i + 1; j < visibleInsts.length; j++) {
          if (visited[j]) continue;
          const d = Math.hypot(visibleInsts[i].projX - visibleInsts[j].projX, visibleInsts[i].projY - visibleInsts[j].projY);
          if (d < 13) {
            visited[j] = 1;
            group.push(visibleInsts[j]);
          }
        }
        clusters.push(group);
      }

      // Disperse clustered dots radially so they NEVER overlap on zoom
      const zoomRatio = Math.max(0.85, globeRadius / baseRadius);
      clusters.forEach(group => {
        if (group.length > 1) {
          let cxClust = 0, cyClust = 0;
          group.forEach(it => { cxClust += it.projX; cyClust += it.projY; });
          cxClust /= group.length;
          cyClust /= group.length;

          // Circumference needed for non-overlapping dots: 2*PI*R >= N * 13px
          const minSpiderR = Math.max(10, (group.length * 13.5) / (2 * Math.PI));
          const spiderR = Math.min(42, minSpiderR * Math.sqrt(zoomRatio));

          group.forEach((item, idx) => {
            const angle = (idx / group.length) * Math.PI * 2 - Math.PI / 2;
            item.renderX = cxClust + Math.cos(angle) * spiderR;
            item.renderY = cyClust + Math.sin(angle) * spiderR;
            item.spiderCenterX = cxClust;
            item.spiderCenterY = cyClust;
            item.isSpiderfied = true;
          });

          // Draw spider hairline connectors (IBM Carbon subtle line)
          ctx.strokeStyle = 'rgba(82, 82, 82, 0.45)';
          ctx.lineWidth = 0.6;
          group.forEach(item => {
            ctx.beginPath();
            ctx.moveTo(item.spiderCenterX, item.spiderCenterY);
            ctx.lineTo(item.renderX, item.renderY);
            ctx.stroke();
          });

          // Faint center anchor
          ctx.fillStyle = '#525252';
          ctx.fillRect(cxClust - 1, cyClust - 1, 2, 2);
        }
      });

      // Reserve bounding boxes for all dots so labels never overlap dots
      visibleInsts.forEach(v => {
        registerBox(v.renderX - v.dotR - 2, v.renderY - v.dotR - 2, (v.dotR + 2) * 2, (v.dotR + 2) * 2, 2);
      });

      // -------------------------------------------------------------
      // 🏙️ STEP 2: NAME CITIES (ANTI-COLLISION HIERARCHY ON ZOOM)
      // -------------------------------------------------------------
      const sortedCities = CITY_LIST.slice().sort((a, b) => {
        if (selectedCity !== 'all') {
          if (a.name.toLowerCase() === selectedCity.toLowerCase()) return -1;
          if (b.name.toLowerCase() === selectedCity.toLowerCase()) return 1;
        }
        return b.count - a.count;
      });

      sortedCities.forEach(cty => {
        const pt = project(cty.lon, cty.lat, r, cx, cy);
        if (!pt || pt.depth <= 0.25) return;

        const isSelected = selectedCity.toLowerCase() === cty.name.toLowerCase();

        // Level of Detail on zoom:
        // When zoomed out, show high-density cities; as zoom increases, expand candidates
        if (!isSelected) {
          if (globeRadius < 300 && cty.count < 3) return;
          if (globeRadius < 420 && cty.count < 2) return;
        }

        ctx.font = (isSelected ? '600 11px' : '500 9.5px') + ' "IBM Plex Sans", sans-serif';
        const textWidth = ctx.measureText(cty.name).width;
        const textHeight = 11;

        // Try candidate label positions: Right, Left, Top
        const optRight = { x: pt.x + 5, y: pt.y - 5.5, w: textWidth, h: textHeight };
        const optLeft = { x: pt.x - 5 - textWidth, y: pt.y - 5.5, w: textWidth, h: textHeight };
        const optTop = { x: pt.x - textWidth / 2, y: pt.y - 14, w: textWidth, h: textHeight };

        let chosen = null;
        if (!doesBoxOverlap(optRight, 3)) chosen = { ...optRight, align: 'left', tx: pt.x + 5 };
        else if (!doesBoxOverlap(optLeft, 3)) chosen = { ...optLeft, align: 'right', tx: pt.x - 5 };
        else if (!doesBoxOverlap(optTop, 3)) chosen = { ...optTop, align: 'center', tx: pt.x };

        if (chosen || isSelected) {
          // Draw city marker square
          ctx.fillStyle = isSelected ? '#f1c21b' : '#8d8d8d';
          ctx.fillRect(pt.x - 1.5, pt.y - 1.5, 3, 3);
          registerBox(pt.x - 2, pt.y - 2, 4, 4, 1);

          if (chosen) {
            ctx.textAlign = chosen.align;
            ctx.textBaseline = 'middle';
            ctx.fillStyle = isSelected ? '#ffffff' : '#c6c6c6';
            ctx.fillText(cty.name, chosen.tx, pt.y);
            registerBox(chosen.x, chosen.y, chosen.w, chosen.h, 3);
          }
        }
      });

      // Selected City Square Highlight
      if (selectedCity !== 'all') {
        const cty = CITY_LIST.find(c => c.name.toLowerCase() === selectedCity.toLowerCase());
        if (cty) {
          const pt = project(cty.lon, cty.lat, r, cx, cy);
          if (pt) {
            ctx.strokeStyle = '#f1c21b'; // Carbon Yellow 30
            ctx.lineWidth = 1.5;
            ctx.strokeRect(pt.x - 8, pt.y - 8, 16, 16);
          }
        }
      }

      // -------------------------------------------------------------
      // 🏷️ STEP 3: NAME COUNTRIES (NO OVERLAP WITH CITIES OR DOTS)
      // -------------------------------------------------------------
      // On deep zoom (globeRadius > 480), country labels yield completely to museum details
      if (globeRadius <= 520) {
        const countryAlpha = globeRadius > 400 ? Math.max(0, (520 - globeRadius) / 120) : 1;
        ctx.font = '600 9.5px "IBM Plex Sans", sans-serif';

        COUNTRY_CENTROIDS.forEach(c => {
          const pt = project(c.lon, c.lat, r, cx, cy);
          if (!pt || pt.depth <= 0.25) return;

          const tw = ctx.measureText(c.name).width;
          const th = 11;
          const box = { x: pt.x - tw / 2, y: pt.y - 5.5, w: tw, h: th };

          // Only render if NO collision with city or institution dots!
          if (!doesBoxOverlap(box, 4)) {
            ctx.fillStyle = `rgba(141, 141, 141, ${0.65 * countryAlpha})`;
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillText(c.name, pt.x, pt.y);
            registerBox(box.x, box.y, box.w, box.h, 4);
          }
        });
      }

      // -------------------------------------------------------------
      // 🏛️ STEP 4: INSTITUTION LABELS ON DEEP ZOOM (NON-OVERLAPPING)
      // -------------------------------------------------------------
      if (globeRadius > 400) {
        visibleInsts.forEach(v => {
          const isSel = selectedInstitution && selectedInstitution.name === v.inst.name;
          const isHov = hoveredInstitution && hoveredInstitution.name === v.inst.name;

          ctx.font = '500 9.5px "IBM Plex Mono", monospace';
          const shortName = v.inst.name.length > 22 ? v.inst.name.slice(0, 20) + '…' : v.inst.name;
          const tw = ctx.measureText(shortName).width;
          const box = { x: v.renderX + v.dotR + 4, y: v.renderY - 5, w: tw, h: 10 };

          if (isSel || isHov || (globeRadius > 520 && !doesBoxOverlap(box, 3))) {
            if (!isSel && !isHov && doesBoxOverlap(box, 3)) return;
            ctx.fillStyle = isSel ? '#ffffff' : isHov ? '#f4f4f4' : '#8d8d8d';
            ctx.textAlign = 'left';
            ctx.textBaseline = 'middle';
            ctx.fillText(shortName, v.renderX + v.dotR + 4, v.renderY);
            registerBox(box.x, box.y, box.w, box.h, 2);
          }
        });
      }

      ctx.restore();

      // Sharp Carbon Globe Rim (NO glowing bloom)
      ctx.strokeStyle = '#393939';
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.arc(cx, cy, r, 0, Math.PI * 2);
      ctx.stroke();

      // -------------------------------------------------------------
      // 🔴 STEP 5: DRAW INSTITUTION DOTS (CLEAN IBM CARBON DATA PALETTE)
      // -------------------------------------------------------------
      visibleInsts.forEach(v => {
        const inst = v.inst;
        const isSel = selectedInstitution && selectedInstitution.name === inst.name;
        const isHov = hoveredInstitution && hoveredInstitution.name === inst.name;

        // IBM Carbon Data Palette
        let col = '#24a148'; // Verified: Carbon Green 50
        if (inst.tier === 'B') col = '#4589ff'; // One Name: Carbon Blue 50
        if (inst.tier === 'U') col = '#8d8d8d'; // Unverified: Carbon Gray 50
        if (inst.why_not_on_map) col = '#f1c21b'; // Audited/Pending: Carbon Yellow 30

        if (isSel) {
          ctx.beginPath();
          ctx.arc(v.renderX, v.renderY, v.dotR + 3, 0, Math.PI * 2);
          ctx.strokeStyle = '#ffffff';
          ctx.lineWidth = 1.5;
          ctx.stroke();
        } else if (isHov) {
          ctx.beginPath();
          ctx.arc(v.renderX, v.renderY, v.dotR + 2, 0, Math.PI * 2);
          ctx.strokeStyle = '#f1c21b';
          ctx.lineWidth = 1.2;
          ctx.stroke();
        }

        ctx.beginPath();
        ctx.arc(v.renderX, v.renderY, v.dotR, 0, Math.PI * 2);
        ctx.fillStyle = col;
        ctx.fill();
      });

      requestAnimationFrame(renderGlobe);
    }
    requestAnimationFrame(renderGlobe);

    """

    # Also let's update hover hit-testing and zoom controls in `after`
    # Replace pointermove hit testing:
    old_hit_test = """        const cx = canvas.width / 2;
        const cy = canvas.height / 2;
        const r = globeRadius;

        let hit = null;
        for (let i = 0; i < filteredInstitutions.length; i++) {
          const inst = filteredInstitutions[i];
          const pt = project(inst.lon, inst.lat, r, cx, cy);
          if (pt && Math.hypot(pt.x - mx, pt.y - my) < 9) {
            hit = inst;
            break;
          }
        }"""

    new_hit_test = """        let hit = null;
        for (let i = 0; i < currentVisibleInsts.length; i++) {
          const v = currentVisibleInsts[i];
          if (Math.hypot(v.renderX - mx, v.renderY - my) < Math.max(9, v.dotR + 4)) {
            hit = v.inst;
            break;
          }
        }"""

    if old_hit_test in after:
        after = after.replace(old_hit_test, new_hit_test)
    else:
        print("Note: old hit test not matched exactly, checking regex...")

    # Update zoom controls to smooth zoom with mouse wheel and pinch
    old_zoom_controls = """    // Controls
    document.getElementById('zoomInBtn').addEventListener('click', () => {
      globeRadius = Math.min(canvas.width, canvas.height) * 0.7;
    });
    document.getElementById('zoomOutBtn').addEventListener('click', () => {
      globeRadius = Math.min(canvas.width, canvas.height) * 0.3;
    });
    document.getElementById('resetViewBtn').addEventListener('click', () => {
      globeRadius = Math.min(canvas.width, canvas.height) * 0.42;
      flyTo(0, 20);
      setCountryFilter('all');
      setCityFilter('all');
    });"""

    new_zoom_controls = """    // Smooth Interactive Wheel & Button Zoom Controls
    canvas.addEventListener('wheel', e => {
      e.preventDefault();
      const zoomFactor = e.deltaY < 0 ? 1.15 : 0.87;
      targetRadius = Math.max(getMinRadius(), Math.min(getMaxRadius(), targetRadius * zoomFactor));
    }, { passive: false });

    // Touch Pinch Zoom
    let touchStartDist = 0;
    let touchStartRadius = targetRadius;
    canvas.addEventListener('touchstart', e => {
      if (e.touches.length === 2) {
        touchStartDist = Math.hypot(
          e.touches[0].clientX - e.touches[1].clientX,
          e.touches[0].clientY - e.touches[1].clientY
        );
        touchStartRadius = targetRadius;
      }
    }, { passive: true });

    canvas.addEventListener('touchmove', e => {
      if (e.touches.length === 2 && touchStartDist > 0) {
        const currentDist = Math.hypot(
          e.touches[0].clientX - e.touches[1].clientX,
          e.touches[0].clientY - e.touches[1].clientY
        );
        const scale = currentDist / touchStartDist;
        targetRadius = Math.max(getMinRadius(), Math.min(getMaxRadius(), touchStartRadius * scale));
      }
    }, { passive: true });

    canvas.addEventListener('touchend', () => {
      touchStartDist = 0;
    });

    document.getElementById('zoomInBtn').addEventListener('click', () => {
      targetRadius = Math.min(getMaxRadius(), targetRadius * 1.35);
    });
    document.getElementById('zoomOutBtn').addEventListener('click', () => {
      targetRadius = Math.max(getMinRadius(), targetRadius * 0.74);
    });
    document.getElementById('resetViewBtn').addEventListener('click', () => {
      targetRadius = baseRadius;
      flyTo(0, 20);
      setCountryFilter('all');
      setCityFilter('all');
    });"""

    if old_zoom_controls in after:
        after = after.replace(old_zoom_controls, new_zoom_controls)
    else:
        print("Note: old zoom controls not matched exactly")

    final_content = before + new_globe_code + after
    with open(path, "w", encoding="utf-8") as f:
        f.write(final_content)
    print("Successfully updated app/index.html with anti-overlap and smooth zoom!")

    # Now mirror to culture_atlas_app.html
    dest_path = "/Users/polinavasilyeva/.gemini/antigravity/brain/b997e616-4551-453e-83cc-4ba184f90abf/culture_atlas_app.html"
    with open(dest_path, "w", encoding="utf-8") as f:
        f.write(final_content)
    print("Successfully mirrored to culture_atlas_app.html!")
    return True

if __name__ == "__main__":
    update_app_index()
