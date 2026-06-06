"""
Pruebas unitarias del reporte de estadísticas, a través de la forma de
despliegue (peticiones al servicio Flask).
"""

import pytest

from main import app


@pytest.fixture
def client():
    return app.test_client()


def test_estadisticas_vacias_antes_de_cualquier_prediccion(client):
    """
    Antes de correr cualquier predicción, las estadísticas deben encontrarse
    vacías / con los valores por defecto.
    """
    reporte = client.get("/estadisticas").get_json()

    assert reporte["total_predicciones"] == 0
    assert reporte["fecha_ultima_prediccion"] is None
    assert reporte["ultimas_5_predicciones"] == []
    assert all(total == 0 for total in reporte["total_por_categoria"].values())


def test_ultima_prediccion_registrada_es_la_esperada(client):
    """
    Realizar una predicción que arroje un tipo de enfermedad y luego chequear
    las estadísticas para asegurar que la última predicción es la esperada.
    """
    # Parte de un estado vacío.
    assert client.get("/estadisticas").get_json()["total_predicciones"] == 0

    sintomas = {"fiebre": 41, "dolor": 10, "fatiga": 10, "duracion_dias": 200, "edad": 80}
    respuesta = client.post("/predecir", json={"sintomas": sintomas}).get_json()
    assert respuesta["prediccion"] == "ENFERMEDAD TERMINAL"

    reporte = client.get("/estadisticas").get_json()
    assert reporte["total_predicciones"] == 1
    assert reporte["fecha_ultima_prediccion"] is not None
    # La última predicción (la más reciente) es la que acabamos de realizar.
    assert reporte["ultimas_5_predicciones"][0]["prediccion"] == "ENFERMEDAD TERMINAL"
    assert reporte["total_por_categoria"]["ENFERMEDAD TERMINAL"] == 1
