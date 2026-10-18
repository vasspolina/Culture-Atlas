/* Chat motion: gossip speech bubbles drawn as SVG that fit their text, a typing reveal for new replies,
   and the app's hairlines drawn in on load. No dependencies; every effect is skipped under reduced motion. */
(function () {
  'use strict';
  var NS = 'http://www.w3.org/2000/svg';
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var SEL = '#curatorMessages>.curator-message-wrap,#curatorMessages>.justify-end,#curatorDrawerLiveStream>.curator-message-wrap,#curatorDrawerLiveStream>.justify-end';
  var seq = 0;

  function gossip() { return document.body.classList.contains('gossip-mode-active'); }

  /* Only a turn that holds gossip gets a balloon. The reply builder in index.html marks it: the turn carries .is-gossip and its
     reported, unverified items carry data-gossip (the record's reported items, a list of spaces with reported items). A plain
     record, a city list, the status line and the reader's own questions carry neither and are left exactly as in normal mode.
     The words of the text never decide this on their own: the status line says "none is independently verified" and is not gossip. */
  function isGossip(el) { return el.classList.contains('is-gossip') || !!el.querySelector('[data-gossip]'); }

  /* Comic-book balloons. Each gossip turn is one of three kinds, chosen by what it says: a speech balloon (a lumpy blob with a long
     curved tail, as in the reference), a shout (a jagged burst) for what is flagged or reported, and a thought cloud
     (scalloped, with a trail of small bubbles) for what is unverified. Every shape starts from the rounded rectangle that
     holds the text and only ever grows outward from it, so the text always sits inside. */
  function rnd(seed) {
    return function () {
      seed |= 0; seed = seed + 0x6D2B79F5 | 0;
      var t = Math.imul(seed ^ seed >>> 15, 1 | seed);
      t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t;
      return ((t ^ t >>> 14) >>> 0) / 4294967296;
    };
  }

  // A point and its outward normal at arc length s along the rounded rectangle, clockwise from the top-left.
  function rim(w, h, r) {
    var top = w - 2 * r, side = h - 2 * r, arc = Math.PI * r / 2;
    var segs = [top, arc, side, arc, top, arc, side, arc];
    var total = segs.reduce(function (a, b) { return a + b; }, 0);
    function at(s) {
      s = ((s % total) + total) % total;
      var i = 0;
      while (s > segs[i]) { s -= segs[i]; i++; }
      var t = s / (segs[i] || 1), a;
      switch (i) {
        case 0: return { x: r + s, y: 0, nx: 0, ny: -1 };
        case 1: a = -Math.PI / 2 + t * Math.PI / 2; return { x: w - r + r * Math.cos(a), y: r + r * Math.sin(a), nx: Math.cos(a), ny: Math.sin(a) };
        case 2: return { x: w, y: r + s, nx: 1, ny: 0 };
        case 3: a = t * Math.PI / 2; return { x: w - r + r * Math.cos(a), y: h - r + r * Math.sin(a), nx: Math.cos(a), ny: Math.sin(a) };
        case 4: return { x: w - r - s, y: h, nx: 0, ny: 1 };
        case 5: a = Math.PI / 2 + t * Math.PI / 2; return { x: r + r * Math.cos(a), y: h - r + r * Math.sin(a), nx: Math.cos(a), ny: Math.sin(a) };
        case 6: return { x: 0, y: h - r - s, nx: -1, ny: 0 };
        default: a = Math.PI + t * Math.PI / 2; return { x: r + r * Math.cos(a), y: r + r * Math.sin(a), nx: Math.cos(a), ny: Math.sin(a) };
      }
    }
    return { at: at, total: total, bottomStart: top + arc + side + arc };
  }

  var f1 = function (n) { return Math.round(n * 10) / 10; };

  // A closed Catmull-Rom spline through the points, written as cubic curves.
  function smooth(p) {
    var n = p.length, d = 'M' + f1(p[0].x) + ',' + f1(p[0].y);
    for (var i = 0; i < n; i++) {
      var p0 = p[(i - 1 + n) % n], p1 = p[i], p2 = p[(i + 1) % n], p3 = p[(i + 2) % n];
      d += ' C' + f1(p1.x + (p2.x - p0.x) / 6) + ',' + f1(p1.y + (p2.y - p0.y) / 6) + ' ' +
        f1(p2.x - (p3.x - p1.x) / 6) + ',' + f1(p2.y - (p3.y - p1.y) / 6) + ' ' + f1(p2.x) + ',' + f1(p2.y);
    }
    return d + ' Z';
  }

  function kindOf(el, right) {
    if (right) return 'speech';
    var t = (el.textContent || '').slice(0, 1500);
    if (/unverified|not independently|none is independently/i.test(t) && !/flagged/i.test(t)) return 'thought';
    if (/flagged|reported|epstein|controvers|protest|boycott/i.test(t)) return 'burst';
    return 'speech';
  }

  function shape(w, h, right, kind, seed) {
    var R = rnd(seed), r = Math.max(10, Math.min(30, h / 2.4, w / 3));
    var rm = rim(w, h, r), L = rm.total;
    var mirror = function (x) { return right ? w - x : x; };
    var tailW = right ? 26 : 34, tailH = right ? 30 : 48;
    var x1 = Math.max(r + 8, w * 0.1), xc = x1 + tailW / 2;
    var sTail = rm.bottomStart + (w - r - (right ? w - xc : xc));
    var near = function (s) { return Math.min(1, Math.abs(s - sTail) / 46); };   // 0 at the tail, 1 away from it
    var phase = [R() * 6.28, R() * 6.28, R() * 6.28], amp = [5 + R() * 4, 3 + R() * 3, 2 + R() * 2];
    var out = { fill: [], line: [], extra: '', tail: 0 };

    var pts = [], n, i, s, q, off;
    if (kind === 'burst') {
      n = Math.max(14, Math.round(L / 34)) & ~1;
      for (i = 0; i < n; i++) {
        s = L * i / n; q = rm.at(s);
        off = (i % 2 ? 9 + R() * 8 : R() * 2) * near(s);
        pts.push({ x: q.x + q.nx * off, y: q.y + q.ny * off });
      }
      var d = 'M' + f1(pts[0].x) + ',' + f1(pts[0].y);
      for (i = 1; i < n; i++) d += ' L' + f1(pts[i].x) + ',' + f1(pts[i].y);
      out.fill.push(d + ' Z'); out.line.push(d + ' Z');
    } else if (kind === 'thought') {
      n = Math.max(10, Math.round(L / 52));
      for (i = 0; i < n; i++) { s = L * i / n; q = rm.at(s); pts.push({ x: q.x, y: q.y }); }
      var rr = L / n * 0.62, dd = 'M' + f1(pts[0].x) + ',' + f1(pts[0].y);
      for (i = 0; i < n; i++) { var b = pts[(i + 1) % n]; dd += ' A' + f1(rr) + ',' + f1(rr) + ' 0 0 1 ' + f1(b.x) + ',' + f1(b.y); }
      out.fill.push(dd + ' Z'); out.line.push(dd + ' Z');
      // the thought trail: three small bubbles stepping down and away from the corner
      var cx = mirror(x1 + 8), cy = h + 6;
      [[0, 0, 7], [mirror(x1 - 2) - cx, 15, 5], [mirror(x1 - 12) - cx, 27, 3.4]].forEach(function (c) {
        out.extra += '<circle class="bubble-fill" cx="' + f1(cx + c[0]) + '" cy="' + f1(cy + c[1]) + '" r="' + c[2] + '" fill="url(#GRAD)"/>' +
          '<circle class="bubble-line" cx="' + f1(cx + c[0]) + '" cy="' + f1(cy + c[1]) + '" r="' + c[2] + '" fill="none" stroke="#fff" stroke-width="1.1" pathLength="1"/>';
      });
      out.tail = 34;
      return out;
    } else {
      n = Math.max(10, Math.round(L / 46));
      for (i = 0; i < n; i++) {
        s = L * i / n; q = rm.at(s); var t = s / L * 6.283;
        off = (amp[0] * (0.5 + 0.5 * Math.sin(t * 1 + phase[0])) + amp[1] * (0.5 + 0.5 * Math.sin(t * 2 + phase[1])) + amp[2] * (0.5 + 0.5 * Math.sin(t * 3 + phase[2]))) * near(s);
        pts.push({ x: q.x + q.nx * off, y: q.y + q.ny * off });
      }
      var sp = smooth(pts);
      out.fill.push(sp); out.line.push(sp);
    }

    // The tail: a curved horn off the bottom edge, filled over the rim so the outline does not cross its mouth.
    var yb = h, bx1 = mirror(x1), bx2 = mirror(x1 + tailW), tip = mirror(x1 - 18);
    var left = 'M' + f1(bx1) + ',' + f1(yb) + ' Q' + f1(mirror(x1 + 2)) + ',' + f1(yb + tailH * 0.55) + ' ' + f1(tip) + ',' + f1(yb + tailH) +
      ' Q' + f1(mirror(x1 + tailW - 16)) + ',' + f1(yb + tailH * 0.3) + ' ' + f1(bx2) + ',' + f1(yb);
    out.fill.push(left + ' L' + f1(bx2) + ',' + f1(yb - 10) + ' L' + f1(bx1) + ',' + f1(yb - 10) + ' Z');
    out.line.push(left);
    out.tail = tailH;
    return out;
  }

  /* Like Messages, the colour belongs to the screen, not the bubble: one green to orange to pink wash runs down the
     chat, so each bubble shows the part of it that sits behind it, and it shifts as you scroll. */
  function paint(el) {
    var svg = el.querySelector(':scope>.bubble-svg');
    var stop = svg && svg.querySelector('linearGradient');
    var sc = el.closest('#curatorScrollArea,#curatorDrawerChatBody');
    if (!stop || !sc) return;
    var top = el.getBoundingClientRect().top - sc.getBoundingClientRect().top;
    stop.setAttribute('y1', -top);
    stop.setAttribute('y2', sc.clientHeight - top);
  }

  function build(el) {
    var old = el.querySelector(':scope>.bubble-svg');
    var w = el.offsetWidth, h = el.offsetHeight;
    if (!w || !h) return;
    var right = el.classList.contains('justify-end');
    var seed = +el.dataset.seed || (el.dataset.seed = ++seq * 7919);
    if (!el.dataset.kind) el.dataset.kind = kindOf(el, right);
    var s = shape(w, h, right, el.dataset.kind, seed);
    var id = 'bg' + seed;
    var svg = old || document.createElementNS(NS, 'svg');
    svg.setAttribute('class', 'bubble-svg');
    svg.setAttribute('width', w);
    svg.setAttribute('height', h + s.tail);
    svg.setAttribute('viewBox', '0 0 ' + w + ' ' + (h + s.tail));
    svg.setAttribute('aria-hidden', 'true');
    var line = function (d) { return '<path class="bubble-line" d="' + d + '" fill="none" stroke="#fff" stroke-width="1.1" stroke-linejoin="round" pathLength="1"/>'; };
    var fill = function (d) { return '<path class="bubble-fill" d="' + d + '" fill="url(#' + id + ')"/>'; };
    // blob fill, blob outline, then the tail fill over the rim, then the tail outline
    var body = fill(s.fill[0]) + line(s.line[0]) + (s.fill[1] ? fill(s.fill[1]) + line(s.line[1]) : '') + s.extra.replace(/GRAD/g, id);
    svg.innerHTML = '<defs><linearGradient id="' + id + '" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="0" y2="' + h + '">' +
      '<stop offset="0" stop-color="#7be04a"/><stop offset=".52" stop-color="#e0a23a"/><stop offset="1" stop-color="#ff2fa8"/></linearGradient></defs>' + body;
    if (!old) el.insertBefore(svg, el.firstChild);
    el.classList.add('has-bubble');
    el.style.marginBottom = (s.tail + 18) + 'px';
    if (el.classList.contains('bubble-drawn')) svg.classList.add('is-drawn');
    paint(el);
  }

  function outline(el) {
    el.classList.add('bubble-drawn');
    var svg = el.querySelector(':scope>.bubble-svg');
    if (svg) svg.classList.add('is-drawn');
  }

  var watch = typeof ResizeObserver === 'function' ? new ResizeObserver(function (list) {
    list.forEach(function (e) { if (gossip()) build(e.target); });
  }) : null;

  function bubble(el) {
    if (!gossip() || el.dataset.bubble || !isGossip(el)) return;
    el.dataset.bubble = '1';
    build(el);
    if (watch) watch.observe(el);
  }

  function unbubble(el) {
    if (!el.dataset.bubble) return;
    delete el.dataset.bubble;
    if (watch) watch.unobserve(el);
    var svg = el.querySelector(':scope>.bubble-svg');
    if (svg) svg.remove();
    el.classList.remove('has-bubble', 'bubble-drawn');
    el.style.marginBottom = '';
    delete el.dataset.kind;
  }

  /* Typing: the reply's text nodes are emptied and refilled in reading order. The element keeps its final height,
     so nothing below it jumps, and the bubble outline is drawn once the last character lands. */
  function textNodes(root) {
    var out = [], skip = '.curator-suggest-chip,[data-exclude-speech],button,script,style,svg,.bubble-svg';
    var walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, {
      acceptNode: function (n) {
        if (!n.nodeValue.trim()) return NodeFilter.FILTER_REJECT;
        var p = n.parentElement;
        var hit = p && p.closest(skip);
        return hit && root.contains(hit) ? NodeFilter.FILTER_REJECT : NodeFilter.FILTER_ACCEPT;
      }
    });
    while (walker.nextNode()) out.push(walker.currentNode);
    return out;
  }

  /* Thinking: before a reply types, the turn holds three pulsing dots and the word, then opens into the reply. */
  function think(el, then) {
    if (reduce) { then(); return; }
    var tag = document.createElement('span');
    tag.className = 'thinking';
    tag.setAttribute('role', 'status');
    tag.innerHTML = 'Thinking<i></i><i></i><i></i>';
    el.classList.add('is-thinking');
    el.appendChild(tag);
    setTimeout(function () {
      tag.remove();
      el.classList.remove('is-thinking');
      then();
    }, 1800);
  }

  // Scroll the chat itself, vertically only (scrollIntoView would also nudge the panels around it sideways).
  function follow(node) {
    var sc = node.closest('#curatorScrollArea,#curatorDrawerChatBody');
    if (!sc) return;
    var a = node.getBoundingClientRect(), b = sc.getBoundingClientRect();
    if (a.bottom > b.bottom - 12) sc.scrollTop += a.bottom - b.bottom + 12;
    else if (a.top < b.top + 12) sc.scrollTop -= b.top - a.top + 12;
  }

  function typeIn(el, done, tries) {
    tries = tries || 0;
    var nodes = textNodes(el);
    var full = nodes.map(function (n) { return n.nodeValue; });
    var total = full.reduce(function (a, s) { return a + s.length; }, 0);
    if (!total || reduce) { done(); return; }
    el.style.minHeight = el.offsetHeight + 'px';
    el.classList.add('is-typing');
    var after = el.nextElementSibling;   // follow-up chips sit beside the reply, not in it
    var chips = after && after.querySelector && after.querySelector('.curator-suggest-chip') ? after : null;
    if (chips) chips.style.visibility = 'hidden';
    nodes.forEach(function (n) { n.nodeValue = ''; });
    var duration = Math.min(7000, Math.max(1000, total * 24)), start = performance.now(), shown = 0;
    function frame(now) {
      // The app may rewrite a reply's markup once it has arrived; when the nodes being typed are gone, start over on the new ones.
      if (nodes.length && !nodes[0].isConnected) {
        el.classList.remove('is-typing'); el.style.minHeight = '';
        if (tries < 3) setTimeout(function () { typeIn(el, done, tries + 1); }, 120); else done();
        return;
      }
      var upto = Math.min(total, Math.ceil(total * (now - start) / duration));
      if (upto !== shown) {
        shown = upto;
        var left = upto, tip = null;
        for (var i = 0; i < nodes.length; i++) {
          var n = Math.max(0, Math.min(full[i].length, left));
          if (nodes[i].nodeValue.length !== n) nodes[i].nodeValue = full[i].slice(0, n);
          if (n > 0 && n < full[i].length) tip = nodes[i].parentElement;
          left -= full[i].length;
        }
        // Follow the text as it is typed so the reader is never looking at an empty bubble.
        if (tip) follow(tip);
      }
      if (shown < total) requestAnimationFrame(frame);
      else { el.classList.remove('is-typing'); el.style.minHeight = ''; if (chips) chips.style.visibility = ''; done(); }
    }
    requestAnimationFrame(frame);
  }

  function arrive(list) {
    var fresh = list.filter(function (el) { return !el.dataset.arrived; });
    fresh.forEach(function (el) { el.dataset.arrived = '1'; bubble(el); });
    if (!fresh.length) return;
    // The newest reply that is on screen after a beat is typed (the phone drawer keeps a hidden copy of every reply);
    // a whole restored history, or the earlier turns of a batch, appear at once.
    var many = fresh.length > 6;
    setTimeout(function () {
      var live = fresh.filter(function (el) { return el.isConnected; });
      var shown = live.filter(function (el) { return el.getClientRects().length; });
      var replies = shown.filter(function (el) { return el.classList.contains('curator-message-wrap'); });
      var target = many ? null : replies[replies.length - 1];
      live.forEach(function (el) {
        if (el === target) think(el, function () { typeIn(el, function () { outline(el); }); });
        else outline(el);
      });
    }, 160);
  }

  function scan() {
    var all = [].slice.call(document.querySelectorAll(SEL));
    if (gossip()) all.forEach(function (el) { if (!el.dataset.bubble && !el.dataset.born) { bubble(el); outline(el); } });
    else all.forEach(unbubble);
  }

  function repaintAll() {
    [].forEach.call(document.querySelectorAll('.has-bubble'), paint);
  }

  function observe() {
    ['curatorScrollArea', 'curatorDrawerChatBody'].forEach(function (id) {
      var sc = document.getElementById(id);
      if (sc) sc.addEventListener('scroll', function () { requestAnimationFrame(repaintAll); }, { passive: true });
    });
    window.addEventListener('resize', repaintAll);
    var pending = [];
    var flush = function () { var l = pending; pending = []; arrive(l); };
    var mo = new MutationObserver(function (muts) {
      muts.forEach(function (m) {
        [].forEach.call(m.addedNodes, function (n) {
          if (n.nodeType === 1 && n.matches && n.matches(SEL)) { n.dataset.born = '1'; pending.push(n); }
        });
      });
      if (pending.length) requestAnimationFrame(flush);
    });
    ['curatorMessages', 'curatorDrawerLiveStream'].forEach(function (id) {
      var box = document.getElementById(id);
      if (box) mo.observe(box, { childList: true });
    });
    new MutationObserver(scan).observe(document.body, { attributes: true, attributeFilter: ['class'] });
    scan();
  }

  /* Hairlines on load: the app's main rules are covered by a copy that draws itself in, then handed back. */
  function drawLines() {
    if (reduce) return;
    // A new release makes the service worker reload the page once; a reload right after a draw must not draw again.
    try {
      var last = +sessionStorage.getItem('atlas-lines') || 0;
      if (Date.now() - last < 20000) return;
      sessionStorage.setItem('atlas-lines', String(Date.now()));
    } catch (e) {}
    var root = document.documentElement;
    var spec = [
      ['header', 'bottom', 'x'],
      ['#workspaceContextTabBar', 'bottom', 'x'],
      ['#globeSplitter', 'left', 'y'],
      ['#workInputCard', 'top', 'x'],
      ['#mobileStickyComposer', 'top', 'x']
    ];
    var lines = [];
    spec.forEach(function (s, i) {
      var el = [].slice.call(document.querySelectorAll(s[0])).filter(function (e) { var b = e.getBoundingClientRect(); return b.width && b.height; })[0];
      if (!el) return;
      var r = el.getBoundingClientRect(), cs = getComputedStyle(el);
      if (!r.width || !r.height) return;
      var colour = cs['border' + s[1].charAt(0).toUpperCase() + s[1].slice(1) + 'Color'];
      lines.push({ s: s, r: r, colour: colour, i: i });
    });
    if (!lines.length) return;
    var layer = document.createElement('div');
    layer.className = 'lines-layer';
    lines.forEach(function (l) {
      var d = document.createElement('i');
      var r = l.r, horiz = l.s[2] === 'x';
      d.style.cssText = 'position:fixed;background:' + l.colour + ';animation-delay:' + (l.i * 240) + 'ms;' +
        (horiz ? 'left:' + r.left + 'px;width:' + r.width + 'px;height:1px;top:' + (l.s[1] === 'top' ? r.top : r.bottom - 1) + 'px;transform-origin:left;' + 'animation-name:line-x'
               : 'top:' + r.top + 'px;height:' + r.height + 'px;width:1px;left:' + r.left + 'px;transform-origin:top;animation-name:line-y');
      layer.appendChild(d);
    });
    root.classList.add('lines-drawing');
    document.body.appendChild(layer);
    setTimeout(function () { root.classList.remove('lines-drawing'); layer.remove(); }, 3200);
  }

  function start() { observe(); setTimeout(drawLines, 1500); }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start); else start();
})();
