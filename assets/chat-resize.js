/* The desktop chat and record column can be dragged wider, up to the whole screen (user, 4 Nov 2026).
   A handle on the column's left edge sets --gmd-w on the root, which the map pane, the column, the chips and the map
   controls all read (atlas.css, DESKTOP MAPS). Drag it, or focus it and use the arrow keys (Shift for bigger steps), Home
   for the narrowest and End for full screen; a double-click goes between the usual width and full screen. The width is
   kept for the next visit. While the map is left narrower than 240px its own controls are hidden, so none sit over the chat. */
(function () {
  // The usual width is 48% of the screen, 420 to 860px, as --gmd-w in atlas.css says: wide enough for the reported items' two
  // columns (user, 4 Nov 2026). The CSS value is a clamp(), which reads back unresolved, so the same sum is done here.
  var MIN = 360, KEY = 'atlasChatWidth', userSet = false;
  function DEFW() { return window.innerWidth < 1024 ? 360 : Math.round(Math.min(860, Math.max(420, window.innerWidth * 0.48))); }
  var mq = window.matchMedia('(min-width: 768px)');
  var root = document.documentElement, handle = null, raf = 0;

  function maxW() { return window.innerWidth; }
  function clamp(w) { return Math.round(Math.min(maxW(), Math.max(MIN, w))); }
  function current() { var v = parseFloat(getComputedStyle(root).getPropertyValue('--gmd-w')); return isNaN(v) ? DEFW() : v; }
  function apply(w, save) {
    w = clamp(w);
    root.style.setProperty('--gmd-w', w + 'px');
    root.classList.toggle('chat-wide', window.innerWidth - w < 240);
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
    col.appendChild(handle);

    var startX = 0, startW = 0, dragging = false;
    handle.addEventListener('pointerdown', function (e) {
      if (e.button !== 0) return;
      // A drag is the visitor's own width from its first move: apply() fires a resize for the globe on every move, and the resize
      // listener below put a width nobody had chosen back to the default, so the column snapped back and could not be dragged.
      dragging = true; userSet = true; startX = e.clientX; startW = current();
      handle.setPointerCapture(e.pointerId); root.classList.add('chat-resizing'); e.preventDefault();
    });
    handle.addEventListener('pointermove', function (e) { if (dragging) apply(startW + (startX - e.clientX), false); });
    function end(e) { if (!dragging) return; dragging = false; root.classList.remove('chat-resizing'); apply(current(), true); }
    handle.addEventListener('pointerup', end);
    handle.addEventListener('pointercancel', end);
    handle.addEventListener('dblclick', function () { apply(current() >= maxW() ? DEFW() : maxW(), true); });
    handle.addEventListener('keydown', function (e) {
      var step = e.shiftKey ? 120 : 24, w = current();
      if (e.key === 'ArrowLeft') w += step; else if (e.key === 'ArrowRight') w -= step;
      else if (e.key === 'Home') w = MIN; else if (e.key === 'End') w = maxW(); else return;
      e.preventDefault(); apply(w, true);
    });
  }

  function start() {
    if (!mq.matches) return;
    build();
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
