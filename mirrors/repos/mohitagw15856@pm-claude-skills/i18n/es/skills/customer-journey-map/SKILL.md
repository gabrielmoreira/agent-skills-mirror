---
# machine-translated to es from skills/customer-journey-map/SKILL.md — review: pending. Native fixes welcome via PR.
name: customer-journey-map
description: "Construye un mapa de viaje del cliente para un producto, servicio o experiencia. Úsalo cuando se te pida mapear un viaje del cliente, crear un viaje del usuario, documentar touchpoints y puntos de fricción, o diseñar un mapa de experiencia. Produce un mapa de viaje completo con etapas, touchpoints, emociones, puntos de fricción y oportunidades priorizadas."
---

# Habilidad de Mapa de Viaje del Cliente

Esta habilidad produce un mapa completo del viaje del cliente que cubre cada etapa desde el conocimiento hasta la recomendación. Cada etapa incluye touchpoints, acciones del cliente, emociones, puntos de fricción y oportunidades específicas de mejora. El resultado está listo para usar en descubrimiento de producto, diseño UX o talleres de alineación multifuncional.

## Inputs Requeridos

Pregunta al usuario por esto si no está proporcionado:
- **Producto o servicio** a mapear
- **Persona del cliente** — ¿para qué segmento de cliente es este mapa? (sé específico — una persona por mapa)
- **Alcance del viaje** — completo de extremo a extremo (conocimiento → recomendación), ¿o una fase específica? (p. ej. solo onboarding?)
- **¿Estado actual o estado futuro?** — ¿mapear cómo funciona hoy, o diseñar cómo debería funcionar?
- **Fuentes de datos** — ¿hay investigación, entrevistas con usuarios, tickets de soporte, comentarios NPS, análisis disponibles?
- **Objetivo del mapa** — ¿qué decisión informará esto? (rediseño, priorización, alineación de stakeholders, nueva característica)

## Estructura de Salida

---

# Mapa de Viaje del Cliente: [Producto / Servicio]

**Persona:** [Nombre — p. ej. "Sarah, la gerente de RRHH abrumada"]
**Alcance del viaje:** [Completo de extremo a extremo / Onboarding / Compra / Renovación]
**Estado actual o futuro:** [Estado actual / Estado futuro deseado]
**Preparado por:** [Nombre / Equipo]
**Fecha:** [Fecha]
**Basado en:** [Fuentes de investigación — entrevistas, análisis, datos de soporte, asumido/hipotético]

---

## Resumen de Persona

| | |
|---|---|
| **Nombre** | [Sarah] |
| **Rol** | [Gerente de RRHH en una firma de servicios profesionales de 200 personas] |
| **Objetivo** | [Reducir el tiempo dedicado a la gestión manual de datos de empleados] |
| **Frustraciones** | [Demasiadas herramientas que no se comunican entre sí; siempre persiguiendo aprobaciones] |
| **Comodidad tecnológica** | [Moderada — cómoda con herramientas SaaS pero no una usuaria avanzada] |
| **Poder de decisión** | [Recomienda herramientas; presupuesto aprobado por CHRO] |

---

## Descripción General del Viaje

```
CONOCIMIENTO → CONSIDERACIÓN → DECISIÓN → ONBOARDING → ADOPCIÓN → RECOMENDACIÓN
   [Etapa 1]      [Etapa 2]      [Etapa 3]    [Etapa 4]     [Etapa 5]   [Etapa 6]
```

**Calificación general de la experiencia (estado actual):** [😤 Frustrante / 😐 Neutral / 😊 Positivo]

---

## Etapa 1: Conocimiento

*¿Cómo descubre el cliente por primera vez que el producto existe?*

**Objetivo del cliente en esta etapa:** [p. ej. Darse cuenta de que tienen un problema que vale la pena resolver — o encontrar una solución a un dolor específico]

| Elemento | Detalle |
|---|---|
| **Disparador** | [¿Qué evento los hace empezar a buscar? — p. ej. El proceso manual se rompe / recomendación de pares / vieron un anuncio] |
| **Dónde están** | [Búsqueda en Google / LinkedIn / conferencia / conversación con un colega / boletín de correo] |
| **Qué hacen** | [p. ej. Buscan "automatizar onboarding de empleados" / pregunta a colegas en comunidad de RRHH / hace clic en anuncio de LinkedIn] |
| **Emoción** | [😤 Frustrado — abrumado por procesos manuales y esperanzado en encontrar una forma mejor] |
| **Puntos de fricción** | [Cantidad abrumadora de opciones / difícil saber qué herramientas son creíbles / no se puede distinguir B2B vs B2C desde la página principal] |
| **Oportunidades** | [Contenido SEO que apunta a la palabra clave del disparador / liderazgo de pensamiento en LinkedIn / presencia en comunidades de pares] |

---

## Etapa 2: Consideración

