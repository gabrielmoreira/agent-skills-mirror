---
# machine-translated to es from skills/changelog-generator/SKILL.md — review: pending. Native fixes welcome via PR.
name: changelog-generator
description: "Convierte un registro git, lista de commits o notas de versión en un changelog pulido, orientado al usuario. Úsalo cuando estés escribiendo notas de versión, generando una entrada en CHANGELOG.md, o documentando qué cambió en una versión. Produce una sección de changelog estructurada con encabezado de versión, cambios categorizados y notas de migración. Para una lista de cambios ya curada, usa changelog-writer en su lugar."
---

# Skill Generador de Changelog

Convierte commits git sin procesar, un resumen de diff o notas de versión de desarrolladores en una entrada de changelog pulida — categorizada, orientada al usuario y siguiendo las convenciones de Keep a Changelog.

## Entradas Requeridas

Solicita estas si no se proporcionan:
- **Commits o notas de versión** (pega `git log --oneline`, mensajes de commit sin procesar, o una descripción de qué cambió)
- **Número de versión** (ej. 2.4.0, v1.0.0-beta.2)
- **Fecha de lanzamiento** (o "hoy")
- **Audiencia** (desarrolladores usando una API / usuarios finales de un producto / equipo interno — afecta el lenguaje)
- **Cambios disruptivos** (marca estos explícitamente si se conocen)
- **Comportamiento de versión anterior** (opcional — pega la entrada anterior del changelog o describe qué está cambiando; necesario para entradas "Changed" precisas)
- **Alcance** (producto completo / paquete específico o módulo — ej. "solo SDK de pagos", "app iOS", "todos los servicios")

## Formato de Salida

Sigue el formato de [Keep a Changelog](https://keepachangelog.com):

---

## [X.Y.Z] — YYYY-MM-DD

### Cambios Disruptivos ⚠️
[Solo incluye si hay cambios disruptivos]
- **[Cambio disruptivo]:** [Qué cambió y qué rompe]
- **Migración requerida:** [Acción específica que el usuario debe tomar]

### Agregado
- [Nueva característica o capacidad, escrita desde la perspectiva del usuario]
- [Otra adición]

### Cambiado
- [Comportamiento cambiado — qué hacía antes vs. qué hace ahora]
- [Mejora de rendimiento con impacto medible si se conoce]

### Corregido
- [Bug corregido — describe qué estaba roto, no la implementación de la corrección]
- [Otra corrección]

### Deprecado
- [Cosa deprecada] — usa [reemplazo] en su lugar. Será removida en [versión].

### Removido
- [Cosa removida] — fue deprecada en [versión]

### Seguridad
- [Corrección de seguridad — describe la clase de vulnerabilidad, no detalles de exploit]

---

---

> **Orientación del skill — no incluyas la siguiente sección en el changelog entregado:**

## Reglas de Formato Aplicadas

**Lenguaje:** Escribe para el lector, no para quien hizo el commit. "Agregar soporte de modo oscuro" no "implementar ThemeProvider con variante de paleta oscura".

**Cambios disruptivos:** Siempre llama la atención sobre estos primero con ⚠️. Incluye una ruta de migración.

**Correcciones de bugs:** Describe qué estaba roto, no qué fue cambiado. "Corregir crash cuando el usuario no tiene foto de perfil" no "verificar nulidad de URL de avatar antes de renderizar".

**Granularidad:** Agrupa commits relacionados en una línea. No lijes cada micro-commit por separado.

**Tono:** Voz activa, modo imperativo. "Agregar", "Corregir", "Remover" — no "Agregado", "Corregido", "Removido".

**Secciones vacías:** Omite cualquier sección sin entradas. No incluyas bloques vacíos de `### Corregido`.

## Verificaciones de Calidad
- [ ] Los cambios disruptivos están al inicio con instrucciones de migración
- [ ] Todas las entradas están en lenguaje orientado al usuario (sin nombres de variables internas o detalles de implementación)
- [ ] Los commits relacionados están agrupados en entradas únicas (no listados individualmente)
- [ ] El encabezado de versión y fecha es correcto
- [ ] Las secciones vacías están omitidas
- [ ] Ninguna entrada comienza con verbos en pasado (no "Agregado", "Corregido", "Removido" — usa "Agregar", "Corregir", "Remover")
- [ ] Toda entrada de cambio disruptivo incluye una acción de migración específica (no solo "actualiza tu código")

## Anti-Patrones

- [ ] No incluyas detalles de implementación en entradas del changelog — los usuarios necesitan saber qué cambió para ellos, no cómo fue refactorizado el código internamente
- [ ] No listes cada micro-commit como una entrada separada — los commits relacionados deben agruparse en un cambio único orientado al usuario
- [ ] No omitas la ruta de migración para cambios disruptivos — una entrada de cambio disruptivo sin una acción de migración específica obliga a los usuarios a leer el código fuente
- [ ] No incluyas secciones vacías — una sección "### Corregido" sin entradas señala que la plantilla fue rellenada descuidadamente
- [ ] No escribas cambios disruptivos con el mismo tono casual que adiciones menores — los cambios disruptivos deben ser visualmente prominentes y aclarar explícitamente los requisitos de migración

## Ejemplos de Uso
- "Escribe un changelog para la versión [X]" + [pega commits]
- "Genera notas de versión a partir de estos commits"
- "Convierte este git log en una entrada de CHANGELOG"
- "Escribe la actualización de CHANGELOG.md para este lanzamiento"
- "¿Qué cambió en este lanzamiento?" + [pega lista de commits]
