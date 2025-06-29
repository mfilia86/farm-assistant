import streamlit as st
import anthropic
import json
import time
import os

# 페이지 설정
st.set_page_config(
    page_title="🐷 농장 도우미 AI",
    page_icon="🐷",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS 스타일링 + JavaScript
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(90deg, #4CAF50, #2E7D32);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid #4CAF50;
        background-color: #f8f9fa !important;
        color: #333333 !important;
    }
    .ai-response {
        background-color: #e8f5e8 !important;
        border-left-color: #4CAF50 !important;
        color: #1a5a1a !important;
    }
    .user-question {
        background-color: #e3f2fd !important;
        border-left-color: #2196F3 !important;
        color: #0d47a1 !important;
    }
    .chat-message strong {
        color: inherit !important;
    }
    .stats-card {
        padding: 1rem;
        background: white;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
</style>

<script>
document.addEventListener('DOMContentLoaded', function() {
    // 엔터키 이벤트 리스너 추가
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.type === 'childList') {
                const inputs = document.querySelectorAll('input[type="text"]');
                inputs.forEach(function(input) {
                    if (input.placeholder && input.placeholder.includes('엔터키로 전송')) {
                        input.addEventListener('keypress', function(e) {
                            if (e.key === 'Enter') {
                                // 전송 버튼 찾아서 클릭
                                const sendBtn = document.querySelector('[data-testid="baseButton-secondary"]');
                                if (sendBtn && sendBtn.textContent.includes('전송')) {
                                    sendBtn.click();
                                }
                            }
                        });
                    }
                });
            }
        });
    });
    
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
});
</script>
""", unsafe_allow_html=True)

def check_api_key():
    """API 키 확인"""
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        st.error("❌ ANTHROPIC_API_KEY가 설정되지 않았습니다!")
        st.info("💡 .env 파일에 ANTHROPIC_API_KEY=your_key_here 를 추가하세요")
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
            st.session_state.client = anthropic.Anthropic(api_key=api_key)
            st.success("✅ AI 연결 성공!")
        except Exception as e:
            st.error(f"❌ API 연결 실패: {e}")
            st.info("API 키를 확인해주세요")
            st.stop()

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
        },
        "포유자돈": {
            "폐사율_조회": {
                "current_rate": 8.5,
                "last_month": 9.2,
                "average": 9.0,
                "trend": "개선",
                "count": 850,
                "message": "포유자돈 폐사율이 개선되고 있어요!"
            },
            "체중_조회": {
                "average_weight": 6.5,
                "target_weight": 7.0,
                "growth_rate": "양호",
                "count": 850,
                "message": "포유자돈들이 잘 자라고 있어요"
            },
            "사료량_조회": {
                "daily_amount": 0,
                "monthly_cost": 0,
                "efficiency": "모유 수유",
                "count": 850,
                "message": "포유자돈은 모유로 키우고 있어요"
            }
        },
        "이유자돈": {
            "폐사율_조회": {
                "current_rate": 3.8,
                "last_month": 4.2,
                "average": 4.0,
                "trend": "개선",
                "count": 780,
                "message": "이유자돈 폐사율이 줄어들었어요!"
            },
            "체중_조회": {
                "average_weight": 18,
                "target_weight": 20,
                "growth_rate": "양호",
                "count": 780,
                "message": "이유자돈들이 건강하게 자라고 있어요"
            },
            "사료량_조회": {
                "daily_amount": 95,
                "monthly_cost": 480000,
                "efficiency": "양호",
                "count": 780,
                "message": "이유자돈 사료 효율이 좋아요"
            }
        },
        "육성돈": {
            "폐사율_조회": {
                "current_rate": 2.1,
                "last_month": 2.4,
                "average": 2.3,
                "trend": "개선",
                "count": 520,
                "message": "육성돈 폐사율이 개선되었어요!"
            },
            "체중_조회": {
                "average_weight": 45,
                "target_weight": 50,
                "growth_rate": "양호",
                "count": 520,
                "message": "육성돈들이 순조롭게 자라고 있어요"
            },
            "사료량_조회": {
                "daily_amount": 165,
                "monthly_cost": 850000,
                "efficiency": "양호",
                "count": 520,
                "message": "육성돈 사료 효율이 좋습니다"
            }
        },
        "비육돈": {
            "폐사율_조회": {
                "current_rate": 1.5,
                "last_month": 1.8,
                "average": 1.7,
                "trend": "개선",
                "count": 380,
                "message": "비육돈 폐사율이 낮아졌어요!"
            },
            "체중_조회": {
                "average_weight": 85,
                "target_weight": 110,
                "growth_rate": "양호",
                "count": 380,
                "message": "비육돈들이 출하 목표에 가까워지고 있어요"
            },
            "사료량_조회": {
                "daily_amount": 190,
                "monthly_cost": 1100000,
                "efficiency": "양호",
                "count": 380,
                "message": "비육돈 사료 효율이 좋습니다"
            }
        }
    }
    
    # 전체 데이터 (모든 돼지 종류 합계)
    if pig_type == "전체":
        total_data = {
            "분만율_조회": pig_data["모돈"]["분만율_조회"],
            "폐사율_조회": {
                "current_rate": 2.8,
                "last_month": 3.2,
                "average": 3.0,
                "trend": "개선",
                "count": 2650,
                "message": "전체 농장 폐사율이 개선되고 있어요!"
            },
            "사료량_조회": {
                "daily_amount": 630,
                "monthly_cost": 3630000,
                "efficiency": "양호",
                "count": 2650,
                "message": "전체 사료 사용량이 적정 수준입니다"
            },
            "체중_조회": {
                "average_weight": "종류별 상이",
                "target_weight": "종류별 상이",
                "growth_rate": "양호",
                "count": 2650,
                "message": "전체적으로 돼지들이 건강하게 자라고 있어요"
            },
            "일반_질문": {
                "message": "농장에 대한 구체적인 질문을 해주세요"
            }
        }
        return total_data.get(intent, total_data["일반_질문"])
    
    # 특정 돼지 종류 데이터
    if pig_type in pig_data and intent in pig_data[pig_type]:
        return pig_data[pig_type][intent]
    
    return {"message": f"{pig_type}에 대한 {intent} 데이터가 없습니다."}

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
        # 자돈이라고 하면 모든 새끼돼지를 의미할 수 있음
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

        response = st.session_state.client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=250,
            messages=[{"role": "user", "content": answer_prompt}]
        )
        
        return response.content[0].text.strip(), pig_type, intent, farm_data
        
    except Exception as e:
        return f"죄송해요, 오류가 발생했습니다: {str(e)}", None, None, None

def display_farm_stats():
    """농장 현황 대시보드"""
    st.sidebar.markdown("## 📊 농장 현황")
    
    # 전체 현황
    st.sidebar.markdown("### 🏠 전체 현황")
    col1, col2 = st.sidebar.columns(2)
    with col1:
        st.metric("총 사육두수", "2,650두", "")
        st.metric("전체 폐사율", "2.8%", "-0.4%")
    with col2:
        st.metric("분만율(모돈)", "85%", "3%")
        st.metric("월 사료비", "363만원", "")
    
    # 돼지 종류별 현황
    st.sidebar.markdown("### 🐷 종류별 현황")
    
    pig_stats = {
        "모돈": {"count": 120, "status": "양호"},
        "포유자돈": {"count": 850, "status": "양호"},
        "이유자돈": {"count": 780, "status": "양호"},
        "육성돈": {"count": 520, "status": "양호"},
        "비육돈": {"count": 380, "status": "출하준비"}
    }
    
    for pig_type, data in pig_stats.items():
        st.sidebar.markdown(f"**{pig_type}**: {data['count']}두 ({data['status']})")
    
    # 주요 알림
    st.sidebar.markdown("### 🔔 주요 알림")
    st.sidebar.success("✅ 전체 폐사율 개선")
    st.sidebar.info("📈 모돈 분만율 상승")
    st.sidebar.warning("⚠️ 비육돈 출하 예정")

def main():
    """메인 애플리케이션"""
    
    # 헤더
    st.markdown("""
    <div class="main-header">
        <h1>🐷 농장 도우미 AI</h1>
        <p>농장 현황을 쉽게 확인하고 관리하세요</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 사이드바 농장 현황
    display_farm_stats()
    
    # 예시 질문
    st.sidebar.markdown("## 💡 예시 질문")
    example_questions = [
        "모돈 분만율 어때?",
        "이유자돈 폐사율 좀 알려줘",
        "비육돈 사료비 얼마나 나왔어?",
        "육성돈 체중은 어떻게 돼?",
        "포유자돈 상태는?",
        "전체 농장 현황 알려줘"
    ]
    
    for question in example_questions:
        if st.sidebar.button(question, key=f"sidebar_{question}"):
            # 사용자 질문 추가
            st.session_state.messages.append({"role": "user", "content": question})
            
            # AI 답변 생성
            with st.spinner("🤔 분석 중..."):
                try:
                    answer, pig_type, intent_data, farm_data = analyze_and_respond(question)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                except Exception as e:
                    st.session_state.messages.append({"role": "assistant", "content": f"오류가 발생했습니다: {str(e)}"})
            
            st.rerun()
    
    # 메인 채팅 인터페이스
    st.markdown("## 💬 농장에 대해 궁금한 걸 물어보세요")
    
    # 이전 대화 기록 표시
    for message in st.session_state.messages:
        if message["role"] == "user":
            # 사용자 메시지
            st.markdown("""
            <div style="background-color: #e3f2fd; padding: 1rem; border-radius: 10px; margin: 1rem 0; border-left: 4px solid #2196F3; color: #0d47a1;">
                <strong style="color: #0d47a1;">👨‍🌾 농장주:</strong> """ + message["content"] + """
            </div>
            """, unsafe_allow_html=True)
        else:
            # AI 메시지  
            st.markdown("""
            <div style="background-color: #e8f5e8; padding: 1rem; border-radius: 10px; margin: 1rem 0; border-left: 4px solid #4CAF50; color: #1a5a1a;">
                <strong style="color: #1a5a1a;">🤖 농장 도우미:</strong> """ + message["content"] + """
            </div>
            """, unsafe_allow_html=True)
    
    # 질문 입력 - chat_input 사용 (엔터키 자동 지원)
    user_input = st.chat_input("농장에 대해 궁금한 것을 물어보세요... (엔터키로 전송)")
    
    # 예시 질문 버튼들
    st.markdown("**💡 빠른 질문:**")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("모돈 분만율", use_container_width=True):
            user_input = "모돈 분만율 어때?"
    with col2:
        if st.button("이유자돈 폐사율", use_container_width=True):
            user_input = "이유자돈 폐사율 좀 알려줘"
    with col3:
        if st.button("비육돈 체중", use_container_width=True):
            user_input = "비육돈 체중은 어떻게 돼?"
    
    # 질문 처리 - chat_input은 엔터키 누르면 자동으로 값이 반환됨
    if user_input and user_input.strip():
        # 중복 처리 방지
        if user_input != st.session_state.get('last_processed_message', ''):
            st.session_state.last_processed_message = user_input
            
            # 사용자 질문 추가
            st.session_state.messages.append({"role": "user", "content": user_input})
            
            # 로딩 상태 표시
            with st.spinner("🤔 분석 중..."):
                try:
                    # AI 답변 생성
                    answer, pig_type, intent_data, farm_data = analyze_and_respond(user_input)
                    
                    # AI 답변 추가
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                except Exception as e:
                    st.session_state.messages.append({"role": "assistant", "content": f"오류가 발생했습니다: {str(e)}"})
            
            # 페이지 새로고침
            st.rerun()
    
    # 디버깅 정보 (개발 중에만 사용)
    with st.expander("🔧 디버깅 정보", expanded=False):
        st.write("메시지 개수:", len(st.session_state.messages))
        st.write("마지막 처리된 메시지:", st.session_state.get('last_processed_message', ''))
        if st.session_state.messages:
            st.write("최근 메시지:", st.session_state.messages[-1])
    
    # 대화 기록 초기화 버튼
    if st.button("🗑️ 대화 기록 지우기", use_container_width=True):
        st.session_state.messages = []
        st.session_state.last_processed_message = ""
        st.rerun()
    
    # 하단 정보
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("🎯 **정확한 분석**\n실시간 농장 데이터 기반")
    
    with col2:
        st.success("💬 **쉬운 대화**\n전문용어 없이 자연스럽게")
    
    with col3:
        st.warning("📈 **성과 개선**\n데이터 기반 농장 최적화")

if __name__ == "__main__":
    initialize_session_state()
    main()