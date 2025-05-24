# crawler/cnn_crawler.py
import os
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException
from ..news_translator.translator import translate_text  # 번역 모듈
import json

# ChromeDriver 경로 설정
CHROMEDRIVER_PATH = os.path.join(".", "chromedriver-win64", "chromedriver.exe")

def get_element_text_if_exists(driver, xpath):
    try:
        element = driver.find_element(By.XPATH, xpath)
        return element.text
    except NoSuchElementException:
        return None

def click_element(driver, xpath):
    try:
        element = driver.find_element(By.XPATH, xpath)
        driver.execute_script("arguments[0].click();", element)
        time.sleep(2)
    except Exception as e:
        print(f"클릭 실패: {e}")

def scroll_into_view(driver, xpath):
    try:
        element = driver.find_element(By.XPATH, xpath)
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
        time.sleep(2)
        return element
    except NoSuchElementException:
        print(f"스크롤 실패: {xpath}")
        return None

def save_text_to_file(base_folder, keyword, index, text):
    today = datetime.now().strftime("%Y%m%d")
    filename = f"{keyword}_{index}_{today}.txt"
    save_folder = os.path.join(".", base_folder)
    os.makedirs(save_folder, exist_ok=True)
    filepath = os.path.join(save_folder, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(text)

    print(f"파일 저장 완료: {filepath}")


def save_json_to_file(base_folder, keyword, index, data):
    today = datetime.now().strftime("%Y%m%d")
    filename = f"{keyword}_{index}_{today}.json"
    save_folder = os.path.join(".", base_folder)
    os.makedirs(save_folder, exist_ok=True)
    filepath = os.path.join(save_folder, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"JSON 파일 저장 완료: {filepath}")


def crawl_cnn_articles(keyword, lang="en"):
    print("CNN Health 기사 크롤링 시작...")
    print(f"검색어: {keyword}")
    print(f"언어 설정: {'영문만 저장' if lang == 'en' else '영문 + 한글 번역 저장'}")

    service = Service(executable_path=CHROMEDRIVER_PATH)
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # 필요 시 활성화
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--allow-insecure-localhost")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-features=IsolateOrigins,site-per-process")
    driver = webdriver.Chrome(service=service, options=options)

    try:
        driver.get("https://edition.cnn.com/health")
        print("CNN 메인 페이지 열기 완료")
        time.sleep(3)

        # 검색 버튼 클릭
        click_element(driver, "/html/body/header/div/div[3]/div/div/nav/div/div/div[1]/div[2]/button[1]")

        # 검색어 입력
        #keyword = "high blood pressure"
        input_box = driver.find_element(By.XPATH, "/html/body/header/div/div[3]/div/div/nav/div/div/div[2]/div/div[1]/form/input")
        input_box.send_keys(keyword)
        time.sleep(1)

        # 검색 제출 버튼 클릭
        click_element(driver, "/html/body/header/div/div[3]/div/div/nav/div/div/div[2]/div/div[1]/form/button")
        time.sleep(5)

        for index in range(1, 6):  # 기사 1~5
            print(f"\n{index}번째 기사 처리 중...")

            article_xpath = f"/html/body/div[1]/section[3]/section[1]/div/section/section/div/div[2]/div/div[2]/div/div[2]/div/div/div[{index}]/a[2]/div/div[1]"
            scroll_into_view(driver, article_xpath)
            click_element(driver, article_xpath)
            time.sleep(3)

             # 기사 URL
            article_url = driver.current_url

            # 기사 제목
            title_xpath = "/html/body/div[2]/section[3]/div[2]/div[1]/h1"
            title = get_element_text_if_exists(driver, title_xpath) or "제목 없음"

            # 본문 수집
            paragraphs = []
            for i in range(1, 50):
                content_xpath = f"/html/body/div[2]/section[4]/section[1]/section[1]/article/section/main/div[2]/div[1]/p[{i}]"
                paragraph = get_element_text_if_exists(driver, content_xpath)
                if paragraph:
                    paragraphs.append(paragraph)
                else:
                    break

            if paragraphs:
                print(f"본문 추출 완료: {len(paragraphs)}개 단락")
                full_text = "\n\n".join(paragraphs)
                filename_keyword = f"cnn_{keyword.replace(' ', '_')}"
                json_data = {
                    "title": title,
                    "url": article_url,
                    "content_en": full_text,
                }

                # 영어 원문 저장
                save_text_to_file(base_folder="saved_articles", keyword=filename_keyword, index=index, text=full_text)

                # 번역 후 한국어 저장
                if lang == "kr":
                    translated_text = translate_text(full_text)
                    print(f"번역된 텍스트: {translated_text[:100]}...")  # 번역된 결과 앞 100자 미리보기
                    save_text_to_file(base_folder="saved_articles_kr", keyword=filename_keyword, index=index, text=translated_text)
        
                save_json_to_file(base_folder="saved_articles_json", keyword=filename_keyword, index=index, data=json_data)

            else:
                print(f"본문이 없습니다. 기사 {index} 건너뜀.")

            driver.back()
            time.sleep(5)

    finally:
        driver.quit()
        print("브라우저 종료 완료.")
