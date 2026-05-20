# 프레임워크 레퍼런스

Context Engineering 원칙, 목적별 블록, 워크플로우 상세, 품질 체크리스트 전체.

---

## Context Engineering 원칙 상세

`context-engineering-collection` 스킬의 핵심 원칙을 프롬프트 생성에 적용합니다.

### 1. Progressive Disclosure
- 프롬프트를 섹션별로 구조화
- 필수 정보만 포함, 부가 정보는 요청 시 제공
- 시스템 프롬프트 → 지시사항 → 예시 순서

### 2. Attention Budget 관리
- 중요 지시사항은 **시작 또는 끝**에 배치
- 중간 부분에는 맥락/배경 정보 배치
- "Lost in the middle" 현상 방지

### 3. Signal-to-Noise Ratio 최적화
- 불필요한 서술 제거
- 핵심 지시사항만 포함
- 모호한 표현 대신 구체적 지시

### 4. Context Quality > Quantity
- 최소 토큰으로 최대 효과
- 반복 제거, 핵심만 유지
- 명확한 구조로 파싱 용이성 확보

---

## Context Engineering 심층 통합

각 모델에 적용해야 할 Context Engineering 원칙을 정리합니다.

### Attention Budget 관리

중요 정보는 프롬프트 **시작 또는 끝**에 배치 (U자형 주의력 곡선):

```
[CRITICAL INSTRUCTIONS]     ← 시작에 배치 (높은 주의력)
[Background/Context]        ← 중간에 배치 (낮은 주의력)
[Detailed Examples]         ← 중간에 배치
[KEY CONSTRAINTS]           ← 끝에 배치 (높은 주의력)
```

### 컨텍스트 저하 방지

| 현상 | 설명 | 대응책 |
|------|------|--------|
| **Lost-in-Middle** | 중간 배치 정보 10-40% 낮은 회수율 | 중요 정보를 시작/끝에 배치 |
| **Context Poisoning** | 오류가 컨텍스트에 누적 | 도구 출력 검증, 명시적 정정 |
| **Context Distraction** | 무관한 정보가 주의력 빼앗음 | 관련성 필터링, 불필요한 정보 제외 |

### 모델별 저하 임계값

| 모델 | 저하 시작 | 심각한 저하 | 대응 |
|------|----------|-------------|------|
| **GPT-5.2** | ~64K 토큰 | ~200K 토큰 | Compaction 엔드포인트 활용 |
| **Claude 4.5 Opus** | ~100K 토큰 | ~180K 토큰 | Memory Tool/Context Editing 활용 |
| **Claude 4.5 Sonnet** | ~80K 토큰 | ~150K 토큰 | Sub-agent 분할 고려 |
| **Gemini 3 Pro** | ~500K 토큰 | ~800K 토큰 | 1M 컨텍스트지만 주의 필요 |

### 도구 설계 원칙

프롬프트에서 도구를 정의할 때:

1. **통합 원칙**: 여러 좁은 도구보다 포괄적인 단일 도구 선호
2. **명확한 설명**: what (무엇), when (언제), what returns (반환값) 명시
3. **MCP 네이밍**: 항상 `ServerName:tool_name` 형식 사용
4. **복구 가능한 에러**: 에러 메시지에 복구 방법 포함

### Context Engineering 적용 템플릿

각 모델 섹션에 다음 패턴을 적용:

```markdown
#### Context Engineering 적용

**Attention Budget**
- 중요 지시사항은 프롬프트 시작 또는 끝에 배치
- 배경 정보/예시는 중간에 배치

**Degradation Prevention**
- 컨텍스트 {임계값}K 토큰 초과 시 압축 고려
- 도구 출력이 누적되면 Observation Masking 적용

**Tool Design**
- 도구 설명에 what, when, what returns 포함
- 에러 메시지에 복구 방법 포함
```

---

## 목적별 추가 블록

### 코딩/개발
```xml
<coding_standards>
  - Follow existing project patterns
  - Include type annotations where applicable
  - Write testable, modular code
  - Handle errors appropriately
</coding_standards>
```

### 글쓰기/창작
```xml
<writing_style>
  - Tone: {formal/casual/technical/conversational}
  - Voice: {active/passive}
  - Target audience: {audience description}
  - Length: {word count or paragraph count}
</writing_style>
```

### 분석/리서치
```xml
<analysis_requirements>
  - Cite sources when available
  - Distinguish facts from interpretations
  - Acknowledge limitations and uncertainties
  - Provide actionable insights
</analysis_requirements>
```

### 에이전트/자동화
```xml
<agent_behavior>
  - Take action by default
  - Ask only when genuinely blocked
  - Complete tasks fully before stopping
  - Use tools efficiently
</agent_behavior>
```

