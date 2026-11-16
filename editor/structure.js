/* How the data editor shows the structure of a text without changing it.

   Two splits, both exact: joining the parts gives back the stored string character for character, so a field that is only
   looked at is saved unchanged (tests/editor-structure.test.mjs checks this on every text in institutions.json).

   - sentences(text): the sentences of a paragraph and the spaces between them. A full stop ends a sentence only after a
     word of two or more letters that is not an abbreviation (e.g., St., pp., Inc.) and not a run of initials (T. J., U.S.),
     and only before a capital, a figure or an opening quote or bracket.
   - citations(text): a critique note, which runs several cited works together ("Author, Title (e-flux, 2023): what it
     says. Author, Title (BAK, 2025): ..."), as one entry per work: the citation, then what it says. A citation is found by
     its "(publication, year): " and starts at the last full stop before it that leaves an "Author, Title" comma ahead; a
     note that does not open with one is not split.

   Registers itself as globalThis.AtlasStructure, for the page and for Node alike. */
(() => {
  'use strict';

  const ABBR = new Set(['e.g', 'i.e', 'etc', 'st', 'dr', 'mr', 'mrs', 'ms', 'prof', 'no', 'nos', 'pp', 'vol', 'vols', 'ed', 'eds',
    'inc', 'co', 'corp', 'ltd', 'jr', 'sr', 'vs', 'approx', 'ca', 'cf', 'fig', 'figs', 'op', 'ch', 'art', 'mt', 'ft', 'est']);
  // A sentence end: . ! or ? with any closing quotes or brackets, the spaces after it, and a start ahead.
  const END = /[.!?]["”’)\]]*( +)(?=["“‘(]?[A-Z0-9À-ÖØ-Þ])/g;

  function endsSentence(text, at) {
    if (text[at] !== '.') return true;
    const before = text.slice(0, at);
    const word = before.slice(before.search(/\S+$/));
    const bare = word.replace(/^["“‘(]+/, '');
    if (!/[A-Za-zÀ-ÿ0-9%)\]”’"]$/.test(bare)) return false;
    if (/^[A-Z]$/.test(bare)) return false;              // an initial: T. J. Demos
    if (/[A-Za-z]\.[A-Za-z]/.test(bare)) return false;   // U.S, e.g, i.e
    if (ABBR.has(bare.toLowerCase())) return false;
    return true;
  }

  // -> { parts: [sentence, ...], gaps: [the spaces after each sentence but the last] }
  function sentences(text) {
    const s = String(text ?? '');
    const parts = [], gaps = [];
    let from = 0, m;
    END.lastIndex = 0;
    while ((m = END.exec(s))) {
      if (!endsSentence(s, m.index)) continue;
      const cut = m.index + m[0].length - m[1].length;
      parts.push(s.slice(from, cut));
      gaps.push(m[1]);
      from = cut + m[1].length;
    }
    parts.push(s.slice(from));
    return { parts, gaps };
  }

  function joinSentences(parts, gaps = []) {
    const kept = [];
    parts.forEach((p, i) => { if (p.trim() || parts.length === 1) kept.push([p, i < gaps.length ? gaps[i] : ' ']); });
    return kept.map(([p, g], i) => (i < kept.length - 1 ? p + g : p)).join('');
  }

  // "(e-flux, 2023): ", "(Books at San Serriffe, 2016): ", "(ArtLeaks Gazette, 12 May 2013): "
  const MARK = /\(([^()]+?), ((?:\d{1,2} )?(?:[A-Z][a-z]+ )?\d{4}(?:[–-]\d{2,4})?)\): /g;

  // -> [{ head: 'Author, Title (publication, year)', body: 'what it says' }, ...] or null when the text is not a list of them
  function citations(text) {
    const s = String(text ?? '');
    const marks = [...s.matchAll(MARK)];
    if (!marks.length) return null;
    // The sentence ends in the text: each citation starts at the last one before its mark.
    const { parts, gaps } = sentences(s);
    const starts = [0];
    let pos = 0;
    // Only after a full stop: a title can hold a ? or ! ("So You Think You're Political?! Seven Notes ...").
    parts.forEach((p, i) => {
      pos += p.length + (gaps[i] ?? '').length;
      if (i < parts.length - 1 && /\.["”’)\]]*$/.test(p)) starts.push(pos);
    });
    const entries = [];
    let prevEnd = 0;
    for (const m of marks) {
      const headEnd = m.index + m[0].length - 2;          // up to the closing bracket, without ": "
      // A citation opens "Author, Title": the latest sentence start with a comma before the mark. A title can hold full
      // stops of its own (an Italian headline: "... il De Appel. A deciderlo è La Corte ..."), so a start without one
      // is passed over for the one before it.
      const cands = starts.filter(x => x >= prevEnd && x <= m.index);
      const start = [...cands].reverse().find(x => s.slice(x, m.index).includes(', ')) ?? cands.pop();
      if (start == null) continue;                        // a mark inside the previous entry's own head
      if (!entries.length && start !== 0) return null;    // the note does not open with a citation
      if (entries.length) {
        const last = entries[entries.length - 1];
        const between = s.slice(last.bodyFrom, start);
        last.body = between.replace(/ +$/, '');
        last.gap = between.slice(last.body.length);
      }
      entries.push({ head: s.slice(start, headEnd), bodyFrom: headEnd + 2 });
      prevEnd = m.index + m[0].length;
    }
    const last = entries[entries.length - 1];
    last.body = s.slice(last.bodyFrom);
    last.gap = '';
    return entries.map(({ head, body, gap }) => ({ head, body, gap }));
  }

  function joinCitations(entries) {
    const kept = entries.filter(e => e.head.trim() || e.body.trim());
    return kept.map((e, i) => e.head + ': ' + e.body + (i < kept.length - 1 ? (e.gap || ' ') : '')).join('');
  }

  globalThis.AtlasStructure = { sentences, joinSentences, citations, joinCitations };
})();
