---
name: crypto_scam_honeypot_hunter
description: Sovereign runbook for detecting smart contract honeypots, hidden sell taxes, mint backdoors, and rugpull indicators
keywords: ["crypto scam", "honeypot hunter", "smart contract audit", "rugpull detection", "solana scan", "evm honeypot", "token security", "malicious contract", "sell tax simulation", "blacklisted transfer", "liquidity lock audit", "proxy contract trap", "reentrancy attack", "drainer detection", "fake token detector", "bytecode analysis", "dex trade simulation", "on-chain audit", "scam token warning", "wallet safety"]
---
# 📊 SKILL: CRYPTO SCAM & HONEYPOT HUNTER
*Diadaptasi dari repositori dunia:* `malvaphe/Crypto_Honeypot_Detector & DevSwanson/how-to-create-honeypot-token (Deconstruction)`

Prosedur Operasi Standar (SOP) resmi kedaulatan Flowork OS untuk membedah smart contract, mendeteksi token penipuan (*honeypot*), dan mitigasi jebakan likuiditas (*rugpull*):

## 1. DOKTRIN AUDIT KONTRAK ANTI-HONEYPOT
- **Simulasi Transaksi Jual-Beli (Buy/Sell Simulation)**:
  - Verifikasi kemampuan token untuk dijual kembali via simulasi RPC (`eth_call` / dry-run DEX pair).
  - Jika simulasi jual menghasilkan *revert* atau pesan kegagalan (misal: "TransferHelper: TRANSFER_FAILED" / blacklisted), token berstatus **HONEYPOT_FATAL**.

- **Inspeksi Struktur Fee & Hidden Taxes**:
  - Cek persentase pajak jual (Sell Tax). Jika > 10% atau variabel fee dapat dinaikkan hingga 100% oleh owner tanpa batas (*unbounded fee modifier*), tandai sebagai risiko tinggi penipuan.
  - Audit mekanisme `_maxTxAmount` atau cooldown transfer buatan yang sengaja dirancang menahan pembeli agar tidak bisa keluar.

- **Indikator Rugpull & Likuiditas**:
  - Status LP Lock: Pastikan likuiditas DEX (Uniswap/Raydium) terkunci di locker tepercaya (PinkSale, Unicrypt, Burned LP).
  - Hak Akses Privileged: Deteksi fungsi minting tanpa batas (`mint()`), pause transfer semena-mena (`pause()`), atau kepemilikan kontrak yang belum di-renounce (`transferOwnership`).
