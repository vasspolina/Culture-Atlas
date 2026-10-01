import re

def update_widget():
    path = "/Users/polinavasilyeva/.gemini/antigravity/brain/b997e616-4551-453e-83cc-4ba184f90abf/concierge_widget.html"
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # Find boundaries
    start_marker = "    let isDragging = false;\n    let lastX = 0, lastY = 0;"
    end_marker = "    function flyTo(lon, lat) {"

    if start_marker not in content or end_marker not in content:
        print("ERROR: markers not found in concierge_widget.html")
        return False

    idx1 = content.find(start_marker) + len(start_marker)
    idx2 = content.find(end_marker)

    new_code = """
    let baseRadius = 140;
    let globeRadius = 140;
    let targetRadius = 140;

    const getMinRadius = () => Math.min(canvas.width, canvas.height) * 0.25;
    const getMaxRadius = () => Math.min(canvas.width, canvas.height) * 2.2;

    function initRadius() {
      baseRadius = Math.min(canvas.width, canvas.height) * 0.44;
      if (!targetRadius || targetRadius === 140) {
        targetRadius = baseRadius;
        globeRadius = baseRadius;
      }
    }
    initRadius();

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

    let currentVisibleInsts = [];

    function render() {
      const w = canvas.width;
      const h = canvas.height;
      const cx = w / 2;
      const cy = h / 2;

      // Smooth zoom transition
      globeRadius += (targetRadius - globeRadius) * 0.16;
      const r = globeRadius;

      ctx.clearRect(0, 0, w, h);
      clearOccupiedBoxes();

      if (isFlying) {
        flightProgress += 0.05;
        if (flightProgress >= 1) {
          flightProgress = 1;
          isFlying = false;
        }
        const ease = 1 - Math.pow(1 - flightProgress, 3);
        rotLon = rotLon + (targetRotLon - rotLon) * ease;
        rotLat = rotLat + (targetRotLat - rotLat) * ease;
      } else if (isAutoSpinning && !isDragging) {
        rotLon = (rotLon + 0.25) % 360;
      }

      // Solid Carbon Sphere (NO glow, NO atmospheric haze)
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
      [-45, 0, 45].forEach(lat => {
        ctx.beginPath();
        let first = true;
        for (let lon = -180; lon <= 180; lon += 12) {
          const pt = project(lon, lat, r, cx, cy);
          if (pt) {
            if (first) { ctx.moveTo(pt.x, pt.y); first = false; }
            else { ctx.lineTo(pt.x, pt.y); }
          } else { first = true; }
        }
        ctx.stroke();
      });

      // Draw Country Boundaries (Sharp 0.8px, NO glow)
      ctx.strokeStyle = '#525252';
      ctx.lineWidth = 0.8;
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
      // 📍 STEP 1: INSTITUTION PROJECTION & ANTI-OVERLAP SPIDERFY
      // -------------------------------------------------------------
      const filtered = DATA.filter(inst => {
        if (selectedCountry !== 'all' && inst.country.toLowerCase() !== selectedCountry.toLowerCase()) return false;
        if (selectedCity !== 'all' && inst.city.toLowerCase() !== selectedCity.toLowerCase()) return false;
        return true;
      });

      const visibleInsts = [];
      filtered.forEach(inst => {
        const pt = project(inst.lon, inst.lat, r, cx, cy);
        if (pt && pt.depth > 0) {
          const isSel = selectedInst && selectedInst.name === inst.name;
          const isHov = hoveredInst && hoveredInst.name === inst.name;
          const dotR = (isSel ? 5.5 : isHov ? 4.5 : inst.size === 'L' ? 3.5 : 2.2) * Math.min(1.4, Math.max(0.7, pt.depth));
          visibleInsts.push({
            inst,
            projX: pt.x,
            projY: pt.y,
            renderX: pt.x,
            renderY: pt.y,
            depth: pt.depth,
            dotR,
            spiderCenterX: pt.x,
            spiderCenterY: pt.y,
            isSpiderfied: false
          });
        }
      });
      currentVisibleInsts = visibleInsts;

      // Cluster detection (12px threshold)
      const clusters = [];
      const visited = new Uint8Array(visibleInsts.length);
      for (let i = 0; i < visibleInsts.length; i++) {
        if (visited[i]) continue;
        visited[i] = 1;
        const group = [visibleInsts[i]];
        for (let j = i + 1; j < visibleInsts.length; j++) {
          if (visited[j]) continue;
          const dist = Math.hypot(visibleInsts[i].projX - visibleInsts[j].projX, visibleInsts[i].projY - visibleInsts[j].projY);
          if (dist < 12) {
            visited[j] = 1;
            group.push(visibleInsts[j]);
          }
        }
        clusters.push(group);
      }

      // Radial spiderfy to prevent dot overlap
      const zoomRatio = Math.max(0.85, globeRadius / baseRadius);
      clusters.forEach(group => {
        if (group.length > 1) {
          let cxClust = 0, cyClust = 0;
          group.forEach(it => { cxClust += it.projX; cyClust += it.projY; });
          cxClust /= group.length;
          cyClust /= group.length;

          const minSpiderR = Math.max(8, (group.length * 11) / (2 * Math.PI));
          const spiderR = Math.min(32, minSpiderR * Math.sqrt(zoomRatio));

          group.forEach((item, idx) => {
            const angle = (idx / group.length) * Math.PI * 2 - Math.PI / 2;
            item.renderX = cxClust + Math.cos(angle) * spiderR;
            item.renderY = cyClust + Math.sin(angle) * spiderR;
            item.spiderCenterX = cxClust;
            item.spiderCenterY = cyClust;
            item.isSpiderfied = true;
          });

          // Spider lines
          ctx.strokeStyle = 'rgba(82, 82, 82, 0.4)';
          ctx.lineWidth = 0.5;
          group.forEach(item => {
            ctx.beginPath();
            ctx.moveTo(item.spiderCenterX, item.spiderCenterY);
            ctx.lineTo(item.renderX, item.renderY);
            ctx.stroke();
          });
        }
      });

      // Reserve dot boxes
      visibleInsts.forEach(v => {
        registerBox(v.renderX - v.dotR - 1, v.renderY - v.dotR - 1, (v.dotR + 1) * 2, (v.dotR + 1) * 2, 2);
      });

      // -------------------------------------------------------------
      // 🏙️ STEP 2: NAME CITIES (ANTI-COLLISION)
      // -------------------------------------------------------------
      const sortedCities = CITIES.slice().sort((a, b) => {
        if (selectedCity !== 'all') {
          if (a.name.toLowerCase() === selectedCity.toLowerCase()) return -1;
          if (b.name.toLowerCase() === selectedCity.toLowerCase()) return 1;
        }
        return b.count - a.count;
      });

      sortedCities.forEach(cty => {
        const pt = project(cty.lon, cty.lat, r, cx, cy);
        if (!pt || pt.depth <= 0.28) return;

        const isSelected = selectedCity.toLowerCase() === cty.name.toLowerCase();
        if (!isSelected && globeRadius < 180 && cty.count < 3) return;

        ctx.font = (isSelected ? '600 9.5px' : '500 8px') + ' "IBM Plex Sans", sans-serif';
        const tw = ctx.measureText(cty.name).width;
        const th = 9.5;

        const optRight = { x: pt.x + 4, y: pt.y - 4.5, w: tw, h: th };
        const optLeft = { x: pt.x - 4 - tw, y: pt.y - 4.5, w: tw, h: th };

        let chosen = null;
        if (!doesBoxOverlap(optRight, 2.5)) chosen = { ...optRight, align: 'left', tx: pt.x + 4 };
        else if (!doesBoxOverlap(optLeft, 2.5)) chosen = { ...optLeft, align: 'right', tx: pt.x - 4 };

        if (chosen || isSelected) {
          ctx.fillStyle = isSelected ? '#f1c21b' : '#8d8d8d';
          ctx.fillRect(pt.x - 1, pt.y - 1, 2.5, 2.5);
          registerBox(pt.x - 1.5, pt.y - 1.5, 3, 3, 1);

          if (chosen) {
            ctx.textAlign = chosen.align;
            ctx.textBaseline = 'middle';
            ctx.fillStyle = isSelected ? '#ffffff' : '#c6c6c6';
            ctx.fillText(cty.name, chosen.tx, pt.y);
            registerBox(chosen.x, chosen.y, chosen.w, chosen.h, 2.5);
          }
        }
      });

      // -------------------------------------------------------------
      // 🏷️ STEP 3: NAME COUNTRIES (NO OVERLAP)
      // -------------------------------------------------------------
      if (globeRadius <= 240) {
        const countryAlpha = globeRadius > 180 ? Math.max(0, (240 - globeRadius) / 60) : 1;
        ctx.font = '600 8.5px "IBM Plex Sans", sans-serif';

        COUNTRY_CENTROIDS.forEach(c => {
          const pt = project(c.lon, c.lat, r, cx, cy);
          if (!pt || pt.depth <= 0.25) return;

          const tw = ctx.measureText(c.name).width;
          const box = { x: pt.x - tw / 2, y: pt.y - 4.5, w: tw, h: 9.5 };

          if (!doesBoxOverlap(box, 3)) {
            ctx.fillStyle = `rgba(141, 141, 141, ${0.6 * countryAlpha})`;
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillText(c.name, pt.x, pt.y);
            registerBox(box.x, box.y, box.w, box.h, 3);
          }
        });
      }

      ctx.restore();

      // Sharp Carbon Globe Rim (NO glow)
      ctx.strokeStyle = '#393939';
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.arc(cx, cy, r, 0, Math.PI * 2);
      ctx.stroke();

      // -------------------------------------------------------------
      // 🔴 STEP 4: DRAW INSTITUTION DOTS
      // -------------------------------------------------------------
      visibleInsts.forEach(v => {
        const inst = v.inst;
        const isSel = selectedInst && selectedInst.name === inst.name;
        const isHov = hoveredInst && hoveredInst.name === inst.name;

        let col = '#24a148'; // Verified
        if (inst.tier === 'B') col = '#4589ff'; // One Name
        if (inst.tier === 'U') col = '#8d8d8d'; // Unverified
        if (inst.why_not_on_map) col = '#f1c21b'; // Yellow 30

        if (isSel) {
          ctx.beginPath();
          ctx.arc(v.renderX, v.renderY, v.dotR + 2.5, 0, Math.PI * 2);
          ctx.strokeStyle = '#ffffff';
          ctx.lineWidth = 1.2;
          ctx.stroke();
        } else if (isHov) {
          ctx.beginPath();
          ctx.arc(v.renderX, v.renderY, v.dotR + 2, 0, Math.PI * 2);
          ctx.strokeStyle = '#f1c21b';
          ctx.lineWidth = 1;
          ctx.stroke();
        }

        ctx.beginPath();
        ctx.arc(v.renderX, v.renderY, v.dotR, 0, Math.PI * 2);
        ctx.fillStyle = col;
        ctx.fill();
      });

      requestAnimationFrame(render);
    }
    requestAnimationFrame(render);

    """

    content = content[:idx1] + new_code + content[idx2:]

    # Update hit-testing and wheel zoom in concierge_widget.html
    old_pointermove_hit = """        let hit = null;
        for (let i = 0; i < DATA.length; i++) {
          const inst = DATA[i];
          const pt = project(inst.lon, inst.lat, r, cx, cy);
          if (pt && Math.hypot(pt.x - mx, pt.y - my) < 9) {
            hit = inst;
            break;
          }
        }"""

    new_pointermove_hit = """        let hit = null;
        for (let i = 0; i < currentVisibleInsts.length; i++) {
          const v = currentVisibleInsts[i];
          if (Math.hypot(v.renderX - mx, v.renderY - my) < Math.max(8, v.dotR + 3)) {
            hit = v.inst;
            break;
          }
        }"""

    if old_pointermove_hit in content:
        content = content.replace(old_pointermove_hit, new_pointermove_hit)
    else:
        print("Note: old widget pointermove hit not found directly")

    # Add wheel zoom to widget canvas
    old_widget_reset = """    document.getElementById('widgetResetBtn').addEventListener('click', () => {
      flyTo(0, 20);
      setWidgetCountry('all');
      setWidgetCity('all');
    });"""

    new_widget_reset = """    // Wheel zoom & Touch zoom
    canvas.addEventListener('wheel', e => {
      e.preventDefault();
      const factor = e.deltaY < 0 ? 1.15 : 0.87;
      targetRadius = Math.max(getMinRadius(), Math.min(getMaxRadius(), targetRadius * factor));
    }, { passive: false });

    document.getElementById('widgetResetBtn').addEventListener('click', () => {
      targetRadius = baseRadius;
      flyTo(0, 20);
      setWidgetCountry('all');
      setWidgetCity('all');
    });"""

    if old_widget_reset in content:
        content = content.replace(old_widget_reset, new_widget_reset)

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("Successfully updated concierge_widget.html with anti-overlap and smooth zoom!")
    return True

if __name__ == "__main__":
    update_widget()
