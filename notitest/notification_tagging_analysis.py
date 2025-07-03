import pandas as pd
import openai
import json
from typing import List, Dict
import asyncio
from tqdm import tqdm

class NotificationTagger:
    def __init__(self, api_key: str):
        self.client = openai.OpenAI(api_key=api_key)
        
    def create_tagging_prompt(self, notification_text: str) -> str:
        return f"""
다음 대출 관련 알림 문구를 분석하여 태그를 생성해주세요.

알림 문구: "{notification_text}"

다음 카테고리에 대해 JSON 형식으로 태그를 생성해주세요:

1. message_tone (메시지 톤)
   - urgent: 긴급성 강조
   - friendly: 친근한 톤
   - informative: 정보 제공형
   - persuasive: 설득형
   - reminder: 리마인더형

2. call_to_action (행동 유도)
   - click_now: 즉시 클릭 유도
   - check_info: 정보 확인 유도
   - complete_action: 미완료 작업 완료 유도
   - compare: 비교 유도
   - none: 행동 유도 없음

3. psychological_triggers (심리적 트리거)
   - fomo: 놓칠까봐 두려움
   - curiosity: 호기심 유발
   - benefit: 혜택 강조
   - personalization: 개인화
   - social_proof: 사회적 증거
   - urgency: 시간 압박
   - simplicity: 간단함 강조

4. content_elements (콘텐츠 요소)
   - emoji_count: 이모지 개수
   - has_question: 질문 포함 여부 (true/false)
   - has_numbers: 숫자 포함 여부 (true/false)
   - has_percentage: 퍼센트 포함 여부 (true/false)
   - has_time_reference: 시간 참조 포함 (true/false)
   - has_arrow: 화살표 포함 (true/false)

5. offer_type (제안 유형)
   - rate_check: 금리 확인
   - limit_check: 한도 확인
   - refinancing: 대환/갈아타기
   - new_loan: 신규 대출
   - report: 리포트/분석
   - event: 이벤트/혜택
   - none: 특정 제안 없음

6. target_emotion (타겟 감정)
   - anxiety: 불안감
   - hope: 희망
   - relief: 안도감
   - excitement: 흥분/기대감
   - trust: 신뢰감

JSON 형식으로만 응답해주세요.
"""

    def tag_notification(self, notification_text: str) -> Dict:
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "당신은 마케팅 문구 분석 전문가입니다."},
                    {"role": "user", "content": self.create_tagging_prompt(notification_text)}
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"Error tagging notification: {e}")
            return {}

    def batch_tag_notifications(self, df: pd.DataFrame, sample_size: int = 100) -> pd.DataFrame:
        """샘플 데이터에 대해 태깅 수행"""
        # 클릭률 기준으로 상위, 중위, 하위 그룹에서 샘플링
        df_sorted = df.sort_values('클릭율', ascending=False)
        
        # 각 그룹에서 샘플링
        n_per_group = sample_size // 3
        
        high_performers = df_sorted.head(len(df) // 3).sample(n=min(n_per_group, len(df) // 3))
        mid_performers = df_sorted[len(df) // 3:2 * len(df) // 3].sample(n=min(n_per_group, len(df) // 3))
        low_performers = df_sorted.tail(len(df) // 3).sample(n=min(n_per_group, len(df) // 3))
        
        sample_df = pd.concat([high_performers, mid_performers, low_performers])
        
        # 태깅 수행
        tags_list = []
        for _, row in tqdm(sample_df.iterrows(), total=len(sample_df), desc="Tagging notifications"):
            tags = self.tag_notification(row['발송 문구'])
            tags_list.append(tags)
        
        # 태그를 데이터프레임에 추가
        for key in ['message_tone', 'call_to_action', 'offer_type', 'target_emotion']:
            sample_df[f'tag_{key}'] = [tag.get(key, 'none') for tag in tags_list]
        
        # psychological_triggers는 리스트이므로 별도 처리
        sample_df['tag_psychological_triggers'] = [
            ','.join(tag.get('psychological_triggers', [])) for tag in tags_list
        ]
        
        # content_elements는 개별 컬럼으로 추가
        for element in ['emoji_count', 'has_question', 'has_numbers', 'has_percentage', 'has_time_reference', 'has_arrow']:
            sample_df[f'tag_{element}'] = [
                tag.get('content_elements', {}).get(element, 0 if element == 'emoji_count' else False) 
                for tag in tags_list
            ]
        
        return sample_df

def analyze_tag_performance(tagged_df: pd.DataFrame):
    """태그별 성과 분석"""
    print("\n=== 태그별 평균 클릭률 분석 ===\n")
    
    # 1. 메시지 톤별 분석
    print("1. 메시지 톤별 평균 클릭률:")
    tone_analysis = tagged_df.groupby('tag_message_tone')['클릭율'].agg(['mean', 'count']).sort_values('mean', ascending=False)
    print(tone_analysis)
    
    # 2. 행동 유도별 분석
    print("\n2. 행동 유도 유형별 평균 클릭률:")
    cta_analysis = tagged_df.groupby('tag_call_to_action')['클릭율'].agg(['mean', 'count']).sort_values('mean', ascending=False)
    print(cta_analysis)
    
    # 3. 제안 유형별 분석
    print("\n3. 제안 유형별 평균 클릭률:")
    offer_analysis = tagged_df.groupby('tag_offer_type')['클릭율'].agg(['mean', 'count']).sort_values('mean', ascending=False)
    print(offer_analysis)
    
    # 4. 타겟 감정별 분석
    print("\n4. 타겟 감정별 평균 클릭률:")
    emotion_analysis = tagged_df.groupby('tag_target_emotion')['클릭율'].agg(['mean', 'count']).sort_values('mean', ascending=False)
    print(emotion_analysis)
    
    # 5. 콘텐츠 요소별 분석
    print("\n5. 콘텐츠 요소별 평균 클릭률:")
    for element in ['has_question', 'has_numbers', 'has_percentage', 'has_time_reference', 'has_arrow']:
        element_col = f'tag_{element}'
        if element_col in tagged_df.columns:
            print(f"\n{element}:")
            element_analysis = tagged_df.groupby(element_col)['클릭율'].agg(['mean', 'count'])
            print(element_analysis)
    
    # 6. 심리적 트리거 분석 (각 트리거별로)
    print("\n6. 심리적 트리거별 평균 클릭률:")
    all_triggers = []
    for triggers in tagged_df['tag_psychological_triggers']:
        if triggers:
            all_triggers.extend(triggers.split(','))
    
    unique_triggers = set(all_triggers)
    trigger_performance = {}
    
    for trigger in unique_triggers:
        if trigger:
            mask = tagged_df['tag_psychological_triggers'].str.contains(trigger, na=False)
            trigger_performance[trigger] = {
                'mean_ctr': tagged_df[mask]['클릭율'].mean(),
                'count': mask.sum()
            }
    
    trigger_df = pd.DataFrame(trigger_performance).T.sort_values('mean_ctr', ascending=False)
    print(trigger_df)

def generate_insights(tagged_df: pd.DataFrame):
    """태깅 결과를 바탕으로 인사이트 생성"""
    print("\n=== 주요 인사이트 ===\n")
    
    # 상위 10% 클릭률 문구의 특징
    top_10_percent_threshold = tagged_df['클릭율'].quantile(0.9)
    top_performers = tagged_df[tagged_df['클릭율'] >= top_10_percent_threshold]
    
    print(f"1. 상위 10% 클릭률({top_10_percent_threshold:.2f}% 이상) 문구의 특징:")
    print(f"   - 가장 많이 사용된 메시지 톤: {top_performers['tag_message_tone'].mode().values[0] if len(top_performers) > 0 else 'N/A'}")
    print(f"   - 가장 많이 사용된 행동 유도: {top_performers['tag_call_to_action'].mode().values[0] if len(top_performers) > 0 else 'N/A'}")
    print(f"   - 평균 이모지 개수: {top_performers['tag_emoji_count'].mean():.1f}")
    print(f"   - 질문 포함 비율: {top_performers['tag_has_question'].mean()*100:.1f}%")
    
    # 서비스별 최적 전략
    print("\n2. 서비스별 최적 전략:")
    for service in tagged_df['서비스명'].unique():
        service_df = tagged_df[tagged_df['서비스명'] == service]
        if len(service_df) > 5:  # 충분한 샘플이 있는 경우만
            print(f"\n   {service}:")
            top_service = service_df.nlargest(5, '클릭율')
            print(f"   - 효과적인 메시지 톤: {top_service['tag_message_tone'].mode().values[0] if len(top_service) > 0 else 'N/A'}")
            print(f"   - 효과적인 타겟 감정: {top_service['tag_target_emotion'].mode().values[0] if len(top_service) > 0 else 'N/A'}")

# 사용 예시
if __name__ == "__main__":
    # 데이터 로드
    df = pd.read_csv('/Users/user/Desktop/notitest/202507_.csv')
    
    # API 키 설정 (실제 사용시 환경변수 등으로 관리)
    # tagger = NotificationTagger(api_key="your-api-key")
    
    # 샘플 태깅 수행
    # tagged_df = tagger.batch_tag_notifications(df, sample_size=100)
    
    # 결과 저장
    # tagged_df.to_csv('tagged_notifications.csv', index=False)
    
    # 성과 분석
    # analyze_tag_performance(tagged_df)
    
    # 인사이트 생성
    # generate_insights(tagged_df)
    
    print("분석 코드가 준비되었습니다. OpenAI API 키를 설정하고 주석을 해제하여 실행하세요.")