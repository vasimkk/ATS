"""
ATS Scoring Engine.
Computes multi-factor match between Resume and Job Description using:
- TF-IDF Cosine Similarity
- Hard Skills and Technical Taxonomy Matching
- Soft Skills & Methodologies Coverage
- Experience & Seniority Alignment
- Structural ATS Readability Compliance
"""
import re
from typing import Dict, Any, List, Set, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from skills_taxonomy import (
    extract_skills_from_text,
    canonicalize_skill,
    find_category_for_skill,
    SKILLS_TAXONOMY
)
from parser import evaluate_ats_readability
from vector_engine import get_vector_match, get_semantic_similarity
from llm_engine import evaluate_with_llm

def compute_tfidf_similarity(resume_text: str, jd_text: str) -> float:
    """Compute semantic text overlap using TF-IDF and Cosine Similarity."""
    try:
        vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            stop_words="english",
            max_features=1000
        )
        tfidf_matrix = vectorizer.fit_transform([resume_text, jd_text])
        sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        # Normalize to 0-100 scale with a realistic curve
        score = min(100.0, sim * 140.0)
        return round(score, 1)
    except Exception:
        return 50.0

def extract_experience_years(text: str) -> List[int]:
    """Extract numbers of years mentioned in context of experience."""
    matches = re.findall(r'(\d+)\+?\s*(?:years?|yrs?)(?:\s+of)?(?:\s+experience)?', text, re.IGNORECASE)
    years = [int(m) for m in matches if int(m) <= 40]
    return years

def extract_education_degrees(text: str) -> Set[str]:
    """Detect degrees mentioned in text."""
    degrees = set()
    t = text.lower()
    if re.search(r'\b(?:bachelor|b\.s\.|b\.sc\.|b\.tech|b\.e\.|undergraduate)\b', t):
        degrees.add("bachelor")
    if re.search(r'\b(?:master|m\.s\.|m\.sc\.|m\.tech|m\.e\.|postgraduate|mba)\b', t):
        degrees.add("master")
    if re.search(r'\b(?:phd|doctorate|ph\.d\.)\b', t):
        degrees.add("phd")
    return degrees

