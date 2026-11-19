/* Share information as a chat (user, 19 Nov 2026: "make share information as chat as well, so it can edit your info or send it").
   The note form stays as it is. This is a second way to the same note: Clio asks which place it is about (a record of the
   atlas, or a place it is missing and its city), then what the visitor knows, and writes the answers into a draft card in
   the chat. Under the card: the visitor's own tick that nothing identifies them, Send, Edit in the form, and Cancel.

   - Nothing is sent until the visitor presses Send. Send posts the same note the form sends (window.atlasPostNote in
     index.html), to the same report service, for the editor to read first.
   - The note keeps the visitor's words. A change asked for in plain words ("drop the second sentence") goes to the chat model
     with the note and nothing else, and its version is taken only when it adds no name or number the visitor did not write.
     Short commands are done here without the model: "add: ...", "sign it ...", "no name", "the city is ...", "it is about ...".
   - Clio points at words in the draft that could identify the visitor (an email, a phone number, "my name is", "my manager").
     The tick stays the visitor's own.
   - None of these turns enter the chat's history, so a note is never sent to the model with a later question. */
(function () {
  'use strict';

  var MIN = 10, MAX = 2000, NAME_MAX = 40;
  var s = null;              // the interview: { step, place, isNew, name, city, note, author, choices }
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
        return '<button type="button" class="curator-followup-pill chat-share-choice' + (c.primary ? ' is-primary' : '') + ' text-left py-1" data-chat-share-act="' + esc(c.act) + '"' +
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
  function OUT() { return [{ label: 'Or fill in a form', act: 'form' }, { label: 'Cancel', act: 'cancel' }]; }
  function p(text) { return '<p class="no-indent">' + esc(text) + '</p>'; }

  function setPlaceholder(on) {
    var box = input();
    if (!box) return;
    if (on) {
      if (keptPlaceholder == null) keptPlaceholder = box.placeholder;
      box.placeholder = 'Answer here, or write cancel';
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

  function askPlace(suggest) {
    s.step = 'place';
    var known = suggest ? findPlaces(suggest).exact : null;
    if (known) {
      clio(p('Is it about ' + known.name + '? If it is about another place, write its name, on the atlas or not.'),
        [{ label: 'Yes, ' + known.name, act: 'place', value: known.id }].concat(OUT()));
    } else {
      clio(p('Which place is it about? Write its name. It can be a place on the atlas, or one the atlas is missing.'),
        OUT());
    }
  }
  function takePlace(text) {
    var hit = findPlaces(text);
    if (hit.exact) return choosePlace(hit.exact);
    if (hit.near.length) {
      s.step = 'pickPlace';
      s.typed = text.trim();
      clio(p('Which of these is it? If none, it goes to the editor as a new place.'),
        hit.near.map(function (i) { return { label: placeLabel(i), act: 'place', value: i.id }; })
          .concat([{ label: 'None of these: ' + s.typed + ' is a new place', act: 'newplace' }], OUT()));
      return;
    }
    newPlace(text.trim());
  }
  function choosePlace(inst) {
    s.place = inst; s.isNew = false; s.name = inst.name; s.city = '';
    afterPlace();
  }
  function newPlace(name) {
    name = String(name || '').replace(/\s+/g, ' ').trim();
    if (name.length < 2) { clio(p('Write the place’s name, two letters or more.'), OUT()); return; }
    s.place = null; s.isNew = true; s.name = name.slice(0, 120);
    if (s.city) return afterPlace();
    s.step = 'city';
    clio(p(s.name + ' is not on the atlas yet. It goes to the editor as a new place. Which city or town is it in?'), OUT());
  }
  function afterPlace() {
    if (s.note) return showDraft();
    s.step = 'note';
    clio(p('What should people know about ' + s.name + '? Write it the way you would tell someone: what happened, when, and how you know. Leave out your name and anything that points to you.'),
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
    if (tag) tag.textContent = s.isNew ? 'Not on the atlas yet: it goes to the editor as a new place.' : (s.place && s.place.city ? s.place.city : '');
  }
  function sizeNote(el) { el.style.height = 'auto'; el.style.height = el.scrollHeight + 'px'; }

  function showDraft(lead) {
    s.step = 'draft';
    // One card at a time: a changed note replaces the earlier card, so no outdated draft (or its tick box) is left above.
    if (s.card && s.card.isConnected) s.card.remove();
    var l = limits();
    var html = (lead ? p(lead) : p('Here is your note. Change anything in it here. Nothing is sent until you press Send.')) +
      '<div class="chat-share-card" role="group" aria-label="Your note, not sent">' +
        '<label class="chat-share-row"><span class="chat-share-k">Place</span><input type="text" class="chat-share-in" data-chat-share-field="name" value="' + esc(s.name) + '" maxlength="120" autocomplete="off" spellcheck="false" autocapitalize="words"></label>' +
        '<p class="no-indent chat-share-new"></p>' +
        '<label class="chat-share-row chat-share-cityrow"' + (s.isNew ? '' : ' hidden') + '><span class="chat-share-k">City or town</span><input type="text" class="chat-share-in" data-chat-share-field="city" value="' + esc(s.city) + '" maxlength="80" autocomplete="off" spellcheck="false" autocapitalize="words"></label>' +
        '<label class="chat-share-row"><span class="chat-share-k">Name shown</span><input type="text" class="chat-share-in" data-chat-share-field="author" value="' + esc(s.author) + '" maxlength="' + l.name + '" placeholder="Whistleblower" autocomplete="off" spellcheck="false"></label>' +
        '<label class="chat-share-notebox"><span class="chat-share-k">Your note</span><textarea class="chat-share-in chat-share-note" data-chat-share-field="note" rows="3" maxlength="' + l.max + '" spellcheck="true" autocapitalize="sentences">' + esc(s.note) + '</textarea></label>' +
        '<label class="nf-check chat-share-ack"><input type="checkbox" data-chat-share-ack' + (s.ack ? ' checked' : '') + '><span>I have left out my name and anything that identifies me.</span></label>' +
        '<p class="no-indent chat-share-status" role="status" aria-live="polite"></p>' +
      '</div><div class="chat-share-checks">' + checksHtml() + '</div>' +
      '<p class="no-indent chat-share-help">You can also tell me here: “add: …”, “sign it …”, or say what to change, and the chat model rewrites the note. To attach a photo or a PDF, use Edit in the form.</p>';
    var div = clio(html, [
      { label: 'Send to the editor', act: 'send', primary: true },
      { label: 'Edit in the form', act: 'form' },
      { label: 'Cancel', act: 'cancel' }
    ]);
    s.card = div;
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
    else if (f === 'name') {
      var name = v.replace(/\s+/g, ' ').trim(), hit = findPlaces(name).exact;
      s.name = name;
      if (hit) { s.place = hit; s.isNew = false; s.name = hit.name; } else { s.place = null; s.isNew = name.length >= 2; }
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
    if ((m = t.match(/^(?:the )?place(?: is)?\s*[:,]?\s+(.+)$/i) || t.match(/^it'?s about\s+(.+)$/i) || t.match(/^it is about\s+(.+)$/i))) {
      s.city = '';
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
    if (!s.place && !s.isNew) return fail('Write the place the note is about.');
    if (s.isNew && !s.city) { var cityIn = card.querySelector('[data-chat-share-field="city"]'); if (cityIn) cityIn.focus(); return fail('Write the city or town ' + s.name + ' is in.'); }
    if (s.note.length < l.min) return fail('Write at least ' + l.min + ' characters.');
    if (!s.ack) return fail('Tick the box to confirm you have left out anything that identifies you.');
    var body = s.place ? { content: s.note } : { content: s.note, placeName: s.name, city: s.city };
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
    if (d.isNew) set('noteCity', d.city);
    set('noteAuthor', d.author);
    set('workInput', d.note);
    var ack = document.getElementById('noteAck');
    if (ack) { ack.checked = !!d.ack; ack.dispatchEvent(new Event('change', { bubbles: true })); }
    if (typeof window.atlasNotePlace === 'function') window.atlasNotePlace();
  }

  function fresh() { return { step: 'place', place: null, isNew: false, name: '', city: '', note: '', author: '', ack: false, card: null, suggest: '' }; }
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
    clio(p('Tell me what you know, a few questions at a time. Archives kept what someone could pay to keep; what you remember can stand beside the record. The editor reads every note before anything goes on the atlas.'));
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
      case 'city':
        s.city = text.replace(/\.$/, '').slice(0, 80);
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
