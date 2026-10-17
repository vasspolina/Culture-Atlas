/* Detail typography (after Jost Hochuli, "Detail in Typography").
   Fixes the small marks the data and the chat engine write as plain ASCII:
   quotes, apostrophes, ellipses, dashes, year ranges, acronyms and the spaces that keep a figure with its unit.
   Runs on text nodes only, never on links' hrefs, code or inputs, and is safe to run twice. */
(function () {
  'use strict';
  var SKIP = { SCRIPT: 1, STYLE: 1, CODE: 1, PRE: 1, TEXTAREA: 1, INPUT: 1, SVG: 1, CANVAS: 1 };
  var NBSP = ' ', THIN = ' ';

  function typeset(s) {
    if (!s || !/["'\-.\d]/.test(s)) return s;
    return s
      // Hochuli p.36: an ellipsis is one sign; three full points are only the fallback
      .replace(/\.{3}|…/g, '…')
      // Ranges of years or figures take an en dash, with no spaces and no collision (p.38). ISO dates are left alone.
      .replace(/\b((?:1[5-9]|20)\d\d)-((?:1[5-9]|20)\d\d)\b(?!-\d)/g, '$1–$2')
      // A spaced hyphen is a dash: the en dash with spaces on both sides (p.38)
      .replace(/(\S) - (\S)/g, '$1 – $2')
      // Double quotes: opening after a space, bracket or start; closing otherwise
      .replace(/(^|[\s(\[–—])"/g, '$1“').replace(/"/g, '”')
      // Single quotes and apostrophes: an apostrophe inside or after a word is the closing form
      .replace(/(^|[\s(\[–—“])'(?=\S)/g, '$1‘').replace(/'/g, '’')
      // Keep "Est. 1859", "No. 4", "p. 12", "fig. 3" and a figure with its unit together (p.37)
      .replace(/\b(Est|No|Nos|p|pp|fig|vol|c|ca)\.\s(?=\d)/g, '$1.' + NBSP)
      .replace(/(\d)\s(km|m|cm|mm|kg|DKK|USD|EUR|GBP|CHF|SEK|NOK|%|sq\.? ?m)\b/g, '$1' + NBSP + '$2')
      // Initials sit close to each other and to the surname, never loose (p.37)
      .replace(/\b([A-Z]\.)\s(?=[A-Z]\.)/g, '$1' + THIN);
  }

  // Capitals in running text look obtrusive; set acronyms one step smaller (p.39, fig. 54c).
  var ACRONYM = /(^|[^A-Za-zÀ-ɏ])([A-Z]{3,6})(?![A-Za-zÀ-ɏ])/g;
  function markAcronyms(node) {
    var t = node.nodeValue;
    ACRONYM.lastIndex = 0;
    if (!ACRONYM.test(t)) return;
    ACRONYM.lastIndex = 0;
    var frag = document.createDocumentFragment(), last = 0, m;
    while ((m = ACRONYM.exec(t))) {
      var start = m.index + m[1].length;
      if (start > last) frag.appendChild(document.createTextNode(t.slice(last, start)));
      var span = document.createElement('span');
      span.className = 'abbr';
      span.textContent = m[2];
      frag.appendChild(span);
      last = start + m[2].length;
    }
    if (last < t.length) frag.appendChild(document.createTextNode(t.slice(last)));
    node.parentNode.replaceChild(frag, node);
  }

  function inHeading(el) { return !!(el.closest && el.closest('h1,h2,h3,h4,button,.t-title,.meta,.kicker,[role=tab],summary,.abbr')); }

  function run(root) {
    if (!root || root.nodeType !== 1 || SKIP[root.tagName]) return;
    var walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, {
      acceptNode: function (n) {
        var p = n.parentElement;
        if (!p || SKIP[p.tagName] || (p.closest && p.closest('script,style,code,pre,textarea,input'))) return NodeFilter.FILTER_REJECT;
        return NodeFilter.FILTER_ACCEPT;
      }
    });
    var nodes = [], n;
    while ((n = walker.nextNode())) nodes.push(n);
    nodes.forEach(function (node) {
      var next = typeset(node.nodeValue);
      if (next !== node.nodeValue) node.nodeValue = next;
      if (!inHeading(node.parentElement)) markAcronyms(node);
    });
  }

  var targets = ['curatorMessages', 'desktopDossierRecordBody', 'detailBody', 'curatorHeroGreeting'];
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
            else if (a.nodeType === 3 && a.parentElement && !SKIP[a.parentElement.tagName]) {
              var v = typeset(a.nodeValue); if (v !== a.nodeValue) a.nodeValue = v;
            }
          });
        });
      }).observe(el, { childList: true, subtree: true });
    });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', watch); else watch();
  window.typeset = typeset;
})();
