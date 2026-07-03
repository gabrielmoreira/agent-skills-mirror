---
# machine-translated to es from skills/writing-great-skills/SKILL.md — review: pending. Native fixes welcome via PR.
name: writing-great-skills
description: "Crea un Agent Skill (SKILL.md) de alta calidad que la IA dispare y ejecute de forma fiable — frontmatter sólido, descripción incisiva con frases de activación, contrato de salida claro, controles de calidad y anti-patrones. Úsalo cuando te pidan escribir un skill, crear un SKILL.md, mejorar un skill, revisar un skill por calidad o contribuir a una librería de skills. Produce un SKILL.md completo que pase SkillCheck más una breve justificación de las decisiones clave."
---

# Skill para Escribir Excelentes Skills

Un skill es una promesa: *dado este tipo de solicitud, produce este tipo de output profesional, siempre.* Los mejores archivos SKILL.md ganan en dos cosas — el modelo los **dispara** en el momento correcto, y una vez disparado **produce el artefacto correcto** sin necesidad de intervención manual. Este skill te ayuda a escribir uno que haga ambas cosas.

## Partiendo de un brief

Dado un concepto inicial ("un skill para escribir changelogs"), **produce el SKILL.md completo de todas formas** — infiere el deliverable, inputs y estructura, y marca las elecciones genuinamente abiertas. Nunca devuelvas un esqueleto con `<!-- TODO -->` pendiente; rellénalo.

## Inputs Requeridos

Solicita (si no se proporcionan ya), o infiere y etiqueta:
- **Qué debe hacer el skill** y el **artefacto concreto** que produce
- **Cuándo debe dispararse** (las formas en que un usuario realmente escribiría la solicitud)
- **Los inputs** que necesita del usuario
- Cualquier **framework o estándar** que codifique (para atribución)

## La anatomía de un excelente SKILL.md

### 1. Frontmatter (esto es lo que hace que tu skill sea *encontrado*)
```yaml
---
name: kebab-case-name           # coincide con la carpeta; corto, específico
description: "<una frase rica>"
---
```
La **descripción es la línea más importante del archivo** — es todo lo que el modelo ve cuando decide si cargar el skill (divulgación progresiva: solo nombres + descripciones están en contexto hasta que uno se invoca). Una descripción sólida tiene tres partes:
- **Qué hace** + el deliverable concreto.
- **Una cláusula de activación "Úsalo cuando…"** listando las formas reales ("Úsalo cuando te pidan escribir un postmortem, hacer un análisis de causa raíz o documentar un incidente").
- **Una cláusula "Produce…"** nombrando el output ("Produce un postmortem sin culpa con cronología, causa raíz e items de acción").

Escribe los disparadores como los usuarios *hablan*, no como los categorizarías. Cubre sinónimos.

### 2. Declaración de valor de una línea
Abre el cuerpo con una sola frase sobre el valor, en la voz de un profesional senior.

### 3. Partiendo de un brief
Declara que el skill entrega un artefacto completo incluso con inputs mínimos — infiere y etiqueta supuestos, nunca dejes placeholders entre corchetes, nunca rechaces por falta de contexto. Esto es lo que separa un skill que *funciona* de uno que demanda.

### 4. Inputs Requeridos
Una breve lista de qué solicitar — e instrucciones para proceder con inferencias etiquetadas si faltan.

### 5. Formato de Salida / Estructura
El corazón del skill: una plantilla concreta — encabezados reales, tablas y secciones — del artefacto final. Muestra la forma, no la describas de forma abstracta. Aquí es donde vive la mayor parte de la calidad.

### 6. Controles de Calidad
Una breve lista de verificación que el output debe satisfacer (la rúbrica que un revisor aplicaría). Hazlos *observables*.

### 7. Anti-Patrones
Los modos de fallo específicos a evitar — los outputs perezosos o genéricos que un modelo más débil produciría.

## Proceso

1. **Clava el deliverable** en una frase antes de escribir nada más.
2. **Escribe la descripción** y somete a prueba los disparadores ("¿elegiría el modelo esto sobre un skill vecino?").
3. **Borra el Formato de Salida** como una plantilla real.
4. **Añade Controles de Calidad** y **Anti-Patrones** que apunten a los modos de fallo específicos de este skill.
5. **Valida**: `npm run skillcheck` (estructura) y ejecútalo contra un brief mínimo para confirmar que no pide inputs.

## Formato de Salida

Devuelve:
1. El **SKILL.md completo** en un bloque cercado, listo para guardar en `skills/<name>/SKILL.md`.
2. Una nota de 3–5 bullets **"por qué funciona"**: las frases de activación elegidas, el deliverable, y el anti-patrón más incisivo que resguarda.

## Controles de Calidad

- [ ] El `name` está en kebab-case y coincide con la carpeta prevista
- [ ] La descripción declara qué hace, tiene una cláusula de activación "Úsalo cuando…", y nombra qué **Produce**
- [ ] El cuerpo tiene: línea de valor, working-from-a-brief, inputs, una plantilla de Formato de Salida concreta, Controles de Calidad, Anti-Patrones
- [ ] Sin texto `TODO`/placeholder dejado
- [ ] Los disparadores son distintos de skills vecinos (no se dispararán erróneamente ni se saltarán)
- [ ] Pasaría `npm run skillcheck` sin errores

## Anti-Patrones

- Una descripción vaga sin frases de activación — el skill nunca se selecciona
- Un Formato de Salida que *describe* el artefacto en lugar de *templatizarlo*
- Controles de Calidad que no son observables ("el output debe ser bueno")
- Dejar `<!-- TODO -->` o placeholders entre corchetes en el archivo final
- Solapamiento tan pesado con un skill existente que el modelo no puede elegir entre ellos
