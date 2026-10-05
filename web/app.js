import { MENSAJES, SINTOMAS_ALARMA, evaluarPersona } from "./riesgo.js";
import { aCSV, borrarFilas, construirFila, contarFilas, guardarFila, leerFilas } from "./registro.js";

// Mismos rangos que pedir_numero() en nmist.py: [campo, mínimo, máximo, opcional]
const NUMEROS = [
  ["edad", 20, 110, false],
  ["actividad_min", 0, 6720, false],
  ["talla_cm", 120, 210, false],
  ["cintura_cm", 50, 180, false],
  ["peso_kg", 30, 250, true],
  ["glucosa", 10, 700, true],
  ["tas", 60, 300, true],
  ["tad", 30, 200, true],
];
const SI_NO = { s: true, n: false };

const $ = (id) => document.getElementById(id);
const form = $("cuestionario");
let modelo = null;

function elegido(nombre) {
  return form.elements[nombre].value || null;
}

function campo(nombre) {
  return form.querySelector(`[data-campo="${nombre}"]`);
}

function crear(etiqueta, texto, clase) {
  const el = document.createElement(etiqueta);
  if (texto != null) el.textContent = texto;
  if (clase) el.className = clase;
  return el;
}

// --------------------------------------------------------------------
// Preguntas que dependen de otras
// --------------------------------------------------------------------
function actualizarVisibilidad() {
  const mujer = elegido("sexo") === "m";
  for (const el of form.querySelectorAll("[data-solo-mujer]")) {
    el.hidden = !mujer;
  }
  campo("en_ayuno").hidden = form.elements.glucosa.value.trim() === "";

  let motivo = null;
  if (elegido("mayor20") === "n") {
    motivo = "No aplique este cuestionario (menor de 20 años).";
  } else if (mujer && elegido("embarazada") === "s") {
    motivo = "No aplique; refiera a control prenatal. " +
      "Si tiene presión de 140/90 o más, o síntomas de alarma, refiera HOY.";
  }
  $("no-aplica").textContent = motivo ?? "";
  $("no-aplica").hidden = !motivo;
  $("resto").hidden = Boolean(motivo);
}

// --------------------------------------------------------------------
// Lectura y validación
// --------------------------------------------------------------------
function marcarError(nombre, mensaje) {
  const el = campo(nombre);
  el.classList.add("invalido");
  el.append(crear("p", mensaje, "error"));
}

function limpiarErrores() {
  for (const el of form.querySelectorAll(".error")) el.remove();
  for (const el of form.querySelectorAll(".invalido")) el.classList.remove("invalido");
}

function leerNumero(nombre, minimo, maximo, opcional) {
  const texto = form.elements[nombre].value.trim().replace(",", ".");
  if (texto === "" && opcional) return null;
  const n = /^\d+(\.\d+)?$/.test(texto) ? Number(texto) : NaN;
  if (!(n >= minimo && n <= maximo)) {
    marcarError(nombre, `Escriba un número entre ${minimo} y ${maximo}` + (opcional ? ", o déjelo vacío." : "."));
    return undefined;
  }
  return n;
}

function leerOpcion(nombre, opciones) {
  const valor = elegido(nombre);
  if (valor == null) {
    marcarError(nombre, "Elija una opción.");
    return undefined;
  }
  return opciones ? opciones[valor] : valor;
}

/** Devuelve las respuestas con las mismas claves que nmist.py, o null si falta algo. */
function leerRespuestas() {
  limpiarErrores();
  const num = Object.fromEntries(NUMEROS.map(([n, ...rango]) => [n, leerNumero(n, ...rango)]));
  const r = {};
  leerOpcion("mayor20");
  r.mujer = leerOpcion("sexo", { h: false, m: true });
  if (r.mujer) leerOpcion("embarazada");
  r.dx_diabetes = leerOpcion("dx_diabetes", SI_NO);
  r.dx_hipertension = leerOpcion("dx_hipertension", SI_NO);
  r.edad = num.edad;
  r.actividad_min = num.actividad_min;
  r.talla_cm = num.talla_cm;
  r.cintura_cm = num.cintura_cm;
  r.peso_kg = num.peso_kg;
  r.glucosa = num.glucosa;
  if (r.glucosa != null) r.en_ayuno = leerOpcion("en_ayuno", SI_NO);
  r.tas = num.tas;
  r.tad = num.tad;
  r.sintomas_alarma = leerOpcion("sintomas_alarma", SI_NO);
  r.c1_familiar_diabetes = leerOpcion("c1_familiar_diabetes");
  if (r.mujer) r.c3_diabetes_gestacional = leerOpcion("c3_diabetes_gestacional");
  r.c4_prediabetes = leerOpcion("c4_prediabetes");
  r.c5_fuma = leerOpcion("c5_fuma");

  const primerError = form.querySelector(".invalido");
  if (primerError) {
    primerError.scrollIntoView({ behavior: "smooth", block: "center" });
    return null;
  }
  return r;
}

