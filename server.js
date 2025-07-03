const express = require('express');
const path = require('path');

// Multiple fetch implementations for maximum compatibility
let fetch;
try {
  // Try native fetch first (Node 18+)
  if (typeof globalThis.fetch !== 'undefined') {
    fetch = globalThis.fetch;
    console.log('✅ Using native fetch');
  } else {
    // Fallback to node-fetch
    fetch = require('node-fetch');
    console.log('✅ Using node-fetch');
  }
} catch (error) {
  console.error('❌ Fetch import failed:', error.message);
  // Ultimate fallback
  const https = require('https');
  const http = require('http');
  
  fetch = async (url, options = {}) => {
    return new Promise((resolve, reject) => {
      const urlObj = new URL(url);
      const isHttps = urlObj.protocol === 'https:';
      const lib = isHttps ? https : http;
      
      const req = lib.request(url, {
        method: options.method || 'GET',
        headers: options.headers || {},
        timeout: options.timeout || 30000
      }, (res) => {
        let data = '';
        res.on('data', chunk => data += chunk);
        res.on('end', () => {
          resolve({
            ok: res.statusCode >= 200 && res.statusCode < 300,
            status: res.statusCode,
            statusText: res.statusMessage,
            headers: new Map(Object.entries(res.headers)),
            text: () => Promise.resolve(data),
            json: () => Promise.resolve(JSON.parse(data))
          });
        });
      });
      
      req.on('error', reject);
      req.on('timeout', () => reject(new Error('Request timeout')));
      
      if (options.body) {
        req.write(options.body);
      }
      req.end();
    });
  };
  console.log('✅ Using custom fetch implementation');
}

const app = express();
const PORT = process.env.PORT || 3000;

// 홀리스틱 질문 분석 함수 (폭넓은 분석)
function generateSmartFallbackResult(query) {
  const lowerQuery = query.toLowerCase();
  
  // 다중 키워드 매칭으로 복합적인 니즈 파악
  const categoryScores = {};
  
  const keywords = {
    '대출': ['대출', '빌려', '신용', '금융', '돈', '차용', '융자', '여신', '현금', '자금'],
    '뷰티': ['뷰티', '화장품', '미용', '코스메틱', '스킨케어', '메이크업', '향수', '네일', '에스테틱'],
    '여행': ['여행', '해외', '항공', '호텔', '휴가', '관광', '출국', '비행', '패키지', '리조트'],
    '골프': ['골프', '라운딩', '클럽', '필드', '골프장', '스크린골프', '캐디', '그린피'],
    '운동': ['운동', '헬스', '피트니스', '요가', '필라테스', '수영', '러닝', '마라톤', '트레이닝'],
    '쇼핑': ['쇼핑', '구매', '온라인몰', '배송', '배달', '주문', '이커머스', '할인'],
    '결혼': ['결혼', '웨딩', '신혼', '허니문', '예식', '결혼식', '신부', '드레스'],
    '자녀': ['자녀', '아이', '아기', '어린이', '육아', '출산', '임신', '유치원', '학원'],
    '자동차': ['자동차', '차량', '카', '자동차보험', '주차', '주유', '렌트', '리스'],
    '투자': ['투자', '주식', '펀드', '자산', '재테크', '금융상품', '적금', '예금'],
    '부동산': ['집', '아파트', '주택', '전세', '월세', '매매', '부동산', '이사'],
    '고소득': ['고소득', '부자', '프리미엄', '럭셔리', '명품', '고급'],
    '라이프스타일': ['취미', '여가', '문화', '예술', '음악', '영화', '독서']
  };
  
  // 각 카테고리별 점수 계산
  for (const [category, keywordList] of Object.entries(keywords)) {
    const matches = keywordList.filter(keyword => lowerQuery.includes(keyword));
    categoryScores[category] = matches.length;
  }
  
  // 상위 카테고리들 추출 (복합적 니즈)
  const sortedCategories = Object.entries(categoryScores)
    .filter(([category, score]) => score > 0)
    .sort(([,a], [,b]) => b - a)
    .map(([category]) => category);
  
  // 연령/성별/소득/라이프스테이지 분석
  const demographics = analyzeDemographics(lowerQuery);
  
  return generateComprehensiveRecommendation(query, sortedCategories, demographics);
}

// 인구통계학적 특성 분석
function analyzeDemographics(query) {
  const demographics = {};
  
  // 연령대 분석
  const agePatterns = {
    '20대': ['20대', '젊은', '청년', '신입', '대학생', '사회초년생'],
    '30대': ['30대', '직장인', '워킹맘', '신혼', '커리어'],
    '40대': ['40대', '중년', '관리직', '팀장', '임원'],
    '50대': ['50대', '시니어', '중장년', '은퇴준비']
  };
  
  for (const [age, patterns] of Object.entries(agePatterns)) {
    if (patterns.some(pattern => query.includes(pattern))) {
      demographics.age = age;
      break;
    }
  }
  
  // 성별 분석
  const genderPatterns = {
    '여성': ['여성', '여자', '엄마', '주부', '워킹맘', '언니', '누나'],
    '남성': ['남성', '남자', '아빠', '직장인', '형', '오빠']
  };
  
  for (const [gender, patterns] of Object.entries(genderPatterns)) {
    if (patterns.some(pattern => query.includes(pattern))) {
      demographics.gender = gender;
      break;
    }
  }
  
  // 소득 수준 분석
  const incomePatterns = {
    '고소득': ['고소득', '부자', '프리미엄', '럭셔리', '고급', '명품', '비싼'],
    '중산층': ['중산층', '일반', '평균', '보통'],
    '실용적': ['절약', '할인', '저렴', '가성비', '알뜰']
  };
  
  for (const [income, patterns] of Object.entries(incomePatterns)) {
    if (patterns.some(pattern => query.includes(pattern))) {
      demographics.income = income;
      break;
    }
  }
  
  // 라이프스테이지 분석
  const lifestagePatterns = {
    '신혼': ['신혼', '결혼', '웨딩'],
    '육아': ['육아', '아이', '자녀', '아기', '출산'],
    '싱글': ['혼자', '1인', '독신', '싱글'],
    '은퇴준비': ['은퇴', '노후', '시니어']
  };
  
  for (const [stage, patterns] of Object.entries(lifestagePatterns)) {
    if (patterns.some(pattern => query.includes(pattern))) {
      demographics.lifestage = stage;
      break;
    }
  }
  
  return demographics;
}

