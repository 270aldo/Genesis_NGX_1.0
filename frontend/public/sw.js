/**
 * Service Worker for GENESIS Frontend Performance Optimization
 * ==========================================================
 *
 * Features:
 * - Static asset caching with versioning
 * - API response caching with TTL
 * - Offline fallbacks
 * - Chunk preloading optimization
 * - Background sync for critical operations
 */

const CACHE_NAME = 'genesis-v1';
const API_CACHE_NAME = 'genesis-api-v1';
const IMAGE_CACHE_NAME = 'genesis-images-v1';
const CDN_CACHE_NAME = 'ngx-cdn-assets-v1';

const STATIC_ASSETS = [
  '/',
  '/index.html',
  '/favicon.ico',
  '/robots.txt',
  '/manifest.json'
];

const API_CACHE_PATTERNS = [
  '/api/agents',
  '/api/chat',
  '/api/user/profile',
];

// CDN configuration received from main thread
let cdnConfig = {
  enabled: false,
  baseUrl: '',
  imageUrl: '',
  staticUrl: '',
};

// Listen for messages from main thread
self.addEventListener('message', (event) => {
  const { type, data } = event.data;

  switch (type) {
    case 'SKIP_WAITING':
      self.skipWaiting();
      break;

    case 'CDN_CONFIG':
      cdnConfig = data.config;
      break;

    case 'PRELOAD_ROUTES':
      preloadRoutes(data.routes);
      break;

    default:
      console.log('Unknown message type:', type);
  }
});

// Install event - cache static assets
self.addEventListener('install', (event) => {
  event.waitUntil(
    Promise.all([
      // Cache static assets
      caches.open(CACHE_NAME).then((cache) => {
        return cache.addAll(STATIC_ASSETS);
      }),

      // Skip waiting to activate immediately
      self.skipWaiting()
    ])
  );
});

// Activate event - cleanup old caches
self.addEventListener('activate', (event) => {
  event.waitUntil(
    Promise.all([
      // Clean up old caches
      caches.keys().then((cacheNames) => {
        return Promise.all(
          cacheNames.map((cacheName) => {
            if (cacheName !== CACHE_NAME &&
                cacheName !== API_CACHE_NAME &&
                cacheName !== IMAGE_CACHE_NAME &&
                cacheName !== CDN_CACHE_NAME) {
              return caches.delete(cacheName);
            }
          })
        );
      }),

      // Take control of all clients
      self.clients.claim()
    ])
  );
});

// Fetch event - implement caching strategies
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // Handle different types of requests
  if (request.method === 'GET') {
    // Static assets (JS, CSS, fonts)
    if (isStaticAsset(request)) {
      event.respondWith(handleStaticAsset(request));
    }
    // Images
    else if (isImage(request)) {
      event.respondWith(handleImage(request));
    }
    // API calls
    else if (isApiCall(request)) {
      event.respondWith(handleApiCall(request));
    }
    // CDN assets
    else if (isCDNAsset(request)) {
      event.respondWith(handleCDNAsset(request));
    }
    // HTML pages
    else if (request.headers.get('accept')?.includes('text/html')) {
      event.respondWith(handleHtmlRequest(request));
    }
  }
});

// Handle static assets with cache-first strategy
async function handleStaticAsset(request) {
  try {
    const cache = await caches.open(CACHE_NAME);
    const cachedResponse = await cache.match(request);

    if (cachedResponse) {
      // Return cached version and update in background
      updateCache(cache, request);
      return cachedResponse;
    }

    // Fetch and cache
    const response = await fetch(request);
    if (response.ok) {
      cache.put(request, response.clone());
    }
    return response;

  } catch (error) {
    console.error('Static asset fetch failed:', error);
    return new Response('Asset not available offline', { status: 503 });
  }
}

// Handle images with cache-first strategy and compression
async function handleImage(request) {
  try {
    const cache = await caches.open(IMAGE_CACHE_NAME);
    const cachedResponse = await cache.match(request);

    if (cachedResponse) {
      return cachedResponse;
    }

    const response = await fetch(request);
    if (response.ok) {
      // Cache images for longer periods
      const responseToCache = response.clone();
      cache.put(request, responseToCache);
    }
    return response;

  } catch (error) {
    console.error('Image fetch failed:', error);
    // Return placeholder image
    return createPlaceholderImage();
  }
}

// Handle API calls with network-first strategy and TTL
async function handleApiCall(request) {
  const cache = await caches.open(API_CACHE_NAME);

  try {
    // Try network first for fresh data
    const response = await fetch(request);

    if (response.ok) {
      // Cache successful responses with timestamp
      const responseToCache = response.clone();
      const cacheKey = createCacheKey(request);

      // Add timestamp for TTL management
      const cacheEntry = {
        response: await responseToCache.text(),
        timestamp: Date.now(),
        ttl: getTTL(request.url),
        headers: Object.fromEntries(response.headers.entries())
      };

      cache.put(cacheKey, new Response(JSON.stringify(cacheEntry), {
        headers: { 'Content-Type': 'application/json' }
      }));
    }

    return response;

  } catch (error) {
    // Network failed, try cache
    const cachedData = await getCachedApiResponse(cache, request);
    if (cachedData) {
      return new Response(cachedData.response, {
        headers: cachedData.headers
      });
    }

    // Return offline indicator
    return new Response(JSON.stringify({
      error: 'Offline',
      message: 'Request failed and no cached data available'
    }), {
      status: 503,
      headers: { 'Content-Type': 'application/json' }
    });
  }
}

