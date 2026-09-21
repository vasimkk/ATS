# ResuMatch ATS Studio 🎯
### AI & NLP-Powered Resume Optimizer & Job Description ATS Matcher

ResuMatch ATS Studio is a full-stack platform engineered to evaluate candidate resumes against target job descriptions, calculate accurate ATS match scores, detect missing keywords and technical competencies, and generate tailored, ATS-compliant resumes with STAR-method achievements and `.docx` / PDF export.

---

## 🌟 Key Features

1. **Multi-Factor ATS Compatibility Algorithm (0–100%)**:
   - **Hard Skills Match (35%)**: Exact and synonym matching against 1,000+ technical skills (languages, frameworks, cloud, databases, DevOps, AI/ML).
   - **Semantic Alignment (20%)**: TF-IDF & Cosine Similarity for vocabulary and contextual alignment.
   - **Structural ATS Readability (15%)**: Contact information detection, standard section header compliance, bullet point density, and length checks.
   - **Soft Skills & Core Competencies (15%)**: Leadership, agile practices, teamwork, and execution keywords.
   - **Experience & Seniority (15%)**: Extraction and alignment of years of experience and educational degree requirements.
2. **Interactive Keyword Gap Matrix**:
   - Filterable view of **Matched Keywords** (emerald) vs **Missing Keywords** (rose) categorized by domain.
3. **Smart Resume Tailoring Engine (Zero Static Data)**:
   - **Tailored Professional Summary**: Dynamically crafted for the target role using the candidate's actual years of experience.
   - **STAR-Method Bullet Points**: Generates quantifiable impact bullets (Situation, Task, Action, Result) embedding the missing keywords.
   - **Optimized Skills Matrix**: Reorganizes skills into standard ATS categories with missing skills cleanly integrated.
4. **Side-by-Side Diff & Interactive Live Editor**:
   - Compare original resume with the tailored version side-by-side with highlight indicators.
   - Tweak wording in the live editor and click **Re-Score ATS** to track real-time score improvements.
5. **Multiple Export Formats**:
   - Direct download as an ATS-standard Microsoft Word document (`.docx`).
   - One-click copy to clipboard.
   - Print or save as formatted ATS PDF.
6. **Multi-Format Document Parsing**:
   - Drag-and-drop or upload PDF (`pypdf`), Word documents (`.docx`), or plain text files.

---

## 🛠 Tech Stack

- **Backend**: Python 3.14, FastAPI, Uvicorn, Scikit-Learn, PyPDF, Python-Docx, Pydantic.
- **Frontend**: React 18, Vite, Vanilla CSS (Modern Dark Glassmorphism, HSL Design Tokens, Micro-animations), Lucide React.

---

## 🚀 Quickstart Guide

### 1. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Install dependencies
pip install -r requirements.txt

# Start FastAPI server
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```
API Documentation will be available at: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### 2. Frontend Setup

```bash
# In a new terminal, navigate to frontend
cd frontend

# Install dependencies
npm install

# Start Vite dev server
npm run dev
```
Open your browser at: [http://localhost:5173](http://localhost:5173)

---

## 📡 API Endpoints Reference

- `POST /api/parse-resume`: Multipart file upload for PDF, DOCX, and TXT documents.
- `POST /api/analyze-ats`: JSON payload `{ resume_text, job_description }` returning scores, keyword gap breakdown, and readability checks.
- `POST /api/optimize-resume`: JSON payload returning tailored summary, STAR bullet points, updated skills, and complete tailored resume.
- `POST /api/export-docx`: Generates a downloadable ATS-formatted `.docx` file.
- `GET /api/health`: Healthcheck endpoint.
