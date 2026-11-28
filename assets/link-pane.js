/* Links open beside the atlas (user, 19 Nov 2026: "make culture atlas open links in the app"). A click on a link that leaves
   the atlas (a source under a chat answer, a funder, press or record link, a place's website) opens the page in a pane at the
   window's right, over the map, with the chat still in sight at the left. The pane has back and forward (between the pages
   opened here), reload, the page's host, "Open in new tab" and a close button; its left edge can be dragged, or focused and
   moved with the arrow keys. On a phone the pane covers the whole screen.

   What still opens a new tab as before: a click with Cmd, Ctrl, Shift or Alt held, a middle click (no click event fires),
   links with a download attribute or data-no-pane, mail and phone links, and links within the page (#...).

   Many sites refuse to be shown inside another page (X-Frame-Options, or CSP frame-ancestors), and a page cannot read that
   from a frame on another site. So: hosts known to refuse (assets/frame-refusers.js, built by tools/frame_refusers.py from the
   headers each host sends) get a plain note with the link at once, without a frame; any other page that has not loaded after
   a few seconds gets the same note under the toolbar; and "Open in new tab" is always in the toolbar. The pane is never blank.

   The frame is sandboxed without allow-top-navigation, so a framed page cannot take the atlas's own tab away. Each page gets
   a fresh frame, so pages opened here add nothing to the browser's own back button.

   The look is in assets/sheet.css (LINK PANE), prefix sh-web. */
