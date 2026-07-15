---
name: ai-platform-demo
description: "특정 고객·산업을 위한 '실제로 동작하는' AI 운영 플랫폼 데모를 Golden Runtime + Adaptive Design DNA 방식의 단일 HTML(SaaS 앱)로 생성합니다. 사이드바·실시간 대시보드·도메인별 운영 콘솔·AI 에이전트 채팅·거버넌스를 갖춘 임원 보고/영업 데모. 고객 이름과 주요 사업이 바뀌어도 동작 품질은 재사용하고 색상·밀도·형태·스토리는 고객별로 적응합니다. Microsoft Foundry·Agent Framework·GitHub Copilot 가치를 고객 사업에 매핑. WHEN: 고객 AI 데모, 임원 데모, 회장 보고 데모, executive demo, AI 플랫폼 데모, AI platform demo, SaaS 데모, 운영 대시보드 데모, operations dashboard demo, 산업 AI 데모, industry AI demo, Foundry/Copilot 데모, 고객사 맞춤 데모, 인터랙티브 데모 HTML, single-file HTML app demo, AI 에이전트 데모, agent studio demo."
argument-hint: "고객 이름과 주요 사업(산업)을 알려주세요 — 예: '삼표산업, 레미콘·골재·시멘트' 또는 'OO은행, 리테일 뱅킹'"
---

# AI 플랫폼 데모 생성기 (Customer AI Platform Demo)

특정 고객을 위한 **실제로 동작하는 단일 HTML SaaS 앱**을 만든다. 슬라이드가 아니라, 임원이 직접
클릭·질문·조작하며 "우리 회사에서 실제 도는 플랫폼"처럼 느끼게 하는 데모다. 검증된
**Golden Runtime**은 동작·안전·QA 계약만 재사용하고, 고객별 **Adaptive Design DNA**와 산업 콘텐츠를
`demo-spec.json`으로 주입해 속도와 차별성을 함께 유지한다.

## 산출물 (반드시 지킬 것)
- **단일 `.html` 파일** 하나. 인라인 CSS/JS, 외부 빌드 의존성 없음. 한글 폰트만 CDN(Pretendard) + 시스템 폰트 폴백으로 오프라인에서도 동작.
- **출력 격리**: 고객별 초안·검증 스크립트·스크린샷은 `<session>/files/<app>-work/`에 두고, 재사용 가능한 Puppeteer·Chromium은 저장소 밖 공용 캐시에 둔다. 검증이 끝난 최종 `.html` 하나만 사용자 출력 위치에 복사한다.
- **8개 화면 SPA**(해시 라우팅): 대시보드 + 도메인 운영 콘솔 3~4 + AI 에이전트 스튜디오 + 거버넌스(+개발/Copilot).
- **실시간감**: `setInterval` 틱으로 KPI 미세 변동·스트리밍 차트·활동 피드·주기적 토스트·움직이는 객체.
- **인터랙티브**: 버튼/슬라이더/채팅이 실제로 반응. 목록의 **모든 행은 클릭 가능**해야 한다(아래 함정 참고).
- **정직성**: 모든 화면에 `● DEMO DATA` 배지. 수치는 시연용 가정치임을 명시. 사실 주장은 검증된 것만.

## 입력 파라미터 (없으면 1개씩 `ask_user`로 질문, 자율 모드면 합리적 가정 후 명시)
| 파라미터 | 설명 | 기본/예시 |
|---|---|---|
| `CUSTOMER` | 고객 회사명 | "삼표산업" |
| `INDUSTRY` | 주요 사업/산업 | "레미콘·골재·시멘트" |
| `AUDIENCE` | 청중(임원·직무) | "CIO, 재무팀장, CI팀장" |
| `BRAND` | 공식 브랜드 색·시각 자산(있으면) | 없으면 산업·청중에서 palette role 도출 |
| `DESIGN_DNA` | archetype·theme·density·shape·chart grammar | 고객 브랜드·산업·청중에서 도출 |
| `EMPHASIS` | 강조할 MS·GitHub 서비스 | Foundry, Agent Framework, GitHub Copilot |
| `LANG` | 언어 | 한국어(용어 영문 병기) |
| `APP_NAME` | 앱 브랜드명 | `<CUSTOMER> IQ` 권장 |

> CI팀·재무팀처럼 **직무 약어는 의미가 다를 수 있다**(CI=Continuous Improvement vs Corporate Identity).
> 데모 화면이 직무에 맞아야 임팩트가 크므로, 모호하면 직무의 실제 역할을 한 번 확인한다.

## 워크플로우

