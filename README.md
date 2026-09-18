# AI 大模型应用开发学习日志

> 目标岗位：大模型应用开发工程师 / AI 应用工程师
> 起点：2026-09 ｜ 每日 4-6 小时 ｜ 计划 10 周达到「可投简历」状态
> 完整路径：`../AI-Agent学习路径-10周.md`（含每周任务、资源清单、项目规格）

## 路线速查（4 个阶段）

| 阶段 | 时间 | 内容 | 交付物 |
| --- | --- | --- | --- |
| 1 API 基础 | 第 1-2 周 | Prompt / token / function calling | 3 个小工具 |
| 2 手写 RAG | 第 3-6 周 | 先手写 naive RAG，再用 LangChain | 作品 1 |
| 3 Agent 项目 | 第 7-10 周 | Text2SQL + 数据分析智能体 | 作品 2、3 |
| 4 包装求职 | 第 11-14 周 | README 包装、博客、PR、投递 | 简历 |

## 进度看板（每完成一天就更新这里）

| 周 | 主题 | 产物 | 状态 |
| --- | --- | --- | --- |
| W0 | API 打通 + 工程习惯 | `src/ai_learning/llm_client.py`（重试/超时/成本统计） | 🚧 进行中 |
| W1 | Python 工程能力：类型注解 / 异步 / 测试 / 日志 | 命令行 AI 笔记助手 CLI | ⬜ |
| W2 | LLM 基础与提示词工程 | 多轮对话 + 结构化抽取器 | ⬜ |
| W3 | 向量检索与 RAG（**不用框架手写一遍**） | 手写 RAG 链路 + 评测脚本 | ⬜ |
| W4-5 | 项目 2：本地知识库 RAG 问答 Agent | 独立仓库 `rag-knowledge-agent` | ⬜ |
| W6 | 工具调用与 ReAct（**手写 Agent 循环**） | 无框架 Agent | ⬜ |
| W7 | LangGraph / MCP / 多智能体 / Dify | 框架对比笔记 + MCP Server | ⬜ |
| W8-9 | 项目 3：智能数据分析 Agent（Text2SQL） | 独立仓库 `analytics-agent` | ⬜ |
| W10 | FastAPI + Docker 部署、简历、模拟面试 | 线上 Demo + 面试材料 | ⬜ |

## 目录结构

```
ai-learning/
├── src/ai_learning/          # 可复用包（所有练习都 import 它）
│   ├── config.py             # 配置统一入口（环境变量只在这里读）
│   └── llm_client.py         # LLM 客户端封装：重试 / 超时 / token 统计
├── days/                     # 按周存放练习代码
│   └── week00/
│       ├── day01_exercise.py # 可运行练习脚本
│       └── notes.md          # 当天笔记与必答问题
├── .env.example              # 环境变量模板（.env 已被 gitignore）
├── requirements.txt
└── pyproject.toml            # ruff + mypy 配置
```

**为什么用 `src/` 布局**：练习脚本会被反复丢弃重写，但 `ai_learning` 包会逐步长大，最后成为项目核心。面试官看仓库先看这个分层。

## 每日流程（雷打不动）

1. 看课/读教程 ≤ 1 小时
2. 写代码 ≥ 1 小时
3. 10 分钟写学习日志，`git push` 到 GitHub

## 三条铁律

- 每天 push，让 GitHub 绿点连起来（零工作经历时这就是你的经历证明）
- API Key 永远不进 git（放 `.env`，已被 `.gitignore` 排除）
- 先手工、后框架：手写 RAG 是面试分水岭，不能跳过

## 环境准备

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
Copy-Item .env.example .env      # 然后编辑 .env 填入 DEEPSEEK_API_KEY
python days\week00\day01_exercise.py
```

### 本机 git 特殊配置（重要）

这台机器 git 默认 TLS 后端（schannel）连 GitHub 会报 `SEC_E_NO_CREDENTIALS`，已改为：

```powershell
git config --global http.sslBackend openssl
git config --global http.proxy  http://127.0.0.1:7897
git config --global https.proxy http://127.0.0.1:7897
```

代理换端口后要同步改这两条。

## 提交前自查（防泄露 key）

```powershell
# 应该没有任何输出
git log -p | Select-String "sk-"
```
