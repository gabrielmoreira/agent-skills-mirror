---
name: audio_dsp_mixing_master
description: Sovereign runbook for digital audio processing, LUFS loudness compliance, EQ frequency carving, multi-band dynamics, and clean master output
keywords: ["audio dsp", "audio mixing", "mastering", "lufs", "equalizer", "compressor", "loudness normalization", "stem mastering", "frequency carving", "acoustic balance", "limiter", "audio processing", "gain staging", "clipping prevention", "stereo imaging", "spectral analysis", "dynamic range", "headroom management", "sound design", "audio filter"]
---
# 🎵 SKILL: AUDIO DSP MIXING & MASTERING ENGINEER
*Diadaptasi dari repositori dunia & standar industri audio-visual:* `EBU R128 / ITU-R BS.1770 Loudness Standards & Professional DAW DSP Pipelines`

Prosedur Operasi Standar (SOP) resmi kedaulatan Flowork OS untuk pemrosesan sinyal audio digital (DSP), mixing multi-track, standarisasi loudness, dan mastering bebas clipping:

## 1. DOKTRIN MIXING & STANDARISASI LOUDNESS
- **Kepatuhan Target Loudness (Loudness Rigor)**:
  - Master Streaming (YouTube, Spotify, Canvas Video): -14 LUFS Integrated (±1 LUFS) dengan True Peak maksimal -1.0 dBTP.
  - Master Video Pendek (Shorts / Reels): -11 hingga -13 LUFS Integrated untuk kejernihan di perangkat mobile.
  - Haram menghasilkan audio dengan inter-sample peaks atau digital clipping (> 0.0 dBFS).

- **Pembersihan Frekuensi (Frequency Carving & EQ)**:
  - High-Pass Filter (Low-Cut): Potong frekuensi sampah di bawah 30-35 Hz pada instrumen non-sub-bass.
  - Voice Clarity: Berikan ruang 2 kHz - 5 kHz untuk artikulasi vokal/dialog agar tidak tenggelam oleh instrumen pengiring.
  - Anti-Mud: Bersihkan penumpukan frekuensi kotor di rentang 250 Hz - 400 Hz.

- **Dynamic Range & Brickwall Limiting**:
  - Gunakan kompresi multi-tahap (gentle glue compressor 1-2 dB GR) sebelum masuk ke final limiter.
  - Pastikan dynamic contrast tetap hidup tanpa over-squashed (*loudness war fatigue*).
