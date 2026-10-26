/* Detail typography for the chat, after Jost Hochuli, "Detail in typography" (Hyphen Press, 2008).
   Page and figure numbers below are the book's. The pass runs on text nodes only: never on hrefs, code, inputs,
   a link whose words are a URL, or data values. It is safe to run twice.

   What each rule serves:
   - Dashes (p.36, figs 47-50). One sign for the whole product: the en dash with a word space either side, the book's
     own practice. Measured in Jokker Regular the hyphen is 0.36 em wide and the en dash 0.557 em (advance widths; Gstaad
     measured 0.39 and 0.59, so the ratio holds), far enough apart that the spaced en dash reads as a dash, so the unspaced em dash (0.93 em) is not
     needed. Every other form (" - ", "--", "—", " — ") is normalised to it; the space before it is non-breaking so no
     line begins with a dash (p.36), and both spaces are the same width (the font's NBSP equals its space).
     Ranges and spans take a closed en dash (fig 49): 10:00–18:00, Wed–Fri, 1965–70, 2024–25;
     a word joiner after it keeps a range on one line.
   - Quotation marks (p.36-38, fig 53). Single marks for the frequent quotation, double for a quotation inside one,
     in the language's own shapes (de „ “, fr « »). Punctuation that is not part of a short quoted phrase goes outside:
     ‘not stated’, not “not stated,”. Apostrophes are ’ (p.38).
   - Ellipsis (p.36, fig 46). One sign, …, never three points; a word space either side when it stands for words
     (the one before non-breaking), closed when part of a word is omitted; no full point after it.
   - Abbreviations and initials (figs 42-43). A reduced space after an abbreviation point (e.g. Prof. Dr.), a thin
     space between initials and a word space before the surname. A figure keeps its unit and a currency code its
     amount (p.37), on a non-breaking space.
   - Figures (p.41-44, figs 45, 52, 57, 59). The multiplication sign in running text is the typeface's × with a space
     a little narrower than a word space either side (150 × 105 cm). The face has no old-style or tabular figures,
     so nothing is asked of it there.
   - Capitals in running text (p.39-40, fig 54). A word in capitals (UNESCO, EU, a shouted word) is wrapped in .abbr,
     which atlas.css sets one size smaller and evenly letterspaced; a lowercase word is never letterspaced (p.25).
   - The word (p.23-31, figs 23-35), letterspacing study of PP Neue Gstaad as served (not re-measured on Jokker); values are in atlas.css.
     Measured: regular n has 139/1000 em of space against a 258/1000 counter (0.54), o 80 against 320 (0.25), H-H 170,
     O-O 94, H-O 132; Compact Bold n 101 against 165. The face is spaced on the counter principle already (fig 25), and
     it is not a narrow cut (n ink / x-height 0.87), so the fig 27 exception does not apply at 14px: lowercase gets
     letter-spacing 0 at every size in the chat. The old .01em also switched off the font's fi fl ff ffi ffl ligatures
     (a browser drops ligatures under any letter-spacing, fig 35); at 0 they set and kerning stays on (font-kerning:
     normal). Lowercase is never tracked (p.25). Capitals (UNESCO, a shouted phrase, the CA/ME marks) start from 0, which
     is dense beside the big counters of O, C, G, Q, so they take .06em, even and not wider (.10em lets the word fall
     apart, figs 28-30); the 22px Compact Bold capitals in headings take .02em; display sizes stay at 0, which is
     already proportionally tighter as the type grows (fig 26). Kerning checked in the browser: Ta Te To -137..-140,
     Ve Vo -70, Wo -52, Ya Ye Yo -116..-125, AV -89, LT -144, r. r, y. y, -72..-83 per 1000 em; f followed by an
     accented letter (fé fö fř fł) does not collide, and f) f! f? have no pair value but a visible gap, so none was added.
     The face has no thin space, narrow no-break space or word joiner, so those are realised as spans (see decorate()).
   The measure, the rag, hyphenation, list markers, emphasis and paragraph indents are CSS: see "detail typography"
   in assets/atlas.css. */
