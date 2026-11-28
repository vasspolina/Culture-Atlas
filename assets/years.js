// Years on the map. A record carries year_founded (the opening year, where a source names one) and, for a space its own
// text says has closed, year_closed and closed_note (data/closures.json, written in by tools/attach_closures.py).
//
// Two controls sit at the end of the filter row, on the desktop (#gmdChips) and the phone (#gmChips):
//   Closed 2006–2026  shows only the spaces with a closing year in those twenty years;
//   By year           opens a year box and a slider. A space is on the map from its opening year and carries the closed
//                     mark from its closing year.
// What the records do not say is never filled in. A space with no closing year is not called open anywhere: it has no
// closing date on record. A space with no opening year stays on the map in every year, drawn as an outline, since no year
// can be given to it. The line under the controls counts the years on record against the spaces that have none, so that
// a thin record is not read as less culture.
//
// Read by assets/layers.js (atlasYearsKeep narrows the map with the other filters) and by index.html (atlasYearMark for
// the mark of each space, atlasYearWords for the words beside a name).
(function () {
  const FROM = 2006, TO = 2026, MIN = 1900, MAX = 2026;
  const S = { closedOnly: false, year: null };
  const records = () => (typeof ALL_INSTITUTIONS !== 'undefined' && Array.isArray(ALL_INSTITUTIONS) ? ALL_INSTITUTIONS : []);
  const opened = i => (Number.isInteger(i.year_founded) ? i.year_founded : null);
  const closedIn = i => (Number.isInteger(i.year_closed) ? i.year_closed : null);
  const isClosed = i => !!(i && (closedIn(i) !== null || i.closed_note));
  const inWindow = i => { const y = closedIn(i); return y !== null && y >= FROM && y <= TO; };
  const num = n => n.toLocaleString('en-GB');

  // The filter, or null when neither control is on.
  window.atlasYearsKeep = function () {
    if (!S.closedOnly && S.year === null) return null;
    return i => {
      if (S.closedOnly && !inWindow(i)) return false;
      if (S.year !== null) { const o = opened(i); if (o !== null && o > S.year) return false; }
      return true;
    };
  };
  // How a space is marked: closed (a cross over its mark) once its closing year has come in the year shown, or always when
  // no year is being shown or the record gives no year for the closure; outline when a year is shown and the record has no
  // opening year. label is the year drawn beside a closed mark while one of the two controls is on.
  window.atlasYearMark = function (i) {
    if (!i) return null;
    const y = closedIn(i), shut = isClosed(i) && (S.year === null || y === null || y <= S.year);
    const outline = S.year !== null && opened(i) === null;
    if (!shut && !outline) return null;
    return { closed: shut, outline, label: shut && (S.closedOnly || S.year !== null) ? (y !== null ? String(y) : 'no year') : '' };
  };
  // The words that go with a space's name: "closed 2021", or "closed, year not on record". Empty for any other space.
  window.atlasYearWords = function (i) {
    if (!isClosed(i)) return '';
    const y = closedIn(i);
    return y !== null ? `closed ${y}` : 'closed, year not on record';
  };
  window.atlasYearsState = () => ({ closedOnly: S.closedOnly, year: S.year, from: FROM, to: TO });

  function counts() {
    const all = records();
    let open = 0, shut = 0, none = 0, win = 0;
    all.forEach(i => { const o = opened(i) !== null, c = closedIn(i) !== null; if (o) open++; if (c) shut++; if (!o && !c) none++; if (inWindow(i)) win++; });
    return { all: all.length, open, shut, none, win };
  }
  function noteText() {
    const c = counts();
    return `${num(c.open)} of ${num(c.all)} places have an opening year on record, ${num(c.shut)} a closing year, ${num(c.none)} neither. ` +
      'A cross marks a closed place, an outline one with no opening year.';
  }

  // ---- The controls ----------------------------------------------------------------------------------------------
  const hosts = () => ['gmdChips', 'gmChips'].map(id => document.getElementById(id)).filter(Boolean);
  let timer = 0, typing = false;   // typing: the year is being typed into the box, which is then left as typed
  function apply() {
    clearTimeout(timer);
    timer = setTimeout(() => { if (typeof window.atlasRefilter === 'function') window.atlasRefilter(); }, 0);
  }
  function paint() {
    hosts().forEach(host => {
      const c = host.querySelector('[data-years="closed"]'), y = host.querySelector('[data-years="year"]'), box = document.getElementById(host.id + 'Years');
      if (!c || !y || !box) return;
      c.setAttribute('aria-pressed', String(S.closedOnly));
      y.setAttribute('aria-pressed', String(S.year !== null));
      y.setAttribute('aria-expanded', String(S.year !== null));
      box.hidden = !S.closedOnly && S.year === null;
      // Where the filter row wraps, the box is its last line. Where it is one bar that scrolls sideways, the box stands
      // under the bar and not in it.
      const bar = getComputedStyle(host).flexWrap === 'nowrap' && getComputedStyle(host).display !== 'none';
      if (bar && box.parentNode !== document.body) { box.classList.add('sh-years-float'); document.body.appendChild(box); }
      if (!bar && box.parentNode !== host) { box.classList.remove('sh-years-float'); box.style.top = ''; host.appendChild(box); }
      if (bar) box.style.top = Math.round(host.getBoundingClientRect().bottom) + 'px';
      const row = box.querySelector('.sh-years-row');
      row.hidden = S.year === null;
      if (S.year !== null) {
        const n = box.querySelector('input[type="number"]'), r = box.querySelector('input[type="range"]');
        if (!typing) n.value = String(S.year);
        r.value = String(S.year);
        r.setAttribute('aria-valuetext', String(S.year));
        box.querySelector('.sh-years-shown').textContent = shownText();
      }
    });
  }
  // What the year shown leaves on the map, in figures: said aloud to a screen reader as the year changes.
  function shownText() {
    if (S.year === null) return '';
    let on = 0, shut = 0, outline = 0;
    const keep = window.atlasYearsKeep();
    records().forEach(i => { if (!keep(i)) return; const m = window.atlasYearMark(i); if (m && m.outline && !m.closed) outline++; else if (m && m.closed) shut++; else on++; });
    return `${num(on)} opened by ${S.year}, ${num(shut)} closed by then, ${num(outline)} with no opening year`;
  }
  function setYear(v) {
    v = Math.round(Number(v));
    if (!Number.isFinite(v)) return;
    S.year = Math.max(MIN, Math.min(MAX, v));
    paint(); apply();
  }
  function build(host, cls) {
    if (host.querySelector('[data-years]')) return;
    const chip = (key, text, title) => {
      const b = document.createElement('button');
      b.type = 'button'; b.className = cls + ' sh-year-chip'; b.dataset.years = key; b.textContent = text; b.title = title;
      b.setAttribute('aria-pressed', 'false');
      host.appendChild(b);
      return b;
    };
    const closed = chip('closed', `Closed ${FROM}–${TO}`, `Show only places with a closing year from ${FROM} to ${TO}; press again to show every place`);
    const year = chip('year', 'By year', 'Pick a year: the map shows the places opened by then and marks the ones closed by then');
    const id = host.id + 'Years';
    const box = document.createElement('div');
    box.className = 'sh-years'; box.id = id; box.hidden = true;
    box.innerHTML =
      `<div class="sh-years-row" hidden>` +
        `<label for="${id}Num">Year</label>` +
        `<input type="number" id="${id}Num" min="${MIN}" max="${MAX}" step="1" inputmode="numeric" value="${MAX}">` +
        `<input type="range" min="${MIN}" max="${MAX}" step="1" value="${MAX}" aria-label="Year, ${MIN} to ${MAX}">` +
        `<span class="sh-years-shown" aria-live="polite"></span>` +
      `</div>` +
      `<p class="sh-years-note"></p>`;
    host.appendChild(box);
    box.querySelector('.sh-years-note').textContent = noteText();
    year.setAttribute('aria-controls', id);
    closed.addEventListener('click', () => { S.closedOnly = !S.closedOnly; paint(); apply(); if (S.closedOnly) tellChat(); });
    year.addEventListener('click', () => {
      if (S.year === null) { setYear(MAX); const n = box.querySelector('input[type="number"]'); if (n && year === document.activeElement) n.focus(); }
      else { S.year = null; paint(); apply(); }
    });
    const n = box.querySelector('input[type="number"]'), r = box.querySelector('input[type="range"]');
    r.addEventListener('input', () => setYear(r.value));
    // A year is taken from the box once it is whole (four figures), so typing 2014 does not pass through 2, 20 and 201.
    n.addEventListener('input', () => { typing = true; if (/^\d{4}$/.test(n.value.trim())) setYear(n.value); typing = false; });
    n.addEventListener('change', () => { setYear(n.value || MAX); n.value = String(S.year); });
    paint();
  }
  // The filter rows are built by assets/desktop-maps.js and assets/phone-maps.js once the page's data is in, the grade
  // chips last; the two controls go after those.
  function tryBuild() {
    let done = 0;
    hosts().forEach(host => {
      if (!host.querySelector('button[data-grade]')) return;
      build(host, host.id === 'gmChips' ? 'gm-filter-chip' : 'gmd-chip');
      done++;
    });
    return done > 0 && done === hosts().length;
  }
  function start() {
    if (tryBuild()) return;
    const t = setInterval(() => { if (tryBuild()) clearInterval(t); }, 500);
    setTimeout(() => clearInterval(t), 30000);
  }
  document.addEventListener('atlas:filter', () => { tryBuild(); paint(); });
  window.addEventListener('resize', paint);
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start); else start();

  // The places behind the Closed chip, as a list in the chat: the map is a canvas, so this is where they can be read.
  let told = 0;
  function tellChat() {
    if (typeof appendCuratorMessage !== 'function' || typeof formatInstLink !== 'function') return;
    if (Date.now() - told < 2000) return;
    told = Date.now();
    const esc = s => String(s).replace(/[&<>"]/g, ch => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[ch]));
    const list = records().filter(inWindow).sort((a, b) => closedIn(b) - closedIn(a) || a.name.localeCompare(b.name));
    const c = counts();
    const rows = list.map(i => `<li>${closedIn(i)} – ${formatInstLink(i, { noDossier: true })}${opened(i) !== null ? ', opened ' + opened(i) : ''}. ${esc(i.closed_note || '')}</li>`).join('');
    appendCuratorMessage(
      `<p class="no-indent">${list.length} of the ${num(c.all)} places on the atlas have a closing year from ${FROM} to ${TO} on record, latest first.</p>` +
      `<ul class="sh-years-list">${rows}</ul>`,
      ['Which museums were founded after 2006?']);
  }
})();
