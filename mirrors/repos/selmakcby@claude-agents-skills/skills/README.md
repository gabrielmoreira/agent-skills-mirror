# Skills — Bilgisayarımda Nasıl Görünüyor?

Ajanların kullandığı skill'lerin gerçek hali. Her skill = bir klasör + `SKILL.md`.

## Klasör yapısı

```
~/.claude/skills/
├── tdd/
│   └── SKILL.md                  ← tek dosyalık basit skill
│
├── ui-ux-pro-max/                ← daha zengin skill
│   ├── SKILL.md                  ← ana talimat dosyası
│   ├── styles.md                 ← referans · stiller
│   ├── palettes.md               ← referans · renk paletleri
│   ├── fonts.md                  ← referans · font eşleşmeleri
│   └── components.md             ← referans · komponent örnekleri
│
└── code-review/
    └── SKILL.md
```

## SKILL.md formatı

Her SKILL.md iki parçadan oluşur:

**1. YAML frontmatter:**
```yaml
---
name: skill-adı
description: Ne zaman tetikleneceği (bu cümle çok önemli)
---
```

**2. Markdown talimatlar:**
- Ne zaman aktif olunacak
- Hangi yaklaşımı kullanacak
- Çıktı formatı nasıl olacak
- Kurallar

## Basit vs zengin skill

**Basit skill** — tek bir `SKILL.md` dosyası (tdd, code-review gibi).  
Tüm talimatlar o tek dosyada.

**Zengin skill** — klasör içinde ek referans dosyaları (ui-ux-pro-max gibi).  
`SKILL.md` ana talimatı tutuyor, başka dosyalardan ek bilgi çekiyor.  
Örnek: "Stil seçmen gerekiyorsa `styles.md`'ye bak."

## Kurulum

```bash
# Tek skill:
cp -r /Users/selma/skills-demo/tdd ~/.claude/skills/

# Tüm skill'ler:
cp -r /Users/selma/skills-demo/*/ ~/.claude/skills/
```

## GitHub'dan skill çekmek

```bash
# Resmi Anthropic skill'leri
git clone https://github.com/anthropics/skills ~/anthropic-skills

# İstediğin skill'i kopyala
cp -r ~/anthropic-skills/skills/claude-api ~/.claude/skills/

# Ya da topluluk (1000+ skill)
# github.com/VoltAgent/awesome-agent-skills
```

## Doğrulama

Claude Code'da skill'i çağırmak için:
```
/skill-adı
```

Örneğin:
```
/tdd
/ui-ux-pro-max
/code-review
```

## Ajan-skill eşleşmesi

Bu video için benim setup:

| Ajan | Kullandığı Skill'ler |
|---|---|
| **planner** | `/plan`, `/new-ai-app` |
| **ui-agent** | `/ui-ux-pro-max`, `/new-ai-app` |
| **builder** | `/tdd`, `/build-fix` |
| **reviewer** | `/code-review`, `/security-review`, `/simplify` |

## Video için notlar

**Ekrana alırken:**
- `/Users/selma/skills-demo/` klasörünü Finder'da aç
- `tdd/SKILL.md`'yi aç → "basit skill örneği"
- `ui-ux-pro-max/`'ı genişlet → "zengin skill örneği, klasör yapısı"
- Frontmatter'daki `description` alanını vurgula — "Claude Code bu cümleyi görüp skill'i tetikliyor"

**Vurgu:**
- Skill = salt talimat dosyası. Kod değil.
- Kendi skill'ini yazmak 5 dakika: klasör + `SKILL.md` yeter.
- Anthropic'in resmi repo'su `anthropics/skills` — pdf, docx, excel, claude-api skill'leri hazır.
