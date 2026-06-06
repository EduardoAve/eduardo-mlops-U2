"""Pruebas unitarias de la función `predecir` (el modelo)."""

from model import ESTADOS, predecir


def test_categoria_esperada_para_sintomas_leves():
    """
    Dados unos parámetros de entrada, la respuesta del modelo es el tipo de
    enfermedad esperado: un paciente joven con síntomas leves -> ENFERMEDAD LEVE.
    """
    sintomas = {"fiebre": 38.0, "dolor": 2, "fatiga": 2, "duracion_dias": 1, "edad": 20}
    assert predecir(sintomas) == "ENFERMEDAD LEVE"


def test_se_obtienen_las_cinco_categorias():
    """
    Considerando distintos grupos de parámetros de entrada, se obtienen las 5
    categorías de enfermedades.
    """
    casos = {
        "NO ENFERMO":          {"fiebre": 36.5, "dolor": 0, "fatiga": 0},
        "ENFERMEDAD LEVE":     {"fiebre": 38.0, "dolor": 2, "fatiga": 2},
        "ENFERMEDAD AGUDA":    {"fiebre": 39.5, "dolor": 7, "fatiga": 8, "duracion_dias": 3},
        "ENFERMEDAD CRÓNICA":  {"fiebre": 38.5, "dolor": 6, "fatiga": 7, "duracion_dias": 60, "edad": 70},
        "ENFERMEDAD TERMINAL": {"fiebre": 41, "dolor": 10, "fatiga": 10, "duracion_dias": 200, "edad": 80},
    }

    obtenidas = {predecir(sintomas) for sintomas in casos.values()}
    # Se alcanzan exactamente las 5 categorías que define el modelo.
    assert obtenidas == set(ESTADOS)

    # Y cada grupo produce la categoría esperada.
    for categoria_esperada, sintomas in casos.items():
        assert predecir(sintomas) == categoria_esperada
