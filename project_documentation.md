# ResuMatch ATS Studio: Complete Project Documentation

Welcome to the comprehensive documentation for the **ResuMatch ATS Studio**. This document provides an in-depth look at the architecture, core modules, frontend interface, and setup instructions for the entire project.

---

## 1. Project Overview

ResuMatch ATS Studio is a full-stack web application designed to help job seekers optimize their resumes for Applicant Tracking Systems (ATS). It uses Natural Language Processing (NLP), mathematical vector embeddings, and rule-based algorithms to evaluate a candidate's resume against a target Job Description (JD). 

The application scores the resume, identifies missing keywords, checks formatting, and generates an optimized, tailored version of the resume that can be exported directly to a `.docx` file.

---

## 2. System Architecture

The project is built on a modern decoupled architecture:
- **Backend**: A REST API built with Python and FastAPI, handling heavy text processing, PDF parsing, ML vector embeddings, and document generation.
- **Frontend**: A Single Page Application (SPA) built with React 18 and Vite, featuring a glassmorphism UI design, interactive dashboards, and real-time state management.

---

## 3. Core Backend Modules (`/backend`)

### A. The Parsing Engine (`parser.py`)
Responsible for ingesting candidate documents and turning them into structured data.
- **Capabilities**: Parses PDF (`pypdf`), DOCX (`python-docx`), and plain text.
- **Features**: Extracts structural metadata (page counts, layouts), detects formatting elements like tables (which often trip up real ATS systems), and pulls out verified contact info (Email, Phone, LinkedIn, GitHub).
- **ATS Readability Checks**: Runs heuristics to ensure the document contains standard headers, bullet points, and parseable layouts.

### B. The Scoring Engine (`ats_scorer.py`)
The central nervous system for calculating the final 0–100 ATS match score. It weights several factors:
1. **Hard Skills (30%)**: Matches against a comprehensive `skills_taxonomy.py` containing thousands of canonical tech skills and synonyms.
2. **Dense Vector Embeddings (20%)**: Leverages the Vector Engine to calculate semantic resonance.
3. **Semantic Similarity (15%)**: TF-IDF Overlap for general vocabulary context.
4. **ATS Formatting (15%)**: Readability and structure constraints.
5. **Soft Skills (10%)**: Leadership, teamwork, and execution keywords.
6. **Experience Alignment (10%)**: Extracts explicit years of experience required vs. provided.

### C. The Vector Embedding Model (`vector_engine.py`)
A mathematical model that projects the text of the resume and JD into a 128-Dimensional dense semantic latent space.
- Calculates an overarching cosine similarity.
- Breaks down requirements into individual points to calculate a point-by-point resonance match between what the JD asks for and the candidate's bullets.
- Exposes raw vector activations for visual debugging on the frontend.

### D. The Optimization Engine (`resume_optimizer.py` & `exporter.py`)
When a user wants to update their resume, this engine kicks in.
- **Tailored Summary**: Generates a new executive summary embedding missing JD keywords.
- **STAR Bullets**: Synthesizes quantifiable impact bullets (Situation, Task, Action, Result) for missing hard skills.
- **Docx Export**: The `exporter.py` module uses `python-docx` to stream a fully formatted, ATS-compliant Word document back to the user.

---

## 4. Core Frontend Components (`/frontend/src/components`)

The React frontend handles all user interactions without relying on server-side rendering, ensuring a fast, snappy experience.

- **`DualInputPanel.jsx`**: The main landing workspace. Handles drag-and-drop file uploads, displays extracted text, and provides the initial text box for pasting the target Job Description.
- **`MatchReport.jsx`**: The analytics dashboard. Renders radial gauges for the overall score, progress bars for individual metrics, and an interactive Keyword Gap Matrix (filtering missing vs. matched skills).
- **`VectorDebugger.jsx`**: A highly interactive widget that displays the 128-D vector arrays as a visual heatmap. It allows the user to hover over individual tensor dimensions to inspect the math behind the semantic match.
- **`ResumeTailor.jsx`**: The post-analysis workspace. Presents the newly generated STAR bullets, an updated skills matrix, and a side-by-side diff editor. Users can make final tweaks here before exporting.

---

## 5. API Endpoints

The FastAPI backend exposes the following primary routes:

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/api/parse-resume` | `POST` | Accepts a multipart file upload. Returns structured text, readability heuristics, and the 128-D document embedding vector. |
| `/api/analyze-ats` | `POST` | Accepts JSON `(resume_text, job_description)`. Returns the comprehensive ATS score, missing keyword taxonomy, and vector analysis. |
| `/api/optimize-resume` | `POST` | Accepts JSON `(resume_text, job_description)`. Returns the newly generated, JD-tailored resume components. |
| `/api/export-docx` | `POST` | Accepts the final tailored text. Returns a downloadable `.docx` binary stream. |

---

## 6. Running the Project Locally

### Prerequisites
- Python 3.9+
- Node.js 18+

### Step 1: Start the Backend (API)
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```
*The backend API will run on `http://127.0.0.1:8000`. You can view the interactive Swagger docs at `/docs`.*

### Step 2: Start the Frontend (React Application)
```bash
cd frontend
npm install
npm run dev
```
*The frontend development server will launch, typically accessible at `http://localhost:5173`.*

---

## 7. Technology Stack Summary

- **Core Python**: FastAPI, Uvicorn, Scikit-Learn (TF-IDF, SVD), NumPy.
- **Document Processing**: `pypdf`, `python-docx`.
- **Frontend Framework**: React 18, Vite.
- **Styling**: Pure CSS Modules utilizing CSS variables for HSL color spaces, enabling the dynamic Dark Glassmorphism aesthetic.
- **Icons**: `lucide-react`.