> **순서를 반드시 지킨다: ① 기초 리서치(google-web-search) → ② 스토리라인 구성 → ③ Design DNA·화면 설계 → ④ 빌드 → ⑤ 검증.**
> 리서치 없이 바로 HTML을 만들지 않는다. 스토리라인이 확정되기 전에 빌드하지 않는다. 이 순서는 생략·역전 불가.

### FULL-OPTIMIZED 기본 실행

`reference/full-optimized.md`를 읽고 모든 단계와 합격 기준은 유지하되 다음 방식으로 실행한다.

- 고객 사업·DX/AI·Microsoft/GitHub 최신 정보 조사를 같은 리서치 단계 안에서 병렬화한다.
- 메인 에이전트가 Fact Ledger를 합친 뒤 Storyline·Design DNA·View Contract·Demo Spec을 단독 소유한다.
- 공통 HTML/CSS/JS는 `runtime/`의 Golden Runtime을 재사용하고 고객별 spec만 작성한다.
- Puppeteer와 Chromium은 저장소 밖 공용 캐시에서 재사용하고, 없을 때만 설치한다.
- 최초와 최종에는 전체 QA를 수행하고, 수정 중에만 영향 route를 증분 검증한다.
- 결함을 한 번에 모아 수정하고 단계별 시간과 캐시 적중 여부를 `metrics.json`에 기록한다.

### 1단계 — 기초 리서치 (⚠️ 필수 · 가장 먼저)
**데모를 만들기 전에 반드시 `google-web-search` 스킬을 호출해 고객·산업 기초자료를 검색·수집한다. 이 단계는 생략 불가이며, 다른 콘텐츠 작업(스토리라인·화면 설계·빌드)보다 먼저 수행한다. 저장소 밖 도구 캐시 확인만 리서치와 병렬 실행할 수 있다.**
1. 입력 파라미터 확정(부족하면 `ask_user`로 질문하거나 합리적 가정 후 명시).
2. **`google-web-search` 스킬로 최소 2~3회 검색**하되, 다음 독립 조사 축은 `/fleet` 또는 병렬 tool call로 동시에 수행할 수 있다:
   - 고객의 주요 사업·제품·브랜드·사업장/생산능력 등 **규모 수치** — 데모 KPI의 현실 범위 근거.
   - 고객의 **디지털 전환·AI·DX 현황과 최근 뉴스/이슈** — 데모를 고객의 *실제 방향*에 정렬(고객이 이미 추진 중인 과제가 있으면 그것을 화면으로).
   - **직무 약어의 실제 의미**(예: PI=Process Innovation, CI=Continuous Improvement) — 모호하면 검색으로 확정. 화면이 직무에 맞아야 임팩트가 크다.
3. 기존 Fact Ledger가 있으면 안정적인 회사 사실은 출처를 재확인하고, 최근 뉴스·제품 상태는 새로 조사한다.
4. **Microsoft·GitHub 서비스 최신 확인**: Foundry(Hosted Agents·Foundry IQ·Agent Framework·Toolboxes), GitHub Copilot(Agent/Coding Agent), 거버넌스(Entra·Purview·Content Safety·Defender·ASSERT/ACS)를 구체 서비스명으로. 변동 정보는 `devblogs.microsoft.com/foundry`·`github.blog`·`learn.microsoft.com`로 확인.
5. 메인 에이전트가 병렬 조사 결과를 하나의 Fact Ledger로 합친다. 이후 모든 화면·KPI·시뮬레이터·채팅·서사는 이 리서치에 근거해야 한다.
> google-web-search 스킬을 도저히 사용할 수 없을 때만 내장 `web_search`/`web_fetch`로 대체하되, **리서치 단계 자체는 절대 건너뛰지 않는다.**

### 2단계 — 스토리라인 구성 (리서치 → 서사)
1단계에서 수집한 사실을 데모의 **이야기(storyline)**로 엮는다. **빌드 전에** 아래 세 가지를 짧게 확정한다:
1. **서사 프레임 한 줄**: 기본은 Satya Nadella의 *"Frontier Ecosystem, not just a Frontier Model"* — Human Capital + Token Capital + **Learning Loop**(쓸수록 강해지는 고객 소유의 AI 자산/주권). 이를 **고객 사업 언어**로 번역(가능하면 리서치에서 찾은 고객의 실제 슬로건·전략 방향을 인용).
2. **청중별 핵심 메시지**: `AUDIENCE`의 각 직무가 "바로 관심 가질" 메시지 하나씩(예: CIO=IT 자체역량·거버넌스, 재무팀장=마진·원가, PI팀장=공정개선·원가절감). 각 직무를 어느 화면이 책임지는지 매핑.
3. **화면 흐름(스토리보드)**: 대시보드에서 시작해 도메인 콘솔 → 재무 → 개발 → 에이전트 → 거버넌스로 이어지는 흐름과 **클라이맥스**(보통 멀티에이전트 협업 + 거버넌스/데이터 주권). 각 화면이 리서치의 어떤 사실·과제에 대응하는지 1줄씩 적는다.
> 스토리라인이 고객의 **실제 사업·AI 방향**과 맞아야 임원이 "우리 회사 얘기"로 인지하고 바로 관심을 갖는다. 추상 "AI"가 아니라 리서치로 확인된 고객의 진짜 과제를 화면으로 만든다.
> 조사 subagent는 스토리라인이나 화면 코드를 작성하지 않는다. 메인 에이전트가 하나의 서사로 통합한다.

