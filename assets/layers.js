// Map layers drawn over the globe. The panel has five boxes: Funding connections (one box for the funding ties, flagged and
// right-wing funders, the funder network around a space and the funders' head offices), Epstein connections (mentions in the
// files and the offices of the people named), Propaganda, Independent and Artist-run.
// Funder types: a filter on all the funder layers.
// Hovering a funder around a space draws everywhere else it funds. Each layer shows something at every zoom. Ties: the web of funders shared between spaces, the selected space's own
// ties on top. Flags: flagged spaces marked, and a flagged count on each city cluster. Money: a space's funders around
// its dot when it is selected, hovered or the view is close enough. Right and Epstein: a square on each space the
// funding map names, with the sponsor's or the person's name when the space is in focus or the view is close.
(function () {
  const L = window.atlasLayers = { ties: false, flags: false, money: false, right: false, epstein: false, hq: false, people: false, propaganda: false, independent: false, artist: false, openbooks: false, bundle: false, flows: false, hulls: false, choro: false, glyphs: false, halos: false, lifted: false, flagged: false, years: null, choroMode: 'abroad', kinds: { gov: true, corp: true, found: true }, pkinds: { today: true, historical: true } };
  // No two layers share a colour, and none repeats a tier colour of the pins (menthol clean, magenta flagged, yellow unverified)
  // (user, 6 Nov 2026). Open books was the clean tier's cyan and propaganda sat beside the flagged magenta. Every pair below,
  // and every layer against each tier colour and the person grey, is 21 or more apart in CIELAB (dE76) on both grounds.
  const COL = { gov: '#7c9bff', corp: '#63c4fd', found: '#ffa3c8', flag: '#f9ab30', right: '#ff7b6e', epstein: '#d39bff', person: '#e5e7eb', prop: '#ff5fa0', indep: '#3fe05a', artist: '#b7d40c', open: '#0af0b0' };
  // Open books: the clean grade (tier A) — filings linked, no flagged funder or funding protest on record.
  const isOpenBooks = i => i.tier === 'A';
  // Independent and artist-run: the records carry no field for either, so the two layers read the record's own words
  // (its summary, watch note, funding note, focus and name). "Independently verified/audited" is not the space being independent.
  const KIND_TEXT = i => ['highlight', 'watch', 'curatorial_focus', 'funding', 'affiliations_note', 'records_note', 'tier_note', 'name'].map(k => i[k] || '').join(' \n ');
  const INDEP_RE = /\bindependent(?:,? (?:non-?profit|not-for-profit|voluntary-led|non-collecting|artist-run|artist-led))*,? (?:art(?:s)?|contemporary|cultural|exhibition|artist|gallery|institution|cent(?:er|re)|space|museum|charity|organi[sz]ation|non-?profit|not-for-profit|foundation|trust|platform|project space|kunsthalle|art room)\b|\bremains independent\b|\bindependent since\b|\bbecame independent\b/i;
  const ARTIST_RE = /artist[- ](?:run|led|founded|managed|organi[sz]ed|initiated|operated)|run by artists|by artists,? for artists|founded (?:in \d{4} )?by (?:a (?:group|collective) of |\w+ )?artists\b|artists.? collective|artist collective|artist cooperative|self-organi[sz]ed/i;
  const kindCache = new WeakMap();
  function selfKinds(i) {
    let k = kindCache.get(i);
    if (!k) { const t = KIND_TEXT(i); k = { independent: INDEP_RE.test(t), artist: ARTIST_RE.test(t) }; kindCache.set(i, k); }
    return k;
  }
  window.atlasSelfKinds = selfKinds;
  // The pale colours above are the fills of the name blocks (black text on them is 7:1 or better) and read on the black
  // ground of dark mode. On the white ground of light mode they measure 1.2 to 3:1, so the lines, rings and dots that carry
  // the data are drawn in a deeper step of the same hue there: 3.05:1 or better against white at the 0.8 alpha they are drawn at.
  const LINE_LIGHT = { '#7c9bff': '#2f5de0', '#63c4fd': '#026caa', '#ffa3c8': '#b04f95', '#f9ab30': '#a36504', '#ff7b6e': '#d0160a', '#d39bff': '#9b30e8', '#e5e7eb': '#6e798f', '#22d3ee': '#0c889b', '#b7d40c': '#557f00', '#3fe05a': '#0a8a1f', '#0af0b0': '#0a7a48', '#2dd4bf': '#0d9488', '#ff5fa0': '#df0050' };
  const lineCol = c => (document.documentElement.getAttribute('data-theme') === 'dark' ? c : (LINE_LIGHT[c] || c));
  // A hex colour with an alpha, for the halos.
  const hexA = (h, a) => `rgba(${parseInt(h.slice(1, 3), 16)}, ${parseInt(h.slice(3, 5), 16)}, ${parseInt(h.slice(5, 7), 16)}, ${Math.max(0, Math.min(1, a)).toFixed(3)})`;
  // The propaganda marks' glow breathes on a 3.2 second cycle between 0.8 and 1.15 of its resting size. With reduced motion it
  // holds at 1. While any such mark is on screen the globe (and the street map) is asked for another frame every 80ms, which
  // is enough for a slow fade and far below the draw rate of a drag.
  const REDUCE = () => window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const propGlow = () => (REDUCE() ? 1 : 0.975 + 0.175 * Math.sin(performance.now() / 3200 * Math.PI * 2));
  let propTimer = 0;
  // Every flagged layer glows (user, 6 Nov 2026): flagged spaces, right-wing funders, the Epstein files and propaganda.
  const GLOWING = () => L.propaganda || L.flags || L.right || L.epstein;
  function propPulse() {
    if (REDUCE() || propTimer) return;
    propTimer = setTimeout(() => { propTimer = 0; if (!GLOWING()) return; if (window.scheduleRender) window.scheduleRender(); svSchedule(); }, 80);
  }
  // The flagged layers' halo: a radial fade from the mark's colour to nothing, breathing with propGlow. The deeper step of the
  // colour on the light ground, where the pale one would vanish into white.
  // The funder marks (right-wing, Epstein) stack in big cities, so theirs is softer than a lone flagged space's.
  function flagHalo(ctx, x, y, col, R0, a0) {
    const dark = document.documentElement.getAttribute('data-theme') === 'dark', halo = dark ? col : lineCol(col), glow = propGlow();
    const R = R0 * glow, g = ctx.createRadialGradient(x, y, 2, x, y, R);
    g.addColorStop(0, hexA(halo, a0 * glow));
    g.addColorStop(0.5, hexA(halo, a0 * 0.4 * glow));
    g.addColorStop(1, hexA(halo, 0));
    ctx.beginPath(); ctx.arc(x, y, R, 0, Math.PI * 2); ctx.fillStyle = g; ctx.fill();
  }
  // Colour is never the only cue (WCAG 1.4.1): each kind of mark has its own outline, the same ones the key in the layers panel shows.
  const SHAPES = {
    square: null,
    hexagon: [[.25, 0], [.75, 0], [1, .5], [.75, 1], [.25, 1], [0, .5]],
    triangle: [[.5, 0], [1, 1], [0, 1]],
    pentagon: [[.5, 0], [1, .38], [.81, 1], [.19, 1], [0, .38]],
    shield: [[.5, 0], [1, .18], [.9, .72], [.5, 1], [.1, .72], [0, .18]],
    star: [[.5, 0], [.62, .35], [1, .35], [.69, .57], [.81, .95], [.5, .72], [.19, .95], [.31, .57], [0, .35], [.38, .35]]
  };
  const KIND_SHAPE = { gov: 'circle', corp: 'circle', found: 'circle' };
  // Every mark is a dot; the colour says the kind, and the names on the map say it in words too.
  const KIND_WORD = { gov: 'Public funding', corp: 'Company', found: 'Foundation' };
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
  // The people who tie a space to the Epstein files; a flagged space with no named person is labelled with its own name,
  // since a tag that says only "Jeffrey Epstein" tells nothing about the pin it sits on.
  const epsteinOf = rec => (rec.ep || []).map(e => e.p).filter(Boolean).concat((rec.fl || []).indexOf('Epstein-linked') >= 0 && !(rec.ep || []).length ? [rec.n] : []);
  const FUNDER = n => n[1] === 'gov' || n[1] === 'corp' || n[1] === 'found';
  const rad = Math.PI / 180;
  const kindOn = k => L.kinds[k] !== false;
  const PKINDS = ['today', 'historical'];
  const pkindOn = k => L.pkinds[k] !== false;
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
  // The widest-reaching funders switched on in the Layers panel: each stays drawn until its switch is turned off or Reset all.
  const FILTERS = new Set();
  const repaint = () => { if (typeof scheduleRender === 'function') scheduleRender(); svSchedule(); };
  function clearReach() { clearTimeout(reachTimer); reachTimer = 0; if (!REACH) return; REACH = null; if (typeof renderTop === 'function') renderTop(); repaint(); }
  function setReach(m) {
    if (REACH && (REACH.pinned || REACH.tapped)) return;
    if (m && m.key) {
      clearTimeout(reachTimer); reachTimer = 0;
      if (!REACH || REACH.key !== m.key || REACH.space !== m.space) { REACH = { key: m.key, keys: [m.key], kind: m.kind, space: m.space, name: m.name }; repaint(); }
    } else if (!m) {
      if (REACH && !reachTimer) reachTimer = setTimeout(clearReach, 1500);
    } else if (REACH) clearReach();
  }
  let recById = null, keyIndex = null, keyKind = null, web = null, loading = false;

  // ---- The filters narrow the spaces on the map (user's instruction, 6 Nov 2026) ----
  // A map layer about spaces (the six under "Filters") is also a filter: with one on, the map draws only the spaces it is
  // about, over every grade, since the grade switch alone would hide most of them (a propaganda space is rarely graded
  // clean). A widest-reaching funder switched on narrows that further, to the spaces it funds. With nothing on, the map is
  // as it was.
  // One at a time (user, 7 Nov 2026: "make filters above instead of layers, so if clicked it only shows what clicked"): the
  // six are a row of filters over the map, and picking one shows only what it is about. Picking the one that is on, or
  // All spaces, shows every space again. The boxes in the Layers menu are the same six, so they follow the same rule.
  const SPACE_TEST = {
    funding: i => { const rec = recById && recById.get(i.id); return !!(rec && rec.nodes.some(FUNDER)); },
    epstein: i => { const rec = recById && recById.get(i.id); return !!(rec && epsteinOf(rec).length); },
    propaganda: i => !!(i.propaganda && i.propaganda.length),
    independent: i => selfKinds(i).independent,
    openbooks: i => isOpenBooks(i),
    artist: i => selfKinds(i).artist
  };
  const spaceLayersOn = () => Object.keys(SPACE_TEST).filter(k => { const inp = document.querySelector(`#layersPanel input[data-layer="${k}"]`); return !!(inp && inp.checked); });
  const spaceBoxes = () => Object.keys(SPACE_TEST).map(k => document.querySelector(`#layersPanel input[data-layer="${k}"]`)).filter(Boolean);
  // The filter on, or null for every space.
  window.atlasSpaceFilter = () => spaceLayersOn()[0] || null;
  // Make `key` the one filter on (null: none), and redraw.
  function applySpaceFilter(key) {
    spaceBoxes().forEach(inp => setBox(inp, inp.dataset.layer === key));
    refilter();
  }
  window.atlasSetSpaceFilter = function (key) { if (window.atlasSpaceFilter() !== key) applySpaceFilter(key); };
  // The row of filters over the map, built by the phone and desktop layouts into their own strip: one chip per marked
  // filter in its colour from the Layers menu. The pressed chip is the filter on; none is pressed when no filter is on.
  // Returns false until the Layers menu is in the page.
  window.atlasFilterChips = function (host, cls) {
    const list = spaceBoxes(); if (!list.length) return false;
    host.setAttribute('role', 'toolbar'); host.setAttribute('aria-label', 'Show only');
    host.replaceChildren();
    const mk = (key, name, col, title) => {
      const b = document.createElement('button');
      b.type = 'button'; b.className = cls; b.textContent = name; b.title = title;
      if (key) b.dataset.layer = key; else b.dataset.all = '';
      if (col) { b.style.setProperty('--layer-color', col); b.classList.add('has-color'); }
      b.addEventListener('click', () => window.atlasSetSpaceFilter(key && window.atlasSpaceFilter() === key ? null : key));
      host.appendChild(b);
    };
    // Only a box marked data-chip gets a chip, and there is no All spaces chip (the four in index.html; user, 7 Nov 2026:
    // "only keep these 4 on top"): pressing the chip that is on shows every space again, and the row fits beside the box.
    list.filter(inp => inp.hasAttribute('data-chip')).forEach(inp => {
      const label = inp.closest('label'), nm = label && label.querySelector('.layer-name');
      const name = (nm ? nm.textContent : inp.dataset.layer).trim();
      mk(inp.dataset.layer, name, label ? label.style.getPropertyValue('--layer-color') : '', `Show only ${name}; press again to show every space`);
    });
    const paint = () => { const on = window.atlasSpaceFilter(); host.querySelectorAll('button').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.layer ? b.dataset.layer === on : !on))); };
    paint(); document.addEventListener('atlas:filter', paint);
    // The row wraps rather than scrolls (user, 7 Nov 2026: "make the filters row not scroll, fit all on screen"), so its
    // height varies with the width. It is published as --<id>-h on the root, and what sits under the row (the page's name
    // on the desktop, the Layers button and the colour key on a phone) is placed from it in assets/atlas.css.
    if (host.id && 'ResizeObserver' in window) {
      const tell = () => document.documentElement.style.setProperty(`--${host.id}-h`, `${host.offsetHeight}px`);
      new ResizeObserver(tell).observe(host); tell();
    }
    return true;
  };
  // The grade as a filter (user, 10 Nov 2026: "color key needs to be a filter as well"): the colour key's three rows are
  // buttons, one on at a time, pressed again to show every grade. It narrows with whatever other filter is on.
  let GRADE = null;
  const gradeOf = i => (i.tier === 'A' || i.tier === 'B') ? i.tier : 'U';
  const keyRows = () => document.querySelectorAll('#mapColourKey .mck-row[data-grade]');
  const syncKey = () => keyRows().forEach(b => b.setAttribute('aria-pressed', String(GRADE === b.dataset.grade)));
  window.atlasGradeFilter = () => GRADE;
  window.atlasSetGradeFilter = function (g) { g = (g === 'A' || g === 'B' || g === 'U') ? g : null; if (g === GRADE) return; GRADE = g; syncKey(); refilter(); };
  keyRows().forEach(b => b.addEventListener('click', () => window.atlasSetGradeFilter(GRADE === b.dataset.grade ? null : b.dataset.grade)));
  syncKey();
  window.atlasLayerKeep = function () {
    const on = spaceLayersOn();
    let funded = null;
    if (FILTERS.size && keyIndex) { funded = new Set(); FILTERS.forEach(t => t.keys.forEach(k => (keyIndex.get(k) || []).forEach(id => funded.add(id)))); }
    if (!on.length && !funded && !GRADE) return null;
    // Funding and Epstein read the funding maps; until they are in, those two keep nothing, and the map fills in once they load.
    if (on.some(k => k === 'funding' || k === 'epstein') && !recById) loadMoney();
    return i => (!on.length || on.some(k => SPACE_TEST[k](i))) && (!funded || funded.has(i.id)) && (!GRADE || gradeOf(i) === GRADE);
  };
  let pinIndex = null;
  function refilter() {
    if (typeof applyFilters === 'function') { try { applyFilters(); } catch (e) { /* the page's own filter state is not ready yet */ } }
    // The street map's pins are built once per city, so a filter changed while a city is open shows or hides them in place.
    const keep = window.atlasLayerKeep();
    const pins = document.querySelectorAll('.custom-inst-pin[data-entity-id]');
    if (pins.length && typeof ALL_INSTITUTIONS !== 'undefined') {
      if (!pinIndex) { pinIndex = new Map(); ALL_INSTITUTIONS.forEach(i => pinIndex.set(i.id || i.name, i)); }
      pins.forEach(el => { const i = pinIndex.get(el.dataset.entityId); el.style.display = !keep || !i || keep(i) ? '' : 'none'; });
    }
    if (typeof window.atlasLayersFiltered === 'function') window.atlasLayersFiltered();
    repaint();
    // The filter rows over the map repaint from this, whichever way the filter was changed.
    document.dispatchEvent(new CustomEvent('atlas:filter'));
  }
  window.atlasRefilter = refilter;
  // Label type is regular on the light theme and light on the dark one.
  const LW = () => document.documentElement.getAttribute('data-theme') !== 'dark' ? 400 : 300;
  let cityFlags = null;
  // Headquarters of the funders and offices of the people the funding map names (assets/hq.json, built by tools/build_hq.py).
  const KIND = { gov: COL.gov, corp: COL.corp, found: COL.found };
  let HQ = null, hqLoading = false;
  // The mark drawn for each office last frame (x, y on the canvas) so a click, a hover and the keyboard buttons can find it;
  // the one picked in the detail panel (assets/hq-detail.js) and the one under the pointer or keyboard focus.
  let HQ_HITS = [], HQ_LABELS = [], HQ_SEL = null, HQ_HOV = null;
  // Every other mark the layers draw (the dots at the ends of tie lines, funder rings, right-wing and Epstein marks, flag,
  // independent and artist-run marks, the flagged counts) can be found by the pointer too. LM holds the ones drawn last frame, LM_HOV the one under
  // the pointer. A mark that sits on a space's own dot (flag) is "pass": its hover goes to the space, and a click asks
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
      // `also`: the funding keys that name this office today when its own key is an older spelling (tools/hq_aliases.json).
      orgs.forEach(o => (o.also || []).forEach(k => { if (!HQ.byKey.has(k)) HQ.byKey.set(k, o); }));
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
        // 0, 0 is the data's "no coordinates". Draw such a space at its city (or not at all), not in the ocean at 0°, 0°.
        if (rec.lat === 0 && rec.lon === 0) {
          const pin = typeof window.atlasPinOf === 'function' ? window.atlasPinOf(rec) : null;
          if (pin) { rec.lat = pin.lat; rec.lon = pin.lon; } else { delete rec.lat; delete rec.lon; }
        }
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
      if (window.atlasLayerKeep()) refilter(); else repaint();
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
  // The lines drawn last frame, each with the funder it stands for (tag: key, kind, the two spaces it joins), so the pointer
  // can find a line: LINES holds runs of points on the canvas, LINE_HOV the funder whose line is under the pointer.
  let LINES = [], LINE_HOV = null;
  function arc(project, a, b, r, cx, cy, ctx, tag) {
    const va = vec(a.lat, a.lon), vb = vec(b.lat, b.lon);
    const dot = Math.max(-1, Math.min(1, va[0] * vb[0] + va[1] * vb[1] + va[2] * vb[2])), om = Math.acos(dot);
    if (om < 1e-5) return false;
    const so = Math.sin(om), N = Math.max(8, Math.ceil(om * 36));
    ctx.beginPath(); let pen = false, drawn = false, run = null;
    for (let i = 0; i <= N; i++) {
      const t = i / N, k1 = Math.sin((1 - t) * om) / so, k2 = Math.sin(t * om) / so;
      const x = k1 * va[0] + k2 * vb[0], y = k1 * va[1] + k2 * vb[1], z = k1 * va[2] + k2 * vb[2];
      const lat = Math.atan2(y, Math.hypot(x, z)) / rad, lon = Math.atan2(x, z) / rad;
      const pt = project(lon, lat, r * (1 + 0.12 * Math.sin(Math.PI * t) * Math.min(1, om)), cx, cy);
      if (!pt.front) { pen = false; run = null; continue; }
      if (pen) { ctx.lineTo(pt.x, pt.y); drawn = true; } else { ctx.moveTo(pt.x, pt.y); pen = true; }
      if (tag) { if (!run) { run = { tag, pts: [] }; LINES.push(run); } run.pts.push(pt.x, pt.y); }
    }
    if (drawn) ctx.stroke();
    return drawn;
  }
  // The funder a key stands for: its name (the office's, else the longest spelling the records use), kind, every key the
  // map groups with it, the office if it has one, and its entry in the widest-reaching list if it is there.
  function funderOf(key) {
    if (!key || !keyIndex) return null;
    const t = TOP && TOP.find(x => x.keys.includes(key));
    const office = HQ && HQ.byKey.get(key);
    let name = office ? office.n : (t && t.name);
    if (!name) {
      const names = new Map();
      (keyIndex.get(key) || []).forEach(id => { const q = recById.get(id); if (q) q.nodes.forEach(n => { if (n[5] === key) names.set(n[0], (names.get(n[0]) || 0) + 1); }); });
      name = [...names.entries()].sort((a, b) => b[1] - a[1] || b[0].length - a[0].length).map(e => e[0])[0] || key;
    }
    const keys = t ? t.keys : [key];
    return { key, keys, kind: keyKind.get(key), name, office: office || null, top: t || null, space: t ? hubOf(t) : recById.get((keyIndex.get(key) || [])[0]) };
  }
  // The spaces a funder is named on, and how many countries they sit in.
  function reachOfKeys(keys) {
    const ids = new Set(), cs = new Set();
    keys.forEach(k => (keyIndex.get(k) || []).forEach(id => { ids.add(id); const q = recById.get(id); if (q && q.co) cs.add(q.co); }));
    return { n: ids.size, countries: cs.size };
  }
  // The line under the point, if any: the nearest run within a few pixels (more for a finger), unless a name block sits there.
  function lineAt(mx, my, dots) {
    if (!LINES.length) return null;
    const touch = window.__lastPointerType === 'touch' || window.__lastPointerType === 'pen', reach = touch ? 10 : 5;
    const inBox = b => mx >= b.x && mx <= b.x + b.w && my >= b.y && my <= b.y + b.h;
    if (labelBoxesOnScreen(dots || []).some(inBox)) return null;
    // A space's own dot under the point takes the pointer; the line gives way.
    if ((dots || []).some(d => Math.hypot((d.renderX ?? d.x) - mx, (d.renderY ?? d.y) - my) <= (touch ? 16 : 9))) return null;
    let best = null, bd = reach;
    for (let i = 0; i < LINES.length; i++) {
      const p = LINES[i].pts;
      for (let k = 2; k < p.length; k += 2) {
        const ax = p[k - 2], ay = p[k - 1], bx = p[k], by = p[k + 1];
        if (Math.min(ax, bx) > mx + bd || Math.max(ax, bx) < mx - bd || Math.min(ay, by) > my + bd || Math.max(ay, by) < my - bd) continue;
        const dx = bx - ax, dy = by - ay, l2 = dx * dx + dy * dy;
        const t = l2 ? Math.max(0, Math.min(1, ((mx - ax) * dx + (my - ay) * dy) / l2)) : 0;
        const d = Math.hypot(mx - (ax + t * dx), my - (ay + t * dy));
        if (d < bd) { bd = d; best = LINES[i].tag; }
      }
    }
    return best;
  }

  const fvOn = () => !!(window.atlasFundingViews && window.atlasFundingViews.any(L));
  const sameInst = (a, b) => !!a && !!b && (a.id ? a.id === b.id : a.name === b.name);

  // Under the dots: the funding ties.
  const streetUp = () => !STREET && typeof window.getIsCityStreetViewActive === 'function' && window.getIsCityStreetViewActive();
  window.atlasLayersDraw = function (ctx, project, r, cx, cy, list, sel, hov, baseRadius) {
    if (streetUp()) return;   // the street map is in front: its own frame draws the layers
    LM = []; LINES = [];
    // The funding views (assets/funding-views.js): bundles, flows, territories, flagged money and funders above the globe.
    if (window.atlasFundingViews) window.atlasFundingViews.under(ctx, project, r, cx, cy, sel, hov, baseRadius);
    if (!L.ties) { drawReach(ctx, project, r, cx, cy); return; }
    if (!recById) { loadMoney(); return; }
    const focus = hov || sel, rec = focus && recById.get(focus.id);
    ctx.save();
    ctx.lineCap = 'round';
    // The whole web, faint when a space is in focus.
    ctx.lineWidth = 0.8;
    // The whole web is a world-view picture: with a space in focus, or zoomed in, only that space's own ties are drawn.
    // With the bundled lines on, the bundles stand for the web.
    const showWeb = !rec && !HQ_HOV && r < baseRadius * 8 && !L.bundle;
    const inYears = window.atlasFundingViews ? window.atlasFundingViews.recInWindow : () => true;
    ctx.globalAlpha = 0.35;
    const W = ctx.canvas.clientWidth || 1e9, H = ctx.canvas.clientHeight || 1e9;
    // The funder under the pointer, or pinned: its whole chain is drawn bright, on top of the rest of the web.
    const hotKeys = REACH ? new Set(REACH.keys || [REACH.key]) : null, hot = [];
    if (showWeb) web.forEach(([a, b, kind, key]) => {
      if (!kindOn(kind) || !inYears(a) || !inYears(b)) return;
      const pa = project(a.lon, a.lat, r, cx, cy), pb = project(b.lon, b.lat, r, cx, cy);
      if (!pa.front && !pb.front) return;
      if ((pa.x < -W || pa.x > 2 * W) && (pb.x < -W || pb.x > 2 * W)) return;
      if ((pa.y < -H || pa.y > 2 * H) && (pb.y < -H || pb.y > 2 * H)) return;
      if (hotKeys && hotKeys.has(key)) { hot.push([a, b, kind, key]); return; }
      ctx.strokeStyle = COL[kind];
      arc(project, a, b, r, cx, cy, ctx, { key, kind, a, b });
    });
    if (hot.length) {
      ctx.globalAlpha = 0.95; ctx.lineWidth = 2;
      hot.forEach(([a, b, kind, key]) => { ctx.strokeStyle = lineCol(COL[kind]); arc(project, a, b, r, cx, cy, ctx, { key, kind, a, b }); });
      ctx.globalAlpha = 0.35; ctx.lineWidth = 0.8;
    }
    // The funder under the pointer or pinned: a line from its office (or, with no office, the hovered line's west end) to every other space that names it.
    ctx.restore(); drawReach(ctx, project, r, cx, cy); ctx.save(); ctx.lineCap = 'round';
    // The focused space's own ties, bright, with a dot at each far end.
    if (rec && typeof rec.lat === 'number') {
      ctx.lineWidth = 0.8; ctx.globalAlpha = 0.8;
      const seen = new Set([rec.id]), ends = [];
      rec.nodes.forEach(n => {
        if (!FUNDER(n) || !n[5] || !kindOn(n[1])) return;
        (keyIndex.get(n[5]) || []).forEach(id => {
          if (seen.has(id) || seen.size > 400) return; seen.add(id);
          const o = recById.get(id); if (!o || typeof o.lat !== 'number') return;
          ctx.strokeStyle = lineCol(COL[n[1]]);
          arc(project, rec, o, r, cx, cy, ctx, { key: n[5], kind: n[1], a: rec, b: o }); ends.push([o, lineCol(COL[n[1]]), COL[n[1]]]);
        });
      });
      ctx.globalAlpha = 1;
      ends.forEach(([o, col, raw]) => {
        const pt = project(o.lon, o.lat, r, cx, cy); if (!pt.front) return;
        const hot = LM_HOV && LM_HOV.rec === o;
        ctx.beginPath(); ctx.arc(pt.x, pt.y, hot ? 6 : 3.5, 0, Math.PI * 2); ctx.fillStyle = col; ctx.fill();
        if (hot) { ctx.lineWidth = 0.8; ctx.strokeStyle = '#000'; ctx.stroke(); }
        LM.push({ x: pt.x, y: pt.y, r: 9, rec: o, col: raw, label: o.n, sub: `Shares a funder with ${rec.n}`, ask: `Who funds ${o.n}?` });
      });
    }
    ctx.restore();
  };

  // The funder under the pointer: a line from its space to every other space that names it, an end dot on each.
  function drawReach(ctx, project, r, cx, cy) {
    if (!recById) return;
    FILTERS.forEach(t => { if (!(REACH && REACH.top === t)) drawOneReach(ctx, project, r, cx, cy, { key: t.keys[0], keys: t.keys, kind: t.kind, space: hubOf(t), name: t.name, top: t }); });
    if (REACH) drawOneReach(ctx, project, r, cx, cy, REACH);
  }
  function drawOneReach(ctx, project, r, cx, cy, R) {
    if (!kindOn(R.kind)) return;
    const home = R.space, ends = [], lc = lineCol(COL[R.kind]), dark = document.documentElement.getAttribute('data-theme') === 'dark';
    if (!home || typeof home.lat !== 'number') return;
    ctx.save(); ctx.lineCap = 'round'; ctx.lineWidth = 0.8; ctx.globalAlpha = 0.9; ctx.strokeStyle = lc;
    const ids = new Set(); (R.keys || [R.key]).forEach(k => (keyIndex.get(k) || []).forEach(id => ids.add(id)));
    ids.forEach(id => {
      const o = recById.get(id); if (!o || o === home || typeof o.lat !== 'number') return;
      arc(project, home, o, r, cx, cy, ctx, { key: R.key, kind: R.kind, a: home, b: o }); ends.push(o);
    });
    ctx.globalAlpha = 1;
    ends.forEach(o => {
      const pt = project(o.lon, o.lat, r, cx, cy); if (!pt.front) return;
      const hot = LM_HOV && LM_HOV.rec === o;
      ctx.beginPath(); ctx.arc(pt.x, pt.y, hot ? 6.5 : 4.5, 0, Math.PI * 2); ctx.fillStyle = lc; ctx.fill();
      ctx.lineWidth = 0.8; ctx.strokeStyle = dark ? '#000' : '#fff'; ctx.stroke();
      LM.push({ x: pt.x, y: pt.y, r: 9, rec: o, col: COL[R.kind], key: R.key, kind: R.kind, space: home, name: R.name, label: o.n, sub: `Funded by ${R.name}`, ask: `Who funds ${o.n}?` });
    });
    ctx.restore();
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
  function drawHighlight(ctx, project, r, baseRadius, cx, cy, sel, hov, boxes, col, namesOf, dx, shape, what, askOf, glows) {
    const close = r >= baseRadius * 22;
    const marks = [];
    recById.forEach(rec => {
      const names = namesOf(rec); if (!names.length || typeof rec.lat !== 'number') return;
      const pt = project(rec.lon, rec.lat, r, cx, cy); if (!pt.front) return;
      const focus = (sel && sel.id === rec.id) || (hov && hov.id === rec.id);
      const mk = { x: pt.x + dx, y: pt.y, r: 9, rec, col, label: names.slice(0, 3).join(', '), sub: `${what}: ${rec.n}`, ask: askOf(rec) };
      marks.push([pt, names, focus, mk]); LM.push(mk);
    });
    ctx.lineWidth = 0.8;
    if (glows && marks.length) { marks.forEach(([pt]) => flagHalo(ctx, pt.x + dx, pt.y, col, 20, 0.5)); propPulse(); }
    marks.forEach(([pt]) => { shapePath(ctx, shape, pt.x + dx, pt.y, 6.5); ctx.fillStyle = col; ctx.fill(); ctx.strokeStyle = '#000'; ctx.stroke(); });
    ctx.textAlign = 'left';
    marks.forEach(([pt, names, focus, mk]) => {
      if (!(focus || close)) return;
      let y = pt.y - 10 - (names.length - 1) * 11;
      names.slice(0, 4).forEach(name => {
        const text = name.length > 28 ? name.slice(0, 26) + '…' : name, tw = ctx.measureText(text).width, w = tw + 28, h = 22;
        const box = { x: pt.x + 10 + dx, y: y - h / 2, w, h };
        if (!collides(box, boxes)) { boxes.push(box); (mk.lboxes = mk.lboxes || []).push(box); drawTag(ctx, box.x, box.y, w, h, col); ctx.fillStyle = '#000'; ctx.fillText(text, box.x + 14, y + 0.5); }
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
      ctx.lineWidth = 0.8; ctx.globalAlpha = 0.85;
      if (L.hq) linkedOrgs.forEach(k => { const o = HQ.byKey.get(k); ctx.strokeStyle = lineCol(KIND[o.k]); arc(project, rec, o, r, cx, cy, ctx); });
      if (L.people) linkedPeople.forEach(n => { const o = HQ.byName.get(n); ctx.strokeStyle = lineCol(COL.person); arc(project, rec, o, r, cx, cy, ctx); });
      ctx.globalAlpha = 1;
    }
    // The picked office's own joins, and the one under the pointer or keyboard focus: an arc to each space it is named on.
    if (recById) [HQ_SEL, HQ_HOV].filter((o, i, a) => o && a.indexOf(o) === i).forEach(o => {
      if (!pts.some(p => p[0] === o)) return;
      ctx.lineWidth = o === HQ_HOV ? 0.8 : 0.8; ctx.globalAlpha = o === HQ_HOV ? 0.9 : 0.8;
      ctx.strokeStyle = lineCol(o.kind === 'org' ? KIND[o.k] : COL.person);
      hq.spaces(o).slice(0, 80).forEach(sp => { if (typeof sp.rec.lat === 'number') arc(project, o, sp.rec, r, cx, cy, ctx); });
      ctx.globalAlpha = 1;
    });
    // marks
    ctx.lineWidth = 0.8;
    pts.forEach(([e, x, y]) => {
      const on = (e.kind === 'org' ? linkedOrgs.has(e.key) : linkedPeople.has(e.n)) || picked(e);
      const s = on ? 7 : (rec ? 3.5 : (e.kind === 'org' && recById ? 4 + Math.min(2.5, Math.sqrt(orgReach(e)) * 0.7) : 5));
      HQ_HITS.push({ e, x, y });
      ctx.globalAlpha = rec && !on ? 0.35 : 1;
      ctx.fillStyle = e.kind === 'org' ? KIND[e.k] : COL.person; ctx.strokeStyle = '#000';
      ctx.beginPath();
      ctx.arc(x, y, s - 0.5, 0, Math.PI * 2);
      ctx.fill(); ctx.stroke();
      if (e === HQ_SEL) {
        // A ring in two colours, so one of them always shows against the ground.
        ctx.globalAlpha = 1; ctx.beginPath(); ctx.arc(x, y, s + 5, 0, Math.PI * 2);
        ctx.lineWidth = 3; ctx.strokeStyle = dark ? '#000' : '#fff'; ctx.stroke();
        ctx.lineWidth = 0.8; ctx.strokeStyle = dark ? '#fff' : '#000'; ctx.stroke(); ctx.lineWidth = 0.8;
      }
    });
    ctx.globalAlpha = 1;
    // City labels are already on the canvas: a diamond that would sit on another city's label shrinks to a small one without its
    // number (the tooltip still gives the count), so the labels stay readable where cities are close.
    const labelBoxes = !STREET && typeof cityBadgeHitboxes !== 'undefined' && Array.isArray(cityBadgeHitboxes) ? cityBadgeHitboxes : [];
    clusters.forEach(list => {
      // The metro area (0.1 degree, about 11 km) is one place: the mark sits at the mean of its pins and takes the commonest city name.
      const n = list.length, mlat = list.reduce((a, e) => a + e.lat, 0) / n, mlon = list.reduce((a, e) => a + e.lon, 0) / n;
      const cn = {}; list.forEach(e => { cn[e.c] = (cn[e.c] || 0) + 1; });
      const e0 = list.find(e => e.c === Object.keys(cn).sort((a, b) => cn[b] - cn[a])[0]), pt = project(mlon, mlat, r, cx, cy); if (!pt.front) return;
      const full = 7 + Math.min(7, Math.sqrt(n) * 1.5), counts = {};
      // A city's label sits right above its pin, so the diamond hangs from the pin (its top tip on it) instead of being centred on it.
      const hits = sz => labelBoxes.some(b => px0 + sz > b.x && px0 - sz < b.x + b.w && pt.y + sz * 2 - 2 > b.y && pt.y - 2 < b.y + b.h);
      const px0 = pt.x, small = !STREET && hits(full), s = small ? 4 : full;
      const px = pt.x, py = pt.y + (STREET ? 0 : s - 2);
      list.forEach(e => { counts[e.k] = (counts[e.k] || 0) + 1; });
      const k = Object.keys(counts).sort((a, b) => counts[b] - counts[a])[0], col = KIND[k] || COL.corp;
      ctx.globalAlpha = rec ? 0.55 : 1; ctx.lineWidth = 0.8; ctx.fillStyle = col; ctx.strokeStyle = '#000';
      ctx.beginPath(); ctx.arc(px, py, s, 0, Math.PI * 2); ctx.fill(); ctx.stroke();
      ctx.globalAlpha = 1; ctx.fillStyle = '#000'; ctx.font = '400 11px "Atlas Serif", "Times New Roman", Times, "EB Garamond", serif'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
      if (!small) ctx.fillText(String(n), px, py + 0.5);
      const names = list.slice(0, 3).map(e => e.n).join(', ') + (n > 3 ? ` and ${n - 3} more` : '');
      LM.push({ x: px, y: py, r: s + 3, col, label: `${e0.c}, ${e0.co}`, sub: `${n} funder offices`, sub2: names, ask: `Which funders are headquartered in ${e0.c}?`,
        go() { if (typeof window.flyTo === 'function') window.flyTo(mlon, mlat, baseRadius * (CLUSTER_AT + 1.5)); } });
    });
    ctx.font = '400 15px "Atlas Serif", "Times New Roman", Times, "EB Garamond", serif';
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

  // Stroke a line except where it passes through a label block (with a 3 px margin), so a tie never runs through text.
  function strokeAround(ctx, x0, y0, x1, y1, bs) {
    const dx = x1 - x0, dy = y1 - y0, iv = [];
    bs.forEach(b => {
      let t0 = 0, t1 = 1;
      for (const [p, q, lo, hi] of [[x0, dx, b.x - 3, b.x + b.w + 3], [y0, dy, b.y - 3, b.y + b.h + 3]]) {
        if (Math.abs(q) < 1e-9) { if (p < lo || p > hi) return; continue; }
        let a = (lo - p) / q, c = (hi - p) / q; if (a > c) [a, c] = [c, a];
        t0 = Math.max(t0, a); t1 = Math.min(t1, c); if (t0 >= t1) return;
      }
      iv.push([t0, t1]);
    });
    iv.sort((a, b) => a[0] - b[0]);
    const seg = (a, c) => { ctx.moveTo(x0 + dx * a, y0 + dy * a); ctx.lineTo(x0 + dx * c, y0 + dy * c); };
    let t = 0; ctx.beginPath();
    iv.forEach(([a, c]) => { if (a > t) seg(t, a); t = Math.max(t, c); });
    if (t < 1) seg(t, 1);
    ctx.stroke();
  }
  // Does the straight spoke from (x0,y0) to (x1,y1) cross a block? The first 12 px, under the space's own mark, do not count.
  function spokeHits(x0, y0, x1, y1, bs, pad) {
    const len = Math.hypot(x1 - x0, y1 - y0), n = Math.ceil(len / 4);
    for (let s = 1; s <= n; s++) {
      const t = s / n; if (t * len < 12) continue;
      const x = x0 + (x1 - x0) * t, y = y0 + (y1 - y0) * t;
      if (bs.some(b => x > b.x - pad && x < b.x + b.w + pad && y > b.y - pad && y < b.y + b.h + pad)) return true;
    }
    return false;
  }
  // The funders of one space, around its dot. Each takes the angle farthest from the ones placed before it where its spoke and
  // its name both fit clear of every label on the map (stepping out to a wider ring when the near one is crowded); the first goes
  // opposite the space's own name block. A funder that fits nowhere keeps the best angle and its name, rather than losing the name.
  // Sets x, y, box (the name's block) on each item, and adds the blocks to `boxes` so later drawing keeps clear of them.
  function placeRing(d, items, R, boxes, W, H, pref) {
    const STEP = Math.PI / 18, TAU = Math.PI * 2, H_ = 24, GAPS = [1, 1.4, 1.8, 2.3];
    const reachBox = R * GAPS[GAPS.length - 1] + 260;
    const near = boxes.filter(b => b.x < d.x + reachBox && b.x + b.w > d.x - reachBox && b.y < d.y + reachBox && b.y + b.h > d.y - reachBox);
    const angles = []; for (let k = 0; k < 36; k++) angles.push(-Math.PI / 2 + k * STEP);
    const sep = (a, b) => { const t = Math.abs(a - b) % TAU; return t > Math.PI ? TAU - t : t; };
    const free = (b, bs) => b.x >= 2 && b.y >= 2 && b.x + b.w <= W - 2 && b.y + b.h <= H - 2 && !bs.some(o => !(b.x + b.w + 2 < o.x || b.x - 2 > o.x + o.w || b.y + b.h + 2 < o.y || b.y - 2 > o.y + o.h));
    const overlap = (b, bs) => bs.reduce((t, o) => t + Math.max(0, Math.min(b.x + b.w, o.x + o.w) - Math.max(b.x, o.x)) * Math.max(0, Math.min(b.y + b.h, o.y + o.h) - Math.max(b.y, o.y)), 0);
    const spots = (x, y, a, w, sr) => {
      const right = Math.cos(a) >= -0.2, up = Math.sin(a) < 0, g = sr + 4;
      const Rt = { x: x + g, y: y - H_ / 2, w, h: H_ }, Lt = { x: x - g - w, y: y - H_ / 2, w, h: H_ };
      const Ab = { x: x - w / 2, y: y - g - H_, w, h: H_ }, Bl = { x: x - w / 2, y: y + g, w, h: H_ };
      return right ? [Rt, up ? Ab : Bl, up ? Bl : Ab, Lt] : [Lt, up ? Ab : Bl, up ? Bl : Ab, Rt];
    };
    // The space's own name block hangs from its dot and reaches only a few px below it: only that part blocks a spoke (a level spoke would run along its lower edge, so those are out).
    const lb = d.labelBox, spokeBlocks = near.map(b => lb && b.x === lb.x && b.y === lb.y ? { x: b.x, y: b.y, w: b.w, h: Math.max(0, d.y - b.y) } : b);
    const placed = [];   // { a, x, y }
    const blocks = near.slice();
    items.forEach((it, i) => {
      let best = null, fallback = null;
      angles.forEach(a => {
        const minSep = placed.length ? Math.min(...placed.map(p => sep(a, p.a))) : Math.PI - sep(a, pref);
        for (let g = 0; g < GAPS.length; g++) {
          const x = d.x + R * GAPS[g] * Math.cos(a), y = d.y + R * GAPS[g] * Math.sin(a);
          if (placed.some(p => Math.hypot(p.x - x, p.y - y) < 26)) continue;
          const mark = { x: x - it.sr - 2, y: y - it.sr - 2, w: it.sr * 2 + 4, h: it.sr * 2 + 4 };
          const spot = !spokeHits(d.x, d.y, x, y, spokeBlocks, 3) && free(mark, blocks) && spots(x, y, a, it.w, it.sr).find(s => free(s, blocks));
          if (spot) { if (!best || minSep > best.s + 1e-6) best = { a, x, y, spot, s: minSep }; break; }
          const sp = spots(x, y, a, it.w, it.sr).map(q => ({ q, o: overlap(q, blocks) + overlap(mark, blocks) })).sort((u, v) => u.o - v.o)[0];
          if (!fallback || sp.o < fallback.o - 1e-6 || (Math.abs(sp.o - fallback.o) < 1e-6 && minSep > fallback.s + 1e-6)) fallback = { a, x, y, spot: sp.q, s: minSep, o: sp.o };
        }
      });
      const pick = best || fallback || { a: pref + i, x: d.x + R, y: d.y, spot: spots(d.x + R, d.y, 0, it.w, it.sr)[0] };
      it.x = pick.x; it.y = pick.y; it.box = pick.spot;
      placed.push({ a: pick.a, x: pick.x, y: pick.y });
      blocks.push(pick.spot, { x: pick.x - it.sr - 2, y: pick.y - it.sr - 2, w: it.sr * 2 + 4, h: it.sr * 2 + 4 });
      boxes.push(pick.spot);
    });
  }
  function drawNodes(ctx, dots, r, baseRadius, sel, hov, gossip, project, cx, cy) {
    if (!REACH && !L.flags && !L.money && !L.right && !L.epstein && !L.hq && !L.people && !L.propaganda && !L.ties && !L.independent && !L.artist && !L.openbooks && !fvOn()) return;
    if ((L.money || L.right || L.epstein || L.hq || L.people) && !recById) loadMoney();
    if ((L.hq || L.people) && !HQ) loadHq();
    const dark = document.documentElement.getAttribute('data-theme') === 'dark';
    const font = '400 15px "Atlas Serif", "Times New Roman", Times, "EB Garamond", serif';
    const boxes = labelBoxesOnScreen(dots);
    ctx.save();
    ctx.font = font; ctx.textBaseline = 'middle';

    if (L.openbooks) {
      // Open-books spaces: the space's own dot glows mint (no longer the clean tier's cyan, so the two never read as one).
      const openCol = lineCol(COL.open);
      ctx.lineWidth = 0.8;
      dots.forEach(d => {
        const i = d.inst; if (!i || !isOpenBooks(i)) return;
        LM.push({ x: d.x, y: d.y, r: 9, rec: i, col: openCol, label: 'Open books', sub: i.name, ask: `What do the filings show for ${i.name}?` });
        ctx.save();
        ctx.shadowColor = openCol; ctx.shadowBlur = dark ? 16 : 10;
        ctx.fillStyle = openCol;
        shapePath(ctx, 'circle', d.x, d.y, 5); ctx.fill(); ctx.fill();
        ctx.restore();
        shapePath(ctx, 'circle', d.x, d.y, 5); ctx.fillStyle = openCol; ctx.fill(); ctx.strokeStyle = '#000'; ctx.stroke();
      });
    }
    if (L.independent || L.artist) {
      // Independent spaces: the space's own dot glows green (a soft halo under a filled green dot with the usual ink outline).
      // Artist-run spaces: a small lime dot just above the space's own dot (the propaganda marks sit below it).
      const indepCol = lineCol(COL.indep);
      ctx.lineWidth = 0.8;
      dots.forEach(d => {
        const i = d.inst; if (!i) return;
        const k = selfKinds(i);
        if (L.independent && k.independent) {
          LM.push({ x: d.x, y: d.y, r: 9, rec: i, col: indepCol, label: 'Independent space', sub: i.name, ask: `How is ${i.name} independent?` });
          ctx.save();
          ctx.shadowColor = indepCol; ctx.shadowBlur = dark ? 16 : 10;
          ctx.fillStyle = indepCol;
          shapePath(ctx, 'circle', d.x, d.y, 5); ctx.fill(); ctx.fill();
          ctx.restore();
          shapePath(ctx, 'circle', d.x, d.y, 5); ctx.fillStyle = indepCol; ctx.fill(); ctx.strokeStyle = '#000'; ctx.stroke();
        }
        if (L.artist && k.artist) {
          const x = d.x, y = d.y - 12;
          LM.push({ x, y, r: 8, rec: i, col: COL.artist, label: 'Artist-run space', sub: i.name, ask: `Who runs ${i.name}?` });
          shapePath(ctx, 'circle', x, y, 6); ctx.fillStyle = COL.artist; ctx.fill(); ctx.strokeStyle = '#000'; ctx.stroke();
        }
      });
    }
    if (L.flags) {
      // Each flagged space: a filled orange dot over its ring, glowing like the other flagged layers.
      ctx.lineWidth = 0.8;
      let flagged = 0;
      dots.forEach(d => {
        const i = d.inst; if (!i || !i.flags || !i.flags.length) return;
        LM.push({ x: d.x, y: d.y, r: 8, pass: true, rec: i, ask: `What is reported about ${i.name}?` });
        flagHalo(ctx, d.x, d.y, COL.flag, 22, 0.75); flagged++;
        shapePath(ctx, 'circle', d.x, d.y, 4.6);
        ctx.fillStyle = COL.flag; ctx.fill();
        ctx.strokeStyle = '#000'; ctx.stroke();
      });
      if (flagged) propPulse();
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

    if (L.propaganda) {
      // Each space a state or regime has used as an instrument of propaganda: a glowing pink dot just below its own dot, filled
      // when it is used that way now, a ring when it was in a past period. A space with both shows both side by side. The glow
      // is a soft halo under the mark that breathes slowly; it holds still when the system asks for reduced motion.
      const glow = propGlow(), halo = dark ? COL.prop : lineCol(COL.prop);
      let drawn = 0;
      ctx.lineWidth = 0.8;
      dots.forEach(d => {
        const i = d.inst; if (!i || !i.propaganda || !i.propaganda.length) return;
        const marks = PKINDS.filter(k => pkindOn(k) && i.propaganda.some(p => p.kind === k));
        marks.forEach((k, n) => {
          const p = i.propaganda.find(q => q.kind === k), x = d.x + (n - (marks.length - 1) / 2) * 14, y = d.y + 12;
          LM.push({ x, y, r: 8, rec: i, col: COL.prop, label: k === 'today' ? 'Used for propaganda now' : 'Used for propaganda in the past', sub: `${i.name}, ${p.period}`, sub2: p.mechanism ? p.mechanism[0].toUpperCase() + p.mechanism.slice(1) : '', ask: `How is ${i.name} used for propaganda?` + (k === 'today' ? '' : ` (${p.period})`) });
          drawn++;
          // The halo: a radial fade from the mark's colour to nothing, wider and brighter for a space used that way now.
          const R = (k === 'today' ? 20 : 15) * glow;
          const g = ctx.createRadialGradient(x, y, 2, x, y, R);
          g.addColorStop(0, hexA(halo, (k === 'today' ? 0.55 : 0.38) * glow));
          g.addColorStop(0.5, hexA(halo, (k === 'today' ? 0.22 : 0.14) * glow));
          g.addColorStop(1, hexA(halo, 0));
          ctx.beginPath(); ctx.arc(x, y, R, 0, Math.PI * 2); ctx.fillStyle = g; ctx.fill();
          if (k === 'today') { shapePath(ctx, 'circle', x, y, 6); ctx.fillStyle = COL.prop; ctx.fill(); ctx.strokeStyle = '#000'; ctx.stroke(); }
          else { ctx.beginPath(); ctx.arc(x, y, 5.5, 0, Math.PI * 2); ctx.fillStyle = dark ? '#000' : '#fff'; ctx.fill(); ctx.lineWidth = 1.2; ctx.strokeStyle = lineCol(COL.prop); ctx.stroke(); ctx.lineWidth = 0.8; }
        });
      });
      if (drawn) propPulse();
    }

    // Both highlights on: the Epstein square sits to the right of the right-wing one, so a space in both shows both.
    if (L.right && recById) drawHighlight(ctx, project, r, baseRadius, cx, cy, sel, hov, boxes, COL.right, rec => rec.nodes.filter(RIGHT).map(n => n[0]), L.epstein ? -7 : 0, 'circle', 'Right-wing funder', rec => `Who funds ${rec.n}?`, true);
    if (L.epstein && recById) drawHighlight(ctx, project, r, baseRadius, cx, cy, sel, hov, boxes, COL.epstein, epsteinOf, L.right ? 7 : 0, 'circle', 'Named in the Epstein files', rec => `What is ${rec.n}'s Epstein link?`, true);

    if (L.hq || L.people) drawHq(ctx, project, r, baseRadius, cx, cy, sel, hov, boxes);
    if (window.atlasFundingViews && recById) window.atlasFundingViews.over(ctx, dots, r, baseRadius, sel, hov, project, cx, cy, boxes);

    if (L.money) {
      if (!recById) { ctx.restore(); return; }
      const byKey = new Map(), rings = [];
      // A selected space with no dot of its own (folded into a cluster) still gets its funders.
      const selPin = sel && typeof window.atlasPinOf === 'function' ? window.atlasPinOf(sel) : null;
      if (selPin && !dots.some(d => sameInst(d.inst, sel))) {
        const pt = project(selPin.lon, selPin.lat, r, cx, cy); if (pt.front) dots = dots.concat([{ inst: sel, x: pt.x, y: pt.y }]);
      }
      const W = ctx.canvas.clientWidth || 1e9, H = ctx.canvas.clientHeight || 1e9;
      // First pass: where every funder of the focused space goes, and where its name goes. Each spoke and each name must stay
      // clear of the labels already on the map and of the names placed before it, so nothing is drawn over text and no name is dropped.
      dots.forEach(d => {
        const inst = d.inst, rec = inst && recById.get(inst.id); if (!rec) return;
        const focus = sameInst(sel, inst) || sameInst(hov, inst);
        if (!focus) return;
        const nodes = rec.nodes.filter(n => FUNDER(n) && kindOn(n[1]));
        if (!nodes.length) return;
        // The ring is 64 px when the view is close; further out it shrinks, so funders never land on other cities.
        const zoomK = Math.max(0.4, Math.min(1, r / (baseRadius * 12)));
        const N = Math.min(nodes.length, 10), R = 64 * zoomK;
        const items = nodes.slice(0, N).map(n => {
          // Two pills, as on displaay.net/typefaces: the name filled in its kind's colour, the kind word in an outline beside it.
          const reach = reachOf(n[5]), word = KIND_WORD[n[1]] || '', text = fitWords(n[0], 40);
          const nw = ctx.measureText(text).width + 2 * PILL_PAD, ww = word ? ctx.measureText(word).width + 2 * PILL_PAD : 0;
          return { n, reach, sr: sizeFor(reach.n > 1 ? reach.n : 1), text, word, nw, ww, w: nw + (word ? PILL_GAP + ww : 0) };
        });
        placeRing(d, items, R, boxes, W, H, d.labelBox ? Math.PI / 2 : -Math.PI / 2);
        rings.push({ d, rec, items });
      });
      // Then the ties, under the marks: a funder named on two spaces on screen is joined across them, in a dashed line that breaks around label blocks.
      ctx.save(); ctx.lineWidth = 0.8; ctx.globalAlpha = 0.4; ctx.setLineDash([3, 5]);
      rings.forEach(({ items }) => items.forEach(it => { if (it.n[5]) { if (!byKey.has(it.n[5])) byKey.set(it.n[5], []); byKey.get(it.n[5]).push([it.x, it.y, COL[it.n[1]]]); } }));
      const onScreen = p => p[0] > -40 && p[0] < W + 40 && p[1] > -40 && p[1] < H + 40;
      byKey.forEach(pts => { pts = pts.filter(onScreen); for (let i = 1; i < pts.length; i++) { ctx.strokeStyle = lineCol(pts[i][2]); strokeAround(ctx, pts[0][0], pts[0][1], pts[i][0], pts[i][1], boxes); } });
      ctx.restore();
      // The spokes and marks; each name's block (lbox) answers the pointer as the mark does.
      rings.forEach(({ d, rec, items }) => {
        items.forEach(it => {
          const n = it.n, col = COL[n[1]], x = it.x, y = it.y;
          ctx.globalAlpha = 1;
          ctx.lineWidth = 0.8; ctx.strokeStyle = lineCol(col); ctx.beginPath(); ctx.moveTo(d.x, d.y); ctx.lineTo(x, y); ctx.stroke();
          // A dot in the kind's colour; the name block beside it says the kind in words.
          shapePath(ctx, KIND_SHAPE[n[1]] || 'circle', x, y, it.sr); ctx.fillStyle = dark ? '#000' : '#fff'; ctx.lineWidth = 0.8; ctx.fill(); ctx.stroke(); ctx.lineWidth = 0.8;
          const shared = it.reach.n > 1;
          LM.push({ x, y, r: Math.max(10, it.sr + 4), col, key: n[5], kind: n[1], space: rec, name: n[0], ox: d.x, oy: d.y, label: n[0], sub: `${KIND_WORD[n[1]] || 'Funder'}, funder of ${rec.n}`, lbox: it.box,
            sub2: shared ? `Also funds ${plural(it.reach.n - 1, 'other space')} in ${plural(it.reach.countries, 'country').replace('countrys', 'countries')}` : 'Funds no other space here',
            ask: shared ? `Which institutions does ${n[0]} fund?` : `How does ${n[0]} fund ${rec.n}?` });
        });
      });
      // Funder names as pills at the spot the layout found for each: the name on the funder's colour, then the kind word.
      ctx.globalAlpha = 1; ctx.textAlign = 'left';
      rings.forEach(({ items }) => items.forEach(it => drawFunderPills(ctx, it, dark)));
    }
    TIP_BOXES = boxes;
    ctx.restore();
  }
  // The block naming the mark or line under the pointer is drawn last of all, over the city names (index.html calls this
  // after them; the street map calls it after the nodes), so nothing covers it.
  let TIP_BOXES = [];
  // No longer drawn (user, 11 Nov 2026: "delete hovers"): the map shows no card under the pointer, on the globe or the street
  // map. A click on a mark still does what it did (asks the chat, or opens the funder's record in the sheet).
  window.atlasLayersDrawTip = function () {};
  void drawMarkTip; void TIP_BOXES;
  // The funder badges take their form from displaay.net/typefaces: a pill (fully rounded ends), a 1px edge in the colour of
  // its text, 10px of air either side of the words. The name pill is filled in the kind's colour with black text (the pale
  // fills measure 7:1 or better against black); the kind pill is an outline on the map's own ground, so it reads as a tag
  // to the name and not a second name. The box the layout placed (it.box) holds both, with a 4px gap between them.
  const PILL_PAD = 10, PILL_GAP = 4;
  // A name too long for its pill is cut at the last whole word that fits, never inside a word ("Federal Culture Incentive ..."
  // read as a different law); the hover block then gives the name in full.
  function fitWords(t, n) {
    if (t.length <= n) return t;
    const cut = t.slice(0, n - 1), sp = cut.lastIndexOf(' ');
    return (sp > n / 2 ? cut.slice(0, sp) : cut).replace(/[\s,;:.\-–]+$/, '') + '…';
  }
  function pill(ctx, x, y, w, h, fill, edge) {
    ctx.beginPath(); ctx.roundRect(x + 0.5, y + 0.5, w - 1, h - 1, (h - 1) / 2);
    ctx.fillStyle = fill; ctx.fill(); ctx.lineWidth = 1; ctx.strokeStyle = edge; ctx.stroke();
  }
  function drawFunderPills(ctx, it, dark) {
    const b = it.box, mid = b.y + b.h / 2 + 0.5, ink = dark ? '#fff' : '#000', paper = dark ? '#000' : '#fff';
    // A pill on the left of its mark puts the name next to the mark, so the kind word goes on the outside.
    const left = it.x > b.x + b.w / 2 && it.word;
    const nx = left ? b.x + it.ww + PILL_GAP : b.x, wx = left ? b.x : b.x + it.nw + PILL_GAP;
    ctx.save();
    pill(ctx, nx, b.y, it.nw, b.h, COL[it.n[1]], '#000');
    ctx.fillStyle = '#000'; ctx.fillText(it.text, nx + PILL_PAD, mid);
    if (it.word) { pill(ctx, wx, b.y, it.ww, b.h, paper, ink); ctx.fillStyle = ink; ctx.fillText(it.word, wx + PILL_PAD, mid); }
    ctx.restore();
  }
  // A label, cut like the city labels (rounded, 22 high, 14 either side) but filled in the mark's colour.
  function drawTag(ctx, x, y, w, h, col) {
    ctx.save(); ctx.beginPath(); ctx.roundRect(x, y, w, h, 0); ctx.fillStyle = col; ctx.fill(); ctx.restore();
  }
  // The mark under the pointer: its name on a block in its colour, and that a click asks the chat.
  function drawMarkTip(ctx, boxes) {
    if (!LM_HOV) return;
    // A bundle, flow or flagged tie that is no longer drawn (its view turned off, or the globe turned it away) has no block.
    if (LM_HOV.agg && !LINES.some(run => run.tag && run.tag.id === LM_HOV.aggId)) return;
    const m = LM_HOV.line ? LM_HOV : (LM.find(q => q.ask === LM_HOV.ask && q.rec === LM_HOV.rec && !q.pass) || null); if (!m) return;
    const W = ctx.canvas.clientWidth || 1e9;
    const clip = t => t.length > 64 ? t.slice(0, 62) + '…' : t;
    const act = m.tip || (m.go ? 'Click to zoom in' : (REACH && REACH.tapped && m.key && !m.rec ? 'Tap again to ask the chat' : 'Click to ask the chat'));
    // A funder in a ring already has its name and kind on the map in its own pills, and its spoke says whose funder it is,
    // so the block does not say them again: it adds only what the pills do not (the full name when the pill cut it, how far
    // the funder reaches) and hangs from the pill, as one more line of it, not as a second label piled beside the mark.
    const pinned = !!m.lbox;
    const named = !pinned || fitWords(m.label, 40) !== m.label;
    const lines = [named ? clip(m.label) : null, !pinned && m.sub ? clip(m.sub) : null, m.sub2 ? clip(m.sub2) : null, act].filter(Boolean);
    ctx.save(); ctx.font = '400 15px "Atlas Serif", "Times New Roman", Times, "EB Garamond", serif'; ctx.textAlign = 'left'; ctx.textBaseline = 'middle';
    // A stack of pills, as the funder names are (displaay.net/typefaces): the name filled in the mark's colour, what it is in
    // outlined pills under it, and what a click does as a solid ink pill, as Displaay sets its one action. Each pill is as
    // wide as its own words; the stack hangs from the side nearest the mark.
    const dark = document.documentElement.getAttribute('data-theme') === 'dark', ink = dark ? '#fff' : '#000', paper = dark ? '#000' : '#fff';
    const h = 24, gap = 4, ws = lines.map(t => ctx.measureText(t).width + 2 * PILL_PAD), w = Math.max(...ws);
    // The block goes where it covers the fewest labels: beside the mark, or above or below it; away from the space a funder
    // ring belongs to first, so the ring's other names stay readable.
    const H = ctx.canvas.clientHeight || 1e9, th = h * lines.length + gap * (lines.length - 1), away = m.ox !== undefined ? Math.sign(m.x - m.ox) || 1 : 1;
    const lb = m.lbox, lbLeft = lb && lb.x + lb.w / 2 < m.x;
    const cand = (pinned
      // Under the pill, then over it, lined up on the pill's outer end.
      ? [[lbLeft ? lb.x + lb.w - w : lb.x, lb.y + lb.h + gap], [lbLeft ? lb.x + lb.w - w : lb.x, lb.y - gap - th], [lbLeft ? lb.x - 12 - w : lb.x + lb.w + 12, lb.y]]
      : [[away > 0 ? m.x + 12 : m.x - 12 - w, m.y - th / 2], [away > 0 ? m.x - 12 - w : m.x + 12, m.y - th / 2], [m.x - w / 2, m.y - 12 - th], [m.x - w / 2, m.y + 12]])
      .map(([x, y]) => ({ x: Math.max(4, Math.min(x, W - w - 4)), y: Math.max(4, Math.min(y, H - th - 4)), w, h: th }));
    // Where every spot covers something, the one that covers least, not simply the first: the first was what put the block
    // over the space's own name.
    const others = (boxes || []).filter(o => o !== lb);
    const cover = c => others.reduce((t, o) => t + Math.max(0, Math.min(c.x + c.w, o.x + o.w) - Math.max(c.x, o.x)) * Math.max(0, Math.min(c.y + c.h, o.y + o.h) - Math.max(c.y, o.y)), 0);
    const spot = cand.find(c => !collides(c, others)) || cand.slice().sort((a, b) => cover(a) - cover(b))[0], bx = spot.x, by = spot.y;
    const right = pinned ? lbLeft : bx + w / 2 < m.x;   // the stack sits left of the mark, so its pills line up on their right ends
    // A halo of the map's ground under each pill closes the gaps between them, so no label under the stack shows through.
    const at = k => ({ pw: ws[k], px: right ? bx + w - ws[k] : bx, py: by + k * (h + gap) });
    ctx.fillStyle = paper;
    lines.forEach((t, k) => { const { pw, px, py } = at(k), e = gap / 2 + 1; ctx.beginPath(); ctx.roundRect(px - e, py - e, pw + 2 * e, h + 2 * e, h / 2 + e); ctx.fill(); });
    lines.forEach((t, k) => {
      const { pw, px, py } = at(k);
      const first = k === 0 && named, act = k === lines.length - 1 && (lines.length > 1 || pinned);
      const fill = first ? (m.col || '#fff') : act ? ink : paper, text = first ? '#000' : act ? paper : ink;
      pill(ctx, px, py, pw, h, fill, first ? '#000' : ink);
      ctx.fillStyle = text; ctx.fillText(t, px + PILL_PAD, py + h / 2 + 0.5);
    });
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
  const keysOf = e => { const ks = [e.key, ...(e.also || [])]; HQ.orgs.forEach(o => { if (o !== e && o.n === e.n && o.co === e.co) ks.push(o.key); }); return ks; };
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
      turnOn(k);
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
      const inBox = b => mx >= b.x && mx <= b.x + b.w && my >= b.y && my <= b.y + b.h;
      if (m.box) { if (!inBox(m.box)) return; d = 0; }
      else {
        d = Math.hypot(m.x - mx, m.y - my);
        // The name drawn beside a mark is part of it: pointing at the name is pointing at the mark.
        if (d > m.r * (touch ? 1.6 : 1)) { if ((m.lbox && inBox(m.lbox)) || (m.lboxes && m.lboxes.some(inBox))) d = m.r; else return; }
      }
      if (m.pass) d += 100;   // a mark on a space's own dot gives way to one that stands alone
      if (d < bd) { bd = d; best = m; }
    });
    return best;
  }
  window.atlasLayerMarks = {
    // The marks drawn last frame (position, name, count line), for checking the layers from a test script.
    marks: () => LM.map(m => ({ x: m.x, y: m.y, r: m.r, label: m.label, sub: m.sub, go: !!m.go })),
    // The line hover and the funder whose web is lit, for checking from a test script.
    lineHover: () => (LM_HOV && LM_HOV.line ? { key: LM_HOV.key, label: LM_HOV.label, sub: LM_HOV.sub, sub2: LM_HOV.sub2, tip: LM_HOV.tip } : null),
    reach: () => (REACH ? { key: REACH.key, keys: REACH.keys, name: REACH.name, pinned: !!REACH.pinned } : null),
    // The widest-reaching funders switched on as filters in the Layers panel.
    filters: () => [...FILTERS].map(t => ({ name: t.name, keys: t.keys, n: t.n })),
    lines: () => LINES.length,
    // Pointer moved: a mark that stands alone takes the hover (true, so the page shows a pointer); a mark on a space's dot does not.
    hover(mx, my, dots) {
      const m = markAt(mx, my), alone = m && !m.pass ? m : null;
      // No mark under the pointer: a funding line may be. Its funder's whole web lights up, and a block names the funder.
      const tag = !m ? lineAt(mx, my, dots) : null, f = tag && !tag.agg && funderOf(tag.key);
      // A bundle, a flow or a flagged tie stands for many funders or one tie: its block says what it carries, and a click asks the chat.
      if (tag && tag.agg) {
        if (!(LM_HOV && LM_HOV.aggId === tag.id)) { LM_HOV = { line: true, agg: true, aggId: tag.id, x: mx, y: my, col: tag.col, label: tag.label, sub: tag.sub, sub2: tag.sub2, tip: 'Click to ask the chat' }; repaint(); }
        return true;
      }
      if (f) {
        const same = LM_HOV && LM_HOV.line && LM_HOV.key === f.key;
        if (!same) {
          const n = reachOfKeys(f.keys), st = tag.a && tag.b ? `${tag.a.n} – ${tag.b.n}` : null;
          LM_HOV = { line: true, key: f.key, x: mx, y: my, col: COL[f.kind], label: f.name, sub: `${KIND_WORD[f.kind] || 'Funder'} · funds ${plural(n.n, 'space')} in ${n.countries} ${n.countries === 1 ? 'country' : 'countries'}`, sub2: st, tip: REACH && REACH.pinned && REACH.key === f.key ? 'Pinned · click to open its record' : 'Click for details' };
        } else { LM_HOV.x = mx; LM_HOV.y = my; }
        if (!(REACH && (REACH.pinned || REACH.tapped)) && (!REACH || REACH.key !== f.key)) { clearTimeout(reachTimer); reachTimer = 0; REACH = { key: f.key, keys: f.keys, kind: f.kind, space: f.office || tag.a || f.space, name: f.name, top: f.top, line: true }; }
        else { clearTimeout(reachTimer); reachTimer = 0; }
        repaint();
        return true;
      }
      if ((alone && alone.ask) !== (LM_HOV && LM_HOV.ask) || (alone && alone.rec) !== (LM_HOV && LM_HOV.rec) || (LM_HOV && LM_HOV.line)) { LM_HOV = alone; repaint(); }
      setReach(alone);
      return !!alone;
    },
    // A click on a mark asks the chat about it, and that is all the click does. The chat answers a question about a space
    // with the space selected on the map and stays in front, so a flag mark loses nothing by not opening the record.
    click(mx, my, dots) {
      const m = markAt(mx, my);
      if (!m) {
        // A finger on a space or a city is a tap on it, not on a funding line running through it: every funded space has
        // lines ending at its dot, and the line used to take the tap and open the funder instead. Touch only: a mouse's
        // hover names the line before the click.
        if ((window.__lastPointerType === 'touch' || window.__lastPointerType === 'pen') && typeof window.resolveGlobeTarget === 'function' && window.resolveGlobeTarget(mx, my)) {
          if (REACH && REACH.tapped) clearReach(); return false;
        }
        // A click on a funding line pins its funder's web on the map and opens the funder's record in the Details tab.
        const tag = lineAt(mx, my, dots), f = tag && !tag.agg && funderOf(tag.key);
        if (tag && tag.agg) { askChat(tag.ask); return true; }
        if (f) {
          clearTimeout(reachTimer); reachTimer = 0;
          REACH = { key: f.key, keys: f.keys, kind: f.kind, space: f.office || tag.a || f.space, name: f.name, top: f.top, pinned: true, line: true };
          if (typeof renderTop === 'function') renderTop();
          if (LM_HOV && LM_HOV.line) LM_HOV.tip = 'Pinned · click to open its record';
          const e = f.office || { key: f.key, kind: 'org', k: f.kind, n: f.name, c: '', co: '', noOffice: true, spaces: reachOfKeys(f.keys).n };
          if (typeof window.atlasHqOpen === 'function') window.atlasHqOpen(e);
          repaint();
          return true;
        }
        if (REACH && REACH.tapped) clearReach(); return false;
      }
      if (m.go) { m.go(); return true; }
      // A finger has no hover: the first tap on a funder around a space shows where else it appears (and its tooltip), a second asks the chat.
      if ((window.__lastPointerType === 'touch' || window.__lastPointerType === 'pen') && m.key && !m.rec && !(REACH && REACH.tapped && REACH.key === m.key && REACH.space === m.space)) {
        clearTimeout(reachTimer);
        REACH = { key: m.key, keys: [m.key], kind: m.kind, space: m.space, name: m.name, tapped: true };
        reachTimer = setTimeout(clearReach, 8000); LM_HOV = m; repaint();
        return true;
      }
      askChat(m.ask);
      return true;
    }
  };

  // "Money map" on a record: turn the layers on and show that space's funders on the globe.
  window.atlasShowMoney = function (id) {
    turnOn('money'); turnOn('ties'); loadMoney();
    if (typeof window.exitCityStreetView === 'function') { try { window.exitCityStreetView(); } catch (e) {} }
    const inst = id && typeof window.resolveInstitutionByIdOrName === 'function' ? window.resolveInstitutionByIdOrName(id) : null;
    if (id && typeof window.selectInstitution === 'function') window.selectInstitution(id, false);
    // On a phone the record sheet would cover the funders; it steps aside, and a tap on the space brings it back.
    if (window.innerWidth < 768) { const sheet = document.getElementById('dossier-bottom-sheet'); if (sheet) sheet.classList.add('hidden'); if (typeof window.setActiveMobileTab === 'function') window.setActiveMobileTab('atlas'); }
    // Close in on the space, so its funders sit around it in its own city rather than across the continent.
    // A space with no coordinates (stored as 0, 0) closes in on its city instead; flying to 0, 0 showed an empty ocean.
    const pin = inst && typeof window.atlasPinOf === 'function' ? window.atlasPinOf(inst) : null;
    if (pin && typeof window.flyTo === 'function' && typeof window.getMaxRadius === 'function') {
      const z = window.getMaxRadius();
      if (typeof window.setTargetRadius === 'function') window.setTargetRadius(z);
      window.flyTo(pin.lon, pin.lat, z);
    }
    repaint();
  };

  // What assets/funding-views.js draws with.
  window.atlasLayersAPI = {
    L, COL, lineCol, hexA, kindOn, FUNDER, RIGHT, collides, repaint, loadMoney, loadHq,
    // The layer boxes and the keys each one holds, for the record's Money map toggle (assets/phone-maps.js).
    boxes: () => boxes(), keysOfBox: (inp) => keysOfBox(inp),
    data: () => ({ recById, keyIndex, keyKind, HQ, web }),
    top: () => TOP,
    reach: () => REACH,
    pushRun: run => LINES.push(run),
    pushMark: m => LM.push(m),
    funderName: key => { const f = funderOf(key); return f ? f.name : null; }
  };

  // What each layer holds, as a count after its name.
  function updateCounts() {
    const set = (k, text) => { const el = document.querySelector(`#layersPanel [data-count="${k}"]`); if (el) el.textContent = text; };
    const formatCount = count => new Intl.NumberFormat('en-US').format(count);
    if (typeof ALL_INSTITUTIONS !== 'undefined') {
      set('flags', `${formatCount(ALL_INSTITUTIONS.filter(i => i.flags && i.flags.length).length)}`);
      set('propaganda', `${formatCount(ALL_INSTITUTIONS.filter(i => (i.propaganda || []).length).length)}\u00a0spaces`);
      set('independent', `${formatCount(ALL_INSTITUTIONS.filter(i => selfKinds(i).independent).length)}\u00a0spaces`);
      set('artist', `${formatCount(ALL_INSTITUTIONS.filter(i => selfKinds(i).artist).length)}\u00a0spaces`);
      set('openbooks', `${formatCount(ALL_INSTITUTIONS.filter(isOpenBooks).length)}\u00a0spaces`);
    }
    if (HQ) {
      set('hq', `${formatCount(HQ.orgs.length)}\u00a0offices`);
      set('people', `${formatCount(HQ.people.length)}\u00a0offices`);
    }
    if (recById && HQ) buildTop();
    if (web) {
      set('ties', `${formatCount(web.length)}\u00a0links`);
      const funded = [...recById.values()].filter(rec => rec.nodes.some(FUNDER)).length;
      set('money', `${formatCount(funded)}\u00a0spaces`);
      set('funding', `${formatCount(funded)}\u00a0spaces`);
      const rightRecs = [...recById.values()].filter(rec => rec.nodes.some(RIGHT));
      set('right', `${formatCount(rightRecs.length)}\u00a0spaces`);
      set('epstein', `${formatCount([...recById.values()].filter(rec => epsteinOf(rec).length).length)}\u00a0spaces`);
      if (window.atlasFundingViews) window.atlasFundingViews.counts(set);
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
    if (!(REACH || L.flags || L.money || L.right || L.epstein || L.hq || L.people || L.propaganda || L.ties || L.independent || L.artist || L.openbooks || fvOn())) { SV.dots = []; LM = []; return; }
    const base = 240, r = base * Math.pow(2, map.getZoom() - 7);
    // Points behind the camera on a tilted map project to nonsense; anything far off the canvas is treated as not in front.
    const project = (lon, lat) => { const p = map.project([lon, lat]); return { x: p.x, y: p.y, front: Math.abs(p.x - W / 2) < 6 * W && Math.abs(p.y - H / 2) < 6 * H, depth: 1 }; };
    const dots = [], list = [], pad = 40, keep = window.atlasLayerKeep();
    ALL_INSTITUTIONS.forEach(i => {
      if (typeof i.lat !== 'number' || typeof i.lon !== 'number') return;
      if (keep && !keep(i)) return;
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
      window.atlasLayersDrawTip(ctx);
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
  // Pointing at a funder in the list previews its web; its switch turns it on as a filter, and several can be on at once.
  function previewTop(t) {
    if (REACH && (REACH.pinned || REACH.tapped)) return;
    clearTimeout(reachTimer); reachTimer = 0;
    REACH = { key: t.keys[0], keys: t.keys, kind: t.kind, space: hubOf(t), name: t.name, top: t };
    repaint();
  }
  function toggleTop(t) {
    const on = !FILTERS.has(t);
    if (on) FILTERS.add(t); else FILTERS.delete(t);
    if (on && FILTERS.size === 1 && typeof window.flyTo === 'function') {
      const home = hubOf(t);
      if (home && typeof home.lat === 'number') window.flyTo(home.lon, home.lat, (window.getBaseRadius ? window.getBaseRadius() : 276) * 1.6);
    }
    renderTop(); refilter();
  }
  // The rows are built again only when the list changes (a funder type switched off); a switch changing only updates its row,
  // so the row under the pointer or with focus stays where it is.
  let topShown = [];
  function renderTop() {
    const box = document.getElementById('topFunders'); if (!box || !TOP) return;
    const list = TOP.filter(t => kindOn(t.kind)).slice(0, 10);
    if (list.length !== topShown.length || list.some((t, i) => t !== topShown[i]) || box.children.length !== list.length) {
      topShown = list;
      box.textContent = '';
      list.forEach(t => {
        const b = document.createElement('button'); b.type = 'button'; b.className = 'top-funder filter-row';
        b.style.setProperty('--marker-color', COL[t.kind]);
        b.setAttribute('role', 'switch');
        b.innerHTML = `<i class="shape-${KIND_SHAPE[t.kind]}" style="--marker-color:${COL[t.kind]}"></i><span class="tf-name"></span><span class="tf-n"></span><span class="filter-switch" aria-hidden="true"></span>`;
        b.querySelector('.tf-name').textContent = t.name;
        b.querySelector('.tf-n').textContent = plural(t.n, 'space');
        b.addEventListener('mouseenter', () => previewTop(t));
        b.addEventListener('focus', () => previewTop(t));
        const leave = () => { if (REACH && !REACH.pinned && REACH.top === t) clearReach(); };
        b.addEventListener('mouseleave', leave);
        b.addEventListener('blur', leave);
        b.addEventListener('click', () => toggleTop(t));
        box.appendChild(b);
      });
    }
    [...box.children].forEach((b, i) => {
      const t = list[i], on = FILTERS.has(t);
      b.setAttribute('aria-checked', String(on));
      b.title = `${t.name}: named on ${t.n} spaces. ${on ? 'Switch off to hide' : 'Switch on to keep'} its connections on the map.`;
    });
  }

  // ---- Boxes in the panel ----
  // A box turns on the layers its data-layers attribute names (or the one its data-layer names). Turning a layer on from
  // elsewhere (a record's "Money map", an office being named) turns on the whole box it sits in, so what the map shows and
  // what the panel says agree.
  const boxes = () => [...document.querySelectorAll('#layersPanel input[data-layer]')];
  const keysOfBox = inp => (inp.dataset.layers || inp.dataset.layer).split(/\s+/).filter(Boolean);
  function setBox(inp, on) {
    inp.checked = on;
    keysOfBox(inp).forEach(k => { L[k] = on; });
    if (!on) return;
    const ks = keysOfBox(inp);
    if (ks.some(k => k !== 'flags' && k !== 'propaganda' && k !== 'independent' && k !== 'artist' && k !== 'openbooks')) loadMoney();
    if (ks.some(k => k === 'hq' || k === 'people' || k === 'flows' || k === 'choro' || k === 'lifted' || k === 'flagged' || k === 'hulls')) loadHq();
  }
  function turnOn(k) {
    const inp = boxes().find(i => keysOfBox(i).includes(k));
    if (!inp) { L[k] = true; return; }
    // A filter box (funding, epstein) becomes the one filter on, so the others go off with it.
    if (SPACE_TEST[inp.dataset.layer]) { window.atlasSetSpaceFilter(inp.dataset.layer); return; }
    const was = inp.checked; setBox(inp, true); if (!was) refilter();
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
      box.querySelectorAll('input[data-layer]').forEach(input => setBox(input, false));
      box.querySelectorAll('input[data-kind]').forEach(input => { input.checked = true; L.kinds[input.dataset.kind] = true; });
      box.querySelectorAll('input[data-pkind]').forEach(input => { input.checked = true; L.pkinds[input.dataset.pkind] = true; });
      const yOn = box.querySelector('input[data-years-on]'); if (yOn) { yOn.checked = false; L.years = null; }
      const cDef = box.querySelector('input[data-choro="abroad"]'); if (cDef) { cDef.checked = true; L.choroMode = 'abroad'; }
      FILTERS.clear(); GRADE = null; syncKey(); renderTop();
      clearReach();
      refilter();
    });
    document.addEventListener('click', e => { if (!panel.hidden && !box.contains(e.target)) setOpen(false); });
    document.addEventListener('keydown', e => { if (e.key === 'Escape') { clearReach(); if (!panel.hidden) setOpen(false); } });
    window.addEventListener('resize', () => { if (!panel.hidden) placePanel(); });
    box.querySelectorAll('input[data-layer]').forEach(inp => inp.addEventListener('change', () => {
      // The six filters are one at a time: ticking one unticks the others; unticking the one on shows every space.
      if (SPACE_TEST[inp.dataset.layer]) { applySpaceFilter(inp.checked ? inp.dataset.layer : null); return; }
      setBox(inp, inp.checked);
      refilter();
    }));
    box.querySelectorAll('input[data-kind]').forEach(inp => inp.addEventListener('change', () => {
      L.kinds[inp.dataset.kind] = inp.checked;
      renderTop();
      repaint();
    }));
    box.querySelectorAll('input[data-pkind]').forEach(inp => inp.addEventListener('change', () => {
      L.pkinds[inp.dataset.pkind] = inp.checked;
      repaint();
    }));
    // Countries shaded: by the share of funding from abroad, or by the main funder type.
    box.querySelectorAll('input[data-choro]').forEach(inp => inp.addEventListener('change', () => {
      if (!inp.checked) return;
      L.choroMode = inp.dataset.choro;
      const legend = box.querySelector('[data-choro-legend]'); if (legend) legend.hidden = L.choroMode !== 'abroad';
      repaint();
    }));
    // Years: a decade, over the years the funding lines name.
    const yOn = box.querySelector('input[data-years-on]'), ySl = box.querySelector('input[data-years]'), yOut = box.querySelector('[data-years-out]');
    if (yOn && ySl) {
      const setYears = () => {
        const y0 = Number(ySl.value);
        if (yOut) yOut.textContent = `${y0}s`;
        ySl.setAttribute('aria-valuetext', `${y0}s`);
        L.years = yOn.checked ? [y0, y0 + 9] : null;
        if (yOn.checked) loadMoney();
        updateCounts(); repaint();
      };
      yOn.addEventListener('change', setYears);
      ySl.addEventListener('input', () => { if (!yOn.checked) yOn.checked = true; setYears(); });
    }
    updateCounts();
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
