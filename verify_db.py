
import asyncio
import uuid
from app.db.database import init_db, save_job_description, save_resume, save_ranking_result, get_job_description, get_resume, get_rankings_for_job, delete_old_records

async def verify_database():
    print("Testing Database Persistence...")
    
    # 1. Init
    await init_db()
    
    # 2. Save JD
    jd_id = str(uuid.uuid4())
    await save_job_description({
        "id": jd_id,
        "content": "Python Developer needed."
    })
    print(f"Saved JD: {jd_id}")
    
    # 3. Save Resume
    res_id = str(uuid.uuid4())
    await save_resume({
        "id": res_id,
        "filename": "john_doe.pdf",
        "file_path": "/tmp/john_doe.pdf",
        "extracted_text": "John Doe Python Dev",
        "parsed_data": {"email": "john@example.com", "skills": ["Python"]}
    })
    print(f"Saved Resume: {res_id}")
    
    # 4. Save Ranking
    await save_ranking_result({
        "job_description_id": jd_id,
        "resume_id": res_id,
        "total_score": 88.5,
        "details": {"tfidf": 0.8, "skills": 90}
    })
    print("Saved Ranking Result.")
    
    # 5. Retrieve
    jd = await get_job_description(jd_id)
    assert jd.content == "Python Developer needed."
    print("Verified JD Retrieval.")
    
    res = await get_resume(res_id)
    assert res.parsed_data["email"] == "john@example.com"
    print("Verified Resume Retrieval.")
    
    rankings = await get_rankings_for_job(jd_id)
    assert len(rankings) == 1
    assert rankings[0].total_score == 88.5
    print("Verified Ranking Retrieval.")
    
    # 6. Delete Old (Should not delete our just-created records as they are new)
    await delete_old_records(30)
    remaining_jd = await get_job_description(jd_id)
    assert remaining_jd is not None
    print("Deletion Logic Checked (Records preserved).")
    
    print("\n--- Database Verification Passed ---")

if __name__ == "__main__":
    asyncio.run(verify_database())
