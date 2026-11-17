// Influence mode: the atlas seen from the sender's side (user, 17 Nov 2026: "switch the perspective a little from the receivers
// to the senders ... and see what kind of influence they're buying"; "build it as layer on top of the app for now like a gossip mode").
//
// It reads assets/influence.json, written by tools/build_influence.py from the reviewed entries in data/influence_review.json:
// for each pilot funder, every tie where a record says what came with the money (a name, a seat, a programme, access, a
// building, silence, a tax break, licence to operate), or that the tie ended or met protest. Nothing here is inferred: each
// entry is a sentence of the record, summarised by the editor, with the record's sources for it.
//
// Switched on, it does four things and nothing else:
//   - the map shows only the spaces that hold an entry (window.atlasModeKeep, read by assets/layers.js)
//   - the chat says what the mode is and lists the funders with what each got, each one a button
//   - a space's record leads with "What funders got here"
//   - a funder's record (assets/hq-detail.js) leads with its ledger: what it got, kind by kind, space by space
// Switched off, all four go and the page is as it was. Its look is the "INFLUENCE MODE" block at the end of assets/sheet.css.
(function () {
  let DATA = null, loading = null, on = false;
  const BY_SPACE = new Map(), BY_FUNDER = new Map();

  function load() {
    if (DATA) return Promise.resolve(DATA);
    if (loading) return loading;
    loading = fetch('assets/influence.json?v=1', { cache: 'no-cache' }).then(r => r.json()).then(d => {
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

  // ---- The map: only the spaces with an entry ----
  window.atlasModeKeep = () => (on && DATA ? (i => !!(i && BY_SPACE.has(i.id))) : null);

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
      say('<p class="no-indent">Influence mode is off. The map shows every space again.</p>');
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
    const spaces = BY_SPACE.size;
    const rows = DATA.funders.map(f => `<li><button type="button" class="influence-funder-link" data-influence-funder="${esc(f.key)}">${esc(f.name)}</button> ${esc(tallyLine(f))}</li>`).join('');
    const kinds = ORDER.map(k => `<li><span class="lead-in">${esc(label(k))}</span> ${esc(MEANS[k])}</li>`).join('');
    say(`<div class="influence-chat">
<p class="no-indent">Influence mode is on. It turns the atlas round, from the spaces that take the money to the funders that give it, and asks what the money bought. The map now shows only the ${spaces} spaces where a record says so.</p>
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
      const e = (hq && hq.funderRecord && hq.funderRecord(key)) || { key, kind: 'org', k: f.kind === 'corp' ? 'corp' : 'found', n: f.name, c: '', co: '', noOffice: true };
      if (typeof window.atlasHqOpen === 'function') window.atlasHqOpen(e);
      openFor = f;
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

  function funderPart(f) {
    const t = tally(f.ties);
    const el = document.createElement('div');
    el.className = 'prose-part d-rows influence-part';
    el.setAttribute('role', 'region');
    el.setAttribute('aria-label', `What ${f.name} got`);
    let html = row(`What ${f.name} got`, tallyLine(f), '');
    ORDER.forEach(k => {
      const ties = f.ties.filter(x => (x.kinds.length ? x.kinds : []).includes(k));
      if (ties.length) html += row(label(k), MEANS[k], `<ul class="d-row-list influence-list">${ties.map(x => lineFor(x, true, null)).join('')}</ul>`);
    });
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
