---
name: adaptive-presentation
description: "주제·청중·목적에 맞춘 PowerPoint(.pptx) 발표자료를 실시간 조사 → 스토리라인 설계 → 자유 슬라이드 제작 → 빠른 렌더 검증 순으로 만든다. 핵심은 데이터 수집과 스토리라인 구성이며, 슬라이드 시각화는 고정 템플릿·고정 프레임워크 없이 매 요청마다 자유롭고 다양하게 python-pptx로 직접 만들되 제작·검증 시간을 최소화한다. WHEN: PPT 만들어줘, PPTX 생성, 발표자료, 슬라이드 덱, presentation deck, executive presentation, 임원 보고자료, 제안서, 영업 자료, 제품 소개서, 기술 아키텍처 발표, 교육 자료, 세미나 자료, 투자 설명자료, 전략 보고서, 컨퍼런스 발표, 10장/20장/30장 슬라이드."
argument-hint: "주제, 청중, 목적, 슬라이드 수를 알려주세요 — 예: '병원 경영진 대상 의료 AI 전략, 의사결정용 20장'"
---

# Adaptive Presentation Studio

임의의 주제와 청중을 위한 **실제 편집 가능한 PowerPoint**를 만든다. 이 스킬의 무게 중심은
**① 실시간 데이터 수집(Fact Ledger)** 과 **② 목적에 맞는 스토리라인 설계**다. 슬라이드 시각화는
고정 템플릿이나 고정 생성 프레임워크에 의존하지 않고, 매 요청마다 주제에 맞게 **자유롭고 다양하게**
`python-pptx`로 직접 구성한다. 다만 제작과 검증에 드는 시간은 최소화한다.

## 산출물

기본 사용자 산출물은 1개다.

1. `<topic>_<audience>_<count>slides.pptx` — 요청한 장수의 편집 가능한 16:9 PowerPoint

생성 스크립트·조사 메모·QA 이미지는 내부 작업 자산으로만 유지한다.

`<session>`은 클라이언트가 제공하는 **세션 전용 artifact 디렉터리**를 뜻한다. 그런 디렉터리가 없으면
저장소와 최종 출력 폴더 **밖**의 OS 임시 영역에 이 작업만을 위한 고유 디렉터리를 만든다. 특정
클라이언트의 `<session>/files` 구조를 가정하지 않는다. 작업 시작 전 경로를 resolve해 저장소·최종 출력
폴더의 하위가 아님을 확인하고, 완료 시 내부 작업 디렉터리 전체를 정리한다.

```text
<session>/<deck>-work/
  fact-ledger.md
  storyline.md
  build_<deck>.py
  qa/
```

이 파일들을 저장소 내부나 사용자의 최종 출력 폴더에 만들거나 복사하지 않는다. 사용자가 소스
스크립트나 PDF를 명시적으로 요청한 경우에만 별도 최종 산출물로 제공한다. 중간 PDF·QA JPEG도 세션 작업
폴더에 두고 완료 시 정리하며, 최종 출력 위치에는 사용자가 요청한 최종 artifact만 남긴다.

## 입력 해석

| 입력 | 의미 | 없을 때 |
|---|---|---|
| `TOPIC` | 발표 주제와 범위 | 반드시 확인하거나 문맥에서 명확히 추론 |
| `AUDIENCE` | 직급·직무·사전지식 | 목적에서 추론, 방향이 크게 달라지면 한 번 질문 |
| `PURPOSE` | 설명·의사결정·설득·교육·영업·보고 | 사용자 동사와 상황에서 추론 |
| `SLIDE_COUNT` | 정확한 장수 | 지정하면 정확히 준수, 미지정 시 목적에 맞춰 결정 |
| `LANG` | 언어와 용어 표기 | 사용자 언어 |
| `TEMPLATE/BRAND` | 사용자가 준 .pptx 템플릿·로고·색 | 있으면 그대로 활용, 없으면 주제에 맞게 자유 구성 |
| `OUTPUT` | 최종 파일명·경로·PPTX/PDF | 사용자 출력 위치에는 요청한 최종 파일만 생성 |

이미 충분한 정보가 있으면 질문하지 말고 진행한다. 결과를 크게 바꾸지만 문맥에서 추론할 수 없는
선택만 한 번에 하나씩 사용자에게 확인한다. `ask_user`를 사용할 수 있으면 사용하고, 없으면 클라이언트의
일반 채팅 UX로 한 가지 핵심 질문만 한다. 비대화형 환경에서는 가장 합리적인 가정을 명시하고 진행한다.

