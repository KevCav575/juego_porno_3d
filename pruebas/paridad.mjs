// Comprueba que web/riesgo.js da lo mismo que nmist.py.
// Antes: py exportar_modelo.py  y  py pruebas/generar_casos.py
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";

import { evaluarPersona } from "../web/riesgo.js";
import { aCSV, construirFila } from "../web/registro.js";

const leer = (ruta) => JSON.parse(readFileSync(new URL(ruta, import.meta.url), "utf8"));
const modelo = leer("../web/modelo.json");
const casos = leer("./casos.json");

const TOLERANCIA = 1e-6;
const cerca = (a, b) => (a == null || b == null ? a == b : Math.abs(a - b) <= TOLERANCIA);

let fallos = 0;
const conteo = {};
for (const [i, { r, esperado }] of casos.entries()) {
  const res = evaluarPersona(modelo, r);
  const errores = [];
  if (res.puntos_total !== esperado.puntos_total) errores.push("puntos_total");
  if (!cerca(res.cintura_talla, esperado.cintura_talla)) errores.push("cintura_talla");
  if (!cerca(res.imc, esperado.imc)) errores.push("imc");
  for (const clave of ["diabetes", "hipertension"]) {
    const a = res[clave];
    const b = esperado[clave];
    if (a.nivel !== b.nivel) errores.push(`${clave}.nivel`);
    if (a.escala !== b.escala) errores.push(`${clave}.escala`);
    if (a.urgente !== b.urgente) errores.push(`${clave}.urgente`);
    if (Boolean(a.control) !== Boolean(b.control)) errores.push(`${clave}.control`);
    if (!cerca(a.prob, b.prob)) errores.push(`${clave}.prob`);
    conteo[`${clave}: ${a.nivel}`] = (conteo[`${clave}: ${a.nivel}`] ?? 0) + 1;
  }
  if (errores.length > 0) {
    fallos += 1;
    if (fallos <= 5) {
      console.error(`Caso ${i} difiere en: ${errores.join(", ")}`);
      console.error("  respuestas:", JSON.stringify(r));
      console.error("  python:    ", JSON.stringify(esperado));
      console.error("  javascript:", JSON.stringify(res));
    }
  }
}

// La primera fila de registro_campo.csv, tal como la escribió la app de consola.
const fila = construirFila(
  { ...casos[0].r, c1_familiar_diabetes: "si", c4_prediabetes: "si", c5_fuma: "actual" },
  evaluarPersona(modelo, casos[0].r),
  new Date(2026, 8, 28, 18, 6, 45)
);
assert.equal(
  aCSV([fila]).split("\r\n")[1],
  "2026-09-28T18:06:45,hombre,no,no,20,30,170,100,120,,,,,si,si,,si,actual,3,BAJO,2,4.3%,ATENCIÓN INMEDIATA,,7.6%"
);

console.log(`Casos por nivel: ${JSON.stringify(conteo, null, 1)}`);
if (fallos > 0) {
  console.error(`\nFALLÓ: ${fallos} de ${casos.length} casos difieren de Python.`);
  process.exit(1);
}
console.log(`\nOK: ${casos.length} casos idénticos a Python y el CSV coincide con registro_campo.csv.`);