(function () {
  'use strict';
  var SKIP = { SCRIPT: 1, STYLE: 1, CODE: 1, PRE: 1, TEXTAREA: 1, INPUT: 1, SVG: 1, CANVAS: 1, KBD: 1, SAMP: 1 };
  var NBSP = ' ', THIN = ' ', NNBSP = ' ';

  // The language's marks (fig 53): outer open/close, inner open/close.
  var MARKS = {
    en: ['‘', '’', '“', '”'],
    de: ['„', '“', '‚', '‘'],
    fr: ['«' + NNBSP, NNBSP + '»', '“', '”'],
    it: ['«', '»', '“', '”'],
    es: ['«', '»', '“', '”'],
    nl: ['‘', '’', '“', '”'],
    da: ['»', '«', '„', '“'],
    sv: ['”', '”', '’', '’'],
    'de-CH': ['«', '»', '‹', '›']
  };
  function marksFor(lang) {
    lang = String(lang || 'en');
    return MARKS[lang] || MARKS[lang.split('-')[0]] || MARKS.en;
  }
  var esc = function (s) { return s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'); };

  // Quotation marks: straight marks are paired by position, then the levels are set for the language.
  function quotes(s, lang) {
    var m = marksFor(lang), O = m[0], C = m[1], IO = m[2], IC = m[3];
    var OPEN = '\u0001', CLOSE = '\u0002', IOPEN = '\u0003', NOPEN = '\u0005', NCLOSE = '\u0006';
    s = s
      // Straight doubles, and curly doubles the model already wrote, become the outer pair.
      .replace(/(^|[\s(\[–—‘])["“]/g, '$1' + OPEN).replace(/["“”]/g, CLOSE)
      // A straight single opening a word is an opening mark; any other single is an apostrophe. ’90s is an apostrophe.
      .replace(/(^|[\s(\[–—\u0001])'(?=[^\s\d])/g, '$1' + IOPEN).replace(/'/g, '’');
    // Singles that the model wrote as the frequent quotation ('the Bathtub') are outer marks too, so the text uses one
    // level consistently; only a single pair inside an outer pair is the inner level (p.37).
    s = s.replace(new RegExp(OPEN + '([^' + OPEN + CLOSE + ']*)' + CLOSE, 'g'), function (_, inner) {
      inner = inner.replace(/\u0003([^\u0003’]*?)’(?=[\s.,;:!?)\]]|$)/g, NOPEN + '$1' + NCLOSE)
                   .replace(/‘([^‘’]*?)’(?=[\s.,;:!?)\]]|$)/g, NOPEN + '$1' + NCLOSE);
      return OPEN + inner + CLOSE;
    });
    s = s.replace(/\u0003([^\u0003\u0001\u0002]*?)’(?=[\s.,;:!?)\]]|$)/g, OPEN + '$1' + CLOSE)
         .replace(/‘([^‘\u0001\u0002]*?)’(?=[\s.,;:!?)\]]|$)/g, OPEN + '$1' + CLOSE)
         .replace(/\u0003/g, O).replace(/‘/g, O);
    // A comma or full point inside the closing mark of a short quoted phrase moves outside it (p.37).
    s = s.replace(new RegExp(OPEN + '([^' + OPEN + CLOSE + ']{1,60}?)([.,])' + CLOSE, 'g'), OPEN + '$1' + CLOSE + '$2');
    return s.replace(/\u0001/g, O).replace(/\u0002/g, C).replace(/\u0005/g, IO).replace(/\u0006/g, IC);
  }

  var DAY = '(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun)[a-z]*', MON = '(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)[a-z]*';
  var SPAN = new RegExp('\\b(' + DAY + '|' + MON + ')\\s?[-–—]\\s?(' + DAY + '|' + MON + ')\\b', 'g');
  var TIME = /\b(\d{1,2}(?::\d\d)?(?:\s?[ap]m)?)\s?[-–—]\s?(\d{1,2}(?::\d\d)?(?:\s?[ap]m)?)\b(?![-–:\d])/g;

  function typeset(s, lang) {
    if (!s || !/["'\-.\d–—‘’“”…x×A-Z]/.test(s)) return s;
    s = s
      // Ellipsis (fig 46): one sign; spaced when it stands for words, closed inside a word; no full point after it.
      .replace(/\.(?:\s?\.){2,}/g, '…')
      .replace(/(\S)…(?=\s|$|[,;:)\]])/g, '$1' + NBSP + '…')
      .replace(/…\.(?!\d)/g, '…')
      // Closed en dash for ranges and spans (fig 49): figures, times, years, days, months. An ISO date is left alone.
      // A year and a month (2025-06) is a date, not a span: a range cannot end before it starts, so it keeps its hyphen.
      .replace(/(?<![-\u2013\d]|\d[.,:])(\d{1,4}(?::\d\d)?)-(\d{1,4}(?::\d\d)?)(?![-\u2013\d]|[.,:]\d)/g, function (m, a, b) {
        if (/^(?:1[5-9]|20)\d\d$/.test(a) && /^\d\d$/.test(b) && +b <= +a.slice(2)) return m;
        return a + '\u2013' + b;
      })
      .replace(/\b(\d{1,2}:\d\d)\s[-\u2013]\s(\d{1,2}:\d\d)\b/g, '$1\u2013$2')
      .replace(/\b((?:1[5-9]|20)\d\d)\s[-\u2013]\s((?:1[5-9]|20)\d\d)\b/g, '$1\u2013$2')
      .replace(/\b(\d{1,2}(?::\d\d)?\s?[ap]m)\s?[-\u2013]\s?(\d{1,2}(?::\d\d)?\s?[ap]m)\b/g, '$1\u2013$2')
      .replace(SPAN, '$1\u2013$2')
      // The dash (figs 47-48): a spaced hyphen, a double hyphen, an em dash or a half-spaced en dash all become the
      // spaced en dash, its leading space non-breaking so a line never begins with it. A closed en dash is a span and stays.
      .replace(/(\S)[ \u00a0]*(?:\u2014|--)[ \u00a0]*(?=\S)/g, '$1\u00a0\u2013 ')
      .replace(/(\S)(?:[ \u00a0]+\u2013[ \u00a0]*|[ \u00a0]*\u2013[ \u00a0]+)(?=\S)/g, '$1\u00a0\u2013 ')
      .replace(/(\S)[ \u00a0]+-[ \u00a0]+(?=\S)/g, '$1\u00a0\u2013 ')
      .replace(/^-\s+(?=\S)/g, '\u2013 ');
    s = quotes(s, lang);
    s = s.replace(/(\d)\u2013(?=\d)/g, '$1\u2013\u2060');
    return s
      // Abbreviation points (fig 42): a reduced space after e.g., Prof., Dr.; a figure stays with No., p., fig. (p.37).
      .replace(/\b(e\.g|i\.e|cf|vs|etc|Prof|Dr|Mr|Mrs|Ms|Messrs|St|Ste|approx|resp)\.[  ](?=\S)/g, '$1.' + THIN)
      .replace(/\b(Est|No|Nos|p|pp|fig|figs|vol|c|ca)\.[  ](?=\d)/g, '$1.' + NBSP)
      // Initials (fig 43): a thin space between them, a word space before the surname.
      .replace(/\b([A-Z]\.)[  ](?=[A-Z]\.)/g, '$1' + THIN)
      // A figure keeps its unit, a currency code its amount (p.37).
      .replace(/(\d)[  ](km|m|cm|mm|kg|sq\.? ?m|m²|%|DKK|USD|EUR|GBP|CHF|SEK|NOK|JPY|AUD|CAD|CNY|INR|KRW|NZ\$)(?![A-Za-z])/g, '$1' + NBSP + '$2')
      .replace(/\b(CHF|DKK|USD|EUR|GBP|SEK|NOK|JPY|AUD|CAD|CNY|INR|KRW|NZ\$|US\$)[  ](?=\d)/g, '$1' + NBSP)
      // Multiplication in running text (fig 52): the typeface's × with a narrower space either side.
      .replace(/(\d)[  ]?[x×][  ]?(\d[\d.,]*[  ]?(?:cm|mm|m|km|in|ft|px|pt)\b)/g, '$1' + THIN + '×' + THIN + '$2');
  }

  // Capitals in running text (fig 54): wrapped so the stylesheet can set them a size smaller and evenly spaced. A shouted
  // phrase is one run, so a lone A between capital words is set small with its neighbours.
  var ACRONYM = /(^|[^A-Za-z\u00c0-\u024f\d])([A-Z]{2,}[A-Z\u00c0-\u00de]*(?: (?:[A-Z]{2,}[A-Z\u00c0-\u00de]*|A)(?![A-Za-z\u00e0-\u024f\d]))*)(?![a-z\u00e0-\u024f\d])/g;
  var KEEP = { OK: 1 };
  // Jokker has a thin space but no narrow no-break space or word joiner (checked in the cmap), so a browser would
  // draw them in another typeface. typeset() writes them as markers; the DOM pass turns each into a span set in this
  // face: a thin space is a no-break space narrowed by word-spacing (.ts in atlas.css), a word joiner keeps a range on one line.
  var MARK = /([^\s\u00a0\u2009\u202f]*\u2060[^\s\u00a0\u2009\u202f]*)|[\u2009\u202f]/g;
  function pushText(frag, text, abbr) {
    var last = 0, m;
    if (abbr) {
      ACRONYM.lastIndex = 0;
      while ((m = ACRONYM.exec(text))) {
        if (KEEP[m[2]]) continue;
        var start = m.index + m[1].length;
        if (start > last) frag.appendChild(document.createTextNode(text.slice(last, start)));
        var sp = document.createElement('span');
        sp.className = 'abbr';
        sp.textContent = m[2];
        frag.appendChild(sp);
        last = start + m[2].length;
      }
    }
    if (last < text.length) frag.appendChild(document.createTextNode(text.slice(last)));
  }
  function decorate(node, abbr) {
    var t = node.nodeValue;
    ACRONYM.lastIndex = 0;
    var hasMark = /[\u2009\u202f\u2060]/.test(t), hasAbbr = abbr && ACRONYM.test(t);
    ACRONYM.lastIndex = 0;
    if (!hasMark && !hasAbbr) return;
    var frag = document.createDocumentFragment(), last = 0, m;
    MARK.lastIndex = 0;
    while ((m = MARK.exec(t))) {
      if (m.index > last) pushText(frag, t.slice(last, m.index), abbr);
      var sp = document.createElement('span');
      if (m[1] !== undefined) { sp.className = 'nb'; sp.textContent = m[1].replace(/\u2060/g, ''); }
      else { sp.className = 'ts'; sp.textContent = '\u00a0'; }
      frag.appendChild(sp);
      last = m.index + m[0].length;
    }
    pushText(frag, t.slice(last), abbr);
    node.parentNode.replaceChild(frag, node);
  }

  function inHeading(el) { return !!(el.closest && el.closest('h1,h2,h3,h4,button,.t-title,.meta,.kicker,[role=tab],summary,.abbr,.grade-word')); }
  // A link whose words are an address is data, not prose.
  function isAddress(node) {
    var a = node.parentElement && node.parentElement.closest('a');
    return !!a && /^(https?:\/\/|www\.)\S*$/i.test(a.textContent.trim());
  }
  function langOf(el) {
    var l = el && el.closest && el.closest('[lang]');
    return (l && l.getAttribute('lang')) || document.documentElement.lang || 'en';
  }

  // A grade is named bold, in its own colour (user's instruction, 20 Oct 2026), wherever an answer or a record names it:
  // "Grade B", "grade B", "graded B", "rating B". The letter must be a capital, so "graded a little" is left alone; only
  // "grade" reads an old number (Grade 4) as its letter, so "rating 4 out of 5" is left alone; a range (Grade D-F) stays plain.
  // The person's own question, buttons and the landing questions keep their own colour.
  var GRADE_WORD = /\b(?:(?:Clean Funding Grade|[Gg]raded?)\s+([A-F1-5])|(?:Funding transparency rating|[Rr]ating)\s+([A-F]))\b(?!\s*(?:\u2013|\u2014|-|to|and)\s*[A-F1-5])/g;
  var GRADE_SKIP = '.grade-word,.grade-mark,.user-bubble,.justify-end,button,a,.starter-prompt,#curatorHeroGreeting,#curatorDrawerGreeting,h1,h2,h3,h4';
  function markGrades(node) {
    var G = window.atlasGrade, from = window.atlasGradeFromLetter, t = node.nodeValue;
    if (!G || !from || !node.parentElement || node.parentElement.closest(GRADE_SKIP)) return;
    GRADE_WORD.lastIndex = 0;
    if (!GRADE_WORD.test(t)) return;
    GRADE_WORD.lastIndex = 0;
    var frag = document.createDocumentFragment(), last = 0, m;
    while ((m = GRADE_WORD.exec(t))) {
      var n = from(m[1] || m[2]);
      if (!n || !G[n]) continue;
      if (m.index > last) frag.appendChild(document.createTextNode(t.slice(last, m.index)));
      var sp = document.createElement('span');
      sp.className = 'grade-word grade-word-' + n;
      sp.textContent = m[0].slice(0, -1) + G[n].letter;
      frag.appendChild(sp);
      last = m.index + m[0].length;
    }
    if (!last) return;
    if (last < t.length) frag.appendChild(document.createTextNode(t.slice(last)));
    node.parentNode.replaceChild(frag, node);
  }

  function run(root) {
    if (!root || root.nodeType !== 1 || SKIP[root.tagName]) return;
    var walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, {
      acceptNode: function (n) {
        var p = n.parentElement;
        if (!p || SKIP[p.tagName] || (p.closest && p.closest('script,style,code,pre,kbd,samp,textarea,input,[data-no-typeset],.nb,.ts'))) return NodeFilter.FILTER_REJECT;
        if (isAddress(n)) return NodeFilter.FILTER_REJECT;
        return NodeFilter.FILTER_ACCEPT;
      }
    });
    var nodes = [], n;
    while ((n = walker.nextNode())) nodes.push(n);
    nodes.forEach(function (node) {
      if (!node.parentNode) return;  // already split by markGrades() on an earlier text node of the same parent
      var next = typeset(node.nodeValue, langOf(node.parentElement));
      if (next !== node.nodeValue) node.nodeValue = next;
      var parent = node.parentElement;
      decorate(node, !inHeading(parent));
      // decorate() may have split the node; mark grades in whatever text it left under the same parent.
      if (parent) [].slice.call(parent.childNodes).forEach(function (c) { if (c.nodeType === 3) markGrades(c); });
    });
  }

  // Every place the conversation is drawn: the desktop column, the phone drawer, the greeting and the record panels.
  var targets = ['curatorMessages', 'curatorDrawerLiveStream', 'curatorDrawerGreeting', 'desktopDossierRecordBody', 'detailBody', 'curatorHeroGreeting'];
  function watch() {
    targets.forEach(function (id) {
      var el = document.getElementById(id);
      if (!el || el.__typeset) return;
      el.__typeset = true;
      run(el);
      new MutationObserver(function (list) {
        list.forEach(function (m) {
          m.addedNodes.forEach(function (a) {
            if (a.nodeType === 1) run(a);
            else if (a.nodeType === 3 && a.parentElement && !SKIP[a.parentElement.tagName] && !a.parentElement.closest('.nb,.ts') && !isAddress(a)) {
              var v = typeset(a.nodeValue, langOf(a.parentElement)); if (v !== a.nodeValue) a.nodeValue = v; var par = a.parentElement; decorate(a, false);
              [].slice.call(par.childNodes).forEach(function (c) { if (c.nodeType === 3) markGrades(c); });
            }
          });
        });
      }).observe(el, { childList: true, subtree: true });
    });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', watch); else watch();
  window.typeset = typeset;
})();

