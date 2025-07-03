# 🤖 CDP AI 자연어 쿼리 플랫폼

AI가 단계별로 분석하여 최적의 고객 세그먼테이션 전략을 추천하는 웹 플랫폼입니다.

## ⚠️ 보안 개선 완료

- ✅ API 키를 클라이언트에서 제거하고 서버에서 환경 변수로 관리
- ✅ Express 서버를 통한 API 프록시로 보안 강화
- ✅ 환경 변수 누락시 명확한 에러 메시지 제공

## 🚀 Railway 배포 방법

### 1. GitHub 저장소 연결
1. Railway 대시보드에서 "New Project" 클릭
2. "Deploy from GitHub repo" 선택
3. 이 저장소(`ddoriboo/cdptest`) 선택

### 2. 환경 변수 설정 (중요!)
Railway 프로젝트 설정에서 다음 환경 변수를 추가하세요:

```
OPENAI_API_KEY=your_openai_api_key_here
NODE_ENV=production
```

**주의**: OpenAI API 키가 없으면 더미 데이터로 동작합니다.

### 3. 자동 배포
- Railway가 자동으로 Node.js 프로젝트를 인식하고 빌드합니다
- `npm install` → `npm start` 순서로 실행됩니다

## 💻 로컬 실행 방법

```bash
# 의존성 설치
npm install

# 환경 변수 설정 (.env 파일 생성)
echo "OPENAI_API_KEY=your_api_key_here" > .env

# 서버 실행
npm start
```

## 📁 프로젝트 구조

```
├── working_ai_query_platform.html  # 메인 HTML 파일
├── server.js                       # Express 서버 (API 프록시)
├── package.json                    # Node.js 설정
└── README.md                       # 이 파일
```

## 🛠️ 기술 스택

- **Frontend**: HTML, CSS, JavaScript
- **Backend**: Node.js, Express.js
- **Deployment**: Railway
- **AI**: OpenAI API (서버에서 처리)

## 🌟 주요 기능

### 🔍 AI 쿼리 분석기
- 자연어로 질문하면 AI가 단계별로 분석
- 최적의 CDP 컬럼 조합 추천
- 실행 가능한 SQL 쿼리 자동 생성
- 비즈니스 인사이트 및 마케팅 방안 제시

### 📚 CDP 컬럼 브라우저
- 847개 CDP 컬럼 카테고리별 탐색
- 실시간 검색 및 필터링
- 컬럼별 상세 정보 및 사용 예시

### 👥 팀별 맞춤 추천
- 6개 팀별 특화 질문 템플릿
- 원클릭으로 질문 적용 및 분석

### 📨 Notitest 고급 메시지 생성
- AI 분석 결과 기반 태그 자동 추출
- 페르소나별 맞춤 메시지 생성
- A/B 테스트 변형 자동 생성
- 채널별 성과 예측
- 최적 발송 시간 추천

## 🚀 빠른 시작

### 로컬 개발 환경

1. **저장소 클론**
```bash
git clone <your-repo-url>
cd cdp
```

2. **가상환경 생성 및 활성화**
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. **패키지 설치**
```bash
pip install -r requirements.txt
```

4. **환경변수 설정**
```bash
# .streamlit/secrets.toml 파일 생성
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# 실제 API 키로 수정
```

5. **앱 실행**
```bash
streamlit run app.py
```

## ☁️ Streamlit Cloud 배포

### 1. GitHub 준비
```bash
git add .
git commit -m "CDP AI 플랫폼 초기 배포"
git push origin main
```

