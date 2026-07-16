---
name: ai-platform-demo
description: "특정 고객·산업을 위한 '실제로 동작하는' AI 운영 플랫폼 데모를 Golden Runtime 기반 고정 GitHub Primer Dark Dimmed 계열 soft-dark 디자인의 단일 HTML(SaaS 앱)로 생성합니다. 사이드바·실시간 대시보드·도메인별 운영 콘솔·AI 에이전트 채팅·거버넌스를 갖춘 임원 보고/영업 데모. 고객 이름과 주요 사업이 바뀌어도 soft-dark 디자인은 고정하고 메뉴와 데이터만 고객·산업별로 바꿉니다. Microsoft Foundry·Agent Framework·GitHub Copilot 가치를 고객 사업에 매핑. WHEN: 고객 AI 데모, 임원 데모, 회장 보고 데모, executive demo, AI 플랫폼 데모, AI platform demo, SaaS 데모, 운영 대시보드 데모, operations dashboard demo, 산업 AI 데모, industry AI demo, Foundry/Copilot 데모, 고객사 맞춤 데모, 인터랙티브 데모 HTML, single-file HTML app demo, AI 에이전트 데모, agent studio demo, 식음료 AI 데모, 제약 AI 데모, 헬스케어 AI 데모, 금융 AI 데모, 소프트웨어 개발 AI 데모, SW개발 AI 데모, 교육 AI 데모, 보안 SOC AI 데모."
argument-hint: "고객 이름과 주요 사업(산업)을 알려주세요 — 예: '삼표산업, 레미콘·골재·시멘트', 'OO식품, 식음료 제조·유통', 'OO은행, 금융'"
---

# AI 플랫폼 데모 생성기 (Customer AI Platform Demo)

특정 고객을 위한 **실제로 동작하는 단일 HTML SaaS 앱**을 만든다. 슬라이드가 아니라, 임원이 직접
클릭·질문·조작하며 "우리 회사에서 실제 도는 플랫폼"처럼 느끼게 하는 데모다. 검증된
**Golden Runtime**과 **고정 GitHub Primer Dark Dimmed 계열 soft-dark 디자인**을 재사용하고,
고객별로는 **메뉴(라우트/도메인명)와
데이터만** `demo-spec.json`으로 주입한다. 디자인을 매번 새로 설계하지 않으므로 생성이 빠르다.

## 산출물 (반드시 지킬 것)
- **단일 `.html` 파일** 하나. 인라인 CSS/JS, 외부 빌드 의존성 없음. 한글 폰트만 CDN(Pretendard) + 시스템 폰트 폴백으로 오프라인에서도 동작.
- **Portable session root**: `<session>`은 client가 제공하는 session artifact directory를 우선 사용한다.
  그런 directory가 없으면 저장소와 최종 출력 폴더 밖의 OS temporary directory에 고유한 작업 root를
  만든다. 저장소 안에 session/temp directory를 만들지 않는다.
- **출력 격리**: 고객별 초안·검증 스크립트·스크린샷은 `<session>/<app>-work/`에 두고, 재사용 가능한
  Puppeteer·Chromium은 저장소 밖 공용 캐시에 둔다. 검증이 끝난 요청 산출물 `.html` 하나만 사용자
  출력 위치에 복사한다. 그 밖의 임시 asset은 출력 위치나 저장소에 남기지 않으며, OS temporary
  directory fallback을 사용했다면 작업 완료 후 해당 work directory를 삭제한다.
- **8개 화면 SPA**(해시 라우팅): 대시보드 + 도메인 운영 콘솔 3~4 + AI 에이전트 스튜디오 + 거버넌스(+개발/Copilot).
- **실시간감**: `setInterval` 틱으로 KPI 미세 변동·스트리밍 차트·활동 피드·주기적 토스트·움직이는 객체.
- **인터랙티브**: 버튼/슬라이더/채팅이 실제로 반응. 목록의 **모든 행은 클릭 가능**해야 한다(아래 함정 참고).
- **임원용 한글 우선**: 메뉴·제목·버튼·상태·표·토스트·에이전트 설명처럼 임원이 보는 문구는 자연스러운
  한국어를 기본으로 쓴다. 공식 제품명, 업계 표준 약어·단위, 영어가 더 명확하거나 일반적인 용어만
  영어를 유지한다.
- **정직성**: 모든 화면에 `● 시연 데이터` 배지. 수치는 시연용 가정치임을 명시. 사실 주장은 검증된 것만.

