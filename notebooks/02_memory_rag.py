from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
import os

load_dotenv()

llm = ChatOpenAI(
    model="deepseek-chat",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
)

# ---- Part 1: 对话记忆 ----
# LangChain 里最简单的记忆就是自己维护 message history
# 每次把历史消息一起传给模型

history = [
    SystemMessage(content="你是一个helpful助手，回答要简洁")
]

def chat(user_input):
    history.append(HumanMessage(content=user_input))
    response = llm.invoke(history)
    history.append(AIMessage(content=response.content))
    return response.content

print("=== 对话记忆测试 ===")
print(chat("我叫Kyle，我是一个NLP工程师"))
print(chat("我刚才说我叫什么？"))  # 测试它是否记得

# ---- Part 2: 读本地文件做问答 ----
# 先在项目根目录建一个 test.txt 测试用

test_file = "test.txt"
if not os.path.exists(test_file):
    with open(test_file, "w", encoding="utf-8") as f:
        f.write("""
LangChain是一个用于构建LLM应用的框架。
它支持对话记忆、RAG检索、Agent编排等功能。
DeepSeek是深度求索公司开发的大语言模型，API兼容OpenAI格式。
Kyle是一个有3年NLP经验的工程师，擅长信息抽取和知识图谱。
        """)

print("\n=== 本地文件问答测试 ===")

# 加载文件
loader = TextLoader(test_file, encoding="utf-8")
docs = loader.load()

# 切分
splitter = RecursiveCharacterTextSplitter(chunk_size=100, chunk_overlap=20)
chunks = splitter.split_documents(docs)

# 向量化存索引，这里用 DeepSeek 做 embedding 需要额外配置
# 先用最简单的方式：直接把全文塞进 context 问
context = "\n".join([doc.page_content for doc in docs])

response = llm.invoke([
    SystemMessage(content=f"根据以下内容回答问题：\n{context}"),
    HumanMessage(content="Kyle是做什么的？")
])
print(response.content)
