---
name: google-web-search
description: "최신 정보가 필요할 때 Google 검색을 우선하고 접근 가능한 웹 검색과 공식 원문으로 실시간 사실을 검증한 뒤, 결론부터 Straightforward하게 요약합니다. 학습 데이터 이후의 뉴스·기술 업데이트·릴리스·가격 변경·규제 동향·전략 리포트 등. WHEN: 최신 정보 검색, 실시간 검색, Google 검색, web search, 최신 뉴스, latest news, 최근 업데이트, 릴리스 노트, release notes, changelog, 최신 버전, 현재 가격, current price, 현재 상태, what's new, 오늘/최근 연도 정보, 최신 트렌드, 기술·시장·산업 동향, 전략 리포트, 공식 발표, 최신 문서, AI 규제 동향, EU AI Act, GDPR, 개인정보보호법, 컴플라이언스, ISO 27001, NIST, 클라우드·AI 도입 사례."
argument-hint: "검색하고 싶은 주제나 질문을 입력하세요"
---

# 실시간 웹 검색 (Google 우선)

## Straightforward 출력 원칙
- 검색 과정이 아니라 **사용자가 바로 쓸 결론**을 먼저 1~3문장으로 제시한다.
- 단순한 사실 질문은 단순하게 답하고, 검색어·탐색 일지·불필요한 배경 설명을 노출하지 않는다.
- 상세 내용은 결론의 근거·조건·예외를 이해하는 데 필요한 만큼만 붙인다. 확실한 사실, 조건부 사실,
  확인하지 못한 내용을 분리한다.
- 출처는 주장 바로 뒤 또는 마지막 `### 출처`에 원문 중심으로 제공한다. 출처 수를 늘리기보다 핵심 주장과
  직접 연결되는 1차 출처를 우선한다.

## 절차
1. **쿼리 설계**: 질문을 독립 검증 가능한 주장으로 나누고, 출처가 쓰는 언어의 구체 용어를 사용한다.
   최신성이 중요한 주장에만 현재 연도·날짜 범위를 넣고, 사용자가 지정한 도메인과 공식 도메인을 우선한다.
2. **소스(동적, 고정 화이트리스트 아님)**: 주제별 가장 권위 있는 1차 출처를 탐색·검증.
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
3. **검색과 원문 수집**:
   - 사용 가능한 검색 도구가 있으면 먼저 사용한다. URL 기반 탐색만 가능하면 Google Search/Google News를
     우선하고, 차단되면 한 번만 DuckDuckGo HTML로 전환한다. 공식 문서 URL을 알면 검색엔진을 거치지 않는다.
   - 검색 결과 페이지·검색 스니펫·AI 요약은 URL 발견용일 뿐 근거가 아니다. 신뢰 기준을 통과한 원문을
     `web_fetch`, `fetch_webpage` 등 현재 환경의 페이지 조회 도구로 직접 연다.
   - JS challenge·봇 차단·403이면 같은 URL을 반복 호출하지 말고 접근 가능한 공식 원문이나 동급 1차
     출처로 전환한다. 일반 조회 도구가 없을 때만 `curl`을 사용하며 URL·헤더에 PII나 secret을 넣지 않는다.
4. **검증**: 주장마다 원문의 발행/갱신일, 적용 지역, 제품 버전, GA/Preview 상태를 확인한다. 상충하면
   현재 공식 원문을 우선하되 상충 사실과 남은 불확실성을 함께 밝힌다. 시간에 따라 바뀌는 주장은
   오래된 문서 하나만으로 확정하지 않는다.
5. **정리**: 결론(1~3문장) → 필요한 상세 → `### 출처`(제목·원문 URL·해당 주장의 근거) 순서로 쓴다.
   단순 질문에는 별도 `검색 결과` 제목이나 쿼리 목록을 붙이지 않는다. 최신성 추적이 중요한 경우에만
   확인일과 핵심 쿼리를 짧게 표시하고, 변동 가능성이 있으면 확인 시점을 명시한다.

## 연산자
`site:` · `"exact"` · `after:YYYY-MM-DD` · `filetype:` · `-kw` · `OR`.

## 처리
결과 없음→쿼리 재구성 1회. 비신뢰 출처만 있으면 사실 확정을 보류한다. 페이월·403의 스니펫은
근거로 사용하지 않는다. 모든 실시간 경로가 실패하면 "실시간 검증 불가"와 실패 범위를 명시하고,
학습 데이터만으로 `현재`·`최신` 답을 단정하지 않는다. 쿼리·URL·로그에 개인정보와 secret을 넣지 않는다.
