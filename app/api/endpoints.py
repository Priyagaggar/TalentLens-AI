
import os
import shutil
import logging
from typing import List

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status
from fastapi.responses import JSONResponse

from app.schemas import ResumeAnalysisResponse, ErrorResponse, UploadResponse, BatchAnalysisRequest, BatchAnalysisResponse, RankedCandidate
from app.core.pdf_extractor import extract_text_from_pdf
from app.core.docx_extractor import extract_text_from_docx
from app.core.text_processor import TextProcessor
from app.core.skill_extractor import SkillExtractor
from app.core.experience_extractor import extract_experience
from app.core.resume_matcher import ResumeMatcher
from app.core.skill_matcher import SkillMatcher
from app.core.ranker import Ranker

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize core components (load models once at startup)
text_processor = TextProcessor()
skill_extractor = SkillExtractor()
# Dictionary databases and heavy models loaded here
# ResumeMatcher needs to be fitted per request (per JD), or cache extraction?
# SkillMatcher is stateless.
ranker = Ranker()

@router.post("/analyze", response_model=ResumeAnalysisResponse, responses={400: {"model": ErrorResponse}})
async def analyze_resume(
    resume_file: UploadFile = File(...),
    job_description: str = Form(...)
):
    """
    Analyzes a resume against a job description.
    
    Process:
    1. Extract text from uploaded file (PDF/DOCX).
    2. Extract Key Information (Skills, Exp, Entities).
    3. Match content against Job Description.
    4. Calculate Fit Score.
    """
    
    # 1. Validate File Type
    filename = resume_file.filename
    extension = filename.split(".")[-1].lower()
    
    if extension not in ["pdf", "docx"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file format. Only PDF and DOCX are supported."
        )

    # 2. Save File Temporarily
    temp_dir = "temp_uploads"
    os.makedirs(temp_dir, exist_ok=True)
    temp_path = os.path.join(temp_dir, filename)
    
    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(resume_file.file, buffer)
            
        # 3. Extract Text
        content_text = ""
        try:
            if extension == "pdf":
                content_text = extract_text_from_pdf(temp_path)
            elif extension == "docx":
                content_text = extract_text_from_docx(temp_path)
        except Exception as e:
            logger.error(f"Extraction failed: {e}")
            raise HTTPException(status_code=400, detail=f"Failed to extract text: {str(e)}")
            
        if not content_text:
             raise HTTPException(status_code=400, detail="Could not extract any text from the file.")

        # 4. NLP Processing (Entities, Cleaning)
        processed_data = text_processor.preprocess(content_text)
        
        # 5. Extract Skills from Resume
        # We use the raw text or cleaned text? SkillExtractor handles case, so calculated text.
        # Let's use the 'original_text' passed to TextProcessor (which is content_text)
        # But text_processor.preprocess returns 'skills' using its simple list.
        # We want the ADVANCED SkillExtractor here.
        resume_skills_dict = skill_extractor.extract_skills(content_text)
        
        # Flatten skills for matching
        resume_flat_skills = []
        for cat_skills in resume_skills_dict.values():
            resume_flat_skills.extend(cat_skills)

        # 6. Extract Experience
        years_exp = extract_experience(content_text)

        # 7. Extract Skills from JD (for Gap Analysis)
        jd_skills_dict = skill_extractor.extract_skills(job_description)
        jd_flat_skills = []
        for cat_skills in jd_skills_dict.values():
            jd_flat_skills.extend(cat_skills)
            
        # 8. Skill Matching (Gap Analysis)
        skill_matcher = SkillMatcher()
        skill_match_result = skill_matcher.match_skills(resume_flat_skills, jd_flat_skills)
        
        # 9. Semantic Matching (TF-IDF)
        matcher = ResumeMatcher()
        matcher.fit(job_description)
        tfidf_score = matcher.score_resume(content_text)
        
        # 10. Final Scoring (Using Ranker Logic)
        # Construct a candidate object for the ranker
        candidate_data = {
            "name": filename, # Using filename as fallback for name
            "tfidf_score": tfidf_score,
            "skill_match_percentage": skill_match_result["match_percentage"],
            "years_of_experience": years_exp
        }
        
        # Ranker expects a list, returns a list
        ranked_result = ranker.rank_candidates([candidate_data])[0]
        
        # 11. cleanup and response
        response_data = ResumeAnalysisResponse(
            filename=filename,
            emails=processed_data.get("emails", []),
            phones=processed_data.get("phone_numbers", []),
            years_of_experience=years_exp,
            extracted_skills=resume_skills_dict,
            tfidf_similarity=tfidf_score,
            skill_match_details=skill_match_result,
            final_score=ranked_result["final_score"],
            scoring_explanation=ranked_result.get("scoring_explanation", "")
        )
        
        return response_data

    except Exception as e:
        logger.error(f"Error processing request: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Cleanup
        if os.path.exists(temp_path):
            os.remove(temp_path)

import uuid

@router.post("/upload/resumes", response_model=UploadResponse)
async def upload_resumes(
    resumes: List[UploadFile] = File(...),
    job_description_file: UploadFile = File(None),
    job_description_text: str = Form(None)
):
    """
    Uploads multiple resumes and a job description.
    Validates file types (PDF, DOCX) and size (max 5MB).
    Saves files with UUIDs.
    """
    
    # Validation Constants
    ALLOWED_EXTENSIONS = {"pdf", "docx", "txt"} # txt for JD
    MAX_FILE_SIZE = 5 * 1024 * 1024 # 5MB
    UPLOAD_DIR = "uploaded_files"
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    
    # 1. Handle Job Description
    jd_id = str(uuid.uuid4())
    jd_content = ""
    
    if job_description_text:
        jd_content = job_description_text
        # Save text as file for consistency? Or just return ID? 
        # User wants ID returned, so let's save it.
        jd_path = os.path.join(UPLOAD_DIR, f"{jd_id}.txt")
        with open(jd_path, "w", encoding="utf-8") as f:
            f.write(jd_content)
            
    elif job_description_file:
        # Validate JD file
        ext = job_description_file.filename.split(".")[-1].lower()
        if ext not in ALLOWED_EXTENSIONS:
             raise HTTPException(status_code=400, detail=f"Invalid JD file type: {ext}")
        
        # Save JD File
        jd_path = os.path.join(UPLOAD_DIR, f"{jd_id}.{ext}")
        try:
            content = await job_description_file.read()
            if len(content) > MAX_FILE_SIZE:
                raise HTTPException(status_code=400, detail="Job description file exceeds 5MB limit.")
            
            with open(jd_path, "wb") as f:
                f.write(content)
        except Exception as e:
             raise HTTPException(status_code=500, detail=f"Failed to save JD: {str(e)}")
    else:
        raise HTTPException(status_code=400, detail="Job description is required (text or file).")

    # 2. Handle Resumes
    resume_ids = []
    
    for resume in resumes:
        # Validate Extension
        ext = resume.filename.split(".")[-1].lower()
        if ext not in ["pdf", "docx"]:
            # We could skip or raise error. Raising error is safer for now.
            raise HTTPException(status_code=400, detail=f"Invalid resume file type: {resume.filename}. Only PDF/DOCX allowed.")
        
        # Validate Size and Save
        res_id = str(uuid.uuid4())
        save_path = os.path.join(UPLOAD_DIR, f"{res_id}.{ext}")
        
        try:
            # Read content to check size
            # Note: For very large files this eats memory, but limit is 5MB so it's fine.
            content = await resume.read() 
            if len(content) > MAX_FILE_SIZE:
                 raise HTTPException(status_code=400, detail=f"File {resume.filename} exceeds 5MB limit.")
            
            with open(save_path, "wb") as f:
                f.write(content)
                
            resume_ids.append(res_id)
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to save resume {resume.filename}: {str(e)}")
            
    return {
        "job_description_id": jd_id,
        "resume_ids": resume_ids,
        "message": "Files uploaded successfully"
    }

import time
import asyncio

@router.post("/analyze/batch", response_model=BatchAnalysisResponse)
async def analyze_batch(request: BatchAnalysisRequest):
    """
    Analyzes multiple resumes against a job description.
    Files must have been previously uploaded to get IDs.
    """
    start_time = time.time()
    UPLOAD_DIR = "uploaded_files"
    
    # 1. Resolve Job Description File
    jd_id = request.job_description_id
    jd_text = ""
    # Look for .txt, .pdf, .docx
    found_jd = False
    for ext in ["txt", "pdf", "docx"]:
        path = os.path.join(UPLOAD_DIR, f"{jd_id}.{ext}")
        if os.path.exists(path):
            found_jd = True
            try:
                if ext == "txt":
                    with open(path, "r", encoding="utf-8") as f:
                        jd_text = f.read()
                elif ext == "pdf":
                    jd_text = extract_text_from_pdf(path)
                elif ext == "docx":
                    jd_text = extract_text_from_docx(path)
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to read JD: {str(e)}")
            break
            
    if not found_jd:
        raise HTTPException(status_code=404, detail=f"Job Description {jd_id} not found.")

    if not jd_text.strip():
        raise HTTPException(status_code=400, detail="Job Description text is empty.")

    # 2. Process Resumes Loop
    candidates_data = [] # For Ranking
    results_map = {} # For final response construction
    
    # Fit matcher once
    matcher = ResumeMatcher()
    matcher.fit(jd_text)
    
    # Get JD skills once
    jd_skills_dict = skill_extractor.extract_skills(jd_text)
    jd_flat_skills = []
    for cat_skills in jd_skills_dict.values():
        jd_flat_skills.extend(cat_skills)

    for resume_id in request.resume_ids:
        # Find file
        res_path = None
        for ext in ["pdf", "docx"]:
            path = os.path.join(UPLOAD_DIR, f"{resume_id}.{ext}")
            if os.path.exists(path):
                res_path = path
                break
        
        if not res_path:
            logger.warning(f"Resume {resume_id} not found, skipping.")
            continue
            
        try:
            # Extract Text
            content_text = ""
            if res_path.endswith(".pdf"):
                content_text = extract_text_from_pdf(res_path)
            else:
                content_text = extract_text_from_docx(res_path)
                
            if not content_text:
                continue

            # NLP Extraction
            # We can run these in parallel? For now sequential.
            processed_data = text_processor.preprocess(content_text)
            emails = processed_data.get("emails", [])
            name = emails[0].split("@")[0] if emails else f"Candidate-{resume_id[:4]}"
            
            # Skills
            resume_skills_dict = skill_extractor.extract_skills(content_text)
            resume_flat_skills = []
            for cat_skills in resume_skills_dict.values():
                resume_flat_skills.extend(cat_skills)
                
            # Experience
            years_exp = extract_experience(content_text)
            
            # Scores
            tfidf_score = matcher.score_resume(content_text)
            
            skill_matcher_inst = SkillMatcher()
            skill_result = skill_matcher_inst.match_skills(resume_flat_skills, jd_flat_skills)
            
            # Collect data for Ranker
            cand_obj = {
                "resume_id": resume_id, # Extra field for mapping back
                "name": name,
                "tfidf_score": tfidf_score,
                "skill_match_percentage": skill_result["match_percentage"],
                "years_of_experience": years_exp,
                "matched_skills": skill_result["matched_skills"],
                "missing_skills": skill_result["missing_skills"]
            }
            candidates_data.append(cand_obj)
            
        except Exception as e:
            logger.error(f"Error processing resume {resume_id}: {e}")
            continue

    # 3. Rank
    ranked_list = ranker.rank_candidates(candidates_data)
    
    # 4. Construct Response
    final_output = []
    for ranked in ranked_list:
        final_output.append(RankedCandidate(
            resume_id=ranked["resume_id"],
            name=ranked["name"],
            final_score=ranked["final_score"],
            tfidf_score=ranked["normalized_scores"]["tfidf"], # Use normalized or raw? Request asked for raw score potentially but normalized is decent. 
            # Re-reading request: "tfidf_score": 0.78". That's raw. 
            # My Ranker normalizes internal but keeps input? 
            # Wait, my Ranker rank_candidates returns enriched dict but doesn't overwrite raw inputs unless I did "ranked_candidate = candidate.copy()". Yes I did.
            # So "tfidf_score" in 'ranked' is essentialy the input 0.78
            # Let's check Ranker code.
            # "tfidf_score": 0.85 (input)
            # "normalized_scores": { "tfidf": 85.0 }
            # So I should return the raw input key "tfidf_score".
            # BUT Schema expects float.
            # Let's return raw input tfidf (0-1) as it's more standard.
            skill_match_percentage=ranked["skill_match_percentage"],
            experience_years=ranked["years_of_experience"],
            matched_skills=ranked["matched_skills"],
            missing_skills=ranked["missing_skills"],
            explanation=ranked["scoring_explanation"]
        ))
        
    processing_time = f"{round(time.time() - start_time, 2)}s"
    
    return BatchAnalysisResponse(
        ranked_candidates=final_output,
        processing_time=processing_time
    )