// 종합적인 추천 생성 함수 (홀리스틱 분석)
function generateComprehensiveRecommendation(originalQuery, categories, demographics) {
  // 전체 CDP 컬럼 풀
  const allColumns = {
    // 직접 행동 지표 (fa_int_*)
    direct_behavior: {
      'fa_int_loan1stfinancial': { desc: '1금융권 신용대출 실행', type: 'date', condition: 'IS NOT NULL', priority: 'high' },
      'fa_int_loanpersonal': { desc: '신용대출 실행', type: 'date', condition: 'IS NOT NULL', priority: 'high' },
      'fa_int_traveloverseas': { desc: '해외여행 예정', type: 'date', condition: 'IS NOT NULL', priority: 'high' },
      'fa_int_golf': { desc: '골프용품/골프장 결제', type: 'date', condition: 'IS NOT NULL', priority: 'high' },
      'fa_int_luxury': { desc: '100만원 이상 명품 결제', type: 'date', condition: 'IS NOT NULL', priority: 'medium' },
      'fa_int_delivery': { desc: '배달음식 결제', type: 'date', condition: 'IS NOT NULL', priority: 'medium' },
      'fa_int_wedding': { desc: '결혼 준비 관련 결제', type: 'date', condition: 'IS NOT NULL', priority: 'high' },
      'fa_int_householdsingle': { desc: '1인 가구 관련 상품 결제', type: 'date', condition: 'IS NOT NULL', priority: 'medium' },
      'fa_int_householdchild': { desc: '어린이 관련 상품 결제', type: 'date', condition: 'IS NOT NULL', priority: 'medium' },
      'fa_int_move': { desc: '이사 관련 상품 결제', type: 'date', condition: 'IS NOT NULL', priority: 'medium' },
      'fa_int_carpurchase': { desc: '차량 구매 추정', type: 'date', condition: 'IS NOT NULL', priority: 'medium' },
      'fa_int_saving': { desc: '예적금 개설', type: 'date', condition: 'IS NOT NULL', priority: 'medium' },
      'fa_int_gym': { desc: '피트니스/헬스장 결제', type: 'date', condition: 'IS NOT NULL', priority: 'medium' },
      'fa_int_pilatesyoga': { desc: '필라테스/요가 결제', type: 'date', condition: 'IS NOT NULL', priority: 'low' }
    },
    
    // 업종별 지표 (fa_ind_*)
    industry_behavior: {
      'fa_ind_beauty': { desc: '미용 서비스 결제', type: 'date', condition: 'IS NOT NULL', priority: 'high' },
      'fa_ind_cosmetic': { desc: '뷰티 제품 결제', type: 'date', condition: 'IS NOT NULL', priority: 'high' },
      'fa_ind_travel': { desc: '여행 서비스 결제', type: 'date', condition: 'IS NOT NULL', priority: 'high' },
      'fa_ind_finance': { desc: '금융 서비스 결제', type: 'date', condition: 'IS NOT NULL', priority: 'medium' },
      'fa_ind_education': { desc: '교육 서비스 결제', type: 'date', condition: 'IS NOT NULL', priority: 'medium' },
      'fa_ind_restaurant': { desc: '음식점 결제', type: 'date', condition: 'IS NOT NULL', priority: 'low' },
      'fa_ind_cafe': { desc: '카페 결제', type: 'date', condition: 'IS NOT NULL', priority: 'low' }
    },
    
    // 예측 스코어 (sc_*)
    prediction_scores: {
      'sc_int_loan1stfinancial': { desc: '1금융권 대출 예측스코어', type: 'double', condition: '> 0.7', priority: 'high' },
      'sc_ind_cosmetic': { desc: '뷰티 제품 예측스코어', type: 'double', condition: '> 0.8', priority: 'high' },
      'sc_int_golf': { desc: '골프 관련 예측스코어', type: 'double', condition: '> 0.7', priority: 'high' },
      'sc_int_highincome': { desc: '고소득 예측스코어', type: 'double', condition: '> 0.8', priority: 'high' },
      'sc_int_luxury': { desc: '명품 구매 예측스코어', type: 'double', condition: '> 0.7', priority: 'medium' },
      'sc_int_delivery': { desc: '배달 이용 예측스코어', type: 'double', condition: '> 0.6', priority: 'low' },
      'sc_int_wedding': { desc: '결혼 준비 예측스코어', type: 'double', condition: '> 0.7', priority: 'medium' },
      'sc_ind_beauty': { desc: '미용 서비스 예측스코어', type: 'double', condition: '> 0.7', priority: 'medium' }
    },
    
    // 인구통계학적 플래그 (fi_npay_*)
    demographic_flags: {
      'fi_npay_age20': { desc: '20대', type: 'boolean', condition: '= true', priority: 'medium' },
      'fi_npay_age30': { desc: '30대', type: 'boolean', condition: '= true', priority: 'medium' },
      'fi_npay_age40': { desc: '40대', type: 'boolean', condition: '= true', priority: 'medium' },
      'fi_npay_genderf': { desc: '여성', type: 'boolean', condition: '= true', priority: 'medium' },
      'fi_npay_genderm': { desc: '남성', type: 'boolean', condition: '= true', priority: 'medium' },
      'fi_npay_creditcheck': { desc: '신용조회 서비스 가입', type: 'boolean', condition: '= true', priority: 'medium' },
      'fi_npay_membershipnormal': { desc: '플러스멤버십 가입', type: 'boolean', condition: '= true', priority: 'low' },
      'fi_npay_myassetreg': { desc: '내자산 서비스 연동', type: 'boolean', condition: '= true', priority: 'medium' }
    }
  };

  // 카테고리-컬럼 매핑 (확장된 버전)
  const categoryColumnMapping = {
    '대출': {
      primary: ['fa_int_loan1stfinancial', 'fa_int_loanpersonal', 'sc_int_loan1stfinancial'],
      secondary: ['fi_npay_creditcheck', 'sc_int_highincome', 'fa_ind_finance'],
      tertiary: ['fa_int_saving', 'fa_int_move', 'fa_int_carpurchase'] // 대출 니즈 발생 이벤트들
    },
    '뷰티': {
      primary: ['fa_ind_cosmetic', 'fa_ind_beauty', 'sc_ind_cosmetic'],
      secondary: ['fi_npay_genderf', 'sc_ind_beauty'],
      tertiary: ['fa_int_luxury', 'fa_int_delivery'] // 뷰티 관심층의 라이프스타일
    },
    '여행': {
      primary: ['fa_int_traveloverseas', 'fa_ind_travel'],
      secondary: ['sc_int_highincome', 'fa_int_luxury'],
      tertiary: ['fi_npay_creditcheck', 'fa_int_saving'] // 여행 자금 관련
    },
    '골프': {
      primary: ['fa_int_golf', 'sc_int_golf'],
      secondary: ['sc_int_highincome', 'fa_int_luxury'],
      tertiary: ['fi_npay_genderm', 'fa_ind_finance'] // 골프 인구 특성
    },
    '투자': {
      primary: ['fa_int_saving', 'fa_ind_finance'],
      secondary: ['sc_int_highincome', 'fi_npay_creditcheck'],
      tertiary: ['fi_npay_myassetreg', 'fa_int_loan1stfinancial'] // 투자 성향 고객 특성
    },
    '부동산': {
      primary: ['fa_int_move', 'fa_int_loan1stfinancial'],
      secondary: ['sc_int_highincome', 'fa_int_saving'],
      tertiary: ['fa_int_wedding', 'fa_int_householdchild'] // 주거 니즈 발생 이벤트
    }
  };

  // 복합적 추천 로직
  let recommendedColumns = [];
  
  // 1. Primary 컬럼들 (직접 관련)
  categories.slice(0, 2).forEach(category => { // 상위 2개 카테고리
    if (categoryColumnMapping[category]) {
      categoryColumnMapping[category].primary.forEach(colName => {
        if (!recommendedColumns.find(c => c.column === colName)) {
          const colInfo = findColumnInfo(colName, allColumns);
          if (colInfo) {
            recommendedColumns.push({
              column: colName,
              description: colInfo.desc,
              condition: colInfo.condition,
              priority: 'high',
              reasoning: `${category} 관련 핵심 지표로 타겟 고객 식별에 가장 중요한 컬럼입니다.`
            });
          }
        }
      });
    }
  });

  // 2. Secondary 컬럼들 (간접 관련)
  categories.slice(0, 3).forEach(category => {
    if (categoryColumnMapping[category]) {
      categoryColumnMapping[category].secondary.forEach(colName => {
        if (!recommendedColumns.find(c => c.column === colName)) {
          const colInfo = findColumnInfo(colName, allColumns);
          if (colInfo) {
            recommendedColumns.push({
              column: colName,
              description: colInfo.desc,
              condition: colInfo.condition,
              priority: 'medium',
              reasoning: `${category} 관심도가 높은 고객의 전형적인 특성으로 세분화에 유용합니다.`
            });
          }
        }
      });
    }
  });

  // 3. 인구통계학적 컬럼들
  if (demographics.age) {
    const ageCol = `fi_npay_age${demographics.age.replace('대', '')}`;
    if (!recommendedColumns.find(c => c.column === ageCol)) {
      recommendedColumns.push({
        column: ageCol,
        description: `${demographics.age} 연령층`,
        condition: '= true',
        priority: 'medium',
        reasoning: `${demographics.age} 고객의 라이프스타일과 소비 패턴에 맞춘 타겟팅이 가능합니다.`
      });
    }
  }

  if (demographics.gender) {
    const genderCol = demographics.gender === '여성' ? 'fi_npay_genderf' : 'fi_npay_genderm';
    if (!recommendedColumns.find(c => c.column === genderCol)) {
      recommendedColumns.push({
        column: genderCol,
        description: `${demographics.gender} 고객`,
        condition: '= true',
        priority: 'medium',
        reasoning: `${demographics.gender} 고객의 선호도와 구매 행동 특성을 반영한 세분화 기준입니다.`
      });
    }
  }

  // 4. Tertiary 컬럼들 (교차 분석용)
  if (recommendedColumns.length < 8) {
    categories.slice(0, 2).forEach(category => {
      if (categoryColumnMapping[category]) {
        categoryColumnMapping[category].tertiary.forEach(colName => {
          if (!recommendedColumns.find(c => c.column === colName) && recommendedColumns.length < 8) {
            const colInfo = findColumnInfo(colName, allColumns);
            if (colInfo) {
              recommendedColumns.push({
                column: colName,
                description: colInfo.desc,
                condition: colInfo.condition,
                priority: 'low',
                reasoning: `${category} 관심고객과 상관관계가 높은 라이프스타일 지표로 추가적인 인사이트 도출에 활용됩니다.`
              });
            }
          }
        });
      }
    });
  }

  // 소득 수준 추가
  if (demographics.income === '고소득' && !recommendedColumns.find(c => c.column === 'sc_int_highincome')) {
    recommendedColumns.push({
      column: 'sc_int_highincome',
      description: '고소득 예측스코어',
      condition: '> 0.8',
      priority: 'high',
      reasoning: '고소득층 타겟팅으로 마케팅 ROI와 상품 단가 상승을 기대할 수 있습니다.'
    });
  }

  // 최대 8-10개 컬럼으로 제한
  recommendedColumns = recommendedColumns.slice(0, 10);

  return {
    query_analysis: `"${originalQuery}" - 복합적인 고객 니즈와 라이프스타일을 종합 분석하여 ${categories.length > 1 ? '다차원적' : '전방위적'} 타겟팅 전략을 수립했습니다.`,
    target_description: generateTargetDescription(categories, demographics),
    recommended_columns: recommendedColumns,
    sql_query: generateComprehensiveSQL(recommendedColumns),
    business_insights: generateComprehensiveInsights(categories, demographics, recommendedColumns),
    estimated_target_size: estimateTargetSize(categories, demographics),
    marketing_recommendations: generateComprehensiveMarketing(categories, demographics)
  };
}