// Handle CDN assets
async function handleCDNAsset(request) {
  const cache = await caches.open(CDN_CACHE_NAME);
  const cachedResponse = await cache.match(request);

  if (cachedResponse) {
    // Return cached version and update in background
    fetch(request).then((networkResponse) => {
      if (networkResponse.ok) {
        cache.put(request, networkResponse.clone());
      }
    }).catch(() => {});
    return cachedResponse;
  }

  // Not in cache, fetch from network
  try {
    const response = await fetch(request);
    if (response.ok) {
      cache.put(request, response.clone());
    }
    return response;
  } catch (error) {
    return new Response('CDN asset not available offline', { status: 503 });
  }
}

// Handle HTML requests with network-first, cache fallback
async function handleHtmlRequest(request) {
  try {
    const response = await fetch(request);
    if (response.ok) {
      const cache = await caches.open(CACHE_NAME);
      cache.put(request, response.clone());
    }
    return response;

  } catch (error) {
    // Try cache first
    const cache = await caches.open(CACHE_NAME);
    const cachedResponse = await cache.match(request);

    if (cachedResponse) {
      return cachedResponse;
    }

    // Return offline page
    return caches.match('/index.html');
  }
}

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

// Utility functions
function isStaticAsset(request) {
  const url = new URL(request.url);
  return /\.(js|css|woff|woff2|ttf|otf)$/i.test(url.pathname);
}

function isImage(request) {
  const url = new URL(request.url);
  return /\.(jpg|jpeg|png|gif|webp|svg|avif)$/i.test(url.pathname);
}

function isApiCall(request) {
  const url = new URL(request.url);
  return url.pathname.startsWith('/api/') ||
         API_CACHE_PATTERNS.some(pattern => url.pathname.includes(pattern));
}

function isCDNAsset(request) {
  const url = new URL(request.url);
  return cdnConfig.enabled && (
    url.href.startsWith(cdnConfig.baseUrl) ||
    url.href.startsWith(cdnConfig.imageUrl) ||
    url.href.startsWith(cdnConfig.staticUrl)
  );
}

function createCacheKey(request) {
  const url = new URL(request.url);
  return `${url.pathname}${url.search}`;
}

function getTTL(url) {
  // Different TTL based on endpoint
  if (url.includes('/api/user/')) return 5 * 60 * 1000; // 5 minutes
  if (url.includes('/api/agents/')) return 10 * 60 * 1000; // 10 minutes
  if (url.includes('/api/chat/')) return 2 * 60 * 1000; // 2 minutes
  return 60 * 1000; // 1 minute default
}

async function getCachedApiResponse(cache, request) {
  const cacheKey = createCacheKey(request);
  const cached = await cache.match(cacheKey);

  if (!cached) return null;

  try {
    const cacheEntry = JSON.parse(await cached.text());
    const isExpired = Date.now() - cacheEntry.timestamp > cacheEntry.ttl;

    if (isExpired) {
      cache.delete(cacheKey);
      return null;
    }

    return cacheEntry;
  } catch (error) {
    return null;
  }
}

async function updateCache(cache, request) {
  try {
    const response = await fetch(request);
    if (response.ok) {
      cache.put(request, response);
    }
  } catch (error) {
    // Ignore errors in background updates
  }
}

function createPlaceholderImage() {
  const svg = `
    <svg width="400" height="300" xmlns="http://www.w3.org/2000/svg">
      <rect width="100%" height="100%" fill="#f0f0f0"/>
      <text x="50%" y="50%" text-anchor="middle" fill="#999" font-family="Arial" font-size="16">
        Image unavailable offline
      </text>
    </svg>
  `;

  return new Response(svg, {
    headers: {
      'Content-Type': 'image/svg+xml',
      'Cache-Control': 'no-cache'
    }
  });
}

async function preloadRoutes(routes) {
  const cache = await caches.open(CACHE_NAME);

  for (const route of routes) {
    try {
      const response = await fetch(route);
      if (response.ok) {
        cache.put(route, response);
      }
    } catch (error) {
      console.warn(`Failed to preload route: ${route}`, error);
    }
  }
}

// Background sync for critical operations
self.addEventListener('sync', (event) => {
  if (event.tag === 'chat-messages') {
    event.waitUntil(syncChatMessages());
  }
  if (event.tag === 'user-profile') {
    event.waitUntil(syncUserProfile());
  }
});

async function syncChatMessages() {
  // Implement chat message syncing logic
  console.log('Syncing chat messages in background');
}

async function syncUserProfile() {
  // Implement user profile syncing logic
  console.log('Syncing user profile in background');
}

// Performance monitoring
console.log('🔧 GENESIS Service Worker installed with performance optimizations');
