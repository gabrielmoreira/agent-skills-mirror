---
# machine-translated to es from skills/feature-prioritisation/SKILL.md — review: pending. Native fixes welcome via PR.
name: feature-prioritisation
description: "Aplicar marcos de priorización (RICE, MoSCoW, Kano, ICE, Opportunity Scoring) para clasificar características y elementos de backlog. Usar cuando se solicite priorizar características, clasificar un backlog, decidir qué construir a continuación, o evaluar compensaciones entre ideas en competencia. Produce una lista de características clasificada y puntuada con tablas específicas del marco, orden de construcción recomendado, elementos depriorizados, y supuestos realizados."
---

# Skill de Priorización de Características

Aplicar el marco de priorización correcto a cualquier backlog y producir una clasificación clara y defendible con justificación — no solo una lista ordenada.

## Entradas Requeridas

Solicitar al usuario estos datos si no se proporcionan:
- **Lista de características o iniciativas a priorizar**
- **Objetivo o métrica** siendo priorizada (OKR, lanzamiento, sprint)
- **Marco preferido** (o recomendar basado en contexto más abajo)
- **Datos del equipo**: estimaciones de alcance, estimaciones de esfuerzo, velocidad (para RICE)

## Guía de Selección de Marco

Preguntar al usuario qué marco prefiere, o recomendar basado en contexto:

| Situación | Marco Recomendado |
|---|---|
| Necesitar una puntuación rápida basada en datos | RICE |
| Reunión de alineación de stakeholders | MoSCoW |
| Entender deleite del cliente vs expectativas | Kano |
| Startup en fase temprana, decisiones rápidas | ICE |
| Identificar necesidades de clientes infraservidas | Opportunity Scoring |
| Decisiones estratégicas de cartera | Matriz de Valor vs Esfuerzo |

---

## Puntuación RICE

**Fórmula:** (Alcance × Impacto × Confianza) ÷ Esfuerzo

| Factor | Definición | Escala |
|---|---|---|
| Alcance | Usuarios impactados por trimestre | Número real |
| Impacto | Efecto en el objetivo por usuario | 0.25 / 0.5 / 1 / 2 / 3 |
| Confianza | Qué tan seguro estás? | 50% / 80% / 100% |
| Esfuerzo | Personas-mes requeridos | Número real |

Tabla de salida:
| Característica | Alcance | Impacto | Confianza | Esfuerzo | Puntuación RICE | Prioridad |
|---|---|---|---|---|---|---|

---

## Método MoSCoW

Categorizar cada característica como:
- **Must Have** — no negociable para lanzamiento/sprint; el producto falla sin ella
- **Should Have** — importante pero no crítica; existen soluciones alternativas
- **Could Have** — agradable de tener; incluir solo si hay tiempo
- **Won't Have (this time)** — explícitamente fuera de alcance ahora; puede revisitarse

Siempre preguntar: "Must have para *qué*?" — definir el alcance (lanzamiento, sprint, trimestre) antes de categorizar.

---

## Puntuación ICE (Startup/modo rápido)

**Fórmula:** Impacto + Confianza + Facilidad (cada una 1–10)

Rápido, subjetivo — bueno para decisiones tempranas antes de que existan datos.

---

## Modelo Kano

Clasificar características en:
- **Basic (Must-be):** Esperado; la ausencia causa insatisfacción
- **Performance:** Más = mejor satisfacción; relación lineal
- **Excitement (Delighters):** Inesperado; crea deleite; la ausencia es neutral
- **Indifferent:** A los usuarios no les importa de una forma u otra
- **Reverse:** Algunos usuarios lo quieren, otros no

Recomendar construir: todas las características Basic primero → características Performance para casos de uso clave → 1–2 características Excitement por release.

---

## Helper Programático

Este skill incluye un script Python que solo usa stdlib y que calcula la clasificación para los marcos basados en matemáticas (RICE, ICE) para que la puntuación de características sea consistente entre sesiones.

```bash
# RICE desde JSON
python3 scripts/feature_prioritisation.py initiatives.json --framework rice

# RICE desde CSV
python3 scripts/feature_prioritisation.py initiatives.csv --framework rice --format csv

# ICE desde JSON
python3 scripts/feature_prioritisation.py features.json --framework ice

# Pasar mediante pipe
printf '%s\n' '[{"name":"API refactor","impact":8,"confidence":80,"ease":5}]' \
  | python3 scripts/feature_prioritisation.py --framework ice -
```

Usar `--json` para producir salida legible por máquina para herramientas posteriores.

---

## Formato de Salida

### Priorización de Características — [Producto/Equipo] — [Fecha]

**Marco Utilizado:** [RICE / MoSCoW / ICE / Kano / Personalizado]
**Alcance:** [Sprint / Trimestre / Release]
**Objetivo siendo priorizado:** [Métrica u objetivo]

[Tabla puntuada usando marco seleccionado]

**Orden de Construcción Recomendado:**
1. [Característica] — [justificación de 1 línea]
2. [Característica] — [justificación de 1 línea]
3. ...

**Explícitamente Depriorizadas:**
- [Característica] — Razón: [breve]

**Supuestos Realizados:**
- [Cualquier estimación o juicio usado en la puntuación]

---

## Directrices

- Siempre anclar la priorización a un objetivo o métrica específica — nunca priorizar en el vacío
- Señalar cuando dos características tienen puntuaciones similares pero perfiles de riesgo muy diferentes
- Si la política de stakeholders está influenciando la priorización, nombrarla explícitamente y sugerir separar la puntuación del marco de la decisión final
- Recomendar revisitar prioridades cada 2 semanas como mínimo
- Nunca producir una lista clasificada de una sola columna sin justificación — explicar las 3 decisiones superiores e inferiores

## Verificaciones de Calidad

- [ ] Cada elemento se puntúa contra el mismo objetivo o métrica (no diferentes objetivos por elemento)
- [ ] Los elementos depriorizados se enumeran explícitamente con razones (no solo ausentes de la lista clasificada)
- [ ] Los supuestos usados en la puntuación están documentados
- [ ] La política de stakeholders o preferencias personales se separan de la puntuación del marco
- [ ] La priorización está anclada a un alcance específico (sprint / trimestre / lanzamiento)

## Anti-Patrones

- [ ] No puntuaizar elementos contra diferentes objetivos — cada elemento en una sesión de priorización debe puntuarse contra el mismo objetivo
- [ ] No omitir elementos depriorizados — enumerar explícitamente qué se eliminó y por qué es tan importante como la lista clasificada
- [ ] No dejar que la política de stakeholders anule las puntuaciones del marco sin documentar el override y la razón
- [ ] No mezclar puntuaciones RICE, ICE, o MoSCoW entre marcos en una sola sesión — elegir un marco por ejercicio de priorización
- [ ] No tratar la salida como final sin documentar los supuestos usados en la puntuación — los supuestos cambian, y la lista debe ser revisitable
