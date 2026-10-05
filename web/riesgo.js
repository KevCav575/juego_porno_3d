// Lógica del tamizaje. Es un port 1 a 1 de nmist.py: si cambia una regla allá,
// cámbiela aquí también y corra pruebas/paridad.mjs.

// Escala 1-10 por nivel. Una medición (glucosa / presión) puede subir el nivel.
export const BANDAS_ESCALA = { BAJO: [1, 3], MEDIO: [4, 6], ALTO: [7, 10] };
export const ESCALA_MINIMA_POR_MEDICION = { MEDIO: 5, ALTO: 9 };
export const ORDEN_NIVEL = { BAJO: 0, MEDIO: 1, ALTO: 2 };

export const SINTOMAS_ALARMA = [
  "Dolor o presión en el pecho",
  "Falta de aire",
  "Debilidad, adormecimiento o cara 'chueca' de un lado",
  "Dificultad repentina para hablar o entender",
  "Visión borrosa o pérdida de la vista repentina",
  "Dolor de cabeza muy fuerte y repentino",
  "Confusión, desmayo o mucho sueño fuera de lo normal",
];

export const MENSAJES = {
  BAJO: "Su riesgo es bajo. Siga cuidándose y revísese de nuevo en un año.",
  MEDIO: "Le conviene hacerse una prueba de confirmación en su centro de salud en las próximas semanas.",
  ALTO: "Le recomendamos acudir a su centro de salud en los próximos días para confirmar. " +
    "(Entregue hoja de referencia.)",
  CONTROL: "Ya tiene diagnóstico: continúe su control en su centro de salud.",
  "ATENCIÓN INMEDIATA": "ATENCIÓN HOY: acompañe/traslade a la persona a un servicio de salud o urgencias.",
};

// ====================================================================
// 1. Cuestionario: puntos (idénticos al cuestionario en papel)
// ====================================================================
export function puntosEdad(edad) {
  if (edad < 30) return 0;
  if (edad < 40) return 2;
  if (edad < 50) return 4;
  if (edad < 60) return 6;
  return 8;
}

export function puntosSexo(mujer) {
  return mujer ? 2 : 0;
}

export function puntosActividad(minutosSemana) {
  return minutosSemana < 150 ? 1 : 0;
}

export function puntosCinturaTalla(ratio) {
  if (ratio < 0.5) return 0;
  if (ratio < 0.7) return 2;
  return 3;
}

export function nivelPorPuntosDiabetes(puntos) {
  if (puntos <= 6) return "BAJO";
  if (puntos <= 10) return "MEDIO";
  return "ALTO";
}

// ====================================================================
// 2. Probabilidades (coeficientes exportados por exportar_modelo.py)
// ====================================================================
function logistica(z) {
  return 1 / (1 + Math.exp(-z));
}

export function probDiabetes(modelo, puntos) {
  return logistica(modelo.dm.intercepto + modelo.dm.coef_puntos * puntos);
}

export function probHipertension(modelo, x) {
  const c = modelo.hta.coef;
  return logistica(
    modelo.hta.intercepto +
      c.edad_decadas * x.edad_decadas +
      c.mujer * x.mujer +
      c.cintura_talla * x.cintura_talla +
      c.actividad_baja * x.actividad_baja
  );
}

// ====================================================================
// 3. Reglas de medición (la medición sube el nivel, nunca lo baja)
// ====================================================================
/** Devuelve 'URGENTE', 'ALTO', 'MEDIO' o null. */
export function nivelPorGlucosa(glucosa, enAyuno) {
  if (glucosa == null) return null;
  if (glucosa < 54 || glucosa >= 300) return "URGENTE";
  if (enAyuno) {
    if (glucosa >= 126) return "ALTO";
    if (glucosa >= 100) return "MEDIO";
  } else {
    if (glucosa >= 200) return "ALTO";
    if (glucosa >= 140) return "MEDIO";
  }
  return null;
}

/** Devuelve 'URGENTE', 'ALTO', 'MEDIO' o null. */
export function nivelPorPresion(sistolica, diastolica) {
  const s = sistolica || 0;
  const d = diastolica || 0;
  if (s >= 180 || d >= 110) return "URGENTE";
  if (s >= 140 || d >= 90) return "ALTO";
  if (s >= 130 || d >= 80) return "MEDIO";
  return null;
}

