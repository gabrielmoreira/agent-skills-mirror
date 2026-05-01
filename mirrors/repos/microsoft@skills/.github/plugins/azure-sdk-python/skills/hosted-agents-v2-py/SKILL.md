---
name: hosted-agents-v2-py
description: |
  Build Microsoft Foundry hosted agents on the refreshed public preview across Python and C#.
  Use when creating containerized agents with Responses or Invocations protocols, Agent Framework,
  LangGraph, BYO/custom code, agent.yaml, azd ai agent, or AIProjectClient HostedAgentDefinition.
  Triggers: "hosted agent", "Foundry hosted agent", "Responses protocol", "Invocations protocol",
  "ResponsesAgentServerHost", "InvocationAgentServerHost", "ResponsesHostServer",
  "HostedAgentDefinition", "agent.yaml", "azd ai agent".
license: MIT
metadata:
  author: Microsoft
  version: "2.0.0"
  packages:
    - azure-ai-agentserver-responses
    - azure-ai-agentserver-invocations
    - agent-framework-foundry-hosting
    - azure-ai-projects
---

# Microsoft Foundry Hosted Agents

Build hosted agents on the refreshed Microsoft Foundry Agent Service backend. Hosted agents are containerized agentic applications that expose one or more platform protocols and run on managed Foundry infrastructure.

> Migration note: the initial-preview backend is being retired. Do not build new hosted agents around `ImageBasedHostedAgentDefinition`, protocol `version="v1"`, capability hosts, `tools` in the agent definition, shared project managed identity runtime access, or `agent_reference` invocation routing.

## Before Implementation

Hosted agents are preview and change quickly. Search Microsoft Learn for current hosted-agent docs before generating production code:

- Query: "Microsoft Foundry hosted agents deploy hosted agent refreshed preview"
- Query: "azure-ai-agentserver-responses ResponsesAgentServerHost"
- Query: "azure-ai-agentserver-invocations InvocationAgentServerHost"
- Query: "AIProjectClient HostedAgentDefinition protocol version 1.0.0"

## Installation

Use the packages that match your implementation path.

| Path | Python | .NET |
|------|--------|------|
| Agent Framework | `agent-framework-foundry-hosting` plus current Agent Framework packages | Microsoft Agent Framework hosting package with Foundry responses extensions |
| BYO Responses protocol | `azure-ai-agentserver-responses` | `Azure.AI.AgentServer.Responses` |
| BYO Invocations protocol | `azure-ai-agentserver-invocations` | `Azure.AI.AgentServer.Invocations` |
| Direct deployment management | `azure-ai-projects>=2.1.0` | Use REST or current .NET management SDK support |
| Authentication | `azure-identity` | `Azure.Identity` |

```bash
pip install azure-identity azure-ai-agentserver-responses azure-ai-agentserver-invocations
pip install agent-framework-foundry-hosting "azure-ai-projects>=2.1.0"
```

## Environment Variables

```bash
FOUNDRY_PROJECT_ENDPOINT=https://<account>.services.ai.azure.com/api/projects/<project> # Auto-injected in hosted containers
AZURE_AI_MODEL_DEPLOYMENT_NAME=<model-deployment-name> # Declare this in agent.manifest.yaml when your code needs it
APPLICATIONINSIGHTS_CONNECTION_STRING=<connection-string> # Auto-injected in hosted containers
AZURE_TOKEN_CREDENTIALS=prod # Required only if DefaultAzureCredential is used in production
```

Platform-injected variables are set automatically at runtime. Do not redeclare `FOUNDRY_PROJECT_ENDPOINT`, `FOUNDRY_PROJECT_ARM_ID`, `FOUNDRY_AGENT_NAME`, `FOUNDRY_AGENT_VERSION`, `FOUNDRY_AGENT_SESSION_ID`, or `APPLICATIONINSIGHTS_CONNECTION_STRING` in `agent.yaml` or `agent.manifest.yaml`.

## Choose a Protocol

| Scenario | Protocol | Endpoint | Why |
|----------|----------|----------|-----|
| Conversational assistant, RAG, tools, streaming, Teams/M365 logic | Responses | `/responses` locally, dedicated OpenAI-compatible endpoint after deploy | Platform manages conversation history, streaming lifecycle, and background polling |
| Background processing that fits OpenAI Responses polling | Responses | `/responses` | Use `background: true` with platform-managed polling and cancellation |
| Webhook receiver, classification/extraction, custom payloads | Invocations | `/invocations` | Caller sends arbitrary JSON that does not map to `/responses` |
| Custom streaming protocol such as AG-UI | Invocations | `/invocations` | You control raw SSE and payload semantics |
| Protocol bridge or inter-service orchestration | Invocations | `/invocations` | Caller owns the protocol contract |

