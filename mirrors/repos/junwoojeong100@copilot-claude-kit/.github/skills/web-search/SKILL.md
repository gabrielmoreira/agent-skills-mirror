---
name: web-search
description: "최신 정보와 기초자료가 필요할 때 전용 웹 검색 도구와 공식 문서 검색을 우선하고, 접근 가능한 공식 원문으로 사실을 검증해 구조화한 뒤 결론부터 Straightforward하게 요약합니다. 공개 검색 결과 페이지를 직접 scraping하지 않습니다. 학습 데이터 이후의 뉴스·기술 업데이트·기업·시장·산업·규제 자료 등. WHEN: 최신 정보 검색, 실시간 검색, Google 검색, web search, 기초자료 조사, 자료 검색/수집, 고객/기업 조사, 시장 규모, 산업 리서치, 최신 뉴스, latest news, 최근 업데이트, 릴리스 노트, release notes, changelog, 최신 버전, 현재 가격, current price, 현재 상태, what's new, 오늘/최근 연도 정보, 최신 트렌드, 기술·시장·산업 동향, 전략 리포트, 공식 발표, 최신 문서, AI 규제 동향, EU AI Act, GDPR, 개인정보보호법, 컴플라이언스, ISO 27001, NIST, 클라우드·AI 도입 사례."
argument-hint: "검색하고 싶은 주제나 질문을 입력하세요"
---

# 실시간 웹 검색 (도구 우선 · 원문 검증)

Google·DuckDuckGo·Bing의 공개 검색 결과 페이지(SERP)를 `curl`, 일반 page fetch, headless browser로
직접 조회하지 않는다.

## Straightforward 출력 원칙
- 검색 과정이 아니라 **사용자가 바로 쓸 결론**을 먼저 1~3문장으로 제시한다.
- 단순한 사실 질문은 단순하게 답하고, 검색어·탐색 일지·불필요한 배경 설명을 노출하지 않는다.
- 상세 내용은 결론의 근거·조건·예외를 이해하는 데 필요한 만큼만 붙인다. 확실한 사실, 조건부 사실,
  확인하지 못한 내용을 분리한다.
- 출처는 주장 바로 뒤 또는 마지막 `### 출처`에 원문 중심으로 제공한다. 출처 수를 늘리기보다 핵심 주장과
  직접 연결되는 1차 출처를 우선한다.

## 실행 전 capability 확인
- 이 스킬은 GitHub Copilot CLI와 VS Code Copilot Chat/Agent에서만 사용한다.
- 스킬은 검색 전략을 제공할 뿐 검색 backend를 생성하지 않는다. 먼저 GitHub Copilot이 현재 세션에
  제공하는 도구를 확인한다.
- 범용 최신 검색에는 Copilot이 제공하는 `web_search` 또는 web source를 지원하는 Research agent가 필요하다.
  Copilot CLI에서는 `/research` 또는 내부 Research subagent가 이 역할을 수행할 수 있다.
- Microsoft Learn MCP·GitHub search처럼 범위가 제한된 도구만 있으면 해당 도메인만 최신 검증할 수 있다.
  이를 범용 웹 검색 성공으로 간주하지 않는다.
- Copilot의 범용 검색 capability가 없고 공식 URL도 모르면 공개 SERP를 직접 조회하지 않는다. 사용자가
  출발 URL을 제공해야 함을 먼저 알리고, 현재 지식만으로 최신 사실을 만들지 않는다.

## 절차
1. **조사 범위 확정**:
   - 단순 사실 질문은 바로 검색한다. 기초자료 조사·자료 수집·복합 리서치는 검색 전에 목적, 대상 독자,
     지역, 기간, 필수 조사 축, 원하는 산출물을 짧은 Research Brief로 확정한다.
   - 조사 축은 서로 독립적으로 검증 가능하게 나누고, 누락된 입력이 결론을 바꾸는 경우에만 한 번에 하나씩
     확인한다. 자율 실행 환경에서는 합리적인 범위를 정하고 결과에 가정을 표시한다.
2. **쿼리 설계**: 질문을 독립 검증 가능한 주장으로 나누고, 출처가 쓰는 언어의 구체 용어를 사용한다.
   최신성이 중요한 주장에만 현재 연도·날짜 범위를 넣고, 사용자가 지정한 도메인과 공식 도메인을 우선한다.
