---
repo: t8y2/dbx
repoUrl: https://github.com/t8y2/dbx.git
refType: branch
ref: main
---

# Mirror Manifest

Mirror of `t8y2/dbx` — 26 default patterns, 8 followed patterns, 627 file(s) materialized.

## Metadata

| Field         | Value |
|---------------|-------|
| Repo          | `t8y2/dbx` |
| Ref Type      | `branch` |
| Ref           | `main` |
| Default pats  | 26 |
| Followed pats | 8 |
| Files         | 627 |

## Default Sparse Patterns  *(included from config)*

- `**/AGENTS.md`
- `**/CLAUDE.md`
- `**/claude.md`
- `**/gemini.md`
- `**/GEMINI.md`
- `**/SKILL.md`
- `**/skills.md`
- `**/LLMs.txt`
- `**/llms.txt`
- `**/copilot-instructions.md`
- `**/.cursorrules`
- `**/.cursor/rules/**`
- `**/.windsurfrules`
- `**/.continue/**`
- `.github/instructions/**`
- `.github/prompts/**`
- `.agents/**`
- `agents/**`
- `skills/**`
- `skill/**`
- `prompts/**`
- `prompt/**`
- `.cursor/**`
- `.continue/**`
- `.mcp/**`
- `mcp/**`

## Followed Sparse Patterns  *(discovered via markdown refs)*

- `README.zh-CN.md`
- `README.md`
- `packages/mcp-server/README.md`
- `packages/cli/README.md`
- `deploy/database/README.zh-CN.md`
- `CONTRIBUTING.zh-CN.md`
- `deploy/database/README.md`
- `CONTRIBUTING.md`

## File Index

Legend: **✓** = default pattern · **→** = followed via markdown

