/* The empty chat narrates what the atlas does (user, 13 Nov 2026: "make chat at the beginning explain while typing what
   Leaving it on the table is doing as narration and add visual").

   Four sentences are typed out under the chat's title, one after another, and a small diagram beside them builds in step:
   a space, then the funders around it with a line to each and a source mark on each line, then the grade in the space's
   dot, then the whole map at rest. The diagram uses the money map's own shapes (square for public funding, hexagon for a
   company, triangle for a foundation) and the clean-tier colour for the space.

   Layout never moves while it types: every sentence is laid out at full length from the start, and the untyped letters
   are only hidden, so the question list under it is measured once against its final height. A screen reader gets the
   whole text at once from a visually hidden copy; the typed copy and the diagram are aria-hidden. With reduced motion the
   text and the diagram appear complete. The typing stops as soon as the greeting leaves the page (the first question). */
(function () {
  'use strict';

  var LINES = [
    'Leaving it on the table looks up who funds museums and cultural spaces.',
    'Each record names the funders it can source – public money, companies and foundations – and links every fact to where it comes from.',
    'A grade from A to F says how much of that money the record shows.',
    'Ask below about a space, a city or a funder.'
  ];
  var CHAR_MS = 22;      // about 45 characters a second: quick enough to read along, slow enough to be seen typing
  var PAUSE_MS = 420;    // a breath between sentences, while the diagram takes its next step

  var SVG = '' +
    '<svg class="intro-visual" viewBox="0 0 220 160" aria-hidden="true" focusable="false">' +
      // lines from the space to each funder, drawn in at step 2
      '<g class="iv-step iv-2">' +
        '<line class="iv-line" x1="110" y1="80" x2="40" y2="36"/>' +
        '<line class="iv-line" x1="110" y1="80" x2="184" y2="40"/>' +
        '<line class="iv-line" x1="110" y1="80" x2="112" y2="142"/>' +
        // a source mark on each line: a small page with a folded corner
        '<g class="iv-src"><path d="M68 52h8l3 3v9h-11z"/><path d="M76 52v3h3"/></g>' +
        '<g class="iv-src"><path d="M141 56h8l3 3v9h-11z"/><path d="M149 56v3h3"/></g>' +
        '<g class="iv-src"><path d="M104 104h8l3 3v9h-11z"/><path d="M112 104v3h3"/></g>' +
      '</g>' +
      // funders: public funding (square), a company (hexagon), a foundation (triangle)
      '<g class="iv-step iv-2 iv-funders">' +
        '<rect x="28" y="24" width="24" height="24"/>' +
        '<polygon points="184,26 196,33 196,47 184,54 172,47 172,33"/>' +
        '<polygon points="112,128 125,150 99,150"/>' +
      '</g>' +
      // the space, at step 1
      '<g class="iv-step iv-1">' +
        '<circle class="iv-space" cx="110" cy="80" r="17"/>' +
      '</g>' +
      // its grade, at step 3
      '<g class="iv-step iv-3">' +
        '<text class="iv-grade" x="110" y="80" text-anchor="middle" dominant-baseline="central">B</text>' +
      '</g>' +
    '</svg>';

  var reduced = function () {
    try { return window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches; } catch (e) { return false; }
  };

  function build() {
    var box = document.createElement('div');
    box.className = 'intro-narration';
    box.setAttribute('data-no-typeset', '');   // typeset.js leaves it alone: the spans are rewritten letter by letter
    var sr = '<p class="sr-only">' + LINES.join(' ') + '</p>';
    var shown = LINES.map(function (t, i) {
      return '<p class="intro-line" data-i="' + i + '"><span class="intro-typed"></span><span class="intro-rest">' + t + '</span></p>';
    }).join('');
    box.innerHTML = sr + '<div class="intro-text" aria-hidden="true">' + shown + '</div>' + SVG;
    return box;
  }

  function finish(box) {
    box.querySelectorAll('.intro-line').forEach(function (p, i) {
      p.querySelector('.intro-typed').textContent = LINES[i];
      p.querySelector('.intro-rest').textContent = '';
    });
    box.setAttribute('data-step', '4');
    box.classList.add('is-done');
  }

  function run(box) {
    if (reduced()) { finish(box); return; }
    var line = 0, ch = 0;
    box.setAttribute('data-step', '0');
    var lines = box.querySelectorAll('.intro-line');
    function tick() {
      if (!box.isConnected) return;               // the greeting is gone: the visitor has asked something
      var p = lines[line];
      if (!p) { box.classList.add('is-done'); return; }
      if (ch === 0) { p.classList.add('is-typing'); box.setAttribute('data-step', String(line + 1)); }
      ch++;
      p.querySelector('.intro-typed').textContent = LINES[line].slice(0, ch);
      p.querySelector('.intro-rest').textContent = LINES[line].slice(ch);
      if (ch < LINES[line].length) { setTimeout(tick, CHAR_MS); return; }
      p.classList.remove('is-typing');
      line++; ch = 0;
      setTimeout(tick, PAUSE_MS);
    }
    setTimeout(tick, 300);
  }

  // Puts the narration under the title of each empty-chat greeting (the desktop column and the phone drawer) that does not
  // have one yet, and starts it. Called by initCuratorConversation before the question list is laid out.
  window.atlasNarrateIntro = function () {
    ['curatorHeroGreeting', 'curatorDrawerGreeting'].forEach(function (id) {
      var host = document.getElementById(id);
      if (!host) return;
      var old = host.querySelector('.intro-narration');
      if (old) old.remove();
      var box = build();
      var title = host.querySelector('h1');
      if (title && title.nextSibling) host.insertBefore(box, title.nextSibling);
      else host.insertBefore(box, host.firstChild);
      run(box);
    });
  };
})();