// --------------------------------------------------------------------
// Resultado
// --------------------------------------------------------------------
function tarjetaEnfermedad(nombre, r) {
  const clase = r.urgente ? "URGENTE" : r.nivel;
  const tarjeta = crear("div", null, `tarjeta resultado ${clase}`);
  tarjeta.append(crear("h3", nombre));
  if (r.urgente) {
    tarjeta.append(crear("p", "ATENCIÓN INMEDIATA", "titular"));
  } else if (r.control) {
    tarjeta.append(crear("p", "Ruta de CONTROL", "titular"), crear("p", "Diagnóstico previo.", "nota"));
  } else {
    tarjeta.append(
      crear("p", `Riesgo ${r.escala} / 10 · nivel ${r.nivel}`, "titular"),
      crear("p", `Probabilidad estimada por el modelo (solo para promotor/médico): ${(r.prob * 100).toFixed(1)} %`, "nota")
    );
  }
  tarjeta.append(crear("p", MENSAJES[r.nivel]));
  return tarjeta;
}

function mostrarResultado(res) {
  const p = res.puntos;
  const resumen = crear("div", null, "tarjeta");
  resumen.append(
    crear("h2", "Resultado del tamizaje"),
    crear("p", `Puntos del cuestionario de diabetes: edad ${p.edad} + sexo ${p.sexo} + actividad ${p.actividad}` +
      ` + cintura/estatura ${p.cintura_talla} = ${res.puntos_total} / 14`, "nota"),
    crear("p", `Cintura/estatura: ${res.cintura_talla.toFixed(2)}` +
      (res.imc != null ? ` · IMC: ${res.imc.toFixed(1)}` : ""), "nota")
  );
  $("resultado-contenido").replaceChildren(
    resumen,
    tarjetaEnfermedad("DIABETES", res.diabetes),
    tarjetaEnfermedad("HIPERTENSIÓN", res.hipertension),
    crear("p", "Recuerde: la glucosa se mide a TODAS las personas. Este resultado NO es un diagnóstico.", "nota")
  );
  form.hidden = true;
  $("resultado").hidden = false;
  $("resultado").scrollIntoView({ block: "start" });
}

// --------------------------------------------------------------------
// Registro
// --------------------------------------------------------------------
async function actualizarConteo() {
  try {
    const n = await contarFilas();
    $("conteo-registro").textContent =
      n === 1 ? "1 persona guardada en este dispositivo." : `${n} personas guardadas en este dispositivo.`;
  } catch {
    $("conteo-registro").textContent = "Este navegador no permite guardar el registro (¿modo privado?).";
  }
}

async function descargar() {
  const filas = await leerFilas();
  if (filas.length === 0) {
    alert("Todavía no hay registros guardados.");
    return;
  }
  const url = URL.createObjectURL(new Blob([aCSV(filas)], { type: "text/csv;charset=utf-8" }));
  const enlace = crear("a");
  enlace.href = url;
  enlace.download = `registro_campo_${filas[filas.length - 1].fecha.slice(0, 10)}.csv`;
  enlace.click();
  URL.revokeObjectURL(url);
}

async function borrar() {
  const n = await contarFilas();
  if (n === 0) return;
  if (!confirm(`Se borrarán ${n} registro(s) de este dispositivo. ¿Ya descargó el CSV?`)) return;
  await borrarFilas();
  await actualizarConteo();
}

// --------------------------------------------------------------------
// Eventos
// --------------------------------------------------------------------
form.addEventListener("input", actualizarVisibilidad);

form.addEventListener("submit", async (evento) => {
  evento.preventDefault();
  const r = leerRespuestas();
  if (!r) return;
  const res = evaluarPersona(modelo, r);
  mostrarResultado(res);
  try {
    await guardarFila(construirFila(r, res));
    $("estado-guardado").textContent = "Guardado en el registro de este dispositivo.";
  } catch {
    $("estado-guardado").textContent = "NO se pudo guardar en el registro. Anote el resultado en papel.";
  }
  actualizarConteo();
});

$("otra-persona").addEventListener("click", () => {
  form.reset();
  limpiarErrores();
  actualizarVisibilidad();
  $("resultado").hidden = true;
  form.hidden = false;
  window.scrollTo(0, 0);
});

$("descargar").addEventListener("click", descargar);
$("borrar").addEventListener("click", borrar);

$("lista-sintomas").append(...SINTOMAS_ALARMA.map((s) => crear("li", s)));
actualizarVisibilidad();
actualizarConteo();

try {
  const respuesta = await fetch("modelo.json");
  if (!respuesta.ok) throw new Error(respuesta.statusText);
  modelo = await respuesta.json();
} catch {
  $("error-carga").textContent = "No se pudo cargar el modelo (modelo.json). Recargue la página con conexión a internet.";
  $("error-carga").hidden = false;
  form.hidden = true;
}

if ("serviceWorker" in navigator) {
  navigator.serviceWorker.register("sw.js");
}
