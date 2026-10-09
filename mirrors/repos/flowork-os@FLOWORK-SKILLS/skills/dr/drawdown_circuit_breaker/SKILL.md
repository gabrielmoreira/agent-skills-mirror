---
name: drawdown_circuit_breaker
description: Sovereign runbook for portfolio drawdown limits, streak cooldowns, daily loss caps, and capital preservation circuit breakers
keywords: ["drawdown circuit breaker", "trading risk management", "stop loss", "portfolio protection", "max drawdown", "risk limits", "capital preservation", "position sizing", "margin call defense", "volatility halt", "equity curve filter", "daily loss limit", "trailing stop", "exposure control", "account ruin prevention", "risk per trade", "emergency liquidation", "kill switch trading", "var analysis", "disciplined exits"]
---
# 📊 SKILL: DRAWDOWN CIRCUIT BREAKER & PORTFOLIO RISK CONTROLLER
*Diadaptasi dari repositori dunia:* `tradermonty/claude-trading-skills/skills/drawdown-circuit-breaker`

Prosedur Operasi Standar (SOP) resmi kedaulatan Flowork OS untuk penegakan batas penurunan ekuitas (*drawdown limits*), rem darurat modal, dan preservasi kapital:

## 1. DOKTRIN REM DARURAT PORTOFOLIO (CIRCUIT BREAKER)
- **Hierarki Batas Kerugian Bertingkat (Loss Caps)**:
  - **Daily Loss Cap (Maks 2-3% Ekuitas)**: Jika kerugian terealisasi harian menyentuh batas, seluruh aktivitas trade baru HARI ITU DIBEKUKAN (HALTED).
  - **Weekly Drawdown Cap (Maks 5% Ekuitas)**: Mengurangi ukuran posisi (size down) sebesar 50% untuk minggu berikutnya.
  - **Maximum Portfolio Drawdown (Maks 10% Ekuitas)**: Pembekuan total akun, penutupan sisa posisi berisiko tinggi, dan evaluasi ulang komprehensif sistem strategi.

- **Losing Streak Cooldown Trigger**:
  - Jika terjadi 3 kekalahan berturut-turut: Wajib berhenti minimal 24 jam untuk menetralkan bias psikologis.
  - Setiap order baru wajib ditolak secara otomatis oleh gate sistem hingga masa cooldown berakhir.

- **Ledger Realized P&L Tracker**:
  - Menghitung drawdown murni berbasis *realized P&L* dari riwayat ledger transaksi tanpa mengandalkan floating unrealized yang bias.