3. **소스(동적, 고정 화이트리스트 아님)**: 주제별 가장 권위 있는 1차 출처를 탐색·검증.
   - 신뢰 기준: 1차성 · 권위(`*.go.kr`/`*.gov`/`europa.eu`/표준기구/공식 벤더) · 검증가능(작성주체·게시일) · 최신성 · 교차검증.
   - 우선순위: ① 1차(공식문서·법령·규제공지·표준 원문·원 연구/데이터) →
     ② 공신력 2차(동료평가 리뷰·공공기관/분석기관 해설·주요 언론) → ③ 커뮤니티(①②로 교차검증).
     `arXiv` 논문은 원 연구일 수 있지만 미동료평가 preprint일 수 있으므로 그 상태를 표시한다.
   - 벤더 문서는 해당 제품의 기능·상태에는 1차 출처지만, 경쟁 비교·ROI·고객 성과 주장은 독립 근거로 교차검증한다.
   - 앵커(출발점, 더 권위 있는 1차 발견 시 우선): `learn.microsoft.com`·`azure.microsoft.com`·`devblogs.microsoft.com`·`github.blog`·`docs.github.com`; 규제 `eur-lex.europa.eu`·`law.go.kr`·`fsc.go.kr`·`fsec.or.kr`·`pipc.go.kr`·`nist.gov`·`iso.org`; 연구 `arxiv.org`. 도메인 개편·리다이렉트 고려.
   - MS/Azure/GitHub 주제: 일반어 대신 구체 서비스명(Microsoft Foundry·Microsoft Agent Framework·
     Azure AI Search·Azure AI Content Safety·Microsoft Entra·Microsoft Purview·Microsoft Defender·
     GitHub Copilot·GitHub Platform/GitHub Actions/GitHub Advanced Security·AKS·Azure Container
     Apps)으로 기능·통제·가치를 수집.
4. **검색과 원문 수집**:
   - 다음 capability 순서로 경로를 선택한다. 앞 경로가 없거나 실패할 때만 다음 경로로 전환한다.
     1. Copilot이 제공하는 general web search tool(예: `web_search`)
     2. Copilot CLI의 `/research` 또는 web source를 지원하는 Research agent
     3. 도메인 전용 검색(예: Microsoft Learn/Docs MCP, GitHub search/API, 공식 문서 사이트 검색)
     4. 알려진 canonical URL, 공식 문서 index, `sitemap.xml`, RSS/Atom, release notes/changelog
     5. 접근 가능한 경로가 없으면 실시간 검증 불가로 명시
   - 공식 문서 URL을 알면 검색엔진을 거치지 않고 원문을 직접 연다. 범용 검색이 없어도 공식 sitemap,
     RSS/Atom, 문서 index를 이용해 후보 URL을 찾을 수 있다.
   - 검색 결과 페이지·검색 스니펫·AI 요약은 URL 발견용일 뿐 근거가 아니다. 신뢰 기준을 통과한 원문을
     `web_fetch`, `fetch_webpage` 등 현재 환경의 페이지 조회 도구로 직접 연다.
   - JS challenge·CAPTCHA·봇 차단·403/429이면 같은 URL을 반복 호출하지 않는다. User-Agent 회전, proxy,
     cookie 재사용, CAPTCHA 우회도 시도하지 않고 접근 가능한 공식 원문이나 동급 1차 출처로 전환한다.
   - `curl`은 일반 원문 조회 도구가 없고 해당 사이트가 자동 조회를 허용할 때만 사용한다. Google Search/
     Google News, DuckDuckGo HTML/Lite, Bing Search의 SERP endpoint에는 사용하지 않으며 URL·헤더에 PII나
     secret을 넣지 않는다.
5. **검증**: 주장마다 원문의 발행/갱신일, 적용 지역, 제품 버전, GA/Preview 상태를 확인한다. 상충하면
   현재 공식 원문을 우선하되 상충 사실과 남은 불확실성을 함께 밝힌다. 시간에 따라 바뀌는 주장은
   오래된 문서 하나만으로 확정하지 않는다. 검색 provider의 답변만으로 검증 완료 처리하지 않고 최소 한
   개의 canonical 원문을 직접 확인한다.
