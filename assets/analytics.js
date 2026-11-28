// Visit counting, without cookies and without anyone else's script. Off until window.ATLAS_ANALYTICS_URL (assets/config.js)
// holds the count address of a GoatCounter site, e.g. 'https://culture-atlas.goatcounter.com/count'.
//
// What is sent, as one small request per count: the page's path (never its query string or hash), its title, the site
// that linked here, and the screen width. For the three events below, a name instead of a path. Nothing is stored in the
// browser, so a visitor is not followed from one day to the next. Never sent: what is typed into the chat, the text or
// files of a note, the settings, an API key.
//
// Nothing is sent when the browser asks not to be tracked (Do Not Track or Global Privacy Control), on localhost or a
// file opened from disk, or while a page is only being prerendered.
//
// Events: 'record/<id>' when a record is opened, 'chat/question' when a question is put to the chat (the words are not
// sent), 'gossip/on' when Gossip mode is switched on. window.atlasCount(name) adds one from anywhere on the page.
(function () {
  'use strict';
  var url = String(window.ATLAS_ANALYTICS_URL || '').replace(/\/+$/, '');
  var off = !/^https:\/\//.test(url)
    || navigator.doNotTrack === '1' || window.doNotTrack === '1' || navigator.globalPrivacyControl === true
    || location.protocol === 'file:'
    || /(^localhost$|^127\.|^10\.|^192\.168\.|^0\.0\.0\.0$|\.local$)/.test(location.hostname);

  function send(data) {
    if (off || document.visibilityState === 'prerender') return;
    data.s = window.screen ? window.screen.width : '';
    data.rnd = Math.random().toString(36).slice(2, 7);
    var q = Object.keys(data).filter(function (k) { return data[k] !== '' && data[k] != null && data[k] !== false; })
      .map(function (k) { return encodeURIComponent(k) + '=' + encodeURIComponent(data[k]); }).join('&');
    try {
      if (!(navigator.sendBeacon && navigator.sendBeacon(url + '?' + q))) { new Image().src = url + '?' + q; }
    } catch (e) { /* counting never breaks the page */ }
  }

  var last = '', lastAt = 0;
  window.atlasCount = function (name, title) {
    name = String(name || '').slice(0, 120);
    var now = Date.now();
    if (!name || (name === last && now - lastAt < 2000)) return;   // one open, one count
    last = name; lastAt = now;
    send({ p: name, t: title ? String(title).slice(0, 120) : '', e: true });
  };

  function view() {
    var ref = '';
    try { if (document.referrer && new URL(document.referrer).host !== location.host) ref = document.referrer.split('?')[0]; } catch (e) {}
    send({ p: location.pathname, t: document.title, r: ref });
  }
  if (document.visibilityState === 'visible' || !('visibilityState' in document)) view();
  else document.addEventListener('visibilitychange', function once() {
    if (document.visibilityState !== 'visible') return;
    document.removeEventListener('visibilitychange', once); view();
  });
})();
