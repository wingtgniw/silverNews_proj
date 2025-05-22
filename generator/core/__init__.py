from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph
from langchain_core.runnables import RunnableLambda

### gpt-3.5-turbo 모델의 최대 컨텍스트 길이는 16385 토큰입니다.

class NewsletterGenerator:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
        
        ## only crawling 뉴스레터 생성 그래프
        self.newsletter_graph = self.get_newsletter_graph()

    def generate_newsletter_from_articles(self, article):
        return self.newsletter_graph.invoke({"article":article})
    
    def get_newsletter_graph(self):

        llm = self.llm

        role = """너는 이제부터 30년동안 시니어 건강 분야의 뉴스를 작성했던 기자야."""

        # lang graph 구축
        ## 상태 정의
        class MyState(dict):
            article: str
            keywords: str
            summary: str
            newsletter: str
            newsletter_summary: str
            newsletter_title: str

        ## articles to each keywords
        ### input : articles
        ### output : keywords
        def generate_keywords(state):
            prompt = role + """다음 내용들은 키워드를 검색해서 모아찾은 기사야. 잘 읽어보고 키워드들을 정리해줘.
            기사 내용: """ + state["article"] + "\n기사 키워드:"
            result = llm.invoke(prompt)
            return {"keywords": result.content}
        
        ## articles to summary
        ### input : articles, keywords
        ### output : summary
        def generate_summary(state):
            prompt = role + """다음 내용들을 확인해서 기사를 요약해줘.
            기사 내용: """ + state["article"] + "\n기사 키워드: " + state["keywords"] + "\n기사 요약:"
            result = llm.invoke(prompt)
            return {"summary": result.content}
        
        ## articles to newsletter
        ### input : articles, keywords, summary
        ### output : newsletter
        def generate_newsletter(state):
            prompt = role + """다음 내용들을 확인해서 뉴스레터를 작성해줘.
            기사 내용: """ + state["article"] + "\n기사 키워드: " + state["keywords"] + "\n기사 요약: " + state["summary"] + "\n뉴스레터 내용:"
            result = llm.invoke(prompt)
            return {"newsletter": result.content}

        ## articles to newsletter title
        ### input : articles, keywords, summary, newsletter, newsletter_summary
        ### output : newsletter_title
        def generate_newsletter_title(state):
            prompt = role + """다음 내용들을 확인해서 뉴스레터 제목을 생성해줘.
            기사 내용: """ + state["article"] + "\n기사 키워드: " + state["keywords"] + "\n기사 요약: " + state["summary"] + "\n뉴스레터 내용: " + state["newsletter"] + "\n뉴스레터 제목:"
            result = llm.invoke(prompt)
            return {"newsletter_title": result.content}

        ## 그래프 만들기
        graph = StateGraph(MyState)
        graph.add_node("키워드 생성", RunnableLambda(generate_keywords))
        graph.add_node("기사 요약", RunnableLambda(generate_summary))
        graph.add_node("뉴스레터 생성", RunnableLambda(generate_newsletter))
        graph.add_node("뉴스레터 제목 생성", RunnableLambda(generate_newsletter_title))

        graph.set_entry_point("키워드 생성")
        graph.add_edge("키워드 생성", "기사 요약")
        graph.add_edge("기사 요약", "뉴스레터 생성")
        graph.add_edge("뉴스레터 생성", "뉴스레터 제목 생성")

        graph.set_finish_point("뉴스레터 제목 생성")

        ## 그래프 반환
        return graph.compile()
    
class ArticleEditor:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
        
        ## only crawling 뉴스레터 생성 그래프
        self.article_editor_graph = self.get_article_editor_graph()

    def generate_newsletter_from_articles(self, article):
        return self.article_editor_graph.invoke({"article":article})
    
    def get_article_editor_graph(self):

        llm = self.llm

        role = """너는 이제부터 30년동안 시니어 건강 분야의 뉴스를 작성했던 기자야. 또한 영어를 원어민 처럼 구사할 수 있는 기자야."""

        # lang graph 구축
        ## 상태 정의
        class MyState(dict):
            article: str
            translation: str
            translation_summary: str
            translation_title: str

        ## articles to each keywords
        ### input : articles
        ### output : keywords
        def generate_translation(state):
            prompt = role + """다음 내용들을 확인해서 기사를 번역해줘.
            기사 내용: """ + state["article"] + "\n기사 번역:"
            result = llm.invoke(prompt)
            return {"translation": result.content}
        
        ## articles to summary
        ### input : articles, keywords
        ### output : summary
        def generate_translation_summary(state):
            prompt = role + """다음 내용들을 확인해서 기사를 요약해줘.
            기사 번역: """ + state["translation"] + "\n번역 요약:"
            result = llm.invoke(prompt)
            return {"translation_summary": result.content}
        
        ## articles to newsletter
        ### input : articles, keywords, summary
        ### output : newsletter
        def generate_translation_title(state):
            prompt = role + """다음 내용들을 확인해서 한글로 기사의 제목을 작성해줘.
            기사 번역: """ + state["translation"] + "\n번역 요약: " + state["translation_summary"] + "\n번역 제목:"
            result = llm.invoke(prompt)
            return {"translation_title": result.content}

        ## 그래프 만들기
        graph = StateGraph(MyState)
        graph.add_node("기사 번역", RunnableLambda(generate_translation))
        graph.add_node("번역 요약", RunnableLambda(generate_translation_summary))
        graph.add_node("번역 제목", RunnableLambda(generate_translation_title))

        graph.set_entry_point("기사 번역")
        graph.add_edge("기사 번역", "번역 요약")
        graph.add_edge("번역 요약", "번역 제목")

        graph.set_finish_point("번역 제목")

        ## 그래프 반환
        return graph.compile()