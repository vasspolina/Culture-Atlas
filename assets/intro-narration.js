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
    'Each record names the funders it can source, from public money, companies and foundations, and links every fact to where it comes from.',
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

  // The typing runs on from the last sentence into the suggested questions (user, 14 Nov 2026: "combine the intro and
  // suggestions so it all looks like intro and types like intro"). The questions are the buttons index.html renders into
  // the same greeting; they stay buttons. While the typing runs the greeting carries .intro-pending, which hides (but
  // still lays out) every question not yet reached, so nothing moves. index.html renders the list again on a resize and
  // swaps single questions after checking them: the observer marks the ones already typed before the next paint, and a
  // question replaced while it is being typed is started again in its place.
  function run(host, box) {
    if (reduced()) { finish(box); return; }
    var line = 0, ch = 0;
    var lines = box.querySelectorAll('.intro-line');
    var asked = 0, cur = null, text = '', waited = 0;
    var questions = function () { return host.querySelectorAll('.starter-prompt'); };
    var mark = function () {
      var list = questions();
      for (var i = 0; i < asked && i < list.length; i++) list[i].classList.add('is-typed');
    };
    var watch = typeof MutationObserver === 'function' ? new MutationObserver(mark) : null;
    function end() {
      if (watch) watch.disconnect();
      host.classList.remove('intro-pending');
      box.classList.add('is-done');
    }
    host.classList.add('intro-pending');
    if (watch) watch.observe(host, { childList: true, subtree: true });

    function ask() {
      if (!box.isConnected) { end(); return; }
      if (cur && !cur.isConnected) cur = null;
      if (!cur) {
        var list = questions();
        mark();
        cur = list[asked];
        if (!cur) {
          // none left, or the list is not rendered yet: wait a little for it, then stop
          if (list.length || waited > 3000) { end(); return; }
          waited += 100; setTimeout(ask, 100); return;
        }
        var span = cur.querySelector('.sp-text') || cur;
        text = span.textContent;
        ch = 0;
        cur.setAttribute('aria-label', text);   // the untyped letters are hidden, so the name is given whole
        span.innerHTML = '<span class="intro-typed"></span><span class="intro-rest"></span>';
        span.lastChild.textContent = text;
        cur.classList.add('is-typed', 'is-typing');
      }
      ch++;
      cur.querySelector('.intro-typed').textContent = text.slice(0, ch);
      cur.querySelector('.intro-rest').textContent = text.slice(ch);
      if (ch < text.length) { setTimeout(ask, CHAR_MS); return; }
      (cur.querySelector('.sp-text') || cur).textContent = text;
      cur.classList.remove('is-typing');
      cur = null; asked++;
      setTimeout(ask, PAUSE_MS);
    }

    function tick() {
      if (!box.isConnected) { end(); return; }    // the greeting is gone: the visitor has asked something
      var p = lines[line];
      if (!p) { ch = 0; ask(); return; }
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
      run(host, box);
    });
  };
})();