*El cliente está evaluando activamente opciones. ¿Qué hace para decidir?*

| Elemento | Detalle |
|---|---|
| **Objetivo del cliente** | [Reducir de muchas opciones a una lista corta de 2–3] |
| **Qué hacen** | [Lee reseñas en G2/Capterra / ve video de demostración / descarga guía de comparación / pregunta a colegas que usan algo similar] |
| **Touchpoints** | [Sitio web / sitios de reseñas / prueba social / flujo de solicitud de demostración / correo electrónico de ventas] |
| **Emoción** | [😕 Ansioso — preocupado por tomar la decisión equivocada; compras de herramientas anteriores no han entregado] |
| **Puntos de fricción** | [Precios no visibles en el sitio web / la demostración requiere una llamada antes de ver el producto / no está claro si funciona con su stack existente] |
| **Oportunidades** | [Demo de autoservicio o tour de producto interactivo / página de precios transparentes / calculadora de ROI / casos de estudio de tamaño de empresa similar] |

---

## Etapa 3: Decisión

*El cliente está listo para comprar — o no. ¿Qué los hace comprometerse?*

| Elemento | Detalle |
|---|---|
| **Objetivo del cliente** | [Obtener la aprobación del CHRO y justificar la decisión con un caso de negocio] |
| **Qué hacen** | [Reserva una llamada de ventas / solicita cuestionario de seguridad / construye caso de negocio interno / negocia contrato] |
| **Touchpoints** | [AE / llamada de ventas / revisión de seguridad / contrato / proceso de adquisición] |
| **Emoción** | [😬 Cauteloso — no quiere equivocarse; presentar a liderazgo añade presión] |
| **Puntos de fricción** | [El proceso de ventas es lento / el cuestionario de seguridad toma semanas / los términos del contrato son no estándar y requieren asesor legal] |
| **Oportunidades** | [FAQ de seguridad de autoservicio / contrato estándar con términos predecibles / kit de champion (diapositivas, plantilla de caso de negocio) para ayudarlos a vender internamente] |

---

## Etapa 4: Onboarding

*El cliente ha comprado. Ahora necesita obtener valor rápidamente.*

| Elemento | Detalle |
|---|---|
| **Objetivo del cliente** | [Que el producto funcione y mostrar al CHRO que fue una buena decisión] |
| **Qué hacen** | [Recibe correo de bienvenida / asiste a llamada de kickoff / configura integraciones / invita al equipo] |
| **Touchpoints** | [Secuencia de correos de onboarding / lista de verificación de onboarding en el producto / CSM / centro de ayuda / marketplace de integraciones] |
| **Emoción** | [😬 Ansioso pero esperanzado — emocionado por el potencial pero estresado por el trabajo de configuración] |
| **Puntos de fricción** | [La configuración es más compleja de lo esperado / TI requerido para SSO pero TI es lento para responder / el onboarding genérico no coincide con su caso de uso] |
| **Oportunidades** | [Rutas de onboarding específicas por rol / conector de TI con plantilla de solicitud pre-rellenada / correo de victoria rápida en el día 3 (muéstrales una cosa que ya funciona)] |

**Momento crítico:** [¿Qué momento único en esta etapa determina si se convertirán en un usuario activo o desaparecerán? — p. ej. "La primera vez que el producto les ahorra 30 minutos en una tarea que solían hacer manualmente"]

---

## Etapa 5: Adopción

*El cliente está usando el producto. ¿Están obteniendo valor consistente?*

| Elemento | Detalle |
|---|---|
| **Objetivo del cliente** | [Hacer del producto una parte regular de su flujo de trabajo; demostrar ROI al liderazgo] |
| **Qué hacen** | [Usa características principales diariamente / descubre nuevas características / golpea una limitación / contacta a soporte / asiste a webinar] |
| **Touchpoints** | [UI del producto / notificaciones en la aplicación / correo electrónico / soporte / comunidad / gestor de éxito del cliente] |
| **Emoción** | [Variable — algunos días 😊 cuando el producto funciona bien; algunos días 😤 cuando hay una brecha o error] |
| **Puntos de fricción** | [Falta una característica que esperaban / los reportes no muestran la métrica que quiere el liderazgo / las características avanzadas son demasiado complejas / sienten que están subutilizando lo que pagan] |
| **Oportunidades** | [Check-in proactivo del CSM en el día 30 / descubrimiento de características en el producto / dashboard de uso para que el cliente vea su propio ROI / comunidad para aprendizaje entre pares] |

**Indicadores de salud de adopción:**
- [Ratio DAU/MAU — ¿cómo se ve la salud?]
- [Característica X usada por Y% de puestos dentro de Z semanas]
- [Primera encuesta NPS en 60 días — puntuación objetivo]

---

## Etapa 6: Recomendación

*El cliente adora el producto. ¿Cómo lo conviertes en un motor de referidos?*

