// Writing aids for the whistleblower note (the Share information form): spelling corrected as the reader types, and
// dictation. Everything here runs in the reader's browser. The note's text is never sent anywhere to be checked; the
// only thing that leaves the page is the note itself, when the reader presses Send. Dictation is the one exception the
// reader is told about first: unless the browser can turn speech into text on the device, it sends the audio to its maker.
(function () {
  'use strict';
  const box = document.getElementById('workInput');
  const autoBox = document.getElementById('noteAutoCorrect');
  const micBtn = document.getElementById('noteDictateBtn');
  const info = document.getElementById('noteDictateInfo');
  if (!box) return;
  const inNote = () => document.body.classList.contains('chat-input-mode-active');
  const lang = (navigator.language || 'en-US');
  const english = /^en\b/i.test(lang);

  // ---- Spelling, corrected as the reader types ----------------------------------------------------------------------
  // Only misspellings that are not words in English or in the other languages the atlas covers, so a correct word is never
  // changed. A word is corrected when the reader finishes it (a space, a line break or punctuation after it).
  const TYPOS = {
    abscence: 'absence', accidently: 'accidentally', accomodate: 'accommodate', accomodation: 'accommodation',
    acheive: 'achieve', acheived: 'achieved', acknowlege: 'acknowledge', acknowleged: 'acknowledged', acquaintence: 'acquaintance',
    acquited: 'acquitted', adress: 'address', adressed: 'addressed', agressive: 'aggressive', alot: 'a lot', allready: 'already',
    amatuer: 'amateur', anually: 'annually', apparantly: 'apparently', appearence: 'appearance', arguement: 'argument',
    assistent: 'assistant', athiest: 'atheist', aweful: 'awful', basicly: 'basically', becuase: 'because', becasue: 'because',
    begining: 'beginning', beleive: 'believe', beleived: 'believed', belive: 'believe', bizzare: 'bizarre', buisness: 'business',
    calender: 'calendar', carribean: 'Caribbean', catagory: 'category', cemetary: 'cemetery', changable: 'changeable',
    cheif: 'chief', collegue: 'colleague', collegues: 'colleagues', comming: 'coming', commitee: 'committee', committment: 'commitment',
    completly: 'completely', concious: 'conscious', consciencious: 'conscientious', curiousity: 'curiosity', definately: 'definitely',
    definatly: 'definitely', definitly: 'definitely', dissapoint: 'disappoint', dissapointed: 'disappointed', dilemna: 'dilemma',
    dosent: "doesn't", embarass: 'embarrass', embarassed: 'embarrassed', embarassing: 'embarrassing', enviroment: 'environment',
    equiptment: 'equipment', excercise: 'exercise', existance: 'existence', experiance: 'experience', explaination: 'explanation',
    familar: 'familiar', finaly: 'finally', florescent: 'fluorescent', foriegn: 'foreign', foward: 'forward', freind: 'friend',
    freinds: 'friends', fullfil: 'fulfil', goverment: 'government', govenment: 'government', grammer: 'grammar', gaurd: 'guard',
    happend: 'happened', harrass: 'harass', harrassment: 'harassment', harrassed: 'harassed', heighth: 'height', heirarchy: 'hierarchy',
    humourous: 'humorous', ignorence: 'ignorance', immediatly: 'immediately', imediately: 'immediately', incidently: 'incidentally',
    independant: 'independent', indispensible: 'indispensable', innoculate: 'inoculate', inteligence: 'intelligence',
    intresting: 'interesting', interupt: 'interrupt', irrelevent: 'irrelevant', knowlege: 'knowledge', liason: 'liaison',
    libary: 'library', lisence: 'licence', maintainance: 'maintenance', maintenence: 'maintenance', managment: 'management',
    millenium: 'millennium', mischievious: 'mischievous', mispell: 'misspell', neccessary: 'necessary', necessery: 'necessary',
    neccesary: 'necessary', negociate: 'negotiate', noticable: 'noticeable', occassion: 'occasion',
    occassionally: 'occasionally', occured: 'occurred', occurence: 'occurrence', occuring: 'occurring', offical: 'official',
    oppurtunity: 'opportunity', opporunity: 'opportunity', paralell: 'parallel', parliment: 'parliament', persistant: 'persistent',
    personell: 'personnel', posession: 'possession', potatos: 'potatoes', prefered: 'preferred', presance: 'presence',
    privelege: 'privilege', priviledge: 'privilege', probaly: 'probably', probabaly: 'probably', proffesional: 'professional',
    profesional: 'professional', promiss: 'promise', pronounciation: 'pronunciation', publically: 'publicly', realy: 'really',
    recieve: 'receive', recieved: 'received', reciept: 'receipt', recomend: 'recommend', recommed: 'recommend',
    recomended: 'recommended', refered: 'referred', relevent: 'relevant', religous: 'religious', remeber: 'remember',
    repitition: 'repetition', resistence: 'resistance', responsability: 'responsibility', resturant: 'restaurant', rythm: 'rhythm',
    sargent: 'sergeant', secratary: 'secretary', seperate: 'separate', seperated: 'separated', seperately: 'separately',
    sieze: 'seize', similiar: 'similar', sincerly: 'sincerely', speach: 'speech', sucess: 'success', succesful: 'successful',
    sucessful: 'successful', supercede: 'supersede', suprise: 'surprise', suprised: 'surprised', tecnical: 'technical',
    tendancy: 'tendency', therefor: 'therefore', threshhold: 'threshold', tommorow: 'tomorrow', tommorrow: 'tomorrow',
    tounge: 'tongue', truely: 'truly', unforseen: 'unforeseen', unfortunatly: 'unfortunately', untill: 'until', vaccum: 'vacuum',
    vehical: 'vehicle', visable: 'visible', wierd: 'weird', wich: 'which', whith: 'with', wiht: 'with', withold: 'withhold',
    writting: 'writing', teh: 'the', taht: 'that', adn: 'and', hte: 'the', thier: 'their', recieving: 'receiving',
    beacuse: 'because', becuse: 'because', becouse: 'because', thats: "that's", dont: "don't", doesnt: "doesn't", didnt: "didn't",
    isnt: "isn't", wasnt: "wasn't", werent: "weren't", havent: "haven't", hasnt: "hasn't", hadnt: "hadn't", couldnt: "couldn't",
    wouldnt: "wouldn't", shouldnt: "shouldn't", arent: "aren't", theyre: "they're", youre: "you're", wouldve: "would've",
    couldve: "could've", shouldve: "should've", ive: "I've", theyve: "they've", weve: "we've", youve: "you've",
    curater: 'curator', exibition: 'exhibition', exhibtion: 'exhibition',
    exhibiton: 'exhibition', exibit: 'exhibit', galery: 'gallery', gallary: 'gallery', musuem: 'museum', meusum: 'museum',
    museam: 'museum', sponser: 'sponsor', sponsered: 'sponsored', sponsorhip: 'sponsorship', donaton: 'donation',
    trustie: 'trustee', trusties: 'trustees', fundng: 'funding', funidng: 'funding', directer: 'director', comission: 'commission',
    comissioned: 'commissioned', artwrok: 'artwork', artowrk: 'artwork', colection: 'collection', collecton: 'collection'
  };
  // Abbreviations after which the next word does not start a sentence.
  const ABBREV = /\b(e\.g|i\.e|etc|vs|cf|approx|dept|mr|mrs|ms|dr|prof|st|inc|ltd)\.$/i;
  const ignored = new Set();   // words the reader put back with Backspace: never corrected again in this visit
  let last = null;             // the latest correction, so Backspace straight after it can undo it

  const STORE = 'atlas-note-autocorrect';
  if (autoBox) {
    let saved = null;
    try { saved = localStorage.getItem(STORE); } catch (e) {}
    autoBox.checked = saved === null ? english : saved === 'on';
    autoBox.addEventListener('change', () => {
      last = null;
      try { localStorage.setItem(STORE, autoBox.checked ? 'on' : 'off'); } catch (e) {}
    });
  }
  const correcting = () => inNote() && (!autoBox || autoBox.checked);

  const sameCase = (model, word) => {
    if (model.length > 1 && model === model.toUpperCase()) return word.toUpperCase();
    if (model[0] === model[0].toUpperCase()) return word[0].toUpperCase() + word.slice(1);
    return word;
  };
  // True when the next word begins a sentence: at the start of the note, after a line break, or after . ! ? that does not
  // end an abbreviation.
  const startsSentence = (text) => {
    const t = text.replace(/[ \t"'“‘(\[]+$/, '');
    if (!t.trim() || /\n$/.test(t)) return true;
    return /[.!?]["'”’)]*$/.test(t) && !ABBREV.test(t);
  };
  // The corrected form of `word`, or the word itself. `before` is all the text in front of it.
  function correct(word, before) {
    if (ignored.has(word.toLowerCase())) return word;
    let out = word;
    if (english) {
      const lower = word.toLowerCase();
      if (TYPOS[lower] && TYPOS[lower] !== lower) out = sameCase(word, TYPOS[lower]);
      else if (word === 'i') out = 'I';
      else if (/^i'(m|ve|ll|d)$/.test(word)) out = 'I' + word.slice(1);
    }
    // A sentence starts with a capital, except a word that has capitals of its own (iPhone, eBay) or starts a link.
    if (startsSentence(before) && /^[a-z]/.test(out) && !/[A-Z]/.test(out) && !/^(www|https?)$/.test(out)) out = out[0].toUpperCase() + out.slice(1);
    return out;
  }

  // Replaces box[start, end) with text through the editing commands, so the browser's own Undo (Cmd/Ctrl+Z) still works.
  function replaceRange(start, end, text, caret) {
    box.focus();
    box.setSelectionRange(start, end);
    const done = document.execCommand && document.execCommand('insertText', false, text);
    if (!done) { box.setRangeText(text, start, end, 'end'); box.dispatchEvent(new Event('input', { bubbles: true })); }
    box.setSelectionRange(caret, caret);
  }

  box.addEventListener('input', (e) => {
    if (!e.inputType) return;   // dictation and this file's own changes
    if (!correcting()) { last = null; return; }
    if (e.inputType !== 'insertText' && e.inputType !== 'insertLineBreak') {
      if (e.inputType !== 'deleteContentBackward') last = null;
      return;
    }
    // A keyboard sends one character; a phone's suggested word arrives with its space. Either way the last character decides.
    const sep = e.inputType === 'insertLineBreak' ? '\n' : (e.data || '').slice(-1);
    if (!/^[\s.,;:!?)\]"”’]$/.test(sep)) { last = null; return; }
    const caret = box.selectionStart;
    if (caret !== box.selectionEnd) return;
    const v = box.value;
    const wordEnd = caret - sep.length;
    const m = /[A-Za-z']+$/.exec(v.slice(0, wordEnd));
    if (!m) { last = null; return; }
    let word = m[0];
    let start = wordEnd - word.length;
    // Leading apostrophes (quotes) are not part of the word.
    while (word[0] === "'") { word = word.slice(1); start += 1; }
    if (!word) return;
    // Part of a link, an address, a number or a hyphenated word: left as typed.
    const prev = v[start - 1];
    if (prev && !/[\s"“‘(\[]/.test(prev)) { last = null; return; }
    if (sep === '.' && /^(e|i|g|vs|etc|cf|mr|mrs|ms|dr|prof|st)$/i.test(word)) { last = null; return; }
    const fixed = correct(word, v.slice(0, start));
    if (fixed === word) { last = null; return; }
    replaceRange(start, start + word.length, fixed, caret + fixed.length - word.length);
    last = { start, original: word, fixed, sep };
  });

  // Backspace straight after a correction puts the reader's own spelling back, and that word is left alone afterwards.
  box.addEventListener('keydown', (e) => {
    if (e.key !== 'Backspace' || !last || !correcting()) return;
    const end = last.start + last.fixed.length + last.sep.length;
    const caret = box.selectionStart;
    if (caret !== box.selectionEnd || caret !== end || box.value.slice(last.start, end) !== last.fixed + last.sep) { last = null; return; }
    e.preventDefault();
    ignored.add(last.original.toLowerCase());
    const back = last;
    last = null;
    replaceRange(back.start, end, back.original, back.start + back.original.length);
  });
  box.addEventListener('blur', () => { last = null; });

  // ---- Dictation ----------------------------------------------------------------------------------------------------
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!micBtn) return;
  if (!SR) { micBtn.hidden = true; return; }
  micBtn.hidden = false;

  let onDevice = false;     // true when this browser turns speech into text without sending the audio anywhere
  let told = false;         // the reader has read where the audio goes, in this visit
  try { told = sessionStorage.getItem('atlas-note-dictation-told') === '1'; } catch (e) {}
  let rec = null, listening = false, base = '', tail = '', joiner = '', capFirst = false;

  // Chrome 139 and later can recognise speech on the device. Where that is installed, it is used and the reader is told so.
  (async () => {
    try {
      if (typeof SR.available === 'function' && 'processLocally' in SR.prototype) {
        onDevice = (await SR.available({ langs: [lang], processLocally: true })) === 'available';
      }
    } catch (e) { onDevice = false; }
  })();

  const say = (text) => { if (info) { info.textContent = text; info.hidden = !text; } };
  const setButton = () => {
    micBtn.setAttribute('aria-pressed', String(listening));
    micBtn.textContent = listening ? 'Stop dictating' : 'Dictate';
    micBtn.classList.toggle('is-listening', listening);
  };

  function stop() {
    if (rec) { try { rec.stop(); } catch (e) {} }
    listening = false;
    setButton();
  }

  function start() {
    rec = new SR();
    rec.lang = lang;
    rec.continuous = true;
    rec.interimResults = true;
    if (onDevice) { try { rec.processLocally = true; } catch (e) {} }
    const s = box.selectionStart ?? box.value.length;
    const t = box.selectionEnd ?? s;
    base = box.value.slice(0, s);
    tail = box.value.slice(t);
    joiner = base && !/\s$/.test(base) ? ' ' : '';
    capFirst = startsSentence(base);
    rec.onstart = () => { listening = true; setButton(); say('Listening. Speak your note, then press Stop dictating. Check the text before you send it.'); };
    rec.onresult = (event) => {
      let heard = '';
      for (let i = 0; i < event.results.length; i++) heard += event.results[i][0].transcript;
      heard = heard.replace(/\s+/g, ' ').trim();
      if (!heard) return;
      if (capFirst) heard = heard[0].toUpperCase() + heard.slice(1);
      const spacer = tail && !/^\s/.test(tail) ? ' ' : '';
      box.value = base + joiner + heard + spacer + tail;
      const caret = (base + joiner + heard).length;
      box.setSelectionRange(caret, caret);
      box.dispatchEvent(new Event('input', { bubbles: true }));
    };
    rec.onerror = (event) => {
      const why = {
        'not-allowed': 'The microphone is blocked for this site. Allow it in the browser\'s site settings to dictate.',
        'service-not-allowed': 'This browser does not allow dictation here. Use your keyboard\'s own dictation instead.',
        'no-speech': 'No speech was heard. Press Dictate and speak.',
        'audio-capture': 'No microphone was found.',
        'network': 'Dictation needs a connection to the browser\'s speech service.',
        'language-not-supported': 'Dictation does not support this language in this browser.'
      }[event.error];
      if (why) say(why);
      listening = false;
      setButton();
    };
    rec.onend = () => {
      listening = false;
      setButton();
      if (info && /^Listening/.test(info.textContent)) say('Dictation stopped. Check the text before you send it.');
    };
    try { rec.start(); } catch (e) { say('Dictation could not start.'); }
  }

  micBtn.addEventListener('click', (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (listening) { stop(); return; }
    if (!told) {
      told = true;
      try { sessionStorage.setItem('atlas-note-dictation-told', '1'); } catch (err) {}
      say(onDevice
        ? 'This browser turns speech into text on this device. The audio is not sent anywhere. Press Dictate again to start.'
        : 'This browser sends your voice to its maker to turn it into text: Google for Chrome, Microsoft for Edge, Apple for Safari. The atlas receives only the text you send. Press Dictate again to start.');
      setButton();
      return;
    }
    start();
  });

  // Dictation stops when the note screen closes or the note is sent.
  new MutationObserver(() => { if (!inNote()) { if (listening) stop(); say(''); } })
    .observe(document.body, { attributes: true, attributeFilter: ['class'] });
  document.getElementById('workSendBtn')?.addEventListener('click', () => { if (listening) stop(); }, true);
  setButton();
})();
