# Port Registry - sm-buttonpusher

## Frontend

| Service | Port | Notes |
|---------|------|-------|
| None (ESP-IDF firmware) | — | No frontend application |

## Backend / Device Interfaces

| Service | Interface | Notes |
|---------|-----------|-------|
| UART/USB Console | Serial | Primary debug and configuration interface |
| BLE Provisioning | Bluetooth LE | Wireless device provisioning |

## Shared External Dependencies

| Service | Port/Value | Notes |
|---------|------------|-------|
| PostgreSQL (shared) | 5432 | For test data via web-hmi API |