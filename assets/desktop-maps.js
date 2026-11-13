// Desktop layout after a maps app (user, 4 Nov 2026: "make the desktop version of atlas now function like google map,
// keep features"). The globe fills the window left of the Details and Chat panel, which sits at the right edge and
// stays open ("just move this to the right and keep it open"). A search box floats at the top left: it finds spaces
// and cities as you type and flies to them, and anything else goes to the curator as a question. The layers sit as
// chips beside it and as a square Layers tile at the bottom left. Zoom, your location and the world view are buttons
// at the bottom right. Gossip mode and Dark are pills at the top of the panel. Only windows 768px and wider are
// touched; the phone keeps assets/phone-maps.js. The look is in assets/atlas.css, "DESKTOP: MAPS APP".
(function () {
  'use strict';
  const DESK = () => window.innerWidth >= 768;
  const root = document.documentElement;
  const $ = (id) => document.getElementById(id);
  // The globe's state lives in top-level lets of the page's script, which are not window properties.
  const g = (name) => { try { return (0, eval)(name); } catch (_) { return undefined; } };
  const svg = (body, sw) => '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="' + (sw || 1.8) + '" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' + body + '</svg>';
  const ICON = {
    lens: '<circle cx="10.5" cy="10.5" r="6.5"/><path d="M15.5 15.5 21 21"/>',
    close: '<path d="M6 6l12 12M18 6 6 18"/>',
    pin: '<path d="M12 21s-6.5-6.2-6.5-11a6.5 6.5 0 0 1 13 0c0 4.8-6.5 11-6.5 11z"/><circle cx="12" cy="10" r="2.3"/>',
    city: '<path d="M4 20V9l5-3v14M9 20V4l6 3v13M15 20v-9l5 2v7M3 20h18"/>',
    ask: '<path d="M4 5h16v11H9l-5 4z"/><path d="M10 9.2a2 2 0 1 1 2.6 1.9c-.5.2-.6.5-.6 1M12 13.6v.1"/>',
    plus: '<path d="M12 5v14M5 12h14"/>',
    minus: '<path d="M5 12h14"/>',
    globe: '<circle cx="12" cy="12" r="8.5"/><path d="M3.5 12h17M12 3.5c2.6 2.6 2.6 14.4 0 17M12 3.5c-2.6 2.6-2.6 14.4 0 17"/>',
    layers: '<path d="M12 3 2.5 8.5 12 14l9.5-5.5z"/><path d="m4.6 12.3-2.1 1.2L12 19l9.5-5.5-2.1-1.2"/>',
  };

  function ready(fn) {
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', fn);
    else fn();
  }

  ready(function () {
    const app = $('mainAppContainer');
    const panel = $('workViewContainer');
    const dossierCol = $('desktopDossierColumn');
    const topBar = document.querySelector('body > header:not(#mobileTopBar)');
    if (!app || !panel) return;
    if (topBar && !topBar.id) topBar.id = 'gmdTopBar';

    // ---- Desktop or not ------------------------------------------------------------------------------------------
    let wasDesk = null;
    function syncDesk() {
      const d = DESK();
      if (d === wasDesk) return;
      wasDesk = d;
      root.classList.toggle('gmd', d);
      // The globe sizes itself to its box, which has just changed: let it measure again.
      setTimeout(() => window.dispatchEvent(new Event('resize')), 0);
    }
    window.addEventListener('resize', syncDesk);

    // ---- The side panel: always open on the right; the search box follows the record it shows ------------------------
    const detailsShown = () => !!dossierCol && dossierCol.style.display !== 'none' && !dossierCol.classList.contains('hidden');
    if (dossierCol) new MutationObserver(() => syncSearch()).observe(dossierCol, { attributes: true, attributeFilter: ['style', 'class'] });
    // A new record shows its name in the box, as a place does.
    const recName = $('desktopDossierRecordBody') || dossierCol;
    if (recName) new MutationObserver(() => syncSearch()).observe(recName, { childList: true });

    // ---- The search box -------------------------------------------------------------------------------------------
    const box = document.createElement('div');
    box.id = 'gmdSearch';
    box.setAttribute('role', 'search');
    box.innerHTML =
      '<input id="gmdInput" type="text" autocomplete="off" spellcheck="false" role="combobox" aria-autocomplete="list" aria-expanded="false" aria-controls="gmdResults" placeholder="Search the atlas" aria-label="Search spaces and cities, or ask the curator">' +
      '<button type="button" id="gmdGo" class="gmd-ico-btn" aria-label="Search">' + svg(ICON.lens) + '</button>' +
      '<button type="button" id="gmdClear" class="gmd-ico-btn" aria-label="Clear the search" hidden>' + svg(ICON.close) + '</button>' +
      '<ul id="gmdResults" role="listbox" aria-label="Results" hidden></ul>';
    document.body.appendChild(box);
    const input = $('gmdInput'), results = $('gmdResults'), clearBtn = $('gmdClear');

    // The box shows the open record's name, as a maps app shows the place. Its cross clears the box; the record stays.
    let typed = false, dismissed = null;
    function syncSearch() {
      const inst = g('selectedInstitution');
      const onRecord = inst && inst !== dismissed && detailsShown();
      if (!typed && document.activeElement !== input) input.value = onRecord ? (inst.name || '') : '';
      clearBtn.hidden = !input.value;
    }

    // Searching: spaces by name, alias, city or country; cities by name. A question goes to the curator.
    const norm = (s) => String(s || '').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '');
    let index = null;
    function buildIndex() {
      if (index) return index;
      const insts = g('ALL_INSTITUTIONS') || [];
      const cities = g('ALL_CITIES_REGISTRY') || [];
      index = {
        insts: insts.filter((i) => i && i.name).map((i) => ({ i, n: norm(i.name), a: norm([].concat(i.aliases || []).join(' | ')), p: norm([i.city, i.country].join(' ')) })),
        cities: cities.filter((c) => c && c.name && typeof c.lat === 'number').map((c) => ({ c, n: norm(c.name) })),
      };
      return index;
    }
    function find(q) {
      const n = norm(q).trim();
      if (!n) return [];
      const ix = buildIndex();
      const out = [];
      ix.cities.forEach((x) => {
        const s = x.n === n ? 0 : x.n.startsWith(n) ? 1 : -1;
        if (s >= 0) out.push({ kind: 'city', s, x: x.c, label: x.c.name, sub: [x.c.country, x.c.count ? x.c.count + (x.c.count === 1 ? ' space' : ' spaces') : ''].filter(Boolean).join(' · ') });
      });
      ix.insts.forEach((x) => {
        let s = -1;
        if (x.n === n) s = 0;
        else if (x.n.startsWith(n)) s = 1;
        else if (x.n.includes(' ' + n) || x.a.includes(n)) s = 2;
        else if (x.n.includes(n)) s = 3;
        else if (n.length > 2 && x.p.includes(n)) s = 4;
        if (s >= 0) out.push({ kind: 'space', s: s + 0.5, x: x.i, label: x.i.name, sub: [x.i.city, x.i.country].filter(Boolean).join(', ') });
      });
      out.sort((a, b) => a.s - b.s || a.label.localeCompare(b.label));
      return out.slice(0, 7);
    }
    let items = [], active = -1;
    function render() {
      const q = input.value.trim();
      items = q ? find(q) : [];
      if (q) items.push({ kind: 'ask', label: q, sub: 'Ask the curator' });
      active = q && items.length > 1 ? 0 : -1;
      results.innerHTML = '';
      items.forEach((it, k) => {
        const li = document.createElement('li');
        li.id = 'gmdOpt' + k;
        li.setAttribute('role', 'option');
        li.className = 'gmd-opt is-' + it.kind;
        li.innerHTML = '<span class="gmd-opt-ico">' + svg(it.kind === 'city' ? ICON.city : it.kind === 'space' ? ICON.pin : ICON.ask) + '</span><span class="gmd-opt-text"><span class="gmd-opt-label"></span><span class="gmd-opt-sub"></span></span>';
        li.querySelector('.gmd-opt-label').textContent = it.label;
        li.querySelector('.gmd-opt-sub').textContent = it.sub;
        li.addEventListener('mousedown', (e) => e.preventDefault());
        li.addEventListener('click', () => choose(it));
        li.addEventListener('mousemove', () => mark(k));
        results.appendChild(li);
      });
      mark(active);
      showResults(items.length > 0);
    }
    function mark(k) {
      active = k;
      [...results.children].forEach((li, j) => li.setAttribute('aria-selected', String(j === k)));
      if (k >= 0) input.setAttribute('aria-activedescendant', 'gmdOpt' + k); else input.removeAttribute('aria-activedescendant');
    }
    function showResults(on) {
      results.hidden = !on;
      input.setAttribute('aria-expanded', String(on));
      box.classList.toggle('has-results', on);
    }
    function choose(it) {
      showResults(false);
      typed = false;
      if (it.kind === 'space') {
        input.value = it.x.name;
        input.blur();
        const sel = g('selectInstitution');
        if (typeof sel === 'function') sel(it.x, true);
      } else if (it.kind === 'city') {
        input.value = it.x.name;
        input.blur();
        const fly = g('flyTo'), cityR = g('getCityTargetRadius');
        let r = null;
        try { r = typeof cityR === 'function' ? cityR(it.x.name) : null; } catch (_) { r = null; }
        if (typeof fly === 'function') fly(it.x.lon, it.x.lat, r);
      } else {
        ask(it.label);
      }
    }
    // A question goes into the chat's own box and is sent with its own button, so it is answered as one typed there.
    function ask(q) {
      const sw = window.setWorkspaceTab || g('setWorkspaceTab');
      if (typeof sw === 'function') sw('chat');
      input.value = '';
      input.blur();
      const w = $('workInput'), send = $('workSendBtn');
      if (!w) return;
      w.value = q;
      w.dispatchEvent(new Event('input', { bubbles: true }));
      setTimeout(() => { if (send && !send.disabled) send.click(); else w.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true })); }, 30);
    }

    input.addEventListener('focus', render);
    input.addEventListener('input', () => { typed = true; clearBtn.hidden = false; render(); });
    input.addEventListener('blur', () => setTimeout(() => { showResults(false); typed = !!input.value && typed; syncSearch(); }, 120));
    input.addEventListener('keydown', (e) => {
      if (e.key === 'ArrowDown' && items.length) { e.preventDefault(); mark((active + 1) % items.length); }
      else if (e.key === 'ArrowUp' && items.length) { e.preventDefault(); mark((active - 1 + items.length) % items.length); }
      else if (e.key === 'Enter') {
        e.preventDefault();
        if (active >= 0 && items[active]) choose(items[active]);
        else if (input.value.trim()) ask(input.value.trim());
      } else if (e.key === 'Escape') { showResults(false); input.blur(); }
    });
    $('gmdGo').addEventListener('click', () => {
      if (!input.value.trim()) { input.focus(); return; }
      const hit = find(input.value)[0];
      if (hit && hit.s < 1) choose(hit); else ask(input.value.trim());
    });
    clearBtn.addEventListener('click', () => {
      typed = false;
      dismissed = g('selectedInstitution') || null;
      input.value = '';
      syncSearch();
    });

    // ---- The page's name, under the filter row -----------------------------------------------------------------
    // The header's brand button is hidden in this layout, so its name is set again here; a click does what that button did.
    if (!$('gmdTitle')) {
      const title = document.createElement('h1');
      title.id = 'gmdTitle';
      const tb = document.createElement('button');
      tb.type = 'button';
      tb.textContent = 'Leaving it on the table';
      tb.title = 'Back to the world view';
      tb.addEventListener('click', () => { const b = $('topBrandLogoBtn'); if (b) b.click(); });
      title.appendChild(tb);
      document.body.appendChild(title);
    }

    // ---- The filter row beside the box ---------------------------------------------------------------------------
    // All spaces, then one chip per filter from the Layers menu, one at a time (user, 7 Nov 2026: "make filters above
    // instead of layers, so if clicked it only shows what clicked"). assets/layers.js builds the row and owns the rule, so
    // the chips and the menu's boxes always agree; the funding views stay in the menu, they draw lines and are not filters.
    const chips = document.createElement('div');
    chips.id = 'gmdChips';
    document.body.appendChild(chips);
    const buildChips = () => typeof window.atlasFilterChips === 'function' && window.atlasFilterChips(chips, 'gmd-chip');
    if (!buildChips()) {
      // The filter boxes are built once the page's data is in.
      const t = setInterval(() => { if (buildChips()) clearInterval(t); }, 500);
      setTimeout(() => clearInterval(t), 20000);
    }

    // ---- Layers: a square tile at the bottom left ----------------------------------------------------------------
    const layersBtn = $('layersBtn');
    if (layersBtn && !layersBtn.querySelector('.gmd-layers-icon')) {
      const icon = document.createElement('span');
      icon.className = 'gmd-layers-icon';
      icon.setAttribute('aria-hidden', 'true');
      icon.innerHTML = svg(ICON.layers);
      layersBtn.insertBefore(icon, layersBtn.firstChild);
    }

    // ---- Map buttons at the bottom right: your location, zoom in, zoom out, the world ------------------------------
    // Zoom uses the page's own + and - keys, so the globe and the street map each zoom their own way.
    const ctl = document.createElement('div');
    ctl.id = 'gmdMapCtl';
    const zoomKey = (key) => window.dispatchEvent(new KeyboardEvent('keydown', { key, bubbles: true }));
    const mk = (id, label, icon, fn) => {
      const b = document.createElement('button');
      b.type = 'button';
      b.id = id;
      b.setAttribute('aria-label', label);
      b.title = label;
      b.innerHTML = svg(icon, 2);
      b.addEventListener('click', fn);
      return b;
    };
    const zoom = document.createElement('div');
    zoom.className = 'gmd-zoom';
    zoom.appendChild(mk('gmdZoomIn', 'Zoom in', ICON.plus, () => zoomKey('+')));
    zoom.appendChild(mk('gmdZoomOut', 'Zoom out', ICON.minus, () => zoomKey('-')));
    ctl.appendChild(mk('gmdWorld', 'World view', ICON.globe, () => { const b = $('topBrandLogoBtn'); if (b) b.click(); }));
    ctl.appendChild(zoom);
    app.appendChild(ctl);
    // The location button is the phone's (assets/phone-maps.js); here it joins the stack, over the zoom.
    // On a phone it goes back where phone-maps.js put it, so the phone layout keeps it.
    const locate = $('gmLocateBtn');
    const locateHome = locate && locate.parentNode;
    function placeLocate() {
      if (!locate) return;
      if (DESK()) { if (locate.parentNode !== ctl) ctl.insertBefore(locate, ctl.firstChild); }
      else if (locateHome && locate.parentNode !== locateHome) locateHome.appendChild(locate);
    }
    placeLocate();
    window.addEventListener('resize', placeLocate);

    // ---- The index column's list of places (THE SHEET; user, 10 Nov 2026: "Yes, build both") ---------------------
    // The column at the left is the sheet's index. Under the search line, the filters and Layers it lists the places the
    // map is showing: every city with its count at the world view, a country's cities inside a country, a city's spaces
    // (each with a dot in its grade's colour) inside a city. A filter that is on narrows the list as it narrows the map.
    // A click on a city opens it as a click on its name on the map does; a click on a space opens its record.
    const idx = document.createElement('nav');
    idx.id = 'shIndex';
    idx.setAttribute('aria-labelledby', 'shIndexTitle');
    idx.innerHTML = '<h2 id="shIndexTitle" class="sh-index-title title-small"></h2><input id="shIndexFind" type="text" autocomplete="off" spellcheck="false" aria-label="Find in this list"><ul class="sh-index-list"></ul>';
    document.body.appendChild(idx);
    const idxTitle = idx.querySelector('h2'), idxList = idx.querySelector('ul');
    // A line to find a name in the list (user, 10 Nov 2026: "add search here"): the list narrows as you type, Enter opens
    // the first name left, Escape clears. It is emptied when the list changes from cities to a city's spaces or back.
    const idxFind = idx.querySelector('input');
    let idxQuery = '', idxScope = '';
    idxFind.addEventListener('input', () => { idxQuery = idxFind.value; renderIndex(true); });
    idxFind.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') { e.preventDefault(); const first = idxList.querySelector('.sh-index-row:not(.sh-index-back)'); if (first) first.click(); }
      else if (e.key === 'Escape' && idxFind.value) { e.preventDefault(); idxFind.value = ''; idxQuery = ''; renderIndex(true); }
    });
    // (A title block stood over the list, the place in large italic with its counts; the user had it deleted, 10 Nov 2026.
    // The list's band says what it lists and how many.)
    const plural = (n, one, many) => n.toLocaleString('en-GB') + ' ' + (n === 1 ? one : many);
    const low = (v) => String(v || '').toLowerCase().trim();
    let byCity = null;
    function cityIndex() {
      if (byCity) return byCity;
      const insts = g('ALL_INSTITUTIONS') || [];
      if (!insts.length) return null;
      byCity = new Map();
      insts.forEach((i) => { if (!i || !i.name) return; const k = low(i.city); if (!byCity.has(k)) byCity.set(k, []); byCity.get(k).push(i); });
      return byCity;
    }
    const idxRow = (name, right, tier, current, fn) => {
      const li = document.createElement('li');
      const b = document.createElement('button');
      b.type = 'button';
      b.className = 'sh-index-row';
      if (tier) { b.dataset.tier = tier; const d = document.createElement('i'); d.className = 'sh-index-dot'; d.setAttribute('aria-hidden', 'true'); b.appendChild(d); }
      const n = document.createElement('span'); n.className = 'sh-index-name'; n.textContent = name; b.appendChild(n);
      if (right !== '') { const c = document.createElement('span'); c.className = 'sh-index-count'; c.textContent = right; b.appendChild(c); }
      if (current) b.setAttribute('aria-current', 'true');
      b.addEventListener('click', fn);
      li.appendChild(b);
      return li;
    };
    let idxKey = '';
    function renderIndex(force) {
      if (!DESK()) return;
      // The colour key and the filters set where the list starts and stops; both are measured here, not observed, so the
      // list is placed even while the window is in the background.
      const key = $('mapColourKey'), chipsEl = $('gmdChips');
      if (key) root.style.setProperty('--sh-key-h', key.offsetHeight + 'px');
      if (chipsEl && chipsEl.offsetHeight) root.style.setProperty('--sh-chips-h', chipsEl.offsetHeight + 'px');
      const map = cityIndex();
      if (!map) return;
      const country = g('selectedCountryFilter'), city = g('selectedCityFilter'), sel = g('selectedInstitution');
      const filter = typeof window.atlasSpaceFilter === 'function' ? window.atlasSpaceFilter() : null;
      const keep = typeof window.atlasLayerKeep === 'function' ? window.atlasLayerKeep() : null;
      const grade = typeof window.atlasGradeFilter === 'function' ? window.atlasGradeFilter() : null;
      const scope = country + '|' + city;
      if (scope !== idxScope) { idxScope = scope; idxQuery = ''; idxFind.value = ''; }
      const k = [country, city, sel && sel.name, filter, grade, keep ? 1 : 0, typeof window.atlasLayerKeep, idxQuery].join('|');
      if (!force && k === idxKey) return;
      idxKey = k;
      const q = norm(idxQuery).trim();
      const hit = (name) => !q || norm(name).includes(q);
      const back = () => { const li = idxRow('‹ World', '', '', false, () => { const b = $('backToWorldBtn'); if (b) b.click(); }); li.firstChild.classList.add('sh-index-back'); return li; };
      const frag = document.createDocumentFragment();
      const inCity = city && city !== 'all', inCountry = !inCity && country && country !== 'all';
      if (inCity) {
        const all = (map.get(low(city)) || []).filter((i) => !keep || keep(i)).sort((a, b) => a.name.localeCompare(b.name));
        const list = all.filter((i) => hit(i.name));
        idxFind.placeholder = 'Find a space';
        idxTitle.textContent = city + ', ' + plural(all.length, 'space', 'spaces');
        if (!q) frag.appendChild(back());
        list.forEach((i) => frag.appendChild(idxRow(i.name, '', i.tier === 'A' || i.tier === 'B' ? i.tier : 'U', !!sel && sel.name === i.name, () => {
          const pick = g('selectInstitution'); if (typeof pick === 'function') pick(i, false);
        })));
      } else {
        const match = g('matchC');
        const same = (a, b) => typeof match === 'function' ? match(a, b) : low(a) === low(b);
        const cities = (g('ALL_CITIES_REGISTRY') || []).filter((c) => c && c.name && (!inCountry || same(c.country, country)));
        const rows = cities.map((c) => { const all = map.get(low(c.name)) || []; return { c, n: keep ? all.filter(keep).length : (all.length || c.count || 0) }; })
          .filter((x) => x.n > 0).sort((a, b) => b.n - a.n || a.c.name.localeCompare(b.c.name));
        idxTitle.textContent = (inCountry ? country + ', ' : '') + plural(rows.length, 'city', 'cities');
        idxFind.placeholder = 'Find a city';
        if (inCountry && !q) frag.appendChild(back());
        rows.filter((x) => hit(x.c.name)).forEach((x) => frag.appendChild(idxRow(x.c.name, String(x.n), '', false, () => {
          const open = g('filterByCity'); if (typeof open === 'function') open(x.c.name, true, true);
        })));
      }
      idxList.replaceChildren(frag);
      const cur = !q && idxList.querySelector('[aria-current="true"]');
      if (cur && cur.scrollIntoView) cur.scrollIntoView({ block: 'nearest' });
      else idxList.scrollTop = 0;
    }
    document.addEventListener('atlas:filter', () => renderIndex(true));
    window.addEventListener('resize', () => renderIndex(false));
    // The map's state (country, city, the open space) lives in the page's script and has no event: look twice a second.
    setInterval(() => renderIndex(false), 500);
    renderIndex(true);

    // ---- The latest reports, in the index column (THE SHEET; user, 10 Nov 2026: "pull articles on the left as
    // well, no need bottom button") ---------------------------------------------------------------------------------------
    // The reports the foot bar's strip used to name one at a time are listed under the places, every one of them, newest
    // first, in a list that scrolls (user, 10 Nov 2026: "reports also need to be able to scroll"): each its headline on up
    // to two lines and, indented, how long ago and its space. A report opens the reports panel at it; the line under the
    // list opens them all. The list comes from assets/phone-maps.js (window.atlasReports), which also keeps the panel.
    const rep = document.createElement('nav');
    rep.id = 'shReports';
    rep.setAttribute('aria-labelledby', 'shReportsTitle');
    rep.innerHTML = '<h2 id="shReportsTitle" class="sh-reports-title title-small">Latest reports</h2><ul class="sh-reports-list"></ul><div class="sh-reports-foot"></div>';
    document.body.appendChild(rep);
    const repList = rep.querySelector('ul'), repFoot = rep.querySelector('.sh-reports-foot');
    const openReport = (key) => { if (typeof window.atlasOpenTopStory === 'function') window.atlasOpenTopStory(key); };
    let repKey = '';
    function renderReports() {
      const all = Array.isArray(window.atlasReports) ? window.atlasReports : [];
      rep.hidden = !all.length;
      const k = all.map((x) => x.key).join('|');
      if (k === repKey) return;
      repKey = k;
      const frag = document.createDocumentFragment();
      all.forEach((x) => {
        const li = document.createElement('li');
        const b = document.createElement('button');
        b.type = 'button';
        b.className = 'sh-report' + (x.alert ? ' is-alert' : '');
        b.title = x.head;
        const h = document.createElement('span'); h.className = 'sh-report-head'; h.textContent = x.head; b.appendChild(h);
        const m = document.createElement('span'); m.className = 'sh-report-meta'; m.textContent = [x.when, x.space].filter(Boolean).join(', '); b.appendChild(m);
        b.addEventListener('click', () => openReport(x.key));
        li.appendChild(b);
        frag.appendChild(li);
      });
      repList.replaceChildren(frag);
      repList.scrollTop = 0;
      const allBtn = document.createElement('button');
      allBtn.type = 'button';
      allBtn.className = 'sh-report-all';
      allBtn.textContent = 'All reports, ' + all.length;
      allBtn.addEventListener('click', () => openReport());
      repFoot.replaceChildren(allBtn);
    }
    document.addEventListener('atlas:reports', renderReports);
    renderReports();

    // ---- Closing and opening the index column (user, 13 Nov 2026: "add cross here to close this panel and put open
    // button on top to open it like in claude") ------------------------------------------------------------------------
    // A cross at the column's top right closes it: the search line, the filters, Layers, the places, the reports and the
    // colour key go, and the map takes the width. A sidebar mark at the top left of the head bar opens it again, as
    // Claude's sidebar does. Only where the column exists (1080px and wider); the choice is remembered in this browser.
    const COL_KEY = 'atlas.indexColumnClosed';
    const colBtn = (id, label, icon) => {
      const b = document.createElement('button');
      b.type = 'button';
      b.id = id;
      b.className = 'sh-col-toggle';
      b.setAttribute('aria-label', label);
      b.title = label;
      b.setAttribute('aria-controls', 'shIndex shReports gmdSearch gmdChips');
      b.innerHTML = svg(icon, 1.6);
      document.body.appendChild(b);
      return b;
    };
    const colClose = colBtn('shColClose', 'Close the side panel', ICON.close);
    const colOpen = colBtn('shColOpen', 'Open the side panel', '<rect x="3.5" y="4.5" width="17" height="15" rx="2"/><path d="M9.5 4.5v15"/>');
    function setCol(closed, focus) {
      root.classList.toggle('sh-col-closed', closed);
      colClose.setAttribute('aria-expanded', String(!closed));
      colOpen.setAttribute('aria-expanded', String(!closed));
      try { localStorage.setItem(COL_KEY, closed ? '1' : '0'); } catch (_) {}
      // The globe and the street map size themselves on resize.
      window.dispatchEvent(new Event('resize'));
      if (focus) (closed ? colOpen : colClose).focus();
    }
    colClose.addEventListener('click', () => setCol(true, true));
    colOpen.addEventListener('click', () => setCol(false, true));
    let colStart = false;
    try { colStart = localStorage.getItem(COL_KEY) === '1'; } catch (_) {}
    setCol(colStart, false);

    // ---- What the atlas is, at the map's top right (user, 10 Nov 2026: "use this typesetting but with times to put tagline
    // and explain what atlas does in right corner of the map space") ------------------------------------------------------
    // Set as the "A Chess and Music Evening" poster sets its line-up, flush right: the counts underlined with a small italic
    // "in" between them, the tagline in italic, then each thing the atlas does as a small italic lead-in before a large
    // phrase. The counts are the atlas's own: its spaces, and the cities the list of places shows.
    const tag = document.createElement('div');
    tag.id = 'shTagline';
    tag.setAttribute('role', 'note');
    tag.setAttribute('aria-label', 'About the atlas');
    const fmt = (n) => n.toLocaleString('en-GB');
    const strip = document.createElement('div');
    strip.id = 'shStrip';
    strip.setAttribute('role', 'note');
    strip.setAttribute('aria-label', 'What the atlas does');
    function renderTagline() {
      const insts = g('ALL_INSTITUTIONS') || [];
      const map = cityIndex();
      if (!insts.length || !map) return false;
      const cities = (g('ALL_CITIES_REGISTRY') || []).filter((c) => c && c.name && (map.get(low(c.name)) || []).length).length;
      // The "mesmarize" poster's top right, copied (user, 10 Nov 2026: "need to look like this"): a first line of two
      // underlined phrases with a small joining word and a small figure after them ("Jeudi 2 novembre au Sample 19h-23h");
      // a short paragraph whose first line steps in from the right, ending on an underlined italic credit; a small italic
      // "with"; then three large names, each with a tiny italic tag at its top left ("Live Aja"). The atlas's name is the
      // first line and takes the map back to the world; the credit, the curator, opens the chat; each name is one of the
      // map's filters and turns it on or off. The counts are read from the data.
      tag.innerHTML =
        '<p class="pt-head"><button type="button" class="pt-name" title="Back to the world view"><span class="pt-u">Leaving it</span> <span class="pt-small">on</span> <span class="pt-u">the table</span></button> <span class="pt-time">' + fmt(insts.length) + ' spaces</span></p>' +
        '<p class="pt-para"><span class="pt-l1">An atlas of who pays for culture:</span><span class="pt-l2">every space in ' + fmt(cities) + ' cities graded by its funders,</span>' +
        '<span class="pt-l3">with questions answered by <button type="button" class="pt-credit">the curator.</button></span></p>' +
        '<p class="pt-with">with</p>' +
        '<div class="pt-lineup">' +
        '<p class="pt-row"><button type="button" class="pt-big" data-layer="funding"><i class="pt-tag">filter</i>Funding</button></p>' +
        '<p class="pt-row"><button type="button" class="pt-big" data-layer="epstein"><i class="pt-tag">filter</i>Epstein</button></p>' +
        '<p class="pt-row"><button type="button" class="pt-big" data-layer="propaganda"><i class="pt-tag">filter</i>Propaganda</button></p>' +
        '</div>';
      tag.querySelector('.pt-credit').addEventListener('click', () => { const sw = window.setWorkspaceTab || g('setWorkspaceTab'); if (typeof sw === 'function') sw('chat'); const w = $('workInput'); if (w) w.focus(); });
      const syncNames = () => { const on = typeof window.atlasSpaceFilter === 'function' ? window.atlasSpaceFilter() : null; document.querySelectorAll('#shTagline .pt-big, #shStrip .pt-big').forEach((b) => b.setAttribute('aria-pressed', String(on === b.dataset.layer))); };
      tag.querySelectorAll('.pt-big').forEach((b) => b.addEventListener('click', () => { if (typeof window.atlasSetSpaceFilter === 'function') window.atlasSetSpaceFilter(window.atlasSpaceFilter() === b.dataset.layer ? null : b.dataset.layer); syncNames(); }));
      // The paragraph, "with" and the names run on one line in a band under the map, over the foot bar (user, 11 Nov 2026: "put this below map in one
      // line"); the name and count stay at the top right. placeChips() fits the line to the map's width.
      strip.textContent = '';
      tag.querySelectorAll('.pt-para, .pt-with, .pt-lineup').forEach((el) => strip.appendChild(el));
      if (!syncNames.on) { document.addEventListener('atlas:filter', syncNames); syncNames.on = true; }
      syncNames();
      const vp = $('globeViewport');
      if (vp && tag.parentNode !== vp) vp.appendChild(tag);
      if (strip.parentNode !== document.body) document.body.appendChild(strip);
      return true;
    }
    if (!renderTagline()) { const tt = setInterval(() => { if (renderTagline()) clearInterval(tt); }, 500); setTimeout(() => clearInterval(tt), 20000); }

    // ---- Where the filter pills go (user, 11 Nov 2026: "these can go on top of map section") ------------------------
    // At the map's top left, in the room the block at its top right leaves; when that room is narrower than the widest
    // pill (a narrow window or a wide chat), they go to the map's bottom left instead. sheet.css reads the variables.
    function fitStrip() {
      // One line: the strip's type scales down (never above 15px) until the line fits the room it has.
      if (!strip.getClientRects().length || !strip.clientWidth) return;
      const fs = parseFloat(strip.style.getPropertyValue('--ps-fs')) || 15;
      const next = Math.max(8, Math.min(15, Math.floor(fs * strip.clientWidth / Math.max(1, strip.scrollWidth) * 10) / 10));
      if (Math.abs(next - fs) >= 0.1) strip.style.setProperty('--ps-fs', next + 'px');
    }
    // The question box grows with what is typed, as Claude's does: one line to start, up to two fifths of the window,
    // then it scrolls (user, 11 Nov 2026: "chat need to expand and work like claude chat UI UX"). Enter sends and
    // Shift+Enter starts a new line already (index.html). An inline !important height beats the sheet's layered rules.
    const wi = $('workInput');
    function growInput() {
      if (!wi || !wi.getClientRects().length || !window.matchMedia('(min-width:768px)').matches) return;
      const max = Math.round(window.innerHeight * 0.4);
      wi.style.setProperty('height', '0px', 'important');
      const h = Math.min(wi.scrollHeight, max);
      wi.style.setProperty('height', h + 'px', 'important');
      wi.style.setProperty('overflow-y', wi.scrollHeight > max ? 'auto' : 'hidden', 'important');
    }
    if (wi) {
      wi.addEventListener('input', growInput);
      wi.addEventListener('keydown', (e) => { if (e.key === 'Enter') { setTimeout(growInput, 0); setTimeout(growInput, 120); } });
      const sb = $('workSendBtn');
      if (sb) sb.addEventListener('click', () => { setTimeout(growInput, 0); setTimeout(growInput, 120); });
      window.addEventListener('resize', growInput);
    }
    // The grade filters join the filter pills at the top, after the others, and the colour key goes (user, 11 Nov 2026:
    // "add clean flagged verified filter to the top to other filters and delete color key"). They drive the same grade
    // filter the key's rows did (assets/layers.js atlasSetGradeFilter). Rebuilt if the row is ever redrawn.
    const GRADES = [['A', 'Clean'], ['B', 'Flagged'], ['U', 'Unverified']];
    function gradePills() {
      if (typeof window.atlasSetGradeFilter !== 'function' || !chips.querySelector('button')) return;
      if (!chips.querySelector('button[data-grade]')) {
        GRADES.forEach(([g, name]) => {
          const b = document.createElement('button');
          b.type = 'button';
          b.className = 'gmd-chip sh-grade-chip';
          b.dataset.grade = g;
          b.textContent = name;
          b.title = `Show only ${name.toLowerCase()} spaces; press again to show every space`;
          b.addEventListener('click', () => { window.atlasSetGradeFilter(window.atlasGradeFilter() === g ? null : g); gradePills(); });
          chips.appendChild(b);
        });
      }
      const on = typeof window.atlasGradeFilter === 'function' ? window.atlasGradeFilter() : null;
      chips.querySelectorAll('button[data-grade]').forEach((b) => { const v = String(b.dataset.grade === on); if (b.getAttribute('aria-pressed') !== v) b.setAttribute('aria-pressed', v); });
    }
    function placeChips() {
      gradePills();
      growInput();
      fitStrip();
      const root = document.documentElement, vp = $('globeViewport'), tag = $('shTagline');
      if (!vp || !chips.isConnected || !window.matchMedia('(min-width:1080px)').matches) return;
      const v = vp.getBoundingClientRect();
      if (!v.width) return;
      const pad = parseFloat(getComputedStyle(root).getPropertyValue('--sh-pad')) || 22;
      const t = tag && tag.getClientRects().length ? tag.getBoundingClientRect() : null;
      const widest = Math.max(0, ...[...chips.querySelectorAll('button')].map((b) => b.getBoundingClientRect().width));
      const room = (t ? t.left : v.right) - v.left - 2 * pad;
      const top = room >= widest;
      const set = (k, val) => { if (root.style.getPropertyValue(k) !== val) root.style.setProperty(k, val); };
      set('--sh-chips-l', `${Math.round(v.left + pad)}px`);
      set('--sh-chips-t', top ? `${Math.round(v.top + pad * 0.6)}px` : 'auto');
      set('--sh-chips-b', top ? 'auto' : `${Math.round(window.innerHeight - v.bottom + pad)}px`);
      set('--sh-chips-mw', `${Math.round(top ? room : v.width - 2 * pad - 60)}px`);
    }
    placeChips();
    setInterval(placeChips, 500);
    window.addEventListener('resize', placeChips);

    // ---- Keys: / puts the cursor in the search box, as on a maps site ----------------------------------------------
    window.addEventListener('keydown', (e) => {
      if (!DESK() || e.defaultPrevented) return;
      const t = e.target;
      if (t && (t.tagName === 'INPUT' || t.tagName === 'TEXTAREA' || t.isContentEditable)) return;
      if (e.key === '/' && !e.metaKey && !e.ctrlKey && !e.altKey) { e.preventDefault(); input.focus(); }
    });

    syncDesk();
    syncSearch();
  });
})();
