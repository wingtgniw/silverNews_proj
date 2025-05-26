from dotenv import load_dotenv
import os
load_dotenv()

import streamlit as st
from streamlit_option_menu import option_menu
from DB import init_db
from routers import show_articles, crawling_articles_page, newsletter_page
from streamlit_page.chat_page import chat_page
# from fact_checker import agent

# 데이터베이스 초기화
if st.session_state.get("DB") is None:
    init_db()
    st.session_state["init_db"] = True
    st.session_state["use_reranker"] = True
    # st.session_state["fact_checker"] = agent

# URL 파라미터 확인
if "id" in st.query_params:
    st.session_state["menu"] = "뉴스레터"

with st.sidebar:
    menu = option_menu(
        menu_title="",
        options=["크롤링", "기사", "뉴스레터", "아카이브", "채팅"],
        icons=["search", "newspaper", "envelope", "archive", "chat"],
        default_index=["크롤링", "기사", "뉴스레터", "아카이브", "채팅"].index(st.session_state.get("menu", "크롤링"))
    )

if menu == "크롤링":
    crawling_articles_page()
elif menu == "기사":
    show_articles()
elif menu == "뉴스레터":
    newsletter_page()
elif menu == "아카이브":
    # archive_page()
    st.write("아카이브")
elif menu == "채팅":
    chat_page()
    #st.write("채팅")
