from typing import Literal
from pydantic import BaseModel, ConfigDict, Field

class LLMDiagnosis(BaseModel):
    status:Literal['diagnosed','insufficient_context']
    root_cause:str | None
    evidence:list[str]
    suggested_fix:str | None
    verification_steps:list[str]
    limitations:list[str]
    model_config = ConfigDict(extra="forbid")