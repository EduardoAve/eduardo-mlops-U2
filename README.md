# eduardo-mlops-U2

Repositorio de la **Unidad 2** del curso de MLOps (Maestría). Aquí se lleva el
control de versiones, el flujo de trabajo con GitHub y el pipeline de CI/CD del
servicio de **predicción de enfermedades** desarrollado en la Unidad 1.

## Problema

Un médico necesita una herramienta que, a partir de los síntomas de un paciente
(fiebre, dolor, fatiga, duración de los síntomas y edad), prediga su estado de
salud. La solución es un servicio contenedorizado con Docker que expone una
función `predecir`. Este repositorio versiona dicha solución y le añade un flujo
de trabajo profesional sobre GitHub.

## Propósito

- Mantener un **control de versiones** ordenado de la solución mediante ramas y
  Pull Requests (PRs).
- Incorporar **nuevos requerimientos médicos** de forma trazable.
- Automatizar **pruebas y despliegue** con un pipeline de CI/CD en GitHub Actions.

## Estructura del repositorio

> Se irá completando a medida que se integren las ramas de trabajo.

```
eduardo-mlops-U2/
├── README.md              # Este archivo (problema, propósito, estructura, uso)
├── Dockerfile             # Empaquetado del servicio
├── app/                   # Código del servicio (función predecir + API/web Flask)
├── tests/                 # Pruebas unitarias (pytest)
└── .github/workflows/     # Pipelines de CI/CD (GitHub Actions)
```

## Flujo de trabajo

La rama `main` está protegida: los cambios entran únicamente mediante **Pull
Requests** desde ramas de trabajo. Las ramas previstas son:

| Rama | Propósito |
| --- | --- |
| `solución-inicial` | Solución de la Unidad 1 (servicio Docker + función `predecir`). |
| `nueva-prediccion` | Nuevo requerimiento: categoría `ENFERMEDAD TERMINAL`. |
| `reporte-estadisticas` | Nuevo requerimiento: reporte de estadísticas de predicciones. |
| `añadir-github-actions` | Pipeline de CI/CD con GitHub Actions. |
