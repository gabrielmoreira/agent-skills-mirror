---
# machine-translated to es from skills/cs-escalation-brief/SKILL.md — review: pending. Native fixes welcome via PR.
name: cs-escalation-brief
description: "Redacta un resumen de escalada estructurado para una cuenta de cliente en riesgo. Úsalo cuando una cuenta se haya escalado, cuando un cliente amenace con churn, cuando un problema P1 de un cliente necesite atención ejecutiva, o cuando se prepare un plan de retención interno. Produce un resumen de escalada nítido con contexto de cuenta, cronología, causa raíz, impacto comercial y un plan de resolución claro."
---

# Skill de Resumen de Escalada de Cliente

Produce un resumen de escalada claro y conciso que proporcione a los stakeholders internos —VP de CS, CCO, liderazgo de producto o el CEO— todo lo que necesitan para entender la situación, tomar decisiones y actuar rápidamente.

Un buen resumen de escalada no es una queja. Es un documento profesional que expone los hechos, asigna responsabilidad con honestidad y propone un plan de resolución específico.

## Inputs Requeridos

Solicita estos si no están ya disponibles:
- **Nombre de la cuenta**, tier y ARR
- **Nombre del CSM** y propietario de la cuenta
- **Naturaleza de la escalada** — qué pasó, qué dice el cliente
- **Cronología** de los eventos que llevaron a la escalada
- **Contacto del cliente** que escaló (nombre, cargo, nivel de influencia)
- **Qué quiere el cliente** — su solicitud explícita
- **Qué creemos que es la causa raíz**
- **Qué ya se ha hecho** para abordar la situación
- **Fecha de renovación** y evaluación actual del riesgo de renovación

## Niveles de Escalada

Calibra la urgencia y la audiencia según el nivel de escalada:

| Nivel | Disparador | Audiencia | Tiempo de respuesta |
|---|---|---|---|
| L1 — Riesgo de Cuenta | Cliente expresando insatisfacción; renovación en riesgo | CSM + CS Manager | 24 horas |
| L2 — Escalada Ejecutiva | Cliente escalado a su ejecutivo; solicitando implicación de ejecutivo del proveedor | VP CS + Account Exec | 4 horas |
| L3 — Riesgo de Churn | Cliente ha emitido noticia o está en conversación activa de churn | CCO / CEO + liderazgo de Revenue | 1 hora |
| L4 — Riesgo Público | Cliente amenazando escalada pública, legal o prensa | CCO / Legal / Comms | Inmediato |

## Formato de Output

---

# Resumen de Escalada: [Nombre de Cuenta]

**Nivel de escalada:** L[1/2/3/4] — [Etiqueta]
**Fecha de levantamiento:** [Fecha]
**Levantado por:** [nombre del CSM]
**Propietario de escalada:** [Nombre del ejecutivo o stakeholder senior ahora liderando la respuesta]

---

## Cuenta de un Vistazo

| Campo | Detalle |
|---|---|
| ARR | £/$/€[X] |
| Tier | Enterprise / Mid-Market / SMB |
| Cliente desde | [Fecha] |
| Fecha de renovación | [Fecha] — [N] días |
| Riesgo de renovación (pre-escalada) | Verde / Ámbar / Rojo |
| Riesgo de renovación (actual) | Verde / Ámbar / Rojo |
| Contacto del cliente que escaló | [Nombre, cargo, nivel de seniority] |
| Patrocinador ejecutivo (cliente) | [Nombre, cargo — activo / pasivo / vacante] |
| Patrocinador ejecutivo (proveedor) | [Nombre, cargo] |

---

## Qué Pasó — Resumen

[3–5 oraciones. Expón los hechos claramente. Qué experimentó el cliente, cómo reaccionó y cómo nos enteramos de la escalada. Sin editorializaciones. Sin culpas.]

---

## Cronología

Lista en orden cronológico. Cada entrada: `[Fecha / hora] — [Qué pasó. Quién hizo qué.]`

Incluye:
- Cuándo ocurrió el problema original o evento disparador
- Cuándo el cliente planteó preocupaciones por primera vez (informalmente)
- Cuándo escaló (escalada formal o implicación ejecutiva)
- Acciones tomadas desde la escalada

---

## Causa Raíz

