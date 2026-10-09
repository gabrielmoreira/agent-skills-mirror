---
name: protocol_reverse_engineer
description: Sovereign runbook for network wire protocol reverse engineering, packet schema recovery, clean-room IPC reconstruction, and interoperability design
keywords: ["protocol reverse engineering", "packet analysis", "wire format decoding", "clean room design", "binary schema recovery", "pcap dissection", "network protocol specification", "ipc protocol reverse", "tlv framing", "byte stream deserialization", "state machine recovery", "hex payload inspection", "custom protocol decoder", "reverse engineering runbook", "interoperability specification", "protocol fuzzing preparation", "endianness handling", "header parsing", "undocumented api recovery", "wire protocol modeling"]
---
# 🔬 SKILL: PROTOCOL REVERSE ENGINEER

Prosedur Operasi Standar (SOP) resmi kedaulatan Flowork OS untuk reverse engineering protokol komunikasi data, analisis format biner kawat (wire format), dan rekonstruksi antarmuka *clean-room*:

## 1. Intent & Trigger Boundaries
- **Pemicu**: Interoperabilitas sistem dengan protokol tertutup tanpa dokumentasi, decoding payload biner/hex kustom, pemulihan skema IPC, dan migrasi arsitektur legacy.
- **Batasan**: Ditujukan eksklusif untuk interoperabilitas perangkat lunak, dokumentasi format kawat, dan implementasi clean-room berdaulat. Dilarang digunakan untuk pembobolan DRM atau malware reverse engineering.

## 2. Standard Operating Procedures (SOP)
1. **Traffic Capture & Isolation**:
   - Isolasi aliran data jaringan atau IPC menggunakan instrumen packet capture (`tcpdump`, Wireshark, atau Unix domain socket dump).
   - Filter sesi spesifik untuk memisahkan handshake, stream sinkronisasi, dan termination packets.
2. **Framing & Delimiter Identification**:
   - Identifikasi struktur frame: Magic bytes, Header length, Type-Length-Value (TLV), sequence counter, payload boundary, dan trailer (CRC/checksum).
   - Analisis byte order (Big-Endian vs Little-Endian) serta skema serialisasi (Protobuf, MessagePack, CBOR, atau raw struct).
3. **State Machine Modeling**:
   - Petakan alur request-response dan transisi status (Handshake -> Authentication -> Ready -> Streaming -> Ping/Pong -> Teardown).
   - Catat respon terhadap invalid packet untuk memahami batasan validasi server/client.
4. **Clean-Room Specification & Parser Crafting**:
   - Susun spesifikasi format data formal dalam dokumen netral tanpa menyertakan kode biner proprietary.
   - Buat parser nano-modular yang tahan terhadap malformed input dengan validasi batas buffer ketat.

## 3. Strict Prohibitions & Edge Cases
- **Dilarang**: Menyertakan biner proprietary atau melanggar hak cipta kode asli dalam dokumentasi clean-room.
- **Buffer Overflow Defense**: Wajib pastikan parser memeriksa panjang buffer sebelum membaca byte payload untuk mencegah buffer over-read/out-of-bounds error.

## 4. Verification & Exit Code 0 Proof
- Uji parser dengan replay paket valid dan malformed packet dummy.
- Parser wajib mendecode byte stream secara deterministik tanpa crash (Exit Code 0).
