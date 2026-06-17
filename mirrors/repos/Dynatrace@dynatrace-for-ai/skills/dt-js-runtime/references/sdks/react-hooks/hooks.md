# React Hooks — Hooks, Components, Functions, Constants

> ⚠️ BROWSER-ONLY — frontend (React) use only.

Import from `@dynatrace-sdk/react-hooks`. Hooks grouped by domain.

## Grail / DQL

`useDql`, `useDqlQuery`, `useGrailFields`.

## Documents (wrap `client-document`)

`useDocument`, `useDocumentMetaData`, `useListDocuments`, `useDownloadDocument`, `useCreateDocument`, `useUpdateDocument`, `useUpdateDocumentMetadata`, `useDeleteDocument`, `useTransferOwnershipV2`.

## Document permissions (V2)

`usePermissionsV2`, `useAccessorPermissionsV2`, `useAllUsersPermissionsV2`, `useEffectivePermissionsV2`, `useCreatePermissionsV2`, `useUpdateAccessorPermissionsV2`, `useUpdateAllUsersPermissionsV2`, `useDeleteAccessorPermissionsV2`, `useDeleteAllUsersPermissionsV2`.

## App / user state (wrap `client-state`)

`useAppState`, `useAppStates`, `useSetAppState`, `useDeleteAppState`, `useDeleteAppStates`, `useUserAppState`, `useUserAppStates`, `useSetUserAppState`, `useDeleteUserAppState`, `useDeleteUserAppStates`.

## Settings (v1 + V2)

`useSettings`, `useSettingsObjects`, `useSettingsV2`, `useSettingsObjectsV2`, `useCreateSettings`, `useCreateSettingsV2`, `useUpdateSettings`, `useUpdateSettingsV2`, `useDeleteSettings`, `useDeleteSettingsV2`, `useEffectivePermissions`.

## Davis & app functions

`useAnalyzer` (wraps `client-davis-analyzers`), `useAppFunction` (call an app function).

## Users (wrap `client-iam`)

`useUser`, `useUsers`.

## Components

`DqlQueryParamsProvider` — provides shared DQL query params (timeframe, filters) to descendant hooks.

## Functions

`UseUsersProvider`, `getGrailFieldsQueryOptions`.

## Constants

`DqlQueryParamsContext` — React context backing `DqlQueryParamsProvider`.
