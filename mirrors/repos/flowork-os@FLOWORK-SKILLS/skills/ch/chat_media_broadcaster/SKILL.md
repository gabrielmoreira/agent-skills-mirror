---
name: chat_media_broadcaster
description: Sovereign runbook for dispatching rich media, HTML5 video previews, and interactive artifacts to canvas chat
keywords: ["chat media", "media broadcast", "send_media", "inline image", "audio broadcast", "multimodal chat", "media streaming", "chat attachment", "canvas media", "rich messaging", "embedded player", "visual broadcast", "chat payload", "image preview", "waveform render", "audio player", "video player", "media pipeline", "interactive card", "multimodal ui"]
---
# 🛠️ SKILL: CHAT MEDIA BROADCASTER & EMBED DISPATCHER
*Diadaptasi untuk tool Flowork:* `send_media` | *Referensi:* ECC Content Engine & Media Streaming

Prosedur Operasi Standar (SOP) resmi kedaulatan Flowork OS untuk mengirim media interaktif ke obrolan.

## 1. DOKTRIN PENGIRIMAN MEDIA
- **Format Ramah Browser**: Utamakan MP4 (H.264), WebM, PNG, atau SVG yang langsung dapat di-render oleh native HTML5 video player canvas.
- **Path Resolution Dinamis**: Pastikan file media dapat diakses oleh webview tanpa memicu CORS atau path 404.