## 핵심 원칙

- **조사와 스토리라인 우선**: 시간과 노력의 대부분은 사실 수집과 논리 설계에 쓴다. 슬라이드는 그
  결과를 담는 그릇이다.
- **실시간 사실**: 외부 사실은 매 요청마다 다시 조사한다. 기능 상태·가격·규제·고객 성과는 항상 재확인.
- **정해진 틀 없이**: 슬라이드 시각화는 고정 템플릿·고정 컴포넌트·강제 레이아웃 목록을 따르지 않는다.
  주제·내용에 맞게 매번 다양하게 구성한다.
- **템플릿 우선 편집**: 사용자가 준 템플릿·샘플 덱·브랜드 가이드가 있으면 그 master·grid·font·color를
  먼저 분석해 따른다. `Cowork-like` 요청은 Anthropic 브랜드 복제가 아니라 템플릿 인식형 편집 품질을 뜻한다.
- **제목이 서사**: 슬라이드 제목만 연속해서 읽어도 논리가 완성되어야 한다.
- **제목 규격 일관성**: 표지·section divider를 제외한 같은 역할의 본제목은 덱 전체에서 한 가지 font
  size를 사용한다. 긴 제목은 문구·폭·전용 행 높이로 해결하고 슬라이드마다 31/32/34pt처럼 임의 축소하지
  않는다.
- **한 장 한 메시지**: 슬라이드마다 결론 1개, 시각 구조 1개, 보조 근거 2~4개를 기본으로 한다.
- **문서 붙여넣기 금지**: 긴 문단·작은 글씨·표 과밀로 장수를 채우지 않는다.
- **편집 가능성**: 핵심 도형·다이어그램·차트·텍스트는 PowerPoint 벡터 객체로 만든다.
- **절제된 임원 팔레트**: 브랜드·템플릿이 없는 CIO/임원 자료는 Microsoft Fluent 계열의 neutral
  canvas/ink + primary blue + 선택적 blue-teal처럼 **3~4개 색상 계열**로 제한한다. 같은 의미는 같은
  색을 쓰고, 카드마다 다른 포인트 색을 배정하는 rainbow palette를 피한다.
- **요청된 캔버스 우선**: 사용자가 `완전 흰 배경`을 요청하면 모든 슬라이드 canvas를 정확히
  `#FFFFFF`로 고정한다. 섹션 리듬은 off-white 슬라이드 배경 교대가 아니라 여백·구성·surface로 만든다.
- **컨테이너 우선 타이포**: 텍스트는 도형과 제목 전용 행 안에 여유를 두고 들어가야 한다. 넘칠 때는
  내용·도형 높이·줄바꿈을 먼저 조정하고, 사용자가 축소를 요청했거나 소폭 축소로 해결되면 문제 frame만
  줄인다.
- **역할별 소폭 축소**: 사용자가 전체 글자를 조금 줄여 달라고 하면 title/body/secondary/label 역할별로
  0.5~2pt를 일관되게 낮추고, 특정 슬라이드나 긴 문장만 임의 축소하지 않는다. 축소로 생긴 여백에는
  근거·KPI·owner·예외 조건처럼 의사결정에 필요한 정보만 보강하며 장식적 문장으로 채우지 않는다.
- **기하·렌더 이중 겹침 검사**: shape frame 좌표만 보지 않고 PDF에 실제 렌더된 text span까지 검사한다.
  `--strict` 완료 조건은 승인되지 않은 geometry overlap과 rendered text overlap이 모두 0인 상태다.
  의도적 연결·포함 겹침은 시각 확인 후에만 `--allow-overlap`으로 슬라이드 단위 승인한다.
- **편집형 비즈니스 기본값**: 템플릿이 없는 임원 자료는 강한 제목 위계, 정밀한 grid, 넓은 여백,
  hairline rule, native chart/table/diagram을 기본으로 한다. 둥근 카드·pill·soft shadow를 반복하지 않는다.
- **매 장 시각 구조**: 이미지가 없어도 숫자, 표, 차트, 흐름, 계층, 비교, 타임라인 중 하나는 있어야 한다.
  제목+불릿만 있는 슬라이드를 기본값으로 만들지 않는다.
