# TalentLens AI 🚀

![Python](https://img.shields.io/badge/Python-3.11-3776ab?style=flat&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-009688?style=flat&logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-18-61dafb?style=flat&logo=react&logoColor=black)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Free_Tier-336791?style=flat&logo=postgresql&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=flat)
![Deployed on Render](https://img.shields.io/badge/Deployed_on-Render-46E3B7?style=flat&logo=render&logoColor=white)

> **An intelligent, automated resume screening system that uses NLP and Machine Learning to rank candidates against job descriptions, manage screening history, and automate recruiter outreach with professional email workflows.**

---

## 🌐 Live Demo

| Service | URL |
|---|---|
| 🖥️ **Frontend App** | [talentlens-frontend-t7go.onrender.com](https://talentlens-frontend-t7go.onrender.com) |
| 📡 **API Docs (Swagger)** | [ai-resume-screener-1qf8.onrender.com/docs](https://ai-resume-screener-1qf8.onrender.com/docs) |

> ⚠️ Hosted on Render's free tier. The backend may take **30–60 seconds** to wake up on first visit after inactivity.

---

## 🌟 Key Features

### 📄 Universal Resume Parsing
- Extracts text from **PDF**, **DOCX**, and **TXT** files
- Automatically parses candidate **email addresses**, **phone numbers**, and **names**
- Handles multi-column layouts, bullet points, and unicode characters

### 🧠 Multi-Layer NLP Scoring Pipeline
Each resume is scored against the job description using a **composite weighted index**:

| Component | Weight | Method |
|---|---|---|
| **Content Match** | 40% | Semantic similarity via HuggingFace Inference API (BERT `all-MiniLM-L6-v2`) with TF-IDF cosine fallback |
| **Skill Match** | 40% | FuzzyWuzzy fuzzy keyword matching against a structured skills taxonomy |
| **Experience** | 20% | Date regex extraction to compute total years of experience |

### 🎯 Intelligent Candidate Ranking
- Ranks all uploaded candidates by composite score in a single batch
- Custom **adjustable thresholds** for interview invite and rejection via UI sliders
- Returns structured per-candidate feedback explaining match results

### 🔐 JWT Authentication & Multi-Tenancy
- Secure recruiter registration and login with **bcrypt** password hashing
- **JWT bearer tokens** for all protected endpoints
- Strict recruiter isolation — recruiters can only access their own screenings and candidates

### 📧 Automated Email Workflows
- **Three-tier smart routing** based on candidate score:
  - ✅ **High score** → Congratulations + Interview invite
  - 🔄 **Mid score** → Application under review notice
  - ❌ **Low score** → Polite, professional rejection
- **Batch email dispatch** to multiple selected candidates in one click
- Rate-limit-aware delivery (1.5s delay between sends for Mailtrap sandbox compliance)
- Integrated with **Mailtrap SMTP sandbox** for safe, visual email testing
- Error-tolerant batching — returns per-candidate success/failure report

### 📊 History & Management Dashboard
- View all past screenings with timestamps (auto-converted to local timezone)
- Inspect original job descriptions and resume texts via modals
- Delete screenings with full cascade (removes all associated records)
- Clean job title display (strips markdown/formatting artifacts)

---

## 🏗️ Architecture

```
┌─────────────────────────────────┐
│        React Frontend           │
│  (Vite + TailwindCSS)           │
│  Drag-drop upload, Results UI,  │
│  History, Email config modals   │
└──────────────┬──────────────────┘
               │ HTTPS (Axios)
               ▼
┌─────────────────────────────────┐
│       FastAPI Backend           │
│  Auth, Routing, Validation,     │
│  SMTP Dispatch, CORS            │
└───┬───────────┬─────────────────┘
    │           │
    ▼           ▼
┌───────┐  ┌──────────────────────┐
│  DB   │  │   Processing Engine  │
│  PG/  │  │  ┌────────────────┐  │
│ SQLite│  │  │ PDF/DOCX Parser│  │
└───────┘  │  ├────────────────┤  │
           │  │ NLTK Processor │  │
           │  ├────────────────┤  │
           │  │ FuzzyWuzzy     │  │
           │  │ Skill Matcher  │  │
           │  ├────────────────┤  │
           │  │ HuggingFace    │  │
           │  │ Inference API  │  │
           │  │ (BERT / TF-IDF)│  │
           │  └────────────────┘  │
           └──────────────────────┘
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | React 18, Vite, TailwindCSS, Axios |
| **Backend** | Python 3.11, FastAPI, Uvicorn |
| **Auth** | JWT (`PyJWT`), bcrypt (`passlib`) |
| **NLP / AI** | NLTK, FuzzyWuzzy, scikit-learn (TF-IDF), HuggingFace Inference API (BERT) |
| **File Parsing** | pypdf, python-docx, pdfplumber |
| **Database** | PostgreSQL (production), SQLite (local development) |
| **ORM** | SQLAlchemy (async) |
| **Email** | SMTP via Mailtrap sandbox |
| **Deployment** | Render (Web Service + Static Site + PostgreSQL) |

---

## 🚀 Installation & Local Setup

### Prerequisites
- Python 3.11+
- Node.js 18+

### 1. Clone the repository
```bash
git clone https://github.com/Priyagaggar/TalentLens-AI.git
cd TalentLens-AI
```

### 2. Create your `.env` file
Create a `.env` file in the project root:
```ini
# Database (SQLite for local dev)
DATABASE_URL=sqlite+aiosqlite:///./sql_app.db

# JWT Auth
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# HuggingFace Inference API (free - get token at huggingface.co)
HF_API_TOKEN=hf_your_token_here

# Email SMTP - Mailtrap sandbox (get credentials at mailtrap.io)
SMTP_HOST=sandbox.smtp.mailtrap.io
SMTP_PORT=2525
SMTP_USER=your_mailtrap_smtp_user
SMTP_PASSWORD=your_mailtrap_smtp_password
SENDER_EMAIL=noreply@talentlens.ai
MOCK_EMAIL=false
```

> **Getting your free tokens:**
> - **HF_API_TOKEN**: Sign up at [huggingface.co](https://huggingface.co) → Settings → Access Tokens → New Token (Read)
> - **Mailtrap SMTP**: Sign up at [mailtrap.io](https://mailtrap.io) → Email Testing → Inboxes → SMTP Settings

### 3. Install & run
The project includes a launcher script (`run.bat`) that starts both servers concurrently on Windows:
```bash
# Install Python dependencies
pip install -r requirements.txt

# Install React dependencies
cd frontend
npm install
cd ..

# Start both servers
.\run.bat
```

| Service | URL |
|---|---|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8000 |
| Swagger Docs | http://localhost:8000/docs |

---

## 📡 API Endpoints

### Authentication
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/auth/register` | Create a new recruiter account |
| `POST` | `/api/v1/auth/login` | Login and receive a JWT token |

### Screening
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/upload/resumes` | Upload resume files (PDF/DOCX/TXT), returns UUIDs |
| `POST` | `/api/v1/analyze/batch` | Run NLP scoring pipeline and rank all candidates |

### History & Communications
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/history/jobs` | List all past screenings for the logged-in recruiter |
| `GET` | `/api/v1/history/jobs/{job_id}/results` | Get full ranking results for a screening |
| `DELETE` | `/api/v1/history/jobs/{job_id}` | Delete a screening and all its records |
| `POST` | `/api/v1/history/jobs/{job_id}/email` | Batch email selected candidates |

---

## 📁 Project Structure

```
TalentLens-AI/
├── app/
│   ├── api/
│   │   ├── auth.py              # JWT auth endpoints & token logic
│   │   └── endpoints.py         # All screening & history endpoints
│   ├── core/
│   │   ├── advanced_matcher.py  # HuggingFace API + TF-IDF similarity scoring
│   │   ├── skill_extractor.py   # FuzzyWuzzy skill extraction from resume text
│   │   ├── skill_matcher.py     # Skill comparison between resume and JD
│   │   ├── experience_extractor.py  # Date regex → years of experience
│   │   ├── text_processor.py    # NLTK cleaning & lemmatization
│   │   ├── ranker.py            # Composite score calculator & sorter
│   │   ├── pdf_extractor.py     # PDF text extraction
│   │   ├── docx_extractor.py    # DOCX text extraction
│   │   └── email_service.py     # SMTP email builder & dispatcher
│   ├── db/
│   │   ├── database.py          # SQLAlchemy async engine & CRUD helpers
│   │   └── models.py            # ORM models (User, Job, Resume, Ranking)
│   ├── config.py                # Pydantic settings (reads from .env)
│   ├── main.py                  # FastAPI app, CORS, lifespan
│   └── schemas.py               # Pydantic request/response schemas
├── frontend/                    # React + Vite application
│   ├── src/
│   │   ├── components/          # UI components (Upload, Results, History, Auth)
│   │   └── App.jsx              # Root component & routing
│   └── package.json
├── data/
│   └── skills_database.json     # Structured skills taxonomy for matching
├── scripts/
│   └── init_db.py               # Database initialisation script
├── requirements.txt             # Python dependencies
├── render.yaml                  # Render deployment configuration
├── run.bat                      # Windows local dev launcher
└── start.sh                     # Render startup script
```

---

## ⚙️ Deployment (Render)

This project is configured for one-click deployment on Render via `render.yaml`:

- **`ai-resume-screener`** — Python Web Service (FastAPI backend)
- **`talentlens-frontend`** — Static Site (React frontend built with Vite)
- **`resume-db`** — PostgreSQL database (free tier)

After deploying, set the following environment variables in the Render dashboard under the backend service:

| Key | Value |
|---|---|
| `HF_API_TOKEN` | Your HuggingFace access token |
| `SMTP_USER` | Your Mailtrap sandbox SMTP username |
| `SMTP_PASSWORD` | Your Mailtrap sandbox SMTP password |
| `MOCK_EMAIL` | `false` |
| `SECRET_KEY` | A strong random string for JWT signing |

---

## 🗺️ Roadmap

- [ ] Docker + Docker Compose support for one-command local setup
- [ ] Resume parsing improvements (multi-column PDF layouts)
- [ ] Export rankings to CSV/PDF
- [ ] Candidate pipeline stages (shortlisted, interviewed, offered)

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
