"""
Configuración común de las pruebas (pytest).

- Agrega la carpeta ``app/`` al ``sys.path`` para poder importar los módulos del
  servicio (``model``, ``estadisticas``, ``main``).
- Aísla el archivo de estadísticas en un directorio temporal único por prueba,
  de modo que cada test arranca con las estadísticas vacías.
"""

import os
import sys

import pytest

# Raíz del repositorio y carpeta de la aplicación.
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "app"))


@pytest.fixture(autouse=True)
def stats_aisladas(tmp_path, monkeypatch):
    """Usa un archivo de estadísticas temporal y vacío para cada prueba."""
    ruta = tmp_path / "predicciones.jsonl"
    monkeypatch.setenv("STATS_PATH", str(ruta))
    yield
