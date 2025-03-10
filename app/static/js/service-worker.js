// Service Worker for AKC Construction CRM
const CACHE_NAME = 'akc-construction-cache-v1';

// Assets to cache immediately on install
const PRECACHE_ASSETS = [
  '/',
  '/static/css/bootstrap.min.css',
  '/static/js/bootstrap.bundle.min.js',
  '/field/',
  '/field/tasks',
  '/field/quick_log',
  '/auth/login'
];

// Additional URLs to cache when visited
const RUNTIME_CACHE_URLS = [
  /\/field\/.*/,
  /\/static\/.*/,
  /.*\.css/,
  /.*\.js/,
  /.*\.woff2/,
  /.*\.jpg/,
  /.*\.png/,
  /.*\.svg/
];

// Install event - precache static resources
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('Pre-caching assets');
        return cache.addAll(PRECACHE_ASSETS);
      })
      .then(() => self.skipWaiting())
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', event => {
  const currentCaches = [CACHE_NAME];
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return cacheNames.filter(cacheName => !currentCaches.includes(cacheName));
    }).then(cachesToDelete => {
      return Promise.all(cachesToDelete.map(cacheToDelete => {
        return caches.delete(cacheToDelete);
      }));
    }).then(() => self.clients.claim())
  );
});

// Helper function to check if URL should be cached
function shouldCache(url) {
  const parsedUrl = new URL(url);
  
  // Don't cache API requests or authentication endpoints
  if (parsedUrl.pathname.startsWith('/api/') || 
      (parsedUrl.pathname.startsWith('/auth/') && !parsedUrl.pathname.includes('/login'))) {
    return false;
  }
  
  // Check against our runtime cache patterns
  return RUNTIME_CACHE_URLS.some(pattern => {
    if (typeof pattern === 'string') {
      return parsedUrl.pathname === pattern;
    } else {
      return pattern.test(url);
    }
  });
}

// Fetch event - serve from cache or network
self.addEventListener('fetch', event => {
  // Skip cross-origin requests
  if (!event.request.url.startsWith(self.location.origin)) {
    return;
  }
  
  // Handle API requests differently (network-first for fresh data)
  if (event.request.url.includes('/api/')) {
    event.respondWith(
      fetch(event.request)
        .then(response => {
          // Clone the response for the cache and for the return
          const responseToCache = response.clone();
          
          caches.open(CACHE_NAME)
            .then(cache => {
              cache.put(event.request, responseToCache);
            });
            
          return response;
        })
        .catch(() => {
          return caches.match(event.request);
        })
    );
    return;
  }
  
  // For everything else, use cache-first strategy
  event.respondWith(
    caches.match(event.request)
      .then(cachedResponse => {
        if (cachedResponse) {
          // Return cached response
          return cachedResponse;
        }
        
        // Not in cache, fetch from network
        return fetch(event.request)
          .then(response => {
            // Don't cache non-successful responses
            if (!response || response.status !== 200 || response.type !== 'basic') {
              return response;
            }
            
            // Should this response be cached?
            if (shouldCache(event.request.url)) {
              const responseToCache = response.clone();
              caches.open(CACHE_NAME)
                .then(cache => {
                  cache.put(event.request, responseToCache);
                });
            }
            
            return response;
          })
          .catch(error => {
            console.error('Fetch failed:', error);
            
            // For HTML requests, return the offline page
            if (event.request.headers.get('accept').includes('text/html')) {
              return caches.match('/field/offline');
            }
            
            return new Response('Network error', {
              status: 408,
              headers: new Headers({
                'Content-Type': 'text/plain'
              })
            });
          });
      })
  );
});

// Background sync for offline submissions
self.addEventListener('sync', event => {
  if (event.tag === 'sync-time-entries') {
    event.waitUntil(syncTimeEntries());
  } else if (event.tag === 'sync-photos') {
    event.waitUntil(syncPhotos());
  }
});

// Function to sync offline time entries
async function syncTimeEntries() {
  try {
    // Retrieve stored time entries from IndexedDB
    const db = await openDatabase();
    const timeEntries = await getStoredTimeEntries(db);
    
    // For each entry, send to server
    for (const entry of timeEntries) {
      try {
        const response = await fetch('/api/time-entries', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(entry.data)
        });
        
        if (response.ok) {
          // If successful, remove from IndexedDB
          await deleteTimeEntry(db, entry.id);
        }
      } catch (error) {
        console.error('Failed to sync time entry:', error);
      }
    }
  } catch (error) {
    console.error('Error syncing time entries:', error);
  }
}

// Function to sync offline photos
async function syncPhotos() {
  try {
    // Retrieve stored photos from IndexedDB
    const db = await openDatabase();
    const photos = await getStoredPhotos(db);
    
    // For each photo, send to server
    for (const photo of photos) {
      try {
        const formData = new FormData();
        formData.append('photo', photo.data.blob, 'photo.jpg');
        formData.append('project_id', photo.data.project_id);
        formData.append('description', photo.data.description);
        
        const response = await fetch('/field/upload_photo', {
          method: 'POST',
          body: formData
        });
        
        if (response.ok) {
          // If successful, remove from IndexedDB
          await deletePhoto(db, photo.id);
        }
      } catch (error) {
        console.error('Failed to sync photo:', error);
      }
    }
  } catch (error) {
    console.error('Error syncing photos:', error);
  }
}

// IndexedDB helper functions
function openDatabase() {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open('AKC_OfflineStorage', 1);
    
    request.onupgradeneeded = event => {
      const db = event.target.result;
      
      // Create object stores if they don't exist
      if (!db.objectStoreNames.contains('timeEntries')) {
        db.createObjectStore('timeEntries', { keyPath: 'id', autoIncrement: true });
      }
      
      if (!db.objectStoreNames.contains('photos')) {
        db.createObjectStore('photos', { keyPath: 'id', autoIncrement: true });
      }
    };
    
    request.onsuccess = event => resolve(event.target.result);
    request.onerror = event => reject(event.target.error);
  });
}

function getStoredTimeEntries(db) {
  return new Promise((resolve, reject) => {
    const transaction = db.transaction('timeEntries', 'readonly');
    const store = transaction.objectStore('timeEntries');
    const request = store.getAll();
    
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error);
  });
}

function getStoredPhotos(db) {
  return new Promise((resolve, reject) => {
    const transaction = db.transaction('photos', 'readonly');
    const store = transaction.objectStore('photos');
    const request = store.getAll();
    
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error);
  });
}

function deleteTimeEntry(db, id) {
  return new Promise((resolve, reject) => {
    const transaction = db.transaction('timeEntries', 'readwrite');
    const store = transaction.objectStore('timeEntries');
    const request = store.delete(id);
    
    request.onsuccess = () => resolve();
    request.onerror = () => reject(request.error);
  });
}

function deletePhoto(db, id) {
  return new Promise((resolve, reject) => {
    const transaction = db.transaction('photos', 'readwrite');
    const store = transaction.objectStore('photos');
    const request = store.delete(id);
    
    request.onsuccess = () => resolve();
    request.onerror = () => reject(request.error);
  });
} 