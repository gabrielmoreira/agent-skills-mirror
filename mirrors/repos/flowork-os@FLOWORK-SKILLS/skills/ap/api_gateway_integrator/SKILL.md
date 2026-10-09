---
name: api_gateway_integrator
description: Sovereign runbook for RESTful and gRPC API contract design, Bearer auth validation, rate limiting token bucket algorithms, and resilient webhook retries
keywords: ["api gateway", "restful api", "grpc schema", "openapi spec", "rate limiting", "token bucket", "bearer token", "oauth2 jwt", "webhook retry", "hmac signature", "input validation", "zod schema", "pydantic model", "reverse proxy routing", "api idempotency", "circuit breaker http", "cors policy", "status code contract", "payload sanitization", "api monitoring"]
---

# ⚙️ SKILL: API GATEWAY INTEGRATOR

## 1. Intent & Trigger Boundaries
- **Intent**: Perancangan kontrak antarmuka API (REST, gRPC, Webhook), otentikasi JWT/Bearer, validasi skema input data ketat, algoritma rate limiting, dan mekanisme webhook delivery dengan retry backoff.
- **Trigger**: Diminta merancang route API backend, membuat integrasi webhook aman (HMAC verification), menerapkan throttling/rate limiting, mendesain skema OpenAPI/Swagger, atau menstandarkan respon error HTTP.
- **Boundaries**: Tidak mengurusi arsitektur persistent streaming duplex WebSocket (gunakan `websocket_realtime_architect`). Fokus pada request-response HTTP/REST, RPC, dan event webhooks.

## 2. Standard Operating Procedures (SOP)
1. **Contract-First & Schema Validation**:
   - Terapkan validasi runtime ketat pada setiap request body, header, dan query param menggunakan schema validator (Zod, Pydantic, atau Joi).
   - Seluruh endpoint wajib mengembalikan response JSON konsisten: `{ "success": boolean, "data": ..., "error": { "code": string, "message": string } }`.
2. **Authentication & Authorization Guard**:
   - Validasi Authorization Header (`Bearer <token>`) di middleware terpusat sebelum mencapai business logic handler.
   - Periksa validitas signature JWT, expiration timestamp (`exp`), issuer (`iss`), dan roles/claims tanpa melakukan DB lookup berulang jika stateless.
3. **Rate Limiting & Abuse Defense**:
   - Terapkan rate limiter berbasis IP atau User ID menggunakan algoritma Token Bucket atau Sliding Window Counter.
   - Kembalikan HTTP Status `429 Too Many Requests` disertai header standar `Retry-After`, `X-RateLimit-Limit`, dan `X-RateLimit-Remaining`.
4. **Secure Webhook Delivery & Idempotency**:
   - Webhook yang diterima WAJIB diverifikasi integritasnya via cryptographic signature HMAC SHA-256 (`x-hub-signature-256`).
   - Webhook outgoing WAJIB mendukung header idempotency (`Idempotency-Key`) dan sistem retry exponential backoff dengan jitter saat target merespons non-2xx.

## 3. Strict Prohibitions & Edge Cases
- **PROHIBITION**: Dilarang mengembalikan internal stack trace sistem atau kredensial database pada respon HTTP error 500 ke klien publik.
- **PROHIBITION**: Dilarang menerima webhook tanpa validasi timestamp (replay attack prevention) atau tanpa validasi HMAC secret signature.
- **EDGE CASE**: Payload webhook sangat besar yang memicu timeout: segera kembalikan respon HTTP `202 Accepted` dan proses payload secara asinkron di worker queue.

## 4. Verification & Exit Code 0 Proof
- Schema Validation Test: Validasi skema input lolos unit test (`npm test` atau `pytest`) dengan exit code 0.
- HMAC Verification Test: Test suite menguji signature valid sukses dan menolak tamper request dengan status 401/403.
- Rate Limiting Test: Simulasi load burst menerima 429 setelah ambang batas terlampaui dan pulih sesuai header Retry-After.
