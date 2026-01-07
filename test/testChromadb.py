try:
    from langchain_community.vectorstores import Chroma
    from langchain_community.embeddings import OpenAIEmbeddings, HuggingFaceEmbeddings
    from langchain_community.chat_models import ChatOpenAI
except ImportError:
    # 兼容旧版本
    from langchain.vectorstores import Chroma
    from langchain.embeddings import OpenAIEmbeddings, HuggingFaceEmbeddings
    from langchain.chat_models import ChatOpenAI

from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import time
import os
from datetime import datetime

class LangChainMemoryManager:
    """使用LangChain的记忆管理器"""

    def __init__(self, persist_directory: str = "./chroma_db/user_memory") -> None:
        api_key = os.getenv("LLM_API_KEY") or os.getenv("DASHSCOPE_API_KEY") 
        base_url = os.getenv("LLM_BASE_URL")
        model_name = os.getenv("DEFAULT_MODEL", "gpt-4")
        
        # 使用 HuggingFace 本地模型作为 Embeddings，避免调用不支持的 API
        # 使用轻量级的 all-MiniLM-L6-v2 模型
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        
        # 创建或加载 Chroma向量存储
        self.vectorstore = Chroma(
            collection_name="emotion_chat_memory",
            embedding_function=self.embeddings,
            persist_directory=persist_directory
        )

        # 初始化 LLM (使用配置的 DeepSeek)
        self.llm = ChatOpenAI(
            model=model_name, 
            temperature=0.7,
            openai_api_key=api_key,
            openai_api_base=base_url
        )

    def save_memory(self, user_id: str, text: str, metadata: dict = None):
        """保存记忆"""
        if metadata is None:
            metadata = {}

        metadata.update({
            "user_id": user_id,
            "timestamp": time.time(),
            "datetime": datetime.now().isoformat()
        })

        # 使用LangChain的方式添加文档
        self.vectorstore.add_texts(
            texts=[text],
            metadatas=[metadata]
        )

        # 持久化
        self.vectorstore.persist()

    def get_user_all_memories(self, user_id: str):
        """获取用户所有记忆"""
        results = self.vectorstore.get(where={"user_id": user_id})

        memories = []

        for i, doc in enumerate(results["documents"]):
            memory = {
                'id': results["ids"][i],
                'text': doc,
                'metadata': results["metadatas"][i]
            }
            memories.append(memory)

        return memories


    def retrieve_memory(self, user_id: str, query: str, top_k: int = 3):
        """检索记忆"""
        # 使用LangChain的相似度搜索
        docs = self.vectorstore.similarity_search(query, k=top_k * 3)

        # 过滤属于该用户的记忆
        user_docs = [
            doc for doc in docs 
            if doc.metadata.get("user_id") == user_id
        ][:top_k]

        return user_docs

    def chat(self, user_id: str, user_input: str):
        """带记忆的聊天"""
        # 检索记忆
        memories = self.retrieve_memory(user_id, user_input)

        # 构建记忆上下文
        memory_context = "\n".join([
            f"- [{m.metadata.get('datetime', '未知')}] {m.page_content}"
            for m in memories
        ])

        # 创建prompt模板
        template = """你是一位温暖的心理陪伴者"心语"。请结合用户的历史记忆进行回应。
        
        历史记忆：
        {memory_context}
        
        当前输入：{user_input}
        
        请以共情、支持的语气回应。"""
        
        prompt = PromptTemplate(
            template=template,
            input_variables=["memory_context", "user_input"]
        )

        # 创建链
        chain = LLMChain(llm=self.llm, prompt=prompt)

        # 生成回复
        response = chain.run(
            memory_context=memory_context if memory_context else "暂无历史记忆",
            user_input=user_input
        )

        # 保存记忆
        self.save_memory(user_id, user_input, {"role": "user"})
        self.save_memory(user_id, response, {"role": "assistant"})

        # 返回回复和检索到的记忆（用于调试）
        formatted_memories = [
            {
                "text": m.page_content,
                "metadata": m.metadata
            }
            for m in memories
        ]

        return response, formatted_memories
