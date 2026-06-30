---
name: ai-platform-demo
description: "특정 고객·산업을 위한 '실제로 동작하는' AI 운영 플랫폼 데모를 단일 HTML(SaaS 앱) 하나로 생성합니다. 사이드바·실시간 대시보드·도메인별 운영 콘솔·AI 에이전트 채팅·거버넌스를 갖춘 임원 보고/영업 데모. 고객 이름과 주요 사업이 바뀌어도 동일 품질로 재현됩니다. Microsoft Foundry·Agent Framework·GitHub Copilot 가치를 고객 사업에 매핑. WHEN: 고객 AI 데모, 임원 데모, 회장 보고 데모, executive demo, AI 플랫폼 데모, AI platform demo, SaaS 데모, 운영 대시보드 데모, operations dashboard demo, 산업 AI 데모, industry AI demo, Foundry/Copilot 데모, 고객사 맞춤 데모, 인터랙티브 데모 HTML, single-file HTML app demo, AI 에이전트 데모, agent studio demo."
argument-hint: "고객 이름과 주요 사업(산업)을 알려주세요 — 예: '삼표산업, 레미콘·골재·시멘트' 또는 'OO은행, 리테일 뱅킹'"
---

# AI 플랫폼 데모 생성기 (Customer AI Platform Demo)

특정 고객을 위한 **실제로 동작하는 단일 HTML SaaS 앱**을 만든다. 슬라이드가 아니라, 임원이 직접
클릭·질문·조작하며 "우리 회사에서 실제 도는 플랫폼"처럼 느끼게 하는 데모다. 고객 이름·산업·강조
서비스가 바뀌어도 이 스킬로 동일한 완성도를 재현한다.

## 산출물 (반드시 지킬 것)
- **단일 `.html` 파일** 하나. 인라인 CSS/JS, 외부 빌드 의존성 없음. 한글 폰트만 CDN(Pretendard) + 시스템 폰트 폴백으로 오프라인에서도 동작.
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
| `BRAND` | 브랜드 포인트 컬러(있으면) | 고객 로고 색 / 없으면 레드+블루 |
| `EMPHASIS` | 강조할 MS·GitHub 서비스 | Foundry, Agent Framework, GitHub Copilot |
| `LANG` | 언어 | 한국어(용어 영문 병기) |
| `APP_NAME` | 앱 브랜드명 | `<CUSTOMER> IQ` 권장 |

> CI팀·재무팀처럼 **직무 약어는 의미가 다를 수 있다**(CI=Continuous Improvement vs Corporate Identity).
> 데모 화면이 직무에 맞아야 임팩트가 크므로, 모호하면 직무의 실제 역할을 한 번 확인한다.

## 워크플로우

### 1단계 — 인테이크 & 리서치
1. 입력 파라미터 확정(부족하면 질문 또는 가정 명시).
2. **고객·산업 사실 수집**: `google-web-search` 스킬로 고객의 주요 사업·제품·디지털 현황·최근 이슈를 조사.
   숫자/브랜드/제품명은 데모의 현실감을 좌우하므로 1차 출처로 확인.
3. **Microsoft·GitHub 서비스 최신 확인**: Foundry(Hosted Agents·Foundry IQ·Agent Framework·Toolboxes),
   GitHub Copilot(Agent/Coding Agent), 거버넌스(Entra·Purview·Content Safety·Defender·ASSERT/ACS)를
   구체 서비스명으로. (변동 정보는 `devblogs.microsoft.com/foundry`, `github.blog`, `learn.microsoft.com` 확인.)
4. **서사 프레임 선택**: 기본 프레임은 Satya Nadella의 *"Frontier Ecosystem, not just a Frontier Model"* —
   Human Capital + Token Capital + **Learning Loop**(쓸수록 강해지는 고객 소유의 AI 자산/주권). 고객 산업에 맞춰 한 문장으로 번역.

### 2단계 — 화면 설계 (산업 매핑)
`reference/screen-blueprints.md`를 읽고, `INDUSTRY`를 8개 화면에 매핑한다. 고정 골격 + 산업별 콘텐츠:
- **대시보드**(필수): 전사 실시간 KPI·스트리밍 차트·에이전트 활동 피드·권역/부문 현황.
- **도메인 운영 콘솔 3~4개**(산업별): 그 산업의 핵심 업무를 각각 한 화면으로. 최소 하나는 **실시간 시각화**(맵/흐름), 하나는 **시뮬레이터**(슬라이더→예측), 하나는 **분석/개선**(실행→차트).
- **재무 인사이트**(권장): What-if 슬라이더 → 마진/원가 + 이상탐지.
- **개발 가속**(권장): GitHub Copilot Issue→PR.
- **AI 에이전트 스튜디오**(필수·핵심): 도메인 에이전트 목록 + 채팅 + 멀티에이전트 오케스트레이션.
- **거버넌스**(필수): 고객 소유 평가셋·제도적 기억·데이터 주권 + MS 보안 스택.

