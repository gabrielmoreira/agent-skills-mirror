# Resilience Guide (Español)

🌐 **Languages:** 🇺🇸 [English](../../../../architecture/RESILIENCE_GUIDE.md) · 🇪🇹 [am](../../../am/docs/architecture/RESILIENCE_GUIDE.md) · 🇸🇦 [ar](../../../ar/docs/architecture/RESILIENCE_GUIDE.md) · 🇦🇿 [az](../../../az/docs/architecture/RESILIENCE_GUIDE.md) · 🇧🇬 [bg](../../../bg/docs/architecture/RESILIENCE_GUIDE.md) · 🇧🇩 [bn](../../../bn/docs/architecture/RESILIENCE_GUIDE.md) · 🇨🇿 [cs](../../../cs/docs/architecture/RESILIENCE_GUIDE.md) · 🇩🇰 [da](../../../da/docs/architecture/RESILIENCE_GUIDE.md) · 🇩🇪 [de](../../../de/docs/architecture/RESILIENCE_GUIDE.md) · 🇬🇷 [el](../../../el/docs/architecture/RESILIENCE_GUIDE.md) · 🇪🇪 [et](../../../et/docs/architecture/RESILIENCE_GUIDE.md) · 🇮🇷 [fa](../../../fa/docs/architecture/RESILIENCE_GUIDE.md) · 🇫🇮 [fi](../../../fi/docs/architecture/RESILIENCE_GUIDE.md) · 🇫🇷 [fr](../../../fr/docs/architecture/RESILIENCE_GUIDE.md) · 🇮🇪 [ga](../../../ga/docs/architecture/RESILIENCE_GUIDE.md) · 🇮🇳 [gu](../../../gu/docs/architecture/RESILIENCE_GUIDE.md) · 🇳🇬 [ha](../../../ha/docs/architecture/RESILIENCE_GUIDE.md) · 🇮🇱 [he](../../../he/docs/architecture/RESILIENCE_GUIDE.md) · 🇮🇳 [hi](../../../hi/docs/architecture/RESILIENCE_GUIDE.md) · 🇭🇷 [hr](../../../hr/docs/architecture/RESILIENCE_GUIDE.md) · 🇭🇺 [hu](../../../hu/docs/architecture/RESILIENCE_GUIDE.md) · 🇦🇲 [hy](../../../hy/docs/architecture/RESILIENCE_GUIDE.md) · 🇮🇩 [id](../../../id/docs/architecture/RESILIENCE_GUIDE.md) · 🇳🇬 [ig](../../../ig/docs/architecture/RESILIENCE_GUIDE.md) · 🇮🇹 [it](../../../it/docs/architecture/RESILIENCE_GUIDE.md) · 🇯🇵 [ja](../../../ja/docs/architecture/RESILIENCE_GUIDE.md) · 🇬🇪 [ka](../../../ka/docs/architecture/RESILIENCE_GUIDE.md) · 🇰🇭 [km](../../../km/docs/architecture/RESILIENCE_GUIDE.md) · 🇮🇳 [kn](../../../kn/docs/architecture/RESILIENCE_GUIDE.md) · 🇰🇷 [ko](../../../ko/docs/architecture/RESILIENCE_GUIDE.md) · 🇱🇹 [lt](../../../lt/docs/architecture/RESILIENCE_GUIDE.md) · 🇱🇻 [lv](../../../lv/docs/architecture/RESILIENCE_GUIDE.md) · 🇮🇳 [ml](../../../ml/docs/architecture/RESILIENCE_GUIDE.md) · 🇮🇳 [mr](../../../mr/docs/architecture/RESILIENCE_GUIDE.md) · 🇲🇾 [ms](../../../ms/docs/architecture/RESILIENCE_GUIDE.md) · 🇲🇹 [mt](../../../mt/docs/architecture/RESILIENCE_GUIDE.md) · 🇲🇲 [my](../../../my/docs/architecture/RESILIENCE_GUIDE.md) · 🇳🇵 [ne](../../../ne/docs/architecture/RESILIENCE_GUIDE.md) · 🇳🇱 [nl](../../../nl/docs/architecture/RESILIENCE_GUIDE.md) · 🇳🇴 [no](../../../no/docs/architecture/RESILIENCE_GUIDE.md) · 🇮🇳 [or](../../../or/docs/architecture/RESILIENCE_GUIDE.md) · 🇮🇳 [pa](../../../pa/docs/architecture/RESILIENCE_GUIDE.md) · 🇵🇭 [phi](../../../phi/docs/architecture/RESILIENCE_GUIDE.md) · 🇵🇱 [pl](../../../pl/docs/architecture/RESILIENCE_GUIDE.md) · 🇵🇹 [pt](../../../pt/docs/architecture/RESILIENCE_GUIDE.md) · 🇧🇷 [pt-BR](../../../pt-BR/docs/architecture/RESILIENCE_GUIDE.md) · 🇷🇴 [ro](../../../ro/docs/architecture/RESILIENCE_GUIDE.md) · 🇷🇺 [ru](../../../ru/docs/architecture/RESILIENCE_GUIDE.md) · 🇱🇰 [si](../../../si/docs/architecture/RESILIENCE_GUIDE.md) · 🇸🇰 [sk](../../../sk/docs/architecture/RESILIENCE_GUIDE.md) · 🇸🇮 [sl](../../../sl/docs/architecture/RESILIENCE_GUIDE.md) · 🇷🇸 [sr](../../../sr/docs/architecture/RESILIENCE_GUIDE.md) · 🇸🇪 [sv](../../../sv/docs/architecture/RESILIENCE_GUIDE.md) · 🇰🇪 [sw](../../../sw/docs/architecture/RESILIENCE_GUIDE.md) · 🇮🇳 [ta](../../../ta/docs/architecture/RESILIENCE_GUIDE.md) · 🇮🇳 [te](../../../te/docs/architecture/RESILIENCE_GUIDE.md) · 🇹🇭 [th](../../../th/docs/architecture/RESILIENCE_GUIDE.md) · 🇹🇷 [tr](../../../tr/docs/architecture/RESILIENCE_GUIDE.md) · 🇺🇦 [uk-UA](../../../uk-UA/docs/architecture/RESILIENCE_GUIDE.md) · 🇵🇰 [ur](../../../ur/docs/architecture/RESILIENCE_GUIDE.md) · 🇺🇿 [uz](../../../uz/docs/architecture/RESILIENCE_GUIDE.md) · 🇻🇳 [vi](../../../vi/docs/architecture/RESILIENCE_GUIDE.md) · 🇳🇬 [yo](../../../yo/docs/architecture/RESILIENCE_GUIDE.md) · 🇨🇳 [zh-CN](../../../zh-CN/docs/architecture/RESILIENCE_GUIDE.md) · 🇹🇼 [zh-TW](../../../zh-TW/docs/architecture/RESILIENCE_GUIDE.md)

---

OmniRoute cuenta con tres mecanismos de resiliencia distintos pero relacionados. Cada uno tiene un alcance y propósito diferentes. Manténgalos separados al depurar el comportamiento del enrutamiento.

![Modelo de resiliencia de 3 capas](../diagrams/exported/resilience-3layers.svg)

> Fuente: [diagrams/resilience-3layers.mmd](../diagrams/resilience-3layers.mmd)

## 1. Disyuntor del proveedor

