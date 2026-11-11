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
    const ul = h('ul', { class: 'd-row-list hq-list' });
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
    // A person's tie to a space is shown as the record's own sentence, without its category tag.
    if (s.text) li.append(h('p', { class: 'hq-note', text: s.text }));
    return li;
  };
  const officeRow = (o, shared) => {
    const b = h('button', { type: 'button', class: 'hq-link' }, h('span', { class: 'hq-l', text: o.n }), h('span', { class: 'hq-s', text: `${hq().kindLabel(o)} · ${o.c} · ${shared} shared ${shared === 1 ? 'space' : 'spaces'}` }));
    b.addEventListener('click', () => { hq().flyToOffice(o); openRecord(o, null, true); });
    return h('li', null, b);
  };

  // The record is set like a space's record (user, 2 Nov 2026): the name over a rule, then two columns, a third and two thirds. In the head
  // the Ask in chat pill is on the left and the place, address, note and source on the right. Under the head each part is a row under a
  // hairline: Names, then each connections group, its title on the left and its items on the right. All the classes are the space record's,
  // so the funder's record takes its typesetting (sizes, rhythm, the narrow one-column form) from the same rules.
  const row = (id, title, sub, items, extra) => {
    const head = h('div', { class: 'd-row-head' }, h('h3', { id, class: 'd-row-title', text: title }));
    if (sub) head.append(h('p', { class: 'd-row-sub no-indent', text: sub }));
    const sec = h('section', { class: 'd-row', role: 'group', 'aria-labelledby': id }, head);
    if (items) sec.append(items);
    if (extra) sec.append(extra);
    return sec;
  };
  const fact = (k, v) => v ? h('li', null, h('span', { class: 'lead-in', text: k + ' ' }), v instanceof Node ? v : document.createTextNode(v)) : null;

  function fill(e) {
    const p = panel, ready = hq().loaded();
    const close = h('button', { type: 'button', class: 'hq-close', 'aria-label': 'Close this record' });
    // A drawn cross, not the × character: the glyph sat low and small in its box and the hover square was off its centre.
    close.innerHTML = '<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"/></svg>';
    close.addEventListener('click', () => closeRecord(true));
    const title = h('div', { class: 'hq-head' }, h('div', null, h('p', { class: 'hq-kind', text: hq().kindLabel(e) }), h('h2', { id: 'hqPanelTitle', class: 'dossier-main-heading', text: e.n })), close);
    const ask = h('button', { type: 'button', class: 'record-action', text: 'Ask in chat' });
    ask.addEventListener('click', () => askInChat(e));

    // Head: the pill on the left; the place as the row's title, the address under it, then the note and the source as the row's points.
    const facts = h('ul', { class: 'd-row-list' });
    const add = li => { if (li) facts.append(li); };
    add(fact(e.kind === 'person' ? 'Role' : 'Note', e.w));
    if (e.s) { let host = e.s; try { host = new URL(e.s).hostname.replace(/^www\./, ''); } catch (x) {} add(fact('Source', h('a', { href: e.s, target: '_blank', rel: 'noopener noreferrer', text: host }))); }
    if (e.noOffice) facts.append(h('li', { text: 'No head office is mapped for this funder; the record is what the spaces’ funding lines say.' }));
    const info = row('hqInfoT', where(e) || 'Record', e.a || '', facts);
    const head = h('div', { class: 'record-head head-sheet rule-b hq-sheet' }, title,
      h('div', { class: 'head-grid' }, h('div', { class: 'head-side record-actions record-action-row' }, ask), h('div', { class: 'head-main' }, h('div', { class: 'prose-part d-rows', role: 'region', 'aria-label': 'Info' }, info))));

    const rows = h('div', { class: 'prose-part d-rows', role: 'region', 'aria-label': 'Names and connections' });
    // A row is shown only when it has something in it: no 'no other name', 'no space', 'None' lines (user, 3 Nov 2026).
    if (!ready) rows.append(row('hqConnT', 'Connections', 'Loading…'));
    else {
      // The other spellings only: the funder's own name is the title above, and the sentence that explained the list is gone
      // (user, 9 Nov 2026: "Slop"). No row when every funding line spells it as the title does.
      const others = hq().names(e).filter(n => n !== e.n);
      if (others.length) rows.append(row('hqNamesT', 'Also written', '', h('ul', { class: 'd-row-list hq-names' }, others.map(n => h('li', { text: n })))));
      const sp = hq().spaces(e), rel = hq().related(e);
      const group = (id, title, list, build) => { if (list.length) rows.append(row(id, title, '', listOf(list, build, LIST_SHOWN))); };
      // The row's title is the relation, not a count ("Funds 1 space": user, 9 Nov 2026, "Slop"); the list under it is the count.
      group('hqConnSpaces', e.kind === 'org' ? 'Funds' : 'Named on', sp, spaceRow);
      if (e.kind === 'org') {
        group('hqConnFunders', 'Funds alongside', rel.funders, r => officeRow(r.e, r.shared));
        group('hqConnPeople', 'People the files tie to these spaces', rel.people, r => officeRow(r.e, r.shared));
      }
    }
    p.replaceChildren(head, rows);
    p.scrollTop = 0;
  }

  function openRecord(e, from, keepFocusOrigin) {
    const p = ensurePanel(); if (!p) return;
    closeChooser(false);
    if (!keepFocusOrigin) openFrom = from;
    openFor = e;
    if (!e.noOffice) hq().showLayer(e);
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
    openFor = null; if (hq()) hq().select(null);
    if (window.atlasPlacePin) { window.atlasPlacePin = null; if (window.atlasDropPinRefresh) window.atlasDropPinRefresh(); }
    if (restore && openFrom && openFrom.isConnected) openFrom.focus();
    openFrom = null;
  }
  // ---- A city's place sheet ----
  // A tap on a city opens its sheet, as a maps app opens a place's (user, 11 Nov 2026: "when a place or pin drops the info
  // shows in sheet not like on hover"). It takes the funder's record's panel and host, so it sits in the Details tab: the
  // right column on a desktop, the record sheet at its peek height on a phone. It holds what the city's hover slip held:
  // the city, its country, and its spaces by name, the large ones first, each a button that opens that space's record.
  const SIZE_RANK = { XL: 0, L: 1, M: 2, S: 3, XS: 4 };
  function fillPlace(c) {
    const p = panel;
    const close = h('button', { type: 'button', class: 'hq-close', 'aria-label': 'Close this place' });
    close.innerHTML = '<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"/></svg>';
    close.addEventListener('click', () => closeRecord(true));
    const title = h('div', { class: 'hq-head' }, h('div', null, h('p', { class: 'hq-kind', text: 'City' }), h('h2', { id: 'hqPanelTitle', class: 'dossier-main-heading', text: c.name })), close);
    const ask = h('button', { type: 'button', class: 'record-action', text: 'Ask in chat' });
    ask.addEventListener('click', () => {
      const fn = window.atlasAskInChat || window.atlasAskCurator;
      if (typeof fn === 'function') fn(`What should I know about the spaces in ${c.name}?`);
    });
    const n = c.spaces.length;
    const info = row('hqInfoT', c.country || 'Place', `${n} ${n === 1 ? 'space' : 'spaces'} on the atlas`, null);
    const head = h('div', { class: 'record-head head-sheet rule-b hq-sheet' }, title,
      h('div', { class: 'head-grid' }, h('div', { class: 'head-side record-actions record-action-row' }, ask), h('div', { class: 'head-main' }, h('div', { class: 'prose-part d-rows', role: 'region', 'aria-label': 'Info' }, info))));
    const rows = h('div', { class: 'prose-part d-rows', role: 'region', 'aria-label': 'Spaces' });
    if (n) rows.append(row('hqConnSpaces', 'Spaces', '', listOf(c.spaces, inst => {
      const b = h('button', { type: 'button', class: 'hq-link' }, h('span', { class: 'hq-l', text: inst.shortName || inst.name }), h('span', { class: 'hq-s', text: [inst.neighborhood, inst.category].filter(Boolean).join(' · ') }));
      b.addEventListener('click', () => { if (typeof window.selectInstitution === 'function') window.selectInstitution(inst, false); });
      return h('li', null, b);
    }, LIST_SHOWN)));
    p.replaceChildren(head, rows);
    p.scrollTop = 0;
  }
  window.atlasPlaceOpen = function (cityName) {
    if (!cityName || cityName === 'all') return;
    const g = n => { try { return (0, eval)(n); } catch (_) { return undefined; } };
    const cities = g('ALL_CITIES_REGISTRY') || [], all = g('ALL_INSTITUTIONS') || [];
    const same = (a, b) => String(a || '').trim().toLowerCase() === String(b || '').trim().toLowerCase();
    const meta = cities.find(c => same(c.name, cityName)) || { name: cityName };
    const spaces = all.filter(i => same(i.city, meta.name)).map((inst, k) => ({ inst, k }))
      .sort((a, b) => ((SIZE_RANK[a.inst.size] ?? 5) - (SIZE_RANK[b.inst.size] ?? 5)) || (a.k - b.k)).map(o => o.inst);
    const p = ensurePanel(); if (!p) return;
    closeChooser(false);
    openFrom = null;
    openFor = { place: meta.name };
    if (hq()) hq().select(null);
    let lon = Number(meta.lon), lat = Number(meta.lat);
    if (!isFinite(lon) || !isFinite(lat)) { const s0 = spaces.find(i => isFinite(Number(i.lon)) && isFinite(Number(i.lat))); if (s0) { lon = Number(s0.lon); lat = Number(s0.lat); } }
    window.atlasPlacePin = isFinite(lon) && isFinite(lat) ? { name: meta.name, lon, lat } : null;
    if (window.atlasDropPinRefresh) window.atlasDropPinRefresh();
    fillPlace({ name: meta.name, country: meta.country ? String(meta.country).trim() : '', spaces });
    p.hidden = false;
    showDetails(p.parentElement);
  };
  window.atlasPlaceIsOpen = () => !!(openFor && openFor.place);

  // Choosing a space (on the map, in the chat, or from a connection in this record) puts that space's record in the tab.
  window.atlasHqClose = () => closeRecord(false);
  // A click on a funding line (assets/layers.js) opens the line's funder here, with or without a mapped office.
  window.atlasHqOpen = e => openRecord(e, null);
  // Escape closes the list first, then the record, and does not also clear the space or city the page has selected.
  document.addEventListener('keydown', ev => {
    if (ev.key !== 'Escape') return;
    if (chooser) { ev.stopPropagation(); closeChooser(true); return; }
    if (panel && !panel.hidden && (panel.contains(document.activeElement) || document.activeElement === document.body || (marksBox && marksBox.contains(document.activeElement)))) {
      ev.stopPropagation(); closeRecord(true);
    }
  }, true);
})();
