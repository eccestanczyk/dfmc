/* ============================================================
   HERUMON TOWER — service worker
   Purpose: defeat GitHub Pages' blanket `cache-control: max-age=600`,
   which makes the browser serve stale HTML/CSS/JS for 10 minutes
   without even revalidating. Pages gives no control over headers,
   so we override caching behaviour on the client instead.

   Strategy: NETWORK-FIRST for every same-origin request.
     - online  -> always fetch fresh from the network, then cache it
     - offline -> fall back to the last cached copy
   Net effect: the codex is never stale while you have a connection,
   and still opens offline.

   Kill switch: bump KILL to true, deploy, load any page once — the
   worker unregisters itself and wipes its caches.
   ============================================================ */

const VERSION = 'ht-v1';
const KILL = false;

self.addEventListener('install', (e) => {
  // take over immediately, don't wait for old tabs to close
  self.skipWaiting();
});

self.addEventListener('activate', (e) => {
  e.waitUntil((async () => {
    if (KILL) {
      const keys = await caches.keys();
      await Promise.all(keys.map((k) => caches.delete(k)));
      await self.registration.unregister();
      const cs = await self.clients.matchAll({ type: 'window' });
      cs.forEach((c) => c.navigate(c.url));
      return;
    }
    // drop caches from older versions
    const keys = await caches.keys();
    await Promise.all(keys.filter((k) => k !== VERSION).map((k) => caches.delete(k)));
    await self.clients.claim();
  })());
});

self.addEventListener('fetch', (e) => {
  const req = e.request;

  if (KILL) return;                                  // pass straight through
  if (req.method !== 'GET') return;                  // never touch writes

  const url = new URL(req.url);
  if (url.origin !== self.location.origin) return;   // let raw.githubusercontent / CDN handle themselves

  e.respondWith((async () => {
    try {
      // `cache: 'no-store'` stops the HTTP cache from short-circuiting us
      const fresh = await fetch(req, { cache: 'no-store' });
      if (fresh && fresh.ok) {
        const cache = await caches.open(VERSION);
        cache.put(req, fresh.clone());
      }
      return fresh;
    } catch (err) {
      const cached = await caches.match(req);
      if (cached) return cached;
      throw err;
    }
  })());
});
