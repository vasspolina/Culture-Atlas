// Funder headquarters and people's offices as things you can pick. layers.js draws the marks and keeps what each one links to;
// this file adds the three ways in and the record that opens:
//   a mouse or finger on the map  -> atlasHqPointer (index.html calls it from the globe's hover and click handlers)
//   the keyboard                  -> one real button laid over each mark in view (#hqMarks), invisible until it has focus
//   a crowded spot                -> a short list of everything under the pointer, so each mark and space stays pickable
// The record (#hqPanel) is set in the Details tab, the right column on a desktop and the record sheet on a phone, not in a window over the map
// (user's instruction, 19 Oct 2026). It shows the info the data holds, every name it holds, and the connections it holds: the spaces the
// office is named on, the other funders on those spaces, and the people the files tie to them. Nothing here is inferred.
(function () {
  const hq = () => window.atlasHq;
  const viewport = () => document.getElementById('globeViewport');
  const MAX_MARKS = 60;   // buttons laid over the map: the ones nearest the centre of the view, so the tab order stays short
  const LIST_SHOWN = 8;   // a connections list shows this many until "Show all" is pressed
  let panel = null, chooser = null, marksBox = null;
  let openFor = null, openFrom = null, chooserReturn = null;
  const buttons = new Map();

  function h(tag, attrs, ...kids) {
    const n = document.createElement(tag);
    Object.entries(attrs || {}).forEach(([k, v]) => { if (v === false || v == null) return; if (k === 'text') n.textContent = v; else n.setAttribute(k, v === true ? '' : v); });
    kids.flat().forEach(k => { if (k != null && k !== false) n.append(k); });
    return n;
  }
  const where = e => [e.c, e.co].filter(Boolean).join(', ');
  const markName = e => `${e.n}, ${hq().kindLabel(e)}, ${where(e)}`;

  // ---- Keyboard: a button over each mark in view ----
  function box() {
    if (marksBox && marksBox.isConnected) return marksBox;
    const vp = viewport(); if (!vp) return null;
    marksBox = h('div', { id: 'hqMarks', role: 'group', 'aria-label': 'Funder headquarters and offices in view. Press Enter on one to open its record.' });
    vp.appendChild(marksBox);
    return marksBox;
  }
  function markButton(e) {
    let b = buttons.get(e);
    if (b) return b;
    b = h('button', { type: 'button', class: 'hq-mark', 'aria-haspopup': 'dialog', 'aria-label': markName(e) });
    b.addEventListener('focus', () => { hq().hover(e); if (window.atlasHoldGlobe) window.atlasHoldGlobe(); });
    b.addEventListener('blur', () => hq().hover(null));
    b.addEventListener('click', () => openRecord(e, b));
    buttons.set(e, b);
    return b;
  }
  window.atlasHqFrame = function (hits) {
    const root = box(); if (!root) return;
    const vp = viewport(), W = vp.clientWidth, H = vp.clientHeight;
    const live = hits.filter(p => p.x > 4 && p.x < W - 4 && p.y > 4 && p.y < H - 4)
      .sort((a, b) => Math.hypot(a.x - W / 2, a.y - H / 2) - Math.hypot(b.x - W / 2, b.y - H / 2)).slice(0, MAX_MARKS)
      .sort((a, b) => a.x - b.x || a.y - b.y);
    const keep = new Set(live.map(p => p.e));
    const focused = document.activeElement && document.activeElement.classList.contains('hq-mark') ? document.activeElement : null;
    buttons.forEach((b, e) => { if (!keep.has(e) && b !== focused) { b.remove(); if (e !== openFor) buttons.delete(e); } });
    const settled = !root.contains(document.activeElement);
    live.forEach((p, i) => {
      const b = markButton(p.e);
      b.style.transform = `translate(${Math.round(p.x - 12)}px, ${Math.round(p.y - 12)}px)`;
      // The tab order follows the picture left to right, but is only rearranged while no mark has focus.
      if (!b.isConnected) root.appendChild(b);
      if (settled && root.children[i] !== b) root.insertBefore(b, root.children[i] || null);
    });
  };

  // ---- Chat: a click on a name prints what the records say about it in the chat ----
  // A funder asks the question the chat already answers for funders; a person asks the one it answers for people on boards.
  function askInChat(e) {
    const ask = window.atlasAskInChat || window.atlasAskCurator;
    if (typeof ask !== 'function') return;
    ask(e.kind === 'org' ? `Which institutions does ${e.n} fund?` : `Tell me about ${e.n} and museum board conflicts`);
  }

  // ---- Pointer: the globe's own handlers ask these first ----
  window.atlasHqPointer = {
    hover(mx, my, dots) {
      if (!hq() || !hq().loaded()) return false;
      const named = hq().labelAt(mx, my);
      if (named) { hq().hover(named); return true; }
      const t = hq().at(mx, my, hq().reach(), dots), m = t.marks[0];
      if (m && (!t.spaces[0] || m.d <= t.spaces[0].d)) { hq().hover(m.e); return true; }
      if (!(document.activeElement && document.activeElement.classList.contains('hq-mark'))) hq().hover(null);
      return false;
    },
    click(mx, my, clientX, clientY, dots) {
      if (!hq() || !hq().loaded()) return false;
      const named = hq().labelAt(mx, my);
      if (named) { askInChat(named); return true; }
      const t = hq().at(mx, my, hq().reach(), dots);
      if (!t.marks.length) return false;
      if (t.marks.length + t.spaces.length === 1) { openRecord(t.marks[0].e, null); return true; }
      openChooser(t, mx, my);
      return true;
    }
  };

  // ---- A crowded spot: everything under the pointer, each one pickable ----
  function closeChooser(restore) {
    if (!chooser) return;
    chooser.remove(); chooser = null;
    if (restore && chooserReturn && chooserReturn.isConnected) chooserReturn.focus();
    chooserReturn = null;
  }
  function openChooser(t, mx, my) {
    closeChooser(false);
    const vp = viewport(); if (!vp) return;
    chooserReturn = document.activeElement && document.activeElement !== document.body ? document.activeElement : null;
    const items = [];
    t.marks.forEach(m => items.push({ label: m.e.n, sub: `${hq().kindLabel(m.e)} · ${m.e.c}`, go: () => openRecord(m.e, null) }));
    t.spaces.forEach(s => items.push({ label: s.inst.name, sub: `Cultural space${s.inst.city ? ' · ' + s.inst.city : ''}`, go: () => { if (typeof window.selectInstitution === 'function') window.selectInstitution(s.inst, false); } }));
    chooser = h('div', { id: 'hqChooser', role: 'dialog', 'aria-label': `${items.length} places here. Choose one.` },
      h('p', { class: 'hq-chooser-title', text: `${items.length} places here` }),
      h('ul', null, items.map(it => h('li', null, (() => {
        const b = h('button', { type: 'button' }, h('span', { class: 'hq-l', text: it.label }), h('span', { class: 'hq-s', text: it.sub }));
        b.addEventListener('click', () => { closeChooser(false); it.go(); });
        return b;
      })()))));
    vp.appendChild(chooser);
    const W = vp.clientWidth, H = vp.clientHeight, cw = chooser.offsetWidth, ch = chooser.offsetHeight;
    chooser.style.left = Math.max(8, Math.min(W - cw - 8, mx + 14)) + 'px';
    chooser.style.top = Math.max(8, Math.min(H - ch - 8, my - 12)) + 'px';
    const first = chooser.querySelector('button'); if (first) first.focus();
  }
  document.addEventListener('pointerdown', ev => { if (chooser && !chooser.contains(ev.target)) closeChooser(false); }, true);

  // ---- The record ----
  // The record lives in the Details tab. On a desktop that is the record body of the right column; on a phone it is the record sheet's
  // scroll body. Whatever the tab held (a space's record) is hidden, not removed, while a funder's record shows, and comes back on close.
  function detailsHost() {
    return document.getElementById(window.innerWidth >= 768 ? 'desktopDossierRecordBody' : 'dossier-sheet-scrollable-body');
  }
  function ensurePanel() {
    if (!panel) panel = h('aside', { id: 'hqPanel', class: 'is-details', role: 'region', 'aria-labelledby': 'hqPanelTitle', tabindex: '-1', hidden: true });
    const host = detailsHost(); if (!host) return null;
    if (panel.parentElement !== host) {
      if (panel.parentElement) panel.parentElement.classList.remove('is-hq');
      host.appendChild(panel);
    }
    return panel;
  }
  function showDetails(host) {
    host.classList.add('is-hq');
    if (window.innerWidth >= 768) {
      if (typeof window.toggleDesktopDossier === 'function') window.toggleDesktopDossier(true);
    } else {
      const sheet = document.getElementById('dossier-bottom-sheet');
      if (sheet) { sheet.classList.remove('hidden'); sheet.classList.add('is-hq-sheet'); }
      const tab = document.getElementById('tab-dossier');
      if (tab && typeof window.setActiveMobileTab === 'function') window.setActiveMobileTab(tab);
    }
  }
  function listOf(items, build, cap) {
    const ul = h('ul', { class: 'hq-list' });
    const rows = items.map(build);
    rows.forEach((li, i) => { if (i >= cap) li.hidden = true; ul.appendChild(li); });
    if (rows.length <= cap) return ul;
    const more = h('button', { type: 'button', class: 'hq-more', 'aria-expanded': 'false', text: `Show all ${rows.length}` });
    more.addEventListener('click', () => {
      const expand = more.getAttribute('aria-expanded') !== 'true';
      rows.forEach((li, i) => { li.hidden = !expand && i >= cap; });
      more.setAttribute('aria-expanded', String(expand));
      more.textContent = expand ? 'Show fewer' : `Show all ${rows.length}`;
    });
    return h('div', null, ul, more);
  }
  const spaceRow = s => {
    const b = h('button', { type: 'button', class: 'hq-link' }, h('span', { class: 'hq-l', text: s.rec.n }), h('span', { class: 'hq-s', text: s.rec.c || '' }));
    b.addEventListener('click', () => hq().flyToSpace(s.rec));
    const li = h('li', null, b);
    // A person's tie to a space carries the record's own wording and how well it is documented; shown as written.
    if (s.label) li.append(h('p', { class: 'hq-note', text: `${s.label.charAt(0).toUpperCase() + s.label.slice(1)}${s.status ? ' (' + s.status + ')' : ''}${s.text ? ': ' + s.text : ''}` }));
    return li;
  };
  const officeRow = (o, shared) => {
    const b = h('button', { type: 'button', class: 'hq-link' }, h('span', { class: 'hq-l', text: o.n }), h('span', { class: 'hq-s', text: `${hq().kindLabel(o)} · ${o.c} · ${shared} shared ${shared === 1 ? 'space' : 'spaces'}` }));
    b.addEventListener('click', () => { hq().flyToOffice(o); openRecord(o, null, true); });
    return h('li', null, b);
  };

  function fill(e) {
    const p = panel, ready = hq().loaded();
    const close = h('button', { type: 'button', class: 'hq-close', 'aria-label': 'Close this record' }, '×');
    close.addEventListener('click', () => closeRecord(true));
    const head = h('div', { class: 'hq-head' }, h('div', null, h('p', { class: 'hq-kind', text: hq().kindLabel(e) }), h('h2', { id: 'hqPanelTitle', text: e.n })), close);
    const ask = h('button', { type: 'button', class: 'hq-ask', text: 'Ask in chat' });
    ask.addEventListener('click', () => askInChat(e));

    const info = h('section', { 'aria-labelledby': 'hqInfoT' }, h('h3', { id: 'hqInfoT', text: 'Info' }));
    const dl = h('dl');
    const row = (k, v) => { if (v) dl.append(h('dt', { text: k }), v instanceof Node ? h('dd', null, v) : h('dd', { text: v })); };
    row('Place', where(e));
    row('Address', e.a);
    if (e.kind === 'person') row('Role', e.w); else row('Note', e.w);
    if (e.s) { let host = e.s; try { host = new URL(e.s).hostname.replace(/^www\./, ''); } catch (x) {} row('Source', h('a', { href: e.s, target: '_blank', rel: 'noopener noreferrer', text: host })); }
    info.append(dl, h('p', { class: 'hq-note', text: 'The pin marks the city, not the building.' }));

    const names = h('section', { 'aria-labelledby': 'hqNamesT' }, h('h3', { id: 'hqNamesT', text: 'Names' }));
    if (!ready) names.append(h('p', { class: 'hq-note', text: 'Loading the other names…' }));
    else {
      const all = hq().names(e);
      names.append(h('ul', { class: 'hq-names' }, all.map((n, i) => h('li', { text: n }, i === 0 ? h('span', { class: 'hq-s', text: ' · used on the map' }) : null))));
      if (all.length === 1) names.append(h('p', { class: 'hq-note', text: 'The records give no other name for this one.' }));
      else names.append(h('p', { class: 'hq-note', text: 'The others are how spaces’ funding lines spell the same funder.' }));
    }

    const conns = h('section', { 'aria-labelledby': 'hqConnT' }, h('h3', { id: 'hqConnT', text: 'Connections' }));
    if (!ready) conns.append(h('p', { class: 'hq-note', role: 'status', text: 'Loading connections…' }));
    else {
      const sp = hq().spaces(e), rel = hq().related(e);
      const group = (id, title, list, build, empty) => {
        const g = h('div', { class: 'hq-group', role: 'group', 'aria-labelledby': id }, h('h4', { id, text: title }));
        g.append(list.length ? listOf(list, build, LIST_SHOWN) : h('p', { class: 'hq-note', text: empty }));
        conns.append(g);
      };
      group('hqConnSpaces', e.kind === 'org' ? `Funds ${sp.length} ${sp.length === 1 ? 'space' : 'spaces'}` : `Named on ${sp.length} ${sp.length === 1 ? 'space' : 'spaces'}`, sp, spaceRow,
        e.kind === 'org' ? 'No space in the atlas names this funder.' : 'No space in the atlas records this person.');
      if (e.kind === 'org') {
        group('hqConnFunders', 'Funds alongside', rel.funders, r => officeRow(r.e, r.shared), 'No other funder with a mapped head office shares a space with this one.');
        group('hqConnPeople', 'People the files tie to these spaces', rel.people, r => officeRow(r.e, r.shared), 'None.');
      }
    }
    p.replaceChildren(head, ask, info, names, conns);
    p.scrollTop = 0;
  }

  function openRecord(e, from, keepFocusOrigin) {
    const p = ensurePanel(); if (!p) return;
    closeChooser(false);
    if (!keepFocusOrigin) openFrom = from;
    openFor = e;
    hq().showLayer(e);
    hq().select(e);
    fill(e);
    p.hidden = false;
    showDetails(p.parentElement);
    p.querySelector('h2').setAttribute('tabindex', '-1');
    p.focus({ preventScroll: true });
    if (!hq().loaded()) hq().ready(() => { if (openFor === e) fill(e); });
  }
  function closeRecord(restore) {
    if (!panel || panel.hidden) return;
    panel.hidden = true; panel.replaceChildren();
    if (panel.parentElement) panel.parentElement.classList.remove('is-hq');
    const sheet = document.getElementById('dossier-bottom-sheet'); if (sheet) sheet.classList.remove('is-hq-sheet');
    openFor = null; hq().select(null);
    if (restore && openFrom && openFrom.isConnected) openFrom.focus();
    openFrom = null;
  }
  // Choosing a space (on the map, in the chat, or from a connection in this record) puts that space's record in the tab.
  window.atlasHqClose = () => closeRecord(false);
  // Escape closes the list first, then the record, and does not also clear the space or city the page has selected.
  document.addEventListener('keydown', ev => {
    if (ev.key !== 'Escape') return;
    if (chooser) { ev.stopPropagation(); closeChooser(true); return; }
    if (panel && !panel.hidden && (panel.contains(document.activeElement) || document.activeElement === document.body || (marksBox && marksBox.contains(document.activeElement)))) {
      ev.stopPropagation(); closeRecord(true);
    }
  }, true);
})();
