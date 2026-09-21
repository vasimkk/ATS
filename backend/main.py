"""
FastAPI Server for ATS Resume Matcher & Optimizer Studio.
"""
from fastapi import FastAPI, UploadFile, File, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

from parser import (
    parse_resume_document,
    extract_text_from_pdf,
    extract_text_from_docx,
    evaluate_ats_readability,
    detect_sections,
    extract_contact_info
)
from vector_engine import vector_engine
from ats_scorer import analyze_ats_match
from resume_optimizer import optimize_resume
from exporter import create_docx_from_text

app = FastAPI(
    title="ResuMatch ATS Studio API",
    description="Intelligent ATS Resume Scoring, Keyword Gap Detection & Resume Tailoring Engine",
    version="1.0.0"
)

# Enable CORS for local dev server and web apps
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalyzeRequest(BaseModel):
    resume_text: str = Field(..., description="Full text of candidate resume")
    job_description: str = Field(..., description="Target job description posting")

class BatchAnalyzeRequest(BaseModel):
    resume_text: str = Field(..., description="Full text of candidate resume")
    job_descriptions: List[Dict[str, str]] = Field(..., description="List of JDs with 'id' and 'text'")

class OptimizeRequest(BaseModel):
    resume_text: str = Field(..., description="Full text of candidate resume")
    job_description: str = Field(..., description="Target job description posting")
    target_role: Optional[str] = Field(None, description="Optional target job role title")

class ExportRequest(BaseModel):
    resume_text: str = Field(..., description="Tailored resume text to export")
    filename: Optional[str] = Field("ATS_Optimized_Resume.docx", description="Output filename")

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": "ResuMatch ATS Studio API",
        "version": "1.0.0"
    }

@app.post("/api/parse-resume")
async def parse_resume_file(file: UploadFile = File(...)):
    """
    Parse an uploaded resume file (PDF, DOCX, or TXT) with table, column, and multi-page support.
    Generates a dense 128-D embedding vector and returns full diagnostic metadata for debugging.
    """
    contents = await file.read()
    
    if not contents:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    try:
        parsed_doc = parse_resume_document(contents, file.filename)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to extract text from {file.filename}: {str(e)}"
        )

    if not parsed_doc["text"].strip():
        raise HTTPException(
            status_code=400,
            detail="Could not extract readable text. The document might be an image-only scan."
        )

    # Generate dense embedding vector and diagnostic metadata
    embedding_info = vector_engine.generate_document_vector(
        text=parsed_doc["text"],
        sections=parsed_doc.get("sections")
    )

    parsed_doc["embedding_vector"] = embedding_info
    # Top-level readability score for backwards compatibility
    parsed_doc["readability_score"] = parsed_doc["readability"]["score"]

    return parsed_doc

@app.post("/api/analyze-ats")
def analyze_ats(payload: AnalyzeRequest):
    """
    Compute comprehensive ATS match score, keyword gaps, and tailored recommendations.
    """
    if len(payload.resume_text.strip()) < 50:
        raise HTTPException(status_code=400, detail="Resume text is too short to analyze.")
    if len(payload.job_description.strip()) < 50:
        raise HTTPException(status_code=400, detail="Job description is too short to analyze.")

    try:
        results = analyze_ats_match(payload.resume_text, payload.job_description)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ATS Analysis failed: {str(e)}")

@app.post("/api/analyze-ats-batch")
def analyze_ats_batch(payload: BatchAnalyzeRequest):
    """
    Compute ATS match scores against multiple job descriptions and return a ranked list.
    """
    if len(payload.resume_text.strip()) < 50:
        raise HTTPException(status_code=400, detail="Resume text is too short to analyze.")
    
    results = []
    for jd in payload.job_descriptions:
        jd_id = jd.get("id", "unknown")
        jd_text = jd.get("text", "")
        
        if len(jd_text.strip()) < 50:
            continue
            
        try:
            match = analyze_ats_match(payload.resume_text, jd_text)
            
            # Remove heavy vector arrays for batch response to keep payload light
            if "vector_analysis" in match:
                match["vector_analysis"].pop("resume_vector", None)
                match["vector_analysis"].pop("jd_vector", None)
                match["vector_analysis"].pop("dimensional_correlation", None)
                
            results.append({
                "jd_id": jd_id,
                "overall_score": match["overall_score"],
                "grade": match["grade"],
                "match_details": match
            })
        except Exception:
            continue
            
    # Sort by overall_score descending
    results.sort(key=lambda x: x["overall_score"], reverse=True)
    return {"ranked_matches": results}

@app.post("/api/optimize-resume")
def optimize_resume_endpoint(payload: OptimizeRequest):
    """
    Generate tailored executive summary, STAR-method bullet points with missing keywords,
    and a complete updated ATS-ready resume.
    """
    if len(payload.resume_text.strip()) < 50 or len(payload.job_description.strip()) < 50:
        raise HTTPException(status_code=400, detail="Both resume and job description are required.")

    try:
        results = optimize_resume(
            resume_text=payload.resume_text,
            jd_text=payload.job_description,
            target_role=payload.target_role
        )
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Resume optimization failed: {str(e)}")

@app.post("/api/export-docx")
def export_docx_endpoint(payload: ExportRequest):
    """
    Generate and stream an ATS-formatted Microsoft Word document (.docx).
    """
    if not payload.resume_text.strip():
        raise HTTPException(status_code=400, detail="Resume text cannot be empty.")

    try:
        stream = create_docx_from_text(payload.resume_text)
        filename = payload.filename if payload.filename.endswith(".docx") else f"{payload.filename}.docx"
        
        headers = {
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
        return StreamingResponse(
            stream,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers=headers
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
