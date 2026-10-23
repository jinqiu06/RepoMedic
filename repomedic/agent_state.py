
from typing import Any, NotRequired, TypedDict

from repomedic.llm_models import InvestigationDecision, LLMDiagnosis


class AgentState(TypedDict):
    project_root: str
    error_info: dict[str, Any]

    investigation_decision: NotRequired[InvestigationDecision | None]
    search_results: NotRequired[list[dict[str, Any]]]
    additional_context: NotRequired[list[dict[str, Any]]]
    diagnosis: NotRequired[LLMDiagnosis | None]
    error_message: NotRequired[str | None]
    warnings: NotRequired[list[str]]
