
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey, JSON
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class JobDescription(Base):
    __tablename__ = "job_descriptions"

    id = Column(String, primary_key=True, index=True) # UUID
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Resume(Base):
    __tablename__ = "resumes"

    id = Column(String, primary_key=True, index=True) # UUID
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=True) # Local path if saved
    extracted_text = Column(Text, nullable=True)
    parsed_data = Column(JSON, nullable=True) # Skills, Exp, Emails etc
    created_at = Column(DateTime, default=datetime.utcnow)

class RankingResult(Base):
    __tablename__ = "ranking_results"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    job_description_id = Column(String, ForeignKey("job_descriptions.id"), nullable=False)
    resume_id = Column(String, ForeignKey("resumes.id"), nullable=False)
    total_score = Column(Float, nullable=False)
    details = Column(JSON, nullable=True) # Breakdown, matched skills, etc.
    created_at = Column(DateTime, default=datetime.utcnow)
