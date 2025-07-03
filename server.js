const express = require('express');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;

// 스마트 질문 분석 함수
function generateSmartFallbackResult(query) {
  const lowerQuery = query.toLowerCase();
  
  // 키워드 기반 타겟 타입 결정
  let targetType = '일반';
  
  const keywords = {
    '대출': ['대출', '빌려', '신용', '금융', '돈', '차용', '융자', '여신'],
    '뷰티': ['뷰티', '화장품', '미용', '코스메틱', '스킨케어', '메이크업', '향수'],
    '여행': ['여행', '해외', '항공', '호텔', '휴가', '관광', '출국', '비행'],
    '골프': ['골프', '라운딩', '클럽', '필드', '골프장', '스크린골프'],
    '운동': ['운동', '헬스', '피트니스', '요가', '필라테스', '수영', '러닝'],
    '쇼핑': ['쇼핑', '구매', '온라인몰', '배송', '배달', '주문'],
    '결혼': ['결혼', '웨딩', '신혼', '허니문', '예식', '결혼식'],
    '자녀': ['자녀', '아이', '아기', '어린이', '육아', '출산', '임신'],
    '자동차': ['자동차', '차량', '카', '자동차보험', '주차', '주유'],
    '투자': ['투자', '주식', '펀드', '자산', '재테크', '금융상품']
  };
  
  for (const [type, keywordList] of Object.entries(keywords)) {
    if (keywordList.some(keyword => lowerQuery.includes(keyword))) {
      targetType = type;
      break;
    }
  }
  
  // 연령/성별 키워드 확인
  const ageKeywords = {
    '20대': ['20대', '젊은', '청년', '신입'],
    '30대': ['30대', '직장인', '워킹맘'],
    '40대': ['40대', '중년', '관리직'],
    '50대': ['50대', '시니어', '중장년']
  };
  
  const genderKeywords = {
    '여성': ['여성', '여자', '엄마', '주부'],
    '남성': ['남성', '남자', '아빠', '직장인']
  };
  
  let targetAge = null;
  let targetGender = null;
  
  for (const [age, keywords] of Object.entries(ageKeywords)) {
    if (keywords.some(keyword => lowerQuery.includes(keyword))) {
      targetAge = age;
      break;
    }
  }
  
  for (const [gender, keywords] of Object.entries(genderKeywords)) {
    if (keywords.some(keyword => lowerQuery.includes(keyword))) {
      targetGender = gender;
      break;
    }
  }
  
  return generateTargetRecommendation(targetType, query, targetAge, targetGender);
}

// 타겟별 추천 생성 함수
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

