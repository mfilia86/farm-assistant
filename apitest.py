from dotenv import load_dotenv
import anthropic

# .env 파일에서 환경변수 로드
load_dotenv()

client = anthropic.Anthropic()
print("API 키 설정 완료!")