from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, String, Text, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

from models.schemas import Insight, InsightRecord
from utils.config import settings
from utils.logging import get_logger

logger = get_logger(__name__)


class Base(DeclarativeBase):
    pass


class InsightORM(Base):
    __tablename__ = "insights"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    question: Mapped[str] = mapped_column(String(512), nullable=False)
    insight: Mapped[str] = mapped_column(Text, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class InsightRepository:
    def __init__(self) -> None:
        url = settings.postgres_url if settings.use_postgres else "sqlite+pysqlite:///./ontology.db"
        self.engine = create_engine(url, future=True)
        self.session_local = sessionmaker(bind=self.engine, autoflush=False, autocommit=False)

    def initialize(self) -> None:
        Base.metadata.create_all(self.engine)

    def save_insight(self, question: str, payload: Insight) -> None:
        with Session(self.engine) as session:
            record = InsightORM(
                question=question,
                insight=payload.insight,
                confidence=payload.confidence,
                created_at=datetime.now(timezone.utc),
            )
            session.add(record)
            session.commit()
            logger.info("Persisted insight for question: %s", question)

    def list_insights(self, limit: int = 20) -> list[InsightRecord]:
        with Session(self.engine) as session:
            rows = (
                session.query(InsightORM)
                .order_by(InsightORM.created_at.desc())
                .limit(limit)
                .all()
            )
        return [
            InsightRecord(
                question=row.question,
                insight=row.insight,
                confidence=row.confidence,
                created_at=row.created_at,
            )
            for row in rows
        ]
