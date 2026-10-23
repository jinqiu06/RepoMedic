from typing import Literal,Self
from pydantic import BaseModel, ConfigDict, Field,field_validator,model_validator

class LLMDiagnosis(BaseModel):
    status:Literal['diagnosed','insufficient_context']
    root_cause:str | None
    evidence:list[str]
    suggested_fix:str | None
    verification_steps:list[str]
    limitations:list[str]
    model_config = ConfigDict(extra="forbid")

class InvestigationDecision(BaseModel):
    needs_investigation:bool
    symbols:list[str] = Field(max_length = 3)
    reason:str = Field(min_length = 1,max_length = 300)
    model_config = ConfigDict(extra="forbid", strict=True)

    @field_validator("symbols")
    @classmethod
    def validate_symbols(cls, symbols: list[str]) -> list[str]:
        if any(not symbol.isidentifier() for symbol in symbols):
            raise ValueError("symbols 必须是合法的 Python 标识符")
        if len(symbols) != len(set(symbols)):
           raise ValueError("symbols 不允许重复")
        return symbols

    @model_validator(mode="after")
    def validate_decision(self) -> Self:
    # 在这里检查字段之间的关系
        if self.needs_investigation and not self.symbols:
           raise ValueError("需要调查时,symbols 不能为空")
        elif not self.needs_investigation and self.symbols:
            raise ValueError("不需要调查时,symbols应为空")
        return self
