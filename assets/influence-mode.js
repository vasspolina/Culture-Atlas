// Influence mode: the atlas seen from the sender's side (user, 17 Nov 2026: "switch the perspective a little from the receivers
// to the senders ... and see what kind of influence they're buying"; "build it as layer on top of the app for now like a gossip mode").
//
// It reads assets/influence.json, written by tools/build_influence.py from the reviewed entries in data/influence_review.json:
// for each pilot funder, every tie where a record says what came with the money (a name, a seat, a programme, access, a
// building, silence, a tax break, licence to operate), or that the tie ended or met protest. Nothing here is inferred: each
// entry is a sentence of the record, summarised by the editor, with the record's sources for it.
//
// Switched on, it does four things and nothing else:
//   - the map shows the funders at their head offices instead of the spaces (user, 17 Nov 2026: "Influence mode needs to
//     switch the map from culture spaces to cultural funders"); a picked funder shows its spaces, joined to its office
//     (window.atlasModeKeep, read by assets/layers.js; atlasInfluenceDraw and atlasInfluencePointer, called by index.html)
//   - the chat says what the mode is and lists the funders with what each got, each one a button
//   - a space's record leads with "What funders got here"
//   - a funder's record (assets/hq-detail.js) leads with its ledger: what it got, kind by kind, space by space
//
// The sender is the subject (user, 17 Nov 2026: "If the money doesn't go to culture it doesn't disappear so who is at
// fault?"). A space that says no ends one tie, not the money: so a funder's ledger also says where its money comes from and
// what else it pays for beside culture (hand-sourced facts, data/influence_senders.json, each with its own source), and,
// when a space ended a tie, which ties the records still date after that and do not say ended. On the map an ended tie is a
// dashed line and a running one solid, so a picked funder shows at a glance where it was refused and where it went on paying.
// Switched off, all four go and the page is as it was. Its look is the "INFLUENCE MODE" block at the end of assets/sheet.css.
(function () {
  let DATA = null, loading = null, on = false;
  const BY_SPACE = new Map(), BY_FUNDER = new Map();

  function load() {
    if (DATA) return Promise.resolve(DATA);
    if (loading) return loading;
    loading = fetch('assets/influence.json?v=4', { cache: 'no-cache' }).then(r => r.json()).then(d => {
      DATA = d;
      d.funders.forEach(f => {
        BY_FUNDER.set(f.key, f);
        f.ties.forEach(t => {
          if (!BY_SPACE.has(t.space)) BY_SPACE.set(t.space, []);
          BY_SPACE.get(t.space).push({ funder: f, tie: t });
        });
      });
      return d;
    }).catch(() => { loading = null; return null; });
    return loading;
  }

  const esc = s => String(s == null ? '' : s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const host = u => { try { return new URL(u).hostname.replace(/^www\./, ''); } catch (_) { return ''; } };
  const label = k => { const x = DATA && DATA.kinds.find(q => q.key === k); return x ? x.label : k; };
  const plural = (n, one, many) => `${n} ${n === 1 ? one : (many || one + 's')}`;
  // What each kind means, said once in the chat and in the ledger's head, so a reader knows what "Seat" or "Silence" counts.
  const MEANS = {
    name: 'its name on a prize, a room, a building or a programme',
    seat: 'a place on the board, or its people on it',
    programme: 'a show, a festival, research or education it paid for',
    access: 'galas, corporate memberships, events and hospitality',
    building: 'a building, a refurbishment or an endowment',
    silence: 'terms kept from the public, or work withdrawn',
    tax: 'a gift routed through a tax incentive',
    licence: 'culture tied to its own operations or reputation',
    money: 'money is stated, and nothing about what came with it'
  };
  // The order a ledger lists kinds: what was bought first, money alone last.
  const ORDER = ['name', 'seat', 'programme', 'building', 'access', 'silence', 'licence', 'tax', 'money'];

  function tally(ties) {
    const n = {};
    ties.forEach(t => (t.kinds.length ? t.kinds : []).forEach(k => { n[k] = (n[k] || 0) + 1; }));
    const ended = ties.filter(t => t.ended).length, protest = ties.filter(t => t.protest).length;
    const spaces = new Set(ties.map(t => t.space)).size;
    return { n, ended, protest, spaces };
  }
  function tallyLine(f) {
    const t = tally(f.ties);
    const parts = ORDER.filter(k => t.n[k]).map(k => `${label(k).toLowerCase()} ${t.n[k]}`);
    const tail = [t.ended ? `ended ${t.ended}` : '', t.protest ? `met protest ${t.protest}` : ''].filter(Boolean);
    return `${plural(t.spaces, 'space')}: ${parts.join(', ')}${tail.length ? '; ' + tail.join(', ') : ''}`;
  }

  // A tie's year, from a date like "2023-12" or "2019"; a date the record could not give is null.
  const yearOf = t => { const m = String(t.date || '').match(/\b(1[89]|20)\d\d\b/); return m ? +m[0] : null; };
  // The year a tie ended. An entry is sometimes dated at the gift (the Guggenheim's Sackler centre, 1995; Hay, 2017) with
  // the end in its summary ("the name was removed in 2022", "suspended in May 2024"), so it is the latest year either names.
  const endYearOf = t => { const ys = (String(t.summary || '') + ' ' + String(t.date || '')).match(/\b(1[89]|20)\d\d\b/g); return ys ? Math.max(...ys.map(Number)) : null; };
  // When a space said no: the ties that ended, and the ties the records date in or after the first refusal and do not say
  // ended, at spaces that did not end it later. Nothing is claimed about the same money moving; only what the records date.
  function afterNo(f) {
    const ended = f.ties.filter(t => t.ended);
    const ys = ended.map(endYearOf).filter(y => y != null);
    if (!ended.length || !ys.length) return { ended, first: null, kept: [] };
    const first = Math.min(...ys);
    const endedAt = new Map();
    ended.forEach(t => { const y = endYearOf(t); if (y != null) endedAt.set(t.space, Math.max(endedAt.get(t.space) || 0, y)); });
    const kept = f.ties.filter(t => !t.ended && yearOf(t) != null && yearOf(t) >= first && !(endedAt.get(t.space) >= yearOf(t)))
      .sort((a, b) => yearOf(a) - yearOf(b));
    return { ended: ended.slice().sort((a, b) => (endYearOf(a) || 0) - (endYearOf(b) || 0)), first, kept };
  }
  const shortAfter = f => {
    const a = afterNo(f); if (!a.ended.length) return '';
    const left = new Set(a.ended.map(t => t.space)).size, kept = new Set(a.kept.map(t => t.space)).size;
    // A clause the records have nothing for is left out (user, 17 Nov 2026: "only add section if there is an info"): no
    // "none dated … or later in the records", just the spaces that ended it.
    return `${plural(left, 'space')} ended it${a.first && kept ? `, ${plural(kept, 'space')} still dated ${a.first} or later` : ''}`;
  };

  // ---- The map: the funders, not the spaces ----
  // No space is drawn while the mode is on, except the spaces of the funder picked, which come back joined to its office.
  let picked = null;   // the funder whose spaces are on the map
  const spacesOf = f => new Set(f.ties.map(t => t.space));
  let pickedSpaces = null;
  // A space opened some other way (the search, the chat, a record) stays on the map too, so its pin has somewhere to be.
  window.atlasModeKeep = () => (on && DATA ? (i => !!(i && ((pickedSpaces && pickedSpaces.has(i.id)) || i === g('selectedInstitution')))) : null);
  function pick(f) {
    picked = f; pickedSpaces = f ? spacesOf(f) : null;
    if (typeof window.atlasRefilter === 'function') window.atlasRefilter();
    else if (window.scheduleRender) window.scheduleRender();
  }
  const isDark = () => document.documentElement.getAttribute('data-theme') === 'dark';
  // Funders in one city fan out around it, as the offices of assets/layers.js do, so London's two never sit on each other.
  let fan = null;
  function fanOut() {
    fan = new Map();
    const byCity = new Map();
    DATA.funders.filter(f => f.hq).forEach(f => { const k = f.hq.lat.toFixed(1) + ',' + f.hq.lon.toFixed(1); if (!byCity.has(k)) byCity.set(k, []); byCity.get(k).push(f); });
    byCity.forEach(list => list.forEach((f, i) => { const a = -Math.PI / 2 + i * 2.39996, rr = i === 0 ? 0 : 18 + 6 * Math.sqrt(i); fan.set(f, { dx: Math.cos(a) * rr, dy: Math.sin(a) * rr }); }));
  }
  // A great-circle path from the office to a space, cut where it goes behind the globe.
  function arc(ctx, project, r, cx, cy, a, b) {
    const rad = Math.PI / 180, v = (lon, lat) => [Math.cos(lat * rad) * Math.cos(lon * rad), Math.cos(lat * rad) * Math.sin(lon * rad), Math.sin(lat * rad)];
    const p = v(a.lon, a.lat), q = v(b.lon, b.lat);
    const w = Math.acos(Math.max(-1, Math.min(1, p[0] * q[0] + p[1] * q[1] + p[2] * q[2])));
    const n = Math.max(2, Math.ceil(w / (2 * rad)));
    let down = false;
    ctx.beginPath();
    for (let i = 0; i <= n; i++) {
      const t = i / n, s1 = w ? Math.sin((1 - t) * w) / Math.sin(w) : 1 - t, s2 = w ? Math.sin(t * w) / Math.sin(w) : t;
      const x = s1 * p[0] + s2 * q[0], y = s1 * p[1] + s2 * q[1], z = s1 * p[2] + s2 * q[2];
      const pt = project(Math.atan2(y, x) / rad, Math.atan2(z, Math.hypot(x, y)) / rad, r, cx, cy);
      if (!pt.front) { down = false; continue; }
      if (down) ctx.lineTo(pt.x, pt.y); else { ctx.moveTo(pt.x, pt.y); down = true; }
    }
    ctx.stroke();
  }
  // A company is a hexagon and a family or foundation a triangle, as on the money map (README, "A mark is never told only by colour").
  function mark(ctx, f, x, y, s) {
    ctx.beginPath();
    if (f.kind === 'corp') for (let i = 0; i < 6; i++) { const a = Math.PI / 6 + i * Math.PI / 3; ctx[i ? 'lineTo' : 'moveTo'](x + s * Math.cos(a), y + s * Math.sin(a)); }
    else { ctx.moveTo(x, y - s * 1.15); ctx.lineTo(x + s, y + s * 0.75); ctx.lineTo(x - s, y + s * 0.75); }
    ctx.closePath();
  }
  let HITS = [], hover = null;
  const FONT = '400 15px "Atlas Serif", "Times New Roman", Times, "EB Garamond", serif';
  window.atlasInfluenceDraw = function (ctx, project, r, cx, cy, ground, text) {
    HITS = [];
    if (!on || !DATA) return;
    if (!fan) fanOut();
    const ink = text || (isDark() ? '#e6e1d7' : '#000000'), paper = ground || (isDark() ? '#151412' : '#ffffff');
    const insts = g('ALL_INSTITUTIONS') || [];
    ctx.save();
    // The picked funder's ties: a line from its office to each space it got something from.
    if (picked && picked.hq) {
      const byId = new Map(insts.map(i => [i.id, i]));
      // A space that ended the tie is a dashed line, a running one solid: shape, not colour, says which. A space with ties
      // of both kinds takes the solid line, since some tie there is not said to have ended.
      const running = new Set(picked.ties.filter(t => !t.ended).map(t => t.space));
      ctx.strokeStyle = ink; ctx.lineWidth = 1;
      new Set(picked.ties.map(t => t.space)).forEach(id => {
        const i = byId.get(id); if (!i || typeof i.lat !== 'number') return;
        ctx.setLineDash(running.has(id) ? [] : [4, 4]);
        arc(ctx, project, r, cx, cy, picked.hq, i);
      });
      ctx.setLineDash([]);
    }
    // Marks first, then names, the funders that reach most spaces first, so their names get the best place.
    const marks = [];
    DATA.funders.forEach(f => {
      if (!f.hq) return;
      const pt = project(f.hq.lon, f.hq.lat, r, cx, cy); if (!pt.front) return;
      const o = fan.get(f) || { dx: 0, dy: 0 }, x = pt.x + o.dx, y = pt.y + o.dy;
      const n = new Set(f.ties.map(t => t.space)).size;
      marks.push({ f, x, y, s: 5 + 2 * Math.sqrt(n), n });
    });
    const placed = marks.map(m => ({ x: m.x - m.s - 2, y: m.y - m.s - 2, w: 2 * m.s + 4, h: 2 * m.s + 4 }));
    marks.forEach(m => {
      const sel = picked === m.f, hov = hover === m.f;
      mark(ctx, m.f, m.x, m.y, m.s);
      ctx.fillStyle = sel || hov ? ink : paper; ctx.fill();
      ctx.strokeStyle = ink; ctx.lineWidth = sel ? 2 : 1.5; ctx.stroke();
    });
    ctx.font = FONT; ctx.textBaseline = 'middle'; ctx.lineJoin = 'round';
    marks.slice().sort((a, b) => b.n - a.n).forEach(m => {
      const { f, x, y, s } = m, sel = picked === f, hov = hover === f;
      // The name beside the mark in plain type on a halo of the map's ground, never cut short, moved round the mark
      // until it covers no other name or mark. Where every place is taken (Europe at world zoom) it waits, as a city's
      // name does, and shows once the map is zoomed in or the mark is pointed at; the picked funder's always shows.
      const label = f.name, w = ctx.measureText(label).width, gap = s + 5;
      const spots = [[gap, 0], [-gap - w, 0], [-w / 2, gap + 8], [-w / 2, -gap - 8], [gap, 15], [gap, -15], [-gap - w, 15], [-gap - w, -15], [gap, 30], [-gap - w, 30], [gap, -30], [-gap - w, -30]];
      const boxAt = ([dx, dy]) => ({ x: x + dx - 2, y: y + dy - 9, w: w + 4, h: 18 });
      const clash = b => placed.some(q => b.x < q.x + q.w && q.x < b.x + b.w && b.y < q.y + q.h && q.y < b.y + b.h);
      const free = spots.find(sp => !clash(boxAt(sp)));
      if (!free && !sel && !hov) { HITS.push({ f, x, y, s, label: null }); return; }
      const spot = free || spots[0], b = boxAt(spot), lx = x + spot[0], ly = y + spot[1];
      placed.push(b);
      ctx.lineWidth = 4; ctx.strokeStyle = paper; ctx.strokeText(label, lx, ly);
      ctx.fillStyle = hov && !sel ? (isDark() ? '#8bbdf5' : '#1f5fbf') : ink; ctx.fillText(label, lx, ly);
      HITS.push({ f, x, y, s, label: b });
    });
    ctx.restore();
  };
  const hitAt = (mx, my) => {
    let best = null, bd = Infinity;
    HITS.forEach(h => {
      const d = Math.hypot(h.x - mx, h.y - my), inLabel = !!h.label && mx >= h.label.x && mx <= h.label.x + h.label.w && my >= h.label.y && my <= h.label.y + h.label.h;
      const dd = inLabel ? 0 : d;
      if ((inLabel || d <= h.s + 6) && dd < bd) { bd = dd; best = h.f; }
    });
    return best;
  };
  // The marks drawn last frame, for checking the layer from a test script.
  window.atlasInfluenceMarks = () => HITS.map(h => ({ key: h.f.key, name: h.f.name, x: h.x, y: h.y, s: h.s, label: h.label || null }));
  window.atlasInfluencePointer = {
    hover(mx, my) {
      if (!on) return false;
      const f = hitAt(mx, my);
      if (f !== hover) { hover = f; if (window.scheduleRender) window.scheduleRender(); }
      return !!f;
    },
    // A funder opens its ledger and its spaces come onto the map; picking it again puts it away.
    click(mx, my) {
      if (!on) return false;
      const f = hitAt(mx, my); if (!f) return false;
      if (picked === f) { pick(null); if (typeof window.atlasHqClose === 'function') window.atlasHqClose(); return true; }
      openFunder(f.key);
      return true;
    }
  };

  // ---- The toggle ----
  const BTN_IDS = ['topInfluenceBtn', 'mobileInfluenceBtn', 'gmInfluenceBtn'];
  function paintButtons() { BTN_IDS.forEach(id => { const b = document.getElementById(id); if (b) b.setAttribute('aria-pressed', String(on)); }); }
  async function toggle(force) {
    on = typeof force === 'boolean' ? force : !on;
    document.body.classList.toggle('influence-mode-active', on);
    paintButtons();
    if (on) {
      if (window.atlasCount) window.atlasCount('influence/on');
      await load();
      if (!on) return;   // switched off again while the data loaded
      if (window.atlasHq && window.atlasHq.ready) window.atlasHq.ready(() => {});   // the funding maps, so a funder's record can open
      greet();
    } else {
      picked = null; pickedSpaces = null; hover = null;
      say('<p class="no-indent">Influence mode is off. The map shows the spaces again.</p>');
    }
    if (typeof window.atlasRefilter === 'function') window.atlasRefilter();
    decorate();
  }
  window.toggleInfluenceMode = toggle;
  window.isInfluenceModeActive = () => on;

  // ---- The chat ----
  function say(html) {
    if (typeof appendCuratorMessage === 'function') appendCuratorMessage(html, [], null, null, false);
  }
  function greet() {
    if (!DATA) { say('<p class="no-indent">Influence mode is on, but its entries could not be loaded. Try again in a moment.</p>'); return; }
    const total = DATA.funders.reduce((s, f) => s + f.ties.length, 0);
    const rows = DATA.funders.map(f => { const a = shortAfter(f); return `<li><button type="button" class="influence-funder-link" data-influence-funder="${esc(f.key)}">${esc(f.name)}</button> ${esc(tallyLine(f))}${a ? `<br><span class="influence-meta">${esc(a)}</span>` : ''}</li>`; }).join('');
    const kinds = ORDER.map(k => `<li><span class="lead-in">${esc(label(k))}</span> ${esc(MEANS[k])}</li>`).join('');
    say(`<div class="influence-chat">
<p class="no-indent">Influence mode is on. It turns the atlas round, from the spaces that take the money to the funders that give it, and asks what the money bought. The map now shows the funders at their head offices instead of the spaces: a hexagon for a company, a triangle for a family or foundation, larger the more spaces it reaches. Pick one to open what it got and bring its spaces onto the map, joined to its office.</p>
<p>A space that turns the money down ends one tie, not the money. So each funder’s record also says what its money is made from, what else it pays for beside culture, and, where a space ended a tie, which ties the records still date after that. On the map a picked funder’s ended ties are dashed lines and its running ones solid.</p>
<p>These are ${total} entries on ${DATA.funders.length} funders, a first batch read by hand: oil and gas, tobacco, mining, the Sacklers, and the family and finance money the records flag. Bloomberg and the banks are not read yet, and public funders are left out on purpose: the question is what private money buys.</p>
<ul class="influence-funders">${rows}</ul>
<p>What each word counts:</p>
<ul class="influence-kinds">${kinds}</ul>
<p>Each entry is a sentence of a space’s record, checked against that record, not yet against the source page it cites.</p>
</div>`);
  }
  // A funder named in the chat or in a ledger opens its record, which then leads with what it got.
  document.addEventListener('click', ev => {
    const b = ev.target.closest && ev.target.closest('[data-influence-funder]');
    if (b) { ev.preventDefault(); openFunder(b.getAttribute('data-influence-funder')); return; }
    const s = ev.target.closest && ev.target.closest('[data-influence-space]');
    if (s) { ev.preventDefault(); if (typeof window.selectInstitution === 'function') window.selectInstitution(s.getAttribute('data-influence-space'), false); }
  });
  function openFunder(key) {
    const f = BY_FUNDER.get(key); if (!f) return;
    const go = () => {
      const hq = window.atlasHq;
      let e = (hq && hq.funderRecord && hq.funderRecord(key)) || { key, kind: 'org', k: f.kind === 'corp' ? 'corp' : 'found', n: f.name, c: '', co: '', noOffice: true };
      // The mode places every pilot funder at an office (assets/influence.json, hq), so its record names that office too.
      if (e.noOffice && f.hq) e = Object.assign({}, e, { c: f.hq.c, co: f.hq.co, a: f.hq.a, lat: f.hq.lat, lon: f.hq.lon, noOffice: false });
      // Its own office layer stays off: the mode draws the funders itself (assets/hq-detail.js reads noLayer).
      if (typeof window.atlasHqOpen === 'function') window.atlasHqOpen(Object.assign({}, e, { noLayer: true }));
      openFor = f;
      pick(f);
      decorate();
    };
    if (window.atlasHq && window.atlasHq.ready && !window.atlasHq.loaded()) window.atlasHq.ready(go); else go();
  }
  let openFor = null;   // the funder whose record the ledger was asked for, so the ledger finds it even under another spelling

  // ---- The records ----
  const lineFor = (t, withSpace, withFunder) => {
    const src = (t.sources || [])[0];
    const marks = [t.ended ? 'Ended' : '', t.protest ? 'Met protest' : ''].filter(Boolean).join(', ');
    const kinds = t.kinds.length ? t.kinds.map(label).join(', ') : '';
    const who = withFunder ? `<button type="button" class="influence-funder-link" data-influence-funder="${esc(withFunder.key)}">${esc(withFunder.name)}</button>` : '';
    const where = withSpace ? `<button type="button" class="influence-space-link" data-influence-space="${esc(t.space)}">${esc(t.space_name)}</button>${t.city ? `<span class="influence-meta">, ${esc(t.city)}</span>` : ''}` : '';
    return `<li class="influence-entry">
<p class="no-indent">${who || where ? `<span class="influence-who">${who || where}</span> ` : ''}${kinds ? `<span class="lead-in">${esc(kinds)}.</span> ` : ''}${esc(t.summary)}</p>
<p class="no-indent influence-meta">${[t.date ? esc(String(t.date).slice(0, 10)) : '', marks ? `<span class="influence-mark">${esc(marks)}</span>` : '', src ? `<a href="${esc(src)}" target="_blank" rel="noopener noreferrer">${esc(host(src))}</a>` : ''].filter(Boolean).join(' · ')}</p>
</li>`;
  };
  const row = (title, sub, inner) => `<section class="d-row" role="group"><div class="d-row-head"><h3 class="d-row-title">${esc(title)}</h3>${sub ? `<p class="d-row-sub no-indent">${esc(sub)}</p>` : ''}</div>${inner}</section>`;

  function spacePart(inst) {
    const list = inst && BY_SPACE.get(inst.id);
    if (!list || !list.length) return null;
    const byF = new Map();
    list.forEach(({ funder, tie }) => { if (!byF.has(funder)) byF.set(funder, []); byF.get(funder).push(tie); });
    // What was bought first, newest first; a protest or resignation with nothing bought stated comes after.
    byF.forEach(ties => ties.sort((a, b) => (!a.kinds.length - !b.kinds.length) || String(b.date || '0').localeCompare(String(a.date || '0'))));
    const el = document.createElement('div');
    el.className = 'prose-part d-rows influence-part';
    el.setAttribute('role', 'region');
    el.setAttribute('aria-label', 'What funders got here');
    el.innerHTML = row('What funders got here', '', '') +
      [...byF.entries()].map(([f, ties]) => row(f.name, '', `<ul class="d-row-list influence-list">${ties.map(t => lineFor(t, false, null)).join('')}</ul><p class="no-indent influence-more"><button type="button" class="influence-funder-link" data-influence-funder="${esc(f.key)}">Everything ${esc(f.name)} got</button></p>`)).join('');
    return el;
  }

  // The sender's side, from data/influence_senders.json: what the money is made from, what else it pays for, and what the
  // sources say happened to the money after a space said no. Each fact carries its own source, read on its page.
  const FACT_ROWS = [
    ['harm', 'Where the money comes from', null],
    ['scale', 'Beside culture: the business', 'the size of what makes the money, one stated year'],
    ['lobbying', 'Beside culture: lobbying', 'what it spends on lobbying governments'],
    ['politics', 'Beside culture: politics', 'political donations and campaigns']
  ];
  const factLine = x => `<li class="influence-entry"><p class="no-indent">${esc(x.text)}</p><p class="no-indent influence-meta">${[x.date ? esc(x.date) : '', x.source ? `<a href="${esc(x.source)}" target="_blank" rel="noopener noreferrer">${esc(host(x.source))}</a>` : ''].filter(Boolean).join(' · ')}</p></li>`;
  function senderRows(f) {
    const s = f.sender; if (!s) return '';
    const facts = s.facts || [];
    return FACT_ROWS.map(([k, title, sub]) => {
      const list = facts.filter(x => x.kind === k);
      const lead = k === 'harm' && s.made_from ? `<p class="no-indent">${esc(s.made_from)}</p>` : '';
      if (!list.length && !lead) return '';
      return row(title, sub || '', `${lead}${list.length ? `<ul class="d-row-list influence-list">${list.map(factLine).join('')}</ul>` : ''}`);
    }).join('');
  }
  // The section is drawn only when the records hold something on what came after a refusal: a tie dated after it, or what a
  // source says happened next (user, 17 Nov 2026: "do not publish sections that lack the info, only add section if there is
  // an info"). A refusal alone is not enough: the ended ties are already in the ledger, marked Ended, and a section that could
  // only say the records do not say where the money went (Chevron) is not drawn.
  function afterRows(f) {
    const a = afterNo(f), told = ((f.sender && f.sender.facts) || []).filter(x => x.kind === 'after');
    if (!a.kept.length && !told.length) return '';
    let inner = '';
    if (a.ended.length) inner += `<p class="no-indent"><span class="lead-in">Ended it.</span></p><ul class="d-row-list influence-list">${a.ended.map(x => lineFor(x, true, null)).join('')}</ul>`;
    if (a.kept.length) inner += `<p class="no-indent"><span class="lead-in">Dated ${esc(a.first)} or later, and not said to have ended.</span></p><ul class="d-row-list influence-list">${a.kept.map(x => lineFor(x, true, null)).join('')}</ul>`;
    if (told.length) inner += `<p class="no-indent"><span class="lead-in">What the sources say happened next.</span></p><ul class="d-row-list influence-list">${told.map(factLine).join('')}</ul>`;
    return row('When a space said no', 'a refusal ends one tie, not the money', inner);
  }

  function funderPart(f) {
    const t = tally(f.ties);
    const el = document.createElement('div');
    el.className = 'prose-part d-rows influence-part';
    el.setAttribute('role', 'region');
    el.setAttribute('aria-label', `What ${f.name} got`);
    let html = row(`What ${f.name} got`, tallyLine(f), '');
    html += senderRows(f);
    ORDER.forEach(k => {
      const ties = f.ties.filter(x => (x.kinds.length ? x.kinds : []).includes(k));
      if (ties.length) html += row(label(k), MEANS[k], `<ul class="d-row-list influence-list">${ties.map(x => lineFor(x, true, null)).join('')}</ul>`);
    });
    html += afterRows(f);
    const pushback = f.ties.filter(x => !x.kinds.length);
    if (pushback.length) html += row('Pushback', 'protests and resignations with nothing bought stated', `<ul class="d-row-list influence-list">${pushback.map(x => lineFor(x, true, null)).join('')}</ul>`);
    if (t.ended || t.protest) html += `<p class="no-indent influence-meta">${esc([t.ended ? plural(t.ended, 'tie') + ' ended' : '', t.protest ? plural(t.protest, 'entry', 'entries') + ' met protest' : ''].filter(Boolean).join('; '))}. Each entry is checked against the space’s record, not yet against its source.</p>`;
    el.innerHTML = html;
    return el;
  }

  const g = n => { try { return (0, eval)(n); } catch (_) { return undefined; } };
  const norm = s => String(s || '').toLowerCase().replace(/[^a-z0-9]+/g, '');
  function funderForPanel(panel) {
    const h = panel.querySelector('#hqPanelTitle'); if (!h) return null;
    const name = norm(h.textContent);
    if (openFor && (norm(openFor.name) === name || name.includes(norm(openFor.name).slice(0, 6)))) return openFor;
    // Opened another way (a mark on the map, a funding line): match the record's name to a ledger funder.
    return DATA.funders.find(f => norm(f.name) === name || norm(f.name.split(/[ /]/)[0]) === name || name.startsWith(norm(f.name.split(/[ /]/)[0]))) || null;
  }

  let busy = false;
  function decorate() {
    if (busy) return;
    busy = true;
    try {
      document.querySelectorAll('.influence-part').forEach(el => { if (!on) el.remove(); });
      if (!on || !DATA) return;
      // A funder's record in the Details tab.
      const panel = document.getElementById('hqPanel');
      if (panel && !panel.hidden && !panel.querySelector('.influence-part')) {
        const f = funderForPanel(panel), head = panel.querySelector('.record-head');
        if (f && head) head.after(funderPart(f));
      }
      // A space's record: the desktop Details page, the phone's record page and its sheet.
      const inst = g('dossierInst') || g('selectedInstitution');
      ['desktopDossierRecordBody', 'detailBody'].forEach(id => {
        const box = document.getElementById(id);
        if (!box || !box.firstElementChild || box.querySelector('.influence-part')) return;
        const part = spacePart(inst); if (!part) return;
        const head = box.querySelector('.record-head');
        if (head && head.parentElement) head.after(part); else box.prepend(part);
      });
      const pane = document.getElementById('dossier-sheet-verified-pane');
      if (pane && !pane.querySelector('.influence-part')) {
        const part = spacePart(g('selectedInstitution'));
        const summary = document.getElementById('dossier-sheet-summary');
        if (part) { if (summary) summary.after(part); else pane.prepend(part); }
      }
    } finally { busy = false; }
  }
  // The records are rebuilt whenever a space or funder is opened; the ledger goes back in after each rebuild.
  let queued = false;
  const later = () => { if (queued) return; queued = true; requestAnimationFrame(() => { queued = false; decorate(); }); };
  function watch() {
    ['desktopDossierRecordBody', 'detailBody', 'dossier-sheet-verified-pane', 'dossier-sheet-scrollable-body', 'desktopDossierBody'].forEach(id => {
      const el = document.getElementById(id);
      if (el && !el.dataset.influenceWatched) { el.dataset.influenceWatched = '1'; new MutationObserver(() => { if (on) later(); }).observe(el, { childList: true, subtree: true }); }
    });
  }

  // ---- The phone's row of top buttons (assets/phone-maps.js builds it): Influence mode sits after Gossip mode ----
  function phoneButton() {
    const gossip = document.getElementById('gmGossipBtn');
    if (!gossip || document.getElementById('gmInfluenceBtn')) return !!gossip;
    const b = document.createElement('button');
    b.type = 'button'; b.id = 'gmInfluenceBtn'; b.textContent = 'Influence mode';
    b.setAttribute('aria-pressed', String(on));
    b.addEventListener('click', () => toggle());
    gossip.after(b);
    const bar = gossip.parentElement;
    if (bar && bar.getAttribute('aria-label')) bar.setAttribute('aria-label', 'Chat, dark mode, gossip mode and influence mode');
    return true;
  }

  function init() {
    watch();
    let n = 0;
    const t = setInterval(() => { watch(); if (phoneButton() || ++n > 50) clearInterval(t); }, 200);
    // Load the entries early, so the first switch is instant and ?influence opens the page in the mode.
    load().then(() => { if (/[?&]influence\b/.test(location.search)) toggle(true); });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
