from crawler.cnn_crawler import crawl_cnn_articles
from crawler.usatoday_crawler import crawl_usatoday_articles
from crawler.wikipedia_crawler import crawl_wikipedia
from translator.translator import kor_to_eng
import re
from concurrent.futures import ThreadPoolExecutor

# CRAWLER_FUNCTIONS = [
#     crawl_cnn_articles,
#     crawl_usatoday_articles,
# ]

CRAWLER_FUNCTIONS = [
    crawl_cnn_articles,
    crawl_usatoday_articles,
    crawl_wikipedia
]


def is_korean(text):
    return bool(re.search(r"[가-힣]", text))

def main():
    print("CNN Health 뉴스 크롤러")
    print("입력 예시: kr 당뇨   /  en high blood pressure  /  high blood pressure (언어 생략 시 영문 기본값)")

    user_input = input("언어와 검색어를 한 줄로 입력하세요: ").strip()

    if not user_input:
        print("입력이 없습니다. 종료합니다.")
        return

    parts = user_input.split(maxsplit=1)

    if parts[0].lower() in ("en", "kr"):
        lang = parts[0].lower()
        keyword_input = parts[1] if len(parts) > 1 else ""
    else:
        lang = "en"
        keyword_input = user_input

    if not keyword_input:
        print("검색어가 없습니다. 종료합니다.")
        return

    if is_korean(keyword_input):
        print(f"입력된 한글을 영어로 번역 중: '{keyword_input}'")
        keyword = kor_to_eng(keyword_input)
        print(f"번역된 검색어: {keyword}")
    else:
        keyword = keyword_input

    print(f"\n크롤링 시작: 검색어='{keyword}' / 언어='{lang}'")

    with ThreadPoolExecutor(max_workers=len(CRAWLER_FUNCTIONS)) as executor:
        futures = [executor.submit(func, keyword, lang) for func in CRAWLER_FUNCTIONS]
        for future in futures:
            try:
                future.result()  # 예외가 있으면 여기서 출력됨
            except Exception as e:
                print(f"크롤러 실행 중 오류 발생: {e}")


if __name__ == "__main__":
    main()
