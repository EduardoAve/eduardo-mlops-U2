"""
Registro y reporte de estadísticas de las predicciones realizadas.

Nuevo requerimiento (Unidad 2): los médicos necesitan un reporte con algunas
estadísticas de las predicciones. Cada predicción se exporta como una línea en
formato JSON (JSON Lines) dentro de un archivo de texto, que luego puede leerse
y retornarse cuando se solicite.

El reporte entrega:
  - Número total de predicciones realizadas por cada categoría.
  - Últimas 5 predicciones realizadas.
  - Fecha de la última predicción.

La ruta del archivo es configurable con la variable de entorno ``STATS_PATH``
(útil para las pruebas y para persistir vía un volumen de Docker). Por defecto
se guarda en ``data/predicciones.jsonl``.
"""

import json
import os
from datetime import datetime, timezone
from typing import Any, Dict, List

from model import ESTADOS

# Ruta por defecto del archivo de estadísticas. Se puede sobreescribir con la
# variable de entorno STATS_PATH (p. ej. para aislar el archivo en las pruebas).
DEFAULT_STATS_PATH = os.path.join("data", "predicciones.jsonl")


def _ruta() -> str:
    """Ruta efectiva del archivo de estadísticas (lee STATS_PATH en runtime)."""
    return os.environ.get("STATS_PATH", DEFAULT_STATS_PATH)


def registrar_prediccion(entrada: Any, prediccion: str) -> Dict[str, Any]:
    """
    Exporta una predicción al archivo de estadísticas.

    Cada llamada agrega una línea JSON con la fecha (ISO 8601, UTC), la entrada
    recibida y la categoría predicha. Crea el directorio contenedor si no existe.
    """
    ruta = _ruta()
    carpeta = os.path.dirname(ruta)
    if carpeta:
        os.makedirs(carpeta, exist_ok=True)

    registro = {
        "fecha": datetime.now(timezone.utc).isoformat(),
        "entrada": entrada,
        "prediccion": prediccion,
    }
    with open(ruta, "a", encoding="utf-8") as f:
        f.write(json.dumps(registro, ensure_ascii=False) + "\n")
    return registro


def _leer_registros() -> List[Dict[str, Any]]:
    """Lee y parsea todos los registros del archivo (lista vacía si no existe)."""
    ruta = _ruta()
    registros: List[Dict[str, Any]] = []
    if not os.path.exists(ruta):
        return registros
    with open(ruta, "r", encoding="utf-8") as f:
        for linea in f:
            linea = linea.strip()
            if not linea:
                continue
            try:
                registros.append(json.loads(linea))
            except json.JSONDecodeError:
                # Se ignoran líneas corruptas para no romper el reporte.
                continue
    return registros


def generar_reporte() -> Dict[str, Any]:
    """
    Construye el reporte de estadísticas a partir del archivo exportado.

    Si todavía no se ha realizado ninguna predicción, retorna los valores por
    defecto: todos los totales en 0, lista de últimas predicciones vacía y
    fecha de la última predicción en ``None``.
    """
    registros = _leer_registros()

    # Total por cada una de las categorías del modelo (todas presentes, en 0
    # si no han ocurrido). Las categorías desconocidas también se contabilizan.
    total_por_categoria: Dict[str, int] = {estado: 0 for estado in ESTADOS}
    for r in registros:
        pred = r.get("prediccion")
        total_por_categoria[pred] = total_por_categoria.get(pred, 0) + 1

    # Últimas 5 predicciones, de la más reciente a la más antigua.
    ultimas_5 = list(reversed(registros[-5:]))

    fecha_ultima = registros[-1]["fecha"] if registros else None

    return {
        "total_predicciones": len(registros),
        "total_por_categoria": total_por_categoria,
        "ultimas_5_predicciones": ultimas_5,
        "fecha_ultima_prediccion": fecha_ultima,
    }


def reiniciar() -> None:
    """Elimina el archivo de estadísticas (deja el reporte en su estado vacío)."""
    ruta = _ruta()
    if os.path.exists(ruta):
        os.remove(ruta)