**Alcance:** proveedor completo (p. ej., `glm`, `openai`, `anthropic`).

**Propósito:** dejar de enviar tráfico a un proveedor que falla repetidamente en el nivel ascendente o del servicio.

**Implementación:**

- Clase principal: `src/shared/utils/circuitBreaker.ts`
- Integración: `src/sse/handlers/chatHelpers.ts`, `src/sse/handlers/chat.ts`
- API de estado: `GET /api/monitoring/health`
- API de restablecimiento: `POST /api/resilience/reset`
- Envoltorios: `open-sse/services/accountFallback.ts`
- Tabla de BD: `domain_circuit_breakers`

**Estados:**

- `CLOSED` — se permite el tráfico normal
- `DEGRADED` — el tráfico sigue estando permitido, pero se realiza un seguimiento del aumento de los fallos del proveedor
- `OPEN` — proveedor bloqueado temporalmente; el enrutamiento combinado lo omite
- `HALF_OPEN` — ha transcurrido el tiempo de espera de restablecimiento; se permite una solicitud de prueba

**Valores predeterminados configurables (`open-sse/config/constants.ts`, disponibles en Panel de control → Configuración → Resiliencia):**

| Clase        | Se degrada tras | Se abre tras | Tiempo de espera de restablecimiento |
| ------------ | --------------- | ------------ | ------------------------------------ |
| OAuth        | 5 fallos        | 8 fallos     | 60s                                  |
| Clave de API | 7 fallos        | 12 fallos    | 30s                                  |
| Local        | derivado        | 2 fallos     | 15s                                  |

`degradationThreshold` controla cuándo un proveedor pasa a `DEGRADED`; `failureThreshold` controla cuándo se abre y se omite. Los perfiles de proveedores locales aún no están disponibles en la página de configuración de Resiliencia.

**Códigos de activación:** solo estados de nivel de proveedor `[408, 500, 502, 503, 504]`. NO active el disyuntor por errores de nivel de cuenta (la mayoría de los 401/403/429; estos corresponden al período de enfriamiento o al bloqueo).

**Recuperación diferida:** cuando vence el estado `OPEN`, `getStatus()`, `canExecute()` y `getRetryAfterMs()` actualizan el estado a `HALF_OPEN`. No se necesita ningún temporizador en segundo plano.

---

### Período de enfriamiento global opcional del proveedor (puerta de ventana)

Una cuarta capa **opcional** (`PROVIDER_COOLDOWN_ENABLED`, desactivada de forma predeterminada) mantiene una
memoria entre solicitudes de los proveedores con fallos en
`open-sse/services/providerCooldownTracker.ts`, que se consulta durante la resolución de destinos combinados
para que las solicitudes combinadas consecutivas dejen de volver a recorrer un proveedor que acaba de
fallar. Las entradas de nivel de proveedor respetan la puerta de ventana `PROVIDER_PROFILES`:

| Perfil       | se activa tras (`providerFailureThreshold`) | dentro de (`providerFailureWindowMs`) | se enfría durante (`providerCooldownMs`) |
| ------------ | ------------------------------------------: | ------------------------------------: | ---------------------------------------: |
| OAuth        |                                        `10` |                               `15min` |                                   `5min` |
| Clave de API |                                        `15` |                               `30min` |                                  `10min` |

Por debajo del umbral, el proveedor **no** se considera en enfriamiento; un resultado satisfactorio borra
la ventana. En cambio, las entradas de nivel de conexión (`provider:connectionId`) mantienen el
retroceso exponencial `minRetryCooldownMs → maxRetryCooldownMs`. Anulaciones:
`OMNIROUTE_PROVIDER_BREAKER_{OAUTH,API_KEY}_{FAILURE_THRESHOLD,FAILURE_WINDOW_MS,COOLDOWN_MS}`.
Protección contra regresiones: `tests/unit/provider-cooldown-window-gate.test.ts`.

## 2. Enfriamiento de conexión

**Ámbito:** una sola conexión/cuenta/clave de proveedor.

**Propósito:** omitir una clave defectuosa mientras las demás conexiones del mismo proveedor siguen prestando servicio.

**Implementación:**

- Marcar como no disponible: `src/sse/services/auth.ts::markAccountUnavailable()`
- Selección: `getProviderCredentials*` en el mismo archivo
- Cálculo del enfriamiento: `open-sse/services/accountFallback.ts::checkFallbackError()`
- Configuración: `src/lib/resilience/settings.ts`

**Campos por conexión:**

- `rateLimitedUntil` — marca de tiempo hasta que vence el enfriamiento
- `testStatus: "unavailable"`
- `lastError`, `lastErrorType`, `errorCode`
- `backoffLevel` — contador de espera exponencial

**Enfriamientos predeterminados:**

- Base de OAuth: 5s
- Base de clave de API: 3s
- 429 de clave de API: prioriza los encabezados `Retry-After`/de restablecimiento del servicio ascendente o el texto de restablecimiento que pueda analizarse
- Espera: `baseCooldownMs * 2 ** failureIndex`

**Protección contra avalanchas:** evita que los fallos simultáneos prolonguen excesivamente el enfriamiento o incrementen dos veces `backoffLevel`.

**Estados terminales (NO son enfriamientos):**

- `banned` — establecido por la detección de palabras clave de prohibición/bloqueo de cuenta (consulte [BAN_DETECTION](../security/BAN_DETECTION.md)) y por tres rechazos consecutivos del servicio ascendente por solicitud (`request_rejected`, p. ej., el error 403 de OAuth de Anthropic "Solicitud no permitida" — `open-sse/services/requestRejectedStreak.ts`); un solo rechazo únicamente pone la conexión en enfriamiento
- `expired` (pasa al estado terminal después de un número limitado de reintentos — `EXPIRED_RETRY_MAX = 3` con espera exponencial —, de modo que los errores transitorios de OAuth puedan resolverse por sí solos antes de que la cuenta se desactive permanentemente)
- `credits_exhausted`

Estos persisten hasta que cambien las credenciales o un operador los restablezca. No sobrescriba los estados terminales con un estado de enfriamiento transitorio.

**Recuperación diferida:** cuando `rateLimitedUntil` queda en el pasado, la conexión vuelve a ser apta. Tras un uso correcto, `clearAccountError()` borra todos los campos de error.

### Afinidad de sesión (#7274)

**Ámbito:** una sesión de cliente (`X-Session-Id` / `x-codex-session-id` / encabezado `x-omniroute-session`) fijada a una conexión para **cualquier** proveedor.

**Propósito:** mantener un agente de varios turnos (Claude Code, aider, agentes personalizados) en la misma cuenta entre solicitudes, lo que reduce la pérdida de contexto entre cuentas y los errores 429 repetidos de arranque en frío en proveedores con estado de sesión por cuenta.

**Implementación:**

- Resolución del TTL: `src/sse/services/sessionAffinityPin.ts::resolveSessionAffinityTtlMs()`
- Selección/creación de la fijación: `src/sse/services/sessionAffinityPin.ts::selectSessionAffinityConnection()`
- Extracción del encabezado (genérica, para cualquier proveedor): `src/sse/services/auth.ts::extractSessionAffinityKey()`
- Tabla de fijaciones persistentes: `sessionAccountAffinity` (`src/lib/db/sessionAccountAffinity.ts`)
- Configuración: `sessionAffinityTtlMs` (TTL global en ms, `0` lo desactiva) — `src/lib/db/settings.ts`. Se cambió el nombre del parámetro exclusivo de Codex `codexSessionAffinityTtlMs` mediante la migración `124_generic_session_affinity_ttl.sql`, que conserva cualquier TTL de Codex configurado previamente como nuevo valor predeterminado.

