from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Mapped, mapped_column

from repopilot.database.sqlite import Base


class AnalysisRecord(Base):
    __tablename__ = "analysis_records"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    repo_url: Mapped[str] = mapped_column(unique=True)
    repo_name: Mapped[str] = mapped_column(index=True)
    analyzed_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    summary: Mapped[str]
    maturity_level: Mapped[str]
    difficulty_level: Mapped[str]
    overall_score: Mapped[float]
    analysis_json: Mapped[str]
    raw_response: Mapped[Optional[str]] = mapped_column(default="")