// Titles under 17px are set in Documan Regular, the rest in Thin (user, 26 Oct 2026: "use regular for any size under 17"; "thin for the rest").
// A rule in CSS cannot test a font size, so each title is measured once its page has drawn and the small ones get the class title-small, which atlas.css
// sets at weight 400. The sizes are read all together, then the classes are written, so a scan costs one style pass. It runs again when content is added,
// when the window is resized (the phone sizes differ) and when the fonts have loaded.
(function () {
  var SEL = 'h1,h2,h3,h4,h5,h6,.t-title,.lede,.curator-section-hdr,.curator-hero-title,.dossier-main-heading,.d-row-title,.layers-title,.layers-section-title,.hq-chooser-title,.facts-title,.critique-title,#floatingCardTitle,.record-popup-name,#desktopDossierName,#dossier-sheet-name,.inst-link,.space-name,.layer-name,#topBrandLogoBtn>span:first-child,#mobileTopBrandBtn span:first-child';
  var timer = 0;
  function scan() {
    timer = 0;
    var els = [].slice.call(document.querySelectorAll(SEL));
    var small = els.map(function (el) { return parseFloat(getComputedStyle(el).fontSize) < 17; });
    els.forEach(function (el, i) { if (el.classList.contains('title-small') !== small[i]) el.classList.toggle('title-small', small[i]); });
  }
  function later() { if (!timer) timer = setTimeout(scan, 120); }
  function start() {
    scan();
    new MutationObserver(later).observe(document.body, { childList: true, subtree: true });
    window.addEventListener('resize', later);
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(later);
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start); else start();
})();
