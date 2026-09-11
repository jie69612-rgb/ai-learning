"""Day 2：多轮对话助手

核心知识点：大模型是"无状态"的——它不记得上一轮说过什么。
所以每轮都要把完整历史一起发过去，它的"记忆"其实是
我们替它保存的 messages 列表。
"""
from dotenv import load_dotenv
from openai import OpenAI
import os

load_dotenv()
# 读取Deepseek密钥
api_key = os.getenv("DEEPSEEK_API_KEY")

client = OpenAI(
    base_url="https://api.deepseek.com",
    api_key=api_key
)

# 对话历史：system 是给模型的人设，之后每轮往里面追加消息
messages = [
    {"role": "system", "content": "你是一个简洁、耐心的助手，回答尽量短。"}
]

print("多轮对话助手已启动（输入 quit 退出）")

while True:
    user_input = input("你: ").strip()
    if user_input.lower() == "quit":
        print("AI: 再见！")
        break

    # 第1步：把用户的话放进历史
    messages.append({"role": "user", "content": user_input})

    # 第2步：把完整历史发给模型
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
    )

    reply = response.choices[0].message.content
    print("AI:", reply)

    # 第3步：把模型的回答也放进历史，下一轮它才记得
    messages.append({"role": "assistant", "content": reply})