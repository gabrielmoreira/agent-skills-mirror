---
name: tdd
description: Test-Driven Development workflow. Use when writing new features, fixing bugs, or refactoring code. Enforces RED-GREEN-REFACTOR cycle with 80%+ coverage.
---

# TDD — Test-Driven Development

## Ne zaman tetiklenir
- Yeni özellik yazıldığında
- Bug fix öncesi (hatayı üreten test ilk yazılır)
- Refactor sırasında (mevcut testler yeşil kalmalı)

## RED — GREEN — REFACTOR

### 1. RED — Önce başarısız test yaz
- Yeni davranışı test olarak yaz
- Testi çalıştır, **başarısız olduğunu** gör
- Başarısız olmazsa, test gerçekten bir şey ölçmüyor demektir

### 2. GREEN — Minimum kodu yaz
- Testi geçiren **en az** kodu yaz
- Güzel olmasına çalışma, sadece geçsin
- Testin geçtiğini doğrula

### 3. REFACTOR — Temizle
- Kod çalışıyor, şimdi netleştir
- Testler yeşil kalmalı
- İsim düzelt, duplication kaldır, fonksiyonları böl

## Kapsam hedefleri

- **Genel kod:** %80+ coverage
- **Kritik:** auth, ödeme, güvenlik → %100 coverage
- **Test türleri (hepsi gerekli):**
  - Unit (fonksiyon/utility)
  - Integration (API, DB)
  - E2E (kritik kullanıcı akışları)

## Kurallar

- Önce test, sonra kod. İstisnasız.
- Test başarısız olursa kodu düzelt — **testi düzeltme**
- Tüm dış bağımlılıkları mock'la (DB, API'ler, 3. parti)
- Testler bağımsız olmalı (state paylaşmamalı)
