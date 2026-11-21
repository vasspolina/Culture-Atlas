// Tab suggestions in the chat box (user, 17 Nov 2026: "add tab suggestions to chat window"). While a question is typed, the
// rest of a likely question or of a space's name is shown in grey after the caret; Tab (or the right arrow at the end of the
// text) takes it, Escape puts it away for what is typed, and on a phone a tap on the grey words takes it. Nothing is sent
// anywhere to make a suggestion: it comes from the questions below and the names, aliases and cities already on the page.
// The pure part (`suggest`, `buildIndex`) has no DOM, so tests/tab-suggest.test.mjs loads it in Node.
(function (root) {
  // Whole questions, matched from the start of the box. The first five are the suggestion chips' own questions.
  var QUESTIONS = [
    'Who funds MoMA?',
    'Which museums take oil and gas money?',
    'Which museums still carry the Sackler name?',
    'Which museums have arms-industry donors?',
    'Which museums near me are flagged, and why?',
    'Which museums are funded by the state?',
    'Which museums have a billionaire on the board?',
    'What changed in the news this week?',
    'Where does the money come from?',
    'Show me museums in Berlin',
    'Show me museums in London',
    'Show me museums in New York'
  ];
  // A fragment that is only one of these words is too common to complete: "the" would finish as "The Bowes Museum".
  var STOP = { the: 1, who: 1, what: 1, which: 1, where: 1, when: 1, why: 1, how: 1, and: 1, are: 1, for: 1, from: 1,
    has: 1, have: 1, does: 1, did: 1, show: 1, tell: 1, about: 1, with: 1, take: 1, takes: 1, money: 1, museum: 1,
    museums: 1, gallery: 1, art: 1, funds: 1, fund: 1, near: 1, this: 1, that: 1, any: 1, all: 1, most: 1, more: 1 };

  // Accents off and lower case, one character for one, so an index into the folded text is an index into the original.
  function fold(s) {
    var out = '';
    for (var i = 0; i < s.length; i++) {
      var c = s[i], f = c.normalize ? c.normalize('NFD').replace(/[̀-ͯ]/g, '') : c;
      out += (f.length === 1 ? f : c).toLowerCase();
    }
    return out;
  }

  // Names, the properly cased aliases (the lower-case ones are search keys, not names) and cities, once each.
  function buildIndex(list) {
    var seen = {}, items = [];
    function add(s) {
      if (typeof s !== 'string') return;
      s = s.trim();
      if (s.length < 3) return;
      var k = fold(s);
      if (seen[k]) return;
      seen[k] = 1;
      items.push({ text: s, key: k });
    }
    (list || []).forEach(function (r) {
      if (!r) return;
      add(r.name);
      (Array.isArray(r.aliases) ? r.aliases : []).forEach(function (a) { if (/[A-Z]/.test(a)) add(a); });
      add(r.city);
    });
    // Shortest first: the name a person is most likely typing is the one that needs the fewest letters to tell apart.
    items.sort(function (a, b) { return a.text.length - b.text.length || (a.key < b.key ? -1 : 1); });
    return items;
  }

  // The rest of the text to show after what is typed, or '' when there is nothing worth showing.
  function suggest(text, index) {
    if (typeof text !== 'string' || text.trim().length < 2 || /\n/.test(text)) return '';
    var t = fold(text);
    for (var q = 0; q < QUESTIONS.length; q++) {
      var fq = fold(QUESTIONS[q]);
      if (fq.length > t.length && fq.indexOf(t) === 0) return QUESTIONS[q].slice(text.length);
    }
    if (/\s$/.test(text) || !index || !index.length) return '';
    // Word starts among the last six words, longest fragment first, so "Tate Mo" finishes as a name and not as "Mo…".
    var starts = [], re = /(^|[\s"'(“‘])(?=\S)/g, m;
    while ((m = re.exec(text))) { starts.push(m.index + m[1].length); if (re.lastIndex === m.index) re.lastIndex++; }
    starts = starts.slice(-6);
    for (var s = 0; s < starts.length; s++) {
      var frag = t.slice(starts[s]);
      var letters = frag.replace(/[^a-z0-9]/g, '');
      if (letters.length < 3) continue;
      if (!/\s/.test(frag) && STOP[frag]) continue;
      for (var i = 0; i < index.length; i++) {
        var it = index[i];
        if (it.key.length > frag.length && it.key.indexOf(frag) === 0) return it.text.slice(frag.length);
      }
    }
    return '';
  }

  var api = { suggest: suggest, buildIndex: buildIndex, fold: fold, QUESTIONS: QUESTIONS };
  root.AtlasTabSuggest = api;

  if (typeof document === 'undefined') return;

  var index = null;
  function getIndex() {
    if (!index) {
      var list = null;
      try { list = typeof ALL_INSTITUTIONS !== 'undefined' ? ALL_INSTITUTIONS : root.ALL_INSTITUTIONS; } catch (e) { list = null; }
      index = buildIndex(list || []);
    }
    return index;
  }

  // One polite live region for both boxes: a screen reader hears the suggestion once the typing pauses.
  var live = null, liveTimer = 0;
  function announce(msg) {
    if (!live) {
      live = document.createElement('div');
      live.setAttribute('aria-live', 'polite');
      live.className = 'tab-suggest-live';
      document.body.appendChild(live);
    }
    clearTimeout(liveTimer);
    liveTimer = setTimeout(function () { live.textContent = msg; }, msg ? 900 : 0);
  }

  var COPY = ['fontFamily', 'fontSize', 'fontWeight', 'fontStyle', 'fontFeatureSettings', 'fontVariationSettings',
    'fontKerning', 'letterSpacing', 'wordSpacing', 'lineHeight', 'textIndent', 'textTransform', 'textRendering',
    'paddingTop', 'paddingRight', 'paddingBottom', 'paddingLeft', 'borderTopWidth', 'borderRightWidth',
    'borderBottomWidth', 'borderLeftWidth', 'boxSizing', 'tabSize', 'direction'];

  function put(el, prop, value) { el.style.setProperty(prop.replace(/[A-Z]/g, function (c) { return '-' + c.toLowerCase(); }), value, 'important'); }
  var TYPE = COPY.filter(function (p) { return !/^(padding|border|boxSizing)/.test(p); });

  function bind(box) {
    if (!box || box.dataset.tabSuggest) return;
    box.dataset.tabSuggest = '1';
    var parent = box.parentNode;
    if (getComputedStyle(parent).position === 'static') parent.style.position = 'relative';
    // A copy of the box laid over it: the typed text is invisible in it, only the grey rest shows, so the box itself is untouched.
    var mirror = document.createElement('div');
    mirror.className = 'tab-suggest-mirror';
    mirror.setAttribute('aria-hidden', 'true');
    var typed = document.createElement('span');
    typed.className = 'tab-suggest-typed';
    var ghost = document.createElement('span');
    ghost.className = 'tab-suggest-ghost';
    mirror.appendChild(typed);
    mirror.appendChild(ghost);
    parent.appendChild(mirror);
    // Set here as well as in atlas.css, inline and !important, for the same reason as the type below.
    [['position', 'absolute'], ['pointer-events', 'none'], ['overflow', 'hidden'], ['white-space', 'pre-wrap'],
      ['overflow-wrap', 'break-word'], ['background', 'transparent'], ['border-color', 'transparent'],
      ['border-style', 'solid'], ['margin', '0'], ['z-index', '2']].forEach(function (d) { mirror.style.setProperty(d[0], d[1], 'important'); });
    typed.style.setProperty('color', 'transparent', 'important');
    ghost.style.setProperty('color', 'color-mix(in srgb, var(--ink) 58%, var(--paper))', 'important');
    ghost.style.setProperty('pointer-events', 'auto', 'important');
    ghost.style.setProperty('cursor', 'pointer', 'important');

    var rest = '', dismissedFor = null, composing = false;

    function hide() { rest = ''; mirror.hidden = true; mirror.style.setProperty('display', 'none', 'important'); box.removeAttribute('aria-describedby'); announce(''); }

    function place() {
      var cs = getComputedStyle(box);
      // The page's stylesheet sets type with !important on every element, spans included; only an inline !important outranks
      // it, so the copy and its two runs take the box's own computed type that way.
      COPY.forEach(function (p) { put(mirror, p, cs[p]); });
      [typed, ghost].forEach(function (el) {
        TYPE.forEach(function (p) { put(el, p, cs[p]); });
        ['padding', 'margin', 'border-width'].forEach(function (p) { el.style.setProperty(p, '0', 'important'); });
      });
      mirror.style.top = box.offsetTop + 'px';
      mirror.style.left = box.offsetLeft + 'px';
      mirror.style.width = box.offsetWidth + 'px';
      mirror.style.height = box.offsetHeight + 'px';
      mirror.scrollTop = box.scrollTop;
    }

    function update() {
      var v = box.value;
      var atEnd = box.selectionStart === v.length && box.selectionEnd === v.length;
      var off = document.activeElement !== box || !atEnd || composing || v === dismissedFor ||
        document.body.classList.contains('chat-input-mode-active') || box.offsetParent === null;
      var next = off ? '' : suggest(v, getIndex());
      if (!next) { hide(); return; }
      var changed = next !== rest;
      rest = next;
      typed.textContent = v;
      ghost.textContent = rest;
      mirror.hidden = false; mirror.style.setProperty('display', 'block', 'important');
      place();
      if (changed) announce('Suggestion: ' + v + rest + '. Press Tab to accept.');
    }

    function accept() {
      if (!rest) return false;
      box.value = box.value + rest;
      box.setSelectionRange(box.value.length, box.value.length);
      hide();
      box.dispatchEvent(new Event('input', { bubbles: true }));
      return true;
    }

    box.addEventListener('keydown', function (e) {
      if (!rest) return;
      if (e.key === 'Tab' && !e.shiftKey && !e.altKey && !e.ctrlKey && !e.metaKey) { if (accept()) e.preventDefault(); }
      else if (e.key === 'ArrowRight' && !e.shiftKey && box.selectionStart === box.value.length) { if (accept()) e.preventDefault(); }
      else if (e.key === 'Escape') { dismissedFor = box.value; hide(); e.stopPropagation(); }
    });
    box.addEventListener('input', function () { if (box.value !== dismissedFor) dismissedFor = null; update(); });
    box.addEventListener('compositionstart', function () { composing = true; hide(); });
    box.addEventListener('compositionend', function () { composing = false; update(); });
    ['focus', 'click', 'keyup', 'select'].forEach(function (ev) { box.addEventListener(ev, update); });
    box.addEventListener('blur', hide);
    box.addEventListener('scroll', function () { mirror.scrollTop = box.scrollTop; });
    window.addEventListener('resize', function () { if (rest) place(); });
    // A tap on the grey words takes them. pointerdown, and kept from taking focus, so the keyboard stays up on a phone.
    ghost.addEventListener('pointerdown', function (e) { e.preventDefault(); accept(); box.focus(); });
    hide();
  }

  function start() { bind(document.getElementById('workInput')); bind(document.getElementById('chat-input')); }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start);
  else start();
})(typeof window !== 'undefined' ? window : globalThis);
