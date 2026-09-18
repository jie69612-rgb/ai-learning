"""Day 01 练习：跑通 LLM 调用，并观察 API 的行为。

运行前：
    1. 激活虚拟环境：.\.venv\Scripts\Activate.ps1
    2. 确认 .env 里有 DEEPSEEK_API_KEY
    3. 在仓库根目录运行：python days\week00\day01_exercise.py

这个文件依赖 src/ai_learning/llm_client.py —— 那个文件的 TODO 由你补完。
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

# 让脚本能 import 到 src 下的包（不用装成 package）
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from ai_learning.config import ConfigError, load_settings  # noqa: E402
from ai_learning.llm_client import LLMClient, LLMError  # noqa: E402

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)


def experiment_temperature(client: LLMClient) -> None:
    """练习 1：同一问题换 temperature，观察差别。

    TODO（你写）：
        - 对 temperature ∈ {0, 0.7, 1.5} 各调用一次
        - 问题用："用一句话解释什么是 RAG"
        - 打印每个 temperature 下的回答、耗时、总 token
        - 观察：0 跑两次结果一样吗？1.5 呢？把结论写进 notes.md

    要求：用 client.chat(...)，不要绕过封装直接调 SDK。
    """
    raise NotImplementedError("练习 1")


def experiment_json_output(client: LLMClient) -> None:
    """练习 2：强制模型输出合法 JSON。

    TODO（你写）：
        - 用 response_format={"type": "json_object"}
        - 让模型输出："学习 RAG 的 3 个步骤，每步含 name 和 duration 字段"
        - 用 json.loads 解析并打印，验证它是合法 JSON
        - 进阶：把 json.loads 的结果用 pydantic 校验（第 1 周学，先留个 TODO 注释）

    坑：json_object 模式要求提示词里必须出现 "json" 这个词，否则 DeepSeek 会报错。
        亲自踩一次这个坑，把报错信息记进 notes.md。
    """
    raise NotImplementedError("练习 2")


def experiment_error_handling() -> None:
    """练习 3：验证错误处理真的有效（不是摆设）。

    TODO（你写）：
        - 故意用错误的 key（比如 "sk-wrong"）建一个 Settings，调用一次
        - 期望：抛出 LLMAuthError，且提示信息是人话，不是 traceback 糊脸
        - 再故意把 timeout 设成 0.001 秒，观察是否触发重试（看日志里的 warning）
        - 把两次观察结果记进 notes.md
    """
    raise NotImplementedError("练习 3")


def main() -> int:
    try:
        settings = load_settings()
    except ConfigError as exc:
        print(f"\n配置有问题：\n{exc}\n", file=sys.stderr)
        return 1

    print(f"使用模型：{settings.default_model}")
    print(f"超时：{settings.timeout_seconds}s ｜ 最大重试：{settings.max_retries}\n")

    client = LLMClient(settings)

    try:
        # 骨架：先跑一个最简单的调用，确认链路通了
        result = client.chat(
            [
                {"role": "system", "content": "你是一个简洁的中文 AI 老师。"},
                {"role": "user", "content": "用一句话说明什么是 RAG"},
            ]
        )
        print("回答：", result.content)
        print(f"\n耗时：{result.elapsed_seconds:.2f}s")
        print(f"token：输入 {result.usage.prompt_tokens} / 输出 {result.usage.completion_tokens} / 合计 {result.usage.total_tokens}")
        print(f"重试次数：{result.attempts}")
        print(f"估算花费：¥{result.cost_cny():.6f}")
    except LLMError as exc:
        print(f"\n调用失败：{exc}", file=sys.stderr)
        return 1

    print("\n" + "=" * 50)
    print("接下来把上面三个 experiment_* 函数补完，逐个取消注释运行：")
    # experiment_temperature(client)
    # experiment_json_output(client)
    # experiment_error_handling()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
