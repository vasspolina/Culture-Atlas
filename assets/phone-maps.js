// Phone layout after a maps app (user, 3 Nov 2026: "make the cultural atlas work like the Google app on mobile").
// The globe fills the screen; the search and chat box floats over it at the bottom (user, 3 Nov 2026: "add a chat at the
// bottom not on top") with the suggested questions as a row of chips over it; Layers is a round button at the top right that opens its menu as a sheet; a space's record is a sheet with three heights
// (peek, half, full) that follows the finger and snaps to the nearest one, and a pull down from peek closes it.
// Only phones (under 768px) are touched. The look itself is in assets/atlas.css, "PHONE: MAPS APP".
(function () {
  'use strict';
  const PHONE = () => window.innerWidth < 768;
  const root = document.documentElement;
  const $ = (id) => document.getElementById(id);

  function ready(fn) {
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', fn);
    else fn();
  }

  ready(function () {
    const body = document.body;
    const sheet = $('dossier-bottom-sheet');
    const chatDrawer = $('curator-chat-drawer');
    const detailDrawer = $('detailDrawer');
    const card = $('mobileComposerCard');
    const input = $('chat-input');

    // ---- Which screen the phone is on --------------------------------------------------------------------------
    // gm-map: the map with nothing over it but the floating controls (the chat and the full record page are screens
    // of their own and keep the bar at the top). gm-sheet: a record sheet is up, so the search and chips step aside.
    function syncState() {
      const mode = body.dataset.mobileMode || 'map';
      const onMap = PHONE() && mode !== 'chat' && mode !== 'split'
        && !(chatDrawer && !chatDrawer.classList.contains('hidden'))
        && !(detailDrawer && !detailDrawer.classList.contains('hidden'));
      const changed = root.classList.contains('gm-map') !== onMap;
      root.classList.toggle('gm-map', onMap);
      // The bar at the top comes and goes with this, so the map's height changes: let the globe redraw to fit.
      if (changed) requestAnimationFrame(() => window.dispatchEvent(new Event('resize')));
      root.classList.toggle('gm-sheet', onMap && !!sheet && !sheet.classList.contains('hidden'));
      if (!onMap) closeMenu();
    }
    const watch = new MutationObserver(syncState);
    watch.observe(body, { attributes: true, attributeFilter: ['data-mobile-mode', 'class'] });
    [sheet, chatDrawer, detailDrawer].forEach((el) => el && watch.observe(el, { attributes: true, attributeFilter: ['class'] }));
    window.addEventListener('resize', syncState);

    // ---- Search box: a magnifier at the start, a menu at the end ------------------------------------------------
    let menuBtn = null, menu = null;
    if (card && input) {
      const lens = document.createElement('span');
      lens.className = 'gm-lens';
      lens.setAttribute('aria-hidden', 'true');
      lens.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="10.5" cy="10.5" r="6.5"/><path d="M15.5 15.5 21 21"/></svg>';
      card.insertBefore(lens, card.firstChild);
      // One line, as a maps app's box: the long prompt wrapped to two lines in it. The full prompt is the box's name.
      input.setAttribute('aria-label', input.getAttribute('placeholder') || 'Ask about a space, its funders or controversies');
      input.setAttribute('placeholder', 'Search the atlas');

      // Chat stays one tap away on the map (user, 3 Nov 2026: "keep features like chat"): a button in the box opens
      // the conversation where it was left, or a fresh one when there is none yet. The menu's New chat starts over.
      const chatBtn = document.createElement('button');
      chatBtn.type = 'button';
      chatBtn.id = 'gmChatBtn';
      chatBtn.setAttribute('aria-label', 'Open the chat');
      chatBtn.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round" aria-hidden="true"><path d="M4 5h16v11H9l-5 4z"/></svg><span>Chat</span>';
      chatBtn.addEventListener('click', openChat);
      card.appendChild(chatBtn);

      menuBtn = document.createElement('button');
      menuBtn.type = 'button';
      menuBtn.id = 'gmMenuBtn';
      menuBtn.setAttribute('aria-label', 'Menu');
      menuBtn.setAttribute('aria-haspopup', 'true');
      menuBtn.setAttribute('aria-expanded', 'false');
      menuBtn.setAttribute('aria-controls', 'gmMenu');
      menuBtn.innerHTML = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><circle cx="12" cy="5" r="2"/><circle cx="12" cy="12" r="2"/><circle cx="12" cy="19" r="2"/></svg>';
      card.appendChild(menuBtn);

      menu = document.createElement('div');
      menu.id = 'gmMenu';
      menu.setAttribute('role', 'menu');
      menu.setAttribute('aria-label', 'Menu');
      menu.hidden = true;
      card.parentNode.insertBefore(menu, card.nextSibling);

      // The menu holds the controls the top bar holds on the other screens, and calls the same buttons, so their
      // labels and pressed states are always the bar's own.
      const items = [
        ['mobileGossipBtn'],
        ['mobileThemeBtn'],
        ['mobileStickyShareBtn'],
        ['mobileStickyVoiceBtn', 'Read answers aloud'],
        ['reset-state-btn', 'New chat'],
      ];
      const buildMenu = () => {
        menu.innerHTML = '';
        items.forEach(([id, label]) => {
          const src = $(id);
          if (!src) return;
          const b = document.createElement('button');
          b.type = 'button';
          b.setAttribute('role', 'menuitem');
          b.textContent = label || src.textContent.trim();
          const pressed = src.getAttribute('aria-pressed');
          if (pressed !== null) { b.setAttribute('role', 'menuitemcheckbox'); b.setAttribute('aria-checked', pressed); }
          b.addEventListener('click', () => { closeMenu(true); src.click(); });
          menu.appendChild(b);
        });
      };
      menuBtn.addEventListener('click', () => (menu.hidden ? openMenu() : closeMenu(true)));
      function openMenu() {
        buildMenu();
        menu.hidden = false;
        menuBtn.setAttribute('aria-expanded', 'true');
        const first = menu.querySelector('button');
        if (first) first.focus();
      }
      menu.addEventListener('keydown', (e) => {
        const list = [...menu.querySelectorAll('button')];
        const i = list.indexOf(document.activeElement);
        if (e.key === 'Escape') { e.preventDefault(); closeMenu(true); }
        else if (e.key === 'ArrowDown') { e.preventDefault(); list[(i + 1) % list.length].focus(); }
        else if (e.key === 'ArrowUp') { e.preventDefault(); list[(i - 1 + list.length) % list.length].focus(); }
      });
      document.addEventListener('pointerdown', (e) => {
        if (menu && !menu.hidden && !menu.contains(e.target) && e.target !== menuBtn && !menuBtn.contains(e.target)) closeMenu(false);
      });
    }
    function openChat() {
      closeMenu(false);
      const hasTalk = !!document.querySelector('#curatorMessages > *:not(#curatorHeroGreeting):not(#curatorStarterPrompts)');
      if (!hasTalk && typeof window.resetToNewChat === 'function') window.resetToNewChat();
      chatDrawer && chatDrawer.classList.add('hidden');
      sheet && sheet.classList.add('hidden');
      if (typeof window.setMobileViewMode === 'function') window.setMobileViewMode('chat');
      document.getElementById('tab-chat')?.classList.add('is-on');
      const box = $('workInput');
      if (box) setTimeout(() => { try { box.focus({ preventScroll: true }); } catch (_) { box.focus(); } }, 60);
    }
    window.atlasOpenPhoneChat = openChat;
    function closeMenu(refocus) {
      if (!menu || menu.hidden) return;
      menu.hidden = true;
      menuBtn.setAttribute('aria-expanded', 'false');
      if (refocus) menuBtn.focus();
    }

    // ---- Layers: a round button; the panel is a sheet from the bottom --------------------------------------------
    const layersBtn = $('layersBtn');
    if (layersBtn) {
      layersBtn.setAttribute('aria-label', 'Layers');
      const icon = document.createElement('span');
      icon.className = 'gm-layers-icon';
      icon.setAttribute('aria-hidden', 'true');
      icon.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"><path d="M12 3 2.5 8.5 12 14l9.5-5.5z"/><path d="m4.6 12.3-2.1 1.2L12 19l9.5-5.5-2.1-1.2"/></svg>';
      layersBtn.insertBefore(icon, layersBtn.firstChild);
    }

    // ---- Record sheet: peek, half and full, like a maps app's place sheet -----------------------------------------
    if (sheet) {
      // The actions (Ask in chat, Full record, Money map, Website…) go straight under the name, as a place sheet's
      // row of buttons, so they are in reach at the peek height. The sheet is the phone's only; the desktop is untouched.
      const titleBlock = sheet.querySelector('.sheet-title-block');
      const actions = sheet.querySelector('.record-action-row');
      if (titleBlock && actions) {
        actions.classList.add('gm-actions');
        titleBlock.parentNode.insertBefore(actions, titleBlock.nextSibling);
      }

      buildPlaceCard(sheet, titleBlock, actions);

      const sizeBtn = $('sheet-size-btn');
      const closeBtn = $('close-sheet-btn');
      const chrome = $('sheet-drag-handle');
      const DETENTS = ['peek', 'half', 'full'];
      let detent = 'peek';

      // The height is the custom property --gm-h, not style.height: an older phone rule pins the sheet's height with
      // !important, which an inline height cannot beat (atlas.css, "PHONE: MAPS APP").
      // The heights are measured against the map the sheet sits in, so they hold with the keyboard and on any phone.
      const room = () => (sheet.parentElement ? sheet.parentElement.clientHeight : window.innerHeight);
      function heightOf(d) {
        const h = room();
        if (d === 'full') return h;
        if (d === 'half') return Math.round(h * 0.55);
        // Peek holds the title and the description (user, 3 Nov 2026: "bottom drawer needs to fit title and description"):
        // for a space, its name, grade, place and actions down to the end of its summary; for a funder's record (assets/hq-detail.js),
        // its head block (kind, name, place, source). Never more than 70% of the map, so some map stays in sight, never less than 168px.
        const bottomOf = (el) => (el && el.offsetParent !== null ? el.getBoundingClientRect().bottom - sheet.getBoundingClientRect().top + sheet.scrollTop : 0);
        let end = 0;
        if (sheet.classList.contains('is-hq-sheet')) {
          // A funder's record opens with a head block: its kind, its name, Ask in chat, its place and its source. That is its
          // title and description, so peek ends under it.
          const panel = $('hqPanel');
          const head = panel && (panel.querySelector('.record-head') || panel.querySelector('h2'));
          end = bottomOf(head);
        } else {
          // The description now sits in the title block, above the actions, so the actions' end is the end of both.
          end = bottomOf(actions) || bottomOf(titleBlock);
        }
        end = end ? end + 20 : 168;
        return Math.max(168, Math.min(Math.round(end), Math.round(h * 0.7)));
      }
      function setDetent(d, animate) {
        detent = d;
        sheet.dataset.detent = d;
        sheet.classList.toggle('is-large', d === 'full');
        // gm-still: no animation (the CSS transition is !important, so an inline 'none' would not stop it).
        sheet.classList.toggle('gm-still', animate === false);
        if (animate === false) requestAnimationFrame(() => requestAnimationFrame(() => sheet.classList.remove('gm-still')));
        sheet.style.setProperty('--gm-h', heightOf(d) + 'px');
        if (d !== 'full') sheet.scrollTop = 0;
        if (sizeBtn) {
          sizeBtn.setAttribute('aria-expanded', String(d === 'full'));
          sizeBtn.setAttribute('aria-label', d === 'full' ? 'Shrink space details' : 'Expand space details');
        }
      }
      window.atlasSetSheetDetent = (d) => { if (DETENTS.includes(d)) setDetent(d); };

      // The grabber, tapped or pressed with Enter, steps up a height, and from full goes back to peek.
      sizeBtn?.addEventListener('click', () => setDetent(detent === 'peek' ? 'half' : detent === 'half' ? 'full' : 'peek'));

      // A new record opens at peek, scrolled to its name, so the space stays in sight on the map above it.
      // A funder's record opening in the sheet, or giving way to the space again, starts at peek too.
      let wasHidden = sheet.classList.contains('hidden'), wasHq = sheet.classList.contains('is-hq-sheet');
      new MutationObserver(() => {
        const hidden = sheet.classList.contains('hidden'), hq = sheet.classList.contains('is-hq-sheet');
        if (hidden) { sheet.scrollTop = 0; sheet.style.removeProperty('--gm-h'); }
        else if ((wasHidden || hq !== wasHq) && PHONE()) requestAnimationFrame(() => setDetent('peek', false));
        wasHidden = hidden; wasHq = hq;
      }).observe(sheet, { attributes: true, attributeFilter: ['class'] });
      const name = $('dossier-sheet-name');
      if (name) new MutationObserver(() => {
        sheet.scrollTop = 0;
        if (PHONE() && !sheet.classList.contains('hidden')) requestAnimationFrame(() => setDetent(detent === 'full' ? 'full' : 'peek', false));
      }).observe(name, { childList: true, characterData: true, subtree: true });
      window.addEventListener('resize', () => { if (PHONE() && !sheet.classList.contains('hidden')) setDetent(detent, false); });
      // While at peek, a record that fills in after it opened (a funder's record waits for assets/hq.json) is measured again.
      let remeasure = 0;
      const body = $('dossier-sheet-scrollable-body');
      if (body) new MutationObserver(() => {
        if (!PHONE() || sheet.classList.contains('hidden') || detent !== 'peek') return;
        cancelAnimationFrame(remeasure);
        remeasure = requestAnimationFrame(() => setDetent('peek', false));
      }).observe(body, { childList: true, subtree: true });
      if (document.fonts && document.fonts.ready) document.fonts.ready.then(() => { if (PHONE() && !sheet.classList.contains('hidden') && detent === 'peek') setDetent('peek', false); });

      // Dragging. Below full the whole sheet moves with the finger; at full the record scrolls, and only a pull down
      // from its top moves the sheet. On release it snaps to the nearest height, a flick goes one further, and a pull
      // well below peek closes it.
      let y0 = null, h0 = 0, t0 = 0, lastY = 0, lastT = 0, vel = 0, dragging = false;
      sheet.addEventListener('touchstart', (e) => {
        if (!PHONE() || e.touches.length !== 1) { y0 = null; return; }
        if (e.target.closest('button, a, input, textarea, select, summary, label') && !(chrome && chrome.contains(e.target) && !e.target.closest('#close-sheet-btn'))) { y0 = null; return; }
        y0 = lastY = e.touches[0].clientY; t0 = lastT = Date.now(); h0 = sheet.offsetHeight; vel = 0; dragging = false;
      }, { passive: true });
      sheet.addEventListener('touchmove', (e) => {
        if (y0 === null) return;
        const y = e.touches[0].clientY, d = y - y0, now = Date.now();
        if (!dragging) {
          if (Math.abs(d) < 6) return;
          const inChrome = chrome && chrome.contains(e.target);
          // At full, the record scrolls unless the pull starts from the grabber or from the top of the record going down.
          if (detent === 'full' && !inChrome && (d < 0 || sheet.scrollTop > 0)) { y0 = null; return; }
          dragging = true;
          sheet.classList.add('gm-still');
        }
        if (e.cancelable) e.preventDefault();
        vel = (y - lastY) / Math.max(1, now - lastT);
        lastY = y; lastT = now;
        sheet.style.setProperty('--gm-h', Math.max(64, Math.min(room(), h0 - d)) + 'px');
      }, { passive: false });
      const end = () => {
        if (y0 === null) return;
        y0 = null;
        if (!dragging) return;
        dragging = false;
        sheet.classList.remove('gm-still');
        const h = sheet.offsetHeight;
        const hs = DETENTS.map(heightOf);
        if (h < hs[0] * 0.6 || (vel > 0.9 && detent === 'peek')) { closeBtn?.click(); return; }
        let i;
        if (Math.abs(vel) > 0.6) {
          // A flick goes one height in its direction.
          const cur = DETENTS.indexOf(detent);
          i = Math.max(0, Math.min(2, cur + (vel < 0 ? 1 : -1)));
        } else {
          i = hs.reduce((best, v, k) => (Math.abs(v - h) < Math.abs(hs[best] - h) ? k : best), 0);
        }
        setDetent(DETENTS[i]);
      };
      sheet.addEventListener('touchend', end, { passive: true });
      sheet.addEventListener('touchcancel', end, { passive: true });
    }

    // ---- The record as a maps app's place card (user, 3 Nov 2026: "make it look like Google Maps when it pulls info") ----
    // Under the name, a rating line: the funding grade as its letter in a dot of its colour, where a place card has stars.
    // The actions are pills with icons, the first one filled. Then tabs (Overview, Funding, Record, Sources) with the
    // open one underlined, and on Overview the visiting facts as rows with an icon each: address, hours, admission, website.
    // The record's own blocks are moved into the tabs, never copied, so everything the sheet showed is still in it.
    function buildPlaceCard(sheet, titleBlock, actions) {
      const pane = $('dossier-sheet-verified-pane');
      const name = $('dossier-sheet-name');
      if (!pane || !titleBlock || !name) return;
      const ICON = {
        'dossier-sheet-ask-btn': '<path d="M4 5h16v11H9l-5 4z"/>',
        'dossier-sheet-audit-btn': '<path d="M7 3h7l4 4v14H7z"/><path d="M14 3v4h4M10 12h5M10 16h5"/>',
        'dossier-sheet-plan-btn': '<rect x="4" y="5" width="16" height="15"/><path d="M4 10h16M9 3v4M15 3v4"/>',
        'dossier-sheet-moneymap-btn': '<circle cx="12" cy="12" r="2.5"/><circle cx="5" cy="6" r="2"/><circle cx="19" cy="6" r="2"/><circle cx="12" cy="20" r="2"/><path d="M10.2 10.4 6.5 7.3M13.8 10.4l3.7-3.1M12 14.5V18"/>',
        'dossier-sheet-link-web': '<circle cx="12" cy="12" r="8.5"/><path d="M3.5 12h17M12 3.5c2.6 2.6 2.6 14.4 0 17M12 3.5c-2.6 2.6-2.6 14.4 0 17"/>',
      };
      const svg = (body) => '<svg class="gm-ico" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' + body + '</svg>';
      if (actions) actions.querySelectorAll('.record-action').forEach((a) => {
        if (ICON[a.id] && !a.querySelector('.gm-ico')) a.insertAdjacentHTML('afterbegin', svg(ICON[a.id]));
      });

      // Rating line, between the name and the place.
      const rating = document.createElement('p');
      rating.className = 'gm-rating';
      name.insertAdjacentElement('afterend', rating);

      // Tabs, under the actions.
      const TABS = [['overview', 'Overview'], ['funding', 'Funding'], ['record', 'Record'], ['sources', 'Sources']];
      const tabs = document.createElement('div');
      tabs.className = 'gm-tabs';
      tabs.setAttribute('role', 'tablist');
      tabs.setAttribute('aria-label', 'Space details');
      TABS.forEach(([key, label]) => {
        const b = document.createElement('button');
        b.type = 'button';
        b.setAttribute('role', 'tab');
        b.id = 'gmTab-' + key;
        b.dataset.tab = key;
        b.setAttribute('aria-controls', 'dossier-sheet-verified-pane');
        b.textContent = label;
        // A tab is read at full height, with the tabs at the top and its first lines under them.
        b.addEventListener('click', () => {
          setTab(key);
          if (window.atlasSetSheetDetent && sheet.dataset.detent !== 'full') window.atlasSetSheetDetent('full');
          requestAnimationFrame(() => { sheet.scrollTop = Math.max(0, tabs.offsetTop - 24); });
        });
        tabs.appendChild(b);
      });
      tabs.addEventListener('keydown', (e) => {
        if (e.key !== 'ArrowRight' && e.key !== 'ArrowLeft') return;
        const list = [...tabs.querySelectorAll('button:not([hidden])')];
        const i = list.indexOf(document.activeElement);
        if (i < 0) return;
        e.preventDefault();
        const next = list[(i + (e.key === 'ArrowRight' ? 1 : -1) + list.length) % list.length];
        next.focus(); setTab(next.dataset.tab);
      });
      (actions || titleBlock).insertAdjacentElement('afterend', tabs);
      pane.setAttribute('role', 'tabpanel');

      // Overview's rows of visiting facts, after the summary.
      const info = document.createElement('ul');
      info.className = 'gm-info';
      info.dataset.tab = 'overview';
      pane.prepend(info);

      // The description sits under the name and place, before the actions, as a place card's does: it is the first thing read, at
      // every height. At peek it is cut to three lines (atlas.css); higher up it is whole.
      const summaryEl = $('dossier-sheet-summary');
      if (summaryEl) { summaryEl.classList.add('gm-desc'); titleBlock.appendChild(summaryEl); }
      const blockTab = { 'dossier-sheet-visit': 'visit', 'dossier-sheet-funding': 'funding', 'dossier-sheet-record': 'record', 'dossier-sheet-sources': 'sources' };
      let current = 'overview';
      const filled = (el) => !!el && !el.classList.contains('hidden') && el.textContent.trim().length > 0;
      function setTab(key) {
        current = key;
        tabs.querySelectorAll('button').forEach((b) => {
          const on = b.dataset.tab === key;
          b.setAttribute('aria-selected', String(on));
          b.tabIndex = on ? 0 : -1;
        });
        pane.setAttribute('aria-labelledby', 'gmTab-' + key);
        Object.entries(blockTab).forEach(([id, tab]) => { const el = $(id); if (el) el.toggleAttribute('data-gm-off', tab !== key); });
        info.toggleAttribute('data-gm-off', key !== 'overview');
      }

      const esc = (t) => String(t).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
      const ROW_ICON = {
        place: '<path d="M12 21s-6.5-6.2-6.5-11a6.5 6.5 0 0 1 13 0c0 4.8-6.5 11-6.5 11z"/><circle cx="12" cy="10" r="2.3"/>',
        hours: '<circle cx="12" cy="12" r="8.5"/><path d="M12 7.5V12l3 2"/>',
        ticket: '<path d="M4 7h16v3a2 2 0 0 0 0 4v3H4v-3a2 2 0 0 0 0-4z"/><path d="M14 7v10" stroke-dasharray="1.5 2"/>',
        web: ICON['dossier-sheet-link-web'],
        grade: '<path d="M12 3 4 6v6c0 4.5 3.4 8 8 9 4.6-1 8-4.5 8-9V6z"/>',
      };
      function fill() {
        const inst = (typeof selectedInstitution !== 'undefined' && selectedInstitution) || null;
        if (!inst) return;
        // Rating line.
        let g = null;
        try { g = (typeof GRADE !== 'undefined' && inst.grade && GRADE[inst.grade]) || null; } catch (_) { g = null; }
        let status = '';
        try { status = typeof tierName === 'function' ? tierName(inst) : ''; } catch (_) { status = ''; }
        if (g) {
          rating.innerHTML = '<span class="gm-grade-dot" style="--gm-dot:' + esc(g.col) + '" aria-hidden="true">' + esc(g.letter) + '</span>'
            // One line, as a rating is: the label up to its first clause ("Funders listed; no funders flagged" reads
            // "Funders listed"), and the whole label is the line's title.
            + '<span class="gm-grade-text" title="' + esc(g.label) + '">Grade ' + esc(g.letter) + ' · ' + esc(String(g.label).split(/;|,| or /)[0].trim()) + '</span>';
        } else {
          rating.innerHTML = status ? '<span class="gm-grade-text">' + esc(status) + '</span>' : '';
        }
        rating.hidden = !rating.innerHTML;
        // Visiting rows.
        let web = '';
        try { web = typeof getValidWebUrl === 'function' ? getValidWebUrl(inst) : (inst.website || ''); } catch (_) { web = inst.website || ''; }
        const place = inst.address || [inst.location || inst.city, inst.country].filter(Boolean).join(', ');
        const rows = [
          ['place', place],
          ['hours', inst.opening_hours],
          ['ticket', inst.admission_fee || inst.admission_policy],
          ['web', web ? '<a href="' + esc(web) + '" target="_blank" rel="noopener noreferrer">' + esc(web.replace(/^https?:\/\/(www\.)?/, '').replace(/\/$/, '')) + '</a>' : '', true],
        ].filter((r) => r[1]);
        const rowsHtml = rows.map(([k, v, html]) => '<li>' + svg(ROW_ICON[k]) + '<span>' + (html ? v : esc(v)) + '</span></li>').join('');
        // Only when it differs (against what was last written: the browser serializes it back differently), since writing
        // the rows is a change in the pane, which this function is listening to.
        if (info.dataset.src !== rowsHtml) { info.dataset.src = rowsHtml; info.innerHTML = rowsHtml; }
        // The visit block's facts are Overview's rows now.
        const visit = $('dossier-sheet-visit');
        if (visit && !visit.hasAttribute('data-gm-dup')) visit.setAttribute('data-gm-dup', '');
        // A tab with nothing in it is not offered; the open one falls back to Overview.
        const has = { overview: true, funding: filled($('dossier-sheet-funding')), record: filled($('dossier-sheet-record')), sources: filled($('dossier-sheet-sources')) };
        tabs.querySelectorAll('button').forEach((b) => { b.hidden = !has[b.dataset.tab]; });
        tabs.hidden = Object.values(has).filter(Boolean).length < 2;
        setTab(has[current] ? current : 'overview');
      }
      let queued = false;
      const refill = () => { if (queued) return; queued = true; requestAnimationFrame(() => { queued = false; fill(); }); };
      // A new space opens on Overview.
      new MutationObserver(() => { current = 'overview'; refill(); }).observe(name, { childList: true, characterData: true, subtree: true });
      new MutationObserver(refill).observe(pane, { childList: true, subtree: true, attributes: true, attributeFilter: ['class'] });
      fill();
    }

    // ---- The map's gestures and buttons, as a maps app's (user, 3 Nov 2026: "make it interactive like Google Maps") ----
    // The globe already turns with one finger (with momentum), zooms with two about the point between them, and zooms in
    // on a double click. On a phone this adds: a double tap zooms in where it lands (phones do not all send a double
    // click), a tap with two fingers zooms out, panning the map lowers a half-open record to its peek so the map is free,
    // and a location button flies to where the visitor is and marks it with a dot. The globe's own functions do the
    // work (flyTo, the zoom keys, project); none of them is changed.
    (function mapGestures() {
      const canvas = $('globeCanvas');
      if (!canvas) return;
      const g = (name) => { try { return (0, eval)(name); } catch (_) { return undefined; } };

      // Double tap: zoom in where the second tap lands. A browser that also sends its own double click after it is not
      // let through, or the globe would zoom twice.
      let lastTap = null, synthAt = 0, t1 = null;
      canvas.addEventListener('touchstart', (e) => {
        if (!PHONE()) return;
        if (e.touches.length === 1) t1 = { x: e.touches[0].clientX, y: e.touches[0].clientY, t: Date.now() };
        else t1 = null;
      }, { passive: true });
      canvas.addEventListener('touchend', (e) => {
        if (!PHONE() || !t1 || e.touches.length) return;
        const p = e.changedTouches[0], now = Date.now();
        const tap = Math.hypot(p.clientX - t1.x, p.clientY - t1.y) < 10 && now - t1.t < 250;
        t1 = null;
        if (!tap) { lastTap = null; return; }
        if (lastTap && now - lastTap.t < 320 && Math.hypot(p.clientX - lastTap.x, p.clientY - lastTap.y) < 40) {
          lastTap = null; synthAt = now;
          canvas.dispatchEvent(new MouseEvent('dblclick', { clientX: p.clientX, clientY: p.clientY, bubbles: true, cancelable: true }));
        } else {
          lastTap = { x: p.clientX, y: p.clientY, t: now };
        }
      }, { passive: true });
      canvas.addEventListener('dblclick', (e) => {
        if (e.isTrusted && Date.now() - synthAt < 600) { e.stopImmediatePropagation(); e.preventDefault(); }
      }, true);

      // Two-finger tap: zoom out a step, the same step as the minus key.
      let two = null;
      canvas.addEventListener('touchstart', (e) => {
        if (!PHONE()) return;
        if (e.touches.length === 2) {
          const [a, b] = e.touches;
          two = { t: Date.now(), d: Math.hypot(a.clientX - b.clientX, a.clientY - b.clientY), mx: (a.clientX + b.clientX) / 2, my: (a.clientY + b.clientY) / 2, moved: false };
        } else if (e.touches.length > 2) two = null;
      }, { passive: true });
      canvas.addEventListener('touchmove', (e) => {
        if (!two || e.touches.length !== 2) return;
        const [a, b] = e.touches;
        const d = Math.hypot(a.clientX - b.clientX, a.clientY - b.clientY);
        if (Math.abs(d - two.d) > 12 || Math.hypot((a.clientX + b.clientX) / 2 - two.mx, (a.clientY + b.clientY) / 2 - two.my) > 12) two.moved = true;
      }, { passive: true });
      canvas.addEventListener('touchend', (e) => {
        if (!two || e.touches.length) return;
        const quick = Date.now() - two.t < 300 && !two.moved;
        two = null;
        if (quick) window.dispatchEvent(new KeyboardEvent('keydown', { key: '-', bubbles: true }));
      }, { passive: true });

      // Panning the map with a record half open lowers it to its peek, so the map is free to look at.
      let pan = null;
      canvas.addEventListener('pointerdown', (e) => { pan = PHONE() ? { x: e.clientX, y: e.clientY } : null; });
      window.addEventListener('pointermove', (e) => {
        if (!pan || Math.hypot(e.clientX - pan.x, e.clientY - pan.y) < 12) return;
        pan = null;
        if (sheet && !sheet.classList.contains('hidden') && sheet.dataset.detent === 'half' && window.atlasSetSheetDetent) window.atlasSetSheetDetent('peek');
      });
      window.addEventListener('pointerup', () => { pan = null; });

      // Your location: a round button at the bottom right, over the chips. The first tap asks the browser for the
      // position and flies there at the zoom a city gets; the place is marked with a dot in a ring, which follows the
      // globe as it turns and is hidden on its far side and on the street map.
      if (!('geolocation' in navigator)) return;
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.id = 'gmLocateBtn';
      btn.setAttribute('aria-label', 'Show my location');
      btn.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" aria-hidden="true"><circle cx="12" cy="12" r="6.5"/><circle cx="12" cy="12" r="2.2" fill="currentColor"/><path d="M12 2.5v3M12 18.5v3M2.5 12h3M18.5 12h3"/></svg>';
      const note = document.createElement('p');
      note.id = 'gmLocateNote';
      note.setAttribute('role', 'status');
      note.setAttribute('aria-live', 'polite');
      const viewport = $('globeViewport') || document.body;
      viewport.appendChild(btn);
      viewport.appendChild(note);
      const dot = document.createElement('span');
      dot.id = 'gmHereDot';
      dot.setAttribute('aria-hidden', 'true');
      viewport.appendChild(dot);

      let here = null, noteTimer = 0;
      const say = (t) => { note.textContent = t; note.classList.toggle('is-on', !!t); clearTimeout(noteTimer); if (t) noteTimer = setTimeout(() => say(''), 4000); };
      const nearestCity = (lat, lon) => {
        const list = g('ALL_CITIES_REGISTRY') || [];
        let best = null, bd = Infinity;
        const R = Math.PI / 180;
        list.forEach((c) => {
          if (typeof c.lat !== 'number' || typeof c.lon !== 'number') return;
          const d = Math.acos(Math.min(1, Math.sin(lat * R) * Math.sin(c.lat * R) + Math.cos(lat * R) * Math.cos(c.lat * R) * Math.cos((lon - c.lon) * R)));
          if (d < bd) { bd = d; best = c; }
        });
        return best ? { city: best, km: Math.round(bd * 6371) } : null;
      };
      btn.addEventListener('click', () => {
        btn.setAttribute('aria-busy', 'true');
        say('Finding where you are…');
        navigator.geolocation.getCurrentPosition((pos) => {
          btn.removeAttribute('aria-busy');
          btn.classList.add('is-on');
          here = { lat: pos.coords.latitude, lon: pos.coords.longitude };
          window.atlasHere = here;
          document.dispatchEvent(new CustomEvent('atlas:here'));
          const flyTo = g('flyTo'), cityR = g('getCityTargetRadius');
          const near = nearestCity(here.lat, here.lon);
          let r = null;
          try { r = near && typeof cityR === 'function' ? cityR(near.city.name) : null; } catch (_) { r = null; }
          if (typeof flyTo === 'function') flyTo(here.lon, here.lat, r);
          say(near ? 'You are here. The nearest city on the atlas is ' + near.city.name + (near.km > 5 ? ', ' + near.km + ' km away.' : '.') : 'You are here.');
        }, (err) => {
          btn.removeAttribute('aria-busy');
          say(err && err.code === 1 ? 'Location is turned off for this site. Allow it in the browser to use this.' : 'Your location could not be found.');
        }, { enableHighAccuracy: false, timeout: 12000, maximumAge: 300000 });
      });

      // The dot follows the globe.
      (function follow() {
        requestAnimationFrame(follow);
        if (!here || !PHONE()) { dot.classList.remove('is-on'); return; }
        const project = g('project'), r = g('currentRadius'), w = g('width'), h = g('height');
        if (typeof project !== 'function' || g('isCityStreetViewActive')) { dot.classList.remove('is-on'); return; }
        const p = project(here.lon, here.lat, r, w / 2, h / 2);
        const rect = canvas.getBoundingClientRect(), vr = viewport.getBoundingClientRect();
        dot.classList.toggle('is-on', !!p.front);
        if (p.front) dot.style.transform = 'translate(' + (rect.left - vr.left + p.x) + 'px,' + (rect.top - vr.top + p.y) + 'px)';
      })();
    })();

    // ---- Top story: the latest reports about the spaces, as a news app's feed (user, 3 Nov 2026) ----
    // Built only from what the records hold, never written here: the dated items in gossip_data.gossip (each with its
    // headline, what is said, who says it, where, when, its sources and any reply) and the dated case_notes. The rules of
    // notes/gossip-criteria.md hold: outside Gossip mode the feed shows only what is on record as confirmed or resolved,
    // and the documented cases; in Gossip mode it adds talk and denials, each labelled as what it is, with the reply.
    // Stale items never lead. A strip over the chips shows the newest headline; a tap opens the feed as a sheet.
    (function topStory() {
      const g = (name) => { try { return (0, eval)(name); } catch (_) { return undefined; } };
      const bar = $('mobileStickyInputBar');
      if (!bar) return;
      const esc = (t) => String(t == null ? '' : t).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
      const gossipOn = () => !!window.isGossipModeActive;
      const STATUS = { confirmed: 'Confirmed', resolved: 'Resolved', talk: 'Talk, not confirmed', denied: 'Denied', stale: 'Old talk', documented: 'On record' };
      const KIND = { dispute: 'Dispute', report: 'Report', departure: 'Departure', money: 'Money', allegation: 'Allegation', leak: 'Leak', rumour: 'Rumour', case: 'Case' };
      const WHO = { press: 'Press', court_or_regulator: 'Court or regulator', union: 'Union', open_letter: 'Open letter', campaign: 'Campaign', social_named: 'Named account', social_anonymous: 'Anonymous posts', review_platform: 'Review site' };
      const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
      const parse = (w) => { const m = /^(\d{4})-(\d{2})(?:-(\d{2}))?/.exec(String(w || '')); return m ? { d: new Date(Date.UTC(+m[1], +m[2] - 1, m[3] ? +m[3] : 1)), day: !!m[3] } : null; };
      const dateText = (w) => { const p = parse(w); if (!p) return ''; const d = p.d; return (p.day ? d.getUTCDate() + ' ' : '') + MONTHS[d.getUTCMonth()] + ' ' + d.getUTCFullYear(); };
      const ago = (w) => {
        const p = parse(w); if (!p) return '';
        const days = Math.floor((Date.now() - p.d.getTime()) / 864e5);
        if (!p.day || days > 60) return dateText(w);
        if (days <= 0) return 'today';
        if (days === 1) return 'yesterday';
        if (days < 14) return days + ' days ago';
        return Math.round(days / 7) + ' weeks ago';
      };

      function items() {
        const A = g('ALL_INSTITUTIONS') || [];
        const on = gossipOn(), out = [];
        A.forEach((inst) => {
          ((inst.gossip_data || {}).gossip || []).forEach((it) => {
            if (!it || !it.headline || !parse(it.when)) return;
            const st = it.status || 'talk';
            if (!on && st !== 'confirmed' && st !== 'resolved') return;
            out.push({ inst, when: it.when, head: it.headline, said: it.said, where: it.where, who: WHO[it.who_says] || '', urls: it.urls || [], status: st, kind: KIND[it.kind] || 'Report', reply: it.response || '', outcome: it.outcome || '' });
          });
          (inst.case_notes || []).forEach((c) => {
            if (!c || !c.title || !parse(c.meta)) return;
            const urls = (c.sources || []).map((u) => (typeof u === 'string' ? u : u && u.url)).filter(Boolean);
            let where = '';
            try { where = urls[0] ? new URL(urls[0]).hostname.replace(/^www\./, '') : ''; } catch (_) { where = ''; }
            out.push({ inst, when: c.meta, head: c.title, said: c.text, where, who: '', urls, status: 'documented', kind: 'Case', reply: '', outcome: '' });
          });
        });
        out.sort((a, b) => String(b.when).localeCompare(String(a.when)));
        return out;
      }
      const placeOf = (inst) => [inst.city, inst.country].filter(Boolean).join(', ');
      const shareUrl = (inst) => location.origin + location.pathname + '?inst=' + encodeURIComponent(inst.id || inst.name);

      // The strip on the map.
      const strip = document.createElement('button');
      strip.type = 'button';
      strip.id = 'gmStoryStrip';
      bar.appendChild(strip);
      function paintStrip() {
        const top = items().find((x) => x.status !== 'stale');
        strip.hidden = !top;
        if (!top) return;
        strip.innerHTML = '<span class="gm-strip-label"><i aria-hidden="true"></i>Top story</span><span class="gm-strip-head">' + esc(top.head) + '</span><span class="gm-strip-meta">' + esc(top.inst.name) + ' · ' + esc(ago(top.when)) + '</span>';
        strip.setAttribute('aria-label', 'Top story: ' + top.head + '. ' + top.inst.name + ', ' + ago(top.when) + '. Open the latest reports');
      }

      // The feed.
      const feed = document.createElement('section');
      feed.id = 'gmFeed';
      feed.hidden = true;
      feed.setAttribute('role', 'dialog');
      feed.setAttribute('aria-modal', 'true');
      feed.setAttribute('aria-labelledby', 'gmFeedTitle');
      document.body.appendChild(feed);
      let lastFocus = null;

      const ICO = {
        globe: '<circle cx="12" cy="12" r="8.5"/><path d="M3.5 12h17M12 3.5c2.6 2.6 2.6 14.4 0 17M12 3.5c-2.6 2.6-2.6 14.4 0 17"/>',
        link: '<path d="M10 14a4 4 0 0 0 5.7 0l3-3a4 4 0 0 0-5.7-5.7l-1 1"/><path d="M14 10a4 4 0 0 0-5.7 0l-3 3a4 4 0 0 0 5.7 5.7l1-1"/>',
        reply: '<path d="M4 5h16v11H9l-5 4z"/>',
        share: '<path d="M14 5l6 6-6 6"/><path d="M20 11H11a7 7 0 0 0-7 7"/>',
        pin: '<path d="M12 21s-6.5-6.2-6.5-11a6.5 6.5 0 0 1 13 0c0 4.8-6.5 11-6.5 11z"/><circle cx="12" cy="10" r="2.3"/>',
      };
      const svg = (b) => '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' + b + '</svg>';

      function card(x, i, top) {
        const n = x.urls.length;
        const src = n ? '<a class="gm-stat" href="' + esc(x.urls[0]) + '" target="_blank" rel="noopener noreferrer">' + svg(ICO.link) + n + (n === 1 ? ' source' : ' sources') + '</a>' : '';
        const reply = x.status === 'documented' ? '' : '<span class="gm-stat">' + svg(ICO.reply) + (x.reply && !/^no reply/i.test(x.reply) ? 'Reply on record' : 'No reply found') + '</span>';
        const poster = top ? '<div class="gm-poster" aria-hidden="true"><p class="gm-poster-pill">' + esc(x.kind) + ' · ' + esc(dateText(x.when)) + '</p><p class="gm-poster-name">' + esc(x.inst.name) + '</p><p class="gm-poster-place">' + esc(placeOf(x.inst)) + '</p><p class="gm-poster-status" data-status="' + esc(x.status) + '">' + esc(STATUS[x.status] || '') + '</p></div>' : '';
        return '<article class="gm-story' + (top ? ' is-top' : '') + '" data-i="' + i + '">' + poster
          + '<p class="gm-story-src"><span class="gm-story-mark" aria-hidden="true">' + esc((x.where || x.inst.name).trim().charAt(0).toUpperCase()) + '</span>' + esc(x.where || 'The record') + (x.who && x.who !== 'Press' ? ' · ' + esc(x.who) : '') + '</p>'
          + '<h3 class="gm-story-head"><button type="button" class="gm-open" data-i="' + i + '">' + esc(x.head) + '</button></h3>'
          + '<p class="gm-story-when">' + (x.status === 'documented' ? 'On record' : 'Reported') + ' ' + esc(ago(x.when)) + ' · ' + esc(x.inst.name) + (placeOf(x.inst) ? ', ' + esc(x.inst.city || x.inst.country) : '') + '</p>'
          + (x.said ? '<p class="gm-story-said">' + esc(x.said) + '</p>' : '')
          + (x.reply && x.status !== 'documented' ? '<p class="gm-story-reply"><span>Reply</span> ' + esc(x.reply) + '</p>' : '')
          + (x.outcome ? '<p class="gm-story-reply"><span>Outcome</span> ' + esc(x.outcome) + '</p>' : '')
          + '<div class="gm-story-stats">' + src + reply + '<span class="gm-stat gm-status" data-status="' + esc(x.status) + '">' + esc(STATUS[x.status] || '') + '</span>'
          + '<button type="button" class="gm-share" data-i="' + i + '">' + svg(ICO.share) + 'Share</button></div></article>';
      }

      let list = [];
      function render() {
        list = items();
        const fresh = list.filter((x) => x.status !== 'stale');
        const top = fresh[0];
        const rest = list.filter((x) => x !== top);
        const here = window.atlasHere;
        let near = [];
        if (here) {
          const R = Math.PI / 180;
          const km = (i) => (typeof i.lat === 'number' && typeof i.lon === 'number') ? 6371 * Math.acos(Math.min(1, Math.sin(here.lat * R) * Math.sin(i.lat * R) + Math.cos(here.lat * R) * Math.cos(i.lat * R) * Math.cos((here.lon - i.lon) * R))) : Infinity;
          near = rest.filter((x) => km(x.inst) < 400);
        }
        const world = rest.filter((x) => !near.includes(x)).slice(0, 40);
        const month = list.filter((x) => { const p = parse(x.when); return p && Date.now() - p.d.getTime() < 30 * 864e5; }).length;
        const sec = (title, meta, arr) => arr.length ? '<h2 class="gm-feed-sec">' + svg(title === 'Near you' ? ICO.pin : ICO.globe) + '<span>' + title + '</span><small>' + meta + '</small></h2>' + arr.map((x) => card(x, list.indexOf(x), false)).join('') : '';
        feed.innerHTML = '<div class="gm-feed-grab" aria-hidden="true"></div>'
          + '<header class="gm-feed-head"><h2 id="gmFeedTitle">' + svg(ICO.globe) + '<span>Top story</span></h2><small>' + (month ? month + ' in the past 30 days' : 'Latest') + '</small>'
          + '<button type="button" class="gm-feed-close" aria-label="Close the reports"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M19 5 5 19M5 5l14 14" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg></button></header>'
          + '<p class="gm-feed-note">' + (gossipOn() ? 'Gossip mode: talk and denials are included, each marked for what it is. Talk is what people say, not a finding.' : 'Reports on record as confirmed or resolved, and documented cases. Turn on Gossip mode to include talk.') + '</p>'
          + (top ? card(top, list.indexOf(top), true) : '<p class="gm-feed-note">No dated reports on record yet.</p>')
          + sec('Near you', near.length + (near.length === 1 ? ' report' : ' reports'), near)
          + sec('Worldwide', 'Newest first', world);
      }
      function open() {
        lastFocus = document.activeElement;
        render();
        feed.hidden = false;
        root.classList.add('gm-feed-open');
        feed.scrollTop = 0;
        const c = feed.querySelector('.gm-feed-close'); if (c) c.focus();
      }
      function close(refocus) {
        if (feed.hidden) return;
        feed.hidden = true;
        root.classList.remove('gm-feed-open');
        if (refocus !== false && lastFocus && lastFocus.focus) lastFocus.focus();
      }
      window.atlasOpenTopStory = open;
      strip.addEventListener('click', open);
      // Escape closes the feed wherever the focus is; caught first, so the app's own Escape handling does not take it.
      document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && !feed.hidden) { e.preventDefault(); e.stopPropagation(); close(); }
      }, true);
      feed.addEventListener('keydown', (e) => {
        if (e.key !== 'Tab') return;
        const f = [...feed.querySelectorAll('button, a[href]')].filter((el) => el.offsetParent !== null);
        if (!f.length) return;
        if (e.shiftKey && document.activeElement === f[0]) { e.preventDefault(); f[f.length - 1].focus(); }
        else if (!e.shiftKey && document.activeElement === f[f.length - 1]) { e.preventDefault(); f[0].focus(); }
      });
      feed.addEventListener('click', (e) => {
        if (e.target.closest('.gm-feed-close')) { close(); return; }
        const sh = e.target.closest('.gm-share');
        if (sh) {
          const x = list[+sh.dataset.i]; if (!x) return;
          const url = shareUrl(x.inst), title = x.head;
          if (navigator.share) navigator.share({ title, text: x.inst.name + ': ' + title, url }).catch(() => {});
          else if (navigator.clipboard) navigator.clipboard.writeText(url).then(() => { sh.lastChild.textContent = 'Link copied'; setTimeout(() => { sh.lastChild.textContent = 'Share'; }, 2000); }).catch(() => {});
          return;
        }
        if (e.target.closest('a')) return;
        const art = e.target.closest('.gm-story');
        if (!art) return;
        const x = list[+art.dataset.i]; if (!x) return;
        close(false);
        if (typeof window.selectInstitution === 'function') window.selectInstitution(x.inst, false);
        const fly = g('flyTo');
        if (typeof fly === 'function' && typeof x.inst.lon === 'number') fly(x.inst.lon, x.inst.lat);
      });
      // Pull the feed down from its top to close it.
      let y0 = null;
      feed.addEventListener('touchstart', (e) => { y0 = (feed.scrollTop <= 0 && e.touches.length === 1) ? e.touches[0].clientY : null; }, { passive: true });
      feed.addEventListener('touchmove', (e) => {
        if (y0 === null) return;
        const d = e.touches[0].clientY - y0;
        if (d < 0) { y0 = null; feed.style.transform = ''; return; }
        if (e.cancelable) e.preventDefault();
        feed.style.transform = 'translateY(' + d + 'px)';
      }, { passive: false });
      feed.addEventListener('touchend', (e) => {
        if (y0 === null) return;
        const d = e.changedTouches[0].clientY - y0; y0 = null;
        feed.style.transform = '';
        if (d > 110) close();
      }, { passive: true });

      // Gossip mode and a known location change what is shown.
      const gb = $('mobileGossipBtn');
      if (gb) new MutationObserver(() => { paintStrip(); if (!feed.hidden) render(); }).observe(gb, { attributes: true, attributeFilter: ['aria-pressed'] });
      document.addEventListener('atlas:here', () => { if (!feed.hidden) render(); });
      // The feed is a phone screen; on a wider window it closes.
      window.addEventListener('resize', () => { if (!PHONE()) close(false); });
      paintStrip();

      // The bottom stack's height, for the buttons that sit over it.
      if (window.ResizeObserver) new ResizeObserver(() => root.style.setProperty('--gm-stack-h', bar.offsetHeight + 'px')).observe(bar);
    })();

    syncState();
  });
})();