Default to Responses when unsure. A single container can expose multiple protocols by listing each protocol in `agent.yaml` or `container_protocol_versions`.

Additional protocols exist for specialized cases: Activity for Teams/M365 channels and A2A for agent-to-agent delegation.

## Choose an Implementation Path

| Path | Use When | Packages |
|------|----------|----------|
| Agent Framework | Starting fresh on Foundry, or using AutoGen/Semantic Kernel through Agent Framework | `agent-framework-foundry-hosting` (Python) or Foundry hosting extensions for .NET |
| LangGraph | Existing LangGraph code that should keep its graph/tools | `azure-ai-agentserver-responses` or `azure-ai-agentserver-invocations` |
| Bring your own/custom | Existing CrewAI, Pydantic AI, custom HTTP, or non-Python/.NET logic wrapped by a protocol server | Protocol library for Python or .NET, or custom container that honors the protocol contract |

Hosted agents currently have first-party protocol libraries for Python and C#. The deployment and container contract are language-neutral.

## Core Workflow with azd

Use `azd` for the fastest path because it handles project setup, container build/push, version creation, and common RBAC.

```bash
azd ext install azure.ai.agents

mkdir my-hosted-agent
cd my-hosted-agent

azd ai agent init
azd ai agent run
azd ai agent invoke --local "What can you do?"

azd up
azd ai agent show --output table
azd ai agent invoke "What can you do?"
azd ai agent monitor --tail 20

azd down
```

For non-interactive environments, use `azd ai agent init --no-prompt` and provide all required flags.

## Container Contract

- Build Linux x64 images. On Apple Silicon, use `docker build --platform linux/amd64 ...`.
- Serve locally on port `8088`. The Foundry gateway handles production routing.
- Use protocol libraries to expose `/responses`, `/invocations`, and `/readiness`; do not hand-roll the health endpoint.
- Use the agent's dedicated Entra identity at runtime. The project managed identity is for platform infrastructure work such as ACR pulls.
- Grant downstream Azure resource RBAC to the agent identity, not to the project managed identity.
- Put only custom configuration in `environment_variables`; never put secrets in images or environment variables.

## Python: Agent Framework Responses

Use this path for new Python agents that want Foundry integration with Agent Framework.

```python
import os

from agent_framework import Agent
from agent_framework.foundry import FoundryChatClient
from agent_framework_foundry_hosting import ResponsesHostServer
from azure.identity import DefaultAzureCredential


client = FoundryChatClient(
    project_endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"],
    model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
    credential=DefaultAzureCredential(),
)

agent = Agent(
    client=client,
    instructions="You are a helpful assistant.",
    default_options={"store": False},
)

ResponsesHostServer(agent).run()
```

Why `store=False`: hosted-agent Responses protocol stores conversation history in the platform. Avoid duplicating history in the agent service unless you intentionally manage it yourself.

For Agent Framework MCP tools, use runtime MCP clients such as `client.get_mcp_tool(...)`. Do not put `tools=[...]` in the hosted agent version definition.

## Python: BYO Responses Protocol

Use the protocol library directly when you already have LangGraph, CrewAI, Pydantic AI, or custom orchestration.

```python
import asyncio

from azure.ai.agentserver.responses import (
    CreateResponse,
    ResponseContext,
    ResponsesAgentServerHost,
    TextResponse,
)

app = ResponsesAgentServerHost()


@app.response_handler
async def handle_response(
    request: CreateResponse,
    context: ResponseContext,
    cancellation_signal: asyncio.Event,
):
    user_text = await context.get_input_text()
    return TextResponse(context, request, text=f"Echo: {user_text}")


app.run()
```

For streaming, pass an async iterable to `TextResponse`. Use `ResponseEventStream` when you need fine-grained output items, function-call events, or reasoning events.

## Python: BYO Invocations Protocol

Use Invocations for arbitrary JSON, webhooks, custom SSE, or long-running workflows that do not fit OpenAI Responses.

```python
from azure.ai.agentserver.invocations import InvocationAgentServerHost
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

app = InvocationAgentServerHost()


@app.invoke_handler
async def handle_invocation(request: Request) -> Response:
    payload = await request.json()
    message = payload.get("message", "")
    return JSONResponse({"response": f"Echo: {message}"})


app.run()
```

