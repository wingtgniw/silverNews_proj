import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
import os
import json
from datetime import datetime

def save_text_to_file(base_folder, keyword, text):
    today = datetime.now().strftime("%Y%m%d")
    filename = f"wikipedia_{keyword}_{today}.txt"
    save_folder = os.path.join(".", base_folder)
    os.makedirs(save_folder, exist_ok=True)
    path = os.path.join(save_folder, filename)

    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"저장 완료: {path}")

def save_json_to_file(base_folder, keyword, data):
    today = datetime.now().strftime("%Y%m%d")
    filename = f"wikipedia_{keyword}_{today}.json"
    save_folder = os.path.join(".", base_folder)
    os.makedirs(save_folder, exist_ok=True)
    path = os.path.join(save_folder, filename)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"JSON 저장 완료: {path}")

def crawl_wikipedia(keyword, lang='en'):
    print(f"위키피디아 크롤링 시작: '{keyword}' (언어: {lang})")

    base_url = f"https://{lang}.wikipedia.org/wiki/"
    encoded_keyword = quote(keyword)
    url = base_url + encoded_keyword

    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        if response.status_code != 200:
            print(f"페이지 요청 실패: {response.status_code}")
            return

        soup = BeautifulSoup(response.text, "html.parser")

        # 제목 추출
        title_tag = soup.select_one("h1 span")
        title = title_tag.get_text(strip=True) if title_tag else "제목 없음"
        print(f"제목: {title}")

        # 본문 추출: main > div[3] > div[3] > div[1] > p
        content_div = soup.select_one("main > div:nth-of-type(3) > div:nth-of-type(3) > div:nth-of-type(1)")
        if not content_div:
            print("본문 영역을 찾을 수 없습니다.")
            return

        paragraphs = content_div.find_all("p")
        filtered_paragraphs = [p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 50]

        if not filtered_paragraphs:
            print("유효한 본문이 없습니다.")
            return

        summary = "\n\n".join(filtered_paragraphs[:5])  # 앞부분 5단락만 저장
        print(f"본문 추출 완료 (문단 수: {len(filtered_paragraphs)})")

        # 저장
        save_text_to_file("saved_articles", keyword.replace(" ", "_"), summary)

        json_data = {
            "title": title,
            "url": url,
            "content": summary
        }
        save_json_to_file("saved_articles_json", keyword.replace(" ", "_"), json_data)

    except Exception as e:
        print(f"예외 발생: {e}")