6. **구조화 수집**: 기초자료 조사·자료 수집·복합 리서치는 답변 작성 전에 조사 결과를 아래 공통
   Fact Ledger 계약으로 병합한다. downstream 스킬이 별도 schema를 지정하면 이 필드를 보존해 변환한다.

   | ID | Type | Claim | Evidence | Source | Publisher | Published/updated | Accessed | Scope/status | Confidence |
   |---|---|---|---|---|---|---|---|---|---|

   - `Type`은 `Fact`·`Inference`·`Assumption` 중 하나다. 추론과 가정을 사실처럼 쓰지 않는다.
   - 한 행에는 검증 가능한 주장 하나만 기록한다. `Evidence`에는 짧은 직접 근거 또는 정확한 요약을,
     `Source`에는 문서 제목과 canonical URL을 기록한다. PDF·보고서·긴 문서는 Evidence에 page·section·
     table 등 원문 위치(locator)를 함께 기록한다.
   - `Scope/status`에는 적용 지역·제품 버전·GA/Preview·표본 등 해석 조건을 기록한다. 날짜를 찾지 못하면
     빈칸 대신 `확인 불가`로 표시하고, 확인 가능한 날짜는 `YYYY-MM-DD`로 통일한다.
   - `Confidence`는 `High`(최신 canonical 1차 출처가 직접 뒷받침), `Medium`(신뢰할 수 있는 2차 출처 또는
     조건부·간접 근거), `Low`(비1차 단일 근거 또는 미해결 충돌) 중 하나다. `Low` 주장을 핵심 결론의
     확정 근거로 사용하지 않는다.
   - 같은 주장은 중복 제거하고, 상충하는 주장은 각각 보존한 뒤 채택 근거와 남은 불확실성을 기록한다.
     접근 실패·페이월·신뢰 기준 미달 자료는 근거로 넣지 않고 제외 사유를 별도로 남긴다.
   - 재현 가능한 수집물이 필요한 작업은 Research Brief, 핵심 쿼리, Fact Ledger, 확인일을 함께 보존한다.
     사람이 읽는 원장은 해당 작업 폴더의 `fact-ledger.md`에 저장한다.
   - downstream 빌드가 research metadata를 검증하는 작업에서는 같은 내용을
     [`schema/fact-ledger.schema.json`](./schema/fact-ledger.schema.json)에 맞춘 `fact-ledger.json`으로도
     저장한다. `checkedAt`은 timezone이 포함된 ISO 8601 timestamp이며, `source`는 제목과 URL을 분리한다.
     예시는 [`examples/fact-ledger.example.json`](./examples/fact-ledger.example.json)을 따른다.
7. **완료 판정**: 다음 조건을 모두 충족해야 조사를 완료한다.
   - 필수 조사 축마다 근거를 확보했거나, 확보하지 못한 범위와 이유를 명시했다.
   - 결론에 영향을 주는 각 사실 주장에 최소 한 개의 canonical 원문이 연결되어 있다.
   - 경쟁 비교·ROI·고객 성과처럼 이해관계가 있는 주장은 가능한 경우 독립 출처로 교차검증했다.
   - 날짜·지역·버전·GA/Preview 등 시간과 범위에 민감한 조건을 확인했고, Fact·Inference·Assumption을 분리했다.
8. **정리**: 결론(1~3문장) → 필요한 상세 → `### 출처`(제목·원문 URL·해당 주장의 근거) 순서로 쓴다.
   단순 질문에는 별도 `검색 결과` 제목이나 쿼리 목록을 붙이지 않는다. 최신성 추적이 중요한 경우에만
   확인일을 표시하고, 변동 가능성이 있으면 확인 시점을 명시한다. 사용자가 수집물이나 조사 근거를
   요청했으면 Fact Ledger 또는 그 핵심 열을 함께 제공한다.

## 연산자
`site:` · `"exact"` · `after:YYYY-MM-DD` · `filetype:` · `-kw` · `OR`.

## 처리
결과가 없으면 용어·언어·기간·출처 유형을 바꿔 재구성한다. 완료 기준을 충족하면 멈추고, 합리적인
재구성에도 신뢰할 수 있는 새 근거가 더 나오지 않으면 미확보 범위와 탐색 한계를 기록한다. 검색 provider
자체가 차단되면 다른 공개 SERP를 scraping하는 fallback 대신 도메인 전용 검색 또는 공식
index/sitemap/RSS 경로로 전환한다. 비신뢰 출처만 있으면 사실 확정을 보류한다.
페이월·403의 스니펫은 근거로 사용하지 않는다. 모든 실시간 경로가 실패하면 "실시간 검증 불가"와 실패
범위를 명시하고, 학습 데이터만으로 `현재`·`최신` 답을 단정하지 않는다. 쿼리·URL·로그에 개인정보와
secret을 넣지 않는다.
