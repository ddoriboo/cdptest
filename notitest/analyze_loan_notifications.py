import pandas as pd
import numpy as np
import re
from collections import Counter
import matplotlib.pyplot as plt
import seaborn as sns
plt.rcParams['font.family'] = 'AppleGothic'
plt.rcParams['axes.unicode_minus'] = False

# 데이터 로드
df = pd.read_csv('/Users/user/Desktop/notitest/202507_.csv')

# 데이터 정보 출력
print("=== 데이터 기본 정보 ===")
print(f"전체 레코드 수: {len(df)}")
print(f"컬럼: {df.columns.tolist()}")
print("\n데이터 타입:")
print(df.dtypes)
print("\n")

# 1. 각 서비스별 통계
print("=== 1. 서비스별 통계 ===")
service_stats = df.groupby('서비스명').agg({
    'ID': 'count',
    '발송회원수': 'sum',
    '클릭회원수': 'sum',
    '클릭율': 'mean',
    '클릭까지 소요된 평균 분(Minutes)': 'mean'
}).round(2)
service_stats.columns = ['발송건수', '총발송회원수', '총클릭회원수', '평균클릭율', '평균클릭소요시간(분)']
service_stats['전체클릭율'] = (service_stats['총클릭회원수'] / service_stats['총발송회원수'] * 100).round(2)
print(service_stats)
print("\n")

# 2. 각 채널별 통계
print("=== 2. 채널별 통계 ===")
channel_stats = df.groupby('발송채널 (noti : 네이버앱, npay: 페이앱)').agg({
    'ID': 'count',
    '발송회원수': 'sum',
    '클릭회원수': 'sum',
    '클릭율': 'mean',
    '클릭까지 소요된 평균 분(Minutes)': 'mean'
}).round(2)
channel_stats.columns = ['발송건수', '총발송회원수', '총클릭회원수', '평균클릭율', '평균클릭소요시간(분)']
channel_stats['전체클릭율'] = (channel_stats['총클릭회원수'] / channel_stats['총발송회원수'] * 100).round(2)
print(channel_stats)
print("\n")

# 3. 문구에서 자주 사용되는 패턴이나 특징적인 표현들
print("=== 3. 문구 패턴 분석 ===")

# 이모지 추출
emoji_pattern = re.compile(r'[^\w\s,.\!?\-()·]+')
all_emojis = []
for text in df['발송 문구']:
    emojis = emoji_pattern.findall(text)
    all_emojis.extend(emojis)

emoji_counter = Counter(all_emojis)
print("자주 사용되는 이모지 Top 10:")
for emoji, count in emoji_counter.most_common(10):
    print(f"  {emoji}: {count}회")

# 주요 키워드 분석
keywords = ['한도', '금리', '대출', '갈아타기', '신용', '약관', '리포트', '확인', '비교', '시간', '고민', '이자', '집']
keyword_stats = {}
for keyword in keywords:
    count = df['발송 문구'].str.contains(keyword).sum()
    if count > 0:
        avg_ctr = df[df['발송 문구'].str.contains(keyword)]['클릭율'].mean()
        keyword_stats[keyword] = {'사용횟수': count, '평균클릭율': round(avg_ctr, 2)}

print("\n주요 키워드별 사용횟수 및 평균 클릭율:")
for keyword, stats in sorted(keyword_stats.items(), key=lambda x: x[1]['평균클릭율'], reverse=True):
    print(f"  {keyword}: {stats['사용횟수']}회 사용, 평균 클릭율 {stats['평균클릭율']}%")

# 4. 클릭률이 높은 문구들의 공통적인 특징
print("\n=== 4. 클릭률 높은 문구 분석 ===")

# 상위 20% 클릭률 문구 분석
top_20_percentile = df['클릭율'].quantile(0.8)
high_ctr_df = df[df['클릭율'] >= top_20_percentile]

print(f"상위 20% 클릭률 기준: {top_20_percentile:.2f}%")
print(f"해당 문구 개수: {len(high_ctr_df)}개")

# 고클릭률 문구의 특징 분석
print("\n고클릭률 문구 Top 10:")
top_10_ctr = df.nlargest(10, '클릭율')[['서비스명', '발송 문구', '클릭율', '클릭까지 소요된 평균 분(Minutes)']]
for idx, row in top_10_ctr.iterrows():
    print(f"\n[{row['클릭율']:.2f}%] {row['서비스명']}")
    print(f"  문구: {row['발송 문구']}")
    print(f"  클릭소요시간: {row['클릭까지 소요된 평균 분(Minutes)']:.0f}분")

