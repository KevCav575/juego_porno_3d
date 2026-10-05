// Guarda la app en el dispositivo para usarla sin señal. Responde desde la copia
// guardada y la actualiza en segundo plano: los cambios se ven en la siguiente carga.
const CACHE = "tamizaje-v1";
const ARCHIVOS = ["./", "index.html", "app.js", "riesgo.js", "registro.js", "modelo.json", "manifest.webmanifest", "icono.svg"];

self.addEventListener("install", (evento) => {
  evento.waitUntil(caches.open(CACHE).then((c) => c.addAll(ARCHIVOS)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", (evento) => {
  evento.waitUntil(
    caches.keys()
      .then((claves) => Promise.all(claves.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (evento) => {
  const peticion = evento.request;
  if (peticion.method !== "GET" || new URL(peticion.url).origin !== self.location.origin) return;
  evento.respondWith(
    caches.open(CACHE).then(async (cache) => {
      const guardada = await cache.match(peticion, { ignoreSearch: true });
      const deRed = fetch(peticion)
        .then((respuesta) => {
          if (respuesta.ok) cache.put(peticion, respuesta.clone());
          return respuesta;
        })
        .catch(() => guardada);
      return guardada ?? deRed;
    })
  );
});
