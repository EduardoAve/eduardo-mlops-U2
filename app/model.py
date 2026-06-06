"""
Función "modelo" simulada para el Taller 1 de MLOps.

No se entrena un modelo real. La función toma síntomas del paciente y
retorna uno de cinco estados posibles:

    - NO ENFERMO
    - ENFERMEDAD LEVE
    - ENFERMEDAD AGUDA
    - ENFERMEDAD CRÓNICA
    - ENFERMEDAD TERMINAL

La lógica usa un puntaje ponderado a partir de los síntomas para
garantizar que cada uno de los cinco estados sea alcanzable según
los parámetros de entrada.
"""

from typing import Dict, List, Union

ESTADOS = [
    "NO ENFERMO",
    "ENFERMEDAD LEVE",
    "ENFERMEDAD AGUDA",
    "ENFERMEDAD CRÓNICA",
    "ENFERMEDAD TERMINAL",
]

SintomasInput = Union[Dict[str, float], List[float]]


def _normalizar_entrada(sintomas: SintomasInput) -> Dict[str, float]:
    """Acepta dict o lista y lo normaliza a un dict con claves esperadas."""
    claves = ["fiebre", "dolor", "fatiga", "duracion_dias", "edad"]

    if isinstance(sintomas, dict):
        datos = {k: float(sintomas.get(k, 0)) for k in claves}
    elif isinstance(sintomas, (list, tuple)):
        if len(sintomas) < 3:
            raise ValueError("Se requieren al menos 3 valores de entrada.")
        datos = {k: 0.0 for k in claves}
        for i, v in enumerate(sintomas):
            if i < len(claves):
                datos[claves[i]] = float(v)
    else:
        raise TypeError("sintomas debe ser dict o list/tuple.")

    return datos


def predecir(sintomas: SintomasInput) -> str:
    """
    Predice el estado del paciente a partir de sus síntomas.

    Parámetros esperados (todos numéricos, 0 si no aplica):
        - fiebre:        temperatura en °C (ej. 36.5 - 41.0)
        - dolor:         intensidad 0-10
        - fatiga:        intensidad 0-10
        - duracion_dias: días con síntomas
        - edad:          edad del paciente en años

    Retorna uno de: NO ENFERMO, ENFERMEDAD LEVE, ENFERMEDAD AGUDA,
    ENFERMEDAD CRÓNICA, ENFERMEDAD TERMINAL.
    """
    datos = _normalizar_entrada(sintomas)

    fiebre = datos["fiebre"]
    dolor = datos["dolor"]
    fatiga = datos["fatiga"]
    duracion = datos["duracion_dias"]
    edad = datos["edad"]

    # Puntaje compuesto: cada síntoma aporta de forma ponderada.
    puntaje = 0.0
    if fiebre >= 37.5:
        puntaje += (fiebre - 37.0) * 2.0
    puntaje += dolor * 0.6
    puntaje += fatiga * 0.5
    if edad >= 60:
        puntaje += 1.5

    # La duración de los síntomas decide entre estado agudo y crónico.
    es_cronico = duracion >= 30

    # Nuevo requerimiento (Unidad 2): la categoría ENFERMEDAD TERMINAL se
    # alcanza cuando el cuadro es de gravedad extrema (puntaje muy alto) y
    # además prolongado (crónico). Es el escalón más severo del modelo.
    GRAVEDAD_TERMINAL = 14.0
    es_terminal = es_cronico and puntaje >= GRAVEDAD_TERMINAL

    if puntaje < 2.0:
        return "NO ENFERMO"
    if puntaje < 5.0:
        return "ENFERMEDAD LEVE"
    if es_terminal:
        return "ENFERMEDAD TERMINAL"
    if es_cronico:
        return "ENFERMEDAD CRÓNICA"
    return "ENFERMEDAD AGUDA"
