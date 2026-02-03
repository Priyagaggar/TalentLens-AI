
# TalentLens AI 🚀

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.11-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688.svg)
![React](https://img.shields.io/badge/React-18-61dafb.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ed.svg)

> **An intelligent, automated resume screening system that uses NLP and Machine Learning to rank candidates against job descriptions with human-readable explanations.**

---

## 🌟 Key Features

*   **📄 Universal Parsing**: Robustly extracts text from **PDF** and **DOCX** files, handling complex layouts and tables.
*   **🧠 Advanced NLP Pipeline**:
    *   **Entity Extraction**: Automatically identifies emails and phone numbers.
    *   **Skill Extraction**: Uses fuzzy matching against a database of 100+ technical skills.
    *   **Experience Calculation**: Smartly parses date ranges to compute total years of experience.
*   **🎯 Intelligent Ranking**:
    *   **TF-IDF Vectorization**: Measures semantic similarity between resumes and job descriptions.
    *   **Weighted Scoring**: Custom algorithm combining Content Match (40%), Skill Match (40%), and Experience (20%).
    *   **Explainable AI**: Generates human-readable feedback explaining *why* a candidate was ranked high or low.
*   **📊 Insightful Dashboard**:
    *   Modern **React** frontend with drag-and-drop uploads.
    *   Visual candidate cards with score breakdowns.
    *   Dynamic filtering by Score, Experience, and Skills.
    *   CSV Export for easy integration with HR tools.
*   **⚙️ Production Ready**:
    *   **Dockerized** for easy deployment.
    *   **Async** processing for high performance.
    *   **PostgreSQL** integration for data persistence.

---

## 🖼️ Demo

[![Live Demo](https://img.shields.io/badge/demo-live-green.svg?style=for-the-badge&logo=vercel)](https://talentlens-frontend-t7go.onrender.com)

**[Try the Live App Here](https://talentlens-frontend-t7go.onrender.com)**






---

## 🏗️ Architecture

### System Diagram
The system follows a modern client-server architecture:

1.  **Frontend (React/Vite)**: Handles file uploads and renders the results dashboard.
2.  **API Gateway (FastAPI)**: Manages endpoints, validation, and orchestrates the pipeline.
3.  **Processing Engine**:
    *   **Extractors**: Parsers for PDF/DOCX.
    *   **NLP Core**: SpaCy/NLTK for text cleaning and entity recognition.
    *   **Matchers**: TF-IDF (Scikit-Learn) and FuzzyWuzzy for scoring.
4.  **Database (PostgreSQL)**: Stores metadata, parsed text, and ranking results.

### Data Flow
1.  **Upload**: User uploads Resumes + JD via Frontend.
2.  **Ingest**: Backend saves files securely with UUIDs.
3.  **Parse**: Extractors convert binary files to clean text.
4.  **Analyze**: Text is tokenized; Skills and Experience are extracted.
5.  **Score**: Resumes are compared to the JD using vector similarity and set operations.
6.  **Rank**: Candidates are sorted by final weighted score.
7.  **Persist**: Results are saved to DB.
8.  **Present**: JSON response drives the Frontend Dashboard.

---

## 🚀 Installation & Setup

### Prerequisites
*   Python 3.10+
*   Node.js 16+
*   Docker & Docker Compose (optional but recommended)

### Option A: Docker (Recommended)
The easiest way to run the full stack (Backend + DB).

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/ai-resume-screener.git
cd ai-resume-screener

# 2. Build and Run
docker-compose up --build
```

Access the dashboard at `http://localhost:5173` (if frontend containerized) or API at `http://localhost:8000/docs`.

### Option B: Manual Setup

#### Backend
```bash
cd ai_resume_screener

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Download NLP models
python -m spacy download en_core_web_sm

# Init Database (SQLite default for local)
python scripts/init_db.py

# Run Server
uvicorn app.main:app --reload
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Environment Variables
Create a `.env` file (managed by `app/config.py`):
```ini
PROJECT_NAME="TalentLens AI"
BACKEND_CORS_ORIGINS=["http://localhost:5173"]
DATABASE_URL="sqlite+aiosqlite:///./resume_screener.db" # or postgresql://...
```

---

## 📡 Usage

### API Endpoints

#### 1. Batch Analyze (Core Workflow)
Performs full extraction, matching, and ranking.

```bash
curl -X POST "http://localhost:8000/api/v1/analyze/batch" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "job_description_file=@jd.txt" \
  -F "resume_files=@candidate1.pdf" \
  -F "resume_files=@candidate2.docx"
```

**Response Sample:**
```json
{
  "job_description": "Senior Python Developer...",
  "ranked_candidates": [
    {
      "rank": 1,
      "name": "Alice Smith",
      "final_score": 92.5,
      "skill_match_percentage": 85,
      "experience_years": 5,
      "matched_skills": ["Python", "FastAPI", "Docker"],
      "missing_skills": ["Kubernetes"],
      "explanation": "Strong candidate with 85% skill match..."
    }
  ]
}
```

---

## 📂 Project Structure

```
ai_resume_screener/
├── app/
│   ├── api/            # Route handlers (endpoints)
│   ├── core/           # Core Logic (NLP, Extraction, Scoring)
│   │   ├── pdf_extractor.py
│   │   ├── resume_matcher.py
│   │   ├── skill_extractor.py
│   │   └── ...
│   ├── db/             # Database Models & Session
│   └── schemas.py      # Pydantic Data Models
├── frontend/           # React Application
│   ├── src/
│   │   ├── components/ # UI Components (Uploader, Dashboard)
│   │   └── ...
├── tests/              # Pytest Suite
├── data/               # Skill databases & fixtures
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

---

## 💡 Technical Highlights

### 🧠 NLP & Machine Learning
*   **TF-IDF (Term Frequency-Inverse Document Frequency)**: Used to convert text into numerical vectors. This allows us to measure cosine similarity between the Job Description and Resume content effectively, capturing context beyond simple keyword matching.
*   **Named Entity Recognition (NER)**: SpaCy is utilized for robust tokenization and identifying custom entities.
*   **Fuzzy Matching**: `fuzzywuzzy` ensures that "React.js" and "ReactJS" are treated as the same skill, improving accuracy significantly.

### 🛡️ Design Decisions
*   **FastAPI**: Chosen for its high performance (Starlette), native Async support (essential for I/O heavy parsing), and automatic OpenAPI documentation.
*   **React + Tailwind**: Ensures a lightweight, responsive, and highly customizable frontend without the bloat of heavy component libraries.
*   **Strategy Pattern**: Extractors (`pdf_extractor`, `docx_extractor`) are designed to be modular. Adding support for `.txt` or `.md` files would require minimal changes.

---

## 🔮 Future Enhancements

*   [ ] **LLM Integration**: Use OpenAI/Gemini for deeper qualitative analysis and summary generation.
*   [ ] **User Accounts**: Multi-tenancy for different recruiters.
*   [ ] **Email Integration**: Auto-email top candidates directly from the dashboard.
*   [ ] **OCR Support**: Processing scanned image-based PDFs.

---

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
