import json
import pytest

from langchain_core.messages import SystemMessage, HumanMessage

from repomedic.prompt_builder import (
    build_diagnosis_messages,
    MAX_PROMPT_BYTES
)

def test_build_normal():
    error_info = {
        "error_type": "ZeroDivisionError",
        "message": "division by zero",
        "file_path": "demo.py",
        "line_number": 3
    }

    messages = build_diagnosis_messages(error_info)

    assert len(messages) == 2

    assert isinstance(messages[0], SystemMessage)
    assert isinstance(messages[1], HumanMessage)

    data = json.loads(messages[1].content)

    assert data["error_type"] == "ZeroDivisionError"
    assert data["line_number"] == 3

def test_build_empty():
    error_info = {}

    with pytest.raises(ValueError):
      build_diagnosis_messages(error_info)
      
def test_build_invalid_type():
   error_info = "这是一个字符串"

   with pytest.raises(TypeError):
      build_diagnosis_messages(error_info)
   
def test_build_missing_error_type():
   error_info = {
      'message':'division by zero'
   }

   with pytest.raises(ValueError):
      build_diagnosis_messages(error_info)

def test_build_whitelist():
   error_info = {
    "error_type": "ZeroDivisionError",
    "message": "division by zero",
    "extra_field": "不应该出现在Prompt中"
}
   messages = build_diagnosis_messages(error_info)

   content = json.loads(messages[1].content)

   assert 'extra_field' not in content

def test_build_oversized():
   error_info = {
    "error_type": "ZeroDivisionError",
    "message": "a" * (MAX_PROMPT_BYTES + 1)
}
   with pytest.raises(ValueError):
      build_diagnosis_messages(error_info)