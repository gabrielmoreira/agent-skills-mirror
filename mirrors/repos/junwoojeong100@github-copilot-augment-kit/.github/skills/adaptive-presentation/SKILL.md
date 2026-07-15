---
name: adaptive-presentation
description: "주제·청중·목적에 맞춘 고품질 PowerPoint(.pptx) 발표자료를 조사→스토리라인→Design DNA→생성→렌더 QA 순으로 제작합니다. 고정 템플릿이나 고정 색상 대신 매 요청의 브랜드·정서·정보 밀도·발표 환경에서 디자인 시스템을 새로 도출하며, 생성·검증 파일은 세션 작업 폴더에 격리하고 최종 PPTX만 사용자 출력 위치에 남깁니다. WHEN: PPT 만들어줘, PPTX 생성, 발표자료, 슬라이드 덱, presentation deck, executive presentation, 임원 보고자료, 제안서, 영업 자료, 제품 소개서, 기술 아키텍처 발표, 교육 자료, 세미나 자료, 투자 설명자료, 전략 보고서, 컨퍼런스 발표, 슬라이드 디자인 개선, 기존 PPT 재디자인, 10장/20장/30장 슬라이드."
argument-hint: "주제, 청중, 목적, 슬라이드 수를 알려주세요 — 예: '병원 경영진 대상 의료 AI 전략, 의사결정용 20장'"
---

# Adaptive Presentation Studio

임의의 주제와 청중을 위한 **실제 편집 가능한 PowerPoint**를 만든다. 품질의 기준은 특정 템플릿을
복제하는 것이 아니라, 매 요청에서 적절한 서사와 시각 언어를 새로 설계하고 렌더 결과로 검증하는 것이다.

## 산출물

기본 사용자 산출물은 다음 1개다.

1. `<topic>_<audience>_<count>slides.pptx` — 요청한 장수의 편집 가능한 16:9 PowerPoint

재생성 스크립트와 생성 프롬프트는 내부 작업 자산으로만 유지한다.

```text
<session>/files/<deck>-work/
  fact-ledger.md
  deck-spec.md
  design-dna.md
  build_<deck>.py
  <deck>_generation_prompt.txt     # 필요할 때만
  defects.md
  metrics.json
  qa/
```

이 파일들을 저장소 루트나 사용자의 최종 출력 폴더에 만들거나 복사하지 않는다. 사용자가 소스
스크립트나 프롬프트를 명시적으로 요청한 경우에만 별도 산출물로 제공한다. 검증용 JPEG·contact
sheet와 중간 PDF도 세션 작업 폴더에 두며, 사용자가 PDF를 요청한 경우에만 최종 PDF를 제공한다.

## 입력 해석

| 입력 | 의미 | 없을 때 |
|---|---|---|
| `TOPIC` | 발표 주제와 범위 | 반드시 확인하거나 문맥에서 명확히 추론 |
| `AUDIENCE` | 직급·직무·사전지식 | 목적에서 추론, 구현 방향이 크게 달라지면 한 번 질문 |
| `PURPOSE` | 설명·의사결정·설득·교육·영업·보고 | 사용자 동사와 상황에서 추론 |
| `SLIDE_COUNT` | 정확한 장수 | 사용자가 지정하면 정확히 준수, 미지정 시 목적에 맞춰 결정 |
| `LANG` | 언어와 용어 표기 | 사용자 언어 |
| `BRAND_ASSETS` | 로고·색상·기존 템플릿 | 있으면 검사 후 활용, 없으면 Design DNA에서 도출 |
| `TONE` | 신뢰·혁신·프리미엄·친근함 등 | 청중·목적·산업에서 도출 |
| `OUTPUT` | 최종 파일명·경로·PPTX/PDF | 사용자 출력 위치에는 요청한 최종 파일만 생성 |

