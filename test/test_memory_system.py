# test_memory_system.py

import os
from dotenv import load_dotenv
from pathlib import Path

# 加载环境变量 (指向根目录的 config.env)
env_path = Path(__file__).parent.parent / 'config.env'
load_dotenv(env_path)

from testChromadb import LangChainMemoryManager

def test_memory_system():
    """测试记忆系统"""
    print("=" * 70)
    print(" 心语机器人 - Chroma 记忆系统测试")
    print("=" * 70)

    # 初始化记忆管理器
    memory_manager = LangChainMemoryManager(persist_directory="./chroma_db/test_memory")

    user_id = "test_user_001"

    # 第一轮对话
    print("\n【第1轮对话】")
    print("-" * 70)
    user_input_1 = "最近工作压力好大，每天都加班到很晚。"
    print(f"用户: {user_input_1}")

    response_1, memories_1 = memory_manager.chat(user_id, user_input_1)
    print(f"检索到的记忆: {memories_1}")
    print(f"\n心语: {response_1}")

    # 第二轮对话
    print("\n\n【第2轮对话】")
    print("-" * 70)
    user_input_2 = "我觉得自己快撑不住了，感觉身体也吃不消了。"
    print(f"用户: {user_input_2}")

    response_2, memories_2 = memory_manager.chat(user_id, user_input_2)
    print(f"检索到的记忆: {memories_2}")
    print(f"\n心语: {response_2}")

    # 第三轮对话（测试记忆检索）
    print("\n\n【第3轮对话 - 测试记忆检索】")
    print("-" * 70)
    user_input_3 = "项目快上线了，这周又要天天熬夜了。"
    print(f"用户: {user_input_3}")

    response_3, memories_3 = memory_manager.chat(user_id, user_input_3)
    print(f"检索到的记忆: {memories_3}")
    print(f"\n心语: {response_3}")

    # 显示检索到的记忆
    print("\n\n【检索到的历史记忆】")
    print("-" * 70)
    for i, mem in enumerate(memories_3, 1):
        print(f"{i}. {mem['text']}")
        print(f"   时间: {mem['metadata']['datetime']}")
        print(f"   情绪: {mem['metadata'].get('emotion', '未知')}")
        print()

    print("=" * 70)
    print("测试完成！")
    print("=" * 70)

if __name__ == "__main__":
    # test_memory_system()

    # 获取用户的所有记忆
        # 初始化记忆管理器
    memory_manager = LangChainMemoryManager(persist_directory="./chroma_db/test_memory")

    user_id = "test_user_001"

    memories = memory_manager.get_user_all_memories(user_id)
    print(f"用户{user_id}的所有记忆: {memories}")
    