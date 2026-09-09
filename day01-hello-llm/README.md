# Day 1：调通第一个大模型 API

## 今天的任务清单

- [ ] 注册 DeepSeek（platform.deepseek.com），创建 API Key
- [ ] 复制上级目录 `.env.example` 为 `.env`，粘贴 key
- [ ] 运行 `python first_llm.py`，看到回答就算成功
- [ ] 小改动练习 1：把 `temperature` 改成 0 和 1.5，观察回答差异
- [ ] 小改动练习 2：把问题改成"用 JSON 格式输出三个学习 RAG 的步骤"，学会结构化输出
- [ ] 写学习日志，`git commit` + `push` 到 GitHub

## 今天要弄懂的概念

- API Key 是什么、为什么不能写进代码提交到 GitHub
- temperature 参数对输出的影响
- token 是什么（注意上面输出的"消耗 token"数字）
