from pydantic import BaseModel, Field


class TechStack(BaseModel):
    language: str = ""
    architecture: str = ""
    core_deps: list[str] = Field(default_factory=list)


class Suggestions(BaseModel):
    beginner: str = ""
    intermediate: str = ""
    senior: str = ""


class AnalysisResult(BaseModel):
    summary: str
    positioning: str = ""
    tech_stack: TechStack = Field(default_factory=TechStack)
    highlights: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    suggestions: Suggestions = Field(default_factory=Suggestions)
    target_audience: list[str] = Field(default_factory=list)
    career_value: str = ""
    maturity_score: float = 0.0   # 1-5，映射到 L1-L5
    difficulty_score: float = 0.0  # 1-5，映射到 D1-D5
    overall_score: float = 0.0     # 0-10
    confidence: float = 1.0        # LLM 自评置信度 0-1


class GradeResult(BaseModel):
    maturity_level: str    # L1-L5
    maturity_name: str
    maturity_reason: str = ""
    difficulty_level: str  # D1-D5
    difficulty_name: str
    difficulty_reason: str = ""
