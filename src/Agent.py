import os
import asyncio
from dotenv import load_dotenv
from langchain_community.llms import LlamaCpp
from langchain_classic.agents import AgentExecutor, create_react_agent
from langchain_classic.tools import Tool
from langchain_core.prompts import PromptTemplate
from ConnectMCP import Context7Manager

async def run_analysis_agent():
    load_dotenv()
    
    file_path = os.environ.get('FILE_PATH')
    
    ctx7 = Context7Manager()
    await ctx7.connect()

    # LangChain용 도구 생성
    tools = [
        Tool(
            name="search_library_docs",
            func=lambda q: asyncio.run(ctx7.search_docs(q)),
            description="특정 라이브러리의 최신 문서와 모범 사례를 검색할 때 사용합니다. 라이브러리 이름을 입력하세요."
        )
    ]

    # 모델 설정 
    llm = LlamaCpp(
        model_path=os.environ.get('MODEL_PATH'),
        n_ctx=8192,
        rope_freq_base=500000,   # Llama 3 기본값은 500000입니다.
        rope_freq_scale=1.0,     # 상황에 따라 0.5~1.0 사이 조정
        n_gpu_layers=-1,         # GPU 사용시 -1, CPU 사용시 0   
        temperature=0.1,         # 너무 낮으면(0) 오히려 반복될 때가 있음
        repeat_penalty=1.2,      # [핵심] 반복될 경우 벌점을 줘서 다른 단어를 쓰게 함
        top_p=0.9,               # 상위 확률 단어 중에서 선택
        last_n_tokens_size=64,   # 최근 64개 토큰을 기억해서 반복 여부 판단,
        n_batch=512,
        verbose=False
    )

    # ReAct 에이전트용 프롬프트 (Context7 문서 반영을 유도)
    template = """
    당신은 20년차 소프트웨어 아키텍트입니다.
    제공된 코드를 분석할 때, 사용된 라이브러리의 최신 버전 문서를 확인하여 비즈니스 가치와 유지보수성 관점에서 보고서를 작성하세요.

    사용 가능한 도구: {tool_names}
    도구 설명: {tools}

    분석 프로세스:
    1. 코드에서 사용된 주요 외부 라이브러리를 식별합니다.
    2. 'search_library_docs' 도구를 사용하여 해당 라이브러리의 최신 문서나 권장 사항을 가져옵니다.
    3. 가져온 문서 내용과 코드를 비교하여 분석합니다.

    형식:
    Question: 분석할 코드 내용
    Thought: 어떤 라이브러리를 검색해야 할까?
    Action: 도구 선택 (search_library_docs)
    Action Input: 라이브러리 이름
    Observation: 도구의 결과(문서 내용)
    ... (이 과정 반복 가능)
    Thought: 이제 최종 답변을 작성할 수 있습니다.
    Final Answer: 최종 분석 보고서 (기존 필수 분석 항목 포함)

    분석 대상 코드:
    {input}

    {agent_scratchpad}
    """
    prompt = PromptTemplate.from_template(template)
    agent = create_react_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(
        agent=agent, 
        tools=tools, 
        verbose=True, 
        handle_parsing_errors=True,
        max_iterations=5, # 최대 5회까지만 도구 사용/생각 허용
        early_stopping_method="generate"
    )

    with open(file_path, "r", encoding="UTF-8") as f:
        code_content = f.read()

    # 실행
    print(f"--- Context7 기반 '{file_path}' 심층 분석 시작 ---")
    result = await agent_executor.ainvoke({"input": code_content})
    
    await ctx7.close()
    return result["output"]

if __name__ == "__main__":
    # 비동기 실행
    final_report = asyncio.run(run_analysis_agent())
    print("\n\n" + "="*50)
    print("최종 심층 분석 보고서")
    print("="*50)
    print(final_report)