---
name: cloudvision-api-specialist
description: CloudVision API specialist for Python automation. Full version with workflows, examples, and troubleshooting.
version: full
includes: core.md + advanced sections
---

<!--
  CLAUDE VERSION (Full)
  =====================
  Deploy: Copy core.md content first, then add these advanced sections
-->

# Advanced Sections for Claude

The following sections extend the core instructions with detailed workflows, complete code examples, troubleshooting guides, and best practices suited for Claude's large context window.

---

## CVaaS Regional URLs

| Region | URL |
|--------|-----|
| United States 1a | `www.arista.io` |
| United States 1b | `www.cv-prod-us-central1-b.arista.io` |
| United States 1c | `www.cv-prod-us-central1-c.arista.io` |
| Canada | `www.cv-prod-na-northeast1-b.arista.io` |
| Europe West 2 | `www.cv-prod-euwest-2.arista.io` |
| Japan | `www.cv-prod-apnortheast-1.arista.io` |
| Australia | `www.cv-prod-ausoutheast-1.arista.io` |
| United Kingdom | `www.cv-prod-uk-1.arista.io` |

**Important**: CVaaS URLs must include `www` prefix.

---

## Advanced Authentication Patterns

### Pattern 1: CVaaS (No Custom CA)

```python
import os
import grpc

CV_HOST = os.environ["CLOUDVISION_HOST"]  # e.g., www.arista.io
CV_TOKEN = os.environ["CLOUDVISION_ACCESS_TOKEN"]

call_credentials = grpc.access_token_call_credentials(CV_TOKEN)
channel_credentials = grpc.ssl_channel_credentials()
combined_credentials = grpc.composite_channel_credentials(
    channel_credentials, call_credentials
)

channel = grpc.secure_channel(f"{CV_HOST}:443", combined_credentials)
```

### Pattern 2: Async Client (cloudvision >= 1.26.1)

```python
import os
from cloudvision.api.client import AsyncCVClient

client = AsyncCVClient.from_token(
    os.environ["CLOUDVISION_ACCESS_TOKEN"],
    os.environ["CLOUDVISION_HOST"],
)
```

### Pattern 3: With CA Bundle from Environment

```python
import os
import grpc
from pathlib import Path

CV_HOST = os.environ["CLOUDVISION_HOST"]
CV_TOKEN = os.environ["CLOUDVISION_ACCESS_TOKEN"]
CA_CERT_PATH = Path(os.environ.get("CLOUDVISION_CA_CERT", "/etc/nginx/cvp.crt"))

call_credentials = grpc.access_token_call_credentials(CV_TOKEN)
channel_credentials = grpc.ssl_channel_credentials(CA_CERT_PATH.read_bytes())
combined_credentials = grpc.composite_channel_credentials(
    channel_credentials, call_credentials
)

channel = grpc.secure_channel(f"{CV_HOST}:443", combined_credentials)
```

---

## Workflow 1: Get Device Inventory

**Goal**: Retrieve all devices with filtering by model or streaming status.

### Complete Example

```python
#!/usr/bin/env python3
"""
Get device inventory from CloudVision.
Filters by device model and streaming status.
"""
import os
import grpc
from cloudvision.api.arista.inventory.v1 import (
    inventory_pb2,
    inventory_pb2_grpc,
    models,
    services,
)

def get_all_devices(stub: services.DeviceServiceStub) -> list[models.DeviceKey]:
    """
    Retrieve all device keys from CloudVision inventory.

    Args:
        stub: gRPC DeviceService stub

    Returns:
        List of DeviceKey objects
    """
    devices = []
    request = services.DeviceStreamRequest()

    for response in stub.GetAll(request):
        devices.append(response.value.key)

    return devices


def filter_devices_by_model(
    stub: services.DeviceServiceStub,
    model_name: str
) -> list[tuple[models.DeviceKey, models.Device]]:
    """
    Filter devices by hardware model.

    Args:
        stub: gRPC DeviceService stub
        model_name: Hardware model to filter (e.g., "DCS-7050SX3-48YC8")

    Returns:
        List of (DeviceKey, Device) tuples matching the model
    """
    matching = []
    request = services.DeviceStreamRequest()

    for response in stub.GetAll(request):
        device = response.value
        if device.hardware_info and device.hardware_info.model == model_name:
            matching.append((device.key, device))

    return matching


def main():
    CV_HOST = os.environ["CLOUDVISION_HOST"]
    CV_TOKEN = os.environ["CLOUDVISION_ACCESS_TOKEN"]

    # CVaaS pattern (no CA cert needed)
    call_creds = grpc.access_token_call_credentials(CV_TOKEN)
    channel_creds = grpc.ssl_channel_credentials()
    combined_creds = grpc.composite_channel_credentials(channel_creds, call_creds)

    with grpc.secure_channel(f"{CV_HOST}:443", combined_creds) as channel:
        stub = services.DeviceServiceStub(channel)

        # Get all devices
        all_devices = get_all_devices(stub)
        print(f"Total devices: {len(all_devices)}")

        # Filter by model
        model_filter = "DCS-7050SX3-48YC8"
        filtered = filter_devices_by_model(stub, model_filter)
        print(f"Devices with model {model_filter}: {len(filtered)}")

        for key, device in filtered:
            print(f"  - {key.device_id}: {device.hostname}")


if __name__ == "__main__":
    main()
```

**Dependencies**:
```toml
[project]
dependencies = [
    "cloudvision>=1.26.1",
    "grpcio>=1.60.0",
]
```

---

## Workflow 2: Query Events and Alerts

**Goal**: Retrieve critical events from the last 24 hours.

### Complete Example

