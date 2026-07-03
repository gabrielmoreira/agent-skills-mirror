---
# machine-translated to es from skills/cohort-analysis/SKILL.md — review: pending. Native fixes welcome via PR.
name: cohort-analysis
description: "Estructura un análisis de cohortes para retención, LTV o patrones de comportamiento. Úsalo cuando te pidan ejecutar un análisis de cohortes, analizar retención por cohorte, segmentar usuarios por comportamiento en el tiempo, o calcular el valor de vida del cliente por período de adquisición. Produce un marco de análisis de cohortes completo con metodología, definiciones de cohortes, curvas de retención e intervenciones priorizadas."
---

# Skill de Análisis de Cohortes

Este skill produce un análisis de cohortes estructurado que cubre curvas de retención, estimación de LTV, segmentación por comportamiento e intervenciones accionables. El resultado está listo para presentar a la dirección de producto o compartir con equipos de crecimiento y datos.

## Inputs Necesarios

Pide al usuario estos datos si no están disponibles:
- **Objetivo del análisis** (mejora de retención / modelado de LTV / segmentación por comportamiento / predicción de churn)
- **Producto o feature que se analiza**
- **Definición de cohorte** — ¿qué agrupa a los usuarios? (mes de adquisición, canal de signup, tier de plan, adopción de feature)
- **Ventana de observación** — ¿cuántos períodos rastrear? (p. ej. 12 meses, 8 semanas)
- **Métrica clave** — ¿qué mides por cohorte? (tasa de retención, ingresos, engagement score, uso de feature)
- **Datos disponibles** — ¿qué tablas/métricas hay disponibles? (pega el esquema o describe)
- **Baseline** — ¿hay benchmarks o metas de retención existentes?

## Estructura del Output

---

# Análisis de Cohortes: [Producto / Feature]

**Tipo de análisis:** [Retención / LTV / Comportamiento / Churn]
**Definición de cohorte:** [Mes de adquisición / Canal de signup / Tier de plan / Fecha de adopción de feature]
**Ventana de observación:** [X meses / semanas]
**Métrica principal:** [Nombre de la métrica]
**Fecha de preparación:** [Fecha]

---

## 1. Definiciones de Cohortes

| Cohorte | Período | Tamaño | Descripción |
|---|---|---|---|
| [Cohorte 1] | [Ene 2025] | [N usuarios] | [p. ej. Usuarios que se registraron en ene 2025 a través de orgánico] |
| [Cohorte 2] | [Feb 2025] | [N usuarios] | [...] |

**Lógica de cohorte:**
- Evento de entrada a cohorte: [Primer registro / Primera compra / Activación de feature]
- Criterios de salida de cohorte: [Churnado / Downgrade / Sin actividad durante 30 días]
- Exclusiones: [Usuarios de prueba / Cuentas de prueba internas / Usuarios con < X días de datos]

---

## 2. Curva de Retención

**Cómo leer:** Cada celda muestra qué % de la cohorte realizó la métrica clave en el período N.

| Cohorte | Período 0 | Período 1 | Período 2 | Período 3 | Período 6 | Período 12 |
|---|---|---|---|---|---|---|
| Ene 2025 | 100% | [X%] | [X%] | [X%] | [X%] | [X%] |
| Feb 2025 | 100% | [X%] | [X%] | [X%] | [X%] | [X%] |
| [Tendencia] | — | [↑/↓ vs anterior] | [...] | [...] | [...] | [...] |

**Meseta de retención:** [¿En qué período se estabiliza la retención? ¿En qué % se estabiliza?]

**Observaciones clave:**
- [p. ej. La caída de Período 1 → Período 2 es la mayor — churn promedio de X% en los primeros 30 días]
- [p. ej. Las cohortes adquiridas a través de [canal] retienen X% mejor en Período 6]
- [p. ej. La retención ha mejorado de X% → Y% en Período 3 comparando la cohorte más antigua con la más reciente]

