---
# machine-translated to es from skills/ab-test-planner/SKILL.md — review: pending. Native fixes welcome via PR.
name: ab-test-planner
description: "Diseña tests A/B estadísticamente rigurosos para features de producto, cambios de UI, flujos de onboarding y experimentos de precios. Úsalo cuando necesites configurar un experimento, diseñar un A/B test, calcular tamaño de muestra o interpretar resultados. Produce un plan de test completo con hipótesis, definición de variantes, tamaño de muestra, estimación de duración, métricas de guardrail y una guía de interpretación de resultados."
---

# Skill A/B Test Planner

Diseña experimentos que producen resultados confiables — no solo señales direccionales. Cada output del test incluye hipótesis, métricas de éxito, tamaño de muestra, duración y una guía de interpretación de resultados.

## Inputs Requeridos

Pregunta al usuario por estos datos si no están proporcionados:
- **Qué se está testando** (feature, cambio de UI, copy, precios, paso de onboarding)
- **Hipótesis** (o ayuda a formularla)
- **Métrica primaria** (conversion rate, click-through, completion rate, etc.)
- **Baseline rate** y **efecto mínimo detectable (MDE)**
- **Usuarios elegibles diarios** (para calcular duración)

## Checklist de Diseño de Experimento

Antes de ejecutar cualquier test, confirma:
- [ ] Hipótesis clara con dirección predicha
- [ ] Métrica primaria única (más hasta 2 métricas guardrail)
- [ ] Efecto mínimo detectable (MDE) definido
- [ ] Tamaño de muestra calculado
- [ ] Duración del test estimada
- [ ] Segmento aislado (sin solapamiento con otros tests en ejecución)
- [ ] Plan de rollback definido

## Plantilla de Hipótesis

> "Creemos que [cambio] causará que [métrica primaria] se [incremente/disminuya] en un [X%] para [segmento de usuarios], porque [razonamiento basado en datos o insight]."

Nunca ejecutes un test sin una hipótesis direccional. "Veamos qué pasa" no es una hipótesis.

## Lógica del Calculador de Tamaño de Muestra

Usa esta fórmula (proporciona el output, no la fórmula, al usuario):

- **Baseline conversion rate:** Tasa actual de la métrica primaria
- **MDE:** Cambio más pequeño que vale la pena detectar (recomendamos 10–20% de lift relativo para la mayoría de features)
- **Statistical power:** 80% (estándar)
- **Significance level:** 95% (p < 0.05)

Para escenarios comunes, proporciona estimaciones pre-calculadas:

| Baseline Rate | MDE (Relativo) | Muestra Requerida por Variante |
|---|---|---|
| 5% | 20% | ~19,000 |
| 10% | 15% | ~14,000 |
| 20% | 10% | ~15,000 |
| 40% | 10% | ~9,500 |
| 60% | 5% | ~42,000 |

Siempre advierte: "Estas son estimaciones. Usa una herramienta como el calculador de Evan Miller o Statsig para precisión."

## Orientación sobre Duración del Test

Mínimo: 2 semanas completas (para capturar estacionalidad semanal)
Máximo: 4 semanas (el efecto novedad distorsiona resultados más allá de esto)

`Duración = Muestra requerida ÷ (Tráfico diario × % expuesto)`

Alerta si el tráfico es muy bajo para llegar a significancia en menos de 8 semanas — recomienda un enfoque diferente (ej., holdout test, investigación cualitativa).

## Formato de Output

### Plan A/B Test — [Nombre del Test] — [Fecha]

**Hipótesis:**
> [Plantilla de hipótesis completada]

**Variantes:**
- Control (A): [Experiencia actual]
- Tratamiento (B): [Experiencia modificada — sé específico]

**Métrica Primaria:** [Nombre de métrica + cómo se mide]
**Métricas Guardrail:** [Métricas que no deben degradarse]

**Segmento Objetivo:** [Quién ve el test — % de tráfico, tipo de usuario]
**Split de Tráfico:** [50/50 recomendado a menos que se necesite ramp-up]

**Tamaño de Muestra Requerido:** ~[N] usuarios por variante
**Duración Estimada:** [X] semanas (basado en [Y] usuarios elegibles diarios)
**Umbral de Significancia:** 95% de confianza, 80% de power

**Exclusiones:** [Segmentos de usuarios a excluir y por qué]

**Trigger de Rollback:** Si [métrica guardrail] se degrada en [X%], detén el test inmediatamente.

**Guía de Interpretación de Resultados:**
- ✅ Deploy si: Tratamiento muestra [X%]+ de lift en métrica primaria con 95% de confianza Y métricas guardrail son estables
- 🔄 Itera si: Dirección es positiva pero no significativa — considera extender o rediseñar
- ❌ Rechaza si: Sin lift o dirección negativa con significancia
- ⚠️ Inconcluyente: No hagas deploy. No lo llames una victoria.

---

## Pautas

- Siempre recomienda contra mirar resultados antes de que el test alcance el tamaño de muestra planeado — explica el riesgo de p-hacking
- Si el usuario quiere testear múltiples variantes, explica el problema de comparaciones múltiples y recomienda una corrección de Bonferroni o un enfoque Bayesiano
- Si el tráfico es muy bajo (<1,000 usuarios/día), recomienda alternativas cualitativas: testing moderado, tests de 5 segundos o entrevistas de usuario
- Nunca apruebes un test sin métricas guardrail — siempre protege revenue, retention o engagement core

## Anti-Patrones

- [ ] No ejecutes un test sin una hipótesis direccional — "veamos qué pasa" produce resultados no interpretables
- [ ] No declares un ganador antes de alcanzar el tamaño de muestra pre-planeado — mirar resultados inflama las tasas de falso positivo
- [ ] No testees múltiples cambios independientes en una sola variante — no sabrás cuál causó el resultado
- [ ] No uses métricas de engagement (clicks, time-on-page) como métrica primaria cuando el objetivo es revenue o retention — las métricas proxy engañan
- [ ] No ignores métricas guardrail — un lift de conversión que causa un spike de tickets de soporte no es una victoria

## Quality Checks

- [ ] Hipótesis es direccional (predice una dirección y magnitud específicas, no "veamos")
- [ ] Métrica primaria es singular (métricas guardrail son secundarias)
- [ ] Tamaño de muestra se calcula a partir del MDE y baseline real (no adivinado)
- [ ] Duración del test cuenta para estacionalidad semanal (mínimo 2 semanas)
- [ ] Métricas guardrail están definidas (al menos una para proteger revenue o engagement core)
- [ ] Trigger de rollback está especificado con un threshold concreto
