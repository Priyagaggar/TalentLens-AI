# TalentLens AI 🚀

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.10-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688.svg)
![React](https://img.shields.io/badge/React-18-61dafb.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ed.svg)

> **An intelligent, automated resume screening system that uses NLP and Machine Learning to rank candidates against job descriptions, manage history, and automate recruiter outreach with styled email templates.**

---

## 🌟 Key Features

*   **📄 Universal Parsing**: Robustly extracts text from **PDF**, **DOCX**, and **TXT** files, parsing candidate info in-memory.
*   **🧠 Advanced NLP Pipeline**:
    *   **Entity Extraction**: Identifies emails, phone numbers, and names.
    *   **Skill Extraction**: Employs fuzzy keyword matching against a predefined skills taxonomy.
    *   **Experience Calculation**: Computes total years of experience using date regex patterns.
*   **🎯 Intelligent Ranking**:
    *   **Semantic Matching**: Uses SentenceTransformer BERT embeddings (`all-MiniLM-L6-v2`) to measure textual similarity between resumes and JDs.
    *   **Weighted Scoring**: Custom composite index combining Content Match (40%), Skill Match (40%), and Experience (20%).
    *   **Explainable AI**: Returns structured feedback explaining candidate matches.
*   **🔐 Auth & Multi-Tenancy**:
    *   **JWT Security**: Register and login securely using encrypted passwords (`bcrypt`).
    *   **Recruiter Isolation**: Multi-tenant database architecture. Recruiters can only access, delete, and email candidates from screenings they own.
*   **📧 Automated Email Workflows**:
    *   **Three-Tier Routing**: Tailors communication dynamically based on candidate score. Top matches get an **Interview Invitation** (with CTA booking links), middling candidates get a **Keep-in-Touch holding notice**, and low scorers get a **Polite Rejection**.
    *   **Dynamic Thresholds**: Select candidates and adjust Invite/Rejection scores using sliding controllers on the UI before sending.
    *   **Error-Tolerant Batching**: Performs batch sends with a try-except layer, returning a detailed success/failure report instead of failing the batch.
    *   **Developer Sandbox**: Integrates with **Mailtrap** SMTP for testing, with a local **HTML Mock Logger** (`mock_emails.html`) to visually preview templates locally behind corporate firewalls.
*   **📊 History & Management**:
    *   Dynamic history dashboard with auto-conversion to user's local timezone.
    *   Clean job title parser that strips markdown tags to keep the history list neat.
    *   Screening deletion (cascades database records to clean up unused resumes/results).
    *   Modal triggers to inspect original Job Description and Resume texts directly.

---

## 🏗️ Architecture

### System Diagram
The system follows a modern client-server architecture:

1.  **Frontend (React/Vite)**: Renders the drag-and-drop uploader, history lists, email configuration modals, and results cards.
2.  **API Gateway (FastAPI)**: Manages authentication, endpoint routing, schemas validation, and SMTP dispatches.
3.  **Processing Engine**:
    *   **Extractors**: Parsers for PDF, DOCX, and TXT.
    *   **Advanced Scorer**: SentenceTransformer lazy-loader that batches and calculates cosine similarities.
4.  **Database (SQLite/PostgreSQL)**: Persists registered users, job descriptions, resumes, and evaluation results.

---

## 🚀 Installation & Setup

### Prerequisites
*   Python 3.10+
*   Node.js 16+
*   Docker & Docker Compose (optional)

### Environment Variables
Create a `.env` file in the root folder of your project:
```ini
PROJECT_NAME="TalentLens AI"
DATABASE_URL="sqlite+aiosqlite:///./sql_app.db"

# JWT Auth Settings
SECRET_KEY="your-secret-key-change-in-prod"
ALGORITHM="HS256"

# Email SMTP Settings (Mailtrap sandbox example)
SMTP_HOST="sandbox.smtp.mailtrap.io"
SMTP_PORT=2525
SMTP_USER="your_mailtrap_smtp_user"
SMTP_PASSWORD="your_mailtrap_smtp_password"
SENDER_EMAIL="noreply@talentlens.ai"

# Developer Mock Mode (Bypasses network blocks/firewalls and outputs mock HTML logs)
MOCK_EMAIL=true
```

### Installation
The project includes a launcher script (`run.bat`) for Windows users to spin up both servers concurrently.
```bash
# 1. Install Python dependencies
pip install -r requirements.txt

# 2. Install React frontend dependencies
cd frontend
npm install
cd ..

# 3. Start the application
.\run.bat
```
- Access the **Frontend** at `http://localhost:5173`
- Access the **API documentation** at `http://localhost:8000/docs`

---

## 📡 Core API Endpoints

### 1. Authentication
*   `POST /api/v1/auth/register`: Create a new recruiter account.
*   `POST /api/v1/auth/login`: Exchange credentials for a JWT bearer token.

### 2. Screening
*   `POST /api/v1/upload/resumes`: Upload files and get temporary storage UUIDs.
*   `POST /api/v1/analyze/batch`: Run NLP extraction, BERT cosine comparisons, and save results.

### 3. History & Communications
*   `GET /api/v1/history/jobs`: Retrieve list of past job screenings.
*   `GET /api/v1/history/jobs/{job_id}/results`: Retrieve candidate rankings, job description content, and resume texts.
*   `DELETE /api/v1/history/jobs/{job_id}`: Delete a past job screening and all its records.
*   `POST /api/v1/history/jobs/{job_id}/email`: Trigger batch emails to selected candidates with HTML templates.

---

## 🛠️ Project Structure

```
TalentLens-AI/
├── app/
│   ├── api/            # Router endpoints (auth, screenings)
│   ├── core/           # Text processing, BERT scoring, SMTP mailer
│   │   ├── advanced_matcher.py
│   │   ├── email_service.py
│   │   └── ...
│   ├── db/             # SQLAlchemy schemas & CRUD operations
│   └── schemas.py      # Pydantic models
├── frontend/           # React Application
│   ├── src/
│   │   ├── components/ # ResultsDashboard, HistoryList, Auth views
│   │   └── ...
├── tests/              # Test suite (pytest)
├── requirements.txt    # Python requirements
└── run.bat             # Batch launcher script
```

---

## 📄 License
This project is licensed under the MIT License.
