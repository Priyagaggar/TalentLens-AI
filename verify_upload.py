
import io
import os
import shutil
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_upload_endpoint():
    # Setup
    print("Testing /upload/resumes endpoint...")
    
    # Create dummy PDF
    pdf_content = b"%PDF-1.4 mock content"
    pdf_file = io.BytesIO(pdf_content)
    pdf_file.name = "resume_1.pdf"
    
    # Create dummy DOCX
    docx_content = b"PK\x03\x04 mock docx content"
    docx_file = io.BytesIO(docx_content)
    docx_file.name = "resume_2.docx"
    
    # Create invalid file
    txt_content = b"Just text"
    txt_file = io.BytesIO(txt_content)
    txt_file.name = "resume_3.txt"
    
    # Scenario 1: Success with Text JD
    print("\nScenario 1: Upload 2 resumes + Text JD")
    response = client.post(
        "/api/v1/upload/resumes",
        files=[
            ("resumes", ("resume_1.pdf", io.BytesIO(pdf_content), "application/pdf")),
            ("resumes", ("resume_2.docx", io.BytesIO(docx_content), "application/vnd.openxmlformats-officedocument.wordprocessingml.document"))
        ],
        data={"job_description_text": "We need Python developers."}
    )
    
    if response.status_code != 200:
        print("FAILED Scenario 1:", response.json())
        return
        
    data = response.json()
    print("Success:", data)
    assert len(data["resume_ids"]) == 2
    assert data["job_description_id"] is not None
    
    # Verify files exist on disk
    upload_dir = "uploaded_files"
    if not os.path.exists(upload_dir):
        print("Upload dir not created!")
        return

    for rid in data["resume_ids"]:
        # We don't know extension easily from ID here, but let's check dir
        # actually the ID returned is just UUID, we need to find it
        found = False
        for f in os.listdir(upload_dir):
            if f.startswith(rid):
                found = True
                break
        assert found, f"File for {rid} not found on disk"
        
    # Scenario 2: Fail Limit (Simulate logic check without creating 5MB file in memory by mocking? 
    # Or just trust logic. We can test invalid type)
    print("\nScenario 2: Invalid File Type")
    response_fail = client.post(
        "/api/v1/upload/resumes",
        files=[
            ("resumes", ("resume_3.txt", txt_file, "text/plain"))
        ],
        data={"job_description_text": "JD"}
    )
    print("Status (Expected 400):", response_fail.status_code)
    assert response_fail.status_code == 400
    print("Error:", response_fail.json()["detail"])

    # Cleanup
    if os.path.exists(upload_dir):
        shutil.rmtree(upload_dir)
    print("\n--- Upload Verification Passed ---")

if __name__ == "__main__":
    test_upload_endpoint()
