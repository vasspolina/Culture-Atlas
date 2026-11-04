// Funding views: other ways to draw the funding data over the globe, beside the lines of assets/layers.js.
// Bundled lines (the shared-funder web gathered into one trunk per pair of countries), flows between countries (from the
// country of a funder's head office to the country of each space it funds), countries shaded by how much of their funding comes
// from abroad or by their main funder type, funder territories (a shaded area around the spaces a funder pays for), the funding
// mix on each space (a ring split by funder type), the shared-funder glow (with a space in focus, every space that shares a funder
// with it glows), funders above the globe (the widest-reaching funders float over their head office, higher the more spaces they
// fund), flagged money only, and a decade filter on the years the funding lines name.
// layers.js calls under() before the dots and over() after them; index.html asks countryFill() for each country's ground.
(function () {
  const NEW = ['bundle', 'flows', 'hulls', 'choro', 'glyphs', 'halos', 'lifted', 'flagged'];
  const KIND_WORD = { gov: 'Public funding', corp: 'Company', found: 'Foundation' };
  const ABROAD = '#2dd4bf';
  const rad = Math.PI / 180;
  const api = () => window.atlasLayersAPI;
  const V = window.atlasFundingViews = { keys: NEW };
  V.any = L => NEW.some(k => L[k]) || !!L.years;

  // ---- Countries: the records, the offices and the map's outlines spell some of them differently ----
  const CN = { 'UK': 'United Kingdom', 'USA': 'United States of America', 'United States': 'United States of America', 'Czechia': 'Czech Republic', 'DR Congo': 'Democratic Republic of the Congo', "Côte d'Ivoire": 'Ivory Coast', 'North Macedonia': 'Macedonia', 'Tanzania': 'United Republic of Tanzania', 'UAE': 'United Arab Emirates', 'Palestine': 'West Bank', 'Serbia': 'Republic of Serbia' };
  const SHORT = { 'United States of America': 'USA', 'United Kingdom': 'UK', 'United Arab Emirates': 'UAE', 'Democratic Republic of the Congo': 'DR Congo', 'United Republic of Tanzania': 'Tanzania', 'West Bank': 'Palestine', 'Republic of Serbia': 'Serbia' };
  const norm = c => (c ? (CN[c.trim()] || c.trim()) : '');
  const say = c => SHORT[c] || c;
  // The country a funder sits in: its head office's, else the country its key carries ('aarhusmunicipality|Denmark').
  function funderCountry(key, HQ) {
    if (!key) return '';
    const o = HQ && HQ.byKey.get(key);
    if (o && o.co) return norm(o.co);
    const bar = key.indexOf('|');
    return bar > 0 ? norm(key.slice(bar + 1)) : '';
  }

  // ---- Years: the funding line is the only place a record gives one ----
  const yearCache = new WeakMap();
  function yearsOf(rec) {
    let y = yearCache.get(rec);
    if (!y) { y = ((rec.f || '') + ' ' + (rec.why || '')).match(/\b(19[4-9]\d|20[0-2]\d)\b/g) || []; y = [...new Set(y.map(Number))]; yearCache.set(rec, y); }
    return y;
  }
  V.recInWindow = rec => {
    const L = window.atlasLayers; if (!L || !L.years) return true;
    return yearsOf(rec).some(y => y >= L.years[0] && y <= L.years[1]);
  };

  // ---- Derived tables, built once the data is in ----
  let T = null;
  function tables() {
    const A = api(); if (!A) return null;
    const d = A.data(); if (!d.recById) return null;
    if (T && T.rec === d.recById && T.hq === d.HQ && T.kinds === kindSig() && T.years === yearSig()) return T;
    const L = window.atlasLayers;
    // Where each country sits on the globe: the mean of its spaces and offices.
    const anchors = new Map();
    const add = (c, lat, lon) => { if (!c || typeof lat !== 'number') return; let a = anchors.get(c); if (!a) anchors.set(c, a = { lat: 0, lon: 0, n: 0, x: 0, y: 0, z: 0 }); const p = lat * rad, l = lon * rad; a.x += Math.cos(p) * Math.sin(l); a.y += Math.sin(p); a.z += Math.cos(p) * Math.cos(l); a.n++; };
    d.recById.forEach(rec => add(norm(rec.co), rec.lat, rec.lon));
    if (d.HQ) d.HQ.orgs.forEach(o => add(norm(o.co), o.lat, o.lon));
    anchors.forEach(a => { a.lat = Math.atan2(a.y, Math.hypot(a.x, a.z)) / rad; a.lon = Math.atan2(a.x, a.z) / rad; });
    // Per country of the spaces: links with a funder of known country, how many come from abroad, and the funder types.
    const country = new Map(), flows = new Map();
    d.recById.forEach(rec => {
      const co = norm(rec.co); if (!co || !V.recInWindow(rec)) return;
      let s = country.get(co); if (!s) country.set(co, s = { known: 0, abroad: 0, kinds: { gov: 0, corp: 0, found: 0 }, spaces: 0 });
      s.spaces++;
      rec.nodes.forEach(n => {
        if (!A.FUNDER(n) || !A.kindOn(n[1])) return;
        s.kinds[n[1]]++;
        const fc = funderCountry(n[5], d.HQ); if (!fc) return;
        s.known++;
        if (fc === co) return;
        s.abroad++;
        const k = fc + '>' + co; let f = flows.get(k);
        if (!f) flows.set(k, f = { from: fc, to: co, n: 0, kinds: { gov: 0, corp: 0, found: 0 }, names: new Map() });
        f.n++; f.kinds[n[1]]++; f.names.set(n[0], (f.names.get(n[0]) || 0) + 1);
      });
    });
    const top = m => Object.keys(m).sort((a, b) => m[b] - m[a])[0];
    const flowList = [...flows.values()].filter(f => f.n >= 2 && anchors.has(f.from) && anchors.has(f.to)).sort((a, b) => b.n - a.n).slice(0, 90);
    flowList.forEach(f => { f.kind = top(f.kinds); f.top = [...f.names.entries()].sort((a, b) => b[1] - a[1]).slice(0, 3).map(e => e[0]); });
    // The shared-funder web, gathered by pair of countries: a trunk between the two countries' anchors per funder type.
    const trunks = new Map(), feeders = new Map(), local = [];
    (d.web || []).forEach(([a, b, kind, key]) => {
      if (!A.kindOn(kind) || !V.recInWindow(a) || !V.recInWindow(b)) return;
      const ca = norm(a.co), cb = norm(b.co);
      if (!ca || !cb || !anchors.has(ca) || !anchors.has(cb)) return;
      if (ca === cb) { local.push([a, b, kind, key]); return; }
      const [p, q] = ca < cb ? [ca, cb] : [cb, ca], k = p + '|' + q;
      let t = trunks.get(k); if (!t) trunks.set(k, t = { a: p, b: q, n: 0, kinds: { gov: 0, corp: 0, found: 0 }, keys: new Map() });
      t.n++; t.kinds[kind]++; t.keys.set(key, (t.keys.get(key) || 0) + 1);
      [[a, ca], [b, cb]].forEach(([rec, c]) => { const fk = rec.id + '|' + kind; if (!feeders.has(fk)) feeders.set(fk, [rec, c, kind]); });
    });
    trunks.forEach(t => { t.kind = top(t.kinds); });
    T = { rec: d.recById, hq: d.HQ, kinds: kindSig(), years: yearSig(), anchors, country, flows: flowList, trunks: [...trunks.values()].sort((a, b) => a.n - b.n), feeders: [...feeders.values()], local };
    if (L && L.choro) A.repaint();
    return T;
  }
  const kindSig = () => { const L = window.atlasLayers; return L ? ['gov', 'corp', 'found'].map(k => L.kinds[k] !== false ? 1 : 0).join('') : ''; };
  const yearSig = () => { const L = window.atlasLayers; return L && L.years ? L.years.join('-') : ''; };

  // ---- Drawing helpers ----
  const vec = (lat, lon) => { const p = lat * rad, l = lon * rad; return [Math.cos(p) * Math.sin(l), Math.sin(p), Math.cos(p) * Math.cos(l)]; };
  // Points along the great circle from a to b, lifted off the ground in the middle by `lift` of the radius.
  function path(project, a, b, r, cx, cy, lift) {
    const va = vec(a.lat, a.lon), vb = vec(b.lat, b.lon);
    const om = Math.acos(Math.max(-1, Math.min(1, va[0] * vb[0] + va[1] * vb[1] + va[2] * vb[2])));
    if (om < 1e-5) return [];
    const so = Math.sin(om), N = Math.max(10, Math.ceil(om * 40)), out = [];
    for (let i = 0; i <= N; i++) {
      const t = i / N, k1 = Math.sin((1 - t) * om) / so, k2 = Math.sin(t * om) / so;
      const x = k1 * va[0] + k2 * vb[0], y = k1 * va[1] + k2 * vb[1], z = k1 * va[2] + k2 * vb[2];
      const pt = project(Math.atan2(x, z) / rad, Math.atan2(y, Math.hypot(x, z)) / rad, r * (1 + lift * Math.sin(Math.PI * t) * Math.min(1, om)), cx, cy);
      pt.t = t; out.push(pt);
    }
    return out;
  }
  // Stroke a path's visible runs, each segment at the width width(t) gives; the runs answer the pointer with `tag`.
  function strokePath(ctx, pts, width, tag) {
    const A = api();
    let run = null;
    for (let i = 1; i < pts.length; i++) {
      const p = pts[i - 1], q = pts[i];
      if (!p.front || !q.front) { run = null; continue; }
      ctx.lineWidth = width(q.t); ctx.beginPath(); ctx.moveTo(p.x, p.y); ctx.lineTo(q.x, q.y); ctx.stroke();
      if (tag) { if (!run) { run = { tag, pts: [p.x, p.y] }; A.pushRun(run); } run.pts.push(q.x, q.y); }
    }
  }
  const visible = (pt, r, cx, cy) => pt.front || Math.hypot(pt.x - cx, pt.y - cy) > r;

  // ---- Under the dots ----
  V.under = function (ctx, project, r, cx, cy, sel, hov, baseRadius) {
    const A = api(), L = window.atlasLayers; if (!A || !L) return;
    if (!NEW.some(k => L[k])) return;
    const d = A.data(); if (!d.recById) { A.loadMoney(); return; }
    if ((L.flows || L.choro || L.lifted || L.flagged) && !d.HQ) A.loadHq();
    const t = tables(); if (!t) return;
    const focus = hov || sel, rec = focus && d.recById.get(focus.id);
    ctx.save(); ctx.lineCap = 'round';
    if (L.hulls) drawHulls(ctx, project, r, cx, cy, A, d);
    if (L.bundle && !rec) drawBundle(ctx, project, r, cx, cy, A, t, baseRadius);
    if (L.flows) drawFlows(ctx, project, r, cx, cy, A, t);
    if (L.flagged) drawFlagged(ctx, project, r, cx, cy, A, d, rec);
    if (L.lifted) drawLiftedLines(ctx, project, r, cx, cy, A, d);
    ctx.restore();
  };

  function drawBundle(ctx, project, r, cx, cy, A, t, baseRadius) {
    // A pair of countries joined by one link only shows once the view is close; at the world view the trunks carry the picture.
    const close = r >= baseRadius * 2.5, shown = t.trunks.filter(tr => close || tr.n >= 2);
    const feed = new Set(); shown.forEach(tr => { feed.add(tr.a); feed.add(tr.b); });
    // Feeders: each space to its country's anchor, faint.
    ctx.globalAlpha = 0.18; ctx.lineWidth = 0.6;
    t.feeders.forEach(([rec, c, kind]) => {
      if (!feed.has(c)) return;
      const a = t.anchors.get(c); if (!a) return;
      ctx.strokeStyle = A.COL[kind];
      strokePath(ctx, path(project, rec, a, r, cx, cy, 0.01), () => 0.6, null);
    });
    // Ties inside one country stay as they are, faint.
    ctx.globalAlpha = 0.15;
    t.local.forEach(([a, b, kind]) => { ctx.strokeStyle = A.COL[kind]; strokePath(ctx, path(project, a, b, r, cx, cy, 0.04), () => 0.6, null); });
    // Trunks: one per pair of countries, as thick as the links it carries, in the colour of the funder type most of them are.
    ctx.globalAlpha = 0.65;
    shown.forEach(tr => {
      const a = t.anchors.get(tr.a), b = t.anchors.get(tr.b);
      const top = [...tr.keys.entries()].sort((x, y) => y[1] - x[1]).slice(0, 3);
      const names = top.map(([k]) => { const f = A.funderName(k); return f || k; });
      const w = Math.min(10, 0.6 + 1.1 * Math.sqrt(tr.n));
      ctx.strokeStyle = A.lineCol(A.COL[tr.kind]);
      const mix = ['gov', 'found', 'corp'].filter(k => tr.kinds[k]).map(k => `${tr.kinds[k]} ${KIND_WORD[k].toLowerCase()}`).join(', ');
      strokePath(ctx, path(project, a, b, r, cx, cy, 0.08), () => w, {
        agg: true, id: 'bundle:' + tr.a + tr.b, col: A.COL[tr.kind],
        label: `${say(tr.a)} – ${say(tr.b)}`, sub: `${tr.n} shared-funder ${tr.n === 1 ? 'link' : 'links'}: ${mix}`,
        sub2: names.length ? 'Most: ' + names.join(', ') : '', ask: `Which funders link spaces in ${say(tr.a)} and ${say(tr.b)}?`
      });
    });
    ctx.globalAlpha = 1;
  }

  function drawFlows(ctx, project, r, cx, cy, A, t) {
    // Ribbons from the funders' country to the spaces' country: thick at the source, thin at the end, with a dot on the end.
    const max = t.flows.length ? t.flows[0].n : 1;
    ctx.globalAlpha = 0.7;
    t.flows.slice().reverse().forEach(f => {
      const a = t.anchors.get(f.from), b = t.anchors.get(f.to), col = A.lineCol(A.COL[f.kind]);
      const w = 1.2 + 9 * Math.sqrt(f.n / max);
      ctx.strokeStyle = col;
      const pts = path(project, a, b, r, cx, cy, 0.14);
      strokePath(ctx, pts, s => Math.max(0.8, w * (1 - 0.8 * s)), {
        agg: true, id: 'flow:' + f.from + '>' + f.to, col: A.COL[f.kind],
        label: `${say(f.from)} → ${say(f.to)}`, sub: `${f.n} ties from funders based in ${say(f.from)} to spaces in ${say(f.to)}`,
        sub2: 'Most: ' + f.top.join(', '), ask: `Which funders based in ${say(f.from)} fund spaces in ${say(f.to)}?`
      });
      const end = pts[pts.length - 1];
      if (end && end.front) { ctx.beginPath(); ctx.arc(end.x, end.y, 2.6, 0, Math.PI * 2); ctx.fillStyle = col; ctx.fill(); }
    });
    ctx.globalAlpha = 1;
  }

  // Funder territories: the spaces a funder pays for, grouped where they lie within about 800 km of each other, each group
  // drawn as the shaded outline around them. The funder under the pointer or pinned is drawn alone; otherwise the six widest-reaching.
  function drawHulls(ctx, project, r, cx, cy, A, d) {
    const reach = A.reach();
    let list;
    if (reach && reach.keys) list = [{ keys: reach.keys, kind: reach.kind, name: reach.name, hot: true }];
    else list = (A.top() || []).filter(x => A.kindOn(x.kind)).slice(0, 6).map(x => ({ keys: x.keys, kind: x.kind, name: x.name }));
    list.forEach(f => {
      const ids = new Set(); f.keys.forEach(k => (d.keyIndex.get(k) || []).forEach(id => ids.add(id)));
      const recs = [...ids].map(id => d.recById.get(id)).filter(q => q && typeof q.lat === 'number' && V.recInWindow(q));
      if (!recs.length) return;
      // Single-linkage groups within 7 degrees.
      const vs = recs.map(q => vec(q.lat, q.lon)), group = recs.map((_, i) => i);
      const find = i => (group[i] === i ? i : (group[i] = find(group[i])));
      const lim = Math.cos(7 * rad);
      for (let i = 0; i < recs.length; i++) for (let j = i + 1; j < recs.length; j++) {
        if (vs[i][0] * vs[j][0] + vs[i][1] * vs[j][1] + vs[i][2] * vs[j][2] > lim) group[find(i)] = find(j);
      }
      const groups = new Map(); recs.forEach((q, i) => { const g = find(i); if (!groups.has(g)) groups.set(g, []); groups.get(g).push(q); });
      const col = A.COL[f.kind] || '#fff';
      groups.forEach(members => {
        const pts = [];
        members.forEach(q => {
          for (let k = 0; k < 10; k++) {
            const a = k / 10 * Math.PI * 2, dl = 1.3 * Math.sin(a), dn = 1.3 * Math.cos(a) / Math.max(0.2, Math.cos(q.lat * rad));
            const p = project(q.lon + dn, Math.max(-89, Math.min(89, q.lat + dl)), r, cx, cy); if (p.front) pts.push([p.x, p.y]);
          }
        });
        if (pts.length < 3) return;
        const hull = convexHull(pts);
        ctx.beginPath(); hull.forEach(([x, y], i) => (i ? ctx.lineTo(x, y) : ctx.moveTo(x, y))); ctx.closePath();
        ctx.fillStyle = A.hexA(A.lineCol(col), f.hot ? 0.24 : 0.15); ctx.fill();
        ctx.globalAlpha = f.hot ? 0.95 : 0.75; ctx.strokeStyle = A.lineCol(col); ctx.lineWidth = f.hot ? 1.6 : 1; ctx.setLineDash([4, 3]); ctx.stroke(); ctx.setLineDash([]); ctx.globalAlpha = 1;
        // The outline answers the pointer as a funding line does: the funder is named and its web lights up.
        const run = { tag: { key: f.keys[0], kind: f.kind }, pts: [] }; hull.concat([hull[0]]).forEach(([x, y]) => run.pts.push(x, y)); A.pushRun(run);
      });
    });
  }
  function convexHull(pts) {
    const p = pts.slice().sort((a, b) => a[0] - b[0] || a[1] - b[1]);
    const cross = (o, a, b) => (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0]);
    const lo = [], up = [];
    p.forEach(q => { while (lo.length >= 2 && cross(lo[lo.length - 2], lo[lo.length - 1], q) <= 0) lo.pop(); lo.push(q); });
    for (let i = p.length - 1; i >= 0; i--) { const q = p[i]; while (up.length >= 2 && cross(up[up.length - 2], up[up.length - 1], q) <= 0) up.pop(); up.push(q); }
    return lo.slice(0, -1).concat(up.slice(0, -1));
  }

  // Flagged money only: from each flagged space, or a space with a right-wing funder, to the head offices of its funders.
  // The flag is recorded on the space, not on any one funder, and the line's label says so.
  function drawFlagged(ctx, project, r, cx, cy, A, d, focusRec) {
    if (!d.HQ) return;
    // A space in focus with flagged ties of its own shows only those; one without keeps the whole picture.
    if (focusRec && !((focusRec.fl || []).length || focusRec.nodes.some(A.RIGHT))) focusRec = null;
    ctx.lineWidth = 0.9;
    d.recById.forEach(rec => {
      if (typeof rec.lat !== 'number' || !V.recInWindow(rec)) return;
      if (focusRec && focusRec !== rec) return;
      const fl = (rec.fl || []).filter(Boolean);
      rec.nodes.forEach(n => {
        if (!A.FUNDER(n) || !n[5] || !A.kindOn(n[1])) return;
        const right = A.RIGHT(n);
        if (!right && !fl.length) return;
        const o = d.HQ.byKey.get(n[5]); if (!o) return;
        const col = right ? A.COL.right : A.COL.flag;
        ctx.globalAlpha = focusRec ? 0.95 : 0.55; ctx.strokeStyle = A.lineCol(col);
        strokePath(ctx, path(project, rec, o, r, cx, cy, 0.12), () => 0.9, {
          agg: true, id: 'flag:' + rec.id + n[5], col,
          label: `${n[0]} → ${rec.n}`, sub: right ? 'Right-wing funder' : `${KIND_WORD[n[1]] || 'Funder'} of a flagged space`,
          sub2: fl.length ? 'Flag on the space: ' + fl.slice(0, 3).join(', ') : '', ask: right ? `What is ${n[0]}'s politics, and how does it fund ${rec.n}?` : `What is the flag on ${rec.n} about?`
        });
      });
    });
    ctx.globalAlpha = 1;
  }

  // Funders above the globe: the widest-reaching funders with a head office, lifted over it by how many spaces they fund.
  let LIFTED = [];
  function liftedList(A, d) {
    if (!d.HQ) return [];
    return (A.top() || []).filter(x => x.hub && x.hub.lat !== undefined && x.hub.n && A.kindOn(x.kind)).slice(0, 24);
  }
  const liftOf = (n, r) => r * (0.05 + 0.045 * Math.log2(Math.max(2, n)));
  function drawLiftedLines(ctx, project, r, cx, cy, A, d) {
    LIFTED = [];
    const reach = A.reach();
    liftedList(A, d).forEach(f => {
      const o = f.hub, h = liftOf(f.n, r);
      const top = project(o.lon, o.lat, r + h, cx, cy), ground = project(o.lon, o.lat, r, cx, cy);
      if (!visible(top, r, cx, cy)) return;
      const col = A.lineCol(A.COL[f.kind]), hot = reach && reach.keys && reach.keys.some(k => f.keys.includes(k));
      // The stem down to the head office.
      if (ground.front) { ctx.globalAlpha = 0.8; ctx.strokeStyle = col; ctx.lineWidth = 0.8; ctx.setLineDash([2, 3]); ctx.beginPath(); ctx.moveTo(ground.x, ground.y); ctx.lineTo(top.x, top.y); ctx.stroke(); ctx.setLineDash([]); }
      // Straight drops from the funder to every space it funds.
      const ids = new Set(); f.keys.forEach(k => (d.keyIndex.get(k) || []).forEach(id => ids.add(id)));
      ctx.globalAlpha = hot ? 0.85 : 0.2; ctx.lineWidth = hot ? 1 : 0.6; ctx.strokeStyle = col;
      ctx.beginPath();
      ids.forEach(id => { const q = d.recById.get(id); if (!q || typeof q.lat !== 'number' || !V.recInWindow(q)) return; const p = project(q.lon, q.lat, r, cx, cy); if (!p.front) return; ctx.moveTo(top.x, top.y); ctx.lineTo(p.x, p.y); });
      ctx.stroke();
      LIFTED.push({ f, x: top.x, y: top.y, front: top.front, hot });
    });
    ctx.globalAlpha = 1;
  }

  // ---- Over the dots ----
  V.over = function (ctx, dots, r, baseRadius, sel, hov, project, cx, cy, boxes) {
    const A = api(), L = window.atlasLayers; if (!A || !L) return;
    const d = A.data(); if (!d.recById) return;
    const dark = document.documentElement.getAttribute('data-theme') === 'dark';
    if (L.glyphs) drawGlyphs(ctx, dots, A, d, dark);
    if (L.halos) drawHalos(ctx, dots, A, d, sel, hov, dark);
    if (L.lifted) drawLiftedNodes(ctx, A, r, baseRadius, boxes, dark);
  };

  // A ring around each space, split by the share of its funders of each type.
  function drawGlyphs(ctx, dots, A, d, dark) {
    const ORDER = ['gov', 'found', 'corp'];
    dots.forEach(dt => {
      const i = dt.inst, rec = i && d.recById.get(i.id); if (!rec || !V.recInWindow(rec)) return;
      const c = { gov: 0, found: 0, corp: 0 };
      rec.nodes.forEach(n => { if (A.FUNDER(n) && A.kindOn(n[1])) c[n[1]]++; });
      const tot = c.gov + c.found + c.corp; if (!tot) return;
      const R = 8.5; let a0 = -Math.PI / 2;
      ctx.lineWidth = 3.4; ctx.lineCap = 'butt';
      ctx.beginPath(); ctx.arc(dt.x, dt.y, R, 0, Math.PI * 2); ctx.strokeStyle = dark ? '#000' : '#fff'; ctx.lineWidth = 5; ctx.stroke(); ctx.lineWidth = 3.4;
      ORDER.forEach(k => {
        if (!c[k]) return;
        const a1 = a0 + c[k] / tot * Math.PI * 2;
        ctx.beginPath(); ctx.arc(dt.x, dt.y, R, a0 + (tot > 1 ? 0.06 : 0), a1); ctx.strokeStyle = A.lineCol(A.COL[k]); ctx.stroke();
        a0 = a1;
      });
      const parts = ORDER.filter(k => c[k]).map(k => `${c[k]} ${KIND_WORD[k].toLowerCase()}`);
      A.pushMark({ x: dt.x, y: dt.y, r: 11, rec: i, col: A.COL[ORDER.slice().sort((a, b) => c[b] - c[a])[0]], label: i.name, sub: 'Funders: ' + parts.join(', '), ask: `Who funds ${i.name}?` });
    });
    ctx.lineCap = 'round';
  }

  // With a space in focus: every space that shares a funder with it glows, brighter the more funders they share.
  function drawHalos(ctx, dots, A, d, sel, hov, dark) {
    const focus = hov || sel, rec = focus && d.recById.get(focus.id); if (!rec) return;
    const shared = new Map();
    rec.nodes.forEach(n => {
      if (!A.FUNDER(n) || !n[5] || !A.kindOn(n[1])) return;
      (d.keyIndex.get(n[5]) || []).forEach(id => {
        if (id === rec.id) return;
        let s = shared.get(id); if (!s) shared.set(id, s = { names: [], kind: n[1] });
        if (!s.names.includes(n[0])) s.names.push(n[0]);
      });
    });
    dots.forEach(dt => {
      const i = dt.inst, s = i && shared.get(i.id); if (!s) return;
      const q = d.recById.get(i.id); if (q && !V.recInWindow(q)) return;
      const col = A.lineCol(A.COL[s.kind]), R = 11 + 4 * Math.min(4, s.names.length);
      const g = ctx.createRadialGradient(dt.x, dt.y, 2, dt.x, dt.y, R);
      g.addColorStop(0, A.hexA(col, dark ? 0.75 : 0.6)); g.addColorStop(0.5, A.hexA(col, 0.25)); g.addColorStop(1, A.hexA(col, 0));
      ctx.beginPath(); ctx.arc(dt.x, dt.y, R, 0, Math.PI * 2); ctx.fillStyle = g; ctx.fill();
      ctx.beginPath(); ctx.arc(dt.x, dt.y, 4.5, 0, Math.PI * 2); ctx.fillStyle = col; ctx.fill(); ctx.lineWidth = 0.8; ctx.strokeStyle = '#000'; ctx.stroke();
      A.pushMark({ x: dt.x, y: dt.y, r: 10, rec: i, col: A.COL[s.kind], label: i.name, sub: `Shares ${s.names.length === 1 ? 'a funder' : s.names.length + ' funders'} with ${rec.n}`, sub2: s.names.slice(0, 3).join(', '), ask: `What do ${i.name} and ${rec.n} have in common?` });
    });
  }

  function drawLiftedNodes(ctx, A, r, baseRadius, boxes, dark) {
    ctx.save(); ctx.font = (dark ? 300 : 400) + ' 13px "Jokker", sans-serif'; ctx.textBaseline = 'middle'; ctx.textAlign = 'left';
    LIFTED.forEach(({ f, x, y, hot }) => {
      const s = 4 + Math.min(6, Math.sqrt(f.n)), col = A.COL[f.kind];
      ctx.beginPath(); ctx.arc(x, y, s, 0, Math.PI * 2); ctx.fillStyle = col; ctx.fill(); ctx.lineWidth = hot ? 1.6 : 0.8; ctx.strokeStyle = dark ? '#fff' : '#000'; ctx.stroke();
      A.pushMark({ x, y, r: s + 4, col, key: f.keys[0], kind: f.kind, space: f.hub, name: f.name, label: f.name, sub: `${KIND_WORD[f.kind] || 'Funder'} · funds ${f.n} spaces`, sub2: `Head office: ${f.hub.c ? f.hub.c + ', ' : ''}${f.hub.co || ''}`, ask: `Which institutions does ${f.name} fund?` });
      // Names when the view is close, or for the funder in play.
      if (!(hot || r >= baseRadius * 2.2)) return;
      const t = f.name.length > 30 ? f.name.slice(0, 28) + '…' : f.name, w = ctx.measureText(t).width + 12, box = { x: x + s + 4, y: y - 10, w, h: 20 };
      if (A.collides(box, boxes)) return;
      boxes.push(box);
      ctx.fillStyle = col; ctx.fillRect(box.x, box.y, w, 20); ctx.fillStyle = '#000'; ctx.fillText(t, box.x + 6, y + 0.5);
    });
    ctx.restore();
  }

  // ---- Countries shaded (index.html asks for each country's fill) ----
  const parse = c => {
    if (c[0] === '#') return [parseInt(c.slice(1, 3), 16), parseInt(c.slice(3, 5), 16), parseInt(c.slice(5, 7), 16)];
    const m = c.match(/\d+(\.\d+)?/g); return m ? m.slice(0, 3).map(Number) : [0, 0, 0];
  };
  const blend = (g, c, t) => { const a = parse(g), b = parse(c); return `rgb(${a.map((v, i) => Math.round(v + (b[i] - v) * t)).join(', ')})`; };
  V.countryFill = function (name, ground) {
    const L = window.atlasLayers; if (!L || !L.choro) return null;
    const t = tables(); if (!t) return null;
    const s = t.country.get(name); if (!s) return null;
    const A = api();
    if (L.choroMode === 'kind') {
      const tot = s.kinds.gov + s.kinds.corp + s.kinds.found; if (!tot) return null;
      const k = Object.keys(s.kinds).sort((a, b) => s.kinds[b] - s.kinds[a])[0];
      return blend(ground, A.lineCol(A.COL[k]), 0.3 + 0.55 * s.kinds[k] / tot);
    }
    if (s.known < 3) return null;
    // Square root: most countries take well under a third from abroad, and a straight scale would leave them all one shade.
    return blend(ground, A.lineCol(ABROAD), 0.12 + 0.78 * Math.sqrt(s.abroad / s.known));
  };
  window.atlasCountryFill = V.countryFill;

  // ---- Counts after each box's name in the panel ----
  V.counts = function (set) {
    const t = tables(); if (!t) return;
    const fmt = n => new Intl.NumberFormat('en-US').format(n);
    set('bundle', `${fmt(t.trunks.length)} trunks`);
    set('flows', `${fmt(t.flows.length)} flows`);
    set('choro', `${fmt([...t.country.values()].filter(s => s.known >= 3).length)} countries`);
    const d = api().data();
    let flagged = 0; d.recById.forEach(rec => { if ((rec.fl || []).length || rec.nodes.some(api().RIGHT)) flagged++; });
    set('flagged', `${fmt(flagged)} spaces`);
    let yrs = 0; d.recById.forEach(rec => { if (yearsOf(rec).length) yrs++; });
    set('years', `${fmt(yrs)} spaces name a year`);
  };
})();
