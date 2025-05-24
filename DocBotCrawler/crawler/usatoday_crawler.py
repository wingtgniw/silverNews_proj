import os
import time
import traceback
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
from ..news_translator.translator import translate_text  # 번역 모듈
import json

BASE_URL = "https://www.usatoday.com"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
}


def save_text_to_file(base_folder, keyword, index, text):
    today = datetime.now().strftime("%Y%m%d")
    filename = f"{keyword}_{index}_{today}.txt"
    save_folder = os.path.join(".", base_folder)
    os.makedirs(save_folder, exist_ok=True)
    filepath = os.path.join(save_folder, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"저장 완료: {filepath}")



def save_json_to_file(base_folder, keyword, index, data):
    today = datetime.now().strftime("%Y%m%d")
    filename = f"{keyword}_{index}_{today}.json"
    save_folder = os.path.join(".", base_folder)
    os.makedirs(save_folder, exist_ok=True)
    filepath = os.path.join(save_folder, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"JSON 저장 완료: {filepath}")


def crawl_usatoday_articles(keyword, lang="en"):
    print(f"USA Today 기사 크롤링 시작: '{keyword}' / 언어: {lang}")

    encoded_keyword = quote_plus(keyword)
    search_url = f"{BASE_URL}/search/?q={encoded_keyword}"
    print(f"검색 URL: {search_url}")

    try:
        response = requests.get(search_url, headers=HEADERS)
        if response.status_code != 200:
            print(f"검색 페이지 요청 실패: {response.status_code}")
            return

        soup = BeautifulSoup(response.text, "html.parser")
        article_tags = soup.select("main a[href^='/story']")

        if not article_tags:
            print("검색 결과가 없습니다.")
            return

        for index, tag in enumerate(article_tags[:5], start=1):
            href = tag["href"]
            article_url = BASE_URL + href
            print(f"\n[{index}] 기사 방문: {article_url}")

            try:
                article_response = requests.get(article_url, headers=HEADERS)
                if article_response.status_code != 200:
                    print(f"기사 요청 실패: {article_response.status_code}")
                    continue

                article_soup = BeautifulSoup(article_response.text, "html.parser")
                article_tag = article_soup.find("article")

                if not article_tag:
                    print("article 태그를 찾을 수 없습니다.")
                    continue

                paragraphs = [p.get_text(strip=True) for p in article_tag.find_all("p")]
                if not paragraphs:
                    print("본문이 없습니다. 건너뜀.")
                    continue

                full_text = "\n\n".join(paragraphs)
                title_tag = article_soup.select_one("h1")
                title = title_tag.get_text(strip=True) if title_tag else "제목 없음"
                filename_keyword = f"usatoday_{keyword.replace(' ', '_')}"

                # 텍스트 파일 저장 (기존 함수 유지)
                save_text_to_file("saved_articles", filename_keyword, index, full_text)

                if lang == "kr":
                    translated = translate_text(full_text)
                    save_text_to_file("saved_articles_kr", filename_keyword, index, translated)
                else:
                    translated = None

                # JSON 저장
                json_data = {
                    "title": title,
                    "url": article_url,
                    "content_en": full_text
                }
                if translated:
                    json_data["content_kr"] = translated

                save_json_to_file("saved_articles_json", filename_keyword, index, json_data)

            except Exception as e:
                print(f"예외 발생: {e}")
                traceback.print_exc()

    except Exception as e:
        print(f"전체 크롤링 실패: {e}")
        traceback.print_exc()