| # | S | File |
|---|---|------|
| 1 | ✓ | [`agents/.gitignore`](agents/.gitignore) |
| 2 | ✓ | [`agents/build.gradle`](agents/build.gradle) |
| 3 | ✓ | [`agents/common/build.gradle`](agents/common/build.gradle) |
| 4 | ✓ | [`agents/common/src/main/java/com/dbx/agent/AbstractJdbcAgent.java`](agents/common/src/main/java/com/dbx/agent/AbstractJdbcAgent.java) |
| 5 | ✓ | [`agents/common/src/main/java/com/dbx/agent/AgentExecutionContext.java`](agents/common/src/main/java/com/dbx/agent/AgentExecutionContext.java) |
| 6 | ✓ | [`agents/common/src/main/java/com/dbx/agent/AgentProtocol.java`](agents/common/src/main/java/com/dbx/agent/AgentProtocol.java) |
| 7 | ✓ | [`agents/common/src/main/java/com/dbx/agent/AgentRpcError.java`](agents/common/src/main/java/com/dbx/agent/AgentRpcError.java) |
| 8 | ✓ | [`agents/common/src/main/java/com/dbx/agent/BaseDatabaseAgent.java`](agents/common/src/main/java/com/dbx/agent/BaseDatabaseAgent.java) |
| 9 | ✓ | [`agents/common/src/main/java/com/dbx/agent/BatchExecutor.java`](agents/common/src/main/java/com/dbx/agent/BatchExecutor.java) |
| 10 | ✓ | [`agents/common/src/main/java/com/dbx/agent/CheckConstraintInfo.java`](agents/common/src/main/java/com/dbx/agent/CheckConstraintInfo.java) |
| 11 | ✓ | [`agents/common/src/main/java/com/dbx/agent/ColumnInfo.java`](agents/common/src/main/java/com/dbx/agent/ColumnInfo.java) |
| 12 | ✓ | [`agents/common/src/main/java/com/dbx/agent/CompletionAssistantCandidate.java`](agents/common/src/main/java/com/dbx/agent/CompletionAssistantCandidate.java) |
| 13 | ✓ | [`agents/common/src/main/java/com/dbx/agent/CompletionAssistantCandidateKind.java`](agents/common/src/main/java/com/dbx/agent/CompletionAssistantCandidateKind.java) |
| 14 | ✓ | [`agents/common/src/main/java/com/dbx/agent/CompletionAssistantMatchMode.java`](agents/common/src/main/java/com/dbx/agent/CompletionAssistantMatchMode.java) |
| 15 | ✓ | [`agents/common/src/main/java/com/dbx/agent/CompletionAssistantObjectKind.java`](agents/common/src/main/java/com/dbx/agent/CompletionAssistantObjectKind.java) |
| 16 | ✓ | [`agents/common/src/main/java/com/dbx/agent/CompletionAssistantRequest.java`](agents/common/src/main/java/com/dbx/agent/CompletionAssistantRequest.java) |
| 17 | ✓ | [`agents/common/src/main/java/com/dbx/agent/CompletionAssistantResponse.java`](agents/common/src/main/java/com/dbx/agent/CompletionAssistantResponse.java) |
| 18 | ✓ | [`agents/common/src/main/java/com/dbx/agent/ConfiguredJdbcAgent.java`](agents/common/src/main/java/com/dbx/agent/ConfiguredJdbcAgent.java) |
| 19 | ✓ | [`agents/common/src/main/java/com/dbx/agent/ConnectParams.java`](agents/common/src/main/java/com/dbx/agent/ConnectParams.java) |
| 20 | ✓ | [`agents/common/src/main/java/com/dbx/agent/DatabaseAgent.java`](agents/common/src/main/java/com/dbx/agent/DatabaseAgent.java) |
| 21 | ✓ | [`agents/common/src/main/java/com/dbx/agent/DatabaseInfo.java`](agents/common/src/main/java/com/dbx/agent/DatabaseInfo.java) |
| 22 | ✓ | [`agents/common/src/main/java/com/dbx/agent/DdlBuilder.java`](agents/common/src/main/java/com/dbx/agent/DdlBuilder.java) |
| 23 | ✓ | [`agents/common/src/main/java/com/dbx/agent/EwkbWktDecoder.java`](agents/common/src/main/java/com/dbx/agent/EwkbWktDecoder.java) |
| 24 | ✓ | [`agents/common/src/main/java/com/dbx/agent/ExecuteQueryOptions.java`](agents/common/src/main/java/com/dbx/agent/ExecuteQueryOptions.java) |
| 25 | ✓ | [`agents/common/src/main/java/com/dbx/agent/ExecuteQueryParams.java`](agents/common/src/main/java/com/dbx/agent/ExecuteQueryParams.java) |
| 26 | ✓ | [`agents/common/src/main/java/com/dbx/agent/ForeignKeyInfo.java`](agents/common/src/main/java/com/dbx/agent/ForeignKeyInfo.java) |
| 27 | ✓ | [`agents/common/src/main/java/com/dbx/agent/IndexInfo.java`](agents/common/src/main/java/com/dbx/agent/IndexInfo.java) |
| 28 | ✓ | [`agents/common/src/main/java/com/dbx/agent/JdbcAgentProfile.java`](agents/common/src/main/java/com/dbx/agent/JdbcAgentProfile.java) |
| 29 | ✓ | [`agents/common/src/main/java/com/dbx/agent/JdbcConnectionAffinity.java`](agents/common/src/main/java/com/dbx/agent/JdbcConnectionAffinity.java) |
| 30 | ✓ | [`agents/common/src/main/java/com/dbx/agent/JdbcConnectionPoolRegistry.java`](agents/common/src/main/java/com/dbx/agent/JdbcConnectionPoolRegistry.java) |
| 31 | ✓ | [`agents/common/src/main/java/com/dbx/agent/JdbcDatabaseInfo.java`](agents/common/src/main/java/com/dbx/agent/JdbcDatabaseInfo.java) |
| 32 | ✓ | [`agents/common/src/main/java/com/dbx/agent/JdbcExecutor.java`](agents/common/src/main/java/com/dbx/agent/JdbcExecutor.java) |
| 33 | ✓ | [`agents/common/src/main/java/com/dbx/agent/JdbcIdentifiers.java`](agents/common/src/main/java/com/dbx/agent/JdbcIdentifiers.java) |
| 34 | ✓ | [`agents/common/src/main/java/com/dbx/agent/JdbcSchemaSwitcher.java`](agents/common/src/main/java/com/dbx/agent/JdbcSchemaSwitcher.java) |
| 35 | ✓ | [`agents/common/src/main/java/com/dbx/agent/JdbcSessionRole.java`](agents/common/src/main/java/com/dbx/agent/JdbcSessionRole.java) |
| 36 | ✓ | [`agents/common/src/main/java/com/dbx/agent/JsonRpcServer.java`](agents/common/src/main/java/com/dbx/agent/JsonRpcServer.java) |
| 37 | ✓ | [`agents/common/src/main/java/com/dbx/agent/MetadataListConstraints.java`](agents/common/src/main/java/com/dbx/agent/MetadataListConstraints.java) |
| 38 | ✓ | [`agents/common/src/main/java/com/dbx/agent/MetadataSqlSupport.java`](agents/common/src/main/java/com/dbx/agent/MetadataSqlSupport.java) |
| 39 | ✓ | [`agents/common/src/main/java/com/dbx/agent/MultiSessionJsonRpcServer.java`](agents/common/src/main/java/com/dbx/agent/MultiSessionJsonRpcServer.java) |
| 40 | ✓ | [`agents/common/src/main/java/com/dbx/agent/ObjectInfo.java`](agents/common/src/main/java/com/dbx/agent/ObjectInfo.java) |
| 41 | ✓ | [`agents/common/src/main/java/com/dbx/agent/ObjectSource.java`](agents/common/src/main/java/com/dbx/agent/ObjectSource.java) |
| 42 | ✓ | [`agents/common/src/main/java/com/dbx/agent/PostgresLikeAgent.java`](agents/common/src/main/java/com/dbx/agent/PostgresLikeAgent.java) |
| 43 | ✓ | [`agents/common/src/main/java/com/dbx/agent/PostgresLikeAgentProfile.java`](agents/common/src/main/java/com/dbx/agent/PostgresLikeAgentProfile.java) |
| 44 | ✓ | [`agents/common/src/main/java/com/dbx/agent/QueryPageOptions.java`](agents/common/src/main/java/com/dbx/agent/QueryPageOptions.java) |
| 45 | ✓ | [`agents/common/src/main/java/com/dbx/agent/QueryPageParams.java`](agents/common/src/main/java/com/dbx/agent/QueryPageParams.java) |
| 46 | ✓ | [`agents/common/src/main/java/com/dbx/agent/QueryPageResult.java`](agents/common/src/main/java/com/dbx/agent/QueryPageResult.java) |
| 47 | ✓ | [`agents/common/src/main/java/com/dbx/agent/QueryResult.java`](agents/common/src/main/java/com/dbx/agent/QueryResult.java) |
| 48 | ✓ | [`agents/common/src/main/java/com/dbx/agent/SchemaTableParams.java`](agents/common/src/main/java/com/dbx/agent/SchemaTableParams.java) |
| 49 | ✓ | [`agents/common/src/main/java/com/dbx/agent/SessionRpcHandler.java`](agents/common/src/main/java/com/dbx/agent/SessionRpcHandler.java) |
| 50 | ✓ | [`agents/common/src/main/java/com/dbx/agent/SpatialColumn.java`](agents/common/src/main/java/com/dbx/agent/SpatialColumn.java) |
| 51 | ✓ | [`agents/common/src/main/java/com/dbx/agent/SpatialValue.java`](agents/common/src/main/java/com/dbx/agent/SpatialValue.java) |
| 52 | ✓ | [`agents/common/src/main/java/com/dbx/agent/StandardJdbcMetadata.java`](agents/common/src/main/java/com/dbx/agent/StandardJdbcMetadata.java) |
| 53 | ✓ | [`agents/common/src/main/java/com/dbx/agent/TableInfo.java`](agents/common/src/main/java/com/dbx/agent/TableInfo.java) |
| 54 | ✓ | [`agents/common/src/main/java/com/dbx/agent/TransactionExecutor.java`](agents/common/src/main/java/com/dbx/agent/TransactionExecutor.java) |
| 55 | ✓ | [`agents/common/src/main/java/com/dbx/agent/TriggerInfo.java`](agents/common/src/main/java/com/dbx/agent/TriggerInfo.java) |
| 56 | ✓ | [`agents/common/src/main/resources/agent-protocol-v1.json`](agents/common/src/main/resources/agent-protocol-v1.json) |
| 57 | ✓ | [`agents/common/src/main/resources/agent-protocol-v2.json`](agents/common/src/main/resources/agent-protocol-v2.json) |
| 58 | ✓ | [`agents/common/src/test/java/com/dbx/agent/AbstractJdbcAgentTest.java`](agents/common/src/test/java/com/dbx/agent/AbstractJdbcAgentTest.java) |
| 59 | ✓ | [`agents/common/src/test/java/com/dbx/agent/AgentRpcErrorTest.java`](agents/common/src/test/java/com/dbx/agent/AgentRpcErrorTest.java) |
| 60 | ✓ | [`agents/common/src/test/java/com/dbx/agent/BatchExecutorTest.java`](agents/common/src/test/java/com/dbx/agent/BatchExecutorTest.java) |
| 61 | ✓ | [`agents/common/src/test/java/com/dbx/agent/CommonJavaCompatibilityTest.java`](agents/common/src/test/java/com/dbx/agent/CommonJavaCompatibilityTest.java) |
| 62 | ✓ | [`agents/common/src/test/java/com/dbx/agent/ConfiguredJdbcAgentTest.java`](agents/common/src/test/java/com/dbx/agent/ConfiguredJdbcAgentTest.java) |
| 63 | ✓ | [`agents/common/src/test/java/com/dbx/agent/EwkbWktDecoderTest.java`](agents/common/src/test/java/com/dbx/agent/EwkbWktDecoderTest.java) |
| 64 | ✓ | [`agents/common/src/test/java/com/dbx/agent/JdbcAgentProfileExtendedTest.java`](agents/common/src/test/java/com/dbx/agent/JdbcAgentProfileExtendedTest.java) |
| 65 | ✓ | [`agents/common/src/test/java/com/dbx/agent/JdbcConnectionPoolingTest.java`](agents/common/src/test/java/com/dbx/agent/JdbcConnectionPoolingTest.java) |
| 66 | ✓ | [`agents/common/src/test/java/com/dbx/agent/JdbcExecutorTest.java`](agents/common/src/test/java/com/dbx/agent/JdbcExecutorTest.java) |
| 67 | ✓ | [`agents/common/src/test/java/com/dbx/agent/MetadataConstraintCoverageTest.java`](agents/common/src/test/java/com/dbx/agent/MetadataConstraintCoverageTest.java) |
| 68 | ✓ | [`agents/common/src/test/java/com/dbx/agent/MetadataListConstraintsTest.java`](agents/common/src/test/java/com/dbx/agent/MetadataListConstraintsTest.java) |
| 69 | ✓ | [`agents/common/src/test/java/com/dbx/agent/PostgresLikeAgentTest.java`](agents/common/src/test/java/com/dbx/agent/PostgresLikeAgentTest.java) |
| 70 | ✓ | [`agents/common/src/test/java/com/dbx/agent/StandardJdbcMetadataTest.java`](agents/common/src/test/java/com/dbx/agent/StandardJdbcMetadataTest.java) |
| 71 | ✓ | [`agents/docs/agent-authoring.md`](agents/docs/agent-authoring.md) |
| 72 | ✓ | [`agents/docs/agent-authoring.zh-CN.md`](agents/docs/agent-authoring.zh-CN.md) |
| 73 | ✓ | [`agents/docs/agent-protocol-v2.md`](agents/docs/agent-protocol-v2.md) |
| 74 | ✓ | [`agents/docs/examples/jdbc-agent-template/build.gradle`](agents/docs/examples/jdbc-agent-template/build.gradle) |
| 75 | ✓ | [`agents/docs/examples/jdbc-agent-template/README.md`](agents/docs/examples/jdbc-agent-template/README.md) |
| 76 | ✓ | [`agents/docs/examples/jdbc-agent-template/settings.gradle`](agents/docs/examples/jdbc-agent-template/settings.gradle) |
| 77 | ✓ | [`agents/docs/examples/jdbc-agent-template/src/main/java/com/dbx/agent/template/TemplateAgent.java`](agents/docs/examples/jdbc-agent-template/src/main/java/com/dbx/agent/template/TemplateAgent.java) |
| 78 | ✓ | [`agents/docs/examples/jdbc-agent-template/src/test/java/com/dbx/agent/template/TemplateAgentTest.java`](agents/docs/examples/jdbc-agent-template/src/test/java/com/dbx/agent/template/TemplateAgentTest.java) |
| 79 | ✓ | [`agents/docs/release-checklist.md`](agents/docs/release-checklist.md) |
| 80 | ✓ | [`agents/drivers/access/build.gradle`](agents/drivers/access/build.gradle) |
| 81 | ✓ | [`agents/drivers/access/src/main/java/com/dbx/agent/access/AccessAgent.java`](agents/drivers/access/src/main/java/com/dbx/agent/access/AccessAgent.java) |
| 82 | ✓ | [`agents/drivers/access/src/main/java/com/dbx/agent/access/EncryptedAccessOpener.java`](agents/drivers/access/src/main/java/com/dbx/agent/access/EncryptedAccessOpener.java) |
| 83 | ✓ | [`agents/drivers/access/src/test/java/com/dbx/agent/access/AccessAgentTest.java`](agents/drivers/access/src/test/java/com/dbx/agent/access/AccessAgentTest.java) |
| 84 | ✓ | [`agents/drivers/access/src/test/resources/db2007-enc.accdb`](agents/drivers/access/src/test/resources/db2007-enc.accdb) |
| 85 | ✓ | [`agents/drivers/argo-go/bench/agent_compare.py`](agents/drivers/argo-go/bench/agent_compare.py) |
| 86 | ✓ | [`agents/drivers/argo-go/bench/functional_probe.py`](agents/drivers/argo-go/bench/functional_probe.py) |
| 87 | ✓ | [`agents/drivers/argo-go/bench/kdc_fixture/main.go`](agents/drivers/argo-go/bench/kdc_fixture/main.go) |
| 88 | ✓ | [`agents/drivers/argo-go/bench/README.md`](agents/drivers/argo-go/bench/README.md) |
| 89 | ✓ | [`agents/drivers/argo-go/config_test.go`](agents/drivers/argo-go/config_test.go) |
| 90 | ✓ | [`agents/drivers/argo-go/config.go`](agents/drivers/argo-go/config.go) |
| 91 | ✓ | [`agents/drivers/argo-go/connector_test.go`](agents/drivers/argo-go/connector_test.go) |
| 92 | ✓ | [`agents/drivers/argo-go/connector.go`](agents/drivers/argo-go/connector.go) |
| 93 | ✓ | [`agents/drivers/argo-go/discovery_test.go`](agents/drivers/argo-go/discovery_test.go) |
| 94 | ✓ | [`agents/drivers/argo-go/discovery.go`](agents/drivers/argo-go/discovery.go) |
| 95 | ✓ | [`agents/drivers/argo-go/go.mod`](agents/drivers/argo-go/go.mod) |
| 96 | ✓ | [`agents/drivers/argo-go/go.sum`](agents/drivers/argo-go/go.sum) |
| 97 | ✓ | [`agents/drivers/argo-go/init_test.go`](agents/drivers/argo-go/init_test.go) |
| 98 | ✓ | [`agents/drivers/argo-go/kerberos_defaults_unix.go`](agents/drivers/argo-go/kerberos_defaults_unix.go) |
| 99 | ✓ | [`agents/drivers/argo-go/kerberos_defaults_windows.go`](agents/drivers/argo-go/kerberos_defaults_windows.go) |
| 100 | ✓ | [`agents/drivers/argo-go/main.go`](agents/drivers/argo-go/main.go) |
| 101 | ✓ | [`agents/drivers/argo-go/metadata_test.go`](agents/drivers/argo-go/metadata_test.go) |
| 102 | ✓ | [`agents/drivers/argo-go/metadata.go`](agents/drivers/argo-go/metadata.go) |
| 103 | ✓ | [`agents/drivers/argo-go/MIGRATION_PARITY.md`](agents/drivers/argo-go/MIGRATION_PARITY.md) |
| 104 | ✓ | [`agents/drivers/argo-go/protocol_error.go`](agents/drivers/argo-go/protocol_error.go) |
| 105 | ✓ | [`agents/drivers/argo-go/query_test.go`](agents/drivers/argo-go/query_test.go) |
| 106 | ✓ | [`agents/drivers/argo-go/query.go`](agents/drivers/argo-go/query.go) |
| 107 | ✓ | [`agents/drivers/argo-go/zookeeper_protocol_test.go`](agents/drivers/argo-go/zookeeper_protocol_test.go) |
| 108 | ✓ | [`agents/drivers/argo-go/zookeeper_protocol.go`](agents/drivers/argo-go/zookeeper_protocol.go) |
| 109 | ✓ | [`agents/drivers/argo-go/zookeeper_tls_test.go`](agents/drivers/argo-go/zookeeper_tls_test.go) |
| 110 | ✓ | [`agents/drivers/argo-go/zookeeper_tls.go`](agents/drivers/argo-go/zookeeper_tls.go) |
| 111 | ✓ | [`agents/drivers/bigquery/build.gradle`](agents/drivers/bigquery/build.gradle) |
| 112 | ✓ | [`agents/drivers/bigquery/src/main/java/com/dbx/agent/bigquery/BigQueryAgent.java`](agents/drivers/bigquery/src/main/java/com/dbx/agent/bigquery/BigQueryAgent.java) |
| 113 | ✓ | [`agents/drivers/bigquery/src/test/java/com/dbx/agent/bigquery/BigQueryAgentMetadataTest.java`](agents/drivers/bigquery/src/test/java/com/dbx/agent/bigquery/BigQueryAgentMetadataTest.java) |
| 114 | ✓ | [`agents/drivers/bigquery/src/test/java/com/dbx/agent/bigquery/BigQueryAgentTest.java`](agents/drivers/bigquery/src/test/java/com/dbx/agent/bigquery/BigQueryAgentTest.java) |
| 115 | ✓ | [`agents/drivers/cache/build.gradle`](agents/drivers/cache/build.gradle) |
| 116 | ✓ | [`agents/drivers/cache/libs/CacheDB.jar`](agents/drivers/cache/libs/CacheDB.jar) |
| 117 | ✓ | [`agents/drivers/cache/src/main/java/com/dbx/agent/cache/CacheAgent.java`](agents/drivers/cache/src/main/java/com/dbx/agent/cache/CacheAgent.java) |
| 118 | ✓ | [`agents/drivers/cache/src/test/java/com/dbx/agent/cache/CacheAgentTest.java`](agents/drivers/cache/src/test/java/com/dbx/agent/cache/CacheAgentTest.java) |
| 119 | ✓ | [`agents/drivers/cassandra-go/astra_test.go`](agents/drivers/cassandra-go/astra_test.go) |
| 120 | ✓ | [`agents/drivers/cassandra-go/bench/agent_compare.py`](agents/drivers/cassandra-go/bench/agent_compare.py) |
| 121 | ✓ | [`agents/drivers/cassandra-go/bench/README.md`](agents/drivers/cassandra-go/bench/README.md) |
| 122 | ✓ | [`agents/drivers/cassandra-go/bench/results/cassandra-4.1.10.json`](agents/drivers/cassandra-go/bench/results/cassandra-4.1.10.json) |
| 123 | ✓ | [`agents/drivers/cassandra-go/config_file_test.go`](agents/drivers/cassandra-go/config_file_test.go) |
| 124 | ✓ | [`agents/drivers/cassandra-go/config_file.go`](agents/drivers/cassandra-go/config_file.go) |
| 125 | ✓ | [`agents/drivers/cassandra-go/config_test.go`](agents/drivers/cassandra-go/config_test.go) |
| 126 | ✓ | [`agents/drivers/cassandra-go/config.go`](agents/drivers/cassandra-go/config.go) |
| 127 | ✓ | [`agents/drivers/cassandra-go/dialer.go`](agents/drivers/cassandra-go/dialer.go) |
| 128 | ✓ | [`agents/drivers/cassandra-go/go.mod`](agents/drivers/cassandra-go/go.mod) |
| 129 | ✓ | [`agents/drivers/cassandra-go/go.sum`](agents/drivers/cassandra-go/go.sum) |
| 130 | ✓ | [`agents/drivers/cassandra-go/integration_test.go`](agents/drivers/cassandra-go/integration_test.go) |
| 131 | ✓ | [`agents/drivers/cassandra-go/kerberos_test.go`](agents/drivers/cassandra-go/kerberos_test.go) |
| 132 | ✓ | [`agents/drivers/cassandra-go/kerberos.go`](agents/drivers/cassandra-go/kerberos.go) |
| 133 | ✓ | [`agents/drivers/cassandra-go/main.go`](agents/drivers/cassandra-go/main.go) |
| 134 | ✓ | [`agents/drivers/cassandra-go/metadata_test.go`](agents/drivers/cassandra-go/metadata_test.go) |
| 135 | ✓ | [`agents/drivers/cassandra-go/metadata.go`](agents/drivers/cassandra-go/metadata.go) |
| 136 | ✓ | [`agents/drivers/cassandra-go/protocol_error.go`](agents/drivers/cassandra-go/protocol_error.go) |
| 137 | ✓ | [`agents/drivers/cassandra-go/protocol_test.go`](agents/drivers/cassandra-go/protocol_test.go) |
| 138 | ✓ | [`agents/drivers/cassandra-go/query.go`](agents/drivers/cassandra-go/query.go) |
| 139 | ✓ | [`agents/drivers/cassandra-go/README.md`](agents/drivers/cassandra-go/README.md) |
| 140 | ✓ | [`agents/drivers/cassandra-go/runtime_test.go`](agents/drivers/cassandra-go/runtime_test.go) |
| 141 | ✓ | [`agents/drivers/cassandra-go/runtime.go`](agents/drivers/cassandra-go/runtime.go) |
| 142 | ✓ | [`agents/drivers/cassandra-go/values_test.go`](agents/drivers/cassandra-go/values_test.go) |
| 143 | ✓ | [`agents/drivers/cassandra-go/values.go`](agents/drivers/cassandra-go/values.go) |
| 144 | ✓ | [`agents/drivers/dameng/build.gradle`](agents/drivers/dameng/build.gradle) |
| 145 | ✓ | [`agents/drivers/dameng/libs/.gitkeep`](agents/drivers/dameng/libs/.gitkeep) |
| 146 | ✓ | [`agents/drivers/dameng/src/main/java/com/dbx/agent/dameng/DamengAgent.java`](agents/drivers/dameng/src/main/java/com/dbx/agent/dameng/DamengAgent.java) |
| 147 | ✓ | [`agents/drivers/dameng/src/test/java/com/dbx/agent/dameng/DamengAgentMetadataTest.java`](agents/drivers/dameng/src/test/java/com/dbx/agent/dameng/DamengAgentMetadataTest.java) |
| 148 | ✓ | [`agents/drivers/dameng/src/test/java/com/dbx/agent/dameng/DamengAgentPagingTest.java`](agents/drivers/dameng/src/test/java/com/dbx/agent/dameng/DamengAgentPagingTest.java) |
| 149 | ✓ | [`agents/drivers/dameng/src/test/java/com/dbx/agent/dameng/DamengAgentTest.java`](agents/drivers/dameng/src/test/java/com/dbx/agent/dameng/DamengAgentTest.java) |
| 150 | ✓ | [`agents/drivers/dameng/src/test/java/com/dbx/agent/dameng/DamengAgentUrlTest.java`](agents/drivers/dameng/src/test/java/com/dbx/agent/dameng/DamengAgentUrlTest.java) |
| 151 | ✓ | [`agents/drivers/databend/build.gradle`](agents/drivers/databend/build.gradle) |
| 152 | ✓ | [`agents/drivers/databend/src/main/java/com/dbx/agent/databend/DatabendAgent.java`](agents/drivers/databend/src/main/java/com/dbx/agent/databend/DatabendAgent.java) |
| 153 | ✓ | [`agents/drivers/databend/src/test/java/com/dbx/agent/databend/DatabendAgentTest.java`](agents/drivers/databend/src/test/java/com/dbx/agent/databend/DatabendAgentTest.java) |
| 154 | ✓ | [`agents/drivers/databricks/build.gradle`](agents/drivers/databricks/build.gradle) |
| 155 | ✓ | [`agents/drivers/databricks/src/main/java/com/dbx/agent/databricks/DatabricksAgent.java`](agents/drivers/databricks/src/main/java/com/dbx/agent/databricks/DatabricksAgent.java) |
| 156 | ✓ | [`agents/drivers/databricks/src/test/java/com/dbx/agent/databricks/DatabricksAgentTest.java`](agents/drivers/databricks/src/test/java/com/dbx/agent/databricks/DatabricksAgentTest.java) |
| 157 | ✓ | [`agents/drivers/db2/build.gradle`](agents/drivers/db2/build.gradle) |
| 158 | ✓ | [`agents/drivers/db2/src/main/java/com/dbx/agent/db2/Db2Agent.java`](agents/drivers/db2/src/main/java/com/dbx/agent/db2/Db2Agent.java) |
| 159 | ✓ | [`agents/drivers/db2/src/test/java/com/dbx/agent/db2/Db2AgentTest.java`](agents/drivers/db2/src/test/java/com/dbx/agent/db2/Db2AgentTest.java) |
| 160 | ✓ | [`agents/drivers/duckdb/.cargo/config.toml`](agents/drivers/duckdb/.cargo/config.toml) |
| 161 | ✓ | [`agents/drivers/duckdb/Cargo.lock`](agents/drivers/duckdb/Cargo.lock) |
| 162 | ✓ | [`agents/drivers/duckdb/Cargo.toml`](agents/drivers/duckdb/Cargo.toml) |
| 163 | ✓ | [`agents/drivers/duckdb/README.md`](agents/drivers/duckdb/README.md) |
| 164 | ✓ | [`agents/drivers/duckdb/src/connection.rs`](agents/drivers/duckdb/src/connection.rs) |
| 165 | ✓ | [`agents/drivers/duckdb/src/lib.rs`](agents/drivers/duckdb/src/lib.rs) |
| 166 | ✓ | [`agents/drivers/duckdb/src/main.rs`](agents/drivers/duckdb/src/main.rs) |
| 167 | ✓ | [`agents/drivers/duckdb/src/query.rs`](agents/drivers/duckdb/src/query.rs) |
| 168 | ✓ | [`agents/drivers/duckdb/src/runtime.rs`](agents/drivers/duckdb/src/runtime.rs) |
| 169 | ✓ | [`agents/drivers/duckdb/src/schema.rs`](agents/drivers/duckdb/src/schema.rs) |
| 170 | ✓ | [`agents/drivers/duckdb/src/sql.rs`](agents/drivers/duckdb/src/sql.rs) |
| 171 | ✓ | [`agents/drivers/duckdb/src/wire.rs`](agents/drivers/duckdb/src/wire.rs) |
| 172 | ✓ | [`agents/drivers/duckdb/tests/duckdb_worker_process.rs`](agents/drivers/duckdb/tests/duckdb_worker_process.rs) |
| 173 | ✓ | [`agents/drivers/duckdb/tests/support/duckdb_worker_file_lock_owner.rs`](agents/drivers/duckdb/tests/support/duckdb_worker_file_lock_owner.rs) |
| 174 | ✓ | [`agents/drivers/duckdb/tests/support/duckdb_worker_hanging_connect_test_host.rs`](agents/drivers/duckdb/tests/support/duckdb_worker_hanging_connect_test_host.rs) |
| 175 | ✓ | [`agents/drivers/duckdb/tests/support/duckdb_worker_pid_test_host.rs`](agents/drivers/duckdb/tests/support/duckdb_worker_pid_test_host.rs) |
| 176 | ✓ | [`agents/drivers/etcd-go/auth.go`](agents/drivers/etcd-go/auth.go) |
| 177 | ✓ | [`agents/drivers/etcd-go/client.go`](agents/drivers/etcd-go/client.go) |
| 178 | ✓ | [`agents/drivers/etcd-go/go.mod`](agents/drivers/etcd-go/go.mod) |
| 179 | ✓ | [`agents/drivers/etcd-go/go.sum`](agents/drivers/etcd-go/go.sum) |
| 180 | ✓ | [`agents/drivers/etcd-go/history.go`](agents/drivers/etcd-go/history.go) |
| 181 | ✓ | [`agents/drivers/etcd-go/integration_test.go`](agents/drivers/etcd-go/integration_test.go) |
| 182 | ✓ | [`agents/drivers/etcd-go/kv.go`](agents/drivers/etcd-go/kv.go) |
| 183 | ✓ | [`agents/drivers/etcd-go/lease.go`](agents/drivers/etcd-go/lease.go) |
| 184 | ✓ | [`agents/drivers/etcd-go/main_test.go`](agents/drivers/etcd-go/main_test.go) |
| 185 | ✓ | [`agents/drivers/etcd-go/main.go`](agents/drivers/etcd-go/main.go) |
| 186 | ✓ | [`agents/drivers/etcd-go/maintenance.go`](agents/drivers/etcd-go/maintenance.go) |
| 187 | ✓ | [`agents/drivers/etcd-go/MIGRATION_PARITY.md`](agents/drivers/etcd-go/MIGRATION_PARITY.md) |
| 188 | ✓ | [`agents/drivers/etcd-go/protocol_error.go`](agents/drivers/etcd-go/protocol_error.go) |
| 189 | ✓ | [`agents/drivers/etcd-go/status.go`](agents/drivers/etcd-go/status.go) |
| 190 | ✓ | [`agents/drivers/etcd-go/watch.go`](agents/drivers/etcd-go/watch.go) |
| 191 | ✓ | [`agents/drivers/etcd2-go/auth.go`](agents/drivers/etcd2-go/auth.go) |
| 192 | ✓ | [`agents/drivers/etcd2-go/client.go`](agents/drivers/etcd2-go/client.go) |
| 193 | ✓ | [`agents/drivers/etcd2-go/go.mod`](agents/drivers/etcd2-go/go.mod) |
| 194 | ✓ | [`agents/drivers/etcd2-go/integration_test.go`](agents/drivers/etcd2-go/integration_test.go) |
| 195 | ✓ | [`agents/drivers/etcd2-go/kv.go`](agents/drivers/etcd2-go/kv.go) |
| 196 | ✓ | [`agents/drivers/etcd2-go/main_test.go`](agents/drivers/etcd2-go/main_test.go) |
| 197 | ✓ | [`agents/drivers/etcd2-go/main.go`](agents/drivers/etcd2-go/main.go) |
| 198 | ✓ | [`agents/drivers/etcd2-go/protocol_error.go`](agents/drivers/etcd2-go/protocol_error.go) |
| 199 | ✓ | [`agents/drivers/etcd2-go/README.md`](agents/drivers/etcd2-go/README.md) |
| 200 | ✓ | [`agents/drivers/etcd2-go/status.go`](agents/drivers/etcd2-go/status.go) |
| 201 | ✓ | [`agents/drivers/etcd2-go/watch.go`](agents/drivers/etcd2-go/watch.go) |
| 202 | ✓ | [`agents/drivers/exasol/build.gradle`](agents/drivers/exasol/build.gradle) |
| 203 | ✓ | [`agents/drivers/exasol/src/main/java/com/dbx/agent/exasol/ExasolAgent.java`](agents/drivers/exasol/src/main/java/com/dbx/agent/exasol/ExasolAgent.java) |
| 204 | ✓ | [`agents/drivers/firebird/build.gradle`](agents/drivers/firebird/build.gradle) |
| 205 | ✓ | [`agents/drivers/firebird/src/main/java/com/dbx/agent/firebird/FirebirdAgent.java`](agents/drivers/firebird/src/main/java/com/dbx/agent/firebird/FirebirdAgent.java) |
| 206 | ✓ | [`agents/drivers/firebird/src/test/java/com/dbx/agent/firebird/FirebirdAgentTest.java`](agents/drivers/firebird/src/test/java/com/dbx/agent/firebird/FirebirdAgentTest.java) |
| 207 | ✓ | [`agents/drivers/gbase8a/build.gradle`](agents/drivers/gbase8a/build.gradle) |
| 208 | ✓ | [`agents/drivers/gbase8a/libs/gbase-connector-java-9.5.0.10-build1-bin.jar`](agents/drivers/gbase8a/libs/gbase-connector-java-9.5.0.10-build1-bin.jar) |
| 209 | ✓ | [`agents/drivers/gbase8a/src/main/java/com/dbx/agent/gbase8a/Gbase8aAgent.java`](agents/drivers/gbase8a/src/main/java/com/dbx/agent/gbase8a/Gbase8aAgent.java) |
| 210 | ✓ | [`agents/drivers/gbase8a/src/test/java/com/dbx/agent/gbase8a/Gbase8aAgentTest.java`](agents/drivers/gbase8a/src/test/java/com/dbx/agent/gbase8a/Gbase8aAgentTest.java) |
| 211 | ✓ | [`agents/drivers/gbase8s/build.gradle`](agents/drivers/gbase8s/build.gradle) |
| 212 | ✓ | [`agents/drivers/gbase8s/libs/gbasedbt-jdbc.jar`](agents/drivers/gbase8s/libs/gbasedbt-jdbc.jar) |
| 213 | ✓ | [`agents/drivers/gbase8s/src/main/java/com/dbx/agent/gbase8s/Gbase8sAgent.java`](agents/drivers/gbase8s/src/main/java/com/dbx/agent/gbase8s/Gbase8sAgent.java) |
| 214 | ✓ | [`agents/drivers/gbase8s/src/test/java/com/dbx/agent/gbase8s/Gbase8sAgentTest.java`](agents/drivers/gbase8s/src/test/java/com/dbx/agent/gbase8s/Gbase8sAgentTest.java) |
| 215 | ✓ | [`agents/drivers/goldendb/build.gradle`](agents/drivers/goldendb/build.gradle) |
| 216 | ✓ | [`agents/drivers/goldendb/libs/.gitkeep`](agents/drivers/goldendb/libs/.gitkeep) |
| 217 | ✓ | [`agents/drivers/goldendb/src/main/java/com/dbx/agent/goldendb/GoldendbAgent.java`](agents/drivers/goldendb/src/main/java/com/dbx/agent/goldendb/GoldendbAgent.java) |
| 218 | ✓ | [`agents/drivers/goldendb/src/test/java/com/dbx/agent/goldendb/GoldendbAgentMetadataTest.java`](agents/drivers/goldendb/src/test/java/com/dbx/agent/goldendb/GoldendbAgentMetadataTest.java) |
| 219 | ✓ | [`agents/drivers/goldendb/src/test/java/com/dbx/agent/goldendb/GoldendbAgentTest.java`](agents/drivers/goldendb/src/test/java/com/dbx/agent/goldendb/GoldendbAgentTest.java) |
| 220 | ✓ | [`agents/drivers/h2-legacy/build.gradle`](agents/drivers/h2-legacy/build.gradle) |
| 221 | ✓ | [`agents/drivers/h2-legacy/src/main/java/com/dbx/agent/h2legacy/H2LegacyAgent.java`](agents/drivers/h2-legacy/src/main/java/com/dbx/agent/h2legacy/H2LegacyAgent.java) |
| 222 | ✓ | [`agents/drivers/h2/build.gradle`](agents/drivers/h2/build.gradle) |
| 223 | ✓ | [`agents/drivers/h2/src/main/java/com/dbx/agent/h2/H2Agent.java`](agents/drivers/h2/src/main/java/com/dbx/agent/h2/H2Agent.java) |
| 224 | ✓ | [`agents/drivers/h2/src/main/java/com/dbx/agent/h2/H2DriverLoader.java`](agents/drivers/h2/src/main/java/com/dbx/agent/h2/H2DriverLoader.java) |
| 225 | ✓ | [`agents/drivers/h2/src/main/java/com/dbx/agent/h2/H2DriverVersion.java`](agents/drivers/h2/src/main/java/com/dbx/agent/h2/H2DriverVersion.java) |
| 226 | ✓ | [`agents/drivers/h2/src/main/java/com/dbx/agent/h2/H2FileFormatDetector.java`](agents/drivers/h2/src/main/java/com/dbx/agent/h2/H2FileFormatDetector.java) |
| 227 | ✓ | [`agents/drivers/h2/src/test/java/com/dbx/agent/h2/H2AgentProcessTest.java`](agents/drivers/h2/src/test/java/com/dbx/agent/h2/H2AgentProcessTest.java) |
| 228 | ✓ | [`agents/drivers/h2/src/test/java/com/dbx/agent/h2/H2AgentTest.java`](agents/drivers/h2/src/test/java/com/dbx/agent/h2/H2AgentTest.java) |
| 229 | ✓ | [`agents/drivers/highgo/build.gradle`](agents/drivers/highgo/build.gradle) |
| 230 | ✓ | [`agents/drivers/highgo/src/main/java/com/dbx/agent/highgo/HighgoAgent.java`](agents/drivers/highgo/src/main/java/com/dbx/agent/highgo/HighgoAgent.java) |
| 231 | ✓ | [`agents/drivers/highgo/src/test/java/com/dbx/agent/highgo/HighgoAgentTest.java`](agents/drivers/highgo/src/test/java/com/dbx/agent/highgo/HighgoAgentTest.java) |
| 232 | ✓ | [`agents/drivers/hive-go/bench/agent_compare.py`](agents/drivers/hive-go/bench/agent_compare.py) |
| 233 | ✓ | [`agents/drivers/hive-go/bench/functional_probe.py`](agents/drivers/hive-go/bench/functional_probe.py) |
| 234 | ✓ | [`agents/drivers/hive-go/bench/kdc_fixture/main.go`](agents/drivers/hive-go/bench/kdc_fixture/main.go) |
| 235 | ✓ | [`agents/drivers/hive-go/bench/README.md`](agents/drivers/hive-go/bench/README.md) |
| 236 | ✓ | [`agents/drivers/hive-go/config_test.go`](agents/drivers/hive-go/config_test.go) |
| 237 | ✓ | [`agents/drivers/hive-go/config.go`](agents/drivers/hive-go/config.go) |
| 238 | ✓ | [`agents/drivers/hive-go/connector_test.go`](agents/drivers/hive-go/connector_test.go) |
| 239 | ✓ | [`agents/drivers/hive-go/connector.go`](agents/drivers/hive-go/connector.go) |
| 240 | ✓ | [`agents/drivers/hive-go/discovery_test.go`](agents/drivers/hive-go/discovery_test.go) |
| 241 | ✓ | [`agents/drivers/hive-go/discovery.go`](agents/drivers/hive-go/discovery.go) |
| 242 | ✓ | [`agents/drivers/hive-go/go.mod`](agents/drivers/hive-go/go.mod) |
| 243 | ✓ | [`agents/drivers/hive-go/go.sum`](agents/drivers/hive-go/go.sum) |
| 244 | ✓ | [`agents/drivers/hive-go/init_test.go`](agents/drivers/hive-go/init_test.go) |
| 245 | ✓ | [`agents/drivers/hive-go/kerberos_defaults_unix.go`](agents/drivers/hive-go/kerberos_defaults_unix.go) |
| 246 | ✓ | [`agents/drivers/hive-go/kerberos_defaults_windows.go`](agents/drivers/hive-go/kerberos_defaults_windows.go) |
| 247 | ✓ | [`agents/drivers/hive-go/main.go`](agents/drivers/hive-go/main.go) |
| 248 | ✓ | [`agents/drivers/hive-go/metadata_test.go`](agents/drivers/hive-go/metadata_test.go) |
| 249 | ✓ | [`agents/drivers/hive-go/metadata.go`](agents/drivers/hive-go/metadata.go) |
| 250 | ✓ | [`agents/drivers/hive-go/MIGRATION_PARITY.md`](agents/drivers/hive-go/MIGRATION_PARITY.md) |
| 251 | ✓ | [`agents/drivers/hive-go/protocol_error.go`](agents/drivers/hive-go/protocol_error.go) |
| 252 | ✓ | [`agents/drivers/hive-go/query_test.go`](agents/drivers/hive-go/query_test.go) |
| 253 | ✓ | [`agents/drivers/hive-go/query.go`](agents/drivers/hive-go/query.go) |
| 254 | ✓ | [`agents/drivers/hive-go/zookeeper_protocol_test.go`](agents/drivers/hive-go/zookeeper_protocol_test.go) |
| 255 | ✓ | [`agents/drivers/hive-go/zookeeper_protocol.go`](agents/drivers/hive-go/zookeeper_protocol.go) |
| 256 | ✓ | [`agents/drivers/hive-go/zookeeper_tls_test.go`](agents/drivers/hive-go/zookeeper_tls_test.go) |
| 257 | ✓ | [`agents/drivers/hive-go/zookeeper_tls.go`](agents/drivers/hive-go/zookeeper_tls.go) |
| 258 | ✓ | [`agents/drivers/ignite/build.gradle`](agents/drivers/ignite/build.gradle) |
| 259 | ✓ | [`agents/drivers/ignite/src/main/java/com/dbx/agent/ignite/IgniteAgent.java`](agents/drivers/ignite/src/main/java/com/dbx/agent/ignite/IgniteAgent.java) |
| 260 | ✓ | [`agents/drivers/ignite/src/test/java/com/dbx/agent/ignite/IgniteAgentTest.java`](agents/drivers/ignite/src/test/java/com/dbx/agent/ignite/IgniteAgentTest.java) |
| 261 | ✓ | [`agents/drivers/ignite3/build.gradle`](agents/drivers/ignite3/build.gradle) |
| 262 | ✓ | [`agents/drivers/ignite3/src/main/java/com/dbx/agent/ignite3/Ignite3Agent.java`](agents/drivers/ignite3/src/main/java/com/dbx/agent/ignite3/Ignite3Agent.java) |
| 263 | ✓ | [`agents/drivers/ignite3/src/test/java/com/dbx/agent/ignite3/Ignite3AgentTest.java`](agents/drivers/ignite3/src/test/java/com/dbx/agent/ignite3/Ignite3AgentTest.java) |
| 264 | ✓ | [`agents/drivers/ignite3/src/test/java/com/dbx/agent/ignite3/Ignite3AgentUrlTest.java`](agents/drivers/ignite3/src/test/java/com/dbx/agent/ignite3/Ignite3AgentUrlTest.java) |
| 265 | ✓ | [`agents/drivers/informix/build.gradle`](agents/drivers/informix/build.gradle) |
| 266 | ✓ | [`agents/drivers/informix/src/main/java/com/dbx/agent/informix/InformixAgent.java`](agents/drivers/informix/src/main/java/com/dbx/agent/informix/InformixAgent.java) |
| 267 | ✓ | [`agents/drivers/informix/src/test/java/com/dbx/agent/informix/InformixAgentExecutionTest.java`](agents/drivers/informix/src/test/java/com/dbx/agent/informix/InformixAgentExecutionTest.java) |
| 268 | ✓ | [`agents/drivers/informix/src/test/java/com/dbx/agent/informix/InformixAgentTest.java`](agents/drivers/informix/src/test/java/com/dbx/agent/informix/InformixAgentTest.java) |
| 269 | ✓ | [`agents/drivers/iotdb/bench/build.gradle`](agents/drivers/iotdb/bench/build.gradle) |
| 270 | ✓ | [`agents/drivers/iotdb/bench/go/go.mod`](agents/drivers/iotdb/bench/go/go.mod) |
| 271 | ✓ | [`agents/drivers/iotdb/bench/go/go.sum`](agents/drivers/iotdb/bench/go/go.sum) |
| 272 | ✓ | [`agents/drivers/iotdb/bench/go/main.go`](agents/drivers/iotdb/bench/go/main.go) |
| 273 | ✓ | [`agents/drivers/iotdb/bench/java/com/dbx/agent/iotdb/bench/JdbcDriverBenchmark.java`](agents/drivers/iotdb/bench/java/com/dbx/agent/iotdb/bench/JdbcDriverBenchmark.java) |
| 274 | ✓ | [`agents/drivers/iotdb/bench/README.md`](agents/drivers/iotdb/bench/README.md) |
| 275 | ✓ | [`agents/drivers/iotdb/bench/results/iotdb-2.0.8-macos-arm64.json`](agents/drivers/iotdb/bench/results/iotdb-2.0.8-macos-arm64.json) |
| 276 | ✓ | [`agents/drivers/iotdb/bench/results/README.md`](agents/drivers/iotdb/bench/results/README.md) |
| 277 | ✓ | [`agents/drivers/iotdb/bench/run.py`](agents/drivers/iotdb/bench/run.py) |
| 278 | ✓ | [`agents/drivers/iotdb/bench/settings.gradle`](agents/drivers/iotdb/bench/settings.gradle) |
| 279 | ✓ | [`agents/drivers/iotdb/driver.go`](agents/drivers/iotdb/driver.go) |
| 280 | ✓ | [`agents/drivers/iotdb/go.mod`](agents/drivers/iotdb/go.mod) |
| 281 | ✓ | [`agents/drivers/iotdb/go.sum`](agents/drivers/iotdb/go.sum) |
| 282 | ✓ | [`agents/drivers/iotdb/integration_test.go`](agents/drivers/iotdb/integration_test.go) |
| 283 | ✓ | [`agents/drivers/iotdb/main_test.go`](agents/drivers/iotdb/main_test.go) |
| 284 | ✓ | [`agents/drivers/iotdb/main.go`](agents/drivers/iotdb/main.go) |
| 285 | ✓ | [`agents/drivers/iotdb/metadata.go`](agents/drivers/iotdb/metadata.go) |
| 286 | ✓ | [`agents/drivers/iotdb/protocol_error.go`](agents/drivers/iotdb/protocol_error.go) |
| 287 | ✓ | [`agents/drivers/iotdb/query.go`](agents/drivers/iotdb/query.go) |
| 288 | ✓ | [`agents/drivers/iotdb/README.md`](agents/drivers/iotdb/README.md) |
| 289 | ✓ | [`agents/drivers/iris/build.gradle`](agents/drivers/iris/build.gradle) |
| 290 | ✓ | [`agents/drivers/iris/src/main/java/com/dbx/agent/iris/IrisAgent.java`](agents/drivers/iris/src/main/java/com/dbx/agent/iris/IrisAgent.java) |
| 291 | ✓ | [`agents/drivers/iris/src/test/java/com/dbx/agent/iris/IrisAgentQueryPrefetchTest.java`](agents/drivers/iris/src/test/java/com/dbx/agent/iris/IrisAgentQueryPrefetchTest.java) |
| 292 | ✓ | [`agents/drivers/iris/src/test/java/com/dbx/agent/iris/IrisAgentTest.java`](agents/drivers/iris/src/test/java/com/dbx/agent/iris/IrisAgentTest.java) |
| 293 | ✓ | [`agents/drivers/kafka/build.gradle`](agents/drivers/kafka/build.gradle) |
| 294 | ✓ | [`agents/drivers/kafka/src/main/java/com/dbx/agent/kafka/DbxInsecureTrustManagerFactory.java`](agents/drivers/kafka/src/main/java/com/dbx/agent/kafka/DbxInsecureTrustManagerFactory.java) |
| 295 | ✓ | [`agents/drivers/kafka/src/main/java/com/dbx/agent/kafka/KafkaAgent.java`](agents/drivers/kafka/src/main/java/com/dbx/agent/kafka/KafkaAgent.java) |
| 296 | ✓ | [`agents/drivers/kafka/src/test/java/com/dbx/agent/kafka/KafkaAgentTest.java`](agents/drivers/kafka/src/test/java/com/dbx/agent/kafka/KafkaAgentTest.java) |
| 297 | ✓ | [`agents/drivers/kingbase-go/bench/agent_compare.go`](agents/drivers/kingbase-go/bench/agent_compare.go) |
| 298 | ✓ | [`agents/drivers/kingbase-go/go.mod`](agents/drivers/kingbase-go/go.mod) |
| 299 | ✓ | [`agents/drivers/kingbase-go/go.sum`](agents/drivers/kingbase-go/go.sum) |
| 300 | ✓ | [`agents/drivers/kingbase-go/integration_test.go`](agents/drivers/kingbase-go/integration_test.go) |
| 301 | ✓ | [`agents/drivers/kingbase-go/kingbase_metadata.go`](agents/drivers/kingbase-go/kingbase_metadata.go) |
| 302 | ✓ | [`agents/drivers/kingbase-go/main_test.go`](agents/drivers/kingbase-go/main_test.go) |
| 303 | ✓ | [`agents/drivers/kingbase-go/main.go`](agents/drivers/kingbase-go/main.go) |
| 304 | ✓ | [`agents/drivers/kylin/build.gradle`](agents/drivers/kylin/build.gradle) |
| 305 | ✓ | [`agents/drivers/kylin/src/main/java/com/dbx/agent/kylin/KylinAgent.java`](agents/drivers/kylin/src/main/java/com/dbx/agent/kylin/KylinAgent.java) |
| 306 | ✓ | [`agents/drivers/kylin/src/test/java/com/dbx/agent/kylin/KylinAgentTest.java`](agents/drivers/kylin/src/test/java/com/dbx/agent/kylin/KylinAgentTest.java) |
| 307 | ✓ | [`agents/drivers/mongodb/build.gradle`](agents/drivers/mongodb/build.gradle) |
| 308 | ✓ | [`agents/drivers/mongodb/src/main/java/com/dbx/agent/mongodb/MongoAgent.java`](agents/drivers/mongodb/src/main/java/com/dbx/agent/mongodb/MongoAgent.java) |
| 309 | ✓ | [`agents/drivers/mongodb/src/test/java/com/dbx/agent/mongodb/MongoAgentTest.java`](agents/drivers/mongodb/src/test/java/com/dbx/agent/mongodb/MongoAgentTest.java) |
| 310 | ✓ | [`agents/drivers/neo4j-go/driver.go`](agents/drivers/neo4j-go/driver.go) |
| 311 | ✓ | [`agents/drivers/neo4j-go/go.mod`](agents/drivers/neo4j-go/go.mod) |
| 312 | ✓ | [`agents/drivers/neo4j-go/go.sum`](agents/drivers/neo4j-go/go.sum) |
| 313 | ✓ | [`agents/drivers/neo4j-go/integration_test.go`](agents/drivers/neo4j-go/integration_test.go) |
| 314 | ✓ | [`agents/drivers/neo4j-go/main_test.go`](agents/drivers/neo4j-go/main_test.go) |
| 315 | ✓ | [`agents/drivers/neo4j-go/main.go`](agents/drivers/neo4j-go/main.go) |
| 316 | ✓ | [`agents/drivers/neo4j-go/metadata.go`](agents/drivers/neo4j-go/metadata.go) |
| 317 | ✓ | [`agents/drivers/neo4j-go/protocol_error.go`](agents/drivers/neo4j-go/protocol_error.go) |
| 318 | ✓ | [`agents/drivers/neo4j-go/query.go`](agents/drivers/neo4j-go/query.go) |
| 319 | ✓ | [`agents/drivers/neo4j-go/README.md`](agents/drivers/neo4j-go/README.md) |
| 320 | ✓ | [`agents/drivers/oceanbase-oracle/build.gradle`](agents/drivers/oceanbase-oracle/build.gradle) |
| 321 | ✓ | [`agents/drivers/oceanbase-oracle/src/main/java/com/dbx/agent/oceanbaseoracle/OceanBaseOracleAgent.java`](agents/drivers/oceanbase-oracle/src/main/java/com/dbx/agent/oceanbaseoracle/OceanBaseOracleAgent.java) |
| 322 | ✓ | [`agents/drivers/oceanbase-oracle/src/test/java/com/dbx/agent/oceanbaseoracle/OceanBaseOracleAgentTest.java`](agents/drivers/oceanbase-oracle/src/test/java/com/dbx/agent/oceanbaseoracle/OceanBaseOracleAgentTest.java) |
| 323 | ✓ | [`agents/drivers/oracle-go/.gitignore`](agents/drivers/oracle-go/.gitignore) |
| 324 | ✓ | [`agents/drivers/oracle-go/go.mod`](agents/drivers/oracle-go/go.mod) |
| 325 | ✓ | [`agents/drivers/oracle-go/go.sum`](agents/drivers/oracle-go/go.sum) |
| 326 | ✓ | [`agents/drivers/oracle-go/main_test.go`](agents/drivers/oracle-go/main_test.go) |
| 327 | ✓ | [`agents/drivers/oracle-go/main.go`](agents/drivers/oracle-go/main.go) |
| 328 | ✓ | [`agents/drivers/oracle-go/README.md`](agents/drivers/oracle-go/README.md) |
| 329 | ✓ | [`agents/drivers/oracle-go/tns_test.go`](agents/drivers/oracle-go/tns_test.go) |
| 330 | ✓ | [`agents/drivers/oracle-go/tns.go`](agents/drivers/oracle-go/tns.go) |
| 331 | ✓ | [`agents/drivers/oscar/build.gradle`](agents/drivers/oscar/build.gradle) |
| 332 | ✓ | [`agents/drivers/oscar/libs/oscarJDBC8.jar`](agents/drivers/oscar/libs/oscarJDBC8.jar) |
| 333 | ✓ | [`agents/drivers/oscar/src/main/java/com/dbx/agent/oscar/OscarAgent.java`](agents/drivers/oscar/src/main/java/com/dbx/agent/oscar/OscarAgent.java) |
| 334 | ✓ | [`agents/drivers/oscar/src/test/java/com/dbx/agent/oscar/OscarAgentTest.java`](agents/drivers/oscar/src/test/java/com/dbx/agent/oscar/OscarAgentTest.java) |
| 335 | ✓ | [`agents/drivers/rabbitmq/bench/agent_compare.go`](agents/drivers/rabbitmq/bench/agent_compare.go) |
| 336 | ✓ | [`agents/drivers/rabbitmq/go.mod`](agents/drivers/rabbitmq/go.mod) |
| 337 | ✓ | [`agents/drivers/rabbitmq/go.sum`](agents/drivers/rabbitmq/go.sum) |
| 338 | ✓ | [`agents/drivers/rabbitmq/helpers_test.go`](agents/drivers/rabbitmq/helpers_test.go) |
| 339 | ✓ | [`agents/drivers/rabbitmq/helpers.go`](agents/drivers/rabbitmq/helpers.go) |
| 340 | ✓ | [`agents/drivers/rabbitmq/integration_test.go`](agents/drivers/rabbitmq/integration_test.go) |
| 341 | ✓ | [`agents/drivers/rabbitmq/main.go`](agents/drivers/rabbitmq/main.go) |
| 342 | ✓ | [`agents/drivers/rabbitmq/management_test.go`](agents/drivers/rabbitmq/management_test.go) |
| 343 | ✓ | [`agents/drivers/rabbitmq/management.go`](agents/drivers/rabbitmq/management.go) |
| 344 | ✓ | [`agents/drivers/rabbitmq/mapping_test.go`](agents/drivers/rabbitmq/mapping_test.go) |
| 345 | ✓ | [`agents/drivers/rabbitmq/operations.go`](agents/drivers/rabbitmq/operations.go) |
| 346 | ✓ | [`agents/drivers/rocketmq/acl.go`](agents/drivers/rocketmq/acl.go) |
| 347 | ✓ | [`agents/drivers/rocketmq/cluster.go`](agents/drivers/rocketmq/cluster.go) |
| 348 | ✓ | [`agents/drivers/rocketmq/connection_test.go`](agents/drivers/rocketmq/connection_test.go) |
| 349 | ✓ | [`agents/drivers/rocketmq/connection.go`](agents/drivers/rocketmq/connection.go) |
| 350 | ✓ | [`agents/drivers/rocketmq/consumers_test.go`](agents/drivers/rocketmq/consumers_test.go) |
| 351 | ✓ | [`agents/drivers/rocketmq/consumers.go`](agents/drivers/rocketmq/consumers.go) |
| 352 | ✓ | [`agents/drivers/rocketmq/go.mod`](agents/drivers/rocketmq/go.mod) |
| 353 | ✓ | [`agents/drivers/rocketmq/go.sum`](agents/drivers/rocketmq/go.sum) |
| 354 | ✓ | [`agents/drivers/rocketmq/helpers.go`](agents/drivers/rocketmq/helpers.go) |
| 355 | ✓ | [`agents/drivers/rocketmq/integration_test.go`](agents/drivers/rocketmq/integration_test.go) |
| 356 | ✓ | [`agents/drivers/rocketmq/main_test.go`](agents/drivers/rocketmq/main_test.go) |
| 357 | ✓ | [`agents/drivers/rocketmq/main.go`](agents/drivers/rocketmq/main.go) |
| 358 | ✓ | [`agents/drivers/rocketmq/messages_test.go`](agents/drivers/rocketmq/messages_test.go) |
| 359 | ✓ | [`agents/drivers/rocketmq/messages.go`](agents/drivers/rocketmq/messages.go) |
| 360 | ✓ | [`agents/drivers/rocketmq/remoting.go`](agents/drivers/rocketmq/remoting.go) |
| 361 | ✓ | [`agents/drivers/rocketmq/routing_test.go`](agents/drivers/rocketmq/routing_test.go) |
| 362 | ✓ | [`agents/drivers/rocketmq/routing.go`](agents/drivers/rocketmq/routing.go) |
| 363 | ✓ | [`agents/drivers/rocketmq/scripts/run-integration.sh`](agents/drivers/rocketmq/scripts/run-integration.sh) |
| 364 | ✓ | [`agents/drivers/rocketmq/server_test.go`](agents/drivers/rocketmq/server_test.go) |
| 365 | ✓ | [`agents/drivers/rocketmq/server.go`](agents/drivers/rocketmq/server.go) |
| 366 | ✓ | [`agents/drivers/rocketmq/topics_test.go`](agents/drivers/rocketmq/topics_test.go) |
| 367 | ✓ | [`agents/drivers/rocketmq/topics.go`](agents/drivers/rocketmq/topics.go) |
| 368 | ✓ | [`agents/drivers/saphana/build.gradle`](agents/drivers/saphana/build.gradle) |
| 369 | ✓ | [`agents/drivers/saphana/src/main/java/com/dbx/agent/saphana/SapHanaAgent.java`](agents/drivers/saphana/src/main/java/com/dbx/agent/saphana/SapHanaAgent.java) |
| 370 | ✓ | [`agents/drivers/saphana/src/test/java/com/dbx/agent/saphana/SapHanaAgentTest.java`](agents/drivers/saphana/src/test/java/com/dbx/agent/saphana/SapHanaAgentTest.java) |
| 371 | ✓ | [`agents/drivers/snowflake/build.gradle`](agents/drivers/snowflake/build.gradle) |
| 372 | ✓ | [`agents/drivers/snowflake/src/main/java/com/dbx/agent/snowflake/SnowflakeAgent.java`](agents/drivers/snowflake/src/main/java/com/dbx/agent/snowflake/SnowflakeAgent.java) |
| 373 | ✓ | [`agents/drivers/snowflake/src/test/java/com/dbx/agent/snowflake/SnowflakeAgentMetadataTest.java`](agents/drivers/snowflake/src/test/java/com/dbx/agent/snowflake/SnowflakeAgentMetadataTest.java) |
| 374 | ✓ | [`agents/drivers/snowflake/src/test/java/com/dbx/agent/snowflake/SnowflakeAgentTest.java`](agents/drivers/snowflake/src/test/java/com/dbx/agent/snowflake/SnowflakeAgentTest.java) |
| 375 | ✓ | [`agents/drivers/spanner/build.gradle`](agents/drivers/spanner/build.gradle) |
| 376 | ✓ | [`agents/drivers/spanner/src/main/java/com/dbx/agent/spanner/SpannerAgent.java`](agents/drivers/spanner/src/main/java/com/dbx/agent/spanner/SpannerAgent.java) |
| 377 | ✓ | [`agents/drivers/spanner/src/test/java/com/dbx/agent/spanner/SpannerAgentTest.java`](agents/drivers/spanner/src/test/java/com/dbx/agent/spanner/SpannerAgentTest.java) |
| 378 | ✓ | [`agents/drivers/spark/build.gradle`](agents/drivers/spark/build.gradle) |
| 379 | ✓ | [`agents/drivers/spark/src/main/java/com/dbx/agent/spark/SparkAgent.java`](agents/drivers/spark/src/main/java/com/dbx/agent/spark/SparkAgent.java) |
| 380 | ✓ | [`agents/drivers/spark/src/test/java/com/dbx/agent/spark/SparkAgentTest.java`](agents/drivers/spark/src/test/java/com/dbx/agent/spark/SparkAgentTest.java) |
| 381 | ✓ | [`agents/drivers/sqlserver-legacy/build.gradle`](agents/drivers/sqlserver-legacy/build.gradle) |
| 382 | ✓ | [`agents/drivers/sqlserver-legacy/src/main/java/com/dbx/agent/sqlserverlegacy/SqlServerLegacyAgent.java`](agents/drivers/sqlserver-legacy/src/main/java/com/dbx/agent/sqlserverlegacy/SqlServerLegacyAgent.java) |
| 383 | ✓ | [`agents/drivers/sqlserver-legacy/src/test/java/com/dbx/agent/sqlserverlegacy/SqlServerLegacyAgentTest.java`](agents/drivers/sqlserver-legacy/src/test/java/com/dbx/agent/sqlserverlegacy/SqlServerLegacyAgentTest.java) |
| 384 | ✓ | [`agents/drivers/sundb/build.gradle`](agents/drivers/sundb/build.gradle) |
| 385 | ✓ | [`agents/drivers/sundb/src/main/java/com/dbx/agent/sundb/SundbAgent.java`](agents/drivers/sundb/src/main/java/com/dbx/agent/sundb/SundbAgent.java) |
| 386 | ✓ | [`agents/drivers/sundb/src/test/java/com/dbx/agent/sundb/SundbAgentMetadataTest.java`](agents/drivers/sundb/src/test/java/com/dbx/agent/sundb/SundbAgentMetadataTest.java) |
| 387 | ✓ | [`agents/drivers/sundb/src/test/java/com/dbx/agent/sundb/SundbAgentTest.java`](agents/drivers/sundb/src/test/java/com/dbx/agent/sundb/SundbAgentTest.java) |
| 388 | ✓ | [`agents/drivers/tdengine/.gitignore`](agents/drivers/tdengine/.gitignore) |
| 389 | ✓ | [`agents/drivers/tdengine/Cargo.lock`](agents/drivers/tdengine/Cargo.lock) |
| 390 | ✓ | [`agents/drivers/tdengine/Cargo.toml`](agents/drivers/tdengine/Cargo.toml) |
| 391 | ✓ | [`agents/drivers/tdengine/src/config.rs`](agents/drivers/tdengine/src/config.rs) |
| 392 | ✓ | [`agents/drivers/tdengine/src/driver.rs`](agents/drivers/tdengine/src/driver.rs) |
| 393 | ✓ | [`agents/drivers/tdengine/src/lib.rs`](agents/drivers/tdengine/src/lib.rs) |
| 394 | ✓ | [`agents/drivers/tdengine/src/main.rs`](agents/drivers/tdengine/src/main.rs) |
| 395 | ✓ | [`agents/drivers/tdengine/src/model.rs`](agents/drivers/tdengine/src/model.rs) |
| 396 | ✓ | [`agents/drivers/tdengine/src/runtime.rs`](agents/drivers/tdengine/src/runtime.rs) |
| 397 | ✓ | [`agents/drivers/tdengine/src/value.rs`](agents/drivers/tdengine/src/value.rs) |
| 398 | ✓ | [`agents/drivers/tdengine/tests/live.rs`](agents/drivers/tdengine/tests/live.rs) |
| 399 | ✓ | [`agents/drivers/tdengine/tests/protocol.rs`](agents/drivers/tdengine/tests/protocol.rs) |
| 400 | ✓ | [`agents/drivers/teradata/build.gradle`](agents/drivers/teradata/build.gradle) |
| 401 | ✓ | [`agents/drivers/teradata/src/main/java/com/dbx/agent/teradata/TeradataAgent.java`](agents/drivers/teradata/src/main/java/com/dbx/agent/teradata/TeradataAgent.java) |
| 402 | ✓ | [`agents/drivers/trino/build.gradle`](agents/drivers/trino/build.gradle) |
| 403 | ✓ | [`agents/drivers/trino/src/main/java/com/dbx/agent/trino/TrinoAgent.java`](agents/drivers/trino/src/main/java/com/dbx/agent/trino/TrinoAgent.java) |
| 404 | ✓ | [`agents/drivers/trino/src/test/java/com/dbx/agent/trino/TrinoAgentTest.java`](agents/drivers/trino/src/test/java/com/dbx/agent/trino/TrinoAgentTest.java) |
| 405 | ✓ | [`agents/drivers/uxdb/build.gradle`](agents/drivers/uxdb/build.gradle) |
| 406 | ✓ | [`agents/drivers/uxdb/libs/uxdbjdbc-2.1.2.3p.jre8.jar`](agents/drivers/uxdb/libs/uxdbjdbc-2.1.2.3p.jre8.jar) |
| 407 | ✓ | [`agents/drivers/uxdb/src/main/java/com/dbx/agent/uxdb/UxdbAgent.java`](agents/drivers/uxdb/src/main/java/com/dbx/agent/uxdb/UxdbAgent.java) |
| 408 | ✓ | [`agents/drivers/uxdb/src/test/java/com/dbx/agent/uxdb/UxdbAgentTest.java`](agents/drivers/uxdb/src/test/java/com/dbx/agent/uxdb/UxdbAgentTest.java) |
| 409 | ✓ | [`agents/drivers/vastbase-go/bench/agent_compare.go`](agents/drivers/vastbase-go/bench/agent_compare.go) |
| 410 | ✓ | [`agents/drivers/vastbase-go/bench/direct/main.go`](agents/drivers/vastbase-go/bench/direct/main.go) |
| 411 | ✓ | [`agents/drivers/vastbase-go/bench/README.md`](agents/drivers/vastbase-go/bench/README.md) |
| 412 | ✓ | [`agents/drivers/vastbase-go/connection_info_test.go`](agents/drivers/vastbase-go/connection_info_test.go) |
| 413 | ✓ | [`agents/drivers/vastbase-go/connection_state_test.go`](agents/drivers/vastbase-go/connection_state_test.go) |
| 414 | ✓ | [`agents/drivers/vastbase-go/connection_state.go`](agents/drivers/vastbase-go/connection_state.go) |
| 415 | ✓ | [`agents/drivers/vastbase-go/driver.go`](agents/drivers/vastbase-go/driver.go) |
| 416 | ✓ | [`agents/drivers/vastbase-go/go.mod`](agents/drivers/vastbase-go/go.mod) |
| 417 | ✓ | [`agents/drivers/vastbase-go/go.sum`](agents/drivers/vastbase-go/go.sum) |
| 418 | ✓ | [`agents/drivers/vastbase-go/integration_test.go`](agents/drivers/vastbase-go/integration_test.go) |
| 419 | ✓ | [`agents/drivers/vastbase-go/main_test.go`](agents/drivers/vastbase-go/main_test.go) |
| 420 | ✓ | [`agents/drivers/vastbase-go/main.go`](agents/drivers/vastbase-go/main.go) |
| 421 | ✓ | [`agents/drivers/vastbase-go/protocol_error_test.go`](agents/drivers/vastbase-go/protocol_error_test.go) |
| 422 | ✓ | [`agents/drivers/vastbase-go/protocol_error.go`](agents/drivers/vastbase-go/protocol_error.go) |
| 423 | ✓ | [`agents/drivers/vastbase-go/README.md`](agents/drivers/vastbase-go/README.md) |
| 424 | ✓ | [`agents/drivers/vastbase-go/runtime_pool_test.go`](agents/drivers/vastbase-go/runtime_pool_test.go) |
| 425 | ✓ | [`agents/drivers/vastbase-go/runtime_pool.go`](agents/drivers/vastbase-go/runtime_pool.go) |
| 426 | ✓ | [`agents/drivers/vastbase-go/spatial_test.go`](agents/drivers/vastbase-go/spatial_test.go) |
| 427 | ✓ | [`agents/drivers/vastbase-go/spatial.go`](agents/drivers/vastbase-go/spatial.go) |
| 428 | ✓ | [`agents/drivers/vastbase-go/vastbase_metadata_test.go`](agents/drivers/vastbase-go/vastbase_metadata_test.go) |
| 429 | ✓ | [`agents/drivers/vastbase-go/vastbase_metadata.go`](agents/drivers/vastbase-go/vastbase_metadata.go) |
| 430 | ✓ | [`agents/drivers/vertica/build.gradle`](agents/drivers/vertica/build.gradle) |
| 431 | ✓ | [`agents/drivers/vertica/src/main/java/com/dbx/agent/vertica/VerticaAgent.java`](agents/drivers/vertica/src/main/java/com/dbx/agent/vertica/VerticaAgent.java) |
| 432 | ✓ | [`agents/drivers/xugu/common_integration_live_test.go`](agents/drivers/xugu/common_integration_live_test.go) |
| 433 | ✓ | [`agents/drivers/xugu/data_types_live_test.go`](agents/drivers/xugu/data_types_live_test.go) |
| 434 | ✓ | [`agents/drivers/xugu/go.mod`](agents/drivers/xugu/go.mod) |
| 435 | ✓ | [`agents/drivers/xugu/go.sum`](agents/drivers/xugu/go.sum) |
| 436 | ✓ | [`agents/drivers/xugu/index_partition_live_test.go`](agents/drivers/xugu/index_partition_live_test.go) |
| 437 | ✓ | [`agents/drivers/xugu/main_test.go`](agents/drivers/xugu/main_test.go) |
| 438 | ✓ | [`agents/drivers/xugu/main.go`](agents/drivers/xugu/main.go) |
| 439 | ✓ | [`agents/drivers/xugu/package_members_test.go`](agents/drivers/xugu/package_members_test.go) |
| 440 | ✓ | [`agents/drivers/xugu/package_members.go`](agents/drivers/xugu/package_members.go) |
| 441 | ✓ | [`agents/drivers/xugu/protocol_error_live_test.go`](agents/drivers/xugu/protocol_error_live_test.go) |
| 442 | ✓ | [`agents/drivers/xugu/protocol_error_test.go`](agents/drivers/xugu/protocol_error_test.go) |
| 443 | ✓ | [`agents/drivers/xugu/protocol_error.go`](agents/drivers/xugu/protocol_error.go) |
| 444 | ✓ | [`agents/drivers/xugu/README.md`](agents/drivers/xugu/README.md) |
| 445 | ✓ | [`agents/drivers/xugu/scheduler_jobs_live_test.go`](agents/drivers/xugu/scheduler_jobs_live_test.go) |
| 446 | ✓ | [`agents/drivers/xugu/spatial_index_live_test.go`](agents/drivers/xugu/spatial_index_live_test.go) |
| 447 | ✓ | [`agents/drivers/xugu/spatial_live_test.go`](agents/drivers/xugu/spatial_live_test.go) |
| 448 | ✓ | [`agents/drivers/xugu/spatial_test.go`](agents/drivers/xugu/spatial_test.go) |
| 449 | ✓ | [`agents/drivers/xugu/spatial.go`](agents/drivers/xugu/spatial.go) |
| 450 | ✓ | [`agents/drivers/xugu/synonym_scope_live_test.go`](agents/drivers/xugu/synonym_scope_live_test.go) |
| 451 | ✓ | [`agents/drivers/xugu/tablespaces_live_test.go`](agents/drivers/xugu/tablespaces_live_test.go) |
| 452 | ✓ | [`agents/drivers/xugu/tablespaces_test.go`](agents/drivers/xugu/tablespaces_test.go) |
| 453 | ✓ | [`agents/drivers/xugu/trigger_live_test.go`](agents/drivers/xugu/trigger_live_test.go) |
| 454 | ✓ | [`agents/drivers/xugu/type_members_live_test.go`](agents/drivers/xugu/type_members_live_test.go) |
| 455 | ✓ | [`agents/drivers/xugu/type_members_test.go`](agents/drivers/xugu/type_members_test.go) |
| 456 | ✓ | [`agents/drivers/xugu/type_members.go`](agents/drivers/xugu/type_members.go) |
| 457 | ✓ | [`agents/drivers/yashandb/build.gradle`](agents/drivers/yashandb/build.gradle) |
| 458 | ✓ | [`agents/drivers/yashandb/src/main/java/com/dbx/agent/yashandb/YashandbAgent.java`](agents/drivers/yashandb/src/main/java/com/dbx/agent/yashandb/YashandbAgent.java) |
| 459 | ✓ | [`agents/drivers/yashandb/src/test/java/com/dbx/agent/yashandb/YashandbAgentTest.java`](agents/drivers/yashandb/src/test/java/com/dbx/agent/yashandb/YashandbAgentTest.java) |
| 460 | ✓ | [`agents/drivers/zookeeper/agent_test.go`](agents/drivers/zookeeper/agent_test.go) |
| 461 | ✓ | [`agents/drivers/zookeeper/connection.go`](agents/drivers/zookeeper/connection.go) |
| 462 | ✓ | [`agents/drivers/zookeeper/go.mod`](agents/drivers/zookeeper/go.mod) |
| 463 | ✓ | [`agents/drivers/zookeeper/go.sum`](agents/drivers/zookeeper/go.sum) |
| 464 | ✓ | [`agents/drivers/zookeeper/integration_test.go`](agents/drivers/zookeeper/integration_test.go) |
| 465 | ✓ | [`agents/drivers/zookeeper/main.go`](agents/drivers/zookeeper/main.go) |
| 466 | ✓ | [`agents/drivers/zookeeper/operations.go`](agents/drivers/zookeeper/operations.go) |
| 467 | ✓ | [`agents/drivers/zookeeper/sasl_test.go`](agents/drivers/zookeeper/sasl_test.go) |
| 468 | ✓ | [`agents/drivers/zookeeper/sasl.go`](agents/drivers/zookeeper/sasl.go) |
| 469 | ✓ | [`agents/go-common/go-gssapi/common/channel_binding.go`](agents/go-common/go-gssapi/common/channel_binding.go) |
| 470 | ✓ | [`agents/go-common/go-gssapi/flags_test.go`](agents/go-common/go-gssapi/flags_test.go) |
| 471 | ✓ | [`agents/go-common/go-gssapi/flags.go`](agents/go-common/go-gssapi/flags.go) |
| 472 | ✓ | [`agents/go-common/go-gssapi/go.mod`](agents/go-common/go-gssapi/go.mod) |
| 473 | ✓ | [`agents/go-common/go-gssapi/go.sum`](agents/go-common/go-gssapi/go.sum) |
| 474 | ✓ | [`agents/go-common/go-gssapi/interface.go`](agents/go-common/go-gssapi/interface.go) |
| 475 | ✓ | [`agents/go-common/go-gssapi/krb5/APRep_test.go`](agents/go-common/go-gssapi/krb5/APRep_test.go) |
| 476 | ✓ | [`agents/go-common/go-gssapi/krb5/APRep.go`](agents/go-common/go-gssapi/krb5/APRep.go) |
| 477 | ✓ | [`agents/go-common/go-gssapi/krb5/context_token_test.go`](agents/go-common/go-gssapi/krb5/context_token_test.go) |
| 478 | ✓ | [`agents/go-common/go-gssapi/krb5/context_token.go`](agents/go-common/go-gssapi/krb5/context_token.go) |
| 479 | ✓ | [`agents/go-common/go-gssapi/krb5/credentials_test.go`](agents/go-common/go-gssapi/krb5/credentials_test.go) |
| 480 | ✓ | [`agents/go-common/go-gssapi/krb5/default_paths_unix.go`](agents/go-common/go-gssapi/krb5/default_paths_unix.go) |
| 481 | ✓ | [`agents/go-common/go-gssapi/krb5/default_paths_windows.go`](agents/go-common/go-gssapi/krb5/default_paths_windows.go) |
| 482 | ✓ | [`agents/go-common/go-gssapi/krb5/keyinfo_test.go`](agents/go-common/go-gssapi/krb5/keyinfo_test.go) |
| 483 | ✓ | [`agents/go-common/go-gssapi/krb5/keyinfo.go`](agents/go-common/go-gssapi/krb5/keyinfo.go) |
| 484 | ✓ | [`agents/go-common/go-gssapi/krb5/krb5_test.go`](agents/go-common/go-gssapi/krb5/krb5_test.go) |
| 485 | ✓ | [`agents/go-common/go-gssapi/krb5/krb5.go`](agents/go-common/go-gssapi/krb5/krb5.go) |
| 486 | ✓ | [`agents/go-common/go-gssapi/krb5/message_token_test.go`](agents/go-common/go-gssapi/krb5/message_token_test.go) |
| 487 | ✓ | [`agents/go-common/go-gssapi/krb5/message_token.go`](agents/go-common/go-gssapi/krb5/message_token.go) |
| 488 | ✓ | [`agents/go-common/go-gssapi/krb5/sample_test.go`](agents/go-common/go-gssapi/krb5/sample_test.go) |
| 489 | ✓ | [`agents/go-common/go-gssapi/LICENSE`](agents/go-common/go-gssapi/LICENSE) |
| 490 | ✓ | [`agents/go-common/go-gssapi/README.md`](agents/go-common/go-gssapi/README.md) |
| 491 | ✓ | [`agents/go-common/go-gssapi/registry.go`](agents/go-common/go-gssapi/registry.go) |
| 492 | ✓ | [`agents/go-common/go-semver/go.mod`](agents/go-common/go-semver/go.mod) |
| 493 | ✓ | [`agents/go-common/go-semver/semver.go`](agents/go-common/go-semver/semver.go) |
| 494 | ✓ | [`agents/go-common/go-semver/sort.go`](agents/go-common/go-semver/sort.go) |
| 495 | ✓ | [`agents/go-common/gohive/browser_auth_test.go`](agents/go-common/gohive/browser_auth_test.go) |
| 496 | ✓ | [`agents/go-common/gohive/browser_auth.go`](agents/go-common/gohive/browser_auth.go) |
| 497 | ✓ | [`agents/go-common/gohive/connector.go`](agents/go-common/gohive/connector.go) |
| 498 | ✓ | [`agents/go-common/gohive/driver_test.go`](agents/go-common/gohive/driver_test.go) |
| 499 | ✓ | [`agents/go-common/gohive/driver.go`](agents/go-common/gohive/driver.go) |
| 500 | ✓ | [`agents/go-common/gohive/dsn_test.go`](agents/go-common/gohive/dsn_test.go) |
| 501 | ✓ | [`agents/go-common/gohive/dsn.go`](agents/go-common/gohive/dsn.go) |
| 502 | ✓ | [`agents/go-common/gohive/go.mod`](agents/go-common/gohive/go.mod) |
| 503 | ✓ | [`agents/go-common/gohive/go.sum`](agents/go-common/gohive/go.sum) |
| 504 | ✓ | [`agents/go-common/gohive/hive_status_error_test.go`](agents/go-common/gohive/hive_status_error_test.go) |
| 505 | ✓ | [`agents/go-common/gohive/hive.go`](agents/go-common/gohive/hive.go) |
| 506 | ✓ | [`agents/go-common/gohive/http_auth_test.go`](agents/go-common/gohive/http_auth_test.go) |
| 507 | ✓ | [`agents/go-common/gohive/LICENSE`](agents/go-common/gohive/LICENSE) |
| 508 | ✓ | [`agents/go-common/gohive/metadata.go`](agents/go-common/gohive/metadata.go) |
| 509 | ✓ | [`agents/go-common/gohive/sasl_transport_test.go`](agents/go-common/gohive/sasl_transport_test.go) |
| 510 | ✓ | [`agents/go-common/gohive/sasl_transport.go`](agents/go-common/gohive/sasl_transport.go) |
| 511 | ✓ | [`agents/go-common/gosasl/go.mod`](agents/go-common/gosasl/go.mod) |
| 512 | ✓ | [`agents/go-common/gosasl/go.sum`](agents/go-common/gosasl/go.sum) |
| 513 | ✓ | [`agents/go-common/gosasl/gssapi_backend_nonwindows.go`](agents/go-common/gosasl/gssapi_backend_nonwindows.go) |
| 514 | ✓ | [`agents/go-common/gosasl/gssapi_backend_windows.go`](agents/go-common/gosasl/gssapi_backend_windows.go) |
| 515 | ✓ | [`agents/go-common/gosasl/gssapi_purego.go`](agents/go-common/gosasl/gssapi_purego.go) |
| 516 | ✓ | [`agents/go-common/gosasl/gssapi.go`](agents/go-common/gosasl/gssapi.go) |
| 517 | ✓ | [`agents/go-common/gosasl/http_spnego_test.go`](agents/go-common/gosasl/http_spnego_test.go) |
| 518 | ✓ | [`agents/go-common/gosasl/http_spnego.go`](agents/go-common/gosasl/http_spnego.go) |
| 519 | ✓ | [`agents/go-common/gosasl/LICENSE`](agents/go-common/gosasl/LICENSE) |
| 520 | ✓ | [`agents/go-common/gosasl/README.md`](agents/go-common/gosasl/README.md) |
| 521 | ✓ | [`agents/go-common/gosasl/sasl_gssapi_test.go`](agents/go-common/gosasl/sasl_gssapi_test.go) |
| 522 | ✓ | [`agents/go-common/gosasl/sasl_test.go`](agents/go-common/gosasl/sasl_test.go) |
| 523 | ✓ | [`agents/go-common/gosasl/sasl.go`](agents/go-common/gosasl/sasl.go) |
| 524 | ✓ | [`agents/go-common/iotdb-client-go/client/bitmap.go`](agents/go-common/iotdb-client-go/client/bitmap.go) |
| 525 | ✓ | [`agents/go-common/iotdb-client-go/client/column_decoder.go`](agents/go-common/iotdb-client-go/client/column_decoder.go) |
| 526 | ✓ | [`agents/go-common/iotdb-client-go/client/column.go`](agents/go-common/iotdb-client-go/client/column.go) |
| 527 | ✓ | [`agents/go-common/iotdb-client-go/client/errors.go`](agents/go-common/iotdb-client-go/client/errors.go) |
| 528 | ✓ | [`agents/go-common/iotdb-client-go/client/field.go`](agents/go-common/iotdb-client-go/client/field.go) |
| 529 | ✓ | [`agents/go-common/iotdb-client-go/client/options.go`](agents/go-common/iotdb-client-go/client/options.go) |
| 530 | ✓ | [`agents/go-common/iotdb-client-go/client/protocol.go`](agents/go-common/iotdb-client-go/client/protocol.go) |
| 531 | ✓ | [`agents/go-common/iotdb-client-go/client/rowrecord.go`](agents/go-common/iotdb-client-go/client/rowrecord.go) |
| 532 | ✓ | [`agents/go-common/iotdb-client-go/client/rpcdataset.go`](agents/go-common/iotdb-client-go/client/rpcdataset.go) |
| 533 | ✓ | [`agents/go-common/iotdb-client-go/client/session.go`](agents/go-common/iotdb-client-go/client/session.go) |
| 534 | ✓ | [`agents/go-common/iotdb-client-go/client/sessiondataset.go`](agents/go-common/iotdb-client-go/client/sessiondataset.go) |
| 535 | ✓ | [`agents/go-common/iotdb-client-go/client/sessionpool.go`](agents/go-common/iotdb-client-go/client/sessionpool.go) |
| 536 | ✓ | [`agents/go-common/iotdb-client-go/client/tablesession.go`](agents/go-common/iotdb-client-go/client/tablesession.go) |
| 537 | ✓ | [`agents/go-common/iotdb-client-go/client/tablesessionpool.go`](agents/go-common/iotdb-client-go/client/tablesessionpool.go) |
| 538 | ✓ | [`agents/go-common/iotdb-client-go/client/tablet.go`](agents/go-common/iotdb-client-go/client/tablet.go) |
| 539 | ✓ | [`agents/go-common/iotdb-client-go/client/tls.go`](agents/go-common/iotdb-client-go/client/tls.go) |
| 540 | ✓ | [`agents/go-common/iotdb-client-go/client/tsblock.go`](agents/go-common/iotdb-client-go/client/tsblock.go) |
| 541 | ✓ | [`agents/go-common/iotdb-client-go/client/utils.go`](agents/go-common/iotdb-client-go/client/utils.go) |
| 542 | ✓ | [`agents/go-common/iotdb-client-go/common/common-consts.go`](agents/go-common/iotdb-client-go/common/common-consts.go) |
| 543 | ✓ | [`agents/go-common/iotdb-client-go/common/common.go`](agents/go-common/iotdb-client-go/common/common.go) |
| 544 | ✓ | [`agents/go-common/iotdb-client-go/common/GoUnusedProtection__.go`](agents/go-common/iotdb-client-go/common/GoUnusedProtection__.go) |
| 545 | ✓ | [`agents/go-common/iotdb-client-go/go.mod`](agents/go-common/iotdb-client-go/go.mod) |
| 546 | ✓ | [`agents/go-common/iotdb-client-go/go.sum`](agents/go-common/iotdb-client-go/go.sum) |
| 547 | ✓ | [`agents/go-common/iotdb-client-go/LICENSE`](agents/go-common/iotdb-client-go/LICENSE) |
| 548 | ✓ | [`agents/go-common/iotdb-client-go/NOTICE`](agents/go-common/iotdb-client-go/NOTICE) |
| 549 | ✓ | [`agents/go-common/iotdb-client-go/rpc/client-consts.go`](agents/go-common/iotdb-client-go/rpc/client-consts.go) |
| 550 | ✓ | [`agents/go-common/iotdb-client-go/rpc/client.go`](agents/go-common/iotdb-client-go/rpc/client.go) |
| 551 | ✓ | [`agents/go-common/iotdb-client-go/rpc/GoUnusedProtection__.go`](agents/go-common/iotdb-client-go/rpc/GoUnusedProtection__.go) |
| 552 | ✓ | [`agents/gradle/wrapper/gradle-wrapper.jar`](agents/gradle/wrapper/gradle-wrapper.jar) |
| 553 | ✓ | [`agents/gradle/wrapper/gradle-wrapper.properties`](agents/gradle/wrapper/gradle-wrapper.properties) |
| 554 | ✓ | [`agents/gradlew`](agents/gradlew) |
| 555 | ✓ | [`agents/gradlew.bat`](agents/gradlew.bat) |
| 556 | ✓ | [`agents/metadata-constraint-coverage.tsv`](agents/metadata-constraint-coverage.tsv) |
| 557 | ✓ | [`agents/README.md`](agents/README.md) |
| 558 | ✓ | [`agents/README.zh-CN.md`](agents/README.zh-CN.md) |
| 559 | ✓ | [`agents/scripts/build_driver_zips.py`](agents/scripts/build_driver_zips.py) |
| 560 | ✓ | [`agents/scripts/build_offline_jdbc_payload.mjs`](agents/scripts/build_offline_jdbc_payload.mjs) |
| 561 | ✓ | [`agents/scripts/build_offline_zip.sh`](agents/scripts/build_offline_zip.sh) |
| 562 | ✓ | [`agents/scripts/driver_release_packages_test.py`](agents/scripts/driver_release_packages_test.py) |
| 563 | ✓ | [`agents/scripts/release.sh`](agents/scripts/release.sh) |
| 564 | ✓ | [`agents/scripts/validate_agent_jars.py`](agents/scripts/validate_agent_jars.py) |
| 565 | ✓ | [`agents/scripts/validate_agents_test.py`](agents/scripts/validate_agents_test.py) |
| 566 | ✓ | [`agents/scripts/validate_agents.py`](agents/scripts/validate_agents.py) |
| 567 | ✓ | [`agents/scripts/validate_windows_pe_dependencies_test.py`](agents/scripts/validate_windows_pe_dependencies_test.py) |
| 568 | ✓ | [`agents/scripts/validate_windows_pe_dependencies.py`](agents/scripts/validate_windows_pe_dependencies.py) |
| 569 | ✓ | [`agents/scripts/verify_offline_jdbc_release.mjs`](agents/scripts/verify_offline_jdbc_release.mjs) |
| 570 | ✓ | [`agents/scripts/version_agent_artifacts.py`](agents/scripts/version_agent_artifacts.py) |
| 571 | ✓ | [`agents/settings.gradle`](agents/settings.gradle) |
| 572 | ✓ | [`agents/test-support/build.gradle`](agents/test-support/build.gradle) |
| 573 | ✓ | [`agents/test-support/src/main/java/com/dbx/agent/test/JdbcAgentFake.java`](agents/test-support/src/main/java/com/dbx/agent/test/JdbcAgentFake.java) |
| 574 | ✓ | [`agents/test-support/src/main/java/com/dbx/agent/test/JdbcConnectedAgentTest.java`](agents/test-support/src/main/java/com/dbx/agent/test/JdbcConnectedAgentTest.java) |
| 575 | ✓ | [`agents/test-support/src/main/java/com/dbx/agent/test/JdbcExecutionBehaviorTest.java`](agents/test-support/src/main/java/com/dbx/agent/test/JdbcExecutionBehaviorTest.java) |
| 576 | ✓ | [`agents/test-support/src/main/java/com/dbx/agent/test/JdbcFakeExecutionBehaviorTest.java`](agents/test-support/src/main/java/com/dbx/agent/test/JdbcFakeExecutionBehaviorTest.java) |
| 577 | ✓ | [`agents/test-support/src/main/java/com/dbx/agent/test/JdbcMetadataBehaviorTest.java`](agents/test-support/src/main/java/com/dbx/agent/test/JdbcMetadataBehaviorTest.java) |
| 578 | ✓ | [`agents/test-support/src/main/java/com/dbx/agent/test/JdbcMetadataSqlFake.java`](agents/test-support/src/main/java/com/dbx/agent/test/JdbcMetadataSqlFake.java) |
| 579 | ✓ | [`agents/test-support/src/main/java/com/dbx/agent/test/TestSupport.java`](agents/test-support/src/main/java/com/dbx/agent/test/TestSupport.java) |
| 580 | ✓ | [`agents/versions.json`](agents/versions.json) |
| 581 | ✓ | [`apps/desktop/src/components/mq/README.md`](apps/desktop/src/components/mq/README.md) |
| 582 | ✓ | [`apps/desktop/src/lib/README.md`](apps/desktop/src/lib/README.md) |
| 583 | ✓ | [`apps/desktop/src/lib/sql/semantic/README.md`](apps/desktop/src/lib/sql/semantic/README.md) |
| 584 | ✓ | [`apps/README.md`](apps/README.md) |
| 585 | ✓ | [`crates/dbx-core/src/mq/README.md`](crates/dbx-core/src/mq/README.md) |
| 586 | ✓ | [`crates/README.md`](crates/README.md) |
| 587 | ✓ | [`deploy/1panel/README.md`](deploy/1panel/README.md) |
| 588 | ✓ | [`deploy/database/consul/2.0.2/init/README.md`](deploy/database/consul/2.0.2/init/README.md) |
| 589 | ✓ | [`deploy/database/elasticsearch/6.8/init/README.md`](deploy/database/elasticsearch/6.8/init/README.md) |
| 590 | ✓ | [`deploy/database/etcd/3.5/init/README.md`](deploy/database/etcd/3.5/init/README.md) |
| 591 | ✓ | [`deploy/database/etcd/3.7/init/README.md`](deploy/database/etcd/3.7/init/README.md) |
| 592 | ✓ | [`deploy/database/kafka/4.3/init/README.md`](deploy/database/kafka/4.3/init/README.md) |
| 593 | ✓ | [`deploy/database/nacos/2.5/init/README.md`](deploy/database/nacos/2.5/init/README.md) |
| 594 | ✓ | [`deploy/database/nacos/3.2/init/README.md`](deploy/database/nacos/3.2/init/README.md) |
| 595 | ✓ | [`deploy/database/pulsar/4.2/init/README.md`](deploy/database/pulsar/4.2/init/README.md) |
| 596 | ✓ | [`deploy/database/qdrant/1.8/init/README.md`](deploy/database/qdrant/1.8/init/README.md) |
| 597 | ✓ | [`deploy/database/redis/3.0.7/init/README.md`](deploy/database/redis/3.0.7/init/README.md) |
| 598 | ✓ | [`deploy/database/redis/7.4/init/README.md`](deploy/database/redis/7.4/init/README.md) |
| 599 | ✓ | [`deploy/database/rnacos/0.8/init/README.md`](deploy/database/rnacos/0.8/init/README.md) |
| 600 | ✓ | [`deploy/database/zookeeper/3.9/init/README.md`](deploy/database/zookeeper/3.9/init/README.md) |
| 601 | ✓ | [`deploy/dockerhub/README.md`](deploy/dockerhub/README.md) |
| 602 | ✓ | [`docs/public/llms.txt`](docs/public/llms.txt) |
| 603 | ✓ | [`examples/README.md`](examples/README.md) |
| 604 | ✓ | [`packages/mcp-darwin-arm64/README.md`](packages/mcp-darwin-arm64/README.md) |
| 605 | ✓ | [`packages/mcp-darwin-x64/README.md`](packages/mcp-darwin-x64/README.md) |
| 606 | ✓ | [`packages/mcp-linux-arm64-gnu/README.md`](packages/mcp-linux-arm64-gnu/README.md) |
| 607 | ✓ | [`packages/mcp-linux-x64-gnu/README.md`](packages/mcp-linux-x64-gnu/README.md) |
| 608 | ✓ | [`packages/mcp-win32-arm64/README.md`](packages/mcp-win32-arm64/README.md) |
| 609 | ✓ | [`packages/mcp-win32-x64/README.md`](packages/mcp-win32-x64/README.md) |
| 610 | ✓ | [`plugins/connection-types/README.md`](plugins/connection-types/README.md) |
| 611 | ✓ | [`plugins/jdbc/README.md`](plugins/jdbc/README.md) |
| 612 | ✓ | [`plugins/README.md`](plugins/README.md) |
| 613 | ✓ | [`skills/dbx/SKILL.md`](skills/dbx/SKILL.md) |
| 614 | ✓ | [`src-tauri/tests/fixtures/pnpm/10.27.0/README.md`](src-tauri/tests/fixtures/pnpm/10.27.0/README.md) |
| 615 | ✓ | [`vendor/ctor/README.md`](vendor/ctor/README.md) |
| 616 | ✓ | [`vendor/dirs-sys/README.md`](vendor/dirs-sys/README.md) |
| 617 | ✓ | [`vendor/rumqttc/README.md`](vendor/rumqttc/README.md) |
| 618 | ✓ | [`vendor/tiberius/README.md`](vendor/tiberius/README.md) |
| 619 | ✓ | [`vendor/wry/README.md`](vendor/wry/README.md) |
| 620 | → | [`CONTRIBUTING.md`](CONTRIBUTING.md) |
| 621 | → | [`CONTRIBUTING.zh-CN.md`](CONTRIBUTING.zh-CN.md) |
| 622 | → | [`deploy/database/README.md`](deploy/database/README.md) |
| 623 | → | [`deploy/database/README.zh-CN.md`](deploy/database/README.zh-CN.md) |
| 624 | → | [`packages/cli/README.md`](packages/cli/README.md) |
| 625 | → | [`packages/mcp-server/README.md`](packages/mcp-server/README.md) |
| 626 | → | [`README.md`](README.md) |
| 627 | → | [`README.zh-CN.md`](README.zh-CN.md) |

---

*Generated by mirror — do not edit manually*