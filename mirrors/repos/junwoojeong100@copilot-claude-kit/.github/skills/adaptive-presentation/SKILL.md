---
name: adaptive-presentation
description: "주제·청중·목적에 맞춘 편집 가능한 PowerPoint(.pptx)를 결론과 다음 행동이 먼저 보이도록 만듭니다. 기존 덱은 핵심 내용을 보존하며 대비·도식·가독성을 개선하고 새 버전으로 전달합니다. 필요한 조사 → 스토리라인 → python-pptx 제작 → 렌더 검증 순으로 실행합니다. WHEN: PPT 만들어줘, PPTX 생성, 기존 PPT 개선, 가독성·Straightforwardness 개선, 발표자료, 슬라이드 덱, 임원 보고자료, 제안서, 영업 자료, 제품 소개서, 기술 아키텍처 발표, 교육·세미나·컨퍼런스 자료. NOT WHEN: 기존 문서의 텍스트 요약만 필요하거나 PowerPoint 파일이 아닌 웹 앱·단일 HTML 데모를 요청한 경우."
argument-hint: "주제, 청중, 목적, 슬라이드 수를 알려주세요 — 예: '병원 경영진 대상 의료 AI 전략, 의사결정용 20장'"
---

# Adaptive Presentation

사용자가 바로 발표하고 편집할 수 있으며 첫 본문부터 **결론·의미·다음 행동**이 보이는 PowerPoint를 만든다.

## 산출물

- 기본 산출물: 덱마다 요청한 장수의 편집 가능한 `.pptx` 1개. 명시적 요청 없이 원본을 덮어쓰지 않는다.
- 템플릿이 없으면 16:9, 있으면 그 canvas를 보존한다. PDF·생성 스크립트는 요청한 경우에만 추가한다.
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

### 0. 기존 덱 개선

- 기존 PPT 개선은 [`reference/refinement.md`](./reference/refinement.md)를 먼저 따른다. 내용 원본과
  디자인 참고 덱을 구분하고, 장수·발표 시간·사례·수치·조건·출처를 목록화한 뒤 새 버전을 만든다.
- 여러 덱은 각각 완성·검증한다. 파일별 위임을 요청받았을 때만
  [`reference/full-optimized.md`](./reference/full-optimized.md)의 단일 소유·공통 근거 공유 계약을 적용한다.

### 1. 조사와 Fact Ledger

- 외부 사실·최신 정보·가격·규제·제품 상태·고객 성과를 사용하는 경우 `web-search` 스킬을 호출한다.
  검색 backend와 원문 검증 방법은 `web-search`가 결정한다.
- 사용자 제공 자료만 재구성하거나 외부 사실이 없는 창작형 덱은 불필요한 웹 조사를 강제하지 않는다.
- 복합 조사는 공통 Fact Ledger 계약의 `fact-ledger.json`을 정본으로 검증하고, `fact-ledger.md`는
  `web-search` 검증기의 `--markdown-output`으로 생성한다. Ledger를 확장하지 않고
  슬라이드 매핑은 storyline과 deck spec에 기록한다.
- 공개 사례·협력 발표·검토 후보를 구분하고, 수치의 분모·기간·초기 결과 같은 조건을 함께 표시한다.
  상충·Preview·가정·시연 데이터도 표시하며, 필요한 근거가 모이면 검색을 종료한다.

### 2. 스토리라인

- 코드 전에 [`reference/deck-spec.md`](./reference/deck-spec.md)의 `deck-spec.json`과 `storyline.md`에
  장별 결론형 제목·한 문장 메시지·다음 행동·근거·시각 형태·앞뒤 연결·발표 cue를 확정한다.
- 제목만 읽어도 논리가 이어져야 한다. 반복 설명은 통합하되 원본의 의미·조건을 누락하지 않는다.
  장수가 고정이면 장식 대신 근거·사례·비교·실행 기준으로 채운다.
- 새 근거나 시각적 blocker가 있을 때만 storyline과 deck spec을 함께 갱신한다.
  목적별 흐름은 [`reference/narrative-patterns.md`](./reference/narrative-patterns.md)를 참고한다.

### 3. 제작·가독성

- [`reference/pptx-production.md`](./reference/pptx-production.md)를 따라 `python-pptx`로 직접 만든다.
- 템플릿이 있으면 `scripts/inspect_template.py`로 profile을 만들고 template-aware initializer로
  master·layout·theme·canvas를 보존한다. 없으면 고정 템플릿을 강제하지 않는다.
- 첫 본문에서 결론·가치·다음 행동을 보여준다. 한 장은 질문 하나·결론 하나·핵심 근거 2~4개를 맡는다.
- 제목+불릿 대신 전후 비교·흐름·책임 경계·표·차트·타임라인으로 관계를 보여준다.
  핵심 도형·차트·텍스트는 편집 가능한 native visual로 만들고 같은 카드 구조를 기계적으로 반복하지 않는다.
