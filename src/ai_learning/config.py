"""配置读取：所有环境变量只在这里读，其他地方不许直接 os.getenv。

为什么统一入口？
- 换模型/换供应商时只改一处
- 缺 key 时能给出人话提示，而不是让 SDK 抛一堆 traceback
- 测试时容易 monkeypatch
"""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


class ConfigError(RuntimeError):
    """配置缺失或不合法。刻意用自定义异常，方便上层区分处理。"""


@dataclass(frozen=True)
class Settings:
    """运行配置。frozen=True 表示创建后不可修改（不可变配置，好测试）。"""

    api_key: str
    base_url: str
    default_model: str
    timeout_seconds: float = 60.0
    max_retries: int = 3


def load_settings() -> Settings:
    """从环境变量组装配置，缺失关键项就报错。

    Raises:
        ConfigError: DEEPSEEK_API_KEY 未设置。
    """
    api_key = (os.getenv("DEEPSEEK_API_KEY") or "").strip()
    if not api_key:
        raise ConfigError(
            "没找到 DEEPSEEK_API_KEY。\n"
            "解决方式（二选一）：\n"
            "  1) 把 .env.example 复制成 .env，填入你的 key：\n"
            "     Copy-Item .env.example .env\n"
            "  2) 当前终端临时设置：\n"
            "     $env:DEEPSEEK_API_KEY='sk-你的key'"
        )

    return Settings(
        api_key=api_key,
        base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
        default_model=os.getenv("DEFAULT_MODEL", "deepseek-chat"),
        timeout_seconds=float(os.getenv("LLM_TIMEOUT_SECONDS", "60")),
        max_retries=int(os.getenv("LLM_MAX_RETRIES", "3")),
    )
