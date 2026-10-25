#!/usr/bin/env bash
# Inicializar archivos de planificación para una nueva sesión
# Uso: ./init-session.sh [nombre_del_proyecto]

set -e

PROJECT_NAME="${1:-project}"
DATE=$(date +%Y-%m-%d)

echo "Inicializando archivos de planificación: $PROJECT_NAME"

# Crear task_plan.md si no existe
if [ ! -f "task_plan.md" ]; then
    cat > task_plan.md << 'EOF'
# Plan de Tareas: [descripción breve]

Esta es la hoja de ruta visible de toda la tarea y la memoria de trabajo persistente en disco. Actualízala al completar cada fase.

## Objetivo
[describir el estado final en una frase]

## Fase Actual
Fase 1

## Fases

### Phase 1: Requisitos y Descubrimiento
- [ ] Comprender la intención del usuario
- [ ] Identificar restricciones y requisitos
- [ ] Documentar hallazgos en findings.md
- **Estado:** in_progress

### Phase 2: Planificación y Estructura
- [ ] Definir enfoque técnico
- [ ] Crear estructura de proyecto si es necesario
- **Estado:** pending

### Phase 3: Implementación
- [ ] Ejecutar paso a paso según el plan
- [ ] Escribir código en archivos antes de ejecutar
- **Estado:** pending

### Phase 4: Pruebas y Validación
- [ ] Verificar que todos los requisitos están satisfechos
- [ ] Documentar resultados de pruebas en progress.md
- **Estado:** pending

### Phase 5: Entrega
- [ ] Revisar todos los archivos de salida
- [ ] Entregar al usuario
- **Estado:** pending

## Decisiones Tomadas
| Decisión | Justificación |
|------|------|

## Errores Encontrados
| Error | Solución |
|------|---------|

## Notas
- Relee este plan antes de decisiones importantes para mantener presente el objetivo aprobado.
- Registra todos los errores y cambia de enfoque cuando falle una acción.
EOF
    echo "Creado task_plan.md"
else
    echo "task_plan.md ya existe, omitiendo"
fi

# Crear findings.md si no existe
if [ ! -f "findings.md" ]; then
    cat > findings.md << 'EOF'
# Hallazgos y Decisiones

## Requisitos
-

## Hallazgos de Investigación
-

## Decisiones Técnicas
| Decisión | Justificación |
|------|------|

## Problemas Encontrados
| Problema | Solución |
|------|---------|

## Recursos
-
EOF
    echo "Creado findings.md"
else
    echo "findings.md ya existe, omitiendo"
fi

# Crear progress.md si no existe
if [ ! -f "progress.md" ]; then
    cat > progress.md << EOF
# Registro de Progreso

## Sesión: $DATE

### Estado Actual
- **Fase:** 1 - Requisitos y Descubrimiento
- **Inicio:** $DATE

### Acciones Realizadas
-

### Resultados de Pruebas
| Prueba | Resultado esperado | Resultado real | Estado |
|------|---------|---------|------|

### Errores
| Error | Solución |
|------|---------|
EOF
    echo "Creado progress.md"
else
    echo "progress.md ya existe, omitiendo"
fi

echo ""
echo "¡Archivos de planificación inicializados!"
echo "Archivos: task_plan.md, findings.md, progress.md"
