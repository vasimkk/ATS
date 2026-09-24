# ResuMatch ATS Studio API Documentation

This document provides a comprehensive collection of all the API endpoints available in the ResuMatch ATS Studio backend, including the endpoints used to fetch the embedding vectors (float arrays) shown in the Vector Debugger UI.

## Base URL
All endpoints are available at the base path: `http://localhost:8000` (or your configured host).

---

### 1. Parse Resume & Generate Vectors (Debugging/Float32 Data)
**Endpoint:** `POST /api/parse-resume`
**Content-Type:** `multipart/form-data`

**Description:**
Parses an uploaded resume file (PDF, DOCX, or TXT), extracts the text, and generates the dense 128-D Float32 embedding vector. This is the API responsible for returning the `f1, f2, f3...` (Float32 vector) data and diagnostic metadata you see in the **Vector Debugger** UI.

**Request Payload:**
- `file`: The resume file upload (`UploadFile`).

**Response Structure (JSON):**
Returns the full parsed document object, which includes the raw vector data and readability scores.
```json
{
  "text": "Extracted full text of the resume...",
  "sections": {
    "education": ["..."],
    "experience": ["..."]
  },
  "readability": {
    "score": 85
  },
  "readability_score": 85,
  "embedding_vector": {
    "vector": [0.0123, -0.0456, 0.0789, ...], // Float32 Array shown in the Debugger UI
    "metadata": { ... }
  }
}
```

---

### 2. Analyze ATS Match
**Endpoint:** `POST /api/analyze-ats`
**Content-Type:** `application/json`

**Description:**
Computes the comprehensive ATS match score, keyword gaps, and tailored recommendations by comparing the resume text against a target job description.

**Request Body:**
```json
{
  "resume_text": "Full text of candidate resume...",
  "job_description": "Target job description posting..."
}
```

**Response Structure (JSON):**
```json
{
  "overall_score": 82,
  "grade": "B",
  "vector_analysis": {
    "resume_vector": [...],
    "jd_vector": [...],
    "dimensional_correlation": [...]
  },
  "keyword_gaps": ["React", "Node.js"],
  "recommendations": ["Add more metrics to experience."]
}
```

---

### 3. Batch Analyze ATS Matches
**Endpoint:** `POST /api/analyze-ats-batch`
**Content-Type:** `application/json`

**Description:**
Computes ATS match scores against multiple job descriptions and returns a ranked list based on the overall match score. Heavy vector arrays are omitted to keep the payload light.

**Request Body:**
```json
{
  "resume_text": "Full text of candidate resume...",
  "job_descriptions": [
    {
      "id": "job_1",
      "text": "Job description 1 text..."
    },
    {
      "id": "job_2",
      "text": "Job description 2 text..."
    }
  ]
}
```

**Response Structure (JSON):**
```json
{
  "ranked_matches": [
    {
      "jd_id": "job_1",
      "overall_score": 88,
      "grade": "A",
      "match_details": { ... }
    }
  ]
}
```

---

### 4. Optimize Resume
**Endpoint:** `POST /api/optimize-resume`
**Content-Type:** `application/json`

**Description:**
Generates a tailored executive summary, STAR-method bullet points filling in missing keywords, and a complete updated ATS-ready resume text.

**Request Body:**
```json
{
  "resume_text": "Full text of candidate resume...",
  "job_description": "Target job description posting...",
  "target_role": "Senior Frontend Developer" // Optional
}
```

**Response Structure (JSON):**
Returns the generated optimizations from the LLM engine.
```json
{
  "executive_summary": "Highly motivated Senior Frontend Developer...",
  "optimized_bullets": [
    "Improved application performance by 20% using React."
  ],
  "full_optimized_resume": "..."
}
```

---

### 5. Export Optimized Resume to DOCX
**Endpoint:** `POST /api/export-docx`
**Content-Type:** `application/json`

**Description:**
Generates and streams an ATS-formatted Microsoft Word document (`.docx`) containing the optimized resume text.

**Request Body:**
```json
{
  "resume_text": "Tailored resume text to export...",
  "filename": "ATS_Optimized_Resume.docx" // Optional
}
```

**Response:**
Returns a `StreamingResponse` (binary file download) with `Content-Type: application/vnd.openxmlformats-officedocument.wordprocessingml.document`.

---

### 6. Health Check
**Endpoint:** `GET /api/health`

**Description:**
Simple health check endpoint to verify if the API server is running.

**Response Structure (JSON):**
```json
{
  "status": "healthy",
  "service": "ResuMatch ATS Studio API",
  "version": "1.0.0"
}
```
