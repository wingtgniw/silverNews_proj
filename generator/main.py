from core import NewsletterGenerator

if __name__ == "__main__":
    generator = NewsletterGenerator()
    while True:
        subjects = input("뉴스레터 주제: ")
        if subjects.lower() == "q":
            break
        else:
            result = generator.generate_newsletter(subjects)
            print(result)
