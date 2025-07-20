/**
 * Service Worker for CDN caching
 * Implements offline-first strategy for CDN assets
 */

const CACHE_NAME = 'ngx-cdn-v1';
const CDN_CACHE_NAME = 'ngx-cdn-assets-v1';

// CDN configuration received from main thread
let cdnConfig = {
  enabled: false,
  baseUrl: '',
  imageUrl: '',
  staticUrl: '',
};

// Listen for CDN configuration
self.addEventListener('message', (event) => {
  if (event.data.type === 'CDN_CONFIG') {
    cdnConfig = event.data.config;
  }
});

// Install event - cache essential assets
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll([
        '/',
        '/index.html',
        '/manifest.json',
      ]);
    })
  );
  self.skipWaiting();
});

// Activate event - clean old caches
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames
          .filter((name) => name !== CACHE_NAME && name !== CDN_CACHE_NAME)
          .map((name) => caches.delete(name))
      );
    })
  );
  self.clients.claim();
});

// Fetch event - implement caching strategies
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // Check if request is for CDN asset
  const isCDNAsset = cdnConfig.enabled && (
    url.href.startsWith(cdnConfig.baseUrl) ||
    url.href.startsWith(cdnConfig.imageUrl) ||
    url.href.startsWith(cdnConfig.staticUrl)
  );

  if (isCDNAsset) {
    // CDN assets - cache first, fallback to network
    event.respondWith(
      caches.open(CDN_CACHE_NAME).then((cache) => {
        return cache.match(request).then((cachedResponse) => {
          if (cachedResponse) {
            // Return cached version and update in background
            fetch(request).then((networkResponse) => {
              cache.put(request, networkResponse.clone());
            }).catch(() => {});
            return cachedResponse;
          }

          // Not in cache, fetch from network
          return fetch(request).then((networkResponse) => {
            // Cache successful responses
            if (networkResponse.ok) {
              cache.put(request, networkResponse.clone());
            }
            return networkResponse;
          });
        });
      })
    );
  } else if (request.mode === 'navigate') {
    // Navigation requests - network first, fallback to cache
    event.respondWith(
      fetch(request).catch(() => {
        return caches.match('/index.html');
      })
    );
  } else {
    // Other requests - network first
    event.respondWith(
      fetch(request).catch(() => {
        return caches.match(request);
      })
    );
  }
});

// Background sync for offline actions
self.addEventListener('sync', (event) => {
  if (event.tag === 'sync-cdn-assets') {
    event.waitUntil(syncCDNAssets());
  }
});

// Periodic background sync (if supported)
self.addEventListener('periodicsync', (event) => {
  if (event.tag === 'update-cdn-cache') {
    event.waitUntil(updateCDNCache());
  }
});

/**
 * Sync CDN assets when back online
 */
async function syncCDNAssets() {
  const cache = await caches.open(CDN_CACHE_NAME);
  const requests = await cache.keys();
  
  for (const request of requests) {
    try {
      const response = await fetch(request);
      if (response.ok) {
        await cache.put(request, response);
      }
    } catch (error) {
      console.error('Failed to sync CDN asset:', request.url);
    }
  }
}

/**
 * Update CDN cache periodically
 */
async function updateCDNCache() {
  const cache = await caches.open(CDN_CACHE_NAME);
  const requests = await cache.keys();
  
  // Update stale assets
  const ONE_DAY = 24 * 60 * 60 * 1000;
  const now = Date.now();
  
  for (const request of requests) {
    const response = await cache.match(request);
    if (response) {
      const dateHeader = response.headers.get('date');
      if (dateHeader) {
        const responseDate = new Date(dateHeader).getTime();
        if (now - responseDate > ONE_DAY) {
          // Asset is older than one day, update it
          try {
            const freshResponse = await fetch(request);
            if (freshResponse.ok) {
              await cache.put(request, freshResponse);
            }
          } catch (error) {
            console.error('Failed to update CDN asset:', request.url);
          }
        }
      }
    }
  }
}