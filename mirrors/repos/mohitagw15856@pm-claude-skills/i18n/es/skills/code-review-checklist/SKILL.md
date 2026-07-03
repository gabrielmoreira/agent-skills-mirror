---
# machine-translated to es from skills/code-review-checklist/SKILL.md — review: pending. Native fixes welcome via PR.
name: code-review-checklist
description: "Genera una lista de verificación de revisión de código personalizada para cualquier solicitud de cambios basada en el lenguaje, tipo de cambio y nivel de riesgo. Úsalo cuando te pidan revisar código, verificar un PR, revisar una solicitud de cambios o generar una lista de verificación de revisión de código. Produce una lista de verificación enfocada con comprobaciones específicas del lenguaje, profundidad apropiada al nivel de riesgo y una recomendación clara de aprobar o solicitar cambios."
---

# Habilidad de Lista de Verificación de Revisión de Código

Produce una lista de verificación de revisión de código personalizada para una solicitud de cambios específica — escalada al lenguaje, tipo de cambio y nivel de riesgo. No es una plantilla genérica.

## Entradas Requeridas

Solicita al usuario estos datos si no los proporciona:
- **Lenguaje y framework** (p. ej. TypeScript + React / Python + FastAPI / Go)
- **Tipo de cambio** (feature / bug fix / refactor / dependency upgrade / security patch / performance)
- **Nivel de riesgo** (low / medium / high / critical)
- **Descripción del PR** (pega la descripción o un enlace al PR)
- **Código o diff** (opcional — pega archivos clave modificados o un `git diff`; mejora significativamente la especificidad de la lista)
- **Contexto del autor** (developer junior / experimentado / contributor externo)

## Formato de Salida

---

# Revisión de Código: [Título del PR o Referencia]

### 1. Descripción General del PR
**Evaluación del alcance:** [Pequeño / Medio / Grande / Demasiado grande — debería dividirse]
**Profundidad de revisión recomendada:** [Rápida / Estándar / Profunda]
**Tiempo estimado de revisión:** [p. ej. 20–30 min — usa aproximadamente 5 min por cada 50 líneas de diff como guía]

### 2. Comprobaciones de Corrección

Comprobaciones de corrección específicas del lenguaje — elige según el lenguaje indicado:

**Para TypeScript/JavaScript:**
- Las definiciones de tipos coinciden con el uso real
- No hay `any` implícito en código de no-prueba
- async/await se usa consistentemente; no hay promesas sin manejar
- El manejo de null/undefined es explícito

**Para Python:**
- Type hints presentes en funciones públicas
- El manejo de excepciones es específico (sin except desnudo)
- Los recursos se cierran (context managers, with blocks)

**Para Go:**
- Los errores se manejan o se ignoran explícitamente con un comentario
- La propagación de Context es correcta
- Los tiempos de vida de goroutine están limitados

[Incluye solo la sección que coincida con el lenguaje indicado]

### 3. Comprobaciones Específicas del Tipo de Cambio

**Para bug fixes:**
- Existe una prueba que hubiera detectado este bug
- El fix aborda la causa raíz, no el síntoma
- Rutas de código relacionadas verificadas para el mismo problema

**Para features:**
- Criterios de aceptación cumplidos
- Casos límite manejados (vacío, grande, concurrente)
- Rutas de error probadas, no solo el camino feliz
- Telemetría/logging añadido para depuración

**Para refactors:**
- Comportamiento sin cambios (las pruebas siguen pasando)
- Sin scope creep — solo refactor
- Complejidad reducida, no solo movida

**Para dependency upgrades:**
- Breaking changes revisados
- Security advisories verificados
- Compatibilidad de licencia verificada

[Incluye solo la sección que coincida con el tipo de cambio indicado]

### 4. Comprobaciones Apropiadas al Nivel de Riesgo

**Low risk:** corrección básica, convenciones de estilo, cobertura de pruebas
**Medium risk:** anterior + plan de rollback, actualizaciones de monitoreo, consideraciones de rendimiento
**High risk:** anterior + implicaciones de seguridad, seguridad de migración de datos, feature flag/rollout gradual
**Critical risk:** anterior + plan de validación en staging, plan de respuesta ante incidentes, checklist de verificación post-despliegue

### 5. Adecuación de Pruebas
- Las pruebas unitarias cubren la lógica nueva
- Las pruebas de integración cubren los cambios de contrato
- Casos límite probados
- Modos de fallo probados
- Pruebas de rendimiento si es sensible al rendimiento

### 6. Marco de Decisión de Revisión

**Aprobar si:** [2-3 condiciones específicas basadas en este PR]
**Solicitar cambios si:** [Bloqueadores específicos]
**Comentar (no bloqueante) si:** [Elementos que valen la pena discutir pero no bloquean la fusión]

### 7. Trampas Comunes para Este Tipo de Cambio
Basado en el tipo de cambio e idioma, señala 2-3 cosas que los revisores típicamente pasan por alto para esta combinación.

---

## Comprobaciones de Calidad
- [ ] La lista está personalizada al lenguaje indicado (no genérica)
- [ ] La sección específica del tipo de cambio está incluida
- [ ] La profundidad apropiada al riesgo coincide con el nivel de riesgo indicado
- [ ] El marco de decisión incluye al menos una condición bloqueante nombrada y una condición de comentario no bloqueante nombrada
- [ ] Las trampas comunes son específicas de la combinación lenguaje + tipo de cambio (no consejos genéricos como "cuidado con los bugs")

## Anti-Patrones

- [ ] No generes una lista genérica que ignore el lenguaje indicado — una lista de Python y una de Go tienen preocupaciones de corrección fundamentalmente diferentes
- [ ] No trates "se ve bien" como un resultado válido de revisión — la lista existe para identificar preocupaciones específicas, no para validar una lectura superficial
- [ ] No hagas un scope de una revisión "high risk" igual que una revisión "low risk" — la profundidad debe escalar con el nivel de riesgo indicado
- [ ] No marques cada preferencia estilística como un problema bloqueante — distingue entre problemas bloqueantes de corrección y comentarios no bloqueantes
- [ ] No omitas la sección "trampas comunes" para la combinación lenguaje + tipo de cambio indicada — aquí es donde vive el conocimiento más valioso

## Ejemplos de Uso
- "Genera una lista de verificación de revisión de código para [descripción del PR]"
- "¿Qué debo verificar en esta solicitud de cambios?"
- "Dame una lista de verificación de revisión de código para un [lenguaje] [tipo de cambio]"
- "Lista de verificación de revisión para un PR de alto riesgo en [lenguaje]"
