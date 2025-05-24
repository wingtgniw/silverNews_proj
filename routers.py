import streamlit as st
from DB import *
from DocBotCrawler.run_crawler import NewsCrawlerRunner
#from crawler_copy import crawl_cnn_articles
#from translator_copy import kor_to_eng
from DocBotCrawler.news_translator.translator import kor_to_eng
from glob import glob
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
            ## cnn 사이트로부터 기사 크롤링, 번역 및 저장
            #crawl_cnn_articles(keyword)
            crawler = NewsCrawlerRunner()
            crawler.run(keyword, lang="en")
            st.write(f'crawl time: {time.time() - start_time}')

        st.success("기사들이 크롤링 되었습니다.")

def show_articles():
    files = glob(f"./saved_articles/*.txt")
    if st.session_state.get("articles") is None :
        st.session_state["articles"] = []

    generator = st.session_state['newsletter_generator']
    article_editor = st.session_state['article_editor']
    user_id = st.session_state["user_id"]
        
    if files:
        # chat gpt turbo 3.5 모델 사용
        if len(st.session_state["articles"]) == 0:
            for i, file in enumerate(files):
                # 기사 내용 추출
                with open(file, "r", encoding="utf-8") as f:
                    article = f.read()
            
                # 기사 편집
                result = article_editor.generate_newsletter_from_articles(article)
                # with st.expander(f"{article['title']} ({article['created_at']})"):
                with st.expander(result['translation_title']):
                    button = st.button("뉴스레터 작성", key=f"button_{i}")
                    
                    st.write("번역 요약:")
                    st.write(result['translation_summary'])
                    st.write("기사 번역:")
                    st.write(result['translation'])

                    if button:
                        with st.spinner("뉴스레터 작성 중..."):
                            rst = generator.generate_newsletter_from_articles(article)
                            print(rst)
                        insert_newsletter_2(user_id, rst)
                        st.success("뉴스레터가 작성되었습니다.")

                st.session_state["articles"].append([article, result['translation_title'], result['translation_summary']])
        else:
            for i, (article, title, summary) in enumerate(st.session_state["articles"]):
                with st.expander(title):
                    button = st.button("뉴스레터 작성", key=f"button_{i}")

                    st.write(f"요약:\n{summary}")
                    st.write(f"기사:\n{article}")

                    if button:
                        with st.spinner("뉴스레터 작성 중..."):
                            rst = generator.generate_newsletter_from_articles(article)
                        insert_newsletter_2(user_id, rst)
                        st.success("뉴스레터가 작성되었습니다.")
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
                
                st.write(f"키워드:\n{newsletter['crawled_keywords']}")
                st.write(f"뉴스레터 내용:\n{newsletter['content']}")

                if button:
                    st.error("미구현")
                #     delete_newsletter(newsletter['id'])
                #     st.success("뉴스레터가 삭제되었습니다.")

    else:
        st.info("뉴스레터가 없습니다.")

