import streamlit as st
import openai
import json
import pandas as pd
from datetime import datetime
import time
import os
from typing import Dict, List, Any

# 페이지 설정
st.set_page_config(
    page_title="CDP AI 자연어 쿼리 & 마케팅 메시지 플랫폼",
    page_icon="🤖",
    layout="wide"
)

# OpenAI 설정
# Streamlit Cloud에서는 st.secrets 사용, 로컬에서는 환경변수 사용
try:
    openai.api_key = st.secrets["OPENAI_API_KEY"]
except:
    openai.api_key = os.getenv("OPENAI_API_KEY")

if not openai.api_key:
    st.error("OpenAI API 키가 설정되지 않았습니다. 환경변수나 Streamlit secrets를 확인해주세요.")
    st.stop()

# CDP 컬럼 정의
CDP_COLUMNS = {
    "interests": {
        'fa_int_householdsingle': {'desc': '1인 가구 관련 상품 결제 또는 오피스텔/원룸 거주 추정 고객', 'type': 'date'},
        'fa_int_householdpet': {'desc': '반려동물 관련 상품 결제 고객', 'type': 'date'},
        'fa_int_householdchild': {'desc': '어린이 관련 상품 결제 고객', 'type': 'date'},
        'fa_int_householdbaby': {'desc': '영유아 관련 상품 결제 또는 출산 정책지원금 수령 고객', 'type': 'date'},
        'fa_int_loan1stfinancial': {'desc': '1금융권에서 신용 대출 실행 고객', 'type': 'date'},
        'fa_int_loan2ndfinancial': {'desc': '저축은행, 카드사, 보험사, 증권사 등에서 신용 대출 실행 고객', 'type': 'date'},
        'fa_int_loanpersonal': {'desc': '신용대출을 실행 고객', 'type': 'date'},
        'fa_int_luxury': {'desc': '100만원 이상 명품관련 결제 고객', 'type': 'date'},
        'fa_int_traveloverseas': {'desc': '향후 1개월 내 해외 여행 목적의 출국 예정 추정 고객', 'type': 'date'},
        'fa_int_golf': {'desc': '골프용품/골프장 관련 상품 결제 고객', 'type': 'date'},
        'fa_int_gym': {'desc': '피트니스/헬스장 가맹점 결제 고객', 'type': 'date'},
        'fa_int_wedding': {'desc': '결혼 준비 관련 상품 결제 및 활동 발생 고객', 'type': 'date'},
    },
    "industries": {
        'fa_ind_beauty': {'desc': '미용 서비스 결제 이력', 'type': 'date'},
        'fa_ind_travel': {'desc': '여행 관련 결제 이력', 'type': 'date'},
        'fa_ind_airsevice': {'desc': '항공 서비스 이용', 'type': 'date'},
        'fa_ind_food': {'desc': '음식점 결제 이력', 'type': 'date'},
        'fa_ind_shopping': {'desc': '쇼핑 관련 결제 이력', 'type': 'date'},
    },
    "scores": {
        'sc_int_loan1stfinancial': {'desc': '1금융권 신용대출 예측스코어', 'type': 'double'},
        'sc_int_highincome': {'desc': '고소득 예측스코어', 'type': 'double'},
        'sc_ind_cosmetic': {'desc': '뷰티 제품 결제 예측스코어', 'type': 'double'},
        'sc_int_travel': {'desc': '여행 관심도 예측스코어', 'type': 'double'},
    },
    "flags": {
        'fi_npay_creditcheck': {'desc': '신용조회 서비스 가입 여부', 'type': 'boolean'},
        'fi_npay_genderf': {'desc': '여성 고객', 'type': 'boolean'},
        'fi_npay_age20': {'desc': '20대 연령층', 'type': 'boolean'},
        'fi_npay_premium': {'desc': '프리미엄 서비스 이용', 'type': 'boolean'},
    }
}

