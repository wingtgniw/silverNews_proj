# run_crawler.py
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import re
from concurrent.futures import ThreadPoolExecutor
from .crawler.cnn_crawler import crawl_cnn_articles
from .crawler.usatoday_crawler import crawl_usatoday_articles
from .crawler.wikipedia_crawler import crawl_wikipedia
from .news_translator.translator import kor_to_eng  # 상위 모듈


class NewsCrawlerRunner:
    def __init__(self):
        self.crawlers = [
            crawl_cnn_articles,
            crawl_usatoday_articles,
            crawl_wikipedia
        ]

    def is_korean(self, text):
        return bool(re.search(r"[가-힣]", text))

    def run(self, keyword: str, lang: str = "en"):
        """ 뉴스 크롤러 실행 """
        if self.is_korean(keyword):
            print(f"입력된 한글을 영어로 번역 중: '{keyword}'")
            keyword = kor_to_eng(keyword)
            print(f"번역된 검색어: {keyword}")

        print(f"\n크롤링 시작: 검색어='{keyword}' / 언어='{lang}'")

        with ThreadPoolExecutor(max_workers=len(self.crawlers)) as executor:
            futures = [executor.submit(func, keyword, lang) for func in self.crawlers]
            for future in futures:
                try:
                    future.result()
                except Exception as e:
                    print(f"크롤러 실행 중 오류 발생: {e}")