### 데이터 처리
```xml
<extraction_spec>
  - Input format: {format}
  - Output format: {format}
  - Fields to extract: {field list}
  - Validation rules: {rules}
</extraction_spec>
```

---

## 상세도별 출력 지침

### I. 간결 (3-5문장)
```xml
<verbosity level="minimal">
  - 3-5 sentences maximum
  - Bullet points preferred
  - No elaboration
</verbosity>
```

### II. 보통 (1-2 문단)
```xml
<verbosity level="moderate">
  - 1-2 paragraphs
  - Key points with brief explanation
  - Examples only if essential
</verbosity>
```

### III. 상세 (구조화된 긴 응답)
```xml
<verbosity level="detailed">
  - Structured with headers
  - Comprehensive coverage
  - Examples and explanations included
</verbosity>
```

### IV. 가변 (상황에 따라)
```xml
<verbosity level="adaptive">
  - Scale response to task complexity
  - Simple tasks: brief
  - Complex tasks: detailed
</verbosity>
```

---

## 품질 체크리스트 (전체)

### 공통 체크리스트
- [ ] 역할/페르소나가 명확히 정의됨
- [ ] 핵심 지시사항이 포함됨
- [ ] 출력 형식이 명시됨
- [ ] 불필요한 서술이 제거됨
- [ ] 중요 정보가 시작/끝에 배치됨

### 모델별 체크리스트

**GPT-5.2**:
- [ ] `<output_verbosity_spec>` 포함됨
- [ ] 목적에 맞는 XML 블록 추가됨
- [ ] reasoning_effort 고려됨

**GPT-5.2-Codex**:
- [ ] "Less is more" 원칙 적용됨
- [ ] 서문/맺음말 금지 명시됨
- [ ] 코드 스타일 가이드 포함됨

**Claude 4.5**:
- [ ] 모든 지시가 명시적임
- [ ] 암묵적 기대 없음
- [ ] 액션 기본값 설정됨

**Gemini 3**:
- [ ] 제약 조건이 먼저 배치됨
- [ ] 구조화된 출력 형식 사용됨

**Veo**:
- [ ] 주제/동작/스타일 필수 요소 포함됨
- [ ] 카메라 위치/구도/분위기 선택 요소 고려됨
- [ ] 오디오 프롬프트 적절히 사용됨 (Veo 3+)
- [ ] 부정적 프롬프트는 단순 나열로 작성됨

**Nano Banana (NB Pro / NB2)**:
- [ ] 주제가 명확히 기술됨
- [ ] 스타일/분위기/구도 포함됨
- [ ] NB2: 서술형 프롬프트 사용 (5요소 프레임워크)
- [ ] Veo 연동 시 이미지 형식 확인됨

---

## Step 7: 전문가 3인 퇴고 (상세)

**트리거**: "퇴고해줘", "전문가 검토", "상세 퇴고" 요청 시 적용

### 7.1 전문가 페르소나

| 역할 | 전문 분야 | 검토 초점 |
|------|----------|----------|
| **프롬프트 아키텍트** | Context Engineering, 토큰 최적화 | 구조, 효율성, 모델 특성 적합성 |
| **도메인 전문가** | 작업 유형별 전문 지식 | 내용 정확성, 완전성, 누락 요소 |
| **사용자 경험 디자이너** | UX Writing, 명확성 | 이해도, 모호성 제거, 실행 가능성 |

### 7.2 퇴고 프로세스

```
1. 초안 생성 (Step 1-6 완료)
   ↓
2. 프롬프트 아키텍트 검토
   - CE 원칙 적용 여부
   - 모델별 필수 블록 확인
   - 토큰 효율성 검토
   ↓
3. 도메인 전문가 검토
   - 내용 정확성
   - 누락된 요소
   - 도메인 특화 개선점
   ↓
4. UX 디자이너 검토
   - 명확성/가독성
   - 모호한 표현 제거
   - 실행 가능성 확인
   ↓
5. 합의 도출 → 최종 프롬프트 출력
```

### 7.3 퇴고 출력 형식

```markdown
## 전문가 퇴고 결과

### 프롬프트 아키텍트 의견
- ✅ [확인된 항목]
- ⚠️ 제안: [개선 사항]

### 도메인 전문가 의견
- ✅ [확인된 항목]
- ⚠️ 제안: [개선 사항]

### UX 디자이너 의견
- ✅ [확인된 항목]
- ⚠️ 제안: [개선 사항]

### 합의된 최종 프롬프트
[최종 프롬프트 코드블록]
```

### 7.4 간략 vs 상세 퇴고

