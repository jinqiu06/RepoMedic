from typing import Any

from langchain_core.language_models.chat_models import BaseChatModel

from repomedic.llm_models import LLMDiagnosis
from repomedic.prompt_builder import build_diagnosis_messages
from openai import (
    APITimeoutError,
    APIConnectionError,
    RateLimitError,
    APIStatusError
)
class LLMServiceError(RuntimeError):
    """LLM 服务调用失败"""
    pass

def diagnose_error(
    error_info: dict[str, Any],
    model: BaseChatModel
) -> LLMDiagnosis:
    message = build_diagnosis_messages(error_info)
    try:
       response = model.invoke(message)

    except APITimeoutError as exc:
        raise LLMServiceError('LLM 请求超时') from exc
    
    except APIConnectionError as exc:
        raise LLMServiceError('无法连接LLM服务') from exc
    
    except RateLimitError as exc:
        raise LLMServiceError('LLM请求收到限流') from exc 
    
    except APIStatusError as exc:
        raise LLMServiceError('LLM服务返回HTTP错误状态') from exc 
    
    answer = response.content

    if not isinstance(answer,str) or not answer.strip():
        raise ValueError('LLM返回内容为空或不是字符串')

    diagnosis = LLMDiagnosis.model_validate_json(answer)

    return diagnosis

    