이미 충분한 정보가 있으면 질문하지 말고 진행한다. 디자인 취향처럼 결과를 크게 바꾸지만 문맥에서
추론할 수 없는 선택만 `ask_user`로 하나씩 확인한다.

## 절대 원칙

- **고정 디자인 금지**: 기본 팔레트·배경·카드 모양·섹션 표지·차트 색을 재사용하지 않는다.
- **맥락 기반 디자인**: 청중, 목적, 주제의 물성, 브랜드, 발표 환경, 정서 톤에서 시각 시스템을 도출한다.
- **무작위 디자인 금지**: 새롭게 보이기 위해 임의의 색을 뽑지 않는다. 모든 선택에 설명 가능한 이유가 있어야 한다.
- **제목이 서사**: 슬라이드 제목만 연속해서 읽어도 논리가 완성되어야 한다.
- **한 장 한 메시지**: 슬라이드마다 결론 1개, 시각 구조 1개, 보조 근거 2~4개를 기본으로 한다.
- **문서 붙여넣기 금지**: 긴 문단·작은 글씨·표 과밀·카드 6개 반복으로 장수를 채우지 않는다.
- **편집 가능성**: 핵심 도형·다이어그램·차트·텍스트는 가능한 한 PowerPoint 벡터 객체로 만든다.
- **사실과 디자인 분리**: 보기 좋은 허위 수치보다 검증된 적은 정보가 낫다.
- **렌더 QA 필수**: 생성 성공은 완료가 아니다. 모든 슬라이드를 이미지로 보고 수정해야 완료다.

## FULL-OPTIMIZED 기본 실행

`reference/full-optimized.md`를 읽고 모든 단계와 합격 기준은 유지하되 다음 방식으로 실행한다.

- 독립적인 조사만 `/fleet` 또는 병렬 tool call로 수행하고, 메인 에이전트가 Fact Ledger를 합친다.
- Storyline·Design DNA·슬라이드 청사진·생성 스크립트는 한 에이전트가 일관되게 소유한다.
- 검증된 도구 환경은 저장소 밖 공용 캐시에서 재사용하고, 의존성은 실제로 없을 때만 설치한다.
- 최초 전체 렌더의 PDF를 같은 PPTX 리비전의 상세 검사에 재사용한다.
- 결함을 모아 한 번에 수정하고, 수정 후에는 변경 부분을 확인한 다음 전체 QA를 다시 수행한다.
- 단계별 소요시간과 캐시 적중 여부를 세션 작업 폴더의 `metrics.json`에 기록한다.

## 전체 워크플로

### 1단계 — 조사와 Fact Ledger

1. 외부 사실이 있는 발표자료는 매 요청마다 `google-web-search`와 공식 도구로 실시간 조사한다.
   기존 Fact Ledger는 검색 후보로만 사용하며 기능 상태·가격·규제·고객 성과는 항상 다시 확인한다.
2. 서로 독립적인 조사 축은 최대 2~3개로 나눠 같은 단계 안에서 병렬 수행한다.
3. 1차 출처를 우선하고, 숫자·날짜·제품 상태·규제·고객 성과에는 URL과 확인일을 기록한다.
4. 기존 Fact Ledger가 있으면 안정적 사실은 출처를 재확인하고, 변동 정보는 새로 조사한다.
5. 메인 에이전트가 결과를 다음 형식의 단일 Fact Ledger로 합친다.

| Claim | Evidence | Source | Date/status | Slide candidate |
|---|---|---|---|---|

6. 상충하는 사실은 공식 최신 출처를 우선하며, 해결되지 않으면 슬라이드에서 불확실성을 표시한다.
7. Preview·가정·시연 데이터·추정치는 눈에 띄게 라벨링한다.

### 2단계 — 목적에 맞는 서사 선택

`reference/narrative-patterns.md`를 읽고 하나의 기본 패턴과 필요 시 보조 패턴을 선택한다. 패턴은
슬라이드 제목을 채우는 템플릿이 아니라 **의사결정의 흐름**이다.

