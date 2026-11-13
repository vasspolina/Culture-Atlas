/* The index column, the chat and the map can each be set wider or narrower by dragging the lines between them (COLUMN below).
   The desktop chat and record column can be dragged wider, up to the whole screen (user, 4 Nov 2026).
   A handle on the column's right edge (between the chat and the map; sheet.css, PLACES | CHAT | MAP) sets --gmd-w on the root, which the map pane, the column, the chips and the map
   controls all read (atlas.css, DESKTOP MAPS). Drag it, or focus it and use the arrow keys (Shift for bigger steps), Home
   for the narrowest and End for full screen; a double-click goes between the usual width and full screen. The width is
   kept for the next visit. While the map is left narrower than 240px its own controls are hidden, so none sit over the chat. */
(function () {
  // The usual width is 48% of the screen, 420 to 860px, as --gmd-w in atlas.css says: wide enough for the reported items' two
  // columns (user, 4 Nov 2026). The CSS value is a clamp(), which reads back unresolved, so the same sum is done here.
  // The page loads as index a quarter, chat about half, map the rest (user, 13 Nov 2026: "make it load like this", a screenshot
  // at 25 / 48.5 / 26.5 of the window), so the usual chat width is 48.5% of the window, at least 360px.
  var MIN = 360, KEY = 'atlasChatWidth', userSet = false;
  function DEFW() { return window.innerWidth < 1024 ? 360 : Math.round(Math.max(360, window.innerWidth * 0.485)); }
  var mq = window.matchMedia('(min-width: 768px)');
  var root = document.documentElement, handle = null, raf = 0;

  // The index column at the left (assets/sheet.css, --sh-col): a quarter of a window 1080px or wider, or the width it was
  // dragged to (below, COLUMN), and none while it is closed.
  function indexW() {
    if (window.innerWidth < 1080 || root.classList.contains('sh-col-closed')) return 0;
    var v = parseFloat(root.style.getPropertyValue('--sh-col'));
    return isNaN(v) ? window.innerWidth * 0.25 : v;
  }
  function maxW() { return window.innerWidth; }
  function clamp(w) { return Math.round(Math.min(maxW(), Math.max(MIN, w))); }
  function current() { var v = parseFloat(getComputedStyle(root).getPropertyValue('--gmd-w')); return isNaN(v) ? DEFW() : v; }
  function apply(w, save) {
    w = clamp(w);
    root.style.setProperty('--gmd-w', w + 'px');
    root.classList.toggle('chat-wide', window.innerWidth - w - indexW() < 240);
    root.classList.toggle('chat-full', w >= maxW());
    if (handle) { handle.setAttribute('aria-valuenow', String(w)); handle.setAttribute('aria-valuemax', String(maxW())); handle.setAttribute('aria-valuetext', w >= maxW() ? 'Full screen' : w + ' pixels wide'); }
    if (save) { userSet = true; try { localStorage.setItem(KEY, String(w)); } catch (e) {} }
    // The globe draws to its pane's size on resize; tell it once a frame.
    if (!raf) raf = requestAnimationFrame(function () { raf = 0; window.dispatchEvent(new Event('resize')); });
  }

  function build() {
    var col = document.getElementById('workViewContainer');
    if (!col || handle) return;
    handle = document.createElement('div');
    handle.id = 'chatResizeHandle';
    handle.setAttribute('role', 'separator');
    handle.setAttribute('aria-orientation', 'vertical');
    handle.setAttribute('aria-label', 'Chat width: drag, or use the arrow keys; End for full screen');
    handle.setAttribute('aria-controls', 'workViewContainer');
    handle.setAttribute('aria-valuemin', String(MIN));
    handle.tabIndex = 0;
    // On the page, not in the column: the column clips what overhangs it, so the half of the handle over the map could not
    // be caught (user, 13 Nov 2026: "make all windows adjustable"). sheet.css places it on the line between chat and map.
    document.body.appendChild(handle);

    var startX = 0, startW = 0, dragging = false;
    handle.addEventListener('pointerdown', function (e) {
      if (e.button !== 0) return;
      // A drag is the visitor's own width from its first move: apply() fires a resize for the globe on every move, and the resize
      // listener below put a width nobody had chosen back to the default, so the column snapped back and could not be dragged.
      dragging = true; userSet = true; startX = e.clientX; startW = current();
      handle.setPointerCapture(e.pointerId); root.classList.add('chat-resizing'); e.preventDefault();
    });
    handle.addEventListener('pointermove', function (e) { if (dragging) apply(startW + (e.clientX - startX), false); });
    function end(e) { if (!dragging) return; dragging = false; root.classList.remove('chat-resizing'); apply(current(), true); }
    handle.addEventListener('pointerup', end);
    handle.addEventListener('pointercancel', end);
    handle.addEventListener('dblclick', function () { apply(current() >= maxW() ? DEFW() : maxW(), true); });
    handle.addEventListener('keydown', function (e) {
      var step = e.shiftKey ? 120 : 24, w = current();
      if (e.key === 'ArrowRight') w += step; else if (e.key === 'ArrowLeft') w -= step;
      else if (e.key === 'Home') w = MIN; else if (e.key === 'End') w = maxW(); else return;
      e.preventDefault(); apply(w, true);
    });
  }

  // Back to the map from a chat that covers it (user, 10 Nov 2026: "i do not see the back to map button that will lead back
  // to full mode map"): a button at the head of the panel's pages, shown while the map is covered (html.chat-wide), puts the
  // column back to its usual width and lets that width follow the window again.
  function toMap() {
    userSet = false;
    try { localStorage.removeItem(KEY); } catch (e) {}
    apply(DEFW(), false);
  }
  window.atlasChatToMap = toMap;
  // And the other way (user, 10 Nov 2026: "add button to expand the chat to full mode"): "Expand chat" in the same place
  // while the map is in sight takes the column to the whole window, and the width is kept for the next visit.
  function toFull() { apply(maxW(), true); }
  window.atlasChatToFull = toFull;
  function buildBack() {
    var bar = document.getElementById('workspaceContextTabBar');
    if (!bar || document.getElementById('shBackToMap')) return;
    var b = document.createElement('button');
    b.type = 'button';
    b.id = 'shBackToMap';
    b.textContent = '\u2039 Back to map';
    b.addEventListener('click', toMap);
    var x = document.createElement('button');
    x.type = 'button';
    x.id = 'shExpandChat';
    x.textContent = 'Expand chat';
    x.setAttribute('aria-label', 'Expand the chat to the whole window');
    x.addEventListener('click', toFull);
    bar.insertBefore(x, bar.firstChild);
    bar.insertBefore(b, bar.firstChild);
  }

  // ---- COLUMN: the index column can be dragged wider or narrower too (user, 13 Nov 2026: "make all windows adjustable").
  // A handle on its right edge, between the places and the chat, sets --sh-col on the root. The chat gives or takes the
  // difference, so the map keeps its width: dragging a line moves only the two panes either side of it. The column is 260px
  // at the least (what the head bar's left part needs) and leaves the chat its 360px. Arrow keys as on the chat's handle;
  // a double-click puts it back to a quarter of the window. The width is kept for the next visit. Closing the column (its
  // cross; desktop-maps.js) still takes it to 0, as --sh-col:0 there is !important.
  var COL_MIN = 260, COL_KEY = 'atlasIndexWidth', colMq = window.matchMedia('(min-width: 1080px)'), colHandle = null, colChosen = 0;
  function colDef() { return Math.round(window.innerWidth * 0.25); }
  function colMax() { return Math.round(window.innerWidth * 0.5); }
  function colApply(w, save, chosen) {
    w = Math.round(Math.min(colMax(), Math.max(COL_MIN, w)));
    root.style.setProperty('--sh-col', w + 'px');
    if (chosen) colChosen = w;
    if (colHandle) { colHandle.setAttribute('aria-valuenow', String(w)); colHandle.setAttribute('aria-valuemax', String(colMax())); colHandle.setAttribute('aria-valuetext', w + ' pixels wide'); }
    if (save) { try { localStorage.setItem(COL_KEY, String(w)); } catch (e) {} }
    return w;
  }
  // Move the line between the column and the chat to `w`, keeping the map's left edge where it was.
  function colMove(w, save) {
    var col0 = indexW(), chat0 = current(), wide = root.classList.contains('chat-wide');
    var top = wide ? colMax() : Math.min(colMax(), col0 + chat0 - MIN);
    w = Math.min(top, w);
    var got = colApply(w, save, true);
    if (!wide) apply(chat0 - (got - col0), save); else if (!raf) raf = requestAnimationFrame(function () { raf = 0; window.dispatchEvent(new Event('resize')); });
  }
  function buildCol() {
    if (colHandle) return;
    colHandle = document.createElement('div');
    colHandle.id = 'shColResizeHandle';
    colHandle.setAttribute('role', 'separator');
    colHandle.setAttribute('aria-orientation', 'vertical');
    colHandle.setAttribute('aria-label', 'Side panel width: drag, or use the arrow keys');
    colHandle.setAttribute('aria-controls', 'shIndex shReports');
    colHandle.setAttribute('aria-valuemin', String(COL_MIN));
    colHandle.tabIndex = 0;
    document.body.appendChild(colHandle);
    var startX = 0, startW = 0, dragging = false;
    colHandle.addEventListener('pointerdown', function (e) {
      if (e.button !== 0) return;
      dragging = true; userSet = true; startX = e.clientX; startW = indexW();
      colHandle.setPointerCapture(e.pointerId); root.classList.add('chat-resizing'); e.preventDefault();
    });
    colHandle.addEventListener('pointermove', function (e) { if (dragging) colMove(startW + (e.clientX - startX), false); });
    function end() { if (!dragging) return; dragging = false; root.classList.remove('chat-resizing'); colMove(indexW(), true); }
    colHandle.addEventListener('pointerup', end);
    colHandle.addEventListener('pointercancel', end);
    colHandle.addEventListener('dblclick', function () { colMove(colDef(), true); });
    colHandle.addEventListener('keydown', function (e) {
      var step = e.shiftKey ? 120 : 24, w = indexW();
      if (e.key === 'ArrowRight') w += step; else if (e.key === 'ArrowLeft') w -= step;
      else if (e.key === 'Home') w = COL_MIN; else if (e.key === 'End') w = colMax(); else return;
      e.preventDefault(); colMove(w, true);
    });
  }
  function startCol() {
    if (!colMq.matches) { root.style.removeProperty('--sh-col'); return; }
    buildCol();
    var saved = 0;
    try { saved = parseFloat(localStorage.getItem(COL_KEY)) || 0; } catch (e) {}
    colChosen = saved;
    colApply(saved || colDef(), false);
  }
  colMq.addEventListener('change', startCol);
  window.addEventListener('resize', function () {
    if (!colMq.matches || !colHandle) return;
    // A width nobody chose stays a quarter of the window; a dragged one is kept, within half the window. The width being
    // dragged counts as chosen from its first move, since every move fires a resize for the globe.
    var want = Math.round(Math.min(colMax(), Math.max(COL_MIN, colChosen || colDef())));
    if (Math.round(indexW()) !== want && !root.classList.contains('sh-col-closed')) colApply(want, false);
  });

  function start() {
    if (!mq.matches) return;
    startCol();
    build();
    buildBack();
    var saved = 0;
    try { saved = parseFloat(localStorage.getItem(KEY)) || 0; } catch (e) {}
    userSet = !!saved;
    if (saved) apply(saved, false); else if (handle) apply(DEFW(), false);
  }
  window.addEventListener('resize', function () {
    if (!mq.matches || !handle) return;
    // A width nobody chose follows the window; a dragged one is kept.
    // apply() itself fires a resize for the globe, so it runs only when the width really changes.
    if (!userSet) { if (Math.round(current()) !== clamp(DEFW())) apply(DEFW(), false); return; }
    var w = current(); if (w > maxW() || root.classList.contains('chat-full')) { root.style.setProperty('--gmd-w', maxW() + 'px'); root.classList.toggle('chat-wide', true); }
  });
  mq.addEventListener('change', function () { if (mq.matches) start(); else { root.style.removeProperty('--gmd-w'); root.classList.remove('chat-wide', 'chat-full'); } });
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start); else start();
})();