def analyze_ats_match(resume_text: str, jd_text: str) -> Dict[str, Any]:
    """
    Primary ATS evaluation pipeline comparing resume to job description.
    """
    if not resume_text.strip() or not jd_text.strip():
        raise ValueError("Both resume text and job description must be provided.")

    # 1. Readability & Formatting
    readability_results = evaluate_ats_readability(resume_text)
    readability_score = readability_results["score"]

    # 2. Extract Skills from both
    resume_skills_dict = extract_skills_from_text(resume_text)
    jd_skills_dict = extract_skills_from_text(jd_text)

    # Flatten skills with canonicalization
    resume_skills_flat = {canonicalize_skill(s): s for skills in resume_skills_dict.values() for s in skills}
    jd_skills_flat = {canonicalize_skill(s): s for skills in jd_skills_dict.values() for s in skills}
    
    # Create canonical skill strings for the Matching Engine (F1 & F2)
    resume_canonical_text = " ".join(resume_skills_flat.keys())
    jd_canonical_text = " ".join(jd_skills_flat.keys())

    # Technical vs Soft Skills breakdown
    soft_cat_names = ["Soft Skills & Leadership"]
    
    jd_tech_skills = {k: v for k, v in jd_skills_flat.items() if find_category_for_skill(k) not in soft_cat_names}
    jd_soft_skills = {k: v for k, v in jd_skills_flat.items() if find_category_for_skill(k) in soft_cat_names}

    matched_tech = [v for k, v in jd_tech_skills.items() if k in resume_skills_flat]
    missing_tech = [v for k, v in jd_tech_skills.items() if k not in resume_skills_flat]

    matched_soft = [v for k, v in jd_soft_skills.items() if k in resume_skills_flat]
    missing_soft = [v for k, v in jd_soft_skills.items() if k not in resume_skills_flat]

    # Calculate Technical Match Score
    if jd_tech_skills:
        tech_score = round((len(matched_tech) / len(jd_tech_skills)) * 100, 1)
    else:
        tech_score = 80.0  # JD didn't explicitly mandate hard skills

    # Calculate Soft Skills Match Score
    if jd_soft_skills:
        soft_score = round((len(matched_soft) / len(jd_soft_skills)) * 100, 1)
    else:
        soft_score = 85.0

    # 3. Dense Semantic Vector Content Score (F1 - now uses canonical skills per architecture, via all-MiniLM-L6-v2)
    semantic_score = get_semantic_similarity(resume_canonical_text, jd_canonical_text)

    # 4. Experience & Education Alignment
    jd_years = extract_experience_years(jd_text)
    resume_years = extract_experience_years(resume_text)
    req_years = max(jd_years) if jd_years else None
    cand_years = max(resume_years) if resume_years else None

    exp_score = 85.0
    exp_notes = []
    if req_years is not None:
        if cand_years is not None:
            if cand_years >= req_years:
                exp_score = 100.0
                exp_notes.append(f"Meets or exceeds required experience ({cand_years} yrs vs {req_years} yrs required).")
            else:
                gap = req_years - cand_years
                exp_score = max(40.0, 100.0 - gap * 15.0)
                exp_notes.append(f"Resume states {cand_years} years, but job asks for {req_years}+ years.")
        else:
            exp_score = 70.0
            exp_notes.append(f"Job requires {req_years}+ years; explicit years not detected in resume text.")
    else:
        exp_notes.append("No strict years of experience requirement identified.")

    # Education degrees check
    jd_degrees = extract_education_degrees(jd_text)
    cand_degrees = extract_education_degrees(resume_text)
    if jd_degrees:
        if jd_degrees.intersection(cand_degrees) or (len(cand_degrees) > 0 and "bachelor" in jd_degrees):
            exp_score = min(100.0, exp_score + 5.0)
            exp_notes.append("Education degree matches requirements.")
        else:
            exp_score = max(50.0, exp_score - 10.0)
            exp_notes.append("Degree requirements may need to be explicitly highlighted.")

    # 5. Generative LLM Deep Pass (replaces point-by-point resonance)
    # Since the frontend UI for point-by-point was removed, we only need the overall score
    llm_results = evaluate_with_llm(resume_text, jd_text)
    vector_score = llm_results["score"]
    llm_reasoning = llm_results["reasoning"]

    # 6. Overall Weighted ATS Score
    # User Formula: F1 (Cosine), F2 (Skill Overlap), F3 (Keyword Density) = 60%, F4 (Deep LLM pass) = 40%
    
    # F1: Cosine Similarity (using canonical skills)
    f1_cosine = semantic_score
    
    # F2: Skill Overlap (Average of tech and soft skills)
    f2_skill = (tech_score + soft_score) / 2
    
    # F3: Keyword Density (using canonical skills text per architecture)
    jd_words = set(jd_skills_flat.keys())
    resume_words = set(resume_skills_flat.keys())
    f3_keyword = (len(jd_words.intersection(resume_words)) / max(len(jd_words), 1)) * 100
    f3_keyword = min(100.0, f3_keyword * 1.5) # Boost slightly for realistic scoring
    
    # F4: Deep LLM pass (Generative LLM Score)
    f4_llm = vector_score
    
    # Calculate components
    # Weights: F1 (30%), F2 (18%), F3 (12%), F4 (40%)
    f1_weight_30 = f1_cosine * 0.30
    f2_weight_18 = f2_skill * 0.18
    f3_weight_12 = f3_keyword * 0.12
    f4_weight_40 = f4_llm * 0.40
    
    overall_score = round(f1_weight_30 + f2_weight_18 + f3_weight_12 + f4_weight_40)
    overall_score = max(0, min(100, overall_score))

    # Grade determination
    if overall_score >= 88:
        grade = "A+"
        grade_label = "Exceptional Match"
        status_color = "emerald"
    elif overall_score >= 75:
        grade = "A"
        grade_label = "Strong Match"
        status_color = "teal"
    elif overall_score >= 60:
        grade = "B"
        grade_label = "Moderate Match"
        status_color = "amber"
    elif overall_score >= 45:
        grade = "C"
        grade_label = "Low Match"
        status_color = "orange"
    else:
        grade = "D"
        grade_label = "Poor Match"
        status_color = "rose"

    # Grouped missing keywords with category details
    missing_by_cat: Dict[str, List[str]] = {}
    for skill in missing_tech + missing_soft:
        cat = find_category_for_skill(skill)
        if cat not in missing_by_cat:
            missing_by_cat[cat] = []
        missing_by_cat[cat].append(skill)

    matched_by_cat: Dict[str, List[str]] = {}
    for skill in matched_tech + matched_soft:
        cat = find_category_for_skill(skill)
        if cat not in matched_by_cat:
            matched_by_cat[cat] = []
        matched_by_cat[cat].append(skill)

    # Actionable Recommendations
    recommendations = []
    if missing_tech:
        top_missing = ", ".join(missing_tech[:5])
        recommendations.append({
            "type": "critical",
            "title": f"Incorporate Top Missing Technical Skills",
            "message": f"Add high-value terms such as {top_missing} into your Work Experience bullets or Skills section."
        })
    if vector_score < 65:
        recommendations.append({
            "type": "critical",
            "title": "Boost Semantic Vector Resonance",
            "message": "Align your achievement phrasing more closely with the responsibilities in the Job Description to increase vector embedding alignment."
        })
    if missing_soft:
        top_soft = ", ".join(missing_soft[:3])
        recommendations.append({
            "type": "improvement",
            "title": "Add Missing Core Competencies",
            "message": f"Demonstrate soft skills such as {top_soft} with real project examples."
        })
    if readability_score < 75:
        recommendations.append({
            "type": "critical",
            "title": "Fix ATS Formatting Issues",
            "message": "Ensure your contact info is easy to extract, use standard section headers, and add quantified bullet points."
        })
    if exp_score < 75 and req_years:
        recommendations.append({
            "type": "improvement",
            "title": "Highlight Years of Experience",
            "message": f"Make sure your relevant career duration ({req_years}+ years) is prominently stated in your Executive Summary."
        })

    # Get point-by-point vector analysis for debugging F1
    vector_analysis_data = get_vector_match(resume_text, jd_text)

    return {
        "overall_score": overall_score,
        "grade": grade,
        "grade_label": grade_label,
        "status_color": status_color,
        "metrics": {
            "technical_skills_match": tech_score,
            "vector_similarity": vector_score,
            "vector_coverage": 100.0,
            "semantic_similarity": semantic_score,
            "ats_readability": readability_score,
            "soft_skills_match": soft_score,
            "experience_alignment": round(exp_score, 1),
            "f1_cosine": round(f1_cosine, 1),
            "f2_skill": round(f2_skill, 1),
            "f2_matched_tech": len(matched_tech),
            "f2_jd_tech": len(jd_tech_skills),
            "f2_matched_soft": len(matched_soft),
            "f2_jd_soft": len(jd_soft_skills),
            "f3_keyword": round(f3_keyword, 1),
            "f3_jd_words": len(jd_words),
            "f3_matched_words": len(jd_words.intersection(resume_words)),
            "f3_matched_words_list": sorted(list(jd_words.intersection(resume_words))),
            "f3_missing_words_list": sorted(list(jd_words - resume_words)),
            "f4_llm": round(f4_llm, 1),
            "f1_weight_30": round(f1_weight_30, 1),
            "f2_weight_18": round(f2_weight_18, 1),
            "f3_weight_12": round(f3_weight_12, 1),
            "f4_weight_40": round(f4_weight_40, 1)
        },
        "llm_analysis": llm_results,
        "keywords": {
            "total_jd_skills": len(jd_skills_flat),
            "total_matched": len(matched_tech) + len(matched_soft),
            "total_missing": len(missing_tech) + len(missing_soft),
            "matched_skills": sorted(matched_tech + matched_soft),
            "missing_skills": sorted(missing_tech + missing_soft),
            "matched_by_category": matched_by_cat,
            "missing_by_category": missing_by_cat
        },
        "vector_analysis": vector_analysis_data,
        "readability": readability_results,
        "experience_notes": exp_notes,
        "recommendations": recommendations
    }
