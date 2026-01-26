
import io
import unittest
from unittest.mock import patch, MagicMock

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class TestAPI(unittest.TestCase):
    def test_health_check(self):
        response = client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    @patch("app.api.endpoints.extract_text_from_pdf")
    def test_analyze_endpoint(self, mock_extract):
        # Mock extracted text to simulate a real resume
        mock_extract.return_value = """
        John Doe
        Email: john.doe@example.com
        Experience: 5 years of Python development.
        Skills: Python, FastAPI, Docker.
        """
        
        # Create a dummy PDF file (content doesn't matter as we mock extraction)
        pdf_content = b"%PDF-1.4 mock content"
        pdf_file = io.BytesIO(pdf_content)
        pdf_file.name = "resume.pdf"
        
        job_description = "We need a Python developer with FastAPI and Docker skills."
        
        response = client.post(
            "/api/v1/analyze",
            files={"resume_file": ("resume.pdf", pdf_file, "application/pdf")},
            data={"job_description": job_description}
        )
        
        print("\nAPI Response Status:", response.status_code)
        
        if response.status_code != 200:
            print("Response Error:", response.json())
            
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        print("Analyzed Data Keys:", data.keys())
        
        # specific assertions
        self.assertEqual(data["filename"], "resume.pdf")
        self.assertIn("john.doe@example.com", data["emails"])
        self.assertEqual(data["years_of_experience"], 5.0)
        self.assertTrue(data["tfidf_similarity"] > 0)
        self.assertIn("Python", data["skill_match_details"]["matched_skills"])
        
        print("\n--- Test Passed Successfully ---")

if __name__ == "__main__":
    unittest.main()
