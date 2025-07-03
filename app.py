import streamlit as st
import time
import json
from datetime import datetime
import openai
from typing import Dict, List, Any
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from notitest_integration import NotitestGenerator

# 페이지 설정
st.set_page_config(
    page_title="CDP AI 자연어 쿼리 플랫폼",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS 스타일 적용
st.markdown("""
<style>
    .main {
        background-color: #f8f9fa;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #e9ecef;
        border-radius: 8px;
        padding: 8px 16px;
        font-weight: 500;
    }
    .stTabs [aria-selected="true"] {
        background-color: #4CAF50;
        color: white;
    }
    .result-card {
        background: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    .stat-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
    }
    .thinking-step {
        background: white;
        padding: 15px;
        margin: 10px 0;
        border-radius: 10px;
        border-left: 4px solid #4CAF50;
        transition: all 0.3s ease;
    }
    .noti-tag {
        display: inline-block;
        background: #e3f2fd;
        color: #1976d2;
        padding: 4px 12px;
        border-radius: 16px;
        margin: 4px;
        font-size: 14px;
    }
    .noti-message {
        background: #f5f5f5;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
        border-left: 3px solid #4CAF50;
    }
</style>
""", unsafe_allow_html=True)

# 세션 상태 초기화
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None
if 'thinking_progress' not in st.session_state:
    st.session_state.thinking_progress = 0
if 'noti_messages' not in st.session_state:
    st.session_state.noti_messages = []
if 'noti_generator' not in st.session_state:
    notitest_api_key = st.secrets.get("NOTITEST_API_KEY", "")
    notitest_endpoint = st.secrets.get("NOTITEST_API_ENDPOINT", "")
    st.session_state.noti_generator = NotitestGenerator(notitest_api_key, notitest_endpoint)
if 'ab_test_config' not in st.session_state:
    st.session_state.ab_test_config = None
if 'performance_predictions' not in st.session_state:
    st.session_state.performance_predictions = None
if 'advanced_tags' not in st.session_state:
    st.session_state.advanced_tags = {'primary': [], 'secondary': []}

# OpenAI API 키 설정
OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY", "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")
openai.api_key = OPENAI_API_KEY

# CDP 컬럼 데이터 (일부만 표시)
CDP_COLUMNS = {
    'interests': {
        'fa_int_householdsingle': {'desc': '1인 가구 관련 상품 결제 또는 오피스텔/원룸 거주 추정 고객', 'type': 'date'},
        'fa_int_householdpet': {'desc': '반려동물 관련 상품 결제 고객', 'type': 'date'},
        'fa_int_loan1stfinancial': {'desc': '1금융권에서 신용 대출 실행 고객', 'type': 'date'},
        'fa_int_loanpersonal': {'desc': '신용대출을 실행 고객', 'type': 'date'},
        'fa_int_luxury': {'desc': '100만원 이상 명품관련 결제 고객', 'type': 'date'},
        'fa_int_traveloverseas': {'desc': '향후 1개월 내 해외 여행 목적의 출국 예정 추정 고객', 'type': 'date'},
    },
    'scores': {
        'sc_int_loan1stfinancial': {'desc': '1금융권 신용대출 예측스코어', 'type': 'double'},
        'sc_int_highincome': {'desc': '고소득 예측스코어', 'type': 'double'},
        'sc_ind_cosmetic': {'desc': '뷰티 제품 결제 예측스코어', 'type': 'double'},
    },
    'flags': {
        'fi_npay_creditcheck': {'desc': '신용조회 서비스 가입 여부', 'type': 'boolean'},
        'fi_npay_genderf': {'desc': '여성 고객', 'type': 'boolean'},
        'fi_npay_age20': {'desc': '20대 연령층', 'type': 'boolean'},
    }
}

# 팀별 추천 질문
TEAM_QUESTIONS = {
    '💰 정선영님 (금융 컨텐츠)': [
        "금융 컨텐츠에 관심이 높은 MZ세대 고객을 찾아줘",
        "투자 정보를 자주 찾는 고소득 고객군은?",
        "머니스토리 콘텐츠를 좋아할 만한 고객 특성은?"
    ],
    '👥 박지영님 (회원 플래닝)': [
        "신규 가입 후 이탈 위험이 높은 고객군을 찾아줘",
        "프리미엄 회원으로 업그레이드할 가능성이 높은 고객은?",
        "활동성이 높은 충성 고객의 특성을 분석해줘"
    ],
    '🏦 김정희님 (내자산 플래닝)': [
        "자산관리에 관심이 높은 30-40대 고객을 찾아줘",
        "마이데이터 서비스를 적극 활용할 고객군은?",
        "포트폴리오 다변화에 관심있는 투자자를 찾아줘"
    ],
    '📢 고시현님 (AD 서비스)': [
        "광고 반응률이 높을 것으로 예상되는 고객군은?",
        "프리미엄 브랜드 광고에 관심있는 고객을 찾아줘",
        "모바일 광고 클릭률이 높은 사용자 특성은?"
    ],
    '💳 최동주님 (결제 데이터)': [
        "결제 빈도가 급증한 고객 세그먼트를 찾아줘",
        "특정 업종에서 결제가 활발한 고객군은?",
        "온라인 결제를 선호하는 고객들의 연령대별 분포는?"
    ],
    '🏠 이승한님 (대출 서비스)': [
        "대출 신청 가능성이 높은 고객 세그먼트는?",
        "대환대출 니즈가 있는 고객들을 찾아줘",
        "주택담보대출을 고려할 만한 고객군은?"
    ]
}

# Notitest 메시지 템플릿
NOTI_TEMPLATES = {
    'loan': {
        'tags': ['대출', '금융', '신용', '자금'],
        'templates': [
            "💰 {name}님, 최대 {amount}만원까지 대출 가능! 연 {rate}% 특별금리 제공",
            "🏦 신용등급 우수 고객님께 드리는 특별 혜택! 무서류 간편대출 가능",
            "📊 {name}님의 신용점수가 상승했어요! 더 좋은 조건으로 대출 받으세요"
        ]
    },
    'beauty': {
        'tags': ['뷰티', '화장품', '코스메틱', '미용'],
        'templates': [
            "💄 {name}님만을 위한 뷰티 추천! 인기 제품 최대 {discount}% 할인",
            "✨ 피부타입 맞춤 화장품 큐레이션! 무료 샘플 증정 이벤트",
            "🌸 봄맞이 뷰티 세일! {brand} 전 제품 특가 진행중"
        ]
    },
    'travel': {
        'tags': ['여행', '항공', '호텔', '휴가'],
        'templates': [
            "✈️ {destination} 특가 항공권! 왕복 {price}원부터",
            "🏖️ {name}님, 여름 휴가 준비하세요? 호텔 최대 {discount}% 할인",
            "🗺️ 해외여행 필수템! 환전 수수료 면제 + 여행자보험 무료"
        ]
    },
    'shopping': {
        'tags': ['쇼핑', '할인', '세일', '구매'],
        'templates': [
            "🛍️ {name}님이 관심있어 하시는 상품이 {discount}% 할인중!",
            "💳 오늘만 특가! 구매금액의 {cashback}% 캐시백 제공",
            "🎁 VIP 고객님께만 드리는 시크릿 쿠폰! 추가 {extra}% 할인"
        ]
    }
}

# 기존 함수들은 notitest_integration.py로 이동됨

async def analyze_query_with_ai(query: str) -> Dict:
    """OpenAI API를 사용한 쿼리 분석"""
    try:
        # GPT 모델 호출
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": f"""당신은 CDP(Customer Data Platform) 전문가입니다. 
                    사용자의 자연어 질문을 분석하여 최적의 고객 세그먼테이션 전략을 제공합니다.
                    
                    사용 가능한 CDP 컬럼: {json.dumps(CDP_COLUMNS, ensure_ascii=False)}
                    
                    응답은 반드시 다음 JSON 형식으로 제공해주세요:
                    {{
                        "query_analysis": "사용자 질문 분석 내용",
                        "target_description": "타겟 고객군 설명",
                        "recommended_columns": [
                            {{
                                "column": "컬럼명",
                                "description": "컬럼 설명",
                                "condition": "추천 조건",
                                "priority": "high|medium|low",
                                "reasoning": "선택 이유"
                            }}
                        ],
                        "sql_query": "SELECT 문",
                        "business_insights": ["인사이트1", "인사이트2"],
                        "estimated_target_size": "예상 타겟 규모",
                        "marketing_recommendations": ["추천1", "추천2"]
                    }}"""
                },
                {
                    "role": "user",
                    "content": query
                }
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        return json.loads(response.choices[0].message.content)
    
    except Exception as e:
        # 폴백 데이터 반환
        return generate_fallback_result(query)

def generate_fallback_result(query: str) -> Dict:
    """API 오류 시 폴백 결과 생성"""
    if '대출' in query:
        return {
            "query_analysis": f'"{query}" - 대출 상품에 관심이 높은 고객군을 요청했습니다.',
            "target_description": "신용도가 양호하고 안정적인 소득을 보유한 대출 가능 고객군",
            "recommended_columns": [
                {
                    "column": "sc_int_loan1stfinancial",
                    "description": "1금융권 신용대출 예측스코어",
                    "condition": "> 0.7",
                    "priority": "high",
                    "reasoning": "1금융권 대출 가능성이 높은 우량 고객"
                }
            ],
            "sql_query": "SELECT * FROM cdp_customer WHERE sc_int_loan1stfinancial > 0.7",
            "business_insights": ["고소득층 대출 수요 증가", "신용대출 시장 확대"],
            "estimated_target_size": "15-20%",
            "marketing_recommendations": ["맞춤형 대출 상품 제안", "우대 금리 혜택 제공"]
        }
    else:
        return {
            "query_analysis": f'"{query}"에 대한 분석을 수행했습니다.',
            "target_description": "요청하신 조건에 맞는 고객군",
            "recommended_columns": [],
            "sql_query": "SELECT * FROM cdp_customer LIMIT 100",
            "business_insights": ["추가 분석 필요"],
            "estimated_target_size": "10-15%",
            "marketing_recommendations": ["맞춤형 마케팅 전략 수립"]
        }

def show_thinking_process():
    """AI 사고 과정 시각화"""
    thinking_steps = [
        "🎯 질문 분석 결과",
        "👥 타겟 고객군 정의", 
        "📊 추천 CDP 컬럼 조합",
        "🧠 AI 분석 근거",
        "📝 실행 가능한 SQL 쿼리",
        "💡 비즈니스 인사이트 & 마케팅 활용방안"
    ]
    
    progress_placeholder = st.empty()
    
    for i, step in enumerate(thinking_steps):
        with progress_placeholder.container():
            progress = (i + 1) / len(thinking_steps)
            st.progress(progress)
            st.markdown(f"### {step}")
            time.sleep(0.5)
    
    progress_placeholder.empty()

# 메인 UI
st.title("🤖 CDP AI 자연어 쿼리 플랫폼")
st.markdown("AI가 단계별로 분석하여 최적의 고객 세그먼테이션 전략을 추천합니다")

# 탭 생성
tab1, tab2, tab3, tab4 = st.tabs(["🔍 쿼리 분석기", "📚 컬럼 브라우저", "👥 팀별 추천", "📨 Notitest 메시지"])

with tab1:
    # 쿼리 입력
    col1, col2 = st.columns([5, 1])
    with col1:
        query = st.text_input(
            "자연어로 질문해주세요",
            placeholder="예: 대출 니즈가 높은 고객군 알려줘, 젊은 여성 중 뷰티 관심사가 높은 고객 찾아줘"
        )
    with col2:
        analyze_button = st.button("🔍 AI 분석", type="primary", use_container_width=True)
    
    # 분석 실행
    if analyze_button and query:
        with st.spinner("AI가 분석 중입니다..."):
            # 사고 과정 표시
            show_thinking_process()
            
            # API 호출
            result = st.session_state.analysis_results = generate_fallback_result(query)
            
            # 고급 태그 추출 및 Notitest 메시지 생성
            st.session_state.advanced_tags = st.session_state.noti_generator.extract_advanced_tags(result, query)
            st.session_state.noti_messages = st.session_state.noti_generator.generate_advanced_messages(
                st.session_state.advanced_tags, result
            )
            
            # A/B 테스트 설정 생성
            test_params = {'duration': 7, 'ratio': 20, 'baseline_rate': 0.02, 'mde': 0.2}
            st.session_state.ab_test_config = st.session_state.noti_generator.create_ab_test_config(
                st.session_state.noti_messages, test_params
            )
            
            # 성과 예측 생성
            st.session_state.performance_predictions = st.session_state.noti_generator.generate_performance_prediction(
                st.session_state.noti_messages
            )
        
        # 결과 표시
        st.markdown("---")
        
        # 1. 질문 분석 결과
        with st.container():
            st.markdown("### 🎯 질문 분석 결과")
            st.info(result['query_analysis'])
        
        # 2. 타겟 고객군 정의
        with st.container():
            st.markdown("### 👥 타겟 고객군 정의")
            st.write(result['target_description'])
            
            # 통계 카드
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("추천 컬럼 수", len(result['recommended_columns']))
            with col2:
                st.metric("예상 타겟 규모", result['estimated_target_size'])
            with col3:
                st.metric("마케팅 제안", len(result['marketing_recommendations']))
        
        # 3. 추천 CDP 컬럼 조합
        with st.container():
            st.markdown("### 📊 추천 CDP 컬럼 조합")
            for col in result['recommended_columns']:
                with st.expander(f"{col['column']} - {col['priority'].upper()}"):
                    st.write(f"**설명:** {col['description']}")
                    st.write(f"**조건:** `{col['condition']}`")
                    st.write(f"**선택 이유:** {col['reasoning']}")
        
        # 4. SQL 쿼리
        with st.container():
            st.markdown("### 📝 실행 가능한 SQL 쿼리")
            st.code(result['sql_query'], language='sql')
            st.button("📋 쿼리 복사", key="copy_sql")
        
        # 5. 비즈니스 인사이트
        with st.container():
            st.markdown("### 💡 비즈니스 인사이트")
            for insight in result['business_insights']:
                st.write(f"• {insight}")
        
        # 6. 마케팅 활용 방안
        with st.container():
            st.markdown("### 🚀 마케팅 활용 방안")
            for rec in result['marketing_recommendations']:
                st.write(f"• {rec}")

with tab2:
    st.markdown("### 📚 CDP 컬럼 브라우저")
    st.write("전체 CDP 컬럼을 카테고리별로 탐색할 수 있습니다.")
    
    # 필터 버튼
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("전체", use_container_width=True):
            filter_category = 'all'
    with col2:
        if st.button("관심사", use_container_width=True):
            filter_category = 'interests'
    with col3:
        if st.button("예측스코어", use_container_width=True):
            filter_category = 'scores'
    with col4:
        if st.button("플래그", use_container_width=True):
            filter_category = 'flags'
    
    # 검색
    search_term = st.text_input("컬럼 검색", placeholder="컬럼명이나 설명으로 검색...")
    
    # 컬럼 표시
    for category, columns in CDP_COLUMNS.items():
        if filter_category == 'all' or filter_category == category:
            st.markdown(f"#### {category.upper()}")
            for col_name, col_info in columns.items():
                if not search_term or search_term.lower() in col_name.lower() or search_term.lower() in col_info['desc'].lower():
                    with st.expander(col_name):
                        st.write(f"**타입:** {col_info['type']}")
                        st.write(f"**설명:** {col_info['desc']}")

with tab3:
    st.markdown("### 👥 팀별 맞춤 추천 질문")
    st.write("각 담당자님의 업무 영역에 특화된 질문들을 추천드립니다.")
    
    # 팀 선택
    selected_team = st.selectbox("담당자 선택", list(TEAM_QUESTIONS.keys()))
    
    # 추천 질문 표시
    if selected_team:
        st.markdown(f"#### {selected_team}")
        for question in TEAM_QUESTIONS[selected_team]:
            col1, col2 = st.columns([5, 1])
            with col1:
                st.info(question)
            with col2:
                if st.button("사용", key=f"use_{question[:10]}"):
                    st.session_state.query = question
                    st.experimental_rerun()

with tab4:
    st.markdown("### 📨 Notitest 고급 메시지 생성")
    st.write("AI 분석 결과를 기반으로 페르소나별 맞춤 메시지와 A/B 테스트를 자동 생성합니다.")
    
    if st.session_state.noti_messages and st.session_state.ab_test_config:
        # 태그 분석 결과
        st.markdown("#### 🏷️ 고급 태그 분석")
        
        if hasattr(st.session_state, 'advanced_tags'):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**주요 태그 (Primary)**")
                for tag in st.session_state.advanced_tags.get('primary', []):
                    st.markdown(f'<span class="noti-tag" style="background: #e8f5e8; color: #2e7d32;">{tag}</span>', unsafe_allow_html=True)
            
            with col2:
                st.markdown("**보조 태그 (Secondary)**")
                for tag in st.session_state.advanced_tags.get('secondary', []):
                    st.markdown(f'<span class="noti-tag" style="background: #e3f2fd; color: #1976d2;">{tag}</span>', unsafe_allow_html=True)
        
        # A/B 테스트 메시지 비교
        st.markdown("#### 🔬 A/B 테스트 메시지 비교")
        
        control_messages = [msg for msg in st.session_state.noti_messages if msg['test_group'] == 'A']
        test_messages = [msg for msg in st.session_state.noti_messages if msg['test_group'] == 'B']
        
        for i, (control, test) in enumerate(zip(control_messages, test_messages)):
            with st.expander(f"테스트 세트 {i+1}: {control['category'].upper()}", expanded=True):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**🅰️ 컨트롤 그룹 (기본)**")
                    st.markdown(f'<div class="noti-message">{control["message"]}</div>', unsafe_allow_html=True)
                    st.write(f"📱 **채널:** {control['channel']}")
                    st.write(f"👤 **페르소나:** {control['persona']}")
                    st.write(f"⏰ **최적 시간:** {control['timing']['best_time']}")
                
                with col2:
                    st.markdown(f"**🅱️ 테스트 그룹 ({test['variation']})**")
                    st.markdown(f'<div class="noti-message">{test["message"]}</div>', unsafe_allow_html=True)
                    st.write(f"📱 **채널:** {test['channel']}")
                    st.write(f"👤 **페르소나:** {test['persona']}")
                    st.write(f"⏰ **최적 시간:** {test['timing']['best_time']}")
        
        # 성과 예측
        if st.session_state.performance_predictions:
            st.markdown("#### 📊 AI 성과 예측")
            
            predictions = st.session_state.performance_predictions
            summary = predictions['summary']
            
            # 요약 지표
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("평균 오픈율", f"{summary['avg_open_rate']*100:.1f}%")
            with col2:
                st.metric("평균 클릭률", f"{summary['avg_click_rate']*100:.1f}%")
            with col3:
                st.metric("평균 전환율", f"{summary['avg_conversion_rate']*100:.1f}%")
            with col4:
                st.metric("최고 성과 변형", summary['best_performing_variation'])
            
            # 상세 예측 데이터프레임
            prediction_df = pd.DataFrame(predictions['predictions'])
            prediction_df['예상 오픈율(%)'] = prediction_df['predicted_open_rate'] * 100
            prediction_df['예상 클릭률(%)'] = prediction_df['predicted_click_rate'] * 100
            prediction_df['예상 전환율(%)'] = prediction_df['predicted_conversion_rate'] * 100
            
            st.markdown("**상세 예측 결과**")
            st.dataframe(
                prediction_df[['category', 'channel', 'variation', '예상 오픈율(%)', '예상 클릭률(%)', '예상 전환율(%)']],
                use_container_width=True
            )
            
            # 채널별 성과 비교 차트
            channel_performance = prediction_df.groupby('channel').agg({
                'predicted_open_rate': 'mean',
                'predicted_click_rate': 'mean',
                'predicted_conversion_rate': 'mean'
            }).reset_index()
            
            fig = go.Figure()
            fig.add_trace(go.Bar(
                name='오픈율',
                x=channel_performance['channel'],
                y=channel_performance['predicted_open_rate'] * 100,
                marker_color='#4CAF50'
            ))
            fig.add_trace(go.Bar(
                name='클릭률',
                x=channel_performance['channel'],
                y=channel_performance['predicted_click_rate'] * 100,
                marker_color='#2196F3'
            ))
            fig.add_trace(go.Bar(
                name='전환율',
                x=channel_performance['channel'],
                y=channel_performance['predicted_conversion_rate'] * 100,
                marker_color='#FF9800'
            ))
            
            fig.update_layout(
                title="채널별 예상 성과 비교",
                xaxis_title="채널",
                yaxis_title="비율 (%)",
                barmode='group',
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # A/B 테스트 설정
        st.markdown("#### 🧪 A/B 테스트 실행 설정")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            test_ratio = st.slider("테스트 그룹 비율", 10, 50, 20, step=5)
        with col2:
            test_duration = st.number_input("테스트 기간 (일)", 1, 30, 7)
        with col3:
            min_sample_size = st.number_input("최소 샘플 수", 1000, 100000, 10000, step=1000)
        
        # 테스트 설정 요약
        test_config = st.session_state.ab_test_config
        st.markdown("**테스트 구성 요약**")
        
        config_col1, config_col2 = st.columns(2)
        with config_col1:
            st.write(f"🆔 **테스트 ID:** {test_config['test_id']}")
            st.write(f"📊 **총 변형 수:** {test_config['total_variations']}")
            st.write(f"👥 **예상 샘플 크기:** {test_config['estimated_sample_size']:,}명")
        
        with config_col2:
            st.write(f"📈 **통계적 검정력:** {test_config['statistical_power']*100}%")
            st.write(f"🎯 **신뢰도:** {test_config['confidence_level']*100}%")
            st.write(f"⏱️ **테스트 기간:** {test_config['test_duration_days']}일")
        
        # Notitest 발송 버튼
        st.markdown("#### 🚀 Notitest 캠페인 실행")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.info("모든 설정이 완료되었습니다. 아래 버튼을 클릭하여 Notitest로 캠페인을 전송하세요.")
        
        with col2:
            if st.button("📨 캠페인 실행", type="primary", use_container_width=True):
                with st.spinner("Notitest API로 전송 중..."):
                    # 실제 API 호출
                    response = st.session_state.noti_generator.send_to_notitest(
                        st.session_state.noti_messages,
                        test_config
                    )
                    
                    if response['status'] == 'success':
                        st.success(f"✅ 캠페인이 성공적으로 생성되었습니다!")
                        st.write(f"**캠페인 ID:** {response['campaign_id']}")
                        st.write(f"**예상 도달 수:** {response['estimated_reach']:,}명")
                        st.write(f"**시작 시간:** {response['scheduled_start'][:19]}")
                    else:
                        st.error(f"❌ 캠페인 생성 실패: {response['message']}")
        
        # 다운로드 옵션
        st.markdown("#### 📥 결과 다운로드")
        
        download_col1, download_col2, download_col3 = st.columns(3)
        
        with download_col1:
            messages_json = json.dumps(st.session_state.noti_messages, ensure_ascii=False, indent=2)
            st.download_button(
                label="💬 메시지 다운로드",
                data=messages_json,
                file_name=f"notitest_messages_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )
        
        with download_col2:
            config_json = json.dumps(test_config, ensure_ascii=False, indent=2)
            st.download_button(
                label="⚙️ 테스트 설정 다운로드",
                data=config_json,
                file_name=f"ab_test_config_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )
        
        with download_col3:
            predictions_json = json.dumps(st.session_state.performance_predictions, ensure_ascii=False, indent=2)
            st.download_button(
                label="📊 성과 예측 다운로드",
                data=predictions_json,
                file_name=f"performance_predictions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )
    
    else:
        st.info("🔍 먼저 쿼리 분석을 실행하면 고급 태그 분석과 A/B 테스트 메시지가 자동으로 생성됩니다.")
        
        # 샘플 결과 미리보기
        with st.expander("📋 기능 미리보기", expanded=False):
            st.markdown("""
            **🎯 주요 기능:**
            1. **고급 태그 추출**: 주요/보조 태그 분류 및 우선순위 설정
            2. **페르소나 기반 메시지**: 고객 세그먼트별 맞춤 메시지 생성
            3. **A/B 테스트 자동화**: 다양한 변형 메시지 자동 생성
            4. **성과 예측**: AI 기반 캠페인 성과 사전 예측
            5. **채널 최적화**: 페르소나별 최적 발송 채널 추천
            6. **타이밍 최적화**: 카테고리별 최적 발송 시간 제안
            
            **🔬 A/B 테스트 변형:**
            - 이모지 강화 (emoji_heavy)
            - 긴급성 추가 (urgent)
            - 개인화 강화 (personalized)
            - 혜택 중심 (benefit_focused)
            - 사회적 증거 (social_proof)
            
            **📊 측정 지표:**
            - 오픈율 (Open Rate)
            - 클릭률 (Click Rate)
            - 전환율 (Conversion Rate)
            - 메시지당 수익 (Revenue per Message)
            """)

# 사이드바
with st.sidebar:
    st.markdown("### ⚙️ 설정")
    
    # API 설정
    with st.expander("API 설정"):
        api_key = st.text_input("OpenAI API Key", type="password", value=OPENAI_API_KEY[:20] + "...")
        model = st.selectbox("GPT 모델", ["gpt-3.5-turbo", "gpt-4", "o3-mini-2025-01-31"])
    
    # Notitest 설정
    with st.expander("Notitest 설정"):
        noti_api_endpoint = st.text_input("Notitest API Endpoint", value="https://api.notitest.com/v1/messages")
        noti_api_key = st.text_input("Notitest API Key", type="password")
        
    # 내보내기
    st.markdown("### 📤 내보내기")
    if st.session_state.analysis_results:
        # JSON 내보내기
        if st.button("분석 결과 JSON 다운로드"):
            json_str = json.dumps(st.session_state.analysis_results, ensure_ascii=False, indent=2)
            st.download_button(
                label="💾 다운로드",
                data=json_str,
                file_name=f"cdp_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
        
        # SQL 내보내기
        if st.button("SQL 쿼리 다운로드"):
            sql_content = st.session_state.analysis_results.get('sql_query', '')
            st.download_button(
                label="💾 다운로드",
                data=sql_content,
                file_name=f"cdp_query_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql",
                mime="text/plain"
            )