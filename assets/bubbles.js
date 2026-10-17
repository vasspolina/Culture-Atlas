/* Chat motion: gossip speech bubbles drawn as SVG that fit their text, a typing reveal for new replies,
   and the app's hairlines drawn in on load. No dependencies; every effect is skipped under reduced motion. */
(function () {
  'use strict';
  var NS = 'http://www.w3.org/2000/svg';
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var SEL = '#curatorMessages>.curator-message-wrap,#curatorMessages>.justify-end,#curatorDrawerLiveStream>.curator-message-wrap,#curatorDrawerLiveStream>.justify-end';
  var seq = 0;

  function gossip() { return document.body.classList.contains('gossip-mode-active'); }

  /* Apple Messages shape: a rounded rectangle with one small curved tail on the bottom corner, left for replies and
     right for your own turns. The tail hooks out past the edge, so the bubble itself keeps its size. */
  function shape(w, h, right) {
    var r = Math.min(18, h / 2);
    var x = function (v) { return right ? w - v : v; };
    var d = 'M' + x(r) + ',0';
    d += ' H' + x(w - r);
    d += ' Q' + x(w) + ',0 ' + x(w) + ',' + r;
    d += ' V' + (h - r);
    d += ' Q' + x(w) + ',' + h + ' ' + x(w - r) + ',' + h;
    d += ' H' + x(16);
    d += ' C' + x(10) + ',' + h + ' ' + x(4) + ',' + (h - 1) + ' ' + x(-6) + ',' + h;
    d += ' C' + x(-1) + ',' + (h - 4) + ' ' + x(0) + ',' + (h - 9) + ' ' + x(0) + ',' + (h - 14);
    d += ' V' + r;
    d += ' Q' + x(0) + ',0 ' + x(r) + ',0 Z';
    return { d: d };
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
    var seed = +el.dataset.seed || (el.dataset.seed = ++seq);
    var s = shape(w, h, right);
    var id = 'bg' + seed;
    var svg = old || document.createElementNS(NS, 'svg');
    svg.setAttribute('class', 'bubble-svg');
    svg.setAttribute('width', w);
    svg.setAttribute('height', h);
    svg.setAttribute('viewBox', '0 0 ' + w + ' ' + h);
    svg.setAttribute('aria-hidden', 'true');
    svg.innerHTML = '<defs><linearGradient id="' + id + '" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="0" y2="' + h + '">' +
      '<stop offset="0" stop-color="#7be04a"/><stop offset=".52" stop-color="#e0a23a"/><stop offset="1" stop-color="#ff2fa8"/></linearGradient></defs>' +
      '<path class="bubble-fill" d="' + s.d + '" fill="url(#' + id + ')"/>' +
      '<path class="bubble-line" d="' + s.d + '" fill="none" stroke="#000" stroke-width="1.1" stroke-linejoin="round" pathLength="1"/>';
    if (!old) el.insertBefore(svg, el.firstChild);
    el.classList.add('has-bubble');
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
    if (!gossip() || el.dataset.bubble) return;
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
    nodes.forEach(function (n) { n.nodeValue = ''; });
    var duration = Math.min(3200, Math.max(500, total * 11)), start = performance.now(), shown = 0;
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
      else { el.classList.remove('is-typing'); el.style.minHeight = ''; done(); }
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
        if (el === target) typeIn(el, function () { outline(el); });
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
      d.style.cssText = 'position:fixed;background:' + l.colour + ';animation-delay:' + (l.i * 110) + 'ms;' +
        (horiz ? 'left:' + r.left + 'px;width:' + r.width + 'px;height:1px;top:' + (l.s[1] === 'top' ? r.top : r.bottom - 1) + 'px;transform-origin:left;' + 'animation-name:line-x'
               : 'top:' + r.top + 'px;height:' + r.height + 'px;width:1px;left:' + r.left + 'px;transform-origin:top;animation-name:line-y');
      layer.appendChild(d);
    });
    root.classList.add('lines-drawing');
    document.body.appendChild(layer);
    setTimeout(function () { root.classList.remove('lines-drawing'); layer.remove(); }, 1500);
  }

  function start() { observe(); setTimeout(drawLines, 120); }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start); else start();
})();
