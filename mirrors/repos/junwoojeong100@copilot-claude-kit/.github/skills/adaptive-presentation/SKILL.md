---
name: adaptive-presentation
description: "주제·청중·목적에 맞춘 편집 가능한 PowerPoint(.pptx)를 결론과 다음 행동이 먼저 보이도록 만듭니다. 필요한 조사 → 스토리라인 → python-pptx 제작 → 렌더 검증 순으로 실행하며 고정 템플릿 없이 내용에 맞게 구성합니다. WHEN: PPT 만들어줘, PPTX 생성, 발표자료, 슬라이드 덱, 임원 보고자료, 제안서, 영업 자료, 제품 소개서, 기술 아키텍처 발표, 교육·세미나·컨퍼런스 자료. NOT WHEN: 기존 문서의 텍스트 요약만 필요하거나 PowerPoint 파일이 아닌 웹 앱·단일 HTML 데모를 요청한 경우."
argument-hint: "주제, 청중, 목적, 슬라이드 수를 알려주세요 — 예: '병원 경영진 대상 의료 AI 전략, 의사결정용 20장'"
---

# Adaptive Presentation

사용자가 바로 발표하고 편집할 수 있으며 첫 본문부터 **결론·의미·다음 행동**이 보이는 PowerPoint를 만든다.

## 산출물

- 기본 산출물: 요청한 장수의 편집 가능한 `.pptx` 1개. 템플릿이 없으면 16:9, 있으면 원본 canvas를 보존한다.
- 사용자가 요청한 경우에만 PDF 또는 생성 스크립트를 추가한다.
- 최종 출력 위치에는 요청한 파일만 남긴다. 조사 메모·생성 스크립트·PDF·QA 이미지는 저장소와 최종
  출력 폴더 밖의 세션 작업 디렉터리에 두고 완료 시 정리한다.
- `<session>`은 client가 제공한 artifact 디렉터리다. 없으면 저장소·최종 출력 폴더 밖의 고유 OS
  temporary directory를 사용하고 최종 파일을 복사한 뒤 삭제한다.

## 입력

| 입력 | 처리 |
|---|---|
| `TOPIC` | 반드시 확인하거나 문맥에서 명확히 추론 |
| `AUDIENCE` | 직급·직무·사전지식에 맞춰 내용과 표현 조정 |
| `PURPOSE` | 설명·의사결정·설득·교육·영업·보고 중 결정 |
| `SLIDE_COUNT` | 지정하면 정확히 준수, 없으면 목적에 맞게 결정 |
| `LANG` | 사용자 언어 사용. 한국어 덱은 설명 문장을 한글 우선으로 쓰되 서비스명·공식 기능명·정착된 기술 용어는 영문 유지 |
| `TEMPLATE/BRAND` | 제공되면 profile을 추출하고 master·layout·font·color·canvas를 보존 |
| `OUTPUT` | 사용자 지정 파일명·경로·형식 준수 |

결과를 크게 바꾸는 blocking 정보만 질문한다. 안전한 기본값이 있으면 가정을 표시하고 진행한다.

## 필수 워크플로

### 1. 조사와 Fact Ledger

- 외부 사실·최신 정보·가격·규제·제품 상태·고객 성과를 사용하는 경우 `web-search` 스킬을 호출한다.
  검색 backend와 원문 검증 방법은 `web-search`가 결정하며 이 스킬에서 별도 정책을 정의하지 않는다.
- 사용자 제공 자료만 재구성하거나 외부 사실이 없는 창작형 덱은 불필요한 웹 조사를 강제하지 않는다.
- 복합 조사 결과는 `web-search`의 공통 Fact Ledger 계약으로 `fact-ledger.md`에 병합하고, deck spec
  handoff용 `fact-ledger.json`도 공통 schema에 맞춰 만든다.
  슬라이드 매핑은 Ledger를 확장하지 않고 storyline과 deck spec에 기록한다.
- 상충, Preview, 가정, 추정, 시연 데이터는 명시적으로 표시한다.
- 필요한 조사 축만 선택하고 `web-search` 완료 기준을 충족하면 탐색을 종료한다.

### 2. 스토리라인

코드 전에 [`reference/deck-spec.md`](./reference/deck-spec.md)의 `deck-spec.json`과 `storyline.md`에
요청 장수를 배분하고 슬라이드별로 다음을 확정한다.

- 청중이 받아들일 결론형 제목
- 기억해야 할 한 문장과 다음 판단·행동
- 사용할 Fact Ledger 근거와 출처
- 정보 관계에 맞는 시각 형태
- 이전·다음 슬라이드와의 논리적 연결
- 발표자가 말할 핵심 메시지·전체 흐름·구성 요소·실제 예시·검증 기준·상태/조건·발표 한 문장·출처

제목만 연속해서 읽어도 논리가 완성되어야 한다. 결론이나 판단을 바꾸지 않는 장은 제거·통합하고,
고정 장수를 채워야 하면 반복 문구 대신 근거·사례·비교·실행 기준을 추가한다.
코드 작성 후에는 새 근거나 시각적 blocker가 있을 때만 storyline과 deck spec을 함께 갱신한다.
목적별 서사 패턴은 [`reference/narrative-patterns.md`](./reference/narrative-patterns.md)를 참고한다.

