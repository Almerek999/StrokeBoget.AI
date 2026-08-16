const CACHE_NAME = 'stroke-ai-v1';
const ASSETS = [
    '/',
    '/manifest.json',
    '/icon.svg'
];

// Установка Service Worker и кэширование файлов
self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME).then(cache => cache.addAll(ASSETS))
    );
});

// Активация и удаление старого кэша
self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys().then(keys => Promise.all(
            keys.map(key => {
                if (key !== CACHE_NAME) {
                    return caches.delete(key);
                }
            })
        ))
    );
});

// Перехват запросов (возвращаем кэш если нет сети)
self.addEventListener('fetch', event => {
    // Не кэшируем API-запросы (POST)
    if (event.request.method !== 'GET') return;
    
    event.respondWith(
        caches.match(event.request).then(cachedResponse => {
            return cachedResponse || fetch(event.request);
        })
    );
});
