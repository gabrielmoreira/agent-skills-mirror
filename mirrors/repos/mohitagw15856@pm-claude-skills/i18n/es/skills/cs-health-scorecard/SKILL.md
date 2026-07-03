---
# machine-translated to es from skills/cs-health-scorecard/SKILL.md — review: pending. Native fixes welcome via PR.
name: cs-health-scorecard
description: "Construir un cuadro de mando de salud del cliente para una cuenta específica. Úsalo cuando se te pida puntuar la salud de la cuenta, evaluar el riesgo de renovación, construir un panel de salud, o valorar la probabilidad de que una cuenta se renueve o expanda. Produce un cuadro de mando de salud estructurado con estado RAG, puntuaciones por dimensión, riesgos clave y acciones recomendadas."
---

# Skill de Cuadro de Mando de Salud del Cliente

Produce un cuadro de mando de salud estructurado y basado en datos para una cuenta de cliente — proporcionando al CSM y a la dirección una visión clara del riesgo de renovación, potencial de expansión, y las acciones necesarias para mover la cuenta en la dirección correcta.

## Lee desde / Escribe en el Brain

Si existe un [`professional-brain`](../professional-brain/SKILL.md) (`brain/`), utiliza la información en lugar de volver a preguntar lo que ya sabes:

- **Lee primero:** el archivo `entities/` de la cuenta, sus `stakeholders/` (campeón, comprador económico, detractores) y `knowledge/`. Ejecuta `python3 ../professional-brain/scripts/brain_query.py ./brain "<nombre de cuenta>"` y mantén la etiqueta de procedencia de cada hecho.
- **📥 Propón al Brain:** después de producir, propón registrar el veredicto de salud + riesgos clave en el archivo `entities/` de la cuenta, y una entrada de riesgo de renovación en `decisions/` si se toma una decisión, cada una con etiqueta de procedencia. Muéstralas, obtén un sí, y luego escribe con `../professional-brain/scripts/brain_write.py … --commit` (solo append, dry-run por defecto).

## Entradas Requeridas

Pregunta por estas si no se proporcionan ya:
- **Nombre de la cuenta** y tier (enterprise / mid-market / SMB)
- **Valor del contrato** (ARR) y **fecha de renovación**
- **Datos de uso del producto** — logins, ratio DAU/MAU, adopción de funcionalidades clave
- **Datos de soporte** — tickets abiertos, puntuación CSAT o NPS, escalaciones recientes
- **Datos de engagement** — fecha del último QBR, estado del patrocinador ejecutivo, nombre del campeón
- **Datos comerciales** — historial de pagos, conversaciones de expansión, puestos utilizados vs. licenciados
- **Cualquier riesgo conocido o cambio reciente** en la cuenta

## Marco de Puntuación

Puntúa cada dimensión de 1 a 5. Pondera según se muestra. Calcula el total ponderado sobre 100.

| Dimensión | Ponderación | Qué Puntuar |
|---|---|---|
| **Adopción del Producto** | 30% | Ratio DAU/MAU, amplitud de funcionalidades utilizadas, usuarios avanzados identificados |
| **Engagement** | 20% | Cadencia de QBR, patrocinador ejecutivo activo, fortaleza del campeón |
| **Resultados** | 20% | Cliente logrando sus objetivos declarados / métricas de éxito |
| **Salud del Soporte** | 15% | Tendencia en volumen de tickets, escalaciones sin resolver, CSAT |
| **Comercial** | 15% | Pagos a tiempo, puestos utilizados, señales de expansión |

**Conversión Puntuación → RAG:**
- 80–100: Verde (saludable, renovación probable)
- 60–79: Ámbar (en riesgo, requiere atención)
- 0–59: Rojo (alto riesgo de churn, escalar)

## Helper Programático

Este skill incluye un script Python que solo utiliza stdlib y aplica las ponderaciones anteriores y convierte el total ponderado a estado RAG — para que la puntuación titular se calcule idénticamente cada vez y las ponderaciones siempre sumen 100%.

```bash
# Cinco puntuaciones 1-5 en orden: adopción engagement resultados soporte comercial
python3 scripts/health_score.py --scores 4 3 4 2 5 --account "Acme Corp"

# O desde JSON (te permite sobrescribir las ponderaciones por defecto por cuenta/segmento)
python3 scripts/health_score.py --input account.json
```

Devuelve los puntos ponderados por dimensión, el **total sobre 100**, y la **banda RAG** (Verde ≥80, Ámbar 60–79, Rojo <60) con un siguiente paso de una línea. Ejecútalo para establecer el número titular, luego escribe el detalle de la dimensión y las acciones debajo. Añade `--json` para tooling aguas abajo.

## Formato de Salida

---

# Cuadro de Mando de Salud del Cliente: [Nombre de Cuenta]

