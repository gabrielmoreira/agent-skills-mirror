# 4 Ajan — Bilgisayarımda Nasıl Görünüyor?

Bu klasör videoda gösterdiğin 4 ajanın gerçek hali. Her biri ayrı bir markdown dosyası.

## Klasör yapısı

```
~/.claude/agents/
├── planner.md       ← Ne yapılacağını planlar
├── ui-agent.md      ← Görsel + component mantığı
├── builder.md       ← Kodu yazar (TDD)
└── reviewer.md      ← Kalite + güvenlik (çift görev)
```

## Dosya formatı

Her ajan dosyası iki bölümden oluşur:

**1. YAML frontmatter** (üstte `---` ile çevrili blok):
- `name` — ajanın ismi
- `description` — ne zaman otomatik tetikleneceği
- `tools` — hangi araçlara erişebileceği
- `model` — opus / sonnet / haiku

**2. Sistem promptu** — markdown olarak ajanın nasıl davranacağı

`description` alanı kritik. Claude Code bu cümleye bakıp ajanı otomatik çağırıp çağırmayacağına karar veriyor. "Use PROACTIVELY when..." yazarsan otomatik tetiklenir.

## Kurulum

```bash
# Bu klasördeki 4 dosyayı gerçek agents klasörüne kopyala
cp *.md ~/.claude/agents/
```

## Doğrulama

Kurulumdan sonra Claude Code'da şunu yaz:

```
/agents
```

4 ajanın listede olduğunu göreceksin.

## Kullanım akışı

```
kullanıcı: "Pricing sayfası yap"
    ↓
ANA CLAUDE (orchestrator)
    ↓ (Task tool ile sırayla çağırıyor)
    ├─→ planner    → plan döner
    ├─→ ui-agent   → component brief döner
    ├─→ builder    → kod + test döner
    └─→ reviewer   → bulgular döner (CRITICAL varsa builder'a loop)
```

## Model seçimleri

| Ajan | Model | Neden? |
|---|---|---|
| planner | opus | En derin akıl yürütme, mimari karar |
| ui-agent | sonnet | Tasarım + component, dengeli |
| builder | sonnet | Ana kod üretimi, en iyi coding modeli |
| reviewer | sonnet | Detaylı inceleme, dengeli |

## Araç izinleri (güç paylaşımı)

Her ajanın sadece işine yetecek kadar aracı var:

| Ajan | Okuma | Yazma | Bash (komut) |
|---|---|---|---|
| planner | ✓ | ✗ | ✗ |
| ui-agent | ✓ | ✗ | ✗ |
| builder | ✓ | ✓ | ✓ (test çalıştırma) |
| reviewer | ✓ | ✗ | ✓ (statik analiz) |

Builder yazabilir ama review edemez. Reviewer review edebilir ama yazamaz. Planner sadece okur.

## Önemli: ajanlar birbirini çağırmıyor

Hiçbirinin `Task` aracı yok. Bu bilinçli bir seçim:
- Ajanlar birbirini çağıramıyor (alt-ajan spawn edemez)
- Tüm koordinasyon **Ana Claude** üzerinden geçiyor
- Context fragmentasyonu olmuyor, debug kolay

## Skills

Ajanlar bu skill'leri kullanıyor (ayrı kurulum · `~/.claude/skills/` altında):

- `/plan` — planner için
- `/new-ai-app` — planner + ui-agent için
- `/ui-ux-pro-max` — ui-agent için
- `/tdd` — builder için
- `/build-fix` — builder için
- `/code-review` — reviewer için
- `/security-review` — reviewer için
- `/simplify` — reviewer için

Skill kurulumu için `/Users/selma/skills-demo/` klasörüne bak.

## Video için notlar

**Ekrana alırken:** bu 4 dosyayı Finder'da yan yana aç. İçeriğe tıkla.

**Vurgu noktaları:**
- `description` alanı — Claude ajanı ne zaman çağıracağını buradan öğreniyor
- `tools` alanı — güç paylaşımı, her ajanın sadece gerekli aracı var
- Hiçbirinde `Task` yok — ajanlar birbirini çağıramaz, Ana Claude postacı