# 팀별 추천 질문
TEAM_QUESTIONS = {
    '금융 컨텐츠': [
        "재테크에 관심이 높은 젊은 직장인 고객군을 찾아줘",
        "부동산 투자에 관심있는 고소득층 고객은?",
        "연금/보험 가입 가능성이 높은 40대 고객 세그먼트는?"
    ],
    '회원 플래닝': [
        "이탈 위험이 높은 고객군의 특성을 분석해줘",
        "VIP 고객으로 성장 가능성이 높은 그룹을 찾아줘",
        "신규 가입 후 활성화가 필요한 고객들은?"
    ],
    '내자산 플래닝': [
        "자산관리 서비스에 관심이 높을 고객군을 추천해줘",
        "투자 포트폴리오 다변화가 필요한 고객은?",
        "목돈 마련이 필요한 신혼부부 고객군을 찾아줘"
    ],
    'AD 서비스': [
        "광고 클릭률이 높을 것으로 예상되는 고객 세그먼트는?",
        "프리미엄 상품 광고에 반응할 고소득층 고객을 찾아줘",
        "모바일 광고에 친화적인 젊은층 타겟을 추천해줘"
    ],
    '결제 데이터': [
        "결제 빈도가 급증한 고객 세그먼트를 찾아줘",
        "특정 업종에서 결제가 활발한 고객군은?",
        "온라인 결제를 선호하는 고객들의 특성은?"
    ],
    '대출 서비스': [
        "대출 신청 가능성이 높은 고객 세그먼트는?",
        "대환대출 니즈가 있는 고객들을 찾아줘",
        "주택담보대출을 고려할 만한 고객군은?"
    ]
}

# 마케팅 메시지 템플릿 (Notitest 연계)
MESSAGE_TEMPLATES = {
    "loan": {
        "tags": ["대출", "금융", "신용", "자금", "투자"],
        "noti_types": ["앱푸시", "SMS", "이메일"],
        "templates": [
            {
                "type": "urgency",
                "message": "🏦 {customer_trait}님만을 위한 특별 대출 상품! 한정 수량으로 {deadline}까지만 신청 가능합니다.",
                "cta": "지금 바로 확인하기",
                "timing": "오전 10시 또는 오후 2시"
            },
            {
                "type": "benefit",
                "message": "💰 {customer_trait}이신가요? 최저 {interest_rate}% 금리로 {max_amount}까지! {benefit} 혜택까지!",
                "cta": "금리 계산해보기",
                "timing": "점심시간 또는 퇴근시간"
            },
            {
                "type": "social_proof",
                "message": "📊 이미 {user_count}명의 고객이 선택한 인기 대출! {customer_trait}님도 지금 바로 신청하세요.",
                "cta": "고객 후기 보기",
                "timing": "저녁 8-9시"
            }
        ]
    },
    "beauty": {
        "tags": ["뷰티", "화장품", "미용", "스킨케어", "메이크업"],
        "noti_types": ["앱푸시", "카카오톡", "인스타그램"],
        "templates": [
            {
                "type": "trend",
                "message": "✨ 지금 인스타에서 핫한 {product_name}! {customer_trait}님 피부에 딱 맞는 {benefit} 효과!",
                "cta": "트렌드 확인하기",
                "timing": "오후 3-5시"
            },
            {
                "type": "seasonal",
                "message": "🌸 {season} 환절기 {customer_trait}님을 위한 맞춤 스킨케어! {discount}% 할인 + {gift} 증정",
                "cta": "세트 구성 보기",
                "timing": "저녁 7-8시"
            },
            {
                "type": "personal",
                "message": "💅 {customer_trait}님의 뷰티 루틴을 업그레이드! AI가 분석한 맞춤 {product_category} 추천",
                "cta": "AI 분석 받기",
                "timing": "오전 11시 또는 오후 8시"
            }
        ]
    },
    "travel": {
        "tags": ["여행", "휴가", "항공", "호텔", "패키지"],
        "noti_types": ["앱푸시", "이메일", "카카오톡"],
        "templates": [
            {
                "type": "limited_time",
                "message": "✈️ {destination} 항공료 {discount}% 폭락! {customer_trait}님이 찜한 일정, {seats_left}석만 남았어요!",
                "cta": "예약하러 가기",
                "timing": "오전 9시 또는 오후 6시"
            },
            {
                "type": "personalized",
                "message": "🏖️ {customer_trait}님의 여행 스타일 분석 완료! {destination} {duration} 맞춤 패키지 {price}부터",
                "cta": "맞춤 여행 보기",
                "timing": "주말 오전 10시"
            },
            {
                "type": "experience",
                "message": "🗺️ 지난번 {last_destination} 여행 어떠셨나요? 이번엔 {recommended_destination} 어떠세요?",
                "cta": "후기 남기고 할인받기",
                "timing": "목요일 저녁"
            }
        ]
    },
    "investment": {
        "tags": ["투자", "재테크", "적금", "펀드", "주식"],
        "noti_types": ["앱푸시", "SMS", "웹알림"],
        "templates": [
            {
                "type": "market_alert",
                "message": "📈 {customer_trait}님이 관심있는 {asset_type} {change_rate}% 상승! 지금이 기회일까요?",
                "cta": "시장 분석 보기",
                "timing": "장 마감 후"
            },
            {
                "type": "goal_based",
                "message": "🎯 {goal} 달성까지 {period} 남았어요! 월 {monthly_amount} 투자로 목표 달성 가능해요.",
                "cta": "투자 계획 보기",
                "timing": "월초 또는 급여일"
            }
        ]
    },
    "food": {
        "tags": ["음식", "배달", "맛집", "쿠폰"],
        "noti_types": ["앱푸시", "카카오톡"],
        "templates": [
            {
                "type": "craving",
                "message": "🍔 {customer_trait}님이 좋아하는 {cuisine_type} 생각나지 않나요? 지금 주문하면 {discount} 할인!",
                "cta": "메뉴 보러가기",
                "timing": "식사시간 30분 전"
            },
            {
                "type": "weather_based",
                "message": "☔ 비오는 날엔 따뜻한 {food_type}! {customer_trait}님 근처 인기 맛집 배달 {delivery_time}분",
                "cta": "지금 주문하기",
                "timing": "날씨 변화 시"
            }
        ]
    }
}

