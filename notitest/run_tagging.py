import pandas as pd
import openai
import json
from typing import List, Dict
from tqdm import tqdm
import time

class NotificationTagger:
    def __init__(self, api_key: str):
        self.client = openai.OpenAI(api_key=api_key)
        
    def create_tagging_prompt(self, notification_text: str) -> str:
        return f"""
다음 대출 관련 알림 문구를 분석하여 태그를 생성해주세요.

알림 문구: "{notification_text}"

다음 카테고리에 대해 JSON 형식으로 태그를 생성해주세요:

1. message_tone (메시지 톤) - 하나만 선택
   - urgent: 긴급성 강조
   - friendly: 친근한 톤
   - informative: 정보 제공형
   - persuasive: 설득형
   - reminder: 리마인더형

2. call_to_action (행동 유도) - 하나만 선택
   - click_now: 즉시 클릭 유도
   - check_info: 정보 확인 유도
   - complete_action: 미완료 작업 완료 유도
   - compare: 비교 유도
   - none: 행동 유도 없음

3. psychological_triggers (심리적 트리거) - 여러 개 가능 (배열)
   - fomo: 놓칠까봐 두려움
   - curiosity: 호기심 유발
   - benefit: 혜택 강조
   - personalization: 개인화
   - social_proof: 사회적 증거
   - urgency: 시간 압박
   - simplicity: 간단함 강조

4. content_elements (콘텐츠 요소)
   - emoji_count: 이모지 개수 (정수)
   - has_question: 질문 포함 여부 (true/false)
   - has_numbers: 숫자 포함 여부 (true/false)
   - has_percentage: 퍼센트 포함 여부 (true/false)
   - has_time_reference: 시간 참조 포함 (true/false)
   - has_arrow: 화살표 포함 (true/false)

5. offer_type (제안 유형) - 하나만 선택
   - rate_check: 금리 확인
   - limit_check: 한도 확인
   - refinancing: 대환/갈아타기
   - new_loan: 신규 대출
   - report: 리포트/분석
   - event: 이벤트/혜택
   - none: 특정 제안 없음

6. target_emotion (타겟 감정) - 하나만 선택
   - anxiety: 불안감
   - hope: 희망
   - relief: 안도감
   - excitement: 흥분/기대감
   - trust: 신뢰감

JSON 형식으로만 응답해주세요.
"""

    def tag_notification(self, notification_text: str, max_retries: int = 3) -> Dict:
        for attempt in range(max_retries):
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
                print(f"Error on attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2)  # 재시도 전 대기
                else:
                    print(f"Failed to tag: {notification_text}")
                    return {}

    def batch_tag_notifications(self, df: pd.DataFrame, sample_size: int = 50) -> pd.DataFrame:
        """샘플 데이터에 대해 태깅 수행"""
        # 클릭률 기준으로 상위, 중위, 하위 그룹에서 샘플링
        df_sorted = df.sort_values('클릭율', ascending=False).reset_index(drop=True)
        
        # 각 그룹에서 샘플링
        n_per_group = sample_size // 3
        
        # 각 그룹의 크기 계산
        group_size = len(df) // 3
        
        high_performers = df_sorted.head(group_size).sample(n=min(n_per_group, group_size), random_state=42)
        mid_performers = df_sorted.iloc[group_size:2*group_size].sample(n=min(n_per_group, group_size), random_state=42)
        low_performers = df_sorted.tail(group_size).sample(n=min(n_per_group, group_size), random_state=42)
        
        sample_df = pd.concat([high_performers, mid_performers, low_performers]).reset_index(drop=True)
        
        print(f"샘플링 완료: 총 {len(sample_df)}개 문구")
        print(f"- 상위 그룹: {len(high_performers)}개")
        print(f"- 중위 그룹: {len(mid_performers)}개")
        print(f"- 하위 그룹: {len(low_performers)}개")
        
        # 태깅 수행
        tags_list = []
        for _, row in tqdm(sample_df.iterrows(), total=len(sample_df), desc="Tagging notifications"):
            tags = self.tag_notification(row['발송 문구'])
            tags_list.append(tags)
            time.sleep(0.5)  # API 호출 제한 방지
        
        # 태그를 데이터프레임에 추가
        for key in ['message_tone', 'call_to_action', 'offer_type', 'target_emotion']:
            sample_df[f'tag_{key}'] = [tag.get(key, 'none') if tag else 'none' for tag in tags_list]
        
        # psychological_triggers는 리스트이므로 별도 처리
        sample_df['tag_psychological_triggers'] = [
            ','.join(tag.get('psychological_triggers', [])) if tag else '' for tag in tags_list
        ]
        
        # content_elements는 개별 컬럼으로 추가
        for element in ['emoji_count', 'has_question', 'has_numbers', 'has_percentage', 'has_time_reference', 'has_arrow']:
            sample_df[f'tag_{element}'] = [
                tag.get('content_elements', {}).get(element, 0 if element == 'emoji_count' else False) if tag else (0 if element == 'emoji_count' else False)
                for tag in tags_list
            ]
        
        return sample_df

def analyze_tag_performance(tagged_df: pd.DataFrame):
    """태그별 성과 분석"""
    print("\n=== 태그별 평균 클릭률 분석 ===\n")
    
    # 1. 메시지 톤별 분석
    print("1. 메시지 톤별 평균 클릭률:")
    tone_analysis = tagged_df.groupby('tag_message_tone')['클릭율'].agg(['mean', 'count']).round(2).sort_values('mean', ascending=False)
    print(tone_analysis)
    
    # 2. 행동 유도별 분석
    print("\n2. 행동 유도 유형별 평균 클릭률:")
    cta_analysis = tagged_df.groupby('tag_call_to_action')['클릭율'].agg(['mean', 'count']).round(2).sort_values('mean', ascending=False)
    print(cta_analysis)
    
    # 3. 제안 유형별 분석
    print("\n3. 제안 유형별 평균 클릭률:")
    offer_analysis = tagged_df.groupby('tag_offer_type')['클릭율'].agg(['mean', 'count']).round(2).sort_values('mean', ascending=False)
    print(offer_analysis)
    
    # 4. 타겟 감정별 분석
    print("\n4. 타겟 감정별 평균 클릭률:")
    emotion_analysis = tagged_df.groupby('tag_target_emotion')['클릭율'].agg(['mean', 'count']).round(2).sort_values('mean', ascending=False)
    print(emotion_analysis)
    
    # 5. 콘텐츠 요소별 분석
    print("\n5. 콘텐츠 요소별 평균 클릭률:")
    for element in ['has_question', 'has_numbers', 'has_percentage', 'has_time_reference', 'has_arrow']:
        element_col = f'tag_{element}'
        if element_col in tagged_df.columns:
            print(f"\n{element}:")
            element_analysis = tagged_df.groupby(element_col)['클릭율'].agg(['mean', 'count']).round(2)
            print(element_analysis)

def main():
    print("=== 대출 알림 문구 LLM 태깅 시작 ===\n")
    
    # API 키 설정
    api_key = "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"
    
    # 데이터 로드
    print("데이터 로딩 중...")
    df = pd.read_csv('/Users/user/Desktop/notitest/202507_.csv')
    print(f"총 {len(df)}개의 알림 데이터 로드 완료")
    
    # 태거 초기화
    tagger = NotificationTagger(api_key=api_key)
    
    # 샘플 태깅 수행 (50개)
    print("\n태깅 시작...")
    tagged_df = tagger.batch_tag_notifications(df, sample_size=50)
    
    # 결과 저장
    output_filename = 'tagged_notifications_sample.csv'
    tagged_df.to_csv(f'/Users/user/Desktop/notitest/{output_filename}', index=False, encoding='utf-8-sig')
    print(f"\n태깅 결과 저장 완료: {output_filename}")
    
    # 성과 분석
    analyze_tag_performance(tagged_df)
    
    # 간단한 인사이트
    print("\n=== 주요 인사이트 ===")
    top_10_percent = tagged_df['클릭율'].quantile(0.9)
    top_performers = tagged_df[tagged_df['클릭율'] >= top_10_percent]
    
    if len(top_performers) > 0:
        print(f"\n상위 10% 클릭률({top_10_percent:.2f}% 이상) 문구 특징:")
        print(f"- 주요 메시지 톤: {top_performers['tag_message_tone'].mode().values[0]}")
        print(f"- 주요 행동 유도: {top_performers['tag_call_to_action'].mode().values[0]}")
        print(f"- 평균 이모지 수: {top_performers['tag_emoji_count'].mean():.1f}개")
        print(f"- 질문 포함 비율: {top_performers['tag_has_question'].mean()*100:.1f}%")

if __name__ == "__main__":
    main()