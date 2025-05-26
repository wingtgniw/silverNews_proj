import streamlit as st
from DB import *
from DocBotCrawler.news_translator.translator import kor_to_eng
from glob import glob
import json
import re
import time
from datetime import datetime

def is_korean(text):
    return bool(re.search(r"[가-힣]", text))

def crawling_articles_page():
    
    subjects = st.text_input("뉴스레터 주제:")
    button = st.button("생성 및 발송")

    # 기사 작성 시작
    if (button or subjects):
        
        # 크롤링 시작
        with st.spinner("크롤링 중..."):

            input_keyword = subjects.strip()
            
            start_time = time.time()    
            # 한글이면 영어로 번역
            if is_korean(input_keyword):
                with st.spinner("한글을 영어로 번역 중..."):
                    keyword = kor_to_eng(input_keyword)
                    st.write(f"번역된 검색어: {keyword}")
            else:
                keyword = input_keyword
            st.write(f'translate time: {time.time() - start_time}')

            start_time = time.time()
            st.session_state["crawler"].run(keyword, lang="kr")
            st.write(f'crawl time: {time.time() - start_time}') # only eng = 약 96초, with kr = 약 430초

        st.success("기사들이 크롤링 되었습니다.")

def show_articles_session():
    files = glob(f"./saved_articles_json/*.json")
    if st.session_state.get("articles") is None :
        st.session_state["articles"] = []

    generator = st.session_state['newsletter_generator']
    user_id = st.session_state["user_id"]
        
    if files:
        # chat gpt turbo 3.5 모델 사용
        if len(st.session_state["articles"]) == 0:
            for i, file in enumerate(files):
                if "usatoday" not in file:
                    continue
                with open(file, "r", encoding="utf-8") as f:
                    article = json.load(f)
                
                # st.write(article['title'])
                with st.expander(article['title']):
                    button = st.button("뉴스레터 작성", key=f"button_{i}")

                    if button:
                        with st.spinner("뉴스레터 작성 중..."):
                            rst = generator.generate_newsletter_from_article(article['content_en'])
                            RAG_rst = st.session_state["RAG_reviewer"].get_review(rst['newsletter'])
                        
                        print(RAG_rst)
                        
                        insert_newsletter(user_id, rst)
                        st.success("뉴스레터가 작성되었습니다.")

                    st.write("원문:")
                    st.write(article['url'])
                    st.write("기사 내용:")
                    st.write(article['content_kr'])


                st.session_state["articles"].append(article)
        else:
            for i, article in enumerate(st.session_state["articles"]):
                with st.expander(article['title']):
                    button = st.button("뉴스레터 작성", key=f"button_{i}")

                    st.write("원문:")
                    st.write(article['url'])
                    st.write("기사 내용:")
                    st.write(article['content_kr'])

                    if button:
                        with st.spinner("뉴스레터 작성 중..."):
                            rst = generator.generate_newsletter_from_article(article['content_en'])
                            RAG_rst = st.session_state["RAG_reviewer"].get_review(rst['newsletter'])

                        print(RAG_rst)
                        insert_newsletter(user_id, rst)
                        st.success("뉴스레터가 작성되었습니다.")
    else:
        st.info("아직 크롤링된 기사가 없습니다.")

def show_articles():
    files = glob(f"./saved_articles_json/*.json")

    generator = st.session_state['newsletter_generator']
    user_id = st.session_state["user_id"]
        
    if files:
        # chat gpt turbo 3.5 모델 사용
        for i, file in enumerate(files):
            if "usatoday" not in file:
                continue
            with open(file, "r", encoding="utf-8") as f:
                article = json.load(f)
            
            # st.write(article['title'])
            with st.expander(article['title']):
                button = st.button("뉴스레터 작성", key=f"button_{i}")

                if button:
                    with st.spinner("뉴스레터 작성 중..."):
                        newsletter_rst = generator.generate_newsletter_from_article(article['content_en'])
                        RAG_rst = st.session_state["RAG_reviewer"].get_review(newsletter_rst['newsletter'])
                    
                    insert_newsletter(user_id, newsletter_rst, RAG_rst)
                    st.success("뉴스레터가 작성되었습니다.")

                st.write("원문:")
                st.write(article['url'])
                st.write("기사 내용:")
                st.write(article['content_kr'])

    else:
        st.info("아직 크롤링된 기사가 없습니다.")

def newsletter_page():
    st.title("뉴스레터")

    # 뉴스레터 목록 조회
    newsletters = get_all_newsletters(st.session_state["user_id"])
    if newsletters:
        for i, newsletter in enumerate(newsletters):
            with st.expander(f"{newsletter['title']} ({newsletter['created_at']})"):
                button = st.button("메일 발송", key=f"button_{i}")
                
                st.markdown("---")
                st.write("키워드:")
                st.write(newsletter['crawled_keywords'])
                st.markdown("---")
                st.write("뉴스레터 내용:")
                st.write(newsletter['content'])
                st.markdown("---")
                st.write("RAG 결과:")
                st.write("점수: {:.2f}%".format(newsletter['r_score']*100))
                st.write("결과:")
                if newsletter['r_score'] <= 0.6:
                    st.warning("데이터 베이스와 연관성이 적은 뉴스레터입니다.")
                else:
                    st.success("데이터 베이스와 연관성이 높은 뉴스레터입니다.")


                if button:
                    st.error("미구현")
                #     delete_newsletter(newsletter['id'])
                #     st.success("뉴스레터가 삭제되었습니다.")

    else:
        st.info("뉴스레터가 없습니다.")

