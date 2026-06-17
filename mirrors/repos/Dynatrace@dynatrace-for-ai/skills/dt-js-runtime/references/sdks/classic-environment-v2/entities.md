# Monitored-entities clients

Query monitored entities, manage custom tags and monitoring state. Import from `@dynatrace-sdk/client-classic-environment-v2`.

## `monitoredEntitiesClient`

| Method | Purpose |
|---|---|
| `getEntities` | Query entities via entity selector (paginated). |
| `getEntity` | Get one entity by id. |
| `getEntityTypes` | List entity types. |
| `getEntityType` | Get one entity type. |
| `pushCustomDevice` | Create/update a custom device entity. |
| `setSecurityContext` | Set an entity's security context. |
| `deleteSecurityContext` | Remove an entity's security context. |

## `monitoredEntitiesCustomTagsClient`

| Method | Purpose |
|---|---|
| `getTags` | List custom tags for entities matching a selector. |
| `postTags` | Add custom tags. |
| `deleteTags` | Remove custom tags. |

## `monitoredEntitiesMonitoringStateClient`

| Method | Purpose |
|---|---|
| `getStates` | Get monitoring state of entities. |
