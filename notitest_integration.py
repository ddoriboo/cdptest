"""
Notitest 통합 모듈
태그 기반 마케팅 메시지 생성 및 A/B 테스트 관리
"""

import json
import requests
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import hashlib
import random

class NotitestGenerator:
    """Notitest 메시지 생성 및 관리 클래스"""
    
    def __init__(self, api_key: str = None, api_endpoint: str = None):
        self.api_key = api_key
        self.api_endpoint = api_endpoint or "https://api.notitest.com/v1"
        
        # 확장된 메시지 템플릿
        self.templates = {
            'loan': {
                'tags': ['대출', '금융', '신용', '자금', '융자', '대환'],
                'personas': {
                    'high_credit': {
                        'templates': [
                            "💎 {name}님, 프리미엄 신용대출 최대 1억원까지! 연 {rate}% 특별우대",
                            "🏆 신용등급 1~2등급 전용! 무서류 모바일 완결 대출",
                            "⭐ VIP 고객님께만 제공되는 초저금리 {rate}% 신용대출"
                        ],
                        'variables': {'rate': '2.9', 'amount': '10000'}
                    },
                    'refinance': {
                        'templates': [
                            "💰 대출 이자 부담 줄이세요! 대환대출로 월 {save}만원 절약",
                            "🔄 고금리 대출을 {rate}% 저금리로! 중도상환 수수료 전액 지원",
                            "📉 여러 대출을 하나로! 통합대환으로 이자 최대 {percent}% 절감"
                        ],
                        'variables': {'rate': '3.5', 'save': '50', 'percent': '40'}
                    }
                }
            },
            'beauty': {
                'tags': ['뷰티', '화장품', '코스메틱', '미용', '스킨케어', '메이크업'],
                'personas': {
                    'premium': {
                        'templates': [
                            "💄 {brand} 신제품 단독 런칭! {name}님만을 위한 {discount}% 할인",
                            "✨ 프리미엄 안티에이징 라인 체험 키트 무료 증정",
                            "🌟 VIP 전용 뷰티 클래스 초대 + 풀세트 선물"
                        ],
                        'variables': {'brand': '샤넬', 'discount': '30'}
                    },
                    'trendy': {
                        'templates': [
                            "🎨 올해의 컬러! 트렌디한 립 컬렉션 {discount}% 세일",
                            "📸 SNS 인기템! 글로우 쿠션 + 립틴트 세트 특가",
                            "🌸 봄 신상 뷰티템 모음전! 최대 {discount}% + 사은품"
                        ],
                        'variables': {'discount': '50', 'brand': '3CE'}
                    }
                }
            },
            'travel': {
                'tags': ['여행', '항공', '호텔', '휴가', '해외', '국내여행'],
                'personas': {
                    'luxury': {
                        'templates': [
                            "✈️ {destination} 비즈니스석 특가! 마일리지 {bonus}% 추가 적립",
                            "🏖️ 5성급 리조트 패키지 {discount}% 할인 + 스파 무료 이용권",
                            "🛳️ 프리미엄 크루즈 여행! 발코니 객실 무료 업그레이드"
                        ],
                        'variables': {'destination': '파리', 'bonus': '200', 'discount': '40'}
                    },
                    'budget': {
                        'templates': [
                            "🎒 {destination} 왕복 {price}원! 초특가 항공권 오픈",
                            "🏨 호텔 깜짝 세일! 1박당 {price}원부터 + 조식 포함",
                            "🗺️ 가성비 패키지! {days}박 {nights}일 올인클루시브 {price}원"
                        ],
                        'variables': {'destination': '방콕', 'price': '199,000', 'days': '4', 'nights': '3'}
                    }
                }
            },
            'shopping': {
                'tags': ['쇼핑', '할인', '세일', '구매', '패션', '브랜드'],
                'personas': {
                    'vip': {
                        'templates': [
                            "👑 VIP 프리뷰! 시즌오프 최대 {discount}% + 추가 {extra}% 쿠폰",
                            "💳 블랙프라이데이 사전 오픈! VIP 전용 {hour}시간 단독 세일",
                            "🎁 연간 최대 혜택! 구매금액의 {cashback}% 즉시 캐시백"
                        ],
                        'variables': {'discount': '70', 'extra': '20', 'hour': '24', 'cashback': '15'}
                    },
                    'smart': {
                        'templates': [
                            "🛍️ 장바구니 상품 {discount}% 추가 할인! 오늘만 특가",
                            "⏰ 타임세일! {time}시 정각 선착순 {limit}명 반값 이벤트",
                            "📦 무료배송 + {discount}% 할인! 앱 전용 특별 혜택"
                        ],
                        'variables': {'discount': '30', 'time': '12', 'limit': '100'}
                    }
                }
            },
            'investment': {
                'tags': ['투자', '주식', '펀드', '자산', '재테크', '금융상품'],
                'personas': {
                    'beginner': {
                        'templates': [
                            "📈 투자 첫걸음! 소액으로 시작하는 {product} 가입시 {bonus}원 지급",
                            "🎯 초보자 맞춤 포트폴리오! AI가 추천하는 안정형 상품",
                            "💡 재테크 무료 강의 + 실전 투자금 {amount}원 지원"
                        ],
                        'variables': {'product': 'ETF', 'bonus': '50,000', 'amount': '100,000'}
                    },
                    'experienced': {
                        'templates': [
                            "💼 해외주식 수수료 평생 무료! 환전 우대 {rate}% 제공",
                            "🌐 글로벌 분산투자! 전문가 추천 포트폴리오 무료 구성",
                            "📊 프리미엄 리서치 무료 이용 + 세미나 VIP 초청"
                        ],
                        'variables': {'rate': '90'}
                    }
                }
            }
        }
        
        # A/B 테스트 변형
        self.ab_variations = {
            'emoji_heavy': lambda msg: self._add_more_emojis(msg),
            'urgent': lambda msg: self._add_urgency(msg),
            'personalized': lambda msg: self._add_personalization(msg),
            'benefit_focused': lambda msg: self._focus_on_benefits(msg),
            'social_proof': lambda msg: self._add_social_proof(msg)
        }
    
    def extract_advanced_tags(self, analysis_result: Dict, user_query: str) -> Dict[str, List[str]]:
        """고급 태그 추출 - 주 태그와 부 태그 구분"""
        primary_tags = []
        secondary_tags = []
        
        # 쿼리에서 직접 추출
        query_lower = user_query.lower()
        for category, info in self.templates.items():
            for tag in info['tags']:
                if tag in query_lower:
                    primary_tags.append(tag)
        
        # 추천 컬럼에서 추출
        for col in analysis_result.get('recommended_columns', []):
            col_name = col.get('column', '').lower()
            col_desc = col.get('description', '').lower()
            
            for category, info in self.templates.items():
                for tag in info['tags']:
                    if tag in col_name or tag in col_desc:
                        if col.get('priority') == 'high':
                            primary_tags.append(tag)
                        else:
                            secondary_tags.append(tag)
        
        # 비즈니스 인사이트에서 추출
        for insight in analysis_result.get('business_insights', []):
            insight_lower = insight.lower()
            for category, info in self.templates.items():
                for tag in info['tags']:
                    if tag in insight_lower:
                        secondary_tags.append(tag)
        
        return {
            'primary': list(set(primary_tags)),
            'secondary': list(set(secondary_tags))
        }
    
    def determine_persona(self, analysis_result: Dict) -> str:
        """분석 결과를 바탕으로 페르소나 결정"""
        # 고소득 관련 키워드
        if any('highincome' in str(col.get('column', '')).lower() 
               for col in analysis_result.get('recommended_columns', [])):
            return 'premium'
        
        # 신용 관련 키워드
        if any('credit' in str(col.get('column', '')).lower() 
               for col in analysis_result.get('recommended_columns', [])):
            return 'high_credit'
        
        # 가격 민감도
        if '할인' in str(analysis_result) or '특가' in str(analysis_result):
            return 'budget'
        
        return 'general'
    
    def generate_advanced_messages(
        self, 
        tags: Dict[str, List[str]], 
        analysis_result: Dict,
        user_profile: Optional[Dict] = None
    ) -> List[Dict]:
        """고급 메시지 생성 - 페르소나와 A/B 테스트 변형 포함"""
        messages = []
        persona = self.determine_persona(analysis_result)
        
        # 주 태그 기반 메시지 생성
        for category, info in self.templates.items():
            if any(tag in tags['primary'] for tag in info['tags']):
                # 페르소나별 템플릿 선택
                persona_templates = info.get('personas', {}).get(persona, {})
                if not persona_templates:
                    # 기본 페르소나 사용
                    persona_key = list(info['personas'].keys())[0]
                    persona_templates = info['personas'][persona_key]
                
                templates = persona_templates.get('templates', [])
                variables = persona_templates.get('variables', {})
                
                # 사용자 프로필 정보 추가
                if user_profile:
                    variables.update({
                        'name': user_profile.get('name', '고객'),
                        'age': user_profile.get('age', ''),
                        'gender': user_profile.get('gender', '')
                    })
                else:
                    variables['name'] = '고객'
                
                # 각 템플릿에 대해 A/B 변형 생성
                for template in templates[:2]:  # 상위 2개 템플릿만 사용
                    base_message = template.format(**variables)
                    
                    # 기본 메시지
                    messages.append({
                        'category': category,
                        'message': base_message,
                        'tags': info['tags'],
                        'priority': 'high' if category in tags['primary'] else 'medium',
                        'channel': self._determine_channel(category, persona),
                        'persona': persona,
                        'variation': 'control',
                        'test_group': 'A',
                        'timing': self._suggest_timing(category, persona)
                    })
                    
                    # A/B 테스트 변형 생성
                    for variation_name, variation_func in list(self.ab_variations.items())[:1]:
                        varied_message = variation_func(base_message)
                        messages.append({
                            'category': category,
                            'message': varied_message,
                            'tags': info['tags'],
                            'priority': 'high' if category in tags['primary'] else 'medium',
                            'channel': self._determine_channel(category, persona),
                            'persona': persona,
                            'variation': variation_name,
                            'test_group': 'B',
                            'timing': self._suggest_timing(category, persona)
                        })
        
        return messages
    
    def _determine_channel(self, category: str, persona: str) -> str:
        """카테고리와 페르소나에 따른 최적 채널 결정"""
        channel_matrix = {
            'loan': {'high_credit': 'app_push', 'refinance': 'sms', 'default': 'email'},
            'beauty': {'premium': 'kakao', 'trendy': 'app_push', 'default': 'sms'},
            'travel': {'luxury': 'email', 'budget': 'app_push', 'default': 'kakao'},
            'shopping': {'vip': 'app_push', 'smart': 'web_push', 'default': 'sms'},
            'investment': {'beginner': 'email', 'experienced': 'app_push', 'default': 'kakao'}
        }
        
        return channel_matrix.get(category, {}).get(persona, 
               channel_matrix.get(category, {}).get('default', 'sms'))
    
    def _suggest_timing(self, category: str, persona: str) -> Dict[str, Any]:
        """최적 발송 시간 제안"""
        timing_matrix = {
            'loan': {'best_time': '14:00', 'best_day': 'weekday', 'frequency': 'weekly'},
            'beauty': {'best_time': '20:00', 'best_day': 'weekend', 'frequency': 'bi-weekly'},
            'travel': {'best_time': '19:00', 'best_day': 'thursday', 'frequency': 'monthly'},
            'shopping': {'best_time': '12:00', 'best_day': 'friday', 'frequency': 'weekly'},
            'investment': {'best_time': '09:00', 'best_day': 'monday', 'frequency': 'monthly'}
        }
        
        return timing_matrix.get(category, {
            'best_time': '10:00',
            'best_day': 'weekday',
            'frequency': 'weekly'
        })
    
    def _add_more_emojis(self, message: str) -> str:
        """이모지 추가 변형"""
        emoji_map = {
            '할인': '🎉',
            '특가': '⚡',
            '무료': '🎁',
            '혜택': '💝',
            '프리미엄': '👑'
        }
        
        for word, emoji in emoji_map.items():
            if word in message and emoji not in message:
                message = message.replace(word, f"{emoji} {word}")
        
        return message + " 🎊"
    
    def _add_urgency(self, message: str) -> str:
        """긴급성 추가 변형"""
        urgency_phrases = [
            "⏰ 오늘 마감!",
            "🔥 한정 수량!",
            "⚡ 24시간 한정!",
            "🚨 마지막 기회!"
        ]
        return f"{random.choice(urgency_phrases)} {message}"
    
    def _add_personalization(self, message: str) -> str:
        """개인화 강화 변형"""
        if "{name}" not in message:
            message = "고객님, " + message
        return message.replace("고객", "소중한 고객")
    
    def _focus_on_benefits(self, message: str) -> str:
        """혜택 중심 변형"""
        benefit_prefix = "💰 최대 혜택! "
        return benefit_prefix + message
    
    def _add_social_proof(self, message: str) -> str:
        """사회적 증거 추가 변형"""
        social_proofs = [
            "🏆 10만명이 선택한",
            "⭐ 만족도 98%",
            "👥 지금 1,000명이 보는 중!",
            "✨ 베스트셀러 1위"
        ]
        return f"{random.choice(social_proofs)} {message}"
    
    def create_ab_test_config(self, messages: List[Dict], test_params: Dict) -> Dict:
        """A/B 테스트 설정 생성"""
        total_messages = len(messages)
        control_group = [msg for msg in messages if msg['test_group'] == 'A']
        test_group = [msg for msg in messages if msg['test_group'] == 'B']
        
        config = {
            'test_id': hashlib.md5(str(datetime.now()).encode()).hexdigest()[:8],
            'created_at': datetime.now().isoformat(),
            'test_duration_days': test_params.get('duration', 7),
            'test_ratio': test_params.get('ratio', 20),
            'total_variations': len(self.ab_variations),
            'groups': {
                'control': {
                    'size': len(control_group),
                    'messages': control_group
                },
                'test': {
                    'size': len(test_group),
                    'messages': test_group
                }
            },
            'success_metrics': [
                'open_rate',
                'click_rate',
                'conversion_rate',
                'revenue_per_message'
            ],
            'estimated_sample_size': self._calculate_sample_size(test_params),
            'statistical_power': 0.8,
            'confidence_level': 0.95
        }
        
        return config
    
    def _calculate_sample_size(self, test_params: Dict) -> int:
        """A/B 테스트에 필요한 샘플 사이즈 계산"""
        # 간단한 샘플 사이즈 계산 (실제로는 통계적 공식 사용)
        baseline_rate = test_params.get('baseline_rate', 0.02)  # 2% 기본 전환율
        min_detectable_effect = test_params.get('mde', 0.2)  # 20% 개선 목표
        
        # Rule of thumb: 1000 * (1/baseline_rate) * (1/mde)
        sample_size = int(1000 * (1/baseline_rate) * (1/min_detectable_effect))
        
        return min(sample_size, 100000)  # 최대 10만명으로 제한
    
    def generate_performance_prediction(self, messages: List[Dict], historical_data: Optional[Dict] = None) -> Dict:
        """메시지 성과 예측"""
        predictions = []
        
        for msg in messages:
            category = msg['category']
            channel = msg['channel']
            variation = msg['variation']
            
            # 기본 예측값 (실제로는 ML 모델 사용)
            base_rates = {
                'app_push': {'open': 0.45, 'click': 0.12, 'convert': 0.035},
                'sms': {'open': 0.98, 'click': 0.08, 'convert': 0.025},
                'email': {'open': 0.25, 'click': 0.05, 'convert': 0.015},
                'kakao': {'open': 0.65, 'click': 0.15, 'convert': 0.04},
                'web_push': {'open': 0.30, 'click': 0.07, 'convert': 0.02}
            }
            
            # 변형별 조정
            variation_multipliers = {
                'control': 1.0,
                'emoji_heavy': 1.1,
                'urgent': 1.15,
                'personalized': 1.2,
                'benefit_focused': 1.12,
                'social_proof': 1.18
            }
            
            base = base_rates.get(channel, base_rates['sms'])
            multiplier = variation_multipliers.get(variation, 1.0)
            
            prediction = {
                'message_id': hashlib.md5(msg['message'].encode()).hexdigest()[:8],
                'category': category,
                'channel': channel,
                'variation': variation,
                'predicted_open_rate': round(base['open'] * multiplier, 3),
                'predicted_click_rate': round(base['click'] * multiplier, 3),
                'predicted_conversion_rate': round(base['convert'] * multiplier, 3),
                'confidence_interval': {
                    'open_rate': [
                        round(base['open'] * multiplier * 0.9, 3),
                        round(base['open'] * multiplier * 1.1, 3)
                    ],
                    'click_rate': [
                        round(base['click'] * multiplier * 0.9, 3),
                        round(base['click'] * multiplier * 1.1, 3)
                    ]
                }
            }
            
            predictions.append(prediction)
        
        return {
            'predictions': predictions,
            'summary': {
                'avg_open_rate': round(sum(p['predicted_open_rate'] for p in predictions) / len(predictions), 3),
                'avg_click_rate': round(sum(p['predicted_click_rate'] for p in predictions) / len(predictions), 3),
                'avg_conversion_rate': round(sum(p['predicted_conversion_rate'] for p in predictions) / len(predictions), 3),
                'best_performing_variation': max(predictions, key=lambda x: x['predicted_conversion_rate'])['variation'],
                'best_channel': max(predictions, key=lambda x: x['predicted_click_rate'])['channel']
            }
        }
    
    def send_to_notitest(self, messages: List[Dict], test_config: Dict) -> Dict:
        """Notitest API로 메시지 전송"""
        if not self.api_key or not self.api_endpoint:
            return {
                'status': 'error',
                'message': 'API credentials not configured',
                'test_id': test_config['test_id']
            }
        
        try:
            # API 호출 (실제 구현 시)
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'test_config': test_config,
                'messages': messages,
                'schedule': {
                    'start_date': datetime.now().isoformat(),
                    'end_date': (datetime.now() + timedelta(days=test_config['test_duration_days'])).isoformat()
                }
            }
            
            # 실제 API 호출 (현재는 시뮬레이션)
            # response = requests.post(f"{self.api_endpoint}/campaigns/create", json=payload, headers=headers)
            
            # 시뮬레이션 응답
            return {
                'status': 'success',
                'test_id': test_config['test_id'],
                'campaign_id': hashlib.md5(str(datetime.now()).encode()).hexdigest()[:12],
                'estimated_reach': test_config['estimated_sample_size'],
                'scheduled_start': datetime.now().isoformat(),
                'api_response': 'Campaign created successfully'
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e),
                'test_id': test_config['test_id']
            }