For long-running Invocations, add `@app.get_invocation_handler` and `@app.cancel_invocation_handler` so callers can poll and cancel explicitly.

## Python: Multi-Protocol Host

Expose both Responses and Invocations by composing hosts and declaring both protocols in deployment config.

```python
from azure.ai.agentserver.invocations import InvocationAgentServerHost
from azure.ai.agentserver.responses import ResponsesAgentServerHost


class HostedAgentHost(InvocationAgentServerHost, ResponsesAgentServerHost):
    pass


app = HostedAgentHost()
```

Register both handlers on the same `app`.

## C# Patterns

For C# hosted agents, use the .NET protocol packages:

- Responses: `Azure.AI.AgentServer.Responses`
- Invocations: `Azure.AI.AgentServer.Invocations`
- Core hosting support: `Azure.AI.AgentServer.Core`
- Authentication: `Azure.Identity`

For .NET Agent Framework agents, use the Agent Framework Foundry hosting extensions. The refreshed pattern uses ASP.NET extension methods such as `AddFoundryResponses` and `MapFoundryResponses` rather than the old `Azure.AI.AgentServer.AgentFramework` adapter. Verify exact overloads against the installed package version before coding.

## agent.manifest.yaml

Use `agent.manifest.yaml` for sample scaffolding with `azd ai agent init -m`.

```yaml
name: basic-responses-agent
description: >
  A hosted agent using the Responses protocol.
template:
  name: basic-responses-agent
  kind: hosted
  protocols:
    - protocol: responses
      version: 1.0.0
  environment_variables:
    - name: AZURE_AI_MODEL_DEPLOYMENT_NAME
      value: "{{AZURE_AI_MODEL_DEPLOYMENT_NAME}}"
resources:
  - kind: model
    id: gpt-4.1-mini
    name: AZURE_AI_MODEL_DEPLOYMENT_NAME
```

## agent.yaml

The deployed container definition uses protocol version `1.0.0`, not `v1`.

```yaml
kind: hosted
name: basic-responses-agent
protocols:
  - protocol: responses
    version: 1.0.0
resources:
  cpu: "0.25"
  memory: "0.5Gi"
```

To expose both protocols:

```yaml
protocols:
  - protocol: responses
    version: 1.0.0
  - protocol: invocations
    version: 1.0.0
```

## Direct Deployment with Python SDK

Use SDK deployment when you manage agent versions from automation. Prefer `azd` or VS Code for first deployment.

```python
import os
import time

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    AgentProtocol,
    HostedAgentDefinition,
    ProtocolVersionRecord,
)
from azure.identity import DefaultAzureCredential


project = AIProjectClient(
    endpoint=os.environ["AZURE_AI_PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential(),
    allow_preview=True,
)

agent = project.agents.create_version(
    agent_name="my-hosted-agent",
    definition=HostedAgentDefinition(
        container_protocol_versions=[
            ProtocolVersionRecord(
                protocol=AgentProtocol.RESPONSES,
                version="1.0.0",
            ),
            ProtocolVersionRecord(
                protocol=AgentProtocol.INVOCATIONS,
                version="1.0.0",
            ),
        ],
        image="myregistry.azurecr.io/my-agent:v1",
        cpu="1",
        memory="2Gi",
        environment_variables={
            "AZURE_AI_MODEL_DEPLOYMENT_NAME": os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
        },
    ),
)

while True:
    version = project.agents.get_version(
        agent_name="my-hosted-agent",
        agent_version=agent.version,
    )
    status = version["status"]
    if status == "active":
        break
    if status == "failed":
        raise RuntimeError(f"Hosted agent provisioning failed: {version['error']}")
    time.sleep(5)

openai_client = project.get_openai_client(agent_name="my-hosted-agent")
response = openai_client.responses.create(input="Hello!")
print(response.output_text)
```

For Invocations over REST, call the dedicated endpoint:

```python
import os
import requests
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()
token = credential.get_token("https://ai.azure.com/.default").token
project_endpoint = os.environ["AZURE_AI_PROJECT_ENDPOINT"]

response = requests.post(
    f"{project_endpoint}/agents/my-hosted-agent/endpoint/protocols/invocations",
    headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Foundry-Features": "HostedAgents=V1Preview",
    },
    params={"api-version": "v1"},
    json={"message": "Process this task"},
    timeout=30,
)
response.raise_for_status()
print(response.json())
```

