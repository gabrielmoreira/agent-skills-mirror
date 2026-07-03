---
# machine-translated to es from skills/meeting-notes/SKILL.md — review: pending. Native fixes welcome via PR.
name: meeting-notes
description: "Estructura y formatea notas de reunión siguiendo mejores prácticas de PM. Úsalo cuando te pidan crear notas de reunión, formatear notas de discusión, capturar elementos de acción, o documentar decisiones de cualquier tipo de reunión. Produce notas estructuradas con decisiones, elementos de acción (propietario + plazo), preguntas abiertas y próximos pasos."
---

# Skill de Notas de Reunión

Esta skill estructura notas de reunión para maximizar su valor y asegurar el seguimiento.

## Inputs Requeridos

Pregunta al usuario por estos datos si no los proporciona:
- **Título de la reunión y fecha**
- **Asistentes** (nombres y roles)
- **Notas sin procesar o transcripción** (pega notas de discusión, una transcripción, o describe lo que se discutió)
- **Tipo de reunión** (1:1 / planificación de sprint / revisión de producto / sincronización con stakeholders / otro) — determina qué plantilla usar

## Lee desde / Escribe en el Brain

Si existe un [`professional-brain`](../professional-brain/SKILL.md) (`brain/`), aquí es donde las notas se convierten en memoria durable:

- **Lee primero:** los archivos relevantes de `stakeholders/` (para llegar sabiendo las solicitudes y preocupaciones abiertas de cada asistente) y cualquier `decisions/` que la reunión revise.
- **Escribe después:** añade cada **decisión** (con su justificación y un `reopen-when`) a `decisions/`, agrega nuevas **solicitudes/preocupaciones** al archivo `stakeholders/` correcto, e identifica cualquier nueva **suposición** en `hypotheses/`. Etiqueta cada hecho capturado con su provenance — la mayoría de afirmaciones de reunión son `[verbal]` hasta que se confirmen independientemente. Guarda las notas sin procesar en `source/`.

## Plantilla Estándar de Notas de Reunión

### Encabezado de la Reunión
**Reunión**: [Título de la Reunión]  
**Fecha**: [Fecha]  
**Asistentes**: [Nombres/Roles]  
**Tomador de Notas**: [Nombre]  
**Duración**: [Duración real]

### Agenda
- [ ] Tema 1
- [ ] Tema 2
- [ ] Tema 3

*(Marca los elementos a medida que se discutan)*

### Decisiones Tomadas
Documentación clara de las decisiones:

**Decisión**: [Qué se decidió]  
**Contexto**: [Por qué se tomó esta decisión]  
**Propietario**: [Quién es responsable de ejecutarla]  
**Plazo**: [Cuándo, si aplica]  

Usa este formato para cada decisión tomada.

### Elementos de Acción
Todos los elementos de acción deben ser:
- [ ] **[Elemento de acción]** - @Propietario - Vence: [Fecha]
- [ ] **[Elemento de acción]** - @Propietario - Vence: [Fecha]

Formato:
- Acción clara y específica
- Un solo propietario (sin propiedad de "equipo")
- Plazo concreto
- Casilla de verificación para seguimiento

### Notas de Discusión
Puntos clave discutidos organizados por tema:

**Tema 1: [Nombre]**
- Punto clave o destaque de la discusión
- Contexto importante o preocupación planteada
- Cualquier dato o información compartida

**Tema 2: [Nombre]**
- Puntos clave de la discusión
- Decisiones o conclusiones alcanzadas

### Preguntas Abiertas / Seguimiento
Preguntas que no pudieron ser respondidas:
- **Pregunta**: [Qué necesitamos saber]
- **Propietario**: [Quién lo investigará]
- **Para Cuándo**: [Plazo]

### Próximos Pasos
Resumen claro de lo que sucede a continuación:
1. [Acción inmediata siguiente]
2. [Reunión de seguimiento si es necesaria]
3. [Cualquier proceso más amplio a iniciar]