def analyze_with_ai(query: str, model: str = "gpt-4o-mini") -> Dict[str, Any]:
    """OpenAI API를 사용한 쿼리 분석"""
    try:
        # 시스템 프롬프트
        system_prompt = f"""당신은 CDP(Customer Data Platform) 전문가입니다. 
        사용자의 자연어 질문을 분석하여 최적의 고객 세그먼테이션 전략을 제공합니다.
        
        다음 CDP 컬럼들을 활용하여 분석해주세요:
        {json.dumps(CDP_COLUMNS, ensure_ascii=False, indent=2)}
        
        응답은 반드시 다음 JSON 형식으로 제공해주세요:
        {{
            "query_analysis": "사용자 질문 분석 내용",
            "target_description": "타겟 고객군 설명",
            "recommended_columns": [
                {{
                    "column": "컬럼명",
                    "description": "컬럼 설명",
                    "condition": "추천 조건 (예: > 0.7, IS NOT NULL 등)",
                    "priority": "high|medium|low",
                    "reasoning": "선택 이유"
                }}
            ],
            "sql_query": "SELECT 문으로 된 쿼리",
            "business_insights": ["비즈니스 인사이트 1", "비즈니스 인사이트 2"],
            "estimated_target_size": "예상 타겟 규모 (%)",
            "marketing_recommendations": ["마케팅 추천사항 1", "마케팅 추천사항 2"],
            "target_tags": ["태그1", "태그2", "태그3"],
            "customer_traits": ["특성1", "특성2"]
        }}"""
        
        # API 호출
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ],
            temperature=0.7,
            max_tokens=2000 if "o3-mini" not in model else None,
            max_completion_tokens=2000 if "o3-mini" in model else None
        )
        
        # 응답 파싱
        result = json.loads(response.choices[0].message.content)
        return result
        
    except Exception as e:
        st.error(f"AI 분석 중 오류 발생: {str(e)}")
        # 폴백 응답
        return generate_fallback_response(query)

