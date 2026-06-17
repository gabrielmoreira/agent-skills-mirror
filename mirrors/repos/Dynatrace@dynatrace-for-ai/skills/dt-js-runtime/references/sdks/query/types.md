# DQL Query — Types & Enums

All exported types/enums of `@dynatrace-sdk/client-query`. Full field definitions: https://developer.dynatrace.com/develop/sdks/client-query/#types

## Request types

`AutocompleteRequest`, `ExecuteRequest`, `ParseRequest`, `VerifyRequest`, `QueryOptions`.

## Response / result types

`AutocompleteResponse`, `AutocompleteSuggestion`, `AutocompleteSuggestionPart`, `QueryStartResponse`, `QueryPollResponse`, `QueryResult`, `ResultRecord`, `ResultRecordValue`, `VerifyResponse`.

## Metadata & type-mapping types

`GrailMetadata`, `Metadata`, `MetadataNotification`, `MetricMetadata`, `RangedFieldTypes`, `RangedFieldTypesMappings`, `FieldType`, `BucketContribution`, `Contributions`, `Timeframe`, `GeoPoint`, `PositionInfo`, `TokenPosition`.

## DQL parse-tree types

`DQLNode`, `DQLAlternativeNode`, `DQLContainerNode`, `DQLTerminalNode`.

## Filter-segment types

`FilterSegment`, `FilterSegments`, `FilterSegmentVariableDefinition`.

## Error types

`ErrorEnvelope`, `ErrorResponse`, `ErrorResponseDetails`, `ErrorResponseDetailsConstraintViolationsItem`.

## Enums

- `QueryState` — `NOT_STARTED`, `RUNNING`, `SUCCEEDED`, `CANCELLED`, `FAILED`.
- `DQLNodeNodeType` — node kinds in the parse tree.
- `FieldTypeType` — record field data types.
- `TokenType` — `USER`, `CANONICAL`, `INFO`, etc.