## Mejores Prácticas

**Durante la reunión:**
- Enfócate en decisiones y elementos de acción más que en el diálogo
- Captura compromisos específicos, no discusiones generales
- Anota opiniones disidentes sobre decisiones importantes
- Pide claridad sobre compromisos vagos ("Investigaré" → "Analizaré los datos y compartiré hallazgos el viernes")

**Después de la reunión:**
- Envía notas dentro de 2 horas mientras estén frescas
- Etiqueta a los propietarios de elementos de acción (@menciónalos)
- Incluye enlaces a documentos relevantes
- Realiza seguimiento de elementos de acción vencidos

**Qué capturar:**
✅ Decisiones tomadas
✅ Elementos de acción con propietarios y plazos
✅ Puntos clave de la discusión
✅ Preguntas abiertas
✅ Próximos pasos

**Qué omitir:**
❌ Transcripciones verbatim
❌ Tangentes fuera de tema
❌ Discusión preliminar antes de decisiones
❌ Información redundante

## Tipos de Reunión y Adaptaciones

### Reuniones 1:1
Enfoque en:
- Discusiones de desarrollo de carrera
- Retroalimentación (ambas direcciones)
- Desafíos actuales
- Elementos de acción para ambas partes

Adiciones a la plantilla:
- **Logros Recientes**: Qué está yendo bien
- **Desafíos**: Qué no está yendo bien
- **Discusión de Carrera**: Temas de desarrollo
- **Retroalimentación**: Para ambas partes

### Planificación de Sprint
Enfoque en:
- Criterios de aceptación de historias
- Decisiones de estimación/dimensionamiento
- Identificación de dependencias
- Compromiso del sprint

Adiciones a la plantilla:
- **Objetivo del Sprint**: Qué nos comprometemos a entregar
- **Puntos de Historia**: Capacidad y estimaciones
- **Dependencias**: Bloqueadores externos
- **Definición de Hecho**: Criterios de aceptación

### Revisiones de Producto
Enfoque en:
- Decisiones de diseño
- Retroalimentación de usuarios discutida
- Cambios solicitados
- Evaluación de preparación para lanzamiento

Adiciones a la plantilla:
- **Decisiones de Diseño**: Qué se aprobó/rechazó
- **Retroalimentación de Usuarios**: Insights clave discutidos
- **Preguntas de Diseño Abiertas**: Qué necesita iteración
- **Criterios de Lanzamiento**: Requisitos pendientes

### Sincronización con Stakeholders
Enfoque en:
- Actualizaciones de estado entregadas
- Preocupaciones planteadas
- Aprobaciones otorgadas
- Necesidades de escalada

Adiciones a la plantilla:
- **Descripción General del Estado**: Progreso de alto nivel
- **Aprobaciones Obtenidas**: Sign-offs recibidos
- **Escaladas**: Problemas planteados a stakeholders
- **Próxima Sincronización**: Cuándo y qué cubrir

## Ejemplo de Notas de Reunión