```python
#!/usr/bin/env python3
"""
Query CloudVision events with severity filtering.
"""
import os
import grpc
from datetime import datetime, timedelta, timezone
from google.protobuf.timestamp_pb2 import Timestamp
from cloudvision.api.arista.event.v1 import (
    event_pb2,
    event_pb2_grpc,
    models,
    services,
)


def get_critical_events_last_24h(
    stub: services.EventServiceStub
) -> list[models.Event]:
    """
    Retrieve critical events from the last 24 hours.

    Args:
        stub: gRPC EventService stub

    Returns:
        List of Event objects
    """
    events = []
    now = datetime.now(timezone.utc)
    time_24h_ago = now - timedelta(hours=24)

    # Build request with filter
    request = services.EventStreamRequest(
        partial_eq_filter=[
            models.Event(
                severity=event_pb2.EVENT_SEVERITY_CRITICAL
            )
        ]
    )

    for response in stub.GetAll(request):
        event = response.value
        event_time = event.key.timestamp.ToDatetime()

        if event_time >= time_24h_ago:
            events.append(event)

    return events


def main():
    CV_HOST = os.environ["CLOUDVISION_HOST"]
    CV_TOKEN = os.environ["CLOUDVISION_ACCESS_TOKEN"]

    call_creds = grpc.access_token_call_credentials(CV_TOKEN)
    channel_creds = grpc.ssl_channel_credentials()
    combined_creds = grpc.composite_channel_credentials(channel_creds, call_creds)

    with grpc.secure_channel(f"{CV_HOST}:443", combined_creds) as channel:
        stub = services.EventServiceStub(channel)

        critical_events = get_critical_events_last_24h(stub)
        print(f"Critical events (last 24h): {len(critical_events)}")

        for event in critical_events:
            timestamp = event.key.timestamp.ToDatetime()
            print(f"[{timestamp}] {event.title}")
            print(f"  Device: {event.key.key.device_id}")
            print(f"  Component: {event.key.key.component_type}")
            print(f"  Description: {event.description}\n")


if __name__ == "__main__":
    main()
```

---

## Workflow 3: Change Control Lifecycle

**Goal**: Create, approve, and execute a change control.

### Complete Example

```python
#!/usr/bin/env python3
"""
Manage CloudVision change control lifecycle.

WARNING: This script modifies CloudVision state.
"""
import os
import grpc
from google.protobuf.wrappers_pb2 import StringValue, BoolValue
from google.protobuf.timestamp_pb2 import Timestamp
from datetime import datetime, timedelta, timezone
from cloudvision.api.arista.changecontrol.v1 import (
    changecontrol_pb2,
    models,
    services,
)


def create_change_control(
    stub: services.ChangeControlServiceStub,
    name: str,
    description: str,
    device_ids: list[str],
) -> models.ChangeControlKey:
    """
    Create a new change control.

    Args:
        stub: gRPC ChangeControlService stub
        name: Change control name
        description: Change control description
        device_ids: List of device IDs to include

    Returns:
        ChangeControlKey for the created change control

    WARNING: This operation modifies CloudVision state.
    """
    # Generate unique CC ID
    cc_id = f"cc_{int(datetime.now(timezone.utc).timestamp())}"

    # Build change control config
    cc_config = models.ChangeControlConfig(
        name=StringValue(value=name),
        description=StringValue(value=description),
    )

    # Set stages (example: single stage with all devices)
    stage = models.StageConfig(
        name=StringValue(value="Stage 1"),
    )
    for device_id in device_ids:
        stage.rows.append(
            models.RowConfig(values=[StringValue(value=device_id)])
        )
    cc_config.stages.append(stage)

    # Create the change control
    key = models.ChangeControlKey(id=StringValue(value=cc_id))
    request = services.ChangeControlConfigSetRequest(
        value=models.ChangeControlConfig(
            key=key,
            **cc_config.__dict__
        )
    )

    response = stub.Set(request)
    return response.key


def approve_change_control(
    stub: services.ChangeControlServiceStub,
    cc_key: models.ChangeControlKey,
) -> None:
    """
    Approve a change control.

    WARNING: This operation modifies CloudVision state.
    """
    approval = models.ChangeControlApprovalConfig(
        key=cc_key,
        approve=BoolValue(value=True),
    )
    request = services.ChangeControlApprovalConfigSetRequest(value=approval)
    stub.ApprovalSet(request)


def start_change_control(
    stub: services.ChangeControlServiceStub,
    cc_key: models.ChangeControlKey,
) -> None:
    """
    Start an approved change control.

    WARNING: This operation modifies CloudVision state.
    """
    start_request = services.ChangeControlConfigSetRequest(
        value=models.ChangeControlConfig(
            key=cc_key,
        )
    )
    # Note: Actual start mechanism depends on CloudVision version
    # This is a simplified example
    stub.Start(start_request)


def main():
    CV_HOST = os.environ["CLOUDVISION_HOST"]
    CV_TOKEN = os.environ["CLOUDVISION_ACCESS_TOKEN"]

    call_creds = grpc.access_token_call_credentials(CV_TOKEN)
    channel_creds = grpc.ssl_channel_credentials()
    combined_creds = grpc.composite_channel_credentials(channel_creds, call_creds)

    with grpc.secure_channel(f"{CV_HOST}:443", combined_creds) as channel:
        stub = services.ChangeControlServiceStub(channel)

        # WARNING: Uncomment to create a change control
        # cc_key = create_change_control(
        #     stub,
        #     name="Test Change Control",
        #     description="Automated CC created by script",
        #     device_ids=["device1", "device2"],
        # )
        # print(f"Created change control: {cc_key.id.value}")

        print("Change control creation commented out for safety.")
        print("Uncomment in main() to execute.")


if __name__ == "__main__":
    main()
```

---

## Workflow 4: Configlet Management

**Goal**: Create, update, and assign configlets to devices.

### Complete Example

