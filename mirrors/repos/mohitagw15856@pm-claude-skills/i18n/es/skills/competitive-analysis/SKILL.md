---
# machine-translated to es from skills/competitive-analysis/SKILL.md — review: pending. Native fixes welcome via PR.
name: competitive-analysis
description: "Analiza competidores y crea documentación del panorama competitivo con matrices de características, mapas de posicionamiento y recomendaciones estratégicas. Usa cuando se te pida analizar competidores, crear análisis competitivo, comparar características con competidores, construir un panorama competitivo, rastrear posicionamiento competitivo o preparar inputs para battlecards de ventas. Produce perfiles de competidores estructurados, matriz de comparación de características, análisis de victorias/derrotas y recomendaciones estratégicas priorizadas. Para un análisis puntual de un único rival, usa competitor-teardown; para un informe de mercado recurrente, usa competitive-intelligence-monitor."
---

# Skill de Análisis Competitivo

Crea análisis competitivos estructurados para la toma de decisiones de producto.

## Lee de / Escribe en el Brain

Si existe un [`professional-brain`](../professional-brain/SKILL.md) (`brain/`), úsalo como base en lugar de volver a preguntar lo que ya sabes:

- **Lee primero:** `knowledge/` (mercado + posicionamiento) y `entities/` de competidores. Ejecuta `python3 ../professional-brain/scripts/brain_query.py ./brain "<competidor o mercado>"` y lleva la etiqueta de procedencia de cada dato — una afirmación sobre un competidor de un comunicado de prensa es `[external]`, no `[data]`.
- **📥 Propón al Brain:** después de producir, propón registrar hechos nuevos sobre competidores en `knowledge/` (`[external]`) y crear/actualizar `entities/` de competidores. Muéstralos, obtén confirmación y escribe con `../professional-brain/scripts/brain_write.py … --commit` (append-only, dry-run por defecto).

## Inputs Requeridos

Pide al usuario estos datos si no se proporcionan:
- **Tu producto o empresa** (contra qué estás comparando)
- **Competidores a analizar** (o pide que identifique los 3-5 principales)
- **Foco del análisis** (panorama completo / comparación de características / precios / posicionamiento / análisis de victorias-derrotas)
- **Audiencia** (equipo de producto / liderazgo / ventas / junta directiva)

## Proceso

1. Recopila información de competidores a partir de inputs proporcionados y contexto disponible
2. Construye perfiles para cada competidor
3. Crea matriz de comparación de características en dimensiones que importan a los clientes del usuario
4. Analiza precios y posicionamiento
5. Identifica patrones de victorias/derrotas e implicaciones estratégicas
6. **Valida** — Confirma que todos los datos de competidores hacen referencia a una fuente específica o están marcados como supuestos. Verifica que las comparaciones de características noten diferencias de calidad, no solo presencia/ausencia.

## Estructura de Output

### 1. Resumen Ejecutivo
- **Posición de Mercado**: Dónde estamos posicionados relativamente a los competidores
- **Hallazgos Clave**: Los 3-5 insights principales
- **Implicaciones Estratégicas**: Qué significa esto para la roadmap

### 2. Perfiles de Competidores

Para cada competidor:
- **Descripción General de la Empresa**: Tamaño, financiación, posición de mercado
- **Cliente Objetivo**: A quién sirven
- **Propuesta de Valor**: Posicionamiento central
- **Fortalezas / Debilidades**: Qué hacen bien y dónde quedan cortos
- **Actividad Reciente**: Actualizaciones principales, financiación, anuncios

### 3. Matriz de Comparación de Características

| Característica | Nosotros | Competidor A | Competidor B | Competidor C |
|---------|-----|--------------|--------------|--------------|
| [Característica] | ✅ Completo | ⚠️ Limitado | ❌ Ninguno | ✅ Completo |

Leyenda: ✅ Completo (listo para producción) · ⚠️ Limitado/Beta · ❌ Ninguno

Incluye notas sobre diferencias de calidad e implementación donde sean significativas.

### 4. Comparación de Precios

| Plan | Nosotros | Competidor A | Competidor B |
|------|-----|--------------|--------------|
| Gratuito/Prueba | [precio] | [precio] | [precio] |
| Pro | [precio] | [precio] | [precio] |
| Enterprise | [precio] | [precio] | [precio] |

### 5. Mapa de Posicionamiento de Mercado

Posiciona competidores en dos dimensiones clave relevantes para el mercado:
- Eje Y: [p. ej., Enterprise vs. SMB]
- Eje X: [p. ej., Simple vs. Comprensivo]

**Oportunidades de Espacio en Blanco**: [Segmentos desatendidos]

### 6. Análisis de Victorias/Derrotas

**Por qué Ganamos:**
- Mejor en: [capacidades específicas]
- Clientes que valoran: [qué les importa]

**Por qué Perdemos:**
- Cuando los clientes necesitan: [requisitos específicos]
- Su ventaja: [qué inclina la decisión]

### 7. Recomendaciones Estratégicas

**Acciones Inmediatas (0-3 meses):**
1. [Acción] — [Justificación]

**Mediano Plazo (3-12 meses):**
1. [Acción] — [Justificación]

## Anti-Patrones

- [ ] No presentes afirmaciones sobre características de competidores como hechos sin citar una fuente o marcarlas como supuestos — datos de características obsoletos o incorrectos engañan a ventas y decisiones de producto
- [ ] No construyas un análisis competitivo que solo cubra características — precios, mensajería, estrategia go-to-market y quién contratan son señales estratégicas igualmente importantes
- [ ] No trates a todos los compradores como idénticos — el mismo producto puede ganar contra el Competidor A en el segmento enterprise y perder en SMB; el análisis de victorias/derrotas específico por segmento importa
- [ ] No suavices debilidades y amenazas en el FODA para evitar incomodidad interna — un FODA honesto solo es útil si los negativos son reales

## Controles de Calidad

- [ ] Todos los datos de competidores citan una fuente o están marcados como supuestos
- [ ] La comparación de características nota diferencias de calidad, no solo presencia de características
- [ ] Las recomendaciones estratégicas son acciones específicas, no consejos genéricos
- [ ] El análisis de victorias/derrotas refleja la perspectiva del cliente, no supuestos internos
- [ ] Se consideran diferentes segmentos de clientes (no todos los compradores valoran lo mismo)