| 모드 | 트리거 | 출력 |
|------|--------|------|
| **간략 퇴고** | "퇴고해줘" | 3인 의견 요약 + 최종 프롬프트 |
| **상세 퇴고** | "상세 퇴고" | 체크리스트별 상세 검토 + 근거 + 최종 프롬프트 |

### Step 후 개선 제안

**Step 1 후:**
- GPT-5.2 선택 시: "reasoning_effort 레벨도 지정하시겠어요?"
- Claude 4.5 선택 시: "Extended Thinking 활성화가 필요한가요?"
- Veo 선택 시: "오디오 포함 여부를 확인해주세요"

**Step 3 후:**
- 코딩: "테스트 코드 포함 여부, 기존 패턴 따르기 등 명시할까요?"
- 분석: "출처 인용 스타일, 불확실성 표현 방식 정할까요?"
- 에이전트: "도구 사용 규칙, 병렬 실행 허용 여부 정할까요?"

**Step 6 후:**
- "출력 길이 제한을 더 명확히 할까요?"
- "예시를 추가하면 품질이 올라갈 수 있어요"
- "제약 조건을 더 구체화할까요?"

---

## 중간 구조화 워크플로우 (Step 1.7)

프롬프트 생성 전, 목적에 따라 **중간 구조화 단계**를 수행하여 품질을 높입니다.

> ⚠️ **CRITICAL: 동영상 생성 시 스토리보드 단계 생략 절대 금지**
> - 동영상 요청 시 **반드시** 스토리보드를 먼저 생성
> - 사용자가 스토리보드 확인 후 프롬프트 생성 진행
> - 이 단계를 건너뛰면 품질이 크게 저하됨

### 적용 조건

| 목적 | 구조화 유형 | 출력 형식 | 다음 단계 |
|------|------------|----------|----------|
| **동영상생성** | 스토리보드 | 시간순 장면 테이블 + JSON | 시간초별 프롬프트 생성 |
| **글쓰기/창작** | 개요 | 섹션별 목록 | 섹션별 프롬프트 생성 |
| **분석/리서치** | 개요 | 섹션별 목록 | 섹션별 프롬프트 생성 |

### 동영상: 스토리보드 생성 (MANDATORY)

**자동 수행 (생략 금지):**
1. 사용자 요청을 분석하여 스토리보드 생성
2. 시간순으로 장면 구성 (오프닝 → 전개 → 클라이막스)
3. 각 장면별: 설명, 캐릭터 행동, 조명/빛, 카메라 워크, 오디오 정의

**스토리보드 필수 요소 체크리스트:**

| 요소 | 설명 | 예시 |
|------|------|------|
| **sequence** | 장면 순서 | 1, 2, 3... |
| **duration** | 장면 길이 | "3s", "2.5s" |
| **description** | 장면 + 캐릭터 행동 + 조명/빛 | "Santa waves with rosy cheeks, golden glow from moon" |
| **camera** | 카메라 위치 + 모션 | "Wide establishing shot, slow pan following sleigh" |
| **audio** | 대사 + 효과음 + 배경음 | "Jingle bells, Santa's laugh: 'Ho ho ho!'" |

**스토리보드 출력 형식 (반드시 준수):**

```markdown
## 📋 스토리보드

### 장면 구성

| # | 시간 | 장면 설명 | 조명 | 카메라 | 오디오 |
|---|------|----------|------|--------|--------|
| 1 | 0-3초 | [장면 + 캐릭터 행동] | [조명/빛] | [카메라 워크] | [대사/효과음/배경음] |
| 2 | 3-6초 | [장면 + 캐릭터 행동] | [조명/빛] | [카메라 워크] | [대사/효과음/배경음] |
| 3 | 6-8초 | [장면 + 캐릭터 행동] | [조명/빛] | [카메라 워크] | [대사/효과음/배경음] |

### 프롬프트 JSON (상세)

---
✅ 이 스토리보드로 프롬프트를 생성할까요? (Y/수정 요청)
```

**스토리보드 기반 동영상 프롬프트 JSON (상세 예시):**

