---
# machine-translated to es from skills/assumption-mapper/SKILL.md — review: pending. Native fixes welcome via PR.
name: assumption-mapper
description: "Extrae y clasifica por riesgo las suposiciones ocultas en un brief de producto o PRD. Úsalo cuando te pidan revisar un brief de producto para identificar suposiciones, auditar un PRD para detectar riesgos, encontrar suposiciones ocultas, validar planes de producto o ejecutar un análisis de suposiciones. Produce un mapa de suposiciones priorizado con puntuaciones de confianza e impacto, métodos de validación recomendados e indicadores de suposiciones críticas."
---

# Skill Assumption Mapper

Identifica y prioriza las suposiciones sin probar incrustadas en cualquier plan de producto antes de que comience el desarrollo.

## Datos Necesarios

Pide al usuario estos datos si no los proporciona:
- **Brief de producto, PRD o descripción de concepto** (incluso notas aproximadas funcionan)
- **Fase** (concepto / descubrimiento / previo a construcción / post-lanzamiento — afecta cuáles suposiciones importan más)

## Proceso
1. Lee el brief, PRD o descripción de concepto proporcionado
2. Extrae suposiciones en cuatro categorías:
   - **Deseabilidad** (¿lo quieren los usuarios?)
   - **Viabilidad técnica** (¿podemos construirlo?)
   - **Viabilidad comercial** (¿será sostenible para el negocio?)
   - **Usabilidad** (¿pueden los usuarios usarlo realmente?)
3. Puntúa cada suposición:
   - Confianza (1-5): ¿Qué tan seguros estamos de que esto es verdad?
   - Impacto (1-5): ¿Cuán mal falla el plan si esta suposición es incorrecta?
   - Prioridad = Impacto − Confianza (mayor = probar primero)
4. **Valida completitud** — Asegúrate de que haya al menos una suposición por categoría. Si una categoría está vacía, relee el brief buscando específicamente ese tipo de suposición.
5. Proporciona una lista ordenada con métodos de validación recomendados

## Estructura de Salida

### Mapa de Suposiciones: [Nombre de Característica/Producto]

| Suposición | Categoría | Confianza | Impacto | Prioridad | Método de Validación |
|-----------|-----------|-----------|---------|-----------|----------------------|
| [suposición] | [tipo] | [1-5] | [1-5] | [puntuación] | [método] |

#### Suposiciones Críticas (Impacto 4+ y Confianza 2 o inferior)
[Elementos marcados con recomendaciones de validación detalladas]

#### Top 3 Suposiciones a Validar Primero
[Recomendaciones detalladas incluyendo método de investigación específico, esfuerzo estimado y qué resultado cambiaría]

## Ejemplo (Parcial)

Entrada: *"Estamos construyendo un flujo de onboarding de autoservicio para reducir el tiempo hasta valor para clientes PYME."*

| Suposición | Categoría | Confianza | Impacto | Prioridad | Método de Validación |
|-----------|-----------|-----------|---------|-----------|----------------------|
| Los usuarios PYME pueden completar el onboarding sin ayuda humana | Usabilidad | 2 | 5 | 3 | Prueba de usabilidad no moderada (n=8) |
| El onboarding más rápido se correlaciona con mayor retención | Viabilidad comercial | 3 | 4 | 1 | Análisis de cohortes de tiempos de onboarding actuales vs. retención a 90 días |
| El onboarding actual es la razón principal de la lentitud en el tiempo hasta valor | Deseabilidad | 2 | 4 | 2 | Entrevistas con usuarios de cuentas PYME que abandonaron recientemente |

## Antipatrones

- [ ] No surfaces solo suposiciones de deseabilidad — las suposiciones de viabilidad técnica y comercial pueden acabar con un producto con igual probabilidad y a menudo se pasan por alto
- [ ] No asignes alta confianza a una suposición simplemente porque no ha sido cuestionada — la ausencia de evidencia no es evidencia
- [ ] No recomiendes "entrevistas con usuarios" como método de validación para cada suposición — algunas suposiciones requieren datos cuantitativos, análisis competitivo o spikes técnicos
- [ ] No listes suposiciones que no puedan ser probadas — cada suposición en el mapa debe tener un método de validación plausible, o debe ser marcada como desconocible y tratada como un riesgo

## Comprobaciones de Calidad

- [ ] Al menos una suposición por categoría (Deseabilidad, Viabilidad Técnica, Viabilidad Comercial, Usabilidad)
- [ ] Todas las suposiciones con Impacto 4+ / Confianza 2− marcadas como CRÍTICAS
- [ ] Cada método de validación es específico (no solo "hacer investigación" — nombra el método y tamaño de muestra)
- [ ] Puntuaciones de prioridad son consistentes (Impacto − Confianza, mayor = más urgente)