```python
#!/usr/bin/env python3
"""
Manage CloudVision configlets.

WARNING: This script modifies CloudVision state.
"""
import os
import grpc
from google.protobuf.wrappers_pb2 import StringValue
from cloudvision.api.arista.configlet.v1 import (
    models,
    services,
)


def create_static_configlet(
    stub: services.ConfigletServiceStub,
    name: str,
    body: str,
) -> models.ConfigletKey:
    """
    Create a static configlet.

    Args:
        stub: gRPC ConfigletService stub
        name: Configlet name
        body: EOS configuration content

    Returns:
        ConfigletKey for the created configlet

    WARNING: This operation modifies CloudVision state.
    """
    configlet = models.ConfigletConfig(
        key=models.ConfigletKey(name=StringValue(value=name)),
        body=StringValue(value=body),
        # display_name and description optional
    )

    request = services.ConfigletConfigSetRequest(value=configlet)
    response = stub.Set(request)
    return response.key


def get_configlet(
    stub: services.ConfigletServiceStub,
    name: str,
) -> models.ConfigletConfig | None:
    """
    Retrieve a configlet by name.

    Args:
        stub: gRPC ConfigletService stub
        name: Configlet name

    Returns:
        ConfigletConfig if found, None otherwise
    """
    key = models.ConfigletKey(name=StringValue(value=name))
    request = services.ConfigletConfigRequest(key=key)

    try:
        response = stub.GetOne(request)
        return response.value
    except grpc.RpcError as e:
        if e.code() == grpc.StatusCode.NOT_FOUND:
            return None
        raise


def delete_configlet(
    stub: services.ConfigletServiceStub,
    name: str,
) -> None:
    """
    Delete a configlet.

    WARNING: This operation modifies CloudVision state.
    """
    key = models.ConfigletKey(name=StringValue(value=name))
    request = services.ConfigletConfigDeleteRequest(key=key)
    stub.Delete(request)


def main():
    CV_HOST = os.environ["CLOUDVISION_HOST"]
    CV_TOKEN = os.environ["CLOUDVISION_ACCESS_TOKEN"]

    call_creds = grpc.access_token_call_credentials(CV_TOKEN)
    channel_creds = grpc.ssl_channel_credentials()
    combined_creds = grpc.composite_channel_credentials(channel_creds, call_creds)

    with grpc.secure_channel(f"{CV_HOST}:443", combined_creds) as channel:
        stub = services.ConfigletServiceStub(channel)

        # Example: Get existing configlet
        existing = get_configlet(stub, "NTP-SERVERS")
        if existing:
            print(f"Found configlet: {existing.key.name.value}")
            print(f"Body:\n{existing.body.value}")
        else:
            print("Configlet not found")

        # WARNING: Uncomment to create a configlet
        # configlet_body = """
        # ntp server 0.pool.ntp.org prefer
        # ntp server 1.pool.ntp.org
        # """
        # key = create_static_configlet(stub, "NTP-SERVERS", configlet_body)
        # print(f"Created configlet: {key.name.value}")


if __name__ == "__main__":
    main()
```

---

## Workflow 5: Workspace Operations

**Goal**: Create a workspace, make changes, and submit or abandon.

### Complete Example

```python
#!/usr/bin/env python3
"""
Manage CloudVision workspaces for staged configuration changes.

WARNING: This script modifies CloudVision state.
"""
import os
import grpc
from google.protobuf.wrappers_pb2 import StringValue, BoolValue
from cloudvision.api.arista.workspace.v1 import (
    models,
    services,
)


def create_workspace(
    stub: services.WorkspaceServiceStub,
    name: str,
    description: str,
) -> models.WorkspaceKey:
    """
    Create a new workspace.

    WARNING: This operation modifies CloudVision state.
    """
    workspace_id = f"ws_{int(os.urandom(4).hex(), 16)}"

    workspace = models.WorkspaceConfig(
        key=models.WorkspaceKey(workspace_id=StringValue(value=workspace_id)),
        display_name=StringValue(value=name),
        description=StringValue(value=description),
    )

    request = services.WorkspaceConfigSetRequest(value=workspace)
    response = stub.Set(request)
    return response.key


def submit_workspace(
    stub: services.WorkspaceServiceStub,
    workspace_key: models.WorkspaceKey,
) -> None:
    """
    Submit a workspace (create change control).

    WARNING: This operation modifies CloudVision state.
    """
    request = services.WorkspaceConfigSetRequest(
        value=models.WorkspaceConfig(
            key=workspace_key,
            # Additional submit parameters here
        )
    )
    # Note: Submit mechanism varies by CloudVision version
    # This is a simplified example
    stub.Submit(request)


def abandon_workspace(
    stub: services.WorkspaceServiceStub,
    workspace_key: models.WorkspaceKey,
) -> None:
    """
    Abandon a workspace (discard changes).

    WARNING: This operation modifies CloudVision state.
    """
    request = services.WorkspaceConfigDeleteRequest(key=workspace_key)
    stub.Delete(request)


def main():
    CV_HOST = os.environ["CLOUDVISION_HOST"]
    CV_TOKEN = os.environ["CLOUDVISION_ACCESS_TOKEN"]

    call_creds = grpc.access_token_call_credentials(CV_TOKEN)
    channel_creds = grpc.ssl_channel_credentials()
    combined_creds = grpc.composite_channel_credentials(channel_creds, call_creds)

    with grpc.secure_channel(f"{CV_HOST}:443", combined_creds) as channel:
        stub = services.WorkspaceServiceStub(channel)

        print("Workspace operations require careful planning.")
        print("Uncomment code in main() to execute.")


if __name__ == "__main__":
    main()
```

---

## Workflow 6: Tag Management

**Goal**: Create, assign, and query device tags.

### Complete Example

```python
#!/usr/bin/env python3
"""
Manage CloudVision tags (device and interface tagging).

WARNING: This script modifies CloudVision state.
"""
import os
import grpc
from google.protobuf.wrappers_pb2 import StringValue
from cloudvision.api.arista.tag.v2 import (
    models,
    services,
)


def create_device_tag(
    stub: services.TagServiceStub,
    label: str,
    value: str,
    device_id: str,
) -> models.TagKey:
    """
    Create and assign a device tag.

    WARNING: This operation modifies CloudVision state.
    """
    tag_key = models.TagKey(
        label=StringValue(value=label),
        value=StringValue(value=value),
        device_id=StringValue(value=device_id),
    )

    tag_config = models.TagConfig(
        key=tag_key,
    )

    request = services.TagConfigSetRequest(value=tag_config)
    response = stub.Set(request)
    return response.key


def get_devices_by_tag(
    stub: services.TagServiceStub,
    label: str,
    value: str,
) -> list[str]:
    """
    Get all devices with a specific tag.

    Returns:
        List of device IDs
    """
    device_ids = []

    # Query tags with partial match on label and value
    partial_eq = models.Tag(
        key=models.TagKey(
            label=StringValue(value=label),
            value=StringValue(value=value),
        )
    )

    request = services.TagStreamRequest(partial_eq_filter=[partial_eq])

    for response in stub.GetAll(request):
        tag = response.value
        if tag.key.device_id and tag.key.device_id.value:
            device_ids.append(tag.key.device_id.value)

    return device_ids


def delete_device_tag(
    stub: services.TagServiceStub,
    label: str,
    value: str,
    device_id: str,
) -> None:
    """
    Delete a device tag.

    WARNING: This operation modifies CloudVision state.
    """
    tag_key = models.TagKey(
        label=StringValue(value=label),
        value=StringValue(value=value),
        device_id=StringValue(value=device_id),
    )

    request = services.TagConfigDeleteRequest(key=tag_key)
    stub.Delete(request)


def main():
    CV_HOST = os.environ["CLOUDVISION_HOST"]
    CV_TOKEN = os.environ["CLOUDVISION_ACCESS_TOKEN"]

    call_creds = grpc.access_token_call_credentials(CV_TOKEN)
    channel_creds = grpc.ssl_channel_credentials()
    combined_creds = grpc.composite_channel_credentials(channel_creds, call_creds)

    with grpc.secure_channel(f"{CV_HOST}:443", combined_creds) as channel:
        stub = services.TagServiceStub(channel)

        # Query devices by tag
        devices = get_devices_by_tag(stub, "datacenter", "dc1")
        print(f"Devices tagged datacenter=dc1: {len(devices)}")
        for device_id in devices:
            print(f"  - {device_id}")


if __name__ == "__main__":
    main()
```

