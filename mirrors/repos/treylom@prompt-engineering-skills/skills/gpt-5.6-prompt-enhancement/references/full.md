---
name: gpt-5-6-prompt-enhancement
description: Use when composing prompts targeting GPT-6.2 Sol (GPT 디폴트), GPT-6.2 Astra, GPT-6 Sol (직전 디폴트), GPT-6 Astra, GPT-6 Luna, GPT-5.6 Sol or legacy GPT-5.5/5.4/5.2 — lean outcome-first 7블록 규칙 + LEGACY 섹션(구 XML 스택)을 담은 GPT 프롬프트 전략 레퍼런스. /prompt 커맨드가 GPT 타겟 감지 시 로드.
disable-model-invocation: true
---

# GPT-5.6 Sol 프롬프트 향상 스킬 (Lean Outcome-First + Legacy)

> **Version**: 1.5.0 | **Updated**: 2026-11-18 (GPT-6.2 Astra · Sol 절 신설 — GPT 디폴트를 GPT-6.2 Sol 로 전환, 공식 가이드 «Using GPT-6.2» 의 성향 4가지 · 처방 블록 원문 · reasoning items 를 버리는 조건 · 옮길 때 바꿀 값 · GPT-6 처방 중 6.2 에서 바뀐 것에 «GPT-6 판 한정» 표지.) | 이전: 1.4.0 · 2026-09-27 (GPT-6 Sol·Luna 절 신설 — GPT 디폴트를 GPT-6 Sol 로 전환, `none` 지원·Chat Completions 함수 호출 조건·샘플링 매개변수 제거·출시 공지 기준 문체·GPT-5.6 Sol → GPT-6 Sol/Luna 마이그레이션 체크. 공식 문서 대조.) | 이전: 1.3.0 · 2026-09-06
> **Source**: [Using GPT-6.2](https://developers.openai.com/api/docs/guides/latest-model) · [GPT-6.2 출시 공지 (OpenAI 개발자 포럼)](https://community.openai.com/t/gpt-6-2-astra-and-sol-are-now-available/1417531) — 접근일 2026-11-18 · [Prompting guidance for GPT-5.6 Sol](https://developers.openai.com/api/docs/guides/prompt-guidance-gpt-5p6) · [Using GPT-6](https://developers.openai.com/api/docs/guides/latest-model) (GPT-6 패밀리 가이드 — 같은 주소가 지금은 «Using GPT-6.2» · 구 표기 «Using GPT-6 Astra») · 모델 카드 [gpt-6-sol](https://developers.openai.com/api/docs/models/gpt-6-sol.md) · [gpt-6-luna](https://developers.openai.com/api/docs/models/gpt-6-luna.md) · [출시 공지](https://openai.com/index/introducing-gpt-6-sol-and-luna/) — 접근일 2026-09-27
> **Scope**: GPT 5.x~6.2 통합 — **GPT-6.2 Sol = 현행 GPT 디폴트(2026-11-17~)**, GPT-6.2 Astra = 최고 성능, GPT-6 Sol = 직전 디폴트(2026-09-22~), GPT-6 Astra = 직전 세대 최고 성능, GPT-6 Luna = 대량·반복·효율(6.2 판 없음), GPT-5.6 Sol = 그 전 디폴트. GPT-6.2 Astra · Sol 절 + GPT-6 Sol·Luna 절 + GPT-6 Astra 절 + lean outcome-first(5.6/5.5) + 하단 legacy(5.5 outcome-first / 5.4·5.2 XML stack) 보존. GPTs/Gems 첨부 10개 한도 대응으로 단일 파일 통합.

---

## 핵심 변화 요약 (vs GPT-5.5)

| 항목 | GPT-5.5 | GPT-5.6 Sol |
|------|---------|-------------|
| 기본 간결성 | plain paragraph 디폴트 | **더 간결** — "간결하게/짧게" 광범위 지시가 역효과일 수 있음 |
| 프롬프트 철학 | outcome-first | **lean 우선** — 군더더기 제거만으로 (내부 테스트 기준) eval ~10~15%↑, 토큰 41~66%↓, 비용 33~67%↓ |
| Reasoning effort | low/medium 우선 | `low/medium/high/`**`xhigh/max`** — baseline 보존 + 한 단계 낮춰 비교, effort↑ 전 프롬프트 강화 먼저 |
| 도구 | 병렬/persistence | **PTC(프로그래매틱 도구 호출)** 경계 추가 |
| 자율성 | eagerness control | **승인 레벨(authorization) 3단** 명시 |
| 구조 | Markdown 6섹션 | **7블록**(Tools 분리 + Stop Rules 강조) |
| 절대어 | judgment 영역 자제 | 진짜 불변식(안전·필수·금지)에만, 판단엔 decision rule |

---

## 트리거 조건

- 사용자가 "GPT-5.6용 프롬프트", "ChatGPT 5.6", "Codex 5.6", "GPT-5.6 Sol" 명시 (맨 "Sol" 단독은 GPT-6.2 Sol · GPT-6 Sol 과 겹치므로 세대를 확인)
- Batch 모드에서 첫 토큰이 `GPT-5.6` 일 때
- **모델 미지정 = GPT 디폴트 = GPT-6.2 Sol** (2026-11-17~) → 아래 «GPT-6.2 Astra · Sol» 절. GPT-6 Sol(2026-09-22~)은 직전 디폴트, GPT-5.6 Sol 은 그 전 디폴트 — 이 절(5.6 lean outcome-first)은 GPT-5.6 명시 시 적용하며, GPT-6.2 · GPT-6 절의 출발점 구조로도 쓰인다

> ⚠️ **하위호환**: 사용자가 "5.5", "5.4 XML 스타일", "legacy XML stack" 명시 시 아래 LEGACY 섹션으로 fallback.

---

## 권장 프롬프트 구조 (Markdown, 7블록)

```markdown
Role:
[1-2 문장. 기능 + 컨텍스트]

# Personality
[톤·협업 스타일. 짧게.]

# Goal
[사용자가 받게 될 최종 산출물 1-2문장.]

# Success Criteria
- [최종 답 전 참이어야 할 조건]

# Constraints
- [정책·안전·증거·부작용 한계. 절대어는 진짜 불변식만.]

# Tools
[어떤 도구를 언제 쓰고 무엇을 쓰지 말지. PTC vs 직접 호출 경계.]

# Output
[섹션·길이·형식·톤. text.verbosity와 호흡.]

# Stop Rules
- [재시도·폴백·기권·질문·정지 규칙 — 루프 최소화하되 정확성·증거·계산·인용이 우선(요약)]
```

> **5.5 대비 변화**: `# Tools` 블록 분리(도구 라우팅·PTC 명시), `# Stop Rules` 강조. 나머지 6섹션은 5.5 outcome-first 계승.

---

## 필수 적용 블록 (GPT-5.6)

### 1. `lean_first` — 프롬프트 단순화 (최우선)

**용도**: 작성/이관한 프롬프트에서 아래를 먼저 삭제. 삭제만으로 eval↑·토큰↓·비용↓.

```markdown
Remove: 중복 규칙 진술 / 행동 안 바꾸는 예시·스타일 반복 / 이미 잘하는 것의 절차 지시 / 무관한 도구 설명.
Preserve: 사용자 가시 결과 / 성공 기준·정지 조건 / 안전·비즈니스·증거·권한 제약 / 맥락 의존 도구 라우팅 / 출력 구조·검증 요건.
```

### 2. `outcome_first_structure` — destination 우선

```markdown
Role:
You are a pragmatic assistant helping the user complete the task end to end.

# Goal
Deliver a usable final artifact that directly satisfies the user's request.

# Success Criteria
- The core request is answered or completed.
- Missing assumptions are stated briefly.
- Any required validation is performed or explicitly marked as not run.
```

> 절차 대신 목적지. 절대어(ALWAYS/NEVER/must/only)는 진짜 불변식(안전·필수 필드·절대 금지)에만; 판단은 decision rule로.

### 3. `personality_and_collaboration` — 톤·협업

```markdown
# Personality
Steady and direct. GPT-5.6 is already brief by default — set the default detail level via text.verbosity rather than broad "be concise" directives.

# Collaboration Style
State what you are doing before multi-step tool work. Ask only for the smallest missing input when blocked.
```

### 4. `constraints_block` — lean·no-fabrication

```markdown
# Constraints
- Do not invent facts, metrics, names, dates, roadmap status, or capabilities.
- Reserve ALWAYS/NEVER/must/only for true invariants; use decision rules for judgment calls.
- Preserve working behavior; prefer the simplest solution meeting success criteria.
```

### 5. ★ `tools_and_ptc` — 도구 라우팅 + 프로그래매틱 도구 호출 (5.6 신규)

```markdown
# Tools
Expose only task-relevant tools. Describe function, when to use, key return fields, error behavior.
Before acting, resolve required discovery/retrieval/validation; do not skip a prerequisite because the final state seems obvious.
On empty/partial/suspiciously narrow results, attempt one or two meaningful fallbacks before concluding "no result".
Parallelize independent reads; keep sequential when one result determines the next; synthesize after parallel retrieval.

# PTC (Programmatic Tool Calling) vs Direct
Use PTC for: filtering, joining, sorting, ranking, dedup, aggregation, batching across many similar records, repeated deterministic validation, large results reducible to compact schemas.
Prefer direct calls when: one call suffices; intermediate outputs are already small; each result changes the next decision; action needs approval; citations/native artifacts must be preserved; semantic judgment is needed between calls.
For PTC, state the bounded stage, eligible tools, output schema, retry limit, stop condition, and handoff back to direct judgment.
```

### 6. ★ `authorization_boundaries` — 자율성 승인 3단 (5.6 신규)

```markdown
# Autonomy
- Answer/explain/review/diagnose/plan → inspect and report; no changes unless asked.
- Change/build/fix → make in-scope local changes + non-destructive validation without asking.
- External writes / destructive actions / purchases / scope expansion → require confirmation.
```

### 7. `stop_rules` + retrieval budget

```markdown
# Stop Rules
Resolve in the fewest useful tool loops, but do not let loop minimization outrank correctness, required evidence, calculations, or citations.
Start Q&A with one broad search (short discriminative keywords). Retrieve again only when required facts/owners/dates/IDs/sources are missing, exhaustive coverage is asked, a specific artifact must be read, or a claim would be unsupported.
Do not search to improve phrasing or support non-essential details.
```

### 8. `validation_rules` — 끝내기 전 검증

```markdown
# Validation
- Coding: run the most relevant targeted test, type check, lint, build, or smoke test.
- Visual: render and inspect for layout, clipping, spacing, missing content; revise until it matches requirements.
- Planning: include requirements, named resources, state transitions, validation commands, failure behavior, privacy/security, open questions.
- Creative drafting: ground product/customer/metric/capability claims in retrieved facts; label assumptions otherwise. Do not invent names/dates/metrics/roadmap.
```

---

## Preamble (멀티스텝/도구 작업 시)

```markdown
Before tool calls for a multi-step task, send a one- or two-sentence user-visible update stating the first step.
During the task, update only when a major phase begins or findings change the plan. Each update = one concrete outcome + next step. Do not narrate routine tool calls.
```

도구 1-2회 단순 작업엔 생략. (⚠️ *5.5 가이드 계승 — 5.6 공식문서 미기재*: Codex CLI엔 preamble 요구 금지, 조기 종료 유발.)

---

## Phase Parameter / State (Responses API, 멀티턴)

- Replay 시 assistant `phase` 값 보존. `phase: "commentary"`(중간) / `"final_answer"`(최종). user 메시지엔 phase 추가 X.
- `previous_response_id`로 이전 상태 자동 유지, 또는 phase 보존하며 수동 replay.
- **주요 마일스톤 후 compaction**(매 턴 ❌). compaction 후 프롬프트 기능 일관 유지, 압축 항목은 opaque state로.
- Persisted reasoning은 목표·가정·우선순위가 턴 간 안정적일 때만.

---

## Reasoning Effort 권장값 (5.6 기준)

| 작업 | 권장 effort | 비고 |
|------|------------|------|
| 지연 민감·품질 유지 | `low` | baseline에서 한 단계 낮춰 비교 |
| 균형 시작점 | `medium` | 기본 |
| 장기·다단 검증 | `high` / `xhigh` | **eval 상 유의미 이득 확인 시만** |
| 최난도 품질 우선 | `max` | **전역 권장 ❌** — 특정 워크로드만 |

> effort 올리기 **전**: 프롬프트에 성공 기준·의존 규칙·도구 라우팅·검증 루프가 있는지 확인. **강한 프롬프트 > 높은 effort.** 모델 전환 시 현 effort를 baseline으로 보존.

---

## Anti-Patterns (GPT-5.6에서 회피)

| 안티패턴 | 이유 |
|---------|------|
| "간결하게/짧게" 광범위 지시 | 5.6은 기본이 더 간결 — 역효과 가능 |
| 중복 규칙·불필요 예시·무관 도구 설명 | lean 위반, eval↓·토큰↑·비용↑ |
| effort부터 올리기 | 프롬프트 강화가 먼저 |
| 작동하는 프롬프트 통째 재작성 | 원인 귀속 불가 — surgical edit만 |
| 모든 도구를 PTC로 | 승인·인용보존·판단개입엔 직접 호출 |
| ALWAYS/NEVER 남발 | 판단 영역 추론 차단 — decision rule로 |

---

## 마이그레이션 (GPT-5.5 → GPT-5.6)

1. 모델 전환 — **현 reasoning effort 보존**
2. 프롬프트 변경 전 대표 eval 실행
3. 낡은 scaffolding·반복 지시·무관 도구 제거 (lean)
4. 측정된 회귀를 고치는 **가장 작은 타깃 지시만** 추가
5. 프롬프트·effort 변경마다 eval 재실행

> **작동하는 프롬프트 스택을 통째로 재작성하지 말 것** — 행동 변화 원인(모델/effort/프롬프트/도구/런타임) 귀속을 위해. 회귀 디버깅 = 작은 real-trace로 실패모드 식별 → 문제 지시·모순 위치 → surgical edit → 동일 케이스 재실행.

---

## 예시: 웹 리서치 에이전트 (5.6 7블록)

```markdown
Role:
You are an expert research assistant.

# Goal
Provide a verified answer to the user's question with citations for any factual claim.

# Success Criteria
- Every factual claim traces to a retrieved source; inference is labeled separately.
- Contradictions across sources are flagged; narrow the answer or report missing evidence instead of guessing.

# Constraints
- Do not fabricate sources, dates, or numbers. Absence of evidence is not automatically a factual "no".

# Tools
Search + fetch. One broad search first; parallelize independent reads; synthesize before answering.

# Output
Concise Markdown. Lead with the answer, then cite sources inline.

# Stop Rules
Retrieve again only when required facts are missing, exhaustive coverage is asked, or a claim would be unsupported. Stop when success criteria are met.
```

## 예시: 코딩 에이전트 (5.6 7블록 + validation)

```markdown
Role:
You are a senior engineer pairing with the user.

# Goal
Ship a focused change that satisfies the request and passes the most relevant validation.

# Success Criteria
- The change compiles, type-checks, and passes targeted tests. No drive-by refactors.

# Constraints
- Preserve existing behavior unless the request changes it. Prefer the simplest solution.

# Tools
Use direct edits/tests. Reserve programmatic batching for many similar records.

# Autonomy
- In-scope local changes + non-destructive validation without asking; require confirmation for external/destructive actions.

# Output
Plain Markdown. Show edited files, then the validation outcome.

# Stop Rules
Run the most relevant validation (test/type/lint/build/smoke). Stop when success criteria are met; ask only for the smallest missing input if blocked.
```

---

## GPT-6.2 Astra · Sol (2026-11-17~, GPT 디폴트 = GPT-6.2 Sol)

> **공식 출처** (접근일 2026-11-18): [Using GPT-6.2](https://developers.openai.com/api/docs/guides/latest-model) (GPT-6.2 패밀리 가이드 — 같은 주소의 직전 판 제목 = «Using GPT-6») · 모델 카드 [gpt-6.2-astra](https://developers.openai.com/api/docs/models/gpt-6.2-astra) · [gpt-6.2-sol](https://developers.openai.com/api/docs/models/gpt-6.2-sol) · [출시 공지 (OpenAI 개발자 포럼)](https://community.openai.com/t/gpt-6-2-astra-and-sol-are-now-available/1417531)
> 모델 ID = `gpt-6.2-astra` · `gpt-6.2-sol` · 출시 2026-11-17 · API 가격(출시 공지 표, 100만 토큰당 입력 / 출력) = GPT-6.2 Astra 8달러 / 40달러 · GPT-6.2 Sol 2달러 / 10달러

### 공식 출처와 한계

- 공식 페이지 한 장이 두 모델을 함께 다룬다. GPT-6.2 Sol 전용 프롬프트 가이드 = 확인 범위 내 미발견 (2026-11-18).
- 예시 프롬프트의 범위 (원문):

  > "Use the following prompts as a starting point across the GPT-6.2 model family. The examples address behaviors we’ve seen when working with GPT-6.2 Astra and Sol."

- 직전 판(«Using GPT-6»)은 예시를 GPT-6 Astra 관찰 기반으로 한정했다. 이 판은 Astra·Sol 둘 다에서 본 성향이라고 적는다. 그래도 가이드 스스로 «starting point»(출발점)라고 적는다 — 넣기 전에 자기 워크로드에서 기본 출력을 먼저 보고 실제로 관찰된 문제에 맞는 처방만 넣는다.
- 성향 목록의 소제목은 «GPT-6.2 Astra behavior» 지만 바로 앞 문장 기준으로 이 절의 처방은 두 모델 공통이다.
- GPT-6 Luna 의 6.2 판은 공식 페이지에 없다 → 대량·반복·효율 작업은 아래 «GPT-6 Sol · Luna» 절의 GPT-6 Luna 를 그대로 쓴다.
- 이 페이지에는 직전 판의 `configuration_update`(대화 중 추론 강도 변경)·턴 중간 조종(mid-turn steering)·오정렬 모니터링 안내와 «Limitations»·«Subagent delegation» 소제목이 없다(확인 범위 내 미발견). 기능이 없어졌다는 뜻인지는 이 페이지만으로 알 수 없다 — 쓰기 전에 그 기능 문서를 따로 확인한다.
- 같은 주소의 2026-10-28 웹 보관본(제목 «Using GPT-6»)에는 GPT-6.1 Sol · GPT-6.1 Terra 도 실려 있었고 그때 가이드가 안내하던 Sol 은 GPT-6.1 Sol 이다. 이 파일의 GPT-6 절들(아래 «GPT-6 Astra» · «GPT-6 Sol · Luna»)은 2026-09-27 접근 판 기준이고 GPT-6.1 은 다루지 않는다. 그래서 이 저장소의 «직전 디폴트 = GPT-6 Sol» 은 이 스킬이 직전에 기본으로 쓰던 모델이라는 뜻이다. 이 절의 «직전 판» 비교 문구는 2026-10-28 보관본 기준이다.

### 트리거 조건

- 사용자가 "GPT-6.2", "GPT-6.2 Astra", "gpt-6.2-astra", "GPT-6.2 Sol", "gpt-6.2-sol" 명시. 변형 없이 "GPT-6.2" 만 적으면 GPT-6.2 Sol(디폴트)로 쓰고 최고 성능을 요구하면 GPT-6.2 Astra 로 쓴다.
- **GPT 모델 미지정 = 이 절, 모델 = GPT-6.2 Sol** (2026-11-17~). 가장 어려운 작업·최고 성능이라고 하면 GPT-6.2 Astra.
- 대량·반복·효율 위주 = GPT-6 Luna (6.2 판 없음) → 아래 «GPT-6 Sol · Luna» 절.
- "GPT-6 Astra"·"GPT-6 Sol"·"GPT-6 Luna"·"GPT-5.6 Sol" 처럼 세대를 적어 지정하면 그 모델의 절을 그대로 쓴다(이 절로 바꾸지 않는다).
- 🔴 **맨 "Sol"·"Astra" 단독은 트리거로 쓰지 않는다** — GPT-6.2 · GPT-6 · GPT-5.6 이 이름이 겹친다. 세대가 적혀 있지 않으면 어느 쪽인지 확인하고 산출 프롬프트에도 `GPT-6.2 Sol` 처럼 세대를 붙인다.

### 모델 선택 — GPT-6.2 Astra / GPT-6.2 Sol

| 모델 | ID | 가이드 원문 | 출시 공지 원문 |
|---|---|---|---|
| GPT-6.2 Astra | `gpt-6.2-astra` | "for the most demanding tasks" | "A frontier model built for your hardest projects." · "less than a third of the cost per task of GPT‑6 Astra" |
| **GPT-6.2 Sol** (디폴트) | `gpt-6.2-sol` | "for complex work at lower cost" | "An efficient and versatile model for everyday work." · "On FrontierCode 2.0, Sol nearly matches Astra on merge-ready changes to real codebases at about one-fifth the cost." |

- 비교 수치는 출시 공지의 서술 그대로 옮긴다(평가 조건은 공지 참조).

### 행동 성향 4가지 (가이드 원문)

| 축 | 원문 | 프롬프트에 주는 뜻 |
|---|---|---|
| 글쓰기 | "The model’s writing tends to be more concise and direct by default. When migrating, revisit instructions like “be concise” in your system prompt." | 기본이 짧고 직설적이다 → 옮겨 올 때 "간결하게" 류 지시를 다시 본다 |
| 작업 완수 | "When the user’s intent is unclear, the model may propose a next step and wait for confirmation. For longer tasks, give it room to make reasonable assumptions and keep working." | 의도가 애매하면 다음 단계를 제안하고 확인을 기다릴 수 있다 → 긴 작업은 가정하고 계속하게 둔다 |
| 코딩 | "The model tends to write more efficient, high-quality code than its predecessors. Describe any project conventions that should guide how it writes or edits code." | 프로젝트 관례를 적어 준다 |
| 프런트엔드 | "If the interface needs a particular look, specify the imagery and typography it should use." | 원하는 이미지 종류·타이포그래피(필요하면 특정 서체까지)를 적는다 |

### 새 API 동작 — reasoning items 를 버리는 조건 (프롬프트 설계에 영향)

> "Starting with GPT-6.2, the API will drop reasoning items when it detects mid-conversation changes to the conversation history (prefix edits), model downgrade, end user, or organization. When the model loses access to reasoning items, answer quality can decline and the model may use more tokens to repeat earlier work."

- 「대화 중간에 앞쪽 기록(지시문·도구 호출)을 고치거나, 모델을 낮추거나, 최종 사용자·조직이 바뀌면 API 가 이전 추론 기록을 버린다」 — 답 품질이 떨어질 수 있고 앞서 한 일을 되풀이하느라 토큰을 더 쓸 수 있다.
- 처방 원문: "keep the prefix unchanged" — 응답 사이에 설정을 바꿀 때 앞부분을 고치지 않는다 — 추론 기록과 프롬프트 캐시를 함께 지킨다. 가이드는 점검 대상으로 "changes to instructions or tool calls" 를 든다.
- 프롬프트를 만들 때: 매 턴 시스템 지시를 다시 쓰거나 앞쪽 도구 호출을 고치는 구조는 피하고 바뀌는 값은 뒤쪽 새 입력으로 넣는다(편집 판단).

### 프롬프트 작성 — 처방 블록

**구조 = 위 GPT-5.6 7블록(Role · Personality · Goal · Success Criteria · Constraints · Tools · Output · Stop Rules)을 출발점으로.** 7블록·lean outcome-first 는 이 가이드에 다시 실리지 않았으나 폐지 표기도 없다(확인 범위 내 미발견). 아래 처방 블록은 관찰된 문제에 맞는 것만 해당 블록에 넣는다.

| 처방 블록 | 넣을 블록 위치(7블록 + 필수 블록) | 가이드 절 |
|---|---|---|
| ① 동료·생각 파트너용 글쓰기 | `# Personality` / `# Output` | Writing style |
| ② 바깥 독자용 글쓰기 | `# Output` | Writing style |
| ③ 최종 답 자족 | `# Output` | Writing style |
| ④ 끝까지 진행 · 멈춤 조건 | `# Autonomy` / `# Stop Rules` | Task completion |
| ⑤ 완료 확인 · 지속 | `# Stop Rules` / `# Validation` | Task completion |
| ⑥ 애매할 때 가정하고 진행 | `# Autonomy` | Task completion |
| ⑦ 코딩 (a)~(d) | `# Constraints` | Coding style |
| ⑧ 프런트엔드 | `# Constraints` / `# Output` | Frontend design |

#### Writing style

가이드 원문: "GPT-6.2 Astra is more concise and direct by default than earlier models."

① 동료·생각 파트너용 (원문):

```text
Write using terminology the user and sources use. Keep technical details and use domain-specific language when they make the explanation more precise. Use the active voice and keep closely related details together. Cover the key points up front, and avoid references that the reader can only make sense of later in the response. Give the user enough context to follow your reasoning.
```

② 바깥 독자용 — 문서·메일·메시지·외부 게시물 (원문):

```text
When drafting a message or any other material on behalf of the user to be sent to an external audience, consider who will read it and tailor the content to that intended audience. The intended audience likely does not have the same context as the user, so ensure that you provide the background information or reasoning required for the audience to understand the content. When reviewing or editing existing content, preserve the author’s content and wording, and follow the user's instruction carefully for what edits they want.
```

③ 긴 작업의 최종 답 (원문):

```text
Treat your final answer as the user's first look at your work, and not as a continuation of intermediate commentary. The final answer must always be fully self-contained: users should never need to read earlier commentary updates for context, since they are collapsed when the final answer is shown to the user.

Write the final answer and all other human-facing material anew for the intended reader. Do not copy or closely paraphrase your reasoning or adopt its writing style. Do not carry over working shorthand, jargon, or abbreviations from your reasoning, tool calls, or instructions to subagents and automations.
```

> 🔴 **누가 읽는지에 따라 ① · ② 를 고른다.** 가이드는 둘을 읽는 사람으로 가른다 — ① 은 모델과 함께 일하는 사용자 본인에게 하는 답, ② 는 사용자를 대신해 바깥 독자(문서·메일·메시지·외부 게시물)에게 보낼 글이다. ① 의 "Keep technical details and use domain-specific language when they make the explanation more precise." 는 설명이 더 정확해질 때만 전문어를 쓰라는 조건부 처방이고 따를 용어도 "terminology the user and sources use" — 사용자와 자료가 쓰는 말이다. 산출 프롬프트가 만들 글을 비개발자·일반 독자·바깥 사람이 읽는다면 ② 의 "consider who will read it and tailor the content to that intended audience" 를 넣고 ① 은 빼거나 「독자가 사용자 본인일 때」 라는 조건을 붙인다. 둘을 조건 없이 같이 넣으면 서로 어긋날 수 있다(편집 판단).

- 직전 판(«Using GPT-6»)의 "Use plain language over jargon" 문구와 상투어 금지 목록은 이 판에 없다 — 가이드가 빼라고 적은 것은 아니다. 옮겨 올 때는 대표 작업으로 다시 재서 남길지 정하고 쉬운 말이 필요한 독자라면 ② 로 푼다(편집 판단).

#### Task completion

가이드 원문: "For work that can proceed without supervision, specify the outcome the model should complete and which decisions need the user’s input."

④ 끝까지 진행 · 멈춤 조건 (원문 · «maketo» 는 가이드 표기 그대로):

```text
Avoid stopping to end the turn while the task is incomplete or if there is an authorized next step you can take, and instead take the next steps within task scope to progress the user's request. If your final response before ending the turn is a suggested next step, a plan, a request to the user for a routine decision, instructions for a task to execute, or similar handoff to the user, take these steps yourself to make progress towards what the user asked for. Make sure that you have authorization to do so, and flag any assumptions or decisions you maketo the user.

Only stop to clarify with the user if there is significant change in task scope, you are concretely blocked, have a decision that the user needs to resolve, or before irreversible or destructive actions.
```

⑤ 완료 확인 · 지속 (원문) — 가이드: "Higher reasoning effort can help it persist through the final checks on complex or long-running tasks."

```text
Bias towards action, and persist until you've completed the task the user asked for. Avoid stopping to end the turn while the task is incomplete or if there is an authorized next step you can take, and instead take the next steps within task scope to progress the user's request. Make sure that you have accounted for every part of the user's request, and persist until you've delivered a result that fully satisfies the user's goal. If a task requires sustained work, do all the necessary work until the intended outcome is completely fulfilled.

Progress autonomously towards the user's goal (e.g. creating isolated worktrees / checkouts if needed, resolving merge conflicts, creating draft PRs etc) unless they are clearly destructive or irreversible. Before ending a turn or calling your work complete, check that your work fully satisfies what the user asked for. If any steps remain or any part of the result still needs verification, follow through on this work before finishing.
```

⑥ 애매할 때 가정하고 진행 (원문):

```text
Make reasonable, reversible assumptions to carry work forward and state them if it progresses the task within scope. Do not second guess yourself, stop after describing what you could do, offer to do the work, or provide a partial answer unless there is no way you can proceed.
```

- 비동기 질문 도구 (원문): "With an async tool such as `request_user_input_async` in your application, GPT-6.2 can ask the user for clarification and continue work that doesn’t depend on the answer." — 앱에 그런 도구가 있을 때만 그 도구를 쓰라는 문장을 넣는다.

#### Coding style

가이드 원문: "Describe the codebase’s conventions and any behavior that existing callers rely on. For example, specify when to reuse existing logic, how narrowly to scope a change, and when to add a test for behavior the existing suite doesn’t cover."

⑦ 코딩 (원문):

```text
Above all, be thorough in producing high-quality, correct code that completely fulfills the user's task. Keep the code easy to read and verify that the user-requested outcome works as they intend. Follow these instructions when coding:

(a) Reuse existing logic in the user's repo when you can. You should reuse existing classes, methods, representations, and APIs in the codebase as long as they preserve correctness. Before consolidating or removing code, preserve the behavior its callers rely on unless the task requires changing it.
(b) Skip new tests unless requested, required by the repo, or needed to catch a specific regression existing tests would miss.
(c) Make sure that code is human readable. Do not use fewer lines, shorter variable names, minified formatting, or dense one-liners as substitutes for simplicity. Ensure that comments and variable names are readable and understandable to a human. Code-golfed expressions count as overly complex when they encode many branches, conditions, or hidden assumptions.
(d) Avoid unnecessary indirection and abstraction. Helper functions, utility functions, and class abstractions can add cognitive complexity even when they do not add branches.
```

- (b) 테스트 처방은 직전 판보다 범위가 넓다. 직전 판 "Do not write tests for reversible, low-impact changes that mirror the implementation." 은 되돌릴 수 있고 영향이 작은 변경에서 구현을 그대로 따라 하는 테스트만 막았고 이 판은 세 예외(요청 · 저장소 요구 · 기존 테스트가 놓칠 회귀) 밖이면 새 테스트를 건너뛰라고 한다.
- GPT-5.6 필수 블록 `# Validation`(가장 관련 있는 검증 실행)과 같이 넣을 때는 「새 테스트 작성」과 「기존 검사 실행」을 갈라 적는다 — (b) 는 새 테스트에 대한 문장이다(편집 판단).

#### Frontend design

가이드 원문: "If the application depends on a specific visual style, describe it in the prompt." · "Keep interface copy focused on what people need to know or do."

⑧ 프런트엔드 (원문):

```text
When generating webpages or apps with a frontend user interface, follow these instructions:

- When choosing visuals, generally prefer realistic images from ImageGen or image search that suit the project's style and purpose. Use SVGs when the user specifically asks for them.
- Include a text element only when it provides information the user needs, helps them navigate or act, or fulfills an explicit content request. Remove decorative numbering, filler badges, redundant headings, and explanatory copy that merely restates what the surrounding interface already makes clear, while preserving necessary labels, instructions, and status feedback.
```

- 참조 이미지 (원문): "A reference can enrich your prompt with details that are hard to describe in words." → "ask the model to build the asset, render it, and refine it against the reference." — 디자인 도구의 참조 이미지를 주거나 이미지 생성 도구로 만들게 한 뒤, 그 참조에 맞춰 만들고 렌더링하고 다듬게 한다.

### 매개변수 · 옮길 때 바꿀 값 (가이드 «Migration quickstart» 원문)

| 항목 | GPT-6.2 원문 | 직전 판(GPT-6) |
|---|---|---|
| reasoning effort | "Start with `medium` for a new integration. If you currently use `none` or `minimal`, use `low` instead." · 필드 = Responses `reasoning.effort` / Chat Completions `reasoning_effort` | 현 effort 보존(아래 «GPT-6 Sol · Luna» 절 마이그레이션 원문) |
| 도구 호출 | "GPT-6.2 Astra and GPT-6.2 Sol support Chat Completions, but tool calling requires Responses." | GPT-6 Sol·Luna = Chat Completions 함수 호출은 `reasoning_effort: "none"` 일 때만 |
| 안 받는 매개변수 | "When migrating Chat Completions requests, omit `temperature`, `top_p`, `logprobs`, and `top_logprobs`. For Responses requests, omit `temperature`, `top_p`, and `top_logprobs` and remove `message.output_text.logprobs` from `include`." | effort ≠ `none` 일 때 제거(조건부) |
| 프롬프트 캐시 | "When migrating from GPT-5.5 or earlier, replace `prompt_cache_retention` with `prompt_cache_options.ttl` set to `"30m"`." | 같음 |
| ZDR | "With ZDR enabled, the Responses API treats `store` as `false`. For multi-turn work, pass the prior output items back in order, including encrypted reasoning items." (승인된 조직 · 대상 엔드포인트만) | 이 항목 없음 |
| 처리 등급·지역 | "Ultrafast supports US data residency only." (US·EU = Standard · Fast · Batch) | 모델마다 다름 |

- effort 는 `medium` 에서 시작해 대표 작업에 돌려 보며 올리거나 내린다. 긴 작업의 마지막 확인이 약하면 올리는 쪽(위 ⑤ 의 가이드 문장).
- `text.verbosity` 는 이 가이드에 나오지 않는다(확인 범위 내 미발견). 기본 길이가 짧은 쪽이라는 성향(위 표)부터 보고 필요한 길이·구조는 프롬프트에 적는다.

### 직전 판(GPT-6)에서 바뀐 것 — 옮겨 올 때 고칠 문구

1. **글쓰기 처방이 바뀜** — 직전 판의 쉬운 말 처방("Use plain language over jargon")과 상투어 금지 목록(«"delve," "foster," "leverage,"» 등)이 없다. 이 판 = ① 사용자 용어 따르기 + ② 독자 맞춤.
2. **기본 길이** — 직전 판은 상세·포맷팅 쪽으로 기운다고 보고 문단 위주로 누르는 문구를 줬다. 이 판은 기본이 더 짧고 직설적이다 → "간결하게" 류는 빼거나 다시 잰다.
3. **확인 질문 성향** — 직전 "more likely to ask for clarification where earlier models would make assumptions" → 이 판 "may propose a next step and wait for confirmation". 처방 방향은 둘 다 「더 밀고 나가게」.
4. **테스트** — 위 Coding style (b).
5. **effort** — 현 effort 보존 → `medium` 에서 시작.
6. **새로 생긴 것** — reasoning items 버림 · 최종 답 자족(③) · 코드 가독성 (c) · 추상화 줄이기 (d) · 프런트엔드(⑧) · ZDR.

### 마이그레이션 체크 (GPT-6 Astra · GPT-6 Sol · GPT-5.6 Sol → GPT-6.2)

1. 모델명 교체 — `gpt-6.2-sol`(디폴트 · 복잡한 작업을 낮은 비용으로) 또는 `gpt-6.2-astra`(가장 어려운 작업). GPT-6 Luna 로 돌리던 대량·반복 작업은 6.2 판이 없으니 그대로 두거나 GPT-6.2 Sol 과 비용·품질을 비교한다.
2. effort = `medium` 에서 시작 · `none`/`minimal` 을 쓰던 곳은 `low` (위 표).
3. 도구 호출 = Responses API.
4. 안 받는 매개변수 제거 (위 표 — 가이드 원문은 effort 조건을 달지 않는다).
5. 대화 중간에 앞쪽 기록·지시문을 고치지 않는다 (reasoning items 버림 · 위 절).
6. 직전 판 문구 정리 — 상투어 금지 목록 · 쉬운 말 처방 · 문단 위주 누르기 · "간결하게" 를 빼거나 다시 잰다.
7. 글을 읽을 독자를 정하고 ① / ② 를 고른다 · 긴 작업이면 ③.
8. 나머지 원칙은 위 «마이그레이션 (GPT-5.5 → GPT-5.6)» 그대로 — 변경 전 대표 eval, 측정된 회귀만 가장 작은 지시로 고치기, 통째 재작성 ❌.

코딩 에이전트로 옮길 때 (원문): "To migrate an API application to GPT-6.2 Astra with a coding agent" — [OpenAI Docs skill](https://github.com/openai/codex/tree/main/codex-rs/skills/src/assets/samples/openai-docs) 사용.

---

## GPT-6 Astra (2026-09-01~, GPT-5.6 Sol 다음 세대)

> **공식 출처**: [Using GPT-6 Astra](https://developers.openai.com/api/docs/guides/latest-model) — 접근일 2026-09-05
> 모델 ID = `gpt-6-astra`(스냅샷·별칭 1개) · context 1,050,000(최대 입력 922,000) · 최대 출력 128,000 · reasoning.effort "`low` · `medium` · `high` · `xhigh` · `max` — 🔴 **`none` 미지원**" · 장문 할증: "**272K 입력 초과 요청은 전체 요청에 입력·캐시 2배, 출력 1.5배**" · 추론 모델은 Responses API 사용 권장

### 트리거 조건

- 사용자가 "GPT-6 Astra", "gpt-6-astra" 명시 (변형 없이 "GPT-6" 만 적어도 이 절 · 맨 "Astra" 단독은 GPT-6.2 Astra 와 겹치므로 세대를 확인)
- 모델 미지정 = 이 절이 아니라 위 «GPT-6.2 Astra · Sol» 절 — GPT 디폴트 = GPT-6.2 Sol(2026-11-17~), GPT-6 Sol = 직전 디폴트, GPT-5.6 Sol = 그 전 디폴트. (이전 판의 「GPT 기본 모델이 Astra 로 전환된 이후」 조건은 GPT-6 Sol 출시로 대체)

### 마이그레이션 필수 3건 (5.6 → Astra)

- effort `none`/`minimal` → **`low`** 로 교체 — "effort `none`/`minimal` → **`low`** 로 교체 (`none` 미지원)"
- 대화 중 추론 강도 변경은 요청 재전송 대신 `configuration_update` 항목으로 — "요청 수준 effort 변경 대신 **`configuration_update` 항목** 적용" (요청 수준 `reasoning.effort` 는 그대로 두어 "요청 수준 `reasoning.effort` 는 그대로 두므로 **프롬프트 접두부 캐시가 유지**된다.")
- Chat Completions 은 `temperature`·`top_p`·`top_logprobs`(+`logprobs`) 제거, 도구 호출은 **Responses API** 사용 권장

### 행동 성향 5가지 — 공식 교정 프롬프트

Astra 는 GPT-5.6 Sol 과 **반대 방향** 튜닝이 필요하다. GPT-5.6 Sol 은 「간결하게」 광범위 지시를 눌러 앉혀야 했다면(위 Anti-Patterns 표), Astra 는 **과잉 승인 요청·과잉 포맷팅·과잉 테스트**를 눌러 앉혀야 한다.

| 성향 | 공식 서술 | 교정 프롬프트 요지 |
|---|---|---|
| 주도성·완수 | 입력이 결과를 실질적으로 바꿀 수 있으면 **질문한다** → 사용자가 「알아서 가정하고 계속하길」 기대할 때 멈춘다 | 되돌릴 수 있는 작업은 승인 없이 진행 — "unless they are clearly destructive or irreversible." 만 예외 |
| 승인 순서 | 🔴 승인은 **마지막 단계**로 | "The user should be approving a concrete, reviewable result." — 배포·PR 머지·게시 전 필요한 작업을 다 끝내 놓고 승인만 남긴다 |
| 지시 따르기 | skills·`AGENTS.md` 등 파일 안 지시에 더 민감 | "auditing skills and other files accessible to your model for instructions that could influence its behavior." (strongly recommend) |
| 지시 따르기(투명성) | 스킬이 확인·중단을 유발하면 출처 명시 | "name and link to the exact SKILL.md file you read, quote the relevant instruction, and briefly explain how it applies." |
| 성격·문체 | 상세·포맷팅된 응답으로 기운다 — **산문 쪽으로 눌러야** · **GPT-6 판 한정**(GPT-6.2 는 기본이 더 짧고 직설적 · 위 «GPT-6.2 Astra · Sol» 절) | "Use lists only when the information is genuinely parallel, sequential, or easier to compare" |
| 상투어(slop) 차단 | 금지 어휘가 구체적 · **GPT-6 판 한정**(GPT-6.2 가이드에는 이 목록이 없다 · 위 «GPT-6.2 Astra · Sol» 절) | "Avoid using slop words or phrases like "Bottom Line:" in conclusions, "delve," "foster," "leverage,"" 등 |

```text
You should infer the user's intent and task scope from the instructions and prior conversation context. Your job is to bias towards action and carry the user's intended task to completion.
```

```text
Before asking the user clarifying questions, you should complete the work that is already authorized from context and necessary to make the proposed action concrete and reviewable. The user should be approving a concrete, reviewable result.
```

⚠️ **계보 간 충돌** — 위 성격·문체 교정(산문 쪽으로 누르기)은 GPT-5.6 Sol 절의 Anti-Patterns("간결하게/짧게" 광범위 지시 역효과)와 방향이 같다. 단 Claude 계열 Fable 5.1(`claude-fable-5-prompt-strategies.md` Part 2.6.3)은 **정반대**(안티-포맷팅 규칙 제거)를 요구한다 — 모델 계열이 다르면 같은 규칙을 이식하지 말 것. (Fable 5.2 가이드에는 채팅 포맷팅 절이 없다 — 확인 범위 내 미발견. Fable 5.2 대상은 같은 파일 Part 2.8 을 따르고, 필요 없어진 딱딱한 문체 규칙은 뺀다.)

### 서브에이전트 위임 · 테스트·검증

- 위임: "If at any point you can parallelize work by delegating tasks to another agent (no matter if you are the root or subagent), you should do so using collaboration tools if it could save time or improve quality."
- 에이전트 간 메시지: "Messages that you send to other agents and your final answer may be read by a human, so ensure they are legible."
- 테스트 (**GPT-6 판 한정** — GPT-6.2 는 위 «GPT-6.2 Astra · Sol» 절 Coding style (b)): "Do not write tests for reversible, low-impact changes that mirror the implementation. If you do choose to verify your work with tests, make sure that the tests are meaningful and necessary to verify implementation."

### 새 기능 3+1 (프롬프트 설계에 영향)

- **비동기 도구 호출**(`async: true`) — 호출 대기 없이 다른 도구·추론 계속, 결과는 같은 `call_id` 로 나중 반환
- **턴 중간 조종(mid-turn steering)** — WebSocket 으로 작업 중 추가 지시, 완료된 작업은 보존
- **대화 중 추론 강도 변경** — `configuration_update`, GPT-6 패밀리 표준 단일 에이전트 모드에서 지원(reasoning 가이드: "supported by the GPT-6 model family in standard, single-agent mode")
- 비동기 오정렬 모니터링

---

## GPT-6 Sol · Luna (2026-09-22~, 직전 GPT 디폴트 = GPT-6 Sol)

> **공식 출처** (접근일 2026-09-27): [Using GPT-6](https://developers.openai.com/api/docs/guides/latest-model) (GPT-6 패밀리 가이드) · 모델 카드 [gpt-6-sol](https://developers.openai.com/api/docs/models/gpt-6-sol.md) · [gpt-6-luna](https://developers.openai.com/api/docs/models/gpt-6-luna.md) · [출시 공지](https://openai.com/index/introducing-gpt-6-sol-and-luna/) · 매개변수 = [reasoning 가이드](https://developers.openai.com/api/docs/guides/reasoning.md) · [배포 체크리스트](https://developers.openai.com/api/docs/guides/deployment-checklist.md) · [API changelog](https://developers.openai.com/api/docs/changelog.md)
> 모델 ID = `gpt-6-sol` · `gpt-6-luna` (모델 카드에 스냅샷 각 1개) · API 출시 2026-09-22 — changelog 원문 "Released GPT-6 Sol (`gpt-6-sol`) and GPT-6 Luna (`gpt-6-luna`)." · 지식 컷오프 GPT-6 Sol = Apr 20, 2026 / GPT-6 Luna = May 18, 2026 · 기본 reasoning effort = `medium`

### 공식 출처와 한계

- **GPT-6 Sol·Luna 전용 프롬프트 가이드·쿡북·마이그레이션 가이드 = 확인 범위 내 미발견** (2026-09-27). docs 색인(`llms.txt`)의 GPT-6 항목은 «Using GPT-6» 하나이고, 전용 후보 주소 4곳(`guides/latest-model/gpt-6-sol.md` · `guides/latest-model/gpt-6-luna.md` · `guides/prompt-guidance-gpt-6.md` · `guides/upgrading-to-gpt-6.md`)은 404.
- 따라서 이 절의 근거 = 패밀리 가이드 «Using GPT-6» + 모델 카드 2 + 출시 공지. GPT-6 Sol 과 GPT-6 Luna 를 **서로 다르게 프롬프트하라는 절은 확인 범위 내 미발견** — 이 절은 둘을 함께 다루고, 차이는 용도·매개변수로만 적는다.
- 패밀리 가이드의 예시 프롬프트는 스스로 범위를 이렇게 한정한다:

  > "Use the following prompts as a starting point across the GPT-6 model family. They address behavior observed with GPT-6 Astra; evaluate them with your chosen model and workload."

- 연 페이지에서 "breaking change" 표현, GPT-6 Sol·Luna 의 `text.verbosity` 값 변경·폐지 문장 = 확인 범위 내 미발견.
- ⚠️ `openai/codex` 저장소의 `references/upgrading-to-gpt-6-astra.md` 로컬 사본은 라이브 문서보다 오래되어 빠른/저가 작업을 `gpt-5.6-luna`, 균형 작업을 `gpt-5.6-terra` 로 매핑하고 `gpt-6-sol` 을 적지 않는다. 그 파일 스스로 라이브 문서를 canonical 로 지정하므로 현재 권고로 쓰지 않는다.

### 트리거 조건

- 사용자가 "GPT-6 Sol", "gpt-6-sol", "GPT-6 Luna", "gpt-6-luna" 명시
- GPT 모델 미지정 = 이 절이 아니라 위 «GPT-6.2 Astra · Sol» 절(GPT 디폴트 = GPT-6.2 Sol, 2026-11-17~ · GPT-6 Sol = 직전 디폴트). 작업이 대량·반복·효율 위주면 GPT-6 Luna(6.2 판 없음 → 이 절)를 선택지로 제시
- 🔴 **맨 "Sol" 단독은 트리거로 쓰지 않는다** — GPT-6.2 Sol · GPT-6 Sol · GPT-5.6 Sol 이 이름이 겹친다. 세대가 적혀 있지 않으면 어느 쪽인지 확인하고, 산출 프롬프트에도 항상 `GPT-6 Sol` / `GPT-5.6 Sol` 로 세대를 붙인다
- "GPT-5.6", "GPT-5.6 Sol" 명시 = 위 GPT-5.6 절(그 전 디폴트) · "GPT-6 Astra", "gpt-6-astra" 명시 = 위 GPT-6 Astra 절 · "GPT-6.2" 계열 명시 = 위 «GPT-6.2 Astra · Sol» 절

### 모델 선택 — Astra / GPT-6 Sol / GPT-6 Luna

| 모델 | ID | 패밀리 가이드 원문 | 모델 카드·공지 원문 |
|---|---|---|---|
| GPT-6 Astra | `gpt-6-astra` | "Use gpt-6-astra for our highest level of capability" | "GPT-6 Astra continues to be our best model across the board. Choose it when you want the best results and an uncompromising experience." (출시 공지) |
| **GPT-6 Sol** (직전 디폴트) | `gpt-6-sol` | "gpt-6-sol for strong reasoning on demanding tasks" | "GPT-6 Sol is built for complex coding and agentic workflows." (모델 카드) |
| GPT-6 Luna | `gpt-6-luna` | "gpt-6-luna for efficient, repeatable work at scale." | "GPT-6 Luna is our most efficient model for focused, high-volume tasks." (모델 카드) |

- 배포 체크리스트 표현: "gpt-6-sol for demanding reasoning and coding, and gpt-6-luna for efficient, repeatable work."
- 출시 공지의 GPT-6 Sol 서술: "GPT-6 Sol can take on difficult work tasks while giving you more room to iterate with higher usage limits and lower cost"
- 가용성(출시 공지): "Free and Go users can access GPT-6 Luna in the desktop app. These models are not yet available in Chat. In the OpenAI API, they are available as `gpt-6-sol` and `gpt-6-luna`." — ChatGPT 채팅용 프롬프트를 쓸 때 모델 가용성부터 확인.

### 매개변수

| 항목 | GPT-6 Sol · GPT-6 Luna | GPT-6 Astra (비교) |
|---|---|---|
| reasoning effort | `none` · `low` · `medium` · `high` · `xhigh` · `max`, 기본 `medium` | `none` 미지원 (`low`~`max`) |
| 기존 `minimal` | `low` 로 시작해 대표 작업에서 비교 | 동일 |
| Chat Completions 함수 호출 | `reasoning_effort: "none"` 일 때만 → 추론+도구 = Responses | Responses 전용 |
| 샘플링 매개변수 | effort ≠ `none` 이면 제거 | 제거 |
| 턴 중 effort 변경 | `configuration_update` | `configuration_update` |
| 출력 상세도 | `text.verbosity` (`low` / `medium` / `high`) | 동일(배포 체크리스트 예제 모델 = GPT-6 Astra · GPT-6 Sol·Luna 별도 표기 없음) |

- effort 원문: "If you omit `reasoning.effort`, GPT-5.6 defaults to `medium` in both modes. GPT-6 Sol and Luna also default to `medium` reasoning effort."
- 마이그레이션 원문 (**GPT-6 판 한정** — GPT-6.2 는 `medium` 에서 시작 · 위 «GPT-6.2 Astra · Sol» 절): "Preserve your current effective reasoning effort where supported. GPT-6 Astra does not support `none`; use `low` instead. GPT-6 Sol and Luna support `none`. If your existing request uses `minimal`, start with `low` and compare results on representative tasks."
- 도구 호출 원문: "GPT-6 Sol and Luna support function calling in Chat Completions only with `reasoning_effort: \"none\"`. Use Responses for reasoning with tools."
- 샘플링 원문: "When reasoning effort is not `none`, remove `temperature`, `top_p`, and `top_logprobs`. For Chat Completions, also remove `logprobs`. For Responses, remove `message.output_text.logprobs` from `include`."
- `configuration_update` 원문: "Add a `configuration_update` input item to increase reasoning effort for difficult work or reduce it for routine follow-ups without rewriting the original prompt prefix." · reasoning 가이드: "Configuration updates are supported by the GPT-6 model family in standard, single-agent mode. They change only reasoning effort."
- `text.verbosity` 원문(배포 체크리스트 — 예제 모델은 `gpt-6-astra`, GPT-6 Sol·Luna 를 따로 적지 않음): "`text.verbosity` is the main lever for balancing brevity against completeness." · "When migrating, check whether broad instructions like \"Be concise\" still help. Prefer `text.verbosity` to control the default level of detail, then use the prompt to specify required content, structure, and length."
- effort 고르는 방법은 위 «Reasoning Effort 권장값 (5.6 기준)» 을 출발점으로 쓴다 — 현 effort 를 baseline 으로 보존하고 대표 eval 로 비교하는 방향이 위 마이그레이션 원문과 같다.

### 프롬프트 작성

**구조 = 위 GPT-5.6 7블록(Role · Personality · Goal · Success Criteria · Constraints · Tools · Output · Stop Rules)을 그대로 출발점으로.** GPT-5.6 가이드의 simplify prompts first · outcome-first · stopping conditions · tool routing · Programmatic Tool Calling · grounding · suggested prompt structure 는 GPT-6 가이드 Prompting best practices 에 **재수록되지 않았으나 폐지 표기도 없다**(확인 범위 내 미발견). 7블록을 유지하고, 아래 예시 문구를 해당 블록에 필요한 것만 넣는다.

> 🔴 **아래 예시 = Astra 관찰 기반 출발점.** 가이드 원문: "They address behavior observed with GPT-6 Astra; evaluate them with your chosen model and workload." — GPT-6 Sol·Luna 가 같은 성향을 보인다고 문서가 보장하지 않는다. 넣기 전에 GPT-6 Sol·Luna 의 기본 출력을 자기 워크로드로 먼저 평가하고, 실제로 관찰된 문제에 맞는 문구만 추가한다.

가이드가 GPT-5.6 Sol 과 직접 비교한 문장도 Astra 에 대한 것이다: "GPT-6 Astra is generally better than GPT-5.6 Sol and earlier models at staying coherent during long tasks. It is also more likely to ask for clarification where earlier models would make assumptions."

| 예시 문구 | 넣을 블록 위치(7블록 + 필수 블록) | 이 문서의 대응 절(편집 판단) |
|---|---|---|
| 자율 진행 | `# Autonomy` | Initiative and follow-through |
| 요청 = 실행 지시 | `# Autonomy` / `# Stop Rules` | Initiative and follow-through |
| 승인 전 검토 가능한 결과 | `# Autonomy` | Initiative and follow-through |
| 스킬보다 사용자 지시 | `# Constraints` | Instruction following |
| 문단 위주 문체 (**GPT-6 판 한정** — GPT-6.2 는 위 «GPT-6.2 Astra · Sol» 절 ① · ②) | `# Output` | Personality and writing style |
| 테스트 조절 (**GPT-6 판 한정** — GPT-6.2 는 위 «GPT-6.2 Astra · Sol» 절 Coding style (b)) | `# Validation` | Testing and verification |

자율 진행 (원문):

```text
You should infer the user's intent and task scope from the instructions and prior conversation context. Your job is to bias towards action and carry the user's intended task to completion.

When the user expresses intent to perform new work or fix an existing issue, persist until the user's intended goal is complete. Progress autonomously towards the user's goal (e.g. creating isolated worktrees / checkouts if needed, resolving merge conflicts, read-only actions, creating draft PRs etc.) unless they are clearly destructive or irreversible.
```

요청을 실행 지시로 다루기 (원문):

```text
When the user's prompt indicates a request for action, such as "can you...", "I want to...", "help me..." and similar expressions, treat these as instructions to do the work and take action. Do not stop at acknowledging capability (e.g. "Yes…"), proposing a plan, or offering to continue. Do not settle for a partial or "helpful enough" solution that does not fully satisfy the user's task to save time, effort or tokens. If a task requires sustained work, complete all the necessary work until the intended outcome is fulfilled.
```

승인 전에 검토 가능한 결과까지 (원문):

```text
Before asking the user clarifying questions, you should complete the work that is already authorized from context and necessary to make the proposed action concrete and reviewable. The user should be approving a concrete, reviewable result. For example, before deploying a change, writing to an external application, merging a PR or publishing a site, do all the required work first so that user approval is the final step. You don't need user permission for reversible tasks, read-only actions, reviews or fixes, or anything for which authorization is provided earlier in the session or strongly implied from the task instruction.

Do not introduce unsolicited warnings, disclaimers, approval flows, or safety/compliance checklists due to hypothetical risk.
```

스킬보다 사용자 지시 (원문):

```text
The user's instructions take precedence over guidelines provided in a skill. If explicit user instructions conflict with a skill's instructions, prioritize the user's instructions.
```

문단 위주 문체 (원문 · **GPT-6 판 한정** — GPT-6.2 는 위 «GPT-6.2 Astra · Sol» 절 ① · ②):

```text
Default to using clear, concise paragraphs, each developing one main idea. Use lists only when the information is genuinely parallel, sequential, or easier to compare, and avoid nested lists unless the hierarchy cannot be expressed clearly in prose. Use plain, simple language: familiar words, concrete examples, and precise verbs. Prefer active voice and direct statements.

Make sure to state the main point clearly and early, then develop it with the explanation and detail the reader needs. Let each sentence build on what came before. Develop the points that matter and provide enough support to be useful.
```

테스트 조절 (원문 · **GPT-6 판 한정** — GPT-6.2 는 위 «GPT-6.2 Astra · Sol» 절 Coding style (b)):

```text
Do not write tests for reversible, low-impact changes that mirror the implementation. If you do choose to verify your work with tests, make sure that the tests are meaningful and necessary to verify implementation.

Run tests appropriate to the change and complete required checks. Once those pass, broaden or repeat testing only when new changes, failures, or unresolved concerns justify it; otherwise, continue toward completing the task.
```

- 상투어 줄이기·서브에이전트 위임 문구는 위 GPT-6 Astra 절에 인용돼 있다. 같은 전제(Astra 관찰 기반 출발점)로 필요할 때만 가져온다.
- 테스트 조절은 GPT-5.6 필수 블록 `# Validation`(가장 관련 있는 검증 실행)과 방향이 다르다 — GPT-5.6 가이드는 코딩 후 검증을 돌리라고 하고, GPT-6 가이드는 작은 변경에서 테스트가 과해질 수 있다고 적는다(대상 = Astra). 두 문구를 같이 넣을 때는 GPT-6 Sol·Luna 의 실제 테스트 범위를 먼저 확인한다.

### 문체 — 출시 공지 기준

**출시 공지 기준으로, Astra 의 소통 문체가 GPT-6 Sol·Luna 에 적용되었다.** 이것은 프롬프트 가이드가 아니라 제품 공지의 기본 동작 서술이다.

> "We've also brought GPT-6 Astra's improved communication style to Sol and Luna... Expect to see more clarity, less jargon, fewer odd turns of phrase, fewer low-value details, and slightly shorter answers overall without losing substance."

- (GPT-6 판 기준 — GPT-6.2 는 기본이 더 짧고 직설적이라 가이드가 "간결하게" 류를 다시 보라고 직접 적는다 · 위 «GPT-6.2 Astra · Sol» 절) GPT-5.6 Sol 용으로 쓰던 문체·길이 지시("간결하게" 등)는 GPT-6 Sol·Luna 에서 그대로 필요한지 다시 잰다 — 배포 체크리스트의 "check whether broad instructions like \"Be concise\" still help" 와 같은 방향. 기본 상세도는 `text.verbosity`, 프롬프트는 필수 내용·구조·길이만.
- 공지의 "verbosity sweeps" 는 사실성 평가 방법이지 매개변수 변경이 아니다: "our verbosity sweeps showed almost no dependence on answer length."
- **여러 모델이 함께 쓰는 지시문 주의.** 공식 Astra 블로그 글(https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra.md) 원문: "Guidance that helps Sol or Luna may overconstrain GPT-6 Astra, so consider which models will use the instructions you leave behind." — `AGENTS.md`·스킬 파일처럼 GPT-6 Astra 와 GPT-6 Sol·Luna 가 같이 읽는 지시문에 GPT-6 Sol·Luna 용 보강을 넣을 때는 어느 모델이 읽는지 먼저 따진다. 같은 글은 GPT-6 Sol·Luna 용으로 무엇을 새로 넣으라고는 적지 않는다.

### 마이그레이션 체크 (GPT-5.6 Sol → GPT-6 Sol / GPT-6 Luna)

1. 모델명 교체 — `gpt-6-sol`(어려운 추론·코딩·에이전트) 또는 `gpt-6-luna`(대량·반복·효율)
2. **현 reasoning effort 보존** — "Preserve your current effective reasoning effort where supported." (`none` 은 GPT-6 Sol·Luna 에서 그대로 가능) — **GPT-6 판 한정**(GPT-6.2 로 옮길 때는 `medium` 에서 시작 · 위 «GPT-6.2 Astra · Sol» 절)
3. `minimal` → **`low`** 로 시작, 대표 작업에서 비교
4. effort ≠ `none` 이면 `temperature` · `top_p` · `top_logprobs` 제거 / Chat Completions 은 `logprobs` 도 제거 / Responses 는 `include` 에서 `message.output_text.logprobs` 제거
5. 추론 + 도구 = **Responses 로 전환** — Chat Completions 함수 호출은 `reasoning_effort: "none"` 일 때만
6. 대화 중 effort 변경 = 요청 수준 `reasoning.effort` 는 두고 `configuration_update` 항목으로 (원래 프롬프트 접두부를 다시 쓰지 않음)
7. 문체·길이 지시 재평가 → `text.verbosity` 우선 (위 «문체 — 출시 공지 기준»)
8. Astra 관찰 기반 예시 문구는 GPT-6 Sol·Luna 워크로드 eval 로 확인된 문제에만 추가 · 여러 모델이 공유하는 지시문 점검
9. 나머지 절차는 위 «마이그레이션 (GPT-5.5 → GPT-5.6)» 원칙 그대로 — 변경 전 대표 eval, 측정된 회귀만 가장 작은 지시로 고치기, 통째 재작성 ❌

Codex 로 옮길 때 (가이드 «Migrate with Codex» 원문):

```text
$openai-docs migrate this project to the GPT-6 model family
```

---

# 📦 LEGACY — GPT-5.5 outcome-first / GPT-5.4·5.2 XML stack (명시 요청 시 fallback)

> 아래는 이전 세대 패턴 보존분이다. 사용자가 "5.5", "5.4 XML 스타일", "legacy XML stack", 또는 GPT-5.5/5.4/5.2/5/4o 이하 모델을 명시할 때만 적용. 그 외 GPT 작업은 위 절 사용 — 모델 미지정 = GPT-6.2 Astra · Sol 절(GPT 디폴트 = GPT-6.2 Sol), GPT-6 명시 = GPT-6 절(직전 디폴트), GPT-5.6 명시 = GPT-5.6 lean outcome-first(그 전 디폴트).

## ▼ GPT-5.5 / 5.4 / 5.2 패턴 (원본 보존)

> **provenance**: 아래는 구 `gpt-5.5-prompt-enhancement.md` v1.1.0 (2026-04-30)에서 이관·보존한 원본이다.

### [LEGACY] 핵심 변화 요약 (GPT-5.4 → GPT-5.5)

| 항목 | GPT-5.4 | GPT-5.5 |
|------|---------|---------|
| 기본 구조 | XML 12블록 stack | Markdown 6섹션 (outcome-first) |
| 절차 지시 | step-by-step 명시 권장 | destination + success criteria 우선 |
| 절대 규칙 | ALWAYS / NEVER 사용 | judgment 영역에선 자제 |
| Reasoning effort | 기본 medium~high | **low/medium 우선**, 부족할 때만 escalate |
| Retrieval | 적극 권장 | budget 정의 (빈도 줄임) |
| Output 형식 | 구조화 디폴트 | plain paragraph 디폴트, bullets sparingly |
| Verbosity | output_verbosity_spec 블록 | text.verbosity = "low" + 짧은 contract |

### [LEGACY] GPT-5.5 트리거 조건 (5.5 시절 기준)

- 사용자가 "GPT-5.5용 프롬프트", "ChatGPT GPT-5.5", "Codex GPT-5.5" 명시
- Batch 모드에서 첫 토큰이 `GPT-5.5` 일 때
- ⚠️ **5.5 시절 기본값 — 현재 기본은 GPT-6.2 Sol (GPT-6 Sol = 직전 디폴트 · GPT-5.6 Sol = 그 전 디폴트)**: 모델 미지정 + 일반 Q&A/단순 작업이면 5.5 outcome-first 권장 (legacy 5.4 XML stack은 명시 요청 시만)

> ⚠️ **GPT-5.4 호환**: 사용자가 "5.4 XML 스타일", "legacy XML stack" 등을 명시하면 아래 GPT-5.4/5.2 XML stack 섹션으로 fallback.

## 권장 프롬프트 구조 (Markdown, 6섹션)

```markdown
Role:
[1-2 문장. 기능 + 컨텍스트]

# Personality
[톤·태도·격식. 짧게 유지.]

# Goal
[사용자가 받게 될 최종 산출물 1-2문장.]

# Success Criteria
- [최종 답 전 충족해야 할 조건들]
- [필요 시 검증 통과 / 누락 항목 처리 명시]

# Constraints
- [정책·안전·증거·부작용 한계]
- [사실 조작 금지 / 보존할 것 명시]

# Output
[섹션·길이·톤. 플레인 텍스트 디폴트, 헤더/불릿은 가독성 향상 시만.]

# Stop Rules
- [도구 루프·재시도·중단 조건]
- [매 결과 후 "Can I answer the core request now with useful evidence?" 자가점검]
```

---

## 필수 적용 블록 (6개)

### 1. `outcome_first_structure` — destination 우선 정의

**용도**: 절차보다 산출물과 성공 조건을 먼저 고정.

```markdown
Role:
You are a pragmatic assistant helping the user complete the task end to end.

# Goal
Deliver a usable final artifact that directly satisfies the user's request.

# Success Criteria
- The core request is answered or completed.
- Missing assumptions are stated briefly.
- Any required validation is performed or explicitly marked as not run.
```

### 2. `personality_and_collaboration` — 톤·협업 스타일

**용도**: 톤(Personality)과 상호작용 방식(Collaboration Style)을 짧게 분리 정의.

```markdown
# Personality
Steady, direct, and concise. Be helpful without becoming verbose.

# Collaboration Style
State what you are doing before multi-step tool work. Ask only for the smallest missing input when blocked.
```

**Steady 예시** (공식 가이드):
> "You are a capable collaborator: approachable, steady, and direct. Assume the user is competent and acting in good faith. Stay concise without becoming curt."

**Expressive 예시** (공식 가이드):
> "Adopt a vivid conversational presence: intelligent, curious, playful when appropriate. Be warm, collaborative, and polished."

### 3. `constraints_block` — 압축 제약

**용도**: 정책·증거·부작용 제한을 짧게.

```markdown
# Constraints
- Do not invent facts, metrics, names, dates, or capabilities.
- Preserve existing working behavior unless the user asks to change it.
- Prefer the simplest solution that satisfies the success criteria.
```

### 4. `output_contract` — 응답 형식 계약

**용도**: 응답 구조·길이를 가볍게 명시. `text.verbosity = low` 와 호흡.

```markdown
# Output
Use concise Markdown. Prefer short paragraphs and bullets only when they improve scanability.
Include completed work, validation status, and blockers if any.
```

### 5. `stop_rules` — 도구 루프·종결

**용도**: 불필요한 retrieval/tool loop 차단.

```markdown
# Stop Rules
After each tool result, ask: Can I answer the core request now with useful evidence?
Stop when the success criteria are met.
Retrieve again only when required facts, dates, IDs, documents, or evidence are missing.
```

**Retrieval Budget (공식 가이드 발췌)**:
```text
For ordinary Q&A, start with one broad search using discriminative keywords.
Make another retrieval call only when:
- Top results don't answer core question
- Required fact/parameter/date/ID missing
- User asked for exhaustive coverage or comparison
- Specific document/URL/code artifact must be read
- Answer would contain unsupported factual claim

Do not search to improve phrasing or support non-essential details.
```

### 6. `validation_rules` — 검증 안내

**용도**: 작업 유형별 가벼운 검증 트리거.

```markdown
# Validation
- Coding: run the most relevant targeted test, type check, lint, build, or smoke test.
- Visual: render and inspect for layout, clipping, spacing, and missing content.
- Planning: include requirements, named resources, state transitions, validation commands, and failure behavior.
- Creative drafting: ground product/customer/metric/capability claims in retrieved facts; otherwise label assumptions clearly.
```

---

## Preamble (멀티스텝/도구 작업 시)

```markdown
Before any tool calls for a multi-step task, send a short user-visible update that acknowledges the request and states the first step.
```

도구 1-2회만 쓰는 단순 작업엔 생략.

---

## Phase Parameter (Responses API, 멀티턴)

장기 실행 Responses 워크플로:
- Replay 시 assistant `phase` 보존
- `phase: "commentary"` — intermediate updates
- `phase: "final_answer"` — 최종 답변
- user 메시지에는 `phase` 추가 X

---

## Anti-Patterns (GPT-5.5에서 회피)

| 안티패턴 | 이유 |
|---------|------|
| process-heavy XML stack 그대로 이전 | GPT-5.4 패턴, 5.5는 outcome-first에서 더 잘 동작 |
| ALWAYS/NEVER 절대 규칙 | 판단 영역에선 모델의 추론을 막음 |
| step sequence 강요 | outcome 명확하면 모델이 알아서 처리 |
| 탐색 전 multi-step plan 작성 강요 | 불필요한 token + 탐색 지연 |
| retrieval 기반 wording 다듬기 | retrieval은 사실 보충용 |
| 구조화 포맷 디폴트 | plain paragraph가 더 명확할 때 많음 |
| Codex CLI에 preamble 요구 | 조기 종료 유발 |

---

## Reasoning Effort 권장값 (5.5 기준)

| 작업 | 권장 effort | 비고 |
|------|------------|------|
| 일반 Q&A, 짧은 작업 | `low` | 5.4 대비 1단계 낮춤 |
| 중간 복잡도 분석/추출 | `medium` | 검증 필요시 high로 escalate |
| 장기 코딩, 다단 검증 | `high` | 결과 검증 후 유지/하향 |
| 안전·법률·금융 고위험 | `xhigh` | 변동 적게 |

> 실패하거나 결과가 부족할 때만 effort를 한 단계 올리세요. Reasoning trace 폭주는 비용·지연을 키웁니다.

---

## Creative Drafting Guardrails

슬라이드·카피·리더십 블러브 등:
- 검색된 사실로만 product/customer/metric/capability 클레임 작성
- 특정 이름·1자 데이터·메트릭·고객 결과 발명 금지
- 근거 부족 시 generic 초안 + "labeled assumptions" 명시

---

## Editing Tasks

```markdown
Preserve the requested artifact, length, structure, and genre first.
Quietly improve clarity, flow, and correctness.
```

---

## Migration: GPT-5.4 → GPT-5.5

| 5.4 블록 | 5.5 대체 |
|---------|----------|
| `<output_verbosity_spec>` | `# Output` + `text.verbosity = "low"` |
| `<design_and_scope_constraints>` | `# Constraints` + outcome 명시 |
| `<uncertainty_and_ambiguity>` | `# Stop Rules` 자가점검 |
| `<tool_usage_rules>` | `# Stop Rules` + Preamble |
| `<extraction_spec>` | `# Output` (스키마 명시) + `# Stop Rules` |
| `<output_contract>` | `# Output` (간소화) |
| `<follow_through_policy>` | `# Stop Rules` 통합 |
| `<completeness_contract>` | `# Success Criteria` |
| `<tool_persistence>` | `# Stop Rules` |
| `<dependency_check>` | `# Constraints` |
| `<eagerness_control>` | `# Stop Rules` ("fewest useful tool loops") |
| `<empty_result_recovery>` | `# Stop Rules` 자가점검 |
| `<missing_context_gating>` | `# Stop Rules` (smallest missing field) |

핵심: **블록 12개 스택 → 짧은 6섹션** + 자연어로 절차 압축.

---

## Legacy GPT-5.2/5.4 XML Stack (참조용 — "5.4 XML 스타일" 명시 시 사용)

GPT-5.4 이하 모델 또는 사용자가 "legacy XML 스타일" 명시 시 다음 12 블록을 적용합니다. (이전 별도 파일 `gpt-5.4-prompt-enhancement.md`를 본 섹션으로 통합 — 2026-04-30 v1.1.0)

### 1. `<output_verbosity_spec>` — 장황함 제어 (항상 포함)

```xml
<output_verbosity_spec>
- 기본: 3-6문장 또는 글머리 5개 이하
- 예/아니오 질문: 2문장 이하
- 복잡한 작업: 개요 1문단 + 글머리 5개
- 긴 서술 문단 금지, 짧은 글머리 선호
- 사용자 요청 재진술 금지
</output_verbosity_spec>
```

### 2. `<design_and_scope_constraints>` — 범위 제약 (코딩/디자인)

```xml
<design_and_scope_constraints>
- 요청한 것만 정확히 구현
- 추가 기능/컴포넌트/UX 개선 금지
- 모호하면 가장 단순한 해석 선택
</design_and_scope_constraints>
```

### 3. `<uncertainty_and_ambiguity>` — 불확실성 처리 (분석/리서치)

```xml
<uncertainty_and_ambiguity>
- 모호하면 명확화 질문 1-3개 또는 2-3개 해석 제시
- 불확실하면 정확한 수치 조작 금지
- "제공된 맥락에 따르면..." 표현 사용
</uncertainty_and_ambiguity>
```

### 4. `<tool_usage_rules>` — 도구 사용 (에이전트)

```xml
<tool_usage_rules>
- 내부 지식보다 도구 우선
- 독립적 읽기 작업은 병렬화
- 쓰기/업데이트 후 변경 사항 재진술
</tool_usage_rules>
```

### 5. `<extraction_spec>` — 구조화된 추출 (PDF/Office)

```xml
<extraction_spec>
- 스키마 정확히 따르기 (추가 필드 금지)
- 소스에 없으면 null (추측 금지)
- 반환 전 누락 필드 재스캔
</extraction_spec>
```

### 6. `<output_contract>` — 출력 계약 (GPT-5.4)

```xml
<output_contract>
- format: [markdown | json | plain_text | xml]
- max_length: [토큰 수 또는 "as_needed"]
- structure: [headings | bullet_list | numbered_steps | table]
- language: [ko | en | match_input]
</output_contract>
```

### 7. `<follow_through_policy>` — 후속 이행 (에이전트)

```xml
<follow_through_policy>
- 도구 호출 실패 시: 1회 재시도 후 사용자에게 알림
- 빈 결과 시: 대안 검색어로 재시도 (최대 2회)
- 부분 결과 시: 있는 결과로 진행, 누락 부분 명시
- 사용자 확인 필요 시: 명확화 질문 1개 (선택지 포함)
</follow_through_policy>
```

### 8. `<completeness_contract>` — 완전성

```xml
<completeness_contract>
- 입력 목록의 모든 항목을 처리할 것
- 처리 완료 후 누락 항목 체크리스트 실행
- 누락 발견 시 즉시 보충 (사용자 확인 불필요)
- 최종 출력에 "처리 완료: N/N건" 표시
</completeness_contract>
```

### 9. `<tool_persistence>` / `<dependency_check>` / `<parallel_calling_strategy>` — 에이전틱

```xml
<tool_persistence>
- 도구 호출 실패 시 즉시 포기하지 말 것
- 대안 파라미터로 재시도 (최대 2회)
- 모든 재시도 실패 시에만 사용자에게 보고
</tool_persistence>

<dependency_check>
- 행동 전 전제 조건 확인
- 부재 시: 도구로 탐색 → 없으면 질문
- 가정으로 진행하지 말 것
</dependency_check>

<parallel_calling_strategy>
- 독립적인 정보 수집은 동시에 실행
- 의존 관계가 있는 호출은 순차 실행
</parallel_calling_strategy>
```

### 10. `<eagerness_control>` — 적극성 제어

```xml
<eagerness_control>
- 탐색 과잉 방지: 요청 범위 내에서만 행동
- 탐색 부족 방지: 모호한 요청도 가장 유용한 해석으로 진행
- 기본 모드: "moderate"
</eagerness_control>
```

### 11. `<empty_result_recovery>` — 빈 결과 복구

```xml
<empty_result_recovery>
- 빈 결과 시 대안 검색어/접근법으로 자동 재시도
- 최대 2회 재시도 후 "결과 없음" 보고
- 최종 출력 전 검증 루프 실행
</empty_result_recovery>
```

### 12. `<missing_context_gating>` — 누락 컨텍스트

```xml
<missing_context_gating>
- 필수 정보 부재 시: 명확화 질문 (선택지 2-3개 포함)
- 선택적 정보 부재 시: 합리적 기본값으로 진행, 가정 명시
- 질문은 1회로 제한 (연쇄 질문 금지)
</missing_context_gating>
```

> **legacy 적용 트리거**: 사용자가 "5.4 스타일", "legacy XML stack", "GPT-5.4용 / GPT-5.2용 프롬프트" 명시 또는 GPT-5.4 / 5.2 / 5 / 4o 이하 모델 지정 시. 그 외 모든 GPT 작업은 위 outcome-first 6섹션 사용.

---

## 예시: 웹 리서치 에이전트 (5.5 outcome-first)

```markdown
Role:
You are an expert research assistant.

# Goal
Provide a verified answer to the user's question with citations for any factual claim.

# Success Criteria
- All factual claims trace to a retrieved source.
- Contradictions across sources are flagged and resolved.
- The user's intent is fully covered without restating their question.

# Constraints
- Do not fabricate sources, dates, or numbers.
- Prefer recent sources when facts may have changed.

# Output
Concise Markdown. Lead with the answer. Then cite sources inline.

# Stop Rules
After the first broad search, retrieve again only when required facts are missing or unsupported.
Stop when success criteria are met.
```

---

## 예시: 코딩 에이전트 (5.5 outcome-first + validation)

```markdown
Role:
You are a senior engineer pairing with the user.

# Goal
Ship a focused change that satisfies the user's request and passes the most relevant validation.

# Success Criteria
- The change compiles, type-checks, and passes targeted tests.
- No drive-by refactors or unrelated edits.
- Edited files and the validation result are reported.

# Constraints
- Preserve existing behavior unless the request changes it.
- Prefer the simplest solution.

# Output
Plain Markdown. Show the diff or list of edited files, then the validation outcome.

# Stop Rules
Run the most relevant validation (test/type/lint/build/smoke).
Stop when success criteria are met.
Ask only for the smallest missing input if blocked.
```

---

---

## 참고 자료

- [Using GPT-6.2 (공식, GPT-6.2 패밀리 가이드)](https://developers.openai.com/api/docs/guides/latest-model) · 모델 카드 [gpt-6.2-astra](https://developers.openai.com/api/docs/models/gpt-6.2-astra) · [gpt-6.2-sol](https://developers.openai.com/api/docs/models/gpt-6.2-sol) · [GPT-6.2 출시 공지 (OpenAI 개발자 포럼)](https://community.openai.com/t/gpt-6-2-astra-and-sol-are-now-available/1417531)
- [Using GPT-6 (공식, GPT-6 패밀리 가이드 — 접근 2026-09-27 판 · 같은 주소가 지금은 «Using GPT-6.2»)](https://developers.openai.com/api/docs/guides/latest-model) · 모델 카드 [gpt-6-sol](https://developers.openai.com/api/docs/models/gpt-6-sol.md) · [gpt-6-luna](https://developers.openai.com/api/docs/models/gpt-6-luna.md) · [GPT-6 Sol·Luna 출시 공지](https://openai.com/index/introducing-gpt-6-sol-and-luna/)
- [GPT-5.6 Sol Prompt Guidance (공식)](https://developers.openai.com/api/docs/guides/prompt-guidance-gpt-5p6)
- [GPT-5.5 Prompt Guidance (공식)](https://developers.openai.com/api/docs/guides/prompt-guidance?model=gpt-5.5)
- `skills/prompt-engineering-guide/references/full.md` — 모델별 통합 전략
- vault MOC: `020-Library/Research/Prompt-Guidance/05-GPT-5.6-Sol-Prompting/` (GPT-5.6 가이드 2티어)

---

## Metadata

- **Version**: 1.5.0
- **Created**: 2026-07-11
- **Updated**: 2026-11-18
- **Source**: OpenAI Using GPT-6.2 · GPT-6.2 출시 공지 (접근 2026-11-18) + OpenAI GPT-5.6 Sol Prompt Guidance (2026-07) + OpenAI Using GPT-6 Astra (2026-09) + OpenAI Using GPT-6 · gpt-6-sol / gpt-6-luna 모델 카드 · GPT-6 Sol·Luna 출시 공지 (접근 2026-09-27) + preserved GPT-5.5/5.4/5.2 legacy patterns
- **Author**: tofukyung (prompt-engineering-skills maintainers)
- **Changes v1.5.0** (2026-11-18):
  - [NEW] GPT-6.2 Astra · Sol 절 신설 — 공식 출처와 한계(두 모델을 한 페이지에서 다룸 · GPT-6.2 Sol 전용 가이드 확인 범위 내 미발견 · GPT-6 Luna 의 6.2 판 없음), 트리거(맨 "Sol"·"Astra" 단독 ❌), 모델 선택 표(가이드·출시 공지 원문), 행동 성향 4가지, reasoning items 를 버리는 조건, 처방 블록 원문(Writing style 3 · Task completion 3 · Coding style (a)~(d) · Frontend design 1)과 7블록 위치, 독자에 따라 ① 사용자 용어 따르기 / ② 바깥 독자 맞춤 고르기, 옮길 때 바꿀 값 표, 직전 판에서 바뀐 것, 마이그레이션 체크.
  - [MAJOR] GPT 디폴트 = GPT-6.2 Sol (2026-11-17~). GPT-6 Sol = 직전 디폴트 · GPT-5.6 Sol = 그 전 디폴트 — 머리·트리거·모델 미지정·LEGACY 안내 문장 갱신. GPT-6 Astra · Sol · Luna · GPT-5.6 Sol 절은 그대로(사용자가 지정하면 그 절).
  - [NOTE] GPT-6 처방 중 6.2 에서 바뀐 것에 «GPT-6 판 한정» 표지 — 상투어 금지 목록 · 성격·문체(산문 쪽으로 누르기) · 문단 위주 문체 · 테스트 조절 · 현 effort 보존 · "간결하게" 재측 안내. 같은 주소의 10-28 웹 보관본에 실린 GPT-6.1 Sol · Terra 는 이 파일이 다루지 않는다고 적음.
- **Changes v1.4.0** (2026-09-27):
  - [NEW] GPT-6 Sol · Luna 절 신설 — 공식 출처와 한계(전용 프롬프트 가이드 확인 범위 내 미발견 → 패밀리 가이드 «Using GPT-6» + 모델 카드 2 + 출시 공지), 트리거(맨 "Sol" 단독 ❌), 모델 선택 표(Astra / GPT-6 Sol / GPT-6 Luna 원문), 매개변수(`none`~`max` 기본 `medium` · GPT-6 Sol·Luna `none` 지원 · Chat Completions 함수 호출은 `none` 일 때만 · 샘플링 매개변수 제거 · `configuration_update` · `text.verbosity`), 프롬프트 작성(7블록 출발점 + Astra 관찰 기반 예시 원문 6개), 출시 공지 기준 문체, GPT-5.6 Sol → GPT-6 Sol/Luna 마이그레이션 체크.
  - [MAJOR] GPT 디폴트 = GPT-6 Sol (2026-09-22~). GPT-5.6 Sol = 직전 디폴트 — 트리거·모델 미지정·LEGACY 안내 문장 갱신. GPT-5.6 트리거의 맨 "Sol" → "GPT-5.6 Sol".
  - [NOTE] Astra 절의 모델 미지정 조건(「Astra 로 전환된 이후」 `[미검증]`)을 GPT-6 Sol 디폴트로 대체.
- **Changes v1.3.0** (2026-09-06):
  - [NEW] GPT-6 Astra 절 신설 — 모델 스펙(`none` 미지원·272K 장문 할증)·마이그레이션 3건·행동 성향 5가지 공식 교정 프롬프트·새 기능 3+1(비동기 도구·mid-turn steering·configuration_update).
  - [NOTE] Fable 5.1(Claude 계열)과 포맷팅 축 정반대 — 교차 이식 금지 표기.
- **Changes v1.2.0** (2026-07-11):
  - [MAJOR] GPT-5.6 Sol을 기본(default) 모델로 승격. lean 우선 철학 + 7블록 구조 도입.
  - [NEW] `tools_and_ptc`(프로그래매틱 도구 호출 경계) + `authorization_boundaries`(자율성 승인 3단) 블록.
  - [NEW] reasoning effort `xhigh/max` 반영, effort 상향 전 프롬프트 강화 원칙.
  - [NEW] anti-pattern "간결하게 광범위 지시"(5.6 기본 간결 반영).
  - [KEEP] GPT-5.5 outcome-first 6섹션 + GPT-5.4/5.2 XML 12블록 = 하단 LEGACY 보존(명시 요청 시 fallback).
  - 기존 `gpt-5.5-prompt-enhancement.md` = 3줄 포인터 stub으로 교체.
