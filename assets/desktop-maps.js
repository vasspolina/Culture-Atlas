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

    // ---- The Mesma sheet (user, 10 Nov 2026: "design this web like this poster", the "mesmarize" sheet) ------------------
    // The poster's top line runs the width of the sheet: the wordmark, then the date and place in a serif. Here the page's name
    // is the wordmark and the filter chips run after it in the serif, so the two share one row that wraps; its measured height
    // is --sheet-top, which places the map and the panel under it. Down the left margin, as on the sheet, a small swirl, one
    // line of serif turned to read upwards (the page's own description: real text, so a screen reader reads it) and a stepped
    // bracket. The swirl and the bracket are drawings only. The look is in assets/atlas.css, "THE MESMA SHEET".
    const sheetTop = document.createElement('div');
    sheetTop.id = 'gmdSheetTop';
    document.body.appendChild(sheetTop);
    sheetTop.appendChild($('gmdTitle'));
    const measureSheet = () => {
      const h = DESK() ? Math.ceil(sheetTop.getBoundingClientRect().height) : 0;
      if (h) root.style.setProperty('--sheet-top', h + 'px');
    };
    if (window.ResizeObserver) new ResizeObserver(measureSheet).observe(sheetTop);
    window.addEventListener('resize', measureSheet);
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(measureSheet);
    if (!$('gmdSheetMargin')) {
      const margin = document.createElement('div');
      margin.id = 'gmdSheetMargin';
      let blades = '';
      for (let i = 0; i < 9; i++) {
        const a = (i / 9) * Math.PI * 2, pt = (r, t) => (20 + r * Math.cos(a + t)).toFixed(2) + ' ' + (20 + r * Math.sin(a + t)).toFixed(2);
        // One curved blade: out from near the centre, sweeping round, and back on a tighter curve, so it tapers.
        blades += '<path d="M' + pt(4, 0) + 'Q' + pt(15, 0.35) + ' ' + pt(19, 1.25) + 'Q' + pt(12, 0.55) + ' ' + pt(4, 0) + 'Z"/>';
      }
      const desc = (document.querySelector('meta[name="description"]') || {}).content || '';
      const side = desc.replace(/^[^:]*:\s*/, '').replace(/\.$/, '');
      margin.innerHTML = '<svg class="sheet-swirl" viewBox="0 0 40 40" aria-hidden="true" focusable="false"><g fill="currentColor">' + blades + '</g></svg>' +
        (side ? '<p class="sheet-side">' + side.charAt(0).toUpperCase() + side.slice(1) + '</p>' : '') +
        '<svg class="sheet-bracket" viewBox="0 0 14 120" aria-hidden="true" focusable="false"><path d="M12 2H3v22h8v24H3v24h8v24H3v22h9" fill="none" stroke="currentColor" stroke-width="5" stroke-linejoin="miter"/></svg>';
      document.body.appendChild(margin);
    }

    // ---- The filter row beside the box ---------------------------------------------------------------------------
    // All spaces, then one chip per filter from the Layers menu, one at a time (user, 7 Nov 2026: "make filters above
    // instead of layers, so if clicked it only shows what clicked"). assets/layers.js builds the row and owns the rule, so
    // the chips and the menu's boxes always agree; the funding views stay in the menu, they draw lines and are not filters.
    const chips = document.createElement('div');
    chips.id = 'gmdChips';
    sheetTop.appendChild(chips);
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
