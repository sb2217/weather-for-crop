// AgriWeather PWA Service Worker
const CACHE_NAME = 'agriweather-cache-v1';
const ASSETS_TO_CACHE = [
  './index.html',
  './manifest.json',
  './static/crop_weather_bg.jpg',
  './static/w_bg.png'
];

self.addEventListener('install', (e) => {
  e.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(ASSETS_TO_CACHE))
  );
  self.skipWaiting();
});

self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.map((key) => {
          if (key !== CACHE_NAME) return caches.delete(key);
        })
      );
    })
  );
  self.clients.claim();
});

self.addEventListener('fetch', (e) => {
  // Network first, then cache fallback
  e.respondWith(
    fetch(e.request).catch(() => caches.match(e.request))
  );
});
