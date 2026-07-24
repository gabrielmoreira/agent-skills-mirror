---
name: ai-platform-demo
description: "특정 고객·산업을 위한 실제 동작하는 AI·App Platform 운영 데모를 단일 HTML SaaS 앱으로 생성합니다. Golden Runtime과 고정 GitHub Primer Dark Dimmed 계열 soft-dark 디자인을 재사용하고 목적에 맞는 4~8개 route의 메뉴·데이터·서사만 교체합니다. 첫 화면에서 결론·가치·다음 행동을 보여주는 임원 보고·영업 데모입니다. WHEN: 고객사 맞춤 AI 플랫폼 데모, 고객용 App Platform 운영 데모, 산업별 인터랙티브 SaaS 데모, 임원용 단일 HTML 운영 대시보드. NOT WHEN: 일반 AKS·ACA·CI/CD 설명, 코드 샘플, 아키텍처 문서, 슬라이드/PPT, 고객·산업 맥락이 없는 범용 웹 앱."
argument-hint: "고객 이름, 산업, 청중, 데모 focus를 알려주세요 — 예: 'OO사, CIO 대상 App Platform·CI/CD 중심'"
---

# AI · App Platform Demo

특정 고객의 임원이 직접 클릭하며 가치를 이해할 수 있는 **단일 HTML SaaS 데모**를 만든다.
디자인과 runtime은 재사용하고, 고객별 서사·메뉴·데이터·Agent만 교체한다.

## 산출물

- 인라인 CSS/JS를 포함한 단일 `.html` 파일 1개
- GitHub Primer Dark Dimmed 계열 soft-dark 디자인의 4~8-route SPA
- 대시보드와 목적에 필요한 고객 업무/App Platform 운영, 개발·배포, AI Agent, 거버넌스 route를 포함
- 버튼·슬라이더·목록·채팅이 실제 동작하고 KPI·차트·활동 피드가 변하는 데모
- 모든 화면에 `● 시연 데이터` 표시

고객별 작업 파일과 스크린샷은 저장소와 최종 출력 폴더 밖의 세션 작업 디렉터리에 둔다. 재사용 가능한
Puppeteer·Chromium만 외부 공용 캐시에 유지하고, 최종 출력 위치에는 HTML 하나만 남긴다.

## 입력

| 입력 | 처리 |
|---|---|
| `CUSTOMER` | 고객 회사명 |
| `INDUSTRY` | 주요 사업·산업 |
| `AUDIENCE` | 임원 직무와 관심사 |
| `DEMO_FOCUS` | `균형형`, `AI 중심`, `App Platform·CI/CD 중심` |
| `EMPHASIS` | 강조할 Microsoft·GitHub 서비스 |
| `LANG` | 지정 언어를 준수. 미지정 시 한국어, 공식 제품명·일반 약어는 원문 유지 |
| `APP_NAME` | 기본 `<CUSTOMER> IQ` |
| `ROUTE_SCOPE` | 기본 8개, 좁은 목적이면 핵심 4~7개 route만 노출 |

고객과 산업은 필수다. 결과를 크게 바꾸는 모호성만 한 번에 하나씩 확인한다. `CI`, `PI`처럼 의미가
여러 개인 직무 약어는 실제 역할을 확인한다.

## 표현 계약

- 첫 화면에서 고객 결과 한 문장, KPI 4개, primary action 1개를 보여준다.
- 각 route는 임원의 질문 하나에 답하고 행동 하나를 강조한다.
- 기본 시연 동선은 4~6개 핵심 장면으로 끝낸다. 전체 운영 서사는 8개 route를 쓰고, 좁은 목적의
  데모는 결론에 필요한 4~7개만 노출한다.
- 제품 catalog로 시작하지 않는다. 고객 가치 → 업무 흐름 → 담당 서비스 순으로 설명한다.
- 고객의 현재 도입이 확인되지 않은 서비스는 `목표 아키텍처` 또는 `시연 가정`으로 표시한다.
- 임원이 보는 메뉴·제목·버튼·상태·표·Agent 문구는 `LANG`를 따른다. 한국어일 때만 자연스러운
  한국어를 우선하고 공식 제품명·일반 약어는 원문을 유지한다.

플랫폼 역할은 고객 과제에 필요한 화면에서만 구체적으로 연결한다.

- Microsoft Foundry + Microsoft Agent Framework: 모델·Agent·도구·오케스트레이션·평가
- GitHub Copilot + GitHub Platform: 계획·코드·PR·GitHub Actions·GitHub Advanced Security
- AKS + Azure Container Apps: 애플리케이션·Agent workload의 배포·확장·운영
- Microsoft Entra·Purview·Defender·Azure AI Content Safety·GitHub AI Controls: 통제와 거버넌스

## 필수 워크플로

### 1. 고객 조사

- 먼저 `web-search` 스킬로 고객 사업, 규모, DX/AI/App Platform/DevOps 현황, 최근 이슈를 조사한다.
- 검색 backend와 원문 검증 방법은 `web-search`가 결정하며 이 스킬에서 별도 정책을 정의하지 않는다.
- 고객 요청마다 변동 사실을 다시 확인하고, 이전 Ledger와 Industry Pack은 검색 출발점으로만 사용한다.
- 결과를 `web-search`의 공통 Fact Ledger 계약과 schema에 맞춘 `fact-ledger.json`으로 저장한다.
  `checkedAt`과 서로 다른 canonical `Fact` source URL 2개 이상이 필요하다.
  데모 매핑이 필요하면 `Demo candidate`만 확장 필드로 추가한다.
