import streamlit as st
from DB import *
from DocBotCrawler.news_translator.translator import kor_to_eng
from generator import NewsletterGenerator
from RAG import RAG_reviewer
from DocBotCrawler.run_crawler import NewsCrawlerRunner
from glob import glob
import json
import re
import time
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os


def is_korean(text):
    return bool(re.search(r"[가-힣]", text))

def crawling_articles_page():
    st.title("기사 크롤링")

    # 크롤러 초기화
    if st.session_state.get("crawler") is None:
        st.session_state["crawler"] = NewsCrawlerRunner()

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

def show_articles():

    st.title("기사 보기")

    if st.session_state.get("newsletter_generator") is None:
        # 뉴스레터 생성기 초기화
        st.session_state["newsletter_generator"] = NewsletterGenerator()

    if st.session_state.get("RAG_reviewer") is None:
        # RAG 리뷰어 초기화
        st.session_state["RAG_reviewer"] = RAG_reviewer()

    files = glob(f"./saved_articles_json/*.json")

    generator = st.session_state['newsletter_generator']
    user_id = st.session_state["sender_email"] if st.session_state.get("sender_email") is not None else "wingtgniw@gmail.com"
        
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

    if st.session_state.get("sender_email") is None:
        # 이메일 정보 초기화
        st.session_state["sender_email"] = "wingtgniw@gmail.com"
        st.session_state["email_password"] = os.getenv("EMAIL_PASSWORD")

    # URL 파라미터에서 newsletter_id 확인
    target_newsletter_id = st.query_params.get("id")

    # 뉴스레터 목록 조회
    newsletters = get_all_newsletters(st.session_state["sender_email"])
    if newsletters:
        for i, newsletter in enumerate(newsletters):
            # 특정 뉴스레터로 이동
            if target_newsletter_id and str(newsletter['id']) == target_newsletter_id:
                st.session_state['expand_newsletter_' + str(i)] = True
            
            with st.expander(f"{newsletter['title']} ({newsletter['created_at']})", 
                           expanded=st.session_state.get('expand_newsletter_' + str(i), False)):
                receiver_email = st.text_input("받으실 분 이메일", key=f"receiver_email_{i}")
                button = st.button("메일 발송", key=f"button_{i}")
                
                if button:
                    if receiver_email == "":
                        st.error("수신자를 입력해주세요.")
                        
                        newsletter_expanded_page(newsletter)
                        continue
                    elif "@" not in receiver_email:
                        st.error("올바른 이메일을 입력해주세요.")

                        newsletter_expanded_page(newsletter)
                        continue

                    with st.spinner("전송중..."):
                        print("send_email")
                        print(f"send_email ---- title: {newsletter['title']}")
                        print(f"send_email ---- receiver_email: {receiver_email}")

                        sender_email = st.session_state["sender_email"]
                        password = st.session_state["email_password"]

                        print(f"send_email ---- sender_email: {sender_email}")
                        print(f"send_email ---- password: {password}")
                        print(f"send_email ---- receiver_email: {receiver_email}")

                        msg = MIMEMultipart()
                        msg["Subject"] = "[뉴스레터 발송] Silver News에서 새로운 뉴스레터가 작성되었습니다."
                        msg["From"] = sender_email
                        msg["To"] = receiver_email
                        
                        # 메일 내용 작성
                        content = newsletter['title']\
                        + "\n\n" + newsletter['content_summary']\
                        + "\n\n자세한 기사는 아래의 링크를 클릭해주세요:\n"
                        content_part = MIMEText(content, "plain")
                        msg.attach(content_part)

                        # 뉴스레터 링크 수정
                        base_url = os.getenv("BASE_URL", "http://192.168.0.166:8501")
                        newsletter_link = f"{base_url}/?menu=뉴스레터&id={newsletter['id']}"

                        # 메일 내용에 링크 삽입
                        link = f'<a href="{newsletter_link}">뉴스레터 보기</a>'
                        link_part = MIMEText(link, "html") 
                        msg.attach(link_part)

                        try:
                            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                                server.login(sender_email, password)
                                server.sendmail(sender_email, receiver_email, msg.as_string())
                            st.success("메일 전송 완료")
                        except smtplib.SMTPRecipientsRefused as e:
                            st.error("이메일 전송 실패: 수신자 주소가 올바르지 않습니다.")
                        except Exception as e:
                            st.error(f"이메일 전송 실패: {str(e)}")
                    
                newsletter_expanded_page(newsletter)
                
    else:
        st.info("뉴스레터가 없습니다.")

def newsletter_expanded_page(newsletter):
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
