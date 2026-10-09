---
name: websocket_realtime_architect
description: Sovereign runbook for bidirectional WebSocket architectures, heartbeat ping-pong protocols, reconnection exponential backoff, SSE, and Pub/Sub routing
keywords: ["websocket architect", "realtime communication", "bidirectional socket", "heartbeat ping pong", "reconnection backoff", "server sent events", "pubsub message broker", "socket multiplexing", "channel subscription", "connection pooling", "backpressure control", "websocket handshake", "binary frame transfer", "socket state machine", "disconnect handling", "cross origin socket", "realtime presence", "broadcast message", "room based dispatch", "low latency event"]
---

# ⚙️ SKILL: WEBSOCKET REALTIME ARCHITECT

## 1. Intent & Trigger Boundaries
- **Intent**: Arsitektur komunikasi dua arah real-time berlatensi rendah menggunakan WebSockets (RFC 6455) atau Server-Sent Events (SSE), manajemen heartbeat ping-pong, rekoneksi tangguh, dan pola pub/sub per room/channel.
- **Trigger**: Diminta membangun komunikasi live telemetry, chat server real-time, terminal stream duplex, sinkronisasi state UI kanvas secara instan, atau menangani koneksi socket yang sering terputus (reconnection handling).
- **Boundaries**: Tidak mengurusi RESTful request-response stateless biasa (gunakan `api_gateway_integrator`). Fokus pada persistent full-duplex TCP socket connections dan streaming state.

## 2. Standard Operating Procedures (SOP)
1. **Handshake & Protocol Verification**:
   - Validasi HTTP Upgrade header (`Upgrade: websocket`, `Connection: Upgrade`) dan Sec-WebSocket-Key.
   - Autentikasi sesi klien saat proses jabat tangan awal (via query token, subprotocol auth, atau cookie valid) sebelum upgrade koneksi diterima.
2. **Heartbeat & Zombie Connection Pruning**:
   - Implementasikan protokol heartbeat deterministik: server mengirim Frame `Ping` berkala (misal tiap 30 detik) dan klien wajib membalas `Pong`.
   - Jika `Pong` tidak diterima dalam interval toleransi (misal 10 detik), tandai koneksi sebagai zombie, panggil `.terminate()`, dan bebaskan resource memori.
3. **Client-Side Reconnection with Exponential Backoff**:
   - Klien WebSocket dilarang melakukan reconnect seketika secara agresif saat putus.
   - Wajib gunakan algoritma Exponential Backoff disertai random jitter: `delay = min(max_delay, base * 2^retry_count) + random_jitter`.
4. **Channel & Room Pub/Sub Multiplexing**:
   - Strukturkan frame pesan JSON terstandar: `{ "event": string, "channel": string, "payload": any, "trace_id": string }`.
   - Gunakan arsitektur event emitter internal atau Redis Pub/Sub untuk mendistribusikan broadcast antar instans node.

## 3. Strict Prohibitions & Edge Cases
- **PROHIBITION**: Dilarang membiarkan klien WebSocket terus terhubung tanpa mekanisme deteksi heartbeat mati (dead connection leak).
- **PROHIBITION**: Dilarang mem-broadcast data mentah tanpa sanitasi channel subscription (risiko kebocoran data antar tenant).
- **EDGE CASE**: Backpressure socket: jika klien lambat mengonsumsi paket buffer output socket, terapkan throttling atau drop message non-kritis agar RAM server tidak meledak (OOM).

## 4. Verification & Exit Code 0 Proof
- Ping-Pong Loop Test: Unit test membuktikan frame ping direspons pong dan timeout memicu pemutusan socket secara bersih.
- Reconnect Test: Simulasi network severance membuktikan client mencoba rekoneksi dengan interval waktu bertahap (backoff) dan sukses pulih.
- Concurrency Soak Test: Uji muatan ratusan simulasi koneksi socket aktif dengan nol unhandled error dan exit code 0.
