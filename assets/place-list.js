/* The place list of the note form (user, 19 Nov 2026: "design this using atlas typography", text in dark green).
   The browser's own drop-down for a datalist is drawn by the system in its own sans and cannot be styled, so the box no
   longer points at the datalist. This script reads the same options (filled by fillNoteInstitutions in index.html, with
   each place's city) and draws a list of its own under the box, set in the sheet's serif (assets/sheet.css, #notePlaceList).
   It is a combobox: typing narrows the list (accents and case ignored, names that start with the text first), the arrow
   keys move, Enter or a click picks, Escape closes. A pick fires input and change on the box, so the form's own checks
   (a known place, a new one with its city, Send ready) run as they did with the datalist. */
(function () {
  'use strict';

  var box, list, data = null, shown = [], active = -1, open = false;

  function fold(t) {
    return String(t || '').normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase();
  }

  function load() {
    if (data && data.length) return data;
    var src = document.getElementById('noteInstitutionList');
    data = src ? Array.prototype.map.call(src.options, function (o) {
      var name = o.value, city = o.getAttribute('data-city') || '';
      return { name: name, city: city, key: fold(name), cityKey: fold(city) };
    }) : [];
    return data;
  }

  function matches(q) {
    var all = load();
    q = fold(q).trim();
    if (!q) return all.slice();
    var first = [], word = [], rest = [];
    all.forEach(function (p) {
      var i = p.key.indexOf(q);
      if (i === 0) first.push(p);
      else if (i > 0 && /[\s(\-'’]/.test(p.key.charAt(i - 1))) word.push(p);
      else if (i > 0 || p.cityKey.indexOf(q) === 0) rest.push(p);
    });
    return first.concat(word, rest);
  }

  // The list sits fixed under the box, or over it when there is more room above (the form is at the foot of the panel).
  function place() {
    var r = box.getBoundingClientRect();
    var gap = 4, vh = window.innerHeight;
    var below = vh - r.bottom - gap - 8, above = r.top - gap - 8;
    var up = below < 200 && above > below;
    var room = Math.max(120, up ? above : below);
    list.style.left = r.left + 'px';
    list.style.width = r.width + 'px';
    list.style.maxHeight = Math.min(room, 420) + 'px';
    if (up) { list.style.top = 'auto'; list.style.bottom = (vh - r.top + gap) + 'px'; }
    else { list.style.bottom = 'auto'; list.style.top = (r.bottom + gap) + 'px'; }
  }

  function esc(t) {
    return String(t).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; });
  }

  function render() {
    shown = matches(box.value);
    active = -1;
    box.removeAttribute('aria-activedescendant');
    if (!shown.length) { close(); return; }
    list.innerHTML = shown.map(function (p, i) {
      return '<li role="option" id="notePlaceOpt' + i + '" data-i="' + i + '" aria-selected="false">' +
        '<span class="npl-name">' + esc(p.name) + '</span>' +
        (p.city ? '<span class="npl-city">' + esc(p.city) + '</span>' : '') + '</li>';
    }).join('');
    list.scrollTop = 0;
    show();
  }

  function show() {
    list.hidden = false;
    open = true;
    box.setAttribute('aria-expanded', 'true');
    place();
  }

  function close() {
    if (!list) return;
    list.hidden = true;
    open = false;
    active = -1;
    box.setAttribute('aria-expanded', 'false');
    box.removeAttribute('aria-activedescendant');
  }

  function mark(i) {
    var old = list.querySelector('[aria-selected="true"]');
    if (old) old.setAttribute('aria-selected', 'false');
    active = i;
    var li = list.children[i];
    if (!li) { box.removeAttribute('aria-activedescendant'); return; }
    li.setAttribute('aria-selected', 'true');
    box.setAttribute('aria-activedescendant', li.id);
    var top = li.offsetTop, bottom = top + li.offsetHeight;
    if (top < list.scrollTop) list.scrollTop = top;
    else if (bottom > list.scrollTop + list.clientHeight) list.scrollTop = bottom - list.clientHeight;
  }

  function pick(i) {
    var p = shown[i];
    if (!p) return;
    box.value = p.name;
    close();
    box.dispatchEvent(new Event('input', { bubbles: true }));
    box.dispatchEvent(new Event('change', { bubbles: true }));
  }

  function init() {
    box = document.getElementById('noteInstitution');
    if (!box) return;
    box.removeAttribute('list');
    list = document.createElement('ul');
    list.id = 'notePlaceList';
    list.setAttribute('role', 'listbox');
    list.setAttribute('aria-label', 'Places on the atlas');
    list.setAttribute('data-no-typeset', '');
    list.hidden = true;
    document.body.appendChild(list);
    box.setAttribute('role', 'combobox');
    box.setAttribute('aria-autocomplete', 'list');
    box.setAttribute('aria-controls', 'notePlaceList');
    box.setAttribute('aria-expanded', 'false');

    // The datalist is filled on the box's first focus (index.html); the list is drawn just after that.
    box.addEventListener('focus', function () { setTimeout(function () { if (document.activeElement === box) render(); }, 0); });
    box.addEventListener('input', function (e) { if (e.isTrusted) render(); });
    box.addEventListener('blur', function () { setTimeout(close, 120); });
    box.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
        e.preventDefault();
        if (!open) { render(); if (!open) return; }
        var n = shown.length;
        mark(e.key === 'ArrowDown' ? (active + 1) % n : (active <= 0 ? n - 1 : active - 1));
      } else if (e.key === 'Enter' && open && active >= 0) {
        e.preventDefault();
        pick(active);
      } else if (e.key === 'Escape' && open) {
        e.preventDefault();
        e.stopPropagation();
        close();
      }
    });
    // mousedown, not click, so the box keeps the focus and its blur does not close the list first.
    list.addEventListener('mousedown', function (e) {
      var li = e.target.closest('li[data-i]');
      e.preventDefault();
      if (li) pick(+li.getAttribute('data-i'));
    });
    list.addEventListener('mousemove', function (e) {
      var li = e.target.closest('li[data-i]');
      if (li && +li.getAttribute('data-i') !== active) mark(+li.getAttribute('data-i'));
    });
    window.addEventListener('resize', function () { if (open) place(); });
    document.addEventListener('scroll', function (e) { if (open && e.target !== list) place(); }, true);
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
