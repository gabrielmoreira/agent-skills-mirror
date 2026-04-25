# AGENTS.md

## 프로젝트 개요

이 저장소는 웹 개발 기초를 초보자에게 가르치기 위한 교육용 커리큘럼 저장소입니다. 이 커리큘럼은 Microsoft Cloud Advocates가 개발한 12주 과정의 포괄적인 교육 과정으로, JavaScript, CSS, HTML을 다루는 24개의 실습 중심 수업으로 구성되어 있습니다.

### 주요 구성 요소

- **교육 콘텐츠**: 프로젝트 기반 모듈로 조직된 24개의 체계적인 수업
- **실습 프로젝트**: 테라리움, 타이핑 게임, 브라우저 확장 프로그램, 우주 게임, 은행 앱, 코드 편집기 및 AI 채팅 어시스턴트
- **인터랙티브 퀴즈**: 각 3문항씩 구성된 48개의 퀴즈 (수업 전/후 평가)
- **다국어 지원**: GitHub Actions를 통한 50개 이상 언어 자동 번역
- **기술 스택**: HTML, CSS, JavaScript, Vue.js 3, Vite, Node.js, Express, Python (AI 프로젝트용)

### 아키텍처

- 수업 기반 구조의 교육용 저장소
- 각 수업 폴더는 README, 코드 예제 및 솔루션 포함
- 독립형 프로젝트가 별도 디렉터리에 있음 (quiz-app, 다양한 수업 프로젝트)
- GitHub Actions를 이용한 번역 시스템 (co-op-translator)
- Docsify로 제공되는 문서 및 PDF로도 이용 가능

## 설정 명령어

이 저장소는 주로 교육 콘텐츠 소비용입니다. 특정 프로젝트 작업 시:

### 메인 저장소 설정

```bash
git clone https://github.com/microsoft/Web-Dev-For-Beginners.git
cd Web-Dev-For-Beginners
```

### 퀴즈 앱 설정 (Vue 3 + Vite)

```bash
cd quiz-app
npm install
npm run dev        # 개발 서버 시작
npm run build      # 프로덕션용 빌드
npm run lint       # ESLint 실행
```

### 은행 프로젝트 API (Node.js + Express)

```bash
cd 7-bank-project/api
npm install
npm start          # API 서버 시작
npm run lint       # ESLint 실행
npm run format     # Prettier로 포맷팅
```

### 브라우저 확장 프로젝트

```bash
cd 5-browser-extension/solution
npm install
# 브라우저별 확장 프로그램 로딩 지침을 따르세요
```

### 우주 게임 프로젝트

```bash
cd 6-space-game/solution
npm install
# 브라우저에서 index.html을 열거나 Live Server를 사용하세요
```

### 채팅 프로젝트 (Python 백엔드)

```bash
cd 9-chat-project/solution/backend/python
pip install openai
# GITHUB_TOKEN 환경 변수를 설정하세요
python api.py
```

## 개발 워크플로우

### 콘텐츠 기여자를 위한 절차

1. <strong>저장소를 포크</strong>하여 개인 GitHub 계정에 저장
2. **포크한 저장소를 로컬에 클론**
3. **변경을 위한 새 브랜치 생성**
4. 수업 콘텐츠 또는 코드 예제 수정
5. 관련 프로젝트 디렉터리에서 코드 변경 내용 테스트
6. 기여 지침에 따라 풀 리퀘스트 제출

### 학습자를 위한 절차

1. 저장소 포크 또는 클론
2. 수업 디렉터리를 순서대로 탐색
3. 각 수업의 README 파일 읽기
4. https://ff-quizzes.netlify.app/web/ 에서 수업 전 퀴즈 완료
5. 수업 폴더 내 코드 예제 실습
6. 과제 및 도전 과제 완료
7. 수업 후 퀴즈 풀기

### 라이브 개발

