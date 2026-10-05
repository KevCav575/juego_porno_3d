// Registro de campo: se guarda en el dispositivo (IndexedDB) y se descarga como
// CSV con las mismas columnas que escribe guardar_registro() en nmist.py.

export const CAMPOS = [
  "fecha", "sexo", "dx_diabetes", "dx_hipertension", "edad", "actividad_min", "talla_cm",
  "cintura_cm", "peso_kg", "glucosa", "en_ayuno", "tas", "tad", "sintomas_alarma",
  "c1_familiar_diabetes", "c3_diabetes_gestacional", "c4_prediabetes", "c5_fuma",
  "puntos_total", "diabetes_nivel", "diabetes_escala", "diabetes_prob",
  "hta_nivel", "hta_escala", "hta_prob",
];

/** Convierte las respuestas al formato en que la persona las dio. */
function valorLegible(v) {
  if (v == null) return "";
  if (typeof v === "boolean") return v ? "si" : "no";
  return v;
}

function porcentaje(p) {
  return p == null ? "" : `${(p * 100).toFixed(1)}%`;
}

function fechaLocal(d) {
  const dos = (n) => String(n).padStart(2, "0");
  return `${d.getFullYear()}-${dos(d.getMonth() + 1)}-${dos(d.getDate())}` +
    `T${dos(d.getHours())}:${dos(d.getMinutes())}:${dos(d.getSeconds())}`;
}

export function construirFila(r, res, fecha = new Date()) {
  const fila = { fecha: fechaLocal(fecha) };
  for (const [k, v] of Object.entries(r)) {
    fila[k] = valorLegible(v);
  }
  fila.sexo = r.mujer ? "mujer" : "hombre";
  fila.puntos_total = res.puntos_total;
  fila.diabetes_nivel = res.diabetes.nivel;
  fila.diabetes_escala = valorLegible(res.diabetes.escala);
  fila.diabetes_prob = porcentaje(res.diabetes.prob);
  fila.hta_nivel = res.hipertension.nivel;
  fila.hta_escala = valorLegible(res.hipertension.escala);
  fila.hta_prob = porcentaje(res.hipertension.prob);
  return fila;
}

function celda(v) {
  const s = String(v ?? "");
  return /[",\r\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
}

/** Con BOM y saltos \r\n, igual que el archivo que genera Python (abre bien en Excel). */
export function aCSV(filas) {
  const lineas = [CAMPOS.join(",")];
  for (const fila of filas) {
    lineas.push(CAMPOS.map((c) => celda(fila[c])).join(","));
  }
  return "﻿" + lineas.join("\r\n") + "\r\n";
}

// --------------------------------------------------------------------
// IndexedDB
// --------------------------------------------------------------------
const BD = "tamizaje";
const ALMACEN = "registro";

function abrir() {
  return new Promise((resolve, reject) => {
    const req = indexedDB.open(BD, 1);
    req.onupgradeneeded = () => req.result.createObjectStore(ALMACEN, { autoIncrement: true });
    req.onsuccess = () => resolve(req.result);
    req.onerror = () => reject(req.error);
  });
}

async function transaccion(modo, operacion) {
  const bd = await abrir();
  try {
    return await new Promise((resolve, reject) => {
      const tx = bd.transaction(ALMACEN, modo);
      const req = operacion(tx.objectStore(ALMACEN));
      tx.oncomplete = () => resolve(req.result);
      tx.onerror = () => reject(tx.error);
      tx.onabort = () => reject(tx.error);
    });
  } finally {
    bd.close();
  }
}

export const guardarFila = (fila) => transaccion("readwrite", (a) => a.add(fila));
export const leerFilas = () => transaccion("readonly", (a) => a.getAll());
export const contarFilas = () => transaccion("readonly", (a) => a.count());
export const borrarFilas = () => transaccion("readwrite", (a) => a.clear());
