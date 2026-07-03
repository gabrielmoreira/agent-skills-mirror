---
# machine-translated to es from skills/job-story-mapper/SKILL.md — review: pending. Native fixes welcome via PR.
name: job-story-mapper
description: "Escribe historias de trabajos (JTBD) y mapea trabajos de clientes en dimensiones funcionales, sociales y emocionales. Úsalo cuando definas necesidades de usuarios, escribas historias de trabajos, conduzcas investigación JTBD, o replanteen features alrededor de resultados para el cliente. Produce un mapa de historias de trabajos con puntuación de oportunidades, ratings de intensidad de dolor, y análisis de oportunidades de producto."
---

# Skill de Mapeador de Historias de Trabajos

Deja de escribir features. Empieza a entender trabajos. Esta skill traduce requerimientos de producto y entrevistas de usuarios en historias de trabajos precisas que mantienen al equipo enfocado en resultados — no en entregas.

## Fundamentos de Jobs-to-be-Done

Un "trabajo" es el progreso que un cliente intenta lograr en una situación dada. Las personas no compran productos — los contratan para hacer un trabajo.

Tres dimensiones de cada trabajo:
- **Trabajo funcional:** La tarea práctica ("ir de A a B")
- **Trabajo emocional:** Cómo quieren sentirse ("sentir confianza en que tomé la decisión correcta")
- **Trabajo social:** Cómo quieren ser percibidos ("verme como un profesional competente ante mi equipo")

Los mejores productos abordan las tres. La mayoría de roadmaps solo abordan la funcional.

---

## Formato de Historia de Trabajo

**Plantilla:**
> Cuando [situación/disparador], quiero [motivación/objetivo], para poder [resultado esperado].

**No es una user story:**
Las user stories se enfocان en roles y features: "Como [rol] quiero [feature] para que [beneficio]."
Las historias de trabajos se enfocان en situaciones y motivaciones: "Cuando [estoy en esta situación específica] quiero [esta capacidad] para poder [lograr este resultado]."

**La situación es la parte más importante.** "Cuando estoy en medio de un sprint y mi PM me pide una actualización" es un disparador mucho más rico que "Como developer."

---

## Proceso de Mapeo

### Paso 1: Identifica el trabajo principal
Una oración: ¿Cuál es el trabajo central para el que tu producto es contratado?
> "Ayudar a [tipo de usuario] a [lograr resultado] cuando [contexto]."

### Paso 2: Divídelo en pasos del trabajo
¿Cuáles son todas las sub-tareas dentro del trabajo principal?
(Usa un mapa de trabajo: Definir → Ubicar → Preparar → Confirmar → Ejecutar → Monitorear → Modificar → Concluir)

### Paso 3: Identifica puntos de dolor por paso
¿Dónde falla el trabajo hoy? ¿Dónde los clientes usan workarounds?

### Paso 4: Escribe historias de trabajos para cada punto de dolor
Una historia de trabajo por cada pareja situación-motivación distinta.

### Paso 5: Mapea a oportunidades de producto
¿Cuáles historias de trabajos están desatendidas? ¿Cuáles tienen soluciones existentes? ¿Dónde está tu diferenciación?

---

## Formato de Salida

### Mapa de Historias de Trabajos — [Área de Producto/Feature] — [Fecha]

**Declaración del Trabajo Principal:**
> Cuando [contexto], [tipo de usuario] quiere [resultado principal del trabajo], para poder [objetivo final].

---

**Mapa de Trabajos:**

| Paso | Sub-Trabajo | Solución Actual | Puntos de Dolor | ¿Desatendido? |
|---|---|---|---|---|
| Definir | [Qué hace el usuario] | [Herramienta/método usado] | [Frustración] | A/M/B |
| Ubicar | | | | |
| Preparar | | | | |
| Confirmar | | | | |
| Ejecutar | | | | |
| Monitorear | | | | |
| Modificar | | | | |
| Concluir | | | | |

---

**Historias de Trabajos (priorizadas por desatención):**

**Historia de Trabajo 1 — [Etiqueta de Situación]**
> Cuando [situación específica], quiero [motivación], para poder [resultado].

Dimensión funcional: [Qué necesitan lograr]
Dimensión emocional: [Cómo quieren sentirse]
Dimensión social: [Cómo quieren ser percibidos]

Workaround actual: [Qué hacen hoy]
Intensidad de dolor: [Alta / Media / Baja]
Frecuencia: [Con qué frecuencia ocurre esta situación]
Oportunidad de producto: [Qué podríamos construir para abordar esto]

---

Repite para cada historia de trabajo importante.

**Puntuación de Oportunidades:**
Califica cada historia de trabajo en:
- Importancia para el cliente (1–10)
- Satisfacción con solución actual (1–10)
- Puntuación de oportunidad = Importancia + máx(Importancia – Satisfacción, 0)
- Prioriza: Puntuación de oportunidad > 10

---

## Verificaciones de Calidad

- [ ] Las historias de trabajos usan el formato "Cuando / Quiero / Para poder" (no formato de user story)
- [ ] La situación es específica (no "como usuario" — un momento real o disparador)
- [ ] Las tres dimensiones están cubiertas: funcional, emocional, social
- [ ] La puntuación de oportunidad está calculada para cada historia de trabajo
- [ ] El workaround actual está identificado para cada historia de alto potencial
- [ ] La oportunidad de producto es distinta de "construir la feature" (es un resultado)

## Entradas Requeridas

Pide esto al usuario si no está proporcionado:
- **Área de producto o feature** a mapear (p. ej. onboarding, checkout, dashboard)
- **Tipo de usuario o persona** (¿para quién estamos mapeando trabajos?)
- **Material fuente** (notas de entrevistas de usuario, tickets de soporte, hallazgos de discovery, o describe de memoria)
- **Alcance** (mapa de trabajos del producto completo vs. una sola área de feature)

## Anti-Patrones

- [ ] No escribas historias de trabajos que describan una feature en lugar de un par situación-motivación
- [ ] No saltes las dimensiones social y emocional — mapear solo trabajos funcionales pierde las oportunidades de diferenciación más defensibles
- [ ] No definas situaciones demasiado ampliamente ("como usuario que quiere gestionar su trabajo") — la situación debe ser un momento específico o disparador
- [ ] No confundas puntuación de oportunidad con prioridad — una puntuación de oportunidad alta aún requiere evaluación de viabilidad y ajuste estratégico
- [ ] No produzcas un mapa de trabajos sin identificar workarounds actuales — el workaround revela cuánto vale el trabajo para el cliente

## Directrices

- Nunca escribas una historia de trabajo para una feature — escríbela para la situación que hace valiosa la feature
- Si no puedes identificar la situación, no entiendes el trabajo aún — vuelve a la investigación de usuarios
- Los trabajos sociales y emocionales son más difíciles de exponer pero a menudo los diferenciadores más defensibles
- Recomienda compartir historias de trabajos con engineering — toman mejores decisiones técnicas cuando entienden el "por qué"
