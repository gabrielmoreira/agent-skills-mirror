---
# machine-translated to es from skills/rice-impact-matrix/SKILL.md — review: pending. Native fixes welcome via PR.
name: rice-impact-matrix
description: "Califica iniciativas usando tanto RICE como alineación estratégica para una priorización matizada. Úsalo cuando te pidan priorizar características, construir una matriz de prioridades, combinar puntuación cuantitativa con ajuste estratégico, o decidir qué construir después con múltiples iniciativas en competencia. Produce una matriz de prioridades calificada con puntuaciones RICE, calificaciones de alineación estratégica, ubicación en cuadrantes y recomendaciones de secuenciación."
---

# Habilidad RICE + Alineación Estratégica

Produce un resultado de priorización que equilibre la puntuación cuantitativa RICE con el ajuste estratégico cualitativo — porque la puntuación RICE más alta no siempre es la apuesta correcta siguiente.

## Entradas Requeridas

Pide al usuario estas entradas si no se proporcionan:
- **Lista de iniciativas o características a priorizar** (nombres y breves descripciones)
- **Prioridades estratégicas actuales u OKRs** (necesarias para calificar la alineación estratégica)
- **Estimaciones de Reach** (usuarios afectados por trimestre — incluso estimaciones aproximadas funcionan)
- **Estimaciones de Effort** (meses-persona — de ingeniería si está disponible)
- **Trimestre o período de planificación**

## Proceso de Dos Etapas

### Etapa 1: Puntuación RICE
- Reach: Usuarios afectados por trimestre
- Impact: Escala 3/2/1/0.5/0.25
- Confidence: 100% / 80% / 50%
- Effort: Meses-persona
- RICE = (R × I × C) / E

### Etapa 2: Puntuación de Alineación Estratégica
Califica cada iniciativa contra tus prioridades estratégicas actuales (proporcionadas como entrada):
- Apoya directamente el OKR principal: +3
- Apoya un OKR secundario: +2
- Neutral: +1
- Contradice la dirección estratégica: -1

### Puntuación de Prioridad Final
Puntuación Combinada = Puntuación RICE + (Alineación Estratégica × 10)

**Valida** — Marca cualquier iniciativa donde la puntuación RICE y la alineación estratégica entren en conflicto agudo (p. ej., RICE alto, alineación baja). Estas requieren una conversación explícita del equipo antes de la secuenciación.

## Estructura de Salida

### Matriz de Prioridades — [Trimestre]
| Iniciativa | Puntuación RICE | Alineación Estratégica | Puntuación Combinada | Cuadrante | Recomendación |
|------------|------------|--------------------|--------------------|----------|----------------|
| [nombre] | [puntuación] | [puntuación] | [combinada] | [Ahora/Siguiente/Después/Descartar] | [acción] |

#### Definiciones de Cuadrantes
- **Ahora:** RICE Alto + Alineación Estratégica Alta → Construir este trimestre
- **Siguiente:** RICE Alto + Alineación Inferior → Encolar para el próximo trimestre
- **Después:** RICE Inferior + Alineación Estratégica Alta → Revisar cuando haya capacidad
- **Descartar:** RICE Bajo + Alineación Baja → Eliminar del backlog

#### Recomendaciones
[Las 5 iniciativas principales con justificación para la secuenciación]

## Verificaciones de Calidad

- [ ] Todos los componentes RICE tienen una estimación (incluso si confianza baja — marca esos)
- [ ] La alineación estratégica se califica contra OKRs específicos, no contra "se siente estratégico" general
- [ ] Los conflictos entre rango RICE y alineación estratégica están explícitamente marcados
- [ ] Las recomendaciones de "Descartar" son específicas — no solo "prioridad baja, deprioritizar"
- [ ] Los niveles de confianza en estimaciones se notan donde son débiles (impulsa el indicador de confianza 50%)

## Anti-Patrones

- [ ] No trates la puntuación combinada como una clasificación definitiva — úsala para estructurar una conversación, no para reemplazar una
- [ ] No califiques la alineación estratégica como "alta" porque una iniciativa se siente importante sin mapearla a un OKR específico
- [ ] No coloques todas las iniciativas en el cuadrante "Ahora" — una matriz sin recomendaciones de "Descartar" no es creíble
- [ ] No ignores el indicador de conflicto cuando el rango RICE y la alineación estratégica divergen agudamente
- [ ] No aceptes confianza 100% en estimaciones que no hayan sido validadas con datos
