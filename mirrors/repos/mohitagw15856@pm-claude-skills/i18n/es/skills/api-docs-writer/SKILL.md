---
# machine-translated to es from skills/api-docs-writer/SKILL.md — review: pending. Native fixes welcome via PR.
name: api-docs-writer
description: "Escribe documentación clara de API orientada a desarrolladores. Úsalo cuando necesites documentar un endpoint de API, escribir documentos de referencia de API, crear una guía para desarrolladores o convertir una especificación bruta o colección de Postman en documentación. Produce documentación de endpoints con descripciones, parámetros, ejemplos de solicitud/respuesta y códigos de error."
---

# Skill API Docs Writer

Este skill transforma especificaciones de API brutas, descripciones de endpoints o colecciones de Postman en documentación limpia orientada a desarrolladores, siguiendo convenciones similares a OpenAPI. El resultado está listo para un portal de desarrolladores, README o página de Notion/Confluence.

## Entradas Requeridas

Solicita al usuario estos datos si no están disponibles:
- **Detalles de API o endpoint** (especificación bruta, exportación de Postman o descripción verbal)
- **Método de autenticación** (clave de API / token Bearer / OAuth 2.0 / Ninguno)
- **URL base**
- **Versión de API** (p. ej. v1, v2.3, o "sin versión" — afecta notas de deprecación y headers de versionado)
- **Límites de velocidad** (solicitudes por segundo/minuto por token o IP, si se conocen — o "desconocido")
- **Audiencia** (desarrolladores internos / partners externos / público)
- **Formato de salida** (Markdown para portales de desarrolladores y READMEs / Prosa simple para Confluence o Notion — nota: este skill no produce YAML de OpenAPI)

## Formato de Salida

Para cada endpoint, produce lo siguiente:

---

## `[MÉTODO] /ruta/al/endpoint`

**Resumen:** [Una línea — qué hace este endpoint]

**Descripción:** [2–4 oraciones. Cuándo usar este endpoint. Qué devuelve. Comportamiento importante a conocer (paginación, límites de velocidad, procesamiento asíncrono, etc.)]

**Autenticación:** [Requerida / Opcional — método]

---

### Solicitud

**Headers:**

| Header | Requerido | Descripción |
|---|---|---|
| `Authorization` | Sí | `Bearer <token>` |
| `Content-Type` | Sí | `application/json` |

**Parámetros de Ruta:**

| Parámetro | Tipo | Requerido | Descripción |
|---|---|---|---|
| `id` | string | Sí | Identificador único del recurso |

**Parámetros de Consulta:**

| Parámetro | Tipo | Requerido | Predeterminado | Descripción |
|---|---|---|---|---|
| `limit` | integer | No | 20 | Máximo de resultados por página (1–100) |
| `cursor` | string | No | — | Cursor de paginación de respuesta anterior |

**Cuerpo de la Solicitud:**

```json
{
  "field_name": "value",
  "another_field": 42
}
```

| Campo | Tipo | Requerido | Descripción |
|---|---|---|---|
| `field_name` | string | Sí | [Descripción clara de qué hace este campo] |
| `another_field` | integer | No | [Descripción. Incluye rango válido o valores enum si aplica] |

---

### Respuesta

**Respuesta de Éxito: `200 OK`**

```json
{
  "id": "abc123",
  "status": "active",
  "created_at": "2025-04-01T10:00:00Z"
}
```

| Campo | Tipo | Descripción |
|---|---|---|
| `id` | string | Identificador único del recurso creado/recuperado |
| `status` | string | Estado actual. Enum: `active`, `inactive`, `pending` |
| `created_at` | string ISO 8601 | Timestamp de creación en UTC |

---

### Códigos de Error

| Código de Estado | Código de Error | Descripción | Cómo Resolver |
|---|---|---|---|
| `400` | `INVALID_REQUEST` | El cuerpo de solicitud está malformado o falta campos requeridos | Verifica el cuerpo de solicitud contra el schema anterior |
| `401` | `UNAUTHORIZED` | Token de autenticación faltante o inválido | Verifica tu clave de API o refresca tu token |
| `404` | `NOT_FOUND` | El recurso solicitado no existe | Verifica el ID en el parámetro de ruta |
| `429` | `RATE_LIMITED` | Demasiadas solicitudes | Retrocede e intenta de nuevo después del valor del header `Retry-After` |
| `500` | `INTERNAL_ERROR` | Error inesperado del servidor | Reinténtalo con backoff exponencial; contacta soporte si persiste |

---

### Ejemplos de Código

Produce ejemplos en al menos 2 lenguajes relevantes para la audiencia (predeterminado: cURL + Python):

**cURL:**
```bash
curl -X POST https://api.example.com/v1/endpoint \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"field_name": "value"}'
```

**Python:**
```python
import requests

response = requests.post(
    "https://api.example.com/v1/endpoint",
    headers={"Authorization": "Bearer YOUR_TOKEN"},
    json={"field_name": "value"}
)
data = response.json()
```

---

## Controles de Calidad

- [ ] Cada parámetro está documentado (tipo, requerido/opcional, descripción)
- [ ] Los campos de respuesta están completamente documentados con tipos
- [ ] Se listan todos los códigos de error relevantes con orientación de resolución
- [ ] Los códigos de error cubren como mínimo: 400 (solicitud incorrecta), 401/403 (autenticación), 404 (no encontrado), 429 (límite de velocidad), 500 (error del servidor) — o indica explícitamente cuáles no aplican a este endpoint
- [ ] Los ejemplos de código usan la URL base actual y un token placeholder realista — ningún ejemplo referencia variables indefinidas o "YOUR_ENDPOINT" fuera del snippet
- [ ] El método de autenticación se indica claramente arriba
- [ ] Los valores enum se listan donde aplica
- [ ] Se documenta la paginación si el endpoint es un endpoint de lista

## Anti-Patrones

- [ ] No documentes solo el camino feliz — cada endpoint debe tener códigos de error para al menos 400, 401/403, 404, 429 y 500
- [ ] No uses valores placeholder como "YOUR_ENDPOINT" o "INSERT_TOKEN" en ejemplos de código — usa placeholders realistas anclados a la URL base actual
- [ ] No omitas valores enum para campos con un conjunto fijo de valores aceptados — los enums no documentados causan bugs de integración
- [ ] No omitas documentación de paginación en endpoints de lista — los desarrolladores que se la pierdan construirán integraciones que silenciosamente pierdan datos
- [ ] No describa qué es un campo sin describir qué hace — "el ID" no es documentación; "el identificador único usado para recuperar o actualizar este recurso" lo es

## Ejemplos de Uso
- "Documenta este endpoint de API: [pega especificación o descripción]"
- "Convierte esta colección de Postman en documentos para desarrolladores"
- "Escribe documentación de referencia de API para [endpoint]"
- "Escribe una guía para desarrolladores para nuestra API de [producto]"
