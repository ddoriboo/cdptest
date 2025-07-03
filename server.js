const express = require('express');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;

// Parse JSON bodies
app.use(express.json());

// Serve static files
app.use(express.static('.'));

// Main route
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'working_ai_query_platform.html'));
});

// API endpoint for OpenAI calls (보안을 위해 서버에서 처리)
app.post('/api/analyze', async (req, res) => {
  try {
    const { query } = req.body;
    
    if (!process.env.OPENAI_API_KEY) {
      return res.status(500).json({ 
        error: 'OPENAI_API_KEY 환경변수가 설정되지 않았습니다. Railway에서 환경변수를 설정해주세요.' 
      });
    }

    // OpenAI API 호출 로직은 실제 배포시 구현
    // 현재는 더미 데이터 반환
    const fallbackResult = {
      query_analysis: `"${query}" - 사용자의 질문을 분석했습니다.`,
      target_description: '요청하신 조건에 맞는 고객군을 찾았습니다.',
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
      business_insights: [
        '고소득층 타겟팅으로 마케팅 ROI 향상 가능',
        '프리미엄 상품 및 서비스 추천 기회 확대'
      ],
      estimated_target_size: '15-20%',
      marketing_recommendations: [
        '개인화된 프리미엄 서비스 제안',
        '고급 브랜드 파트너십 마케팅 진행'
      ]
    };

    res.json(fallbackResult);
  } catch (error) {
    console.error('API Error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Start server
app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
  console.log(`Environment: ${process.env.NODE_ENV || 'development'}`);
});