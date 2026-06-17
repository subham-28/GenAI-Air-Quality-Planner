from services.rag_service import ask_guidelines
from dotenv import load_dotenv

load_dotenv()

question = "What should people do during very poor or severe AQI?"

answer = ask_guidelines(question)

print(answer)