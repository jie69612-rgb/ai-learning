from dotenv import load_dotenv
from openai import OpenAI
import os

load_dotenv()

# 从.env读取DEEPSEEK_API_KEY
api_key = os.getenv("DEEPSEEK_API_KEY")

client = OpenAI(
    base_url="https://api.deepseek.com",
    api_key=api_key
)

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "user", "content": "用JSON格式列出学习RAG的三个步骤，每个步骤包含 name 和 duration"}
    ],
    response_format={"type":"json_object"},
)
print(response.choices[0].message.content)