function acotar(valor, minimo, maximo) {
  return Math.min(Math.max(valor, minimo), maximo);
}

/** Reparte la probabilidad dentro de la banda del nivel (BAJO 1-3, MEDIO 4-6, ALTO 7-10). */
export function escala1a10(probabilidad, nivel, limites) {
  const [eMin, eMax] = BANDAS_ESCALA[nivel];
  const [lo, hi] = limites[nivel];
  const frac = hi <= lo ? 0 : (probabilidad - lo) / (hi - lo);
  return acotar(eMin + Math.floor(frac * (eMax - eMin + 1)), eMin, eMax);
}

export function combinar(prob, nivelModelo, nivelMedicion, limites) {
  if (nivelMedicion === "URGENTE") {
    return { urgente: true, nivel: "ATENCIÓN INMEDIATA", escala: null, prob };
  }
  let nivel = nivelModelo;
  if (nivelMedicion && ORDEN_NIVEL[nivelMedicion] > ORDEN_NIVEL[nivel]) {
    nivel = nivelMedicion;
  }
  let escala = nivel === nivelModelo ? escala1a10(prob, nivel, limites) : BANDAS_ESCALA[nivel][0];
  if (nivelMedicion && ORDEN_NIVEL[nivelMedicion] >= ORDEN_NIVEL[nivel]) {
    escala = Math.max(escala, ESCALA_MINIMA_POR_MEDICION[nivelMedicion] ?? 1);
  }
  escala = acotar(escala, ...BANDAS_ESCALA[nivel]);
  return { urgente: false, nivel, escala, prob };
}

function rutaControl(nivelMedicion) {
  const urgente = nivelMedicion === "URGENTE";
  return { urgente, control: true, prob: null, escala: null, nivel: urgente ? "ATENCIÓN INMEDIATA" : "CONTROL" };
}

// ====================================================================
// 4. Evaluación de una persona
// ====================================================================
/** r: objeto con las respuestas del cuestionario (mismas claves que en nmist.py). */
export function evaluarPersona(modelo, r) {
  const ratio = r.cintura_cm / r.talla_cm;
  const pts = {
    edad: puntosEdad(r.edad),
    sexo: puntosSexo(r.mujer),
    actividad: puntosActividad(r.actividad_min),
    cintura_talla: puntosCinturaTalla(ratio),
  };
  const total = pts.edad + pts.sexo + pts.actividad + pts.cintura_talla;
  const res = { cintura_talla: ratio, puntos: pts, puntos_total: total };
  if (r.peso_kg) {
    res.imc = r.peso_kg / (r.talla_cm / 100) ** 2;
  }

  const alarma = Boolean(r.sintomas_alarma);

  // --- Diabetes ---
  let nivelGlu = nivelPorGlucosa(r.glucosa, r.en_ayuno ?? false);
  if (alarma && (r.glucosa || 0) >= 250) {
    nivelGlu = "URGENTE";
  }
  res.diabetes = r.dx_diabetes
    ? rutaControl(nivelGlu)
    : combinar(probDiabetes(modelo, total), nivelPorPuntosDiabetes(total), nivelGlu, modelo.limites_dm);

  // --- Hipertensión ---
  let nivelPa = nivelPorPresion(r.tas, r.tad);
  if (alarma) {
    nivelPa = "URGENTE";
  }
  const probHta = probHipertension(modelo, {
    edad_decadas: r.edad / 10,
    mujer: r.mujer ? 1 : 0,
    cintura_talla: ratio,
    actividad_baja: r.actividad_min < 150 ? 1 : 0,
  });
  const [cMedio, cAlto] = modelo.cortes_hta;
  const nivelHta = probHta >= cAlto ? "ALTO" : probHta >= cMedio ? "MEDIO" : "BAJO";
  res.hipertension = r.dx_hipertension
    ? rutaControl(nivelPa)
    : combinar(probHta, nivelHta, nivelPa, modelo.limites_hta);
  return res;
}
