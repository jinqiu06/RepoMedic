
import re
from typing import Any


# 匹配 API Key、密码等敏感变量的赋值
SECRET_PATTERN = re.compile(
    r"""(?P<prefix>\b(?:api[_-]?key|password|passwd|secret|access[_-]?token|token)\b["']?\s*[:=]\s*)(?P<quote>["'])(?P<value>.*?)(?P=quote)""",
    re.IGNORECASE
)

# 匹配 Bearer Token
BEARER_PATTERN = re.compile(
    r"(?P<prefix>\bBearer\s+)[A-Za-z0-9._~+/\-=]+",
    re.IGNORECASE
)


def redact_text(text: str) -> str:
    """对字符串中的常见敏感信息进行脱敏。"""

    # 1. 处理 API_KEY、password 等赋值
    text = SECRET_PATTERN.sub(
        lambda match: (
            match.group("prefix")
            + match.group("quote")
            + "[REDACTED]"
            + match.group("quote")
        ),
        text
    )

    # 2. 处理 Bearer Token
    text = BEARER_PATTERN.sub(
        r"\g<prefix>[REDACTED]",
        text
    )

    return text


def sanitize_error_info(
    error_info: dict[str, Any]
) -> dict[str, Any]:
    """递归脱敏错误信息，保留原始数据不变。"""

    def sanitize(value: Any) -> Any:

        if isinstance(value, str):
            return redact_text(value)

        if isinstance(value, dict):
            return {
                key: sanitize(item)
                for key, item in value.items()
            }

        if isinstance(value, list):
            return [
                sanitize(item)
                for item in value
            ]

        return value

    return sanitize(error_info)