- 모든 고객 사실·KPI 범위·서사는 이 Ledger에 근거한다. 확인하지 못한 내용은 사실처럼 표현하지 않는다.

### 2. 스토리라인

`storyline.md`에 다음만 먼저 확정한다.

1. 고객 과제와 목표 결과를 연결하는 서사 한 줄
2. 청중 직무별 핵심 메시지와 담당 route
3. 4~6개 핵심 시연 동선, focus별 climax, 노출할 `story.routeScope`

서사는 고정 인용문이나 범용 AI 메시지에서 시작하지 않는다. 조사로 확인한 고객 과제와 사업 언어에서
시작한다. `AI 중심`은 Agent 협업·평가·거버넌스, `App Platform·CI/CD 중심`은
계획→코드→배포→운영→학습의 폐루프를 climax로 둔다.

### 3. View Contract와 Customer Overlay

[`reference/screen-blueprints.md`](./reference/screen-blueprints.md)를 참고해 기본 8개 route를 고객
산업에 매핑한다. 좁은 목적이면 `story.routeScope`로 노출할 4~7개를 고르고, `view-contract.md`에는
노출 route별 질문·KPI·primary action·필수 DOM ID·시뮬레이터 결과·Agent 전환 조건을 기록한다.

[`reference/composable-spec.md`](./reference/composable-spec.md)에 따라 `customer-overlay.json`을 만든다.
Overlay는 고객 `meta`·`story`·route·Agent만 소유하며 `design`을 정의하지 않는다. 디자인은 Golden
Runtime이 고정 제공한다.

### 4. 빌드

1. 적합한 Industry Pack이 있으면 terminology·공식·Agent 역할의 출발점으로 사용한다.
2. Pack이 맞지 않으면 억지로 사용하지 않고 전체 Spec을 직접 작성한다.
3. `scripts/compose_demo_spec.py`로 Base + Pack + Overlay + Fact Ledger를 합쳐
   `demo-spec.json`과 HTML을 생성한다.
4. 직접 작성한 Spec은 먼저 `scripts/lint_spec.py`로 검사한 뒤 `scripts/render_demo.py`로 렌더한다.
5. 기본 수정 surface는 HTML이 아니라 `customer-overlay.json`이다.
6. Golden Runtime으로 핵심 장면을 표현할 수 없을 때만 해당 route를 세션 작업 폴더에서 확장한다.
   고객 전용 분기를 공용 runtime이나 Pack에 추가하지 않는다.

구체 명령과 파일 계약은
[`reference/authoring-cheatsheet.md`](./reference/authoring-cheatsheet.md),
[`reference/composable-spec.md`](./reference/composable-spec.md),
[`reference/demo-spec.md`](./reference/demo-spec.md)를 따른다.

### 5. 검증

[`scripts/verify_demo.js`](./scripts/verify_demo.js)와
[`reference/verification.md`](./reference/verification.md)를 사용한다.

1. 노출된 모든 route를 한 browser/page 세션에서 전체 렌더한다.
2. 레이아웃·겹침·깨짐·`LANG` 위반을 화면별로 확인한다.
3. 콘솔/페이지 오류와 빠른 route 전환 오류가 0인지 확인한다.
4. 슬라이더, action button, 모든 클릭 가능한 행, Agent 전환, 채팅을 검증한다.
5. 결함을 일괄 수정하고 영향 route를 빠르게 확인한다.
6. 수정 후에는 완료 전에 전체 route와 핵심 interaction을 다시 검증한다.

캐시와 증분 검증 방법은 [`reference/full-optimized.md`](./reference/full-optimized.md)를 따르되 최종 전체
QA를 생략하지 않는다.

## 완료 조건

- 최종 산출물이 외부 빌드 없이 열리는 단일 HTML이다.
- 첫 화면에서 고객 결과·KPI·primary action이 즉시 보인다.
- 목적에 맞는 4~8개 route와 4~6개 핵심 시연 동선이 완성됐다.
- 노출된 모든 route, 버튼, 슬라이더, 클릭 가능한 행, Agent 전환, 채팅이 동작한다.
- 콘솔/페이지 오류와 route 전환 시 null 접근·listener 누수가 없다.
- 고객 사실은 Fact Ledger와 연결되고 가정 수치는 `시연 데이터`로 표시된다.
- 디자인은 공용 Golden Runtime을 유지하고 고객 전용 내용이 runtime·Pack에 섞이지 않았다.
- 저장소와 최종 출력 폴더에는 결과 HTML 외 임시 파일이 남지 않는다.

## 참고

- Golden Runtime: [`reference/golden-runtime.md`](./reference/golden-runtime.md)
- 고정 디자인: [`reference/fixed-design-dna.md`](./reference/fixed-design-dna.md)
- 화면 매핑: [`reference/screen-blueprints.md`](./reference/screen-blueprints.md)
- Spec 합성: [`reference/composable-spec.md`](./reference/composable-spec.md)
- 직접 작성: [`reference/authoring-cheatsheet.md`](./reference/authoring-cheatsheet.md)
- 검증: [`reference/verification.md`](./reference/verification.md)
- 최적화: [`reference/full-optimized.md`](./reference/full-optimized.md)
