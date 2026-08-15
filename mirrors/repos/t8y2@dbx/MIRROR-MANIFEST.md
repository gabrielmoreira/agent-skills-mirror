---
repo: t8y2/dbx
repoUrl: https://github.com/t8y2/dbx.git
refType: branch
ref: main
---

# Mirror Manifest

Mirror of `t8y2/dbx` — 26 default patterns, 8 followed patterns, 511 file(s) materialized.

## Metadata

| Field         | Value |
|---------------|-------|
| Repo          | `t8y2/dbx` |
| Ref Type      | `branch` |
| Ref           | `main` |
| Default pats  | 26 |
| Followed pats | 8 |
| Files         | 511 |

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
| 130 | ✓ | [`agents/drivers/duckdb/.cargo/config.toml`](agents/drivers/duckdb/.cargo/config.toml) |
| 131 | ✓ | [`agents/drivers/duckdb/Cargo.lock`](agents/drivers/duckdb/Cargo.lock) |
| 132 | ✓ | [`agents/drivers/duckdb/Cargo.toml`](agents/drivers/duckdb/Cargo.toml) |
| 133 | ✓ | [`agents/drivers/duckdb/README.md`](agents/drivers/duckdb/README.md) |
| 134 | ✓ | [`agents/drivers/duckdb/src/connection.rs`](agents/drivers/duckdb/src/connection.rs) |
| 135 | ✓ | [`agents/drivers/duckdb/src/lib.rs`](agents/drivers/duckdb/src/lib.rs) |
| 136 | ✓ | [`agents/drivers/duckdb/src/main.rs`](agents/drivers/duckdb/src/main.rs) |
| 137 | ✓ | [`agents/drivers/duckdb/src/query.rs`](agents/drivers/duckdb/src/query.rs) |
| 138 | ✓ | [`agents/drivers/duckdb/src/runtime.rs`](agents/drivers/duckdb/src/runtime.rs) |
| 139 | ✓ | [`agents/drivers/duckdb/src/schema.rs`](agents/drivers/duckdb/src/schema.rs) |
| 140 | ✓ | [`agents/drivers/duckdb/src/sql.rs`](agents/drivers/duckdb/src/sql.rs) |
| 141 | ✓ | [`agents/drivers/duckdb/src/wire.rs`](agents/drivers/duckdb/src/wire.rs) |
| 142 | ✓ | [`agents/drivers/duckdb/tests/duckdb_worker_process.rs`](agents/drivers/duckdb/tests/duckdb_worker_process.rs) |
| 143 | ✓ | [`agents/drivers/duckdb/tests/support/duckdb_worker_file_lock_owner.rs`](agents/drivers/duckdb/tests/support/duckdb_worker_file_lock_owner.rs) |
| 144 | ✓ | [`agents/drivers/duckdb/tests/support/duckdb_worker_hanging_connect_test_host.rs`](agents/drivers/duckdb/tests/support/duckdb_worker_hanging_connect_test_host.rs) |
| 145 | ✓ | [`agents/drivers/duckdb/tests/support/duckdb_worker_pid_test_host.rs`](agents/drivers/duckdb/tests/support/duckdb_worker_pid_test_host.rs) |
| 146 | ✓ | [`agents/drivers/etcd/build.gradle`](agents/drivers/etcd/build.gradle) |
| 147 | ✓ | [`agents/drivers/etcd/src/main/java/com/dbx/agent/etcd/EtcdAgent.java`](agents/drivers/etcd/src/main/java/com/dbx/agent/etcd/EtcdAgent.java) |
| 148 | ✓ | [`agents/drivers/etcd/src/test/java/com/dbx/agent/etcd/EtcdAgentTest.java`](agents/drivers/etcd/src/test/java/com/dbx/agent/etcd/EtcdAgentTest.java) |
| 149 | ✓ | [`agents/drivers/exasol/build.gradle`](agents/drivers/exasol/build.gradle) |
| 150 | ✓ | [`agents/drivers/exasol/src/main/java/com/dbx/agent/exasol/ExasolAgent.java`](agents/drivers/exasol/src/main/java/com/dbx/agent/exasol/ExasolAgent.java) |
| 151 | ✓ | [`agents/drivers/firebird/build.gradle`](agents/drivers/firebird/build.gradle) |
| 152 | ✓ | [`agents/drivers/firebird/src/main/java/com/dbx/agent/firebird/FirebirdAgent.java`](agents/drivers/firebird/src/main/java/com/dbx/agent/firebird/FirebirdAgent.java) |
| 153 | ✓ | [`agents/drivers/firebird/src/test/java/com/dbx/agent/firebird/FirebirdAgentTest.java`](agents/drivers/firebird/src/test/java/com/dbx/agent/firebird/FirebirdAgentTest.java) |
| 154 | ✓ | [`agents/drivers/gbase8a/build.gradle`](agents/drivers/gbase8a/build.gradle) |
| 155 | ✓ | [`agents/drivers/gbase8a/libs/gbase-connector-java-9.5.0.10-build1-bin.jar`](agents/drivers/gbase8a/libs/gbase-connector-java-9.5.0.10-build1-bin.jar) |
| 156 | ✓ | [`agents/drivers/gbase8a/src/main/java/com/dbx/agent/gbase8a/Gbase8aAgent.java`](agents/drivers/gbase8a/src/main/java/com/dbx/agent/gbase8a/Gbase8aAgent.java) |
| 157 | ✓ | [`agents/drivers/gbase8a/src/test/java/com/dbx/agent/gbase8a/Gbase8aAgentTest.java`](agents/drivers/gbase8a/src/test/java/com/dbx/agent/gbase8a/Gbase8aAgentTest.java) |
| 158 | ✓ | [`agents/drivers/gbase8s/build.gradle`](agents/drivers/gbase8s/build.gradle) |
| 159 | ✓ | [`agents/drivers/gbase8s/libs/gbasedbt-jdbc.jar`](agents/drivers/gbase8s/libs/gbasedbt-jdbc.jar) |
| 160 | ✓ | [`agents/drivers/gbase8s/src/main/java/com/dbx/agent/gbase8s/Gbase8sAgent.java`](agents/drivers/gbase8s/src/main/java/com/dbx/agent/gbase8s/Gbase8sAgent.java) |
| 161 | ✓ | [`agents/drivers/gbase8s/src/test/java/com/dbx/agent/gbase8s/Gbase8sAgentTest.java`](agents/drivers/gbase8s/src/test/java/com/dbx/agent/gbase8s/Gbase8sAgentTest.java) |
| 162 | ✓ | [`agents/drivers/goldendb/build.gradle`](agents/drivers/goldendb/build.gradle) |
| 163 | ✓ | [`agents/drivers/goldendb/libs/.gitkeep`](agents/drivers/goldendb/libs/.gitkeep) |
| 164 | ✓ | [`agents/drivers/goldendb/src/main/java/com/dbx/agent/goldendb/GoldendbAgent.java`](agents/drivers/goldendb/src/main/java/com/dbx/agent/goldendb/GoldendbAgent.java) |
| 165 | ✓ | [`agents/drivers/goldendb/src/test/java/com/dbx/agent/goldendb/GoldendbAgentMetadataTest.java`](agents/drivers/goldendb/src/test/java/com/dbx/agent/goldendb/GoldendbAgentMetadataTest.java) |
| 166 | ✓ | [`agents/drivers/goldendb/src/test/java/com/dbx/agent/goldendb/GoldendbAgentTest.java`](agents/drivers/goldendb/src/test/java/com/dbx/agent/goldendb/GoldendbAgentTest.java) |
| 167 | ✓ | [`agents/drivers/h2-legacy/build.gradle`](agents/drivers/h2-legacy/build.gradle) |
| 168 | ✓ | [`agents/drivers/h2-legacy/src/main/java/com/dbx/agent/h2legacy/H2LegacyAgent.java`](agents/drivers/h2-legacy/src/main/java/com/dbx/agent/h2legacy/H2LegacyAgent.java) |
| 169 | ✓ | [`agents/drivers/h2/build.gradle`](agents/drivers/h2/build.gradle) |
| 170 | ✓ | [`agents/drivers/h2/src/main/java/com/dbx/agent/h2/H2Agent.java`](agents/drivers/h2/src/main/java/com/dbx/agent/h2/H2Agent.java) |
| 171 | ✓ | [`agents/drivers/h2/src/test/java/com/dbx/agent/h2/H2AgentTest.java`](agents/drivers/h2/src/test/java/com/dbx/agent/h2/H2AgentTest.java) |
| 172 | ✓ | [`agents/drivers/highgo/build.gradle`](agents/drivers/highgo/build.gradle) |
| 173 | ✓ | [`agents/drivers/highgo/src/main/java/com/dbx/agent/highgo/HighgoAgent.java`](agents/drivers/highgo/src/main/java/com/dbx/agent/highgo/HighgoAgent.java) |
| 174 | ✓ | [`agents/drivers/highgo/src/test/java/com/dbx/agent/highgo/HighgoAgentTest.java`](agents/drivers/highgo/src/test/java/com/dbx/agent/highgo/HighgoAgentTest.java) |
| 175 | ✓ | [`agents/drivers/hive-go/bench/agent_compare.py`](agents/drivers/hive-go/bench/agent_compare.py) |
| 176 | ✓ | [`agents/drivers/hive-go/bench/functional_probe.py`](agents/drivers/hive-go/bench/functional_probe.py) |
| 177 | ✓ | [`agents/drivers/hive-go/bench/kdc_fixture/main.go`](agents/drivers/hive-go/bench/kdc_fixture/main.go) |
| 178 | ✓ | [`agents/drivers/hive-go/bench/README.md`](agents/drivers/hive-go/bench/README.md) |
| 179 | ✓ | [`agents/drivers/hive-go/config_test.go`](agents/drivers/hive-go/config_test.go) |
| 180 | ✓ | [`agents/drivers/hive-go/config.go`](agents/drivers/hive-go/config.go) |
| 181 | ✓ | [`agents/drivers/hive-go/connector_test.go`](agents/drivers/hive-go/connector_test.go) |
| 182 | ✓ | [`agents/drivers/hive-go/connector.go`](agents/drivers/hive-go/connector.go) |
| 183 | ✓ | [`agents/drivers/hive-go/discovery_test.go`](agents/drivers/hive-go/discovery_test.go) |
| 184 | ✓ | [`agents/drivers/hive-go/discovery.go`](agents/drivers/hive-go/discovery.go) |
| 185 | ✓ | [`agents/drivers/hive-go/go.mod`](agents/drivers/hive-go/go.mod) |
| 186 | ✓ | [`agents/drivers/hive-go/go.sum`](agents/drivers/hive-go/go.sum) |
| 187 | ✓ | [`agents/drivers/hive-go/init_test.go`](agents/drivers/hive-go/init_test.go) |
| 188 | ✓ | [`agents/drivers/hive-go/kerberos_defaults_unix.go`](agents/drivers/hive-go/kerberos_defaults_unix.go) |
| 189 | ✓ | [`agents/drivers/hive-go/kerberos_defaults_windows.go`](agents/drivers/hive-go/kerberos_defaults_windows.go) |
| 190 | ✓ | [`agents/drivers/hive-go/main.go`](agents/drivers/hive-go/main.go) |
| 191 | ✓ | [`agents/drivers/hive-go/metadata_test.go`](agents/drivers/hive-go/metadata_test.go) |
| 192 | ✓ | [`agents/drivers/hive-go/metadata.go`](agents/drivers/hive-go/metadata.go) |
| 193 | ✓ | [`agents/drivers/hive-go/MIGRATION_PARITY.md`](agents/drivers/hive-go/MIGRATION_PARITY.md) |
| 194 | ✓ | [`agents/drivers/hive-go/protocol_error.go`](agents/drivers/hive-go/protocol_error.go) |
| 195 | ✓ | [`agents/drivers/hive-go/query_test.go`](agents/drivers/hive-go/query_test.go) |
| 196 | ✓ | [`agents/drivers/hive-go/query.go`](agents/drivers/hive-go/query.go) |
| 197 | ✓ | [`agents/drivers/hive-go/zookeeper_protocol_test.go`](agents/drivers/hive-go/zookeeper_protocol_test.go) |
| 198 | ✓ | [`agents/drivers/hive-go/zookeeper_protocol.go`](agents/drivers/hive-go/zookeeper_protocol.go) |
| 199 | ✓ | [`agents/drivers/hive-go/zookeeper_tls_test.go`](agents/drivers/hive-go/zookeeper_tls_test.go) |
| 200 | ✓ | [`agents/drivers/hive-go/zookeeper_tls.go`](agents/drivers/hive-go/zookeeper_tls.go) |
| 201 | ✓ | [`agents/drivers/informix/build.gradle`](agents/drivers/informix/build.gradle) |
| 202 | ✓ | [`agents/drivers/informix/src/main/java/com/dbx/agent/informix/InformixAgent.java`](agents/drivers/informix/src/main/java/com/dbx/agent/informix/InformixAgent.java) |
| 203 | ✓ | [`agents/drivers/informix/src/test/java/com/dbx/agent/informix/InformixAgentExecutionTest.java`](agents/drivers/informix/src/test/java/com/dbx/agent/informix/InformixAgentExecutionTest.java) |
| 204 | ✓ | [`agents/drivers/informix/src/test/java/com/dbx/agent/informix/InformixAgentTest.java`](agents/drivers/informix/src/test/java/com/dbx/agent/informix/InformixAgentTest.java) |
| 205 | ✓ | [`agents/drivers/iotdb/bench/build.gradle`](agents/drivers/iotdb/bench/build.gradle) |
| 206 | ✓ | [`agents/drivers/iotdb/bench/go/go.mod`](agents/drivers/iotdb/bench/go/go.mod) |
| 207 | ✓ | [`agents/drivers/iotdb/bench/go/go.sum`](agents/drivers/iotdb/bench/go/go.sum) |
| 208 | ✓ | [`agents/drivers/iotdb/bench/go/main.go`](agents/drivers/iotdb/bench/go/main.go) |
| 209 | ✓ | [`agents/drivers/iotdb/bench/java/com/dbx/agent/iotdb/bench/JdbcDriverBenchmark.java`](agents/drivers/iotdb/bench/java/com/dbx/agent/iotdb/bench/JdbcDriverBenchmark.java) |
| 210 | ✓ | [`agents/drivers/iotdb/bench/README.md`](agents/drivers/iotdb/bench/README.md) |
| 211 | ✓ | [`agents/drivers/iotdb/bench/results/iotdb-2.0.8-macos-arm64.json`](agents/drivers/iotdb/bench/results/iotdb-2.0.8-macos-arm64.json) |
| 212 | ✓ | [`agents/drivers/iotdb/bench/results/README.md`](agents/drivers/iotdb/bench/results/README.md) |
| 213 | ✓ | [`agents/drivers/iotdb/bench/run.py`](agents/drivers/iotdb/bench/run.py) |
| 214 | ✓ | [`agents/drivers/iotdb/bench/settings.gradle`](agents/drivers/iotdb/bench/settings.gradle) |
| 215 | ✓ | [`agents/drivers/iotdb/driver.go`](agents/drivers/iotdb/driver.go) |
| 216 | ✓ | [`agents/drivers/iotdb/go.mod`](agents/drivers/iotdb/go.mod) |
| 217 | ✓ | [`agents/drivers/iotdb/go.sum`](agents/drivers/iotdb/go.sum) |
| 218 | ✓ | [`agents/drivers/iotdb/integration_test.go`](agents/drivers/iotdb/integration_test.go) |
| 219 | ✓ | [`agents/drivers/iotdb/main_test.go`](agents/drivers/iotdb/main_test.go) |
| 220 | ✓ | [`agents/drivers/iotdb/main.go`](agents/drivers/iotdb/main.go) |
| 221 | ✓ | [`agents/drivers/iotdb/metadata.go`](agents/drivers/iotdb/metadata.go) |
| 222 | ✓ | [`agents/drivers/iotdb/protocol_error.go`](agents/drivers/iotdb/protocol_error.go) |
| 223 | ✓ | [`agents/drivers/iotdb/query.go`](agents/drivers/iotdb/query.go) |
| 224 | ✓ | [`agents/drivers/iotdb/README.md`](agents/drivers/iotdb/README.md) |
| 225 | ✓ | [`agents/drivers/iris/build.gradle`](agents/drivers/iris/build.gradle) |
| 226 | ✓ | [`agents/drivers/iris/src/main/java/com/dbx/agent/iris/IrisAgent.java`](agents/drivers/iris/src/main/java/com/dbx/agent/iris/IrisAgent.java) |
| 227 | ✓ | [`agents/drivers/iris/src/test/java/com/dbx/agent/iris/IrisAgentTest.java`](agents/drivers/iris/src/test/java/com/dbx/agent/iris/IrisAgentTest.java) |
| 228 | ✓ | [`agents/drivers/kafka/build.gradle`](agents/drivers/kafka/build.gradle) |
| 229 | ✓ | [`agents/drivers/kafka/src/main/java/com/dbx/agent/kafka/KafkaAgent.java`](agents/drivers/kafka/src/main/java/com/dbx/agent/kafka/KafkaAgent.java) |
| 230 | ✓ | [`agents/drivers/kafka/src/test/java/com/dbx/agent/kafka/KafkaAgentTest.java`](agents/drivers/kafka/src/test/java/com/dbx/agent/kafka/KafkaAgentTest.java) |
| 231 | ✓ | [`agents/drivers/kingbase-go/bench/agent_compare.go`](agents/drivers/kingbase-go/bench/agent_compare.go) |
| 232 | ✓ | [`agents/drivers/kingbase-go/go.mod`](agents/drivers/kingbase-go/go.mod) |
| 233 | ✓ | [`agents/drivers/kingbase-go/go.sum`](agents/drivers/kingbase-go/go.sum) |
| 234 | ✓ | [`agents/drivers/kingbase-go/integration_test.go`](agents/drivers/kingbase-go/integration_test.go) |
| 235 | ✓ | [`agents/drivers/kingbase-go/kingbase_metadata.go`](agents/drivers/kingbase-go/kingbase_metadata.go) |
| 236 | ✓ | [`agents/drivers/kingbase-go/main_test.go`](agents/drivers/kingbase-go/main_test.go) |
| 237 | ✓ | [`agents/drivers/kingbase-go/main.go`](agents/drivers/kingbase-go/main.go) |
| 238 | ✓ | [`agents/drivers/kylin/build.gradle`](agents/drivers/kylin/build.gradle) |
| 239 | ✓ | [`agents/drivers/kylin/src/main/java/com/dbx/agent/kylin/KylinAgent.java`](agents/drivers/kylin/src/main/java/com/dbx/agent/kylin/KylinAgent.java) |
| 240 | ✓ | [`agents/drivers/kylin/src/test/java/com/dbx/agent/kylin/KylinAgentTest.java`](agents/drivers/kylin/src/test/java/com/dbx/agent/kylin/KylinAgentTest.java) |
| 241 | ✓ | [`agents/drivers/mongodb/build.gradle`](agents/drivers/mongodb/build.gradle) |
| 242 | ✓ | [`agents/drivers/mongodb/src/main/java/com/dbx/agent/mongodb/MongoAgent.java`](agents/drivers/mongodb/src/main/java/com/dbx/agent/mongodb/MongoAgent.java) |
| 243 | ✓ | [`agents/drivers/mongodb/src/test/java/com/dbx/agent/mongodb/MongoAgentTest.java`](agents/drivers/mongodb/src/test/java/com/dbx/agent/mongodb/MongoAgentTest.java) |
| 244 | ✓ | [`agents/drivers/neo4j-go/driver.go`](agents/drivers/neo4j-go/driver.go) |
| 245 | ✓ | [`agents/drivers/neo4j-go/go.mod`](agents/drivers/neo4j-go/go.mod) |
| 246 | ✓ | [`agents/drivers/neo4j-go/go.sum`](agents/drivers/neo4j-go/go.sum) |
| 247 | ✓ | [`agents/drivers/neo4j-go/integration_test.go`](agents/drivers/neo4j-go/integration_test.go) |
| 248 | ✓ | [`agents/drivers/neo4j-go/main_test.go`](agents/drivers/neo4j-go/main_test.go) |
| 249 | ✓ | [`agents/drivers/neo4j-go/main.go`](agents/drivers/neo4j-go/main.go) |
| 250 | ✓ | [`agents/drivers/neo4j-go/metadata.go`](agents/drivers/neo4j-go/metadata.go) |
| 251 | ✓ | [`agents/drivers/neo4j-go/protocol_error.go`](agents/drivers/neo4j-go/protocol_error.go) |
| 252 | ✓ | [`agents/drivers/neo4j-go/query.go`](agents/drivers/neo4j-go/query.go) |
| 253 | ✓ | [`agents/drivers/neo4j-go/README.md`](agents/drivers/neo4j-go/README.md) |
| 254 | ✓ | [`agents/drivers/oceanbase-oracle/build.gradle`](agents/drivers/oceanbase-oracle/build.gradle) |
| 255 | ✓ | [`agents/drivers/oceanbase-oracle/src/main/java/com/dbx/agent/oceanbaseoracle/OceanBaseOracleAgent.java`](agents/drivers/oceanbase-oracle/src/main/java/com/dbx/agent/oceanbaseoracle/OceanBaseOracleAgent.java) |
| 256 | ✓ | [`agents/drivers/oceanbase-oracle/src/test/java/com/dbx/agent/oceanbaseoracle/OceanBaseOracleAgentTest.java`](agents/drivers/oceanbase-oracle/src/test/java/com/dbx/agent/oceanbaseoracle/OceanBaseOracleAgentTest.java) |
| 257 | ✓ | [`agents/drivers/oracle-go/.gitignore`](agents/drivers/oracle-go/.gitignore) |
| 258 | ✓ | [`agents/drivers/oracle-go/go.mod`](agents/drivers/oracle-go/go.mod) |
| 259 | ✓ | [`agents/drivers/oracle-go/go.sum`](agents/drivers/oracle-go/go.sum) |
| 260 | ✓ | [`agents/drivers/oracle-go/main_test.go`](agents/drivers/oracle-go/main_test.go) |
| 261 | ✓ | [`agents/drivers/oracle-go/main.go`](agents/drivers/oracle-go/main.go) |
| 262 | ✓ | [`agents/drivers/oracle-go/README.md`](agents/drivers/oracle-go/README.md) |
| 263 | ✓ | [`agents/drivers/oracle-go/tns_test.go`](agents/drivers/oracle-go/tns_test.go) |
| 264 | ✓ | [`agents/drivers/oracle-go/tns.go`](agents/drivers/oracle-go/tns.go) |
| 265 | ✓ | [`agents/drivers/oscar/build.gradle`](agents/drivers/oscar/build.gradle) |
| 266 | ✓ | [`agents/drivers/oscar/libs/oscarJDBC8.jar`](agents/drivers/oscar/libs/oscarJDBC8.jar) |
| 267 | ✓ | [`agents/drivers/oscar/src/main/java/com/dbx/agent/oscar/OscarAgent.java`](agents/drivers/oscar/src/main/java/com/dbx/agent/oscar/OscarAgent.java) |
| 268 | ✓ | [`agents/drivers/oscar/src/test/java/com/dbx/agent/oscar/OscarAgentTest.java`](agents/drivers/oscar/src/test/java/com/dbx/agent/oscar/OscarAgentTest.java) |
| 269 | ✓ | [`agents/drivers/rabbitmq/bench/agent_compare.go`](agents/drivers/rabbitmq/bench/agent_compare.go) |
| 270 | ✓ | [`agents/drivers/rabbitmq/go.mod`](agents/drivers/rabbitmq/go.mod) |
| 271 | ✓ | [`agents/drivers/rabbitmq/go.sum`](agents/drivers/rabbitmq/go.sum) |
| 272 | ✓ | [`agents/drivers/rabbitmq/helpers_test.go`](agents/drivers/rabbitmq/helpers_test.go) |
| 273 | ✓ | [`agents/drivers/rabbitmq/helpers.go`](agents/drivers/rabbitmq/helpers.go) |
| 274 | ✓ | [`agents/drivers/rabbitmq/integration_test.go`](agents/drivers/rabbitmq/integration_test.go) |
| 275 | ✓ | [`agents/drivers/rabbitmq/main.go`](agents/drivers/rabbitmq/main.go) |
| 276 | ✓ | [`agents/drivers/rabbitmq/management_test.go`](agents/drivers/rabbitmq/management_test.go) |
| 277 | ✓ | [`agents/drivers/rabbitmq/management.go`](agents/drivers/rabbitmq/management.go) |
| 278 | ✓ | [`agents/drivers/rabbitmq/mapping_test.go`](agents/drivers/rabbitmq/mapping_test.go) |
| 279 | ✓ | [`agents/drivers/rabbitmq/operations.go`](agents/drivers/rabbitmq/operations.go) |
| 280 | ✓ | [`agents/drivers/rocketmq/acl.go`](agents/drivers/rocketmq/acl.go) |
| 281 | ✓ | [`agents/drivers/rocketmq/cluster.go`](agents/drivers/rocketmq/cluster.go) |
| 282 | ✓ | [`agents/drivers/rocketmq/connection_test.go`](agents/drivers/rocketmq/connection_test.go) |
| 283 | ✓ | [`agents/drivers/rocketmq/connection.go`](agents/drivers/rocketmq/connection.go) |
| 284 | ✓ | [`agents/drivers/rocketmq/consumers_test.go`](agents/drivers/rocketmq/consumers_test.go) |
| 285 | ✓ | [`agents/drivers/rocketmq/consumers.go`](agents/drivers/rocketmq/consumers.go) |
| 286 | ✓ | [`agents/drivers/rocketmq/go.mod`](agents/drivers/rocketmq/go.mod) |
| 287 | ✓ | [`agents/drivers/rocketmq/go.sum`](agents/drivers/rocketmq/go.sum) |
| 288 | ✓ | [`agents/drivers/rocketmq/helpers.go`](agents/drivers/rocketmq/helpers.go) |
| 289 | ✓ | [`agents/drivers/rocketmq/integration_test.go`](agents/drivers/rocketmq/integration_test.go) |
| 290 | ✓ | [`agents/drivers/rocketmq/main_test.go`](agents/drivers/rocketmq/main_test.go) |
| 291 | ✓ | [`agents/drivers/rocketmq/main.go`](agents/drivers/rocketmq/main.go) |
| 292 | ✓ | [`agents/drivers/rocketmq/messages_test.go`](agents/drivers/rocketmq/messages_test.go) |
| 293 | ✓ | [`agents/drivers/rocketmq/messages.go`](agents/drivers/rocketmq/messages.go) |
| 294 | ✓ | [`agents/drivers/rocketmq/remoting.go`](agents/drivers/rocketmq/remoting.go) |
| 295 | ✓ | [`agents/drivers/rocketmq/routing_test.go`](agents/drivers/rocketmq/routing_test.go) |
| 296 | ✓ | [`agents/drivers/rocketmq/routing.go`](agents/drivers/rocketmq/routing.go) |
| 297 | ✓ | [`agents/drivers/rocketmq/scripts/run-integration.sh`](agents/drivers/rocketmq/scripts/run-integration.sh) |
| 298 | ✓ | [`agents/drivers/rocketmq/server_test.go`](agents/drivers/rocketmq/server_test.go) |
| 299 | ✓ | [`agents/drivers/rocketmq/server.go`](agents/drivers/rocketmq/server.go) |
| 300 | ✓ | [`agents/drivers/rocketmq/topics_test.go`](agents/drivers/rocketmq/topics_test.go) |
| 301 | ✓ | [`agents/drivers/rocketmq/topics.go`](agents/drivers/rocketmq/topics.go) |
| 302 | ✓ | [`agents/drivers/saphana/build.gradle`](agents/drivers/saphana/build.gradle) |
| 303 | ✓ | [`agents/drivers/saphana/src/main/java/com/dbx/agent/saphana/SapHanaAgent.java`](agents/drivers/saphana/src/main/java/com/dbx/agent/saphana/SapHanaAgent.java) |
| 304 | ✓ | [`agents/drivers/snowflake/build.gradle`](agents/drivers/snowflake/build.gradle) |
| 305 | ✓ | [`agents/drivers/snowflake/src/main/java/com/dbx/agent/snowflake/SnowflakeAgent.java`](agents/drivers/snowflake/src/main/java/com/dbx/agent/snowflake/SnowflakeAgent.java) |
| 306 | ✓ | [`agents/drivers/snowflake/src/test/java/com/dbx/agent/snowflake/SnowflakeAgentMetadataTest.java`](agents/drivers/snowflake/src/test/java/com/dbx/agent/snowflake/SnowflakeAgentMetadataTest.java) |
| 307 | ✓ | [`agents/drivers/snowflake/src/test/java/com/dbx/agent/snowflake/SnowflakeAgentTest.java`](agents/drivers/snowflake/src/test/java/com/dbx/agent/snowflake/SnowflakeAgentTest.java) |
| 308 | ✓ | [`agents/drivers/spark/build.gradle`](agents/drivers/spark/build.gradle) |
| 309 | ✓ | [`agents/drivers/spark/src/main/java/com/dbx/agent/spark/SparkAgent.java`](agents/drivers/spark/src/main/java/com/dbx/agent/spark/SparkAgent.java) |
| 310 | ✓ | [`agents/drivers/spark/src/test/java/com/dbx/agent/spark/SparkAgentTest.java`](agents/drivers/spark/src/test/java/com/dbx/agent/spark/SparkAgentTest.java) |
| 311 | ✓ | [`agents/drivers/sqlserver-legacy/build.gradle`](agents/drivers/sqlserver-legacy/build.gradle) |
| 312 | ✓ | [`agents/drivers/sqlserver-legacy/src/main/java/com/dbx/agent/sqlserverlegacy/SqlServerLegacyAgent.java`](agents/drivers/sqlserver-legacy/src/main/java/com/dbx/agent/sqlserverlegacy/SqlServerLegacyAgent.java) |
| 313 | ✓ | [`agents/drivers/sqlserver-legacy/src/test/java/com/dbx/agent/sqlserverlegacy/SqlServerLegacyAgentTest.java`](agents/drivers/sqlserver-legacy/src/test/java/com/dbx/agent/sqlserverlegacy/SqlServerLegacyAgentTest.java) |
| 314 | ✓ | [`agents/drivers/sundb/build.gradle`](agents/drivers/sundb/build.gradle) |
| 315 | ✓ | [`agents/drivers/sundb/src/main/java/com/dbx/agent/sundb/SundbAgent.java`](agents/drivers/sundb/src/main/java/com/dbx/agent/sundb/SundbAgent.java) |
| 316 | ✓ | [`agents/drivers/sundb/src/test/java/com/dbx/agent/sundb/SundbAgentMetadataTest.java`](agents/drivers/sundb/src/test/java/com/dbx/agent/sundb/SundbAgentMetadataTest.java) |
| 317 | ✓ | [`agents/drivers/sundb/src/test/java/com/dbx/agent/sundb/SundbAgentTest.java`](agents/drivers/sundb/src/test/java/com/dbx/agent/sundb/SundbAgentTest.java) |
| 318 | ✓ | [`agents/drivers/tdengine/.gitignore`](agents/drivers/tdengine/.gitignore) |
| 319 | ✓ | [`agents/drivers/tdengine/Cargo.lock`](agents/drivers/tdengine/Cargo.lock) |
| 320 | ✓ | [`agents/drivers/tdengine/Cargo.toml`](agents/drivers/tdengine/Cargo.toml) |
| 321 | ✓ | [`agents/drivers/tdengine/src/config.rs`](agents/drivers/tdengine/src/config.rs) |
| 322 | ✓ | [`agents/drivers/tdengine/src/driver.rs`](agents/drivers/tdengine/src/driver.rs) |
| 323 | ✓ | [`agents/drivers/tdengine/src/lib.rs`](agents/drivers/tdengine/src/lib.rs) |
| 324 | ✓ | [`agents/drivers/tdengine/src/main.rs`](agents/drivers/tdengine/src/main.rs) |
| 325 | ✓ | [`agents/drivers/tdengine/src/model.rs`](agents/drivers/tdengine/src/model.rs) |
| 326 | ✓ | [`agents/drivers/tdengine/src/runtime.rs`](agents/drivers/tdengine/src/runtime.rs) |
| 327 | ✓ | [`agents/drivers/tdengine/src/value.rs`](agents/drivers/tdengine/src/value.rs) |
| 328 | ✓ | [`agents/drivers/tdengine/tests/live.rs`](agents/drivers/tdengine/tests/live.rs) |
| 329 | ✓ | [`agents/drivers/tdengine/tests/protocol.rs`](agents/drivers/tdengine/tests/protocol.rs) |
| 330 | ✓ | [`agents/drivers/teradata/build.gradle`](agents/drivers/teradata/build.gradle) |
| 331 | ✓ | [`agents/drivers/teradata/src/main/java/com/dbx/agent/teradata/TeradataAgent.java`](agents/drivers/teradata/src/main/java/com/dbx/agent/teradata/TeradataAgent.java) |
| 332 | ✓ | [`agents/drivers/trino/build.gradle`](agents/drivers/trino/build.gradle) |
| 333 | ✓ | [`agents/drivers/trino/src/main/java/com/dbx/agent/trino/TrinoAgent.java`](agents/drivers/trino/src/main/java/com/dbx/agent/trino/TrinoAgent.java) |
| 334 | ✓ | [`agents/drivers/trino/src/test/java/com/dbx/agent/trino/TrinoAgentTest.java`](agents/drivers/trino/src/test/java/com/dbx/agent/trino/TrinoAgentTest.java) |
| 335 | ✓ | [`agents/drivers/uxdb/build.gradle`](agents/drivers/uxdb/build.gradle) |
| 336 | ✓ | [`agents/drivers/uxdb/libs/uxdbjdbc-2.1.2.3p.jre8.jar`](agents/drivers/uxdb/libs/uxdbjdbc-2.1.2.3p.jre8.jar) |
| 337 | ✓ | [`agents/drivers/uxdb/src/main/java/com/dbx/agent/uxdb/UxdbAgent.java`](agents/drivers/uxdb/src/main/java/com/dbx/agent/uxdb/UxdbAgent.java) |
| 338 | ✓ | [`agents/drivers/uxdb/src/test/java/com/dbx/agent/uxdb/UxdbAgentTest.java`](agents/drivers/uxdb/src/test/java/com/dbx/agent/uxdb/UxdbAgentTest.java) |
| 339 | ✓ | [`agents/drivers/vastbase-go/bench/agent_compare.go`](agents/drivers/vastbase-go/bench/agent_compare.go) |
| 340 | ✓ | [`agents/drivers/vastbase-go/bench/direct/main.go`](agents/drivers/vastbase-go/bench/direct/main.go) |
| 341 | ✓ | [`agents/drivers/vastbase-go/bench/README.md`](agents/drivers/vastbase-go/bench/README.md) |
| 342 | ✓ | [`agents/drivers/vastbase-go/connection_info_test.go`](agents/drivers/vastbase-go/connection_info_test.go) |
| 343 | ✓ | [`agents/drivers/vastbase-go/connection_state_test.go`](agents/drivers/vastbase-go/connection_state_test.go) |
| 344 | ✓ | [`agents/drivers/vastbase-go/connection_state.go`](agents/drivers/vastbase-go/connection_state.go) |
| 345 | ✓ | [`agents/drivers/vastbase-go/driver.go`](agents/drivers/vastbase-go/driver.go) |
| 346 | ✓ | [`agents/drivers/vastbase-go/go.mod`](agents/drivers/vastbase-go/go.mod) |
| 347 | ✓ | [`agents/drivers/vastbase-go/go.sum`](agents/drivers/vastbase-go/go.sum) |
| 348 | ✓ | [`agents/drivers/vastbase-go/integration_test.go`](agents/drivers/vastbase-go/integration_test.go) |
| 349 | ✓ | [`agents/drivers/vastbase-go/main_test.go`](agents/drivers/vastbase-go/main_test.go) |
| 350 | ✓ | [`agents/drivers/vastbase-go/main.go`](agents/drivers/vastbase-go/main.go) |
| 351 | ✓ | [`agents/drivers/vastbase-go/protocol_error_test.go`](agents/drivers/vastbase-go/protocol_error_test.go) |
| 352 | ✓ | [`agents/drivers/vastbase-go/protocol_error.go`](agents/drivers/vastbase-go/protocol_error.go) |
| 353 | ✓ | [`agents/drivers/vastbase-go/README.md`](agents/drivers/vastbase-go/README.md) |
| 354 | ✓ | [`agents/drivers/vastbase-go/runtime_pool_test.go`](agents/drivers/vastbase-go/runtime_pool_test.go) |
| 355 | ✓ | [`agents/drivers/vastbase-go/runtime_pool.go`](agents/drivers/vastbase-go/runtime_pool.go) |
| 356 | ✓ | [`agents/drivers/vastbase-go/spatial_test.go`](agents/drivers/vastbase-go/spatial_test.go) |
| 357 | ✓ | [`agents/drivers/vastbase-go/spatial.go`](agents/drivers/vastbase-go/spatial.go) |
| 358 | ✓ | [`agents/drivers/vastbase-go/vastbase_metadata_test.go`](agents/drivers/vastbase-go/vastbase_metadata_test.go) |
| 359 | ✓ | [`agents/drivers/vastbase-go/vastbase_metadata.go`](agents/drivers/vastbase-go/vastbase_metadata.go) |
| 360 | ✓ | [`agents/drivers/vertica/build.gradle`](agents/drivers/vertica/build.gradle) |
| 361 | ✓ | [`agents/drivers/vertica/src/main/java/com/dbx/agent/vertica/VerticaAgent.java`](agents/drivers/vertica/src/main/java/com/dbx/agent/vertica/VerticaAgent.java) |
| 362 | ✓ | [`agents/drivers/xugu/go.mod`](agents/drivers/xugu/go.mod) |
| 363 | ✓ | [`agents/drivers/xugu/go.sum`](agents/drivers/xugu/go.sum) |
| 364 | ✓ | [`agents/drivers/xugu/main_test.go`](agents/drivers/xugu/main_test.go) |
| 365 | ✓ | [`agents/drivers/xugu/main.go`](agents/drivers/xugu/main.go) |
| 366 | ✓ | [`agents/drivers/xugu/package_members_test.go`](agents/drivers/xugu/package_members_test.go) |
| 367 | ✓ | [`agents/drivers/xugu/package_members.go`](agents/drivers/xugu/package_members.go) |
| 368 | ✓ | [`agents/drivers/xugu/protocol_error_live_test.go`](agents/drivers/xugu/protocol_error_live_test.go) |
| 369 | ✓ | [`agents/drivers/xugu/protocol_error_test.go`](agents/drivers/xugu/protocol_error_test.go) |
| 370 | ✓ | [`agents/drivers/xugu/protocol_error.go`](agents/drivers/xugu/protocol_error.go) |
| 371 | ✓ | [`agents/drivers/xugu/README.md`](agents/drivers/xugu/README.md) |
| 372 | ✓ | [`agents/drivers/xugu/synonym_scope_live_test.go`](agents/drivers/xugu/synonym_scope_live_test.go) |
| 373 | ✓ | [`agents/drivers/xugu/trigger_live_test.go`](agents/drivers/xugu/trigger_live_test.go) |
| 374 | ✓ | [`agents/drivers/xugu/type_members_live_test.go`](agents/drivers/xugu/type_members_live_test.go) |
| 375 | ✓ | [`agents/drivers/xugu/type_members_test.go`](agents/drivers/xugu/type_members_test.go) |
| 376 | ✓ | [`agents/drivers/xugu/type_members.go`](agents/drivers/xugu/type_members.go) |
| 377 | ✓ | [`agents/drivers/yashandb/build.gradle`](agents/drivers/yashandb/build.gradle) |
| 378 | ✓ | [`agents/drivers/yashandb/src/main/java/com/dbx/agent/yashandb/YashandbAgent.java`](agents/drivers/yashandb/src/main/java/com/dbx/agent/yashandb/YashandbAgent.java) |
| 379 | ✓ | [`agents/drivers/yashandb/src/test/java/com/dbx/agent/yashandb/YashandbAgentTest.java`](agents/drivers/yashandb/src/test/java/com/dbx/agent/yashandb/YashandbAgentTest.java) |
| 380 | ✓ | [`agents/drivers/zookeeper/agent_test.go`](agents/drivers/zookeeper/agent_test.go) |
| 381 | ✓ | [`agents/drivers/zookeeper/connection.go`](agents/drivers/zookeeper/connection.go) |
| 382 | ✓ | [`agents/drivers/zookeeper/go.mod`](agents/drivers/zookeeper/go.mod) |
| 383 | ✓ | [`agents/drivers/zookeeper/go.sum`](agents/drivers/zookeeper/go.sum) |
| 384 | ✓ | [`agents/drivers/zookeeper/integration_test.go`](agents/drivers/zookeeper/integration_test.go) |
| 385 | ✓ | [`agents/drivers/zookeeper/main.go`](agents/drivers/zookeeper/main.go) |
| 386 | ✓ | [`agents/drivers/zookeeper/operations.go`](agents/drivers/zookeeper/operations.go) |
| 387 | ✓ | [`agents/drivers/zookeeper/sasl_test.go`](agents/drivers/zookeeper/sasl_test.go) |
| 388 | ✓ | [`agents/drivers/zookeeper/sasl.go`](agents/drivers/zookeeper/sasl.go) |
| 389 | ✓ | [`agents/go-common/go-gssapi/common/channel_binding.go`](agents/go-common/go-gssapi/common/channel_binding.go) |
| 390 | ✓ | [`agents/go-common/go-gssapi/flags_test.go`](agents/go-common/go-gssapi/flags_test.go) |
| 391 | ✓ | [`agents/go-common/go-gssapi/flags.go`](agents/go-common/go-gssapi/flags.go) |
| 392 | ✓ | [`agents/go-common/go-gssapi/go.mod`](agents/go-common/go-gssapi/go.mod) |
| 393 | ✓ | [`agents/go-common/go-gssapi/go.sum`](agents/go-common/go-gssapi/go.sum) |
| 394 | ✓ | [`agents/go-common/go-gssapi/interface.go`](agents/go-common/go-gssapi/interface.go) |
| 395 | ✓ | [`agents/go-common/go-gssapi/krb5/APRep_test.go`](agents/go-common/go-gssapi/krb5/APRep_test.go) |
| 396 | ✓ | [`agents/go-common/go-gssapi/krb5/APRep.go`](agents/go-common/go-gssapi/krb5/APRep.go) |
| 397 | ✓ | [`agents/go-common/go-gssapi/krb5/context_token_test.go`](agents/go-common/go-gssapi/krb5/context_token_test.go) |
| 398 | ✓ | [`agents/go-common/go-gssapi/krb5/context_token.go`](agents/go-common/go-gssapi/krb5/context_token.go) |
| 399 | ✓ | [`agents/go-common/go-gssapi/krb5/credentials_test.go`](agents/go-common/go-gssapi/krb5/credentials_test.go) |
| 400 | ✓ | [`agents/go-common/go-gssapi/krb5/default_paths_unix.go`](agents/go-common/go-gssapi/krb5/default_paths_unix.go) |
| 401 | ✓ | [`agents/go-common/go-gssapi/krb5/default_paths_windows.go`](agents/go-common/go-gssapi/krb5/default_paths_windows.go) |
| 402 | ✓ | [`agents/go-common/go-gssapi/krb5/keyinfo_test.go`](agents/go-common/go-gssapi/krb5/keyinfo_test.go) |
| 403 | ✓ | [`agents/go-common/go-gssapi/krb5/keyinfo.go`](agents/go-common/go-gssapi/krb5/keyinfo.go) |
| 404 | ✓ | [`agents/go-common/go-gssapi/krb5/krb5_test.go`](agents/go-common/go-gssapi/krb5/krb5_test.go) |
| 405 | ✓ | [`agents/go-common/go-gssapi/krb5/krb5.go`](agents/go-common/go-gssapi/krb5/krb5.go) |
| 406 | ✓ | [`agents/go-common/go-gssapi/krb5/message_token_test.go`](agents/go-common/go-gssapi/krb5/message_token_test.go) |
| 407 | ✓ | [`agents/go-common/go-gssapi/krb5/message_token.go`](agents/go-common/go-gssapi/krb5/message_token.go) |
| 408 | ✓ | [`agents/go-common/go-gssapi/krb5/sample_test.go`](agents/go-common/go-gssapi/krb5/sample_test.go) |
| 409 | ✓ | [`agents/go-common/go-gssapi/LICENSE`](agents/go-common/go-gssapi/LICENSE) |
| 410 | ✓ | [`agents/go-common/go-gssapi/README.md`](agents/go-common/go-gssapi/README.md) |
| 411 | ✓ | [`agents/go-common/go-gssapi/registry.go`](agents/go-common/go-gssapi/registry.go) |
| 412 | ✓ | [`agents/go-common/gohive/browser_auth_test.go`](agents/go-common/gohive/browser_auth_test.go) |
| 413 | ✓ | [`agents/go-common/gohive/browser_auth.go`](agents/go-common/gohive/browser_auth.go) |
| 414 | ✓ | [`agents/go-common/gohive/connector.go`](agents/go-common/gohive/connector.go) |
| 415 | ✓ | [`agents/go-common/gohive/driver_test.go`](agents/go-common/gohive/driver_test.go) |
| 416 | ✓ | [`agents/go-common/gohive/driver.go`](agents/go-common/gohive/driver.go) |
| 417 | ✓ | [`agents/go-common/gohive/dsn_test.go`](agents/go-common/gohive/dsn_test.go) |
| 418 | ✓ | [`agents/go-common/gohive/dsn.go`](agents/go-common/gohive/dsn.go) |
| 419 | ✓ | [`agents/go-common/gohive/go.mod`](agents/go-common/gohive/go.mod) |
| 420 | ✓ | [`agents/go-common/gohive/go.sum`](agents/go-common/gohive/go.sum) |
| 421 | ✓ | [`agents/go-common/gohive/hive.go`](agents/go-common/gohive/hive.go) |
| 422 | ✓ | [`agents/go-common/gohive/http_auth_test.go`](agents/go-common/gohive/http_auth_test.go) |
| 423 | ✓ | [`agents/go-common/gohive/LICENSE`](agents/go-common/gohive/LICENSE) |
| 424 | ✓ | [`agents/go-common/gohive/metadata.go`](agents/go-common/gohive/metadata.go) |
| 425 | ✓ | [`agents/go-common/gohive/sasl_transport_test.go`](agents/go-common/gohive/sasl_transport_test.go) |
| 426 | ✓ | [`agents/go-common/gohive/sasl_transport.go`](agents/go-common/gohive/sasl_transport.go) |
| 427 | ✓ | [`agents/go-common/gosasl/go.mod`](agents/go-common/gosasl/go.mod) |
| 428 | ✓ | [`agents/go-common/gosasl/go.sum`](agents/go-common/gosasl/go.sum) |
| 429 | ✓ | [`agents/go-common/gosasl/gssapi_backend_nonwindows.go`](agents/go-common/gosasl/gssapi_backend_nonwindows.go) |
| 430 | ✓ | [`agents/go-common/gosasl/gssapi_backend_windows.go`](agents/go-common/gosasl/gssapi_backend_windows.go) |
| 431 | ✓ | [`agents/go-common/gosasl/gssapi_purego.go`](agents/go-common/gosasl/gssapi_purego.go) |
| 432 | ✓ | [`agents/go-common/gosasl/gssapi.go`](agents/go-common/gosasl/gssapi.go) |
| 433 | ✓ | [`agents/go-common/gosasl/http_spnego_test.go`](agents/go-common/gosasl/http_spnego_test.go) |
| 434 | ✓ | [`agents/go-common/gosasl/http_spnego.go`](agents/go-common/gosasl/http_spnego.go) |
| 435 | ✓ | [`agents/go-common/gosasl/LICENSE`](agents/go-common/gosasl/LICENSE) |
| 436 | ✓ | [`agents/go-common/gosasl/README.md`](agents/go-common/gosasl/README.md) |
| 437 | ✓ | [`agents/go-common/gosasl/sasl_gssapi_test.go`](agents/go-common/gosasl/sasl_gssapi_test.go) |
| 438 | ✓ | [`agents/go-common/gosasl/sasl_test.go`](agents/go-common/gosasl/sasl_test.go) |
| 439 | ✓ | [`agents/go-common/gosasl/sasl.go`](agents/go-common/gosasl/sasl.go) |
| 440 | ✓ | [`agents/gradle/wrapper/gradle-wrapper.jar`](agents/gradle/wrapper/gradle-wrapper.jar) |
| 441 | ✓ | [`agents/gradle/wrapper/gradle-wrapper.properties`](agents/gradle/wrapper/gradle-wrapper.properties) |
| 442 | ✓ | [`agents/gradlew`](agents/gradlew) |
| 443 | ✓ | [`agents/gradlew.bat`](agents/gradlew.bat) |
| 444 | ✓ | [`agents/metadata-constraint-coverage.tsv`](agents/metadata-constraint-coverage.tsv) |
| 445 | ✓ | [`agents/README.md`](agents/README.md) |
| 446 | ✓ | [`agents/README.zh-CN.md`](agents/README.zh-CN.md) |
| 447 | ✓ | [`agents/scripts/build_driver_zips.py`](agents/scripts/build_driver_zips.py) |
| 448 | ✓ | [`agents/scripts/build_offline_jdbc_payload.mjs`](agents/scripts/build_offline_jdbc_payload.mjs) |
| 449 | ✓ | [`agents/scripts/build_offline_zip.sh`](agents/scripts/build_offline_zip.sh) |
| 450 | ✓ | [`agents/scripts/driver_release_packages_test.py`](agents/scripts/driver_release_packages_test.py) |
| 451 | ✓ | [`agents/scripts/release.sh`](agents/scripts/release.sh) |
| 452 | ✓ | [`agents/scripts/validate_agent_jars.py`](agents/scripts/validate_agent_jars.py) |
| 453 | ✓ | [`agents/scripts/validate_agents_test.py`](agents/scripts/validate_agents_test.py) |
| 454 | ✓ | [`agents/scripts/validate_agents.py`](agents/scripts/validate_agents.py) |
| 455 | ✓ | [`agents/scripts/validate_windows_pe_dependencies_test.py`](agents/scripts/validate_windows_pe_dependencies_test.py) |
| 456 | ✓ | [`agents/scripts/validate_windows_pe_dependencies.py`](agents/scripts/validate_windows_pe_dependencies.py) |
| 457 | ✓ | [`agents/scripts/verify_offline_jdbc_release.mjs`](agents/scripts/verify_offline_jdbc_release.mjs) |
| 458 | ✓ | [`agents/scripts/version_agent_artifacts.py`](agents/scripts/version_agent_artifacts.py) |
| 459 | ✓ | [`agents/settings.gradle`](agents/settings.gradle) |
| 460 | ✓ | [`agents/test-support/build.gradle`](agents/test-support/build.gradle) |
| 461 | ✓ | [`agents/test-support/src/main/java/com/dbx/agent/test/JdbcAgentFake.java`](agents/test-support/src/main/java/com/dbx/agent/test/JdbcAgentFake.java) |
| 462 | ✓ | [`agents/test-support/src/main/java/com/dbx/agent/test/JdbcConnectedAgentTest.java`](agents/test-support/src/main/java/com/dbx/agent/test/JdbcConnectedAgentTest.java) |
| 463 | ✓ | [`agents/test-support/src/main/java/com/dbx/agent/test/JdbcExecutionBehaviorTest.java`](agents/test-support/src/main/java/com/dbx/agent/test/JdbcExecutionBehaviorTest.java) |
| 464 | ✓ | [`agents/test-support/src/main/java/com/dbx/agent/test/JdbcFakeExecutionBehaviorTest.java`](agents/test-support/src/main/java/com/dbx/agent/test/JdbcFakeExecutionBehaviorTest.java) |
| 465 | ✓ | [`agents/test-support/src/main/java/com/dbx/agent/test/JdbcMetadataBehaviorTest.java`](agents/test-support/src/main/java/com/dbx/agent/test/JdbcMetadataBehaviorTest.java) |
| 466 | ✓ | [`agents/test-support/src/main/java/com/dbx/agent/test/JdbcMetadataSqlFake.java`](agents/test-support/src/main/java/com/dbx/agent/test/JdbcMetadataSqlFake.java) |
| 467 | ✓ | [`agents/test-support/src/main/java/com/dbx/agent/test/TestSupport.java`](agents/test-support/src/main/java/com/dbx/agent/test/TestSupport.java) |
| 468 | ✓ | [`agents/versions.json`](agents/versions.json) |
| 469 | ✓ | [`apps/desktop/src/components/mq/README.md`](apps/desktop/src/components/mq/README.md) |
| 470 | ✓ | [`apps/desktop/src/lib/README.md`](apps/desktop/src/lib/README.md) |
| 471 | ✓ | [`apps/desktop/src/lib/sql/semantic/README.md`](apps/desktop/src/lib/sql/semantic/README.md) |
| 472 | ✓ | [`apps/README.md`](apps/README.md) |
| 473 | ✓ | [`crates/dbx-core/src/mq/README.md`](crates/dbx-core/src/mq/README.md) |
| 474 | ✓ | [`crates/README.md`](crates/README.md) |
| 475 | ✓ | [`deploy/1panel/README.md`](deploy/1panel/README.md) |
| 476 | ✓ | [`deploy/database/consul/2.0.2/init/README.md`](deploy/database/consul/2.0.2/init/README.md) |
| 477 | ✓ | [`deploy/database/elasticsearch/6.8/init/README.md`](deploy/database/elasticsearch/6.8/init/README.md) |
| 478 | ✓ | [`deploy/database/etcd/3.7/init/README.md`](deploy/database/etcd/3.7/init/README.md) |
| 479 | ✓ | [`deploy/database/kafka/4.3/init/README.md`](deploy/database/kafka/4.3/init/README.md) |
| 480 | ✓ | [`deploy/database/nacos/2.5/init/README.md`](deploy/database/nacos/2.5/init/README.md) |
| 481 | ✓ | [`deploy/database/nacos/3.2/init/README.md`](deploy/database/nacos/3.2/init/README.md) |
| 482 | ✓ | [`deploy/database/pulsar/4.2/init/README.md`](deploy/database/pulsar/4.2/init/README.md) |
| 483 | ✓ | [`deploy/database/qdrant/1.8/init/README.md`](deploy/database/qdrant/1.8/init/README.md) |
| 484 | ✓ | [`deploy/database/redis/3.0.7/init/README.md`](deploy/database/redis/3.0.7/init/README.md) |
| 485 | ✓ | [`deploy/database/redis/7.4/init/README.md`](deploy/database/redis/7.4/init/README.md) |
| 486 | ✓ | [`deploy/database/rnacos/0.8/init/README.md`](deploy/database/rnacos/0.8/init/README.md) |
| 487 | ✓ | [`deploy/database/zookeeper/3.9/init/README.md`](deploy/database/zookeeper/3.9/init/README.md) |
| 488 | ✓ | [`deploy/dockerhub/README.md`](deploy/dockerhub/README.md) |
| 489 | ✓ | [`docs/public/llms.txt`](docs/public/llms.txt) |
| 490 | ✓ | [`examples/README.md`](examples/README.md) |
| 491 | ✓ | [`packages/mcp-darwin-arm64/README.md`](packages/mcp-darwin-arm64/README.md) |
| 492 | ✓ | [`packages/mcp-darwin-x64/README.md`](packages/mcp-darwin-x64/README.md) |
| 493 | ✓ | [`packages/mcp-linux-arm64-gnu/README.md`](packages/mcp-linux-arm64-gnu/README.md) |
| 494 | ✓ | [`packages/mcp-linux-x64-gnu/README.md`](packages/mcp-linux-x64-gnu/README.md) |
| 495 | ✓ | [`packages/mcp-win32-arm64/README.md`](packages/mcp-win32-arm64/README.md) |
| 496 | ✓ | [`packages/mcp-win32-x64/README.md`](packages/mcp-win32-x64/README.md) |
| 497 | ✓ | [`plugins/jdbc/README.md`](plugins/jdbc/README.md) |
| 498 | ✓ | [`plugins/README.md`](plugins/README.md) |
| 499 | ✓ | [`skills/dbx/SKILL.md`](skills/dbx/SKILL.md) |
| 500 | ✓ | [`vendor/ctor/README.md`](vendor/ctor/README.md) |
| 501 | ✓ | [`vendor/dirs-sys/README.md`](vendor/dirs-sys/README.md) |
| 502 | ✓ | [`vendor/rumqttc/README.md`](vendor/rumqttc/README.md) |
| 503 | ✓ | [`vendor/wry/README.md`](vendor/wry/README.md) |
| 504 | → | [`CONTRIBUTING.md`](CONTRIBUTING.md) |
| 505 | → | [`CONTRIBUTING.zh-CN.md`](CONTRIBUTING.zh-CN.md) |
| 506 | → | [`deploy/database/README.md`](deploy/database/README.md) |
| 507 | → | [`deploy/database/README.zh-CN.md`](deploy/database/README.zh-CN.md) |
| 508 | → | [`packages/cli/README.md`](packages/cli/README.md) |
| 509 | → | [`packages/mcp-server/README.md`](packages/mcp-server/README.md) |
| 510 | → | [`README.md`](README.md) |
| 511 | → | [`README.zh-CN.md`](README.zh-CN.md) |

---

*Generated by mirror — do not edit manually*