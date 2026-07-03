---
# machine-translated to es from skills/go-to-market/SKILL.md — review: pending. Native fixes welcome via PR.
name: go-to-market
description: "Crea activos de entrada al mercado para cualquier producto o feature. Úsalo cuando te pidan un plan GTM, positioning statement, plan de lanzamiento de producto, pillares de mensajería, casos de uso, o lista de características/beneficios. Produce un pack GTM completo: positioning statement, pillares de mensajería, mapeo de características a beneficios, y casos de uso específicos por rol. Para un plan de lanzamiento por fases con coordinación entre equipos, usa go-to-market-planner en su lugar."
---

# Skill Go-To-Market

Este skill produce un pack completo de activos de entrada al mercado para un producto, feature o iniciativa. Sigue el framework de posicionamiento de Geoffrey Moore y estructura todos los outputs para su uso en decks de ventas, landing pages, emails de lanzamiento y documentos de alineación interna.

## Trabajar a partir de un brief

Frecuentemente recibirás un brief corto sin todos los detalles. **Siempre entrega el pack GTM completo de todas formas** — no te detengas para hacer preguntas y no dejes placeholders entre corchetes como `[AGREGAR PROOF POINT]` o `[Capacidad técnica]`. Cuando falte un detalle (diferenciadores, proof points, features), infiere unos específicos y realistas a partir de la descripción del producto y el cliente objetivo, y marca cualquier cosa inferida como *(asumido — confirmar)*. Una suposición concreta y etiquetada siempre es mejor que un espacio en blanco.

## Inputs (infiere cualquiera no proporcionado — etiqueta asunciones)

- **Nombre del producto/feature**
- **Descripción de una línea** (qué hace, técnicamente)
- **Cliente objetivo** (rol, tamaño de empresa, industria si es relevante)
- **Problema principal que resuelve**
- **Competidor clave o alternativa** (qué hacen hoy sin esto)
- **Top 3 diferenciadores**

## Lee desde / Escribe hacia el Brain

Si existe un [`professional-brain`](../professional-brain/SKILL.md) (`brain/`), úsalo antes de preguntar:

- **Lee primero:** `context.md` (producto, ICP, voz), `knowledge/market.md` y `knowledge/strategy.md`, y el matching `entities/` del feature que se lanza.
- **Escribe después:** guarda el plan de lanzamiento en `entities/`, y cualquier decisión de posicionamiento o canal en `decisions/`, cada uno etiquetado con provenance.

## Estructura del Output

Siempre produce las cuatro secciones de abajo en orden.

---

### 1. Positioning Statement

Usa el formato de Geoffrey Moore exactamente:

> Para **[cliente objetivo]** que **[tiene este problema o necesidad]**, **[Nombre del Producto]** es una **[categoría de producto]** que **[beneficio clave/resultado]**. A diferencia de **[alternativa principal o competidor]**, nuestro producto **[diferenciador clave]**.

Escribe un positioning statement principal, luego ofrece una versión tagline más corta (10 palabras o menos) apta para un titular hero.

---

### 2. Pillares de Mensajería

Genera 3–5 pillares de mensajería. Cada pilar debe incluir:

- **Nombre del pilar** (2–4 palabras, negrita)
- **Resumen de una oración** de lo que este pilar afirma
- **2–3 proof points** (específicos y respaldados por evidencia; si no se proporcionó dato, infiere un proof point realista y etiquétalo *(asumido)* — nunca dejes un placeholder vacío)
- **Ejemplo de uso en copy** (una oración como aparecería en una landing page o deck)

Los pillares deben ser distintos — evita solapamiento. Cada pilar debe ser defendible contra el competidor principal.

---

### 3. Lista de Features & Funcionalidades

Produce una tabla de dos columnas:

| Feature / Funcionalidad | Beneficio para el Comprador (qué significa para el usuario) |
|---|---|
| [Capacidad técnica] | [Resultado en lenguaje simple — comienza con un verbo: "Reduce...", "Permite...", "Elimina..."] |

Reglas:
- Nunca listes un feature sin un beneficio correspondiente
- Los beneficios deben referenciar el workflow o pain point del cliente objetivo
- Apunta a 6–12 filas; si solo se dieron 1–2 features, infiere el resto de forma plausible a partir de la descripción del producto
- Evita jerga en la columna de beneficios — escribe como si explicaras a un comprador, no a un ingeniero

---

### 4. Casos de Uso

Genera 3–5 casos de uso específicos por rol. Cada caso de uso debe seguir este formato:

**Caso de Uso [N]: [Rol] — [Título del Escenario]**

- **Quién:** [Título del puesto / rol]
- **Situación:** [El momento específico o trigger que los lleva a usar el producto]
- **Antes:** [Lo que tenían que hacer sin este producto — sé específico sobre tiempo, fricción o riesgo]
- **Con [Nombre del Producto]:** [Lo que hacen ahora — acción concreta, no beneficio vago]
- **Resultado:** [Resultado medible o tangible]

Los casos de uso deben cubrir diferentes buyer personas si es posible (p. ej. usuario final, manager, admin).

---

## Quality Checks

Antes de entregar el output, verifica:
- [ ] El positioning statement sigue el formato Moore exactamente
- [ ] El tagline tiene 10 palabras o menos
- [ ] Cada pilar tiene al menos 2 proof points (o placeholders etiquetados)
- [ ] Cada feature tiene un beneficio — sin features huérfanos
- [ ] Los beneficios comienzan con verbos de acción
- [ ] Los casos de uso incluyen estructura Antes/Después
- [ ] El lenguaje es consistente con el vocabulario del cliente objetivo (sin términos internos de ingeniería)

## Anti-Patterns

- [ ] No escribas descripciones de features en lugar de beneficios — el pack GTM debe traducir features en valor para el cliente
- [ ] No uses el mismo mensaje para todas las buyer personas — cada rol tiene diferentes prioridades y lenguaje
- [ ] No crees un positioning statement que podría aplicarse a cualquier competidor — la diferenciación debe ser específica y defendible
- [ ] No omitas la sección "no es para" — definir quién no es el objetivo afila el posicionamiento y previene esfuerzo de ventas desorientado
- [ ] No listes casos de uso sin vincularlos a títulos de puesto específicos o roles de comprador

## Frases Trigger de Ejemplo

- "Crea un positioning statement para [producto]"
- "Escribe un plan GTM para [feature]"
- "Dame los pillares clave para [nombre de producto]"
- "Construye una lista de features y casos de uso para [producto]"
- "Estamos lanzando [X] — ayúdame con la mensajería"
