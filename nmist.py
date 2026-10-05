import csv
import os
from datetime import datetime

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import RepeatedStratifiedKFold, cross_val_predict, cross_val_score

CARPETA = os.path.dirname(os.path.abspath(__file__))
DATASET = os.path.join(CARPETA, "Hipertension_Arterial_Mexico_limpio.csv")
REGISTRO = os.path.join(CARPETA, "registro_campo.csv")

# Escala 1-10 por nivel. Una medición (glucosa / presión) puede subir el nivel.
BANDAS_ESCALA = {"BAJO": (1, 3), "MEDIO": (4, 6), "ALTO": (7, 10)}
ESCALA_MINIMA_POR_MEDICION = {"MEDIO": 5, "ALTO": 9}
ORDEN_NIVEL = {"BAJO": 0, "MEDIO": 1, "ALTO": 2}

# Hipertensión: mismos cortes relativos a la prevalencia que el cuestionario de
# diabetes (MEDIO desde ~0.65x la prevalencia, ALTO desde ~1.55x).
HTA_CORTE_MEDIO = 0.65
HTA_CORTE_ALTO = 1.55

SINTOMAS_ALARMA = [
    "Dolor o presión en el pecho",
    "Falta de aire",
    "Debilidad, adormecimiento o cara 'chueca' de un lado",
    "Dificultad repentina para hablar o entender",
    "Visión borrosa o pérdida de la vista repentina",
    "Dolor de cabeza muy fuerte y repentino",
    "Confusión, desmayo o mucho sueño fuera de lo normal",
]


# ====================================================================
# 1. Cuestionario: puntos (idénticos al cuestionario en papel)
# ====================================================================
def puntos_edad(edad):
    if edad < 30:
        return 0
    if edad < 40:
        return 2
    if edad < 50:
        return 4
    if edad < 60:
        return 6
    return 8


def puntos_sexo(mujer):
    return 2 if mujer else 0


def puntos_actividad(minutos_semana):
    return 1 if minutos_semana < 150 else 0


def puntos_cintura_talla(ratio):
    if ratio < 0.50:
        return 0
    if ratio < 0.70:
        return 2
    return 3


def nivel_por_puntos_diabetes(puntos):
    if puntos <= 6:
        return "BAJO"
    if puntos <= 10:
        return "MEDIO"
    return "ALTO"


# ====================================================================
# 2. Carga del dataset limpio y entrenamiento
# ====================================================================
def cargar_datos():
    df = pd.read_csv(DATASET, encoding="utf-8-sig")
    df["mujer"] = (df["sexo"] == 2).astype(int)
    df["actividad_baja"] = (df["actividad_min_semana"] < 150).astype(int)
    df["edad_decadas"] = df["edad"] / 10
    return df


def preparar_diabetes(df):
    """Adultos >= 20 años con HbA1c real (apto_modelo_diabetes) y datos completos."""
    cols = ["edad", "sexo", "actividad_min_semana", "cintura_talla", "diabetes_hba1c"]
    d = df[df["apto_modelo_diabetes"] == True].dropna(subset=cols).copy()  # noqa: E712
    d["puntos"] = (
        d["edad"].apply(puntos_edad)
        + d["mujer"].apply(puntos_sexo)
        + d["actividad_min_semana"].apply(puntos_actividad)
        + d["cintura_talla"].apply(puntos_cintura_talla)
    )
    return d[["puntos"]], d["diabetes_hba1c"].astype(int)


FEATURES_HTA = ["edad_decadas", "mujer", "cintura_talla", "actividad_baja"]


def preparar_hipertension(df):
    """Adultos >= 20 años; hipertensión = presión sistólica medida >= 140 mmHg."""
    cols = ["edad", "sexo", "actividad_min_semana", "cintura_talla", "tas_mmhg"]
    d = df[df["edad"] >= 20].dropna(subset=cols).copy()
    return d[FEATURES_HTA], (d["tas_mmhg"] >= 140).astype(int)


def evaluar(model, X, y):
    cv = RepeatedStratifiedKFold(n_splits=5, n_repeats=20, random_state=42)
    auc = cross_val_score(model, X, y, cv=cv, scoring="roc_auc")
    return auc.mean(), auc.std()