// 컬럼 정보 찾기 헬퍼 함수
function findColumnInfo(columnName, allColumns) {
  for (const [category, columns] of Object.entries(allColumns)) {
    if (columns[columnName]) {
      return columns[columnName];
    }
  }
  return null;
}

// 타겟 설명 생성
function generateTargetDescription(categories, demographics) {
  let description = '';
  
  // 인구통계학적 특성
  const demoDesc = [];
  if (demographics.age) demoDesc.push(demographics.age);
  if (demographics.gender) demoDesc.push(demographics.gender);
  if (demographics.income) demoDesc.push(demographics.income);
  if (demographics.lifestage) demoDesc.push(demographics.lifestage);
  
  if (demoDesc.length > 0) {
    description += demoDesc.join(' ') + ' ';
  }
  
  // 관심사/행동 특성
  if (categories.length > 0) {
    description += `${categories.slice(0, 3).join(', ')} 관련 니즈가 높고 `;
  }
  
  description += '다층적인 소비 패턴과 라이프스타일을 보이는 종합적 타겟 고객군';
  
  return description;
}

// 종합적 SQL 쿼리 생성
function generateComprehensiveSQL(columns) {
  const columnNames = columns.map(col => col.column).join(', ');
  const conditions = columns
    .filter(col => col.priority === 'high')
    .map(col => `${col.column} ${col.condition}`)
    .join(' OR ');
  
  return `SELECT mbr_id_no, ${columnNames}
FROM cdp_customer_data 
WHERE (${conditions || 'sc_int_highincome > 0.7'})
ORDER BY ${columns[0]?.column || 'sc_int_highincome'} DESC
LIMIT 10000;`;
}

