# chat_page.py
def chat_page():
    import sys
    import os
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

    import warnings
    import streamlit as st
    from dotenv import load_dotenv
    from langchain.prompts import PromptTemplate
    from langchain_openai import ChatOpenAI
    from langchain.callbacks.base import BaseCallbackHandler
    from streamlit_chat import message

    # ───────────────────────────────
    # 1. 스트리밍 핸들러 정의
    # ───────────────────────────────
    class StreamHandler(BaseCallbackHandler):
        def __init__(self, container):
            self.container = container
            self.output = ""

        def on_llm_new_token(self, token: str, **kwargs) -> None:
            self.output += token
            self.container.markdown(self.output)

    # ───────────────────────────────
    # 2. 환경 설정 및 초기화
    # ───────────────────────────────
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

    # ───────────────────────────────
    # 3. 세션 상태 초기화
    # ───────────────────────────────
    st.session_state.keywords = [
        "가자", "이스라엘", "기아", "영양실조", "보건",
        "유니세프", "적십자", "임신부", "만성질환", "인도양부지구특별위원회"
    ]

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    if "generated_prompts" not in st.session_state:
        st.session_state.generated_prompts = []

    if "pending_prompt_question" not in st.session_state:
        st.session_state.pending_prompt_question = None

    if "trigger_from_prompt" not in st.session_state:
        st.session_state.trigger_from_prompt = False

    if "user_profile" not in st.session_state:
        st.session_state.user_profile = {
            "성별": "",
            "나이": "",
            "키": "",
            "몸무게": ""
        }

    # ───────────────────────────────
    # 4. 사용자 건강 정보 입력
    # ───────────────────────────────
    with st.expander("👤 건강 정보 입력 (선택)"):
        gender = st.selectbox("성별", ["", "남성", "여성"])
        age = st.text_input("나이 (숫자만)")
        height = st.text_input("키 (cm)")
        weight = st.text_input("몸무게 (kg)")

        st.session_state.user_profile = {
            "성별": gender,
            "나이": age,
            "키": height,
            "몸무게": weight
        }

    def get_health_context():
        info = st.session_state.user_profile
        return f"사용자 정보: 성별={info['성별']}, 나이={info['나이']}세, 키={info['키']}cm, 몸무게={info['몸무게']}kg"

    # ───────────────────────────────
    # 5. UI 및 질문 흐름
    # ───────────────────────────────
    st.title("키워드 기반 프롬프트 & 건강 챗봇")

    # 키워드별 버튼 생성
    if st.session_state.keywords:
        st.markdown("### 🔍 키워드를 클릭해 질문 예시를 생성하세요")
        kw_cols = st.columns(4)
        for i, kw in enumerate(st.session_state.keywords):
            if kw_cols[i % 4].button(kw):
                chain = prompt_template | llm
                with st.spinner(f"'{kw}' 키워드로 질문 예시 생성 중..."):
                    response = chain.invoke({"keyword": kw})
                    prompts = response.content.strip().split("\n")
                    st.session_state.generated_prompts = [p.strip() for p in prompts if p.strip()]

    # 프롬프트 → 질문 실행
    prompts = st.session_state.get("generated_prompts", [])
    if prompts:
        st.markdown("### 💡 프롬프트를 클릭하면 아래에서 답변을 받을 수 있어요")
        cols = st.columns(2)
        for idx, prompt in enumerate(prompts):
            if cols[idx % 2].button(prompt):
                st.session_state.pending_prompt_question = prompt
                st.session_state.trigger_from_prompt = True
                st.rerun()

    # 직접 질문 UI
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

    # 프롬프트 질문 → 아래에서 답변 실행
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

    # 대화 기록
    if st.session_state.chat_history:
        st.markdown("---")
        st.subheader("💬 대화 기록")
        for idx, (q, a) in enumerate(st.session_state.chat_history):
            message(q, is_user=True, key=f"user_{idx}")
            message(a, is_user=False, key=f"bot_{idx}")