| Elemento | Detalle |
|---|---|
| **Objetivo del cliente** | [Resolver problemas más rápido; sentirse como un experto; sentirse valorado como cliente] |
| **Qué hacen** | [Refiere a un colega / escribe una reseña en G2 / participa en caso de estudio / habla en un evento / se convierte en usuario avanzado / se une a la comunidad] |
| **Touchpoints** | [CSM / comunidad / correo de solicitud de reseña / programa de referidos / divulgación de caso de estudio / patrocinio de conferencia] |
| **Emoción** | [😊 Orgulloso — la herramienta es parte de su identidad profesional; se sienten inteligentes por haberla elegido] |
| **Puntos de fricción** | [El programa de referidos es engorroso / no hay forma estructurada de conectar con colegas / el proceso de caso de estudio es lento y requiere esfuerzo de su parte] |
| **Oportunidades** | [Solicitud de reseña en G2 de un clic en un momento de alta satisfacción / comunidad de pares / programa de referidos con recompensa significativa / proceso de caso de estudio que hace la mayor parte del trabajo para ellos] |

---

## Curva de Emoción

Traza la experiencia emocional del cliente a lo largo del viaje:

```
Alto  😊 │        *                              *          *
          │                                   *
Neutral 😐│  *         *
          │                  *
Bajo  😤 │                        *    *
          └────────────────────────────────────────────────────
            Conocer  Considerar  Decidir  Incorporar  Adoptar  Recomendar
```

**Punto más bajo:** [¿Qué etapa tiene la peor experiencia — y por qué?]
**Punto más alto:** [¿Cuándo está el cliente más encantado — qué lo impulsó?]
**Caída más grande:** [¿Dónde cae el sentimiento más bruscamente — esta es generalmente la mayor oportunidad]

---

## Oportunidades Priorizadas

| Oportunidad | Etapa | Impacto en el cliente | Esfuerzo para arreglar | Prioridad |
|---|---|---|---|---|
| [Tour de producto de autoservicio antes de la llamada de ventas] | Consideración | [Alto — elimina la barrera de compra principal] | [Medio] | P1 |
| [Correo de victoria rápida en el día 3] | Onboarding | [Alto — construye hábito temprano] | [Bajo] | P1 |
| [Plantilla de configuración de SSO de TI] | Onboarding | [Medio — elimina bloqueador específico] | [Bajo] | P2 |
| [Check-in proactivo del CSM en el día 30] | Adopción | [Medio — detecta señales de churn temprano] | [Medio] | P2 |
| [Programa de referidos entre pares] | Recomendación | [Alto para crecimiento — reduce CAC] | [Alto] | P3 |

---

## Lo Que No Sabemos (Brechas de Investigación)

| Brecha | Cómo cerrarla | Prioridad |
|---|---|---|
| [¿Qué dispara realmente la decisión de empezar a buscar?] | [5 entrevistas JTBD con compradores recientes] | [Alto] |
| [¿Qué causa que los clientes se estanquen en el onboarding?] | [Análisis de caída en el embudo de onboarding + 3 entrevistas con clientes que hicieron churn] | [Alto] |
| [¿Qué % de clientes han llegado a la etapa de recomendación?] | [Análisis de producto — identificar usuarios avanzados; NPS por cohorte] | [Medio] |

---

## Verificaciones de Calidad

- [ ] El mapa cubre una persona específica — no "todos los clientes"
- [ ] Cada etapa incluye el estado emocional del cliente — no solo acciones
- [ ] Los puntos de fricción son el dolor del cliente — no el dolor de la empresa
- [ ] Las oportunidades son lo suficientemente específicas para convertirse en elementos de backlog o prompts de diseño
- [ ] La curva de emoción muestra la experiencia real — no una versión aspiracionalmente positiva
- [ ] Las brechas de investigación están documentadas — el mapa refleja lo que se sabe, no lo asumido

## Anti-patrones

- [ ] No construyas el mapa solo a partir de suposiciones — fundamenta al menos los puntos de fricción en datos o investigación real del cliente
- [ ] No trates todas las etapas del viaje como igualmente ponderadas — identifica explícitamente los momentos de mayor fricción
- [ ] No omitas la capa emocional — un mapa de viaje sin emociones es un flujo de proceso, no un mapa de cliente
- [ ] No crees touchpoints genéricos que se apliquen a cualquier producto — cada touchpoint debe ser específico para este producto y cliente
- [ ] No dejes oportunidades sin clasificar — prioriza por impacto y viabilidad

## Ejemplos de Frases Disparadoras

- "Mapea el viaje del cliente para [producto]"
- "Construye un viaje del usuario desde el conocimiento hasta la recomendación"
- "Crea un mapa de viaje para nuestra experiencia de onboarding"
- "Mapea los touchpoints y puntos de fricción para [tipo de cliente]"
- "Diseña un mapa de experiencia para [proceso o producto]"