```json
{
  "model": "Veo 3.1",
  "shared_style": {
    "visual_style": "Cute and whimsical 2D storybook illustration, soft textures, vibrant festive colors (red, green, gold)",
    "color_grade": "Warm golden glow from the moon against a deep indigo starry night",
    "aspect_ratio": "16:9"
  },
  "scenes": [
    {
      "sequence": 1,
      "duration": "3s",
      "description": "Santa's sleigh pulled by reindeer enters from the left, flying over a cozy, snow-covered village with glowing windows. Stardust falls from the runners.",
      "camera": "Wide establishing shot, slow pan following the sleigh's path.",
      "audio": "Ambient quiet night, distant wind, and light jingle bells."
    },
    {
      "sequence": 2,
      "duration": "3s",
      "description": "Close-up on Santa Claus, rosy cheeks and a big smile. He waves his hand and tosses a brightly wrapped gift box toward a village chimney.",
      "camera": "Medium close-up on Santa, moving at the same speed as the sleigh.",
      "audio": "Santa's hearty laugh: 'Ho ho ho! Merry Christmas!'"
    },
    {
      "sequence": 3,
      "duration": "2s",
      "description": "The sleigh accelerates toward a large, bright full moon, becoming a silhouette while golden sparkles fill the screen.",
      "camera": "Zoom out showing the entire landscape as the sleigh disappears into the distance.",
      "audio": "Upbeat festive orchestral music reaching a gentle climax, then fading."
    }
  ],
  "negative": "realistic photography, 3D render, dark or scary atmosphere, distorted faces, wall, frame",
  "details": "High-quality digital illustration, clean outlines, cozy and joyful mood, magical glittering effects."
}
```

### 글쓰기/리서치: 개요 생성

**자동 수행:**
1. 사용자 요청을 분석하여 개요(아웃라인) 생성
2. 논리적 구조로 섹션 구성
3. 각 섹션별: 목표, 핵심 포인트 정의

**개요 출력 형식:**

```markdown
## 📋 개요

### 글 구조

1. **서론** - [핵심 메시지]
   - 도입부 훅
   - 배경 설명

2. **본론 1** - [첫 번째 논점]
   - 주요 내용
   - 예시/근거

3. **본론 2** - [두 번째 논점]
   - 주요 내용
   - 예시/근거

4. **결론** - [정리 및 Call-to-Action]
   - 요약
   - 다음 단계 제안

---
✅ 이 개요로 프롬프트를 생성할까요? (Y/수정 요청)
```

### 중간 구조화의 이점

1. **명확한 방향성**: 프롬프트 생성 전 구조 확정
2. **품질 향상**: 단계별 검토로 누락 방지
3. **사용자 참여**: 중간 확인으로 의도 반영
4. **일관성 유지**: 전체 흐름의 논리적 연결

---

## 참고 문서 출처 (Reference Sources)

이 가이드 작성에 참고한 공식 문서 및 자료 목록입니다.

### OpenAI 공식 문서

| 문서 | URL | 주요 내용 |
|------|-----|----------|
| GPT-5.2 Prompting Guide | https://cookbook.openai.com/examples/gpt-5-2_prompting_guide | reasoning_effort, XML 구조, 장황함 제어 |
| GPT-5.4 Prompt Guidance | — | Output Contract, Agentic Patterns, Eagerness Control |
| GPT-5.2-Codex Prompting Guide | https://cookbook.openai.com/examples/gpt-5-codex_prompting_guide | 코딩 에이전트 전용 최적화, Anti-Prompting |
| Introducing GPT-5.2-Codex | https://openai.com/index/introducing-gpt-5-2-codex/ | Codex 모델 소개 및 특성 |

### Anthropic 공식 문서

| 문서 | URL | 주요 내용 |
|------|-----|----------|
| Claude 4.5 What's New | https://platform.claude.com/docs/en/about-claude/models/whats-new-claude-4-5 | Claude 4.5 모델 변경사항, Extended Thinking |
| Claude 4.6 Prompt Guide | — | Adaptive Thinking, Effort Parameter, Prefill 제거, Over-prompting |
| Claude 4 Best Practices | https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-4-best-practices | 명시적 지시, 병렬 도구 호출, 프론트엔드 가이드라인 |

### Google 공식 문서

| 문서 | URL | 주요 내용 |
|------|-----|----------|
| Veo API Documentation | https://ai.google.dev/gemini-api/docs/video?hl=ko | 동영상 생성 API, 확장, 참조 이미지 |
| Image Generation (Nano Banana) | https://ai.google.dev/gemini-api/docs/image-generation?hl=ko | 이미지 생성 API, 프롬프트 구조 |
| NanoBanana2 (NB2) Guide | — | NB2 서술형 프롬프트, 5요소 프레임워크, 14종 비율 |

### 내부 참조 자료

| 자료 | 위치 | 내용 |
|------|------|------|
| Threads 크롤링 결과 | `AI_Second_Brain/Threads/` | @choi.openai 게시물 기반 전략 |
| GPT-5.2 프롬프트 전략 | `AI_Second_Brain/Threads/GPT-5.2-프롬프트-전략.md` | 상세 프롬프트 패턴 |
| Claude 4.5 프롬프트 전략 | `AI_Second_Brain/Threads/Claude-4.5-프롬프트-전략.md` | Claude 전용 최적화 |
