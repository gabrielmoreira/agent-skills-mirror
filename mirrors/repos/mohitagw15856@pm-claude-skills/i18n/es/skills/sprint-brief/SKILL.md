---
# machine-translated to es from skills/sprint-brief/SKILL.md — review: pending. Native fixes welcome via PR.
name: sprint-brief
description: "Genera un resumen de sprint estructurado a partir de datos y objetivos del sprint. Úsalo cuando te pidan escribir un resumen de sprint, crear un sumario de sprint, documentar objetivos y alcance del sprint, o producir una descripción de sprint dirigida al equipo. Produce un resumen escaneable con objetivo del sprint, justificación, trabajo agrupado, ruta crítica, riesgos y definición de terminado."
---

# Sprint Brief Skill

Produce un resumen de sprint claro y escaneable que cada miembro del equipo —ingeniero, diseñador, PM— pueda leer en menos de tres minutos y entienda exactamente qué estamos haciendo y por qué.

## Entradas Requeridas

Pídele al usuario lo siguiente si no lo proporciona:
- **Nombre y número del sprint**
- **Objetivo del sprint** (1-2 oraciones — marca si es demasiado vago)
- **Lista de tickets con responsables** (o una descripción del trabajo)
- **Dependencias o bloqueos conocidos**
- **Elementos trasladados del sprint anterior** (si los hay)

## Proceso
1. Lee el objetivo del sprint y verifica que sea específico y medible — marca si es demasiado vago
2. Agrupa los tickets por tema o área de funcionalidad
3. Identifica la ruta crítica — ¿cuáles tickets deben completarse para que se cumpla el objetivo del sprint?
4. Señala riesgos: tickets con criterios de aceptación poco claros, diseños faltantes, dependencias sin resolver
5. Anota elementos trasladados y si afectan el objetivo del sprint actual
6. **Valida** — Confirma que el objetivo del sprint es alcanzable dado el alcance de tickets y capacidad. Si solo los tickets de la ruta crítica llenarían el sprint, marca como sobrecargado.

## Estructura de Salida

### Resumen Sprint [Número] — [Fechas]
**Objetivo del Sprint:** [1-2 oraciones — específico y medible]
**Por Qué Este Sprint Importa:** [Conecta con el OKR trimestral en 2-3 oraciones]

**Lo Que Estamos Construyendo:**
- [Tema 1]: [tickets y responsables]
- [Tema 2]: [tickets y responsables]

**Ruta Crítica:** [Los 2-3 tickets de los que todo lo demás depende]

**Riesgos a Señalar:**
- [Riesgo 1 + mitigación]
- [Riesgo 2 + mitigación]

**Trasladado del Sprint Anterior:** [Lista + impacto en el objetivo actual]

**Definición de Terminado:** [Criterios específicos y acordados para el éxito del sprint]

## Verificaciones de Calidad

- [ ] El objetivo del sprint es específico enough para calificar aprobado/desaprobado al final del sprint
- [ ] Los tickets de ruta crítica están nombrados — no solo "los importantes"
- [ ] Cada riesgo tiene una mitigación u owner (no solo "esto es un riesgo")
- [ ] Los elementos trasladados están conectados a su impacto en el objetivo del sprint actual
- [ ] La Definición de Terminado son criterios acordados, no una lista de tareas

## Anti-Patrones

- [ ] No escribas un objetivo de sprint como una lista de tareas — el objetivo debe ser una declaración única enfocada en resultados que pueda calificarse aprobado/desaprobado
- [ ] No dejes sin nombrar la ruta crítica — "los tickets importantes" no es una ruta crítica
- [ ] No listes riesgos sin una mitigación u owner — un riesgo sin respuesta es solo una lista de preocupaciones
- [ ] No ignores el impacto de los elementos trasladados en la capacidad y objetivo de este sprint
- [ ] No escribas una Definición de Terminado que mezcle completitud de tareas con criterios de resultado — deben ser observables y acordados antes de que inicie el sprint
