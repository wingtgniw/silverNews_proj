# chat_page.py
def chat_page():
    import sys
    import os
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    import re
    import warnings
    import json
    import streamlit as st
    from dotenv import load_dotenv
    import openai
    from langchain.prompts import PromptTemplate
    from langchain_openai import ChatOpenAI
    from langchain.callbacks.base import BaseCallbackHandler
    from streamlit_chat import message
    from DB.newsletter import get_newsletter_keywords_by_id

    # 1. 스트리밍 핸들러 정의
    class StreamHandler(BaseCallbackHandler):
        def __init__(self, container):
            self.container = container
            self.output = ""

        def on_llm_new_token(self, token: str, **kwargs) -> None:
            self.output += token
            self.container.markdown(self.output)

    # 2. 환경 설정 및 초기화
    load_dotenv()
    warnings.filterwarnings("ignore", category=UserWarning)

    api_key = os.getenv("OPENAI_API_KEY")
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7, api_key=api_key, streaming=True)

    prompt_template = PromptTemplate(
        input_variables=["keyword"],
        template="""'{keyword}' 키워드에 대해 사용자가 ChatGPT에 물어볼 수 있는 다양한 질문 5개를 만들어줘. 
각 문장은 1줄로 명확하게 작성해줘.
출력 형식은 번호 없이, 질문 5개를 줄바꿈으로 나열해줘."""
    )

    def categorize_keywords_with_gpt(api_key: str, keywords: list[str]) -> dict:
        llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.3, api_key=api_key)
        template = PromptTemplate(
            input_variables=["keywords"],
            template="""
            아래는 건강과 의학 분야 키워드 목록입니다. 의미상 유사한 것끼리 묶어서 카테고리 이름을 붙이고, JSON 형식으로 출력해줘.

            키워드: {keywords}

            출력 형식 예시:
            {{
            "혈액 응고 관련": ["혈전", "응고", "혈소판"],
            "질환 이름": ["뇌졸중", "심근경색"]
            }}
            """
        )
        chain = template | llm
        response = chain.invoke({"keywords": ", ".join(keywords)})
        try:
            return json.loads(response.content)
        except Exception:
            return {"기타": keywords}

    # 3. 키워드 불러오기 및 카테고리화
    newsletter_id = 1
    raw_keywords = get_newsletter_keywords_by_id(newsletter_id)
    keyword_list = []
    if raw_keywords:
        lines = raw_keywords.strip().splitlines()
        for line in lines:
            match = re.match(r"^\d+\.\s*(.+)", line.strip())
            if match:
                keyword_list.append(match.group(1).strip())
    categorized_keywords = categorize_keywords_with_gpt(api_key, keyword_list)
    st.session_state.categorized_keywords = categorized_keywords

    # 4. 세션 상태 초기화
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "generated_prompts" not in st.session_state:
        st.session_state.generated_prompts = []
    if "pending_prompt_question" not in st.session_state:
        st.session_state.pending_prompt_question = None
    if "trigger_from_prompt" not in st.session_state:
        st.session_state.trigger_from_prompt = False

    for field, default in [("gender", ""), ("age", ""), ("height", ""), ("weight", "")]:
        if field not in st.session_state:
            st.session_state[field] = default

    # 5. 건강 정보 입력
    with st.expander("👤 건강 정보 입력 (선택)"):
        with st.form(key="health_form"):
            gender = st.selectbox("성별", ["", "남성", "여성"], index=["", "남성", "여성"].index(st.session_state.get("gender", "")))
            age = st.text_input("나이 (숫자만)", value=st.session_state.get("age", ""))
            height = st.text_input("키 (cm)", value=st.session_state.get("height", ""))
            weight = st.text_input("몸무게 (kg)", value=st.session_state.get("weight", ""))

            submitted = st.form_submit_button("✅ 저장하기")
            if submitted:
                st.session_state["gender"] = gender
                st.session_state["age"] = age
                st.session_state["height"] = height
                st.session_state["weight"] = weight
                st.success("건강 정보가 저장되었습니다.")


    def get_health_context():
        return f"사용자 정보: 성별={st.session_state.gender}, 나이={st.session_state.age}세, 키={st.session_state.height}cm, 몸무게={st.session_state.weight}kg"

    # 6. UI 및 질문 흐름
    st.title("키워드 기반 프롬프트 & 건강 챗봇")

    if st.session_state.get("categorized_keywords"):
        st.markdown("### 🔍 키워드를 클릭해 질문 예시를 생성하세요")
        for category, words in st.session_state.categorized_keywords.items():
            with st.expander(f"📂 {category}"):
                kw_cols = st.columns(4)
                for i, kw in enumerate(words):
                    if kw_cols[i % 4].button(kw, key=f"kw_btn_{category}_{i}"):
                        chain = prompt_template | llm
                        with st.spinner(f"'{kw}' 키워드로 질문 예시 생성 중..."):
                            response = chain.invoke({"keyword": kw})
                            prompts = response.content.strip().split("\n")
                            st.session_state.generated_prompts = [p.strip() for p in prompts if p.strip()]

    prompts = st.session_state.get("generated_prompts", [])
    if prompts:
        st.markdown("### 💡 프롬프트를 클릭하면 아래에서 답변을 받을 수 있어요")
        cols = st.columns(2)
        for idx, prompt in enumerate(prompts):
            if cols[idx % 2].button(prompt):
                st.session_state.pending_prompt_question = prompt
                st.session_state.trigger_from_prompt = True
                st.rerun()

    st.markdown("### ✏️ 직접 질문하기")
    user_input = st.text_input("질문을 입력해보세요", key="direct_input")
    if st.button("답변 받기", key="direct_submit") and user_input.strip():
        context = get_health_context()
        full_prompt = context + "\n질문: " + user_input.strip()
        with st.spinner("답변 생성 중..."):
            placeholder = st.empty()
            handler = StreamHandler(placeholder)
            llm_with_stream = ChatOpenAI(
                model="gpt-3.5-turbo",
                temperature=0.7,
                api_key=api_key,
                streaming=True,
                callbacks=[handler],
            )
            response = llm_with_stream.invoke(full_prompt)
            st.session_state.chat_history.append((user_input.strip(), response.content))

    if st.session_state.trigger_from_prompt and st.session_state.pending_prompt_question:
        context = get_health_context()
        prompt_question = st.session_state.pending_prompt_question
        full_prompt = context + "\n질문: " + prompt_question
        with st.spinner("답변 생성 중..."):
            placeholder = st.empty()
            handler = StreamHandler(placeholder)
            llm_with_stream = ChatOpenAI(
                model="gpt-3.5-turbo",
                temperature=0.7,
                api_key=api_key,
                streaming=True,
                callbacks=[handler],
            )
            response = llm_with_stream.invoke(full_prompt)
            st.session_state.chat_history.append((prompt_question, response.content))
        st.session_state.trigger_from_prompt = False
        st.session_state.pending_prompt_question = None

    if st.session_state.chat_history:
        st.markdown("---")
        st.subheader("💬 대화 기록")
        for idx, (q, a) in enumerate(st.session_state.chat_history):
            message(q, is_user=True, key=f"user_{idx}")
            message(a, is_user=False, key=f"bot_{idx}")
