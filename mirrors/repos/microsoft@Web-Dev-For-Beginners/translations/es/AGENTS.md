# AGENTS.md

## Descripción del Proyecto

Este es un repositorio educativo para enseñar los fundamentos del desarrollo web a principiantes. El currículum es un curso integral de 12 semanas desarrollado por Microsoft Cloud Advocates, que incluye 24 lecciones prácticas sobre JavaScript, CSS y HTML.

### Componentes Clave

- **Contenido Educativo**: 24 lecciones estructuradas organizadas en módulos basados en proyectos
- **Proyectos Prácticos**: Terrarium, Juego de mecanografía, Extensión de navegador, Juego espacial, Aplicación bancaria, Editor de código y Asistente de chat con IA
- **Cuestionarios Interactivos**: 48 cuestionarios con 3 preguntas cada uno (evaluaciones pre y post lección)
- **Soporte Multilenguaje**: Traducciones automáticas en más de 50 idiomas vía GitHub Actions
- **Tecnologías**: HTML, CSS, JavaScript, Vue.js 3, Vite, Node.js, Express, Python (para proyectos de IA)

### Arquitectura

- Repositorio educativo con estructura basada en lecciones
- Cada carpeta de lección contiene README, ejemplos de código y soluciones
- Proyectos independientes en directorios separados (quiz-app, varios proyectos de lecciones)
- Sistema de traducción usando GitHub Actions (co-op-translator)
- Documentación servida vía Docsify y disponible en PDF

## Comandos de Configuración

Este repositorio está principalmente para consumo de contenido educativo. Para trabajar con proyectos específicos:

### Configuración Principal del Repositorio

```bash
git clone https://github.com/microsoft/Web-Dev-For-Beginners.git
cd Web-Dev-For-Beginners
```

### Configuración de Quiz App (Vue 3 + Vite)

```bash
cd quiz-app
npm install
npm run dev        # Iniciar servidor de desarrollo
npm run build      # Construir para producción
npm run lint       # Ejecutar ESLint
```

### API para Proyecto Bancario (Node.js + Express)

```bash
cd 7-bank-project/api
npm install
npm start          # Iniciar servidor API
npm run lint       # Ejecutar ESLint
npm run format     # Formatear con Prettier
```

### Proyectos de Extensión para Navegador

```bash
cd 5-browser-extension/solution
npm install
# Sigue las instrucciones específicas del navegador para cargar extensiones
```

### Proyectos de Juego Espacial

```bash
cd 6-space-game/solution
npm install
# Abre index.html en el navegador o usa Live Server
```

### Proyecto de Chat (Backend en Python)

```bash
cd 9-chat-project/solution/backend/python
pip install openai
# Establecer la variable de entorno GITHUB_TOKEN
python api.py
```

## Flujo de Desarrollo

### Para Contribuidores de Contenido

1. **Hacer fork del repositorio** a tu cuenta de GitHub
2. **Clonar tu fork** localmente
3. **Crear una nueva rama** para tus cambios
4. Realizar cambios en contenido de lecciones o ejemplos de código
5. Probar cualquier cambio de código en los directorios de proyectos relevantes
6. Enviar pull requests siguiendo las directrices de contribución

### Para Estudiantes

1. Hacer fork o clonar el repositorio
2. Navegar secuencialmente por los directorios de lecciones
3. Leer los archivos README de cada lección
4. Completar cuestionarios pre-lección en https://ff-quizzes.netlify.app/web/
5. Trabajar con ejemplos de código en las carpetas de las lecciones
6. Completar tareas y desafíos
7. Realizar cuestionarios post-lección

### Desarrollo en Vivo

- **Documentación**: Ejecutar `docsify serve` en la raíz (puerto 3000)
- **Quiz App**: Ejecutar `npm run dev` en el directorio quiz-app
- **Proyectos**: Usar extensión Live Server de VS Code para proyectos HTML
- **Proyectos API**: Ejecutar `npm start` en los directorios API respectivos

## Instrucciones para Pruebas

### Pruebas de Quiz App

```bash
cd quiz-app
npm run lint       # Verificar problemas de estilo de código
npm run build      # Verificar que la compilación sea exitosa
```

### Pruebas de API Bancaria

```bash
cd 7-bank-project/api
npm run lint       # Verificar problemas de estilo de código
node server.js     # Verificar que el servidor arranque sin errores
```

### Enfoque General para Pruebas

- Este repositorio educativo no cuenta con pruebas automatizadas completas
- Las pruebas manuales se centran en:
  - Que los ejemplos de código se ejecuten sin errores
  - Que los enlaces en la documentación funcionen correctamente
  - Que las compilaciones de proyectos finalicen sin errores
  - Que los ejemplos sigan las mejores prácticas

### Chequeos Previo al Envío

- Ejecutar `npm run lint` en directorios con package.json
- Verificar que los enlaces en markdown sean válidos
- Probar ejemplos de código en navegador o Node.js
- Comprobar que las traducciones mantengan la estructura adecuada

## Guías de Estilo de Código

### JavaScript

