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
      // gm-chat: the phone's chat, set as a sheet over the map like the record (user, 4 Nov 2026: "make chat part of the app,
      // same as the map"). The map stays drawn behind it.
      const onChat = PHONE() && mode === 'chat' && !(detailDrawer && !detailDrawer.classList.contains('hidden'));
      const changed = root.classList.contains('gm-map') !== onMap || root.classList.contains('gm-chat') !== onChat;
      root.classList.toggle('gm-chat', onChat);
      root.classList.toggle('gm-map', onMap);
      // The bar at the top comes and goes with this, so the map's height changes: let the globe redraw to fit.
      if (changed) requestAnimationFrame(() => window.dispatchEvent(new Event('resize')));
      root.classList.toggle('gm-sheet', onMap && !!sheet && !sheet.classList.contains('hidden'));
      if (!onMap && !onChat) closeMenu();
    }
    const watch = new MutationObserver(syncState);
    watch.observe(body, { attributes: true, attributeFilter: ['data-mobile-mode', 'class'] });
    [sheet, chatDrawer, detailDrawer].forEach((el) => el && watch.observe(el, { attributes: true, attributeFilter: ['class'] }));
    window.addEventListener('resize', syncState);

    // ---- Search box: a magnifier at the start, a menu at the end ------------------------------------------------
    let menuBtn = null, menu = null, anchorBtn = null;
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
      // The menu is the page's own, not the search box's: the map's box and the chat's header both open it.
      document.body.appendChild(menu);

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
      menuBtn.addEventListener('click', () => (menu.hidden ? openMenu(menuBtn) : closeMenu(true)));
      window.atlasToggleMenu = (anchor) => (menu.hidden ? openMenu(anchor) : closeMenu(true));
      function openMenu(anchor) {
        buildMenu();
        anchorBtn = anchor || menuBtn;
        // Under the button when it is in the top half of the screen, over it when in the bottom half.
        const r = anchorBtn.getBoundingClientRect();
        menu.style.right = Math.max(12, window.innerWidth - r.right) + 'px';
        if (r.top > window.innerHeight / 2) { menu.style.top = 'auto'; menu.style.bottom = (window.innerHeight - r.top + 6) + 'px'; }
        else { menu.style.bottom = 'auto'; menu.style.top = (r.bottom + 6) + 'px'; }
        menu.hidden = false;
        anchorBtn.setAttribute('aria-expanded', 'true');
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
        if (menu && !menu.hidden && !menu.contains(e.target) && !(anchorBtn && anchorBtn.contains(e.target))) closeMenu(false);
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
      const a = anchorBtn || menuBtn;
      a.setAttribute('aria-expanded', 'false');
      if (refocus) a.focus();
    }

    // ---- The chat's header, as the record sheet's: a title, the same menu, and one cross ----------------------------
    const chatHead = $('phoneChatHead');
    if (chatHead) {
      const title = chatHead.querySelector('.flex-1');
      if (title) { title.classList.add('gm-chat-title'); title.textContent = 'Chat'; }
      const b = document.createElement('button');
      b.type = 'button';
      b.id = 'gmChatMenuBtn';
      b.setAttribute('aria-label', 'Menu');
      b.setAttribute('aria-haspopup', 'true');
      b.setAttribute('aria-expanded', 'false');
      b.setAttribute('aria-controls', 'gmMenu');
      b.innerHTML = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><circle cx="12" cy="5" r="2"/><circle cx="12" cy="12" r="2"/><circle cx="12" cy="19" r="2"/></svg>';
      b.addEventListener('click', () => { if (window.atlasToggleMenu) window.atlasToggleMenu(b); });
      const close = $('phoneChatCloseBtn');
      chatHead.insertBefore(b, close || null);
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
      // The sheet's cross is the only one: on a funder's record (assets/hq-detail.js) it closes that record too.
      closeBtn?.addEventListener('click', () => { if (sheet.classList.contains('is-hq-sheet') && typeof window.atlasHqClose === 'function') window.atlasHqClose(); });
      const chrome = $('sheet-drag-handle');
      const DETENTS = ['peek', 'half', 'full'];
      let detent = 'peek';

      // The height is the custom property --gm-h, not style.height: an older phone rule pins the sheet's height with
      // !important, which an inline height cannot beat (atlas.css, "PHONE: MAPS APP").
      // The heights are measured against the map the sheet sits in, so they hold with the keyboard and on any phone.
      const room = () => (sheet.parentElement ? sheet.parentElement.clientHeight : window.innerHeight);
      const safeBottom = (() => {
        let v = null;
        return () => {
          if (v !== null) return v;
          const probe = document.createElement('div');
          probe.style.cssText = 'position:fixed;left:0;bottom:0;width:1px;height:env(safe-area-inset-bottom,0px);visibility:hidden;pointer-events:none';
          document.body.appendChild(probe); v = probe.offsetHeight || 0; probe.remove();
          return v;
        };
      })();
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
        // The iPhone's home strip covers the page's bottom edge (the page runs under it, viewport-fit=cover), so peek leaves
        // room for it, or the actions sat under it (user, 4 Nov 2026: text overlapped at the bottom when a space was opened).
        end = end ? end + 20 + safeBottom() : 168;
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
      // The full record lives in the sheet's tabs (user, 3 Nov 2026: the sheet and the separate Full record page showed the
      // same things twice). recordHtml is the page's own record, the one the Full record page and the desktop's Details show;
      // its sections are sorted into the tabs, and the sheet's shorter blocks that say the same give way to it.
      const full = document.createElement('div');
      full.id = 'gmFull';
      pane.appendChild(full);
      const tabOf = (el) => {
        if (el.matches('figure')) return 'overview';
        const t = ((el.querySelector('.d-row-title') || {}).textContent || '').trim().toLowerCase();
        if (/^(overview|what it publishes|bottom line)\b/.test(t)) return 'overview';
        if (/^(funding|scale and money)\b/.test(t)) return 'funding';
        if (/^sources\b/.test(t)) return 'sources';
        // A flag about money (fossil fuels, opioids, arms, tobacco and the rest) is about who funds the space; a protest,
        // a case or a personal account is part of its record.
        if (el.classList.contains('is-flag') && !/protest|boycott|case|account|gossip|talk|report/.test(t)) return 'funding';
        return 'record';
      };
      function buildFull(inst) {
        const key = (inst.id || inst.name) + '|' + (window.isGossipModeActive ? 1 : 0) + '|' + (window.dossierVcIndex || 0);
        if (full.dataset.key === key) return full.childElementCount > 0;
        full.dataset.key = key;
        let html = '';
        try {
          html = typeof recordHtml === 'function' ? recordHtml(inst) : '';
          if (html && typeof linkRecordSpaces === 'function') html = linkRecordSpaces(html, inst);
        } catch (_) { html = ''; }
        full.innerHTML = html;
        full.querySelectorAll('.record-head').forEach((e) => e.remove());
        // The same record also sits in the page's Full record copy; its ids are dropped here so none is on the page twice.
        full.querySelectorAll('[id]').forEach((e) => e.removeAttribute('id'));
        const secs = [...full.querySelectorAll('section.d-row, figure.standalone-quote')];
        const conts = new Set();
        secs.forEach((sec) => {
          sec.dataset.tab = tabOf(sec);
          // A section named as its tab is (Overview, Funding, Sources) does not say its name again under the tab.
          const t = ((sec.querySelector('.d-row-title') || {}).textContent || '').trim().toLowerCase();
          if (t && t === sec.dataset.tab) sec.classList.add('gm-same-as-tab');
          for (let p = sec.parentElement; p && p !== full; p = p.parentElement) conts.add(p);
        });
        // Anything else in the record that is not a section (a card, a note) belongs to Record.
        [full, ...conts].forEach((c) => [...c.children].forEach((ch) => { if (!conts.has(ch) && !ch.dataset.tab) ch.dataset.tab = 'record'; }));
        return full.childElementCount > 0;
      }

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
        full.querySelectorAll('[data-tab]').forEach((el) => el.toggleAttribute('data-gm-off', el.dataset.tab !== key));
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
        // The full record in the tabs; when it is there, the sheet's own shorter blocks would say the same again, so they go.
        const hasFull = PHONE() && buildFull(inst);
        ['dossier-sheet-funding', 'dossier-sheet-record', 'dossier-sheet-sources'].forEach((id) => {
          const el = $(id); if (el && el.hasAttribute('data-gm-dup') !== hasFull) el.toggleAttribute('data-gm-dup', hasFull);
        });
        const inFull = (t) => !!full.querySelector('[data-tab="' + t + '"]');
        // A tab with nothing in it is not offered; the open one falls back to Overview.
        const has = hasFull
          ? { overview: true, funding: inFull('funding'), record: inFull('record'), sources: inFull('sources') }
          : { overview: true, funding: filled($('dossier-sheet-funding')), record: filled($('dossier-sheet-record')), sources: filled($('dossier-sheet-sources')) };
        tabs.querySelectorAll('button').forEach((b) => { b.hidden = !has[b.dataset.tab]; });
        tabs.hidden = Object.values(has).filter(Boolean).length < 2;
        setTab(has[current] ? current : 'overview');
      }
      let queued = false;
      const refill = () => { if (queued) return; queued = true; requestAnimationFrame(() => { queued = false; fill(); }); };
      // A new space opens on Overview.
      new MutationObserver(() => { current = 'overview'; refill(); }).observe(name, { childList: true, characterData: true, subtree: true });
      new MutationObserver(refill).observe(pane, { childList: true, subtree: true, attributes: true, attributeFilter: ['class'] });
      // Gossip mode changes what the record says, so the tabs are filled again.
      const gb = $('mobileGossipBtn');
      if (gb) new MutationObserver(refill).observe(gb, { attributes: true, attributeFilter: ['aria-pressed'] });
      window.atlasRefillSheet = () => { full.dataset.key = ''; refill(); };
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

    // ---- Top story, alerts and the minute-by-minute check (user, 3 Nov 2026) ----
    // "Add the top story UI features like last reports on culture spaces", "add alerts about a scandal or protest at the museum
    // at the moment", "gossip mode needs super recent info, updated up to the minute", "make sure the info is not made up".
    //
    // Nothing here is written: every item is a record's own dated gossip item (gossip_data.gossip, under notes/gossip-criteria.md)
    // or dated case note, and one is shown only if it can be traced: a headline, a date, at least one web address, and for gossip
    // who says it, where, and the day the editor last opened its addresses. tools/build_live_feed.py writes the same items, with
    // the same test, to assets/live.json on every deploy; this page checks assets/live-stamp.json every minute while it is open
    // and, when the stamp changes, loads the new items without a reload. So the page is as current as the records, never ahead
    // of them: a report reaches it once the editor has checked it and it is deployed.
    //
    // The rules of notes/gossip-criteria.md hold: outside Gossip mode only what is confirmed or resolved, and documented cases;
    // in Gossip mode talk and denials too, each labelled, with the reply. Every card says what kind of source it rests on, and
    // says outright when that source is user-generated (anonymous posts, reviews).
    (function topStory() {
      const g = (name) => { try { return (0, eval)(name); } catch (_) { return undefined; } };
      const bar = $('mobileStickyInputBar');
      if (!bar) return;
      const esc = (t) => String(t == null ? '' : t).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
      const gossipOn = () => !!window.isGossipModeActive;
      const store = { get(k) { try { return localStorage.getItem(k); } catch (_) { return null; } }, set(k, v) { try { localStorage.setItem(k, v); } catch (_) {} } };
      const STATUS = { confirmed: 'Confirmed', resolved: 'Resolved', talk: 'Talk, not confirmed', denied: 'Denied', stale: 'Old talk', documented: 'On record', user: 'User post, not verified' };
      const KIND = { dispute: 'Dispute', report: 'Report', departure: 'Departure', money: 'Money', allegation: 'Allegation', leak: 'Leak', rumour: 'Rumour', case: 'Case', account: 'Staff or visitor post' };
      // What the item rests on, said outright. The two user-generated kinds say so.
      const SOURCE = {
        press: ['Press report, named outlet', false], court_or_regulator: ['Court or regulator record', false], union: ['Union statement', false],
        open_letter: ['Open letter, named signatories', false], campaign: ['Named campaign', false], social_named: ['Post by a named person', false],
        social_anonymous: ['Anonymous posts online', true], review_platform: ['Reviews posted by users', true], case: ['Documented case', false],
        // Not every item is the press: posts by staff and visitors, and leaked documents, are on the record too.
        user_post: ['Staff or visitor post', true], leak: ['Leaked document', false],
      };
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
      const since = (t) => { const s = Math.round((Date.now() - t) / 1000); return s < 10 ? 'just now' : s < 60 ? s + ' s ago' : Math.round(s / 60) + ' min ago'; };
      const http = (u) => typeof u === 'string' && /^https?:\/\//.test(u.trim());

      // The items, from the records the page loaded, or from assets/live.json once a newer one has been deployed.
      let live = null;
      const recordOf = (() => { let map = null; return (id) => { if (!map) { map = new Map(); (g('ALL_INSTITUTIONS') || []).forEach((i) => { map.set(i.id || i.name, i); map.set(i.name, i); }); } return map.get(id); }; })();
      function allItems() {
        const out = [];
        if (live) {
          live.items.forEach((x) => {
            const inst = recordOf(x.inst) || { id: x.inst, name: x.name, city: x.city, country: x.country, lat: x.lat, lon: x.lon };
            out.push({ key: x.type + ':' + (x.id || x.headline) + (x.type === 'leak' || x.type === 'account' ? ':' + x.inst + ':' + String(x.said).length : ''), inst, type: x.type, when: x.when, head: x.headline, said: x.said, where: x.where, who: x.type === 'case' ? 'case' : x.who_says, urls: (x.urls || []).filter(http), status: x.status, kind: x.kind, reply: x.response, outcome: x.outcome, checked: x.checked, role: x.role || '', dated: x.dated || '' });
          });
        } else {
          (g('ALL_INSTITUTIONS') || []).forEach((inst) => {
            ((inst.gossip_data || {}).gossip || []).forEach((it) => {
              const urls = (it && it.urls || []).filter(http);
              // The same test as tools/build_live_feed.py: nothing without a date, an address, a named source and a check date.
              if (!it || !it.headline || !parse(it.when) || !urls.length || !it.who_says || !it.where || !/^\d{4}-\d{2}-\d{2}$/.test(it.retrieved_on || '')) return;
              out.push({ key: 'gossip:' + (it.id || it.headline), inst, type: 'gossip', when: it.when, head: it.headline, said: it.said, where: it.where, who: it.who_says, urls, status: it.status || 'talk', kind: it.kind || 'report', reply: it.response || '', outcome: it.outcome || '', checked: it.retrieved_on });
            });
            // Staff and visitor posts, read as the record reads them (accountView), with the date from the post's own fields.
            ((inst.gossip_data || {}).accounts || []).forEach((a) => {
              const urls = (a && a.sources || []).map((u) => (typeof u === 'string' ? u : u && u.url)).filter(http);
              const F = {}; (a && a.fields || []).forEach((f) => { F[f[0]] = f[1]; });
              const part = (v, k) => String(v || '').split(/\s*·\s*/)[k] || '';
              const date = F['Original post date'] || (F['Subreddit / post date'] ? part(F['Subreddit / post date'], 1) : '') || part(F['Posted · self-described role'], 0) || part(F['Posting date and claimed role'], 0);
              let v = null; try { v = typeof accountView === 'function' ? accountView(a, inst) : null; } catch (_) { v = null; }
              if (!v || !v.summary || !/^\d{4}-\d{2}(-\d{2})?$/.test(date) || !urls.length) return;
              const first = (v.summary.match(/^.+?[.!?](?=\s|$)/) || [v.summary])[0];
              const head = first.length > 160 ? first.slice(0, 157).replace(/\s+\S*$/, '') + '…' : first;
              const [where, role] = v.title.split(' · ');
              out.push({ key: 'account:' + (a.id || head) + ':' + (inst.id || inst.name) + ':' + v.summary.length, inst, type: 'account', when: date, head, said: v.summary, where: where.replace(/ review$/, ''), who: 'user_post', urls, status: 'user', kind: 'account', reply: '', outcome: '', checked: '', role: role || '' });
            });
            // Leaked documents on the record.
            (inst.wikileaks_records || []).forEach((w) => {
              const urls = (w && w.sources || []).filter(http);
              const months = String(w && w.date || '').match(/\d{4}-\d{2}/g);
              if (!w || !months || !w.what_shows || !urls.length) return;
              out.push({ key: 'leak:' + (w.doc_id || '') + ':' + (inst.id || inst.name) + ':' + w.what_shows.length, inst, type: 'leak', when: months[months.length - 1], head: w.doc_id || 'Leaked document', said: w.what_shows, where: 'WikiLeaks', who: 'leak', urls, status: 'documented', kind: 'leak', reply: '', outcome: '', checked: '', dated: String(w.date) });
            });
            (inst.case_notes || []).forEach((c, i) => {
              const urls = (c && c.sources || []).map((u) => (typeof u === 'string' ? u : u && u.url)).filter(http);
              if (!c || !c.title || !/^\d{4}-\d{2}-\d{2}$/.test(c.meta || '') || !urls.length) return;
              out.push({ key: 'case:C-' + (inst.id || inst.name) + '-' + i, inst, type: 'case', when: c.meta, head: c.title, said: c.text, where: '', who: 'case', urls, status: 'documented', kind: 'case', reply: '', outcome: '', checked: '' });
            });
          });
        }
        out.forEach((x) => { if (x.type === 'case' && !x.where) { try { x.where = new URL(x.urls[0]).hostname.replace(/^www\./, ''); } catch (_) { x.where = ''; } } });
        out.sort((a, b) => String(b.when).localeCompare(String(a.when)));
        return out;
      }
      // What the visitor may see in the current mode.
      // Posts by staff and visitors are on the record outside Gossip mode too (its Personal accounts), always marked as user posts.
      const shown = (x) => gossipOn() || x.status === 'confirmed' || x.status === 'resolved' || x.status === 'documented' || x.status === 'user';
      function items() { return allItems().filter(shown); }

      // Alerts: a scandal or protest at a space now. Reported in the last 60 days, not resolved or stale, and about a protest,
      // strike, boycott, dispute, allegation, leak, dismissal or the like by its kind or its own words. Outside Gossip mode only
      // confirmed ones. The rule is shown on the page with the alerts.
      const ALERT_DAYS = 60;
      const TOPIC = /protest|strike|boycott|walk-?out|picket|petition|open letter|occupation|sit-in|demonstrat|lawsuit|sued|tribunal|resign|dismiss|fired|sacked|censor|cancel|scandal|harass|layoff|redundanc|union/i;
      function isAlert(x) {
        const p = parse(x.when);
        if (!p || Date.now() - p.d.getTime() > ALERT_DAYS * 864e5) return false;
        if (x.status === 'resolved' || x.status === 'stale') return false;
        // A user post or an old document does not raise an alert outside Gossip mode, and a document never does.
        if (x.type === 'leak' || (x.status === 'user' && !gossipOn())) return false;
        return ['dispute', 'allegation', 'leak'].includes(x.kind) || TOPIC.test(x.head + ' ' + (x.said || ''));
      }
      const placeOf = (inst) => [inst.city, inst.country].filter(Boolean).join(', ');
      const shareUrl = (inst) => location.origin + location.pathname + '?inst=' + encodeURIComponent(inst.id || inst.name);

      // The strip on the map.
      const strip = document.createElement('button');
      strip.type = 'button';
      strip.id = 'gmStoryStrip';
      bar.appendChild(strip);
      function paintStrip(list, alerts) {
        const top = alerts[0] || list.find((x) => x.status !== 'stale');
        strip.hidden = !top;
        if (!top) return;
        strip.classList.toggle('is-alert', !!alerts.length);
        // An alert now is the top story (user, 4 Nov 2026: "make alert to be a top story"): the strip keeps its name, takes the
        // alert's colour and headline, and says the report is an alert, and how many more there are.
        const label = 'Top story';
        const more = alerts.length > 1 ? ' · ' + (alerts.length - 1) + ' more alert' + (alerts.length > 2 ? 's' : '') : '';
        const meta = (alerts.length ? 'Alert · ' : '') + top.inst.name + ' · ' + ago(top.when) + more;
        strip.innerHTML = '<span class="gm-strip-label"><i aria-hidden="true"></i>' + esc(label) + '</span><span class="gm-strip-head">' + esc(top.head) + '</span><span class="gm-strip-meta">' + esc(meta) + '</span>';
        strip.setAttribute('aria-label', label + (alerts.length ? ', an alert now' : '') + ': ' + top.head + '. ' + top.inst.name + ', ' + ago(top.when) + more + '. Open the latest reports');
      }

      // The feed.
      const feed = document.createElement('section');
      feed.id = 'gmFeed';
      feed.hidden = true;
      feed.setAttribute('role', 'dialog');
      feed.setAttribute('aria-modal', 'true');
      feed.setAttribute('aria-labelledby', 'gmFeedTitle');
      document.body.appendChild(feed);
      const toast = document.createElement('p');
      toast.id = 'gmToast';
      toast.setAttribute('role', 'status');
      toast.setAttribute('aria-live', 'polite');
      document.body.appendChild(toast);
      let toastTimer = 0;
      const say = (t) => { toast.textContent = t; toast.classList.toggle('is-on', !!t); clearTimeout(toastTimer); if (t) toastTimer = setTimeout(() => say(''), 6000); };
      let lastFocus = null;

      const ICO = {
        globe: '<circle cx="12" cy="12" r="8.5"/><path d="M3.5 12h17M12 3.5c2.6 2.6 2.6 14.4 0 17M12 3.5c-2.6 2.6-2.6 14.4 0 17"/>',
        alert: '<path d="M12 3 2.5 20h19z"/><path d="M12 10v4.5M12 17.2v.3"/>',
        link: '<path d="M10 14a4 4 0 0 0 5.7 0l3-3a4 4 0 0 0-5.7-5.7l-1 1"/><path d="M14 10a4 4 0 0 0-5.7 0l-3 3a4 4 0 0 0 5.7 5.7l1-1"/>',
        reply: '<path d="M4 5h16v11H9l-5 4z"/>',
        share: '<path d="M14 5l6 6-6 6"/><path d="M20 11H11a7 7 0 0 0-7 7"/>',
        pin: '<path d="M12 21s-6.5-6.2-6.5-11a6.5 6.5 0 0 1 13 0c0 4.8-6.5 11-6.5 11z"/><circle cx="12" cy="10" r="2.3"/>',
        bell: '<path d="M6 16V11a6 6 0 0 1 12 0v5l1.5 2h-15z"/><path d="M10 20.5a2 2 0 0 0 4 0"/>',
      };
      const svg = (b) => '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' + b + '</svg>';

      // A post's headline is its own first sentence, so its text below starts after it and does not say it twice.
      const saidRest = (x) => {
        const said = String(x.said || ''), head = String(x.head || '').replace(/…$/, '');
        if (x.type === 'account' && head && said.startsWith(head)) return said.slice(head.length).replace(/^[\s.;,]+/, '');
        return said;
      };
      const monthsText = (t) => String(t || '').replace(/\d{4}-\d{2}(?:-\d{2})?/g, (m) => dateText(m));
      let list = [];
      function card(x, poster, alert) {
        const i = list.indexOf(x);
        const n = x.urls.length;
        const src = SOURCE[x.who] || ['Source type not recorded', false];
        const links = '<a class="gm-stat" href="' + esc(x.urls[0]) + '" target="_blank" rel="noopener noreferrer">' + svg(ICO.link) + n + (n === 1 ? ' source' : ' sources') + '</a>';
        const reply = x.type !== 'gossip' ? '' : '<span class="gm-stat">' + svg(ICO.reply) + (x.reply && !/^no reply/i.test(x.reply) ? 'Reply on record' : 'No reply found') + '</span>';
        const posterHtml = poster ? '<div class="gm-poster' + (alert ? ' is-alert' : '') + '" aria-hidden="true"><p class="gm-poster-pill">' + esc(alert ? 'Alert · ' : '') + esc(KIND[x.kind] || 'Report') + ' · ' + esc(dateText(x.when)) + '</p><p class="gm-poster-name">' + esc(x.inst.name) + '</p><p class="gm-poster-place">' + esc(placeOf(x.inst)) + '</p><p class="gm-poster-status" data-status="' + esc(x.status) + '">' + esc(STATUS[x.status] || '') + '</p></div>' : '';
        // Where this comes from, in words: the kind of source, whether it is user-generated, who published it and when, and
        // the day the atlas last opened its addresses.
        const prov = '<p class="gm-story-prov' + (src[1] ? ' is-user' : '') + '">' + (src[1] ? '<b>User-generated, not verified</b> · ' : '') + esc(src[0])
          + (x.where ? ' · ' + esc(x.where) : '') + (x.role ? ' · ' + esc(x.role) : '') + (x.type === 'leak' ? ' · dated ' + esc(monthsText(x.dated) || dateText(x.when)) : x.type === 'account' ? ' · posted ' + esc(dateText(x.when)) : ' · published ' + esc(dateText(x.when)))
          + (x.checked ? ' · links checked by the atlas ' + esc(dateText(x.checked)) : '') + '</p>';
        return '<article class="gm-story' + (poster ? ' is-top' : '') + (alert ? ' is-alert' : '') + '" data-i="' + i + '" data-key="' + esc(x.key) + '">' + posterHtml
          + '<p class="gm-story-src"><span class="gm-story-mark" aria-hidden="true">' + esc((x.where || x.inst.name).trim().charAt(0).toUpperCase()) + '</span>' + esc(x.where || 'The record') + (x.role ? ' · ' + esc(x.role) : '') + '</p>'
          + '<h3 class="gm-story-head"><button type="button" class="gm-open" data-i="' + i + '">' + (alert && !poster ? '<span class="gm-alert-tag">Alert</span> ' : '') + esc(x.head) + '</button></h3>'
          + '<p class="gm-story-when">' + ({ case: 'On record', account: 'Posted', leak: 'Dated' }[x.type] || 'Reported') + ' ' + esc(ago(x.when)) + ' · ' + esc(x.inst.name) + (x.inst.city || x.inst.country ? ', ' + esc(x.inst.city || x.inst.country) : '') + '</p>'
          + (saidRest(x) ? '<p class="gm-story-said">' + esc(saidRest(x)) + '</p>' : '')
          + (x.reply && x.type === 'gossip' ? '<p class="gm-story-reply"><span>Reply</span> ' + esc(x.reply) + '</p>' : '')
          + (x.outcome ? '<p class="gm-story-reply"><span>Outcome</span> ' + esc(x.outcome) + '</p>' : '')
          + prov
          + '<div class="gm-story-stats">' + links + reply + '<span class="gm-stat gm-status" data-status="' + esc(x.status) + '">' + esc(STATUS[x.status] || '') + '</span>'
          + '<button type="button" class="gm-share" data-i="' + i + '">' + svg(ICO.share) + 'Share</button></div></article>';
      }

      // Checking for new reports.
      let checkedAt = 0, checkFailed = false, baseline = null, liveDigest = null;
      const notifyOn = () => store.get('atlas-alerts') === 'on' && 'Notification' in window && Notification.permission === 'granted';
      function render() {
        list = items();
        const alerts = list.filter(isAlert);
        const seen = new Set();
        const take = (arr) => arr.filter((x) => !seen.has(x) && seen.add(x));
        const here = window.atlasHere;
        const R = Math.PI / 180;
        const km = (i) => (here && typeof i.lat === 'number' && typeof i.lon === 'number') ? 6371 * Math.acos(Math.min(1, Math.sin(here.lat * R) * Math.sin(i.lat * R) + Math.cos(here.lat * R) * Math.cos(i.lat * R) * Math.cos((here.lon - i.lon) * R))) : Infinity;
        // The top story is the first alert now when there is one, else the newest report; the other alerts follow it.
        const fresh = list.filter((x) => x.status !== 'stale');
        const top = take(alerts.length ? alerts.slice(0, 1) : fresh.slice(0, 1))[0];
        const topIsAlert = !!(top && alerts.includes(top));
        const alertList = take(alerts);
        const near = here ? take(list.filter((x) => km(x.inst) < 400)) : [];
        // Reports and documented cases first; posts by staff and visitors and leaked documents in sections of their own, so
        // the press is not drowned out by visitor comments and every kind of source is told apart at a glance.
        const world = take(list.filter((x) => x.type === 'gossip' || x.type === 'case')).slice(0, 30);
        const posts = take(list.filter((x) => x.type === 'account')).slice(0, 15);
        const docs = take(list.filter((x) => x.type === 'leak')).slice(0, 10);
        const month = list.filter((x) => { const p = parse(x.when); return p && Date.now() - p.d.getTime() < 30 * 864e5; }).length;
        const sec = (title, icon, meta, arr, alert) => arr.length ? '<h2 class="gm-feed-sec' + (alert ? ' is-alert' : '') + '">' + svg(icon) + '<span>' + title + '</span><small>' + meta + '</small></h2>' + arr.map((x) => card(x, false, alert)).join('') : '';
        const bellOn = store.get('atlas-alerts') === 'on';
        feed.innerHTML = '<div class="gm-feed-grab" aria-hidden="true"></div>'
          + '<header class="gm-feed-head"><h2 id="gmFeedTitle">' + svg(ICO.globe) + '<span>Top story</span></h2>'
          + ('Notification' in window ? '<button type="button" class="gm-bell" aria-pressed="' + bellOn + '">' + svg(ICO.bell) + (bellOn ? 'Alerts on' : 'Alert me') + '</button>' : '')
          + '<button type="button" class="gm-feed-close" aria-label="Close the reports"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M19 5 5 19M5 5l14 14" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg></button></header>'
          + '<p class="gm-feed-live"><i aria-hidden="true"></i><span class="gm-feed-checked">' + liveLine() + '</span></p>'
          + '<p class="gm-feed-note">' + (gossipOn()
            ? 'Gossip mode: talk and denials are included, each marked for what it is. Talk is what people say, not a finding. Items from anonymous posts or user reviews say so.'
            : 'Reports on record as confirmed or resolved, and documented cases. Turn on Gossip mode to include talk.')
            + ' Every item comes from the records, with its source and the day its links were last checked; nothing here is written by the atlas.</p>'
          + (topIsAlert ? '<p class="gm-feed-note">An alert is a protest, strike, dispute, allegation or similar reported in the last ' + ALERT_DAYS + ' days and not resolved' + (gossipOn() ? '' : ', and confirmed') + '.</p>' : '')
          + (top ? card(top, true, topIsAlert) : '')
          + sec(topIsAlert ? 'More alerts now' : 'Alerts now', ICO.alert, alertList.length + ' active', alertList, true)
          + sec('Near you', ICO.pin, near.length + (near.length === 1 ? ' report' : ' reports'), near, false)
          + sec(alertList.length || near.length ? 'Latest' : 'Worldwide', ICO.globe, month ? month + ' in the past 30 days' : 'Newest first', world, false)
          + (posts.length ? '<h2 class="gm-feed-sec">' + svg(ICO.reply) + '<span>From staff and visitors</span><small>User posts</small></h2><p class="gm-feed-note">Posts by staff and visitors on review sites and Reddit, quoted as posted. User-generated: one person\u2019s experience each, not checked as fact.</p>' + posts.map((x) => card(x, false, false)).join('') : '')
          + (docs.length ? '<h2 class="gm-feed-sec">' + svg(ICO.link) + '<span>From leaked documents</span><small>' + docs.length + ' on record</small></h2>' + docs.map((x) => card(x, false, false)).join('') : '')
          + (!list.length ? '<p class="gm-feed-note">No dated reports on record yet.</p>' : '');
      }
      function liveLine() {
        if (checkFailed) return 'Could not check for new reports just now. Showing what was loaded.';
        const n = live ? live.newest : (list[0] && list[0].when);
        return (checkedAt ? 'Checked for new reports ' + since(checkedAt) : 'Checking for new reports…') + (n ? ' · newest on record ' + esc(dateText(n)) : '');
      }
      setInterval(() => { const el = feed.querySelector('.gm-feed-checked'); if (el && !feed.hidden) el.innerHTML = liveLine(); }, 5000);

      // Map marks for the alerts: a ring at each space with an alert now, which opens the alert.
      const marks = new Map();
      const viewport = $('globeViewport') || document.body;
      const canvas = $('globeCanvas');
      function paintMarks(alerts) {
        const want = new Map();
        alerts.forEach((x) => { const k = x.inst.id || x.inst.name; if (!want.has(k) && typeof x.inst.lat === 'number') want.set(k, x); });
        marks.forEach((el, k) => { if (!want.has(k)) { el.remove(); marks.delete(k); } });
        want.forEach((x, k) => {
          let el = marks.get(k);
          if (!el) {
            el = document.createElement('button');
            el.type = 'button';
            el.className = 'gm-alert-mark';
            el.innerHTML = '<span aria-hidden="true">!</span>';
            el.addEventListener('click', () => open(el.dataset.key));
            viewport.appendChild(el);
            marks.set(k, el);
          }
          el.dataset.key = x.key;
          el._x = x;
          el.setAttribute('aria-label', 'Alert at ' + x.inst.name + ': ' + x.head);
        });
      }
      (function follow() {
        requestAnimationFrame(follow);
        if (!marks.size) return;
        const project = g('project'), r = g('currentRadius'), w = g('width'), h = g('height');
        const ok = PHONE() && root.classList.contains('gm-map') && typeof project === 'function' && !g('isCityStreetViewActive') && canvas;
        const rect = ok ? canvas.getBoundingClientRect() : null, vr = ok ? viewport.getBoundingClientRect() : null;
        marks.forEach((el) => {
          const x = el._x;
          const p = ok ? project(x.inst.lon, x.inst.lat, r, w / 2, h / 2) : null;
          const on = !!(p && p.front);
          el.classList.toggle('is-on', on);
          el.tabIndex = on ? 0 : -1;
          if (on) el.style.transform = 'translate(' + (rect.left - vr.left + p.x) + 'px,' + (rect.top - vr.top + p.y) + 'px)';
        });
      })();

      function refresh() {
        render();
        const alerts = list.filter(isAlert);
        paintStrip(list, alerts);
        paintMarks(alerts);
        return alerts;
      }
      // New alerts since the visitor last looked: said on the page, and as a notification if they asked for one. The first
      // run only remembers what is there, so opening the page never sets off a burst of old alerts.
      function announce(alerts, quiet) {
        let seenKeys = [];
        try { seenKeys = JSON.parse(store.get('atlas-alerts-seen') || '[]'); } catch (_) { seenKeys = []; }
        const fresh = alerts.filter((x) => !seenKeys.includes(x.key));
        store.set('atlas-alerts-seen', JSON.stringify(alerts.map((x) => x.key).concat(seenKeys).slice(0, 300)));
        if (quiet || !fresh.length) return;
        const x = fresh[0];
        say('New alert: ' + x.inst.name + '. ' + x.head);
        if (notifyOn()) {
          try { new Notification('Alert: ' + x.inst.name, { body: x.head + ' (' + (SOURCE[x.who] || ['Source'])[0] + ', ' + (x.where || 'record') + ')', tag: x.key }); } catch (_) {}
        }
      }

      async function check() {
        if (document.visibilityState === 'hidden') return;
        try {
          const r = await fetch('assets/live-stamp.json?t=' + Date.now(), { cache: 'no-store' });
          if (!r.ok) throw new Error(String(r.status));
          const s = await r.json();
          checkedAt = Date.now(); checkFailed = false;
          // The first stamp is the one the page loaded with; only a later one means new reports.
          if (baseline === null) { baseline = s.digest; liveDigest = s.digest; }
          else if (s.digest !== liveDigest) {
            const lr = await fetch('assets/live.json?t=' + Date.now(), { cache: 'no-store' });
            if (lr.ok) {
              const data = await lr.json();
              if (data && Array.isArray(data.items)) {
                const before = new Set(allItems().map((x) => x.key));
                live = data; liveDigest = s.digest;
                const alerts = refresh();
                const added = items().filter((x) => !before.has(x.key));
                if (added.length) say(added.length === 1 ? 'New report: ' + added[0].inst.name + '. ' + added[0].head : added.length + ' new reports on the record.');
                announce(alerts, false);
                if (!feed.hidden) { const sc = feed.scrollTop; render(); feed.scrollTop = sc; }
                return;
              }
            }
          }
        } catch (_) { checkFailed = true; }
        const el = feed.querySelector('.gm-feed-checked'); if (el) el.innerHTML = liveLine();
      }
      setInterval(check, 60000);
      document.addEventListener('visibilitychange', () => { if (document.visibilityState === 'visible') check(); });

      function open(focusKey) {
        lastFocus = document.activeElement;
        render();
        feed.hidden = false;
        root.classList.add('gm-feed-open');
        feed.scrollTop = 0;
        check();
        const target = focusKey && feed.querySelector('.gm-story[data-key="' + (window.CSS && CSS.escape ? CSS.escape(focusKey) : focusKey) + '"]');
        if (target) { target.scrollIntoView({ block: 'start' }); target.classList.add('is-focus'); const b = target.querySelector('.gm-open'); if (b) b.focus(); }
        else { const c = feed.querySelector('.gm-feed-close'); if (c) c.focus(); }
      }
      function close(refocus) {
        if (feed.hidden) return;
        feed.hidden = true;
        root.classList.remove('gm-feed-open');
        if (refocus !== false && lastFocus && lastFocus.focus) lastFocus.focus();
      }
      window.atlasOpenTopStory = open;
      strip.addEventListener('click', () => open());
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
      feed.addEventListener('click', async (e) => {
        if (e.target.closest('.gm-feed-close')) { close(); return; }
        const bell = e.target.closest('.gm-bell');
        if (bell) {
          if (store.get('atlas-alerts') === 'on') { store.set('atlas-alerts', 'off'); }
          else {
            let perm = Notification.permission;
            if (perm === 'default') { try { perm = await Notification.requestPermission(); } catch (_) { perm = 'denied'; } }
            if (perm === 'granted') { store.set('atlas-alerts', 'on'); say('Alerts on. You will be told of a new alert while the atlas is open.'); }
            else say('Notifications are blocked for this site. Allow them in the browser to get alerts.');
          }
          const on = store.get('atlas-alerts') === 'on';
          bell.setAttribute('aria-pressed', String(on));
          bell.lastChild.textContent = on ? 'Alerts on' : 'Alert me';
          return;
        }
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
        if (typeof window.selectInstitution === 'function' && recordOf(x.inst.id || x.inst.name)) window.selectInstitution(x.inst, false);
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
      if (gb) new MutationObserver(() => { refresh(); }).observe(gb, { attributes: true, attributeFilter: ['aria-pressed'] });
      document.addEventListener('atlas:here', () => { if (!feed.hidden) render(); });
      window.addEventListener('resize', () => { if (!PHONE()) close(false); });
      window.atlasAlerts = () => list.filter(isAlert);
      announce(refresh(), true);
      check();

      // The bottom stack's height, for the buttons that sit over it.
      if (window.ResizeObserver) new ResizeObserver(() => root.style.setProperty('--gm-stack-h', bar.offsetHeight + 'px')).observe(bar);
    })();

    // ---- Suggested questions from where the visitor is (user, 3 Nov 2026: "make prompt suggestions hooked to location") ----
    // The chips over the search box ask about the place in view: the visitor's own city once the location button has found
    // them, otherwise the city the map is looking at when zoomed in, otherwise the city picked on the map. Each question is one
    // the chat answers from the records (who funds a named space, the flagged spaces in a city, the oil and gas money there,
    // and in Gossip mode what is being said). A space with an alert now gets its own chip. Zoomed out, the general chips return.
    (function locationChips() {
      const box = $('mobileSuggestChips');
      const input = $('chat-input');
      const send = $('mobileStickySendBtn');
      if (!box || !input || !send) return;
      const g = (name) => { try { return (0, eval)(name); } catch (_) { return undefined; } };
      const original = [...box.children];
      let shownFor = '';
      const R = Math.PI / 180;
      const dist = (a, b) => 6371 * Math.acos(Math.min(1, Math.sin(a.lat * R) * Math.sin(b.lat * R) + Math.cos(a.lat * R) * Math.cos(b.lat * R) * Math.cos((a.lon - b.lon) * R)));
      function nearestCity(pt, maxKm) {
        let best = null, bd = Infinity;
        (g('ALL_CITIES_REGISTRY') || []).forEach((c) => { if (typeof c.lat !== 'number') return; const d = dist(pt, c); if (d < bd) { bd = d; best = c; } });
        return best && bd <= maxKm ? { city: best, km: bd } : null;
      }
      function placeNow() {
        const here = window.atlasHere;
        if (here) { const n = nearestCity(here, 250); if (n) return { city: n.city, why: 'near you' }; }
        const r = g('currentRadius'), base = g('baseRadius');
        if (typeof r === 'number' && typeof base === 'number' && r > base * 2.2) {
          const n = nearestCity({ lat: g('rotLat'), lon: g('rotLon') }, 300);
          if (n) return { city: n.city, why: 'on the map' };
        }
        const sel = g('selectedCityFilter');
        if (sel && sel !== 'all') { const c = (g('ALL_CITIES_REGISTRY') || []).find((x) => x.name === sel); if (c) return { city: c, why: 'on the map' }; }
        return null;
      }
      const ask = (q) => { input.value = q; input.dispatchEvent(new Event('input', { bubbles: true })); send.click(); };
      function chip(label, q, cls) {
        const b = document.createElement('button');
        b.type = 'button';
        b.className = 'curator-suggest-chip gm-loc-chip' + (cls ? ' ' + cls : '');
        b.textContent = label;
        if (q) { b.dataset.query = q; b.addEventListener('click', () => ask(q)); }
        return b;
      }
      function paint() {
        const p = placeNow();
        const gossip = !!window.isGossipModeActive;
        const key = p ? p.city.name + '|' + p.why + '|' + gossip : 'none|' + gossip;
        if (key === shownFor) return;
        shownFor = key;
        if (!p) { box.replaceChildren(...original); box.setAttribute('aria-label', 'Suggested questions'); return; }
        const C = p.city.name;
        const spaces = (g('ALL_INSTITUTIONS') || []).filter((i) => i.city === C);
        const big = spaces.slice().sort((a, b) => ({ L: 3, M: 2, S: 1 }[b.size] || 0) - ({ L: 3, M: 2, S: 1 }[a.size] || 0) || ((b.gossip_data ? 1 : 0) - (a.gossip_data ? 1 : 0)))[0];
        const alerts = (typeof window.atlasAlerts === 'function' ? window.atlasAlerts() : []).filter((x) => x.inst.city === C);
        const chips = [chip(C + (p.why === 'near you' ? ', near you' : ''), '', 'gm-loc-label')];
        if (alerts[0]) chips.push(chip('What is happening at ' + alerts[0].inst.name + '?', 'What is happening at ' + alerts[0].inst.name + '?', 'is-alert'));
        if (big) chips.push(chip('Who funds ' + big.name + '?', 'Who funds ' + big.name + '?'));
        chips.push(chip('Flagged in ' + C, 'Which spaces in ' + C + ' are flagged, and why?'));
        chips.push(chip('Oil and gas money in ' + C, 'Which spaces in ' + C + ' take oil and gas money?'));
        if (gossip) chips.push(chip('Gossip in ' + C, "What's the gossip at spaces in " + C + '?'));
        box.replaceChildren(...chips);
        box.setAttribute('aria-label', 'Suggested questions about ' + C);
      }
      document.addEventListener('atlas:here', paint);
      const gb = $('mobileGossipBtn');
      if (gb) new MutationObserver(paint).observe(gb, { attributes: true, attributeFilter: ['aria-pressed'] });
      setInterval(() => { if (PHONE() && root.classList.contains('gm-map')) paint(); }, 1500);
      paint();
    })();

    // ---- One record view on the phone: the separate Full record page gives way to the sheet ----
    // Whatever opens the Full record page on a phone (a link in the chat, the Details button, the next critique) opens the
    // record sheet at full height instead, on the same space; the sheet's tabs hold the whole record.
    (function oneRecordView() {
      const drawer = $('detailDrawer');
      const body = $('detailBody');
      if (!drawer || !body) return;
      const g = (name) => { try { return (0, eval)(name); } catch (_) { return undefined; } };
      new MutationObserver(() => {
        if (!PHONE() || drawer.classList.contains('hidden')) return;
        const head = body.querySelector('.dossier-main-heading');
        const nameText = head ? head.textContent.trim() : '';
        const inst = nameText && (g('ALL_INSTITUTIONS') || []).find((i) => i.name === nameText);
        if (!inst) return;   // not a space's record (the Share form, a funder's page): left as it is
        drawer.classList.add('hidden');
        const sel = g('selectedInstitution');
        if (sel !== inst && typeof window.selectInstitution === 'function') window.selectInstitution(inst, false);
        else if (typeof window.atlasRefillSheet === 'function') window.atlasRefillSheet();
        if (sheet && sheet.classList.contains('hidden') && typeof window.atlasOpenPhoneDetails === 'function') window.atlasOpenPhoneDetails();
        requestAnimationFrame(() => { if (window.atlasSetSheetDetent) window.atlasSetSheetDetent('full'); });
      }).observe(drawer, { attributes: true, attributeFilter: ['class'] });
    })();

    syncState();
  });
})();
