from langchain_community.llms import LlamaCpp
from langchain_core.prompts import PromptTemplate
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# 1. 모델 설정
# 로컬에 다운로드한 GGUF 모델 파일 경로를 지정하세요.
MODEL_PATH = "./models/Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf"

llm = LlamaCpp(
model_path=MODEL_PATH,
    n_ctx=8192,
    rope_freq_base=500000, # Llama 3 기본값은 500000입니다.
    rope_freq_scale=1.0,   # 상황에 따라 0.5~1.0 사이 조정
    n_gpu_layers=-1,
    temperature=0.1,         # 너무 낮으면(0) 오히려 반복될 때가 있음
    repeat_penalty=1.2,      # [핵심] 반복될 경우 벌점을 줘서 다른 단어를 쓰게 함
    top_p=0.9,               # 상위 확률 단어 중에서 선택
    last_n_tokens_size=64,    # 최근 64개 토큰을 기억해서 반복 여부 판단,
    n_batch=512,
    verbose=False
)

# 2. 프롬프트 템플릿 정의
system_template = """
당신은 전 세계 상위 1% 수준의 소프트웨어 아키텍트이자 기술 문서 전문가입니다.
제공된 소스코드를 정적으로 분석하고, 비즈니스 가치와 유지보수성 관점에서 심층 보고서를 작성합니다.

분석 시 다음의 아키텍처 원칙을 준수하세요:
- SOLID 원칙 및 디자인 패턴 적용 여부 검토
- 시간 및 공간 복잡성(Big-O)의 효율성 평가
- 데이터 무결성 및 보안 취약점 식별
"""

user_template = """
당신은 보안 감사원 및 소프트웨어 아키텍트입니다. 다음 코드를 '비판적'으로 분석하세요.

### [분석 대상 코드]
{source_code}

### [필수 분석 항목]
1. **Business Logic Summary**: 이 코드가 해결하려는 현실의 문제는 무엇인가?
2. **Technical Debt**: 현재 코드에서 '기술적 부채'가 느껴지는 지점 3곳
3. **Security & Exception**: 예외 처리가 누락되었거나 보안상 위험한 부분
4. **Refactoring Roadmap**: 가독성과 유지보수성을 위해 즉시 변경해야 할 우선순위

**결과물에 소스코드를 그대로 포함하지 마십시오. 오직 '분석 결과'만 기술하세요.**
"""

prompt = ChatPromptTemplate.from_messages([ ("system", system_template), ("user", user_template) ])

# 3. 체인 구성 (LCEL 방식)
chain = prompt | llm | StrOutputParser()

# 4. 소스코드 로드 및 실행
def generate_documentation(file_path):
    with open(file_path, "r", encoding="UTF-8") as f:
        code_content = f.read()
    
    print(f"--- '{file_path}' 분석 중 ---")
    response = chain.invoke({"source_code": code_content})
    return response

# 사용 예시
if __name__ == "__main__":
    # 분석할 실제 파일 경로를 넣으세요.
    result = generate_documentation("my_script.py")
    print(result)