- [타이포그래피](./reference/pptx-production.md#typography)·[대비](./reference/pptx-production.md#contrast)의
  상세 기준은 제작 가이드 한 곳에서 관리한다. 작은 글씨로 과밀을 숨기지 않고 의미별 색을 일관되게 쓴다.
- `scripts/toolcheck.py`로 폰트를 확인하고 [글꼴 계약](./reference/pptx-production.md#fonts)을
  `fontPolicy`에 기록한다. 임의의 slide별 스타일 변경이나 전달 PPTX의 fallback 혼용은 허용하지 않는다.
- 한국어 설명을 우선하고 공식 서비스·기능·API·SDK·component 이름은 영문으로 유지한다.
  새 핵심 technical term은 장당 3~5개로 제한하고 `쉬운 결론 → 공식명 → 한글 역할 → 고객 의미`로 읽히게 한다.
- `languagePolicy`의 `targetLatinRatio=0.40`, `maxLatinRatio=0.55`, `maxSlideLatinRatio=0.75`를 유지한다.
  `protectedTerms`는 실제 공식명·정착된 기술 용어만 중립 처리하며, 비율을 맞추려고 설명 문장을 등록하지 않는다.
- 한국어 전 장의 notes는 새 덱에서 재생성하고 [발표 노트 계약](./reference/pptx-production.md#speaker-notes)을
  따른다. 기본 `core-only`와 명시적으로 요청된 `guided-flow`를 구분하고 쉬운 구어체로 관계와 고객 의미를 설명한다.
- footer는 발행자·문서명과 원문 링크로 표시하고 내부 Fact ID는 노출하지 않는다.
  원본 확인 날짜는 기본적으로 화면에서 생략하되 Fact Ledger의 `accessed`에는 보존한다.
  수치 기준일·발행 연도·버전·시행일처럼 의미를 바꾸는 날짜와 조건은 삭제하지 않는다.
- 차트는 실제 데이터·축·단위를 사용한다. 그림은 설명에 기여할 때만 넣고 사용권·원문을 확인한다.
  슬라이드를 통째로 이미지화하거나 권한이 불분명한 로고·인물을 임의 생성하지 않는다.

### 4. 렌더 검증과 수정

```bash
python3 -B .github/skills/adaptive-presentation/scripts/verify_deck.py <deck>.pptx --out <work> \
  --deck-spec <work>/deck-spec.json --reuse-render
```

- [`scripts/verify_deck.py`](./scripts/verify_deck.py)와 [`검증 가이드`](./reference/verification.md)로
  동일 PPTX의 구조 감사·전체 렌더를 실행한다. 전체 contact sheet는 한 장씩 보고 위험 장만 확대한다.
- 미지원 chart·SmartArt·unmapped text도 finding ID별로 검토한다. 결함을 일괄 수정하고 다시 렌더한다.
  의도적 예외만 이유를 기록하며, 최종 SHA-256에 묶인 `visual-review.json`으로 verifier를 재실행한다.
  재사용 모드의 증거는 현재 `qa/render-cache.json`의 SHA-256을 `renderCacheSha256`으로 연결해 환경 변경 시 무효화한다.
- `--reuse-render`는 입력·환경·옵션·산출물 해시가 같은 전체 렌더만 재사용한다. QA 판단은 매번 다시 검사하며,
  변경된 입력은 새로 렌더한다. 손상된 캐시는 오류로 처리하고 옵션 없는 실행으로 새 검증을 수행한다.
- `claimIds`에서 출처 대상이 도출되며 footer 발행자·상태·언어·폰트·notes를 검증한다.
  대비 측정·의미 보존·발표 시간은 별도 편집 검토로 확인하고 자동 PASS와 혼동하지 않는다.

## 완료 조건

- 요청한 형식·장수·언어·템플릿·내용 보존 조건을 지키고, 첫 본문부터 결론과 다음 행동이 읽힌다.
- 본문에는 관계형 visual이 있고 발표 거리에서 읽힌다. 표지·구분·마무리에는 장식 도식을 강제하지 않는다.
- 자동 검증 결함이 없고, 미지원 객체·대비·조건·notes의 구어체는 별도로 검토했다.
- 최종 revision의 시각 검토·ZIP·전달 파일 해시와 원본 보존(명시적 덮어쓰기 대상 제외)을 확인했다.
- 저장소와 최종 출력 폴더에는 요청한 파일만 남기고 작업 소유 임시 PDF·QA 이미지·`.pyc`를 정리했다.

## 참고

- 제작·서사·시각: [`pptx-production`](./reference/pptx-production.md) ·
  [`narrative-patterns`](./reference/narrative-patterns.md) · [`slide-blueprints`](./reference/slide-blueprints.md) ·
  [`editorial-business-style`](./reference/editorial-business-style.md)
- 기존 덱 개선·최적화: [`refinement`](./reference/refinement.md) · [`full-optimized`](./reference/full-optimized.md)