### 3단계 — Adaptive Design DNA + 화면 설계

`reference/adaptive-design-dna.md`를 읽고 고객별 시각 계약을 먼저 확정한다.

- concept words 3개, visual metaphor, archetype, counter-influence
- dark/light theme, density, motion
- palette role, typography scale, radius·line·shadow, chart grammar
- 이번 고객에게 사용하지 않을 `avoid` 3개

Golden Runtime이 제공하는 archetype은 시작점일 뿐이며 고객 token이 우선한다. 모든 고객을 같은 dark
dashboard나 같은 브랜드 색 치환 결과로 만들지 않는다.

`reference/screen-blueprints.md`를 읽고, `INDUSTRY`를 8개 화면에 매핑한다. 고정 골격 + 산업별 콘텐츠:
- **대시보드**(필수): 전사 실시간 KPI·스트리밍 차트·에이전트 활동 피드·권역/부문 현황.
- **도메인 운영 콘솔 3~4개**(산업별): 그 산업의 핵심 업무를 각각 한 화면으로. 최소 하나는 **실시간 시각화**(맵/흐름), 하나는 **시뮬레이터**(슬라이더→예측), 하나는 **분석/개선**(실행→차트).
- **재무 인사이트**(권장): What-if 슬라이더 → 마진/원가 + 이상탐지.
- **개발 가속**(권장): GitHub Copilot Issue→PR.
- **AI 에이전트 스튜디오**(필수·핵심): 도메인 에이전트 목록 + 채팅 + 멀티에이전트 오케스트레이션.
- **거버넌스**(필수): 고객 소유 평가셋·제도적 기억·데이터 주권 + MS 보안 스택.

각 도메인 화면에는 **그 산업의 진짜 용어/단위**를 쓴다(예: 레미콘=배차·압축강도·슬럼프 / 은행=여신·연체·이상거래 / 물류=적재율·리드타임). 매핑 예시는 blueprints 참조.

빌드 전에 세션 작업 폴더의 `view-contract.md`에 route별 KPI, 필수 DOM ID, 클릭 동작, 시뮬레이터
입력·결과, 에이전트 전환 조건을 확정한다. 이어서 `reference/demo-spec.md`에 따라
`demo-spec.json`을 작성한다. Spec은 Fact Ledger·Storyline·Design DNA·View Contract를 하나의
machine-readable build contract로 합친다.

### 4단계 — 빌드
1. `reference/golden-runtime.md`, `reference/adaptive-design-dna.md`, `reference/demo-spec.md`를 읽는다.
2. `examples/precision-manufacturing.example.json`을 구조 참고용으로만 사용하고 고객의 `demo-spec.json`을 새로 작성한다. 예제의 고객명·문구·색을 복제하지 않는다.
3. Renderer로 Golden Runtime과 고객 spec을 합쳐 단일 HTML을 생성한다.
   ```bash
   python3 -B .github/skills/ai-platform-demo/scripts/render_demo.py \
     --spec <session>/files/<app>-work/demo-spec.json \
     --output <session>/files/<app>-work/<app>.html
   ```
4. 기본 수정 surface는 HTML이 아니라 `demo-spec.json`이다. 콘텐츠·색상·공식·Agent를 바꾸면 spec을 수정하고 재생성한다.
5. Golden Runtime이 핵심 고객 장면을 충분히 표현하지 못할 때만 해당 route를 session 작업 폴더에서 bespoke extension한다. 고객 전용 분기를 `runtime/`에 추가하지 않는다.
6. Runtime 내부의 모든 타이머·listener·SVG·agent 행 click·escaping·QA ID는 고정 계약으로 유지한다.
7. 화면별 코드를 여러 에이전트에 분산하지 않고 메인 에이전트가 Design DNA·Spec·최종 HTML을 일관되게 소유한다.

