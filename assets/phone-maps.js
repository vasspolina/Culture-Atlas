// Phone layout after a maps app (user, 3 Nov 2026: "make the cultural atlas work like the Google app on mobile").
// The globe fills the screen; the search and chat box floats over it at the bottom (user, 3 Nov 2026: "add a chat at the
// bottom not on top") with the suggested questions as a row of chips over it; a row of filters sits at the top, one at a time; Layers is a round button under it at the right that opens its menu as a sheet; a space's record is a sheet with three heights
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
      // One box for asking and finding (user, 4 Nov 2026: "no need for search, combine it with chat, search behaviour"): a
      // speech mark, not a magnifier, since what is typed is mostly a question.
      lens.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"><path d="M4 5h16v11H9l-5 4z"/></svg>';
      card.insertBefore(lens, card.firstChild);
      // One line, as a maps app's box: the long prompt wrapped to two lines in it. The full prompt is the box's name.
      input.setAttribute('aria-label', 'Ask the atlas, or type a space or a city to find it on the map');
      input.setAttribute('placeholder', 'Ask the atlas');

      // Finding: a space's or a city's name on its own goes to the map (the record opens, or the map flies to the city)
      // instead of the chat. It is a find only when it has no question mark, is six words or fewer and names exactly one
      // space (the page's own matcher, or a name that starts with it) or one city; anything else is a question for the chat.
      const fold = (t) => String(t || '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase().replace(/[^a-z0-9]+/g, ' ').trim();
      function findOnMap(q) {
        const raw = String(q || '').trim();
        if (!raw || /\?/.test(raw) || raw.split(/\s+/).length > 6) return null;
        const A = window.ALL_INSTITUTIONS || (typeof ALL_INSTITUTIONS !== 'undefined' ? ALL_INSTITUTIONS : []);
        const f = fold(raw);
        if (f.length < 3) return null;
        const cities = window.ALL_CITIES_REGISTRY || (() => { try { return (0, eval)('ALL_CITIES_REGISTRY'); } catch (_) { return []; } })();
        const city = (cities || []).find((c) => fold(c.name) === f);
        if (city) return { city };
        const names = (i) => [i.name].concat(i.aliases || []).map(fold);
        const exact = A.filter((i) => names(i).includes(f));
        if (exact.length === 1) return { inst: exact[0] };
        // One word on its own finds a space only by its full name or a recorded short name: a word that only starts a name
        // ("tate" for Tate Modern) goes to the chat, which can say what is on the atlas under that word (user, 4 Nov 2026).
        const oneWord = f.split(' ').length === 1;
        if (oneWord) return null;
        const prefix = A.filter((i) => names(i).some((n) => n.startsWith(f + ' ') || n === f));
        if (prefix.length === 1) return { inst: prefix[0] };
        let m = null;
        try { m = window.AtlasNames && window.AtlasNames.findNamedSpace ? window.AtlasNames.findNamedSpace(raw, A) : null; } catch (_) { m = null; }
        // The matcher also finds a name inside a sentence; a find is the name alone, so its words must be most of the query.
        if (m && fold(m.name).split(' ').length >= f.split(' ').length - 1) return { inst: m };
        return null;
      }
      function find(e) {
        if (!PHONE() || !root.classList.contains('gm-map')) return;
        const hit = findOnMap(input.value);
        if (!hit) return;
        e.preventDefault(); e.stopImmediatePropagation();
        input.value = '';
        input.dispatchEvent(new Event('input', { bubbles: true }));
        try { input.blur(); } catch (_) {}
        const g = (n) => { try { return (0, eval)(n); } catch (_) { return undefined; } };
        if (hit.city) { const fc = g('filterByCity'); if (typeof fc === 'function') fc(hit.city.name, true, false); return; }
        if (typeof window.selectInstitution === 'function') window.selectInstitution(hit.inst, false);
        const fly = g('flyTo'), base = g('baseRadius');
        if (typeof fly === 'function' && typeof hit.inst.lon === 'number') fly(hit.inst.lon, hit.inst.lat, typeof base === 'number' ? base * 6 : null);
      }
      // Caught first, before the page's own send, so a find never reaches the chat.
      input.addEventListener('keydown', (e) => { if (e.key === 'Enter' && !e.shiftKey) find(e); }, true);
      const sendBtn = $('mobileStickySendBtn');
      if (sendBtn) sendBtn.addEventListener('click', find, true);
      window.atlasFindOnMap = findOnMap;

      // The box is the chat's: with a conversation under way, a tap on the empty box goes back to it.
      input.addEventListener('focus', () => {
        if (!PHONE() || input.value.trim()) return;
        const hasTalk = !!document.querySelector('#curatorMessages > *:not(#curatorHeroGreeting):not(#curatorStarterPrompts)');
        if (hasTalk) { input.blur(); openChat(); }
      });

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
        // The way back to the whole globe, from a city, a country or the street map. On a phone it was two buttons in the
        // street map's old bar (Exit and World) and the brand button in the top bar; now it is here, once.
        const g = (n) => { try { return (0, eval)(n); } catch (_) { return undefined; } };
        const zoomedIn = g('isCityStreetViewActive') || (g('selectedCityFilter') && g('selectedCityFilter') !== 'all') || (g('selectedCountryFilter') && g('selectedCountryFilter') !== 'all') || (g('currentRadius') > g('baseRadius') * 1.3);
        if (zoomedIn) {
          const w = document.createElement('button');
          w.type = 'button';
          w.setAttribute('role', 'menuitem');
          w.textContent = 'Whole world';
          w.addEventListener('click', () => {
            closeMenu(true);
            const back = $('backToWorldBtn');
            if (g('isCityStreetViewActive') && back) back.click();
            else if (typeof window.resetGlobeView === 'function') window.resetGlobeView();
          });
          menu.insertBefore(w, menu.firstChild);
        }
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
    // The chat's box is one line too, as the map's: its long prompt wrapped to two lines in the pill (user, 7 Nov 2026,
    // the phone's look after the foundry's site). The full prompt stays as the box's name. Only on a phone: the desktop's panel keeps it.
    const work = $('workInput');
    if (work && PHONE()) {
      work.setAttribute('aria-label', work.getAttribute('placeholder') || 'Ask about a space, its funders or controversies');
      work.setAttribute('placeholder', 'Ask about a space or a funder');
    }

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
      // Details is a toggle (user, 6 Nov 2026): it opens the record, and the record's own Details button, pressed, closes it.
      $('phoneChatDetailsBtn')?.setAttribute('aria-pressed', 'false');
    }

    // ---- One of each in the chat (user, 6 Nov 2026: "make chat window not repeating buttons") ----
    // Share information is in the chat's ⋮ menu, so on a phone the composer holds only the box and Send, as the Claude app's
    // does. The keyboard's own close key does what the composer's chevron did, and the chevron sat over the words being typed,
    // so it goes too. On the note screen itself both stay: there Share is the way back out of the form.
    const shareBtn = $('chatShareBtn');
    if (shareBtn) {
      const syncShare = () => {
        const off = PHONE() && !body.classList.contains('chat-input-mode-active');
        [shareBtn, $('workKbCloseBtn')].forEach((el) => {
          if (!el) return;
          if (off) el.style.setProperty('display', 'none', 'important');
          else el.style.removeProperty('display');
        });
      };
      new MutationObserver(syncShare).observe(body, { attributes: true, attributeFilter: ['class'] });
      window.addEventListener('resize', syncShare);
      syncShare();
    }

    // ---- The street map's bar: one back button and the place's name -------------------------------------------------
    // The old bar held Exit, World, the country and the place in a square box; Exit and World both left the street map. On a
    // phone it is a round back button (what Exit did: back to the globe at this place) beside the place's name, and Whole
    // world is in the menu.
    const exitBtn = $('exitStreetViewBtn');
    if (exitBtn) {
      exitBtn.setAttribute('aria-label', 'Back to the globe');
      const ico = document.createElement('span');
      ico.className = 'gm-back-ico';
      ico.setAttribute('aria-hidden', 'true');
      ico.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 5l-7 7 7 7"/></svg>';
      exitBtn.insertBefore(ico, exitBtn.firstChild);
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

    // ---- The filter row at the top of the map --------------------------------------------------------------------
    // All spaces, then one chip per filter from the Layers menu, one at a time (user, 7 Nov 2026: "make filters above
    // instead of layers, so if clicked it only shows what clicked"). assets/layers.js builds the row and owns the rule.
    // The look is in assets/atlas.css under PHONE: MAPS APP (#gmChips); it shows on the map screen only.
    if (!$('gmChips')) {
      const row = document.createElement('div');
      row.id = 'gmChips';
      body.appendChild(row);
      const build = () => typeof window.atlasFilterChips === 'function' && window.atlasFilterChips(row, 'gm-filter-chip');
      if (!build()) {
        const t = setInterval(() => { if (build()) clearInterval(t); }, 500);
        setTimeout(() => clearInterval(t), 20000);
      }
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
        if (root.classList.contains('gm-from-chat')) d = 'full';   // opened from the chat: a page of its own, always full
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
        else if ((wasHidden || hq !== wasHq) && PHONE()) requestAnimationFrame(() => setDetent(root.classList.contains('gm-from-chat') ? 'full' : 'peek', false));
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
        // Opened from the chat, the record is a page of its own at full height: it only scrolls, it is never dragged.
        if (!PHONE() || e.touches.length !== 1 || root.classList.contains('gm-from-chat')) { y0 = null; return; }
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

      // ---- Details from the chat, as the Claude app opens an artifact (user, 6 Nov 2026: "make details button on chat window
      // a toggle", "function more like Claude with details toggle and back button") ----
      // The chat's Details button opens the record as a page of its own: full height, scrolling, never dragged, with a back
      // button to the chat at the top left and the same Details button, pressed, at the top right. Either one goes back to the
      // conversation where it was left, scrolled where it was. The sheet's grabber and cross are put away while it is open, so
      // no control is on screen twice; Ask in chat stays, pressed, and is a third way back (see the toggles below).
      const fromChatBar = document.createElement('div');
      fromChatBar.className = 'gm-from-chat-bar';
      fromChatBar.innerHTML = '<button type="button" id="gmDetailsBackBtn" aria-label="Back to the chat">'
        + '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M15 5l-7 7 7 7"/></svg>'
        + '<span>Chat</span></button>'
        + '<button type="button" id="gmDetailsToggleBtn" aria-pressed="true" aria-label="Space details">Details</button>';
      fromChatBar.hidden = true;
      if (chrome) chrome.appendChild(fromChatBar);
      const putAway = () => [sheet.querySelector('.sheet-grabber'), sizeBtn, closeBtn].filter(Boolean);
      let chatScrollTop = 0;
      function markFromChat() {
        if (!PHONE()) return;
        const sc = $('curatorScrollArea');
        chatScrollTop = sc ? sc.scrollTop : 0;
        root.classList.add('gm-from-chat');
        fromChatBar.hidden = false;
        $('phoneChatDetailsBtn')?.setAttribute('aria-pressed', 'true');
        $('dossier-sheet-ask-btn')?.setAttribute('aria-pressed', 'true');
        // Inline and !important: the sheet's controls are drawn by rules that are themselves !important (atlas.css).
        putAway().forEach((el) => el.style.setProperty('display', 'none', 'important'));
      }
      function clearFromChat() {
        if (!root.classList.contains('gm-from-chat')) return;
        root.classList.remove('gm-from-chat');
        fromChatBar.hidden = true;
        $('phoneChatDetailsBtn')?.setAttribute('aria-pressed', 'false');
        $('dossier-sheet-ask-btn')?.setAttribute('aria-pressed', 'false');
        putAway().forEach((el) => el.style.removeProperty('display'));
      }
      function backToChat() {
        clearFromChat();
        sheet.classList.add('hidden');
        $('tab-dossier')?.classList.remove('is-on');
        if (typeof window.setMobileViewMode === 'function') window.setMobileViewMode('chat');
        $('tab-chat')?.classList.add('is-on');
        // The conversation comes back where it was left, and focus returns to the button that opened the record.
        // The chat is laid out again once it is shown, so the scroll is put back over a few frames.
        const restore = () => { const sc = $('curatorScrollArea'); if (sc) sc.scrollTop = chatScrollTop; };
        requestAnimationFrame(() => requestAnimationFrame(restore));
        setTimeout(() => {
          restore();
          const d = $('phoneChatDetailsBtn');
          if (d && d.offsetParent !== null) { try { d.focus({ preventScroll: true }); } catch (_) { d.focus(); } }
        }, 120);
      }
      window.atlasMarkDetailsFromChat = markFromChat;
      window.atlasDetailsBackToChat = backToChat;
      $('gmDetailsBackBtn')?.addEventListener('click', backToChat);
      $('gmDetailsToggleBtn')?.addEventListener('click', backToChat);
      document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && root.classList.contains('gm-from-chat') && !sheet.classList.contains('hidden')) { e.preventDefault(); backToChat(); }
      });
      // Anything else that closes the record (a link to another screen, the map's own controls) ends the mode too.
      new MutationObserver(() => { if (sheet.classList.contains('hidden')) clearFromChat(); })
        .observe(sheet, { attributes: true, attributeFilter: ['class'] });
      window.addEventListener('resize', () => { if (!PHONE()) clearFromChat(); });

      // ---- The record's actions as toggles (user, 7 Nov 2026: "make buttons toggles") ----
      // Ask in chat is pressed while the record is open over the chat, and pressing it then goes back to the chat. Money map is
      // pressed while the money layers (the funders and their ties) are on, and pressing it then turns them off; off, it opens
      // the money map as before. The record's own click handlers run only when a button is not pressed: this listener sits on
      // the sheet in the capture phase, so it is reached first.
      const askBtn = $('dossier-sheet-ask-btn'), moneyBtn = $('dossier-sheet-moneymap-btn');
      // A layer box holds several keys (the Funding box is money and ties), so the layers' own API says which box is which.
      const api = () => window.atlasLayersAPI || null;
      const layerBox = (k) => { const a = api(); return a && a.boxes ? a.boxes().find((i) => a.keysOfBox(i).includes(k)) : null; };
      const moneyOn = () => { const a = api(); return !!(a && a.L && a.L.money); };
      function syncToggles() {
        if (!PHONE()) return;
        if (moneyBtn) moneyBtn.setAttribute('aria-pressed', String(moneyOn()));
        if (askBtn) askBtn.setAttribute('aria-pressed', String(root.classList.contains('gm-from-chat')));
      }
      sheet.addEventListener('click', (e) => {
        if (!PHONE()) return;
        const t = e.target.closest('button');
        if (!t || t.getAttribute('aria-pressed') !== 'true') return;
        if (t === askBtn) { e.preventDefault(); e.stopPropagation(); backToChat(); }
        if (t === moneyBtn) {
          e.preventDefault(); e.stopPropagation();
          ['money', 'ties'].forEach((k) => { const b = layerBox(k); if (b && b.checked) { b.checked = false; b.dispatchEvent(new Event('change', { bubbles: true })); } });
          syncToggles();
        }
      }, true);
      document.getElementById('layersPanel')?.addEventListener('change', syncToggles);
      new MutationObserver(syncToggles).observe(sheet, { attributes: true, attributeFilter: ['class'] });
      syncToggles();
    }

    // ---- The record as a maps app's place card (user, 3 Nov 2026: "make it look like Google Maps when it pulls info") ----
    // Under the name, a rating line: the funding grade as the words "Grade B" in its colour, where a place card has stars.
    // The actions are pills of words, the first one filled. Then tabs (Overview, Funding, Record, Sources) with the
    // open one underlined, and on Overview the visiting facts as rows: address, hours, admission, website. No icons on the
    // pills or the rows, and no Website pill while the website is one of the rows (user, 7 Nov 2026: "delete slop").
    // The record's own blocks are moved into the tabs, never copied, so everything the sheet showed is still in it.
    function buildPlaceCard(sheet, titleBlock, actions) {
      const pane = $('dossier-sheet-verified-pane');
      const name = $('dossier-sheet-name');
      if (!pane || !titleBlock || !name) return;
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
      function fill() {
        const inst = (typeof selectedInstitution !== 'undefined' && selectedInstitution) || null;
        if (!inst) return;
        // Rating line.
        let g = null;
        try { g = (typeof GRADE !== 'undefined' && inst.grade && GRADE[inst.grade]) || null; } catch (_) { g = null; }
        let status = '';
        try { status = typeof tierName === 'function' ? tierName(inst) : ''; } catch (_) { status = ''; }
        if (g) {
          // The grade as Google Maps writes a place's standing ("Open" in green, "Closed" in red): the words
          // "Grade F" in the grade's colour, a dot, then the label up to its first clause. No letter in a circle
          // (user, 7 Nov 2026: "Don't do F in circles on mobile. Just say grade F"; "make color coding note UI
          // like on Google Maps"). The whole label is the line's title.
          rating.innerHTML = '<span class="gm-grade-text" title="' + esc(g.label) + '">'
            + '<span class="gm-grade-word" data-grade="' + esc(g.letter) + '">Grade ' + esc(g.letter) + '</span>'
            + '<span aria-hidden="true"> \u22c5 </span>'
            + esc(String(g.label).split(/;|,| or /)[0].trim()) + '</span>';
        } else {
          rating.innerHTML = status ? '<span class="gm-grade-text">' + esc(status) + '</span>' : '';
        }
        // The i button on the rating line opens how grades work, this space's grade marked (user, 6 Nov 2026).
        const parts = typeof window.atlasGradeInfoParts === 'function' && rating.innerHTML ? window.atlasGradeInfoParts(inst) : null;
        const oldPanel = rating.nextElementSibling && rating.nextElementSibling.classList.contains('grade-info') ? rating.nextElementSibling : null;
        if (oldPanel) oldPanel.remove();
        if (parts) { rating.insertAdjacentHTML('beforeend', parts.btn); rating.insertAdjacentHTML('afterend', parts.panel); }
        rating.hidden = !rating.innerHTML;
        // Visiting rows.
        let web = '';
        try { web = typeof getValidWebUrl === 'function' ? getValidWebUrl(inst) : (inst.website || ''); } catch (_) { web = inst.website || ''; }
        // The address row is the street address only: without one it would say the place line again (and "Windhoek, Namibia,
        // Namibia", since the location already names the country). And when the record's overview opens with the street itself
        // ("Natural history museum at 200 Central Park West in Theodore Roosevelt Park ..."), the row would say it twice over.
        const street = String(inst.address || '').split(',')[0].trim();
        const overview = (((inst.details || {}).overview) || []).slice(0, 2).join(' ');
        const place = street.length > 4 && overview.includes(street) ? '' : (inst.address || '');
        const rows = [
          ['place', place],
          ['hours', inst.opening_hours],
          ['ticket', inst.admission_fee || inst.admission_policy],
          ['web', web ? '<a href="' + esc(web) + '" target="_blank" rel="noopener noreferrer">' + esc(web.replace(/^https?:\/\/(www\.)?/, '').replace(/\/$/, '')) + '</a>' : '', true],
        ].filter((r) => r[1]);
        const rowsHtml = rows.map(([k, v, html]) => '<li><span>' + (html ? v : esc(v)) + '</span></li>').join('');
        // The website is one of the rows, so the Website pill would say it twice.
        const webBtn = $('dossier-sheet-link-web');
        if (webBtn) webBtn.toggleAttribute('data-gm-off', !!web);
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
        if (!here) { dot.classList.remove('is-on'); return; }
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
      // On desktop the same strip, feed, toast and alert marks serve the wide window (user, 4 Nov 2026: "add notifications same
      // as on mobile on desktop"). The strip and the toast float over the globe there, so they move into its viewport; the feed
      // opens as a panel at the left of the globe. The look is in assets/atlas.css, "DESKTOP: TOP STORY AND ALERTS".
      const placeStrip = () => {
        const home = PHONE() ? bar : ($('globeViewport') || document.body);
        if (strip.parentNode !== home) home.appendChild(strip);
        const th = PHONE() ? document.body : home; if (toast.parentNode !== th) th.appendChild(toast);
      };
      function paintStrip(list, alerts) {
        const top = alerts[0] || list.find((x) => x.status !== 'stale');
        strip.hidden = !top;
        if (!top) return;
        strip.classList.toggle('is-alert', !!alerts.length);
        // An alert now is the top story (user, 4 Nov 2026: "make alert to be a top story"): the strip keeps its name, takes the
        // alert's colour and headline, and says the report is an alert, and how many more there are.
        const label = 'Top story';
        const more = alerts.length > 1 ? ' · ' + (alerts.length - 1) + ' more alert' + (alerts.length > 2 ? 's' : '') : '';
        // No "Alert" word on the strip either (user, 5 Nov 2026): the meta line is the space, when, and how many more.
        const meta = top.inst.name + ' · ' + ago(top.when) + more;
        // No badge: the strip is its headline and meta line only (user, 5 Nov 2026: "delete icon"); its aria-label still says "Top story".
        strip.innerHTML = '<span class="gm-strip-head">' + esc(top.head) + '</span><span class="gm-strip-meta">' + esc(meta) + '</span>';
        strip.setAttribute('aria-label', label + (alerts.length ? ', an alert now' : '') + ': ' + top.head + '. ' + top.inst.name + ', ' + ago(top.when) + more + '. Open the latest reports');
      }

      // The feed.
      const feed = document.createElement('section');
      feed.id = 'gmFeed';
      feed.hidden = true;
      // Not modal (user, 5 Nov 2026: "make this notification UI work like google map"): the feed is a maps app's results
      // panel, so the map stays in sight and in use beside it or above it, and focus is not held inside it.
      feed.setAttribute('role', 'region');
      feed.setAttribute('aria-labelledby', 'gmFeedTitle');
      document.body.appendChild(feed);
      // On desktop the panel has a tab on its right edge, as the maps app's side panel does, that folds it away to the left
      // and brings it back. It sits outside the feed, since the feed scrolls and would clip it.
      const tab = document.createElement('button');
      tab.type = 'button';
      tab.id = 'gmFeedTab';
      tab.hidden = true;
      tab.setAttribute('aria-controls', 'gmFeed');
      tab.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M14.5 6l-6 6 6 6"/></svg>';
      document.body.appendChild(tab);
      const toast = document.createElement('div');
      toast.id = 'gmToast';
      toast.setAttribute('role', 'status');
      toast.setAttribute('aria-live', 'polite');
      document.body.appendChild(toast);
      placeStrip();
      // The notice is set as typography, not as a line of text (user, 5 Nov 2026: "design mobile notifications as detailed
      // typography"). A plain message (Alerts on, blocked) is one line of Serrif. A report or an alert is four lines, each in its
      // own voice: a kicker in tracked capitals over a hairline (what kind of notice, with how long ago hung on the right in
      // tabular figures), the name of the space large and tight in Jokker, the headline in Serrif Light, and a meta line of
      // status, source and place. The look is in assets/atlas.css, "NOTIFICATIONS AS TYPOGRAPHY". It stays up longer the more
      // there is to read: 6s, plus a quarter second a word past the first twelve, to 12s.
      let toastTimer = 0, toastClear = 0;
      const nb = (t) => esc(t).replace(/ (\S+)$/, '\u00a0$1');
      const dot = '<span class="gm-toast-dot" aria-hidden="true">\u00a0\u00b7 </span>';
      const noteHtml = (n) => '<p class="gm-toast-kick"><span class="gm-toast-mark" data-tone="' + esc(n.tone || 'report') + '" aria-hidden="true"></span>'
        + '<span class="gm-toast-label">' + n.label.map(esc).join(dot) + '</span>'
        + (n.when ? '<span class="gm-toast-when">' + esc(n.when) + '</span>' : '') + '</p>'
        + '<p class="gm-toast-name">' + nb(n.name) + '</p>'
        + (n.head ? '<p class="gm-toast-head">' + nb(n.head) + '</p>' : '')
        + (n.meta && n.meta.length ? '<p class="gm-toast-meta">' + n.meta.map((m, i, a) => '<span>' + esc(m) + (i < a.length - 1 ? '<span class="gm-toast-dot" aria-hidden="true">\u00a0\u00b7</span>' : '') + '</span>').join(' ') + '</p>' : '');
      const say = (t) => {
        clearTimeout(toastTimer); clearTimeout(toastClear);
        if (!t) { toast.classList.remove('is-on'); toastClear = setTimeout(() => { toast.innerHTML = ''; }, 250); return; }
        const rich = typeof t === 'object';
        toast.classList.toggle('is-rich', rich);
        toast.dataset.tone = rich ? (t.tone || 'report') : '';
        toast.innerHTML = rich ? noteHtml(t) : '<p class="gm-toast-text">' + nb(t) + '</p>';
        toast.classList.add('is-on');
        const words = toast.textContent.trim().split(/\s+/).length;
        toastTimer = setTimeout(() => say(''), Math.min(12000, 6000 + Math.max(0, words - 12) * 250));
      };
      // One report or alert as a notice. The meta line names the status first, so talk is never read as a finding.
      const note = (x, alert) => ({
        tone: alert ? 'alert' : (x.status === 'talk' || x.status === 'user' ? 'talk' : 'report'),
        label: [alert ? 'New alert' : 'New report', KIND[x.kind] || ''].filter(Boolean),
        when: ago(x.when),
        name: x.inst.name,
        head: x.head,
        meta: [STATUS[x.status], (SOURCE[x.who] || [''])[0], x.where, placeOf(x.inst)].filter(Boolean),
      });
      let lastFocus = null;


      // A post's headline is its own first sentence, so its text below starts after it and does not say it twice.
      const saidRest = (x) => {
        const said = String(x.said || ''), head = String(x.head || '').replace(/…$/, '');
        if (x.type === 'account' && head && said.startsWith(head)) return said.slice(head.length).replace(/^[\s.;,]+/, '');
        return said;
      };
      const monthsText = (t) => String(t || '').replace(/\d{4}-\d{2}(?:-\d{2})?/g, (m) => dateText(m));
      let list = [];
      // The feed is set as the Info block on displaay.net/typeface/documan (user, 5 Nov 2026: "layout needs to be similar to
      // this and use serif font, delete slop like icons, greyed out text etc, badges"). A 4px ink rule and a large plain title;
      // each part of a report under a small uppercase label with a 1px rule beneath it; the headline and the words in Serrif;
      // the facts as key and value lines, the key hung in a column. No icons, no pills, no status colours, no grey type: the
      // status is a line in the facts, said in words. Ink and paper only. The look is "TOP STORY: DISPLAAY INFO" in atlas.css.
      const row = (k, v) => v ? '<div class="ts-row"><dt>' + esc(k) + '</dt><dd>' + v + '</dd></div>' : '';
      function card(x, poster, alert) {
        const i = list.indexOf(x);
        const n = x.urls.length;
        const src = SOURCE[x.who] || ['Source type not recorded', false];
        // A reply printed in full is its own part; only its absence is a line in the facts.
        const hasReply = x.type === 'gossip' && x.reply && !/^no reply/i.test(x.reply);
        // Each fact is said once (user, 4 Nov 2026: "remove all repetition"). A leak's own dating (months) is kept when it says
        // more than the day.
        const day = dateText(x.when), rel = ago(x.when);
        const when = day && rel && rel !== day ? day + ', ' + rel : (day || rel);
        const leakDated = x.type === 'leak' && x.dated ? monthsText(x.dated) : '';
        const said = saidRest(x);
        const facts = '<dl class="ts-rows">'
          // The headline is plain text (user, 5 Nov 2026); the space's name is the one way from a report to its place on the map.
          + row('Space', '<button type="button" class="gm-open ts-space" data-i="' + i + '">' + esc(x.inst.name) + '</button>')
          + row('Place', esc(placeOf(x.inst)))
          + row('Status', esc(STATUS[x.status] || ''))
          + row({ case: 'On record', account: 'Posted', leak: 'Dated' }[x.type] || 'Reported', esc(when))
          + row('Source', esc(x.where || 'The record') + (x.role ? ', ' + esc(x.role) : ''))
          + row('Basis', (src[1] ? 'User-generated, not verified. ' : '') + esc(src[0]))
          + (leakDated && leakDated !== day ? row('Document', 'dated ' + esc(leakDated)) : '')
          + (x.type === 'gossip' && !hasReply ? row('Reply', 'None found') : '')
          + (x.checked ? row('Links checked', esc(dateText(x.checked))) : '')
          + row(n === 1 ? 'Link' : 'Links', '<a href="' + esc(x.urls[0]) + '" target="_blank" rel="noopener noreferrer">' + n + (n === 1 ? ' source' : ' sources') + '</a>')
          + '</dl>';
        return '<article class="gm-story ts-story' + (poster ? ' is-top' : '') + (alert ? ' is-alert' : '') + '" data-i="' + i + '" data-key="' + esc(x.key) + '">'
          + '<p class="ts-label">' + esc((alert ? 'Alert · ' : '') + (KIND[x.kind] || 'Report')) + '</p>'
          + '<h3 class="ts-headline">' + esc(x.head) + '</h3>'
          + (said ? '<p class="ts-prose">' + esc(said) + '</p>' : '')
          + (hasReply ? '<p class="ts-label">Reply</p><p class="ts-prose">' + esc(x.reply) + '</p>' : '')
          + (x.outcome ? '<p class="ts-label">Outcome</p><p class="ts-prose">' + esc(x.outcome) + '</p>' : '')
          + '<p class="ts-label">Details</p>' + facts
          + '<button type="button" class="gm-share ts-share' + (poster ? ' is-main' : '') + '" data-i="' + i + '">Share</button></article>';
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
        // A section is a plain title on a 4px ink rule with its count beside it, the reports under it.
        const sec = (title, meta, arr, alert, note) => arr.length ? '<section class="ts-sec"><h2 class="ts-sec-title"><span>' + title + '</span>' + (meta ? '<span class="ts-sec-meta">' + meta + '</span>' : '') + '</h2>'
          + (note ? '<p class="ts-prose ts-note">' + note + '</p>' : '') + arr.map((x) => card(x, false, alert)).join('') + '</section>' : '';
        const bellOn = store.get('atlas-alerts') === 'on';
        // What the feed holds, and the rule for an alert, are said once, at the foot, in the same ink as the rest.
        const about = (gossipOn()
            ? 'Gossip mode: talk and denials are included, each marked for what it is. Talk is what people say, not a finding. Items from anonymous posts or user reviews say so.'
            : 'Reports on record as confirmed or resolved, and documented cases. Turn on Gossip mode to include talk.')
          + ' Every item comes from the records, with its source and the day its links were last checked; nothing here is written by the atlas.';
        const alertRule = 'An alert is a protest, strike, dispute, allegation or similar reported in the last ' + ALERT_DAYS + ' days and not resolved' + (gossipOn() ? '' : ', and confirmed') + '.';
        // The close is the record's big thin cross, two 1.1px lines on a paper square with no circle (user, 7 Nov 2026: "make proper
        // cross like big one with no outline"). It sits before the head in a sticky holder of no height, so the head scrolls away with
        // the reports and the cross alone stays at the top right (user, 7 Nov 2026: "keep cross on scroll").
        feed.innerHTML = '<div class="ts">'
          + '<div class="ts-pin"><button type="button" class="gm-feed-close ts-btn ts-x" aria-label="Close the reports"><svg viewBox="0 0 24 24" width="28" height="28" fill="none" stroke="currentColor" stroke-width="1.1" aria-hidden="true"><line x1="21" y1="3" x2="3" y2="21"></line><line x1="3" y1="3" x2="21" y2="21"></line></svg></button></div>'
          + '<header class="gm-feed-head ts-bar"><button type="button" class="ts-grab" aria-label="' + grabLabel() + '"></button><h2 id="gmFeedTitle" class="ts-title">Top story</h2>'
          + ('Notification' in window ? '<button type="button" class="gm-bell ts-btn" aria-pressed="' + bellOn + '">' + (bellOn ? 'Alerts on' : 'Alert me') + '</button>' : '')
          + '</header>'
          + (top ? card(top, true, topIsAlert) : '')
          + sec(topIsAlert ? 'More stories' : 'Alerts now', '', alertList, true)
          + sec('Near you', near.length + (near.length === 1 ? ' report' : ' reports'), near, false)
          // No count beside Latest (user, 7 Nov 2026: "delete 1 in the past 30 days").
          + sec(alertList.length || near.length ? 'Latest' : 'Worldwide', '', world, false)
          + sec('From staff and visitors', 'User posts', posts, false, 'Posts by staff and visitors on review sites and Reddit, quoted as posted. User-generated: one person’s experience each, not checked as fact.')
          + sec('From leaked documents', docs.length + ' on record', docs, false)
          + '<section class="ts-sec"><h2 class="ts-sec-title"><span>About these reports</span></h2>'
          + (!list.length ? '<p class="ts-prose ts-note">No dated reports on record yet.</p>' : '')
          + '<p class="ts-prose ts-note">' + about + '</p>'
          + (alertList.length || topIsAlert ? '<p class="ts-prose ts-note">' + alertRule + '</p>' : '')
          + '</section></div>';
      }
      // The line that said when the reports were last checked and the newest date on record is gone (user, 7 Nov 2026:
      // "delete this text Checked for new reports 41 s ago · newest on record 28 Oct 2026"); the check itself still runs.

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
        const ok = (PHONE() ? root.classList.contains('gm-map') : root.classList.contains('gmd')) && typeof project === 'function' && !g('isCityStreetViewActive') && canvas;
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
        say(note(x, true));
        // The system notification cannot be styled, so its text carries the same order: the space as the title, then the
        // kicker, the headline, and status, source and place, each on its own line.
        if (notifyOn()) {
          const n = note(x, true);
          try { new Notification(n.name, { body: n.label.join(' \u00b7 ') + ' \u00b7 ' + n.when + '\n' + n.head + '\n' + n.meta.join(' \u00b7 '), tag: x.key }); } catch (_) {}
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
                if (added.length === 1) say(note(added[0], false));
                else if (added.length) {
                  const names = [...new Set(added.map((y) => y.inst.name))];
                  const shown = names.slice(0, 2).join(', ') + (names.length > 2 ? ' and ' + (names.length - 2) + ' more' : '');
                  say({ tone: 'report', label: ['New reports'], when: 'now', name: added.length + ' new reports', head: shown, meta: ['On the record', 'Open Top story to read them'] });
                }
                announce(alerts, false);
                if (!feed.hidden) { const sc = feed.scrollTop; render(); feed.scrollTop = sc; }
                return;
              }
            }
          }
        } catch (_) { checkFailed = true; }
      }
      setInterval(check, 60000);
      document.addEventListener('visibilitychange', () => { if (document.visibilityState === 'visible') check(); });

      // ---- The feed as a maps app's results panel (user, 5 Nov 2026: "make this notification UI work like google map") ----
      // On a phone it is a bottom sheet with three heights, as the maps app's list is: peek (the title and the top story's
      // headline, with the map in sight above), half, and full, where the reports scroll. It follows the finger and snaps to
      // the nearest height, a flick goes one further, and a pull down from peek closes it; the grabber, tapped, steps up a
      // height and from full goes back to peek. Tapping a report puts the list away and opens that space's record on the map;
      // when the record is closed the list comes back where it was, as the maps app's Back to results does. On desktop it is
      // the side panel: the full height of the map at its left edge, folded away and back by the tab on its edge.
      const DETENTS = ['peek', 'half', 'full'];
      let detent = 'peek', collapsed = false, parked = null;
      const safe = (() => {
        const v = {};
        return (side) => {
          if (v[side] != null) return v[side];
          const probe = document.createElement('div');
          probe.style.cssText = 'position:fixed;left:0;top:0;width:1px;height:env(safe-area-inset-' + side + ',0px);visibility:hidden;pointer-events:none';
          document.body.appendChild(probe); v[side] = probe.offsetHeight || 0; probe.remove();
          return v[side];
        };
      })();
      const room = () => window.innerHeight - safe('top') - 8;
      function grabLabel() {
        return detent === 'full' ? 'Shrink the reports to the top story' : detent === 'half' ? 'Expand the reports to full screen' : 'Expand the reports';
      }
      function heightOf(d) {
        const h = room();
        if (d === 'full') return h;
        if (d === 'half') return Math.round(h * 0.55);
        // Peek ends under the top story's headline, so its alert and its words are read with the map still in sight; never
        // more than 70% of the screen and never less than the head alone.
        const fr = feed.getBoundingClientRect();
        const head = feed.querySelector('.is-top .ts-headline') || feed.querySelector('.ts-bar');
        const end = head ? head.getBoundingClientRect().bottom - fr.top + feed.scrollTop + 24 + safe('bottom') : 0;
        return Math.max(160, Math.min(Math.round(end) || 160, Math.round(h * 0.7), Math.round(h * 0.55) - 1));
      }
      function setDetent(d, animate) {
        if (!PHONE()) return;
        detent = d;
        feed.dataset.detent = d;
        feed.classList.toggle('gm-still', animate === false);
        if (animate === false) requestAnimationFrame(() => requestAnimationFrame(() => feed.classList.remove('gm-still')));
        feed.style.setProperty('--ts-h', heightOf(d) + 'px');
        if (d !== 'full') feed.scrollTop = 0;
        const g = feed.querySelector('.ts-grab');
        if (g) { g.setAttribute('aria-label', grabLabel()); g.setAttribute('aria-expanded', String(d === 'full')); }
      }
      function setCollapsed(c) {
        collapsed = !!c && !PHONE();
        root.classList.toggle('ts-collapsed', collapsed);
        feed.inert = collapsed;
        tab.setAttribute('aria-expanded', String(!collapsed));
        tab.setAttribute('aria-label', collapsed ? 'Show the reports panel' : 'Hide the reports panel');
      }
      function layout(animate) {
        tab.hidden = feed.hidden || PHONE();
        if (feed.hidden) return;
        if (PHONE()) { setCollapsed(false); setDetent(detent, animate); }
        else { feed.style.removeProperty('--ts-h'); delete feed.dataset.detent; }
      }

      function open(focusKey) {
        lastFocus = document.activeElement;
        parked = null;
        render();
        feed.hidden = false;
        root.classList.add('gm-feed-open');
        setCollapsed(false);
        feed.scrollTop = 0;
        check();
        const target = focusKey && feed.querySelector('.gm-story[data-key="' + (window.CSS && CSS.escape ? CSS.escape(focusKey) : focusKey) + '"]');
        // From an alert mark the sheet opens full at that alert; from the strip it opens at peek, on the top story.
        detent = target ? 'full' : 'peek';
        layout(false);
        // The headline is plain text now, so the report itself takes the focus.
        if (target) { target.scrollIntoView({ block: 'start' }); target.classList.add('is-focus'); target.tabIndex = -1; target.focus({ preventScroll: true }); }
        else { const c = feed.querySelector('.gm-feed-close'); if (c) c.focus({ preventScroll: true }); }
      }
      function close(refocus) {
        parked = null;
        if (feed.hidden) return;
        feed.hidden = true;
        root.classList.remove('gm-feed-open');
        setCollapsed(false);
        layout();
        if (refocus !== false && lastFocus && lastFocus.focus) lastFocus.focus();
      }
      // Put the list away while a space's record is up, and bring it back, at the same height and place, when it closes.
      function park() {
        parked = { detent, top: feed.scrollTop };
        feed.hidden = true;
        root.classList.remove('gm-feed-open');
        layout();
      }
      const dossier = $('dossier-bottom-sheet');
      if (dossier) {
        let was = dossier.classList.contains('hidden');
        new MutationObserver(() => {
          const now = dossier.classList.contains('hidden');
          if (now && !was && parked && PHONE()) {
            const p = parked; parked = null;
            feed.hidden = false;
            root.classList.add('gm-feed-open');
            detent = p.detent;
            layout(false);
            feed.scrollTop = p.top;
          }
          was = now;
        }).observe(dossier, { attributes: true, attributeFilter: ['class'] });
      }
      window.atlasOpenTopStory = open;
      strip.addEventListener('click', () => open());
      tab.addEventListener('click', () => {
        setCollapsed(!collapsed);
        if (!collapsed) { const c = feed.querySelector('.gm-feed-close'); if (c) c.focus({ preventScroll: true }); }
      });
      window.addEventListener('resize', () => { layout(false); });
      if (document.fonts && document.fonts.ready) document.fonts.ready.then(() => { if (!feed.hidden && detent === 'peek') layout(false); });
      document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && !feed.hidden && feed.contains(document.activeElement)) { e.preventDefault(); e.stopPropagation(); close(); }
      }, true);
      // Below full the sheet does not scroll, so a key that moves focus to a report under its edge raises it to full first.
      feed.addEventListener('focusin', (e) => {
        if (!PHONE() || detent === 'full' || e.target.closest('.ts-bar')) return;
        if (e.target.getBoundingClientRect().bottom > feed.getBoundingClientRect().bottom) setDetent('full');
      });
      feed.addEventListener('click', async (e) => {
        if (e.target.closest('.gm-feed-close')) { close(); return; }
        if (e.target.closest('.ts-grab')) { setDetent(detent === 'peek' ? 'half' : detent === 'half' ? 'full' : 'peek'); return; }
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
        // Only the space's name in the Space line opens the space (user, 5 Nov 2026: "Headline stops being a link").
        const go = e.target.closest('.gm-open');
        if (!go) return;
        const x = list[+go.dataset.i]; if (!x) return;
        const hasRecord = typeof window.selectInstitution === 'function' && !!recordOf(x.inst.id || x.inst.name);
        // As in the maps app: on a phone the list steps aside for the space's record (or drops to peek when there is no
        // record, so the map shows the place). On desktop the panel closes, so the space's record and the map have the room
        // (user, 5 Nov 2026: "close panel on desktop too when opening museum").
        if (PHONE()) { if (hasRecord) park(); else setDetent('peek'); }
        else close(false);
        if (hasRecord) window.selectInstitution(x.inst, false);
        const fly = g('flyTo');
        if (typeof fly === 'function' && typeof x.inst.lon === 'number') fly(x.inst.lon, x.inst.lat);
      });
      // Dragging the sheet (phone). Below full the whole sheet follows the finger; at full the reports scroll, and only a
      // pull down from their top, or a drag on the grabber, moves the sheet.
      let y0 = null, h0 = 0, lastY = 0, lastT = 0, vel = 0, dragging = false;
      feed.addEventListener('touchstart', (e) => {
        if (!PHONE() || e.touches.length !== 1) { y0 = null; return; }
        if (e.target.closest('a, button:not(.ts-grab)')) { y0 = null; return; }
        y0 = lastY = e.touches[0].clientY; lastT = Date.now(); h0 = feed.offsetHeight; vel = 0; dragging = false;
      }, { passive: true });
      feed.addEventListener('touchmove', (e) => {
        if (y0 === null) return;
        const y = e.touches[0].clientY, d = y - y0, now = Date.now();
        if (!dragging) {
          if (Math.abs(d) < 6) return;
          if (detent === 'full' && !e.target.closest('.ts-grab') && (d < 0 || feed.scrollTop > 0)) { y0 = null; return; }
          dragging = true;
          feed.classList.add('gm-still');
        }
        if (e.cancelable) e.preventDefault();
        vel = (y - lastY) / Math.max(1, now - lastT);
        lastY = y; lastT = now;
        feed.style.setProperty('--ts-h', Math.max(64, Math.min(room(), h0 - d)) + 'px');
      }, { passive: false });
      const dragEnd = () => {
        if (y0 === null) return;
        y0 = null;
        if (!dragging) return;
        dragging = false;
        feed.classList.remove('gm-still');
        const h = feed.offsetHeight;
        const hs = DETENTS.map(heightOf);
        if (h < hs[0] * 0.6 || (vel > 0.9 && detent === 'peek')) { close(false); return; }
        let i;
        if (Math.abs(vel) > 0.6) i = Math.max(0, Math.min(2, DETENTS.indexOf(detent) + (vel < 0 ? 1 : -1)));
        else i = hs.reduce((best, v, k) => (Math.abs(v - h) < Math.abs(hs[best] - h) ? k : best), 0);
        setDetent(DETENTS[i]);
      };
      feed.addEventListener('touchend', dragEnd, { passive: true });
      feed.addEventListener('touchcancel', dragEnd, { passive: true });

      // Gossip mode and a known location change what is shown.
      const gb = $('mobileGossipBtn');
      if (gb) new MutationObserver(() => { refresh(); }).observe(gb, { attributes: true, attributeFilter: ['aria-pressed'] });
      document.addEventListener('atlas:here', () => { if (!feed.hidden) render(); });
      // Crossing between the phone and desktop layouts closes the feed, since it is a sheet on one and a panel on the other.
      let wasPhone = PHONE();
      window.addEventListener('resize', () => { if (PHONE() !== wasPhone) { wasPhone = PHONE(); close(false); placeStrip(); } });
      // A click on the map no longer closes the feed (user, 5 Nov 2026: "work like google map"): the panel stays beside the
      // map while it is panned and zoomed, and is folded away by its tab or closed by Close.
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
        const label = chip(C + (p.why === 'near you' ? ', near you' : ''), '', 'gm-loc-label');
        // The place chip looked like a button and did nothing; now it takes the map to the place.
        label.setAttribute('aria-label', 'Show ' + C + ' on the map');
        label.addEventListener('click', () => { const f = g('filterByCity'); if (typeof f === 'function') f(C, true, false); });
        const chips = [label];
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
