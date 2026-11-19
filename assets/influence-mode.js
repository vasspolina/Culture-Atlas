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
//   - a space's record leads with "What came with the money"
//   - a funder's record (assets/hq-detail.js) leads with its ledger: what it got, kind by kind, space by space
//
// The sender is the subject (user, 17 Nov 2026: "If the money doesn't go to culture it doesn't disappear so who is at
// fault?"). A space that says no ends one tie, not the money: so a funder's ledger also says where its money comes from and
// what else it pays for beside culture (hand-sourced facts, data/influence_senders.json, each with its own source), and,
// when a space ended a tie, which ties the records still date after that and do not say ended. On the map every space stays,
// faint where no money goes and darker the more funders reach it; a picked funder's spaces come up in full ink and the rest of
// the world stays pale (see "The field" below). An ended tie is a dashed line, the one line drawn unasked.
// Switched off, all four go and the page is as it was. Its look is the "INFLUENCE MODE" block at the end of assets/sheet.css.
(function () {
  let DATA = null, STUDY = null, ART = null, loading = null, on = false;
  const BY_SPACE = new Map(), BY_FUNDER = new Map();

  function load() {
    if (DATA) return Promise.resolve(DATA);
    if (loading) return loading;
    loading = fetch('assets/influence.json?v=24', { cache: 'no-cache' }).then(r => r.json()).then(d => {
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
    fetch('assets/moma-influence.json?v=8d', { cache: 'no-cache' }).then(r => r.json()).then(d => { STUDY = d; mergeStudy(); }).catch(() => {});
    // What art each funder's money goes to (tools/build_art_periods.py). Read beside the ledger; without it a record
    // simply goes without the row.
    fetch('assets/art-periods.json?v=1', { cache: 'no-cache' }).then(r => r.json()).then(d => { ART = d; }).catch(() => {});
    return loading;
  }

  const esc = s => String(s == null ? '' : s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const host = u => { try { return new URL(u).hostname.replace(/^www\./, ''); } catch (_) { return ''; } };
  // What came with the money, one plain label per kind, the user's own list (user, 19 Nov 2026: "just keep this not need
  // another column"): no second wording for the influence, and no note under a ledger row's heading. assets/influence.json
  // keeps its own labels and these win. "Its name on something" became "Its name on a building, room or prize" (user, 19 Nov 2026).
  const CAME = { name: 'Its name on a building, room or prize', seat: 'A board seat', programme: 'A show or programme it paid for',
    building: 'A building or endowment', access: 'Galas and perks', silence: 'Secrecy', licence: 'An image clean-up',
    tax: 'A tax break', money: 'Money only' };
  const label = k => { if (CAME[k]) return CAME[k]; const x = DATA && DATA.kinds.find(q => q.key === k); return x ? x.label : k; };
  const plural = (n, one, many) => `${n} ${n === 1 ? one : (many || one + 's')}`;
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
    mergeStudy();
    if (window.scheduleRender) window.scheduleRender();
  }
  // MoMA's funders from the MoMA Influence Map study join as dots (user, 17 Nov 2026: "show moma funders as dots on
  // the influence map"; "show government funders too"; "add the other public bodies too"; "add the other MoMA trustees as dots too"; the list and the offices are in tools/build_moma_influence.mjs). One the map already draws gains
  // MoMA among its museums; the rest are new dots at their offices, with MoMA as their one museum. Run once, after the
  // funding maps have joined, so a funder they name is never drawn twice.
  let studyMerged = false;
  function mergeStudy() {
    if (studyMerged || !merged || !DATA || !STUDY || !STUDY.funders) return;
    studyMerged = true;
    const inst = (g('ALL_INSTITUTIONS') || []).find(i => i.id === STUDY.space);
    const space = { id: STUDY.space, name: inst ? inst.name : 'MoMA' };
    const norm = x => String(x || '').toLowerCase().replace(/[^a-z0-9]+/g, ' ').trim();
    STUDY.funders.forEach(s => {
      const names = new Set([s.name, ...(s.names || [])].map(norm));
      let f = (s.keys || []).map(k => BY_FUNDER.get(k)).find(Boolean) || DATA.funders.find(q => names.has(norm(q.name)));
      if (!f) {
        if (!s.hq) return;
        f = { key: 'moma-study:' + norm(s.name).replace(/ /g, '-'), name: s.name, kind: s.kind, hq: Object.assign({ n: s.name }, s.hq), ties: [], moneySpaces: [], moneyOnly: true, study: s.from, notFunder: !!s.notFunder, kindLabel: s.kindLabel || (s.notFunder ? 'Public body' : '') };
        DATA.funders.push(f); BY_FUNDER.set(f.key, f);
      }
      f.moneySpaces = f.moneySpaces || [];
      if (!f.ties.some(t => t.space === space.id) && !f.moneySpaces.some(q => q.id === space.id)) f.moneySpaces.push(space);
      delete f._ms;
    });
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
    // The widest-reaching funder sits on the office and the rest spiral out from it in order of reach, so the big names
    // stay nearest their city. Only the place in the spiral is kept here; spread() turns it into pixels at the map's zoom.
    byCity.forEach(list => {
      list.sort((a, b) => cultureSpaces(b) - cultureSpaces(a));
      const outer = list.length > 1 ? 18 + 6 * Math.sqrt(list.length - 1) : 0;
      list.forEach((f, i) => fan.set(f, { a: -Math.PI / 2 + i * 2.39996, rr: i === 0 ? 0 : 18 + 6 * Math.sqrt(i), outer }));
    });
  }
  // A city's spiral, in pixels, at a globe radius of r. Its natural spacing (18px out, then 6 times the root of the place)
  // took New York's several hundred funders some 120px out over the Atlantic at world zoom, a cloud of dots at sea that
  // read as places (user, 18 Nov 2026: "keep working on it", then "there are dots in the ocean"). A cap in pixels (a
  // twenty-fourth of the globe's radius, never under 10px) cleared the Atlantic but not a narrow coast: Wellington's few
  // funders still sat in the sea round New Zealand ("i still couls see some dots in the waterr"). So the cap is now a
  // distance on the ground: the spiral's outer edge is held to SPIRAL_RAD of arc, about 19km, which is r * SPIRAL_RAD in
  // pixels. At world zoom that is about a pixel, so a city's funders sit on its office; their pale dots are one shape
  // filled once, so the pile does not darken. The spiral opens as the map closes in on the city, and reaches its natural
  // spacing only where a city fills the screen and each dot can be pointed at.
  const SPIRAL_RAD = 0.003;
  function spread(o, r) {
    if (!o || !o.rr) return { dx: 0, dy: 0 };
    const k = Math.min(1, r * SPIRAL_RAD / o.outer), d = o.rr * k;
    return { dx: Math.cos(o.a) * d, dy: Math.sin(o.a) * d };
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
      // A funder known only from the MoMA study names MoMA instead of "1 museum" (user, 17 Nov 2026: "keep working on this"),
      // so the CIA or a trustee does not read as a museum funder at large.
      text: f => { const n = cultureSpaces(f); if (n === 1 && f.study) return 'MoMA'; return n ? `${n} ${n === 1 ? 'museum' : 'museums'}` : ''; } },
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
    // The places that pay their own way, the other side of the map (user, 18 Nov 2026: "add tab about the places that have
    // no funding, self funded institions"; of three readings offered, "Pays its own way"). It is a measure of spaces, not of
    // funders, so no funder is drawn under it: the spaces it names are rings with their names, the rest of the world faint.
    self: { label: 'Self-funded', noun: 'self-funding', what: 'the places that pay their own way',
      value: () => null, text: () => '' },
  };
  // A space pays its own way when either
  //   - its accounts (the record's `finance`, read from a filed annual report) show at least half its income earned:
  //     tickets, shop, hire, sales, the money a place makes itself rather than is given; or
  //   - its record says in its own words that sales, visitors or artists pay for it, and names no private funder: the
  //     three below, read by hand on 18 Nov 2026 from the records' funding lines.
  // "Artist-run" alone is not enough: Khoj names the Ford Foundation and Sangeeta Jindal, the Lagos Biennial Terra and Ford,
  // Urban Shaman runs on the Canada Council. Nor is "self-funded by its founder": a founder's own fortune is private money
  // too (Ishara, Fabrika's paper mill, Bandjoun Station's coffee plantations), and Kupalaŭcy's record names projects paid
  // through a politician's foundation. tests/influence.test.mjs checks that these ids are records.
  const SELF_RECORDS = ['the-factory-contemporary-arts-centre-ho-chi-minh-city', 'taipei-contemporary-art-center-taipei', 'le-cube-independent-art-room-rabat'];
  let SELF = null;
  function selfFunded() {
    if (SELF) return SELF;
    const insts = g('ALL_INSTITUTIONS') || []; if (!insts.length) return new Map();
    SELF = new Map();
    insts.forEach(i => {
      const f = i.finance;
      if (f && f.income > 0 && f.earned != null && f.earned / f.income >= 0.5) {
        const pct = Math.round(100 * f.earned / f.income);
        SELF.set(i.id, { name: i.name, why: `earns ${pct}% of its income itself${f.fy ? ` (${f.fy} accounts)` : ''}`, source: f.url || '', share: f.earned / f.income });
      }
    });
    SELF_RECORDS.forEach(id => { const i = insts.find(q => q.id === id); if (i && !SELF.has(id)) SELF.set(id, { name: i.name, why: (i.funding || '').split(/(?<=\.)\s/).find(x => /self-funded|sales|paid by artists/i.test(x)) || i.funding || '', source: (i.sources || [])[0] || '', share: null }); });
    return SELF;
  }
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
  // ---- The field: the money as presence, its absence as fading ----
  // (user, 18 Nov 2026: "Maybe it's a little bit about fading out where the money doesn't go? And not using the lines as
  // much?", after Walid Raad, whose colours and lines withdraw from the artworks; then "do this": "Every space stays on the
  // map, set faint. The spaces a funder pays come up in full ink. Picking a funder no longer draws a starburst ... Lines
  // would become the exception: one appears only when you point at a space, or for an ended tie".) Before this the mode
  // took every space off the map, so where the money did not go was not drawn at all, and the lines did all the telling.
  // Now the page still hides the spaces (atlasModeKeep) and this layer draws all of them itself as small ink dots: with no
  // funder picked, a space's ink follows how many funders on the map reach it under the measure (FAINT for none, then up
  // a log scale to full ink for the most reached, MoMA); with one picked, its spaces are the page's own pins and this
  // layer's rings, and every other space is FAINT. ?lines in the address brings back the old drawing, to compare.
  const LINES = /[?&]lines(=|&|$)/.test(location.search);
  // An unreached space; a funder that is not the one in question, its dot and its name. The dots are fainter than the names:
  // at 0.3 the pale dots of Europe's hundreds of funders stacked back up into a dark mass round the picked funder's museums.
  // The pale dots are one shape filled once (below), so their ink no longer adds up where they overlap, and they have no
  // outline; 0.2 reads about as 0.15 with an outline did.
  const FAINT = 0.12, DIM_DOT = 0.2, DIM = 0.35;
  let REACH = null;
  function reach() {
    const key = MEASURE + ':' + DATA.funders.length + ':' + merged + ':' + studyMerged;
    if (REACH && REACH.key === key) return REACH;
    const by = new Map(); let max = 1;
    DATA.funders.forEach(f => mapSpaces(f).forEach((x, id) => { const n = (by.get(id) || 0) + 1; by.set(id, n); if (n > max) max = n; }));
    return (REACH = { key, by, max });
  }
  // Ink in eight steps, so the field is eight paths a frame and not 1,773.
  const STEPS = 8;
  const inkStep = (n, max) => n ? Math.max(1, Math.round(STEPS * Math.log(1 + n) / Math.log(1 + max))) : 0;
  const stepAlpha = k => k ? 0.3 + 0.7 * k / STEPS : FAINT;
  function field(ctx, project, r, cx, cy, ink, insts) {
    const R = reach(), sel = g('selectedInstitution'), paths = [], selfOn = MEASURE === 'self' && !picked;
    insts.forEach(i => {
      if (typeof i.lat !== 'number' || i === sel || (pickedSpaces && pickedSpaces.has(i.id))) return;
      if (selfOn && selfFunded().has(i.id)) return;
      const pt = project(i.lon, i.lat, r, cx, cy); if (!pt.front) return;
      const k = picked || selfOn ? 0 : inkStep(R.by.get(i.id) || 0, R.max);
      (paths[k] || (paths[k] = [])).push(pt);
    });
    ctx.fillStyle = ink;
    paths.forEach((pts, k) => {
      if (!pts) return;
      ctx.globalAlpha = stepAlpha(k);
      ctx.beginPath();
      pts.forEach(pt => { ctx.moveTo(pt.x + 2, pt.y); ctx.arc(pt.x, pt.y, 2, 0, Math.PI * 2); });
      ctx.fill();
    });
    ctx.globalAlpha = 1;
  }
  function setMeasure(m) {
    if (!MEASURES[m] || (m === MEASURE && m !== 'culture')) m = 'culture';
    MEASURE = m;
    paintMeasureButtons();
    if (window.scheduleRender) window.scheduleRender();
    if (on && DATA) sayMeasure();
  }
  function sayMeasure() {
    const M = MEASURES[MEASURE];
    if (MEASURE === 'self') {
      // The accounts first, those that earn most of their income at the top, then the records read by hand.
      const list = [...selfFunded()].sort((a, b) => (b[1].share == null ? -1 : b[1].share) - (a[1].share == null ? -1 : a[1].share));
      const items = list.map(([id, x]) => `<li><a href="#" class="influence-space-link" data-influence-space="${esc(id)}">${esc(x.name)}</a>: ${esc(x.why)}${x.source ? ` <a class="influence-meta" href="${esc(x.source)}" target="_blank" rel="noopener noreferrer">${esc(host(x.source))}</a>` : ''}</li>`).join('');
      // The list is kept out of assets/repeats.js: its lines differ by the place's name only (the National Theatre and English
      // National Ballet both earn 64% in their 2024-25 accounts on the same register), so the pass took one for a repeat. And
      // they are places, not all museums: an orchestra, a ballet, a college and a festival pay their own way too.
      say(`<div class="influence-chat"><p class="no-indent">Self-funded: ${list.length} places that pay their own way. Their accounts show they earn at least half their income themselves, from tickets, shops, hire and sales, or their record says sales and artists pay for them. A founder's own fortune does not count.</p><ul class="influence-funders" data-repeat-ok>${items}</ul></div>`);
      return;
    }
    const ranked = DATA.funders.filter(f => shown(f) && (M.value(f) || MEASURE !== 'culture')).sort((a, b) => (M.value(b) || 0) - (M.value(a) || 0));
    if (MEASURE !== 'culture') {
      // Each funder is listed with the museums its money for this measure is recorded at, and under it what each record
      // says happened there, with its source.
      const items = ranked.map(f => {
        const fig = M.text(f), links = tiesFor(f).flatMap(t => (t.links || []).filter(l => l.measure === MEASURE).map(l => ({ t, l })));
        const sub = links.map(({ t, l }) => `<li><a href="#" class="influence-space-link" data-influence-space="${esc(t.space)}">${esc(t.space_name)}</a>: ${esc(l.text)}${l.source ? ` <a class="influence-meta" href="${esc(l.source)}" target="_blank" rel="noopener noreferrer">${esc(host(l.source))}</a>` : ''}</li>`).join('');
        return `<li><a href="#" class="influence-funder-link" data-influence-funder="${esc(f.key)}">${esc(f.name)}</a>${fig ? ` ${esc(fig)}` : ''}<ul class="influence-funders">${sub}</ul></li>`;
      }).join('');
      say(`<div class="influence-chat"><p class="no-indent">${esc(M.label)} at a museum${items ? '' : ': none'}.</p>${items ? `<ul class="influence-funders">${items}</ul>` : ''}</div>`);
      return;
    }
    const top = ranked.slice(0, 6).map(f => `<li><a href="#" class="influence-funder-link" data-influence-funder="${esc(f.key)}">${esc(f.name)}</a> ${esc(M.text(f))}</li>`).join('');
    say(`<div class="influence-chat"><p class="no-indent">${esc(M.label)}: each dot is labelled with ${esc(M.what)}.</p><ul class="influence-funders">${top}</ul></div>`);
  }
  // The buttons sit in the map's filter row (#gmdChips on a desktop, #gmChips on a phone) and take its place while the mode is
  // on: the space filters have nothing to filter when the map shows funders. assets/layers.js rebuilds that row, so the
  // buttons are put back whenever they go.
  const MEASURE_COLOURS = { culture: '#ffb066', us: '#8fc1ff', eu: '#d6a8ff', politics: '#f4b6c8', other: '#f2d95c', self: '#7fd1ae' };
  function measureButtons() {
    [['gmdChips', 'gmd-chip'], ['gmChips', 'gm-filter-chip']].forEach(([id, cls]) => {
      const host = document.getElementById(id); if (!host || host.querySelector('[data-influence-measure]')) return;
      Object.entries(MEASURES).forEach(([k, M]) => {
        const b = document.createElement('button');
        b.type = 'button'; b.className = cls; b.dataset.influenceMeasure = k; b.textContent = M.label;
        // Each measure wears its own colour (user, 18 Nov 2026: "color code"), through the coloured-filters rules in
        // atlas.css (.has-color + --layer-color): a pale wash off, the full fill on. Black text on every fill measures 10.9:1 or better.
        b.style.setProperty('--layer-color', MEASURE_COLOURS[k]); b.classList.add('has-color');
        b.title = k === 'culture' ? `Label each funder with ${M.what}` : k === 'self' ? `Show ${M.what}` : `${M.label} at a museum`;
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
    if (!LINES) field(ctx, project, r, cx, cy, ink, insts);
    // The picked funder's ties. A space that ended the tie is a dashed line, a running one solid: shape, not colour, says
    // which; a space with ties of both kinds takes the solid line, since some tie there is not said to have ended. Only the
    // dashed lines are drawn unasked, and a solid one to the space pointed at (its name here, or its pin on the page); the
    // rest is said by the field, the picked funder's spaces in ink on a pale world.
    if (picked && picked.hq) {
      const byId = new Map(insts.map(i => [i.id, i]));
      const hovInst = g('hoveredInstitution'), pointed = hoverSpace || (hovInst && hovInst.id);
      ctx.strokeStyle = ink; ctx.lineWidth = 1;
      mapSpaces(picked).forEach((x, id) => {
        if (!LINES && x.open && id !== pointed) return;
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
    // Its funders stay in full ink and the others go pale; a line goes only to the funder pointed at.
    if (FOCUS) {
      ctx.strokeStyle = ink; ctx.lineWidth = 1; ctx.setLineDash([]);
      FOCUS.forEach(f => { if (LINES || f === hover) arc(ctx, project, r, cx, cy, f.hq, sel); });
    }
    // A funder that is not the one in question (the picked funder, or a funder of the space in focus) is drawn pale, name
    // and dot, unless it is pointed at.
    const dim = f => !LINES && f !== hover && ((picked && picked !== f) || (FOCUS && !FOCUS.has(f)));
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
      const o = spread(fan.get(f), r), x = pt.x + o.dx, y = pt.y + o.dy;
      const v = linked ? M.value(f) : null;
      // Culture keeps its old scale, capped so Bloomberg's 80 spaces do not cover New York; a money measure is scaled to the
      // largest figure on the map, by area. No figure: a small hollow dot.
      const s = DOT;
      // A funder tied to a space under a money measure is labelled even with no figure (lobbying of other governments has
      // no filing to total): the tie is what the filter shows.
      marks.push({ f, x, y, s, n: v || 0, none: !v && !(linked && MEASURE !== 'culture') });
    });
    const placed = marks.map(m => ({ x: m.x - m.s - 2, y: m.y - m.s - 2, w: 2 * m.s + 4, h: 2 * m.s + 4 }));
    // At rest (nothing picked, no space in focus) the field is what the map says, so the funders step back: every dot is
    // drawn pale here, and only the funders whose names find a place are set again in full ink once the names are down
    // (below). With 1,216 solid dots the field could not be seen (user, 18 Nov 2026: "keep working", on the question of
    // whether the funder dots should give way); the dots keep their one size, as the user asked on 17 Nov 2026.
    const resting = !LINES && !picked && !FOCUS;
    const dot = (m, a) => {
      const sel = picked === m.f, hov = hover === m.f;
      mark(ctx, m.f, m.x, m.y, m.s);
      ctx.globalAlpha = a;
      // Solid ink; a funder with no figure for the measure is hollow, the picked one gets a ring.
      ctx.fillStyle = m.none && !sel && !hov ? paper : ink; ctx.fill();
      ctx.strokeStyle = ink; ctx.lineWidth = 1; ctx.stroke();
      if (sel) { ctx.beginPath(); ctx.arc(m.x, m.y, DOT + 3, 0, Math.PI * 2); ctx.stroke(); }
      ctx.globalAlpha = 1;
    };
    // The pale dots are drawn as one shape and filled once, so where they overlap the ink does not add up: drawn one by one,
    // a few hundred funders in one city at 0.15 each stacked into solid black, which on a phone, where a city's spiral is
    // 10px across, made the US and Europe black blots over the field again (user, 18 Nov 2026: "keep working on this").
    const pale = marks.filter(m => dim(m.f) || (resting && hover !== m.f));
    if (pale.length) {
      ctx.beginPath();
      pale.forEach(m => { ctx.moveTo(m.x + m.s + 0.5, m.y); ctx.arc(m.x, m.y, m.s + 0.5, 0, Math.PI * 2); });
      ctx.globalAlpha = DIM_DOT; ctx.fillStyle = ink; ctx.fill(); ctx.globalAlpha = 1;
    }
    const paleSet = new Set(pale);
    marks.forEach(m => { if (!paleSet.has(m)) dot(m, 1); });
    ctx.font = FONT; ctx.textBaseline = 'middle'; ctx.lineJoin = 'round';
    const hits = (b, list) => list.some(q => b.x < q.x + q.w && q.x < b.x + b.w && b.y < q.y + q.h && q.y < b.y + b.h);
    // A place that runs off the map's edge counts as taken, so a long label turns inward.
    const off = b => b.x < 2 || b.y < 2 || b.x + b.w > W - 2 || b.y + b.h > H - 2;
    // The names set so far, kept apart from the dots: a museum's name may lie over another funder's dot (the halo keeps
    // it readable), never over another name (user, 17 Nov 2026: the picked funder's name, its museums' names and the
    // names round them were drawn over each other in Europe).
    const names = [];
    // The measure buttons sit over the map (#gmdChips on a desktop, #gmChips on a phone), so their places count as taken: a
    // name was set under them ("Samsung (Lee family)" under Other lobbying on a phone, a name cut by Political giving on
    // a desktop). A hidden row measures nothing and takes no place.
    const cr = ctx.canvas.getBoundingClientRect();
    ['gmdChips', 'gmChips'].forEach(id => {
      const h = document.getElementById(id); if (!h) return;
      h.querySelectorAll('button').forEach(b => { const q = b.getBoundingClientRect(); if (q.width && q.height) names.push({ x: q.left - cr.left - 4, y: q.top - cr.top - 4, w: q.width + 8, h: q.height + 8 }); });
    });
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
    // Under Self-funded, with no funder picked, the places that pay their own way take the picked funder's part: rings with
    // their names, which open the place.
    const ringNames = picked ? new Map([...mapSpaces(picked)].map(([id, x]) => [id, x.name]))
      : MEASURE === 'self' ? new Map([...selfFunded()].map(([id, x]) => [id, x.name])) : null;
    if (ringNames) {
      const byId = new Map(insts.map(i => [i.id, i]));
      const spaceNames = ringNames;
      const pts = [];
      spaceNames.forEach((nm, id) => {
        const i = byId.get(id); if (!i || typeof i.lat !== 'number') return;
        const pt = project(i.lon, i.lat, r, cx, cy); if (!pt.front) return;
        pts.push({ id, x: pt.x, y: pt.y, label: i.name || nm || '' });
        museumDots.push({ id, x: pt.x, y: pt.y });
      });
      // The space in focus is named by the globe itself, above its dot (index.html): it is not named twice here, and that
      // name's place is kept clear: it is set larger than these names and stands above the pin, so the box is wide and tall.
      const selNow = g('selectedInstitution');
      if (selNow && typeof selNow.lat === 'number') {
        const sp = project(selNow.lon, selNow.lat, r, cx, cy);
        if (sp.front) { const w = ctx.measureText(selNow.name || '').width * 1.6 + 24; names.push({ x: sp.x - w / 2, y: sp.y - 70, w, h: 64 }); }
      }
      // A space's own dot is kept clear by every name, its own and the others'.
      const spaceDots = pts.map(q => ({ x: q.x - 5, y: q.y - 5, w: 10, h: 10 }));
      if (pickedMark) spaceDots.push({ x: pickedMark.x - DOT - 5, y: pickedMark.y - DOT - 5, w: 2 * DOT + 10, h: 2 * DOT + 10 });
      pts.forEach(({ id, x, y, label }) => {
        if (!label || (selNow && selNow.id === id)) return;
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
      // Never over another name: a focused or pointed-at funder with no free place takes the first place clear of names. A
      // funder of the space in focus with none (MoMA's two dozen, all in New York) keeps its dot and line and waits for the
      // map to be zoomed in, as any other name does; only the one pointed at insists.
      const clear = free || spots.find(sp => !off(boxAt(sp)) && !hits(boxAt(sp), names));
      if (!clear && !hov) { HITS.push({ f, x, y, s, label: null }); return; }
      const spot = clear || spots[0], b = boxAt(spot), lx = x + spot[0], ly = y + spot[1];
      names.push(b);
      ctx.globalAlpha = dim(f) ? DIM : 1;
      ctx.lineWidth = 4; ctx.strokeStyle = paper; ctx.strokeText(label, lx, ly);
      ctx.fillStyle = hov && !sel ? (isDark() ? '#8bbdf5' : '#1f5fbf') : ink; ctx.fillText(label, lx, ly);
      ctx.globalAlpha = 1;
      HITS.push({ f, x, y, s, label: b });
    });
    if (resting) {
      const named = new Set(HITS.filter(h => h.label).map(h => h.f));
      marks.forEach(m => { if (named.has(m.f) && hover !== m.f) dot(m, 1); });
    }
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
    // Its last sentence says what the field's ink means (user, 18 Nov 2026: "fading out where the money doesn't go"),
    // since nothing else on the page does.
    say(`<div class="influence-chat">
<p class="no-indent">Influence map is on. The map now shows the companies, foundations and private fortunes that pay for culture, at their head offices. Pick one to see which museums it pays, what its money bought and what kind of art it backs. A museum is darker the more of them pay it, and faint where none is on record.</p>
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
      // A funder from the MoMA study has no record in the funding maps, whose lookup would answer with its key for a name.
      let e = (!f.study && hq && hq.funderRecord && hq.funderRecord(key)) || { key, kind: 'org', k: f.kind === 'corp' ? 'corp' : f.kind === 'fund' ? 'priv' : f.kind === 'gov' ? 'gov' : 'found', n: f.name, c: '', co: '', noOffice: true };
      // The mode places every pilot funder at an office (assets/influence.json, hq), so its record names that office too.
      if (f.kindLabel) e = Object.assign({}, e, { kindLabel: f.kindLabel });
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
    const art = artLine(f);
    say(`<div class="influence-chat">
<p class="no-indent">${esc(f.name)}: ${plural(list.length, 'museum')}.</p>${art ? `
<p class="no-indent">${esc(art)}</p>` : ''}
<ul class="influence-funders">${rows}</ul>
</div>`);
  }
  let openFor = null;   // the funder whose record the ledger was asked for, so the ledger finds it even under another spelling

  // ---- The records ----
  // Each line was checked against its source pages (user, 17 Nov 2026: "check the entries against their source pages"); the
  // result stays in the data (check, checked_source) and is not printed: "Source checked" and "Not found on its sources yet"
  // were notes on the research, not facts about the funder (user, 18 Nov 2026: "notes like founded not founded ... gone").
  // The link is the page that bears it out where there is one.
  const lineFor = (t, withSpace, withFunder) => {
    const src = t.checked_source || (t.sources || [])[0];
    const marks = [t.ended ? 'Ended' : '', t.protest ? 'Protested' : ''].filter(Boolean).join(', ');
    // No label opens the line (user, 19 Nov 2026: "keep it simple by saying what actually he put the name on, and skipping
    // the title"): the sentence says what the money paid for or what carries the name.
    const kinds = '';
    const who = withFunder ? `<a href="#" class="influence-funder-link" data-influence-funder="${esc(withFunder.key)}">${esc(withFunder.name)}</a>` : '';
    const where = withSpace ? `<a href="#" class="influence-space-link" data-influence-space="${esc(t.space)}">${esc(t.space_name)}</a>${t.city ? `<span class="influence-meta">, ${esc(t.city)}</span>` : ''}` : '';
    return `<li class="influence-entry">
<p class="no-indent">${who || where ? `<span class="influence-who">${who || where}</span> ` : ''}${kinds ? `<span class="lead-in">${esc(kinds)}.</span> ` : ''}${esc(t.summary)}</p>
<p class="no-indent influence-meta">${[t.date ? esc(String(t.date).slice(0, 10)) : '', marks ? `<span class="influence-mark">${esc(marks)}</span>` : '', src ? `<a href="${esc(src)}" target="_blank" rel="noopener noreferrer">${esc(host(src))}</a>` : ''].filter(Boolean).join(' · ')}</p>
</li>`;
  };
  const row = (title, sub, inner, titleHtml) => `<section class="d-row" role="group"><div class="d-row-head"><h3 class="d-row-title">${titleHtml || esc(title)}</h3>${sub ? `<p class="d-row-sub no-indent">${esc(sub)}</p>` : ''}</div>${inner}</section>`;

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
    const head = row('From the MoMA Influence Map', 'who funds and governs MoMA',
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
    el.setAttribute('aria-label', 'What came with the money');
    el.innerHTML = row('What came with the money', '', '') +
      [...byF.entries()].map(([f, ties]) => row(f.name, '', `<ul class="d-row-list influence-list">${ties.map(t => lineFor(t, false, null)).join('')}</ul>`, `<a href="#" class="influence-funder-link" data-influence-funder="${esc(f.key)}">${esc(f.name)}</a>`)).join('') + study;
    return el;
  }

  // The sender's side, from data/influence_senders.json: what the money is made from, what else it pays for, and what the
  // sources say happened to the money after a space said no. Each fact carries its own source, read on its page.
  const FACT_ROWS = [
    ['harm', 'Where the money comes from', null],
    ['scale', 'Size of its business', 'in one year']
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
    if (a.kept.length) inner += `<p class="no-indent"><span class="lead-in">Gifts since ${esc(a.first)}.</span></p><ul class="d-row-list influence-list">${a.kept.map(x => lineFor(x, true, null)).join('')}</ul>`;
    if (told.length) inner += `<p class="no-indent"><span class="lead-in">What happened next.</span></p><ul class="d-row-list influence-list">${told.map(factLine).join('')}</ul>`;
    return row('When a museum said no', '', inner);
  }

  // What it gives culture, with the largest gift the atlas entries state and that gift's source. The lobbying and political
  // giving lines that stood beside it were taken out of the record (user, 17 Nov 2026: "delete these, only keep relevant
  // info to cultural spaces"); the figures stay in data/influence_senders.json for the map's measures.
  function compareRow(f) {
    const c = fig(f).culture || {}, src = c.largest_gift && c.largest_gift.source;
    const n = cultureSpaces(f);
    const body = `Gives to ${n} ${n === 1 ? 'museum' : 'museums'}.${c.largest_gift ? ` The largest gift is ${c.largest_gift.text}.` : ''}`;
    return row('Giving to museums', '', `<ul class="d-row-list influence-list"><li class="influence-entry"><p class="no-indent">${esc(body)}</p>${src ? `<p class="no-indent influence-meta"><a href="${esc(src)}" target="_blank" rel="noopener noreferrer">${esc(host(src))}</a></p>` : ''}</li></ul>`);
  }

  // What the records say its lobbying or political money did at a space, measure by measure, each with its source.
  function linkRows(f) {
    const items = f.ties.flatMap(t => (t.links || []).map(l => ({ t, l })));
    if (!items.length) return '';
    const what = { us: 'US lobbying', eu: 'EU lobbying', politics: 'Political giving', other: 'Other lobbying' };
    const lis = items.map(({ t, l }) => `<li class="influence-entry"><p class="no-indent"><span class="influence-who"><a href="#" class="influence-space-link" data-influence-space="${esc(t.space)}">${esc(t.space_name)}</a></span> <span class="lead-in">${esc(what[l.measure] || l.measure)}${l.gov ? `, ${esc(l.gov)}` : ''}.</span> ${esc(l.text)}</p>${l.source ? `<p class="no-indent influence-meta"><a href="${esc(l.source)}" target="_blank" rel="noopener noreferrer">${esc(host(l.source))}</a></p>` : ''}</li>`).join('');
    return row('Lobbying through museums', '', `<ul class="d-row-list influence-list">${lis}</ul>`);
  }
  // ---- What art the money pays for ----
  // Reader feedback (user, 19 Nov 2026): "see what kind of influence they're buying. I.e. are they funding modern art,
  // contemporary, or old masters?" assets/art-periods.json, from tools/build_art_periods.py, reads each space from its own
  // description in the atlas and keeps the sentence that decided it; where a tie's own line names the art the gift paid for
  // ("Major partner of the contemporary galleries"), that wins for that space. A space whose words name no period is
  // counted as not stated, never guessed: the Louvre's and the Prado's descriptions name none, so they are not old masters
  // here until a record says so. The spaces are the ones the map joins to the funder, so the counts add up to "Gives to N".
  const ART_KEYS = ['ancient', 'old', 'c19', 'modern', 'contemporary', 'all', 'art'];
  const NOT_ART = ['mixed', 'performing', 'design', 'photo', 'books', 'history', 'science'];
  function artGroups(f) {
    if (!ART) return null;
    const gift = new Map();
    f.ties.forEach(t => { const x = t.cid && ART.ties[t.cid]; if (x) gift.set(t.space, [...new Set([...(gift.get(t.space) || []), ...x.p])]); });
    const groups = new Map();
    for (const [id, x] of mapSpaces(f, 'culture')) {
      const s = ART.spaces[id];
      let keys = gift.get(id);
      const fromGift = !!keys;
      if (keys) keys = keys.length >= 4 ? ['all'] : keys;
      else keys = !s ? ['none'] : s.f === 'all' ? ['all'] : (s.p || [s.f]);
      keys.forEach(k => { if (!groups.has(k)) groups.set(k, []); groups.get(k).push({ id, name: x.name, gift: fromGift, field: s && !s.p ? s.f : null }); });
    }
    groups.forEach(l => l.sort((a, b) => String(a.name).localeCompare(String(b.name))));
    return groups;
  }
  const artLabel = k => {
    if (k === 'none') return 'Not stated';
    const x = ART && [...ART.periods, ...ART.fields].find(q => q.key === k);
    return x ? x.label : k;
  };
  const artSpan = k => { const x = ART && ART.periods.find(q => q.key === k); return x ? x.span : ''; };
  // One line for the chat: the periods first, then everything that is not visual art in one count.
  function artLine(f) {
    const g = artGroups(f); if (!g || !g.size) return '';
    const parts = ART_KEYS.filter(k => g.has(k)).map(k => `${artLabel(k).toLowerCase()} ${g.get(k).length}`);
    const other = new Set(NOT_ART.flatMap(k => (g.get(k) || []).map(x => x.id))).size;
    if (other) parts.push(`not visual art ${other}`);
    if (g.has('none')) parts.push(`not stated ${g.get('none').length}`);
    return parts.length ? `What art it backs: ${parts.join(', ')}.` : '';
  }
  const ART_SHOWN = 8;
  function artNames(list, withField) {
    const one = x => `<a href="#" class="influence-space-link" data-influence-space="${esc(x.id)}">${esc(x.name)}</a>${withField && x.field ? `<span class="influence-meta"> (${esc(artLabel(x.field).toLowerCase())})</span>` : ''}${x.gift ? '<span class="influence-meta"> (named in the gift)</span>' : ''}`;
    const shown = list.slice(0, ART_SHOWN).map(one).join(', '), rest = list.slice(ART_SHOWN).map(one).join(', ');
    return shown + (rest ? `<details class="influence-art-more"><summary><span class="fold-closed">${list.length - ART_SHOWN} more</span><span class="fold-open">Fewer</span></summary>${rest}</details>` : '');
  }
  function artRow(f) {
    const g = artGroups(f);
    // Not drawn when no museum of the funder's says what it shows: a row of "not stated" alone tells nothing.
    if (!g || !g.size || (g.size === 1 && g.has('none'))) return '';
    const line = (lead, list, meta, withField) => `<li class="influence-entry"><p class="no-indent"><span class="lead-in">${esc(lead)}.</span> ${plural(list.length, 'museum')}: ${artNames(list, withField)}</p>${meta ? `<p class="no-indent influence-meta">${esc(meta)}</p>` : ''}</li>`;
    let lis = ART_KEYS.filter(k => g.has(k)).map(k => line(artLabel(k), g.get(k), artSpan(k), false)).join('');
    const seen = new Set(), other = [];
    NOT_ART.forEach(k => (g.get(k) || []).forEach(x => { if (!seen.has(x.id)) { seen.add(x.id); other.push(x); } }));
    other.sort((a, b) => String(a.name).localeCompare(String(b.name)));
    if (other.length) lis += line('Not visual art', other, '', true);
    if (g.has('none')) lis += line('Not stated', g.get('none'), 'the atlas does not yet say what these show', false);
    return row('What art it backs', '', `<ul class="d-row-list influence-list">${lis}</ul><p class="no-indent influence-meta">From each museum’s own description in the atlas, or the gift’s own line where it names the art.</p>`);
  }
  // A funder from the funding maps alone has no ledger, but its museums still say what they show.
  function artPart(f) {
    const html = artRow(f); if (!html) return null;
    const el = document.createElement('div');
    el.className = 'prose-part d-rows influence-part';
    el.setAttribute('role', 'region');
    el.setAttribute('aria-label', 'What art it backs');
    el.innerHTML = html;
    return el;
  }
  function funderPart(f) {
    const t = tally(f.ties);
    const el = document.createElement('div');
    el.className = 'prose-part d-rows influence-part';
    el.setAttribute('role', 'region');
    el.setAttribute('aria-label', 'What came with the money');
    let html = row('What came with the money', '', '');
    html += compareRow(f);
    html += artRow(f);
    html += linkRows(f);
    html += senderRows(f);
    ORDER.forEach(k => {
      const ties = f.ties.filter(x => (x.kinds.length ? x.kinds : []).includes(k));
      if (ties.length) html += row(label(k), '', `<ul class="d-row-list influence-list">${ties.map(x => lineFor(x, true, null)).join('')}</ul>`);
    });
    html += afterRows(f);
    const pushback = f.ties.filter(x => !x.kinds.length);
    if (pushback.length) html += row('Protests and resignations', '', `<ul class="d-row-list influence-list">${pushback.map(x => lineFor(x, true, null)).join('')}</ul>`);
    if (t.ended || t.protest) html += `<p class="no-indent influence-meta">${esc([t.ended ? plural(t.ended, 'deal') + ' ended' : '', t.protest ? plural(t.protest, 'deal') + ' drew protest' : ''].filter(Boolean).join('; '))}.</p>`;
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
  // A MoMA-study funder's record: what the study says about it at MoMA, entry by entry, each with its source (user, 17 Nov
  // 2026: "show moma funders as dots on the influence map"; "show government funders too").
  function studyFunderPart(f) {
    if (!STUDY) return null;
    // In the order the funder's list gives them, so its own entry leads.
    const all = STUDY.groups.flatMap(gr => gr.entries);
    const entries = (f.study || []).map(n => all.find(x => x.name === n)).filter(Boolean);
    if (!entries.length) return null;
    const lis = entries.map(x => {
      const src = (x.sources || [])[0];
      return `<li class="influence-entry"><p class="no-indent">${entries.length > 1 || x.name !== f.name ? `<span class="influence-who">${esc(x.name)}.</span> ` : ''}${x.role ? `<span class="lead-in">${esc(x.role)}.</span> ` : ''}${x.money ? esc(x.money) + '. ' : ''}${esc(x.note)}</p>${src ? `<p class="no-indent influence-meta"><a href="${esc(src)}" target="_blank" rel="noopener noreferrer">${esc(host(src))}</a></p>` : ''}</li>`;
    }).join('');
    const el = document.createElement('div');
    el.className = 'prose-part d-rows influence-part';
    el.setAttribute('role', 'region');
    el.setAttribute('aria-label', 'At MoMA');
    el.innerHTML = row('At MoMA', 'from the MoMA Influence Map', `<ul class="d-row-list influence-list">${lis}</ul><p class="no-indent influence-more"><a href="#" class="influence-space-link" data-influence-space="${esc(STUDY.space)}">MoMA</a> · <a href="${esc(STUDY.page)}">Open the study</a></p>`);
    return el;
  }
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
        else if (f && f.study && head) { const part = studyFunderPart(f); if (part) head.after(part); }
        else if (f && f.moneyOnly && head) { const part = artPart(f); if (part) head.after(part); }
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
