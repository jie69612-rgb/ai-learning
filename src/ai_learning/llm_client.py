"""LLM 客户端封装 —— 这是你第 0 周要完成的核心练习。

设计目标（面试会问，所以要能讲清为什么）：
1. 调用逻辑与业务逻辑分离：任何脚本 import 就能用，不许写成一把梭脚本
2. 网络调用必须能失败：超时 + 重试 + 指数退避
3. 每一次调用都要能看到成本：token 用量、耗时
4. 错误信息对人友好：key 错、余额不足、限流，分别给不同提示

文件里标了 TODO 的部分是留给你写的，其余是我给的脚手架。
写之前先读一遍 usage / exceptions 的用法。
"""

from __future__ import annotations

import logging
import random
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Sequence, TypeVar

from openai import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    AuthenticationError,
    BadRequestError,
    OpenAI,
    RateLimitError,
)

from .config import Settings, load_settings

logger = logging.getLogger(__name__)

T = TypeVar("T")

Message = dict[str, str]


# --------------------------------------------------------------------------
# 第一部分：数据模型（已完成，读懂即可）
# --------------------------------------------------------------------------


@dataclass
class TokenUsage:
    """一次调用的 token 消耗。"""

    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0

    @classmethod
    def from_response(cls, usage: Any) -> "TokenUsage":
        """从 SDK 响应的 usage 字段构造。usage 可能为 None，要防住。"""
        if usage is None:
            return cls()
        return cls(
            prompt_tokens=getattr(usage, "prompt_tokens", 0) or 0,
            completion_tokens=getattr(usage, "completion_tokens", 0) or 0,
            total_tokens=getattr(usage, "total_tokens", 0) or 0,
        )


@dataclass
class ChatResult:
    """一次对话调用的完整结果，比裸返回 str 信息量大得多。"""

    content: str
    model: str
    usage: TokenUsage
    elapsed_seconds: float
    attempts: int = 1
    finish_reason: str | None = None

    def cost_cny(self, price_in: float = 2.0, price_out: float = 8.0) -> float:
        """按 DeepSeek 大致价格估算人民币花费（元 / 百万 token）。

        注意：价格会变，参数留成可覆盖的，别把价格写死在业务代码里。
        """
        return (
            self.usage.prompt_tokens / 1_000_000 * price_in
            + self.usage.completion_tokens / 1_000_000 * price_out
        )


class LLMError(RuntimeError):
    """所有 LLM 调用错误的基类，方便上层统一捕获。"""


class LLMAuthError(LLMError):
    """key 不对或没权限 —— 重试没有意义。"""


class LLMBadRequestError(LLMError):
    """请求本身有问题（参数错、上下文超长）—— 重试没有意义。"""


class LLMTransientError(LLMError):
    """临时故障（网络抖动、限流、5xx）—— 值得重试。"""


# --------------------------------------------------------------------------
# 第二部分：重试工具（已完成，读懂即可）
# --------------------------------------------------------------------------


def retry_with_backoff(
    func: Callable[[], T],
    *,
    max_retries: int = 3,
    base_delay: float = 0.5,
    max_delay: float = 8.0,
    jitter: bool = True,
    on_retry: Callable[[int, Exception, float], None] | None = None,
) -> T:
    """执行 func，遇到 LLMTransientError 时按指数退避重试。

    退避序列大致为：0.5s, 1s, 2s（加随机抖动，避免多客户端同时重试打爆服务端）。

    Args:
        func: 无参可调用对象，内部负责抛 LLMTransientError。
        max_retries: 最多重试次数（不含首次调用）。
        base_delay: 首次重试等待秒数。
        max_delay: 单次等待上限。
        jitter: 是否加随机抖动。
        on_retry: 回调 (第几次重试, 异常, 等待秒数)，用于打日志。

    Returns:
        func 的返回值。

    Raises:
        最后一次的异常（非 LLMTransientError 会立刻向上抛，不重试）。
    """
    attempt = 0
    while True:
        try:
            return func()
        except LLMTransientError as exc:
            if attempt >= max_retries:
                logger.error("重试 %d 次后仍失败：%s", max_retries, exc)
                raise
            delay = min(base_delay * (2**attempt), max_delay)
            if jitter:
                delay *= 0.5 + random.random()
            attempt += 1
            if on_retry is not None:
                on_retry(attempt, exc, delay)
            time.sleep(delay)


