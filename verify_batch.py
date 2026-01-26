
import io
import os
import shutil
import time
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_batch_flow():
    print("Testing Full Batch Flow (Upload -> Analyze/Batch)...")
    
    # Setup Files
    # 1. Valid PDF with content
    pdf_content = b"%PDF-1.4 mock content" # Mock
    pdf_file = io.BytesIO(pdf_content)
    pdf_file.name = "resume_A.pdf"
    
    # 2. Valid DOCX with content
    docx_content = b"PK\x03\x04 mock docx" # Mock
    docx_file = io.BytesIO(docx_content)
    docx_file.name = "resume_B.docx"
    
    # Mocking Extraction at module level is hard with TestClient unless we mock the imports in app.api.endpoints
    # We can use unittest.mock.patch
    # However, verify_api used patch correctly. Here we are outside a class.
    # Let's define a class or use 'with patch'
    
    from unittest.mock import patch
    
    # We need to mock ALL extractors used
    with patch("app.api.endpoints.extract_text_from_pdf") as mock_pdf, \
         patch("app.api.endpoints.extract_text_from_docx") as mock_docx:
         
        # Mock Return Values
        mock_pdf.return_value = """
        Alice
        Email: alice@example.com
        Skills: Python, AWS, Docker.
        Experience: 5 years dev.
        """
        mock_docx.return_value = """
        Bob
        Email: bob@example.com
        Skills: Java, Spring.
        Experience: 2 years.
        """
        
        # 1. Upload
        print("\nStep 1: Uploading Resumes...")
        upload_resp = client.post(
            "/api/v1/upload/resumes",
            files=[
                ("resumes", ("resume_A.pdf", io.BytesIO(pdf_content), "application/pdf")),
                ("resumes", ("resume_B.docx", io.BytesIO(docx_content), "application/vnd.openxmlformats-officedocument.wordprocessingml.document"))
            ],
            data={"job_description_text": "Looking for Python AWS Docker developer."}
        )
        assert upload_resp.status_code == 200
        upload_data = upload_resp.json()
        jd_id = upload_data["job_description_id"]
        resume_ids = upload_data["resume_ids"]
        print(f"Uploaded. JD ID: {jd_id}, Resume IDs: {resume_ids}")
        
        # 2. Batch Analyze
        print("\nStep 2: Batch Analysis...")
        batch_req = {
            "job_description_id": jd_id,
            "resume_ids": resume_ids
        }
        
        # Wait a bit to simulate processing time if needed, though mocking is fast
        start = time.time()
        analyze_resp = client.post("/api/v1/analyze/batch", json=batch_req)
        
        if analyze_resp.status_code != 200:
            print("Analyze Failed:", analyze_resp.json())
            return
            
        result = analyze_resp.json()
        print("Analysis Success. Processing Time:", result["processing_time"])
        
        # Verify Ranking
        ranked = result["ranked_candidates"]
        assert len(ranked) == 2
        
        # Alice (Python/AWS/Docker) should be higher than Bob (Java) for Python JD
        top_candidate = ranked[0]
        print(f"Top Candidate: {top_candidate['name']} with Score {top_candidate['final_score']}")
        print(f"Explanation: {top_candidate['explanation']}")
        
        # Check name extraction logic (from email)
        # Alice@example.com -> Alice
        # Bob@example.com -> Bob
        names = [c["name"] for c in ranked]
        assert "alice" in names[0].lower() or "alice" in names[1].lower()
        
        # Check scores
        # Alice should have matched skills
        alice = next(c for c in ranked if "alice" in c["name"].lower())
        assert "Python" in alice["matched_skills"]
        
    # Cleanup
    shutil.rmtree("uploaded_files")
    print("\n--- Batch Flow Verified ---")

if __name__ == "__main__":
    test_batch_flow()
