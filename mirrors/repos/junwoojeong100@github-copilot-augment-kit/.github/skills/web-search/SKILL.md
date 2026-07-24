---
name: web-search
description: "최신 정보·기초자료·공식 근거가 필요한 질문을 검색하고 canonical 원문으로 검증해 결론부터 요약합니다. 단순 사실은 바로 답하고, 복합 조사는 Research Brief와 Fact Ledger로 구조화합니다. 공개 검색 결과 페이지를 scraping하지 않습니다. WHEN: 최신 정보 검색, 실시간 검색, Google 검색, web search, 기초자료 조사, 자료 검색/수집, 고객/기업 조사, 시장 규모, 산업 리서치, 최신 뉴스, 릴리스 노트, changelog, 최신 버전, 현재 가격, 현재 상태, 공식 발표, 최신 문서, 규제·컴플라이언스 조사. NOT WHEN: 사용자가 제공한 정적 문서만 요약하거나 최신성·외부 근거가 필요 없는 창작·코딩 작업."
argument-hint: "검색할 주제, 지역·기간, 필요한 산출물을 입력하세요"
---

# Web Search

최신 정보와 외부 근거가 필요한 질문을 **검색 → 원문 확인 → 결론 우선 답변**으로 처리한다.
이 스킬은 GitHub Copilot CLI와 VS Code Copilot Chat/Agent에서 검색 전략을 제공하며, 검색 backend를
직접 만들지 않는다.

## 실행 계약

- 단순 사실 질문은 바로 검색하고 답한다.
- 기초자료 조사·자료 수집·복합 리서치는 목적, 대상, 지역, 기간, 필수 조사 축, 산출물을 짧은
  **Research Brief**로 먼저 확정한다.
- 검색 과정이나 쿼리 목록보다 사용자가 바로 쓸 결론을 첫 1~3문장에 제시한다.
- 최신성·버전·지역·GA/Preview 상태가 결론을 바꾸면 반드시 확인한다.
- Google·DuckDuckGo·Bing의 공개 검색 결과 페이지(SERP)를 `curl`, page fetch, browser로 직접 조회하지 않는다.

## 도구 선택

다음 순서를 사용하며, 앞 경로가 없거나 실패할 때만 다음으로 이동한다.

1. Copilot이 제공하는 general web search tool(예: `web_search`)
2. Copilot CLI의 `/research` 또는 web source를 지원하는 Research agent
3. 도메인 전용 검색(예: Microsoft Learn/Docs MCP, GitHub search/API)
4. 알려진 canonical URL, 공식 문서 index, `sitemap.xml`, RSS/Atom, release notes
5. 접근 가능한 경로가 없으면 실시간 검증 불가로 명시

공식 URL을 알면 검색엔진을 거치지 않고 원문을 직접 연다. 검색 결과·스니펫·AI 요약은 URL 발견용일
뿐 근거가 아니다. `web_fetch` 같은 조회 도구로 원문을 확인한다. JS challenge·CAPTCHA·403·429가
발생하면 우회하거나 반복 호출하지 않고 동급 공식 출처로 전환한다.
범용 검색 capability도 공식 URL도 없으면 사용자가 출발 URL을 제공해야 함을 알리고, 현재 지식만으로
최신 사실을 만들지 않는다.

## 워크플로

1. **범위 확정**: 결론을 바꾸는 입력만 한 번에 하나씩 확인한다. 비대화형 환경에서는 합리적인 가정을 표시한다.
2. **주장 분해**: 질문을 독립 검증 가능한 주장으로 나누고, 출처가 사용하는 구체 용어로 검색한다.
3. **출처 선택**: 공식 문서·법령·표준·원 연구·공식 데이터 등 1차 출처를 우선한다. 벤더의 경쟁 비교,
   ROI, 고객 성과는 가능한 경우 독립 출처로 교차검증한다.
4. **원문 확인**: 작성 주체, 발행·갱신일, 적용 지역, 버전, GA/Preview, 표본과 단위를 확인한다.
   검색 provider의 답변만으로 검증 완료 처리하지 않고 최소 한 개의 canonical 원문을 직접 확인한다.
5. **구조화**: 복합 조사와 downstream 작업은 아래 공통 Fact Ledger 계약으로 병합한다.
6. **답변**: 결론 → 필요한 근거·조건·예외 → `### 출처` 순서로 작성한다.

## Fact Ledger 계약

| ID | Type | Claim | Evidence | Source | Publisher | Published/updated | Accessed | Scope/status | Confidence |
|---|---|---|---|---|---|---|---|---|---|

- `Type`은 `Fact`·`Inference`·`Assumption` 중 하나다.
- 한 행에는 주장 하나만 기록한다. PDF·보고서·긴 문서는 `Evidence`에 짧은 근거와 page·section·
  table 등 원문 위치(locator)를 기록한다.
- `Source`에는 문서 제목과 canonical URL을 기록한다.
- 확인 가능한 날짜는 `YYYY-MM-DD`, 확인하지 못한 날짜는 `확인 불가`로 쓴다.
- `Scope/status`에는 지역·버전·GA/Preview·표본 등 해석 조건을 기록한다.
- `Confidence`는 `High`(canonical 1차 출처가 직접 뒷받침), `Medium`(신뢰할 수 있는 2차 또는 간접 근거),
  `Low`(비1차 단일 근거 또는 미해결 충돌)다. `Low`를 핵심 결론의 확정 근거로 쓰지 않는다.
- 상충하는 주장은 각각 보존하고 채택 근거와 남은 불확실성을 기록한다.
- 접근 실패·페이월·신뢰 기준 미달 자료는 근거에서 제외하고 제외 사유를 별도로 남긴다.
- 재현 가능한 수집물은 `fact-ledger.md`로 보존한다. machine-readable handoff가 필요하면
  [`schema/fact-ledger.schema.json`](./schema/fact-ledger.schema.json)에 맞춘 `fact-ledger.json`도 만든다.
  `checkedAt`은 timezone이 포함된 ISO 8601 timestamp이며, 예시는
  [`examples/fact-ledger.example.json`](./examples/fact-ledger.example.json)을 따른다.

## **완료 판정**

- 필수 조사 축마다 근거를 확보했거나 확보하지 못한 범위와 이유를 밝혔다.
- 결론에 영향을 주는 각 사실 주장에 최소 한 개의 canonical 원문이 연결되어 있다.
- 이해관계가 있는 비교·ROI·고객 성과는 가능한 경우 독립 출처로 교차검증했다.
- Fact·Inference·Assumption과 날짜·지역·버전·상태를 구분했다.
- 결과가 없으면 용어·언어·기간·출처 유형을 바꿔 재구성하고, 그래도 실패하면 미확보 범위와 탐색 한계를
  명시했다.

## 출력 원칙

- 확실한 사실, 조건부 사실, 확인하지 못한 내용을 구분한다.
- 출처는 주장 바로 뒤 또는 마지막 `### 출처`에 제목·canonical URL·근거를 연결한다.
- 단순 질문에는 별도 검색 보고서나 Fact Ledger를 노출하지 않는다.
- 모든 실시간 경로가 실패하면 현재 지식만으로 `현재`·`최신`을 단정하지 않는다.
- 쿼리·URL·로그에 개인정보와 secret을 넣지 않는다.
