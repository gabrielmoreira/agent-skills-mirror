---
# machine-translated to es from skills/product-health-analysis/SKILL.md — review: pending. Native fixes welcome via PR.
name: product-health-analysis
description: "Interpretar métricas de producto contra objetivos y exponer señales accionables. Utiliza cuando se te pida analizar la salud del producto, revisar métricas clave, investigar un problema de rendimiento, producir un informe de salud o evaluar señales de ajuste producto-mercado. Produce un informe de salud estructurado con estado RAG, análisis de tendencias, hipótesis de causa raíz y acciones priorizadas."
---

# Skill de Análisis de Salud del Producto

Transforma datos de métricas en bruto en una narrativa clara de salud — qué funciona, qué no, y qué requiere atención inmediata.

## Inputs Requeridos

Solicita al usuario estos datos si no están disponibles:
- **Datos de métricas** (valores actuales para métricas clave — incluso números aproximados funcionan)
- **Objetivos o puntos de referencia** (targets de OKR, líneas base históricas, o benchmarks de industria)
- **Período** (semana / mes / trimestre siendo analizado)
- **Área de producto o segmento** (¿estamos mirando el producto completo o una feature específica?)

## Marco de Métricas
Analiza a través de cuatro capas:
1. **Acquisition** — nuevos usuarios, calidad de fuente, tendencias de CAC
2. **Activation** — tiempo para primer valor, tasas de completitud de onboarding
3. **Engagement** — DAU/MAU, adopción de features, profundidad de sesión
4. **Retention** — retención D1/D7/D30, tasa de churn, tasa de resurrección

## Proceso
1. Para cada métrica, compara: período actual vs. período anterior, actual vs. objetivo
2. Marca cualquier cosa más del 10% fuera del objetivo como requiriendo investigación
3. Busca correlaciones — ¿una caída en activation explica una caída de retention 2 semanas después?
4. Escribe un resumen de salud en inglés claro (sin jerga) adecuado para compartir con stakeholders no técnicos
5. Recomienda top 3 áreas para investigación inmediata con pasos diagnósticos sugeridos
6. **Valida** — Confirma que cada métrica marcada tiene una hipótesis de causa raíz plausible, no solo un número en bruto, y cada acción recomendada tiene un propietario o equipo específico

## Estructura de Output

### Informe de Salud del Producto — [Período]
**Salud General:** 🟢 On Track / 🟡 Watch / 🔴 Action Required

| Métrica | Actual | Objetivo | vs. Período Anterior | Estado |
|---------|--------|----------|----------------------|--------|
| [métrica] | [valor] | [objetivo] | [+/-%] | [🟢/🟡/🔴] |

**Observaciones Clave:**
[3-5 observaciones puntuales escritas en inglés claro]

**Áreas Requiriendo Investigación:**
1. [Métrica + hipótesis + diagnóstico sugerido]
2. [Métrica + hipótesis + diagnóstico sugerido]
3. [Métrica + hipótesis + diagnóstico sugerido]

**Acciones Recomendadas:**
[Pasos específicos siguientes con propietarios y cronogramas]

## Verificaciones de Calidad

- [ ] Cada métrica incluye tanto un objetivo como una tendencia (no solo una captura de momento)
- [ ] Al menos una correlación se traza entre métricas (p. ej., activation → retention)
- [ ] Cada métrica marcada tiene una hipótesis de causa raíz, no solo "bajó"
- [ ] Las observaciones están escritas para un stakeholder no técnico (sin lenguaje de query en bruto o jerga de datos)
- [ ] La valoración general de salud está justificada con evidencia específica

## Anti-Patrones

- [ ] No reportes una única métrica agregada sin desgloses de segmentos — los promedios ocultan tendencias opuestas
- [ ] No marques una métrica como saludable solo porque esté por encima del objetivo — verifica si el objetivo en sí es significativo
- [ ] No listes movimientos de métricas sin hipótesis de causa raíz — observaciones sin explicaciones no son análisis
- [ ] No mezcles métricas de salud del producto con KPIs de negocio sin explicar la relación entre ellos
- [ ] No omitas acciones recomendadas — un informe de salud que solo describe problemas sin pasos priorizados siguientes está incompleto