- **사실 우선**: 보기 좋은 허위 수치보다 검증된 적은 정보가 낫다.
- **시간 최소화**: 슬라이드는 한 번에 생성하고, 검증은 한 번의 전체 렌더로 확인한 뒤 결함을 모아 일괄
  수정한다. 불필요한 반복 렌더를 피한다.
- **렌더 검증 필수**: 생성 성공은 완료가 아니다. 최소 한 번은 이미지로 확인하고 결함을 고쳐야 완료다.

## 전체 워크플로

병렬화·캐시·일괄 수정 등 시간 단축 실행 규칙은
[`reference/full-optimized.md`](./reference/full-optimized.md)를 따른다.

### 1단계 — 데이터 수집과 Fact Ledger

1. 외부 사실이 있는 발표자료는 매 요청마다 `google-web-search`와 공식 도구로 실시간 조사한다.
2. 독립적인 조사 축을 **먼저 모두 정한 뒤 한 번의 병렬 tool call 배치**로 동시에 실행한다(왕복 최소화). 결과를 본 뒤 꼭 필요할 때만 축을 추가한다.
3. 1차 출처를 우선하고, 숫자·날짜·제품 상태·규제·고객 성과에는 URL과 확인일을 기록한다.
4. 메인 에이전트가 결과를 하나의 Fact Ledger(`fact-ledger.md`)로 합친다.

| Claim | Evidence | Source | Date/status | Slide candidate |
|---|---|---|---|---|

5. 상충하는 사실은 공식 최신 출처를 우선하고, 해결되지 않으면 슬라이드에서 불확실성을 표시한다.
6. Preview·가정·시연 데이터·추정치는 눈에 띄게 라벨링한다.

### 2단계 — 스토리라인 설계

[`reference/narrative-patterns.md`](./reference/narrative-patterns.md)를 읽고 목적에 맞는 서사 흐름을 고른다. 패턴은 제목을 채우는
템플릿이 아니라 **청중의 생각이 이동하는 순서**다.

요청 장수를 정확히 배분하고, 각 슬라이드에 다음을 정의해 `storyline.md`에 확정한다.

- 결론형 제목
- 청중이 기억해야 할 한 문장
- 근거와 출처(어떤 Fact Ledger 항목을 쓰는지)
- 정보 관계(숫자/흐름/비교/계층/사례 등)에 맞는 시각 형태
- 이전/다음 슬라이드와의 논리적 연결

조사와 스토리라인이 잠기기 전에는 슬라이드 코드를 작성하지 않는다. 변경이 필요하면 먼저
`storyline.md`를 갱신한다.

### 3단계 — 슬라이드 자유 제작

[`reference/pptx-production.md`](./reference/pptx-production.md)를 읽고 세션 작업 폴더의
`build_<deck>.py`에서 **`python-pptx`로 직접**
슬라이드를 만든다. 고정 생성 엔진이나 컴포넌트 라이브러리를 쓰지 않는다.
`Cowork-like`·컨설팅·임원 편집 스타일 요청은
[`reference/editorial-business-style.md`](./reference/editorial-business-style.md)를 함께 읽는다.

빌드 전 [`scripts/toolcheck.py`](./scripts/toolcheck.py)로
소프트웨어(soffice·PyMuPDF·Pillow·python-pptx)와 한글 폰트를 한 번 확인·캐시한다
(이후 재탐색 생략). 원하면 [`pptx_helpers.py`](./pptx_helpers.py)(디자인 중립 기계적 프리미티브:
box·text·bullets·chip·chevron·
grid_table)를 import해 보일러플레이트를 줄인다 — 색·레이아웃·구조는 여전히 매 덱 자유롭게 정한다.

- 기본 화면비 16:9(13.333 × 7.5 inch), 사용자가 다른 비율·템플릿을 주면 따른다.
- 정보 관계에 맞는 시각 형태를 슬라이드마다 자유롭게 선택한다. 아이디어가 필요하면
  [`reference/slide-blueprints.md`](./reference/slide-blueprints.md)의 관계형 패턴을 **선택적 참고**로만
  사용하고 그대로 복제하지 않는다.
- 같은 구조를 기계적으로 반복하지 않는다. 숫자는 크게, 과정은 흐름으로, 비교는 공통 축으로, 구조는
  계층으로 표현한다.
