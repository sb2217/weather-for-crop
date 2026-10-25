// AgriWeather PWA Service Worker v7 - Interactive Manual Soil Lab
const CACHE_NAME = 'agriweather-cache-v7';
const ASSETS_TO_CACHE = [
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
  const url = e.request.url;
  // NEVER cache live hardware telemetry or Telegram API calls
  if (url.includes('telegram.org') || url.includes('projectiot.in') || url.includes('open-meteo.com')) {
    return;
  }

  // Network-first strategy for everything else
  e.respondWith(
    fetch(e.request)
      .then((res) => {
        return res;
      })
      .catch(() => caches.match(e.request))
  );
});
