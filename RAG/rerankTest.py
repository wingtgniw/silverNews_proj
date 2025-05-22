from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.retrievers import ContextualCompressionRetriever
from langchain_cohere import CohereRerank
from langchain.chains import RetrievalQA

pdfLoad = PyPDFLoader('RAG/med_data_all.pdf')
documents = pdfLoad.load()

txt_split = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=20)
docs = txt_split.split_documents(documents)
print(len(docs))

embedding = OpenAIEmbeddings(model='text-embedding-ada-002')
vdb = FAISS.from_documents(docs, embedding)
base_retriever = vdb.as_retriever(search_kwargs={"k": 10})

reranker = CohereRerank(
    model="rerank-multilingual-v3.0",  
    top_n=5  # 최종 문서 5개만 선택 (원하는 수로 조정 가능)
)

retriever = ContextualCompressionRetriever(
    base_compressor=reranker,
    base_retriever=base_retriever,
)

gpt = ChatOpenAI(model='gpt-3.5-turbo', temperature=0)

qa = RetrievalQA.from_chain_type(
    llm=gpt,
    chain_type='stuff',
    retriever=retriever,
)

query = "고혈압 치료 방법"
result = qa.invoke({'query': query})
print(result)
print(result['result'])