def entrenar():
    df = cargar_datos()

    # --- Diabetes: logística sobre el puntaje total del cuestionario ---
    X_dm, y_dm = preparar_diabetes(df)
    modelo_dm = LogisticRegression()
    auc_dm = evaluar(modelo_dm, X_dm, y_dm)
    modelo_dm.fit(X_dm, y_dm)

    # --- Hipertensión: logística con las mismas preguntas del cuestionario ---
    X_hta, y_hta = preparar_hipertension(df)
    modelo_hta = LogisticRegression()
    auc_hta = evaluar(modelo_hta, X_hta, y_hta)
    modelo_hta.fit(X_hta, y_hta)

    prev_hta = y_hta.mean()
    cortes_hta = (HTA_CORTE_MEDIO * prev_hta, HTA_CORTE_ALTO * prev_hta)

    # Límites de probabilidad de cada nivel (para repartir la escala 1-10)
    p_dm = lambda pts: modelo_dm.predict_proba(pd.DataFrame({"puntos": [pts]}))[0, 1]
    limites_dm = {
        "BAJO": (0.0, p_dm(7)),
        "MEDIO": (p_dm(7), p_dm(11)),
        "ALTO": (p_dm(11), p_dm(14)),
    }
    p_max_hta = modelo_hta.predict_proba(X_hta)[:, 1].max()
    limites_hta = {
        "BAJO": (0.0, cortes_hta[0]),
        "MEDIO": cortes_hta,
        "ALTO": (cortes_hta[1], p_max_hta),
    }

    # --- Reporte ---
    print("=" * 68)
    print("MODELOS ENTRENADOS CON EL DATASET LIMPIO")
    print("=" * 68)
    print(f"Diabetes (HbA1c >= 6.5 %): n = {len(y_dm):,}, casos = {y_dm.sum()} ({y_dm.mean():.1%})")
    print(f"  AUC-ROC validación cruzada (5x20): {auc_dm[0]:.3f} ± {auc_dm[1]:.3f}")
    print("  Probabilidad por puntaje del cuestionario:")
    for pts in range(15):
        print(f"    {pts:>2} pts -> {p_dm(pts):5.1%}  {nivel_por_puntos_diabetes(pts)}")

    print(f"\nHipertensión (sistólica >= 140): n = {len(y_hta):,}, casos = {y_hta.sum()} ({prev_hta:.1%})")
    print(f"  AUC-ROC validación cruzada (5x20): {auc_hta[0]:.3f} ± {auc_hta[1]:.3f}")
    print(f"  Cortes: MEDIO desde {cortes_hta[0]:.1%}, ALTO desde {cortes_hta[1]:.1%}")
    p_cv = cross_val_predict(LogisticRegression(), X_hta, y_hta, cv=5, method="predict_proba")[:, 1]
    niveles_cv = np.where(p_cv >= cortes_hta[1], "ALTO", np.where(p_cv >= cortes_hta[0], "MEDIO", "BAJO"))
    for nivel in ("BAJO", "MEDIO", "ALTO"):
        m = niveles_cv == nivel
        if m.any():
            print(f"    {nivel:<5}: {m.mean():5.1%} de las personas; con hipertensión {y_hta[m].mean():5.1%}")
    print("=" * 68)

    return {
        "dm": modelo_dm,
        "hta": modelo_hta,
        "cortes_hta": cortes_hta,
        "limites_dm": limites_dm,
        "limites_hta": limites_hta,
    }


# ====================================================================
# 3. Reglas de medición (la medición sube el nivel, nunca lo baja)
# ====================================================================
def nivel_por_glucosa(glucosa, en_ayuno):
    """Devuelve 'URGENTE', 'ALTO', 'MEDIO' o None."""
    if glucosa is None:
        return None
    if glucosa < 54 or glucosa >= 300:
        return "URGENTE"
    if en_ayuno:
        if glucosa >= 126:
            return "ALTO"
        if glucosa >= 100:
            return "MEDIO"
    else:
        if glucosa >= 200:
            return "ALTO"
        if glucosa >= 140:
            return "MEDIO"
    return None


def nivel_por_presion(sistolica, diastolica):
    """Devuelve 'URGENTE', 'ALTO', 'MEDIO' o None."""
    s = sistolica or 0
    d = diastolica or 0
    if s >= 180 or d >= 110:
        return "URGENTE"
    if s >= 140 or d >= 90:
        return "ALTO"
    if s >= 130 or d >= 80:
        return "MEDIO"
    return None