**CSM:** [Nombre] | **Tier:** [Enterprise / Mid-Market / SMB]
**ARR:** £/$/€[X] | **Fecha de renovación:** [Fecha] | **Días hasta renovación:** [N]
**Salud general:** [Verde / Ámbar / Rojo] — [Puntuación]/100
**Última actualización:** [Fecha]

---

## Resumen de Puntuación de Salud

| Dimensión | Puntuación (1–5) | Ponderación | Puntuación Ponderada | Tendencia |
|---|---|---|---|---|
| Adopción del Producto | [1–5] | 30% | [X] | ↑ / → / ↓ |
| Engagement | [1–5] | 20% | [X] | ↑ / → / ↓ |
| Resultados | [1–5] | 20% | [X] | ↑ / → / ↓ |
| Salud del Soporte | [1–5] | 15% | [X] | ↑ / → / ↓ |
| Comercial | [1–5] | 15% | [X] | ↑ / → / ↓ |
| **Total** | — | 100% | **[X]/100** | |

---

## Detalle de Dimensión

### Adopción del Producto — [Puntuación]/5
- **Ratio DAU/MAU:** [X]% (benchmark: >25% = saludable)
- **Funcionalidades clave adoptadas:** [Lista funcionalidades en uso]
- **Funcionalidades no adoptadas:** [Lista funcionalidades de alto valor no utilizadas]
- **Usuarios avanzados identificados:** [Sí / No — cuántos]
- **Evaluación:** [1–2 frases sobre salud de adopción]

### Engagement — [Puntuación]/5
- **Último QBR:** [Fecha] — [Resumen de resultado]
- **Próximo QBR:** [Programado / Vencido]
- **Patrocinador ejecutivo:** [Activo / Pasivo / Vacante]
- **Campeón:** [Nombre, cargo, fortaleza: fuerte / moderada / débil]
- **Evaluación:** [1–2 frases]

### Resultados — [Puntuación]/5
- **Objetivos declarados del cliente:** [Lista 2–3 objetivos de la incorporación o último QBR]
- **Progreso contra objetivos:** [En camino / Parcial / Desviado]
- **Evidencia de valor:** [Métrica o cita que demuestre ROI]
- **Evaluación:** [1–2 frases]

### Salud del Soporte — [Puntuación]/5
- **Tickets abiertos:** [N] (desglose por prioridad: P1: X, P2: X, P3: X)
- **CSAT / NPS:** [Puntuación] (benchmark: >8 CSAT / >30 NPS = saludable)
- **Escalaciones sin resolver:** [Sí / No — detalles si aplica]
- **Tendencia de tickets (últimos 90 días):** Aumentando / Estable / Disminuyendo
- **Evaluación:** [1–2 frases]

### Comercial — [Puntuación]/5
- **Puestos licenciados:** [N] | **Puestos activos:** [N] ([X]% utilización)
- **Historial de pagos:** [A tiempo / Retraso — detalles]
- **Señales de expansión:** [Sí — describe / No]
- **Señales de degradación o cancelación:** [Sí — describe / No]
- **Evaluación:** [1–2 frases]

---

## Riesgos Principales

| Riesgo | Severidad | Mitigación |
|---|---|---|
| [Descripción del riesgo] | Alta / Media / Baja | [Acción específica para mitigar] |

---

## Acciones Recomendadas

**Inmediatas (esta semana):**
1. [Acción — propietario — fecha límite]

**Este mes:**
1. [Acción — propietario — fecha límite]

**Antes de renovación:**
1. [Acción — propietario — fecha límite]

---

## Pronóstico de Renovación

| Escenario | Probabilidad | ARR en riesgo |
|---|---|---|
| Renovación completa en ARR actual | [X]% | £/$/€0 |
| Renovación con contracción | [X]% | £/$/€[X] |
| Churn | [X]% | £/$/€[ARR completo] |

**Jugada de renovación recomendada:** [Expandir / Mantener / Salvar / Gestionar salida]

---

## Controles de Calidad

- [ ] La puntuación se basa en datos, no en intuición — cada dimensión tiene evidencia
- [ ] Los riesgos son específicos (no "bajo engagement" — algo como "el patrocinador ejecutivo se fue en marzo, sin reemplazo identificado")
- [ ] Las acciones tienen propietarios y fechas límite
- [ ] La probabilidad de renovación está calibrada contra la realidad del pipeline
- [ ] Las flechas de tendencia reflejan la dirección del cambio versus el último cuadro de mando, no solo el estado actual

## Anti-patrones

- [ ] No puntúes dimensiones de salud basándote en intuición — cada puntuación necesita evidencia de apoyo específica
- [ ] No des estado Verde a cuentas con problemas P1 sin resolver o hitos incumplidos
- [ ] No listes riesgos vagamente — "bajo engagement" sin especificidades no es accionable
- [ ] No dejes acciones recomendadas sin propietarios nombrados y fechas límite
- [ ] No confundas frecuencia de uso del producto con entrega de valor del producto