**Causa principal:** [Una oración clara. Qué específicamente salió mal.]

**Factores contributivos:**
- [Factor 1 — sé honesto sobre fallos internos además de los externos]
- [Factor 2]

**¿Es esto un problema sistémico o aislado?**
[ ] Aislado a esta cuenta
[ ] Patrón visto en otras cuentas — detalles: [_______]
[ ] Brecha de producto o proceso que necesita arreglarse

---

## Posición Explícita del Cliente

**Qué dice el cliente que pasó:** [Su versión de los eventos — justa e sin filtros]

**Qué están pidiendo:** [Su solicitud explícita — compensación, corrección en fecha, llamada ejecutiva, crédito de SLA, cláusula de salida]

**Sentimiento del contacto que escaló:** [Frustrado pero constructivo / Enojado / Buscando salida / Desconocido]

**Riesgo de escalada pública:** Bajo / Medio / Alto — [evidencia si Medio o Alto]

---

## Impacto Comercial

| Tipo de impacto | Detalle |
|---|---|
| ARR en riesgo | £/$/€[X] |
| Probabilidad de churn potencial | [X]% |
| Riesgo reputacional | Bajo / Medio / Alto |
| Estado de referencia / case study | [Era una referencia — ahora en riesgo / No es una referencia] |
| Pipeline de expansión en riesgo | £/$/€[X] |

---

## Qué Se Ha Hecho Hasta Ahora

1. [Acción tomada — por quién — fecha — resultado]
2. [Acción tomada — por quién — fecha — resultado]
3. [Acción tomada — por quién — fecha — resultado]

**¿Se ha emitido una disculpa formal o reconocimiento?** Sí / No

---

## Plan de Resolución Propuesto

**Acciones inmediatas (próximas 24–48 horas):**

| Acción | Propietario | Para cuándo |
|---|---|---|
| [Acción] | [Nombre] | [Fecha] |
| [Acción] | [Nombre] | [Fecha] |

**Acciones a mediano plazo (próximas 2–4 semanas):**

| Acción | Propietario | Para cuándo |
|---|---|---|
| [Acción] | [Nombre] | [Fecha] |

**Qué NO estamos ofreciendo:** [Sé explícito sobre qué no está sobre la mesa — evita expectativas desalineadas]

**Criterios de éxito:** [¿Cómo sabremos que la escalada se ha resuelto? ¿Qué necesita confirmar el cliente para estar satisfecho?]

---

## Decisión Requerida del Propietario de Escalada

[Indica claramente qué decisión o recurso el propietario de escalada necesita proporcionar. Sé específico — no hagas que pregunten. P. ej.: "Necesitamos aprobación para ofrecer un crédito de servicio del 20% para Q2" o "Necesitamos una llamada ejecutiva con [nombre] dentro de 48 horas."]

---

## Plan de Comunicación

| Audiencia | Mensaje | Canal | Propietario | Para cuándo |
|---|---|---|---|---|
| Contacto del cliente que escaló | [Resumen del mensaje] | Email / Llamada | [Nombre] | [Fecha] |
| Patrocinador ejecutivo del cliente | [Resumen] | Llamada | [Nombre] | [Fecha] |
| Equipo interno de CS | [Resumen] | Slack / Reunión | CS Manager | [Fecha] |

---

## Verificaciones de Calidad

- [ ] La causa raíz es específica — no "falta de comunicación" o "brecha de producto" sin detalle
- [ ] La posición del cliente está enunciada justamente — no minimizada ni desestimada
- [ ] Se solicita una decisión clara del propietario de escalada — el resumen no termina con "¿qué piensas?"
- [ ] El ARR en riesgo está cuantificado
- [ ] El plan de comunicación tiene propietarios y fechas — no "TBD"
- [ ] El lenguaje es profesional y sin culpa hacia individuos

## Anti-Patrones

- [ ] No asignes culpa a individuos — enfócate en fallos sistémicos y brechas de proceso
- [ ] No minimices el ARR en riesgo ni describas el riesgo de churn vagamente sin un número
- [ ] No dejes la propiedad del plan de resolución como "TBD" o sin asignar
- [ ] No escribas el resumen sin una solicitud clara del propietario de escalada
- [ ] No omitas la posición propia del cliente — su perspectiva debe estar representada justamente