### 한국어·영문 균형 계약

- 한국어 덱의 기본 목표는 **설명용 영문 문자 약 40%**다. `protectedTerms`의 공식명은 계산에서
  중립 처리하며, 원시 영문 비율은 참고값으로만 기록한다.
- 고객 결과·설명·판단·행동·KPI 의미는 자연스러운 한국어를 우선한다.
- **서비스명, 제품명, 공식 기능명, 명령·API·SDK·프로토콜·표준 약어는 번역하지 않는다.**
  예: `GitHub Copilot`, `Microsoft Foundry`, `Hosted Agents`, `Code Review`, `Browser Tools`,
  `Managed Settings`, `Session Streaming`, `Control Plane`, `AKS`, `ACA`, `MCP`.
- `deck-spec.json`의 `languagePolicy.protectedTerms`에는 해당 덱에서 반드시 영문으로 유지할 공식 용어를
  기록한다. Verifier는 이 용어가 최종 PPTX에 실제로 존재하는지 확인한다.
- 한국어 문장 안에서 공식 영문명을 억지로 번역하거나, 반대로 설명 전체를 영어 catalog로 쓰지 않는다.
  `Code Review로 결함을 조기에 찾습니다`처럼 역할 설명만 한국어로 연결한다.

### 비기술 청중에게 기술을 설명하는 계약

- 비기술 청중이라고 서비스·기능·architecture component를 제거하거나 모호한 한국어로 바꾸지 않는다.
  기술 이름은 정확한 공식 영문과 capitalization을 유지한다.
- 기본 읽기 순서는 `고객 질문/결론(쉬운 한글) → English 기술명 → 역할 설명(쉬운 한글) →
  고객 가치·판단`이다.
- 한 슬라이드에서 새로 소개하는 핵심 technical term은 원칙적으로 3~5개로 제한하고, 첫 등장 시
  한 줄 역할 설명을 붙인다.
- 권장 예:
  - `Hosted Agents` — 격리된 환경에서 Agent를 실행
  - `Foundry IQ` — 사용자 권한을 반영해 근거를 찾음
  - `Toolboxes` — 허용된 업무 action을 연결
  - `Code Review` — 코드 품질을 검증
  - `Control Plane` — 여러 Agent의 상태·비용·위험을 관리
- 금지 예:
  - 공식명 `Hosted Agents`를 주 라벨에서 `호스팅 실행환경`으로 대체
  - 서비스명만 나열하고 고객에게 무엇이 달라지는지 설명하지 않음
  - 설명 문장까지 `permission-aware knowledge layer`처럼 불필요하게 영어로 작성

### 3. 제작

- [`reference/pptx-production.md`](./reference/pptx-production.md)를 따라 `python-pptx`로 직접 만든다.
- 템플릿이 있으면 `scripts/inspect_template.py`로 profile을 만들고 template-aware initializer로
  master·layout·theme·canvas를 보존한다. 없으면 고정 템플릿을 강제하지 않는다.
- `scripts/toolcheck.py`가 선택한 언어·환경별 설치 폰트를 `deck-spec.json`에 기록하고 제작에 사용한다.
- 한국어 덱은 `languagePolicy` 기본값(`targetLatinRatio=0.40`, `maxLatinRatio=0.55`,
  `maxSlideLatinRatio=0.75`)을 사용하고 관련 `protectedTerms`를 채운다.
- `protectedTerms`에는 서비스명·공식 기능명뿐 아니라 해당 덱의 주요 architecture component와
  안정적으로 통용되는 technical term을 포함한다. 해당 용어가 있는 장에는 쉬운 한글 역할 설명을 둔다.
- 한국어 덱은 모든 슬라이드에 speaker notes를 작성한다. 기존 notes가 있더라도 먼저 완전히 지우고
  storyline·현재 slide visual·Fact Ledger만 기준으로 새로 생성한다. 기본 형식은 아래 9개 블록이며
  `speakerNotesPolicy`가 이를 검증한다.
  - `핵심 메시지:` “이 슬라이드의 핵심은 …입니다”로 시작하는 결론
  - `전체 흐름:` 화면을 읽는 순서와 요소 간 관계를 3~5문장으로 설명
  - `구성 요소:` 핵심 English 기술명·단계·카드를 항목별로 쉬운 한국어로 해설
  - `실제 예시:` 고객 업무 한 가지를 골라 입력→처리→결과 순서로 설명
  - `검증 기준:` KPI·확인 evidence·의사결정 기준
  - `상태/조건:` GA/Preview/가정, API·portal·source·tool별 적용 범위와 예외
  - `질문/전환:` 고객 질문, 다음 장 연결 또는 다음 행동
  - `발표 한 문장:` 발표자가 그대로 말할 수 있는 짧은 결론
  - `출처:` Fact ID·발행자·문서명·확인일
