---
name: browser_qa_tester
description: Sovereign runbook for Canvas UI end-to-end automation, IPC event verification, headless browser QA, and visual regression defense
keywords: ["browser qa", "canvas ui testing", "headless browser", "puppeteer", "playwright", "e2e testing", "visual regression", "ui automation", "dom inspection", "click automation", "screenshot testing", "browser console errors", "network inspection", "form submission test", "element locator", "web regression", "integration testing", "session validation", "page load audit", "cross-browser testing"]
---
# 🌐 SKILL: BROWSER QA TESTER & CANVAS HARNESS

Prosedur Operasi Standar (SOP) resmi kedaulatan Flowork OS untuk pengujian antarmuka antarmuka Canvas UI, verifikasi event bridge IPC, dan kendali mutu visual.

## 1. DOKTRIN PENGUJIAN CANVAS & BROWSER
1. **Mandatori Visual QC Empiris**:
   - Setiap penggarapan komponen antarmuka, CSS layout, Canvas split-view, atau modal dialog wajib mengambil bukti tangkapan layar nyata via native tool `flow_screenshot`.
   - Haram mengklaim tampilan UI selesai tanpa bukti visual pixel nyata.

2. **Standar Bahasa Global Antarmuka (English-Only UI)**:
   - Antarmuka Canvas UI, label tombol, menu bar, header tab, dan modal HARAM berbahasa Indonesia.
   - Wajib 100% menggunakan Bahasa Inggris formal dan ringkas.

3. **Verifikasi Event Bridge & Komunikasi IPC**:
   - Seluruh interaksi iframe Canvas dengan backend plugin wajib menggunakan event message terstruktur (`window.postMessage` / REST endpoint port dinamis).
   - Pastikan backend merespon payload tanpa error status 500 dan mematuhi skema JSON yang didefinisikan di `plugin.manifest.json`.

4. **Headless & Console Sanity Check**:
   - Pastikan tidak ada `Uncaught TypeError`, CSP violation, atau syntax error pada console log antarmuka web.
   - Seluruh asset (CSS, fonts, JS modul) wajib dimuat menggunakan jalur relatif atau native gateway CDN. Dilarang menggunakan jalur absolut lokal mesin operator.

## 2. PANDUAN PENGUJIAN OTOMASI
1. Pastikan server backend plugin aktif dan mendengarkan port lingkungan (`process.env.PORT` / `process.env.FLOWORK_APP_PORT`).
2. Uji respon endpoint menggunakan curl atau skrip harness di `.FL_BIN/`.
3. Buka plugin di Canvas menggunakan `plugin_control(action: 'open', plugin_id: '<id>')`.
4. Ambil screenshot visual verifikasi dan pastikan render elemen sempurna.