def escala_1_10(probabilidad, nivel, limites):
    """Reparte la probabilidad dentro de la banda del nivel (BAJO 1-3, MEDIO 4-6, ALTO 7-10)."""
    e_min, e_max = BANDAS_ESCALA[nivel]
    lo, hi = limites[nivel]
    frac = 0.0 if hi <= lo else (probabilidad - lo) / (hi - lo)
    escala = e_min + int(np.floor(frac * (e_max - e_min + 1)))
    return int(np.clip(escala, e_min, e_max))


def combinar(prob, nivel_modelo, nivel_medicion, limites):
    if nivel_medicion == "URGENTE":
        return {"urgente": True, "nivel": "ATENCIÓN INMEDIATA", "escala": None, "prob": prob}
    nivel = nivel_modelo
    if nivel_medicion and ORDEN_NIVEL[nivel_medicion] > ORDEN_NIVEL[nivel]:
        nivel = nivel_medicion
    escala = escala_1_10(prob, nivel, limites) if nivel == nivel_modelo else BANDAS_ESCALA[nivel][0]
    if nivel_medicion and ORDEN_NIVEL[nivel_medicion] >= ORDEN_NIVEL[nivel]:
        escala = max(escala, ESCALA_MINIMA_POR_MEDICION.get(nivel_medicion, 1))
    escala = int(np.clip(escala, *BANDAS_ESCALA[nivel]))
    return {"urgente": False, "nivel": nivel, "escala": escala, "prob": prob}


# ====================================================================
# 4. Evaluación de una persona
# ====================================================================
def evaluar_persona(modelos, r):
    """r: diccionario con las respuestas del cuestionario."""
    ratio = r["cintura_cm"] / r["talla_cm"]
    pts = {
        "edad": puntos_edad(r["edad"]),
        "sexo": puntos_sexo(r["mujer"]),
        "actividad": puntos_actividad(r["actividad_min"]),
        "cintura_talla": puntos_cintura_talla(ratio),
    }
    total = sum(pts.values())
    res = {"cintura_talla": ratio, "puntos": pts, "puntos_total": total}
    if r.get("peso_kg"):
        res["imc"] = r["peso_kg"] / (r["talla_cm"] / 100) ** 2

    alarma = bool(r.get("sintomas_alarma"))

    # --- Diabetes ---
    nivel_glu = nivel_por_glucosa(r.get("glucosa"), r.get("en_ayuno", False))
    if alarma and (r.get("glucosa") or 0) >= 250:
        nivel_glu = "URGENTE"
    prob_dm = modelos["dm"].predict_proba(pd.DataFrame({"puntos": [total]}))[0, 1]
    if r.get("dx_diabetes"):
        dm = {"urgente": nivel_glu == "URGENTE", "control": True, "prob": None, "escala": None,
              "nivel": "ATENCIÓN INMEDIATA" if nivel_glu == "URGENTE" else "CONTROL"}
    else:
        dm = combinar(prob_dm, nivel_por_puntos_diabetes(total), nivel_glu, modelos["limites_dm"])
    res["diabetes"] = dm

    # --- Hipertensión ---
    nivel_pa = nivel_por_presion(r.get("tas"), r.get("tad"))
    if alarma:
        nivel_pa = "URGENTE"
    X = pd.DataFrame([{
        "edad_decadas": r["edad"] / 10,
        "mujer": int(r["mujer"]),
        "cintura_talla": ratio,
        "actividad_baja": int(r["actividad_min"] < 150),
    }])[FEATURES_HTA]
    prob_hta = modelos["hta"].predict_proba(X)[0, 1]
    c_medio, c_alto = modelos["cortes_hta"]
    nivel_hta = "ALTO" if prob_hta >= c_alto else "MEDIO" if prob_hta >= c_medio else "BAJO"
    if r.get("dx_hipertension"):
        hta = {"urgente": nivel_pa == "URGENTE", "control": True, "prob": None, "escala": None,
               "nivel": "ATENCIÓN INMEDIATA" if nivel_pa == "URGENTE" else "CONTROL"}
    else:
        hta = combinar(prob_hta, nivel_hta, nivel_pa, modelos["limites_hta"])
    res["hipertension"] = hta
    return res


