
# API Documentation

**Base URL**: `http://localhost:8000` (Local) / `https://your-app.onrender.com` (Production)

## Overview
The TalentLens AI API allows you to upload resumes and job descriptions to perform automated screening, ranking, and detailed analysis using NLP.

### Common Error Codes
- `400 Bad Request`: Invalid file format or missing data.
- `404 Not Found`: Referenced Job Description or Resume ID not found.
- `422 Validation Error`: JSON body did not match schema.
- `500 Internal Server Error`: Server-side processing failure.

---

## Endpoints

### 1. Upload Resumes
Uploads multiple resumes and a Job Description (JD) to the staging area.

- **URL**: `/api/v1/upload/resumes`
- **Method**: `POST`
- **Content-Type**: `multipart/form-data`

#### Request Parameters
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `resumes` | `List[File]` | Yes | List of resume files (`.pdf`, `.docx`). Max 5MB each. |
| `job_description_file` | `File` | Optional | Job Description file (`.txt`, `.pdf`, `.docx`). |
| `job_description_text` | `String` | Optional | Raw text of the Job Description. |
> **Note**: You must provide either `job_description_file` OR `job_description_text`.

#### Example Request (Curl)
```bash
curl -X POST "http://localhost:8000/api/v1/upload/resumes" \
  -F "resumes=@alice_resume.pdf" \
  -F "resumes=@bob_resume.docx" \
  -F "job_description_text=Looking for a Senior Python Developer with FastAPI experience."
```

#### Success Response (200 OK)
```json
{
  "job_description_id": "a1b2c3d4-...",
  "resume_ids": [
    "e5f6g7h8-...",
    "i9j0k1l2-..."
  ],
  "message": "Files uploaded successfully"
}
```

---

### 2. Batch Analyze
Triggers the full NLP analysis pipeline for a set of uploaded resumes against a specific Job Description.

- **URL**: `/api/v1/analyze/batch`
- **Method**: `POST`
- **Content-Type**: `application/json`

#### Request Body
```json
{
  "job_description_id": "String (UUID)",
  "resume_ids": ["String (UUID)", "String (UUID)"]
}
```

#### Example Request (Curl)
```bash
curl -X POST "http://localhost:8000/api/v1/analyze/batch" \
  -H "Content-Type: application/json" \
  -d '{
    "job_description_id": "a1b2c3d4-...",
    "resume_ids": ["e5f6g7h8-...", "i9j0k1l2-..."]
  }'
```

#### Success Response (200 OK)
```json
{
  "processing_time": "1.2s",
  "ranked_candidates": [
    {
      "resume_id": "e5f6g7h8-...",
      "name": "Alice Candidate",
      "final_score": 92.5,
      "skill_match_percentage": 85,
      "experience_years": 5,
      "matched_skills": ["Python", "FastAPI", "Docker"],
      "missing_skills": ["Kubernetes"],
      "explanation": "Top Tier Candidate. Strong match (85%) with skills: Python, Docker..."
    },
    {
       "resume_id": "i9j0k1l2-...",
       "name": "Bob Candidate",
       "final_score": 45.0,
       ...
    }
  ]
}
```

---

### 3. Single Resume Analysis
Directly analyzes a single file against a text JD without separate upload step (stateless).

- **URL**: `/api/v1/analyze`
- **Method**: `POST`
- **Content-Type**: `multipart/form-data`

#### Request Parameters
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `resume_file` | `File` | Yes | Single resume file (`.pdf`, `.docx`). |
| `job_description` | `String` | Yes | Raw text of the Job Description. |

#### Example CUrl
```bash
curl -X POST "http://localhost:8000/api/v1/analyze" \
  -F "resume_file=@my_resume.pdf" \
  -F "job_description=Python developer needed."
```

#### Success Response (200 OK)
Returns detailed analysis for the single candidate (similar structure to `ranked_candidates` item above, plus extracted email/phone entities).

---

### 4. Health Check
Checks if the API is running.

- **URL**: `/health`
- **Method**: `GET`

#### Response
```json
{
  "status": "ok"
}
```