- 임원 의사결정: 결론 → 변화/위험 → 선택지 → 권고 → 실행
- 제품/플랫폼 소개: 왜 → 무엇 → 작동 방식 → 차별점 → 증거 → 도입
- 고객 제안/영업: 고객 맥락 → 문제 → 미래상 → 제안 → 가치 → 신뢰 → 다음 행동
- 기술 아키텍처: 요구사항 → 구조 → 흐름 → 보안 → 운영 → 전환
- 교육/세미나: 학습 목표 → 개념 모델 → 예제 → 적용 → 확인
- 분석/전략 보고: 발견 → 근거 → 의미 → 시나리오 → 권고

요청 장수를 정확히 배분하고, 각 슬라이드에 다음을 정의한다.

- 결론형 제목
- 청중이 기억해야 할 한 문장
- 가장 적합한 시각 구조
- 근거와 출처
- 이전/다음 슬라이드와의 논리적 연결

이 결과를 세션 작업 폴더의 `deck-spec.md`에 확정한다. 이후 조사 subagent가 서사나 슬라이드 코드를
각자 작성하지 않으며, 변경이 필요하면 먼저 deck spec을 갱신한다.

### 3단계 — Design DNA 생성

슬라이드를 만들기 전에 `reference/design-dna.md`에 따라 이번 덱만의 Design DNA를 만든다.

반드시 결정할 항목:

1. **Concept words 3개** — 예: 정밀함·신뢰·속도
2. **Visual metaphor 1개** — 예: 항해도, 설계도, 편집 매거진, 신호망
3. **Primary archetype + counter-influence** — 한 스타일의 획일화를 피하는 조합
4. **Palette roles** — canvas, surface, ink, muted ink, primary, secondary, accent, semantic status의 HEX
5. **Typography** — 언어·환경에 실제 존재하는 글꼴과 크기 계층
6. **Shape language** — 모서리, 선, 그림자, 여백, 밀도
7. **Image/illustration strategy** — 사진, 아이콘, 추상 도형, 데이터 시각화 중 우선순위
8. **Chart grammar** — 색상·축·라벨·강조 방식
9. **Layout rhythm** — 최소 6개 레이아웃 패밀리와 섹션별 변화
10. **Avoid list** — 이번 덱에서 쓰지 않을 익숙한 패턴 3개

Design DNA는 브랜드 가이드가 있으면 이를 존중하되, 브랜드 색 하나로 모든 면을 채우지 않는다.
기존 덱이 저장소에 있으면 품질 기준은 참고하되 동일 팔레트·배치·카드 스타일을 복제하지 않는다.
결과는 `design-dna.md`에 확정하고 제작 중 임의로 팔레트·타이포·형태 언어를 바꾸지 않는다.

### 4단계 — 슬라이드 청사진

`reference/slide-blueprints.md`에서 내용에 맞는 구조를 고른다. 같은 구조를 반복하지 말고 다음 원칙을 지킨다.

- 20장 이상이면 최소 8개, 10~19장이면 최소 5개의 서로 다른 레이아웃 패밀리 사용
- 같은 레이아웃 패밀리는 의도적 연속 설명이 아니면 2장 넘게 연속 사용 금지
- 카드 그리드는 전체 슬라이드의 35% 이하를 권장
- 숫자는 숫자로 크게, 과정은 흐름으로, 비교는 공통 축으로, 구조는 계층으로 표현
- 표는 정확한 비교가 핵심일 때만 사용하고 6행×5열을 넘기지 않는다
- 장식용 도형 대신 정보 관계를 표현하는 선·공간·크기 차이를 사용

`deck-spec.md`를 잠근 후 표준 슬라이드는 `reference/deck-recipe.md`의 `DeckRecipe`로 구조화한다.
Recipe에는 의미·콘텐츠·source key·blueprint intent만 넣고 HEX·폰트·좌표를 넣지 않는다. 커버,
핵심 thesis, 복잡한 아키텍처, 최신 업데이트 overview, close는 custom builder로 직접 구성한다.