def generate_fallback_response(query: str) -> Dict[str, Any]:
    """API 실패 시 폴백 응답 생성"""
    if "대출" in query:
        return {
            "query_analysis": f'"{query}" - 대출 관련 고객 세그먼트를 요청하셨습니다.',
            "target_description": "대출 니즈가 높은 신용 우량 고객군",
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
            "business_insights": ["대출 니즈가 높은 고객 발굴 가능"],
            "estimated_target_size": "15-20%",
            "marketing_recommendations": ["맞춤형 대출 상품 제안"],
            "target_tags": ["대출", "금융", "신용우량"],
            "customer_traits": ["안정적 소득", "신용도 우수"]
        }
    return {
        "query_analysis": f'"{query}"에 대한 분석',
        "target_description": "요청하신 고객군",
        "recommended_columns": [],
        "sql_query": "SELECT * FROM cdp_customer LIMIT 100",
        "business_insights": ["추가 분석 필요"],
        "estimated_target_size": "10-15%",
        "marketing_recommendations": ["맞춤 전략 수립 필요"],
        "target_tags": ["일반"],
        "customer_traits": ["분석 필요"]
    }

def generate_marketing_message(tags: List[str], traits: List[str], segment_info: Dict) -> Dict[str, Any]:
    """태그 기반 마케팅 메시지 생성 (Notitest 연계)"""
    
    # 관련 템플릿 찾기
    relevant_categories = []
    for category, data in MESSAGE_TEMPLATES.items():
        if any(tag in data["tags"] for tag in tags):
            relevant_categories.append(category)
    
    if not relevant_categories:
        relevant_categories = ["loan"]  # 기본값
    
    # 각 카테고리별 메시지 생성
    all_messages = []
    noti_recommendations = {}
    
    for category in relevant_categories[:2]:  # 최대 2개 카테고리
        template_data = MESSAGE_TEMPLATES[category]
        
        for template in template_data["templates"]:
            # 동적 변수 생성
            variables = generate_dynamic_variables(category, traits, segment_info)
            
            try:
                # 메시지 생성
                message = template["message"].format(**variables)
                cta = template["cta"]
                
                all_messages.append({
                    "category": category,
                    "type": template["type"],
                    "message": message,
                    "cta": cta,
                    "timing": template["timing"],
                    "channels": template_data["noti_types"],
                    "tags": tags,
                    "effectiveness_score": calculate_effectiveness_score(template["type"], tags, traits),
                    "variables": variables
                })
                
            except KeyError as e:
                # 변수가 없는 경우 기본값으로 처리
                st.warning(f"메시지 생성 중 변수 오류: {e}")
                continue
        
        # 알림 추천 정보
        noti_recommendations[category] = {
            "channels": template_data["noti_types"],
            "frequency": "주 2-3회",
            "ab_test": True
        }
    
    return {
        "messages": all_messages[:5],  # 최대 5개 메시지
        "noti_recommendations": noti_recommendations,
        "personalization_level": "매우 높음",
        "estimated_ctr": f"{calculate_estimated_ctr(tags, traits):.1f}%",
        "recommended_testing": generate_ab_test_plan(all_messages[:3])
    }

