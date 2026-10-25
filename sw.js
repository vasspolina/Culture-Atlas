// Culture Atlas Service Worker (network-first for the page, same-origin cache only)
const CACHE_NAME = 'culture-atlas-v286';
const ASSETS_TO_CACHE = [
  './',
  './index.html',
  './reports-admin.html',
  './manifest.json',
  './assets/atlas.css',
  './assets/maplibre-gl.css',
  './assets/layers.js',
  './assets/hq-detail.js',
  './assets/bubbles.js',
  './assets/money-maps.json',
  './assets/hq.json',
  './assets/config.js',
  './assets/typeset.js'
];

self.addEventListener('install', (event) => {
  self.skipWaiting();
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(ASSETS_TO_CACHE).catch(() => {});
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

  const isNavigation = event.request.mode === 'navigate' || event.request.destination === 'document';

  // NETWORK-FIRST FOR THE PAGE: always the server's current copy; the cached copy only when the network fails.
  if (isNavigation) {
    event.respondWith(
      fetch(event.request, { cache: 'no-cache' }).then((networkResponse) => {
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
    fetch(event.request, { cache: 'no-cache' }).then((networkResponse) => {
      if (networkResponse && networkResponse.status === 200) {
        const responseToCache = networkResponse.clone();
        caches.open(CACHE_NAME).then((cache) => {
          cache.put(event.request, responseToCache);
        });
      }
      return networkResponse;
    }).catch(() => {
      return caches.match(event.request);
    })
  );
});
