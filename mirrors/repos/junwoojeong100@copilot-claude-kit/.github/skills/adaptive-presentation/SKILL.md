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
| `LANG` | 사용자 언어 사용 |
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

제목만 연속해서 읽어도 논리가 완성되어야 한다. 결론이나 판단을 바꾸지 않는 장은 제거·통합하고,
고정 장수를 채워야 하면 반복 문구 대신 근거·사례·비교·실행 기준을 추가한다.
코드 작성 후에는 새 근거나 시각적 blocker가 있을 때만 storyline과 deck spec을 함께 갱신한다.
목적별 서사 패턴은 [`reference/narrative-patterns.md`](./reference/narrative-patterns.md)를 참고한다.

### 3. 제작

- [`reference/pptx-production.md`](./reference/pptx-production.md)를 따라 `python-pptx`로 직접 만든다.
- 템플릿이 있으면 `scripts/inspect_template.py`로 profile을 만들고 template-aware initializer로
  master·layout·theme·canvas를 보존한다. 없으면 고정 템플릿을 강제하지 않는다.
- `scripts/toolcheck.py`가 선택한 언어·환경별 설치 폰트를 `deck-spec.json`에 기록하고 제작에 사용한다.
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
- 최종 PPTX revision과 일치하는 전체 시각 검토 증거가 있다.
- PPTX가 정상적으로 열리고 압축 구조 오류가 없다.
- 저장소와 최종 출력 폴더에 임시 `.py`, `.pyc`, `__pycache__`, PDF, QA 이미지가 남지 않는다.
## 참고

- 제작·서사·시각: [`pptx-production`](./reference/pptx-production.md) ·
  [`narrative-patterns`](./reference/narrative-patterns.md) · [`slide-blueprints`](./reference/slide-blueprints.md)
- 계약·검증·최적화: [`deck-spec`](./reference/deck-spec.md) ·
  [`verification`](./reference/verification.md) · [`full-optimized`](./reference/full-optimized.md)
