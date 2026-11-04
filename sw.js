// Culture Atlas Service Worker (network-first for the page, same-origin cache only)
const CACHE_NAME = 'culture-atlas-v509';
const ASSETS_TO_CACHE = [
  './',
  './index.html',
  './assets/institutions.js',
  './reports-admin.html',
  './manifest.json',
  './assets/icons/icon-192.png',
  './assets/icons/icon-512.png',
  './assets/icons/icon-512-maskable.png',
  './assets/icons/apple-touch-icon-180.png',
  './assets/icons/chat-mark.svg',
  './assets/atlas.css',
  './assets/maplibre-gl.css',
  './assets/layers.js',
  './assets/hq-detail.js',
  './assets/bubbles.js',
  './assets/money-maps.json',
  './assets/studies.json',
  './studies.html',
  './moma-money-map.html',
  './assets/hq.json',
  './assets/config.js',
  './assets/typeset.js',
  './assets/phone-maps.js',
  './assets/desktop-maps.js',
  './assets/chat-resize.js',
  './assets/subtopic.js',
  './assets/names.js',
  './assets/grounding.js'
];

self.addEventListener('install', (event) => {
  self.skipWaiting();
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return Promise.all(
        ASSETS_TO_CACHE.map((u) =>
          fetch(u, { cache: 'no-cache' })
            .then((r) => (r && r.status === 200 ? cache.put(u, r) : null))
            .catch(() => {})
        )
      );
    })
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key))
      );
    })
  );
  self.clients.claim();
  // Tell every open page which release is now live. The page decides whether to reload: a page that already
  // loaded this release stays as it is (the worker used to navigate every window here, which wiped a chat
  // that had just begun), and a page from an older release reloads only when nothing is in progress on it.
  event.waitUntil(self.clients.matchAll({ type: 'window', includeUncontrolled: true }).then((windows) => {
    windows.forEach((w) => { try { w.postMessage({ type: 'atlas-release', cache: CACHE_NAME }); } catch (e) {} });
  }));
});

self.addEventListener('fetch', (event) => {
  if (event.request.method !== 'GET') return;

  // Other sites answer for themselves: nothing from them is cached here, so lookups are never served stale.
  let url;
  try { url = new URL(event.request.url); } catch (e) { return; }
  if (url.origin !== self.location.origin) return;
  // The latest-reports feed (assets/live.json and the stamp the page checks every minute) always comes from the network and
  // is never stored: each check has its own address, so storing them would fill the cache, and an old copy is no use.
  if (/\/assets\/live(-stamp)?\.json$/.test(url.pathname)) return;

  const isNavigation = event.request.mode === 'navigate' || event.request.destination === 'document';

  // NETWORK-FIRST FOR THE PAGE: always the server's current copy; the cached copy only when the network fails.
  if (isNavigation) {
    event.respondWith(
      fetch(event.request.url, { cache: 'no-cache' }).then((networkResponse) => {
        if (networkResponse && networkResponse.status === 200) {
          const responseToCache = networkResponse.clone();
          caches.open(CACHE_NAME).then((cache) => {
            cache.put(event.request, responseToCache);
          });
        }
        return networkResponse;
      }).catch(() => {
        return caches.match(event.request, { ignoreSearch: true })
          .then((res) => res || caches.match('./index.html'))
          .then((res) => res || caches.match('./'));
      })
    );
    return;
  }

  // Network-first with cache fallback for the page's own files
  // Revalidated on every load, so a release is never hidden behind the host's ten-minute HTTP cache.
  event.respondWith(
    fetch(event.request.url, { cache: 'no-cache' }).then((networkResponse) => {
      if (networkResponse && networkResponse.status === 200) {
        const responseToCache = networkResponse.clone();
        caches.open(CACHE_NAME).then((cache) => {
          cache.put(event.request, responseToCache);
        });
      }
      return networkResponse;
    }).catch(() => {
      // The page asks for its files with a `?v=` release number; the copies put away at install have none. Offline,
      // either copy will do, so the search part is ignored.
      return caches.match(event.request, { ignoreSearch: true });
    })
  );
});
