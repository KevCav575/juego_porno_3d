"""Genera pruebas/casos.json: respuestas al azar con el resultado que da nmist.py.

pruebas/paridad.mjs corre los mismos casos contra web/riesgo.js para comprobar
que la página da exactamente lo mismo que Python.
"""
import json
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nmist import entrenar, evaluar_persona  # noqa: E402

SALIDA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "casos.json")
N_ALEATORIOS = 2000

# Las 3 filas de registro_campo.csv (capturadas con la app de consola).
FIJOS = [
    {"mujer": False, "dx_diabetes": False, "dx_hipertension": False, "edad": 20.0, "actividad_min": 30.0,
     "talla_cm": 170.0, "cintura_cm": 100.0, "peso_kg": 120.0, "glucosa": None, "tas": None, "tad": None,
     "sintomas_alarma": True},
    {"mujer": False, "dx_diabetes": False, "dx_hipertension": False, "edad": 20.0, "actividad_min": 240.0,
     "talla_cm": 181.0, "cintura_cm": 80.0, "peso_kg": 73.0, "glucosa": None, "tas": None, "tad": None,
     "sintomas_alarma": False},
    {"mujer": False, "dx_diabetes": False, "dx_hipertension": False, "edad": 20.0, "actividad_min": 150.0,
     "talla_cm": 170.0, "cintura_cm": 65.0, "peso_kg": 70.0, "glucosa": None, "tas": None, "tad": None,
     "sintomas_alarma": False},
]

# Valores justo en los cortes de las reglas, para que salgan seguido.
GLUCOSAS = [None, 53, 54, 99, 100, 125, 126, 139, 140, 199, 200, 249, 250, 299, 300]
SISTOLICAS = [None, 110, 129, 130, 139, 140, 179, 180]
DIASTOLICAS = [None, 70, 79, 80, 89, 90, 109, 110]


def caso_aleatorio(rng):
    talla = float(rng.randint(120, 210))
    r = {
        "mujer": rng.random() < 0.5,
        "dx_diabetes": rng.random() < 0.15,
        "dx_hipertension": rng.random() < 0.15,
        "edad": float(rng.randint(20, 110)),
        "actividad_min": float(rng.choice([0, 60, 149, 150, 151, 300, rng.randint(0, 6720)])),
        "talla_cm": talla,
        # La mitad de las veces la cintura cae exacto en un corte (0.50 / 0.70 de la estatura).
        "cintura_cm": min(180.0, max(50.0, talla * rng.choice([0.5, 0.7, rng.uniform(0.3, 0.9)]))),
        "peso_kg": rng.choice([None, float(rng.randint(30, 250))]),
        "glucosa": rng.choice(GLUCOSAS + [float(rng.randint(10, 700))]),
        "tas": rng.choice(SISTOLICAS + [float(rng.randint(60, 300))]),
        "tad": rng.choice(DIASTOLICAS + [float(rng.randint(30, 200))]),
        "sintomas_alarma": rng.random() < 0.15,
    }
    if r["glucosa"] is not None:
        r["en_ayuno"] = rng.random() < 0.5
    return r


def a_json(res):
    """Convierte los tipos de numpy a tipos nativos."""
    for clave in ("diabetes", "hipertension"):
        d = res[clave]
        d["prob"] = None if d["prob"] is None else float(d["prob"])
        d["escala"] = None if d["escala"] is None else int(d["escala"])
        d["urgente"] = bool(d["urgente"])
    return res


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    modelos = entrenar()
    rng = random.Random(42)
    respuestas = FIJOS + [caso_aleatorio(rng) for _ in range(N_ALEATORIOS)]
    casos = [{"r": r, "esperado": a_json(evaluar_persona(modelos, r))} for r in respuestas]
    with open(SALIDA, "w", encoding="utf-8") as f:
        json.dump(casos, f, ensure_ascii=False)
    print(f"{len(casos)} casos escritos en pruebas/casos.json")