# 고클릭률 문구의 공통 특징
high_ctr_features = {
    '이모지_포함': high_ctr_df['발송 문구'].apply(lambda x: bool(emoji_pattern.search(x))).sum() / len(high_ctr_df) * 100,
    '물음표_포함': high_ctr_df['발송 문구'].str.contains('\\?').sum() / len(high_ctr_df) * 100,
    '숫자_포함': high_ctr_df['발송 문구'].str.contains('\\d').sum() / len(high_ctr_df) * 100,
    '화살표_포함': high_ctr_df['발송 문구'].str.contains('👉|>').sum() / len(high_ctr_df) * 100,
}

print("\n고클릭률 문구의 특징 (상위 20% 기준):")
for feature, percentage in high_ctr_features.items():
    print(f"  {feature}: {percentage:.1f}%")

# 5. 클릭 소요 시간과 클릭률 간의 관계
print("\n=== 5. 클릭 소요 시간과 클릭률 관계 ===")

# 상관관계 계산
correlation = df['클릭율'].corr(df['클릭까지 소요된 평균 분(Minutes)'])
print(f"클릭률과 클릭소요시간의 상관계수: {correlation:.3f}")

# 클릭 소요 시간 구간별 평균 클릭률
df['클릭소요시간_구간'] = pd.cut(df['클릭까지 소요된 평균 분(Minutes)'], 
                                bins=[0, 1000, 5000, 10000, 20000, float('inf')],
                                labels=['1시간이내', '1-3일', '3-7일', '7-14일', '14일이상'])

time_interval_stats = df.groupby('클릭소요시간_구간').agg({
    '클릭율': ['mean', 'count'],
    '발송회원수': 'sum',
    '클릭회원수': 'sum'
}).round(2)

print("\n클릭소요시간 구간별 통계:")
print(time_interval_stats)

# 시각화
fig, axes = plt.subplots(2, 2, figsize=(15, 12))

# 1. 서비스별 평균 클릭률
ax1 = axes[0, 0]
service_stats['평균클릭율'].plot(kind='bar', ax=ax1)
ax1.set_title('서비스별 평균 클릭률')
ax1.set_xlabel('서비스')
ax1.set_ylabel('평균 클릭률 (%)')
ax1.tick_params(axis='x', rotation=45)

# 2. 클릭률 분포
ax2 = axes[0, 1]
df['클릭율'].hist(bins=30, ax=ax2)
ax2.set_title('클릭률 분포')
ax2.set_xlabel('클릭률 (%)')
ax2.set_ylabel('빈도')

# 3. 클릭소요시간과 클릭률의 산점도
ax3 = axes[1, 0]
ax3.scatter(df['클릭까지 소요된 평균 분(Minutes)'], df['클릭율'], alpha=0.5)
ax3.set_title('클릭소요시간 vs 클릭률')
ax3.set_xlabel('클릭소요시간 (분)')
ax3.set_ylabel('클릭률 (%)')

# 4. 서비스별 클릭소요시간
ax4 = axes[1, 1]
df.boxplot(column='클릭까지 소요된 평균 분(Minutes)', by='서비스명', ax=ax4)
ax4.set_title('서비스별 클릭소요시간 분포')
ax4.set_xlabel('서비스')
ax4.set_ylabel('클릭소요시간 (분)')

plt.tight_layout()
plt.savefig('/Users/user/Desktop/notitest/loan_notification_analysis.png', dpi=300, bbox_inches='tight')
plt.close()

# 추가 인사이트
print("\n=== 추가 인사이트 ===")

# 서비스별 최고/최저 클릭률 문구
for service in df['서비스명'].unique():
    service_df = df[df['서비스명'] == service]
    best = service_df.loc[service_df['클릭율'].idxmax()]
    worst = service_df.loc[service_df['클릭율'].idxmin()]
    
    print(f"\n[{service}]")
    print(f"  최고 클릭률({best['클릭율']:.2f}%): {best['발송 문구'][:50]}...")
    print(f"  최저 클릭률({worst['클릭율']:.2f}%): {worst['발송 문구'][:50]}...")

# 시간대별 발송 패턴 (날짜 기준)
df['발송일'] = pd.to_datetime(df['발송일'])
df['요일'] = df['발송일'].dt.day_name()
weekday_stats = df.groupby('요일')['클릭율'].mean().round(2)
print(f"\n요일별 평균 클릭률:")
for day, ctr in weekday_stats.items():
    print(f"  {day}: {ctr}%")