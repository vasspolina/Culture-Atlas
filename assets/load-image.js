// The picture the atlas shows while it loads (user, 13 Nov 2026: "make one of the image shown when website loading, maybe take
// few more seconds for it to load, make it aprox 40% size of the screen on desktop and 70 on mobile"). One of the artists'
// images (window.LOAD_IMAGES, written by tools/build_critique_gallery.py) at random, on the paper, with its title and artist
// under it. A click, a tap or any key takes it away sooner. The size and look are the load image rules at the end of
// assets/sheet.css. Loaded at the top of <body>, so it covers the page before anything else is drawn.
//
// The image is picked and requested by a small script at the top of <head> (window.LOAD_PICK, window.LOAD_PICK_IMG), so the
// download starts before the 2 MB of head is parsed. When it was only asked for here, it was still downloading behind the
// stylesheets and scripts while the paper was already up, and the screen stayed blank (user, 14 Nov 2026: "the image is not
// showing while its loading in cultural atlas, fix and just load web for 3 seconds").
//
// SHOW_MS (4 seconds) is counted from the moment the picture is on screen, not from the first paint, so the reader always
// sees it for the full 4 seconds. If the picture fails, or has not arrived after WAIT_MS, the screen goes and the page shows.
(function () {
  const list = window.LOAD_IMAGES;
  if (!list || !list.length) return;
  const SHOW_MS = 4000;   // the picture stays 4 seconds once visible (user, 14 Nov 2026: "make show on image load 4 sec"; it was 3, before that 5)
  const WAIT_MS = 6000;   // never hold the page longer than this waiting for a picture that does not come
  const pick = window.LOAD_PICK || list[Math.floor(Math.random() * list.length)];

  const el = document.createElement('div');
  el.id = 'loadImage';
  el.setAttribute('role', 'status');
  el.setAttribute('aria-label', 'Loading the atlas');
  const fig = document.createElement('figure');
  // The preloaded element itself goes on the page, so the bytes already fetched are the ones drawn.
  const img = (window.LOAD_PICK && window.LOAD_PICK_IMG) || new Image();
  if (!img.src) img.src = pick.src;
  img.width = pick.w; img.height = pick.h; img.decoding = 'async';
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
  let started = false;
  function shown() { if (started) return; started = true; setTimeout(hide, SHOW_MS); }
  if (img.complete && img.naturalWidth) shown();
  else {
    img.addEventListener('load', shown, { once: true });
    img.addEventListener('error', hide, { once: true });
    setTimeout(() => { if (!started) hide(); }, WAIT_MS);
  }
  el.addEventListener('click', hide);
  window.addEventListener('keydown', function k() { hide(); window.removeEventListener('keydown', k); });
})();
