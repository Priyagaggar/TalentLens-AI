
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class SkillMatchDetails(BaseModel):
    match_percentage: float
    matched_skills: List[str]
    partial_matches: List[Dict[str, Any]]
    missing_skills: List[str]
    extra_skills: List[str]

class ResumeAnalysisResponse(BaseModel):
    filename: str
    name_inferred: str = "Unknown"
    emails: List[str]
    phones: List[str]
    years_of_experience: float
    extracted_skills: Dict[str, List[str]]
    
    # Matching Scores
    tfidf_similarity: float
    skill_match_details: SkillMatchDetails
    
    # Final Ranking Score (if we were ranking relative to something, but here it's per resume)
    # We can include a "composite_score" for this single resume
    final_score: float
    scoring_explanation: str

class UploadResponse(BaseModel):
    job_description_id: str
    resume_ids: List[str]
    message: str

class BatchAnalysisRequest(BaseModel):
    job_description_id: str
    resume_ids: List[str]

class RankedCandidate(BaseModel):
    resume_id: str
    name: str = "Unknown"
    final_score: float
    tfidf_score: float
    skill_match_percentage: float
    experience_years: float
    matched_skills: List[str]
    missing_skills: List[str]
    explanation: str

class BatchAnalysisResponse(BaseModel):
    ranked_candidates: List[RankedCandidate]
    processing_time: str

class ErrorResponse(BaseModel):
    detail: str
