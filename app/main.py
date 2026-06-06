"""Servicio Flask que expone la función `predecir` por API y formulario web."""

from flask import Flask, jsonify, render_template, request

import estadisticas
from model import ESTADOS, predecir

app = Flask(__name__)


@app.get("/")
def index():
    return render_template("index.html", estados=ESTADOS, resultado=None)


@app.post("/")
def index_post():
    try:
        sintomas = {
            "fiebre": float(request.form.get("fiebre") or 0),
            "dolor": float(request.form.get("dolor") or 0),
            "fatiga": float(request.form.get("fatiga") or 0),
            "duracion_dias": float(request.form.get("duracion_dias") or 0),
            "edad": float(request.form.get("edad") or 0),
        }
        resultado = predecir(sintomas)
        estadisticas.registrar_prediccion(sintomas, resultado)
    except (ValueError, TypeError) as e:
        resultado = f"Error en los datos: {e}"

    return render_template("index.html", estados=ESTADOS, resultado=resultado)


@app.post("/predecir")
def predecir_api():
    """Endpoint JSON. Acepta dict u objeto con clave `sintomas` (lista o dict)."""
    payload = request.get_json(silent=True) or {}
    entrada = payload.get("sintomas", payload)

    try:
        resultado = predecir(entrada)
    except (ValueError, TypeError) as e:
        return jsonify({"error": str(e)}), 400

    estadisticas.registrar_prediccion(entrada, resultado)
    return jsonify({"prediccion": resultado, "entrada": entrada})


@app.get("/estadisticas")
def estadisticas_endpoint():
    """Reporte con las estadísticas de las predicciones realizadas."""
    return jsonify(estadisticas.generar_reporte())


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