- 노트는 슬라이드 문구를 낭독하는 원고가 아니라 발표자가 필요한 설명을 선택할 수 있는
  **상세 설명형 reference**로 작성한다. 한국어 기본 목표는 약 3분, 1,000~2,600자다. `전체 흐름`은
  220자·3문장 이상, `실제 예시` 100자 이상, `검증 기준` 70자 이상, `상태/조건` 120자 이상으로
  작성한다. 서비스 전체와 개별 API·portal·source·tool의 상태가 다르면 한 덩어리로 `GA`라고 쓰지
  말고 범위를 분리한다. 외부 제품 상태가 없는 장은 `내부 프레임`, `ASSUMPTION`, `Recommendation`
  중 성격과 고객별 검증 조건을 적는다.
- 한 슬라이드는 질문 하나, 결론 하나, 핵심 근거 2~4개를 기본으로 한다.
- 첫 본문 슬라이드에서 핵심 결론·가치·다음 행동을 보여준다.
- 제목+불릿만 반복하지 않고 숫자·표·차트·흐름·비교·계층·타임라인 중 적합한 native visual을 사용한다.
- 핵심 도형·차트·텍스트는 편집 가능한 PowerPoint 객체로 만든다.
- 같은 역할의 본문 제목 크기와 색상 의미를 덱 전체에서 일관되게 유지한다.
- 작은 글씨로 과밀 문제를 숨기지 않는다. 주요 본문은 원칙적으로 15pt 이상을 유지한다.
- 차트는 실제 데이터와 축·단위·기준일을 사용한다. 외부 사실이 있는 슬라이드에는 footer 출처를 표시한다.
- 권한이 불분명한 로고·인물·브랜드 자산을 임의 생성하지 않는다.

관계형 레이아웃 아이디어는 [`reference/slide-blueprints.md`](./reference/slide-blueprints.md)를 선택적으로
참고하고, 임원 편집 스타일은
[`reference/editorial-business-style.md`](./reference/editorial-business-style.md)를 따른다.

### 4. 렌더 검증과 수정

[`scripts/verify_deck.py`](./scripts/verify_deck.py)와
[`reference/verification.md`](./reference/verification.md)를 사용한다.

```bash
python3 -B .github/skills/adaptive-presentation/scripts/verify_deck.py <deck>.pptx --out <work> \
  --deck-spec <work>/deck-spec.json
```
외부 사실 슬라이드와 `[Fact ID]` 출처는 deck spec에서 자동 도출한다.

1. 동일한 최초 PPTX에 대해 구조 감사와 전체 렌더를 실행한다.
2. compact contact sheet를 확인하고 위험 슬라이드만 상세 확인한다.
3. 자동 검증이 지원하지 않는 chart·SmartArt와 unmapped text도 finding ID로 기록한다.
4. 결함을 일괄 수정한다. 의도적 예외는 finding ID·검토 이유를 exception manifest에 기록한다.
5. contact sheet와 위험 슬라이드를 확인한 뒤 현재 PPTX SHA-256에 묶인 `visual-review.json`을 만들고
   verifier를 다시 실행한다.

시각 검증 없이 완료했다고 주장하지 않는다. 실행 최적화와 캐시는
[`reference/full-optimized.md`](./reference/full-optimized.md)를 따르되 품질 단계를 생략하지 않는다.

## 완료 조건

- 요청한 형식·장수·언어·템플릿 조건을 지켰다.
- 첫 본문에서 결론·가치·다음 행동이 보이고 제목만 읽어도 서사가 이어진다.
- 내용 전달이 목적인 본문 슬라이드에는 관계를 설명하는 시각 구조가 있다. 표지·section divider·단순
  마무리 장은 장식적 visual을 억지로 추가하지 않는다.
- 자동 검증 범위의 geometry·rendered text 결함이 0이며, 미지원 객체는 finding 단위 검토 근거가 있다.
- 텍스트가 경계와 컨테이너 안에 있고 발표 거리에서 읽힌다.
- 외부 사실을 사용하는 슬라이드에 출처가 있고 Preview·가정·시연 데이터가 표시된다.
- 한국어 덱은 설명 문구가 한글 우선이고, `protectedTerms`의 서비스·공식 기능명이 영문으로 유지되며,
  language balance QA를 통과한다.
- 모든 슬라이드 notes가 `핵심 메시지/전체 흐름/구성 요소/실제 예시/검증 기준/상태/조건/
  질문·전환/발표 한 문장/출처`를 포함하고 notes QA를 통과한다.
- 최종 PPTX revision과 일치하는 전체 시각 검토 증거가 있다.
- PPTX가 정상적으로 열리고 압축 구조 오류가 없다.
- 저장소와 최종 출력 폴더에 임시 `.py`, `.pyc`, `__pycache__`, PDF, QA 이미지가 남지 않는다.
## 참고

- 제작·서사·시각: [`pptx-production`](./reference/pptx-production.md) ·
  [`narrative-patterns`](./reference/narrative-patterns.md) · [`slide-blueprints`](./reference/slide-blueprints.md)
- 계약·검증·최적화: [`deck-spec`](./reference/deck-spec.md) ·
  [`verification`](./reference/verification.md) · [`full-optimized`](./reference/full-optimized.md)