Antes de #7274, `resolveSessionAffinityTtlMs()` devolvía inmediatamente `0` para todos los proveedores excepto `codex`, por lo que la configuración del TTL (y los encabezados de sesión) no tenía efecto en ningún otro lugar, aunque el mecanismo de fijación y la extracción de encabezados ya eran independientes del proveedor. La corrección eliminó ese retorno anticipado; ahora el TTL se aplica uniformemente a todos los proveedores una vez establecido globalmente por encima de `0`.

Los tres encabezados de afinidad de sesión nunca se reenvían al servicio ascendente: los ejecutores construyen desde cero sus propios encabezados para el servicio ascendente en lugar de transmitir los encabezados del cliente, por lo que esto sigue siendo únicamente un identificador interno de correlación.

### Arrendamientos exclusivos de conexiones para sesiones administradas

**Ámbito:** un cliente/sesión HTTP administrado activo posee una conexión apta de OmniRoute.

**Propósito:** proporcionar la propiedad exclusiva y duradera de una conexión a los clientes que necesiten una barrera estricta de enrutamiento
entre solicitudes. Esto difiere de la afinidad de sesión, que es una preferencia flexible de continuidad:
un arrendamiento exclusivo conserva el estado del ciclo de vida en SQLite, exige la unicidad global del propietario activo y de la
conexión activa, y rechaza una generación obsoleta antes de despachar al proveedor.

La función es opcional para cada clave de API. Una clave administrada debe tener el ámbito `lease:exclusive` y una
lista `allowedConnections` explícita y no vacía. Cualquier cliente HTTP puede usar el extremo del ciclo de vida; no se
requiere ningún nombre de cliente, agente de usuario, proveedor, método OAuth ni modelo. El arrendamiento posee una conexión,
no un modelo, por lo que un cambio de modelo conserva la vinculación mientras la conexión siga siendo
apta según los criterios habituales. Las reglas normales de modelo, cuota, estado, enfriamiento y lista de permitidos siguen siendo vinculantes y pueden
transferir la misma generación a otra conexión apta que esté libre.

El ciclo de vida es `POST /api/v1/session-leases` con las acciones JSON `acquire`, `renew` y `release`.
Las solicitudes de inferencia administradas presentan el valor opaco `X-OmniRoute-Lease-Owner` y el valor exacto
`X-OmniRoute-Lease-Generation`. El propietario usa `vlo_` seguido de 43 caracteres base64url; solo
se almacena su hash SHA-256. Cada barrera final de despacho también vincula el ID de la clave de API autenticada y
el ID de la conexión activa. Los encabezados de control del arrendamiento se eliminan de los registros, de las instantáneas conservadas de las solicitudes y de
los encabezados de los ejecutores del servicio ascendente.

Si el enrutamiento ordinario tiene candidatos administrados aptos, pero todos los candidatos libres están ocupados por un
arrendamiento activo ajeno, OmniRoute devuelve el estado HTTP `429`, un código de capacidad de arrendamiento no disponible, un
estado de espera de capacidad y un valor `Retry-After` acotado y derivado del vencimiento pertinente más próximo.
La ausencia ordinaria de conexiones aptas no constituye una contención de arrendamientos y conserva la semántica existente de los errores de enrutamiento.

Los mecanismos relacionados siguen siendo independientes:

- La ocupación de sesiones OAuth es una distribución flexible de cuentas OAuth local al proceso.
- Los semáforos de cuenta conceden permisos de concurrencia de solicitudes y terminan cuando finaliza una solicitud.
- Los arrendamientos exclusivos de conexiones para sesiones administradas constituyen una propiedad duradera durante el ciclo de vida con una barrera de generación.

---

## 3. Bloqueo de modelos

**Ámbito:** combinación de proveedor + conexión + modelo.

**Ámbito de la clave según el estado:** el estado del fallo determina en qué clave se escribe un bloqueo
(`resolveLockoutScope()` en `open-sse/services/accountFallback/exactModelLock.ts`):

- `429` / `403` / `402` — una señal de cuota o autorización — bloquean la **familia de cuota**:
  para codex, todo el ámbito `codex` / `spark` (todos los modelos `gpt-5*` de la
  conexión); para otros proveedores, `getQuotaScopedModelForProvider()`.
- `404` bloquea el modelo individual (`getModelLockKey()` restringe `not_found`).
- Cualquier otro estado — fallos de transporte/servidor `5xx` y el `502`
  sintetizado por OmniRoute a partir de la validación de calidad — bloquea únicamente la
  combinación **exacta** de proveedor/conexión/modelo. Un flujo defectuoso en un modelo no constituye
  evidencia sobre la cuota de la cuenta; antes de esta regla, una respuesta vacía en
  `codex/gpt-5.6-luna` eliminaba del enrutamiento todos los modelos `gpt-5*` de esa conexión
  durante 2–30 min (con escalado), aunque su cuota no se hubiera visto afectada.
- La opción `scope` explícita del llamador siempre prevalece (Antigravity pasa `"exact"`).

**Propósito:** evitar deshabilitar una conexión completa cuando solo un modelo no está disponible o tiene la cuota limitada.

**Ejemplos:**

- Proveedores con cuota por modelo que devuelven 429
- Proveedores locales que devuelven 404 para un único modelo ausente
- Fallos de permisos específicos del proveedor para un modo/modelo (p. ej., modos de Grok)

**Implementación:** `open-sse/services/accountFallback.ts` — `lockModel()`, `clearModelLock()`, `getAllModelLockouts()`.

### Panel de tiempos de espera de modelos (v3.8.0)

IU: Configuración → Tiempos de espera de modelos (`src/app/(dashboard)/dashboard/settings/components/ModelCooldownsCard.tsx`)

Enumera los bloqueos activos con: proveedor, conexión, modelo, motivo y expiresAt. Los operadores pueden volver a habilitar manualmente un modelo desde la tarjeta.

**API REST:**

- `GET /api/resilience/model-cooldowns` — enumera los bloqueos activos
- `DELETE /api/resilience/model-cooldowns` — rehabilitación manual. Cuerpo: `{provider, connection, model}`. Autenticación: administración.

### IU de configuración de bloqueos + recuperación por reducción tras éxitos (v3.8.23)

El bloqueo de modelos pasó de ser un comportamiento codificado y siempre activo a una función
opcional y completamente configurable, con su propia tarjeta de configuración y una ruta de recuperación autorreparable.

**Tarjeta de configuración:** Configuración → Bloqueo de modelos
(`src/app/(dashboard)/dashboard/settings/components/ModelLockoutCard.tsx`).
Esta es **diferente** de la tarjeta de solo lectura `ModelCooldownsCard` anterior (que únicamente
_enumera_ los bloqueos activos): la nueva tarjeta _configura los parámetros_. Los valores predeterminados
se encuentran en `DEFAULT_MODEL_LOCKOUT_SETTINGS`
(`src/lib/resilience/modelLockoutSettings.ts`):

