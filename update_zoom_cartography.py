with open('build_conversational_atlas.py', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Replace procedural naming/street generation with clean getCityStreetData
part1_start = '    // Authentic Multi-Lingual Cultural Cartography Naming Engine'
part1_end = '    function getCityTargetRadius(cityName) {{'

new_part1 = """    // Clean Metropolitan Network Lookup (Curated cities only, zero synthetic noise)
    function getCityStreetData(cityName) {{
      if (!cityName) return null;
      const key = cityName.toLowerCase().trim();
      const normKey = key.normalize('NFD').replace(/[\\u0300-\\u036f]/g, '');
      const pCty = PRIORITY_CITIES.find(c => matchC(c.name, cityName));
      const cityInsts = ALL_INSTITUTIONS.filter(i => matchC(i.city, cityName));
      let centerLon = pCty ? pCty.lon : 0;
      let centerLat = pCty ? pCty.lat : 0;
      if (!pCty && cityInsts.length > 0) {{
        centerLon = cityInsts[0].lon;
        centerLat = cityInsts[0].lat;
      }}

      const curated = CITY_STREET_NETWORKS[key] || CITY_STREET_NETWORKS[normKey];
      if (curated) {{
        return {{
          center: curated.center || [centerLon, centerLat],
          waterways: curated.waterways || [],
          parks: curated.parks || [],
          major_streets: curated.major_streets || [],
          secondary_streets: curated.secondary_streets || []
        }};
      }}

      return {{
        center: [centerLon, centerLat],
        waterways: [],
        parks: [],
        major_streets: [],
        secondary_streets: []
      }};
    }}

"""

assert part1_start in code, "part1_start not found"
assert part1_end in code, "part1_end not found"

idx1 = code.find(part1_start)
idx2 = code.find(part1_end)
code = code[:idx1] + new_part1 + code[idx2:]
print("Part 1 replaced successfully.")

# 2. Update navigation banner title from 'STREET VIEW' to clean 'SANCTUARIES'
code = code.replace(
    "cityTitleEl.textContent = `${{activeCity.toUpperCase()}} · ${{cityMatches.length}} CLEAN SPACES · STREET VIEW`;",
    "cityTitleEl.textContent = `${{activeCity.toUpperCase()}} · ${{cityMatches.length}} CULTURAL SPACES`;"
)

# 3. Replace Deep Zoom rendering with pristine, clutter-free anti-collision layout
part2_start = '        // 🗺️ DEEP ZOOM CITY VIEW: URBAN ARCHITECTURE & CULTURAL CARTOGRAPHY'
part2_end = '        // 14. Architectural Cartographic Live HUD'

new_part2 = """        // 🗺️ DEEP ZOOM CITY VIEW: PRISTINE ARCHITECTURAL CARTOGRAPHY
        // =======================================================
        const cityData = getCityStreetData(activeCity);

        // 1. Regional Ocean & Water Surface Background
        ctx.fillStyle = '#050a14';
        ctx.fillRect(0, 0, width, height);

        // 2. Continental Landmass & Coastlines
        for (let i = 0; i < COUNTRY_POLYS.length; i++) {{
          const country = COUNTRY_POLYS[i];
          for (let j = 0; j < country.r.length; j++) {{
            const ring = country.r[j];
            if (!ring || ring.length < 3) continue;
            ctx.beginPath();
            let started = false;
            for (let k = 0; k < ring.length; k++) {{
              const p = project(ring[k][0], ring[k][1], r, cx, cy);
              if (p.front) {{
                if (!started) {{ ctx.moveTo(p.x, p.y); started = true; }}
                else ctx.lineTo(p.x, p.y);
              }}
            }}
            if (started) {{
              ctx.closePath();
              ctx.fillStyle = '#0a121e';
              ctx.fill();
              ctx.strokeStyle = '#14253c';
              ctx.lineWidth = 1.2;
              ctx.stroke();
            }}
          }}
        }}

        // 3. Subtle Ambient City Focus Spotlight
        const cityCenter = cityData && cityData.center ? cityData.center : [rotLon, rotLat];
        const cProj = project(cityCenter[0], cityCenter[1], r, cx, cy);
        if (cProj.front) {{
          const grad = ctx.createRadialGradient(cProj.x, cProj.y, 15, cProj.x, cProj.y, Math.max(width, height) * 0.65);
          grad.addColorStop(0, 'rgba(15, 30, 54, 0.40)');
          grad.addColorStop(0.5, 'rgba(10, 20, 36, 0.18)');
          grad.addColorStop(1, 'rgba(5, 10, 20, 0)');
          ctx.fillStyle = grad;
          ctx.fillRect(0, 0, width, height);
        }}

        // 4. Subtle City Watermark in Background
        if (activeCity) {{
          ctx.save();
          ctx.font = '700 48px "PP Telegraf", "PP Telegraph", sans-serif';
          ctx.fillStyle = 'rgba(148, 163, 184, 0.06)';
          ctx.textAlign = 'center';
          ctx.textBaseline = 'middle';
          ctx.fillText(activeCity.toUpperCase(), width / 2, Math.max(65, height * 0.16));
          ctx.restore();
        }}

        // 5. Curated Waterways (Only for real curated networks, zero text clutter)
        if (cityData && cityData.waterways && cityData.waterways.length > 0) {{
          ctx.save();
          cityData.waterways.forEach(w => {{
            if (!w.pts || w.pts.length < 2) return;
            ctx.beginPath();
            let started = false;
            w.pts.forEach(pt => {{
              const p = project(pt[0], pt[1], r, cx, cy);
              if (p.front) {{
                if (!started) {{ ctx.moveTo(p.x, p.y); started = true; }}
                else ctx.lineTo(p.x, p.y);
              }}
            }});
            if (started) {{
              ctx.lineCap = 'round';
              ctx.lineJoin = 'round';
              ctx.strokeStyle = '#081729';
              ctx.lineWidth = (w.width || 18) + 6;
              ctx.stroke();
              ctx.strokeStyle = '#0e2947';
              ctx.lineWidth = (w.width || 18);
              ctx.stroke();
            }}
          }});
          ctx.restore();
        }}

        // 6. Curated Parks (Only for real curated networks)
        if (cityData && cityData.parks && cityData.parks.length > 0) {{
          ctx.save();
          cityData.parks.forEach(park => {{
            if (!park.pts || park.pts.length < 3) return;
            ctx.beginPath();
            let started = false;
            park.pts.forEach(pt => {{
              const p = project(pt[0], pt[1], r, cx, cy);
              if (p.front) {{
                if (!started) {{ ctx.moveTo(p.x, p.y); started = true; }}
                else ctx.lineTo(p.x, p.y);
              }}
            }});
            if (started) {{
              ctx.closePath();
              ctx.fillStyle = '#0a1d15';
              ctx.fill();
              ctx.strokeStyle = '#143d26';
              ctx.lineWidth = 1;
              ctx.stroke();
            }}
          }});
          ctx.restore();
        }}

        // 7. Curated Major Arterial Streets (Only for real curated networks)
        if (cityData && cityData.major_streets && cityData.major_streets.length > 0) {{
          ctx.save();
          ctx.strokeStyle = '#182740';
          ctx.lineWidth = 1.8;
          ctx.lineCap = 'round';
          cityData.major_streets.forEach(s => {{
            if (!s.pts || s.pts.length < 2) return;
            ctx.beginPath();
            let started = false;
            s.pts.forEach(pt => {{
              const p = project(pt[0], pt[1], r, cx, cy);
              if (p.front) {{
                if (!started) {{ ctx.moveTo(p.x, p.y); started = true; }}
                else ctx.lineTo(p.x, p.y);
              }}
            }});
            if (started) ctx.stroke();
          });
          ctx.restore();
        }}

        // 8. Render City Cultural Institutions (Exact Pins & Anti-Collision Badges)
        cityMuseumHitboxes = [];
        const cityInsts = ALL_INSTITUTIONS.filter(i => matchC(i.city, activeCity));

        const projectedInsts = [];
        cityInsts.forEach(inst => {{
          const pt = project(inst.lon, inst.lat, r, cx, cy);
          if (pt.front) {{
            projectedInsts.push({{ inst, pt }});
          }}
        }});

        // First pass: render crisp pins & haloes
        projectedInsts.forEach(({{ inst, pt }}) => {{
          const isSel = selectedInstitution && selectedInstitution.name === inst.name;
          const isHov = hoveredInstitution && hoveredInstitution.name === inst.name;
          const tierColor = inst.tier === 'A' ? '#10b981' : inst.tier === 'B' ? '#3b82f6' : '#94a3b8';

          ctx.save();
          // Halo
          ctx.beginPath();
          ctx.arc(pt.x, pt.y, isSel ? 16 : isHov ? 12 : 8, 0, Math.PI * 2);
          ctx.fillStyle = isSel ? 'rgba(59, 130, 246, 0.25)' : inst.tier === 'A' ? 'rgba(16, 185, 129, 0.22)' : 'rgba(59, 130, 246, 0.20)';
          ctx.fill();

          // Stroke ring
          ctx.beginPath();
          ctx.arc(pt.x, pt.y, isSel ? 10 : isHov ? 8 : 6, 0, Math.PI * 2);
          ctx.strokeStyle = isSel ? '#ffffff' : tierColor;
          ctx.lineWidth = isSel ? 2 : 1.2;
          ctx.stroke();

          // Center solid dot
          ctx.beginPath();
          ctx.arc(pt.x, pt.y, isSel ? 5 : isHov ? 4.5 : 3.5, 0, Math.PI * 2);
          ctx.fillStyle = tierColor;
          ctx.fill();
          ctx.restore();
        }});

        // Second pass: position and render non-colliding callout badges
        // Sort by latitude descending (top-to-bottom on screen)
        projectedInsts.sort((a, b) => b.inst.lat - a.inst.lat);

        const placedBoxes = [];
        const bh = 36;

        projectedInsts.forEach(({{ inst, pt }}) => {{
          const isSel = selectedInstitution && selectedInstitution.name === inst.name;
          const isHov = hoveredInstitution && hoveredInstitution.name === inst.name;
          const tierColor = inst.tier === 'A' ? '#10b981' : inst.tier === 'B' ? '#3b82f6' : '#94a3b8';

          ctx.font = 'bold 12px "PP Telegraf", "PP Telegraph", sans-serif';
          const nameTxt = inst.name;
          const nw = ctx.measureText(nameTxt).width;

          const subTxt = inst.neighborhood || inst.curatorial_focus || (inst.tier === 'A' ? 'Verified Sanctuary' : 'Watch Space');
          ctx.font = '10px "PP Telegraf", "PP Telegraph", sans-serif';
          const sw = ctx.measureText(subTxt).width;

          const bw = Math.min(270, Math.max(160, Math.max(nw, sw) + 28));

          // Candidates to test
          const candidateOffsets = [
            {{ dx: 24, dy: -bh / 2 }},
            {{ dx: 24, dy: -bh - 10 }},
            {{ dx: 24, dy: 10 }},
            {{ dx: -bw - 24, dy: -bh / 2 }},
            {{ dx: -bw - 24, dy: -bh - 10 }},
            {{ dx: -bw - 24, dy: 10 }},
            {{ dx: -bw / 2, dy: -bh - 28 }},
            {{ dx: -bw / 2, dy: 28 }}
          ];

          let bestX = pt.x + 24;
          let bestY = pt.y - bh / 2;
          let foundClean = false;

          for (const slot of candidateOffsets) {{
            let candX = Math.max(16, Math.min(width - bw - 16, pt.x + slot.dx));
            let candY = Math.max(48, Math.min(height - bh - 48, pt.y + slot.dy));

            const collides = placedBoxes.some(box => {{
              return !(candX + bw + 12 < box.x || candX > box.x + box.w + 12 ||
                       candY + bh + 12 < box.y || candY > box.y + box.h + 12);
            }});

            if (!collides) {{
              bestX = candX;
              bestY = candY;
              foundClean = true;
              break;
            }}
          }}

          if (!foundClean && placedBoxes.length > 0) {{
            const lowest = placedBoxes.reduce((max, b) => (b.y + b.h > max.y + max.h ? b : max), placedBoxes[0]);
            bestX = Math.max(16, Math.min(width - bw - 16, pt.x + 24));
            bestY = Math.min(height - bh - 48, lowest.y + lowest.h + 10);
          }}

          placedBoxes.push({{ x: bestX, y: bestY, w: bw, h: bh }});

          // Leader line from pin to badge
          let attachX = bestX > pt.x ? bestX : bestX + bw;
          let attachY = bestY + bh / 2;

          ctx.save();
          ctx.beginPath();
          ctx.moveTo(pt.x, pt.y);
          ctx.lineTo(attachX, attachY);
          ctx.strokeStyle = isSel ? '#60a5fa' : isHov ? '#38bdf8' : 'rgba(56, 189, 248, 0.40)';
          ctx.lineWidth = isSel ? 1.5 : 1;
          ctx.stroke();
          ctx.restore();

          // Card Background
          ctx.save();
          ctx.fillStyle = isSel ? 'rgba(15, 23, 42, 0.97)' : isHov ? 'rgba(15, 23, 42, 0.94)' : 'rgba(10, 16, 28, 0.92)';
          ctx.beginPath();
          ctx.roundRect ? ctx.roundRect(bestX, bestY, bw, bh, 6) : ctx.rect(bestX, bestY, bw, bh);
          ctx.fill();

          ctx.strokeStyle = isSel ? '#60a5fa' : isHov ? '#38bdf8' : (inst.tier === 'A' ? 'rgba(16, 185, 129, 0.45)' : 'rgba(56, 189, 248, 0.35)');
          ctx.lineWidth = isSel ? 1.5 : 1;
          ctx.stroke();

          // Left tier accent bar
          ctx.fillStyle = tierColor;
          ctx.beginPath();
          ctx.roundRect ? ctx.roundRect(bestX, bestY, 3.5, bh, [6, 0, 0, 6]) : ctx.rect(bestX, bestY, 3.5, bh);
          ctx.fill();

          // Institution Name
          ctx.font = 'bold 12px "PP Telegraf", "PP Telegraph", sans-serif';
          ctx.fillStyle = isSel ? '#ffffff' : '#f8fafc';
          ctx.textAlign = 'left';
          ctx.textBaseline = 'top';
          ctx.fillText(nameTxt, bestX + 10, bestY + 5);

          // Subtitle
          ctx.beginPath();
          ctx.arc(bestX + 12, bestY + 23, 2, 0, Math.PI * 2);
          ctx.fillStyle = tierColor;
          ctx.fill();

          ctx.font = '10px "PP Telegraf", "PP Telegraph", sans-serif';
          ctx.fillStyle = '#94a3b8';
          ctx.fillText(subTxt, bestX + 18, bestY + 19);
          ctx.restore();

          cityMuseumHitboxes.push({{
            inst: inst,
            x: bestX,
            y: bestY,
            w: bw,
            h: bh,
            pinX: pt.x,
            pinY: pt.y
          }});
        }});
        
"""

assert part2_start in code, "part2_start not found"
assert part2_end in code, "part2_end not found"

z_idx1 = code.find(part2_start)
z_idx2 = code.find(part2_end)
code = code[:z_idx1] + new_part2 + code[z_idx2:]
print("Part 2 replaced successfully.")

with open('build_conversational_atlas.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("Saved updated build_conversational_atlas.py")
