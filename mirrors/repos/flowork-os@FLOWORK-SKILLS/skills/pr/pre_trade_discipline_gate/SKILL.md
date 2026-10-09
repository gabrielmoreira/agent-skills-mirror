---
name: pre_trade_discipline_gate
description: Sovereign runbook for pre-trade checklist gating, revenge trade prevention, risk-reward verification, and offline execution rigor
keywords: ["pre trade discipline", "trading gatekeeper", "risk reward ratio", "trade checklist", "emotional trading defense", "order execution gate", "trade validation", "fomo blocker", "position sizing checklist", "trading rules verification", "setup confirmation", "technical analysis gate", "risk parameters check", "stop loss mandatory", "trading journal precheck", "leverage constraint", "market condition filter", "disciplined entry", "trading plan compliance", "overtrading defense"]
---
# 📊 SKILL: PRE-TRADE DISCIPLINE GATE & ORDER AUDITOR
*Diadaptasi dari repositori dunia:* `tradermonty/claude-trading-skills/skills/pre-trade-discipline-gate`

Prosedur Operasi Standar (SOP) resmi kedaulatan Flowork OS untuk verifikasi gerbang disiplin pra-transaksi trading, audit posisi, dan pencegahan emosi trading (*anti-revenge trading*):

## 1. DOKTRIN GERBANG PRA-TRADING (DISCIPLINE GATE)
- **Mandatori Checklist Tertulis**:
  - Setiap keputusan eksekusi order (saham, crypto, forex) WAJIB lolos verifikasi 5 poin wajib:
    1. **Written Plan**: Setup terdefinisi jelas dalam trading plan (bukan impulsif melihat candle bergerak).
    2. **Predefined Stop-Loss**: Level proteksi modal dan cut-loss sudah ditetapkan sebelum entry.
    3. **Position Sizing Sesuai Batas**: Risiko modal per transaksi maksimal 1% - 2% dari total ekuitas.
    4. **Risk-to-Reward Ratio (RRR)**: Minimal 1:2 atau 1:3; tolak transaksi dengan RRR di bawah 1:1.5.
    5. **Market Regime Alignment**: Konfirmasi bahwa tren market utama (macro) searah dengan arah posisi (kecuali setup contrarian teruji).

- **Pencegahan Revenge Trading (Cooldown Lock)**:
  - Setelah mengalami kerugian berturut-turut (losing streak), aktifkan jendela waktu cooldown wajib sebelum membuka posisi baru.
  - Dilarang memperbesar ukuran lot/kontrak untuk "membalas" kekalahan sebelumnya.

- **Offline Gating Log**:
  - Catat seluruh evaluasi pra-trade ke artefak log `pre_trade_decision.json` sebelum order diteruskan ke platform broker/exchange.