## 입력 파라미터

입력이 부족하면 **한 번에 하나의 focused question만** 묻는다. `ask_user`를 사용할 수 있는 client에서는
해당 도구를 사용하고, 그렇지 않으면 client의 일반 chat UX로 같은 질문을 한다. 자율 모드에서는
합리적으로 가정한 뒤 명시한다.
| 파라미터 | 설명 | 기본/예시 |
|---|---|---|
| `CUSTOMER` | 고객 회사명 | "삼표산업" |
| `INDUSTRY` | 주요 사업/산업 | "레미콘·골재·시멘트" |
| `AUDIENCE` | 청중(임원·직무) | "CIO, 재무팀장, CI팀장" |
| `EMPHASIS` | 강조할 MS·GitHub 서비스 | Foundry, Agent Framework, GitHub Copilot |
| `LANG` | 언어 | 한국어 우선(공식 제품명·일반 약어만 영어 유지) |
| `APP_NAME` | 앱 브랜드명 | `<CUSTOMER> IQ` 권장 |

> CI팀·재무팀처럼 **직무 약어는 의미가 다를 수 있다**(CI=Continuous Improvement vs Corporate Identity).
> 데모 화면이 직무에 맞아야 임팩트가 크므로, 모호하면 직무의 실제 역할을 한 번 확인한다.

### 임원용 문구 원칙

- **한글 우선 대상**: 사이드바 메뉴·짧은 설명, 화면 제목·부제, KPI명, 표 머리글·상태, 버튼, 알림,
  에이전트 이름·역할·답변, 시뮬레이터 설명.
- **영어 유지 대상**: `Microsoft Foundry`, `GitHub Copilot`, `Microsoft Entra ID` 같은 공식 제품명,
  `AI`, `KPI`, `OEE`, `SCM`, `API`, `PR`, `ESS`, `MWh`, `SOC`처럼 업계에서 일반적인 약어·단위,
  코드·Issue·PR 식별자.
- 영어 전문용어가 임원에게 낯설 수 있으면 첫 노출에 한글 뜻을 붙인다. 예:
  `OEE(설비종합효율)`, `SOC(충전율)`.
- 장식용 영어는 쓰지 않는다. 예: `Executive Cockpit`→`경영 현황`, `Overview`→`전체 현황`,
  `Live`→`실시간`, `Simulator`→`예측 시뮬레이션`, `Improvement`→`개선 과제`,
  `Finance`→`재무 효과`, `Agent Studio`→`AI 에이전트`, `Trust & Sovereignty`→`신뢰·데이터 주권`.
- 직역투보다 고객의 경영·사업 언어를 우선한다. 같은 의미를 한글과 영어로 반복 병기하지 않는다.

## 워크플로우

> **순서를 반드시 지킨다: ① 기초 리서치(google-web-search) → ② 스토리라인 구성 → ③ 메뉴·데이터 매핑 → ④ 빌드 → ⑤ 검증.**
> 리서치 없이 바로 HTML을 만들지 않는다. 스토리라인이 확정되기 전에 빌드하지 않는다. 이 순서는 생략·역전 불가.
> **디자인은 GitHub Primer Dark Dimmed 계열 soft-dark로 고정**되어 있으므로 매 요청 새로 설계하지 않는다(고객별로는 메뉴와 데이터만 바꾼다).

### FULL-OPTIMIZED 기본 실행

[FULL-OPTIMIZED 실행 가이드](./reference/full-optimized.md)를 읽고 모든 단계와 합격 기준은 유지하되
다음 방식으로 실행한다.

- 고객 사업·DX/AI·Microsoft/GitHub 최신 정보 조사를 같은 리서치 단계 안에서 병렬화한다.
- 메인 에이전트가 Fact Ledger를 합친 뒤 Storyline·View Contract·Demo Spec을 단독 소유한다(디자인은 고정).
- 공통 HTML/CSS/JS는 `runtime/`의 Golden Runtime을 재사용하고 고객별 spec만 작성한다.
- Puppeteer와 Chromium은 저장소 밖 공용 캐시에서 재사용하고, 없을 때만 설치한다. 설치가 필요하면 **리서치·작성과 병렬로 미리 프리워밍**해 QA 단계 대기를 없앤다.
- 최초와 최종에는 전체 QA를 수행하고, 수정 중에만 영향 route를 증분 검증한다.
- 결함을 한 번에 모아 수정하고 단계별 시간과 캐시 적중 여부를 `metrics.json`에 기록한다.