- 템플릿이 없으면 한 가지 visual motif를 고르고, dominant color 1개(시각 무게 약 60~70%) +
  support 1~2개 + sharp accent 1개 안에서 덱 전체를 구성한다.
- 제목 바로 아래의 짧은 장식용 accent line, 반복 pill chip, rounded-card grid, soft shadow는 기본값으로
  쓰지 않는다. 구분은 grid·여백·타이포·hairline rule로 먼저 만든다.
- 색·글꼴은 주제와 (있다면) 사용자 브랜드에 맞게 자유롭게 정하되 본문 대비는 최소 4.5:1을 지킨다.
  브랜드가 없는 임원 자료는 neutral 2계열 + primary 1계열 + optional secondary 1계열을 기본으로 하고,
  동일 계열의 tint/shade는 같은 색상 계열로 본다. 채도가 높은 accent는 최대 2계열만 사용한다.
- `완전 흰 배경` 요청이 있으면 모든 `slide.background`와 slide 전체를 덮는 canvas 도형은
  `RGB(255,255,255)`를 사용한다. 카드·강조 surface의 연한 neutral tint는 유지할 수 있다.
- 권장 크기: 제목 30~42pt, 주요 본문 15~19pt, 보조 13~15pt, 표·도식 label 11~13pt,
  출처 8~9.5pt. 긴 제목은 2줄 전용 높이를 확보하거나 문구를 줄이고, 28~29pt는 예외로만 사용한다.
- 본문 슬라이드의 title role은 빌드 시작 전에 한 크기(예: 30pt 또는 32pt)로 잠그고 전 장에 적용한다.
  표지·section divider만 명시적 예외로 두며, 예외가 필요하면 검수에서 `--allow-title-size`로 기록한다.
- 텍스트 도형은 렌더링 차이를 고려해 가로·세로 8~12%의 여유를 목표로 한다. 컨테이너를 벗어나면
  도형/문구 조정을 우선하고, 필요한 경우 보조 텍스트는 13pt, 본문은 15pt를 하한으로 해당 frame만
  0.5~1pt 단위로 줄인다.
- `01`·`02` 같은 단계 번호와 짧은 영문 라벨도 한 줄 폭을 실제 글꼴 기준으로 확보한다. 좁은 frame에서
  숫자·단어가 강제 줄바꿈되어 다음 행을 침범하지 않게 한다.
- chevron·arrow·connector는 카드 사이 gap 안에 배치한다. 대상 카드 아래로 일부를 숨기는 방식은 의도적
  예외가 아니면 사용하지 않는다.
- 대부분의 슬라이드는 주요 본문 40~65단어 이내로 유지한다. 축소 후 여백이 충분하면 근거·KPI·owner·
  예외 조건 중 1~2개를 추가하되, 이미 밀도가 높은 슬라이드는 내용을 늘리지 않는다.
- 차트는 실제 데이터에서 만들고 축·단위·기준일을 표시한다. 가짜 그래프를 만들지 않는다.
- 숫자·기능 상태·고객 성과 주장 슬라이드의 footer에 출처를 직접 표시한다.
- 인물 사진·고객 로고·브랜드 마크를 임의 생성하지 않는다. 사용 권한이 분명한 자산만 쓴다.
- Python은 `python3 -B` 또는 `PYTHONDONTWRITEBYTECODE=1`로 실행해 `__pycache__`·`.pyc`를 만들지 않는다.
- 폰트 설치 여부를 먼저 확인하고 한글/라틴 폴백을 정한다.

### 4단계 — 빠른 검증과 수정

[`reference/verification.md`](./reference/verification.md)의 절차와
[`scripts/verify_deck.py`](./scripts/verify_deck.py)(또는
[`scripts/audit_pptx.py`](./scripts/audit_pptx.py) +
[`scripts/render_pptx.py`](./scripts/render_pptx.py))를 사용한다. 목표는 **한 번의 전체 패스**로 결함을
찾아 일괄 수정하는 것이다.

1. 구조 감사와 최초 전체 렌더를 같은 immutable PPTX에 대해 병렬 실행한다.
   (`soffice` → PDF → PyMuPDF 소형 JPEG contact sheet) 구조 감사는 text/text·shape/shape·
   text/container 교차와 본문 title row의 font-size 편차를 찾고, 렌더 감사는 PDF text span의 frame
   이탈과 서로 다른 text frame 간 충돌을 찾는다.