MENSAJES = {
    "BAJO": "Su riesgo es bajo. Siga cuidándose y revísese de nuevo en un año.",
    "MEDIO": "Le conviene hacerse una prueba de confirmación en su centro de salud en las próximas semanas.",
    "ALTO": "Le recomendamos acudir a su centro de salud en los próximos días para confirmar. "
            "(Entregue hoja de referencia.)",
    "CONTROL": "Ya tiene diagnóstico: continúe su control en su centro de salud.",
    "ATENCIÓN INMEDIATA": "ATENCIÓN HOY: acompañe/traslade a la persona a un servicio de salud o urgencias.",
}


def imprimir_resultado(res):
    print("\n" + "=" * 68)
    print("RESULTADO DEL TAMIZAJE")
    print("=" * 68)
    p = res["puntos"]
    print(f"Puntos cuestionario diabetes: edad {p['edad']} + sexo {p['sexo']} + actividad {p['actividad']}"
          f" + cintura/estatura {p['cintura_talla']} = {res['puntos_total']} / 14")
    print(f"Cintura/estatura: {res['cintura_talla']:.2f}" + (f"   IMC: {res['imc']:.1f}" if "imc" in res else ""))

    for nombre, clave in (("DIABETES", "diabetes"), ("HIPERTENSIÓN", "hipertension")):
        r = res[clave]
        print(f"\n--- {nombre} ---")
        if r["urgente"]:
            print(">>> ATENCIÓN INMEDIATA <<<")
        elif r.get("control"):
            print("Ruta de CONTROL (diagnóstico previo)")
        else:
            print(f"Riesgo: {r['escala']} / 10   (nivel {r['nivel']})")
            print(f"Probabilidad estimada por el modelo (solo para promotor/médico): {r['prob']:.1%}")
        print(f"Mensaje: {MENSAJES[r['nivel']]}")
    print("\nRecuerde: la glucosa se mide a TODAS las personas. Este resultado NO es un diagnóstico.")
    print("=" * 68)


# ====================================================================
# 5. Cuestionario interactivo por consola
# ====================================================================
def pedir_numero(texto, minimo, maximo, opcional=False):
    while True:
        valor = input(texto).strip().replace(",", ".")
        if valor == "" and opcional:
            return None
        try:
            n = float(valor)
            if minimo <= n <= maximo:
                return n
        except ValueError:
            pass
        print(f"  Valor no válido. Escriba un número entre {minimo} y {maximo}"
              + (" (o Enter para omitir)." if opcional else "."))


def pedir_opcion(texto, opciones):
    """opciones: dict tecla -> valor."""
    teclas = "/".join(opciones)
    while True:
        valor = input(f"{texto} [{teclas}]: ").strip().lower()
        if valor in opciones:
            return opciones[valor]
        print(f"  Responda con una de: {teclas}")


SI_NO = {"s": True, "n": False}
SI_NO_NS = {"s": "si", "n": "no", "ns": "no_se"}


