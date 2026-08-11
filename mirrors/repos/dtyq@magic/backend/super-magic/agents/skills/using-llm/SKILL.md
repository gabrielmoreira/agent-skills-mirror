---
name: using-llm
description: List available large language models and send chat completion requests programmatically. Use this skill when you need to call an LLM within a snippet, including model comparison, visual understanding, batch inference, and model performance testing.

---

# LLM Calling Skill

List available models and send chat requests to any of them without extra configuration.

## Core Capabilities

- List currently available models
- Use the current Agent text model for requests
- Send chat completion requests in OpenAI format, non-streaming
- Attach images to vision-capable model requests

## Usage Guide

When you need to call an LLM in code, use the SDK functions from `sdk.llm`. There are two supported execution paths:

- Use `run_python_snippet` to execute a short or medium code snippet directly.
- Write the code to a `.py` file, then execute it with `shell_exec`.

`create_openai_sync_client` is a Python SDK function, not a tool name. Import it inside your Python code.

By default, call `create_openai_sync_client()` with no arguments. This uses the current Super Magic OpenAI-compatible endpoint and credentials automatically.

To use a custom OpenAI-compatible provider, pass `api_key` and `base_url` explicitly. You can also pass OpenAI client options such as `timeout`, `max_retries`, `default_headers`, and any additional keyword arguments supported by the OpenAI SDK.

To use the current Agent text model, read the `SUPER_MAGIC_CURRENT_MODEL_ID` environment variable in the script. This variable is injected by `run_python_snippet`. If it is missing, list models first and choose an explicit model ID.

```python
# Option 1: run_python_snippet
run_python_snippet(
    purpose="Run model code",
    python_code="""
import os
from sdk.llm import create_openai_sync_client

client = create_openai_sync_client()
model_id = os.environ.get("SUPER_MAGIC_CURRENT_MODEL_ID") or "<model-id>"
...
""",
    timeout=300,
)

# Option 2: write a .py file, then run it with shell_exec
# First write the script with write_file, then execute:
shell_exec("python scripts/my_llm_script.py")
```

LLM calls can take a while. Increase the timeout based on task complexity, for example `timeout=120` for a single call and `timeout=300` or more for multi-model comparisons or batch inference.

## Client Configuration

### Default Super Magic Provider

Use the no-argument form when you want the current Super Magic provider:

```python
run_python_snippet(
    purpose="Send test prompt",
    python_code="""
import os
from sdk.llm import create_openai_sync_client

client = create_openai_sync_client()
model_id = os.environ.get("SUPER_MAGIC_CURRENT_MODEL_ID") or "<model-id>"

response = client.chat.completions.create(
    model=model_id,
    messages=[{"role": "user", "content": "Hello"}],
    extra_body={"thinking": {"type": "disabled"}},
)
print(response.choices[0].message.content)
""",
    timeout=120,
)
```

### Custom OpenAI-Compatible Provider

Use explicit client arguments when the user provides their own OpenAI-compatible service:

```python
run_python_snippet(
    purpose="Use custom model",
    python_code="""
import os
from sdk.llm import create_openai_sync_client

client = create_openai_sync_client(
    api_key=os.environ["CUSTOM_OPENAI_API_KEY"],
    base_url="https://api.example.com/v1",
    timeout=120,
    max_retries=1,
)

response = client.chat.completions.create(
    model="custom-model-id",
    messages=[{"role": "user", "content": "Hello"}],
)
print(response.choices[0].message.content)
""",
    timeout=180,
)
```

Supported client factory arguments:

| Argument | Type | Description |
|---|---|---|
| `api_key` | `str` | API key for the custom provider. Omit it to use the current Super Magic credentials. |
| `base_url` | `str` | OpenAI-compatible base URL, usually ending with `/v1`. Omit it to use the current Super Magic endpoint. |
| `timeout` | `float` | Per-request timeout passed to the OpenAI client. |
| `max_retries` | `int` | OpenAI client retry count. Default is `0`. |
| `default_headers` | `dict[str, str]` | Headers attached to every request. |
| `**kwargs` | `Any` | Additional options passed through to `openai.OpenAI`. |

## Quick Start

### Step 1: List Available Models

When unsure of the model ID, query available models first:

```python
run_python_snippet(
    purpose="List models",
    python_code="""
import json
from sdk.llm import create_openai_sync_client

client = create_openai_sync_client()
models = client.models.list()
print(json.dumps([{"id": m.id} for m in models.data], ensure_ascii=False, indent=2))
""",
)
```

Example output:

