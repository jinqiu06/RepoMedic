import json
import pytest

from unittest.mock import Mock
from pydantic import ValidationError
from langchain_core.messages import AIMessage

from repomedic.llm_client import diagnose_error
from repomedic.llm_models import LLMDiagnosis
import httpx

from openai import (
    APITimeoutError,
    APIConnectionError,
    RateLimitError,
    APIStatusError
)
from repomedic.llm_client import LLMServiceError

model = Mock()

def test_diagnose_success():
    error_info = {
    "error_type": "ZeroDivisionError",
    "message": "division by zero",
    "file_path": "demo.py",
    "line_number": 3,
    "function": "divide",
    "source_context": None
}

    response_data = {
    "status": "diagnosed",
    "root_cause": "除数为零",
    "evidence": ["第3行执行了除法"],
    "suggested_fix": "检查除数是否为零",
    "verification_steps": ["测试除数为零的情况"],
    "limitations": []
}
    model.invoke.return_value = AIMessage(
        content=json.dumps(response_data, ensure_ascii=False)
    )

    answer = diagnose_error(error_info,model)

    assert isinstance(answer, LLMDiagnosis)
    assert answer.status == "diagnosed"
    assert answer.root_cause == "除数为零"
def test_diagnose_empty():
    error_info = {
    "error_type": "ZeroDivisionError",
    "message": "division by zero",
    "file_path": "demo.py",
    "line_number": 3,
    "function": "divide",
    "source_context": None
}
    model.invoke.return_value = AIMessage(content = "")


    with pytest.raises(ValueError):
        diagnose_error(error_info,model)
def test_diagnose_invalid_schema():
    error_info = {
        "error_type": "ZeroDivisionError",
        "message": "division by zero",
        "file_path": "demo.py",
        "line_number": 3,
        "function": "divide",
        "source_context": None
    }
    
    model.invoke.return_value = AIMessage(
            content = '{"status": "diagnosed"}'
        )

    with pytest.raises(ValidationError):
        diagnose_error(error_info,model) 

def test_llm_timeout():
    error_info = {
    "error_type": "ZeroDivisionError",
    "message": "division by zero"
}
    request = httpx.Request(
        "POST",
        "https://example.invalid/v1/chat/completions"
    )
    model.invoke.side_effect = APITimeoutError(request = request)

    with pytest.raises(LLMServiceError,match = "请求超时"):
        diagnose_error(error_info,model)
def test_llm_connection_error():
    error_info = {
    "error_type": "ZeroDivisionError",
    "message": "division by zero"
}
    request = httpx.Request(
            "POST",
            "https://example.invalid/v1/chat/completions"
        )
    model.invoke.side_effect = APIConnectionError(request = request)

    with pytest.raises(LLMServiceError,match = "无法连接LLM服务"):
        diagnose_error(error_info,model)