---

## Workflow 7: Provisioning with cvprac

**Goal**: Use cvprac for provisioning workflows — containers, devices, configlets, tasks, change controls.

### Setup

```toml
[project]
dependencies = [
    "cvprac>=1.4.0",
]
```

```python
from cvprac.cvp_client import CvpClient

# Token-based auth (recommended for automation)
clnt = CvpClient()
clnt.connect(
    nodes=["192.0.2.100"],
    username="svc-account",
    password="",
    api_token=os.environ["CLOUDVISION_ACCESS_TOKEN"],
)

# For CVaaS
clnt.connect(
    nodes=["www.arista.io"],
    username="svc-account",
    password="",
    api_token=os.environ["CLOUDVISION_ACCESS_TOKEN"],
)
```

### End-to-End Provisioning Workflow

```python
#!/usr/bin/env python3
"""
End-to-end provisioning workflow using cvprac.

Creates a container, moves devices into it, assigns configlets,
creates and executes a change control.

WARNING: This script modifies CloudVision state.
"""
import os
import uuid
import time
from datetime import datetime
from cvprac.cvp_client import CvpClient


def provision_devices(
    clnt: CvpClient,
    container_name: str,
    devices: list[dict],
) -> None:
    """
    Provision a list of devices:
    - Create target container (idempotent)
    - Move each device into container
    - Assign configlet to each device
    - Create and execute a change control

    Args:
        clnt: CvpClient instance
        container_name: Target container name
        devices: List of dicts with 'fqdn' and 'configlet_name' keys

    WARNING: This operation modifies CloudVision state.
    """
    # Get or create container
    parent = clnt.api.get_container_by_name("Tenant")
    try:
        clnt.api.add_container(container_name, parent["name"], parent["key"])
        print(f"Container '{container_name}' created")
    except Exception as e:
        if "Data already exists in Database" in str(e):
            print(f"Container '{container_name}' already exists")
        else:
            raise

    container = clnt.api.get_container_by_name(container_name)

    task_ids = []
    for device_spec in devices:
        fqdn = device_spec["fqdn"]
        configlet_name = device_spec["configlet_name"]

        # Move device to target container
        device = clnt.api.get_device_by_name(fqdn)
        result = clnt.api.move_device_to_container("automation", device, container)
        task_ids.extend(result["data"]["taskIds"])

        # Assign configlet
        configlet = clnt.api.get_configlet_by_name(configlet_name)
        clnt.api.apply_configlets_to_device("automation", device, [configlet])

    print(f"Generated task IDs: {task_ids}")

    if task_ids:
        # Create change control from task list
        cc_id = str(uuid.uuid4())
        cc_name = f"CC_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        clnt.api.create_change_control_v3(cc_id, cc_name, task_ids)
        print(f"Change control '{cc_name}' created")

        # Small delay to avoid timestamp drift between client and CVP
        time.sleep(2)
        clnt.api.approve_change_control(
            cc_id,
            timestamp=datetime.utcnow().isoformat() + "Z",
        )
        print("Change control approved")

        clnt.api.execute_change_controls([cc_id])
        print("Change control executing")


def main():
    clnt = CvpClient()
    clnt.connect(
        nodes=[os.environ["CLOUDVISION_HOST"]],
        username=os.environ.get("CLOUDVISION_USER", "svc-account"),
        password="",
        api_token=os.environ["CLOUDVISION_ACCESS_TOKEN"],
    )

    devices = [
        {"fqdn": "leaf1.example.com", "configlet_name": "leaf1-config"},
        {"fqdn": "leaf2.example.com", "configlet_name": "leaf2-config"},
    ]

    # WARNING: Uncomment to execute provisioning
    # provision_devices(clnt, "DC1_LEAFS", devices)
    print("Provisioning workflow ready. Uncomment provision_devices() to execute.")


if __name__ == "__main__":
    main()
```

### Useful cvprac Methods

```python
# Containers
clnt.api.get_container_by_name("Tenant")
clnt.api.add_container("DC1_LEAFS", parent_name, parent_key)

# Devices
clnt.api.get_device_by_name("leaf1")
clnt.api.get_all_devices()
clnt.api.move_device_to_container("label", device, container)

# Configlets
clnt.api.get_configlet_by_name("NTP-SERVERS")
clnt.api.add_configlet("name", "config body")
clnt.api.update_configlet("new body", configlet_key, "name")
clnt.api.apply_configlets_to_device("label", device, [configlet])
clnt.api.apply_configlets_to_container("label", container, [configlet])

# Tasks and Change Controls
clnt.api.execute_task(task_id)
clnt.api.create_change_control_v3(cc_id, cc_name, task_list)
clnt.api.approve_change_control(cc_id, timestamp=...)
clnt.api.execute_change_controls([cc_id])

# Compliance
clnt.post("/api/v3/services/compliancecheck.Compliance/GetConfigDiff", data=body)
```

---

## Workflow 8: Device Decommissioning

**Goal**: Remove a device from CloudVision inventory using the DeviceDecommissioningConfig API.

**Supported from**: CVP 2021.3.0+

### Pattern (REST)

