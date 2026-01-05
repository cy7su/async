const STATIC_CACHE = "async-pw-static-v1";
const DYNAMIC_CACHE = "async-pw-dynamic-v1";

// Ресурсы для кеширования
const STATIC_ASSETS = [
  "/",
  "/static/css/styles.css",
  "/static/js/main.js",
  "https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;600&display=swap",
];

// Установка Service Worker
self.addEventListener("install", (event) => {
  console.log("Service Worker: Installing...");

  event.waitUntil(
    caches
      .open(STATIC_CACHE)
      .then((cache) => {
        console.log("Service Worker: Caching static assets");
        return cache.addAll(STATIC_ASSETS);
      })
      .then(() => {
        console.log("Service Worker: Installation complete");
        return self.skipWaiting();
      }),
  );
});

// Активация Service Worker
self.addEventListener("activate", (event) => {
  console.log("Service Worker: Activating...");

  event.waitUntil(
    caches
      .keys()
      .then((cacheNames) => {
        return Promise.all(
          cacheNames.map((cacheName) => {
            if (cacheName !== STATIC_CACHE && cacheName !== DYNAMIC_CACHE) {
              console.log("Service Worker: Deleting old cache:", cacheName);
              return caches.delete(cacheName);
            }
          }),
        );
      })
      .then(() => {
        console.log("Service Worker: Activation complete");
        return self.clients.claim();
      }),
  );
});

// Перехват запросов
self.addEventListener("fetch", (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // Стратегия кеширования для разных типов ресурсов
  if (request.method === "GET") {
    if (url.pathname.startsWith("/static/")) {
      // Статические ресурсы - Cache First
      event.respondWith(cacheFirst(request));
    } else if (url.pathname.startsWith("/api/")) {
      // API - Network First
      event.respondWith(networkFirst(request));
    } else {
      // HTML страницы - Stale While Revalidate
      event.respondWith(staleWhileRevalidate(request));
    }
  }
});

/**
 * Cache First стратегия
 * Сначала проверяем кеш, затем сеть
 */
async function cacheFirst(request) {
  try {
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }

    const networkResponse = await fetch(request);
    if (networkResponse.ok) {
      const cache = await caches.open(STATIC_CACHE);
      cache.put(request, networkResponse.clone());
    }

    return networkResponse;
  } catch (error) {
    console.error("Cache First error:", error);
    return new Response("Offline", {
      status: 503,
    });
  }
}

/**
 * Network First стратегия
 * Сначала сеть, затем кеш
 */
async function networkFirst(request) {
  try {
    const networkResponse = await fetch(request);
    if (networkResponse.ok) {
      const cache = await caches.open(DYNAMIC_CACHE);
      cache.put(request, networkResponse.clone());
    }
    return networkResponse;
  } catch (error) {
    console.log("Network failed, trying cache:", error);
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    return new Response("Offline", {
      status: 503,
    });
  }
}

/**
 * Stale While Revalidate стратегия
 * Возвращаем кеш, обновляем в фоне
 */
async function staleWhileRevalidate(request) {
  const cache = await caches.open(DYNAMIC_CACHE);
  const cachedResponse = await cache.match(request);

  const fetchPromise = fetch(request)
    .then((networkResponse) => {
      if (networkResponse.ok) {
        cache.put(request, networkResponse.clone());
      }
      return networkResponse;
    })
    .catch(() => cachedResponse);

  return cachedResponse || fetchPromise;
}

// Фоновые задачи
self.addEventListener("message", (event) => {
  if (event.data && event.data.type === "SKIP_WAITING") {
    self.skipWaiting();
  }
});

// Периодическая очистка кеша
self.addEventListener("periodicsync", (event) => {
  if (event.tag === "cache-cleanup") {
    event.waitUntil(cleanupCache());
  }
});

async function cleanupCache() {
  const cacheNames = await caches.keys();
  const oldCaches = cacheNames.filter(
    (name) => name !== STATIC_CACHE && name !== DYNAMIC_CACHE,
  );

  await Promise.all(oldCaches.map((cacheName) => caches.delete(cacheName)));

  console.log("Service Worker: Cache cleanup completed");
}
