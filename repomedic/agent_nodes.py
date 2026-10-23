import logging
from typing import Any

from repomedic.agent_state import AgentState
from repomedic.config import get_load
from repomedic.llm_models import InvestigationDecision
from repomedic.prompt_builder import build_investigation_messages


logger = logging.getLogger(__name__)


def decision_node(state: AgentState, model: Any = None) -> dict[str, Any]:
    error_info = state.get("error_info")

    if not isinstance(error_info, dict) or not error_info:
        return {
            "investigation_decision": None,
            "error_message": "有效的错误信息缺失",
        }

    try:
        messages = build_investigation_messages(error_info)

        model = model if model is not None else get_load()
        structured_model = model.with_structured_output(
            InvestigationDecision,
            method="function_calling",
        )

        decision = structured_model.invoke(messages)

        if not isinstance(decision, InvestigationDecision):
            raise TypeError("模型未返回有效的调查决策")

        return {
            "investigation_decision": decision,
            "error_message": None,
        }

    except Exception as exc:
        # 不记录异常正文，避免意外记录敏感信息
        logger.error(
            "调查决策节点执行失败，异常类型：%s",
            type(exc).__name__,
        )
        return {
            "investigation_decision": None,
            "error_message": "调查决策失败，请检查模型配置、请求状态或输出格式",
        }


def investigation_node(state: AgentState) -> dict[str, Any]:
    """Execute a single bounded investigation without running project code."""
    from repomedic.code_search import search_symbol
    from repomedic.source_reader import read_source_context

    results, contexts, warnings = [], [], []
    seen = set()
    decision = state.get("investigation_decision")
    if decision is None or not decision.needs_investigation:
        return {"search_results": results, "additional_context": contexts}
    for symbol in decision.symbols[:3]:
        try:
            matches = search_symbol(state["project_root"], symbol, max_results=2)
            results.append({"symbol": symbol, "matches": matches})
            if not matches:
                warnings.append(f"未找到符号：{symbol}")
            for match in matches:
                key = (match["file_path"], match["line_number"])
                if key in seen:
                    continue
                seen.add(key)
                context = read_source_context(
                    state["project_root"], *key, context_lines=5
                )
                if context is not None:
                    contexts.append({"symbol": symbol, **context})
                else:
                    warnings.append(f"无法读取符号上下文：{symbol}")
        except (OSError, UnicodeError, ValueError):
            warnings.append(f"调查未完成：{symbol}")
    return {"search_results": results, "additional_context": contexts,
            "warnings": warnings}


def diagnosis_node(state: AgentState, model: Any = None) -> dict[str, Any]:
    from repomedic.llm_client import diagnose_error

    try:
        info = {**state["error_info"],
                "additional_context": state.get("additional_context", [])}
        model = model if model is not None else get_load()
        diagnosis = diagnose_error(info, model)
        return {"diagnosis": diagnosis, "error_message": None}
    except Exception as exc:
        logger.error("最终诊断失败，异常类型：%s", type(exc).__name__)
        return {"diagnosis": None, "error_message": "最终诊断失败，请检查模型配置、输入大小或响应格式"}
