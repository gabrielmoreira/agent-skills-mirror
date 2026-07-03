---
# machine-translated to es from skills/data-analysis-standard/SKILL.md — review: pending. Native fixes welcome via PR.
name: data-analysis-standard
description: "Estructura un análisis de datos de producto, profundización en métricas, análisis de funnel o estudio de cohortes. Usa cuando se te pida analizar métricas de producto, investigar una caída en la conversión, explicar un cambio de datos a stakeholders o encontrar la causa raíz de un movimiento de métrica. Produce un análisis estructurado con pregunta, causa raíz, nivel de confianza y acción recomendada."
---

# Habilidad Data Analysis Standard

Convierte números crudos en decisiones de producto. Estructura cada análisis con una pregunta clara, metodología, hallazgo y acción recomendada.

## Marco de Análisis: El Método de 4 Preguntas

Todo análisis comienza aquí:
1. **¿Qué cambió?** (describe la métrica y su movimiento)
2. **¿Por qué cambió?** (causa raíz — segmento, paso del funnel, cohorte, canal)
3. **¿Y qué?** (impacto en el negocio o producto)
4. **¿Ahora qué?** (acción recomendada con nivel de confianza)

Nunca entregues datos sin responder las cuatro preguntas. Un gráfico sin narrativa no es un análisis.

---

## Plantilla de Triage de Métricas

Usa cuando una métrica se haya movido inesperadamente:

```
MÉTRICA: [Nombre]
MOVIMIENTO: [X% de cambio durante Y período]
LÍNEA BASE: [Cuál era lo normal]

VALIDACIÓN POR SEGMENTACIÓN:
- ¿Por plataforma (iOS / Android / Web)?
- ¿Por cohorte de usuario (nuevos / recurrentes / power users)?
- ¿Por canal de adquisición?
- ¿Por geografía?
- ¿Por plan/tier?

HIPÓTESIS DE CAUSA RAÍZ:
1. [Explicación más probable] — Evidencia: [punto de dato]
2. [Explicación alternativa] — Evidencia: [punto de dato]
3. [Descartando] — Eliminada porque: [razón]

CONCLUSIÓN: [Respuesta en una oración a "¿por qué cambió esto?"]
CONFIANZA: [Alta / Media / Baja] — basada en [datos disponibles]
```

---

## Estructura de Análisis de Funnel

| Etapa | Métrica | Actual | Benchmark/Meta | Caída % | Notas |
|---|---|---|---|---|---|
| [Inicio del funnel] | [Usuarios] | [N] | [N] | — | |
| [Paso 2] | [Usuarios] | [N] | [N] | [X%] | |
| [Paso 3] | [Usuarios] | [N] | [N] | [X%] | |
| [Conversión] | [Usuarios] | [N] | [N] | [X%] | |

**Mayor caída:** [Paso X → Paso Y] — Hipótesis: [razón]
**Investigación recomendada:** [consulta específica o test]

---

## Directrices de Análisis de Cohortes

Siempre define:
- **Definición de cohorte:** [Qué agrupa usuarios — semana de registro, primera acción, tipo de plan]
- **Métrica de retención:** [Qué cuenta como retención — login, acción principal, revenue]
- **Ventana de retención:** [D1, D7, D30, W4, M3, etc.]

Entrega una tabla de retención de cohortes y anota:
- Retención base para cada cohorte
- Cohortes que funcionan mejor/peor y por qué (lanzamiento de feature, campaña, estacional)
- Dirección de tendencia entre cohortes (mejorando / empeorando / estable)

---

## Formato de Output de Análisis para Stakeholders

### [Título del Análisis] — [Fecha]

**Pregunta que se responde:** [Pregunta específica en lenguaje claro]
**Período de tiempo:** [Rango de fechas]
**Fuente de datos:** [De dónde vienen los datos]

**Hallazgo:**
> [Resumen de 1–2 oraciones en lenguaje claro de qué muestran los datos]

**Gráfico/tabla clave:** [Incluir o describir]

**Causa raíz:** [Mejor explicación con evidencia]

**Nivel de confianza:** [Alto / Medio / Bajo] — [razón]

**Acción recomendada:**
1. [Acción inmediata — propietario, timeline]
2. [Investigación necesaria — qué verificar después]
3. [Monitoreo — qué métrica observar y a qué frecuencia]

**Qué este análisis NO nos dice:** [Salvedad importante — qué datos faltan o qué no se puede concluir]

---

## Inputs Requeridos

Pregunta al usuario por esto si no está proporcionado:
- **Métrica o pregunta** bajo investigación
- **Período de tiempo** (qué cambió, de cuándo a cuándo)
- **Datos disponibles** (qué segmentos, fuentes o queries tienes disponibles)
- **Contexto de negocio** (qué decisión informa este análisis)
- **Audiencia** (quién leerá esto — ejecutivo / equipo / equipo de datos)

## Validaciones de Calidad

- [ ] El análisis responde las 4 preguntas: qué cambió, por qué, y qué, ahora qué
- [ ] La causa raíz tiene evidencia (no solo hipótesis)
- [ ] El nivel de confianza está establecido y justificado
- [ ] Lo que los datos no pueden decirnos está nombrado explícitamente
- [ ] La acción recomendada incluye propietario y timeline

## Antipatrones

- [ ] No presentes correlaciones como causalidad — siempre establece la distinción explícitamente
- [ ] No reportes un movimiento de métrica sin indicar la ventana de tiempo y línea base de comparación
- [ ] No saltes el "y qué" — observaciones crudas sin acciones recomendadas son análisis incompleto
- [ ] No exageres la confianza — etiqueta hipótesis claramente y anota qué datos serían necesarios para confirmarlas
- [ ] No ignores breakdowns por segmento — métricas agregadas pueden enmascarar tendencias opuestas en subsegmentos

## Directrices

- Siempre indica qué los datos *no pueden* decirte — nunca sobrevenda confianza
- Las correlaciones no son causalidad — marca esto cada vez
- Si el usuario no tiene línea base, recomienda establecer una antes de extraer conclusiones
- Recomienda el gráfico más simple para cada hallazgo: barras para comparación, líneas para tendencias, scatter para correlación, tabla para breakdowns detallados
- Siempre especifica la ventana de tiempo — "la conversión bajó" es sin sentido sin "de X a Y durante Z período"