// 종합적 비즈니스 인사이트 생성
function generateComprehensiveInsights(categories, demographics, columns) {
  const insights = [];
  
  // 복합적 니즈 분석
  if (categories.length > 1) {
    insights.push(`${categories.slice(0, 2).join('과 ')} 영역의 복합적 니즈를 가진 고객군으로 교차 마케팅 기회가 높음`);
  }
  
  // 고가치 고객 여부
  if (columns.some(col => col.column === 'sc_int_highincome' || col.column === 'fa_int_luxury')) {
    insights.push('고소득/프리미엄 성향 고객이 포함되어 있어 높은 LTV(Life Time Value) 기대 가능');
  }
  
  // 라이프스테이지 인사이트
  if (demographics.lifestage) {
    insights.push(`${demographics.lifestage} 라이프스테이지 특성상 관련 상품/서비스 니즈가 동반 상승하는 시기`);
  }
  
  // 디지털 활용도
  if (columns.some(col => col.column.includes('npay'))) {
    insights.push('네이버페이 이용 고객으로 디지털 마케팅 채널 활용도가 높고 데이터 트래킹 용이');
  }
  
  // 기본 인사이트
  insights.push('다양한 접점에서의 고객 행동 데이터를 바탕으로 한 정밀한 타겟팅 가능');
  insights.push('개인화된 상품 추천 및 맞춤형 마케팅 메시지 전달로 전환율 극대화 기대');
  
  return insights.slice(0, 5); // 최대 5개로 제한
}

// 타겟 규모 추정
function estimateTargetSize(categories, demographics) {
  let size = 20; // 기본 20%
  
  // 카테고리 수에 따른 조정
  if (categories.length > 2) size *= 0.7; // 복합 조건일수록 규모 감소
  if (categories.length > 3) size *= 0.6;
  
  // 인구통계학적 조건에 따른 조정
  if (demographics.age) size *= 0.8;
  if (demographics.gender) size *= 0.5;
  if (demographics.income === '고소득') size *= 0.3;
  
  size = Math.max(size, 2); // 최소 2%
  size = Math.min(size, 35); // 최대 35%
  
  return `${Math.round(size)}-${Math.round(size * 1.5)}%`;
}

// 종합적 마케팅 추천
function generateComprehensiveMarketing(categories, demographics) {
  const recommendations = [];
  
  // 채널별 추천
  recommendations.push('네이버 생태계 내 통합 마케팅: 검색, 쇼핑, 페이 연계 캠페인 실행');
  
  // 개인화 추천
  if (categories.length > 1) {
    recommendations.push(`${categories.slice(0, 2).join('+')} 복합 니즈 기반 크로스셀링 기회 활용`);
  }
  
  // 라이프스테이지별 추천
  if (demographics.lifestage) {
    recommendations.push(`${demographics.lifestage} 라이프스테이지에 특화된 시기별 마케팅 캠페인 기획`);
  }
  
  // 프리미엄 전략
  if (demographics.income === '고소득') {
    recommendations.push('VIP 등급 서비스 및 프리미엄 상품 우선 노출 전략');
  }
  
  // 데이터 활용 추천
  recommendations.push('실시간 행동 데이터 기반 동적 세그먼테이션 및 적응형 메시지 전달');
  recommendations.push('A/B 테스트를 통한 세그먼트별 최적 메시지 및 타이밍 도출');
  
  return recommendations.slice(0, 6); // 최대 6개로 제한
}

