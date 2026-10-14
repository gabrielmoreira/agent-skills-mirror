# Consolidated plugin offer

The editorial offer contains 30 focused packs plus the full-library plugin. Both Codex and Claude marketplaces derive their entries from the same editorial manifest. The 28 overlapping packs are merged into existing destinations, not offered as duplicate compatibility plugins. No canonical skill is deleted.

The Web App and Design Studio destination IDs are shortened to `web-app` and `design-studio` so Codex qualified skill names remain within the existing 64-character limit. Their former AAS IDs are lookup aliases only; use the new marketplace entries when migrating.

## Existing installations

Existing installed copies are not automatically replaced or removed. Update the marketplace, inspect the destination pack, install it with your host's normal plugin controls, then disable or uninstall the retired pack to avoid duplicate skill activation. Do not uninstall your old pack until the replacement has been verified. The full-library plugin is unchanged.

Old bundle IDs and former names remain lookup aliases for the activation helper. They resolve to the entire consolidated pack, which may contain more skills than the old pack. They are not installable marketplace aliases; neither Codex nor Claude is claimed to redirect plugin IDs automatically. No account, external connector or credentials are configured by this migration.

## Replacements

| Former pack / ID | Replacement | Stable destination ID |
| --- | --- | --- |
| Security Engineer (`security-engineer`) | AAS Security Engineer | `aas-security-engineer` |
| Security Developer (`security-developer`) | AAS Secure App Builder | `aas-secure-app-builder` |
| Web Wizard (`web-wizard`) | AAS Web App Builder | `web-app` |
| Web Designer (`web-designer`) | AAS Product Design Studio | `design-studio` |
| Agent Architect (`agent-architect`) | AAS Agent & MCP Builder | `aas-agent-mcp-builder` |
| LLM Application Developer (`llm-application-developer`) | AAS Agent & MCP Builder | `aas-agent-mcp-builder` |
| Python Pro (`python-pro`) | AAS Python Development | `aas-python-api-builder` |
| Startup Founder (`startup-founder`) | AAS SaaS Launch & Revenue | `aas-saas-launch-revenue` |
| Marketing & Growth (`marketing-growth`) | AAS Marketing, SEO & Growth | `aas-marketing-seo-growth` |
| DevOps & Cloud (`devops-cloud`) | AAS DevOps & Cloud | `aas-devops-cloud` |
| Observability & Monitoring (`observability-monitoring`) | AAS Observability & Incident Response | `aas-observability-ir` |
| Data & Analytics (`data-analytics`) | AAS Data Analytics & Business Intelligence | `aas-data-analytics` |
| Data Engineering (`data-engineering`) | AAS Data Engineering Platform | `aas-data-engineering-platform` |
| QA & Testing (`qa-testing`) | AAS QA & Test Automation | `aas-qa-test-automation` |
| Mobile Developer (`mobile-developer`) | AAS Mobile App Builder | `aas-mobile-app-builder` |
| Automation Builder (`automation-builder`) | AAS Automation Builder | `aas-automation-builder` |
| Documents & Presentations (`documents-presentations`) | AAS Documents & Presentations | `aas-documents-presentations` |
| SEO Specialist (`seo-specialist`) | AAS Marketing, SEO & Growth | `aas-marketing-seo-growth` |
| Expo & React Native (`expo-react-native`) | AAS Mobile App Builder | `aas-mobile-app-builder` |
| Creative Director (`creative-director`) | AAS Product Design Studio | `design-studio` |
| Business Analyst (`business-analyst`) | AAS Data Analytics & Business Intelligence | `aas-data-analytics` |
| DDD & Evented Architecture (`ddd-evented-architecture`) | Architecture & Domain Modeling | `architecture-design` |
| Integration & APIs (`integration-apis`) | Payments & Service Integrations | `commerce-payments` |
| Full-Stack Developer (`full-stack-developer`) | AAS Backend & API Platform | `aas-api-platform-builder` |
| RevOps & CRM Automation (`revops-crm-automation`) | AAS Automation Builder | `aas-automation-builder` |
| Apple Platform Design (`apple-platform-design`) | AAS Mobile App Builder | `aas-mobile-app-builder` |
| Azure AI & Cloud (`azure-ai-cloud`) | AAS DevOps & Cloud | `aas-devops-cloud` |
| TypeScript & JavaScript (`typescript-javascript`) | AAS Web App Builder | `web-app` |
| AAS Web App Builder (`aas-web-app-builder`) | AAS Web App Builder | `web-app` |
| AAS Product Design Studio (`aas-product-design-studio`) | AAS Product Design Studio | `design-studio` |

## Choosing between remaining packs

Shared individual skills do not create duplicate packs. Security Engineer assesses authorized targets; Secure App Builder implements defensive controls; Privacy & Compliance Engineering maps data controls and evidence. Product Design Studio prepares visual direction; Web App Builder implements browser features; Mobile App Builder implements mobile features. Backend & API Platform covers cross-stack service architecture and contract lifecycle; Python Development covers Python language and framework implementation. Data Analytics & Business Intelligence interprets metrics and decisions; Data Engineering Platform builds ingestion and transformation pipelines. SaaS Launch & Revenue covers product launch and pricing; Marketing, SEO & Growth covers acquisition content. AI Product & Evaluation Ops defines feature success and evaluation; Agent & MCP Builder implements agent tools and workflows.

Odoo ERP, Makepad Builder, Systems Programming, Indie Game Dev, OSS Maintainer, Skill Author and Essentials retain distinct jobs. Other overlapping historical specializations have been absorbed rather than kept as parallel packs.

This consolidation is source maintenance. Installation availability follows the next published release; the immutable 19.6.0 marketplace and package are not rewritten.
