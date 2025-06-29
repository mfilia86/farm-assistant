import streamlit as st
import anthropic
import json
import time
import os

def check_api_key():
    """API 키 확인"""
    # Streamlit secrets에서 먼저 확인
    api_key = None
    
    try:
        api_key = st.secrets["ANTHROPIC_API_KEY"]
    except (KeyError, FileNotFoundError):
        # 환경변수에서 확인
        api_key = os.getenv('ANTHROPIC_API_KEY')
    
    if not api_key:
        st.error("❌ ANTHROPIC_API_KEY가 설정되지 않았습니다!")
        st.info("💡 Streamlit Cloud의 Secrets에서 API 키를 설정해주세요")
        st.stop()
    
    return api_key

def initialize_session_state():
    """세션 상태 초기화"""
    if 'messages' not in st.session_state:
        st.session_state.messages = []
        
    if 'last_processed_message' not in st.session_state:
        st.session_state.last_processed_message = ""
    
    if 'client' not in st.session_state:
        try:
            api_key = check_api_key()
            # 최신 anthropic 라이브러리 방식으로 클라이언트 생성
            st.session_state.client = anthropic.Anthropic(
                api_key=api_key
                # proxies 매개변수 제거됨
            )
            st.success("✅ AI 연결 성공!")
        except Exception as e:
            st.error(f"❌ API 연결 실패: {e}")
            st.info("API 키를 확인해주세요")
            st.stop()

def analyze_and_respond(user_question):
    """질문 분석 및 답변 생성"""
    try:
        # 1단계: 돼지 종류와 의도 분류
        pig_type, intent = classify_pig_type_and_intent(user_question)
        
        # 2단계: 농장 데이터 조회
        farm_data = get_mock_farm_data(intent, pig_type)
        
        # 3단계: AI 답변 생성
        if intent != "일반_질문":
            # 돼지 종류 정보 추가
            pig_info = f"({pig_type})" if pig_type != "전체" else ""
            
            answer_prompt = f"""
농장 도우미로서 친근하고 유용한 답변을 해주세요.

농장주 질문: {user_question}
돼지 종류: {pig_type}
농장 데이터: {farm_data}

조건:
- 농장주에게 친근하게 말하세요
- 구체적인 숫자와 함께 설명하세요
- 돼지 종류를 명확히 언급하세요
- 간단하고 이해하기 쉽게 답변하세요
- 200자 이내로 답변하세요
"""
        else:
            answer_prompt = f"""
농장 도우미로서 다음 질문에 답변해주세요.

질문: {user_question}

조건:
- 돼지 농장과 관련된 도움을 주세요
- 돼지 종류(모돈, 포유자돈, 이유자돈, 육성돈, 비육돈)에 대해 설명할 수 있어요
- 친근하고 이해하기 쉽게 답변하세요
- 200자 이내로 답변하세요
"""

        # 최신 anthropic API 방식 사용
        response = st.session_state.client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=250,
            messages=[{"role": "user", "content": answer_prompt}]
        )
        
        return response.content[0].text.strip(), pig_type, intent, farm_data
        
    except Exception as e:
        return f"죄송해요, 오류가 발생했습니다: {str(e)}", None, None, None

def classify_pig_type_and_intent(question):
    """돼지 종류와 의도 분류"""
    question_lower = question.lower()
    
    # 돼지 종류 분류
    pig_type = "전체"  # 기본값
    
    if "모돈" in question_lower:
        pig_type = "모돈"
    elif "포유자돈" in question_lower or "포유" in question_lower:
        pig_type = "포유자돈"
    elif "이유자돈" in question_lower or "이유" in question_lower:
        pig_type = "이유자돈"
    elif "육성돈" in question_lower or "육성" in question_lower:
        pig_type = "육성돈"
    elif "비육돈" in question_lower or "비육" in question_lower:
        pig_type = "비육돈"
    elif "자돈" in question_lower:
        pig_type = "자돈전체"
    
    # 의도 분류
    intent = "일반_질문"
    if "분만" in question_lower or "새끼" in question_lower:
        intent = "분만율_조회"
    elif "폐사" in question_lower or "죽" in question_lower:
        intent = "폐사율_조회"
    elif "사료" in question_lower or "먹이" in question_lower:
        intent = "사료량_조회"
    elif "체중" in question_lower or "무게" in question_lower or "몸무게" in question_lower:
        intent = "체중_조회"
    
    return pig_type, intent

def get_mock_farm_data(intent, pig_type="전체"):
    """가상 농장 데이터 생성 (돼지 종류별)"""
    # 돼지 종류별 기본 데이터
    pig_data = {
        "모돈": {
            "분만율_조회": {
                "current_rate": 85,
                "last_month": 82,
                "average": 80,
                "trend": "상승",
                "count": 120,
                "message": "모돈 분만율이 좋아졌어요!"
            },
            "폐사율_조회": {
                "current_rate": 1.2,
                "last_month": 1.5,
                "average": 1.4,
                "trend": "개선",
                "count": 120,
                "message": "모돈 폐사율이 줄어들고 있어요!"
            },
            "사료량_조회": {
                "daily_amount": 180,
                "monthly_cost": 1200000,
                "efficiency": "양호",
                "count": 120,
                "message": "모돈 사료 사용량이 적정 수준입니다"
            },
            "체중_조회": {
                "average_weight": 180,
                "target_weight": 185,
                "growth_rate": "양호",
                "count": 120,
                "message": "모돈들이 건강한 상태입니다"
            }
        }
        # 다른 돼지 종류 데이터도 동일하게...
    }
    
    # 간단한 예시만 반환
    if pig_type == "모돈" and intent in pig_data["모돈"]:
        return pig_data["모돈"][intent]
    else:
        return {
            "message": f"{pig_type}의 {intent} 정보를 확인 중입니다.",
            "current_rate": 85,
            "count": 100
        }

# 테스트용 메인 함수
if __name__ == "__main__":
    st.title("🐷 농장 도우미 AI")
    
    # 세션 상태 초기화
    initialize_session_state()
    
    # 간단한 테스트
    if st.button("AI 연결 테스트"):
        try:
            response = st.session_state.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=100,
                messages=[{"role": "user", "content": "안녕하세요"}]
            )
            st.success(f"✅ 테스트 성공: {response.content[0].text}")
        except Exception as e:
            st.error(f"❌ 테스트 실패: {e}")