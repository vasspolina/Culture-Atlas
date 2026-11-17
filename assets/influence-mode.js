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
//   - the chat says in two lines what the mode is
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
  let DATA = null, STUDY = null, loading = null, on = false;
  const BY_SPACE = new Map(), BY_FUNDER = new Map();

  function load() {
    if (DATA) return Promise.resolve(DATA);
    if (loading) return loading;
    loading = fetch('assets/influence.json?v=15', { cache: 'no-cache' }).then(r => r.json()).then(d => {
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
    // The MoMA Influence Map study's entries, text only (assets/moma-influence.json, tools/build_moma_influence.mjs). Read
    // beside the ledger; if it fails to load, MoMA's record simply goes without it.
    fetch('assets/moma-influence.json?v=1', { cache: 'no-cache' }).then(r => r.json()).then(d => { STUDY = d; }).catch(() => {});
    return loading;
  }

  const esc = s => String(s == null ? '' : s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const host = u => { try { return new URL(u).hostname.replace(/^www\./, ''); } catch (_) { return ''; } };
  // Plain names for the kinds (user, 17 Nov 2026: "delete all the jargon"): "Seat", "Silence" and "Licence to operate" were
  // the editor's shorthand, not words a reader uses. assets/influence.json keeps its own labels; these win.
  const PLAIN = { name: 'Its name on something', seat: 'A board seat', programme: 'Shows and programmes', building: 'Buildings',
    access: 'Parties and perks', silence: 'Secrecy', licence: 'A better image', tax: 'Tax breaks', money: 'Money only' };
  const label = k => { if (PLAIN[k]) return PLAIN[k]; const x = DATA && DATA.kinds.find(q => q.key === k); return x ? x.label : k; };
  const plural = (n, one, many) => `${n} ${n === 1 ? one : (many || one + 's')}`;
  // What each kind means, said once in the chat and in the ledger's head, so a reader knows what "Seat" or "Silence" counts.
  const MEANS = {
    name: 'its name on a prize, a room, a building or a programme',
    seat: 'a place on the board, or its people on it',
    programme: 'a show, a festival, research or education it paid for',
    access: 'galas, corporate memberships, events and hospitality',
    building: 'a building, a refurbishment or an endowment',
    silence: 'terms kept from the public, or work withdrawn',
    tax: 'a gift that cut its tax bill',
    licence: 'culture used to make its business look better',
    money: 'money, with nothing said about what came back'
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
  // The ledger has no line under its title (user, 17 Nov 2026, of "15 ties with 14 spaces. At 7 it got something back: ...":
  // "do not add this explanation"). The rows below say what it got, kind by kind.

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

  // ---- The money map's funders join the ledger's ----
  // The funding maps (assets/money-maps.json and the offices of assets/hq.json, through window.atlasHq) name far more private
  // funders than the ledger reads by hand. Each one with a head office joins the map as a dot, its spaces those the records
  // name it on; a ledger funder gains the spaces the funding maps name it on beyond its ledger. A funder from the maps alone
  // (moneyOnly) has no ledger: its record is its office's, which lists the spaces it funds. Public bodies stay out, as they
  // do in the ledger: the question is what private money buys.
  let merged = false;
  function mergeMoney() {
    const hq = window.atlasHq;
    if (merged || !DATA || !hq || !hq.loaded || !hq.loaded() || !hq.moneyFunders) return;
    merged = true;
    const own = new Set(DATA.funders.map(f => f.key)), offices = new Set();
    DATA.funders.forEach(f => {
      const ledger = new Set(f.ties.map(t => t.space));
      f.moneySpaces = hq.spacesOfKey(f.key).filter(q => !ledger.has(q.id));
      const r = hq.funderRecord && hq.funderRecord(f.key); if (r && !r.noOffice) offices.add(r.key);
    });
    hq.moneyFunders().forEach(m => {
      if (offices.has(m.key) || m.keys.some(k => own.has(k))) return;
      const f = { key: m.key, name: m.name, kind: m.k === 'corp' ? 'corp' : m.k === 'priv' ? 'fund' : 'found', hq: m.hq, ties: [], moneySpaces: m.spaces, moneyOnly: true };
      DATA.funders.push(f); BY_FUNDER.set(f.key, f);
    });
    DATA.funders.forEach(f => { delete f._ms; });
    fan = null;
    if (window.scheduleRender) window.scheduleRender();
  }

  // ---- The map: the funders, not the spaces ----
  // No space is drawn while the mode is on, except the spaces of the funder picked, which come back joined to its office.
  let picked = null;   // the funder whose spaces are on the map
  // Every space a funder reaches on the map, from its ledger and, under Culture, from the funding maps (user, 17 Nov 2026:
  // "Influence mode is now money map. Combine the research"): id -> { name, open }. A space every ledger tie of which ended
  // is not open, so its line is dashed. Kept per funder and measure; mergeMoney clears it.
  function mapSpaces(f, m = MEASURE) {
    const c = f._ms || (f._ms = {}); if (c[m]) return c[m];
    const out = new Map();
    tiesFor(f, m).forEach(t => { const x = out.get(t.space) || { name: t.space_name, open: false }; if (!t.ended) x.open = true; out.set(t.space, x); });
    if (m === 'culture') (f.moneySpaces || []).forEach(q => { if (!out.has(q.id)) out.set(q.id, { name: q.name, open: true }); });
    return (c[m] = out);
  }
  const spacesOf = f => new Set(mapSpaces(f, 'culture').keys());
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
    const pts = [];
    for (let i = 0; i <= n; i++) {
      const t = i / n, s1 = w ? Math.sin((1 - t) * w) / Math.sin(w) : 1 - t, s2 = w ? Math.sin(t * w) / Math.sin(w) : t;
      const x = s1 * p[0] + s2 * q[0], y = s1 * p[1] + s2 * q[1], z = s1 * p[2] + s2 * q[2];
      pts.push(project(Math.atan2(y, x) / rad, Math.atan2(z, Math.hypot(x, y)) / rad, r, cx, cy));
    }
    // On the flat (Winkel) map every point is "front", so a path that runs off one edge comes back in at the other: the
    // pen lifts there, as the coastlines do (index.html), or the two ends are joined by a straight line across the map.
    const flat = pts[0].lam != null;
    const seamAt = i => flat && Math.abs(pts[i].lam - pts[i - 1].lam) > Math.PI;
    ctx.beginPath();
    // On the flat map a route that wanders far out of its way, as Munich to Tokyo does over the top of the map, where the
    // pole is a line (user, 17 Nov 2026: "Shorten the Tokyo line so it doesn't run along the top edge"), is drawn as a
    // gentle bow between its two ends instead, bent the way the true route goes. "Far out of its way" is a path more than a
    // tenth longer than the straight line between its ends; the bow is at most 15% of that line. A route that crosses the
    // edge is bowed only when every crossing comes back in nearer than its two ends are to each other, as one over the pole
    // line does; a route that leaves at one side of the map and comes back at the other (Munich to Auckland) keeps its
    // two pieces, since a straight bow would invent a way across the map that the route does not take.
    if (flat) {
      const A = pts[0], B = pts[pts.length - 1], chord = Math.hypot(B.x - A.x, B.y - A.y);
      let len = 0, wide = false;
      for (let i = 1; i < pts.length; i++) {
        const d = Math.hypot(pts[i].x - pts[i - 1].x, pts[i].y - pts[i - 1].y);
        if (seamAt(i)) { if (d >= chord) wide = true; } else len += d;
      }
      if (!wide && chord > 0 && len > 1.1 * chord) {
        const mx = (A.x + B.x) / 2, my = (A.y + B.y) / 2, M = pts[Math.floor(pts.length / 2)];
        const nx = -(B.y - A.y) / chord, ny = (B.x - A.x) / chord;   // the chord's normal
        const side = Math.sign((M.x - mx) * nx + (M.y - my) * ny) || 1;
        const k = 0.3 * chord * side;   // a quadratic's middle sits halfway to its control point: a bow of 15%
        ctx.moveTo(A.x, A.y);
        ctx.quadraticCurveTo(mx + nx * k, my + ny * k, B.x, B.y);
        ctx.stroke();
        return;
      }
    }
    let down = false;
    pts.forEach((pt, i) => {
      if (!pt.front) { down = false; return; }
      if (down && !seamAt(i)) ctx.lineTo(pt.x, pt.y); else { ctx.moveTo(pt.x, pt.y); down = true; }
    });
    ctx.stroke();
  }
  // Every funder is a dot (user, 17 Nov 2026: "just do dots dont do different figure"); its size says how many spaces it
  // reaches. Company or family is said in its record and in the chat, not by the shape.
  // Every dot is 6px across whatever the measure (user, 17 Nov 2026: "these dots are way too big, make all dots same size
  // and like 4px", then "make the dots a bit bigger"); the measure is said by the figure in the label, not by the size.
  const DOT = 3;
  function mark(ctx, f, x, y) {
    ctx.beginPath();
    ctx.arc(x, y, DOT, 0, Math.PI * 2);
    ctx.closePath();
  }
  // ---- The measures: cultural giving next to lobbying and political giving ----
  // (user, 17 Nov 2026: "Set cultural giving next to their public lobbying, political donation and sponsorship filings
  // (filters on influence map) ... This is the part that actually answers 'who is at fault?'"). One measure at a time
  // sizes the dots and labels each with its figure. Every figure is in data/influence_senders.json under `figures`, with
  // its own source: culture from the atlas entries, US lobbying from the Lobbying Disclosure Act reports (lda.gov), EU
  // lobbying from the EU Transparency Register, political giving from corporate PAC reports to the Federal Election
  // Commission. A funder with no figure for the measure is a small hollow dot, its name only on pointing: no filing found
  // is not the same as nothing spent, so it is never drawn as zero.
  const fmtMoney = (v, cur) => {
    const sym = { USD: '$', EUR: '€', GBP: '£', CAD: 'C$', BRL: 'R$', QAR: 'QAR ', INR: 'Rs ' }[cur] || '$';
    if (v >= 1e9) return `${sym}${(v / 1e9).toFixed(v >= 1e10 ? 0 : 1).replace(/\.0$/, '')}bn`;
    if (v >= 1e6) return `${sym}${(v / 1e6).toFixed(v >= 1e7 ? 0 : 1).replace(/\.0$/, '')}M`;
    if (v >= 1e3) return `${sym}${Math.round(v / 1e3)}k`;
    return `${sym}${Math.round(v)}`;
  };
  const fig = f => (f.sender && f.sender.figures) || {};
  const cultureSpaces = f => Math.max((fig(f).culture || {}).spaces || 0, mapSpaces(f, 'culture').size);
  const MEASURES = {
    // A funder with no hand-sourced figures yet (the private fortunes added 17 Nov 2026) counts the spaces its kept entries
    // name, which is how the sourced figure is counted too; culture is never a missing filing, so never a hollow dot.
    culture: { label: 'Culture', what: 'how many museums it gives to',
      value: f => cultureSpaces(f) || null,
      text: f => { const n = cultureSpaces(f); return n ? `${n} ${n === 1 ? 'museum' : 'museums'}` : ''; } },
    us: { label: 'US lobbying', noun: 'US lobbying', what: 'what it spent lobbying the US government in 2025',
      value: f => (fig(f).us_lobbying || {}).usd || null,
      text: f => { const u = fig(f).us_lobbying; return u ? fmtMoney(u.usd, 'USD') : ''; } },
    eu: { label: 'EU lobbying', noun: 'EU lobbying', what: 'what it says it spent lobbying the EU in its last full year',
      value: f => { const e = fig(f).eu_lobbying; return e ? (e.eur_min + e.eur_max) / 2 : null; },
      text: f => { const e = fig(f).eu_lobbying; return e ? (e.eur_min ? `${fmtMoney(e.eur_min, 'EUR')}–${fmtMoney(e.eur_max + 1, 'EUR')}` : `under ${fmtMoney(e.eur_max + 1, 'EUR')}`) : ''; } },
    // Political giving adds two kinds of filing, told apart in the label: what the company's political fund (its PAC) gave US
    // candidates, and what the people behind a family or individual funder gave in personal contributions (FEC individual
    // contributions, 2023 and 2024, to candidates, parties and political groups, super PACs included). A company's
    // executives are not counted as the company.
    politics: { label: 'Political giving', noun: 'political giving', what: 'what its company political fund gave US candidates in 2023 and 2024, and what the people behind it gave personally',
      value: f => (((fig(f).political || {}).usd || 0) + ((fig(f).personal || {}).usd || 0)) || null,
      text: f => {
        const p = fig(f).political, q = fig(f).personal, parts = [];
        if (q) parts.push(`${fmtMoney(q.usd, 'USD')} personal`);
        if (p) parts.push(`${fmtMoney(p.usd, 'USD')} company fund${p.rep_usd != null ? `, ${Math.round(100 * p.rep_usd / p.usd)}% Republican` : ''}`);
        return parts.join('; ');
      } },
    // Lobbying of a government outside the US and the EU (Mexico, Russia ...), recorded only where it went through a space:
    // there is no register to total, so the label names the governments instead of a sum.
    other: { label: 'Other lobbying', noun: 'lobbying of another government', what: 'which governments it lobbied through a museum',
      value: () => null,
      text: f => { const g = [...new Set(tiesFor(f, 'other').flatMap(t => (t.links || []).filter(l => l.measure === 'other').map(l => l.gov)).filter(Boolean))]; return g.length ? `lobbying ${g.length > 1 ? g.slice(0, -1).join(', ') + ' and ' + g[g.length - 1] : g[0]}` : ''; } },
  };
  let MEASURE = 'culture';
  // A money measure shows only where a record ties it to a space (user, 17 Nov 2026: "the lobbying need to appear only if it
  // was shown at that particular cultural space not that the company does lobbying in general, same for other filters").
  // A company's lobbying or political giving in general says nothing about a museum; a tie's `links` (from
  // data/influence_review.json, each { measure: 'us' | 'eu' | 'politics', text, source }) is a record that it reached that
  // space: a filing that names the museum, a lobbying event held there, a candidate's fundraiser in its hall. Culture is
  // giving at a space by definition, so every tie counts for it. A funder with no linked tie is not drawn under the measure,
  // and a picked funder's lines go only to the linked spaces.
  const tiesFor = (f, m = MEASURE) => m === 'culture' ? f.ties : f.ties.filter(t => (t.links || []).some(l => l.measure === m));
  const shown = f => mapSpaces(f).size > 0;
  function setMeasure(m) {
    if (!MEASURES[m] || (m === MEASURE && m !== 'culture')) m = 'culture';
    MEASURE = m;
    paintMeasureButtons();
    if (window.scheduleRender) window.scheduleRender();
    if (on && DATA) sayMeasure();
  }
  function sayMeasure() {
    const M = MEASURES[MEASURE];
    const ranked = DATA.funders.filter(f => shown(f) && (M.value(f) || MEASURE !== 'culture')).sort((a, b) => (M.value(b) || 0) - (M.value(a) || 0));
    if (MEASURE !== 'culture') {
      // Each funder is listed with the museums its money for this measure is recorded at, and under it what each record
      // says happened there, with its source.
      const items = ranked.map(f => {
        const fig = M.text(f), links = tiesFor(f).flatMap(t => (t.links || []).filter(l => l.measure === MEASURE).map(l => ({ t, l })));
        const sub = links.map(({ t, l }) => `<li><a href="#" class="influence-space-link" data-influence-space="${esc(t.space)}">${esc(t.space_name)}</a>: ${esc(l.text)}${l.source ? ` <a class="influence-meta" href="${esc(l.source)}" target="_blank" rel="noopener noreferrer">${esc(host(l.source))}</a>` : ''}</li>`).join('');
        return `<li><a href="#" class="influence-funder-link" data-influence-funder="${esc(f.key)}">${esc(f.name)}</a>${fig ? ` ${esc(fig)}` : ''}<ul class="influence-funders">${sub}</ul></li>`;
      }).join('');
      say(`<div class="influence-chat"><p class="no-indent">${esc(M.label)}: a company is shown only where a record ties its ${esc(M.noun)} to a museum in the atlas.</p>${items ? `<ul class="influence-funders">${items}</ul>` : `<p class="no-indent">No record does yet, so no company is shown. What each one spends in general is in its own record.</p>`}</div>`);
      return;
    }
    const none = DATA.funders.filter(f => !M.value(f)).map(f => f.name);
    const top = ranked.slice(0, 6).map(f => `<li><a href="#" class="influence-funder-link" data-influence-funder="${esc(f.key)}">${esc(f.name)}</a> ${esc(M.text(f))}</li>`).join('');
    say(`<div class="influence-chat"><p class="no-indent">${esc(M.label)}: each dot is labelled with ${esc(M.what)}.</p><ul class="influence-funders">${top}</ul>${none.length ? `<p class="no-indent influence-meta">Nothing found for ${esc(none.join(', '))}, which does not mean they spent nothing.</p>` : ''}</div>`);
  }
  // The buttons sit in the map's filter row (#gmdChips on a desktop, #gmChips on a phone) and take its place while the mode is
  // on: the space filters have nothing to filter when the map shows funders. assets/layers.js rebuilds that row, so the
  // buttons are put back whenever they go.
  function measureButtons() {
    [['gmdChips', 'gmd-chip'], ['gmChips', 'gm-filter-chip']].forEach(([id, cls]) => {
      const host = document.getElementById(id); if (!host || host.querySelector('[data-influence-measure]')) return;
      Object.entries(MEASURES).forEach(([k, M]) => {
        const b = document.createElement('button');
        b.type = 'button'; b.className = cls; b.dataset.influenceMeasure = k; b.textContent = M.label;
        b.title = k === 'culture' ? `Label each funder with ${M.what}` : `Show only where a record ties ${M.noun} to a museum`;
        b.addEventListener('click', () => setMeasure(k));
        host.appendChild(b);
      });
      paintMeasureButtons();
    });
  }
  function paintMeasureButtons() { document.querySelectorAll('[data-influence-measure]').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.influenceMeasure === MEASURE))); }
  window.atlasInfluenceMeasure = () => MEASURE;
  window.atlasSetInfluenceMeasure = setMeasure;

  let HITS = [], SPACE_HITS = [], hover = null, hoverSpace = null, FOCUS = null;
  const FONT = '400 15px "Atlas Serif", "Times New Roman", Times, "EB Garamond", serif';
  window.atlasInfluenceDraw = function (ctx, project, r, cx, cy, ground, text) {
    HITS = []; SPACE_HITS = [];
    if (!on || !DATA) return;
    if (!fan) fanOut();
    const ink = text || (isDark() ? '#e6e1d7' : '#000000'), paper = ground || (isDark() ? '#151412' : '#ffffff');
    const dpr = ctx.getTransform ? (ctx.getTransform().a || 1) : 1, W = ctx.canvas.width / dpr, H = ctx.canvas.height / dpr;
    const insts = g('ALL_INSTITUTIONS') || [];
    ctx.save();
    // The picked funder's ties: a line from its office to each space it got something from.
    if (picked && picked.hq) {
      const byId = new Map(insts.map(i => [i.id, i]));
      // A space that ended the tie is a dashed line, a running one solid: shape, not colour, says which. A space with ties
      // of both kinds takes the solid line, since some tie there is not said to have ended.
      ctx.strokeStyle = ink; ctx.lineWidth = 1;
      mapSpaces(picked).forEach((x, id) => {
        const i = byId.get(id); if (!i || typeof i.lat !== 'number') return;
        ctx.setLineDash(x.open ? [] : [4, 4]);
        arc(ctx, project, r, cx, cy, picked.hq, i);
      });
      ctx.setLineDash([]);
    }
    // A space opened in the mode (its record's Money map button, the search, the chat) is joined to each funder's office, as
    // the old money map set a space's funders round it; those funders' names are placed first.
    const sel = !picked && g('selectedInstitution');
    FOCUS = sel && typeof sel.lat === 'number' ? new Set(DATA.funders.filter(f => f.hq && spacesOf(f).has(sel.id))) : null;
    if (FOCUS) {
      ctx.strokeStyle = ink; ctx.lineWidth = 1; ctx.setLineDash([]);
      FOCUS.forEach(f => arc(ctx, project, r, cx, cy, f.hq, sel));
    }
    // Marks first, then names, the funders that reach most spaces first, so their names get the best place.
    const marks = [];
    const M = MEASURES[MEASURE];
    DATA.funders.forEach(f => {
      if (!f.hq) return;
      // Not tied to any space under this measure: not drawn, unless it is the funder picked (opened from the chat), which
      // keeps its dot but not the figure.
      const linked = shown(f);
      if (!linked && picked !== f) return;
      const pt = project(f.hq.lon, f.hq.lat, r, cx, cy); if (!pt.front) return;
      const o = fan.get(f) || { dx: 0, dy: 0 }, x = pt.x + o.dx, y = pt.y + o.dy;
      const v = linked ? M.value(f) : null;
      // Culture keeps its old scale, capped so Bloomberg's 80 spaces do not cover New York; a money measure is scaled to the
      // largest figure on the map, by area. No figure: a small hollow dot.
      const s = DOT;
      // A funder tied to a space under a money measure is labelled even with no figure (lobbying of other governments has
      // no filing to total): the tie is what the filter shows.
      marks.push({ f, x, y, s, n: v || 0, none: !v && !(linked && MEASURE !== 'culture') });
    });
    const placed = marks.map(m => ({ x: m.x - m.s - 2, y: m.y - m.s - 2, w: 2 * m.s + 4, h: 2 * m.s + 4 }));
    marks.forEach(m => {
      const sel = picked === m.f, hov = hover === m.f;
      mark(ctx, m.f, m.x, m.y, m.s);
      // Solid ink; a funder with no figure for the measure is hollow, the picked one gets a ring.
      ctx.fillStyle = m.none && !sel && !hov ? paper : ink; ctx.fill();
      ctx.strokeStyle = ink; ctx.lineWidth = 1; ctx.stroke();
      if (sel) { ctx.beginPath(); ctx.arc(m.x, m.y, DOT + 3, 0, Math.PI * 2); ctx.stroke(); }
    });
    ctx.font = FONT; ctx.textBaseline = 'middle'; ctx.lineJoin = 'round';
    const hits = (b, list) => list.some(q => b.x < q.x + q.w && q.x < b.x + b.w && b.y < q.y + q.h && q.y < b.y + b.h);
    // A place that runs off the map's edge counts as taken, so a long label turns inward.
    const off = b => b.x < 2 || b.y < 2 || b.x + b.w > W - 2 || b.y + b.h > H - 2;
    // The names set so far, kept apart from the dots: a museum's name may lie over another funder's dot (the halo keeps
    // it readable), never over another name (user, 17 Nov 2026: the picked funder's name, its museums' names and the
    // names round them were drawn over each other in Europe).
    const names = [];
    // The picked funder's name always shows, beside its own dot: it may lie over other funders' dots (the halo keeps it
    // readable), and it is placed before any other name, so nothing else can be under it.
    const spotFor = (spots, boxAt) => spots.find(sp => !off(boxAt(sp))) || spots[0];
    // The picked funder's name first: it is what was clicked, so it gets the best place and its museums' names go round it.
    const pickedMark = picked && marks.find(m => m.f === picked);
    let pickedDone = null;
    if (pickedMark) {
      const { f, x, y, s } = pickedMark;
      const figure = shown(f) ? MEASURES[MEASURE].text(f) : '';
      const label = figure ? `${f.name}  ${figure}` : f.name, w = ctx.measureText(label).width, gap = s + 5;
      const spots = [[gap, 0], [-gap - w, 0], [-w / 2, gap + 8], [-w / 2, -gap - 8], [gap, 15], [gap, -15], [-gap - w, 15], [-gap - w, -15], [gap, 30], [-gap - w, 30], [gap, -30], [-gap - w, -30]];
      const boxAt = ([dx, dy]) => ({ x: x + dx - 2, y: y + dy - 9, w: w + 4, h: 18 });
      const spot = spotFor(spots, boxAt), b = boxAt(spot);
      names.push(b);
      pickedDone = { label, lx: x + spot[0], ly: y + spot[1], b };
    }
    // The picked funder's spaces are named on the map (user, 17 Nov 2026: "show names of the museums when i click on dots
    // in influence mode"). They are placed before the other funders' names, so those give way to them; a space whose
    // every place is taken by another name waits for the map to be zoomed in, as a funder's name does.
    const museumDots = [];
    if (picked) {
      const byId = new Map(insts.map(i => [i.id, i]));
      const spaceNames = new Map([...mapSpaces(picked)].map(([id, x]) => [id, x.name]));
      const pts = [];
      spaceNames.forEach((nm, id) => {
        const i = byId.get(id); if (!i || typeof i.lat !== 'number') return;
        const pt = project(i.lon, i.lat, r, cx, cy); if (!pt.front) return;
        pts.push({ id, x: pt.x, y: pt.y, label: i.name || nm || '' });
        museumDots.push({ id, x: pt.x, y: pt.y });
      });
      // A space's own dot is kept clear by every name, its own and the others'.
      const spaceDots = pts.map(q => ({ x: q.x - 5, y: q.y - 5, w: 10, h: 10 }));
      if (pickedMark) spaceDots.push({ x: pickedMark.x - DOT - 5, y: pickedMark.y - DOT - 5, w: 2 * DOT + 10, h: 2 * DOT + 10 });
      pts.forEach(({ id, x, y, label }) => {
        if (!label) return;
        const w = ctx.measureText(label).width, gap = 9;
        const spots = [[gap, 0], [-gap - w, 0], [-w / 2, gap + 6], [-w / 2, -gap - 6], [gap, 15], [gap, -15], [-gap - w, 15], [-gap - w, -15], [gap, 30], [-gap - w, 30], [gap, -30], [-gap - w, -30]];
        const boxAt = ([dx, dy]) => ({ x: x + dx - 2, y: y + dy - 9, w: w + 4, h: 18 });
        const spot = spots.find(sp => { const b = boxAt(sp); return !off(b) && !hits(b, names) && !hits(b, spaceDots); }); if (!spot) return;
        const box = boxAt(spot); names.push(box);
        // The name is a link, as it is in the chat: pointed at it turns the link colour, clicked it opens the space.
        SPACE_HITS.push({ id, box });
        ctx.lineWidth = 4; ctx.strokeStyle = paper; ctx.strokeText(label, x + spot[0], y + spot[1]);
        ctx.fillStyle = hoverSpace === id ? (isDark() ? '#8bbdf5' : '#1f5fbf') : ink; ctx.fillText(label, x + spot[0], y + spot[1]);
      });
      spaceDots.forEach(b => placed.push(b));
    }
    if (pickedDone) {
      const { label, lx, ly, b } = pickedDone;
      ctx.lineWidth = 4; ctx.strokeStyle = paper; ctx.strokeText(label, lx, ly);
      ctx.fillStyle = ink; ctx.fillText(label, lx, ly);
      HITS.push({ f: picked, x: pickedMark.x, y: pickedMark.y, s: pickedMark.s, label: b });
    }
    const first = f => picked === f ? 2 : FOCUS && FOCUS.has(f) ? 1 : 0;
    let tried = 0;
    marks.slice().sort((a, b) => first(b.f) - first(a.f) || b.n - a.n).forEach(m => {
      const { f, x, y, s } = m, sel = picked === f || (FOCUS && FOCUS.has(f)), hov = hover === f;
      if (pickedDone && f === picked) return;
      // The name beside the mark in plain type on a halo of the map's ground, never cut short, moved round the mark
      // until it covers no other name or mark. Where every place is taken (Europe at world zoom) it waits, as a city's
      // name does, and shows once the map is zoomed in or the mark is pointed at; the picked funder's always shows.
      const figure = shown(f) ? MEASURES[MEASURE].text(f) : '';
      if (m.none && !sel && !hov) { HITS.push({ f, x, y, s, label: null }); return; }
      // The funding maps add some 600 funders; only the widest-reaching of them try for a name, so placing names stays quick.
      // The rest show theirs when pointed at, picked, or tied to the space in focus.
      if (f.moneyOnly && !sel && !hov && ++tried > 60) { HITS.push({ f, x, y, s, label: null }); return; }
      const label = figure ? `${f.name}  ${figure}` : f.name, w = ctx.measureText(label).width, gap = s + 5;
      const spots = [[gap, 0], [-gap - w, 0], [-w / 2, gap + 8], [-w / 2, -gap - 8], [gap, 15], [gap, -15], [-gap - w, 15], [-gap - w, -15], [gap, 30], [-gap - w, 30], [gap, -30], [-gap - w, -30]];
      const boxAt = ([dx, dy]) => ({ x: x + dx - 2, y: y + dy - 9, w: w + 4, h: 18 });
      const clash = b => off(b) || hits(b, placed) || hits(b, names);
      const free = spots.find(sp => !clash(boxAt(sp)));
      if (!free && !sel && !hov) { HITS.push({ f, x, y, s, label: null }); return; }
      // Never over another name: a focused or pointed-at funder with no free place takes the first place clear of names.
      const spot = free || spots.find(sp => !off(boxAt(sp)) && !hits(boxAt(sp), names)) || spots[0], b = boxAt(spot), lx = x + spot[0], ly = y + spot[1];
      names.push(b);
      ctx.lineWidth = 4; ctx.strokeStyle = paper; ctx.strokeText(label, lx, ly);
      ctx.fillStyle = hov && !sel ? (isDark() ? '#8bbdf5' : '#1f5fbf') : ink; ctx.fillText(label, lx, ly);
      HITS.push({ f, x, y, s, label: b });
    });
    // The picked funder's museums get their own dots, drawn last (user, 17 Nov 2026: "museums lost its dots"). The page's
    // own dot for a space is a 3.5px ring 0.8px thick in its grade's colour, drawn before this layer, so the lines and the
    // paper halos of the names covered it (Anchorage, Banff) and an Unverified ring, olive on paper, barely showed (MALBA).
    // Here each is an ink ring 8px across on paper, 1.5px thick: hollow, so it is told from a funder's solid 6px dot.
    ctx.setLineDash([]); ctx.lineWidth = 1.5; ctx.strokeStyle = ink;
    museumDots.forEach(({ id, x, y }) => {
      ctx.beginPath(); ctx.arc(x, y, 4, 0, Math.PI * 2);
      ctx.fillStyle = hoverSpace === id ? ink : paper; ctx.fill(); ctx.stroke();
    });
    ctx.restore();
  };
  // A picked funder's space named on the map, under the pointer.
  const spaceAt = (mx, my) => { const h = SPACE_HITS.find(q => mx >= q.box.x && mx <= q.box.x + q.box.w && my >= q.box.y && my <= q.box.y + q.box.h); return h ? h.id : null; };
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
      const sp = spaceAt(mx, my), f = sp ? null : hitAt(mx, my);
      if (f !== hover || sp !== hoverSpace) { hover = f; hoverSpace = sp; if (window.scheduleRender) window.scheduleRender(); }
      return !!(f || sp);
    },
    // A funder opens its ledger and its spaces come onto the map; picking it again puts it away.
    click(mx, my) {
      if (!on) return false;
      // A space's name opens that space, as its name in the chat does (user, 17 Nov 2026: "make the museum names in chat
      // clickable on the map too").
      const sp = spaceAt(mx, my);
      if (sp) { if (typeof window.selectInstitution === 'function') window.selectInstitution(sp, false); return true; }
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
      if (window.atlasHq && window.atlasHq.ready) window.atlasHq.ready(mergeMoney);   // the funding maps: their funders join the map, and a funder's record can open
      measureButtons();
      greet();
    } else {
      picked = null; pickedSpaces = null; hover = null; hoverSpace = null; MEASURE = 'culture'; paintMeasureButtons();
      say('<p class="no-indent">Influence map is off. The map shows the museums again.</p>');
    }
    if (typeof window.atlasRefilter === 'function') window.atlasRefilter();
    decorate();
  }
  window.toggleInfluenceMode = toggle;
  // A space's Money map button (assets/layers.js, atlasShowMoney): the mode opens on that space and the chat lists who pays it.
  window.atlasInfluenceFocusSpace = id => {
    pick(null);
    const go = () => {
      mergeMoney();
      if (!on || !DATA || !id) return;
      const list = DATA.funders.filter(f => spacesOf(f).has(id)).sort((a, b) => (b.ties.length - a.ties.length) || a.name.localeCompare(b.name));
      const inst = (g('ALL_INSTITUTIONS') || []).find(i => i.id === id);
      if (!list.length || !inst) return;
      const rows = list.map(f => `<li><a href="#" class="influence-funder-link" data-influence-funder="${esc(f.key)}">${esc(f.name)}</a></li>`).join('');
      say(`<div class="influence-chat"><p class="no-indent">${esc(inst.name)}: ${plural(list.length, 'private funder')} with a head office on the map.</p><ul class="influence-funders">${rows}</ul></div>`);
      if (window.scheduleRender) window.scheduleRender();
    };
    if (window.atlasHq && window.atlasHq.ready && !window.atlasHq.loaded()) window.atlasHq.ready(go); else go();
  };
  window.isInfluenceModeActive = () => on;

  // ---- The chat ----
  function say(html) {
    if (typeof appendCuratorMessage === 'function') appendCuratorMessage(html, [], null, null, false);
  }
  function greet() {
    if (!DATA) { say('<p class="no-indent">Influence map is on, but it could not load. Try again in a moment.</p>'); return; }
    // One short paragraph (user, 17 Nov 2026: "influence mode intro in chat is a slop, shorten it ... no need to list all
    // spaces"; then, of "351 entries on 25 private funders, read by hand from the spaces' records": "this is a slop, delete
    // all the jargon"). The funders are on the map and each record says what it got, so the chat does not list them again.
    say(`<div class="influence-chat">
<p class="no-indent">Influence map is on. The map now shows the companies, foundations and private fortunes that pay for culture, at their head offices. Pick one to see which museums it pays and, where the records say, what its money bought.</p>
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
      let e = (hq && hq.funderRecord && hq.funderRecord(key)) || { key, kind: 'org', k: f.kind === 'corp' ? 'corp' : f.kind === 'fund' ? 'priv' : 'found', n: f.name, c: '', co: '', noOffice: true };
      // The mode places every pilot funder at an office (assets/influence.json, hq), so its record names that office too.
      if (e.noOffice && f.hq) e = Object.assign({}, e, { c: f.hq.c, co: f.hq.co, a: f.hq.a, lat: f.hq.lat, lon: f.hq.lon, noOffice: false });
      // Its own office layer stays off: the mode draws the funders itself (assets/hq-detail.js reads noLayer).
      if (typeof window.atlasHqOpen === 'function') window.atlasHqOpen(Object.assign({}, e, { noLayer: true }));
      openFor = f;
      pick(f);
      decorate();
      if (on) sayFunderSpaces(f);
    };
    if (window.atlasHq && window.atlasHq.ready && !window.atlasHq.loaded()) window.atlasHq.ready(go); else go();
  }
  // The picked funder's spaces in the chat as well as on the map (user, 17 Nov 2026: "show the museum names in the chat
  // too"): one line each, the name a link to its record, the city after it, and "ended" where every tie there ended.
  function sayFunderSpaces(f) {
    const city = new Map(f.ties.map(t => [t.space, t.city]));
    const list = [...mapSpaces(f, 'culture')].map(([id, x]) => ({ id, name: x.name, city: city.get(id) || '', open: x.open })).sort((a, b) => String(a.name).localeCompare(String(b.name)));
    if (!list.length) return;
    const rows = list.map(x => `<li><a href="#" class="influence-space-link" data-influence-space="${esc(x.id)}">${esc(x.name)}</a>${x.city || !x.open ? `<span class="influence-meta">${x.city ? ', ' + esc(x.city) : ''}${x.open ? '' : ', ended'}</span>` : ''}</li>`).join('');
    say(`<div class="influence-chat">
<p class="no-indent">${esc(f.name)}: ${plural(list.length, 'museum')}.</p>
<ul class="influence-funders">${rows}</ul>
</div>`);
  }
  let openFor = null;   // the funder whose record the ledger was asked for, so the ledger finds it even under another spelling

  // ---- The records ----
  // Each line says how far it is checked (user, 17 Nov 2026: "check the entries against their source pages"): against a
  // page it cites, partly (the page gives the tie but not one detail), or only against the museum's page in this atlas.
  // The link is the page that bears it out where there is one.
  const checkWords = t => t.check === 'source' ? 'Source checked' : t.check === 'source-partly' ? `Source checked, except ${t.checked_missing || 'one detail'}` : 'Not found on its sources yet';
  const lineFor = (t, withSpace, withFunder) => {
    const src = t.checked_source || (t.sources || [])[0];
    const marks = [t.ended ? 'Ended' : '', t.protest ? 'Protested' : ''].filter(Boolean).join(', ');
    const kinds = t.kinds.length ? t.kinds.map(label).join(', ') : '';
    const who = withFunder ? `<a href="#" class="influence-funder-link" data-influence-funder="${esc(withFunder.key)}">${esc(withFunder.name)}</a>` : '';
    const where = withSpace ? `<a href="#" class="influence-space-link" data-influence-space="${esc(t.space)}">${esc(t.space_name)}</a>${t.city ? `<span class="influence-meta">, ${esc(t.city)}</span>` : ''}` : '';
    return `<li class="influence-entry">
<p class="no-indent">${who || where ? `<span class="influence-who">${who || where}</span> ` : ''}${kinds ? `<span class="lead-in">${esc(kinds)}.</span> ` : ''}${esc(t.summary)}</p>
<p class="no-indent influence-meta">${[t.date ? esc(String(t.date).slice(0, 10)) : '', marks ? `<span class="influence-mark">${esc(marks)}</span>` : '', `<span class="influence-check">${esc(checkWords(t))}</span>`, src ? `<a href="${esc(src)}" target="_blank" rel="noopener noreferrer">${esc(host(src))}</a>` : ''].filter(Boolean).join(' · ')}</p>
</li>`;
  };
  const row = (title, sub, inner) => `<section class="d-row" role="group"><div class="d-row-head"><h3 class="d-row-title">${esc(title)}</h3>${sub ? `<p class="d-row-sub no-indent">${esc(sub)}</p>` : ''}</div>${inner}</section>`;

  // What the MoMA Influence Map study says (user, 17 Nov 2026: "add moma money map to moma on our influence map ... just
  // add info ... skip visualisation"): its entries group by group, each with its role, money, note and first source, as the
  // study states them. A group shows three and folds the rest, as a record's long lists do.
  const STUDY_KEEP = 3;
  function studyRows(inst) {
    if (!STUDY || !inst || inst.id !== STUDY.space) return '';
    const line = x => {
      const src = (x.sources || [])[0];
      return `<li class="influence-entry"><p class="no-indent"><span class="influence-who">${esc(x.name)}.</span> ${x.role ? `<span class="lead-in">${esc(x.role)}.</span> ` : ''}${x.money ? esc(x.money) + '. ' : ''}${esc(x.note)}</p>${src ? `<p class="no-indent influence-meta"><a href="${esc(src)}" target="_blank" rel="noopener noreferrer">${esc(host(src))}</a></p>` : ''}</li>`;
    };
    const head = row('From the MoMA Influence Map', 'who funds and governs MoMA, from the study',
      `${STUDY.museum && STUDY.museum.note ? `<p class="no-indent">${esc(STUDY.museum.role)} ${esc(STUDY.museum.note)}</p>` : ''}<p class="no-indent influence-more"><a href="${esc(STUDY.page)}">Open the study</a></p>`);
    return head + STUDY.groups.map(g => {
      const shown = g.entries.slice(0, STUDY_KEEP).map(line), rest = g.entries.slice(STUDY_KEEP).map(line);
      const fold = rest.length ? `<li class="d-row-fold"><details><summary><span class="fold-closed">${rest.length} more</span><span class="fold-open">Fewer</span></summary><ul class="d-row-list influence-list">${rest.join('')}</ul></details></li>` : '';
      return row(g.title, '', `<ul class="d-row-list influence-list">${shown.join('')}${fold}</ul>`);
    }).join('');
  }

  function spacePart(inst) {
    const list = (inst && BY_SPACE.get(inst.id)) || [];
    const study = studyRows(inst);
    if (!list.length && !study) return null;
    const byF = new Map();
    list.forEach(({ funder, tie }) => { if (!byF.has(funder)) byF.set(funder, []); byF.get(funder).push(tie); });
    // What was bought first, newest first; a protest or resignation with nothing bought stated comes after.
    byF.forEach(ties => ties.sort((a, b) => (!a.kinds.length - !b.kinds.length) || String(b.date || '0').localeCompare(String(a.date || '0'))));
    const el = document.createElement('div');
    el.className = 'prose-part d-rows influence-part';
    el.setAttribute('role', 'region');
    el.setAttribute('aria-label', 'What funders got here');
    el.innerHTML = row('What funders got here', '', '') +
      [...byF.entries()].map(([f, ties]) => row(f.name, '', `<ul class="d-row-list influence-list">${ties.map(t => lineFor(t, false, null)).join('')}</ul><p class="no-indent influence-more"><a href="#" class="influence-funder-link" data-influence-funder="${esc(f.key)}">Everything ${esc(f.name)} got</a></p>`)).join('') + study;
    return el;
  }

  // The sender's side, from data/influence_senders.json: what the money is made from, what else it pays for, and what the
  // sources say happened to the money after a space said no. Each fact carries its own source, read on its page.
  const FACT_ROWS = [
    ['harm', 'Where the money comes from', null],
    ['scale', 'Its business', 'how big it is, for one year']
  ];
  // Lobbying and politics facts are no longer drawn in the record (user, 17 Nov 2026: "only keep relevant info to cultural
  // spaces"); they stay in the data.
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
    if (a.ended.length) inner += `<p class="no-indent"><span class="lead-in">Museums that dropped it.</span></p><ul class="d-row-list influence-list">${a.ended.map(x => lineFor(x, true, null)).join('')}</ul>`;
    if (a.kept.length) inner += `<p class="no-indent"><span class="lead-in">Gifts from ${esc(a.first)} on, with no word that they ended.</span></p><ul class="d-row-list influence-list">${a.kept.map(x => lineFor(x, true, null)).join('')}</ul>`;
    if (told.length) inner += `<p class="no-indent"><span class="lead-in">What happened next.</span></p><ul class="d-row-list influence-list">${told.map(factLine).join('')}</ul>`;
    return row('When a museum said no', 'saying no ends one deal, not the money', inner);
  }

  // What it gives culture, with the largest gift the atlas entries state and that gift's source. The lobbying and political
  // giving lines that stood beside it were taken out of the record (user, 17 Nov 2026: "delete these, only keep relevant
  // info to cultural spaces"); the figures stay in data/influence_senders.json for the map's measures.
  function compareRow(f) {
    const c = fig(f).culture || {}, src = c.largest_gift && c.largest_gift.source;
    const n = cultureSpaces(f);
    const body = `${n} ${n === 1 ? 'museum' : 'museums'}${c.largest_gift ? `; the largest gift found is ${c.largest_gift.text}` : ', with no amount given'}.`;
    return row('Culture', 'what it gives culture', `<ul class="d-row-list influence-list"><li class="influence-entry"><p class="no-indent">${esc(body)}</p>${src ? `<p class="no-indent influence-meta"><a href="${esc(src)}" target="_blank" rel="noopener noreferrer">${esc(host(src))}</a></p>` : ''}</li></ul>`);
  }

  // What the records say its lobbying or political money did at a space, measure by measure, each with its source.
  function linkRows(f) {
    const items = f.ties.flatMap(t => (t.links || []).map(l => ({ t, l })));
    if (!items.length) return '';
    const what = { us: 'US lobbying', eu: 'EU lobbying', politics: 'Political giving', other: 'Other lobbying' };
    const lis = items.map(({ t, l }) => `<li class="influence-entry"><p class="no-indent"><span class="influence-who"><a href="#" class="influence-space-link" data-influence-space="${esc(t.space)}">${esc(t.space_name)}</a></span> <span class="lead-in">${esc(what[l.measure] || l.measure)}${l.gov ? `, ${esc(l.gov)}` : ''}.</span> ${esc(l.text)}</p>${l.source ? `<p class="no-indent influence-meta"><a href="${esc(l.source)}" target="_blank" rel="noopener noreferrer">${esc(host(l.source))}</a></p>` : ''}</li>`).join('');
    return row('Lobbying through museums', 'where a record ties its lobbying or political money to a space', `<ul class="d-row-list influence-list">${lis}</ul>`);
  }
  function funderPart(f) {
    const t = tally(f.ties);
    const el = document.createElement('div');
    el.className = 'prose-part d-rows influence-part';
    el.setAttribute('role', 'region');
    el.setAttribute('aria-label', `What ${f.name} got`);
    let html = row(`What ${f.name} got`, '', '');
    html += compareRow(f);
    html += linkRows(f);
    html += senderRows(f);
    ORDER.forEach(k => {
      const ties = f.ties.filter(x => (x.kinds.length ? x.kinds : []).includes(k));
      if (ties.length) html += row(label(k), MEANS[k], `<ul class="d-row-list influence-list">${ties.map(x => lineFor(x, true, null)).join('')}</ul>`);
    });
    html += afterRows(f);
    const pushback = f.ties.filter(x => !x.kinds.length);
    if (pushback.length) html += row('Pushback', 'protests and resignations', `<ul class="d-row-list influence-list">${pushback.map(x => lineFor(x, true, null)).join('')}</ul>`);
    if (t.ended || t.protest) html += `<p class="no-indent influence-meta">${esc([t.ended ? plural(t.ended, 'deal') + ' ended' : '', t.protest ? plural(t.protest, 'deal') + ' drew protest' : ''].filter(Boolean).join('; '))}.</p>`;
    { const ok = f.ties.filter(x => x.check === 'source').length, part = f.ties.filter(x => x.check === 'source-partly').length, n = f.ties.length;
      html += `<p class="no-indent influence-meta">${esc(`${ok} of ${n} lines are checked against a page they cite${part ? `, ${part} more in part` : ''}; the rest match the museum’s page in this atlas.`)}</p>`; }
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
    return DATA.funders.filter(f => !f.moneyOnly).find(f => norm(f.name) === name || norm(f.name.split(/[ /]/)[0]) === name || name.startsWith(norm(f.name.split(/[ /]/)[0]))) || null;
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
        if (f && !f.moneyOnly && head) head.after(funderPart(f));
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
    b.type = 'button'; b.id = 'gmInfluenceBtn'; b.textContent = 'Influence map';
    b.setAttribute('aria-pressed', String(on));
    b.addEventListener('click', () => toggle());
    gossip.after(b);
    const bar = gossip.parentElement;
    if (bar && bar.getAttribute('aria-label')) bar.setAttribute('aria-label', 'Chat, dark mode, gossip mode and influence map');
    return true;
  }

  // assets/layers.js repaints every chip in the row after a filter change, and would mark these as "All": they are painted after it.
  document.addEventListener('atlas:filter', () => setTimeout(() => { measureButtons(); paintMeasureButtons(); }));
  function init() {
    watch();
    let n = 0;
    const t = setInterval(() => { watch(); measureButtons(); if ((phoneButton() && document.querySelector('[data-influence-measure]')) || ++n > 50) clearInterval(t); }, 200);
    // Load the entries early, so the first switch is instant and ?influence opens the page in the mode.
    load().then(() => { if (/[?&](?:influence|money)\b/.test(location.search)) toggle(true); });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
