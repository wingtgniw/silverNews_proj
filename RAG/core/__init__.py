from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.retrievers import ContextualCompressionRetriever
from langchain_cohere import CohereRerank
from langchain.chains import RetrievalQA

class RAG_reviewer:
    def __init__(self):
        self.set_retriever_and_QA()

    def set_retriever_and_QA(self):

        print("RAG_reviewer set_retriever_and_QA")
        print("Read pdf")
        pdfLoad = PyPDFLoader('RAG/med_data_all.pdf')
        documents = pdfLoad.load()

        print("Split documents")
        txt_split = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=20)
        docs = txt_split.split_documents(documents)

        print("Embedding")
        embedding = OpenAIEmbeddings(model='text-embedding-ada-002')
        vdb = FAISS.from_documents(docs, embedding)
        base_retriever = vdb.as_retriever(search_kwargs={"k": 10})

        print("Reranker")
        reranker = CohereRerank(
            model="rerank-multilingual-v3.0",  
            top_n=5  # 최종 문서 5개만 선택 (원하는 수로 조정 가능)
        )

        print("ContextualCompressionRetriever")
        self.retriever = ContextualCompressionRetriever(
            base_compressor=reranker,
            base_retriever=base_retriever,
        )

        print("GPT")
        gpt = ChatOpenAI(model='gpt-3.5-turbo', temperature=0)

        print("RetrievalQA")
        self.QA = RetrievalQA.from_chain_type(
            llm=gpt,
            chain_type='stuff',
            retriever=self.retriever,
        )
    
    def get_review(self, newsletter):
        print(f"RAG get_review")
        # print(f"RAG ---- newsletter: {newsletter}")

        print(f"RAG ---- get_reranked_results")
        reranked_results = self.get_reranked_results(newsletter)

        average_score = 0
        for doc in reranked_results:
            average_score += doc.metadata['relevance_score']
        
        average_score /= len(reranked_results)
        print(f"RAG ---- average_score: {average_score}")

        prompt = """
        다음 내용들을 확인해서 뉴스레터 내용에 대한 사실 여부를 확인해줘.
        뉴스레터 내용: """ + newsletter + "\n뉴스레터 리뷰:"
        result = self.QA.invoke(prompt)

        # print(f"RAG ---- result: {result}")

        return average_score, result['result']
    
    def get_reranked_results(self, query):

        # 리랭킹된 결과
        reranked_results = self.retriever.get_relevant_documents(query)

        return reranked_results
    
    