**Curvas de retención, dibujadas** — también renderiza las curvas como un gráfico de líneas Mermaid/chart para que la meseta y las brechas entre cohortes sean visibles (se renderiza en vivo en el playground y se exporta como PNG). Una línea por cohorte, período en el eje x:

```chart
{
  "type": "line",
  "title": "Retención por cohorte (%)",
  "labels": ["P0", "P1", "P2", "P3", "P6", "P12"],
  "series": [
    { "name": "Ene 2025", "data": [100, 62, 51, 45, 40, 37] },
    { "name": "Feb 2025", "data": [100, 66, 55, 49, 44, 41] }
  ]
}
```

---

## 3. Proyección de LTV (si aplica)

**ARPU por período:** [£/$/€ X por usuario activo por mes]
**Curva de retención utilizada:** [Qué cohorte o promedio combinado]

| Período | Retenido % | Ingresos por usuario | LTV acumulado |
|---|---|---|---|
| Mes 1 | [X%] | [£X] | [£X] |
| Mes 3 | [X%] | [£X] | [£X] |
| Mes 6 | [X%] | [£X] | [£X] |
| Mes 12 | [X%] | [£X] | [£X] |

**LTV combinado:** [£X a 12 meses — basado en retención combinada entre cohortes]

**LTV por segmento:**
| Segmento | LTV (12M) | vs Baseline |
|---|---|---|
| [Orgánico] | [£X] | [+X%] |
| [Paid] | [£X] | [-X%] |
| [Enterprise] | [£X] | [+X%] |

---

## 4. Segmentación por Comportamiento

Agrupa cohortes por patrones de comportamiento, no solo por fecha de adquisición:

| Segmento | Definición | Tamaño | Retención (P6) | LTV (12M) |
|---|---|---|---|---|
| **Power users** | [Usó feature central ≥ 3x/semana en primeros 30 días] | [X%] | [X%] | [£X] |
| **Casual users** | [Usó 1–2x/semana en primeros 30 días] | [X%] | [X%] | [£X] |
| **Dormant** | [Inició sesión pero no usó feature central] | [X%] | [X%] | [£X] |
| **Never activated** | [Se registró pero nunca completó onboarding] | [X%] | [X%] | [£X] |

**Insight de activación:** [Qué acción — realizada en los primeros X días — predice mejor la retención? Este es el "momento aha" a optimizar.]

---

## 5. Indicadores Adelantados de Churn

Lista las señales que aparecen **antes** de que los usuarios hagan churn, para que los equipos puedan intervenir:

| Señal | ¿Con cuánta anticipación aparece? | Correlación con churn | Intervención |
|---|---|---|---|
| [Sin login durante 7 días] | [7 días antes del churn] | [Fuerte] | [Secuencia de email de re-engagement] |
| [Ticket de soporte con escalada] | [14 días antes del churn] | [Moderada] | [Outreach de CSM dentro de 48 horas] |
| [Uso de feature cayó >50% WoW] | [10 días antes del churn] | [Fuerte] | [Nudge in-app con tutorial de caso de uso] |

---

## 6. Comparación de Cohortes: Qué Ha Cambiado en el Tiempo

Compara la cohorte más antigua con la más reciente para evaluar si las mejoras de producto se reflejan en la retención:

| Métrica | [Cohorte más antigua — p. ej. Ene 2024] | [Cohorte más reciente — p. ej. Ene 2025] | Cambio |
|---|---|---|---|
| Retención Período 1 | [X%] | [X%] | [↑/↓ X pp] |
| Retención Período 3 | [X%] | [X%] | [↑/↓ X pp] |
| Tasa de activación | [X%] | [X%] | [↑/↓ X pp] |
| Sesiones promedio en primeros 30 días | [X] | [X] | [↑/↓] |

**Veredicto:** [¿Las cohortes más recientes rinden mejor o peor? ¿Qué se lanzó en ese período que podría explicar el cambio?]

