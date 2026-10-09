---
name: wallet_aml_risk_scanner
description: Sovereign runbook for multi-chain wallet risk scoring, AML screening, sanctioned entity/mixer tracing, and phishing drainer detection
keywords: ["wallet aml", "aml risk scanner", "blockchain forensics", "tainted address", "crypto compliance", "on-chain tracking", "wallet transaction audit", "ofac sanctioned list", "mixer interaction scan", "tornado cash exposure", "suspicious fund flow", "crypto risk scoring", "know your transaction", "on-chain clustering", "illicit activity detection", "wallet counterparty risk", "forensic analysis crypto", "token flow tracing", "sanction screening", "crypto provenance"]
---
# 📊 SKILL: WALLET AML RISK SCANNER & PHISHING DRAINER DETECTOR
*Diadaptasi dari repositori dunia:* `Soniavasseur/Wallet-Risk-Scanner & Web3 Security Intelligence`

Prosedur Operasi Standar (SOP) resmi kedaulatan Flowork OS untuk pemindaian risiko alamat wallet multi-chain, kepatuhan anti pencucian uang (AML), dan deteksi malicious drainer:

## 1. DOKTRIN PEMINDAIAN RISIKO WALLET & DRAINER
- **Skor Risiko Alamat (Risk Scoring 0 - 100)**:
  - **Skor 0 - 20 (Clean / Low Risk)**: Aktivitas wallet normal pada protokol DeFi resmi tanpa keterlibatan jejak hitam.
  - **Skor 21 - 60 (Medium Risk)**: Interaksi dengan kontrak tidak terverifikasi atau volume transaksi anomali.
  - **Skor 61 - 100 (Critical / High Risk)**: Terbukti pernah berinteraksi dengan smart contract Tornado Cash / mixer terlarang, wallet peretas berlabel OFAC, atau drainer signature.

- **Deteksi Phishing Permit / Drainer Approval**:
  - Periksa riwayat *unlimited ERC20 approval* atau *Permit2 signatures*.
  - Segera rekomendasikan eksekusi pencabutan izin (*revoke approvals*) jika alamat terhubung ke kontrak penyedot aset yang mencurigakan.

- **Pencegahan Interaksi Beracun (Tainted Fund Defense)**:
  - Dilarang menandatangani transaksi jika smart contract target atau penerima memiliki keterkaitan dengan eksploit terpublikasi.