- <strong>문서</strong>: 루트에서 `docsify serve` 실행 (포트 3000)
- **퀴즈 앱**: quiz-app 디렉터리에서 `npm run dev` 실행
- <strong>프로젝트</strong>: HTML 프로젝트는 VS Code Live Server 확장 사용
- **API 프로젝트**: 각 API 디렉터리에서 `npm start` 실행

## 테스트 안내

### 퀴즈 앱 테스트

```bash
cd quiz-app
npm run lint       # 코드 스타일 문제 확인
npm run build      # 빌드 성공 여부 확인
```

### 은행 API 테스트

```bash
cd 7-bank-project/api
npm run lint       # 코드 스타일 문제 확인
node server.js     # 서버가 오류 없이 시작하는지 확인
```

### 일반 테스트 방법

- 본 저장소는 종합 자동화 테스트 없이 교육용으로 운영
- 수동 테스트는 아래에 집중:
  - 코드 예제가 오류 없이 실행되는지
  - 문서 내 링크 정상 작동 여부
  - 프로젝트 빌드 성공 여부
  - 예제들이 모범 사례 준수 여부

### 제출 전 점검

- package.json이 있는 디렉터리에서 `npm run lint` 실행
- 마크다운 링크 유효성 확인
- 브라우저 또는 Node.js에서 코드 예제 테스트
- 번역 파일이 올바른 구조 유지하는지 확인

## 코드 스타일 가이드

### JavaScript

- 최신 ES6+ 문법 사용
- 프로젝트 내 기본 ESLint 설정 준수
- 교육 목적의 명확한 변수 및 함수 명칭 사용
- 학습자 이해를 돕는 주석 추가
- 설정된 경우 Prettier로 포맷팅

### HTML/CSS

- 의미론적 HTML5 태그 사용
- 반응형 디자인 원칙 준수
- 명확한 클래스 네이밍 규칙
- CSS 기법을 설명하는 주석 포함

### Python

- PEP 8 스타일 가이드 준수
- 명확하고 교육적인 코드 예제 제공
- 학습에 도움이 되는 타입 힌트 활용

### 마크다운 문서화

- 명확한 제목 계층 구조
- 언어 지정된 코드 블록
- 추가 리소스 링크
- `images/` 내 스크린샷 및 이미지
- 접근성을 위한 이미지 대체 텍스트

### 파일 구성

- 수업은 번호 순서대로 정렬 (1-getting-started-lessons, 2-js-basics 등)
- 각 프로젝트는 `solution/` 및 대개 `start/` 또는 `your-work/` 디렉터리 포함
- 수업 별 `images/` 폴더에 이미지 저장
- 번역 파일은 `translations/{language-code}/` 구조로 관리

## 빌드 및 배포

### 퀴즈 앱 배포 (Azure Static Web Apps)

quiz-app은 Azure Static Web Apps 배포용으로 구성됨:

```bash
cd quiz-app
npm run build      # dist/ 폴더를 생성합니다
# main 브랜치에 푸시할 때 GitHub Actions 워크플로우를 통해 배포합니다
```

Azure Static Web Apps 구성:
- **앱 위치**: `/quiz-app`
- **출력 위치**: `dist`
- <strong>워크플로우</strong>: `.github/workflows/azure-static-web-apps-ashy-river-0debb7803.yml`

### 문서 PDF 생성

```bash
npm install                    # docsify-to-pdf 설치
npm run convert               # docs에서 PDF 생성
```

### Docsify 문서

```bash
npm install -g docsify-cli    # Docsify를 전역 설치하기
docsify serve                 # localhost:3000에서 서비스하기
```

### 프로젝트별 빌드

각 프로젝트 폴더는 자체 빌드 프로세스를 가질 수 있음:
- Vue 프로젝트: `npm run build`로 프로덕션 번들 생성
- 정적 프로젝트: 빌드 단계 없이 파일을 직접 서비스

