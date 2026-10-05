# Tamizaje de riesgo de diabetes e hipertensión

Cuestionario para promotores de salud. Hay dos formas de usarlo:

- **Página web** (`web/`): funciona en el celular y sin internet. No necesita Python.
- **Consola** (`nmist.py`): la versión original.

Este cuestionario NO diagnostica. Debe validarse con el asesor médico antes de usarse con personas reales.

## Página web

La página calcula todo en el navegador con los coeficientes de `web/modelo.json`. Los registros
se guardan solo en el dispositivo y se descargan como CSV (mismas columnas que `registro_campo.csv`).

Probarla en la computadora:

```
py -m http.server 8000 --directory web
```

y abrir http://localhost:8000. No funciona abriendo `index.html` con doble clic.

Publicarla: subir el contenido de `web/` a cualquier hosting estático con HTTPS (GitHub Pages,
Cloudflare Pages, Netlify). Después de abrirla una vez con internet, se puede instalar en el
celular y usar sin señal.

Al publicar una versión nueva, cada celular la toma la segunda vez que abre la página con
internet (la primera vez la descarga en segundo plano).

## Reentrenar el modelo

```
python -m venv .venv
.\.venv\Scripts\activate.bat
pip install pandas numpy scikit-learn
py exportar_modelo.py
```

`exportar_modelo.py` entrena con `Hipertension_Arterial_Mexico_limpio.csv` y reescribe `web/modelo.json`.

## Pruebas

Comprueban que la página da exactamente lo mismo que `nmist.py` (requiere Node.js):

```
py pruebas/generar_casos.py
npm test
```

Si cambia una regla en `nmist.py`, haga el mismo cambio en `web/riesgo.js` y corra las pruebas.

## Consola

```
py nmist.py
```
