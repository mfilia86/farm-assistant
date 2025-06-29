# VS Code + Python 설정 확인용 테스트 코드
# 파일명: test_setup.py

import sys
import json
from datetime import datetime

print("=" * 50)
print("🐷 농장 도우미 개발환경 테스트")
print("=" * 50)

# 1. Python 버전 확인
print(f"✅ Python 버전: {sys.version}")
print(f"✅ Python 경로: {sys.executable}")

# 2. 기본 변수 및 함수 테스트
farm_name = "행복농장"
pig_count = 150
today = datetime.now()

def calculate_daily_feed(pig_count):
    """돼지 일일 사료량 계산 (kg)"""
    feed_per_pig = 2.5  # 돼지 1마리당 2.5kg
    total_feed = pig_count * feed_per_pig
    return total_feed

# 3. 데이터 처리 테스트
farm_data = {
    "농장명": farm_name,
    "돼지수": pig_count,
    "일일사료량": calculate_daily_feed(pig_count),
    "테스트날짜": today.strftime("%Y-%m-%d %H:%M:%S")
}

print(f"\n📊 농장 정보:")
print(f"   농장명: {farm_data['농장명']}")
print(f"   돼지수: {farm_data['돼지수']}마리")
print(f"   일일 사료량: {farm_data['일일사료량']}kg")
print(f"   테스트 시간: {farm_data['테스트날짜']}")

# 4. JSON 처리 테스트 (Claude API 응답 형식과 유사)
mock_ai_response = '{"intent": "사료량_조회", "period": "오늘", "location": null}'
try:
    parsed_response = json.loads(mock_ai_response)
    print(f"\n🤖 AI 응답 파싱 테스트:")
    print(f"   의도: {parsed_response['intent']}")
    print(f"   기간: {parsed_response['period']}")
    print(f"   위치: {parsed_response['location']}")
    print("   ✅ JSON 파싱 성공!")
except json.JSONDecodeError as e:
    print(f"   ❌ JSON 파싱 실패: {e}")

# 5. 에러 처리 테스트
try:
    result = 10 / 2
    print(f"\n🧮 계산 테스트: 10 ÷ 2 = {result}")
    print("   ✅ 계산 정상 작동!")
except Exception as e:
    print(f"   ❌ 계산 오류: {e}")

# 6. 리스트/반복문 테스트
pen_numbers = [1, 2, 3, 4, 5]
print(f"\n🏠 돈방 상태 시뮬레이션:")
for pen in pen_numbers:
    status = "정상" if pen % 2 == 1 else "점검필요"
    print(f"   {pen}번 돈방: {status}")

print("\n" + "=" * 50)
print("🎉 모든 테스트 완료!")
print("VS Code + Python 설정이 정상적으로 되었습니다.")
print("이제 농장 도우미 개발을 시작할 수 있어요!")
print("=" * 50)

# 사용자 입력 테스트
print("\n마지막 테스트: 농장 이름을 입력해보세요!")
user_input = input("농장 이름: ")
print(f"입력하신 농장명: '{user_input}'")
print("✅ 사용자 입력도 정상 작동합니다!")