```python
#!/usr/bin/env python3
"""
Decommission a device from CloudVision.

WARNING: This script modifies CloudVision state.
"""
import os
import uuid
import requests
import json


def decommission_device(cv_host: str, token: str, device_id: str) -> str:
    """
    Send a decommissioning request for a device.

    Args:
        cv_host: CloudVision host (IP or FQDN)
        token: Service account token
        device_id: Device serial number

    Returns:
        request_id: UUID of the decommissioning request (use to poll status)

    WARNING: This operation modifies CloudVision state.
    """
    request_id = str(uuid.uuid4())
    url = f"https://{cv_host}/api/resources/inventory/v1/DeviceDecommissioningConfig"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    payload = {
        "key": {"requestId": request_id},
        "deviceId": device_id,
    }

    response = requests.post(url, headers=headers, json=payload, verify=True)
    response.raise_for_status()
    return request_id


def poll_decommissioning_status(
    cv_host: str, token: str, request_id: str
) -> dict:
    """
    Poll the decommissioning status for a given request ID.

    Args:
        request_id: UUID returned by decommission_device()

    Returns:
        Status dict with 'status' and 'statusMessage' fields
    """
    url = f"https://{cv_host}/api/resources/inventory/v1/DeviceDecommissioning"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"key.requestId": request_id}

    response = requests.get(url, headers=headers, params=params, verify=True)
    response.raise_for_status()
    return response.json().get("value", {})


def main():
    cv_host = os.environ["CLOUDVISION_HOST"]
    token = os.environ["CLOUDVISION_ACCESS_TOKEN"]
    device_id = os.environ["DEVICE_SERIAL"]  # e.g., "BAD032986065E8DC14CBB6472EC314A6"

    # WARNING: Uncomment to execute decommissioning
    # request_id = decommission_device(cv_host, token, device_id)
    # print(f"Decommissioning request submitted: {request_id}")
    # status = poll_decommissioning_status(cv_host, token, request_id)
    # print(f"Status: {status.get('status')}")
    print("Decommissioning workflow ready. Uncomment to execute.")


if __name__ == "__main__":
    main()
```

---

## Workflow 9: gNMI and RESTCONF — Accessing OpenConfig Data

**Goal**: Access YANG-modeled device data (interfaces, BGP, counters, DOM…) and CVP-wide models via gNMI and RESTCONF through CloudVision.

### EOS and TerminAttr Configuration

```eos
! Enable gNMI on EOS
management api gnmi
   transport grpc default
   vrf management
!
daemon TerminAttr
   exec /usr/bin/TerminAttr \
     -cvaddr=192.0.2.100:9910 \
     -cvcompression=gzip \
     -cvauth=token,/tmp/token \
     -cvgnmi \
     -cvvrf=management \
     -smashexcludes=ale,flexCounter,hardware,kni,pulse,strata \
     -ingestexclude=/Sysdb/cell/1/agent,/Sysdb/cell/2/agent \
     -taillogs
   no shutdown
!
```

> **Note**: TerminAttr must use certificate-based auth (`-cvauth=token,...`) — ingestkey auth is not supported for gNMI streaming.

### gNMI with gnmi CLI

```bash
# Get interface admin-status for a device (STREAM)
gnmi -addr=192.0.2.100:443 -token=$(cat token.tok) \
  -mode=stream subscribe \
  origin=openconfig target=JPE17471528 \
  /interfaces/interface/state/admin-status

# Get CVP inventory (ONCE mode)
gnmi -addr=192.0.2.100:443 -token=$(cat token.tok) \
  -mode=once subscribe /inventory/state/device/device-id

# Historical snapshot at specific time
gnmi -addr=192.0.2.100:443 -token=$(cat token.tok) \
  -mode=once -history_snapshot=2024-01-15T09:47:00Z \
  subscribe origin=openconfig target=JPE17471508 \
  "/interfaces/interface[name=Ethernet47]/state/admin-status"

# Historical range
gnmi -addr=192.0.2.100:443 -token=$(cat token.tok) \
  -mode=stream \
  -history_start=2024-01-15T09:47:00Z \
  -history_end=2024-01-15T09:51:00Z \
  subscribe origin=openconfig target=JPE17471508 \
  "/interfaces/interface[name=Ethernet47]/state/admin-status"
```

### gNMI with gnmic

```bash
# Subscribe to interface counters (OpenConfig)
gnmic -a 192.0.2.100:443 \
  --mode=once subscribe \
  --path "openconfig:/interfaces/interface/state/counters" \
  --token=$CLOUDVISION_ACCESS_TOKEN \
  --gzip --skip-verify \
  --target=JPE17471528

# Get CVP inventory (arista origin, CVaaS)
gnmic -a www.arista.io:443 \
  --mode=once subscribe \
  --path /inventory/state/device/device-id \
  --token=$CLOUDVISION_ACCESS_TOKEN \
  --gzip
```

> **Note**: For CVP data via gnmic, use gnmic >= 0.17.0.

### gNMI with Python (pygnmi)

```python
#!/usr/bin/env python3
"""Query OpenConfig data via gNMI through CloudVision."""
import os
from pygnmi.client import gNMIclient

cv_host = os.environ["CLOUDVISION_HOST"]
token = os.environ["CLOUDVISION_ACCESS_TOKEN"]
device_sn = os.environ["DEVICE_SERIAL"]

with gNMIclient(
    target=(cv_host, 443),
    token=token,
    skip_verify=False,
) as gc:
    # Query interface admin-status for a specific device
    result = gc.get(
        path=["openconfig:/interfaces/interface/state/admin-status"],
        target=device_sn,
    )
    for notification in result.get("notification", []):
        for update in notification.get("update", []):
            print(f"{update['path']}: {update['val']}")
```

### RESTCONF

```python
#!/usr/bin/env python3
"""Access YANG data via RESTCONF through CloudVision."""
import os
import requests

cv_host = os.environ["CLOUDVISION_HOST"]
token = os.environ["CLOUDVISION_ACCESS_TOKEN"]
device_sn = os.environ["DEVICE_SERIAL"]

headers = {
    "Authorization": f"Bearer {token}",
    "Accept": "application/json",
}

# Get LLDP system-name for a device
url = f"https://{cv_host}/restconf/data/lldp/state/system-name"
resp = requests.get(
    url,
    headers=headers,
    params={"arista-target": device_sn, "arista-origin": "openconfig"},
    verify=True,
)
resp.raise_for_status()
print(resp.json())

# Get interface counters
url = f"https://{cv_host}/restconf/data/interfaces/interface/state/counters"
resp = requests.get(
    url,
    headers=headers,
    params={"arista-target": device_sn, "arista-origin": "openconfig"},
    verify=True,
)
resp.raise_for_status()
print(resp.json())

# Get CVP inventory
url = f"https://{cv_host}/restconf/data/inventory/state/device/device-id"
resp = requests.get(
    url,
    headers=headers,
    params={"arista-origin": "arista", "arista-target": ""},
    verify=True,
)
resp.raise_for_status()
print(resp.json())
```

