당뇨뇨# DocBotCrawler

**DocBotCrawler**는 시니어 및 건강 관심자를 위한 뉴스 정보 크롤링 도구입니다.  
CNN, USA Today, Wikipedia에서 건강 관련 뉴스 및 정보를 자동으로 수집하고,  
필요 시 한국어 번역까지 지원합니다.  

---

## 주요 기능

- CNN Health 뉴스 기사 자동 크롤링 (Selenium + BeautifulSoup)
- USA Today 뉴스 기사 빠른 크롤링 (Selenium 제거 → BeautifulSoup 적용)
- Wikipedia 정보 검색 및 요약 (5단락 기준)
- 입력값 자동 처리 (언어 선택 + 번역)
- 병렬 크롤링 처리로 속도 최적화 (약 2초 내외)
- 결과 텍스트 파일 저장 (영문/번역본 분리)

---

## 디렉토리 구조

```
DocBotCrawler/
├── main.py                  # 실행 진입점
├── crawler/
│   ├── cnn\_crawler.py       # CNN 뉴스 크롤러
│   ├── usatoday\_crawler.py  # USA Today 크롤러
│   └── wikipedia\_crawler.py # 위키피디아 정보 크롤러
├── translator/
│   └── translator.py        # 텍스트 번역 모듈
├── saved\_articles/          # 원문 저장 위치
├── saved\_articles\_kr/       # 번역본 저장 위치
├── chromedriver-win64/      # 크롬 드라이버 위치
└── README.md
````

---

## 사용 기술

- Python 3.12
- BeautifulSoup4
- Requests
- Selenium (CNN 전용)
- deep-translator
- concurrent.futures (ThreadPoolExecutor)

---

## 실행 방법

### 1. 콘솔 기반 실행

```bash
python main.py
````

입력 예시:

```text
kr 당뇨
```

자동 번역 및 병렬 크롤링 실행 예:

```
입력된 한글을 영어로 번역 중: '당뇨'
번역된 검색어: diabetes

크롤링 시작: 검색어='diabetes' / 언어='kr'

- CNN 크롤링...
- USA Today 크롤링...
- Wikipedia 크롤링...

저장 완료: saved_articles/cnn_diabetes_1_20250517.txt
저장 완료: saved_articles_kr/cnn_diabetes_1_20250517.txt
```

---

### 2. FastAPI 서버 실행 (선택사항)

> API 연동 기능이 구현되어 있다면 해당 코드 기준

```bash
uvicorn api.server:app --reload
```

접속 URL:

* Swagger 문서: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* 크롤링 요청:

  ```bash
  curl "http://127.0.0.1:8000/crawl?keyword=고혈압"
  ```

---

## 결과 저장 위치

| 폴더명                  | 설명                 |
| -------------------- | ------------------ |
| `saved_articles/`    | 크롤링한 영어 원문 저장      |
| `saved_articles_kr/` | 번역된 한국어 기사 저장 (선택) |

파일명 형식:

```
cnn_<keyword>_1_<날짜>.txt
usatoday_<keyword>_3_<날짜>.txt
wikipedia_<keyword>_<날짜>.txt
```

---

## 참고 사항

* `chromedriver.exe`는 `chromedriver-win64/` 폴더에 있어야 합니다.
* CNN 뉴스는 Selenium 기반으로 JavaScript 렌더링 후 본문을 가져옵니다.
* Wikipedia/USA Today는 BeautifulSoup 기반으로 빠르게 처리됩니다.
* 사이트 구조 변경 시 크롤러 로직(XPath, CSS Selector) 업데이트 필요합니다.

---

## 향후 계획

* API 서버와의 연동 기능 정식 배포
* 키워드 기반 예약 크롤링 기능
* 크롤링 데이터 DB 저장 기능 추가 (PostgreSQL)

---

## 🗓 성능 개선 요약 (2025.05.18)

| 항목        | 개선 전        | 개선 후                      |
| --------- | ----------- | ------------------------- |
| USA Today | Selenium 기반 | BeautifulSoup로 전환 (2초 이내) |
| Wikipedia | 신규 추가 없음    | 신규 추가 (1초 이내 추출)          |
| CNN       | JS 렌더링 필수   | Selenium 유지               |
| 전체 크롤링 소요 | 10\~15초     | 2\~3초 (병렬 실행 기준)          |

---