### 5단계 — PPTX 제작

`reference/pptx-production.md`와 `reference/slide-compiler.md`를 읽고 저장소의
`pptx_compiler`를 기본 생성 엔진으로 사용한다.

- 기본 화면비: 16:9, 사용자가 다른 비율을 지정하면 따름
- Python 환경에서는 `python-pptx`를 우선 사용
- 매 덱의 `DesignDNA` 객체는 `design-dna.md`에서 새로 생성하며 Compiler에 기본 팔레트나 테마를 추가하지 않음
- semantic blueprint는 정보 관계에 따라 슬라이드마다 선택하고, 커버·핵심 아키텍처는 visual metaphor에 맞게 custom composition
- 주제별 생성 스크립트는 세션 작업 폴더에 두고 Compiler를 import하여 슬라이드별 콘텐츠와 구성만 작성
- 표준 슬라이드는 `RecipeAssembler`와 certified component로 조립하고, layout selector가 반복률과 density를 고려
- 실제 설치 폰트를 찾을 수 있으면 Pillow font metrics로 수평 overflow를 사전 차단
- Compiler에 없는 primitive가 정말 필요할 때만 세션 생성 스크립트에 추가하고, 범용성이 검증되면 Compiler로 승격
- Python은 `python3 -B` 또는 `PYTHONDONTWRITEBYTECODE=1`로 실행해 `__pycache__`·`.pyc` 생성을 막음
- Python·렌더링 도구·폰트 탐색 결과는 저장소 밖 공용 캐시에서 재사용
- 폰트 설치 여부를 먼저 확인하고 한글/라틴 폴백을 정함
- 권장 크기: 제목 28~40pt, 주요 본문 18~24pt, 보조 14~17pt, 출처 8.5~10pt
- 출처 외 본문은 16pt 미만으로 축소하지 않는다. 안 맞으면 내용을 줄이거나 구조를 바꾼다.
- 대부분의 슬라이드는 주요 본문 35~55단어 이내
- 차트는 실제 데이터에서 생성하고 축·단위·기준일을 표시
- 로고와 이미지는 사용 권한이 분명한 자산만 사용
- 인물 사진·고객 로고·브랜드 마크를 임의 생성하지 않는다
- 코드 슬라이드는 발표에 필요한 핵심 6~12줄만 크게 보여준다

### 6단계 — 렌더링과 수정

`reference/verification.md`의 절차와 `scripts/verify_deck.py`를 사용한다.

1. 구조 감사와 최초 전체 렌더를 같은 immutable PPTX에 대해 병렬 실행
2. 전체 렌더: `soffice` → PDF → PyMuPDF 소형 JPEG, 같은 리비전의 상세 검사용 PDF 유지
3. 30장 단위 compact contact sheet와 `--reuse-pdf` 기반 위험 슬라이드 선택 확인
4. 겹침·잘림·낮은 대비·고아 문장·시선 흐름·레이아웃 반복 결함을 모두 기록
5. 결함을 한 번에 수정하고 변경 슬라이드를 확인
6. 수정이 있었다면 전체 구조 감사와 전체 렌더를 다시 수행
7. 세션 작업 폴더의 임시 PDF·JPEG·QA 파일 정리

렌더링 도구가 없으면 가능한 대체 도구를 사용하고, 시각 검증 없이 완료했다고 주장하지 않는다.

### 첨부 용량 안전 규칙

