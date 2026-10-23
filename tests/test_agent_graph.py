import json
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from repomedic.agent_graph import run_agent
from repomedic.llm_models import InvestigationDecision
from repomedic.prompt_builder import build_diagnosis_messages


def fake_model(investigate=True):
    model = Mock()
    model.with_structured_output.return_value.invoke.return_value = InvestigationDecision(
        needs_investigation=investigate, symbols=["load_user"] if investigate else [],
        reason="需要检查返回值",
    )
    model.invoke.return_value = SimpleNamespace(content=json.dumps({
        "status": "diagnosed", "root_cause": "返回空值", "evidence": ["源码返回 None"],
        "suggested_fix": "校验返回值", "verification_steps": ["增加空值测试"],
        "limitations": ["未运行项目"],
    }))
    return model


@pytest.mark.parametrize("investigate", [True, False])
def test_graph_paths(tmp_path, investigate):
    (tmp_path / "users.py").write_text('def load_user():\n    password = "hidden-secret"\n    return None\n', encoding="utf-8")
    model = fake_model(investigate)
    result = run_agent(str(tmp_path), {"error_type": "TypeError"}, model)
    assert result["diagnosis"].status == "diagnosed"
    assert model.invoke.call_count == 1
    assert model.with_structured_output.return_value.invoke.call_count == 1
    payload = json.loads(model.invoke.call_args.args[0][1].content)
    assert bool(payload["additional_context"]) == investigate
    assert "hidden-secret" not in model.invoke.call_args.args[0][1].content


def test_decision_failure_terminates(tmp_path):
    model = fake_model()
    model.with_structured_output.return_value.invoke.side_effect = RuntimeError("private-key")
    state = run_agent(str(tmp_path), {"error_type": "TypeError"}, model)
    assert state["error_message"]
    assert "private-key" not in state["error_message"]
    model.invoke.assert_not_called()


def test_missing_symbol_still_diagnoses(tmp_path):
    state = run_agent(str(tmp_path), {"error_type": "TypeError"}, fake_model())
    assert state["warnings"]
    assert state["diagnosis"]


def test_invalid_final_output(tmp_path):
    model = fake_model(False)
    model.invoke.return_value.content = "invalid"
    state = run_agent(str(tmp_path), {"error_type": "TypeError"}, model)
    assert state["diagnosis"] is None
    assert state["error_message"]


def test_symbol_validation():
    with pytest.raises(ValueError):
        InvestigationDecision(needs_investigation=True, symbols=["../secret"], reason="x")


def test_additional_evidence_size_limit():
    with pytest.raises(ValueError):
        build_diagnosis_messages({"error_type": "TypeError", "additional_context": ["x" * 20000]})
