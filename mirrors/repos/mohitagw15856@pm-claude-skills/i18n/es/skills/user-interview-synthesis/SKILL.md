---
# machine-translated to es from skills/user-interview-synthesis/SKILL.md — review: pending. Native fixes welcome via PR.
name: user-interview-synthesis
description: "Sintetiza transcripciones de entrevistas con usuarios en hallazgos de investigación estructurados. Utiliza cuando se te pida analizar notas de entrevistas, sintetizar investigación cualitativa, identificar temas en entrevistas o convertir datos brutos de entrevistas en insights accionables para el producto. Produce una síntesis temática con citas de apoyo por tema, implicaciones 'y qué significa esto', y pasos recomendados. Para fuentes mixtas más allá de entrevistas (encuestas, tickets, feedback) utiliza user-research-synthesis en su lugar."
---

# Habilidad de Síntesis de Entrevistas con Usuarios

Transforma transcripciones de entrevistas brutes en un documento de síntesis estructurado que destaque temas, puntos de dolor e insights accionables.

## Inputs Requeridos

Solicita al usuario estos datos si no están disponibles:
- **Transcripciones o notas de entrevistas** (incluso notas aproximadas sirven)
- **Número de participantes y sus perfiles** (rol, tamaño de empresa, contexto)
- **Preguntas de investigación** (¿qué pretendía responder el estudio?)
- **Rango de fechas** de la investigación (para contexto)

## Proceso
1. Lee todas las transcripciones proporcionadas en su totalidad antes de extraer conclusiones
2. Identifica temas recurrentes (mínimo 3 menciones para calificar como tema)
3. Categoriza hallazgos en: Puntos de Dolor, Insights de Flujo de Trabajo, Solicitudes de Features, Momentos de Satisfacción
4. Selecciona 2-3 citas textuales por tema que mejor representen el patrón
5. Redacta implicaciones "y qué significa esto" para cada tema — ¿qué significa esto para el producto?
6. **Valida** — Confirma que cada tema tiene citas de al menos 3 participantes. Marca como baja confianza cualquier insight basado en menos participantes.

## Estructura del Output

### Síntesis de Investigación: [Nombre del Estudio]
**Participantes:** [n]
**Rango de Fechas:** [fechas]
**Preguntas de Investigación:** [lista]

#### Tema 1: [Nombre del Tema]
- Resumen (2-3 oraciones)
- Citas de apoyo (de al menos 3 participantes)
- Implicación para el producto

[Repite para cada tema]

#### Señales de Baja Confianza (1-2 participantes solamente)
[Hallazgos que vale la pena monitorear pero aún no actuar — nota qué investigación adicional confirmaría o negaría]

#### Pasos Recomendados
[Recomendaciones específicas y accionables basadas en hallazgos]

## Controles de Calidad

- [ ] Cada tema está respaldado por citas de al menos 3 participantes
- [ ] Las implicaciones conectan con decisiones específicas de producto, no solo observaciones
- [ ] Verificación de sesgos del investigador: sin lenguaje tendencioso, hallazgos no todos favorecen una hipótesis
- [ ] Las señales de fuente única están marcadas por separado, no mezcladas en temas principales
- [ ] Cada pregunta de investigación del brief del estudio está respondida (incluso si la respuesta es "inconclusivo")

## Anti-Patrones

- [ ] No mezcles señales de fuente única en temas principales — insights citados por solo un participante deben estar marcados por separado
- [ ] No escribas implicaciones que sean solo observaciones reformuladas en lugar de decisiones de producto habilitadas
- [ ] No incluyas temas que solo apoyen la hipótesis del proyecto — hallazgos contradictorios deben ser expuestos, no omitidos
- [ ] No presentes hallazgos sin citas — cada tema requiere evidencia textual de al menos 3 participantes
- [ ] No dejes preguntas de investigación sin responder — cada pregunta del brief del estudio debe ser explícitamente respondida, incluso si la respuesta es inconclusiva
