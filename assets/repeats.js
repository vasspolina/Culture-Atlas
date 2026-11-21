// No text is said twice. The atlas builds a record, a chat answer or a card out of many fields that were researched apart, and the
// same sentence often sits in two of them (the funding line and the flag reason, an Epstein record and the reported findings, two
// press items quoting one point). The model behind the chat repeats itself too. This file finds a sentence, a list item or a block
// that was already said earlier in the same view and takes the later copy out, so the reader meets each statement once.
//
// - dropRepeatedText(text): for Markdown or plain text, the chat model's answer before it is rendered.
// - dedupeHtml(html) / dedupeDom(root): for a rendered view, the record page, the phone sheet, a chat turn.
// - repeats(text): what would be dropped, for the tests and for tools/check_repetition.py's JS twin.
//
// Two sentences are the same when they match once case, accents, quotes and punctuation are set aside, or when the later one is
// held whole inside an earlier one (eight words or more), or when they share nearly all their words (nine in ten, ten words or
// more). Short strings (under five words: labels, names, dates, "Confirmed") are never touched: a name may be printed in a title
// and again in a sentence. Mark an element data-repeat-ok to keep it out of the pass.
//
// Pure functions apart from dedupeDom; index.html calls dedupeHtml on every record and chat turn, tests/repeats.test.mjs loads the
// file in Node.
(function (root) {
  var MIN_WORDS = 5;        // shorter strings are labels and names, never compared
  var CONTAIN_WORDS = 8;    // a sentence this long held whole inside an earlier one is a repeat
  var NEAR_WORDS = 10;      // a sentence this long sharing NEAR of its words with an earlier one is a repeat
  var NEAR = 0.9;

  function norm(s) {
    return String(s == null ? '' : s).toLowerCase().normalize('NFKD').replace(/[̀-ͯ]/g, '')
      .replace(/[’‘`]/g, "'").replace(/[^a-z0-9$€£%']+/g, ' ').replace(/(^| )'+|'+( |$)/g, ' ').replace(/\s+/g, ' ').trim();
  }
  function wordCount(k) { return k ? k.split(' ').length : 0; }
  // A statement, not a name: five words or more, three of them in lower case. "Pushkin State Museum of Fine Arts", "Ho Chi Minh City,
  // Vietnam" and "La Friche la Belle de Mai" are names and may be printed as often as they are needed.
  function isStatement(raw) {
    var t = String(raw || '');
    if (wordCount(norm(t)) < MIN_WORDS) return false;
    return (t.match(/(?:^|[\s(,;:'"“‘])[a-z][a-z'’-]+/g) || []).length >= 3;
  }

  // Sentences, keeping their own trailing space. A full stop after an initial, a title or a common abbreviation ("James H.W.
  // Thompson", "St. Petersburg", "Inc.") does not end one.
  var ABBR = /(?:^|[\s(])(?:[A-Z]|[A-Z]\.[A-Z]|[A-Z]\.[A-Z]\.[A-Z]|Mr|Mrs|Ms|Dr|Prof|St|Ste|Mt|Inc|Ltd|Co|Corp|Jr|Sr|No|Nos|Nr|vs|etc|e\.g|i\.e|approx|ca|cf|Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec|U\.S|U\.K)\.$/;
  function sentences(text) {
    var parts = String(text || '').match(/[^.!?]*(?:[.!?]+["'’”)\]]*\s*|$)/g) || [];
    var out = [];
    parts.forEach(function (p) {
      if (!p) return;
      var last = out.length ? out[out.length - 1] : '';
      if (last && (!/\s$/.test(last) || ABBR.test(last.trimEnd()))) out[out.length - 1] += p;   // "3.5", "e-flux.com" or "H.W. Thompson"
      else out.push(p);
    });
    return out;
  }

  // A memory of what the view has said so far.
  function Seen() { this.exact = new Set(); this.long = []; this.dropped = []; }   // dropped: what the pass took out, in order
  Seen.prototype.has = function (k) {
    if (this.exact.has(k)) return true;
    var n = wordCount(k);
    if (n >= CONTAIN_WORDS) {
      var padded = ' ' + k + ' ';
      for (var i = 0; i < this.long.length; i++) if (this.long[i].key.length > k.length && this.long[i].padded.indexOf(padded) >= 0) return true;
    }
    if (n >= NEAR_WORDS) {
      var mine = new Set(k.split(' '));
      for (var j = 0; j < this.long.length; j++) {
        var other = this.long[j];
        if (other.words.size < NEAR_WORDS) continue;
        var shared = 0;
        mine.forEach(function (w) { if (other.words.has(w)) shared++; });
        if (shared / Math.max(mine.size, other.words.size) >= NEAR) return true;
      }
    }
    return false;
  };
  Seen.prototype.add = function (k) {
    if (this.exact.has(k)) return;
    this.exact.add(k);
    if (wordCount(k) >= CONTAIN_WORDS) this.long.push({ key: k, padded: ' ' + k + ' ', words: new Set(k.split(' ')) });
  };
  // The words compared: a source in brackets closing the sentence ("(English Wikipedia).") is not part of what it says, so the
  // same sentence cited once and uncited once is still one sentence.
  var TAIL_CITE = /\s*\((?:[^()]|\([^()]*\))*\)\s*[.!?]*["'’”\]]*\s*$/;
  function key(s) { var k = norm(String(s || '').replace(TAIL_CITE, '')); return k || norm(s); }
  // True when the sentence was said already; otherwise it is remembered and false comes back.
  Seen.prototype.check = function (s) {
    var k = key(s);
    if (!isStatement(s)) return false;
    if (this.has(k)) { this.dropped.push(String(s).trim()); return true; }
    this.add(k);
    return false;
  };

  // Markdown or plain text. Headings and table rows keep their shape; a list item or a paragraph sentence said before goes, and a
  // line left empty goes with it.
  function dropRepeatedText(text, seen) {
    if (!text || typeof text !== 'string') return text;
    seen = seen || new Seen();
    var lines = text.split('\n').map(function (line) {
      if (/^\s*(?:#|\||>?\s*$)/.test(line)) return line;
      var m = /^(\s*(?:>\s*)?(?:[-*•]|\d+[.)])\s+)([\s\S]*)$/.exec(line) || /^(\s*>\s*)([\s\S]*)$/.exec(line);
      var lead = m ? m[1] : '', body = m ? m[2] : line;
      var plain = body.replace(/\*\*|__|`/g, '').replace(/\[([^\]]*)\]\([^)]*\)/g, '$1');
      var kept = sentences(body).filter(function (s, i, all) {
        var p = all.length === 1 ? plain : s.replace(/\*\*|__|`/g, '').replace(/\[([^\]]*)\]\([^)]*\)/g, '$1');
        return !seen.check(p);
      }).join('').trim();
      return kept ? lead + kept : (m ? '' : '');
    });
    return lines.filter(function (line, i, arr) { return line.trim() !== '' || (i > 0 && arr[i - 1].trim() !== ''); }).join('\n').trim();
  }

  // What dropRepeatedText would take out, as the sentences themselves.
  function repeats(text) {
    var seen = new Seen();
    String(text || '').split('\n').forEach(function (line) {
      sentences(line.replace(/^\s*(?:>\s*)?(?:[-*•]|\d+[.)])\s+/, '')).forEach(function (s) { seen.check(s); });
    });
    return seen.dropped;
  }

  // ---- rendered views -------------------------------------------------------------------------------------------------------
  var SKIP = 'script,style,button,select,option,input,textarea,svg,nav,.sr-only,[aria-hidden="true"],[data-repeat-ok]';
  var LEAF = 'p,li,blockquote,dd,dt,td,th,figcaption,h1,h2,h3,h4,h5,h6,summary,.kicker,.meta';
  var BLOCK = 'p,li,ul,ol,blockquote,dd,dt,dl,table,div,section,article,figure,h1,h2,h3,h4,h5,h6,details,summary,header,footer';
  var HOLDER = '.record-card,.d-row,[role="region"],section,details,figure';

  function isLeaf(el) {
    if (el.closest && el.closest(SKIP)) return false;
    if (el.matches(LEAF)) return !el.querySelector(BLOCK);
    // A div that holds text of its own and no blocks below it reads like a paragraph.
    if (el.tagName === 'DIV' && !el.querySelector(BLOCK)) return /\S/.test(el.textContent || '');
    return false;
  }
  function textNodes(el) {
    var out = [], walk = el.ownerDocument.createTreeWalker(el, 4, null), n;
    while ((n = walk.nextNode())) if (!(n.parentElement && n.parentElement.closest(SKIP))) out.push(n);
    return out;
  }
  function hasWords(el) {
    if (!el) return false;
    var copy = el.cloneNode(true);
    copy.querySelectorAll(SKIP).forEach(function (x) { x.remove(); });
    return /[A-Za-z0-9]/.test(copy.textContent || '') || !!el.querySelector('img,a[href],video,canvas,button');
  }
  // After a leaf goes, a list, a card or a row left with only its label goes too.
  // An element with an id is a slot the page fills again later: it is emptied, never removed.
  function prune(el, rootEl) {
    var parent = el.parentElement;
    if (el.id) { el.innerHTML = ''; return; }
    el.remove();
    while (parent && parent !== rootEl && !parent.id) {
      var next = parent.parentElement;
      if (parent.matches('ul,ol,dl,blockquote') && !parent.querySelector('li,dd,dt,p') && !hasWords(parent)) { parent.remove(); parent = next; continue; }
      if (parent.matches(HOLDER) && !parent.querySelector('p,li,dd,blockquote,td,img,video,canvas,a[href],button')) { parent.remove(); parent = next; continue; }
      break;
    }
  }

  function dedupeDom(rootEl, seen) {
    if (!rootEl || !rootEl.querySelectorAll) return 0;
    seen = seen || new Seen();
    var removed = 0;
    var leaves = Array.prototype.filter.call(rootEl.querySelectorAll(LEAF + ',div'), isLeaf);
    var set = new Set(leaves);
    // A label inside a paragraph is read as part of that paragraph, not on its own.
    leaves = leaves.filter(function (el) { for (var a = el.parentElement; a && a !== rootEl; a = a.parentElement) if (set.has(a)) return false; return true; });
    leaves.forEach(function (leaf) {
      if (!rootEl.contains(leaf)) return;   // taken out with an earlier one
      // A row of source links is provenance, printed beside each claim it backs; it is not compared.
      var own = leaf.cloneNode(true);
      own.querySelectorAll('a,' + SKIP).forEach(function (x) { x.remove(); });
      if (!isStatement(own.textContent)) return;
      var nodes = textNodes(leaf), text = '', at = [];
      nodes.forEach(function (n) { at.push(text.length); text += n.nodeValue; });
      var whole = text.replace(/\s+/g, ' ').trim(), k = norm(whole);
      if (seen.has(k)) { seen.dropped.push(whole); prune(leaf, rootEl); removed++; return; }
      // Sentence by sentence over the whole leaf, so a sentence that runs through a link is read as one. A repeat inside one text
      // node is cut there; one that runs across a link stays unless it is the whole leaf (handled above).
      var pos = 0, cuts = [];
      sentences(text).forEach(function (sent) {
        var start = pos, end = pos + sent.length; pos = end;
        if (!seen.check(sent)) return;
        for (var i = 0; i < nodes.length; i++) {
          var ns = at[i], ne = ns + nodes[i].nodeValue.length;
          if (start >= ns && end <= ne) { cuts.push([i, start - ns, end - ns]); return; }
        }
        seen.dropped.pop();
      });
      cuts.reverse().forEach(function (c) { var v = nodes[c[0]].nodeValue; nodes[c[0]].nodeValue = v.slice(0, c[1]) + v.slice(c[2]); removed++; });
      if (cuts.length && !hasWords(leaf)) prune(leaf, rootEl);
      else if (cuts.length) { leaf.normalize(); if (leaf.firstChild && leaf.firstChild.nodeType === 3) leaf.firstChild.nodeValue = leaf.firstChild.nodeValue.replace(/^\s+/, ''); }
      seen.add(k);
    });
    return removed;
  }

  function dedupeHtml(html, seen) {
    if (!html || typeof html !== 'string' || typeof document === 'undefined') return html;
    var t = document.createElement('template');
    t.innerHTML = html;
    var holder = document.createElement('div');
    holder.appendChild(t.content);
    return dedupeDom(holder, seen) ? holder.innerHTML : html;
  }

  var api = { norm: norm, isStatement: isStatement, sentences: sentences, Seen: Seen, dropRepeatedText: dropRepeatedText, repeats: repeats,
    dedupeDom: dedupeDom, dedupeHtml: dedupeHtml, MIN_WORDS: MIN_WORDS };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  root.AtlasRepeats = api;
})(typeof window !== 'undefined' ? window : globalThis);
