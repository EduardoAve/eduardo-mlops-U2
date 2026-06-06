# eduardo-mlops-U2 — Predictor de Enfermedades (Docker)

Servicio dockerizado que expone una función `predecir` para clasificar el estado
de un paciente a partir de sus síntomas. Es la solución desarrollada en la
**Unidad 1** de MLOps, ahora versionada en GitHub con un flujo de trabajo
profesional (ramas, Pull Requests y CI/CD) en la **Unidad 2**.

## Problema y propósito

Un médico necesita una herramienta de apoyo que, a partir de al menos tres
síntomas del paciente (fiebre, dolor, fatiga, duración y edad), sugiera su
estado de salud. El propósito de este repositorio es:

- Empaquetar y desplegar localmente esa solución con **Docker**.
- Mantener un **control de versiones** trazable mediante ramas y PRs.
- Incorporar nuevos requerimientos médicos y un pipeline de **CI/CD**.

> El "modelo" es una función determinista basada en un puntaje ponderado de los
> síntomas. No se entrena un modelo de ML real; el foco está en el empaquetado,
> el despliegue y el flujo de trabajo de MLOps.

## Estados que retorna el modelo

A partir de los síntomas, la función retorna uno de estos estados:

- `NO ENFERMO`
- `ENFERMEDAD LEVE`
- `ENFERMEDAD AGUDA`
- `ENFERMEDAD CRÓNICA`
- `ENFERMEDAD TERMINAL`

## Estructura del proyecto

```
eduardo-mlops-U2/
├── Dockerfile
├── .dockerignore
├── README.md
└── app/
    ├── main.py            # Servicio Flask (web + API)
    ├── model.py           # Función predecir + estados
    ├── estadisticas.py    # Registro y reporte de estadísticas
    ├── requirements.txt
    └── templates/
        └── index.html     # Formulario web
```

## Requisitos

- Docker (>= 20.x)

## Cómo construir la imagen

Desde la raíz del proyecto:

```bash
docker build -t eduardo-mlops-u2:latest .
```

## Cómo correr el contenedor

```bash
docker run --rm -p 5000:5000 --name predictor eduardo-mlops-u2:latest
```

El servicio queda expuesto en `http://localhost:5000`.

> **Nota para macOS**: el puerto `5000` lo usa AirPlay Receiver. Si ves el error
> `address already in use`, mapea otro puerto del host:
>
> ```bash
> docker run --rm -p 8080:5000 --name predictor eduardo-mlops-u2:latest
> ```
>
> Y usa `http://localhost:8080` en lugar de `:5000` en los ejemplos siguientes.

## Cómo obtener respuestas del modelo

### Opción 1 — Página web

Abrir en el navegador <http://localhost:5000>, llenar el formulario con los
síntomas y presionar **Predecir**.

### Opción 2 — API REST (JSON)

Endpoint: `POST /predecir`. Acepta un JSON con un objeto `sintomas` (dict) o una
lista.

```bash
curl -X POST http://localhost:5000/predecir \
     -H "Content-Type: application/json" \
     -d '{"sintomas": {"fiebre": 38.5, "dolor": 6, "fatiga": 7, "duracion_dias": 40, "edad": 65}}'
```

Respuesta:

```json
{
  "prediccion": "ENFERMEDAD CRÓNICA",
  "entrada": {"fiebre": 38.5, "dolor": 6, "fatiga": 7, "duracion_dias": 40, "edad": 65}
}
```

### Verificación de los estados

| Entrada                                                      | Estado esperado     |
| ------------------------------------------------------------ | ------------------- |
| `{fiebre: 36.5, dolor: 0, fatiga: 0}`                        | NO ENFERMO          |
| `{fiebre: 38.0, dolor: 2, fatiga: 2}`                        | ENFERMEDAD LEVE     |
| `{fiebre: 39.5, dolor: 7, fatiga: 8, duracion: 3}`           | ENFERMEDAD AGUDA    |
| `{fiebre: 38.5, dolor: 6, fatiga: 7, duracion: 60, edad: 70}`| ENFERMEDAD CRÓNICA  |
| `{fiebre: 41, dolor: 10, fatiga: 10, duracion: 200, edad: 80}`| ENFERMEDAD TERMINAL |

### Health check

```bash
curl http://localhost:5000/health
# {"status": "ok"}
```

## Reporte de estadísticas

Nuevo requerimiento (Unidad 2): los médicos pueden consultar un reporte con las
estadísticas de las predicciones realizadas. Cada predicción se exporta a un
archivo de texto (`data/predicciones.jsonl`, formato JSON Lines) y el servicio
expone un endpoint para leerlo y retornarlo.

Endpoint: `GET /estadisticas`

```bash
curl http://localhost:5000/estadisticas
```

El reporte incluye:

- **Número total de predicciones por cada categoría** (las 5 categorías siempre
  presentes, en 0 si no han ocurrido).
- **Últimas 5 predicciones** realizadas (de la más reciente a la más antigua).
- **Fecha de la última predicción**.

Respuesta (ejemplo, tras 2 predicciones):

```json
{
  "total_predicciones": 2,
  "total_por_categoria": {
    "NO ENFERMO": 1,
    "ENFERMEDAD LEVE": 0,
    "ENFERMEDAD AGUDA": 0,
    "ENFERMEDAD CRÓNICA": 0,
    "ENFERMEDAD TERMINAL": 1
  },
  "ultimas_5_predicciones": [
    {"fecha": "2026-06-06T18:30:05+00:00", "entrada": {"fiebre": 41, "dolor": 10, "fatiga": 10, "duracion_dias": 200, "edad": 80}, "prediccion": "ENFERMEDAD TERMINAL"},
    {"fecha": "2026-06-06T18:30:00+00:00", "entrada": {"fiebre": 36.5, "dolor": 0, "fatiga": 0}, "prediccion": "NO ENFERMO"}
  ],
  "fecha_ultima_prediccion": "2026-06-06T18:30:05+00:00"
}
```

Si aún no se ha realizado ninguna predicción, los totales están en 0, la lista
vacía y la fecha en `null`.

### Persistencia de las estadísticas

El archivo vive dentro del contenedor. Para conservarlo entre reinicios, monta
un volumen en `/app/data`:

```bash
docker run --rm -p 5000:5000 -v "$(pwd)/data:/app/data" --name predictor eduardo-mlops-u2:latest
```

La ruta del archivo se puede cambiar con la variable de entorno `STATS_PATH`.

## Detalle de la función `predecir`

Ver [`app/model.py`](app/model.py). La lógica:

1. Calcula un **puntaje** ponderado a partir de fiebre (>37.5 °C), dolor, fatiga
   y edad (>=60).
2. Si el puntaje es bajo → `NO ENFERMO`.
3. Si es moderado → `ENFERMEDAD LEVE`.
4. Si el puntaje es extremo (>= 14) y la condición es crónica → `ENFERMEDAD TERMINAL`.
5. Si es alto y la duración de los síntomas es >= 30 días → `ENFERMEDAD CRÓNICA`.
6. Si es alto y la duración es corta → `ENFERMEDAD AGUDA`.

## Flujo de trabajo del repositorio

La rama `main` se mantiene protegida y los cambios entran mediante Pull Requests
desde ramas de trabajo (`solución-inicial`, `nueva-prediccion`,
`reporte-estadisticas`, `añadir-github-actions`).
