import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
import os
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

        # 본문 <p> 태그 추출 (요약 중심)
        paragraphs = soup.select("div.mw-parser-output > p")
        filtered_paragraphs = [p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 50]

        if not filtered_paragraphs:
            print("유효한 본문이 없습니다.")
            return

        summary = "\n\n".join(filtered_paragraphs[:5])  # 앞부분 5단락만 저장
        print(f"본문 추출 완료 (문단 수: {len(filtered_paragraphs)})")

        save_text_to_file("saved_articles", keyword.replace(" ", "_"), summary)

    except Exception as e:
        print(f"예외 발생: {e}")

