---
# machine-translated to es from skills/churn-analysis/SKILL.md — review: pending. Native fixes welcome via PR.
name: churn-analysis
description: "Produce a structured churn analysis that separates avoidable from unavoidable churn. Use when investigating why customers are leaving, identifying at-risk segments, calculating net revenue retention, or building a retention intervention plan. Produces a churn report with rate calculations, categorised reasons by avoidability, segment breakdown, timing analysis, early warning signals, and prioritised interventions ranked by estimated impact."
---

# Skill de Análisis de Churn

Produce un análisis de churn estructurado que vaya más allá de la tasa titular — identificando por qué se van los clientes, qué segmentos corren mayor riesgo, y qué intervenciones tendrán el mayor impacto en la retención.

## Lee de / Escribe en el Brain

Si existe un [`professional-brain`](../professional-brain/SKILL.md) (`brain/`), usa los datos que ya tienes en lugar de volver a preguntar:

- **Lee primero:** `context.md` (definiciones de métricas — qué significa "churn" aquí), `knowledge/`, y las `entities/` de segmentos relacionados. Ejecuta `python3 ../professional-brain/scripts/brain_query.py ./brain "churn"` y conserva la etiqueta de procedencia de cada hecho.
- **📥 Propón al Brain:** después de producir, propón registrar el hallazgo de retención principal en `knowledge/` (`[data]`), cualquier decisión de retención en `decisions/`, y los factores de riesgo como `hypotheses/`. Muéstralos, obtén un sí, y luego escribe con `../professional-brain/scripts/brain_write.py … --commit` (solo adición, simulación por defecto).

## Datos de Entrada Requeridos

Solicita estos si no se proporcionan ya:
- **Período de tiempo** siendo analizado (ej. Q1, últimos 12 meses)
- **Total de clientes al inicio del período** y **clientes perdidos**
- **ARR o ingresos perdidos** por churn
- **Datos de motivos de churn** — resultados de encuestas de salida, notas de CSM, datos de soporte, o motivos de pérdida de ventas
- **Segmentos de clientes** — por tier, industria, cohorte, o línea de producto
- **Tasa de retención actual** si se conoce
- **Cambios recientes** — precios, producto, modelo de soporte — que pueden haber afectado el churn

## Categorías de Churn

Clasifica siempre el churn antes de analizarlo:

| Categoría | Definición |
|---|---|
| **Voluntario — evitable** | El cliente se fue debido a un problema que podríamos haber resuelto (brechas de producto, onboarding deficiente, fallos en relaciones) |
| **Voluntario — inevitable** | El cliente se fue por razones fuera de nuestro control (recortes presupuestarios, adquisición, cierre de empresa) |
| **Involuntario** | Fallo de pago, no renovación de contrato por error, error administrativo |

Las intervenciones para cada categoría son diferentes. Confundirlas lleva a conclusiones equivocadas.

## Formato de Salida

---

# Análisis de Churn: [Producto / Segmento / Empresa]
**Período:** [Fecha de inicio] — [Fecha de fin]
**Preparado por:** [Nombre] | **Fecha:** [Fecha]

---

## Números Clave

| Métrica | Valor |
|---|---|
| Clientes al inicio del período | [N] |
| Clientes perdidos | [N] |
| **Tasa de churn de clientes** | **[X]%** |
| ARR al inicio del período | £/$/€[X] |
| ARR perdido por churn | £/$/€[X] |
| **Tasa de churn de ingresos (bruto)** | **[X]%** |
| ARR de expansiones (mismo período) | £/$/€[X] |
| **Net Revenue Retention (NRR)** | **[X]%** |

**Contexto de comparativa:**
- Tasa de churn de clientes: [X]% vs. comparativa de industria [Y]% — [por encima / por debajo / en línea]
- NRR: [X]% — [Qué significa: por encima del 100% = expansión compensa churn; por debajo del 100% = base encogiendo]

---

## Desglose de Churn por Categoría

| Categoría | Clientes | % del churn | ARR perdido |
|---|---|---|---|
| Voluntario — evitable | [N] | [X]% | £/$/€[X] |
| Voluntario — inevitable | [N] | [X]% | £/$/€[X] |
| Involuntario | [N] | [X]% | £/$/€[X] |
| **Total** | **[N]** | **100%** | **£/$/€[X]** |

**Churn evitable como % del churn total:** [X]% — este es el número que realmente podemos influir.

---

## Motivos de Churn — Solo Churn Evitable

Ordena por frecuencia. Incluye peso de ARR donde los datos lo permitan.

| Motivo | Conteo | % del churn evitable | ARR perdido | Cita representativa |
|---|---|---|---|---|
| [Motivo 1 — ej. "Producto falta característica clave"] | [N] | [X]% | £/$/€[X] | "[Cita]" |
| [Motivo 2] | [N] | [X]% | £/$/€[X] | "[Cita]" |
| [Motivo 3] | [N] | [X]% | £/$/€[X] | "[Cita]" |
| [Motivo 4] | [N] | [X]% | £/$/€[X] | "[Cita]" |
| Otro | [N] | [X]% | £/$/€[X] | — |