def generate_dynamic_variables(category: str, traits: List[str], segment_info: Dict) -> Dict[str, str]:
    """카테고리별 동적 변수 생성"""
    base_variables = {
        "customer_trait": traits[0] if traits else "고객",
        "benefit": "특별한 혜택",
        "product_name": "추천 상품",
        "season": "이번 시즌"
    }
    
    if category == "loan":
        base_variables.update({
            "interest_rate": "2.9",
            "max_amount": "5,000만원",
            "deadline": "이번 주말",
            "user_count": "10,000",
            "credit_grade": "우수"
        })
    elif category == "beauty":
        base_variables.update({
            "product_category": "스킨케어",
            "discount": "30",
            "gift": "미니 세트"
        })
    elif category == "travel":
        base_variables.update({
            "destination": "제주도",
            "duration": "2박3일",
            "price": "99,000원",
            "seats_left": "3",
            "last_destination": "부산",
            "recommended_destination": "강릉"
        })
    elif category == "investment":
        base_variables.update({
            "asset_type": "국내주식",
            "change_rate": "5.2",
            "goal": "내 집 마련",
            "period": "2년",
            "monthly_amount": "50만원"
        })
    elif category == "food":
        base_variables.update({
            "cuisine_type": "한식",
            "food_type": "찌개",
            "discount": "20%",
            "delivery_time": "25"
        })
    
    return base_variables

def calculate_effectiveness_score(message_type: str, tags: List[str], traits: List[str]) -> float:
    """메시지 유형별 효과 점수 계산"""
    base_score = 0.7
    
    # 메시지 유형별 가중치
    type_weights = {
        "urgency": 0.85,
        "benefit": 0.80,
        "social_proof": 0.75,
        "trend": 0.82,
        "seasonal": 0.78,
        "personal": 0.88,
        "limited_time": 0.86,
        "personalized": 0.90,
        "experience": 0.84,
        "market_alert": 0.79,
        "goal_based": 0.83,
        "craving": 0.81,
        "weather_based": 0.77
    }
    
    # 태그 매칭 보너스
    tag_bonus = min(len(tags) * 0.02, 0.1)
    
    # 개인화 수준 보너스
    personalization_bonus = len(traits) * 0.01
    
    final_score = base_score * type_weights.get(message_type, 0.75) + tag_bonus + personalization_bonus
    return min(final_score, 0.95)

def calculate_estimated_ctr(tags: List[str], traits: List[str]) -> float:
    """예상 클릭률 계산"""
    base_ctr = 3.5  # 기본 CTR 3.5%
    
    # 태그 개수에 따른 개인화 보너스
    personalization_bonus = len(tags) * 0.2
    
    # 고객 특성에 따른 보너스
    trait_bonus = len(traits) * 0.1
    
    return min(base_ctr + personalization_bonus + trait_bonus, 8.0)

def generate_ab_test_plan(messages: List[Dict]) -> Dict[str, Any]:
    """A/B 테스트 계획 생성"""
    if len(messages) < 2:
        return {"available": False, "reason": "최소 2개 메시지 필요"}
    
    return {
        "available": True,
        "test_groups": [
            {
                "group": "A",
                "percentage": 50,
                "message": messages[0]["message"],
                "type": messages[0]["type"]
            },
            {
                "group": "B", 
                "percentage": 50,
                "message": messages[1]["message"],
                "type": messages[1]["type"]
            }
        ],
        "metrics": ["오픈율", "클릭률", "전환율", "이탈률"],
        "duration": "2주",
        "sample_size": "최소 1,000명",
        "confidence_level": "95%"
    }

