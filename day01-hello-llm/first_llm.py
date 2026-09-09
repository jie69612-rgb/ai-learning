"""Day 1：调通你的第一个大模型 API

运行前需要：
1. 到 platform.deepseek.com 注册并创建 API Key（充值几块钱或使用赠送额度）
2. 把 key 填进 .env 文件（复制上级目录的 .env.example 改名为 .env）
3. 运行：python first_llm.py
"""
import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv("DEEPSEEK_API_KEY")
if not api_key:
    print("没找到 API Key。")
    print("方法一：把 key 填进 .env 文件（推荐）")
    print("方法二：PowerShell 里执行  $env:DEEPSEEK_API_KEY='sk-你的key'")
    raise SystemExit(1)

client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "system", "content": "你是一个耐心的 AI 老师，回答要简短清楚。"},
        {"role": "user", "content": "用一句话解释什么是 RAG"},
    ],
    temperature=0.7,
)

print(response.choices[0].message.content)
print("\n--- 元信息 ---")
print("模型:", response.model)
print("消耗 token:", response.usage.total_tokens)
