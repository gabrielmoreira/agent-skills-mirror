---
# machine-translated to es from skills/competitor-teardown/SKILL.md — review: pending. Native fixes welcome via PR.
name: competitor-teardown
description: "Produce un análisis competitivo estructurado para cualquier producto o mercado. Úsalo cuando se te pida un análisis de competidores, desglose competitivo, comparación de mercado, SWOT, o mapa de posicionamiento. Genera un desglose estructurado con mapa de posicionamiento, comparación de características, brechas de mensajería y recomendaciones estratégicas. Para un documento de panorama completo con matriz de características y análisis de victorias/derrotas, usa competitive-analysis en su lugar."
---

# Skill de Desglose Competitivo

Este skill produce un documento de análisis competitivo completo — estructurado para usar en decks de estrategia, materiales para inversores, habilitación de ventas, o sesiones de planificación de producto.

## Entradas Requeridas

Solicita estos datos al usuario si no se proporcionan:
- **Tu producto** (nombre + descripción de una línea)
- **Competidores a analizar** (lista de 2–5 nombres; si no se proporciona, pregunta)
- **Profundidad del análisis** (descripción general rápida / desglose detallado)
- **Caso de uso principal para este análisis** (p. ej. habilitación de ventas, deck de inversores, estrategia interna, planificación de producto)

## Materiales Más Profundos

- **`references/intel-sourcing-guide.md`** — de dónde provienen los datos competitivos (cuatro niveles de fuentes), qué fuente usar por sección de desglose, las etiquetas de confianza [verificado]/[reportado]/[asumido], y la línea ética. Aplica su etiquetado a cada afirmación sustancial en la salida.
- **`templates/teardown-skeleton.md`** — un desglose relleno con las etiquetas de confianza y una cola de verificación integrada. Ofrécelo cuando el usuario quiera reunir la información por sí mismo.

## Estructura de Salida

### 1. Descripción General del Panorama Competitivo

Un párrafo que resuma la dinámica del mercado: quiénes son los actores clave, cómo está segmentado el mercado y dónde se encuentra el espacio en blanco. Mantenlo bajo 150 palabras — es el resumen ejecutivo.

### 2. Mapa de Posicionamiento

Describe un mapa de posicionamiento 2x2 en forma de texto (ya que no puedes renderizar imágenes):

- Define los dos ejes relevantes para este mercado (p. ej. "Facilidad de uso vs. Profundidad de características" o "Precio vs. Preparación empresarial")
- Coloca cada competidor en un cuadrante con una justificación de una oración
- Posiciona el producto del usuario e destaca la implicación estratégica

### 3. Tabla de Comparación de Características

| Característica / Capacidad | [Tu Producto] | [Competidor A] | [Competidor B] | [Competidor C] |
|---|---|---|---|---|
| [Característica] | ✅ / ❌ / 🟡 Parcial | | | |

Usa ✅ (la tiene), ❌ (no la tiene), 🟡 (parcial/limitada). Añade una columna "Notas Estratégicas" para características donde la diferencia es un punto de venta significativo o un riesgo.

Incluye 10–15 filas. Si el usuario no ha proporcionado detalles de características, nota qué celdas necesitan ser verificadas.

### 4. Análisis de Mensajería

Para cada competidor, analiza su mensajería orientada al público (titular del sitio web, eslogan, propuesta de valor principal):

**[Nombre del Competidor]**
- **Su afirmación principal:** [lo que dicen que hacen]
- **Señal de audiencia objetivo:** [a quién parecen estar dirigiéndose según lenguaje/imagen]
- **Gancho emocional:** [miedo / aspiración / autoridad / velocidad / simplicidad]
- **Brecha o debilidad en su mensajería:** [lo que no abordan que tu producto podría apropiar]

### 5. Resumen SWOT

Produce un SWOT limpio para el producto del usuario en el contexto de este panorama competitivo:

- **Fortalezas:** [2–3 diferenciadores genuinos]
- **Debilidades:** [2–3 brechas honestas o vulnerabilidades]
- **Oportunidades:** [2–3 brechas de mercado o debilidades de competidores para explotar]
- **Amenazas:** [2–3 movimientos de competidores o cambios de mercado a monitorear]

### 6. Recomendaciones Estratégicas

3–5 recomendaciones accionables basadas en el análisis. Enmarca cada una como: **"Dado [observación], [tu producto] debería [acción] para [resultado]."**

## Verificaciones de Calidad

- [ ] Los ejes en el mapa de posicionamiento son significativos y específicos para este mercado
- [ ] La tabla de características incluye notas estratégicas sobre diferenciadores clave
- [ ] El análisis de mensajería cubre todos los competidores nombrados
- [ ] El SWOT es honesto — Debilidades y Amenazas no deben ser suavizadas
- [ ] Las recomendaciones son específicas y accionables, no consejos de estrategia genérica

## Antipatrones

- [ ] No marques la presencia de características como equivalente entre competidores sin notar diferencias de calidad — ambos productos pueden tener "reporting" mientras que uno es significativamente mejor
- [ ] No posiciones el producto del usuario en el cuadrante más favorable sin justificación — un mapa de posicionamiento que se sirve a sí mismo e ignora la presión competitiva real no proporciona valor estratégico
- [ ] No suavices Debilidades o Amenazas en el SWOT — un SWOT que solo celebra fortalezas es un documento de marketing, no una herramienta de estrategia
- [ ] No incluyas afirmaciones no verificables sobre capacidades de competidores sin marcarlas como asunciones — presentar rumores como hechos daña la credibilidad analítica

## Frases Desencadenantes de Ejemplo

- "Haz un análisis de competidores de [Producto] vs [Competidor A] y [Competidor B]"
- "Desglosa el posicionamiento de [Competidor]"
- "Dame un panorama competitivo para [mercado]"
- "Construye un SWOT para nuestro producto contra [competidor]"
