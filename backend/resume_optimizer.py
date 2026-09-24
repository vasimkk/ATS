"""
Resume Optimizer and Tailoring Engine.
Generates tailored executive summaries, STAR bullet points with missing keywords,
optimized skills matrices, and full ATS-tailored resume text.
"""
import re
import random
from typing import Dict, Any, List, Optional
from skills_taxonomy import (
    extract_skills_from_text,
    find_category_for_skill,
    canonicalize_skill
)
from parser import extract_contact_info, detect_sections
from ats_scorer import analyze_ats_match
from llm_engine import generate_action_verbs

# Metric templates for impactful STAR bullet generation
METRIC_TEMPLATES = [
    "improving system throughput by 38% and lowering latency across critical services",
    "reducing deployment cycle time by 45% with automated CI/CD workflows",
    "enhancing query response times by 50% and cutting cloud infrastructure overhead by 25%",
    "scaling high-availability architectures to support 250k+ daily active users",
    "driving a 30% increase in test coverage while reducing post-release defect rates by 40%",
    "boosting team delivery velocity by 35% through standardized Agile practices and code reviews",
    "slashing average page load time by 1.8 seconds, elevating user retention by 22%",
    "optimizing API response times by 40% and achieving 99.95% service uptime"
]

def extract_job_title(jd_text: str) -> str:
    """Attempt to extract likely job title from the first lines of the JD."""
    lines = [l.strip() for l in jd_text.split('\n') if l.strip()]
    if not lines:
        return "Software Professional"
    
    first_few = " ".join(lines[:3])
    # Search common title patterns
    match = re.search(
        r'(Senior\s+|Lead\s+|Principal\s+|Staff\s+|Junior\s+)?(Software Engineer|Full Stack Developer|Frontend Developer|Backend Developer|DevOps Engineer|Data Scientist|Machine Learning Engineer|Cloud Architect|Product Manager|QA Engineer|Systems Engineer|Data Engineer)',
        first_few,
        re.IGNORECASE
    )
    if match:
        return match.group(0).title()
    
    # Fallback to first line if short
    if len(lines[0].split()) <= 6:
        return lines[0].title()
        
    return "Software Engineer"

def generate_tailored_summary(
    target_role: str,
    matched_skills: List[str],
    missing_skills: List[str],
    years_exp: Optional[int] = None
) -> str:
    """Generate a targeted, high-impact Professional Summary without hardcoded static data."""
    core_tech = matched_skills[:4] + missing_skills[:3]
    skills_str = ", ".join(core_tech) if core_tech else "specialized industry technologies and methodologies"
    
    exp_phrase = f"with {years_exp}+ years of experience" if years_exp and years_exp > 0 else "with a proven track record"
    
    summary = (
        f"Results-driven {target_role} {exp_phrase} architecting, "
        f"developing, and delivering high-performance solutions. "
        f"Proficient in {skills_str}, with hands-on expertise in optimizing system performance, "
        f"accelerating delivery pipelines, and driving cross-functional collaboration to exceed organizational goals."
    )
    return summary

def generate_star_bullets(
    missing_skills: List[str],
    existing_bullets: List[str],
    target_role: str = ""
) -> List[Dict[str, str]]:
    """
    Generate or upgrade existing bullet points into STAR formatted bullets
    incorporating the missing keywords and quantifiable metrics.
    """
    enhanced = []
    skills_to_use = list(missing_skills)
    
    # Base templates for inserting skills
    templates = [
        ("Spearheaded the design and implementation of microservices using {skill}, {metric}.", "Technical Leadership"),
        ("Architected and deployed resilient cloud workflows integrating {skill}, {metric}.", "Cloud & Infrastructure"),
        ("Optimized backend data pipelines and API endpoints leveraging {skill}, {metric}.", "Performance Engineering"),
        ("Engineered modern, responsive web interfaces utilizing {skill}, {metric}.", "Frontend Architecture"),
        ("Automated end-to-end testing and delivery suites utilizing {skill}, {metric}.", "Quality Assurance & DevOps"),
        ("Collaborated cross-functionally to standardize {skill} best practices, {metric}.", "Engineering Excellence")
    ]
    
    dynamic_action_verbs = generate_action_verbs(target_role)

    # If we have existing bullets, upgrade them
    for i, orig_b in enumerate(existing_bullets[:6]):
        clean_b = re.sub(r'^[•\-\*\s]+', '', orig_b).strip()
        if not clean_b:
            continue
            
        skill_insert = skills_to_use.pop(0) if skills_to_use else None
        action_verb = dynamic_action_verbs[i % len(dynamic_action_verbs)]
        metric = METRIC_TEMPLATES[i % len(METRIC_TEMPLATES)]
        
        if skill_insert:
            tailored = f"{action_verb} core modules utilizing {skill_insert}, enhancing existing architecture: {clean_b[:120]}..., {metric}."
        else:
            tailored = f"{action_verb} and optimized key deliverables ({clean_b[:140]}), {metric}."
            
        enhanced.append({
            "original": clean_b,
            "optimized": tailored,
            "injected_skill": skill_insert
        })
        
    # If more missing skills remain, generate fresh high-impact bullets
    while skills_to_use and len(enhanced) < 6:
        skill = skills_to_use.pop(0)
        template, category = templates[len(enhanced) % len(templates)]
        metric = METRIC_TEMPLATES[len(enhanced) % len(METRIC_TEMPLATES)]
        bullet_text = template.format(skill=skill, metric=metric)
        enhanced.append({
            "original": "(New bullet recommended to address missing keyword)",
            "optimized": bullet_text,
            "injected_skill": skill
        })
        
    return enhanced

