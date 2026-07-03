
import os
import shutil
import logging
from typing import List

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from app.api.auth import get_current_user
from app.db.models import User

from app.schemas import ResumeAnalysisResponse, ErrorResponse, UploadResponse, BatchAnalysisRequest, BatchAnalysisResponse, RankedCandidate, BatchEmailRequest
from app.core.pdf_extractor import extract_text_from_pdf
from app.core.docx_extractor import extract_text_from_docx
from app.core.text_processor import TextProcessor
from app.core.skill_extractor import SkillExtractor
from app.core.experience_extractor import extract_experience, extract_required_experience_from_jd

from app.core.advanced_matcher import AdvancedMatcher
from app.core.skill_matcher import SkillMatcher
from app.core.ranker import Ranker
from app.db.database import (
    save_job_description,
    save_resume,
    save_ranking_result,
    get_all_job_descriptions,
    get_job_description,
    get_rankings_for_job,
    get_resume,
    delete_job_description,
    update_resume_text
)

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
    
    if extension not in ["pdf", "docx", "txt"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file format. Only PDF, DOCX, and TXT are supported."
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
            elif extension == "txt":
                with open(temp_path, "r", encoding="utf-8") as f:
                    content_text = f.read()
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
        
        # 9. Semantic Matching (BERT)
        matcher = AdvancedMatcher()
        bert_score = matcher.batch_compare([content_text], job_description)[0]
        
        # 10. Final Scoring (Using Ranker Logic)
        # Construct a candidate object for the ranker
        candidate_data = {
            "name": filename, # Using filename as fallback for name
            "bert_score": bert_score,
            "skill_match_percentage": skill_match_result["match_percentage"],
            "years_of_experience": years_exp
        }
        
        # Ranker expects a list, returns a list
        jd_req_exp = extract_required_experience_from_jd(job_description)
        ranked_result = ranker.rank_candidates([candidate_data], required_experience=jd_req_exp)[0]
        
        # 11. cleanup and response
        response_data = ResumeAnalysisResponse(
            filename=filename,
            emails=processed_data.get("emails", []),
            phones=processed_data.get("phone_numbers", []),
            years_of_experience=years_exp,
            extracted_skills=resume_skills_dict,
            tfidf_similarity=bert_score, # Keeping field name for schema compatibility
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
async def upload_resumes_and_jd(
    resumes: List[UploadFile] = File(...),
    job_description_file: UploadFile = File(None),
    job_description_text: str = Form(None),
    current_user: User = Depends(get_current_user)
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
        await save_job_description({
            "id": jd_id, 
            "content": jd_content,
            "user_id": current_user.id
        })
            
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
            await save_job_description({"id": jd_id, "content": f"File: {job_description_file.filename}", "user_id": current_user.id})
        except Exception as e:
             raise HTTPException(status_code=500, detail=f"Failed to save JD: {str(e)}")
    else:
        raise HTTPException(status_code=400, detail="Job description is required (text or file).")

    # 2. Handle Resumes
    resume_ids = []
    
    for resume in resumes:
        # Validate Extension
        ext = resume.filename.split(".")[-1].lower()
        if ext not in ["pdf", "docx", "txt"]:
            # We could skip or raise error. Raising error is safer for now.
            raise HTTPException(status_code=400, detail=f"Invalid resume file type: {resume.filename}. Only PDF/DOCX/TXT allowed.")
        
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
                
            await save_resume({
                "id": res_id,
                "filename": resume.filename,
                "file_path": save_path,
                "user_id": current_user.id
            })
                
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
async def analyze_batch(request: BatchAnalysisRequest, current_user: User = Depends(get_current_user)):
    """
    Analyzes multiple resumes against a job description.
    Files must have been previously uploaded to get IDs.
    """
    # 1. Fetch JD
    jd_record = await get_job_description(request.job_description_id, current_user.id)
    if not jd_record:
        raise HTTPException(status_code=404, detail="Job Description not found or unauthorized.")
        
    start_time = time.time()
    UPLOAD_DIR = "uploaded_files"
    
    # Resolve Job Description File
    jd_id = request.job_description_id
    jd_text = jd_record.content
    
    # If the record is just a reference to a file (simplified implementation)
    if jd_text.startswith("File: "):
        filename = jd_text.replace("File: ", "")
        for ext in ["txt", "pdf", "docx"]:
            path = os.path.join(UPLOAD_DIR, f"{jd_id}.{ext}")
            if os.path.exists(path):
                if ext == "txt":
                    with open(path, "r", encoding="utf-8") as f:
                        jd_text = f.read()
                elif ext == "pdf":
                    jd_text = extract_text_from_pdf(path)
                elif ext == "docx":
                    jd_text = extract_text_from_docx(path)
                break

    if not jd_text.strip():
        raise HTTPException(status_code=400, detail="Job Description text is empty.")

    # 2. Process Resumes Loop
    candidates_data = [] # For Ranking
    resume_texts = []
    resume_details = []
    
    # Get JD skills once
    jd_skills_dict = skill_extractor.extract_skills(jd_text)
    jd_flat_skills = []
    for cat_skills in jd_skills_dict.values():
        jd_flat_skills.extend(cat_skills)

    # Extract Required Experience from JD
    jd_req_exp = extract_required_experience_from_jd(jd_text)

    for resume_id in request.resume_ids:
        r_record = await get_resume(resume_id, current_user.id)
        if not r_record:
            continue
            
        res_path = r_record.file_path
        
        if not os.path.exists(res_path):
            logger.warning(f"Resume {resume_id} not found, skipping.")
            continue
            
        try:
            # Extract Text
            content_text = ""
            if res_path.endswith(".pdf"):
                content_text = extract_text_from_pdf(res_path)
            elif res_path.endswith(".docx"):
                content_text = extract_text_from_docx(res_path)
            elif res_path.endswith(".txt"):
                with open(res_path, "r", encoding="utf-8") as f:
                    content_text = f.read()
                
            if not content_text:
                continue

            # Save extracted text to DB
            await update_resume_text(resume_id, content_text)

            resume_texts.append(content_text)
            resume_details.append({
                "resume_id": resume_id,
                "content_text": content_text
            })
            
        except Exception as e:
            logger.error(f"Error extracting resume {resume_id}: {e}")
            continue

    # Batch compute BERT scores
    advanced_matcher = AdvancedMatcher()
    bert_scores = advanced_matcher.batch_compare(resume_texts, jd_text)
    
    for i, details in enumerate(resume_details):
        content_text = details["content_text"]
        resume_id = details["resume_id"]
        
        try:
            # NLP Extraction
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
            
            skill_matcher_inst = SkillMatcher()
            skill_result = skill_matcher_inst.match_skills(resume_flat_skills, jd_flat_skills)
            
            # Collect data for Ranker
            cand_obj = {
                "resume_id": resume_id,
                "name": name,
                "bert_score": bert_scores[i],
                "skill_match_percentage": skill_result["match_percentage"],
                "years_of_experience": years_exp,
                "matched_skills": skill_result["matched_skills"],
                "missing_skills": skill_result["missing_skills"],
                "resume_text": content_text
            }
            candidates_data.append(cand_obj)
            
        except Exception as e:
            logger.error(f"Error processing resume {resume_id}: {e}")
            continue

    # 3. Rank
    ranked_list = ranker.rank_candidates(candidates_data, required_experience=jd_req_exp)
    
    # 4. Construct Response
    final_output = []
    for ranked in ranked_list:
        final_output.append(RankedCandidate(
            resume_id=ranked["resume_id"],
            name=ranked["name"],
            final_score=ranked["final_score"],
            tfidf_score=ranked["normalized_scores"]["bert"], 
            skill_match_percentage=ranked["skill_match_percentage"],
            experience_years=ranked["years_of_experience"],
            matched_skills=ranked["matched_skills"],
            missing_skills=ranked["missing_skills"],
            explanation=ranked["scoring_explanation"],
            resume_text=ranked.get("resume_text", "")
        ))
        
        # Save to DB
        await save_ranking_result({
            "job_description_id": jd_id,
            "resume_id": ranked["resume_id"],
            "total_score": ranked["final_score"],
            "details": {
                "skill_match": ranked["skill_match_percentage"],
                "experience": ranked["years_of_experience"],
                "matched_skills": ranked["matched_skills"],
                "missing_skills": ranked["missing_skills"],
                "explanation": ranked["scoring_explanation"]
            }
        })
        
    processing_time = f"{round(time.time() - start_time, 2)}s"
    
    return BatchAnalysisResponse(
        ranked_candidates=final_output,
        processing_time=processing_time,
        job_description_content=jd_record.content,
        job_description_id=jd_id
    )

def get_clean_title(content: str) -> str:
    lines = [line.strip() for line in content.split('\n') if line.strip()]
    if not lines:
        return "Untitled Job Description"
    first_line = lines[0]
    for char in ['#', '*', '_', '`']:
        first_line = first_line.replace(char, '')
    first_line = first_line.strip()
    return first_line[:80] + "..." if len(first_line) > 80 else first_line

@router.get("/history/jobs")
async def get_jobs_history(current_user: User = Depends(get_current_user)):
    """Returns a list of all past job runs."""
    jobs = await get_all_job_descriptions(current_user.id)
    result = []
    for j in jobs:
        result.append({
            "id": j.id,
            "title": get_clean_title(j.content),
            "created_at": j.created_at.isoformat() + "Z"
        })
    return result

@router.get("/history/jobs/{job_id}/results")
async def get_job_results_history(job_id: str, current_user: User = Depends(get_current_user)):
    """Returns the ranking results for a specific job."""
    
    # Verify user owns the job
    job = await get_job_description(job_id, current_user.id)
    if not job:
        raise HTTPException(status_code=404, detail="Job description not found.")
        
    rankings = await get_rankings_for_job(job_id)
    if not rankings:
        raise HTTPException(status_code=404, detail="No results found for this job.")
        
    final_output = []
    for r in rankings:
        resume = await get_resume(r.resume_id, current_user.id)
        name = resume.filename if resume else f"Unknown-{r.resume_id[:4]}"
        details = r.details or {}
        
        final_output.append({
            "resume_id": r.resume_id,
            "name": name,
            "final_score": r.total_score,
            "tfidf_score": details.get("bert", details.get("tfidf", 0.0)),
            "skill_match_percentage": details.get("skill_match", 0.0),
            "experience_years": details.get("experience", 0.0),
            "matched_skills": details.get("matched_skills", []),
            "missing_skills": details.get("missing_skills", []),
            "explanation": details.get("explanation", ""),
            "resume_text": resume.extracted_text if resume else ""
        })
        
    return {
        "job_description_content": job.content,
        "job_description_id": job_id,
        "ranked_candidates": final_output,
        "processing_time": "0.0s (Loaded from History)"
    }

@router.delete("/history/jobs/{job_id}")
async def delete_job_history(job_id: str, current_user: User = Depends(get_current_user)):
    """Deletes a job and its associated results and resumes."""
    job = await get_job_description(job_id, current_user.id)
    if not job:
        raise HTTPException(status_code=404, detail="Job description not found.")
        
    await delete_job_description(job_id, current_user.id)
    return {"message": "Job screening history successfully deleted."}

@router.post("/history/jobs/{job_id}/email")
async def email_candidates(
    job_id: str,
    payload: BatchEmailRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Emails the selected candidates based on match thresholds, 
    with robust error handling, security checks, and HTML layouts.
    """
    # 1. Ownership validation
    job = await get_job_description(job_id, current_user.id)
    if not job:
        raise HTTPException(status_code=404, detail="Job description not found.")
        
    # 2. Path parameter cross-check validation:
    # Ensure all candidate IDs belong to this job description.
    rankings = await get_rankings_for_job(job_id)
    job_resume_ids = {r.resume_id for r in rankings}
    
    # Filter the request list to only include candidate IDs that actually belong to this job
    valid_candidate_ids = [c_id for c_id in payload.candidate_ids if c_id in job_resume_ids]
    
    if not valid_candidate_ids:
        raise HTTPException(
            status_code=400, 
            detail="No valid candidate IDs found belonging to this screening."
        )
        
    # Build a mapping of resume_id -> ranking_result
    ranking_map = {r.resume_id: r for r in rankings}
    
    successful_count = 0
    failed_count = 0
    failures = []
    
    from app.core.email_service import send_candidate_email
    
    # 3. Batch Email Dispatch Loop with try-except
    for resume_id in valid_candidate_ids:
        name = None
        email = None
        try:
            resume = await get_resume(resume_id, current_user.id)
            if not resume:
                raise Exception("Resume record not found.")
                
            # Extract email address
            parsed_data = resume.parsed_data or {}
            if "emails" in parsed_data and parsed_data["emails"]:
                email = parsed_data["emails"][0]
            else:
                # Fallback parser if not pre-stored in parsed_data
                from app.core.text_processor import TextProcessor
                tp = TextProcessor()
                prep = tp.preprocess(resume.extracted_text or "")
                if prep.get("emails"):
                    email = prep["emails"][0]
                    
            if not email:
                raise Exception("No email address could be found in the candidate resume.")
                
            # Extract name
            if "name" in parsed_data and parsed_data["name"]:
                name = parsed_data["name"]
            else:
                name = email.split("@")[0] if email else f"Candidate-{resume_id[:4]}"
                
            score = ranking_map[resume_id].total_score
            
            # Send email
            send_candidate_email(
                to_email=email,
                candidate_name=name,
                score=score,
                interview_threshold=payload.interview_threshold,
                rejection_threshold=payload.rejection_threshold
            )
            successful_count += 1
            
        except Exception as e:
            failed_count += 1
            failures.append({
                "candidate_id": resume_id,
                "name": name if name else "Unknown Candidate",
                "email": email if email else "Unknown Email",
                "reason": str(e)
            })
            
    return {
        "successful_count": successful_count,
        "failed_count": failed_count,
        "failures": failures
    }

