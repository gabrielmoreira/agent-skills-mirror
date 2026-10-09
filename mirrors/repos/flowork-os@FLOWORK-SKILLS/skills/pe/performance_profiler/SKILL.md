---
name: performance_profiler
description: Sovereign runbook for detecting memory leaks, CPU thread bottlenecks, and empirical optimization loops
keywords: ["performance profiler", "profiling", "benchmark", "memory leak", "cpu bottleneck", "flamegraph", "latency optimization", "throughput analysis", "allocations audit", "garbage collection tuning", "execution timing", "system performance", "io wait profiling", "cache misses", "hotspot detection", "memory heap snapshot", "concurrency bottleneck", "profiler report", "optimization pass", "runtime efficiency"]
---
# ⚙️ SKILL: PERFORMANCE PROFILER & V8 BOTTLENECK HUNTER
*Diadaptasi dari repositori dunia:* `affaan-m/ECC/skills/benchmark-optimization-loop (274k★) & V8 Memory Inspector`

Prosedur Operasi Standar (SOP) resmi kedaulatan Flowork OS untuk membedah bottleneck performa sistem, memory leak, dan efisiensi eksekusi V8:

## 1. DOKTRIN PENGUKURAN & OPTIMISASI PERFORMA
- **Baseline First (Haram Optimasi Tanpa Alat Ukur)**:
  - Dilarang melakukan optimasi buta sebelum mengukur baseline (`performance.now()`, CPU time, RAM delta).
  - Catat metrik sebelum vs sesudah: latency p95, memory footprint (RSS / HeapUsed), dan wall clock time.

- **Deteksi V8 Memory Leak**:
  - Periksa event listener yang tidak dilepas (`removeEventListener` / `emitter.off`).
  - Hati-hati dengan closure yang menahan referensi objek besar dan global Map/Cache yang tidak memiliki batas pembersihan (gunakan `WeakMap` atau LRU cache terikat batas).

- **Non-Blocking Event Loop**:
  - Proses intensif komputasi (parsing file besar, hash biner, image manipulation) wajib dipecah menjadi batch atau dialihkan ke Worker Thread / subprocess background agar tidak memblokir UI Canvas Flowork.