- PPTX와 PDF를 `view`로 직접 열거나 대화에 첨부하지 않는다. 중간 PDF는 같은 리비전의 QA 동안만 유지하고 완료 시 삭제한다.
- 첫 검수는 기본 렌더 명령으로 생성되는 **5열 compact overview JPEG 1장**만 확인한다.
- overview에서 문제가 의심되는 슬라이드만 `--reuse-pdf ... --slides 8,16 --keep-slide-images`로 확인한다.
- 한 응답에서 full-slide 이미지는 최대 2~3개만 확인하고, 여러 고해상도 이미지를 병렬 `view`하지 않는다.
- 미리보기 한 파일은 기본 900KiB 이하로 유지한다.
- 최종 답변에는 QA 이미지·PDF를 첨부하지 않고 사용자가 요청한 PPTX만 링크한다.

## 합격 기준

- 요청한 장수와 파일 형식이 정확하다.
- 제목만 읽어도 서사가 이어진다.
- 핵심 본문이 발표 거리에서 읽힌다.
- 모든 요소가 슬라이드 경계 안에 있고 텍스트가 카드 밖으로 넘치지 않는다.
- Design DNA가 청중·목적·주제와 연결되며 이전 덱의 외형을 복제하지 않는다.
- 최소 요구 수만큼 레이아웃 패밀리가 사용되고 카드 그리드에 과도하게 의존하지 않는다.
- 숫자·기능 상태·고객 성과에 출처가 있다.
- Preview·가정·시연 데이터가 명확히 표시된다.
- PPTX가 열리고 압축 구조 오류가 없으며 세션 작업 폴더의 재생성 스크립트가 실행된다.
- 저장소와 최종 출력 폴더에는 요청한 PPTX/PDF 외에 `.py`, `.pyc`, `__pycache__`, QA 이미지가 남지 않는다.

## 흔한 실패와 교정

| 실패 | 교정 |
|---|---|
| 모든 요청에 파란색 SaaS 카드 디자인 | Design DNA를 다시 만들고 시각 은유·팔레트·형태 언어를 주제에서 도출 |
| 30장을 같은 3열 카드로 채움 | 정보 유형별 청사진으로 재배치하고 레이아웃 반복률을 낮춤 |
| 글자가 작아짐 | 내용을 줄이고 슬라이드를 재구성. 폰트 축소로 해결하지 않음 |
| 제목이 명사형 주제 | 청중이 받아들일 결론형 문장으로 변경 |
| 출처가 마지막 장에만 있음 | 해당 주장 슬라이드의 footer에 직접 표시 |
| 생성 후 파일만 열어봄 | compact JPEG overview와 선택 슬라이드를 실제로 확인 |
| 브랜드 색을 모든 배경에 사용 | 브랜드 색은 강조 역할로 제한하고 중립 canvas와 대비 체계 구축 |
| 디자인을 새롭게 하려고 무작위 색 사용 | concept words와 정서적 의도에 근거한 팔레트로 재선정 |

## 참고 파일

- `reference/design-dna.md` — 요청마다 다른 디자인 시스템을 도출하는 방법
- `reference/narrative-patterns.md` — 목적·청중별 서사 패턴과 장수 배분
- `reference/slide-blueprints.md` — 정보 유형별 편집 가능한 슬라이드 구조
- `reference/pptx-production.md` — python-pptx 구현·타이포·차트·출처 처리
- `reference/slide-compiler.md` — 재사용 Compiler API·semantic blueprint·고정 디자인 방지 규칙
- `reference/deck-recipe.md` — semantic Recipe·adaptive layout selection·certified component·QA Runner
- `reference/verification.md` — 구조 감사·렌더링·contact sheet·수정 절차
- `reference/full-optimized.md` — 단계 유지형 병렬화·캐시·PDF 재사용·시간 측정
- `scripts/audit_pptx.py` — 장수·경계·폰트·밀도·압축 구조 감사
- `scripts/render_pptx.py` — soffice/PyMuPDF 기반 소형 JPEG·contact sheet·검증된 PDF 재사용
- `scripts/verify_deck.py` — audit·전체 render·위험 슬라이드·ZIP 검사를 한 번에 실행
- `pptx_compiler/` — Design DNA를 입력받는 theme-agnostic PPTX 생성·preflight 엔진