- Usar sintaxis moderna ES6+
- Seguir configuraciones standard de ESLint proporcionadas en proyectos
- Usar nombres significativos para variables y funciones para claridad educativa
- Añadir comentarios que expliquen conceptos para los estudiantes
- Formatear usando Prettier donde esté configurado

### HTML/CSS

- Elementos semánticos HTML5
- Principios de diseño responsivo
- Convenciones claras de nombres de clases
- Comentarios que expliquen técnicas CSS para estudiantes

### Python

- Guías de estilo PEP 8
- Código claro y educativo
- Anotaciones de tipo donde sean útiles para el aprendizaje

### Documentación en Markdown

- Jerarquía clara de encabezados
- Bloques de código con especificación de lenguaje
- Enlaces a recursos adicionales
- Capturas de pantalla e imágenes en directorios `images/`
- Texto alternativo para imágenes para accesibilidad

### Organización de Archivos

- Lecciones numeradas secuencialmente (1-getting-started-lessons, 2-js-basics, etc.)
- Cada proyecto tiene `solution/` y a menudo `start/` o `your-work/`
- Imágenes almacenadas en carpetas `images/` específicas por lección
- Traducciones en la estructura `translations/{language-code}/`

## Construcción y Despliegue

### Despliegue de Quiz App (Azure Static Web Apps)

La quiz-app está configurada para despliegue en Azure Static Web Apps:

```bash
cd quiz-app
npm run build      # Crea la carpeta dist/
# Despliega mediante el flujo de trabajo de GitHub Actions al hacer push en main
```

Configuración de Azure Static Web Apps:
- **Ubicación de la app**: `/quiz-app`
- **Ubicación de salida**: `dist`
- **Flujo de trabajo**: `.github/workflows/azure-static-web-apps-ashy-river-0debb7803.yml`

### Generación de Documentación PDF

```bash
npm install                    # Instalar docsify-to-pdf
npm run convert               # Generar PDF desde docs
```

### Documentación con Docsify

```bash
npm install -g docsify-cli    # Instalar Docsify globalmente
docsify serve                 # Servir en localhost:3000
```

### Compilaciones específicas de proyectos

Cada directorio de proyecto puede tener su propio proceso de compilación:
- Proyectos Vue: `npm run build` crea paquetes para producción
- Proyectos estáticos: No tienen paso de compilación, se sirven archivos directamente

## Directrices para Pull Requests

### Formato del Título

Usar títulos claros y descriptivos indicando la área de cambio:
- `[Quiz-app] Añadir nuevo cuestionario para la lección X`
- `[Lesson-3] Corregir error tipográfico en proyecto terrarium`
- `[Translation] Añadir traducción al español para la lección 5`
- `[Docs] Actualizar instrucciones de configuración`

### Verificaciones Requeridas

Antes de enviar un PR:

1. **Calidad del código**:
   - Ejecutar `npm run lint` en directorios afectados
   - Corregir todos los errores y advertencias de linting

2. **Verificación de compilación**:
   - Ejecutar `npm run build` si aplica
   - Asegurar que no hay errores en la compilación

3. **Validación de enlaces**:
   - Probar todos los enlaces markdown
   - Verificar referencias de imágenes

4. **Revisión de contenido**:
   - Revisar ortografía y gramática
   - Asegurar que ejemplos de código sean correctos y educativos
   - Verificar que las traducciones mantengan el significado original

### Requisitos para Contribuir

