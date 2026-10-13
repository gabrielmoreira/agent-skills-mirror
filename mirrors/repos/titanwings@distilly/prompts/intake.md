# Basic Info Intake Script

## Opening

```
I'll help you create a Skill for this colleague. Just answer 3 questions — you can skip any of them.
```

---

## Question Sequence

### Q1: Alias / Codename

```
What do you call this colleague? (An alias, nickname, or codename all work; join multiple words with -)

Example: qing-yun
```

- Accept any string
- The generated slug always uses `-` as the separator (no underscores)
- Chinese names are automatically converted to pinyin and joined with `-` (a Chinese name such as "Qingyun" → `qing-yun`, "Xiao Li" → `xiao-li`)
- English names are lowercased and joined with `-` ("Big Mike" → `big-mike`)

---

### Q2: Basic Info

Put company, level, role, and gender into a single question so the user can answer in one sentence:

```
Describe their basic info in one sentence — company, level, role, gender. Write whatever comes to mind, or skip it.

Example: ByteDance 2-1 backend engineer male
```

Parse the following fields from the user's answer (leave missing ones blank):
- **Company**
- **Level**
- **Role**
- **Gender**

#### Level Reference Table

| Company | Level format | Engineer/Researcher | Senior Engineer | Senior Staff/Expert | Staff/Principal |
|------|---------|------------|---------|---------|----------------|
| ByteDance | X-Y | 2-1, 2-2 | 3-1, 3-2 | 3-3 | 3-3+ (O-level) |
| Alibaba | P-level | P5, P6 | P7 | P8 | P9+ |
| Tencent | T-level | T1-1~T2-2 | T3-1, T3-2 | T4 | T4+ |
| Baidu | T-level | T5, T6 | T7 | T8 | T9+ |
| Meituan | P-level | P4, P5 | P6 | P7 | P8+ |
| Huawei | Numeric | 13-15 | 16-17 | 18-19 | 20-21 |
| NetEase | P-level | P1-P3 | P4 | P5 | P6+ |
| JD.com | T-level | T3-T4 | T5 | T6 | T7+ |
| Xiaomi | Numeric | 1-3 | 4-5 | 6-7 | 8+ |

**Rough cross-company mapping**:

```
ByteDance 2-1/2-2  ≈  Alibaba P6   ≈  Tencent T2   ≈  Baidu T6
ByteDance 3-1      ≈  Alibaba P7   ≈  Tencent T3-1 ≈  Baidu T7
ByteDance 3-2      ≈  Alibaba P7+  ≈  Tencent T3-2
ByteDance 3-3      ≈  Alibaba P8   ≈  Tencent T4
```

> Note: ByteDance 2-1 is the Engineer title; Senior Engineer starts at 3-1.
> 2-1 is roughly equivalent to Alibaba P6 — a core engineer who completes tasks independently.

---

### Q3: Personality Profile

Combine MBTI, zodiac sign, personality tags, corporate culture tags, and subjective impressions, and let the user describe freely:

```
Describe their personality in one sentence — MBTI, zodiac sign, traits, corporate culture imprint, your impression of them.
Write whatever comes to mind, or skip it.

Example: INTJ Capricorn master blame-shifter ByteDance-style very strict in CR but never explains why
```

Identify and extract the following fields from the user's answer (leave missing ones blank):
- **MBTI**: the 16 standard types
- **Zodiac**: the 12 signs
- **Personality tags**: match against the tag library below; custom descriptions are also accepted
- **Corporate culture tags**: match against the tag library below
- **Subjective impression**: free-form description that can't be categorized; keep the original text as-is

#### Personality Tag Library

**Work attitude**: Conscientious / Good-enough / Master blame-shifter / Scapegoat / Perfectionist / Procrastinator

**Communication style**: Direct / Beats around the bush / Quiet / Talkative / Loves voice messages / Reads but never replies / Replies off-topic / Compulsive instant replier

**Decision style**: Decisive / Flip-flopper / Defers to the boss / Pushes hard / Data-driven / Goes by gut feeling

**Emotional style**: Emotionally stable / Thin-skinned / Easily agitated / Cold and distant / Superficially pleasant / Passive-aggressive

**Tactics and maneuvers**: Gaslighting expert / Office politics player / Blame-shifting artist / Managing-up expert / Loves to lecture on principles / Emotional blackmailer

#### Corporate Culture Tag Library

- **ByteDance-style** — candid and direct, chases impact, always opens with context, loves to say "align"
- **Alibaba-flavor** — the "Six Vein Spirit Sword" values, loves "empower", "lever", "ecosystem", "closed loop"
- **Tencent-flavor** — lets data speak, horse-race mechanism, restrained and conservative, focused on user experience
- **Huawei-flavor** — striver culture, process and standards, loves PPT reporting, emphasizes execution
- **Baidu-flavor** — technology above all, strong hierarchy awareness, fierce internal competition
- **Meituan-flavor** — extreme execution, obsesses over details, localization mindset
- **First principles** — Musk-style, digs for the essence, rejects analogy, radical simplification
- **OKR zealot** — asks for the Objective first in everything, nitpicks every KR
- **Big-tech assembly line** — well-established standards but low creativity, relies on SOPs, afraid of taking blame
- **Startup type** — limited resources, full-stack mindset, results-oriented, tolerates chaos

---

## Confirmation Summary

After collection, display:

```
Info summary:

  👤  {alias}
  🏢  {company} {level} {role} (omit if not provided)
  ⚧   {gender} (omit if not provided)
  🧠  {MBTI} {zodiac} (omit if not provided)
  🏷️   Personality: {tag list} (omit if not provided)
  🏢  Corporate culture: {tag list} (omit if not provided)
  💬  Impression: {impression text} (omit if not provided)

Is this correct? (confirm / edit [field name])
```

Once the user confirms, proceed to Step 2: file import.