2. 30장 단위 compact contact sheet 1장을 확인하고, 위험 슬라이드만 `--reuse-pdf`로 개별 확인한다.
3. 겹침·잘림·낮은 대비·고아 문장·경계 이탈·과도한 색상 분산 결함을 모두 기록한다. 텍스트가 도형,
   연결선, 다른 텍스트 상자 아래로 들어가거나 컨테이너 밖으로 나오는지, 긴 제목이 제목 행을 넘어
   구분선을 침범하는지도 개별 슬라이드에서 확인한다.
4. 결함을 한 번에 수정하고 PPTX를 재생성한다. 변경 후에는 새 PPTX에서 PDF를 다시 변환한다.
   **국소(단일·소수 슬라이드, 비구조) 수정이면 변경 슬라이드 이미지만 렌더·확인하고 전체 contact sheet는
   다시 만들지 않는다.**
5. 여러 슬라이드·구조가 바뀐 경우에만 전체 contact sheet를 다시 열람한다. 변경이 없으면 최초 전체
   렌더가 최종 검증이다.
6. 세션 작업 폴더의 임시 PDF·JPEG를 정리한다.

렌더링 도구가 없으면 가능한 대체 도구를 쓰되, 시각 검증 없이 완료했다고 주장하지 않는다.

### 첨부 용량 안전 규칙

- PPTX와 PDF를 `view`로 직접 열거나 대화에 첨부하지 않는다. 중간 PDF는 QA 동안만 두고 완료 시 삭제한다.
- 첫 검수는 5열 compact overview JPEG 1장만 확인한다.
- 문제가 의심되는 슬라이드만 `--reuse-pdf ... --slides 8,16 --keep-slide-images`로 확인한다.
- 한 응답에서 full-slide 이미지는 최대 2~3개만 확인하고, 여러 고해상도 이미지를 병렬 `view`하지 않는다.
- 미리보기 한 파일은 기본 900KiB 이하로 유지한다.
- 최종 답변에는 QA 이미지·PDF를 첨부하지 않고 사용자가 요청한 PPTX만 링크한다.

## 합격 기준

- 요청한 장수와 파일 형식이 정확하다.
- 제목만 읽어도 서사가 이어진다.
- 핵심 본문이 발표 거리에서 읽힌다(원칙 16pt+, 최소 15pt). 자동 감사의 13pt 하한은 secondary
  annotation과 label을 primary body로 오인하지 않기 위한 절대 안전선이며, 주요 본문 합격 기준을 대체하지 않는다.
- 모든 요소가 슬라이드 경계 안에 있고 텍스트가 도형 밖으로 넘치지 않는다.
- 의도하지 않은 도형-도형·도형-텍스트·텍스트-텍스트 겹침이 0이다.
- 모든 슬라이드에 내용 관계를 설명하는 native visual이 하나 이상 있다.
- 제목·본문·caption의 위계가 thumbnail에서도 즉시 구분되고, 같은 레이아웃이 의도 없이 3장 연속되지 않는다.
- 표지·section divider를 제외한 본문 슬라이드 제목 크기가 덱 전체에서 동일하다.
- `완전 흰 배경` 요청 시 모든 슬라이드 canvas가 `#FFFFFF`다.
- 브랜드가 없는 임원 자료는 3~4개 색상 계열 안에서 일관되고, 구조 요소마다 다른 색을 쓰지 않는다.
- 같은 구조를 기계적으로 반복하지 않고 정보 유형에 맞게 다양하게 구성했다.
- 숫자·기능 상태·고객 성과에 출처가 있다.
- Preview·가정·시연 데이터가 명확히 표시된다.
- PPTX가 열리고 `unzip -t` 압축 구조 오류가 없다.
- 저장소와 최종 출력 폴더에는 요청한 PPTX/PDF 외에 `.py`, `.pyc`, `__pycache__`, QA 이미지가 남지 않는다.

## 흔한 실패와 교정

