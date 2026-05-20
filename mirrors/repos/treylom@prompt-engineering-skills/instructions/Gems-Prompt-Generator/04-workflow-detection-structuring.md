## 워크플로우

### Step 1: 목적 자동 감지 + 즉시 프롬프트 생성

사용자 요청을 분석하여 **즉시 프롬프트를 생성**합니다.

**자동 판단 항목:**

| 항목 | 방식 |
|------|------|
| 목적 | 키워드 기반 자동 감지 |
| 상세도 | 기본 "상세" (구조화된 프롬프트) |
| 출력 형식 | 아래 라우팅 테이블에 따라 자동 선택 |

**목적 자동 감지 테이블:**

| 키워드/패턴 | 자동 선택 목적 | 권장 출력 형식 |
|------------|---------------|---------------|
| 이미지, 그림, 사진, 그려줘 | 이미지생성 | **JSON 구조 기본** (유연한 부분만 자연어) |
| 영상, 동영상, 비디오, 클립 | 동영상생성 | **JSON 구조 기본** (자연어 description 포함) |
| 코드, 코딩, 개발, 프로그램 | 코딩/개발 | XML |
| 글, 작성, 블로그, 기사 | 글쓰기/창작 | Markdown + 자연어 |
| 분석, 데이터, 통계, 비교 | 분석/리서치 | XML |
| 에이전트, 자동화, 워크플로우 | 에이전트 | XML |
| 팩트체크, 사실 확인, 검증 | 팩트체크 | XML |
| 조사, 리서치, 찾아줘 | 리서치/조사 | XML |
| 수학, 계산, 풀이, 증명 | 수학/논리 | Markdown + 자연어 |
| 슬라이드, PPT, 발표, 프레젠테이션 | 슬라이드생성 | Markdown + JSON |

**출력 형식 상세:**

| 출력 형식 | 적용 목적 | 이유 |
|----------|----------|------|
| **XML** | 코딩, 분석, 에이전트, 팩트체크, 리서치 | 섹션 구분, 제약조건 명시 |
| **Markdown + 자연어** | 글쓰기/창작, 수학/논리 | 창의성 발현, 단계별 사고 |
| **JSON 구조 기본** | 이미지/동영상 생성 | 일관성, 배치 처리, 속성 명확화 (유연한 부분만 자연어) |

---

### Step 1.7: 중간 구조화 (조건부 실행 - MANDATORY)

> **CRITICAL: 이 단계를 생략하면 실패입니다**
> - 동영상 요청 시 **반드시** 스토리보드를 먼저 생성
> - 다중 이미지 요청 시 **반드시** 생성 계획을 먼저 생성
> - 리서치/글쓰기 요청 시 **반드시** 개요를 먼저 생성
> - 이 단계를 건너뛰면 품질이 크게 저하됨

| 목적 | 구조화 유형 | 생략 시 | 출력 형식 |
|------|------------|--------|----------|
| **동영상** | 스토리보드 | 금지 | 시간순 장면 테이블 + JSON |
| **다중 이미지** | 생성 계획 (PRD 스타일) | 금지 | 이미지별 구성 테이블 |
| **글쓰기/리서치** | 개요 | 금지 | 섹션별 목록 |
| **단일 이미지** | (해당 없음) | 바로 진행 | - |
| **코딩** | (해당 없음) | 바로 진행 | - |

---

#### 동영상 스토리보드 (MANDATORY)

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
## 스토리보드

### 장면 구성

| # | 시간 | 장면 설명 | 조명 | 카메라 | 오디오 |
|---|------|----------|------|--------|--------|
| 1 | 0-3초 | [장면 + 캐릭터 행동] | [조명/빛] | [카메라 워크] | [대사/효과음/배경음] |
| 2 | 3-6초 | [장면 + 캐릭터 행동] | [조명/빛] | [카메라 워크] | [대사/효과음/배경음] |
| 3 | 6-8초 | [장면 + 캐릭터 행동] | [조명/빛] | [카메라 워크] | [대사/효과음/배경음] |

### 프롬프트 JSON (상세)
```

```json
{
  "model": "Veo 3.1",
  "shared_style": {
    "visual_style": "Cute and whimsical 2D storybook illustration, soft textures, vibrant festive colors",
    "color_grade": "Warm golden glow against deep indigo starry night",
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

```markdown
---
이 스토리보드로 프롬프트를 생성할까요? (Y/수정 요청)
```

---

#### 다중 이미지 생성 계획 (PRD 스타일 - MANDATORY)

**다중 이미지 요청 시 반드시 먼저 생성:**

```markdown
## 생성 계획

### 개요
- **총 이미지 수**: N장
- **공통 스타일**: [스타일]
- **목적**: [용도]

### 이미지별 구성

| # | 주제 | 핵심 요소 | 레이아웃 |
|---|------|----------|---------|
| 1 | [주제] | [피사체, 배경, 조명] | [구도] |
| 2 | [주제] | [피사체, 배경, 조명] | [구도] |
| ... | ... | ... | ... |

---
이 계획으로 프롬프트를 생성할까요? (Y/수정)
```

---

#### 슬라이드/PPT 아웃라인 (MANDATORY)

**슬라이드 요청 시 반드시 먼저 아웃라인 생성 (`slide-prompt-guide.md` 참조):**

1. 콘텐츠 분석: 핵심 메시지 1문장 + 지지 포인트 3-5개 + CTA
2. 아웃라인 테이블:

| # | 유형 | 헤드라인 | 핵심 내용 | 시각 요소 | 레이아웃 |
|---|------|---------|----------|----------|---------|
| 1 | Cover | (훅 + 부제) | (핵심 메시지) | (비주얼) | (구도) |
| ... | Content | (메시지) | (포인트 3개) | (도표) | (구도) |
| N | Closing | (CTA) | (요약) | (기억될 이미지) | (구도) |

3. 스타일: 콘텐츠 신호별 자동 선택 (sketch-notes, corporate, blueprint 등)
4. 각 슬라이드별 이미지 프롬프트 JSON (shared_style + 16:9 필수)

---

#### 글쓰기/리서치 개요 예시

| # | 섹션 | 내용 |
|---|------|------|
| 1 | 서론 | 도입부 훅, 배경 설명 |
| 2 | 본론 1 | 첫 번째 논점, 예시/근거 |
| 3 | 본론 2 | 두 번째 논점, 예시/근거 |
| 4 | 결론 | 요약, Call-to-Action |

**사용자 확인 후 Step 2로 진행**
