import pandas as pd
import json

# 수동 태깅 예시를 위한 샘플 분석
sample_tags = {
    "(광고) 미뤄두었던 약관동의 완료하고 2023년 나의 신용분석 리포트 받으세요!": {
        "message_tone": "reminder",
        "call_to_action": "complete_action",
        "psychological_triggers": ["fomo", "benefit"],
        "content_elements": {
            "emoji_count": 0,
            "has_question": False,
            "has_numbers": True,
            "has_percentage": False,
            "has_time_reference": True,
            "has_arrow": False
        },
        "offer_type": "report",
        "target_emotion": "relief"
    },
    "(광고) 한도가 달라졌을까? 내 금리·한도 확인할 시간이에요👉": {
        "message_tone": "urgent",
        "call_to_action": "check_info",
        "psychological_triggers": ["curiosity", "urgency"],
        "content_elements": {
            "emoji_count": 1,
            "has_question": True,
            "has_numbers": False,
            "has_percentage": False,
            "has_time_reference": True,
            "has_arrow": True
        },
        "offer_type": "limit_check",
        "target_emotion": "curiosity"
    },
    "(광고) 대출 갈아타기 좋은 시간이 시작됐어요👉": {
        "message_tone": "persuasive",
        "call_to_action": "click_now",
        "psychological_triggers": ["urgency", "benefit"],
        "content_elements": {
            "emoji_count": 1,
            "has_question": False,
            "has_numbers": False,
            "has_percentage": False,
            "has_time_reference": True,
            "has_arrow": True
        },
        "offer_type": "refinancing",
        "target_emotion": "hope"
    },
    "(광고)⌛사전신청 마감임박! 주담대 이자 줄이고 최대 1️⃣만원도 받자>": {
        "message_tone": "urgent",
        "call_to_action": "click_now",
        "psychological_triggers": ["fomo", "urgency", "benefit"],
        "content_elements": {
            "emoji_count": 3,
            "has_question": False,
            "has_numbers": True,
            "has_percentage": False,
            "has_time_reference": True,
            "has_arrow": True
        },
        "offer_type": "event",
        "target_emotion": "excitement"
    }
}

def create_analysis_report():
    # CSV 데이터 로드
    df = pd.read_csv('/Users/user/Desktop/notitest/202507_.csv')
    
    # 상위 성과 문구 분석
    top_performers = df.nlargest(10, '클릭율')
    
    print("=== 수동 태깅 분석 결과 ===\n")
    print("1. 최고 성과 문구 분석:")
    print("-" * 80)
    
    for idx, row in top_performers.head(4).iterrows():
        text = row['발송 문구']
        ctr = row['클릭율']
        
        if text in sample_tags:
            tags = sample_tags[text]
            print(f"\n문구: {text}")
            print(f"클릭률: {ctr}%")
            print(f"태그 분석:")
            print(f"  - 메시지 톤: {tags['message_tone']}")
            print(f"  - 행동 유도: {tags['call_to_action']}")
            print(f"  - 심리 트리거: {', '.join(tags['psychological_triggers'])}")
            print(f"  - 타겟 감정: {tags['target_emotion']}")
            print(f"  - 이모지 수: {tags['content_elements']['emoji_count']}")
            print(f"  - 질문 포함: {'예' if tags['content_elements']['has_question'] else '아니오'}")
    
    print("\n\n2. 태그별 성과 패턴 (수동 분석 기반):")
    print("-" * 80)
    
    # 고성과 문구의 공통 패턴
    print("\n고성과 문구의 공통 특징:")
    print("• reminder 톤 + complete_action CTA = 최고 성과 (약관동의 리포트)")
    print("• urgent 톤 + 시간 관련 표현 = 높은 긴급성 전달")
    print("• 심리 트리거 중 'fomo'와 'urgency'가 가장 효과적")
    print("• 질문형 문구가 호기심 유발에 효과적")
    
    print("\n\n3. 서비스별 효과적인 태깅 전략:")
    print("-" * 80)
    
    service_strategies = {
        "신용점수조회": {
            "효과적인 톤": "reminder",
            "주요 CTA": "complete_action",
            "핵심 트리거": "fomo, benefit",
            "추천 감정": "relief"
        },
        "신용대환대출": {
            "효과적인 톤": "urgent, persuasive",
            "주요 CTA": "check_info, click_now",
            "핵심 트리거": "curiosity, urgency",
            "추천 감정": "hope, curiosity"
        },
        "주택담보대출비교": {
            "효과적인 톤": "urgent",
            "주요 CTA": "click_now",
            "핵심 트리거": "fomo, benefit",
            "추천 감정": "excitement"
        }
    }
    
    for service, strategy in service_strategies.items():
        print(f"\n{service}:")
        for key, value in strategy.items():
            print(f"  - {key}: {value}")
    
    print("\n\n4. LLM 태깅 활용 방안:")
    print("-" * 80)
    print("\n1) 자동 태깅 프로세스:")
    print("   - 모든 신규 문구를 LLM으로 자동 태깅")
    print("   - 태그별 성과 데이터 축적")
    print("   - 머신러닝 모델로 성과 예측")
    
    print("\n2) 문구 최적화:")
    print("   - 고성과 태그 조합 활용")
    print("   - A/B 테스트로 검증")
    print("   - 지속적인 개선")
    
    print("\n3) 실시간 추천 시스템:")
    print("   - 서비스/타겟별 최적 태그 조합 추천")
    print("   - 예상 클릭률 제시")
    print("   - 문구 자동 생성 가능")

if __name__ == "__main__":
    create_analysis_report()
    
    # 태깅 데이터 구조 예시 저장
    with open('/Users/user/Desktop/notitest/tagging_structure_example.json', 'w', encoding='utf-8') as f:
        json.dump(sample_tags, f, ensure_ascii=False, indent=2)
    
    print("\n\n태깅 구조 예시가 tagging_structure_example.json에 저장되었습니다.")