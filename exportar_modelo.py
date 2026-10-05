"""Entrena los modelos de nmist.py y exporta sus números a web/modelo.json.

La página web no usa Python: calcula la probabilidad con estos coeficientes.
Vuelva a correr este script cada vez que cambie el dataset o el modelo.
"""
import json
import os

from nmist import CARPETA, FEATURES_HTA, entrenar

SALIDA = os.path.join(CARPETA, "web", "modelo.json")


def exportar(modelos):
    dm, hta = modelos["dm"], modelos["hta"]
    return {
        "dm": {"intercepto": float(dm.intercept_[0]), "coef_puntos": float(dm.coef_[0][0])},
        "hta": {
            "intercepto": float(hta.intercept_[0]),
            "coef": {f: float(c) for f, c in zip(FEATURES_HTA, hta.coef_[0])},
        },
        "cortes_hta": [float(c) for c in modelos["cortes_hta"]],
        "limites_dm": {k: [float(a), float(b)] for k, (a, b) in modelos["limites_dm"].items()},
        "limites_hta": {k: [float(a), float(b)] for k, (a, b) in modelos["limites_hta"].items()},
    }


if __name__ == "__main__":
    try:
        import sys
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    datos = exportar(entrenar())
    os.makedirs(os.path.dirname(SALIDA), exist_ok=True)
    with open(SALIDA, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)
    print(f"Modelo exportado a {os.path.relpath(SALIDA, CARPETA)}")