각 도메인 화면에는 **그 산업의 진짜 용어/단위**를 쓴다(예: 레미콘=배차·압축강도·슬럼프 / 은행=여신·연체·이상거래 / 물류=적재율·리드타임). 매핑 예시는 blueprints 참조.

### 3단계 — 빌드
1. `reference/design-system.md`(디자인 토큰+컴포넌트 CSS)와 `reference/app-shell.md`(앱 셸·라우터·실시간 유틸·VIEWS 패턴)를 **그대로 토대로** 단일 HTML을 구성한다. 브랜드 컬러/이름만 치환.
2. 각 화면은 `VIEWS.<id> = () => ({ html, init })` 패턴으로 작성. `init`의 타이머는 **반드시 `addTimer`**, 리스너/구독은 **`addCleanup`**으로 등록(라우트 전환 시 정리).
3. 차트/게이지/도넛/맵은 순수 SVG로 직접 그린다(외부 차트 라이브러리 금지 — 오프라인 안정성).
4. AI 에이전트 스튜디오는 `reference/screen-blueprints.md`의 패턴을 따른다. **에이전트별 프로필(아이콘·이름·소개·전용 추천질문 3개·도메인 답변)**을 만들고, 목록의 각 행에 `onclick`으로 `selectAgent(i)` 연결(헤더·아바타·인사·추천질문·답변 모두 전환).

### 4단계 — 검증 (필수)
`reference/verification.md`의 puppeteer 절차로:
1. 8개 화면 전부 렌더링 스크린샷 → 레이아웃·겹침·깨짐 점검(이미지 확인).
2. **콘솔/페이지 에러 0건** 확인 + **빠른 라우트 전환 스트레스 테스트**(null 접근·리스너 누수 적발).
3. 핵심 인터랙션 동작 확인: 슬라이더, 액션 버튼, **모든 에이전트 행 클릭 전환**, 채팅 답변.
4. 발견된 버그 수정 후 재검증. 끝나면 **검증 부산물(node_modules·스크립트·스크린샷) 정리**, 결과 HTML만 남긴다.

## 고객/산업이 바뀔 때 교체하는 것 (재현 핵심)
| 바뀌는 것 | 어디를 바꾸나 |
|---|---|
| 고객명·앱명 | 사이드바 브랜드, 토프바, `APP_NAME`(=`<CUSTOMER> IQ`) |
| 브랜드 컬러 | `:root`의 `--brand`(레드 계열) — 토큰 1곳 |
| 도메인 화면 3~4개 | blueprints의 산업 매핑으로 운영 콘솔/시뮬레이터/분석 내용 교체 |
| 에이전트 구성 | 산업 도메인 에이전트로 목록·프로필·추천질문·답변 교체 |
| KPI·시뮬레이터 공식 | 산업 단위(㎥/건/원/%)·현실적 범위로 |
| 채팅 시나리오 | 산업 질문·답변으로 |
| 서사 프레임 한 줄 | Learning Loop를 고객 사업 언어로 번역 |
| 고정 유지 | 앱 셸·라우터·실시간 틱·디자인 토큰·컴포넌트·거버넌스 골격 |

## 흔한 함정 (이전 빌드에서 실제로 겪은 것)
- **목록 행에 클릭 핸들러 누락**: 에이전트/항목 목록을 렌더만 하고 `onclick`을 안 달면 "첫 항목만 동작"하는 것처럼 보인다. 모든 클릭 가능한 행에 핸들러 필수.
- **비동기 콜백의 null 접근**: 라우트 전환 후 실행되는 `setTimeout`/체인에서 `$('#id')`가 null일 수 있다. 자동 실행 타이머는 `addTimer` 등록 + 존재 체크(`const el=$('#x'); if(!el)return;`).
- **리스너 누적**: 뷰마다 `addEventListener('resize',…)`를 달면 재방문 시 누적. `addCleanup(()=>removeEventListener(...))`로 해제.
- **인라인 style이 CSS 트랜지션을 덮음**: SVG `stroke-dashoffset` 등은 인라인으로 직접 0 설정해 애니메이션.
- **가상 인물명**: 데모에 실명/특정 가상 인물명을 넣지 말 것. 직무/회사명만("○○ 임원", `<CUSTOMER>`).
- **과장**: 추상 "AI"가 아니라 구체 서비스로 가치 매핑. 데모 수치는 `DEMO DATA`로 정직하게.

## 참고 파일 (필요할 때 읽기)
- `reference/design-system.md` — CSS 변수·타이포·컴포넌트(검증된 자산, 거의 그대로 사용).
- `reference/app-shell.md` — 앱 셸 HTML·해시 라우터·전역/뷰 타이머·차트 유틸·VIEWS 패턴.
- `reference/screen-blueprints.md` — 8종 화면 청사진 + 산업별 매핑 표/예시.
- `reference/verification.md` — puppeteer 스크린샷·콘솔 에러·스트레스 테스트·정리.
