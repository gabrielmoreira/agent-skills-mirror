---
# machine-translated to es from skills/retro-analysis/SKILL.md — review: pending. Native fixes welcome via PR.
name: retro-analysis
description: "Analiza datos de entrega de sprint y produce un resumen estructurado de retrospectiva. Úsalo cuando se pida ejecutar una retrospectiva, analizar datos de sprint, preparar un resumen de retro o convertir métricas de sprint en puntos de discusión. Produce un resumen de retrospectiva fundamentado en datos con estadísticas de finalización, análisis de patrones, preguntas para Iniciar/Detener/Continuar, y un experimento concreto para el próximo sprint."
---

# Skill de Análisis de Retrospectiva

Genera un resumen de retrospectiva fundamentado en datos que separa hechos de percepciones, para que el equipo dedique el tiempo de retro a soluciones en lugar de debatir qué pasó.

## Inputs Requeridos

Pide al usuario estos datos si no se proporcionan:
- **Tickets del sprint: planificados vs. completados**
- **Tickets llevados al siguiente sprint y razones** (si se conocen)
- **Tickets reabiertos después de cerrar** (señal de calidad)
- **Cualquier incidente o trabajo no planificado** (señal de scope creep)
- **Velocidad del sprint vs. promedio histórico** (contexto de tendencia)

## Proceso
1. Calcula: tasa de finalización, tasa de carry-over, porcentaje de trabajo no planificado
2. Identifica patrones: ¿qué tipos de tickets tenían más probabilidad de ser llevados? ¿Cuáles causaron bloqueos?
3. Anota cualquier ruptura de procesos o comunicación visible en los datos
4. Prepara 3 preguntas "Iniciar / Detener / Continuar" basadas en los datos — no genéricas, específicas de este sprint
5. Sugiere 1 experimento concreto para el próximo sprint basado en el mayor punto de fricción
6. **Valida** — Confirma que cada pregunta es específica de este sprint (no una pregunta genérica reciclada), y que el experimento recomendado es concreto y medible

## Estructura del Output

### Resumen de Retrospectiva Sprint [Número]

**Por los Números:**
- Planificado: [n] tickets | Completado: [n] | Carry-over: [n] | Tasa de finalización: [%]
- Trabajo no planificado: [n] tickets ([%] de capacidad)
- Velocidad: [puntos] vs. [promedio] promedio

**Lo que Sugieren los Datos:**
[2-3 observaciones fundamentadas en los números anteriores]

**Preguntas para la Discusión:**
- Iniciar: [pregunta específica basada en datos de este sprint]
- Detener: [pregunta específica basada en datos de este sprint]
- Continuar: [pregunta específica basada en datos de este sprint]

**Experimento Sugerido para el Próximo Sprint:**
[Un cambio de proceso concreto y comprobable — con una métrica específica de éxito]

## Verificaciones de Calidad

- [ ] Cada pregunta Iniciar/Detener/Continuar nombra un comportamiento específico, no una categoría vaga
- [ ] El experimento recomendado es comprobable en un sprint
- [ ] El análisis de carry-over identifica el tipo de ticket o causa, no solo el número
- [ ] Las observaciones de datos no asignan culpa — describen patrones
- [ ] La tendencia de velocidad se menciona en contexto (¿es esto un caso aislado o un patrón?)

## Anti-Patrones

- [ ] No asignes culpa a individuos en el resumen de retrospectiva — las observaciones deben describir patrones, no personas
- [ ] No produzcas preguntas Iniciar/Detener/Continuar que sean categorías vagas — cada una debe nombrar un comportamiento específico
- [ ] No recomiendes un experimento que no pueda completarse en un sprint — solo experimentos pequeños y comprobables
- [ ] No trates tickets de carry-over como un problema de velocidad sin antes identificar la categoría de causa raíz
- [ ] No ejecutes el mismo formato de retrospectiva cada sprint — varía el formato para prevenir fatiga de engagement
