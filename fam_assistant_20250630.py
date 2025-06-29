#프로토타입을 내가 만들 수 있는지 알아보기 위해 간단한 질문 답변 프로그램을 클로드를 통해 만들어 보았다.
#2025-06-30

from dotenv import load_dotenv
import anthropic
import json

# .env 파일에서 환경변수 로드
load_dotenv()

def analyze_farm_question(user_question):
    """
    농장 질문을 분석하고 답변하는 함수
    """
    client = anthropic.Anthropic()
    
    # 질문 분석을 위한 프롬프트
    prompt = f"""
농장 관리 질문을 분석해주세요.

질문: "{user_question}"

다음 중 하나로 분류해주세요:
분만율_조회, 폐사율_조회, 사료량_조회, 체중_조회, 일반_질문, 돼지 종류

JSON 형식으로만 답변:
{{"pig_type":돼지 종류, "intent": "분류결과", "period": "기간정보", "location": "장소정보"}}
"""

    try:
        # 1단계: 질문 의도 파악
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=100,
            messages=[{"role": "user", "content": prompt}]
        )
        
        # JSON 파싱
        intent_data = json.loads(response.content[0].text.strip())
        print(f"✅ 질문 분석 완료: {intent_data}")
        
        # 2단계: 가상의 농장 데이터로 답변 생성
        farm_data = get_mock_farm_data(intent_data)
        
        # 3단계: 자연스러운 답변 생성
        answer = generate_natural_answer(intent_data, farm_data)
        
        return answer
        
    except json.JSONDecodeError as e:
        return "죄송해요, 질문을 이해하지 못했어요. 다시 질문해주세요."
    except Exception as e:
        return f"오류가 발생했어요: {e}"

def get_mock_farm_data(intent_data):
    """
    가상의 농장 데이터 생성 (실제로는 엑셀/DB에서 읽어올 예정)
    """
    mock_data = {
        "분만율_조회": {
            "current_month": 85,
            "last_month": 82,
            "average": 80
        },
        "폐사율_조회": {
            "current_month": 2.1,
            "last_month": 2.5,
            "average": 2.3
        },
        "사료량_조회": {
            "daily_amount": 450,
            "monthly_total": 13500,
            "cost": 2800000
        },
        "체중_조회": {
            "average_weight": 85,
            "target_weight": 90,
            "growth_rate": "좋음"
        }
    }
    
    intent = intent_data.get("intent", "일반_질문")
    return mock_data.get(intent, {"message": "데이터가 없습니다"})

def generate_natural_answer(intent_data, farm_data):
    """
    Claude를 사용해서 자연스러운 답변 생성
    """
    client = anthropic.Anthropic()
    
    # 답변 생성 프롬프트
    prompt = f"""
농장 도우미로서 친근하고 유용한 답변을 해주세요.

질문 의도: {intent_data}
농장 데이터: {farm_data}

농장주에게 도움이 되는 자연스러운 한국어로 답변해주세요.
전문용어보다는 쉬운 말로, 격려나 조언도 포함해주세요.
"""

    try:
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=200,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.content[0].text.strip()
        
    except Exception as e:
        return f"답변 생성 중 오류: {e}"

def main():
    """
    메인 프로그램 - 사용자와 대화
    """
    print("🐷 농장 도우미에 오신 걸 환영합니다!")
    print("농장에 대해 궁금한 걸 물어보세요.")
    print("(종료하려면 'quit' 또는 '종료'를 입력하세요)")
    print("-" * 50)
    
    while True:
        # 사용자 질문 입력받기
        user_question = input("\n💬 질문: ").strip()
        
        # 종료 조건
        if user_question.lower() in ['quit', 'exit', '종료', '끝']:
            print("👋 농장 도우미를 이용해주셔서 감사합니다!")
            break
        
        # 빈 입력 체크
        if not user_question:
            print("❓ 질문을 입력해주세요.")
            continue
        
        print("🤔 분석 중...")
        
        # 질문 분석 및 답변
        answer = analyze_farm_question(user_question)
        
        print(f"🤖 답변: {answer}")
        print("-" * 50)

if __name__ == "__main__":
    # 프로그램 시작 전 API 연결 테스트
    try:
        load_dotenv()
        client = anthropic.Anthropic()
        print("✅ Claude API 연결 확인 완료!")
        
        # 메인 프로그램 실행
        main()
        
    except Exception as e:
        print(f"❌ API 연결 실패: {e}")
        print("📝 .env 파일에 ANTHROPIC_API_KEY가 올바르게 설정되어 있는지 확인해주세요.")