### 5단계 — 검증 (필수)
`reference/verification.md`의 puppeteer 절차로:
1. 공용 캐시의 Puppeteer·Chromium을 재사용해 최초 전체 QA를 한 browser/page 세션에서 실행한다.
2. 8개 화면 전부 렌더링 스크린샷 → 레이아웃·겹침·깨짐 점검(이미지 확인).
3. **콘솔/페이지 에러 0건** 확인 + **빠른 라우트 전환 스트레스 테스트**(null 접근·리스너 누수 적발).
4. 핵심 인터랙션 동작 확인: 슬라이더, 액션 버튼, **모든 에이전트 행 클릭 전환**, 채팅 답변.
5. 발견된 버그를 모두 기록한 뒤 한 번에 수정하고 영향 route를 증분 검증한다.
6. 수정이 있었다면 8개 화면과 모든 핵심 인터랙션을 다시 전체 검증한다.
7. 세션 작업 폴더의 스크립트·스크린샷을 정리하되 공용 도구 캐시는 유지하고, 저장소와 최종 출력 폴더에는 결과 HTML만 남긴다.

## 고객/산업이 바뀔 때 교체하는 것 (재현 핵심)
| 바뀌는 것 | 어디를 바꾸나 |
|---|---|
| 고객명·앱명 | 사이드바 브랜드, 토프바, `APP_NAME`(=`<CUSTOMER> IQ`) |
| Design DNA | `design.archetype/theme/density/tokens/avoid` |
| 브랜드 컬러 | `design.tokens`의 palette role — brand 하나만 바꾸지 않음 |
| 도메인 화면 3~4개 | blueprints의 산업 매핑으로 운영 콘솔/시뮬레이터/분석 내용 교체 |
| 에이전트 구성 | 산업 도메인 에이전트로 목록·프로필·추천질문·답변 교체 |
| KPI·시뮬레이터 공식 | 산업 단위(㎥/건/원/%)·현실적 범위로 |
| 채팅 시나리오 | 산업 질문·답변으로 |
| 서사 프레임 한 줄 | Learning Loop를 고객 사업 언어로 번역 |
| 고정 유지 | Golden Runtime의 route lifecycle·interaction engine·QA hook |

## 흔한 함정 (이전 빌드에서 실제로 겪은 것)
- **목록 행에 클릭 핸들러 누락**: 에이전트/항목 목록을 렌더만 하고 `onclick`을 안 달면 "첫 항목만 동작"하는 것처럼 보인다. 모든 클릭 가능한 행에 핸들러 필수.
- **비동기 콜백의 null 접근**: 라우트 전환 후 실행되는 `setTimeout`/체인에서 `$('#id')`가 null일 수 있다. 자동 실행 타이머는 `addTimer` 등록 + 존재 체크(`const el=$('#x'); if(!el)return;`).
- **리스너 누적**: 뷰마다 `addEventListener('resize',…)`를 달면 재방문 시 누적. `addCleanup(()=>removeEventListener(...))`로 해제.
- **인라인 style이 CSS 트랜지션을 덮음**: SVG `stroke-dashoffset` 등은 인라인으로 직접 0 설정해 애니메이션.
- **가상 인물명**: 데모에 실명/특정 가상 인물명을 넣지 말 것. 직무/회사명만("○○ 임원", `<CUSTOMER>`).
- **과장**: 추상 "AI"가 아니라 구체 서비스로 가치 매핑. 데모 수치는 `DEMO DATA`로 정직하게.

## 참고 파일 (필요할 때 읽기)
- `reference/golden-runtime.md` — 고정 Runtime과 고객별 Spec의 경계, extension 규칙.
- `reference/adaptive-design-dna.md` — 고객별 archetype·palette·density·shape·chart 계약.
- `reference/demo-spec.md` — Renderer가 읽는 고객별 machine-readable build contract.
- `runtime/` — 검증된 shell·CSS·JavaScript Runtime. 고객 전용 내용을 직접 넣지 않는다.
- `scripts/render_demo.py` — spec validation + 단일 HTML inline Renderer.
- `examples/precision-manufacturing.example.json` — 구조 예제. 고객 콘텐츠 복제 금지.
- `reference/design-system.md` — CSS 변수·타이포·컴포넌트(검증된 자산, 거의 그대로 사용).
- `reference/app-shell.md` — 앱 셸 HTML·해시 라우터·전역/뷰 타이머·차트 유틸·VIEWS 패턴.
- `reference/screen-blueprints.md` — 8종 화면 청사진 + 산업별 매핑 표/예시.
- `reference/verification.md` — puppeteer 스크린샷·콘솔 에러·스트레스 테스트·정리.
- `reference/full-optimized.md` — 단계 유지형 병렬 조사·공용 캐시·증분/최종 전체 QA·시간 측정.