```
# Revisión de Roadmap de Producto - Q1 2026
**Fecha**: 20 de enero de 2026  
**Asistentes**: Sarah (CPO), Mike (Líder de Ing), Jennifer (Diseño), Tom (PM)  
**Tomador de Notas**: Tom  
**Duración**: 45 minutos

## Agenda
- [x] Revisar features planeadas para Q1
- [x] Discutir restricciones de recursos
- [x] Discusión de priorización
- [x] Alineación de cronograma

## Decisiones Tomadas

**Decisión**: Mover dashboard multicanal a Q2, priorizar mejoras de app móvil para Q1  
**Contexto**: La retroalimentación de clientes muestra que la experiencia móvil está impactando significativamente la retención (65% de usuarios principalmente móviles). El equipo de ingeniería solo puede abordar una iniciativa mayor este trimestre.  
**Propietario**: Tom (PM) para comunicar a stakeholders  
**Plazo**: 22 de enero

**Decisión**: Asignar 20% del tiempo de ingeniería a deuda técnica  
**Contexto**: La deuda técnica acumulada está ralentizando el desarrollo de features. La velocidad del equipo bajó 30% el trimestre pasado.  
**Propietario**: Mike (Líder de Ing) para crear backlog de deuda técnica  
**Plazo**: 27 de enero

**Decisión**: Ejecutar beta móvil con 100 usuarios antes del lanzamiento completo
**Contexto**: Necesitamos validar mejoras en dispositivos diversos
**Propietario**: Jennifer (Diseño) para coordinar con QA
**Plazo**: 10 de febrero

## Elementos de Acción
- [ ] **Actualizar deck del roadmap Q1 con nueva priorización** - @Tom - Vence: 22 de enero
- [ ] **Programar reunión de alineación con equipo de soporte sobre retraso del dashboard** - @Tom - Vence: 24 de enero
- [ ] **Crear rubric de priorización de deuda técnica** - @Mike - Vence: 27 de enero
- [ ] **Ejecutar user testing en diseños móviles** - @Jennifer - Vence: 3 de febrero
- [ ] **Documentar justificación de decisión para ejecutivos** - @Sarah - Vence: 23 de enero
- [ ] **Identificar 100 usuarios para beta móvil** - @Tom - Vence: 1 de febrero

## Notas de Discusión

**Priorización de Features Q1**
- La retención de clientes es la prioridad #1 de la empresa este trimestre
- NPS de app móvil es 6.2 (vs 8.1 en web)
- Móvil representa 65% de usuarios activos diarios
- Dashboard multicanal tomaría 8 semanas de ingeniería
- Mejoras móviles estimadas en 6 semanas de ingeniería con ROI más alto
- Ventas tiene 3 deals empresariales esperando feature de dashboard

**Restricciones de Recursos**
- Actualmente 4 ingenieros disponibles (bajó de 6 el trimestre pasado por attrición)
- Equipo de diseño puede soportar ambas iniciativas pero con capacidad reducida
- Equipo de QA necesita 2 semanas para testing exhaustivo en móvil
- Un ingeniero prestado al equipo de seguridad hasta febrero

**Discusión de Riesgos**
- Retrasar dashboard puede impactar ventas empresariales (3 deals esperando)
- Sarah señaló: "Podemos posicionar mejoras móviles como fundación para features empresariales"
- Mike planteó preocupación sobre estabilidad del stack tecnológico móvil — abordado mediante asignación de deuda técnica
- Necesitamos comunicar claramente con Ventas sobre cambio de cronograma

**Plan de Implementación Móvil**
- Semana 1-2: Refinamientos de diseño basados en retroalimentación de usuarios
- Semana 3-4: Implementación de ingeniería
- Semana 5: Testing interno
- Semana 6: Beta con 100 usuarios
- Semana 7: Lanzamiento completo

## Preguntas Abiertas
- **Pregunta**: ¿Cuál es el impacto en pipeline empresarial si retrasamos el dashboard?  
  **Propietario**: Sarah verificará con liderazgo de Ventas  
  **Para Cuándo**: 23 de enero

- **Pregunta**: ¿Podemos hacer una beta limitada del dashboard para clientes empresariales?  
  **Propietario**: Tom explorará alcance de MVP con Mike  
  **Para Cuándo**: 25 de enero

- **Pregunta**: ¿Cuál es nuestro plan si las mejoras móviles no alcanzan métricas objetivo?
  **Propietario**: Tom creará plan de contingencia
  **Para Cuándo**: 27 de enero

## Próximos Pasos
1. Tom enviar roadmap actualizado a liderazgo antes de fin de miércoles (22 de enero)
2. Equipo comenzar planificación de sprint para mejoras móviles el próximo lunes (27 de enero)
3. Reunión de seguimiento el 1 de febrero para revisar progreso y validar priorización
4. Sarah presentar justificación de decisión a equipo ejecutivo el 24 de enero

---

**Próxima Reunión**: 1 de febrero de 2026 - Revisión de Progreso
**Notas Enviadas**: 20 de enero de 2026 5:30 PM
```

