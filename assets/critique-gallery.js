// Artists' images: a map layer over the spaces that the cultural space critique collection (references 1801–2000) names.
// The data is assets/critique-gallery-data.js, written by tools/build_critique_gallery.py; only references whose own
// credit, note or source page names a space the atlas has a record for are in it.
//
// With the layer on (Layers panel, "Artists’ images"), each of those spaces gets a diamond ring on the globe, and pointing
// at it opens a card with its images (user, 13 Nov 2026: "pop ups on map, like a layer when hovering a space"). This is
// the one hover card on the map, and it shows only while the layer is on; a click on the space still opens its sheet as
// before. A thumbnail or Open gallery opens the gallery, which steps through the space's images (arrows, swipe, keys).
// Touch screens have no hover: the record carries the same images in an Artists' images row (critiqueGalleryRowHtml).
//
// On a desktop the images show in the chat window, not over the map (user, 15 Nov 2026: "the images can show in chat
// window when user hovers map"): pointing at a marked space lays its images over the right column, one large picture with
// its title and artist under it and the rest as a strip, as a gallery site shows an exhibition's picture beside its list
// when a name is pointed at. The column keeps the picture while the pointer travels from the map into it; leaving it, or
// pointing at empty map, gives the conversation back. Where the column is not on screen the card over the map is kept.
(function () {
  const DATA = window.CRITIQUE_GALLERY;
  if (!DATA) return;
  const SPACES = DATA.spaces;
  const e = s => String(s == null ? '' : s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const forInst = inst => (inst && inst.id && SPACES[inst.id]) || null;
  const canHover = () => window.matchMedia('(hover: hover) and (pointer: fine)').matches;
  let on = false;

  // ---- The layer: its box in the Layers panel, and the marks it draws on the globe ----
  const box = () => document.getElementById('critiqueLayerBox');
  function setOn(v) {
    on = !!v;
    window.atlasCritiqueLayer = on;
    const b = box(); if (b) b.checked = on;
    if (!on) { hidePop(true); if (pane) hidePane(true); }
    if (typeof window.renderGlobe === 'function') window.renderGlobe();
    document.dispatchEvent(new CustomEvent('atlas:critique', { detail: on }));
  }
  function wirePanel() {
    const b = box();
    if (!b) return;
    const count = document.querySelector('[data-count="critique"]');
    if (count) count.textContent = Object.keys(SPACES).length;
    b.addEventListener('change', () => setOn(b.checked));
    const reset = document.querySelector('#layersPanel .layers-reset');
    if (reset) reset.addEventListener('click', () => setOn(false));
  }

  // A diamond ring around the dot: told by its shape, not its colour, so it reads beside the tier circles, squares and
  // triangles. Ink on a paper halo, so it holds on the globe's black and on the light theme's white alike.
  // At world zoom the map draws one dot per city and leaves most spaces out, so a diamond tied only to the dots on
  // screen showed nothing until a city was zoomed into (user, 13 Nov 2026: "dont see any changes"). A space with no dot
  // drawn is placed from its own coordinates with the page's projection, on the visible side of the globe only.
  let recs = null;
  const recFor = id => {
    if (!recs && typeof ALL_INSTITUTIONS !== 'undefined') { recs = new Map(); ALL_INSTITUTIONS.forEach(i => { if (i.id && SPACES[i.id]) recs.set(i.id, i); }); }
    return recs && recs.get(id);
  };
  window.atlasCritiqueDraw = function (ctx, dots, sel, hov, project, r, cx, cy) {
    if (!on || !dots) return;
    const css = getComputedStyle(document.documentElement);
    const ink = css.getPropertyValue('--ink').trim() || '#000';
    const paper = css.getPropertyValue('--paper').trim() || '#fff';
    const marks = [], seen = new Set();
    dots.forEach(d => {
      if (!forInst(d.inst)) return;
      seen.add(d.inst.id);
      marks.push([d.inst, d.renderX != null ? d.renderX : d.x, d.renderY != null ? d.renderY : d.y]);
    });
    if (typeof project === 'function') Object.keys(SPACES).forEach(id => {
      if (seen.has(id)) return;
      const i = recFor(id); if (!i || !isFinite(+i.lat) || !isFinite(+i.lon)) return;
      const q = project(+i.lon, +i.lat, r, cx, cy);
      if (q && q.front !== false && isFinite(q.x) && isFinite(q.y)) marks.push([i, q.x, q.y]);
    });
    ctx.save();
    marks.forEach(([inst, x, y]) => {
      const big = (sel && sel.name === inst.name) || (hov && hov.name === inst.name);
      const s = big ? 11 : 9;
      ctx.beginPath();
      ctx.moveTo(x, y - s); ctx.lineTo(x + s, y); ctx.lineTo(x, y + s); ctx.lineTo(x - s, y); ctx.closePath();
      ctx.lineWidth = 4; ctx.strokeStyle = paper; ctx.stroke();
      ctx.lineWidth = 1.5; ctx.strokeStyle = ink; ctx.stroke();
    });
    ctx.restore();
  };

  // ---- The hover card ----
  let pop = null, popFor = null, hideTimer = null;
  function buildPop() {
    pop = document.createElement('div');
    pop.id = 'critiquePop';
    pop.className = 'critique-pop';
    pop.hidden = true;
    pop.addEventListener('pointerenter', () => clearTimeout(hideTimer));
    pop.addEventListener('pointerleave', () => hidePop());
    pop.addEventListener('click', ev => {
      const t = ev.target.closest('[data-cg-open]');
      if (t) openGallery(popFor, +t.dataset.cgOpen || 0);
    });
    document.getElementById('globeViewport').appendChild(pop);
  }
  function popHtml(id, sp) {
    const shown = sp.images.slice(0, 4);
    const more = sp.images.length - shown.length;
    // One image fills the card's width, so a single picture is not a 96px strip (user, 14 Nov 2026: "image is too small");
    // several sit in a row at 160px. The single one offers the full file too, since the 480px thumb is soft at card width.
    const one = sp.images.length === 1;
    return `<p class="critique-pop-name space-name">${e(sp.name)}</p>
      <p class="critique-pop-tie">${e(sp.tie)}</p>
      <div class="critique-pop-thumbs${one ? ' is-one' : ''}">${shown.map((im, i) => `<button type="button" data-cg-open="${i}" aria-label="${e(im.project)}, image ${i + 1} of ${sp.images.length}"><img src="${e(im.thumb)}"${one ? ` srcset="${e(im.thumb)} ${Math.min(480, Math.round(480 * im.w / Math.max(im.w, im.h)))}w, ${e(im.src)} ${im.w}w" sizes="588px"` : ''} alt="" loading="lazy" width="${one ? im.w : Math.round(im.w * 160 / im.h)}" height="${one ? im.h : 160}"></button>`).join('')}${more > 0 ? `<button type="button" class="critique-pop-more" data-cg-open="${shown.length}">${more} more</button>` : ''}</div>
      <button type="button" class="critique-pop-open" data-cg-open="0">Open gallery, ${sp.images.length} ${sp.images.length === 1 ? 'image' : 'images'}</button>`;
  }
  // ---- The images in the chat window ----
  let pane = null, paneFor = null, paneTimer = null;
  const column = () => document.getElementById('workspacePanelsWrapper');
  const columnShown = () => { const c = column(); if (!c) return false; const r = c.getBoundingClientRect(); return r.width >= 280 && r.height >= 240; };
  function buildPane() {
    pane = document.createElement('div');
    pane.id = 'critiquePane';
    pane.className = 'critique-pane';
    pane.hidden = true;
    pane.setAttribute('role', 'region');
    pane.setAttribute('aria-label', 'Artists’ images of the space under the pointer');
    pane.addEventListener('pointerenter', () => clearTimeout(paneTimer));
    pane.addEventListener('pointerleave', () => hidePane());
    pane.addEventListener('click', ev => {
      const t = ev.target.closest('[data-cg-open]');
      if (t) openGallery(paneFor, +t.dataset.cgOpen || 0);
    });
    // Pointing at a picture in the strip makes it the large one, without opening the gallery.
    pane.addEventListener('pointerover', ev => {
      const t = ev.target.closest('[data-cg-pick]');
      if (t) pick(+t.dataset.cgPick);
    });
    column().appendChild(pane);
  }
  function capFor(im) {
    const c = window.critiqueCaption(im);
    return { project: c.title, who: c.who };
  }
  function pick(i) {
    const sp = SPACES[paneFor]; if (!sp || !sp.images[i]) return;
    const im = sp.images[i], c = capFor(im);
    const big = pane.querySelector('[data-cg-big]');
    big.dataset.cgOpen = i;
    big.setAttribute('aria-label', `${im.project}, image ${i + 1} of ${sp.images.length}, open the gallery`);
    const img = big.querySelector('img');
    img.src = im.mid || im.src; img.width = im.w; img.height = im.h;
    pane.querySelector('[data-cg-project]').textContent = c.project;
    pane.querySelector('[data-cg-who]').textContent = c.who;
    pane.querySelectorAll('[data-cg-pick]').forEach(b => b.setAttribute('aria-current', +b.dataset.cgPick === i ? 'true' : 'false'));
  }
  function paneHtml(sp) {
    const n = sp.images.length;
    return `<p class="critique-pane-name space-name">${e(sp.name)}</p>
      <p class="critique-pane-tie">${e(sp.tie)}</p>
      <button type="button" class="critique-pane-big" data-cg-big data-cg-open="0"><img alt="" decoding="async"></button>
      <p class="critique-pane-project" data-cg-project></p>
      <p class="critique-pane-who" data-cg-who></p>
      ${n > 1 ? `<div class="critique-pane-strip">${sp.images.map((im, i) => `<button type="button" data-cg-pick="${i}" data-cg-open="${i}" aria-label="${e(im.project)}, image ${i + 1} of ${n}"><img src="${e(im.thumb)}" alt="" loading="lazy" width="${Math.round(im.w * 72 / im.h)}" height="72"></button>`).join('')}</div>` : ''}
      <button type="button" class="critique-pane-open" data-cg-open="0">Open gallery, ${n} ${n === 1 ? 'image' : 'images'}</button>`;
  }
  function showPane(id) {
    if (!pane) buildPane();
    clearTimeout(paneTimer);
    if (pop && !pop.hidden) hidePop(true);
    if (paneFor !== id) { pane.innerHTML = paneHtml(SPACES[id]); paneFor = id; pick(0); pane.scrollTop = 0; }
    pane.hidden = false;
  }
  // Longer grace than the card's: the column is further from the map than a card beside the pointer.
  function hidePane(now) {
    clearTimeout(paneTimer);
    const go = () => { if (pane) pane.hidden = true; paneFor = null; };
    if (now) go(); else paneTimer = setTimeout(go, 600);
  }
  const anyShown = () => (pop && !pop.hidden) || (pane && !pane.hidden);
  function hideAll(now) { if (pop && !pop.hidden) hidePop(now); if (pane && !pane.hidden) hidePane(now); }

  function showPop(id, clientX, clientY) {
    if (!pop) buildPop();
    clearTimeout(hideTimer);
    if (popFor !== id) { pop.innerHTML = popHtml(id, SPACES[id]); popFor = id; }
    pop.hidden = false;
    const vp = document.getElementById('globeViewport').getBoundingClientRect();
    const w = pop.offsetWidth, h = pop.offsetHeight;
    let x = clientX - vp.left + 18, y = clientY - vp.top + 18;
    if (x + w > vp.width - 8) x = clientX - vp.left - w - 18;
    if (y + h > vp.height - 8) y = Math.max(8, vp.height - h - 8);
    pop.style.left = Math.max(8, x) + 'px';
    pop.style.top = Math.max(8, y) + 'px';
  }
  // A short grace period, so the pointer can travel from the dot onto the card and its thumbnails.
  function hidePop(now) {
    clearTimeout(hideTimer);
    const go = () => { if (pop) pop.hidden = true; popFor = null; };
    if (now) go(); else hideTimer = setTimeout(go, 280);
  }
  function wireHover() {
    const canvas = document.getElementById('globeCanvas');
    if (!canvas) return;
    // Registered after the page's own pointer handlers, so the hovered space is already worked out when this runs.
    canvas.addEventListener('pointermove', ev => {
      if (!on || !canHover() || ev.buttons) { if (ev.buttons && anyShown()) hideAll(true); return; }
      const inst = typeof window.getHoveredInstitution === 'function' ? window.getHoveredInstitution() : null;
      const sp = forInst(inst);
      if (sp) { if (columnShown()) showPane(inst.id); else showPop(inst.id, ev.clientX, ev.clientY); }
      else if (anyShown()) hideAll();
    });
    canvas.addEventListener('pointerleave', () => { if (anyShown()) hideAll(); });
    canvas.addEventListener('wheel', () => hideAll(true), { passive: true });
  }

  // ---- The gallery ----
  let dlg = null, gId = null, gIdx = 0, lastFocus = null;
  function buildDialog() {
    dlg = document.createElement('dialog');
    dlg.id = 'critiqueGallery';
    dlg.className = 'critique-gallery';
    dlg.setAttribute('aria-labelledby', 'critiqueGalleryTitle');
    dlg.innerHTML = `<div class="cg-top">
        <h2 id="critiqueGalleryTitle" class="cg-title"><span class="space-name" data-cg-space></span> <span class="cg-count" data-cg-count></span></h2>
        <button type="button" class="cg-btn cg-close" data-cg-close aria-label="Close gallery">Close</button>
      </div>
      <div class="cg-stage">
        <button type="button" class="cg-btn cg-prev" data-cg-step="-1" aria-label="Previous image">Previous</button>
        <figure class="cg-figure"><img data-cg-img alt=""><figcaption class="cg-cap" aria-live="polite"></figcaption></figure>
        <button type="button" class="cg-btn cg-next" data-cg-step="1" aria-label="Next image">Next</button>
      </div>`;
    dlg.addEventListener('click', ev => {
      if (ev.target === dlg || ev.target.closest('[data-cg-close]')) return dlg.close();
      const s = ev.target.closest('[data-cg-step]');
      if (s) step(+s.dataset.cgStep);
    });
    dlg.addEventListener('keydown', ev => {
      if (ev.key === 'ArrowRight') { ev.preventDefault(); step(1); }
      else if (ev.key === 'ArrowLeft') { ev.preventDefault(); step(-1); }
    });
    dlg.addEventListener('close', () => { if (lastFocus && lastFocus.isConnected) lastFocus.focus(); });
    // Swipe on a touch screen: a sideways drag of 40px or more steps one image.
    let sx = null;
    const stage = dlg.querySelector('.cg-figure');
    stage.addEventListener('pointerdown', ev => { sx = ev.clientX; });
    stage.addEventListener('pointerup', ev => { if (sx != null && Math.abs(ev.clientX - sx) > 40) step(ev.clientX < sx ? 1 : -1); sx = null; });
    document.body.appendChild(dlg);
  }
  function show() {
    const sp = SPACES[gId], im = sp.images[gIdx], n = sp.images.length;
    dlg.querySelector('[data-cg-space]').textContent = sp.name;
    dlg.querySelector('[data-cg-count]').textContent = n > 1 ? `${gIdx + 1} of ${n}` : '';
    const img = dlg.querySelector('[data-cg-img]');
    img.src = im.src; img.width = im.w; img.height = im.h;
    // The caption is the hand-written one of assets/critique-captions.js, as on artists-images.html: the work, the people,
    // what the picture is and where, then the photographer when the credit names one. The raw credit is not printed: it
    // restated the title and the artist the two lines above already give (user, 14 Nov 2026: "the description is a slop"),
    // and neither is the collection's type label, which read the same way (user, 15 Nov 2026: "slop?").
    const c = window.critiqueCaption(im);
    img.alt = `${c.title}, ${c.who}`;
    dlg.querySelector('.cg-cap').innerHTML = `<p class="cg-project">${e(c.title)}</p>
      <p class="cg-meta">${e(c.who)}</p>
      ${c.line ? `<p class="cg-meta">${e(c.line)}.</p>` : ''}
      <p class="cg-credit">${c.photo ? `${e(c.photo)}. ` : ''}<a href="${e(im.source)}" target="_blank" rel="noopener noreferrer">Source</a></p>`;
    dlg.querySelectorAll('[data-cg-step]').forEach(b => { b.hidden = n < 2; });
    // The next image is fetched ahead, so stepping through does not wait on the network.
    if (n > 1) new Image().src = sp.images[(gIdx + 1) % n].src;
  }
  function step(d) {
    const n = SPACES[gId].images.length;
    gIdx = (gIdx + d + n) % n;
    show();
  }
  function openGallery(id, idx) {
    if (!SPACES[id]) return;
    if (!dlg) buildDialog();
    lastFocus = document.activeElement;
    gId = id; gIdx = Math.max(0, Math.min(idx || 0, SPACES[id].images.length - 1));
    hidePop(true);
    if (pane) hidePane(true);
    show();
    if (!dlg.open) dlg.showModal();
    dlg.querySelector('[data-cg-close]').focus();
  }
  window.openCritiqueGallery = openGallery;

  // ---- The record's row: the same images, for touch screens and for anyone reading the record ----
  window.critiqueGalleryRowHtml = function (inst) {
    const sp = forInst(inst);
    if (!sp) return '';
    return `<div class="cg-row" data-cg-row="${e(inst.id)}">
      <p class="cg-row-tie">${e(sp.tie)}</p>
      <div class="cg-row-thumbs">${sp.images.map((im, i) => `<button type="button" data-cg-open="${i}" aria-label="${e(im.project)}, image ${i + 1} of ${sp.images.length}"><img src="${e(im.thumb)}" alt="" loading="lazy" width="${Math.round(im.w * 120 / im.h)}" height="120"></button>`).join('')}</div>
    </div>`;
  };
  document.addEventListener('click', ev => {
    const t = ev.target.closest('[data-cg-row] [data-cg-open]');
    if (!t) return;
    ev.stopPropagation();
    openGallery(t.closest('[data-cg-row]').dataset.cgRow, +t.dataset.cgOpen || 0);
  }, true);

  // The Images filter (assets/layers.js, SPACE_TEST.images) shows only these spaces; while it is on the diamonds are on too,
  // so each image card is one point away. Switched off with the filter only if the filter switched them on.
  let byFilter = false;
  document.addEventListener('atlas:filter', () => {
    const f = typeof window.atlasSpaceFilter === 'function' ? window.atlasSpaceFilter() : null;
    if (f === 'images' && !on) { byFilter = true; setOn(true); }
    else if (f !== 'images' && byFilter) { byFilter = false; if (on) setOn(false); }
  });

  function init() { wirePanel(); wireHover(); }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