# --------------------------------------------------------------------------
# 第三部分：客户端（TODO 留给你）
# --------------------------------------------------------------------------


class LLMClient:
    """DeepSeek 客户端封装（OpenAI 兼容协议）。

    用法：
        client = LLMClient()
        result = client.chat([{"role": "user", "content": "你好"}])
        print(result.content, result.usage.total_tokens, result.elapsed_seconds)

    要求：
    - 构造函数里从 Settings 建 OpenAI 客户端，并显式设置 timeout
    - chat() 必须走 retry_with_backoff
    - 异常必须翻译成上面定义的 LLMError 子类
    """

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or load_settings()
        self._client = OpenAI(
            api_key=self.settings.api_key,
            base_url=self.settings.base_url,
            timeout=self.settings.timeout_seconds,
        )

    # ---------------- TODO 1：完成这个方法 ----------------
    def _call_once(
        self,
        messages: Sequence[Message],
        model: str,
        temperature: float,
        max_tokens: int | None,
        response_format: dict[str, str] | None,
    ) -> Any:
        """发一次请求，不做重试。把 SDK 异常翻译成我们的异常体系。

        翻译规则（这张表是重点，面试会问为什么要这么分）：
            AuthenticationError        -> LLMAuthError        （不重试，key 问题重试无用）
            BadRequestError            -> LLMBadRequestError  （不重试，请求本身有问题）
            RateLimitError             -> LLMTransientError   （重试，等一会可能就好了）
            APITimeoutError            -> LLMTransientError   （重试）
            APIConnectionError         -> LLMTransientError   （重试）
            APIStatusError >= 500      -> LLMTransientError   （重试）
            APIStatusError 其他 4xx     -> LLMError            （不重试）
        """
        # 提示：
        # 1) 组装 kwargs；max_tokens 为 None 时不要放进 kwargs，否则某些模型会报错
        # 2) response_format 同理
        # 3) 用 self._client.chat.completions.create(...) 发起调用
        # 4) 捕获上面那些异常做翻译，记住 RateLimitError 是 APIStatusError 的子类，
        #    所以捕获顺序很重要：具体的在前，宽泛的在后
        raise NotImplementedError("TODO 1")

    # ---------------- TODO 2：完成这个方法 ----------------
    def chat(
        self,
        messages: Sequence[Message],
        *,
        model: str | None = None,
        temperature: float = 0.0,
        max_tokens: int | None = None,
        response_format: dict[str, str] | None = None,
    ) -> ChatResult:
        """对外主入口：带重试、带计时、返回结构化结果。

        必须做到：
        1. 用 time.perf_counter() 计时（比 time.time() 精度高，不受系统时钟调整影响）
        2. 通过 retry_with_backoff 调用 _call_once，on_retry 里打 warning 日志
        3. 记录实际重试次数到 ChatResult.attempts
        4. 从 response.choices[0].message.content 取文本，
           从 response.usage 取 token（用 TokenUsage.from_response）
        5. content 可能是 None（比如模型只返回工具调用），要处理成空字符串
        """
        raise NotImplementedError("TODO 2")

    def stream_chat(
        self,
        messages: Sequence[Message],
        *,
        model: str | None = None,
        temperature: float = 0.0,
    ) -> Any:
        """（进阶，第 2 周做）流式输出，逐块 yield 文本。

        为什么需要流式？首 token 延迟 vs 总耗时的区别，写笔记里解释。
        """
        raise NotImplementedError("第 2 周再做")
