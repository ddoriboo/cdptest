# CDP AI 플랫폼 배포 가이드

## 🚀 Streamlit Cloud 배포 (권장)

### 1. GitHub 저장소 준비
```bash
# 저장소 생성 및 코드 업로드
git init
git add .
git commit -m "Initial commit: CDP AI Platform"
git branch -M main
git remote add origin https://github.com/your-username/cdp-ai-platform.git
git push -u origin main
```

### 2. Streamlit Cloud 배포
1. [Streamlit Cloud](https://streamlit.io/cloud) 접속
2. GitHub 계정으로 로그인
3. "New app" 클릭
4. 저장소 선택: `your-username/cdp-ai-platform`
5. 브랜치: `main`
6. 메인 파일: `cdp_ai_platform.py`
7. "Deploy" 클릭

### 3. 환경 변수 설정
앱 설정 → Advanced settings → Secrets에 추가:
```toml
OPENAI_API_KEY = "sk-proj-..."
```

### 4. 배포 완료
- 약 2-3분 후 앱이 활성화됩니다
- 제공된 URL로 접속 가능

## 🖥️ 로컬 실행

### 1. 환경 설정
```bash
# Python 3.8+ 필요
python --version

# 가상환경 생성 (선택사항)
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux  
source venv/bin/activate
```

### 2. 패키지 설치
```bash
pip install -r requirements.txt
```

### 3. 환경변수 설정
`.env` 파일 생성:
```bash
OPENAI_API_KEY=your-api-key-here
```

### 4. 실행
```bash
streamlit run cdp_ai_platform.py
```

브라우저에서 `http://localhost:8501` 접속

## 🔧 고급 배포 옵션

### Docker를 사용한 배포

1. **Dockerfile 생성**
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["streamlit", "run", "cdp_ai_platform.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

2. **빌드 및 실행**
```bash
# 이미지 빌드
docker build -t cdp-ai-platform .

# 컨테이너 실행
docker run -p 8501:8501 -e OPENAI_API_KEY=your-key cdp-ai-platform
```

### AWS/GCP/Azure 배포

#### AWS ECS 배포
```bash
# ECR에 이미지 푸시
aws ecr get-login-password | docker login --username AWS --password-stdin your-account.dkr.ecr.region.amazonaws.com
docker tag cdp-ai-platform:latest your-account.dkr.ecr.region.amazonaws.com/cdp-ai-platform:latest
docker push your-account.dkr.ecr.region.amazonaws.com/cdp-ai-platform:latest

# ECS 서비스 배포
aws ecs create-service --cluster your-cluster --service-name cdp-ai-platform --task-definition cdp-ai-platform:1
```

## 📊 성능 최적화

### 1. 캐싱 설정
```python
# 함수에 캐싱 추가
@st.cache_data(ttl=3600)  # 1시간 캐시
def analyze_with_ai(query: str, model: str):
    # ... 기존 코드
```

### 2. 세션 상태 관리
```python
# 큰 데이터는 세션 상태에 저장
if 'cdp_columns' not in st.session_state:
    st.session_state.cdp_columns = load_cdp_columns()
```

### 3. 병렬 처리
```python
import asyncio
import aiohttp

async def parallel_api_calls():
    # 여러 API 동시 호출
    tasks = [
        analyze_with_ai(query1),
        analyze_with_ai(query2)
    ]
    results = await asyncio.gather(*tasks)
    return results
```

## 🔒 보안 설정

### 1. API 키 보안
```python
# 절대 하드코딩하지 말 것
❌ openai.api_key = "sk-proj-..."

# 환경변수 또는 secrets 사용
✅ openai.api_key = st.secrets["OPENAI_API_KEY"]
✅ openai.api_key = os.getenv("OPENAI_API_KEY")
```

### 2. 입력 검증
```python
def validate_query(query: str) -> bool:
    # SQL 인젝션 방지
    dangerous_keywords = ['DROP', 'DELETE', 'UPDATE', 'INSERT']
    return not any(keyword in query.upper() for keyword in dangerous_keywords)
```

### 3. 율제한 설정
```python
import time
from functools import wraps

def rate_limit(calls_per_minute=10):
    def decorator(func):
        func.last_called = 0
        func.call_count = 0
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            now = time.time()
            if now - func.last_called > 60:
                func.call_count = 0
                func.last_called = now
            
            if func.call_count >= calls_per_minute:
                st.error("API 호출 한도를 초과했습니다. 잠시 후 다시 시도해주세요.")
                return None
                
            func.call_count += 1
            return func(*args, **kwargs)
        return wrapper
    return decorator
```

## 📈 모니터링 설정

### 1. 로깅
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def analyze_with_ai(query: str):
    logger.info(f"AI 분석 요청: {query[:50]}...")
    # ... 분석 로직
    logger.info("AI 분석 완료")
```

### 2. 메트릭 수집
```python
import time

if 'metrics' not in st.session_state:
    st.session_state.metrics = {
        'total_queries': 0,
        'successful_queries': 0,
        'average_response_time': 0
    }

def track_query_metrics(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        st.session_state.metrics['total_queries'] += 1
        
        try:
            result = func(*args, **kwargs)
            st.session_state.metrics['successful_queries'] += 1
            return result
        finally:
            end_time = time.time()
            response_time = end_time - start_time
            st.session_state.metrics['average_response_time'] = (
                st.session_state.metrics['average_response_time'] + response_time
            ) / 2
    
    return wrapper
```

## 🐛 문제 해결

### 일반적인 오류

1. **OpenAI API 키 오류**
```
Error: openai.error.AuthenticationError
해결: API 키가 올바른지 확인, secrets.toml 설정 점검
```

2. **메모리 부족**
```
Error: Streamlit memory limit exceeded
해결: st.cache_data 사용, 세션 상태 정리
```

3. **배포 실패**
```
Error: App failed to deploy
해결: requirements.txt 확인, Python 버전 호환성 점검
```

### 디버깅 모드
```python
# 개발 모드에서만 디버그 정보 표시
if st.sidebar.checkbox("디버그 모드"):
    st.sidebar.json(st.session_state)
    st.sidebar.write("Current time:", datetime.now())
```

## 📞 지원

- **GitHub Issues**: 버그 리포트 및 기능 요청
- **이메일**: support@example.com  
- **문서**: [Streamlit Docs](https://docs.streamlit.io/)

## 📝 라이선스
MIT License - 자세한 내용은 LICENSE 파일 참조