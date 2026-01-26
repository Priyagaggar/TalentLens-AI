
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete

from app.config import settings
from app.db.models import Base, JobDescription, Resume, RankingResult

# Initializing Engine
# Note: config.DATABASE_URL is "sqlite:///./sql_app.db", for async we need "sqlite+aiosqlite:///..."
DATABASE_URL = settings.DATABASE_URL.replace("sqlite://", "sqlite+aiosqlite://")

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

logger = logging.getLogger(__name__)

async def init_db():
    """Initializes the database by creating tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database initialized.")

# --- CRUD Functions ---

async def save_job_description(jd_data: Dict[str, Any]):
    """Saves a Job Description."""
    async with AsyncSessionLocal() as session:
        async with session.begin():
            jd = JobDescription(**jd_data)
            session.add(jd)
            # Commit happens automatically with session.begin() context
            
async def save_resume(resume_data: Dict[str, Any]):
    """Saves a Resume."""
    async with AsyncSessionLocal() as session:
        async with session.begin():
            resume = Resume(**resume_data)
            session.add(resume)

async def save_ranking_result(ranking_data: Dict[str, Any]):
    """Saves a Ranking Result."""
    async with AsyncSessionLocal() as session:
        async with session.begin():
            result = RankingResult(**ranking_data)
            session.add(result)

async def get_job_description(jd_id: str) -> Optional[JobDescription]:
    """Retrieves a Job Description by ID."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(JobDescription).where(JobDescription.id == jd_id))
        return result.scalars().first()

async def get_resume(resume_id: str) -> Optional[Resume]:
    """Retrieves a Resume by ID."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Resume).where(Resume.id == resume_id))
        return result.scalars().first()

async def get_rankings_for_job(jd_id: str) -> List[RankingResult]:
    """Retrieves all rankings for a specific Job Description."""
    async with AsyncSessionLocal() as session:
        # Order by score desc
        stmt = select(RankingResult).where(RankingResult.job_description_id == jd_id).order_by(RankingResult.total_score.desc())
        result = await session.execute(stmt)
        return result.scalars().all()

async def delete_old_records(days: int = 30):
    """Deletes records older than X days."""
    cutoff = datetime.utcnow() - timedelta(days=days)
    async with AsyncSessionLocal() as session:
        async with session.begin():
            # Delete old rankings first (FK constraint usually requires this or cascade)
            await session.execute(delete(RankingResult).where(RankingResult.created_at < cutoff))
            await session.execute(delete(JobDescription).where(JobDescription.created_at < cutoff))
            await session.execute(delete(Resume).where(Resume.created_at < cutoff))
            logger.info(f"Deleted records older than {days} days.")