### 2. Streamlit Cloud 배포
1. [Streamlit Cloud](https://share.streamlit.io/)에 접속
2. GitHub 연동 및 저장소 선택
3. 메인 파일: `app.py` 설정
4. Advanced settings에서 secrets 설정:

```toml
OPENAI_API_KEY = "your-openai-api-key"
OPENAI_MODEL = "gpt-3.5-turbo"
NOTITEST_API_KEY = "your-notitest-api-key"
NOTITEST_API_ENDPOINT = "https://api.notitest.com/v1"
```

### 3. 커스텀 도메인 설정 (선택사항)
- Streamlit Cloud 설정에서 커스텀 도메인 연결
- DNS 설정으로 CNAME 레코드 추가

## 🔧 기술 스택

- **Frontend**: Streamlit
- **AI/ML**: OpenAI GPT API
- **Data Visualization**: Plotly
- **Message Management**: Notitest API
- **Data Processing**: Pandas
- **Deployment**: Streamlit Cloud

## 📝 API 키 설정

### OpenAI API
```python
# OpenAI API 키 발급: https://platform.openai.com/api-keys
OPENAI_API_KEY = "sk-..."
```

### Notitest API
```python
# Notitest API 키 (고객사 제공)
NOTITEST_API_KEY = "nt_..."
NOTITEST_API_ENDPOINT = "https://api.notitest.com/v1"
```

## 🗂️ 프로젝트 구조

```
cdp/
├── app.py                          # 메인 Streamlit 앱
├── notitest_integration.py         # Notitest 연계 모듈
├── requirements.txt                # Python 패키지 의존성
├── README.md                       # 프로젝트 문서
├── .streamlit/
│   ├── config.toml                 # Streamlit 설정
│   ├── secrets.toml.example        # 환경변수 예시
│   └── secrets.toml                # 실제 환경변수 (gitignore)
└── working_ai_query_platform.html  # 원본 HTML 버전
```

## 🎯 사용법

### 1. 기본 쿼리 분석
1. "쿼리 분석기" 탭 선택
2. 자연어로 질문 입력 (예: "대출 니즈가 높은 고객군 알려줘")
3. "AI 분석" 버튼 클릭
4. 단계별 분석 결과 확인

### 2. 팀별 추천 질문 활용
1. "팀별 추천" 탭 선택
2. 담당자 선택
3. 추천 질문 중 "사용" 버튼 클릭
4. 자동으로 쿼리 분석 실행

### 3. Notitest 메시지 생성
1. 쿼리 분석 완료 후 "Notitest 메시지" 탭 이동
2. 자동 생성된 A/B 테스트 메시지 확인
3. 성과 예측 및 최적 채널 확인
4. "캠페인 실행" 버튼으로 Notitest 전송

## 🔄 A/B 테스트 변형

### 자동 생성 변형
- **이모지 강화**: 핵심 키워드에 이모지 추가
- **긴급성 추가**: 시간 제한 문구 삽입
- **개인화 강화**: 고객 맞춤 표현 증가
- **혜택 중심**: 혜택을 강조하는 메시지
- **사회적 증거**: 인기도/만족도 정보 추가

### 성과 지표
- 오픈율 (Open Rate)
- 클릭률 (Click Rate)
- 전환율 (Conversion Rate)
- 메시지당 수익 (Revenue per Message)

## 📊 지원하는 CDP 컬럼

### 관심사 지표 (fa_int_*)
- 1인 가구, 반려동물, 대출, 여행, 뷰티 등 52개 지표

### 업종별 지표 (fa_ind_*)
- 결제 패턴 기반 업종별 행동 142개 지표

### 예측 스코어 (sc_*)
- AI 기반 구매/행동 예측 스코어 156개

### 플래그 지표 (fi_npay_*)
- 인구통계학적 특성 및 서비스 이용 여부 497개

## 🚨 주의사항

### 보안
- API 키는 절대 코드에 하드코딩하지 말 것
- secrets.toml은 .gitignore에 포함되어 있음
- 프로덕션 환경에서는 환경변수 사용 권장

### 성능
- OpenAI API 호출 제한 고려
- 대용량 데이터 처리 시 캐싱 활용
- Streamlit 세션 상태 적절히 관리

### 법적 고려사항
- 개인정보 처리방침 준수
- 마케팅 동의 확인 필수
- GDPR, 개인정보보호법 등 관련 법규 준수

## 🔗 관련 링크

- [Streamlit 문서](https://docs.streamlit.io/)
- [OpenAI API 문서](https://platform.openai.com/docs)
- [Plotly 문서](https://plotly.com/python/)

## 🤝 기여하기

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 라이센스

이 프로젝트는 MIT 라이센스 하에 배포됩니다.

## 🆘 문제 해결

### 일반적인 문제

**Q: OpenAI API 오류가 발생해요**
A: API 키 확인 및 요청 제한 확인

**Q: Notitest 연동이 안 돼요**
A: API 엔드포인트 및 인증 정보 확인

**Q: 성능이 느려요**
A: 캐싱 활성화 및 세션 상태 최적화

### 지원
- 이슈 등록: GitHub Issues
- 문의: [연락처 정보]

---

🚀 **Happy Analyzing & Marketing!** 🚀