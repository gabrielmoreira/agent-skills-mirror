---
# machine-translated to es from skills/metrics-framework/SKILL.md — review: pending. Native fixes welcome via PR.
name: metrics-framework
description: "Construye un marco de métricas para cualquier producto, equipo o negocio. Úsalo cuando se solicite un árbol de métricas, marco de KPI, métrica North Star, embudo AARRR, marco HEART, u OKR de métricas. Produce una jerarquía de métricas estructurada desde North Star hasta indicadores adelantados, con orientación sobre medición."
---

# Marco de Métricas — Skill

Este skill construye un marco de métricas completo adaptado a un producto o negocio. Conecta la métrica North Star con indicadores adelantados accionables, dejando claro qué métricas rastrear, cuáles optimizar y cómo se relacionan entre sí.

## Inputs Obligatorios

Pide al usuario estos datos si no se proporcionan:
- **Descripción del producto o negocio** (un párrafo es suficiente)
- **Modelo de negocio** (SaaS / Marketplace / E-commerce / App de consumo / B2B / Otro)
- **Etapa** (Pre-PMF / Crecimiento / Escala / Maduro)
- **Preferencia de marco** (si tienen una): North Star + Árbol de Métricas / AARRR / HEART / OKR / Personalizado
- **Objetivo principal este trimestre** (p. ej. crecer activación, reducir churn, aumentar ingresos)

Si no se especifica preferencia de marco, recomienda el mejor ajuste según la etapa y modelo de negocio.

## Lee/Escribe en el Cerebro

Si existe un [`professional-brain`](../professional-brain/SKILL.md) (`brain/`), úsalo antes de preguntar:

- **Lee primero:** `context.md` para las *definiciones* de métricas que la organización ya acordó (reutilízalas — no redefinas una métrica silenciosamente) y `knowledge/strategy.md` para qué está optimizando el negocio.
- **Escribe después:** guarda el árbol de métricas y definiciones en `knowledge/`, y cualquier decisión de objetivos en `decisions/`, cada uno marcado con procedencia para que un objetivo `[hunch]` no se trate como un objetivo comprometido.

## Estructura del Output

### 1. Recomendación de Marco (si no se especifica)

Explica en 2–3 frases por qué recomiendas este marco para su contexto.

---

### 2. Métrica North Star

**[Nombre de la Métrica]:** [Definición — exactamente qué se mide y cómo]

**Por qué esta es la North Star correcta para este negocio:**
[2–3 frases. Debe reflejar el valor entregado al cliente, no solo ingresos o actividad. Explica qué comportamiento captura y por qué maximizarla se correlaciona con la salud comercial a largo plazo.]

**Cómo medirla:** [Fórmula o fuente de datos]
**Baseline actual:** [Deja como [AGREGAR BASELINE] para que el usuario complete]
**Objetivo:** [Deja como [AGREGAR OBJETIVO] para que el usuario complete]

---

### 3. Árbol de Métricas

Muestra cómo las métricas de apoyo se agrupan en la North Star. Formato como jerarquía:

```
[Métrica North Star]
├── [Driver 1: p. ej. Adquisición]
│   ├── [Métrica L2: p. ej. Signups orgánicos / semana]
│   └── [Métrica L2: p. ej. CAC pagado por canal]
├── [Driver 2: p. ej. Activación]
│   ├── [Métrica L2: p. ej. % usuarios completando onboarding en 7 días]
│   └── [Métrica L2: p. ej. Tiempo hasta primera acción de valor]
└── [Driver 3: p. ej. Retención]
    ├── [Métrica L2: p. ej. Tasa de retención Day 30]
    └── [Métrica L2: p. ej. Profundidad de adopción de funciones]
```

Para cada métrica L2, proporciona:
- **Definición:** [Qué exactamente se mide]
- **Por qué importa:** [Cómo se conecta con la North Star]
- **¿Adelantada o rezagada?** [Adelantada = predictiva / Rezagada = resultado]
- **Cómo medirla:** [Fuente de datos o cálculo]

---

### 4. Contra-Métricas

[2–3 métricas a monitorear que evitan optimizar la North Star de formas que dañen el negocio. P. ej. "Si optimizamos por signups, necesitamos monitorear la tasa de cuentas spam. Si optimizamos por engagement, necesitamos monitorear el volumen de tickets de soporte."]

---

### 5. Recomendación de Dashboard

Sugiere una estructura de dashboard de 3 niveles:
- **Vista ejecutiva (semanal):** [3–5 métricas — solo resultados]
- **Vista de equipo (diaria):** [7–10 métricas — indicadores adelantados + outputs]
- **Vista diagnóstica (bajo demanda):** [Métricas para profundizar cuando algo se ve mal]

---

### 6. Preguntas de Health Check de Métricas

[5 preguntas que el equipo debe hacer en su revisión semanal de métricas para convertir números en insights. P. ej. "¿Está mejorando nuestra tasa de activación mientras la retención se mantiene plana? Eso sugiere un problema de calidad del onboarding, no un problema de product-market fit."]

---

## Quality Checks

- [ ] North Star refleja valor del cliente, no solo actividad comercial
- [ ] Árbol de métricas tiene 3–4 drivers distintos (no todo en una categoría)
- [ ] Cada métrica L2 está clasificada como adelantada o rezagada
- [ ] Se incluyen contra-métricas para prevenir incentivos perversos
- [ ] Los niveles de dashboard se adaptan a la etapa del producto
- [ ] Todas las definiciones de métricas son inequívocas (fórmula o descripción clara)

## Anti-Patrones

- [ ] No establecer una North Star que mida actividad comercial (ingresos, pageviews) en lugar de valor entregado al cliente — esto crea incentivos desalineados con la calidad del producto
- [ ] No definir métricas sin especificar la fórmula o fuente de datos — una métrica ambigua será medida diferente por diferentes personas
- [ ] No saltarse contra-métricas — optimizar cualquier métrica única sin un guard rail eventualmente producirá incentivos perversos
- [ ] No incluir más de 4–5 métricas en una vista de equipo diaria — un dashboard con 20 métricas es un dashboard que nadie mira
- [ ] No clasificar todas las métricas como "adelantadas" — sé honesto sobre cuáles son métricas de resultado rezagadas y cuáles genuinamente predicen resultados futuros

## Frases Trigger de Ejemplo

- "Construye un marco de métricas para [producto]"
- "¿Cuál debería ser nuestra métrica North Star?"
- "Crea un árbol de KPI para [negocio]"
- "Dame un desglose AARRR para [producto]"
- "¿Qué métricas debe rastrear nuestro equipo de [tipo de equipo]?"