## 풀 리퀘스트 가이드라인

### 제목 형식

변경 영역을 명확히 나타내는 제목 사용:
- `[Quiz-app] 수업 X를 위한 새 퀴즈 추가`
- `[Lesson-3] 테라리움 프로젝트 오타 수정`
- `[Translation] 5과 스페인어 번역 추가`
- `[Docs] 설정 지침 업데이트`

### 필수 점검 사항

PR 제출 전:

1. **코드 품질**:
   - 관련 프로젝트 디렉터리에서 `npm run lint` 실행
   - 모든 린트 에러 및 경고 수정

2. **빌드 검증**:
   - 해당 시 `npm run build` 실행
   - 빌드 오류 없을 것

3. **링크 확인**:
   - 모든 마크다운 링크 테스트
   - 이미지 참조 확인

4. **내용 검토**:
   - 맞춤법 및 문법 교정
   - 코드 예제 올바르고 교육적임 확인
   - 번역 내용 원문 의미 유지 확인

### 기여 요구 사항

- Microsoft CLA 동의 (첫 PR 시 자동 확인)
- [Microsoft 오픈 소스 행동 강령](https://opensource.microsoft.com/codeofconduct/) 준수
- 자세한 지침은 [CONTRIBUTING.md](./CONTRIBUTING.md) 참고
- PR 설명에 관련 이슈 번호 명시 (해당 시)

### 검토 절차

- PR은 유지 관리자 및 커뮤니티가 검토
- 교육적 명확성 우선 고려
- 코드 예제는 최신 모범 사례에 부합해야 함
- 번역은 정확성과 문화적 적합성 검토

## 번역 시스템

### 자동 번역

- GitHub Actions의 co-op-translator 워크플로우 사용
- 50개 이상의 언어로 자동 번역 수행
- 원본 파일은 메인 디렉터리에 위치
- 번역 파일은 `translations/{language-code}/`에 저장

### 수동 번역 개선 추가

1. `translations/{language-code}/`에서 파일 찾기
2. 구조를 유지하며 개선사항 반영
3. 코드 예제는 정상 작동 유지해야 함
4. 지역화된 퀴즈 콘텐츠 테스트

### 번역 메타데이터

번역 파일에는 메타데이터 헤더 포함:
```markdown
<!--
CO_OP_TRANSLATOR_METADATA:
{
  "original_hash": "...",
  "translation_date": "...",
  "source_file": "...",
  "language_code": "..."
}
-->
```

## 디버깅 및 문제 해결

### 자주 발생하는 문제

**퀴즈 앱 실행 실패**:
- Node.js 버전 확인 (v14 이상 권장)
- `node_modules` 및 `package-lock.json` 삭제 후 `npm install` 재실행
- 포트 충돌 검사 (기본 포트: Vite 5173)

**API 서버 실행 불가**:
- Node.js 최소 버전 충족 확인 (node >=10)
- 포트 사용 중인지 확인
- 모든 의존성 `npm install`로 설치 완료 여부

**브라우저 확장 프로그램 로드 실패**:
- manifest.json 형식 확인
- 브라우저 콘솔 에러 체크
- 브라우저별 확장 설치 지침 준수

**Python 채팅 프로젝트 문제**:
- OpenAI 패키지 설치 확인: `pip install openai`
- GITHUB_TOKEN 환경 변수 설정 여부
- GitHub Models 접근 권한 확인

**Docsify가 문서를 제공하지 않음**:
- docsify-cli 전역 설치: `npm install -g docsify-cli`
- 저장소 루트에서 실행
- `docs/_sidebar.md` 파일 존재 여부

### 개발 환경 팁

- HTML 프로젝트에 VS Code Live Server 확장 사용
- 일관된 포맷팅을 위한 ESLint 및 Prettier 확장 설치
- 브라우저 개발자 도구로 JavaScript 디버깅
- Vue 프로젝트는 Vue DevTools 브라우저 확장 설치

### 성능 고려사항

- 번역 파일 다수가 존재(50개 이상 언어)해 전체 클론 시 용량 큼
- 콘텐츠 작업만 할 경우 얕은 복제 사용: `git clone --depth 1`
- 영어 콘텐츠 작업 시 번역 검색 제외
- 초기 빌드 과정은 느릴 수 있음 (npm install, Vite 빌드)

## 보안 고려사항

### 환경 변수

- API 키는 저장소에 커밋 금지
- `.env` 파일 사용 (이미 `.gitignore`에 포함)
- 필수 환경 변수는 프로젝트 README에 문서화

### Python 프로젝트

- 가상 환경 사용 권장: `python -m venv venv`
- 의존성 최신 상태 유지
- GitHub 토큰 최소 권한 설정

### GitHub Models 접근

- GitHub Models 접근을 위한 개인 액세스 토큰(PAT) 필요
- 토큰은 환경 변수로 저장
- 토큰이나 자격 증명 절대 커밋 금지

## 추가 참고사항

### 대상 사용자

- 웹 개발 완전 초보자
- 학생 및 독학자
- 교실 수업에서 본 커리큘럼 사용하는 교사
- 접근성 및 점진적 기술 향상을 고려한 콘텐츠 설계

### 교육 철학

- 프로젝트 기반 학습 접근법
- 빈번한 지식 점검(퀴즈)
- 실습 코딩 연습
- 실제 적용 사례 예시
- 프레임워크 도입 전 기초기에 집중

### 저장소 유지 관리

- 활발한 학습자 및 기여자 커뮤니티
- 의존성과 콘텐츠 정기 업데이트
- 유지 관리자가 이슈 및 토론 지속 모니터링
- 번역 업데이트 자동화(GitHub Actions 활용)

### 관련 리소스

- [Microsoft Learn 모듈](https://docs.microsoft.com/learn/)
- [학생 허브 리소스](https://docs.microsoft.com/learn/student-hub/)
- 학습자를 위한 [GitHub Copilot](https://marketplace.visualstudio.com/items?itemName=GitHub.copilot) 권장
- 추가 코스: 생성 AI, 데이터 과학, ML, IoT 커리큘럼 제공

### 개별 프로젝트 작업

각 프로젝트별 자세한 지침은 다음 README 파일 참조:
- `quiz-app/README.md` - Vue 3 퀴즈 애플리케이션
- `7-bank-project/README.md` - 인증 기능이 있는 은행 앱
- `5-browser-extension/README.md` - 브라우저 확장 개발
- `6-space-game/README.md` - 캔버스 기반 게임 개발
- `9-chat-project/README.md` - AI 채팅 어시스턴트 프로젝트

### 모노레포 구조

전통적인 모노레포는 아니지만 여러 독립 프로젝트 포함:
- 각 수업/프로젝트는 독립적임
- 프로젝트 간 의존성 공유 없음
- 개별 프로젝트 작업 시 타 프로젝트 영향 없음
- 전체 커리큘럼 체험 위해 전체 저장소 클론 권장

---

<!-- CO-OP TRANSLATOR DISCLAIMER START -->
**면책 조항**:  
이 문서는 AI 번역 서비스 [Co-op Translator](https://github.com/Azure/co-op-translator)를 사용하여 번역되었습니다. 정확성을 위해 노력하고 있지만, 자동 번역에는 오류나 부정확성이 포함될 수 있음을 유의하시기 바랍니다. 원본 문서는 해당 언어로 된 원문이 권위 있는 출처로 간주되어야 합니다. 중요 정보의 경우 전문적인 인간 번역을 권장합니다. 이 번역 사용으로 인해 발생하는 모든 오해나 오역에 대해 당사는 책임을 지지 않습니다.
<!-- CO-OP TRANSLATOR DISCLAIMER END -->