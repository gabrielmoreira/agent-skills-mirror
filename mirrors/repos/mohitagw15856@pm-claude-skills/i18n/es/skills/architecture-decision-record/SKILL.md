---
# machine-translated to es from skills/architecture-decision-record/SKILL.md — review: pending. Native fixes welcome via PR.
name: architecture-decision-record
description: "Crea un Registro de Decisiones de Arquitectura (ADR) para cualquier decisión técnica. Úsalo cuando te pidan documentar una decisión técnica, escribir un ADR, registrar una opción de arquitectura, o capturar por qué se seleccionó una tecnología o enfoque. Produce un ADR estructurado con contexto, decisión, consecuencias e intercambios."
---

# Habilidad de Registro de Decisiones de Arquitectura (ADR)

Esta habilidad produce un Registro de Decisiones de Arquitectura (ADR) completo siguiendo el formato Nygard — el estándar más ampliamente adoptado. Los ADR documentan el razonamiento detrás de decisiones técnicas significativas para que los miembros del equipo futuro entiendan no solo *qué* se decidió, sino *por qué*.

## Entradas Requeridas

Pide al usuario esto si no está proporcionado:
- **Número de ADR** (número secuencial en tu registro de ADR — p. ej. 012; o "próximo disponible" si no se conoce)
- **Título de la decisión** (breve, p. ej. "Usar PostgreSQL como almacenamiento de datos principal")
- **Contexto** (¿qué situación llevó a que esta decisión fuera necesaria?)
- **Opciones consideradas** (al menos 2; si solo se proporciona 1, solicita alternativas que fueron consideradas o descartadas)
- **Decisión tomada** (qué opción fue elegida)
- **Razón de la elección**
- **Estado** (Propuesto / Aceptado / Deprecado / Supersedido)
- **Autor y fecha**
- **Contexto del equipo** (opcional — tamaño del equipo, experiencia relevante, restricciones organizacionales; ayuda a calibrar la formalidad y profundidad de la sección de Contexto)

## Formato de Salida

---

# ADR-[NNN]: [Título de la Decisión]

**Fecha:** [AAAA-MM-DD]
**Estado:** [Propuesto / Aceptado / Deprecado / Supersedido por ADR-NNN]
**Autor(es):** [Nombre(s)]
**Decisores:** [Quién tuvo la palabra final — individuo o equipo]

---

## Contexto

[3–6 oraciones. Describe la situación, restricciones y fuerzas en juego que hicieron que esta decisión fuera necesaria. Incluye: el problema que se está resolviendo, estado relevante del sistema, restricciones del equipo, presiones de cronograma, o requisitos innegociables. Escribe como si explicaras a alguien que se une al equipo en 18 meses que no tiene contexto previo.]

**Restricciones clave:**
- [Restricción 1: p. ej. "Debe ser desplegable en las instalaciones para clientes empresariales"]
- [Restricción 2: p. ej. "El equipo no tiene experiencia previa con Go"]
- [Agrega tantas como sean relevantes]

---

## Opciones Consideradas

Para cada opción, produce:

### Opción [N]: [Nombre]

**Descripción:** [Qué es esta opción — 1–3 oraciones]

**Ventajas:**
- [Ventaja 1]
- [Ventaja 2]

**Desventajas:**
- [Desventaja 1]
- [Desventaja 2]

**Por qué fue descartada (si no fue elegida):** [Razón honesta]

---

## Decisión

**Usaremos [opción elegida].**

[2–4 oraciones explicando la decisión en lenguaje sencillo. Esto debería ser legible de forma aislada — alguien debería entender la decisión solo de este párrafo sin leer el documento completo.]

---

## Consecuencias

### Consecuencias Positivas
- [Qué esta decisión permite o mejora]
- [Qué riesgo mitiga]

### Consecuencias Negativas / Intercambios Aceptados
- [Qué estamos abandonando o asumiendo como resultado de esta decisión]
- [Deuda técnica o limitaciones introducidas]
- [Qué debe ser verdadero ahora para que esta decisión siga siendo válida]

### Riesgos
- [Qué podría hacer que esta decisión fuera incorrecta en retrospectiva]
- [Qué nos triggrearía a reconsiderar esta decisión]

---

## Notas de Implementación

[Incluye si la decisión tiene obstáculos de implementación no obvios, o si hay tickets/RFCs relacionados que los implementadores necesitarán. Omite solo si la decisión es puramente selección de herramientas sin ambigüedad de implementación.]

---

## Fecha de Revisión

[Incluye a menos que la decisión sea permanente o evidentemente final. Especifica una condición de trigger — p. ej. "Revisar si el equipo crece más allá de 20 ingenieros o el tráfico supera 10M solicitudes/día" — no solo "debería ser revisado periódicamente".]

---

## Verificaciones de Calidad

- [ ] El contexto explica el *por qué* — no solo el *qué*
- [ ] Al menos 2 opciones están documentadas (incluyendo las rechazadas)
- [ ] Las opciones rechazadas incluyen razones honestas de rechazo
- [ ] Las consecuencias incluyen consecuencias *negativas* — ninguna decisión está libre de consecuencias
- [ ] La decisión se expresa en lenguaje sencillo en la sección Decisión
- [ ] La sección Riesgos identifica qué invalidaría esta decisión
- [ ] La sección Contexto declara explícitamente el problema en sus primeras 1–2 oraciones (no asume que el lector sabe qué problema estaba resolviendo el equipo)
- [ ] La explicación de "Por qué fue descartada" de cada opción rechazada nombra una restricción específica o intercambio (no una declaración circular como "no cumplió con nuestros requisitos")

## Anti-Patrones

- [ ] No escribas un ADR después de que la decisión ya haya sido completamente implementada y el equipo haya avanzado — los ADR escritos retrospectivamente a menudo omiten las razones reales y alternativas
- [ ] No listes solo la opción elegida — las opciones rechazadas con razones honestas son la parte más valiosa de un ADR para lectores futuros
- [ ] No escribas consecuencias que sean todas positivas — cada decisión arquitectónica implica intercambios; un ADR sin consecuencias negativas no fue escrutinizado honestamente
- [ ] No dejes el estado como "Propuesto" indefinidamente — un ADR que nadie ha aprobado no está guiando las decisiones de nadie
- [ ] No escribas contexto que asuma que el lector ya sabe qué problema estaba siendo resuelto — la sección contexto existe precisamente para lectores que carecen de ese trasfondo

## Ejemplos de Uso
- "Escribe un ADR para usar [tecnología]"
- "Documenta nuestra decisión de [opción arquitectónica]"
- "Crea un registro de decisiones de arquitectura para [tema]"
- "Ayúdame a escribir por qué elegimos [opción] sobre [alternativa]"
