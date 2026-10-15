// Map layers drawn over the globe: funding ties, flagged spaces, and the money network.
(function () {
  const L = window.atlasLayers = { ties: false, flags: false, money: false };
  const TIE_COL = { gov: '#8fa2ff', corp: '#a9e0e6', found: '#ff9966', flag: '#ec4fe8' };
  const rad = Math.PI / 180;
  let recById = null, keyIndex = null, loading = false;

  function loadMoney(cb) {
    if (recById) return cb && cb();
    if (loading) return;
    loading = true;
    fetch('assets/money-maps.json').then(r => r.json()).then(D => {
      recById = new Map(); keyIndex = new Map();
      D.forEach(rec => {
        recById.set(rec.id, rec);
        rec.nodes.forEach(n => {
          if (!(n[1] === 'gov' || n[1] === 'corp' || n[1] === 'found') || !n[5]) return;
          if (!keyIndex.has(n[5])) keyIndex.set(n[5], []);
          keyIndex.get(n[5]).push(rec.id);
        });
      });
      loading = false;
      if (cb) cb();
      if (typeof scheduleRender === 'function') scheduleRender();
    }).catch(() => { loading = false; });
  }

  function vec(lat, lon) { const p = lat * rad, l = lon * rad; return [Math.cos(p) * Math.sin(l), Math.sin(p), Math.cos(p) * Math.cos(l)]; }
  function arc(project, a, b, r, cx, cy, ctx, col) {
    const va = vec(a.lat, a.lon), vb = vec(b.lat, b.lon);
    const dot = Math.max(-1, Math.min(1, va[0] * vb[0] + va[1] * vb[1] + va[2] * vb[2])), om = Math.acos(dot);
    if (om < 1e-4) return;
    const so = Math.sin(om), N = Math.max(12, Math.ceil(om * 40));
    ctx.beginPath(); let pen = false;
    for (let i = 0; i <= N; i++) {
      const t = i / N, k1 = Math.sin((1 - t) * om) / so, k2 = Math.sin(t * om) / so;
      const x = k1 * va[0] + k2 * vb[0], y = k1 * va[1] + k2 * vb[1], z = k1 * va[2] + k2 * vb[2];
      const lat = Math.atan2(y, Math.hypot(x, z)) / rad, lon = Math.atan2(x, z) / rad;
      const pt = project(lon, lat, r * (1 + 0.16 * Math.sin(Math.PI * t) * Math.min(1, om)), cx, cy);
      if (!pt.front) { pen = false; continue; }
      if (pen) ctx.lineTo(pt.x, pt.y); else { ctx.moveTo(pt.x, pt.y); pen = true; }
    }
    ctx.strokeStyle = col; ctx.stroke();
  }

  window.atlasLayersDraw = function (ctx, project, r, cx, cy, list, sel, hov) {
    if (L.flags) {
      ctx.save(); ctx.lineWidth = 1.4; ctx.strokeStyle = '#ec4fe8'; ctx.fillStyle = 'rgba(236,79,232,.28)';
      list.forEach(i => {
        if (!i.flags || !i.flags.length || typeof i.lat !== 'number' || typeof i.lon !== 'number') return;
        const pt = project(i.lon, i.lat, r, cx, cy); if (!pt.front) return;
        ctx.beginPath(); ctx.arc(pt.x, pt.y, 7, 0, Math.PI * 2); ctx.fill(); ctx.stroke();
      });
      ctx.restore();
    }
    if (L.ties) {
      if (!recById) { loadMoney(); }
      else {
        const inst = hov || sel, rec = inst && recById.get(inst.id);
        if (rec && typeof rec.lat === 'number') {
          ctx.save(); ctx.lineWidth = 1.2; ctx.globalAlpha = 0.75;
          const seen = new Set([rec.id]), ends = [];
          rec.nodes.forEach(n => {
            if (!(n[1] === 'gov' || n[1] === 'corp' || n[1] === 'found') || !n[5]) return;
            (keyIndex.get(n[5]) || []).forEach(id => {
              if (seen.has(id) || seen.size > 400) return; seen.add(id);
              const o = recById.get(id); if (!o || typeof o.lat !== 'number') return;
              arc(project, rec, o, r, cx, cy, ctx, TIE_COL[n[1]]); ends.push([o, TIE_COL[n[1]]]);
            });
          });
          ctx.globalAlpha = 1;
          ends.forEach(([o, col]) => { const pt = project(o.lon, o.lat, r, cx, cy); if (!pt.front) return; ctx.beginPath(); ctx.arc(pt.x, pt.y, 3.2, 0, Math.PI * 2); ctx.fillStyle = col; ctx.fill(); });
          const home = project(rec.lon, rec.lat, r, cx, cy);
          if (home.front) { ctx.beginPath(); ctx.arc(home.x, home.y, 5, 0, Math.PI * 2); ctx.fillStyle = '#fff'; ctx.fill(); }
          ctx.restore();
        }
      }
    }
  };

  // Money network on the globe: each space's funders sit around its dot; a funder named on several spaces is joined across them.
  window.atlasLayersDrawNodes = function (ctx, dots, r, baseRadius, sel, hov, gossip, project, cx, cy) {
    if (!L.money) return;
    if (!recById) { loadMoney(); return; }
    const zoomAll = r >= baseRadius * 22, deep = r >= baseRadius * 40, dark = document.documentElement.getAttribute('data-theme') === 'dark';
    const byKey = new Map(), active = [];
    const font = '14px "PP Neue Gstaad", sans-serif';
    // a selected space with no dot of its own (no city on record, or folded into a cluster) still gets its funders
    if (sel && typeof sel.lat === 'number' && typeof sel.lon === 'number' && !dots.some(d => d.inst && d.inst.name === sel.name)) {
      const pt = project(sel.lon, sel.lat, r, cx, cy); if (pt.front) dots = dots.concat([{ inst: sel, x: pt.x, y: pt.y }]);
    }
    ctx.save();
    ctx.lineWidth = 1;
    dots.forEach(d => {
      const inst = d.inst, rec = inst && recById.get(inst.id); if (!rec) return;
      const isSel = sel && sel.name === inst.name, isHov = hov && hov.name === inst.name;
      if (!(zoomAll || isSel || isHov)) return;
      const nodes = rec.nodes.filter(n => n[1] === 'gov' || n[1] === 'corp' || n[1] === 'found' || n[1] === 'flag');
      if (!nodes.length) return;
      const N = Math.min(nodes.length, isSel || isHov ? 10 : 6), R = isSel || isHov ? 44 : 30;
      for (let i = 0; i < N; i++) {
        const n = nodes[i], a = -Math.PI / 2 + (i * 2 * Math.PI) / N, x = d.x + R * Math.cos(a), y = d.y + R * Math.sin(a);
        const col = gossip ? '#ffd600' : TIE_COL[n[1]] || '#fff';
        ctx.globalAlpha = isSel || isHov ? 1 : 0.7;
        ctx.strokeStyle = col; ctx.beginPath(); ctx.moveTo(d.x, d.y); ctx.lineTo(x, y); ctx.stroke();
        ctx.beginPath(); ctx.arc(x, y, n[1] === 'flag' ? 4 : 5, 0, Math.PI * 2);
        if (n[1] === 'flag') { ctx.fillStyle = col; ctx.fill(); } else { ctx.stroke(); }
        if (n[5]) { if (!byKey.has(n[5])) byKey.set(n[5], []); byKey.get(n[5]).push([x, y, col]); }
        if (isSel || isHov || deep) active.push([n[0], x, y, a]);
      }
    });
    ctx.globalAlpha = 0.55;
    const W = ctx.canvas.clientWidth || 1e9, H = ctx.canvas.clientHeight || 1e9, onScreen = p => p[0] > -40 && p[0] < W + 40 && p[1] > -40 && p[1] < H + 40;
    byKey.forEach(pts => { pts = pts.filter(onScreen); for (let i = 1; i < pts.length; i++) { ctx.strokeStyle = pts[i][2]; ctx.beginPath(); ctx.moveTo(pts[0][0], pts[0][1]); ctx.lineTo(pts[i][0], pts[i][1]); ctx.stroke(); } });
    ctx.globalAlpha = 1; ctx.font = font; ctx.textBaseline = 'middle'; ctx.lineJoin = 'round';
    const boxes = [];
    active.forEach(([label, x, y, a]) => {
      const text = label.length > 28 ? label.slice(0, 26) + '…' : label, right = Math.cos(a) >= -0.2;
      ctx.textAlign = right ? 'left' : 'right';
      const tx = x + (right ? 9 : -9), tw = ctx.measureText(text).width, bx = right ? tx : tx - tw, box = [bx - 2, y - 9, tw + 4, 18];
      if (boxes.some(o => !(box[0] + box[2] < o[0] || box[0] > o[0] + o[2] || box[1] + box[3] < o[1] || box[1] > o[1] + o[3]))) return;
      boxes.push(box);
      ctx.strokeStyle = '#000'; ctx.lineWidth = 3; ctx.strokeText(text, tx, y);
      ctx.fillStyle = '#fff'; ctx.fillText(text, tx, y);
    });
    ctx.restore();
  };

  function init() {
    const box = document.getElementById('layersControl'); if (!box) return;
    const btn = box.querySelector('#layersBtn'), panel = box.querySelector('#layersPanel');
    btn.addEventListener('click', () => { const open = panel.hidden; panel.hidden = !open; btn.setAttribute('aria-expanded', String(open)); });
    box.querySelectorAll('input[data-layer]').forEach(inp => inp.addEventListener('change', () => {
      const k = inp.dataset.layer;
      L[k] = inp.checked;
      if ((k === 'ties' || k === 'money') && inp.checked) loadMoney();
      if (typeof scheduleRender === 'function') scheduleRender();
    }));
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
