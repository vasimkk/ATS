# Resume Parsing & ATS Scoring Documentation

This document explains the inner workings of how ResuMatch extracts data from a resume, mathematically calculates an ATS score, and details the matching architecture.

---

## 1. How Resume Parsing Works (`parser.py`)

When you upload a resume to the system, it goes through a multi-stage extraction and analysis pipeline before any scoring occurs.

### A. Text Extraction
- **PDF Files**: Uses `pypdf` to extract text. It's smart enough to detect multi-column layouts and parse tables correctly, which is a common failure point for older ATS systems.
- **Word Documents (.docx)**: Uses `python-docx` to read paragraphs, tables, and headers natively.
- **Plain Text**: Reads standard UTF-8 text directly.

### B. Structural & Layout Analysis
The parser doesn't just read words; it evaluates the structure:
- **Section Detection**: It looks for standard headers like "Work Experience", "Education", "Skills", and "Certifications" to chunk the resume into logical sections.
- **Formatting Checks**: It counts the number of bullet points, checks for excessively long paragraphs (which lower readability), and verifies the page count (1 to 2 pages is optimal).

### C. Contact Information Extraction
It uses Regular Expressions (Regex) to securely extract and verify:
- **Emails** (`@domain.com`)
- **Phone Numbers** (standard global formats)
- **LinkedIn / GitHub / Portfolio URLs**
- **Location data**

### D. Output
The final parsed object contains the clean text, structural metadata, and contact info, which is then fed into the Vector Engine and the ATS Scorer.

---

## 2. How the ATS Score is Calculated (`ats_scorer.py`)

The overarching ATS Score (0–100%) is a weighted average of 6 distinct algorithms. It does not rely on a single keyword matching logic. 

Here is the exact mathematical breakdown of your ATS score:

### 1. Hard Skills Match (30% Weight)
- Extracts skills from both the Resume and the Job Description using `skills_taxonomy.py`. 
- It uses canonical matching (knowing that "React", "ReactJS", and "React.js" are the same thing).
- The score is the percentage of JD technical skills successfully found in the resume.

### 2. Dense Vector Embeddings (20% Weight)
- Evaluates the semantic meaning of the text, bypassing exact keywords.
- Calculates how closely the candidate's achievements map to the JD's responsibilities using a 128-Dimensional Cosine Similarity score.

### 3. Semantic Overlap / TF-IDF (15% Weight)
- Looks at the vocabulary overlap across the entire document using Term Frequency-Inverse Document Frequency.
- Ensures the "tone" and industry jargon align between the two documents.

### 4. ATS Formatting Readability (15% Weight)
- Uses the data from the parser to check if a Taleo or Workday system could read the resume. 
- You lose points for missing contact info, missing standard section headers, or having too few bullet points.

### 5. Soft Skills & Leadership (10% Weight)
- Separates soft skills (e.g., "Agile", "Team Leadership", "Cross-functional") from technical skills.
- Checks if the candidate demonstrates these core competencies.

### 6. Experience & Seniority Alignment (10% Weight)
- Dynamically extracts requirements like "5+ years of experience" from the JD.
- Scans the resume to confirm if the candidate explicitly mentions having equivalent or greater years of experience.

---

## 3. Job Matching Strategy: 1-to-1 vs. 1-to-Many

### Current Architecture: **1-to-1 Matching**
Out of the box, the ResuMatch architecture operates on a strict **1-to-1** matching model. 
- You provide **one candidate resume** and **one specific target job description**.
- The API (`/api/analyze-ats`) receives this pair and performs a deep, computationally heavy analysis (including generating dense vector matrices and dynamic STAR bullets).
- This approach is favored because it generates highly actionable, targeted recommendations for a specific job application.

### Can it do 1-to-Many?
While the UI is built for 1-to-1, the backend functions are stateless. You could easily adapt the system for 1-to-many (e.g., matching a candidate's resume against an entire database of jobs) by:
1. Parsing the candidate's resume **once** to get their text and Embedding Vector.
2. Writing a script to iterate over a database of JDs, calling `compute_tfidf_similarity()` and `get_vector_match()` in a loop.
3. Ranking the JDs based on the highest returned `overall_score`.