---

## 7. Recomendaciones

Prioriza por impacto en la curva de retención:

| # | Recomendación | Segmento objetivo | Impacto esperado | Esfuerzo | Prioridad |
|---|---|---|---|---|---|
| 1 | [p. ej. Rediseñar onboarding para alcanzar hito de activación en día 1, no día 7] | [Segmento never-activated] | [+X pp retención P1] | [Medio] | P1 |
| 2 | [p. ej. Lanzar secuencia de re-engagement en trigger de inactividad día 7] | [Segmento dormant] | [+X pp retención P2] | [Bajo] | P1 |
| 3 | [p. ej. Introducir features de power-user más temprano para acelerar formación de hábito] | [Casual users] | [+X pp LTV P6] | [Alto] | P2 |

---

## 8. Referencia SQL (si aplica)

Proporciona la query de cohorte principal para que equipos de datos puedan replicar o extender el análisis:

```sql
-- Query de cohorte de retención
SELECT
  DATE_TRUNC('month', u.created_at) AS cohort_month,
  DATE_TRUNC('month', e.event_date) AS activity_month,
  DATEDIFF('month', u.created_at, e.event_date) AS period,
  COUNT(DISTINCT e.user_id) AS retained_users,
  COUNT(DISTINCT c.user_id) AS cohort_size,
  ROUND(COUNT(DISTINCT e.user_id) * 100.0 / COUNT(DISTINCT c.user_id), 1) AS retention_rate
FROM users u
JOIN events e ON u.user_id = e.user_id
JOIN (
  SELECT user_id, DATE_TRUNC('month', created_at) AS cohort_month
  FROM users
  WHERE created_at >= '[start_date]'
) c ON u.user_id = c.user_id AND DATE_TRUNC('month', u.created_at) = c.cohort_month
WHERE e.event_type = '[key_retention_event]'
GROUP BY 1, 2, 3
ORDER BY 1, 3;
```

---

## Controles de Calidad

- [ ] Definición de cohorte es inequívoca — el mismo usuario no puede aparecer en dos cohortes
- [ ] Curva de retención muestra una meseta clara, o el análisis indica que la ventana es demasiado corta para verla
- [ ] Proyección de LTV usa retención observada, no asumida
- [ ] Segmentos de comportamiento son mutuamente excluyentes y exhaustivos
- [ ] Recomendaciones están vinculadas a hallazgos específicos de cohorte o segmento — no son consejos de crecimiento genéricos
- [ ] Indicadores adelantados son observables en datos de producción, no solo en teoría

## Anti-Patrones

- [ ] No permitas que el mismo usuario aparezca en múltiples cohortes — las cohortes superpuestas producen números de retención que no se pueden comparar ni actuar
- [ ] No asumas ARPU en proyecciones de LTV — usa ingresos observados por usuario retenido por período, no un promedio combinado que oculte diferencias de segmento
- [ ] No saques conclusiones de cohortes demasiado pequeñas para ser estadísticamente significativas — marca umbrales de tamaño mínimo de cohorte y anota cuándo una cohorte es demasiado pequeña para confiar
- [ ] No confundas tasa de retención con tasa de engagement — un usuario que inicia sesión pero no completa el evento de retención clave no está retenido por la definición utilizada
- [ ] No hagas recomendaciones sin conectarlas a hallazgos específicos de cohorte o segmento — el consejo de crecimiento genérico que se podría aplicar a cualquier producto no añade valor

## Frases Gatillo de Ejemplo

- "Ejecuta un análisis de cohortes para nuestro producto SaaS"
- "Analiza retención por mes de adquisición para las últimas 12 cohortes"
- "¿Cuál es el LTV de usuarios que vinieron a través de paid vs orgánico?"
- "Construye un modelo de retención de cohortes mostrando período 0 a período 12"
- "Segmenta usuarios por comportamiento y muéstrame qué grupo retiene mejor"