| 실패 | 교정 |
|---|---|
| 조사를 건너뛰고 일반론으로 채움 | 실시간 공식 출처로 Fact Ledger를 먼저 만든다 |
| 30장을 같은 3열 카드로 채움 | 정보 유형별로 시각 형태를 바꿔 다양하게 재배치 |
| 제목+불릿만 있는 흰 슬라이드가 반복됨 | stat·chart·table·process·hierarchy·timeline 중 내용에 맞는 native visual 추가 |
| 둥근 카드·pill·그림자가 모든 장에 반복됨 | square surface·grid·hairline·여백 중심으로 바꾸고 한 가지 motif만 유지 |
| 제목 바로 아래 장식선이 반복됨 | 장식선을 제거하고 제목 높이·여백·section label로 계층을 표현 |
| 임원 자료가 빨강·초록·보라·노랑으로 알록달록함 | neutral + primary + optional secondary의 3~4개 계열로 줄이고 위치·크기·굵기로 구분 |
| 전체 글자가 너무 크고 본문이 비어 보임 | title/body/secondary/label을 역할별로 0.5~2pt 일괄 축소하고, 여백에는 근거·KPI·owner·예외 조건만 보강 |
| 글자가 작아짐 | 내용을 줄이고 슬라이드를 재구성. 본문 15pt·보조 13pt 아래 축소로 해결하지 않음 |
| 본문 슬라이드마다 제목이 31/32/34pt로 달라짐 | title role의 기준 크기를 하나로 잠그고 전 장에 적용. 긴 제목은 문구·폭·행 높이를 조정하고 의도적 예외만 `--allow-title-size`로 승인 |
| 도형이 겹치거나 글자가 컨테이너 밖으로 나옴 | `unexpected_overlap_candidates`와 `unexpected_rendered_text_overlaps`를 먼저 확인하고, gap·frame 폭·컨테이너 높이를 조정한다. 의도적 예외만 `--allow-overlap`로 승인 |
| 흰 배경 요청인데 일부 장이 연회색임 | 모든 slide canvas와 전체 화면 배경 도형을 `#FFFFFF`로 통일하고 surface만 neutral tint 사용 |
| 제목이 명사형 주제 | 청중이 받아들일 결론형 문장으로 변경 |
| 출처가 마지막 장에만 있음 | 해당 주장 슬라이드의 footer에 직접 표시 |
| 생성 후 파일만 열어봄 | compact JPEG overview와 선택 슬라이드를 실제로 확인 |
| 검증을 여러 번 반복해 시간 낭비 | 결함을 모아 한 번에 수정하고 변경 영향에 맞는 범위만 다시 렌더 |

## 참고 파일

- [`reference/narrative-patterns.md`](./reference/narrative-patterns.md) — 목적·청중별 스토리라인 패턴과 장수 배분
- [`reference/slide-blueprints.md`](./reference/slide-blueprints.md) — 정보 유형별 시각 형태 아이디어(선택적 참고)
- [`reference/editorial-business-style.md`](./reference/editorial-business-style.md) — Cowork-like·컨설팅형 편집 덱의 템플릿 우선 시각 원칙
- [`reference/pptx-production.md`](./reference/pptx-production.md) — python-pptx 직접 구현·타이포·차트·출처·파일 위생
- [`reference/verification.md`](./reference/verification.md) — 구조 감사·렌더링·contact sheet·빠른 수정 절차
- [`reference/full-optimized.md`](./reference/full-optimized.md) — 단계 유지형 병렬화·캐시·일괄 수정·시간 측정
- [`pptx_helpers.py`](./pptx_helpers.py) — (선택) 디자인 중립 python-pptx 프리미티브(색·좌표는 인자, 팔레트·레이아웃 없음)
- [`scripts/toolcheck.py`](./scripts/toolcheck.py) — soffice·PyMuPDF·Pillow·python-pptx·한글 폰트 탐지·캐시와 runtime 재검증
- [`scripts/tooling.py`](./scripts/tooling.py) — toolcheck와 renderer가 공유하는 LibreOffice resolver
- [`scripts/audit_pptx.py`](./scripts/audit_pptx.py) — 장수·경계·텍스트 상자/표 셀의 글자 크기·밀도·압축 구조와 geometry overlap 감사
- [`scripts/render_pptx.py`](./scripts/render_pptx.py) — soffice/PyMuPDF 기반 소형 JPEG·contact sheet 렌더
- [`scripts/rendered_overlap.py`](./scripts/rendered_overlap.py) — PDF text span을 원본 frame에 매핑해 실제 글자 충돌·이탈 후보 탐지
- [`scripts/verify_deck.py`](./scripts/verify_deck.py) — audit·전체 render·PDF text-span collision·위험 슬라이드·ZIP 검사를 한 번에 실행