---

## Workflow 10: Discovering NetDB Paths with the Connector

**Goal**: Understand how to find relevant NetDB paths and access raw/aggregated telemetry.

### NetDB Dataset Structure

The CloudVision Telemetry Browser organizes data into:

| Dataset Type | Datasets | Contents |
|---|---|---|
| **Active Devices** | One per device (serial number) | Raw streamed data: Sysdb, Kernel, NTP, Smash, Logs, Config, etc. |
| **Application Datasets** | `analytics` | Aggregated/versioned counters, BugAlerts, topology, inventory list |
| | `cvp` | Provisioning data: configlets, containers, tasks, change controls, users |
| | `files` | EOS images, extensions (fileserver) |
| **Configuration Datasets** | `AllDeviceConfig` | TerminAttr include/exclude list |
| **Archived Datasets** | Per removed device | Data for devices removed from provisioning |

### How to Find Paths

**Option 1: Dashboard modal view**
Go to any device dashboard (e.g., Traffic Counters), click any metric → the modal shows the Data Paths the UI is querying.

```
analytics: /Devices/BAD032986065E8DC14CBB6472EC314A6/versioned-data/interfaces/data/Ethernet1/rates
analytics: /Devices/BAD032986065E8DC14CBB6472EC314A6/versioned-data/interfaces/data/Ethernet1/aggregate/rates/1m
analytics: /Devices/BAD032986065E8DC14CBB6472EC314A6/versioned-data/interfaces/data/Ethernet1/aggregate/rates/15m
```

**Option 2: Metric Explorer** (Settings and Tools → Metric Explorer)
Search for a metric name — results show the dataset and path.

**Option 3: Telemetry Browser**
Browse paths manually starting from the dataset root.

### Connector Examples

```python
#!/usr/bin/env python3
"""Access NetDB data via CloudVision Connector."""
import os
from cloudvision.Connector.grpc_client import GRPCClient, create_query

cv_host = os.environ["CLOUDVISION_HOST"]
token = os.environ["CLOUDVISION_ACCESS_TOKEN"]
device_sn = os.environ["DEVICE_SERIAL"]


def get_interface_rates(
    cv_host: str,
    token: str,
    device_sn: str,
    interface: str = "Ethernet1",
) -> None:
    """Get raw interface rates from analytics dataset."""
    path_elts = [
        "Devices",
        device_sn,
        "versioned-data",
        "interfaces",
        "data",
        interface,
        "rates",
    ]
    query = [create_query([(path_elts, [])], "analytics")]

    with GRPCClient(f"{cv_host}:443", token=token) as client:
        for batch in client.get(query):
            for notif in batch["notifications"]:
                print(notif["updates"])


def get_1m_aggregate_rates(
    cv_host: str,
    token: str,
    device_sn: str,
    interface: str = "Ethernet1",
) -> None:
    """Get 1-minute aggregated rates."""
    path_elts = [
        "Devices",
        device_sn,
        "versioned-data",
        "interfaces",
        "data",
        interface,
        "aggregate",
        "rates",
        "1m",
    ]
    query = [create_query([(path_elts, [])], "analytics")]

    with GRPCClient(f"{cv_host}:443", token=token) as client:
        for batch in client.get(query):
            for notif in batch["notifications"]:
                print(notif["updates"])


def get_provisioning_data(cv_host: str, token: str) -> None:
    """Access CVP provisioning state from cvp dataset."""
    path_elts = ["DatasetInfo", "Devices"]
    query = [create_query([(path_elts, [])], "analytics")]

    with GRPCClient(f"{cv_host}:443", token=token) as client:
        for batch in client.get(query):
            for notif in batch["notifications"]:
                for key, val in notif["updates"].items():
                    print(f"{key}: {val}")


if __name__ == "__main__":
    get_interface_rates(cv_host, token, device_sn)
```

---

## Workflow 11: Testing APIs with gRPCurl

**Goal**: Use gRPCurl to explore and test CloudVision gRPC APIs without writing Python code.

### Setup

```bash
# Install gRPCurl (macOS)
brew install grpcurl

# Clone CloudVision API definitions
git clone https://github.com/aristanetworks/cloudvision-apis.git $GOPATH/src/github.com/cloudvision-apis
```

### Common Operations

```bash
# Variables
CV_HOST=192.0.2.100
TOKEN=$(cat token.tok)
PROTO_PATH=$GOPATH/src/github.com/cloudvision-apis
CERT=cvp.crt

# List all services for event.v1
grpcurl \
  -H "Authorization: Bearer $TOKEN" \
  -import-path $PROTO_PATH \
  -proto $PROTO_PATH/arista/event.v1/services.gen.proto \
  -cacert $CERT \
  $CV_HOST:443 list

# List methods of EventService
grpcurl \
  -H "Authorization: Bearer $TOKEN" \
  -import-path $PROTO_PATH \
  -proto $PROTO_PATH/arista/event.v1/services.gen.proto \
  -cacert $CERT \
  $CV_HOST:443 list arista.event.v1.EventService

# Describe the GetAll method signature
grpcurl \
  -H "Authorization: Bearer $TOKEN" \
  -import-path $PROTO_PATH \
  -proto $PROTO_PATH/arista/event.v1/services.gen.proto \
  -cacert $CERT \
  $CV_HOST:443 describe arista.event.v1.EventService.GetAll

# Describe EventStreamRequest message template
grpcurl -plaintext -msg-template \
  -H "Authorization: Bearer $TOKEN" \
  -import-path $PROTO_PATH \
  -proto $PROTO_PATH/arista/event.v1/services.gen.proto \
  -cacert $CERT \
  $CV_HOST:443 describe .arista.event.v1.EventStreamRequest

# Get all ERROR severity events
grpcurl \
  -H "Authorization: Bearer $TOKEN" \
  -import-path $PROTO_PATH \
  -proto $PROTO_PATH/arista/event.v1/services.gen.proto \
  -cacert $CERT \
  -d '{"partialEqFilter":[{"severity":"EVENT_SEVERITY_ERROR"}]}' \
  $CV_HOST:443 arista.event.v1.EventService/GetAll

# Describe EventSeverity enum
grpcurl \
  -H "Authorization: Bearer $TOKEN" \
  -import-path $PROTO_PATH \
  -proto $PROTO_PATH/arista/event.v1/services.gen.proto \
  -cacert $CERT \
  $CV_HOST:443 describe arista.event.v1.EventSeverity
```

