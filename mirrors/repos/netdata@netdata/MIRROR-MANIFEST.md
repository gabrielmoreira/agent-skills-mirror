---
repo: netdata/netdata
repoUrl: https://github.com/netdata/netdata.git
refType: branch
ref: master
---

# Mirror Manifest

Mirror of `netdata/netdata` — 26 default patterns, 1 followed patterns, 345 file(s) materialized.

## Metadata

| Field         | Value |
|---------------|-------|
| Repo          | `netdata/netdata` |
| Ref Type      | `branch` |
| Ref           | `master` |
| Default pats  | 26 |
| Followed pats | 1 |
| Files         | 345 |

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

- `README.md`

## File Index

Legend: **✓** = default pattern · **→** = followed via markdown

| # | S | File |
|---|---|------|
| 1 | ✓ | [`.agents/skills/coverity-audit/scripts/_lib.sh`](.agents/skills/coverity-audit/scripts/_lib.sh) |
| 2 | ✓ | [`.agents/skills/coverity-audit/scripts/fetch-details.sh`](.agents/skills/coverity-audit/scripts/fetch-details.sh) |
| 3 | ✓ | [`.agents/skills/coverity-audit/scripts/fetch-table.sh`](.agents/skills/coverity-audit/scripts/fetch-table.sh) |
| 4 | ✓ | [`.agents/skills/coverity-audit/scripts/finalize-defect.sh`](.agents/skills/coverity-audit/scripts/finalize-defect.sh) |
| 5 | ✓ | [`.agents/skills/coverity-audit/scripts/keepalive.sh`](.agents/skills/coverity-audit/scripts/keepalive.sh) |
| 6 | ✓ | [`.agents/skills/coverity-audit/scripts/prepare-defect.sh`](.agents/skills/coverity-audit/scripts/prepare-defect.sh) |
| 7 | ✓ | [`.agents/skills/coverity-audit/scripts/resolve-cid-to-diid.sh`](.agents/skills/coverity-audit/scripts/resolve-cid-to-diid.sh) |
| 8 | ✓ | [`.agents/skills/coverity-audit/scripts/update-triage.sh`](.agents/skills/coverity-audit/scripts/update-triage.sh) |
| 9 | ✓ | [`.agents/skills/coverity-audit/SKILL.md`](.agents/skills/coverity-audit/SKILL.md) |
| 10 | ✓ | [`.agents/skills/graphql-audit/scripts/_lib.sh`](.agents/skills/graphql-audit/scripts/_lib.sh) |
| 11 | ✓ | [`.agents/skills/graphql-audit/scripts/codeql-dismiss.sh`](.agents/skills/graphql-audit/scripts/codeql-dismiss.sh) |
| 12 | ✓ | [`.agents/skills/graphql-audit/scripts/codeql-list.sh`](.agents/skills/graphql-audit/scripts/codeql-list.sh) |
| 13 | ✓ | [`.agents/skills/graphql-audit/SKILL.md`](.agents/skills/graphql-audit/SKILL.md) |
| 14 | ✓ | [`.agents/skills/pr-reviews/scripts/_lib.sh`](.agents/skills/pr-reviews/scripts/_lib.sh) |
| 15 | ✓ | [`.agents/skills/pr-reviews/scripts/ci-status.sh`](.agents/skills/pr-reviews/scripts/ci-status.sh) |
| 16 | ✓ | [`.agents/skills/pr-reviews/scripts/fetch-all.sh`](.agents/skills/pr-reviews/scripts/fetch-all.sh) |
| 17 | ✓ | [`.agents/skills/pr-reviews/scripts/fetch-sonar-findings.sh`](.agents/skills/pr-reviews/scripts/fetch-sonar-findings.sh) |
| 18 | ✓ | [`.agents/skills/pr-reviews/scripts/list-open-threads.sh`](.agents/skills/pr-reviews/scripts/list-open-threads.sh) |
| 19 | ✓ | [`.agents/skills/pr-reviews/scripts/reply-thread.sh`](.agents/skills/pr-reviews/scripts/reply-thread.sh) |
| 20 | ✓ | [`.agents/skills/pr-reviews/scripts/resolve-thread.sh`](.agents/skills/pr-reviews/scripts/resolve-thread.sh) |
| 21 | ✓ | [`.agents/skills/pr-reviews/scripts/trigger-copilot.sh`](.agents/skills/pr-reviews/scripts/trigger-copilot.sh) |
| 22 | ✓ | [`.agents/skills/pr-reviews/scripts/trigger-cubic.sh`](.agents/skills/pr-reviews/scripts/trigger-cubic.sh) |
| 23 | ✓ | [`.agents/skills/pr-reviews/scripts/wait-for-activity.sh`](.agents/skills/pr-reviews/scripts/wait-for-activity.sh) |
| 24 | ✓ | [`.agents/skills/pr-reviews/SKILL.md`](.agents/skills/pr-reviews/SKILL.md) |
| 25 | ✓ | [`.agents/skills/project-writing-collectors/SKILL.md`](.agents/skills/project-writing-collectors/SKILL.md) |
| 26 | ✓ | [`.agents/skills/sonarqube-audit/scripts/_lib.sh`](.agents/skills/sonarqube-audit/scripts/_lib.sh) |
| 27 | ✓ | [`.agents/skills/sonarqube-audit/scripts/sonar-mark.sh`](.agents/skills/sonarqube-audit/scripts/sonar-mark.sh) |
| 28 | ✓ | [`.agents/skills/sonarqube-audit/scripts/sonar-search.sh`](.agents/skills/sonarqube-audit/scripts/sonar-search.sh) |
| 29 | ✓ | [`.agents/skills/sonarqube-audit/SKILL.md`](.agents/skills/sonarqube-audit/SKILL.md) |
| 30 | ✓ | [`.agents/sow/audit.sh`](.agents/sow/audit.sh) |
| 31 | ✓ | [`.agents/sow/current/.gitkeep`](.agents/sow/current/.gitkeep) |
| 32 | ✓ | [`.agents/sow/done/.gitkeep`](.agents/sow/done/.gitkeep) |
| 33 | ✓ | [`.agents/sow/done/SOW-0001-20260502-project-writing-collectors-skill.md`](.agents/sow/done/SOW-0001-20260502-project-writing-collectors-skill.md) |
| 34 | ✓ | [`.agents/sow/pending/.gitkeep`](.agents/sow/pending/.gitkeep) |
| 35 | ✓ | [`.agents/sow/SOW.template.md`](.agents/sow/SOW.template.md) |
| 36 | ✓ | [`.agents/sow/specs/.gitkeep`](.agents/sow/specs/.gitkeep) |
| 37 | ✓ | [`AGENTS.md`](AGENTS.md) |
| 38 | ✓ | [`CLAUDE.md`](CLAUDE.md) |
| 39 | ✓ | [`docs/.map/README.md`](docs/.map/README.md) |
| 40 | ✓ | [`docs/alerts-and-notifications/creating-alerts-with-netdata-alerts-configuration-manager.md`](docs/alerts-and-notifications/creating-alerts-with-netdata-alerts-configuration-manager.md) |
| 41 | ✓ | [`docs/alerts-and-notifications/notifications/centralized-cloud-notifications/centralized-cloud-notifications-reference.md`](docs/alerts-and-notifications/notifications/centralized-cloud-notifications/centralized-cloud-notifications-reference.md) |
| 42 | ✓ | [`docs/alerts-and-notifications/notifications/centralized-cloud-notifications/manage-alert-notification-silencing-rules.md`](docs/alerts-and-notifications/notifications/centralized-cloud-notifications/manage-alert-notification-silencing-rules.md) |
| 43 | ✓ | [`docs/alerts-and-notifications/notifications/centralized-cloud-notifications/manage-notification-methods.md`](docs/alerts-and-notifications/notifications/centralized-cloud-notifications/manage-notification-methods.md) |
| 44 | ✓ | [`docs/alerts-and-notifications/notifications/README.md`](docs/alerts-and-notifications/notifications/README.md) |
| 45 | ✓ | [`docs/category-overview-pages/machine-learning-and-assisted-troubleshooting.md`](docs/category-overview-pages/machine-learning-and-assisted-troubleshooting.md) |
| 46 | ✓ | [`docs/dashboards-and-charts/alerts-tab.md`](docs/dashboards-and-charts/alerts-tab.md) |
| 47 | ✓ | [`docs/dashboards-and-charts/anomaly-advisor-tab.md`](docs/dashboards-and-charts/anomaly-advisor-tab.md) |
| 48 | ✓ | [`docs/dashboards-and-charts/dashboards-tab.md`](docs/dashboards-and-charts/dashboards-tab.md) |
| 49 | ✓ | [`docs/dashboards-and-charts/events-feed.md`](docs/dashboards-and-charts/events-feed.md) |
| 50 | ✓ | [`docs/dashboards-and-charts/home-tab.md`](docs/dashboards-and-charts/home-tab.md) |
| 51 | ✓ | [`docs/dashboards-and-charts/kubernetes-tab.md`](docs/dashboards-and-charts/kubernetes-tab.md) |
| 52 | ✓ | [`docs/dashboards-and-charts/live-tab.md`](docs/dashboards-and-charts/live-tab.md) |
| 53 | ✓ | [`docs/dashboards-and-charts/logs-tab.md`](docs/dashboards-and-charts/logs-tab.md) |
| 54 | ✓ | [`docs/dashboards-and-charts/metrics-tab-and-single-node-tabs.md`](docs/dashboards-and-charts/metrics-tab-and-single-node-tabs.md) |
| 55 | ✓ | [`docs/dashboards-and-charts/netdata-charts.md`](docs/dashboards-and-charts/netdata-charts.md) |
| 56 | ✓ | [`docs/dashboards-and-charts/node-filter.md`](docs/dashboards-and-charts/node-filter.md) |
| 57 | ✓ | [`docs/dashboards-and-charts/nodes-tab.md`](docs/dashboards-and-charts/nodes-tab.md) |
| 58 | ✓ | [`docs/dashboards-and-charts/README.md`](docs/dashboards-and-charts/README.md) |
| 59 | ✓ | [`docs/deployment-guides/deployment-with-centralization-points.md`](docs/deployment-guides/deployment-with-centralization-points.md) |
| 60 | ✓ | [`docs/deployment-guides/README.md`](docs/deployment-guides/README.md) |
| 61 | ✓ | [`docs/deployment-guides/standalone-deployment.md`](docs/deployment-guides/standalone-deployment.md) |
| 62 | ✓ | [`docs/developer-and-contributor-corner/collect-apache-nginx-web-logs.md`](docs/developer-and-contributor-corner/collect-apache-nginx-web-logs.md) |
| 63 | ✓ | [`docs/developer-and-contributor-corner/monitor-debug-applications-ebpf.md`](docs/developer-and-contributor-corner/monitor-debug-applications-ebpf.md) |
| 64 | ✓ | [`docs/developer-and-contributor-corner/README.md`](docs/developer-and-contributor-corner/README.md) |
| 65 | ✓ | [`docs/exporting-metrics/enable-an-exporting-connector.md`](docs/exporting-metrics/enable-an-exporting-connector.md) |
| 66 | ✓ | [`docs/exporting-metrics/README.md`](docs/exporting-metrics/README.md) |
| 67 | ✓ | [`docs/learn/node-identities.md`](docs/learn/node-identities.md) |
| 68 | ✓ | [`docs/learn/remove-node.md`](docs/learn/remove-node.md) |
| 69 | ✓ | [`docs/learn/vm-templates.md`](docs/learn/vm-templates.md) |
| 70 | ✓ | [`docs/metric-correlations.md`](docs/metric-correlations.md) |
| 71 | ✓ | [`docs/ml-ai/ai-insights.md`](docs/ml-ai/ai-insights.md) |
| 72 | ✓ | [`docs/ml-ai/anomaly-advisor.md`](docs/ml-ai/anomaly-advisor.md) |
| 73 | ✓ | [`docs/ml-ai/ml-anomaly-detection/ml-accuracy.md`](docs/ml-ai/ml-anomaly-detection/ml-accuracy.md) |
| 74 | ✓ | [`docs/ml-ai/ml-anomaly-detection/ml-anomaly-detection.md`](docs/ml-ai/ml-anomaly-detection/ml-anomaly-detection.md) |
| 75 | ✓ | [`docs/netdata-agent/configuration/anonymous-telemetry-events.md`](docs/netdata-agent/configuration/anonymous-telemetry-events.md) |
| 76 | ✓ | [`docs/netdata-agent/configuration/dynamic-configuration.md`](docs/netdata-agent/configuration/dynamic-configuration.md) |
| 77 | ✓ | [`docs/netdata-agent/configuration/organize-systems-metrics-and-alerts.md`](docs/netdata-agent/configuration/organize-systems-metrics-and-alerts.md) |
| 78 | ✓ | [`docs/netdata-agent/configuration/README.md`](docs/netdata-agent/configuration/README.md) |
| 79 | ✓ | [`docs/netdata-agent/configuration/running-the-netdata-agent-behind-a-reverse-proxy/README.md`](docs/netdata-agent/configuration/running-the-netdata-agent-behind-a-reverse-proxy/README.md) |
| 80 | ✓ | [`docs/netdata-agent/configuration/running-the-netdata-agent-behind-a-reverse-proxy/Running-behind-apache.md`](docs/netdata-agent/configuration/running-the-netdata-agent-behind-a-reverse-proxy/Running-behind-apache.md) |
| 81 | ✓ | [`docs/netdata-agent/configuration/running-the-netdata-agent-behind-a-reverse-proxy/Running-behind-caddy.md`](docs/netdata-agent/configuration/running-the-netdata-agent-behind-a-reverse-proxy/Running-behind-caddy.md) |
| 82 | ✓ | [`docs/netdata-agent/configuration/running-the-netdata-agent-behind-a-reverse-proxy/Running-behind-haproxy.md`](docs/netdata-agent/configuration/running-the-netdata-agent-behind-a-reverse-proxy/Running-behind-haproxy.md) |
| 83 | ✓ | [`docs/netdata-agent/configuration/running-the-netdata-agent-behind-a-reverse-proxy/Running-behind-lighttpd.md`](docs/netdata-agent/configuration/running-the-netdata-agent-behind-a-reverse-proxy/Running-behind-lighttpd.md) |
| 84 | ✓ | [`docs/netdata-agent/configuration/running-the-netdata-agent-behind-a-reverse-proxy/Running-behind-nginx.md`](docs/netdata-agent/configuration/running-the-netdata-agent-behind-a-reverse-proxy/Running-behind-nginx.md) |
| 85 | ✓ | [`docs/netdata-agent/configuration/secure-your-netdata-agent-with-bearer-token.md`](docs/netdata-agent/configuration/secure-your-netdata-agent-with-bearer-token.md) |
| 86 | ✓ | [`docs/netdata-agent/sizing-netdata-agents/README.md`](docs/netdata-agent/sizing-netdata-agents/README.md) |
| 87 | ✓ | [`docs/netdata-agent/start-stop-restart.md`](docs/netdata-agent/start-stop-restart.md) |
| 88 | ✓ | [`docs/netdata-ai/alerts-automation/alerts-automation.md`](docs/netdata-ai/alerts-automation/alerts-automation.md) |
| 89 | ✓ | [`docs/netdata-ai/conversations.md`](docs/netdata-ai/conversations.md) |
| 90 | ✓ | [`docs/netdata-ai/insights/anomaly-analysis.md`](docs/netdata-ai/insights/anomaly-analysis.md) |
| 91 | ✓ | [`docs/netdata-ai/insights/capacity-planning.md`](docs/netdata-ai/insights/capacity-planning.md) |
| 92 | ✓ | [`docs/netdata-ai/insights/infrastructure-summary.md`](docs/netdata-ai/insights/infrastructure-summary.md) |
| 93 | ✓ | [`docs/netdata-ai/insights/performance-optimization.md`](docs/netdata-ai/insights/performance-optimization.md) |
| 94 | ✓ | [`docs/netdata-ai/insights/scheduled-reports.md`](docs/netdata-ai/insights/scheduled-reports.md) |
| 95 | ✓ | [`docs/netdata-ai/investigations/custom-investigations.md`](docs/netdata-ai/investigations/custom-investigations.md) |
| 96 | ✓ | [`docs/netdata-ai/investigations/index.md`](docs/netdata-ai/investigations/index.md) |
| 97 | ✓ | [`docs/netdata-ai/investigations/scheduled-investigations.md`](docs/netdata-ai/investigations/scheduled-investigations.md) |
| 98 | ✓ | [`docs/netdata-ai/mcp/ai-chat-netdata.md`](docs/netdata-ai/mcp/ai-chat-netdata.md) |
| 99 | ✓ | [`docs/netdata-ai/mcp/mcp-clients/ai-devops-copilot.md`](docs/netdata-ai/mcp/mcp-clients/ai-devops-copilot.md) |
| 100 | ✓ | [`docs/netdata-ai/mcp/mcp-clients/claude-code.md`](docs/netdata-ai/mcp/mcp-clients/claude-code.md) |
| 101 | ✓ | [`docs/netdata-ai/mcp/mcp-clients/claude-desktop.md`](docs/netdata-ai/mcp/mcp-clients/claude-desktop.md) |
| 102 | ✓ | [`docs/netdata-ai/mcp/mcp-clients/codex-cli.md`](docs/netdata-ai/mcp/mcp-clients/codex-cli.md) |
| 103 | ✓ | [`docs/netdata-ai/mcp/mcp-clients/crush.md`](docs/netdata-ai/mcp/mcp-clients/crush.md) |
| 104 | ✓ | [`docs/netdata-ai/mcp/mcp-clients/cursor.md`](docs/netdata-ai/mcp/mcp-clients/cursor.md) |
| 105 | ✓ | [`docs/netdata-ai/mcp/mcp-clients/gemini-cli.md`](docs/netdata-ai/mcp/mcp-clients/gemini-cli.md) |
| 106 | ✓ | [`docs/netdata-ai/mcp/mcp-clients/jetbrains-ides.md`](docs/netdata-ai/mcp/mcp-clients/jetbrains-ides.md) |
| 107 | ✓ | [`docs/netdata-ai/mcp/mcp-clients/opencode.md`](docs/netdata-ai/mcp/mcp-clients/opencode.md) |
| 108 | ✓ | [`docs/netdata-ai/mcp/mcp-clients/vs-code.md`](docs/netdata-ai/mcp/mcp-clients/vs-code.md) |
| 109 | ✓ | [`docs/netdata-ai/mcp/README.md`](docs/netdata-ai/mcp/README.md) |
| 110 | ✓ | [`docs/netdata-ai/troubleshooting/index.md`](docs/netdata-ai/troubleshooting/index.md) |
| 111 | ✓ | [`docs/netdata-cloud/authentication-and-authorization/api-tokens.md`](docs/netdata-cloud/authentication-and-authorization/api-tokens.md) |
| 112 | ✓ | [`docs/netdata-cloud/authentication-and-authorization/README.md`](docs/netdata-cloud/authentication-and-authorization/README.md) |
| 113 | ✓ | [`docs/netdata-cloud/authentication-and-authorization/role-based-access-model.md`](docs/netdata-cloud/authentication-and-authorization/role-based-access-model.md) |
| 114 | ✓ | [`docs/netdata-cloud/node-states-and-transitions.md`](docs/netdata-cloud/node-states-and-transitions.md) |
| 115 | ✓ | [`docs/netdata-cloud/organize-your-infrastructure-invite-your-team.md`](docs/netdata-cloud/organize-your-infrastructure-invite-your-team.md) |
| 116 | ✓ | [`docs/netdata-cloud/README.md`](docs/netdata-cloud/README.md) |
| 117 | ✓ | [`docs/netdata-cloud/view-plan-and-billing.md`](docs/netdata-cloud/view-plan-and-billing.md) |
| 118 | ✓ | [`docs/nodes-ephemerality.md`](docs/nodes-ephemerality.md) |
| 119 | ✓ | [`docs/observability-centralization-points/best-practices.md`](docs/observability-centralization-points/best-practices.md) |
| 120 | ✓ | [`docs/observability-centralization-points/logs-centralization-points-with-systemd-journald/passive-journal-centralization-without-encryption.md`](docs/observability-centralization-points/logs-centralization-points-with-systemd-journald/passive-journal-centralization-without-encryption.md) |
| 121 | ✓ | [`docs/observability-centralization-points/logs-centralization-points-with-systemd-journald/README.md`](docs/observability-centralization-points/logs-centralization-points-with-systemd-journald/README.md) |
| 122 | ✓ | [`docs/observability-centralization-points/metrics-centralization-points/configuration.md`](docs/observability-centralization-points/metrics-centralization-points/configuration.md) |
| 123 | ✓ | [`docs/observability-centralization-points/metrics-centralization-points/README.md`](docs/observability-centralization-points/metrics-centralization-points/README.md) |
| 124 | ✓ | [`docs/security-and-privacy-design/README.md`](docs/security-and-privacy-design/README.md) |
| 125 | ✓ | [`docs/top-monitoring-netdata-functions.md`](docs/top-monitoring-netdata-functions.md) |
| 126 | ✓ | [`docs/troubleshooting/troubleshoot.md`](docs/troubleshooting/troubleshoot.md) |
| 127 | ✓ | [`GEMINI.md`](GEMINI.md) |
| 128 | ✓ | [`integrations/cloud-notifications/integrations/netdata_mobile_app.md`](integrations/cloud-notifications/integrations/netdata_mobile_app.md) |
| 129 | ✓ | [`integrations/README.md`](integrations/README.md) |
| 130 | ✓ | [`integrations/templates/README.md`](integrations/templates/README.md) |
| 131 | ✓ | [`packaging/dag/README.md`](packaging/dag/README.md) |
| 132 | ✓ | [`packaging/docker/README.md`](packaging/docker/README.md) |
| 133 | ✓ | [`packaging/installer/methods/ansible.md`](packaging/installer/methods/ansible.md) |
| 134 | ✓ | [`packaging/installer/methods/aws.md`](packaging/installer/methods/aws.md) |
| 135 | ✓ | [`packaging/installer/methods/azure.md`](packaging/installer/methods/azure.md) |
| 136 | ✓ | [`packaging/installer/methods/freebsd.md`](packaging/installer/methods/freebsd.md) |
| 137 | ✓ | [`packaging/installer/methods/gcp.md`](packaging/installer/methods/gcp.md) |
| 138 | ✓ | [`packaging/installer/methods/kickstart.md`](packaging/installer/methods/kickstart.md) |
| 139 | ✓ | [`packaging/installer/methods/kubernetes.md`](packaging/installer/methods/kubernetes.md) |
| 140 | ✓ | [`packaging/installer/methods/macos.md`](packaging/installer/methods/macos.md) |
| 141 | ✓ | [`packaging/installer/methods/manual.md`](packaging/installer/methods/manual.md) |
| 142 | ✓ | [`packaging/installer/methods/offline.md`](packaging/installer/methods/offline.md) |
| 143 | ✓ | [`packaging/installer/methods/packages.md`](packaging/installer/methods/packages.md) |
| 144 | ✓ | [`packaging/installer/methods/pfsense.md`](packaging/installer/methods/pfsense.md) |
| 145 | ✓ | [`packaging/installer/methods/synology.md`](packaging/installer/methods/synology.md) |
| 146 | ✓ | [`packaging/installer/README.md`](packaging/installer/README.md) |
| 147 | ✓ | [`packaging/installer/UNINSTALL.md`](packaging/installer/UNINSTALL.md) |
| 148 | ✓ | [`packaging/installer/UPDATE.md`](packaging/installer/UPDATE.md) |
| 149 | ✓ | [`packaging/maintainers/README.md`](packaging/maintainers/README.md) |
| 150 | ✓ | [`packaging/makeself/README.md`](packaging/makeself/README.md) |
| 151 | ✓ | [`packaging/PLATFORM_SUPPORT.md`](packaging/PLATFORM_SUPPORT.md) |
| 152 | ✓ | [`packaging/windows/WINDOWS_INSTALLER.md`](packaging/windows/WINDOWS_INSTALLER.md) |
| 153 | ✓ | [`src/aclk/mqtt_websockets/README.md`](src/aclk/mqtt_websockets/README.md) |
| 154 | ✓ | [`src/aclk/README.md`](src/aclk/README.md) |
| 155 | ✓ | [`src/claim/README.md`](src/claim/README.md) |
| 156 | ✓ | [`src/cli/README.md`](src/cli/README.md) |
| 157 | ✓ | [`src/collectors/apps.plugin/README.md`](src/collectors/apps.plugin/README.md) |
| 158 | ✓ | [`src/collectors/cgroups.plugin/README.md`](src/collectors/cgroups.plugin/README.md) |
| 159 | ✓ | [`src/collectors/charts.d.plugin/example/README.md`](src/collectors/charts.d.plugin/example/README.md) |
| 160 | ✓ | [`src/collectors/charts.d.plugin/README.md`](src/collectors/charts.d.plugin/README.md) |
| 161 | ✓ | [`src/collectors/COLLECTORS.md`](src/collectors/COLLECTORS.md) |
| 162 | ✓ | [`src/collectors/debugfs.plugin/README.md`](src/collectors/debugfs.plugin/README.md) |
| 163 | ✓ | [`src/collectors/ebpf.plugin/libbpf_api/README.md`](src/collectors/ebpf.plugin/libbpf_api/README.md) |
| 164 | ✓ | [`src/collectors/ebpf.plugin/README.md`](src/collectors/ebpf.plugin/README.md) |
| 165 | ✓ | [`src/collectors/freebsd.plugin/README.md`](src/collectors/freebsd.plugin/README.md) |
| 166 | ✓ | [`src/collectors/log2journal/README.md`](src/collectors/log2journal/README.md) |
| 167 | ✓ | [`src/collectors/log2journal/tests.d/README.md`](src/collectors/log2journal/tests.d/README.md) |
| 168 | ✓ | [`src/collectors/proc.plugin/README.md`](src/collectors/proc.plugin/README.md) |
| 169 | ✓ | [`src/collectors/profile.plugin/README.md`](src/collectors/profile.plugin/README.md) |
| 170 | ✓ | [`src/collectors/python.d.plugin/haproxy/README.md`](src/collectors/python.d.plugin/haproxy/README.md) |
| 171 | ✓ | [`src/collectors/python.d.plugin/README.md`](src/collectors/python.d.plugin/README.md) |
| 172 | ✓ | [`src/collectors/python.d.plugin/traefik/README.md`](src/collectors/python.d.plugin/traefik/README.md) |
| 173 | ✓ | [`src/collectors/README.md`](src/collectors/README.md) |
| 174 | ✓ | [`src/collectors/REFERENCE.md`](src/collectors/REFERENCE.md) |
| 175 | ✓ | [`src/collectors/statsd.plugin/README.md`](src/collectors/statsd.plugin/README.md) |
| 176 | ✓ | [`src/collectors/systemd-journal.plugin/README.md`](src/collectors/systemd-journal.plugin/README.md) |
| 177 | ✓ | [`src/collectors/windows-events.plugin/README.md`](src/collectors/windows-events.plugin/README.md) |
| 178 | ✓ | [`src/collectors/windows.plugin/README.md`](src/collectors/windows.plugin/README.md) |
| 179 | ✓ | [`src/crates/journal-registry/README.md`](src/crates/journal-registry/README.md) |
| 180 | ✓ | [`src/crates/netdata-log-viewer/otel-signal-viewer-plugin/README.md`](src/crates/netdata-log-viewer/otel-signal-viewer-plugin/README.md) |
| 181 | ✓ | [`src/crates/netdata-log-viewer/README.md`](src/crates/netdata-log-viewer/README.md) |
| 182 | ✓ | [`src/crates/netflow-plugin/README.md`](src/crates/netflow-plugin/README.md) |
| 183 | ✓ | [`src/crates/netflow-plugin/src/routing/proto/README.md`](src/crates/netflow-plugin/src/routing/proto/README.md) |
| 184 | ✓ | [`src/daemon/config/README.md`](src/daemon/config/README.md) |
| 185 | ✓ | [`src/daemon/dyncfg/README.md`](src/daemon/dyncfg/README.md) |
| 186 | ✓ | [`src/daemon/README.md`](src/daemon/README.md) |
| 187 | ✓ | [`src/database/CONFIGURATION.md`](src/database/CONFIGURATION.md) |
| 188 | ✓ | [`src/database/contexts/README.md`](src/database/contexts/README.md) |
| 189 | ✓ | [`src/database/engine/README.md`](src/database/engine/README.md) |
| 190 | ✓ | [`src/database/ram/README.md`](src/database/ram/README.md) |
| 191 | ✓ | [`src/database/README.md`](src/database/README.md) |
| 192 | ✓ | [`src/database/sqlite/vendored/README.md`](src/database/sqlite/vendored/README.md) |
| 193 | ✓ | [`src/exporting/prometheus/README.md`](src/exporting/prometheus/README.md) |
| 194 | ✓ | [`src/exporting/README.md`](src/exporting/README.md) |
| 195 | ✓ | [`src/exporting/TIMESCALE.md`](src/exporting/TIMESCALE.md) |
| 196 | ✓ | [`src/go/AGENTS.md`](src/go/AGENTS.md) |
| 197 | ✓ | [`src/go/BEST-PRACTICES.md`](src/go/BEST-PRACTICES.md) |
| 198 | ✓ | [`src/go/CLAUDE.md`](src/go/CLAUDE.md) |
| 199 | ✓ | [`src/go/GEMINI.md`](src/go/GEMINI.md) |
| 200 | ✓ | [`src/go/pkg/matcher/README.md`](src/go/pkg/matcher/README.md) |
| 201 | ✓ | [`src/go/pkg/metrix/README.md`](src/go/pkg/metrix/README.md) |
| 202 | ✓ | [`src/go/pkg/prometheus/selector/README.md`](src/go/pkg/prometheus/selector/README.md) |
| 203 | ✓ | [`src/go/pkg/topology/engine/parity/README.md`](src/go/pkg/topology/engine/parity/README.md) |
| 204 | ✓ | [`src/go/plugin/agent/README.md`](src/go/plugin/agent/README.md) |
| 205 | ✓ | [`src/go/plugin/agent/runtimechartemit/README.md`](src/go/plugin/agent/runtimechartemit/README.md) |
| 206 | ✓ | [`src/go/plugin/framework/chartengine/README.md`](src/go/plugin/framework/chartengine/README.md) |
| 207 | ✓ | [`src/go/plugin/framework/charttpl/README.md`](src/go/plugin/framework/charttpl/README.md) |
| 208 | ✓ | [`src/go/plugin/framework/functions/README.md`](src/go/plugin/framework/functions/README.md) |
| 209 | ✓ | [`src/go/plugin/go.d/collector/bind/README.md`](src/go/plugin/go.d/collector/bind/README.md) |
| 210 | ✓ | [`src/go/plugin/go.d/collector/sensors/lmsensors/README.md`](src/go/plugin/go.d/collector/sensors/lmsensors/README.md) |
| 211 | ✓ | [`src/go/plugin/go.d/config/go.d/snmp.profiles/default/README.md`](src/go/plugin/go.d/config/go.d/snmp.profiles/default/README.md) |
| 212 | ✓ | [`src/go/plugin/go.d/pkg/iprange/README.md`](src/go/plugin/go.d/pkg/iprange/README.md) |
| 213 | ✓ | [`src/go/plugin/go.d/pkg/README.md`](src/go/plugin/go.d/pkg/README.md) |
| 214 | ✓ | [`src/go/plugin/go.d/README.md`](src/go/plugin/go.d/README.md) |
| 215 | ✓ | [`src/go/plugin/ibm.d/AGENTS.md`](src/go/plugin/ibm.d/AGENTS.md) |
| 216 | ✓ | [`src/go/plugin/ibm.d/CLAUDE.md`](src/go/plugin/ibm.d/CLAUDE.md) |
| 217 | ✓ | [`src/go/plugin/ibm.d/docgen/README.md`](src/go/plugin/ibm.d/docgen/README.md) |
| 218 | ✓ | [`src/go/plugin/ibm.d/framework/README.md`](src/go/plugin/ibm.d/framework/README.md) |
| 219 | ✓ | [`src/go/plugin/ibm.d/GEMINI.md`](src/go/plugin/ibm.d/GEMINI.md) |
| 220 | ✓ | [`src/go/plugin/ibm.d/metricgen/README.md`](src/go/plugin/ibm.d/metricgen/README.md) |
| 221 | ✓ | [`src/go/plugin/ibm.d/modules/README.md`](src/go/plugin/ibm.d/modules/README.md) |
| 222 | ✓ | [`src/go/plugin/ibm.d/modules/websphere/README.md`](src/go/plugin/ibm.d/modules/websphere/README.md) |
| 223 | ✓ | [`src/go/plugin/ibm.d/pkg/odbcbridge/README.md`](src/go/plugin/ibm.d/pkg/odbcbridge/README.md) |
| 224 | ✓ | [`src/go/plugin/ibm.d/pkg/README.md`](src/go/plugin/ibm.d/pkg/README.md) |
| 225 | ✓ | [`src/go/plugin/ibm.d/protocols/as400/README.md`](src/go/plugin/ibm.d/protocols/as400/README.md) |
| 226 | ✓ | [`src/go/plugin/ibm.d/protocols/pcf/README.md`](src/go/plugin/ibm.d/protocols/pcf/README.md) |
| 227 | ✓ | [`src/go/plugin/ibm.d/protocols/README.md`](src/go/plugin/ibm.d/protocols/README.md) |
| 228 | ✓ | [`src/go/plugin/ibm.d/README.md`](src/go/plugin/ibm.d/README.md) |
| 229 | ✓ | [`src/go/plugin/ibm.d/samples.d/README.md`](src/go/plugin/ibm.d/samples.d/README.md) |
| 230 | ✓ | [`src/go/plugin/scripts.d/pkg/timeperiod/README.md`](src/go/plugin/scripts.d/pkg/timeperiod/README.md) |
| 231 | ✓ | [`src/go/plugin/scripts.d/README.md`](src/go/plugin/scripts.d/README.md) |
| 232 | ✓ | [`src/go/tools/functions-validation/README.md`](src/go/tools/functions-validation/README.md) |
| 233 | ✓ | [`src/go/tools/topology-ip-intel-downloader/README.md`](src/go/tools/topology-ip-intel-downloader/README.md) |
| 234 | ✓ | [`src/go/tools/topology-ip-intel-downloader/stock/README.md`](src/go/tools/topology-ip-intel-downloader/stock/README.md) |
| 235 | ✓ | [`src/health/alert-configuration-ordering.md`](src/health/alert-configuration-ordering.md) |
| 236 | ✓ | [`src/health/notifications/alerta/README.md`](src/health/notifications/alerta/README.md) |
| 237 | ✓ | [`src/health/notifications/awssns/README.md`](src/health/notifications/awssns/README.md) |
| 238 | ✓ | [`src/health/notifications/custom/README.md`](src/health/notifications/custom/README.md) |
| 239 | ✓ | [`src/health/notifications/discord/README.md`](src/health/notifications/discord/README.md) |
| 240 | ✓ | [`src/health/notifications/dynatrace/README.md`](src/health/notifications/dynatrace/README.md) |
| 241 | ✓ | [`src/health/notifications/email/README.md`](src/health/notifications/email/README.md) |
| 242 | ✓ | [`src/health/notifications/flock/README.md`](src/health/notifications/flock/README.md) |
| 243 | ✓ | [`src/health/notifications/gotify/README.md`](src/health/notifications/gotify/README.md) |
| 244 | ✓ | [`src/health/notifications/ilert/README.md`](src/health/notifications/ilert/README.md) |
| 245 | ✓ | [`src/health/notifications/irc/README.md`](src/health/notifications/irc/README.md) |
| 246 | ✓ | [`src/health/notifications/kavenegar/README.md`](src/health/notifications/kavenegar/README.md) |
| 247 | ✓ | [`src/health/notifications/matrix/README.md`](src/health/notifications/matrix/README.md) |
| 248 | ✓ | [`src/health/notifications/messagebird/README.md`](src/health/notifications/messagebird/README.md) |
| 249 | ✓ | [`src/health/notifications/msteams/README.md`](src/health/notifications/msteams/README.md) |
| 250 | ✓ | [`src/health/notifications/ntfy/README.md`](src/health/notifications/ntfy/README.md) |
| 251 | ✓ | [`src/health/notifications/opsgenie/README.md`](src/health/notifications/opsgenie/README.md) |
| 252 | ✓ | [`src/health/notifications/pagerduty/README.md`](src/health/notifications/pagerduty/README.md) |
| 253 | ✓ | [`src/health/notifications/prowl/README.md`](src/health/notifications/prowl/README.md) |
| 254 | ✓ | [`src/health/notifications/pushbullet/README.md`](src/health/notifications/pushbullet/README.md) |
| 255 | ✓ | [`src/health/notifications/pushover/README.md`](src/health/notifications/pushover/README.md) |
| 256 | ✓ | [`src/health/notifications/README.md`](src/health/notifications/README.md) |
| 257 | ✓ | [`src/health/notifications/rocketchat/README.md`](src/health/notifications/rocketchat/README.md) |
| 258 | ✓ | [`src/health/notifications/signl4/README.md`](src/health/notifications/signl4/README.md) |
| 259 | ✓ | [`src/health/notifications/slack/README.md`](src/health/notifications/slack/README.md) |
| 260 | ✓ | [`src/health/notifications/smseagle/README.md`](src/health/notifications/smseagle/README.md) |
| 261 | ✓ | [`src/health/notifications/smstools3/README.md`](src/health/notifications/smstools3/README.md) |
| 262 | ✓ | [`src/health/notifications/syslog/README.md`](src/health/notifications/syslog/README.md) |
| 263 | ✓ | [`src/health/notifications/telegram/README.md`](src/health/notifications/telegram/README.md) |
| 264 | ✓ | [`src/health/notifications/twilio/README.md`](src/health/notifications/twilio/README.md) |
| 265 | ✓ | [`src/health/notifications/web/README.md`](src/health/notifications/web/README.md) |
| 266 | ✓ | [`src/health/overriding-stock-alerts.md`](src/health/overriding-stock-alerts.md) |
| 267 | ✓ | [`src/health/README.md`](src/health/README.md) |
| 268 | ✓ | [`src/health/REFERENCE.md`](src/health/REFERENCE.md) |
| 269 | ✓ | [`src/libnetdata/adaptive_resortable_list/README.md`](src/libnetdata/adaptive_resortable_list/README.md) |
| 270 | ✓ | [`src/libnetdata/aral/README.md`](src/libnetdata/aral/README.md) |
| 271 | ✓ | [`src/libnetdata/avl/README.md`](src/libnetdata/avl/README.md) |
| 272 | ✓ | [`src/libnetdata/buffer/README.md`](src/libnetdata/buffer/README.md) |
| 273 | ✓ | [`src/libnetdata/buffered_reader/README.md`](src/libnetdata/buffered_reader/README.md) |
| 274 | ✓ | [`src/libnetdata/circular_buffer/README.md`](src/libnetdata/circular_buffer/README.md) |
| 275 | ✓ | [`src/libnetdata/clocks/README.md`](src/libnetdata/clocks/README.md) |
| 276 | ✓ | [`src/libnetdata/datetime/README.md`](src/libnetdata/datetime/README.md) |
| 277 | ✓ | [`src/libnetdata/dictionary/README.md`](src/libnetdata/dictionary/README.md) |
| 278 | ✓ | [`src/libnetdata/eval/re2c_lemon/README.md`](src/libnetdata/eval/re2c_lemon/README.md) |
| 279 | ✓ | [`src/libnetdata/eval/README.md`](src/libnetdata/eval/README.md) |
| 280 | ✓ | [`src/libnetdata/facets/README.md`](src/libnetdata/facets/README.md) |
| 281 | ✓ | [`src/libnetdata/functions_evloop/README.md`](src/libnetdata/functions_evloop/README.md) |
| 282 | ✓ | [`src/libnetdata/gorilla/README.md`](src/libnetdata/gorilla/README.md) |
| 283 | ✓ | [`src/libnetdata/inicfg/README.md`](src/libnetdata/inicfg/README.md) |
| 284 | ✓ | [`src/libnetdata/json/README.md`](src/libnetdata/json/README.md) |
| 285 | ✓ | [`src/libnetdata/line_splitter/README.md`](src/libnetdata/line_splitter/README.md) |
| 286 | ✓ | [`src/libnetdata/locks/README.md`](src/libnetdata/locks/README.md) |
| 287 | ✓ | [`src/libnetdata/log/README.md`](src/libnetdata/log/README.md) |
| 288 | ✓ | [`src/libnetdata/log/systemd-cat-native.md`](src/libnetdata/log/systemd-cat-native.md) |
| 289 | ✓ | [`src/libnetdata/onewayalloc/README.md`](src/libnetdata/onewayalloc/README.md) |
| 290 | ✓ | [`src/libnetdata/procfile/README.md`](src/libnetdata/procfile/README.md) |
| 291 | ✓ | [`src/libnetdata/query_progress/README.md`](src/libnetdata/query_progress/README.md) |
| 292 | ✓ | [`src/libnetdata/README.md`](src/libnetdata/README.md) |
| 293 | ✓ | [`src/libnetdata/simple_pattern/README.md`](src/libnetdata/simple_pattern/README.md) |
| 294 | ✓ | [`src/libnetdata/socket/README.md`](src/libnetdata/socket/README.md) |
| 295 | ✓ | [`src/libnetdata/statistical/README.md`](src/libnetdata/statistical/README.md) |
| 296 | ✓ | [`src/libnetdata/storage_number/README.md`](src/libnetdata/storage_number/README.md) |
| 297 | ✓ | [`src/libnetdata/string/README.md`](src/libnetdata/string/README.md) |
| 298 | ✓ | [`src/libnetdata/threads/README.md`](src/libnetdata/threads/README.md) |
| 299 | ✓ | [`src/libnetdata/url/README.md`](src/libnetdata/url/README.md) |
| 300 | ✓ | [`src/libnetdata/uuid/README.md`](src/libnetdata/uuid/README.md) |
| 301 | ✓ | [`src/libnetdata/worker_utilization/README.md`](src/libnetdata/worker_utilization/README.md) |
| 302 | ✓ | [`src/libnetdata/yaml/README.md`](src/libnetdata/yaml/README.md) |
| 303 | ✓ | [`src/ml/ml-configuration.md`](src/ml/ml-configuration.md) |
| 304 | ✓ | [`src/ml/notebooks/README.md`](src/ml/notebooks/README.md) |
| 305 | ✓ | [`src/ml/README.md`](src/ml/README.md) |
| 306 | ✓ | [`src/plugins.d/README.md`](src/plugins.d/README.md) |
| 307 | ✓ | [`src/registry/README.md`](src/registry/README.md) |
| 308 | ✓ | [`src/streaming/README.md`](src/streaming/README.md) |
| 309 | ✓ | [`src/web/api/exporters/prometheus/README.md`](src/web/api/exporters/prometheus/README.md) |
| 310 | ✓ | [`src/web/api/exporters/README.md`](src/web/api/exporters/README.md) |
| 311 | ✓ | [`src/web/api/exporters/shell/README.md`](src/web/api/exporters/shell/README.md) |
| 312 | ✓ | [`src/web/api/formatters/csv/README.md`](src/web/api/formatters/csv/README.md) |
| 313 | ✓ | [`src/web/api/formatters/json/README.md`](src/web/api/formatters/json/README.md) |
| 314 | ✓ | [`src/web/api/formatters/README.md`](src/web/api/formatters/README.md) |
| 315 | ✓ | [`src/web/api/formatters/ssv/README.md`](src/web/api/formatters/ssv/README.md) |
| 316 | ✓ | [`src/web/api/formatters/value/README.md`](src/web/api/formatters/value/README.md) |
| 317 | ✓ | [`src/web/api/health/README.md`](src/web/api/health/README.md) |
| 318 | ✓ | [`src/web/api/queries/average/README.md`](src/web/api/queries/average/README.md) |
| 319 | ✓ | [`src/web/api/queries/countif/README.md`](src/web/api/queries/countif/README.md) |
| 320 | ✓ | [`src/web/api/queries/des/README.md`](src/web/api/queries/des/README.md) |
| 321 | ✓ | [`src/web/api/queries/incremental_sum/README.md`](src/web/api/queries/incremental_sum/README.md) |
| 322 | ✓ | [`src/web/api/queries/max/README.md`](src/web/api/queries/max/README.md) |
| 323 | ✓ | [`src/web/api/queries/median/README.md`](src/web/api/queries/median/README.md) |
| 324 | ✓ | [`src/web/api/queries/min/README.md`](src/web/api/queries/min/README.md) |
| 325 | ✓ | [`src/web/api/queries/percentile/README.md`](src/web/api/queries/percentile/README.md) |
| 326 | ✓ | [`src/web/api/queries/README.md`](src/web/api/queries/README.md) |
| 327 | ✓ | [`src/web/api/queries/ses/README.md`](src/web/api/queries/ses/README.md) |
| 328 | ✓ | [`src/web/api/queries/stddev/README.md`](src/web/api/queries/stddev/README.md) |
| 329 | ✓ | [`src/web/api/queries/sum/README.md`](src/web/api/queries/sum/README.md) |
| 330 | ✓ | [`src/web/api/queries/trimmed_mean/README.md`](src/web/api/queries/trimmed_mean/README.md) |
| 331 | ✓ | [`src/web/api/README.md`](src/web/api/README.md) |
| 332 | ✓ | [`src/web/api/v1/api_v1_badge/README.md`](src/web/api/v1/api_v1_badge/README.md) |
| 333 | ✓ | [`src/web/mcp/bridges/README.md`](src/web/mcp/bridges/README.md) |
| 334 | ✓ | [`src/web/mcp/bridges/stdio-golang/README.md`](src/web/mcp/bridges/stdio-golang/README.md) |
| 335 | ✓ | [`src/web/mcp/bridges/stdio-nodejs/README.md`](src/web/mcp/bridges/stdio-nodejs/README.md) |
| 336 | ✓ | [`src/web/mcp/bridges/stdio-python/README.md`](src/web/mcp/bridges/stdio-python/README.md) |
| 337 | ✓ | [`src/web/mcp/README.md`](src/web/mcp/README.md) |
| 338 | ✓ | [`src/web/README.md`](src/web/README.md) |
| 339 | ✓ | [`src/web/rtc/README.md`](src/web/rtc/README.md) |
| 340 | ✓ | [`src/web/server/README.md`](src/web/server/README.md) |
| 341 | ✓ | [`src/web/server/static/README.md`](src/web/server/static/README.md) |
| 342 | ✓ | [`src/web/websocket/README.md`](src/web/websocket/README.md) |
| 343 | ✓ | [`tests/ebpf/README.md`](tests/ebpf/README.md) |
| 344 | ✓ | [`tests/health_mgmtapi/README.md`](tests/health_mgmtapi/README.md) |
| 345 | → | [`README.md`](README.md) |

---

*Generated by mirror — do not edit manually*