| Configuración           | Valor predeterminado             | Significado                                                                                |
| ----------------------- | -------------------------------- | ------------------------------------------------------------------------------------------ |
| `enabled`               | `false`                          | Interruptor principal: el bloqueo de modelos está **desactivado de forma predeterminada**. |
| `errorCodes`            | `[403, 404, 429, 502, 503, 504]` | Estados del servicio ascendente que cuentan como un fallo específico del modelo.           |
| `baseCooldownMs`        | `120_000` (120 s)                | Duración inicial del bloqueo para el primer fallo.                                         |
| `maxCooldownMs`         | `1_800_000` (30 min)             | Límite máximo del tiempo de espera escalado.                                               |
| `maxBackoffSteps`       | `10`                             | Número máximo de pasos de escalado con retroceso exponencial.                              |
| `useExponentialBackoff` | `true`                           | Indica si los fallos repetidos aumentan exponencialmente el tiempo de espera.              |

La configuración se conserva mediante el almacén de configuración habitual y se valida mediante el
esquema de configuración de resiliencia; la tarjeta limita `baseCooldownMs`/`maxCooldownMs`
(con `maxCooldownMs ≥ baseCooldownMs`) y `maxBackoffSteps`.

**Recuperación por reducción tras éxitos:** la recuperación **no** depende exclusivamente de que expire el temporizador. Una respuesta
correcta reduce progresivamente el recuento de fallos del modelo, de modo que un modelo que se haya recuperado
durante el intervalo deje de escalar (y se desbloquee) antes de que termine su temporizador. Cuando un
destino combinado responde correctamente, `open-sse/services/combo.ts` llama a `decayModelFailureCount()`
(`open-sse/services/accountFallback.ts`), que reduce a la **mitad** el
`failureCount` almacenado (`Math.floor(failureCount / 2)`); cuando llega a `0`, la entrada
de bloqueo se elimina por completo. La función complementaria `recordModelLockoutFailure()`
incrementa el recuento (y aumenta el tiempo de espera) en los fallos que ocurren dentro del
intervalo de escalado. Esta reducción tras éxitos se suma a la expiración normal del temporizador:
cualquiera de las dos vías puede volver a habilitar un modelo.

**Estado:** los bloqueos se mantienen **en memoria** (`Map`s de
`ModelLockoutEntry` por proceso, indexados mediante `provider:connectionId:model`; los bloqueos de ámbito exacto,
mediante `provider:connectionId:exact:model`) y no se conservan en
la base de datos, por lo que se pierden al reiniciar. La _configuración_ sí se conserva; el
_estado_ de los bloqueos activos es efímero.

---

## 4. Control de concurrencia de cuota compartida (v3.8.36)

Las cuentas de suscripción (GLM, MiniMax, etc.) suelen aceptar solo entre ~1 y 3
solicitudes simultáneas; superar ese límite provoca errores 429 y períodos de espera. Esto resulta especialmente grave con
combinaciones de **cuota compartida** (`qtSd/…`), en las que varias claves de API comparten una misma
cuenta ascendente. Tres capas evitan que una cuenta compartida se sature.

### Límite de concurrencia por conexión (`max_concurrent`)

Cada conexión de proveedor puede declarar un límite máximo `max_concurrent`
(`provider_connections.max_concurrent`, configurado en el modal de conexión, la API o la base de datos).
Déjelo vacío para no aplicar ningún límite. Este es el único parámetro que controla la capa de serialización
descrita a continuación: establézcalo en la concurrencia real de la cuenta (p. ej., GLM ~1, MiniMax ~2).

### Serialización de solicitudes de cuota compartida

Cuando un envío de cuota compartida se dirige a una conexión que declara un valor positivo de
`max_concurrent`, las solicitudes simultáneas a esa **cuenta** se serializan mediante un
semáforo por conexión (clave `qsconn:<connectionId>`): las solicitudes excedentes **esperan en
la cola** en lugar de saturar la cuenta. Tiene un comportamiento **fail-open**: si la
cola está saturada o se agota el tiempo de espera, la solicitud continúa sin una plaza en lugar de rechazar jamás una
solicitud que pueda enviarse. Se activa o desactiva en **Configuración → Resiliencia → Concurrencia por conexión
de cuota compartida** (`resilienceSettings.quotaShareConcurrencyLimit.enabled`, activada
de forma predeterminada). Sin un límite `max_concurrent`, el comportamiento no cambia.

> La compuerta de enrutamiento de cuota compartida (`selectQuotaShareTarget`, DRR + P2C) también es
> fail-open y solo _reduce la prioridad_ de una conexión que haya alcanzado su límite; con un
> grupo de una sola conexión no puede imponer un límite estricto, por lo que este semáforo es el que realmente
> contiene la saturación.

### Reintento de combinaciones con reconocimiento del período de espera

Para cada estrategia de combinación (cuando está activada), una solicitud que consolidaría un error 429
debido a un período de espera transitorio BREVE espera a que finalice y vuelve a enviarse en lugar de
devolver el error 429; esto cubre las ventanas TPM/RPM de la clase Gemini (~60 s según retry-after)
en combinaciones de varios modelos, por ejemplo, cuando ambos destinos de una combinación de 2 modelos alcanzan un límite
de frecuencia por modelo. Está acotado por `comboCooldownWait` (`enabled`, `maxWaitMs`, `maxAttempts`,
`budgetMs`) en **Configuración → Resiliencia**. Nunca espera por `quota_exhausted`
(bloqueado hasta medianoche) ni por motivos de autenticación o recurso no encontrado.

---

## 5. Control de admisión de la cola de solicitudes (v3.8.49 · incidencia #6593)

**Ámbito**: la cola local de límites de frecuencia por proveedor+conexión (`open-sse/services/rateLimitManager.ts`,
respaldada por Bottleneck), una capa por debajo de los tres mecanismos anteriores.

**`maxWaitMs` es un nombre persistente heredado para la expiración de la ejecución.**
`resilienceSettings.requestQueue.maxWaitMs` se pasa a Bottleneck como la propiedad
`expiration` de un trabajo, cuyo temporizador solo se inicia después del envío. Por lo tanto, limita
la ejecución administrada por el limitador, no el tiempo empleado en la cola local. La expiración se
expone como el `code: "RATE_LIMIT_EXECUTION_TIMEOUT"` local de confianza (HTTP 504);
el nombre anterior del código de tiempo de espera de la cola solo se acepta para mantener la compatibilidad
interna retroactiva de confianza. El valor predeterminado es 15000ms; puede sobrescribirse mediante
`RATE_LIMIT_MAX_WAIT_MS` (variable de entorno) o el panel (**Configuración → Resiliencia**,
límite de la interfaz de usuario de 1–30000ms). La permanencia en la cola no tiene un límite de tiempo; utilice
`maxQueueDepth` a continuación para limitar las solicitudes en cola.

**`maxQueueDepth`: límite de admisión opcional (nuevo).** `resilienceSettings.requestQueue.maxQueueDepth`
limita cuántas solicitudes pueden permanecer en cola (todavía sin enviar) simultáneamente para una
combinación de proveedor+conexión. Cuando la cola ya contiene `maxQueueDepth`
solicitudes, una nueva solicitud se rechaza inmediatamente con un error tipado
`code: "RATE_LIMIT_QUEUE_FULL"` **antes** de que llegue a `limiter.schedule()`;
por lo tanto, el rechazo tiene un coste bajo y ocurre antes de cualquier trabajo posterior de
compresión o traducción del prompt para esa solicitud. El valor predeterminado `0` =
desactivado, lo que conserva el comportamiento existente de cola sin límites; intervalo permitido: 0–100000.
Puede sobrescribirse mediante `RATE_LIMIT_MAX_QUEUE_DEPTH` (variable de entorno) o
`resilienceSettings.requestQueue.maxQueueDepth` (parche del panel o la API).

