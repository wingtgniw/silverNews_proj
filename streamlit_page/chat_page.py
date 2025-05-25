# chat_page.py
def chat_page():
    import streamlit as st
    from dotenv import load_dotenv
    import os
    import warnings
    from openai import OpenAI
    from langchain.prompts import PromptTemplate
    from langchain_openai import ChatOpenAI

    load_dotenv()
    warnings.filterwarnings("ignore", category=UserWarning)

    api_key = os.getenv("OPENAI_API_KEY")
    client = OpenAI(api_key=api_key)
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7, api_key=api_key)

    generation_template = PromptTemplate(
        input_variables=["keyword"],
        template="""
'{keyword}' 키워드에 대해 사용자가 ChatGPT에 물어볼 수 있는 다양한 질문 5개를 만들어줘. 
각 문장은 1줄로 명확하게 작성해줘.
출력 형식은 번호 없이, 질문 5개를 줄바꿈으로 나열해줘.
"""
    )
    answer_template = PromptTemplate(
        input_variables=["question"],
        template="{question} 에 대한 답변을 해줘."
    )
    answer_chain = answer_template | llm

    if "page" not in st.session_state:
        st.session_state.page = 2

    def go_to_page(page_num):
        st.session_state.page = page_num

    if st.session_state.page == 2:
        st.title("프롬프트 자동 생성기")
        keyword = st.text_input("키워드를 입력하세요 (예: 고혈압)", value=st.session_state.get("keyword", ""))

        if st.button("프롬프트 생성하기") and keyword.strip():
            st.session_state.keyword = keyword
            generation_chain = generation_template | llm
            response = generation_chain.invoke({"keyword": keyword})
            prompts = response.content.strip().split("\n")
            st.session_state.generated_prompts = [p.strip() for p in prompts if p.strip()]

        prompts = st.session_state.get("generated_prompts", [])
        if prompts:
            st.markdown("### 생성된 프롬프트 선택")
            for p in prompts:
                if st.button(p):
                    st.session_state.selected_prompt = p
                    go_to_page(3)

    elif st.session_state.page == 3:
        st.title("프롬프트 실행 결과")
        question = st.session_state.get("selected_prompt", "")
        result = answer_chain.invoke({"question": question})

        st.markdown("### 선택된 프롬프트")
        st.success(question)

        st.markdown("### 요약 기사")
        st.write(result.content[:150] + "...")

        st.markdown("### 상세 기사")
        st.write(result.content)

        st.button("← 다시 키워드 입력하기", on_click=lambda: go_to_page(2))
