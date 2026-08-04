---
repo: t8y2/dbx
repoUrl: https://github.com/t8y2/dbx.git
refType: branch
ref: main
---

# Mirror Manifest

Mirror of `t8y2/dbx` — 26 default patterns, 8 followed patterns, 361 file(s) materialized.

## Metadata

| Field         | Value |
|---------------|-------|
| Repo          | `t8y2/dbx` |
| Ref Type      | `branch` |
| Ref           | `main` |
| Default pats  | 26 |
| Followed pats | 8 |
| Files         | 361 |

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
| 85 | ✓ | [`agents/drivers/bigquery/build.gradle`](agents/drivers/bigquery/build.gradle) |
| 86 | ✓ | [`agents/drivers/bigquery/src/main/java/com/dbx/agent/bigquery/BigQueryAgent.java`](agents/drivers/bigquery/src/main/java/com/dbx/agent/bigquery/BigQueryAgent.java) |
| 87 | ✓ | [`agents/drivers/bigquery/src/test/java/com/dbx/agent/bigquery/BigQueryAgentMetadataTest.java`](agents/drivers/bigquery/src/test/java/com/dbx/agent/bigquery/BigQueryAgentMetadataTest.java) |
| 88 | ✓ | [`agents/drivers/bigquery/src/test/java/com/dbx/agent/bigquery/BigQueryAgentTest.java`](agents/drivers/bigquery/src/test/java/com/dbx/agent/bigquery/BigQueryAgentTest.java) |
| 89 | ✓ | [`agents/drivers/cassandra-go/astra_test.go`](agents/drivers/cassandra-go/astra_test.go) |
| 90 | ✓ | [`agents/drivers/cassandra-go/bench/agent_compare.py`](agents/drivers/cassandra-go/bench/agent_compare.py) |
| 91 | ✓ | [`agents/drivers/cassandra-go/bench/README.md`](agents/drivers/cassandra-go/bench/README.md) |
| 92 | ✓ | [`agents/drivers/cassandra-go/bench/results/cassandra-4.1.10.json`](agents/drivers/cassandra-go/bench/results/cassandra-4.1.10.json) |
| 93 | ✓ | [`agents/drivers/cassandra-go/config_file_test.go`](agents/drivers/cassandra-go/config_file_test.go) |
| 94 | ✓ | [`agents/drivers/cassandra-go/config_file.go`](agents/drivers/cassandra-go/config_file.go) |
| 95 | ✓ | [`agents/drivers/cassandra-go/config_test.go`](agents/drivers/cassandra-go/config_test.go) |
| 96 | ✓ | [`agents/drivers/cassandra-go/config.go`](agents/drivers/cassandra-go/config.go) |
| 97 | ✓ | [`agents/drivers/cassandra-go/dialer.go`](agents/drivers/cassandra-go/dialer.go) |
| 98 | ✓ | [`agents/drivers/cassandra-go/go.mod`](agents/drivers/cassandra-go/go.mod) |
| 99 | ✓ | [`agents/drivers/cassandra-go/go.sum`](agents/drivers/cassandra-go/go.sum) |
| 100 | ✓ | [`agents/drivers/cassandra-go/integration_test.go`](agents/drivers/cassandra-go/integration_test.go) |
| 101 | ✓ | [`agents/drivers/cassandra-go/kerberos_test.go`](agents/drivers/cassandra-go/kerberos_test.go) |
| 102 | ✓ | [`agents/drivers/cassandra-go/kerberos.go`](agents/drivers/cassandra-go/kerberos.go) |
| 103 | ✓ | [`agents/drivers/cassandra-go/main.go`](agents/drivers/cassandra-go/main.go) |
| 104 | ✓ | [`agents/drivers/cassandra-go/metadata_test.go`](agents/drivers/cassandra-go/metadata_test.go) |
| 105 | ✓ | [`agents/drivers/cassandra-go/metadata.go`](agents/drivers/cassandra-go/metadata.go) |
| 106 | ✓ | [`agents/drivers/cassandra-go/protocol_error.go`](agents/drivers/cassandra-go/protocol_error.go) |
| 107 | ✓ | [`agents/drivers/cassandra-go/protocol_test.go`](agents/drivers/cassandra-go/protocol_test.go) |
| 108 | ✓ | [`agents/drivers/cassandra-go/query.go`](agents/drivers/cassandra-go/query.go) |
| 109 | ✓ | [`agents/drivers/cassandra-go/README.md`](agents/drivers/cassandra-go/README.md) |
| 110 | ✓ | [`agents/drivers/cassandra-go/runtime_test.go`](agents/drivers/cassandra-go/runtime_test.go) |
| 111 | ✓ | [`agents/drivers/cassandra-go/runtime.go`](agents/drivers/cassandra-go/runtime.go) |
| 112 | ✓ | [`agents/drivers/cassandra-go/values_test.go`](agents/drivers/cassandra-go/values_test.go) |
| 113 | ✓ | [`agents/drivers/cassandra-go/values.go`](agents/drivers/cassandra-go/values.go) |
| 114 | ✓ | [`agents/drivers/dameng/build.gradle`](agents/drivers/dameng/build.gradle) |
| 115 | ✓ | [`agents/drivers/dameng/libs/.gitkeep`](agents/drivers/dameng/libs/.gitkeep) |
| 116 | ✓ | [`agents/drivers/dameng/src/main/java/com/dbx/agent/dameng/DamengAgent.java`](agents/drivers/dameng/src/main/java/com/dbx/agent/dameng/DamengAgent.java) |
| 117 | ✓ | [`agents/drivers/dameng/src/test/java/com/dbx/agent/dameng/DamengAgentMetadataTest.java`](agents/drivers/dameng/src/test/java/com/dbx/agent/dameng/DamengAgentMetadataTest.java) |
| 118 | ✓ | [`agents/drivers/dameng/src/test/java/com/dbx/agent/dameng/DamengAgentPagingTest.java`](agents/drivers/dameng/src/test/java/com/dbx/agent/dameng/DamengAgentPagingTest.java) |
| 119 | ✓ | [`agents/drivers/dameng/src/test/java/com/dbx/agent/dameng/DamengAgentTest.java`](agents/drivers/dameng/src/test/java/com/dbx/agent/dameng/DamengAgentTest.java) |
| 120 | ✓ | [`agents/drivers/dameng/src/test/java/com/dbx/agent/dameng/DamengAgentUrlTest.java`](agents/drivers/dameng/src/test/java/com/dbx/agent/dameng/DamengAgentUrlTest.java) |
| 121 | ✓ | [`agents/drivers/databend/build.gradle`](agents/drivers/databend/build.gradle) |
| 122 | ✓ | [`agents/drivers/databend/src/main/java/com/dbx/agent/databend/DatabendAgent.java`](agents/drivers/databend/src/main/java/com/dbx/agent/databend/DatabendAgent.java) |
| 123 | ✓ | [`agents/drivers/databend/src/test/java/com/dbx/agent/databend/DatabendAgentTest.java`](agents/drivers/databend/src/test/java/com/dbx/agent/databend/DatabendAgentTest.java) |
| 124 | ✓ | [`agents/drivers/databricks/build.gradle`](agents/drivers/databricks/build.gradle) |
| 125 | ✓ | [`agents/drivers/databricks/src/main/java/com/dbx/agent/databricks/DatabricksAgent.java`](agents/drivers/databricks/src/main/java/com/dbx/agent/databricks/DatabricksAgent.java) |
| 126 | ✓ | [`agents/drivers/databricks/src/test/java/com/dbx/agent/databricks/DatabricksAgentTest.java`](agents/drivers/databricks/src/test/java/com/dbx/agent/databricks/DatabricksAgentTest.java) |
| 127 | ✓ | [`agents/drivers/db2/build.gradle`](agents/drivers/db2/build.gradle) |
| 128 | ✓ | [`agents/drivers/db2/src/main/java/com/dbx/agent/db2/Db2Agent.java`](agents/drivers/db2/src/main/java/com/dbx/agent/db2/Db2Agent.java) |
| 129 | ✓ | [`agents/drivers/db2/src/test/java/com/dbx/agent/db2/Db2AgentTest.java`](agents/drivers/db2/src/test/java/com/dbx/agent/db2/Db2AgentTest.java) |
| 130 | ✓ | [`agents/drivers/duckdb/Cargo.lock`](agents/drivers/duckdb/Cargo.lock) |
| 131 | ✓ | [`agents/drivers/duckdb/Cargo.toml`](agents/drivers/duckdb/Cargo.toml) |
| 132 | ✓ | [`agents/drivers/duckdb/README.md`](agents/drivers/duckdb/README.md) |
| 133 | ✓ | [`agents/drivers/duckdb/src/connection.rs`](agents/drivers/duckdb/src/connection.rs) |
| 134 | ✓ | [`agents/drivers/duckdb/src/lib.rs`](agents/drivers/duckdb/src/lib.rs) |
| 135 | ✓ | [`agents/drivers/duckdb/src/main.rs`](agents/drivers/duckdb/src/main.rs) |
| 136 | ✓ | [`agents/drivers/duckdb/src/query.rs`](agents/drivers/duckdb/src/query.rs) |
| 137 | ✓ | [`agents/drivers/duckdb/src/runtime.rs`](agents/drivers/duckdb/src/runtime.rs) |
| 138 | ✓ | [`agents/drivers/duckdb/src/schema.rs`](agents/drivers/duckdb/src/schema.rs) |
| 139 | ✓ | [`agents/drivers/duckdb/src/sql.rs`](agents/drivers/duckdb/src/sql.rs) |
| 140 | ✓ | [`agents/drivers/duckdb/src/wire.rs`](agents/drivers/duckdb/src/wire.rs) |
| 141 | ✓ | [`agents/drivers/duckdb/tests/duckdb_worker_process.rs`](agents/drivers/duckdb/tests/duckdb_worker_process.rs) |
| 142 | ✓ | [`agents/drivers/duckdb/tests/support/duckdb_worker_file_lock_owner.rs`](agents/drivers/duckdb/tests/support/duckdb_worker_file_lock_owner.rs) |
| 143 | ✓ | [`agents/drivers/duckdb/tests/support/duckdb_worker_hanging_connect_test_host.rs`](agents/drivers/duckdb/tests/support/duckdb_worker_hanging_connect_test_host.rs) |
| 144 | ✓ | [`agents/drivers/duckdb/tests/support/duckdb_worker_pid_test_host.rs`](agents/drivers/duckdb/tests/support/duckdb_worker_pid_test_host.rs) |
| 145 | ✓ | [`agents/drivers/etcd/build.gradle`](agents/drivers/etcd/build.gradle) |
| 146 | ✓ | [`agents/drivers/etcd/src/main/java/com/dbx/agent/etcd/EtcdAgent.java`](agents/drivers/etcd/src/main/java/com/dbx/agent/etcd/EtcdAgent.java) |
| 147 | ✓ | [`agents/drivers/etcd/src/test/java/com/dbx/agent/etcd/EtcdAgentTest.java`](agents/drivers/etcd/src/test/java/com/dbx/agent/etcd/EtcdAgentTest.java) |
| 148 | ✓ | [`agents/drivers/exasol/build.gradle`](agents/drivers/exasol/build.gradle) |
| 149 | ✓ | [`agents/drivers/exasol/src/main/java/com/dbx/agent/exasol/ExasolAgent.java`](agents/drivers/exasol/src/main/java/com/dbx/agent/exasol/ExasolAgent.java) |
| 150 | ✓ | [`agents/drivers/firebird/build.gradle`](agents/drivers/firebird/build.gradle) |
| 151 | ✓ | [`agents/drivers/firebird/src/main/java/com/dbx/agent/firebird/FirebirdAgent.java`](agents/drivers/firebird/src/main/java/com/dbx/agent/firebird/FirebirdAgent.java) |
| 152 | ✓ | [`agents/drivers/gbase8a/build.gradle`](agents/drivers/gbase8a/build.gradle) |
| 153 | ✓ | [`agents/drivers/gbase8a/libs/gbase-connector-java-9.5.0.10-build1-bin.jar`](agents/drivers/gbase8a/libs/gbase-connector-java-9.5.0.10-build1-bin.jar) |
| 154 | ✓ | [`agents/drivers/gbase8a/src/main/java/com/dbx/agent/gbase8a/Gbase8aAgent.java`](agents/drivers/gbase8a/src/main/java/com/dbx/agent/gbase8a/Gbase8aAgent.java) |
| 155 | ✓ | [`agents/drivers/gbase8a/src/test/java/com/dbx/agent/gbase8a/Gbase8aAgentTest.java`](agents/drivers/gbase8a/src/test/java/com/dbx/agent/gbase8a/Gbase8aAgentTest.java) |
| 156 | ✓ | [`agents/drivers/gbase8s/build.gradle`](agents/drivers/gbase8s/build.gradle) |
| 157 | ✓ | [`agents/drivers/gbase8s/libs/gbasedbt-jdbc.jar`](agents/drivers/gbase8s/libs/gbasedbt-jdbc.jar) |
| 158 | ✓ | [`agents/drivers/gbase8s/src/main/java/com/dbx/agent/gbase8s/Gbase8sAgent.java`](agents/drivers/gbase8s/src/main/java/com/dbx/agent/gbase8s/Gbase8sAgent.java) |
| 159 | ✓ | [`agents/drivers/gbase8s/src/test/java/com/dbx/agent/gbase8s/Gbase8sAgentTest.java`](agents/drivers/gbase8s/src/test/java/com/dbx/agent/gbase8s/Gbase8sAgentTest.java) |
| 160 | ✓ | [`agents/drivers/goldendb/build.gradle`](agents/drivers/goldendb/build.gradle) |
| 161 | ✓ | [`agents/drivers/goldendb/libs/.gitkeep`](agents/drivers/goldendb/libs/.gitkeep) |
| 162 | ✓ | [`agents/drivers/goldendb/src/main/java/com/dbx/agent/goldendb/GoldendbAgent.java`](agents/drivers/goldendb/src/main/java/com/dbx/agent/goldendb/GoldendbAgent.java) |
| 163 | ✓ | [`agents/drivers/goldendb/src/test/java/com/dbx/agent/goldendb/GoldendbAgentMetadataTest.java`](agents/drivers/goldendb/src/test/java/com/dbx/agent/goldendb/GoldendbAgentMetadataTest.java) |
| 164 | ✓ | [`agents/drivers/goldendb/src/test/java/com/dbx/agent/goldendb/GoldendbAgentTest.java`](agents/drivers/goldendb/src/test/java/com/dbx/agent/goldendb/GoldendbAgentTest.java) |
| 165 | ✓ | [`agents/drivers/h2-legacy/build.gradle`](agents/drivers/h2-legacy/build.gradle) |
| 166 | ✓ | [`agents/drivers/h2-legacy/src/main/java/com/dbx/agent/h2legacy/H2LegacyAgent.java`](agents/drivers/h2-legacy/src/main/java/com/dbx/agent/h2legacy/H2LegacyAgent.java) |
| 167 | ✓ | [`agents/drivers/h2/build.gradle`](agents/drivers/h2/build.gradle) |
| 168 | ✓ | [`agents/drivers/h2/src/main/java/com/dbx/agent/h2/H2Agent.java`](agents/drivers/h2/src/main/java/com/dbx/agent/h2/H2Agent.java) |
| 169 | ✓ | [`agents/drivers/h2/src/test/java/com/dbx/agent/h2/H2AgentTest.java`](agents/drivers/h2/src/test/java/com/dbx/agent/h2/H2AgentTest.java) |
| 170 | ✓ | [`agents/drivers/highgo/build.gradle`](agents/drivers/highgo/build.gradle) |
| 171 | ✓ | [`agents/drivers/highgo/src/main/java/com/dbx/agent/highgo/HighgoAgent.java`](agents/drivers/highgo/src/main/java/com/dbx/agent/highgo/HighgoAgent.java) |
| 172 | ✓ | [`agents/drivers/highgo/src/test/java/com/dbx/agent/highgo/HighgoAgentTest.java`](agents/drivers/highgo/src/test/java/com/dbx/agent/highgo/HighgoAgentTest.java) |
| 173 | ✓ | [`agents/drivers/hive/build.gradle`](agents/drivers/hive/build.gradle) |
| 174 | ✓ | [`agents/drivers/hive/src/main/java/com/dbx/agent/hive/HiveAgent.java`](agents/drivers/hive/src/main/java/com/dbx/agent/hive/HiveAgent.java) |
| 175 | ✓ | [`agents/drivers/hive/src/test/java/com/dbx/agent/hive/HiveAgentExecutionTest.java`](agents/drivers/hive/src/test/java/com/dbx/agent/hive/HiveAgentExecutionTest.java) |
| 176 | ✓ | [`agents/drivers/hive/src/test/java/com/dbx/agent/hive/HiveAgentMetadataTest.java`](agents/drivers/hive/src/test/java/com/dbx/agent/hive/HiveAgentMetadataTest.java) |
| 177 | ✓ | [`agents/drivers/hive/src/test/java/com/dbx/agent/hive/HiveAgentTest.java`](agents/drivers/hive/src/test/java/com/dbx/agent/hive/HiveAgentTest.java) |
| 178 | ✓ | [`agents/drivers/informix/build.gradle`](agents/drivers/informix/build.gradle) |
| 179 | ✓ | [`agents/drivers/informix/src/main/java/com/dbx/agent/informix/InformixAgent.java`](agents/drivers/informix/src/main/java/com/dbx/agent/informix/InformixAgent.java) |
| 180 | ✓ | [`agents/drivers/informix/src/test/java/com/dbx/agent/informix/InformixAgentExecutionTest.java`](agents/drivers/informix/src/test/java/com/dbx/agent/informix/InformixAgentExecutionTest.java) |
| 181 | ✓ | [`agents/drivers/informix/src/test/java/com/dbx/agent/informix/InformixAgentTest.java`](agents/drivers/informix/src/test/java/com/dbx/agent/informix/InformixAgentTest.java) |
| 182 | ✓ | [`agents/drivers/iotdb/build.gradle`](agents/drivers/iotdb/build.gradle) |
| 183 | ✓ | [`agents/drivers/iotdb/src/main/java/com/dbx/agent/iotdb/IoTDBAgent.java`](agents/drivers/iotdb/src/main/java/com/dbx/agent/iotdb/IoTDBAgent.java) |
| 184 | ✓ | [`agents/drivers/iotdb/src/test/java/com/dbx/agent/iotdb/IoTDBAgentTest.java`](agents/drivers/iotdb/src/test/java/com/dbx/agent/iotdb/IoTDBAgentTest.java) |
| 185 | ✓ | [`agents/drivers/iris/build.gradle`](agents/drivers/iris/build.gradle) |
| 186 | ✓ | [`agents/drivers/iris/src/main/java/com/dbx/agent/iris/IrisAgent.java`](agents/drivers/iris/src/main/java/com/dbx/agent/iris/IrisAgent.java) |
| 187 | ✓ | [`agents/drivers/iris/src/test/java/com/dbx/agent/iris/IrisAgentTest.java`](agents/drivers/iris/src/test/java/com/dbx/agent/iris/IrisAgentTest.java) |
| 188 | ✓ | [`agents/drivers/kafka/build.gradle`](agents/drivers/kafka/build.gradle) |
| 189 | ✓ | [`agents/drivers/kafka/src/main/java/com/dbx/agent/kafka/KafkaAgent.java`](agents/drivers/kafka/src/main/java/com/dbx/agent/kafka/KafkaAgent.java) |
| 190 | ✓ | [`agents/drivers/kafka/src/test/java/com/dbx/agent/kafka/KafkaAgentTest.java`](agents/drivers/kafka/src/test/java/com/dbx/agent/kafka/KafkaAgentTest.java) |
| 191 | ✓ | [`agents/drivers/kingbase-go/bench/agent_compare.go`](agents/drivers/kingbase-go/bench/agent_compare.go) |
| 192 | ✓ | [`agents/drivers/kingbase-go/go.mod`](agents/drivers/kingbase-go/go.mod) |
| 193 | ✓ | [`agents/drivers/kingbase-go/go.sum`](agents/drivers/kingbase-go/go.sum) |
| 194 | ✓ | [`agents/drivers/kingbase-go/integration_test.go`](agents/drivers/kingbase-go/integration_test.go) |
| 195 | ✓ | [`agents/drivers/kingbase-go/kingbase_metadata.go`](agents/drivers/kingbase-go/kingbase_metadata.go) |
| 196 | ✓ | [`agents/drivers/kingbase-go/main_test.go`](agents/drivers/kingbase-go/main_test.go) |
| 197 | ✓ | [`agents/drivers/kingbase-go/main.go`](agents/drivers/kingbase-go/main.go) |
| 198 | ✓ | [`agents/drivers/kylin/build.gradle`](agents/drivers/kylin/build.gradle) |
| 199 | ✓ | [`agents/drivers/kylin/src/main/java/com/dbx/agent/kylin/KylinAgent.java`](agents/drivers/kylin/src/main/java/com/dbx/agent/kylin/KylinAgent.java) |
| 200 | ✓ | [`agents/drivers/kylin/src/test/java/com/dbx/agent/kylin/KylinAgentTest.java`](agents/drivers/kylin/src/test/java/com/dbx/agent/kylin/KylinAgentTest.java) |
| 201 | ✓ | [`agents/drivers/mongodb/build.gradle`](agents/drivers/mongodb/build.gradle) |
| 202 | ✓ | [`agents/drivers/mongodb/src/main/java/com/dbx/agent/mongodb/MongoAgent.java`](agents/drivers/mongodb/src/main/java/com/dbx/agent/mongodb/MongoAgent.java) |
| 203 | ✓ | [`agents/drivers/mongodb/src/test/java/com/dbx/agent/mongodb/MongoAgentTest.java`](agents/drivers/mongodb/src/test/java/com/dbx/agent/mongodb/MongoAgentTest.java) |
| 204 | ✓ | [`agents/drivers/neo4j/build.gradle`](agents/drivers/neo4j/build.gradle) |
| 205 | ✓ | [`agents/drivers/neo4j/src/main/java/com/dbx/agent/neo4j/Neo4jAgent.java`](agents/drivers/neo4j/src/main/java/com/dbx/agent/neo4j/Neo4jAgent.java) |
| 206 | ✓ | [`agents/drivers/neo4j/src/test/java/com/dbx/agent/neo4j/Neo4jAgentTest.java`](agents/drivers/neo4j/src/test/java/com/dbx/agent/neo4j/Neo4jAgentTest.java) |
| 207 | ✓ | [`agents/drivers/oceanbase-oracle/build.gradle`](agents/drivers/oceanbase-oracle/build.gradle) |
| 208 | ✓ | [`agents/drivers/oceanbase-oracle/src/main/java/com/dbx/agent/oceanbaseoracle/OceanBaseOracleAgent.java`](agents/drivers/oceanbase-oracle/src/main/java/com/dbx/agent/oceanbaseoracle/OceanBaseOracleAgent.java) |
| 209 | ✓ | [`agents/drivers/oceanbase-oracle/src/test/java/com/dbx/agent/oceanbaseoracle/OceanBaseOracleAgentTest.java`](agents/drivers/oceanbase-oracle/src/test/java/com/dbx/agent/oceanbaseoracle/OceanBaseOracleAgentTest.java) |
| 210 | ✓ | [`agents/drivers/oracle-go/.gitignore`](agents/drivers/oracle-go/.gitignore) |
| 211 | ✓ | [`agents/drivers/oracle-go/go.mod`](agents/drivers/oracle-go/go.mod) |
| 212 | ✓ | [`agents/drivers/oracle-go/go.sum`](agents/drivers/oracle-go/go.sum) |
| 213 | ✓ | [`agents/drivers/oracle-go/main_test.go`](agents/drivers/oracle-go/main_test.go) |
| 214 | ✓ | [`agents/drivers/oracle-go/main.go`](agents/drivers/oracle-go/main.go) |
| 215 | ✓ | [`agents/drivers/oracle-go/README.md`](agents/drivers/oracle-go/README.md) |
| 216 | ✓ | [`agents/drivers/oracle-go/tns_test.go`](agents/drivers/oracle-go/tns_test.go) |
| 217 | ✓ | [`agents/drivers/oracle-go/tns.go`](agents/drivers/oracle-go/tns.go) |
| 218 | ✓ | [`agents/drivers/oscar/build.gradle`](agents/drivers/oscar/build.gradle) |
| 219 | ✓ | [`agents/drivers/oscar/libs/oscarJDBC8.jar`](agents/drivers/oscar/libs/oscarJDBC8.jar) |
| 220 | ✓ | [`agents/drivers/oscar/src/main/java/com/dbx/agent/oscar/OscarAgent.java`](agents/drivers/oscar/src/main/java/com/dbx/agent/oscar/OscarAgent.java) |
| 221 | ✓ | [`agents/drivers/oscar/src/test/java/com/dbx/agent/oscar/OscarAgentTest.java`](agents/drivers/oscar/src/test/java/com/dbx/agent/oscar/OscarAgentTest.java) |
| 222 | ✓ | [`agents/drivers/rabbitmq/bench/agent_compare.go`](agents/drivers/rabbitmq/bench/agent_compare.go) |
| 223 | ✓ | [`agents/drivers/rabbitmq/go.mod`](agents/drivers/rabbitmq/go.mod) |
| 224 | ✓ | [`agents/drivers/rabbitmq/go.sum`](agents/drivers/rabbitmq/go.sum) |
| 225 | ✓ | [`agents/drivers/rabbitmq/helpers_test.go`](agents/drivers/rabbitmq/helpers_test.go) |
| 226 | ✓ | [`agents/drivers/rabbitmq/helpers.go`](agents/drivers/rabbitmq/helpers.go) |
| 227 | ✓ | [`agents/drivers/rabbitmq/integration_test.go`](agents/drivers/rabbitmq/integration_test.go) |
| 228 | ✓ | [`agents/drivers/rabbitmq/main.go`](agents/drivers/rabbitmq/main.go) |
| 229 | ✓ | [`agents/drivers/rabbitmq/management_test.go`](agents/drivers/rabbitmq/management_test.go) |
| 230 | ✓ | [`agents/drivers/rabbitmq/management.go`](agents/drivers/rabbitmq/management.go) |
| 231 | ✓ | [`agents/drivers/rabbitmq/mapping_test.go`](agents/drivers/rabbitmq/mapping_test.go) |
| 232 | ✓ | [`agents/drivers/rabbitmq/operations.go`](agents/drivers/rabbitmq/operations.go) |
| 233 | ✓ | [`agents/drivers/rocketmq/build.gradle`](agents/drivers/rocketmq/build.gradle) |
| 234 | ✓ | [`agents/drivers/rocketmq/src/main/java/com/dbx/agent/rocketmq/RocketMqAgent.java`](agents/drivers/rocketmq/src/main/java/com/dbx/agent/rocketmq/RocketMqAgent.java) |
| 235 | ✓ | [`agents/drivers/rocketmq/src/test/java/com/dbx/agent/rocketmq/RocketMqAgentTest.java`](agents/drivers/rocketmq/src/test/java/com/dbx/agent/rocketmq/RocketMqAgentTest.java) |
| 236 | ✓ | [`agents/drivers/rocketmq/src/test/java/com/dbx/agent/rocketmq/RocketMqLiveMessagePropertyTest.java`](agents/drivers/rocketmq/src/test/java/com/dbx/agent/rocketmq/RocketMqLiveMessagePropertyTest.java) |
| 237 | ✓ | [`agents/drivers/rocketmq/src/test/java/com/dbx/agent/rocketmq/RocketMqLiveTopicTypeTest.java`](agents/drivers/rocketmq/src/test/java/com/dbx/agent/rocketmq/RocketMqLiveTopicTypeTest.java) |
| 238 | ✓ | [`agents/drivers/saphana/build.gradle`](agents/drivers/saphana/build.gradle) |
| 239 | ✓ | [`agents/drivers/saphana/src/main/java/com/dbx/agent/saphana/SapHanaAgent.java`](agents/drivers/saphana/src/main/java/com/dbx/agent/saphana/SapHanaAgent.java) |
| 240 | ✓ | [`agents/drivers/snowflake/build.gradle`](agents/drivers/snowflake/build.gradle) |
| 241 | ✓ | [`agents/drivers/snowflake/src/main/java/com/dbx/agent/snowflake/SnowflakeAgent.java`](agents/drivers/snowflake/src/main/java/com/dbx/agent/snowflake/SnowflakeAgent.java) |
| 242 | ✓ | [`agents/drivers/snowflake/src/test/java/com/dbx/agent/snowflake/SnowflakeAgentMetadataTest.java`](agents/drivers/snowflake/src/test/java/com/dbx/agent/snowflake/SnowflakeAgentMetadataTest.java) |
| 243 | ✓ | [`agents/drivers/snowflake/src/test/java/com/dbx/agent/snowflake/SnowflakeAgentTest.java`](agents/drivers/snowflake/src/test/java/com/dbx/agent/snowflake/SnowflakeAgentTest.java) |
| 244 | ✓ | [`agents/drivers/spark/build.gradle`](agents/drivers/spark/build.gradle) |
| 245 | ✓ | [`agents/drivers/spark/src/main/java/com/dbx/agent/spark/SparkAgent.java`](agents/drivers/spark/src/main/java/com/dbx/agent/spark/SparkAgent.java) |
| 246 | ✓ | [`agents/drivers/sqlserver-legacy/build.gradle`](agents/drivers/sqlserver-legacy/build.gradle) |
| 247 | ✓ | [`agents/drivers/sqlserver-legacy/src/main/java/com/dbx/agent/sqlserverlegacy/SqlServerLegacyAgent.java`](agents/drivers/sqlserver-legacy/src/main/java/com/dbx/agent/sqlserverlegacy/SqlServerLegacyAgent.java) |
| 248 | ✓ | [`agents/drivers/sqlserver-legacy/src/test/java/com/dbx/agent/sqlserverlegacy/SqlServerLegacyAgentTest.java`](agents/drivers/sqlserver-legacy/src/test/java/com/dbx/agent/sqlserverlegacy/SqlServerLegacyAgentTest.java) |
| 249 | ✓ | [`agents/drivers/sundb/build.gradle`](agents/drivers/sundb/build.gradle) |
| 250 | ✓ | [`agents/drivers/sundb/src/main/java/com/dbx/agent/sundb/SundbAgent.java`](agents/drivers/sundb/src/main/java/com/dbx/agent/sundb/SundbAgent.java) |
| 251 | ✓ | [`agents/drivers/sundb/src/test/java/com/dbx/agent/sundb/SundbAgentMetadataTest.java`](agents/drivers/sundb/src/test/java/com/dbx/agent/sundb/SundbAgentMetadataTest.java) |
| 252 | ✓ | [`agents/drivers/sundb/src/test/java/com/dbx/agent/sundb/SundbAgentTest.java`](agents/drivers/sundb/src/test/java/com/dbx/agent/sundb/SundbAgentTest.java) |
| 253 | ✓ | [`agents/drivers/tdengine/build.gradle`](agents/drivers/tdengine/build.gradle) |
| 254 | ✓ | [`agents/drivers/tdengine/src/main/java/com/dbx/agent/tdengine/TDengineAgent.java`](agents/drivers/tdengine/src/main/java/com/dbx/agent/tdengine/TDengineAgent.java) |
| 255 | ✓ | [`agents/drivers/tdengine/src/test/java/com/dbx/agent/tdengine/TDengineAgentPagingTest.java`](agents/drivers/tdengine/src/test/java/com/dbx/agent/tdengine/TDengineAgentPagingTest.java) |
| 256 | ✓ | [`agents/drivers/tdengine/src/test/java/com/dbx/agent/tdengine/TDengineAgentTest.java`](agents/drivers/tdengine/src/test/java/com/dbx/agent/tdengine/TDengineAgentTest.java) |
| 257 | ✓ | [`agents/drivers/teradata/build.gradle`](agents/drivers/teradata/build.gradle) |
| 258 | ✓ | [`agents/drivers/teradata/src/main/java/com/dbx/agent/teradata/TeradataAgent.java`](agents/drivers/teradata/src/main/java/com/dbx/agent/teradata/TeradataAgent.java) |
| 259 | ✓ | [`agents/drivers/trino/build.gradle`](agents/drivers/trino/build.gradle) |
| 260 | ✓ | [`agents/drivers/trino/src/main/java/com/dbx/agent/trino/TrinoAgent.java`](agents/drivers/trino/src/main/java/com/dbx/agent/trino/TrinoAgent.java) |
| 261 | ✓ | [`agents/drivers/trino/src/test/java/com/dbx/agent/trino/TrinoAgentTest.java`](agents/drivers/trino/src/test/java/com/dbx/agent/trino/TrinoAgentTest.java) |
| 262 | ✓ | [`agents/drivers/uxdb/build.gradle`](agents/drivers/uxdb/build.gradle) |
| 263 | ✓ | [`agents/drivers/uxdb/libs/uxdbjdbc-2.1.2.3p.jre8.jar`](agents/drivers/uxdb/libs/uxdbjdbc-2.1.2.3p.jre8.jar) |
| 264 | ✓ | [`agents/drivers/uxdb/src/main/java/com/dbx/agent/uxdb/UxdbAgent.java`](agents/drivers/uxdb/src/main/java/com/dbx/agent/uxdb/UxdbAgent.java) |
| 265 | ✓ | [`agents/drivers/uxdb/src/test/java/com/dbx/agent/uxdb/UxdbAgentTest.java`](agents/drivers/uxdb/src/test/java/com/dbx/agent/uxdb/UxdbAgentTest.java) |
| 266 | ✓ | [`agents/drivers/vastbase-go/bench/agent_compare.go`](agents/drivers/vastbase-go/bench/agent_compare.go) |
| 267 | ✓ | [`agents/drivers/vastbase-go/bench/direct/main.go`](agents/drivers/vastbase-go/bench/direct/main.go) |
| 268 | ✓ | [`agents/drivers/vastbase-go/bench/README.md`](agents/drivers/vastbase-go/bench/README.md) |
| 269 | ✓ | [`agents/drivers/vastbase-go/connection_info_test.go`](agents/drivers/vastbase-go/connection_info_test.go) |
| 270 | ✓ | [`agents/drivers/vastbase-go/connection_state_test.go`](agents/drivers/vastbase-go/connection_state_test.go) |
| 271 | ✓ | [`agents/drivers/vastbase-go/connection_state.go`](agents/drivers/vastbase-go/connection_state.go) |
| 272 | ✓ | [`agents/drivers/vastbase-go/driver.go`](agents/drivers/vastbase-go/driver.go) |
| 273 | ✓ | [`agents/drivers/vastbase-go/go.mod`](agents/drivers/vastbase-go/go.mod) |
| 274 | ✓ | [`agents/drivers/vastbase-go/go.sum`](agents/drivers/vastbase-go/go.sum) |
| 275 | ✓ | [`agents/drivers/vastbase-go/integration_test.go`](agents/drivers/vastbase-go/integration_test.go) |
| 276 | ✓ | [`agents/drivers/vastbase-go/main_test.go`](agents/drivers/vastbase-go/main_test.go) |
| 277 | ✓ | [`agents/drivers/vastbase-go/main.go`](agents/drivers/vastbase-go/main.go) |
| 278 | ✓ | [`agents/drivers/vastbase-go/protocol_error_test.go`](agents/drivers/vastbase-go/protocol_error_test.go) |
| 279 | ✓ | [`agents/drivers/vastbase-go/protocol_error.go`](agents/drivers/vastbase-go/protocol_error.go) |
| 280 | ✓ | [`agents/drivers/vastbase-go/README.md`](agents/drivers/vastbase-go/README.md) |
| 281 | ✓ | [`agents/drivers/vastbase-go/runtime_pool_test.go`](agents/drivers/vastbase-go/runtime_pool_test.go) |
| 282 | ✓ | [`agents/drivers/vastbase-go/runtime_pool.go`](agents/drivers/vastbase-go/runtime_pool.go) |
| 283 | ✓ | [`agents/drivers/vastbase-go/spatial_test.go`](agents/drivers/vastbase-go/spatial_test.go) |
| 284 | ✓ | [`agents/drivers/vastbase-go/spatial.go`](agents/drivers/vastbase-go/spatial.go) |
| 285 | ✓ | [`agents/drivers/vastbase-go/vastbase_metadata.go`](agents/drivers/vastbase-go/vastbase_metadata.go) |
| 286 | ✓ | [`agents/drivers/vertica/build.gradle`](agents/drivers/vertica/build.gradle) |
| 287 | ✓ | [`agents/drivers/vertica/src/main/java/com/dbx/agent/vertica/VerticaAgent.java`](agents/drivers/vertica/src/main/java/com/dbx/agent/vertica/VerticaAgent.java) |
| 288 | ✓ | [`agents/drivers/xugu/go.mod`](agents/drivers/xugu/go.mod) |
| 289 | ✓ | [`agents/drivers/xugu/go.sum`](agents/drivers/xugu/go.sum) |
| 290 | ✓ | [`agents/drivers/xugu/main_test.go`](agents/drivers/xugu/main_test.go) |
| 291 | ✓ | [`agents/drivers/xugu/main.go`](agents/drivers/xugu/main.go) |
| 292 | ✓ | [`agents/drivers/xugu/README.md`](agents/drivers/xugu/README.md) |
| 293 | ✓ | [`agents/drivers/yashandb/build.gradle`](agents/drivers/yashandb/build.gradle) |
| 294 | ✓ | [`agents/drivers/yashandb/src/main/java/com/dbx/agent/yashandb/YashandbAgent.java`](agents/drivers/yashandb/src/main/java/com/dbx/agent/yashandb/YashandbAgent.java) |
| 295 | ✓ | [`agents/drivers/yashandb/src/test/java/com/dbx/agent/yashandb/YashandbAgentTest.java`](agents/drivers/yashandb/src/test/java/com/dbx/agent/yashandb/YashandbAgentTest.java) |
| 296 | ✓ | [`agents/drivers/zookeeper/build.gradle`](agents/drivers/zookeeper/build.gradle) |
| 297 | ✓ | [`agents/drivers/zookeeper/src/main/java/com/dbx/agent/zookeeper/ZooKeeperAgent.java`](agents/drivers/zookeeper/src/main/java/com/dbx/agent/zookeeper/ZooKeeperAgent.java) |
| 298 | ✓ | [`agents/drivers/zookeeper/src/test/java/com/dbx/agent/zookeeper/ZooKeeperAgentTest.java`](agents/drivers/zookeeper/src/test/java/com/dbx/agent/zookeeper/ZooKeeperAgentTest.java) |
| 299 | ✓ | [`agents/gradle/wrapper/gradle-wrapper.jar`](agents/gradle/wrapper/gradle-wrapper.jar) |
| 300 | ✓ | [`agents/gradle/wrapper/gradle-wrapper.properties`](agents/gradle/wrapper/gradle-wrapper.properties) |
| 301 | ✓ | [`agents/gradlew`](agents/gradlew) |
| 302 | ✓ | [`agents/gradlew.bat`](agents/gradlew.bat) |
| 303 | ✓ | [`agents/metadata-constraint-coverage.tsv`](agents/metadata-constraint-coverage.tsv) |
| 304 | ✓ | [`agents/README.md`](agents/README.md) |
| 305 | ✓ | [`agents/README.zh-CN.md`](agents/README.zh-CN.md) |
| 306 | ✓ | [`agents/scripts/build_driver_zips.py`](agents/scripts/build_driver_zips.py) |
| 307 | ✓ | [`agents/scripts/build_offline_zip.sh`](agents/scripts/build_offline_zip.sh) |
| 308 | ✓ | [`agents/scripts/driver_release_packages_test.py`](agents/scripts/driver_release_packages_test.py) |
| 309 | ✓ | [`agents/scripts/release.sh`](agents/scripts/release.sh) |
| 310 | ✓ | [`agents/scripts/validate_agent_jars.py`](agents/scripts/validate_agent_jars.py) |
| 311 | ✓ | [`agents/scripts/validate_agents_test.py`](agents/scripts/validate_agents_test.py) |
| 312 | ✓ | [`agents/scripts/validate_agents.py`](agents/scripts/validate_agents.py) |
| 313 | ✓ | [`agents/scripts/version_agent_artifacts.py`](agents/scripts/version_agent_artifacts.py) |
| 314 | ✓ | [`agents/settings.gradle`](agents/settings.gradle) |
| 315 | ✓ | [`agents/test-support/build.gradle`](agents/test-support/build.gradle) |
| 316 | ✓ | [`agents/test-support/src/main/java/com/dbx/agent/test/JdbcAgentFake.java`](agents/test-support/src/main/java/com/dbx/agent/test/JdbcAgentFake.java) |
| 317 | ✓ | [`agents/test-support/src/main/java/com/dbx/agent/test/JdbcConnectedAgentTest.java`](agents/test-support/src/main/java/com/dbx/agent/test/JdbcConnectedAgentTest.java) |
| 318 | ✓ | [`agents/test-support/src/main/java/com/dbx/agent/test/JdbcExecutionBehaviorTest.java`](agents/test-support/src/main/java/com/dbx/agent/test/JdbcExecutionBehaviorTest.java) |
| 319 | ✓ | [`agents/test-support/src/main/java/com/dbx/agent/test/JdbcFakeExecutionBehaviorTest.java`](agents/test-support/src/main/java/com/dbx/agent/test/JdbcFakeExecutionBehaviorTest.java) |
| 320 | ✓ | [`agents/test-support/src/main/java/com/dbx/agent/test/JdbcMetadataBehaviorTest.java`](agents/test-support/src/main/java/com/dbx/agent/test/JdbcMetadataBehaviorTest.java) |
| 321 | ✓ | [`agents/test-support/src/main/java/com/dbx/agent/test/JdbcMetadataSqlFake.java`](agents/test-support/src/main/java/com/dbx/agent/test/JdbcMetadataSqlFake.java) |
| 322 | ✓ | [`agents/test-support/src/main/java/com/dbx/agent/test/TestSupport.java`](agents/test-support/src/main/java/com/dbx/agent/test/TestSupport.java) |
| 323 | ✓ | [`agents/versions.json`](agents/versions.json) |
| 324 | ✓ | [`apps/desktop/src/components/mq/README.md`](apps/desktop/src/components/mq/README.md) |
| 325 | ✓ | [`apps/desktop/src/lib/README.md`](apps/desktop/src/lib/README.md) |
| 326 | ✓ | [`apps/desktop/src/lib/sql/semantic/README.md`](apps/desktop/src/lib/sql/semantic/README.md) |
| 327 | ✓ | [`apps/README.md`](apps/README.md) |
| 328 | ✓ | [`crates/dbx-core/src/mq/README.md`](crates/dbx-core/src/mq/README.md) |
| 329 | ✓ | [`crates/README.md`](crates/README.md) |
| 330 | ✓ | [`deploy/1panel/README.md`](deploy/1panel/README.md) |
| 331 | ✓ | [`deploy/database/etcd/3.7/init/README.md`](deploy/database/etcd/3.7/init/README.md) |
| 332 | ✓ | [`deploy/database/kafka/4.3/init/README.md`](deploy/database/kafka/4.3/init/README.md) |
| 333 | ✓ | [`deploy/database/nacos/2.5/init/README.md`](deploy/database/nacos/2.5/init/README.md) |
| 334 | ✓ | [`deploy/database/nacos/3.2/init/README.md`](deploy/database/nacos/3.2/init/README.md) |
| 335 | ✓ | [`deploy/database/pulsar/4.2/init/README.md`](deploy/database/pulsar/4.2/init/README.md) |
| 336 | ✓ | [`deploy/database/qdrant/1.8/init/README.md`](deploy/database/qdrant/1.8/init/README.md) |
| 337 | ✓ | [`deploy/database/redis/3.0.7/init/README.md`](deploy/database/redis/3.0.7/init/README.md) |
| 338 | ✓ | [`deploy/database/redis/7.4/init/README.md`](deploy/database/redis/7.4/init/README.md) |
| 339 | ✓ | [`deploy/database/rnacos/0.8/init/README.md`](deploy/database/rnacos/0.8/init/README.md) |
| 340 | ✓ | [`deploy/database/zookeeper/3.9/init/README.md`](deploy/database/zookeeper/3.9/init/README.md) |
| 341 | ✓ | [`deploy/dockerhub/README.md`](deploy/dockerhub/README.md) |
| 342 | ✓ | [`docs/public/llms.txt`](docs/public/llms.txt) |
| 343 | ✓ | [`examples/README.md`](examples/README.md) |
| 344 | ✓ | [`packages/mcp-darwin-arm64/README.md`](packages/mcp-darwin-arm64/README.md) |
| 345 | ✓ | [`packages/mcp-darwin-x64/README.md`](packages/mcp-darwin-x64/README.md) |
| 346 | ✓ | [`packages/mcp-linux-arm64-gnu/README.md`](packages/mcp-linux-arm64-gnu/README.md) |
| 347 | ✓ | [`packages/mcp-linux-x64-gnu/README.md`](packages/mcp-linux-x64-gnu/README.md) |
| 348 | ✓ | [`packages/mcp-win32-arm64/README.md`](packages/mcp-win32-arm64/README.md) |
| 349 | ✓ | [`packages/mcp-win32-x64/README.md`](packages/mcp-win32-x64/README.md) |
| 350 | ✓ | [`plugins/jdbc/README.md`](plugins/jdbc/README.md) |
| 351 | ✓ | [`plugins/README.md`](plugins/README.md) |
| 352 | ✓ | [`skills/dbx/SKILL.md`](skills/dbx/SKILL.md) |
| 353 | ✓ | [`vendor/ctor/README.md`](vendor/ctor/README.md) |
| 354 | → | [`CONTRIBUTING.md`](CONTRIBUTING.md) |
| 355 | → | [`CONTRIBUTING.zh-CN.md`](CONTRIBUTING.zh-CN.md) |
| 356 | → | [`deploy/database/README.md`](deploy/database/README.md) |
| 357 | → | [`deploy/database/README.zh-CN.md`](deploy/database/README.zh-CN.md) |
| 358 | → | [`packages/cli/README.md`](packages/cli/README.md) |
| 359 | → | [`packages/mcp-server/README.md`](packages/mcp-server/README.md) |
| 360 | → | [`README.md`](README.md) |
| 361 | → | [`README.zh-CN.md`](README.zh-CN.md) |

---

*Generated by mirror — do not edit manually*