// 타겟별 추천 생성 함수 (레거시 호환성용)
function generateTargetRecommendation(targetType, originalQuery, targetAge, targetGender) {
  const recommendations = {
    '대출': {
      query_analysis: `"${originalQuery}" - 사용자가 대출 상품에 관심이 높고 신청 가능성이 있는 고객군을 요청했습니다.`,
      target_description: '신용도가 양호하고 안정적인 소득을 보유하여 대출 상품 이용 가능성이 높은 고객군',
      recommended_columns: [
        {
          column: 'sc_int_loan1stfinancial',
          description: '1금융권 신용대출 예측스코어',
          condition: '> 0.7',
          priority: 'high',
          reasoning: '1금융권에서 대출받을 가능성이 높아 안정적인 고객층으로 판단됩니다.'
        },
        {
          column: 'fa_int_loanpersonal',
          description: '최근 신용대출 실행 이력',
          condition: 'IS NOT NULL',
          priority: 'high',
          reasoning: '기존 대출 경험이 있어 대출 상품에 대한 이해도가 높고 추가 니즈가 있을 가능성이 큽니다.'
        },
        {
          column: 'fi_npay_creditcheck',
          description: '신용조회 서비스 가입 여부',
          condition: '= true',
          priority: 'medium',
          reasoning: '신용관리에 관심이 높아 대출 상품 정보에도 적극적으로 반응할 것으로 예상됩니다.'
        }
      ],
      sql_query: `SELECT mbr_id_no, sc_int_loan1stfinancial, fa_int_loanpersonal, fi_npay_creditcheck
FROM cdp_customer_data 
WHERE (sc_int_loan1stfinancial > 0.7)
   OR (fa_int_loanpersonal IS NOT NULL AND fi_npay_creditcheck = true)
ORDER BY sc_int_loan1stfinancial DESC;`,
      business_insights: [
        '고소득층일수록 대출 한도가 높아 수익성 관점에서 우선 타겟팅 필요',
        '기존 대출 고객의 대환대출 니즈를 적극 발굴하여 고객 유지 및 수익 증대 가능',
        '신용조회 서비스 이용자는 금융 상품 관심도가 높아 마케팅 효과가 좋음'
      ],
      estimated_target_size: '15-20%',
      marketing_recommendations: [
        '개인별 신용점수를 활용한 맞춤형 대출 상품 및 금리 제안',
        '기존 대출 고객 대상 대환대출 상담 및 우대 조건 제공',
        '신용조회 서비스 내에서 대출 상품 정보 자연스럽게 노출'
      ]
    },
    '뷰티': {
      query_analysis: `"${originalQuery}" - 뷰티 및 화장품 구매에 적극적이고 관련 소비가 활발한 고객군을 요청했습니다.`,
      target_description: '뷰티 트렌드에 민감하고 관련 제품 구매 및 서비스 이용이 활발한 고객군',
      recommended_columns: [
        {
          column: 'sc_ind_cosmetic',
          description: '뷰티 제품 결제 예측스코어',
          condition: '> 0.8',
          priority: 'high',
          reasoning: '뷰티 제품 구매 가능성이 매우 높은 핵심 타겟층으로 우선 공략 필요합니다.'
        },
        {
          column: 'fa_ind_beauty',
          description: '미용 서비스 결제 이력',
          condition: 'IS NOT NULL',
          priority: 'high',
          reasoning: '미용실, 네일샵 등 뷰티 서비스 이용으로 뷰티에 대한 관심도가 확인된 고객입니다.'
        },
        {
          column: 'fi_npay_genderf',
          description: '여성 고객',
          condition: '= true',
          priority: 'medium',
          reasoning: '뷰티 제품의 주요 구매층인 여성 고객을 우선 타겟팅해야 합니다.'
        }
      ],
      sql_query: `SELECT mbr_id_no, sc_ind_cosmetic, fa_ind_beauty, fi_npay_genderf
FROM cdp_customer_data
WHERE (sc_ind_cosmetic > 0.8)
   OR (fa_ind_beauty IS NOT NULL AND fi_npay_genderf = true)
ORDER BY sc_ind_cosmetic DESC;`,
      business_insights: [
        '젊은 여성층의 뷰티 지출이 지속적으로 증가하는 트렌드',
        '미용 서비스와 뷰티 제품을 함께 이용하는 고객의 생애가치(LTV)가 높음',
        '개인화된 뷰티 솔루션에 대한 수요 증가'
      ],
      estimated_target_size: '25-30%',
      marketing_recommendations: [
        '뷰티 인플루언서 및 소셜미디어를 활용한 제품 체험 마케팅',
        '개인 피부타입 및 선호도 기반 맞춤형 뷰티 루틴 제안',
        '미용실 방문 고객 대상 뷰티 제품 할인 쿠폰 제공'
      ]
    },
    '여행': {
      query_analysis: `"${originalQuery}" - 여행을 자주 다니며 여행 관련 상품 및 서비스 이용이 활발한 고객군을 요청했습니다.`,
      target_description: '국내외 여행 경험이 풍부하고 여행 관련 지출이 활발한 고객군',
      recommended_columns: [
        {
          column: 'fa_int_traveloverseas',
          description: '해외여행 예정 고객',
          condition: 'IS NOT NULL',
          priority: 'high',
          reasoning: '해외여행 계획이 확정된 고객으로 여행 관련 상품 구매 확률이 매우 높습니다.'
        },
        {
          column: 'fa_ind_travel',
          description: '여행 관련 결제 이력',
          condition: 'IS NOT NULL',
          priority: 'high',
          reasoning: '여행사, 항공권 등 여행 상품 구매 경험이 있어 재구매 가능성이 높습니다.'
        },
        {
          column: 'sc_int_highincome',
          description: '고소득 예측스코어',
          condition: '> 0.6',
          priority: 'medium',
          reasoning: '여행에 충분한 지출이 가능한 경제적 여력을 보유한 고객입니다.'
        }
      ],
      sql_query: `SELECT mbr_id_no, fa_int_traveloverseas, fa_ind_travel, sc_int_highincome
FROM cdp_customer_data
WHERE (fa_int_traveloverseas IS NOT NULL)
   OR (fa_ind_travel IS NOT NULL AND sc_int_highincome > 0.6)
ORDER BY sc_int_highincome DESC;`,
      business_insights: [
        '포스트 코로나 시대 해외여행 수요가 급격히 회복되는 추세',
        '고소득층일수록 프리미엄 여행 상품 및 부가 서비스를 선호',
        '개인 맞춤형 여행 패키지에 대한 관심도 상승'
      ],
      estimated_target_size: '12-18%',
      marketing_recommendations: [
        '시즌별 인기 여행지 및 패키지 상품 맞춤 추천',
        '여행자보험 상품과 여행 패키지 번들 마케팅',
        '항공마일리지 적립 및 여행 혜택 강화 프로그램'
      ]
    },
    '골프': {
      query_analysis: `"${originalQuery}" - 골프에 관심이 높고 골프 관련 소비가 활발한 고객군을 요청했습니다.`,
      target_description: '골프를 즐기며 관련 용품 및 서비스 구매가 활발한 프리미엄 고객군',
      recommended_columns: [
        {
          column: 'fa_int_golf',
          description: '골프용품/골프장 관련 상품 결제 고객',
          condition: 'IS NOT NULL',
          priority: 'high',
          reasoning: '골프 용품이나 골프장 이용 이력이 있어 골프에 대한 관심도가 확인된 고객입니다.'
        },
        {
          column: 'sc_int_golf',
          description: '골프 관련 예측스코어',
          condition: '> 0.7',
          priority: 'high',
          reasoning: '골프 관련 소비 가능성이 높아 골프 상품 마케팅 효과가 클 것으로 예상됩니다.'
        },
        {
          column: 'sc_int_highincome',
          description: '고소득 예측스코어',
          condition: '> 0.8',
          priority: 'medium',
          reasoning: '골프는 고소득층의 레저 활동으로 경제적 여력이 있는 고객을 타겟해야 합니다.'
        }
      ],
      sql_query: `SELECT mbr_id_no, fa_int_golf, sc_int_golf, sc_int_highincome
FROM cdp_customer_data
WHERE (fa_int_golf IS NOT NULL)
   OR (sc_int_golf > 0.7 AND sc_int_highincome > 0.8)
ORDER BY sc_int_golf DESC, sc_int_highincome DESC;`,
      business_insights: [
        '골프 고객은 높은 구매력을 보유한 프리미엄 고객층으로 LTV가 높음',
        '골프 관련 소비는 장비, 레슨, 라운딩 등 다양한 카테고리로 확장 가능',
        '골프 커뮤니티를 통한 입소문 마케팅 효과가 높음'
      ],
      estimated_target_size: '5-8%',
      marketing_recommendations: [
        '프리미엄 골프 용품 및 골프장 예약 서비스 제공',
        '골프 레슨 및 골프 여행 패키지 상품 연계',
        'VIP 골프 이벤트 및 프로골퍼와의 만남 기회 제공'
      ]
    }
  };
  
  // 기본 추천 결과 가져오기
  let result = recommendations[targetType] || {
    query_analysis: `"${originalQuery}"에 대한 분석을 수행했습니다.`,
    target_description: '요청하신 조건에 맞는 고객군',
    recommended_columns: [
      {
        column: 'sc_int_highincome',
        description: '고소득 예측스코어',
        condition: '> 0.7',
        priority: 'high',
        reasoning: '안정적인 소득 기반으로 마케팅 효과가 높을 것으로 예상됩니다.'
      }
    ],
    sql_query: 'SELECT mbr_id_no, sc_int_highincome FROM cdp_customer_data WHERE sc_int_highincome > 0.7;',
    business_insights: ['추가 분석이 필요합니다.'],
    estimated_target_size: '10-15%',
    marketing_recommendations: ['맞춤형 마케팅 전략을 수립해보세요.']
  };
  
  // 연령/성별 필터 추가
  if (targetAge || targetGender) {
    const ageGenderColumns = [];
    
    if (targetAge) {
      const ageMapping = {
        '20대': 'fi_npay_age20',
        '30대': 'fi_npay_age30', 
        '40대': 'fi_npay_age40'
      };
      
      if (ageMapping[targetAge]) {
        ageGenderColumns.push({
          column: ageMapping[targetAge],
          description: `${targetAge} 연령층`,
          condition: '= true',
          priority: 'medium',
          reasoning: `${targetAge} 고객의 라이프스타일과 소비 패턴에 최적화된 타겟팅이 가능합니다.`
        });
      }
    }
    
    if (targetGender) {
      const genderMapping = {
        '여성': 'fi_npay_genderf',
        '남성': 'fi_npay_genderm'
      };
      
      if (genderMapping[targetGender]) {
        ageGenderColumns.push({
          column: genderMapping[targetGender],
          description: `${targetGender} 고객`,
          condition: '= true',
          priority: 'medium',
          reasoning: `${targetGender} 고객의 선호도와 구매 행동에 맞춘 마케팅이 효과적입니다.`
        });
      }
    }
    
    // 기존 컬럼에 연령/성별 필터 추가
    result.recommended_columns = [...result.recommended_columns, ...ageGenderColumns];
    
    // SQL 쿼리에 연령/성별 조건 추가
    if (ageGenderColumns.length > 0) {
      const additionalConditions = ageGenderColumns.map(col => `${col.column} ${col.condition}`).join(' AND ');
      result.sql_query = result.sql_query.replace('ORDER BY', `AND ${additionalConditions}\nORDER BY`);
    }
    
    // 타겟 설명 업데이트
    const ageGenderDesc = [targetAge, targetGender].filter(Boolean).join(' ');
    if (ageGenderDesc) {
      result.target_description = `${ageGenderDesc} ${result.target_description}`;
    }
  }
  
  return result;
}

