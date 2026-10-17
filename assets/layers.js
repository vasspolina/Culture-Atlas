// Map layers drawn over the globe: funding ties, flagged spaces, the Clean Funding Grade, the money network, and the two highlights the funding
// map had: right-wing sponsors and the Epstein files.
// Each layer shows something at every zoom. Ties: the web of funders shared between spaces, the selected space's own
// ties on top. Flags: flagged spaces marked, and a flagged count on each city cluster. Money: a space's funders around
// its dot when it is selected, hovered or the view is close enough. Right and Epstein: a square on each space the
// funding map names, with the sponsor's or the person's name when the space is in focus or the view is close.
(function () {
  const L = window.atlasLayers = { ties: false, flags: false, grade: false, money: false, right: false, epstein: false, hq: false, people: false };
  const COL = { gov: '#8fa2ff', corp: '#a9e0e6', found: '#ff9966', flag: '#ff6119', right: '#ff5a4d', epstein: '#ec4fe8' };
  const RIGHT = n => typeof n[5] === 'string' && n[5].indexOf('right:') === 0;
  const epsteinOf = rec => (rec.ep || []).map(e => e.p).filter(Boolean).concat((rec.fl || []).indexOf('Epstein-linked') >= 0 && !(rec.ep || []).length ? ['Jeffrey Epstein'] : []);
  const FUNDER = n => n[1] === 'gov' || n[1] === 'corp' || n[1] === 'found';
  const rad = Math.PI / 180;
  let recById = null, keyIndex = null, keyKind = null, web = null, loading = false;
  let cityFlags = null;
  // Headquarters of the funders and offices of the people the funding map names (assets/hq.json, built by tools/build_hq.py).
  const KIND = { gov: COL.gov, corp: COL.corp, found: COL.found };
  let HQ = null, hqLoading = false;
  function loadHq() {
    if (HQ || hqLoading) return;
    hqLoading = true;
    fetch('assets/hq.json').then(r => r.json()).then(d => {
      const orgs = Object.entries(d.org).map(([key, o]) => Object.assign({ key, kind: 'org' }, o));
      const people = Object.entries(d.people).map(([name, o]) => Object.assign({ key: 'person:' + name, kind: 'person' }, o));
      // Pins are city-level, so entries in one city fan out around it instead of stacking.
      const byCity = new Map();
      orgs.concat(people).forEach(e => { const k = e.c; if (!byCity.has(k)) byCity.set(k, []); byCity.get(k).push(e); });
      byCity.forEach(list => list.forEach((e, i) => { const a = i * 2.39996, rr = i === 0 ? 0 : 8 + 5 * Math.sqrt(i); e.dx = Math.cos(a) * rr; e.dy = Math.sin(a) * rr; }));
      HQ = { orgs, people, byKey: new Map(orgs.map(o => [o.key, o])), byName: new Map(people.map(p => [p.n, p])) };
      hqLoading = false; updateCounts();
      if (typeof scheduleRender === 'function') scheduleRender();
    }).catch(() => { hqLoading = false; });
  }

  function loadMoney(cb) {
    if (recById) return cb && cb();
    if (loading) return;
    loading = true;
    fetch('assets/money-maps.json').then(r => r.json()).then(D => {
      recById = new Map(); keyIndex = new Map(); keyKind = new Map();
      D.forEach(rec => {
        recById.set(rec.id, rec);
        rec.nodes.forEach(n => {
          if (!FUNDER(n) || !n[5]) return;
          if (!keyIndex.has(n[5])) { keyIndex.set(n[5], []); keyKind.set(n[5], n[1]); }
          if (!keyIndex.get(n[5]).includes(rec.id)) keyIndex.get(n[5]).push(rec.id);
        });
      });
      // The web: one chain per funder named on two or more spaces, west to east, so every space is joined to its neighbour.
      web = [];
      keyIndex.forEach((ids, key) => {
        const recs = ids.map(id => recById.get(id)).filter(o => o && typeof o.lat === 'number').sort((a, b) => a.lon - b.lon);
        for (let i = 1; i < recs.length; i++) web.push([recs[i - 1], recs[i], keyKind.get(key), key]);
      });
      loading = false;
      updateCounts();
      if (cb) cb();
      if (typeof scheduleRender === 'function') scheduleRender();
    }).catch(() => { loading = false; });
  }

  function flaggedByCity() {
    if (cityFlags) return cityFlags;
    cityFlags = new Map();
    if (typeof ALL_INSTITUTIONS === 'undefined') return cityFlags;
    ALL_INSTITUTIONS.forEach(i => {
      if (!i.flags || !i.flags.length || !i.city) return;
      const k = i.city.toLowerCase().trim();
      cityFlags.set(k, (cityFlags.get(k) || 0) + 1);
    });
    return cityFlags;
  }

  function vec(lat, lon) { const p = lat * rad, l = lon * rad; return [Math.cos(p) * Math.sin(l), Math.sin(p), Math.cos(p) * Math.cos(l)]; }
  function arc(project, a, b, r, cx, cy, ctx) {
    const va = vec(a.lat, a.lon), vb = vec(b.lat, b.lon);
    const dot = Math.max(-1, Math.min(1, va[0] * vb[0] + va[1] * vb[1] + va[2] * vb[2])), om = Math.acos(dot);
    if (om < 1e-5) return false;
    const so = Math.sin(om), N = Math.max(8, Math.ceil(om * 36));
    ctx.beginPath(); let pen = false, drawn = false;
    for (let i = 0; i <= N; i++) {
      const t = i / N, k1 = Math.sin((1 - t) * om) / so, k2 = Math.sin(t * om) / so;
      const x = k1 * va[0] + k2 * vb[0], y = k1 * va[1] + k2 * vb[1], z = k1 * va[2] + k2 * vb[2];
      const lat = Math.atan2(y, Math.hypot(x, z)) / rad, lon = Math.atan2(x, z) / rad;
      const pt = project(lon, lat, r * (1 + 0.12 * Math.sin(Math.PI * t) * Math.min(1, om)), cx, cy);
      if (!pt.front) { pen = false; continue; }
      if (pen) { ctx.lineTo(pt.x, pt.y); drawn = true; } else { ctx.moveTo(pt.x, pt.y); pen = true; }
    }
    if (drawn) ctx.stroke();
    return drawn;
  }

  const sameInst = (a, b) => !!a && !!b && (a.id ? a.id === b.id : a.name === b.name);

  // Under the dots: the funding ties.
  window.atlasLayersDraw = function (ctx, project, r, cx, cy, list, sel, hov, baseRadius) {
    if (!L.ties) return;
    if (!recById) { loadMoney(); return; }
    const focus = hov || sel, rec = focus && recById.get(focus.id);
    ctx.save();
    ctx.lineCap = 'round';
    // The whole web, faint when a space is in focus.
    ctx.lineWidth = 0.8;
    // The whole web is a world-view picture: with a space in focus, or zoomed in, only that space's own ties are drawn.
    const showWeb = !rec && r < baseRadius * 8;
    ctx.globalAlpha = 0.35;
    const W = ctx.canvas.clientWidth || 1e9, H = ctx.canvas.clientHeight || 1e9;
    if (showWeb) web.forEach(([a, b, kind]) => {
      const pa = project(a.lon, a.lat, r, cx, cy), pb = project(b.lon, b.lat, r, cx, cy);
      if (!pa.front && !pb.front) return;
      if ((pa.x < -W || pa.x > 2 * W) && (pb.x < -W || pb.x > 2 * W)) return;
      if ((pa.y < -H || pa.y > 2 * H) && (pb.y < -H || pb.y > 2 * H)) return;
      ctx.strokeStyle = COL[kind];
      arc(project, a, b, r, cx, cy, ctx);
    });
    // The focused space's own ties, bright, with a dot at each far end.
    if (rec && typeof rec.lat === 'number') {
      ctx.lineWidth = 1.4; ctx.globalAlpha = 0.8;
      const seen = new Set([rec.id]), ends = [];
      rec.nodes.forEach(n => {
        if (!FUNDER(n) || !n[5]) return;
        (keyIndex.get(n[5]) || []).forEach(id => {
          if (seen.has(id) || seen.size > 400) return; seen.add(id);
          const o = recById.get(id); if (!o || typeof o.lat !== 'number') return;
          ctx.strokeStyle = COL[n[1]];
          arc(project, rec, o, r, cx, cy, ctx); ends.push([o, COL[n[1]]]);
        });
      });
      ctx.globalAlpha = 1;
      ends.forEach(([o, col]) => { const pt = project(o.lon, o.lat, r, cx, cy); if (!pt.front) return; ctx.beginPath(); ctx.arc(pt.x, pt.y, 3.5, 0, Math.PI * 2); ctx.fillStyle = col; ctx.fill(); });
    }
    ctx.restore();
  };

  // A box collides with any of the label boxes already on screen (city pills, museum pills, our own labels).
  function collides(box, boxes) {
    return boxes.some(o => !(box.x + box.w < o.x || box.x > o.x + o.w || box.y + box.h < o.y || box.y > o.y + o.h));
  }
  function labelBoxesOnScreen(dots) {
    const out = [];
    if (typeof cityBadgeHitboxes !== 'undefined' && Array.isArray(cityBadgeHitboxes)) cityBadgeHitboxes.forEach(b => out.push({ x: b.x, y: b.y, w: b.w, h: b.h }));
    dots.forEach(d => { if (d.labelBox) out.push(d.labelBox); });
    return out;
  }

  // Over the dots and labels: flag marks and the money network.
  // A square on each space the funding map names for this highlight, and its names on blocks when in focus or close.
  function drawHighlight(ctx, project, r, baseRadius, cx, cy, sel, hov, boxes, col, namesOf, dx) {
    const close = r >= baseRadius * 22;
    const marks = [];
    recById.forEach(rec => {
      const names = namesOf(rec); if (!names.length || typeof rec.lat !== 'number') return;
      const pt = project(rec.lon, rec.lat, r, cx, cy); if (!pt.front) return;
      const focus = (sel && sel.id === rec.id) || (hov && hov.id === rec.id);
      marks.push([pt, names, focus]);
    });
    ctx.lineWidth = 0.8;
    marks.forEach(([pt]) => { ctx.fillStyle = col; ctx.fillRect(pt.x - 6 + dx, pt.y - 6, 12, 12); ctx.strokeStyle = '#000'; ctx.strokeRect(pt.x - 6 + dx, pt.y - 6, 12, 12); });
    ctx.textAlign = 'left';
    marks.forEach(([pt, names, focus]) => {
      if (!(focus || close)) return;
      let y = pt.y - 10 - (names.length - 1) * 11;
      names.slice(0, 4).forEach(name => {
        const text = name.length > 28 ? name.slice(0, 26) + '…' : name, tw = ctx.measureText(text).width, w = tw + 12, h = 20;
        const box = { x: pt.x + 10 + dx, y: y - h / 2, w, h };
        if (!collides(box, boxes)) { boxes.push(box); ctx.fillStyle = col; ctx.fillRect(box.x, box.y, w, h); ctx.fillStyle = '#000'; ctx.fillText(text, box.x + 6, y + 0.5); }
        y += 22;
      });
    });
  }


  // Headquarters and offices: a diamond for each funder's head office, a circle for each person's office; the focused
  // space is joined to the head offices of its funders, and to the people the Epstein files tie to it.
  function drawHq(ctx, project, r, baseRadius, cx, cy, sel, hov, boxes) {
    if (!HQ) return;
    const focus = hov || sel, rec = focus && recById && recById.get(focus.id);
    const linkedOrgs = new Set(), linkedPeople = new Set();
    if (rec) {
      rec.nodes.forEach(n => { if (n[5] && HQ.byKey.has(n[5])) linkedOrgs.add(n[5]); });
      (rec.ep || []).forEach(e => { if (e.p && HQ.byName.has(e.p)) linkedPeople.add(e.p); });
    }
    const pts = [];
    const place = (e, show) => {
      if (!show) return;
      const pt = project(e.lon, e.lat, r, cx, cy); if (!pt.front) return;
      pts.push([e, pt.x + e.dx, pt.y + e.dy]);
    };
    if (L.hq) HQ.orgs.forEach(e => place(e, true));
    if (L.people) HQ.people.forEach(e => place(e, true));
    // joins from the focused space
    if (rec && typeof rec.lat === 'number') {
      ctx.lineWidth = 1.2; ctx.globalAlpha = 0.85;
      if (L.hq) linkedOrgs.forEach(k => { const o = HQ.byKey.get(k); ctx.strokeStyle = KIND[o.k]; arc(project, rec, o, r, cx, cy, ctx); });
      if (L.people) linkedPeople.forEach(n => { const o = HQ.byName.get(n); ctx.strokeStyle = COL.epstein; arc(project, rec, o, r, cx, cy, ctx); });
      ctx.globalAlpha = 1;
    }
    // marks
    ctx.lineWidth = 1;
    pts.forEach(([e, x, y]) => {
      const on = e.kind === 'org' ? linkedOrgs.has(e.key) : linkedPeople.has(e.n);
      const s = on ? 7 : (rec ? 3.5 : 5);
      ctx.globalAlpha = rec && !on ? 0.35 : 1;
      ctx.fillStyle = e.kind === 'org' ? KIND[e.k] : COL.epstein; ctx.strokeStyle = '#000';
      ctx.beginPath();
      if (e.kind === 'org') { ctx.moveTo(x, y - s); ctx.lineTo(x + s, y); ctx.lineTo(x, y + s); ctx.lineTo(x - s, y); ctx.closePath(); }
      else ctx.arc(x, y, s - 0.5, 0, Math.PI * 2);
      ctx.fill(); ctx.stroke();
    });
    ctx.globalAlpha = 1;
    // Names: on blocks for the focused space's own funders and people. With nothing in focus, only a very close view names them,
    // as plain text on a halo, so the map is not covered in blocks.
    const veryClose = !rec && r >= baseRadius * 30;
    ctx.textAlign = 'left'; ctx.textBaseline = 'middle';
    pts.forEach(([e, x, y]) => {
      const on = e.kind === 'org' ? linkedOrgs.has(e.key) : linkedPeople.has(e.n);
      if (!(on || veryClose)) return;
      const text = e.kind === 'org' ? (on ? `${e.n}, ${e.c}` : e.n) : `${e.n}, ${e.w}`, t = text.length > 40 ? text.slice(0, 38) + '…' : text;
      const tw = ctx.measureText(t).width, w = tw + 12, h = 20, box = { x: x + 10, y: y - h / 2, w, h };
      if (collides(box, boxes)) return;
      boxes.push(box);
      if (on) { ctx.fillStyle = e.kind === 'org' ? KIND[e.k] : COL.epstein; ctx.fillRect(box.x, box.y, w, h); ctx.fillStyle = '#000'; ctx.fillText(t, box.x + 6, y + 0.5); }
      else { ctx.lineJoin = 'round'; ctx.lineWidth = 3; ctx.strokeStyle = document.documentElement.getAttribute('data-theme') === 'dark' ? '#000' : '#fff'; ctx.strokeText(t, box.x + 6, y + 0.5); ctx.fillStyle = document.documentElement.getAttribute('data-theme') === 'dark' ? '#fff' : '#161616'; ctx.fillText(t, box.x + 6, y + 0.5); }
    });
  }

  window.atlasLayersDrawNodes = function (ctx, dots, r, baseRadius, sel, hov, gossip, project, cx, cy) {
    if (!L.flags && !L.grade && !L.money && !L.right && !L.epstein && !L.hq && !L.people) return;
    if ((L.money || L.right || L.epstein || L.hq || L.people) && !recById) loadMoney();
    if ((L.hq || L.people) && !HQ) loadHq();
    const dark = document.documentElement.getAttribute('data-theme') === 'dark';
    const font = '14px "PP Neue Gstaad", sans-serif';
    const boxes = labelBoxesOnScreen(dots);
    ctx.save();
    ctx.font = font; ctx.textBaseline = 'middle';

    if (L.grade) {
      // Each graded space: a dot filled with its Clean Funding Grade colour (window.atlasGrade, set by the page).
      // A space with no grade keeps its hollow ring.
      const G = window.atlasGrade || {};
      ctx.lineWidth = 0.8;
      dots.forEach(d => {
        const i = d.inst; if (!i || !i.grade || !G[i.grade]) return;
        ctx.beginPath(); ctx.arc(d.x, d.y, 5, 0, Math.PI * 2);
        ctx.fillStyle = G[i.grade].col; ctx.fill();
        ctx.strokeStyle = '#000'; ctx.stroke();
      });
    }
    if (L.flags) {
      // Each flagged space: a filled orange dot over its ring.
      ctx.lineWidth = 0.8;
      dots.forEach(d => {
        const i = d.inst; if (!i || !i.flags || !i.flags.length) return;
        ctx.beginPath(); ctx.arc(d.x, d.y, 5, 0, Math.PI * 2);
        ctx.fillStyle = COL.flag; ctx.fill();
        ctx.strokeStyle = '#000'; ctx.stroke();
      });
      // Each city cluster: the number of flagged spaces in it, on an orange block after the city's label.
      if (typeof cityBadgeHitboxes !== 'undefined' && Array.isArray(cityBadgeHitboxes)) {
        const byCity = flaggedByCity();
        ctx.textAlign = 'left';
        cityBadgeHitboxes.forEach(b => {
          if (!(b.count >= 2)) return;
          const n = byCity.get((b.name || '').toLowerCase().trim()); if (!n) return;
          const text = String(n), tw = ctx.measureText(text).width, w = tw + 12, h = b.h;
          const x = b.x + b.w + 2, y = b.y;
          ctx.fillStyle = COL.flag; ctx.fillRect(x, y, w, h);
          ctx.fillStyle = '#000'; ctx.fillText(text, x + 6, y + h / 2 + 0.5);
          boxes.push({ x, y, w, h });
        });
      }
    }

    // Both highlights on: the Epstein square sits to the right of the right-wing one, so a space in both shows both.
    if (L.right && recById) drawHighlight(ctx, project, r, baseRadius, cx, cy, sel, hov, boxes, COL.right, rec => rec.nodes.filter(RIGHT).map(n => n[0]), L.epstein ? -7 : 0);
    if (L.epstein && recById) drawHighlight(ctx, project, r, baseRadius, cx, cy, sel, hov, boxes, COL.epstein, epsteinOf, L.right ? 7 : 0);

    if (L.hq || L.people) drawHq(ctx, project, r, baseRadius, cx, cy, sel, hov, boxes);

    if (L.money) {
      if (!recById) { ctx.restore(); return; }
      const byKey = new Map(), labels = [];
      // A selected space with no dot of its own (folded into a cluster) still gets its funders.
      if (sel && typeof sel.lat === 'number' && typeof sel.lon === 'number' && !dots.some(d => sameInst(d.inst, sel))) {
        const pt = project(sel.lon, sel.lat, r, cx, cy); if (pt.front) dots = dots.concat([{ inst: sel, x: pt.x, y: pt.y }]);
      }
      ctx.lineWidth = 0.8;
      dots.forEach(d => {
        const inst = d.inst, rec = inst && recById.get(inst.id); if (!rec) return;
        const focus = sameInst(sel, inst) || sameInst(hov, inst);
        if (!focus) return;
        const nodes = rec.nodes.filter(FUNDER);
        if (!nodes.length) return;
        // The ring is 64 px when the view is close; further out it shrinks, so funders never land on other cities.
        const zoomK = Math.max(0.4, Math.min(1, r / (baseRadius * 12)));
        const N = Math.min(nodes.length, focus ? 10 : 6), R = (focus ? 64 : 36) * zoomK;
        for (let i = 0; i < N; i++) {
          const n = nodes[i], a = -Math.PI / 2 + (i * 2 * Math.PI) / N, x = d.x + R * Math.cos(a), y = d.y + R * Math.sin(a);
          const col = gossip ? '#ffd600' : COL[n[1]];
          ctx.globalAlpha = focus ? 1 : 0.7;
          ctx.strokeStyle = col; ctx.beginPath(); ctx.moveTo(d.x, d.y); ctx.lineTo(x, y); ctx.stroke();
          ctx.beginPath(); ctx.arc(x, y, 5, 0, Math.PI * 2); ctx.fillStyle = dark ? '#000' : '#fff'; ctx.fill(); ctx.stroke();
          if (n[5]) { if (!byKey.has(n[5])) byKey.set(n[5], []); byKey.get(n[5]).push([x, y, col]); }
          labels.push([n[0], x, y, a, col]);
        }
      });
      // A funder named on two spaces on screen is joined across them.
      ctx.globalAlpha = 0.55;
      const W = ctx.canvas.clientWidth || 1e9, H = ctx.canvas.clientHeight || 1e9, onScreen = p => p[0] > -40 && p[0] < W + 40 && p[1] > -40 && p[1] < H + 40;
      byKey.forEach(pts => { pts = pts.filter(onScreen); for (let i = 1; i < pts.length; i++) { ctx.strokeStyle = pts[i][2]; ctx.beginPath(); ctx.moveTo(pts[0][0], pts[0][1]); ctx.lineTo(pts[i][0], pts[i][1]); ctx.stroke(); } });
      // Funder names on flat blocks, in the funder's colour, never over another label.
      ctx.globalAlpha = 1;
      labels.forEach(([label, x, y, a, col]) => {
        const text = label.length > 28 ? label.slice(0, 26) + '…' : label, right = Math.cos(a) >= -0.2;
        const tw = ctx.measureText(text).width, w = tw + 12, h = 20;
        const bx = right ? x + 9 : x - 9 - w, box = { x: bx, y: y - h / 2, w, h };
        if (collides(box, boxes)) return;
        boxes.push(box);
        ctx.fillStyle = col; ctx.fillRect(box.x, box.y, w, h);
        ctx.fillStyle = '#000'; ctx.textAlign = 'left'; ctx.fillText(text, box.x + 6, y + 0.5);
      });
    }
    ctx.restore();
  };

  // "Money map" on a record: turn the layers on and show that space's funders on the globe.
  window.atlasShowMoney = function (id) {
    L.money = true; L.ties = true; loadMoney();
    document.querySelectorAll('#layersPanel input[data-layer]').forEach(i => { if (i.dataset.layer === 'money' || i.dataset.layer === 'ties') i.checked = true; });
    if (typeof window.exitCityStreetView === 'function') { try { window.exitCityStreetView(); } catch (e) {} }
    const inst = id && typeof window.resolveInstitutionByIdOrName === 'function' ? window.resolveInstitutionByIdOrName(id) : null;
    if (id && typeof window.selectInstitution === 'function') window.selectInstitution(id, false);
    // On a phone the record sheet would cover the funders; it steps aside, and a tap on the space brings it back.
    if (window.innerWidth < 768) { const sheet = document.getElementById('dossier-bottom-sheet'); if (sheet) sheet.classList.add('hidden'); if (typeof window.setActiveMobileTab === 'function') window.setActiveMobileTab('atlas'); }
    // Close in on the space, so its funders sit around it in its own city rather than across the continent.
    if (inst && typeof inst.lat === 'number' && typeof inst.lon === 'number' && typeof window.flyTo === 'function' && typeof window.getMaxRadius === 'function') {
      const z = window.getMaxRadius();
      if (typeof window.setTargetRadius === 'function') window.setTargetRadius(z);
      window.flyTo(inst.lon, inst.lat, z);
    }
    if (typeof scheduleRender === 'function') scheduleRender();
  };

  // What each layer holds, as a count after its name.
  function updateCounts() {
    const set = (k, text) => { const el = document.querySelector(`#layersPanel [data-count="${k}"]`); if (el) el.textContent = text; };
    if (typeof ALL_INSTITUTIONS !== 'undefined') {
      set('spaces', String(ALL_INSTITUTIONS.length));
      set('flags', String(ALL_INSTITUTIONS.filter(i => i.flags && i.flags.length).length));
      const graded = ALL_INSTITUTIONS.filter(i => i.grade).length;
      set('grade', `${graded} graded, ${ALL_INSTITUTIONS.length - graded} not graded`);
    }
    if (HQ) {
      set('hq', `${HQ.orgs.length} head offices in ${new Set(HQ.orgs.map(o => o.c)).size} cities`);
      set('people', `${HQ.people.length} offices of people named in the records`);
    }
    if (web) {
      set('ties', `${web.length} links, ${[...keyIndex.values()].filter(ids => ids.length >= 2).length} shared funders`);
      set('money', `${[...recById.values()].filter(rec => rec.nodes.some(FUNDER)).length} spaces with funders named`);
      const rightRecs = [...recById.values()].filter(rec => rec.nodes.some(RIGHT)), rightKeys = new Set();
      rightRecs.forEach(rec => rec.nodes.filter(RIGHT).forEach(n => rightKeys.add(n[5])));
      set('right', `${rightRecs.length} spaces, ${rightKeys.size} sponsors`);
      set('epstein', `${[...recById.values()].filter(rec => epsteinOf(rec).length).length} spaces`);
    }
  }

  function init() {
    const box = document.getElementById('layersControl'); if (!box) return;
    const btn = box.querySelector('#layersBtn'), panel = box.querySelector('#layersPanel');
    const setOpen = open => { panel.hidden = !open; btn.setAttribute('aria-expanded', String(open)); };
    btn.addEventListener('click', () => setOpen(panel.hidden));
    document.addEventListener('click', e => { if (!panel.hidden && !box.contains(e.target)) setOpen(false); });
    document.addEventListener('keydown', e => { if (e.key === 'Escape' && !panel.hidden) setOpen(false); });
    box.querySelectorAll('input[data-layer]').forEach(inp => inp.addEventListener('change', () => {
      const k = inp.dataset.layer;
      L[k] = inp.checked;
      if (k !== 'flags' && k !== 'grade' && inp.checked) loadMoney();
      if ((k === 'hq' || k === 'people') && inp.checked) loadHq();
      if (typeof scheduleRender === 'function') scheduleRender();
    }));
    updateCounts();
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