## Controles de Calidad

- [ ] Cada elemento de acción tiene un propietario único nombrado (no "equipo")
- [ ] Cada elemento de acción tiene un plazo concreto
- [ ] Las decisiones incluyen contexto (por qué se tomó la decisión)
- [ ] Las preguntas abiertas tienen un propietario y un "para cuándo"
- [ ] Sin transcripciones verbatim — solo síntesis

## Anti-Patrones

- [ ] No asignes elementos de acción a "el equipo" o "todos" — cada elemento de acción debe tener exactamente un propietario nombrado o no se completará
- [ ] No captures contenido de transcripción verbatim — las notas de reunión registran decisiones y compromisos, no la ruta conversacional completa para llegar allí
- [ ] No omitas el contexto de las decisiones — una decisión sin su justificación es inútil cuando alguien pregunta "¿por qué hicimos esto?" seis meses después
- [ ] No dejes preguntas abiertas sin un propietario y plazo — una pregunta sin respuesta sin seguimiento asignado es una decisión bloqueada
- [ ] No retrases el envío de notas más allá de 2 horas después de la reunión — las notas enviadas al día siguiente pierden la ventana cuando los propietarios de elementos de acción pueden actuar sobre compromisos mientras están frescos

## Distribución de Notas

**Formato de Línea de Asunto**: "[Tipo de Reunión] Notas - [Fecha] - [Tema Clave]"

Ejemplo: "Notas de Revisión de Roadmap de Producto - 20 de enero - Priorización Q1"

**Destinatarios**:
- Todos los asistentes
- Cualquiera mencionado en elementos de acción
- Cualquiera que haya solicitado notas

**Seguimiento**:
- Enviar recordatorio 3 días antes de las fechas de vencimiento de elementos de acción
- Resumen semanal de todos los elementos de acción abiertos
- Marcar elementos de acción como completados y compartir actualizaciones

## Ejecución

Para agentes que usan herramientas con servidores MCP conectados (Notion, Linear/Jira, Slack). Los runtimes sin acceso a herramientas ignoran esta sección y entregan el documento. Ver [SKILLSPEC.md §5](../../SKILLSPEC.md) y [connectors/mcp-pairings.md](../../connectors/mcp-pairings.md).

### Precondiciones
- Las notas estructuradas anteriores han sido mostradas al usuario y **explícitamente aprobadas**, incluyendo el destino (qué base de datos/página de Notion, qué proyecto de tracker).
- Los servidores MCP ya están conectados y autenticados en el entorno del agente.
- Cada elemento de acción tiene un propietario nombrado — los elementos sin propietario se resuelven con el usuario primero, nunca se asignan por suposición.

### Acciones Permitidas
- Crear UNA página en la base de datos de Notion aprobada (o herramienta de docs equivalente) conteniendo las notas aprobadas, verbatim.
- Crear un issue de tracker por cada elemento de acción aprobado (título, propietario, fecha de vencimiento de las notas) en el proyecto aprobado.
- Publicar el enlace de la página (solo el enlace y un resumen de una línea) en el canal aprobado, si el usuario especificó uno.
- Nada más: sin editar páginas/issues existentes, sin invitar o notificar personas más allá del canal nombrado, sin escrituras de calendario.

### Verificación
- Obtener la página creada y cada issue creado; confirmar que títulos, propietarios y fechas coincidan con las notas aprobadas.
- Reportar cada URL creada al usuario en una lista.

### Rollback
- Deshacer = archivar/eliminar la página y los issues recién creados, solo con instrucción explícita del usuario.
- Detener y preguntar a un usuario si: la base de datos/proyecto destino no se encuentra, cualquier creación de issue falla a mitad (reporta qué FUE creado), o un propietario de elemento de acción no existe en el tracker.
