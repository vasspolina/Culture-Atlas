/* Share information as a chat (user, 19 Nov 2026: "make share information as chat as well, so it can edit your info or send it").
   The note form stays as it is. This is a second way to the same note: Clio asks which place it is about (a record of the
   atlas, or a place it is missing and its city), then what the visitor knows, and writes the answers into a draft card in
   the chat. Under the card: the visitor's own tick that nothing identifies them, Send, Edit in the form, and Cancel.

   - Nothing is sent until the visitor presses Send. Send posts the same note the form sends (window.atlasPostNote in
     index.html), to the same report service, for the editor to read first.
   - The note keeps the visitor's words. A change asked for in plain words ("drop the second sentence") goes to the chat model
     with the note and nothing else, and its version is taken only when it adds no name or number the visitor did not write.
     Short commands are done here without the model: "add: ...", "sign it ...", "no name", "the city is ...", "the address is ...", "it is about ...".
   - Clio points at words in the draft that could identify the visitor (an email, a phone number, "my name is", "my manager").
     The tick stays the visitor's own.
   - None of these turns enter the chat's history, so a note is never sent to the model with a later question. */
(function () {
  'use strict';

  var MIN = 10, MAX = 2000, NAME_MAX = 40;
  var s = null;              // the interview: { step, place, isNew, name, city, address, kind, where, note, author, choices }
  var keptPlaceholder = null;

  function esc(t) {
    return String(t == null ? '' : t).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }
  function fold(t) {
    return String(t || '').normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase().replace(/\s+/g, ' ').trim();
  }
  function places() {
    return (window.ALL_INSTITUTIONS || []).filter(function (i) { return i && i.id && i.name; });
  }
  function limits() {
    var l = window.atlasReviewLimits || {};
    return { min: l.min || MIN, max: l.max || MAX, name: l.name || NAME_MAX };
  }
  function msgs() { return document.getElementById('curatorMessages'); }
  function input() { return document.getElementById('workInput'); }
  function scroll() { if (typeof window.scrollChatToBottom === 'function') window.scrollChatToBottom(true); }

  // Choices belong to the latest turn only: a new turn takes the earlier row of buttons away.
  function retireChoices() {
    var root = msgs();
    if (!root) return;
    root.querySelectorAll('.chat-share-choices').forEach(function (el) { el.remove(); });
  }

  function clio(html, choices) {
    var root = msgs();
    if (!root) return null;
    retireChoices();
    var hero = document.getElementById('curatorHeroGreeting');
    if (hero) hero.remove();
    var wrap = document.getElementById('curatorScrollContent');
    if (wrap) wrap.classList.remove('my-auto');
    var div = document.createElement('div');
    div.className = 'curator-message-wrap chat-share-turn my-3 w-full';
    div.setAttribute('data-exclude-speech', 'true');
    var row = '';
    if (choices && choices.length) {
      row = '<div class="curator-followups chat-share-choices mt-3 flex flex-col items-start gap-1">' + choices.map(function (c) {
        return '<button type="button" class="curator-followup-pill chat-share-choice' + (c.primary ? ' is-primary' : '') + (c.link ? ' is-link' : '') + ' text-left py-1" data-chat-share-act="' + esc(c.act) + '"' +
          (c.value != null ? ' data-chat-share-value="' + esc(c.value) + '"' : '') + '>' + esc(c.label) + '</button>';
      }).join('') + '</div>';
    }
    div.innerHTML = '<div class="space-y-2_5">' + html + row + '</div>';
    root.appendChild(div);
    if (typeof window.atlasBubbleOutline === 'function') { try { window.atlasBubbleOutline(div); } catch (e) {} }
    scroll();
    return div;
  }
  function said(text) {
    var root = msgs();
    if (!root) return;
    var div = document.createElement('div');
    div.className = 'flex justify-end my-1 w-full chat-share-turn';
    div.innerHTML = '<div class="user-bubble whitespace-pre-wrap">' + esc(text) + '</div>';
    root.appendChild(div);
    scroll();
  }
  // The way out under every question: the form instead (it takes what was answered so far), or stop.
  // A typed name that is keyboard mash is not a new place (user, 19 Nov 2026).
  function nameOk(name) { return typeof window.atlasLooksLikeName !== 'function' || window.atlasLooksLikeName(name); }
  function OUT() { return [{ label: 'Or fill in a form', act: 'form' }, { label: 'Cancel', act: 'cancel' }]; }
  function p(text) { return '<p class="no-indent">' + esc(text) + '</p>'; }

  // While Clio asks, the chat box says what it is for, and the Share information bar is put away (assets/sheet.css,
  // body.chat-share-active): the visitor is sharing already. On the draft the box takes the request for a change.
  function setPlaceholder(on, text) {
    var box = input();
    document.body.classList.toggle('chat-share-active', !!on);
    if (!box) return;
    if (on) {
      if (keptPlaceholder == null) keptPlaceholder = box.placeholder;
      box.placeholder = text || 'Answer here, or write cancel';
    } else if (keptPlaceholder != null) {
      box.placeholder = keptPlaceholder;
      keptPlaceholder = null;
    }
  }

  // ---- the place ----
  function findPlaces(text) {
    var q = fold(text);
    if (!q) return { exact: null, near: [] };
    var all = places(), exact = null, first = [], word = [], rest = [];
    all.forEach(function (i) {
      var k = fold(i.name);
      if (k === q) { exact = exact || i; return; }
      var at = k.indexOf(q);
      if (at === 0) first.push(i);
      else if (at > 0 && /[\s(\-'’]/.test(k.charAt(at - 1))) word.push(i);
      else if (q.length >= 4 && (at > 0 || q.indexOf(k) >= 0)) rest.push(i);
    });
    return { exact: exact, near: first.concat(word, rest).slice(0, 6) };
  }
  function placeLabel(i) { return i.city ? i.name + ', ' + i.city : i.name; }

  // ---- reading the answer ----
  // The visitor answers the way people talk: "one place in Berlin on Arkonaplatz", "Galerie Wedding, Berlin". The answer is
  // read before anything is asked again: a city the atlas knows is taken out of it, and words that describe a place without
  // naming it ("a gallery on ...") are kept as a description, never used as the name.
  var cityKeys = null;
  function cities() {
    if (cityKeys) return cityKeys;
    var seen = {};
    cityKeys = [];
    places().forEach(function (i) {
      var k = fold(i.city);
      if (k.length >= 3 && !seen[k]) { seen[k] = 1; cityKeys.push({ key: k, name: i.city }); }
    });
    cityKeys.sort(function (x, y) { return y.key.length - x.key.length; });
    return cityKeys;
  }
  function knownCity(text) {
    var k = fold(text), hit = cities().find(function (c) { return c.key === k; });
    return hit ? hit.name : '';
  }
  function rx(t) { return t.replace(/[.*+?^${}()|[\]\\\/]/g, '\\$&'); }
  function tidy(t) { return String(t || '').replace(/\s+/g, ' ').replace(/\s+,/g, ',').replace(/^[\s,]+|[\s,.!]+$/g, ''); }

  var ADJ = '(?:(?:small|little|tiny|new|old|big|large|local|private|public|independent|artist[- ]run|non[- ]?profit|commercial|contemporary|art)\\s+)*';
  var NOUN = '(project space|exhibition space|art space|off[- ]space|place|space|spot|venue|gallery|museum|institution|organisation|organization|foundation|theatre|theater|cinema|studio|centre|center|kunstverein|kunsthalle|collective|archive|library|festival|residency|school|academy)';
  var PREP = '(?:on|at|near|by|next to|opposite|behind|off|around|beside|across from|close to|in|inside|above|under|between)';
  var VAGUE_A = new RegExp('^(?:a|an|one|some|this|that)\\s+' + ADJ + NOUN + '\\b\\s*(.*)$', 'i');
  var VAGUE_THE = new RegExp('^(?:the\\s+)?' + ADJ + NOUN + '(?:\\s+(' + PREP + '\\b.*))?$', 'i');
  var VAGUE_SOME = /^(?:somewhere|someplace|something)\b\s*(.*)$/i;
  var STARTS_PREP = new RegExp('^' + PREP + '\\b', 'i');
  var UNKNOWN = /^(?:i\s+)?(?:do\s*n[o'’]?t|dont)\s+(?:know|remember|recall)\b|^(?:no idea|not sure|unknown|idk|no name|none)\b/i;

  function readPlace(text) {
    var t = tidy(String(text || '').normalize('NFC')), f = fold(t), out = { name: t, city: '', kind: '', where: '' };
    // The city: "in Berlin", or ", Berlin". Written with its capital, unless the whole answer is in small letters.
    if (f.length === t.length) {
      var small = t === t.toLowerCase();
      cities().some(function (c) {
        var m = new RegExp('(?:(?:^|[\\s(])in\\s+|,\\s*)(' + rx(c.key) + ')(?=$|[\\s,.;:)!?])').exec(f);
        if (!m) return false;
        var at = m.index + m[0].length - c.key.length, first = t.charAt(at);
        if (!small && first === first.toLowerCase()) return false;
        out.city = c.name;
        out.name = tidy(t.slice(0, m.index) + ' ' + t.slice(m.index + m[0].length));
        return true;
      });
    }
    var n = out.name, m2;
    if (!n || UNKNOWN.test(n)) {
      out.kind = 'place'; out.name = '';
      out.where = (/\b(?:on|at|near|next to|opposite|behind)\s+\S.*$/i.exec(n) || [''])[0];
      return out;
    }
    if ((m2 = VAGUE_SOME.exec(n))) { out.kind = 'place'; out.where = STARTS_PREP.test(m2[1]) ? m2[1] : ''; return out; }
    var a = VAGUE_A.exec(n), the = !a && (/^the\s/i.test(n) || n.charAt(0) === n.charAt(0).toLowerCase()) ? VAGUE_THE.exec(n) : null;
    if (a) {
      var called = /^(?:called|named)\s+(.+)$/i.exec(a[2]);
      if (called) { out.name = tidy(called[1]); return out; }
      out.kind = a[1].toLowerCase(); out.where = STARTS_PREP.test(a[2]) ? a[2] : '';
    } else if (the) {
      out.kind = the[1].toLowerCase(); out.where = the[2] || '';
    }
    return out;
  }

  // Places of the atlas on the street the visitor named, in the city they named.
  function street(t) { return fold(t).replace(/ß/g, 'ss').replace(/strasse\b|str\./g, 'str'); }
  var STREET_STOP = /^(?:street|corner|square|avenue|platz|place|road|station|market|church|river|bridge|centre|center|close|north|south|east|west)$/;
  function onStreet(where, city) {
    var words = street(where).split(/[^a-z0-9ß-ɏ]+/).filter(function (w) { return w.length >= 5 && !STREET_STOP.test(w) && !STARTS_PREP.test(w); });
    if (!words.length) return [];
    var c = fold(city);
    return places().filter(function (i) {
      if (!i.address || (c && fold(i.city) !== c)) return false;
      var a = street(i.address);
      return words.some(function (w) { return a.indexOf(w) >= 0; });
    }).slice(0, 6);
  }

  // ---- asking for the place ----
  function askPlace(suggest) {
    s.step = 'place';
    setPlaceholder(true);
    var known = suggest ? findPlaces(suggest).exact : null;
    if (known) {
      clio(p('Is it about ' + known.name + '? If not, write the place it is about.'),
        [{ label: 'Yes, ' + known.name, act: 'place', value: known.id }].concat(OUT()));
    } else {
      clio(p('Which place is it about? It can be one the atlas is missing.'), OUT());
    }
  }
  function takePlace(text) {
    var hit = findPlaces(text);
    if (hit.exact) return choosePlace(hit.exact);
    var r = readPlace(text);
    if (r.city) s.city = r.city;
    if (r.kind) { s.kind = r.kind; s.where = r.where; return askName(); }
    takeName(r.name);
  }
  // A name, with nothing left to read out of it.
  function takeName(name) {
    name = tidy(name);
    var hit = findPlaces(name);
    if (hit.exact) return choosePlace(hit.exact);
    var near = hit.near, c = fold(s.city);
    if (c) { var here = near.filter(function (i) { return fold(i.city) === c; }); if (here.length) near = here; }
    if (near.length) {
      s.step = 'pickPlace';
      s.typed = name;
      clio(p('Which of these is it?'),
        near.map(function (i) { return { label: placeLabel(i), act: 'place', value: i.id }; })
          .concat([{ label: 'None of these', act: 'newplace' }], OUT()));
      return;
    }
    newPlace(name);
  }
  // The visitor described a place and gave no name: ask for the name once. "I don't know" keeps the description.
  function described() { return 'the ' + s.kind + (s.where ? ' ' + s.where : ''); }
  function askName() {
    s.step = 'name';
    var inCity = s.city ? ' in ' + s.city : '';
    if (!s.where) { clio(p('Which ' + s.kind + inCity + '? Write its name, or the street it is on.'), OUT()); return; }
    var hits = onStreet(s.where, s.city);
    var noName = [{ label: 'I don’t know its name', act: 'noname' }];
    if (hits.length) {
      clio(p('Is it one of these? If not, write what it is called.'),
        hits.map(function (i) { return { label: placeLabel(i), act: 'place', value: i.id }; }).concat(noName, OUT()));
    } else {
      clio(p('What is ' + described() + inCity + ' called?'), noName.concat(OUT()));
    }
  }
  function answerName(text) {
    var t = tidy(text);
    if (UNKNOWN.test(t)) return noName();
    if (!s.where && STARTS_PREP.test(t) && !findPlaces(t).exact) {
      var r = readPlace('somewhere ' + t);
      if (r.city) s.city = r.city;
      s.where = r.where || t;
      return askName();
    }
    var named = readPlace(t);
    if (named.city) s.city = named.city;
    takeName(named.kind ? t : named.name);
  }
  function noName() {
    if (!s.where) { s.step = 'where'; clio(p('Then write the street it is on, or what it is next to.'), OUT()); return; }
    s.place = null; s.isNew = true;
    s.name = (s.kind.charAt(0).toUpperCase() + s.kind.slice(1) + ' ' + s.where).slice(0, 120);
    streetAsAddress(s.where);
    if (s.city) return afterPlace();
    s.step = 'city';
    clio(p('Which city or town is it in?'), OUT());
  }
  function choosePlace(inst) {
    s.place = inst; s.isNew = false; s.name = inst.name; s.city = ''; s.address = ''; s.kind = ''; s.where = '';
    afterPlace();
  }
  function newPlace(name) {
    name = tidy(name);
    if (name.length < 2) { clio(p('Write the place’s name, two letters or more.'), OUT()); return; }
    // Keyboard mash is not a new place (window.atlasLooksLikeName in index.html; user, 19 Nov 2026).
    if (!nameOk(name)) {
      s.step = 'place';
      clio(p('That does not look like the name of a place. Write it the way it is written on the place or in the press.'), OUT());
      return;
    }
    var where = s.where;
    s.place = null; s.isNew = true; s.name = name.slice(0, 120); s.kind = ''; s.where = '';
    streetAsAddress(where);
    var lead = s.name + (s.city ? ' in ' + s.city : '') + ' is new to the atlas.';
    if (s.city) return s.address ? afterPlace(lead) : askAddress(lead);
    s.step = 'city';
    clio(p(s.name + ' is new to the atlas. Which city or town is it in?'), OUT());
  }
  function takeCity(text) {
    var t = tidy(text).replace(/^(?:it(?:['’]s| is)\s+)?in\s+/i, '');
    s.city = (knownCity(t) || t).slice(0, 80);
  }
  // A street the visitor already wrote ("on Arkonaplatz") is the address: it is not asked for again.
  function streetAsAddress(where) {
    var m = /^(?:on|at)\s+(.+)$/i.exec(where || '');
    if (m && !s.address) s.address = m[1].slice(0, 200);
  }
  // A new place's street address, optional (user, 19 Nov 2026: "add adress field"). Asked once, when the city is known.
  function askAddress(lead) {
    s.step = 'address';
    clio(p(lead ? lead + ' What is its address? If you do not know it, skip this.' : 'What is the address of ' + s.name + '? If you do not know it, skip this.'),
      [{ label: 'Skip', act: 'skipaddress' }].concat(OUT()));
  }
  function afterPlace(lead) {
    if (s.note) return showDraft();
    s.step = 'note';
    var about = lead ? 'it' : (s.isNew && s.kind ? described() : s.name);
    clio(p((lead ? lead + ' ' : '') + 'What should people know about ' + about + '? Write it the way you would tell someone: what happened, when, and how you know. Leave out your name and anything that points to you.'),
      OUT());
  }

  // ---- words that could identify the writer ----
  var TELLS = [
    [/[\w.+-]+@[\w-]+\.[\w.]+/g, 'an email address'],
    [/(?:\+|\b)\d[\d\s().-]{7,}\d\b/g, 'a phone number'],
    [/\bmy name is\s+\S+(?:\s+[A-Z]\S*)?/gi, 'your name'],
    [/\bI(?:'m| am)\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?\b/g, 'a name'],
    [/\bI\s+(?:work|worked|was employed|am employed|was hired|was an? intern)\s+(?:as|at|in|on)\s+[^.,;]{1,40}/gi, 'your job'],
    [/\bmy\s+(?:manager|boss|supervisor|line manager|director|colleague|team|department|desk|contract)\b/gi, 'your place at work']
  ];
  function tells(text) {
    var out = [];
    TELLS.forEach(function (t) {
      var m, re = new RegExp(t[0].source, t[0].flags);
      while ((m = re.exec(text))) { if (m[0].trim().length > 2) out.push({ what: t[1], words: m[0].trim() }); if (!re.global) break; }
    });
    return out.slice(0, 4);
  }

  // ---- the draft card ----
  // The card is edited in place (user, 19 Nov 2026: "i need to edit it inside of this"): the place, a new place's city, the
  // name shown and the note are fields of the card itself. What is typed there is the draft; a change asked for in the chat
  // redraws the card from it. The checks under the card (words that could identify the writer, a note too short) follow
  // the typing.
  function checksHtml() {
    var l = limits(), warn = tells(s.note);
    var w = warn.length ? '<p class="no-indent chat-share-warn">These words could point to you: ' + warn.map(function (x) {
      return '“' + esc(x.words) + '” (' + esc(x.what) + ')';
    }).join('; ') + '. Change them in the card.</p>' : '';
    var short = s.note.length < l.min ? '<p class="no-indent chat-share-warn">The note needs at least ' + l.min + ' characters.</p>' : '';
    return w + short;
  }
  function refreshChecks() {
    var box = s && s.card && s.card.querySelector('.chat-share-checks');
    if (box) box.innerHTML = checksHtml();
  }
  function placeState() {
    var row = s.card && s.card.querySelector('.chat-share-cityrow'), tag = s.card && s.card.querySelector('.chat-share-new');
    if (row) row.hidden = !s.isNew;
    var addressRow = s.card && s.card.querySelector('.chat-share-addressrow');
    if (addressRow) addressRow.hidden = !s.isNew;
    var mash = !s.place && !s.isNew && s.name.length >= 2;
    if (tag) tag.textContent = s.isNew ? 'Not on the atlas yet: it goes to the editor as a new place.'
      : mash ? 'That does not look like the name of a place.' : '';
    var city = s.card && s.card.querySelector('.chat-share-placecity');
    if (city) city.textContent = !s.isNew && s.place && s.place.city ? s.place.city : '';
  }
  function sizeNote(el) { el.style.height = 'auto'; el.style.height = el.scrollHeight + 'px'; }

  function showDraft(lead) {
    s.step = 'draft';
    // One card at a time: a changed note replaces the earlier card, so no outdated draft (or its tick box) is left above.
    if (s.card && s.card.isConnected) s.card.remove();
    var l = limits();
    var html = (lead ? p(lead) : p('Here is your note. Nothing is sent until you press Send.')) +
      '<div class="chat-share-card" role="group" aria-label="Your note, not sent">' +
        '<label class="chat-share-row"><span class="chat-share-k">Place</span><input type="text" class="chat-share-in" data-chat-share-field="name" value="' + esc(s.name) + '" maxlength="120" autocomplete="off" spellcheck="false" autocapitalize="words"><span class="chat-share-placecity"></span></label>' +
        '<p class="no-indent chat-share-new"></p>' +
        '<label class="chat-share-row chat-share-cityrow"' + (s.isNew ? '' : ' hidden') + '><span class="chat-share-k">City or town</span><input type="text" class="chat-share-in" data-chat-share-field="city" value="' + esc(s.city) + '" maxlength="80" autocomplete="off" spellcheck="false" autocapitalize="words"></label>' +
        '<label class="chat-share-row chat-share-addressrow"' + (s.isNew ? '' : ' hidden') + '><span class="chat-share-k">Address</span><input type="text" class="chat-share-in" data-chat-share-field="address" value="' + esc(s.address) + '" maxlength="200" placeholder="Optional" autocomplete="off" spellcheck="false" autocapitalize="words"></label>' +
        '<label class="chat-share-row"><span class="chat-share-k">Name shown</span><input type="text" class="chat-share-in" data-chat-share-field="author" value="' + esc(s.author) + '" maxlength="' + l.name + '" placeholder="Whistleblower" autocomplete="off" spellcheck="false"></label>' +
        '<label class="chat-share-notebox"><span class="chat-share-k">Your note</span><textarea class="chat-share-in chat-share-note" data-chat-share-field="note" rows="3" maxlength="' + l.max + '" spellcheck="true" autocapitalize="sentences">' + esc(s.note) + '</textarea></label>' +
        '<label class="nf-check chat-share-ack"><input type="checkbox" data-chat-share-ack' + (s.ack ? ' checked' : '') + '><span>I have left out my name and anything that identifies me.</span></label>' +
        '<p class="no-indent chat-share-status" role="status" aria-live="polite"></p>' +
      '</div><div class="chat-share-checks">' + checksHtml() + '</div>';
    var div = clio(html, [
      { label: 'Send to the editor', act: 'send', primary: true },
      { label: 'Edit in the form', act: 'form' },
      { label: 'Cancel', act: 'cancel', link: true }
    ]);
    s.card = div;
    setPlaceholder(true, 'Or tell me what to change');
    placeState();
    var note = div && div.querySelector('textarea.chat-share-note');
    if (note) sizeNote(note);
  }

  // Typing in the card keeps the draft current.
  document.addEventListener('input', function (e) {
    var el = e.target;
    if (!s || !s.card || !el || !el.matches || !el.matches('[data-chat-share-field]') || !s.card.contains(el)) return;
    var f = el.getAttribute('data-chat-share-field'), v = el.value;
    if (f === 'note') { s.note = v.trim(); sizeNote(el); refreshChecks(); }
    else if (f === 'author') s.author = v.trim().slice(0, limits().name);
    else if (f === 'city') s.city = v.trim().slice(0, 80);
    else if (f === 'address') s.address = v.replace(/\s+/g, ' ').trim().slice(0, 200);
    else if (f === 'name') {
      var name = v.replace(/\s+/g, ' ').trim(), hit = findPlaces(name).exact;
      s.name = name;
      if (hit) { s.place = hit; s.isNew = false; s.name = hit.name; } else { s.place = null; s.isNew = name.length >= 2 && nameOk(name); }
      placeState();
    }
    var st = s.card.querySelector('.chat-share-status');
    if (st && st.dataset.state === 'error') { st.textContent = ''; delete st.dataset.state; }
  });

  // Simple changes done here; anything else is asked of the model.
  function takeEdit(text) {
    var t = text.trim(), m;
    if (/^(start over|restart|begin again)\b/i.test(t)) { var keep = s.suggest; s = fresh(); return askPlace(keep); }
    if ((m = t.match(/^(?:add|also|and)\s*[:,]?\s+([\s\S]+)/i))) {
      var add = m[1].trim();
      s.note = (s.note + (/[.!?]$/.test(s.note) ? ' ' : '. ') + add).slice(0, limits().max);
      return showDraft('Added.');
    }
    if (/^(?:no name|anonymous|leave (?:the|my) name out|don'?t show (?:a|my) name)\b/i.test(t)) {
      s.author = ''; return showDraft('The name shown is Whistleblower.');
    }
    if ((m = t.match(/^(?:sign(?: it)?(?: as)?|call me|show (?:my name as|the name)|name(?: shown)?(?: is)?)\s*[:,]?\s+(.+)$/i))) {
      s.author = m[1].trim().replace(/^["“']|["”']$/g, '').slice(0, limits().name);
      return showDraft('The name shown is ' + s.author + '.');
    }
    if ((m = t.match(/^(?:the )?(?:city|town)(?: is)?\s*[:,]?\s+(.+)$/i) || t.match(/^it'?s in\s+(.+)$/i) || t.match(/^it is in\s+(.+)$/i))) {
      if (!s.isNew) return showDraft(s.name + ' is on the atlas already, so its city is set.');
      s.city = m[1].trim().replace(/\.$/, '').slice(0, 80);
      return showDraft('The city is ' + s.city + '.');
    }
    if ((m = t.match(/^(?:the )?address(?: is)?\s*[:,]?\s+(.+)$/i))) {
      if (!s.isNew) return showDraft(s.name + ' is on the atlas already, so its address is not needed.');
      s.address = m[1].trim().replace(/\.$/, '').replace(/\s+/g, ' ').slice(0, 200);
      return showDraft('The address is ' + s.address + '.');
    }
    if ((m = t.match(/^(?:the )?place(?: is)?\s*[:,]?\s+(.+)$/i) || t.match(/^it'?s about\s+(.+)$/i) || t.match(/^it is about\s+(.+)$/i))) {
      s.city = ''; s.address = '';
      return takePlace(m[1].trim().replace(/\.$/, ''));
    }
    return modelEdit(t);
  }

  function newWords(before, after, asked) {
    // Names and numbers the model's version carries that neither the note nor the request had.
    var known = fold(before + ' ' + asked);
    var words = (after.match(/\b[A-Z][\w'’-]+|\d[\d.,]*/g) || []);
    return words.filter(function (w) {
      var k = fold(w);
      if (known.indexOf(k) >= 0) return false;
      // A capital only because it opens a sentence is not a new name.
      var at = after.indexOf(w), prev = after.slice(Math.max(0, at - 3), at);
      if (/^[A-Z]/.test(w) && (at === 0 || /[.!?]\s+$/.test(prev) || /\n\s*$/.test(prev))) return false;
      return true;
    });
  }

  async function modelEdit(asked) {
    var url = window.ATLAS_AI_PROXY_URL;
    if (!url) return showDraft('I can only make small changes here: “add: …”, “sign it …” or “no name”. Use Edit in the form for the rest.');
    var waiting = clio(p('Changing the note. This can take half a minute…'));
    var system = 'You edit a short note a visitor wrote for a cultural atlas. Apply the change the visitor asks for, and change nothing else. ' +
      'Keep their words. Add no fact, name, date or number that is not in the note or the request. Do not comment, greet or explain. ' +
      'Return only the full note after the change, as plain text, with no quotation marks around it.';
    var user = 'NOTE\n' + s.note + '\n\nCHANGE\n' + asked;
    var ctl = typeof AbortController === 'function' ? new AbortController() : null;
    var timer = ctl ? setTimeout(function () { ctl.abort(); }, 45000) : null;
    var text = '';
    try {
      var res = await fetch(url, {
        method: 'POST', signal: ctl ? ctl.signal : undefined,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ max_tokens: 900, system: system, messages: [{ role: 'user', content: user }] })
      });
      if (res.ok) {
        var data = await res.json();
        text = (Array.isArray(data.content) ? data.content.filter(function (b) { return b.type === 'text'; }).map(function (b) { return b.text; }).join('') : String(data.content || '')).trim();
      }
    } catch (e) { text = ''; } finally { if (timer) clearTimeout(timer); }
    if (waiting) waiting.remove();
    if (!s || s.step !== 'draft') return;
    text = text.replace(/^(?:NOTE|Note)\s*:?\s*\n/, '').replace(/^["“]([\s\S]*)["”]$/, '$1').trim();
    var l = limits();
    var extra = text ? newWords(s.note, text, asked) : [];
    if (!text || text.length > l.max || text === s.note || extra.length) {
      return showDraft(extra.length
        ? 'The change came back with words you did not write (' + extra.slice(0, 3).join(', ') + '), so I kept your note as it was. Say it another way, or use Edit in the form.'
        : 'I could not make that change, so the note is as it was. Say it another way, or use Edit in the form.');
    }
    s.note = text;
    showDraft('Changed. Check it before you send.');
  }

  // ---- send and the form ----
  async function send() {
    var card = s && s.card;
    var status = card && card.querySelector('.chat-share-status');
    var fail = function (m) { if (status) { status.textContent = m; status.dataset.state = 'error'; } };
    var l = limits();
    if (typeof window.atlasPostNote !== 'function' || !window.ATLAS_REPORT_API_URL) return fail('The report service is not set up, so the note was not sent.');
    if (!s.place && !s.isNew) return fail(s.name.length >= 2 ? 'That does not look like the name of a place. Write it the way it is written.' : 'Write the place the note is about.');
    if (s.isNew && !s.city) { var cityIn = card.querySelector('[data-chat-share-field="city"]'); if (cityIn) cityIn.focus(); return fail('Write the city or town ' + s.name + ' is in.'); }
    if (s.note.length < l.min) return fail('Write at least ' + l.min + ' characters.');
    if (!s.ack) return fail('Tick the box to confirm you have left out anything that identifies you.');
    var body = s.place ? { content: s.note } : { content: s.note, placeName: s.name, city: s.city };
    if (!s.place && s.address) body.address = s.address;
    if (s.author) body.authorLabel = s.author;
    if (status) { delete status.dataset.state; status.textContent = 'Sending…'; }
    var buttons = card.querySelectorAll('.chat-share-choice');
    buttons.forEach(function (b) { b.disabled = true; });
    try {
      await window.atlasPostNote(s.place, body);
    } catch (err) {
      buttons.forEach(function (b) { b.disabled = false; });
      return fail('Not sent: ' + (err && err.message || 'no connection') + '. Your note is still here.');
    }
    var name = s.name, isNew = s.isNew;
    end();
    var cardDone = card.querySelector('.chat-share-card');
    if (cardDone) cardDone.classList.add('is-sent');
    card.querySelectorAll('.chat-share-ack, .chat-share-status').forEach(function (el) { el.remove(); });
    card.querySelectorAll('.chat-share-help, .chat-share-checks').forEach(function (el) { el.remove(); });
    card.querySelectorAll('[data-chat-share-field]').forEach(function (el) { el.readOnly = true; el.tabIndex = -1; });
    clio(p(isNew ? 'Sent to the editor as a new place: ' + name + '. It goes on the atlas only once the editor approves it.'
      : 'Sent to the editor for review. It appears on the record of ' + name + ', as a review, only once it is approved.'),
      [{ label: 'Share something else', act: 'again' }]);
  }

  function toForm() {
    var d = s;
    end(true);
    if (typeof window.enterChatInputMode !== 'function') return;
    window.enterChatInputMode('whistleblower');
    // Only what was answered is carried over: an empty answer leaves the form's own value (the open record's name) in place.
    var set = function (id, v) { var el = document.getElementById(id); if (el && v) { el.value = v; el.dispatchEvent(new Event('input', { bubbles: true })); } };
    set('noteInstitution', d.name);
    if (d.isNew) { set('noteCity', d.city); set('noteAddress', d.address); }
    set('noteAuthor', d.author);
    set('workInput', d.note);
    var ack = document.getElementById('noteAck');
    if (ack) { ack.checked = !!d.ack; ack.dispatchEvent(new Event('change', { bubbles: true })); }
    if (typeof window.atlasNotePlace === 'function') window.atlasNotePlace();
  }

  function fresh() { return { step: 'place', place: null, isNew: false, name: '', city: '', address: '', note: '', author: '', ack: false, card: null, suggest: '', kind: '', where: '' }; }
  function end(quiet) {
    s = null;
    setPlaceholder(false);
    if (!quiet) retireChoices();
  }

  function start(opts) {
    opts = opts || {};
    if (document.body.classList.contains('chat-input-mode-active') && typeof window.exitChatInputMode === 'function') window.exitChatInputMode(true);
    if (typeof window.setWorkspaceTab === 'function' && window.innerWidth >= 768) { try { window.setWorkspaceTab('chat'); } catch (e) {} }
    if (typeof window.setMobileViewMode === 'function' && window.innerWidth < 768) { try { window.setMobileViewMode('chat'); } catch (e) {} }
    s = fresh();
    s.suggest = opts.place || '';
    setPlaceholder(true);
    clio(p('Tell me what you know. Archives kept what someone could pay to keep; what you remember can stand beside the record. The editor reads every note before anything goes on the atlas.'));
    askPlace(s.suggest);
    var box = input();
    if (box && window.innerWidth >= 768) box.focus();
  }

  // What the visitor writes in the chat box while the interview is open.
  function take(text) {
    if (!s) return false;
    text = String(text || '').trim();
    if (!text) return true;
    said(text);
    if (/^(cancel|stop|never ?mind|quit)\.?$/i.test(text)) { cancel(); return true; }
    var l = limits();
    switch (s.step) {
      case 'place':
      case 'pickPlace':
        if (s.step === 'place' && /^(yes|yeah|yep|right|correct)\b/i.test(text) && s.suggest) {
          var k = findPlaces(s.suggest).exact;
          if (k) { choosePlace(k); break; }
        }
        takePlace(text); break;
      case 'name':
        answerName(text); break;
      case 'where':
        var w = readPlace('somewhere ' + (STARTS_PREP.test(tidy(text)) ? '' : 'at ') + text);
        if (w.city) s.city = w.city;
        s.where = w.where || 'at ' + tidy(text);
        noName(); break;
      case 'city':
        takeCity(text);
        // A described place carries its street in its name; a named one is asked for its address once.
        if (s.isNew && !s.kind && !s.address) { askAddress(); break; }
        afterPlace(); break;
      case 'address':
        if (!/^(skip|no|none|don'?t know|i don'?t know|not sure)\.?$/i.test(text)) s.address = text.replace(/\s+/g, ' ').slice(0, 200);
        afterPlace(); break;
      case 'note':
        if (text.length < l.min) { clio(p('Write a little more, at least ' + l.min + ' characters.'), OUT()); break; }
        s.note = text.slice(0, l.max);
        showDraft(text.length > l.max ? 'The note was longer than ' + l.max + ' characters, so the end was cut. Check it before you send.' : '');
        break;
      case 'draft':
        takeEdit(text); break;
    }
    return true;
  }

  function cancel() {
    end();
    clio(p('Nothing was sent. Ask me anything, or share what you know whenever you like.'));
  }

  document.addEventListener('click', function (e) {
    var b = e.target && e.target.closest ? e.target.closest('[data-chat-share-act]') : null;
    if (!b) return;
    e.preventDefault();
    e.stopPropagation();
    var act = b.getAttribute('data-chat-share-act'), v = b.getAttribute('data-chat-share-value');
    if (act === 'again') { start(); return; }
    if (!s) return;
    if (act === 'cancel') { said(b.textContent); cancel(); return; }
    if (act === 'place') {
      var inst = places().find(function (i) { return String(i.id) === v; });
      if (inst) { said(placeLabel(inst)); choosePlace(inst); }
      return;
    }
    if (act === 'newplace') { said(b.textContent); newPlace(s.typed); return; }
    if (act === 'noname') { said(b.textContent); noName(); return; }
    if (act === 'skipaddress') { said(b.textContent); afterPlace(); return; }
    if (act === 'send') { send(); return; }
    if (act === 'form') { toForm(); return; }
  }, true);
  document.addEventListener('change', function (e) {
    if (s && e.target && e.target.matches && e.target.matches('[data-chat-share-ack]')) {
      s.ack = e.target.checked;
      var st = s.card && s.card.querySelector('.chat-share-status');
      if (st && s.ack && st.dataset.state === 'error') { st.textContent = ''; delete st.dataset.state; }
    }
  });

  window.atlasChatShare = {
    start: start,
    take: take,
    active: function () { return !!s; },
    cancel: function () { if (s) end(); }
  };
})();