### 1단계 — 기초 리서치 (⚠️ 필수 · 가장 먼저)
**데모를 만들기 전에 반드시 `google-web-search` 스킬을 호출해 고객·산업 기초자료를 검색·수집한다. 이 단계는 생략 불가이며, 다른 콘텐츠 작업(스토리라인·화면 설계·빌드)보다 먼저 수행한다. 저장소 밖 도구 캐시 확인만 리서치와 병렬 실행할 수 있다.**
1. 입력 파라미터 확정. 부족하면 사용 가능한 경우 `ask_user`, 그렇지 않으면 client의 일반 chat UX로
   **한 번에 하나의 focused question만** 묻는다. 자율 모드에서는 합리적 가정 후 명시한다.
2. **`google-web-search` 스킬로 최소 2~3회 검색**하고, 메인 에이전트가 다음 독립 조사 축을 병렬 tool call로 직접 수행한다:
   - 고객의 주요 사업·제품·브랜드·사업장/생산능력 등 **규모 수치** — 데모 KPI의 현실 범위 근거.
   - 고객의 **디지털 전환·AI·DX 현황과 최근 뉴스/이슈** — 데모를 고객의 *실제 방향*에 정렬(고객이 이미 추진 중인 과제가 있으면 그것을 화면으로).
   - **직무 약어의 실제 의미**(예: PI=Process Innovation, CI=Continuous Improvement) — 모호하면 검색으로 확정. 화면이 직무에 맞아야 임팩트가 크다.
3. **자료조사는 고객 요청마다 실시간으로 새로 수행한다.** 기존 Fact Ledger는 검색어와 출처 후보를 잡는
   참고로만 사용하고, 안정적인 회사 사실도 공식 원문을 다시 확인한다. 이전 조사 결과가 이번 실시간
   조사를 대체하면 안 된다.
4. **Microsoft·GitHub 서비스 최신 확인**: Microsoft Foundry(hosted agents·Foundry IQ·Agent Framework·Toolboxes),
   GitHub Copilot(Copilot cloud agent), 거버넌스(Microsoft Entra ID·Microsoft Purview·Azure AI Content
   Safety·Microsoft Defender·GitHub AI Controls)를 구체 서비스명으로 확인한다. GA/Preview 상태는 공식
   문서에서 해당 기능의 현재 상태를 확인한 경우에만 표시한다. 변동 정보는
   `devblogs.microsoft.com/foundry`·`github.blog`·`learn.microsoft.com`로 확인.
5. 메인 에이전트가 병렬 조사 결과를 하나의 Fact Ledger로 합친다. 이후 모든 화면·KPI·시뮬레이터·채팅·서사는 이 리서치에 근거해야 한다.
> google-web-search 스킬을 도저히 사용할 수 없을 때만 내장 `web_search`/`web_fetch`로 대체하되, **리서치 단계 자체는 절대 건너뛰지 않는다.**

