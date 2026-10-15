// Map layers drawn over the globe: funding ties, flagged spaces, and the money network.
(function () {
  const L = window.atlasLayers = { ties: false, flags: false, money: false };
  const TIE_COL = { gov: '#8fa2ff', corp: '#a9e0e6', found: '#ff9966', flag: '#ec4fe8' };
  const rad = Math.PI / 180;
  let recById = null, keyIndex = null, loading = false, lastFrameId = null;

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
  setInterval(() => {
    if (!L.money) return;
    const f = document.getElementById('moneyLayerFrame'), cur = window.atlasGetSelected && window.atlasGetSelected(), id = cur && cur.id ? cur.id : 'all';
    if (f && id !== lastFrameId) { lastFrameId = id; try { f.contentWindow.location.hash = '#' + encodeURIComponent(id); } catch (e) {} }
  }, 400);

  function setMoney(on) {
    L.money = on;
    const vp = document.getElementById('globeViewport'); let f = document.getElementById('moneyLayerFrame');
    if (on && !f) {
      f = document.createElement('iframe'); f.id = 'moneyLayerFrame'; f.title = 'Money network';
      const cur = window.atlasGetSelected && window.atlasGetSelected(); lastFrameId = (cur && cur.id) || 'all';
      f.src = 'money-maps.html?embed&theme=' + (document.documentElement.getAttribute('data-theme') === 'dark' ? 'dark' : 'light') + '#' + encodeURIComponent(lastFrameId);
      vp.appendChild(f);
    }
    if (f) f.hidden = !on;
  }

  window.atlasLayersTheme = function (t) {
    const f = document.getElementById('moneyLayerFrame'); if (!f) return;
    try { f.contentWindow.postMessage({ atlasTheme: t }, '*'); } catch (e) {}
  };

  function init() {
    const box = document.getElementById('layersControl'); if (!box) return;
    const btn = box.querySelector('#layersBtn'), panel = box.querySelector('#layersPanel');
    btn.addEventListener('click', () => { const open = panel.hidden; panel.hidden = !open; btn.setAttribute('aria-expanded', String(open)); });
    box.querySelectorAll('input[data-layer]').forEach(inp => inp.addEventListener('change', () => {
      const k = inp.dataset.layer;
      if (k === 'money') setMoney(inp.checked); else L[k] = inp.checked;
      if (k === 'ties' && inp.checked) loadMoney();
      if (typeof scheduleRender === 'function') scheduleRender();
    }));
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
