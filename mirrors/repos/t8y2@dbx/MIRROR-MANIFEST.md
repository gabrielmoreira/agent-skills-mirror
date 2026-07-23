---
repo: t8y2/dbx
repoUrl: https://github.com/t8y2/dbx.git
refType: branch
ref: main
---

# Mirror Manifest

Mirror of `t8y2/dbx` — 26 default patterns, 8 followed patterns, 285 file(s) materialized.

## Metadata

| Field         | Value |
|---------------|-------|
| Repo          | `t8y2/dbx` |
| Ref Type      | `branch` |
| Ref           | `main` |
| Default pats  | 26 |
| Followed pats | 8 |
| Files         | 285 |

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
| 7 | ✓ | [`agents/common/src/main/java/com/dbx/agent/BaseDatabaseAgent.java`](agents/common/src/main/java/com/dbx/agent/BaseDatabaseAgent.java) |
| 8 | ✓ | [`agents/common/src/main/java/com/dbx/agent/BatchExecutor.java`](agents/common/src/main/java/com/dbx/agent/BatchExecutor.java) |
| 9 | ✓ | [`agents/common/src/main/java/com/dbx/agent/CheckConstraintInfo.java`](agents/common/src/main/java/com/dbx/agent/CheckConstraintInfo.java) |
| 10 | ✓ | [`agents/common/src/main/java/com/dbx/agent/ColumnInfo.java`](agents/common/src/main/java/com/dbx/agent/ColumnInfo.java) |
| 11 | ✓ | [`agents/common/src/main/java/com/dbx/agent/CompletionAssistantCandidate.java`](agents/common/src/main/java/com/dbx/agent/CompletionAssistantCandidate.java) |
| 12 | ✓ | [`agents/common/src/main/java/com/dbx/agent/CompletionAssistantCandidateKind.java`](agents/common/src/main/java/com/dbx/agent/CompletionAssistantCandidateKind.java) |
| 13 | ✓ | [`agents/common/src/main/java/com/dbx/agent/CompletionAssistantMatchMode.java`](agents/common/src/main/java/com/dbx/agent/CompletionAssistantMatchMode.java) |
| 14 | ✓ | [`agents/common/src/main/java/com/dbx/agent/CompletionAssistantObjectKind.java`](agents/common/src/main/java/com/dbx/agent/CompletionAssistantObjectKind.java) |
| 15 | ✓ | [`agents/common/src/main/java/com/dbx/agent/CompletionAssistantRequest.java`](agents/common/src/main/java/com/dbx/agent/CompletionAssistantRequest.java) |
| 16 | ✓ | [`agents/common/src/main/java/com/dbx/agent/CompletionAssistantResponse.java`](agents/common/src/main/java/com/dbx/agent/CompletionAssistantResponse.java) |
| 17 | ✓ | [`agents/common/src/main/java/com/dbx/agent/ConfiguredJdbcAgent.java`](agents/common/src/main/java/com/dbx/agent/ConfiguredJdbcAgent.java) |
| 18 | ✓ | [`agents/common/src/main/java/com/dbx/agent/ConnectParams.java`](agents/common/src/main/java/com/dbx/agent/ConnectParams.java) |
| 19 | ✓ | [`agents/common/src/main/java/com/dbx/agent/DatabaseAgent.java`](agents/common/src/main/java/com/dbx/agent/DatabaseAgent.java) |
| 20 | ✓ | [`agents/common/src/main/java/com/dbx/agent/DatabaseInfo.java`](agents/common/src/main/java/com/dbx/agent/DatabaseInfo.java) |
| 21 | ✓ | [`agents/common/src/main/java/com/dbx/agent/DdlBuilder.java`](agents/common/src/main/java/com/dbx/agent/DdlBuilder.java) |
| 22 | ✓ | [`agents/common/src/main/java/com/dbx/agent/EwkbWktDecoder.java`](agents/common/src/main/java/com/dbx/agent/EwkbWktDecoder.java) |
| 23 | ✓ | [`agents/common/src/main/java/com/dbx/agent/ExecuteQueryOptions.java`](agents/common/src/main/java/com/dbx/agent/ExecuteQueryOptions.java) |
| 24 | ✓ | [`agents/common/src/main/java/com/dbx/agent/ExecuteQueryParams.java`](agents/common/src/main/java/com/dbx/agent/ExecuteQueryParams.java) |
| 25 | ✓ | [`agents/common/src/main/java/com/dbx/agent/ForeignKeyInfo.java`](agents/common/src/main/java/com/dbx/agent/ForeignKeyInfo.java) |
| 26 | ✓ | [`agents/common/src/main/java/com/dbx/agent/IndexInfo.java`](agents/common/src/main/java/com/dbx/agent/IndexInfo.java) |
| 27 | ✓ | [`agents/common/src/main/java/com/dbx/agent/JdbcAgentProfile.java`](agents/common/src/main/java/com/dbx/agent/JdbcAgentProfile.java) |
| 28 | ✓ | [`agents/common/src/main/java/com/dbx/agent/JdbcDatabaseInfo.java`](agents/common/src/main/java/com/dbx/agent/JdbcDatabaseInfo.java) |
| 29 | ✓ | [`agents/common/src/main/java/com/dbx/agent/JdbcExecutor.java`](agents/common/src/main/java/com/dbx/agent/JdbcExecutor.java) |
| 30 | ✓ | [`agents/common/src/main/java/com/dbx/agent/JdbcIdentifiers.java`](agents/common/src/main/java/com/dbx/agent/JdbcIdentifiers.java) |
| 31 | ✓ | [`agents/common/src/main/java/com/dbx/agent/JdbcSchemaSwitcher.java`](agents/common/src/main/java/com/dbx/agent/JdbcSchemaSwitcher.java) |
| 32 | ✓ | [`agents/common/src/main/java/com/dbx/agent/JsonRpcServer.java`](agents/common/src/main/java/com/dbx/agent/JsonRpcServer.java) |
| 33 | ✓ | [`agents/common/src/main/java/com/dbx/agent/MetadataListConstraints.java`](agents/common/src/main/java/com/dbx/agent/MetadataListConstraints.java) |
| 34 | ✓ | [`agents/common/src/main/java/com/dbx/agent/MetadataSqlSupport.java`](agents/common/src/main/java/com/dbx/agent/MetadataSqlSupport.java) |
| 35 | ✓ | [`agents/common/src/main/java/com/dbx/agent/MultiSessionJsonRpcServer.java`](agents/common/src/main/java/com/dbx/agent/MultiSessionJsonRpcServer.java) |
| 36 | ✓ | [`agents/common/src/main/java/com/dbx/agent/ObjectInfo.java`](agents/common/src/main/java/com/dbx/agent/ObjectInfo.java) |
| 37 | ✓ | [`agents/common/src/main/java/com/dbx/agent/ObjectSource.java`](agents/common/src/main/java/com/dbx/agent/ObjectSource.java) |
| 38 | ✓ | [`agents/common/src/main/java/com/dbx/agent/PostgresLikeAgent.java`](agents/common/src/main/java/com/dbx/agent/PostgresLikeAgent.java) |
| 39 | ✓ | [`agents/common/src/main/java/com/dbx/agent/PostgresLikeAgentProfile.java`](agents/common/src/main/java/com/dbx/agent/PostgresLikeAgentProfile.java) |
| 40 | ✓ | [`agents/common/src/main/java/com/dbx/agent/QueryPageOptions.java`](agents/common/src/main/java/com/dbx/agent/QueryPageOptions.java) |
| 41 | ✓ | [`agents/common/src/main/java/com/dbx/agent/QueryPageParams.java`](agents/common/src/main/java/com/dbx/agent/QueryPageParams.java) |
| 42 | ✓ | [`agents/common/src/main/java/com/dbx/agent/QueryPageResult.java`](agents/common/src/main/java/com/dbx/agent/QueryPageResult.java) |
| 43 | ✓ | [`agents/common/src/main/java/com/dbx/agent/QueryResult.java`](agents/common/src/main/java/com/dbx/agent/QueryResult.java) |
| 44 | ✓ | [`agents/common/src/main/java/com/dbx/agent/SchemaTableParams.java`](agents/common/src/main/java/com/dbx/agent/SchemaTableParams.java) |
| 45 | ✓ | [`agents/common/src/main/java/com/dbx/agent/StandardJdbcMetadata.java`](agents/common/src/main/java/com/dbx/agent/StandardJdbcMetadata.java) |
| 46 | ✓ | [`agents/common/src/main/java/com/dbx/agent/TableInfo.java`](agents/common/src/main/java/com/dbx/agent/TableInfo.java) |
| 47 | ✓ | [`agents/common/src/main/java/com/dbx/agent/TransactionExecutor.java`](agents/common/src/main/java/com/dbx/agent/TransactionExecutor.java) |
| 48 | ✓ | [`agents/common/src/main/java/com/dbx/agent/TriggerInfo.java`](agents/common/src/main/java/com/dbx/agent/TriggerInfo.java) |
| 49 | ✓ | [`agents/common/src/main/resources/agent-protocol-v1.json`](agents/common/src/main/resources/agent-protocol-v1.json) |
| 50 | ✓ | [`agents/common/src/main/resources/agent-protocol-v2.json`](agents/common/src/main/resources/agent-protocol-v2.json) |
| 51 | ✓ | [`agents/common/src/test/java/com/dbx/agent/AbstractJdbcAgentTest.java`](agents/common/src/test/java/com/dbx/agent/AbstractJdbcAgentTest.java) |
| 52 | ✓ | [`agents/common/src/test/java/com/dbx/agent/BatchExecutorTest.java`](agents/common/src/test/java/com/dbx/agent/BatchExecutorTest.java) |
| 53 | ✓ | [`agents/common/src/test/java/com/dbx/agent/CommonJavaCompatibilityTest.java`](agents/common/src/test/java/com/dbx/agent/CommonJavaCompatibilityTest.java) |
| 54 | ✓ | [`agents/common/src/test/java/com/dbx/agent/ConfiguredJdbcAgentTest.java`](agents/common/src/test/java/com/dbx/agent/ConfiguredJdbcAgentTest.java) |
| 55 | ✓ | [`agents/common/src/test/java/com/dbx/agent/EwkbWktDecoderTest.java`](agents/common/src/test/java/com/dbx/agent/EwkbWktDecoderTest.java) |
| 56 | ✓ | [`agents/common/src/test/java/com/dbx/agent/JdbcAgentProfileExtendedTest.java`](agents/common/src/test/java/com/dbx/agent/JdbcAgentProfileExtendedTest.java) |
| 57 | ✓ | [`agents/common/src/test/java/com/dbx/agent/JdbcExecutorTest.java`](agents/common/src/test/java/com/dbx/agent/JdbcExecutorTest.java) |
| 58 | ✓ | [`agents/common/src/test/java/com/dbx/agent/MetadataConstraintCoverageTest.java`](agents/common/src/test/java/com/dbx/agent/MetadataConstraintCoverageTest.java) |
| 59 | ✓ | [`agents/common/src/test/java/com/dbx/agent/PostgresLikeAgentTest.java`](agents/common/src/test/java/com/dbx/agent/PostgresLikeAgentTest.java) |
| 60 | ✓ | [`agents/common/src/test/java/com/dbx/agent/StandardJdbcMetadataTest.java`](agents/common/src/test/java/com/dbx/agent/StandardJdbcMetadataTest.java) |
| 61 | ✓ | [`agents/docs/agent-authoring.md`](agents/docs/agent-authoring.md) |
| 62 | ✓ | [`agents/docs/agent-protocol-v2.md`](agents/docs/agent-protocol-v2.md) |
| 63 | ✓ | [`agents/docs/examples/jdbc-agent-template/build.gradle`](agents/docs/examples/jdbc-agent-template/build.gradle) |
| 64 | ✓ | [`agents/docs/examples/jdbc-agent-template/README.md`](agents/docs/examples/jdbc-agent-template/README.md) |
| 65 | ✓ | [`agents/docs/examples/jdbc-agent-template/settings.gradle`](agents/docs/examples/jdbc-agent-template/settings.gradle) |
| 66 | ✓ | [`agents/docs/examples/jdbc-agent-template/src/main/java/com/dbx/agent/template/TemplateAgent.java`](agents/docs/examples/jdbc-agent-template/src/main/java/com/dbx/agent/template/TemplateAgent.java) |
| 67 | ✓ | [`agents/docs/examples/jdbc-agent-template/src/test/java/com/dbx/agent/template/TemplateAgentTest.java`](agents/docs/examples/jdbc-agent-template/src/test/java/com/dbx/agent/template/TemplateAgentTest.java) |
| 68 | ✓ | [`agents/docs/release-checklist.md`](agents/docs/release-checklist.md) |
| 69 | ✓ | [`agents/drivers/access/build.gradle`](agents/drivers/access/build.gradle) |
| 70 | ✓ | [`agents/drivers/access/src/main/java/com/dbx/agent/access/AccessAgent.java`](agents/drivers/access/src/main/java/com/dbx/agent/access/AccessAgent.java) |
| 71 | ✓ | [`agents/drivers/access/src/main/java/com/dbx/agent/access/EncryptedAccessOpener.java`](agents/drivers/access/src/main/java/com/dbx/agent/access/EncryptedAccessOpener.java) |
| 72 | ✓ | [`agents/drivers/access/src/test/java/com/dbx/agent/access/AccessAgentTest.java`](agents/drivers/access/src/test/java/com/dbx/agent/access/AccessAgentTest.java) |
| 73 | ✓ | [`agents/drivers/access/src/test/resources/db2007-enc.accdb`](agents/drivers/access/src/test/resources/db2007-enc.accdb) |
| 74 | ✓ | [`agents/drivers/bigquery/build.gradle`](agents/drivers/bigquery/build.gradle) |
| 75 | ✓ | [`agents/drivers/bigquery/src/main/java/com/dbx/agent/bigquery/BigQueryAgent.java`](agents/drivers/bigquery/src/main/java/com/dbx/agent/bigquery/BigQueryAgent.java) |
| 76 | ✓ | [`agents/drivers/bigquery/src/test/java/com/dbx/agent/bigquery/BigQueryAgentMetadataTest.java`](agents/drivers/bigquery/src/test/java/com/dbx/agent/bigquery/BigQueryAgentMetadataTest.java) |
| 77 | ✓ | [`agents/drivers/bigquery/src/test/java/com/dbx/agent/bigquery/BigQueryAgentTest.java`](agents/drivers/bigquery/src/test/java/com/dbx/agent/bigquery/BigQueryAgentTest.java) |
| 78 | ✓ | [`agents/drivers/cassandra/build.gradle`](agents/drivers/cassandra/build.gradle) |
| 79 | ✓ | [`agents/drivers/cassandra/src/main/java/com/dbx/agent/cassandra/CassandraAgent.java`](agents/drivers/cassandra/src/main/java/com/dbx/agent/cassandra/CassandraAgent.java) |
| 80 | ✓ | [`agents/drivers/cassandra/src/test/java/com/dbx/agent/cassandra/CassandraAgentTest.java`](agents/drivers/cassandra/src/test/java/com/dbx/agent/cassandra/CassandraAgentTest.java) |
| 81 | ✓ | [`agents/drivers/dameng/build.gradle`](agents/drivers/dameng/build.gradle) |
| 82 | ✓ | [`agents/drivers/dameng/libs/.gitkeep`](agents/drivers/dameng/libs/.gitkeep) |
| 83 | ✓ | [`agents/drivers/dameng/src/main/java/com/dbx/agent/dameng/DamengAgent.java`](agents/drivers/dameng/src/main/java/com/dbx/agent/dameng/DamengAgent.java) |
| 84 | ✓ | [`agents/drivers/dameng/src/test/java/com/dbx/agent/dameng/DamengAgentMetadataTest.java`](agents/drivers/dameng/src/test/java/com/dbx/agent/dameng/DamengAgentMetadataTest.java) |
| 85 | ✓ | [`agents/drivers/dameng/src/test/java/com/dbx/agent/dameng/DamengAgentPagingTest.java`](agents/drivers/dameng/src/test/java/com/dbx/agent/dameng/DamengAgentPagingTest.java) |
| 86 | ✓ | [`agents/drivers/dameng/src/test/java/com/dbx/agent/dameng/DamengAgentTest.java`](agents/drivers/dameng/src/test/java/com/dbx/agent/dameng/DamengAgentTest.java) |
| 87 | ✓ | [`agents/drivers/dameng/src/test/java/com/dbx/agent/dameng/DamengAgentUrlTest.java`](agents/drivers/dameng/src/test/java/com/dbx/agent/dameng/DamengAgentUrlTest.java) |
| 88 | ✓ | [`agents/drivers/databend/build.gradle`](agents/drivers/databend/build.gradle) |
| 89 | ✓ | [`agents/drivers/databend/src/main/java/com/dbx/agent/databend/DatabendAgent.java`](agents/drivers/databend/src/main/java/com/dbx/agent/databend/DatabendAgent.java) |
| 90 | ✓ | [`agents/drivers/databend/src/test/java/com/dbx/agent/databend/DatabendAgentTest.java`](agents/drivers/databend/src/test/java/com/dbx/agent/databend/DatabendAgentTest.java) |
| 91 | ✓ | [`agents/drivers/databricks/build.gradle`](agents/drivers/databricks/build.gradle) |
| 92 | ✓ | [`agents/drivers/databricks/src/main/java/com/dbx/agent/databricks/DatabricksAgent.java`](agents/drivers/databricks/src/main/java/com/dbx/agent/databricks/DatabricksAgent.java) |
| 93 | ✓ | [`agents/drivers/databricks/src/test/java/com/dbx/agent/databricks/DatabricksAgentTest.java`](agents/drivers/databricks/src/test/java/com/dbx/agent/databricks/DatabricksAgentTest.java) |
| 94 | ✓ | [`agents/drivers/db2/build.gradle`](agents/drivers/db2/build.gradle) |
| 95 | ✓ | [`agents/drivers/db2/src/main/java/com/dbx/agent/db2/Db2Agent.java`](agents/drivers/db2/src/main/java/com/dbx/agent/db2/Db2Agent.java) |
| 96 | ✓ | [`agents/drivers/db2/src/test/java/com/dbx/agent/db2/Db2AgentTest.java`](agents/drivers/db2/src/test/java/com/dbx/agent/db2/Db2AgentTest.java) |
| 97 | ✓ | [`agents/drivers/etcd/build.gradle`](agents/drivers/etcd/build.gradle) |
| 98 | ✓ | [`agents/drivers/etcd/src/main/java/com/dbx/agent/etcd/EtcdAgent.java`](agents/drivers/etcd/src/main/java/com/dbx/agent/etcd/EtcdAgent.java) |
| 99 | ✓ | [`agents/drivers/etcd/src/test/java/com/dbx/agent/etcd/EtcdAgentTest.java`](agents/drivers/etcd/src/test/java/com/dbx/agent/etcd/EtcdAgentTest.java) |
| 100 | ✓ | [`agents/drivers/exasol/build.gradle`](agents/drivers/exasol/build.gradle) |
| 101 | ✓ | [`agents/drivers/exasol/src/main/java/com/dbx/agent/exasol/ExasolAgent.java`](agents/drivers/exasol/src/main/java/com/dbx/agent/exasol/ExasolAgent.java) |
| 102 | ✓ | [`agents/drivers/firebird/build.gradle`](agents/drivers/firebird/build.gradle) |
| 103 | ✓ | [`agents/drivers/firebird/src/main/java/com/dbx/agent/firebird/FirebirdAgent.java`](agents/drivers/firebird/src/main/java/com/dbx/agent/firebird/FirebirdAgent.java) |
| 104 | ✓ | [`agents/drivers/gbase8a/build.gradle`](agents/drivers/gbase8a/build.gradle) |
| 105 | ✓ | [`agents/drivers/gbase8a/libs/gbase-connector-java-9.5.0.10-build1-bin.jar`](agents/drivers/gbase8a/libs/gbase-connector-java-9.5.0.10-build1-bin.jar) |
| 106 | ✓ | [`agents/drivers/gbase8a/src/main/java/com/dbx/agent/gbase8a/Gbase8aAgent.java`](agents/drivers/gbase8a/src/main/java/com/dbx/agent/gbase8a/Gbase8aAgent.java) |
| 107 | ✓ | [`agents/drivers/gbase8a/src/test/java/com/dbx/agent/gbase8a/Gbase8aAgentTest.java`](agents/drivers/gbase8a/src/test/java/com/dbx/agent/gbase8a/Gbase8aAgentTest.java) |
| 108 | ✓ | [`agents/drivers/gbase8s/build.gradle`](agents/drivers/gbase8s/build.gradle) |
| 109 | ✓ | [`agents/drivers/gbase8s/libs/gbasedbt-jdbc.jar`](agents/drivers/gbase8s/libs/gbasedbt-jdbc.jar) |
| 110 | ✓ | [`agents/drivers/gbase8s/src/main/java/com/dbx/agent/gbase8s/Gbase8sAgent.java`](agents/drivers/gbase8s/src/main/java/com/dbx/agent/gbase8s/Gbase8sAgent.java) |
| 111 | ✓ | [`agents/drivers/gbase8s/src/test/java/com/dbx/agent/gbase8s/Gbase8sAgentTest.java`](agents/drivers/gbase8s/src/test/java/com/dbx/agent/gbase8s/Gbase8sAgentTest.java) |
| 112 | ✓ | [`agents/drivers/goldendb/build.gradle`](agents/drivers/goldendb/build.gradle) |
| 113 | ✓ | [`agents/drivers/goldendb/libs/.gitkeep`](agents/drivers/goldendb/libs/.gitkeep) |
| 114 | ✓ | [`agents/drivers/goldendb/src/main/java/com/dbx/agent/goldendb/GoldendbAgent.java`](agents/drivers/goldendb/src/main/java/com/dbx/agent/goldendb/GoldendbAgent.java) |
| 115 | ✓ | [`agents/drivers/goldendb/src/test/java/com/dbx/agent/goldendb/GoldendbAgentMetadataTest.java`](agents/drivers/goldendb/src/test/java/com/dbx/agent/goldendb/GoldendbAgentMetadataTest.java) |
| 116 | ✓ | [`agents/drivers/goldendb/src/test/java/com/dbx/agent/goldendb/GoldendbAgentTest.java`](agents/drivers/goldendb/src/test/java/com/dbx/agent/goldendb/GoldendbAgentTest.java) |
| 117 | ✓ | [`agents/drivers/h2-legacy/build.gradle`](agents/drivers/h2-legacy/build.gradle) |
| 118 | ✓ | [`agents/drivers/h2-legacy/src/main/java/com/dbx/agent/h2legacy/H2LegacyAgent.java`](agents/drivers/h2-legacy/src/main/java/com/dbx/agent/h2legacy/H2LegacyAgent.java) |
| 119 | ✓ | [`agents/drivers/h2/build.gradle`](agents/drivers/h2/build.gradle) |
| 120 | ✓ | [`agents/drivers/h2/src/main/java/com/dbx/agent/h2/H2Agent.java`](agents/drivers/h2/src/main/java/com/dbx/agent/h2/H2Agent.java) |
| 121 | ✓ | [`agents/drivers/h2/src/test/java/com/dbx/agent/h2/H2AgentTest.java`](agents/drivers/h2/src/test/java/com/dbx/agent/h2/H2AgentTest.java) |
| 122 | ✓ | [`agents/drivers/highgo/build.gradle`](agents/drivers/highgo/build.gradle) |
| 123 | ✓ | [`agents/drivers/highgo/src/main/java/com/dbx/agent/highgo/HighgoAgent.java`](agents/drivers/highgo/src/main/java/com/dbx/agent/highgo/HighgoAgent.java) |
| 124 | ✓ | [`agents/drivers/highgo/src/test/java/com/dbx/agent/highgo/HighgoAgentTest.java`](agents/drivers/highgo/src/test/java/com/dbx/agent/highgo/HighgoAgentTest.java) |
| 125 | ✓ | [`agents/drivers/hive/build.gradle`](agents/drivers/hive/build.gradle) |
| 126 | ✓ | [`agents/drivers/hive/src/main/java/com/dbx/agent/hive/HiveAgent.java`](agents/drivers/hive/src/main/java/com/dbx/agent/hive/HiveAgent.java) |
| 127 | ✓ | [`agents/drivers/hive/src/test/java/com/dbx/agent/hive/HiveAgentExecutionTest.java`](agents/drivers/hive/src/test/java/com/dbx/agent/hive/HiveAgentExecutionTest.java) |
| 128 | ✓ | [`agents/drivers/hive/src/test/java/com/dbx/agent/hive/HiveAgentMetadataTest.java`](agents/drivers/hive/src/test/java/com/dbx/agent/hive/HiveAgentMetadataTest.java) |
| 129 | ✓ | [`agents/drivers/hive/src/test/java/com/dbx/agent/hive/HiveAgentTest.java`](agents/drivers/hive/src/test/java/com/dbx/agent/hive/HiveAgentTest.java) |
| 130 | ✓ | [`agents/drivers/informix/build.gradle`](agents/drivers/informix/build.gradle) |
| 131 | ✓ | [`agents/drivers/informix/src/main/java/com/dbx/agent/informix/InformixAgent.java`](agents/drivers/informix/src/main/java/com/dbx/agent/informix/InformixAgent.java) |
| 132 | ✓ | [`agents/drivers/informix/src/test/java/com/dbx/agent/informix/InformixAgentExecutionTest.java`](agents/drivers/informix/src/test/java/com/dbx/agent/informix/InformixAgentExecutionTest.java) |
| 133 | ✓ | [`agents/drivers/informix/src/test/java/com/dbx/agent/informix/InformixAgentTest.java`](agents/drivers/informix/src/test/java/com/dbx/agent/informix/InformixAgentTest.java) |
| 134 | ✓ | [`agents/drivers/iotdb/build.gradle`](agents/drivers/iotdb/build.gradle) |
| 135 | ✓ | [`agents/drivers/iotdb/src/main/java/com/dbx/agent/iotdb/IoTDBAgent.java`](agents/drivers/iotdb/src/main/java/com/dbx/agent/iotdb/IoTDBAgent.java) |
| 136 | ✓ | [`agents/drivers/iotdb/src/test/java/com/dbx/agent/iotdb/IoTDBAgentTest.java`](agents/drivers/iotdb/src/test/java/com/dbx/agent/iotdb/IoTDBAgentTest.java) |
| 137 | ✓ | [`agents/drivers/iris/build.gradle`](agents/drivers/iris/build.gradle) |
| 138 | ✓ | [`agents/drivers/iris/src/main/java/com/dbx/agent/iris/IrisAgent.java`](agents/drivers/iris/src/main/java/com/dbx/agent/iris/IrisAgent.java) |
| 139 | ✓ | [`agents/drivers/iris/src/test/java/com/dbx/agent/iris/IrisAgentTest.java`](agents/drivers/iris/src/test/java/com/dbx/agent/iris/IrisAgentTest.java) |
| 140 | ✓ | [`agents/drivers/kafka/build.gradle`](agents/drivers/kafka/build.gradle) |
| 141 | ✓ | [`agents/drivers/kafka/src/main/java/com/dbx/agent/kafka/KafkaAgent.java`](agents/drivers/kafka/src/main/java/com/dbx/agent/kafka/KafkaAgent.java) |
| 142 | ✓ | [`agents/drivers/kafka/src/test/java/com/dbx/agent/kafka/KafkaAgentTest.java`](agents/drivers/kafka/src/test/java/com/dbx/agent/kafka/KafkaAgentTest.java) |
| 143 | ✓ | [`agents/drivers/kingbase-go/bench/agent_compare.go`](agents/drivers/kingbase-go/bench/agent_compare.go) |
| 144 | ✓ | [`agents/drivers/kingbase-go/go.mod`](agents/drivers/kingbase-go/go.mod) |
| 145 | ✓ | [`agents/drivers/kingbase-go/go.sum`](agents/drivers/kingbase-go/go.sum) |
| 146 | ✓ | [`agents/drivers/kingbase-go/integration_test.go`](agents/drivers/kingbase-go/integration_test.go) |
| 147 | ✓ | [`agents/drivers/kingbase-go/kingbase_metadata.go`](agents/drivers/kingbase-go/kingbase_metadata.go) |
| 148 | ✓ | [`agents/drivers/kingbase-go/main_test.go`](agents/drivers/kingbase-go/main_test.go) |
| 149 | ✓ | [`agents/drivers/kingbase-go/main.go`](agents/drivers/kingbase-go/main.go) |
| 150 | ✓ | [`agents/drivers/kingbase/build.gradle`](agents/drivers/kingbase/build.gradle) |
| 151 | ✓ | [`agents/drivers/kingbase/libs/.gitkeep`](agents/drivers/kingbase/libs/.gitkeep) |
| 152 | ✓ | [`agents/drivers/kingbase/src/main/java/com/dbx/agent/kingbase/KingbaseAgent.java`](agents/drivers/kingbase/src/main/java/com/dbx/agent/kingbase/KingbaseAgent.java) |
| 153 | ✓ | [`agents/drivers/kingbase/src/test/java/com/dbx/agent/kingbase/KingbaseAgentTest.java`](agents/drivers/kingbase/src/test/java/com/dbx/agent/kingbase/KingbaseAgentTest.java) |
| 154 | ✓ | [`agents/drivers/kylin/build.gradle`](agents/drivers/kylin/build.gradle) |
| 155 | ✓ | [`agents/drivers/kylin/src/main/java/com/dbx/agent/kylin/KylinAgent.java`](agents/drivers/kylin/src/main/java/com/dbx/agent/kylin/KylinAgent.java) |
| 156 | ✓ | [`agents/drivers/kylin/src/test/java/com/dbx/agent/kylin/KylinAgentTest.java`](agents/drivers/kylin/src/test/java/com/dbx/agent/kylin/KylinAgentTest.java) |
| 157 | ✓ | [`agents/drivers/mongodb/build.gradle`](agents/drivers/mongodb/build.gradle) |
| 158 | ✓ | [`agents/drivers/mongodb/src/main/java/com/dbx/agent/mongodb/MongoAgent.java`](agents/drivers/mongodb/src/main/java/com/dbx/agent/mongodb/MongoAgent.java) |
| 159 | ✓ | [`agents/drivers/mongodb/src/test/java/com/dbx/agent/mongodb/MongoAgentTest.java`](agents/drivers/mongodb/src/test/java/com/dbx/agent/mongodb/MongoAgentTest.java) |
| 160 | ✓ | [`agents/drivers/neo4j/build.gradle`](agents/drivers/neo4j/build.gradle) |
| 161 | ✓ | [`agents/drivers/neo4j/src/main/java/com/dbx/agent/neo4j/Neo4jAgent.java`](agents/drivers/neo4j/src/main/java/com/dbx/agent/neo4j/Neo4jAgent.java) |
| 162 | ✓ | [`agents/drivers/neo4j/src/test/java/com/dbx/agent/neo4j/Neo4jAgentTest.java`](agents/drivers/neo4j/src/test/java/com/dbx/agent/neo4j/Neo4jAgentTest.java) |
| 163 | ✓ | [`agents/drivers/oceanbase-oracle/build.gradle`](agents/drivers/oceanbase-oracle/build.gradle) |
| 164 | ✓ | [`agents/drivers/oceanbase-oracle/src/main/java/com/dbx/agent/oceanbaseoracle/OceanBaseOracleAgent.java`](agents/drivers/oceanbase-oracle/src/main/java/com/dbx/agent/oceanbaseoracle/OceanBaseOracleAgent.java) |
| 165 | ✓ | [`agents/drivers/oceanbase-oracle/src/test/java/com/dbx/agent/oceanbaseoracle/OceanBaseOracleAgentTest.java`](agents/drivers/oceanbase-oracle/src/test/java/com/dbx/agent/oceanbaseoracle/OceanBaseOracleAgentTest.java) |
| 166 | ✓ | [`agents/drivers/oracle-go/.gitignore`](agents/drivers/oracle-go/.gitignore) |
| 167 | ✓ | [`agents/drivers/oracle-go/go.mod`](agents/drivers/oracle-go/go.mod) |
| 168 | ✓ | [`agents/drivers/oracle-go/go.sum`](agents/drivers/oracle-go/go.sum) |
| 169 | ✓ | [`agents/drivers/oracle-go/main_test.go`](agents/drivers/oracle-go/main_test.go) |
| 170 | ✓ | [`agents/drivers/oracle-go/main.go`](agents/drivers/oracle-go/main.go) |
| 171 | ✓ | [`agents/drivers/oracle-go/README.md`](agents/drivers/oracle-go/README.md) |
| 172 | ✓ | [`agents/drivers/oscar/build.gradle`](agents/drivers/oscar/build.gradle) |
| 173 | ✓ | [`agents/drivers/oscar/libs/oscarJDBC8.jar`](agents/drivers/oscar/libs/oscarJDBC8.jar) |
| 174 | ✓ | [`agents/drivers/oscar/src/main/java/com/dbx/agent/oscar/OscarAgent.java`](agents/drivers/oscar/src/main/java/com/dbx/agent/oscar/OscarAgent.java) |
| 175 | ✓ | [`agents/drivers/oscar/src/test/java/com/dbx/agent/oscar/OscarAgentTest.java`](agents/drivers/oscar/src/test/java/com/dbx/agent/oscar/OscarAgentTest.java) |
| 176 | ✓ | [`agents/drivers/rabbitmq/build.gradle`](agents/drivers/rabbitmq/build.gradle) |
| 177 | ✓ | [`agents/drivers/rabbitmq/src/main/java/com/dbx/agent/rabbitmq/RabbitMqAgent.java`](agents/drivers/rabbitmq/src/main/java/com/dbx/agent/rabbitmq/RabbitMqAgent.java) |
| 178 | ✓ | [`agents/drivers/rabbitmq/src/test/java/com/dbx/agent/rabbitmq/RabbitMqAgentTest.java`](agents/drivers/rabbitmq/src/test/java/com/dbx/agent/rabbitmq/RabbitMqAgentTest.java) |
| 179 | ✓ | [`agents/drivers/rocketmq/build.gradle`](agents/drivers/rocketmq/build.gradle) |
| 180 | ✓ | [`agents/drivers/rocketmq/src/main/java/com/dbx/agent/rocketmq/RocketMqAgent.java`](agents/drivers/rocketmq/src/main/java/com/dbx/agent/rocketmq/RocketMqAgent.java) |
| 181 | ✓ | [`agents/drivers/rocketmq/src/test/java/com/dbx/agent/rocketmq/RocketMqAgentTest.java`](agents/drivers/rocketmq/src/test/java/com/dbx/agent/rocketmq/RocketMqAgentTest.java) |
| 182 | ✓ | [`agents/drivers/rocketmq/src/test/java/com/dbx/agent/rocketmq/RocketMqLiveMessagePropertyTest.java`](agents/drivers/rocketmq/src/test/java/com/dbx/agent/rocketmq/RocketMqLiveMessagePropertyTest.java) |
| 183 | ✓ | [`agents/drivers/rocketmq/src/test/java/com/dbx/agent/rocketmq/RocketMqLiveTopicTypeTest.java`](agents/drivers/rocketmq/src/test/java/com/dbx/agent/rocketmq/RocketMqLiveTopicTypeTest.java) |
| 184 | ✓ | [`agents/drivers/saphana/build.gradle`](agents/drivers/saphana/build.gradle) |
| 185 | ✓ | [`agents/drivers/saphana/src/main/java/com/dbx/agent/saphana/SapHanaAgent.java`](agents/drivers/saphana/src/main/java/com/dbx/agent/saphana/SapHanaAgent.java) |
| 186 | ✓ | [`agents/drivers/snowflake/build.gradle`](agents/drivers/snowflake/build.gradle) |
| 187 | ✓ | [`agents/drivers/snowflake/src/main/java/com/dbx/agent/snowflake/SnowflakeAgent.java`](agents/drivers/snowflake/src/main/java/com/dbx/agent/snowflake/SnowflakeAgent.java) |
| 188 | ✓ | [`agents/drivers/snowflake/src/test/java/com/dbx/agent/snowflake/SnowflakeAgentMetadataTest.java`](agents/drivers/snowflake/src/test/java/com/dbx/agent/snowflake/SnowflakeAgentMetadataTest.java) |
| 189 | ✓ | [`agents/drivers/snowflake/src/test/java/com/dbx/agent/snowflake/SnowflakeAgentTest.java`](agents/drivers/snowflake/src/test/java/com/dbx/agent/snowflake/SnowflakeAgentTest.java) |
| 190 | ✓ | [`agents/drivers/spark/build.gradle`](agents/drivers/spark/build.gradle) |
| 191 | ✓ | [`agents/drivers/spark/src/main/java/com/dbx/agent/spark/SparkAgent.java`](agents/drivers/spark/src/main/java/com/dbx/agent/spark/SparkAgent.java) |
| 192 | ✓ | [`agents/drivers/sqlserver-legacy/build.gradle`](agents/drivers/sqlserver-legacy/build.gradle) |
| 193 | ✓ | [`agents/drivers/sqlserver-legacy/src/main/java/com/dbx/agent/sqlserverlegacy/SqlServerLegacyAgent.java`](agents/drivers/sqlserver-legacy/src/main/java/com/dbx/agent/sqlserverlegacy/SqlServerLegacyAgent.java) |
| 194 | ✓ | [`agents/drivers/sqlserver-legacy/src/test/java/com/dbx/agent/sqlserverlegacy/SqlServerLegacyAgentTest.java`](agents/drivers/sqlserver-legacy/src/test/java/com/dbx/agent/sqlserverlegacy/SqlServerLegacyAgentTest.java) |
| 195 | ✓ | [`agents/drivers/sundb/build.gradle`](agents/drivers/sundb/build.gradle) |
| 196 | ✓ | [`agents/drivers/sundb/src/main/java/com/dbx/agent/sundb/SundbAgent.java`](agents/drivers/sundb/src/main/java/com/dbx/agent/sundb/SundbAgent.java) |
| 197 | ✓ | [`agents/drivers/sundb/src/test/java/com/dbx/agent/sundb/SundbAgentMetadataTest.java`](agents/drivers/sundb/src/test/java/com/dbx/agent/sundb/SundbAgentMetadataTest.java) |
| 198 | ✓ | [`agents/drivers/sundb/src/test/java/com/dbx/agent/sundb/SundbAgentTest.java`](agents/drivers/sundb/src/test/java/com/dbx/agent/sundb/SundbAgentTest.java) |
| 199 | ✓ | [`agents/drivers/tdengine/build.gradle`](agents/drivers/tdengine/build.gradle) |
| 200 | ✓ | [`agents/drivers/tdengine/src/main/java/com/dbx/agent/tdengine/TDengineAgent.java`](agents/drivers/tdengine/src/main/java/com/dbx/agent/tdengine/TDengineAgent.java) |
| 201 | ✓ | [`agents/drivers/tdengine/src/test/java/com/dbx/agent/tdengine/TDengineAgentPagingTest.java`](agents/drivers/tdengine/src/test/java/com/dbx/agent/tdengine/TDengineAgentPagingTest.java) |
| 202 | ✓ | [`agents/drivers/tdengine/src/test/java/com/dbx/agent/tdengine/TDengineAgentTest.java`](agents/drivers/tdengine/src/test/java/com/dbx/agent/tdengine/TDengineAgentTest.java) |
| 203 | ✓ | [`agents/drivers/teradata/build.gradle`](agents/drivers/teradata/build.gradle) |
| 204 | ✓ | [`agents/drivers/teradata/src/main/java/com/dbx/agent/teradata/TeradataAgent.java`](agents/drivers/teradata/src/main/java/com/dbx/agent/teradata/TeradataAgent.java) |
| 205 | ✓ | [`agents/drivers/trino/build.gradle`](agents/drivers/trino/build.gradle) |
| 206 | ✓ | [`agents/drivers/trino/src/main/java/com/dbx/agent/trino/TrinoAgent.java`](agents/drivers/trino/src/main/java/com/dbx/agent/trino/TrinoAgent.java) |
| 207 | ✓ | [`agents/drivers/trino/src/test/java/com/dbx/agent/trino/TrinoAgentTest.java`](agents/drivers/trino/src/test/java/com/dbx/agent/trino/TrinoAgentTest.java) |
| 208 | ✓ | [`agents/drivers/vastbase/build.gradle`](agents/drivers/vastbase/build.gradle) |
| 209 | ✓ | [`agents/drivers/vastbase/libs/.gitkeep`](agents/drivers/vastbase/libs/.gitkeep) |
| 210 | ✓ | [`agents/drivers/vastbase/src/main/java/com/dbx/agent/vastbase/VastbaseAgent.java`](agents/drivers/vastbase/src/main/java/com/dbx/agent/vastbase/VastbaseAgent.java) |
| 211 | ✓ | [`agents/drivers/vastbase/src/test/java/com/dbx/agent/vastbase/VastbaseAgentTest.java`](agents/drivers/vastbase/src/test/java/com/dbx/agent/vastbase/VastbaseAgentTest.java) |
| 212 | ✓ | [`agents/drivers/vertica/build.gradle`](agents/drivers/vertica/build.gradle) |
| 213 | ✓ | [`agents/drivers/vertica/src/main/java/com/dbx/agent/vertica/VerticaAgent.java`](agents/drivers/vertica/src/main/java/com/dbx/agent/vertica/VerticaAgent.java) |
| 214 | ✓ | [`agents/drivers/xugu/go.mod`](agents/drivers/xugu/go.mod) |
| 215 | ✓ | [`agents/drivers/xugu/go.sum`](agents/drivers/xugu/go.sum) |
| 216 | ✓ | [`agents/drivers/xugu/main_test.go`](agents/drivers/xugu/main_test.go) |
| 217 | ✓ | [`agents/drivers/xugu/main.go`](agents/drivers/xugu/main.go) |
| 218 | ✓ | [`agents/drivers/xugu/README.md`](agents/drivers/xugu/README.md) |
| 219 | ✓ | [`agents/drivers/yashandb/build.gradle`](agents/drivers/yashandb/build.gradle) |
| 220 | ✓ | [`agents/drivers/yashandb/src/main/java/com/dbx/agent/yashandb/YashandbAgent.java`](agents/drivers/yashandb/src/main/java/com/dbx/agent/yashandb/YashandbAgent.java) |
| 221 | ✓ | [`agents/drivers/yashandb/src/test/java/com/dbx/agent/yashandb/YashandbAgentTest.java`](agents/drivers/yashandb/src/test/java/com/dbx/agent/yashandb/YashandbAgentTest.java) |
| 222 | ✓ | [`agents/drivers/zookeeper/build.gradle`](agents/drivers/zookeeper/build.gradle) |
| 223 | ✓ | [`agents/drivers/zookeeper/src/main/java/com/dbx/agent/zookeeper/ZooKeeperAgent.java`](agents/drivers/zookeeper/src/main/java/com/dbx/agent/zookeeper/ZooKeeperAgent.java) |
| 224 | ✓ | [`agents/drivers/zookeeper/src/test/java/com/dbx/agent/zookeeper/ZooKeeperAgentTest.java`](agents/drivers/zookeeper/src/test/java/com/dbx/agent/zookeeper/ZooKeeperAgentTest.java) |
| 225 | ✓ | [`agents/gradle/wrapper/gradle-wrapper.jar`](agents/gradle/wrapper/gradle-wrapper.jar) |
| 226 | ✓ | [`agents/gradle/wrapper/gradle-wrapper.properties`](agents/gradle/wrapper/gradle-wrapper.properties) |
| 227 | ✓ | [`agents/gradlew`](agents/gradlew) |
| 228 | ✓ | [`agents/gradlew.bat`](agents/gradlew.bat) |
| 229 | ✓ | [`agents/metadata-constraint-coverage.tsv`](agents/metadata-constraint-coverage.tsv) |
| 230 | ✓ | [`agents/README.md`](agents/README.md) |
| 231 | ✓ | [`agents/README.zh-CN.md`](agents/README.zh-CN.md) |
| 232 | ✓ | [`agents/scripts/build_driver_zips.py`](agents/scripts/build_driver_zips.py) |
| 233 | ✓ | [`agents/scripts/build_offline_zip.sh`](agents/scripts/build_offline_zip.sh) |
| 234 | ✓ | [`agents/scripts/driver_release_packages_test.py`](agents/scripts/driver_release_packages_test.py) |
| 235 | ✓ | [`agents/scripts/release.sh`](agents/scripts/release.sh) |
| 236 | ✓ | [`agents/scripts/validate_agent_jars.py`](agents/scripts/validate_agent_jars.py) |
| 237 | ✓ | [`agents/scripts/validate_agents_test.py`](agents/scripts/validate_agents_test.py) |
| 238 | ✓ | [`agents/scripts/validate_agents.py`](agents/scripts/validate_agents.py) |
| 239 | ✓ | [`agents/scripts/version_agent_artifacts.py`](agents/scripts/version_agent_artifacts.py) |
| 240 | ✓ | [`agents/settings.gradle`](agents/settings.gradle) |
| 241 | ✓ | [`agents/test-support/build.gradle`](agents/test-support/build.gradle) |
| 242 | ✓ | [`agents/test-support/src/main/java/com/dbx/agent/test/JdbcAgentFake.java`](agents/test-support/src/main/java/com/dbx/agent/test/JdbcAgentFake.java) |
| 243 | ✓ | [`agents/test-support/src/main/java/com/dbx/agent/test/JdbcConnectedAgentTest.java`](agents/test-support/src/main/java/com/dbx/agent/test/JdbcConnectedAgentTest.java) |
| 244 | ✓ | [`agents/test-support/src/main/java/com/dbx/agent/test/JdbcExecutionBehaviorTest.java`](agents/test-support/src/main/java/com/dbx/agent/test/JdbcExecutionBehaviorTest.java) |
| 245 | ✓ | [`agents/test-support/src/main/java/com/dbx/agent/test/JdbcFakeExecutionBehaviorTest.java`](agents/test-support/src/main/java/com/dbx/agent/test/JdbcFakeExecutionBehaviorTest.java) |
| 246 | ✓ | [`agents/test-support/src/main/java/com/dbx/agent/test/JdbcMetadataBehaviorTest.java`](agents/test-support/src/main/java/com/dbx/agent/test/JdbcMetadataBehaviorTest.java) |
| 247 | ✓ | [`agents/test-support/src/main/java/com/dbx/agent/test/JdbcMetadataSqlFake.java`](agents/test-support/src/main/java/com/dbx/agent/test/JdbcMetadataSqlFake.java) |
| 248 | ✓ | [`agents/test-support/src/main/java/com/dbx/agent/test/TestSupport.java`](agents/test-support/src/main/java/com/dbx/agent/test/TestSupport.java) |
| 249 | ✓ | [`agents/versions.json`](agents/versions.json) |
| 250 | ✓ | [`apps/desktop/src/components/mq/README.md`](apps/desktop/src/components/mq/README.md) |
| 251 | ✓ | [`apps/desktop/src/lib/README.md`](apps/desktop/src/lib/README.md) |
| 252 | ✓ | [`apps/desktop/src/lib/sql/semantic/README.md`](apps/desktop/src/lib/sql/semantic/README.md) |
| 253 | ✓ | [`apps/README.md`](apps/README.md) |
| 254 | ✓ | [`crates/dbx-core/src/mq/README.md`](crates/dbx-core/src/mq/README.md) |
| 255 | ✓ | [`crates/README.md`](crates/README.md) |
| 256 | ✓ | [`deploy/1panel/README.md`](deploy/1panel/README.md) |
| 257 | ✓ | [`deploy/database/etcd/3.7/init/README.md`](deploy/database/etcd/3.7/init/README.md) |
| 258 | ✓ | [`deploy/database/kafka/4.3/init/README.md`](deploy/database/kafka/4.3/init/README.md) |
| 259 | ✓ | [`deploy/database/nacos/2.5/init/README.md`](deploy/database/nacos/2.5/init/README.md) |
| 260 | ✓ | [`deploy/database/nacos/3.2/init/README.md`](deploy/database/nacos/3.2/init/README.md) |
| 261 | ✓ | [`deploy/database/pulsar/4.2/init/README.md`](deploy/database/pulsar/4.2/init/README.md) |
| 262 | ✓ | [`deploy/database/qdrant/1.8/init/README.md`](deploy/database/qdrant/1.8/init/README.md) |
| 263 | ✓ | [`deploy/database/redis/3.0.7/init/README.md`](deploy/database/redis/3.0.7/init/README.md) |
| 264 | ✓ | [`deploy/database/redis/7.4/init/README.md`](deploy/database/redis/7.4/init/README.md) |
| 265 | ✓ | [`deploy/database/zookeeper/3.9/init/README.md`](deploy/database/zookeeper/3.9/init/README.md) |
| 266 | ✓ | [`deploy/dockerhub/README.md`](deploy/dockerhub/README.md) |
| 267 | ✓ | [`docs/public/llms.txt`](docs/public/llms.txt) |
| 268 | ✓ | [`examples/README.md`](examples/README.md) |
| 269 | ✓ | [`packages/mcp-darwin-arm64/README.md`](packages/mcp-darwin-arm64/README.md) |
| 270 | ✓ | [`packages/mcp-darwin-x64/README.md`](packages/mcp-darwin-x64/README.md) |
| 271 | ✓ | [`packages/mcp-linux-arm64-gnu/README.md`](packages/mcp-linux-arm64-gnu/README.md) |
| 272 | ✓ | [`packages/mcp-linux-x64-gnu/README.md`](packages/mcp-linux-x64-gnu/README.md) |
| 273 | ✓ | [`packages/mcp-win32-arm64/README.md`](packages/mcp-win32-arm64/README.md) |
| 274 | ✓ | [`packages/mcp-win32-x64/README.md`](packages/mcp-win32-x64/README.md) |
| 275 | ✓ | [`plugins/jdbc/README.md`](plugins/jdbc/README.md) |
| 276 | ✓ | [`plugins/README.md`](plugins/README.md) |
| 277 | ✓ | [`skills/dbx/SKILL.md`](skills/dbx/SKILL.md) |
| 278 | → | [`CONTRIBUTING.md`](CONTRIBUTING.md) |
| 279 | → | [`CONTRIBUTING.zh-CN.md`](CONTRIBUTING.zh-CN.md) |
| 280 | → | [`deploy/database/README.md`](deploy/database/README.md) |
| 281 | → | [`deploy/database/README.zh-CN.md`](deploy/database/README.zh-CN.md) |
| 282 | → | [`packages/cli/README.md`](packages/cli/README.md) |
| 283 | → | [`packages/mcp-server/README.md`](packages/mcp-server/README.md) |
| 284 | → | [`README.md`](README.md) |
| 285 | → | [`README.zh-CN.md`](README.zh-CN.md) |

---

*Generated by mirror — do not edit manually*