**Síntesis temática:** [2–3 oraciones agrupando los principales motivos en 2–3 temas. Ej. "Los tres principales motivos se agrupan en dos temas: brechas de producto en [área] (afectando X% del churn evitable) y fallos de onboarding donde los clientes nunca lograron valor (Y%)."]

---

## Churn por Segmento

Identifica qué segmentos tienen churn sobre o bajo el promedio.

### Por Tier

| Tier | Tasa de churn | vs. General | Notas |
|---|---|---|---|
| Enterprise | [X]% | +/-[X]pp | |
| Mid-Market | [X]% | +/-[X]pp | |
| SMB | [X]% | +/-[X]pp | |

### Por Cohorte (Año de Adquisición)

| Cohorte | Tasa de churn | Notas |
|---|---|---|
| [Año 1] | [X]% | |
| [Año 2] | [X]% | |
| [Año 3] | [X]% | |

### Por Industria / Caso de Uso (si hay datos disponibles)

| Segmento | Tasa de churn | Notas |
|---|---|---|
| [Segmento 1] | [X]% | |
| [Segmento 2] | [X]% | |

**Patrón clave:** [Qué segmento tiene la tasa de churn más alta y qué probablemente lo explica]

---

## Análisis de Temporalidad

- **Duración promedio del contrato antes del churn:** [X meses]
- **Momento de mayor riesgo:** [ej. "Mes 3 — cuando el valor de prueba se ha agotado pero la adopción completa no ha ocurrido"]
- **Distribución temporal del churn:**

| Cuándo ocurrió el churn | % de cuentas perdidas |
|---|---|
| 0–3 meses | [X]% |
| 3–6 meses | [X]% |
| 6–12 meses | [X]% |
| 12+ meses | [X]% |

---

## Señales de Alerta Temprana

Basado en las cuentas perdidas, identifica las señales que precedieron al churn (y podrían haber desencadenado intervención anterior):

| Señal | Tiempo de avance antes del churn | Cómo detectarla |
|---|---|---|
| [Señal 1 — ej. "DAU/MAU cayó por debajo del 15%"] | [~X semanas] | [Dashboard de uso / alerta] |
| [Señal 2 — ej. "No QBR en 90+ días"] | [~X semanas] | [Flag en CRM] |
| [Señal 3 — ej. "Defensor de la cuenta se fue"] | [~X semanas] | [Alerta de LinkedIn / seguimiento de CSM] |
| [Señal 4] | [~X semanas] | [Método de detección] |

---

## Recomendaciones de Intervención

Ordenadas por impacto estimado × viabilidad.

| Intervención | Dirige a | Est. reducción de churn | Esfuerzo | Propietario |
|---|---|---|---|---|
| [Intervención 1 — ej. "Mejorar onboarding para [segmento] con check-in dedicado de 30 días"] | [Motivo 1] | [X cuentas / £X ARR] | Bajo / Med / Alto | [Equipo] |
| [Intervención 2] | [Motivo 2] | [X cuentas / £X ARR] | Bajo / Med / Alto | [Equipo] |
| [Intervención 3] | [Motivo 3] | [X cuentas / £X ARR] | Bajo / Med / Alto | [Equipo] |

**Prioridad decidida:** [Cuál es la única intervención que, si se implementa este trimestre, tendría el mayor impacto y por qué]

---

## Lo que No Sabemos (Brechas de Datos)

- [Brecha de datos 1 — ej. "Tasa de respuesta de encuesta de salida es solo 30% — los datos de motivos pueden no ser representativos"]
- [Brecha de datos 2 — ej. "Sin datos de uso de producto para tier SMB — no se puede confirmar correlación de señal de uso"]
- [Brecha de datos 3]

---

## Anti-patrones

- [ ] No mezcles churn evitable e inevitable en planes de intervención — recomendar arreglos de producto para clientes que se fueron debido a cierre de empresa desperdicia recursos
- [ ] No calcules tasa de churn usando el conteo de clientes de fin de período como denominador — esto subestima el churn; siempre divide clientes perdidos entre la cohorte inicial
- [ ] No confíes únicamente en datos de encuesta de salida para motivos de churn — las tasas de respuesta típicamente son bajas y el sesgo de autoselección favorece clientes lo suficientemente comprometidos para completar una encuesta
- [ ] No recomiendes intervenciones sin vincularlas a un motivo de churn específico — intervenciones desconectadas de causas raíz no moverán la retención
- [ ] No reportes solo churn de ingresos bruto — sin net revenue retention (NRR), un número de retención saludable puede esconder una base de ingresos que se encoge

## Controles de Calidad

- [ ] Tasa de churn se calcula correctamente (perdidos ÷ cohorte inicial, no total de fin de período)
- [ ] Churn evitable e inevitable están separados — intervenciones solo dirigen al churn evitable
- [ ] Motivos de churn son reportados por cliente, no asumidos internamente
- [ ] Análisis de segmento identifica qué segmentos sobre-indexan — no solo promedios
- [ ] Señales de alerta temprana son específicas y detectables, no genéricas ("bajo engagement")
- [ ] Intervenciones vinculan directamente a los principales motivos de churn — sin recomendaciones sin emparejamiento de causa raíz
