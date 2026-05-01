# Font Eşleşmeleri — Referans

Bu dosya `SKILL.md` tarafından referans olarak okunuyor. Ajan "tipografi seçmesi" gerektiğinde buraya bakıyor.

## Kural: 2 font

Her tasarım için **heading + body** olmak üzere 2 font seç. 3+ font genellikle karmaşa yaratır.

## Geometric + Neutral (SaaS, dokümantasyon)

### Geist Sans + Geist Mono
- Heading: Geist Sans — modern, geometrik
- Mono: Geist Mono — kod blokları için
- Uygun: Vercel tarzı, developer tools

### Inter + JetBrains Mono
- Heading & Body: Inter — sistem tarzı, 9 ağırlık
- Mono: JetBrains Mono — ligature destekli
- Uygun: SaaS, dashboard, admin panel

## Serif + Sans (yayın, marka)

### Fraunces + Inter
- Heading: Fraunces — karakterli serif
- Body: Inter — nötr sans
- Uygun: blog, haber, yazı ağırlıklı ürünler

### Playfair Display + Source Sans
- Heading: Playfair — yüksek kontrastlı serif
- Body: Source Sans — okunabilir
- Uygun: editorial, premium marka

## Terminal / Hacker estetiği

### JetBrains Mono + JetBrains Mono
- Tek font, tüm metin monospace
- Uygun: CTF, hacker teması, bu video sunumunun fontu

### Space Mono + Space Grotesk
- Heading: Space Grotesk — yarı-geometrik sans
- Mono: Space Mono — retro teknik his
- Uygun: AI/ML ürünleri, teknik portfolio

## Yumuşak / Oyuncu

### Cal Sans + Inter
- Heading: Cal Sans — yuvarlak, dostane
- Body: Inter
- Uygun: startup landing, oyun, eğitim

### Poppins + Roboto
- Heading: Poppins — geometrik dostane
- Body: Roboto — sistem
- Uygun: e-ticaret, lifestyle

## Kurumsal / Ciddi

### IBM Plex Sans + IBM Plex Mono
- Tek aile, iki varyant
- Uygun: enterprise, fintech, B2B

---

(gerçek skill'de 57 eşleşme olurdu — bu kısaltılmış demo örneği)

## Kullanım notu

- Heading ağırlığı: 600-700
- Body ağırlığı: 400-500
- `font-display: swap` her zaman ekle (CLS düşürmek için)
- Mobilde minimum 16px body size — altı iOS'ta zoom tetikler