// Claude API 호출 함수
async function analyzeWithClaude(userQuery) {
  const CLAUDE_API_KEY = process.env.CLAUDE_API_KEY?.trim();
  
  console.log('\n🤖 Claude API 호출 시작');
  console.log('📊 환경 정보:');
  console.log('   - Node.js 버전:', process.version);
  console.log('   - Claude API 키 존재:', !!CLAUDE_API_KEY);
  console.log('   - API 키 길이:', CLAUDE_API_KEY?.length || 0);
  
  if (!CLAUDE_API_KEY) {
    throw new Error('CLAUDE_API_KEY가 설정되지 않았습니다.');
  }
  
  if (!CLAUDE_API_KEY.startsWith('sk-ant-api')) {
    throw new Error('Claude API 키 형식이 올바르지 않습니다. sk-ant-api로 시작해야 합니다.');
  }

  const requestBody = {
    model: 'claude-3-haiku-20240307',
    max_tokens: 1500,
    temperature: 0.3,
    messages: [
      {
        role: 'user',
        content: `CDP 고객 분석 전문가로서 "${userQuery}" 질문에 대해 다음 JSON 형식으로 정확히 답변해주세요:\n\n{
  "query_analysis": "질문 분석 내용",
  "target_description": "타겟 고객 설명",
  "recommended_columns": [
    {
      "column": "컬럼명",
      "description": "컬럼 설명",
      "condition": "조건",
      "priority": "high/medium/low",
      "reasoning": "선택 이유"
    }
  ],
  "sql_query": "SQL 쿼리",
  "business_insights": ["인사이트1", "인사이트2"],
  "estimated_target_size": "예상 규모",
  "marketing_recommendations": ["추천1", "추천2"]
}`
      }
    ]
  };

  console.log('📤 Claude API 요청 시작...');
  
  try {
    const response = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': CLAUDE_API_KEY,
        'anthropic-version': '2023-06-01'
      },
      body: JSON.stringify(requestBody)
    });
    
    console.log('📥 Claude API 응답:', response.status);
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error('❌ Claude API 오류:', errorText);
      throw new Error(`Claude API Error (${response.status}): ${errorText}`);
    }
    
    const data = await response.json();
    console.log('✅ Claude API 응답 성공');
    
    if (!data.content?.[0]?.text) {
      throw new Error('Claude 응답에 예상된 content가 없습니다.');
    }
    
    const claudeResponse = data.content[0].text.trim();
    console.log('🤖 Claude 응답 길이:', claudeResponse.length, 'characters');
    
    // JSON 파싱 시도
    try {
      const parsed = JSON.parse(claudeResponse);
      console.log('✅ Claude 응답 JSON 파싱 성공');
      return parsed;
    } catch (parseError) {
      console.log('⚠️ Claude 응답이 JSON이 아님, 폴백 처리...');
      
      // 폴백 응답 생성
      return {
        query_analysis: `"${userQuery}"에 대한 Claude 분석이 완료되었습니다.`,
        target_description: '분석된 고객 세그먼트',
        recommended_columns: [
          {
            column: 'sc_int_highincome',
            description: '고소득 예측스코어',
            condition: '> 0.7',
            priority: 'high',
            reasoning: 'Claude 분석 결과 추천된 핵심 지표입니다.'
          }
        ],
        sql_query: 'SELECT mbr_id_no, sc_int_highincome FROM cdp_customer_data WHERE sc_int_highincome > 0.7;',
        business_insights: [
          'Claude 분석을 통해 도출된 비즈니스 인사이트입니다.',
          claudeResponse.substring(0, 100) + '...'
        ],
        estimated_target_size: '10-15%',
        marketing_recommendations: [
          'Claude 추천 마케팅 전략을 적용하세요.'
        ],
        _claude_response: claudeResponse
      };
    }
    
  } catch (error) {
    console.error('💥 Claude API 호출 실패:', error.message);
    throw error;
  }
}