## Direct Deployment with REST

```bash
BASE_URL="https://<account>.services.ai.azure.com/api/projects/<project>"
API_VERSION="v1"
TOKEN=$(az account get-access-token --resource https://ai.azure.com --query accessToken -o tsv)

curl -X POST "$BASE_URL/agents?api-version=$API_VERSION" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my-hosted-agent",
    "definition": {
      "kind": "hosted",
      "image": "myregistry.azurecr.io/my-agent:v1",
      "cpu": "1",
      "memory": "2Gi",
      "container_protocol_versions": [
        {"protocol": "responses", "version": "1.0.0"},
        {"protocol": "invocations", "version": "1.0.0"}
      ],
      "environment_variables": {
        "AZURE_AI_MODEL_DEPLOYMENT_NAME": "gpt-5-mini"
      }
    }
  }'
```

REST calls to hosted-agent endpoints require `Foundry-Features: HostedAgents=V1Preview` during preview. SDK clients set preview headers automatically.

## Migration Checklist

1. Replace `azure-ai-agentserver-agentframework` and `azure-ai-agentserver-langgraph` with protocol libraries.
2. For Agent Framework Python, replace `AzureAIAgentClient` with `FoundryChatClient`, `ChatAgent` with `Agent`, `@ai_function` with `@tool`, and `from_agent_framework(agent).run()` with `ResponsesHostServer(agent).run()`.
3. For LangGraph, replace `from_langgraph(graph).run()` with `ResponsesAgentServerHost` plus a `@app.response_handler`.
4. For custom/BYO code, implement `ResponsesAgentServerHost` or `InvocationAgentServerHost`.
5. Update protocol versions from `"v1"` to `"1.0.0"`.
6. Remove capability host creation and manual start/stop/replica commands.
7. Remove `tools` from hosted agent version definitions; use runtime MCP/Foundry Toolbox integration.
8. Replace shared project endpoint invocation with dedicated endpoint routing or `project.get_openai_client(agent_name="...")`.
9. Grant downstream resource RBAC to the dedicated agent Entra identity.
10. Redeploy with `azd up` or `create_version`, then wait for version status `active`.

## Common Errors

| Error or Symptom | Cause | Fix |
|------------------|-------|-----|
| `preview_feature_required` | REST endpoint call missing preview header | Add `Foundry-Features: HostedAgents=V1Preview` |
| `image_pull_failed` or `AcrImageNotFound` | Bad image URL/tag or project MI lacks ACR pull access | Use immutable image tags and grant Container Registry Repository Reader/AcrPull |
| Agent starts locally but not in Foundry | ARM image or missing runtime env var | Build linux/amd64 and declare custom env vars in manifest |
| `PermissionDenied` calling models/tools | Runtime identity lacks RBAC | Grant required roles to the agent Entra identity |
| `/readiness` missing | Protocol host library not used | Use the Responses or Invocations protocol library |
| Conversation state duplicated | Agent stores history while Responses platform stores it too | Set Agent Framework default options to avoid duplicate storage |

## Best Practices

1. Start with Responses unless the caller requires arbitrary JSON, custom SSE, or non-OpenAI protocol semantics.
2. Use Agent Framework for new Python/C# agents; use protocol libraries for existing frameworks or custom code.
3. Test locally on `http://localhost:8088/responses` or `http://localhost:8088/invocations` before deployment.
4. Use immutable image tags, not `latest`, for production versions.
5. Keep secrets out of images and environment variables; prefer managed identity and managed connections.
6. Treat each agent version as immutable. Create a new version for runtime changes.
7. Use Application Insights and OpenTelemetry from the protocol libraries for logs, traces, and metrics.
8. Clean up with `azd down`, `project.agents.delete_version(...)`, or REST delete calls when finished.

## Reference Links

| Resource | URL |
|----------|-----|
| Hosted agents overview | https://learn.microsoft.com/azure/foundry/agents/concepts/hosted-agents |
| Deploy a hosted agent | https://learn.microsoft.com/azure/foundry/agents/how-to/deploy-hosted-agent |
| Quickstart | https://learn.microsoft.com/azure/foundry/agents/quickstarts/quickstart-hosted-agent |
| Migration guide | https://learn.microsoft.com/azure/foundry/agents/how-to/migrate-hosted-agent-preview |
| Hosted agent permissions | https://learn.microsoft.com/azure/foundry/agents/concepts/hosted-agent-permissions |