```json
[
  {"id": "claude-3-5-sonnet-20241022"},
  {"id": "gpt-4o"},
  {"id": "deepseek-v3"}
]
```

### Step 2: Send a Chat Request

Use a real model ID to send a chat request. When executed through `run_python_snippet`, you can read `SUPER_MAGIC_CURRENT_MODEL_ID` to use the current model:

```python
run_python_snippet(
    purpose="Send chat",
    python_code="""
import os
from sdk.llm import create_openai_sync_client

client = create_openai_sync_client()
model_id = os.environ.get("SUPER_MAGIC_CURRENT_MODEL_ID") or "<model-id>"

response = client.chat.completions.create(
    model=model_id,
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello"},
    ],
    extra_body={"thinking": {"type": "disabled"}},
)

print(response.choices[0].message.content)
""",
    timeout=120,
)
```

## Vision: Attach Images in Messages

When using a vision-capable model, images can be included in messages. The SDK provides two ways to convert a workspace file to a URL:

| Function | Use Case |
|---|---|
| `file_to_url(path)` | Use this first. It returns a directly accessible URL. |
| `image_to_base64(path)` | Fallback if `file_to_url` fails. It encodes the image as base64. |

Both functions accept `http` and `https` URLs as input and return them unchanged.

Important: `image_to_base64` already returns a complete data URL string, such as `data:image/jpeg;base64,/9j/4AAQ...`. Use the return value directly as the `url` field. Do not prepend `data:image/jpeg;base64,` again.

```python
run_python_snippet(
    purpose="Analyze image",
    python_code="""
import os
from sdk.llm import create_openai_sync_client, file_to_url, image_to_base64

client = create_openai_sync_client()
model_id = os.environ.get("SUPER_MAGIC_CURRENT_MODEL_ID") or "<vision-model-id>"

# Use file_to_url first. Paths are relative to the .workspace directory.
image_url = file_to_url("test/screenshot.png")

# Fallback if file_to_url fails:
# image_url = image_to_base64("test/screenshot.png")
# image_to_base64 returns a complete data URL. Use it directly.

response = client.chat.completions.create(
    model=model_id,
    messages=[{
        "role": "user",
        "content": [
            {"type": "image_url", "image_url": {"url": image_url}},
            {"type": "text", "text": "Describe this image."},
        ],
    }],
    extra_body={"thinking": {"type": "disabled"}},
)

print(response.choices[0].message.content)
""",
    timeout=120,
)
```

## Parameter Reference

### Common Parameters for `client.chat.completions.create()`

| Parameter | Type | Required | Description |
|---|---|---|---|
| `model` | `str` | Yes | Model ID. Use a real ID from the model list or `SUPER_MAGIC_CURRENT_MODEL_ID`. |
| `messages` | `list` | Yes | List of messages, each with `role` and `content`. |
| `temperature` | `float` | No | Sampling temperature, 0 to 2. The default is 1. |
| `max_tokens` | `int` | No | Maximum output tokens. |
| `tools` | `list` | No | Tool definitions for Function Calling. |
| `extra_body` | `dict` | No | Extra fields not natively supported by the OpenAI SDK, such as `thinking`. |

### `thinking` Parameter

Pass `thinking` via `extra_body` to control whether the model emits reasoning content. The recommended default is `disabled` to avoid unnecessary token usage and latency.

| `thinking.type` value | Description |
|---|---|
| `disabled` | Disable deep thinking. Recommended default. |
| `enabled` | Enable deep thinking when the target model supports it. |
| `auto` | Let the model decide whether to use deep thinking. |

Note: The `thinking` parameter only applies to models that support it. Passing it to unsupported models may cause errors, so check the target model before using it.

```python
# Disable thinking. Recommended default.
extra_body={"thinking": {"type": "disabled"}}

# Enable thinking.
extra_body={"thinking": {"type": "enabled"}}

# Let the model decide.
extra_body={"thinking": {"type": "auto"}}
```

## Return Value

`client.chat.completions.create()` returns a `ChatCompletion` object:

```python
response.choices[0].message.content
response.choices[0].message.tool_calls
response.choices[0].finish_reason
response.usage.total_tokens

# Only present when thinking.type is "enabled" or "auto" and the model emits reasoning content.
response.choices[0].message.reasoning_content
response.usage.completion_tokens_details
```

`reasoning_content` is a non-standard field and may not be parsed by the OpenAI SDK as a normal attribute. Access it as follows:

```python
reasoning = response.choices[0].message.model_extra.get("reasoning_content")

import json
msg_dict = json.loads(response.choices[0].message.model_dump_json())
reasoning = msg_dict.get("reasoning_content")
```
