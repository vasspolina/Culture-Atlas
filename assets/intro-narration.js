/* The empty chat narrates what the atlas does (user, 13 Nov 2026: "make chat at the beginning explain while typing what
   Leaving it on the table is doing as narration"). Four sentences are typed out under the chat's title, one after another,
   with the suggested questions under them. The diagram that once built beside them was taken out the same day (user: "dont do
   that illustration add questions prompts underneath").

   Layout never moves while it types: every sentence is laid out at full length from the start, and the untyped letters
   are only hidden, so the question list under it is measured once against its final height. A screen reader gets the
   whole text at once from a visually hidden copy; the typed copy is aria-hidden. With reduced motion the text appears
   complete. The typing stops as soon as the greeting leaves the page (the first question). */
(function () {
  'use strict';

  var LINES = [
    'Leaving it on the table looks up who funds museums and cultural spaces.',
    'Each record names the funders it can source – public money, companies and foundations – and links every fact to where it comes from.',
    'A grade from A to F says how much of that money the record shows.',
    'Ask below about a space, a city or a funder.'
  ];
  var CHAR_MS = 22;      // about 45 characters a second: quick enough to read along, slow enough to be seen typing
  var PAUSE_MS = 420;    // a breath between sentences


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
    box.innerHTML = sr + '<div class="intro-text" aria-hidden="true">' + shown + '</div>';
    return box;
  }

  function finish(box) {
    box.querySelectorAll('.intro-line').forEach(function (p, i) {
      p.querySelector('.intro-typed').textContent = LINES[i];
      p.querySelector('.intro-rest').textContent = '';
    });
    box.classList.add('is-done');
  }

  function run(box) {
    if (reduced()) { finish(box); return; }
    var line = 0, ch = 0;
    var lines = box.querySelectorAll('.intro-line');
    function tick() {
      if (!box.isConnected) return;               // the greeting is gone: the visitor has asked something
      var p = lines[line];
      if (!p) { box.classList.add('is-done'); return; }
      if (ch === 0) p.classList.add('is-typing');
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
