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
        // Peek: down to the end of the row of actions, never more than 45% of the map, never less than 168px.
        let end = 168;
        if (actions && titleBlock) end = actions.offsetTop + actions.offsetHeight + 16;
        return Math.max(168, Math.min(end, Math.round(h * 0.45)));
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
      let wasHidden = sheet.classList.contains('hidden');
      new MutationObserver(() => {
        const hidden = sheet.classList.contains('hidden');
        if (hidden) { sheet.scrollTop = 0; sheet.style.removeProperty('--gm-h'); }
        else if (wasHidden && PHONE()) requestAnimationFrame(() => setDetent('peek', false));
        wasHidden = hidden;
      }).observe(sheet, { attributes: true, attributeFilter: ['class'] });
      const name = $('dossier-sheet-name');
      if (name) new MutationObserver(() => {
        sheet.scrollTop = 0;
        if (PHONE() && !sheet.classList.contains('hidden')) requestAnimationFrame(() => setDetent(detent === 'full' ? 'full' : 'peek', false));
      }).observe(name, { childList: true, characterData: true, subtree: true });
      window.addEventListener('resize', () => { if (PHONE() && !sheet.classList.contains('hidden')) setDetent(detent, false); });

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

    syncState();
  });
})();