- Aceptar Microsoft CLA (verificación automática en primer PR)
- Seguir el [Código de Conducta de Código Abierto de Microsoft](https://opensource.microsoft.com/codeofconduct/)
- Consultar [CONTRIBUTING.md](./CONTRIBUTING.md) para directrices detalladas
- Referenciar números de issues en la descripción del PR si aplica

### Proceso de Revisión

- Los PR son revisados por mantenedores y la comunidad
- Se prioriza la claridad educativa
- Los ejemplos de código deben seguir mejores prácticas actuales
- Las traducciones se revisan para exactitud y adecuación cultural

## Sistema de Traducción

### Traducción Automática

- Usa GitHub Actions con el workflow co-op-translator
- Traduce automáticamente a más de 50 idiomas
- Archivos fuente en directorios principales
- Archivos traducidos en `translations/{language-code}/`

### Agregar Mejoras Manuales de Traducción

1. Localizar archivo en `translations/{language-code}/`
2. Mejorar manteniendo la estructura
3. Asegurar que los ejemplos de código sigan funcionando
4. Probar cualquier cuestionario localizado

### Metadatos de Traducción

Los archivos traducidos incluyen encabezado de metadatos:
```markdown
<!--
CO_OP_TRANSLATOR_METADATA:
{
  "original_hash": "...",
  "translation_date": "...",
  "source_file": "...",
  "language_code": "..."
}
-->
```

## Depuración y Resolución de Problemas

### Problemas Comunes

**La app de cuestionarios no arranca**:
- Verificar versión de Node.js (recomendada v14+)
- Eliminar `node_modules` y `package-lock.json`, ejecutar de nuevo `npm install`
- Revisar conflictos de puertos (por defecto: Vite usa puerto 5173)

**El servidor API no inicia**:
- Verificar que la versión de Node.js sea compatible (node >=10)
- Comprobar si el puerto está en uso
- Asegurar que todas las dependencias estén instaladas con `npm install`

**La extensión del navegador no carga**:
- Verificar que el manifest.json esté bien formado
- Revisar la consola del navegador para errores
- Seguir instrucciones específicas del navegador para instalar extensiones

**Problemas con el proyecto de chat en Python**:
- Asegurar que el paquete OpenAI esté instalado: `pip install openai`
- Verificar que la variable de entorno GITHUB_TOKEN esté configurada
- Comprobar permisos de acceso a GitHub Models

**Docsify no sirve la documentación**:
- Instalar docsify-cli globalmente: `npm install -g docsify-cli`
- Ejecutar desde el directorio raíz del repositorio
- Confirmar que `docs/_sidebar.md` exista

### Consejos para el Entorno de Desarrollo

- Usar VS Code con extensión Live Server para proyectos HTML
- Instalar extensiones ESLint y Prettier para formateo consistente
- Usar DevTools del navegador para depurar JavaScript
- Para proyectos Vue, instalar extensión Vue DevTools para navegador

### Consideraciones de Rendimiento

- Gran cantidad de archivos traducidos (más de 50 idiomas) hace que clonaciones completas sean grandes
- Usar clonación superficial si solo se trabaja con contenido: `git clone --depth 1`
- Excluir traducciones de búsquedas al trabajar con contenido en inglés
- Los procesos de compilación pueden ser lentos en la primera ejecución (npm install, compilación Vite)

## Consideraciones de Seguridad

### Variables de Entorno

- Las claves API nunca deben subirse al repositorio
- Usar archivos `.env` (ya incluidos en `.gitignore`)
- Documentar variables de entorno necesarias en los READMEs de los proyectos

### Proyectos en Python

- Usar entornos virtuales: `python -m venv venv`
- Mantener dependencias actualizadas
- Los tokens de GitHub deben tener permisos mínimos necesarios

### Acceso a GitHub Models

- Se requieren Tokens de Acceso Personal (PAT) para GitHub Models
- Los tokens deben almacenarse como variables de entorno
- Nunca subir tokens o credenciales al repositorio

## Notas Adicionales

### Público Objetivo

- Principiantes completos en desarrollo web
- Estudiantes y autodidactas
- Profesores que usan el currículum en aulas
- Contenido diseñado para accesibilidad y desarrollo gradual de habilidades

### Filosofía Educativa

- Enfoque basado en aprendizaje por proyectos
- Chequeos frecuentes de conocimiento (cuestionarios)
- Ejercicios prácticos de codificación
- Ejemplos de aplicaciones del mundo real
- Enfoque en fundamentos antes que frameworks

### Mantenimiento del Repositorio

- Comunidad activa de aprendices y contribuyentes
- Actualizaciones regulares en dependencias y contenido
- Issues y discusiones monitoreadas por mantenedores
- Actualizaciones de traducción automatizadas vía GitHub Actions

### Recursos Relacionados

- [Módulos Microsoft Learn](https://docs.microsoft.com/learn/)
- [Recursos para estudiantes hub](https://docs.microsoft.com/learn/student-hub/)
- [GitHub Copilot](https://marketplace.visualstudio.com/items?itemName=GitHub.copilot) recomendado para aprendices
- Cursos adicionales: IA generativa, Ciencia de datos, ML, currículos IoT disponibles

### Trabajo con Proyectos Específicos

Para instrucciones detalladas de proyectos individuales, consultar los archivos README en:
- `quiz-app/README.md` - aplicación de cuestionarios en Vue 3
- `7-bank-project/README.md` - aplicación bancaria con autenticación
- `5-browser-extension/README.md` - desarrollo de extensión de navegador
- `6-space-game/README.md` - desarrollo de juego en canvas
- `9-chat-project/README.md` - proyecto de asistente de chat IA

### Estructura Monorepo

Aunque no es un monorepo tradicional, este repositorio contiene múltiples proyectos independientes:
- Cada lección es autónoma
- Los proyectos no comparten dependencias
- Se puede trabajar en proyectos individuales sin afectar otros
- Clonar el repositorio completo para experiencia completa del currículum

---

<!-- CO-OP TRANSLATOR DISCLAIMER START -->
**Descargo de responsabilidad**:  
Este documento ha sido traducido utilizando el servicio de traducción automática [Co-op Translator](https://github.com/Azure/co-op-translator). Aunque nos esforzamos por la precisión, tenga en cuenta que las traducciones automatizadas pueden contener errores o inexactitudes. El documento original en su idioma nativo debe considerarse la fuente autorizada. Para información crítica, se recomienda una traducción profesional humana. No nos hacemos responsables de malentendidos o interpretaciones erróneas derivadas del uso de esta traducción.
<!-- CO-OP TRANSLATOR DISCLAIMER END -->