from langchain_openai import ChatOpenAI
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import ZhipuAIEmbeddings
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv
import os

load_dotenv()

# ---- 模型初始化 ----
llm = ChatOpenAI(
    model="deepseek-chat",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
)

embeddings = ZhipuAIEmbeddings(
    model="embedding-3",
    api_key=os.getenv("ZHIPU_API_KEY"),
)

# ---- 加载和切分 ----
print("加载文本...")
loader = TextLoader("data/三国演义.txt", encoding="utf-8")
docs = loader.load()

print("切分文本...")
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
)
chunks = splitter.split_documents(docs)
print(f"共切分为 {len(chunks)} 个 chunk")

# ---- 向量化并建索引 ----
# 改成分批处理
print("向量化中，请稍候...")
batch_size = 64
vectorstore = None

for i in range(0, len(chunks), batch_size):
    batch = chunks[i:i + batch_size]
    if vectorstore is None:
        vectorstore = FAISS.from_documents(batch, embeddings)
    else:
        vectorstore.add_documents(batch)
    print(f"进度：{min(i + batch_size, len(chunks))}/{len(chunks)}")

vectorstore.save_local("data/sanguo_index")
print("索引已保存")


# ---- 检索问答 ----
def ask(question):
    # 检索最相关的 8 个 chunk
    relevant_docs = vectorstore.similarity_search(question, k=8)
    print("=== 检索到的原文 ===")
    for i, doc in enumerate(relevant_docs):
        print(f"--- chunk {i+1} ---")
        print(doc.page_content[:200])  # 先只看前200字
    print("===================")
    context = "\n\n".join([doc.page_content for doc in relevant_docs])
    
    response = llm.invoke([
        SystemMessage(content=f"你是一个三国演义专家，根据以下原文内容回答问题，引用原文时请注明：\n\n{context}"),
        HumanMessage(content=question)
    ])
    return response.content

print("\n=== 三国演义问答系统 ===")
print(ask("赤壁之战的经过是什么？"))
print("\n---")
print(ask("诸葛亮第一次出场是什么情形？"))