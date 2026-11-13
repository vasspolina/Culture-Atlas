// The picture the atlas shows while it loads (user, 13 Nov 2026: "make one of the image shown when website loading, maybe take
// few more seconds for it to load, make it aprox 40% size of the screen on desktop and 70 on mobile"). One of the artists'
// images (window.LOAD_IMAGES, written by tools/build_critique_gallery.py) at random, on the paper, with its title and artist
// under it. It stays until the page has loaded and for at least MIN_MS (5 seconds, user, 13 Nov 2026: "make load time 5sec", after 10) from the first paint, never longer than MAX_MS, and
// a click, a tap or any key takes it away sooner. The size and look are the load image rules at the end of assets/sheet.css.
// Loaded at the top of <body>, so it covers the page before anything else is drawn.
(function () {
  const list = window.LOAD_IMAGES;
  if (!list || !list.length) return;
  const MIN_MS = 5000, MAX_MS = 5000;   // 5 seconds, never more (user, 13 Nov 2026: "make load time 5sec"; it was 10, at most 15)
  const pick = list[Math.floor(Math.random() * list.length)];
  const t0 = performance.now();

  const el = document.createElement('div');
  el.id = 'loadImage';
  el.setAttribute('role', 'status');
  el.setAttribute('aria-label', 'Loading the atlas');
  const fig = document.createElement('figure');
  const img = document.createElement('img');
  img.src = pick.src; img.width = pick.w; img.height = pick.h; img.decoding = 'async';
  img.alt = `${pick.project}, by ${pick.artist}`;
  const cap = document.createElement('figcaption');
  const t = document.createElement('i');
  t.textContent = pick.project;
  cap.append(t, `, ${pick.artist}`);
  fig.append(img, cap);
  el.append(fig);
  document.body.prepend(el);

  let gone = false;
  function hide() {
    if (gone) return;
    gone = true;
    const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (reduce) { el.remove(); return; }
    el.classList.add('is-leaving');
    setTimeout(() => el.remove(), 600);
  }
  function whenLoaded() { setTimeout(hide, Math.max(0, MIN_MS - (performance.now() - t0))); }
  if (document.readyState === 'complete') whenLoaded(); else window.addEventListener('load', whenLoaded, { once: true });
  setTimeout(hide, MAX_MS);
  el.addEventListener('click', hide);
  window.addEventListener('keydown', function k() { hide(); window.removeEventListener('keydown', k); });
})();