def cuestionario_interactivo():
    print("\n" + "=" * 68)
    print("CUESTIONARIO DE RIESGO DE DIABETES E HIPERTENSIÓN")
    print("=" * 68)
    r = {}

    # --- Antes de empezar ---
    if not pedir_opcion("A. ¿La persona tiene 20 años o más?", SI_NO):
        print("-> No aplique este cuestionario (menor de 20 años).")
        return None
    r["mujer"] = pedir_opcion("Sexo (h = hombre, m = mujer)", {"h": False, "m": True})
    if r["mujer"] and pedir_opcion("B. ¿Está embarazada?", SI_NO):
        print("-> No aplique; refiera a control prenatal.")
        print("   Si tiene presión >= 140/90 o síntomas de alarma, refiera HOY.")
        return None
    r["dx_diabetes"] = pedir_opcion("C. ¿Algún médico le ha dicho que tiene diabetes o 'azúcar alta'?", SI_NO)
    r["dx_hipertension"] = pedir_opcion("C2. ¿Algún médico le ha dicho que tiene presión alta?", SI_NO)

    # --- Preguntas ---
    r["edad"] = pedir_numero("1. Edad en años: ", 20, 110)
    print("3. En una semana normal (trabajo, traslados a pie/bici, ejercicio), ¿cuántos minutos")
    print("   de actividad que lo haga respirar más rápido o sudar? (30 min x 5 días = 150)")
    r["actividad_min"] = pedir_numero("   Minutos por semana: ", 0, 6720)

    # --- Medición ---
    r["talla_cm"] = pedir_numero("4. Estatura (cm, sin zapatos): ", 120, 210)
    r["cintura_cm"] = pedir_numero("   Cintura (cm): ", 50, 180)
    r["peso_kg"] = pedir_numero("C6. Peso (kg, Enter para omitir): ", 30, 250, opcional=True)

    r["glucosa"] = pedir_numero("Glucosa con glucómetro (mg/dL, Enter si no se midió): ", 10, 700, opcional=True)
    if r["glucosa"] is not None:
        r["en_ayuno"] = pedir_opcion("   ¿Lleva 8 horas o más sin comer?", SI_NO)
    r["tas"] = pedir_numero("Presión SISTÓLICA (la alta, mmHg, Enter si no se midió): ", 60, 300, opcional=True)
    r["tad"] = pedir_numero("Presión DIASTÓLICA (la baja, mmHg, Enter si no se midió): ", 30, 200, opcional=True)

    print("\nSíntomas de alarma. ¿Tiene AHORA alguno de estos?")
    for s in SINTOMAS_ALARMA:
        print(f"   - {s}")
    r["sintomas_alarma"] = pedir_opcion("¿Alguno?", SI_NO)

    # --- Complementarias (se registran, no suman puntos) ---
    print("\nPreguntas complementarias (se registran, NO suman puntos):")
    r["c1_familiar_diabetes"] = pedir_opcion("C1. ¿Papá, mamá, hermanos o hijos con diabetes?", SI_NO_NS)
    if r["mujer"]:
        r["c3_diabetes_gestacional"] = pedir_opcion(
            "C3. ¿Azúcar alta en algún embarazo o bebé de más de 4 kg?", SI_NO_NS)
    r["c4_prediabetes"] = pedir_opcion("C4. ¿Le dijeron que tenía el azúcar 'un poco alta'?", SI_NO_NS)
    r["c5_fuma"] = pedir_opcion("C5. ¿Fuma? (n = nunca, a = antes sí, s = sí actualmente)",
                                {"n": "nunca", "a": "antes", "s": "actual"})
    return r


def valor_legible(v):
    """Convierte las respuestas al formato en que la persona las dio."""
    if v is None:
        return ""
    if isinstance(v, bool):
        return "si" if v else "no"
    if isinstance(v, float):
        return int(v) if v.is_integer() else v
    return v


def guardar_registro(r, res):
    datos = {k: valor_legible(v) for k, v in r.items()}
    datos["sexo"] = "mujer" if r["mujer"] else "hombre"
    prob = lambda p: "" if p is None else f"{p:.1%}"
    fila = {"fecha": datetime.now().isoformat(timespec="seconds"), **datos,
            "puntos_total": res["puntos_total"],
            "diabetes_nivel": res["diabetes"]["nivel"], "diabetes_escala": valor_legible(res["diabetes"]["escala"]),
            "diabetes_prob": prob(res["diabetes"]["prob"]),
            "hta_nivel": res["hipertension"]["nivel"], "hta_escala": valor_legible(res["hipertension"]["escala"]),
            "hta_prob": prob(res["hipertension"]["prob"])}
    campos = ["fecha", "sexo", "dx_diabetes", "dx_hipertension", "edad", "actividad_min", "talla_cm",
              "cintura_cm", "peso_kg", "glucosa", "en_ayuno", "tas", "tad", "sintomas_alarma",
              "c1_familiar_diabetes", "c3_diabetes_gestacional", "c4_prediabetes", "c5_fuma",
              "puntos_total", "diabetes_nivel", "diabetes_escala", "diabetes_prob",
              "hta_nivel", "hta_escala", "hta_prob"]
    nuevo = not os.path.exists(REGISTRO)
    with open(REGISTRO, "a", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=campos, extrasaction="ignore")
        if nuevo:
            w.writeheader()
        w.writerow(fila)


if __name__ == "__main__":
    try:
        import sys
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    modelos = entrenar()
    while True:
        respuestas = cuestionario_interactivo()
        if respuestas is not None:
            resultado = evaluar_persona(modelos, respuestas)
            imprimir_resultado(resultado)
            guardar_registro(respuestas, resultado)
            print(f"(Guardado en {os.path.basename(REGISTRO)})")
        if not pedir_opcion("\n¿Evaluar a otra persona?", SI_NO):
            break