def generate_optimized_skills_matrix(
    resume_skills: Dict[str, List[str]],
    missing_skills: List[str]
) -> Dict[str, List[str]]:
    """
    Build an upgraded skills matrix incorporating missing JD skills.
    """
    upgraded = {k: list(v) for k, v in resume_skills.items()}
    
    for skill in missing_skills:
        cat = find_category_for_skill(skill)
        if cat not in upgraded:
            upgraded[cat] = []
        if skill not in upgraded[cat]:
            upgraded[cat].append(skill)
            
    # Sort each category
    return {cat: sorted(skills) for cat, skills in upgraded.items() if skills}

def optimize_resume(
    resume_text: str,
    jd_text: str,
    target_role: Optional[str] = None
) -> Dict[str, Any]:
    """
    Orchestrate complete resume tailoring and optimization process.
    """
    # 1. Analyze current ATS match
    ats_results = analyze_ats_match(resume_text, jd_text)
    
    # 2. Extract sections & contacts
    contacts = extract_contact_info(resume_text)
    sections = detect_sections(resume_text)
    
    # 3. Determine role & years
    detected_role = target_role or extract_job_title(jd_text)
    missing_skills = ats_results["keywords"]["missing_skills"]
    matched_skills = ats_results["keywords"]["matched_skills"]
    
    # Extract candidate years of experience dynamically from resume
    from ats_scorer import extract_experience_years
    cand_years_list = extract_experience_years(resume_text)
    cand_years = max(cand_years_list) if cand_years_list else None

    # Extract existing bullet points
    raw_bullets = re.findall(r'(?:^|\n)\s*[•\-\*\u2022\u2023\u25E6]\s*(.+)', resume_text)
    if not raw_bullets:
        # Split experience paragraphs by sentences if no bullet points found
        exp_text = sections.get("experience", "")
        raw_bullets = [s.strip() for s in exp_text.split('\n') if len(s.strip()) > 25]

    # 4. Generate components dynamically
    tailored_summary = generate_tailored_summary(
        target_role=detected_role,
        matched_skills=matched_skills,
        missing_skills=missing_skills,
        years_exp=cand_years
    )
    
    tailored_bullets = generate_star_bullets(
        missing_skills=missing_skills,
        existing_bullets=raw_bullets,
        target_role=detected_role
    )
    
    resume_skills_dict = extract_skills_from_text(resume_text)
    optimized_skills_matrix = generate_optimized_skills_matrix(
        resume_skills=resume_skills_dict,
        missing_skills=missing_skills
    )
    
    # 5. Extract candidate name / top header from original resume
    first_line = ""
    for line in resume_text.split('\n'):
        if line.strip() and not line.strip().startswith(('PROFESSIONAL RESUME', '=', '-')):
            first_line = line.strip()
            break
            
    contact_header_parts = []
    if contacts.get("email"): contact_header_parts.append(contacts["email"])
    if contacts.get("phone"): contact_header_parts.append(contacts["phone"])
    if contacts.get("linkedin"): contact_header_parts.append(contacts["linkedin"])
    if contacts.get("github"): contact_header_parts.append(contacts["github"])
    
    header_name = first_line if first_line else f"CANDIDATE - {detected_role.upper()}"
    contact_header = " | ".join(contact_header_parts) if contact_header_parts else ""

    full_resume_lines = [
        header_name.upper(),
    ]
    if contact_header:
        full_resume_lines.append(contact_header)
        
    full_resume_lines.extend([
        "=" * 60,
        "",
        "PROFESSIONAL SUMMARY",
        "-" * 30,
        tailored_summary,
        "",
        "KEY TECHNICAL SKILLS & COMPETENCIES",
        "-" * 30,
    ])
    
    for cat, skills in optimized_skills_matrix.items():
        full_resume_lines.append(f"• {cat}: {', '.join(skills)}")
        
    full_resume_lines.extend([
        "",
        "PROFESSIONAL EXPERIENCE & ACHIEVEMENTS",
        "-" * 30,
    ])
    
    for b in tailored_bullets:
        full_resume_lines.append(f"• {b['optimized']}")
        
    if "education" in sections and sections["education"].strip():
        full_resume_lines.extend([
            "",
            "EDUCATION & CREDENTIALS",
            "-" * 30,
            sections["education"].strip()
        ])
        
    full_optimized_resume = "\n".join(full_resume_lines)
    
    # 6. Re-evaluate ATS match for the optimized resume!
    optimized_ats = analyze_ats_match(full_optimized_resume, jd_text)

    return {
        "target_role": detected_role,
        "original_score": ats_results["overall_score"],
        "projected_score": optimized_ats["overall_score"],
        "score_delta": optimized_ats["overall_score"] - ats_results["overall_score"],
        "tailored_summary": tailored_summary,
        "tailored_bullets": tailored_bullets,
        "optimized_skills": optimized_skills_matrix,
        "injected_keywords": missing_skills,
        "full_optimized_resume": full_optimized_resume,
        "before_metrics": ats_results["metrics"],
        "after_metrics": optimized_ats["metrics"]
    }