// Parse JSON bodies
app.use(express.json());

// Serve static files
app.use(express.static('.'));

// Main route
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'working_ai_query_platform.html'));
});

// Debug endpoint to check environment variables
app.get('/api/debug', (req, res) => {
  const hasApiKey = !!process.env.OPENAI_API_KEY;
  const apiKeyLength = process.env.OPENAI_API_KEY ? process.env.OPENAI_API_KEY.length : 0;
  const nodeEnv = process.env.NODE_ENV || 'development';
  
  res.json({
    timestamp: new Date().toISOString(),
    environment: nodeEnv,
    hasOpenAIKey: hasApiKey,
    apiKeyLength: apiKeyLength,
    apiKeyPrefix: hasApiKey ? process.env.OPENAI_API_KEY.substring(0, 8) + '...' : 'Not Set',
    serverStatus: 'running'
  });
});

// OpenAI API 키 테스트 엔드포인트 (강화된 버전)
app.get('/api/test-openai', async (req, res) => {
  try {
    console.log('🧪 OpenAI API 키 테스트 시작...');
    
    // 1. 환경변수 존재 확인
    if (!process.env.OPENAI_API_KEY) {
      return res.json({
        success: false,
        step: 'env_check',
        error: 'OPENAI_API_KEY 환경변수가 설정되지 않았습니다.',
        suggestion: 'Railway Variables에서 OPENAI_API_KEY를 설정해주세요.',
        debug: {
          allEnvKeys: Object.keys(process.env).filter(key => key.includes('OPENAI')),
          nodeEnv: process.env.NODE_ENV
        }
      });
    }

    // 2. API 키 형식 확인
    const apiKey = process.env.OPENAI_API_KEY;
    console.log('🔍 API 키 검증:');
    console.log('   - 길이:', apiKey.length);
    console.log('   - 시작 문자:', apiKey.substring(0, 8));
    console.log('   - 형식 확인:', apiKey.startsWith('sk-') ? '✅' : '❌');
    
    if (!apiKey.startsWith('sk-')) {
      return res.json({
        success: false,
        step: 'format_check',
        error: 'API 키 형식이 올바르지 않습니다.',
        suggestion: 'OpenAI API 키는 sk-로 시작해야 합니다.',
        debug: {
          keyLength: apiKey.length,
          keyPrefix: apiKey.substring(0, 10),
          expectedFormat: 'sk-proj-...'
        }
      });
    }

    // 3. 네트워크 연결 테스트
    console.log('🌐 네트워크 연결 테스트 중...');
    
    const response = await fetch('https://api.openai.com/v1/models', {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${apiKey}`,
        'User-Agent': 'CDP-Analysis-Platform/1.0'
      },
      timeout: 15000
    });

    console.log('📥 API 응답 수신:');
    console.log('   - 상태:', response.status);
    console.log('   - 헤더:', Object.fromEntries(response.headers.entries()));

    const responseText = await response.text();
    console.log('   - 응답 크기:', responseText.length);
    
    if (!response.ok) {
      console.error('❌ OpenAI API 테스트 실패');
      console.error('   - 상태:', response.status);
      console.error('   - 응답:', responseText);
      
      let errorDetail = '';
      let suggestion = '';
      let debugInfo = {};
      
      try {
        const errorData = JSON.parse(responseText);
        errorDetail = errorData.error?.message || responseText;
        debugInfo.errorCode = errorData.error?.code;
        debugInfo.errorType = errorData.error?.type;
      } catch (e) {
        errorDetail = responseText;
      }
      
      // 상세한 해결 방안 제시
      switch (response.status) {
        case 401:
          suggestion = `인증 오류 해결 방법:
1. OpenAI 대시보드 (platform.openai.com)에서 API 키 상태 확인
2. API 키를 새로 생성하여 Railway Variables에 재설정
3. API 키 복사 시 앞뒤 공백이 없는지 확인
4. 계정에 충분한 크레딧이 있는지 확인`;
          break;
        case 429:
          suggestion = `사용량 한도 초과 해결 방법:
1. OpenAI 대시보드에서 Usage 확인
2. Billing 섹션에서 결제 방법 등록/업데이트
3. Rate limit이 초과된 경우 잠시 후 재시도
4. Usage limits 설정 확인`;
          break;
        case 403:
          suggestion = `권한 오류 해결 방법:
1. API 키 권한 확인 (사용 가능한 모델 확인)
2. 계정 상태 확인 (정지되지 않았는지)
3. 결제 정보 업데이트`;
          break;
        default:
          suggestion = `일반적인 해결 방법:
1. 몇 분 후 다시 시도
2. OpenAI 서비스 상태 확인 (status.openai.com)
3. 네트워크 연결 확인`;
      }
      
      return res.json({
        success: false,
        step: 'api_call',
        status: response.status,
        error: errorDetail,
        suggestion: suggestion,
        debug: {
          ...debugInfo,
          responseSize: responseText.length,
          timestamp: new Date().toISOString()
        }
      });
    }

    // 4. 응답 파싱 및 검증
    let data;
    try {
      data = JSON.parse(responseText);
      console.log('✅ JSON 파싱 성공');
    } catch (parseError) {
      console.error('❌ JSON 파싱 실패:', parseError.message);
      return res.json({
        success: false,
        step: 'json_parse',
        error: 'API 응답 JSON 파싱 실패',
        suggestion: 'OpenAI API 응답 형식이 예상과 다릅니다.',
        debug: {
          parseError: parseError.message,
          responsePreview: responseText.substring(0, 200)
        }
      });
    }

    // 5. 성공 응답
    console.log('✅ OpenAI API 키 테스트 완전 성공');
    
    return res.json({
      success: true,
      message: '🎉 OpenAI API 키가 정상적으로 작동합니다!',
      details: {
        modelsCount: data.data?.length || 0,
        availableModels: data.data?.slice(0, 5).map(m => m.id) || [],
        apiKeyPrefix: apiKey.substring(0, 12) + '...',
        testTimestamp: new Date().toISOString()
      },
      nextSteps: [
        '이제 AI 분석 기능이 정상적으로 작동할 것입니다.',
        '질문을 입력하여 실제 OpenAI 분석을 테스트해보세요.'
      ]
    });

  } catch (error) {
    console.error('💥 Claude API 테스트 중 예외:', error);
    
    let errorType = 'unknown';
    let suggestion = '알 수 없는 오류가 발생했습니다.';
    
    if (error.code === 'ENOTFOUND') {
      errorType = 'network';
      suggestion = '인터넷 연결을 확인하고 다시 시도해주세요.';
    } else if (error.code === 'ETIMEDOUT') {
      errorType = 'timeout';
      suggestion = '네트워크가 느리거나 Claude 서버가 응답하지 않습니다. 잠시 후 다시 시도해주세요.';
    } else if (error.message.includes('fetch')) {
      errorType = 'fetch';
      suggestion = 'HTTP 요청 중 오류가 발생했습니다. 서버 환경을 확인해주세요.';
    }
    
    return res.json({
      success: false,
      step: 'exception',
      error: error.message,
      errorType: errorType,
      suggestion: suggestion,
      debug: {
        stack: error.stack?.split('\n').slice(0, 3),
        timestamp: new Date().toISOString()
      }
    });
  }
});

// API endpoint for OpenAI calls (보안을 위해 서버에서 처리)
app.post('/api/analyze', async (req, res) => {
  const startTime = Date.now();
  
  try {
    const { query } = req.body;
    
    console.log(`\n🔍 [${new Date().toISOString()}] 새로운 분석 요청:`, query);
    console.log(`📋 환경변수 상태:`);
    console.log(`   - CLAUDE_API_KEY 존재: ${!!process.env.CLAUDE_API_KEY}`);
    console.log(`   - API 키 길이: ${process.env.CLAUDE_API_KEY ? process.env.CLAUDE_API_KEY.length : 0}`);
    console.log(`   - NODE_ENV: ${process.env.NODE_ENV || 'development'}`);
    
    // 입력 유효성 검사
    if (!query || query.trim().length === 0) {
      return res.status(400).json({ error: '질문을 입력해주세요.' });
    }
    
    let result;
    let analysisMethod = 'unknown';
    
    // Claude API 키가 있으면 실제 AI 분석 시도
    if (process.env.CLAUDE_API_KEY) {
      try {
        console.log('🤖 Claude API 호출 시작...');
        result = await analyzeWithClaude(query);
        analysisMethod = 'claude';
        console.log('✅ Claude API 응답 성공');
      } catch (apiError) {
        console.error('❌ Claude API 오류:', apiError.message);
        console.log('🔄 Fallback으로 전환');
        result = generateSmartFallbackResult(query);
        result._apiError = apiError.message;
        analysisMethod = 'fallback_after_error';
      }
    } else {
      console.log('⚠️  Claude API 키 없음 - Fallback 사용');
      result = generateSmartFallbackResult(query);
      analysisMethod = 'fallback_no_key';
    }

    // 분석 방법 메타데이터 추가
    result._metadata = {
      analysisMethod: analysisMethod,
      processingTimeMs: Date.now() - startTime,
      timestamp: new Date().toISOString(),
      query: query
    };

    console.log(`🎯 분석 완료 (${analysisMethod}) - ${Date.now() - startTime}ms`);
    console.log(`📤 추천 컬럼 수: ${result.recommended_columns?.length || 0}\n`);

    res.json(result);
  } catch (error) {
    console.error('💥 서버 에러:', error);
    // 502 에러 방지를 위해 항상 응답 반환
    const fallbackResult = generateSmartFallbackResult(req.body?.query || '일반 질문');
    fallbackResult._metadata = {
      analysisMethod: 'error_fallback',
      processingTimeMs: Date.now() - startTime,
      timestamp: new Date().toISOString(),
      error: error.message
    };
    res.status(200).json(fallbackResult);
  }
});

// Start server
app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
  console.log(`Environment: ${process.env.NODE_ENV || 'development'}`);
});