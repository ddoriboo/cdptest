import pandas as pd
import openai
import json
from typing import List, Dict
from tqdm import tqdm
import time
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import warnings
warnings.filterwarnings('ignore')

class EnhancedNotificationTagger:
    def __init__(self, api_key: str):
        self.client = openai.OpenAI(api_key=api_key)
        self.tagged_data = []
        
    def create_advanced_tagging_prompt(self, notification_text: str) -> str:
        return f"""
다음 대출 관련 알림 문구를 심층 분석하여 태그를 생성해주세요.

알림 문구: "{notification_text}"

다음 카테고리에 대해 JSON 형식으로 태그를 생성해주세요:

1. message_tone (메시지 톤) - 하나만 선택
   - urgent: 긴급성 강조
   - friendly: 친근한 톤
   - informative: 정보 제공형
   - persuasive: 설득형
   - reminder: 리마인더형
   - professional: 전문적/공식적

2. call_to_action (행동 유도) - 하나만 선택
   - click_now: 즉시 클릭 유도
   - check_info: 정보 확인 유도
   - complete_action: 미완료 작업 완료 유도
   - compare: 비교 유도
   - apply: 신청 유도
   - none: 행동 유도 없음

3. psychological_triggers (심리적 트리거) - 여러 개 가능 (배열)
   - fomo: 놓칠까봐 두려움
   - curiosity: 호기심 유발
   - benefit: 혜택 강조
   - personalization: 개인화
   - social_proof: 사회적 증거
   - urgency: 시간 압박
   - simplicity: 간단함 강조
   - authority: 권위/신뢰성
   - scarcity: 희소성

4. content_elements (콘텐츠 요소)
   - emoji_count: 이모지 개수 (정수)
   - has_question: 질문 포함 여부 (true/false)
   - has_numbers: 숫자 포함 여부 (true/false)
   - has_percentage: 퍼센트 포함 여부 (true/false)
   - has_time_reference: 시간 참조 포함 (true/false)
   - has_arrow: 화살표 포함 (true/false)
   - has_exclamation: 느낌표 포함 (true/false)
   - word_count: 단어 수 (정수)

5. offer_type (제안 유형) - 하나만 선택
   - rate_check: 금리 확인
   - limit_check: 한도 확인
   - refinancing: 대환/갈아타기
   - new_loan: 신규 대출
   - report: 리포트/분석
   - event: 이벤트/혜택
   - comparison: 비교 서비스
   - none: 특정 제안 없음

6. target_emotion (타겟 감정) - 하나만 선택
   - anxiety: 불안감
   - hope: 희망
   - relief: 안도감
   - excitement: 흥분/기대감
   - trust: 신뢰감
   - curiosity: 호기심
   - satisfaction: 만족감

7. value_proposition (가치 제안)
   - main_benefit: 주요 혜택 (문자열, 예: "금리 인하", "한도 증가", "신용점수 확인")
   - benefit_clarity: 혜택 명확성 (1-5 점수, 5가 가장 명확)
   - personalization_level: 개인화 수준 (1-5 점수, 5가 가장 개인화됨)

8. linguistic_features (언어적 특징)
   - sentence_type: 문장 유형 (declarative/interrogative/imperative/exclamatory)
   - formality_level: 격식 수준 (1-5, 1이 가장 캐주얼, 5가 가장 격식있음)
   - reading_ease: 가독성 (1-5, 5가 가장 읽기 쉬움)

JSON 형식으로만 응답해주세요.
"""

    def tag_notification_batch(self, notifications: List[str], batch_size: int = 5) -> List[Dict]:
        """배치로 여러 알림을 한 번에 태깅"""
        results = []
        
        for i in range(0, len(notifications), batch_size):
            batch = notifications[i:i+batch_size]
            batch_prompt = "다음 알림 문구들을 각각 분석해주세요:\n\n"
            
            for idx, notif in enumerate(batch):
                batch_prompt += f"{idx+1}. {notif}\n"
            
            batch_prompt += "\n각 문구에 대해 위의 태깅 구조를 따라 JSON 배열로 응답해주세요."
            
            try:
                response = self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "당신은 마케팅 문구 분석 전문가입니다."},
                        {"role": "user", "content": self.create_advanced_tagging_prompt(batch[0]) if len(batch) == 1 else batch_prompt}
                    ],
                    temperature=0.1,
                    response_format={"type": "json_object"}
                )
                
                result = json.loads(response.choices[0].message.content)
                if isinstance(result, dict):
                    results.append(result)
                else:
                    results.extend(result)
                    
            except Exception as e:
                print(f"배치 태깅 에러: {e}")
                # 개별 처리로 폴백
                for notif in batch:
                    results.append(self.tag_single_notification(notif))
            
            time.sleep(1)  # API 제한 방지
            
        return results

    def tag_single_notification(self, notification_text: str) -> Dict:
        """단일 알림 태깅"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "당신은 마케팅 문구 분석 전문가입니다."},
                    {"role": "user", "content": self.create_advanced_tagging_prompt(notification_text)}
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"개별 태깅 에러: {e}")
            return self.get_default_tags()

    def get_default_tags(self) -> Dict:
        """에러 시 기본 태그 반환"""
        return {
            "message_tone": "none",
            "call_to_action": "none",
            "psychological_triggers": [],
            "content_elements": {
                "emoji_count": 0,
                "has_question": False,
                "has_numbers": False,
                "has_percentage": False,
                "has_time_reference": False,
                "has_arrow": False,
                "has_exclamation": False,
                "word_count": 0
            },
            "offer_type": "none",
            "target_emotion": "none",
            "value_proposition": {
                "main_benefit": "",
                "benefit_clarity": 0,
                "personalization_level": 0
            },
            "linguistic_features": {
                "sentence_type": "declarative",
                "formality_level": 3,
                "reading_ease": 3
            }
        }

    def process_dataframe(self, df: pd.DataFrame, sample_size: int = 100) -> pd.DataFrame:
        """데이터프레임 전체 처리"""
        print(f"\n=== 지능형 샘플링 시작 ===")
        
        # 1. 서비스별, 클릭률 구간별 층화 샘플링
        df['ctr_quartile'] = pd.qcut(df['클릭율'], q=4, labels=['Q1', 'Q2', 'Q3', 'Q4'])
        
        # 샘플링 전략
        sample_dfs = []
        
        # 서비스별 샘플링
        for service in df['서비스명'].unique():
            service_df = df[df['서비스명'] == service]
            
            # 각 분위별로 샘플링
            for quartile in ['Q1', 'Q2', 'Q3', 'Q4']:
                quartile_df = service_df[service_df['ctr_quartile'] == quartile]
                if len(quartile_df) > 0:
                    n_samples = min(5, len(quartile_df))  # 각 그룹에서 최대 5개
                    sample_dfs.append(quartile_df.sample(n=n_samples, random_state=42))
        
        # 전체 샘플 합치기
        sample_df = pd.concat(sample_dfs).drop_duplicates().reset_index(drop=True)
        
        # 샘플 크기 조정
        if len(sample_df) > sample_size:
            sample_df = sample_df.sample(n=sample_size, random_state=42)
        
        print(f"총 {len(sample_df)}개 문구 샘플링 완료")
        print(f"서비스 분포: {sample_df['서비스명'].value_counts().to_dict()}")
        print(f"클릭률 분포: Q1({sample_df[sample_df['ctr_quartile']=='Q1']['클릭율'].mean():.2f}%) ~ Q4({sample_df[sample_df['ctr_quartile']=='Q4']['클릭율'].mean():.2f}%)")
        
        # 2. 태깅 수행
        print("\n=== 태깅 시작 ===")
        notifications = sample_df['발송 문구'].tolist()
        
        # 배치 처리
        tags_list = []
        batch_size = 5
        
        for i in tqdm(range(0, len(notifications), batch_size), desc="배치 태깅"):
            batch = notifications[i:i+batch_size]
            batch_tags = self.tag_notification_batch(batch, batch_size=1)  # 안정성을 위해 개별 처리
            tags_list.extend(batch_tags)
            
            # 중간 저장
            if i % 20 == 0 and i > 0:
                self.save_intermediate_results(sample_df[:len(tags_list)], tags_list)
        
        # 3. 태그 데이터프레임에 추가
        self.add_tags_to_dataframe(sample_df, tags_list)
        
        return sample_df

    def add_tags_to_dataframe(self, df: pd.DataFrame, tags_list: List[Dict]):
        """태그를 데이터프레임에 추가"""
        # 기본 태그
        for key in ['message_tone', 'call_to_action', 'offer_type', 'target_emotion']:
            df[f'tag_{key}'] = [tag.get(key, 'none') for tag in tags_list]
        
        # 심리적 트리거
        df['tag_psychological_triggers'] = [
            ','.join(tag.get('psychological_triggers', [])) for tag in tags_list
        ]
        df['tag_trigger_count'] = [
            len(tag.get('psychological_triggers', [])) for tag in tags_list
        ]
        
        # 콘텐츠 요소
        content_elements = ['emoji_count', 'has_question', 'has_numbers', 'has_percentage', 
                          'has_time_reference', 'has_arrow', 'has_exclamation', 'word_count']
        for element in content_elements:
            df[f'tag_{element}'] = [
                tag.get('content_elements', {}).get(element, 0 if 'count' in element else False) 
                for tag in tags_list
            ]
        
        # 가치 제안
        df['tag_main_benefit'] = [
            tag.get('value_proposition', {}).get('main_benefit', '') for tag in tags_list
        ]
        df['tag_benefit_clarity'] = [
            tag.get('value_proposition', {}).get('benefit_clarity', 0) for tag in tags_list
        ]
        df['tag_personalization_level'] = [
            tag.get('value_proposition', {}).get('personalization_level', 0) for tag in tags_list
        ]
        
        # 언어적 특징
        df['tag_sentence_type'] = [
            tag.get('linguistic_features', {}).get('sentence_type', 'declarative') for tag in tags_list
        ]
        df['tag_formality_level'] = [
            tag.get('linguistic_features', {}).get('formality_level', 3) for tag in tags_list
        ]
        df['tag_reading_ease'] = [
            tag.get('linguistic_features', {}).get('reading_ease', 3) for tag in tags_list
        ]

    def save_intermediate_results(self, df: pd.DataFrame, tags_list: List[Dict]):
        """중간 결과 저장"""
        temp_df = df.copy()
        self.add_tags_to_dataframe(temp_df, tags_list)
        temp_df.to_csv('/Users/user/Desktop/notitest/tagged_intermediate.csv', index=False, encoding='utf-8-sig')

class AdvancedAnalyzer:
    def __init__(self, tagged_df: pd.DataFrame):
        self.df = tagged_df
        
    def comprehensive_analysis(self):
        """종합적인 분석 수행"""
        print("\n=== 심층 분석 결과 ===\n")
        
        # 1. 기본 태그별 성과
        self.analyze_tag_performance()
        
        # 2. 태그 조합 분석
        self.analyze_tag_combinations()
        
        # 3. 서비스별 최적 전략
        self.analyze_service_strategies()
        
        # 4. 예측 모델 구축
        self.build_prediction_model()
        
        # 5. 시각화
        self.create_visualizations()
        
    def analyze_tag_performance(self):
        """태그별 성과 분석"""
        print("1. 핵심 태그별 클릭률 분석")
        print("-" * 50)
        
        # 주요 태그별 분석
        key_tags = ['tag_message_tone', 'tag_call_to_action', 'tag_offer_type', 'tag_target_emotion']
        
        for tag in key_tags:
            print(f"\n{tag.replace('tag_', '').replace('_', ' ').title()}:")
            analysis = self.df.groupby(tag).agg({
                '클릭율': ['mean', 'std', 'count'],
                '클릭회원수': 'sum'
            }).round(2)
            analysis.columns = ['평균_클릭률', '표준편차', '건수', '총_클릭수']
            print(analysis.sort_values('평균_클릭률', ascending=False))
        
        # 콘텐츠 요소별 분석
        print("\n\n콘텐츠 요소별 영향:")
        content_features = ['tag_has_question', 'tag_has_numbers', 'tag_has_emoji_count', 
                          'tag_has_time_reference', 'tag_has_exclamation']
        
        for feature in content_features:
            if feature in self.df.columns:
                if 'has_' in feature:
                    true_ctr = self.df[self.df[feature] == True]['클릭율'].mean()
                    false_ctr = self.df[self.df[feature] == False]['클릭율'].mean()
                    print(f"{feature}: 있음({true_ctr:.2f}%) vs 없음({false_ctr:.2f}%)")
    
    def analyze_tag_combinations(self):
        """태그 조합 분석"""
        print("\n\n2. 고성과 태그 조합 분석")
        print("-" * 50)
        
        # 톤 + CTA 조합
        combo_analysis = self.df.groupby(['tag_message_tone', 'tag_call_to_action'])['클릭율'].agg(['mean', 'count'])
        top_combos = combo_analysis[combo_analysis['count'] >= 2].sort_values('mean', ascending=False).head(10)
        
        print("\n상위 10개 톤+CTA 조합:")
        for idx, row in top_combos.iterrows():
            tone, cta = idx
            print(f"{tone} + {cta}: {row['mean']:.2f}% (n={row['count']})")
        
        # 심리 트리거 조합
        print("\n\n효과적인 심리 트리거 조합:")
        
        # 트리거 개수별 성과
        trigger_count_analysis = self.df.groupby('tag_trigger_count')['클릭율'].agg(['mean', 'count'])
        print("\n트리거 개수별 평균 클릭률:")
        print(trigger_count_analysis)
        
    def analyze_service_strategies(self):
        """서비스별 최적 전략 도출"""
        print("\n\n3. 서비스별 최적 전략")
        print("-" * 50)
        
        for service in self.df['서비스명'].unique():
            service_df = self.df[self.df['서비스명'] == service]
            if len(service_df) < 5:
                continue
                
            print(f"\n[{service}]")
            
            # 상위 20% 성과 문구의 특징
            top_20_threshold = service_df['클릭율'].quantile(0.8)
            top_performers = service_df[service_df['클릭율'] >= top_20_threshold]
            
            if len(top_performers) > 0:
                print(f"상위 20% 클릭률: {top_20_threshold:.2f}% 이상")
                
                # 주요 태그
                for tag in ['tag_message_tone', 'tag_call_to_action', 'tag_offer_type']:
                    if tag in top_performers.columns:
                        top_value = top_performers[tag].mode()
                        if len(top_value) > 0:
                            print(f"- 최적 {tag.replace('tag_', '')}: {top_value.values[0]}")
                
                # 평균 특성
                print(f"- 평균 이모지 수: {top_performers['tag_emoji_count'].mean():.1f}")
                print(f"- 질문 포함률: {top_performers['tag_has_question'].mean()*100:.0f}%")
                print(f"- 평균 혜택 명확성: {top_performers['tag_benefit_clarity'].mean():.1f}/5")
    
    def build_prediction_model(self):
        """클릭률 예측 모델 구축"""
        print("\n\n4. 클릭률 예측 모델")
        print("-" * 50)
        
        # 특성 준비
        feature_columns = [col for col in self.df.columns if col.startswith('tag_') and col != 'tag_psychological_triggers']
        
        # 카테고리 변수 인코딩
        categorical_features = ['tag_message_tone', 'tag_call_to_action', 'tag_offer_type', 
                              'tag_target_emotion', 'tag_sentence_type']
        
        df_encoded = self.df.copy()
        label_encoders = {}
        
        for cat_feature in categorical_features:
            if cat_feature in df_encoded.columns:
                le = LabelEncoder()
                df_encoded[cat_feature] = le.fit_transform(df_encoded[cat_feature].fillna('none'))
                label_encoders[cat_feature] = le
        
        # 특성과 타겟 분리
        valid_features = [col for col in feature_columns if col in df_encoded.columns]
        X = df_encoded[valid_features].fillna(0)
        y = df_encoded['클릭율']
        
        # 학습/테스트 분할
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # 모델 학습
        rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
        rf_model.fit(X_train, y_train)
        
        # 성능 평가
        train_score = rf_model.score(X_train, y_train)
        test_score = rf_model.score(X_test, y_test)
        
        print(f"모델 성능:")
        print(f"- 학습 R²: {train_score:.3f}")
        print(f"- 테스트 R²: {test_score:.3f}")
        
        # 특성 중요도
        feature_importance = pd.DataFrame({
            'feature': valid_features,
            'importance': rf_model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        print("\n상위 10개 중요 특성:")
        for idx, row in feature_importance.head(10).iterrows():
            print(f"- {row['feature']}: {row['importance']:.3f}")
        
        return rf_model, label_encoders
    
    def create_visualizations(self):
        """시각화 생성"""
        print("\n\n5. 시각화 저장 중...")
        
        plt.rcParams['font.family'] = 'AppleGothic'
        plt.rcParams['axes.unicode_minus'] = False
        
        # 1. 서비스별 클릭률 분포
        plt.figure(figsize=(12, 6))
        self.df.boxplot(column='클릭율', by='서비스명', ax=plt.gca())
        plt.title('서비스별 클릭률 분포')
        plt.suptitle('')
        plt.ylabel('클릭률 (%)')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig('/Users/user/Desktop/notitest/service_ctr_distribution.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 2. 메시지 톤별 평균 클릭률
        plt.figure(figsize=(10, 6))
        tone_avg = self.df.groupby('tag_message_tone')['클릭율'].mean().sort_values(ascending=True)
        tone_avg.plot(kind='barh')
        plt.title('메시지 톤별 평균 클릭률')
        plt.xlabel('평균 클릭률 (%)')
        plt.tight_layout()
        plt.savefig('/Users/user/Desktop/notitest/tone_performance.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print("시각화 파일 저장 완료")

def main():
    print("=== 대출 알림 문구 심층 분석 시작 ===\n")
    
    # API 키 설정
    api_key = "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"
    
    # 데이터 로드
    print("데이터 로딩 중...")
    df = pd.read_csv('/Users/user/Desktop/notitest/202507_.csv')
    print(f"총 {len(df)}개의 알림 데이터 로드 완료")
    
    # 태거 초기화 및 실행
    tagger = EnhancedNotificationTagger(api_key=api_key)
    
    # 샘플 크기 설정 (API 제한을 고려하여 조정)
    sample_size = 80  # 더 많은 샘플로 분석
    
    # 태깅 수행
    tagged_df = tagger.process_dataframe(df, sample_size=sample_size)
    
    # 결과 저장
    output_filename = 'enhanced_tagged_notifications.csv'
    tagged_df.to_csv(f'/Users/user/Desktop/notitest/{output_filename}', index=False, encoding='utf-8-sig')
    print(f"\n태깅 결과 저장 완료: {output_filename}")
    
    # 심층 분석
    analyzer = AdvancedAnalyzer(tagged_df)
    analyzer.comprehensive_analysis()
    
    # 최종 인사이트 요약
    print("\n\n=== 핵심 인사이트 요약 ===")
    print("-" * 50)
    
    # 전체 평균 대비 상위 성과 태그
    overall_mean_ctr = tagged_df['클릭율'].mean()
    print(f"\n전체 평균 클릭률: {overall_mean_ctr:.2f}%")
    
    # 평균 이상 성과를 보이는 요소들
    print("\n평균 이상 성과를 보이는 핵심 요소:")
    
    # 메시지 톤
    tone_performance = tagged_df.groupby('tag_message_tone')['클릭율'].mean()
    high_performing_tones = tone_performance[tone_performance > overall_mean_ctr].sort_values(ascending=False)
    if len(high_performing_tones) > 0:
        print(f"\n효과적인 메시지 톤:")
        for tone, ctr in high_performing_tones.items():
            print(f"  - {tone}: {ctr:.2f}% (+{ctr-overall_mean_ctr:.2f}%p)")
    
    # 실행 가능한 권장사항
    print("\n\n=== 실행 권장사항 ===")
    print("1. 즉시 적용 가능한 개선사항:")
    print("   - 질문형 문구 활용 확대")
    print("   - 구체적인 숫자와 퍼센트 포함")
    print("   - 시간 관련 표현으로 긴급성 부여")
    
    print("\n2. A/B 테스트 제안:")
    print("   - reminder vs urgent 톤 비교")
    print("   - 이모지 개수 최적화 (0개 vs 1개 vs 2개)")
    print("   - 혜택 명확성 수준별 테스트")
    
    print("\n3. 장기 전략:")
    print("   - 서비스별 맞춤형 템플릿 개발")
    print("   - 예측 모델 기반 실시간 문구 최적화")
    print("   - 지속적인 성과 모니터링 체계 구축")

if __name__ == "__main__":
    main()