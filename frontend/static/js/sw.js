/* Kuhiston offline shell (Этап 6).
   Кэширует статику приложения и тайлы карты, скачанные по региону
   (см. precacheRegionTiles в map.js). */
// Новая версия очищает устаревший CSS, из-за которого контейнер карты мог
// оставаться нулевой ширины у уже посетивших сайт пользователей.
const SHELL_CACHE = "kuhiston-shell-v4";

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(SHELL_CACHE).then((cache) =>
      cache.addAll([
        "/static/css/base.css",
        "/static/css/map.css",
        "/static/js/map.js",
      ]),
    ),
  );
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(
        keys
          .filter((key) => key.startsWith("kuhiston-shell-") && key !== SHELL_CACHE)
          .map((key) => caches.delete(key)),
      ),
    ),
  );
  self.clients.claim();
});

self.addEventListener("fetch", (event) => {
  const url = new URL(event.request.url);

  if (url.hostname.includes("maptiler")) {
    event.respondWith(
      caches.match(event.request).then((cached) => cached || fetch(event.request)),
    );
    return;
  }

  if (event.request.method !== "GET" || url.origin !== self.location.origin) {
    return;
  }

  event.respondWith(
    caches.match(event.request).then((cached) => {
      const network = fetch(event.request)
        .then((resp) => {
          if (resp && resp.status === 200) {
            const clone = resp.clone();
            caches.open(SHELL_CACHE).then((cache) => cache.put(event.request, clone));
          }
          return resp;
        })
        .catch(() => cached);
      return cached || network;
    }),
  );
});