(function () {
  'use strict';
  var root = document.documentElement;
  var phone = window.matchMedia('(max-width: 767px)');
  var KEY = 'atlasWebPaneWidth', MIN = 320, WAIT = 8000;
  var pane, bar, hint, host, backB, fwdB, reloadB, newTabB, closeB, stage, note, handle;
  var stack = [], at = -1, frame = null, timer = 0, opener = null, built = false;

  // 1: the host refuses to be framed, 0: it allows it, null: not known (not checked, no answer, or a host that only
  // redirects elsewhere, such as doi.org, whose answer depends on where each link leads).
  var REDIRECTORS = { 'doi.org': 1, 'dx.doi.org': 1, 'bit.ly': 1, 't.co': 1, 'tinyurl.com': 1, 'ow.ly': 1, 'goo.gl': 1, 'lnkd.in': 1, 'buff.ly': 1, 'archive.ph': 1, 'archive.today': 1 };
  function framing(h) {
    var list = window.ATLAS_FRAME_REFUSERS;
    if (!list || !h) return null;
    h = h.replace(/^www\./, '');
    if (REDIRECTORS[h]) return null;
    // The list has every host checked: 1 refuses, 0 allows. The host itself decides; a host not checked takes the answer
    // of the nearest domain above it that was (a refusing domain usually refuses on every subdomain it serves).
    for (var parts = h.split('.'); parts.length >= 2; parts.shift()) {
      var d = parts.join('.');
      if (Object.prototype.hasOwnProperty.call(list, d)) return list[d];
    }
    return null;
  }
  function hostOf(u) { try { return new URL(u).hostname.replace(/^www\./, ''); } catch (e) { return u; } }

  // Should this URL open in the pane? Only web pages: http(s), not this page itself or a place on it.
  function paneable(href) {
    var u;
    try { u = new URL(href, location.href); } catch (e) { return null; }
    if (u.protocol !== 'http:' && u.protocol !== 'https:') return null;
    if (u.origin === location.origin && u.pathname === location.pathname) return null;
    // An https atlas cannot frame an http page (the browser blocks mixed content), so the pane asks for the https address;
    // nearly every site the atlas links to serves one, and the pane's fallback note covers the rest.
    if (location.protocol === 'https:' && u.protocol === 'http:') u.protocol = 'https:';
    return u.href;
  }

  function el(tag, attrs, text) {
    var n = document.createElement(tag);
    for (var k in attrs) n.setAttribute(k, attrs[k]);
    if (text) n.textContent = text;
    return n;
  }
  function button(cls, label, glyph) {
    var b = el('button', { type: 'button', 'class': 'sh-web-btn ' + cls, 'aria-label': label, title: label });
    b.textContent = glyph;
    return b;
  }

  function build() {
    if (built) return;
    built = true;
    pane = el('section', { id: 'shWeb', 'class': 'sh-web', role: 'region', 'aria-label': 'Linked page', hidden: '' });
    bar = el('div', { 'class': 'sh-web-bar' });
    backB = button('sh-web-back', 'Previous linked page', '‹');
    fwdB = button('sh-web-fwd', 'Next linked page', '›');
    reloadB = button('sh-web-reload', 'Reload linked page', '↻');
    host = el('span', { 'class': 'sh-web-host', 'aria-live': 'polite' });
    newTabB = el('a', { 'class': 'sh-web-btn sh-web-newtab', target: '_blank', rel: 'noopener noreferrer', 'data-no-pane': '', 'aria-label': 'Open in new tab', title: 'Open in new tab' });
    // On a phone only the arrow shows (sheet.css), so the host keeps its room.
    newTabB.append(el('span', { 'class': 'sh-web-newtab-word', 'aria-hidden': 'true' }, 'Open in new tab '), document.createTextNode('↗'));
    closeB = button('sh-web-close', 'Close linked page', '×');
    bar.append(backB, fwdB, reloadB, host, newTabB, closeB);
    // Under the toolbar, for a page whose site is not known to allow framing: a site that refuses still fires the frame's
    // load event and draws an empty frame, which the atlas cannot see. This line says so and gives the link.
    hint = el('p', { 'class': 'sh-web-hint', hidden: '' });
    stage = el('div', { 'class': 'sh-web-stage' });
    note = el('div', { 'class': 'sh-web-note', role: 'status' });
    stage.appendChild(note);
    handle = el('div', { 'class': 'sh-web-edge', role: 'separator', 'aria-orientation': 'vertical', tabindex: '0',
      'aria-label': 'Linked page width: drag, or use the arrow keys', 'aria-controls': 'shWeb', 'aria-valuemin': String(MIN) });
    pane.append(handle, bar, hint, stage);
    document.body.appendChild(pane);

    backB.addEventListener('click', function () { if (at > 0) show(--at); });
    fwdB.addEventListener('click', function () { if (at < stack.length - 1) show(++at); });
    reloadB.addEventListener('click', function () { if (at >= 0) show(at); });
    closeB.addEventListener('click', function () { close(); });
    pane.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') { e.preventDefault(); e.stopPropagation(); close(); return; }
      // Keep Tab inside the pane while it covers the phone screen.
      if (e.key === 'Tab' && phone.matches) {
        var f = pane.querySelectorAll('button:not([disabled]), a[href], iframe, [tabindex="0"]');
        f = Array.prototype.filter.call(f, function (n) { return n.offsetParent !== null; });
        if (!f.length) return;
        var first = f[0], last = f[f.length - 1];
        if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
        else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
      }
    });
    edge();
  }

  // ---- width: the pane covers the map by default (the chat stays in sight), at least MIN px and at most the window less
  // 240px, or the width it was dragged to. Kept for the next visit.
  function defaultW() {
    // Where the chat column ends is where the map starts (--sh-map-l in sheet.css is a calc(), which reads back unresolved).
    var col = document.getElementById('workViewContainer');
    var r = col ? col.getBoundingClientRect() : null;
    var w = r && r.width ? window.innerWidth - r.right : 0;
    if (w < 420) w = window.innerWidth * 0.45;
    return w;
  }
  function maxW() { return Math.max(MIN, window.innerWidth - 240); }
  function chosen() { var v = 0; try { v = parseFloat(localStorage.getItem(KEY)) || 0; } catch (e) {} return v; }
  function setW(w, save) {
    w = Math.round(Math.min(maxW(), Math.max(MIN, w)));
    root.style.setProperty('--sh-web-w', w + 'px');
    handle.setAttribute('aria-valuenow', String(w));
    handle.setAttribute('aria-valuemax', String(Math.round(maxW())));
    handle.setAttribute('aria-valuetext', w + ' pixels wide');
    if (save) { try { localStorage.setItem(KEY, String(w)); } catch (e) {} }
    return w;
  }
  function current() { var v = parseFloat(root.style.getPropertyValue('--sh-web-w')); return isNaN(v) ? defaultW() : v; }
  function edge() {
    var startX = 0, startW = 0, dragging = false;
    handle.addEventListener('pointerdown', function (e) {
      if (e.button !== 0) return;
      dragging = true; startX = e.clientX; startW = current();
      handle.setPointerCapture(e.pointerId); root.classList.add('sh-web-resizing'); e.preventDefault();
    });
    // The pane's edge is on its left, so dragging left makes it wider.
    handle.addEventListener('pointermove', function (e) { if (dragging) setW(startW - (e.clientX - startX), false); });
    function end() { if (!dragging) return; dragging = false; root.classList.remove('sh-web-resizing'); setW(current(), true); }
    handle.addEventListener('pointerup', end);
    handle.addEventListener('pointercancel', end);
    handle.addEventListener('dblclick', function () { try { localStorage.removeItem(KEY); } catch (e) {} setW(defaultW(), false); });
    handle.addEventListener('keydown', function (e) {
      var step = e.shiftKey ? 120 : 24, w = current();
      if (e.key === 'ArrowLeft') w += step; else if (e.key === 'ArrowRight') w -= step;
      else if (e.key === 'Home') w = maxW(); else if (e.key === 'End') w = MIN; else return;
      e.preventDefault(); setW(w, true);
    });
    window.addEventListener('resize', function () { if (!pane.hidden) setW(chosen() || defaultW(), false); });
  }

  function setNote(kind, url) {
    var h = hostOf(url);
    note.textContent = '';
    note.className = 'sh-web-note sh-web-note-' + kind;
    if (kind === 'loading') { note.appendChild(document.createTextNode('Loading ' + h + '…')); return; }
    var p = el('p', {}, kind === 'refused'
      ? h + ' does not allow its pages to be shown inside other sites.'
      : h + ' has not shown here yet. Some sites refuse to be shown inside other sites.');
    var a = el('a', { href: url, target: '_blank', rel: 'noopener noreferrer', 'data-no-pane': '' }, 'Open ' + h + ' in a new tab ↗');
    note.append(p, a);
  }

  function show(i) {
    var url = stack[i];
    clearTimeout(timer);
    if (frame) { frame.remove(); frame = null; }
    host.textContent = hostOf(url);
    host.title = url;
    newTabB.href = url;
    backB.disabled = i <= 0;
    fwdB.disabled = i >= stack.length - 1;
    stage.classList.remove('sh-web-loaded');
    var known = framing(hostOf(url));
    hint.hidden = known !== null;
    if (known === null) {
      hint.textContent = '';
      hint.append(document.createTextNode('Some sites refuse to be shown here. If this stays empty, '),
        el('a', { href: url, target: '_blank', rel: 'noopener noreferrer', 'data-no-pane': '' }, 'open ' + hostOf(url) + ' in a new tab \u2197'), document.createTextNode('.'));
    }
    if (known === 1) { setNote('refused', url); return; }
    setNote('loading', url);
    frame = el('iframe', {
      'class': 'sh-web-frame', title: 'Linked page: ' + hostOf(url), src: url, referrerpolicy: 'no-referrer',
      sandbox: 'allow-scripts allow-same-origin allow-forms allow-popups allow-popups-to-escape-sandbox'
    });
    var f = frame;
    f.addEventListener('load', function () {
      if (f !== frame) return;
      clearTimeout(timer);
      stage.classList.add('sh-web-loaded');
    });
    timer = setTimeout(function () { if (f === frame && !stage.classList.contains('sh-web-loaded')) setNote('slow', url); }, WAIT);
    stage.appendChild(f);
  }

  function open(url, from) {
    build();
    var wasOpen = !pane.hidden;
    // Closing gives focus back to the link that was clicked last, so a second link opened while the pane is up takes over
    // from the first. Focus inside the pane itself (its close button, after the first link) is never what to go back to.
    var src = from || document.activeElement;
    if (src && !pane.contains(src) && src !== document.body && src !== root) opener = src;
    else if (!wasOpen) opener = null;
    // A new page drops whatever was ahead of the current one, as a browser does.
    if (stack[at] !== url) { stack = stack.slice(0, at + 1); stack.push(url); at = stack.length - 1; }
    if (!wasOpen) {
      pane.hidden = false;
      root.classList.add('sh-web-open');
      setW(chosen() || defaultW(), false);
    }
    show(at);
    closeB.focus();
  }

  // keepFocus: the pane closes because another control was pressed, which keeps the focus.
  function close(keepFocus) {
    if (!pane || pane.hidden) return;
    clearTimeout(timer);
    if (frame) { frame.remove(); frame = null; }
    hint.hidden = true;
    pane.hidden = true;
    root.classList.remove('sh-web-open');
    var back = opener; opener = null;
    if (!keepFocus && back && document.contains(back) && typeof back.focus === 'function') back.focus();
  }

  function plainClick(e) { return !(e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) && (e.button === 0 || e.button == null); }

  // Every link click, before the page's own handlers (capture), so a handler that stops the click from reaching a card
  // behind the link does not stop this too.
  window.addEventListener('click', function (e) {
    if (e.defaultPrevented || !plainClick(e)) return;
    var a = e.target && e.target.closest ? e.target.closest('a[href]') : null;
    if (!a || a.hasAttribute('download') || a.hasAttribute('data-no-pane')) return;
    if (pane && pane.contains(a)) return;
    var url = paneable(a.getAttribute('href'));
    if (!url) return;
    // Within the atlas's own site only links meant for a new tab leave the page; the rest are its own navigation.
    if (new URL(url).origin === location.origin && a.target !== '_blank') return;
    e.preventDefault();
    open(url, a);
  }, true);

  // Pages opened from script (the globe's website buttons) come through window.open.
  var nativeOpen = window.open;
  window.open = function (u, target) {
    var ev = window.event;
    var url = u != null ? paneable(String(u)) : null;
    if (url && (target == null || target === '_blank') && !(ev && (ev.metaKey || ev.ctrlKey || ev.shiftKey || ev.altKey))) {
      open(url, document.activeElement);
      return null;
    }
    return nativeOpen.apply(window, arguments);
  };

  // The top bar's map controls close the pane, since it covers the map they change (user, 20 Nov 2026: "if i press top
  // menu button switch to influence map"): Influence map, and the title that goes back to the map.
  var MAP_CONTROLS = '#topInfluenceBtn, #mobileInfluenceBtn, #topBrandLogoBtn, #mobileTopBrandBtn';
  document.addEventListener('click', function (e) {
    if (!pane || pane.hidden || !e.target || !e.target.closest) return;
    if (e.target.closest(MAP_CONTROLS)) close(true);
  }, true);

  // Escape closes the pane while focus is in it (its own keydown above) or nowhere in particular.
  document.addEventListener('keydown', function (e) {
    if (e.key !== 'Escape' || !pane || pane.hidden) return;
    var a = document.activeElement;
    if (a === document.body || a === root || !a) { e.preventDefault(); close(); }
  });

  window.atlasOpenLink = open;
  window.atlasCloseLink = close;
})();
