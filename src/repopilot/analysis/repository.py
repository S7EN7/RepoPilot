from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from repopilot.analysis.models import AnalysisRecord
from repopilot.analysis.schemas import AnalysisResult, GradeResult
from repopilot.database.sqlite import AsyncSessionLocal


class AnalysisRepository:
    async def save(
        self,
        repo_url: str,
        repo_name: str,
        result: AnalysisResult,
        grade: GradeResult,
    ) -> AnalysisRecord:
        async with AsyncSessionLocal() as session:
            existing = await session.scalar(
                select(AnalysisRecord).where(AnalysisRecord.repo_url == repo_url)
            )
            if existing:
                existing.analyzed_at = datetime.utcnow()
                existing.summary = result.summary
                existing.maturity_level = grade.maturity_level
                existing.difficulty_level = grade.difficulty_level
                existing.overall_score = result.overall_score
                existing.analysis_json = result.model_dump_json()
                await session.commit()
                await session.refresh(existing)
                return existing

            record = AnalysisRecord(
                repo_url=repo_url,
                repo_name=repo_name,
                analyzed_at=datetime.utcnow(),
                summary=result.summary,
                maturity_level=grade.maturity_level,
                difficulty_level=grade.difficulty_level,
                overall_score=result.overall_score,
                analysis_json=result.model_dump_json(),
            )
            session.add(record)
            await session.commit()
            await session.refresh(record)
            return record

    async def get_history(self) -> list[AnalysisRecord]:
        async with AsyncSessionLocal() as session:
            rows = await session.execute(
                select(AnalysisRecord).order_by(AnalysisRecord.analyzed_at.desc())
            )
            return list(rows.scalars().all())

    async def get_by_repo(self, repo_name: str) -> list[AnalysisRecord]:
        async with AsyncSessionLocal() as session:
            rows = await session.execute(
                select(AnalysisRecord)
                .where(AnalysisRecord.repo_name == repo_name)
                .order_by(AnalysisRecord.analyzed_at.desc())
            )
            return list(rows.scalars().all())