> **Pro tip**: Add `GRPC_GO_LOG_VERBOSITY_LEVEL=99 GRPC_GO_LOG_SEVERITY_LEVEL=info` before your gRPCurl command for detailed trace logging.

> **Port note**: From CVP 2020.2.0 to 2021.2.x, the gRPC port was TCP 8443. From CVP 2021.3.0+, it is TCP 443.

---

## REST API: JSON Streaming

Resource API `GetAll` endpoints return **newline-delimited JSON** (a stream of JSON objects), not a single JSON array.

```python
import os
import requests

CV_HOST = os.environ["CLOUDVISION_HOST"]
CV_TOKEN = os.environ["CLOUDVISION_ACCESS_TOKEN"]

headers = {"Authorization": f"Bearer {CV_TOKEN}"}

# GetAll with server-side filter (partialEqFilter)
url = f"https://{CV_HOST}/api/resources/inventory/v1/Device/all"
payload = {"partialEqFilter": [{"streamingStatus": 2}]}  # STREAMING_STATUS_ACTIVE = 2

response = requests.post(url, headers=headers, json=payload, verify=True, stream=True)
response.raise_for_status()

devices = []
for line in response.iter_lines():
    if line:
        import json
        obj = json.loads(line)
        value = obj.get("result", {}).get("value", {})
        if value:
            devices.append(value)

print(f"Active streaming devices: {len(devices)}")
for device in devices:
    print(f"  {device.get('hostname', {}).get('value', 'unknown')}: {device['key']['deviceId']}")
```

---

## Legacy REST API: Pagination

For older `/cvpservice/` endpoints that use `startIndex`/`endIndex` pagination, use `concurrent.futures` for parallel fetching:

```python
import os
import math
import json
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

CV_HOST = os.environ["CLOUDVISION_HOST"]
CV_TOKEN = os.environ["CLOUDVISION_ACCESS_TOKEN"]

session = requests.Session()
session.headers.update({"Authorization": f"Bearer {CV_TOKEN}"})


def fetch_configlets_page(start: int, end: int) -> list[dict]:
    """Fetch a page of configlets."""
    url = f"https://{CV_HOST}/cvpservice/configlet/getConfiglets.do"
    params = {"startIndex": start, "endIndex": end, "type": "All"}
    resp = session.get(url, params=params, verify=True)
    resp.raise_for_status()
    data = resp.json()
    return data.get("data", [])


def get_all_configlets(page_size: int = 50) -> list[dict]:
    """Fetch all configlets using parallel pagination."""
    # First call to get total count
    url = f"https://{CV_HOST}/cvpservice/configlet/getConfiglets.do"
    resp = session.get(url, params={"startIndex": 0, "endIndex": 1, "type": "All"}, verify=True)
    total = resp.json().get("total", 0)

    if total == 0:
        return []

    # Build page ranges
    pages = [
        (i, min(i + page_size - 1, total - 1))
        for i in range(0, total, page_size)
    ]

    all_configlets = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(fetch_configlets_page, s, e): (s, e) for s, e in pages}
        for future in as_completed(futures):
            all_configlets.extend(future.result())

    return all_configlets


if __name__ == "__main__":
    configlets = get_all_configlets()
    print(f"Total configlets: {len(configlets)}")
```

---

## Error Handling Patterns

### Pattern 1: Basic gRPC Error Handling

```python
import grpc

try:
    response = stub.GetOne(request)
except grpc.RpcError as e:
    if e.code() == grpc.StatusCode.NOT_FOUND:
        print("Resource not found")
    elif e.code() == grpc.StatusCode.PERMISSION_DENIED:
        print("Permission denied - check service account permissions")
    elif e.code() == grpc.StatusCode.UNAUTHENTICATED:
        print("Authentication failed - check token validity")
    else:
        print(f"RPC failed: {e.code()} - {e.details()}")
```

### Pattern 2: Retry with Exponential Backoff

```python
import time
import grpc

def retry_rpc(func, max_retries=3, initial_delay=1.0):
    """Retry gRPC call with exponential backoff."""
    for attempt in range(max_retries):
        try:
            return func()
        except grpc.RpcError as e:
            if e.code() in (grpc.StatusCode.UNAVAILABLE, grpc.StatusCode.DEADLINE_EXCEEDED):
                if attempt < max_retries - 1:
                    delay = initial_delay * (2 ** attempt)
                    print(f"Retry {attempt + 1}/{max_retries} after {delay}s...")
                    time.sleep(delay)
                else:
                    raise
            else:
                raise
```

---

## Troubleshooting Guide

### Issue: "UNAUTHENTICATED" error

**Cause**: Invalid or expired service account token.

**Solution**:
1. Verify token in CloudVision: Settings → Access Control → Service Accounts
2. Check token expiration date
3. Regenerate token if expired
4. Verify `CLOUDVISION_ACCESS_TOKEN` environment variable is set correctly

### Issue: "PERMISSION_DENIED" when calling Set/Delete RPCs

**Cause**: Service account lacks write permissions.

**Solution**:
1. Check service account role in CloudVision
2. Ensure role has necessary permissions (e.g., `network-admin` for config changes)
3. Verify resource-level permissions if using custom roles

### Issue: "UNAVAILABLE" or connection timeout

**Cause**: Network connectivity issue or incorrect host/port.

**Solution**:
1. Verify `CLOUDVISION_HOST` resolves correctly
2. Check firewall rules allow HTTPS (443) to CloudVision
3. For on-prem: Verify CA certificate path is correct
4. Test with `curl https://<CV_HOST>:443/api/v3/services/arista.inventory.v1.DeviceService/GetAll`

### Issue: Certificate verification failed

**Cause**: CA certificate mismatch (on-prem only).

**Solution**:
1. Verify CA certificate file exists at specified path
2. Ensure certificate matches CloudVision instance
3. For CVaaS: Do NOT specify CA certificate (use default system CA bundle)

### Issue: "Field not found" or "unknown field" in Protobuf