### 2단계 — 스토리라인 구성 (리서치 → 서사)
1단계에서 수집한 사실을 데모의 **이야기(storyline)**로 엮는다. **빌드 전에** 아래 세 가지를 짧게 확정한다:
1. **서사 프레임 한 줄**: 기본 출발점은 Satya Nadella가 2026-06-14 게시한
   *“our priority has to be building a frontier ecosystem, not just a frontier model”*이라는 문구다
   ([공식 게시물](https://x.com/satyanadella/status/2066182223213293753)). 이 문구를 이 skill의
   Human Capital + Token Capital + **Learning Loop**(쓸수록 강해지는 고객 소유의 AI 자산/주권)
   프레임으로 확장한 뒤 **고객 사업 언어**로 번역한다(가능하면 리서치에서 찾은 고객의 실제
   슬로건·전략 방향을 인용).
2. **청중별 핵심 메시지**: `AUDIENCE`의 각 직무가 "바로 관심 가질" 메시지 하나씩(예: CIO=IT 자체역량·거버넌스, 재무팀장=마진·원가, PI팀장=공정개선·원가절감). 각 직무를 어느 화면이 책임지는지 매핑.
3. **화면 흐름(스토리보드)**: 대시보드에서 시작해 도메인 콘솔 → 재무 → 개발 → 에이전트 → 거버넌스로 이어지는 흐름과 **클라이맥스**(보통 멀티에이전트 협업 + 거버넌스/데이터 주권). 각 화면이 리서치의 어떤 사실·과제에 대응하는지 1줄씩 적는다.
> 스토리라인이 고객의 **실제 사업·AI 방향**과 맞아야 임원이 "우리 회사 얘기"로 인지하고 바로 관심을 갖는다. 추상 "AI"가 아니라 리서치로 확인된 고객의 진짜 과제를 화면으로 만든다.
> 리서치·스토리라인·화면 코드는 메인 에이전트가 하나의 맥락으로 직접 통합한다.

### 3단계 — 메뉴·데이터 매핑

디자인은 GitHub Primer Dark Dimmed 계열 soft-dark로 **고정**되어 있다(색·레이아웃·타이포·모션 =
`runtime/` 고정). 이 단계에서는
시각 디자인을 설계하지 않고, **어떤 메뉴(도메인 화면)와 어떤 데이터**를 고객 산업에 맞출지만 정한다.

[화면 청사진](./reference/screen-blueprints.md)을 읽고, `INDUSTRY`를 8개 화면에 매핑한다.
고정 골격 + 산업별 콘텐츠:
- **대시보드**(필수): 전사 실시간 KPI·스트리밍 차트·에이전트 활동 피드·권역/부문 현황.
- **도메인 운영 콘솔 3~4개**(산업별): 그 산업의 핵심 업무를 각각 한 화면으로. 최소 하나는 **실시간 시각화**(맵/흐름), 하나는 **시뮬레이터**(슬라이더→예측), 하나는 **분석/개선**(실행→차트).
- **재무 인사이트**(권장): What-if 슬라이더 → 마진/원가 + 이상탐지.
- **개발 가속**(권장): GitHub Copilot Issue→PR.
- **AI 에이전트 스튜디오**(필수·핵심): 도메인 에이전트 목록 + 채팅 + 멀티에이전트 오케스트레이션.
- **거버넌스**(필수): 고객 소유 평가셋·제도적 기억·데이터 주권 + MS 보안 스택.

각 도메인 화면에는 **그 산업의 진짜 용어/단위**를 쓴다(예: 레미콘=배차·압축강도·슬럼프 /
식음료=배치·수율·폐기·콜드체인 / 제약=배치·편차·CAPA / 헬스케어=병상·대기·재원일 /
금융=여신·연체·이상거래 / 소프트웨어=SLO·배포·Incident / 교육=출석·이수·학습참여 /
보안=SOC·경보·MTTD·MTTR). 매핑 예시는 blueprints 참조.

기본 산업 시작점은 건설소재, 금융, 유통, 물류, 식음료, 제조, 제약·바이오, 헬스케어,
에너지·유틸리티, 소프트웨어·SaaS, 교육·에듀테크, 사이버보안이다. 지원 산업과 Pack 보유 여부는
동일하지 않다. 적합한 Pack이 없으면 관련 없는 Pack을 억지로 쓰지 말고 blueprints를 기준으로 전체
Spec을 직접 작성한다.

빌드 전에 세션 작업 폴더의 `view-contract.md`에 route별 KPI, 필수 DOM ID, 클릭 동작, 시뮬레이터
입력·결과, 에이전트 전환 조건을 확정한다. 이어서
[Composable Spec 계약](./reference/composable-spec.md)에 따라
`customer-overlay.json`을 작성한다. **Overlay는 실시간 research metadata와 고객 `meta`·`story`·핵심
route·Agent(=메뉴와 데이터)만 소유하며, `design`은 넣지 않는다**(디자인은 base가 고정 제공).

### 4단계 — 빌드
1. [Golden Runtime 가이드](./reference/golden-runtime.md),
   [Composable Spec 계약](./reference/composable-spec.md),
   [Demo Spec 계약](./reference/demo-spec.md)을 읽는다.
2. 고객 산업과 가까운 `packs/*.pack.json`을 선택한다. Pack은 산업 terminology·공식·Agent 역할의
   출발점만 제공하며 `meta`, `story`, `design`을 포함할 수 없다.
3. 실시간 조사 결과(메뉴·데이터)를 `customer-overlay.json`에 작성한다. **`design`은 넣지 않는다**(디자인 고정). Pack이 요구하는
   high-impact path(Hero, 운영 flow, simulator, Agent, climax)는 고객 Overlay에서 반드시 새로 쓴다.
4. Composer로 base + Industry Pack + Customer Overlay를 합치고 단일 HTML까지 한 번에 생성한다.
   ```bash
   python3 -B .github/skills/ai-platform-demo/scripts/compose_demo_spec.py \
     --base .github/skills/ai-platform-demo/examples/precision-manufacturing.example.json \
     --pack .github/skills/ai-platform-demo/packs/<industry>.pack.json \
     --customer <session>/<app>-work/customer-overlay.json \
     --output <session>/<app>-work/demo-spec.json \
     --html-output <session>/<app>-work/<app>.html
   ```
5. Composer는 Overlay가 `design`을 정의하거나(디자인은 고정) research metadata가 오래됐거나 Pack의 고객
   필수 path가 빠지면 실패한다. Repository example/test에서만 `--allow-stale-research`를 쓴다.
6. 기본 수정 surface는 HTML이나 전체 Spec이 아니라 `customer-overlay.json`이다. 고객 콘텐츠·
   공식·Agent(메뉴·데이터)를 바꾸면 Overlay를 수정하고 재합성한다.
7. 적합한 Pack이 없으면 전체 `demo-spec.json`을 직접 작성한다.
   **[Authoring cheatsheet](./reference/authoring-cheatsheet.md)**를 따라
   `examples/precision-manufacturing.example.json`을 복사해 **내부 ID는 두고 콘텐츠만 교체**하면 한 번에 유효한 spec이 된다.
   렌더 전에 **먼저 `scripts/lint_spec.py`로 린트**(구조 + QA 불변식, <1초)해 gotcha를 차단한다.
   ```bash
   python3 -B .github/skills/ai-platform-demo/scripts/lint_spec.py <session>/<app>-work/demo-spec.json
   python3 -B .github/skills/ai-platform-demo/scripts/render_demo.py \
     --spec <session>/<app>-work/demo-spec.json \
     --output <session>/<app>-work/<app>.html
   ```
   속도를 위해 맞지 않는 Pack을 억지로 사용하지 않는다.
8. Golden Runtime이 핵심 고객 장면을 충분히 표현하지 못할 때만 해당 route를 session 작업 폴더에서
   bespoke extension한다. 고객 전용 분기를 `runtime/`이나 공용 Pack에 추가하지 않는다.
9. 화면별 코드를 여러 에이전트에 분산하지 않고 메인 에이전트가 Overlay·최종 HTML을 일관되게 소유한다.

### 5단계 — 검증 (필수)
spec은 이미 `scripts/lint_spec.py`(구조 + QA 불변식)를 통과한 상태여야 한다. 이어서
[Verification 가이드](./reference/verification.md)의 puppeteer 절차로:
1. 공용 캐시의 Puppeteer·Chromium을 재사용해 최초 전체 QA를 한 browser/page 세션에서 실행한다.
2. 8개 화면 전부 렌더링 스크린샷 → 레이아웃·겹침·깨짐 점검(이미지 확인).
3. **콘솔/페이지 에러 0건** 확인 + **빠른 라우트 전환 스트레스 테스트**(null 접근·리스너 누수 적발).
4. 메뉴·제목·버튼·상태·표·에이전트 문구를 화면별로 확인해, 불필요한 영어가 남아 있지 않은지 검수한다.
5. 핵심 인터랙션 동작 확인: 슬라이더, 액션 버튼, **모든 에이전트 행 클릭 전환**, 채팅 답변.
6. 발견된 버그를 모두 기록한 뒤 한 번에 수정하고 영향 route를 증분 검증한다.
7. 수정이 있었다면 8개 화면과 모든 핵심 인터랙션을 다시 전체 검증한다.
8. 세션 작업 폴더의 스크립트·스크린샷을 정리하되 공용 도구 캐시는 유지하고, 저장소와 최종 출력 폴더에는 결과 HTML만 남긴다.

## 고객/산업이 바뀔 때 교체하는 것 (재현 핵심)
| 바뀌는 것 | 어디를 바꾸나 |
|---|---|
| 고객명·앱명 | 사이드바 브랜드, 토프바, `APP_NAME`(=`<CUSTOMER> IQ`) |
| 디자인(색·레이아웃·타이포) | **고정** — GitHub Primer Dark Dimmed 계열 soft-dark(`runtime/`). 고객별로 바꾸지 않음 |
| 도메인 화면 3~4개 | blueprints의 산업 매핑으로 운영 콘솔/시뮬레이터/분석 내용 교체 |
| 에이전트 구성 | 산업 도메인 에이전트로 목록·프로필·추천질문·답변 교체 |
| KPI·시뮬레이터 공식 | 산업 단위(㎥/건/원/%)·현실적 범위로 |
| 채팅 시나리오 | 산업 질문·답변으로 |
| 서사 프레임 한 줄 | Learning Loop를 고객 사업 언어로 번역 |
| 고정 유지 | Golden Runtime의 route lifecycle·interaction engine·QA hook + GitHub soft-dark 디자인 |

## 흔한 함정 (이전 빌드에서 실제로 겪은 것)
- **목록 행에 클릭 핸들러 누락**: 에이전트/항목 목록을 렌더만 하고 `onclick`을 안 달면 "첫 항목만 동작"하는 것처럼 보인다. 모든 클릭 가능한 행에 핸들러 필수.
- **비동기 콜백의 null 접근**: 라우트 전환 후 실행되는 `setTimeout`/체인에서 `$('#id')`가 null일 수 있다. 자동 실행 타이머는 `addTimer` 등록 + 존재 체크(`const el=$('#x'); if(!el)return;`).
- **리스너 누적**: 뷰마다 `addEventListener('resize',…)`를 달면 재방문 시 누적. `addCleanup(()=>removeEventListener(...))`로 해제.
- **인라인 style이 CSS 트랜지션을 덮음**: SVG `stroke-dashoffset` 등은 인라인으로 직접 0 설정해 애니메이션.
- **가상 인물명**: 데모에 실명/특정 가상 인물명을 넣지 말 것. 직무/회사명만("○○ 임원", `<CUSTOMER>`).
- **불필요한 영어**: 공식 제품명·일반 약어·단위가 아닌 영어 메뉴, 상태, 버튼, 설명을 그대로 두지 않는다.
- **과장**: 추상 "AI"가 아니라 구체 서비스로 가치 매핑. 데모 수치는 `시연 데이터`로 정직하게.

## 참고 파일 (필요할 때 읽기)
- [Golden Runtime 가이드](./reference/golden-runtime.md) — 고정 Runtime과 고객별 Spec의 경계, extension 규칙.
- [고정 디자인 DNA](./reference/fixed-design-dna.md) — **고정** GitHub Primer Dark Dimmed 계열 soft-dark 디자인 시스템 설명(고객별로 바꾸지 않음).
- [Composable Spec 계약](./reference/composable-spec.md) — Base + Industry Pack + Customer Overlay 합성 계약.
- [Demo Spec 계약](./reference/demo-spec.md) — Renderer가 읽는 고객별 machine-readable build contract.
- [Authoring cheatsheet](./reference/authoring-cheatsheet.md) — 전체 spec 직접 작성 시 개수·ID연동·tone·rich-text·QA 불변식 압축표.
- Golden Runtime assets: [shell template](./runtime/shell.tmpl), [CSS](./runtime/runtime.css),
  [JavaScript](./runtime/runtime.js). 고객 전용 내용을 직접 넣지 않는다.
- [Renewable Energy Industry Pack](./packs/renewable-energy-holdings.pack.json) — 디자인·고객 사실을 포함하지 않는 Pack 구조 예제.
- [Composer](./scripts/compose_demo_spec.py) — layer merge·live research·design 고정 검사·Spec/HTML 동시 생성.
- [Renderer](./scripts/render_demo.py) — spec validation + 단일 HTML inline Renderer.
- [Spec linter](./scripts/lint_spec.py) — 렌더 전 pre-QA 린트(구조 + QA 불변식, <1초).
- [Browser verifier](./scripts/verify_demo.js) — 8-route interaction·console·screenshot QA.
- [Customer Overlay 예제](./examples/renewable-energy.customer-overlay.example.json) — compact 고객 Overlay 구조 예제.
- [전체 Spec 예제](./examples/precision-manufacturing.example.json) — 구조 예제. 고객 콘텐츠 복제 금지.
- [Demo Spec JSON Schema](./schema/demo-spec.schema.json) — machine-readable Spec shape와 고정 디자인 marker.
- [디자인 시스템](./reference/design-system.md) — 고정 soft-dark CSS 변수·타이포·컴포넌트.
- [App shell](./reference/app-shell.md) — 앱 셸 HTML·해시 라우터·전역/뷰 타이머·차트 유틸·VIEWS 패턴.
- [화면 청사진](./reference/screen-blueprints.md) — 8종 화면 청사진 + 산업별 매핑 표/예시.
- [Verification 가이드](./reference/verification.md) — puppeteer 스크린샷·콘솔 에러·스트레스 테스트·정리.
- [FULL-OPTIMIZED 가이드](./reference/full-optimized.md) — 단계 유지형 병렬 조사·공용 캐시·증분/최종 전체 QA·시간 측정.
