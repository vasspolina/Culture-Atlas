// Map layers drawn over the globe: funding connections, flagged organizations, funding transparency ratings, funder networks,
// and the two highlights the funding map had: right-wing funders and mentions in the Epstein files.
// Funding mix: a ring on each space split by the kinds of funder it has. Funder types: a filter on all the funder layers.
// Hovering a funder around a space draws everywhere else it funds. Each layer shows something at every zoom. Ties: the web of funders shared between spaces, the selected space's own
// ties on top. Flags: flagged spaces marked, and a flagged count on each city cluster. Money: a space's funders around
// its dot when it is selected, hovered or the view is close enough. Right and Epstein: a square on each space the
// funding map names, with the sponsor's or the person's name when the space is in focus or the view is close.
(function () {
  const L = window.atlasLayers = { ties: false, flags: false, grade: false, money: false, mix: false, right: false, epstein: false, hq: false, people: false, kinds: { gov: true, corp: true, found: true } };
  const COL = { gov: '#818cf8', corp: '#38bdf8', found: '#f472b6', flag: '#f59e0b', right: '#fb7185', epstein: '#a78bfa', person: '#e5e7eb' };
  // The pale colours above are the fills of the name blocks (black text on them is 7:1 or better) and read on the black
  // ground of dark mode. On the white ground of light mode they measure 1.2 to 3:1, so the lines, rings and dots that carry
  // the data are drawn in a deeper step of the same hue there: 3.05:1 or better against white at the 0.8 alpha they are drawn at.
  const LINE_LIGHT = { '#818cf8': '#5e6cf6', '#38bdf8': '#0785bd', '#f472b6': '#ef3295', '#f59e0b': '#ab6e07', '#fb7185': '#f93451', '#a78bfa': '#865ff8', '#e5e7eb': '#6e798f', '#22d3ee': '#0c889b', '#ffd600': '#8f7800', '#e2f86c': '#6b8a00' };
  const lineCol = c => (document.documentElement.getAttribute('data-theme') === 'dark' ? c : (LINE_LIGHT[c] || c));
  // Colour is never the only cue (WCAG 1.4.1): each kind of mark has its own outline, the same ones the key in the layers panel shows.
  const SHAPES = {
    square: null,
    hexagon: [[.25, 0], [.75, 0], [1, .5], [.75, 1], [.25, 1], [0, .5]],
    triangle: [[.5, 0], [1, 1], [0, 1]],
    shield: [[.5, 0], [1, .18], [.9, .72], [.5, 1], [.1, .72], [0, .18]],
    star: [[.5, 0], [.62, .35], [1, .35], [.69, .57], [.81, .95], [.5, .72], [.19, .95], [.31, .57], [0, .35], [.38, .35]]
  };
  const KIND_SHAPE = { gov: 'square', corp: 'hexagon', found: 'triangle' };
  function shapePath(ctx, shape, x, y, s) {
    ctx.beginPath();
    const pts = SHAPES[shape];
    if (shape === 'circle' || (!pts && shape !== 'square')) { ctx.arc(x, y, s, 0, Math.PI * 2); return; }
    if (!pts) { ctx.rect(x - s, y - s, 2 * s, 2 * s); return; }
    pts.forEach((q, i) => { const px = x + (q[0] - .5) * 2 * s, py = y + (q[1] - .5) * 2 * s; if (i) ctx.lineTo(px, py); else ctx.moveTo(px, py); });
    ctx.closePath();
  }
  window.atlasShapePath = shapePath;
  const RIGHT = n => typeof n[5] === 'string' && n[5].indexOf('right:') === 0;
  const epsteinOf = rec => (rec.ep || []).map(e => e.p).filter(Boolean).concat((rec.fl || []).indexOf('Epstein-linked') >= 0 && !(rec.ep || []).length ? ['Jeffrey Epstein'] : []);
  const FUNDER = n => n[1] === 'gov' || n[1] === 'corp' || n[1] === 'found';
  const rad = Math.PI / 180;
  const kindOn = k => L.kinds[k] !== false;
  // How many spaces name a funder, and in how many countries (the key is the same across spaces; local bodies such as a city
  // government have a key of their own per space and so reach one).
  const reachCache = new Map();
  function reachOf(key) {
    if (!key || !keyIndex) return { n: 1, countries: 1 };
    let o = reachCache.get(key); if (o) return o;
    const ids = keyIndex.get(key) || [], cs = new Set();
    ids.forEach(id => { const q = recById.get(id); if (q && q.co) cs.add(q.co); });
    o = { n: Math.max(1, ids.length), countries: Math.max(1, cs.size) }; reachCache.set(key, o); return o;
  }
  const sizeFor = n => 5.5 + Math.min(4, Math.log2(Math.max(1, n)));
  const plural = (n, w) => `${n} ${w}${n === 1 ? '' : 's'}`;
  // The funder under the pointer: where else it appears is drawn until the pointer has been off it a moment.
  // One picked from the list of widest-reaching funders can be pinned, and then stays until it is picked again or Esc is pressed.
  let STREET = false;   // true while the layers are being drawn over the street map
  let REACH = null, reachTimer = 0;
  const repaint = () => { if (typeof scheduleRender === 'function') scheduleRender(); svSchedule(); };
  function clearReach() { clearTimeout(reachTimer); reachTimer = 0; if (!REACH) return; REACH = null; if (typeof renderTop === 'function') renderTop(); repaint(); }
  function setReach(m) {
    if (REACH && REACH.pinned) return;
    if (m && m.key) {
      clearTimeout(reachTimer); reachTimer = 0;
      if (!REACH || REACH.key !== m.key || REACH.space !== m.space) { REACH = { key: m.key, keys: [m.key], kind: m.kind, space: m.space, name: m.name }; repaint(); }
    } else if (!m) {
      if (REACH && !reachTimer) reachTimer = setTimeout(clearReach, 1500);
    } else if (REACH) clearReach();
  }
  let recById = null, keyIndex = null, keyKind = null, web = null, loading = false;
  let cityFlags = null;
  // Headquarters of the funders and offices of the people the funding map names (assets/hq.json, built by tools/build_hq.py).
  const KIND = { gov: COL.gov, corp: COL.corp, found: COL.found };
  let HQ = null, hqLoading = false;
  // The mark drawn for each office last frame (x, y on the canvas) so a click, a hover and the keyboard buttons can find it;
  // the one picked in the detail panel (assets/hq-detail.js) and the one under the pointer or keyboard focus.
  let HQ_HITS = [], HQ_LABELS = [], HQ_SEL = null, HQ_HOV = null;
  // Every other mark the layers draw (the dots at the ends of tie lines, funder rings, right-wing and Epstein marks, flag and
  // grade marks, the flagged counts) can be found by the pointer too. LM holds the ones drawn last frame, LM_HOV the one under
  // the pointer. A mark that sits on a space's own dot (flag, grade) is "pass": its hover goes to the space, and a click asks
  // the chat.
  let LM = [], LM_HOV = null;
  // Ask the chat: show its tab (on a desktop the Details tab may be in front) and put the question to it.
  function askChat(q) {
    // atlasAskQuestion sends it as a question and brings the chat forward; atlasAskCurator would turn any question that names a space
    // into "Tell me about" that space.
    if (typeof window.atlasAskQuestion === 'function') { window.atlasAskQuestion(q); return; }
    if (typeof window.setWorkspaceTab === 'function') { try { window.setWorkspaceTab('chat'); } catch (e) {} }
    if (typeof window.atlasAskCurator === 'function') window.atlasAskCurator(q);
  }
  window.atlasAskInChat = askChat;
  // The name blocks drawn last frame, so a click on a name can ask the chat about it.
  function loadHq() {
    if (HQ || hqLoading) return;
    hqLoading = true;
    fetch('assets/hq.json').then(r => r.json()).then(d => {
      const orgs = Object.entries(d.org).map(([key, o]) => Object.assign({ key, kind: 'org' }, o));
      const people = Object.entries(d.people).map(([name, o]) => Object.assign({ key: 'person:' + name, kind: 'person' }, o));
      // Pins are city-level, so entries in one city fan out around it instead of stacking.
      const byCity = new Map();
      // Grouped by place, not by the city's spelling: "Düsseldorf" and "Dusseldorf" are one spot and must not sit on each other.
      orgs.concat(people).forEach(e => { const k = e.lat.toFixed(2) + ',' + e.lon.toFixed(2); if (!byCity.has(k)) byCity.set(k, []); byCity.get(k).push(e); });
      byCity.forEach(list => list.forEach((e, i) => { const a = i * 2.39996, rr = i === 0 ? 0 : 8 + 5 * Math.sqrt(i); e.dx = Math.cos(a) * rr; e.dy = Math.sin(a) * rr; }));
      HQ = { orgs, people, byKey: new Map(orgs.map(o => [o.key, o])), byName: new Map(people.map(p => [p.n, p])) };
      hqLoading = false; updateCounts();
      repaint();
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
      repaint();
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
  const streetUp = () => !STREET && typeof window.getIsCityStreetViewActive === 'function' && window.getIsCityStreetViewActive();
  window.atlasLayersDraw = function (ctx, project, r, cx, cy, list, sel, hov, baseRadius) {
    if (streetUp()) return;   // the street map is in front: its own frame draws the layers
    LM = [];
    drawReach(ctx, project, r, cx, cy);
    if (!L.ties) return;
    if (!recById) { loadMoney(); return; }
    const focus = hov || sel, rec = focus && recById.get(focus.id);
    ctx.save();
    ctx.lineCap = 'round';
    // The whole web, faint when a space is in focus.
    ctx.lineWidth = 0.8;
    // The whole web is a world-view picture: with a space in focus, or zoomed in, only that space's own ties are drawn.
    const showWeb = !rec && !HQ_HOV && r < baseRadius * 8;
    ctx.globalAlpha = 0.35;
    const W = ctx.canvas.clientWidth || 1e9, H = ctx.canvas.clientHeight || 1e9;
    if (showWeb) web.forEach(([a, b, kind]) => {
      if (!kindOn(kind)) return;
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
        if (!FUNDER(n) || !n[5] || !kindOn(n[1])) return;
        (keyIndex.get(n[5]) || []).forEach(id => {
          if (seen.has(id) || seen.size > 400) return; seen.add(id);
          const o = recById.get(id); if (!o || typeof o.lat !== 'number') return;
          ctx.strokeStyle = lineCol(COL[n[1]]);
          arc(project, rec, o, r, cx, cy, ctx); ends.push([o, lineCol(COL[n[1]]), COL[n[1]]]);
        });
      });
      ctx.globalAlpha = 1;
      ends.forEach(([o, col, raw]) => {
        const pt = project(o.lon, o.lat, r, cx, cy); if (!pt.front) return;
        const hot = LM_HOV && LM_HOV.rec === o;
        ctx.beginPath(); ctx.arc(pt.x, pt.y, hot ? 6 : 3.5, 0, Math.PI * 2); ctx.fillStyle = col; ctx.fill();
        if (hot) { ctx.lineWidth = 1.5; ctx.strokeStyle = '#000'; ctx.stroke(); }
        LM.push({ x: pt.x, y: pt.y, r: 9, rec: o, col: raw, label: o.n, sub: `Shares a funder with ${rec.n}`, ask: `Who funds ${o.n}?` });
      });
    }
    ctx.restore();
  };

  // The funder under the pointer: a line from its space to every other space that names it, an end dot on each.
  function drawReach(ctx, project, r, cx, cy) {
    if (!REACH || !recById || !kindOn(REACH.kind)) return;
    const home = REACH.space, ends = [], lc = lineCol(COL[REACH.kind]), dark = document.documentElement.getAttribute('data-theme') === 'dark';
    if (!home || typeof home.lat !== 'number') return;
    ctx.save(); ctx.lineCap = 'round'; ctx.lineWidth = 1.6; ctx.globalAlpha = 0.9; ctx.strokeStyle = lc;
    const ids = new Set(); (REACH.keys || [REACH.key]).forEach(k => (keyIndex.get(k) || []).forEach(id => ids.add(id)));
    ids.forEach(id => {
      const o = recById.get(id); if (!o || o === home || typeof o.lat !== 'number') return;
      arc(project, home, o, r, cx, cy, ctx); ends.push(o);
    });
    ctx.globalAlpha = 1;
    ends.forEach(o => {
      const pt = project(o.lon, o.lat, r, cx, cy); if (!pt.front) return;
      const hot = LM_HOV && LM_HOV.rec === o;
      ctx.beginPath(); ctx.arc(pt.x, pt.y, hot ? 6.5 : 4.5, 0, Math.PI * 2); ctx.fillStyle = lc; ctx.fill();
      ctx.lineWidth = 1.5; ctx.strokeStyle = dark ? '#000' : '#fff'; ctx.stroke();
      LM.push({ x: pt.x, y: pt.y, r: 9, rec: o, col: COL[REACH.kind], key: REACH.key, kind: REACH.kind, space: home, name: REACH.name, label: o.n, sub: `Funded by ${REACH.name}`, ask: `Who funds ${o.n}?` });
    });
    ctx.restore();
  }

  // The funding mix of a whole city, for the bar under its label: the funders of every space in it, by kind.
  let cityMixCache = null;
  function cityMix() {
    const sig = ['gov', 'found', 'corp'].map(k => (kindOn(k) ? 1 : 0)).join('');
    if (cityMixCache && cityMixCache.sig === sig) return cityMixCache.map;
    const map = new Map();
    if (typeof ALL_INSTITUTIONS !== 'undefined') ALL_INSTITUTIONS.forEach(i => {
      const rec = i.city && recById.get(i.id); if (!rec) return;
      const k = i.city.toLowerCase().trim(); let c = map.get(k); if (!c) map.set(k, c = { gov: 0, found: 0, corp: 0, spaces: 0 });
      let any = false; rec.nodes.forEach(n => { if (FUNDER(n) && kindOn(n[1])) { c[n[1]]++; any = true; } });
      if (any) c.spaces++;
    });
    cityMixCache = { sig, map }; return map;
  }

  // A box collides with any of the label boxes already on screen (city pills, museum pills, our own labels).
  function collides(box, boxes) {
    return boxes.some(o => !(box.x + box.w < o.x || box.x > o.x + o.w || box.y + box.h < o.y || box.y > o.y + o.h));
  }
  function labelBoxesOnScreen(dots) {
    const out = [];
    if (!STREET && typeof cityBadgeHitboxes !== 'undefined' && Array.isArray(cityBadgeHitboxes)) cityBadgeHitboxes.forEach(b => out.push({ x: b.x, y: b.y, w: b.w, h: b.h }));
    dots.forEach(d => { if (d.labelBox) out.push(d.labelBox); });
    return out;
  }

  // Over the dots and labels: flag marks and the money network.
  // A square on each space the funding map names for this highlight, and its names on blocks when in focus or close.
  function drawHighlight(ctx, project, r, baseRadius, cx, cy, sel, hov, boxes, col, namesOf, dx, shape, what, askOf) {
    const close = r >= baseRadius * 22;
    const marks = [];
    recById.forEach(rec => {
      const names = namesOf(rec); if (!names.length || typeof rec.lat !== 'number') return;
      const pt = project(rec.lon, rec.lat, r, cx, cy); if (!pt.front) return;
      const focus = (sel && sel.id === rec.id) || (hov && hov.id === rec.id);
      marks.push([pt, names, focus]);
      LM.push({ x: pt.x + dx, y: pt.y, r: 9, rec, col, label: names.slice(0, 3).join(', '), sub: `${what}: ${rec.n}`, ask: askOf(rec) });
    });
    ctx.lineWidth = 0.8;
    marks.forEach(([pt]) => { shapePath(ctx, shape, pt.x + dx, pt.y, 6.5); ctx.fillStyle = col; ctx.fill(); ctx.strokeStyle = '#000'; ctx.stroke(); });
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
  // Marks nearer than a diamond's width are nudged apart, so every one has a spot of its own under the pointer: before, a
  // mark with a neighbour a few pixels away could not be hovered, because the neighbour was always the nearer. Nothing moves
  // more than MAX_SHIFT pixels from its place, and marks that already have room stay put. The relaxation is costly, so it is
  // worked out once the view has settled and the offsets are reused while it pans or turns; it is not redone during a zoom.
  const MIN_GAP = 12, MAX_SHIFT = 70, PASSES = 40, CLUSTER_AT = 10;
  let spreadCache = null, spreadAt = 0;
  function relax(pts) {
    const n = pts.length, ox = pts.map(p => p[1]), oy = pts.map(p => p[2]), x = ox.slice(), y = oy.slice();
    for (let it = 0; it < PASSES; it++) {
      const grid = new Map();
      for (let i = 0; i < n; i++) { const k = Math.floor(x[i] / MIN_GAP) + ',' + Math.floor(y[i] / MIN_GAP); const c = grid.get(k); if (c) c.push(i); else grid.set(k, [i]); }
      let moved = false;
      for (let i = 0; i < n; i++) {
        const gx = Math.floor(x[i] / MIN_GAP), gy = Math.floor(y[i] / MIN_GAP);
        for (let a = -1; a <= 1; a++) for (let b = -1; b <= 1; b++) {
          const cell = grid.get((gx + a) + ',' + (gy + b)); if (!cell) continue;
          for (const j of cell) {
            if (j <= i) continue;
            let dx = x[j] - x[i], dy = y[j] - y[i], d = Math.hypot(dx, dy);
            if (d >= MIN_GAP) continue;
            if (d < 0.01) { const t = i * 2.39996 + j; dx = Math.cos(t); dy = Math.sin(t); d = 1; }
            const push = (MIN_GAP - d) / 2, ux = dx / d, uy = dy / d;
            x[i] -= ux * push; y[i] -= uy * push; x[j] += ux * push; y[j] += uy * push;
            moved = true;
          }
        }
      }
      if (!moved) break;
    }
    const off = new Map();
    for (let i = 0; i < n; i++) {
      let dx = x[i] - ox[i], dy = y[i] - oy[i]; const d = Math.hypot(dx, dy);
      if (d > MAX_SHIFT) { dx *= MAX_SHIFT / d; dy *= MAX_SHIFT / d; }
      off.set(pts[i][0], [dx, dy]);
    }
    return off;
  }
  function spreadMarks(pts, r, baseRadius) {
    // With the whole globe in view there is no room to spread into; the crowd is picked from the list a click opens.
    if (pts.length < 2 || r < baseRadius * 1.5) return;
    const v = typeof window.getView === 'function' ? window.getView() : null;
    const settled = !v || Math.abs(v.r - v.target) < 0.5;
    const fresh = spreadCache && Math.abs(r - spreadCache.r) / spreadCache.r < 0.02 && spreadCache.hq === L.hq && spreadCache.people === L.people;
    const now = performance.now();
    if (settled && (!fresh || (now - spreadAt > 400 && pts.some(p => !spreadCache.off.has(p[0]))))) {
      spreadCache = { r, hq: L.hq, people: L.people, off: relax(pts) };
      spreadAt = now;
    } else if (!fresh) return;
    pts.forEach(p => { const o = spreadCache.off.get(p[0]); if (o) { p[1] += o[0]; p[2] += o[1]; } });
  }

  // How many spaces name an office's funder: the bigger the diamond, the wider its reach.
  const orgReach = e => { if (e._reach === undefined) e._reach = keysOf(e).reduce((a, k) => a + (keyIndex.get(k) || []).length, 0); return e._reach; };
  function drawHq(ctx, project, r, baseRadius, cx, cy, sel, hov, boxes) {
    if (!HQ) return;
    const focus = hov || sel, rec = focus && recById && recById.get(focus.id);
    const linkedOrgs = new Set(), linkedPeople = new Set();
    if (rec) {
      rec.nodes.forEach(n => { if (n[5] && HQ.byKey.has(n[5])) linkedOrgs.add(n[5]); });
      (rec.ep || []).forEach(e => { if (e.p && HQ.byName.has(e.p)) linkedPeople.add(e.p); });
    }
    const dark = document.documentElement.getAttribute('data-theme') === 'dark';
    let pts = [];
    const place = (e, show) => {
      if (!show || (e.kind === 'org' && !kindOn(e.k))) return;
      const pt = project(e.lon, e.lat, r, cx, cy); if (!pt.front) return;
      pts.push([e, pt.x + e.dx, pt.y + e.dy]);
    };
    const picked = e => e === HQ_SEL || e === HQ_HOV;
    if (L.hq) HQ.orgs.forEach(e => place(e, true));
    if (L.people) HQ.people.forEach(e => place(e, true));
    // Offices are pinned to their city, and a city holds up to 45 of them. Spread across the map they settle into a lattice that
    // spills over the sea and the next country, so until the view is close enough to give each its own room a city with several
    // offices is one numbered mark at the city's true place. The ones in play (the focused space's funders, the picked office)
    // stay out of it and are drawn singly.
    const clusters = [];
    if (r < baseRadius * CLUSTER_AT) {
      const groups = new Map();
      pts.forEach(p => {
        const e = p[0]; if (e.kind !== 'org' || picked(e) || (rec && linkedOrgs.has(e.key))) return;
        const k = e.lat.toFixed(1) + ',' + e.lon.toFixed(1); if (!groups.has(k)) groups.set(k, []); groups.get(k).push(p);
      });
      const drop = new Set();
      groups.forEach(list => { if (list.length < 2) return; list.forEach(p => drop.add(p)); clusters.push(list.map(p => p[0])); });
      if (drop.size) pts = pts.filter(p => !drop.has(p));
    }
    spreadMarks(pts, r, baseRadius);
    // joins from the focused space
    if (rec && typeof rec.lat === 'number') {
      ctx.lineWidth = 1.2; ctx.globalAlpha = 0.85;
      if (L.hq) linkedOrgs.forEach(k => { const o = HQ.byKey.get(k); ctx.strokeStyle = lineCol(KIND[o.k]); arc(project, rec, o, r, cx, cy, ctx); });
      if (L.people) linkedPeople.forEach(n => { const o = HQ.byName.get(n); ctx.strokeStyle = lineCol(COL.person); arc(project, rec, o, r, cx, cy, ctx); });
      ctx.globalAlpha = 1;
    }
    // The picked office's own joins, and the one under the pointer or keyboard focus: an arc to each space it is named on.
    if (recById) [HQ_SEL, HQ_HOV].filter((o, i, a) => o && a.indexOf(o) === i).forEach(o => {
      if (!pts.some(p => p[0] === o)) return;
      ctx.lineWidth = o === HQ_HOV ? 1.4 : 1.2; ctx.globalAlpha = o === HQ_HOV ? 0.9 : 0.8;
      ctx.strokeStyle = lineCol(o.kind === 'org' ? KIND[o.k] : COL.person);
      hq.spaces(o).slice(0, 80).forEach(sp => { if (typeof sp.rec.lat === 'number') arc(project, o, sp.rec, r, cx, cy, ctx); });
      ctx.globalAlpha = 1;
    });
    // marks
    ctx.lineWidth = 1;
    pts.forEach(([e, x, y]) => {
      const on = (e.kind === 'org' ? linkedOrgs.has(e.key) : linkedPeople.has(e.n)) || picked(e);
      const s = on ? 7 : (rec ? 3.5 : (e.kind === 'org' && recById ? 4 + Math.min(2.5, Math.sqrt(orgReach(e)) * 0.7) : 5));
      HQ_HITS.push({ e, x, y });
      ctx.globalAlpha = rec && !on ? 0.35 : 1;
      ctx.fillStyle = e.kind === 'org' ? KIND[e.k] : COL.person; ctx.strokeStyle = '#000';
      ctx.beginPath();
      if (e.kind === 'org') { ctx.moveTo(x, y - s); ctx.lineTo(x + s, y); ctx.lineTo(x, y + s); ctx.lineTo(x - s, y); ctx.closePath(); }
      else ctx.arc(x, y, s - 0.5, 0, Math.PI * 2);
      ctx.fill(); ctx.stroke();
      if (e === HQ_SEL) {
        // A ring in two colours, so one of them always shows against the ground.
        ctx.globalAlpha = 1; ctx.beginPath(); ctx.arc(x, y, s + 5, 0, Math.PI * 2);
        ctx.lineWidth = 3; ctx.strokeStyle = dark ? '#000' : '#fff'; ctx.stroke();
        ctx.lineWidth = 1.5; ctx.strokeStyle = dark ? '#fff' : '#000'; ctx.stroke(); ctx.lineWidth = 1;
      }
    });
    ctx.globalAlpha = 1;
    clusters.forEach(list => {
      // The metro area (0.1 degree, about 11 km) is one place: the mark sits at the mean of its pins and takes the commonest city name.
      const n = list.length, mlat = list.reduce((a, e) => a + e.lat, 0) / n, mlon = list.reduce((a, e) => a + e.lon, 0) / n;
      const cn = {}; list.forEach(e => { cn[e.c] = (cn[e.c] || 0) + 1; });
      const e0 = list.find(e => e.c === Object.keys(cn).sort((a, b) => cn[b] - cn[a])[0]), pt = project(mlon, mlat, r, cx, cy); if (!pt.front) return;
      const s = 7 + Math.min(7, Math.sqrt(n) * 1.5), counts = {};
      // A city's label sits right above its pin, so the diamond hangs from the pin (its top tip on it) instead of being centred on it.
      const px = pt.x, py = pt.y + (STREET ? 0 : s - 2);
      list.forEach(e => { counts[e.k] = (counts[e.k] || 0) + 1; });
      const k = Object.keys(counts).sort((a, b) => counts[b] - counts[a])[0], col = KIND[k] || COL.corp;
      ctx.globalAlpha = rec ? 0.55 : 1; ctx.lineWidth = 1; ctx.fillStyle = col; ctx.strokeStyle = '#000';
      ctx.beginPath(); ctx.moveTo(px, py - s); ctx.lineTo(px + s, py); ctx.lineTo(px, py + s); ctx.lineTo(px - s, py); ctx.closePath(); ctx.fill(); ctx.stroke();
      ctx.globalAlpha = 1; ctx.fillStyle = '#000'; ctx.font = '700 10px "PP Neue Gstaad", sans-serif'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
      ctx.fillText(String(n), px, py + 0.5);
      const names = list.slice(0, 3).map(e => e.n).join(', ') + (n > 3 ? ` and ${n - 3} more` : '');
      LM.push({ x: px, y: py, r: s + 3, col, label: `${e0.c}, ${e0.co}`, sub: `${n} funder offices`, sub2: names, ask: `Which funders are headquartered in ${e0.c}?`,
        go() { if (typeof window.flyTo === 'function') window.flyTo(mlon, mlat, baseRadius * (CLUSTER_AT + 1.5)); } });
    });
    ctx.font = '14px "Jokker", sans-serif';
    // Names: on blocks for the focused space's own funders and people. With nothing in focus, only a very close view names them,
    // as plain text on a halo, so the map is not covered in blocks.
    const veryClose = !rec && r >= baseRadius * 30;
    ctx.textAlign = 'left'; ctx.textBaseline = 'middle';
    pts.forEach(([e, x, y]) => {
      const on = (e.kind === 'org' ? linkedOrgs.has(e.key) : linkedPeople.has(e.n)) || picked(e);
      if (!(on || veryClose)) return;
      const text = e.kind === 'org' ? (on ? `${e.n}, ${e.c}` : e.n) : `${e.n}, ${e.w}`, t = text.length > 40 ? text.slice(0, 38) + '…' : text;
      const tw = ctx.measureText(t).width, w = tw + 12, h = 20, box = { x: x + 10, y: y - h / 2, w, h };
      if (collides(box, boxes)) return;
      boxes.push(box); HQ_LABELS.push({ e, x: box.x, y: box.y, w, h });
      if (on) { ctx.fillStyle = e.kind === 'org' ? KIND[e.k] : COL.person; ctx.fillRect(box.x, box.y, w, h); ctx.fillStyle = '#000'; ctx.fillText(t, box.x + 6, y + 0.5); }
      else { ctx.lineJoin = 'round'; ctx.lineWidth = 3; ctx.strokeStyle = document.documentElement.getAttribute('data-theme') === 'dark' ? '#000' : '#fff'; ctx.strokeText(t, box.x + 6, y + 0.5); ctx.fillStyle = document.documentElement.getAttribute('data-theme') === 'dark' ? '#fff' : '#161616'; ctx.fillText(t, box.x + 6, y + 0.5); }
    });
  }

  function drawNodes(ctx, dots, r, baseRadius, sel, hov, gossip, project, cx, cy) {
    if (!REACH && !L.flags && !L.grade && !L.money && !L.mix && !L.right && !L.epstein && !L.hq && !L.people && !L.ties) return;
    if ((L.money || L.mix || L.right || L.epstein || L.hq || L.people) && !recById) loadMoney();
    if ((L.hq || L.people) && !HQ) loadHq();
    const dark = document.documentElement.getAttribute('data-theme') === 'dark';
    const font = '14px "Jokker", sans-serif';
    const boxes = labelBoxesOnScreen(dots);
    ctx.save();
    ctx.font = font; ctx.textBaseline = 'middle';

    if (L.grade) {
      // Each rated space: a dot filled with its funding transparency rating colour (window.atlasGrade, set by the page).
      // A space with no grade keeps its hollow ring.
      const G = window.atlasGrade || {};
      ctx.lineWidth = 0.8;
      dots.forEach(d => {
        const i = d.inst; if (!i || !i.grade || !G[i.grade]) return;
        LM.push({ x: d.x, y: d.y, r: 8, pass: true, rec: i, ask: `Why is ${i.name} graded ${G[i.grade].letter || i.grade}?` });
        ctx.beginPath(); ctx.arc(d.x, d.y, 6.5, 0, Math.PI * 2);
        ctx.fillStyle = G[i.grade].col; ctx.fill();
        ctx.strokeStyle = '#000'; ctx.stroke();
        // The letter is the second cue: grade A and B are two near greens, and colour alone cannot tell the five apart.
        ctx.save(); ctx.font = '700 9px "PP Neue Gstaad", sans-serif'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillStyle = '#000';
        ctx.fillText(G[i.grade].letter, d.x, d.y + 0.5); ctx.restore();
      });
    }
    if (L.mix && recById && r >= baseRadius * 3) {
      // Each space with funders: a ring split into public funding, foundations and companies, by how many of each it names,
      // in the same order and colours as the funder marks. A kind switched off under Funder types leaves the ring. Only from a moderately close view, where the dots have room.
      const order = ['gov', 'found', 'corp'], GAP = 0.16, R = 10;
      dots.forEach(d => {
        const i = d.inst, rec = i && recById.get(i.id); if (!rec) return;
        const c = { gov: 0, found: 0, corp: 0 }; rec.nodes.forEach(n => { if (FUNDER(n) && kindOn(n[1])) c[n[1]]++; });
        const parts = order.filter(k => c[k]), total = parts.reduce((a, k) => a + c[k], 0); if (!total) return;
        ctx.lineCap = 'butt';
        ctx.beginPath(); ctx.arc(d.x, d.y, R, 0, Math.PI * 2); ctx.lineWidth = 6.5; ctx.strokeStyle = dark ? '#000' : '#fff'; ctx.stroke();
        let a0 = -Math.PI / 2; ctx.lineWidth = 4;
        parts.forEach(k => {
          const span = (c[k] / total) * Math.PI * 2, gap = parts.length > 1 ? Math.min(GAP, span * 0.4) : 0;
          ctx.beginPath(); ctx.arc(d.x, d.y, R, a0 + gap / 2, a0 + span - gap / 2); ctx.strokeStyle = lineCol(COL[k]); ctx.stroke(); a0 += span;
        });
      });
    }
    if (L.mix && recById && !STREET && r < baseRadius * 3 && typeof cityBadgeHitboxes !== 'undefined' && Array.isArray(cityBadgeHitboxes)) {
      // Too far out for a ring on each space: a bar under each city's label instead, the same three colours in the same order.
      const mixes = cityMix(), order = ['gov', 'found', 'corp'];
      cityBadgeHitboxes.forEach(b => {
        const c = mixes.get((b.name || '').toLowerCase().trim()); if (!c) return;
        const parts = order.filter(k => c[k]), total = parts.reduce((a, k) => a + c[k], 0); if (!total) return;
        const y = b.y + b.h + 1, h = 4;
        ctx.fillStyle = dark ? '#000' : '#fff'; ctx.fillRect(b.x - 1, y - 1, b.w + 2, h + 2);
        let x = b.x; parts.forEach(k => { const w = b.w * c[k] / total; ctx.fillStyle = lineCol(COL[k]); ctx.fillRect(x, y, Math.max(1, w - 1), h); x += w; });
        const text = parts.map(k => `${c[k]} ${k === 'gov' ? 'public' : k === 'found' ? (c[k] === 1 ? 'foundation' : 'foundations') : (c[k] === 1 ? 'company' : 'companies')}`).join(', ');
        LM.push({ box: { x: b.x, y: y - 3, w: b.w, h: h + 6 }, x: b.x + b.w / 2, y, r: 0, col: COL.person, label: `Funders in ${b.name}`, sub: text, sub2: `${plural(c.spaces, 'space')} with funders`, ask: `How are the spaces in ${b.name} funded?` });
      });
    }
    if (L.flags) {
      // Each flagged space: a filled orange dot over its ring.
      ctx.lineWidth = 0.8;
      dots.forEach(d => {
        const i = d.inst; if (!i || !i.flags || !i.flags.length) return;
        LM.push({ x: d.x, y: d.y, r: 8, pass: true, rec: i, ask: `What is reported about ${i.name}?` });
        shapePath(ctx, 'square', d.x, d.y, 4.6);
        ctx.fillStyle = COL.flag; ctx.fill();
        ctx.strokeStyle = '#000'; ctx.stroke();
      });
      // Each city cluster: the number of flagged spaces in it, on an orange block after the city's label.
      if (!STREET && typeof cityBadgeHitboxes !== 'undefined' && Array.isArray(cityBadgeHitboxes)) {
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
          LM.push({ box: { x, y, w, h }, x: x + w / 2, y: y + h / 2, r: 0, col: COL.flag, label: `${n} flagged in ${b.name}`, sub: 'Flagged spaces', ask: `Which spaces in ${b.name} are flagged, and why?` });
        });
      }
    }

    // Both highlights on: the Epstein square sits to the right of the right-wing one, so a space in both shows both.
    if (L.right && recById) drawHighlight(ctx, project, r, baseRadius, cx, cy, sel, hov, boxes, COL.right, rec => rec.nodes.filter(RIGHT).map(n => n[0]), L.epstein ? -7 : 0, 'shield', 'Right-wing funder', rec => `Who funds ${rec.n}?`);
    if (L.epstein && recById) drawHighlight(ctx, project, r, baseRadius, cx, cy, sel, hov, boxes, COL.epstein, epsteinOf, L.right ? 7 : 0, 'star', 'Named in the Epstein files', rec => `What is ${rec.n}'s Epstein link?`);

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
        const nodes = rec.nodes.filter(n => FUNDER(n) && kindOn(n[1]));
        if (!nodes.length) return;
        // The ring is 64 px when the view is close; further out it shrinks, so funders never land on other cities.
        const zoomK = Math.max(0.4, Math.min(1, r / (baseRadius * 12)));
        const N = Math.min(nodes.length, focus ? 10 : 6), R = (focus ? 64 : 36) * zoomK;
        for (let i = 0; i < N; i++) {
          const n = nodes[i], a = -Math.PI / 2 + (i * 2 * Math.PI) / N, x = d.x + R * Math.cos(a), y = d.y + R * Math.sin(a);
          const col = gossip ? '#e2f86c' : COL[n[1]];
          ctx.globalAlpha = focus ? 1 : 0.7;
          ctx.strokeStyle = lineCol(col); ctx.beginPath(); ctx.moveTo(d.x, d.y); ctx.lineTo(x, y); ctx.stroke();
          // The outline says the kind (square public funding, hexagon company, triangle foundation); the colour repeats it.
          const reach = reachOf(n[5]), sr = sizeFor(reach.n > 1 ? reach.n : 1);
          shapePath(ctx, KIND_SHAPE[n[1]] || 'circle', x, y, sr); ctx.fillStyle = dark ? '#000' : '#fff'; ctx.lineWidth = 1.3; ctx.fill(); ctx.stroke(); ctx.lineWidth = 0.8;
          if (n[5]) { if (!byKey.has(n[5])) byKey.set(n[5], []); byKey.get(n[5]).push([x, y, col]); }
          labels.push([n[0], x, y, a, col]);
          const shared = reach.n > 1;
          LM.push({ x, y, r: Math.max(10, sr + 4), col, key: n[5], kind: n[1], space: rec, name: n[0], ox: d.x, oy: d.y, label: n[0], sub: `Funder of ${rec.n}`,
            sub2: shared ? `Also funds ${plural(reach.n - 1, 'other space')} in ${plural(reach.countries, 'country').replace('countrys', 'countries')}` : 'Funds no other space here',
            ask: shared ? `Which institutions does ${n[0]} fund?` : `How does ${n[0]} fund ${rec.n}?` });
        }
      });
      // A funder named on two spaces on screen is joined across them.
      ctx.globalAlpha = 0.8;
      const W = ctx.canvas.clientWidth || 1e9, H = ctx.canvas.clientHeight || 1e9, onScreen = p => p[0] > -40 && p[0] < W + 40 && p[1] > -40 && p[1] < H + 40;
      byKey.forEach(pts => { pts = pts.filter(onScreen); for (let i = 1; i < pts.length; i++) { ctx.strokeStyle = lineCol(pts[i][2]); ctx.beginPath(); ctx.moveTo(pts[0][0], pts[0][1]); ctx.lineTo(pts[i][0], pts[i][1]); ctx.stroke(); } });
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
    drawMarkTip(ctx, boxes);
    ctx.restore();
  }
  // The mark under the pointer: its name on a block in its colour, and that a click asks the chat.
  function drawMarkTip(ctx, boxes) {
    if (!LM_HOV) return;
    const m = LM.find(q => q.ask === LM_HOV.ask && q.rec === LM_HOV.rec && !q.pass) || null; if (!m) return;
    const W = ctx.canvas.clientWidth || 1e9;
    const clip = t => t.length > 64 ? t.slice(0, 62) + '…' : t;
    const lines = [clip(m.label), m.sub ? clip(m.sub) : null, m.sub2 ? clip(m.sub2) : null, m.go ? 'Click to zoom in' : 'Click to ask the chat'].filter(Boolean);
    ctx.save(); ctx.font = '14px "Jokker", "PP Neue Gstaad", sans-serif'; ctx.textAlign = 'left'; ctx.textBaseline = 'middle';
    const w = Math.max(...lines.map(t => ctx.measureText(t).width)) + 12, h = 20;
    // The block goes where it covers the fewest labels: beside the mark, or above or below it; away from the space a funder
    // ring belongs to first, so the ring's other names stay readable.
    const H = ctx.canvas.clientHeight || 1e9, th = h * lines.length, away = m.ox !== undefined ? Math.sign(m.x - m.ox) || 1 : 1;
    const cand = [[away > 0 ? m.x + 12 : m.x - 12 - w, m.y - th / 2], [away > 0 ? m.x - 12 - w : m.x + 12, m.y - th / 2], [m.x - w / 2, m.y - 12 - th], [m.x - w / 2, m.y + 12]]
      .map(([x, y]) => ({ x: Math.max(4, Math.min(x, W - w - 4)), y: Math.max(4, Math.min(y, H - th - 4)), w, h: th }));
    const spot = cand.find(c => !collides(c, boxes || [])) || cand[0], bx = spot.x, by = spot.y;
    ctx.fillStyle = m.col || '#fff'; ctx.fillRect(bx, by, w, h * lines.length);
    ctx.fillStyle = '#000'; lines.forEach((t, k) => ctx.fillText(t, bx + 6, by + h * k + h / 2 + 0.5));
    ctx.restore();
  }
  window.atlasLayersDrawNodes = function (ctx, dots, r, baseRadius, sel, hov, gossip, project, cx, cy) {
    if (streetUp()) return;
    HQ_HITS = []; HQ_LABELS = [];
    try { drawNodes(ctx, dots, r, baseRadius, sel, hov, gossip, project, cx, cy); }
    finally { if (window.atlasHqFrame) window.atlasHqFrame(HQ_HITS); }
  };

  // ---- Offices as things you can pick: hit-testing, the connections in the data, and the selection ----
  const KIND_LABEL = { gov: 'Public funder', corp: 'Company', found: 'Foundation or individual donor', person: 'Individual\u2019s office' };
  const kindLabel = e => KIND_LABEL[e.kind === 'org' ? e.k : 'person'];
  // An office is keyed by funder key, and the same body can sit under two keys ('artscouncilengland|UK' and '|United Kingdom').
  const keysOf = e => { const ks = [e.key]; HQ.orgs.forEach(o => { if (o !== e && o.n === e.n && o.co === e.co) ks.push(o.key); }); return ks; };
  const byName = (a, b) => a.n.localeCompare(b.n);
  const hq = {
    kindLabel,
    ready(cb) { loadMoney(); loadHq(); let n = 0; const t = setInterval(() => { if ((HQ && recById) || ++n > 300) { clearInterval(t); if (HQ && recById) cb(); } }, 40); },
    loaded: () => !!(HQ && recById),
    // Every name the records give this office: the one the map uses, then each spelling a space's funding line uses for the same key.
    names(e) {
      const out = [e.n];
      if (e.kind === 'org' && recById) {
        const ks = new Set(keysOf(e)), seen = new Set([e.n.toLowerCase()]);
        recById.forEach(rec => rec.nodes.forEach(n => { if (FUNDER(n) && ks.has(n[5]) && !seen.has(n[0].toLowerCase())) { seen.add(n[0].toLowerCase()); out.push(n[0]); } }));
      }
      return out;
    },
    // The spaces an office is named on: a funder through the funding lines, a person through the Epstein-files records.
    spaces(e) {
      const out = [];
      if (!recById) return out;
      if (e.kind === 'org') {
        const seen = new Set();
        keysOf(e).forEach(k => (keyIndex.get(k) || []).forEach(id => { if (!seen.has(id) && recById.get(id)) { seen.add(id); out.push({ rec: recById.get(id) }); } }));
      } else {
        recById.forEach(rec => (rec.ep || []).forEach(x => { if (x.p === e.n) out.push({ rec, label: x.l, status: x.s, text: x.t }); }));
      }
      return out.sort((a, b) => a.rec.n.localeCompare(b.rec.n));
    },
    // Other offices tied through the same spaces: funders that sit beside this one on a space, and people the files tie to those spaces.
    related(e) {
      const funders = new Map(), people = new Map();
      if (!HQ || !recById) return { funders: [], people: [] };
      const own = e.kind === 'org' ? new Set(keysOf(e)) : null;
      hq.spaces(e).forEach(({ rec }) => {
        if (e.kind === 'org') (rec.ep || []).forEach(x => { const p = x.p && HQ.byName.get(x.p); if (p) people.set(p, (people.get(p) || 0) + 1); });
        rec.nodes.forEach(n => {
          if (!FUNDER(n) || !n[5] || (own && own.has(n[5]))) return;
          const o = HQ.byKey.get(n[5]); if (!o || (o.n === e.n && o.co === e.co)) return;
          funders.set(o, (funders.get(o) || 0) + 1);
        });
      });
      const rank = m => [...m.entries()].sort((a, b) => b[1] - a[1] || byName(a[0], b[0])).map(([o, c]) => ({ e: o, shared: c }));
      return { funders: rank(funders), people: rank(people) };
    },
    // Marks under a point, nearest first; the spaces' own dots under it too, so a crowded spot can still offer each one.
    at(mx, my, reach, dots) {
      const marks = HQ_HITS.map(h => ({ e: h.e, d: Math.hypot(h.x - mx, h.y - my) })).filter(h => h.d <= reach).sort((a, b) => a.d - b.d);
      const spaces = (dots || []).map(d => ({ inst: d.inst, d: Math.hypot(d.x - mx, d.y - my) })).filter(d => d.d <= reach).sort((a, b) => a.d - b.d);
      return { marks, spaces };
    },
    // The office whose drawn name is under the point, if any.
    labelAt(mx, my) { const l = HQ_LABELS.find(b => mx >= b.x && mx <= b.x + b.w && my >= b.y && my <= b.y + b.h); return l ? l.e : null; },
    reach: () => (window.__lastPointerType === 'touch' || window.__lastPointerType === 'pen') ? 22 : 12,
    hover(e) { if (HQ_HOV === e) return; HQ_HOV = e; repaint(); },
    select(e) { HQ_SEL = e; repaint(); },
    selected: () => HQ_SEL,
    screenPos(e) { const m = HQ_HITS.find(x => x.e === e); return m ? { x: m.x, y: m.y } : null; },
    // Turn on the layer an office belongs to, so the mark being named is on the map.
    showLayer(e) {
      const k = e.kind === 'org' ? 'hq' : 'people';
      if (L[k]) return;
      L[k] = true;
      document.querySelectorAll('#layersPanel input[data-layer]').forEach(i => { if (i.dataset.layer === k) i.checked = true; });
    },
    // Centre the map on an office, keeping the zoom unless the view is too wide to tell offices apart.
    flyToOffice(e) {
      hq.showLayer(e);
      if (typeof window.flyTo !== 'function') return;
      const base = window.getBaseRadius ? window.getBaseRadius() : 276, cur = window.getView ? window.getView().r : 0;
      window.flyTo(e.lon, e.lat, Math.max(cur, base * 8));
    },
    flyToSpace(rec) {
      if (typeof window.selectInstitution === 'function') window.selectInstitution(rec.id, false);
      if (typeof window.flyTo !== 'function' || typeof rec.lat !== 'number') return;
      const base = window.getBaseRadius ? window.getBaseRadius() : 276, cur = window.getView ? window.getView().r : 0;
      window.flyTo(rec.lon, rec.lat, Math.max(cur, base * 8));
    }
  };
  window.atlasHq = hq;

  // ---- The other marks as things you can point at and click ----
  function markAt(mx, my) {
    const touch = window.__lastPointerType === 'touch' || window.__lastPointerType === 'pen';
    let best = null, bd = Infinity;
    LM.forEach(m => {
      let d;
      if (m.box) { if (mx < m.box.x || mx > m.box.x + m.box.w || my < m.box.y || my > m.box.y + m.box.h) return; d = 0; }
      else { d = Math.hypot(m.x - mx, m.y - my); if (d > m.r * (touch ? 1.6 : 1)) return; }
      if (m.pass) d += 100;   // a mark on a space's own dot gives way to one that stands alone
      if (d < bd) { bd = d; best = m; }
    });
    return best;
  }
  window.atlasLayerMarks = {
    // The marks drawn last frame (position, name, count line), for checking the layers from a test script.
    marks: () => LM.map(m => ({ x: m.x, y: m.y, r: m.r, label: m.label, sub: m.sub, go: !!m.go })),
    // Pointer moved: a mark that stands alone takes the hover (true, so the page shows a pointer); a mark on a space's dot does not.
    hover(mx, my) {
      const m = markAt(mx, my), alone = m && !m.pass ? m : null;
      if ((alone && alone.ask) !== (LM_HOV && LM_HOV.ask) || (alone && alone.rec) !== (LM_HOV && LM_HOV.rec)) { LM_HOV = alone; repaint(); }
      setReach(alone);
      return !!alone;
    },
    // A click on a mark asks the chat about it, and that is all the click does. The chat answers a question about a space
    // with the space selected on the map and stays in front, so a flag or grade mark loses nothing by not opening the record.
    click(mx, my) {
      const m = markAt(mx, my); if (!m) return false;
      if (m.go) { m.go(); return true; }
      askChat(m.ask);
      return true;
    }
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
    repaint();
  };

  // What each layer holds, as a count after its name.
  function updateCounts() {
    const set = (k, text) => { const el = document.querySelector(`#layersPanel [data-count="${k}"]`); if (el) el.textContent = text; };
    const formatCount = count => new Intl.NumberFormat('en-US').format(count);
    if (typeof ALL_INSTITUTIONS !== 'undefined') {
      set('spaces', `${formatCount(ALL_INSTITUTIONS.length)}`);
      set('flags', `${formatCount(ALL_INSTITUTIONS.filter(i => i.flags && i.flags.length).length)}`);
      const graded = ALL_INSTITUTIONS.filter(i => i.grade).length;
      set('grade', `${formatCount(graded)} rated · ${formatCount(ALL_INSTITUTIONS.length - graded)} unrated`);
    }
    if (HQ) {
      set('hq', `${formatCount(HQ.orgs.length)} offices · ${formatCount(new Set(HQ.orgs.map(o => o.c)).size)} cities`);
      set('people', `${formatCount(HQ.people.length)} offices`);
    }
    if (recById && HQ) buildTop();
    if (web) {
      set('ties', `${formatCount(web.length)} links · ${formatCount([...keyIndex.values()].filter(ids => ids.length >= 2).length)} shared funders`);
      set('money', `${formatCount([...recById.values()].filter(rec => rec.nodes.some(FUNDER)).length)} spaces`);
      set('mix', `${formatCount([...recById.values()].filter(rec => rec.nodes.some(FUNDER)).length)} spaces`);
      const rightRecs = [...recById.values()].filter(rec => rec.nodes.some(RIGHT)), rightKeys = new Set();
      rightRecs.forEach(rec => rec.nodes.filter(RIGHT).forEach(n => rightKeys.add(n[5])));
      set('right', `${formatCount(rightRecs.length)} spaces · ${formatCount(rightKeys.size)} funders`);
      set('epstein', `${formatCount([...recById.values()].filter(rec => epsteinOf(rec).length).length)} spaces`);
    }
  }

  // ---- Street view ----
  // Opening a city puts a MapLibre map over the globe, so the globe canvas, where the layers draw, is out of sight. A canvas of
  // the same size is laid over the street map instead, and the same drawing code runs on it with the map's own projection, at a
  // scale that grows with the map's zoom (so a layer that waits for a close view shows at street zoom). The marks answer the pointer
  // as they do on the globe.
  const SV = { map: null, el: null, canvas: null, raf: 0, dots: [], on: false, bound: null };
  function svSchedule() { if (SV.on && !SV.raf) SV.raf = requestAnimationFrame(svRender); }
  function svRender() {
    SV.raf = 0; if (!SV.on || !SV.map || typeof ALL_INSTITUTIONS === 'undefined') return;
    const map = SV.map, W = SV.el.clientWidth, H = SV.el.clientHeight, dpr = window.devicePixelRatio || 1, cv = SV.canvas;
    if (!W || !H) return;
    if (cv.width !== Math.round(W * dpr) || cv.height !== Math.round(H * dpr)) { cv.width = Math.round(W * dpr); cv.height = Math.round(H * dpr); cv.style.width = W + 'px'; cv.style.height = H + 'px'; }
    const ctx = cv.getContext('2d'); ctx.setTransform(dpr, 0, 0, dpr, 0, 0); ctx.clearRect(0, 0, W, H);
    if (!(REACH || L.flags || L.grade || L.money || L.mix || L.right || L.epstein || L.hq || L.people || L.ties)) { SV.dots = []; LM = []; return; }
    const base = 240, r = base * Math.pow(2, map.getZoom() - 7);
    // Points behind the camera on a tilted map project to nonsense; anything far off the canvas is treated as not in front.
    const project = (lon, lat) => { const p = map.project([lon, lat]); return { x: p.x, y: p.y, front: Math.abs(p.x - W / 2) < 6 * W && Math.abs(p.y - H / 2) < 6 * H, depth: 1 }; };
    const dots = [], list = [], pad = 40;
    ALL_INSTITUTIONS.forEach(i => {
      if (typeof i.lat !== 'number' || typeof i.lon !== 'number') return;
      const p = project(i.lon, i.lat); if (!p.front) return;
      list.push(i);
      if (p.x > -pad && p.x < W + pad && p.y > -pad && p.y < H + pad) dots.push({ inst: i, x: p.x, y: p.y });
    });
    SV.dots = dots;
    const sel = typeof window.getSelectedInstitution === 'function' ? window.getSelectedInstitution() : null;
    STREET = true;
    try {
      window.atlasLayersDraw(ctx, project, r, W / 2, H / 2, list, sel, null, base);
      window.atlasLayersDrawNodes(ctx, dots, r, base, sel, null, false, project, W / 2, H / 2);
    } finally { STREET = false; }
  }
  window.atlasStreetLayers = {
    start(map, el) {
      if (SV.map !== map) {
        if (SV.map && SV.bound) { SV.map.off('render', SV.bound.render); SV.map.off('mousemove', SV.bound.move); SV.map.off('click', SV.bound.click); }
        SV.map = map; SV.el = el;
        const render = () => svSchedule();
        const move = e => {
          if (!SV.on) return;
          const hit = (window.atlasHqPointer && window.atlasHqPointer.hover(e.point.x, e.point.y, SV.dots)) || (window.atlasLayerMarks && window.atlasLayerMarks.hover(e.point.x, e.point.y));
          map.getCanvas().style.cursor = hit ? 'pointer' : '';
        };
        const click = e => {
          if (!SV.on) return;
          const oe = e.originalEvent || {};
          if (window.atlasHqPointer && window.atlasHqPointer.click(e.point.x, e.point.y, oe.clientX, oe.clientY, SV.dots)) return;
          if (window.atlasLayerMarks) window.atlasLayerMarks.click(e.point.x, e.point.y);
        };
        SV.bound = { render, move, click };
        map.on('render', render); map.on('mousemove', move); map.on('click', click);
      }
      if (!SV.canvas || !SV.canvas.isConnected) {
        SV.canvas = document.createElement('canvas'); SV.canvas.id = 'streetLayersCanvas'; SV.canvas.setAttribute('aria-hidden', 'true');
        SV.canvas.style.cssText = 'position:absolute;left:0;top:0;pointer-events:none;z-index:1';
        el.appendChild(SV.canvas);
      }
      SV.on = true; if (REACH || L.hq || L.people) { loadMoney(); loadHq(); }
      svSchedule();
    },
    stop() {
      SV.on = false; if (SV.canvas) SV.canvas.getContext('2d').clearRect(0, 0, SV.canvas.width, SV.canvas.height);
      LM = []; LM_HOV = null; HQ_HITS = []; if (SV.map) SV.map.getCanvas().style.cursor = '';
      repaint();
    },
    // The marks and dots drawn last frame, for checking from a script.
    marks: () => ({ n: LM.length, dots: SV.dots.length, on: SV.on })
  };

  // ---- The widest-reaching funders, as a list in the panel ----
  // Offices the map already groups as one body (same name and country) are one funder here, whatever keys the records use.
  let TOP = null;
  function buildTop() {
    if (!recById || !HQ || TOP) return;
    const groups = new Map();
    keyIndex.forEach((ids, key) => {
      const o = HQ.byKey.get(key), g = o ? `${o.n}|${o.co}` : key;
      let e = groups.get(g); if (!e) groups.set(g, e = { keys: [], ids: new Set(), names: new Map(), kinds: new Map(), hub: o || null });
      e.keys.push(key); ids.forEach(id => e.ids.add(id));
    });
    recById.forEach(rec => rec.nodes.forEach(n => {
      if (!FUNDER(n) || !n[5]) return;
      const o = HQ.byKey.get(n[5]), e = groups.get(o ? `${o.n}|${o.co}` : n[5]); if (!e) return;
      e.names.set(n[0], (e.names.get(n[0]) || 0) + 1); e.kinds.set(n[1], (e.kinds.get(n[1]) || 0) + 1);
    }));
    const top = (m, tie) => [...m.entries()].sort((a, b) => b[1] - a[1] || tie(a[0], b[0]))[0][0];
    TOP = [...groups.values()].filter(e => e.names.size).map(e => ({
      keys: e.keys, n: e.ids.size, hub: e.hub, kind: top(e.kinds, () => 0),
      name: e.hub ? e.hub.n : top(e.names, (a, b) => b.length - a.length)
    })).filter(t => t.n >= 2).sort((a, b) => b.n - a.n || a.name.localeCompare(b.name));
    renderTop();
  }
  function hubOf(t) { return t.hub || recById.get([...(keyIndex.get(t.keys[0]) || [])][0]); }
  function pickTop(t, pin) {
    if (REACH && REACH.pinned && !pin) return;
    clearTimeout(reachTimer); reachTimer = 0;
    const same = REACH && REACH.top === t;
    if (pin && same && REACH.pinned) { clearReach(); return; }
    REACH = { key: t.keys[0], keys: t.keys, kind: t.kind, space: hubOf(t), name: t.name, top: t, pinned: !!pin };
    if (pin && typeof window.flyTo === 'function' && REACH.space && typeof REACH.space.lat === 'number') {
      const base = window.getBaseRadius ? window.getBaseRadius() : 276;
      window.flyTo(REACH.space.lon, REACH.space.lat, base * 1.6);
    }
    renderTop(); repaint();
  }
  function renderTop() {
    const box = document.getElementById('topFunders'); if (!box || !TOP) return;
    const list = TOP.filter(t => kindOn(t.kind)).slice(0, 10), max = list.length ? list[0].n : 1;
    box.textContent = '';
    list.forEach(t => {
      const b = document.createElement('button'); b.type = 'button'; b.className = 'top-funder';
      b.setAttribute('aria-pressed', String(!!(REACH && REACH.pinned && REACH.top === t)));
      b.innerHTML = `<i class="shape-${KIND_SHAPE[t.kind]}" style="--marker-color:${COL[t.kind]}"></i><span class="tf-name"></span><span class="tf-bar"><b style="width:${Math.round(100 * t.n / max)}%"></b></span><span class="tf-n">${t.n}</span>`;
      b.querySelector('.tf-name').textContent = t.name;
      b.title = `${t.name}: named on ${t.n} spaces. Click to pin its connections on the map.`;
      b.addEventListener('mouseenter', () => pickTop(t, false));
      b.addEventListener('focus', () => pickTop(t, false));
      b.addEventListener('mouseleave', () => { if (REACH && !REACH.pinned && REACH.top === t) clearReach(); });
      b.addEventListener('blur', () => { if (REACH && !REACH.pinned && REACH.top === t) clearReach(); });
      b.addEventListener('click', () => pickTop(t, true));
      box.appendChild(b);
    });
  }

  function init() {
    const box = document.getElementById('layersControl'); if (!box) return;
    const btn = box.querySelector('#layersBtn'), panel = box.querySelector('#layersPanel');
    const placePanel = () => {
      panel.classList.remove('is-above');
      const buttonRect = btn.getBoundingClientRect();
      // The room is the globe's, not the window's: the page header above and the phone's tab bar below are not free space.
      const host = box.offsetParent ? box.offsetParent.getBoundingClientRect() : { top: 0, bottom: window.innerHeight };
      const spaceBelow = host.bottom - buttonRect.bottom - 12;
      const spaceAbove = buttonRect.top - host.top - 12;
      const placeAbove = panel.scrollHeight > spaceBelow && spaceAbove > spaceBelow;
      panel.classList.toggle('is-above', placeAbove);
      panel.style.maxHeight = `${Math.max(120, placeAbove ? spaceAbove : spaceBelow)}px`;
    };
    const setOpen = open => {
      panel.hidden = !open;
      btn.setAttribute('aria-expanded', String(open));
      if (open) { placePanel(); loadMoney(); loadHq(); }
    };
    btn.addEventListener('click', () => setOpen(panel.hidden));
    box.querySelector('.layers-close').addEventListener('click', () => { setOpen(false); btn.focus(); });
    box.querySelector('.layers-reset').addEventListener('click', () => {
      box.querySelectorAll('input[data-layer]').forEach(input => {
        input.checked = false;
        L[input.dataset.layer] = false;
      });
      box.querySelectorAll('input[data-kind]').forEach(input => { input.checked = true; L.kinds[input.dataset.kind] = true; });
      clearReach();
      repaint();
    });
    document.addEventListener('click', e => { if (!panel.hidden && !box.contains(e.target)) setOpen(false); });
    document.addEventListener('keydown', e => { if (e.key === 'Escape') { clearReach(); if (!panel.hidden) setOpen(false); } });
    window.addEventListener('resize', () => { if (!panel.hidden) placePanel(); });
    box.querySelectorAll('input[data-layer]').forEach(inp => inp.addEventListener('change', () => {
      const k = inp.dataset.layer;
      L[k] = inp.checked;
      if (k !== 'flags' && k !== 'grade' && inp.checked) loadMoney();
      if ((k === 'hq' || k === 'people') && inp.checked) loadHq();
      repaint();
    }));
    box.querySelectorAll('input[data-kind]').forEach(inp => inp.addEventListener('change', () => {
      L.kinds[inp.dataset.kind] = inp.checked;
      renderTop();
      repaint();
    }));
    updateCounts();
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