La propia comprobación de admisión es una función pura
(`open-sse/services/rateLimitManager/admission.ts::checkQueueAdmission`), por lo que
puede someterse a pruebas unitarias sin un limitador Bottleneck real.

> El RFC que abrió la incidencia #6593 también propuso una marca `bypassCompressionOnRateLimit`.
> La canalización `open-sse/services/compression/` de este repositorio realiza
> la compresión del prompt/contexto en la solicitud saliente al LLM (`chatCore.ts`,
> alrededor del bloque `resolveCompressionSettings`/`selectCompressionStrategy`),
> no la compresión de respuestas HTTP en cuerpos 429 sintetizados; no existe una
> ruta de código correspondiente para una marca de omisión literal. Ese paso de compresión del prompt
> también se ejecuta actualmente _antes_ de `withRateLimit()` en la canalización de solicitudes, por lo que
> cambiar el orden para omitirlo ante un rechazo por cola llena constituye un cambio independiente y de mayor
> alcance que el de esta incidencia; **no** se implementó aquí intencionadamente
> y se dejó como tarea posterior por si el ahorro de CPU compensa el
> riesgo de cambiar el orden.

---

## 6. Vigilante de rendimiento de flujos lentos (#9709)

La protección opcional `resilienceSettings.streamRecovery.throughputWatchdog` detecta
un upstream que sigue enviando fragmentos, pero genera una salida del asistente por
debajo de la tasa configurada de salida útil. Es deliberadamente distinta del tiempo
de espera por inactividad: los latidos y los metadatos no reinician ninguno de los
temporizadores ni cuentan como progreso. También es distinta del plazo máximo
absoluto del intento (#9153), que sigue siendo un límite de seguridad absoluto,
independientemente de la calidad de la salida.

El vigilante requiere un período de calentamiento seguido de una ventana móvil
completa antes de poder abortar. Cuenta los deltas de texto de los eventos de salida
de Chat Completions y Responses API (una aproximación conservadora en bytes UTF-8),
ignora los eventos vacíos y los que solo contienen datos de uso, y suspende la
evaluación mientras haya eventos de llamadas a herramientas o de razonamiento en
curso. Está deshabilitado de forma predeterminada y puede habilitarse con
`STREAM_THROUGHPUT_WATCHDOG_ENABLED=true`; la ventana, el calentamiento, la tasa
mínima y la salida mínima medible están acotados por la capa normal de normalización
de la configuración de resiliencia.

Cuando está habilitado, una cancelación del vigilante se aplica únicamente al intento
upstream activo. Antes de que haya bytes visibles para el cliente, la ruta existente
de recuperación temprana dentro de la misma cuenta puede volver a abrir el intento.
Después de la confirmación, el flujo nunca se reproduce de nuevo a ciegas; solo el
contrato existente de continuación segura a mitad del flujo puede empalmar un sufijo.
La finalización sigue ejecutándose una sola vez, por lo que ni la contabilización del
uso ni la liberación del semáforo se duplican.

---

## 7. Reformulación del estado upstream (errores de cuota con estado incorrecto)

**Alcance:** un gateway upstream que informa del agotamiento temporal de la cuota con un estado HTTP incorrecto.

**Propósito:** corregir un estado engañoso ANTES de la clasificación, de modo que los consumidores downstream (el motor de fallback, la agregación combinada y la respuesta enviada al cliente) perciban la verdadera naturaleza reintentable del fallo.

Algunos gateways indican el agotamiento TEMPORAL de la cuota mediante un estado
HTTP no reintentable. `agentrouter.org` devuelve `403` (a veces `400`) con un cuerpo
en chino (`用户额度不足` / `额度不足`) en lugar del `429` estándar. Los clientes como
Claude Code tratan `403` como permanente y abortan la sesión; sin la corrección,
el motor de fallback lo clasificaría como `AUTH_ERROR` en lugar de como un evento
de cuota.

**Implementación:**

- Registro + comparador: `open-sse/config/upstreamStatusRestatement.ts` — una
  lista de reglas por proveedor (`{id, fromStatuses, toStatus, textMarkers,
excludeMarkers, defaultRetryAfterMs}`), evaluadas mediante `applyStatusRestatement()`.
- Punto de llamada: el bloque `providerFailure:` de `open-sse/handlers/chatCore.ts`
  (alrededor de la línea 3654), justo después de que `parseUpstreamError()` analice
  una respuesta upstream con un estado HTTP de error (`!providerResponse.ok`) y antes
  de que se ejecute cualquier clasificación, de modo que todos los consumidores
  downstream vean el estado corregido. Los errores incrustados dentro de un flujo
  SSE `200` siguen una ruta posterior y separada de análisis del flujo y **no** están
  cubiertos actualmente por este hook; se trata de una limitación conocida, que aún
  no es necesaria para el estado incorrecto de agentrouter (que aparece como un
  estado HTTP de error).
- Elegibilidad para reintentos: `429` está incluido en `RETRY_AFTER_ELIGIBLE_STATUSES`
  (`open-sse/services/combo/unavailableRetryGate.ts`), por lo que un error reformulado
  incluye una ventana de reintento real en lugar de presentarse como un `403` sin
  posibilidad de recuperación.
- El `60s` sintético de `defaultRetryAfterMs` (`upstreamStatusRestatement.ts`) es
  únicamente lo que la respuesta reformulada comunica al **cliente**; no constituye
  por sí mismo la duración interna de enfriamiento/bloqueo de la conexión, que se rige
  por separado mediante el mecanismo que gestione realmente el error reformulado
  (el backoff creciente de Connection Cooldown, §2, con una base de `3s` para
  proveedores de claves de API; o Model Lockout, §3, para proveedores con cuota por
  modelo como agentrouter). El router puede volver a ser elegible internamente para
  reintentar antes de la ventana de 60s que anuncia al cliente; se trata de un margen
  intencionado, no de un error.

Los errores permanentes (`无权访问模型` de agentrouter — sin acceso a este modelo)
NUNCA se reformulan: `excludeMarkers` veta la regla incluso cuando hay una
coincidencia con `textMarkers`, por lo que el error conserva su estado original y
nada intenta repetirlo indefinidamente. La regla de clasificación de proveedor
correspondiente (`agentrouter-model-access-denied` en
`open-sse/config/providerErrorRules.ts`: `reason: "auth_error"`, `scope: "model"`,
un enfriamiento base declarado de `6h`) es consultada por `checkFallbackError`
(`open-sse/services/accountFallback.ts`) _antes_ del retorno anticipado genérico
`FORBIDDEN` de la categoría apikey, condicionado a `honorsRuleLockScope(provider)`
(#10334 — actualmente exclusivo de agentrouter mediante la lista de permitidos
`HONORS_RULE_LOCK_SCOPE_PROVIDERS` de `providerErrorRules.ts`). El enfriamiento
declarado de 6h de la regla se transmite como `fallbackResult.baseCooldownMs`, pero
sigue alimentando la ruta preexistente de bloqueo por cuota por modelo
(`lockModelIfPerModelQuota()` / `recordModelLockoutFailure()`, sin cambios por
#10334 salvo por el origen del enfriamiento): se limita al valor de
`mlSettings.maxCooldownMs` del operador (de forma predeterminada,
`1_800_000ms` / 30min), como cualquier otro bloqueo de modelo, y el _motivo de
bloqueo persistido_ sigue siendo el valor preexistente codificado de forma fija
`"forbidden"`, no el valor `"auth_error"` de la regla; solo se respeta de extremo
a extremo la duración del enfriamiento, no la cadena del motivo. La propia conexión
permanece activa; los modelos hermanos de la misma conexión no se ven afectados.

Los errores de cuota reformulados (`额度不足`) alcanzan una regla de proveedor en producción
(`agentrouter-user-quota-exhausted`: `reason: "quota_exhausted"`, `scope:
"connection"`, sin un tiempo de espera declarado propio; se aplica el valor
predeterminado de retroceso escalado de la capa de persistencia). Desde #10334,
`scope` en `ProviderErrorRuleMatch` SE consume de extremo a extremo, pero
**solo** para los proveedores incluidos en la lista de permitidos
`HONORS_RULE_LOCK_SCOPE_PROVIDERS` (`providerErrorRules.ts`; actualmente solo
`"agentrouter"`, controlado mediante `honorsRuleLockScope()`). Para cualquier
otro proveedor, `scope` sigue siendo informativo, exactamente igual que antes
de #10334. `checkFallbackError` expone el ámbito de la regla coincidente como
`fallbackResult.ruleScope`; `isAgentrouterConnectionQuotaScope()`
(`src/sse/services/auth.ts`) es la protección compartida que confirma que un
`ruleScope` es realmente seguro de respetar como una señal autorrecuperable
para toda la conexión (ámbito `"connection"`, motivo `quota_exhausted`, nunca
`permanent`, nunca `creditsExhausted`; una defensa contra una futura regla que
combine el ámbito `"connection"` con un estado permanente de la cuenta). Dos
consumidores la invocan:

- **Persistencia** (`markAccountUnavailable()`, `src/sse/services/auth.ts`):
  en lugar de entrar en la rama de bloqueo **por modelo** del proveedor de
  paso directo (agentrouter tiene `passthroughModels: true` →
  `hasPerModelQuota()` devuelve `true`), aplica un **tiempo de espera temporal
  de la conexión**: `testStatus: "unavailable"` + `rateLimitedUntil`, nunca un
  estado terminal (`credits_exhausted`/`banned`/`expired`), de modo que la
  conexión se recupera automáticamente una vez transcurrido el tiempo de
  espera, en vez de requerir un restablecimiento manual de las credenciales.
  Se omite para conexiones con `disableCooling: true` (#2997): esa exclusión
  voluntaria pasa en su lugar al bloqueo por modelo (una contrapartida
  documentada; consulte el comentario del código situado encima de la rama).
- **Enrutamiento combinado de la misma solicitud** (`applyComboTargetExhaustion()`,
  `open-sse/services/combo/targetExhaustion.ts`): la misma protección añade la
  conexión al conjunto en memoria `exhaustedConnections`, con la clave
  `${provider}:${connectionId}`. Esto solo omite un destino restante DE LA
  MISMA SOLICITUD que _ya contiene exactamente ese `connectionId`_ en su propio
  objeto de destino (`getExhaustedTargetSkipReason()`,
  `open-sse/services/combo/comboPredicates.ts`, `if (provider &&
connectionId)` antes de la consulta de `exhaustedConnections`); una
  combinación simple de listas de modelos, en la que los destinos hermanos no
  contienen ningún `connectionId` fijado propio y solo se resuelve uno por
  envío a partir de la cabecera `X-OmniRoute-Selected-Connection-Id` de la
  respuesta, nunca coincide con esa clave. Para ese caso habitual, la
  protección real contra la reutilización de la cuenta que acaba de agotarse
  por parte de un tramo restante NO es este conjunto, sino la capa de
  persistencia anterior (el `rateLimitedUntil` de la conexión está ahora en el
  futuro), combinada con la supresión, mediante esta misma protección, de
  `transientRateLimitedProviders` para el fallo (consulte «Diseño en dos
  etapas» y el comentario del código sobre la rama
  `isAgentrouterConnectionQuotaScope` en `targetExhaustion.ts`): al no marcarse
  ese conjunto, la autorización forzada de `allowRateLimitedConnection` en
  `combo.ts` (`open-sse/services/combo.ts:1005-1013`, `:2734-2738`) NO se
  activa para los tramos restantes del proveedor, por lo que el filtro
  `rateLimitedUntil` de la selección de credenciales
  (`src/sse/services/auth.ts:1238`) se respeta normalmente y un tramo restante
  selecciona otra conexión de agentrouter que siga siendo apta o falla porque
  no hay credenciales disponibles; no fuerza su regreso a la conexión que
  esta rama acaba de poner en espera.

### Diseño en dos etapas: reformulación del estado y, después, clasificación

La reformulación del estado (`upstreamStatusRestatement.ts`) y las reglas de
clasificación de proveedores (`open-sse/config/providerErrorRules.ts`,
`providerRuleRegistry`) son registros separados que usan como claves tanto el
identificador del proveedor como marcadores de texto, pero se ejecutan en
lugares distintos y cumplen propósitos diferentes: la reformulación
reescribe el estado HTTP al principio de `chatCore.ts`; las reglas de
clasificación eligen el `reason` de respaldo y el `scope` del bloqueo
(`model` / `provider` / `connection`) dentro de `checkFallbackError()`
(`open-sse/services/accountFallback.ts`).

Las reglas de clasificación solo ven el **texto** completo del error
(necesario para hacer coincidir marcadores del cuerpo como `额度不足`) en el
caso de los proveedores incluidos en la lista de permitidos
`FULL_TEXT_RULE_PROVIDERS` de `providerErrorRules.ts`; actualmente solo
`"agentrouter"`. Para cualquier otro proveedor del **catálogo integrado**,
`checkFallbackError` únicamente pasa a `getProviderErrorRuleMatch` el error
estructurado (`{code, type}`), que basta para las reglas basadas en
cabeceras/estado/código, pero no puede detectar marcadores de texto del
cuerpo. La función auxiliar `resolveRuleMatchBody()` realiza esta selección:
el texto completo del error para los proveedores incluidos en la lista de
permitidos y, para los demás, el error estructurado. Añadir un proveedor
**integrado** a `FULL_TEXT_RULE_PROVIDERS` supone una adhesión explícita por
proveedor; existe para que la ruta predeterminada de todos los proveedores
que no estén en la lista permanezca idéntica byte por byte.

El `scope` de una regla (`model` / `provider` / `connection`) constituye una
adhesión independiente de `FULL_TEXT_RULE_PROVIDERS`: `checkFallbackError`
solo lo expone como `fallbackResult.ruleScope`, y los consumidores posteriores
solo lo respetan como algo distinto de una etiqueta informativa para los
proveedores incluidos en la lista de permitidos
`HONORS_RULE_LOCK_SCOPE_PROVIDERS` del mismo archivo (controlado mediante
`honorsRuleLockScope()`; actualmente solo `"agentrouter"`). Consulte «Errores
de cuota reformulados» más arriba para saber qué hace realmente una
coincidencia con `scope: "connection"` una vez que un proveedor está incluido
en esa lista de permitidos.

**#11104 — las reglas declaradas por el operador omiten ambas listas de permitidos.** Un operador puede
declarar una regla por proveedor en tiempo de ejecución mediante `settings.providerErrorRules`
(`open-sse/config/providerErrorRules.ts::setOperatorProviderErrorRules`)
sin editar este archivo. Condicionar una regla del operador a
`FULL_TEXT_RULE_PROVIDERS`/`HONORS_RULE_LOCK_SCOPE_PROVIDERS` —listas de permitidos
destinadas a proteger el comportamiento **predeterminado** de las reglas integradas del catálogo—
haría que el mecanismo de configuración quedara inerte para todos los proveedores salvo los que ya
figuran allí, puesto que declarar la regla ya constituye la adhesión explícita
del operador. `resolveRuleMatchBody()` y `honorsRuleLockScope()` comprueban
primero `hasOperatorRuleForProvider()`: un proveedor con una regla del operador recibe
el texto sin procesar del error y se respeta su `scope` declarado, independientemente de
si también aparece en alguna de las listas de permitidos.

**Limitación conocida — `providerRuleRegistry` nunca se consulta para HTTP 400.**
La rama `BAD_REQUEST` de `checkFallbackError` clasifica el estado 400 por completo
mediante sus propios arrays de patrones (`MODEL_ACCESS_DENIED_PATTERNS`,
`CONTEXT_OVERFLOW_PATTERNS`, etc. en `accountFallback.ts`) y retorna antes de
alcanzar la rama `configuredRule`/`getProviderErrorRuleMatch` situada encima.
Una regla integrada del catálogo (o una regla del operador) con `status: 400` es
sintácticamente válida, pero nunca se activará. Actualmente, ninguna regla existente se aplica a 400,
por lo que nada en producción se ve afectado; pero una futura regla para 400 requerirá modificar
primero esta rama, lo cual supone un cambio mayor que añadir una regla (reclasifica el 400 para
todos los proveedores que ya dependen del comportamiento basado en arrays de patrones)
y queda fuera del alcance de añadir una regla para un único proveedor.

### Añadir un nuevo gateway que informa incorrectamente sobre la cuota

1. Registre un array de reglas en `statusRestatementRegistry`
   (`open-sse/config/upstreamStatusRestatement.ts`). Mantenga los `textMarkers`
   específicos del proveedor; nunca reutilice frases genéricas en inglés que colisionen con
   `CREDITS_EXHAUSTED_SIGNALS` (`open-sse/services/accountFallback.ts`).
2. Opcionalmente, registre reglas de clasificación en
   `open-sse/config/providerErrorRules.ts` (`providerRuleRegistry`) para seleccionar
   el ámbito de bloqueo adecuado (`connection` para una cuota aplicable a toda la cuenta, `model` para
   errores por modelo). Este paso solo surte efecto en producción para
   proveedores cuyas reglas necesiten el texto completo del error (marcadores del cuerpo): añada el
   id del proveedor a `FULL_TEXT_RULE_PROVIDERS` en el mismo archivo; de lo contrario,
   `checkFallbackError` únicamente entrega a la regla el error estructurado
   `{code, type}` y una regla basada en el texto del cuerpo nunca coincidirá con el tráfico real.
   Las reglas que coinciden únicamente con `status`/`headers` (como las de Opencode o
   Minimax) no necesitan esta adhesión. Por separado, si la regla declara
   `scope: "connection"` y se pretende aplicar un periodo de espera realmente válido para toda la conexión,
   además de omitir la combinación en la misma solicitud (y no solo una etiqueta informativa), añada el
   id del proveedor a `HONORS_RULE_LOCK_SCOPE_PROVIDERS` en el mismo archivo; esto
   es lo que habilita el consumo al estilo de `isAgentrouterConnectionQuotaScope()` en
   `markAccountUnavailable()` (`src/sse/services/auth.ts`) y
   `applyComboTargetExhaustion()`
   (`open-sse/services/combo/targetExhaustion.ts`); sin ello, `scope`
   se sigue propagando mediante `fallbackResult.ruleScope`, pero nada actúa sobre él.
3. Añada pruebas unitarias siguiendo el modelo de `tests/unit/upstream-status-restatement.test.ts`
   y `tests/unit/agentrouter-error-rules.test.ts` (incluidas las
   protecciones not-permanent / not-creditsExhausted y, si el proveedor necesita
   la lista de permitidos, una prueba que confirme que `resolveRuleMatchBody()` devuelve el
   texto completo únicamente para ese proveedor).

No es necesario realizar cambios en `chatCore.ts`, `classifyError` ni en combo.

#### Bloqueo agrupado por egreso (#10880)

Los proveedores de `EGRESS_BUCKETED_LOCK_PROVIDERS` (familia opencode) se tratan
como proveedores ascendentes agrupados por IP (el nivel gratuito de opencode está agrupado por IP, no
por cuenta; consulte #9611): un estado 429 clasificado como `quota_exhausted`
**o** `rate_limit_exceeded` aplica un periodo de espera a todas las conexiones de la familia incluida en la lista de permitidos
cuya última IP de egreso conocida coincida con la de la conexión que presenta el fallo, antes de que
la rotación pueda probarlas,
evitando así N-1 llamadas ascendentes con fallo garantizado (la misma forma que #10460/#10525).
`rate_limit_exceeded` se incluye deliberadamente: en la ruta `markAccountUnavailable`,
las reglas específicas de opencode nunca coinciden (no se pasan encabezados ni cuerpo a
`checkFallbackError`, y opencode no está en `FULL_TEXT_RULE_PROVIDERS`), por lo que un 429
cuyo cuerpo contiene el texto de cuota de suscripción ("monthly usage limit
reached") se clasifica como `quota_exhausted` mediante el fallback de texto de cuota
(`buildSubscriptionQuotaFallback`, `accountFallback.ts`; periodo de espera de 1 h) antes de
alcanzar la regla `status_429`, mientras que un 429 sin texto de cuota (simple
limitación de frecuencia) se clasifica mediante la regla `status_429` como `rate_limit_exceeded`
y aun así aplica el periodo de espera a la familia de IP. Para un proveedor incluido en la lista de permitidos, un límite
de frecuencia agrupado por IP constituye la misma señal que una cuota agotada. Límites reales:

- **Mejor esfuerzo**: el bloqueo determina la última `egress_ip` conocida de la
  conexión a partir de `proxy_logs` (ventana de 24h, síncrono, sin caché). Una
  caché fría (la IP de salida nunca se sondeó) o la ausencia de una fila → la
  rama sigue aplicando el enfriamiento a la conexión que falla (registrado como
  hasta ahora), pero no se bloquea ninguna conexión hermana.
- **Nunca terminal**: el enfriamiento es una ventana de cuota renovable
  (`testStatus: "unavailable"`); nunca se deriva un estado permanente de una
  señal a nivel de IP. Las conexiones `disableCooling` omiten la rama por
  completo.
- **La granularidad del bloqueo cambia para la familia incluida en la lista de permitidos**:
  se trata de un cambio de ámbito, no solo de una optimización para conexiones
  hermanas. opencode es un proveedor `passthroughModels`, por lo que antes de
  esta rama un 429 producía un bloqueo por MODELO; ahora produce un enfriamiento
  de la conexión, incluso para un operador que ejecuta una única conexión sin
  ninguna conexión hermana. Esa es la granularidad que la tabla de reglas de
  opencode ya declara correcta (`scope: "connection"`,
  `providerErrorRules.ts`), pero que hasta ahora nunca se respetó porque
  opencode no está en `HONORS_RULE_LOCK_SCOPE_PROVIDERS`. La rama escribe por
  sí misma el enfriamiento + `backoffLevel` de la conexión que falla, reflejando
  la rama de agentrouter con ámbito de conexión, y retorna; nunca se alcanzan
  el bloqueo por modelo ni la ruta genérica posterior.
- **Combo incluido**: al igual que la rama de agentrouter, el ámbito ignora
  deliberadamente la degradación `persistUnavailableState`/`isCombo` que un
  llamador combo aplica a un 429. Un bloqueo por modelo no es una forma más
  débil de este ámbito, sino la unidad equivocada: no dice nada sobre la IP
  agotada, por lo que la rotación combo seguiría desperdiciando una llamada con
  fallo garantizado por cada conexión hermana.
- **Seguridad de las conexiones hermanas**: nunca se sobrescribe una conexión
  hermana que ya esté en un estado terminal (banned/credits_exhausted) o en un
  enfriamiento más prolongado.
- **Lista de permitidos exclusiva**: ampliar `EGRESS_BUCKETED_LOCK_PROVIDERS` es
  una decisión explícita del responsable; no hay integración genérica (patrón
  #10334/#10419). La consulta de conexiones hermanas utiliza esa misma lista de
  permitidos en lugar de repetirla como un literal SQL, de modo que ampliarla
  siga siendo un cambio de una sola línea.
- **Rotación de la IP de salida, en ambas direcciones**: la ventana de búsqueda
  (24h) es mucho más amplia que el TTL de la caché de IP de salida (5 min), por
  lo que «última IP conocida» es información histórica, no el estado actual. Si
  el proxy de una conexión rotó dentro de la ventana, el bloqueo puede **no
  detectar** una IP realmente compartida (la IP registrada es la nueva, no
  agotada) y, simétricamente, puede **enfriar una conexión hermana que desde
  entonces ya haya rotado** y dejado de usar la IP agotada. El segundo caso le
  cuesta a esa conexión hermana una ventana de enfriamiento; ambos se aceptan
  como limitaciones de mejor esfuerzo de una búsqueda basada en el historial.
- **Coste**: dos recorridos acotados de `proxy_logs` (filtrados por ventana
  mediante `idx_pl_timestamp`), únicamente con la frecuencia de los errores 429. Sin índice nuevo (migración 134, YAGNI). Medido en una copia de tamaño
  moderado de una base de datos con tráfico real; una instancia de alto
  rendimiento conserva proporcionalmente más filas en la misma ventana.

---

## Otras funciones de resiliencia

- **19 estrategias de enrutamiento** (prioridad, ponderado, round-robin, retransmisión de contexto, llenar primero, p2c, aleatorio, menos usado, optimizado por costes, consciente del reinicio, ventana de reinicio, margen disponible, aleatorio estricto, automático, lkgp, optimizado por contexto, optimizado para caché, fusión, canalización) — consulta [AUTO-COMBO.md](../routing/AUTO-COMBO.md).
- **Enrutamiento consciente del reinicio** (v3.8.0) — prioriza las conexiones según el tiempo de reinicio de la cuota.
- **Degradación del modo en segundo plano** — `background: true` de la Responses API se degrada al modo síncrono con una advertencia.
- **Detección dinámica del límite de herramientas** — reduce el uso de proveedores cuando se alcanzan los límites de cantidad de herramientas.
- **Respaldo de emergencia** — controlado por `OMNIROUTE_EMERGENCY_FALLBACK`; los operadores pueden modificarlo desde la página de indicadores de funciones sin reiniciar.

---

## Depuración

- Las respuestas de combinación ponderada `503 all_targets_cooling_down` (con `Retry-After` establecido y `diagnostics.excluded` enumerando cada destino con `model_lockout` / `circuit_open` / `provider_cooldown` / `unavailable`) → el grupo está configurado y conectado; simplemente, todos los destinos están excluidos por un temporizador de resiliencia. La advertencia `[COMBO] Weighted selection: every target excluded before dispatch — …` indica los motivos y los segundos restantes. Un `404 no_executable_targets` de la misma combinación significa que no intervino ningún temporizador de resiliencia (no hay nada que ejecutar o todas las cuentas fallaron la comprobación de disponibilidad). Implementado en `open-sse/services/combo/pinRecovery.ts` a partir de las exclusiones recopiladas en `targetResolution.ts`.
- Se omiten todas las claves de un proveedor → compruebe tanto el estado del disyuntor como `rateLimitedUntil`/`testStatus` de cada conexión.
- Proveedor excluido permanentemente después de la ventana de restablecimiento → el código lee el valor `state` sin procesar en lugar de `getStatus()`/`canExecute()`.
- Una clave falla, pero las demás deberían funcionar → priorice el tiempo de espera de la conexión sobre el disyuntor.
- Solo falla un modelo → priorice el bloqueo del modelo sobre el tiempo de espera de la conexión.
- El estado debería recuperarse automáticamente, pero no lo hace → compruebe si hay una marca de tiempo futura y una ruta de lectura que actualice el estado expirado. Los estados permanentes requieren cambios manuales.

---

## Huellas digitales TLS y sigilo

El sigilo específico de cada proveedor (JA3/JA4, CCH, ofuscación) se documenta por separado; consulta `docs/security/STEALTH_GUIDE.md` (git; no se compila en `/docs`).

---

## Pruebas de resiliencia (Fase 8 · Bloque C)

Además de las pruebas unitarias de la lógica de resiliencia, tres pruebas evalúan el entorno de ejecución bajo
condiciones reales de estrés y fallo (todas son de integración/nocturnas; ninguna bloquea los PR):

| Prueba               | Descripción                                                                                                                                                                                                                 | Ejecución                                 |
| -------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------- |
| Caos                 | Un nodo ascendente simulado inyecta latencia/restablecimientos/tiempos de espera/errores 503 reales; valida que el disyuntor se abra/recupere y que `checkFallbackError` clasifique el error 503 como respaldo recuperable. | `RUN_CHAOS_INT=1 npm run test:chaos`      |
| Crecimiento del heap | ~500 flujos por `createSSEStream` con `--expose-gc`; falla si el heap supera el límite máximo (protección contra OOM #3069).                                                                                                | `npm run test:heap`                       |
| Prueba prolongada k6 | Carga sostenida contra `/api/monitoring/health`; umbrales de p95/errores.                                                                                                                                                   | `k6 run tests/load/k6-soak.js` (nocturna) |

Orquestadas por `.github/workflows/nightly-resilience.yml` (cron + ejecución manual). En la configuración
predeterminada de `test:integration`, las pruebas de caos y heap se omiten automáticamente (sin `RUN_CHAOS_INT`/`--expose-gc`).

---

## Véase también

- [Guía de arquitectura](./ARCHITECTURE.md) — Arquitectura del sistema y funcionamiento interno
- [Guía del usuario](../guides/USER_GUIDE.md) — Proveedores, combos, integración con la CLI
- [Motor de combos automáticos](../routing/AUTO-COMBO.md) — Puntuación de 16 factores, paquetes de modos