// OpenAI API 호출 함수
async function analyzeWithOpenAI(userQuery) {
  const OPENAI_API_KEY = process.env.OPENAI_API_KEY;
  
  // CDP 컬럼 정의 (간소화된 버전)
  const CDP_COLUMNS_INFO = `
CDP 컬럼 카테고리:

관심사 지표 (fa_int_*):
- fa_int_loan1stfinancial: 1금융권 신용대출 실행 고객
- fa_int_loanpersonal: 신용대출 실행 고객  
- fa_int_traveloverseas: 해외여행 예정 고객
- fa_int_golf: 골프용품/골프장 결제 고객
- fa_int_luxury: 100만원 이상 명품 결제 고객
- fa_int_delivery: 배달 결제 고객
- fa_int_wedding: 결혼 준비 관련 결제 고객

업종별 지표 (fa_ind_*):
- fa_ind_beauty: 미용 서비스 결제 고객
- fa_ind_cosmetic: 뷰티 제품 결제 고객
- fa_ind_travel: 여행 서비스 결제 고객
- fa_ind_finance: 금융 서비스 결제 고객

예측 스코어 (sc_*):
- sc_int_loan1stfinancial: 1금융권 대출 예측스코어 (0-1)
- sc_ind_cosmetic: 뷰티 제품 예측스코어 (0-1)
- sc_int_golf: 골프 관련 예측스코어 (0-1)
- sc_int_highincome: 고소득 예측스코어 (0-1)

플래그 지표 (fi_npay_*):
- fi_npay_age20/30/40: 20대/30대/40대 여부 (boolean)
- fi_npay_genderf/m: 여성/남성 여부 (boolean)
- fi_npay_creditcheck: 신용조회 서비스 가입 (boolean)
`;

  const prompt = `당신은 CDP(Customer Data Platform) 전문가입니다. 사용자의 자연어 질문을 분석하여 최적의 고객 세그먼테이션 전략을 제공합니다.

${CDP_COLUMNS_INFO}

사용자 질문: "${userQuery}"

위 질문을 분석하여 다음 JSON 형식으로 응답해주세요:

{
  "query_analysis": "질문의 핵심 요구사항 분석",
  "target_description": "타겟 고객군 설명", 
  "recommended_columns": [
    {
      "column": "컬럼명",
      "description": "컬럼 설명",
      "condition": "추천 조건 (예: > 0.7, IS NOT NULL)",
      "priority": "high|medium|low",
      "reasoning": "선택 이유"
    }
  ],
  "sql_query": "실행 가능한 SELECT 쿼리",
  "business_insights": ["비즈니스 인사이트 배열"],
  "estimated_target_size": "예상 타겟 규모 (%)",
  "marketing_recommendations": ["마케팅 추천사항 배열"]
}

반드시 유효한 JSON 형식으로만 응답해주세요.`;

  const response = await fetch('https://api.openai.com/v1/chat/completions', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${OPENAI_API_KEY}`
    },
    body: JSON.stringify({
      model: 'gpt-4o-mini',
      messages: [
        {
          role: 'system',
          content: 'You are a CDP expert. Always respond in valid JSON format only.'
        },
        {
          role: 'user', 
          content: prompt
        }
      ],
      temperature: 0.7,
      max_tokens: 2000
    })
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`OpenAI API Error: ${response.status} - ${errorText}`);
  }

  const data = await response.json();
  const aiResponse = data.choices[0].message.content;

  try {
    // JSON 파싱 시도
    const parsed = JSON.parse(aiResponse);
    return parsed;
  } catch (parseError) {
    console.error('JSON 파싱 실패:', parseError.message);
    console.error('원본 응답:', aiResponse);
    throw new Error(`JSON Parse Error: ${parseError.message}`);
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

// OpenAI API 키 테스트 엔드포인트
app.get('/api/test-openai', async (req, res) => {
  try {
    if (!process.env.OPENAI_API_KEY) {
      return res.json({
        success: false,
        error: 'OPENAI_API_KEY 환경변수가 설정되지 않았습니다.',
        suggestion: 'Railway Variables에서 OPENAI_API_KEY를 설정해주세요.'
      });
    }

    console.log('🧪 OpenAI API 키 테스트 시작...');
    
    // 간단한 API 테스트 호출
    const response = await fetch('https://api.openai.com/v1/models', {
      headers: {
        'Authorization': `Bearer ${process.env.OPENAI_API_KEY}`
      }
    });

    const responseText = await response.text();
    
    if (!response.ok) {
      console.error('❌ OpenAI API 테스트 실패:', response.status, responseText);
      
      let errorDetail = '';
      let suggestion = '';
      
      try {
        const errorData = JSON.parse(responseText);
        errorDetail = errorData.error?.message || responseText;
      } catch (e) {
        errorDetail = responseText;
      }
      
      if (response.status === 401) {
        suggestion = '1. API 키가 올바른지 확인하세요\n2. OpenAI 대시보드에서 API 키 유효성 확인\n3. API 키 앞뒤 공백 제거';
      } else if (response.status === 429) {
        suggestion = '1. API 사용량 한도 초과\n2. 결제 정보 확인\n3. 잠시 후 다시 시도';
      } else if (response.status === 403) {
        suggestion = '1. API 키 권한 확인\n2. 계정 상태 확인';
      }
      
      return res.json({
        success: false,
        status: response.status,
        error: errorDetail,
        suggestion: suggestion
      });
    }

    console.log('✅ OpenAI API 키 테스트 성공');
    const data = JSON.parse(responseText);
    
    return res.json({
      success: true,
      message: 'OpenAI API 키가 정상적으로 작동합니다.',
      modelsCount: data.data?.length || 0,
      apiKeyPrefix: process.env.OPENAI_API_KEY.substring(0, 10) + '...'
    });

  } catch (error) {
    console.error('💥 OpenAI API 테스트 중 오류:', error);
    return res.json({
      success: false,
      error: error.message,
      suggestion: '네트워크 연결을 확인하고 다시 시도해주세요.'
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
    console.log(`   - OPENAI_API_KEY 존재: ${!!process.env.OPENAI_API_KEY}`);
    console.log(`   - API 키 길이: ${process.env.OPENAI_API_KEY ? process.env.OPENAI_API_KEY.length : 0}`);
    console.log(`   - NODE_ENV: ${process.env.NODE_ENV || 'development'}`);
    
    // 입력 유효성 검사
    if (!query || query.trim().length === 0) {
      return res.status(400).json({ error: '질문을 입력해주세요.' });
    }
    
    let result;
    let analysisMethod = 'unknown';
    
    // OpenAI API 키가 있으면 실제 AI 분석 시도
    if (process.env.OPENAI_API_KEY) {
      try {
        console.log('🤖 OpenAI API 호출 시작...');
        result = await analyzeWithOpenAI(query);
        analysisMethod = 'openai';
        console.log('✅ OpenAI API 응답 성공');
      } catch (apiError) {
        console.error('❌ OpenAI API 오류:', apiError.message);
        console.error('   상세 에러:', apiError);
        console.error('   API 키 상태:', {
          hasKey: !!process.env.OPENAI_API_KEY,
          keyLength: process.env.OPENAI_API_KEY?.length,
          keyPrefix: process.env.OPENAI_API_KEY?.substring(0, 10) + '...'
        });
        console.log('🔄 Fallback으로 전환');
        result = generateSmartFallbackResult(query);
        result._apiError = apiError.message; // 클라이언트에 오류 정보 전달
        analysisMethod = 'fallback_after_error';
      }
    } else {
      console.log('⚠️  OpenAI API 키 없음 - Fallback 사용');
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