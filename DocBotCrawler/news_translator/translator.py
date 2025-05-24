from deep_translator import GoogleTranslator
import time

def translate_text(text: str) -> str:
    """
    영어 텍스트를 문단 단위로 쪼개서 한국어로 번역
    """
    try:
        if not text.strip():
            print("번역할 텍스트가 없습니다.")
            return ""

        paragraphs = text.split("\n\n")  # 문단 단위로 나누기
        translated_paragraphs = []

        for para in paragraphs:
            if para.strip():
                translated = GoogleTranslator(source='en', target='ko').translate(para)
                translated_paragraphs.append(translated)
                time.sleep(1)  # 서버 부담 줄이기 위해 약간 딜레이

        combined_translation = "\n\n".join(translated_paragraphs)
        print(f"번역 완료: {len(translated_paragraphs)}개 문단")
        return combined_translation

    except Exception as e:
        print(f"번역 실패: {e}")
        return ""


def kor_to_eng(text: str) -> str:
    """한글 텍스트를 영어로 번역하는 함수 (검색어 번역 전용)"""
    try:
        return GoogleTranslator(source='ko', target='en').translate(text.strip())
    except Exception as e:
        print(f"한글 → 영어 번역 실패: {e}")
        return text