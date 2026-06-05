# Port Registry - device

## Frontend

| Service | Port | Notes |
|---------|------|-------|
| None (firmware-only) | — | No frontend application |

## Backend / Device Interfaces

| Service | Interface | Notes |
|---------|-----------|-------|
| UART/USB Console | Serial | Primary debug and configuration interface |
| BLE Provisioning | Bluetooth LE | Wireless device provisioning (ESP32 only) |
| SPIFFS Storage | Filesystem | Firmware binary storage on ESP32 |

## Shared External Dependencies

| Service | Port/Value | Notes |
|---------|------------|-------|
| PostgreSQL (shared) | 5432 | For OTA metadata via web-hmi API |