def main():
    st.title("🤖 CDP AI 자연어 쿼리 & 마케팅 메시지 플랫폼")
    st.markdown("AI가 고객 세그먼트를 분석하고 맞춤형 마케팅 메시지를 생성합니다")
    
    # 사이드바
    with st.sidebar:
        st.header("⚙️ 설정")
        selected_model = st.selectbox(
            "AI 모델 선택",
            ["gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"]
        )
        
        st.header("👥 팀별 추천 질문")
        selected_team = st.selectbox(
            "담당 팀 선택",
            list(TEAM_QUESTIONS.keys())
        )
        
        if st.button("추천 질문 보기"):
            st.write(f"**{selected_team} 추천 질문:**")
            for q in TEAM_QUESTIONS[selected_team]:
                if st.button(f"→ {q}", key=q):
                    st.session_state['query_input'] = q
    
    # 메인 컨텐츠
    tabs = st.tabs(["🔍 쿼리 분석", "📚 컬럼 브라우저", "💬 마케팅 메시지 생성"])
    
    with tabs[0]:
        # 쿼리 입력
        query = st.text_input(
            "자연어로 질문해주세요",
            value=st.session_state.get('query_input', ''),
            placeholder="예: 대출 니즈가 높은 고객군 알려줘"
        )
        
        col1, col2 = st.columns([1, 5])
        with col1:
            analyze_button = st.button("🔍 AI 분석", type="primary")
        
        if analyze_button and query:
            # 진행 상태 표시
            progress_placeholder = st.empty()
            results_placeholder = st.empty()
            
            with st.spinner("AI가 분석 중입니다..."):
                # 단계별 진행 상황 표시
                steps = [
                    "🎯 질문 분석 중...",
                    "👥 타겟 고객군 정의 중...",
                    "📊 CDP 컬럼 매핑 중...",
                    "🧠 분석 근거 도출 중...",
                    "📝 SQL 쿼리 생성 중...",
                    "💡 인사이트 도출 중..."
                ]
                
                progress_bar = st.progress(0)
                for i, step in enumerate(steps):
                    progress_placeholder.info(step)
                    progress_bar.progress((i + 1) / len(steps))
                    time.sleep(0.5)
                
                # AI 분석 실행
                result = analyze_with_ai(query, selected_model)
                
                # 세션에 저장
                st.session_state['analysis_result'] = result
                
            # 결과 표시
            progress_placeholder.empty()
            progress_bar.empty()
            
            with results_placeholder.container():
                # 질문 분석 결과
                st.success("✅ 분석 완료!")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("🎯 질문 분석 결과")
                    st.write(result["query_analysis"])
                    
                    st.subheader("👥 타겟 고객군 정의")
                    st.write(result["target_description"])
                    
                    # 통계
                    cols = st.columns(3)
                    cols[0].metric("추천 컬럼 수", len(result["recommended_columns"]))
                    cols[1].metric("예상 타겟 규모", result["estimated_target_size"])
                    cols[2].metric("마케팅 제안", len(result["marketing_recommendations"]))
                
                with col2:
                    st.subheader("📊 추천 CDP 컬럼 조합")
                    for col in result["recommended_columns"]:
                        with st.expander(f"{col['column']} - {col['priority']} 우선순위"):
                            st.write(f"**설명:** {col['description']}")
                            st.write(f"**조건:** `{col['condition']}`")
                            st.write(f"**이유:** {col['reasoning']}")
                
                # SQL 쿼리
                st.subheader("📝 실행 가능한 SQL 쿼리")
                st.code(result["sql_query"], language="sql")
                
                # 인사이트
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("💡 비즈니스 인사이트")
                    for insight in result["business_insights"]:
                        st.write(f"• {insight}")
                
                with col2:
                    st.subheader("🚀 마케팅 활용 방안")
                    for rec in result["marketing_recommendations"]:
                        st.write(f"• {rec}")
                
                # 태그
                st.subheader("🏷️ 추출된 태그")
                tag_cols = st.columns(len(result.get("target_tags", [])))
                for i, tag in enumerate(result.get("target_tags", [])):
                    tag_cols[i].info(f"#{tag}")
    
    with tabs[1]:
        st.header("📚 CDP 컬럼 브라우저")
        
        # 검색
        search_term = st.text_input("컬럼 검색", placeholder="컬럼명 또는 설명으로 검색")
        
        # 필터
        col1, col2, col3, col4 = st.columns(4)
        filters = {
            "관심사": col1.checkbox("관심사 (fa_int_*)"),
            "업종별": col2.checkbox("업종별 (fa_ind_*)"),
            "예측스코어": col3.checkbox("예측스코어 (sc_*)"),
            "플래그": col4.checkbox("플래그 (fi_npay_*)")
        }
        
        # 컬럼 표시
        for category, columns in CDP_COLUMNS.items():
            category_map = {
                "interests": "관심사",
                "industries": "업종별",
                "scores": "예측스코어",
                "flags": "플래그"
            }
            
            if not any(filters.values()) or filters.get(category_map.get(category, "")):
                st.subheader(f"{category_map.get(category, category)}")
                
                for col_name, col_info in columns.items():
                    if not search_term or search_term.lower() in col_name.lower() or search_term.lower() in col_info['desc'].lower():
                        with st.expander(f"{col_name} ({col_info['type']})"):
                            st.write(col_info['desc'])
                            st.code(f"WHERE {col_name} IS NOT NULL", language="sql")
    
    with tabs[2]:
        st.header("💬 마케팅 메시지 생성")
        
        if 'analysis_result' in st.session_state:
            result = st.session_state['analysis_result']
            
            st.info("🎯 분석된 고객 세그먼트를 기반으로 마케팅 메시지를 생성합니다")
            
            # 태그 표시
            st.subheader("추출된 태그")
            selected_tags = st.multiselect(
                "메시지 생성에 사용할 태그 선택",
                result.get("target_tags", ["일반"]),
                default=result.get("target_tags", ["일반"])
            )
            
            # 고객 특성
            st.subheader("고객 특성")
            traits = st.text_area(
                "고객 특성 입력 (쉼표로 구분)",
                value=", ".join(result.get("customer_traits", ["일반 고객"]))
            ).split(", ")
            
            # 메시지 유형 선택
            st.subheader("메시지 유형 선택")
            message_types = st.multiselect(
                "생성할 메시지 유형 선택",
                ["urgency", "benefit", "social_proof", "trend", "seasonal", "personal", "limited_time"],
                default=["benefit", "personal"]
            )
            
            # 알림 채널 선택
            st.subheader("알림 채널 설정")
            col1, col2, col3 = st.columns(3)
            channels = {
                "앱 푸시": col1.checkbox("앱 푸시", value=True),
                "SMS": col2.checkbox("SMS", value=True),
                "이메일": col3.checkbox("이메일", value=False),
                "카카오톡": col1.checkbox("카카오톡", value=False),
                "인스타그램": col2.checkbox("인스타그램", value=False)
            }
            selected_channels = [k for k, v in channels.items() if v]
            
            if st.button("💬 Notitest 연계 메시지 생성", type="primary"):
                with st.spinner("AI가 맞춤형 마케팅 메시지를 생성 중입니다..."):
                    time.sleep(1)  # 사용자 경험 향상
                    messages_data = generate_marketing_message(
                        selected_tags,
                        traits,
                        result
                    )
                
                # 생성된 메시지 표시
                st.success("✅ Notitest 연계 메시지 생성 완료!")
                
                # 성과 예측 요약
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("예상 CTR", messages_data["estimated_ctr"])
                col2.metric("개인화 수준", messages_data["personalization_level"])
                col3.metric("생성된 메시지", len(messages_data["messages"]))
                col4.metric("A/B 테스트", "가능" if messages_data["recommended_testing"]["available"] else "불가능")
                
                # 메시지 카드들
                st.subheader("🎯 생성된 마케팅 메시지")
                
                for i, msg in enumerate(messages_data["messages"]):
                    with st.expander(f"📩 메시지 {i+1}: {msg['type'].title()} 타입 ({msg['category']})"):
                        # 메시지 본문
                        st.markdown(f"""
                        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                                   color: white; padding: 20px; border-radius: 15px; margin: 10px 0;">
                            <h4 style="margin: 0 0 10px 0; color: white;">📱 {msg['type'].replace('_', ' ').title()} 메시지</h4>
                            <p style="font-size: 16px; margin: 10px 0; line-height: 1.4;">{msg['message']}</p>
                            <div style="background: rgba(255,255,255,0.2); padding: 10px; border-radius: 8px; margin-top: 15px;">
                                <strong>🎬 CTA:</strong> {msg['cta']}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # 메시지 상세 정보
                        col1, col2, col3, col4 = st.columns(4)
                        
                        col1.metric("효과 예상", f"{msg['effectiveness_score']*100:.0f}%")
                        col2.write("**📱 추천 채널**")
                        for ch in msg['channels']:
                            if ch in selected_channels:
                                col2.success(f"✅ {ch}")
                            else:
                                col2.write(f"• {ch}")
                        
                        col3.write("**⏰ 최적 발송 시간**")
                        col3.write(msg['timing'])
                        
                        col4.write("**🏷️ 관련 태그**")
                        for tag in msg['tags'][:3]:
                            col4.caption(f"#{tag}")
                        
                        # 변수 표시
                        with st.expander("🔧 사용된 변수들"):
                            st.json(msg['variables'])
                
                # Notitest 연계 정보
                st.subheader("🔔 Notitest 발송 설정")
                
                for category, noti_info in messages_data["noti_recommendations"].items():
                    with st.expander(f"📊 {category.title()} 카테고리 발송 설정"):
                        col1, col2, col3 = st.columns(3)
                        
                        col1.write("**📱 추천 채널**")
                        for ch in noti_info["channels"]:
                            col1.write(f"• {ch}")
                        
                        col2.write("**📅 발송 빈도**")
                        col2.write(noti_info["frequency"])
                        
                        col3.write("**🧪 A/B 테스트**")
                        col3.write("권장됨" if noti_info["ab_test"] else "불필요")
                
                # A/B 테스트 상세 계획
                if messages_data["recommended_testing"]["available"]:
                    st.subheader("🔬 A/B 테스트 상세 계획")
                    
                    test_plan = messages_data["recommended_testing"]
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write("**그룹 A (50%)**")
                        st.info(f"**타입:** {test_plan['test_groups'][0]['type']}")
                        st.write(test_plan['test_groups'][0]['message'])
                    
                    with col2:
                        st.write("**그룹 B (50%)**")
                        st.info(f"**타입:** {test_plan['test_groups'][1]['type']}")
                        st.write(test_plan['test_groups'][1]['message'])
                    
                    # 테스트 설정
                    st.write("**📊 테스트 설정**")
                    test_col1, test_col2, test_col3, test_col4 = st.columns(4)
                    test_col1.metric("기간", test_plan['duration'])
                    test_col2.metric("표본 크기", test_plan['sample_size'])
                    test_col3.metric("신뢰도", test_plan['confidence_level'])
                    test_col4.write("**측정 지표**")
                    for metric in test_plan['metrics']:
                        test_col4.write(f"• {metric}")
                    
                    # Notitest 연동 코드 예시
                    with st.expander("💻 Notitest API 연동 코드 예시"):
                        st.code(f"""
# Notitest API 연동 예시
import requests

# A/B 테스트 설정
ab_test_config = {{
    "test_name": "CDP_분석_기반_메시지_테스트",
    "groups": [
        {{
            "name": "A",
            "percentage": 50,
            "message": "{test_plan['test_groups'][0]['message'][:50]}...",
            "channels": {selected_channels}
        }},
        {{
            "name": "B", 
            "percentage": 50,
            "message": "{test_plan['test_groups'][1]['message'][:50]}...",
            "channels": {selected_channels}
        }}
    ],
    "target_segment": "{result.get('target_description', '분석된 고객군')}",
    "tags": {selected_tags},
    "duration_days": 14
}}

# Notitest API 호출
response = requests.post(
    "https://api.notitest.com/v1/campaigns/ab-test",
    headers={{"Authorization": "Bearer YOUR_API_KEY"}},
    json=ab_test_config
)

print(f"Campaign ID: {{response.json()['campaign_id']}}")
                        """, language="python")
                else:
                    st.warning("A/B 테스트를 위해서는 최소 2개 이상의 서로 다른 메시지가 필요합니다.")
        else:
            st.warning("먼저 쿼리 분석을 실행해주세요.")

if __name__ == "__main__":
    # 세션 상태 초기화
    if 'query_input' not in st.session_state:
        st.session_state['query_input'] = ''
    
    main()