**Cause**: Using wrong API version or field name.

**Solution**:
1. Check API documentation: https://aristanetworks.github.io/cloudvision-apis
2. Verify `cloudvision` package version matches CloudVision version
3. Inspect Protobuf definitions: `python -m grpc_tools.protoc --python_out=. --grpc_python_out=. <proto_file>`

---

## REST API Examples

### Example 1: Get All Devices (REST with JSON Streaming)

```python
import os
import json
import requests

CV_HOST = os.environ["CLOUDVISION_HOST"]
CV_TOKEN = os.environ["CLOUDVISION_ACCESS_TOKEN"]

url = f"https://{CV_HOST}/api/resources/inventory/v1/Device/all"
headers = {"Authorization": f"Bearer {CV_TOKEN}"}

# NOTE: GetAll returns newline-delimited JSON (stream of dicts, not a single array)
response = requests.get(url, headers=headers, verify=True, stream=True)
response.raise_for_status()

devices = []
for line in response.iter_lines():
    if line:
        obj = json.loads(line)
        value = obj.get("result", {}).get("value")
        if value:
            devices.append(value)

print(f"Total devices: {len(devices)}")
```

### Example 2: Query Events with Filters (REST)

```python
import os
import requests
from datetime import datetime, timedelta, timezone

CV_HOST = os.environ["CLOUDVISION_HOST"]
CV_TOKEN = os.environ["CLOUDVISION_ACCESS_TOKEN"]

url = f"https://{CV_HOST}/api/resources/event/v1/Event/all"
headers = {"Authorization": f"Bearer {CV_TOKEN}"}

# Filter: critical severity
params = {
    "key.severity": "EVENT_SEVERITY_CRITICAL",
}

response = requests.get(url, headers=headers, params=params, verify=True)
response.raise_for_status()

events = response.json()
print(f"Critical events: {len(events.get('result', {}).get('value', []))}")
```

---

## Production Best Practices

### 1. Connection Management

- **Reuse gRPC channels** across multiple RPC calls
- **Use context managers** (`with` statements) to ensure cleanup
- **Set reasonable deadlines** for long-running operations:

```python
stub.GetAll(request, timeout=30.0)  # 30 second deadline
```

### 2. Streaming Efficiency

- **Use `GetAll` streaming** instead of multiple `GetOne` calls
- **Batch writes** with `SetSome` instead of multiple `Set` calls
- **Process stream in chunks** to avoid memory exhaustion

### 3. Error Recovery

- **Implement retry logic** for transient failures (UNAVAILABLE, DEADLINE_EXCEEDED)
- **Log gRPC status codes** and details for debugging
- **Gracefully handle NOT_FOUND** for optional resources

### 4. Security

- **Never log tokens** — mask in log output
- **Use environment variables** for credentials, not hardcoded values
- **Rotate service account tokens** regularly
- **Use least-privilege roles** for service accounts

### 5. Performance Optimization

- **Filter at the API level** using `partial_eq_filter` instead of client-side filtering
- **Use async clients** for I/O-bound workloads
- **Parallelize independent RPC calls** with asyncio

---

## Complete API Domain Reference

Extended domain list with additional details:

| Domain | Key Resources | Common Use Cases |
|--------|---------------|------------------|
| `inventory.v1` | Device, DeviceStatus | Device discovery, hardware inventory |
| `event.v1` | Event, EventAnnotation | Event monitoring, alert correlation |
| `changecontrol.v1` | ChangeControl, ChangeControlApproval | Automated change management |
| `configlet.v1` | Configlet, ConfigletAssignment | Configuration template management |
| `configstatus.v1` | ConfigStatus, Summary | Config compliance checking |
| `workspace.v1` | Workspace, WorkspaceConfig | Staged configuration workflows |
| `tag.v2` | Tag, DeviceTag, InterfaceTag | Device categorization, RBAC |
| `studio.v1` | Studio, StudioConfig | Custom topology views |
| `studio_topology.v1` | TopologyEdge, TopologyNode | Network topology visualization |
| `connectivitymonitor.v1` | Probe, ProbeStatus | Path tracing, reachability tests |
| `dashboard.v1` | Dashboard, Widget | Custom monitoring dashboards |
| `lifecycle.v1` | DeviceLifecycleSummary | EOS EOL tracking |
| `alert.v1` | Rule, AlertCondition | Proactive alerting configuration |
| `serviceaccount.v1` | AccountConfig, Token | Service account automation |
| `softwaremanagement.v1` | ImageBundle, UpgradeTask | EOS upgrade orchestration |
| `imagestatus.v1` | ImageStatus, ImageInfo | Running vs designed image comparison |
| `endpointlocation.v1` | Endpoint, Location | MAC address tracking |
| `bugexposure.v1` | BugExposure, BugDetail | Known bug impact analysis |
| `syslog.v1` | Syslog, SyslogConfig | Centralized syslog collection |
| `action.v1` | Action, ActionStatus | Change control action tracking |
| `auditlog.v1` | AuditEvent | Compliance audit trail |
| `license.v1` | License, EntitlementSummary | License management |

---

# Resources

- [CloudVision API Documentation](https://aristanetworks.github.io/cloudvision-apis)
- [CloudVision Python Library Docs](https://aristanetworks.github.io/cloudvision-python/)
- [CloudVision Examples Repository](https://github.com/arista-netdevops-community/CloudVisionPortal-Examples)
- [Python Client Source](https://github.com/aristanetworks/cloudvision-python)
- [Go Client Source](https://github.com/aristanetworks/cloudvision-go)
- [gRPC Python Documentation](https://grpc.io/docs/languages/python/)
- [cvprac Library](https://github.com/aristanetworks/cvprac)
- [cvprac Lab Examples](https://github.com/aristanetworks/cvprac/tree/develop/docs/labs)
- [ansible-cvp Collection](https://cvp.avd.sh)
- [ansible-avd Collection](https://avd.sh)
- [OpenMGMT (gNMI/OpenConfig)](https://aristanetworks.github.io/openmgmt/)
- [gRPCurl](https://github.com/fullstorydev/grpcurl)
- [gnmic](https://gnmic.openconfig.net/)
- [cvp-events-pubsub (Kafka demo)](https://github.com/arista-netdevops-community/cvp-events-pubsub)
- [cvp-to-influx (InfluxDB demo)](https://github.com/arista-netdevops-community/cvp-to-influx)

